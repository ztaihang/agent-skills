---
name: hyperframes-shorts
description: HyperFrames 中文短视频（口播解说）。必读 hyperframes-core/animation/creative；写 HTML 前 P0 video-composition + scene-density，有数据镜 P0 data-in-motion；写 HTML 后 P0 design-adherence；≥4镜 P0 snapshot；P1 atomic-rules/beat-direction/design-picker；P2 media-use SFX/motion.json/registry 条件触发。Edge TTS + design.md + L0–L4 + npm run check。用户仅 npm run dev。
---

# 使用说明

本 Skill 用于在**用户指定的项目路径**下构建 HyperFrames 短视频工程。修改视频内容请改项目目录内的文件；若要**贡献或修改 skill 源码**，见仓库 [CONTRIBUTING.md](https://github.com/ztaihang/agent-skills/blob/main/CONTRIBUTING.md)。

---

# HyperFrames 0.7 能力对齐（Agent 必读）

> 新版 HyperFrames 能力很多；**中文口播短视频不必全用**。下表说明本 Skill 与官方 0.7 的关系。  
> 图例：**✅ 必用** · **⭐ 推荐升级** · **⚪ 可选** · **🚫 不用**

## 领域 Skill 对照

| 官方能力 | 本 Skill | 说明 |
|---------|---------|------|
| `hyperframes-core` — HTML 合约、clip/track | ✅ 必用 | 写 `index.html` 前读 `determinism-rules.md` 要点 |
| `hyperframes-animation` — GSAP `mt` | ✅ 必用 | L1–L3 主路径 |
| `hyperframes-animation` — CSS keyframe L0 | ✅ 必用 | `adapters/css-animations.md` |
| `hyperframes-animation` — **转场 catalog** | ⭐ 推荐 | 见下方「L4 转场分级」；写 HTML 前读 `transitions/catalog.md` 对应条目 |
| `hyperframes-animation` — atomic rules / blueprints | ⭐ P1 | L2/L3 查 `rules-index.md`；复杂镜查 blueprints |
| `hyperframes-animation` — Lottie / Three.js / TypeGPU | 🚫 默认不用 | 口播解说 seek 成本高；用户明确要求 3D/shader 镜才启用 |
| `hyperframes-creative` — visual-styles / house-style | ✅ 必用 | 写 `design.md` |
| `hyperframes-cli` — lint / validate / inspect | ✅ 必用 | `npm run check` |
| `hyperframes-cli` — snapshot | ✅ P0 | **≥4 镜** 交付前 `npx hyperframes snapshot --frames 9` |
| `hyperframes-creative` — design-adherence | ✅ P0 | HTML 写完后对照 design.md |
| `hyperframes-creative` — video-composition | ✅ P0 | 写 HTML 前必读 |
| `hyperframes-creative` — data-in-motion | ✅ P0 | 有数据镜时必读 |
| `hyperframes-creative` — design-picker | ⭐ P1 | 用户未指定风格时 offer |
| `hyperframes-creative` — beat-direction | ⭐ P1 | 口播 >90s 或 ≥6 镜 |
| `hyperframes-animation` — atomic rules | ⭐ P1 | L2/L3 查 rules-index |
| `media-use` — SFX resolve | ⚪ P2 | HeyGen 已登录时替代 FFmpeg 滴声 |
| `hyperframes-registry` — add 组件 | ⚪ P2 | 数据图表镜可选 |
| `*.motion.json` sidecar | ⚪ P2 | ≥5 镜复杂动效 |
| `hyperframes-cli` — Lambda 云渲染 | ⚪ 可选 | 仅用户要求长片/4K 云导出 |
| `hyperframes-media` — 官方 TTS/BGM | 🚫 不用 | 见下方「TTS 路线对比」；中文坚持用 Edge TTS |
| 11 条官方 workflow | 🚫 不用 | 本 Skill 是 `/faceless-explainer` 的中文增强替代 |

## L4 转场分级（对接 0.7 catalog）

写 `design.md` Motion Plan 时，从 **`hyperframes-animation/transitions/`** 选型；实现须 **seek-safe + `mt` 时间轴**，禁止 ScrollTrigger。

|  tier | 转场 | catalog 参考 | 适用 |
|------|------|-------------|------|
| **A · 默认池**（每支至少用其中 3 种轮换） | push · blur · zoom/scale · focus pull / crossfade | `css-push.md` · `css-blur.md` · `css-scale.md` · `css-dissolve.md` | 全部口播镜；相邻镜不重复 |
| **B · 增强池**（全片选 1–2 处「亮点转场」） | radial iris · grid dissolve · horizontal blinds · light leak | `css-radial.md` · `css-grid.md` · `css-cover.md` · `css-light.md` | 话题切换、章节转折、数据镜→总结镜 |
| **C · 慎用池**（默认禁止，除非用户点名） | glitch · VHS · page burn · shader/WebGL | `css-distortion.md` · `css-destruction.md` · shader-transitions | 易抢戏、调试慢；快节奏口播慎用 |

**硬性规则（不变）：** 全片 ≥2 种转场；相邻两镜类型不重复；`TR` 0.24–0.28s。  
**升级规则（0.7+）：** 每支视频 Motion Plan 须列 **A 池轮换顺序** + 可选 **1 处 B 池**；`assets/style-history.json` 的 `lastTransitionSet` 下一支至少换 2 项。

Agent 写转场 HTML 前：**只读**本镜用到的 1 个 `transitions/css-*.md`，不要通读全部。

## TTS 路线对比（你最开始的 vs 新版官方）

| 维度 | **本 Skill（Edge TTS）** — 默认、推荐 | **hyperframes-media（官方）** |
|------|--------------------------------------|------------------------------|
| 命令 | `python scripts/generate-tts.py` | `node hyperframes-media/scripts/audio.mjs` 或 `npx hyperframes tts` |
| 中文质量 | ✅ 微软 Edge 神经网络，多方言音色 | ⚠️ Kokoro 本地偏英文；HeyGen 需 API |
| 费用 | 免费，无需 Key | HeyGen/ElevenLabs 需 Key；Kokoro 免费但中文弱 |
| 词级对齐 | ✅ **WordBoundary 原生** → `alignments.json` | HeyGen 原生 words；Kokoro/ElevenLabs 需再跑 Whisper |
| 字幕流水线 | `voice` 整句 wav + `subtitle` 显示层拆分 | `audio_request.json` lines + 官方 caption 链 |
| 读音纠偏 | `speak` 按 id（如「含金辆」） | 不同 schema，无本 Skill 的 `subtitleParts` 校验 |
| BGM/SFX | FFmpeg 程序化 + 可选用户素材 | HeyGen 素材库检索 / Lyria 生成 |
| 何时切换 | **始终默认 Edge** | 仅用户明确要求 HeyGen 音色 / 官方 audio 引擎 |

**结论：** 你「最开始用的」就是 **Edge TTS + 自研对齐脚本**；新版 HyperFrames 的 TTS 是 **另一条产品线**（HeyGen/Kokoro），**没有替换 Edge 流程**，也**不应**为中文口播默认改用 `hyperframes-media`。

---

# 真实感提质 · P0 / P1 / P2（已写入流水线）

> 目标：成片越来越像真人团队制作，减少「AI 模板 / 网页截图 / PPT 感」。  
> **Agent 必须按优先级执行**；P2 在条件触发时执行，不交给用户手动跑。

## P0 · 每支必做（真实感基础包）

| # | 能力 | 来源 | 何时 | Agent 动作 |
|---|------|------|------|-----------|
| P0-1 | **video-composition** | `hyperframes-creative/references/video-composition.md` | 写 HTML **前** | 每镜目标 8–10 视觉元素；视频字号尺度；accent 可见；禁止网页式居中堆叠 |
| P0-2 | **data-in-motion** | `hyperframes-creative/references/data-in-motion.md` | 分镜表有 **数据/对比/百分比/季度序列** 镜 | 数字配条形/色块/count-up；禁止饼图/dashboard；同概念只换数值不换整套 UI |
| P0-3 | **design-adherence** | `hyperframes-creative/references/design-adherence.md` | HTML 写 **后**、TTS 前 | 对照 `design.md` 查 hex/字体/圆角/Don'ts；违规 **必须改 HTML** 再继续 |
| P0-4 | **snapshot 快检** | `npx hyperframes snapshot` | **≥4 镜** 或 inspect 报 layout 风险 | `npx hyperframes snapshot --frames 9`（Agent 内部）；目视叠字/空镜/首镜布局 |

## P1 · 明显提质（条件 + 默认）

| # | 能力 | 来源 | 何时 | Agent 动作 |
|---|------|------|------|-----------|
| P1-1 | **atomic rules / gsap-effects** | `hyperframes-animation/rules-index.md` · `rules/gsap-effects.md` | 写 **L2/L3**（count-up、punch、卡片高亮、kinetic） | 先查 rules 再手写 GSAP；禁止重复发明 y:30 |
| P1-2 | **beat-direction** | `hyperframes-creative/references/beat-direction.md` | 预估口播 **>90s** 或 **≥6 镜** | 写 `design.md` 时声明节奏模板（快-快-慢-转场）；Motion Plan 对齐 |
| P1-3 | **design-picker** | `hyperframes-creative/references/design-picker.md` | 用户 **未指定** 视觉风格/mood | **主动 offer**：「要浏览器可视化选风格吗？」；用户同意则生成 `.hyperframes/pick-design.html` |
| P1-4 | **L4 转场 A+B 池** | §0.7 转场分级 | 每支 | Motion Plan 列 A 池 ≥3 种 + 可选 1 处 B 池；实现读对应 `css-*.md` |

## P2 · 有余力 / 条件触发

| # | 能力 | 来源 | 何时 | Agent 动作 |
|---|------|------|------|-----------|
| P2-1 | **media-use SFX** | `media-use` skill · `resolve.mjs` | 用户已 `hyperframes auth login` **或** 明确要求更好音效 | 用 `resolve --type sfx` 替代纯 sine 滴声；**TTS 仍 Edge** |
| P2-2 | **motion.json sidecar** | `hyperframes-cli` inspect | **≥5 镜** 且每镜 L2/L3 tween ≥3 | 写 `index.motion.json`；`npm run check` 时 inspect 验入场/stagger |
| P2-3 | **registry 组件** | `hyperframes-registry` · `hyperframes add` | 数据对比/图表镜重复劳动 | 可 `add` chart/grain 块再改中文样式；**非默认** |
| P2-4 | **animation-map 审计** | `hyperframes-animation/scripts/animation-map.mjs` | Post-audit 仍觉动效「空/乱」 | Agent 内部跑，根据 JSON 补 tween |
| P2-5 | **Lambda 云渲染** | `hyperframes lambda render` | 用户要求导出且本地 render 过长/4K | 仅 **用户确认 render 后** |

## 触发条件速查

```text
每支视频     → P0-1 P0-3 P0-4 P1-4
有数据镜     → + P0-2
未指定风格   → + P1-3（offer design-picker）
>90s / ≥6镜  → + P1-2
L2/L3 动效   → + P1-1
≥4 镜        → P0-4 snapshot
≥5镜复杂动效 → + P2-2 motion.json
HeyGen 登录  → + P2-1 可选 SFX
数据图表重复 → + P2-3 registry
```

## design-adherence 清单（P0-3 · Agent 内部执行）

HTML 写完后逐项对照 `design.md`（无 design 则对照 house-style）：

1. HTML 中每个 hex 是否都在 design 调色板内？有无发明色？
2. `font-family` / 字重是否与 spec 一致？
3. `border-radius` 是否符合 `rounded` 声明？
4. padding/gap 是否在声明密度范围内？
5. Do's and Don'ts 是否违反（glass 默认、左侧竖条、渐变字等）？

**有违规 → 改 HTML → 再跑 P0-3，通过后才进 TTS。**

---

# 执行顺序

1. **本 Skill** — 环境检查、稿子拆镜、**视觉风格选定**、音频规划
2. **`design-taste-frontend`**（taste-skill）— **必读**，反 slop pre-flight；设 `tasteDials`（默认 5/6/6）
3. **`templates/anti-slop-motion-scheme.md`** — **必读**，五道门禁 + L0–L4 动效（拒绝 AI 味 + 防廉价静态）
4. **`hyperframes-creative`** — `visual-styles` / `house-style`；写 **`design.md`**；**P0-1** 读 `video-composition.md`；有数据镜 **P0-2** 读 `data-in-motion.md`；未指定风格 **P1-3** offer `design-picker`
5. **`hyperframes-animation`** — L0: `adapters/css-animations.md` + GSAP: `adapters/gsap.md`；**L4** + **P1-1** rules；**P1-2** `beat-direction`（长片）
6. **`design-motion-principles`** — **必读**，入场 stagger、缓动、Post-audit（L1–L3）
7. **`web-typography`** — **必读**，标题/字幕字号层级（尤其竖屏）
8. **`templates/visual-style-guide.md`** — **必读**，首镜布局、片尾变体、禁止同质化清单
9. **`templates/hyperframes-zh-checklist.md`** — **必读**，中文字体/字幕安全区/背景/圆角 + **生成后自检**
10. **`templates/delivery-pitfalls.md`** — **必读**，交付复盘避坑（背景/布局/字幕对齐/流水线；可转发给接手人）
11. **`templates/scene-density-guide.md`** — **必读**，镜内防太空、副信息层次
12. **`templates/subtitle-tts-guide.md`** — **必读**，字幕语义拆条 + `speak` 读音
13. **`hyperframes-core`** + **`hyperframes-animation`** — 写 HTML composition、GSAP **`mt` 时间轴**动画、字幕（**禁止 ScrollTrigger**）
14. **Agent 自动执行** — TTS（含 Edge WordBoundary 对齐）、时间轴、**交付自检脚本**、SFX 对齐、`npm run check`（见「全自动交付流水线」）
15. **用户手动一步** — `npm run dev` 预览；**仅用户确认后再 render**

---

# 全自动交付流水线（Agent 必须跑完，用户只启动预览）

> **对用户友好原则：** Agent 在对话里**自动执行**下方全部步骤，**不要**把 TTS、校验等命令丢给用户自己跑。交付时用户**只需**打开终端执行 `npm run dev` 即可预览成片。

## Agent 必须自动完成（按顺序）

| 步骤 | 动作 | 说明 |
|------|------|------|
| 1 | 环境预检 | FFmpeg / Node≥22 / Python / **edge-tts**；**faster-whisper 可选**（仅 Edge 边界缺失时兜底，见 `requirements-align.txt`） |
| 2 | 创建/进入项目 | `package.json`、`hyperframes.json`、`meta.json`、`.git`（若新建）；**从本 skill `templates/` 复制 `scripts/` 到项目** |
| 3 | 资源准备 | 头像下载→`assets/avatar.png`；FFmpeg 生成 `bgm.mp3`、`sfx_*.mp3` |
| 3a | **风格路径** | 用户指定 → visual-styles + style-history；**未指定 → P1-3 offer design-picker** |
| 3b | **视觉规划** | taste + anti-slop + visual-style-guide + scene-density + **P0-1 video-composition**；有数据镜 +**P0-2 data-in-motion**；写 **`design.md`**（Motion Plan + tasteDials + L4 表 + 长片 beat-direction） |
| 3c | **Pre-flight** | anti-slop 门禁 2 + **P0-1 密度/字号**；不通过禁止写 HTML |
| 3d | **口播→lines.json** | `subtitle-tts-guide.md`；`voice` 整句；标记哪些 scene 为数据镜（供 P0-2） |
| 4 | 拆镜 + HTML | zh-checklist + scene-density；**P1-1** L2/L3 查 rules；数据镜遵守 P0-2；L0–L4 + `mt` |
| 5 | TTS + 字幕对齐 | `generate-tts.py` → alignments.json |
| 5b | **改 subtitleParts 后** | 若只改显示断句、未重录：`realign-line.py <id>` → 同步 alignments；**必查** parts 条数一致 |
| 6 | 时间轴同步 | `apply-audio-schedule.mjs` |
| 6b | 品牌片尾 | `apply-brand.mjs`（若有） |
| 7 | 动画/音效对齐 | schedule 对齐 L2/转场/SFX；**P2-1** 已登录 HeyGen 时 media-use 补 SFX |
| 7b | HTML 编码校验 | `verify-index-encoding.py` |
| 7c | **design-adherence（P0-3）** | 对照 `design.md` hex/字体/圆角/Don'ts；**0 违规** |
| 7d | 中文交付自检 | `verify-delivery-checklist.py` → 0 ERROR |
| 7e | Post-audit | anti-slop 门禁 4 + taste |
| 7f | **snapshot（P0-4）** | **≥4 镜**：`npx hyperframes snapshot --frames 9` |
| 7g | **motion.json（P2-2）** | ≥5 镜且动效复杂：写 sidecar + inspect 验动效 |
| 7h | **registry（P2-3）** | 数据图表镜可选 `hyperframes add` |
| 7i | **animation-map（P2-4）** | 动效仍空/乱时内部审计 |
| 8 | 质量门禁 | `npm run check` → 0 error |
| 9 | 交付 + style-history | 更新 `style-history.json`；用户仅 `npm run dev` |

## 用户只需手动做

```powershell
cd "<项目路径>"
npm run dev
```

浏览器打开终端里的 Studio 地址，点播放检查字幕、口播、动效、音效。

> **不要**让用户跑 `verify-index-encoding.py`、`npm run check`、TTS 等——Agent 交付前已在后台跑完（含 HTML 编码校验）。

## 新建项目：复制模板脚本

从本 skill 目录复制到用户项目（勿每次手写脚本）：

```text
templates/scripts/generate-tts.py      → 项目/scripts/
templates/scripts/realign-line.py      → 项目/scripts/  （改 subtitleParts 条数后、不重录 TTS 时用）
templates/scripts/align-subtitles.py   → 项目/scripts/  （可选：Edge 边界缺失时 Whisper 兜底）
templates/scripts/run-align.py         → 项目/scripts/  （可选兜底）
templates/scripts/fallback-alignments.py → 项目/scripts/  （Whisper 全失败时的草稿兜底）
templates/scripts/apply-audio-schedule.mjs → 项目/scripts/
templates/requirements-align.txt       → 项目/（或 pip install faster-whisper）
templates/scripts/apply-brand.mjs      → 项目/scripts/
templates/scripts/verify-index-encoding.py → 项目/scripts/
templates/audio/lines.json.example     → 项目/audio/lines.json（按口播填写）
templates/assets/brand.json.example    → 项目/assets/brand.json（无片尾则 outroMode: off）
templates/design.md.example            → 项目/design.md（按选定 visual-styles 预设改写，含 Motion Plan）
templates/style-history.json.example     → 项目/assets/style-history.json（可选，频道轮换用）
templates/visual-style-guide.md        → Agent 写 HTML 前必读（不复制到项目）
templates/delivery-pitfalls.md       → Agent 开项/交付前必读（不复制到项目；可单独转发给人）
templates/anti-slop-motion-scheme.md   → Agent 写 HTML 前必读（不复制到项目）
templates/scene-density-guide.md       → Agent 写 HTML 前必读（不复制到项目）
templates/subtitle-tts-guide.md        → Agent 写 lines.json 前必读（不复制到项目）
```

详见 **`templates/README.md`**。`index.html` 须预留 `id="voiceover"` 单轨与 `id="bgm"`。**每个项目必须有 `design.md`**（含 **Motion Plan** 与 **tasteDials**），禁止无 design 直接套默认科技蓝 UI。

## 禁止交给用户的步骤

以下必须由 Agent 在会话中执行完毕，**不得**写进「请你运行」清单：

- ❌ `python scripts/generate-tts.py`
- ❌ `python scripts/run-align.py`（**非默认**；仅 Edge WordBoundary 缺失且须 Whisper 兜底时）（**非默认**；仅 Edge WordBoundary 缺失且须 Whisper 兜底时）
- ❌ `node scripts/apply-audio-schedule.mjs`
- ❌ `node scripts/apply-brand.mjs`（有品牌片尾时）
- ❌ `python scripts/verify-index-encoding.py`（**Agent 内部质检**，用户无需知道）
- ❌ `npm run check` / `npm install`（首次 `npx hyperframes` 由 Agent 代跑即可）
- ❌ 头像下载、BGM/SFX 生成、GSAP 时间轴手调

### Agent 写 lines.json 禁止项

- ❌ 为 `maxHan` 把一句口播拆成 s2a/s2b/s2c 并各自 TTS
- ❌ 在「含金量」等词中间拆 TTS（即使用户未提供 speak）
- ❌ 全局替换 `speak` 字符串（须按 id 整行替换用户读音表）
- ✅ 口播整句 `voice` + `speak` 纠音；字幕/画面用 `subtitle` 或 `display` 另写、另拆

## 用户只需手动做（唯一一步）

```powershell
cd "<项目路径>"
npm run dev
```

**用户不需要、也不应该执行：**

- `python scripts/verify-index-encoding.py` — 见下方说明
- `npm run check` / TTS / 时间轴脚本 — Agent 交付前已全部跑完

### `verify-index-encoding.py` 是干什么的？（仅 Agent）

| 谁跑 | 何时 | 作用 |
|------|------|------|
| **Agent** | `npm run check` **之前**，全自动流水线内 | 读 `index.html`，检查中文是否被 Studio 写成 `??`、标签是否断裂；失败则 Agent 重建 HTML，**不把此命令交给用户** |
| **用户** | **不跑** | 交付后直接 `npm run dev` 预览即可 |

若 Agent 已交付且你未在 Studio 改中文，**跳过 verify、直接 dev 启动没问题**。

## 仍须用户确认后才做

- ❌ `npm run render` / 导出 MP4（用户明确说「导出」「render」才执行）

## 交付话术模板

见 **`examples/prompt-template.md`** 末尾「Agent 交付话术」与「导出 MP4」章节。

**对用户只说这一句预览命令：**

```text
cd "<项目路径>"
npm run dev
```

**禁止**在交付清单里写 `verify-index-encoding.py`、`npm run check`、TTS 等——这些 Agent 已跑完。若需说明校验，用一句话：「编码与 lint 已在交付前通过，你直接 dev 预览即可。」

---

# 第一步：环境预检

执行本 Skill 时**必须先做环境检查**，缺失则提示用户安装。

## 系统依赖

| 组件 | 要求 | 安装方式 |
|------|------|---------|
| FFmpeg | ✅ 必须可用 | `winget install FFmpeg` 或系统包管理器 |
| Node.js | ✅ >= 22 | https://nodejs.org |
| Python + edge-tts | ✅ 中文 TTS 需要 | `pip install edge-tts` |

## Skill 安装（Cursor / Codex / Trae）

本 skill（合集仓库需 `@` 指定）：

```bash
npx skills add ztaihang/agent-skills@hyperframes-shorts
```

`npx skills add` 会按当前 runtime 写入 `~/.agents/skills/`、`~/.cursor/skills/` 或 `~/.codex/skills/` 等路径。末尾若出现 `PromptScript does not support global skill installation`，可忽略——Cursor/Codex 已成功。

### 必须安装（HyperFrames 0.7+ 领域 skill）

```bash
# 推荐：一次拉齐核心 skill（含 core / animation / creative / cli）
npx hyperframes skills update

# 或按需单独安装：
npx skills add heygen-com/hyperframes --skill hyperframes
npx skills add heygen-com/hyperframes --skill hyperframes-cli
npx skills add heygen-com/hyperframes --skill hyperframes-core
npx skills add heygen-com/hyperframes --skill hyperframes-animation
npx skills add heygen-com/hyperframes --skill hyperframes-creative
```

> **0.7 变更：** 独立 `gsap` / `css-animations` skill 已并入 **`hyperframes-animation`**；`visual-styles.md` / `house-style.md` 已迁入 **`hyperframes-creative`**。无需再装 `@gsap` / `@css-animations`。

### 必须安装（画面差异化 — 第三方 skill）

```bash
npx skills add leonxlnx/taste-skill@design-taste-frontend -g -y
npx skills add kylezantos/design-motion-principles@design-motion-principles -g -y
npx skills add wondelai/skills@web-typography -g -y
```

写 `index.html` **前**必须读取 **taste-skill** + **hyperframes-creative** + **hyperframes-animation** + **design-motion-principles** + **web-typography** + **`templates/anti-slop-motion-scheme.md`**；缺失则提示安装，**不得**跳过仍用同一套默认 UI。

**taste-skill 短视频默认 dial**（写入 `design.md`，用户可覆盖）：`DESIGN_VARIANCE: 5` · `MOTION_INTENSITY: 6` · `VISUAL_DENSITY: 6`  
**HyperFrames override：** 只用 GSAP 主时间轴 `mt`；**禁止** ScrollTrigger / scroll 监听（taste-skill 的 web 规则不适用于成片时间轴）。

### 视觉风格（不需要单独装 skill）

`heygen-com/skills@visual-style` **已从 GitHub 仓库下架**（仓库现仅有 heygen-avatar / heygen-translate / heygen-video），skills.sh 页面是过期索引，**不要再尝试安装**。

直接用已安装的 **`hyperframes-creative`** skill 内置文件：

- `references/visual-styles.md` — 8 套命名预设（配色、缓动、shader）
- `references/house-style.md` — 默认调色板与字号
- `references/design-picker.md` — 可视化选风格工作流

若仍想要独立 visual-style skill，可试第三方（非官方）：

```bash
npx skills add calesthio/openmontage@visual-style
```

但对 HyperFrames 短视频，**内置 `visual-styles.md` 已足够**。

### 不需要安装

| Skill | 原因 |
|-------|------|
| **`hyperframes-media`** | 中文项目用 **Edge TTS**（`scripts/generate-tts.py`），不用 Kokoro `npx hyperframes tts` |

### 检查是否已安装（PowerShell）

```powershell
# 推荐路径（npx skills add / hyperframes skills update 安装后）
Test-Path "$env:USERPROFILE\.agents\skills\hyperframes-shorts\SKILL.md"
Test-Path "$env:USERPROFILE\.agents\skills\hyperframes\SKILL.md"
Test-Path "$env:USERPROFILE\.agents\skills\hyperframes-cli\SKILL.md"
Test-Path "$env:USERPROFILE\.agents\skills\hyperframes-core\SKILL.md"
Test-Path "$env:USERPROFILE\.agents\skills\hyperframes-animation\SKILL.md"
Test-Path "$env:USERPROFILE\.agents\skills\hyperframes-creative\SKILL.md"
Test-Path "$env:USERPROFILE\.agents\skills\design-taste-frontend\SKILL.md"
Test-Path "$env:USERPROFILE\.agents\skills\design-motion-principles\SKILL.md"
Test-Path "$env:USERPROFILE\.agents\skills\web-typography\SKILL.md"
npx hyperframes skills check   # 应显示 21 current 或至少 core 5 项 current
```

部分旧安装可能在 `~/.codex/skills/` 或 `~/.claude/skills/`，任一存在即可。

缺失必须项时提示：

> 缺少 [hyperframes / hyperframes-cli / hyperframes-core / hyperframes-animation / hyperframes-creative / design-taste-frontend / design-motion-principles / web-typography]，请先运行 `npx hyperframes skills update` 后再使用本 Skill。

---

# 第二步：用户输入格式

用户用**提示词模板**填表即可，**不填的可选项 = 本视频不适用**。

| 字段 | 必填 | 不填时 |
|------|------|--------|
| 项目路径 | ✅ | 用户指定存放 HyperFrames 工程的**本地目录**（任意路径，见 `examples/prompt-template.md`） |
| 口播原文 | ✅ | — |
| 视频尺寸 | 否 | 默认 1920×1080 横屏 30fps |
| 总时长 | 否 | 按口播 + TTS 实测 |
| 风格 | 否 | 按口播 mood + 项目名轮换（见 `templates/visual-style-guide.md`）；**禁止**默认「快节奏科技蓝」 |
| **【品牌片尾】块** | 否 | `outroMode: off`，**完全不生成片尾** |
| 片尾样式 | 否 | 不写 = **默认模板**；写「自定义」= 不用默认 |
| 片尾口播全文 | 否* | *有片尾块时必填；完整 TTS 念出 |
| 频道名 / 头像 | 否* | *default 模式建议填 |

### 提示词模板文件（复制使用）

完整模板（标准 / 最小 / 片尾 / **预览与导出命令**）见：

**`examples/prompt-template.md`**

用户**只需给「片尾口播全文」一行**，不必自己拆句；Agent 按句号拆成 2～3 条 `lines.json` + TTS，并同步 `assets/brand.json`。

**不写【品牌片尾】块** → `outroMode: off`，无片尾镜。片尾三种模式详见 **`examples/outro-rules.md`**。

---

# 第三步：文案原则（口播 ≠ 上屏 ≠ 字幕）

**口播稿（`voice`）**用于：TTS 整句配音、拆镜结构、时长估算。一条 breath = 一条 `lines.json` = 一个 wav。  
**上屏文案**用于：观众阅读，可与口播不一致，允许书面化、精简、美化。  
**底部字幕（`subtitle`）**用于：单行上屏，可短于口播；超长只在显示层拆条，**不拆 TTS**。拆条须同时满足 **上限（≤maxHan）与下限（≥minHan）**，避免孤词快闪。

> **硬性：** 禁止为通过字幕 `maxHan` 校验而把一句口播拆成 s2a/s2b/s2c 并各自 TTS。  
> **节奏：** 一条 wav 建议 **3–6** 条字幕；细则见 **`subtitle-tts-guide.md` §5.3**。

### 必须保留

- 数字、百分比、公式、日期
- 平台名、政策名、专有名词
- 核心论点、结论、行动建议的**含义**

### 允许美化（仅上屏文案）

- 删除口头语（"今天咱们就"、"目前来说"）
- 合并重复句；改成更短更利落的标题/金句
- 修正明显错别字

---

# 第四步：拆镜规则

按**语义断点**拆分，一个语义单元 = 一个镜头。

| 语义断点 | 示例 |
|---------|------|
| 话题切换 | "说完 A，我们再来看 B" |
| 背景→数据 | "根据最新数据显示…" |
| 并列列举 | "第一…第二…第三…" |
| 因果转折 | "但是…"、"因此…" |
| 总结升华 | "总的来说…"、"所以…" |

### 每镜产出

~~~text
Scene N: [语义标题]
  口播:    [原文片段]
  上屏:    [精简后的屏幕文案]
  时长:    [秒]
  布局:    [选一个布局模式]
  转场:    [入场/出场效果]
  音频:    [配音/TTS/音效/BGM]
~~~

---

# 第四步 B：品牌片尾（三种模式）

> **完整规则见 `examples/outro-rules.md`**

| 用户输入 | `outroMode` | 行为 |
|---------|-------------|------|
| **没写**【品牌片尾】 | `off` | **完全不生成片尾镜**、无片尾 TTS、不用默认模板 |
| **写了**【品牌片尾】，未说自定义 | `default` | **三变体之一**（A 头像金句 / B 全屏 kinetic / C 频道卡片），按 `design.md` 风格选，见 `visual-style-guide.md` |
| **写了**片尾 + 明确要别的样式 | `custom` | **不用默认模板**，按「片尾说明」单独实现**片尾镜** |

**硬性规则：** 绝不擅自加用户没写的片尾；没写块 = 当没有片尾。

## 默认片尾格式（`outroMode: default`）

~~~markdown
【品牌片尾】
片尾样式：默认模板
频道名：浣熊不加班
头像：https://你的头像直链.webp

片尾口播全文：
掌握 AI 实战，下班不留遗憾。关注浣熊不加班，我们下期见！
~~~

`片尾样式：默认模板` 可省略——**只要没写「自定义」就视为默认**。用户只填「片尾口播全文」一行即可。

## 自定义片尾格式（`outroMode: custom`）

~~~markdown
【品牌片尾】
片尾样式：自定义
片尾说明：（布局、动效、要不要头像等具体要求）

频道名：浣熊不加班
头像：（可选）

片尾口播全文：
……
~~~

触发词：`片尾样式：自定义` / `不用默认模板` / `片尾说明：` 有具体描述。

## Agent 必做（按模式）

### `off`

1. `assets/brand.json`：`{ "outroMode": "off", "useDefaultOutro": false }`
2. `lines.json` **无片尾镜行**（最后一镜 `scene` 不为片尾）；正文结尾不夹片尾句
3. 跳过 `apply-brand.mjs` 默认 patch

### `default`

1. 拆「片尾口播全文」→ `lines.json` **最后一镜**（2～3 条，带 `scene` 编号）
2. 正文不重复片尾句
3. 按 `design.md` 风格选 **片尾变体** `outroVariant`：`a` | `b` | `c`（见 `templates/visual-style-guide.md` §6）
4. `assets/brand.json`：`outroMode: "default"`, `useDefaultOutro: true`, `outroVariant`, 自动推导 `outroTitle` / `followText` / `outroSub`
5. 片尾镜 HTML/GSAP **按变体实现**（禁止每支复制 variant A）
6. `apply-brand.mjs` → 头像（变体 A/C）+ patch `#sc{N}-title` / `#sc{N}-follow` / `#sc{N}-sub`

### `custom`

1. 片尾口播仍进 `lines.json` 最后一镜并 TTS（必须念出）
2. `assets/brand.json`：`outroMode: "custom"`, `useDefaultOutro: false`, `customOutroNotes` 存用户说明
3. **不**用默认片尾 zoom / `#avatar-ring` 动效；按说明重写片尾镜 HTML + GSAP
4. `apply-brand.mjs` 仅下载头像（若给了 URL）

### 流水线（三种模式共用）

`generate-tts.py`（含 Edge WordBoundary → `alignments.json`）→ `apply-audio-schedule.mjs` → `apply-brand.mjs`（按模式跳过或部分执行）

配音轨仅用 **一条** `voiceover.wav`；字幕上屏去句末标点。

### `assets/brand.json` 结构（default 示例）

~~~json
{
  "outroMode": "default",
  "useDefaultOutro": true,
  "outroVariant": "b",
  "channelName": "浣熊不加班",
  "avatarUrl": "https://...",
  "outroScript": "掌握 AI 实战，下班不留遗憾。关注浣熊不加班，我们下期见！",
  "outroTitle": "掌握 AI 实战，下班不留遗憾。",
  "followText": "关注浣熊不加班",
  "outroSub": "我们下期见！"
}
~~~

`outroVariant`：`a` = 双卡+头像金句；`b` = 全屏 kinetic 无头像；`c` = 频道卡片+小头像。详见 **`outro-rules.md`**。

## 口播 → 动效（按 `outroVariant` 对齐片尾 TTS 的 `start`）

| 变体 | 第 1 条口播 | 第 2 条口播 | 头像 |
|------|------------|------------|------|
| **A** | `#sc{N}-title` zoom punch | 头像弹出 + `#sc{N}-follow` / `#sc{N}-sub` | 圆形居中 |
| **B** | 全屏 `#sc{N}-title` kinetic 逐字 | `#sc{N}-follow` + `#sc{N}-sub` 淡入 | 无 |
| **C** | 频道卡片 + 角标头像入场 | `#sc{N}-follow` / `#sc{N}-sub` 卡片内 punch | 小角标 |

（N = `schedule` 中片尾镜最大 `scene` 号。变体 B/C 仍 patch 相同 id，HTML 结构不同。）

## 头像

| 输入 | Agent 做法 |
|------|-----------|
| `https://...` | `apply-brand.mjs` 下载到 `assets/avatar.png`（**仅 https**） |
| `http://...` | **不下载**；终端提示改用 https / `avatarPath` / 本地 `assets/avatar.png` |
| 本地路径 | `brand.json` 的 `avatarPath` → 复制到 `assets/avatar.png` |
| 留空且已有 `assets/avatar.png` | 直接复用，不下载 |

HTML：`<img id="brand-avatar" src="assets/avatar.png">`，圆形 120–160px，`object-fit: cover`。

## 最后一镜（片尾 scene）

- 独立 scene；布局按 **outroVariant**（A: `dual-highlight-closing` / B: `full-bleed-statement` / C: `narration-card-grid` 或 `metric-comparison-band`）
- 时长 = 片尾镜所有 TTS 实测之和；**不淡出黑屏**
- 动效时间取 `schedule` 中片尾 `scene` 各条的 `start`，**不要写死镜号或 id**

### GSAP 参考（按片尾镜行动态取时）

~~~javascript
const outroScene = Math.max(...schedule.map((l) => l.scene));
const outroLines = schedule.filter((l) => l.scene === outroScene).sort((a, b) => a.start - b.start);
const tSlogan = outroLines[0]?.start ?? sceneStart;
const tFollow = outroLines[1]?.start ?? tSlogan + 0.3;
const titleSel = `#sc${outroScene}-title`;

mt.fromTo(titleSel, { scale: 0.98 }, { scale: 1.08, duration: 0.14, ease: "power2.out" }, tSlogan);
mt.to(titleSel, { scale: 1, duration: 0.12, ease: "power2.in" }, tSlogan + 0.14);
mt.fromTo("#avatar-ring", { opacity: 0, scale: 0.5, y: 36 }, { opacity: 1, scale: 1, y: 0, duration: 0.32, ease: "back.out(1.5)" }, tFollow);
~~~

分镜表注明：`品牌片尾（sc{N}）` + 片尾口播全文。

---

# 第五步：布局模式

### 画面比例规则

- **默认**：1920×1080（横屏 16:9）
- **竖屏 9:16**：用户指定时使用 1080×1920
- **其他比例**：用户明确要求时按需设置
- 所有布局模式同时适配横屏和竖屏，只是排列方向（行/列）根据宽高比自动调整

### 布局模式

基于 HTML + CSS + GSAP。默认 1920×1080。

| 模式名 | 适用场景 | 布局示意 |
|--------|---------|---------|
| `split-narration-visual` | 引入话题、行业背景 | 左文右图 60/40；对侧 **主题化 SVG**（网格/折线/流程，**非默认线框地球**） |
| `narration-card-grid` | 列举 2-4 个并列概览 | 上旁白 + 中 2×2 **实底/线框卡**（材质见 `design.md` `surface`，**默认非 glass**）；强调项 pulse |
| `metric-comparison-band` | 系数/价格/比例变化 | 全宽横条：名称 \| **数字 count-up** \| 变化标签 \| 趋势折线 |
| `bar-comparison-panel` | 成本、结构、占比 | 单面板内柱状对比 + 条柱 stagger 入场 |
| `narration-trend-list` | 罗列趋势、要点 | 左旁白 + 右 **实底面板** 列表 + 渐变圆点；列表项 stagger |
| `dual-highlight-closing` | 结论、行动建议、**品牌片尾 A** | **双强调卡**（accent 边框，非固定金边）；片尾可叠头像 |
| `full-bleed-statement` | 单句强冲击、**片尾 B** | 居中大字 + 装饰线/暗场；**L1 标题 stagger 必做** |
| `kinetic-typography` | 关键数据/金句 | 大字逐字弹跳（**全片 L3 共 2–4 处**） |
| `data-chart-race` | 数据随时间变化 | 图表随时间演进 + **L2 对齐口播** |

---

# 第六步：视觉风格（每项目必须差异化）

> **完整流程见 `templates/visual-style-guide.md` + `templates/anti-slop-motion-scheme.md`**

## 写 HTML 前强制步骤

1. 读 **`design-taste-frontend`**，设 **tasteDials**（默认 5/6/6）；跑 taste **pre-flight**
2. 读 **`anti-slop-motion-scheme.md`**，理解五道门禁与 **L0–L4 动效**
3. 读 **`hyperframes-creative/references/visual-styles.md`**，选定 **1 套命名风格**
4. 读 **`hyperframes-animation`**（`adapters/css-animations.md` + `adapters/gsap.md`）；**L4** 读 `transitions/catalog.md` 并按 §0.7 **A/B 分级**选定本支转场表
5. 读 **`design-motion-principles`**、**`web-typography`**
6. 在项目根写 **`design.md`**（从 `templates/design.md.example` 改，**含 Motion Plan + L4 转场表**）
7. 定 **首镜布局**（禁止无理由连续项目都用 `split-narration-visual`）
8. 有片尾时定 **outroVariant**（`a` | `b` | `c`）
9. **Pre-flight 通过** 后才允许写 `index.html`

## 动效最低标准（防廉价感 — 详见 anti-slop §三）

| 层级 | 必做 | 说明 |
|------|------|------|
| **L0** | `#root` 静态背景 | gradient/网格/暗角；**禁止**每镜 CSS `infinite` ambient |
| **L1** | 每镜 | 主内容 stagger 入场；0.5s 内主块可见 |
| **L2** | 有数字/并列/流程时 | count-up、pulse、逐步高亮 **对齐 schedule** |
| **L3** | 全片 2–4 处 | kinetic 金句，非每句 |
| **L4** | 镜间 | A 池轮换 + 可选 1 处 B 池亮点转场 |

## 优先级

1. 用户指定的风格 / `design.md`
2. `visual-styles.md` 命名预设 + 本项目 `design.md`
3. **`web-typography`** — 字号层级
4. **`design-motion-principles`** — 动效节奏
5. **`hyperframes-animation/adapters/css-animations.md`** — 背景装饰
6. `hyperframes-creative/references/house-style.md` — 仅填 gap，**禁止** lazy defaults（cyan-on-dark、渐变字、左侧竖条）

## 选色与轮换

- 无品牌色时从所选 **visual-styles 预设**取 token，不是固定科技蓝
- **用户未指定风格时**：口播 mood 优先 + 项目文件夹名 hash 轮换（算法见 `visual-style-guide.md`）
- 连续同频道项目：**至少 3 项不同**——命名风格、首镜布局、片尾变体（A/B/C）、背景 atmosphere、转场 shader 中选 3 项
- 禁止复制上一项目的整段 HTML/CSS 组件套

---

# 第七步：音频规划

### 配音（TTS）

**默认音色：`zh-CN-YunyangNeural`（云扬 · 男声 · 专业新闻感）**

中文短视频优先使用 **Edge TTS**（免费、无需 API Key）。**每条 `lines.json` = 一段口播 wav**；字幕可在显示层拆多条。

```bash
# 口播 → wav → 词级对齐 → 字幕时间轴
python scripts/generate-tts.py        # wav + schedule.json + alignments.json (edge-tts)
node scripts/apply-audio-schedule.mjs # 读 alignments 写多条 .sl + GSAP
# 可选兜底: python scripts/run-align.py  （Edge 未返回 WordBoundary 时）
```

**口播 / 字幕 / TTS 规则（必须 — 细则见 `templates/subtitle-tts-guide.md`）：**

- 写 `lines.json` **前**读 **`subtitle-tts-guide.md`**
- **`voice`（TTS 口播）**：整句一条 wav；**保留标点**含句末 `。！？，`；**禁止**为字幕宽度拆 id
- **`text`**：兼容旧稿，等同 `voice`；新稿优先写 `voice`
- **`speak`**：可选，仅 TTS；用户读音表须 **按 id 整行** 填写，禁止全局替换
- **`subtitle` / `subtitleParts`**：底部上屏；**必须是 `voice` 的连续子串**（只拆单行宽度，禁止缩写/改写）；**`minHan ≤ visualUnits ≤ maxHan`**（横屏 8–16 / 竖屏 7–12）；每条 wav **建议 3–6 条**，禁止孤词碎条（见 **`subtitle-tts-guide.md` §5.3**）；超长只在逗号/句号/完整子句处拆 **显示**
- **无 subtitle 时**：脚本从 `voice` 自动按标点拆多条 `.sl`（如 `s2`、`s2_2`），**共享同一段 wav**
- **`generate-tts.py`**：`boundary="WordBoundary"` 合成；聚合 subtitleParts → **`audio/alignments.json`（engine=edge-tts）**；`speak` 自动 `normalize_speak()`；对 `voice` 超长仅 **WARN**
- **`align-subtitles.py` / `run-align.py`**：**可选兜底**（Edge 边界缺失时 Whisper 重算 alignments）
- **`fallback-alignments.py`**：Whisper **崩溃/不可用**时草稿兜底；**须听检**多 part 字幕
- **`apply-audio-schedule.mjs`**：**优先**读 `alignments.json` 写字幕 GSAP；`engine: fallback` 时对后续字幕条略提前 0.08s；缺失或 hash 过期才 inline 估算
- **上屏 `.sl`**：去掉该条 **末尾** 标点（`，。！？：；、`）；不是去掉 TTS 里的标点
- **硬性：底部字幕永远单行**——禁止两行、禁止 `<br>` 换行
  - 超长须在 **subtitle 显示层** 拆多条 `.sl`；**禁止**用 ellipsis 长期挡字
  - 每条 `.sl` CSS **必须**含：`white-space: nowrap; overflow: hidden; text-overflow: ellipsis;`
- 多音字与英文产品名：**必须**检查读音，必要时只改 `speak` 不改 `voice`；同音纠音用 **非多音字、无空格连写**（如含金量 → speak「含金辆」），禁止 `含金 亮 的` 式词内顿音
- 字幕显示时长：多字幕时在同一 wav 内；**时间来自 `alignments.json`**（非字数估算）
- HTML 音轨用 **单条** `voiceover.wav`；GSAP 按各 `.sl` 子段时间轴
- **中文口播禁止夹英文缩写**（如「表达DNA」）——上屏与 TTS 均用中文「表达基因」

### 修改口播/字幕后的强制流程（防「字幕改了音频没变」）

改任意一条字幕文案时，**必须按顺序做完并试听**：

1. 改 `audio/lines.json` 对应 `id` 的 `voice`（及 `subtitle` / `speak` 若需要）
2. 跑 `python scripts/generate-tts.py`（校验 subtitle 为 voice 子串；写入 `schedule.json` + `alignments.json`）
3. 跑 `node scripts/apply-audio-schedule.mjs`（同步字幕 HTML）
4. （可选）Edge 边界缺失时：`python scripts/run-align.py` 或 `python scripts/fallback-alignments.py`
5. **Ctrl+C 重启** `npm run dev`，浏览器硬刷新
6. 跳到该条字幕时间点 **戴耳机确认口播**（不能只看字幕文字）

`apply-audio-schedule.mjs` 必须为配音轨加缓存破坏参数：

```html
<audio id="voiceover" src="audio/voiceover.wav?v=a1b2c3d4" …>
```

`voiceoverHash` 由 `generate-tts.py` 对全部 `lines.json` 口播拼接后 MD5 前 8 位生成；每条 `schedule` 行另有 `textHash` 供调试。**文案不变则 hash 不变；文案一变 hash 必变**，Studio 才会拉新音频。

**常见根因：** HyperFrames Studio / 浏览器按 `voiceover.wav` 路径缓存旧文件，只改字幕不重跑 TTS 或没有 `?v=` 时，用户会听到旧口播（如仍读 DNA）。

**Edge TTS 中文音色一览：**

| Voice ID | 名称 | 性别 | 风格 |
|----------|------|------|------|
| `zh-CN-YunyangNeural` | 云扬 | 男 | 专业、新闻（**默认**） |
| `zh-CN-XiaoxiaoNeural` | 晓晓 | 女 | 温暖、新闻 |
| `zh-CN-XiaoyiNeural` | 晓伊 | 女 | 活泼 |
| `zh-CN-YunjianNeural` | 云健 | 男 | 激情 |
| `zh-CN-YunxiNeural` | 云希 | 男 | 阳光 |
| `zh-CN-YunxiaNeural` | 云夏 | 男 | 可爱 |
| `zh-CN-liaoning-XiaobeiNeural` | 晓北 | 女 | 辽宁方言 |
| `zh-CN-shaanxi-XiaoniNeural` | 晓妮 | 女 | 陕西方言 |
| `zh-HK-HiuGaaiNeural` | 晓佳 | 女 | 粤语(港) |
| `zh-HK-HiuMaanNeural` | 晓曼 | 女 | 粤语(港) |
| `zh-HK-WanLungNeural` | 云龙 | 男 | 粤语(港) |
| `zh-TW-HsiaoChenNeural` | 晓臻 | 女 | 台湾 |
| `zh-TW-HsiaoYuNeural` | 晓雨 | 女 | 台湾 |
| `zh-TW-YunJheNeural` | 云哲 | 男 | 台湾 |

单条试听：`edge-tts --voice zh-CN-YunyangNeural --text "试听" --write-media test.mp3`

**语速控制（Edge TTS 支持，脚本需显式配置）：**

```python
RATE = "+12%"  # 默认快节奏；口播实测总时长 >150s 时用 "+18%"
communicate = edge_tts.Communicate(text, VOICE, rate=RATE)
```

| 实测总时长（TTS 后） | 推荐 `RATE` |
|---------------------|-------------|
| ≤ 150s | `+12%` |
| > 150s（约 2.5 分钟+） | `+18%` |

改语速后必须重跑 `generate-tts.py` → `apply-audio-schedule.mjs`，因为每句时长会变。

**不要用 `hyperframes-media` / Kokoro TTS 替代中文流程**，除非用户明确要求且本机 `kokoro-onnx` 可用。Kokoro 用 `--speed 1.2` 调速，与 Edge 的 `rate` 是不同参数。

TTS 文件作为 `data-track-index` 音频轨道引入 HTML

### 背景音乐（BGM）

- 建议用户自行提供或从免版权库获取
- 默认音量 `data-volume="0.3"`（比配音低）

### 音效（SFX）

分两类，**禁止只用单一 sine 滴声贯穿全片**：

| 类型 | 用途 | 示例文件 | 对齐时机 |
|------|------|---------|---------|
| **功能强调** | 卡片/步骤/数据弹出 | `sfx_card.mp3`（双音 chime） | 元素 GSAP 入场时刻 |
| **重点高亮** | 边框 pulse、结论 punch | `sfx_highlight.mp3` | 高亮动画开始时刻 |
| **流程步骤** | 并列流程逐步展开 | `sfx_step.mp3`（短 tick） | 每步 stagger +0.1s |
| **转场** | 可选，极轻或不加 | 噪声 sweep，**不用**纯 sine 滴声 | 默认快节奏可省略转场音 |

**本项目参考（Scene 3 四宫格）：** 每张功能卡入场各配一条 `sfx_card`；口播提到「静态扫描」「规则引擎」时配 `sfx_highlight` 强调边框。

生成示例（FFmpeg）：

```bash
# 功能卡 chime
ffmpeg -y -f lavfi -i "sine=frequency=523:duration=0.15" -f lavfi -i "sine=frequency=784:duration=0.15" \
  -filter_complex "[0][1]amix=inputs=2,afade=t=out:st=0.06:d=0.09,volume=2.5" assets/sfx_card.mp3
# 步骤 tick
ffmpeg -y -f lavfi -i "anoisesrc=d=0.08:c=pink" -af "highpass=f=800,lowpass=f=4000,volume=3" assets/sfx_step.mp3
# 高亮 ding
ffmpeg -y -f lavfi -i "sine=frequency=880:duration=0.2" -f lavfi -i "sine=frequency=1760:duration=0.12" \
  -filter_complex "[0][1]amix=inputs=2,volume=2" assets/sfx_highlight.mp3
```

HTML 中 `data-volume` **≥ 0.6**；交付前戴耳机确认功能强调音可感知。

### 音频轨道规划表

~~~text
| 轨道 | 文件 | 起始 | 时长 | 音量 | 说明 |
|------|------|------|------|------|------|
| track-0 | voiceover.wav | 0s | 全片 | 1.0 | TTS 配音 |
| track-1 | bgm.mp3 | 0s | 全片(循环) | 0.3 | 背景音乐 |
| track-2 | sfx_pop.mp3 | 3.5s | 0.5s | 0.8 | 数据弹出音效 |
~~~

---

# 第八步：输出分镜表

最终输出一份完整分镜表供 hyperframes skill 使用：

~~~markdown
## 分镜表

总时长: 45s | 30fps | 1080×1920 | 项目: /path/to/project

| # | 语义场景 | 口播 | 上屏文案 | 时长(s) | 布局 | 转场 | 音频 |
|---|---------|------|---------|---------|------|------|------|
| 1 | 引入话题 | ... | ... | 8 | split-narration-visual | fadeIn | TTS |
| 2 | 核心数据 | ... | ... | 12 | metric-comparison-band | slideUp | TTS+SFX |
| 3 | 对比分析 | ... | ... | 10 | bar-comparison-panel | wipe | TTS |
| 4 | 总结升华 | ... | ... | 10 | dual-highlight-closing | crossfade | TTS+BGM渐强 |
| 5 | 片尾 | ... | ... | 5 | full-bleed-statement | fadeOut | BGM收尾 |

### 音频
- TTS: audio/voiceover.wav (track-0, 全片)
- BGM: audio/bgm.mp3 (track-1, volume=0.3, 循环)
- SFX: audio/sfx_data.mp3 (track-2, scene-2 数据弹出)
~~~

---

# 第九步：交付流程（Agent 全自动构建，用户只预览）

> **硬性规则 1：** Agent 必须跑完「全自动交付流水线」全部步骤（含 `npm run check`），再回复用户。  
> **硬性规则 2：** 禁止主动执行 `render` 导出 MP4；须等用户预览确认后，用户明确要求时才导出。

## Agent 做完项目后必须交付

1. **项目路径**（所有文件、音频、资源已生成完毕）
2. **分镜表摘要**（镜数、实际总时长、**视觉风格名**、**首镜布局**、**片尾变体**、**tasteDials**、**Motion Plan 摘要**、`design.md` 是否已写）
3. **用户唯一操作**：`npm run dev` 预览（见下方命令）
4. 说明品牌片尾是否启用、实际时长与目标时长差异（若有）
5. 明确告知：「预览没问题后，跟我说一声再导出 MP4」

**不要**把 TTS 生成、时间轴同步、`npm run check` 列成「请你执行」——这些 Agent 已在后台做完。

## 用户本地预览（唯一需要用户手动执行的命令）

```powershell
cd "<项目路径>"
npm run dev
```

浏览器打开终端里显示的 Studio 地址，点播放检查：字幕、口播对齐、动效、字号、音效。

## Agent 已在交付前自动完成（用户无需重复）

- `python scripts/generate-tts.py`
- `node scripts/apply-audio-schedule.mjs`
- `npm run check`（lint + validate + inspect）

## 用户确认后再导出

**仅当用户明确说「导出」「render」「生成 MP4」等**，才执行：

```powershell
cd "<项目路径>"
npm run render
# 或指定输出：
npx hyperframes render -o "renders/项目名_v1.mp4"
```

导出文件默认在 `renders/` 目录。

## 禁止行为

- ❌ 项目刚建好就自动 `npm run render` / `npx hyperframes render`
- ❌ 未经用户确认就推送/上传视频
- ❌ 把 render 当作交付的默认最后一步
- ❌ 把 TTS / 时间轴 / check 留给用户自己跑（应 Agent 自动执行）
- ❌ 交付清单里列一堆终端命令让用户逐项执行

---

# 第十步：交付自检

### 环境
- [ ] hyperframes / hyperframes-cli / hyperframes-core / hyperframes-animation / hyperframes-creative 已安装（`npx hyperframes skills check` → current）？
- [ ] **`design-taste-frontend`（taste-skill）已安装且写 HTML 前已读**？
- [ ] **已读 `templates/anti-slop-motion-scheme.md`**？
- [ ] **hyperframes-animation / design-motion-principles / web-typography 已安装且写 HTML 前已读**？
- [ ] **已读 `templates/visual-style-guide.md` 并写 `design.md`（含 Motion Plan）**？
- [ ] **视觉风格名 + 首镜布局 + 片尾变体** 已在分镜表摘要中声明？
- [ ] FFmpeg 可用？
- [ ] Node.js >= 22？
- [ ] edge-tts 可用（中文配音）？
- [ ] 未误装 hyperframes-media 替代 Edge TTS？

### 内容
- [ ] 口播已按语义拆镜？
- [ ] 上屏文案未改核心事实？
- [ ] 每镜布局不同（连续两镜结构不重复）？
- [ ] 全片至少 **4 种**不同布局模式？
- [ ] **首镜不是**无理由的 `split-narration-visual`（除非用户指定或 Swiss Pulse 且已轮换）？
- [ ] 未使用 house-style 禁止项（cyan-on-dark 套、渐变字、左侧 accent 竖条）？
- [ ] 多 Skill 同镜：左右双卡 + **共享详情面板**（非纵向堆叠、非详情跟卡走）？
- [ ] Skill 英文名已用 `.skill-name` 凸显？
- [ ] 最后一个 Skill 与总结镜、片尾已**分镜**（场景号连续递增）？
- [ ] 总结镜四宫格在场景开头已入场（非等后半句口播才出现）？
- [ ] 钩子镜 `.t1` 已防换行（`white-space: nowrap`）？
- [ ] **已读 `scene-density-guide.md`，短镜有副信息 + `#root` 静态装饰（非空镜）**？
- [ ] **overline / chip 默认中文**（无 COMPACT 类装饰英文）？
- [ ] **`voice` 整句 TTS**；未为字幕宽度拆 s2a/s2b 式多 wav？
- [ ] **`subtitle` 为 `voice` 连续子串**（见 `subtitle-tts-guide.md` §1.1）；`generate-tts.py` 0 ERROR？
- [ ] **多音字/英文/专有名词已查，`speak` 已填或 notes 说明**？
- [ ] **每条底部字幕单行**（无 stupid 断句、无长期 ellipsis）？
- [ ] **同场景文字无重叠**（标题/卡片/金句/装饰互不遮挡）？
- [ ] **内容区 padding-bottom ≥ 180px**（字幕安全区，见 `hyperframes-zh-checklist.md`）？
- [ ] **中文字体：fonts/ + @font-face**，无 Google Fonts / PingFang / 微软雅黑？
- [ ] **已跑 `verify-delivery-checklist.py` → 0 ERROR**？
- [ ] **未使用 emoji/AI 表情包式插图**（见第十一步）？
- [ ] 总时长 >150s 时 TTS 已用 `+18%`？
- [ ] 已选配色方案？
- [ ] 用户是否提供【品牌片尾】块？未填则 `useDefaultOutro: false`
- [ ] 片尾口播全文是否已写入 `lines.json` 最后一镜并**完整 TTS 念出**？
- [ ] 正文末尾是否**未重复**片尾句？
- [ ] 片尾镜：变体 A/B/C 与 `design.md` 风格一致？GSAP 对齐片尾 TTS？
- [ ] 已跑 `apply-brand.mjs`，头像在 `assets/avatar.png`？
- [ ] 音轨为单条 `voiceover.wav`（无同轨多 segment 叠音）？
- [ ] 新建项目已从 `templates/scripts/` 复制四件套（含 `fallback-alignments.py`）？

### 音频
- [ ] TTS 配音已规划？
- [ ] 改口播后已重跑 `generate-tts.py` + `apply-audio-schedule.mjs`？
- [ ] 音频 `src` 带 `?v=textHash` 缓存破坏？
- [ ] 已试听关键句，口播与字幕一致（非仅看文字）？
- [ ] 无「表达DNA」等英文缩写口播（应用中文「表达基因」）？
- [ ] BGM 音量低于配音（0.2-0.4）？
- [ ] 用户未要求时不加 SFX？

### 画面
- [ ] 无左侧 accent-bar 竖条（除非用户要求）？
- [ ] **L0：`#root` 有静态 gradient/网格**（非每镜 infinite ambient）？
- [ ] **L1：每镜主内容有 stagger 入场**（非一出现全亮）？
- [ ] **L2：数字/并列项与 TTS 同步动效**（count-up / glow / 逐步亮）？
- [ ] **L3：kinetic 全片 2–4 处**，非泛滥？
- [ ] **L4：A 池 ≥3 种轮换 + 相邻不重复；可选 1 处 B 池**？
- [ ] **P0 video-composition + scene-density 已读；有数据镜已读 data-in-motion**？
- [ ] **P0 design-adherence 已对照 design.md（0 违规）**？
- [ ] **≥4 镜已跑 snapshot 快检（Agent 内部）**？
- [ ] **P1 未指定风格时是否 offer 了 design-picker（或用户已指定风格）**？
- [ ] **P1 L2/L3 是否查了 atomic rules；长片是否写 beat-direction**？
- [ ] **P2 motion.json / media-use SFX / registry 在触发条件下已处理**？
- [ ] **Post-audit（步骤 7c）已通过**？
- [ ] 分屏镜头：对侧无换行、无「空箭头」首帧闪现？
- [ ] **各镜布局留白充足，可见文字块 bounding box 不交叉重叠**？
- [ ] GSAP 目标元素用 `mt.set` 设初态（**禁止** CSS 持久 `opacity:0`，见第十一步）？
- [ ] 流程箭头与步骤 stagger 同步，未单独漏动画？
- [ ] `#root` / `#bgm` / `voiceover` 时长 = `meta.json.duration`？

### 转场
- [ ] 入场/出场动效已分配？
- [ ] 转场无叠字？

### 交付
- [ ] Agent 已自动执行：TTS（含 Edge 对齐）→ apply-audio-schedule → apply-brand（若有片尾）→ **`verify-delivery-checklist.py`（0 ERROR）** → **Post-audit** → `verify-index-encoding.py` → GSAP/SFX 对齐 → `npm run check` 通过？
- [ ] 已告知用户：**勿在 Studio 改中文**；改稿走 `lines.json` + 重跑 TTS？
- [ ] 用户交付清单**仅含** `npm run dev` 一条命令（不含 TTS/check 等）？
- [ ] 已告知用户 `npm run dev` 预览方式？
- [ ] **未**自动执行 render 导出 MP4？
- [ ] 等用户确认后再导出？

---

# 第十一步：常见踩坑与交付规范

> 以下规则来自实际项目反馈，**每次交付前必须核对**，避免重复犯错。  
> **完整复盘手册（可转发给接手人）：** **`templates/delivery-pitfalls.md`**

## 字幕样式（单行硬性规则）

> **中文项目完整规则（字体、贴底、安全区）：** 见 **`templates/hyperframes-zh-checklist.md` §二–三**。

- **禁止**底部字幕出现 **两行** 或 `<br>` 换行——每条 `.sl` **只占一行**
- **禁止**给字幕加边框、背景框、圆角容器（`.sub-bar` 不要用 `border` / `background` / `backdrop-filter`）
- 字幕用 **纯文字 + 深色 text-shadow** 保证在任意背景上可读
- 横屏 1920×1080 字幕字号 **≥ 44px**（推荐 56–60px）；竖屏 1080×1920 **≥ 52px**
- 字幕居中全宽，底部留白 40–56px；`.sub-bar` 内 **仅一条 `.sl` 可见**（opacity 切换，不同时叠两条）

**每条 `.sl` 必须有的 CSS：**

```css
.sub-bar { position:absolute; bottom:48px; left:0; width:1920px; display:flex; justify-content:center; align-items:center; padding:0 56px; box-sizing:border-box; }
.sub-bar.clip { top:auto !important; bottom:48px !important; left:0 !important; width:1920px !important; height:auto !important; }
.sub-bar .sl { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: calc(1920px - 112px); text-align: center; }
```

**HTML 结构（避免字幕偏左）：**

```html
<div class="sub-bar clip" id="s1a" data-start="0" data-duration="2.5" data-track-index="22">
  <span class="sl">字幕文案</span>
</div>
```

**文案侧：** 长句口播保持一条 `voice`；字幕超长用 `subtitle` 拆显示，**不要**拆 TTS id。横屏单条 **8–16 视觉单位**（竖屏 **7–12**）；每条 wav **3–6 条**为宜，详见 **`subtitle-tts-guide.md` §5.3**。

## 页面文字不重叠（硬性规则）

同一场景内，**任意时刻**可见的上屏文字块（`.t1` / `.t2` / 卡片标题 / 金句 / 流程步骤 / 详情面板）**不得互相遮挡或叠在同一区域**。

| 规则 | 说明 |
|------|------|
| **分区** | 标题区、内容区、字幕区三层分离；标题在上、卡片在中、字幕固定底栏 |
| **间距** | 相邻文字块垂直间距 **≥ 24px**（竖屏 ≥ 32px）；卡片 grid 用 `gap`，禁止负 margin 挤叠 |
| **Kinetic** | 逐字动画只在**预留空位**内播放；禁止 kinetic 字与静态标题 occupy 同一 baseline 区域 |
| **入场顺序** | 新块入场前，旧块已 `opacity:0` 或移到不冲突区域；**禁止**两条大标题同时全 opacity 叠在一起 |
| **交付前** | 每镜在 **场景起点、口播中段、口播末** 各截一帧，肉眼看无字叠字、无半字被挡 |

## 禁止 AI 风 emoji / 表情包式插图

**禁止**下列视觉（即使用户未明说也不要默认使用）：

- ❌ 大号 **Emoji 字符**当主视觉（🚀😱🔥💡 等堆在画面中央）
- ❌ **AI 生成风** 3D 卡通脸、塑料感人物、Meme 表情包图、「大厂发布会 PPT 小人」式插画
- ❌ 从图库拉的 **夸张表情贴纸**、圆角 blob  mascots
- ❌ 用 `<img>` 贴 emoji PNG / 表情包 GIF 当讲解配图

**允许替代：**

- ✅ **SVG** 线框图标、几何图形、网格/轨道/折线等数据可视化装饰
- ✅ 与内容相关的 **抽象 UI mock**（面板、代码块、指标条）
- ✅ 用户 **【品牌片尾】** 提供的真实 **头像** URL
- ✅ `hyperframes-animation`（CSS keyframe / GSAP）驱动的 **非 figurative** 背景动效（光晕、粒子、线条）

需要「情绪强调」时用 **排版 kinetic + 配色 + L2 pulse**，不要用表情包图。

## 动效与廉价感（硬性 — 详见 `anti-slop-motion-scheme.md`）

**廉价感来源：** 纯静态背景 + 元素一出现就全亮 + 口播念数字画面不动 + 全程同一 `y:30` 入场 + 硬切。

| 必须 | 禁止 |
|------|------|
| 每镜 L0 `#root` 静态装饰 | 纯 `#0a0a0a` 零装饰 |
| 可选 1 个 `#root` 慢循环 | 每镜 feTurbulence / scan-lines infinite |
| 每镜 L1 stagger | 全片同一 `from({ opacity:0, y:30 })` |
| 数字镜 L2 count-up / pulse | 口播报数画面静态 |
| 镜间 L4 转场轮换 | 全程硬切或无转场 |
| GSAP **`mt` 时间轴** | ScrollTrigger / scroll 监听 |
| 动效 **motivated**（design-motion-principles） | 为动而动、无 TTS 对齐的乱 tween |

交付前在 sc1 起点截帧：**背景非纯平黑**（有 gradient/网格）；**不要求**肉眼可见循环动画。

## 片尾时长

- **禁止**在最后一镜末尾做内容淡出 → 黑屏
- 总时长 = 最后一条字幕/TTS 结束时刻（`showEnd`），**不加额外 tail**
- `data-duration` 与 `meta.json` 的 `duration` 保持一致，误差 ≤ 0.5s
- **`#root` 与 `#bgm` 的 `data-duration` 必须等于 `schedule.totalDuration`**（HyperFrames `render` 按 `#root` 裁切；若短于口播会截断片尾）
- `apply-audio-schedule.mjs` 同步 `#root`/`#bgm` 时用 `id="root"` / `id="bgm"` 定位，**勿假设 `id` 是第一个属性**（Studio 可能插入 `data-hf-id` 在前）
- 同步后校验：`#root`、`#bgm`、`voiceover` 时长与 `meta.json.duration` 一致，否则 `npm run check` 前应报错
- 片尾画面保持最后一帧内容直到视频结束

## 移动端字号（上屏文案）

横屏 1920×1080 最低参考（**竖屏转横屏发布到抖音时，宁大勿小**）：

| 元素 | 最小字号 |
|------|---------|
| 主标题 `.t1` | 96px |
| 副标题 `.t2` / `.t3` | 76px |
| 正文 `.bd` | 40px |
| 底部字幕 `.sub-bar` | 56px（推荐 60px） |
| 卡片标题 | 38px |
| 卡片描述 | 32px |
| 标签/芯片 / 流程步骤 | 32px |

竖屏在以上基础 **+15%**。制作完成后用手机预览确认可读性。

## 分屏布局（左右结构）

左右分屏时**放大一侧可视化，必须检查对侧是否被挤换行**。

| 规则 | 说明 |
|------|------|
| **比例** | 默认左右 `flex: 1` 均分；单侧大图用 `max-width` 控制，**不要**只靠 `flex: 0.82 / 1.18` 硬挤 |
| **流程条** | `flex-wrap: nowrap` + `white-space: nowrap` + `flex-shrink: 0` |
| **放不下时** | 优先略收该镜流程步骤字号/内边距，或改竖向流程（步骤 ↓ 箭头 ↓ 步骤），**禁止**首帧就换行 |
| **交付前** | 每镜分屏在场景起点、口播中段各截一帧，确认无换行、无空白箭头 |

示例（Case2 流程三步单行）：

```css
#sc2 .flow { flex-wrap: nowrap; gap: 6px; }
#sc2 .flow-step { font-size: 34px; padding: 14px 18px; white-space: nowrap; flex-shrink: 0; }
.orbit-wrap { width: 540px; max-width: 100%; } /* 右侧大图上限，给左侧留宽 */
```

## GSAP 初态与流程箭头（防闪现）

HyperFrames 按时间轴 **seek** 到某一帧时，尚未播到的 `mt.from` 元素会保持 **CSS 默认样式**。若默认 `opacity: 1`，场景一出现就会闪现箭头、卡片等。

**必须遵守：**

1. **禁止**对 GSAP 动画目标元素在 CSS 中写持久 `opacity: 0`——HyperFrames 按帧 seek 时，内联样式可能被清掉，CSS 会盖住 GSAP，导致**整镜内容永远不显示**
2. 正确做法：`mt.set(…, { opacity: 0 }, sceneStart)` 隐藏 → `mt.fromTo(…, { opacity: 0 }, { opacity: 1, …})` 入场 → 场景结束前 `mt.set(…, { opacity: 1 }, sceneEnd)` **锁定可见**
3. **流程箭头** 与步骤同样用 `fromTo`，按「步骤 → 箭头 → 步骤」顺序，**禁止**首帧单独露出箭头
4. 不要只对 `.flow-step` 做 stagger 而漏掉 `.flow-arrow`

**错误示例（会导致 Case2 全黑）：**

```css
/* ❌ 不要这样 */
#sc2-tag, #sc2-t3 { opacity: 0; }
```

**正确示例：**

```javascript
mt.set("#sc2-tag, #sc2-fs1, #sc2-a1", { opacity: 0 }, s2);
mt.fromTo("#sc2-fs1", { opacity: 0 }, { opacity: 1, duration: 0.22 }, t);
mt.fromTo("#sc2-a1", { opacity: 0 }, { opacity: 1, duration: 0.16 }, t + 0.14);
mt.set("#sc2-tag, #sc2-fs1, #sc2-a1", { opacity: 1 }, sceneEnd);
```

## HyperFrames Studio 中文回写损坏（高频踩坑）

> **现象：** 有 TTS、无字幕/画面，或文字变成 `????`、`??????/div>`。  
> **主因：** Studio 在 `npm run dev` 运行时**回写** `index.html`，破坏 UTF-8 中文与 HTML 结构（插入 `data-hf-id`、标签断裂）。**不是** TTS / `lines.json` 问题。

### Agent 必须遵守

| 规则 | 说明 |
|------|------|
| **写 `index.html` 前** | 若用户已开 Studio，提示先 **Ctrl+C 停 `npm run dev`**，写完再启动预览 |
| **写入方式** | 用 **UTF-8** 落盘（Python `write_text(..., encoding="utf-8")` 或等价方式），交付前跑 `python scripts/verify-index-encoding.py` |
| **场景 clip** | 场景根节点只用 `class="clip"`（**不要** `class="clip scene"`），否则 `apply-audio-schedule.mjs` 可能匹配不到 `data-duration` |
| **禁止让用户** | 在 Studio 画布/属性面板**直接改中文**上屏文案或字幕 |

### 用户预览时

- 只 **播放检查**，文案改动走 `audio/lines.json` → 重跑 TTS 流水线
- 若已出现 `??`：停 dev → 由 Agent 重建 `index.html`（或 `git checkout index.html`）→ `verify-index-encoding.py` → `npm run check` → 再 `npm run dev`
- TTS 更新后 Studio **硬刷新**（Ctrl+Shift+R）；`voiceover.wav` 不用 `?v=` 查询串（否则 `hyperframes validate` 404）

### 损坏特征（`verify-index-encoding.py` 会检测）

- 中文整段消失，只剩 `??`
- 闭合标签变成 `/div&gt;` 或 `??/span>`
- `</script>` 后出现大量多余 `</div>`
- 文件含 `data-hf-id` 且 `lines.json` 样例汉字不在 HTML 中

## 预览启动日志（`npm run dev` 不必惊慌）

以下为 **警告或正常日志**，不是失败，**无需处理即可预览/导出**：

| 输出 | 含义 |
|------|------|
| `overlapping_gsap_tweens` | GSAP 两条动画在 0s 附近略重叠，不影响播放 |
| `composition_file_too_large` | 单 HTML 行数偏多，建议以后拆镜，当前可用 |
| `[Compiler] Fetched … Consolas` 重复 | 字体编译正常日志，不是 error |
| `No deterministic font mapping for: PingFang / Microsoft YaHei` | **ERROR 级** — 见 `hyperframes-zh-checklist.md` §一；加 `fonts/` + `@font-face`，删系统字体回退 |
| `Studio running http://localhost:3002` | 启动成功 |

只有 **error** 或 `validate` 报 console error 才需要修。

## 音效（用户未要求则不加）

- 用户明确说「不要叮声 / 不要特效音」时，**不添加** SFX 轨道
- 默认中文项目可只保留 **TTS + 低音量 BGM**，不主动加 card/highlight 音效

## 金句动效（kinetic typography）

- **禁止**固定加 N 处金句；必须 **逐镜分析文案**，只对真正需要强调的语义单元做 kinetic
- 判断标准：比喻/冲突/转折/核心结论词（如「许愿」「兼」「纸糊」），而非专有名词或普通信息词
- 全片 kinetic **通常 2–4 处**，宁少勿滥；信息型标题（如「Harness 安全护栏」）用普通入场即可
- 片尾总结用 **scale punch** 代替 kinetic

## 快节奏风格

用户未指定慢节奏时，默认 **快节奏短视频**：

| 参数 | 推荐值 |
|------|--------|
| 转场时长 `TR` | 0.24–0.28s |
| 元素入场 stagger | 0.08–0.12s |
| 字幕入场 | 0.12–0.16s |
| kinetic 逐字间隔 | 0.03–0.04s |

转场类型轮换：A 池 blur / push / zoom / crossfade；章节转折可插 1 处 B 池 radial / grid / blinds，避免全程同一效果。

## 音效可听性

- **禁止**全片只用 sine 波形「滴」声做转场；转场音可省略或改用噪声 sweep
- **必须**为功能卡/流程步骤/数据高亮单独规划强调音（card / step / highlight 三类）
- 程序化生成时用 `volume=2~3` 并加 fade
- HTML 中 SFX `data-volume` **≥ 0.6**；BGM 保持 0.2–0.3
- 功能卡入场 = `sfx_card`；边框 pulse / 结论 punch = `sfx_highlight`
- 交付前 **戴耳机试听** 功能强调音是否可感知

## 画面装饰

- **禁止**默认加左侧竖条装饰线（`.accent-bar`）；用户未明确要求时不使用
- 背景用网格/暗角/光晕即可，避免喧宾夺主的固定色条

## 主标题防换行

横屏钩子镜 `.t1` 若含英文 + 中文（如 `OpenClaw 不够聪明？`）：

- 加 `white-space: nowrap`
- 必要时略收字号（如 96px → 88px），**禁止**首帧标题被挤成两行

## 多 Skill 同镜布局（必守，禁止做错）

**适用：** 一镜内并列介绍 2 个 Skill（记忆双保险、生态扩展等）。

**正确结构（用户标注图）：**

```text
┌──────────────────────────────────────┐
│  Skill ① 卡片    │    Skill ② 卡片     │  ← 左右并排，两卡始终可见
├──────────────────────────────────────┤
│  【固定详情面板 — 同一位置切换内容】       │
│  讲到第一个 → 左卡高亮 + 面板显示介绍①   │
│  讲到第二个 → 右卡高亮 + 面板换成介绍②   │
└──────────────────────────────────────┘
```

**必须：**

1. 上方 `.duo` 左右两卡；Skill 英文名用 `.skill-name`（金色 JetBrains Mono）凸显
2. 下方 **单独** `.skill-detail-panel`；两套 `.skill-detail` 用 `position:absolute` 叠在同一区域，按 TTS **切换 opacity**，不要跟在各自卡片下面
3. 口播到第 N 个 Skill 的 `lines.json` 起点 → 高亮对应卡片 + 显示对应 detail；**禁止**第二个 detail 出现在第一个卡片下方或纵向堆叠整块 block

**GSAP 参考：**

```javascript
function setupSkillDuo(sceneNum, card1, card2, detail1, detail2, tFirst, tSecond) {
  const start = getScene(sceneNum).start;
  const dim = { opacity: 0.42, borderColor: "rgba(0,194,255,0.16)", boxShadow: "none" };
  const lit = { opacity: 1, borderColor: "rgba(0,194,255,0.88)", boxShadow: "0 0 36px rgba(0,136,255,0.42)" };
  mt.set(card1 + "," + card2, dim, start);
  mt.set(detail1 + "," + detail2, { opacity: 0 }, start);
  mt.set(card1, lit, tFirst);
  mt.fromTo(detail1, { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: 0.2 }, tFirst + 0.05);
  mt.set(card2, dim, tFirst);
  mt.set(card1, dim, tSecond);
  mt.set(detail1, { opacity: 0 }, tSecond);
  mt.set(card2, lit, tSecond);
  mt.fromTo(detail2, { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: 0.2 }, tSecond + 0.05);
}
```

**禁止：**

- ❌ 两 Skill 纵向堆叠，第二个 block 从下方滑入
- ❌ 详情区固定在画面最底部、与卡片无对应关系
- ❌ 两卡 + 两详情四块同时全亮、无选中态

## 场景编号与内容拆分

- **HTML 场景 id 按顺序递增**：`sc1`…`scN`，**不要**写死「Skill ⑥ 一定是 sc6、片尾一定是 sc7」
- **最后一个 Skill 专镜**（如 agent-browser）单独一镜，**不要**与「连招总结」挤在同一 sc
- **总结镜**（四宫格 / 连招回顾）独立成镜，口播从「这 N 个 Skill…」或「一套连招」开始
- **品牌片尾** = 最后一镜 `sc(N+1)` 或 `sc(N+2)`；片尾元素用 `outro-title` / `outro-follow` 等 id，`apply-brand.mjs` 与 GSAP 取 **schedule 中最大 scene 号**，勿硬编码 `sc7`
- `lines.json` 的 `scene` 与 HTML `id="scN"` **一一对应**

## 总结镜防空屏

总结镜（连招四宫格等）**禁止**等口播到「装上 A 和 B…」才首次出现卡片——否则上一句（如「这 6 个 Skill…」）期间只有 badge，画面空。

**必须：**

1. 场景切入后 **0.5s 内** 四宫格（或全部总结卡片）已 stagger 入场完毕
2. 后续口播逐条对应时，只对**已可见**的卡片做 scale 强调，不再负责首次出现
3. 底部金句 / CTA 仍可按 s42、s43 等较晚 TTS 入场

## 长句字幕拆分（显示层 — 详见 `subtitle-tts-guide.md`）

1. **`voice` 整句一条 wav** — 不因 20+ 字口播拆 TTS id
2. **`subtitle` / `subtitleParts`** 或脚本自动拆：每段 **`minHan ≤ visualUnits ≤ maxHan`**
3. 只在逗号/句号/完整子句处拆 **显示**；**禁止**拦腰断（如「含金量」中间）；**禁止**孤词碎条（§5.3）
4. 每条 wav **建议 3–6 条**字幕；>8 条须合并相邻短条
5. 多条 `.sl` 共享同一 wav 的 `[start, showEnd]`，GSAP 零间隔切换
6. `generate-tts.py` 校验 subtitle **0 ERROR**；voice 超长 WARN 可接受
7. 多音字/专有名词 → `speak` 按 id 填写

## 镜内防太空（详见 `scene-density-guide.md`）

- 口播只有 1–2 句的镜 **最常见 AI 丑感**：不是 slop 配色，而是 **画面空**
- 每镜 **至少 5 项**：`#root`/镜内静态装饰 + 主标题 + 副信息 + L1 stagger + 有意留白
- 口播短 → 上屏加 **overline / chip / ghost 词 / 侧栏 viz**（含义相关，非凑字）
- 交付前：每镜口播起点截帧，**>40% 无装饰/副信息** → 回炉

## 场景 clip 时长防重叠

`apply-audio-schedule.mjs` 写场景 `data-duration` 时：

```javascript
const sceneDur = Math.max(0.001, +(scene.end - scene.start).toFixed(3) - 0.001);
```

避免相邻场景 `end === next.start` 触发 lint `overlapping_clips_same_track`。

## 其他

- HyperFrames 编译时重复打印 JetBrains Mono 字体 fetch 日志是 **正常现象**，不是错误
- Windows 上 `npx hyperframes tts`（Kokoro）可能失败，中文项目默认 Edge TTS
- 同轨道相邻 audio clip 的 `data-duration` 需比实际文件短 **0.001s** 避免 lint 报重叠
