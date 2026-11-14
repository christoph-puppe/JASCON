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

   Needs Playwright with Chromium for 4 to 10 and python3 with jsonschema for
   the runs of the reference; where one is missing, that part is skipped and
   says so. Needs no network: the one thing the page asks the web for, its
   font stylesheet, is answered here with an empty one. */
import test from "node:test";
import assert from "node:assert/strict";
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
  return new Function(`"use strict";\n${HTML.slice(a, b)}\nreturn { inferType, kernelNeeded, kernelPinErrors, whoDecided, authorRecord, authorTailoring, partyUri, requiredParty };`)();
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
const ASSESSMENT = { id: `${EX}/assessment/a`, version: "1", lifecycle: "active", "subject-refs": [REQ.id], method: { kind: "interview" }, "performer-ref": `${EX}/party/assessor`,
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
  const errors = [], answers = [];
  /* a script error on any page of the test is held against it; prompt() takes the next answer a test queued */
  const watch = p => {
    p.on("pageerror", e => errors.push("pageerror: " + e.message));
    p.on("console", m => { if (m.type() === "error") errors.push("console: " + m.text()); });
    p.on("dialog", d => d.type() === "prompt" ? d.accept(answers.length ? answers.shift() : "") : d.accept());
    return p;
  };
  watch(page);
  await page.goto(pathToFileURL(READER).href);
  /* a folder, opened as the button does; done when the page has indexed it (or has stopped at it) */
  const load = async dir => {
    const lines = await page.locator("#log > div").count();
    await page.setInputFiles("#folderpick", dir);
    await page.waitForFunction(n => [...document.querySelectorAll("#log > div")].slice(n)
      .some(x => /indexed \d+ objects|nothing of this bundle is shown/.test(x.textContent)), lines);
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
  return { page, tmp, load, view, detail, text, who, log, download, finish, shutdown, watch, answers, sweep };
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
    const server = http.createServer((req, res) => {
      const u = decodeURIComponent(new URL(req.url, "http://localhost").pathname);
      const file = u.startsWith("/repo/") ? path.join(ROOT, u.slice(6)) : u.startsWith("/tmp/") ? path.join(R.tmp, u.slice(5)) : "";
      if (!file || !fs.existsSync(file) || !fs.statSync(file).isFile()) { res.writeHead(404); res.end(); return; }
      res.writeHead(200, { "content-type": file.endsWith(".html") ? "text/html; charset=utf-8" : "application/json" });
      res.end(fs.readFileSync(file));
    });
    await new Promise(done => server.listen(0, "127.0.0.1", done));
    try {
      const at = `http://127.0.0.1:${server.address().port}`, web = R.watch(await page.context().newPage());
      const linked = async bundle => {
        await web.goto("about:blank");
        await web.goto(`${at}/repo/one-page-apps/jascon-reader.html#load=${at}/tmp/${path.relative(R.tmp, bundle).split(path.sep).join("/")}/&view=stage:tailor`);
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
