/* The OSCAL import against what the repository ships.

   - BSI preset: every object the import makes from the Anwenderkatalog
     Grundschutz++ has the semantic digest the shipped bundle's manifest
     states for it, and the pinned facet schemas are the same.
   - Generic rules on NIST SP 800-53: every object is a valid kernel object
     and every reference closes.
   - NIST preset: the objects of the shipped SP 800-53 bundle by semantic
     digest, and the rules on a small catalog written for the test (this one
     needs no source file).
   - Profile import: the NIST MODERATE profile, imported into the shipped
     SP 800-53 bundle, selects exactly the members of the bundle's own
     MODERATE baseline Set.

   The tests against shipped bundles need the publishers' source files,
   which the repository does not carry (sources/ is ignored). Without them
   they are skipped; the two tests on hand-made input always run; the
   readme says where the files come from. The CIS preset is compared with
   its converter on a catalog written for the test (needs python3). */
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { cisSynthetic } from "./cis-synthetic.mjs";
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
  assert.equal(oscal.jscOscalGuessPreset(src), "nist-sp800-53", "the catalog has a preset of its own; the generic rules are run here on purpose");
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

/* ---------- NIST SP 800-53 preset ---------- */
test("NIST preset: the objects of the shipped SP 800-53 bundle, by semantic digest", { skip: missing(NIST_SRC) }, async () => {
  const dir = path.join(ROOT, "converted_examples/US.SP800-53/sp800-53-core-bundle"), manifest = json(path.join(dir, "content-manifest.json"));
  const src = json(NIST_SRC);
  assert.equal(oscal.jscOscalGuessPreset(src), "nist-sp800-53");
  const out = oscal.jscOscalImportCatalog(src, { preset: "nist-sp800-53" });
  const want = new Map(manifest.objects.map(e => [e.path, e]));
  /* the baselines are profiles; the preset makes no Set for them */
  assert.deepEqual(out.objects.map(o => o.path).sort(), [...want.keys()].filter(p => !/\/baseline-/.test(p)).sort(), "the same files, without the baseline Sets");
  const differ = [];
  for (const o of out.objects) if (await core.jscSemanticDigest(o.obj) !== want.get(o.path)["semantic-digest"]) differ.push(o.path);
  /* NIST republished its 5.2.0 file after the shipped bundle was converted (the statement of SA-15(13), objectives of
     SA-24, labels of SI-2(7), one back-matter resource). From the file the bundle was converted from, nothing may
     differ; from the later file, only those four objects may. */
  const sameFile = src.catalog.metadata["oscal-version"] === manifest.provenance["source-oscal-version"];
  const changedBySource = ["objects/req/sa-15-13.json", "objects/req/sa-24.json", "objects/req/si-2-7.json", "objects/set/root.json"];
  assert.deepEqual(differ.filter(p => sameFile || !changedBySource.includes(p)), [], "objects that differ from the shipped bundle");
  assert.equal(out.objects.length, 1035);
  assert.equal(out.report["withdrawn-not-converted"], 182);
  const pins = new Map(manifest["facet-schemas"].map(e => [e.path, json(path.join(dir, e.path))]));
  assert.deepEqual(out.facetSchemas.map(f => f.path).sort(), [...pins.keys()].sort());
  for (const f of out.facetSchemas) assert.equal(core.jscCanonical(f.def), core.jscCanonical(pins.get(f.path)), f.path);
});

