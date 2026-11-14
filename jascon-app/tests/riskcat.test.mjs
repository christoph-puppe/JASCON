/* The catalogue import against the demo the repository commits
   (risk-catalogs/demo/office-it-moderate/, built by the Python tools):
   the same Risks, the same report, and the coverage numbers the catalogue
   README states for it. */
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
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
const PUBLISHER = "https://github.com/christoph-puppe";   // the publisher-ref both shipped catalogues state

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
    "suggestions-out-of-scope", "without-treatment", "selected-requirements-no-entry-suggests", "provenance", "without-provenance"]) assert.deepEqual(report[k], want[k], k);
  /* who and when: the catalogue's publisher and the day this version was released, on every imported Risk */
  const FROM_CATALOGUE = { "author-ref": PUBLISHER, date: "2026-11-10" }, BY_ORG = { "author-ref": "https://org.example/party/ciso", date: "2026-11-12" };
  assert.deepEqual([office.catalog["publisher-ref"], office.catalog.released], [PUBLISHER, "2026-11-10"]);
  assert.deepEqual(report.provenance, { stated: FROM_CATALOGUE, given: {}, records: { "from-source": 23, "from-caller": 0, none: 0 } });
  assert.deepEqual(report["without-provenance"], []);
  /* The demo then played the organisation for two risks (assessed, rated,
     tied to a component). Everything the import itself writes must match;
     the two risks the organisation assessed are its version, and say so. */
  const imported = ["id", "version", "label", "title", "scenario", "owner-ref", "tailoring-refs", "treatments", "relations", "annotations"];
  let assessed = 0;
  for (const r of risks) {
    const c = committed.get(r.id);
    assert.ok(c, r.id + " is in the demo");
    for (const k of imported) assert.deepEqual(r[k], c[k], `${r.id} ${k}`);
    assert.deepEqual(r.provenance, FROM_CATALOGUE, r.id);
    if (c.state === "identified") assert.deepEqual(c.provenance, FROM_CATALOGUE, `${r.id}: as imported`);
    else { assessed++; assert.deepEqual([c.provenance, c.rating.provenance, c["residual-rating"].provenance], [BY_ORG, BY_ORG, BY_ORG], `${r.id}: assessed by the organisation`); }
    assert.deepEqual(rules.jscMatchTypes(r), ["risk"], r.id + " is a valid Risk");
    assert.deepEqual(rules.jscMatchTypes(c), ["risk"], r.id + " of the demo is a valid Risk");
  }
  assert.equal(assessed, 2);
  assert.deepEqual(tailoring.provenance, { "author-ref": "https://org.example/party/ciso", date: "2026-11-10" }, "the demo's Statement of Applicability names its author");
  // a second import finds every Risk in place and writes nothing
  risks.forEach(r => objs.set(r.id, { type: "risk", obj: r }));
  const again = riskcat.jscCatalogImport(office.catalog, office.entries, objs,
    { org: "https://org.example", owner: "https://org.example/party/ciso", tailoring: tailoring.id, notApplicable });
  assert.equal(again.risks.length, 0);
  assert.equal(again.report["already-there"].length, 23);
});

/* Who and when on an imported Risk (backlog #69). The catalogue states both:
   its publisher and the day the version was released. The caller may give
   either, and what is given replaces what the catalogue states. */
const importWith = (catalog, extra) => {
  const objs = sp80053();
  objs.set(tailoring.id, { type: "tailoring", obj: tailoring });
  return riskcat.jscCatalogImport(catalog, office.entries, objs, { org: "https://org.example", owner: "https://org.example/party/ciso", tailoring: tailoring.id, notApplicable, ...extra });
};
test("catalogue import: the caller's author and day replace the catalogue's, field by field; a Risk gets provenance only with both", () => {
  const ALICE = "https://org.example/party/alice";
  const all = (res, want) => { assert.equal(res.error, undefined); assert.equal(res.risks.length, 23); for (const r of res.risks) assert.deepEqual(r.provenance, want, r.id); };
  const who = importWith(office.catalog, { authorRef: ALICE });
  all(who, { "author-ref": ALICE, date: "2026-11-10" });
  assert.deepEqual(who.report.provenance, { stated: { "author-ref": PUBLISHER, date: "2026-11-10" }, given: { "author-ref": ALICE }, records: { "from-source": 0, "from-caller": 23, none: 0 } });
  const when = importWith(office.catalog, { date: "2026-11-13" });
  all(when, { "author-ref": PUBLISHER, date: "2026-11-13" });
  assert.deepEqual(when.report.provenance.given, { date: "2026-11-13" });
  all(importWith(office.catalog, { authorRef: ALICE, date: "2026-11-13" }), { "author-ref": ALICE, date: "2026-11-13" });
  /* the caller says nobody: no provenance, the Risks are valid, and the report names every one of them */
  const nobody = importWith(office.catalog, { authorRef: "" });
  all(nobody, undefined);
  assert.deepEqual(nobody.report.provenance.records, { "from-source": 0, "from-caller": 0, none: 23 });
  assert.deepEqual(nobody.report["without-provenance"], nobody.report.imported);
  for (const r of nobody.risks) assert.deepEqual(rules.jscMatchTypes(r), ["risk"], r.id);
  /* a catalogue that does not say when it was released: nothing is made up for the day */
  const { released: _released, ...undated } = office.catalog;
  const bare = importWith(undated, {});
  all(bare, undefined);
  assert.deepEqual(bare.report.provenance, { stated: { "author-ref": PUBLISHER, date: null }, given: {}, records: { "from-source": 0, "from-caller": 0, none: 23 } });
  assert.equal(bare.report["without-provenance"].length, 23);
  all(importWith(undated, { date: "2026-11-13" }), { "author-ref": PUBLISHER, date: "2026-11-13" });
  /* no publisher either: the caller gives both, or none is written */
  const { "publisher-ref": _publisher, ...anonymous } = undated;
  all(importWith(anonymous, { date: "2026-11-13" }), undefined);
  all(importWith(anonymous, { authorRef: ALICE, date: "2026-11-13" }), { "author-ref": ALICE, date: "2026-11-13" });
  /* a day that is no date is refused with the reason, and nothing is imported */
  const wrong = importWith(office.catalog, { date: "13.11.2026" });
  assert.match(wrong.error, /is not a date, YYYY-MM-DD/);
  assert.deepEqual(wrong.risks, []);
});

