# hyperframes-shorts

中文 HyperFrames 短视频全流程 Agent Skill：**口播拆镜 → 视觉规划 → Edge TTS（WordBoundary 字幕对齐）→ 时间轴 → 校验**；用户只需 `npm run dev` 预览。

---

## 项目路径

提示词里的 **项目路径** = 你希望存放 HyperFrames 工程的文件夹（任意本地路径，与 skill 安装位置无关）。  
示例：`F:\myvideos\codex-intro`、`~/Videos/my-topic`

## 本机 Skill 源码（开发用）

| 路径 | 说明 |
|------|------|
| `F:\myvideos\agent-skills\skills\hyperframes-shorts\` | 历史路径（若已迁移见下） |
| `D:\projects\agent-skills\skills\hyperframes-shorts\` | **本机源码（D 盘）** |
| `%USERPROFILE%\.agents\skills\hyperframes-shorts\` | Agent 运行时读取（由源码同步/安装） |

改 skill 规范或模板脚本 → 编辑 **D 盘源码** → 再同步到 `~/.agents/skills/`（或 `npx skills add`）。  
已有视频项目须 **重新复制** `templates/scripts/`（含 **`realign-line.py`**）到项目，或手动 merge 脚本更新。

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
npx hyperframes skills update   # 拉齐 hyperframes / core / animation / creative / cli
npx skills add leonxlnx/taste-skill@design-taste-frontend -g -y
npx skills add kylezantos/design-motion-principles@design-motion-principles
npx skills add wondelai/skills@web-typography
```

系统：FFmpeg、Node.js ≥ 22、Python 3 + `pip install edge-tts faster-whisper`（字幕词级对齐用，见 `templates/requirements-align.txt`）

**反 AI 味 + 有质感动效：** [templates/anti-slop-motion-scheme.md](templates/anti-slop-motion-scheme.md)

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
| [templates/anti-slop-motion-scheme.md](templates/anti-slop-motion-scheme.md) | 反 AI 味 + L0–L4 动效方案 |
| [templates/scene-density-guide.md](templates/scene-density-guide.md) | 镜内防太空 |
| [templates/subtitle-tts-guide.md](templates/subtitle-tts-guide.md) | 口播/字幕分离 + speak 读音 |
| [templates/hyperframes-zh-checklist.md](templates/hyperframes-zh-checklist.md) | **中文交付自检（字体/字幕/背景）** |
| [templates/delivery-pitfalls.md](templates/delivery-pitfalls.md) | **交付避坑复盘**（可单独转发给接手人） |
| [SKILL.md](SKILL.md) | 完整 Agent 规范 |

---

## 特性摘要

- 语义拆镜、多种布局、**每项目 `design.md` + Motion Plan + visual-styles 轮换**
- **HyperFrames 0.7 + P0/P1/P2 真实感提质**（design-adherence / video-composition / data-in-motion / snapshot / design-picker 等）
- 写 HTML 前**必读** taste-skill + anti-slop + hyperframes-animation/creative + design-motion-principles + web-typography
- **镜内防太空**：短镜须副信息 + `#root` 静态装饰（`scene-density-guide.md`；禁止每镜 infinite ambient）
- **口播 / 字幕分离**：`voice` 整句 TTS；`subtitle` 仅上屏；禁止为 maxHan 拆多 wav
- **字幕对齐**：TTS 后 **`align-subtitles.py`**（首选）；Whisper 不可用时 **`fallback-alignments.py`**（权重兜底，须听检）→ `apply-audio-schedule.mjs`
- **改 subtitleParts 条数后**：`realign-line.py <id>` → 再跑 `apply-audio-schedule.mjs`（见 `delivery-pitfalls.md`）
- **`speak` 规范**：数字+量词连写（`十三个`）；`generate-tts.py` 自动 `normalize_speak()`
- Edge TTS 单轨 `voiceover.wav` + 字幕与口播同步
- 品牌片尾：`off` / 变体 A·B·C / 自定义
- Agent 自动 TTS → **align-subtitles** → 时间轴、`npm run check`；**不自动 render**
- **交付自检**：`verify-delivery-checklist.py` + `verify-index-encoding.py` + `npm run check`（0 error）
- **版式硬性规则**：字幕单行、文字不重叠、**本地中文字体**、禁止 AI 风 emoji/表情包插图
