# 贡献指南

欢迎 Issue 与 Pull Request。普通使用者只需看 [README.md](README.md)。

---

## 仓库结构

```text
agent-skills/
└── skills/
    └── hyperframes-shorts/
        ├── SKILL.md          # Agent 主规范
        ├── examples/         # 用户提示词
        └── templates/        # 视频项目脚本模板
```

---

## 如何贡献

1. **Fork** 本仓库
2. 在 `skills/hyperframes-shorts/` 下修改（或新增 `skills/<新skill名>/`）
3. 提交 **Pull Request**，说明改动原因与测试方式

---

## 修改 skill 时请注意

- **只改** `skills/` 下的 Git 源码  
- **不要**只在 `~/.codex/skills/` 或 `~/.agents/skills/` 里改——那是 `npx skills add` 写入的安装副本，无法通过 PR 贡献  
- 做 HyperFrames **视频**时改的是用户 **项目路径** 下的工程，不是 skill 目录  

若你本地用 Agent 协助改 skill，请让 Agent 编辑 **fork/clone 后的仓库路径** 下的 `skills/`，不要写死任何维护者私有路径。

---

## 新增 skill

1. 在 `skills/` 下新建目录，包含 `SKILL.md`（YAML frontmatter：`name`、`description`）
2. 更新根目录 [README.md](README.md) 的 Skills 表格
3. 提交 PR

---

## Issue 请尽量包含

- 使用的 Agent（Cursor / Codex 等）与系统（Windows / macOS）
- 提示词片段（可脱敏）
- 报错日志或截图

---

## License

贡献内容以本仓库 [MIT](LICENSE) 协议发布。
