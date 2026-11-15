/* Opens every page of the app in a real browser and fails on any script
   error. This is the check that the pages still start: a unit test of the
   core cannot see a page that forgot to load a script the core now needs
   (see ERRATA.md, 2026-11-10).

   It serves the repository from a throwaway local server, loads the IFA
   bundle through the hub, then opens each tool page on that set, in English
   and in German. Needs Playwright with Chromium; where that is missing the
   test is skipped and says so.

   The second browser test drives what only a page can show: a system built
   on the Implement page (ERRATA.md, 2026-11-12) and an advice pack from its
   preview to the exported set (CP-ADVICE-1 §4.6). */
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import crypto from "node:crypto";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import { cisSynthetic } from "./cis-synthetic.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const APP = path.join(ROOT, "jascon-app");
const core = createRequire(import.meta.url)("../jascon-core.js");
let chromium = null;
try { ({ chromium } = createRequire(import.meta.url)("playwright")); } catch (e) { /* skipped below */ }

const MIME = { ".html": "text/html", ".js": "text/javascript", ".css": "text/css", ".json": "application/json", ".md": "text/markdown" };
/* `list`: answer a folder with a listing of its files, as `python -m http.server` does; without it a folder is a 404.
   `list` "page": answer a folder with a page that lists nothing, as a host does that sends its start page for any
   address it does not know. `seen`: a list that gets the path of every request */
function serve(list, seen) {
  const server = http.createServer((req, res) => {
    const file = path.join(ROOT, decodeURIComponent(new URL(req.url, "http://x").pathname));
    if (seen) seen.push(new URL(req.url, "http://x").pathname);
    if (list === "page" && file.startsWith(ROOT) && fs.existsSync(file) && fs.statSync(file).isDirectory()) {
      res.writeHead(200, { "content-type": "text/html; charset=utf-8" });
      res.end('<!doctype html><title>Start</title><a href="/">Home</a> <a href="attestation-ifa-ato.json">a link that lists nothing</a>');
      return;
    }
    if (list && file.startsWith(ROOT) && fs.existsSync(file) && fs.statSync(file).isDirectory()) {
      res.writeHead(200, { "content-type": "text/html; charset=utf-8" });
      res.end("<ul>" + fs.readdirSync(file).sort().map(n => `<li><a href="${encodeURIComponent(n)}${fs.statSync(path.join(file, n)).isDirectory() ? "/" : ""}">${n}</a></li>`).join("") + "</ul>");
      return;
    }
    if (!file.startsWith(ROOT) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404); res.end(); return; }
    res.writeHead(200, { "content-type": MIME[path.extname(file)] || "application/octet-stream" });
    fs.createReadStream(file).pipe(res);
  });
  return new Promise(resolve => server.listen(0, "127.0.0.1", () => resolve(server)));
}
/* ---------- what the tests of "who decided" share (backlog #69) ----------
   Each of them drives a page as a user would, exports the set through the
   hub's button and hands the folder to the reference validator with
   --require-authors and --as-of. The reference is the judge: a page that
   writes a field the kernel does not have, or forgets the kernel pin, or
   leaves a record without the author the form showed, turns it red. */
const EX = path.join(ROOT, "jascon/examples"), IFA = path.join(ROOT, "converted_examples/US.IFA-GoodRead/ifa-core-bundle");
const AS_OF = "2026-11-13";
const ALICE = "https://org.example/party/alice", BOB = "https://org.example/party/bob";
const tree = (dir, prefix = "") => fs.readdirSync(dir).sort().flatMap(n => fs.statSync(path.join(dir, n)).isDirectory()
  ? tree(path.join(dir, n), prefix + n + "/") : [{ path: prefix + n, text: core.jscDecode(fs.readFileSync(path.join(dir, n))) }]);
const zipOf = (dir, name) => ({ name: name + ".zip", mimeType: "application/zip", buffer: Buffer.from(core.jscZip(tree(dir).map(f => ({ ...f, path: name + "/" + f.path })))) });
const jsonFile = (name, obj) => ({ name, mimeType: "application/json", buffer: Buffer.from(JSON.stringify(obj, null, 1) + "\n") });
const pythonWithJsonschema = spawnSync("python3", ["-c", "import jsonschema"]).status === 0;
const needs = !chromium ? "Playwright with Chromium is not installed" : !pythonWithJsonschema ? "python3 with jsonschema is not installed" : false;
/* a browser on the app -> { page, base, errors, requests, onDialog, close() }; a dialog nobody expects is an error. A test that
   expects a question sets s.onDialog to what answers it, and takes it away again. */
async function session(opts = {}) {
  const requests = [], server = await serve(opts.list, requests), base = `http://127.0.0.1:${server.address().port}/jascon-app/`;
  const browser = await chromium.launch(), page = await (await browser.newContext({ acceptDownloads: true })).newPage(), errors = [];
  const s = { page, base, errors, requests, onDialog: null, close: async () => { await browser.close(); server.close(); } };
  page.on("pageerror", e => errors.push(`${page.url().split("/").pop()}: ${e.message}`));
  page.on("console", m => { if (m.type() === "error") errors.push(`${page.url().split("/").pop()}: ${m.text()}`); });
  page.on("dialog", d => { if (s.onDialog) { s.onDialog(d); return; } errors.push("a dialog asked: " + d.message()); d.dismiss(); });
  await page.goto(base + "index.html");
  await page.waitForFunction(() => document.querySelector("#help h1"));
  await page.evaluate(() => localStorage.setItem("jsc:cfg:ui:lang", "en"));
  return s;
}
/* Types into a field as a user does and stays in it. A text field reports its change when something takes the
   focus away, so after this the page has not heard of the value yet (the helper `type` below leaves the field). */
const keys = async (p, selector, text, replace) => {
  await p.locator(selector).click();
  await p.keyboard.press(replace ? "ControlOrMeta+A" : "End");
  await p.keyboard.type(text);
};
/* One press and release of the mouse in the middle of an element, as it lies when the press begins. Not
   locator.click(): that waits until the element is enabled and stable, and a button that is disabled or about to be
   replaced when the user presses it is what these tests are about. -> what lay under the pointer */
const press = async (p, selector) => {
  const n = p.locator(selector);
  await n.evaluate(x => x.scrollIntoView({ block: "center" }));
  const b = await n.boundingBox(), at = [b.x + b.width / 2, b.y + b.height / 2];
  const under = await n.evaluate((x, [px, py]) => { const hit = document.elementFromPoint(px, py); return !!hit && (hit === x || x.contains(hit)); }, at);
  assert.ok(under, selector + " lies under the pointer");
  await p.mouse.click(...at);
};
const toHub = async s => { await s.page.goto(s.base + "index.html"); await s.page.waitForFunction(() => document.querySelector("#help h1")); };
/* a tool page on its own, ready when it has read the set */
const open = async (s, file, view) => {
  await s.page.goto(s.base + file);
  await s.page.locator("#log .l-ok, #log .l-warn").first().waitFor({ timeout: 30000 });
  if (view) await s.page.locator(`.navitem[data-view="${view}"]`).click();
};
/* loads files into the empty active set through the hub's file button, as a bundle (a ZIP with a manifest) or as loose files */
const load = async (s, files) => { await toHub(s); await s.page.locator("#pick-files").setInputFiles(files); await s.page.waitForFunction(() => document.querySelector("#home-log .l-ok")); };
/* the setting "Who am I", typed on the settings page */
const iAm = async (s, uri) => {
  await s.page.goto(s.base + "config.html");
  const field = s.page.locator('[id="cfg-org:me"]');
  await field.waitFor();
  await type(field, uri);
  assert.equal(await s.page.evaluate(() => jscWhoAmI()), uri, "the accessor reads what the settings page stored");
};
/* types into a field and leaves it, which is when a browser reports the change; a date field reports it at once */
const type = async (locator, value) => { await locator.fill(value); await locator.blur(); };
const pick = async (s, id, query, ref) => { await s.page.locator("#" + id).fill(query); await s.page.locator(`#${id}-sugg [data-pick="${ref}"]`).dispatchEvent("mousedown"); };
const stored = (s, kind) => s.page.evaluate(async t => (await jscStore.files(jscStore.activeSet())).filter(r => r.type === t).map(r => JSON.parse(r.text)), kind);
const today = s => s.page.evaluate(() => jscToday());
/* the active set, exported through the hub's button, as a folder on disk */
async function exported(s) {
  await toHub(s);
  const download = s.page.waitForEvent("download");
  await s.page.locator("#btn-export").click();
  const files = await core.jscUnzip(fs.readFileSync(await (await download).path()));
  const out = fs.mkdtempSync(path.join(os.tmpdir(), "jascon-app-authors-"));
  for (const x of files) { fs.mkdirSync(path.dirname(path.join(out, x.path)), { recursive: true }); fs.writeFileSync(path.join(out, x.path), x.text); }
  return { out, dir: path.join(out, fs.readdirSync(out)[0]), manifest: JSON.parse(files.find(x => x.path.endsWith("/content-manifest.json")).text) };
}
/* What validate_core.py says about a bundle folder. -> { green, summary, said: the AUTHOR and REVIEW lines it
   printed for this bundle, failures: the failures it lists for it }. The notes of a bundle stand above its
   summary line; a required author that is missing is listed as a failure at the end. */
