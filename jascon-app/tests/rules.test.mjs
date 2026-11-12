/* Runs the conformance vectors of jascon/conformance/ against
   jascon-rules.js, family by family. All sixteen families are ported. A
   family that is listed in PORTED must pass completely; NOT_PORTED is empty
   and stays as the place to name a family that is not ported yet. The last
   test fails when a vector file appears that is in neither list, so a new
   family cannot go unnoticed. */
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import nodeCrypto from "node:crypto";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const CONF = path.resolve(here, "../../jascon/conformance");
const require = createRequire(import.meta.url);
const core = require("../jascon-core.js");
const rules = require("../jascon-rules.js");
const vectors = name => JSON.parse(fs.readFileSync(path.join(CONF, name + "-vectors.json"), "utf8"));
const asObjs = list => new Map(list.map(o => [o.id, { type: core.jscInferType(o), obj: o }]));

const PORTED = ["attestation", "check", "composition", "conditional", "dsse", "facet", "jcs", "kernel", "lifecycle", "modality", "parameter", "reference", "risk", "scale", "tailoring", "tier"];
const NOT_PORTED = [];
/* Where a vector carries expected-frag (singular), it asserts the wording of
   one Python schema library's diagnostic; the vector files call that
   advisory and expected-rule the portable assertion, and so do these tests.
   expected-frags (plural) are fragments of the validator's own messages,
   which this port keeps, and they are asserted. */

test("modality: every vector", () => {
  const v = vectors("modality").vectors;
  assert.equal(v.length, 21);
  for (const c of v) assert.equal(rules.jscModalityVerdict(c.from, c.to), c.verdict, `${c.from} -> ${c.to}`);
});

test("parameter: every vector", () => {
  const v = vectors("parameter").vectors;
  assert.equal(v.length, 19);
  for (const c of v) assert.equal(rules.jscParamCheck(c.parameter, c.value), c.verdict, c.name);
});

test("tier: the derived tier of every vector (structural mode)", async () => {
  const v = vectors("tier").vectors;
  assert.equal(v.length, 9);
  for (const c of v) {
    // the vectors carry COMPUTE where a live digest belongs, as the Python runner fills it
    const byId = new Map(c.objects.map(o => [o.id, o]));
    for (const o of c.objects) {
      for (const subj of o["subject-semantic-digests"] || []) {
        if (subj && subj["semantic-digest"] === "COMPUTE" && byId.has(subj.id)) {
          subj["semantic-digest"] = await core.jscSemanticDigest(byId.get(subj.id));
        }
      }
    }
    const objs = asObjs(c.objects);
    const tailoring = [...objs.values()].find(r => r.type === "tailoring").obj;
    assert.equal(await rules.jscDeriveTier(tailoring, objs), c["expected-tier"], c.name);
  }
});

test("state machines: the Finding, Deviation and Risk transition vectors", () => {
  const life = vectors("lifecycle");
  for (const c of life["finding-transitions"]) assert.equal(rules.jscCanMove("finding", c.from, c.to), c.valid, `finding ${c.from} -> ${c.to}`);
  for (const c of life["deviation-transitions"]) assert.equal(rules.jscCanMove("deviation", c.from, c.to), c.valid, `deviation ${c.from} -> ${c.to}`);
  const risk = vectors("risk")["risk-transitions"];
  assert.equal(risk.length, 8);
  for (const c of risk) assert.equal(rules.jscCanMove("risk", c.from, c.to), c.valid, `risk ${c.from} -> ${c.to}`);
});

test("relationship composition never claims more than the vectors allow", () => {
  for (const c of vectors("lifecycle")["relationship-composition"]) {
    const got = rules.jscComposeRelationship(c.a, c.b);
    // floor semantics, as in the Python runner: the composed claim is never stronger than expected
    assert.ok(got === c.composed || (c.composed === "supports" && ["supports", "intersects"].includes(got)), `${c.a} + ${c.b}: ${got}`);
  }
});

test("decimal comparison is exact beyond what a float holds", () => {
  assert.equal(rules.jscDecimalCompare("9007199254740993", "9007199254740992"), 1);
  assert.equal(rules.jscDecimalCompare("1.50", "1.5"), 0);
  assert.equal(rules.jscDecimalCompare("-0.5", "0.25"), -1);
  assert.equal(rules.jscDecimalCompare("0.1", "0.09"), 1);
});

