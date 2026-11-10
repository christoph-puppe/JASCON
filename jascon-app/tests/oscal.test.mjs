/* The OSCAL import against what the repository ships.

   - BSI preset: every object the import makes from the Anwenderkatalog
     Grundschutz++ has the semantic digest the shipped bundle's manifest
     states for it, and the pinned facet schemas are the same.
   - Generic rules on NIST SP 800-53: every object is a valid kernel object
     and every reference closes.
   - Profile import: the NIST MODERATE profile, imported into the shipped
     SP 800-53 bundle, selects exactly the members of the bundle's own
     MODERATE baseline Set.

   The first three need the publishers' source files, which the repository
   does not carry (sources/ is ignored). Without them they are skipped; the
   readme says where the files come from. */
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const require = createRequire(import.meta.url);
const core = require("../jascon-core.js"), rules = require("../jascon-rules.js"), oscal = require("../jascon-oscal.js");
const json = f => JSON.parse(fs.readFileSync(f, "utf8"));
const BSI_SRC = path.join(ROOT, "sources/Grundschutz++-catalog.json");
const NIST_SRC = path.join(ROOT, "sources/nist/NIST_SP-800-53_rev5_catalog.json");
const NIST_MOD = path.join(ROOT, "sources/nist/NIST_SP-800-53_rev5_MODERATE-baseline_profile.json");
const missing = f => !fs.existsSync(f) && `source file not present: ${path.relative(ROOT, f)}`;

test("BSI preset: every object has the semantic digest of the shipped DE.BSI bundle", { skip: missing(BSI_SRC) }, async () => {
  const dir = path.join(ROOT, "converted_examples/DE.BSI/bsi-core-bundle"), manifest = json(path.join(dir, "content-manifest.json"));
  const src = json(BSI_SRC);
  assert.equal(src.catalog.metadata.version, manifest.provenance.sources[0].version, "the source file is the version the shipped bundle was converted from");
  assert.equal(oscal.jscOscalGuessPreset(src), "bsi-gspp");
  const out = oscal.jscOscalImportCatalog(src, { preset: "bsi-gspp" });
  const want = new Map(manifest.objects.map(e => [e.path, e]));
  assert.deepEqual(out.objects.map(o => o.path).sort(), [...want.keys()].sort(), "the same files");
  let differ = 0, first = "";
  for (const o of out.objects) {
    const e = want.get(o.path);
    if (o.obj.id !== e.id || await core.jscSemanticDigest(o.obj) !== e["semantic-digest"]) { differ++; first = first || o.path; }
  }
  assert.equal(differ, 0, `objects whose meaning differs from the shipped bundle (first: ${first})`);
  assert.equal(out.objects.length, 813);
  for (const f of out.facetSchemas) assert.deepEqual(f.def, json(path.join(dir, f.path)), f.path);
  assert.deepEqual(out.facetSchemas.map(f => f.path).sort(), manifest["facet-schemas"].map(e => e.path).sort());
  // the converter's own count of source defects: pseudo-placeholders in prop values, reported and not repaired
  assert.equal(out.report["source-defects"].length, 213);
});

test("generic rules: NIST SP 800-53 becomes valid kernel objects whose references close", { skip: missing(NIST_SRC) }, () => {
  const src = json(NIST_SRC);
  assert.equal(oscal.jscOscalGuessPreset(src), "generic");
  const out = oscal.jscOscalImportCatalog(src, { preset: "generic", ns: "https://example.org/fw/sp800-53", lang: "en", key: "sp800-53" });
  let controls = 0;
  const walk = n => { for (const c of n.controls || []) { controls++; walk(c); } for (const g of n.groups || []) walk(g); };
  walk(src.catalog);
  assert.equal(out.report.controls, controls, "every control, nested ones included, became a Requirement");
  const objs = new Map();
  for (const o of out.objects) {
    const type = rules.jscTypeOf(o.obj);
    assert.ok(type === "requirement" || type === "requirementSet", `${o.path}: ${rules.jscShapeErrors("requirement", o.obj).slice(0, 2).join("; ")}`);
    assert.ok(!objs.has(o.obj.id), "no id twice: " + o.obj.id);
    objs.set(o.obj.id, { type, obj: o.obj });
  }
  assert.deepEqual(rules.jscClosureErrors(objs), []);
  // every {param:} token of a clause is declared on that clause
  for (const r of objs.values()) for (const st of r.obj.statements || []) {
    const declared = new Set((st.parameters || []).map(p => p.name));
    for (const m of core.jscText(st.prose, "en").matchAll(/\{param:([^}]+)\}/g)) assert.ok(declared.has(m[1]), `${r.obj.id} ${st.id}: ${m[1]}`);
  }
  assert.equal(out.facetSchemas.length, 1, "one pinned schema for the holding facet");
  assert.ok(out.report["props-held"].label === undefined && Object.keys(out.report["props-held"]).length > 0, "props are held and counted");
});

