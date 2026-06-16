# 模板目录

Agent 将本目录下文件复制到**用户指定的项目路径**（非 skill 安装目录）。

| 文件 | 说明 |
|------|------|
| `package.json` | dev / build / export 脚本 |
| `scripts/build.mjs` | 读取 `content.json`，生成 `preview/*.html` |
| `scripts/export.mjs` | Playwright 导出 `output/*.png` |
| `families/skill-list/` | Skill 推荐族样式与片段 |
| `examples/codex-skills.json` | 示例 content.json |

复制后 Agent 在项目根写入 `content.json`，再执行 `npm install && npm run build`。