test("selection: nested Sets, an excluded Set removes its members, withdrawn is dropped, a predicate opens it", () => {
  const req = (n, lifecycle = "active") => ({ id: "https://a.example/req/" + n, version: "1", lifecycle,
    statements: [{ id: "s1", modality: "must", "obligated-parties": ["https://a.example/p"], prose: { en: "x" } }] });
  const set = (n, refs) => ({ id: "https://a.example/set/" + n, version: "1", lifecycle: "active", members: refs.map(r => ({ ref: r })) });
  const R = n => "https://a.example/req/" + n, S = n => "https://a.example/set/" + n;
  const objs = asObjs([req(1), req(2), req(3), req(4, "withdrawn"),
    set("inner", [R(1), R(2)]), set("other", [R(3), R(4)]), set("root", [S("inner"), S("other")])]);
  const t = { id: "https://b.example/tailoring/t", version: "1", lifecycle: "active",
    selects: [{ "set-ref": S("root") }], excludes: [{ ref: S("inner") }] };
  const a = rules.jscSelection(t, objs);
  assert.deepEqual([...a.selected], [R(3)]);
  assert.equal(a.open, false);
  assert.equal(a.notes.length, 1, "the withdrawn requirement is said so");
  const b = rules.jscSelection({ ...t, excludes: [], selects: [{ "set-ref": S("inner") }, { predicate: { all: [] } }] }, objs);
  assert.equal(b.open, true);
  assert.deepEqual([...b.selected].sort(), [R(1), R(2)]);
});

test("resolving a Tailoring: operations apply to copies, a second operation on one target is an error", () => {
  const base = { id: "https://a.example/req/1", version: "1", lifecycle: "active", statements: [{ id: "s1", modality: "should",
    "obligated-parties": ["https://a.example/p"], prose: { en: "Rotate keys every {param:period}." },
    parameters: [{ name: "period", type: "calendar-period", num: 12, unit: "months", "calendar-ref": "https://a.example/cal" }] }] };
  const set = { id: "https://a.example/set/all", version: "1", lifecycle: "active", members: [{ ref: base.id }] };
  const t = { id: "https://a.example/tailoring/t", version: "1", lifecycle: "active", selects: [{ "set-ref": set.id }], operations: [
    { op: "set-modality", "requirement-ref": base.id, "statement-id": "s1", modality: "must" },
    { op: "set-parameter", "requirement-ref": base.id, "statement-id": "s1", parameter: "period", value: { num: 1, unit: "months" } },
    { op: "set-modality", "requirement-ref": base.id, "statement-id": "s1", modality: "may" },
  ] };
  const r = rules.jscResolveTailoring(t, asObjs([base, set, t]));
  assert.equal(r.errors.length, 1);
  assert.match(r.errors[0], /same-target conflict/);
  const out = r.resolved.get(base.id);
  assert.equal(out.statements[0].modality, "must");
  assert.equal(out.statements[0].parameters[0].num, 1);
  assert.equal(base.statements[0].modality, "should", "the original is untouched");
  assert.equal(r.touched.get(base.id)[0].verdict, "monotone");
});

test("schema matching: each minimal object matches exactly one type, a field-free object none", () => {
  const P = "https://ex.org";
  const minimal = {
    requirement: { id: P + "/r", version: "1", lifecycle: "active", statements: [{ id: "s1", modality: "must", "obligated-parties": [P + "/p"], prose: { en: "X." } }] },
    requirementSet: { id: P + "/s", version: "1", lifecycle: "active", members: [{ ref: P + "/r", sequence: 10 }] },
    tailoring: { id: P + "/t", version: "1", lifecycle: "active", selects: [{ "set-ref": P + "/s" }] },
    mapping: { id: P + "/m", version: "1", lifecycle: "active", "source-ref": P + "/r", "target-ref": P + "/r2", relationship: "supports",
      direction: "source-to-target", confidence: "draft", provenance: { "author-ref": P + "/p", date: "2026-07-21" } },
    component: { id: P + "/c", version: "1", lifecycle: "active", kind: "service" },
    implementation: { id: P + "/i", version: "1", lifecycle: "active", "component-ref": P + "/c", "requirement-ref": P + "/r",
      responsibility: "provider", "satisfied-by": [{ "capability-ref": "cap" }], status: "implemented" },
    assessment: { id: P + "/a", version: "1", lifecycle: "active", "subject-refs": [P + "/r"], method: { kind: "review" },
      "performer-ref": P + "/p", time: "2026-07-21", result: "satisfied" },
    finding: { id: P + "/f", version: "1", lifecycle: "active", "assessment-ref": P + "/a", "requirement-ref": P + "/r", state: "open" },
    attestation: { id: P + "/at", version: "1", lifecycle: "active", "subject-semantic-digests": ["sha256:" + "0".repeat(64)],
      "content-manifest-digest": "sha256:" + "0".repeat(64), signer: P + "/p", timestamp: "2026-07-21" },
    risk: { id: P + "/rk", version: "1", lifecycle: "active", scenario: { en: "X." }, "owner-ref": P + "/p", state: "identified" },
  };
  for (const [want, o] of Object.entries(minimal)) assert.deepEqual(rules.jscMatchTypes(o), [want], want);
  assert.deepEqual(rules.jscMatchTypes({ id: P + "/x", version: "1", lifecycle: "active" }), []);
  // the identity events of the lifecycle family: only a canonical-alias may be substituted
  for (const c of vectors("lifecycle")["identity-events"]) assert.equal(c.record === "canonical-alias", c.substitution === "allowed", c.record);
});

