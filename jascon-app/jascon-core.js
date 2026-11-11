/* JASCON-App shared core.

   Every page of the app loads this file with <script src="jascon-core.js">;
   it has to sit next to the HTML files. It gives the pages one way to do the
   things they all do: hold a bundle, read and write its objects, verify and
   produce the content manifest, show a shell with navigation and a log, and
   speak two languages.

   Data flow. A "set" is one working bundle. It lives in IndexedDB as one
   record per bundle file, with the file's text exactly as it arrived. A page
   calls jscSet.load(), gets a graph (objects by id, manifest, pinned scales
   and facet schemas), works on it and writes objects back with
   jscSet.saveObjects(). Every write tells the other open pages, which reload.
   jscBuildBundle() turns a graph back into bundle files.

   Invariants the code relies on:
   - A file that was imported and not changed is stored and exported byte for
     byte. Package digests are over bytes, so nothing here re-serialises an
     imported file.
   - An object the app wrote is serialised by jscSerialize() and nowhere else.
   - Exporting twice gives the same bytes: the manifest carries no clock time,
     and a bundle nobody changed leaves with the manifest it came with.

   The file has two parts. The first, between JSC-PURE-START and JSC-PURE-END,
   touches neither the DOM nor storage and runs in node, where the tests load
   it. The second part needs a browser.

   Not here: the kernel rules (jascon-rules.js), anything specific to one
   page, and collaboration between users.

   Storage, ZIP, theme and list filter derive from gpp-core.js of the
   Grundschutz++ OSCAL tools; canonical form, digests, type inference and
   bundle loading derive from the JASCON bundle reader. Both Apache-2.0, see
   NOTICE. */
"use strict";

/* ==JSC-PURE-START== */

const JSC_BUILD = "0.9.1";
const JSC_TOOL = "JASCON-App " + JSC_BUILD;
/* The kernel this app writes, and the kernels it reads (KERNEL-2: a tool
   stops at a pin it does not implement and names both). */
const JSC_KERNEL = "2.0.0";
const JSC_KERNEL_READS = ["1.0.0", "2.0.0"];

const JSC_TYPES = ["requirement", "requirementSet", "tailoring", "mapping", "component",
  "implementation", "risk", "check", "assessment", "finding", "attestation"];
const JSC_TYPE_DIR = { requirement: "req", requirementSet: "set", tailoring: "tailoring",
  mapping: "map", component: "comp", implementation: "impl", risk: "risk", check: "check",
  assessment: "asmt", finding: "finding", attestation: "att" };
const JSC_MANIFEST = "content-manifest.json";

/* Marks a string for translation at a place where it is translated later
   (a table of tools, say). tools/check-i18n.mjs reads N("…") like T("…"). */
const N = s => s;

/* ---------- configuration ----------
   One definition of every setting. config.html renders its form from this
   list and tools/gen-docs.mjs writes the readme table from it, so the three
   cannot disagree. Values live in localStorage; none of them is a secret. */
const JSC_CFG = [
  { key: "ui:lang", def: "", choices: ["", "en", "de"],
    label: N("Language of the interface"), help: N("Empty follows the browser.") },
  { key: "ui:contentlang", def: "", choices: null,
    label: N("Language of the content"), help: N("BCP-47 tag picked from the language maps of a bundle, for example de. Empty follows the interface.") },
  { key: "ui:theme", def: "dark", choices: ["dark", "light", "system"],
    label: N("Colour scheme"), help: N("System follows the operating system.") },
  { key: "org:ns", def: "https://example.org/my", choices: null,
    label: N("Namespace for new objects"), help: N("The URI under which this app mints ids, for example https://your.example. Use a name you control.") },
  { key: "org:owner", def: "", choices: null,
    label: N("Default risk owner"), help: N("A party URI, for example https://your.example/party/ciso. Prefilled when a risk is created.") },
  /* Model access (jascon-ai.js). The key of a service is not a setting: it
     is typed on the page that calls the model and held in memory only. */
  { key: "ai:backend", def: "gemini", choices: ["gemini", "openrouter", "openai"],
    label: N("Model service"), help: N("gemini is Google's API, openrouter is OpenRouter, openai is an endpoint of your own that speaks the OpenAI chat-completions protocol. No model is called until you type a key on a page that offers suggestions.") },
  { key: "ai:model:gemini", def: "gemini-3.8-flash", choices: null,
    label: N("Model at Google Gemini"), help: N("A model id of the Gemini API, for example gemini-3.8-flash, gemini-3.5-flash-lite or gemini-4-argon (no free tier). Check the id against Google's model list; ids are retired.") },
  { key: "ai:model:openrouter", def: "", choices: null,
    label: N("Model at OpenRouter"), help: N("A model slug in the form vendor/model. The model must support structured outputs.") },
  { key: "ai:model:openai", def: "", choices: null,
    label: N("Model at your own endpoint"), help: N("The model name your endpoint expects.") },
  { key: "ai:base:openai", def: "", choices: null,
    label: N("Base URL of your own endpoint"), help: N("For example https://llm.your.example/v1. The app calls /chat/completions under it and sends the key as a bearer token.") },
  { key: "ai:thinking", def: "medium", choices: ["low", "medium", "high", "minimal"],
    label: N("Thinking level"), help: N("Gemini only. minimal exists on gemini-3.6-flash and gemini-3.5-flash-lite; on every other model it is sent as low.") },
  { key: "ai:retries", def: "2", choices: null,
    label: N("Retries per call"), help: N("How often a call is repeated after a rate limit, a server error, a timeout or an answer of the wrong shape. 0 to 5.") },
  { key: "ai:concurrency", def: "3", choices: null,
    label: N("Calls at the same time"), help: N("1 to 8. Lower it when the service answers with rate limits.") },
  { key: "ai:chunk", def: "400", choices: null,
    label: N("Requirements per call"), help: N("How many candidate requirements one call carries when treatments are suggested. A larger selection is cut into several calls per risk. 20 to 2000.") },
];

