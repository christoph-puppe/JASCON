/* The catalogue import against the demo the repository commits
   (risk-catalogs/demo/office-it-moderate/, built by the Python tools):
   the same Risks, the same report, and the coverage numbers the catalogue
   README states for it. */
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const require = createRequire(import.meta.url);
const core = require("../jascon-core.js"), rules = require("../jascon-rules.js"), riskcat = require("../jascon-riskcat.js");
const { JSC_PRESETS } = require("../jascon-presets.js");
const DEMO = path.join(ROOT, "risk-catalogs/demo/office-it-moderate");
const json = f => JSON.parse(fs.readFileSync(f, "utf8"));

function sp80053() {
  const dir = path.join(ROOT, "converted_examples/US.SP800-53/sp800-53-core-bundle");
  const manifest = json(path.join(dir, "content-manifest.json"));
  return new Map(manifest.objects.map(e => { const o = json(path.join(dir, e.path)); return [o.id, { type: core.jscInferType(o), obj: o }]; }));
}
const office = JSC_PRESETS.catalogs.find(c => c.catalog.id.endsWith("/office-it"));
const tailoring = json(path.join(DEMO, "tailoring-soa-office-it.json"));
const notApplicable = json(path.join(DEMO, "not-applicable.json"));
const committed = new Map(fs.readdirSync(path.join(DEMO, "risks")).sort().map(f => { const o = json(path.join(DEMO, "risks", f)); return [o.id, o]; }));

test("importing the office-IT catalogue reproduces the committed demo", () => {
  const objs = sp80053();
  objs.set(tailoring.id, { type: "tailoring", obj: tailoring });
  const { risks, report, error } = riskcat.jscCatalogImport(office.catalog, office.entries, objs,
    { org: "https://org.example", owner: "https://org.example/party/ciso", tailoring: tailoring.id, notApplicable });
  assert.equal(error, undefined);
  assert.equal(risks.length, 23);
  assert.equal(report["not-applicable"].length, 1);
  const want = json(path.join(DEMO, "import-report.json"));
  for (const k of ["catalog", "catalog-version", "selection", "selected-requirements", "imported", "not-applicable",
    "suggestions-out-of-scope", "without-treatment", "selected-requirements-no-entry-suggests"]) assert.deepEqual(report[k], want[k], k);
  /* The demo then played the organisation for two risks (assessed, rated,
     tied to a component). Everything the import itself writes must match. */
  const imported = ["id", "version", "label", "title", "scenario", "owner-ref", "tailoring-refs", "treatments", "relations", "annotations"];
  for (const r of risks) {
    const c = committed.get(r.id);
    assert.ok(c, r.id + " is in the demo");
    for (const k of imported) assert.deepEqual(r[k], c[k], `${r.id} ${k}`);
    assert.deepEqual(rules.jscMatchTypes(r), ["risk"], r.id + " is a valid Risk");
  }
  // a second import finds every Risk in place and writes nothing
  risks.forEach(r => objs.set(r.id, { type: "risk", obj: r }));
  const again = riskcat.jscCatalogImport(office.catalog, office.entries, objs,
    { org: "https://org.example", owner: "https://org.example/party/ciso", tailoring: tailoring.id, notApplicable });
  assert.equal(again.risks.length, 0);
  assert.equal(again.report["already-there"].length, 23);
});

test("coverage of the demo: the numbers the catalogue README states", async () => {
  const objs = sp80053();
  objs.set(tailoring.id, { type: "tailoring", obj: tailoring });
  for (const [id, o] of committed) {
    const { "component-refs": _component, ...risk } = o;   // the demo's component is not part of this graph
    objs.set(id, { type: "risk", obj: risk });
  }
  const { report, errors } = await rules.jscRiskCoverage(objs);
  assert.deepEqual(errors, []);
  const t = report.tailorings[tailoring.id];
  assert.equal(t.selected, 287, "requirements selected by the Tailoring");
  assert.equal(Object.keys(t.covered).length, 13, "justified by a Risk");
  assert.equal(Object.keys(t.pending).length, 65, "named only by a Risk still identified");
  assert.equal(t.uncovered.length - Object.keys(t.pending).length, 209, "named by no entry at all");
});

test("completeness: an entry is instantiated, recorded as not applicable, or a gap", () => {
  const objs = new Map([...committed].map(([id, o]) => [id, { type: "risk", obj: o }]));
  const withRecord = riskcat.jscCatalogCompleteness(office.entries, objs, notApplicable);
  assert.equal(withRecord.filter(x => x.status === "instantiated").length, 23);
  assert.equal(withRecord.filter(x => x.status === "not-applicable").length, 1);
  assert.equal(withRecord.filter(x => x.status === "gap").length, 0);
  assert.equal(riskcat.jscCatalogCompleteness(office.entries, objs, {}).filter(x => x.status === "gap").length, 1);
});

test("the shipped scale presets pass the scale rules, matrices included", () => {
  for (const set of JSC_PRESETS.scaleSets) {
    const r = rules.jscCheckScales(set.scales, new Map());
    assert.deepEqual(r.errors, [], set.key);
    assert.equal([...r.scales.values()].filter(sd => sd.matrix).length, 1, set.key + " has one level scale with a matrix");
  }
});
