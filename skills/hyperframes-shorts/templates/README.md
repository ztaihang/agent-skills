# 项目模板

新建 HyperFrames 短视频项目时，Agent **必须先复制**本目录到用户项目：

| 源 | 目标 |
|----|------|
| `templates/scripts/*` | `项目/scripts/` |
| `templates/audio/lines.json.example` | `项目/audio/lines.json`（按口播改写） |
| `templates/assets/brand.json.example` | `项目/assets/brand.json`（无片尾则 `outroMode: off`） |
| `templates/design.md.example` | `项目/design.md`（**必改**：YAML 来自所选 `visual-styles.md` 预设） |

**写 HTML 前必读（不复制到项目）：**

- `templates/visual-style-guide.md` — 风格轮换、首镜布局、片尾变体 A/B/C、禁止同质化

`index.html` 中须预留：

```html
<!-- narration audio -->
<audio id="voiceover" class="clip" data-start="0" data-duration="60" data-track-index="5" data-volume="1" src="audio/voiceover.wav"></audio>
<!-- /narration audio -->
<audio id="bgm" class="clip" data-start="0" data-duration="60" data-track-index="6" data-volume="0.3" src="assets/bgm.mp3" loop></audio>
```

流水线：`design.md` 定稿 → 写 `index.html`（UTF-8；场景仅用 `class="clip"`）→ `generate-tts.py` → `apply-audio-schedule.mjs` → `apply-brand.mjs`（有片尾时）→ `verify-index-encoding.py` → `npm run check`

**Studio 注意：** `npm run dev` 开着时 Studio 可能回写 `index.html` 并把中文变成 `??`。Agent 写 HTML 前先停 dev；用户勿在 Studio 画布改中文，改 `audio/lines.json` 后重跑 TTS 流水线。