test("NIST preset: the rules on a small catalog", () => {
  const P = "https://ns.nist.gov/sp800-53", rmf = "http://csrc.nist.gov/ns/rmf";
  const label = (v, cls) => ({ name: "label", value: v, ...(cls ? { class: cls } : {}) });
  const cat = { catalog: { metadata: { title: "Electronic (OSCAL) Version of NIST SP 800-53 Rev 5 test", version: "9.9", "oscal-version": "1.1.2" },
    "back-matter": { resources: [{ uuid: "u1", title: "Zeta", rlinks: [{ href: "https://example.org/zeta" }] }, { uuid: "u2", title: "Alpha", citation: { text: "Alpha, 2020." } }] },
    groups: [{ id: "ac", title: "Access Control", parts: [{ name: "overview", prose: "About access." }], controls: [
      { id: "ac-1", title: "Policy", props: [label("AC-1"), label("AC-01", "sp800-53a"), { name: "sort-id", value: "ac-01" }, { name: "implementation-level", ns: rmf, value: "system" }],
        params: [{ id: "ac-1_prm_1", label: "frequency" }, { id: "ac-1_prm_2", select: { "how-many": "one-or-more", choice: ["daily", "per {{ insert: param, ac-1_prm_1 }}"] } }, { id: "ac-1_prm_3", props: [{ name: "alt-identifier", value: "old-3" }] }],
        links: [{ rel: "related", href: "#ac-2" }, { rel: "related", href: "#ac-2" }, { rel: "related", href: "#ac-9" }, { rel: "reference", href: "#u1" }, { rel: "reference", href: "#u2" }],
        parts: [{ id: "ac-1_smt", name: "statement", parts: [
            { id: "ac-1_smt.a", name: "item", prose: "Review every {{ insert: param, ac-1_prm_1 }} as [SP 800-12](#u1) says." },
            { id: "ac-1_smt.b", name: "item", prose: "Use {{ insert: param, ac-2_prm_1 }}." }] },
          { name: "guidance", prose: "See [AC-2](#ac-2)." },
          { id: "ac-1_obj", name: "assessment-objective", props: [label("AC-01", "sp800-53a")], parts: [{ id: "ac-1_obj.a", name: "assessment-objective", prose: "the review happens;" }] },
          { name: "assessment-method", props: [{ name: "method", value: "EXAMINE" }, label("AC-01-Examine", "sp800-53a")], parts: [{ name: "assessment-objects", prose: "Policy\n\nProcedures" }] }],
        controls: [{ id: "ac-1.1", title: "Enhancement", props: [label("AC-1(1)"), { name: "sort-id", value: "ac-01.01" }], parts: [{ id: "ac-1.1_smt", name: "statement", prose: "Do more." }] }] },
      { id: "ac-2", title: "Accounts", props: [label("AC-2"), { name: "sort-id", value: "ac-02" }], params: [{ id: "ac-2_prm_1" }], parts: [{ id: "ac-2_smt", name: "statement", prose: "Manage {{ insert: param, ac-2_prm_1 }}." }] },
      { id: "ac-9", title: "Old", props: [label("AC-9"), { name: "status", value: "withdrawn" }], links: [{ rel: "incorporated-into", href: "#ac-2_smt.a" }] },
      { id: "ac-8", title: "Moved", props: [label("AC-8"), { name: "status", value: "withdrawn" }], links: [{ rel: "moved-to", href: "#ac" }] }] }] } };
  const out = oscal.jscOscalImportCatalog(cat, { preset: "nist-sp800-53" });
  const by = new Map(out.objects.map(o => [o.obj.id, o.obj]));
  assert.deepEqual([...by.keys()], [`${P}/req/AC-1`, `${P}/req/AC-1.1`, `${P}/req/AC-2`, `${P}/set/family/ac`, `${P}/set/root`], "withdrawn controls make no Requirement");
  const ac1 = by.get(`${P}/req/AC-1`), ac2 = by.get(`${P}/req/AC-2`), fam = by.get(`${P}/set/family/ac`), root = by.get(`${P}/set/root`);
  assert.deepEqual(ac1.statements.map(s => s.id), ["smt.a", "smt.b"], "items with prose are the clauses, ids without the control prefix");
  assert.equal(ac1.statements[0].prose.en, "Review every {param:ac-1_prm_1} as SP 800-12 says.", "inserts become tokens, anchor links their text");
  assert.deepEqual(ac1.statements[0]["obligated-parties"], [`${P}/party/system`]);
  assert.deepEqual(ac2.statements[0]["obligated-parties"], [`${P}/party/organization`], "the default party");
  assert.ok(ac1.statements.every(s => s.modality === "must"));
  /* declared where inserted; what no clause inserts goes to the first clause, sorted; a parameter of another control is declared where it is used */
  assert.deepEqual(ac1.statements[0].parameters, [{ name: "ac-1_prm_1", type: "string", label: "frequency" },
    { name: "ac-1_prm_2", type: "choice", choices: [{ value: "daily" }, { value: "per {param:ac-1_prm_1}" }], cardinality: "many" }, { name: "ac-1_prm_3", type: "string" }]);
  assert.deepEqual(ac1.statements[1].parameters, [{ name: "ac-2_prm_1", type: "string" }]);
  assert.deepEqual(out.report["parameters-from-another-control"], [["ac-1", "ac-2_prm_1"]]);
  assert.equal(out.report["parameters-without-insertion"], 2);
  assert.deepEqual(ac1.relations, [{ type: "related", ref: `${P}/req/AC-2` }, { type: "reference", ref: "https://example.org/zeta" }], "once each; a link to a withdrawn control and a reference without a URL are dropped and counted");
  assert.equal(out.report["related-to-withdrawn-or-missing"], 1);
  assert.equal(out.report["references-unresolved"], 1);
  assert.deepEqual(ac1.facets[`${P}/facet/narrative@1`], { guidance: [{ en: "See AC-2." }] });
  assert.deepEqual(ac1.facets[`${P}/facet/sp800-53a@1`], { objectives: [{ id: "ac-1_obj", label: "AC-01", children: [{ id: "ac-1_obj.a", prose: { en: "the review happens;" } }] }],
    methods: [{ method: "EXAMINE", label: "AC-01-Examine", objects: [{ en: "Policy" }, { en: "Procedures" }] }] });
  assert.deepEqual(ac1.facets[`${P}/facet/odp@1`], { params: { "ac-1_prm_3": { "alt-identifiers": ["old-3"] } } });
  /* lineage: the successor names the withdrawn control, a family names what moved to it */
  assert.deepEqual(ac2.replaces, [{ ref: `${P}/req/AC-9`, mode: "merged-into" }]);
  assert.deepEqual(ac2.annotations["nist-withdrawal"], [{ ref: `${P}/req/AC-9`, mode: "merged-into", label: "AC-9", title: "Old", into: "smt.a" }]);
  assert.deepEqual(fam.replaces, [{ ref: `${P}/req/AC-8`, mode: "renamed" }]);
  assert.deepEqual(fam.members, [{ ref: `${P}/req/AC-1`, sequence: 10 }, { ref: `${P}/req/AC-1.1`, sequence: 20 }, { ref: `${P}/req/AC-2`, sequence: 30 }], "members in the order of sort-id");
  assert.deepEqual(fam.facets[`${P}/facet/narrative@1`], { guidance: [{ en: "About access." }] });
  assert.deepEqual(root.facets[`${P}/facet/references@1`].resources, [{ title: "Alpha", citation: "Alpha, 2020." }, { title: "Zeta", url: "https://example.org/zeta" }], "resources by title, empty fields left out");
  assert.equal(out.report["withdrawn-not-converted"], 2);
  /* what comes out is valid kernel content: every object one type, references closed, facets under the pinned schemas */
  const objs = new Map();
  for (const o of out.objects) { const type = rules.jscTypeOf(o.obj); assert.ok(type, `${o.path}: ${rules.jscObjectErrors(o.obj).errors.join("; ")}`); objs.set(o.obj.id, { type, obj: o.obj }); }
  assert.deepEqual(rules.jscClosureErrors(objs), []);
  assert.deepEqual(rules.jscFacetErrors(out.objects.map(o => [o.obj.id, o.obj]), new Map(out.facetSchemas.map(f => [f.def.id, f.def.schema]))), []);
});

