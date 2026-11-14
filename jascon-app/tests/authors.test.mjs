/* Who decided, and when: what the pages and the imports write (backlog #69).

   The kernel has one optional spelling for it since release candidate 4,
   `provenance: {author-ref, date}` (specification D26). The rules that
   report where it is missing are tested in rules.test.mjs. This file tests
   the functions that write it, all of them pure:

   - jscProvenance: both fields or nothing;
   - jscImportProvenance: what the source states, replaced field by field by
     what the caller gives;
   - jscAuthorRecord, jscAuthorTailoring, jscAuthorRisk: the author of a
     save, written without taking over a decision somebody else made;
   - jscDecideDeviation: the day a Deviation was decided.

   Every object these functions make is held to the kernel schema, and the
   pin the export would write is compared with the pin KERNEL-1 asks for. */
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const require = createRequire(import.meta.url);
const core = require("../jascon-core.js"), rules = require("../jascon-rules.js");
const SCHEMA = JSON.parse(fs.readFileSync(path.join(ROOT, "jascon/schemas/jascon-2.0.0.schema.json"), "utf8"));

const O = "https://org.example", ALICE = { "author-ref": O + "/party/alice", date: "2026-11-03" }, BOB = { "author-ref": O + "/party/bob", date: "2026-11-13" };
const SET = "https://authority.example/set/base", REQ = "https://authority.example/req/R-1";
const op1 = { op: "set-parameter", "requirement-ref": REQ, "statement-id": "s1", parameter: "p", value: 3 };
const op2 = { op: "set-modality", "requirement-ref": REQ, "statement-id": "s2", modality: "must" };
const tailoring = extra => ({ id: O + "/tailoring/t", version: "1", lifecycle: "draft", selects: [{ "set-ref": SET }], ...extra });
const isType = (type, o) => assert.deepEqual(rules.jscShapeErrors(type, o), [], JSON.stringify(o));
const copy = o => JSON.parse(JSON.stringify(o));

test("the setting \"who am I\" is one entry of JSC_CFG, empty by default", () => {
  const me = core.JSC_CFG.filter(c => c.key === "org:me");
  assert.equal(me.length, 1);
  assert.equal(me[0].def, "", "nobody is assumed");
  assert.equal(me[0].choices, null);
});

test("provenance: an author and a date, or nothing", () => {
  assert.deepEqual(rules.jscProvenance(O + "/party/alice", "2026-11-13"), { "author-ref": O + "/party/alice", date: "2026-11-13" });
  assert.deepEqual(rules.jscProvenance("  " + O + "/party/alice ", "2026-11-13"), { "author-ref": O + "/party/alice", date: "2026-11-13" }, "the author is trimmed");
  for (const [who, when] of [["", "2026-11-13"], ["   ", "2026-11-13"], [null, "2026-11-13"], [undefined, "2026-11-13"],
    [O + "/party/alice", ""], [O + "/party/alice", null], [O + "/party/alice", "13.11.2026"], [O + "/party/alice", "2026-11-13T10:00:00Z"]]) {
    assert.equal(rules.jscProvenance(who, when), null, JSON.stringify([who, when]));
  }
});

