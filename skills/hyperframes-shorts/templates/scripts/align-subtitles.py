#!/usr/bin/env python3
"""Forced-align each TTS segment wav to subtitleParts via faster-whisper word timestamps.

Reads audio/schedule.json + segment wavs, writes audio/alignments.json.
Times in alignments are relative to each segment (0 = line wav start).
"""
from __future__ import annotations

import difflib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEDULE_PATH = ROOT / "audio/schedule.json"
OUT_PATH = ROOT / "audio/alignments.json"
MODEL_NAME = "base"
SUB_PAD_START = 0.04
SUB_PAD_END = 0.06

try:
    from faster_whisper import WhisperModel
except ImportError as exc:
    print("ERROR: faster-whisper required. pip install faster-whisper", file=sys.stderr)
    raise SystemExit(1) from exc


def is_ignorable(ch: str) -> bool:
    # 口播 voice 常含弯引号/书名号，subtitleParts 往往省略 — 对齐时一律跳过
    return bool(re.match(r'[\s，。！？：；、\u201c\u201d\u2018\u2019「」『』"\']', ch))


def norm_text(text: str) -> str:
    out: list[str] = []
    i = 0
    while i < len(text):
        if is_ignorable(text[i]):
            i += 1
            continue
        sl = text[i:]
        if re.match(r"^agent\b", sl, re.I):
            out.append("agent")
            i += len(re.match(r"^agent", sl, re.I).group())
            continue
        if re.match(r"^a[\s-]?i\b", sl, re.I):
            out.append("ai")
            i += len(re.match(r"^a[\s-]?i", sl, re.I).group())
            continue
        out.append(text[i].lower())
        i += 1
    return "".join(out)


def word_tokens(word: str, start: float, end: float) -> list[dict]:
    s = word.strip()
    toks: list[dict] = []
    i = 0
    while i < len(s):
        if is_ignorable(s[i]):
            i += 1
            continue
        sl = s[i:]
        if re.match(r"^agent\b", sl, re.I):
            m = re.match(r"^agent", sl, re.I)
            toks.append({"t": "agent", "start": start, "end": end})
            i += len(m.group())
            continue
        if re.match(r"^a[\s-]?i\b", sl, re.I):
            m = re.match(r"^a[\s-]?i", sl, re.I)
            toks.append({"t": "ai", "start": start, "end": end})
            i += len(m.group())
            continue
        toks.append({"t": s[i].lower(), "start": start, "end": end})
        i += 1
    return toks


