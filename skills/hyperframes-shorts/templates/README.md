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
| `templates/visual-style-guide.md` | 风格轮换、首镜布局、片尾变体 A/B/C |

**写 HTML 前必读 Skill：**

- `design-taste-frontend`（taste-skill）
- `css-animations` · `design-motion-principles` · `web-typography`

`index.html` 中须预留：

```html
<!-- narration audio -->
<audio id="voiceover" class="clip" data-start="0" data-duration="60" data-track-index="5" data-volume="1" src="audio/voiceover.wav"></audio>
<!-- /narration audio -->
<audio id="bgm" class="clip" data-start="0" data-duration="60" data-track-index="6" data-volume="0.3" src="assets/bgm.mp3" loop></audio>
```

流水线（**全部由 Agent 自动执行**；用户交付后只 `npm run dev`）：

`taste pre-flight` → `design.md` + Motion Plan → **Pre-flight** → **`lines.json`（voice 整句 + subtitle 显示）** → 写 `index.html`（**hyperframes-zh-checklist** + scene-density + L0–L4）→ `generate-tts.py` → **`run-align.py`**（Whisper 全失败 → WSL；草稿 `ALLOW_FALLBACK_ALIGN=1`）→ `apply-audio-schedule.mjs` → `apply-brand.mjs`（有片尾）→ **`verify-delivery-checklist.py`** → **Post-audit** → **`verify-index-encoding.py`** → `npm run check` → 更新 `style-history.json`（若有）

**Studio 注意：** `npm run dev` 开着时 Studio 可能回写 `index.html` 并把中文变成 `??`。Agent 写 HTML 前先停 dev；用户勿在 Studio 画布改中文，改 `audio/lines.json` 后重跑 TTS 流水线。
