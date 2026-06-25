#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Agent-only: post-build delivery checklist for Chinese HyperFrames shorts.

Run after build-index.py + run-align.py + apply-audio-schedule.mjs, before npm run check.
See templates/hyperframes-zh-checklist.md for full rules.

Exit 0 = no ERROR (WARN may remain). Exit 1 = fix required before delivery.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "index.html"
LINES = ROOT / "audio/lines.json"
FONTS = ROOT / "fonts"
META = ROOT / "meta.json"

# HyperFrames compiler cannot map these — dev may hang
FORBIDDEN_FONT_NAMES = [
    "PingFang SC",
    "PingFang",
    "Microsoft YaHei",
    "微软雅黑",
    "SimHei",
    "黑体",
    "Helvetica Neue",
    "Helvetica",
    "Arial",
]

FORBIDDEN_FONT_URLS = [
    "fonts.googleapis.com",
    "fonts.gstatic.com",
    "use.typekit.net",
]

WARNINGS: list[str] = []
ERRORS: list[str] = []


def err(msg: str) -> None:
    ERRORS.append(msg)


def warn(msg: str) -> None:
    WARNINGS.append(msg)


def read_html() -> str:
    if not HTML.exists():
        err(f"missing {HTML}")
        return ""
    return HTML.read_text(encoding="utf-8", errors="replace")


def check_external_fonts(text: str) -> None:
    for url in FORBIDDEN_FONT_URLS:
        if url in text:
            err(f"external font URL forbidden: {url} (use local fonts/ + @font-face)")


def check_forbidden_font_families(text: str) -> None:
    for name in FORBIDDEN_FONT_NAMES:
        if name in text:
            err(f"forbidden font-family fallback: {name!r}")


def check_chinese_custom_fonts(text: str) -> None:
    uses_noto = "Noto Sans SC" in text or "Noto Serif SC" in text
    if not uses_noto:
        return
    if "@font-face" not in text:
        err("uses Noto Sans/Serif SC but no @font-face in index.html")
        return
    if 'url("fonts/' not in text and "url('fonts/" not in text and "url(./fonts/" not in text:
        err("@font-face present but no src url('fonts/...woff2') — add local woff2 under fonts/")
    if FONTS.is_dir():
        woff2 = list(FONTS.glob("*.woff2"))
        if not woff2:
            err("fonts/ directory exists but has no .woff2 files")
    else:
        err("fonts/ directory missing (required for Noto Sans SC / Noto Serif SC)")


def check_subtitles(text: str) -> None:
    if "sub-bar" not in text and 'class="sl' not in text:
        warn("no .sub-bar / .sl subtitle elements found")
        return
    if "white-space:nowrap" not in text.replace(" ", "") and "white-space: nowrap" not in text:
        err("subtitle CSS missing white-space: nowrap")
    if "sub-text" in text or "sub-bar" in text:
        bottom = None
        for block in re.finditer(r"\.sub-bar[^{]*\{([^}]+)\}", text, re.DOTALL):
            m = re.search(r"bottom:\s*(\d+)px", block.group(1))
            if m:
                bottom = int(m.group(1))
                break
        if bottom is None:
            err(".sub-bar missing bottom: Npx (subtitle must sit at screen bottom, 28–48px)")
        elif bottom < 20 or bottom > 56:
            warn(f".sub-bar bottom:{bottom}px outside recommended 28–48px")
    if re.search(r"\.sub-bar[^{]*\{[^}]*background\s*:\s*(?!transparent)[^;}]+", text, re.DOTALL):
        err(".sub-bar must not have background (subtitle = text + shadow only; transparent OK)")


