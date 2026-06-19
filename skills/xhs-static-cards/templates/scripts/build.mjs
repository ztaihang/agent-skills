#!/usr/bin/env node
/**
 * 读取 content.json，生成 preview/*.html
 * 用法：node scripts/build.mjs
 */
import fs from "fs/promises";
import path from "path";

const ROOT = process.cwd();
const PREVIEW = path.join(ROOT, "preview");
const FAMILY = path.join(ROOT, "families", "skill-list");

const THEMES = new Set(["soft-pink", "clean-white", "tool-slate", "dark-neon"]);

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

function wrapPage(title, css, body) {
  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=1080" />
  <title>${esc(title)}</title>
  <style>${css}</style>
</head>
<body>
${body}
</body>
</html>`;
}

function renderCover(content, css) {
  const items = content.items ?? [];
  const circled = ["①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "⑩"];
  const badgePrefix = content.badgeEmoji ?? "";
  const divider = content.divider ?? "—— 必装技能清单 ——";
  const gridFixed = items
    .map((item) => {
      const tag = (item.tags && item.tags[0]) || "";
      const numLabel = circled[item.num - 1] ?? String(item.num);
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

  return wrapPage(content.title + " · 封面", css, body);
}

function renderCard(item, index, total, css, scenesLabel = "适用场景") {
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
  return wrapPage(item.name, css, body);
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
  </style>
</head>
<body>
  <h1>${esc(content.title)}</h1>
  <p class="meta">1080×1440 静态预览 · theme: ${esc(content.theme || "soft-pink")}</p>
  <ul>
    ${links}
  </ul>
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

  await fs.writeFile(path.join(PREVIEW, "cover.html"), renderCover(content, css), "utf8");

  const cardFiles = [];
  const total = content.items.length;
  const scenesLabel = content.scenesLabel ?? "适用场景";
  for (let i = 0; i < total; i++) {
    const file = `card-${padNum(i + 1)}.html`;
    cardFiles.push(file);
    await fs.writeFile(
      path.join(PREVIEW, file),
      renderCard(content.items[i], i + 1, total, css, scenesLabel),
      "utf8"
    );
  }

  await fs.writeFile(path.join(PREVIEW, "index.html"), renderIndex(content, cardFiles), "utf8");

  console.log(`Built ${1 + total} pages → preview/ (theme: ${theme})`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