test("schema matching agrees with the type every shipped object was given by its fields", () => {
  const ROOT = path.resolve(CONF, "../..");
  const dir = path.join(ROOT, "converted_examples/US.IFA-GoodRead/ifa-core-bundle/objects");
  const files = fs.readdirSync(dir, { recursive: true }).filter(f => String(f).endsWith(".json"));
  assert.ok(files.length >= 17);
  for (const f of files) {
    const o = JSON.parse(fs.readFileSync(path.join(dir, String(f)), "utf8"));
    assert.equal(rules.jscTypeOf(o), core.jscInferType(o), String(f));
  }
});

test("a schema keyword this checker does not implement is refused, not skipped", () => {
  assert.throws(() => rules.jscSchemaCheck({ dependentRequired: { a: ["b"] } }, { a: 1 }, {}), /dependentRequired is not supported/);
  // the plain bounds a pinned facet schema may use are implemented
  const errs = (schema, v) => rules.jscSchemaCheck(schema, v, {}).errors.map(e => e.keyword);
  assert.deepEqual(errs({ maximum: 3 }, 4), ["maximum"]);
  assert.deepEqual(errs({ maxLength: 3 }, "abcd"), ["maxLength"]);
  assert.deepEqual(errs({ uniqueItems: true, maxItems: 2 }, [1, 1, 2]), ["maxItems", "uniqueItems"]);
  assert.deepEqual(errs({ oneOf: [{ type: "string" }, { minLength: 1 }] }, "a"), ["oneOf"]);
  assert.deepEqual(errs({ not: { type: "string" } }, "a"), ["not"]);
  assert.deepEqual(errs({ oneOf: [{ type: "string" }, { type: "number" }], not: { const: 5 } }, 4), []);
});

test("reference: the number of closure errors of every vector", () => {
  const v = vectors("reference").vectors;
  assert.equal(v.length, 13);
  for (const c of v) assert.equal(rules.jscClosureErrors(rules.jscTypedObjects(c.objects)).length, c["expected-errors"], c.name);
});

test("kernel: the pin rules of every vector", () => {
  const v = vectors("kernel").vectors;
  assert.equal(v.length, 9);
  for (const c of v) {
    const objs = rules.jscTypedObjects(c.objects);
    const errs = rules.jscShapeErrors("contentManifest", c.manifest).length ? ["manifest schema violation"] : rules.jscKernelPinErrors(c.manifest, objs);
    assert.equal(errs.length, c["expected-fails"] || 0, c.name + ": " + errs.join(" | "));
    assert.equal(objs.size, c.objects.length, c.name + ": every object is typed");
    for (const frag of c["expected-frags"] || []) assert.ok(errs.some(e => e.includes(frag)), `${c.name}: ${frag}`);
  }
});

test("risk: object vectors (shape, with the rule named on refusal)", () => {
  const v = vectors("risk")["object-vectors"];
  assert.equal(v.length, 27);
  for (const c of v) {
    const matched = rules.jscMatchTypes(c.object), named = rules.jscRiskRuleViolations(c.object).map(x => x[0]);
    if (c.expected === "valid") {
      assert.deepEqual(matched, ["risk"], c.name);
      assert.deepEqual(named, [], c.name + ": the two layers agree on valid");
    } else {
      assert.deepEqual(matched, [], c.name);
      if (c["expected-rule"]) assert.ok(named.includes(c["expected-rule"]), `${c.name}: names ${c["expected-rule"]}, got ${named}`);
    }
  }
});

test("risk: bundle vectors (closure, typed edges, coverage, RISK-11, notes)", async () => {
  const v = vectors("risk")["bundle-vectors"];
  assert.equal(v.length, 38);
  const keys = o => Object.keys(o || {}).sort();
  for (const c of v) {
    const objs = rules.jscTypedObjects(c.objects);
    const cov = await rules.jscRiskCoverage(objs);
    const errs = [...rules.jscClosureErrors(objs), ...cov.errors], notes = [...cov.notes, ...rules.jscRiskLinkNotes(objs)];
    assert.equal(errs.length, c["expected-fails"] || 0, `${c.name}: ${errs.join(" | ")}`);
    for (const frag of c["expected-frags"] || []) assert.ok(errs.some(e => e.includes(frag)), `${c.name}: error with ${frag}`);
    for (const frag of c["expected-notes"] || []) assert.ok(notes.some(n => n.includes(frag)), `${c.name}: note with ${frag}; got ${notes.join(" | ")}`);
    for (const [tid, want] of Object.entries(c["expected-coverage"] || {})) {
      const got = cov.report.tailorings[tid] || {};
      assert.deepEqual([...(got.uncovered || [])].sort(), [...(want.uncovered || [])].sort(), `${c.name}: uncovered of ${tid}`);
      assert.deepEqual(keys(got.covered), [...(want.covered || [])].sort(), `${c.name}: covered of ${tid}`);
      if ("lapsed" in want) assert.deepEqual(keys(got.lapsed), [...want.lapsed].sort(), `${c.name}: lapsed of ${tid}`);
      if ("pending" in want) assert.deepEqual(keys(got.pending), [...want.pending].sort(), `${c.name}: pending of ${tid}`);
    }
  }
});

