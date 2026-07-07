# HyperFrames 中文短视频 · 交付避坑清单

> **何时读：** 开项前通读；改背景/字幕/布局后复查；交付前与 `hyperframes-zh-checklist.md` 一起勾选。  
> **来源：** `claude-codex-pipeline` 项目复盘（2026-07）。  
> **适用：** 1920×1080 横屏口播解说类（本 Skill 默认工作流）。

---

## 一句话结论

这类项目最容易翻车的不是「镜头不会做」，而是：

**视觉层（背景 / 卡片 / 布局）和音频层（TTS / WordBoundary / 字幕）两套系统没有联动修改、联动验收。**

改了一处忘了另一处，用户预览时就会集中爆雷。

---

## 开项前必须确认的 5 件事

在写第一行 HTML 之前，向需求方或自己确认：

| # | 确认项 | 说明 |
|---|--------|------|
| 1 | **背景参考哪个项目？** | 有参考项目就抄它的完整背景栈（光晕 + 网格 + sweep），不要只抄一个渐变色值 |
| 2 | **要不要水印 / ghost-word？** | 默认不要；若要加，必须落在安全区内 |
| 3 | **字幕区留多高？** | 横屏建议 `safe-bottom ≥ 280px`，底部字幕不要被画面元素挡住 |
| 4 | **四边安全区多少？** | 建议 `safe-x ≥ 100px`，`safe-top ≥ 96px`，防手机裁切 |
| 5 | **TTS 与字幕断句方案** | 一条 `lines.json` 行 = 一条 wav；显示层用 `subtitleParts` 拆，不拆 wav |

---

## 数据流（必背）

```
audio/lines.json          ← 手写口播稿 + subtitleParts（显示断句）
        ↓
python scripts/generate-tts.py
        ↓
audio/schedule.json       ← 每镜时间轴 + subtitleParts
audio/alignments.json     ← Edge WordBoundary 逐条对齐（关键！）
        ↓
python scripts/build-index.py   ← 生成场景 HTML + 占位字幕
        ↓
node scripts/apply-audio-schedule.mjs   ← 写入真实字幕时间 + GSAP
        ↓
index.html（可 npm run dev 预览）
```

**记住：`apply-audio-schedule.mjs` 读的是 `schedule.json` + `alignments.json`，不是直接读 `lines.json`。**

改 `lines.json` 的 `subtitleParts` 后，必须同步 `schedule.json`（重跑 `generate-tts.py` 或手动改 schedule），并保证 `alignments.json` 条数一致。

---

## 我们犯过的错（按类别）

### 1. 布局与安全区

| 问题 | 表现 | 根因 |
|------|------|------|
| 内容贴四边 | 手机端裁切 | 未预设 safe 变量，元素默认顶满画布 |
| 镜身偏上、中下空 | sc7 / sc10 / sc11 不和谐 | 全程 `justify-content: center`，没为字幕区留垂直空间 |
| 卡片互相压字 | sc5 MCP Bridge 重叠、卡片溢出 | 三列宽度未控、中间连接器用竖排文字 |
| 动画隐藏了内容 | sc10 两张推荐卡完全不显示 | 父容器 `#sc10-duo` 被 `opacity:0`，子元素继承不可见 |
| 标题被裁切 | sc10「物理隔离」显示一半 | `white-space:nowrap` + 卡片 `overflow:hidden` + 宽度过窄 |

**正确做法：**

- 信息密集镜用 `balanced lower`（内容略靠上，但底部给字幕留白）
- 卡片标题默认允许换行，或 HTML 主动拆两行
- **永远不要把 `opacity:0` 设在包住多个子元素的父级上**；应对每个子元素单独做 stagger
- 中间连接区（如「+」「组合使用」）单独留 `min-width`，与两侧卡片保持 `gap`

---

### 2. 背景与配色

| 问题 | 表现 | 根因 |
|------|------|------|
| 背景太暗 / 太平 | 和用户其他项目观感不一致 | 只写了 design.md 色值，没对齐参考项目的多层氛围 |
| 换背景后卡片刺眼 | 深灰卡片 + 暖米白底 = 违和 | 只改了 `#root`，没同步改 `--text` / `--card-bg` / 字幕色 |
| 水印挡画面 | ghost-word 溢出、lint 报错 | 装饰大字未纳入安全区，也未按需求关闭 |

**正确做法：**

- 背景定稿 = **整包复制**参考项目的：`root-atmosphere` + `root-grid` + `root-sweep` + 底色渐变
- **背景一变，立刻改全套 surface 变量**：正文色、卡片底、chip、字幕色、成功/警告色
- 字幕在浅色背景上用深字 + 暖色光晕，不要用白字黑影那套深色主题方案
- 用户说不要水印 → 删除所有 `ghost-word` / `scene-deco`

---

### 3. 字幕与 TTS（最严重）

| 问题 | 表现 | 根因 |
|------|------|------|
| 「合并」显示成「合」 | sc6 最后一行缺字 | 为压 16 字宽上限，硬截断最后一行 |
| 只有某一镜字幕和口播不同步 | 其他镜正常 | 改了 `subtitleParts` 条数，`alignments.json` 条数未更新 |
| 改了 lines.json 但预览没变 | schedule 未同步 | 只改了 `lines.json`，没更新 `schedule.json` / 没重跑对齐 |

**机制（必懂）：**

`apply-audio-schedule.mjs` 里：

```js
if (row.parts.length !== parts.length) return null;  // 放弃 WordBoundary
```

条数对不上 → 退回**字数比例估算** → 只有那一镜字幕飘移。

**字幕断句规则：**

- 单行 ≤ 16 视觉单位（汉字 1，英文约 0.55）
- **禁止**为省宽度截断词语（如「合并」→「合」）
- **禁止**行尾悬空单字（如「并」）
- 应拆成多行，而不是截断

