#!/usr/bin/env python3
"""Whisper alignment with escalation ladder; fallback only as draft preview.

Preferred entry point after generate-tts.py. Tries faster-whisper with multiple
model/compute combinations (subprocess) so Windows segfaults do not kill the parent.

Windows notes (see requirements-align.txt):
  - Pin ctranslate2==4.4.0 (4.8.x may segfault on Py3.12 when loading WhisperModel)
  - Prefer tiny/int8 first — small/int8 can OOM (mkl_malloc) on long projects
"""
from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ALIGN_SCRIPT = Path(__file__).resolve().parent / "align-subtitles.py"
FALLBACK_SCRIPT = Path(__file__).resolve().parent / "fallback-alignments.py"
SCHEDULE_PATH = ROOT / "audio/schedule.json"
OUT_PATH = ROOT / "audio/alignments.json"

# Linux/macOS: quality first. Windows: tiny/int8 first (RAM + ct2 stability).
if platform.system() == "Windows":
    CANDIDATES: list[tuple[str, str]] = [
        ("tiny", "int8"),
        ("tiny", "float32"),
        ("small", "int8"),
        ("small", "float32"),
        ("base", "int8"),
    ]
else:
    CANDIDATES = [
        ("small", "int8"),
        ("small", "float32"),
        ("base", "int8"),
        ("tiny", "int8"),
    ]

WINDOWS_CRASH_CODES = {0xC0000005, -1073741819, 3221225477}
CT2_PIN = "4.4.0"


def check_ctranslate2() -> None:
    try:
        import ctranslate2
    except ImportError:
        print("ERROR: pip install -r requirements-align.txt", file=sys.stderr)
        raise SystemExit(1)
    ver = getattr(ctranslate2, "__version__", "")
    if ver and ver != CT2_PIN and platform.system() == "Windows":
        print(
            f"WARN: ctranslate2 {ver} on Windows — recommend ctranslate2=={CT2_PIN} "
            f"(4.8.x may segfault). Run: pip install -r requirements-align.txt",
            file=sys.stderr,
        )


def run_align_subprocess(model: str, compute_type: str, smoke_only: bool) -> int:
    cmd = [
        sys.executable,
        str(ALIGN_SCRIPT),
        "--model",
        model,
        "--compute-type",
        compute_type,
    ]
    if smoke_only:
        cmd.append("--smoke-only")
    proc = subprocess.run(cmd, cwd=ROOT)
    return int(proc.returncode or 0)


def alignment_ok(expected_rows: int) -> bool:
    if not OUT_PATH.is_file():
        return False
    try:
        data = json.loads(OUT_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    if data.get("engine") != "faster-whisper":
        return False
    lines = data.get("lines") or {}
    return len(lines) >= expected_rows


def main() -> int:
    check_ctranslate2()
    if not SCHEDULE_PATH.is_file():
        print("ERROR: run generate-tts.py first (missing schedule.json)", file=sys.stderr)
        return 1

    schedule = json.loads(SCHEDULE_PATH.read_text(encoding="utf-8"))["schedule"]
    n_rows = len(schedule)

    for model, compute in CANDIDATES:
        print(f"--- Whisper smoke: model={model} compute={compute} ---")
        code = run_align_subprocess(model, compute, smoke_only=True)
        if code in WINDOWS_CRASH_CODES or code != 0:
            print(f"Smoke failed (exit {code}), trying next…", file=sys.stderr)
            continue

        print(f"--- Whisper full align: model={model} compute={compute} ---")
        code = run_align_subprocess(model, compute, smoke_only=False)
        if code in WINDOWS_CRASH_CODES or code != 0:
            print(f"Full align failed (exit {code}), trying next…", file=sys.stderr)
            continue

        if alignment_ok(n_rows):
            print(f"OK: Whisper alignment complete ({model}, {compute}) — {n_rows} lines")
            return 0
        print(
            f"align-subtitles exited 0 but alignments incomplete "
            f"({OUT_PATH.name} engine or line count)",
            file=sys.stderr,
        )

    print(
        "ERROR: faster-whisper unavailable after all candidates. "
        "Ensure pip install -r requirements-align.txt (ctranslate2==4.4.0). "
        "Or try WSL2: python scripts/run-align.py",
        file=sys.stderr,
    )

    if os.environ.get("ALLOW_FALLBACK_ALIGN") == "1":
        print("ALLOW_FALLBACK_ALIGN=1 → running fallback-alignments.py (DRAFT only)", file=sys.stderr)
        fb = subprocess.run([sys.executable, str(FALLBACK_SCRIPT)], cwd=ROOT)
        if fb.returncode != 0:
            return int(fb.returncode or 1)
        print(
            "WARN: alignments.json uses fallback weights — subtitle timing is ESTIMATED. "
            "Not delivery-grade; run Whisper before export.",
            file=sys.stderr,
        )
        return 2

    print(
        "Set ALLOW_FALLBACK_ALIGN=1 only for draft preview (not formal delivery).",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
