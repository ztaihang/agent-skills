# 反 AI 味 + 有质感动效 · 执行方案

> Agent 写 `index.html` **前必读**。与 `visual-style-guide.md`、`design.md` 配套使用。  
> 目标：**拒绝模板化 AI UI**，同时 **该动的地方必须有动效**，避免「静态 PPT 廉价感」。

---

## 一、Skill 栈（按顺序读）

| 顺序 | Skill / 文档 | 职责 |
|------|-------------|------|
| 1 | **本 skill** `SKILL.md` | 拆镜、流水线、交付 |
| 2 | **`design-taste-frontend`**（taste-skill） | 反 slop 门禁、排版纪律、pre-flight |
| 3 | **`hyperframes`** → `visual-styles.md` + `house-style.md` | 命名风格 preset、lazy defaults |
| 4 | **`css-animations`** | 背景 atmosphere 循环动效 |
| 5 | **`design-motion-principles`** | 入场 stagger、缓动、动效 audit |
| 6 | **`web-typography`** | 字号层级、字体配对 |
| 7 | **`visual-style-guide.md`** | 风格轮换、首镜/片尾、禁止清单 |
| 8 | **项目 `design.md`** | 本支视频唯一视觉真相 |

**硬门禁：** 无 `design.md` → 禁止写 `index.html`。  
**硬门禁：** 未读 taste-skill + 三前端 skill → 禁止写 `index.html`。

### taste-skill 安装

```bash
npx skills add leonxlnx/taste-skill@design-taste-frontend -g -y
```

检查：`Test-Path "$env:USERPROFILE\.agents\skills\design-taste-frontend\SKILL.md"`

### HyperFrames 专用 override（读 taste-skill 后必须遵守）

taste-skill 面向 landing page + ScrollTrigger；**短视频成片不同**：

| taste-skill 默认 | HyperFrames 短视频 |
|-----------------|-------------------|
| ScrollTrigger / scroll hijack | **禁止** — 只用 GSAP **主时间轴 `mt`** |
| `window.addEventListener('scroll')` | **禁止** |
| 玻璃拟态 everywhere | 仅当 `design.md` 明确 `surface: glass` 且非默认 |
| 居中 hero 当首镜 | 首镜布局见 `visual-style-guide.md` §4 |
| MOTION 10 级花哨 | 见下方 **默认 dial** |

**短视频默认 dial（用户未覆盖时写入 `design.md`）：**

```yaml
tasteDials:
  DESIGN_VARIANCE: 5    # 解说视频：结构清晰，不过度 asymmetric
  MOTION_INTENSITY: 6   # 有入场/ambient/数据动效，非 scroll 炫技
  VISUAL_DENSITY: 6     # 信息型口播，中等密度
```

用户可在提示词写：`DESIGN_VARIANCE 7` 等覆盖。

---

## 二、反 AI 味 · 五道门禁

### 门禁 1 · 视觉决策（步骤 3b）

产出 **`design.md`** + 分镜摘要字段：

- `styleName` — visual-styles 预设名
- `openingLayout` — 首镜布局（非默认 split+地球）
- `outroVariant` — a | b | c
- `tasteDials` — 三 dial
- `differentiatorsFromLast` — 与上支至少 3 项不同

可选维护 `assets/style-history.json`（见 `style-history.json.example`）。

### 门禁 2 · Pre-flight（写 HTML 前，Agent 自检）

**taste-skill §4 + house-style lazy defaults + visual-style-guide §7：**

- [ ] `design.md` 存在，YAML 完整，色值仅来自 preset
- [ ] 未计划：cyan-on-dark 套、紫蓝渐变字、左侧 accent 竖条、同质 2×2 玻璃卡
- [ ] 首镜不是无理由 `split-narration-visual` + 线框地球
- [ ] 字体非「Inter + 无理由」— 有 headline/body 配对（web-typography）
- [ ] 片尾变体与风格表一致
- [ ] **动效计划**已写进 `design.md` §Motion Plan（见第三节）

任一项不通过 → 回到门禁 1，**不得**开写 HTML。

### 门禁 3 · 写 HTML（按 design，禁止肌肉记忆）

- 所有 hex / font / radius 来自 `design.md`
- 布局材质由 `design.md` 的 `surface` 定（`solid` | `outline` | `glass`），**默认 solid 或 outline，非 glass**
- 装饰用 SVG / 几何 / 数据 viz，**禁止** emoji 主视觉、AI 3D 小人

### 门禁 4 · Post-audit（`npm run check` 前）

**design-motion-principles Audit 思维** + 廉价感检查：

- [ ] 每镜背景有 **≥1 层 ambient 循环**（非纯静态 `#0a0a0a`）
- [ ] 主内容有 **入场 stagger**（非全片同一 `opacity:0,y:30`）
- [ ] 数据/数字镜有 **count-up 或高亮 pulse**（对齐 TTS）
- [ ] 场景转场 **≥2 种** rotate（blur / push / zoom / focus，非全程同一效果）
- [ ] kinetic 全片 **2–4 处**，非每句都 bounce
- [ ] 无未在 `design.md` 声明的 lazy 色（`#06b6d4` `#7c3aed` `#3b82f6` 等）

不通过 → 补动效或改配色 → 再 check。

### 门禁 5 · 交付摘要

分镜表必须声明：

```text
风格: Shadow Cut | 首镜: full-bleed-statement | 片尾: variant-b
taste dial: 5/6/6 | design.md: ✓ | 动效层级: L0–L3 已覆盖
与上支差异: 风格+首镜+ambient
```

---

## 三、有质感动效 · 四层模型（拒绝廉价静态 PPT）

