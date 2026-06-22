# 中文 HyperFrames 短视频 · 交付自检清单（Agent 必读）

> **何时读：** 写 `index.html` / `build-index.py` **前**通读一遍；**全部流水线跑完后**再逐项自检。  
> **配套脚本：** `python scripts/verify-delivery-checklist.py`（ERROR 必须修到 0 再交付）。

---

## 一、写 HTML 前（字体与 design.md）

| # | 规则 | 说明 |
|---|------|------|
| F1 | **中文上屏 + 字幕** | 默认 **Noto Sans SC**（本地 `fonts/*.woff2` + HTML 内 `@font-face`） |
| F2 | **禁止外链字体** | 不得 `<link href="fonts.googleapis.com">` / `@import url(...google...)` |
| F3 | **禁止系统字体回退** | 不得 `PingFang SC` / `Microsoft YaHei` / `微软雅黑` / `SimHei` / `Helvetica` 作中文回退 |
| F4 | **Compiler 可解析** | 自定义字体名必须在 HTML 有 `@font-face { src: url("fonts/...woff2") }`；否则 dev 会 WARN 并可能卡住 |
| F5 | **Skill 英文名** | `.skill-name` 可用 **JetBrains Mono**（HyperFrames 内置映射） |
| F6 | **design.md 落地** | `typography` / `rounded` / `surface` 须写进 CSS，不能只有 YAML 不实现 |

**推荐字体文件（fontsource 简体子集，复制到项目 `fonts/`）：**

- `noto-sans-sc-chinese-simplified-{400,500,600,700}-normal.woff2`
- 标题若用 Serif：另加 `noto-serif-sc-chinese-simplified-{500,600,700}-normal.woff2`

---

## 二、字幕（`.sub-bar` / `.sl`）

| # | 规则 | CSS / 结构 |
|---|------|------------|
| S1 | **永远单行** | `.sub-text` 或 `.sl`：`white-space: nowrap; overflow: hidden; text-overflow: ellipsis` |
| S1b | **HTML 结构** | `<div class="sub-bar clip" id="…"><span class="sl">文案</span></div>` — **clip 在外层**，文字在 `span` 内，避免 Studio 把 clip 缩成文字宽导致偏左 |
| S1c | **全宽居中** | `.sub-bar.clip { width:1920px; display:flex; justify-content:center }` |
| S2 | **贴底** | `.sub-bar`：`bottom: 28px` ~ `48px`（横屏推荐 28–36px） |
| S3 | **纯字 + 描边** | 禁止字幕容器 `border` / `background` / `backdrop-filter` |
| S4 | **弹幕可读** | `font-weight: 700`；`text-shadow` 双层黑色描边 + 轻外晕 |
| S5 | **字号** | 横屏 ≥ 56px（推荐 60px）；竖屏 ≥ 52px |
| S6 | **与口播同步** | 字幕 = `voice` **连续子串**（§1.1）；一条 wav 可多条 `.sl`；改 voice/speak/subtitle **必**重跑 TTS 三件套 |

**上屏副信息（overline / chip）：** 默认 **中文**；英文仅限产品名、Skill 名、口播必须术语。禁止 `COMPACT` / `PAIN POINT` 等装饰英文标签（见 `scene-density-guide.md`）。

---

## 三、布局 · 防重叠

| # | 规则 | 说明 |
|---|------|------|
| L1 | **三层分区** | 标题区（上）→ 内容区（中）→ 字幕区（底），互不占用 |
| L2 | **字幕安全区** | `.scene-content` / `.split` 的 `padding-bottom` **≥ 180px**（横屏 1920×1080） |
| L3 | **底栏禁占** | 对比条、步骤条、大数字卡 **不得**放在画面最底 200px 内（易与字幕叠） |
| L4 | **竖屏** | 字幕安全区 `padding-bottom` **≥ 220px** |
| L5 | **交付截帧** | 每镜 **起点 / 口播中 / 口播末** 各看一眼：无字压字、无字幕挡主视觉 |

---

## 四、背景 · 反「死黑 PPT」

| # | 规则 | 说明 |
|---|------|------|
| B1 | **禁止纯平黑** | `#root` 不得只有 `#0a0a0a` / `#000`，须有多层 gradient / 光晕 / mesh |
| B2 | **L0 背景（静态优先）** | `#root`：gradient + 网格/暗角（**静态即可**）；**禁止**每镜 `.ambient` + CSS `infinite` |
| B2b | **可选动效** | 全片最多 **1 个** `#root` 慢循环；或 GSAP 切镜时 pause 非当前镜 ambient |
| B2c | **禁止** | `feTurbulence` + `infinite`；每镜 scan-lines/grain 复制 |
| B3 | **风格一致** | 装饰色来自 `design.md` accent，禁止 lazy default：cyan-on-dark、紫蓝渐变字 |
| B4 | **可见性质** | sc1 起点截帧：背景非纯平黑（有 gradient/grid）；**不强制**肉眼可见循环动画 |

