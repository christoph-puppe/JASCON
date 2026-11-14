/* Runs the conformance vectors of jascon/conformance/ against
   jascon-rules.js, family by family. All eighteen families are ported. A
   family that is listed in PORTED must pass completely; NOT_PORTED names the families the app does not implement (today: none)
   and stays as the place to name a family that is not ported yet. The last
   test fails when a vector file appears that is in neither list, so a new
   family cannot go unnoticed. */
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import nodeCrypto from "node:crypto";
import { spawnSync } from "node:child_process";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const CONF = path.resolve(here, "../../jascon/conformance");
const require = createRequire(import.meta.url);
const core = require("../jascon-core.js");
const rules = require("../jascon-rules.js");
const vectors = name => JSON.parse(fs.readFileSync(path.join(CONF, name + "-vectors.json"), "utf8"));
const asObjs = list => new Map(list.map(o => [o.id, { type: core.jscInferType(o), obj: o }]));

const PORTED = ["advice", "attestation", "author", "check", "composition", "conditional", "dsse", "facet", "jcs", "kernel", "lifecycle", "modality", "parameter", "reference", "risk", "scale", "tailoring", "tier"];
const NOT_PORTED = [];   // every family of jascon/conformance/ is ported today
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
  assert.equal(v.length, 22);   // 22nd: a decimal that ends in a line break (#68)
  for (const c of v) assert.equal(rules.jscParamCheck(c.parameter, c.value), c.verdict, c.name);
});

test("tier: the derived tier of every vector (structural mode)", async () => {
  const v = vectors("tier").vectors;
  assert.equal(v.length, 10);
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
  assert.ok(files.length >= 16);   // 16 since 2026-11-13: the Attestation lies beside the manifest, not under objects/ (D3.1, backlog #46)
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
  assert.equal(v.length, 18);
  for (const c of v) assert.equal(rules.jscClosureErrors(rules.jscTypedObjects(c.objects)).length, c["expected-errors"], c.name);
});

test("kernel: the pin rules of every vector", () => {
  const v = vectors("kernel").vectors;
  assert.equal(v.length, 19);   // was 11: seven more with CP-AUTHOR-1 (provenance, a Deviation's decided and review-due, an authorization's date); the 19th is a pin that ends in a line break (#68)
  for (const c of v) {
    const objs = rules.jscTypedObjects(c.objects);
    const errs = rules.jscShapeErrors("contentManifest", c.manifest).length ? ["manifest schema violation"] : rules.jscKernelPinErrors(c.manifest, objs);
    assert.equal(errs.length, c["expected-fails"] || 0, c.name + ": " + errs.join(" | "));
    assert.equal(objs.size, c.objects.length, c.name + ": every object is typed");
    for (const frag of c["expected-frags"] || []) assert.ok(errs.some(e => e.includes(frag)), `${c.name}: ${frag}`);
  }
});

/* The closed shapes of fields that 2.0.0 typed or added (Finding.actions[].due,
   Deviation.opened, Component.product-version, and with CP-AUTHOR-1 the
   closed `provenance`, a Deviation's `decided` and `review-due`, the date of
   an authorization and the three times any string satisfied until then).
   The schema says valid or invalid; an invalid one names exactly the rules
   of its `expected-rules`, DATE-1 to DATE-5, as the Python runner
   (run_kernel) asserts it - and no rule where the vector names none. */
test("kernel: the shape vectors of the typed fields, with DATE-1 to DATE-5 named on refusal", () => {
  const v = vectors("kernel")["shape-vectors"];
  assert.equal(v.length, 52);   // 16 more with #68: values that end in a line break, a relation type with a line terminator, and their valid twins
  assert.deepEqual([...new Set(v.flatMap(c => c["expected-rules"] || []))].sort(), ["DATE-1", "DATE-2", "DATE-3", "DATE-4", "DATE-5"], "every DATE rule has a vector that names it");
  for (const c of v) {
    const matched = rules.jscMatchTypes(c.document);
    assert.equal(matched.length === 1 && matched[0] === c.kind ? "valid" : "invalid", c.expected, c.name);
    assert.deepEqual([...new Set(rules.jscDateRuleViolations(c.document).map(x => x[0]))].sort(), [...(c["expected-rules"] || [])].sort(), c.name);
    /* the message of the object check carries the rule and its why */
    for (const rule of c["expected-rules"] || []) assert.ok(rules.jscObjectErrors(c.document).errors.join(" ").includes(`[${rule}]`), `${c.name}: ${rule} in the message`);
  }
  const msg = rules.jscObjectErrors({ id: "https://ex.org/f", version: "1", lifecycle: "active", "assessment-ref": "https://ex.org/a", "requirement-ref": "https://ex.org/r", state: "open",
    deviations: [{ id: "d1", type: "risk-adjustment", rationale: { en: "x" }, state: "pending", "approver-ref": "https://ex.org/p", opened: "next week" }] }).errors[0];
  assert.match(msg, /\[DATE-1\] deviations\[0\]\.opened is 'next week' - a Deviation's `opened` and `decided` are dates, YYYY-MM-DD/);
  /* the wording of the four that came with CP-AUTHOR-1: the place, the value as the reference prints it, the rule's why */
  const said = c => rules.jscObjectErrors(v.find(x => x.name === c).document).errors.join(" ");
  assert.match(said("deviation-decided-as-free-text"), /\[DATE-1\] deviations\[0\]\.decided is '[^']+' - a Deviation's `opened` and `decided` are dates/);
  assert.match(said("mapping-provenance-date-as-free-text"), /\[DATE-3\] provenance\.date is '[^']+' - the `date` of a Mapping's provenance is a date, YYYY-MM-DD/);
  assert.match(said("assessment-time-without-an-offset"), /\[DATE-4\] time is '[^']+' - the `time` of an Assessment is a date or an RFC 3339 date-time with an offset/);
  assert.match(said("attestation-timestamp-as-free-text"), /\[DATE-5\] timestamp is '[^']+' - the `timestamp` of an Attestation is a date or an RFC 3339 date-time with an offset/);
});

/* The export writes the kernel pin from jscNeedsKernel2 (jascon-core.js); the
   whole-set check holds a set to KERNEL-1 with jscKernelNeeded. The same
   reasons stand in two files. Every object set of the kernel and author
   families, and every valid shape document on its own, gets the same answer
   from both - otherwise the app exports a set that its own rules, and the
   reference, refuse for want of the pin. */
