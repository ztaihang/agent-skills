# xhs-static-cards · 用户提示词模板

复制对应区块发给 Agent。Agent 自动解析文案、生成 `content.json`、执行 `npm run build`；**你只需预览，确认后再导出**。

**项目路径**：存放卡片工程的文件夹，例如 `D:\Projects\my-xhs-cards\codex-skills-01`。

---

## 预览（你需要手动执行）

```powershell
cd "<项目路径>"
npm run dev
```

浏览器打开 `http://localhost:5173`，从索引进入封面与各卡片页检查。

---

## 导出 PNG（预览满意后再说「导出」）

```powershell
cd "<项目路径>"
npm run export
```

输出在 `output/cover.png`、`output/card-01.png` …

> Agent **默认不会**自动 export；你说「导出 / 出图 / export」后再执行。

---

## 标准提示词（Skill 推荐清单）

```markdown
请按 xhs-static-cards 制作小红书静态图文卡片。

项目路径：D:\Projects\my-xhs-cards\codex-skills-01
内容类型：skill-list
视觉主题：soft-pink（可选 clean-white / tool-slate）

生成前必读：taste-skill、web-typography、frontend-design

文案稿：
Codex别裸装！这 9 个 Skills 必须安排上！
（粘贴完整文案…）

请：
1. 解析文案写入 content.json
2. 从 xhs-static-cards templates 搭建项目并 npm install && npm run build
3. 我手动 npm run dev 预览
4. 不要自动 npm run export
```

---

## 最小提示词

```markdown
@xhs-static-cards

项目路径：D:\Projects\my-xhs-cards\test-01
theme: soft-pink

（粘贴文案）
```

---

## 修改与重导出

- 改文案 → 让 Agent 更新 `content.json` → `npm run build` → 再预览
- 改样式 → 改 `families/skill-list/themes/*.css` 或让 Agent 在同族内调 theme
- 满意后 → `npm run export`
