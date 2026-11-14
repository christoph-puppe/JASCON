/* Holds one-page-apps/jascon-reader.html to the kernel pin of the reference
   and to what CP-AUTHOR-1 (specification D26) asks of a tool that shows and
   writes who decided and when (backlog #69).

   In node, on the part of the page between its READER-PURE markers, read out
   of the HTML file as it is (the page has no build step and no second copy):
   1. The 19 pin vectors of conformance/kernel-vectors.json: the page's pin
      test gives the reference's number of failures for each, with the
      fragments the vector names in the message.
   2. One case per reason kernel_needed (validate_core.py) knows, and the
      cases that must not ask for the pin. The number of reasons is counted in
      the reference's source: a reason added there turns this test red until
      the page has it and a case holds it. Where python3 is present, the
      reference's own function is run on the same objects and on the object
      sets of the kernel and author vectors, and must give the page's answer.
   3. Who decided an entry: its own provenance, else its record's, else nobody.
      What a save writes: an unchanged record keeps the author it names, and
      an unchanged entry of a Tailoring does not change hands with it.

   In Chromium, driving the page:
   4. jascon/examples, whose objects name their authors: every field is shown
      where it is, and an entry without its own is marked as inherited.
   5. The IFA bundle, whose objects name an author in some places and none
      in others: each place shows what its file says, and the places that say
      "not stated" are those the reference reports (AUTHOR-2 to AUTHOR-4).
   6. The workbenches: without an author nothing is refused, no provenance is
      written and the export pins no kernel; with one, a Tailoring, an
      Implementation and a Finding carry it and the export pins 2.0.0. A
      second author does not take over what the first decided. The exports
      pass validate_core.py, those with authors under --require-authors.
   7. A bundle whose content needs the pin and has none is shown and reported
      (KERNEL-1); at a pin the page does not read, nothing is shown (KERNEL-2).
      Both also for a bundle loaded from a URL with a deep link.
   8. Pasted objects: Deviations in every state with a review date of every
      shape, a Risk whose ratings differ in who decided them, authorizations
      with and without a day. Each is written out as recorded.

   9. A party the kernel requires (backlog #70, "refuse if no party is
      named"): whom a statement binds, the author of a Mapping, the performer
      of an Assessment, the approver of a Deviation. For each, an empty field
      writes nothing and says which field the kernel requires, and a named
      party is written as named. An approver field starts empty for every
      Deviation; a Mapping does not take another form's performer.
  10. The performer starts from the author and from no word, stays once it
      is typed, and is empty once somebody emptied it; the word an earlier
      version stored as performer is no party.
   In node as well: a name becomes a party, an empty field names nobody, and
   the page mints a party in one place only.

  11. What an Attestation binds of a bundle (backlog #46; Appendix B.1.7). In
      node: the 19 binds vectors of conformance/attestation-vectors.json give
      the reference's verdict, manifest, subjects and failure; the line the
      page prints is the one binds_report prints, for every vector; an
      envelope is read as the keyless part of verify_envelope reads it, and
      is never called valid. In Chromium: jascon/examples, the IFA bundle and
      the worked advice pack, loaded as they lie, show for every Attestation
      the line the reference prints, and so do changed copies of them; the
      Attestations beside a manifest are found from a folder, from files and
      from a URL (a listing, names in the link, or neither, which the page
      says); they are counted apart from the objects the manifest lists; an
      export never lists one.
  12. MANIFEST-1 (backlog #75; specification D3.11): no content manifest
      lists an Attestation. In node: the eight listed vectors, with the
      reference's sentence, and the reference's own function on the same
      objects. In Chromium: copies of the IFA bundle, the worked pack and the
      example folder whose manifests list an Attestation fail on the page
      with the reference's sentence, and the Attestation is still held to
      what it binds; what the page says can be done is done on the copy and
      holds in the reference.

  13. An Assessment's method is a facet payload (backlog #55; specification
      D10 as amended). In node: of the thirteen method vectors the page
      decides the ten that turn on where a key is registered, in the
      reference's words, and names the three it cannot decide (a payload
      against its schema: the page carries no schema validator); the
      reference's own facet_errors on the same objects. In Chromium: what
      the Assess workbench writes and its export in the reference; bundles
      and a stored workspace that hold the method an earlier version wrote,
      shown as stored and not rewritten, and what the page says can be done.

   Needs Playwright with Chromium for 4 to 13 and python3 with jsonschema for
   the runs of the reference; where one is missing, that part is skipped and
   says so. Needs no network: the one thing the page asks the web for, its
   font stylesheet, is answered here with an empty one. */
import test from "node:test";
import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { createRequire } from "node:module";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const READER = path.join(ROOT, "one-page-apps/jascon-reader.html");
const VALIDATE = path.join(ROOT, "jascon/scripts/validate_core.py");
const require = createRequire(import.meta.url);
let chromium = null;
try { ({ chromium } = require("playwright")); } catch (e) { /* skipped below */ }
const SKIP = !chromium && "Playwright with Chromium is not installed";
const PYTHON = spawnSync("python3", ["-c", "import json"]).status === 0;
const REFERENCE = PYTHON && spawnSync("python3", ["-c", "import jsonschema"]).status === 0;
const json = rel => JSON.parse(fs.readFileSync(path.join(ROOT, rel), "utf8"));

/* ---------- the pure part of the page, as the page carries it ---------- */
const HTML = fs.readFileSync(READER, "utf8");
const P = (() => {
  const a = HTML.indexOf("/* ==READER-PURE-START== */"), b = HTML.indexOf("/* ==READER-PURE-END== */");
  assert.ok(a >= 0 && b > a, "jascon-reader.html carries the READER-PURE markers");
  return new Function(`"use strict";\n${HTML.slice(a, b)}\nreturn { inferType, kernelNeeded, kernelPinErrors, whoDecided, authorRecord, authorTailoring, partyUri, requiredParty,
    canonical, sha256Fallback, semanticDigest, attestationBinds, bindsLine, envelopeState, listedAttestationErrors,
    STDLIB_FACETS, facetHome, methodKeyErrors, facetKeyErrors, closureNeedErrors, manualMethod, isEarlierWorkbenchMethod };`)();
})();

/* ---------- 1. the pin vectors ---------- */
test("the pin: each of the 19 kernel vectors gets the reference's number of failures from the page's own test", () => {
  const v = json("jascon/conformance/kernel-vectors.json").vectors;
  assert.equal(v.length, 19);   // a vector added to the family is looked at here before this number moves (18 until #68 added the pin that ends in a line break)
  for (const c of v) {
    for (const o of c.objects) assert.ok(![null, "manifest"].includes(P.inferType(o)), `${c.name}: ${o.id} is typed`);
    const errs = P.kernelPinErrors(c.manifest, c.objects);
    assert.equal(errs.length, c["expected-fails"] || 0, `${c.name}: ${errs.join(" | ")}`);
    for (const frag of c["expected-frags"] || []) assert.ok(errs.some(e => e.includes(frag)), `${c.name}: the message names '${frag}': ${errs.join(" | ")}`);
  }
});

/* ---------- 2. one case per reason ---------- */
const EX = "https://org.example";
const REQ = { id: `${EX}/req/1`, version: "1", lifecycle: "active", statements: [{ id: "s1", modality: "should", "obligated-parties": [`${EX}/party/o`], prose: { en: "X." } }] };
const SET = { id: `${EX}/set/base`, version: "1", lifecycle: "active", members: [{ ref: REQ.id, sequence: 10 }] };
const TAILORING = { id: `${EX}/tailoring/t`, version: "1", lifecycle: "active", selects: [{ "set-ref": SET.id }] };
const MAPPING = { id: `${EX}/map/m`, version: "1", lifecycle: "active", "source-ref": REQ.id, "target-ref": "https://other.example/req/9", relationship: "supports",
  direction: "source-to-target", confidence: "draft", provenance: { "author-ref": `${EX}/party/ciso`, date: "2026-11-05" } };
const COMPONENT = { id: `${EX}/component/c`, version: "1", lifecycle: "active", kind: "system" };
const IMPLEMENTATION = { id: `${EX}/impl/i`, version: "1", lifecycle: "active", "component-ref": COMPONENT.id, "requirement-ref": REQ.id, responsibility: "customer",
  "satisfied-by": [{ "capability-ref": "cap" }], status: "implemented" };
const ASSESSMENT = { id: `${EX}/assessment/a`, version: "1", lifecycle: "active", "subject-refs": [REQ.id], method: { "https://ns.jascon.net/stdlib/facet/assessment-criteria@1": { method: "manual" } }, "performer-ref": `${EX}/party/assessor`,
  time: "2026-11-05", result: "satisfied" };
const FINDING = { id: `${EX}/finding/f`, version: "1", lifecycle: "active", "assessment-ref": ASSESSMENT.id, "requirement-ref": REQ.id, state: "open" };
const ATTESTATION = json("jascon/examples/attestation-acme-2026.json");
const RISK = { id: `${EX}/risk/R-1`, version: "1", lifecycle: "active", scenario: { en: "Scenario." }, "owner-ref": `${EX}/party/ciso`, state: "identified" };
const CHECK = json("jascon/examples/check-acme-ssh-ciphers.json");
const ROW = json("jascon/examples/assessment-acme-bastion-2026-11-10.json")["check-results"][0];
const WHO = { "author-ref": `${EX}/party/ciso`, date: "2026-11-05" };
const DEVIATION = { type: "operational-requirement", state: "approved", rationale: { en: "The legacy host cannot." }, "approver-ref": `${EX}/party/ciso`, opened: "2026-11-01" };
const REVIEW = { type: "date", value: "2027-05-12" };
const OP = { op: "set-modality", "requirement-ref": REQ.id, "statement-id": "s1", modality: "must" };

/* [the reason, by its place in kernel_needed; what the case is; the objects; the manifest]. Reason 0: 1.0.0 content. */
const CASES = [
  [1, "a manifest that pins a scale definition", [REQ], { "manifest-version": "1", scales: [{ id: `${EX}/scale/s`, "exact-version": "1", digest: "sha256:" + "0".repeat(64), path: "scale.json" }] }],
  [2, "a manifest with a pack header", [COMPONENT], { "manifest-version": "1", pack: { id: `${EX}/pack/p`, version: "1", publisher: { ref: `${EX}/party/vendor` } } }],
  [3, "a Risk", [RISK]],
  [4, "a Finding with risk-refs", [{ ...FINDING, "risk-refs": [RISK.id] }]],
  [5, "a Check", [CHECK]],
  [6, "an Assessment with check-results", [{ ...ASSESSMENT, "check-results": [ROW] }]],
  [6, "an Assessment with a tailoring-ref", [{ ...ASSESSMENT, "tailoring-ref": TAILORING.id }]],
  [7, "a Finding with a check-ref", [{ ...FINDING, "check-ref": CHECK.id }]],
  [8, "a Component whose capability names clauses (statement-ids)", [{ ...COMPONENT, capabilities: [{ id: "cap", "requirement-ref": REQ.id, "statement-ids": ["s1"] }] }]],
  [9, "a Component with a product-version", [{ ...COMPONENT, "product-version": "7.2" }]],
  [9, "a Component with an empty product-version: the field is there", [{ ...COMPONENT, "product-version": "" }]],
  [10, "a Tailoring with provenance", [{ ...TAILORING, provenance: WHO }]],
  [10, "an Implementation with provenance", [{ ...IMPLEMENTATION, provenance: WHO }]],
  [10, "a Finding with provenance", [{ ...FINDING, provenance: WHO }]],
  [11, "a select with provenance", [{ ...TAILORING, selects: [{ "set-ref": SET.id, provenance: WHO }] }]],
  [11, "an exclude with provenance", [{ ...TAILORING, excludes: [{ ref: REQ.id, provenance: WHO }] }]],
  [11, "an operation with provenance", [{ ...TAILORING, operations: [{ ...OP, provenance: WHO }] }]],
  [12, "a Deviation with `decided` in the list of a Requirement", [{ ...REQ, deviations: [{ ...DEVIATION, decided: "2026-11-03" }] }]],
  [12, "a Deviation with `review-due` in the list of a Finding", [{ ...FINDING, deviations: [{ ...DEVIATION, "review-due": REVIEW }] }]],
  [12, "a Deviation with `decided` inline on an operation", [{ ...TAILORING, operations: [{ ...OP, modality: "may", deviation: { ...DEVIATION, decided: "2026-11-03" } }] }]],
  [12, "a Deviation with `review-due` inline on an operation", [{ ...TAILORING, operations: [{ ...OP, modality: "may", deviation: { ...DEVIATION, "review-due": REVIEW } }] }]],
  [13, "a Component with a dated authorization", [{ ...COMPONENT, authorizations: [{ id: "ato-1", "authority-ref": `${EX}/party/ao`, date: "2026-06-30" }] }]],
  [0, "one of each type the 1.0.0 kernel has, a Mapping with its provenance among them",
    [REQ, SET, TAILORING, MAPPING, { ...COMPONENT, authorizations: [{ id: "ato-1", "authority-ref": `${EX}/party/ao` }], capabilities: [{ id: "cap", "requirement-ref": REQ.id }] },
      IMPLEMENTATION, ASSESSMENT, FINDING, ATTESTATION]],
  [0, "Deviations that say neither `decided` nor `review-due`, in a list and inline",
    [{ ...FINDING, deviations: [DEVIATION] }, { ...TAILORING, operations: [{ ...OP, modality: "may", deviation: DEVIATION }], deviations: [DEVIATION] }]],
  [0, "lists that are there and empty: risk-refs, check-results, statement-ids", [{ ...FINDING, "risk-refs": [] }, { ...ASSESSMENT, "check-results": [] },
    { ...COMPONENT, capabilities: [{ id: "cap", "statement-ids": [] }] }]],
  [0, "no object at all, under a manifest that pins nothing", [], { "manifest-version": "1", objects: [], scales: [] }],
];

/* The reference's function, run by Python on objects typed by the page. Its
   source is taken out of validate_core.py by name, because the script as a
   whole runs the conformance corpus when it is loaded. -> [version] */
function referenceNeeds(cases) {
  const py = `
import ast, json, sys
src = open(sys.argv[1], encoding="utf-8").read()
ns = {}
for node in ast.parse(src).body:
    if isinstance(node, ast.FunctionDef) and node.name in ("deviations_of", "kernel_needed"):
        exec(compile(ast.Module([node], []), sys.argv[1], "exec"), ns)
out = [ns["kernel_needed"]({i: (t, o) for i, t, o in c["objs"]}, c.get("manifest"))[0] for c in json.load(sys.stdin)]
print(json.dumps(out))`;
  const run = spawnSync("python3", ["-c", py, VALIDATE], { input: JSON.stringify(cases), encoding: "utf8" });
  assert.equal(run.status, 0, run.stderr.slice(-1500));
  return JSON.parse(run.stdout);
}
const typed = objs => objs.map(o => [o.id, P.inferType(o), o]);

test("the pin: one case for every reason kernel_needed knows, and none where the content is 1.0.0", () => {
  /* how many reasons the reference has: the returns of "2.0.0" in kernel_needed */
  const src = fs.readFileSync(VALIDATE, "utf8"), at = src.indexOf("\ndef kernel_needed(");
  assert.ok(at >= 0, "validate_core.py has kernel_needed");
  const body = src.slice(at + 1, src.indexOf("\ndef ", at + 1));
  const reasons = (body.match(/return "2\.0\.0"/g) || []).length;
  assert.deepEqual([...new Set(CASES.map(c => c[0]).filter(Boolean))].sort((a, b) => a - b), Array.from({ length: reasons }, (_, i) => i + 1),
    `kernel_needed returns "2.0.0" in ${reasons} places; there is a case here for each, numbered in its order`);
  for (const [reason, what, objs, manifest] of CASES) {
    for (const o of objs) assert.ok(![null, "manifest"].includes(P.inferType(o)), `${what}: ${o.id} is typed`);
    const [need, why] = P.kernelNeeded(objs, manifest || null);
    assert.equal(need, reason ? "2.0.0" : "1.0.0", `${what}${why ? ": " + why : ""}`);
    assert.equal(why === null, !reason, `${what}: a reason is named exactly when the pin is needed`);
    /* the pin rule on the same content: unpinned it fails once (KERNEL-1) exactly when 2.0.0 is needed; pinned it passes */
    const m = manifest || { "manifest-version": "1", objects: [] };
    assert.equal(P.kernelPinErrors(m, objs).length, reason ? 1 : 0, what);
    assert.deepEqual(P.kernelPinErrors({ ...m, "kernel-version": "2.0.0" }, objs), [], what + ", pinned");
  }
});

test("the pin: the reference's own kernel_needed gives the page's answer, on these cases and on the object sets of the kernel and author vectors",
  { skip: !PYTHON && "python3 is not installed" }, () => {
    const k = json("jascon/conformance/kernel-vectors.json"), a = json("jascon/conformance/author-vectors.json");
    const sets = [...CASES.map(([, what, objs, manifest]) => ({ what, objs, manifest })),
      ...k.vectors.map(c => ({ what: c.name, objs: c.objects, manifest: c.manifest })),
      ...k["shape-vectors"].filter(c => c.expected === "valid").map(c => ({ what: c.name, objs: [c.document] })),
      ...[...a["author-vectors"], ...a["review-vectors"]].map(c => ({ what: c.name, objs: c.objects }))];
    for (const s of sets) for (const o of s.objs) assert.ok(![null, "manifest"].includes(P.inferType(o)), `${s.what}: ${o.id} is typed`);
    const ref = referenceNeeds(sets.map(s => ({ objs: typed(s.objs), manifest: s.manifest || null })));
    assert.equal(ref.length, sets.length);
    sets.forEach((s, i) => assert.equal(P.kernelNeeded(s.objs, s.manifest || null)[0], ref[i], s.what));
    assert.ok(ref.includes("1.0.0") && ref.includes("2.0.0"), "both answers occur");
  });

/* ---------- 3. who decided ---------- */
test("who decided an entry: its own provenance, else its record's, else nobody", () => {
  const own = { "author-ref": `${EX}/party/ops`, date: "2026-11-12" };
  assert.deepEqual(P.whoDecided({ provenance: own }, { provenance: WHO }), { ref: own["author-ref"], date: "2026-11-12", from: "own" });
  assert.deepEqual(P.whoDecided({}, { provenance: WHO }), { ref: WHO["author-ref"], date: "2026-11-05", from: "record" });
  assert.equal(P.whoDecided({}, {}), null);
  assert.equal(P.whoDecided({ "owner-ref": `${EX}/party/ciso`, "approver-ref": `${EX}/party/ciso` }, null), null, "an owner or an approver is not an author");
  assert.deepEqual(P.whoDecided({ provenance: WHO }), { ref: WHO["author-ref"], date: "2026-11-05", from: "own" }, "a record alone");
});

test("what a save writes: an unchanged record keeps its author and day; an unchanged entry of a Tailoring does not change hands; nobody is invented", () => {
  const A = { "author-ref": `${EX}/party/ciso`, date: "2026-11-05" }, B = { "author-ref": `${EX}/party/ops`, date: "2026-11-12" };
  /* a record: new, unchanged, changed, and saved by nobody */
  assert.deepEqual(P.authorRecord(IMPLEMENTATION, A, undefined).provenance, A, "a new record names who wrote it");
  assert.deepEqual(P.authorRecord(IMPLEMENTATION, B, { ...IMPLEMENTATION, provenance: A }).provenance, A, "written again unchanged, it is the version it was");
  assert.deepEqual(P.authorRecord({ ...IMPLEMENTATION, status: "partial" }, B, { ...IMPLEMENTATION, provenance: A }).provenance, B, "changed, it is the version of who changed it");
  assert.equal("provenance" in P.authorRecord({ ...IMPLEMENTATION, status: "partial" }, null, { ...IMPLEMENTATION, provenance: A }), false, "changed by nobody, it names nobody");
  assert.equal("provenance" in P.authorRecord(IMPLEMENTATION, null, IMPLEMENTATION), false, "nobody is invented");
  assert.deepEqual(P.authorRecord(IMPLEMENTATION, B, IMPLEMENTATION).provenance, B, "a record that named nobody gets the author of this save");
  assert.equal("provenance" in IMPLEMENTATION, false, "the object handed in is not written on");

  /* a Tailoring by A with a select and an operation; B adds an exclude and saves */
  const first = P.authorTailoring({ ...TAILORING, operations: [OP] }, undefined, A);
  assert.deepEqual([first.provenance, first.selects[0].provenance, first.operations[0].provenance], [A, undefined, undefined], "the first save: the entries have the Tailoring's");
  const second = P.authorTailoring({ ...TAILORING, operations: [OP], excludes: [{ ref: REQ.id }] }, first, B);
  assert.deepEqual(second.provenance, B, "the Tailoring names who wrote this version");
  assert.deepEqual([second.selects[0].provenance, second.operations[0].provenance], [A, A], "what A decided stays A's: it is written onto the entries before the Tailoring changes hands");
  assert.equal("provenance" in second.excludes[0], false, "the new entry carries none and so has B's");
  /* B changes the operation: it is B's decision now */
  const third = P.authorTailoring({ ...TAILORING, operations: [{ ...OP, modality: "may" }], excludes: [{ ref: REQ.id }] }, second, B);
  assert.equal("provenance" in third.operations[0], false, "a changed operation is decided by who changed it");
  assert.deepEqual(third.selects[0].provenance, A);
  /* the same author on the same day writes nothing onto the entries; a Deviation attached later does not make the operation another's */
  assert.deepEqual(P.authorTailoring({ ...TAILORING, operations: [OP] }, first, A), first);
  assert.deepEqual(P.authorTailoring({ ...TAILORING, operations: [{ ...OP, deviation: DEVIATION }] }, first, B).operations[0].provenance, A);
  /* saved by nobody: the Tailoring names nobody, and the entries keep who decided them */
  const fourth = P.authorTailoring({ ...TAILORING, operations: [OP] }, first, null);
  assert.equal("provenance" in fourth, false);
  assert.deepEqual([fourth.selects[0].provenance, fourth.operations[0].provenance], [A, A]);
  /* a Tailoring that named nobody: there is nothing to keep, and its entries become the new author's with it */
  const unsigned = P.authorTailoring({ ...TAILORING, operations: [OP] }, undefined, null);
  assert.equal(JSON.stringify(unsigned).includes("provenance"), false);
  assert.equal(JSON.stringify(P.authorTailoring({ ...TAILORING, operations: [OP] }, unsigned, A).operations).includes("provenance"), false);
});

/* The sentences a workbench shows where the kernel requires a party and nobody named one (backlog #70). */
const REFUSED = {
  mapping: "author is empty — the kernel requires a Mapping to name its author (provenance.author-ref); no Mapping was written",
  assessment: "performer is empty — the kernel requires an Assessment to name who performed it (performer-ref); no Assessment and no Finding was written",
  deviation: "approver is empty — the kernel requires a Deviation to name who approves it (approver-ref); the operation was not added",
  statement: "party is empty — the kernel requires a statement to name whom it binds (obligated-parties); no Requirement was written",
};