function reference(dir, flags = [], t = null, what = "") {
  const out = referenceRun(dir, flags);
  /* what was measured goes into the test's output, so that a run says more than "ok" */
  if (t) t.diagnostic(`validate_core.py ${flags.join(" ")} on ${what}: ${out.summary.replace(/^.*?: (\d+ pass, \d+ fail).*$/, "$1")}; ${out.green ? "ALL GREEN" : "not green"}; ` +
    `${out.said.filter(l => /AUTHOR/.test(l)).length + out.failures.filter(l => /AUTHOR/.test(l)).length} AUTHOR line(s), ${out.said.filter(l => /REVIEW/.test(l)).length} REVIEW line(s)`);
  return out;
}
function referenceRun(dir, flags) {
  const run = spawnSync("python3", [path.join(ROOT, "jascon/scripts/validate_core.py"), dir, ...flags], { encoding: "utf8", cwd: ROOT });
  /* the bundle named on the command line is judged first: its summary is the first one after the heading */
  const lines = run.stdout.split(/\r?\n/), from = lines.indexOf("== bundles =="), end = lines.findIndex((l, i) => i > from && /^ {2}\S.*: \d+ pass, \d+ fail {2}\{/.test(l));
  assert.ok(from >= 0 && end > from, "the reference printed a summary for the bundle:\n" + run.stdout.slice(-1500) + run.stderr.slice(-1500));
  const summary = lines[end].trim(), section = `- [${summary.match(/^(.*?): \d+ pass, \d+ fail/)[1]}] `, above = lines.slice(from, end).map(l => l.trim());
  return { green: run.status === 0 && /\nALL GREEN\s*$/.test(run.stdout), summary,
    said: above.filter(l => /\((AUTHOR-[1-4]|REVIEW-1)[):]/.test(l)),
    /* backlog #46: what every Attestation binds, the state of its envelope, and how many objects of which type were counted */
    binds: above.filter(l => l.startsWith("binds: ")), dsse: above.filter(l => l.startsWith("dsse: ")),
    types: JSON.parse(summary.slice(summary.indexOf("{")).replace(/'/g, '"')), pass: +summary.match(/: (\d+) pass,/)[1],
    failures: lines.map(l => l.trim()).filter(l => l.startsWith(section)).map(l => l.slice(section.length)), stdout: run.stdout };
}
/* What the Validate page shows about the Attestations of the set after a check: the sentence on what was compared,
   every line as shown, and from the result the page holds the envelope lines in the reference's spelling, the
   counts by type and the errors. */
async function attestationsShown(s) {
  const p = s.page, box = p.locator("#report-binds");
  return { basis: await box.count() ? await box.locator("[data-binds-basis]").getAttribute("data-binds-basis") : null,
    said: await box.count() ? await box.locator("[data-binds-basis]").innerText() : "",
    lines: await p.locator("#report-binds [data-binds]").evaluateAll(list => list.map(n => ({ kind: n.dataset.binds, verdict: n.dataset.verdict,
      text: n.querySelector("[data-binds-text]").textContent, advice: (n.querySelector("[data-binds-advice]") || { textContent: "" }).textContent,
      listed: n.querySelector("[data-manifest-1]") ? n.querySelector("[data-manifest-1]").getAttribute("data-manifest-1") : null, listedText: (n.querySelector("[data-manifest-1]") || { textContent: "" }).textContent }))),
    ...await p.evaluate(() => ({ types: last.types, objects: jscSet.graph.objects.size,
      dsse: last.findings.filter(f => f.area === "signature").map(f => `dsse: ${f.object} = ${f.message}`),
      errors: last.findings.filter(f => f.kind === "error").map(f => f.message),
      rows: last.findings.filter(f => f.area === "attestation").map(f => [f.kind, f.object, f.message]) })) };
}
/* a line as the page shows it, from the reference's: a failure is listed without the word, a line is printed as it is */
const asShown = ref => [...ref.binds.map(l => ["line", l]), ...ref.failures.filter(m => m.startsWith("[attestation-binds] ")).map(m => ["failure", "error: " + m])];
const sortedTypes = t => Object.fromEntries(Object.entries(t).sort(([a], [b]) => (a < b ? -1 : 1)));
/* the lines of the two reports as the Validate page shows them, for the day and the switch given */
async function validatePage(s, { asOf, requireAuthors } = {}) {
  await open(s, "validate.html");
  if (asOf) await type(s.page.locator("#asof"), asOf);
  if (requireAuthors !== undefined) await s.page.locator("#require-authors").setChecked(requireAuthors);
  await s.page.locator("#run").click();
  await s.page.locator("#out #report-author").waitFor({ timeout: 60000 });
  const lines = id => s.page.locator(`#${id} [data-line]`).evaluateAll(list => list.map(n => ({ kind: n.dataset.line, rule: n.dataset.rule, text: n.textContent })));
  const rows = (await s.page.locator("#out table.flat tr").allTextContents()).map(r => r.replace(/\s+/g, " ").trim());
  return { author: await lines("report-author"), review: await lines("report-review"), errors: rows.filter(r => /^error/.test(r)), rows };
}

/* the tool pages are the HTML files the hub lists; the test must not keep a list of its own */
const hub = fs.readFileSync(path.join(APP, "index.html"), "utf8");
const TOOLS = [...hub.matchAll(/file: "([a-z-]+\.html)"/g)].map(m => m[1]);

test("the hub lists every tool page that exists, and every listed page exists", () => {
  const onDisk = fs.readdirSync(APP).filter(f => f.endsWith(".html") && !["index.html", "config.html"].includes(f)).sort();
  assert.deepEqual([...TOOLS].sort(), onDisk);
});

test("every page starts without a script error, in English and in German", { skip: !chromium && "Playwright with Chromium is not installed" }, async () => {
  /* The server lists its folders, as `python -m http.server` does: since build 0.9.24 a load from a URL asks for the
     bundle's folder once, and on a server that lists nothing that request is a line in the browser's console (the
     test of the URL load holds that line). The IFA bundle arrives with its Attestation here. */
  const server = await serve(true), base = `http://127.0.0.1:${server.address().port}/jascon-app/`;
  const browser = await chromium.launch();
  try {
    const page = await (await browser.newContext()).newPage();
    const errors = [];
    page.on("pageerror", e => errors.push(`${page.url().split("/").pop()}: ${e.message}`));
    page.on("console", m => { if (m.type() === "error") errors.push(`${page.url().split("/").pop()}: ${m.text()}`); });
    await page.goto(base + "index.html#load=../converted_examples/US.IFA-GoodRead/ifa-core-bundle/");
    await page.waitForFunction(() => document.querySelector("#home-log .l-ok"), null, { timeout: 60000 });
    for (const lang of ["en", "de"]) {
      await page.evaluate(l => localStorage.setItem("jsc:cfg:ui:lang", l), lang);
      for (const file of TOOLS) {
        await page.goto(base + file);
        await page.locator("#log .l-ok").first().waitFor({ timeout: 30000 });   // the set was read and the page rendered
        const views = await page.locator(".navitem[data-view]").count();
        assert.ok(views >= 2, file + " has its views");
        for (let i = 0; i < views; i++) await page.locator(".navitem[data-view]").nth(i).click();
        assert.equal(await page.evaluate(() => document.documentElement.lang), lang, file);
      }
      await page.goto(base + "config.html");
      await page.locator("#fields .field").first().waitFor();
      await page.goto(base + "index.html");
      await page.waitForFunction(() => document.querySelector("#help h1"));
    }
    assert.deepEqual(errors, []);
  } finally {
    await browser.close();
    server.close();
  }
});

/* ERRATA 2026-11-12 and CP-ADVICE-1 §4.6, in the pages themselves. The
   server of this file lists no folders, so the pack is handed over as the
   ZIP a vendor publishes; the files of the base set are picked as loose
   files. Nothing here loads from a URL. */
test("a system built on the Implement page validates; an advice pack is previewed, imported once, adopted, and the export passes the reference validator", { skip: !chromium && "Playwright with Chromium is not installed" }, async () => {
  const server = await serve(), base = `http://127.0.0.1:${server.address().port}/jascon-app/`;
  const browser = await chromium.launch();
  const PACK = path.join(ROOT, "jascon/example-packs/dbvendor-server-7-advice"), EX = path.join(ROOT, "jascon/examples");
  const tree = (dir, prefix = "") => fs.readdirSync(dir).sort().flatMap(n => fs.statSync(path.join(dir, n)).isDirectory()
    ? tree(path.join(dir, n), prefix + n + "/") : [{ path: prefix + n, text: core.jscDecode(fs.readFileSync(path.join(dir, n))) }]);
  const zip = { name: "server-7-advice.zip", mimeType: "application/zip", buffer: Buffer.from(core.jscZip(tree(PACK).map(f => ({ ...f, path: "server-7-advice/" + f.path })))) };
  try {
    const page = await (await browser.newContext({ acceptDownloads: true })).newPage();
    const errors = [];
    page.on("pageerror", e => errors.push(`${page.url().split("/").pop()}: ${e.message}`));
    page.on("console", m => { if (m.type() === "error") errors.push(`${page.url().split("/").pop()}: ${m.text()}`); });
    page.on("dialog", d => { errors.push("a dialog asked: " + d.message()); d.dismiss(); });   // nothing here may ask to replace the set
    const f = page.frameLocator("#app-frame");
    const tool = async id => { await page.locator(`#tabs [data-id="${id}"]`).click(); if (id !== "home") await f.locator("#log .l-ok").first().waitFor({ timeout: 30000 }); };
    const stored = () => page.evaluate(async () => (await jscStore.files(jscStore.activeSet())).map(r => r.path).sort());
    const validate = async () => {
      await tool("validate");
      await f.locator("#run").click();
      await f.locator("#out .chip").first().waitFor({ timeout: 60000 });
      const rows = (await f.locator("#out table.flat tr").allTextContents()).map(r => r.replace(/\s+/g, " ").trim());
      return { errors: rows.filter(r => /^error/.test(r)), advice: rows.filter(r => /^noteadvice/.test(r)) };
    };
    await page.goto(base + "index.html");
    await page.waitForFunction(() => document.querySelector("#help h1"));
    await page.evaluate(() => localStorage.setItem("jsc:cfg:ui:lang", "en"));
    await page.locator("#pick-files").setInputFiles([path.join(EX, "req-konf-14-1.json"), path.join(EX, "gspp-taxonomy-1.1.0.json")]);
    await page.waitForFunction(() => document.querySelector("#home-log .l-ok"));

    /* a system, built the way the page builds one: every edge cites a capability its asset declares */
    await tool("implement");
    await f.locator('.navitem[data-view="build"]').click();
    await f.locator("#sys-title").fill("Shop");
    await f.locator("#sys-title").dispatchEvent("change");
    await f.locator("#new-title").fill("Order database");
    await f.locator("#new-pv").fill("7.2");
    await f.locator("#add-asset").click();
    await f.locator("#pick-0").fill("KONF");
    await f.locator("#pick-0-sugg [data-pick]").first().dispatchEvent("mousedown");
    await f.locator(".wbchip").first().waitFor();
    await f.locator("#sys-save").click();
    await f.locator("#system .stmt").first().waitFor();
    const edge = await page.evaluate(async () => (await jscStore.files(jscStore.activeSet())).filter(r => r.type === "implementation").map(r => JSON.parse(r.text)));
    assert.deepEqual(edge.map(e => e["satisfied-by"]), [[{ "capability-ref": "cap-konf-14-1" }]], "the edge cites the capability its asset declares, not a literal");
    assert.match((await f.locator("#system .stmt").first().innerText()), /product version 7\.2/);
    assert.deepEqual((await validate()).errors, [], "a system the page built has no error, ADVICE-7 included");

    /* the pack: shown before anything is written */
    await tool("home");
    const before = await stored();
    await page.locator("#pick-pack-files").setInputFiles(zip);
    await page.locator("#pack-import").waitFor({ timeout: 30000 });
    const preview = await page.locator("#pack-preview").innerText();
    for (const want of ["https://dbvendor.example/pack/server-7-hardening", "Example DB Vendor Inc.", "https://dbvendor.example/party/vendor", "attested, not verified",
      "product version 7", "cap-tls", "cap-key-rotation", "cap-audit-log", "transport-crypto = \"tls13\"", "statement s2"]) assert.ok(preview.includes(want), `the preview shows ${want}`);
    /* no trusted key is set: an attestation that binds the manifest is shown as attested, in amber, never as proof */
    assert.equal(await page.locator("#pack-preview [data-publisher]").getAttribute("data-publisher"), "attested");
    assert.match(await page.locator("#pack-preview [data-publisher]").getAttribute("style"), /--amber/);
    assert.deepEqual(await stored(), before, "the preview writes nothing");
    await page.locator("#pack-import").click();
    await page.locator("#pack-receipt").waitFor();
    assert.equal(await page.locator("#pack-receipt").innerText(), "unchanged 4 of 4 · added 1 components");
    const after = await stored();
    assert.deepEqual(after.filter(p => !before.includes(p)), ["attestation-dbvendor-server-7-advice.dsse", "attestation-dbvendor-server-7-advice.json",
      "objects/component/server-7.json", "packs/sha256/" + await core.jscSha256(fs.readFileSync(path.join(PACK, "content-manifest.json"), "utf8"))]);
    assert.match(await page.locator("#pack-list").innerText(), /Server 7 hardening advice[\s\S]*release 3[\s\S]*attested, not verified/);

    /* the same file again, through the pack button and through the button that loads a bundle: nothing is written, nothing replaced */
    for (const input of ["#pick-pack-files", "#pick-files"]) {
      await page.locator(input).setInputFiles(zip);
      await page.locator("#pack-preview", { hasText: "Already imported: release 3" }).waitFor();
      assert.deepEqual(await stored(), after, input + ": the set is as it was");
      await page.locator("#pack-cancel").click();
    }

    /* adoption: the product becomes a member, and an edge of the user's system cites the vendor's capability */
    await tool("implement");
    await f.locator('.navitem[data-view="advice"]').click();
    assert.match(await f.locator("#advice [data-pack]").first().innerText(), /release 3[\s\S]*attested, not verified/);
    await f.locator("#adv-own").selectOption({ label: "Shop" });
    const product = f.locator('[data-product="https://dbvendor.example/component/server-7"]');
    assert.equal(await product.locator("[data-adopt]").count(), 0, "no adoption before the product is a member");
    await product.locator("[data-member]").click();
    await f.locator('[data-adopt$="#cap-key-rotation"]').click();
    await f.locator("#advice .badge", { hasText: "adopted" }).first().waitFor();
    await f.locator('[data-copy$="cap-tls|transport-crypto"]').check();
    await f.locator('[data-adopt$="#cap-tls"]').click();
    await f.locator("#log .l-ok", { hasText: "#cap-tls" }).first().waitFor();
    assert.equal(await f.locator('[data-adopt$="#cap-audit-log"]').count(), 0, "advice about a requirement the set does not hold cannot be adopted");
    const edges = await page.evaluate(async () => (await jscStore.files(jscStore.activeSet())).filter(r => r.type === "implementation").map(r => JSON.parse(r.text)));
    const cites = edges.filter(e => e["component-ref"].endsWith("/comp/shop"));
    assert.deepEqual(cites.map(e => e["satisfied-by"][0]["capability-ref"]).sort(), ["https://dbvendor.example/component/server-7#cap-key-rotation", "https://dbvendor.example/component/server-7#cap-tls"]);
    assert.deepEqual(cites.find(e => e["satisfied-by"][0]["capability-ref"].endsWith("#cap-tls"))["parameter-bindings"], { "transport-crypto": "tls13" });
    const checked = await validate();
    assert.deepEqual(checked.errors, []);
    assert.ok(checked.advice.some(r => /kept pack \(1 object\(s\)\).*release 3.*publisher ATTESTED, NOT VERIFIED/.test(r)), "the check reports the kept pack: " + checked.advice.join(" | "));
    assert.equal(await f.locator("#out [data-publisher]").getAttribute("data-publisher"), "attested");
    /* backlog #46: the vendor's Attestation came with the pack and binds the pack manifest the set keeps */
    const bindsShown = await f.locator("#report-binds [data-binds-text]").allTextContents();
    assert.deepEqual(bindsShown, [`binds: ${VENDOR_ATT} = FULL MATCH [1 subject(s) of this bundle; a pack manifest this bundle keeps]`]);
    assert.equal(await f.locator("#report-binds [data-binds-basis]").getAttribute("data-binds-basis"), "none", "a set built here has no manifest yet; the page compares with the one an export writes");

    /* the export carries the vendor's manifest, and the reference validator accepts the set */
    await tool("home");
    const download = page.waitForEvent("download");
    await page.locator("#btn-export").click();
    const files = await core.jscUnzip(fs.readFileSync(await (await download).path()));
    assert.ok(files.some(x => /\/packs\/sha256\/[0-9a-f]{64}$/.test(x.path)), "the kept pack manifest is in the export");
    if (spawnSync("python3", ["-c", "import jsonschema"]).status === 0) {
      const out = fs.mkdtempSync(path.join(os.tmpdir(), "jascon-app-pages-"));
      for (const x of files) { fs.mkdirSync(path.dirname(path.join(out, x.path)), { recursive: true }); fs.writeFileSync(path.join(out, x.path), x.text); }
      const dir = path.join(out, fs.readdirSync(out)[0]);
      const run = spawnSync("python3", [path.join(ROOT, "jascon/scripts/validate_core.py"), dir], { encoding: "utf8" });
      const lines = run.stdout.split("\n"), line = lines.find(l => l.includes(path.basename(out))) || "";
      fs.rmSync(out, { recursive: true });
      assert.match(line, / 0 fail/, run.stdout.slice(-1500));
      assert.deepEqual(lines.slice(0, lines.indexOf(line)).map(l => l.trim()).filter(l => l.startsWith("binds: ")), bindsShown, "what the page said about the Attestation is what the reference prints for the exported folder");
    }

    /* the publisher is shown as proven, in green, only once a key the user trusts verifies the envelope;
       the worked pack is signed with the fixture key of the conformance corpus */
    const signer = "https://dbvendor.example/party/vendor", key = JSON.parse(fs.readFileSync(path.join(ROOT, "jascon/conformance/advice-vectors.json"), "utf8"))["fixture-public-key"];
    const publisherWith = async keys => {
      await page.evaluate(k => localStorage.setItem("jsc:cfg:draft:validate:" + jscStore.activeSet(), JSON.stringify({ keys: k ? JSON.stringify(k) : "", other: "" })), keys);
      await page.reload();
      await page.locator("#pack-list [data-publisher]").waitFor();
      return [await page.locator("#pack-list [data-publisher]").getAttribute("data-publisher"), /--green/.test(await page.locator("#pack-list [data-publisher]").getAttribute("style"))];
    };
    assert.deepEqual(await publisherWith(null), ["attested", false]);
    assert.deepEqual(await publisherWith({ [signer]: key }), ["proven", true]);
    assert.deepEqual(await publisherWith({ [signer]: "00".repeat(32) }), ["claimed", false]);
    assert.match(await page.locator("#pack-list").innerText(), /not proven by .*no signature verifies under the trusted key/);
    assert.deepEqual(errors, []);
  } finally {
    await browser.close();
    server.close();
  }
});

/* ====================================================================
   Who decided, and when: the two reports on the Validate page
   ====================================================================
   The page shows the lines the reference validator prints for the same set
   and the same day. Both are asked here, on the two folders the reference
   is known to report on, for two days and with the switch off and on. */
test("Validate: the AUTHOR and REVIEW lines are the reference validator's, for the day asked about; requiring authors turns AUTHOR lines into errors and no REVIEW line", { skip: needs }, async t => {
  const REVIEW = l => /REVIEW-1/.test(l), counts = {};
  for (const [dir, name] of [[EX, "examples"], [IFA, "ifa"]]) {
    const s = await session();
    try {
      await load(s, zipOf(dir, name));
      /* nothing typed: the day is today's, in UTC, and the switch is off */
      await open(s, "validate.html");
      assert.equal(await s.page.locator("#asof").inputValue(), await today(s));
      assert.equal(await s.page.locator("#require-authors").isChecked(), false);
      for (const asOf of [AS_OF, "2023-06-24"]) {
        const ref = reference(dir, ["--as-of", asOf], t, name), shown = await validatePage(s, { asOf, requireAuthors: false });
        assert.deepEqual([...shown.author, ...shown.review].map(l => l.text), ref.said, `${name} as of ${asOf}`);
        assert.ok(shown.author.every(l => l.kind === "note"));
        assert.ok(ref.green);
        const strictRef = reference(dir, ["--require-authors", "--as-of", asOf], t, name), strict = await validatePage(s, { asOf, requireAuthors: true });
        assert.deepEqual(strict.author.map(l => [l.kind, l.text]), strictRef.failures.map(m => ["error", "error: " + m]), `${name} as of ${asOf}, authors required`);
        assert.deepEqual(strict.review.map(l => l.text), strictRef.said.filter(REVIEW), "the REVIEW lines are as before");
        assert.ok(strict.review.every(l => l.kind !== "error"), "REVIEW-1 never fails anything");
        assert.equal(strict.errors.length - shown.errors.length, strictRef.failures.length, "each required author that is missing is one error more, and nothing else is");
        assert.equal(strictRef.green, strictRef.failures.length === 0);
        counts[`${name} ${asOf}`] = [shown.author.length, shown.review.length];
      }
      /* the switch is kept for the set; the day is not: a reload starts from today again */
      await open(s, "validate.html");
      assert.equal(await s.page.locator("#require-authors").isChecked(), true);
      assert.equal(await s.page.locator("#asof").inputValue(), await today(s));
      assert.deepEqual(s.errors, []);
    } finally { await s.close(); }
  }
  /* what was compared: the example folder names every author and has one review date nobody can evaluate; the IFA
     bundle misses seven (ten until its converter pre-filled what the source states, 2026-11-13), and its two review
     dates of 2023 and 2024 are overdue or not with the day asked about */
  assert.deepEqual(counts, { [`examples ${AS_OF}`]: [0, 2], "examples 2023-06-24": [0, 2], [`ifa ${AS_OF}`]: [7, 3], "ifa 2023-06-24": [7, 2] });
});

/* ====================================================================
   An Attestation is held to what it binds (backlog #46)
   ====================================================================
   The reference prints one line per Attestation it reads with a bundle, or
   lists one failure. The app must say the same about the same folder, word
   for word, and count the same objects. The folders are read as they lie.
   The hub never loads an advice pack over a set (it offers it for import),
   so the pack folder is held to the reference through the rules, on its
   graph, and in the browser the way a user gets one: imported and exported. */
const AS_OF_46 = "2026-11-14", PACK = path.join(ROOT, "jascon/example-packs/dbvendor-server-7-advice"), FIXTURE_KEYS = path.join(ROOT, "jascon/conformance/fixture-trusted-keys.json");
const ACME_ATT = "https://agency-x.example/attestation/acme-2026", VENDOR_ATT = "https://dbvendor.example/attestation/server-7-hardening-3", IFA_ATT = "https://ifa.gov/goodread/attestation/ifa-ato";
const B17 = "(B.1.7: an Attestation binds what is delivered, or it fails; a changed subject is normative content changed after signing)";
const nodeSha256 = bytes => crypto.createHash("sha256").update(bytes).digest("hex");
const byText = pairs => [...pairs].sort((a, b) => (a[1] < b[1] ? -1 : a[1] > b[1] ? 1 : 0));

test("Validate: what every Attestation binds is the reference's line for three folders as they lie; counts and envelopes agree; with the fixture keys both signatures of the example folder verify", { skip: needs }, async t => {
  const rules = createRequire(import.meta.url)("../jascon-rules.js"), keys = JSON.parse(fs.readFileSync(FIXTURE_KEYS, "utf8")), measured = {};
  const graphOf = dir => core.jscGraphFrom(core.jscClassifyFiles(core.jscKeepFiles(tree(dir))).records);
  /* 1. the rules on the graph of each folder, without keys and with them */
  for (const [dir, name] of [[EX, "examples"], [IFA, "ifa"], [PACK, "pack"]]) {
    for (const trusted of [null, keys]) {
      const ref = referenceRun(dir, ["--as-of", AS_OF_46, ...(trusted ? ["--trusted-keys", FIXTURE_KEYS] : [])]);
      const g = graphOf(dir), res = await rules.jscCheckGraph(g, await core.jscVerify(g), { asOf: AS_OF_46, trusted });
      assert.ok(ref.green, name);
      assert.equal(res.binds.basis, "loaded", name);
      assert.deepEqual(res.binds.lines.map(l => [l.kind, l.text]), asShown(ref), name + ": the lines");
      assert.deepEqual(res.findings.filter(f => f.area === "signature").map(f => `dsse: ${f.object} = ${f.message}`), ref.dsse, name + ": the envelopes");
      assert.deepEqual(sortedTypes(res.types), sortedTypes(ref.types), name + ": the counts by type");
      assert.equal(g.objects.size + 1, ref.pass, name + ": the reference counts every object and the manifest");
      assert.deepEqual(res.findings.filter(f => f.kind === "error"), [], name);
      measured[name + (trusted ? " with keys" : "")] = [ref.pass, ...ref.binds.map(l => l.replace(/^binds: \S+ = /, "").replace(/ \[.*; /, " [").replace(/\]$/, "]")), ...ref.dsse.map(l => l.replace(/^dsse: \S+ = /, "").split(" - ")[0])];
    }
  }
  t.diagnostic("validate_core.py --as-of 2026-11-14, pass count, binds and dsse per folder: " + JSON.stringify(measured));
  assert.deepEqual(measured, {
    examples: [27, "FULL MATCH [this manifest]", "FULL MATCH [a pack manifest this bundle keeps]", "signature UNVERIFIED", "signature UNVERIFIED"],
    "examples with keys": [27, "FULL MATCH [this manifest]", "FULL MATCH [a pack manifest this bundle keeps]", "signature VERIFIED (Ed25519)", "signature VERIFIED (Ed25519)"],
    ifa: [18, "FULL MATCH [this manifest]", "no envelope (unsigned attestation)"], "ifa with keys": [18, "FULL MATCH [this manifest]", "no envelope (unsigned attestation)"],
    pack: [3, "FULL MATCH [this manifest]", "signature UNVERIFIED"], "pack with keys": [3, "FULL MATCH [this manifest]", "signature VERIFIED (Ed25519)"],
  });

  /* 2. the Validate page, for the two folders the hub loads as a set */
  for (const [dir, name] of [[EX, "examples"], [IFA, "ifa"]]) {
    const s = await session(), p = s.page;
    try {
      await load(s, zipOf(dir, name));
      const ref = referenceRun(dir, ["--as-of", AS_OF_46]);
      await validatePage(s, { asOf: AS_OF_46, requireAuthors: false });
      const shown = await attestationsShown(s);
      assert.equal(shown.basis, "loaded");
      assert.match(shown.said, /^Compared with the bundle as it was loaded: the manifest this set came with \(sha256:[0-9a-f]{12}…\) and the objects it lists\.$/);
      assert.deepEqual(shown.lines.map(l => [l.kind, l.text]), asShown(ref), name + ": the page's lines are the reference's");
      assert.ok(shown.lines.every(l => l.verdict === "full-match" && l.advice === ""), "a Full Match needs no advice");
      assert.deepEqual(shown.rows, ref.binds.map(l => ["note", l.match(/^binds: (\S+) = /)[1], l.replace(/^binds: \S+ = /, "")]), "the same in the table of findings");
      assert.deepEqual(shown.dsse, ref.dsse);
      assert.deepEqual(sortedTypes(shown.types), sortedTypes(ref.types));
      assert.equal(shown.objects + 1, ref.pass);
      assert.equal(+(await p.locator("#out .chip b").first().innerText()), shown.objects, "the count the page states is the count of objects, the Attestation beside the manifest among them");
      assert.deepEqual(shown.errors, []);
      if (name === "examples") {
        /* verification mode: the public key of the corpus fixture, for the two signers of the folder */
        await p.locator("#keys-box summary").click();
        await p.locator("#keys").fill(fs.readFileSync(FIXTURE_KEYS, "utf8"));
        assert.match(await p.locator("#keys-state").innerText(), /^2 trusted key\(s\): the check runs in verification mode$/);
        const withKeys = referenceRun(dir, ["--as-of", AS_OF_46, "--trusted-keys", FIXTURE_KEYS]);
        await validatePage(s, { asOf: AS_OF_46, requireAuthors: false });
        const verified = await attestationsShown(s);
        assert.deepEqual(verified.dsse, withKeys.dsse);
        assert.deepEqual(verified.dsse, [`dsse: ${ACME_ATT} = signature VERIFIED (Ed25519)`, `dsse: ${VENDOR_ATT} = signature VERIFIED (Ed25519)`]);
        assert.deepEqual(await p.locator("[data-signature] span").allInnerTexts(), ["verified", "verified"]);
        assert.deepEqual(verified.lines.map(l => [l.kind, l.text]), asShown(withKeys), "the verdict is about digests: keys change nothing in it");
        assert.equal(await p.locator("[data-publisher]").getAttribute("data-publisher"), "proven");
        assert.deepEqual(verified.errors, []);
      }
      assert.deepEqual(s.errors, []);
    } finally { await s.close(); }
  }
});

/* MANIFEST-1 (D3.11; backlog #75): no content manifest lists an Attestation. The copies are built as the reference's
   own test builds them (test_attestation_binds.py, c10-listed and c11-pack-listed): the Attestation is moved under
   objects/ and entered in the manifest with both digests, so that nothing else is wrong with the bundle. */
async function listedCopy(dir, attFile, tmp) {
  const out = fs.mkdtempSync(path.join(os.tmpdir(), "jascon-app-listed-")); tmp.push(out);
  const copy = path.join(out, path.basename(dir)), rel = "objects/attestation/" + attFile;
  fs.cpSync(dir, copy, { recursive: true });
  const raw = fs.readFileSync(path.join(copy, attFile)), att = JSON.parse(raw.toString("utf8"));
  fs.mkdirSync(path.join(copy, "objects/attestation"), { recursive: true });
  fs.renameSync(path.join(copy, attFile), path.join(copy, rel));
  const mp = path.join(copy, "content-manifest.json"), m = JSON.parse(fs.readFileSync(mp, "utf8"));
  m.objects.push({ id: att.id, version: att.version, path: rel, "package-digest": "sha256:" + nodeSha256(raw), "semantic-digest": await core.jscSemanticDigest(att) });
  fs.writeFileSync(mp, JSON.stringify(m, null, 1) + "\n");
  return copy;
}
const MANIFEST_1 = id => `${id}: an Attestation is listed in the content manifest (MANIFEST-1: Attestations are excluded from the content manifest by definition, D3.1 - ` +
  "an Attestation lies beside a manifest and is never an entry of one)";

test("MANIFEST-1: a set whose manifest lists an Attestation fails as the reference fails the folder, in a pack with ADVICE-1 beside it; unchanged it leaves as it came; changed, the export leaves the Attestation out and says so", { skip: needs }, async t => {
  const tmp = [], rules = createRequire(import.meta.url)("../jascon-rules.js");
  t.after(() => { for (const d of tmp) fs.rmSync(d, { recursive: true, force: true }); });
  const graphOf = dir => core.jscGraphFrom(core.jscClassifyFiles(core.jscKeepFiles(tree(dir))).records);
  /* 1. the rules on two changed copies, an ordinary bundle and a pack: the failures are the reference's, all of them */
  const counted = {};
  for (const [dir, file, id, name] of [[IFA, "attestation-ifa-ato.json", IFA_ATT, "ifa"], [PACK, "attestation-dbvendor-server-7-advice.json", VENDOR_ATT, "pack"]]) {
    const copy = await listedCopy(dir, file, tmp), ref = referenceRun(copy, ["--as-of", AS_OF_46]);
    const g = graphOf(copy), res = await rules.jscCheckGraph(g, await core.jscVerify(g), { asOf: AS_OF_46 });
    const errors = res.findings.filter(f => f.kind === "error").map(f => (f.object && f.area === "manifest" ? `${f.object}: ${f.message}` : f.message));
    assert.equal(ref.green, false, name);
    assert.ok(ref.failures.includes(MANIFEST_1(id)), name + ": the reference lists MANIFEST-1: " + ref.failures.join(" | "));
    assert.deepEqual([...errors].sort(), [...ref.failures].sort(), name + ": the errors of the check are the reference's failures");
    assert.deepEqual(res.binds.lines.map(l => [l.kind, l.text]), asShown(ref), name + ": the Attestation is still held to what it binds");
    assert.deepEqual(res.binds.lines.map(l => [l.listed, l["manifest-1"]]), [["refused", MANIFEST_1(id)]]);
    counted[name] = [ref.pass, ref.failures.length, ref.binds[0].replace(/^binds: \S+ = /, "").split(" [")[0]];
  }
  t.diagnostic("validate_core.py on the two copies that list their Attestation, pass count, failures, verdict: " + JSON.stringify(counted));
  assert.deepEqual(counted, { ifa: [18, 1, "SEMANTIC MATCH"], pack: [3, 2, "SEMANTIC MATCH"] });

  /* 2. the pages, on the copy of the IFA bundle */
  const copy = await listedCopy(IFA, "attestation-ifa-ato.json", tmp), ref = referenceRun(copy, ["--as-of", AS_OF_46]);
  const s = await session(), p = s.page;
  try {
    await load(s, zipOf(copy, "ifa"));
    assert.match(await p.locator("#home-log .l-warn").allInnerTexts().then(x => x.join(" | ")), /content-manifest\.json lists an Attestation \(objects\/attestation\/attestation-ifa-ato\.json\), which no content manifest may \(MANIFEST-1\)\. The set is kept as it came/,
      "the hub says it when the bundle arrives, and changes nothing");
    await validatePage(s, { asOf: AS_OF_46, requireAuthors: false });
    const refused = await attestationsShown(s);
    assert.equal(refused.basis, "loaded");
    assert.deepEqual(refused.lines.map(l => [l.kind, l.text]), asShown(ref), "the binding is still shown: a Semantic Match here, since the manifest that lists it is not the one it binds");
    assert.deepEqual(refused.lines.map(l => [l.listed, l.listedText]), [["refused", "error: " + MANIFEST_1(IFA_ATT)]]);
    assert.deepEqual(refused.errors.map(m => `${IFA_ATT}: ${m}`), ref.failures, "one error, the reference's");
    /* the Assess page says the same about the Attestation */
    await open(s, "assess.html", "board");
    const card = p.locator(`[data-att-card="${IFA_ATT}"]`);
    await card.locator("[data-att]").click();
    assert.equal(await card.locator('[data-manifest-1="refused"]').innerText(), "error: " + MANIFEST_1(IFA_ATT));
    /* nobody changed the set: it leaves as it came, with the manifest that lists the Attestation, and the reference refuses the export as it refuses the folder */
    const same = await exported(s); tmp.push(same.out);
    assert.equal(fs.readFileSync(path.join(same.dir, "content-manifest.json"), "utf8"), fs.readFileSync(path.join(copy, "content-manifest.json"), "utf8"), "nothing is repaired in silence");
    assert.ok(fs.existsSync(path.join(same.dir, "objects/attestation/attestation-ifa-ato.json")));
    assert.deepEqual(referenceRun(same.dir, ["--as-of", AS_OF_46]).failures, ref.failures);

    /* something else in the set is changed: the manifest in question is now the one an export writes, and that lists no Attestation */
    const risk = (await stored(s, "risk"))[0];
    await p.evaluate(async ([id, title]) => { await jscSet.load(); await jscSet.saveObjects([{ ...jscSet.graph.objects.get(id).obj, title }]); }, [risk.id, { en: "Reworded" }]);
    await validatePage(s, { asOf: AS_OF_46, requireAuthors: false });
    const after = await attestationsShown(s);
    assert.equal(after.basis, "changed");
    assert.deepEqual(after.lines.map(l => l.listed), ["left-out"]);
    assert.match(after.lines[0].listedText, /^The manifest this set came with lists this Attestation, which MANIFEST-1 refuses\. The set was changed since, and the manifest an export writes now does not list it/);
    assert.deepEqual(after.errors, [], "no failure: the bundle the page compares with lists no Attestation");
    const next = await exported(s); tmp.push(next.out);
    assert.match(await p.locator("#home-log .l-warn").allInnerTexts().then(x => x.join(" | ")), new RegExp(IFA_ATT.replace(/[.]/g, "\\.") + ": was listed in the manifest this set came with; a manifest written here lists no Attestation \\(MANIFEST-1\\), so it leaves beside the manifest as attestation-ifa-ato\\.json"),
      "the export says what it did");
    assert.deepEqual(next.manifest.objects.filter(e => /attestation/.test(e.id + e.path)), []);
    assert.deepEqual([fs.existsSync(path.join(next.dir, "attestation-ifa-ato.json")), fs.existsSync(path.join(next.dir, "objects/attestation/attestation-ifa-ato.json"))], [true, false], "the file lies beside the manifest now");
    const fixed = referenceRun(next.dir, ["--as-of", AS_OF_46]);
    assert.ok(fixed.green, fixed.stdout.slice(-800));
    assert.deepEqual(after.lines.map(l => [l.kind, l.text]), asShown(fixed), "what the page said before the export is what the reference says about the exported folder");
    assert.equal(fixed.pass, 18);
    assert.deepEqual(s.errors, []);
  } finally { await s.close(); }
});

/* Backlog #71, point 11 (build 0.9.24): the move as the user's act. A set that came with a manifest listing an
   Attestation and was not changed had no repair in the app: it left as it came, and the reference refused the export
   as it refused the folder (the test above holds that for a set nobody touched). Now the place that shows the failure
   offers to take the Attestation out of the manifest's list, and says before the click what that does to the binding:
   the line the Attestation gets against the manifest an export writes then. The reference is the judge of that line. */
test("MANIFEST-1, the move: where the listing is refused the page offers to take the Attestation out of the manifest's list and says what that does to the binding; only then the export writes a manifest without it, the file lies beside it unchanged, and the reference passes the folder with the binding that was announced", { skip: needs }, async t => {
  const tmp = [];
  t.after(() => { for (const d of tmp) fs.rmSync(d, { recursive: true, force: true }); });
  const copy = await listedCopy(IFA, "attestation-ifa-ato.json", tmp), ref = referenceRun(copy, ["--as-of", AS_OF_46]);
  const LISTED_AT = "objects/attestation/attestation-ifa-ato.json";
  assert.deepEqual(ref.failures, [MANIFEST_1(IFA_ATT)]);
  let s = await session(), p = s.page;
  try {
    await load(s, zipOf(copy, "ifa"));
    const before = await snapshot(s);
    await validatePage(s, { asOf: AS_OF_46, requireAuthors: false });
    const refused = await attestationsShown(s);
    assert.deepEqual(refused.lines.map(l => [l.listed, l.kind, l.text]), [["refused", ...asShown(ref)[0]]]);
    /* the offer: what is done, and what it does to the binding, before anything is done */
    const offer = p.locator("#report-binds [data-move-offer]");
    assert.match(await offer.innerText(), /^You can have the move made now\. The Attestation is taken out of the manifest's list in this set; the next export writes a new manifest without it and puts the file beside the manifest\. The Attestation itself is not changed, and its signature stays what it is\. What the move does to the binding: the Attestation keeps naming the manifest it was issued over, and the manifest an export writes is a new one\. Held to that bundle it reads: binds: /);
    const announced = await offer.locator("[data-move-after]").innerText();
    assert.match(announced, /^binds: https:\/\/ifa\.gov\/goodread\/attestation\/ifa-ato = SEMANTIC MATCH \[3 subject\(s\) of this bundle; another manifest/);
    assert.deepEqual(await snapshot(s), before, "an offer writes nothing");
    assert.equal(await p.evaluate(async () => (await jscStore.files(jscStore.activeSet())).filter(r => r.unlisted).length), 0);

    await p.locator(`#report-binds [data-move="${IFA_ATT}"]`).click();
    await p.locator('#report-binds [data-manifest-1="left-out"]').waitFor({ timeout: 60000 });
    const after = await attestationsShown(s);
    assert.equal(after.basis, "changed", "the set counts as changed, by this act and nothing else");
    assert.deepEqual(after.lines.map(l => [l.listed, l.kind, l.text]), [["left-out", "line", announced]], "the binding is what the page said the move would make it");
    assert.deepEqual(after.errors, [], "no MANIFEST-1 failure is left");
    assert.equal(await p.locator("#report-binds [data-move]").count(), 0, "and nothing is left to offer");
    assert.equal(await p.locator("#log .l-ok", { hasText: "taken out of the manifest's list" }).last().innerText().then(x => x.replace(/^[\d:.]+/, "")),
      `${IFA_ATT}: taken out of the manifest's list in this set. The file (${LISTED_AT}) and the Attestation are unchanged; the next export writes a new manifest without it and puts the file beside the manifest.`);
    /* in the set only the mark is new: every file has the bytes and the place it had, the manifest the set came with among them */
    assert.deepEqual(await snapshot(s), before);
    assert.deepEqual(await p.evaluate(async () => (await jscStore.files(jscStore.activeSet())).filter(r => r.unlisted).map(r => [r.path, r.type, r.origin])), [[LISTED_AT, "attestation", "imported"]]);

    const moved = await exported(s); tmp.push(moved.out);
    assert.match(await p.locator("#home-log .l-warn").allInnerTexts().then(x => x.join(" | ")), new RegExp(IFA_ATT.replace(/[.]/g, "\\.") + ": was listed in the manifest this set came with; a manifest written here lists no Attestation \\(MANIFEST-1\\), so it leaves beside the manifest as attestation-ifa-ato\\.json"),
      "the export says what it did");
    assert.deepEqual(moved.manifest.objects.filter(e => /attestation/.test(e.id + e.path)), []);
    assert.equal(moved.manifest.objects.length, JSON.parse(fs.readFileSync(path.join(copy, "content-manifest.json"), "utf8")).objects.length - 1, "one line less, the Attestation's");
    assert.deepEqual([fs.existsSync(path.join(moved.dir, "attestation-ifa-ato.json")), fs.existsSync(path.join(moved.dir, LISTED_AT))], [true, false], "the file lies beside the manifest now");
    assert.equal(fs.readFileSync(path.join(moved.dir, "attestation-ifa-ato.json"), "utf8"), fs.readFileSync(path.join(copy, LISTED_AT), "utf8"), "with the bytes it had");
    const fixed = referenceRun(moved.dir, ["--as-of", AS_OF_46]);
    t.diagnostic(`validate_core.py on the folder as it came: ${ref.pass} pass, ${ref.failures.length} failure(s); on the export after the move: ${fixed.pass} pass, ${fixed.failures.length} failure(s); ${fixed.binds[0]}`);
    assert.ok(fixed.green, fixed.stdout.slice(-800));
    assert.equal(fixed.pass, 18);
    assert.deepEqual(asShown(fixed), [["line", announced]], "the reference says about the exported folder what the page announced before the move");
    assert.deepEqual(s.errors, []);
  } finally { await s.close(); }
  /* the Assess page shows the same failure for one Attestation and offers the same move */
  s = await session(); p = s.page;
  try {
    await load(s, zipOf(copy, "ifa"));
    await open(s, "assess.html", "board");
    const card = p.locator(`[data-att-card="${IFA_ATT}"]`);
    await card.locator("[data-att]").click();
    assert.equal(await card.locator('[data-manifest-1="refused"]').innerText(), "error: " + MANIFEST_1(IFA_ATT));
    const announced = await card.locator("[data-move-after]").innerText();
    await card.locator(`[data-move="${IFA_ATT}"]`).click();
    await card.locator('[data-manifest-1="left-out"]').waitFor({ timeout: 60000 });
    assert.equal(await card.locator("[data-binds-text]").innerText(), announced);
    assert.deepEqual([await card.locator('[data-manifest-1="refused"]').count(), await card.locator("[data-move]").count()], [0, 0]);
    const moved = await exported(s); tmp.push(moved.out);
    assert.ok(referenceRun(moved.dir, ["--as-of", AS_OF_46]).green);
    assert.deepEqual(s.errors, []);
  } finally { await s.close(); }
});

/* Backlog #71, point 8 (build 0.9.24): the server is asked for the folder of every bundle, once, as the reader does
   since 1.13.0. Until build 0.9.23 it was asked only where a bundle keeps a pack, and the Attestation beside any other
   bundle's manifest did not arrive: the IFA bundle, which the project's site offers behind "Open in the app" and whose
   folder that site lists, came with 16 objects and without its Attestation (measured on a server that lists folders). */
test("a bundle from a URL: the server is asked once for the folder of every bundle; where it lists the folder, the Attestations beside the manifest are read and held to what they bind, with or without a pack; where it does not, the hub says so", { skip: needs }, async () => {
  const NO_LISTING = "This server does not list the folder of the bundle. A URL names files, not folders, so an Attestation beside the manifest could not be looked for, and none is held to what it binds; load the folder or a ZIP for that.";
  const folderRequests = (s, folder) => s.requests.filter(u => u === folder).length;
  /* the example folder keeps a vendor's pack */
  let s = await session({ list: true });
  try {
    await s.page.goto(s.base + "index.html#load=../jascon/examples/");
    await s.page.waitForFunction(() => document.querySelector("#home-log .l-ok"), null, { timeout: 60000 });
    assert.equal(await s.page.locator("#home-log .l-info", { hasText: "does not list the folder" }).count(), 0);
    assert.equal(folderRequests(s, "/jascon/examples/"), 1);
    const ref = referenceRun(EX, ["--as-of", AS_OF_46]);
    await validatePage(s, { asOf: AS_OF_46, requireAuthors: false });
    const shown = await attestationsShown(s);
    assert.deepEqual(shown.lines.map(l => [l.kind, l.text]), asShown(ref), "both Attestations were fetched: the set's own, which binds its manifest, and the vendor's");
    assert.deepEqual(shown.dsse, ref.dsse, "and their envelopes");
    assert.equal(shown.objects + 1, ref.pass);
    assert.deepEqual(shown.errors, []);
    assert.deepEqual(s.errors, []);
  } finally { await s.close(); }
  /* the IFA bundle keeps no pack and has its Attestation beside the manifest: on a server that lists the folder it arrives with it */
  const IFA_FOLDER = "/converted_examples/US.IFA-GoodRead/ifa-core-bundle/";
  s = await session({ list: true });
  try {
    await s.page.goto(s.base + "index.html#load=.." + IFA_FOLDER);
    await s.page.waitForFunction(() => document.querySelector("#home-log .l-ok"), null, { timeout: 60000 });
    assert.equal(await s.page.locator("#home-log .l-info", { hasText: "does not list the folder" }).count(), 0);
    assert.equal(folderRequests(s, IFA_FOLDER), 1, "the folder is asked for once");
    const ref = referenceRun(IFA, ["--as-of", AS_OF_46]);
    await validatePage(s, { asOf: AS_OF_46, requireAuthors: false });
    const shown = await attestationsShown(s);
    assert.deepEqual(shown.lines.map(l => [l.kind, l.text]), asShown(ref), "the Attestation was fetched and is held to what it binds, in the reference's words");
    assert.deepEqual(shown.lines.map(l => [l.kind, l.verdict]), [["line", "full-match"]]);
    assert.deepEqual(shown.dsse, ref.dsse);
    assert.deepEqual([shown.objects, shown.objects + 1], [17, ref.pass], "seventeen objects, the Attestation among them");
    assert.deepEqual(shown.errors, []);
    assert.deepEqual(s.errors, []);
  } finally { await s.close(); }
  /* a server that lists no folders is asked all the same, once: the request is a line in the browser's console, the
     bundle arrives without its Attestation, and the hub says that it could not look */
  s = await session();
  try {
    await s.page.goto(s.base + "index.html#load=.." + IFA_FOLDER);
    await s.page.waitForFunction(() => document.querySelector("#home-log .l-ok"), null, { timeout: 60000 });
    assert.equal(await s.page.locator("#home-log .l-info").last().innerText().then(x => x.replace(/^\d\d:\d\d:\d\d/, "")), NO_LISTING);
    assert.equal(folderRequests(s, IFA_FOLDER), 1, "asked once, and not again for a file it could only have guessed");
    assert.deepEqual(s.requests.filter(u => /attestation/.test(u)), []);
    assert.deepEqual(s.errors.map(m => m.replace(/^[^:]*: /, "")), ["Failed to load resource: the server responded with a status of 404 (Not Found)"], "the one console line of the folder that is not listed");
    s.errors.length = 0;
    await validatePage(s, { asOf: AS_OF_46, requireAuthors: false });
    const shown = await attestationsShown(s);
    assert.deepEqual([shown.objects, shown.basis, shown.lines], [16, null, []], "sixteen objects and no Attestation: the page claims nothing about one");
    assert.deepEqual(s.errors, []);
  } finally { await s.close(); }
  /* a server that answers the folder with a page of its own: a page counts as a listing only when it links
     content-manifest.json, so this folder was not looked into, nothing the page links is fetched, and the hub says so */
  s = await session({ list: "page" });
  try {
    await s.page.goto(s.base + "index.html#load=.." + IFA_FOLDER);
    await s.page.waitForFunction(() => document.querySelector("#home-log .l-ok"), null, { timeout: 60000 });
    assert.equal(await s.page.locator("#home-log .l-info").last().innerText().then(x => x.replace(/^\d\d:\d\d:\d\d/, "")), NO_LISTING);
    assert.deepEqual([folderRequests(s, IFA_FOLDER), s.requests.filter(u => /attestation/.test(u))], [1, []]);
    assert.equal(await s.page.evaluate(async () => (await jscStore.files(jscStore.activeSet())).filter(r => r.type === "attestation").length), 0);
    assert.deepEqual(s.errors, []);
  } finally { await s.close(); }
});

test("Attestations of a set that was changed: the page compares with the bundle an export would write and says so; a changed subject fails until the Attestation is taken out or, unsigned, withdrawn; no export lists an Attestation", { skip: needs }, async t => {
  const tmp = [];
  t.after(() => { for (const d of tmp) fs.rmSync(d, { recursive: true, force: true }); });
  /* the save every page uses, on one object of the set: the stored object with some fields replaced */
  const change = (s, id, fields) => s.page.evaluate(async ([id, fields]) => { await jscSet.load(); await jscSet.saveObjects([{ ...jscSet.graph.objects.get(id).obj, ...fields }]); }, [id, fields]);
  const checked = async s => { await validatePage(s, { asOf: AS_OF_46, requireAuthors: false }); return attestationsShown(s); };
  /* the exported folder, what the reference says about it, and that no Attestation is in its manifest while each travels beside it */
  const shipped = async (s, attestations) => {
    const x = await exported(s); tmp.push(x.out);
    const here = fs.readdirSync(x.dir);
    assert.deepEqual(x.manifest.objects.filter(e => /\/attestation\//.test(e.id) || /attestation/.test(e.path)), [], "the manifest lists no Attestation (D3.1)");
    for (const [file, envelope] of attestations) { assert.ok(here.includes(file), file + " travels beside the manifest"); if (envelope) assert.ok(here.includes(envelope), envelope + " travels with it"); }
    assert.deepEqual(here.filter(f => /attestation/.test(f)).sort(), attestations.flat().filter(Boolean).sort(), "and no other Attestation or envelope does");
    return { ...x, ref: referenceRun(x.dir, ["--as-of", AS_OF_46]) };
  };
  const assessCard = async (s, id) => {
    await open(s, "assess.html", "board");
    const card = s.page.locator(`[data-att-card="${id}"]`);
    await card.locator("[data-att]").click();
    await card.locator("[data-binds]").waitFor();
    return card;
  };
  const SAAS = "https://cso.example/component/acme-saas", ACME_FILES = [["attestation-acme-2026.json", "attestation-acme-2026.dsse"], ["attestation-dbvendor-server-7-advice.json", "attestation-dbvendor-server-7-advice.dsse"]];

  /* ---- the example folder: two signed Attestations, one over the set's manifest, one over a pack manifest the set keeps ---- */
  let s = await session(), p = s.page;
  try {
    await load(s, zipOf(EX, "examples"));
    /* a. nothing changed: the export is the bundle that was loaded, manifest and all */
    const same = await shipped(s, ACME_FILES);
    assert.equal(fs.readFileSync(path.join(same.dir, "content-manifest.json"), "utf8"), fs.readFileSync(path.join(EX, "content-manifest.json"), "utf8"), "the manifest leaves as it came");
    assert.ok(fs.existsSync(path.join(same.dir, "packs/sha256/27bed5464b7113e33a4641599b1861def5a24eebed2746fc9547bbd1de0c3eb1")), "the kept pack manifest travels too");
    assert.ok(same.ref.green);
    assert.deepEqual(same.ref.binds, referenceRun(EX, ["--as-of", AS_OF_46]).binds);

    /* b. an object that no Attestation names is changed: the manifest the set came with no longer describes it */
    await open(s, "validate.html");
    await change(s, LNX, { title: { en: "SSH hardening for Linux hosts (reworded)" } });
    const reworded = await checked(s);
    assert.equal(reworded.basis, "changed");
    /* the digest of the manifest the folder came with, read from the folder: written out here it went stale with every change of the example */
    const CAME = nodeSha256(fs.readFileSync(path.join(EX, "content-manifest.json"))).slice(0, 12);
    assert.match(reworded.said, new RegExp(String.raw`^This set was changed in this app after it was loaded, so the manifest it came with \(sha256:${CAME}…\) no longer describes it\. Compared with the bundle an export would write now: its manifest \(sha256:[0-9a-f]{12}…\) and the objects it lists\.`));
    assert.deepEqual(reworded.lines.map(l => [l.kind, l.verdict, l.text]), [
      ["line", "semantic-match", `binds: ${ACME_ATT} = SEMANTIC MATCH [3 subject(s) of this bundle; another manifest: the content is proven, the packaging was altered]`],
      ["line", "full-match", `binds: ${VENDOR_ATT} = FULL MATCH [1 subject(s) of this bundle; a pack manifest this bundle keeps]`]]);
    assert.match(reworded.lines[0].advice, /^No failure: every subject is as it was signed\./);
    assert.deepEqual(reworded.errors, [], "an Attestation that bound the manifest that was loaded is no failure after an edit elsewhere");
    const second = await shipped(s, ACME_FILES);
    assert.ok(second.ref.green);
    assert.deepEqual(reworded.lines.map(l => [l.kind, l.text]), asShown(second.ref), "what the page said before the export is what the reference says about the exported folder");
    assert.match(reworded.said, new RegExp("its manifest \\(" + ("sha256:" + nodeSha256(fs.readFileSync(path.join(second.dir, "content-manifest.json")))).slice(0, 19) + "…\\)"), "and the manifest it named is the one that was written");

    /* c. a subject of the set's own Attestation is changed: that is a failure, on the page and for the reference */
    await open(s, "validate.html");
    await change(s, SAAS, { title: { en: "Acme SaaS platform (renamed after it was authorized)" } });
    const renamed = await checked(s);
    assert.equal(renamed.lines[0].kind, "failure");
    assert.match(renamed.lines[0].text, new RegExp(`^error: \\[attestation-binds\\] ${ACME_ATT.replace(/[.]/g, "\\.")}: subject ${SAAS.replace(/[.]/g, "\\.")}: recomputed semantic digest sha256:[0-9a-f]{64}, signed sha256:86b98185aa0eef19e6d1fde05853a401b34b1d08dab67756fb05e103f9db19df - another manifest \\(B\\.1\\.7: `));
    assert.match(renamed.lines[0].advice, /^What can be done: the signer issues the Attestation again for the content as it is now, or the Attestation is taken out of the set \(Assess page\)\. It names an envelope, so it is signed/);
    assert.doesNotMatch(renamed.lines[0].advice, /set to withdrawn/, "withdrawing a signed Attestation is the signer's act and is not offered");
    assert.deepEqual(renamed.errors, [renamed.lines[0].text.slice("error: ".length)]);
    const third = await shipped(s, ACME_FILES);
    assert.equal(third.ref.green, false, "the reference fails the exported folder");
    assert.deepEqual(byText(renamed.lines.map(l => [l.kind, l.text])), byText(asShown(third.ref)), "with the failure the page showed, word for word");
    assert.deepEqual(third.ref.failures.length, 1, "and with nothing else");

    /* d. the Assess page says the same about that Attestation, and offers what can be done here: for a signed one, taking it out */
    const card = await assessCard(s, ACME_ATT);
    assert.equal(await card.locator("[data-binds-text]").innerText(), renamed.lines[0].text);
    assert.deepEqual([await card.locator("[data-att-remove]").count(), await card.locator("[data-att-withdraw]").count()], [1, 0]);
    const fine = await assessCard(s, VENDOR_ATT);
    assert.equal(await fine.locator("[data-binds-text]").innerText(), `binds: ${VENDOR_ATT} = FULL MATCH [1 subject(s) of this bundle; a pack manifest this bundle keeps]`);
    assert.equal(await fine.locator("button").count(), 0, "nothing is offered for an Attestation that binds");
    await (await assessCard(s, ACME_ATT)).locator("[data-att-remove]").click();
    await p.locator(`[data-att-card="${VENDOR_ATT}"]`).waitFor();
    await p.waitForFunction(id => !document.querySelector(`[data-att-card="${id}"]`), ACME_ATT);
    assert.deepEqual(await p.evaluate(async () => (await jscStore.files(jscStore.activeSet())).map(r => r.path).filter(x => /attestation/.test(x)).sort()),
      ["attestation-dbvendor-server-7-advice.dsse", "attestation-dbvendor-server-7-advice.json"], "the Attestation and the envelope that signed it left the set");
    const without = await checked(s);
    assert.deepEqual(without.lines.map(l => l.text), [`binds: ${VENDOR_ATT} = FULL MATCH [1 subject(s) of this bundle; a pack manifest this bundle keeps]`]);
    assert.deepEqual(without.errors, []);
    const fourth = await shipped(s, ACME_FILES.slice(1));
    assert.ok(fourth.ref.green, "taken out, the changed component fails nothing: " + fourth.ref.stdout.slice(-800));
    assert.deepEqual(without.lines.map(l => [l.kind, l.text]), asShown(fourth.ref));
    assert.deepEqual(s.errors, []);
  } finally { await s.close(); }

  /* ---- the IFA bundle: one unsigned Attestation ---- */
  const IMPL = "https://ifa.gov/goodread/impl/system1234-ac-6.1";
  /* what the committed Attestation signed for that Implementation: read from its file, so that a conversion run again
     (2026-11-14: the bundle changed twice that day) does not leave a digest of an earlier bundle in this test */
  const IFA_SIGNED = JSON.parse(fs.readFileSync(path.join(IFA, "attestation-ifa-ato.json"), "utf8"))["subject-semantic-digests"].find(x => x.id === IMPL)["semantic-digest"];
  s = await session(); p = s.page;
  try {
    await load(s, zipOf(IFA, "ifa"));
    const before = await assessCard(s, IFA_ATT);
    assert.equal(await before.locator("[data-binds-text]").innerText(), `binds: ${IFA_ATT} = FULL MATCH [3 subject(s) of this bundle; this manifest]`);
    await change(s, IMPL, { status: "planned" });
    const changed = await checked(s);
    assert.equal(changed.lines[0].kind, "failure");
    assert.match(changed.lines[0].advice, /because it names no envelope and is unsigned, it is set to withdrawn \(both on the Assess page\)/);
    const failing = await shipped(s, [["attestation-ifa-ato.json", null]]);
    assert.equal(failing.ref.green, false);
    assert.deepEqual(changed.lines.map(l => [l.kind, l.text]), asShown(failing.ref));
    /* unsigned, it can be set to withdrawn here; after that the verdict is reported and fails nothing */
    const card = await assessCard(s, IFA_ATT);
    assert.deepEqual([await card.locator("[data-att-remove]").count(), await card.locator("[data-att-withdraw]").count()], [1, 1]);
    await card.locator("[data-att-withdraw]").click();
    await p.locator(`[data-att-card="${IFA_ATT}"] .badge`, { hasText: "withdrawn" }).waitFor();
    const withdrawn = await checked(s);
    assert.deepEqual(withdrawn.lines.map(l => [l.kind, l.verdict]), [["line", "fail"]]);
    assert.match(withdrawn.lines[0].text, new RegExp(`^binds: ${IFA_ATT.replace(/[.]/g, "\\.")} = DOES NOT BIND \\[lifecycle withdrawn: reported, not a failure\\] subject ${IMPL.replace(/[.]/g, "\\.")}: recomputed semantic digest sha256:[0-9a-f]{64}, signed ${IFA_SIGNED} - another manifest$`));
    assert.equal(withdrawn.lines[0].advice, "Reported and no failure: the Attestation is not active, so nothing is claimed with it.");
    assert.deepEqual(withdrawn.errors, []);
    const passing = await shipped(s, [["attestation-ifa-ato.json", null]]);
    assert.ok(passing.ref.green, passing.ref.stdout.slice(-800));
    assert.deepEqual(withdrawn.lines.map(l => [l.kind, l.text]), asShown(passing.ref));
    assert.equal(passing.ref.pass, 18, "the withdrawn Attestation is still an object the reference counts");
    assert.deepEqual(s.errors, []);
  } finally { await s.close(); }

  /* ---- ERRATA 2026-11-14: a subject that is not in the set. Until build 0.9.11 the Assess page called this a Full Match ---- */
  s = await session(); p = s.page;
  try {
    await load(s, zipOf(IFA, "ifa"));
    await open(s, "assess.html", "board");
    await p.evaluate(async () => { await jscSet.load(); await jscSet.removeObjects(["https://ns.nist.gov/sp800-53/req/AC-6.1"]); });
    const card = await assessCard(s, IFA_ATT);
    assert.equal(await card.locator("[data-binds]").getAttribute("data-verdict"), "fail");
    assert.equal(await card.locator("[data-binds-text]").innerText(), `error: [attestation-binds] ${IFA_ATT}: subject https://ns.nist.gov/sp800-53/req/AC-6.1: not an object of this bundle - this manifest ${B17}`);
    assert.deepEqual(s.errors, []);
  } finally { await s.close(); }
});

/* ====================================================================
   Who decided, and when: the pages write it (backlog #69)
   ==================================================================== */
const LINUX_SET = "https://cso.example/set/linux-baseline", LNX = "https://cso.example/req/LNX-SSH-1";

test("Tailor: the author of a save stands on the Tailoring; a second author does not take over what the first decided; no author is no refusal", { skip: needs }, async t => {
  const s = await session(), tmp = [];
  try {
    await iAm(s, ALICE);
    await load(s, zipOf(EX, "examples"));
    const day = await today(s);
    await open(s, "tailor.html", "write");
    const p = s.page, mine = async () => (await stored(s, "tailoring")).find(t => t.label === "prod-hosts");
    await type(p.locator("#t-label"), "prod-hosts");
    await pick(s, "t-sel", "linux", LINUX_SET);
    await pick(s, "t-req", "LNX", LNX);
    await p.locator("#op-kind").selectOption("set-parameter");
    await type(p.locator("#op-value"), "3");
    await p.locator("#op-add").click();
    assert.equal(await p.locator("#t-author").inputValue(), ALICE, "the form shows the author it will write, from the setting");
    await p.locator("#t-save").click();
    await p.locator("#resolve .filterrow").waitFor();
    const first = await mine();
    assert.deepEqual(first.provenance, { "author-ref": ALICE, date: day });
    assert.ok([...first.selects, ...first.operations].every(e => !("provenance" in e)), "the entries inherit; nothing is repeated on them");

    /* bob adds an operation and saves the Tailoring of the same id */
    await p.locator('.navitem[data-view="write"]').click();
    await type(p.locator("#t-author"), BOB);
    await pick(s, "t-req", "LNX", LNX);
    await p.locator("#op-stmt").selectOption("s2");
    await p.locator("#op-add").click();
    await p.locator("#t-save").click();
    await p.locator("#resolve .filterrow").waitFor();
    const second = await mine();
    assert.deepEqual(second.provenance, { "author-ref": BOB, date: day });
    assert.deepEqual(second.selects[0].provenance, { "author-ref": ALICE, date: day }, "the select was alice's and says so now");
    assert.deepEqual(second.operations.map(o => o.provenance), [{ "author-ref": ALICE, date: day }, undefined], "alice's operation keeps her name; bob's inherits his");

    /* bob eases a clause, which needs a Deviation; the page writes it as pending, and nothing is decided yet */
    await p.locator('.navitem[data-view="write"]').click();
    await pick(s, "t-req", "LNX", LNX);
    await p.locator("#op-modality").selectOption("should");
    await p.locator("#dev-type").selectOption("operational-requirement");
    await type(p.locator("#dev-rationale"), "The legacy jump host cannot be changed before its replacement.");
    await type(p.locator("#dev-approver"), "https://org.example/party/ciso");   // the approver is named here; the page supplies none (backlog #70)
    await p.locator("#op-add").click();
    await p.locator("#t-save").click();
    await p.locator("#resolve .filterrow").waitFor();
    const eased = await mine(), key = `${eased.id}|2`;
    assert.deepEqual([eased.operations[2].deviation.state, "decided" in eased.operations[2].deviation], ["pending", false]);
    /* alice approves it on the first view: the day is written on the Deviation, the Tailoring is her version, the easing stays bob's */
    await type(p.locator("#d-author"), ALICE);
    await p.locator(`[data-dev="${key}"] [data-dev-to]`).selectOption("approved");
    assert.equal(await p.locator(`[data-dev="${key}"] [data-dev-decided]`).inputValue(), day);
    await p.locator(`[data-dev="${key}"] [data-dev-save]`).click();
    await p.locator(`[data-dev="${key}"] .badge`, { hasText: "approved" }).waitFor();
    const approved = await mine();
    assert.deepEqual([approved.operations[2].deviation.state, approved.operations[2].deviation.decided, approved.operations[2].deviation.opened], ["approved", day, day]);
    assert.deepEqual(approved.provenance, { "author-ref": ALICE, date: day });
    assert.deepEqual(approved.operations.map(o => o.provenance["author-ref"]), [ALICE, BOB, BOB], "each operation names who decided it");
    /* the object view says who decided, per entry */
    await p.locator("#resolve .reflink", { hasText: "⋯" }).click();
    assert.match(await p.locator("#jsc-drawer").innerText(), /who decided\s*alice · \d{4}-\d{2}-\d{2}[\s\S]*bob · \d{4}/);
    /* the second view still holds the Deviation as pending; saving from there does not undo the approval */
    await p.locator("#jsc-drawer-close").click();
    await p.locator('.navitem[data-view="write"]').click();
    await p.locator("#t-save").click();
    await p.locator("#resolve .filterrow").waitFor();
    assert.deepEqual([(await mine()).operations[2].deviation.state, (await mine()).operations[2].deviation.decided], ["approved", day]);

    /* the reference: no AUTHOR line, nothing fails, and the export pinned the kernel the new fields need */
    const one = await exported(s); tmp.push(one.out);
    assert.equal(one.manifest["kernel-version"], "2.0.0");
    const ref = reference(one.dir, ["--require-authors", "--as-of", AS_OF], t, "the example folder with a Tailoring written by two authors and its Deviation approved");
    assert.ok(ref.green, ref.stdout.slice(-2500));
    assert.deepEqual(ref.said.filter(l => /AUTHOR/.test(l)), []);
    assert.deepEqual(ref.failures, []);

    /* no author: the field is emptied, the save goes ahead, and the Tailoring names none */
    await open(s, "tailor.html", "write");
    await type(p.locator("#t-label"), "nobody-signed");
    await type(p.locator("#t-author"), "");
    assert.match(await p.locator("[data-author-hint]").first().innerText(), /no author is written/);
    await p.locator("#t-save").click();
    await p.locator("#resolve .filterrow").waitFor();
    const unsigned = (await stored(s, "tailoring")).find(t => t.label === "nobody-signed");
    assert.ok(unsigned, "a Tailoring without an author is saved");
    assert.equal(JSON.stringify(unsigned).includes("provenance"), false, "and nobody is invented for it");
    /* it is a line of the report: a note, an error only when authors are required; the reference says the same */
    const line = `${unsigned.id}: 1 of 1 select(s), 3 of 3 operation(s) name no author, and the Tailoring names none (AUTHOR-1)`;
    const note = await validatePage(s, { asOf: AS_OF, requireAuthors: false });
    assert.deepEqual(note.author, [{ kind: "note", rule: "AUTHOR-1", text: "note: " + line }]);
    assert.deepEqual(note.errors, []);
    const strict = await validatePage(s, { asOf: AS_OF, requireAuthors: true });
    assert.deepEqual(strict.author, [{ kind: "error", rule: "AUTHOR-1", text: "error: " + line }]);
    assert.equal(strict.errors.length, 1, strict.errors.join(" | "));
    const two = await exported(s); tmp.push(two.out);
    const lax = reference(two.dir, ["--as-of", AS_OF], t, "the same set with a Tailoring nobody signed");
    assert.ok(lax.green, "without the switch a missing author fails nothing\n" + lax.stdout.slice(-1500));
    assert.deepEqual(lax.said.filter(l => /AUTHOR/.test(l)), ["note: " + line]);
    const required = reference(two.dir, ["--require-authors", "--as-of", AS_OF], t, "the same set with a Tailoring nobody signed");
    assert.equal(required.green, false);
    assert.deepEqual(required.failures, [line]);
    assert.deepEqual(s.errors, []);
  } finally {
    for (const d of tmp) fs.rmSync(d, { recursive: true, force: true });
    await s.close();
  }
});

/* The sets above pin kernel 2.0.0 whatever the pages write: the example folder holds a Risk and Checks. Here the
   set is three requirements and two Sets of kernel 1.0.0 without a manifest, so the only reason for the pin is
   what a page wrote. A page that writes one of the new fields and an export that does not pin the kernel give a
   bundle the reference refuses (KERNEL-1). */
test("the export pins kernel 2.0.0 exactly when a page named an author, and the reference accepts the set either way", { skip: needs }, async t => {
  const s = await session(), tmp = [], KONF = "https://ns.bsi.bund.de/gspp/req/KONF.14.1";
  const loose = ["req-konf-14-1.json", "req-ism-1234.json", "req-iec-cso-iir.json", "set-crypto.json", "set-baseline.json", "gspp-taxonomy-1.1.0.json"].map(f => path.join(EX, f));
  try {
    await load(s, loose);
    const p = s.page;
    /* a Tailoring, a system with one edge, and a check with one finding: three pages, no author anywhere */
    const tailoring = async () => {
      await open(s, "tailor.html", "write");
      await type(p.locator("#t-label"), "soa");
      if (!(await p.locator("[data-delsel]").count())) await pick(s, "t-sel", "baseline", "https://ns.bsi.bund.de/gspp/set/baseline/example");
      await p.locator("#t-save").click();
      await p.locator("#resolve .filterrow").waitFor();
    };
    const system = async () => {
      await open(s, "implement.html", "build");
      if (!(await p.locator("[data-delcomp]").count())) {
        await p.locator("#new-title").fill("Order database");
        await p.locator("#add-asset").click();
        await pick(s, "pick-0", "KONF", KONF);
        await p.locator(".wbchip").first().waitFor();
      }
      await p.locator("#sys-save").click();
      await p.locator("#system .stmt").first().waitFor();
    };
    const check = async () => {
      await open(s, "assess.html", "check");
      await type(p.locator("#a-label"), "audit-1");
      await p.locator("#a-scope").selectOption("all");
      /* the performer is required and the page supplies none: named here on the first pass, "Who am I" on the second (backlog #70) */
      if (!(await p.locator("#a-perf").inputValue())) await type(p.locator("#a-perf"), "https://org.example/party/assessor");
      if (await p.locator(`[data-answer="${KONF}"][data-result="not-satisfied"]`).getAttribute("aria-pressed") !== "true") await p.locator(`[data-answer="${KONF}"][data-result="not-satisfied"]`).click();
      await p.locator("#a-write").click();
      await p.locator("#board .kanban").waitFor();
    };
    await tailoring(); await system(); await check();
    const plain = await exported(s); tmp.push(plain.out);
    assert.equal(plain.manifest["kernel-version"], undefined, "nothing in the set needs kernel 2.0.0");
    const lax = reference(plain.dir, ["--as-of", AS_OF], t, "three requirements, a Tailoring, a system and a check, no author");
    assert.ok(lax.green, lax.stdout.slice(-2000));
    assert.deepEqual(lax.said.map(l => l.match(/\((AUTHOR-\d)\)/)[1]).sort(), ["AUTHOR-1", "AUTHOR-2", "AUTHOR-2"], "the three records are reported, and nothing fails");

    /* the same three, saved again by alice */
    await iAm(s, ALICE);
    await tailoring(); await system(); await check();
    const day = await today(s), by = { "author-ref": ALICE, date: day };
    assert.deepEqual([(await stored(s, "tailoring"))[0].provenance, (await stored(s, "implementation"))[0].provenance, (await stored(s, "finding"))[0].provenance], [by, by, by]);
    const signed = await exported(s); tmp.push(signed.out);
    assert.equal(signed.manifest["kernel-version"], "2.0.0", "an author on a Tailoring, an Implementation or a Finding needs the pin");
    const strict = reference(signed.dir, ["--require-authors", "--as-of", AS_OF], t, "the same set, saved again by an author");
    assert.ok(strict.green, strict.stdout.slice(-2000));
    assert.deepEqual(strict.said, []);
    assert.deepEqual(s.errors, []);
  } finally {
    for (const d of tmp) fs.rmSync(d, { recursive: true, force: true });
    await s.close();
  }
});

test("Risk: the author on the Risk and on a rating that is set or changed; an unchanged rating keeps its author; a catalogue import pre-fills who and when and lets both be overwritten", { skip: needs }, async t => {
  const s = await session(), tmp = [], CAROL = "https://org.example/party/carol", R7 = "https://cso.example/risk/R-2026-007";
  try {
    await iAm(s, ALICE);
    await load(s, zipOf(EX, "examples"));
    const day = await today(s), p = s.page, risk = async id => (await stored(s, "risk")).find(r => r.id === id);
    const by = (who, when) => ({ "author-ref": who, date: when || day });
    const save = async () => { await p.locator("#r-save").click(); await p.locator("#register table.flat").waitFor(); };
    const edit = async id => { await p.locator(`[data-risk="${id}"]`).click(); await p.locator("#r-save").waitFor(); };

    /* a risk of the set: the CISO wrote it on 5 November, secops rated it on 28 October, the residual rating names nobody of its own */
    await open(s, "risk.html", "register");
    await edit(R7);
    assert.equal(await p.locator("#r-author").inputValue(), ALICE);
    await type(p.locator("#r-title"), "Tenant data exposure through long-lived KMS keys (reworded)");
    await save();
    const reworded = await risk(R7);
    assert.deepEqual(reworded.provenance, by(ALICE), "this version is alice's");
    assert.deepEqual(reworded.rating.provenance, by("https://cso.example/party/secops", "2026-10-28"), "the rating keeps its own author");
    assert.deepEqual(reworded["residual-rating"].provenance, by("https://cso.example/party/ciso", "2026-11-05"), "the residual rating had the Risk's author, and has him written on it now");
    assert.deepEqual([reworded.rating.level, reworded["residual-rating"].level, reworded.state, reworded.annotations["register-row"]], ["hoch", "gering", "treated", 7], "nothing else changed");

    /* a new risk, written and rated by bob */
    await p.locator("#new-risk").click();
    await type(p.locator("#r-label"), "R-NEW");
    await type(p.locator("#r-scenario"), "A backup is restored from a tape nobody tested.");
    await type(p.locator("#r-owner"), "https://org.example/party/ciso");
    await p.locator("#rating-scale").selectOption("https://cso.example/scale/bsi-200-3-matrix");
    await p.locator("#rating-l").selectOption("mittel");
    await p.locator("#rating-i").selectOption("begrenzt");
    await type(p.locator("#r-author"), BOB);
    await save();
    const NEW = (await stored(s, "risk")).find(r => r.label === "R-NEW").id;
    const written = await risk(NEW);
    assert.deepEqual([written.provenance, written.rating.provenance], [by(BOB), by(BOB)]);
    /* carol rates it again: the rating is hers, and so is this version */
    await edit(NEW);
    await p.locator("#rating-l").selectOption("häufig");
    await type(p.locator("#r-author"), CAROL);
    await save();
    assert.deepEqual([(await risk(NEW)).provenance, (await risk(NEW)).rating.provenance], [by(CAROL), by(CAROL)]);
    /* bob adds a residual rating and leaves the rating alone: the residual is his, the rating stays carol's */
    await edit(NEW);
    await p.locator("#r-residual").check();
    await p.locator('[id="residual-rating-l"]').selectOption("selten");
    await p.locator('[id="residual-rating-i"]').selectOption("begrenzt");
    await type(p.locator("#r-author"), BOB);
    await save();
    const rated = await risk(NEW);
    assert.deepEqual([rated.provenance, rated.rating.provenance, rated["residual-rating"].provenance], [by(BOB), by(CAROL), by(BOB)]);

    /* the catalogue: its publisher and the day it was released stand in two fields, and each can be typed over */
    await p.locator('.navitem[data-view="catalogue"]').click();
    const PUBLISHER = "https://github.com/christoph-puppe", entry = n => `https://github.com/christoph-puppe/JASCON/risk-catalogs/office-it/entry/OFF-0${n}`;
    await type(p.locator("#c-owner"), "https://org.example/party/ciso");
    assert.deepEqual([await p.locator("#c-author").inputValue(), await p.locator("#c-date").inputValue()], [PUBLISHER, "2026-11-10"]);
    const imported = async (n, said) => {
      await p.locator(`[data-import="${entry(n)}"]`).click();
      await p.locator("#log .l-info", { hasText: said }).first().waitFor();
      return (await stored(s, "risk")).find(r => r.label === "OFF-0" + n);
    };
    assert.deepEqual((await imported(1, "1 as the catalogue states it, 0 as entered here, 0 not stated")).provenance, by(PUBLISHER, "2026-11-10"));
    await type(p.locator("#c-author"), ALICE);
    assert.deepEqual((await imported(2, "0 as the catalogue states it, 1 as entered here, 0 not stated")).provenance, by(ALICE, "2026-11-10"), "the author alone was overwritten");
    await type(p.locator("#c-date"), "2026-11-12");
    assert.deepEqual((await imported(3, "0 as the catalogue states it, 1 as entered here, 0 not stated")).provenance, by(ALICE, "2026-11-12"));

    /* the reference on the exported set: every Risk names its author, nothing fails */
    const one = await exported(s); tmp.push(one.out);
    const ref = reference(one.dir, ["--require-authors", "--as-of", AS_OF], t, "the example folder with one Risk reworded, one written and three imported from the catalogue");
    assert.ok(ref.green, ref.stdout.slice(-2500));
    assert.deepEqual(ref.said.filter(l => /AUTHOR/.test(l)), []);
    assert.match(ref.summary, /'risk': 5/);

    /* an emptied day: the import goes ahead and the Risk names nobody; the reports say which one */
    await open(s, "risk.html", "catalogue");
    await type(p.locator("#c-owner"), "https://org.example/party/ciso");
    await type(p.locator("#c-date"), "");
    const bare = await imported(4, "0 as the catalogue states it, 0 as entered here, 1 not stated");
    assert.equal("provenance" in bare, false);
    const line = `${bare.id}: this Risk does not say who wrote it and when (AUTHOR-2)`;
    assert.deepEqual((await validatePage(s, { asOf: AS_OF, requireAuthors: false })).author.map(l => l.text), ["note: " + line]);
    const two = await exported(s); tmp.push(two.out);
    assert.deepEqual(reference(two.dir, ["--require-authors", "--as-of", AS_OF], t, "the same set with a fourth Risk imported without a day").failures, [line]);
    assert.deepEqual(s.errors, []);
  } finally {
    for (const d of tmp) fs.rmSync(d, { recursive: true, force: true });
    await s.close();
  }
});

test("Implement and Assess: an Implementation and a Finding name their author; a Deviation that is decided gets its day, and a review date the Validate page asks about", { skip: needs }, async t => {
  const s = await session(), tmp = [], KONF = "https://ns.bsi.bund.de/gspp/req/KONF.14.1", DEV = "https://org.example/finding/dev-1";
  try {
    await iAm(s, ALICE);
    await load(s, zipOf(EX, "examples"));
    const day = await today(s), p = s.page, by = (who, when) => ({ "author-ref": who, date: when || day });

    /* a system: its edges are alice's */
    await open(s, "implement.html", "build");
    await type(p.locator("#sys-title"), "Shop");
    await p.locator("#new-title").fill("Order database");
    await p.locator("#add-asset").click();
    await pick(s, "pick-0", "KONF", KONF);
    await p.locator(".wbchip").first().waitFor();
    assert.equal(await p.locator("#sys-author").inputValue(), ALICE);
    await p.locator("#sys-save").click();
    await p.locator("#system .stmt").first().waitFor();
    const built = (await stored(s, "implementation")).filter(e => e["component-ref"].endsWith("/comp/order-database"));
    assert.deepEqual(built.map(e => e.provenance), [by(ALICE)]);
    assert.ok((await stored(s, "component")).filter(c => c.id.startsWith("https://example.org/my/")).every(c => !("provenance" in c)), "a Component names no author: the kernel has no field for one");
    /* bob attaches a second requirement and saves the system: the workbench writes both edges, and the one he did not touch stays alice's */
    await p.locator('.navitem[data-view="build"]').click();
    await type(p.locator("#sys-author"), BOB);
    await pick(s, "pick-0", "ISM", "https://ns.cyber.gov.au/ism/req/ISM-1234");
    await p.locator(".wbchip").nth(1).waitFor();
    await p.locator("#sys-save").click();
    await p.locator("#system .stmt").first().waitFor();
    const edges = (await stored(s, "implementation")).filter(e => e["component-ref"].endsWith("/comp/order-database"));
    assert.deepEqual(Object.fromEntries(edges.map(e => [e["requirement-ref"].split("/").pop(), e.provenance["author-ref"]])), { "KONF.14.1": ALICE, "ISM-1234": BOB });
    /* adopting a vendor's recommendation is bob's judgement, and the edge says so */
    await p.locator('.navitem[data-view="advice"]').click();
    await p.locator("#adv-own").selectOption({ label: "Shop" });
    await p.locator('[data-product="https://dbvendor.example/component/server-7"] [data-member]').click();
    await p.locator('[data-adopt$="#cap-key-rotation"]').waitFor();
    await type(p.locator("#adv-author"), BOB);
    await p.locator('[data-adopt$="#cap-key-rotation"]').click();
    await p.locator("#advice .badge", { hasText: "adopted" }).first().waitFor();
    const adopted = (await stored(s, "implementation")).find(e => e["component-ref"].endsWith("/comp/shop"));
    assert.deepEqual(adopted.provenance, by(BOB));

    /* a check with one requirement not satisfied: the Finding is alice's; moved on by bob, that version is bob's */
    await open(s, "assess.html", "check");
    await type(p.locator("#a-label"), "audit-1");
    await p.locator("#a-scope").selectOption("all");
    assert.equal(await p.locator("#a-author").inputValue(), ALICE, "a page starts from the setting again");
    await p.locator(`[data-answer="${KONF}"][data-result="not-satisfied"]`).click();
    await p.locator("#a-write").click();
    await p.locator("#board .kanban").waitFor();
    const raised = (await stored(s, "finding")).find(f => f["assessment-ref"].endsWith("/asmt/audit-1"));
    assert.deepEqual([raised.state, raised.provenance], ["open", by(ALICE)]);
    await type(p.locator("#b-author"), BOB);
    await p.locator(`[data-move="${raised.id}"][data-to="in-remediation"]`).click();
    await p.locator(`[data-move="${raised.id}"][data-to="closed"]`).waitFor();
    const moved = (await stored(s, "finding")).find(f => f.id === raised.id);
    assert.deepEqual([moved.state, moved.provenance], ["in-remediation", by(BOB)]);

    /* a Finding that came with two Deviations nobody has decided: one pending, one still investigated */
    const dev = (type_, state) => ({ type: type_, state, rationale: { en: "The legacy host cannot be changed before its replacement." }, "approver-ref": "https://org.example/party/ciso", opened: "2026-11-01" });
    await load(s, jsonFile("finding-dev-1.json", { id: DEV, version: "1", lifecycle: "draft", provenance: by("https://org.example/party/assessor", "2026-11-01"),
      "assessment-ref": "https://assessor.example/assessment/2026-q3-acme", "requirement-ref": KONF, state: "open",
      deviations: [dev("operational-requirement", "pending"), dev("false-positive", "investigating")] }));
    await open(s, "assess.html", "board");
    const box = n => p.locator(`[data-dev="${DEV}|${n}"]`), finding = async () => (await stored(s, "finding")).find(f => f.id === DEV);
    assert.equal(await box(0).locator("[data-dev-decided]").count(), 0, "no day is asked before a decision");
    await box(0).locator("[data-dev-to]").selectOption("approved");
    assert.equal(await box(0).locator("[data-dev-decided]").inputValue(), day, "the day offered is today");
    await box(0).locator("[data-dev-due]").selectOption("date");
    await type(box(0).locator("[data-dev-duedate]"), "2027-05-13");
    await box(0).locator("[data-dev-save]").click();
    await box(0).locator(".badge", { hasText: "approved" }).waitFor();
    /* the second is withdrawn, and the day is typed over: it was decided the day before */
    await box(1).locator("[data-dev-to]").selectOption("withdrawn");
    assert.equal(await box(1).locator("[data-dev-due]").count(), 0, "a withdrawn Deviation has nothing to review");
    await type(box(1).locator("[data-dev-decided]"), "2026-11-12");
    await box(1).locator("[data-dev-save]").click();
    await box(1).locator(".badge", { hasText: "withdrawn" }).waitFor();
    const decided = await finding();
    assert.deepEqual(decided.deviations[0], { ...dev("operational-requirement", "approved"), decided: day, "review-due": { type: "date", value: "2027-05-13" } });
    assert.deepEqual(decided.deviations[1], { ...dev("false-positive", "withdrawn"), decided: "2026-11-12" });
    assert.deepEqual(decided.provenance, by(ALICE), "who decided the Deviations wrote this version of the Finding");
    assert.equal(await box(0).locator("[data-dev-to]").count(), 0, "approved is final: the page offers no further move");

    /* the reference: nothing is missing, and the review date is asked on the day given */
    const one = await exported(s); tmp.push(one.out);
    assert.equal(one.manifest["kernel-version"], "2.0.0");
    const ref = reference(one.dir, ["--require-authors", "--as-of", AS_OF], t, "the example folder with a system, an adopted recommendation, a check, a moved Finding and two decided Deviations");
    assert.ok(ref.green, ref.stdout.slice(-2500));
    assert.deepEqual(ref.said.filter(l => /AUTHOR/.test(l)), []);
    /* the day asked about: due on the day is not overdue, the day after it is; the page and the reference print the same lines */
    const overdue = `note: ${DEV}: deviations[0] was due on 2027-05-13 (REVIEW-1: overdue; it still holds until someone acts)`;
    for (const [asOf, late] of [["2027-05-13", false], ["2027-05-14", true]]) {
      const shown = await validatePage(s, { asOf, requireAuthors: true }), said = reference(one.dir, ["--require-authors", "--as-of", asOf], t, "the same set");
      assert.deepEqual(shown.review.map(l => l.text), said.said, asOf);
      assert.equal(shown.review.some(l => l.text === overdue), late, asOf);
      /* three are asked: the Risk of the example folder (a calendar period, not evaluable), its Finding's Deviation (due in July 2027) and the one decided here */
      assert.match(shown.review[0].text, new RegExp(`^review: 3 review date\\(s\\) asked as of ${asOf}: ${late ? 1 : 0} overdue, 1 not evaluable`));
      assert.deepEqual(shown.errors, [], "an overdue review fails nothing, also with authors required");
      assert.ok(said.green, "and the reference stays green");
    }
    assert.deepEqual(s.errors, []);
  } finally {
    for (const d of tmp) fs.rmSync(d, { recursive: true, force: true });
    await s.close();
  }
});

test("Import, Map and Checks: a profile's Tailoring names the document's author and day, both can be typed over, and none is no refusal; a Mapping and a Check start from \"Who am I\"", { skip: needs }, async t => {
  const s = await session(), tmp = [], NS = "https://example.org/my";
  /* an OSCAL profile over the example folder's LNX-SSH-1; its metadata names a creator among two parties */
  const profile = (title, metadata) => jsonFile(title.toLowerCase().replace(/ /g, "-") + ".json", { profile: { uuid: "p-1",
    metadata: { title, version: "1", "oscal-version": "1.1.2", ...metadata },
    imports: [{ href: "#catalog", "include-controls": [{ "with-ids": ["lnx-ssh-1"] }] }],
    modify: { "set-parameters": [{ "param-id": "max-auth-tries", values: [3] }] } } });
  const named = { "last-modified": "2026-11-05T09:00:00+01:00",
    parties: [{ uuid: "u-1", type: "person", name: "Jane Roe" }, { uuid: "u-2", type: "organization", name: "Example Agency" }],
    "responsible-parties": [{ "role-id": "creator", "party-uuids": ["u-1"] }, { "role-id": "contact", "party-uuids": ["u-2"] }] };
  try {
    await iAm(s, ALICE);
    await load(s, zipOf(EX, "examples"));
    const day = await today(s), p = s.page, tailoring = async label => (await stored(s, "tailoring")).find(t => t.label === label);
    const offer = async file => { await open(s, "import.html"); await p.locator("#pick").setInputFiles(file); await p.locator("#run").waitFor(); };
    const run = async () => { await p.locator("#run").click(); await p.locator("#report-provenance").waitFor(); return (await p.locator("#report-provenance").innerText()).replace(/\s+/g, " "); };
    const write = async label => { await p.locator("#write").click(); await p.waitForFunction(async l => (await jscStore.files(jscStore.activeSet())).some(r => r.type === "tailoring" && JSON.parse(r.text).label === l), label); };

    /* before the import: who and when, as the document states them, in two fields */
    await offer(profile("Hardened hosts", named));
    assert.deepEqual([await p.locator("#o-author").inputValue(), await p.locator("#o-date").inputValue()], [NS + "/party/jane-roe", "2026-11-05"]);
    assert.match(await run(), /of 1 record\(s\) that can name an author: 1 as the source states it, 0 as entered here, 0 not stated/);
    await write("hardened-hosts");
    assert.deepEqual((await tailoring("hardened-hosts")).provenance, { "author-ref": NS + "/party/jane-roe", date: "2026-11-05" });
    assert.deepEqual((await tailoring("hardened-hosts")).operations.map(o => [o.parameter, o.value]), [["max-auth-tries", 3]]);

    /* the same profile again, the author typed over: the day stays the document's */
    await offer(profile("Hardened hosts", named));
    await type(p.locator("#o-author"), ALICE);
    assert.equal(await p.locator("#o-date").inputValue(), "2026-11-05");
    assert.match(await run(), /0 as the source states it, 1 as entered here, 0 not stated/);
    await write("hardened-hosts");
    assert.deepEqual((await tailoring("hardened-hosts")).provenance, { "author-ref": ALICE, date: "2026-11-05" });
    /* and with the author emptied: nobody, although the document names one; shown in the report before anything is written */
    await offer(profile("Hardened hosts", named));
    await type(p.locator("#o-author"), "");
    assert.match(await run(), /0 as the source states it, 0 as entered here, 1 not stated/);

    /* a Mapping: the field shows "Who am I", and the date written is a date */
    await open(s, "map.html", "write");
    assert.equal(await p.locator("#m-author").inputValue(), ALICE);
    await pick(s, "m-src", "LNX", LNX);
    await pick(s, "m-tgt", "KONF", "https://ns.bsi.bund.de/gspp/req/KONF.14.1");
    await p.locator("#m-add").click();
    await p.locator("#table table.flat").waitFor();
    const mapping = (await stored(s, "mapping")).find(m => m["source-ref"] === LNX);
    assert.deepEqual(mapping.provenance, { "author-ref": ALICE, date: day });
    assert.match(mapping.provenance.date, /^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$/);
    /* a new Check starts from the same setting */
    await open(s, "checks.html", "edit");
    assert.equal(await p.locator("#e-author").inputValue(), ALICE);

    const one = await exported(s); tmp.push(one.out);
    const ref = reference(one.dir, ["--require-authors", "--as-of", AS_OF], t, "the example folder with a profile imported twice and a Mapping written");
    assert.ok(ref.green, ref.stdout.slice(-2500));
    assert.deepEqual(ref.said.filter(l => /AUTHOR/.test(l)), []);

    /* a profile that names two persons and no role: the document does not say who wrote it, the field is empty, and the import goes ahead */
    await offer(profile("Unsigned hosts", { "last-modified": "2026-11-05T09:00:00Z", parties: [{ uuid: "u-1", type: "person", name: "Jane Roe" }, { uuid: "u-3", type: "person", name: "John Doe" }] }));
    assert.deepEqual([await p.locator("#o-author").inputValue(), await p.locator("#o-date").inputValue()], ["", "2026-11-05"]);
    assert.match(await p.locator("#work .form").innerText(), /The source does not say who wrote it/);
    assert.match(await run(), /0 as the source states it, 0 as entered here, 1 not stated/);
    await write("unsigned-hosts");
    const unsigned = await tailoring("unsigned-hosts");
    assert.equal("provenance" in unsigned, false, "nobody is invented");
    const two = await exported(s); tmp.push(two.out);
    assert.deepEqual(reference(two.dir, ["--require-authors", "--as-of", AS_OF], t, "the same set with a profile that names no author").failures, [`${unsigned.id}: 1 of 1 select(s), 1 of 1 operation(s) name no author, and the Tailoring names none (AUTHOR-1)`]);

    /* ERRATA 2026-11-13: a check somebody else wrote, opened for editing, offers who edits now; a save writes today's date
       beside that author, and no longer beside the author of the earlier version. (This comes last: the edited check
       has recorded runs in this set, and a changed check is a different check for them, CHECK-8.) */
    const CHECK = "https://cso.example/check/LNX-SSH-1-ciphers";
    /* since build 0.9.24 the page asks before such a save and names the Assessments that ran the check (backlog #71, point 2;
       the test of that question is further down). Here the answer is yes, both times. */
    const asked = [];
    s.onDialog = d => { asked.push(d.message()); d.accept(); };
    await open(s, "checks.html", "rules");
    await p.locator(`[data-edit="${CHECK}"]`).click();
    assert.equal(await p.locator("#e-author").inputValue(), ALICE, "the check names secops; the editor is alice");
    await p.locator("#e-save").click();
    await p.locator("#log .l-ok", { hasText: "saved check" }).first().waitFor();
    assert.deepEqual((await stored(s, "check")).find(c => c.id === CHECK).provenance, { "author-ref": ALICE, date: day });
    /* without the setting the form shows the author the check names, as before, and a save writes today's date beside it:
       the part of the erratum that is not fixed, because the page cannot know who edits */
    await s.page.evaluate(() => jscCfg.remove("org:me"));
    const OTHER = "https://cso.example/check/LNX-SSH-1-maxauthtries";
    await open(s, "checks.html", "rules");
    await p.locator(`[data-edit="${OTHER}"]`).click();
    assert.equal(await p.locator("#e-author").inputValue(), "https://cso.example/party/secops");
    await p.locator("#e-save").click();
    await p.locator("#log .l-ok", { hasText: "saved check" }).first().waitFor();
    assert.deepEqual((await stored(s, "check")).find(c => c.id === OTHER).provenance, { "author-ref": "https://cso.example/party/secops", date: day });
    assert.deepEqual(asked.map(m => m.split(":")[0]), Array(2).fill("2 Assessment(s) of this set ran this check as it is stored now"), "each of the two saves was asked about");
    s.onDialog = null;
    assert.deepEqual(s.errors, []);
  } finally {
    for (const d of tmp) fs.rmSync(d, { recursive: true, force: true });
    await s.close();
  }
});

/* ====================================================================
   No page writes a party nobody named (backlog #70)
   ====================================================================
   Author decision of 2026-11-14: "refuse if no party is named". Where the
   kernel requires a party (the author of a Mapping and of a Check, the
   performer of an Assessment, the approver of a Deviation, who a statement
   binds) a page refuses the save while the field is empty, says which
   field the kernel requires, and changes nothing. Until build 0.9.10 each
   of these pages wrote a party made from a word of its own.

   Each test below asks the same three things of a field: empty, the save
   is refused and the set is byte for byte what it was; a party that is
   named is written as named (a URI as it is, a short name as a party under
   the namespace); and the field starts where it should. The exported set
   goes to the reference with --require-authors.

   The optional author of a Tailoring, a Risk, an Implementation and a
   Finding is another matter and stays as it was: empty writes none and
   the save goes ahead. The tests above hold that; one line here does too. */
const AS_OF_70 = "2026-11-14", NS = "https://example.org/my", KONF_REQ = "https://ns.bsi.bund.de/gspp/req/KONF.14.1";
/* every file of the active set with its text: what "the set is unchanged" is measured on */
const snapshot = s => s.page.evaluate(async () => (await jscStore.files(jscStore.activeSet())).map(r => [r.path, r.text]).sort());
const HOW = "Name a party: a URI, or a short name, which becomes a party under your namespace.";
const greenWithAuthors = (s, t, tmp, what) => exported(s).then(x => { tmp.push(x.out); const ref = reference(x.dir, ["--require-authors", "--as-of", AS_OF_70], t, what); assert.ok(ref.green, ref.stdout.slice(-2500)); assert.deepEqual(ref.said.filter(l => /AUTHOR/.test(l)), []); return ref; });

test("Map and Checks: an empty author refuses the save and changes nothing; a named author is written as named", { skip: needs }, async t => {
  const s = await session(), tmp = [], p = s.page, ISM = "https://ns.cyber.gov.au/ism/req/ISM-1234";
  try {
    await load(s, zipOf(EX, "examples"));
    const day = await today(s);

    /* --- a Mapping. Nobody is named in this browser: the field is empty, not a word of the page's --- */
    await open(s, "map.html", "write");
    assert.equal(await p.locator("#m-author").inputValue(), "");
    assert.match(await p.locator('[data-author-hint="required"]').innerText(), /the kernel requires an author here/);
    await pick(s, "m-src", "LNX", LNX);
    await pick(s, "m-tgt", "KONF", KONF_REQ);
    const before = await snapshot(s);
    await p.locator("#m-add").click();
    assert.equal(await p.locator("#m-err").innerText(), "No author is named. The kernel requires provenance.author-ref on a Mapping, so nothing was saved. The field “Author” is empty. " + HOW);
    assert.deepEqual(await snapshot(s), before, "a refused mapping leaves the set as it was");
    assert.equal(await p.locator("#m-author").inputValue(), "", "and the field is not filled behind the user's back");
    /* a short name the user types is a party of their own; the field shows the URI that will be written */
    await type(p.locator("#m-author"), "Jane Roe");
    assert.equal(await p.locator("#m-author").inputValue(), NS + "/party/jane-roe");
    await p.locator("#m-add").click();
    await p.locator("#table table.flat").waitFor();
    const mapping = async from => (await stored(s, "mapping")).find(m => m.id.startsWith(NS + "/map/") && m["source-ref"] === from);   // the example folder has a mapping of its own
    assert.deepEqual((await mapping(LNX)).provenance, { "author-ref": NS + "/party/jane-roe", date: day });
    /* a URI is written as it is */
    await p.locator('.navitem[data-view="write"]').click();
    await type(p.locator("#m-author"), "https://other.example/people/bob");
    await pick(s, "m-src", "KONF", KONF_REQ);
    await pick(s, "m-tgt", "ISM", ISM);
    await p.locator("#m-add").click();
    await p.locator("#table table.flat").waitFor();
    assert.deepEqual((await mapping(KONF_REQ)).provenance, { "author-ref": "https://other.example/people/bob", date: day });

    /* --- a Check, written in the editor --- */
    await open(s, "checks.html", "edit");
    assert.equal(await p.locator("#e-author").inputValue(), "", "a new check starts from the setting, and the setting is empty");
    await pick(s, "e-req", "LNX", LNX);
    await type(p.locator('[data-row="observes"][data-i="0"] [data-k="name"]'), "sshd.loglevel");
    await p.locator('[data-row="criteria"][data-i="0"] [data-k="fact"]').selectOption("sshd.loglevel");
    await type(p.locator('[data-row="criteria"][data-i="0"] [data-k="expected"]'), '"INFO"');
    const said = () => p.locator("#e-form .verdict-bad").allInnerTexts(), checks = async () => (await stored(s, "check")).length;
    assert.deepEqual(await said(), ["✗ No author is named. The kernel requires provenance.author-ref on a Check, so the check cannot be saved. The field “Author” is empty. " + HOW], "the missing author is the one thing the form has against the check");
    assert.ok(await p.locator("#e-save").isDisabled(), "and the check cannot be saved");
    assert.equal(await checks(), 2);
    await type(p.locator("#e-author"), "secops team");
    assert.equal(await p.locator("#e-author").inputValue(), NS + "/party/secops-team");
    assert.deepEqual(await said(), []);
    await p.locator("#e-save").click();
    await p.locator("#log .l-ok", { hasText: "saved check" }).first().waitFor();
    const written = (await stored(s, "check")).find(c => c.id.startsWith(NS + "/check/"));
    assert.deepEqual(written.provenance, { "author-ref": NS + "/party/secops-team", date: day });
    /* the author emptied again: it stays empty, and the check that is now in the set cannot be saved over without one */
    await type(p.locator("#e-author"), "");
    assert.equal(await p.locator("#e-author").inputValue(), "", "an emptied field is not filled with the author the check names");
    assert.ok(await p.locator("#e-save").isDisabled());
    assert.equal((await said()).length, 1);

    await greenWithAuthors(s, t, tmp, "the example folder with two Mappings and a Check, each by a named author");

    /* --- with "Who am I" set, both fields start from it; emptied, they stay empty and the save is refused --- */
    await iAm(s, ALICE);
    await open(s, "map.html", "write");
    assert.equal(await p.locator("#m-author").inputValue(), ALICE);
    await type(p.locator("#m-author"), "");
    await pick(s, "m-src", "ISM", ISM);
    await pick(s, "m-tgt", "LNX", LNX);
    const set = await snapshot(s);
    await p.locator("#m-add").click();
    assert.match(await p.locator("#m-err").innerText(), /^No author is named\. The kernel requires provenance\.author-ref on a Mapping/);
    assert.equal(await p.locator("#m-author").inputValue(), "", "the setting does not come back into a field the user emptied");
    assert.deepEqual(await snapshot(s), set);
    assert.deepEqual(s.errors, []);
  } finally {
    for (const d of tmp) fs.rmSync(d, { recursive: true, force: true });
    await s.close();
  }
});

test("Assess: an empty performer refuses the check and writes nothing; the performer starts from \"Who am I\"; an empty author of the Findings stops nothing", { skip: needs }, async t => {
  const s = await session(), tmp = [], p = s.page;
  try {
    await load(s, zipOf(EX, "examples"));
    const day = await today(s);
    const fill = async () => { await type(p.locator("#a-label"), "audit-70"); await p.locator("#a-scope").selectOption("all"); await p.locator(`[data-answer="${KONF_REQ}"][data-result="not-satisfied"]`).click(); };
    const asmt = async () => (await stored(s, "assessment")).find(a => a.id.endsWith("/asmt/audit-70"));

    /* nobody is named in this browser: the performer field is empty, and so is the author field of the same form */
    await open(s, "assess.html", "check");
    assert.deepEqual([await p.locator("#a-perf").inputValue(), await p.locator("#a-author").inputValue()], ["", ""]);
    await fill();
    const before = await snapshot(s);
    await p.locator("#a-write").click();
    assert.equal(await p.locator("#a-err").innerText(), "No performer is named. The kernel requires performer-ref on an Assessment, so nothing was written. The field “Performer” is empty. " + HOW);
    assert.deepEqual(await snapshot(s), before, "a refused check leaves the set as it was: no Assessment, no Finding");
    assert.equal(await p.locator("#a-perf").inputValue(), "");
    /* the performer named, the author of the Findings still empty: the check is written. The first field the kernel
       requires, the second it does not: the Assessment names its performer, the Finding names no author */
    await type(p.locator("#a-perf"), "Jane Roe");
    assert.equal(await p.locator("#a-perf").inputValue(), NS + "/party/jane-roe");
    await p.locator("#a-write").click();
    await p.locator("#board .kanban").waitFor();
    assert.equal((await asmt())["performer-ref"], NS + "/party/jane-roe");
    /* backlog #55: the method is the standard facet for a check a person did, and the tool is named nowhere in the object */
    assert.deepEqual((await asmt()).method, { "https://ns.jascon.net/stdlib/facet/assessment-criteria@1": { method: "manual" } });
    assert.doesNotMatch(JSON.stringify(await asmt()), /JASCON-App|manual-check|"tool"|"kind"/);
    const finding = async () => (await stored(s, "finding")).find(f => f["assessment-ref"].endsWith("/asmt/audit-70"));
    assert.equal("provenance" in await finding(), false, "an empty author writes none, and stopped nothing");

    /* with "Who am I": the performer starts from it, because who sits at the page performs the check; a URI is written as it is */
    await iAm(s, ALICE);
    await open(s, "assess.html", "check");
    assert.deepEqual([await p.locator("#a-perf").inputValue(), await p.locator("#a-author").inputValue()], [ALICE, ALICE]);
    await p.locator("#a-write").click();
    await p.locator("#board .kanban").waitFor();
    assert.equal((await asmt())["performer-ref"], ALICE);
    assert.deepEqual((await finding()).provenance, { "author-ref": ALICE, date: day });
    /* emptied, it stays empty and the check is refused, although the setting names somebody */
    await open(s, "assess.html", "check");
    await type(p.locator("#a-perf"), "");
    const set = await snapshot(s);
    await p.locator("#a-write").click();
    assert.match(await p.locator("#a-err").innerText(), /^No performer is named\. The kernel requires performer-ref on an Assessment/);
    assert.equal(await p.locator("#a-perf").inputValue(), "");
    assert.deepEqual(await snapshot(s), set);

    await greenWithAuthors(s, t, tmp, "the example folder with a check performed and its Finding raised by a named party");
    assert.deepEqual(s.errors, []);
  } finally {
    for (const d of tmp) fs.rmSync(d, { recursive: true, force: true });
    await s.close();
  }
});

test("Tailor: the approver of a Deviation starts empty, also with \"Who am I\" set; empty, the operation is refused; named, it is written as named", { skip: needs }, async t => {
  const s = await session(), tmp = [], p = s.page;
  try {
    await iAm(s, ALICE);
    await load(s, zipOf(EX, "examples"));
    await open(s, "tailor.html", "write");
    await type(p.locator("#t-label"), "eased-hosts");
    await pick(s, "t-sel", "linux", LINUX_SET);
    /* `sameRequirement`: the form still holds the requirement of the operation just added, and it is not chosen again */
    const ease = async (statement, why, sameRequirement) => {
      if (!sameRequirement) await pick(s, "t-req", "LNX", LNX);
      await p.locator("#op-stmt").selectOption(statement);
      await p.locator("#op-modality").selectOption("should");
      await p.locator("#dev-type").selectOption("operational-requirement");
      await type(p.locator("#dev-rationale"), why);
    };
    const operations = () => p.locator("[data-delop]").count();
    /* the author of the Tailoring starts from the setting; the approver does not: who approves an exception is not
       whoever types it, and a pre-filled approver would record self-approval by default */
    await ease("s1", "The legacy jump host cannot be changed before its replacement.");
    assert.equal(await p.locator("#t-author").inputValue(), ALICE);
    assert.equal(await p.locator("#dev-approver").inputValue(), "", "the approver starts empty, whoever sits at the page");
    const before = await snapshot(s);
    await p.locator("#op-add").click();
    assert.equal(await p.locator("#op-err").innerText(), "No approver is named. The kernel requires approver-ref on a Deviation, so the operation was not added. The field “approver” is empty. " + HOW);
    assert.equal(await operations(), 0, "the operation was not added");
    assert.deepEqual(await snapshot(s), before);
    /* a short name is the user's word for a party of their own: "ciso" typed is a party the user named */
    await type(p.locator("#dev-approver"), "ciso");
    assert.equal(await p.locator("#dev-approver").inputValue(), NS + "/party/ciso");
    await p.locator("#op-add").click();
    assert.equal(await operations(), 1);
    /* the next Deviation starts empty again, on the same requirement too: an approver is named per exception, and the
       one of the last exception is not carried over */
    await ease("s2", "The cipher list is fixed by the appliance vendor.", true);
    assert.equal(await p.locator("#dev-approver").inputValue(), "");
    await p.locator("#op-add").click();
    assert.match(await p.locator("#op-err").innerText(), /^No approver is named\./);
    assert.equal(await operations(), 1);
    await type(p.locator("#dev-approver"), "https://other.example/people/bob");
    await p.locator("#op-add").click();
    assert.equal(await operations(), 2);
    await p.locator("#t-save").click();
    await p.locator("#resolve .filterrow").waitFor();
    const saved = (await stored(s, "tailoring")).find(x => x.label === "eased-hosts");
    assert.deepEqual(saved.operations.map(o => [o.deviation["approver-ref"], o.deviation.state]), [[NS + "/party/ciso", "pending"], ["https://other.example/people/bob", "pending"]]);
    assert.equal(saved.provenance["author-ref"], ALICE);

    await greenWithAuthors(s, t, tmp, "the example folder with a Tailoring whose two Deviations each name their approver");
    assert.deepEqual(s.errors, []);
  } finally {
    for (const d of tmp) fs.rmSync(d, { recursive: true, force: true });
    await s.close();
  }
});

test("Browse and Import: who a statement binds is named by the user; empty, the requirement and the import are refused", { skip: needs }, async t => {
  const s = await session(), tmp = [], p = s.page;
  /* a catalog no preset knows: the generic rules read it */
  const catalog = jsonFile("house-rules.json", { catalog: { uuid: "c-1", metadata: { title: "House rules", version: "1", "oscal-version": "1.1.2", "last-modified": "2026-11-14T00:00:00Z" },
    groups: [{ id: "g1", title: "Doors", controls: [{ id: "hr-1", title: "Lock the door", parts: [{ id: "hr-1_smt", name: "statement", prose: "The last person to leave locks the door." }] }] }] } });
  try {
    await iAm(s, ALICE);
    await load(s, zipOf(EX, "examples"));
    /* --- a Requirement written on the Browse page --- */
    await open(s, "browse.html", "author");
    await type(p.locator("#au-title"), "Lock the door");
    await type(p.locator("#au-prose"), "The last person to leave locks the door.");
    assert.equal(await p.locator("#au-party").inputValue(), "", "who a requirement binds is not the person at the page: the field starts empty");
    const before = await snapshot(s);
    await p.locator("#au-addreq").click();
    assert.equal(await p.locator("#au-err").innerText(), "No obligated party is named. The kernel requires obligated-parties on every statement, so nothing was saved. The field “Obligated party” is empty. " + HOW);
    assert.deepEqual(await snapshot(s), before);
    await type(p.locator("#au-party"), "all staff");
    assert.equal(await p.locator("#au-party").inputValue(), NS + "/party/all-staff");
    await p.locator("#au-addreq").click();
    await p.waitForFunction(async () => (await jscStore.files(jscStore.activeSet())).some(r => r.id && r.id.endsWith("/req/lock-the-door")));
    const req = (await stored(s, "requirement")).find(r => r.id.endsWith("/req/lock-the-door"));
    assert.deepEqual(req.statements.map(st => st["obligated-parties"]), [[NS + "/party/all-staff"]]);
    await greenWithAuthors(s, t, tmp, "the example folder with a Requirement that binds a named party");

    /* --- a catalog imported by the generic rules --- */
    await open(s, "import.html");
    await p.locator("#pick").setInputFiles(catalog);
    await p.locator("#run").waitFor();
    assert.equal(await p.locator("#o-preset").inputValue(), "generic");
    assert.equal(await p.locator("#o-party").inputValue(), "");
    const set = await snapshot(s);
    await p.locator("#run").click();
    assert.match(await p.locator("#run-err").innerText(), /^No party is named that the statements bind\. The kernel requires obligated-parties on every statement and OSCAL has no field for it, so the import did not run\./);
    assert.equal(await p.locator("#write").count(), 0, "nothing was imported, so there is nothing to write");
    assert.deepEqual(await snapshot(s), set);
    await type(p.locator("#o-party"), "all staff");
    const ns = await p.locator("#o-ns").inputValue();
    assert.equal(await p.locator("#o-party").inputValue(), ns + "/party/all-staff", "a short name becomes a party under the namespace of the import");
    await p.locator("#run").click();
    await p.locator("#write").click();
    await p.locator("#log .l-ok", { hasText: "wrote" }).first().waitFor();
    const imported = (await stored(s, "requirement"));
    assert.deepEqual(imported.map(r => r.statements.map(st => st["obligated-parties"])), [[[ns + "/party/all-staff"]]]);
    assert.equal(JSON.stringify(imported).includes("/party/organization"), false, "the word the rules used to supply is not written");
    await greenWithAuthors(s, t, tmp, "a catalog of one control imported by the generic rules");
    assert.deepEqual(s.errors, []);
  } finally {
    for (const d of tmp) fs.rmSync(d, { recursive: true, force: true });
    await s.close();
  }
});

/* ---------- Browse: what was withdrawn (backlog #87; build 0.9.18) ----------
   Since phase E every withdrawn item of a catalogue is an object. The page
   leaves them out of its list and its tree until the user asks, and takes
   nothing out of the set. The numbers are counted from the committed CSF
   bundle, so the test follows the bundle. */
test("Browse: withdrawn objects are left out of the list and the tree until they are shown, and stay in the set", { skip: needs }, async () => {
  const CSF = path.join(ROOT, "converted_examples/US.CSF/csf-core-bundle");
  const objs = tree(CSF).filter(f => f.path.startsWith("objects/")).map(f => JSON.parse(f.text));
  const total = objs.length, gone = objs.filter(o => o.lifecycle === "withdrawn"), goneIds = new Set(gone.map(o => o.id));
  assert.ok(gone.length > 0 && gone.length < total, "the bundle holds withdrawn objects and others");
  const s = await session(), p = s.page;
  try {
    await load(s, zipOf(CSF, "csf-core-bundle"));
    await open(s, "browse.html", "objects");
    const before = await snapshot(s);
    const rows = () => p.locator("#objlist .objrow").evaluateAll(els => els.map(e => e.dataset.id));
    const sw = p.locator("#life-withdrawn");
    assert.equal(await sw.innerText(), `withdrawn · ${gone.length} hidden`);
    assert.equal(await sw.getAttribute("aria-pressed"), "false");
    const hiddenRows = await rows();
    assert.equal(hiddenRows.length, total - gone.length);
    assert.equal(hiddenRows.filter(id => goneIds.has(id)).length, 0, "no withdrawn object is in the list");
    assert.equal(await p.locator("#withdrawn-hint").innerText(), `${gone.length} withdrawn object(s) match and are not shown`);
    /* a search that only a withdrawn object answers says so, and does not say that nothing matches alone */
    const one = gone.find(o => o.statements);
    await type(p.locator("#search"), one.id);
    await p.locator("#search").press("Enter");
    await p.waitForFunction(() => document.querySelectorAll("#objlist .objrow").length === 0);
    assert.equal(await p.locator("#withdrawn-hint").innerText(), "1 withdrawn object(s) match and are not shown");
    await sw.click();
    assert.deepEqual(await rows(), [one.id], "shown on request");
    assert.equal(await sw.innerText(), `withdrawn · ${gone.length} shown`);
    assert.equal(await p.locator("#withdrawn-hint").count(), 0);
    await type(p.locator("#search"), "");
    await p.locator("#search").press("Enter");
    await p.waitForFunction(n => document.querySelectorAll("#objlist .objrow").length === n, total);
    /* the tree: with the switch on, every withdrawn member has its leaf; off, none, and the Set says how many it leaves out */
    await p.locator('.navitem[data-view="catalog"]').click();
    const leaves = () => p.locator("#catalog [data-ref]").evaluateAll(els => els.map(e => e.dataset.ref));
    const shownLeaves = await leaves();
    assert.ok(shownLeaves.some(id => goneIds.has(id)), "the tree shows withdrawn members when asked");
    await p.locator('.navitem[data-view="objects"]').click();
    await p.locator("#life-withdrawn").click();
    await p.locator('.navitem[data-view="catalog"]').click();
    const hiddenLeaves = await leaves();
    assert.equal(hiddenLeaves.filter(id => goneIds.has(id)).length, 0, "no withdrawn object in the tree");
    assert.ok(hiddenLeaves.length < shownLeaves.length);
    assert.match(await p.locator("#catalog").innerText(), /\d+ withdrawn not shown/);
    assert.deepEqual(await snapshot(s), before, "the set is as it was: the switch changes what the page shows");
    assert.deepEqual(s.errors, []);
  } finally { await s.close(); }
});

/* Kernel 2.0.0 (the author's decisions of 2026-11-14 on backlog #81 and #84): a statement may carry the label a reader
   of the source sees (`a.`, `(1)`), and any object a `history`. The object view of the Browse page shows the label
   beside the statement's id, and the history as a short list: the date, the comment, the reference as a link (to the
   object where it is in the set, else to the address in a new tab). */
test("Browse: a statement's label stands beside its id; an object's history is a list of date, comment and reference, in English and in German", { skip: needs }, async () => {
  const P = "https://org.example", OLD = `${P}/req/OLD-1`, NEW = `${P}/req/NEW-1`, NOTE = "https://org.example/changes/2026-11";
  const req = (id, label, extra) => ({ id, version: "2", label, lifecycle: "active", title: { en: label }, statements: [
    { id: "smt.a", label: "a.", modality: "must", "obligated-parties": [`${P}/party/ops`], prose: { en: "Do the first thing." } },
    { id: "smt.b", modality: "must", "obligated-parties": [`${P}/party/ops`], prose: { en: "Do the second thing." } }], ...extra });
  const files = [jsonFile("old.json", req(OLD, "OLD-1", {})), jsonFile("new.json", req(NEW, "NEW-1", { history: [
    { date: "2026-10", comment: { en: "Split from OLD-1.", de: "Aus OLD-1 herausgelöst." }, ref: OLD },
    { date: "2026-11-14", ref: NOTE }] }))];
  const s = await session(), p = s.page;
  try {
    await load(s, files);
    for (const lang of ["en", "de"]) {
      await p.evaluate(l => localStorage.setItem("jsc:cfg:ui:lang", l), lang);
      await open(s, "browse.html", "objects");
      await p.locator(`#objlist .objrow[data-id="${NEW}"]`).click();
      const detail = p.locator("#detail");
      await detail.locator("[data-history]").waitFor();
      /* the label stands in the line of its statement, after the id; a statement without one shows none */
      const lines = await detail.locator(".stmt > div:first-child").evaluateAll(els => els.map(e => [...e.querySelectorAll(".badge")].slice(0, 2).map(b => b.textContent.trim())));
      assert.deepEqual(lines.map(l => l[0]), lang === "de" ? ["Statement smt.a", "Statement smt.b"] : ["statement smt.a", "statement smt.b"], lang);
      assert.deepEqual(await detail.locator("[data-stmt-label]").allTextContents(), ["a."], lang);
      assert.equal(lines[0][1], "a.", lang + ": beside the id");
      assert.equal(await detail.locator("[data-stmt-label]").getAttribute("title"), lang === "de" ? "Bezeichnung des Statements in der Quelle" : "label of the statement in the source");
      /* the history: one line per entry, in the order of the object */
      assert.match(await detail.innerText(), lang === "de" ? /ÄNDERUNGSVERLAUF|Änderungsverlauf/ : /HISTORY|History/);
      const entries = await detail.locator("[data-history-entry]").allInnerTexts();
      assert.deepEqual(entries.map(e => e.replace(/\s+/g, " ").trim()),
        [`2026-10 · ${lang === "de" ? "Aus OLD-1 herausgelöst." : "Split from OLD-1."} · ${OLD}`, `2026-11-14 · ${NOTE}`], lang);
      /* a reference to an object of the set opens it; any other address is a link that leaves the page in a new tab */
      const [inSet, outside] = [detail.locator("[data-history-entry]").nth(0).locator("a"), detail.locator("[data-history-entry]").nth(1).locator("a")];
      assert.equal(await inSet.getAttribute("data-ref"), OLD);
      assert.deepEqual([await outside.getAttribute("href"), await outside.getAttribute("target")], [NOTE, "_blank"]);
      await inSet.click();
      await p.waitForFunction(id => document.querySelector("#detail .mono") && document.querySelector("#detail").textContent.includes(id) && !document.querySelector("#detail [data-history]"), OLD);
    }
    assert.deepEqual(s.errors, []);
  } finally { await s.close(); }
});

test("Risk: an empty owner refuses the risk and the catalogue import; the approver of an acceptance starts empty, also with \"Who am I\" and a default owner set; named, both are written as named", { skip: needs }, async t => {
  const s = await session(), tmp = [], p = s.page, CISO = "https://org.example/party/ciso";
  try {
    await load(s, zipOf(EX, "examples"));
    const problems = () => p.locator("#edit .problems .verdict-bad").allInnerTexts();
    const risk = async label => (await stored(s, "risk")).find(r => r.label === label);
    const NO_OWNER = "✗ error: No owner is named. The kernel requires owner-ref on a Risk, so the risk cannot be saved. The field “Owner” is empty. " + HOW;
    const NO_APPROVER = "✗ error: No approver is named. The kernel requires approver-ref on the acceptance of a Risk, so the risk cannot be saved. The field “Approver” is empty. " + HOW;

    /* --- no default owner is set: the owner field is empty, the risk cannot be saved, and the page says it in its own words --- */
    await open(s, "risk.html", "register");
    await p.locator("#new-risk").click();
    await type(p.locator("#r-label"), "R-70");
    await type(p.locator("#r-scenario"), "A door is left open overnight.");
    assert.equal(await p.locator("#r-owner").inputValue(), "");
    assert.deepEqual(await problems(), [NO_OWNER], "one line, and not the schema's “is too short” beside it");
    assert.ok(await p.locator("#r-save").isDisabled());
    assert.equal(await risk("R-70"), undefined);
    await type(p.locator("#r-owner"), "facility manager");
    assert.equal(await p.locator("#r-owner").inputValue(), NS + "/party/facility-manager", "a short name becomes a party under the namespace, here as on every page");
    assert.deepEqual(await problems(), []);
    /* an acceptance is begun: the approver is required from then on, and nothing has filled the field */
    await type(p.locator("#r-accdate"), "2026-11-14");
    await type(p.locator("#r-accwhy"), "The door is inside the guarded perimeter.");
    assert.equal(await p.locator("#r-approver").inputValue(), "");
    assert.deepEqual(await problems(), [NO_APPROVER]);
    assert.ok(await p.locator("#r-save").isDisabled());
    await type(p.locator("#r-approver"), "site director");
    assert.equal(await p.locator("#r-approver").inputValue(), NS + "/party/site-director");
    assert.deepEqual(await problems(), []);
    await p.locator("#r-save").click();
    await p.locator("#register table.flat").waitFor();
    assert.deepEqual([(await risk("R-70"))["owner-ref"], (await risk("R-70")).acceptance["approver-ref"]], [NS + "/party/facility-manager", NS + "/party/site-director"]);
    assert.equal("provenance" in await risk("R-70"), false, "the author field was empty too: that one is optional, so none is written and the save went ahead");
    /* the owner emptied on a risk that is in the set: it stays empty, and the stored risk is not written over */
    await p.locator(`[data-risk="${(await risk("R-70")).id}"]`).click();
    await type(p.locator("#r-owner"), "");
    assert.equal(await p.locator("#r-owner").inputValue(), "");
    assert.deepEqual(await problems(), [NO_OWNER]);
    assert.ok(await p.locator("#r-save").isDisabled());
    assert.equal((await risk("R-70"))["owner-ref"], NS + "/party/facility-manager");

    /* --- the catalogue: without an owner nothing is imported --- */
    await p.locator('.navitem[data-view="catalogue"]').click();
    assert.equal(await p.locator("#c-owner").inputValue(), "");
    const before = await snapshot(s);
    await p.locator("[data-import]").first().click();
    assert.equal(await p.locator("#c-err").innerText(), "No owner is named. The kernel requires owner-ref on a Risk, so nothing was imported. The field “Owner” is empty. " + HOW);
    assert.deepEqual(await snapshot(s), before);

    /* --- with "Who am I" and a default owner set: the owner starts from the setting that is made for it, the approver from nothing --- */
    await iAm(s, ALICE);
    await type(p.locator('[id="cfg-org:owner"]'), CISO);
    await open(s, "risk.html", "register");
    await p.locator("#new-risk").click();
    await type(p.locator("#r-label"), "R-71");
    await type(p.locator("#r-scenario"), "A visitor badge is not returned.");
    assert.deepEqual([await p.locator("#r-owner").inputValue(), await p.locator("#r-author").inputValue(), await p.locator("#r-approver").inputValue()], [CISO, ALICE, ""],
      "the approver is not who sits at the page and not the owner, unless somebody says so");
    await type(p.locator("#r-accdate"), "2026-11-14");
    await type(p.locator("#r-accwhy"), "Badges expire at midnight.");
    assert.deepEqual(await problems(), [NO_APPROVER]);
    await type(p.locator("#r-approver"), "https://other.example/people/bob");
    await p.locator("#r-save").click();
    await p.locator("#register table.flat").waitFor();
    const written = await risk("R-71");
    assert.deepEqual([written["owner-ref"], written.acceptance["approver-ref"], written.provenance["author-ref"]], [CISO, "https://other.example/people/bob", ALICE]);
    /* the first risk, saved again by alice: it names her now, and keeps the owner and the approver it was given */
    await p.locator(`[data-risk="${(await risk("R-70")).id}"]`).click();
    await type(p.locator("#r-title"), "Door left open");
    await p.locator("#r-save").click();
    await p.locator("#register table.flat").waitFor();
    const again = await risk("R-70");
    assert.deepEqual([again["owner-ref"], again.acceptance["approver-ref"], again.provenance["author-ref"]], [NS + "/party/facility-manager", NS + "/party/site-director", ALICE]);
    /* the catalogue's owner field starts from the same setting; emptied, it stays empty and the import is refused */
    await p.locator('.navitem[data-view="catalogue"]').click();
    assert.equal(await p.locator("#c-owner").inputValue(), CISO);
    await type(p.locator("#c-owner"), "");
    const set = await snapshot(s);
    await p.locator("[data-import]").first().click();
    assert.match(await p.locator("#c-err").innerText(), /^No owner is named\. The kernel requires owner-ref on a Risk, so nothing was imported\./);
    assert.equal(await p.locator("#c-owner").inputValue(), "", "the setting does not come back into a field the user emptied");
    assert.deepEqual(await snapshot(s), set);

    await greenWithAuthors(s, t, tmp, "the example folder with two Risks whose owner and approver were named on the page");
    assert.deepEqual(s.errors, []);
  } finally {
    for (const d of tmp) fs.rmSync(d, { recursive: true, force: true });
    await s.close();
  }
});

/* ====================================================================
   Whom a statement binds where the source does not say (backlog #74)
   ====================================================================
   A preset names one party for its corpus. The Import page shows it before
   anything is written and calls it what it is, the preset's default; the
   user may put another in its place; without a party nothing is imported;
   and what the page shows and what the set keeps say who chose. */
test("Import: a preset's party is shown as its default before anything is written; left alone it is written and named as the default; another party takes its place and is named as entered; emptied or no URI, nothing is imported", { skip: needs }, async t => {
  const DEF = "https://ns.cisecurity.org/benchmark/ubuntu-24.04-lts/party/system-administrator", MINE = "https://org.example/party/operator";
  const bound = async s => [...new Set((await stored(s, "requirement")).flatMap(r => r.statements.flatMap(st => st["obligated-parties"])))];
  const manifestProvenance = s => s.page.evaluate(async () => JSON.parse((await jscStore.files(jscStore.activeSet())).find(r => r.kind === "manifest").text).provenance);
  const pickCatalog = async (s, file) => { await s.page.goto(s.base + "import.html"); await s.page.locator("#pick").setInputFiles(file); await s.page.locator("#run").waitFor(); };
  const tmp = [];
  t.after(() => { for (const d of tmp) fs.rmSync(d, { recursive: true, force: true }); });

  /* --- the default, left alone --- */
  let s = await session(), p = s.page;
  try {
    await pickCatalog(s, jsonFile("cis.json", cisSynthetic()));
    assert.equal(await p.locator("#o-preset").inputValue(), "cis-benchmark");
    assert.deepEqual([await p.locator("#o-party").inputValue(), await p.locator("#o-party").getAttribute("data-party"), await p.locator("#o-party-default").count()], [DEF, "default", 0]);
    assert.match(await p.locator("#o-party-hint").innerText(), new RegExp("^This is the preset's default and not a value of the source: " + DEF.replace(/[.]/g, "\\.") + "\\. A catalog seldom says whom it binds"));
    await p.locator("#run").click();
    await p.locator("#write").waitFor();
    assert.deepEqual([await p.locator("[data-party-value]").innerText(), await p.locator("[data-party-origin]").getAttribute("data-party-origin"), await p.locator("[data-party-origin]").innerText()],
      [DEF, "converter-default", "the preset's default, not a value of the source"]);
    await p.locator("#write").click();
    await p.locator("#log .l-ok", { hasText: "wrote" }).first().waitFor();
    assert.equal(await p.locator("#log .l-info", { hasText: "the statements bind" }).first().innerText().then(x => x.replace(/^[\d:.]+/, "")), `the statements bind ${DEF}, the preset's default and not a value of the source`);
    assert.deepEqual(await bound(s), [DEF]);
    assert.equal("obligated-party" in await manifestProvenance(s), false, "with the default left alone the manifest says nothing about it, as before this build");
    assert.deepEqual(s.errors, []);
  } finally { await s.close(); }

  /* --- emptied, no URI, the default put back, another party --- */
  s = await session(); p = s.page;
  try {
    await pickCatalog(s, jsonFile("cis.json", cisSynthetic()));
    await type(p.locator("#o-party"), "");
    assert.deepEqual([await p.locator("#o-party").inputValue(), await p.locator("#o-party").getAttribute("data-party"), await p.locator("#o-party-default").count()], ["", "entered", 1], "an emptied field stays empty; the default does not come back by itself");
    await p.locator("#run").click();
    assert.equal(await p.locator("#run-err").innerText(), "No party is named that the statements bind. The kernel requires obligated-parties on every statement, so the import did not run. " +
      `The field “Who the statements bind” is empty. Name a party, an http(s) URI, or use the preset's default, ${DEF}.`);
    assert.equal(await p.locator("#write").count(), 0, "nothing was imported");
    await type(p.locator("#o-party"), "operator");
    await p.locator("#run").click();
    assert.match(await p.locator("#run-err").innerText(), /^“operator” is not an http\(s\) URI of a party, so the import did not run\. A preset writes under its publisher's namespace and does not make a party from a short name\./);
    assert.equal(await p.locator("#write").count(), 0);
    assert.equal(await p.locator("#o-party").inputValue(), "operator", "what was typed is not turned into something else");
    await p.locator("#o-party-default").click();
    assert.deepEqual([await p.locator("#o-party").inputValue(), await p.locator("#o-party").getAttribute("data-party")], [DEF, "default"]);
    /* the party of one set of rules is not the party of another: the generic rules start empty, a preset from its default */
    await type(p.locator("#o-party"), MINE);
    await p.locator("#o-preset").selectOption("generic");
    assert.equal(await p.locator("#o-party").inputValue(), "", "the generic rules have no default, and a preset's party is not theirs");
    await p.locator("#o-preset").selectOption("cis-benchmark");
    assert.deepEqual([await p.locator("#o-party").inputValue(), await p.locator("#o-party").getAttribute("data-party")], [DEF, "default"]);
    await type(p.locator("#o-party"), MINE);
    assert.match(await p.locator("#o-party-hint").innerText(), new RegExp("^Entered here, in the place of the preset's default " + DEF.replace(/[.]/g, "\\.") + "\\."));
    await p.locator("#run").click();
    await p.locator("#write").waitFor();
    assert.deepEqual([await p.locator("[data-party-value]").innerText(), await p.locator("[data-party-origin]").getAttribute("data-party-origin"), await p.locator("[data-party-origin]").innerText()],
      [MINE, "caller", `entered here, in the place of the preset's default ${DEF}`]);
    await p.locator("#write").click();
    await p.locator("#log .l-ok", { hasText: "wrote" }).first().waitFor();
    assert.equal(await p.locator("#log .l-info", { hasText: "the statements bind" }).first().innerText().then(x => x.replace(/^[\d:.]+/, "")), `the statements bind ${MINE}, entered here`);
    assert.deepEqual(await bound(s), [MINE], "every statement binds the party that was entered");
    assert.deepEqual((await manifestProvenance(s))["obligated-party"], { value: MINE, origin: "caller", "converter-default": DEF }, "the set keeps who named the party");
    const x = await exported(s); tmp.push(x.out);
    const ref = reference(x.dir, ["--as-of", AS_OF_46], t, "a CIS-shaped catalog imported with a party entered on the page");
    assert.ok(ref.green, ref.stdout.slice(-1200));
    assert.deepEqual(s.errors, []);
  } finally { await s.close(); }

  /* --- a source that names parties itself for some statements: said before the import and in the report --- */
  s = await session(); p = s.page;
  try {
    const rmf = "http://csrc.nist.gov/ns/rmf", NS = "https://ns.nist.gov/sp800-53";
    const control = (id, label, props) => ({ id, title: label, props: [{ name: "label", value: label }, { name: "sort-id", value: id }, ...props], parts: [{ id: id + "_smt", name: "statement", prose: "Do it." }] });
    await pickCatalog(s, jsonFile("nist.json", { catalog: { uuid: "n-1", metadata: { title: "Electronic (OSCAL) Version of NIST SP 800-53 Rev 5 test", version: "9.9", "oscal-version": "1.1.2", "last-modified": "2026-11-14T00:00:00Z" },
      groups: [{ id: "ac", title: "Access Control", controls: [control("ac-1", "AC-1", [{ name: "implementation-level", ns: rmf, value: "system" }]), control("ac-2", "AC-2", [])] }] } }));
    assert.equal(await p.locator("#o-preset").inputValue(), "nist-sp800-53");
    assert.equal(await p.locator("#o-party").inputValue(), NS + "/party/organization");
    assert.match(await p.locator("#o-party-hint").innerText(), /Where a control states an implementation level, the source names the party itself and that one is written, whatever stands here\.$/);
    await type(p.locator("#o-party"), MINE);
    await p.locator("#run").click();
    await p.locator("#write").waitFor();
    assert.equal(await p.locator("[data-party-origin]").innerText(), `entered here, in the place of the preset's default ${NS}/party/organization · 1 control(s) state no implementation level and bind this party; the others bind the level they state`);
    await p.locator("#write").click();
    await p.locator("#log .l-ok", { hasText: "wrote" }).first().waitFor();
    assert.deepEqual(Object.fromEntries((await stored(s, "requirement")).map(r => [r.label, r.statements[0]["obligated-parties"]])), { "AC-1": [NS + "/party/system"], "AC-2": [MINE] }, "the level a control states stays the source's");
    assert.deepEqual(s.errors, []);
  } finally { await s.close(); }
});

/* ====================================================================
   An Assessment's method is held to its facet (backlog #55)
   ====================================================================
   Until build 0.9.13 the Assess page wrote `method: {kind, tool}`, which
   names no facet. Such an Assessment may lie in a set a browser stored, or
   in a bundle an earlier build exported. The reference fails it now, and
   so does the Validate page. Nothing rewrites it when a set is loaded: the
   user is told, and the Assess page writes the method as the standard
   facet when asked. */
test("an Assessment with the method this app wrote before build 0.9.13: the Validate page fails it as the reference does and leaves it as it came; the Assess page rewrites it when asked, and only its own", { skip: needs }, async t => {
  const tmp = [], OLD = "https://example.org/my/asmt/audit-old", FOREIGN = "https://example.org/my/asmt/audit-foreign";
  t.after(() => { for (const d of tmp) fs.rmSync(d, { recursive: true, force: true }); });
  const asmt = (id, method, facets) => ({ id, version: "1", lifecycle: "draft", title: { en: "A check of an earlier build" }, "subject-refs": [KONF_REQ], method,
    "performer-ref": "https://example.org/my/party/jane-roe", time: "2026-11-12T10:00:00.000Z", result: "satisfied", ...(facets ? { facets } : {}) });
  /* the second Assessment fails twice: its method names a facet nobody registered, and so does one of its facets */
  const NO_SUCH_FACET = `${FOREIGN}: unregistered facet 'https://example.org/facet/notes@1' — not stdlib, not pinned in the manifest, not private: (dangerous-by-default, D10)`;
  const NO_FACET = (id, key) => `${id}: method '${key}' is no registered facet - not stdlib, not pinned in the manifest, not private: (an Assessment's method is a facet payload and fails closed, D10)`;
  const methodErrors = async s => (await s.page.evaluate(() => last.findings.filter(f => f.kind === "error").map(f => `${f.object}: ${f.message}`))).sort();
  const textOf = (s, id) => s.page.evaluate(async id => (await jscStore.files(jscStore.activeSet())).find(r => r.id === id).text, id);

  /* a set as a browser holds it after an earlier build: the example folder and two Assessments, one with the app's old method, one with a method of another making */
  let s = await session(), p = s.page, old;
  try {
    await load(s, zipOf(EX, "examples"));
    await open(s, "validate.html");
    await p.evaluate(async list => { await jscSet.load(); await jscSet.saveObjects(list); }, [asmt(OLD, { kind: "manual-check", tool: "JASCON-App 0.9.12" }), asmt(FOREIGN, { "https://example.org/facet/our-method@1": { depth: "sampled" } }, { "https://example.org/facet/notes@1": { text: "x" } })]);
    old = await exported(s); tmp.push(old.out);
    const ref = referenceRun(old.dir, ["--as-of", AS_OF_46]);
    assert.equal(ref.green, false, "the reference fails a bundle that an earlier build exported");
    assert.deepEqual([...ref.failures].sort(), [NO_FACET(FOREIGN, "https://example.org/facet/our-method@1"), NO_SUCH_FACET, NO_FACET(OLD, "kind"), NO_FACET(OLD, "tool")].sort());
    assert.deepEqual(s.errors, []);
  } finally { await s.close(); }

  /* that bundle, loaded into another browser */
  s = await session(); p = s.page;
  try {
    await load(s, zipOf(old.dir, "old"));
    const before = await textOf(s, OLD), ref = referenceRun(old.dir, ["--as-of", AS_OF_46]);
    await validatePage(s, { asOf: AS_OF_46, requireAuthors: false });
    assert.deepEqual(await methodErrors(s), [...ref.failures].sort(), "the page's errors are the reference's failures");
    assert.deepEqual(await p.evaluate(id => last.findings.filter(f => f.kind === "note" && f.area === "facet" && f.object === id).map(f => f.message), OLD),
      ["this Assessment was written by this app before build 0.9.13, with a method that names no facet (kind, tool). It is kept as it came. " +
        "The Assess page can write its method as the standard facet for a manual check; that changes the object, so an Attestation that names it no longer binds"], "and the page says what can be done");
    assert.equal(await p.evaluate(id => last.findings.filter(f => f.kind === "note" && f.area === "facet" && f.object === id).length, FOREIGN), 0, "nothing is offered for a method of another making");
    /* the Assess page shows the same, and offers the rewrite for the app's own method only */
    await open(s, "assess.html", "board");
    assert.deepEqual(await p.locator(`[data-method-errors="${OLD}"] .verdict-bad`).allInnerTexts(), ["error: " + NO_FACET(OLD, "kind"), "error: " + NO_FACET(OLD, "tool")]);
    assert.deepEqual([await p.locator(`[data-method-rewrite="${OLD}"]`).count(), await p.locator(`[data-method-rewrite="${FOREIGN}"]`).count(), await p.locator(`[data-method-errors="${FOREIGN}"] .verdict-bad`).count()], [1, 0, 1]);
    assert.deepEqual(await p.locator(`[data-method-errors="${FOREIGN}"] .verdict-bad`).allInnerTexts(), ["error: " + NO_FACET(FOREIGN, "https://example.org/facet/our-method@1")], "under the method stands what is wrong with the method, not with a facet");
    assert.equal(await p.locator("[data-method-errors]").count(), 2, "the Assessments of the example folder, whose methods are facets, show nothing");
    assert.equal(await textOf(s, OLD), before, "loading the set, checking it and looking at it rewrote nothing");
    /* asked for: the method becomes the standard facet, nothing else changes, and the Assessment fails no more */
    await p.locator(`[data-method-rewrite="${OLD}"]`).click();
    await p.waitForFunction(id => !document.querySelector(`[data-method-errors="${id}"]`), OLD);
    assert.deepEqual(JSON.parse(await textOf(s, OLD)), asmt(OLD, { "https://ns.jascon.net/stdlib/facet/assessment-criteria@1": { method: "manual" } }));
    await validatePage(s, { asOf: AS_OF_46, requireAuthors: false });
    assert.deepEqual(await methodErrors(s), [NO_FACET(FOREIGN, "https://example.org/facet/our-method@1"), NO_SUCH_FACET].sort(), "the other one still fails: it is not the app's to rewrite");
    const next = await exported(s); tmp.push(next.out);
    assert.deepEqual([...referenceRun(next.dir, ["--as-of", AS_OF_46]).failures].sort(), [NO_FACET(FOREIGN, "https://example.org/facet/our-method@1"), NO_SUCH_FACET].sort(), "and the reference says the same about the exported folder");
    assert.deepEqual(s.errors, []);
  } finally { await s.close(); }
});

/* ====================================================================
   A click right after typing (backlog #71, point 1; build 0.9.24)
   ====================================================================
   A text field reports its change when it loses the focus, and the press on
   a button is what takes the focus away. Where a form drew itself again on
   that change, the button under the press was replaced, or was still
   disabled because the form did not have the value yet, and the first click
   did nothing; the second worked. Measured with build 0.9.23 in Chromium on
   each form below. The redraw now waits for the press (jscRedraw in
   jascon-core.js).

   These tests type with the keyboard and stay in the field (`keys`), then
   press the mouse where the button lies (`press`). The helper `type` and
   locator.click() of the other tests leave the field first and wait for the
   button, which is the one path that always worked. */
test("a click right after typing is not lost: on the Tailor page the first click adds the operation, also where the button was disabled until the form had the value, and a value the form refuses adds nothing; the Checks editor, the Risk form, the scale editor and the Import page take their first click too", { skip: needs }, async t => {
  const s = await session(), p = s.page, tmp = [];
  try {
    await iAm(s, ALICE);
    await load(s, zipOf(EX, "examples"));

    /* --- Tailor: the workbench --- */
    await open(s, "tailor.html", "write");
    await type(p.locator("#t-label"), "first-click");
    await pick(s, "t-sel", "linux", LINUX_SET);
    await pick(s, "t-req", "LNX", LNX);
    await p.locator("#op-kind").selectOption("set-parameter");
    const operations = () => p.evaluate(() => JSON.parse(JSON.stringify(draft.data.operations)));
    /* a value of the wrong kind: the form takes it, the button stays disabled, and the click adds nothing */
    assert.ok(await p.locator("#op-add").isDisabled(), "no value yet");
    await keys(p, "#op-value", "four");
    await press(p, "#op-add");
    await p.waitForFunction(() => draft.data.op.value === "four");
    await p.waitForTimeout(300);   // the time a click that is handed on would have needed
    assert.deepEqual([await operations(), await p.locator("#op-add").isDisabled(), await p.locator("#op-value").inputValue()], [[], true, "four"]);
    /* a legal value: the button is disabled while the field holds it unreported, and the first click adds the operation */
    await keys(p, "#op-value", "4", true);
    assert.ok(await p.locator("#op-add").isDisabled(), "typed, and the form has not heard of it");
    await press(p, "#op-add");
    await p.locator("[data-delop]").first().waitFor();
    assert.deepEqual(await operations(), [{ op: "set-parameter", "requirement-ref": LNX, "statement-id": "s1", parameter: "max-auth-tries", value: 4 }]);
    /* a button that is enabled when the press begins and that the redraw replaces: the prose of the other statement */
    await p.locator("#op-stmt").selectOption("s2");
    await p.locator("#op-kind").selectOption("replace-prose");
    assert.ok(await p.locator("#op-add").isEnabled());
    await keys(p, "#op-prose", " Reworded.");
    await press(p, "#op-add");
    await p.locator("[data-delop]").nth(1).waitFor();
    assert.deepEqual((await operations())[1], { op: "replace-prose", "requirement-ref": LNX, "statement-id": "s2", prose: { en: "The SSH daemon offers no cipher in CBC mode. Reworded." }, intent: "editorial" }, "the click took what was typed");
    /* the click goes to the button of the form that holds the value, and what that button says stays on the page:
       a second value for the parameter that has an operation already is refused in words */
    await p.locator("#op-kind").selectOption("set-parameter");
    await keys(p, "#op-value", "3");
    await press(p, "#op-add");
    await p.locator("#op-err", { hasText: "Two operations on one target" }).waitFor();
    assert.equal(await p.locator("#op-err").innerText(), "Two operations on one target in one Tailoring are an error. Chain Tailorings to override.");
    assert.equal((await operations()).length, 2);
    /* a press on another field after typing: the field of the new form has the focus the press was for */
    await p.locator("#op-kind").selectOption("replace-prose");
    await keys(p, "#op-prose", " Again.");
    await press(p, "#op-lang");
    await p.waitForFunction(() => document.activeElement && document.activeElement.id === "op-lang" && document.activeElement.isConnected && draft.data.op.prose.endsWith(" Again."));
    await p.locator("#t-save").click();
    await p.locator("#resolve .filterrow").waitFor();
    assert.deepEqual((await stored(s, "tailoring")).find(x => x.label === "first-click").operations.map(o => o.op), ["set-parameter", "replace-prose"]);

    /* --- Checks: the editor. The last missing value is typed and "Save the check", disabled until then, is pressed --- */
    await open(s, "checks.html", "edit");
    await pick(s, "e-req", "LNX", LNX);
    await type(p.locator('[data-row="observes"][data-i="0"] [data-k="name"]'), "sshd.loglevel");
    await p.locator('[data-row="criteria"][data-i="0"] [data-k="fact"]').selectOption("sshd.loglevel");
    assert.ok(await p.locator("#e-save").isDisabled(), "the expected value is missing");
    await keys(p, '[data-row="criteria"][data-i="0"] [data-k="expected"]', '"INFO"');
    assert.ok(await p.locator("#e-save").isDisabled());
    await press(p, "#e-save");
    await p.locator("#log .l-ok", { hasText: "saved check" }).first().waitFor();
    assert.deepEqual((await stored(s, "check")).find(c => c.id.startsWith(NS + "/check/")).criteria, [{ fact: "sshd.loglevel", op: "equals", expected: "INFO" }]);
    /* the list: the filter is typed and "Edit" on a row pressed; the filter is taken and the editor opens on that check */
    const CIPHERS = "https://cso.example/check/LNX-SSH-1-ciphers";
    await p.locator('.navitem[data-view="rules"]').click();
    await keys(p, "#r-q", "LNX");
    await press(p, `[data-edit="${CIPHERS}"]`);
    await p.locator('#main > [data-view="edit"]:not(.hidden)').waitFor();
    assert.deepEqual(await p.evaluate(() => [ui.data.edit.existing, ui.data.filter.q]), [CIPHERS, "LNX"]);

    /* --- Risk: the form, whose redraw is asynchronous, and the scale editor --- */
    await open(s, "risk.html", "register");
    const risk = (await stored(s, "risk"))[0];
    await p.locator(`[data-risk="${risk.id}"]`).click();
    await p.locator("#r-save").waitFor();
    await keys(p, "#r-title", " (reworded)");
    await press(p, "#r-save");
    await p.locator("#log .l-ok", { hasText: "saved 1 object" }).first().waitFor();
    assert.equal((await stored(s, "risk"))[0].title.en, risk.title.en + " (reworded)");
    await p.locator('.navitem[data-view="scales"]').click();
    await p.locator("#scales [data-edit]").first().click();
    await keys(p, "#s-title", " (ours)");
    await press(p, "#s-save");
    await p.locator("#log .l-ok", { hasText: "scale saved" }).first().waitFor();
    assert.equal(await p.evaluate(() => [...jscSet.graph.scales.values()].filter(x => /\(ours\)$/.test((x.def.title || {}).en || "")).length), 1);

    await greenWithAuthors(s, t, tmp, "the example folder with a Tailoring, a Check, a Risk and a scale, each saved by the first click after typing");

    /* --- Import: an option is typed and "Run the import" pressed; the run uses what was typed. Nothing is written. --- */
    await p.goto(s.base + "import.html");
    await p.locator("#pick").setInputFiles(jsonFile("cis.json", cisSynthetic()));
    await p.locator("#run").waitFor();
    const ns = await p.locator("#o-ns").inputValue();
    await keys(p, "#o-ns", "-x");
    await press(p, "#run");
    await p.locator("#write").waitFor();
    assert.equal(await p.locator("#o-ns").inputValue(), ns + "-x");
    assert.deepEqual(s.errors, []);
  } finally {
    for (const d of tmp) fs.rmSync(d, { recursive: true, force: true });
    await s.close();
  }
});

/* ====================================================================
   A Check that an Assessment has run (backlog #71, point 2; build 0.9.24)
   ====================================================================
   A result of an Assessment records the digest of the check it ran
   (CHECK-8). Saving an edit of that check made the Assessment fail, and the
   Checks page said nothing: measured with build 0.9.23 on the example
   folder, two CHECK-8 failures of the reference after one save. Decided on
   2026-11-15: before saving, the page names the Assessments that ran the
   check and asks; the user may save or cancel. Saving the changed check as
   a new version beside the old one was not decided and is not offered. */
test("Checks: before a check that Assessments of the set ran is saved under another digest the page names them and asks; cancelled, nothing is written; saved, the reference fails exactly the Assessments that were named; a save that keeps the digest is not asked about", { skip: needs }, async t => {
  const CHECK = "https://cso.example/check/LNX-SSH-1-ciphers", RUNS = ["https://cso.example/assessment/bastion-01-2026-11-03", "https://cso.example/assessment/bastion-01-2026-11-10"];
  /* the rule, on the files of the example folder */
  const lib = createRequire(import.meta.url)("../jascon-checks.js");
  const g = core.jscGraphFrom(core.jscClassifyFiles(core.jscKeepFiles(tree(EX))).records), held = g.objects.get(CHECK).obj;
  const asStored = await core.jscSemanticDigest(held), changed = await core.jscSemanticDigest({ ...held, confidence: "draft" });
  assert.notEqual(asStored, changed);
  assert.deepEqual(lib.jscChecksRunBy(g.objects, CHECK, asStored, changed), [{ id: RUNS[0], label: "Daily run 2026-11-03", rows: 1 }, { id: RUNS[1], label: "Daily run 2026-11-10", rows: 1 }]);
  assert.deepEqual(lib.jscChecksRunBy(g.objects, CHECK, asStored, asStored), [], "the digest stays: no result changes its verdict");
  assert.deepEqual(lib.jscChecksRunBy(g.objects, CHECK, changed, asStored), [], "results that disagree with the stored check already are not what a save breaks");
  assert.deepEqual(lib.jscChecksRunBy(g.objects, "https://cso.example/check/none", asStored, changed), []);

  const QUESTION = `2 Assessment(s) of this set ran this check as it is stored now: Daily run 2026-11-03 (${RUNS[0]}); Daily run 2026-11-10 (${RUNS[1]}). ` +
    "Each of their results records the digest of the check it ran, and a changed check is a different check (CHECK-8). If you save, these Assessments fail CHECK-8 on the Validate page and in the reference validator until the check is run again. Save the check?";
  const s = await session(), p = s.page, tmp = [];
  try {
    await iAm(s, ALICE);
    await load(s, zipOf(EX, "examples"));
    const asked = [];
    let answer = "dismiss";
    s.onDialog = d => { asked.push(d.message()); d[answer](); };
    const saves = () => p.locator("#log .l-ok", { hasText: "saved check" }).count();
    await open(s, "checks.html", "rules");
    await p.locator(`[data-edit="${CHECK}"]`).click();
    await p.locator("#e-confidence").selectOption("draft");
    const before = await snapshot(s);
    /* cancelled */
    await p.locator("#e-save").click();
    await p.locator("#log .l-info", { hasText: "was not saved" }).first().waitFor();
    assert.deepEqual(asked, [QUESTION]);
    assert.deepEqual(await snapshot(s), before, "cancelled: the set is byte for byte what it was");
    assert.deepEqual([await saves(), await p.locator("#e-confidence").inputValue()], [0, "draft"], "nothing was saved, and the form keeps the edit");
    /* saved */
    answer = "accept";
    await p.locator("#e-save").click();
    await p.locator("#log .l-ok", { hasText: "saved check" }).first().waitFor();
    assert.deepEqual(asked, [QUESTION, QUESTION]);
    assert.equal((await stored(s, "check")).find(c => c.id === CHECK).confidence, "draft");
    assert.equal(await p.locator("#log .l-warn", { hasText: "fail CHECK-8 now" }).last().evaluate(n => n.lastChild.textContent),
      `2 Assessment(s) ran the check as it was and fail CHECK-8 now, until the check is run again: Daily run 2026-11-03 (${RUNS[0]}); Daily run 2026-11-10 (${RUNS[1]})`);
    /* saved once more, unchanged, by the same author on the same day: the digest stays, no result changes, and nothing is asked */
    await p.locator("#e-save").click();
    await p.waitForFunction(() => [...document.querySelectorAll("#log .l-ok")].filter(n => n.textContent.includes("saved check")).length === 2);
    assert.equal(asked.length, 2);
    s.onDialog = null;
    /* the reference on the export: the Assessments the page named, each for the result that ran this check, and nothing else */
    const out = await exported(s); tmp.push(out.out);
    const ref = referenceRun(out.dir, ["--as-of", AS_OF_46]);
    t.diagnostic(`validate_core.py on the export after the save: ${ref.pass} pass, ${ref.failures.length} failure(s)`);
    assert.deepEqual(ref.failures, RUNS.map(a => `${a}: check-results[1]: check-digest does not match ${CHECK} - the check changed after the run (CHECK-8: a result names the check it ran and that check's semantic digest - a changed check is a different check)`));
    assert.deepEqual(s.errors, []);
  } finally {
    for (const d of tmp) fs.rmSync(d, { recursive: true, force: true });
    await s.close();
  }
});

