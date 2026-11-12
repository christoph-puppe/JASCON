#!/usr/bin/env node
/* Census of OSCAL component definitions through the pack builder's import
   (CP-ADVICE-1 §2.3; specification D22, D25).

   For every file in sources/ it opens one-page-apps/jascon-pack-builder.html
   in Chromium, imports the file twice, once into a page with no catalogue
   and once with the SP 800-53 Rev 5 catalogue of converted_examples/
   loaded, and records what the import made of it next to what the source
   holds. A prompt for an id prefix is answered with nothing, so a control
   the page cannot resolve is counted as unresolved and not guessed.

   The measurement is the builder's own code: what this prints is what a
   vendor sees. Writes census.json beside this file and prints a table.

     node drafts/cp-advice-1-census/run_census.mjs

   Needs Playwright with Chromium. Running it twice gives the same
   census.json, apart from its "measured" date. */
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { createRequire } from "node:module";
import { fileURLToPath, pathToFileURL } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "../..");
const { chromium } = createRequire(import.meta.url)("playwright");
const PAGE = pathToFileURL(path.join(ROOT, "one-page-apps/jascon-pack-builder.html")).href;
const CATALOGUE = path.join(ROOT, "converted_examples/US.SP800-53/sp800-53-core-bundle");
const SOURCES = path.join(HERE, "sources");

/* what the source holds, counted from the file itself */
function sourceCounts(doc) {
  const cd = doc["component-definition"], comps = cd.components || [];
  const cis = comps.flatMap(c => c["control-implementations"] || []);
  const irs = cis.flatMap(ci => ci["implemented-requirements"] || []);
  return {
    "oscal-version": cd.metadata && cd.metadata["oscal-version"],
    components: comps.length,
    "component-types": comps.map(c => c.type),
    "control-implementations": cis.length,
    "implemented-requirements": irs.length,
    "control-ids": irs.map(ir => ir["control-id"]),
    statements: irs.reduce((n, ir) => n + (ir.statements || []).length, 0),
    "set-parameters": irs.reduce((n, ir) => n + (ir["set-parameters"] || []).length, 0) + cis.reduce((n, ci) => n + (ci["set-parameters"] || []).length, 0),
    sources: [...new Set(cis.map(ci => ci.source))],
    "insert-markup": (JSON.stringify(doc).match(/\{\{\s*insert:/g) || []).length,
  };
}

async function importOnce(browser, file, withCatalogue) {
  const page = await (await browser.newContext()).newPage();
  const errors = [], prompts = [];
  page.on("pageerror", e => errors.push(e.message));
  page.on("dialog", d => { if (d.type() === "prompt") prompts.push(d.message()); return d.accept(d.type() === "prompt" ? "" : undefined); });
  const ready = () => page.locator('body[data-state="ready"]').waitFor();
  await page.goto(PAGE);
  await ready();
  if (withCatalogue) { await page.setInputFiles("#pick-cat-folder", CATALOGUE); await ready(); }
  for (const [sel, v] of [['[data-bind="origin"]', "https://vendor.example"], ['[data-bind="pack.id"]', "https://vendor.example/pack/census"]]) {
    await page.locator(sel).fill(v); await page.locator(sel).dispatchEvent("change"); await ready();
  }
  await page.setInputFiles("#pick-oscal", file);
  await ready();
  const r = await page.evaluate(() => ({ report: window.jscPackBuilder.report(), draft: window.jscPackBuilder.draft(), problems: window.jscPackBuilder.problems() }));
  await page.context().close();
  const caps = r.draft.components.flatMap(c => c.caps);
  const rules = {};
  for (const p of r.problems.filter(p => p.level === "error")) rules[p.rule] = (rules[p.rule] || 0) + 1;
  return {
    resolved: r.report.how, unresolved: r.report.unresolved,
    recommendations: caps.length,
    "requirement-refs": caps.map(k => k.requirementRef),
    clauses: r.report.clauses, "clauses-not-in-catalogue": r.report.clausesMissing,
    "statement-ids": caps.filter(k => k.statementIds.length).map(k => `${k.requirementRef.split("/").pop()}: ${k.statementIds.join(", ")}`),
    values: r.report.values, "values-not-placed": r.report.valuesUnplaced,
    bindings: caps.filter(k => Object.keys(k.bindings).length).map(k => `${k.requirementRef.split("/").pop()}: ${JSON.stringify(k.bindings)}`),
    "insert-markup-left": caps.reduce((n, k) => n + (JSON.stringify(k.description).match(/\{\{\s*insert:/g) || []).length, 0),
    notes: r.report.notes || [],
    kinds: r.report.kinds, "not-carried": r.report.dropped,
    "errors-by-rule": rules, prompts: prompts.length, "page-errors": errors,
  };
}

const browser = await chromium.launch();
const files = fs.readdirSync(SOURCES).filter(f => f.endsWith(".json")).sort();
const census = { measured: new Date().toISOString().slice(0, 10),
  builder: null, inputs: "drafts/cp-advice-1-census/sources/ (see README.md for their origin)", files: [] };
for (const f of files) {
  const file = path.join(SOURCES, f), bytes = fs.readFileSync(file);
  const doc = JSON.parse(bytes.toString("utf8"));
  const entry = { file: f, sha256: crypto.createHash("sha256").update(bytes).digest("hex"),
    "canonical-sha256": crypto.createHash("sha256").update(JSON.stringify(doc)).digest("hex"),
    source: sourceCounts(doc), "without-catalogue": await importOnce(browser, file, false), "with-sp800-53-rev5": await importOnce(browser, file, true) };
  census.files.push(entry);
}
const probe = await (await browser.newContext()).newPage();
await probe.goto(PAGE);
census.builder = await probe.evaluate(() => window.jscPackBuilder.version);
await browser.close();
fs.writeFileSync(path.join(HERE, "census.json"), JSON.stringify(census, null, 1) + "\n");

const row = (f, run) => {
  const x = f[run];
  return `${f.file.padEnd(40)} ${run.padEnd(18)} recs ${String(x.recommendations).padStart(2)}  resolved cat/nist/prefix ${x.resolved.catalogue}/${x.resolved.nist}/${x.resolved.prefix}  unresolved ${x.unresolved.length}  clauses ${x.clauses} (missing ${x["clauses-not-in-catalogue"].length})  values ${x.values} (not placed ${x["values-not-placed"].length})  markup left ${x["insert-markup-left"]}  errors ${JSON.stringify(x["errors-by-rule"])}`;
};
console.log(`builder ${census.builder}, ${files.length} file(s)`);
for (const f of census.files) for (const run of ["without-catalogue", "with-sp800-53-rev5"]) console.log(row(f, run));
