import { readFileSync, writeFileSync, existsSync, copyFileSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";
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
    httpsGet(url, (res) => {
      if (res.statusCode && res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        const next = res.headers.location;
        if (!/^https:\/\//i.test(next)) {
          reject(new Error(`[apply-brand] 头像重定向到非 https 地址，已拒绝: ${next}`));
          return;
        }
        download(next, dest).then(resolve).catch(reject);
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
  if (brand.avatarUrl) {
    const url = brand.avatarUrl.trim();
    if (/^https:\/\//i.test(url)) {
      await download(url, avatarOut);
      console.log(`Avatar → assets/avatar.png`);
    } else if (/^http:\/\//i.test(url)) {
      console.warn(
        "[apply-brand] 头像地址必须是 https，已跳过 http 下载。请改用 https 链接，或将图片放到 assets/avatar.png，或在 brand.json 使用 avatarPath 本地路径。"
      );
    } else {
      console.warn(
        "[apply-brand] avatarUrl 不是有效 https 链接，已跳过下载。请使用 https://... 或 avatarPath / assets/avatar.png。"
      );
    }
  } else if (brand.avatarPath && existsSync(brand.avatarPath)) {
    copyFileSync(brand.avatarPath, avatarOut);
    console.log(`Avatar copied → assets/avatar.png`);
  } else if (existsSync(avatarOut)) {
    console.log("Using existing assets/avatar.png");
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
