# 口播 / 字幕 / TTS 分离指南（Agent 写 lines.json 前必读）

> **核心原则：TTS 粒度由口播稿决定，不由字幕宽度决定。**  
> 字幕超长只拆「显示」，不拆「配音」。一条口播 wav 可对应多条顺序切换的字幕 `.sl`。

---

## 一、字段分工

| 字段 | 必填 | 用途 | 规则 |
|------|------|------|------|
| `id` | ✅ | 唯一标识 | **一条 id = 一个 wav**；禁止为字幕宽度拆成 s2a/s2b/s2c |
| `scene` | ✅ | 对应 HTML `scN` | 与镜头一一对应 |
| `voice` | ✅* | **TTS 口播整句** | 一条 = 一口气念完；保留标点含句末 |
| `text` | 兼容 | 同 `voice` | 旧项目可只写 `text`；新稿优先 `voice` |
| `speak` | 否 | **仅 TTS 念法** | 整句填写；按 id 逐行替换，**禁止全局替换** |
| `subtitle` | 否 | 底部字幕（字符串或数组） | **必须是 `voice` 的连续子串**（见 §1.1）；仅去句末标点 |
| `subtitleParts` | 否 | 显式字幕拆条 | 同上；不写则由脚本从 `voice` 自动按标点拆 |
| `display` | 否 | HTML 主文案参考 | 与口播解耦；Agent 写画面用 |
| `notes` | 否 | Agent 备注 | 不进 TTS |

\* 无 `voice` 时回退 `text`（兼容旧稿）。

### 1.1 强制对齐红线（Whisper 字幕同步）

本流程 **必须**跑 `align-subtitles.py`。此时字幕 **禁止缩写、改写、增删口播里没有的字**。

| 层 | 能否与口播不同 | 说明 |
|----|----------------|------|
| **`display` / 上屏大字** | ✅ 可以精简美化 | 卡片、标题不要求逐字 |
| **底部 `.sl` / `subtitleParts`** | ❌ **不可以改写** | 只能是 `voice` 按宽度拆开的 **连续片段** |

**规则：**

1. 每条 `subtitle` / `subtitleParts` 去掉句末标点后，必须能在 **`voice` 原文中按顺序找到**（可省略弯引号，不可换词）
2. 多条字幕拼接起来应 **覆盖整句口播**（仅允许省略句末 `。！？`）
3. **`speak` 只改 TTS 读音**，不改上屏；Whisper 对 **speak** 转写，边界仍用 **voice** 定位
4. 凡 **数字+量词**（「七个层级」「13 个数据源」）、**并列结构**、**专有名词** — **必须手写 `subtitleParts`**，不要依赖自动按宽度切字
5. 短句、标点清晰时可留空自动拆；交付前 `verify-delivery-checklist.py` 会 WARN 疑似 orphan 条（如单独「层级」）

**❌ 错误（会导致字幕与口播对不上）：**

```json
{
  "voice": "它完全不同于前段时间爆火、但连环境配置和打开软件都有些繁琐的「小龙虾」 OpenClaw。",
  "subtitleParts": [
    "它不同于前段时间爆火但配置繁琐",
    "小龙虾 OpenClaw 智能体"
  ]
}
```

**✅ 正确：**

```json
{
  "voice": "它完全不同于前段时间爆火、但连环境配置和打开软件都有些繁琐的「小龙虾」 OpenClaw。",
  "speak": "它完全不同于前段时间爆火、但连环境配置和打开软件都有些繁琐的「小龙虾」 Open Claw。",
  "subtitleParts": [
    "它完全不同于前段时间爆火",
    "但连环境配置和打开软件",
    "都有些繁琐的",
    "「小龙虾」 OpenClaw"
  ]
}
```

### 示例（推荐结构）

```json
[
  {
    "id": "s2",
    "scene": 2,
    "voice": "建议先点赞收藏，这些极具含金量的开源工具，迟早能让你的效率翻倍。",
    "speak": "建议先点赞收藏，这些极具含金辆的开源工具，迟早能让你的效率翻倍。",
    "subtitle": [
      "建议先点赞收藏",
      "这些极具含金量的开源工具",
      "迟早能让你的效率翻倍"
    ],
    "notes": "speak 用「辆」替「量」纠 liàng 音；无空格连写；字幕仍显示含金量"
  }
]
```

---

## 二、硬性禁止（Agent）

| ❌ 禁止 | ✅ 正确 |
|--------|--------|
| 为 maxHan 把一句口播拆成 s2a/s2b/s2c 并各自 TTS | 一条 `voice` + `subtitle`/`subtitleParts` 多条上屏 |
| 在「含金量」等词中间拆 TTS | 只在逗号/句号/完整子句处拆 **subtitle** |
| 全局替换 `speak` 字符串 | 按 **id 整行** 填写用户读音表 |
| 为迁就字幕删掉 `voice` 里的句号 | `voice` 保留标点给 Edge TTS 停顿 |
| **缩写/改写 subtitle**（如「之前须花几年学 Python」） | **subtitle 必须是 voice 连续子串**，只拆行不改词 |
| 只改 `speak`/`subtitle` 不重跑 TTS | 改 voice/speak/subtitle 后 **必须** generate-tts → align → apply |