---

## 五、组件 · 反「方方正正 AI 框」

| # | 规则 | 说明 |
|---|------|------|
| C1 | **圆角落地** | 卡片 / 列表 / chip 使用 `design.md` 的 `rounded`；中文解说推荐 **14–28px**，chip 用 **pill** |
| C2 | **层次** | 面板用轻渐变底 + 内高光 + 软阴影，避免「1px 硬框 + 直角 + 纯透明底」 |
| C3 | **禁止** | 全片同一 2×2 玻璃卡、左侧 accent 竖条、无理由 uppercase 细 Inter |
| C4 | **Velvet 注意** | 预设 `rounded: 0px` 是风格起点；**中文口播向用户交付时**应适度圆角，避免监控 UI 感 |

---

## 六、生成完毕 · Agent 强制自检（按顺序）

**全部改完并跑完 TTS → align-subtitles → apply-audio-schedule 之后，Agent 必须：**

```powershell
cd "<项目路径>"
python scripts/verify-delivery-checklist.py
python scripts/verify-index-encoding.py
npm run check
```

| 步骤 | 动作 | 通过标准 |
|------|------|----------|
| 1 | `verify-delivery-checklist.py` | **0 ERROR**；WARN 须读清单判断是否改 |
| 2 | `verify-index-encoding.py` | exit 0 |
| 3 | `npm run check` | lint/validate **0 error**；inspect 布局 **0 issue** |
| 4 | **人工清单** | 本节下方「交付前 30 秒」全部打勾 |
| 5 | 交付用户 | 只给 `npm run dev`；**未确认不 render** |

### 交付前 30 秒（Agent 必须逐项确认）

- [ ] 无 Compiler 字体映射 WARN（Microsoft YaHei / PingFang 等）
- [ ] 字幕在画面最底，未挡 21→1 类对比条/大数字
- [ ] 首镜列表/卡片非直角盒堆砌（有圆角或层次）
- [ ] 背景非死黑（`#root` 有 gradient/网格；勿每镜 infinite ambient）
- [ ] 中文在浏览器/inspect 中无 `??`、无裁切 ellipsis 长期遮挡
- [ ] 关键句口播与字幕一致（至少 spot-check 2 条）

**任一项 FAIL：** 回到 `build-index.py` / CSS 修改 → 重新 `build-index.py` → **align-subtitles**（若 TTS 变了）→ apply-audio-schedule → 再从步骤 1 跑。

---

## 七、常见问题 → 修法

| 现象 | 根因 | 修法 |
|------|------|------|
| dev 卡住 + 字体 WARN | 系统字体 / Google Fonts | 本地 `@font-face` + 删回退 |
| 字幕挡画面 | 内容区太低 / padding-bottom 不足 | 提高安全区或上移对比组件 |
| 背景仍像黑屏 | 只有 flat 色、无 gradient | 加 `#root` gradient + 网格/暗角（静态） |
| 长句字幕偏快/偏慢 / 字与口播不一致 | subtitle 缩写改写、alignments 过期、或用了 fallback 权重 | 改 lines.json 为 voice 子串 + 手写 subtitleParts → 重跑 TTS → align（或 fallback）→ apply → **听检** |
| 字幕 orphan（如单独「层级」） | 未手写 subtitleParts，自动按宽度切字 | lines.json 补语义断点（如「清晰的七个层级」） |
| TTS 数字处怪停顿 | speak 写「十三 个」带空格 | speak 连写「十三个」；脚本已 normalize_speak |
| align-subtitles 崩溃 (Windows) | faster-whisper 进程异常 | `python scripts/fallback-alignments.py` → apply → 听检 |
| preview CPU 高 | 每镜 `.ambient` + CSS infinite / feTurbulence grain | 删 per-scene ambient；保留 `#root` 静态装饰 |
| 全是方框 | 未实现 design.md rounded | 统一 `--r-md` / pill chip |
| inspect clipped_text | 字幕 line-height 过小 | `min-height` + `line-height ≥ 1.3` |

---

## 八、与现有文档关系

| 文档 | 分工 |
|------|------|
| `subtitle-tts-guide.md` | voice/subtitle 分离、speak、标点 |
| `scene-density-guide.md` | 镜内密度、防空镜 |
| `anti-slop-motion-scheme.md` | L0–L4 动效门禁 |
| `visual-style-guide.md` | 风格轮换、禁止纯黑 |
| **本文件** | **中文落地 + 字体 + 字幕区 + 生成后自检** |