test("an import: what the caller gives replaces what the source states, field by field; no provenance without both", () => {
  const stated = { "author-ref": "https://publisher.example", date: "2026-11-10" };
  const P = rules.jscImportProvenance;
  assert.deepEqual(P(stated, {}), { provenance: stated, from: "source" });
  assert.deepEqual(P(stated, undefined), { provenance: stated, from: "source" });
  assert.deepEqual(P(stated, { "author-ref": undefined, date: null }), { provenance: stated, from: "source" }, "undefined and null are not given");
  assert.deepEqual(P(stated, { "author-ref": O + "/party/alice" }), { provenance: { "author-ref": O + "/party/alice", date: "2026-11-10" }, from: "caller" }, "the author alone");
  assert.deepEqual(P(stated, { date: "2026-11-13" }), { provenance: { "author-ref": "https://publisher.example", date: "2026-11-13" }, from: "caller" }, "the date alone");
  assert.deepEqual(P(stated, { "author-ref": O + "/party/alice", date: "2026-11-13" }), { provenance: { "author-ref": O + "/party/alice", date: "2026-11-13" }, from: "caller" });
  /* one field missing: nothing is written, and nothing is made up for the other */
  assert.deepEqual(P({ "author-ref": "https://publisher.example", date: null }, {}), { provenance: null, from: "none" });
  assert.deepEqual(P({ "author-ref": null, date: "2026-11-10" }, {}), { provenance: null, from: "none" });
  assert.deepEqual(P({ "author-ref": null, date: null }, { "author-ref": O + "/party/alice" }), { provenance: null, from: "none" });
  assert.deepEqual(P({ "author-ref": null, date: null }, { "author-ref": O + "/party/alice", date: "2026-11-13" }).from, "caller");
  /* given as empty: the caller says nobody, and that replaces the source too */
  assert.deepEqual(P(stated, { "author-ref": "" }), { provenance: null, from: "none" });
  assert.deepEqual(P(stated, { date: "  " }), { provenance: null, from: "none" });
  /* a source date that is no date is not a date; a caller's is an error, because somebody typed it */
  assert.deepEqual(P({ "author-ref": "https://publisher.example", date: "1.2.3" }, {}), { provenance: null, from: "none" });
  assert.throws(() => P(stated, { date: "13.11.2026" }), /is not a date, YYYY-MM-DD/);
});

test("a record (Implementation, Finding): the author of this save, or none; an earlier author is not kept on a version he did not write", () => {
  const impl = { id: O + "/impl/x", version: "1", lifecycle: "draft", "component-ref": O + "/comp/c", "requirement-ref": REQ, responsibility: "provider",
    "satisfied-by": [{ "capability-ref": "cap-r-1" }], status: "planned" };
  const signed = rules.jscAuthorRecord(impl, BOB);
  assert.deepEqual(signed.provenance, BOB);
  assert.equal("provenance" in impl, false, "the argument is not changed");
  isType("implementation", signed);
  assert.deepEqual(rules.jscAuthorRecord(signed, null), impl, "no author: no provenance, and nothing else changes");
  assert.deepEqual(rules.jscAuthorRecord({ ...impl, provenance: ALICE }, BOB).provenance, BOB);
  const finding = { id: O + "/finding/f", version: "1", lifecycle: "draft", "assessment-ref": O + "/asmt/a", "requirement-ref": REQ, state: "open" };
  isType("finding", rules.jscAuthorRecord(finding, BOB));
});

test("a record written again with nothing changed keeps the author it names; one that names nobody gets the author of this save", () => {
  const impl = { id: O + "/impl/x", version: "1", lifecycle: "draft", "component-ref": O + "/comp/c", "requirement-ref": REQ, responsibility: "provider",
    "satisfied-by": [{ "capability-ref": "cap-r-1" }], status: "planned" };
  const alices = rules.jscAuthorRecord(impl, ALICE);
  /* a workbench saves all its edges; bob changed none of this one */
  assert.deepEqual(rules.jscAuthorRecord(impl, BOB, alices), alices, "the same version: alice's judgement stays alice's");
  assert.deepEqual(rules.jscAuthorRecord({ status: "planned", ...impl }, BOB, alices), alices, "the order of the fields is no change");
  assert.deepEqual(rules.jscAuthorRecord(impl, null, alices), alices, "also when the page knows no author now");
  /* bob changed it: his version */
  assert.deepEqual(rules.jscAuthorRecord({ ...impl, status: "implemented" }, BOB, alices).provenance, BOB);
  assert.equal("provenance" in rules.jscAuthorRecord({ ...impl, status: "implemented" }, null, alices), false, "changed and nobody named: the earlier author is not kept on it");
  /* nobody had signed it: the save that names an author signs it */
  assert.deepEqual(rules.jscAuthorRecord(impl, BOB, impl).provenance, BOB);
  assert.deepEqual(rules.jscAuthorRecord(impl, null, impl), impl);
  /* without a stored version there is nothing to keep */
  assert.deepEqual(rules.jscAuthorRecord(impl, BOB, null).provenance, BOB);
  assert.deepEqual(rules.jscAuthorRecord(impl, BOB, undefined).provenance, BOB);
});

