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
