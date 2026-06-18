import { readFileSync, writeFileSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const htmlPath = join(root, "index.html");
const data = JSON.parse(readFileSync(join(root, "audio/schedule.json"), "utf8"));
const { schedule, sceneTimes, totalDuration, subtitleMaxUnits = 16 } = data;

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
  return text.replace(/[，。！？：；、]+$/u, "").trim();
}

function visualUnits(text) {
  const plain = text.replace(/[，。！？：；、\s]+/gu, "");
  const han = (plain.match(/[\u4e00-\u9fff]/gu) || []).length;
  const ascii = (plain.match(/[\x00-\x7f]/g) || []).length;
  return han + ascii * 0.55;
}

function splitSubtitleDisplay(text, maxUnits) {
  const core = stripSubPunct(text);
  if (visualUnits(core) <= maxUnits) return [core];

  const rawParts = [];
  let buf = "";
  const segs = text.match(/[^，。！？、；]+[，。！？、；]?/gu) || [text];
  for (const seg of segs) {
    const candidate = buf + seg;
    if (visualUnits(stripSubPunct(candidate)) <= maxUnits) {
      buf = candidate;
    } else {
      if (buf.trim()) rawParts.push(stripSubPunct(buf));
      buf = seg;
    }
  }
  if (buf.trim()) rawParts.push(stripSubPunct(buf));
  const seeds = rawParts.length ? rawParts : [core];
  return seeds.flatMap((p) => splitPartUntilFit(p, maxUnits));
}

function splitPartUntilFit(text, maxUnits) {
  const core = stripSubPunct(text);
  if (!core) return [];
  if (visualUnits(core) <= maxUnits) return [core];

  for (const delim of ["，", "、", "；"]) {
    if (!core.includes(delim)) continue;
    const segs = core.split(delim);
    const parts = [];
    let buf = "";
    for (let i = 0; i < segs.length; i++) {
      const suffix = i < segs.length - 1 ? delim : "";
      const piece = segs[i] + suffix;
      const cand = buf + piece;
      if (visualUnits(stripSubPunct(cand)) <= maxUnits) {
        buf = cand;
      } else {
        if (buf.trim()) parts.push(stripSubPunct(buf));
        buf = piece;
      }
    }
    if (buf.trim()) parts.push(stripSubPunct(buf));
    if (parts.length && parts.every((p) => visualUnits(p) <= maxUnits)) return parts;
    if (parts.length) return parts.flatMap((p) => splitPartUntilFit(p, maxUnits));
  }

  return chunkByUnits(core, maxUnits);
}

function chunkByUnits(text, maxUnits) {
  const core = stripSubPunct(text);
  if (visualUnits(core) <= maxUnits) return [core];
  const parts = [];
  let buf = "";
  for (const ch of core) {
    const cand = buf + ch;
    if (visualUnits(cand) <= maxUnits) {
      buf = cand;
    } else {
      if (buf) parts.push(buf);
      buf = ch;
    }
  }
  if (buf) parts.push(buf);
  return parts.length ? parts : [core];
}

function subIdForPart(lineId, index) {
  if (index === 0) return lineId;
  return `${lineId}_${index + 1}`;
}

/** One schedule row (one wav) → N subtitle clips sharing [start, showEnd]. */
function buildSubEntries(line) {
  const parts =
    line.subtitleParts?.length > 0
      ? line.subtitleParts.map(stripSubPunct)
      : splitSubtitleDisplay(line.voice || line.text || "", subtitleMaxUnits);

  if (parts.length <= 1) {
    const dur = Math.max(0.001, +(line.duration - 0.001).toFixed(3));
    return [
      {
        id: line.id,
        start: line.start,
        showEnd: line.showEnd,
        duration: dur,
        text: parts[0] || stripSubPunct(line.voice || line.text || ""),
      },
    ];
  }

  const weights = parts.map((p) => Math.max(1, visualUnits(p)));
  const totalW = weights.reduce((a, b) => a + b, 0);
  let t = line.start;
  const end = line.showEnd;
  return parts.map((part, i) => {
    const partDur =
      i < parts.length - 1 ? ((end - t) * weights[i]) / totalW : end - t;
    const showEnd = i < parts.length - 1 ? t + partDur : end;
    const dur = Math.max(0.001, +(partDur - 0.001).toFixed(3));
    const entry = {
      id: subIdForPart(line.id, i),
      start: +t.toFixed(3),
      showEnd: +showEnd.toFixed(3),
      duration: dur,
      text: part,
    };
    t = showEnd;
    return entry;
  });
}

