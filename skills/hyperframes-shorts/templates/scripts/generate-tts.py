#!/usr/bin/env python3
"""Per-line Edge TTS → segments/*.wav, concat voiceover.wav, write schedule.json.

TTS granularity = one breath per lines.json row (voice/text).
Subtitle display may split into subtitleParts without extra wav files.
"""
import asyncio
import hashlib
import json
import math
import re
import subprocess
import sys
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parent.parent
LINES_PATH = ROOT / "audio/lines.json"
META_PATH = ROOT / "meta.json"
OUT_DIR = ROOT / "audio/segments"
VOICEOVER = ROOT / "audio/voiceover.wav"

OUT_DIR.mkdir(parents=True, exist_ok=True)

VOICE = "zh-CN-YunyangNeural"
RATE = "+12%"  # 实测总时长 >150s 时改为 "+18%" 后重跑
GAP = 0

# 字幕拆条禁止断点 — 见 templates/subtitle-tts-guide.md（仅校验 subtitle，不拦 TTS 整句）
FORBIDDEN_TAIL = (
    "我的",
    "你的",
    "他的",
    "她的",
    "它的",
    "我们的",
    "他们的",
    "让其",
    "让我的",
    "让你的",
    "把",
    "被",
    "在",
    "和",
    "与",
    "或",
    "及",
    "而",
    "并",
    "让",
    "给",
    "对",
    "从",
    "向",
)

FORBIDDEN_HEAD = (
    "的",
    "地",
    "得",
    "了",
    "吗",
    "呢",
    "吧",
    "啊",
    "呀",
)