const python = spawnSync("python3", ["-c", "import jsonschema"], { encoding: "utf8" }).status === 0;
test("catalogue import: risk_catalog.py writes the same Risks and the same report, with and without --author-ref and --date", { skip: !python && "python3 with jsonschema is not installed" }, () => {
  const bundle = path.join(ROOT, "converted_examples/US.SP800-53/sp800-53-core-bundle"), tool = path.join(ROOT, "risk-catalogs/tools/risk_catalog.py");
  const objs = sp80053(), tmp = fs.mkdtempSync(path.join(os.tmpdir(), "jascon-riskcat-"));
  const ALICE = "https://org.example/party/alice";
  const cases = [[], ["--author-ref", ALICE], ["--date", "2026-11-13"], ["--author-ref", ALICE, "--date", "2026-11-13"], ["--author-ref", ""], ["--date", ""]];
  const command = (dir, flags) => spawnSync("python3", [tool, "import", path.join(ROOT, "risk-catalogs/office-it"), "--bundle", bundle, "--org", "https://org.example",
    "--owner", "https://org.example/party/ciso", "--out", dir, ...flags], { encoding: "utf8" });
  try {
    cases.forEach((flags, n) => {
      const dir = path.join(tmp, String(n)), run = command(dir, flags), what = flags.join(" ") || "no flags";
      assert.equal(run.status, 0, run.stderr);
      const given = {};
      for (let i = 0; i < flags.length; i += 2) given[flags[i] === "--author-ref" ? "authorRef" : "date"] = flags[i + 1];
      const mine = riskcat.jscCatalogImport(office.catalog, office.entries, objs, { org: "https://org.example", owner: "https://org.example/party/ciso", tailoring: null, notApplicable: {}, ...given });
      assert.equal(mine.error, undefined);
      const { "already-there": _there, ...report } = mine.report;   // the app skips a Risk that is in the set; the command line writes a folder and has no such case
      assert.deepEqual(report, json(path.join(dir, "import-report.json")), what);
      assert.equal(mine.risks.length, 24);
      for (const r of mine.risks) assert.deepEqual(r, json(path.join(dir, r.label + ".json")), `${r.id} ${what}`);
      const rec = mine.report.provenance.records;
      assert.ok(run.stdout.includes(`authors     ${rec["from-source"]} as the catalogue states, ${rec["from-caller"]} as given, ${rec.none} imported risk(s) name no author`), what + "\n" + run.stdout);
    });
    const bad = command(path.join(tmp, "bad"), ["--date", "13.11.2026"]);
    assert.notEqual(bad.status, 0);
    assert.match(bad.stderr, /is not a date, YYYY-MM-DD/);
    assert.equal(fs.existsSync(path.join(tmp, "bad")), false, "a refused import writes nothing");
  } finally { fs.rmSync(tmp, { recursive: true }); }
});

test("the catalogue schema: `released` is optional and a date; both shipped catalogues state it", { skip: !python && "python3 with jsonschema is not installed" }, () => {
  const schema = json(path.join(ROOT, "risk-catalogs/schema/risk-catalog.draft.schema.json"));
  const errors = cat => rules.jscSchemaCheck({ $ref: "#/$defs/catalog", $defs: schema.$defs }, cat, schema).errors;
  for (const c of JSC_PRESETS.catalogs) {
    assert.equal(c.catalog.released, "2026-11-10", c.catalog.id);
    assert.deepEqual(errors(c.catalog), [], c.catalog.id);
  }
  const { released: _released, ...undated } = office.catalog;
  assert.deepEqual(errors(undated), [], "a catalogue without the day is a catalogue");
  for (const bad of ["last week", "2026-11-10T08:00:00Z", "10.11.2026", "", 20261110]) assert.ok(errors({ ...office.catalog, released: bad }).length > 0, JSON.stringify(bad));
  /* the reference tool reads both catalogues as valid */
  for (const name of ["office-it", "industrial-plant"]) {
    const run = spawnSync("python3", [path.join(ROOT, "risk-catalogs/tools/risk_catalog.py"), "validate", path.join(ROOT, "risk-catalogs", name)], { encoding: "utf8" });
    assert.equal(run.status, 0, run.stdout + run.stderr);
  }
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
