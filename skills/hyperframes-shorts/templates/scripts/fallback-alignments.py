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
    zh_digits = len(re.findall(r"[零一二三四五六七八九十百千万]", raw))
    pct_markers = len(re.findall(r"百分之", raw))
    # 中文数字与「百分之」口播明显慢于同字数汉字
    spoken_extra = zh_digits * 0.22 + pct_markers * 1.8
    return max(1.0, han + ascii_count * 0.95 + spaces * 0.55 + hyphens * 0.4 + spoken_extra)


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
    speak_parts = row.get("subtitleSpeakParts")
    if speak_parts and len(speak_parts) == len(parts):
        return [max(1.0, speak_timing_weight(normalize_speak(str(p)))) for p in speak_parts]

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


def detect_silence_events(wav: Path) -> list[tuple[str, float]]:
    """Return [(kind, time), ...] from ffmpeg silencedetect."""
    try:
        proc = subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-i",
                str(wav),
                "-af",
                "silencedetect=noise=-30dB:d=0.12",
                "-f",
                "null",
                "-",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return []
    events: list[tuple[str, float]] = []
    for line in (proc.stderr or "").splitlines():
        m = re.search(r"silence_(start|end):\s*([\d.]+)", line)
        if m:
            events.append((m.group(1), float(m.group(2))))
    return events


def speech_window(seg_dur: float, events: list[tuple[str, float]]) -> tuple[float, float]:
    """Active speech window inside a segment wav (skip lead/trail silence)."""
    lead = 0.12
    tail = 0.08
    if events:
        if events[0][0] == "start" and events[0][1] <= 0.05:
            for kind, t in events:
                if kind == "end" and t > 0.04:
                    lead = min(0.45, t)
                    break
        if events[-1][0] == "start":
            tail = max(0.06, min(0.65, seg_dur - events[-1][1]))
    active_end = max(lead + 0.35, seg_dur - tail)
    return lead, active_end


def speak_diff_significant(voice: str, speak: str) -> bool:
    """True when TTS speak differs in ways that change pacing (not just spelling)."""
    v = normalize_speak(voice)
    s = normalize_speak(speak)
    if v == s:
        return False
    if re.search(r"[零一二三四五六七八九十百千万]", s) and re.search(r"\d", v):
        return True
    if "百分之" in s and "%" in v:
        return True
    if re.search(r"杰森", s) and re.search(r"json", v, re.I):
        return True
    # cosmetic: SkillSpector / Skill Spector, LTX-2 / LTX二
    v_compact = re.sub(r"[\s\-_""''「」]", "", v.lower())
    s_compact = re.sub(r"[\s\-_""''「」]", "", s.lower())
    if v_compact == s_compact:
        return False
    return abs(speak_timing_weight(s) - speak_timing_weight(v)) > 2.5


def significant_onsets(events: list[tuple[str, float]], seg_dur: float) -> list[float]:
    """Speech resume times after meaningful pauses."""
    raw: list[float] = []
    for i in range(len(events) - 1):
        if events[i][0] != "end" or events[i + 1][0] != "start":
            continue
        t = events[i][1]
        pause = events[i + 1][1] - t
        if t < 0.04 or pause < 0.12:
            continue
        raw.append(round(t, 3))
    if not raw:
        return []
    merged = [raw[0]]
    for t in raw[1:]:
        if t - merged[-1] < 0.28:
            merged[-1] = t
        else:
            merged.append(t)
    return merged


