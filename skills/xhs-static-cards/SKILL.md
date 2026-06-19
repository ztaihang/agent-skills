---
name: xhs-static-cards
description: 小红书静态图文卡片工作流（1080×1440，3:4）。将用户文案稿解析为结构化内容，在用户指定的项目路径生成可预览的 HTML 页面，用户确认后再导出 PNG。支持 template-family：skill-list（工具/Skill 推荐清单）、vibecoding（教程/工作流，P1 仅 skill-list 完整实现）。执行前必须 Step 0 预检配套 skill 与 Node；生成 HTML 前必读 design-taste-frontend（或 taste-skill）、web-typography、frontend-design；禁止 CSS 动画与自动 export。与 hyperframes-shorts（视频）分工不同，本 skill 只做静态图。
---

# xhs-static-cards · 小红书静态图文卡片

本 Skill 用于在**用户指定的项目路径**下构建「文案 → HTML 预览 → 导出 PNG」工程。

- **Skill 源码仓库**：`D:\Projects\agent-skills\skills\xhs-static-cards\`（或 `ztaihang/agent-skills`）
- **本地安装路径**（Agent 读取）：`~/.agents/skills/xhs-static-cards/` 或 `~/.cursor/skills/xhs-static-cards/`
- **卡片工程路径**：用户每次指定，与 skill 安装目录**无关**

修改某次卡片内容 → 改**用户项目目录**；修改 skill 规范 → 改**本 skill 目录**。

---

# 与 hyperframes-shorts 的区别

| | hyperframes-shorts | xhs-static-cards |
|--|-------------------|------------------|
| 产出 | 视频 MP4 | 静态 PNG |
| 画布 | 1920×1080 等 | 1080×1440（3:4） |
| 动效 | GSAP 必须 | **禁止** |
| 预览 | Studio 播放 | 浏览器静态页 |
| 发布 | 不涉及 | **不涉及**（用户手动发小红书） |

---

# Step 0：环境预检（第一步，缺则停止并提示）

> **未通过预检禁止进入生成流程。** 向用户明确列出缺失项与安装命令，等用户确认已安装或授权 Agent 代装后再继续。

## 0.1 检查本 skill 是否可用

在以下路径探测 `SKILL.md` 是否存在：

| 路径 | 说明 |
|------|------|
| `~/.agents/skills/xhs-static-cards/SKILL.md` | 推荐（与 hyperframes 等同级） |
| `~/.cursor/skills/xhs-static-cards/SKILL.md` | Cursor 用户 |
| 仓库 `D:\Projects\agent-skills\skills\xhs-static-cards\SKILL.md` | 开发副本 |

**若均不存在**，停止并提示：

```powershell
Copy-Item -Recurse "D:\Projects\agent-skills\skills\xhs-static-cards" "$env:USERPROFILE\.agents\skills\xhs-static-cards"
# 或
npx skills add ztaihang/agent-skills@xhs-static-cards -g -y
```

## 0.2 检查配套 skill（生成 HTML 前必读）

| 用途 | 必选其一 | 安装命令 |
|------|----------|----------|
| 审美 / 反 slop | **`design-taste-frontend`** 或 `taste-skill` | 已有前者则不必装后者 |
| 中文排版 | **`web-typography`** | `npx skills add wondelai/skills@web-typography -g -y` |
| 布局结构 | **`frontend-design`** | `npx skills add nexu-io/open-design@frontend-design -g -y` |
| 导出方法参考 | **`exporting-to-png`** | `npx skills add spencerpauly/awesome-cursor-skills@exporting-to-png -g -y` |

探测目录：`~/.agents/skills/<name>/`、`~/.cursor/skills/<name>/`（`design-taste-frontend` 可替代 `taste-skill`）。

**若缺 `web-typography` 或 `frontend-design` 或 `exporting-to-png`**，停止并一次性给出上表安装命令，**不要** silently 跳过。

**若缺 taste 类 skill**（两者皆无），停止并提示安装其一：

```bash
npx skills add nexu-io/open-design@taste-skill -g -y
# 或确保已有 design-taste-frontend
```

## 0.3 检查 Node 与项目工具

```powershell
node -v    # 需要 ≥ 18（推荐 ≥ 22）
npm -v
```

缺失 Node → 提示安装 Node.js LTS，停止。

Export 阶段还需 Playwright Chromium（见 Step 7）；**build 阶段不强制**，export 失败再提示：

```powershell
npx playwright install chromium
```

## 0.4 预检通过后的 taste 默认值（静态图）

读 `design-taste-frontend` 或 `taste-skill` 后使用：

```text
DESIGN_VARIANCE 5 | MOTION_INTENSITY 1 | VISUAL_DENSITY 5
```

静态 PNG **禁止**加 CSS animation / transition / GSAP。

---

# 执行顺序（预检通过后）

1. **本 Skill** — 识别内容类型、解析文案、选 template-family、写 `content.json`
2. **`design-taste-frontend`** 或 **`taste-skill`** — 定 aesthetic + theme variant
3. **`web-typography`** — 中文标题/正文字号、行高
4. **`frontend-design`** — 布局与组件结构
5. **`exporting-to-png`** — 导出阶段参考 Playwright 截图做法
6. **复制 `templates/` 到用户项目** → `npm install` → `npm run build`
7. **用户手动** `npm run dev` 预览
8. **用户确认后** Agent 执行 `npm run export`（用户未说「导出/出图」则**禁止**）

---

# 内容分类 → template-family

| 特征 | `type` | family | 状态 |
|------|--------|--------|------|
| 多个 ①②③ / Top N / Skill 名列表 | `skill-list` | `families/skill-list/` | ✅ P1 |
| 步骤 / 流程 / Cursor·Vibecoding 教程 | `vibecoding` | `families/vibecoding/` | 🔜 P3 占位 |

同族内切换 **theme**：`soft-pink` | `clean-white` | `tool-slate` | `dark-neon`（见 `references/theme-variants.md`）。

---

# 全自动交付流水线

## Agent 必须自动完成

| 步骤 | 动作 |
|------|------|
| 0 | **Step 0 预检**（见上） |
| 1 | 确认 **项目路径** |
| 2 | 读 design-taste-frontend/taste-skill + web-typography + frontend-design |
| 3 | 解析文案 → `content.json`（`references/content-schema.md`） |
| 4 | 从 **`{{SKILL_DIR}}/templates/`** 复制到项目：`package.json`、`scripts/`、`families/` |
| 5 | `npm install` |
| 6 | `npm run build` → `preview/` |
| 7 | 交付：仅告知 `npm run dev`；**禁止自动 export** |

`{{SKILL_DIR}}` = 本 skill 安装目录（含 `templates/` 子目录）。

## 用户手动做（预览）

```powershell
cd "<项目路径>"
npm run dev
```

浏览器 `http://localhost:5173` → 索引 → 封面与各卡片。

