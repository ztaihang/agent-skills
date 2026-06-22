#!/usr/bin/env node
/**
 * 读取 content.json，生成 preview/*.html + publish/ 小红书文案
 * 用法：node scripts/build.mjs
 */
import fs from "fs/promises";
import path from "path";

const ROOT = process.cwd();
const PREVIEW = path.join(ROOT, "preview");
const PUBLISH = path.join(ROOT, "publish");
const FAMILY = path.join(ROOT, "families", "skill-list");

const THEMES = new Set(["soft-pink", "clean-white", "tool-slate", "dark-neon"]);
const CIRCLED = ["①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "⑩"];

const PREVIEW_NAV_CSS = `
html, body {
  width: auto !important;
  min-width: 1080px;
  height: auto !important;
  min-height: 1440px;
  overflow: auto !important;
}
.preview-nav {
  width: 1080px;
  box-sizing: border-box;
  padding: 20px 64px 40px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  font-family: system-ui, "PingFang SC", sans-serif;
  background: #0f172a;
  border-top: 1px solid #334155;
}
.preview-nav a {
  color: #94a3b8;
  text-decoration: none;
  font-size: 18px;
  padding: 10px 22px;
  border-radius: 8px;
  border: 1px solid #475569;
}
.preview-nav a:hover {
  color: #f1f5f9;
  background: #334155;
}
.preview-nav .preview-nav-index {
  flex: 1;
  text-align: center;
  border-color: #64748b;
}
.preview-nav .preview-nav-disabled {
  color: #475569;
  font-size: 18px;
  padding: 10px 22px;
  opacity: 0.45;
  user-select: none;
}
html.export-mode .preview-nav { display: none !important; }
`;

const PREVIEW_NAV_SCRIPT = `
<script>
(function () {
  if (new URLSearchParams(location.search).has("export")) {
    document.documentElement.classList.add("export-mode");
    return;
  }
  document.addEventListener("keydown", function (e) {
    if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
    var nav = document.querySelector(".preview-nav");
    if (!nav) return;
    var link = e.key === "ArrowLeft"
      ? nav.querySelector("a:first-of-type")
      : nav.querySelector("a:last-of-type");
    if (link && link.href) link.click();
  });
})();
</script>`;

function esc(s) {
  return String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function padNum(n) {
  return String(n).padStart(2, "0");
}

function defaultHashtags(content) {
  const tags = ["#AI工具推荐", "#Skill", "#Cursor"];
  if (content.highlight) {
    const h = String(content.highlight).replace(/\s+/g, "");
    if (h && !tags.some((t) => t.slice(1) === h)) tags.unshift(`#${h}`);
  }
  return tags;
}

/** 从 content.json 生成小红书标题与正文（与卡片 items 对齐，不含安装步骤） */
function buildXhsPublish(content) {
  const xhs = content.xhs ?? {};
  const title = xhs.title ?? content.subtitle ?? content.title;
  const footer = xhs.footer ?? "左滑看完 👉 收藏备用";
  const hashtags = xhs.hashtags ?? defaultHashtags(content);

  const blocks = [];
  if (xhs.intro) blocks.push(xhs.intro.trim());

  for (const item of content.items ?? []) {
    const num = CIRCLED[item.num - 1] ?? String(item.num);
    const tagLine = (item.tags ?? []).join(" · ");
    const head = tagLine ? `${num} ${item.name}｜${tagLine}` : `${num} ${item.name}`;
    blocks.push(`${head}\n${item.desc}`);
  }

  blocks.push(footer);
  if (hashtags.length) blocks.push(hashtags.join(" "));

  const description = blocks.join("\n");
  const combined = `=== 标题（≤20字，复制到小红书标题栏）===\n${title}\n\n=== 正文描述（复制到正文栏）===\n${description}\n`;

  return { title, description, combined };
}

async function writeXhsPublish(content) {
  const { title, description, combined } = buildXhsPublish(content);
  await fs.mkdir(PUBLISH, { recursive: true });
  await fs.writeFile(path.join(PUBLISH, "xhs-title.txt"), title + "\n", "utf8");
  await fs.writeFile(path.join(PUBLISH, "xhs-description.txt"), description + "\n", "utf8");
  await fs.writeFile(path.join(PUBLISH, "xhs-copy.txt"), combined, "utf8");
  return { title, description };
}

async function loadStyles(theme) {
  const base = await fs.readFile(path.join(FAMILY, "base.css"), "utf8");
  const themeFile = path.join(FAMILY, "themes", `${theme}.css`);
  let themeCss = "";
  try {
    themeCss = await fs.readFile(themeFile, "utf8");
  } catch {
    console.warn(`Theme "${theme}" not found, fallback soft-pink`);
    themeCss = await fs.readFile(path.join(FAMILY, "themes", "soft-pink.css"), "utf8");
  }
  return base + "\n" + themeCss;
}

function buildPageList(total) {
  return [
    "cover.html",
    ...Array.from({ length: total }, (_, i) => `card-${padNum(i + 1)}.html`),
  ];
}

function renderPreviewNav(currentFile, pageList) {
  const idx = pageList.indexOf(currentFile);
  const prev = idx > 0 ? pageList[idx - 1] : null;
  const next = idx < pageList.length - 1 ? pageList[idx + 1] : null;
  return `<nav class="preview-nav" aria-label="页面导航">
  ${prev ? `<a href="${prev}">← 上一页</a>` : `<span class="preview-nav-disabled">← 上一页</span>`}
  <a class="preview-nav-index" href="index.html">${idx + 1} / ${pageList.length} · 索引</a>
  ${next ? `<a href="${next}">下一页 →</a>` : `<span class="preview-nav-disabled">下一页 →</span>`}
</nav>`;
}

function wrapPage(title, css, body, navHtml = "") {
  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=1080" />
  <title>${esc(title)}</title>
  <style>${css}${PREVIEW_NAV_CSS}</style>
</head>
<body>
${body}
${navHtml}
${PREVIEW_NAV_SCRIPT}
</body>
</html>`;
}

function renderCover(content, css, navHtml = "") {
  const items = content.items ?? [];
  const badgePrefix = content.badgeEmoji ?? "";
  const divider = content.divider ?? "—— 必装技能清单 ——";
  const gridFixed = items
    .map((item) => {
      const tag = (item.tags && item.tags[0]) || "";
      const numLabel = CIRCLED[item.num - 1] ?? String(item.num);
      return `<div class="cover-grid-item">
  <div class="cover-grid-num">${numLabel}</div>
  <div class="cover-grid-name">${esc(item.name)}</div>
  ${tag ? `<div class="cover-grid-tag">${esc(tag)}</div>` : ""}
</div>`;
    })
    .join("\n");

  const body = `<div class="canvas">
  <div class="cover-badge">${badgePrefix}${esc(content.badge || "AI 工具推荐")}</div>
  <h1 class="cover-title">${esc(content.title)}</h1>
  <p class="cover-subtitle">${esc(content.subtitle)}</p>
  ${content.intro ? `<p class="cover-intro">${esc(content.intro)}</p>` : ""}
  ${content.highlight ? `<div class="cover-highlight">${esc(content.highlight)}</div>` : ""}
  <div class="cover-divider">${esc(divider)}</div>
  <div class="cover-grid">${gridFixed}</div>
</div>`;

  return wrapPage(content.title + " · 封面", css, body, navHtml);
}

function renderCard(item, index, total, css, scenesLabel = "适用场景", navHtml = "") {
  const tags = (item.tags || [])
    .map((t) => `<span class="card-tag">${esc(t)}</span>`)
    .join("\n    ");
  const body = `<div class="canvas card-canvas">
  <div class="card-inner">
    <div class="card-num">${item.num}</div>
    <h1 class="card-title">${esc(item.name)}</h1>
    <div class="card-tags">${tags}</div>
    <p class="card-desc">${esc(item.desc)}</p>
    ${item.scenes ? `<div class="card-footer">
      <p class="card-scenes">💡 ${esc(scenesLabel)}：${esc(item.scenes)}</p>
    </div>` : ""}
  </div>
</div>`;
  return wrapPage(item.name, css, body, navHtml);
}

function renderIndex(content, cardFiles) {
  const links = [
    `<li><a href="cover.html">封面 · ${esc(content.title)}</a></li>`,
    ...cardFiles.map(
      (f, i) =>
        `<li><a href="${f}">卡片 ${i + 1} · ${esc(content.items[i]?.name ?? f)}</a></li>`
    ),
  ].join("\n    ");
  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <title>预览索引 · ${esc(content.title)}</title>
  <style>
    body { font-family: system-ui, sans-serif; padding: 40px; background: #f5f5f5; }
    h1 { margin-bottom: 8px; }
    p.meta { color: #64748b; margin-bottom: 24px; }
    ul { list-style: none; padding: 0; }
    li { margin: 10px 0; }
    a { color: #2563eb; font-size: 18px; }
    .publish { margin-top: 32px; padding: 20px; background: #fff; border-radius: 12px; border: 1px solid #e2e8f0; }
    .publish h2 { font-size: 18px; margin-bottom: 12px; }
    .publish p { color: #64748b; font-size: 14px; margin-bottom: 8px; }
    .publish code { background: #f1f5f9; padding: 2px 6px; border-radius: 4px; }
  </style>
</head>
<body>
  <h1>${esc(content.title)}</h1>
  <p class="meta">1080×1440 静态预览 · theme: ${esc(content.theme || "soft-pink")}</p>
  <ul>
    ${links}
  </ul>
  <div class="publish">
    <h2>小红书文案</h2>
    <p>build 已生成，请打开项目根目录 <code>publish/</code>：</p>
    <ul>
      <li><code>xhs-title.txt</code> — 标题</li>
      <li><code>xhs-description.txt</code> — 正文描述</li>
      <li><code>xhs-copy.txt</code> — 标题 + 正文合并</li>
    </ul>
  </div>
</body>
</html>`;
}

async function main() {
  const contentPath = path.join(ROOT, "content.json");
  const raw = await fs.readFile(contentPath, "utf8");
  const content = JSON.parse(raw);

  if (content.type !== "skill-list") {
    console.error(`Unsupported type "${content.type}". P1 only supports skill-list.`);
    process.exit(1);
  }

  if (!content.title || !content.items?.length) {
    console.error("content.json 缺少 title 或 items");
    process.exit(1);
  }

  const theme = THEMES.has(content.theme) ? content.theme : "soft-pink";
  content.theme = theme;
  const css = await loadStyles(theme);

  await fs.mkdir(PREVIEW, { recursive: true });

  const total = content.items.length;
  const pageList = buildPageList(total);
  const scenesLabel = content.scenesLabel ?? "适用场景";

  await fs.writeFile(
    path.join(PREVIEW, "cover.html"),
    renderCover(content, css, renderPreviewNav("cover.html", pageList)),
    "utf8"
  );

  const cardFiles = [];
  for (let i = 0; i < total; i++) {
    const file = `card-${padNum(i + 1)}.html`;
    cardFiles.push(file);
    await fs.writeFile(
      path.join(PREVIEW, file),
      renderCard(
        content.items[i],
        i + 1,
        total,
        css,
        scenesLabel,
        renderPreviewNav(file, pageList)
      ),
      "utf8"
    );
  }

  await fs.writeFile(path.join(PREVIEW, "index.html"), renderIndex(content, cardFiles), "utf8");

  const xhs = await writeXhsPublish(content);

  console.log(`Built ${1 + total} pages → preview/ (theme: ${theme})`);
  console.log(`XHS copy → publish/`);
  console.log(`  标题: ${xhs.title}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