---

## 三、标点分工

| 环节 | 标点 | 说明 |
|------|------|------|
| `voice` / `speak` | **保留含句末** | Edge TTS 靠标点控制停顿 |
| `subtitle` / `subtitleParts` | 上屏无句末标点 | `apply-audio-schedule.mjs` 自动 strip 末尾 `，。！？：；、` |
| `voice` 弯引号 `“”` | TTS 保留 | 字幕若省略引号（如 共享状态 无引号），对齐脚本会忽略引号；**推荐字幕不写引号、与口播语义一致** |
| 句中标点 | 字幕可保留 | 如「因此，全球」— 只 strip **末尾** |

---

## 四、动态单行字数上限（仅字幕显示层）

1. 用 `meta.json` 算 **`maxHan`**（横屏约 **16**，竖屏约 **12**）
2. **`voice` 超长** → **WARN**，TTS 仍整句一条 wav
3. **`subtitle` 每条** → 须 `visualUnits ≤ maxHan`；超长只在语义边界拆 **显示**
4. 公式：`visualUnits = 汉字数 + ascii×0.55`

### 自动拆上屏（无 subtitle 时）

`generate-tts.py` 把 `voice` 整句合成一条 wav；**优先** `align-subtitles.py`（faster-whisper 词级时间戳）写入 `audio/alignments.json`；`apply-audio-schedule.mjs` 读对齐结果写多条 `.sl`。若 Whisper **崩溃/无法安装**（常见于 Windows），改跑 **`fallback-alignments.py`**（speak+字数混合权重，**精度有限，须听检**）。无 `alignments.json` 时 `apply-audio-schedule` 才 inline 估算（不推荐交付）。

### 显式规划字幕（推荐长句）

Agent 写 `subtitle` 或 `subtitleParts` 比自动拆更可控：

```json
{
  "id": "s6",
  "scene": 4,
  "voice": "目前项目累计已经拿下超过 32000 个 Star，而且今天一天就狂涨了近 4000 颗星，足见社区对本地隐私 AI 的狂热。",
  "subtitle": [
    "目前项目累计已经拿下超过 32000 个 Star",
    "而且今天一天就狂涨了近 4000 颗星",
    "足见社区对本地隐私 AI 的狂热"
  ]
}
```

---

## 五、语义拆条规则（仅 subtitle，不拆 TTS）

### 5.1 允许断点

| 优先级 | 断点 |
|--------|------|
| P0 | 句号、问号、叹号后 |
| P1 | 分号、逗号后（子句完整） |
| P2 | 并列连词前（但/所以/因为/而且） |
| P3 | 话题切换 |

### 5.2 禁止断点（红线）

| 禁止 | 反例 |
|------|------|
| 量词/结构中间 | 「极具含金 \| 量的开源」 |
| 「的」字结构 | 「我的 \| 电脑」 |
| 专有名词中间 | 「Open \| Claw」 |
| 数字+单位 | 「100 \| 万」 |
| 量词结构 | 「七个 \| 层级」「十三 \| 个」 |
| 上条以虚词结尾 | 「…让我的」+「电脑…」 |

**注意：** 整句 `voice` 以逗号结尾是 **正常口播**，不算 ERROR；禁止断点校验只作用于 **subtitle 相邻条**。

---

## 六、TTS 读音（speak）

1. **改 `speak` 不改 `voice` / `subtitle`**（上屏永远正确汉字）
2. 用户读音表 → **按 id 逐行** 写入 `speak`，整句替换
3. **先试听 `voice`**：读对则 **不写 `speak`**；读错再补
4. `generate-tts.py` 对含英文且缺 `speak` 的行 WARN

### 6.1 同音字纠音（Edge TTS 读错时）

**目标：** 口播连贯，不在词中间出现怪停顿。

| ❌ 错误写法 | 问题 |
|------------|------|
| `含金 亮 的`（字两侧加空格） | Edge TTS 会在空格处 **顿一下**，听感碎 |
| `speak` 用 **多音字** 替代（如「亮」= liàng / liǎng） | 可能读成另一音，更不稳 |

| ✅ 推荐写法 | 说明 |
|------------|------|
| `speak` 整句 **无多余空格**，只替换个别字 | 保持一口气 |
| 用 **同音、非多音字** 替代 | 如「量 liàng」→「**辆**」（口语里几乎只读 liàng） |
| `voice` / 字幕仍写「含金量」 | 观众只看正确写法 |

**示例 — 「含金量」Edge 读错时：**