test("a Tailoring, first save: the author stands once on the Tailoring, the entries inherit", () => {
  const next = tailoring({ excludes: [{ ref: REQ }], operations: [op1] });
  const out = rules.jscAuthorTailoring(next, null, ALICE);
  assert.deepEqual(out.provenance, ALICE);
  for (const e of [...out.selects, ...out.excludes, ...out.operations]) assert.equal("provenance" in e, false);
  assert.equal("provenance" in next, false, "the argument is not changed");
  isType("tailoring", out);
});

test("a Tailoring, saved by somebody else: unchanged entries get the old author written onto them, new and changed ones inherit the new", () => {
  const prev = rules.jscAuthorTailoring(tailoring({ excludes: [{ ref: REQ }], operations: [op1, op2] }), null, ALICE);
  /* bob keeps the select, the exclude and op1, changes the value of op2's target and adds an operation */
  const op2b = { ...op2, modality: "should" }, op3 = { op: "set-parameter", "requirement-ref": REQ, "statement-id": "s3", parameter: "q", value: "x" };
  const out = rules.jscAuthorTailoring(tailoring({ excludes: [{ ref: REQ }], operations: [op1, op2b, op3] }), prev, BOB);
  assert.deepEqual(out.provenance, BOB);
  assert.deepEqual(out.selects[0].provenance, ALICE, "the select was alice's decision");
  assert.deepEqual(out.excludes[0].provenance, ALICE);
  assert.deepEqual(out.operations[0].provenance, ALICE, "op1 is unchanged");
  assert.equal("provenance" in out.operations[1], false, "a changed operation is bob's");
  assert.equal("provenance" in out.operations[2], false, "a new operation is bob's");
  isType("tailoring", out);
  /* a third author: what bob decided is now written as bob's, and alice's stays alice's */
  const CAROL = { "author-ref": O + "/party/carol", date: "2026-12-01" };
  const third = rules.jscAuthorTailoring(tailoring({ excludes: [{ ref: REQ }], operations: [op1, op2b, op3] }), out, CAROL);
  assert.deepEqual(third.provenance, CAROL);
  assert.deepEqual(third.operations.map(o => o.provenance), [ALICE, BOB, BOB]);
  assert.deepEqual([third.selects[0].provenance, third.excludes[0].provenance], [ALICE, ALICE]);
  /* who decided an entry is the entry's provenance, else the Tailoring's: asked of the three versions, op1 always answers alice */
  const who = (t, e) => e.provenance || t.provenance;
  for (const t of [prev, out, third]) assert.deepEqual(who(t, t.operations[0]), ALICE);
});

test("a Tailoring, saved again by the same author on the same day: nothing is written onto the entries", () => {
  const prev = rules.jscAuthorTailoring(tailoring({ operations: [op1] }), null, ALICE);
  const out = rules.jscAuthorTailoring(tailoring({ operations: [op1, op2] }), prev, ALICE);
  assert.deepEqual(out.provenance, ALICE);
  assert.ok(out.operations.every(o => !("provenance" in o)) && !("provenance" in out.selects[0]));
});

test("a Tailoring: the same author on a later day is a change of the Tailoring's provenance, and the earlier day stays on what was decided then", () => {
  const later = { ...ALICE, date: "2026-11-20" };
  const prev = rules.jscAuthorTailoring(tailoring({ operations: [op1] }), null, ALICE);
  const out = rules.jscAuthorTailoring(tailoring({ operations: [op1, op2] }), prev, later);
  assert.deepEqual(out.operations.map(o => o.provenance), [ALICE, undefined]);
  assert.deepEqual(out.provenance, later);
});

test("a Tailoring: an entry's own provenance is never dropped, whether the form carries it or not", () => {
  const own = { "author-ref": O + "/party/ops", date: "2026-10-01" };
  const prev = tailoring({ provenance: ALICE, operations: [{ ...op1, provenance: own }, op2] });
  /* the form knows nothing of the entry's provenance */
  const out = rules.jscAuthorTailoring(tailoring({ operations: [op1, op2] }), prev, BOB);
  assert.deepEqual(out.operations.map(o => o.provenance), [own, ALICE]);
  /* the form carries it */
  const out2 = rules.jscAuthorTailoring(tailoring({ operations: [{ ...op1, provenance: own }] }), prev, BOB);
  assert.deepEqual(out2.operations[0].provenance, own);
  /* saved without an author */
  const out3 = rules.jscAuthorTailoring(tailoring({ operations: [op1, op2] }), prev, null);
  assert.deepEqual(out3.operations.map(o => o.provenance), [own, ALICE]);
});