test("profile: NIST MODERATE selects the members of the shipped MODERATE baseline", { skip: missing(NIST_MOD) }, () => {
  const dir = path.join(ROOT, "converted_examples/US.SP800-53/sp800-53-core-bundle"), manifest = json(path.join(dir, "content-manifest.json"));
  const objs = new Map(manifest.objects.map(e => { const o = json(path.join(dir, e.path)); return [o.id, { type: core.jscInferType(o), obj: o }]; }));
  const out = oscal.jscOscalImportProfile(json(NIST_MOD), { ns: "https://org.example", lang: "en", objs });
  const set = out.objects.find(o => o.obj.members).obj, tailoring = out.objects.find(o => o.obj.selects).obj;
  const shipped = objs.get("https://ns.nist.gov/sp800-53/set/baseline/moderate").obj;
  assert.deepEqual(set.members.map(m => m.ref).sort(), shipped.members.map(m => m.ref).sort());
  assert.equal(set.members.length, 287);
  assert.deepEqual(out.report["not-found"], []);
  assert.deepEqual(tailoring.selects, [{ "set-ref": set.id }]);
  assert.ok(Object.keys(out.report["not-carried"]).some(k => k.startsWith("merge")), "the merge directive is reported, not carried");
  for (const o of out.objects) assert.equal(rules.jscMatchTypes(o.obj).length, 1, o.path);
  objs.set(set.id, { type: "requirementSet", obj: set }); objs.set(tailoring.id, { type: "tailoring", obj: tailoring });
  assert.deepEqual(rules.jscClosureErrors(objs), []);
  assert.equal(rules.jscSelection(tailoring, objs).selected.size, 287);
});

test("profile: excludes, parameters inside and outside their declared space, and what is not carried", () => {
  const P = "https://a.example";
  const req = (id, params) => ({ id: `${P}/req/${id}`, version: "1", lifecycle: "active", statements: [{ id: "s1", modality: "must",
    "obligated-parties": [P + "/p"], prose: { en: "X {param:" + (params[0] || { name: "none" }).name + "}." }, ...(params.length ? { parameters: params } : {}) }] });
  const list = [req("AC-1", [{ name: "ac-1_prm_1", type: "string" }]), req("AC-2", [{ name: "ac-2_prm_1", type: "choice", choices: [{ value: "a" }, { value: "b" }] }]), req("AC-3", [])];
  const root = { id: P + "/set/tax/root", version: "1", lifecycle: "active", members: list.map(r => ({ ref: r.id })) };
  const objs = new Map([...list, root].map(o => [o.id, { type: core.jscInferType(o), obj: o }]));
  const profile = { profile: { uuid: "x", metadata: { title: "My Profile", version: "2" },
    imports: [{ href: "#cat", "include-all": {}, "exclude-controls": [{ "with-ids": ["ac-3", "zz-9"] }] }],
    merge: { "as-is": true },
    modify: { "set-parameters": [{ "param-id": "ac-1_prm_1", values: ["90 days"] }, { "param-id": "ac-2_prm_1", values: ["c"] }, { "param-id": "nope", values: ["1"] }],
      alters: [{ "control-id": "ac-1", adds: [{ position: "ending", parts: [] }] }] } } };
  const out = oscal.jscOscalImportProfile(profile, { ns: "https://org.example", lang: "en", objs, catalogSet: root.id });
  assert.equal(out.objects.length, 1, "include-all makes no Set of its own; it selects the catalogue's");
  const t = out.objects[0].obj;
  assert.deepEqual(t.selects, [{ "set-ref": root.id }]);
  assert.deepEqual(t.excludes, [{ ref: P + "/req/AC-3" }]);
  assert.deepEqual(t.operations, [{ op: "set-parameter", "requirement-ref": P + "/req/AC-1", "statement-id": "s1", parameter: "ac-1_prm_1", value: "90 days" }]);
  assert.deepEqual(out.report["not-found"], ["zz-9"]);
  assert.deepEqual(out.report["parameters-not-found"], ["nope"]);
  assert.equal(out.report["parameters-outside-declared-space"].length, 1, "a value outside the choices needs a Deviation and is not written as an operation");
  assert.deepEqual(Object.keys(out.report["not-carried"]).sort(), ["alters with adds", "merge (as-is)"]);
  assert.deepEqual(rules.jscMatchTypes(t), ["tailoring"]);
});

test("the converters' slug: a long name is cut with a hash, never bare", () => {
  assert.equal(oscal.jscOscalSlug("AC-2 (1)"), "ac-2-1");
  const long = "x".repeat(70), s = oscal.jscOscalSlug(long);
  assert.equal(s.length, 60);
  assert.notEqual(s, oscal.jscOscalSlug("x".repeat(71)));
});