test("scale: every vector (definition, matrix, levels, residual, SCALE-4)", () => {
  const v = vectors("scale").vectors;
  assert.equal(v.length, 18);
  for (const c of v) {
    const objs = rules.jscTypedObjects(c.objects);
    assert.equal(objs.size, c.objects.length, c.name + ": every object is typed");
    const r = rules.jscCheckScales(c.scales, objs);
    assert.equal(r.errors.length, c["expected-fails"] || 0, `${c.name}: ${r.errors.join(" | ")}`);
    for (const frag of c["expected-frags"] || []) assert.ok(r.errors.some(e => e.includes(frag)), `${c.name}: error with ${frag}`);
    for (const frag of c["expected-notes"] || []) assert.ok(r.notes.some(n => n.includes(frag)), `${c.name}: note with ${frag}`);
    if (Array.isArray(c["expected-notes"]) && !c["expected-notes"].length) assert.deepEqual(r.notes, [], c.name + ": no note expected");
  }
});

test("the example bundle: its scales, its matrix and its Risk agree, and coverage reports it", async () => {
  const EX = path.resolve(CONF, "../examples");
  const manifest = JSON.parse(fs.readFileSync(path.join(EX, "content-manifest.json"), "utf8"));
  const read = f => JSON.parse(fs.readFileSync(path.join(EX, f), "utf8"));
  const objs = rules.jscTypedObjects(manifest.objects.map(e => read(e.path)));
  assert.equal(objs.size, manifest.objects.length);
  const pins = new Map(manifest.scales.map(p => [p.id, p]));
  const r = rules.jscCheckScales(manifest.scales.map(p => read(p.path)), objs, pins);
  assert.deepEqual(r.errors, []);
  assert.ok([...r.scales.values()].some(sd => sd.matrix), "the level scale carries its matrix");
  assert.deepEqual(rules.jscClosureErrors(objs), []);
  assert.deepEqual(rules.jscKernelPinErrors(manifest, objs), []);
  const cov = await rules.jscRiskCoverage(objs);
  assert.deepEqual(cov.errors, []);
  assert.equal(cov.report.risks, 1);
});

test("jcs: canonical form, and optional containers that must be absent instead of empty", () => {
  const v = vectors("jcs").vectors;
  assert.equal(v.length, 8);
  for (const c of v) {
    if (c.canonical != null) assert.equal(core.jscCanonical(c.input), c.canonical, c.name);
    else assert.equal(rules.jscOptionalEmptyViolations(c["authoring-input"]).length ? "invalid" : "valid", c.expected, c.name);
  }
});

test("facet: every vector (stdlib, pinned, private, unregistered)", () => {
  const v = vectors("facet").vectors;
  assert.equal(v.length, 7);
  for (const c of v) {
    const errs = rules.jscFacetErrors([[c.name, c.object]], new Map(Object.entries(c.pinned || {})));
    assert.equal(errs.length ? "invalid" : "valid", c.expected, `${c.name}: ${errs[0] || ""}`);
  }
});

