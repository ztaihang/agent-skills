# xhs-static-cards

小红书 **静态图文卡片** Skill：文案稿 → HTML 预览 → 导出 PNG（1080×1440，3:4）。

与同仓库 [hyperframes-shorts](../hyperframes-shorts/)（短视频 MP4）互补，不重叠。

---

## 适用场景

- Codex / Cursor **Skill 推荐榜**（Top N 清单）
- AI 工具清单、效率工具合集
- （P3）Vibecoding / Cursor 教程步骤卡

## 不适用

- 长文滚动页（用 xiaohongshu-images 等）
- 视频笔记（用 hyperframes-shorts）
- 自动发布小红书

---

## 安装

```bash
npx skills add ztaihang/agent-skills@xhs-static-cards
# 或本地：复制 skills/xhs-static-cards 到 ~/.agents/skills/ 与 ~/.cursor/skills/
```

### 配套 skill（Step 0 预检会检查，缺则提示安装）

| Skill | 必须 | 说明 |
|-------|------|------|
| `design-taste-frontend` 或 `taste-skill` | ✅ 二选一 | 审美 / 反 slop |
| `web-typography` | ✅ | 中文排版 |
| `frontend-design` | ✅ | 布局结构 |
| `exporting-to-png` | ✅ | 导出参考 |

```bash
npx skills add nexu-io/open-design@frontend-design -g -y
npx skills add spencerpauly/awesome-cursor-skills@exporting-to-png -g -y
npx skills add wondelai/skills@web-typography -g -y
# 若无 design-taste-frontend：
npx skills add nexu-io/open-design@taste-skill -g -y
```

**Agent 使用前会跑 Step 0 预检**；缺配套 skill 会停止并给出上述命令，不会 silent 跳过。

---

## 使用

1. 对话中 `@xhs-static-cards` 或粘贴 [examples/prompt-template.md](examples/prompt-template.md)
2. 填写 **项目路径** 和 **文案稿**
3. Agent 生成 `content.json` + `preview/` HTML
4. 你执行 `npm run dev` 预览
5. 满意后说「导出」，Agent 跑 `npm run export`

---

## 项目结构（生成在用户指定路径）

```text
my-xhs-cards/
├── content.json
├── package.json
├── scripts/
│   ├── build.mjs
│   └── export.mjs
├── families/
│   └── skill-list/
├── preview/
│   ├── index.html
│   ├── cover.html
│   └── card-01.html ...
└── output/
    ├── cover.png
    └── card-01.png ...
```

---

## License

MIT（与仓库根目录一致）
