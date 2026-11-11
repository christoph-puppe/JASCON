/* Opens every page of the app in a real browser and fails on any script
   error. This is the check that the pages still start: a unit test of the
   core cannot see a page that forgot to load a script the core now needs
   (see ERRATA.md, 2026-11-10).

   It serves the repository from a throwaway local server, loads the IFA
   bundle through the hub, then opens each tool page on that set, in English
   and in German. Needs Playwright with Chromium; where that is missing the
   test is skipped and says so. */
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const APP = path.join(ROOT, "jascon-app");
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