test("tailoring: the operation law of every vector, through the function the app uses", async () => {
  const v = vectors("tailoring").vectors;
  assert.equal(v.length, 19);
  const A = "https://auth.example", C = "https://consumer.example";
  for (const c of v) {
    /* The vectors state a tier, a base modality and a parameter declaration,
       and name requirements of their own. A small graph is built in which
       jscDeriveTier derives the stated tier: one requirement that has every
       statement the operations name, each with the base modality and the
       declared parameter. Every operation aims at that requirement and
       keeps its own statement, parameter, field and facet, so a same-target
       conflict stays one and distinct targets stay distinct. */
    const decl = c["parameter-decl"], sids = [...new Set(["s1", ...(c.operations || []).map(op => op["statement-id"]).filter(Boolean)])];
    const names = [...new Set((c.operations || []).filter(op => op.op === "set-parameter").map(op => op.parameter || (decl && decl.name)).filter(Boolean))];
    const req = { id: A + "/req/1", version: "1", lifecycle: "active", statements: sids.map(id => ({ id, modality: c["base-modality"] || "must",
      "obligated-parties": [A + "/p"], prose: { en: "X." }, ...(decl && names.length ? { parameters: names.map(name => ({ ...decl, name })) } : {}) })) };
    const set = { id: A + "/set/all", version: "1", lifecycle: "active", members: [{ ref: req.id }] };
    const ops = (c.operations || []).map(op => ({ ...op, "requirement-ref": req.id,
      ...(op["statement-id"] === undefined && ["set-modality", "set-parameter", "replace-prose"].includes(op.op) ? { "statement-id": "s1" } : {}),
      ...(op.op === "set-parameter" && op.parameter === undefined && decl ? { parameter: decl.name } : {}) }));
    const owner = c.tier === "consumer" ? C : A;
    const t = { id: owner + "/tailoring/t", version: "1", lifecycle: "active", selects: [{ "set-ref": set.id }], operations: ops };
    const objs = new Map([[req.id, { type: "requirement", obj: req }], [set.id, { type: "requirementSet", obj: set }], [t.id, { type: "tailoring", obj: t }]]);
    if (c.tier) assert.equal(await rules.jscDeriveTier(t, objs), c.tier === "consumer" ? "consumer" : "authority-claimed", c.name + ": tier of the built graph");
    const errs = await rules.jscTailoringDutyErrors(objs, new Map(Object.entries(c["facet-decls"] || {})));
    assert.equal(errs.length ? "error" : "valid", c.verdict, `${c.name}: ${errs.join(" | ")}`);
  }
});

test("attestation: the bi-modal verdict of every vector", async () => {
  const v = vectors("attestation").vectors;
  assert.equal(v.length, 5);
  const digests = async (obj, indent) => ({ semantic: await core.jscSemanticDigest(obj), package: await core.jscPackageDigest(JSON.stringify(obj, null, indent)) });
  for (const c of v) {
    const sc = c.scenario, delivered = JSON.parse(JSON.stringify(sc["delivered-subject"] || sc.subject));
    if (sc["delivered-mutation"] === "annotation-added") delivered.annotations = { web_name: "chrome" };
    const got = rules.jscAttestationVerdict(await digests(sc.subject, 1), await digests(delivered, sc["delivered-mutation"] === "reindent" ? 4 : 1));
    assert.equal(got, c.expected, c.name);
  }
});

test("one object: the 216 rule, duplicate statement ids, a by-statement key that names nothing, an empty optional list", () => {
  const base = { id: "https://a.example/req/1", version: "1", lifecycle: "active" };
  const st = (id, text, params) => ({ id, modality: "must", "obligated-parties": ["https://a.example/p"], prose: { en: text }, ...(params ? { parameters: params } : {}) });
  const errs = o => rules.jscObjectErrors(o).errors.join(" | ");
  assert.equal(errs({ ...base, statements: [st("s1", "Keep {param:days} days.", [{ name: "days", type: "integer" }])] }), "");
  assert.match(errs({ ...base, statements: [st("s1", "Keep {param:days} days.")] }), /unbound \{param:days\}/);
  assert.match(errs({ ...base, statements: [st("s1", "X."), st("s1", "Y.")] }), /duplicate statement ids/);
  assert.match(errs({ ...base, statements: [st("s1", "X.")], facets: { "private:x@1": { "by-statement": { s9: {} } } } }), /names no statement/);
  assert.match(errs({ ...base, statements: [st("s1", "X.")], relations: [] }), /NO type|optional empty/);
  assert.equal(rules.jscObjectErrors({ ...base }).type, null);
});

test("a whole set: every shipped bundle passes the ported rules, as it passes the reference validator", async () => {
  const ROOT = path.resolve(CONF, "../..");
  const tree = (dir, prefix = "") => fs.readdirSync(dir).sort().flatMap(n => fs.statSync(path.join(dir, n)).isDirectory()
    ? tree(path.join(dir, n), prefix + n + "/") : [{ path: prefix + n, text: core.jscDecode(fs.readFileSync(path.join(dir, n))) }]);
  const base = path.join(ROOT, "converted_examples");
  const bundles = fs.readdirSync(base).flatMap(c => fs.statSync(path.join(base, c)).isDirectory()
    ? fs.readdirSync(path.join(base, c)).filter(d => d.endsWith("-bundle")).map(d => path.join(base, c, d)) : []);
  assert.equal(bundles.length, 5);
  for (const dir of bundles) {
    const g = core.jscGraphFrom(core.jscClassifyFiles(tree(dir)).records);
    const res = await rules.jscCheckGraph(g, await core.jscVerify(g));
    const errors = res.findings.filter(f => f.kind === "error");
    assert.deepEqual(errors.slice(0, 3), [], path.relative(ROOT, dir));
    assert.equal(Object.values(res.types).reduce((a, b) => a + b, 0), g.objects.size, "every object is typed: " + path.relative(ROOT, dir));
  }
});