const allSubEntries = schedule.flatMap(buildSubEntries);

const durStr = String(totalDuration);
setAttrById("div", "root", "data-duration", durStr);
setAttrById("audio", "bgm", "data-duration", durStr);
setAttrById("audio", "voiceover", "data-duration", durStr);

for (const [sceneId, times] of Object.entries(sceneTimes)) {
  const sceneDur = Math.max(0.001, +(times.duration - 0.001).toFixed(3));
  const re = new RegExp(`(<div[^>]*id="${sceneId}"[^>]*)(>)`);
  html = html.replace(re, (match, prefix, close) => {
    if (!/\bclass="[^"]*\bclip\b/.test(prefix)) return match;
    let attrs = prefix.replace(/data-start="[^"]+"/, `data-start="${times.start}"`);
    attrs = attrs.replace(/data-duration="[^"]+"/, `data-duration="${sceneDur}"`);
    return attrs + close;
  });
}

function upsertSubBar(entry) {
  const subDur = entry.duration;
  const subRe = new RegExp(
    `(<div class="sub-bar clip" id="${entry.id}"[^>]*)(>\\s*<span class="sl">)[^<]+(</span>)`
  );
  const subReLegacy = new RegExp(
    `(<div class="sub-bar sl clip" id="${entry.id}"[^>]*)(>)[^<]+`
  );
  if (subRe.test(html)) {
    html = html.replace(subRe, (match, divPrefix, spanOpen, spanClose) => {
      let attrs = divPrefix.replace(/data-start="[^"]+"/, `data-start="${entry.start}"`);
      attrs = attrs.replace(/data-duration="[^"]+"/, `data-duration="${subDur}"`);
      return `${attrs}${spanOpen}${entry.text}${spanClose}`;
    });
    return;
  }
  if (subReLegacy.test(html)) {
    html = html.replace(subReLegacy, (match, prefix, close) => {
      let attrs = prefix.replace(/data-start="[^"]+"/, `data-start="${entry.start}"`);
      attrs = attrs.replace(/data-duration="[^"]+"/, `data-duration="${subDur}"`);
      return `${attrs}${close}${entry.text}`;
    });
    return;
  }
  const newBar = `  <div class="sub-bar clip" id="${entry.id}" data-start="${entry.start}" data-duration="${subDur}" data-track-index="20"><span class="sl">${entry.text}</span></div>\n`;
  if (html.includes("<!-- /subs -->")) {
    html = html.replace("<!-- /subs -->", `${newBar}<!-- /subs -->`);
  } else if (html.includes("<!-- narration audio -->")) {
    html = html.replace(
      "<!-- narration audio -->",
      `${newBar}<!-- narration audio -->`
    );
  }
}

for (const entry of allSubEntries) {
  upsertSubBar(entry);
}

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

const gsapLines = allSubEntries
  .map((entry) => {
    const fadeIn = entry.start;
    const fadeOut = entry.showEnd;
    return `mt.fromTo("#${entry.id}", {opacity:0,y:10}, {opacity:1,y:0,duration:0.14,ease:"power2.out",immediateRender:false}, ${fadeIn});\nmt.set("#${entry.id}", {opacity:0}, ${fadeOut});`;
  })
  .join("\n");

html = html.replace(
  /\/\/ Subtitle sync[\s\S]*?window\.__timelines\["main"\] = mt;/,
  `// Subtitle sync: one wav may drive N .sl clips (subtitleParts); zero gap between subs\n${gsapLines}\n\nwindow.__timelines["main"] = mt;`
);

writeFileSync(htmlPath, html);

const metaPath = join(root, "meta.json");
const meta = JSON.parse(readFileSync(metaPath, "utf8"));
meta.duration = totalDuration;
writeFileSync(metaPath, JSON.stringify(meta, null, 2) + "\n");

console.log(
  `Updated index.html — total ${totalDuration}s | ${schedule.length} TTS rows → ${allSubEntries.length} subtitle clips`
);