def pick_part_starts(
    onsets: list[float],
    n_parts: int,
    lead: float,
    weights: list[float] | None = None,
) -> list[float]:
    if n_parts <= 1:
        return [round(lead, 3)]
    if not onsets:
        return [round(lead, 3)] * n_parts
    src = onsets
    starts: list[float] = []
    if weights and len(weights) == n_parts and len(src) >= 2:
        total = sum(weights)
        cum = 0.0
        prev_idx = 0
        for i in range(n_parts):
            if i == 0:
                starts.append(max(lead, src[0]))
            elif i == n_parts - 1 and len(src) >= 3:
                idx = max(prev_idx + 1, len(src) - 2)
                starts.append(src[min(idx, len(src) - 1)])
            else:
                cum += weights[i - 1]
                frac = min(0.98, cum / max(1.0, total))
                idx = max(prev_idx + 1, round(frac * (len(src) - 1)))
                idx = min(idx, len(src) - 2)
                prev_idx = idx
                starts.append(src[idx])
        return [round(s, 3) for s in starts]
    for i in range(n_parts):
        if i == n_parts - 1 and len(src) >= 3:
            idx = len(src) - 2
        else:
            idx = round(i * (len(src) - 1) / max(1, n_parts - 1))
        starts.append(src[min(idx, len(src) - 1)])
    starts[0] = max(lead, starts[0])
    return [round(s, 3) for s in starts]


def snap_last_clause(aligned: list[dict], events: list[tuple[str, float]], seg_dur: float) -> list[dict]:
    """Pull final subtitle earlier to match first onset of last spoken clause."""
    if len(aligned) < 2 or not events:
        return aligned
    onset = final_clause_onset(events, seg_dur)
    if onset is None:
        return aligned
    start = round(onset - 0.02, 3)
    if start >= aligned[-1]["start"] - 0.04:
        return aligned
    if start <= aligned[-2]["start"] + 0.35:
        return aligned
    aligned[-2]["end"] = start
    aligned[-1]["start"] = start
    aligned[-1]["end"] = round(seg_dur, 3)
    return aligned


def snap_aligned_to_onsets(
    aligned: list[dict],
    events: list[tuple[str, float]],
    seg_dur: float,
    lead: float,
    strength: float,
    snap_from: int = 1,
    snap_to: int = -1,
    allow_earlier: bool = True,
    weights: list[float] | None = None,
    mode: str = "blend",
) -> list[dict]:
    """Blend or snap subtitle boundaries toward silence-detected speech onsets."""
    if len(aligned) < 2 or strength <= 0:
        return aligned
    onsets = significant_onsets(events, seg_dur)
    if len(onsets) < 2:
        return aligned
    last_idx = len(aligned) + snap_to if snap_to < 0 else snap_to
    last_idx = min(last_idx, len(aligned) - 1)
    snap_from = max(1, snap_from)

    if mode == "sequential":
        onset_cursor = 0
        while onset_cursor < len(onsets) and onsets[onset_cursor] < aligned[snap_from - 1]["end"] + 0.06:
            onset_cursor += 1
        for i in range(snap_from, last_idx + 1):
            cur = aligned[i]["start"]
            if onset_cursor >= len(onsets):
                break
            tgt = onsets[onset_cursor]
            onset_cursor += 1
            if abs(tgt - cur) < 0.1:
                continue
            new_start = round(cur * (1 - strength) + tgt * strength, 3)
            if not allow_earlier:
                new_start = max(cur, new_start)
            else:
                new_start = min(cur, max(aligned[i - 1]["start"] + 0.22, new_start))
            new_start = max(aligned[i - 1]["start"] + 0.22, min(new_start, seg_dur - 0.25))
            aligned[i - 1]["end"] = new_start
            aligned[i]["start"] = new_start
        aligned[-1]["end"] = round(seg_dur, 3)
        return aligned

    targets = pick_part_starts(onsets, len(aligned), lead, weights)
    for i in range(snap_from, last_idx + 1):
        cur = aligned[i]["start"]
        tgt = targets[i]
        if abs(tgt - cur) < 0.12:
            continue
        new_start = round(cur * (1 - strength) + tgt * strength, 3)
        if not allow_earlier:
            new_start = max(cur, new_start)
        else:
            new_start = min(cur, max(aligned[i - 1]["start"] + 0.22, new_start))
        new_start = max(aligned[i - 1]["start"] + 0.22, min(new_start, seg_dur - 0.25))
        aligned[i - 1]["end"] = new_start
        aligned[i]["start"] = new_start
    aligned[-1]["end"] = round(seg_dur, 3)
    return aligned