**改字幕后的标准命令：**

```powershell
# 只改了显示断句、未改 speak / 未重录 TTS
python scripts/realign-line.py s6          # 把 s6 换成对应 line id
node scripts/apply-audio-schedule.mjs

# 改了 speak、voice 或需要重录
python scripts/generate-tts.py
node scripts/apply-audio-schedule.mjs
```

**改完必查：**

```text
alignments.json 里该 id 的 parts.length == lines.json 里 subtitleParts.length
```

---

### 4. 流程与验证

| 问题 | 表现 | 根因 |
|------|------|------|
| 改了生成器用户仍看到旧版 | 漏跑流水线 | 只改了 `build-index.py`，没跑 `apply-audio-schedule` |
| snapshot 看不出问题镜 | 均匀抽帧，没对准口播时间 | 应按 `schedule.json` 的 `start` 定点截图 |
| contrast 警告被忽略 | 暖底 + 白字几乎不可读 | 换背景后没重新 `npm run check` |

**每次改完的最小闭环：**

```powershell
cd <项目目录>
python scripts/build-index.py          # 若用生成器
node scripts/apply-audio-schedule.mjs
node scripts/apply-brand.mjs          # 若有品牌
python scripts/verify-index-encoding.py
npm run check
```

**建议定点截图的镜号：**

- 首镜 sc1（双卡对比）
- 信息密集镜：sc5 / sc7 / sc9 / sc10 / sc11
- 片尾

```powershell
# 时间取 schedule.json 里该 scene 的 start + 2~3 秒
npx hyperframes snapshot --at 48 --frames 1
```

---

## 交付前自检表（打印勾选）

### 视觉

- [ ] 四边内容距画布边缘 ≥ 安全区，手机不裁切
- [ ] 字幕区（底部约 280px）无画面元素遮挡
- [ ] 背景、卡片、正文、字幕属于**同一套**色系
- [ ] 无 ghost-word / 水印（除非需求明确要求）
- [ ] 长标题在卡片内完整可见（无 `nowrap` 裁切）

### 字幕 / 音频

- [ ] 每条字幕语义完整，无截词（合并、通过等）
- [ ] `alignments.json` 每行 `parts.length` == `subtitleParts.length`
- [ ] 抽查 1~2 镜：字幕出现时间与口播一致（尤其改过断句的镜）
- [ ] `npm run check` 无 error（contrast 警告尽量处理）

### 动画

- [ ] 无父级 `opacity:0` 导致子元素整组不显示
- [ ] GSAP 目标 id 与 HTML 实际 id 一致（重构 HTML 后必查）

### 流水线

- [ ] `build-index` → `apply-audio-schedule` 已跑
- [ ] 用户侧只需 `npm run dev`，**不要擅自 render MP4**（除非用户明确要求）

---

## 常见修复速查

| 现象 | 先查什么 | 怎么修 |
|------|----------|--------|
| 某一镜字幕和口播对不上 | `alignments.json` 该 id 的 parts 条数 | `python scripts/realign-line.py <id>` 后重跑 apply |
| 字幕缺字 | `lines.json` subtitleParts 最后一行 | 拆行，不要截断 |
| 卡片文字被切 | `.cy-card` 的 `overflow` / `nowrap` / `max-width` | 换行或缩小字号或加宽卡片 |
| 中间「+」和卡片贴太紧 | `.rec-duo` gap、`.rec-link` min-width | 加大 gap 和中间列宽度 |
| 按钮压字幕 | `safe-bottom`、镜身 `padding-bottom` | 加大底部留白或上移内容 |
| 暖底上卡片发黑难受 | `:root` 变量是否仍是深色主题 | 换 surface 浅色变量全套 |

---

## 项目内关键文件

| 文件 | 作用 |
|------|------|
| `audio/lines.json` | 口播稿 + 手写 subtitleParts |
| `audio/schedule.json` | 时间轴（apply 的数据源之一） |
| `audio/alignments.json` | WordBoundary 对齐（apply 的数据源之二） |
| `scripts/generate-tts.py` | 全量 TTS + schedule + alignments |
| `scripts/realign-line.py` | 单条 line 重拉 WordBoundary（改断句后用） |
| `scripts/apply-audio-schedule.mjs` | 字幕时间 + GSAP 写入 |
| `scripts/verify-delivery-checklist.py` | 交付自检脚本 |
| `design.md` | 视觉规范（有参考项目时以实机参考为准） |

---

## 给 Agent 的硬性指令（可复制到 prompt）

```
1. 开项先确认：背景参考项目、是否水印、安全区尺寸。
2. 背景定稿必须包含 atmosphere + grid + sweep；改背景必须同步改卡片/文字/字幕色。
3. 字幕禁止截词；超宽就拆 subtitleParts，不要截断。
4. 改 subtitleParts 条数后必须 realign-line 或 generate-tts，再 apply-audio-schedule。
5. 动画禁止对包住多子的父级设 opacity:0。
6. 交付前跑完整流水线 + npm run check；关键镜按 schedule 时间点 snapshot。
7. 不要自动 render MP4，除非用户明确要求。
```

---

## 与现有模板文档关系

| 文档 | 分工 |
|------|------|
| `subtitle-tts-guide.md` | voice/subtitle 分离、speak、断句规则 |
| `hyperframes-zh-checklist.md` | 字体、字幕 CSS、背景、生成后自检 |
| `scene-density-guide.md` | 镜内密度、防空镜 |
| **本文件** | **跨镜复盘、数据流、对齐机制、给人看的避坑手册** |

---

*文档版本：v1.0 · 基于 claude-codex-pipeline 复盘整理*
