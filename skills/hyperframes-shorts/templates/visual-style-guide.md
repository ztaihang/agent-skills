# 视觉差异化指南（Agent 写 HTML 前必读）

> 目标：**每支视频的配色、背景装饰、动效气质、首镜布局、片尾结构都应不同**，禁止套同一套「科技蓝 + 玻璃卡 + split 左文右图」。

---

## 1. 写 HTML 前必须读取

| 顺序 | 来源 | 用途 |
|------|------|------|
| 1 | **`hyperframes` → `visual-styles.md`** | 选命名风格预设（YAML tokens） |
| 2 | **`hyperframes` → `house-style.md`** | 避免 AI 味 lazy defaults（cyan-on-dark、渐变字等） |
| 3 | **`css-animations`** skill | 背景 shimmer / glow / grain 等装饰动效 |
| 4 | **`design-motion-principles`** skill | 入场节奏、缓动、stagger，避免抖动同质化 |
| 5 | **`web-typography`** skill | 竖屏/横屏字号层级、行高、可读性 |
| 6 | **本文件** | 选风格、写 `design.md`、排布局、选片尾变体 |

**禁止**在未读上述文件的情况下直接写 `index.html`。

---

## 2. 必须产出 `design.md`

每个新项目根目录**必须**有 `design.md`（可从 `templates/design.md.example` 改）：

1. 从 `visual-styles.md` 选 **1 套命名风格**（见下表）
2. 把该风格的 YAML token 块复制进 `design.md` front matter
3. 补全 Overview / Colors / Typography / Motion / Do's and Don'ts  prose
4. 写 HTML 时**只引用 `design.md` 的 token**，禁止临时发明第二套配色

交付分镜表摘要须写明：**视觉风格名**（如 `Data Drift`）、**首镜布局**、**片尾变体**（A/B/C）。

---

## 3. 风格怎么选

### 用户指定了「风格：…」

按用户描述匹配 `visual-styles.md` 最近的一套；可微调 accent，但**不得**换整套气质。

### 用户未指定

**两步走（都必须做）：**

**A. 按口播内容选 mood（优先）**

| 口播气质 | 推荐风格 |
|---------|---------|
| 数据、指标、对比、教程步骤 | **Swiss Pulse** |
| AI / ML / 前沿技术 / 未来感 | **Data Drift** |
| 突发新闻、安全、硬核、批判 | **Deconstructed** 或 **Shadow Cut** |
| 大发布、里程碑、强情绪 | **Maximalist Type** |
| 企业级、投资、高端叙事 | **Velvet Standard** |
| 人物故事、品牌温度（少见） | **Soft Signal** |

**B. 与同系列上一支错开（强制）**

若无法得知上一支用了什么风格，用 **项目文件夹名** 做确定性轮换，避免 Agent 每次都选 Data Drift：

```text
预设池（科技财经常用）：
  Swiss Pulse | Data Drift | Deconstructed | Shadow Cut | Velvet Standard | Maximalist Type

索引 = (项目文件夹名每个字符 charCode 之和) mod 6
→ 取预设池[索引] 作为默认候选

若 A 步 mood 与 B 步候选冲突：以 A 为准，但须从 B 步候选借 1 项差异（转场 shader / 背景 atmosphere / 首镜布局）
```

**禁止**连续两支视频（同一频道）使用相同命名风格 + 相同首镜布局 + 相同片尾变体。

---

## 4. 风格 → 首镜 / 装饰 / 转场（勿全用 split-narration-visual）

| 风格 | 推荐首镜布局 | 背景装饰（css-animations） | 转场倾向 |
|------|-------------|---------------------------|---------|
| Swiss Pulse | `metric-comparison-band` 或 `split-narration-visual` | 网格线、注册标记 | 硬切 / cinematic-zoom |
| Data Drift | `kinetic-typography` 或 `data-chart-race` | 粒子场、径向光晕 | gravitational-lens |
| Deconstructed | `full-bleed-statement` | 扫描线、glitch grain | glitch / whip-pan |
| Shadow Cut | `full-bleed-statement` | 深阴影、暗角 | domain-warp |
| Velvet Standard | `narration-trend-list` | 细颗粒、发丝线 | cross-warp-morph |
| Maximalist Type | `kinetic-typography` | 叠字层、色块 | ridged-burn |
| Soft Signal | `narration-card-grid` | 柔渐变、暖 grain | thermal-distortion |
| Folk Frequency | `bar-comparison-panel` | 图案块、色块 | swirl-vortex |

**首镜禁止默认：** 无用户要求时，不得连续项目都以 `split-narration-visual` 开场。

---

## 5. 布局轮换（片内）

- 连续两镜**不得**使用相同布局模式（SKILL 原有规则，须严格执行）
- 全片至少用到 **4 种不同**布局模式
- 数据镜优先 `metric-comparison-band` / `bar-comparison-panel` / `data-chart-race`，不要全部 `narration-card-grid`

---

## 6. 片尾变体（`outroMode: default` 时三选一）

用户写了【品牌片尾】且未要求「自定义」时，Agent **按视觉风格选变体**，不要每支都用 A：

| 变体 | 适用风格 | 布局 | 画面要点 |
|------|---------|------|---------|
| **A** `outro-variant-a` | Swiss Pulse, Velvet Standard, Data Drift | `dual-highlight-closing` | 金句 zoom + 圆形头像 + 关注语（经典） |
| **B** `outro-variant-b` | Deconstructed, Shadow Cut, Maximalist Type | `full-bleed-statement` | 全屏大字 kinetic，**无头像**；`#sc{N}-title` 主 Slogan |
| **C** `outro-variant-c` | Folk Frequency, Soft Signal, 教程向 | `narration-card-grid` 或 `metric-comparison-band` | 频道名卡片 + 小头像角标 + 双行收尾 |

写入 `assets/brand.json` 的 `outroVariant` 字段（`"a"` | `"b"` | `"c"`）。

`apply-brand.mjs` 仍 patch `#sc{N}-title` / `#sc{N}-follow` / `#sc{N}-sub`；变体 B/C 的 HTML 结构由 Agent 按上表实现，**禁止**所有项目复制同一段片尾 HTML。

---

## 7. 禁止清单（同质化红线）

写 HTML 前自检，命中任一项须改方案：

- ❌ 未写 `design.md` 就开写 `index.html`
- ❌ 未读 `css-animations` / `design-motion-principles` / `web-typography`
- ❌ 默认 cyan-on-dark + 紫蓝渐变 + 玻璃卡 2×2（house-style 明确列为 lazy default）
- ❌ 每镜都是相同圆角玻璃卡 + 左侧 accent 竖条
- ❌ 首镜固定 `split-narration-visual` + 线框地球 SVG
- ❌ 片尾固定 variant A（有头像 zoom）而风格明明是 Deconstructed / Shadow Cut
- ❌ 全片只有一种 GSAP 入场：`from({ opacity: 0, y: 30 })` 重复 N 次
- ❌ 背景纯 `#0a0a0a` 无任何 atmosphere 装饰层

---

## 8. 分镜表必须多两列

输出分镜表时增加：

```markdown
| # | … | 布局 | 视觉风格 | 片尾变体 |
```

首行摘要示例：

```text
总时长: 52s | 风格: Data Drift | 首镜: kinetic-typography | 片尾: variant-b | design.md: ✓
```