test("a Tailoring saved without an author: no provenance on the Tailoring; what others decided keeps their names; the new entry names nobody (AUTHOR-1 reports it)", async () => {
  const prev = rules.jscAuthorTailoring(tailoring({ operations: [op1] }), null, ALICE);
  const out = rules.jscAuthorTailoring(tailoring({ operations: [op1, op2] }), prev, null);
  assert.equal("provenance" in out, false);
  assert.deepEqual(out.selects[0].provenance, ALICE);
  assert.deepEqual(out.operations.map(o => o.provenance), [ALICE, undefined]);
  isType("tailoring", out);
  /* the report line: one of two operations names no author */
  const objs = new Map([[out.id, { type: "tailoring", obj: out }]]);
  const report = await rules.jscAuthorReport(objs);
  assert.deepEqual(report.map(e => [e.rule, e.count]), [["AUTHOR-1", 1]]);
  assert.match(report[0].message, /1 of 2 operation\(s\) name no author/);
  /* and without any author ever: the object the page built, unchanged */
  const bare = tailoring({ operations: [op1] });
  assert.deepEqual(rules.jscAuthorTailoring(bare, null, null), bare);
  assert.deepEqual(rules.jscAuthorTailoring(bare, bare, null), bare);
});

test("a Tailoring: deciding the Deviation of an operation does not make the operation somebody else's", () => {
  const dev = { type: "operational-requirement", state: "pending", rationale: { en: "The legacy host cannot." }, "approver-ref": O + "/party/ciso", opened: "2026-11-03" };
  const weak = { op: "set-modality", "requirement-ref": REQ, "statement-id": "s2", modality: "should", deviation: dev };
  const prev = rules.jscAuthorTailoring(tailoring({ operations: [weak] }), null, ALICE);
  const approved = { ...weak, deviation: rules.jscDecideDeviation(dev, "approved", "2026-11-13", { type: "date", value: "2027-05-13" }) };
  const out = rules.jscAuthorTailoring(tailoring({ operations: [approved] }), prev, BOB);
  assert.deepEqual(out.operations[0].provenance, ALICE, "the weakening was alice's; the approval is recorded on the Deviation");
  assert.deepEqual(out.operations[0].deviation.decided, "2026-11-13");
  isType("tailoring", out);
});

test("a Tailoring: a decision recorded on a stored Deviation is not undone by a save from a form that still holds the Deviation as it was", () => {
  const dev = { type: "operational-requirement", state: "pending", rationale: { en: "The legacy host cannot." }, "approver-ref": O + "/party/ciso", opened: "2026-11-03" };
  const weak = { op: "set-modality", "requirement-ref": REQ, "statement-id": "s2", modality: "should", deviation: dev };
  const decided = rules.jscDecideDeviation(dev, "approved", "2026-11-13", { type: "date", value: "2027-05-13" });
  const stored = tailoring({ provenance: ALICE, operations: [{ ...weak, deviation: decided }] });
  /* the form was filled before the approval and is saved again, with one more operation */
  const out = rules.jscAuthorTailoring(tailoring({ operations: [weak, op1] }), stored, BOB);
  assert.deepEqual(out.operations[0].deviation, decided, "the approval, its day and its review date stand");
  assert.deepEqual(out.operations[0].provenance, ALICE);
  /* an investigating Deviation that was withdrawn in the meantime stays withdrawn */
  const asked = { ...weak, deviation: { ...dev, state: "investigating" } }, gone = rules.jscDecideDeviation(asked.deviation, "withdrawn", "2026-11-12", null);
  assert.deepEqual(rules.jscAuthorTailoring(tailoring({ operations: [asked] }), tailoring({ operations: [{ ...weak, deviation: gone }] }), BOB).operations[0].deviation, gone);
  /* the other way round the form wins: the decision is what is being saved */
  const fresh = rules.jscAuthorTailoring(tailoring({ operations: [{ ...weak, deviation: decided }] }), tailoring({ provenance: ALICE, operations: [weak] }), BOB);
  assert.deepEqual(fresh.operations[0].deviation, decided);
  /* another request on the same operation (a new rationale) is the form's: nothing of the stored decision is carried to it */
  const again = { ...weak, deviation: { ...dev, rationale: { en: "Another reason." } } };
  assert.deepEqual(rules.jscAuthorTailoring(tailoring({ operations: [again] }), stored, BOB).operations[0].deviation, again.deviation);
  /* a day added to a Deviation that was approved without one is a change of the form, and is kept */
  const undated = { ...dev, state: "approved" }, dated = rules.jscDecideDeviation(undated, "approved", "2026-06-01", null);
  assert.deepEqual(rules.jscAuthorTailoring(tailoring({ operations: [{ ...weak, deviation: dated }] }), tailoring({ operations: [{ ...weak, deviation: undated }] }), BOB).operations[0].deviation, dated);
});

