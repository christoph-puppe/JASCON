/* Runs the conformance vectors of jascon/conformance/ against
   jascon-rules.js, family by family, as far as the rules are ported. A family
   that is listed here must pass completely; a family that is not ported yet
   is named in NOT_PORTED, and the last test fails when a vector file appears
   that is in neither list, so a new family cannot go unnoticed. */
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const CONF = path.resolve(here, "../../jascon/conformance");
const require = createRequire(import.meta.url);
const core = require("../jascon-core.js");
const rules = require("../jascon-rules.js");
const vectors = name => JSON.parse(fs.readFileSync(path.join(CONF, name + "-vectors.json"), "utf8"));
const asObjs = list => new Map(list.map(o => [o.id, { type: core.jscInferType(o), obj: o }]));

const PORTED = ["jcs", "kernel", "lifecycle", "modality", "parameter", "reference", "risk", "scale", "tier"];
const NOT_PORTED = ["attestation", "composition", "conditional", "dsse", "facet", "tailoring"];
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
  assert.throws(() => rules.jscSchemaCheck({ maxLength: 3 }, "abcd", {}), /maxLength is not supported/);
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

test("every vector family is either ported or named as not ported", () => {
  const families = fs.readdirSync(CONF).filter(f => f.endsWith("-vectors.json")).map(f => f.replace("-vectors.json", "")).sort();
  assert.deepEqual(families, [...PORTED, ...NOT_PORTED].sort());
});