```json
{
  "voice": "这些极具含金量的开源工具，迟早能让你的效率翻倍。",
  "speak": "这些极具含金辆的开源工具，迟早能让你的效率翻倍。"
}
```

- TTS 念：「含金**辆**」→ 听感仍是 liàng，**中间无停顿**
- 字幕：「含金**量**」

**英文/缩写：** 词间加空格即可（如 `Open Claw`、`A I`），那是 **分词** 不是词内顿音：

```json
{
  "voice": "OpenClaw 不够聪明？",
  "speak": "Open Claw 不够聪明？"
}
```

**数字 + 量词（中文 speak）：** 连写，**禁止**在「个」前加空格（Edge TTS 会顿一下）：

```json
{
  "voice": "它把 13 个公开数据源和 28 个查询端点进行了打包合并。",
  "speak": "它把十三个公开数据源和二十八个查询端点进行了打包合并。"
}
```

- 字幕仍显示 `13 个` / `28 个`（来自 `voice` / `subtitleParts`）
- TTS 念「十三个」「二十八个」一口气读完
- `generate-tts.py` 会对 `speak` 自动 `normalize_speak()`（`十三 个` → `十三个`）

### 6.2 常见多音字（优先改 speak，勿改 voice）

| 字 | 场景 | speak 思路 |
|----|------|-----------|
| 量 | 含金量、含量 | 同音非多音字「辆」连写，**不加空格** |
| 行 | 银行、行业 | 试听；仍错再考虑 speak 整词替换或 SSML |
| 重 | 重要 / 重复 | 重要用「重」；重复可 speak「重复」确认读音 |
| 还 | 还是 / 归还 | 按语境换词或 SSML |
| 率 | 概率 / 效率 | 试听后 speak 或 SSML |

**禁止：** 在 `speak` 里用空格把词拦腰拆开（如 `含金 亮 的`）；**禁止** 字幕改成谐音字。

---

## 七、与上屏主文案的关系

| 层 | 规则 |
|----|------|
| **口播稿** | 用户稿子，拆镜 + TTS 依据 |
| **`voice`** | = 口播整句（一条 wav） |
| **上屏大字 / 卡片** | 可精简美化（`display` 或 design.md）；不要求与口播逐字一致 |
| **底部 `.sl`** | = `subtitle` 或从 **`voice` 派生**（连续子串）；单行；N 条共享 1 段 wav |

---

## 八、流水线步骤

| 步骤 | 行为 |
|------|------|
| 3d 写 lines.json | 先写 `voice` 整句；`subtitle` 单独规划或留空自动拆 |
| 5 TTS | 每行一个 wav（行数 = 口播句数） |
| **5b 强制对齐** | `align-subtitles.py`：每段 wav + `speak`/`voice` → `audio/alignments.json`（**字幕时间戳来源**） |
| 6 时间轴 | 口播 1 轨；字幕 N 条共享该段 `[start, showEnd]`，时间来自 alignments |

```bash
python scripts/generate-tts.py        # 校验 subtitle；voice 超长仅 WARN
python scripts/align-subtitles.py     # 首选：词级时间戳对齐 subtitleParts
# 若 align 崩溃 → python scripts/fallback-alignments.py  （权重估算，须听检）
node scripts/apply-audio-schedule.mjs # 读 alignments 写多条 .sl + GSAP
```

> **时间戳不在 TTS 里生成**：Edge TTS 只产出 wav；**对齐步骤**才从已生成的 wav 提取每个词何时说出，并映射到 `subtitleParts`。

---

## 九、交付前自检

- [ ] **口播句数 ≈ lines.json 条数 ≈ wav 段数**（除非用户明确一句拆两句口播）
- [ ] **无** s2a/s2b/s2c 式拆 TTS（`verify-delivery-checklist.py` 会 WARN）
- [ ] 每条 `subtitle`/`subtitleParts` 是 **`voice` 连续子串**（`generate-tts.py` 0 ERROR）
- [ ] 每条 `subtitle`/`subtitleParts` 子句 `visualUnits ≤ maxHan`
- [ ] **`voice` 保留 TTS 标点**；`.sl` 无句末标点
- [ ] 多音字/专有名词已查，`speak` 按 id 填写
- [ ] `generate-tts.py` **0 ERROR**（voice 超长 WARN 可接受）
- [ ] `audio/alignments.json` 存在且 `voiceoverHash` 与 `schedule.json` 一致
- [ ] 戴耳机：同 id 内多字幕切换与口播同步（长句尤其 spot-check）
- [ ] `matchRatio` 过低（如 <0.55）的行已听检或改 `speak`/口播稿
- [ ] 截帧：字幕无第二行、无长期 ellipsis

---

## 十、兼容旧稿（仅 `text`）

旧项目只有 `text` 时行为不变：`text` = TTS 口播；字幕由脚本从 `text` 自动拆显示。  
迁移时把 `text` 改名为 `voice` 并补上 `subtitle` 即可。