def text_hash(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()[:8]


def load_subtitle_limits() -> tuple[int, bool]:
    """Return (max_han conservative, is_vertical)."""
    width, height = 1920, 1080
    font_px = 58
    if META_PATH.exists():
        meta = json.loads(META_PATH.read_text(encoding="utf-8"))
        width = int(meta.get("width", width))
        height = int(meta.get("height", height))
    vertical = height > width
    if vertical:
        font_px = 52
        conservative = 12
    else:
        conservative = 16
    usable = width * 0.88
    per_char = font_px * 1.05
    computed = max(8, int(math.floor(usable / per_char)))
    cap = 14 if vertical else 18
    dynamic = min(cap, computed)
    return min(conservative, dynamic), vertical


def visual_units(text: str) -> float:
    plain = re.sub(r"[，。！？：；、\s]+", "", text)
    han = len(re.findall(r"[\u4e00-\u9fff]", plain))
    ascii_count = len(re.findall(r"[\x00-\x7f]", plain))
    return han + ascii_count * 0.55


def strip_for_check(text: str) -> str:
    return re.sub(r"[，。！？：；、\s]+$", "", text.strip())


def strip_sub_punct(text: str) -> str:
    return re.sub(r"[，。！？：；、]+$", "", text.strip())


def voice_text(item: dict) -> str:
    """TTS 口播原文：voice 优先，兼容旧字段 text。"""
    return (item.get("voice") or item.get("text") or "").strip()


def tts_payload(item: dict) -> str:
    return item.get("speak") or voice_text(item)


def split_subtitle_display(text: str, max_units: float) -> list[str]:
    """显示层自动按标点拆条；仍超长则递归再拆，不生成额外 wav。"""
    core = strip_sub_punct(text)
    if visual_units(core) <= max_units:
        return [core]

    raw_parts: list[str] = []
    buf = ""
    for seg in re.findall(r"[^，。！？、；]+[，。！？、；]?", text):
        candidate = buf + seg
        if visual_units(strip_sub_punct(candidate)) <= max_units:
            buf = candidate
        else:
            if buf.strip():
                raw_parts.append(strip_sub_punct(buf))
            buf = seg
    if buf.strip():
        raw_parts.append(strip_sub_punct(buf))
    if not raw_parts:
        raw_parts = [core]

    final: list[str] = []
    for part in raw_parts:
        final.extend(_split_part_until_fit(part, max_units))
    return final if final else [core]


def _split_part_until_fit(text: str, max_units: float) -> list[str]:
    text = strip_sub_punct(text)
    if not text:
        return []
    if visual_units(text) <= max_units:
        return [text]

    for delim in ("，", "、", "；"):
        if delim not in text:
            continue
        segs = text.split(delim)
        parts: list[str] = []
        buf = ""
        for i, seg in enumerate(segs):
            suffix = delim if i < len(segs) - 1 else ""
            piece = seg + suffix
            cand = buf + piece
            if visual_units(strip_sub_punct(cand)) <= max_units:
                buf = cand
            else:
                if buf.strip():
                    parts.append(strip_sub_punct(buf))
                buf = piece
        if buf.strip():
            parts.append(strip_sub_punct(buf))
        if parts and all(visual_units(p) <= max_units for p in parts):
            return parts
        if parts:
            out: list[str] = []
            for p in parts:
                out.extend(_split_part_until_fit(p, max_units))
            return out

    return _chunk_by_units(text, max_units)


def _chunk_by_units(text: str, max_units: float) -> list[str]:
    """无标点兜底：按视觉宽度贪心切分（仅显示层，不影响 TTS）。"""
    text = strip_sub_punct(text)
    if visual_units(text) <= max_units:
        return [text]
    parts: list[str] = []
    buf = ""
    for ch in text:
        cand = buf + ch
        if visual_units(cand) <= max_units:
            buf = cand
        else:
            if buf:
                parts.append(buf)
            buf = ch
    if buf:
        parts.append(buf)
    return parts if parts else [text]


def get_subtitle_parts(item: dict, max_han: int) -> list[str]:
    if "subtitleParts" in item and item["subtitleParts"]:
        return [strip_sub_punct(str(p)) for p in item["subtitleParts"]]
    sub = item.get("subtitle")
    if isinstance(sub, list) and sub:
        return [strip_sub_punct(str(p)) for p in sub]
    if isinstance(sub, str) and sub.strip():
        return [strip_sub_punct(sub)]
    return split_subtitle_display(voice_text(item), max_han)


def line_scene(item: dict) -> int:
    if "scene" in item:
        return int(item["scene"])
    m = re.match(r"^s(\d+)", item.get("id", ""))
    if m:
        return int(m.group(1))
    return 1


def validate_subtitle_parts(
    line_id: str, parts: list[str], max_han: int, orient: str
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    for j, part in enumerate(parts):
        sub_id = line_id if j == 0 else f"{line_id}_sub{j + 1}"
        units = visual_units(part)
        if units > max_han:
            errors.append(
                f"{sub_id}: 字幕约 {units:.1f} 单位 > {orient}上限 {max_han}，"
                f"请调整 subtitle/subtitleParts 或在逗号/句号处继续拆显示层"
            )
        core = strip_for_check(part)
        for tail in FORBIDDEN_TAIL:
            if core.endswith(tail) and len(core) > len(tail):
                errors.append(
                    f"{sub_id}: 字幕断句错误 — 以「{tail}」结尾，"
                    f"禁止拦腰断（改 subtitle 断点）"
                )
                break
        if j > 0:
            head = strip_for_check(part)[:1]
            if head in FORBIDDEN_HEAD:
                warnings.append(f"{sub_id}: 以「{head}」开头，确认上条字幕断点是否合理")
    return errors, warnings


def warn_tts_over_split(lines: list[dict]) -> list[str]:
    warnings: list[str] = []
    for i in range(1, len(lines)):
        prev, curr = lines[i - 1], lines[i]
        if line_scene(prev) != line_scene(curr):
            continue
        prev_id = prev.get("id", "")
        curr_id = curr.get("id", "")
        m_prev = re.match(r"^(.+?)([a-z]+)$", prev_id)
        m_curr = re.match(r"^(.+?)([a-z]+)$", curr_id)
        if m_prev and m_curr and m_prev.group(1) == m_curr.group(1):
            warnings.append(
                f"{prev_id}+{curr_id}: 疑似为字幕宽度拆成多段 TTS — "
                f"应合并为一条 voice（一条 wav），字幕用 subtitle/subtitleParts 拆显示"
            )
            continue
        prev_speak = tts_payload(prev)
        curr_speak = tts_payload(curr)
        if prev_speak == curr_speak:
            warnings.append(
                f"{prev_id}+{curr_id}: speak 相同却分成两条 wav — 检查是否误拆 TTS"
            )
    return warnings


def validate_lines(lines: list[dict]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    max_han, vertical = load_subtitle_limits()
    orient = "竖屏" if vertical else "横屏"

    for i, item in enumerate(lines):
        line_id = item.get("id", f"#{i}")
        voice = voice_text(item)
        if not voice:
            errors.append(f"{line_id}: voice/text 为空（TTS 口播必填）")
            continue

        units = visual_units(voice)
        if units > max_han:
            warnings.append(
                f"{line_id}: 口播约 {units:.1f} 单位 > {orient}字幕显示上限 {max_han} — "
                f"TTS 保持整句一条 wav；请规划 subtitle/subtitleParts 或交给脚本自动拆上屏"
            )
        elif units > max_han + 8:
            warnings.append(
                f"{line_id}: 口播较长（{units:.1f} 单位），注意节奏；勿为字幕拆 TTS id"
            )

        parts = get_subtitle_parts(item, max_han)
        sub_errs, sub_warns = validate_subtitle_parts(line_id, parts, max_han, orient)
        errors.extend(sub_errs)
        warnings.extend(sub_warns)

        if re.search(r"[A-Za-z]{2,}", voice) and not item.get("speak"):
            warnings.append(
                f"{line_id}: 含英文/专有名词，建议加 speak 字段修正读音"
                f"（如 OpenClaw → Open Claw）"
            )

    warnings.extend(warn_tts_over_split(lines))
    return errors, warnings


async def synth_line(line_id: str, speak_text: str) -> Path:
    mp3 = OUT_DIR / f"{line_id}.mp3"
    wav = OUT_DIR / f"{line_id}.wav"
    communicate = edge_tts.Communicate(speak_text, VOICE, rate=RATE)
    await communicate.save(str(mp3))
    subprocess.check_call(
        ["ffmpeg", "-y", "-i", str(mp3), "-ar", "44100", "-ac", "1", str(wav)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    mp3.unlink(missing_ok=True)
    return wav


def probe_duration(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        text=True,
    )
    return round(float(out.strip()), 3)


def concat_voiceover(wavs: list[Path], out_path: Path) -> None:
    list_file = OUT_DIR / "_concat.txt"
    list_lines = [f"file '{w.resolve().as_posix()}'" for w in wavs]
    list_file.write_text("\n".join(list_lines) + "\n", encoding="utf-8")
    subprocess.check_call(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_file),
            "-ar",
            "44100",
            "-ac",
            "1",
            str(out_path),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    list_file.unlink(missing_ok=True)


async def main() -> None:
    lines = json.loads(LINES_PATH.read_text(encoding="utf-8"))
    max_han, vertical = load_subtitle_limits()
    print(f"字幕显示上限: {max_han} 单位 ({'竖屏' if vertical else '横屏'}, meta.json)")
    print("TTS 粒度: 每条 lines.json = 一个 wav（不因字幕宽度拆 id）")

    errors, warnings = validate_lines(lines)
    for w in warnings:
        print(f"WARN: {w}")
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        print(
            "\n请修正 audio/lines.json 后重跑。"
            "规则见 templates/subtitle-tts-guide.md",
            file=sys.stderr,
        )
        sys.exit(1)

    schedule = []
    wavs = []
    t = 0.0

    for item in lines:
        line_id = item["id"]
        voice = voice_text(item)
        speak = tts_payload(item)
        scene = line_scene(item)
        subtitle_parts = get_subtitle_parts(item, max_han)
        label = speak if speak != voice else voice
        print(f"TTS {line_id} (sc{scene}): {label}")
        if len(subtitle_parts) > 1:
            print(f"  字幕 {len(subtitle_parts)} 条共享本段音频: {subtitle_parts}")
        wav = await synth_line(line_id, speak)
        wavs.append(wav)
        duration = probe_duration(wav)
        show_end = round(t + duration, 3)
        row = {
            "id": line_id,
            "scene": scene,
            "voice": voice,
            "text": voice,  # 兼容旧脚本读 text
            "textHash": text_hash(voice),
            "subtitleParts": subtitle_parts,
            "src": f"audio/segments/{line_id}.wav",
            "start": round(t, 3),
            "duration": duration,
            "showEnd": show_end,
        }
        if speak != voice:
            row["speak"] = speak
            row["speakHash"] = text_hash(speak)
        schedule.append(row)
        t = show_end + GAP

    concat_voiceover(wavs, VOICEOVER)
    total_duration = round(schedule[-1]["showEnd"], 3)
    voiceover_hash = text_hash("".join(tts_payload(item) for item in lines))

    scene_times: dict[str, dict] = {}
    scenes: dict[int, list] = {}
    for row in schedule:
        scenes.setdefault(row["scene"], []).append(row)

    for scene_num, rows in sorted(scenes.items()):
        scene_id = f"sc{scene_num}"
        scene_times[scene_id] = {
            "start": rows[0]["start"],
            "duration": round(rows[-1]["showEnd"] - rows[0]["start"], 3),
        }

    payload = {
        "voice": VOICE,
        "rate": RATE,
        "voiceoverHash": voiceover_hash,
        "subtitleMaxUnits": max_han,
        "schedule": schedule,
        "sceneTimes": scene_times,
        "totalDuration": total_duration,
    }
    (ROOT / "audio/schedule.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nVoiceover: {VOICEOVER} ({probe_duration(VOICEOVER)}s)")
    print(f"Total duration: {total_duration}s | hash: {voiceover_hash}")
    print(f"TTS 条数: {len(lines)}（= wav 段数，非字幕条数）")
    print("下一步: python scripts/align-subtitles.py  （Whisper 词级时间戳 → audio/alignments.json）")
    if total_duration > 150 and RATE != "+18%":
        print("提示: 总时长 >150s，建议将 RATE 改为 '+18%' 后重跑本脚本")


if __name__ == "__main__":
    asyncio.run(main())
