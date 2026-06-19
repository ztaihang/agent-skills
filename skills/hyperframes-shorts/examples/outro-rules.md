# 品牌片尾 · 三种模式（Agent 必须遵守）

## 决策表

| 用户输入 | `outroMode` | 行为 |
|---------|-------------|------|
| **没写**【品牌片尾】块 | `off` | **完全不生成片尾**：无片尾镜、无片尾 TTS、不跑默认模板 |
| **写了**【品牌片尾】，未说自定义 | `default` | **变体 A/B/C 之一**（按视觉风格选，见 §默认片尾三变体） |
| **写了**【品牌片尾】+ 明确要别的样式 | `custom` | **不用默认模板**：按用户「片尾说明」单独实现片尾镜 |

> **硬性规则：** 绝不擅自加用户没写的片尾；没写块 = 当没有片尾。

---

## 模式 A：`off`（没写片尾）

### 用户提示词

只给正文口播，**不出现**【品牌片尾】块。

### Agent 必做

1. `assets/brand.json`：

```json
{
  "outroMode": "off",
  "useDefaultOutro": false
}
```

2. `audio/lines.json`：**不要**有片尾镜行（最后一镜 `scene` 不为片尾）
3. `index.html`：可无片尾 scene；若有占位则 **schedule 里不含片尾镜**（不切镜）
4. **跳过** `apply-brand.mjs` 的默认文案 patch
5. 正文结尾**不要**夹带「关注 / 下期见」等片尾句

---

## 模式 B：`default`（写了片尾 → 默认模板）

### 用户提示词（推荐）

```markdown
【品牌片尾】
片尾样式：默认模板
频道名：浣熊不加班
头像：https://你的头像直链.webp

片尾口播全文：
掌握 AI 实战，下班不留遗憾。关注浣熊不加班，我们下期见！
```

`片尾样式：默认模板` 可省略——**只要没写「自定义」就视为默认**。

### Agent 必做

1. 解析「片尾口播全文」，按句号拆 2～3 条 → `lines.json` **最后一镜**（带 `scene` 编号，如 7）
2. 正文（scene 1–6）**不重复**片尾句
3. `assets/brand.json`：

```json
{
  "outroMode": "default",
  "useDefaultOutro": true,
  "outroVariant": "a",
  "channelName": "浣熊不加班",
  "avatarUrl": "https://...",
  "outroScript": "掌握 AI 实战，下班不留遗憾。关注浣熊不加班，我们下期见！",
  "outroTitle": "掌握 AI 实战，下班不留遗憾。",
  "followText": "关注浣熊不加班",
  "outroSub": "我们下期见！"
}
```

| 字段 | 来源 |
|------|------|
| `outroScript` | 用户「片尾口播全文」原文 |
| `outroTitle` | 全文**第一句**（金句 zoom） |
| `followText` | 第二句「关注…」部分 |
| `outroSub` | 第二句剩余（如「我们下期见！」） |

4. 跑 `apply-brand.mjs` → **https** 头像下载（http 会跳过并提示）+ patch `#sc{N}-title` / `#sc{N}-follow` / `#sc{N}-sub`（N = 片尾镜号）
5. 片尾镜 GSAP 对齐 `schedule` 中该 `scene` 各条的 `start`

### 默认片尾三变体（`outroMode: default`，按视觉风格选，禁止每支都用 A）

| 变体 | `outroVariant` | 适用风格 | 画面 |
|------|----------------|---------|------|
| **A** | `"a"` | Swiss Pulse, Velvet Standard, Data Drift | 双金边卡 + 圆形头像 + 金句 zoom |
| **B** | `"b"` | Deconstructed, Shadow Cut, Maximalist Type | 全屏 kinetic 大字，**无头像** |
| **C** | `"c"` | Soft Signal, Folk Frequency, 教程向 | 频道名卡片 + 小头像角标 |

Agent 写 `brand.json` 时须填 `outroVariant`。HTML/GSAP 按变体实现，**不要**所有项目复制同一段片尾 DOM。

### 默认模板固定画面（variant A 专用）

- 布局：`dual-highlight-closing` + 居中片尾 wrap
- 元素：`#sc{N}-title`（金句）→ `#avatar-ring` + `#brand-avatar`（圆形头像）→ `#sc{N}-follow` + `#sc{N}-sub`
- 动效：第 1 条口播 → 金句 zoom punch；第 2 条口播 → 头像弹出 + 关注/收尾 punch
- **不淡出黑屏**，片尾结束即全片结束

variant B/C 结构见 **`templates/visual-style-guide.md` §6**。

---

## 模式 C：`custom`（写了片尾但要别的样式）

### 用户提示词

```markdown
【品牌片尾】
片尾样式：自定义
片尾说明：不要头像，只要镜内两行大字居中，第一行 Slogan 第二行关注语（**非底部字幕换行**；底部 `.sl` 仍每条单行）

频道名：浣熊不加班
头像：（可留空）

片尾口播全文：
掌握 AI 实战，下班不留遗憾。关注浣熊不加班，我们下期见！
```

关键词（任一击中即 custom）：

- `片尾样式：自定义`
- `不用默认模板` / `不要默认片尾`
- `片尾说明：` 后面有具体布局/动效描述

### Agent 必做

1. `brand.json`：

```json
{
  "outroMode": "custom",
  "useDefaultOutro": false,
  "channelName": "...",
  "avatarUrl": "...",
  "outroScript": "...",
  "customOutroNotes": "用户片尾说明原文"
}
```

2. **仍然**把「片尾口播全文」拆进 `lines.json` 最后一镜并 TTS（口播必须念出）
3. **不要**调用默认模板的 HTML 结构 / GSAP（片尾 title zoom、`#avatar-ring` 等）
4. 按 `片尾说明` **重写**片尾镜的 HTML + GSAP
5. `apply-brand.mjs` 仅下载头像（若给了 URL），**不** patch 默认 `#sc{N}-*` 文案

---

## 流水线

| 步骤 | `off` | `default` | `custom` |
|------|-------|-----------|----------|
| 写 `brand.json` | `outroMode: off` | 完整字段 | `custom` + notes |
| `lines.json` 片尾镜 | ❌ 无 | ✅ 有 | ✅ 有 |
| `generate-tts.py` | 不含片尾句 | 含片尾句 | 含片尾句 |
| `align-subtitles.py` | ✅ | ✅ | ✅ |
| `apply-audio-schedule.mjs` | ✅ | ✅ | ✅ |
| `apply-brand.mjs` | 跳过 | 默认 patch | 仅头像（可选） |
| 片尾镜 HTML/GSAP | 无 / 占位 | **变体 A/B/C** | **按说明定制** |
