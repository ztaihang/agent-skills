# content.json Schema

## skill-list

```json
{
  "type": "skill-list",
  "theme": "soft-pink",
  "title": "Codex 必装 Skill 榜",
  "subtitle": "别再裸装了！这 9 个 Skills 让 AI 能力翻倍",
  "intro": "刚装 Codex 的时候我也是一脸懵…",
  "badge": "AI 工具推荐",
  "highlight": "TOP 9",
  "items": [
    {
      "num": 1,
      "name": "humanizer",
      "tags": ["去 AI 味", "内容质感"],
      "desc": "让 AI 生成的文字像真人写的，再也不怕被看出来是 AI。",
      "scenes": "社交媒体文案、邮件润色、文章改写"
    }
  ]
}
```

| 字段 | 必填 | 说明 |
|------|------|------|
| `type` | ✅ | 固定 `skill-list` |
| `theme` | | `soft-pink`（默认）\| `clean-white` \| `tool-slate` \| `dark-neon` |
| `title` | ✅ | 封面主标题 |
| `subtitle` | ✅ | 封面副标题 |
| `intro` | | 封面下方短引言 |
| `badge` | | 顶栏小标签，默认 `AI 工具推荐` |
| `badgeEmoji` | | 顶栏标签前 emoji，默认无（可设 `"🤖 "` 等） |
| `divider` | | 封面清单分隔文案，默认 `—— 必装技能清单 ——` |
| `scenesLabel` | | 卡片底部标签文案，默认 `适用场景` |
| `highlight` | | 封面强调块，如 `TOP 9` |
| `xhs` | | 小红书发布文案（build 自动生成 `publish/`） |
| `xhs.title` | | 发布标题（≤20 字，必填才可控；缺省用 `subtitle`） |
| `xhs.intro` | | 正文开头段落（可选；缺省不写，仅列 items） |
| `xhs.footer` | | 正文结尾，默认 `左滑看完 👉 收藏备用` |
| `xhs.hashtags` | | 话题数组，如 `["#A股", "#Skill"]` |
| `items` | ✅ | 至少 1 项 |
| `items[].num` | ✅ | 序号 |
| `items[].name` | ✅ | Skill 英文名或主标题 |
| `items[].tags` | | 1–3 个标签 |
| `items[].desc` | ✅ | 1–2 句描述 |
| `items[].scenes` | | 卡片底部补充信息（标签由 `scenesLabel` 控制） |

卡片页内容垂直居中，不显示页码（如 `1 / 5`）。

## 小红书文案（`npm run build` 自动生成）

正文描述**从 `items[]` 自动生成**（与卡片内容一致，不含安装步骤）：

```text
① 行情数据层｜tag1 · tag2
{items[].desc}
…
左滑看完 👉 收藏备用
#话题1 #话题2
```

输出目录 `publish/`：

| 文件 | 用途 |
|------|------|
| `xhs-title.txt` | 复制到小红书标题栏 |
| `xhs-description.txt` | 复制到正文描述栏 |
| `xhs-copy.txt` | 标题 + 正文合并备查 |

示例 `xhs` 字段：

```json
{
  "xhs": {
    "title": "别裸聊 A 股了！这个 Skill 真香",
    "footer": "左滑看完 👉 收藏备用",
    "hashtags": ["#a-stock-data", "#A股", "#AI炒股", "#Cursor", "#Skill"]
  }
}
```

Agent 解析文案时**必须填写 `xhs.title`**（小红书标题，可与封面 `title` 不同）；`xhs.hashtags` 按内容拟定；正文描述无需手写，由 build 从 items 生成。

## vibecoding（P3 占位）

```json
{
  "type": "vibecoding",
  "theme": "dark-terminal",
  "title": "Vibecoding 入门三步骤",
  "subtitle": "不用写代码也能出原型",
  "steps": []
}
```