const rating = (level, extra) => ({ level, "scale-ref": O + "/scale/level", ...extra });
const risk = extra => ({ id: O + "/risk/r", version: "1", lifecycle: "draft", scenario: { en: "Something fails." }, "owner-ref": O + "/party/ciso", state: "identified", ...extra });

test("a Risk: the author on the Risk, and on a rating when it is set or changed; an unchanged rating keeps what it had", () => {
  /* alice writes the risk and rates it */
  const v1 = rules.jscAuthorRisk(risk({ rating: rating("high") }), null, ALICE);
  assert.deepEqual([v1.provenance, v1.rating.provenance], [ALICE, ALICE]);
  isType("risk", v1);
  /* bob changes the title only: the Risk is bob's version, the rating is still alice's decision */
  const v2 = rules.jscAuthorRisk({ ...copy(v1), title: { en: "A title" } }, v1, BOB);
  assert.deepEqual([v2.provenance, v2.rating.provenance], [BOB, ALICE]);
  /* bob adds a residual rating: that one is bob's */
  const v3 = rules.jscAuthorRisk({ ...copy(v2), "residual-rating": rating("low") }, v2, BOB);
  assert.deepEqual([v3.rating.provenance, v3["residual-rating"].provenance], [ALICE, BOB]);
  /* carol changes the rating: hers now; the residual stays bob's */
  const CAROL = { "author-ref": O + "/party/carol", date: "2026-12-01" };
  const v4 = rules.jscAuthorRisk({ ...copy(v3), rating: { ...copy(v3.rating), level: "medium" } }, v3, CAROL);
  assert.deepEqual([v4.provenance, v4.rating.provenance, v4["residual-rating"].provenance], [CAROL, CAROL, BOB]);
  isType("risk", v4);
});

test("a Risk: a rating without provenance of its own had the Risk's, and keeps it when the Risk gets a new author", () => {
  /* written by hand, or imported: the author stands on the Risk only */
  const prev = risk({ provenance: ALICE, rating: rating("high"), "residual-rating": rating("low") });
  const out = rules.jscAuthorRisk({ ...copy(prev), title: { en: "A title" } }, prev, BOB);
  assert.deepEqual([out.provenance, out.rating.provenance, out["residual-rating"].provenance], [BOB, ALICE, ALICE]);
  /* the same author and day: nothing has to be written onto the rating */
  const same = rules.jscAuthorRisk({ ...copy(prev), title: { en: "A title" } }, prev, ALICE);
  assert.equal("provenance" in same.rating, false);
});

test("a Risk saved without an author: no provenance on the Risk; a changed rating names nobody, an unchanged one keeps its author", () => {
  const v1 = rules.jscAuthorRisk(risk({ rating: rating("high"), "residual-rating": rating("low") }), null, ALICE);
  const next = copy(v1); next.rating.level = "medium";
  const out = rules.jscAuthorRisk(next, v1, null);
  assert.equal("provenance" in out, false);
  assert.equal("provenance" in out.rating, false, "a level alice did not choose must not carry her name");
  assert.deepEqual(out["residual-rating"].provenance, ALICE);
  isType("risk", out);
  const bare = risk({ rating: rating("high") });
  assert.deepEqual(rules.jscAuthorRisk(bare, null, null), bare, "no author ever: the object as the page built it");
});

