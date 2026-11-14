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
  // the converter's own counts: lists packed into one comma-separated value are reported; the {{Label}}
  // slots of the sentence template are parameters, every one where the prose inserts a parameter
  const packed = {};
  for (const d of out.report["packed-list-values"]) packed[d.prop] = (packed[d.prop] || 0) + 1;
  assert.deepEqual(packed, { tags: 125, threats: 616, target_object_categories: 40 });
  assert.equal(out.report["parameter-slots"], 221);
  assert.deepEqual(out.report["parameter-slots-not-at-insert"], []);
});

test("generic rules: NIST SP 800-53 becomes valid kernel objects whose references close", { skip: missing(NIST_SRC) }, () => {
  const src = json(NIST_SRC);
  assert.equal(oscal.jscOscalGuessPreset(src), "nist-sp800-53", "the catalog has a preset of its own; the generic rules are run here on purpose");
  const out = oscal.jscOscalImportCatalog(src, { preset: "generic", ns: "https://example.org/fw/sp800-53", lang: "en", key: "sp800-53", party: "organization" });
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

/* Backlog #70. The kernel requires on every statement who it binds (`obligated-parties`), and OSCAL has no field
   for it. Until build 0.9.10 the generic rules wrote <namespace>/party/organization on every clause: a party nobody
   had named. Now the caller names it, and without one the import does not run. Needs no source file. */
test("generic rules: the party the statements bind is the caller's; without one the import is refused, and no party is made up", () => {
  const src = cisSynthetic(), base = { preset: "generic", ns: "https://org.example/fw/x", lang: "en", key: "x" };
  const parties = out => [...new Set(out.objects.filter(o => o.obj.statements).flatMap(o => o.obj.statements.flatMap(s => s["obligated-parties"])))];
  /* a URI is written as it is, on every clause */
  const named = oscal.jscOscalImportCatalog(src, { ...base, party: "https://publisher.example/party/operator" });
  assert.deepEqual(parties(named), ["https://publisher.example/party/operator"]);
  assert.equal(named.objects.filter(o => o.obj.statements).length, 5);
  assert.equal(rules.jscTypedObjects(named.objects.map(o => o.obj)).size, named.objects.length, "every object is one kernel type");
  /* a short name becomes a party under the namespace of the import, by the rule every page uses */
  assert.deepEqual(parties(oscal.jscOscalImportCatalog(src, { ...base, party: "System Administrator" })), ["https://org.example/fw/x/party/system-administrator"]);
  /* nothing named: refused with the reason, whatever "nothing" looks like */
  for (const nothing of [undefined, null, "", "   ", "!!!"]) {
    assert.throws(() => oscal.jscOscalImportCatalog(src, { ...base, party: nothing }), /names no party the statements bind.*the kernel requires obligated-parties/, JSON.stringify(nothing));
  }
  /* the word the rules used to supply is gone: it appears only when the caller types it */
  assert.equal(JSON.stringify(named.objects).includes("/party/organization"), false);
  /* the presets for a publisher's corpus follow their converters and take no party from the caller */
  const cis = oscal.jscOscalImportCatalog(src, { preset: "cis-benchmark", party: "https://publisher.example/party/operator" });
  assert.deepEqual(parties(cis), ["https://ns.cisecurity.org/benchmark/ubuntu-24.04-lts/party/system-administrator"]);
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

/* ---------- who wrote an OSCAL document, and when (backlog #69) ----------
   The rule is stated once, in jascon-oscal.js above jscOscalAuthorParty, and
   the Python converters are written to the same text. The table below is
   the rule's own; a change here is a change of the rule. A and B are
   persons, O and P organisations, all with names; N is defined without a
   name; X is not defined. */
const PARTY = { A: { uuid: "uuid-a", type: "person", name: "Alice Example" }, B: { uuid: "uuid-b", type: "person", name: "Bob Example" },
  O: { uuid: "uuid-o", type: "organization", name: "Example Agency" }, P: { uuid: "uuid-p", type: "organization", name: "Example Provider Inc." },
  N: { uuid: "uuid-n", type: "person" }, X: { uuid: "uuid-x", type: "person", name: "Not Defined" } };
const metaOf = (rp, parties) => ({ title: "t", "last-modified": "2026-11-05T14:30:00+01:00",
  ...(rp ? { "responsible-parties": rp.map(([role, who]) => ({ "role-id": role, "party-uuids": who.map(k => PARTY[k].uuid) })) } : {}),
  ...(parties ? { parties: parties.map(k => PARTY[k]) } : {}) });
const AUTHOR_TABLE = [
  ["creator names A, a contact is B", [["creator", ["A"]], ["contact", ["B"]]], ["A", "B"], "A"],
  ["prepared-by names A, the owner is B", [["prepared-by", ["A"]], ["owner", ["B"]]], ["A", "B"], "A"],
  ["two creators, one prepared-by", [["creator", ["A", "B"]], ["prepared-by", ["B"]]], ["A", "B"], "B"],
  ["no creator, no prepared-by, one party in all roles", [["assessor", ["A"]]], ["A", "B"], "A"],
  ["two parties in roles, one organisation defined", [["owner", ["A"]], ["developer", ["B"]]], ["A", "B", "O"], "O"],
  ["two parties in roles, no organisation", [["owner", ["A"]], ["developer", ["B"]]], ["A", "B"], null],
  ["two parties in roles, two organisations", [["owner", ["A"]], ["developer", ["B"]]], ["A", "B", "O", "P"], null],
  ["no responsible parties, one party", null, ["A"], "A"],
  ["no responsible parties, two persons", null, ["A", "B"], null],
  ["no responsible parties, two persons and one organisation", null, ["A", "B", "O"], "O"],
  ["no parties at all", [["creator", ["A"]]], null, null],
  ["the creator is not defined, one party is", [["creator", ["X"]]], ["A"], "A"],
  ["the one party in a role has no name", [["assessor", ["N"]]], ["N"], null],
];
test("the author of an OSCAL document: the rule's own table", () => {
  for (const [name, rp, parties, want] of AUTHOR_TABLE) {
    const got = oscal.jscOscalAuthorParty(metaOf(rp, parties));
    assert.equal(got ? got.uuid : null, want ? PARTY[want].uuid : null, name);
  }
  assert.equal(AUTHOR_TABLE.length, 13);
});
test("the author of an OSCAL document: what the table does not say", () => {
  const A = PARTY.A, B = PARTY.B, O = PARTY.O, N = PARTY.N;
  const who = meta => { const p = oscal.jscOscalAuthorParty(meta); return p ? p.uuid : null; };
  /* several entries of one role are united, and a uuid named twice counts once */
  assert.equal(who({ parties: [A, B], "responsible-parties": [{ "role-id": "creator", "party-uuids": [A.uuid] }, { "role-id": "creator", "party-uuids": [A.uuid] }] }), A.uuid);
  assert.equal(who({ parties: [A, B], "responsible-parties": [{ "role-id": "creator", "party-uuids": [A.uuid] }, { "role-id": "creator", "party-uuids": [B.uuid] }] }), null, "two creators, and all roles together name two");
  /* creator comes before prepared-by */
  assert.equal(who({ parties: [A, B], "responsible-parties": [{ "role-id": "prepared-by", "party-uuids": [B.uuid] }, { "role-id": "creator", "party-uuids": [A.uuid] }] }), A.uuid);
  /* an undefined uuid is dropped before the count, in every step */
  assert.equal(who({ parties: [A, B], "responsible-parties": [{ "role-id": "creator", "party-uuids": [A.uuid, PARTY.X.uuid] }] }), A.uuid);
  assert.equal(who({ parties: [A, B], "responsible-parties": [{ "role-id": "owner", "party-uuids": [B.uuid] }, { "role-id": "contact", "party-uuids": [PARTY.X.uuid] }] }), B.uuid);
  /* a party without a name ends the rule where it lands: no later step is tried */
  assert.equal(who({ parties: [N, O], "responsible-parties": [{ "role-id": "creator", "party-uuids": [N.uuid] }] }), null, "step 1 lands on a nameless party; the organisation of step 4 is not taken");
  assert.equal(who({ parties: [N, A], "responsible-parties": [{ "role-id": "creator", "party-uuids": [N.uuid] }, { "role-id": "prepared-by", "party-uuids": [A.uuid] }] }), null, "a nameless creator ends the rule: prepared-by is not asked");
  assert.equal(who({ parties: [N, O], "responsible-parties": [{ "role-id": "owner", "party-uuids": [N.uuid] }] }), null, "step 2 lands on it; the organisation of step 4 is not taken");
  assert.equal(who({ parties: [N] }), null, "step 3 lands on it");
  assert.equal(who({ parties: [A, B, { uuid: "uuid-q", type: "organization" }] }), null, "step 4 lands on it");
  /* a uuid defined twice is one party, and its first definition is the party: oscal_conv_lib.py and this file gave
     different answers here when 4,000 generated documents were put to both (2026-11-14) */
  assert.equal(who({ parties: [A, { ...A }] }), A.uuid, "the same party twice is the one party the document defines");
  assert.equal(who({ parties: [A, { uuid: A.uuid, type: "person" }] }), A.uuid, "of two definitions the first counts");
  assert.equal(who({ parties: [{ uuid: A.uuid, type: "person" }, A] }), null, "the first counts also when it has no name");
  assert.equal(who({ parties: [{ type: "organization", name: "Nameless Ltd" }, A] }), A.uuid, "an entry without a uuid is no party");
  assert.equal(who({ parties: [{ ...A, name: "" }] }), null, "an empty name is no name");
  /* what is not there is not there */
  for (const meta of [undefined, null, {}, { parties: [] }, { parties: "x" }, { parties: [A], "responsible-parties": "x" }]) assert.doesNotThrow(() => who(meta), JSON.stringify(meta));
  assert.equal(who({ parties: [A], "responsible-parties": [{ "role-id": "creator" }] }), A.uuid, "an entry without party-uuids names nobody; step 3 finds the one party");
});
test("the author of an OSCAL document as a URI, and the day: the party's name under the namespace of the import; the first ten characters of last-modified", () => {
  const meta = metaOf([["creator", ["A"]]], ["A", "B"]);
  assert.equal(oscal.jscOscalAuthorRef(meta, "https://org.example"), "https://org.example/party/alice-example");
  assert.equal(oscal.jscOscalAuthorRef(meta, "https://org.example/"), "https://org.example/party/alice-example", "a namespace is used without its closing slash");
  assert.equal(oscal.jscOscalAuthorRef(metaOf(null, ["A", "B", "P"]), "https://org.example"), "https://org.example/party/example-provider-inc");
  assert.equal(oscal.jscOscalAuthorRef(metaOf(null, ["A", "B"]), "https://org.example"), null);
  assert.equal(oscal.jscOscalDate(meta), "2026-11-05");
  assert.equal(oscal.jscOscalDate({ "last-modified": "2026-11-05T00:30:00+02:00" }), "2026-11-05", "the day as the document writes it: the offset is not applied, although in UTC this is the 4th");
  assert.equal(oscal.jscOscalDate({ "last-modified": "2026-11-05T23:30:00-05:00" }), "2026-11-05", "nor here, where in UTC it is the 6th");
  assert.equal(oscal.jscOscalDate({ "last-modified": "2026-11-05" }), "2026-11-05");
  for (const bad of [undefined, null, "", "2026-13-05T00:00:00Z", "05.11.2026", "2026-11-5T00:00:00Z", 20261105, "yesterday"]) assert.equal(oscal.jscOscalDate({ "last-modified": bad }), null, JSON.stringify(bad));
  assert.equal(oscal.jscOscalDate(undefined), null);
});

/* a set of three requirements and their root Set, and a profile over it */
function profileFixture(metadata) {
  const P = "https://a.example";
  const req = id => ({ id: `${P}/req/${id}`, version: "1", lifecycle: "active", statements: [{ id: "s1", modality: "must", "obligated-parties": [P + "/p"],
    prose: { en: "X {param:" + id.toLowerCase() + "_prm_1}." }, parameters: [{ name: id.toLowerCase() + "_prm_1", type: "string" }] }] });
  const list = [req("AC-1"), req("AC-2"), req("AC-3")];
  const root = { id: P + "/set/tax/root", version: "1", lifecycle: "active", members: list.map(r => ({ ref: r.id })) };
  const objs = new Map([...list, root].map(o => [o.id, { type: core.jscInferType(o), obj: o }]));
  const profile = { profile: { uuid: "x", metadata: { title: "My Profile", version: "2", ...metadata },
    imports: [{ href: "#cat", "include-controls": [{ "with-ids": ["ac-1", "ac-2"] }], "exclude-controls": [{ "with-ids": ["ac-3"] }] }],
    modify: { "set-parameters": [{ "param-id": "ac-1_prm_1", values: ["90 days"] }] } } };
  return { profile, objs, opts: { ns: "https://org.example", lang: "en", objs, catalogSet: null } };
}
test("profile: the Tailoring names the document's author and day; the caller's author and day replace them field by field; none without both", () => {
  const meta = metaOf([["creator", ["A"]], ["contact", ["B"]]], ["A", "B"]);
  const ALICE = "https://org.example/party/alice-example", ME = "https://org.example/party/me";
  const run = (metadata, extra) => { const f = profileFixture(metadata); const out = oscal.jscOscalImportProfile(f.profile, { ...f.opts, ...extra }); return { out, t: out.objects.find(o => o.obj.selects).obj }; };
  const plain = run(meta, {});
  assert.deepEqual(plain.t.provenance, { "author-ref": ALICE, date: "2026-11-05" });
  assert.deepEqual(plain.out.report.provenance, { stated: { "author-ref": ALICE, date: "2026-11-05" }, given: {}, records: { "from-source": 1, "from-caller": 0, none: 0 } });
  assert.deepEqual(rules.jscMatchTypes(plain.t), ["tailoring"]);
  /* the author stands once on the Tailoring; its entries inherit it and carry none of their own */
  for (const e of [...plain.t.selects, ...(plain.t.excludes || []), ...plain.t.operations]) assert.equal("provenance" in e, false);
  assert.ok(plain.t.operations.length === 1 && plain.t.excludes.length === 1);
  /* the Set of the profile is a RequirementSet: the kernel has no provenance on it, and none is written */
  assert.ok(plain.out.objects.filter(o => o.obj.members).every(o => !("provenance" in o.obj)));
  /* what the page shows before the import is what the import writes when nothing is typed over it */
  const f = profileFixture(meta);
  assert.deepEqual(oscal.jscOscalStated(f.profile, f.opts), { applies: true, "author-ref": ALICE, date: "2026-11-05", party: "Alice Example" });
  /* field by field */
  assert.deepEqual(run(meta, { authorRef: ME }).t.provenance, { "author-ref": ME, date: "2026-11-05" });
  assert.deepEqual(run(meta, { date: "2026-11-13" }).t.provenance, { "author-ref": ALICE, date: "2026-11-13" });
  const both = run(meta, { authorRef: ME, date: "2026-11-13" });
  assert.deepEqual(both.t.provenance, { "author-ref": ME, date: "2026-11-13" });
  assert.deepEqual(both.out.report.provenance, { stated: { "author-ref": ALICE, date: "2026-11-05" }, given: { "author-ref": ME, date: "2026-11-13" }, records: { "from-source": 0, "from-caller": 1, none: 0 } });
  /* no provenance without both: the source names nobody, or no day, or the caller says nobody */
  const anonymous = run(metaOf(null, ["A", "B"]), {});
  assert.equal("provenance" in anonymous.t, false);
  assert.deepEqual(anonymous.out.report.provenance, { stated: { "author-ref": null, date: "2026-11-05" }, given: {}, records: { "from-source": 0, "from-caller": 0, none: 1 } });
  assert.deepEqual(rules.jscMatchTypes(anonymous.t), ["tailoring"], "a Tailoring without an author is a Tailoring");
  assert.equal("provenance" in run({ ...meta, "last-modified": "last week" }, {}).t, false, "an author without a day");
  assert.equal("provenance" in run(meta, { authorRef: "" }).t, false, "the caller says nobody");
  assert.equal("provenance" in run(metaOf(null, ["A", "B"]), { authorRef: ME }).t, true, "the caller names the author the source does not");
  assert.equal("provenance" in run({ title: "t" }, { authorRef: ME }).t, false, "an author and no day, from anywhere");
  assert.deepEqual(run({ title: "t" }, { authorRef: ME, date: "2026-11-13" }).t.provenance, { "author-ref": ME, date: "2026-11-13" });
  assert.throws(() => run(meta, { date: "13.11.2026" }), /is not a date, YYYY-MM-DD/);
  /* at consumer tier the report line appears exactly where the import wrote no author */
  const line = async t => (await rules.jscAuthorReport(new Map([...profileFixture(meta).objs, [t.id, { type: "tailoring", obj: t }]]))).map(e => e.rule);
  return Promise.all([line(plain.t), line(anonymous.t)]).then(([a, b]) => { assert.deepEqual(a, []); assert.deepEqual(b, ["AUTHOR-1"]); });
});

test("CIS preset: a Mapping keeps the author and day it had; the caller may replace either; a Mapping is never written without both", () => {
  const src = cisSynthetic(), NS = "https://ns.cisecurity.org/benchmark/ubuntu-24.04-lts", ME = "https://org.example/party/me";
  const maps = out => out.objects.filter(o => o.path.startsWith("objects/map/")).map(o => o.obj.provenance);
  const plain = oscal.jscOscalImportCatalog(src, { preset: "cis-benchmark" });
  assert.deepEqual(maps(plain), Array(4).fill({ "author-ref": NS + "/party/cis", date: "2026-11-11" }));
  assert.deepEqual(plain.report.provenance, { stated: { "author-ref": NS + "/party/cis", date: "2026-11-11" }, given: {}, records: { "from-source": 4, "from-caller": 0, none: 0 } });
  assert.deepEqual(oscal.jscOscalStated(src, { preset: "cis-benchmark" }), { applies: true, "author-ref": NS + "/party/cis", date: "2026-11-11", party: null });
  /* the document-author rule is not asked here: a party of the catalog's metadata does not become the author of CIS's cross-references */
  const withParty = cisSynthetic();
  withParty.catalog.metadata.parties = [PARTY.A];
  assert.deepEqual(maps(oscal.jscOscalImportCatalog(withParty, { preset: "cis-benchmark" }))[0], { "author-ref": NS + "/party/cis", date: "2026-11-11" });
  /* field by field */
  assert.deepEqual(maps(oscal.jscOscalImportCatalog(src, { preset: "cis-benchmark", authorRef: ME })), Array(4).fill({ "author-ref": ME, date: "2026-11-11" }));
  const dated = oscal.jscOscalImportCatalog(src, { preset: "cis-benchmark", date: "2026-11-13" });
  assert.deepEqual(maps(dated), Array(4).fill({ "author-ref": NS + "/party/cis", date: "2026-11-13" }));
  assert.deepEqual(dated.report.provenance.records, { "from-source": 0, "from-caller": 4, none: 0 });
  assert.equal(rules.jscTypedObjects(dated.objects.map(o => o.obj)).size, dated.objects.length, "every object is one kernel type");
  /* a catalog without a day: the caller's day lets the import go ahead; without one it is refused as before */
  const undated = cisSynthetic();
  delete undated.catalog.metadata["last-modified"];
  assert.deepEqual(maps(oscal.jscOscalImportCatalog(undated, { preset: "cis-benchmark", date: "2026-11-13" })), Array(4).fill({ "author-ref": NS + "/party/cis", date: "2026-11-13" }));
  assert.throws(() => oscal.jscOscalImportCatalog(undated, { preset: "cis-benchmark" }), /last-modified does not begin with a date.*DATE-3/);
  /* the kernel requires provenance on a Mapping, so "nobody" cannot be written: refused with the reason */
  assert.throws(() => oscal.jscOscalImportCatalog(src, { preset: "cis-benchmark", authorRef: "" }), /a Mapping needs its author/);
  assert.throws(() => oscal.jscOscalImportCatalog(src, { preset: "cis-benchmark", date: "" }), /last-modified does not begin with a date|a Mapping needs its author/);
  /* the other catalog rules write no record that can carry provenance, and say so */
  const generic = oscal.jscOscalImportCatalog(src, { preset: "generic", ns: "https://org.example/fw/x", lang: "en", key: "x", party: "https://org.example/party/operator", authorRef: ME, date: "2026-11-13" });
  assert.deepEqual(generic.report.provenance.records, { "from-source": 0, "from-caller": 0, none: 0 });
  assert.ok(generic.objects.every(o => !("provenance" in o.obj)));
  assert.equal(oscal.jscOscalStated(src, { preset: "generic", ns: "https://org.example/fw/x" }).applies, false);
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
   must carry the semantic digest the converter's manifest states.

   Until 2026-11-13 both wrote the catalog's version as the
   `provenance.date` of a Mapping, which kernel 2.0.0 refuses since it holds
   that field to a date (DATE-3; ERRATA.md). Both now write the day of the
   catalog's `last-modified`, and the digests agree without exception. */
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
/* ERRATA 2026-11-13: the preset wrote the catalog's version as the date of a
   Mapping's provenance; since kernel 2.0.0 types that date (DATE-3), such a
   Mapping matches no type. Needs no converter and no source file. */
test("ERRATA 2026-11-13 (DATE-3): a CIS import dates its Mappings with the day of the catalog's last-modified, never with its version", () => {
  const src = cisSynthetic(), out = oscal.jscOscalImportCatalog(src, { preset: "cis-benchmark" });
  const maps = out.objects.filter(o => o.path.startsWith("objects/map/"));
  assert.equal(maps.length, 4);
  assert.equal(src.catalog.metadata["last-modified"], "2026-11-11T00:00:00Z");
  for (const m of maps) assert.equal(m.obj.provenance.date, "2026-11-11", m.path);
  assert.deepEqual(maps.flatMap(m => rules.jscDateRuleViolations(m.obj)), []);
  assert.equal(rules.jscTypedObjects(out.objects.map(o => o.obj)).size, out.objects.length, "every object is one kernel type");
  /* without a date to give, the cross-references are refused with the reason; a catalog that has none imports */
  const undated = cisSynthetic();
  delete undated.catalog.metadata["last-modified"];
  assert.throws(() => oscal.jscOscalImportCatalog(undated, { preset: "cis-benchmark" }), /last-modified does not begin with a date.*DATE-3/);
  for (const g of undated.catalog.groups) for (const sub of [g, ...(g.groups || [])]) for (const c of sub.controls || []) c.parts = c.parts.filter(p => p.class !== "CIS_Controls");
  assert.equal(oscal.jscOscalImportCatalog(undated, { preset: "cis-benchmark" }).objects.filter(o => o.path.startsWith("objects/map/")).length, 0);
});
test("CIS preset: the namespace is the converter's for its benchmark and derived from the title for any other", () => {
  assert.equal(oscal.jscCisNamespace({ metadata: { title: "CIS Ubuntu Linux 24.04 LTS Benchmark" } }), "https://ns.cisecurity.org/benchmark/ubuntu-24.04-lts");
  assert.equal(oscal.jscCisNamespace({ metadata: { title: "CIS Red Hat Enterprise Linux 9 Benchmark v2.0.0" } }), "https://ns.cisecurity.org/benchmark/red-hat-enterprise-linux-9");
  const own = oscal.jscOscalImportCatalog(cisSynthetic(), { preset: "cis-benchmark", ns: "https://example.org/cis" });
  assert.ok(own.objects.every(o => o.obj.id.startsWith("https://example.org/cis/")), "a namespace chosen on the page is used");
});
