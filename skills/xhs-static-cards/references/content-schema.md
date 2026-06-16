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
| `theme` | | `soft-pink`（默认）\| `clean-white` \| `tool-slate` |
| `title` | ✅ | 封面主标题 |
| `subtitle` | ✅ | 封面副标题 |
| `intro` | | 封面下方短引言 |
| `badge` | | 顶栏小标签，默认 `AI 工具推荐` |
| `highlight` | | 封面强调块，如 `TOP 9` |
| `items` | ✅ | 至少 1 项 |
| `items[].num` | ✅ | 序号 |
| `items[].name` | ✅ | Skill 英文名或主标题 |
| `items[].tags` | | 1–3 个标签 |
| `items[].desc` | ✅ | 1–2 句描述 |
| `items[].scenes` | | 适用场景，逗号分隔 |

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