def snap_range_for_row(row: dict, n_parts: int, sig_diff: bool) -> tuple[int, int, str]:
    """Return (snap_from, snap_to, mode)."""
    if row.get("alignSnapFrom") is not None:
        mode = row.get("alignSnapMode", "blend")
        return int(row["alignSnapFrom"]), int(row.get("alignSnapTo", n_parts - 1)), mode
    if row.get("subtitleSpeakParts") and n_parts >= 6:
        return 1, n_parts - 1, "sequential"
    if row.get("subtitleSpeakParts"):
        return 1, n_parts - 1, "sequential"
    if not sig_diff and n_parts >= 6:
        return 2, n_parts - 1, "blend"
    if not sig_diff and n_parts >= 5:
        return 1, n_parts - 1, "blend"
    if sig_diff and n_parts >= 4:
        return 1, n_parts - 1, "blend"
    return 1, n_parts - 1, "blend"


PART_LAG = 0.1
PART_LAG_LONG = 0.12  # speak != voice with real pacing change (numbers / 百分之 / 杰森)


def allocate_parts(
    seg_dur: float,
    parts: list[str],
    weights: list[float],
    *,
    lead: float,
    active_end: float,
    extra_lag: float = 0.0,
) -> list[dict]:
    total_w = sum(weights)
    window = max(0.4, active_end - lead)
    lag = PART_LAG + extra_lag
    lag_budget = sum(lag * (1 + 0.06 * i) for i in range(max(0, len(parts) - 1)))
    usable = max(0.35 * window, window - min(window * 0.32, lag_budget))
    raw_durs = [usable * w / total_w for w in weights]

    t = lead
    aligned: list[dict] = []
    for i, part in enumerate(parts):
        if i > 0:
            t += lag * (1 + 0.06 * (i - 1))
        start = round(t, 3)
        if i == len(parts) - 1:
            end = round(seg_dur, 3)
        else:
            end = round(min(active_end, start + raw_durs[i]), 3)
            t = end
        aligned.append({"index": i, "text": part, "start": start, "end": end})
    return aligned


def tail_phrase_onset(events: list[tuple[str, float]], seg_dur: float) -> float | None:
    """Speech resume immediately before the final trailing silence."""
    threshold = seg_dur - 1.25
    for i in range(len(events) - 2, -1, -1):
        kind, t = events[i]
        if kind != "end":
            continue
        nk, nt = events[i + 1]
        if nk == "start" and nt > threshold:
            return t
    return None


def final_clause_onset(events: list[tuple[str, float]], seg_dur: float) -> float | None:
    """Earliest speech resume in the final sentence cluster."""
    threshold = seg_dur - 2.0
    candidates: list[float] = []
    for i in range(len(events) - 2, -1, -1):
        kind, t = events[i]
        if kind != "end":
            continue
        nk, nt = events[i + 1]
        if nk == "start" and nt > threshold:
            candidates.append(t)
    return min(candidates) if candidates else None


def nudge_short_tail(
    events: list[tuple[str, float]],
    seg_dur: float,
    aligned: list[dict],
    parts: list[str],
) -> list[dict]:
    if len(aligned) < 2 or not events:
        return aligned
    tail_units = visual_units(parts[-1])
    if tail_units > 14:
        return aligned
    onset = tail_phrase_onset(events, seg_dur)
    if onset is None:
        return aligned
    # Only nudge short tail phrases that appear clearly before speech
    gap = onset - aligned[-1]["start"]
    if gap < 0.12 or gap > 0.42:
        return aligned
    start = round(onset - 0.03, 3)
    if start <= aligned[-2]["start"] + 0.2:
        return aligned
    aligned[-2]["end"] = start
    aligned[-1]["start"] = start
    aligned[-1]["end"] = round(seg_dur, 3)
    return aligned


def parts_for_row(row: dict) -> list[str]:
    if row.get("subtitleParts"):
        return [strip_sub_punct(str(p)) for p in row["subtitleParts"]]
    voice = row.get("voice") or row.get("text") or ""
    return [strip_sub_punct(voice)]


def speak_parts_for_row(row: dict, parts: list[str]) -> list[str]:
    raw = row.get("subtitleSpeakParts")
    if raw and len(raw) == len(parts):
        return [strip_sub_punct(str(p)) for p in raw]
    return parts


