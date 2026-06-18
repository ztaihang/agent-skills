# HyperFrames 短视频 · 用户提示词模板

复制对应区块发给 Agent 即可。Agent 自动跑 TTS、时间轴、`npm run check`；**你只需预览，确认后再导出**。

**项目路径**：你要存放 HyperFrames 工程的文件夹（任意本地路径），例如 `~/Videos/项目名` 或 `C:\Users\你\Videos\项目名`。下文 `<项目路径>` 均指此处填写的路径。

---

## 预览（唯一需要你手动执行的命令）

```powershell
cd "<项目路径>"
npm run dev
```

浏览器打开终端里的 Studio 地址，点播放检查字幕、口播、动效。

---

## 导出 MP4（预览满意后再执行）

```powershell
cd "<项目路径>"
npm run render
```

或指定输出文件名：

```powershell
npx hyperframes render -o "renders/项目名_v1.mp4"
```

导出文件默认在项目的 `renders/` 目录。

> Agent 默认**不会**自动 render；你说「导出」「render」「生成 MP4」后再执行。

---

## 标准提示词（带品牌片尾）

```markdown
请按 hyperframes-shorts → hyperframes → hyperframes-cli 制作视频。

项目路径：<你要存放视频的目录>/项目名
视频尺寸：1920×1080 横屏
总时长：（可选，不写就按口播估）
视觉风格：（可选，见下方预设；不写则 Agent 按口播 mood + 项目名自动轮换，保证与上一支不同）

taste 参数：（可选，短视频默认 5/6/6）
  DESIGN_VARIANCE 5 | MOTION_INTENSITY 6 | VISUAL_DENSITY 6

与上支错开：（可选）上一支用了 Data Drift + split 开场 + 片尾 A

可选视觉预设（来自 hyperframes visual-styles.md）：
  Swiss Pulse | Data Drift | Deconstructed | Shadow Cut
  Velvet Standard | Maximalist Type | Soft Signal | Folk Frequency

口播原文：
（正文，到总结结束即可——片尾句写在下方【品牌片尾】里，正文末尾不要重复）

【口播稿 · 仅 TTS】（可选单独块）
（一行一句，完整 breath；Agent 不得为字幕拆 TTS id）

【上屏/字幕文案 · 可选】（可与口播不同）
（页面标题、卡片、底部字幕；超长只在显示层拆，不增加 wav）

【读音表 speak · 整句替换，仅 TTS】（可选）
| id | speak（整句） |
|----|---------------|
| s2 | … |

【品牌片尾】
片尾样式：默认模板
频道名：浣熊不加班
头像：https://你的头像直链.webp（须 https；http 不下载）

片尾口播全文：
掌握 AI 实战，下班不留遗憾。关注浣熊不加班，我们下期见！

请：自动跑完全部环境与构建（含 taste-skill pre-flight、design.md + Motion Plan、TTS、时间轴、Post-audit、npm run check），我只需手动 npm run dev 预览；不要自动导出 MP4。

硬性版式（必须遵守）：
- 口播稿与上屏文案请分开提供；TTS 严格按口播稿整句生成，**禁止为字幕单行上限拆分 TTS**
- 底部字幕每条永远单行；超长只在逗号/句号处拆 **显示**（subtitle），不拆配音 wav
- lines.json：**voice** 整句 TTS；**subtitle** 仅上屏；**speak** 按 id 纠音，禁止全局替换
- TTS 保留标点（含句末）；上屏字幕不要句末标点（脚本自动处理）
- 多音字、英文、专有名词：`speak` 纠 TTS 读音，`voice`/字幕保持正确写法；**同音替代用非多音字（如量→辆），词内不加空格**
- 短口播镜须加副信息+ambient，禁止大面积空镜（见 scene-density-guide）
- 同场景上屏文字不得重叠遮挡
- 禁止 emoji 大图、AI 风表情包/3D 卡通插图；用 SVG/几何/数据 viz 装饰
- 动效：`#root` 静态背景 + 每镜 L1 stagger；数字对齐口播 L2；镜间转场轮换 L4（**禁止**每镜 infinite ambient）
```

| 字段 | 必填 | 不填时 |
|------|------|--------|
| 项目路径 | ✅ | 你要存放工程的本地目录 + 项目文件夹名 |
| 口播原文 | ✅ | — |
| 视频尺寸 | 否 | 默认 1920×1080 横屏 30fps |
| 总时长 | 否 | 按口播 + TTS 实测 |
| 视觉风格 | 否 | Agent 按 mood + 轮换选 `visual-styles.md` 预设，写 `design.md` + Motion Plan；**禁止**每支同一套科技蓝 UI |
| taste 参数 | 否 | 默认 DESIGN_VARIANCE 5 / MOTION 6 / DENSITY 6 |
| 与上支错开 | 否 | Agent 读 `style-history.json` 或项目名 hash 轮换 |
| 【品牌片尾】块 | 否 | **`outroMode: off`，完全不生成片尾** |
| 片尾样式 | 否 | 不写 = **默认模板**（金句+头像+关注） |
| 片尾口播全文 | 否* | *有片尾块时必填 |
| 频道名 / 头像 | 否* | *default 模式建议填 |

### 片尾三种模式（Agent 自动判断）

| 你怎么写 | 结果 |
|---------|------|
| 不写【品牌片尾】 | 无片尾镜、无片尾口播 |
| 写了【品牌片尾】 | 用**变体 A/B/C 之一**（按视觉风格自动选，非固定头像 zoom） |
| 写了 + `片尾样式：自定义` 或 `片尾说明：…` | **不用默认模板**，按你的说明单独做 |

详见 **`outro-rules.md`**

---

## 最小提示词（不要片尾）

```markdown
请按 hyperframes-shorts → hyperframes → hyperframes-cli 制作视频。

项目路径：<你要存放视频的目录>/项目名
视觉风格：Data Drift

口播原文：
（全文）

请：自动跑完全部环境与构建（含 design.md、TTS、时间轴、npm run check），我只需手动 npm run dev 预览；不要自动导出 MP4。
```

不写【品牌片尾】块 → `outroMode: off`，**完全不生成片尾**。

---

## 自定义片尾（不用默认模板）

```markdown
【品牌片尾】
片尾样式：自定义
片尾说明：不要头像，镜内两行大字居中（第一行 Slogan，第二行关注语）；**注意：指片尾画面布局，底部 `.sl` 字幕仍须单行**

频道名：浣熊不加班

片尾口播全文：
掌握 AI 实战，下班不留遗憾。关注浣熊不加班，我们下期见！
```

口播仍会念出；画面按「片尾说明」定制，**不走**默认金句 zoom + 头像模板。

---

## 只改片尾（单独发给 Agent）

```markdown
【品牌片尾】
频道名：浣熊不加班
头像：https://你的头像直链.webp（须 https；http 不下载）

片尾口播全文：
掌握 AI 实战，下班不留遗憾。关注浣熊不加班，我们下期见！
```

只需给「片尾口播全文」一行；Agent 自动拆句、写 TTS、同步 `brand.json`。

---

## Agent 交付话术（你会收到类似回复）

```text
项目已就绪：<项目路径>
实际时长：XXs | 场景：N 镜 | 校验：已通过（含 HTML 编码检查）

请预览（仅此一步）：
  cd "<项目路径>"
  npm run dev

预览满意后跟我说一声，我再帮你导出 MP4。
```

**不要**在交付话术里列出 `verify-index-encoding.py`、`npm run check`、TTS 等命令。

导出时你说「导出」或自己跑：

```powershell
cd "<项目路径>"
npm run render
```
