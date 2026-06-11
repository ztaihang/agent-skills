import { readFileSync, writeFileSync, existsSync, copyFileSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";
import { get as httpGet } from "http";
import { get as httpsGet } from "https";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const brandPath = join(root, "assets/brand.json");
const htmlPath = join(root, "index.html");

if (!existsSync(brandPath)) {
  console.log("No assets/brand.json — skip apply-brand");
  process.exit(0);
}

const brand = JSON.parse(readFileSync(brandPath, "utf8"));
if (brand.outroMode === "off") {
  console.log("outroMode: off — skip apply-brand");
  process.exit(0);
}

function download(url, dest) {
  return new Promise((resolve, reject) => {
    const getter = url.startsWith("https") ? httpsGet : httpGet;
    getter(url, (res) => {
      if (res.statusCode && res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        download(res.headers.location, dest).then(resolve).catch(reject);
        return;
      }
      const chunks = [];
      res.on("data", (c) => chunks.push(c));
      res.on("end", () => {
        writeFileSync(dest, Buffer.concat(chunks));
        resolve(dest);
      });
      res.on("error", reject);
    }).on("error", reject);
  });
}

async function main() {
  const avatarOut = join(root, "assets/avatar.png");
  if (brand.avatarUrl && /^https?:\/\//i.test(brand.avatarUrl)) {
    await download(brand.avatarUrl, avatarOut);
    console.log(`Avatar → assets/avatar.png`);
  } else if (brand.avatarPath && existsSync(brand.avatarPath)) {
    copyFileSync(brand.avatarPath, avatarOut);
    console.log(`Avatar copied → assets/avatar.png`);
  }

  if (!brand.useDefaultOutro) {
    console.log("useDefaultOutro: false — avatar only, skip HTML patch");
    return;
  }

  let html = readFileSync(htmlPath, "utf8");
  let outroScene = brand.outroScene;
  if (!outroScene && existsSync(join(root, "audio/schedule.json"))) {
    const { schedule } = JSON.parse(readFileSync(join(root, "audio/schedule.json"), "utf8"));
    const scenes = schedule.map((l) => l.scene).filter((n) => n != null);
    if (scenes.length) outroScene = Math.max(...scenes);
  }
  outroScene = outroScene || 7;
  const p = `sc${outroScene}`;

  const patches = [
    [`${p}-title`, brand.outroTitle],
    [`${p}-follow`, brand.followText],
    [`${p}-sub`, brand.outroSub],
  ];
  for (const [id, text] of patches) {
    if (!text) continue;
    const re = new RegExp(`(<[^>]+id="${id}"[^>]*>)[^<]+`);
    if (re.test(html)) {
      html = html.replace(re, `$1${text}`);
      console.log(`Patched #${id}`);
    }
  }

  if (brand.channelName) {
    const chRe = /(<[^>]+id="[^"]*-channel"[^>]*>)[^<]+/;
    if (chRe.test(html)) {
      html = html.replace(chRe, `$1@${brand.channelName}`);
    }
  }

  writeFileSync(htmlPath, html);
  console.log(`Default outro patch done (scene ${outroScene})`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