test("a whole set: the example folder, checked as a bundle, passes as it passes the reference validator; a diverging pin of a stdlib facet fails (D26)", async () => {
  const EX = path.resolve(CONF, "../examples");
  /* the folder holds an evidence store in a subfolder (CP-CHECK-1), so it is read as a tree */
  const tree = (dir, prefix = "") => fs.readdirSync(dir).sort().flatMap(n => fs.statSync(path.join(dir, n)).isDirectory()
    ? tree(path.join(dir, n), prefix + n + "/") : [{ path: prefix + n, text: core.jscDecode(fs.readFileSync(path.join(dir, n))) }]);
  const files = tree(EX);
  const g = core.jscGraphFrom(core.jscClassifyFiles(files).records);
  const errorsOf = async () => (await rules.jscCheckGraph(g, await core.jscVerify(g))).findings.filter(f => f.kind === "error").map(f => f.message);
  assert.deepEqual(await errorsOf(), []);
  /* The folder pins the stdlib facet assessment-criteria. A pin of a stdlib id must be the normative descriptor
     verbatim; the same pin with one more property in its schema is the error the folder itself once carried. */
  const pin = g.facetSchemas.find(f => f.def.id === "https://ns.jascon.net/stdlib/facet/assessment-criteria");
  assert.ok(pin, "the example folder pins a stdlib facet");
  pin.def = { ...pin.def, schema: { ...pin.def.schema, properties: { ...pin.def.schema.properties, extra: { type: "string" } } } };
  const errors = await errorsOf();
  assert.equal(errors.length, 1, errors.join(" | "));
  assert.match(errors[0], /DIVERGES from the normative descriptor \(D26\)/);
});

test("composition: every vector, as the reference runner judges it", () => {
  const v = vectors("composition").vectors;
  assert.equal(v.length, 7);
  for (const c of v) {
    const side = x => [(x.objects || []).map(o => [o.id, o]), x.pins || {}];
    const { resolutions, errors } = rules.jscCompose(...side(c.a), ...side(c.b));
    const want = c["expected-errors"] || [];
    assert.equal(errors.length, want.length, `${c.name}: ${errors.join(" | ")}`);
    for (const frag of want) assert.ok(errors.some(e => e.includes(frag)), `${c.name}: ${frag}`);
    for (const [fid, ver] of Object.entries(c["expected-resolutions"] || {})) assert.equal(resolutions[fid], ver, `${c.name}: ${fid}`);
    /* which bundle is called A must not matter to what is resolved or to how much is reported */
    const swapped = rules.jscCompose(...side(c.b), ...side(c.a));
    assert.deepEqual(swapped.resolutions, resolutions, c.name + ": the same resolutions with the sides swapped");
    assert.equal(swapped.errors.length, errors.length, c.name + ": as many errors with the sides swapped");
  }
});

test("conditional: every vector, with the normative text of a failure", () => {
  const v = vectors("conditional").vectors;
  assert.equal(v.length, 8);
  for (const c of v) {
    const errs = rules.jscConditionalApply(c.instance, asObjs(c.objects));
    assert.equal(errs.length, c["expected-fails"] || 0, `${c.name}: ${errs.join(" | ")}`);
    for (const frag of c["expected-frags"] || []) assert.ok(errs.some(e => e.includes(frag)), `${c.name}: ${frag}`);
  }
});

test("dsse: the verdict on every envelope and the tier in verification mode", async () => {
  const v = vectors("dsse").vectors;
  assert.equal(v.length, 5);
  for (const c of v) {
    const objs = asObjs(c.objects), envs = c.envelopes || {}, trusted = c["trusted-keys"] || {};
    const att = [...objs.values()].find(r => r.type === "attestation").obj, env = envs[att["envelope-ref"]];
    const res = att["envelope-ref"] && env !== undefined ? await rules.jscVerifyEnvelope(env, att, trusted) : { status: "absent", detail: "" };
    const want = c["expected-envelope"];
    if (want !== undefined) {
      const [status, frag] = want.includes(":") ? [want.slice(0, want.indexOf(":")), want.slice(want.indexOf(":") + 1)] : [want, ""];
      assert.equal(res.status, status, c.name);
      assert.ok(res.detail.includes(frag), `${c.name}: ${res.detail}`);
    }
    const t = [...objs.values()].find(r => r.type === "tailoring");
    if (c["expected-tier"] !== undefined) assert.equal(await rules.jscDeriveTier(t.obj, objs, { envelopes: new Map(Object.entries(envs)), trusted }), c["expected-tier"], c.name);
  }
});

