#!/usr/bin/env node
/**
 * Playwright 导出 preview/*.html → output/*.png
 * 用法：node scripts/export.mjs
 */
import fs from "fs/promises";
import path from "path";
import { pathToFileURL } from "url";
import { chromium } from "playwright";

const ROOT = process.cwd();
const PREVIEW = path.join(ROOT, "preview");
const OUTPUT = path.join(ROOT, "output");

const WIDTH = 1080;
const HEIGHT = 1440;
const DPR = 2;

async function exportPage(browser, htmlFile, outFile) {
  const fileUrl = pathToFileURL(path.join(PREVIEW, htmlFile)).href;
  const page = await browser.newPage({
    viewport: { width: WIDTH, height: HEIGHT },
    deviceScaleFactor: DPR,
  });
  const exportUrl = fileUrl + (fileUrl.includes("?") ? "&" : "?") + "export=1";
  await page.goto(exportUrl, { waitUntil: "networkidle" });
  await page.waitForTimeout(300);
  await page.screenshot({
    path: outFile,
    clip: { x: 0, y: 0, width: WIDTH, height: HEIGHT },
  });
  await page.close();
  console.log(`  ✓ ${path.basename(outFile)}`);
}

async function main() {
  try {
    await fs.access(path.join(PREVIEW, "cover.html"));
  } catch {
    console.error("preview/ 不存在，请先运行: npm run build");
    process.exit(1);
  }

  await fs.mkdir(OUTPUT, { recursive: true });

  const files = await fs.readdir(PREVIEW);
  const cards = files.filter((f) => /^card-\d+\.html$/.test(f)).sort();

  const browser = await chromium.launch();

  try {
    console.log("Exporting PNG (1080×1440 @2x)…");
    await exportPage(browser, "cover.html", path.join(OUTPUT, "cover.png"));
    for (const card of cards) {
      const base = card.replace(".html", ".png");
      await exportPage(browser, card, path.join(OUTPUT, base));
    }
    console.log(`Done → ${OUTPUT}`);
  } finally {
    await browser.close();
  }
}

main().catch((err) => {
  console.error(err);
  if (String(err).includes("Executable doesn't exist")) {
    console.error("\n请先运行: npx playwright install chromium");
  }
  process.exit(1);
});
