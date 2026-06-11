#!/usr/bin/env python3
"""Per-line Edge TTS → segments/*.wav, concat voiceover.wav, write schedule.json."""
import asyncio
import hashlib
import json
import re
import subprocess
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parent.parent
LINES_PATH = ROOT / "audio/lines.json"
OUT_DIR = ROOT / "audio/segments"
VOICEOVER = ROOT / "audio/voiceover.wav"

OUT_DIR.mkdir(parents=True, exist_ok=True)

VOICE = "zh-CN-YunyangNeural"
RATE = "+12%"  # 实测总时长 >150s 时改为 "+18%" 后重跑
GAP = 0


def text_hash(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()[:8]


def line_scene(item: dict) -> int:
    if "scene" in item:
        return int(item["scene"])
    m = re.match(r"^s(\d+)", item.get("id", ""))
    if m:
        return int(m.group(1))
    return 1


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


async def synth_line(line_id: str, text: str) -> Path:
    mp3 = OUT_DIR / f"{line_id}.mp3"
    wav = OUT_DIR / f"{line_id}.wav"
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE)
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
    lines = [f"file '{w.resolve().as_posix()}'" for w in wavs]
    list_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
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
    schedule = []
    wavs = []
    t = 0.0

    for item in lines:
        line_id = item["id"]
        text = item["text"]
        scene = line_scene(item)
        print(f"TTS {line_id} (sc{scene}): {text}")
        wav = await synth_line(line_id, text)
        wavs.append(wav)
        duration = probe_duration(wav)
        show_end = round(t + duration, 3)
        schedule.append(
            {
                "id": line_id,
                "scene": scene,
                "text": text,
                "textHash": text_hash(text),
                "src": f"audio/segments/{line_id}.wav",
                "start": round(t, 3),
                "duration": duration,
                "showEnd": show_end,
            }
        )
        t = show_end + GAP

    concat_voiceover(wavs, VOICEOVER)
    total_duration = round(schedule[-1]["showEnd"], 3)
    voiceover_hash = text_hash("".join(item["text"] for item in lines))

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