def check_subtitle_safe_zone(text: str) -> None:
    bottoms = [int(x) for x in re.findall(r"padding-bottom:\s*(\d+)px", text)]
    for m in re.finditer(r"padding:\s*\d+px\s+\d+px\s+(\d+)px", text):
        bottoms.append(int(m.group(1)))
    min_safe = 160
    if bottoms:
        if max(bottoms) < min_safe:
            warn(
                f"content padding-bottom max={max(bottoms)}px < {min_safe}px — subtitle may overlap content"
            )
    else:
        warn("could not detect padding-bottom — verify subtitle safe zone (≥180px) manually")


def check_rounded_surfaces(text: str) -> None:
    if "border-radius" not in text:
        warn("no border-radius in CSS — UI may look boxy; see hyperframes-zh-checklist §五")
        return
    m = re.search(r"\.trend-item\s*\{([^}]+)\}", text, re.DOTALL)
    if m and "border-radius" not in m.group(1):
        warn(".trend-item has no border-radius")


def check_subtitle_structure(text: str) -> None:
    if re.search(r'class="sub-bar sl clip"', text):
        err(
            'subtitle must be <div class="sub-bar clip"><span class="sl">…</span></div> '
            "(not sub-bar+sl+clip on one element — causes off-center clips in Studio)"
        )
    if 'class="sub-bar clip"' in text and not re.search(
        r'class="sub-bar clip"[^>]*>\s*<span class="sl">', text
    ):
        warn("sub-bar.clip should wrap inner <span class=\"sl\"> for horizontal centering")


def check_overline_language(text: str) -> None:
    for m in re.finditer(r'<div class="overline[^"]*"[^>]*>([^<]+)</div>', text):
        label = m.group(1).strip()
        if re.search(r"[\u4e00-\u9fff]", label):
            continue
        if re.fullmatch(r"[A-Za-z0-9 /\-·]+", label):
            err(
                f"overline {label!r} is English-only — use Chinese label related to narration "
                "(English only for product/Skill names in .skill-name; see scene-density-guide.md)"
            )


def check_background(text: str) -> None:
    root_block = re.search(r"#root\s*\{([^}]+)\}", text, re.DOTALL)
    if not root_block:
        warn("#root styles not found")
        return
    block = root_block.group(1)
    if re.search(r"background\s*:\s*#0a0a0a\s*;", block) or re.search(
        r"background-color\s*:\s*#0a0a0a\s*;", block
    ):
        if "gradient" not in block:
            err("#root is flat #0a0a0a with no gradient layers (dead black background)")
    if "gradient" not in text and "bg-glow" not in text and "bg-aurora" not in text:
        warn("no gradient / bg-glow / bg-aurora detected — background may look flat")


def check_ambient_layers(text: str) -> None:
    """L0 = static #root decor. Per-scene CSS infinite ambient is forbidden (CPU)."""
    scenes = len(re.findall(r'id="sc\d+"', text))
    if not scenes:
        scenes = len(re.findall(r'class="clip scene"', text))
    ambients = len(re.findall(r'class="ambient', text))
    if not ambients:
        ambients = len(re.findall(r'id="amb-\d+"', text))
    infinite = len(re.findall(r"infinite", text))

    root_block = re.search(r"#root\s*\{([^}]+)\}", text, re.DOTALL)
    root_has_decor = bool(root_block and (
        "gradient" in root_block.group(1) or "background-image" in root_block.group(1)
    ))
    if not root_has_decor and "gradient" not in text:
        err(
            "L0: #root needs static decor (gradient / grid / vignette) — not flat black"
        )

    if scenes >= 3 and ambients >= scenes:
        err(
            f"per-scene .ambient on all {scenes} scenes — forbidden (hidden CSS loops). "
            "Use #root static gradient/grid only; see anti-slop-motion-scheme L0"
        )

    if "feTurbulence" in text and infinite:
        err(
            "feTurbulence + CSS infinite (animated grain) — use static decor or static PNG grain"
        )

    if infinite > 4:
        warn(
            f"{infinite} CSS infinite keywords — keep ≤1 optional loop on #root, not per-scene"
        )