## 用户确认后再导出

用户明确说「可以导出 / export / 出图」后：

```powershell
cd "<项目路径>"
npm run export
```

输出：`output/cover.png`、`output/card-01.png` …

Export 失败且提示 Chromium 缺失 → 运行 `npx playwright install chromium` 后重试。

---

# 文案解析规则（skill-list）

- **title** / **subtitle** / **intro**（可选）
- **badge**：默认 `AI 工具推荐`
- **highlight**：如 `TOP 9`
- **items[]**：`num`, `name`, `tags[]`, `desc`, `scenes`
- 保留用户原文含义，可整理标点，**不擅自删核心信息**

编号识别：`①` `1.` `humanizer — 描述` 等。

---

# 硬约束

- 画布 **1080×1440**，导出 **3:4**
- **禁止** CSS animation / transition
- **禁止** 未经用户确认自动 `npm run export`
- **禁止** AI 直接生图替代 HTML 排版
- **禁止** 帮用户发布小红书（本 skill 只产出 PNG）

---

# 模板与参考

| 路径 | 用途 |
|------|------|
| `templates/scripts/build.mjs` | content.json → preview HTML |
| `templates/scripts/export.mjs` | Playwright → output PNG |
| `templates/families/skill-list/` | Skill 推荐族样式 |
| `templates/examples/codex-skills.json` | 示例数据 |
| `references/content-schema.md` | JSON 字段 |
| `references/theme-variants.md` | 主题变体 |
| `examples/prompt-template.md` | 用户提示词 |

---

# 新建项目：复制清单

```text
{{SKILL_DIR}}/templates/package.json     → <项目>/
{{SKILL_DIR}}/templates/scripts/       → <项目>/scripts/
{{SKILL_DIR}}/templates/families/      → <项目>/families/
content.json                             → <项目>/（Agent 生成）
```

复制后项目结构：

```text
<项目路径>/
├── content.json
├── package.json
├── scripts/build.mjs, export.mjs
├── families/skill-list/
├── preview/          ← build 生成
└── output/           ← export 生成
```

---

# 配套 skill 一键安装（预检失败时用）

```bash
npx skills add nexu-io/open-design@frontend-design -g -y
npx skills add spencerpauly/awesome-cursor-skills@exporting-to-png -g -y
npx skills add wondelai/skills@web-typography -g -y
# taste 二选一（若尚无 design-taste-frontend）：
npx skills add nexu-io/open-design@taste-skill -g -y
```

---

# 禁止交给用户的步骤（Agent 必须代劳）

- ❌ 手写 `build.mjs` / `export.mjs`（必须从 templates 复制）
- ❌ 未经确认自动 `npm run export`
- ❌ 预检失败仍继续生成
- ❌ 把 `npm install` / `npm run build` 丢给用户（Agent 应自动执行）

## 用户只需手动做

1. **`npm run dev`** 预览
2. 确认满意后口头说「导出」