test("a party a person named: a URI as typed, a name under the namespace; an empty field names nobody, and the refusal says which field the kernel requires", () => {
  const NS = "https://example.org/my";
  assert.equal(P.partyUri("https://cso.example/party/ciso", NS), "https://cso.example/party/ciso", "a URI is taken as typed");
  assert.equal(P.partyUri("urn:example:party:ciso", NS), "urn:example:party:ciso");
  assert.equal(P.partyUri("  Head of Security ", NS + "/"), NS + "/party/head-of-security", "a name the person typed is a party the person named");
  for (const nobody of ["", "   ", null, undefined, "?!", "—"]) assert.equal(P.partyUri(nobody, NS), "", JSON.stringify(nobody) + " names nobody");
  for (const [kind, sentence] of Object.entries(REFUSED)) {
    assert.deepEqual(P.requiredParty(kind, "Head of Security", NS), { ref: NS + "/party/head-of-security" }, kind);
    for (const empty of ["", "  ", null, undefined]) assert.deepEqual(P.requiredParty(kind, empty, NS), { refused: sentence }, kind);
    assert.match(P.requiredParty(kind, "?!", NS).refused, /"\?!" names no party \(a URI, or a name with a letter a-z or a digit, does\) — the kernel requires /, kind);
    /* none of the words the page once wrote for an empty field comes back, in the party or in its place */
    for (const typed of ["", "?!"]) assert.equal("ref" in P.requiredParty(kind, typed, NS), false, kind);
  }
  /* The page mints a party in one place, partyUri, from what a field holds. A default word that becomes a party
     would need a second place or a fallback beside a field, and neither is in the page's script. */
  const script = HTML.slice(HTML.indexOf("<script>"));
  assert.equal(script.split('"/party/"').length - 1, 1, 'the string "/party/" stands once in the script, in partyUri');
  assert.deepEqual(script.match(/\|\|\s*"(assessor|ciso|approver|author|organisation)"/g), null, "no fixed word stands in for an empty field");
});

/* ---------- the page in a browser ---------- */
async function open() {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "jascon-reader-"));
  const browser = await chromium.launch();
  const context = await browser.newContext({ acceptDownloads: true, viewport: { width: 1500, height: 1100 } });
  await context.route(/^https:/, route => route.fulfill({ status: 200, contentType: "text/css", body: "" }));   // the font stylesheet; a test does not wait on the web
  const page = await context.newPage();
  const errors = [], answers = [], quiet = [];
  /* a script error on any page of the test is held against it; prompt() takes the next answer a test queued.
     `quiet`: URLs a test expects the server to refuse (a folder on a server that lists none): the browser writes
     such a refusal to its console as an error, and only for these it is not one of the page's. */
  const watch = p => {
    p.on("pageerror", e => errors.push("pageerror: " + e.message));
    p.on("console", m => { if (m.type() === "error" && !(/\b404\b/.test(m.text()) && quiet.some(re => re.test(m.location().url)))) errors.push(`console: ${m.text()} ${m.location().url}`); });
    p.on("dialog", d => d.type() === "prompt" ? d.accept(answers.length ? answers.shift() : "") : d.accept());
    return p;
  };
  watch(page);
  await page.goto(pathToFileURL(READER).href);
  /* a folder, opened as the button does (or files, as "Open JSON file(s)" does); done when the page has indexed
     it (or has stopped at it) and has held every Attestation to it */
  const load = async (dir, pick = "#folderpick") => {
    const lines = await page.locator("#log > div").count();
    await page.setInputFiles(pick, dir);
    await page.waitForFunction(n => [...document.querySelectorAll("#log > div")].slice(n)
      .some(x => /indexed \d+ objects|nothing of this bundle is shown/.test(x.textContent)) && document.body.dataset.binds === "done", lines);
  };
  /* What stage 5 says about every Attestation, in the order shown: the verdict and what it means for the bundle,
     the line, every subject, the manifest bound, the envelope. */
  const attested = async (p = page) => {
    await p.click('.navitem[data-view="stage:assess"]');
    return p.locator("#view-stagefn [data-attestation]").evaluateAll(cards => cards.map(x => ({
      id: x.dataset.attestation, verdict: x.dataset.binds, manifest: x.dataset.bindsManifest ?? null, fails: x.dataset.bindsFails ?? null,
      word: x.querySelector("[data-binds-word]")?.textContent ?? null, shownAs: x.querySelector("[data-binds-word]")?.className ?? null,
      line: x.querySelector("[data-binds-line]")?.textContent ?? null,
      subjects: [...x.querySelectorAll("[data-subject]")].map(tr => ({ status: tr.dataset.subject, id: tr.querySelector(".reflink")?.textContent ?? null,
        signed: tr.querySelector("[data-signed]").textContent, delivered: tr.querySelector("[data-delivered]").textContent })),
      envelope: x.querySelector("[data-envelope]").dataset.envelope, envelopeText: x.querySelector("[data-envelope]").textContent,
      listed: x.dataset.listed ?? null, listedError: x.querySelector("[data-listed-error]")?.textContent ?? null,
      todo: x.querySelector("[data-binds-todo]")?.textContent ?? null })));
  };
  const view = async v => { await page.click(`.navitem[data-view="${v}"]`); };
  /* an object, opened from the list of the object browser */
  const detail = async id => { await view("browser"); await page.locator(`.objrow[data-id="${id}"]`).click(); return page.locator("#detail"); };
  const text = async loc => (await loc.innerText()).replace(/\s+/g, " ").trim();
  /* the line that says who decided `of` ("record", "operations[0]", "rating") inside `root`: [own | record | none, its text] */
  const who = async (root, of) => { const l = root.locator(`[data-who-of="${of}"]`); assert.equal(await l.count(), 1, `one line for ${of}`); return [await l.getAttribute("data-who"), await text(l)]; };
  const log = async () => page.locator("#log").innerText();
  const download = async click => {
    const [d] = await Promise.all([page.waitForEvent("download"), page.click(click)]);
    const file = path.join(tmp, d.suggestedFilename());
    await d.saveAs(file);
    return file;
  };
  const finish = async () => assert.deepEqual(errors, [], "no script error on the page");
  const shutdown = async () => { await browser.close(); fs.rmSync(tmp, { recursive: true, force: true }); };
  /* over every object of the bundle, opened one by one: how many lines name somebody, and how many places say that nobody, no day decided or no date is stated */
  const sweep = async () => {
    await view("browser");
    const n = { named: 0, nobody: 0, undecided: 0, undated: 0 };
    for (const id of await page.locator(".objrow").evaluateAll(l => l.map(x => x.dataset.id))) {
      const d = await detail(id);
      n.named += await d.locator('[data-who="own"], [data-who="record"]').count();
      n.nobody += await d.locator('[data-who="none"]').count();
      n.undecided += await d.locator('[data-decided="none"]').count();
      n.undated += await d.locator('[data-auth-date="none"]').count();
    }
    return n;
  };
  return { page, tmp, load, view, detail, text, who, log, download, finish, shutdown, watch, answers, sweep, quiet, attested };
}
/* The browser is closed whether the test passes or fails. */
async function withReader(fn) {
  const R = await open();
  try { await fn(R); await R.finish(); } finally { await R.shutdown(); }
}
const OPTS = { skip: SKIP, timeout: 120000 };

/* The files of a ZIP as the page writes it (stored, not compressed), written under `dir`. -> the bundle folder */
function unzipTo(file, dir) {
  const buf = fs.readFileSync(file);
  let end = buf.length - 22;
  while (end >= 0 && buf.readUInt32LE(end) !== 0x06054b50) end--;
  assert.ok(end >= 0, "a ZIP");
  let p = buf.readUInt32LE(end + 16), top = null;
  for (let i = 0; i < buf.readUInt16LE(end + 10); i++) {
    assert.equal(buf.readUInt16LE(p + 10), 0, "stored");
    const size = buf.readUInt32LE(p + 24), nl = buf.readUInt16LE(p + 28), at = buf.readUInt32LE(p + 42);
    const name = buf.subarray(p + 46, p + 46 + nl).toString("utf8");
    const data = at + 30 + buf.readUInt16LE(at + 26) + buf.readUInt16LE(at + 28);
    fs.mkdirSync(path.dirname(path.join(dir, name)), { recursive: true });
    fs.writeFileSync(path.join(dir, name), buf.subarray(data, data + size));
    top = name.split("/")[0];
    p += 46 + nl + buf.readUInt16LE(p + 30) + buf.readUInt16LE(p + 32);
  }
  return path.join(dir, top);
}
/* validate_core.py on one bundle folder -> { ok, line: the bundle's line, notes: what it printed about the bundle } */
function reference(dir, ...flags) {
  const run = spawnSync("python3", [VALIDATE, dir, ...flags], { encoding: "utf8" });
  const lines = run.stdout.split("\n"), from = lines.indexOf("== bundles =="), at = lines.findIndex(l => l.includes(path.basename(path.dirname(dir)) + "/" + path.basename(dir) + ":"));
  assert.ok(from >= 0 && at > from, "the reference reports the bundle: " + run.stdout.slice(-1500));
  return { ok: run.status === 0 && /^ALL GREEN$/m.test(run.stdout), line: lines[at], notes: lines.slice(from + 1, at), out: run.stdout };
}

/* The repository (under /repo/) and the test's temporary folder (under /tmp/) over http. `folders` says what a
   request for a folder gets: "listing", a page of links as python's http.server and a static site's index.html give
   it; "page", some other page (a site that answers every unknown address with its start page); or nothing, a 404. */
async function serve(R, folders) {
  const server = http.createServer((req, res) => {
    const u = decodeURIComponent(new URL(req.url, "http://localhost").pathname);
    const file = u.startsWith("/repo/") ? path.join(ROOT, u.slice(6)) : u.startsWith("/tmp/") ? path.join(R.tmp, u.slice(5)) : "";
    const html = body => { res.writeHead(200, { "content-type": "text/html; charset=utf-8" }); res.end(body); };
    if (file && folders && fs.existsSync(file) && fs.statSync(file).isDirectory()) {
      return html(folders === "page" ? '<!doctype html><title>Home</title><a href="about.html">About</a> <a href="notes.json">Notes</a>'
        : "<ul>" + fs.readdirSync(file).sort().map(n => `<li><a href="${encodeURIComponent(n)}${fs.statSync(path.join(file, n)).isDirectory() ? "/" : ""}">${n}</a></li>`).join("") + "</ul>");
    }
    if (!file || !fs.existsSync(file) || !fs.statSync(file).isFile()) { res.writeHead(404); res.end(); return; }
    res.writeHead(200, { "content-type": file.endsWith(".html") ? "text/html; charset=utf-8" : "application/json" });
    res.end(fs.readFileSync(file));
  });
  await new Promise(done => server.listen(0, "127.0.0.1", done));
  const at = `http://127.0.0.1:${server.address().port}`;
  /* the address under which this server has a folder of the repository or of the temporary folder */
  const url = dir => `${at}/${dir.startsWith(R.tmp) ? "tmp/" + path.relative(R.tmp, dir) : "repo/" + path.relative(ROOT, dir)}`.split(path.sep).join("/") + "/";
  return { at, url, reader: `${at}/repo/one-page-apps/jascon-reader.html`, close: () => server.close() };
}

/* One object against the kernel schema, as the reference builds its validator per type. -> [what is wrong] */
function kernelErrors(type, obj) {
  const py = `
import json, sys, jsonschema
s = json.load(open(sys.argv[1], encoding="utf-8"))
v = jsonschema.validators.Draft202012Validator({"$ref": "#/$defs/" + sys.argv[2], "$defs": s["$defs"]})
print(json.dumps([e.message for e in v.iter_errors(json.load(sys.stdin))]))`;
  const run = spawnSync("python3", ["-c", py, path.join(ROOT, "jascon/schemas/jascon-2.0.0.schema.json"), type], { input: JSON.stringify(obj), encoding: "utf8" });
  assert.equal(run.status, 0, run.stderr.slice(-1500));
  return JSON.parse(run.stdout);
}

const EXAMPLES = path.join(ROOT, "jascon/examples");
const IFA = path.join(ROOT, "converted_examples/US.IFA-GoodRead/ifa-core-bundle");

