# hyperframes-shorts

中文 HyperFrames 短视频全流程 Agent Skill：**口播拆镜 → 视觉规划 → Edge TTS → 时间轴 → 校验**；用户只需 `npm run dev` 预览。

---

## 项目路径

提示词里的 **项目路径** = 你希望存放 HyperFrames 工程的文件夹（任意本地路径，与 skill 安装位置无关）。  
示例：`~/Videos/my-topic`、`C:\Users\你\Videos\my-topic`

---

## 安装

```bash
npx skills add ztaihang/agent-skills@hyperframes-shorts
```

CLI 会自动识别 Cursor / Codex / Trae 等 runtime 并安装到对应 skills 目录。需要指定时加 `-a cursor` / `-a codex` / `-a trae`。

**Trae（Vibe Coding）** 建议在 HyperFrames 项目根目录执行：

```bash
npx skills add ztaihang/agent-skills@hyperframes-shorts -a trae -y
# 国内 Trae：-a trae-cn
```

> 末尾若出现 `PromptScript does not support global skill installation`，可忽略——这是 PromptScript 通道的提示，Trae / Cursor 通常已成功。

### 还须安装

```bash
npx skills add heygen-com/hyperframes@hyperframes
npx skills add heygen-com/hyperframes@hyperframes-cli
npx skills add heygen-com/hyperframes@gsap
npx skills add heygen-com/hyperframes@css-animations
npx skills add kylezantos/design-motion-principles@design-motion-principles
npx skills add wondelai/skills@web-typography
```

系统：FFmpeg、Node.js ≥ 22、Python 3 + `pip install edge-tts`

---

## 怎么用

**Cursor：** 对话中 `@hyperframes-shorts`

**Trae（Vibe Coding）：** 安装后输入 `/hyperframes-shorts`，或直接粘贴提示词

1. 按 [examples/prompt-template.md](examples/prompt-template.md) 填写 **项目路径** 与口播
2. Agent 自动构建完成后，进入该项目目录预览：

```powershell
cd "<项目路径>"
npm run dev
```

---

## 文档

| 文件 | 内容 |
|------|------|
| [examples/prompt-template.md](examples/prompt-template.md) | 用户提示词模板 |
| [examples/outro-rules.md](examples/outro-rules.md) | 品牌片尾三种模式 |
| [templates/](templates/) | 新建视频项目时复制的脚本 |
| [SKILL.md](SKILL.md) | 完整 Agent 规范 |

---

## 特性摘要

- 语义拆镜、多种布局、**每项目 `design.md` + visual-styles 预设轮换**
- 写 HTML 前**必读** css-animations / design-motion-principles / web-typography
- Edge TTS 单轨 `voiceover.wav` + 字幕对齐
- 品牌片尾：`off` / 变体 A·B·C / 自定义
- Agent 自动 TTS、时间轴、`npm run check`；**不自动 render**
- **版式硬性规则**：字幕单行、文字不重叠、禁止 AI 风 emoji/表情包插图