test("a Deviation: `decided` is written when it becomes approved or withdrawn, with the day the form states; a review date only on an approved one", () => {
  const dev = { type: "risk-adjustment", state: "pending", rationale: { en: "Accepted for one year." }, "approver-ref": O + "/party/ciso", opened: "2026-11-03" };
  const D = rules.jscDecideDeviation;
  const approved = D(dev, "approved", "2026-11-13", { type: "date", value: "2027-11-13" });
  assert.deepEqual(approved, { ...dev, state: "approved", decided: "2026-11-13", "review-due": { type: "date", value: "2027-11-13" } });
  assert.deepEqual(rules.jscSchemaCheck(SCHEMA.$defs.deviation, approved, SCHEMA).errors, []);
  assert.equal(dev.state, "pending", "the argument is not changed");
  assert.deepEqual(D(dev, "withdrawn", "2026-11-13", { type: "date", value: "2027-11-13" }), { ...dev, state: "withdrawn", decided: "2026-11-13" }, "a withdrawn Deviation has nothing to review");
  assert.deepEqual(D(dev, "approved", "2026-11-13", null), { ...dev, state: "approved", decided: "2026-11-13" }, "the review date is optional");
  /* a state that is no decision gets no day; a day that is no date is not written (AUTHOR-3 reports it) */
  assert.deepEqual(D({ ...dev, state: "investigating" }, "pending", "2026-11-13", null), dev);
  assert.deepEqual(D(dev, "approved", "", null), { ...dev, state: "approved" });
  assert.deepEqual(D(dev, "approved", "13.11.2026", null), { ...dev, state: "approved" });
  /* the state machine is the kernel's: approved and withdrawn are final */
  assert.throws(() => D(approved, "pending", "2026-11-14", null), /may not move/);
  assert.throws(() => D(dev, "investigating", "2026-11-14", null), /may not move/);
  /* a decided Deviation that says no day yet may be given one, and its state stays */
  const old = { ...dev, state: "approved" };
  assert.deepEqual(D(old, "approved", "2026-06-01", null), { ...old, decided: "2026-06-01" });
});

test("the export pins kernel 2.0.0 for everything these functions write, as KERNEL-1 asks", () => {
  const impl = { id: O + "/impl/x", version: "1", lifecycle: "draft", "component-ref": O + "/comp/c", "requirement-ref": REQ, responsibility: "provider",
    "satisfied-by": [{ "capability-ref": "cap-r-1" }], status: "planned" };
  const finding = { id: O + "/finding/f", version: "1", lifecycle: "draft", "assessment-ref": O + "/asmt/a", "requirement-ref": REQ, state: "open" };
  const dev = { type: "risk-adjustment", state: "pending", rationale: { en: "x" }, "approver-ref": O + "/party/ciso", opened: "2026-11-03" };
  const cases = {
    "an Implementation with provenance": [["implementation", rules.jscAuthorRecord(impl, BOB)]],
    "a Finding with provenance": [["finding", rules.jscAuthorRecord(finding, BOB)]],
    "a Tailoring with provenance": [["tailoring", rules.jscAuthorTailoring(tailoring({ operations: [op1] }), null, BOB)]],
    "a Tailoring whose entries carry it and the Tailoring does not": [["tailoring", rules.jscAuthorTailoring(tailoring({ operations: [op1, op2] }),
      rules.jscAuthorTailoring(tailoring({ operations: [op1] }), null, ALICE), null)]],
    "a Finding whose Deviation is decided": [["finding", { ...finding, deviations: [rules.jscDecideDeviation(dev, "approved", "2026-11-13", null)] }]],
    "a Finding whose Deviation has a review date only": [["finding", { ...finding, deviations: [{ ...dev, "review-due": { type: "date", value: "2027-01-01" } }] }]],
    "a Tailoring whose inline Deviation is decided": [["tailoring", tailoring({ operations: [{ ...op2, modality: "should", deviation: rules.jscDecideDeviation(dev, "withdrawn", "2026-11-13", null) }] })]],
    "none of it": [["implementation", impl], ["finding", finding], ["tailoring", tailoring({ operations: [op1] })]],
  };
  for (const [name, list] of Object.entries(cases)) {
    for (const [type, obj] of list) isType(type, obj);
    const objs = new Map(list.map(([type, obj]) => [obj.id, { type, obj }]));
    const asked = rules.jscKernelNeeded(objs, null)[0] === "2.0.0";
    assert.equal(asked, name !== "none of it", name);
    assert.equal(core.jscNeedsKernel2({ scales: new Map(), objects: objs }), asked, name);
  }
});
