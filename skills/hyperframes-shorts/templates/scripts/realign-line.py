#!/usr/bin/env python3
"""Re-fetch Edge WordBoundary alignments for one schedule line (no voiceover regen).

Use after changing subtitleParts count/text without re-recording TTS.
Then run: node scripts/apply-audio-schedule.mjs

Usage:
  python scripts/realign-line.py s6
  python scripts/realign-line.py s6 s7   # multiple ids
"""
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
g: dict = {
    "__name__": "realign_line",
    "__file__": str(ROOT / "scripts" / "generate-tts.py"),
}
exec((ROOT / "scripts/generate-tts.py").read_text(encoding="utf-8"), g)


async def realign(line_id: str) -> None:
    lines = json.loads((ROOT / "audio/lines.json").read_text(encoding="utf-8"))
    align_data = json.loads((ROOT / "audio/alignments.json").read_text(encoding="utf-8"))
    sched = json.loads((ROOT / "audio/schedule.json").read_text(encoding="utf-8"))
    item = next(x for x in lines if x["id"] == line_id)
    row = next(x for x in sched["schedule"] if x["id"] == line_id)
    voice = g["voice_text"](item)
    speak = g["tts_payload"](item)
    parts = row["subtitleParts"]
    sched_parts = [strip for strip in (item.get("subtitleParts") or [])]
    if sched_parts and len(sched_parts) != len(parts):
        print(
            f"WARN {line_id}: schedule subtitleParts ({len(parts)}) "
            f"!= lines.json ({len(sched_parts)}); using schedule"
        )

    mp3 = g["OUT_DIR"] / f"{line_id}_realign.mp3"
    bounds: list[dict] = []
    communicate = g["edge_tts"].Communicate(
        speak, g["VOICE"], rate=g["RATE"], boundary="WordBoundary"
    )
    with open(mp3, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                start = chunk["offset"] / 10_000_000
                end = start + chunk["duration"] / 10_000_000
                bounds.append(
                    {
                        "start": round(start, 3),
                        "end": round(end, 3),
                        "text": chunk["text"],
                    }
                )
    mp3.unlink(missing_ok=True)

    dur = float(row["duration"])
    parts_aligned = g["align_parts_from_boundaries"](voice, speak, parts, bounds, dur)
    if len(parts_aligned) != len(parts):
        print(
            f"ERROR {line_id}: aligned {len(parts_aligned)} parts != "
            f"subtitleParts {len(parts)}",
            file=sys.stderr,
        )
        sys.exit(1)

    align_data["lines"][line_id] = {
        "id": line_id,
        "duration": dur,
        "boundaryCount": len(bounds),
        "mode": "edge-word-boundary" if bounds else "proportional",
        "parts": parts_aligned,
    }
    (ROOT / "audio/alignments.json").write_text(
        json.dumps(align_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Updated {line_id}: {len(parts_aligned)} parts, {len(bounds)} boundaries")
    for p in parts_aligned:
        print(f"  {p['start']:6.3f}-{p['end']:6.3f}  {p['text']}")


async def main() -> None:
    ids = sys.argv[1:] if len(sys.argv) > 1 else ["s6"]
    for line_id in ids:
        await realign(line_id)


if __name__ == "__main__":
    asyncio.run(main())