/* CIS preset. The catalog (tests/cis-synthetic.mjs) is written in the shape
   of the CIS OSCAL export; its text is invented. The Python converter is run
   on it in a throwaway copy of the scripts, and every object the preset makes
   must carry the semantic digest the converter's manifest states. */
const python = spawnSync("python3", ["--version"]).status === 0;
test("CIS preset: on a catalog of the benchmark's shape, every object has the semantic digest of convert_cis_benchmark.py", { skip: !python && "python3 is not installed" }, async () => {
  const src = cisSynthetic();
  assert.equal(oscal.jscOscalGuessPreset(src), "cis-benchmark");
  /* the converter reads fixed paths relative to its own folder: give it a tree of its own */
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "jascon-cis-"));
  try {
    fs.mkdirSync(path.join(tmp, "jascon/scripts"), { recursive: true });
    fs.mkdirSync(path.join(tmp, "sources"));
    for (const f of ["convert_cis_benchmark.py", "oscal_conv_lib.py"]) fs.copyFileSync(path.join(ROOT, "jascon/scripts", f), path.join(tmp, "jascon/scripts", f));
    fs.cpSync(path.join(ROOT, "jascon/schemas"), path.join(tmp, "jascon/schemas"), { recursive: true });
    fs.writeFileSync(path.join(tmp, "sources/CIS Ubuntu Linux 24.04 LTS Benchmark.json"), JSON.stringify(src));
    const run = spawnSync("python3", [path.join(tmp, "jascon/scripts/convert_cis_benchmark.py")], { cwd: tmp, encoding: "utf8" });
    assert.equal(run.status, 0, run.stderr);
    const dir = path.join(tmp, "converted_examples/CIS.Ubuntu2404/cisb-core-bundle"), manifest = json(path.join(dir, "content-manifest.json"));
    const out = oscal.jscOscalImportCatalog(src, { preset: "cis-benchmark" });
    const want = new Map(manifest.objects.map(e => [e.path, e]));
    assert.deepEqual(out.objects.map(o => o.path).sort(), [...want.keys()].sort(), "the same files");
    for (const o of out.objects) {
      assert.equal(o.obj.id, want.get(o.path).id, o.path);
      assert.equal(await core.jscSemanticDigest(o.obj), want.get(o.path)["semantic-digest"], o.path + " has the converter's meaning");
    }
    assert.deepEqual(out.facetSchemas.map(f => f.path).sort(), manifest["facet-schemas"].map(e => e.path).sort());
    for (const f of out.facetSchemas) assert.deepEqual(f.def, json(path.join(dir, f.path)), f.path);
    /* and the report counts what the converter counts */
    assert.deepEqual(out.report.methods, { automated: 3, manual: 2 });
    assert.deepEqual(out.report.mappings, { v7: 1, v8: 3 });
    assert.equal(out.report["unresolved-links"], 2);
    assert.deepEqual(out.report.profiles, { "Level 1 - Server": 2, "Level 2   Workstation": 2 }, "a backslash in a profile title becomes a space, as in the converter");
    const objs = rules.jscTypedObjects(out.objects.map(o => o.obj));
    assert.equal(objs.size, out.objects.length, "every object is one kernel type");
  } finally { fs.rmSync(tmp, { recursive: true, force: true }); }
});
test("CIS preset: the namespace is the converter's for its benchmark and derived from the title for any other", () => {
  assert.equal(oscal.jscCisNamespace({ metadata: { title: "CIS Ubuntu Linux 24.04 LTS Benchmark" } }), "https://ns.cisecurity.org/benchmark/ubuntu-24.04-lts");
  assert.equal(oscal.jscCisNamespace({ metadata: { title: "CIS Red Hat Enterprise Linux 9 Benchmark v2.0.0" } }), "https://ns.cisecurity.org/benchmark/red-hat-enterprise-linux-9");
  const own = oscal.jscOscalImportCatalog(cisSynthetic(), { preset: "cis-benchmark", ns: "https://example.org/cis" });
  assert.ok(own.objects.every(o => o.obj.id.startsWith("https://example.org/cis/")), "a namespace chosen on the page is used");
});