def speak_part_boundaries(speak: str, speak_parts: list[str]) -> list[int]:
    pos = 0
    sn = normalize_speak(speak)
    ends: list[int] = []
    for part in speak_parts:
        sp = normalize_speak(part)
        chunk = sn[pos:]
        if chunk.startswith(sp):
            pos += len(sp)
        else:
            idx = chunk.find(sp)
            pos += idx + len(sp) if idx >= 0 else max(1, len(sp))
        ends.append(min(len(sn), pos))
    return ends


def allocate_by_speak_track(
    seg_dur: float,
    speak: str,
    speak_parts: list[str],
    parts: list[str],
    lead: float,
    active_end: float,
    extra_lag: float = 0.0,
) -> list[dict]:
    bounds = speak_part_boundaries(speak, speak_parts)
    sn_len = max(1, len(normalize_speak(speak)))
    lag = PART_LAG + extra_lag
    t = lead
    aligned: list[dict] = []
    for i, part in enumerate(parts):
        if i > 0:
            t += lag * (1 + 0.05 * (i - 1))
        frac = bounds[i] / sn_len
        end = seg_dur if i == len(parts) - 1 else min(active_end, lead + frac * (active_end - lead))
        start = round(t, 3)
        end = round(max(start + 0.28, end), 3)
        aligned.append({"index": i, "text": part, "start": start, "end": end})
        t = end
    aligned[-1]["end"] = round(seg_dur, 3)
    return aligned


def ensure_continuous_segments(aligned: list[dict], seg_dur: float) -> list[dict]:
    """Close snap gaps so subtitle N stays visible until subtitle N+1 starts."""
    if len(aligned) < 2:
        if aligned:
            aligned[-1]["end"] = round(seg_dur, 3)
        return aligned
    for i in range(len(aligned) - 1):
        nxt = aligned[i + 1]["start"]
        aligned[i]["end"] = round(max(aligned[i]["start"] + 0.22, nxt), 3)
    aligned[-1]["end"] = round(seg_dur, 3)
    return aligned


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

        speak = normalize_speak(row.get("speak") or voice)
        voice_norm = normalize_speak(voice)
        sig_diff = speak_diff_significant(voice_norm, speak)
        extra_lag = PART_LAG_LONG if sig_diff and len(parts) > 1 else 0.0
        snap_strength = 0.0
        if row.get("subtitleSpeakParts"):
            snap_strength = 0.82
        elif sig_diff and len(parts) >= 4:
            snap_strength = 0.72
        elif not sig_diff and speak != voice_norm and len(parts) >= 5:
            # cosmetic speak diff (Skill Spector, LTX二) — onsets only, no extra lag
            snap_strength = 0.68

        events = detect_silence_events(wav) if wav.exists() else []
        lead, active_end = speech_window(seg_dur, events)
        speak_parts = speak_parts_for_row(row, parts)
        if row.get("subtitleSpeakParts") and len(speak_parts) == len(parts):
            aligned = allocate_by_speak_track(
                seg_dur, speak, speak_parts, parts, lead, active_end, extra_lag
            )
        else:
            aligned = allocate_parts(
                seg_dur,
                parts,
                weights,
                lead=lead,
                active_end=active_end,
                extra_lag=extra_lag,
            )
        if snap_strength > 0 and events:
            snap_from, snap_to, snap_mode = snap_range_for_row(row, len(parts), sig_diff)
            if snap_mode == "tail":
                aligned = snap_last_clause(aligned, events, seg_dur)
            else:
                allow_earlier = snap_mode != "sequential" or not sig_diff
                if row.get("subtitleSpeakParts"):
                    allow_earlier = False
                aligned = snap_aligned_to_onsets(
                    aligned,
                    events,
                    seg_dur,
                    lead,
                    snap_strength,
                    snap_from,
                    snap_to,
                    allow_earlier,
                    weights,
                    snap_mode,
                )
        if sig_diff and extra_lag > 0:
            aligned = nudge_short_tail(events, seg_dur, aligned, parts)
        aligned = ensure_continuous_segments(aligned, seg_dur)
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