def find_part_end(voice: str, part: str, from_idx: int) -> int:
    targets = norm_text(part)
    if not targets:
        return from_idx
    vn = norm_text(voice[from_idx:])
    if targets not in vn:
        remaining = max(1, len(voice) - from_idx)
        return min(len(voice), from_idx + max(1, len(part) // 2))
    vi = from_idx
    matched = 0
    while vi < len(voice) and matched < len(targets):
        if is_ignorable(voice[vi]):
            vi += 1
            continue
        sl = voice[vi:]
        if re.match(r"^agent\b", sl, re.I):
            vi += len(re.match(r"^agent", sl, re.I).group())
            matched += 5
            continue
        if re.match(r"^a[\s-]?i\b", sl, re.I):
            vi += len(re.match(r"^a[\s-]?i", sl, re.I).group())
            matched += 2
            continue
        vi += 1
        matched += 1
    return vi


def build_voice_to_trans_map(voice_norm: str, trans_norm: str) -> list[int]:
    sm = difflib.SequenceMatcher(None, voice_norm, trans_norm)
    v2t = [0] * len(voice_norm)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                v2t[i1 + k] = j1 + k
        else:
            for k in range(i1, i2):
                off = k - i1
                span = max(1, j2 - j1)
                v2t[k] = j1 + min(off, span - 1)
    return v2t


def transcribe_tokens(model: WhisperModel, wav: Path, prompt: str) -> list[dict]:
    segments, _ = model.transcribe(
        str(wav),
        language="zh",
        word_timestamps=True,
        initial_prompt=prompt,
        vad_filter=False,
    )
    tokens: list[dict] = []
    for seg in segments:
        if not seg.words:
            continue
        for w in seg.words:
            tokens.extend(word_tokens(w.word, float(w.start), float(w.end)))
    return tokens


def align_line(model: WhisperModel, row: dict) -> dict:
    line_id = row["id"]
    voice = row.get("voice") or row.get("text") or ""
    speak = row.get("speak") or voice
    parts = row.get("subtitleParts") or [voice]
    wav = ROOT / row["src"].replace("/", "\\") if "\\" in row["src"] else ROOT / row["src"]
    if not wav.exists():
        raise FileNotFoundError(f"{line_id}: missing {wav}")

    tokens = transcribe_tokens(model, wav, speak)
    if not tokens:
        raise RuntimeError(f"{line_id}: no word timestamps from whisper")

    char_time: list[tuple[float, float]] = []
    for tok in tokens:
        for _ in tok["t"]:
            char_time.append((tok["start"], tok["end"]))

    voice_norm = norm_text(voice)
    trans_norm = "".join(t["t"] for t in tokens)
    v2t = build_voice_to_trans_map(voice_norm, trans_norm)
    seg_dur = float(row["duration"])

    def norm_idx_for_pos(pos: int) -> int:
        return len(norm_text(voice[:pos]))

    def time_for_norm_idx(idx: int, pick_end: bool) -> float:
        if not char_time:
            return 0.0
        ti = v2t[min(max(idx, 0), len(v2t) - 1)] if v2t else 0
        ti = min(max(ti, 0), len(char_time) - 1)
        return char_time[ti][1 if pick_end else 0]

    aligned_parts: list[dict] = []
    pos = 0
    for i, part in enumerate(parts):
        end_pos = find_part_end(voice, part, pos)
        i0 = norm_idx_for_pos(pos)
        i1 = max(i0 + 1, norm_idx_for_pos(end_pos))
        start = max(0.0, time_for_norm_idx(i0, pick_end=False) - (0 if i == 0 else SUB_PAD_START))
        end = min(seg_dur, time_for_norm_idx(i1 - 1, pick_end=True) + SUB_PAD_END)
        if i > 0 and aligned_parts:
            start = max(start, aligned_parts[-1]["end"] + 0.02)
        if end <= start:
            end = min(seg_dur, start + 0.25)
        aligned_parts.append(
            {
                "index": i,
                "text": part,
                "start": round(start, 3),
                "end": round(end, 3),
            }
        )
        pos = end_pos

    if aligned_parts:
        aligned_parts[-1]["end"] = round(seg_dur, 3)

    return {
        "id": line_id,
        "duration": seg_dur,
        "voiceNormLen": len(voice_norm),
        "transNormLen": len(trans_norm),
        "matchRatio": round(difflib.SequenceMatcher(None, voice_norm, trans_norm).ratio(), 3),
        "parts": aligned_parts,
    }


def main() -> None:
    if not SCHEDULE_PATH.exists():
        print("ERROR: run generate-tts.py first (missing schedule.json)", file=sys.stderr)
        raise SystemExit(1)

    data = json.loads(SCHEDULE_PATH.read_text(encoding="utf-8"))
    schedule = data["schedule"]
    print(f"Loading faster-whisper model: {MODEL_NAME}")
    model = WhisperModel(MODEL_NAME, device="cpu", compute_type="int8")

    lines_out: dict[str, dict] = {}
    errors: list[str] = []

    for row in schedule:
        line_id = row["id"]
        try:
            result = align_line(model, row)
            lines_out[line_id] = result
            parts = result["parts"]
            preview = " | ".join(f"{p['start']:.2f}-{p['end']:.2f}" for p in parts[:3])
            print(f"OK {line_id} ratio={result['matchRatio']:.2f} [{preview}…]")
        except Exception as exc:
            errors.append(f"{line_id}: {exc}")
            print(f"FAIL {line_id}: {exc}", file=sys.stderr)

    payload = {
        "model": MODEL_NAME,
        "engine": "faster-whisper",
        "voiceoverHash": data.get("voiceoverHash"),
        "lines": lines_out,
    }
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {OUT_PATH} ({len(lines_out)}/{len(schedule)} lines)")

    if errors:
        print(f"WARNING: {len(errors)} line(s) failed alignment", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
