import { readFileSync, writeFileSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const htmlPath = join(root, "index.html");
const data = JSON.parse(readFileSync(join(root, "audio/schedule.json"), "utf8"));
const { schedule, sceneTimes, totalDuration } = data;

let html = readFileSync(htmlPath, "utf8");

function setAttrById(tag, id, attr, value) {
  const re = new RegExp(`(<${tag}[^>]*id="${id}"[^>]*)(>)`, "g");
  html = html.replace(re, (match, prefix, close) => {
    let attrs = prefix;
    if (new RegExp(`${attr}="[^"]*"`).test(attrs)) {
      attrs = attrs.replace(new RegExp(`${attr}="[^"]*"`), `${attr}="${value}"`);
    } else {
      attrs += ` ${attr}="${value}"`;
    }
    return attrs + close;
  });
}

function stripSubPunct(text) {
  return text.replace(/[，。！？：；、]+$/u, "");
}

const durStr = String(totalDuration);
setAttrById("div", "root", "data-duration", durStr);
setAttrById("audio", "bgm", "data-duration", durStr);
setAttrById("audio", "voiceover", "data-duration", durStr);

for (const [sceneId, times] of Object.entries(sceneTimes)) {
  const sceneDur = Math.max(0.001, +(times.duration - 0.001).toFixed(3));
  // Match scene clip by id — class may be "clip" or "clip scene"; attrs order may vary (Studio inserts data-hf-id)
  const re = new RegExp(`(<div[^>]*id="${sceneId}"[^>]*)(>)`);
  html = html.replace(re, (match, prefix, close) => {
    if (!/\bclass="[^"]*\bclip\b/.test(prefix)) return match;
    let attrs = prefix.replace(/data-start="[^"]+"/, `data-start="${times.start}"`);
    attrs = attrs.replace(/data-duration="[^"]+"/, `data-duration="${sceneDur}"`);
    return attrs + close;
  });
}

for (const line of schedule) {
  const display = stripSubPunct(line.text);
  const subDur = Math.max(0.001, +(line.duration - 0.001).toFixed(3));
  const subRe = new RegExp(`(<div class="sub-bar sl clip" id="${line.id}"[^>]*)(>)[^<]+`);
  html = html.replace(subRe, (match, prefix, close) => {
    let attrs = prefix.replace(/data-start="[^"]+"/, `data-start="${line.start}"`);
    attrs = attrs.replace(/data-duration="[^"]+"/, `data-duration="${subDur}"`);
    return `${attrs}${close}${display}`;
  });
}

// Plain src — voiceover.wav?v=hash breaks hyperframes validate (404). Hard-refresh Studio after TTS rerun.
const voiceBlock = `<audio id="voiceover" class="clip" data-start="0" data-duration="${durStr}" data-track-index="5" data-volume="1" src="audio/voiceover.wav"></audio>`;

if (html.includes("<!-- narration audio -->")) {
  html = html.replace(
    /<!-- narration audio -->[\s\S]*?<!-- \/narration audio -->/,
    `<!-- narration audio -->\n${voiceBlock}\n<!-- /narration audio -->`
  );
} else {
  html = html.replace(
    "</div>\n<script>",
    `</div>\n<!-- narration audio -->\n${voiceBlock}\n<!-- /narration audio -->\n<script>`
  );
}

const gsapLines = schedule
  .map((line) => {
    const fadeIn = line.start;
    const fadeOut = line.showEnd;
    return `mt.fromTo("#${line.id}", {opacity:0,y:10}, {opacity:1,y:0,duration:0.14,ease:"power2.out",immediateRender:false}, ${fadeIn});\nmt.set("#${line.id}", {opacity:0}, ${fadeOut});`;
  })
  .join("\n");

html = html.replace(
  /\/\/ Subtitle sync[\s\S]*?window\.__timelines\["main"\] = mt;/,
  `// Subtitle sync: TTS duration, zero gap; on-screen text strips trailing punct\n${gsapLines}\n\nwindow.__timelines["main"] = mt;`
);

writeFileSync(htmlPath, html);

const metaPath = join(root, "meta.json");
const meta = JSON.parse(readFileSync(metaPath, "utf8"));
meta.duration = totalDuration;
writeFileSync(metaPath, JSON.stringify(meta, null, 2) + "\n");

console.log(`Updated index.html — total ${totalDuration}s`);
