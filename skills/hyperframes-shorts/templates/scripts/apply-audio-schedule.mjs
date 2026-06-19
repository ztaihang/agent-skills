import { readFileSync, writeFileSync, existsSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const htmlPath = join(root, "index.html");
const alignPath = join(root, "audio/alignments.json");
const data = JSON.parse(readFileSync(join(root, "audio/schedule.json"), "utf8"));
const { schedule, sceneTimes, totalDuration, subtitleMaxUnits = 16, voiceoverHash } = data;

let alignments = null;
if (existsSync(alignPath)) {
  const alignData = JSON.parse(readFileSync(alignPath, "utf8"));
  if (alignData.voiceoverHash === voiceoverHash) {
    alignments = alignData.lines;
  } else {
    console.warn(
      `alignments.json stale (hash ${alignData.voiceoverHash} != ${voiceoverHash}) — run: python scripts/align-subtitles.py`
    );
  }
} else {
  console.warn("audio/alignments.json missing — run: python scripts/align-subtitles.py");
}

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

function isIgnorableVoiceChar(ch) {
  return /[\s，。！？：；、\u201c\u201d\u2018\u2019「」『』"']/.test(ch);
}

function charsToMatch(text) {
  const out = [];
  for (const ch of text) {
    if (isIgnorableVoiceChar(ch)) continue;
    out.push(ch.toLowerCase());
  }
  return out;
}

function tokenAt(voice, vi) {
  const slice = voice.slice(vi);
  if (/^agent\b/i.test(slice)) return { text: "agent", len: slice.match(/^agent/i)[0].length };
  if (/^a[\s-]?i\b/i.test(slice)) return { text: "ai", len: slice.match(/^a[\s-]?i/i)[0].length };
  return null;
}

function normalizeFrom(voice, fromIdx) {
  let norm = "";
  const endAt = [];
  for (let i = fromIdx; i < voice.length; i++) {
    const ch = voice[i];
    if (isIgnorableVoiceChar(ch)) continue;
    const tok = tokenAt(voice, i);
    if (tok) {
      norm += tok.text;
      endAt.push(i + tok.len);
      i += tok.len - 1;
      continue;
    }
    norm += ch.toLowerCase();
    endAt.push(i + 1);
  }
  return { norm, endAt };
}

/** 在 voice 原文里顺序匹配 subtitlePart，返回该段结束位置 */
function findPartEndPos(voice, part, fromIdx) {
  const targets = charsToMatch(part).join("");
  if (!targets) return fromIdx;

  const { norm, endAt } = normalizeFrom(voice, fromIdx);
  const idx = norm.indexOf(targets);
  if (idx < 0) {
    const remaining = Math.max(1, voice.length - fromIdx);
    return Math.min(voice.length, fromIdx + Math.ceil((targets.length / Math.max(1, norm.length)) * remaining));
  }
  return endAt[idx + targets.length - 1] ?? voice.length;
}

function voicePartBoundaries(voice, parts) {
  let pos = 0;
  return parts.map((part) => {
    pos = findPartEndPos(voice, part, pos);
    return pos;
  });
}

function speakTimingWeight(text) {
  const raw = String(text || "");
  const han = (raw.match(/[\u4e00-\u9fff]/gu) || []).length;
  const ascii = (raw.match(/[\x00-\x7f]/g) || []).length;
  const spaces = (raw.match(/\s/g) || []).length;
  const hyphens = (raw.match(/-/g) || []).length;
  return Math.max(1, han + ascii * 0.95 + spaces * 0.55 + hyphens * 0.4);
}

function speakSegmentForPart(voice, speak, prevPos, currPos) {
  const vLen = Math.max(1, voice.length);
  const sLen = speak.length;
  const s0 = Math.floor((prevPos / vLen) * sLen);
  const s1 = Math.ceil((currPos / vLen) * sLen);
  return speak.slice(s0, Math.max(s1, s0 + 1));
}

function partWeights(line, parts, boundaries) {
  const voice = line.voice || line.text || "";
  const speak = line.speak || voice;
  return parts.map((part, i) => {
    const prevPos = i === 0 ? 0 : boundaries[i - 1];
    const currPos = boundaries[i];
    const seg = speakSegmentForPart(voice, speak, prevPos, currPos);
    const base = speak !== voice ? speakTimingWeight(seg) : speakTimingWeight(part);
    return Math.max(1, base);
  });
}

/** 对齐时间戳模式：Whisper 词级时间 + 极小缓冲 */
const ALIGNED_PAD_FIRST = 0.02;

function buildSubEntriesFromAlignment(line, parts) {
  const row = alignments?.[line.id];
  if (!row?.parts?.length) return null;
  if (row.parts.length !== parts.length) return null;

  const lineStart = line.start;
  const lineEnd = line.showEnd;

  return parts.map((part, i) => {
    const ap = row.parts[i];
    const relStart = Math.max(0, ap.start + (i === 0 ? ALIGNED_PAD_FIRST : 0));
    const relEnd =
      i < parts.length - 1
        ? row.parts[i + 1].start
        : (row.duration ?? lineEnd - lineStart);

    const start = +(lineStart + relStart).toFixed(3);
    const showEndR = +(lineStart + relEnd).toFixed(3);
    const cappedEnd = +Math.min(lineEnd, showEndR).toFixed(3);
    const dur = Math.max(0.001, +(cappedEnd - start - 0.003).toFixed(3));
    return {
      id: subIdForPart(line.id, i),
      start,
      showEnd: cappedEnd,
      duration: dur,
      text: part,
    };
  });
}

/** 无 alignments 时的估算参数（fallback） */
const SUB_LEAD_IN = 0.42;
const SUB_PART_LAG = 0.16;
const SUB_TAIL_PAD = 0.08;
function buildSubEntries(line) {
  const parts =
    line.subtitleParts?.length > 0
      ? line.subtitleParts.map(stripSubPunct)
      : splitSubtitleDisplay(line.voice || line.text || "", subtitleMaxUnits);

  if (alignments) {
    const aligned = buildSubEntriesFromAlignment(line, parts);
    if (aligned) return aligned;
  }

  if (parts.length <= 1) {
    const lineDur = line.showEnd - line.start;
    const leadIn = SUB_LEAD_IN + Math.min(0.24, lineDur * 0.032);
    const start = +(line.start + leadIn).toFixed(3);
    const dur = Math.max(0.001, +(line.showEnd - start - 0.003).toFixed(3));
    return [
      {
        id: line.id,
        start,
        showEnd: line.showEnd,
        duration: dur,
        text: parts[0] || stripSubPunct(line.voice || line.text || ""),
      },
    ];
  }

  const voice = line.voice || line.text || "";
  const boundaries = voicePartBoundaries(voice, parts);
  const lineStart = line.start;
  const lineEnd = line.showEnd;
  const lineDur = lineEnd - lineStart;
  const leadIn = SUB_LEAD_IN + Math.min(0.24, lineDur * 0.032);
  const baseLag = SUB_PART_LAG + Math.min(0.12, lineDur * 0.014);
  const tailPad = SUB_TAIL_PAD + Math.min(0.1, lineDur * 0.006);

  const weights = partWeights(line, parts, boundaries);
  const totalW = weights.reduce((a, b) => a + b, 0);
  const windowStart = lineStart + leadIn;
  const windowEnd = lineEnd - tailPad;
  const window = Math.max(0.5, windowEnd - windowStart);
  const minDur = Math.min(0.95, Math.max(0.35, (window / parts.length) * 0.52));

  const ends = [];
  let acc = windowStart;
  for (let i = 0; i < parts.length; i++) {
    acc += (weights[i] / totalW) * window;
    ends.push(+(Math.min(lineEnd, acc)).toFixed(3));
  }
  ends[parts.length - 1] = +lineEnd.toFixed(3);

  return parts.map((part, i) => {
    const idealStart = i === 0 ? windowStart : ends[i - 1];
    const lag =
      i > 0 ? Math.min(baseLag * (1 + (i - 1) * 0.04), Math.max(0.1, minDur * 0.28)) : 0;
    const longLag = lineDur > 5 ? Math.min(0.42, (lineDur - 5) * 0.028 * i) : 0;
    const showEndR = ends[i];
    let start = +(idealStart + lag + longLag).toFixed(3);
    if (start >= showEndR - 0.12) {
      start = +Math.max(idealStart, showEndR - Math.max(minDur, 0.32)).toFixed(3);
    }
    const dur = Math.max(0.001, +(showEndR - start - 0.003).toFixed(3));
    return {
      id: subIdForPart(line.id, i),
      start,
      showEnd: showEndR,
      duration: dur,
      text: part,
    };
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

function rewriteSubBlock(entries) {
  const bars = entries
    .map(
      (entry) =>
        `  <div class="sub-bar clip" id="${entry.id}" data-start="${entry.start}" data-duration="${entry.duration}" data-track-index="20"><span class="sl">${entry.text}</span></div>`
    )
    .join("\n");

  if (html.includes("<!-- subs -->") && html.includes("<!-- /subs -->")) {
    html = html.replace(
      /<!-- subs -->[\s\S]*?<!-- \/subs -->/,
      `<!-- subs -->\n${bars}\n<!-- /subs -->`
    );
    return;
  }

  for (const entry of entries) {
    upsertSubBar(entry);
  }
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

rewriteSubBlock(allSubEntries);

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
  /\/\/ Subtitle sync[\s\S]*?window\.__timelines\[["']main["']\] = mt;/,
  `// Subtitle sync: one wav may drive N .sl clips (subtitleParts); zero gap between subs\n${gsapLines}\n\nwindow.__timelines["main"] = mt;`
);

writeFileSync(htmlPath, html);

const metaPath = join(root, "meta.json");
const meta = JSON.parse(readFileSync(metaPath, "utf8"));
meta.duration = totalDuration;
writeFileSync(metaPath, JSON.stringify(meta, null, 2) + "\n");

console.log(
  `Updated index.html — total ${totalDuration}s | ${schedule.length} TTS rows → ${allSubEntries.length} subtitle clips${alignments ? " (forced-align)" : " (estimated)"}`
);