def check_build_source(text: str) -> None:
    if "data-hf-id" in text:
        warn("Studio data-hf-id in HTML — prefer regenerating from scripts, not canvas edits")


def _line_scene(item: dict) -> int:
    if "scene" in item:
        return int(item["scene"])
    m = re.match(r"^s(\d+)", item.get("id", ""))
    return int(m.group(1)) if m else 1


def check_tts_granularity() -> None:
    """WARN when same breath was split into multiple wav ids for subtitle width."""
    if not LINES.exists():
        return
    try:
        lines = json.loads(LINES.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        warn("could not read audio/lines.json for TTS granularity check")
        return
    if not isinstance(lines, list):
        return
    for i in range(1, len(lines)):
        prev, curr = lines[i - 1], lines[i]
        if _line_scene(prev) != _line_scene(curr):
            continue
        prev_id = prev.get("id", "")
        curr_id = curr.get("id", "")
        m_prev = re.match(r"^(.+?)([a-z]+)$", prev_id)
        m_curr = re.match(r"^(.+?)([a-z]+)$", curr_id)
        if m_prev and m_curr and m_prev.group(1) == m_curr.group(1):
            warn(
                f"lines.json {prev_id}+{curr_id}: 疑似为字幕宽度拆 TTS — "
                f"应合并 voice 为一条 wav，字幕用 subtitle/subtitleParts"
            )
            continue
        prev_voice = (prev.get("voice") or prev.get("text") or "").strip()
        curr_voice = (curr.get("voice") or curr.get("text") or "").strip()
        prev_speak = (prev.get("speak") or prev_voice).strip()
        curr_speak = (curr.get("speak") or curr_voice).strip()
        if prev_speak and prev_speak == curr_speak:
            warn(
                f"lines.json {prev_id}+{curr_id}: speak 相同却两条 wav — 检查是否误拆口播"
            )


def check_subtitle_voice_substrings() -> None:
    """ERROR when subtitleParts are rewritten summaries (breaks Whisper align)."""
    if not LINES.exists():
        return
    try:
        lines = json.loads(LINES.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return
    if not isinstance(lines, list):
        return

    def norm(s: str) -> str:
        return re.sub(
            r'[\s，。！？：；、\u201c\u201d\u2018\u2019「」『』"\']',
            "",
            s,
        ).lower()

    def strip_tail(s: str) -> str:
        return re.sub(r"[，。！？：；、]+$", "", s.strip())

    for item in lines:
        line_id = item.get("id", "?")
        voice = (item.get("voice") or item.get("text") or "").strip()
        if not voice:
            continue
        parts = item.get("subtitleParts") or item.get("subtitle") or []
        if isinstance(parts, str):
            parts = [parts]
        if not parts:
            continue
        vn = norm(voice)
        pos = 0
        for j, part in enumerate(parts):
            sub_id = line_id if j == 0 else f"{line_id}_sub{j + 1}"
            pn = norm(strip_tail(str(part)))
            if not pn:
                continue
            idx = vn.find(pn, pos)
            if idx < 0:
                err(
                    f"lines.json {sub_id}: 字幕不是 voice 连续子串 — "
                    f"禁止缩写/改写（见 subtitle-tts-guide.md §1.1）"
                )
                break
            pos = idx + len(pn)


def check_subtitle_orphan_parts() -> None:
    """Warn when auto-split leaves tiny orphan subtitle rows (e.g. 层级 alone)."""
    schedule_path = ROOT / "audio" / "schedule.json"
    if not schedule_path.is_file():
        return
    try:
        sched = json.loads(schedule_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return

    def strip_tail(s: str) -> str:
        return re.sub(r"[，。！？：；、]+$", "", s.strip())

    for row in sched.get("schedule") or []:
        parts = row.get("subtitleParts") or []
        if len(parts) <= 1:
            continue
        lid = row.get("id", "?")
        for j, part in enumerate(parts):
            if j == 0:
                continue
            core = strip_tail(str(part))
            han = len(re.findall(r"[\u4e00-\u9fff]", core))
            if han <= 2 and len(core) <= 4:
                warn(
                    f"{lid}: subtitleParts[{j}] 仅「{core}」— "
                    f"疑似自动拆断，请在 lines.json 手写语义断点"
                )


def check_alignments() -> None:
    schedule_path = ROOT / "audio" / "schedule.json"
    align_path = ROOT / "audio" / "alignments.json"
    if not schedule_path.is_file():
        return
    if not align_path.is_file():
        err("audio/alignments.json 缺失 — 须先运行 python scripts/generate-tts.py")
        return
    try:
        sched = json.loads(schedule_path.read_text(encoding="utf-8"))
        align = json.loads(align_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        err(f"alignments/schedule JSON 解析失败: {e}")
        return
    sh = sched.get("voiceoverHash")
    ah = align.get("voiceoverHash")
    if sh and ah and sh != ah:
        err(
            f"alignments.json 已过期 (hash {ah} != schedule {sh}) — 重跑 python scripts/generate-tts.py"
        )
    engine = align.get("engine")
    if engine == "edge-tts":
        pass
    elif engine == "fallback":
        if os.environ.get("ALLOW_FALLBACK_DELIVERY") == "1":
            warn(
                "alignments.json 使用 fallback 权重模式 — 精度低于 Whisper，交付前须听检多 part 字幕镜"
            )
        else:
            err(
                "alignments.json 使用 fallback 估算时间轴 — 不能作为正式交付。"
                "请运行 python scripts/run-align.py（或 WSL 内跑 Whisper）；"
                "仅草稿预览可设 ALLOW_FALLBACK_ALIGN=1 后重跑 run-align，"
                "正式放行可设 ALLOW_FALLBACK_DELIVERY=1"
            )
    lines = align.get("lines") or {}
    for row in sched.get("schedule") or []:
        lid = row.get("id")
        parts = row.get("subtitleParts") or []
        if len(parts) <= 1:
            continue
        if lid not in lines:
            warn(f"{lid}: alignments.json 无此行 — 字幕可能 fallback 估算")
            continue
        ar = lines[lid]
        if len(ar.get("parts") or []) != len(parts):
            warn(f"{lid}: alignments 条数与 subtitleParts 不一致")
        ratio = ar.get("matchRatio")
        if isinstance(ratio, (int, float)) and ratio < 0.55:
            warn(f"{lid}: matchRatio={ratio:.2f} 偏低 — 建议听检该镜字幕")


def main() -> int:
    text = read_html()
    if not text:
        _report()
        return 1

    check_external_fonts(text)
    check_forbidden_font_families(text)
    check_chinese_custom_fonts(text)
    check_subtitles(text)
    check_subtitle_structure(text)
    check_overline_language(text)
    check_subtitle_safe_zone(text)
    check_background(text)
    check_ambient_layers(text)
    check_rounded_surfaces(text)
    check_build_source(text)
    check_tts_granularity()
    check_subtitle_voice_substrings()
    check_subtitle_orphan_parts()
    check_alignments()

    return _report()


def _report() -> int:
    print("[verify-delivery-checklist]")
    if ERRORS:
        print(f"  ERROR ({len(ERRORS)}):")
        for e in ERRORS:
            print(f"    [X] {e}")
    if WARNINGS:
        print(f"  WARN ({len(WARNINGS)}):")
        for w in WARNINGS:
            print(f"    [!] {w}")
    if not ERRORS and not WARNINGS:
        print("  OK — 0 errors, 0 warnings")
    elif not ERRORS:
        print("  OK — 0 errors (review WARN against hyperframes-zh-checklist.md)")
    else:
        print("  FAILED — fix ERRORs, rebuild, re-run before delivery")
        print("  See: templates/hyperframes-zh-checklist.md")
    return 1 if ERRORS else 0


if __name__ == "__main__":
    sys.exit(main())
