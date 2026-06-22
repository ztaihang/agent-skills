#!/usr/bin/env python3
"""Fallback alignments.json when faster-whisper crashes — speak-aware part timing."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEDULE_PATH = ROOT / "audio/schedule.json"
OUT_PATH = ROOT / "audio/alignments.json"


def strip_sub_punct(text: str) -> str:
    return re.sub(r"[，。！？：；、]+$", "", text.strip())


def visual_units(text: str) -> float:
    plain = re.sub(r"[，。！？：；、\s]+", "", text)
    han = len(re.findall(r"[\u4e00-\u9fff]", plain))
    ascii_count = len(re.findall(r"[\x00-\x7f]", plain))
    return han + ascii_count * 0.55


def speak_timing_weight(text: str) -> float:
    raw = str(text or "")
    han = len(re.findall(r"[\u4e00-\u9fff]", raw))
    ascii_count = len(re.findall(r"[\x00-\x7f]", raw))
    spaces = len(re.findall(r"\s", raw))
    hyphens = raw.count("-")
    return max(1.0, han + ascii_count * 0.95 + spaces * 0.55 + hyphens * 0.4)


def is_ignorable_voice_char(ch: str) -> bool:
    return bool(re.match(r"[\s，。！？：；、\u201c\u201d\u2018\u2019「」『』\"']", ch))


def chars_to_match(text: str) -> str:
    out: list[str] = []
    for ch in text:
        if is_ignorable_voice_char(ch):
            continue
        out.append(ch.lower())
    return "".join(out)


def token_at(voice: str, vi: int) -> tuple[str, int] | None:
    slice_ = voice[vi:]
    m = re.match(r"^agent\b", slice_, re.I)
    if m:
        return "agent", m.end()
    m = re.match(r"^a[\s-]?i\b", slice_, re.I)
    if m:
        return "ai", m.end()
    return None


def normalize_from(voice: str, from_idx: int) -> tuple[str, list[int]]:
    norm = ""
    end_at: list[int] = []
    i = from_idx
    while i < len(voice):
        ch = voice[i]
        if is_ignorable_voice_char(ch):
            i += 1
            continue
        tok = token_at(voice, i)
        if tok:
            text, length = tok
            norm += text
            end_at.append(i + length)
            i += length
            continue
        norm += ch.lower()
        end_at.append(i + 1)
        i += 1
    return norm, end_at


def find_part_end_pos(voice: str, part: str, from_idx: int) -> int:
    targets = chars_to_match(part)
    if not targets:
        return from_idx

    norm, end_at = normalize_from(voice, from_idx)
    idx = norm.find(targets)
    if idx < 0:
        remaining = max(1, len(voice) - from_idx)
        return min(len(voice), from_idx + int((len(targets) / max(1, len(norm))) * remaining + 0.5))
    return end_at[idx + len(targets) - 1] if idx + len(targets) - 1 < len(end_at) else len(voice)


def voice_part_boundaries(voice: str, parts: list[str]) -> list[int]:
    pos = 0
    out: list[int] = []
    for part in parts:
        pos = find_part_end_pos(voice, part, pos)
        out.append(pos)
    return out


def speak_segment_for_part(voice: str, speak: str, prev_pos: int, curr_pos: int) -> str:
    v_len = max(1, len(voice))
    s_len = len(speak)
    s0 = int((prev_pos / v_len) * s_len)
    s1 = max(s0 + 1, int((curr_pos / v_len) * s_len + 0.999))
    return speak[s0:s1]


VISUAL_BLEND = 0.58
SPEAK_BLEND = 0.42


def normalize_speak(text: str) -> str:
    s = str(text or "").strip()
    s = re.sub(r"([\u4e00-\u9fff\d]+)\s+个", r"\1个", s)
    s = re.sub(r"(\d+)\s+个", r"\1个", s)
    return s


def part_weights(row: dict, parts: list[str], boundaries: list[int]) -> list[float]:
    voice = row.get("voice") or row.get("text") or ""
    speak = normalize_speak(row.get("speak") or voice)
    weights: list[float] = []
    for i, part in enumerate(parts):
        prev_pos = 0 if i == 0 else boundaries[i - 1]
        curr_pos = boundaries[i]
        visual = max(1.0, visual_units(part))
        if speak != normalize_speak(voice):
            seg = speak_segment_for_part(voice, speak, prev_pos, curr_pos)
            spoken = speak_timing_weight(seg)
            base = visual * VISUAL_BLEND + spoken * SPEAK_BLEND
        else:
            base = visual
        weights.append(max(1.0, base))
    return weights


def wav_duration(path: Path) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        text=True,
    )
    return float(out.strip())


def parts_for_row(row: dict) -> list[str]:
    if row.get("subtitleParts"):
        return [strip_sub_punct(str(p)) for p in row["subtitleParts"]]
    voice = row.get("voice") or row.get("text") or ""
    return [strip_sub_punct(voice)]


def main() -> None:
    data = json.loads(SCHEDULE_PATH.read_text(encoding="utf-8"))
    schedule = data["schedule"]
    lines_out = {}

    for row in schedule:
        wav = ROOT / row["src"]
        seg_dur = wav_duration(wav) if wav.exists() else float(row["duration"])
        parts = parts_for_row(row)
        voice = row.get("voice") or row.get("text") or ""
        boundaries = voice_part_boundaries(voice, parts)
        weights = part_weights(row, parts, boundaries)
        total_w = sum(weights)
        t = 0.0
        aligned = []
        for i, part in enumerate(parts):
            part_dur = seg_dur * weights[i] / total_w
            end = seg_dur if i == len(parts) - 1 else round(t + part_dur, 3)
            aligned.append({"index": i, "text": part, "start": round(t, 3), "end": round(end, 3)})
            t = end
        lines_out[row["id"]] = {
            "id": row["id"],
            "duration": seg_dur,
            "matchRatio": 1.0,
            "parts": aligned,
            "mode": "fallback-weight",
        }

    payload = {
        "model": "fallback-weight",
        "engine": "fallback",
        "voiceoverHash": data.get("voiceoverHash"),
        "lines": lines_out,
    }
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_PATH} ({len(lines_out)} lines, fallback speak-weight mode)")
    print("WARN: 精度低于 align-subtitles.py — 交付前须听检多 part 字幕镜")


if __name__ == "__main__":
    main()
