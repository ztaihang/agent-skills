# agent-skills

面向 **Cursor / Codex / Claude Code / Trae（Vibe Coding）** 等 Agent 的 Skills 合集，用于扩展 AI 在特定任务上的工作流。

当前收录：**中文 HyperFrames 解说短视频**一键构建（口播 → 分镜 → TTS → 预览）。

---

## 包含的 Skills

| Skill | 适用场景 | 文档 |
|-------|---------|------|
| **hyperframes-shorts** | 科技 / 教程类中文口播短视频（HyperFrames + GSAP） | [说明与模板](skills/hyperframes-shorts/) |

---

## 项目路径说明

做视频时，在提示词里填 **「项目路径」**——即你希望 Agent **创建/存放 HyperFrames 工程**的文件夹，例如：

- Windows：`C:\Users\你\Videos\my-topic`
- macOS / Linux：`~/Videos/my-topic`

Skill 会在此目录生成 `index.html`、`audio/`、`scripts/` 等。**与 skill 安装目录无关**，任选你有写权限的位置即可。

---

## 快速开始（hyperframes-shorts）

### 1. 安装

在终端执行（支持 Cursor、Codex、Claude Code、Trae 等 [Agent Skills 兼容 runtime](https://github.com/vercel-labs/skills)）：

```bash
npx skills add ztaihang/agent-skills@hyperframes-shorts
```

CLI 会**自动识别**你当前的 runtime，并把 skill 装到对应目录。需要指定时可加 `-a cursor` / `-a codex` / `-a trae` 等。

**Trae（Vibe Coding）用户**建议在项目根目录执行，并显式指定 agent（国内版 Trae 用 `trae-cn`）：

```bash
npx skills add ztaihang/agent-skills@hyperframes-shorts -a trae -y
# 国内 Trae：
# npx skills add ztaihang/agent-skills@hyperframes-shorts -a trae-cn -y
```

Skill 会写入 `.trae/skills/`（或 `.trae-cn/skills/`），Trae 对话中可直接 `/hyperframes-shorts` 或描述需求自动匹配。

也可在对话里直接说：「帮我安装这个 skill：https://github.com/ztaihang/agent-skills（skill 名 hyperframes-shorts）」。

列出本仓库全部 skill：

```bash
npx skills add ztaihang/agent-skills --list
```

> 末尾若出现 `PromptScript does not support global skill installation`，**可忽略**——这是 PromptScript 通道的提示，与 Trae / Cursor / Codex 无关，上述 runtime 通常已成功安装。

<details>
<summary>手动安装（可选）</summary>

| Runtime | 安装路径 |
|---------|---------|
| Cursor | `~/.cursor/skills/hyperframes-shorts/` |
| Codex CLI | `~/.codex/skills/hyperframes-shorts/` |
| Trae（Vibe Coding） | `.trae/skills/hyperframes-shorts/` 或 `~/.trae/skills/hyperframes-shorts/` |
| Trae 国内版 | `.trae-cn/skills/hyperframes-shorts/` 或 `~/.trae-cn/skills/hyperframes-shorts/` |
| 通用（skills CLI） | `~/.agents/skills/hyperframes-shorts/` |

将本仓库中 `skills/hyperframes-shorts/` 目录复制或 clone 到上表对应路径即可。

</details>

### 2. 安装 HyperFrames 相关依赖

```bash
npx skills add heygen-com/hyperframes@hyperframes
npx skills add heygen-com/hyperframes@hyperframes-cli
npx skills add heygen-com/hyperframes@gsap
npx skills add heygen-com/hyperframes@css-animations
npx skills add kylezantos/design-motion-principles@design-motion-principles
npx skills add wondelai/skills@web-typography
```

### 3. 环境要求

| 组件 | 要求 |
|------|------|
| FFmpeg | 必须（音视频处理） |
| Node.js | ≥ 22 |
| Python + edge-tts | 中文配音：`pip install edge-tts` |

### 4. 在 Agent 里使用

**Cursor**

1. 新建对话，附加或 `@hyperframes-shorts`
2. 复制 [提示词模板](skills/hyperframes-shorts/examples/prompt-template.md)，填好 **项目路径** 和 **口播原文**
3. Agent 会自动完成：脚手架、TTS、时间轴、`npm run check`

**Trae（Vibe Coding / SOLO 模式）**

1. 在项目根目录安装 skill（见上方 `-a trae` 命令）
2. 新建对话，输入 `/hyperframes-shorts`，或直接粘贴 [提示词模板](skills/hyperframes-shorts/examples/prompt-template.md) 的内容
3. Agent 同样会自动完成脚手架、TTS、时间轴、`npm run check`

**预览（所有 runtime 通用）**

进入你在提示词里填写的目录预览：

```powershell
cd "<项目路径>"
npm run dev
```

浏览器打开终端里的 Studio 地址，检查字幕、口播、动效。满意后再让 Agent 执行 `npm run render` 导出 MP4。

---

## 这个 skill 会帮你做什么

- 按语义**拆镜**，规划布局与动效；**每支视频轮换视觉风格**（`design.md` + visual-styles 预设）
- 写 HTML 前读取 **css-animations / design-motion-principles / web-typography**，避免千篇一律的科技蓝 UI
- **Edge TTS** 中文配音 + 字幕时间轴对齐
- 可选**品牌片尾**（金句 zoom、头像、关注引导）
- 自动跑校验，交付前 **0 error**

**不会**自动导出 MP4——需你预览确认后再说「导出 / render」。

---

## 提示词模板

| 文档 | 内容 |
|------|------|
| [prompt-template.md](skills/hyperframes-shorts/examples/prompt-template.md) | 标准 / 最小 / 片尾提示词 |
| [outro-rules.md](skills/hyperframes-shorts/examples/outro-rules.md) | 品牌片尾三种模式 |

---

## 示例效果

本 skill 产出 **HyperFrames 网页成片**（HTML + GSAP + TTS）：

1. Agent 在你指定的 **项目路径** 下生成工程  
2. `npm run dev` 在 Studio 里预览  
3. 确认后 `npm run render` 导出 MP4  

欢迎在 [Issues](https://github.com/ztaihang/agent-skills/issues) 分享成片链接或反馈问题。

---

## 常见问题

**Q：安装后 `@` 找不到 skill？**  
新开一条对话再 `@hyperframes-shorts`；或重新执行安装命令。

**Q：Trae Vibe Coding 里找不到 skill？**  
确认 skill 在 `.trae/skills/hyperframes-shorts/`（国内版为 `.trae-cn/skills/`），新开对话后输入 `/hyperframes-shorts`；若装在全局目录，Trae 可能读不到，请用 `-a trae` 装到项目内。

**Q：和 HyperFrames 官方 skill 什么关系？**  
本 skill 是**中文短视频工作流层**（拆镜、TTS、片尾、交付规范）；画面与 HTML 仍依赖 [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) 生态。

**Q：项目路径必须叫什么？**  
任意本地路径，只要 Agent 有读写权限；建议单独建文件夹，例如 `~/Videos/项目名`。

**Q：想贡献改进？**  
欢迎 [Issue / PR](https://github.com/ztaihang/agent-skills/pulls)，说明见 [CONTRIBUTING.md](CONTRIBUTING.md)。

---

## License

[MIT](LICENSE)