test("the example folder names its authors: every record and entry shows who decided and when, an entry without its own as inherited", OPTS, () => withReader(async R => {
  const { page } = R;
  await R.load(EXAMPLES);
  const CISO = "https://cso.example/party/ciso";

  /* a Tailoring by one author with one operation by another */
  let d = await R.detail("https://cso.example/tailoring/linux-prod");
  assert.deepEqual(await R.who(d, "record"), ["own", `${CISO} · 2026-11-02`]);
  assert.deepEqual(await R.who(d, "selects[0]"), ["record", `${CISO} · 2026-11-02 inherited from the Tailoring`]);
  assert.deepEqual(await R.who(d, "operations[0]"), ["own", "https://cso.example/party/platform-ops · 2026-11-02"]);
  assert.equal(await d.locator("[data-inherited]").count(), 1, "one entry of this Tailoring is marked as inherited, the select");

  /* a Tailoring whose two operations name nobody of their own */
  d = await R.detail("https://ns.bsi.bund.de/gspp/tailoring/erhoeht");
  const REDAKTION = "https://ns.bsi.bund.de/gspp/party/redaktion · 2026-07-01";
  assert.deepEqual(await R.who(d, "record"), ["own", REDAKTION]);
  for (const of of ["selects[0]", "operations[0]", "operations[1]"]) assert.deepEqual(await R.who(d, of), ["record", REDAKTION + " inherited from the Tailoring"], of);

  /* a Risk: its own author, a rating by somebody else, a residual rating that has the Risk's */
  d = await R.detail("https://cso.example/risk/R-2026-007");
  assert.deepEqual(await R.who(d, "record"), ["own", `${CISO} · 2026-11-05`]);
  assert.deepEqual(await R.who(d, "rating"), ["own", "https://cso.example/party/secops · 2026-10-28"]);
  assert.deepEqual(await R.who(d, "residual-rating"), ["record", `${CISO} · 2026-11-05 inherited from the Risk`]);

  /* a Finding with an approved Deviation: decided, and due for review */
  d = await R.detail("https://assessor.example/finding/2026-q3-acme-017");
  assert.deepEqual(await R.who(d, "record"), ["own", "https://assessor.example/party/lead-assessor · 2026-07-18"]);
  const dev = d.locator('[data-deviation="deviations[0]"]');
  assert.equal(await R.text(dev.locator("[data-decided]")), "2026-07-18");
  assert.equal(await dev.locator("[data-decided]").getAttribute("data-decided"), "stated");
  assert.equal(await R.text(dev.locator("[data-review]")), "2027-07-18");
  assert.equal(await dev.locator("[data-review]").getAttribute("data-review"), "stated");

  d = await R.detail("https://cso.example/impl/acme--konf-14-1");
  assert.deepEqual(await R.who(d, "record"), ["own", "https://cso.example/party/platform-ops · 2026-07-10"]);

  /* an authorization with its day */
  d = await R.detail("https://paas.example/component/platform");
  const auth = d.locator('[data-authorization="https://paas.example/auth/jab-moderate-2026"]');
  assert.equal(await R.text(auth.locator("[data-auth-date]")), "2026-03-15");
  assert.equal(await auth.locator("[data-auth-date]").getAttribute("data-auth-date"), "stated");

  /* over all objects of the folder: no place says that nobody is named, as the reference prints no AUTHOR line for it */
  assert.deepEqual(await R.sweep(), { named: 14, nobody: 0, undecided: 0, undated: 0 });
  if (REFERENCE) assert.deepEqual(reference(EXAMPLES).notes.filter(l => /\(AUTHOR-/.test(l)), []);

  /* What the page shows first does not depend on the order in which the files of a folder arrive. That order is
     the operating system's: the workflow's runner listed the folder otherwise than the machine this test was
     written on, the page showed the other Tailoring first, and the assertion below failed there (2026-11-14).
     The same files, handed over in reverse, give the same order on the page. */
  const pills = async () => { await R.view("stage:tailor"); return page.locator(".fpill[data-tsel]").evaluateAll(l => l.map(x => x.dataset.tsel)); };
  const asLoaded = await pills();
  assert.deepEqual(asLoaded, ["https://cso.example/tailoring/linux-prod", "https://ns.bsi.bund.de/gspp/tailoring/erhoeht"], "Tailorings in the order of their paths");
  await page.evaluate(async () => { await loadFileList([...document.getElementById("folderpick").files].reverse()); });
  assert.deepEqual(await pills(), asLoaded, "the same files in reverse order: the same order on the page");

  /* the stage views say the same, in short */
  const stage = page.locator("#view-stagefn");
  await R.view("stage:tailor");
  assert.deepEqual(await R.who(stage, "record"), ["own", "ciso · 2026-11-02"]);
  assert.deepEqual(await R.who(stage, "operations[0]"), ["own", "platform-ops · 2026-11-02"]);
  await page.locator('[data-tsel="https://ns.bsi.bund.de/gspp/tailoring/erhoeht"]').click();
  for (const of of ["operations[0]", "operations[1]"]) assert.deepEqual(await R.who(stage, of), ["record", "redaktion · 2026-07-01 inherited"], of);
  await R.view("stage:implement");
  assert.deepEqual(await stage.locator("[data-auth-date]").evaluateAll(l => l.map(x => [x.dataset.authDate, x.textContent])), [["stated", "2026-03-15"]]);
  assert.deepEqual((await stage.locator("table.flat [data-who]").evaluateAll(l => l.map(x => [x.dataset.who, x.textContent]))).sort(),
    [["own", "platform-ops · 2026-07-10"], ["own", "platform-ops · 2026-11-06"]]);
  await R.view("stage:assess");
  assert.deepEqual((await stage.locator(".kanban [data-who]").evaluateAll(l => l.map(x => [x.dataset.who, x.textContent]))).sort(),
    [["own", "lead-assessor · 2026-07-18"], ["own", "secops · 2026-11-10"]]);
  assert.equal(await R.text(stage.locator("[data-deviation-line]")), "⚑ Deviation: false-positive · approved · decided 2026-07-18 · review due 2027-07-18");

  /* the resolved package of each Tailoring: Requirements only, so no kernel is pinned; the one whose
     Requirement carries a facet the folder pins takes that pin and the schema file along */
  for (const [id, reqs, pins] of [["https://cso.example/tailoring/linux-prod", 1, []], ["https://ns.bsi.bund.de/gspp/tailoring/erhoeht", 3, ["https://ns.bsi.bund.de/facet/gspp-taxonomy"]]]) {
    await R.view("stage:tailor");
    await page.locator(`[data-tsel="${id}"]`).click();
    const dir = unzipTo(await R.download("#wb-t-export-resolved"), path.join(R.tmp, "resolved-" + reqs));
    const m = JSON.parse(fs.readFileSync(path.join(dir, "content-manifest.json"), "utf8"));
    assert.equal(m.objects.length, reqs, id);
    assert.equal("kernel-version" in m, false, id);
    assert.deepEqual(m["facet-schemas"].map(x => x.id), pins, id);
    for (const pin of m["facet-schemas"]) assert.ok(fs.existsSync(path.join(dir, pin.path)), "the pinned schema is in the package");
    if (REFERENCE) { const ref = reference(dir); assert.ok(ref.ok, ref.out.slice(-2500)); assert.match(ref.line, / pass, 0 fail/); }
  }

  /* the folder pins its kernel and needs it: nothing is reported */
  await R.view("overview");
  assert.equal(await R.text(page.locator("#ov-kernel")), "2.0.0");
  assert.equal(await page.locator("[data-pin-error]").count(), 0);
  assert.doesNotMatch(await R.log(), /KERNEL-/);
}));

test("the IFA bundle: each record, Deviation and authorization shows what its file says, and says \"not stated\" exactly where the reference reports it", OPTS, () => withReader(async R => {
  const { page } = R;
  await R.load(IFA);
  /* What is expected is read from the bundle's files, not written down here: the conversion is being
     changed to pre-fill who and when from its sources, and this test holds the page to whatever the
     files say on the day it runs. */
  const objs = json(path.relative(ROOT, path.join(IFA, "content-manifest.json"))).objects.map(e => JSON.parse(fs.readFileSync(path.join(IFA, e.path), "utf8")));
  const NOUN = { risk: "Risk", finding: "Finding", implementation: "Implementation" }, last = uri => uri.split("/").filter(Boolean).pop();
  const missing = { "AUTHOR-2": [], "AUTHOR-3": [], "AUTHOR-4": [] }, seen = { records: 0, deviations: 0, authorizations: 0 };
  for (const o of objs) {
    const type = P.inferType(o), d = await R.detail(o.id), p = o.provenance;
    if (NOUN[type]) {
      seen.records++;
      assert.deepEqual(await R.who(d, "record"), p ? ["own", `${p["author-ref"]} · ${p.date}`] : ["none", `nobody is named — this ${NOUN[type]} does not say who wrote it and when`], o.id);
      if (!p) missing["AUTHOR-2"].push(o.id);
    } else assert.equal(await d.locator("[data-who]").count(), 0, `${o.id}: a ${type} gets no line about an author`);
    for (const [i, dev] of (o.deviations || []).entries()) {
      seen.deviations++;
      const box = d.locator(`[data-deviation="deviations[${i}]"]`), settled = ["approved", "withdrawn"].includes(dev.state);
      const decided = "decided" in dev ? ["stated", dev.decided] : settled ? ["none", `not stated — the Deviation is ${dev.state} and does not say on which day`] : ["open", `not decided — state ${dev.state}`];
      assert.deepEqual([await box.locator("[data-decided]").getAttribute("data-decided"), await R.text(box.locator("[data-decided]"))], decided, `${o.id} deviations[${i}]`);
      assert.equal(await box.locator("[data-review]").getAttribute("data-review"), "review-due" in dev ? "stated" : "none", `${o.id} deviations[${i}]`);
      assert.ok((await R.text(box)).includes(`opened ${dev.opened} — the day it was asked for`));
      if (decided[0] === "none" && !missing["AUTHOR-3"].includes(o.id)) missing["AUTHOR-3"].push(o.id);
    }
    for (const a of o.authorizations || []) {
      seen.authorizations++;
      const day = d.locator(`[data-authorization="${a.id}"] [data-auth-date]`);
      assert.equal(await day.getAttribute("data-auth-date"), "date" in a ? "stated" : "none", `${o.id} ${a.id}`);
      if ("date" in a) assert.equal(await R.text(day), a.date); else assert.match(await R.text(day), /^not stated — the authorization carries no `date`/);
      if (!("date" in a) && !missing["AUTHOR-4"].includes(o.id)) missing["AUTHOR-4"].push(o.id);
    }
  }
  assert.ok(seen.records >= 7 && seen.deviations >= 1 && seen.authorizations >= 2, "the bundle holds Risks, Findings, Implementations, a Deviation and authorizations: " + JSON.stringify(seen));

  /* the stage views say the same, in short */
  const stage = page.locator("#view-stagefn"), of = type => objs.filter(o => P.inferType(o) === type);
  const short = o => o.provenance ? ["own", `${last(o.provenance["author-ref"])} · ${o.provenance.date}`] : ["none", "nobody is named"];
  await R.view("stage:implement");
  assert.deepEqual((await stage.locator("table.flat [data-who]").evaluateAll(l => l.map(x => [x.dataset.who, x.textContent]))).sort(), of("implementation").map(short).sort());
  assert.deepEqual((await stage.locator("[data-auth-date]").evaluateAll(l => l.map(x => [x.dataset.authDate, x.textContent]))).sort(),
    of("component").flatMap(o => o.authorizations || []).map(a => "date" in a ? ["stated", a.date] : ["none", "no date field"]).sort());
  await R.view("stage:assess");
  assert.deepEqual((await stage.locator(".kanban [data-who]").evaluateAll(l => l.map(x => [x.dataset.who, x.textContent]))).sort(), of("finding").map(short).sort());
  assert.equal(await stage.locator("[data-deviation-line]").count(), of("finding").flatMap(o => o.deviations || []).length);

  /* the reference names the same objects: a record without provenance (AUTHOR-2), a Deviation approved
     or withdrawn without `decided` (AUTHOR-3), an authorization without `date` (AUTHOR-4) */
  if (REFERENCE) {
    const ref = reference(IFA);
    for (const rule of Object.keys(missing))
      assert.deepEqual(ref.notes.filter(l => l.includes(`(${rule})`)).map(l => l.trim().replace(/^note: /, "").split(": ")[0]).sort(), missing[rule].sort(), rule);
  }
}));

test("the workbenches: no author refuses nothing and writes none; with an author a Tailoring, an Implementation and a Finding name it; the export pins the kernel exactly then and passes the reference",
  OPTS, () => withReader(async R => {
    const { page } = R;
    const pick = async (id, q) => { await page.fill("#" + id, q); await page.locator(`#${id}-sugg [data-pick]`).first().click(); };
    const set = async (sel, value) => { await page.fill(sel, value); await page.locator(sel).dispatchEvent("change"); };
    const NS = "https://example.org/my", T = `${NS}/tailoring/my-tailoring`, I = `${NS}/impl/backup-server-encrypt-backups`;

    /* two Requirements and a Set to work on */
    await R.view("stage:author");
    for (const [title, prose] of [["Encrypt backups", "Backups are encrypted."], ["Rotate keys", "Keys are rotated."]]) {
      await page.fill("#wb-au-title", title);
      await page.fill("#wb-au-prose", prose);
      await page.fill("#wb-au-party", "Operations");
      await page.click("#wb-au-addreq");
    }
    await page.fill("#wb-au-settitle", "My baseline");
    await pick("wb-au-mempick", "encrypt");
    await pick("wb-au-mempick", "rotate");
    await page.click("#wb-au-addset");

    /* everything written once without an author */
    const write = async () => {
      await R.view("stage:tailor");
      if (!await page.locator("[data-delsel]").count()) {
        await pick("wb-t-selpick", "my baseline");
        await pick("wb-t-reqpick", "encrypt");
        await page.selectOption("#wb-t-mod", "should");
        await set("#wb-t-devrat", "The legacy tape library cannot encrypt.");
        await set("#wb-t-devappr", "Head of Security");
        await page.click("#wb-t-add");
      }
      await page.click("#wb-t-graph");
      await R.view("stage:implement");
      if (!await page.locator("[data-delcomp]").count()) {
        await page.fill("#wb-i-ctitle", "Backup server");
        await page.click("#wb-i-addcomp");
        await pick("wb-i-pick-0", "encrypt");
      }
      await page.click("#wb-i-graph");
      await R.view("stage:assess");
      await page.selectOption("#wb-a-scope", "system");
      if (!await page.inputValue("#wb-a-perf")) await set("#wb-a-perf", "Lead Assessor");
      if (!await page.locator(".seg .on-not").count()) await page.locator('[data-az$="|not-satisfied"]').first().click();
      await page.click("#wb-a-gen");
    };
    const exported = async name => {
      const dir = unzipTo(await R.download("#btn-export-ws"), path.join(R.tmp, name));
      const manifest = JSON.parse(fs.readFileSync(path.join(dir, "content-manifest.json"), "utf8"));
      const objs = manifest.objects.map(e => JSON.parse(fs.readFileSync(path.join(dir, e.path), "utf8")));
      return { dir, manifest, objs, of: type => objs.filter(o => P.inferType(o) === type) };
    };

    await R.view("stage:tailor");
    assert.match(await R.text(page.locator("#wb-t-who + [data-who-note]")), /^optional — without an author a Tailoring is written without provenance/);
    await write();
    const day = await page.evaluate(() => new Date().toISOString().slice(0, 10));
    for (const [id, noun] of [[I, "Implementation"], [`${NS}/finding/f-${day}-1`, "Finding"]])
      assert.deepEqual(await R.who(await R.detail(id), "record"), ["none", `nobody is named — this ${noun} does not say who wrote it and when`], id);
    let d = await R.detail(T);
    assert.deepEqual(await R.who(d, "record"), ["none", "nobody is named — this Tailoring does not say who wrote it and when"]);
    for (const of of ["selects[0]", "operations[0]"]) assert.deepEqual(await R.who(d, of), ["none", "nobody is named — neither this entry nor its Tailoring carries provenance"], of);
    const pending = d.locator('[data-deviation="operations[0].deviation"]');
    assert.equal(await R.text(pending.locator("[data-decided]")), "not decided — state pending");
    assert.equal(await pending.locator("[data-review]").getAttribute("data-review"), "none");
    await R.view("stage:tailor");
    assert.deepEqual(await R.who(page.locator("#view-stagefn"), "operations[0]"), ["none", "nobody is named"]);
    assert.equal(await R.text(page.locator("#view-stagefn [data-deviation-line]")), "⚑ Deviation: risk-adjustment · pending · not decided · no review date is stated");

    const A = await exported("without");
    assert.deepEqual(A.objs.filter(o => JSON.stringify(o).includes("provenance")), [], "no provenance anywhere");
    assert.equal("kernel-version" in A.manifest, false, "1.0.0 content: the manifest pins no kernel");
    assert.deepEqual([A.of("tailoring").length, A.of("implementation").length, A.of("finding").length], [1, 1, 1]);
    assert.equal(A.of("tailoring")[0].operations[0].deviation["approver-ref"], `${NS}/party/head-of-security`, "the approver typed is the approver written");
    assert.deepEqual(A.of("assessment").map(o => o["performer-ref"]), [`${NS}/party/lead-assessor`]);
    assert.match(await R.log(), /manifest: no kernel-version is pinned — the content is 1\.0\.0 content/);
    /* the page states its version once: on the top bar, in the manifest it writes, on the first line of its console */
    const version = await page.locator("#pill-version").innerText();
    assert.match(version, /^v\d+\.\d+\.\d+ · build \d{4}-\d{2}-\d{2}$/);
    assert.equal(A.manifest.provenance.converter, "jascon-reader.html " + version.split(" · ")[0]);
    assert.ok((await R.log()).includes(`JASCON Bundle Reader ${version} — `));
    if (REFERENCE) {
      const ref = reference(A.dir);
      assert.ok(ref.ok, ref.out.slice(-2500));
      assert.match(ref.line, / pass, 0 fail/);
      assert.equal(ref.notes.filter(l => /\(AUTHOR-2\)/.test(l)).length, 2, "the missing authors are two lines of the report: the Implementation and the Finding");
      assert.equal(reference(A.dir, "--require-authors").ok, false, "and a failure only where the caller asks for authors");
    }

    /* the same with an author: a URI as typed, on every workbench at once */
    const CISO = `${NS}/party/ciso`;
    await R.view("stage:tailor");
    await set("#wb-t-who", CISO);
    assert.equal(await R.text(page.locator("#wb-t-who + [data-who-note]")), `a Tailoring written here names ${CISO} · ${day} as its provenance; an entry it held before keeps who decided it`);
    await R.view("stage:implement");
    assert.equal(await page.inputValue("#wb-i-who"), CISO, "one author for the three workbenches");
    /* a plain name becomes a party under the namespace, and the field says which. The name is typed and
       the button pressed at once, as a person does: the field's change must not cost the click */
    await page.fill("#wb-i-who", "Platform Ops");
    await page.click("#wb-i-graph");
    assert.equal(await R.text(page.locator("#wb-i-who + [data-who-note]")), `an Implementation written here names ${NS}/party/platform-ops · ${day} as its provenance; one that is unchanged keeps what it names`);
    assert.deepEqual(await R.who(await R.detail(I), "record"), ["own", `${NS}/party/platform-ops · ${day}`]);
    await R.view("stage:implement");
    await set("#wb-i-who", CISO);
    await write();

    d = await R.detail(T);
    assert.deepEqual(await R.who(d, "record"), ["own", `${CISO} · ${day}`]);
    for (const of of ["selects[0]", "operations[0]"]) assert.deepEqual(await R.who(d, of), ["record", `${CISO} · ${day} inherited from the Tailoring`], of);
    const B = await exported("with");
    const WROTE = { "author-ref": CISO, date: day };
    assert.deepEqual(B.of("tailoring").map(o => o.provenance), [WROTE]);
    assert.deepEqual(B.of("implementation").map(o => o.provenance), [{ "author-ref": `${NS}/party/platform-ops`, date: day }], "written again unchanged under another author, the Implementation keeps the author it names");
    assert.deepEqual(B.of("finding").map(o => o.provenance), [WROTE]);
    assert.deepEqual(B.objs.filter(o => !["tailoring", "implementation", "finding"].includes(P.inferType(o)) && "provenance" in o), [], "no other type is given one");
    assert.equal(B.of("tailoring")[0].operations.some(op => "provenance" in op), false, "the entries carry none of their own: they have the Tailoring's");
    assert.equal(B.manifest["kernel-version"], "2.0.0", "provenance is 2.0.0 content: the manifest pins the kernel");
    assert.match(await R.log(), /manifest: pins kernel-version 2\.0\.0 — .* names its author \(provenance\)/);
    if (REFERENCE) {
      const ref = reference(B.dir, "--require-authors", "--as-of", "2026-11-14");
      assert.ok(ref.ok, ref.out.slice(-2500));
      assert.match(ref.line, / pass, 0 fail/);
      assert.deepEqual(ref.notes.filter(l => /\(AUTHOR-/.test(l)), [], "nothing is reported as missing");
    }

    /* one object, downloaded: the Tailoring as the kernel types it, its author in it */
    await R.view("stage:tailor");
    const one = JSON.parse(fs.readFileSync(await R.download("#wb-t-dl"), "utf8"));
    assert.deepEqual(one.provenance, WROTE);
    assert.deepEqual(one.title, { en: "my-tailoring" });
    if (REFERENCE) assert.deepEqual(kernelErrors("tailoring", one), []);

    /* the other export: the resolved package holds Requirements and no decision, and pins nothing */
    const resolved = unzipTo(await R.download("#wb-t-export-resolved"), path.join(R.tmp, "resolved"));
    const rm = JSON.parse(fs.readFileSync(path.join(resolved, "content-manifest.json"), "utf8"));
    assert.equal("kernel-version" in rm, false);
    assert.equal(rm.objects.length, 2);
    if (REFERENCE) assert.ok(reference(resolved).ok);

    /* a second author adds an operation and saves: the Tailoring is hers, what the first decided stays his */
    const OPS = `${NS}/party/head-of-ops`;
    await set("#wb-t-who", OPS);
    await pick("wb-t-reqpick", "rotate");
    await page.selectOption("#wb-t-mod", "must");
    await page.click("#wb-t-add");
    await page.click("#wb-t-graph");
    d = await R.detail(T);
    assert.deepEqual(await R.who(d, "record"), ["own", `${OPS} · ${day}`]);
    for (const of of ["selects[0]", "operations[0]"]) assert.deepEqual(await R.who(d, of), ["own", `${CISO} · ${day}`], of + ": decided by the first author, and still his");
    assert.deepEqual(await R.who(d, "operations[1]"), ["record", `${OPS} · ${day} inherited from the Tailoring`]);
    const C = await exported("second");
    assert.deepEqual(C.of("tailoring")[0].operations.map(op => op.provenance), [WROTE, undefined]);
    if (REFERENCE) { const ref = reference(C.dir, "--require-authors", "--as-of", "2026-11-14"); assert.ok(ref.ok, ref.out.slice(-2500)); }

    /* what the page wrote, read back: pinned and needed, every digest verified */
    await R.load(B.dir);
    assert.equal(await page.locator("[data-pin-error]").count(), 0);
    await page.click("#btn-verify");
    await page.locator("#pill-verify:not(.hidden)").waitFor();
    assert.equal(await R.text(page.locator("#pill-verify")), `✓ ${B.manifest.objects.length} objects verified`);
    assert.equal(B.manifest.objects.length, 9);

    /* KERNEL-1: the same bundle without its pin is shown, and the page says what is missing */
    const unpinned = path.join(R.tmp, "unpinned", "bundle"), ahead = path.join(R.tmp, "ahead", "bundle");
    for (const [dir, pin] of [[unpinned, undefined], [ahead, "3.0.0"]]) {
      fs.cpSync(B.dir, dir, { recursive: true });
      const m = { ...B.manifest };
      if (pin) m["kernel-version"] = pin; else delete m["kernel-version"];
      fs.writeFileSync(path.join(dir, "content-manifest.json"), JSON.stringify(m, null, 1) + "\n");
    }
    await R.load(unpinned);
    await R.view("overview");
    assert.match(await R.text(page.locator("#ov-kernel")), /^none pinned/);
    assert.match(await R.text(page.locator("[data-pin-error]")), /names its author \(provenance\), which needs kernel 2\.0\.0, but the manifest pins no kernel-version \(KERNEL-1/);
    assert.equal(await page.locator("#nc-tailor").innerText(), "1", "the bundle is shown all the same");
    if (REFERENCE) {
      const ref = reference(unpinned);
      assert.equal(ref.ok, false);
      assert.match(ref.out, /names its author \(provenance\), which needs kernel 2\.0\.0, but the manifest pins no kernel-version \(KERNEL-1/, "the reference refuses the same bundle with the same sentence");
    }

    /* KERNEL-2: at a pin the page does not read it stops, names both, and shows nothing of the bundle */
    await R.load(ahead);
    assert.match(await R.text(page.locator("#ov-stop")), /The last bundle was not read\. manifest pins kernel-version 3\.0\.0; this reader implements 2\.0\.0 and reads 1\.0\.0, 2\.0\.0 \(KERNEL-2/);
    assert.equal(await R.text(page.locator("#pill-bundle")), 'not read · kernel-version "3.0.0"');
    assert.equal(await page.locator("#nc-tailor").innerText(), "", "no object of it is counted");
    await R.view("browser");
    assert.equal(await page.locator(".objrow").count(), 0, "or listed");
    assert.equal(await page.locator("#btn-verify").isDisabled(), true);
    /* and a bundle it reads is read again afterwards */
    await R.load(B.dir);
    assert.equal(await page.locator("#ov-stop").isHidden(), true);
    assert.equal(await page.locator("#nc-tailor").innerText(), "1");

    /* the same two bundles from a URL, with a deep link to the Tailor stage: the first opens there and
       shows who decided; the second stays on the overview, which says why nothing is shown */
    const server = await serve(R, "listing");
    try {
      const web = R.watch(await page.context().newPage());
      const linked = async bundle => {
        await web.goto("about:blank");
        await web.goto(`${server.reader}#load=${server.url(bundle)}&view=stage:tailor`);
        await web.waitForFunction(() => /indexed \d+ objects|nothing of this bundle is shown/.test(document.getElementById("log").textContent));
        await web.waitForFunction(() => document.querySelector(".navitem.active")?.dataset.view !== "stages");   // the load leaves the Stages view: for the linked view, or for the overview
      };
      await linked(B.dir);
      assert.equal(await web.locator("#view-stagefn").isVisible(), true);
      assert.deepEqual(await R.who(web.locator("#view-stagefn"), "record"), ["own", `ciso · ${day}`]);
      assert.deepEqual(await R.who(web.locator("#view-stagefn"), "operations[0]"), ["record", `ciso · ${day} inherited`]);
      await linked(ahead);
      assert.equal(await web.locator("#view-stagefn").isVisible(), false, "the linked view is not opened over a bundle that was not read");
      assert.match(await R.text(web.locator("#ov-stop")), /manifest pins kernel-version 3\.0\.0; this reader implements 2\.0\.0/);
    } finally { server.close(); }
  }));

test("a party the kernel requires: an empty field writes nothing and says why; a named party is written as named; an approver is never pre-filled", OPTS, () => withReader(async R => {
  const { page } = R;
  const pick = async (id, q) => { await page.fill("#" + id, q); await page.locator(`#${id}-sugg [data-pick]`).first().click(); };
  const set = async (sel, value) => { await page.fill(sel, value); await page.locator(sel).dispatchEvent("change"); };
  const NS = "https://example.org/my", day = await page.evaluate(() => new Date().toISOString().slice(0, 10));
  /* what a workbench says beside its button when it refuses: [that it is a refusal for want of a party, the sentence] */
  const refused = async id => { const e = page.locator("#" + id); return [await e.getAttribute("data-refused"), await R.text(e)]; };
  /* what the graph holds, by type, as the object browser counts it */
  const held = async () => Object.fromEntries(await page.locator("#typefilters .fpill[data-t]").evaluateAll(l => l.map(x => [x.dataset.t, Number(x.textContent.split("·").pop())])));
  const downloads = [];
  page.on("download", d => downloads.push(d.suggestedFilename()));

  /* 1. whom a statement binds */
  await R.view("stage:author");
  assert.equal(await page.inputValue("#wb-au-party"), "", "the party field starts empty");
  await page.fill("#wb-au-title", "Encrypt backups");
  await page.fill("#wb-au-prose", "Backups are encrypted.");
  await page.click("#wb-au-addreq");
  assert.deepEqual(await refused("wb-au-err"), ["party", REFUSED.statement]);
  assert.deepEqual(await held(), {}, "nothing was written");
  assert.deepEqual([await page.inputValue("#wb-au-title"), await page.inputValue("#wb-au-prose")], ["Encrypt backups", "Backups are encrypted."], "and nothing was changed: the form holds what was typed");
  await page.fill("#wb-au-party", "?!");
  await page.click("#wb-au-addreq");
  assert.match((await refused("wb-au-err"))[1], /^party "\?!" names no party \(a URI, or a name with a letter a-z or a digit, does\) — the kernel requires a statement to name whom it binds/);
  assert.deepEqual(await held(), {});
  await page.fill("#wb-au-party", "Operations Team");
  await page.click("#wb-au-addreq");                       // typed and pressed at once
  assert.deepEqual(await held(), { requirement: 1 });
  assert.equal(await R.text(page.locator("#wb-au-err")), "");
  await page.fill("#wb-au-title", "Rotate keys");
  await page.fill("#wb-au-prose", "Keys are rotated.");
  await page.fill("#wb-au-party", "https://cso.example/party/key-custodian");
  await page.click("#wb-au-addreq");
  await page.fill("#wb-au-settitle", "My baseline");
  await pick("wb-au-mempick", "encrypt");
  await pick("wb-au-mempick", "rotate");
  await page.click("#wb-au-addset");
  const before = { requirement: 2, requirementSet: 1 };
  assert.deepEqual(await held(), before);

  /* 2. who performed an Assessment: no performer is typed and there is no author to start from */
  await R.view("stage:assess");
  assert.equal(await page.inputValue("#wb-a-perf"), "", "the performer field starts empty");
  assert.equal(await R.text(page.locator("[data-performer-note]")), "required — the kernel requires an Assessment to name who performed it; without a performer nothing is generated");
  assert.match(await R.text(page.locator("#wb-a-who + [data-who-note]")), /^optional — without an author a Finding is written without provenance/, "the author beside it stays optional");
  await page.locator('[data-az$="|not-satisfied"]').first().click();
  await page.click("#wb-a-gen");
  assert.deepEqual(await refused("wb-a-err"), ["party", REFUSED.assessment]);
  await page.click("#wb-a-dl");
  assert.deepEqual(await refused("wb-a-err"), ["party", REFUSED.assessment]);
  await page.waitForTimeout(700);                          // a download would have begun by now
  assert.deepEqual(downloads, [], "nothing was downloaded either");
  assert.deepEqual(await held(), before, "no Assessment and no Finding");

  /* 3. whose claim a Mapping is. The performer is named now, in the other form - and a Mapping does not take it. */
  await set("#wb-a-perf", "Lead Assessor");
  await R.view("stage:map");
  assert.equal(await page.inputValue("#wb-m-who"), "");
  assert.equal(await R.text(page.locator("#wb-m-who + [data-who-note]")), "required — the kernel requires a Mapping to name its author; without one no Mapping is written");
  await pick("wb-m-srcpick", "encrypt");
  await pick("wb-m-tgtpick", "rotate");
  await page.click("#wb-m-add");
  assert.deepEqual(await refused("wb-m-err"), ["party", REFUSED.mapping]);
  assert.deepEqual(await held(), before, "no Mapping: not under the performer's name, and not under a word");
  /* The author is typed and the button pressed at once, as a person does. The field loses the focus to the button
     while the pointer is down, and nothing under the pointer may move then, or the click is lost: the note beside
     the field, which can grow by a line and push the button down, waits until the pointer is up. */
  await page.fill("#wb-m-who", "Compliance Office");
  const button = await page.locator("#wb-m-add").boundingBox();
  await page.mouse.move(button.x + button.width / 2, button.y + button.height / 2);
  await page.mouse.down();
  assert.match(await R.text(page.locator("#wb-m-who + [data-who-note]")), /^required — /, "while the pointer is down the note is not rewritten");
  await page.mouse.up();
  assert.deepEqual(await held(), { ...before, mapping: 1 });
  assert.equal(await R.text(page.locator("#wb-m-who + [data-who-note]")), `a Mapping written here names ${NS}/party/compliance-office · ${day} as its provenance`);
  /* A Mapping is one claim, added by one press: added again, it names who adds it now, and not who it named
     before. That is how a Mapping an earlier version wrote under a word comes to a named author. */
  const claimedBy = async () => ((await R.text(await R.detail(`${NS}/map/encrypt-backups-rotate-keys`))).match(/provenance (\S+) · /) || [])[1];
  assert.equal(await claimedBy(), `${NS}/party/compliance-office`);
  await R.view("stage:map");
  await set("#wb-m-who", "Somebody Else");
  await page.click("#wb-m-add");
  assert.equal(await claimedBy(), `${NS}/party/somebody-else`);
  await R.view("stage:map");
  await set("#wb-m-who", "Compliance Office");
  await page.click("#wb-m-add");
  assert.equal(await claimedBy(), `${NS}/party/compliance-office`);
  await R.view("stage:map");

  /* 4. the Assessment, its performer named */
  await R.view("stage:assess");
  assert.equal(await R.text(page.locator("[data-performer-note]")), `the Assessment names ${NS}/party/lead-assessor as its performer`);
  await page.click("#wb-a-gen");
  assert.deepEqual(await held(), { ...before, mapping: 1, assessment: 1, finding: 1 });

  /* 5. who approves a Deviation: the field starts empty for every Deviation, also now that an author is named */
  await R.view("stage:tailor");
  assert.equal(await page.inputValue("#wb-t-who"), "Compliance Office");
  await pick("wb-t-selpick", "my baseline");
  await pick("wb-t-reqpick", "encrypt");
  await page.selectOption("#wb-t-mod", "should");
  assert.equal(await page.inputValue("#wb-t-devappr"), "", "no approver by default, and none taken from the author");
  await set("#wb-t-devrat", "The legacy tape library cannot encrypt.");
  await page.click("#wb-t-add");
  assert.deepEqual(await refused("wb-t-err"), ["party", REFUSED.deviation]);
  assert.equal(await page.locator("[data-delop]").count(), 0, "the operation was not added");
  assert.equal(await page.inputValue("#wb-t-devrat"), "The legacy tape library cannot encrypt.", "what was typed stays");
  await page.fill("#wb-t-devappr", "Head of Security");
  await page.click("#wb-t-add");                           // typed and pressed at once
  assert.equal(await page.locator("[data-delop]").count(), 1);
  assert.equal(await page.inputValue("#wb-t-devappr"), "", "the approver of the Deviation just written does not stay in the field");
  /* the next Deviation: empty again. An approver typed for an operation that is then begun anew does not stay either. */
  await pick("wb-t-reqpick", "rotate");
  await page.selectOption("#wb-t-mod", "may");
  assert.equal(await page.inputValue("#wb-t-devappr"), "", "the approver of the Deviation before is not the approver of this one");
  await set("#wb-t-devappr", "Somebody Else");
  await pick("wb-t-reqpick", "rotate");
  assert.equal(await page.inputValue("#wb-t-devappr"), "");
  await set("#wb-t-devrat", "Rotation is manual until the HSM arrives.");
  await set("#wb-t-devappr", "https://cso.example/party/ciso");
  await page.click("#wb-t-add");
  assert.equal(await page.locator("[data-delop]").count(), 2);
  await page.click("#wb-t-graph");

  /* 6. what was written names the parties as they were named, and no other */
  const dir = unzipTo(await R.download("#btn-export-ws"), path.join(R.tmp, "named"));
  const manifest = JSON.parse(fs.readFileSync(path.join(dir, "content-manifest.json"), "utf8"));
  const objs = manifest.objects.map(e => JSON.parse(fs.readFileSync(path.join(dir, e.path), "utf8"))), of = type => objs.filter(o => P.inferType(o) === type);
  const OFFICE = `${NS}/party/compliance-office`;
  assert.deepEqual(of("requirement").map(o => o.statements[0]["obligated-parties"]), [[`${NS}/party/operations-team`], ["https://cso.example/party/key-custodian"]]);
  assert.deepEqual(of("mapping").map(o => o.provenance), [{ "author-ref": OFFICE, date: day }]);
  assert.deepEqual(of("assessment").map(o => o["performer-ref"]), [`${NS}/party/lead-assessor`]);
  assert.deepEqual(of("tailoring")[0].operations.map(op => op.deviation["approver-ref"]), [`${NS}/party/head-of-security`, "https://cso.example/party/ciso"]);
  assert.deepEqual([...new Set(JSON.stringify(objs).match(/https:[^"]*\/party\/[^"]*/g))].sort(),
    [OFFICE, `${NS}/party/head-of-security`, `${NS}/party/lead-assessor`, `${NS}/party/operations-team`, "https://cso.example/party/ciso", "https://cso.example/party/key-custodian"].sort(),
    "every party in the bundle is one somebody typed");
  /* the optional authors of the same bundle: the Tailoring and the Finding name the author, because one was given */
  assert.deepEqual([of("tailoring")[0].provenance, of("finding")[0].provenance], [{ "author-ref": OFFICE, date: day }, { "author-ref": OFFICE, date: day }]);
  if (REFERENCE) {
    const ref = reference(dir, "--require-authors", "--as-of", "2026-11-14");
    assert.ok(ref.ok, ref.out.slice(-2500));
    assert.match(ref.line, / pass, 0 fail/);
    assert.deepEqual(ref.notes.filter(l => /\(AUTHOR-/.test(l)), []);
  }
}));

test("the performer of an Assessment starts from the author and from no word; typed, it stays; emptied, it is empty; the word an earlier version stored is no party", OPTS, () => withReader(async R => {
  const { page } = R;
  const set = async (sel, value) => { await page.fill(sel, value); await page.locator(sel).dispatchEvent("change"); };
  const NS = "https://example.org/my", day = await page.evaluate(() => new Date().toISOString().slice(0, 10)), ASSESSMENT_ID = `${NS}/asmt/check-${day}`;
  const refused = async id => { const e = page.locator("#" + id); return [await e.getAttribute("data-refused"), await R.text(e)]; };
  /* the performer the generated Assessment names, read where the object browser shows it */
  const performer = async () => { const t = await R.text(await R.detail(ASSESSMENT_ID)); return (t.match(/performer-ref (\S+)/) || [])[1]; };
  await R.load(EXAMPLES);
  await R.view("stage:assess");
  assert.equal(await page.inputValue("#wb-a-perf"), "");

  /* The author is typed, and the pointer pressed somewhere beside the field. While it is down the notes and the
     performer field stay as they are; once it is up they say what will be written. */
  await page.fill("#wb-a-who", "https://cso.example/party/secops");
  const beside = await page.locator("#view-stagefn .wb > .nano").first().boundingBox();
  await page.mouse.move(beside.x + 4, beside.y + 4);
  await page.mouse.down();
  assert.match(await R.text(page.locator("#wb-a-who + [data-who-note]")), /^optional — /, "while the pointer is down nothing is rewritten");
  assert.equal(await page.inputValue("#wb-a-perf"), "");
  await page.mouse.up();
  await page.waitForFunction(() => document.querySelector("#wb-a-perf").value !== "");
  assert.equal(await R.text(page.locator("#wb-a-who + [data-who-note]")), `a Finding written here names https://cso.example/party/secops · ${day} as its provenance; one that is unchanged keeps what it names`);
  /* the performer field has taken the author, and says where it has it from */
  assert.equal(await page.inputValue("#wb-a-perf"), "https://cso.example/party/secops");
  assert.equal(await R.text(page.locator("[data-performer-note]")), "the Assessment names https://cso.example/party/secops as its performer — the author, until a performer is typed");
  await set("#wb-a-who", "Platform Ops");
  assert.equal(await page.inputValue("#wb-a-perf"), "Platform Ops", "and follows the author while nobody has typed a performer");
  await page.click("#wb-a-gen");
  assert.equal(await performer(), `${NS}/party/platform-ops`);

  /* a performer somebody typed stays, whoever the author becomes */
  await R.view("stage:assess");
  await set("#wb-a-perf", "Lead Assessor");
  assert.equal(await R.text(page.locator("[data-performer-note]")), `the Assessment names ${NS}/party/lead-assessor as its performer`);
  await set("#wb-a-who", "https://cso.example/party/secops");
  assert.equal(await page.inputValue("#wb-a-perf"), "Lead Assessor");
  await page.click("#wb-a-gen");
  assert.equal(await performer(), `${NS}/party/lead-assessor`);

  /* a field somebody emptied is empty: the author does not come back into it, and nothing is written */
  await R.view("stage:assess");
  await set("#wb-a-perf", "");
  await page.click("#wb-a-gen");
  assert.deepEqual(await refused("wb-a-err"), ["party", REFUSED.assessment]);
  assert.equal(await performer(), `${NS}/party/lead-assessor`, "the Assessment in the graph is the one written before");
  await R.view("stage:assess");
  assert.equal(await page.inputValue("#wb-a-perf"), "", "also after the workbench is drawn again");

  /* The state an earlier version stored. It began with the performer "assessor", which nobody had typed: that
     word is no party, and nothing is generated under it. A performer somebody did type is kept. */
  const earlier = performerStored => ({ ns: NS, tailor: { label: "my-tailoring", selects: [], excludes: [], operations: [] },
    system: { title: "My System", components: [], implementations: [] }, assess: { scopeKey: "", performer: performerStored, results: {} } });
  for (const [storedWord, shown, written] of [["assessor", "", undefined], ["Jane Roe", "Jane Roe", `${NS}/party/jane-roe`]]) {
    await page.evaluate(w => localStorage.setItem("scr-work", JSON.stringify(w)), earlier(storedWord));
    await page.reload();
    await R.load(EXAMPLES);
    await R.view("stage:assess");
    assert.equal(await page.inputValue("#wb-a-perf"), shown, `stored as ${storedWord}`);
    await page.click("#wb-a-gen");
    if (written) assert.equal(await performer(), written);
    else {
      assert.deepEqual(await refused("wb-a-err"), ["party", REFUSED.assessment]);
      await R.view("browser");
      assert.equal(await page.locator(`.objrow[data-id="${ASSESSMENT_ID}"]`).count(), 0, "no Assessment was written");
    }
  }
}));

test("pasted objects: Deviations in every state with review dates of every shape, a Risk's ratings, authorizations with and without a day - written out as recorded", OPTS, () => withReader(async R => {
  const { page } = R;
  const paste = async obj => { R.answers.push(JSON.stringify(obj)); await page.click("#btn-paste"); return page.locator("#detail"); };
  const SCALE = `${EX}/scale/five`;

  /* a Risk that names no author; its rating has none to inherit, its residual rating names its own */
  let r = await paste({ ...RISK, state: "assessed", rating: { level: "high", "scale-ref": SCALE }, "residual-rating": { level: "low", "scale-ref": SCALE, provenance: WHO } });
  assert.deepEqual(await R.who(r, "record"), ["none", "nobody is named — this Risk does not say who wrote it and when"]);
  assert.deepEqual(await R.who(r, "rating"), ["none", "nobody is named — neither this entry nor its Risk carries provenance"]);
  assert.deepEqual(await R.who(r, "residual-rating"), ["own", `${WHO["author-ref"]} · ${WHO.date}`]);

  /* a Component with one authorization that says its day and one that does not */
  r = await paste({ ...COMPONENT, authorizations: [{ id: "ato-1", "authority-ref": `${EX}/party/ao`, date: "2026-06-30" }, { id: "ato-2", "authority-ref": `${EX}/party/ao`, "scope-label": "interim (2026-01-15)" }] });
  assert.deepEqual(await r.locator("[data-auth-date]").evaluateAll(l => l.map(x => [x.dataset.authDate, x.textContent])),
    [["stated", "2026-06-30"], ["none", "not stated — the authorization carries no `date`: it names the authority and not the day"]]);
  await R.view("stage:implement");
  assert.deepEqual(await page.locator("#view-stagefn [data-auth-date]").evaluateAll(l => l.map(x => [x.dataset.authDate, x.textContent])), [["stated", "2026-06-30"], ["none", "no date field"]]);

  await paste({ ...FINDING, provenance: { "author-ref": `${EX}/party/ciso` }, deviations: [
    { ...DEVIATION, state: "withdrawn" },
    { ...DEVIATION, state: "investigating" },
    { ...DEVIATION, decided: "2026-11-03", "review-due": { type: "elapsed-duration", num: 72, unit: "hours" } },
    { ...DEVIATION, decided: "2026-11-03", "review-due": { type: "calendar-period", num: 6, unit: "months", "calendar-ref": `${EX}/calendar/isms` } },
    { ...DEVIATION, "review-due": { type: "datetime", value: "2027-05-12T09:00:00Z" } }] });
  const d = page.locator("#detail"), dev = i => d.locator(`[data-deviation="deviations[${i}]"]`);
  /* a provenance that names an author and no day shows what is there */
  assert.deepEqual(await R.who(d, "record"), ["own", `${EX}/party/ciso · no date`]);
  assert.equal(await R.text(dev(0).locator("[data-decided]")), "not stated — the Deviation is withdrawn and does not say on which day");
  assert.equal(await dev(0).locator("[data-decided]").getAttribute("data-decided"), "none");
  assert.equal(await R.text(dev(1).locator("[data-decided]")), "not decided — state investigating");
  assert.equal(await dev(1).locator("[data-decided]").getAttribute("data-decided"), "open");
  assert.match(await R.text(dev(2)), /decided 2026-11-03 review-due 72 hours \(elapsed\) — counted from `decided`, else from `opened`/);
  assert.match(await R.text(dev(3)), /review-due 6 months \(calendar https:\/\/org\.example\/calendar\/isms\) — counted from `decided`, else from `opened`/);
  assert.equal(await R.text(dev(4).locator("[data-review]")), "2027-05-12T09:00:00Z");
  assert.equal(await d.locator("[data-deviation]").count(), 5);
  /* the board of stage 5 says the same, in a line each */
  await R.view("stage:assess");
  assert.deepEqual(await page.locator("#view-stagefn [data-deviation-line]").evaluateAll(l => l.map(x => x.textContent.replace(/\s+/g, " "))), [
    "⚑ Deviation: operational-requirement · withdrawn · no day decided is stated · no review date is stated",
    "⚑ Deviation: operational-requirement · investigating · not decided · no review date is stated",
    "⚑ Deviation: operational-requirement · approved · decided 2026-11-03 · review due 72 hours (elapsed)",
    "⚑ Deviation: operational-requirement · approved · decided 2026-11-03 · review due 6 months (calendar https://org.example/calendar/isms)",
    "⚑ Deviation: operational-requirement · approved · no day decided is stated · review due 2027-05-12T09:00:00Z"]);
}));

/* ---------- 11. what an Attestation binds of a bundle (backlog #46; Appendix B.1.7) ---------- */
const BINDS = json("jascon/conformance/attestation-vectors.json")["binds-vectors"];
const PACK = path.join(ROOT, "jascon/example-packs/dbvendor-server-7-advice");
const sha256 = bytes => "sha256:" + crypto.createHash("sha256").update(bytes).digest("hex");
const byId = (a, b) => (a < b ? -1 : a > b ? 1 : 0);
const deliveredOf = async objs => new Map(await Promise.all(objs.map(async o => [o.id, await P.semanticDigest(o)])));
const judged = async c => P.attestationBinds(c.attestation, c["manifest-digest"], await deliveredOf(c.objects), c["kept-packs"] || []);

test("attestation-binds: each of the 19 binds vectors gets the reference's verdict, manifest, subjects and failure from the page's own function", async () => {
  assert.equal(BINDS.length, 19);   // a vector added to the family is looked at here before this number moves
  const seen = new Set();
  for (const c of BINDS) {
    for (const o of c.objects) assert.ok(![null, "manifest"].includes(P.inferType(o)), `${c.name}: ${o.id} is typed`);
    const r = await judged(c);
    assert.deepEqual([r.verdict, r.manifest, r.subjects.map(s => s.status), r.fails],
      [c.expected, c["expected-manifest"], c["expected-subjects"], c["expected-failure"]], c.name);
    for (const x of [r.verdict, r.manifest, ...r.subjects.map(s => s.status), "fails " + r.fails, "lifecycle " + c.attestation.lifecycle]) seen.add(x);
  }
  /* what the deliberate defects need a vector for */
  for (const x of ["full-match", "semantic-match", "fail", "this", "kept-pack", "other", "match", "differs", "absent", "fails true", "fails false",
    "lifecycle active", "lifecycle draft", "lifecycle deprecated", "lifecycle withdrawn"]) assert.ok(seen.has(x), `a vector holds a case of '${x}'`);
  /* no vector holds an Attestation without a subject (the kernel schema refuses one): it binds nothing */
  for (const [lifecycle, fails] of [["active", true], ["draft", false]]) {
    const r = await judged({ ...BINDS[0], attestation: { ...BINDS[0].attestation, lifecycle, "subject-semantic-digests": [] } });
    assert.deepEqual([r.verdict, r.manifest, r.subjects, r.fails], ["fail", "this", [], fails], `no subject, ${lifecycle}`);
  }
});

/* binds_report of the reference, run by Python on cases typed by the page (its source is taken out of
   validate_core.py by name, as for kernel_needed). -> per case, what it prints and what it records as failed */
function referenceBindsLines(cases) {
  const py = `
import ast, contextlib, copy, hashlib, io, json, sys
src = open(sys.argv[1], encoding="utf-8").read()
said = []
ns = {"json": json, "copy": copy, "hashlib": hashlib, "fail": lambda section, msg: said.append(msg)}
names = ("_canon", "canonical", "sdig", "by_code_unit", "attestation_binds", "binds_report")
for node in ast.parse(src).body:
    wanted = isinstance(node, ast.FunctionDef) and node.name in names
    if wanted or (isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "BINDS_MANIFEST"):
        exec(compile(ast.Module([node], []), sys.argv[1], "exec"), ns)
out = []
for c in json.load(sys.stdin):
    del said[:]
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ns["binds_report"]("s", {c["attestation"]["id"]: c["attestation"]}, c["manifest"], {i: (t, o) for i, t, o in c["objs"]}, [(k[len("sha256:"):], b"") for k in c["kept"]])
    out.append([l.strip() for l in buf.getvalue().splitlines()] + said)
print(json.dumps(out))`;
  const run = spawnSync("python3", ["-c", py, VALIDATE], { input: JSON.stringify(cases), encoding: "utf8" });
  assert.equal(run.status, 0, run.stderr.slice(-1500));
  return JSON.parse(run.stdout);
}

test("attestation-binds: the line the page prints about an Attestation is the one the reference's binds_report prints, for every vector and for an Attestation without subjects",
  { skip: !PYTHON && "python3 is not installed" }, async () => {
    const first = BINDS[0], none = lifecycle => ({ ...first, name: `no subject, ${lifecycle}`, attestation: { ...first.attestation, lifecycle, "subject-semantic-digests": [] } });
    const cases = [...BINDS, none("active"), none("draft")];
    const ref = referenceBindsLines(cases.map(c => ({ attestation: c.attestation, manifest: c["manifest-digest"], objs: typed(c.objects), kept: c["kept-packs"] || [] })));
    const lines = [];
    for (const [i, c] of cases.entries()) {
      const line = P.bindsLine(c.attestation, await judged(c));
      assert.deepEqual([line], ref[i], c.name);
      lines.push(line);
    }
    for (const kind of [/^binds: \S+ = FULL MATCH \[\d+ subject\(s\) of this bundle; this manifest\]$/, /= FULL MATCH \[1 subject\(s\) of this bundle; a pack manifest this bundle keeps\]$/,
      /= SEMANTIC MATCH \[\d+ subject\(s\) of this bundle; another manifest: the content is proven, the packaging was altered\]$/,
      /= DOES NOT BIND \[lifecycle withdrawn: reported, not a failure\] subject \S+: recomputed semantic digest sha256:[0-9a-f]{64}, signed sha256:[0-9a-f]{64} - this manifest$/,
      /= DOES NOT BIND \[lifecycle draft: reported, not a failure\] subject \S+: not an object of this bundle - this manifest$/, /= DOES NOT BIND \[lifecycle draft: reported, not a failure\] it names no subject - /,
      /^\[attestation-binds\] \S+: subject sha256:[0-9a-f]{64}: no object of this bundle carries it - this manifest \(B\.1\.7: /, /^\[attestation-binds\] \S+: it names no subject - /])
      assert.ok(lines.some(l => kind.test(l)), `a line of the kind ${kind}`);
  });

/* verify_envelope of the reference, with no trusted key: -> per case [status, detail] */
function referenceEnvelopes(cases) {
  const py = `
import ast, base64, copy, json, sys
src = open(sys.argv[1], encoding="utf-8").read()
ns = {"json": json, "copy": copy, "base64": base64}
for node in ast.parse(src).body:
    wanted = isinstance(node, ast.FunctionDef) and node.name in ("_canon", "canonical", "verify_envelope")
    if wanted or (isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "DSSE_PAYLOAD_TYPE"):
        exec(compile(ast.Module([node], []), sys.argv[1], "exec"), ns)
print(json.dumps([list(ns["verify_envelope"](c["envelope"], c["attestation"], None)) for c in json.load(sys.stdin)]))`;
  const run = spawnSync("python3", ["-c", py, VALIDATE], { input: JSON.stringify(cases), encoding: "utf8" });
  assert.equal(run.status, 0, run.stderr.slice(-1500));
  return JSON.parse(run.stdout);
}
const ENVELOPE = fs.readFileSync(path.join(ROOT, "jascon/examples/attestation-acme-2026.dsse"), "utf8");
const NOT_ITS_ENVELOPE = "payload != the Attestation's canonical form (attestation-binds)";
const UNVERIFIED = "signature UNVERIFIED - this page takes no key and verifies no signature";

test("the envelope of an Attestation, read without a key: this Attestation's or not, as the reference reads it, and never valid", () => {
  const env = JSON.parse(ENVELOPE), said = (att, text) => { const e = P.envelopeState(att, text); return [e.state, e.detail]; };
  /* [what, the Attestation, its envelope, what the page says] */
  const cases = [
    ["as it lies in the example folder", ATTESTATION, env, ["unverified", UNVERIFIED]],
    ["an annotation was added: annotations are outside the canonical form", { ...ATTESTATION, annotations: { note: "read on 2026-11-14" } }, env, ["unverified", UNVERIFIED]],
    ["no signature in the envelope: this page reads none either way", ATTESTATION, { ...env, signatures: [] }, ["unverified", UNVERIFIED]],
    ["the lifecycle was edited after signing", { ...ATTESTATION, lifecycle: "withdrawn" }, env, ["fail", NOT_ITS_ENVELOPE]],
    ["a subject was edited after signing", { ...ATTESTATION, "subject-semantic-digests": ATTESTATION["subject-semantic-digests"].slice(1) }, env, ["fail", NOT_ITS_ENVELOPE]],
    ["an empty payload", ATTESTATION, { ...env, payload: "" }, ["fail", NOT_ITS_ENVELOPE]],
    ["a payload that goes on after the Attestation's text", ATTESTATION, { ...env, payload: Buffer.concat([Buffer.from(env.payload, "base64"), Buffer.from(" ")]).toString("base64") }, ["fail", NOT_ITS_ENVELOPE]],
    ["a payload that stops before its end", ATTESTATION, { ...env, payload: Buffer.from(env.payload, "base64").subarray(0, -1).toString("base64") }, ["fail", NOT_ITS_ENVELOPE]],
    ["another payload type", ATTESTATION, { ...env, payloadType: "application/json" }, ["fail", "wrong payloadType"]],
    ["a payload that is no base64", ATTESTATION, { ...env, payload: env.payload.slice(0, -4) + "*==" + "=" }, ["fail", "payload is not valid base64"]],
    ["a payload with a wrong padding", ATTESTATION, { ...env, payload: env.payload.replace(/=*$/, "") + "A" }, ["fail", "payload is not valid base64"]],
    ["a payload that is no text", ATTESTATION, { ...env, payload: 7 }, ["fail", "payload is not valid base64"]],
    ["an envelope that is a list", ATTESTATION, [], ["fail", "envelope unreadable"]]];
  for (const [what, att, envelope, want] of cases) assert.deepEqual(said(att, JSON.stringify(envelope)), want, what);
  if (PYTHON) {
    /* the reference says `error` where the page says `fail`, with the same reason; without a key both say unverified */
    const ref = referenceEnvelopes(cases.map(([, attestation, envelope]) => ({ attestation, envelope })));
    cases.forEach(([what, , , want], i) => assert.deepEqual(want[0] === "fail" ? ["error", want[1]] : ["unverified", "no trusted key supplied for the signer"], ref[i], what));
  }
  /* what the reference decides before it reads an envelope */
  const { "envelope-ref": ref, ...unsigned } = ATTESTATION;
  assert.equal(ref, "attestation-acme-2026.dsse");
  assert.deepEqual(said(unsigned, ENVELOPE), ["none", "no envelope (unsigned attestation)"]);
  assert.deepEqual(said(ATTESTATION, undefined), ["missing", "envelope-ref 'attestation-acme-2026.dsse' does not resolve beside the manifest"]);
  assert.deepEqual(said(ATTESTATION, "{"), ["fail", "envelope unreadable"]);
  /* the page has no state and no word for a signature that holds: it verifies none */
  const pure = HTML.slice(HTML.indexOf("/* ==READER-PURE-START== */"), HTML.indexOf("/* ==READER-PURE-END== */"));
  assert.deepEqual([...new Set([...pure.slice(pure.indexOf("function envelopeState(")).matchAll(/state: "([^"]+)"/g)].map(m => m[1]))].sort(), ["fail", "missing", "none", "unverified"]);
});

test("the digest: the page's own SHA-256, used where the browser offers none, gives node's for every length of padding", () => {
  for (const n of [0, 1, 55, 56, 63, 64, 65, 119, 120, 1000]) {
    const bytes = Uint8Array.from({ length: n }, (_, i) => (i * 31 + 7) & 255);
    assert.equal(P.sha256Fallback(bytes), crypto.createHash("sha256").update(bytes).digest("hex"), `${n} bytes`);
  }
});

/* What the reference says about the Attestations it reads with one bundle folder.
   -> { ok, binds: [[id, line]], envelopes: [[id, state, detail]] }, each in the order of the ids;
      listed: the MANIFEST-1 failures, in the order the reference records them; others: its other failures */
function referenceAttested(dir) {
  const ref = reference(dir, "--as-of", "2026-11-14"), binds = [], envelopes = [], listed = [], others = [];
  for (const l of ref.notes.map(x => x.trim())) {
    let m;
    if ((m = /^binds: (\S+) = /.exec(l))) binds.push([m[1], l]);
    else if ((m = /^dsse: (\S+) = (.*)$/.exec(l)))
      envelopes.push([m[1], ...(m[2] === "no envelope (unsigned attestation)" ? ["none", m[2]] : m[2].startsWith("signature UNVERIFIED - ") ? ["unverified", "signature UNVERIFIED"]
        : m[2].startsWith("FAIL - ") ? ["fail", m[2].slice(7)] : ["not read by this test", m[2]])]);
  }
  for (const l of ref.out.split("\n")) {   // what failed the bundle is listed at the end, under the bundle's name
    const at = l.indexOf("[attestation-binds] ");
    let m;
    if (at >= 0 && (m = /^\[attestation-binds\] (\S+): /.exec(l.slice(at)))) binds.push([m[1], l.slice(at)]);
    else if ((m = /\] (\S+): (envelope-ref '.*' does not resolve beside the manifest)$/.exec(l))) envelopes.push([m[1], "missing", m[2]]);
    else if ((m = /^  - \[[^\]]*\] (.*\(MANIFEST-1: .*)$/.exec(l))) listed.push(m[1]);
    else if ((m = /^  - \[[^\]]*\] (.*)$/.exec(l)) && !/: dsse: /.test(l)) others.push(m[1]);
  }
  const order = (a, b) => byId(a[0], b[0]);
  return { ok: ref.ok, line: ref.line, out: ref.out, binds: binds.sort(order), envelopes: envelopes.sort(order), listed, others };
}
const WORD = { "full-match": "FULL MATCH", "semantic-match": "SEMANTIC MATCH", fail: "DOES NOT BIND" };
/* MANIFEST-1 as the reference words it, after the id of the Attestation */
const MANIFEST_1 = ": an Attestation is listed in the content manifest (MANIFEST-1: Attestations are excluded from the content manifest by definition, " +
  "D3.1 - an Attestation lies beside a manifest and is never an entry of one)";
/* What the page says about the Attestations of one bundle folder, held to itself and to the reference: the word
   and its colour follow the verdict; a failure is shown exactly where the line is the reference's failure; every
   line and every envelope is read as the reference reads it; an Attestation the manifest lists carries the
   reference's MANIFEST-1 sentence, and no other does; the page shows a failure exactly when the reference fails
   the bundle. `shown`: what R.attested() gave for the folder. `also`: failures of the reference that the page
   is known not to state (a rule it does not hold a bundle to), each a pattern. */
function asTheReference(shown, dir, what, also = []) {
  for (const a of shown) {
    assert.equal(a.listed, String(a.listedError !== null), `${what}: ${a.id} is marked as listed exactly where the sentence stands`);
    if (a.listedError !== null) assert.equal(a.listedError, a.id + MANIFEST_1, `${what}: ${a.id}`);
    assert.equal(a.word, WORD[a.verdict], `${what}: ${a.id}`);
    assert.equal(a.fails, String(a.line.startsWith("[attestation-binds] ")), `${what}: ${a.id} is shown as a failure exactly where the line is one`);
    assert.equal(a.shownAs, a.verdict === "full-match" ? "verdict-ok" : a.fails === "true" ? "verdict-bad" : "verdict-warn", `${what}: ${a.id}`);
    assert.ok(["none", "missing", "fail", "unverified"].includes(a.envelope), `${what}: ${a.id}: ${a.envelope}`);
    if (a.envelope === "unverified") assert.equal(a.envelopeText, UNVERIFIED);
  }
  if (!REFERENCE) return;
  const ref = referenceAttested(dir);
  assert.deepEqual(shown.map(a => [a.id, a.line]), ref.binds, `${what}: the line of every Attestation is the reference's`);
  assert.deepEqual(shown.map(a => [a.id, a.envelope, a.envelope === "unverified" ? "signature UNVERIFIED" : a.envelopeText.replace(/^FAIL - /, "")]), ref.envelopes, `${what}: every envelope is read as the reference reads it`);
  assert.deepEqual(shown.filter(a => a.listed === "true").map(a => a.listedError), ref.listed, `${what}: an Attestation the manifest lists fails with the reference's sentence, each in the reference's order`);
  assert.equal(shown.some(a => a.fails === "true" || a.envelope === "fail" || a.envelope === "missing" || a.listed === "true"), !ref.ok, `${what}: the page shows a failure exactly when the reference fails the bundle — ${ref.line}`);
  /* and the reference fails the bundle for nothing else, but for what a test names */
  assert.deepEqual(ref.others.filter(e => !also.some(re => re.test(e))), [], `${what}: no other failure in the reference`);
  for (const re of also) assert.ok(ref.others.some(e => re.test(e)), `${what}: the reference states ${re}`);
}
/* the Attestations beside a manifest by the reference's rule: a .json of the manifest's folder that the manifest does not list and that types as one */
function besideOf(dir) {
  const manifest = JSON.parse(fs.readFileSync(path.join(dir, "content-manifest.json"), "utf8"));
  return fs.readdirSync(dir).filter(n => n.endsWith(".json") && n !== "content-manifest.json" && !manifest.objects.some(e => e.path === n))
    .map(n => [n, JSON.parse(fs.readFileSync(path.join(dir, n), "utf8"))]).filter(([, o]) => P.inferType(o) === "attestation").sort((a, b) => byId(a[1].id, b[1].id));
}

test("the Attestations beside a manifest: the example folder, the IFA bundle and the worked pack, loaded as they lie, show the reference's verdict for each, every subject with both digests, and how many of each there are",
  OPTS, () => withReader(async R => {
    const { page } = R;
    const asFolder = new Map();   // what each folder says when the button opens it
    for (const dir of [EXAMPLES, IFA, PACK]) {
      const what = path.relative(ROOT, dir), manifestBytes = fs.readFileSync(path.join(dir, "content-manifest.json")), manifest = JSON.parse(manifestBytes);
      const listed = new Map(manifest.objects.map(e => [e.id, e["semantic-digest"]])), beside = besideOf(dir);
      assert.ok(beside.length >= 1, `${what} has an Attestation beside its manifest`);
      await R.load(dir);
      const shown = await R.attested();
      asTheReference(shown, dir, what);
      assert.deepEqual(shown.map(a => a.id), beside.map(([, a]) => a.id), `${what}: every Attestation beside the manifest is shown, in the order of the ids`);
      /* the verdicts arrive after the bundle is shown: stage 5, when it is up, is drawn again with them */
      await page.evaluate(async () => { for (const x of document.querySelectorAll("#view-stagefn [data-attestation]")) x.dataset.binds = "drawn before"; await judgeAttestations(); });
      assert.deepEqual(await page.locator("#view-stagefn [data-attestation]").evaluateAll(l => l.map(x => x.dataset.binds)), shown.map(a => a.verdict), what);
      for (const [i, a] of shown.entries()) {
        /* Worked out here from the files, without the page's code: which manifest is bound, and per subject which
           object, the signed digest, and the digest the manifest records for the object as delivered. */
        const att = beside[i][1], bound = att["content-manifest-digest"];
        const manifestBound = bound === sha256(manifestBytes) ? "this" : fs.existsSync(path.join(dir, "packs/sha256", bound.slice(7))) ? "kept-pack" : "other";
        const subjects = att["subject-semantic-digests"].map(sj => ({ status: listed.get(sj.id) === sj["semantic-digest"] ? "match" : listed.has(sj.id) ? "differs" : "absent",
          id: sj.id, signed: sj["semantic-digest"], delivered: listed.get(sj.id) ?? "not an object the manifest lists" }));
        assert.equal(a.manifest, manifestBound, a.id);
        assert.deepEqual(a.subjects, subjects, a.id);
        assert.equal(a.verdict, subjects.some(sj => sj.status !== "match") ? "fail" : manifestBound === "other" ? "semantic-match" : "full-match", a.id);
        assert.equal(a.envelope, att["envelope-ref"] ? (fs.existsSync(path.join(dir, att["envelope-ref"])) ? "unverified" : "missing") : "none", a.id);
      }
      /* how many of each: the objects the manifest lists, and the Attestations beside it, which are not among them */
      await R.view("overview");
      assert.equal(await R.text(page.locator("#ov-listed")), String(manifest.objects.length), what);
      assert.equal(await R.text(page.locator("#ov-beside")), String(beside.length), what);
      assert.equal(await page.locator("#ov-other").count(), 0, what);
      assert.equal(await page.locator("[data-beside]").count(), 0, `${what}: a folder was looked into; nothing is said about how`);
      assert.deepEqual(await page.locator("[data-ov-binds]").evaluateAll(l => l.map(x => [x.dataset.ovBinds, x.className, x.querySelector("a").textContent])), shown.map(a => [a.verdict, a.shownAs, a.id]), what);
      const pill = await page.locator("#pill-bundle").getAttribute("title");
      assert.ok(pill.startsWith(`${manifest.objects.length} object${manifest.objects.length === 1 ? "" : "s"} · ${beside.length} attestation${beside.length > 1 ? "s" : ""} beside the manifest · `), pill);
      assert.match(await R.log(), new RegExp(` — ${manifest.objects.length} the manifest lists, ${beside.length} Attestation\\(s\\) beside the manifest$`, "m"), what);
      assert.equal(await page.evaluate(() => document.getElementById("app").scrollWidth <= innerWidth), true, `${what}: the page is no wider than the window, however long the bundle's name is`);
      /* in a narrow window the numbers are still read: the tagline gives way first, then the name */
      await page.setViewportSize({ width: 1000, height: 1100 });
      assert.equal(await page.evaluate(() => { const range = document.createRange(), pill = document.getElementById("pill-bundle"), text = pill.firstChild;
        range.setStart(text, 0); range.setEnd(text, text.data.indexOf("beside the manifest") + "beside the manifest".length);
        return range.getBoundingClientRect().right <= pill.getBoundingClientRect().right - 10 && document.getElementById("app").scrollWidth <= innerWidth; }), true, `${what}: at 1000 px the pill shows how many of each`);
      await page.setViewportSize({ width: 1500, height: 1100 });
      /* the object browser lists them too, with where each lies and what it binds; the detail says what stage 5 says */
      await R.view("browser");
      assert.equal(await page.locator(".objrow").count(), manifest.objects.length + beside.length, what);
      for (const [i, a] of shown.entries()) {
        assert.equal(await R.text(page.locator(`.objrow[data-id="${a.id}"] [data-list-binds="${a.verdict}"]`)), "beside the manifest · " + a.word, a.id);
        assert.equal(await page.locator(`.objrow[data-id="${a.id}"] [data-list-binds]`).evaluate(x => { const text = document.createRange(); text.selectNodeContents(x);
          return text.getBoundingClientRect().right <= x.closest(".objrow").getBoundingClientRect().right - 10; }), true, `${a.id}: the line is not cut, however long the id is`);
        const d = await R.detail(a.id);
        assert.equal(await d.locator("[data-binds-line]").evaluate(x => x.textContent), a.line, a.id);
        assert.equal(await d.locator("[data-subject]").count(), a.subjects.length, a.id);
        assert.match(await R.text(d), new RegExp(`where it lies beside the manifest, as ${beside[i][0].replace(/\./g, "\\.")} — not listed`), a.id);
      }
      /* the same files in reverse order say the same: nothing shown depends on the order in which files arrive */
      await page.evaluate(async () => { await loadFileList([...document.getElementById("folderpick").files].reverse()); });
      await page.waitForFunction(() => document.body.dataset.binds === "done");
      assert.deepEqual(await R.attested(), shown, `${what}: in reverse order`);
      asFolder.set(dir, shown);
    }

    /* A folder dropped on the page goes the way of the button, the envelope included: until 1.12.0 a drop handed
       on its .json files only, so the envelope of a dropped bundle did not resolve. The drop is made here of the
       entries a browser hands over, with the files' own bytes. */
    const tree = dir => fs.readdirSync(dir, { withFileTypes: true }).map(e => e.isDirectory() ? { name: e.name, children: tree(path.join(dir, e.name)) }
      : { name: e.name, base64: fs.readFileSync(path.join(dir, e.name)).toString("base64") });
    const lines = await page.locator("#log > div").count();
    await page.evaluate(root => {
      const entry = (node, parent) => node.children
        ? { isDirectory: true, createReader() { let sent = false; return { readEntries: done => { done(sent ? [] : node.children.map(c => entry(c, parent + "/" + node.name))); sent = true; } }; } }
        : { isFile: true, fullPath: parent + "/" + node.name, file: done => done(new File([Uint8Array.from(atob(node.base64), ch => ch.charCodeAt(0))], node.name)) };
      document.body.dispatchEvent(Object.assign(new Event("drop", { bubbles: true }), { dataTransfer: { items: [{ webkitGetAsEntry: () => entry(root, "") }] } }));
    }, { name: "dropped", children: tree(PACK) });
    await page.waitForFunction(n => [...document.querySelectorAll("#log > div")].slice(n).some(x => /indexed \d+ objects/.test(x.textContent)) && document.body.dataset.binds === "done", lines);
    assert.deepEqual(await R.attested(), asFolder.get(PACK), "a dropped folder: as the button");

    /* The example folder opened as files ("Open JSON file(s)…"). Files come without their folders: the Attestations
       among them are found and held to the manifest, an envelope is read where it was opened along, and a pack
       manifest the bundle keeps cannot be among them - which the page says where it matters. */
    const files = ext => fs.readdirSync(EXAMPLES).filter(n => ext.some(e => n.endsWith(e))).map(n => path.join(EXAMPLES, n));
    await R.load(files([".json", ".dsse"]), "#filepick");
    let shown = await R.attested();
    assert.deepEqual(shown.map(a => [a.id.split("/").pop(), a.verdict, a.manifest, a.envelope]), [["acme-2026", "full-match", "this", "unverified"], ["server-7-hardening-3", "semantic-match", "other", "unverified"]]);
    assert.equal(await page.locator("#view-stagefn [data-binds-caveat]").count(), 1, "the one that binds another manifest says that no kept pack manifest was looked for");
    await R.view("overview");
    assert.equal(await page.locator("[data-beside]").getAttribute("data-beside"), "files");
    assert.equal(await R.text(page.locator("#ov-beside")), "2");
    await R.load(files([".json"]), "#filepick");
    shown = await R.attested();
    assert.deepEqual(shown.map(a => [a.envelope, a.envelopeText]), ["acme-2026", "dbvendor-server-7-advice"].map(n => ["missing", `FAIL - envelope-ref 'attestation-${n}.dsse' does not resolve beside the manifest`]),
      "an envelope that was not opened along does not resolve, and is not passed over");
  }));

test("changed copies: a changed subject fails an active Attestation and is only reported for a withdrawn one; another manifest is a Semantic Match; an edited signed Attestation no longer matches its envelope - each as the reference says",
  OPTS, () => withReader(async R => {
    const { page } = R;
    const A = "attestation-ifa-ato.json", PA = "attestation-dbvendor-server-7-advice.json", ZERO = "sha256:" + "0".repeat(64);
    let n = 0;
    const copy = (src, name, change, remove = []) => {
      const dir = path.join(R.tmp, "changed-" + ++n, "bundle");
      fs.cpSync(src, dir, { recursive: true });
      const att = JSON.parse(fs.readFileSync(path.join(dir, name), "utf8"));
      change(att);
      fs.writeFileSync(path.join(dir, name), JSON.stringify(att, null, 1) + "\n");
      for (const r of remove) fs.rmSync(path.join(dir, r));
      return dir;
    };
    const subject = a => { a["subject-semantic-digests"][0]["semantic-digest"] = ZERO; };
    const ISSUE_AGAIN = "What can be done: the signer issues the Attestation again (a new version, signed again), or it is taken out of the bundle. ";
    const UNSIGNED_WAY = ISSUE_AGAIN + "This one names no envelope, so setting its lifecycle to withdrawn is a way out as well: it is then reported and fails nothing.";
    const SIGNED_NO_WAY = ISSUE_AGAIN + "Setting its lifecycle to withdrawn is no way out for this one: it names an envelope, and an Attestation that was edited no longer matches its envelope.";
    /* [what, the folder, the file, the change, files removed, then: verdict, shown as a failure, first subject, envelope, what can be done] */
    const cases = [
      ["a subject's digest changed in an active Attestation", IFA, A, subject, [], "fail", "true", "differs", "none", UNSIGNED_WAY],
      ["a subject the bundle does not hold", IFA, A, a => { a["subject-semantic-digests"][0].id += "-not-delivered"; }, [], "fail", "true", "absent", "none", UNSIGNED_WAY],
      ["the manifest digest changed", IFA, A, a => { a["content-manifest-digest"] = "sha256:" + "b".repeat(64); }, [], "semantic-match", "false", "match", "none", null],
      ...["withdrawn", "deprecated", "draft"].map(lc => [`${lc}, with a changed subject`, IFA, A, a => { subject(a); a.lifecycle = lc; }, [], "fail", "false", "differs", "none", null]),
      ["withdrawn, and it still binds", IFA, A, a => { a.lifecycle = "withdrawn"; }, [], "full-match", "false", "match", "none", null],
      ["signed, the lifecycle edited to withdrawn", PACK, PA, a => { a.lifecycle = "withdrawn"; }, [], "full-match", "false", "match", "fail", null],
      ["signed, a subject's digest changed", PACK, PA, subject, [], "fail", "true", "differs", "fail", SIGNED_NO_WAY],
      ["signed, the envelope taken away", PACK, PA, () => {}, [PA.replace(/json$/, "dsse")], "full-match", "false", "match", "missing", null],
      ["the envelope reference removed and the lifecycle withdrawn: an unsigned record", PACK, PA, a => { a.lifecycle = "withdrawn"; delete a["envelope-ref"]; }, [], "full-match", "false", "match", "none", null]];
    for (const [what, src, name, change, remove, verdict, fails, first, envelope, todo] of cases) {
      const dir = copy(src, name, change, remove);
      await R.load(dir);
      const shown = await R.attested();
      assert.equal(shown.length, 1, what);
      const [a] = shown;
      assert.deepEqual([a.verdict, a.fails, a.subjects[0]?.status, a.envelope, a.todo], [verdict, fails, first, envelope, todo], what);
      asTheReference(shown, dir, what);
      if (a.envelope === "fail") assert.equal(a.envelopeText, "FAIL - " + NOT_ITS_ENVELOPE, what);
      assert.deepEqual(await page.locator("#view-stagefn [data-binds-envelope]").evaluateAll(l => l.map(x => [x.className, x.textContent])),
        ["fail", "missing"].includes(envelope) ? [["verdict-bad", "· ✗ and its envelope fails (below)"]] : [], `${what}: the card names a failing envelope beside the verdict, which is about digests`);
      if (first === "differs") {
        const delivered = JSON.parse(fs.readFileSync(path.join(dir, "content-manifest.json"), "utf8")).objects.find(e => e.id === a.subjects[0].id)["semantic-digest"];
        assert.deepEqual([a.subjects[0].signed, a.subjects[0].delivered], [ZERO, delivered], `${what}: the signed digest beside the delivered one`);
      }
      if (first === "absent") assert.equal(a.subjects[0].delivered, "not an object the manifest lists", what);
      /* the overview says it in a line: a failure in red, what is only reported not */
      await R.view("overview");
      const line = page.locator("[data-ov-binds]");
      assert.equal(await line.getAttribute("class"), verdict === "full-match" ? "verdict-ok" : fails === "true" ? "verdict-bad" : "verdict-warn", what);
      assert.ok((await R.text(line)).startsWith(verdict !== "fail" ? `${WORD[verdict]} (` : fails === "true" ? "✗ DOES NOT BIND — a failure · " : "DOES NOT BIND — reported, not a failure · "), `${what}: ${await R.text(line)}`);
      /* an envelope that fails is named there too, beside whatever the digests say */
      assert.deepEqual(await line.locator("[data-ov-envelope]").evaluateAll(l => l.map(x => [x.className, x.textContent])),
        ["fail", "missing"].includes(envelope) ? [["verdict-bad", "✗ its envelope: " + a.envelopeText]] : [], what);
    }

    /* Attestations are shown in the order of their ids, as the reference reports them, not in that of their files */
    const renamed = path.join(R.tmp, "renamed", "examples");
    fs.cpSync(EXAMPLES, renamed, { recursive: true });
    fs.renameSync(path.join(renamed, "attestation-acme-2026.json"), path.join(renamed, "z-attestation-acme-2026.json"));
    await R.load(renamed);
    const inOrder = await R.attested();
    assert.deepEqual(inOrder.map(x => [x.id, x.verdict]), [["https://agency-x.example/attestation/acme-2026", "full-match"], ["https://dbvendor.example/attestation/server-7-hardening-3", "full-match"]]);
    asTheReference(inOrder, renamed, "the example folder with an Attestation's file renamed");

    /* Two manifests in what was opened: the one highest up is the bundle's, whichever file arrives first. An
       Attestation in a folder below it does not lie beside it: it is held to the bundle all the same and fails
       nothing, and its subjects are compared with the objects the manifest lists, not with every object loaded. */
    const outer = path.join(R.tmp, "nested", "pack");
    fs.cpSync(PACK, outer, { recursive: true });
    fs.cpSync(IFA, path.join(outer, "below"), { recursive: true });
    await R.load(outer);
    const both = await R.attested();
    assert.deepEqual(both.map(x => [x.id.split("/").pop(), x.verdict, x.fails, x.manifest, x.subjects.map(sj => sj.status).join()]),
      [["server-7-hardening-3", "full-match", "false", "this", "match"], ["ifa-ato", "fail", "false", "other", "absent,absent,absent"]]);
    const below = page.locator('#view-stagefn [data-attestation="https://ifa.gov/goodread/attestation/ifa-ato"]');
    assert.match(await R.text(below), /DOES NOT BIND — the Attestation is active; it was not read with this bundle, so it fails none /);
    assert.match(await R.text(below), /where it lies a file the manifest does not list and that does not lie beside it \(below\/attestation-ifa-ato\.json\) — not read with the bundle/);
    await R.view("overview");
    assert.deepEqual([await R.text(page.locator("#ov-listed")), await R.text(page.locator("#ov-beside")), await R.text(page.locator("#ov-other"))], ["1", "1", "17"]);
    await page.evaluate(async () => { await loadFileList([...document.getElementById("folderpick").files].reverse()); });
    await page.waitForFunction(() => document.body.dataset.binds === "done");
    assert.deepEqual(await R.attested(), both, "the same files in reverse order: the same manifest, the same verdicts");
    if (REFERENCE) {
      const ref = referenceAttested(outer);
      assert.deepEqual([ref.ok, ref.binds.map(b => b[0])], [true, ["https://dbvendor.example/attestation/server-7-hardening-3"]], "the reference reads the one beside the manifest: " + ref.line);
    }

    /* Where the page and the reference differ, measured and not hidden. The page reads an object by its fields and
       checks no schema; the reference reads a file beside the manifest as an Attestation only when the kernel schema
       accepts it. An "Attestation" without a subject is none to the kernel (minItems 1): the reference does not read
       the file and says nothing about it; the page shows it, as what the primitive makes of it, and says under which
       proviso a validator fails the bundle. */
    const dir = copy(IFA, A, a => { a["subject-semantic-digests"] = []; });
    await R.load(dir);
    const [a] = await R.attested();
    assert.deepEqual([a.verdict, a.fails, a.subjects.length, a.line.replace(/^\S+ \S+ /, "").replace(/ \(B\.1\.7.*$/, "")], ["fail", "true", 0, "it names no subject - this manifest"]);
    assert.match(await R.text(page.locator("#view-stagefn [data-attestation]")), /DOES NOT BIND — a failure: the Attestation is active, and validate_core\.py fails the bundle for it — provided the kernel schema accepts the file as an Attestation, which this page does not check/);
    if (REFERENCE) {
      const ref = referenceAttested(dir);
      assert.deepEqual([ref.ok, ref.binds, ref.envelopes], [true, [], []], "the reference does not read a file the kernel schema refuses: " + ref.line);
    }
  }));

test("from a URL: the Attestations beside a manifest are found through the server's listing of the folder or by the names the link gives; with neither the page says that it did not look",
  OPTS, () => withReader(async R => {
    const { page } = R;
    const folder = new Map();   // what each folder says when it is opened as a folder
    for (const dir of [EXAMPLES, IFA, PACK]) { await R.load(dir); folder.set(dir, await R.attested()); }
    const names = dir => besideOf(dir).map(([name]) => name).sort();   // the test knows the names; the page lists the folder or is given them
    const web = R.watch(await page.context().newPage());
    const overview = async () => {
      await web.click('.navitem[data-view="overview"]');
      return [await web.locator("[data-beside]").getAttribute("data-beside"), await web.locator("#ov-beside").innerText(), await web.locator("#pill-bundle").getAttribute("title")];
    };
    const loaded = () => web.waitForFunction(n => [...document.querySelectorAll("#log > div")].slice(n).some(x => /indexed \d+ objects/.test(x.textContent)) && document.body.dataset.binds === "done", 0);
    const linked = async (server, dir, more = "") => { await web.goto("about:blank"); await web.goto(`${server.reader}#load=${server.url(dir)}${more}`); await loaded(); return overview(); };
    const lists = await serve(R, "listing"), silent = await serve(R, null), other = await serve(R, "page");
    R.quiet.push(new RegExp(`^${silent.at}/.*/$`), new RegExp(`^${silent.at}/.*/(packs/sha256/[0-9a-f]{64}|not-there\\.json)$`));   // a folder, a pack manifest that is not kept, a file the link names and the server does not have
    try {
      for (const dir of [EXAMPLES, IFA, PACK]) {
        const what = path.relative(ROOT, dir), count = String(folder.get(dir).length);
        /* a server that lists its folders: as the folder */
        let [how, beside, pill] = await linked(lists, dir);
        assert.deepEqual([how, beside], ["listing", count], what);
        assert.deepEqual(await R.attested(web), folder.get(dir), `${what}, listed by the server: as the folder`);
        /* a server that lists none, and a link that names nothing: none is found, and the page says that it did not look */
        for (const [server, why] of [[silent, "refuses the folder"], [other, "answers the folder with another page"]]) {
          [how, beside, pill] = await linked(server, dir);
          assert.deepEqual([how, beside], ["no-listing", "0"], `${what}: the server ${why}`);
          assert.match(pill, /^(1 object|(?!1 )\d+ objects) · attestations beside the manifest not looked for · /, what);
          assert.match(await R.text(web.locator("[data-beside]")), /^— not looked for: this server lists no folders, and nothing was named\. Add &attestation=<file name> to the link, or open the folder$/);
          assert.match(await web.locator("#log").innerText(), /this server lists no folders: an Attestation beside the manifest cannot be found from a URL/);
          assert.deepEqual(await R.attested(web), [], what);
        }
        /* the same server, and a link that names them: as the folder - also the one that binds a pack manifest the
           bundle keeps, which is asked for under the name its digest gives it */
        [how, beside] = await linked(silent, dir, "&attestation=" + names(dir).join(","));
        assert.deepEqual([how, beside], ["named", count], what);
        assert.deepEqual(await R.attested(web), folder.get(dir), `${what}, named in the link: as the folder`);
        assert.equal(await web.locator("[data-beside-refused]").count(), 0, what);
      }
      /* names that give no Attestation are said, each with its reason, and none of them is shown as one */
      const [how, beside] = await linked(silent, EXAMPLES, "&attestation=attestation-acme-2026.json,not-there.json,authorization-summary.md,req-konf-14-1.json,packs/x.json");
      assert.deepEqual([how, beside], ["named", "1"]);
      assert.deepEqual(await web.locator("[data-beside-refused]").evaluateAll(l => l.map(x => x.textContent)), [
        "✗ not-there.json: not fetched (HTTP 404)", "✗ authorization-summary.md: the file is no Attestation",
        "✗ req-konf-14-1.json: the manifest lists this file, so it does not lie beside it", "✗ packs/x.json: an Attestation beside the manifest is named by its file name, without a folder"]);
      assert.deepEqual((await R.attested(web)).map(a => a.id), ["https://agency-x.example/attestation/acme-2026"]);
      /* the button asks for the address and then for the names */
      R.answers.push(silent.url(PACK), " " + names(PACK).join(" , "));
      await web.click("#btn-url");
      await web.waitForFunction(() => document.getElementById("pill-bundle").title.startsWith("1 object · 1 attestation beside the manifest") && document.body.dataset.binds === "done");
      assert.deepEqual(await R.attested(web), folder.get(PACK), "by the button, with a name");
      R.answers.push(silent.url(IFA));   // and no name
      await web.click("#btn-url");
      await web.waitForFunction(() => document.getElementById("pill-bundle").title.startsWith("16 objects · attestations beside the manifest not looked for"));
    } finally { lists.close(); silent.close(); other.close(); }
  }));

test("an export never lists an Attestation: it is written beside the manifest, and the reference reads it there; a pasted Attestation fails no bundle",
  OPTS, () => withReader(async R => {
    const { page } = R;
    const stored = created => ({ v: 2, ns: "https://example.org/my", tailor: { label: "my-tailoring", selects: [], excludes: [], operations: [] },
      system: { title: "My System", components: [], implementations: [] }, assess: { scopeKey: "", performer: "", results: {} }, created });
    const exported = async (created, name) => {
      await page.evaluate(w => localStorage.setItem("scr-work", JSON.stringify(w)), stored(created));
      await page.reload();
      const dir = unzipTo(await R.download("#btn-export-ws"), path.join(R.tmp, name));
      return { dir, manifest: JSON.parse(fs.readFileSync(path.join(dir, "content-manifest.json"), "utf8")), log: await R.log() };
    };

    /* a workspace that holds an unsigned Attestation and its three subjects (the first binds vector) */
    const c = BINDS[0], att = c.attestation;
    let x = await exported([...c.objects, att], "unsigned");
    let shown = await R.attested();
    assert.deepEqual(shown.map(a => [a.id, a.verdict, a.envelope]), [[att.id, "not-judged", "none"]], "without a bundle an Attestation is held to none");
    assert.deepEqual(x.manifest.objects.map(e => e.id), c.objects.map(o => o.id), "the manifest lists the three objects and no Attestation");
    for (const e of x.manifest.objects) assert.notEqual(P.inferType(JSON.parse(fs.readFileSync(path.join(x.dir, e.path), "utf8"))), "attestation", e.path);
    assert.deepEqual(fs.readdirSync(x.dir).sort(), ["attestation-ato.json", "content-manifest.json", "objects"], "the Attestation lies beside the manifest");
    assert.deepEqual(JSON.parse(fs.readFileSync(path.join(x.dir, "attestation-ato.json"), "utf8")), att, "as it was held");
    /* the manifest is new, so what bound another one with unchanged subjects is a Semantic Match: the page says so when it writes, and the reference says the same of the export */
    const SEMANTIC = `binds: ${att.id} = SEMANTIC MATCH [3 subject(s) of this bundle; another manifest: the content is proven, the packaging was altered]`;
    assert.ok(x.log.includes("in this export — " + SEMANTIC + "\n"), x.log.slice(-900));
    assert.match(x.log, /workspace bundle exported: 3 objects \+ content-manifest with both digests \+ 1 Attestation\(s\) beside the manifest, not listed \(D3\.1\) \([\d.]+ kB zip\) — loads back into this reader and nothing fails in what this page checks \(closure-required references, facet and method keys, Attestations\); it runs no kernel schema and checks no facet payload$/m);
    await R.load(x.dir);
    shown = await R.attested();
    assert.deepEqual(shown.map(a => [a.verdict, a.fails, a.manifest, a.line]), [["semantic-match", "false", "other", SEMANTIC]]);
    asTheReference(shown, x.dir, "the export, loaded again");
    assert.ok((await page.locator("#pill-bundle").getAttribute("title")).startsWith("3 objects · 1 attestation beside the manifest · "));

    /* A manifest that lists its Attestation, as reader 1.12.0 wrote it. D3.1 excludes that, and since 2026-11-14
       the reference refuses it in every bundle (MANIFEST-1; until then it passed: 5 pass, 0 fail). So does the
       page, in the reference's words; the Attestation is still held to its subjects like any other and counted
       among the objects the manifest lists, as the reference counts it, and the page says where it lies. */
    const moved = "objects/att/attestation-ato.json", unsigned = x;
    const listedBy = async (name, listedAtt) => {
      const dir = path.join(R.tmp, name, "bundle"), bytes = Buffer.from(JSON.stringify(listedAtt, null, 1) + "\n");
      fs.cpSync(unsigned.dir, dir, { recursive: true });
      fs.rmSync(path.join(dir, "attestation-ato.json"));
      fs.mkdirSync(path.join(dir, "objects/att"));
      fs.writeFileSync(path.join(dir, moved), bytes);
      fs.writeFileSync(path.join(dir, "content-manifest.json"), JSON.stringify({ ...unsigned.manifest, objects: [...unsigned.manifest.objects,
        { id: listedAtt.id, version: listedAtt.version, "package-digest": sha256(bytes), "semantic-digest": await P.semanticDigest(listedAtt), path: moved }] }, null, 1) + "\n");
      return dir;
    };
    /* one whose subject was changed after signing: listed or not, an active Attestation that does not bind fails the bundle */
    const changed = await listedBy("listed-changed", { ...att, "subject-semantic-digests": att["subject-semantic-digests"].map((sj, i) => i ? sj : { ...sj, "semantic-digest": "sha256:" + "0".repeat(64) }) });
    await R.load(changed);
    shown = await R.attested();
    assert.deepEqual(shown.map(a => [a.verdict, a.fails, a.listed, a.subjects.map(sj => sj.status).join()]), [["fail", "true", "true", "differs,match,match"]]);
    asTheReference(shown, changed, "a manifest that lists an Attestation that does not bind");
    const listing = await listedBy("listed", att);
    await R.load(listing);
    shown = await R.attested();
    assert.deepEqual(shown.map(a => [a.verdict, a.fails, a.manifest, a.listed, a.listedError]), [["semantic-match", "false", "other", "true", att.id + MANIFEST_1]]);
    asTheReference(shown, listing, "a manifest that lists its Attestation");
    assert.match(await R.text(page.locator("#view-stagefn [data-attestation]")), /where it lies listed by the manifest, as objects\/att\/attestation-ato\.json — D3\.1 excludes that: an Attestation lies beside a manifest and is never an entry of one \(MANIFEST-1\)\. It is held to what it binds all the same/);
    await R.view("overview");
    assert.deepEqual([await R.text(page.locator("#ov-listed")), await R.text(page.locator("#ov-beside"))], ["4", "0"]);
    assert.match(await R.text(page.locator("[data-ov-binds]")), /^SEMANTIC MATCH \(another manifest\) · \S+ ✗ listed by the manifest \(MANIFEST-1\)$/);

    /* a signed Attestation in a workspace: the workspace holds objects and no envelope files, so it leaves without
       its envelope - not listed either, and the page says that a validator fails the export for it */
    const packAtt = besideOf(PACK)[0][1], packManifest = json("jascon/example-packs/dbvendor-server-7-advice/content-manifest.json");
    const subjectOfPack = JSON.parse(fs.readFileSync(path.join(PACK, packManifest.objects[0].path), "utf8"));
    x = await exported([subjectOfPack, packAtt], "signed");
    assert.deepEqual(x.manifest.objects.map(e => e.id), [subjectOfPack.id]);
    assert.deepEqual(fs.readdirSync(x.dir).sort(), ["attestation-server-7-hardening-3.json", "content-manifest.json", "objects"]);
    const UNRESOLVED = `envelope-ref '${packAtt["envelope-ref"]}' does not resolve beside the manifest`;
    assert.ok(x.log.includes(`in this export — dsse: ${packAtt.id} = FAIL - ${UNRESOLVED} (the workspace holds no envelope files)\n`), x.log.slice(-900));
    assert.match(x.log, /— loads back into this reader and validate_core\.py fails it: 1 line\(s\) above say why$/m);
    if (REFERENCE) {
      const ref = referenceAttested(x.dir);
      assert.equal(ref.ok, false, ref.line);
      assert.deepEqual(ref.envelopes, [[packAtt.id, "missing", UNRESOLVED]]);
      assert.deepEqual(ref.binds, [[packAtt.id, `binds: ${packAtt.id} = SEMANTIC MATCH [1 subject(s) of this bundle; another manifest: the content is proven, the packaging was altered]`]]);
    }

    /* An Attestation leaves as it is held, whatever is in it. An object written in a workbench has its plain-text
       title written as a language map on the way out; an Attestation is somebody's statement and is not rewritten. */
    const plain = { ...att, title: "Authorization, as somebody typed it" };
    x = await exported([...c.objects, plain], "plain");
    assert.deepEqual(JSON.parse(fs.readFileSync(path.join(x.dir, "attestation-ato.json"), "utf8")), plain);

    /* an export of what was written here does not carry the Attestations of the loaded bundle: they bind that delivery */
    await page.evaluate(() => localStorage.removeItem("scr-work"));
    await page.reload();
    await R.load(EXAMPLES);
    await R.view("stage:tailor");
    const resolved = unzipTo(await R.download("#wb-t-export-resolved"), path.join(R.tmp, "resolved"));
    assert.deepEqual(fs.readdirSync(resolved).sort(), ["content-manifest.json", "objects"]);
    assert.match(await R.log(), /resolved package exported: .* — the 2 Attestation\(s\) of the loaded bundle are not carried: they bind that delivery, and this export delivers other objects$/m);

    /* an Attestation pasted beside a loaded bundle is held to it all the same, and fails nothing: it did not come with it */
    R.answers.push(JSON.stringify(att));
    await page.click("#btn-paste");
    await page.waitForFunction(() => document.body.dataset.binds === "done");
    const pasted = page.locator("#detail [data-attestation]");
    assert.deepEqual([await pasted.getAttribute("data-binds"), await pasted.getAttribute("data-binds-fails"), await pasted.locator("[data-binds-word]").getAttribute("class")], ["fail", "false", "verdict-warn"]);
    assert.match(await R.text(pasted), /^DOES NOT BIND — the Attestation is active; it was not read with this bundle, so it fails none /);
    assert.match(await R.text(pasted), /where it lies pasted — it did not come with the loaded bundle/);
    assert.equal(await pasted.locator("[data-binds-todo]").count(), 0, "what can be done is said where a bundle fails");
    await R.view("overview");
    assert.deepEqual([await R.text(page.locator("#ov-listed")), await R.text(page.locator("#ov-beside")), await R.text(page.locator("#ov-other"))], ["24", "2", "1"]);
    assert.equal(await page.locator("[data-ov-binds]").count(), 2, "the overview lists the two that came with the bundle");
  }));

/* ---------- 12. MANIFEST-1: no content manifest lists an Attestation (backlog #75; specification D3.11) ---------- */
const LISTED = json("jascon/conformance/attestation-vectors.json")["listed-vectors"];

test("MANIFEST-1: each of the 8 listed vectors gets one failure per listed Attestation from the page's own function, in the reference's words and in the order of the ids", () => {
  assert.equal(LISTED.length, 8);   // a vector added to the family is looked at here before this number moves
  const seen = new Set();
  for (const c of LISTED) {
    for (const o of c.objects) assert.ok(![null, "manifest"].includes(P.inferType(o)), `${c.name}: ${o.id} is typed`);
    const errs = P.listedAttestationErrors(c.objects);
    assert.equal(errs.length, c["expected-fails"], c.name);
    assert.deepEqual(errs, c["expected-ids"].map(id => id + MANIFEST_1), c.name);
    const atts = c.objects.filter(o => P.inferType(o) === "attestation");
    seen.add(errs.length + " listed");
    for (const a of atts) { seen.add("lifecycle " + a.lifecycle); seen.add("envelope-ref" in a ? "signed" : "unsigned"); }
    if (atts.length > 1 && atts.map(a => a.id).join() !== c["expected-ids"].join()) seen.add("listed in another order than that of the ids");
    if (c.objects.some(o => /\/attestation\//.test(o.id) && P.inferType(o) !== "attestation")) seen.add("an id that says attestation on another type");
    if (atts.length === c.objects.length) seen.add("nothing but an Attestation");
  }
  /* what the deliberate defects need a vector for */
  for (const x of ["0 listed", "1 listed", "2 listed", "lifecycle active", "lifecycle draft", "lifecycle withdrawn", "signed", "unsigned",
    "listed in another order than that of the ids", "an id that says attestation on another type", "nothing but an Attestation"]) assert.ok(seen.has(x), `a vector holds a case of '${x}'`);
  /* No vector holds an id beyond the Basic Multilingual Plane. The order is that of the UTF-16 code units, as for every
     list of ids (D2): U+1F600 is written D83D DE00 and comes before U+E000, which it follows by code point. */
  const att = LISTED.flatMap(c => c.objects).find(o => P.inferType(o) === "attestation"), home = "https://agency-x.example/attestation/";
  assert.deepEqual(P.listedAttestationErrors(["", "\u{1F600}"].map(tail => ({ ...att, id: home + tail }))), ["\u{1F600}", ""].map(tail => home + tail + MANIFEST_1));
});

/* listed_attestation_errors of the reference, run by Python on objects typed by the page. -> per case [message] */
function referenceListed(cases) {
  const py = `
import ast, json, sys
src = open(sys.argv[1], encoding="utf-8").read()
ns = {}
for node in ast.parse(src).body:
    if isinstance(node, ast.FunctionDef) and node.name in ("by_code_unit", "listed_attestation_errors"):
        exec(compile(ast.Module([node], []), sys.argv[1], "exec"), ns)
cases = json.loads(sys.stdin.buffer.read().decode("utf-8"))
print(json.dumps([ns["listed_attestation_errors"]({i: (t, o) for i, t, o in c}) for c in cases]))`;
  const run = spawnSync("python3", ["-c", py, VALIDATE], { input: JSON.stringify(cases), encoding: "utf8" });
  assert.equal(run.status, 0, run.stderr.slice(-1500));
  return JSON.parse(run.stdout);
}

test("MANIFEST-1: the reference's own listed_attestation_errors gives the page's messages, for every vector and for ids whose order by code unit is not their order by code point",
  { skip: !PYTHON && "python3 is not installed" }, () => {
    const att = LISTED.flatMap(c => c.objects).find(o => P.inferType(o) === "attestation"), named = tail => ({ ...att, id: "https://agency-x.example/attestation/" + tail });
    /* U+1F600 is written with the code units D83D DE00, which come before U+E000; by code point it comes after */
    const cases = [...LISTED, { name: "beyond the Basic Multilingual Plane", objects: [named(""), named("\u{1F600}"), named("z"), named("Z")] }];
    const ref = referenceListed(cases.map(c => typed(c.objects)));
    cases.forEach((c, i) => assert.deepEqual(P.listedAttestationErrors(c.objects), ref[i], c.name));
    assert.deepEqual(ref.at(-1).map(e => e.slice("https://agency-x.example/attestation/".length, e.indexOf(": an Attestation"))), ["Z", "z", "\u{1F600}", ""]);
  });

test("MANIFEST-1 on the page: a manifest that lists an Attestation fails in the reference's words wherever the Attestation is shown; the Attestation is still held to what it binds; what the page says can be done holds in the reference",
  OPTS, () => withReader(async R => {
    const { page } = R;
    let n = 0;
    /* A copy of `src` whose manifest lists the Attestation files `names`: each is moved under objects/attestation/ and
       entered with both digests right, as the IFA bundle had its own until 2026-11-13. `change` edits each first. */
    const listing = async (src, names, change = () => {}) => {
      const dir = path.join(R.tmp, "listed-" + ++n, "bundle"), mp = path.join(dir, "content-manifest.json");
      fs.cpSync(src, dir, { recursive: true });
      const original = fs.readFileSync(mp), manifest = JSON.parse(original);
      fs.mkdirSync(path.join(dir, "objects/attestation"), { recursive: true });
      for (const name of names) {
        const att = JSON.parse(fs.readFileSync(path.join(dir, name), "utf8"));
        change(att);
        const bytes = Buffer.from(JSON.stringify(att, null, 1) + "\n"), rel = "objects/attestation/" + name;
        fs.rmSync(path.join(dir, name));
        fs.writeFileSync(path.join(dir, rel), bytes);
        manifest.objects.push({ id: att.id, version: att.version, path: rel, "package-digest": sha256(bytes), "semantic-digest": await P.semanticDigest(att) });
      }
      fs.writeFileSync(mp, JSON.stringify(manifest, null, 1) + "\n");
      return { dir, mp, original, manifest, names };
    };
    /* What the page says can be done about a listing, done: the entries taken out of the manifest and the files put
       beside it. The manifest is written anew (other bytes than the bundle came with), or its own bytes are put back. */
    const besideAgain = (x, ownBytes) => {
      for (const name of x.names) fs.renameSync(path.join(x.dir, "objects/attestation", name), path.join(x.dir, name));
      fs.rmdirSync(path.join(x.dir, "objects/attestation"));
      const anew = Buffer.from(JSON.stringify({ ...x.manifest, objects: x.manifest.objects.filter(e => !e.path.startsWith("objects/attestation/")) }, null, 2) + "\n");
      assert.equal(anew.equals(x.original), false, "written anew, the manifest has other bytes than it came with");
      fs.writeFileSync(x.mp, ownBytes ? x.original : anew);
    };
    const held = async (x, what, also) => { await R.load(x.dir); const shown = await R.attested(); asTheReference(shown, x.dir, what, also); return shown; };
    const A = "attestation-ifa-ato.json", AID = "https://ifa.gov/goodread/attestation/ifa-ato", ZERO = "sha256:" + "0".repeat(64);
    const MOVE = "What can be done: take its entry out of the manifest and put the file beside the manifest.";
    const THEN = " The manifest is then another file: where its bytes are exactly those the Attestation binds, the Attestation is a Full Match; otherwise it is a Semantic Match, which fails nothing, until the signer issues it again.";
    const ISSUE_AGAIN = "the signer issues the Attestation again (a new version, signed again), or it is taken out of the bundle. This one names no envelope, so setting its lifecycle to withdrawn is a way out as well: it is then reported and fails nothing.";
    const said = shown => shown.map(a => [a.id.split("/").pop(), a.verdict, a.manifest, a.fails, a.listed]);

    /* 1. the IFA bundle, its Attestation listed and nothing else wrong: the listing fails the bundle, the binding does not */
    let x = await listing(IFA, [A]);
    let shown = await held(x, "the IFA bundle, its Attestation listed");
    assert.deepEqual(said(shown), [["ifa-ato", "semantic-match", "other", "false", "true"]]);
    assert.equal(shown[0].listedError, AID + MANIFEST_1);
    assert.equal(shown[0].todo, MOVE + THEN);
    const card = page.locator("#view-stagefn [data-attestation]");
    assert.deepEqual(await card.locator("[data-binds-listed]").evaluateAll(l => l.map(e => [e.className, e.textContent])), [["verdict-bad", "· ✗ and the manifest lists it: the bundle fails (MANIFEST-1)"]]);
    assert.match(await R.text(card), /SEMANTIC MATCH · ✗ and the manifest lists it: the bundle fails \(MANIFEST-1\) — every subject matches and the Attestation binds another manifest: .* The manifest that lists it is never the one it binds; the failure here is the listing /);
    assert.match(await R.text(card), /where it lies listed by the manifest, as objects\/attestation\/attestation-ifa-ato\.json — D3\.1 excludes that: an Attestation lies beside a manifest and is never an entry of one \(MANIFEST-1\)\. It is held to what it binds all the same/);
    assert.equal(await card.locator("[data-where-listed]").getAttribute("class"), "verdict-bad");
    /* the console says it as an error, in the reference's words */
    assert.deepEqual(await page.locator("#log > div.l-err").evaluateAll(l => l.map(e => e.textContent.replace(/^[\d:.]+/, ""))), [AID + MANIFEST_1]);
    /* the overview: the Attestation is one of the objects the manifest lists, as a validator counts it, and that is the failure */
    await R.view("overview");
    const entries = x.manifest.objects.length;
    assert.equal(await R.text(page.locator("#ov-kv .v", { has: page.locator("#ov-listed") })), `${entries} of ${entries} manifest entries ✗ ${AID}${MANIFEST_1}`);
    assert.deepEqual(await page.locator("#ov-kv [data-listed-error]").evaluateAll(l => l.map(e => [e.className, e.textContent])), [["verdict-bad", "✗ " + AID + MANIFEST_1]]);
    assert.equal(await R.text(page.locator("#ov-beside")), "0");
    assert.equal(await R.text(page.locator("[data-ov-binds]")), `SEMANTIC MATCH (another manifest) · ${AID} ✗ listed by the manifest (MANIFEST-1)`);
    assert.equal(await page.locator("[data-ov-listed]").getAttribute("class"), "verdict-bad");
    assert.ok((await page.locator("#pill-bundle").getAttribute("title")).startsWith(`${entries} objects · no attestation beside the manifest · ✗ 1 attestation listed (MANIFEST-1) · `), await page.locator("#pill-bundle").getAttribute("title"));
    /* the object browser: in the list and in the detail */
    await R.view("browser");
    assert.deepEqual(await page.locator(`.objrow[data-id="${AID}"] [data-list-listed]`).evaluateAll(l => l.map(e => [e.className, e.textContent])), [["verdict-bad", "· ✗ listed by the manifest (MANIFEST-1)"]]);
    assert.equal(await R.text(page.locator(`.objrow[data-id="${AID}"] [data-list-binds]`)), "SEMANTIC MATCH · ✗ listed by the manifest (MANIFEST-1)");
    const d = await R.detail(AID);
    assert.equal(await d.locator("[data-listed-error]").evaluate(e => e.textContent), AID + MANIFEST_1);
    assert.equal(await d.locator("[data-attestation]").getAttribute("data-listed"), "true");
    if (REFERENCE) assert.match(referenceAttested(x.dir).line, / pass, 1 fail /, "the listing is the one failure of the bundle");

    /* ... and what the page says can be done, done. Written anew, the manifest is another file: a Semantic Match, and the bundle passes */
    besideAgain(x);
    shown = await held(x, "the Attestation beside the manifest again, the manifest written anew");
    assert.deepEqual([said(shown), shown[0].todo], [[["ifa-ato", "semantic-match", "other", "false", "false"]], null]);
    await R.view("overview");
    assert.deepEqual([await page.locator("[data-listed-error]").count(), await page.locator("[data-ov-listed]").count(), await R.text(page.locator("#ov-beside"))], [0, 0, "1"], "nothing of the listing stays on the page");
    assert.doesNotMatch(await page.locator("#pill-bundle").getAttribute("title"), /listed|MANIFEST-1/);
    assert.match(await R.text(page.locator("#detail")), /^Select an object on the left /, "the detail that was up belonged to the bundle before, and went with it");
    /* with the bytes it binds, the manifest is that manifest again: a Full Match */
    fs.writeFileSync(x.mp, x.original);
    shown = await held(x, "the Attestation beside the manifest again, the manifest's own bytes");
    assert.deepEqual(said(shown), [["ifa-ato", "full-match", "this", "false", "false"]]);

    /* 2. listed, and it does not bind either: two failures, and moving the file cures one of them */
    x = await listing(IFA, [A], a => { a["subject-semantic-digests"][0]["semantic-digest"] = ZERO; });
    shown = await held(x, "listed, and a subject's digest changed");
    assert.deepEqual([said(shown), shown[0].subjects[0].status], [[["ifa-ato", "fail", "other", "true", "true"]], "differs"]);
    assert.equal(shown[0].todo, "What can be done: about the listing, take its entry out of the manifest and put the file beside the manifest. That does not make it bind: " + ISSUE_AGAIN + " The listing fails the bundle whatever the lifecycle is.");
    if (REFERENCE) assert.match(referenceAttested(x.dir).line, / pass, 2 fail /);
    besideAgain(x);
    shown = await held(x, "... beside the manifest again: it still does not bind");
    assert.deepEqual([said(shown), shown[0].todo], [[["ifa-ato", "fail", "other", "true", "false"]], "What can be done: " + ISSUE_AGAIN]);

    /* 3. the lifecycle changes nothing about where an Attestation lies: withdrawn and not binding, the listing is the one failure */
    x = await listing(IFA, [A], a => { a["subject-semantic-digests"][0]["semantic-digest"] = ZERO; a.lifecycle = "withdrawn"; });
    shown = await held(x, "listed, withdrawn, and a subject's digest changed");
    assert.deepEqual(said(shown), [["ifa-ato", "fail", "other", "false", "true"]]);
    assert.equal(shown[0].todo, MOVE + " That it does not bind is then reported and fails nothing: its lifecycle is withdrawn.");
    besideAgain(x);
    shown = await held(x, "... beside the manifest again: reported, and the bundle passes");
    assert.deepEqual([said(shown), shown[0].todo], [[["ifa-ato", "fail", "other", "false", "false"]], null]);
    x = await listing(IFA, [A], a => { a.lifecycle = "draft"; });
    assert.deepEqual(said(await held(x, "listed, a draft")), [["ifa-ato", "semantic-match", "other", "false", "true"]]);

    /* 4. In a pack the reference states two rules: MANIFEST-1, and ADVICE-1 (a pack holds Components only). The page
       states MANIFEST-1. It holds no pack to ADVICE-1 to ADVICE-3 and says nothing of them, here as before. */
    const PA = "attestation-dbvendor-server-7-advice.json";
    x = await listing(PACK, [PA]);
    shown = await held(x, "the worked pack, its Attestation listed", [/ is a attestation - an advice pack holds components only \(an attestation travels beside the manifest, D3\.1\) \(ADVICE-1: /]);
    assert.deepEqual([said(shown), shown[0].envelope], [[["server-7-hardening-3", "semantic-match", "other", "false", "true"]], "unverified"]);
    assert.doesNotMatch(await R.log(), /ADVICE-1/);
    if (REFERENCE) assert.match(referenceAttested(x.dir).line, / pass, 2 fail /);

    /* 5. The example folder with both of its Attestations listed: one sentence each, in the order of the ids. The one
       that binds a pack manifest the bundle keeps is a Full Match all the same - the manifest it binds is not the one
       that lists it - and stays one when it is moved. */
    x = await listing(EXAMPLES, [PA, "attestation-acme-2026.json"]);
    shown = await held(x, "the example folder, both Attestations listed");
    assert.deepEqual(said(shown), [["acme-2026", "semantic-match", "other", "false", "true"], ["server-7-hardening-3", "full-match", "kept-pack", "false", "true"]]);
    assert.deepEqual(shown.map(a => a.todo), [MOVE + THEN, MOVE + " It binds a pack manifest this bundle keeps, which that does not change: it stays a Full Match."]);
    await R.view("overview");
    assert.deepEqual(await page.locator("#ov-kv [data-listed-error]").evaluateAll(l => l.map(e => e.textContent)), shown.map(a => "✗ " + a.id + MANIFEST_1));
    assert.match(await page.locator("#pill-bundle").getAttribute("title"), /^26 objects · no attestation beside the manifest · ✗ 2 attestations listed \(MANIFEST-1\) · /);
    besideAgain(x);
    assert.deepEqual(said(await held(x, "... both beside the manifest again, the manifest written anew")),
      [["acme-2026", "semantic-match", "other", "false", "false"], ["server-7-hardening-3", "full-match", "kept-pack", "false", "false"]]);

    /* 6. Where the page and the reference differ, measured and not hidden (as for a file beside the manifest, above):
       the page reads an object by its fields, the reference by the kernel schema. A listed file with the fields of
       an Attestation and no subject is no Attestation to the kernel. Both fail the bundle, in other words: the page
       with MANIFEST-1 and what the primitive makes of it, the reference with the file matching no type. */
    x = await listing(IFA, [A], a => { a["subject-semantic-digests"] = []; });
    await R.load(x.dir);
    shown = await R.attested();
    assert.deepEqual([said(shown), shown[0].listedError, shown[0].subjects.length], [[["ifa-ato", "fail", "other", "true", "true"]], AID + MANIFEST_1, 0]);
    if (REFERENCE) {
      const ref = referenceAttested(x.dir);
      assert.deepEqual([ref.ok, ref.listed, ref.binds], [false, [], []]);
      assert.deepEqual(ref.others.map(e => e.replace(/ \(closest .*$/, "")), ["objects/attestation/attestation-ifa-ato.json: matches NO type"]);
    }
  }));

/* ---------- 13. an Assessment's method is a facet payload (backlog #55; specification D10 as amended) ---------- */
const METHODS = json("jascon/conformance/facet-vectors.json")["method-vectors"];
const CRITERIA = "https://ns.jascon.net/stdlib/facet/assessment-criteria@1";
const MANUAL = { [CRITERIA]: { method: "manual" } };
/* what the Assess workbench wrote until 1.14.0 */
const EARLIER = { kind: "manual-check", note: "authored in JASCON Bundle Reader workbench" };
const unregistered = (path, key) => `${path}: method '${key}' is no registered facet - not stdlib, not pinned in the manifest, not private: (an Assessment's method is a facet payload and fails closed, D10)`;
const UNCHECKED = "; this page carries no schema validator and does not check it.";
const SAID = { stdlib: "a facet of the standard library. A validator holds this payload to the facet's descriptor" + UNCHECKED,
  pinned: file => `a facet this bundle pins (${file}). A validator holds this payload to that schema` + UNCHECKED,
  private: "private: kept, and ignored by every validator by definition. Nothing checks this payload." };
/* The vectors this page cannot decide. In each, every key of the method names a registered facet, and the payload is
   one that facet's schema refuses: the page carries no schema and no schema validator, so it has nothing to say. */
const UNDECIDED = ["method-stdlib-payload-violates-its-schema", "method-stdlib-payload-with-a-member-the-facet-does-not-know", "method-pinned-payload-violates-the-pin"];

test("an Assessment's method: of the 13 method vectors the page decides the ten that turn on where a key is registered, in the reference's words; three turn on a payload and its schema, which this page does not hold",
  () => {
    assert.equal(METHODS.length, 13);   // a vector added to the family is looked at here before this number moves (12 until the app's port added the object called `method` inside a payload)
    /* the standard library the page knows is the folder of its descriptors */
    const stdlib = fs.readdirSync(path.join(ROOT, "jascon/schemas/stdlib")).filter(n => n.endsWith(".json")).map(n => json("jascon/schemas/stdlib/" + n).id);
    assert.equal(stdlib.length, 8);
    assert.deepEqual([...P.STDLIB_FACETS].sort(), [...stdlib].sort());
    assert.deepEqual(P.manualMethod(), MANUAL);
    assert.ok(stdlib.includes(CRITERIA.replace(/@1$/, "")) && json("jascon/schemas/stdlib/assessment-criteria-1.0.0.json").schema.properties.method.enum.includes("manual"), "what the workbench writes is a value the descriptor knows");
    const homes = new Set(), decided = [];
    for (const c of METHODS) {
      const pinned = new Set(Object.keys(c.pinned || {})), keyOf = frag => /^method '(.*)'$/.exec(frag)[1];
      const errs = P.methodKeyErrors(c.object, pinned, c.name);
      const ofMethod = c["expected-frags"].filter(f => f.startsWith("method '")), ofFacets = c["expected-frags"].filter(f => f.startsWith("facet '"));
      assert.equal(ofMethod.length + ofFacets.length, c["expected-frags"].length, `${c.name}: every fragment names a method or a facet`);
      for (const key of Object.keys(c.object.method || {})) homes.add(String(P.facetHome(key, pinned)));
      if (UNDECIDED.includes(c.name)) {
        assert.deepEqual(errs, [], `${c.name}: every key is registered, and the page has nothing to say`);
        assert.deepEqual([c.expected, c["expected-errors"], ofMethod.length], ["invalid", 1, 1], c.name);
        assert.ok(["stdlib", "pinned"].includes(P.facetHome(keyOf(ofMethod[0]), pinned)), `${c.name}: the error is about the payload of a registered facet`);
        continue;
      }
      /* one message per key no facet registers, each the reference's sentence. What a vector expects of `facets`
         (one does) is another rule, to which this page holds no object. */
      assert.deepEqual(errs, ofMethod.map(f => unregistered(c.name, keyOf(f))), c.name);
      assert.equal(errs.length, c["expected-errors"] - ofFacets.length, c.name);
      if (!ofFacets.length) assert.equal(errs.length ? "invalid" : "valid", c.expected, c.name);
      decided.push(c.name);
    }
    assert.equal(decided.length, 10);
    assert.deepEqual([...homes].sort(), ["null", "pinned", "private", "stdlib"], "the vectors hold a key of every kind");
    /* where a key is registered, case by case */
    const pins = new Set(["https://assessor.example/facet/review"]);
    for (const [key, home] of [[CRITERIA, "stdlib"], ["https://ns.jascon.net/stdlib/facet/assessment-criteria", "stdlib"], ["https://ns.jascon.net/stdlib/facet/assessment-criteria@9", "stdlib"],
      ["https://ns.jascon.net/stdlib/facet/collector@1", "stdlib"], ["https://ns.jascon.net/stdlib/facet/no-such-facet@1", null], ["https://ns.jascon.net/stdlib/facet/", null],
      ["https://assessor.example/facet/review@1", "pinned"], ["https://assessor.example/facet/review", "pinned"], ["https://assessor.example/facet/review@1@2", null],
      ["https://assessor.example/facet/other@1", null], ["private:lab-notes@1", "private"], ["private:", "private"], ["Private:lab-notes@1", null], ["kind", null], ["note", null], ["", null], ["@1", null]])
      assert.equal(P.facetHome(key, pins), home, JSON.stringify(key));
    assert.equal(P.facetHome("https://assessor.example/facet/review@1", new Set()), null, "pinned by another bundle is pinned nowhere here");
    /* the form the workbench wrote until 1.14.0 is known as that, and nothing else is */
    assert.equal(P.isEarlierWorkbenchMethod(EARLIER), true);
    for (const other of [MANUAL, {}, { kind: "manual-check" }, { ...EARLIER, note: "another note" }, { ...EARLIER, more: 1 }, { kind: "review", note: EARLIER.note }, null, "manual-check"])
      assert.equal(P.isEarlierWorkbenchMethod(other), false, JSON.stringify(other));
    assert.deepEqual(P.methodKeyErrors({ id: "https://a.example/asmt/1", method: EARLIER }, new Set()), ["kind", "note"].map(k => unregistered("https://a.example/asmt/1", k)), "one message per key, in the order of the keys, under the object's id");
    for (const none of [{ id: "x" }, { id: "x", method: "manual" }, { id: "x", method: [EARLIER] }, { id: "x", method: null }, null]) assert.deepEqual(P.methodKeyErrors(none, new Set()), []);
  });

/* facet_errors of the reference, run by Python on the same objects. Its source is taken out of validate_core.py by
   name; the validators it asks for are built here from the descriptors of the standard library and from the schemas
   a case pins, as the reference builds them. -> per case [message] */
function referenceFacetErrors(cases) {
  const py = `
import ast, json, os, sys
import jsonschema
src = open(sys.argv[1], encoding="utf-8").read()
make = jsonschema.validators.Draft202012Validator
stdlib = {}
for fn in sorted(os.listdir(sys.argv[2])):
    if fn.endswith(".json"):
        d = json.load(open(os.path.join(sys.argv[2], fn), encoding="utf-8"))
        stdlib[d["id"]] = make(d["schema"])
ns = {"STDLIB": stdlib}
for node in ast.parse(src).body:
    if isinstance(node, ast.FunctionDef) and node.name == "facet_errors":
        exec(compile(ast.Module([node], []), sys.argv[1], "exec"), ns)
cases = json.loads(sys.stdin.buffer.read().decode("utf-8"))
print(json.dumps([ns["facet_errors"](c["object"], {k: make(s) for k, s in (c.get("pinned") or {}).items()}, c["name"]) for c in cases]))`;
  const run = spawnSync("python3", ["-c", py, VALIDATE, path.join(ROOT, "jascon/schemas/stdlib")], { input: JSON.stringify(cases), encoding: "utf8" });
  assert.equal(run.status, 0, run.stderr.slice(-1500));
  return JSON.parse(run.stdout);
}

test("an Assessment's method: the reference's own facet_errors names the keys the page names, in the same words; what it says beyond that is about a payload and its schema, or about `facets`",
  { skip: !REFERENCE && "python3 with jsonschema is not installed" }, () => {
    const a = METHODS[0].object, withMethod = (name, method, pinned) => ({ name, object: { ...a, method }, pinned });
    const cases = [...METHODS,
      withMethod("the form the workbench wrote until 1.14.0", EARLIER),
      withMethod("what the workbench writes now", MANUAL),
      withMethod("the version after the @ is not part of the id", { "https://ns.jascon.net/stdlib/facet/assessment-criteria@9": { method: "automated" } }),
      withMethod("no version at all", { "https://ns.jascon.net/stdlib/facet/assessment-criteria": { method: "automated" } }),
      withMethod("private: is asked before the standard library and is case-sensitive", { "private:x": 1, "Private:x": 1 }),
      withMethod("a second @ belongs to the id", { "https://assessor.example/facet/review@1@2": {} }, { "https://assessor.example/facet/review": { type: "object" } }),
      withMethod("a facet of the standard library that does not exist", { "https://ns.jascon.net/stdlib/facet/no-such-facet@1": {} })];
    const ref = referenceFacetErrors(cases), undecided = [], ofFacets = [];
    cases.forEach((c, i) => {
      const keys = ref[i].filter(e => / method '.*' is no registered facet /.test(e)), payloads = ref[i].filter(e => / method '.*' payload violates its schema: /.test(e));
      const facets = ref[i].filter(e => !keys.includes(e) && !payloads.includes(e));
      assert.deepEqual(P.methodKeyErrors(c.object, new Set(Object.keys(c.pinned || {})), c.name), keys, c.name);
      if (payloads.length) undecided.push(c.name);
      if (facets.length) { ofFacets.push(c.name); for (const e of facets) assert.match(e, /: unregistered facet '/, c.name); }
    });
    assert.deepEqual(undecided, UNDECIDED, "the vectors the page cannot decide are those in which the reference refuses a payload");
    assert.deepEqual(ofFacets, ["method-and-facets-are-both-held"]);
    assert.deepEqual(ref[METHODS.length], ["kind", "note"].map(k => unregistered("the form the workbench wrote until 1.14.0", k)));
    assert.deepEqual(ref.slice(METHODS.length + 1, METHODS.length + 4), [[], [], []], "what the workbench writes passes, and so does the same facet under another version or none");
  });

/* What the reference says about the methods of one bundle folder: -> { ok, line, unregistered: [message], violated: [message], others: [message] } */
function referenceMethods(dir) {
  const ref = reference(dir, "--as-of", "2026-11-14");
  const failures = ref.out.split("\n").map(l => /^  - \[[^\]]*\] (.*)$/.exec(l)).filter(Boolean).map(m => m[1]);
  const unregisteredKeys = failures.filter(e => / method '.*' is no registered facet /.test(e)), violated = failures.filter(e => / method '.*' payload violates its schema: /.test(e));
  return { ok: ref.ok, line: ref.line, unregistered: unregisteredKeys, violated, others: failures.filter(e => !unregisteredKeys.includes(e) && !violated.includes(e)) };
}

test("the method on the page: the Assess workbench states a manual assessment under the standard facet and its export passes the reference; every key of a method is shown with where its facet is registered, a key no facet registers in the reference's words, and the payload as not checked here",
  OPTS, () => withReader(async R => {
    const { page } = R;
    const set = async (sel, value) => { await page.fill(sel, value); await page.locator(sel).dispatchEvent("change"); };
    const NS = "https://example.org/my", day = await page.evaluate(() => new Date().toISOString().slice(0, 10)), WB = `${NS}/asmt/check-${day}`;
    /* what the detail that is up says about a method: per key [key, where it is registered, the error, the word about checking] */
    const methodSaid = d => d.locator(".facetbox[data-method-key]").evaluateAll(l => l.map(x => [x.dataset.methodKey, x.dataset.methodHome,
      x.querySelector("[data-method-error]")?.textContent ?? null, x.querySelector("[data-method-unchecked]")?.textContent ?? null]));
    const cardLine = id => R.text(page.locator("#view-stagefn .stmt", { has: page.locator(`[data-ref="${id}"]`) }).locator("[data-method-line]"));
    const errorsShown = async () => { await R.view("overview"); return page.locator("#ov-kv [data-method-error]").evaluateAll(l => l.map(e => e.textContent)); };
    const consoleErrors = () => page.locator("#log > div.l-err").evaluateAll(l => l.map(e => e.textContent.replace(/^[\d:.]+/, "")));
    /* an object of a bundle written anew, and the manifest's two digests of it with it: nothing else is wrong with the bundle */
    const rewritten = async (dir, id, change) => {
      const mp = path.join(dir, "content-manifest.json"), manifest = JSON.parse(fs.readFileSync(mp, "utf8")), entry = manifest.objects.find(e => e.id === id);
      const obj = JSON.parse(fs.readFileSync(path.join(dir, entry.path), "utf8"));
      change(obj);
      const bytes = Buffer.from(JSON.stringify(obj, null, 1) + "\n");
      fs.writeFileSync(path.join(dir, entry.path), bytes);
      Object.assign(entry, { "package-digest": sha256(bytes), "semantic-digest": await P.semanticDigest(obj) });
      fs.writeFileSync(mp, JSON.stringify(manifest, null, 1) + "\n");
      return obj;
    };
    const held = async (dir, what, also = []) => {   // the page's errors are the reference's, and it fails the bundle for nothing else but what a test names
      const shown = await errorsShown();
      if (REFERENCE) {
        const ref = referenceMethods(dir);
        assert.deepEqual(shown, ref.unregistered.map(e => "✗ " + e), `${what}: the keys no facet registers, in the reference's words and order`);
        assert.deepEqual([ref.violated, ref.others.filter(e => !also.some(re => re.test(e)))], [[], []], `${what}: nothing else fails in the reference — ${ref.line}`);
        for (const re of also) assert.ok(ref.others.some(e => re.test(e)), `${what}: the reference states ${re}`);
        assert.equal(ref.ok, !shown.length && !also.length, `${what}: ${ref.line}`);
      }
      return shown;
    };

    /* 1. The Assess workbench, on a requirement written in the workbench (so that the export holds what its Finding
       names). A person answers the form, which is a manual assessment. The object that is downloaded and the one that
       goes into the graph state it under the standard facet, and carry no note that names this tool: the manifest of
       the export names it. */
    await R.view("stage:author");
    await page.fill("#wb-au-title", "Encrypt backups");
    await page.fill("#wb-au-prose", "Backups are encrypted.");
    await page.fill("#wb-au-party", "Operations Team");
    await page.click("#wb-au-addreq");
    await R.view("stage:assess");
    await set("#wb-a-perf", "Lead Assessor");
    await page.locator('[data-az$="|not-satisfied"]').first().click();
    const downloaded = JSON.parse(fs.readFileSync(await R.download("#wb-a-dl"), "utf8"));
    assert.deepEqual([downloaded.id, downloaded.method], [WB, MANUAL], "the Assessment that is downloaded");
    await page.waitForTimeout(600);   // the Finding that is downloaded after it
    await page.click("#wb-a-gen");
    assert.equal(await cardLine(WB), "method: manual · assessment-criteria@1 (standard library)");
    let d = await R.detail(WB);
    assert.deepEqual(await methodSaid(d), [[CRITERIA, "stdlib", null, SAID.stdlib]]);
    const workbench = unzipTo(await R.download("#btn-export-ws"), path.join(R.tmp, "workbench"));
    const wm = JSON.parse(fs.readFileSync(path.join(workbench, "content-manifest.json"), "utf8")), entry = wm.objects.find(e => e.id === WB);
    const written = JSON.parse(fs.readFileSync(path.join(workbench, entry.path), "utf8"));
    assert.deepEqual(written.method, MANUAL, "the Assessment that is exported");
    assert.deepEqual(Object.keys(written).sort(), ["id", "lifecycle", "method", "performer-ref", "result", "subject-refs", "time", "title", "version"], "and nothing on it names the tool");
    assert.equal(wm.provenance.converter, "jascon-reader.html " + (await page.locator("#pill-version").innerText()).split(" · ")[0], "the manifest does");
    assert.doesNotMatch(await R.log(), /in this export — .* method '/);
    assert.match(await R.log(), /workspace bundle exported: 3 objects .* — loads back into this reader and nothing fails in what this page checks \(closure-required references, facet and method keys, Attestations\); it runs no kernel schema and checks no facet payload$/m);
    if (REFERENCE) { const ref = referenceMethods(workbench); assert.deepEqual([ref.ok, ref.unregistered, ref.violated, ref.others], [true, [], [], []], ref.line); }

    /* 2. The folders as they lie. The example folder's three Assessments state their method under the standard facet;
       the IFA bundle's under a facet the bundle pins. Nothing fails, and nothing is said to have been checked. */
    await R.load(EXAMPLES);
    assert.deepEqual(await held(EXAMPLES, "jascon/examples"), []);
    await R.view("stage:assess");
    assert.equal(await cardLine("https://assessor.example/assessment/2026-q3-acme"), "method: assessment-criteria@1 (standard library)");
    assert.deepEqual(await page.locator("#view-stagefn [data-method-line]").evaluateAll(l => l.map(e => e.textContent.replace(/\s+/g, " ").trim()).sort()),
      ["method: assessment-criteria@1 (standard library)", "method: automated · assessment-criteria@1 (standard library)", "method: automated · assessment-criteria@1 (standard library)"]);
    d = await R.detail("https://assessor.example/assessment/2026-q3-acme");
    assert.deepEqual(await methodSaid(d), [[CRITERIA, "stdlib", null, SAID.stdlib]]);
    assert.match(await R.text(d), /Method — a facet payload \(D10\): each key names the facet the method is stated under .*Document review of KONF\.14\.1 evidence duties/i, "the payload stands under its key, as recorded");
    assert.equal(await d.locator("[data-method-todo]").count(), 0);

    /* 3. A bundle an earlier version exported: the same export with the method as the workbench wrote it until 1.14.0.
       It is shown as loaded - nothing is rewritten - and fails, on the page as in the reference, once for each key. */
    const earlier = path.join(R.tmp, "earlier", "bundle");
    fs.cpSync(workbench, earlier, { recursive: true });
    await rewritten(earlier, WB, o => { o.method = EARLIER; });
    await R.load(earlier);
    const both = ["kind", "note"].map(k => unregistered(WB, k));
    assert.deepEqual(await held(earlier, "an export of 1.14.0"), both.map(e => "✗ " + e));
    assert.deepEqual(await consoleErrors(), both, "the console says it as errors, in the reference's words");
    await R.view("stage:assess");
    assert.equal(await cardLine(WB), "method: ✗ kind (no facet registers this key) · ✗ note (no facet registers this key) — a validator refuses it (D10)");
    d = await R.detail(WB);
    assert.deepEqual(await methodSaid(d), [["kind", "none", both[0], null], ["note", "none", both[1], null]]);
    assert.equal(await d.locator("[data-method-restate]").count(), 0, "an object of a loaded bundle is not the page's to state anew");
    const TODO = `What can be done: state the method under a facet that is registered — the standard ${CRITERIA} for a manual or an automated assessment, a facet whose schema the bundle pins, or a private: key, which every validator keeps and ignores. The object is then another: the manifest's two digests of it are written anew.`;
    assert.equal(await R.text(d.locator("[data-method-todo]")), TODO);
    assert.deepEqual(JSON.parse(fs.readFileSync(path.join(earlier, entry.path), "utf8")).method, EARLIER, "the file is as it was");
    /* ... and what the page says can be done, done on the copy: the standard facet, and the digests anew */
    await rewritten(earlier, WB, o => { o.method = MANUAL; });
    await R.load(earlier);
    assert.deepEqual(await held(earlier, "... its method stated under the standard facet"), []);

    /* 4. The IFA bundle. Its Assessment states its method under a facet the bundle pins; a key beside it that no facet
       registers fails for that key alone (the reference's own copy c12); under private: the same key is kept and ignored;
       and with the pinned schema's file taken away the pin registers nothing, as the reference has it. */
    const IA = "https://ifa.gov/goodread/assessment/conmon-2023-06", PLAN = "https://ifa.gov/goodread/facet/assessment-plan@1";
    const planFile = json("converted_examples/US.IFA-GoodRead/ifa-core-bundle/content-manifest.json")["facet-schemas"].find(f => f.id === PLAN.replace(/@1$/, "")).path;
    await R.load(IFA);
    assert.deepEqual(await held(IFA, "the IFA bundle"), []);
    d = await R.detail(IA);
    assert.deepEqual(await methodSaid(d), [[PLAN, "pinned", null, SAID.pinned(planFile)]]);
    const ifa = n => { const dir = path.join(R.tmp, "ifa-" + n, "bundle"); fs.cpSync(IFA, dir, { recursive: true }); return dir; };
    let copy = ifa(1);
    await rewritten(copy, IA, o => { o.method.kind = "review"; });
    await R.load(copy);
    assert.deepEqual(await held(copy, "the IFA bundle, a key nobody registered beside the pinned one"), ["✗ " + unregistered(IA, "kind")]);
    await R.view("stage:assess");
    assert.equal(await cardLine(IA), "method: assessment-plan@1 (pinned by this bundle) · ✗ kind (no facet registers this key) — a validator refuses it (D10)");
    d = await R.detail(IA);
    assert.deepEqual(await methodSaid(d), [[PLAN, "pinned", null, SAID.pinned(planFile)], ["kind", "none", unregistered(IA, "kind"), null]]);
    assert.equal(await R.text(d.locator("[data-method-todo]")), TODO);
    await rewritten(copy, IA, o => { o.method["private:kind@1"] = o.method.kind; delete o.method.kind; });
    await R.load(copy);
    assert.deepEqual(await held(copy, "... the key under private:"), []);
    d = await R.detail(IA);
    assert.deepEqual((await methodSaid(d)).map(m => m.slice(0, 2).concat(m[3])), [[PLAN, "pinned", SAID.pinned(planFile)], ["private:kind@1", "private", SAID.private]]);
    copy = ifa(2);
    fs.rmSync(path.join(copy, planFile));
    await R.load(copy);
    assert.deepEqual(await held(copy, "the IFA bundle without the schema file of the method's facet", [/^schemas\/goodread-ap-stub\.json: pinned facet schema listed but missing$/]), ["✗ " + unregistered(IA, PLAN)]);
    d = await R.detail(IA);
    assert.deepEqual(await methodSaid(d), [[PLAN, "none", unregistered(IA, PLAN), null]]);
    assert.equal(await R.text(d.locator("[data-method-pin-missing]")), `The manifest pins this facet, and its schema file ${planFile} was not read: a pin without its file registers nothing.`);

    /* 5. A workspace an earlier version stored. Its Assessment is restored as it was stored and said to fail; an export
       that holds it says so and fails the reference; on a person's word the page states the method anew, and then
       the export passes. */
    const req = BINDS[0].objects[0], OLD = { id: `${NS}/asmt/check-2026-11-10`, version: "1", lifecycle: "draft", title: "Check 2026-11-10 — a set", "subject-refs": [req.id], method: EARLIER,
      "performer-ref": `${NS}/party/lead-assessor`, time: "2026-11-10T09:00:00.000Z", result: "satisfied" };
    const stored = { v: 2, ns: NS, tailor: { label: "my-tailoring", selects: [], excludes: [], operations: [] }, system: { title: "My System", components: [], implementations: [] },
      assess: { scopeKey: "", performer: "", results: {} }, created: [req, OLD] };
    await page.evaluate(w => localStorage.setItem("scr-work", JSON.stringify(w)), stored);
    await page.reload();
    const inStore = () => page.evaluate(id => JSON.parse(localStorage.getItem("scr-work")).created.find(o => o.id === id).method, OLD.id);
    assert.deepEqual(await inStore(), EARLIER, "restored, the stored object is as it was");
    assert.match(await R.log(), new RegExp(`1 Assessment\\(s\\) of the workspace state their method under a key no facet registers, as the Assess workbench wrote it until 1\\.14\\.0: an export that holds one fails a validator \\(D10\\)\\. Each is kept as stored; its detail in the object browser says what can be done — ${OLD.id.replace(/[.]/g, "\\.")}$`, "m"));
    d = await R.detail(OLD.id);
    const old = ["kind", "note"].map(k => unregistered(OLD.id, k));
    assert.deepEqual(await methodSaid(d), [["kind", "none", old[0], null], ["note", "none", old[1], null]]);
    assert.match(await R.text(d.locator("[data-method-todo]")), /^This is how the Assess workbench of this page stated a manual check until 1\.14\.0\. It is kept as it was stored, and an export that holds it fails a validator\. State it under the standard facet: manual writes \{"https:\/\/ns\.jascon\.net\/stdlib\/facet\/assessment-criteria@1":\{"method":"manual"\}\} in its place, in the workspace\.$/);
    let out = unzipTo(await R.download("#btn-export-ws"), path.join(R.tmp, "stored"));
    for (const e of old) assert.ok((await R.log()).includes("in this export — " + e + "\n"), e);
    assert.match(await R.log(), /workspace bundle exported: 2 objects .* — loads back into this reader and validate_core\.py fails it: 2 line\(s\) above say why$/m);
    if (REFERENCE) { const ref = referenceMethods(out); assert.deepEqual([ref.ok, ref.unregistered, ref.violated, ref.others], [false, old, [], []], ref.line); }
    assert.deepEqual(await inStore(), EARLIER, "an export rewrites nothing either");
    await d.locator("[data-method-restate]").click();
    assert.deepEqual(await methodSaid(page.locator("#detail")), [[CRITERIA, "stdlib", null, SAID.stdlib]], "stated anew, on a person's word, and shown at once");
    assert.equal(await page.locator("#detail [data-method-todo]").count(), 0);
    assert.deepEqual(await inStore(), MANUAL, "in the workspace too");
    assert.ok((await R.log()).includes(`${OLD.id}: its method is stated anew in the workspace — ${JSON.stringify(MANUAL)} in place of ${JSON.stringify(EARLIER)}, which no facet registers`));
    await R.view("stage:assess");
    assert.equal(await cardLine(OLD.id), "method: manual · assessment-criteria@1 (standard library)");
    out = unzipTo(await R.download("#btn-export-ws"), path.join(R.tmp, "restated"));
    assert.deepEqual(JSON.parse(fs.readFileSync(path.join(out, "objects/asmt", fs.readdirSync(path.join(out, "objects/asmt"))[0]), "utf8")), { ...OLD, title: { en: OLD.title }, method: MANUAL }, "nothing but the method changed (and the title leaves as a language map, as every export writes it)");
    if (REFERENCE) { const ref = referenceMethods(out); assert.deepEqual([ref.ok, ref.unregistered, ref.violated, ref.others], [true, [], [], []], ref.line); }

    /* 6. Pasted: a private key is kept and said to be checked by nobody; an empty method states none; a method of the
       earlier form on an object that is not the workspace's gets no button. */
    const paste = async obj => { R.answers.push(JSON.stringify(obj)); await page.click("#btn-paste"); return page.locator("#detail"); };
    d = await paste({ ...OLD, id: `${NS}/asmt/private`, method: { "private:lab-notes@1": { whatever: [1, 2, 3] } } });
    assert.deepEqual(await methodSaid(d), [["private:lab-notes@1", "private", null, SAID.private]]);
    d = await paste({ ...OLD, id: `${NS}/asmt/empty`, method: {} });
    assert.deepEqual([await methodSaid(d), await R.text(d.locator("[data-method-empty]"))], [[], "it states no method: the object is empty. The kernel schema accepts that, and the rule about facets has no key to hold."]);
    d = await paste({ ...OLD, id: `${NS}/asmt/pasted`, method: EARLIER });
    assert.deepEqual([(await methodSaid(d)).map(m => m[1]), await d.locator("[data-method-restate]").count(), await R.text(d.locator("[data-method-todo]"))], [["none", "none"], 0, TODO]);
  }));

/* ---------- 14. closure-required references in an export, and the keys of `facets` (v1.16.0) ---------- */
/* closure_errors of the reference, run by Python on the same objects, typed as the page types them. -> [message] */
function referenceClosure(objs) {
  const py = `
import ast, json, sys
src = open(sys.argv[1], encoding="utf-8").read()
ns = {"content_digest": lambda o: None}
for node in ast.parse(src).body:
    if isinstance(node, ast.FunctionDef) and node.name == "closure_errors":
        exec(compile(ast.Module([node], []), sys.argv[1], "exec"), ns)
objs = json.loads(sys.stdin.buffer.read().decode("utf-8"))
print(json.dumps(ns["closure_errors"]({o["id"]: (t, o) for t, o in objs})))`;
  const run = spawnSync("python3", ["-c", py, VALIDATE], { input: JSON.stringify(objs.map(o => [P.inferType(o), o])), encoding: "utf8" });
  assert.equal(run.status, 0, run.stderr.slice(-1500));
  return JSON.parse(run.stdout);
}
/* the failures the reference lists for one bundle folder */
const referenceFailures = dir => { const ref = reference(dir, "--as-of", "2026-11-14"); return { ok: ref.ok, line: ref.line, failures: ref.out.split("\n").map(l => /^  - \[[^\]]*\] (.*)$/.exec(l)).filter(Boolean).map(m => m[1]) }; };
/* the lines an export wrote as failing it, after "in this export — " */
const exportFails = log => [...log.matchAll(/in this export — (.*)$/gm)].map(m => m[1]);

test("closure-required references: every reference need() asks for in closure_errors, resolved or not, gets the reference's sentence from the page's own function, and nothing of the typed checks",
  { skip: !PYTHON && "python3 is not installed" }, () => {
    const E = "https://ex.org", R1 = { id: `${E}/req/1`, version: "1", lifecycle: "active", statements: [{ id: "s1" }] };
    const S = { id: `${E}/set/1`, version: "1", lifecycle: "active", members: [{ ref: R1.id }, { ref: `${E}/req/gone-member` }] };
    const T = { id: `${E}/tailoring/1`, version: "1", selects: [{ "set-ref": S.id }, { "set-ref": `${E}/set/gone` }, { all: true }], excludes: [{ ref: R1.id }, { ref: `${E}/req/gone-exclude` }],
      operations: [{ "requirement-ref": `${E}/req/gone-op`, "statement-id": "s1" }, { "requirement-ref": R1.id }] };
    const I = { id: `${E}/impl/1`, "component-ref": `${E}/comp/gone`, "requirement-ref": `${E}/req/gone-impl`, responsibility: "provider" };
    const F = { id: `${E}/finding/1`, "assessment-ref": `${E}/asmt/gone`, "requirement-ref": R1.id, state: "open", "risk-refs": [`${E}/risk/elsewhere`] };
    const K = { id: `${E}/risk/1`, scenario: "x", "owner-ref": `${E}/party/o`, treatments: [{ "requirement-ref": `${E}/req/gone-treat` }, { "requirement-ref": R1.id }],
      "component-refs": [`${E}/comp/gone-risk`], "tailoring-refs": [T.id, `${E}/tailoring/gone`] };
    const objs = [R1, S, T, I, F, K], ref = referenceClosure(objs), page = P.closureNeedErrors(objs);
    assert.deepEqual(page, ref.filter(e => / closure-required .* does not resolve in-bundle: /.test(e)));
    assert.deepEqual(page.map(e => / closure-required (.*) does not resolve/.exec(e)[1]), ["member ref", "selects set-ref", "excludes ref", "operation requirement-ref",
      "component-ref", "requirement-ref", "assessment-ref", "treatments requirement-ref (RISK-7)", "component-refs (RISK-7)", "tailoring-refs (RISK-7)"], "one of every kind");
    assert.deepEqual(P.closureNeedErrors([R1, { ...S, members: [{ ref: R1.id }] }, { ...F, "assessment-ref": R1.id }]), [], "what resolves is not said; a Finding's risk-refs are a landmark, not closure-required");
  });

test("an export whose Finding names a requirement of the loaded bundle: the page fails it with the reference's closure-required line, and where it finds nothing it says what it checked",
  OPTS, () => withReader(async R => {
    const { page } = R;
    await R.load(EXAMPLES);
    await R.view("stage:assess");
    await page.fill("#wb-a-perf", "Lead Assessor");
    await page.locator("#wb-a-perf").dispatchEvent("change");
    await page.locator('[data-az$="|not-satisfied"]').first().click();
    await page.click("#wb-a-gen");
    const out = unzipTo(await R.download("#btn-export-ws"), path.join(R.tmp, "closure"));
    const log = await R.log(), fails = exportFails(log), closure = fails.filter(e => / closure-required /.test(e));
    assert.equal(closure.length, 1, log.slice(-1500));
    assert.match(closure[0], /\/finding\/.*: closure-required requirement-ref does not resolve in-bundle: https:\/\//);
    assert.match(log, new RegExp(`validate_core\\.py fails it: ${fails.length} line\\(s\\) above say why$`, "m"));
    assert.doesNotMatch(log, /passes validate_core\.py/);
    if (REFERENCE) {
      const ref = referenceFailures(out);
      assert.equal(ref.ok, false, ref.line);
      assert.deepEqual(ref.failures.filter(e => / closure-required /.test(e)), closure, "the reference's line, word for word");
      assert.deepEqual(ref.failures, fails, "and the reference fails it for nothing else");
    }
  }));

/* What the facet vectors say of the keys of `facets` against what the page decides. */
test("the keys of facets: the page names the keys the reference's facet_errors names as unregistered, in the same words; a payload against its schema stays undecided, as for a method",
  { skip: !REFERENCE && "python3 with jsonschema is not installed" }, () => {
    const v = json("jascon/conformance/facet-vectors.json"), cases = [...v.vectors, ...v["method-vectors"]], ref = referenceFacetErrors(cases);
    const decided = [], undecided = [];
    cases.forEach((c, i) => {
      const keys = ref[i].filter(e => /: unregistered facet '/.test(e)), payloads = ref[i].filter(e => /: facet '.*' payload violates its schema: /.test(e));
      assert.deepEqual(P.facetKeyErrors(c.object, new Set(Object.keys(c.pinned || {})), c.name), keys, c.name);
      if (payloads.length) undecided.push(c.name);
      else if (c.object.facets && !("expected-errors" in c)) { assert.equal(keys.length ? "invalid" : "valid", c.expected, c.name); decided.push(c.name); }
    });
    assert.deepEqual(decided, ["stdlib-payload-valid", "unregistered-facet-fails-closed", "pinned-framework-facet-valid", "private-facet-ignored-by-definition"]);
    assert.deepEqual(undecided, ["stdlib-payload-corrupt-wrong-types", "stdlib-payload-missing-required", "pinned-framework-facet-corrupt"]);
    assert.deepEqual(P.facetKeyErrors({ id: "x", facets: { "private:a": 1, "https://no.example/f@1": 1 } }, new Set()), ["x: unregistered facet 'https://no.example/f@1' — not stdlib, not pinned in the manifest, not private: (dangerous-by-default, D10)"]);
  });

test("the keys of facets on the page: each key says where its facet is registered; a key no facet registers fails in the reference's words in the detail, the overview, the console and an export",
  OPTS, () => withReader(async R => {
    const { page } = R;
    const KONF = "https://ns.bsi.bund.de/gspp/req/KONF.14.1", PINNED = "https://ns.bsi.bund.de/facet/gspp-taxonomy@1", BAD = "https://ns.bsi.bund.de/facet/not-pinned@1";
    const said = d => d.locator(".facetbox[data-facet-key]").evaluateAll(l => l.map(x => [x.dataset.facetKey, x.dataset.facetHome,
      x.querySelector("[data-facet-error]")?.textContent ?? null, x.querySelector("[data-facet-unchecked]") ? "unchecked" : null]));
    const heading = d => d.locator(".sectionlabel").evaluateAll(l => l.map(x => x.textContent).filter(t => /^Facets/.test(t)));
    const err = (id, key) => `${id}: unregistered facet '${key}' — not stdlib, not pinned in the manifest, not private: (dangerous-by-default, D10)`;
    await R.load(EXAMPLES);
    let d = await R.detail(KONF);
    assert.deepEqual(await said(d), [[PINNED, "pinned", null, "unchecked"]]);
    assert.deepEqual(await heading(d), ["Facets — extensions (D10): each key names a facet, and where it is registered is said per key"]);
    /* a copy whose requirement names a facet nobody pins, with both digests anew */
    const copy = path.join(R.tmp, "facets", "examples");
    fs.cpSync(EXAMPLES, copy, { recursive: true });
    const mp = path.join(copy, "content-manifest.json"), manifest = JSON.parse(fs.readFileSync(mp, "utf8")), entry = manifest.objects.find(e => e.id === KONF);
    const obj = JSON.parse(fs.readFileSync(path.join(copy, entry.path), "utf8"));
    obj.facets = { [BAD]: obj.facets[PINNED] };
    const bytes = Buffer.from(JSON.stringify(obj, null, 1) + "\n");
    fs.writeFileSync(path.join(copy, entry.path), bytes);
    Object.assign(entry, { "package-digest": sha256(bytes), "semantic-digest": await P.semanticDigest(obj) });
    fs.writeFileSync(mp, JSON.stringify(manifest, null, 1) + "\n");
    await R.load(copy);
    const e = err(KONF, BAD);
    await R.view("overview");
    assert.deepEqual(await page.locator("#ov-kv [data-facet-error]").evaluateAll(l => l.map(x => x.textContent)), ["✗ " + e]);
    assert.ok((await page.locator("#log > div.l-err").evaluateAll(l => l.map(x => x.textContent))).some(t => t.endsWith(e)), "the console says it as an error");
    d = await R.detail(KONF);
    assert.deepEqual(await said(d), [[BAD, "none", e, null]]);
    assert.doesNotMatch((await heading(d)).join(), /registered extensions/i, "the heading calls no key registered");
    if (REFERENCE) { const ref = referenceFailures(copy); assert.deepEqual([ref.ok, ref.failures], [false, [e]], ref.line); }
    /* an export: a requirement of the workspace under that key */
    const NS = "https://example.org/my", REQ = { id: `${NS}/req/x`, version: "1", lifecycle: "active",
      statements: [{ id: "s1", modality: "must", "obligated-parties": [`${NS}/party/ops`], prose: { en: "X." } }], facets: { [BAD]: obj.facets[BAD] } };
    await page.evaluate(w => localStorage.setItem("scr-work", JSON.stringify(w)), { v: 2, ns: NS, tailor: { label: "t", selects: [], excludes: [], operations: [] },
      system: { title: "S", components: [], implementations: [] }, assess: { scopeKey: "", performer: "", results: {} }, created: [REQ] });
    await page.reload();
    const out = unzipTo(await R.download("#btn-export-ws"), path.join(R.tmp, "facets-export"));
    const log = await R.log();
    assert.deepEqual(exportFails(log), [err(REQ.id, BAD)]);
    assert.match(log, /validate_core\.py fails it: 1 line\(s\) above say why$/m);
    if (REFERENCE) { const ref = referenceFailures(out); assert.deepEqual([ref.ok, ref.failures], [false, [err(REQ.id, BAD)]], ref.line); }
  }));