test("Ed25519: the two first test vectors of RFC 8032, and agreement with the platform's implementation", async () => {
  const hex = h => Uint8Array.from(h.match(/../g) || [], x => parseInt(x, 16));
  const rfc = [
    ["d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a", "",
      "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e065224901555fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b"],
    ["3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c", "72",
      "92a009a9f0d4cab8720e820b5f642540a2b27b5416503f8fb3762223ebdb69da085ac1e43e15996e458f3613d0f11d8c387b2eaeb4302aeeb00d291612bb0c00"],
  ];
  for (const [pub, msg, sig] of rfc) {
    assert.equal(await rules.jscEd25519Verify(hex(pub), hex(msg), hex(sig)), true, "RFC 8032 vector for " + pub.slice(0, 8));
    assert.equal(await rules.jscEd25519Verify(hex(pub), hex(msg + "00"), hex(sig)), false, "another message does not verify");
  }
  for (let i = 0; i < 12; i++) {
    const { publicKey, privateKey } = nodeCrypto.generateKeyPairSync("ed25519");
    const pub = new Uint8Array(publicKey.export({ format: "der", type: "spki" }).subarray(-32));
    const msg = new Uint8Array(nodeCrypto.randomBytes(1 + i * 37)), sig = new Uint8Array(nodeCrypto.sign(null, msg, privateKey));
    assert.equal(await rules.jscEd25519Verify(pub, msg, sig), true, "a platform signature verifies, round " + i);
    const bad = sig.slice(); bad[i % 64] ^= 1;
    assert.equal(await rules.jscEd25519Verify(pub, msg, bad), nodeCrypto.verify(null, msg, publicKey, bad), "a flipped bit is judged as the platform judges it, round " + i);
    assert.equal(await rules.jscEd25519Verify(pub, msg.slice(1), sig), false);
  }
  assert.equal(await rules.jscEd25519Verify(new Uint8Array(31), new Uint8Array(1), new Uint8Array(64)), false, "a key of the wrong length");
});

test("a whole set: a signed attestation is verified with a trusted key, unverified without one, an error under a wrong one", async () => {
  const c = vectors("dsse").vectors.find(x => x.name === "signed-envelope-proves-in-verification-mode");
  const att = c.objects.find(o => o["envelope-ref"]), tid = c.objects.find(o => o.operations).id;
  const files = [...c.objects.map((o, i) => ({ path: `o${i}.json`, text: core.jscSerialize(o) })),
    { path: att["envelope-ref"], text: JSON.stringify(c.envelopes[att["envelope-ref"]]) }];
  const g = core.jscGraphFrom(core.jscClassifyFiles(files).records);
  assert.equal(g.aux.length, 1, "the envelope is kept beside the objects under the name the attestation gives");
  const sig = async opts => { const r = await rules.jscCheckGraph(g, null, opts); return { status: r.signatures[att.id], tier: r.tiers[tid], errors: r.findings.filter(f => f.kind === "error" && f.area === "signature").map(f => f.message) }; };
  assert.deepEqual(await sig({ trusted: c["trusted-keys"] }), { status: "verified", tier: "authority-proven", errors: [] });
  assert.deepEqual(await sig(), { status: "unverified", tier: "authority-proven", errors: [] }, "without keys the digest match stands and the signature is unverified");
  const wrong = await sig({ trusted: { [att.signer]: "00".repeat(32) } });
  assert.equal(wrong.status, "error");
  assert.equal(wrong.tier, "consumer", "a signature that does not verify proves nothing");
  assert.match(wrong.errors[0], /no signature verifies under the trusted key/);
  /* without the envelope file: the attestation is not listed in a manifest here, so the reference would not look and this is a note */
  const g2 = core.jscGraphFrom(core.jscClassifyFiles(files.slice(0, -1)).records), r2 = await rules.jscCheckGraph(g2, null, { trusted: c["trusted-keys"] });
  assert.equal(r2.signatures[att.id], "missing");
  assert.equal(r2.tiers[tid], "consumer");
  assert.deepEqual(r2.findings.filter(f => f.kind === "error" && f.area === "signature"), []);
});

/* CP-CHECK-1. The bundle vectors name the exact set of CHECK rules a
   conformant tool reports; `store` is the evidence store as text. */
