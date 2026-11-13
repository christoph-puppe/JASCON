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
const NA_FILE = path.join(DEMO, "not-applicable.json");
const notApplicable = riskcat.jscNaRead(json(NA_FILE), JSC_PRESETS.catalogs, "en");
const OFF23 = office.entries.find(e => e.label === "OFF-23");
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

test("the record of entries that do not apply: its schema, its bytes, and the map of before 2026-11-13 (backlog #54)", () => {
  const schema = json(path.join(ROOT, "risk-catalogs/schema/not-applicable.draft.schema.json"));
  const committed = json(NA_FILE);
  assert.deepEqual(rules.jscSchemaCheck(schema, committed, schema).errors, [], "the committed record fits its schema");
  // reading and writing the committed record gives its bytes back
  assert.equal(core.jscSerialize(riskcat.jscNaWrite(notApplicable)), fs.readFileSync(NA_FILE, "utf8"));
  const row = notApplicable[OFF23.id];
  assert.deepEqual(row.provenance, { "author-ref": "https://org.example/party/ciso", date: "2026-11-10" });
  // the schema refuses what the record must not be
  const bad = doc => rules.jscSchemaCheck(schema, doc, schema).errors.length > 0;
  assert.ok(bad({ "OFF-23": "a sentence" }), "the old map is not the record");
  assert.ok(bad({ "record-version": 1, entries: [{ ...row, rationale: "a sentence" }] }), "a rationale is a text in a language");
  assert.ok(bad({ "record-version": 1, entries: [{ ...row, provenance: { "author-ref": "https://org.example/party/ciso" } }] }), "an author without a date");
  assert.ok(bad({ "record-version": 1, entries: [{ ...row, provenance: { ...row.provenance, date: "last week" } }] }), "a date any string satisfies");
  assert.ok(!bad({ "record-version": 1, entries: [{ entry: row.entry, rationale: row.rationale }] }), "a row without an author is reported, not refused");
  // the old map: a label is resolved to the entry's id, and nobody is invented as its author
  const old = riskcat.jscNaRead({ "OFF-23": "Blocked at the proxy.", [office.entries[0].id]: "Not our business." }, JSC_PRESETS.catalogs, "de");
  assert.deepEqual(old[OFF23.id], { entry: OFF23.id, rationale: { de: "Blocked at the proxy." } });
  assert.deepEqual(old[office.entries[0].id], { entry: office.entries[0].id, rationale: { de: "Not our business." } });
  assert.deepEqual(rules.jscSchemaCheck(schema, riskcat.jscNaWrite(old), schema).errors, [], "what the old map becomes fits the schema");
  const rows = riskcat.jscCatalogCompleteness(office.entries, new Map(), old);
  assert.equal(rows.filter(x => x.status === "not-applicable").length, 2);
  assert.equal(rows.find(x => x.entry.id === OFF23.id).row.provenance, undefined);
  // a record of a version this build does not know is not guessed at
  assert.deepEqual(riskcat.jscNaRead({ "record-version": 2, entries: [row] }, JSC_PRESETS.catalogs, "en"), {});
});

test("the shipped scale presets pass the scale rules, matrices included", () => {
  for (const set of JSC_PRESETS.scaleSets) {
    const r = rules.jscCheckScales(set.scales, new Map());
    assert.deepEqual(r.errors, [], set.key);
    assert.equal([...r.scales.values()].filter(sd => sd.matrix).length, 1, set.key + " has one level scale with a matrix");
  }
});
