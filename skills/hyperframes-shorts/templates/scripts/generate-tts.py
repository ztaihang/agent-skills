#!/usr/bin/env python3
"""Per-line Edge TTS → segments/*.wav, concat voiceover.wav, write schedule.json."""
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

# 上句结尾禁止（易拦腰断句）— 见 templates/subtitle-tts-guide.md
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
    "把",
)

# 下句开头禁止（上句已断错）
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


def validate_lines(lines: list[dict]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    max_han, vertical = load_subtitle_limits()
    orient = "竖屏" if vertical else "横屏"

    for i, item in enumerate(lines):
        line_id = item.get("id", f"#{i}")
        text = item.get("text", "")
        if not text.strip():
            errors.append(f"{line_id}: text 为空")
            continue

        units = visual_units(text)
        if units > max_han:
            errors.append(
                f"{line_id}: 字幕约 {units:.1f} 单位 > {orient}上限 {max_han}，"
                f"请按语义拆条（见 subtitle-tts-guide.md）"
            )
        elif units <= max_han - 4 and i + 1 < len(lines):
            nxt = lines[i + 1]
            if line_scene(item) == line_scene(nxt):
                u1 = visual_units(text)
                u2 = visual_units(nxt.get("text", ""))
                if u1 + u2 <= max_han + 1:
                    warnings.append(
                        f"{line_id}+{nxt.get('id')}: 同镜相邻两条合计可合并为一条"
                        f"（{u1 + u2:.1f} ≤ {max_han}），避免碎句"
                    )

        core = strip_for_check(text)
        for tail in FORBIDDEN_TAIL:
            if core.endswith(tail) and len(core) > len(tail):
                errors.append(
                    f"{line_id}: 断句错误 — 以「{tail}」结尾，"
                    f"易出现「{tail} | …」拦腰断（改断点或合并）"
                )
                break

        if i > 0:
            prev = lines[i - 1]
            if line_scene(prev) == line_scene(item):
                prev_core = strip_for_check(prev.get("text", ""))
                for tail in ("让我的", "让你的", "让其", "我的", "你的"):
                    if prev_core.endswith(tail):
                        head = strip_for_check(text)[:2]
                        errors.append(
                            f"{prev.get('id')}+{line_id}: 典型错误断句 "
                            f"「…{tail}」|「{text[:8]}…」— 禁止"
                        )
                        break

        head = strip_for_check(text)[:1]
        if head in FORBIDDEN_HEAD and i > 0:
            prev = lines[i - 1]
            if line_scene(prev) == line_scene(item):
                warnings.append(f"{line_id}: 以「{head}」开头，确认上句断点是否合理")

        if re.search(r"[A-Za-z]{2,}", text) and not item.get("speak"):
            warnings.append(
                f"{line_id}: 含英文/专有名词，建议加 speak 字段修正读音"
                f"（如 OpenClaw → Open Claw）"
            )

    return errors, warnings


def line_scene(item: dict) -> int:
    if "scene" in item:
        return int(item["scene"])
    m = re.match(r"^s(\d+)", item.get("id", ""))
    if m:
        return int(m.group(1))
    return 1


def tts_payload(item: dict) -> str:
    return item.get("speak") or item.get("tts") or item["text"]


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
    print(f"字幕上限: {max_han} 单位 ({'竖屏' if vertical else '横屏'}, meta.json)")

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
        text = item["text"]
        speak = tts_payload(item)
        scene = line_scene(item)
        label = f"{speak}" if speak != text else text
        print(f"TTS {line_id} (sc{scene}): {label}")
        wav = await synth_line(line_id, speak)
        wavs.append(wav)
        duration = probe_duration(wav)
        show_end = round(t + duration, 3)
        row = {
            "id": line_id,
            "scene": scene,
            "text": text,
            "textHash": text_hash(text),
            "src": f"audio/segments/{line_id}.wav",
            "start": round(t, 3),
            "duration": duration,
            "showEnd": show_end,
        }
        if speak != text:
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
    if total_duration > 150 and RATE != "+18%":
        print("提示: 总时长 >150s，建议将 RATE 改为 '+18%' 后重跑本脚本")


if __name__ == "__main__":
    asyncio.run(main())
