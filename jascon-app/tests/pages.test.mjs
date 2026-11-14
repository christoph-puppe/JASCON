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
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const APP = path.join(ROOT, "jascon-app");
const core = createRequire(import.meta.url)("../jascon-core.js");
let chromium = null;
try { ({ chromium } = createRequire(import.meta.url)("playwright")); } catch (e) { /* skipped below */ }

const MIME = { ".html": "text/html", ".js": "text/javascript", ".css": "text/css", ".json": "application/json", ".md": "text/markdown" };
function serve() {
  const server = http.createServer((req, res) => {
    const file = path.join(ROOT, decodeURIComponent(new URL(req.url, "http://x").pathname));
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
/* a browser on the app -> { page, base, errors, close() }; a dialog nobody expects is an error */
async function session() {
  const server = await serve(), base = `http://127.0.0.1:${server.address().port}/jascon-app/`;
  const browser = await chromium.launch(), page = await (await browser.newContext({ acceptDownloads: true })).newPage(), errors = [];
  page.on("pageerror", e => errors.push(`${page.url().split("/").pop()}: ${e.message}`));
  page.on("console", m => { if (m.type() === "error") errors.push(`${page.url().split("/").pop()}: ${m.text()}`); });
  page.on("dialog", d => { errors.push("a dialog asked: " + d.message()); d.dismiss(); });
  await page.goto(base + "index.html");
  await page.waitForFunction(() => document.querySelector("#help h1"));
  await page.evaluate(() => localStorage.setItem("jsc:cfg:ui:lang", "en"));
  return { page, base, errors, close: async () => { await browser.close(); server.close(); } };
}
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
  const summary = lines[end].trim(), section = `- [${summary.match(/^(.*?): \d+ pass, \d+ fail/)[1]}] `;
  return { green: run.status === 0 && /\nALL GREEN\s*$/.test(run.stdout), summary,
    said: lines.slice(from, end).map(l => l.trim()).filter(l => /\((AUTHOR-[1-4]|REVIEW-1)[):]/.test(l)),
    failures: lines.map(l => l.trim()).filter(l => l.startsWith(section)).map(l => l.slice(section.length)), stdout: run.stdout };
}
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
  const server = await serve(), base = `http://127.0.0.1:${server.address().port}/jascon-app/`;
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
    await page.locator("#pick-files").setInputFiles([path.join(EX, "req-konf-14-1.json"), path.join(EX, "gspp-taxonomy-1.0.0.json")]);
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
      const line = run.stdout.split("\n").find(l => l.includes(path.basename(out))) || "";
      fs.rmSync(out, { recursive: true });
      assert.match(line, / 0 fail/, run.stdout.slice(-1500));
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
  const loose = ["req-konf-14-1.json", "req-ism-1234.json", "req-iec-cso-iir.json", "set-crypto.json", "set-baseline.json", "gspp-taxonomy-1.0.0.json"].map(f => path.join(EX, f));
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
    assert.deepEqual(s.errors, []);
  } finally {
    for (const d of tmp) fs.rmSync(d, { recursive: true, force: true });
    await s.close();
  }
});
