# 项目模板

新建 HyperFrames 短视频项目时，Agent **必须先复制**本目录到用户项目：

| 源 | 目标 |
|----|------|
| `templates/scripts/*` | `项目/scripts/` |
| `templates/requirements-align.txt` | `项目/requirements-align.txt`（可选；或 `pip install faster-whisper`） |
| `templates/audio/lines.json.example` | `项目/audio/lines.json`（按口播改写） |
| `templates/assets/brand.json.example` | `项目/assets/brand.json`（无片尾则 `outroMode: off`） |
| `templates/design.md.example` | `项目/design.md`（**必改**：YAML + **Motion Plan** + tasteDials） |
| `templates/style-history.json.example` | `项目/assets/style-history.json`（**可选**，频道轮换） |

**写 HTML 前必读（不复制到项目）：**

| 文件 | 内容 |
|------|------|
| `templates/anti-slop-motion-scheme.md` | **反 AI 味 + L0–L4 动效**（五道门禁） |
| `templates/scene-density-guide.md` | **镜内防太空**、副信息层次 |
| `templates/subtitle-tts-guide.md` | **口播/字幕分离 + speak**（写 `lines.json` 前） |
| `templates/hyperframes-zh-checklist.md` | **中文 HyperFrames 字体/字幕/背景/圆角 + 生成后自检** |
| `templates/delivery-pitfalls.md` | **交付避坑复盘**（背景/布局/字幕对齐/流水线；可转发给接手人） |
| `templates/visual-style-guide.md` | 风格轮换、首镜布局、片尾变体 A/B/C |

**写 HTML 前必读 Skill / 官方文档：**

- `design-taste-frontend` · `hyperframes-creative` · `hyperframes-animation` · `hyperframes-core`
- **P0** `hyperframes-creative/references/video-composition.md`
- **P0** `hyperframes-creative/references/data-in-motion.md`（分镜有数据镜时）
- **P1** `beat-direction.md`（>90s 或 ≥6 镜）· **P1** `design-picker.md`（用户未指定风格）
- `design-motion-principles` · `web-typography`

**HTML 写完后 Agent 内部（不交给用户）：**

- **P0** `design-adherence.md` · **P0** `snapshot --frames 9`（≥4 镜）
- **P2** `motion.json` · **P2** `media-use` SFX · **P2** `hyperframes add`

`index.html` 中须预留：

```html
<!-- narration audio -->
<audio id="voiceover" class="clip" data-start="0" data-duration="60" data-track-index="5" data-volume="1" src="audio/voiceover.wav"></audio>
<!-- /narration audio -->
<audio id="bgm" class="clip" data-start="0" data-duration="60" data-track-index="6" data-volume="0.3" src="assets/bgm.mp3" loop></audio>
```

流水线（**全部由 Agent 自动执行**；用户交付后只 `npm run dev`）：

`taste pre-flight` → `design.md` + Motion Plan（**P0/P1**）→ Pre-flight → `lines.json` → 写 `index.html` → **P0 design-adherence** → TTS 流水线 → `apply-audio-schedule` → `apply-brand`（若有）→ `verify-delivery-checklist` → Post-audit → **P0 snapshot**（≥4镜）→ **P2 motion.json/media-use**（若触发）→ `verify-index-encoding` → `npm run check` → 更新 `style-history.json`

**改 `subtitleParts` 条数后（不重录 TTS）：** `python scripts/realign-line.py <id>` → `apply-audio-schedule.mjs`。详见 **`delivery-pitfalls.md` §字幕与 TTS**。

**Studio 注意：** `npm run dev` 开着时 Studio 可能回写 `index.html` 并把中文变成 `??`。Agent 写 HTML 前先停 dev；用户勿在 Studio 画布改中文，改 `audio/lines.json` 后重跑 TTS 流水线。
