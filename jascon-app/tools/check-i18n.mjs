/* Lists interface strings that have no German translation.

     node jascon-app/tools/check-i18n.mjs

   The English text is the key (see jscI18n in jascon-core.js), so a string
   without a translation shows as English and nothing breaks; this tool makes
   the gap visible. It reads every .html and .js file of the app and compares

     used:        the string literals in the first argument of T(…) and N(…),
                  the text of elements marked data-i18n, and the attributes
                  named in data-i18n-attr;
     translated:  the keys of every jscI18n.add("de", {…}) block.

   A string built at run time (T(variable)) cannot be seen here; mark its
   source with N("…"). Exit code 1 when something is missing. The same check
   runs as a test (tests/i18n.test.mjs). */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const APP = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

/* index just past the string literal that starts at src[i] (a quote) */
function skipString(src, i) {
  const q = src[i];
  for (let j = i + 1; j < src.length; j++) {
    if (src[j] === "\\") j++;
    else if (src[j] === q) return j + 1;
  }
  return src.length;
}
const literal = (src, a, b) => { try { return JSON.parse(src[a] === '"' ? src.slice(a, b) : null); } catch { return null; } };

/* string literals in the first argument of every T( and N( call */
function usedInCalls(src) {
  const out = [];
  const call = /(^|[^\w$.])[TN]\(/g;
  for (let m; (m = call.exec(src));) {
    let depth = 1;
    for (let i = call.lastIndex; i < src.length && depth > 0; i++) {
      const ch = src[i];
      if (ch === '"' || ch === "'" || ch === "`") {
        const end = skipString(src, i);
        const text = ch === '"' ? literal(src, i, end) : ch === "'" ? src.slice(i + 1, end - 1) : null;
        if (depth === 1 && text) out.push(text);
        i = end - 1;
      } else if ("([{".includes(ch)) depth++;
      else if (")]}".includes(ch)) depth--;
      else if (ch === "," && depth === 1) break;
    }
  }
  return out;
}
/* text of data-i18n elements and the attributes named in data-i18n-attr */
function usedInMarkup(src) {
  const out = [];
  const unescape = s => s.replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"');
  for (const m of src.matchAll(/<[a-z0-9]+\b[^>]*\bdata-i18n(?![-\w])[^>]*>([^<]*)</g)) {
    if (m[1].trim()) out.push(unescape(m[1].trim()));
  }
  for (const m of src.matchAll(/<[a-z0-9]+\b[^>]*\bdata-i18n-attr="([^"]*)"[^>]*>/g)) {
    for (const attr of m[1].split(/\s+/).filter(Boolean)) {
      const v = m[0].match(new RegExp(`\\s${attr}="([^"]*)"`));
      if (v && v[1]) out.push(unescape(v[1]));
    }
  }
  return out;
}
/* keys of every jscI18n.add("de", {…}) block; the block is an object literal
   of string keys and string values, so it is evaluated as one */
function translated(src) {
  const keys = new Set();
  const start = /jscI18n\.add\("de",\s*\{/g;
  for (let m; (m = start.exec(src));) {
    let depth = 1, i = start.lastIndex;
    for (; i < src.length && depth > 0; i++) {
      if (src[i] === '"' || src[i] === "'") i = skipString(src, i) - 1;
      else if (src[i] === "{") depth++;
      else if (src[i] === "}") depth--;
    }
    const table = new Function("return ({" + src.slice(start.lastIndex, i - 1) + "})")();
    Object.keys(table).forEach(k => keys.add(k));
  }
  return keys;
}

export function findMissing() {
  const files = fs.readdirSync(APP).filter(f => /\.(html|js)$/.test(f)).sort();
  const have = new Set(), used = new Map();
  for (const f of files) {
    const src = fs.readFileSync(path.join(APP, f), "utf8");
    translated(src).forEach(k => have.add(k));
    for (const s of [...usedInCalls(src), ...(f.endsWith(".html") ? usedInMarkup(src) : [])]) {
      if (!used.has(s)) used.set(s, f);
    }
  }
  /* a string with no letter in it (an arrow, a number) needs no translation */
  const missing = [...used].filter(([s]) => !have.has(s) && /\p{L}/u.test(s)).map(([text, file]) => ({ text, file }));
  return { files: files.length, used: used.size, translated: have.size, missing };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const r = findMissing();
  console.log(`${r.files} files, ${r.used} strings used, ${r.translated} translated, ${r.missing.length} without a German text`);
  for (const m of r.missing) console.log(`  ${m.file}: ${JSON.stringify(m.text)}`);
  process.exit(r.missing.length ? 1 : 0);
}
