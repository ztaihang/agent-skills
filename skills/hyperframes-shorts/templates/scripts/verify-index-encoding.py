#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fail fast if index.html shows Studio UTF-8 / HTML corruption."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "index.html"
LINES = ROOT / "audio/lines.json"

CORRUPT_PATTERNS = [
    (r"/div&gt;", "broken closing tag (/div&gt;)"),
    (r"<span[^>]*>\?{2,}</span>\s*</span>", "nested span corruption"),
    (r"</div>\s*</div>\s*</div>\s*</div>\s*</body>", "extra closing divs before </body>"),
]


def main() -> int:
    if not HTML.exists():
        print(f"[verify-index-encoding] missing {HTML}")
        return 1

    text = HTML.read_text(encoding="utf-8", errors="replace")
    errors: list[str] = []

    for pattern, label in CORRUPT_PATTERNS:
        if re.search(pattern, text):
            errors.append(label)

    if LINES.exists():
        lines = json.loads(LINES.read_text(encoding="utf-8"))
        samples = []
        for item in lines[:3]:
            t = item.get("text", "")
            sample = re.sub(r"[，。！？：；、\s]+", "", t)[:6]
            if sample and re.search(r"[\u4e00-\u9fff]", sample):
                samples.append(sample)
        for sample in samples:
            if sample not in text:
                errors.append(f"lines.json sample not in HTML: {sample!r} (likely Studio ?? corruption)")

    if "data-hf-id" in text and samples and any(s not in text for s in samples):
        errors.append("Studio data-hf-id present while Chinese missing — re-write index.html, do not edit in Studio")

    if errors:
        print("[verify-index-encoding] FAILED:")
        for e in errors:
            print(f"  - {e}")
        print("Fix: stop npm run dev, rebuild index.html (UTF-8), never edit Chinese in Studio canvas.")
        return 1

    print("[verify-index-encoding] OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