test("kernel: the pin the export writes (jscNeedsKernel2) is the pin KERNEL-1 asks for (jscKernelNeeded)", () => {
  const k = vectors("kernel"), a = vectors("author");
  const sets = [...k.vectors.map(c => [c.name, c.objects]), ...k["shape-vectors"].filter(c => c.expected === "valid").map(c => [c.name, [c.document]]),
    ...[...a["author-vectors"], ...a["review-vectors"]].map(c => [c.name, c.objects])];
  let needing = 0;
  for (const [name, list] of sets) {
    const typed = rules.jscTypedObjects(list);
    assert.equal(typed.size, list.length, name + ": every object is typed");
    const asked = rules.jscKernelNeeded(typed)[0] === "2.0.0";
    assert.equal(core.jscNeedsKernel2({ scales: new Map(), objects: asObjs(list) }), asked, name);
    needing += asked ? 1 : 0;
  }
  assert.ok(needing > 0 && needing < sets.length, "both answers occur among the sets");
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

/* CP-AUTHOR-1: who decided, and when. `expected` of an author vector is the
   whole report as [rule, object id, count], in its order. A review vector
   gives the day it is asked about (`as-of`) and names the overdue and the
   not-evaluable places as [object id, where], absent meaning none. A case
   whose objects do not all get a type fails, as in the reference's runner
   (run_author). The messages are not part of the vectors' assertion. */
const authorTyped = c => {
  const objs = rules.jscTypedObjects(c.objects);
  assert.equal(objs.size, c.objects.length, `${c.name}: every object is typed`);
  return objs;
};
const reviewPairs = r => [r.overdue.map(e => [e.id, e.where]), r["not-evaluable"].map(e => [e.id, e.where])];
test("author: what is missing, one entry per object and rule (AUTHOR-1 to AUTHOR-4)", async () => {
  const v = vectors("author")["author-vectors"];
  assert.equal(v.length, 18);
  for (const c of v) {
    const report = await rules.jscAuthorReport(authorTyped(c));
    assert.deepEqual(report.map(e => [e.rule, e.id, e.count]), c.expected, c.name);
    for (const e of report) assert.ok(e.rule in rules.JSC_AUTHOR_RULES && e.message.startsWith(e.id + ": ") && e.message.endsWith(`(${e.rule})`), `${c.name}: ${e.message}`);
  }
});
test("author: a review-due that has passed on the day asked about (REVIEW-1)", () => {
  const v = vectors("author")["review-vectors"];
  assert.equal(v.length, 22);
  for (const c of v) {
    const r = rules.jscReviewReport(authorTyped(c), c["as-of"]);
    assert.deepEqual(reviewPairs(r), [c["expected-overdue"] || [], c["expected-not-evaluable"] || []], c.name);
    assert.ok(r.dated >= r.overdue.length + r["not-evaluable"].length, c.name + ": every place reported was asked");
  }
});
/* What the vectors leave to the platform. JavaScript's Date reads a year
   below 100 as 19xx, rolls the 31st of February over into March and offers
   local time beside UTC; the reference's calendar ends at 0001 and 9999,
   where Python raises. Each line is what validate_core.py's _utc_day gives. */
test("REVIEW-1: the day a review-due falls on - leap days, the ends of the calendar, offsets, durations", () => {
  const NO = "not a day of the calendar", day = (due, start) => rules.jscUtcDay(due, start);
  const date = value => day({ type: "date", value }), at = value => day({ type: "datetime", value });
  const after = (num, unit, start) => day({ type: "elapsed-duration", num, unit }, start);
  for (const ok of ["2024-02-29", "2000-02-29", "0001-01-01", "0099-12-31", "9999-12-31"]) assert.deepEqual(date(ok), [ok, null], ok);
  for (const bad of ["2026-02-29", "1900-02-29", "2026-02-31", "2026-04-31", "0000-01-01", "2026-00-10", "2026-13-01", "2026-11-00", "next week"]) assert.deepEqual(date(bad), [null, NO], bad);
  /* a date-time is an instant: its day is the UTC day, whatever the offset says the local day is */
  assert.deepEqual(at("2026-11-13T00:30:00+02:00"), ["2026-11-12", null]);
  assert.deepEqual(at("2026-11-12T23:30:00-05:00"), ["2026-11-13", null]);
  assert.deepEqual(at("2026-11-12T23:59:59.999Z"), ["2026-11-12", null]);
  assert.deepEqual(at("2026-12-31T23:00:00-01:00"), ["2027-01-01", null]);
  assert.deepEqual(at("2024-03-01T00:00:00+00:01"), ["2024-02-29", null]);
  assert.deepEqual(at("0050-06-01T12:00:00Z"), ["0050-06-01", null], "a year below 100 is that year, not 19xx");
  for (const bad of ["2026-02-31T10:00:00Z", "2026-11-13T24:00:00Z", "2026-11-13T23:60:00Z", "2026-11-13T23:59:60Z", "2026-11-13T12:00:00+24:00"]) assert.deepEqual(at(bad), [null, NO], bad);
  assert.deepEqual(at("0001-01-01T00:00:00+01:00"), [null, NO], "the instant lies before the calendar begins");
  assert.deepEqual(at("9999-12-31T23:30:00-01:00"), [null, NO], "the instant lies after the calendar ends");
  /* an elapsed duration is added to 00:00 UTC of the day it counts from */
  assert.deepEqual(after(86399, "seconds", "2026-11-12"), ["2026-11-12", null]);
  assert.deepEqual(after(86400, "seconds", "2026-11-12"), ["2026-11-13", null]);
  assert.deepEqual(after(1440, "minutes", "2026-12-31"), ["2027-01-01", null]);
  assert.deepEqual(after(24, "hours", "2024-02-28"), ["2024-02-29", null]);
  assert.deepEqual(after(24, "hours", "2026-02-28"), ["2026-03-01", null]);
  assert.deepEqual(after(24, "hours", "2026-02-31"), [null, NO], "the day it counts from is no day");
  assert.deepEqual(after(24, "hours", "9999-12-31"), [null, NO]);
  assert.deepEqual(after(9007199254740991, "hours", "2026-11-12"), [null, NO], "the largest number a bundle may carry");
  assert.deepEqual(after(24, "hours", undefined), [null, "a duration, and no date to count it from"]);
  assert.match(day({ type: "calendar-period", num: 1, unit: "months", "calendar-ref": "https://org.example/cal" }, "2026-11-12")[1], /no calendar https:\/\/org\.example\/cal \(D9/);
  assert.deepEqual(day({ type: "fortnight", num: 1 }, "2026-11-12"), [null, "not a typed review-due"]);
  /* the day asked about is an argument the caller owes; a day that is none is refused, not rolled over */
  for (const bad of [undefined, "", "13.11.2026", "2026-02-31", "2026-11-13T00:00:00Z"]) assert.throws(() => rules.jscReviewReport(new Map(), bad), /REVIEW-1 is asked about a day/, String(bad));
  assert.deepEqual(rules.jscReviewReport(new Map(), "2026-11-13"), { dated: 0, overdue: [], "not-evaluable": [] });
});
test("REVIEW-1: the report does not depend on the time zone of the machine", t => {
  const v = vectors("author")["review-vectors"], was = process.env.TZ;
  const run = () => JSON.stringify([v.map(c => rules.jscReviewReport(rules.jscTypedObjects(c.objects), c["as-of"])),
    ["2026-11-13T00:30:00+02:00", "2026-11-12T23:30:00-05:00", "2026-01-01T00:00:00Z", "2026-12-31T23:59:59Z"].map(value => rules.jscUtcDay({ type: "datetime", value })),
    rules.jscUtcDay({ type: "elapsed-duration", num: 24, unit: "hours" }, "2026-12-31"), rules.jscUtcDay({ type: "date", value: "2026-03-01" })]);
  try {
    process.env.TZ = "UTC";
    const utc = run();
    /* fourteen hours ahead of UTC and eleven behind: local midnight is another UTC day in both */
    for (const zone of ["Pacific/Kiritimati", "Pacific/Pago_Pago"]) {
      process.env.TZ = zone;
      /* a node without time zone data stays in UTC whatever TZ says; the test would then prove nothing */
      if (new Date(Date.UTC(2026, 10, 13)).getHours() === 0) return t.skip(`this node does not switch to ${zone} at run time`);
      assert.equal(run(), utc, zone);
    }
  } finally {
    if (was === undefined) delete process.env.TZ; else process.env.TZ = was;
  }
});

/* The two reports on the two folders the reference prints them for. A set is
   read as the app reads it (a graph from the folder's files), so this is the
   map a page will pass. The expectation is what validate_core.py printed for
   these folders with --as-of 2026-11-13; the next test asks it again. */
const EXAMPLES = path.resolve(CONF, "../examples"), IFA = path.resolve(CONF, "../../converted_examples/US.IFA-GoodRead/ifa-core-bundle");
const folderTree = (dir, prefix = "") => fs.readdirSync(dir).sort().flatMap(n => fs.statSync(path.join(dir, n)).isDirectory()
  ? folderTree(path.join(dir, n), prefix + n + "/") : [{ path: prefix + n, text: core.jscDecode(fs.readFileSync(path.join(dir, n))) }]);
const folderObjects = dir => core.jscGraphFrom(core.jscClassifyFiles(folderTree(dir)).records).objects;
test("author and review on the example folder and the IFA bundle, as of 2026-11-13: what the reference reports", async () => {
  const ex = folderObjects(EXAMPLES), exReview = rules.jscReviewReport(ex, "2026-11-13");
  assert.deepEqual(await rules.jscAuthorReport(ex), [], "the example folder names its authors");
  assert.equal(exReview.dated, 2);
  assert.deepEqual(exReview.overdue, []);
  assert.deepEqual(exReview["not-evaluable"].map(e => [e.id, e.where]), [["https://cso.example/risk/R-2026-007", "review-due"]]);
  assert.match(exReview["not-evaluable"][0].why, /^a calendar period, and this tool has no calendar https:\/\/cso\.example\/calendar\/isms /);
  const G = "https://ifa.gov/goodread/", ifa = folderObjects(IFA);
  /* seven lines since the converter pre-fills from the source (backlog #69): the two authorizations carry the
     date the source states, and the system's Implementation the author its plan names. The plan of action
     names no party and the leveraged pair no party with a name, so their records still say nobody. */
  assert.deepEqual((await rules.jscAuthorReport(ifa)).map(e => [e.rule, e.id, e.count]), [
    ["AUTHOR-2", G + "finding/goodread-risk-1", 1], ["AUTHOR-3", G + "finding/goodread-risk-1", 1], ["AUTHOR-2", G + "finding/goodread-risk-2", 1],
    ["AUTHOR-2", G + "impl/csp-iaas-ac-2", 1], ["AUTHOR-2", G + "impl/saas-ac-2", 1],
    ["AUTHOR-2", G + "risk/goodread-risk-1", 1], ["AUTHOR-2", G + "risk/goodread-risk-2", 1]]);
  assert.deepEqual(rules.jscReviewReport(ifa, "2026-11-13"), { dated: 2, "not-evaluable": [], overdue: [
    { id: G + "risk/goodread-risk-1", where: "review-due", day: "2024-01-01" }, { id: G + "risk/goodread-risk-2", where: "review-due", day: "2023-06-23" }] });
});
const pythonWithJsonschema = spawnSync("python3", ["-c", "import jsonschema"], { encoding: "utf8" }).status === 0;
test("author and review: the reference validator prints the same lines for the two folders", { skip: !pythonWithJsonschema && "python3 with jsonschema is not installed" }, async () => {
  const AS_OF = "2026-11-13";
  /* the lines of report_authors_and_reviews, from the app's two reports: jscAuthorReviewLines is what the Validate page shows */
  const lines = async objs => rules.jscAuthorReviewLines(await rules.jscAuthorReport(objs), rules.jscReviewReport(objs, AS_OF), AS_OF, false)
    .map(l => (l.kind === "summary" ? l.text : `note: ${l.text}`));
  /* one run: the bundle named on the command line, then the example folder, each above its summary line */
  const run = spawnSync("python3", [path.resolve(CONF, "../scripts/validate_core.py"), "--as-of", AS_OF, IFA], { encoding: "utf8" });
  assert.equal(run.status, 0, run.stdout.slice(-2000) + run.stderr.slice(-2000));
  const out = run.stdout.split(/\r?\n/), from = out.indexOf("== bundles =="), ifaEnd = out.findIndex(l => /^ {2}\S*ifa-core-bundle: \d+ pass/.test(l)), exEnd = out.findIndex(l => l.startsWith("  skill-examples: "));
  assert.ok(from >= 0 && ifaEnd > from && exEnd > ifaEnd, "the output has its two sections");
  const said = part => part.map(l => l.trim()).filter(l => /\((AUTHOR-[1-4]|REVIEW-1)[):]/.test(l));
  assert.deepEqual(await lines(folderObjects(IFA)), said(out.slice(from, ifaEnd)), "the IFA bundle");
  assert.deepEqual(await lines(folderObjects(EXAMPLES)), said(out.slice(ifaEnd, exEnd)), "the example folder");
});

/* The two reports as part of the check of a whole set (what the Validate page
   runs). The day is an argument: the rules read no clock. */
const folderGraph = dir => core.jscGraphFrom(core.jscClassifyFiles(folderTree(dir)).records);
test("a whole set: the two reports are part of the check; AUTHOR lines fail only when the caller requires authors, REVIEW-1 never", async () => {
  const g = folderGraph(IFA), verified = await core.jscVerify(g);
  const of = (res, area, kind) => res.findings.filter(f => f.area === area && f.kind === kind);
  const plain = await rules.jscCheckGraph(g, verified, { asOf: "2026-11-13" });
  assert.equal(plain.report["as-of"], "2026-11-13");
  assert.equal(plain.report["require-authors"], false);
  assert.equal(plain.report.authors.length, 7);   // 7 since the converter pre-fills from the source (backlog #69); 10 before
  assert.deepEqual(plain.report.review, rules.jscReviewReport(g.objects, "2026-11-13"));
  assert.deepEqual(plain.report.lines, rules.jscAuthorReviewLines(await rules.jscAuthorReport(g.objects), rules.jscReviewReport(g.objects, "2026-11-13"), "2026-11-13", false));
  assert.deepEqual([of(plain, "author", "note").length, of(plain, "author", "error").length], [7, 0], "a missing author is a line of the report");
  assert.deepEqual([of(plain, "review", "note").length, of(plain, "review", "error").length], [3, 0], "the summary and the two overdue reviews");
  const errorsBefore = plain.findings.filter(f => f.kind === "error").length;
  const strict = await rules.jscCheckGraph(g, verified, { asOf: "2026-11-13", requireAuthors: true });
  assert.equal(strict.report["require-authors"], true);
  assert.deepEqual([of(strict, "author", "note").length, of(strict, "author", "error").length], [0, 7], "required: every AUTHOR line is a failure");
  assert.deepEqual([of(strict, "review", "note").length, of(strict, "review", "error").length], [3, 0], "REVIEW-1 fails nothing, with any switch");
  assert.equal(strict.findings.filter(f => f.kind === "error").length, errorsBefore + 7, "nothing else changes");
  assert.ok(strict.report.lines.filter(l => l.rule !== "REVIEW-1").every(l => l.kind === "error") && strict.report.lines.filter(l => l.rule === "REVIEW-1").every(l => l.kind !== "error"));
  /* the day asked about decides what is overdue: due on that day is not overdue, the day after it is */
  const overdueOn = async day => (await rules.jscCheckGraph(g, verified, { asOf: day })).report.review.overdue.map(e => e.day);
  assert.deepEqual(await overdueOn("2023-06-23"), []);
  assert.deepEqual(await overdueOn("2023-06-24"), ["2023-06-23"]);
  assert.deepEqual(await overdueOn("2024-01-02"), ["2024-01-01", "2023-06-23"]);
  /* no day given: who is missing is still reported, a review is not asked, and nothing is read from a clock */
  const undated = await rules.jscCheckGraph(g, verified);
  assert.equal(undated.report.review, null);
  assert.equal(undated.report["as-of"], null);
  assert.equal(undated.report.authors.length, 7);
  assert.equal(of(undated, "review", "note").length, 0);
  await assert.rejects(rules.jscCheckGraph(g, verified, { asOf: "13.11.2026" }), /REVIEW-1 is asked about a day/);
  /* the example folder names its authors: required or not, nothing fails */
  const ex = folderGraph(EXAMPLES), exStrict = await rules.jscCheckGraph(ex, await core.jscVerify(ex), { asOf: "2026-11-13", requireAuthors: true });
  assert.deepEqual(exStrict.findings.filter(f => f.kind === "error"), []);
  assert.deepEqual(exStrict.report.lines.map(l => l.kind), ["summary", "note"]);
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

test("jcs: canonical form, optional containers that must be absent instead of empty, and the number domain", () => {
  const v = vectors("jcs").vectors;
  assert.equal(v.length, 22);
  for (const c of v) {
    if (c.canonical != null) assert.equal(core.jscCanonical(c.input), c.canonical, c.name);
    else if ("authoring-input" in c) assert.equal(rules.jscOptionalEmptyViolations(c["authoring-input"]).length ? "invalid" : "valid", c.expected, c.name);
    else {
      /* NUMBER-1 (errata 2026-11-13): the vector is a JSON text, because JSON.parse reads 1.0 as 1 */
      const text = c["number-text"], value = JSON.parse(text);
      const verdict = rules.jscNumberSpellingViolations(text).length || rules.jscNumberViolations(value).length ? "invalid" : "valid";
      assert.equal(verdict, c.expected, c.name);
      if (verdict === "valid") assert.equal(core.jscCanonical(value), c["canonical-text"], c.name);
    }
  }
});
test("NUMBER-1 (errata 2026-11-13): JSON.parse alone would let every spelling and the reported integer through", () => {
  /* why the rule needs the text: after parsing, these are indistinguishable from valid numbers */
  for (const text of ['{"n":1.0}', '{"n":1e3}', '{"n":-0}']) {
    assert.equal(rules.jscNumberViolations(JSON.parse(text)).length, 0, `${text}: the value alone looks fine`);
    assert.equal(rules.jscNumberSpellingViolations(text).length, 1, `${text}: the text is refused`);
  }
  /* the reported case: the parser rounds, and the value check still refuses, because the result is past the range */
  assert.equal(JSON.parse("9007199254740993"), 9007199254740992);
  assert.equal(rules.jscNumberViolations(JSON.parse('{"n":9007199254740993}')).length, 1);
  const check = { observes: [{ name: "n", type: "integer" }], criteria: [{ fact: "n", op: "equals", expected: 9007199254740992 }] };
  assert.equal(rules.jscCheckVerdict(check, JSON.parse('{"facts":{"n":9007199254740993}}'), null)[0], "inconclusive");
  /* an object and a whole file */
  const req = { id: "https://ex.org/req/1", version: "1", lifecycle: "active", statements: [{ id: "s1", modality: "must", "obligated-parties": ["https://ex.org/party/o"],
    prose: { en: "At most {param:n}." }, parameters: [{ name: "n", type: "integer", max: 9007199254740992 }] }] };
  assert.match(rules.jscObjectErrors(req).errors.join(" | "), /\[NUMBER-1\] \$\.statements\[0\]\.parameters\[0\]\.max/);
  assert.match(rules.jscNumberError('{"id":"x","annotations":{"alpha":0.5}}'), /\[NUMBER-1\] written as 0\.5/);
  assert.equal(rules.jscNumberError('{"s":"1.0 and -0","n":7}'), null);
});

test("facet: every vector (stdlib, pinned, private, unregistered)", () => {
  const v = vectors("facet").vectors;
  assert.equal(v.length, 7);
  for (const c of v) {
    const errs = rules.jscFacetErrors([[c.name, c.object]], new Map(Object.entries(c.pinned || {})));
    assert.equal(errs.length ? "invalid" : "valid", c.expected, `${c.name}: ${errs[0] || ""}`);
  }
});

/* An Assessment's `method` is a facet payload (backlog #55). The reference runner holds an implementation to the number
   of errors for the object and to a fragment of each: an error about a method names it as method '<key>', one about a
   facet as facet '<key>'. The name of a vector is no part of an error, so the object is labelled with its own id here. */
test("facets: an Assessment's method is held to its facet, all 13 vectors by the number of errors and a fragment of each", () => {
  const v = vectors("facet")["method-vectors"];
  assert.equal(v.length, 13);
  let errors = 0;
  for (const c of v) {
    const errs = rules.jscFacetErrors([[c.object.id || "object", c.object]], new Map(Object.entries(c.pinned || {})));
    assert.equal(errs.length, c["expected-errors"], `${c.name}: ${errs.join(" | ")}`);
    assert.equal(errs.length ? "invalid" : "valid", c.expected, c.name);
    for (const frag of c["expected-frags"]) assert.ok(errs.some(e => e.includes(frag)), `${c.name}: no error says ${frag}: ${errs.join(" | ")}`);
    assert.ok(errs.every(e => !e.includes(c.name)), c.name + ": the name of the vector is in no error");
    errors += errs.length;
  }
  assert.equal(errors, 8, "eight errors in the thirteen cases");
  /* the two sentences of the reference, written out once */
  const asmt = method => ({ id: "https://a.example/assessment/x", version: "1", lifecycle: "active", "subject-refs": ["https://a.example/req/1"], method, "performer-ref": "https://a.example/p", time: "2026-11-14T09:00:00Z", result: "satisfied" });
  const said = method => rules.jscFacetErrors([["https://a.example/assessment/x", asmt(method)]], new Map());
  assert.deepEqual(said({ kind: "manual-check", tool: "JASCON-App 0.9.12" }), ["kind", "tool"].map(k =>
    `https://a.example/assessment/x: method '${k}' is no registered facet - not stdlib, not pinned in the manifest, not private: (an Assessment's method is a facet payload and fails closed, D10)`));
  assert.match(said({ [rules.JSC_ASSESSMENT_CRITERIA]: { method: "by hand" } })[0], /^https:\/\/a\.example\/assessment\/x: method 'https:\/\/ns\.jascon\.net\/stdlib\/facet\/assessment-criteria@1' payload violates its schema: /);
  assert.deepEqual(said("manual"), [], "a method that is no object is the kernel schema's matter and not this rule's");
  /* a member called `method` inside a facet payload is that facet's business, also where it is an object with keys of its own */
  assert.deepEqual(rules.jscFacetErrors([["x", { ...asmt(rules.jscManualMethod()), facets: { "https://assessor.example/facet/review@1": { method: { kind: "sampled" } } } }]],
    new Map([["https://assessor.example/facet/review", { type: "object" }]])), []);
  assert.equal(rules.jscFacetErrors([["x", { id: "x", method: { kind: "y" } }]], new Map()).length, 1, "the member is read at the top of any object, as the reference reads it");
  /* what the Assess page writes is the standard facet for a manual check, and the reference's rule accepts it */
  assert.deepEqual(rules.jscManualMethod(), { "https://ns.jascon.net/stdlib/facet/assessment-criteria@1": { method: "manual" } });
  assert.deepEqual(said(rules.jscManualMethod()), []);
  assert.deepEqual(rules.jscObjectErrors(asmt(rules.jscManualMethod())).errors, []);
  /* the method this app wrote before build 0.9.13 is recognised as its own, and nothing else is */
  const own = { kind: "manual-check", tool: "JASCON-App 0.9.12" };
  assert.equal(rules.jscIsAppMethodBefore0913(own), true);
  for (const other of [{ kind: "manual-check" }, { kind: "manual-check", tool: "Another Tool 1.0" }, { kind: "scan", tool: "JASCON-App 0.9.12" }, { ...own, note: "x" }, rules.jscManualMethod(), {}, null, "manual"]) {
    assert.equal(rules.jscIsAppMethodBefore0913(other), false, JSON.stringify(other));
    assert.equal(rules.jscRewriteAppMethod(asmt(other)), null, "a method of another shape is somebody else's and is not rewritten: " + JSON.stringify(other));
  }
  assert.deepEqual(rules.jscRewriteAppMethod(asmt(own)), asmt(rules.jscManualMethod()), "only the method changes");
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

/* attestation-binds applied to a bundle (Appendix B.1.7; backlog #46). The reference runner holds an
   implementation to four things per case: the verdict, which manifest is bound, the status of every subject in
   the Attestation's order, and whether the bundle fails. So does this test, and it holds the count: a list
   that grew in the reference and not here would otherwise pass. Every object of a case must type, as in the
   runner (`len(objs) == len(case["objects"])`). */
test("attestation-binds on a bundle: all 19 vectors, by verdict, manifest bound, every subject and failure", async () => {
  const v = vectors("attestation")["binds-vectors"];
  assert.equal(v.length, 19);
  const seen = { verdicts: new Set(), manifests: new Set(), statuses: new Set(), lifecycles: new Set() };
  for (const c of v) {
    const objs = rules.jscTypedObjects(c.objects);
    assert.equal(objs.size, c.objects.length, c.name + ": every object of the case types");
    const r = rules.jscAttestationBinds(c.attestation, c["manifest-digest"], await rules.jscSemanticDigests(objs), c["kept-packs"] || []);
    assert.deepEqual([r.verdict, r.manifest, r.subjects.map(s => s.status), r.fails],
      [c.expected, c["expected-manifest"], c["expected-subjects"], c["expected-failure"]], c.name);
    seen.verdicts.add(r.verdict); seen.manifests.add(r.manifest); r.subjects.forEach(s => seen.statuses.add(s.status)); seen.lifecycles.add(c.attestation.lifecycle);
  }
  /* the vectors reach every value an answer can take; a list that lost a kind of case would be noticed here */
  assert.deepEqual([[...seen.verdicts].sort(), [...seen.manifests].sort(), [...seen.statuses].sort(), [...seen.lifecycles].sort()],
    [["fail", "full-match", "semantic-match"], ["kept-pack", "other", "this"], ["absent", "differs", "match"], ["active", "deprecated", "draft", "withdrawn"]]);
});

/* The lines of the reference (binds_report of validate_core.py), word for word. The expected texts are written
   out here; tests/pages.test.mjs compares the page with what the reference prints for three folders. */
test("attestation-binds: one line per Attestation in the order of the ids, in the reference's words; a failure only while the Attestation is active", async () => {
  const A = "https://a.example", D = n => "sha256:" + String(n).repeat(64);
  const req = n => ({ id: `${A}/req/${n}`, version: "1", lifecycle: "active", statements: [{ id: "s1", modality: "must", "obligated-parties": [A + "/p"], prose: { en: `Do ${n}.` } }] });
  const objs = rules.jscTypedObjects([req(1), req(2)]), delivered = await rules.jscSemanticDigests(objs);
  const d1 = delivered.get(A + "/req/1"), d2 = delivered.get(A + "/req/2");
  const att = (name, subjects, bound, lifecycle = "active") => [`${A}/attestation/${name}`, { id: `${A}/attestation/${name}`, version: "1", lifecycle,
    "subject-semantic-digests": subjects, "content-manifest-digest": bound, signer: A + "/p", timestamp: "2026-11-14T09:00:00Z" }];
  const named = (n, digest) => ({ id: `${A}/req/${n}`, "semantic-digest": digest });
  const atts = new Map([
    att("z-full", [named(1, d1), d2], D("a")),
    att("b-kept", [named(2, d2)], D("c")),
    att("c-other", [named(1, d1)], D("e")),
    att("d-changed", [named(1, D(9)), named(2, d2), named(3, D(8)), D(7)], D("a")),
    att("e-withdrawn", [named(1, D(9))], D("e"), "withdrawn"),
    att("f-empty", [], D("a")),
    att("g-draft", [D(7)], D("a"), "draft"),
  ]);
  const lines = rules.jscBindsReport(atts, D("a"), delivered, [D("c")]);
  const B17 = "(B.1.7: an Attestation binds what is delivered, or it fails; a changed subject is normative content changed after signing)";
  assert.deepEqual(lines.map(l => [l.kind, l.text]), [
    ["line", `binds: ${A}/attestation/b-kept = FULL MATCH [1 subject(s) of this bundle; a pack manifest this bundle keeps]`],
    ["line", `binds: ${A}/attestation/c-other = SEMANTIC MATCH [1 subject(s) of this bundle; another manifest: the content is proven, the packaging was altered]`],
    ["failure", `[attestation-binds] ${A}/attestation/d-changed: subject ${A}/req/1: recomputed semantic digest ${d1}, signed ${D(9)}; subject ${A}/req/3: not an object of this bundle; subject ${D(7)}: no object of this bundle carries it - this manifest ${B17}`],
    ["line", `binds: ${A}/attestation/e-withdrawn = DOES NOT BIND [lifecycle withdrawn: reported, not a failure] subject ${A}/req/1: recomputed semantic digest ${d1}, signed ${D(9)} - another manifest`],
    ["failure", `[attestation-binds] ${A}/attestation/f-empty: it names no subject - this manifest ${B17}`],
    ["line", `binds: ${A}/attestation/g-draft = DOES NOT BIND [lifecycle draft: reported, not a failure] subject ${D(7)}: no object of this bundle carries it - this manifest`],
    ["line", `binds: ${A}/attestation/z-full = FULL MATCH [2 subject(s) of this bundle; this manifest]`],
  ]);
  assert.deepEqual(lines.filter(l => l.fails).map(l => l.id.split("/").pop()), ["d-changed", "f-empty"]);
});

/* MANIFEST-1 (D3.11; backlog #75): no content manifest lists an Attestation. The reference runner holds an
   implementation to the number of failures and to the id each one starts with, and so does this test; the count
   of the vectors is held too. */
test("MANIFEST-1: all 8 vectors; one failure per Attestation among the objects a manifest lists, in the order of the ids", () => {
  const v = vectors("attestation")["listed-vectors"];
  assert.equal(v.length, 8);
  let failures = 0;
  for (const c of v) {
    const objs = rules.jscTypedObjects(c.objects);
    assert.equal(objs.size, c.objects.length, c.name + ": every object of the case types");
    const errs = rules.jscListedAttestationErrors(objs);
    assert.equal(errs.length, c["expected-fails"], c.name);
    assert.deepEqual(errs.map(e => e.slice(0, e.indexOf(": an Attestation is listed"))), c["expected-ids"], c.name + ": each failure starts with the id, in the order of the ids");
    assert.ok(errs.every(e => e.includes("(MANIFEST-1: ")), c.name);
    failures += errs.length;
  }
  assert.equal(failures, 7, "seven listed Attestations in the eight cases");
  /* the reference's sentence, written out once */
  const att = { id: "https://a.example/attestation/x", version: "1", lifecycle: "withdrawn", "subject-semantic-digests": ["sha256:" + "0".repeat(64)],
    "content-manifest-digest": "sha256:" + "1".repeat(64), signer: "https://a.example/p", timestamp: "2026-11-14T09:00:00Z" };
  assert.deepEqual(rules.jscListedAttestationErrors(rules.jscTypedObjects([att])), ["https://a.example/attestation/x: an Attestation is listed in the content manifest " +
    "(MANIFEST-1: Attestations are excluded from the content manifest by definition, D3.1 - an Attestation lies beside a manifest and is never an entry of one)"]);
});

/* The reference sees a bundle on disk. A set is a bundle that was loaded and may have been written to since, so
   jscSetBinds first decides which bundle the comparison is made against (its `basis`). Held here on the IFA
   bundle with files added the way the store holds them: `origin` says whether a file arrived or was written. */
test("attestation-binds on a set: as loaded it is held to the manifest it came with, written to since to the bundle an export would write; what is only an artefact of the app is no failure", async () => {
  const AID = "https://ifa.gov/goodread/attestation/ifa-ato", NS = "https://org.example";
  const arrived = () => core.jscClassifyFiles(folderTree(IFA)).records.map(r => ({ ...r, origin: "imported" }));
  const file = (path, obj, origin) => ({ path, text: core.jscSerialize(obj), kind: "object", type: core.jscInferType(obj), id: obj.id, origin });
  const binds = async records => { const g = core.jscGraphFrom(records); return { g, ...(await rules.jscSetBinds(g, rules.jscTypedObjects([...g.objects.values()].map(r => r.obj)))) }; };
  const said = (b, id) => { const l = b.lines.find(x => x.id === id); return [l.kind, l.text.replace(/^(binds: \S+ = |\[attestation-binds\] \S+ )/, "").replace(/sha256:[0-9a-f]{64}/g, "sha256:…").replace(/ \(B\.1\.7.*$/, "")]; };
  const req = { id: NS + "/req/door", version: "1", lifecycle: "active", statements: [{ id: "s1", modality: "must", "obligated-parties": [NS + "/party/staff"], prose: { en: "Lock the door." } }] };
  const att = (name, subjects, bound) => ({ id: `${NS}/attestation/${name}`, version: "1", lifecycle: "active", "subject-semantic-digests": subjects,
    "content-manifest-digest": bound, signer: NS + "/party/ao", timestamp: "2026-11-14T09:00:00Z" });
  const named = async o => ({ id: o.id, "semantic-digest": await core.jscSemanticDigest(o) });

  /* as it was loaded: the manifest it came with, and the objects that manifest lists */
  const loaded = await binds(arrived()), delivered = await core.jscPackageDigest(loaded.g.manifestText);
  assert.deepEqual([loaded.basis, loaded["manifest-digest"], loaded["loaded-manifest-digest"]], ["loaded", delivered, delivered]);
  assert.deepEqual(said(loaded, AID), ["line", "FULL MATCH [3 subject(s) of this bundle; this manifest]"]);

  /* as loaded, and damaged: a file that arrived with the bundle and that its manifest does not list is no object of the
     bundle, for the reference too. An Attestation that names it fails, and one that names an Attestation beside the
     manifest by its digest does as well: what is not listed is no subject of anything */
  const ifaAtt = loaded.g.objects.get(AID).obj;
  const damaged = await binds([...arrived(), file("objects/req/door.json", req, "imported"),
    file("attestation-door.json", att("door", [await named(req)], delivered), "imported"),
    file("attestation-of-an-attestation.json", att("meta", [await core.jscSemanticDigest(ifaAtt)], delivered), "imported")]);
  assert.equal(damaged.basis, "loaded", "nothing was written here: the folder is judged against its own manifest");
  assert.deepEqual(said(damaged, NS + "/attestation/door"), ["failure", `subject ${req.id}: not an object of this bundle - this manifest`]);
  assert.deepEqual(said(damaged, NS + "/attestation/meta"), ["failure", "subject sha256:…: no object of this bundle carries it - this manifest"]);
  assert.deepEqual(said(damaged, AID), ["line", "FULL MATCH [3 subject(s) of this bundle; this manifest]"]);

  /* the same Requirement written here: the manifest the set came with does not list it and never will. Held to that
     manifest, an Attestation that names it would fail for no reason but that this app has written no manifest yet.
     It is held to the bundle an export would write: the Requirement is listed there */
  const withReq = [...arrived(), file("objects/req/door.json", req, "authored")];
  const next = await core.jscPackageDigest((await core.jscBuildBundle(core.jscGraphFrom(withReq))).files[0].text);
  assert.notEqual(next, delivered);
  const door = att("door", [await named(req)], next);
  const written = await binds([...withReq, file("attestation-door.json", door, "authored"),
    file("attestation-of-an-attestation.json", att("meta", [await core.jscSemanticDigest(door)], next), "authored")]);
  assert.deepEqual([written.basis, written["manifest-digest"], written["loaded-manifest-digest"]], ["export", next, delivered]);
  assert.deepEqual(said(written, NS + "/attestation/door"), ["line", "FULL MATCH [1 subject(s) of this bundle; this manifest]"]);
  assert.deepEqual(said(written, NS + "/attestation/meta"), ["failure", "subject sha256:…: no object of this bundle carries it - this manifest"],
    "an Attestation beside the manifest is not listed by an export either, so it is no subject");
  assert.deepEqual(said(written, AID), ["line", "SEMANTIC MATCH [3 subject(s) of this bundle; another manifest: the content is proven, the packaging was altered]"],
    "the Attestation that bound the manifest that was loaded is no failure: its subjects are as signed");
  assert.deepEqual(written.lines.filter(l => l.fails).map(l => l.id), [NS + "/attestation/meta"]);

  /* a subject that was changed here is a failure on either basis */
  const impl = loaded.g.objects.get("https://ifa.gov/goodread/impl/system1234-ac-6.1");
  const edited = await binds(arrived().map(r => (r.path === impl.path ? { ...r, text: core.jscSerialize({ ...impl.obj, status: "planned" }), origin: "authored" } : r)));
  assert.equal(edited.basis, "export");
  assert.deepEqual(said(edited, AID), ["failure", `subject ${impl.obj.id}: recomputed semantic digest sha256:…, signed sha256:… - another manifest`]);
  /* saved here without a change: the manifest the set came with still describes it */
  const untouched = await binds(arrived().map(r => (r.path === impl.path ? { ...r, origin: "authored" } : r)));
  assert.deepEqual([untouched.basis, said(untouched, AID)[1]], ["loaded", "FULL MATCH [3 subject(s) of this bundle; this manifest]"]);
  /* an Attestation written here, and nothing else: it is no object of the manifest, so the manifest still describes the set */
  const withdrawn = await binds(arrived().map(r => (r.id === AID ? { ...r, text: core.jscSerialize({ ...ifaAtt, lifecycle: "withdrawn" }), origin: "authored" } : r)));
  assert.deepEqual([withdrawn.basis, said(withdrawn, AID)[1]], ["loaded", "FULL MATCH [3 subject(s) of this bundle; this manifest]"]);
  /* and that holds for a damaged folder too: an Attestation written here does not make the folder one that was changed here */
  const both = await binds([...arrived().map(r => (r.id === AID ? { ...r, text: core.jscSerialize({ ...ifaAtt, lifecycle: "withdrawn" }), origin: "authored" } : r)), file("objects/req/door.json", req, "imported")]);
  assert.deepEqual([both.basis, said(both, AID)[1]], ["loaded", "FULL MATCH [3 subject(s) of this bundle; this manifest]"]);

  /* a scale written here changes the manifest an export writes, as an object does */
  const scaleText = fs.readFileSync(path.join(EXAMPLES, "scale-bsi-200-3-schadenshoehe.json"), "utf8");
  const scaled = await binds([...arrived(), { path: "scales/schadenshoehe.json", text: scaleText, kind: "scale", type: null, id: JSON.parse(scaleText).id, origin: "authored" }]);
  assert.deepEqual([scaled.basis, said(scaled, AID)[1]], ["export", "SEMANTIC MATCH [3 subject(s) of this bundle; another manifest: the content is proven, the packaging was altered]"]);

  /* MANIFEST-1 on the two bases. A bundle whose manifest lists its Attestation, as the IFA bundle had it until 2026-11-13:
     the file lies under objects/ and the manifest has a line for it with both digests */
  const manifest = JSON.parse(loaded.g.manifestText), attText = loaded.g.objects.get(AID).text, attPath = "objects/attestation/attestation-ifa-ato.json";
  manifest.objects.push({ id: AID, version: ifaAtt.version, path: attPath, "package-digest": await core.jscPackageDigest(attText), "semantic-digest": await core.jscSemanticDigest(ifaAtt) });
  const listing = () => arrived().map(r => (r.kind === "manifest" ? { ...r, text: core.jscSerialize(manifest) } : r.id === AID ? { ...r, path: attPath } : r));
  const MANIFEST_1 = `${AID}: an Attestation is listed in the content manifest (MANIFEST-1: Attestations are excluded from the content manifest by definition, D3.1 - ` +
    "an Attestation lies beside a manifest and is never an entry of one)";
  const refused = await binds(listing()), line = b => b.lines.find(l => l.id === AID);
  assert.deepEqual([refused.basis, line(refused).listed, line(refused)["manifest-1"]], ["loaded", "refused", MANIFEST_1]);
  assert.deepEqual(said(refused, AID), ["line", "SEMANTIC MATCH [3 subject(s) of this bundle; another manifest: the content is proven, the packaging was altered]"],
    "it is still held to what it binds: a manifest that lists it cannot be the one it binds");
  const asCame = await core.jscBuildBundle(refused.g);
  assert.deepEqual([asCame.verbatim, asCame.files[0].text === core.jscSerialize(manifest), asCame.problems], [true, true, []], "a set nobody changed leaves as it came, listing and all: nothing is repaired in silence");
  const res = await rules.jscCheckGraph(refused.g, await core.jscVerify(refused.g));
  assert.deepEqual(res.findings.filter(f => f.kind === "error").map(f => `${f.object}: ${f.message}`), [MANIFEST_1], "the whole-set check fails the set with the reference's sentence, and with nothing else");
  /* the same set after something else in it was written here: the manifest in question is the export's, which lists no Attestation */
  const risk = [...refused.g.objects.values()].find(r => r.type === "risk");
  const after = await binds(listing().map(r => (r.path === risk.path ? { ...r, text: core.jscSerialize({ ...risk.obj, title: { en: "Reworded" } }), origin: "authored" } : r)));
  assert.deepEqual([after.basis, line(after).listed, line(after)["manifest-1"]], ["export", "left-out", null]);
  const rewritten = await core.jscBuildBundle(after.g);
  assert.equal(rewritten.verbatim, false);
  assert.deepEqual(rewritten.manifest.objects.filter(e => e.id === AID), [], "the manifest written here does not list the Attestation");
  assert.equal(rewritten.manifest.objects.length, manifest.objects.length - 1, "and lists everything else");
  assert.deepEqual(rewritten.files.filter(f => /attestation/.test(f.path)).map(f => [f.path, f.text === attText]), [["attestation-ifa-ato.json", true]], "its file leaves beside the manifest, unchanged");
  assert.deepEqual(rewritten.problems, [`${AID}: was listed in the manifest this set came with; a manifest written here lists no Attestation (MANIFEST-1), so it leaves beside the manifest as attestation-ifa-ato.json`]);
  assert.equal(after["manifest-digest"], await core.jscPackageDigest(rewritten.files[0].text), "and that manifest is the one the comparison names");
  const res2 = await rules.jscCheckGraph(after.g, await core.jscVerify(after.g));
  assert.deepEqual(res2.findings.filter(f => f.kind === "error"), []);
  assert.deepEqual(res2.findings.filter(f => f.area === "manifest" && f.object === AID).map(f => [f.kind, f.message]),
    [["note", "the manifest this set came with lists this Attestation, which MANIFEST-1 refuses; the manifest an export writes now does not list it, and the file leaves beside the manifest"]]);

  /* a set without a manifest: there is nothing it was loaded with, and the comparison is with what an export would write */
  const loose = await binds(arrived().filter(r => r.kind !== "manifest"));
  assert.deepEqual([loose.basis, loose["loaded-manifest-digest"], said(loose, AID)[1]], ["export", null, "SEMANTIC MATCH [3 subject(s) of this bundle; another manifest: the content is proven, the packaging was altered]"]);
});

test("one object: prose-params-resolve, duplicate statement ids, a by-statement key that names nothing, an empty optional list", () => {
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
  assert.equal(v.length, 9);   // two more with #68: a pin version that ends in a line break, and one in other digits
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
  /* without the envelope file: an error, for an attestation beside the manifest as for a listed one. Until the reference
     read the Attestations beside a manifest (backlog #46, 2026-11-14) it did not look, and this was a note here */
  const g2 = core.jscGraphFrom(core.jscClassifyFiles(files.slice(0, -1)).records), r2 = await rules.jscCheckGraph(g2, null, { trusted: c["trusted-keys"] });
  assert.equal(r2.signatures[att.id], "missing");
  assert.equal(r2.tiers[tid], "consumer");
  assert.deepEqual(r2.findings.filter(f => f.kind === "error" && f.area === "signature").map(f => [f.object, f.message]),
    [[att.id, `envelope-ref '${att["envelope-ref"]}' does not resolve beside the manifest`]]);
});

/* CP-CHECK-1. The bundle vectors name the exact set of CHECK rules a
   conformant tool reports; `store` is the evidence store as text. */
test("check: I-Regexp - what must and must not match whole-value, and what every implementation refuses", () => {
  for (const c of vectors("check")["regex-vectors"]) {
    let valid = true, why = "";
    /* a pattern that no JSON text may carry (a lone surrogate) is given as code points */
    const pat = c["pattern-codepoints"] ? String.fromCodePoint(...c["pattern-codepoints"]) : c.pattern;
    try { rules.jscIreCompile(pat); } catch (e) { if (!(e instanceof rules.JscIRegexpError)) throw e; valid = false; why = e.message; }
    assert.equal(valid, c.valid, `${JSON.stringify(pat)}: ${why}`);
    for (const t of c.match || []) assert.ok(rules.jscIreFullMatch(pat, t), `${JSON.stringify(pat)} matches ${JSON.stringify(t)}`);
    for (const t of c["no-match"] || []) assert.ok(!rules.jscIreFullMatch(pat, t), `${JSON.stringify(pat)} does not match ${JSON.stringify(t)}`);
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

/* CP-ADVICE-1. The harness is the reference's (run_advice): a vector's
   manifest lists its objects by id, and version and digests are computed
   from the objects as published (_advice_fill); a kept manifest is the
   canonical form of its filled manifest, named by its SHA-256 unless the
   vector gives a name or raw text (_advice_kept). Every vector names the
   exact set of rules a conformant tool reports. */
const adviceFill = async (manifest, published) => {
  const byId = new Map((published || []).map(o => [o.id, o])), m = JSON.parse(JSON.stringify(manifest));
  for (const e of m.objects || []) {
    const src = byId.get(e.id);
    if (e["semantic-digest"] === "COMPUTE" && src) e["semantic-digest"] = await core.jscSemanticDigest(src);
    if (!("version" in e)) e.version = src ? src.version : "1";
    if (!("package-digest" in e)) e["package-digest"] = "sha256:" + "0".repeat(64);
    if (!("path" in e)) e.path = "objects/" + e.id.split("/").pop() + ".json";
  }
  return m;
};
const adviceKept = async list => {
  const out = [];
  for (const k of list || []) {
    const raw = "raw" in k ? k.raw : core.jscCanonical(await adviceFill(k.manifest, k.published));
    out.push([k.name || await core.jscSha256(raw), raw]);
  }
  return out;
};
const adviceTyped = (c, list) => {
  const objs = rules.jscTypedObjects(list);
  assert.equal(objs.size, list.length, `${c.name}: every object is typed`);
  return objs;
};
const adviceJudge = (c, errs, notes = []) => {
  assert.deepEqual([...new Set(errs.map(([r]) => r))].sort(), [...new Set(c["expected-rules"] || [])].sort(), `${c.name}: ${errs.map(([, m]) => m).join(" | ")}`);
  for (const frag of c["expected-frags"] || []) assert.ok(errs.some(([, m]) => m.includes(frag)), `${c.name}: a message with "${frag}"; got ${errs.map(([, m]) => m).join(" | ")}`);
  for (const frag of c["expected-notes"] || []) assert.ok(notes.some(n => n.includes(frag)), `${c.name}: a note with "${frag}"`);
};
test("advice: the family has its 74 vectors", () => {
  const v = vectors("advice");
  assert.deepEqual(["shape", "pack", "graph", "kept", "publisher", "import"].map(k => v[k + "-vectors"].length), [9, 15, 21, 11, 8, 10]);
});
test("advice: closed shapes - the pack header of a manifest and a capability's statement-ids", () => {
  for (const c of vectors("advice")["shape-vectors"]) {
    const matched = rules.jscMatchTypes(c.document);
    const got = c.kind === "manifest" ? !rules.jscShapeErrors("contentManifest", c.document).length : matched.length === 1 && matched[0] === c.kind;
    assert.equal(got ? "valid" : "invalid", c.expected, c.name);
  }
});
test("advice: what a pack may hold (ADVICE-1 to ADVICE-3) and that it pins its kernel", async () => {
  for (const c of vectors("advice")["pack-vectors"]) {
    const objs = adviceTyped(c, c.objects), m = await adviceFill(c.manifest, c.objects);
    const errs = rules.jscShapeErrors("contentManifest", m).length ? [["SCHEMA", "manifest schema violation"]]
      : [...rules.jscPackErrors(m, objs, new Map(Object.entries(c.declared || {}))), ...rules.jscKernelPinErrors(m, objs).map(e => ["KERNEL-1", e])];
    adviceJudge(c, errs);
  }
});
test("advice: capabilities and the edges that cite them (ADVICE-4 to ADVICE-7)", () => {
  for (const c of vectors("advice")["graph-vectors"]) {
    const objs = adviceTyped(c, c.objects), caps = rules.jscCapabilityErrors(objs);
    adviceJudge(c, [...caps.errors, ...rules.jscCapabilityRefErrors(objs)], caps.notes);
  }
});
test("advice: the pack manifests a set keeps (ADVICE-8 to ADVICE-10)", async () => {
  for (const c of vectors("advice")["kept-vectors"]) {
    const objs = adviceTyped(c, c.objects);
    const res = await rules.jscKeptPackErrors(await adviceKept(c.kept), c.manifest || null, objs);
    adviceJudge(c, res.errors);
    if ("expected-packs" in c) assert.equal(res.packs.length, c["expected-packs"], c.name + ": well-formed kept manifests");
  }
});
test("advice: the publisher is claimed or proven, in structural and in verification mode", async () => {
  for (const c of vectors("advice")["publisher-vectors"]) {
    const m = await adviceFill(c.manifest, c.published), mdig = "sha256:" + await core.jscSha256(core.jscCanonical(m));
    const subjects = JSON.parse(JSON.stringify(c.objects));
    for (const o of subjects) if (o["content-manifest-digest"] === "COMPUTE") o["content-manifest-digest"] = mdig;
    const objs = adviceTyped(c, subjects);
    const verify = c["trusted-keys"] !== undefined ? { envelopes: new Map(Object.entries(c.envelopes || {})), trusted: c["trusted-keys"], notes: [] } : null;
    assert.equal(await rules.jscPackPublisher(m.pack, mdig, objs, verify), c.expected, c.name);
  }
});
test("advice: import (ADVICE-11) - the plan, the same file again, another release, what is refused", async () => {
  for (const c of vectors("advice")["import-vectors"]) {
    const aObjs = adviceTyped(c, c.a.objects), bObjs = adviceTyped(c, c.b.objects);
    const kept = await rules.jscKeptPackErrors(await adviceKept(c.a.kept), null, new Map());
    const bm = await adviceFill(c.b.manifest, c.b.objects), bdig = await core.jscSha256(core.jscCanonical(bm));
    const R = rules.jscComposeAdvice(aObjs, kept.packs, bm, bdig, bObjs);
    for (const k of ["result", "added", "replaced", "removed", "dangling", "unchanged"]) if (k in c.expected) assert.deepEqual(R[k], c.expected[k], `${c.name}: ${k}`);
    adviceJudge(c, R.errors);
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

test("NUMBER-1 (errata 2026-11-13): a whole set - a file that writes 10.0 is an error although the parsed object is fine", async () => {
  const P = "https://ex.org";
  const req = { id: P + "/r", version: "1", lifecycle: "active", statements: [{ id: "s1", modality: "must", "obligated-parties": [P + "/p"], prose: { en: "X." } }] };
  const set = { id: P + "/s", version: "1", lifecycle: "active", members: [{ ref: P + "/r", sequence: 10 }] };
  const files = text => [{ path: "content-manifest.json", text: JSON.stringify({ "manifest-version": "1", objects: [] }) },
    { path: "objects/r.json", text: JSON.stringify(req) }, { path: "objects/s.json", text }];
  const numberErrors = async text => (await rules.jscCheckGraph(core.jscGraphFrom(core.jscClassifyFiles(files(text)).records), null))
    .findings.filter(f => f.kind === "error" && /NUMBER-1/.test(f.message));
  assert.deepEqual(await numberErrors(JSON.stringify(set)), []);
  const spelled = await numberErrors(JSON.stringify(set).replace('"sequence":10', '"sequence":10.0'));
  assert.equal(spelled.length, 1);
  assert.equal(spelled[0].object, set.id);
  assert.match(spelled[0].message, /objects\/s\.json: \[NUMBER-1\] written as 10\.0/);
  const large = await numberErrors(JSON.stringify(set).replace('"sequence":10', '"sequence":9007199254740993'));
  assert.ok(large.length >= 1 && /written as 9007199254740993/.test(large[0].message));
});