test("check: I-Regexp - what must and must not match whole-value, and what every implementation refuses", () => {
  for (const c of vectors("check")["regex-vectors"]) {
    let valid = true, why = "";
    try { rules.jscIreCompile(c.pattern); } catch (e) { if (!(e instanceof rules.JscIRegexpError)) throw e; valid = false; why = e.message; }
    assert.equal(valid, c.valid, `${JSON.stringify(c.pattern)}: ${why}`);
    for (const t of c.match || []) assert.ok(rules.jscIreFullMatch(c.pattern, t), `${JSON.stringify(c.pattern)} matches ${JSON.stringify(t)}`);
    for (const t of c["no-match"] || []) assert.ok(!rules.jscIreFullMatch(c.pattern, t), `${JSON.stringify(c.pattern)} does not match ${JSON.stringify(t)}`);
  }
});
test("check: check-verdict over every verdict vector, and the aggregate", () => {
  const v = vectors("check");
  for (const c of v["verdict-vectors"]) {
    const [got, why] = rules.jscCheckVerdict(c.check, c.observation, c.parameters);
    assert.equal(got, c.expected, `${c.name}: ${why.join("; ")}`);
    if (c["expected-resources"]) {   // a per-resource check: every resource is evaluated and counted
      const { results, ...counts } = rules.jscCheckEach(c.check, c.observation, c.parameters);
      assert.deepEqual(counts, c["expected-resources"], c.name);
      assert.equal(results.length, c.observation.resources.length, c.name);
    }
  }
  for (const c of v["aggregate-vectors"]) assert.equal(rules.jscCheckAggregate(c.outcomes), c.expected, JSON.stringify(c.outcomes));
  for (const c of v["share-vectors"]) assert.equal(rules.jscPercentShare(c.part, c.whole), c.expected, `${c.part} of ${c.whole}`);
});
test("check: closed shapes - each object vector matches exactly its type, or none", () => {
  for (const c of vectors("check")["object-vectors"]) {
    assert.deepEqual(rules.jscMatchTypes(c.object), c.expected === "valid" ? [c.type] : [], c.name);
  }
});
test("check: the CHECK rules every bundle vector names, the evidence chain included", async () => {
  for (const c of vectors("check")["bundle-vectors"]) {
    const objs = rules.jscTypedObjects(c.objects);
    assert.equal(objs.size, c.objects.length, `${c.name}: every object is typed`);
    const store = c.store ? new Map(Object.entries(c.store)) : null;
    const res = await rules.jscCheckErrors(objs, store ? ref => (store.has(ref) ? store.get(ref) : null) : null);
    assert.deepEqual([...new Set(res.errors.map(([r]) => r))].sort(), [...new Set(c["expected-rules"])].sort(),
      `${c.name}: ${res.errors.map(([, m]) => m).join(" | ")}`);
    for (const frag of c["expected-notes"] || []) assert.ok(res.notes.some(n => n.includes(frag)), `${c.name}: a note with "${frag}"`);
  }
});

test("every vector family is either ported or named as not ported", () => {
  const families = fs.readdirSync(CONF).filter(f => f.endsWith("-vectors.json")).map(f => f.replace("-vectors.json", "")).sort();
  assert.deepEqual(families, [...PORTED, ...NOT_PORTED].sort());
});

/* ERRATA 2026-11-11: a Risk or a Check written in the app into a set whose
   manifest pins no kernel was reported as a KERNEL-1 error, although the
   export writes the pin. What the set came with is held to KERNEL-1; what
   the app wrote is a note until the export. */
test("a whole set: content written in the app needs no pin before the export; imported content does", async () => {
  const P = "https://ex.org";
  const req = { id: P + "/r", version: "1", lifecycle: "active", statements: [{ id: "s1", modality: "must", "obligated-parties": [P + "/p"], prose: { en: "X." } }] };
  const check = { id: P + "/ck", version: "1", lifecycle: "draft", "requirement-ref": P + "/r", platform: P + "/pl",
    observes: [{ name: "x", type: "integer" }], criteria: [{ fact: "x", op: "at-most", expected: 4 }], confidence: "draft", provenance: { "author-ref": P + "/p", date: "2026-11-11" } };
  const files = [{ path: "content-manifest.json", text: JSON.stringify({ "manifest-version": "1", objects: [] }) }, { path: "objects/r.json", text: JSON.stringify(req) }];
  const g = core.jscGraphFrom(core.jscClassifyFiles(files).records);
  g.objects.set(check.id, { obj: check, type: "check", path: "objects/check/ck.json", text: JSON.stringify(check), origin: "authored", entry: null });
  const res = await rules.jscCheckGraph(g, null);
  assert.deepEqual(res.findings.filter(f => f.area === "manifest" && f.kind === "error").map(f => f.message), []);
  assert.ok(res.findings.some(f => f.area === "manifest" && f.kind === "note" && /the export writes kernel-version/.test(f.message)));
  g.objects.get(check.id).origin = "imported";
  const res2 = await rules.jscCheckGraph(g, null);
  assert.ok(res2.findings.some(f => f.area === "manifest" && f.kind === "error" && /KERNEL-1/.test(f.message)), "the same Check, imported, needs the pin");
});
