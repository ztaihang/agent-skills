#!/usr/bin/env python3
"""Forced-align each TTS segment wav to subtitleParts via faster-whisper word timestamps.

Reads audio/schedule.json + segment wavs, writes audio/alignments.json.
Times in alignments are relative to each segment (0 = line wav start).

Alignment uses speak (TTS audio) for Whisper; subtitleParts must be contiguous
substrings of voice — see templates/subtitle-tts-guide.md §1.1.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEDULE_PATH = ROOT / "audio/schedule.json"
OUT_PATH = ROOT / "audio/alignments.json"
MODEL_NAME = "small"
SUB_PAD_START = 0.02
SUB_PAD_END = 0.04
MATCH_FALLBACK = 0.45

try:
    from faster_whisper import WhisperModel
except ImportError as exc:
    print("ERROR: faster-whisper required. pip install faster-whisper", file=sys.stderr)
    raise SystemExit(1) from exc


def is_ignorable(ch: str) -> bool:
    return bool(re.match(r'[\s，。！？：；、\u201c\u201d\u2018\u2019「」『』"\']', ch))


def norm_text(text: str) -> str:
    out: list[str] = []
    i = 0
    while i < len(text):
        if is_ignorable(text[i]):
            i += 1
            continue
        sl = text[i:]
        if re.match(r"^c\s*\+\+", sl, re.I):
            out.append("c++")
            i += len(re.match(r"^c\s*\+\+", sl, re.I).group())
            continue
        if re.match(r"^c\s*加加", sl):
            out.append("c++")
            i += len(re.match(r"^c\s*加加", sl).group())
            continue
        if re.match(r"^x\s*code", sl, re.I):
            out.append("xcode")
            i += len(re.match(r"^x\s*code", sl, re.I).group())
            continue
        if re.match(r"^solid\s*works", sl, re.I):
            out.append("solidworks")
            i += len(re.match(r"^solid\s*works", sl, re.I).group())
            continue
        if re.match(r"^open\s*claw", sl, re.I):
            out.append("openclaw")
            i += len(re.match(r"^open\s*claw", sl, re.I).group())
            continue
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
        remaining_parts_chars = len(targets)
        voice_remaining = len(norm_text(voice[from_idx:]))
        if voice_remaining <= 0:
            return len(voice)
        share = min(1.0, remaining_parts_chars / max(1, voice_remaining))
        advance = max(1, int(len(voice[from_idx:]) * share))
        return min(len(voice), from_idx + advance)
    vi = from_idx
    matched = 0
    while vi < len(voice) and matched < len(targets):
        if is_ignorable(voice[vi]):
            vi += 1
            continue
        sl = voice[vi:]
        if re.match(r"^c\s*\+\+", sl, re.I):
            vi += len(re.match(r"^c\s*\+\+", sl, re.I).group())
            matched += 3
            continue
        if re.match(r"^c\s*加加", sl):
            vi += len(re.match(r"^c\s*加加", sl).group())
            matched += 3
            continue
        if re.match(r"^x\s*code", sl, re.I):
            vi += len(re.match(r"^x\s*code", sl, re.I).group())
            matched += 5
            continue
        if re.match(r"^solid\s*works", sl, re.I):
            vi += len(re.match(r"^solid\s*works", sl, re.I).group())
            matched += 10
            continue
        if re.match(r"^open\s*claw", sl, re.I):
            vi += len(re.match(r"^open\s*claw", sl, re.I).group())
            matched += 8
            continue
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


def build_norm_char_map(src_norm: str, dst_norm: str) -> list[int]:
    sm = difflib.SequenceMatcher(None, src_norm, dst_norm)
    src2dst = [0] * len(src_norm)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                src2dst[i1 + k] = j1 + k
        else:
            for k in range(i1, i2):
                off = k - i1
                span = max(1, j2 - j1)
                src2dst[k] = j1 + min(off, span - 1)
    return src2dst


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


def norm_idx_for_pos(text: str, pos: int) -> int:
    return len(norm_text(text[:pos]))


def proportional_align(line_id: str, parts: list[str], seg_dur: float) -> dict:
    weights = [max(1, len(norm_text(p))) for p in parts]
    total = sum(weights)
    aligned: list[dict] = []
    t = 0.0
    for i, part in enumerate(parts):
        if i == len(parts) - 1:
            end = seg_dur
        else:
            end = min(seg_dur, t + (weights[i] / total) * seg_dur)
        aligned.append(
            {
                "index": i,
                "text": part,
                "start": round(t, 3),
                "end": round(end, 3),
            }
        )
        t = end
    return {
        "id": line_id,
        "duration": seg_dur,
        "voiceNormLen": sum(weights),
        "transNormLen": 0,
        "matchRatio": 0.0,
        "parts": aligned,
        "mode": "proportional",
    }


def rebalance_parts(aligned_parts: list[dict], seg_dur: float) -> list[dict]:
    if len(aligned_parts) <= 1:
        return aligned_parts
    weights = [max(1, len(norm_text(p["text"]))) for p in aligned_parts]
    total = sum(weights)
    out: list[dict] = []
    t = 0.0
    for i, p in enumerate(aligned_parts):
        share = weights[i] / total * seg_dur
        min_dur = max(1.1, share * 0.72)
        start = t if i == 0 else max(t, p["start"])
        whisper_dur = max(0.001, p["end"] - p["start"])
        dur = max(min_dur, whisper_dur * 0.45 + share * 0.55)
        if i == len(aligned_parts) - 1:
            end = seg_dur
        else:
            end = min(seg_dur - 0.35 * (len(aligned_parts) - i - 1), start + dur)
        out.append({**p, "start": round(start, 3), "end": round(end, 3)})
        t = end
    out[-1]["end"] = round(seg_dur, 3)
    return out


def align_line(model: WhisperModel, row: dict) -> dict:
    line_id = row["id"]
    voice = row.get("voice") or row.get("text") or ""
    speak = row.get("speak") or voice
    parts = row.get("subtitleParts") or [voice]
    wav = ROOT / row["src"].replace("/", "\\") if "\\" in row["src"] else ROOT / row["src"]
    if not wav.exists():
        raise FileNotFoundError(f"{line_id}: missing {wav}")

    seg_dur = float(row["duration"])
    tokens = transcribe_tokens(model, wav, speak)
    if not tokens:
        out = proportional_align(line_id, parts, seg_dur)
        out["mode"] = "proportional-no-whisper"
        out["parts"] = rebalance_parts(out["parts"], seg_dur)
        return out

    char_time: list[tuple[float, float]] = []
    for tok in tokens:
        for _ in tok["t"]:
            char_time.append((tok["start"], tok["end"]))

    speak_norm = norm_text(speak)
    trans_norm = "".join(t["t"] for t in tokens)
    match_ratio = difflib.SequenceMatcher(None, speak_norm, trans_norm).ratio()
    if match_ratio < MATCH_FALLBACK:
        out = proportional_align(line_id, parts, seg_dur)
        out["matchRatio"] = round(match_ratio, 3)
        out["mode"] = "proportional-fallback"
        out["parts"] = rebalance_parts(out["parts"], seg_dur)
        return out

    v2t = build_voice_to_trans_map(speak_norm, trans_norm)
    voice_norm = norm_text(voice)
    v2s = build_norm_char_map(voice_norm, speak_norm)

    def time_for_speak_idx(idx: int, pick_end: bool) -> float:
        if not char_time:
            return 0.0
        ti = v2t[min(max(idx, 0), len(v2t) - 1)] if v2t else 0
        ti = min(max(ti, 0), len(char_time) - 1)
        return char_time[ti][1 if pick_end else 0]

    aligned_parts: list[dict] = []
    pos = 0
    for i, part in enumerate(parts):
        end_pos = find_part_end(voice, part, pos)
        if end_pos <= pos:
            end_pos = min(len(voice), pos + max(1, len(part)))
        i0_v = norm_idx_for_pos(voice, pos)
        i1_v = max(i0_v + 1, norm_idx_for_pos(voice, end_pos))
        i0_s = v2s[min(i0_v, len(v2s) - 1)] if v2s else 0
        i1_s = v2s[min(max(i1_v - 1, 0), len(v2s) - 1)] if v2s else 0
        start = max(0.0, time_for_speak_idx(i0_s, pick_end=False) - (0 if i == 0 else SUB_PAD_START))
        end = min(seg_dur, time_for_speak_idx(i1_s, pick_end=True) + SUB_PAD_END)
        if i > 0 and aligned_parts:
            start = max(start, aligned_parts[-1]["end"] + 0.02)
        if end <= start:
            end = min(seg_dur, start + max(0.35, seg_dur / max(1, len(parts)) * 0.55))
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
        aligned_parts = rebalance_parts(aligned_parts, seg_dur)

    return {
        "id": line_id,
        "duration": seg_dur,
        "voiceNormLen": len(speak_norm),
        "transNormLen": len(trans_norm),
        "matchRatio": round(match_ratio, 3),
        "parts": aligned_parts,
        "mode": "whisper",
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Whisper forced alignment for subtitle parts")
    p.add_argument("--model", default=MODEL_NAME, help="faster-whisper model size")
    p.add_argument("--compute-type", default="int8", help="ctranslate2 compute type")
    p.add_argument(
        "--smoke-only",
        action="store_true",
        help="Load model and transcribe first segment only (for run-align.py probes)",
    )
    return p.parse_args()


def smoke_test(model: WhisperModel, schedule: list[dict]) -> bool:
    row = next((r for r in schedule if r.get("src")), None)
    if not row:
        return False
    wav = ROOT / row["src"].replace("\\", "/")
    if not wav.exists():
        return False
    speak = row.get("speak") or row.get("voice") or row.get("text") or ""
    try:
        tokens = transcribe_tokens(model, wav, speak)
    except Exception as exc:
        print(f"SMOKE transcribe error: {exc}", file=sys.stderr)
        return False
    return len(tokens) > 0


def main() -> None:
    args = parse_args()
    if not SCHEDULE_PATH.exists():
        print("ERROR: run generate-tts.py first (missing schedule.json)", file=sys.stderr)
        raise SystemExit(1)

    data = json.loads(SCHEDULE_PATH.read_text(encoding="utf-8"))
    schedule = data["schedule"]
    print(f"Loading faster-whisper model: {args.model} ({args.compute_type})")
    model = WhisperModel(args.model, device="cpu", compute_type=args.compute_type)

    if args.smoke_only:
        ok = smoke_test(model, schedule)
        if ok:
            print(f"SMOKE OK model={args.model} compute={args.compute_type}")
            raise SystemExit(0)
        print(f"SMOKE FAIL model={args.model} compute={args.compute_type}", file=sys.stderr)
        raise SystemExit(1)

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
        "model": args.model,
        "computeType": args.compute_type,
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
        raise SystemExit(1)


if __name__ == "__main__":
    main()