const jscEsc = s => String(s ?? "").replace(/[&<>"']/g,
  c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const jscSlug = s => String(s || "").toLowerCase().replace(/[^a-z0-9]+/g, "-")
  .replace(/^-+|-+$/g, "").slice(0, 60) || "x";
const jscToday = () => new Date().toISOString().slice(0, 10);

/* ---------- text primitive ----------
   Kernel prose is a language map {"en": "...", "de": "..."}; a value may be a
   string or a list of strings. jscText picks the wanted language, then
   English, then whatever is there. */
function jscText(v, lang) {
  if (v == null) return "";
  if (typeof v === "string") return v;
  if (Array.isArray(v)) return v.join(" ");
  if (typeof v !== "object") return String(v);
  const pick = v[lang] ?? v[String(lang || "").split("-")[0]] ?? v.en ?? Object.values(v)[0];
  return Array.isArray(pick) ? pick.join(" ") : String(pick ?? "");
}

/* ---------- type inference ----------
   The kernel has no type field; the reference validator asks which schema an
   object matches. This is the cheap signature test the reader used, kept
   until jascon-rules.js replaces it with schema matching. Order matters:
   the more specific signatures come first. */
function jscInferType(o) {
  if (!o || typeof o !== "object" || Array.isArray(o)) return null;
  if ("manifest-version" in o) return "manifest";
  if ("statements" in o) return "requirement";
  if ("observes" in o && "criteria" in o) return "check";   // before Implementation: a Check has a requirement-ref too
  if ("selects" in o) return "tailoring";
  if ("source-ref" in o && "target-ref" in o) return "mapping";
  if ("kind" in o) return "component";
  if ("component-ref" in o && "requirement-ref" in o && "responsibility" in o) return "implementation";
  if ("subject-refs" in o && "method" in o) return "assessment";
  if ("assessment-ref" in o && "state" in o) return "finding";
  if ("scenario" in o && "owner-ref" in o) return "risk";
  if ("subject-semantic-digests" in o) return "attestation";
  if ("members" in o) return "requirementSet";
  return null;
}
const jscIsScale = o => !!o && typeof o === "object" && Array.isArray(o.levels) &&
  typeof o.id === "string" && jscInferType(o) === null;
const jscIsFacetDescriptor = o => !!o && typeof o === "object" && typeof o.id === "string" &&
  "schema" in o && "modifies-semantics" in o;

/* ---------- canonical form and digests ----------
   Semantic digest: SHA-256 over the canonical form, which is the object
   without its top-level `annotations`, keys sorted, no whitespace. Key order
   is JavaScript's default string order (UTF-16 code units), the same order
   the Python validator sorts by. Numbers: JSON.stringify writes 1.0 as 1
   where Python writes 1.0; kernel content carries decimals as strings for
   that reason, so the two agree on everything the schema allows. */
function jscCanonical(obj) {
  const sort = o => {
    if (Array.isArray(o)) return o.map(sort);
    if (o && typeof o === "object") {
      const out = {};
      for (const k of Object.keys(o).sort()) out[k] = sort(o[k]);
      return out;
    }
    return o;
  };
  const top = {};
  for (const k of Object.keys(obj)) if (k !== "annotations") top[k] = obj[k];
  return JSON.stringify(sort(top));
}
const jscUtf8 = text => new TextEncoder().encode(text);
async function jscSha256(data) {
  const bytes = typeof data === "string" ? jscUtf8(data) : data;
  const subtle = typeof crypto !== "undefined" && crypto.subtle;
  if (!subtle) return jscSha256Js(bytes);
  const h = await subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(h), b => b.toString(16).padStart(2, "0")).join("");
}
/* Pure-JS SHA-256 for pages opened from file://, where some browsers give no
   crypto.subtle. */
function jscSha256Js(bytes) {
  const K = [0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
  let H = [0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
  const len = bytes.length, bitLen = len * 8;
  const padded = new Uint8Array(((len + 8) >> 6 << 6) + 64);
  padded.set(bytes); padded[len] = 0x80;
  new DataView(padded.buffer).setUint32(padded.length - 4, bitLen >>> 0);
  new DataView(padded.buffer).setUint32(padded.length - 8, Math.floor(bitLen / 0x100000000));
  const w = new Int32Array(64), rr = (x, n) => (x >>> n) | (x << (32 - n));
  for (let i = 0; i < padded.length; i += 64) {
    const dv = new DataView(padded.buffer, i, 64);
    for (let t = 0; t < 16; t++) w[t] = dv.getUint32(t * 4);
    for (let t = 16; t < 64; t++) {
      const s0 = rr(w[t-15],7) ^ rr(w[t-15],18) ^ (w[t-15] >>> 3);
      const s1 = rr(w[t-2],17) ^ rr(w[t-2],19) ^ (w[t-2] >>> 10);
      w[t] = (w[t-16] + s0 + w[t-7] + s1) | 0;
    }
    let [a,b,c,d,e,f,g,h] = H;
    for (let t = 0; t < 64; t++) {
      const S1 = rr(e,6) ^ rr(e,11) ^ rr(e,25), ch = (e & f) ^ (~e & g);
      const t1 = (h + S1 + ch + K[t] + w[t]) | 0;
      const S0 = rr(a,2) ^ rr(a,13) ^ rr(a,22), maj = (a & b) ^ (a & c) ^ (b & c);
      const t2 = (S0 + maj) | 0;
      h=g; g=f; f=e; e=(d+t1)|0; d=c; c=b; b=a; a=(t1+t2)|0;
    }
    H = H.map((x, j) => (x + [a,b,c,d,e,f,g,h][j]) | 0);
  }
  return H.map(x => (x >>> 0).toString(16).padStart(8, "0")).join("");
}
const jscPackageDigest = async text => "sha256:" + await jscSha256(text);
const jscSemanticDigest = async obj => "sha256:" + await jscSha256(jscCanonical(obj));

/* The one serialisation of an object this app writes. */
const jscSerialize = obj => JSON.stringify(obj, null, 1) + "\n";

/* ---------- from files to a graph ----------
   A bundle arrives as a list of {path, text}. Three steps:
   jscNormalizePaths cuts the folder the manifest sits in off every path,
   jscClassifyFiles says what each file is, jscGraphFrom builds the index the
   pages work on. Each step isolates a bad file as a problem entry and goes
   on; only an unsupported kernel pin stops the load. */
function jscNormalizePaths(files) {
  const manifests = files.map(f => f.path).filter(p => p === JSC_MANIFEST || p.endsWith("/" + JSC_MANIFEST));
  if (!manifests.length) return { files, dropped: 0 };
  const prefix = manifests.sort((a, b) => a.length - b.length)[0].slice(0, -JSC_MANIFEST.length);
  const inside = files.filter(f => f.path.startsWith(prefix));
  return { files: inside.map(f => ({ ...f, path: f.path.slice(prefix.length) })), dropped: files.length - inside.length };
}

class JscKernelError extends Error {}

function jscCheckKernelPin(manifest) {
  const pin = manifest && manifest["kernel-version"];
  if (pin && !JSC_KERNEL_READS.includes(pin)) {
    throw new JscKernelError(`manifest pins kernel-version ${pin}; this app implements ${JSC_KERNEL} ` +
      `and reads ${JSC_KERNEL_READS.join(", ")} (KERNEL-2)`);
  }
}

/* -> { records: [{path, text, kind, type, id}], problems: [string] }
   kind: manifest | object | scale | facet-schema | aux */
function jscClassifyFiles(files) {
  const problems = [];
  let manifest = null;
  const manFile = files.find(f => f.path === JSC_MANIFEST);
  if (manFile) {
    try { manifest = JSON.parse(manFile.text); }
    catch (e) { problems.push(`${JSC_MANIFEST}: not JSON (${e.message}); loading the files without integrity data`); }
  }
  jscCheckKernelPin(manifest);
  const pinned = key => new Set(((manifest && manifest[key]) || []).map(e => e && e.path).filter(Boolean));
  const facetPaths = pinned("facet-schemas"), scalePaths = pinned("scales");
  const records = [];
  for (const f of files) {
    const rec = { path: f.path, text: f.text, kind: "aux", type: null, id: null };
    records.push(rec);
    if (f.path === JSC_MANIFEST) { rec.kind = "manifest"; continue; }
    if (!f.path.endsWith(".json")) continue;
    let json;
    try { json = JSON.parse(f.text); }
    catch (e) { problems.push(`${f.path}: not JSON (${e.message})`); continue; }
    const type = jscInferType(json);
    if (facetPaths.has(f.path) || (!type && jscIsFacetDescriptor(json))) { rec.kind = "facet-schema"; rec.id = json.id || null; }
    else if (scalePaths.has(f.path) || jscIsScale(json)) { rec.kind = "scale"; rec.id = json.id || null; }
    else if (type && type !== "manifest") { rec.kind = "object"; rec.type = type; rec.id = json.id || f.path; }
  }
  return { records, problems };
}

/* -> graph {
     manifest, manifestText,
     objects: Map(id -> {obj, type, path, text, origin, entry}), order: [id],
     scales: Map(id -> {def, path, text, pin}),
     facetSchemas: [{def, path, text, pin}], aux: [{path, text}], problems }
   `entry` and `pin` are the manifest's lines for that file, or null.
   `order` is manifest order, then everything the manifest does not list,
   by path. */
function jscGraphFrom(records) {
  const g = { manifest: null, manifestText: null, objects: new Map(), order: [],
    scales: new Map(), facetSchemas: [], aux: [], problems: [] };
  const man = records.find(r => r.kind === "manifest");
  if (man) {
    g.manifestText = man.text;
    try { g.manifest = JSON.parse(man.text); } catch (e) { g.problems.push(`${JSC_MANIFEST}: not JSON`); }
  }
  const lines = key => new Map(((g.manifest && g.manifest[key]) || []).map(e => [e.path, e]));
  const objLines = lines("objects"), facetLines = lines("facet-schemas"), scaleLines = lines("scales");
  const byPath = new Map();
  for (const r of records) {
    if (r.kind === "manifest") continue;
    if (r.kind === "aux") { g.aux.push({ path: r.path, text: r.text }); continue; }
    let json;
    try { json = JSON.parse(r.text); } catch (e) { g.problems.push(`${r.path}: not JSON`); continue; }
    if (r.kind === "scale") {
      g.scales.set(json.id, { def: json, path: r.path, text: r.text, pin: scaleLines.get(r.path) || null });
    } else if (r.kind === "facet-schema") {
      g.facetSchemas.push({ def: json, path: r.path, text: r.text, pin: facetLines.get(r.path) || null });
    } else {
      const id = json.id || r.path;
      if (g.objects.has(id)) { g.problems.push(`${r.path}: id ${id} is already defined by ${g.objects.get(id).path}; second file ignored`); continue; }
      g.objects.set(id, { obj: json, type: r.type || jscInferType(json), path: r.path, text: r.text,
        origin: r.origin || "imported", entry: objLines.get(r.path) || null });
      byPath.set(r.path, id);
    }
  }
  /* Pinned files in the manifest's order, the unpinned after them by path:
     a re-export then lists them the way they arrived. */
  const inManifestOrder = (items, lineMap) => {
    const rank = new Map([...lineMap.keys()].map((p, i) => [p, i]));
    const at = x => (rank.has(x.path) ? rank.get(x.path) : rank.size);
    return [...items].sort((a, b) => at(a) - at(b) || (a.path < b.path ? -1 : a.path > b.path ? 1 : 0));
  };
  g.facetSchemas = inManifestOrder(g.facetSchemas, facetLines);
  g.scales = new Map(inManifestOrder([...g.scales.values()], scaleLines).map(x => [x.def.id, x]));
  const listed = [...objLines.keys()].map(p => byPath.get(p)).filter(Boolean);
  const seen = new Set(listed);
  const pathOf = id => g.objects.get(id).path;
  const rest = [...g.objects.keys()].filter(id => !seen.has(id))
    .sort((a, b) => (pathOf(a) < pathOf(b) ? -1 : pathOf(a) > pathOf(b) ? 1 : 0));
  g.order = [...listed, ...rest];
  const missing = [...objLines.keys()].filter(p => !byPath.has(p));
  if (missing.length) g.problems.push(`${missing.length} manifest entries have no file (first: ${missing[0]})`);
  return g;
}

function jscTypeCounts(g) {
  const c = {};
  for (const r of g.objects.values()) c[r.type] = (c[r.type] || 0) + 1;
  return c;
}

/* A bundle path for an object the app writes. `taken` is the set of paths in
   use; the result is added to it. An attestation goes beside the manifest,
   not under objects/: nothing signed contains its own signature (D3.1). */
function jscObjectPath(type, id, taken) {
  const name = jscSlug(String(id).split("/").slice(-2).join("-"));
  const base = type === "attestation" ? `attestation-${name}` : `objects/${JSC_TYPE_DIR[type] || "obj"}/${name}`;
  let path = base + ".json";
  for (let n = 2; taken.has(path); n++) path = `${base}-${n}.json`;
  taken.add(path);
  return path;
}

/* ---------- from a graph to bundle files ----------
   The manifest is computed from what is in the graph now. If it says the same
   as the manifest the bundle came with, that manifest leaves unchanged, text
   and all; otherwise the computed one is written. Either way a second export
   of the same graph gives the same bytes. `provenance` is the provenance of
   a bundle that has no manifest of its own (an imported catalog names its
   source, a resolved package the Tailoring it was resolved with).
   -> { files: [{path, text}], manifest, verbatim, problems } */
/* An attestation is listed only if the manifest it came with listed it;
   otherwise it travels beside the manifest (D3.1). */
const jscBesideManifest = r => r.type === "attestation" && !r.entry;
function jscNeedsKernel2(g) {
  if (g.scales.size) return true;
  for (const r of g.objects.values()) {
    if (r.type === "risk" || r.type === "check") return true;
    if (r.type === "finding" && ((Array.isArray(r.obj["risk-refs"]) && r.obj["risk-refs"].length) || r.obj["check-ref"])) return true;
    if (r.type === "assessment" && (r.obj["check-results"] || r.obj["tailoring-ref"])) return true;
  }
  return false;
}
async function jscBuildBundle(g, provenance) {
  const problems = [];
  const objects = [];
  for (const id of g.order) {
    const r = g.objects.get(id);
    if (jscBesideManifest(r)) continue;
    objects.push({ id: r.obj.id, version: r.obj.version,
      "package-digest": await jscPackageDigest(r.text),
      "semantic-digest": await jscSemanticDigest(r.obj), path: r.path });
  }
  const pinOf = async x => {
    const id = (x.pin && x.pin.id) || x.def.id, version = (x.pin && x.pin["exact-version"]) || x.def.version;
    if (!id || !version) { problems.push(`${x.path}: has no id and version to pin; left out of the bundle`); return null; }
    return { id, "exact-version": version, digest: await jscPackageDigest(x.text), path: x.path };
  };
  const facetPins = [], scalePins = [], shipped = [];
  for (const x of g.facetSchemas) { const p = await pinOf(x); if (p) { facetPins.push(p); shipped.push(x); } }
  for (const x of g.scales.values()) { const p = await pinOf(x); if (p) { scalePins.push(p); shipped.push(x); } }
  const old = g.manifest || {};
  const kernel = jscNeedsKernel2(g) ? JSC_KERNEL : old["kernel-version"];
  const said = m => JSON.stringify([m["kernel-version"] || null, m.objects || [], m["facet-schemas"] || [], m.scales || []]);
  const manifest = { "manifest-version": "1" };
  if (kernel) manifest["kernel-version"] = kernel;
  manifest.provenance = g.manifest
    ? { ...(old.provenance || {}), "edited-with": JSC_TOOL }
    : provenance ? { ...provenance, "written-with": JSC_TOOL } : { source: "JASCON-App", converter: JSC_TOOL };
  manifest.objects = objects;
  manifest["facet-schemas"] = facetPins;
  if (scalePins.length) manifest.scales = scalePins;
  if (old.renderings) manifest.renderings = old.renderings;
  const verbatim = !!g.manifest && said(old) === said(manifest);
  const files = [
    { path: JSC_MANIFEST, text: verbatim ? g.manifestText : jscSerialize(manifest) },
    ...g.order.map(id => ({ path: g.objects.get(id).path, text: g.objects.get(id).text })),
    ...shipped.map(x => ({ path: x.path, text: x.text })),
    ...g.aux,
  ];
  return { files, manifest: verbatim ? old : manifest, verbatim, problems };
}

/* ---------- verification ----------
   Recomputes both digests of every object and the digest of every pin
   against the manifest the bundle came with.
   -> { objects: Map(id -> {pkg, sem} | null when the manifest does not list it),
        pins: [{path, ok}], counts: {ok, bad, unlisted, missing} } */
async function jscVerify(g, onProgress) {
  const out = { objects: new Map(), pins: [], counts: { ok: 0, bad: 0, unlisted: 0, missing: 0 } };
  if (!g.manifest) return out;
  let done = 0;
  for (const id of g.order) {
    const r = g.objects.get(id);
    if (!r.entry) { out.objects.set(id, null); if (!jscBesideManifest(r)) out.counts.unlisted++; }
    else {
      const v = { pkg: await jscPackageDigest(r.text) === r.entry["package-digest"],
                  sem: await jscSemanticDigest(r.obj) === r.entry["semantic-digest"] };
      out.objects.set(id, v);
      out.counts[v.pkg && v.sem ? "ok" : "bad"]++;
    }
    if (onProgress && (++done % 100 === 0 || done === g.order.length)) onProgress(done, g.order.length);
  }
  for (const x of [...g.facetSchemas, ...g.scales.values()]) {
    if (x.pin) out.pins.push({ path: x.path, ok: await jscPackageDigest(x.text) === x.pin.digest });
  }
  const have = new Set([...g.objects.values()].map(r => r.path));
  out.counts.missing = (g.manifest.objects || []).filter(e => !have.has(e.path)).length;
  return out;
}

/* ---------- ZIP (store only on write, store and deflate on read) ----------
   No library: the archives are small and JSON travels compressed anyway. */
const JSC_CRC_TABLE = (() => {
  const t = new Uint32Array(256);
  for (let i = 0; i < 256; i++) {
    let c = i;
    for (let k = 0; k < 8; k++) c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1);
    t[i] = c >>> 0;
  }
  return t;
})();
function jscCrc32(bytes) {
  let c = 0xFFFFFFFF;
  for (let i = 0; i < bytes.length; i++) c = JSC_CRC_TABLE[(c ^ bytes[i]) & 0xFF] ^ (c >>> 8);
  return (c ^ 0xFFFFFFFF) >>> 0;
}
/* files: [{path, text}] -> Uint8Array. The entry time is fixed (1980-01-01),
   so the same files give the same archive. */
function jscZip(files) {
  const chunks = [], central = [];
  let offset = 0;
  const u16 = v => [v & 0xFF, (v >>> 8) & 0xFF];
  const u32 = v => [v & 0xFF, (v >>> 8) & 0xFF, (v >>> 16) & 0xFF, (v >>> 24) & 0xFF];
  for (const f of files) {
    const name = jscUtf8(f.path), data = jscUtf8(f.text), crc = jscCrc32(data);
    // 0x0800: the file name is UTF-8; time 0, date 0x0021 = 1980-01-01
    const common = [...u16(20), ...u16(0x0800), ...u16(0), ...u16(0), ...u16(0x0021),
      ...u32(crc), ...u32(data.length), ...u32(data.length), ...u16(name.length), ...u16(0)];
    chunks.push(new Uint8Array([...u32(0x04034b50), ...common]), name, data);
    central.push(new Uint8Array([...u32(0x02014b50), ...u16(20), ...common,
      ...u16(0), ...u16(0), ...u16(0), ...u32(0), ...u32(offset), ...name]));
    offset += 30 + name.length + data.length;
  }
  let cdLen = 0;
  for (const c of central) { chunks.push(c); cdLen += c.length; }
  chunks.push(new Uint8Array([...u32(0x06054b50), ...u16(0), ...u16(0),
    ...u16(files.length), ...u16(files.length), ...u32(cdLen), ...u32(offset), ...u16(0)]));
  const out = new Uint8Array(chunks.reduce((s, c) => s + c.length, 0));
  let p = 0;
  for (const c of chunks) { out.set(c, p); p += c.length; }
  return out;
}
const jscDecode = bytes => new TextDecoder("utf-8", { ignoreBOM: true }).decode(bytes);

/* ---------- which files of a folder or ZIP a set keeps ---------- */
const TEXT_FILE = /\.(json|md|txt|csv|html|xml|ya?ml|dsse)$/i;   // .dsse: the envelope of an attestation, JSON
/* A content-addressed evidence blob beside the manifest (CP-CHECK-1,
   CHECK-15): its name is the SHA-256 of its bytes and it has no extension. */
const JSC_EVIDENCE_PATH = /(^|\/)evidence\/sha256\/[0-9a-f]{64}$/;
/* Of everything handed over, the files a set keeps: those with a text
   extension, any file an attestation names as its envelope, whatever it is
   called, and the blobs of the evidence store. A set holds text only; an
   evidence blob that is not UTF-8 text cannot be verified here and the check
   says so. entries: [{path, text}] */
function jscKeepFiles(entries) {
  const out = entries.filter(e => TEXT_FILE.test(e.path) || JSC_EVIDENCE_PATH.test(e.path));
  const named = new Set(out.flatMap(e => [...e.text.matchAll(/"envelope-ref"\s*:\s*"([^"\\]+)"/g)].map(m => m[1])));
  for (const e of entries) {
    if (!TEXT_FILE.test(e.path) && [...named].some(n => e.path === n || e.path.endsWith("/" + n))) out.push(e);
  }
  return out;
}

/* -> [{path, text}] for every entry that is not a directory */
async function jscUnzip(bytes) {
  const buf = bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  const dv = new DataView(buf.buffer, buf.byteOffset, buf.byteLength);
  let eocd = -1;
  for (let i = buf.length - 22; i >= Math.max(0, buf.length - 22 - 65535); i--) {
    if (dv.getUint32(i, true) === 0x06054b50) { eocd = i; break; }
  }
  if (eocd < 0) throw new Error("not a ZIP archive (no end-of-central-directory record)");
  const count = dv.getUint16(eocd + 10, true);
  let off = dv.getUint32(eocd + 16, true);
  const out = [];
  for (let n = 0; n < count; n++) {
    if (dv.getUint32(off, true) !== 0x02014b50) throw new Error("ZIP central directory is damaged");
    const method = dv.getUint16(off + 10, true), csize = dv.getUint32(off + 20, true);
    const nameLen = dv.getUint16(off + 28, true), extraLen = dv.getUint16(off + 30, true);
    const commentLen = dv.getUint16(off + 32, true), lho = dv.getUint32(off + 42, true);
    const path = jscDecode(buf.subarray(off + 46, off + 46 + nameLen));
    const start = lho + 30 + dv.getUint16(lho + 26, true) + dv.getUint16(lho + 28, true);
    const raw = buf.slice(start, start + csize);
    let data;
    if (method === 0) data = raw;
    else if (method === 8) {
      const ds = new DecompressionStream("deflate-raw");
      data = new Uint8Array(await new Response(new Blob([raw]).stream().pipeThrough(ds)).arrayBuffer());
    } else throw new Error(`${path}: ZIP compression method ${method} is not supported`);
    if (!path.endsWith("/")) out.push({ path, text: jscDecode(data) });
    off += 46 + nameLen + extraLen + commentLen;
  }
  return out;
}

/* ==JSC-PURE-END== */

if (typeof module !== "undefined" && module.exports) {
  module.exports = { JSC_CFG, N, JSC_BUILD, JSC_TOOL, JSC_KERNEL, JSC_KERNEL_READS, JSC_TYPES, JSC_MANIFEST, JscKernelError,
    jscEsc, jscSlug, jscText, jscInferType, jscIsScale, jscCanonical, jscSha256, jscSha256Js, jscUtf8,
    jscPackageDigest, jscSemanticDigest, jscSerialize, jscNormalizePaths, jscClassifyFiles, jscGraphFrom, jscKeepFiles,
    jscTypeCounts, jscObjectPath, jscNeedsKernel2, jscBesideManifest, jscBuildBundle, jscVerify, jscCrc32, jscZip, jscUnzip, jscDecode };
}

/* ====================================================================
   Browser part: configuration, languages, theme, storage, page shell.
   ==================================================================== */
if (typeof window !== "undefined") (() => {

const PREFIX = "jsc:cfg:";

const jscCfg = {
  get(key) {
    const v = localStorage.getItem(PREFIX + key);
    if (v !== null) return v;
    const d = JSC_CFG.find(c => c.key === key);
    return d ? d.def : "";
  },
  set(key, value) { localStorage.setItem(PREFIX + key, String(value)); },
  remove(key) { localStorage.removeItem(PREFIX + key); },
};
window.jscCfg = jscCfg;

/* ---------- languages ----------
   The English text is the key: T called with an English text returns the
   German text when the interface is German and a translation exists, the
   English text otherwise. A missing translation therefore shows as English, never as a
   key. tools/check-i18n.mjs lists what is missing. {name} is replaced from
   the second argument. */
const jscI18n = {
  langs: [["en", "English"], ["de", "Deutsch"]],
  table: { de: Object.create(null) },
  lang() {
    const v = jscCfg.get("ui:lang");
    if (v === "en" || v === "de") return v;
    return String(navigator.language || "en").toLowerCase().startsWith("de") ? "de" : "en";
  },
  contentLang() { return jscCfg.get("ui:contentlang").trim() || this.lang(); },
  add(lang, map) { Object.assign(this.table[lang], map); },
  t(s, vars) {
    const table = this.table[this.lang()];
    const out = (table && table[s]) || s;
    return vars ? out.replace(/\{(\w+)\}/g, (m, k) => (k in vars ? String(vars[k]) : m)) : out;
  },
  /* Static markup: <span data-i18n>English text</span> and
     data-i18n-attr="title placeholder". The English original is kept on the
     element, so a language switch needs no reload. */
  apply(root) {
    for (const el of (root || document).querySelectorAll("[data-i18n]")) {
      if (el.dataset.i18nSrc === undefined) el.dataset.i18nSrc = el.textContent.trim();
      el.textContent = this.t(el.dataset.i18nSrc);
    }
    for (const el of (root || document).querySelectorAll("[data-i18n-attr]")) {
      for (const a of el.dataset.i18nAttr.split(/\s+/).filter(Boolean)) {
        const srcKey = "i18nSrc_" + a.replace(/-/g, "_");
        if (el.dataset[srcKey] === undefined) el.dataset[srcKey] = el.getAttribute(a) || "";
        el.setAttribute(a, this.t(el.dataset[srcKey]));
      }
    }
    document.documentElement.lang = this.lang();
  },
};
window.jscI18n = jscI18n;
const T = (s, vars) => jscI18n.t(s, vars);
window.T = T;
/* jscText with the configured content language */
window.TT = v => jscText(v, jscI18n.contentLang());

jscI18n.add("de", {
  "Home": "Übersicht", "Settings": "Einstellungen", "Console": "Konsole", "clear": "leeren",
  "{n} lines": "{n} Zeilen", "no bundle": "kein Bundle", "{n} objects": "{n} Objekte",
  "Set": "Set", "{n} entries, type to filter …": "{n} Einträge filtern …", "Filter the list": "Liste filtern",
  "dark": "dunkel", "light": "hell", "system": "System",
  "jascon-core.css is missing or did not load. Unpack the complete jascon-app folder.":
    "jascon-core.css fehlt oder wurde nicht geladen. Bitte den kompletten Ordner jascon-app entpacken.",
  "Could not read the set: {msg}": "Das Set konnte nicht gelesen werden: {msg}",
  "set \"{set}\": {n} objects ({types})": "Set „{set}“: {n} Objekte ({types})",
  "set \"{set}\" is empty. Load a bundle on the Home page.": "Set „{set}“ ist leer. Ein Bundle auf der Übersichtsseite laden.",
  "the set changed in another page; reloaded": "Das Set wurde in einer anderen Seite geändert; neu geladen",
  "saved {n} object(s) to set \"{set}\"": "{n} Objekt(e) in Set „{set}“ gespeichert",
  "removed {n} object(s) from set \"{set}\"": "{n} Objekt(e) aus Set „{set}“ entfernt",
  "Hide this message": "Meldung ausblenden", "Show or hide the console": "Konsole ein- oder ausklappen",
  "error: {msg}": "Fehler: {msg}",
});

/* ---------- theme ----------
   The tokens are in jascon-core.css; this sets the attribute on <html> and
   remembers the choice. Each page also sets it in a one-line script in its
   <head>, before the first paint, because this file loads at the end. */
const jscTheme = {
  options: ["dark", "light", "system"],
  get() { const v = jscCfg.get("ui:theme"); return this.options.includes(v) ? v : "dark"; },
  apply(doc) {
    const root = (doc || document).documentElement, v = this.get();
    if (v === "system") root.removeAttribute("data-theme"); else root.setAttribute("data-theme", v);
  },
  set(v) { jscCfg.set("ui:theme", v); this.apply(); },
  next() { return this.options[(this.options.indexOf(this.get()) + 1) % this.options.length]; },
};
window.jscTheme = jscTheme;
jscTheme.apply();

/* ---------- storage ----------
   IndexedDB "jascon-app", one store "files". A record is one file of one set:
     { key: set + "\n" + path, set, path, text, kind, type, id, origin, updatedAt }
   The key begins with the set name, so a key range reads one set without an
   index. One operation per transaction and no await inside it: a transaction
   closes itself as soon as the microtask queue runs empty. */
const DB = "jascon-app", STORE = "files", TOUCH = PREFIX + "store:touch", ACTIVE = PREFIX + "store:set";
const DEFAULT_SET = "default";
function openDb() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB, 1);
    req.onupgradeneeded = () => { req.result.createObjectStore(STORE, { keyPath: "key" }); };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}
async function tx(mode, fn) {
  const db = await openDb();
  return new Promise((resolve, reject) => {
    const t = db.transaction(STORE, mode);
    let result;
    try {
      const req = fn(t.objectStore(STORE));
      if (req && "onsuccess" in req) req.onsuccess = () => { result = req.result; };
    } catch (e) { db.close(); reject(e); return; }
    t.oncomplete = () => { db.close(); resolve(result); };
    t.onerror = t.onabort = () => { db.close(); reject(t.error); };
  });
}
const keyOf = (set, path) => set + "\n" + path;
const rangeOf = set => IDBKeyRange.bound(set + "\n", set + "\n￿");
const jscStore = {
  activeSet() { return (localStorage.getItem(ACTIVE) || DEFAULT_SET).trim() || DEFAULT_SET; },
  setActiveSet(name) {
    localStorage.setItem(ACTIVE, String(name || DEFAULT_SET).trim() || DEFAULT_SET);
    this.touch();
  },
  /* Tells every open page that the store changed: an event in this window,
     a storage event in all others (the hub and its iframe are two windows). */
  touch() {
    try { localStorage.setItem(TOUCH, Date.now() + ":" + Math.random()); } catch (e) { /* quota: the event below still fires here */ }
    window.dispatchEvent(new CustomEvent("jsc:changed"));
  },
  async files(set) { return (await tx("readonly", s => s.getAll(rangeOf(set)))) || []; },
  /* [{name, count}] for every set that holds a file, plus the active one */
  async sets() {
    const keys = (await tx("readonly", s => s.getAllKeys())) || [];
    const by = new Map([[this.activeSet(), 0]]);
    for (const k of keys) { const set = String(k).split("\n")[0]; by.set(set, (by.get(set) || 0) + 1); }
    return [...by].map(([name, count]) => ({ name, count })).sort((a, b) => a.name.localeCompare(b.name));
  },
  async putMany(set, records) {
    const now = new Date().toISOString();
    await tx("readwrite", s => { for (const r of records) s.put({ ...r, set, key: keyOf(set, r.path), updatedAt: now }); });
    this.touch();
  },
  async remove(set, paths) {
    await tx("readwrite", s => { for (const p of paths) s.delete(keyOf(set, p)); });
    this.touch();
  },
  async removeSet(set) {
    await tx("readwrite", s => s.delete(rangeOf(set)));
    this.touch();
  },
};
window.jscStore = jscStore;

/* ---------- the working set ----------
   What a page holds while it runs: the graph of the active set. Objects the
   app writes get origin "authored" and a path of their own; an imported
   object that is edited keeps its path and becomes "authored". */
const jscSet = {
  name: null,
  graph: jscGraphFrom([]),
  async load() {
    this.name = jscStore.activeSet();
    this.graph = jscGraphFrom(await jscStore.files(this.name));
    return this.graph;
  },
  /* Puts files into a set as they arrived. With replace the set is emptied
     first (a bundle); without, the files are added and a file of the same
     path is overwritten (loose files). Classification runs before anything
     is deleted, so a bundle that cannot be read leaves the set as it was.
     -> {objects, files, problems} */
  async importFiles(set, files, { replace }) {
    const norm = jscNormalizePaths(files);
    const { records, problems } = jscClassifyFiles(norm.files);
    if (norm.dropped) problems.push(`${norm.dropped} file(s) outside the bundle folder were ignored`);
    if (replace) await jscStore.removeSet(set);
    await jscStore.putMany(set, records.map(r => ({ ...r, origin: "imported" })));
    return { objects: records.filter(r => r.kind === "object").length, files: records.length, problems };
  },
  mintId(kind, name) { return jscCfg.get("org:ns").replace(/\/+$/, "") + "/" + kind + "/" + jscSlug(name); },
  async saveObjects(objs) {
    const g = this.graph, taken = new Set([...g.objects.values()].map(r => r.path));
    const records = objs.map(obj => {
      const type = jscInferType(obj);
      if (!type || type === "manifest") throw new Error(`${obj && obj.id}: not a kernel object`);
      const old = g.objects.get(obj.id);
      return { path: old ? old.path : jscObjectPath(type, obj.id, taken), text: jscSerialize(obj),
        kind: "object", type, id: obj.id, origin: "authored" };
    });
    await jscStore.putMany(this.name, records);
    await this.load();
    jscLog.ok(T("saved {n} object(s) to set \"{set}\"", { n: objs.length, set: this.name }));
  },
  async removeObjects(ids) {
    const paths = ids.map(id => this.graph.objects.get(id)).filter(Boolean).map(r => r.path);
    await jscStore.remove(this.name, paths);
    await this.load();
    jscLog.ok(T("removed {n} object(s) from set \"{set}\"", { n: paths.length, set: this.name }));
  },
  /* A scale is a pinned file, not an object; its path follows its id. */
  async saveScale(def) {
    const old = this.graph.scales.get(def.id);
    const path = old ? old.path : `scales/${jscSlug(String(def.id).split("/").pop())}.json`;
    await jscStore.putMany(this.name, [{ path, text: jscSerialize(def), kind: "scale", type: null, id: def.id, origin: "authored" }]);
    await this.load();
  },
  async removeScale(id) {
    const old = this.graph.scales.get(id);
    if (old) { await jscStore.remove(this.name, [old.path]); await this.load(); }
  },
  /* A file beside the manifest that is neither an object nor pinned (a
     record the app keeps with the bundle). Empty text removes it. */
  async saveAux(path, text) {
    if (text) await jscStore.putMany(this.name, [{ path, text, kind: "aux", type: null, id: null, origin: "authored" }]);
    else await jscStore.remove(this.name, [path]);
    await this.load();
  },
  /* -> {name, bytes, verbatim, problems} : the set as a bundle ZIP */
  async exportZip() {
    const built = await jscBuildBundle(this.graph);
    const folder = jscSlug(this.name) + "-bundle";
    return { name: folder + ".zip", verbatim: built.verbatim, problems: built.problems,
      count: built.files.length, bytes: jscZip(built.files.map(f => ({ path: folder + "/" + f.path, text: f.text }))) };
  },
};
window.jscSet = jscSet;

/* ---------- reading what the user hands over ---------- */
/* FileList or File[] -> [{path, text}]; a .zip is opened in place. A file
   that is neither text by its name nor named as an envelope is read only if
   it is small: an image or a PDF in a bundle folder is not loaded. */
async function jscReadFiles(fileList) {
  const all = [];
  for (const f of [...fileList]) {
    const path = f.jscPath || f.webkitRelativePath || f.name;
    if (/\.zip$/i.test(f.name)) all.push(...await jscUnzip(new Uint8Array(await f.arrayBuffer())));
    else if (TEXT_FILE.test(f.name) || f.size <= 262144) all.push({ path, text: jscDecode(new Uint8Array(await f.arrayBuffer())) });
  }
  return jscKeepFiles(all);
}
/* A drop may carry folders; walk them and keep the relative path. */
async function jscReadDrop(dataTransfer) {
  const entries = [...(dataTransfer.items || [])].map(i => i.webkitGetAsEntry && i.webkitGetAsEntry()).filter(Boolean);
  if (!entries.length) return jscReadFiles(dataTransfer.files || []);
  const files = [];
  const walk = async entry => {
    if (entry.isFile) {
      const file = await new Promise((res, rej) => entry.file(res, rej));
      file.jscPath = entry.fullPath.replace(/^\//, "");
      files.push(file);
    } else if (entry.isDirectory) {
      const reader = entry.createReader();
      for (;;) {   // readEntries returns at most 100 entries per call
        const batch = await new Promise((res, rej) => reader.readEntries(res, rej));
        if (!batch.length) break;
        for (const e of batch) await walk(e);
      }
    }
  };
  for (const e of entries) await walk(e);
  return jscReadFiles(files);
}
/* Fetches a bundle folder over http(s): the manifest, then every file it
   lists, sixteen at a time. file:// blocks fetch by design. */
async function jscFetchBundle(url) {
  let base = new URL(String(url).trim().replace(/content-manifest\.json$/, ""), location.href);
  if (!base.pathname.endsWith("/")) base = new URL(base.href + "/");
  const get = async rel => {
    const res = await fetch(new URL(rel, base));
    if (!res.ok) throw new Error(`${rel}: HTTP ${res.status}`);
    return { path: rel, text: jscDecode(new Uint8Array(await res.arrayBuffer())) };
  };
  const man = await get(JSC_MANIFEST);
  const manifest = JSON.parse(man.text);
  const paths = ["objects", "facet-schemas", "scales", "renderings"]
    .flatMap(k => (manifest[k] || []).map(e => e && e.path)).filter(Boolean);
  const files = [man], failed = [];
  let next = 0;
  await Promise.all(Array.from({ length: Math.min(16, paths.length) }, async () => {
    while (next < paths.length) {
      const p = paths[next++];
      try { files.push(await get(p)); } catch (e) { failed.push(e.message); }
    }
  }));
  /* the envelope of a listed attestation lies beside the manifest and is named only by the attestation */
  for (const f of [...files]) {
    if (!f.text.includes('"envelope-ref"')) continue;
    let ref = null;
    try { ref = JSON.parse(f.text)["envelope-ref"]; } catch (e) { /* not JSON: nothing to follow */ }
    if (typeof ref !== "string" || !ref || /^[a-z]+:|^\/|\.\./i.test(ref) || files.some(x => x.path === ref)) continue;
    try { files.push(await get(ref)); } catch (e) { /* a missing envelope is reported by the check, not by the load */ }
  }
  /* The evidence store lies beside the manifest too, named only by the check
     results of an Assessment (record, observation) and by each record (its
     outputs). A blob that is not there is reported as withheld by the check. */
  const want = [], safe = ref => typeof ref === "string" && JSC_EVIDENCE_PATH.test(ref) && !files.some(x => x.path === ref) && !want.includes(ref);
  const follow = async refs => {
    const fresh = refs.filter(safe);
    want.push(...fresh);
    const got = [];
    for (const ref of fresh) { try { const f = await get(ref); files.push(f); got.push(f); } catch (e) { /* withheld */ } }
    return got;
  };
  const rows = files.flatMap(f => { try { return JSON.parse(f.text)["check-results"] || []; } catch (e) { return []; } });
  const records = await follow(rows.flatMap(r => [r && (r["evidence-record"] || {}).ref, r && (r["observation-ref"] || {}).ref]));
  await follow(records.flatMap(f => { try { return (JSON.parse(f.text).outputs || []).map(o => "evidence/sha256/" + String(o.digest).replace(/^sha256:/, "")); } catch (e) { return []; } }));
  return { files, failed };
}
function jscDownload(name, data, mime) {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(data instanceof Blob ? data : new Blob([data], { type: mime || "application/octet-stream" }));
  a.download = name;
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 4000);
}
Object.assign(window, { jscReadFiles, jscReadDrop, jscFetchBundle, jscDownload });

/* ---------- log console ----------
   Lines written before the page shell exists are kept and shown once it
   does. Text only: a message is never parsed as markup. */
const jscLog = (() => {
  const pending = [];
  let host = null, counter = null, n = 0;
  const line = (cls, msg) => {
    const t = new Date();
    const div = document.createElement("div");
    div.className = "l-" + cls;
    const ts = document.createElement("span");
    ts.className = "ts";
    ts.textContent = t.toTimeString().slice(0, 8) + "." + String(t.getMilliseconds()).padStart(3, "0");
    div.append(ts, String(msg));
    return div;
  };
  const write = (cls, msg) => {
    n++;
    const div = line(cls, msg);
    if (!host) { pending.push(div); return; }
    host.appendChild(div);
    host.scrollTop = host.scrollHeight;
    counter.textContent = T("{n} lines", { n });
  };
  return {
    info: m => write("info", m), ok: m => write("ok", m), warn: m => write("warn", m),
    err: m => write("err", m), debug: m => write("debug", m),
    mount(el, countEl) {
      host = el; counter = countEl;
      pending.splice(0).forEach(d => host.appendChild(d));
      counter.textContent = T("{n} lines", { n });
    },
    clear() { n = 0; if (host) { host.textContent = ""; counter.textContent = T("{n} lines", { n }); } },
  };
})();
window.jscLog = jscLog;

/* ---------- list filter ----------
   A list with more than `min` entries (default 10) gets a search field as its
   first entry. Call it after every re-render of the container; the query
   survives the re-render, kept per container id. */
const filterText = new Map();
function jscListFilter(container, opts = {}) {
  if (!container) return 0;
  const key = opts.key || container.id || "";
  const old = container.querySelector(":scope > .jsc-listfilter");
  if (old) old.remove();
  const items = [...container.querySelectorAll(opts.item || ":scope > *")];
  items.forEach(el => el.classList.remove("jsc-listfilter-hidden"));
  if (items.length <= (opts.min ?? 10)) return items.length;
  const wrap = document.createElement(/^(UL|OL)$/.test(container.tagName) ? "li" : "div");
  wrap.className = "jsc-listfilter";
  const input = document.createElement("input");
  input.type = "search"; input.autocomplete = "off"; input.spellcheck = false;
  input.placeholder = T("{n} entries, type to filter …", { n: items.length });
  input.setAttribute("aria-label", T("Filter the list"));
  input.value = filterText.get(key) || "";
  const count = document.createElement("span");
  count.className = "jsc-listfilter-count";
  const apply = () => {
    const q = input.value.trim().toLowerCase();
    let hits = 0;
    for (const el of items) {
      const hit = !q || (el.textContent || "").toLowerCase().includes(q);
      el.classList.toggle("jsc-listfilter-hidden", !hit);
      if (hit) hits++;
    }
    count.textContent = q ? `${hits} / ${items.length}` : String(items.length);
    filterText.set(key, input.value);
  };
  input.addEventListener("input", apply);
  input.addEventListener("keydown", e => { if (e.key === "Escape") { input.value = ""; apply(); } });
  wrap.append(input, count);
  container.prepend(wrap);
  apply();
  return items.length;
}
window.jscListFilter = jscListFilter;

/* ---------- banner: something the user must not miss ---------- */
function jscBanner(msg) {
  let b = document.getElementById("jsc-banner");
  if (!b) {
    b = document.createElement("div");
    b.id = "jsc-banner"; b.setAttribute("role", "alert");
    const x = document.createElement("button");
    x.type = "button"; x.textContent = "✕"; x.title = T("Hide this message");
    x.addEventListener("click", () => b.remove());
    b.append(document.createElement("span"), x);
    document.body.appendChild(b);
  }
  b.firstChild.textContent = msg;
}
jscBanner.clear = () => { const b = document.getElementById("jsc-banner"); if (b) b.remove(); };
window.jscBanner = jscBanner;

/* ---------- page shell ----------
   A tool page writes only what is its own: a rail and a main area inside
   <div id="app"><div id="mid"><nav id="rail">…</nav><main id="main">…</main></div></div>.
   jscPage.init adds the top bar, the splitter and the log console, wires the
   navigation (a .navitem[data-view] shows the one section[data-view] of the
   same name), loads the active set and calls onGraph with it, again whenever
   the set changes. Inside the hub's iframe the brand is hidden; the hub
   shows it. */
const jscPage = {
  tool: null, onGraph: null,
  async init({ tool, title, onGraph }) {
    this.tool = tool; this.onGraph = onGraph;
    if (!getComputedStyle(document.documentElement).getPropertyValue("--bg-deep").trim()) {
      jscBanner(T("jascon-core.css is missing or did not load. Unpack the complete jascon-app folder."));
    }
    if (window.parent !== window) document.body.classList.add("embedded");
    const app = document.getElementById("app"), mid = document.getElementById("mid");
    const el = (tag, attrs, ...kids) => {
      const e = document.createElement(tag);
      for (const [k, v] of Object.entries(attrs || {})) k === "class" ? (e.className = v) : e.setAttribute(k, v);
      e.append(...kids);
      return e;
    };
    const brand = el("div", { class: "brand" }, "◈ JASCON ", el("span", {}, "App"));
    this.setPill = el("div", { class: "pill", id: "pill-set" });
    const home = el("a", { class: "btn small standalone-only", href: "index.html" }, T("Home"));
    app.prepend(el("div", { id: "topbar" }, brand, el("div", { class: "pill on" }, title), this.setPill,
      el("div", { class: "spacer" }), home, el("div", { class: "pill" }, "build " + JSC_BUILD)));
    document.getElementById("rail").after(el("div", { id: "splitter" }));
    const count = el("span", { class: "nano" });
    const clear = el("button", { class: "small", type: "button" }, T("clear"));
    const toggle = el("button", { class: "small", type: "button", title: T("Show or hide the console") }, "▾");
    const log = el("div", { id: "log", role: "log" });
    const wrap = el("div", { id: "logwrap" },
      el("div", { id: "loghead" }, el("span", { class: "nano" }, T("Console")), count, el("div", { style: "flex:1" }), clear, toggle), log);
    app.append(wrap);
    clear.addEventListener("click", () => jscLog.clear());
    const collapsedKey = PREFIX + "log:collapsed";
    const setCollapsed = c => { wrap.classList.toggle("collapsed", c); toggle.textContent = c ? "▴" : "▾"; };
    setCollapsed(localStorage.getItem(collapsedKey) === "1");
    toggle.addEventListener("click", () => {
      const c = !wrap.classList.contains("collapsed");
      setCollapsed(c); localStorage.setItem(collapsedKey, c ? "1" : "0");
    });
    jscLog.mount(log, count);
    this.wireSplitter(mid);
    this.wireNav();
    jscI18n.apply();
    window.addEventListener("error", e => jscLog.err(T("error: {msg}", { msg: e.message })));
    window.addEventListener("unhandledrejection", e => jscLog.err(T("error: {msg}", { msg: (e.reason && e.reason.message) || e.reason })));
    /* Another page wrote to the store (storage event), or the language or
       theme changed there. */
    window.addEventListener("storage", e => {
      if (e.key === TOUCH || e.key === ACTIVE) this.reload(true);
      if (e.key === PREFIX + "ui:theme") jscTheme.apply();
      if (e.key === PREFIX + "ui:lang" || e.key === PREFIX + "ui:contentlang") location.reload();
    });
    await this.reload(false);
  },
  async reload(foreign) {
    try {
      const g = await jscSet.load();
      const counts = jscTypeCounts(g);
      this.setPill.textContent = `${T("Set")} ${jscSet.name} · ${T("{n} objects", { n: g.objects.size })}`;
      this.setPill.classList.toggle("on", g.objects.size > 0);
      if (foreign) jscLog.info(T("the set changed in another page; reloaded"));
      else if (!g.objects.size) jscLog.warn(T("set \"{set}\" is empty. Load a bundle on the Home page.", { set: jscSet.name }));
      else jscLog.ok(T("set \"{set}\": {n} objects ({types})", { set: jscSet.name, n: g.objects.size,
        types: Object.entries(counts).map(([k, v]) => `${k} ${v}`).join(" · ") }));
      g.problems.forEach(p => jscLog.warn(p));
      if (this.onGraph) await this.onGraph(g);
    } catch (e) {
      jscLog.err(T("Could not read the set: {msg}", { msg: e.message }));
      throw e;
    }
  },
  /* Call after a page wrote through jscSet: the graph is already reloaded,
     only the page has to render again. */
  async refresh() {
    const g = jscSet.graph;
    this.setPill.textContent = `${T("Set")} ${jscSet.name} · ${T("{n} objects", { n: g.objects.size })}`;
    if (this.onGraph) await this.onGraph(g);
  },
  wireSplitter(mid) {
    const key = PREFIX + "rail:" + this.tool, splitter = document.getElementById("splitter");
    const saved = parseInt(localStorage.getItem(key), 10);
    if (saved) mid.style.setProperty("--rail-w", saved + "px");
    splitter.addEventListener("mousedown", down => {
      down.preventDefault();
      const move = e => mid.style.setProperty("--rail-w", Math.max(180, Math.min(520, e.clientX)) + "px");
      const up = e => {
        localStorage.setItem(key, String(Math.max(180, Math.min(520, e.clientX))));
        window.removeEventListener("mousemove", move); window.removeEventListener("mouseup", up);
      };
      window.addEventListener("mousemove", move); window.addEventListener("mouseup", up);
    });
  },
  wireNav() {
    const key = PREFIX + "view:" + this.tool;
    const items = [...document.querySelectorAll(".navitem[data-view]")];
    const wanted = new URLSearchParams(location.hash.slice(1)).get("view") || localStorage.getItem(key);
    items.forEach(i => i.addEventListener("click", () => this.show(i.dataset.view)));
    if (items.length) this.show(items.some(i => i.dataset.view === wanted) ? wanted : items[0].dataset.view);
  },
  view: null,
  show(view) {
    this.view = view;
    localStorage.setItem(PREFIX + "view:" + this.tool, view);
    document.querySelectorAll(".navitem[data-view]").forEach(i => {
      const on = i.dataset.view === view;
      i.classList.toggle("active", on);
      if (on) i.setAttribute("aria-current", "page"); else i.removeAttribute("aria-current");
    });
    document.querySelectorAll("#main > [data-view]").forEach(s => s.classList.toggle("hidden", s.dataset.view !== view));
    window.dispatchEvent(new CustomEvent("jsc:view", { detail: view }));
  },
};
window.jscPage = jscPage;

})();