> **原则：** 动效必须 **motivated**（服务层级 / 叙事 / 数据强调 / 转场），不是「有 GSAP 就乱 tween」。  
> **原则：** **背景永远要有生命感**；**内容入场要有节奏**；**讲到数字就要动数字**。

### L0 · 环境层（每镜必做 — 防「死画面」）

| 元素 | 做法 | 参考 |
|------|------|------|
| 背景 atmosphere | 2–5 个装饰层，**共享一种** slow ambient（breath / drift / pulse） | css-animations |
| 实现 | GSAP `mt` 循环 tween 或 CSS `@keyframes` + `animation-play-state` | hyperframes seek 友好 |
| 禁止 | 纯 flat 背景无任何 slow motion | — |

**最低标准：** 每镜至少 **1 个** ambient 循环 + **1 个** 静态装饰（网格/暗角/ghost text）。

### L1 · 场景入场（每镜必做 — 防「一出现就全摆好」）

| 元素 | 做法 | 时长 |
|------|------|------|
| 标题 / 标签 | `mt.fromTo` stagger 0.08–0.12s | 0.2–0.35s each |
| 卡片 / 列表 | 步骤 → 箭头 → 步骤（**箭头也要 animate**） | 同 stagger |
| 初态 | `mt.set(..., { opacity: 0 }, sceneStart)` — **禁止 CSS 持久 opacity:0** | SKILL 第十一步 |

**最低标准：** 场景切入后 **0.5s 内** 主内容 stagger 完毕（总结镜四宫格同理）。

### L2 · 语义强调（按 TTS 对齐 — 防「口播在动画面不动」）

| 触发 | 动效 | 对齐 |
|------|------|------|
| 口播到 **数字/百分比** | count-up、`scale` punch、accent 色 flash | `schedule.json` 该条 `start` |
| 口播到 **并列项 N** | 第 N 卡 border glow / scale 1.04 | 对应 line `start` |
| 口播到 **转折/结论** | 可选 `sfx_highlight` + 边框 pulse | 同 start |
| 流程步骤 | 逐步点亮 + `sfx_step` stagger | 逐步 +0.1s |

**最低标准：** 含 **≥2 个数字/指标** 的视频，至少 **1 镜** 有 count-up；含 **≥3 并列项** 的镜，逐步高亮与口播同步。

### L3 · 精选强调（全片 2–4 处 — 防 kinetic 泛滥）

| 适用 | 动效 | 禁止 |
|------|------|------|
| 钩子/冲突/金句 | kinetic typography 逐字 | 专有名词、普通信息词 |
| 片尾 slogan | scale punch（变体 A/B） | 每镜都做 kinetic |

### L4 · 转场（镜间 — 防「硬切廉价感」）

| 参数 | 推荐 |
|------|------|
| 时长 `TR` | 0.24–0.28s（快节奏默认） |
| 类型 | blur / push / focus pull / zoom **轮换**，禁止全程同一效果 |
| 音效 | 默认可省略；用户要求再加 |

**最低标准：** 全片 **≥2 种** 转场类型；相邻两镜转场类型不重复（除首镜入场）。

---

## 四、动效计划模板（写入 `design.md` §Motion Plan）

Agent 在写 HTML 前填写：

```markdown
## Motion Plan

- L0 ambient: particle-field + radial-glow（共享 sine 8s breath）
- L1 首镜: title stagger 0.1s + 副标题 delay 0.15s
- L2 sc3: 指标 47% count-up @ schedule s17.start；四卡逐步 glow @ s18/s19
- L3 kinetic: sc1 钩子「纸糊」@ s3；sc5 结论 @ s42
- L4 转场: sc1→2 push, sc2→3 blur, sc3→4 zoom, …
- 禁止: 全片 y:30 同一 ease；禁止无 ambient 纯黑底
```

---

## 五、拒绝 vs 必须 · 对照表

| ❌ 拒绝（AI 味 / 廉价） | ✅ 必须（有质感） |
|------------------------|------------------|
| cyan-on-dark + 玻璃 2×2 默认 | `design.md` preset + solid/outline 卡 |
| 线框地球首镜复制粘贴 | 首镜按风格表轮换布局 |
| 纯黑底零装饰 | L0 ambient 每层都有 |
| 一出现全部元素 visibility:1 | L1 stagger 入场 |
| 口播念数字画面静态 | L2 count-up / pulse 对齐 TTS |
| 每句 kinetic bounce | L3 全片 2–4 处 |
| 全程硬切 | L4 转场轮换 |
| ScrollTrigger / scroll 动画 | 仅 `mt` 时间轴 |
| Inter + 渐变字当唯一识别 | web-typography 字体配对 |

---

## 六、与上支错开（频道级）

维护 `assets/style-history.json`（可选）：

```json
{
  "lastStyle": "Data Drift",
  "lastOpeningLayout": "split-narration-visual",
  "lastOutroVariant": "a",
  "lastTransitionSet": ["blur", "blur", "blur"]
}
```

新视频交付后 Agent 更新；下一支 **至少 3 项** 与 history 不同。

无 history 时：用项目文件夹名 hash 轮换（见 `visual-style-guide.md` §3B）。

---

## 七、交付前 30 秒快检

1. 暂停在 sc1 起点 — 背景是否在 **缓慢动**？
2. sc1 切入 0.3s — 标题是否 **刚入场**，非全亮？
3. 任一数字镜 — 数字是否 **随口的** count / highlight？
4. 随机两镜衔接 — 转场是否 **不同**？
5. 全片截图 — 是否还能认出「又是那套科技蓝玻璃」？

五项任一失败 → 回到门禁 4。
