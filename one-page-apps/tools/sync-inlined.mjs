#!/usr/bin/env node
/* Keeps the kernel code inside the single-file tools of one-page-apps/ equal
   to the app's.

   A one-page app is one HTML file a person can save and open without a
   server. The pack builder still has to judge a pack exactly as the app's
   import does, so it carries the app's own code instead of a second port:
   the pure part of jascon-app/jascon-core.js (canonical form, digests, ZIP),
   jascon-app/jascon-schema.js (the kernel schema) and jascon-app/jascon-rules.js
   (the kernel rules). Each sits in the HTML between two markers:

     /* ==INLINE core== *\/ ... /* ==/INLINE core== *\/

   This script rewrites what lies between the markers from the sources.
   With --check it writes nothing and exits 1 if a file is out of date, which
   is what CI runs. Running it twice changes nothing the second time.

     node one-page-apps/tools/sync-inlined.mjs [--check] */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const read = rel => fs.readFileSync(path.join(ROOT, rel), "utf8");

/* What each region holds. The core's browser part (storage, page shell) is
   left out: it needs the app's page around it. */
const SOURCES = {
  core: () => {
    const text = read("jascon-app/jascon-core.js");
    const start = text.indexOf("/* ==JSC-PURE-START== */"), end = text.indexOf("/* ==JSC-PURE-END== */");
    if (start < 0 || end < start) throw new Error("jascon-core.js: the JSC-PURE markers are missing");
    return text.slice(start, end + "/* ==JSC-PURE-END== */".length);
  },
  schema: () => read("jascon-app/jascon-schema.js"),
  rules: () => read("jascon-app/jascon-rules.js"),
};
const TARGETS = ["one-page-apps/jascon-pack-builder.html"];

const check = process.argv.includes("--check");
let stale = 0;
for (const rel of TARGETS) {
  const file = path.join(ROOT, rel);
  const before = fs.readFileSync(file, "utf8");
  let after = before;
  for (const [key, source] of Object.entries(SOURCES)) {
    const open = `/* ==INLINE ${key}== */`, close = `/* ==/INLINE ${key}== */`;
    const a = after.indexOf(open), b = after.indexOf(close);
    if (a < 0) continue;                       // a tool carries only the regions it needs
    if (b < a) throw new Error(`${rel}: '${open}' has no closing marker`);
    const body = source();
    /* an inline script ends at the first "</script"; the sources must never contain one */
    if (/<\/script/i.test(body)) throw new Error(`${key}: the source contains "</script" and cannot be inlined`);
    after = after.slice(0, a + open.length) + "\n" + body + "\n" + after.slice(b);
  }
  if (after === before) { console.log(`${rel}: up to date`); continue; }
  stale++;
  if (check) console.log(`${rel}: OUT OF DATE - run node one-page-apps/tools/sync-inlined.mjs`);
  else { fs.writeFileSync(file, after); console.log(`${rel}: updated`); }
}
process.exit(check && stale ? 1 : 0);
