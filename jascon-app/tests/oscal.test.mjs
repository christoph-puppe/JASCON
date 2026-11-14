/* The OSCAL import against what the repository ships.

   - BSI preset: every object the import makes from the Anwenderkatalog
     Grundschutz++ has the semantic digest the committed bundle's manifest
     states for it, and the pinned facet schemas are the same; every control
     at every depth is a Requirement with its own links, read from the
     source itself; and on a catalogue written for the tests every object is
     what convert_bsi.py writes for it (needs python3).
   - Generic rules on NIST SP 800-53: every object is a valid kernel object
     and every reference closes.
   - NIST preset: the objects of the committed SP 800-53 bundle by semantic
     digest and by bytes, and the rules on a small catalog written for the
     test, which convert_nist.py is run on as well (needs python3).
   - Profile import: the NIST MODERATE profile, imported into the shipped
     SP 800-53 bundle, selects exactly the members of the bundle's own
     MODERATE baseline Set, and its Set carries what that Set carries.

   The tests against shipped bundles need the publishers' source files,
   which the repository does not carry (sources/ is ignored). Without them
   they are skipped; the tests on hand-made input always run; the readme
   says where the files come from. The BSI, NIST and CIS presets are
   compared with their converters on a catalog written for the test (needs
   python3). */
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import crypto from "node:crypto";
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
/* the BSI, NIST and CIS presets are also compared with their converters run on a catalogue written for the tests */
const python = spawnSync("python3", ["--version"]).status === 0;

/* Every control of the catalogue is a Requirement of its own, at every depth (the author, 2026-11-14; convert_bsi.py
   v0.3). The committed bundle decides: every object the preset writes for the pinned source has the semantic
   digest its manifest records. Since build 0.9.14: 1,287 objects, 999 Requirements and 288 Sets. Until then the
   preset wrote 813 (651 Requirements, 162 Sets), the bundle of convert_bsi.py v0.2, in which a nested control was a
   statement of its parent; that bundle was replaced on 2026-11-14 and is no expectation of this test any more. */
test("BSI preset: every object has the semantic digest of the committed DE.BSI bundle, 1,287 of 1,287", { skip: missing(BSI_SRC) }, async () => {
  const dir = path.join(ROOT, "converted_examples/DE.BSI/bsi-core-bundle"), manifest = json(path.join(dir, "content-manifest.json"));
  const src = json(BSI_SRC);
  assert.equal(src.catalog.metadata.version, manifest.provenance.sources[0].version, "the source file is the version the committed bundle was converted from");
  assert.equal(oscal.jscOscalGuessPreset(src), "bsi-gspp");
  const out = oscal.jscOscalImportCatalog(src, { preset: "bsi-gspp" });
  const want = new Map(manifest.objects.map(e => [e.path, e]));
  assert.deepEqual(out.objects.map(o => o.path).sort(), [...want.keys()].sort(), "the same files");
  let same = 0, first = "";
  for (const o of out.objects) {
    const e = want.get(o.path);
    if (o.obj.id === e.id && await core.jscSemanticDigest(o.obj) === e["semantic-digest"]) same++; else first = first || o.path;
  }
  assert.deepEqual([same, out.objects.length, manifest.objects.length], [1287, 1287, 1287], `objects whose meaning is the committed bundle's (the first that differs: ${first})`);
  assert.deepEqual([out.objects.filter(o => o.obj.statements).length, out.objects.filter(o => o.obj.members).length], [999, 288], "999 Requirements and 288 Sets");
  /* and the files the Import page would write are the converter's, byte for byte, but for the line ends (the
     converter writes CRLF, BUNDLE_NEWLINE): the order of the keys is the converter's too */
  const lf = f => fs.readFileSync(path.join(dir, f), "utf8").replace(/\r\n/g, "\n");
  assert.deepEqual(out.objects.filter(o => core.jscSerialize(o.obj) !== lf(o.path)).map(o => o.path), [], "objects whose bytes differ from the committed file");
  for (const f of out.facetSchemas) assert.equal(core.jscSerialize(f.def), lf(f.path), f.path);
  assert.deepEqual(out.facetSchemas.map(f => f.path).sort(), manifest["facet-schemas"].map(e => e.path).sort());
  /* who wrote the document and when stands in the provenance of the import as in the converter's manifest */
  assert.deepEqual(out.provenance.sources, manifest.provenance.sources);
  assert.equal(out.provenance.sources[0]["author-ref"], "https://ns.bsi.bund.de/gspp/party/bundesamt-fuer-sicherheit-in-der-informationstechnik");
  // the converter's own counts: lists packed into one comma-separated value are reported; the {{Label}}
  // slots of the sentence template are parameters, every one where the prose inserts a parameter
  const packed = {};
  for (const d of out.report["packed-list-values"]) packed[d.prop] = (packed[d.prop] || 0) + 1;
  assert.deepEqual(packed, { tags: 125, threats: 616, target_object_categories: 40 });
  assert.equal(out.report["parameter-slots"], 221);
  assert.deepEqual(out.report["parameter-slots-not-at-insert"], []);
  assert.deepEqual([out.report.controls, out.report.statements, out.report["controls-with-nested-controls"]], [999, 999, 126]);
});

/* ERRATA 2026-11-14: before build 0.9.14 the preset turned a nested control into a second statement of its parent's
   Requirement. The control's own links were not read (75 links on 60 nested controls of the pinned catalogue), and a
   link that named a nested control became a relation to an id that was no object (34 of the 191 relations it wrote).
   This test reads the source itself and holds the result to it, so it needs no committed bundle to say what is
   right. */
test("BSI preset: a nested control is a Requirement of its own with its own links; its parent gives a Set that groups them; no relation is made up and none points at nothing", { skip: missing(BSI_SRC) }, () => {
  const NS = "https://ns.bsi.bund.de/gspp", src = json(BSI_SRC), out = oscal.jscOscalImportCatalog(src, { preset: "bsi-gspp" });
  const byId = new Map(out.objects.map(o => [o.obj.id, o.obj])), req = id => byId.get(`${NS}/req/${id}`), slug = id => id.toLowerCase().replace(/[^a-z0-9]+/g, "-");
  /* the controls of the source in document order, each with its depth and its parent */
  const controls = [];
  const walk = (c, depth, parent) => { controls.push({ c, depth, parent }); for (const ch of c.controls || []) walk(ch, depth + 1, c); };
  const groups = g => { for (const sub of g.groups || []) groups(sub); for (const c of g.controls || []) walk(c, 0, null); };
  for (const g of src.catalog.groups) groups(g);
  const nested = controls.filter(x => x.depth > 0), parents = controls.filter(x => (x.c.controls || []).length);
  assert.deepEqual([controls.length, nested.length, parents.length, Math.max(...controls.map(x => x.depth))], [999, 348, 126, 3]);
  /* every control, at every depth, is one Requirement with one statement, `smt`, under its own id */
  for (const { c } of controls) {
    const r = req(c.id);
    assert.ok(r, c.id + " is a Requirement");
    assert.deepEqual([r.statements.map(st => st.id), r.title], [["smt"], { de: c.title }], c.id);
    /* its relations are its own links, one for one and in order; nothing else is a relation */
    assert.deepEqual((r.relations || []).map(x => [x.type, x.ref]), (c.links || []).map(l => [l.rel, `${NS}/req/${l.href.slice(1)}`]), c.id + ": the relations are the control's own links");
  }
  const links = controls.reduce((n, x) => n + (x.c.links || []).length, 0), onNested = nested.filter(x => (x.c.links || []).length);
  assert.deepEqual([links, onNested.length, onNested.reduce((n, x) => n + x.c.links.length, 0)], [266, 60, 75], "266 links, 75 of them on 60 nested controls");
  const relations = out.objects.flatMap(o => (o.obj.relations || []).map(x => x.ref));
  assert.equal(relations.length, 266);
  assert.deepEqual(relations.filter(ref => !byId.has(ref)), [], "no relation points at an id that is no object");
  assert.deepEqual(req("GC.5.1.4").relations, [{ type: "required", ref: `${NS}/req/GC.5.1.3` }], "a link of a nested control, which the preset used to lose");
  /* nesting is grouping and nothing else: a control with nested controls gives a Set, whose members are its own
     Requirement and then what stands for each nested control, in the order of the source */
  for (const { c } of parents) {
    const set = byId.get(`${NS}/set/tax/${slug(c.id)}`);
    assert.ok(set && set.members, c.id + " gives a grouping Set");
    assert.deepEqual(set.members.map(m => m.ref), [`${NS}/req/${c.id}`, ...c.controls.map(ch => ((ch.controls || []).length ? `${NS}/set/tax/${slug(ch.id)}` : `${NS}/req/${ch.id}`))], c.id + ": the members and their order");
    assert.deepEqual(Object.keys(set).sort(), ["id", "lifecycle", "members", "title", "version"], c.id + ": a grouping Set has no label, alias or facet");
    assert.deepEqual(set.members.map(m => m.sequence), [...set.members.map(m => m.sequence)].sort((a, b) => a - b), c.id + ": numbered in that order");
    const mine = [`${NS}/req/${c.id}`, ...c.controls.map(ch => `${NS}/req/${ch.id}`)];
    for (const id of mine) for (const x of byId.get(id).relations || []) {
      const fromLink = [c, ...c.controls].find(k => `${NS}/req/${k.id}` === id).links.some(l => `${NS}/req/${l.href.slice(1)}` === x.ref);
      assert.ok(fromLink, `${id} -> ${x.ref} is a link of the source and not made from the nesting`);
    }
  }
  assert.deepEqual(byId.get(`${NS}/set/tax/gc-3-1`).members, [70, 80, 90, 100, 110].map((sequence, i) => ({ ref: `${NS}/req/GC.3.1${i ? "." + i : ""}`, sequence })), "the numbering of one grouping Set, as the converter numbers it");
  /* in the Set of its group, or of its parent, the grouping Set stands where the control stood */
  const memberOf = new Map(out.objects.filter(o => o.obj.members && !o.obj.id.includes("/set/baseline/")).flatMap(o => o.obj.members.map(m => [m.ref, o.obj.id])));
  for (const { c, parent } of controls) {
    const stands = (c.controls || []).length ? `${NS}/set/tax/${slug(c.id)}` : `${NS}/req/${c.id}`;
    if (parent) assert.equal(memberOf.get(stands), `${NS}/set/tax/${slug(parent.id)}`, c.id + " stands in the Set of its parent");
    else assert.ok(memberOf.has(stands) && memberOf.get(stands) !== `${NS}/set/tax/${slug(c.id)}`, c.id + " stands in the Set of its group");
  }
  /* a baseline lists the Requirements of all controls of its sec_level in document order, a control before the
     controls nested in it, and a nested control in the baseline of its own sec_level, not of its parent's */
  const level = c => ((c.props || []).find(p => p.name === "sec_level") || {}).value;
  for (const lvl of [...new Set(controls.map(x => level(x.c)).filter(Boolean))]) {
    const set = out.objects.map(o => o.obj).find(o => o.title && o.title.de === `Baseline sec_level: ${lvl}`);
    assert.deepEqual(set.members, controls.filter(x => level(x.c) === lvl).map((x, i) => ({ ref: `${NS}/req/${x.c.id}`, sequence: (i + 1) * 10 })), lvl);
  }
  assert.ok(nested.some(x => level(x.c) && level(x.parent) && level(x.c) !== level(x.parent)), "the catalogue has nested controls whose sec_level is not their parent's, so the last assertion says something");
  /* the taxonomy payload holds what classifies the control, and no longer its title, label or alt-identifier */
  const TAX = "https://ns.bsi.bund.de/facet/gspp-taxonomy@1", keys = new Set(out.objects.flatMap(o => Object.keys((((o.obj.facets || {})[TAX] || {})["by-statement"] || {}).smt || {})));
  assert.deepEqual([...keys].sort(), ["class", "effort", "sec-level", "tags"]);
  /* what the document says of itself stands on the root Set, as the source holds it */
  const { title, version, ...rest } = src.catalog.metadata;
  assert.deepEqual(byId.get(`${NS}/set/tax/root`).facets, { "https://ns.jascon.net/compat/oscal-1x@1": { metadata: rest } });
});

/* What the pinned catalogue does not hold, in a catalogue of the Grundschutz++ shape written for the tests: a prop
   in another namespace, a prop that repeats, members the mapping has no place for, a part of another name, a link
   that says more than rel and href, a back-matter resource, a group without controls, a control outside any group,
   a fraction, a modal verb outside the table, an author with umlauts. The rule is that content is not dropped: what
   the mapping does not read is carried as the source holds it, in the compat facet. */
const BSI_CSV = "https://github.com/BSI-Bund/Stand-der-Technik-Bibliothek/tree/main/Dokumentation/namespaces/", BSI_RES = "11111111-2222-4333-8444-555555555555";
const bsiSynthetic = () => {
  const CSV = BSI_CSV, RES = BSI_RES;
  return { catalog: { uuid: "c-1", remarks: "a note on the catalogue",
    metadata: { title: "Anwenderkatalog Grundschutz++ (Probe)", version: "9", "oscal-version": "1.1.3", "last-modified": "2026-11-14T10:00:00Z",
      roles: [{ id: "creator", title: "Creator" }], parties: [{ uuid: "p-0", type: "person", name: "Erika Mustermann" }, { uuid: "p-1", type: "organization", name: "Bundesamt für Größe und Maß" }],
      "responsible-parties": [{ "role-id": "creator", "party-uuids": ["p-1"] }] },
    "back-matter": { resources: [{ uuid: RES, title: "A standard", rlinks: [{ href: "https://standards.example/a" }] }, { uuid: "99999999-2222-4333-8444-555555555555", title: "Named by nobody" }] },
    groups: [
      { id: "EMPTY", title: "A practice without controls", props: [{ name: "label", value: "EMPTY", remarks: "What the practice is about." }, { name: "label", ns: "https://other.example/ns", value: "another label" }, { name: "colour", value: "blue" }], weight: 0.25 },
      { id: "X", title: "A practice", props: [{ name: "label", value: "old X" }, { name: "label", value: "X" }, { name: "alt-identifier", value: "g-uuid" }], controls: [
        { id: "X.1", class: "x", title: "One", status: "new",
          props: [{ name: "alt-identifier", value: "u-1" }, { name: "sec_level", ns: CSV + "security_level.csv", value: "normal-SdT" }, { name: "sec_level", ns: "https://other.example/ns", value: "geheim" },
            { name: "tags", ns: CSV + "tags.csv", value: "a, b" }, { name: "tags", ns: CSV + "tags.csv", value: "c", class: "late" }, { name: "weight", value: "heavy" }],
          params: [{ id: "x.1-prm1", label: "", values: ["one", "two"], props: [{ name: "alt-identifier", value: "pu-1" }, { name: "unit", value: "days" }], usage: "free" }],
          parts: [{ id: "X.1_stm", name: "statement", prose: "X MUSS {{ insert: param, x.1-prm1 }} tun.", title: "a title on the part",
              props: [{ name: "modal_verb", ns: CSV + "modal_verbs.csv", value: "MUSS" }, { name: "modal_verb", value: "KANN" }, { name: "documentation", ns: CSV + "documentation_guidelines.csv", value: " , " }] },
            { id: "X.1_gdn", name: "guidance", prose: "Why.", class: "hint" }, { id: "X.1_other", name: "example", prose: "For instance." }],
          links: [{ href: "#X.2", rel: "required", text: "see also" }, { href: "#" + RES, rel: "reference" }, { href: "https://elsewhere.example/doc" }],
          controls: [{ id: "X.1.1", title: "Nested", props: [{ name: "modal_verb", ns: CSV + "modal_verbs.csv", value: "MUSS" }], parts: [{ id: "elsewhere", name: "statement", prose: "Nested MUSS.", props: [{ name: "modal_verb", ns: CSV + "modal_verbs.csv", value: "WIRD" }] }] }] },
        { id: "X.2", title: "Two", parts: [{ name: "guidance" }] }] }],
    controls: [{ id: "LOOSE.1", title: "In no group", parts: [{ id: "LOOSE.1_stm", name: "statement", prose: "Loose SOLLTE.", props: [{ name: "modal_verb", ns: CSV + "modal_verbs.csv", value: "constructor" }] }] }] } };
};
/* The expectations below were written from the code of convert_bsi.py v0.3, and the next test holds every object to
   what the converter itself writes for this catalogue. */
test("BSI preset: what the mapping does not read is carried as the source holds it; a prop counts only in its namespace; a group without controls and a control outside a group are kept", () => {
  const NS = "https://ns.bsi.bund.de/gspp", CSV = BSI_CSV, COMPAT = "https://ns.jascon.net/compat/oscal-1x@1";
  const cat = bsiSynthetic(), before = JSON.stringify(cat), out = oscal.jscOscalImportCatalog(cat, { preset: "bsi-gspp" });
  assert.equal(JSON.stringify(cat), before, "the source is not changed by the import");
  const byId = new Map(out.objects.map(o => [o.obj.id, o.obj])), req = id => byId.get(`${NS}/req/${id}`), set = id => byId.get(`${NS}/set/tax/${id}`);
  assert.deepEqual(out.objects.map(o => o.path), ["set-tax-empty", "req-x-1", "req-x-1-1", "set-tax-x-1", "req-x-2", "set-tax-x", "req-loose-1", "set-tax-root", "set-baseline-normal-sdt"].map(n => `objects/gspp/${n}.json`));
  /* a prop is read in its own namespace only; one of the same name in another, an earlier one of a name that repeats,
     one that holds a further member and one the mapping does not know are carried whole */
  const x1 = req("X.1"), c = x1.facets[COMPAT];
  assert.deepEqual(x1.facets["https://ns.bsi.bund.de/facet/gspp-taxonomy@1"]["by-statement"].smt, { class: "x", "sec-level": "normal-SdT", tags: ["c"] }, "the last tags prop is read");
  assert.deepEqual(c.props, [{ name: "sec_level", ns: "https://other.example/ns", value: "geheim" }, { name: "tags", ns: CSV + "tags.csv", value: "a, b" },
    { name: "tags", ns: CSV + "tags.csv", value: "c", class: "late" }, { name: "weight", value: "heavy" }]);
  assert.deepEqual(Object.keys(c), ["param-extras", "props", "parts", "links", "control"], "the members of the compat facet in the converter's order");
  assert.deepEqual(c["param-extras"], { "x.1-prm1": { "alt-identifier": "pu-1", values: ["one", "two"], label: "", props: [{ name: "unit", value: "days" }], usage: "free" } });
  assert.deepEqual(x1.statements[0].parameters, [{ name: "x.1-prm1", type: "string", default: "one" }]);
  /* of a part that is read, what is left; a part of another name, whole; the id of a part only where it is not the control's id and the suffix */
  assert.deepEqual(c.parts, [{ name: "statement", title: "a title on the part", props: [{ name: "modal_verb", value: "KANN" }, { name: "documentation", ns: CSV + "documentation_guidelines.csv", value: " , " }] },
    { name: "guidance", class: "hint" }, { id: "X.1_other", name: "example", prose: "For instance." }]);
  assert.deepEqual(x1.facets["https://ns.jascon.net/stdlib/facet/assessment-criteria@1"]["by-statement"].smt, { "required-documentation": [] }, "a list prop without a term gives an empty list, and its value is carried");
  /* a link is a relation; one that says more is carried whole beside it; one that names a back-matter resource gives the address the resource gives */
  assert.deepEqual(x1.relations, [{ type: "required", ref: `${NS}/req/X.2` }, { type: "reference", ref: "https://standards.example/a" }, { type: "related", ref: "https://elsewhere.example/doc" }]);
  assert.deepEqual(c.links, [{ href: "#X.2", rel: "required", text: "see also" }]);
  assert.deepEqual(c.control, { status: "new" });
  /* a nested control: its statement part is the one named `statement`; a verb outside the table is `unspecified` and carried; a modal_verb on the control is not the statement's */
  const nested = req("X.1.1");
  assert.deepEqual([nested.statements[0].modality, nested.statements[0].prose], ["unspecified", { de: "Nested MUSS." }]);
  assert.deepEqual(nested.facets[COMPAT], { props: [{ name: "modal_verb", ns: CSV + "modal_verbs.csv", value: "MUSS" }], parts: [{ id: "elsewhere", name: "statement", props: [{ name: "modal_verb", ns: CSV + "modal_verbs.csv", value: "WIRD" }] }] });
  /* the name of a member every JavaScript object has is no modal verb of the table either */
  assert.deepEqual([req("LOOSE.1").statements[0].modality, req("LOOSE.1").facets[COMPAT]], ["unspecified", { parts: [{ name: "statement", props: [{ name: "modal_verb", ns: CSV + "modal_verbs.csv", value: "constructor" }] }] }]);
  assert.deepEqual(out.report["unknown-modal-verbs"], { WIRD: 1, constructor: 1 });
  assert.deepEqual(req("X.2").facets[COMPAT], { parts: [{ name: "guidance" }] }, "a guidance without a prose is not read and is carried whole");
  assert.equal(req("X.2").statements[0].prose.de, "", "a control without a statement part has an empty statement");
  /* a group: the last label without a namespace is read, the others are carried; a member the mapping does not know is
     carried, a fraction as a decimal string; a group without controls gives a Set without members */
  assert.deepEqual(set("empty"), { id: `${NS}/set/tax/empty`, version: "9", lifecycle: "active", title: { de: "A practice without controls" }, members: [], label: "EMPTY",
    facets: { "https://ns.bsi.bund.de/facet/gspp-narrative@1": { description: { de: "What the practice is about." } },
      [COMPAT]: { props: [{ name: "label", ns: "https://other.example/ns", value: "another label" }, { name: "colour", value: "blue" }], group: { weight: "0.25" } } } });
  assert.deepEqual([set("x").label, set("x").aliases, set("x").facets[COMPAT]], ["X", [{ scheme: "bsi-uuid", value: "g-uuid" }], { props: [{ name: "label", value: "old X" }] }]);
  /* one counter for the run, step 10, taken when an entry is appended: the empty group is 10, then the control's own
     Requirement, its nested control, the grouping Set after its members, the next control, the group, the loose control */
  assert.deepEqual(set("x-1").members, [{ ref: `${NS}/req/X.1`, sequence: 20 }, { ref: `${NS}/req/X.1.1`, sequence: 30 }]);
  assert.deepEqual(set("x").members, [{ ref: `${NS}/set/tax/x-1`, sequence: 40 }, { ref: `${NS}/req/X.2`, sequence: 50 }], "the grouping Set stands where the control stood, numbered after its members");
  /* the root: the groups, then a control that stands in no group; what the document says of itself; a resource that a link names, whole */
  const root = set("root");
  assert.deepEqual(root.members, [{ ref: `${NS}/set/tax/empty`, sequence: 10 }, { ref: `${NS}/set/tax/x`, sequence: 60 }, { ref: `${NS}/req/LOOSE.1`, sequence: 70 }]);
  const { title, version, ...meta } = cat.catalog.metadata;
  assert.deepEqual(root.facets[COMPAT], { metadata: meta, "back-matter": { resources: [cat.catalog["back-matter"].resources[0]] }, catalog: { remarks: "a note on the catalogue" } });
  /* who wrote the document: the party's name in ASCII as a German reader writes it, then the slug */
  assert.deepEqual(out.provenance.sources, [{ key: "gspp", title: "Anwenderkatalog Grundschutz++ (Probe)", version: "9", "oscal-version": "1.1.3",
    "author-ref": `${NS}/party/bundesamt-fuer-groesse-und-mass`, date: "2026-11-14" }]);
  assert.deepEqual(out.report["carried-as-the-source-holds-it"], { "param-extras beyond the alt-identifier": 1, props: 4, parts: 4, links: 1, control: 1, group: 1, metadata: 1, "back-matter": 1, catalog: 1 });
  /* Every object is a valid kernel object but one, and the pinned compat schema accepts every compat payload. The one:
     a control without a statement prose gives a statement with an empty prose, here as in the converter, and the kernel
     refuses an empty text. Nothing is dropped and nothing is made up; the Import page then writes nothing and says how
     many objects are not valid. The pinned catalogue has no such control. */
  for (const o of out.objects) {
    assert.deepEqual(rules.jscObjectErrors(o.obj).errors, o.obj.id === `${NS}/req/X.2` ? ["matches NO type (closest requirement: /statements/0/prose/de: matches none of the allowed shapes)"] : [], o.path);
  }
  const pinned = new Map(out.facetSchemas.map(f => [f.def.id, f.def.schema]));
  assert.deepEqual(rules.jscFacetErrors(out.objects.map(o => [o.obj.id, o.obj]), pinned), []);
});

/* convert_bsi.py decides, also where the pinned catalogue has nothing to show: the converter is run on the catalogue
   of the test above in a tree of its own, and every object, the pinned schemas and the provenance of the source are
   compared. On this catalogue the converter writes its bundle and then ends with exit code 1 for one wiring check of
   its own (measured 2026-11-14): it carries an empty parameter label in compat param-extras, as the preset does,
   and its path map names no place there for `params[].label`. That is a finding about the converter, reported to
   the author; this test accepts that one failure and no other, and a run without it. */
test("BSI preset: on a catalogue of the Grundschutz++ shape with what the pinned one lacks, every object has the semantic digest of convert_bsi.py", { skip: !python && "python3 is not installed" }, async () => {
  const src = bsiSynthetic(), tmp = fs.mkdtempSync(path.join(os.tmpdir(), "jascon-bsi-"));
  try {
    fs.mkdirSync(path.join(tmp, "jascon/scripts"), { recursive: true });
    fs.mkdirSync(path.join(tmp, "sources"));
    for (const f of ["convert_bsi.py", "oscal_conv_lib.py"]) fs.copyFileSync(path.join(ROOT, "jascon/scripts", f), path.join(tmp, "jascon/scripts", f));
    fs.cpSync(path.join(ROOT, "jascon/schemas"), path.join(tmp, "jascon/schemas"), { recursive: true });
    fs.writeFileSync(path.join(tmp, "sources/Grundschutz++-catalog.json"), JSON.stringify(src));
    const run = spawnSync("python3", [path.join(tmp, "jascon/scripts/convert_bsi.py")], { cwd: tmp, encoding: "utf8" });
    const known = /^convert_bsi\.py: 1 wiring check\(s\) failed, 0 claim\(s\) of the conversion ledger do not hold on the written files, 0 source value\(s\) are unaccounted$/m;
    assert.ok(run.status === 0 || (run.status === 1 && known.test(run.stderr) && /params\[\]\.label stand at \S*\/param-extras\/\{param\}\/label, a place the path map does not name/.test(run.stderr)),
      `the converter ran (exit ${run.status}): ${run.stderr.slice(-1500)}`);
    const dir = path.join(tmp, "converted_examples/DE.BSI/bsi-core-bundle"), manifest = json(path.join(dir, "content-manifest.json"));
    const out = oscal.jscOscalImportCatalog(src, { preset: "bsi-gspp" });
    const want = new Map(manifest.objects.map(e => [e.path, e]));
    assert.deepEqual(out.objects.map(o => o.path).sort(), [...want.keys()].sort(), "the same files");
    assert.equal(out.objects.length, 9);
    for (const o of out.objects) {
      assert.equal(o.obj.id, want.get(o.path).id, o.path);
      assert.equal(await core.jscSemanticDigest(o.obj), want.get(o.path)["semantic-digest"], o.path + " has the converter's meaning");
      assert.equal(core.jscSerialize(o.obj), fs.readFileSync(path.join(dir, o.path), "utf8").replace(/\r\n/g, "\n"), o.path + " has the converter's bytes, but for the line ends");
    }
    assert.deepEqual(out.facetSchemas.map(f => f.path).sort(), manifest["facet-schemas"].map(e => e.path).sort());
    for (const f of out.facetSchemas) assert.equal(core.jscSerialize(f.def), fs.readFileSync(path.join(dir, f.path), "utf8").replace(/\r\n/g, "\n"), f.path);
    assert.deepEqual(out.provenance.sources, manifest.provenance.sources, "who wrote the document and when, as the converter writes it");
  } finally { fs.rmSync(tmp, { recursive: true, force: true }); }
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
  /* The presets for a publisher's corpus follow their converters. Until build 0.9.12 that meant they took no party from
     the caller; since the converters have `--obligated-party` (backlog #74) the caller's party stands in the default's
     place, and the default stands where the caller gives none. The tests at the end of this file hold the rest. */
  const cis = oscal.jscOscalImportCatalog(src, { preset: "cis-benchmark", party: "https://publisher.example/party/operator" });
  assert.deepEqual(parties(cis), ["https://publisher.example/party/operator"]);
  assert.deepEqual(parties(oscal.jscOscalImportCatalog(src, { preset: "cis-benchmark" })), ["https://ns.cisecurity.org/benchmark/ubuntu-24.04-lts/party/system-administrator"]);
});

/* Since build 0.9.15 the profile's metadata and merge directive stand on its Set in the compat facet, as convert_nist.py
   writes them on the baseline Set; until then the merge directive was reported as not carried and the metadata was not
   read. */
test("profile: NIST MODERATE selects the members of the shipped MODERATE baseline, and its Set carries what the converter's baseline Set carries", { skip: missing(NIST_MOD) }, () => {
  const dir = path.join(ROOT, "converted_examples/US.SP800-53/sp800-53-core-bundle"), manifest = json(path.join(dir, "content-manifest.json"));
  const objs = new Map(manifest.objects.map(e => { const o = json(path.join(dir, e.path)); return [o.id, { type: core.jscInferType(o), obj: o }]; }));
  const pins = manifest["facet-schemas"].map(e => json(path.join(dir, e.path)));
  const out = oscal.jscOscalImportProfile(json(NIST_MOD), { ns: "https://org.example", lang: "en", objs, facetSchemas: pins });
  const set = out.objects.find(o => o.obj.members).obj, tailoring = out.objects.find(o => o.obj.selects).obj;
  const shipped = objs.get("https://ns.nist.gov/sp800-53/set/baseline/moderate").obj;
  assert.deepEqual(set.members.map(m => m.ref), shipped.members.map(m => m.ref), "the members, in the profile's order");
  assert.equal(set.members.length, 287);
  assert.deepEqual(out.report["not-found"], []);
  assert.deepEqual(tailoring.selects, [{ "set-ref": set.id }]);
  assert.deepEqual(set.facets, shipped.facets, "the profile's metadata and merge directive, as the converter carries them");
  assert.deepEqual([out.report["held-in-compat"], out.report["not-carried"], out.facetSchemas], [["metadata", "merge"], {}, []], "the bundle pins the schema; none is brought");
  assert.deepEqual(rules.jscFacetErrors([[set.id, set]], new Map(pins.map(d => [d.id, d.schema]))), []);
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
  /* an include-all makes no Set of the profile, so its merge directive has no place (since build 0.9.15 a profile with a
     Set of its own carries it there, below) */
  assert.deepEqual(Object.keys(out.report["not-carried"]).sort(), ["alters with adds", "merge (as-is): the profile makes no Set of its own to carry it"]);
  assert.deepEqual(rules.jscMatchTypes(t), ["tailoring"]);

  /* with a Set of its own: what the profile says of itself and its merge directive stand on it, in the compat facet. A
     set that pins no schema for that facet gets the one convert_nist.py pins; a set that pins one without `merge` (as
     convert_bsi.py's does) gets the metadata only, and the report says why the merge directive is not carried. */
  const named = { profile: { uuid: "y", metadata: { title: "Picked", version: "3", "last-modified": "2026-11-01T00:00:00Z", remarks: "a few" },
    imports: [{ href: "#cat", "include-controls": [{ "with-ids": ["ac-1", "ac-2"] }] }], merge: { "as-is": true } } };
  const COMPAT = "https://ns.jascon.net/compat/oscal-1x";
  const plain = oscal.jscOscalImportProfile(named, { ns: "https://org.example", lang: "en", objs });
  const set = plain.objects.find(o => o.obj.members).obj;
  assert.deepEqual(set.facets, { [COMPAT + "@1"]: { metadata: { "last-modified": "2026-11-01T00:00:00Z", remarks: "a few" }, merge: { "as-is": true } } });
  assert.deepEqual([plain.facetSchemas.map(f => [f.path, f.def.id, Object.keys(f.def.schema.properties)]), plain.report["held-in-compat"], plain.report["not-carried"]],
    [[["schemas/oscal-1x-compat-1.0.0-stub.json", COMPAT, ["metadata", "merge", "class"]]], ["metadata", "merge"], {}]);
  assert.deepEqual(rules.jscFacetErrors([[set.id, set]], new Map(plain.facetSchemas.map(f => [f.def.id, f.def.schema]))), []);
  const bsiPin = { id: COMPAT, version: "1.0.0", schema: { type: "object", properties: { metadata: { type: "object" }, props: { type: "array" } }, additionalProperties: false } };
  const narrow = oscal.jscOscalImportProfile(named, { ns: "https://org.example", lang: "en", objs, facetSchemas: [bsiPin] });
  assert.deepEqual([narrow.objects.find(o => o.obj.members).obj.facets[COMPAT + "@1"], narrow.facetSchemas, narrow.report["not-carried"]],
    [{ metadata: { "last-modified": "2026-11-01T00:00:00Z", remarks: "a few" } }, [], { [`merge (as-is): the set pins ${COMPAT} without it`]: 1 }]);
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
/* The preset follows convert_nist.py v0.2 since build 0.9.15, and the committed bundle decides: on the pinned catalogue
   (converted_examples/US.SP800-53/SOURCES.sha256) every object it writes has the semantic digest the manifest records,
   and the bytes of the committed file but for the line ends (the converter writes CRLF). 1,037 objects: the bundle's
   1,041 without its four baseline Sets, which are profiles and are imported as profiles. Until then the preset wrote
   1,035 objects after convert_nist.py v0.1, and the test let four of them differ, because NIST had republished its 5.2.0
   file after that bundle was converted; the bundle is converted from the pinned file since 2026-11-14, and nothing may
   differ any more. */
test("NIST preset: the objects of the committed SP 800-53 bundle, 1,037 of 1,037 by semantic digest and by bytes", { skip: missing(NIST_SRC) }, async () => {
  const dir = path.join(ROOT, "converted_examples/US.SP800-53/sp800-53-core-bundle"), manifest = json(path.join(dir, "content-manifest.json"));
  const src = json(NIST_SRC);
  assert.equal(src.catalog.metadata.version, manifest.provenance["source-version"], "the source file is the version the committed bundle was converted from");
  assert.equal(oscal.jscOscalGuessPreset(src), "nist-sp800-53");
  const out = oscal.jscOscalImportCatalog(src, { preset: "nist-sp800-53" });
  const want = new Map(manifest.objects.map(e => [e.path, e]));
  /* the baselines are profiles; the preset makes no Set for them */
  assert.deepEqual(out.objects.map(o => o.path).sort(), [...want.keys()].filter(p => !/\/baseline-/.test(p)).sort(), "the same files, without the baseline Sets");
  let same = 0, first = "";
  for (const o of out.objects) {
    const e = want.get(o.path);
    if (o.obj.id === e.id && await core.jscSemanticDigest(o.obj) === e["semantic-digest"]) same++; else first = first || o.path;
  }
  assert.deepEqual([same, out.objects.length, manifest.objects.length], [1037, 1037, 1041], `objects whose meaning is the committed bundle's (the first that differs: ${first})`);
  const lf = f => fs.readFileSync(path.join(dir, f), "utf8").replace(/\r\n/g, "\n");
  assert.deepEqual(out.objects.filter(o => core.jscSerialize(o.obj) !== lf(o.path)).map(o => o.path), [], "objects whose bytes differ from the committed file");
  assert.deepEqual(out.facetSchemas.map(f => f.path).sort(), manifest["facet-schemas"].map(e => e.path).sort());
  for (const f of out.facetSchemas) assert.equal(core.jscSerialize(f.def), lf(f.path), f.path);
  /* who wrote the catalogue and when, as the converter's manifest names them */
  assert.deepEqual([out.provenance.sources[0]["author-ref"], out.provenance.sources[0].date], [manifest.provenance["author-ref"], manifest.provenance.date]);
  /* the converter's own counts (sp800-53-coverage-report.json) */
  assert.deepEqual([out.report.controls, out.report.statements, out.report["withdrawn-not-converted"], out.report["withdrawn-without-successor"]], [1016, 1920, 180, ["cp-10.3", "sc-19"]]);
  assert.deepEqual([out.report["assessment-for"], out.report["formal-odp-labels"], out.report["controls-without-a-stated-party"], out.report["parameters-without-insertion"]], [3707, 1458, 2, 399]);
  assert.deepEqual([out.report["links-not-written"], out.report["props-not-read"]], [{}, {}], "every link and every prop of the pinned catalogue is read");
});

/* A catalogue of the SP 800-53 shape, written for the tests, with what the pinned one holds and the preset of build 0.9.14
   lost: objectives that name the statement they assess (of the same control, its statement part as a whole, another
   control's), a withdrawn control that names no successor, a formal ODP label, a markdown link in a text, a family's
   overview with its title, back-matter resources with their uuids and two links, `contributes-to-assurance` false, the
   document's metadata with its author; and the four baseline profiles convert_nist.py reads beside it. */
const NIST_RMF = "http://csrc.nist.gov/ns/rmf";
const nistLabel = (v, cls) => ({ name: "label", value: v, ...(cls ? { class: cls } : {}) });
const nistSynthetic = () => {
  const rmf = NIST_RMF, label = nistLabel;
  return { catalog: { uuid: "c-1",
    metadata: { title: "Electronic (OSCAL) Version of NIST SP 800-53 Rev 5 test", "last-modified": "2026-05-11T16:01:09.00000-00:00", version: "9.9", "oscal-version": "1.1.2",
      roles: [{ id: "creator", title: "Document Creator" }], parties: [{ uuid: "p-1", type: "organization", name: "OSCAL Program" }],
      "responsible-parties": [{ "role-id": "creator", "party-uuids": ["p-1"] }] },
    "back-matter": { resources: [{ uuid: "u1", title: "Zeta", rlinks: [{ href: "https://example.org/zeta" }, { href: "https://example.org/zeta.pdf", "media-type": "application/pdf" }] },
      { uuid: "u2", title: "Alpha", citation: { text: "Alpha, 2020." } }] },
    groups: [{ id: "ac", class: "family", title: "Access Control", props: [label("AC")], parts: [{ id: "ac_ovw", name: "overview", title: "Access Control Overview", prose: "About access, see [Zeta](#u1)." }], controls: [
      { id: "ac-1", class: "SP800-53", title: "Policy", props: [label("AC-1"), label("AC-01", "sp800-53a"), { name: "sort-id", value: "ac-01" }, { name: "implementation-level", ns: rmf, value: "system" },
          { name: "contributes-to-assurance", ns: rmf, value: "false" }],
        params: [{ id: "ac-1_prm_1", props: [label("AC-01_ODP[01]", "sp800-53a")], label: "frequency" },
          { id: "ac-1_prm_2", select: { "how-many": "one-or-more", choice: ["daily", "per {{ insert: param, ac-1_prm_1 }}"] } },
          { id: "ac-1_prm_3", props: [{ name: "alt-identifier", value: "old-3" }, { name: "alt-label", class: "sp800-53", value: "the third" }] }],
        links: [{ rel: "related", href: "#ac-2" }, { rel: "related", href: "#ac-2" }, { rel: "related", href: "#ac-9" }, { rel: "reference", href: "#u1" }, { rel: "reference", href: "#u2" }],
        parts: [{ id: "ac-1_smt", name: "statement", parts: [
            { id: "ac-1_smt.a", name: "item", props: [label("a.")], prose: "Review every {{ insert: param, ac-1_prm_1 }} as [SP 800-12](#u1) says." },
            { id: "ac-1_smt.b", name: "item", props: [label("b.")], prose: "Use {{ insert: param, ac-2_prm_1 }}." }] },
          { id: "ac-1_gdn", name: "guidance", prose: "See [AC-2](#ac-2)." },
          { id: "ac-1_obj", name: "assessment-objective", props: [label("AC-01", "sp800-53a")], links: [{ href: "#ac-1_smt", rel: "assessment-for" }], parts: [
            { id: "ac-1_obj.a", name: "assessment-objective", props: [label("AC-01a.", "sp800-53a")], links: [{ href: "#ac-1_smt.a", rel: "assessment-for" }], prose: "the review happens;" },
            { id: "ac-1_obj.b", name: "assessment-objective", props: [label("AC-01b.", "sp800-53a")], links: [{ href: "#ac-2_smt", rel: "assessment-for" }], prose: "the accounts are used;" }] },
          { id: "ac-1_asm-examine", name: "assessment-method", props: [{ name: "method", ns: rmf, value: "EXAMINE" }, label("AC-01-Examine", "sp800-53a")],
            parts: [{ name: "assessment-objects", prose: "Policy\n\nProcedures for {{ insert: param, ac-1_prm_3 }}" }] }],
        controls: [{ id: "ac-1.1", class: "SP800-53-enhancement", title: "Enhancement", props: [label("AC-1(1)"), label("AC-01(01)", "zero-padded"), { name: "sort-id", value: "ac-01.01" },
            { name: "implementation-level", ns: rmf, value: "organization" }, { name: "contributes-to-assurance", ns: rmf, value: "true" }],
          parts: [{ id: "ac-1.1_smt", name: "statement", prose: "Do more." }] }] },
      { id: "ac-2", class: "SP800-53", title: "Accounts", props: [label("AC-2"), { name: "sort-id", value: "ac-02" }, { name: "implementation-level", ns: rmf, value: "organization" }],
        params: [{ id: "ac-2_prm_1" }], parts: [{ id: "ac-2_smt", name: "statement", prose: "Manage {{ insert: param, ac-2_prm_1 }}." }] },
      { id: "ac-9", class: "SP800-53", title: "Old", props: [label("AC-9"), label("AC-09", "zero-padded"), { name: "sort-id", value: "ac-09" }, { name: "status", value: "withdrawn" }],
        links: [{ rel: "incorporated-into", href: "#ac-2_smt" }] },
      { id: "ac-8", class: "SP800-53", title: "Moved", props: [label("AC-8"), label("AC-08", "zero-padded"), { name: "sort-id", value: "ac-08" }, { name: "status", value: "withdrawn" }],
        links: [{ rel: "moved-to", href: "#ac" }] },
      { id: "ac-7", class: "SP800-53", title: "Gone", props: [label("AC-7"), { name: "sort-id", value: "ac-07" }, { name: "status", value: "withdrawn" }],
        parts: [{ id: "ac-7_smt", name: "statement", prose: "Addressed through tailoring." }] }] }] } };
};
const nistProfiles = () => Object.fromEntries(["LOW", "MODERATE", "HIGH", "PRIVACY"].map(b => [b, { profile: { uuid: "pr-" + b,
  metadata: { title: `NIST SP 800-53 test ${b} BASELINE`, "last-modified": "2026-05-11T16:01:09.00000-00:00", version: "9.9", "oscal-version": "1.1.2" },
  imports: [{ href: "#cat", "include-controls": [{ "with-ids": b === "PRIVACY" ? ["ac-2"] : ["ac-1", "ac-1.1", "ac-2"] }] }],
  merge: { "as-is": true } } }]));

/* The expectations were written from the code of convert_nist.py v0.2, and the next test holds every object to what the
   converter itself writes for this catalogue. */
test("NIST preset: the rules on a small catalog", () => {
  const P = "https://ns.nist.gov/sp800-53", src = nistSynthetic(), before = JSON.stringify(src);
  const out = oscal.jscOscalImportCatalog(src, { preset: "nist-sp800-53" });
  assert.equal(JSON.stringify(src), before, "the source is not changed by the import");
  const by = new Map(out.objects.map(o => [o.obj.id, o.obj]));
  assert.deepEqual([...by.keys()], [`${P}/req/AC-1`, `${P}/req/AC-1.1`, `${P}/req/AC-2`, `${P}/req/AC-7`, `${P}/set/family/ac`, `${P}/set/root`],
    "a withdrawn control that names a successor makes no Requirement; one that names none does");
  const ac1 = by.get(`${P}/req/AC-1`), ac2 = by.get(`${P}/req/AC-2`), ac7 = by.get(`${P}/req/AC-7`), fam = by.get(`${P}/set/family/ac`), root = by.get(`${P}/set/root`);
  assert.deepEqual(ac1.statements.map(s => s.id), ["smt.a", "smt.b"], "items with prose are the clauses, ids without the control prefix");
  assert.equal(ac1.statements[0].prose.en, "Review every {param:ac-1_prm_1} as [SP 800-12](#u1) says.", "inserts become tokens; a markdown link stays as the source wrote it");
  assert.deepEqual(ac1.statements[0]["obligated-parties"], [`${P}/party/system`]);
  assert.ok(ac1.statements.every(s => s.modality === "must"));
  /* a withdrawn control without a successor: lifecycle `withdrawn`, its statement states no obligation, and it binds the preset's party */
  assert.deepEqual([ac7.lifecycle, ac7.label, ac7.statements], ["withdrawn", "AC-7", [{ id: "smt", modality: "unspecified", "obligated-parties": [`${P}/party/organization`], prose: { en: "Addressed through tailoring." } }]]);
  assert.deepEqual(out.report["withdrawn-without-successor"], ["ac-7"]);
  assert.equal(out.report["controls-without-a-stated-party"], 1);
  /* declared where inserted; what no clause inserts goes to the first clause, sorted; a parameter of another control is declared where it is used */
  assert.deepEqual(ac1.statements[0].parameters, [{ name: "ac-1_prm_1", type: "string", label: "frequency" },
    { name: "ac-1_prm_2", type: "choice", choices: [{ value: "daily" }, { value: "per {param:ac-1_prm_1}" }], cardinality: "many" }, { name: "ac-1_prm_3", type: "string" }]);
  assert.deepEqual(ac1.statements[1].parameters, [{ name: "ac-2_prm_1", type: "string" }]);
  assert.deepEqual(out.report["parameters-from-another-control"], [["ac-1", "ac-2_prm_1"]]);
  assert.equal(out.report["parameters-without-insertion"], 2);
  /* once each; a link to a withdrawn control is a relation too (its URI is named in the successor's `replaces`); a reference
     to a resource without a link becomes no relation and is counted */
  assert.deepEqual(ac1.relations, [{ type: "related", ref: `${P}/req/AC-2` }, { type: "related", ref: `${P}/req/AC-9` }, { type: "reference", ref: "https://example.org/zeta" }]);
  assert.deepEqual(out.report["links-not-written"], { reference: 1 });
  assert.deepEqual(ac1.facets[`${P}/facet/narrative@1`], { guidance: [{ en: "See [AC-2](#ac-2)." }] });
  /* every objective names the statement it assesses: of its own control, the statement part as a whole, another control's */
  assert.deepEqual(ac1.facets[`${P}/facet/sp800-53a@1`], { objectives: [{ id: "ac-1_obj", label: "AC-01", "assessment-for": [{ "statement-id": "smt" }], children: [
      { id: "ac-1_obj.a", label: "AC-01a.", "assessment-for": [{ "statement-id": "smt.a" }], prose: { en: "the review happens;" } },
      { id: "ac-1_obj.b", label: "AC-01b.", "assessment-for": [{ "requirement-ref": `${P}/req/AC-2`, "statement-id": "smt" }], prose: { en: "the accounts are used;" } }] }],
    methods: [{ method: "EXAMINE", label: "AC-01-Examine", objects: [{ en: "Policy" }, { en: "Procedures for {param:ac-1_prm_3}" }] }] });
  assert.equal(out.report["assessment-for"], 3);
  /* the formal ODP label as the source gives it; a prop is read in its own class only */
  assert.deepEqual(ac1.facets[`${P}/facet/odp@1`], { params: { "ac-1_prm_1": { "sp800-53a-label": "AC-01_ODP[01]" }, "ac-1_prm_3": { "alt-identifiers": ["old-3"], "alt-label": "the third" } } });
  assert.deepEqual([ac1.facets[`${P}/facet/rmf@1`], by.get(`${P}/req/AC-1.1`).facets[`${P}/facet/rmf@1`]], [{ "contributes-to-assurance": false }, { "contributes-to-assurance": true }]);
  /* lineage: the successor names the withdrawn control with the label a reader sees (not the zero-padded one), a family names what moved to it */
  assert.deepEqual(ac2.replaces, [{ ref: `${P}/req/AC-9`, mode: "merged-into" }]);
  assert.deepEqual(ac2.annotations["nist-withdrawal"], [{ ref: `${P}/req/AC-9`, mode: "merged-into", label: "AC-9", title: "Old", into: "smt" }]);
  assert.deepEqual(fam.annotations["nist-withdrawal"], [{ ref: `${P}/req/AC-8`, mode: "renamed", label: "AC-8", title: "Moved" }]);
  assert.deepEqual(fam.members.map(m => [m.ref, m.sequence]), [[`${P}/req/AC-1`, 10], [`${P}/req/AC-1.1`, 20], [`${P}/req/AC-2`, 30], [`${P}/req/AC-7`, 40]], "members in the order of sort-id");
  assert.deepEqual(fam.facets[`${P}/facet/narrative@1`], { overview: [{ title: { en: "Access Control Overview" }, prose: { en: "About access, see [Zeta](#u1)." } }] });
  /* the root: the resources as the source writes them, in its order; what the document says of itself */
  assert.deepEqual(root.facets[`${P}/facet/references@1`].resources, src.catalog["back-matter"].resources);
  const { title, version, ...meta } = src.catalog.metadata;
  assert.deepEqual(root.facets["https://ns.jascon.net/compat/oscal-1x@1"], { metadata: meta });
  assert.deepEqual([out.provenance.sources[0]["author-ref"], out.provenance.sources[0].date], [`${P}/party/oscal-program`, "2026-05-11"]);
  assert.equal(out.report["withdrawn-not-converted"], 2);
  /* what comes out is valid kernel content: every object one type, references closed, facets under the pinned schemas */
  const objs = new Map();
  for (const o of out.objects) { const type = rules.jscTypeOf(o.obj); assert.ok(type, `${o.path}: ${rules.jscObjectErrors(o.obj).errors.join("; ")}`); objs.set(o.obj.id, { type, obj: o.obj }); }
  assert.deepEqual(rules.jscClosureErrors(objs), []);
  assert.deepEqual(rules.jscFacetErrors(out.objects.map(o => [o.obj.id, o.obj]), new Map(out.facetSchemas.map(f => [f.def.id, f.def.schema]))), []);
  assert.deepEqual(out.report["props-not-read"], {});
  /* a prop of a name the rules read, in another class or in another namespace, is another prop: it is not read, as
     convert_nist.py does not read it (its ledger then ends the run, measured 2026-11-14), and the report counts it */
  const other = nistSynthetic(), oac1 = other.catalog.groups[0].controls[0], oac2 = other.catalog.groups[0].controls[1];
  oac1.params[2].props.unshift({ name: "alt-label", class: "other", value: "not this one" }, { name: "alt-label", value: "nor this one" });
  oac2.props.push({ name: "implementation-level", value: "system" });
  const read = oscal.jscOscalImportCatalog(other, { preset: "nist-sp800-53" }), rby = new Map(read.objects.map(o => [o.obj.id, o.obj]));
  assert.deepEqual([rby.get(`${P}/req/AC-1`).facets[`${P}/facet/odp@1`].params["ac-1_prm_3"]["alt-label"], rby.get(`${P}/req/AC-2`).statements[0]["obligated-parties"]], ["the third", [`${P}/party/organization`]]);
  assert.deepEqual(read.report["props-not-read"], { "alt-label [other]": 1, "alt-label": 1, "implementation-level": 1 });
  /* a status the rules do not know is refused, as the converter refuses it */
  const odd = nistSynthetic();
  odd.catalog.groups[0].controls[1].props.push({ name: "status", value: "draft" });
  assert.throws(() => oscal.jscOscalImportCatalog(odd, { preset: "nist-sp800-53" }), /the status \["draft"\]; these rules know `withdrawn` only/);
});

/* convert_nist.py decides: it is run on the catalogue and the profiles above in a tree of its own, and every object the
   preset writes, the pinned schemas and the author and day of the catalogue are compared; so is what the profile import
   writes on a profile's Set with what the converter writes on a baseline Set. On this catalogue the converter writes its
   bundle and then ends with exit code 1 (measured 2026-11-14): a `reference` link to a back-matter resource without a
   link becomes no relation, and the converter's ledger finds its two values unaccounted. That is a finding about the
   converter, reported to the author; the preset counts the link in `links-not-written`. This test accepts that one
   failure and no other, and a run without it. */
test("NIST preset and profile import: on a catalogue of the SP 800-53 shape with what the preset used to lose, every object has the semantic digest and the bytes of convert_nist.py", { skip: !python && "python3 is not installed" }, async () => {
  const src = nistSynthetic(), profiles = nistProfiles(), tmp = fs.mkdtempSync(path.join(os.tmpdir(), "jascon-nist-"));
  try {
    fs.mkdirSync(path.join(tmp, "jascon/scripts"), { recursive: true });
    fs.mkdirSync(path.join(tmp, "sources/nist"), { recursive: true });
    for (const f of ["convert_nist.py", "oscal_conv_lib.py"]) fs.copyFileSync(path.join(ROOT, "jascon/scripts", f), path.join(tmp, "jascon/scripts", f));
    fs.cpSync(path.join(ROOT, "jascon/schemas"), path.join(tmp, "jascon/schemas"), { recursive: true });
    fs.writeFileSync(path.join(tmp, "sources/nist/NIST_SP-800-53_rev5_catalog.json"), JSON.stringify(src));
    for (const [b, p] of Object.entries(profiles)) fs.writeFileSync(path.join(tmp, `sources/nist/NIST_SP-800-53_rev5_${b}-baseline_profile.json`), JSON.stringify(p));
    const run = spawnSync("python3", [path.join(tmp, "jascon/scripts/convert_nist.py")], { cwd: tmp, encoding: "utf8" });
    const known = /^convert_nist\.py: the conversion ledger has 0 claim\(s\) that do not hold and 2 source value\(s\) unaccounted/m;
    const twoValues = (run.stderr.match(/^\s*unaccounted\s+1\s+nist\.catalog\.groups\[\]\.controls\[\]\.links\[\]\.(href|rel)\s+e\.g\. nist#\/catalog\/groups\/0\/controls\/0\/links\/4\//gm) || []).length;
    assert.ok(run.status === 0 || (run.status === 1 && known.test(run.stderr) && twoValues === 2), `the converter ran (exit ${run.status}): ${run.stderr.slice(-1500)}`);
    const dir = path.join(tmp, "converted_examples/US.SP800-53/sp800-53-core-bundle"), manifest = json(path.join(dir, "content-manifest.json"));
    const lf = f => fs.readFileSync(path.join(dir, f), "utf8").replace(/\r\n/g, "\n");
    const out = oscal.jscOscalImportCatalog(src, { preset: "nist-sp800-53" });
    const want = new Map(manifest.objects.map(e => [e.path, e]));
    assert.deepEqual(out.objects.map(o => o.path).sort(), [...want.keys()].filter(p => !/\/baseline-/.test(p)).sort(), "the same files, without the baseline Sets");
    assert.equal(out.objects.length, 6);
    for (const o of out.objects) {
      assert.equal(await core.jscSemanticDigest(o.obj), want.get(o.path)["semantic-digest"], o.path + " has the converter's meaning");
      assert.equal(core.jscSerialize(o.obj), lf(o.path), o.path + " has the converter's bytes, but for the line ends");
    }
    assert.deepEqual(out.facetSchemas.map(f => f.path).sort(), manifest["facet-schemas"].map(e => e.path).sort());
    for (const f of out.facetSchemas) assert.equal(core.jscSerialize(f.def), lf(f.path), f.path);
    assert.deepEqual([out.provenance.sources[0]["author-ref"], out.provenance.sources[0].date], [manifest.provenance["author-ref"], manifest.provenance.date]);
    /* a profile imported into the converter's bundle: its Set holds the members of the converter's baseline Set, in their
       order, and the same compat facet (the profile's metadata and merge); the bundle pins the schema, so none is brought */
    const objs = new Map(manifest.objects.map(e => { const o = json(path.join(dir, e.path)); return [o.id, { type: core.jscInferType(o), obj: o }]; }));
    const pins = manifest["facet-schemas"].map(e => json(path.join(dir, e.path)));
    for (const [b, prof] of Object.entries(profiles)) {
      const res = oscal.jscOscalImportProfile(prof, { ns: "https://org.example", lang: "en", objs, facetSchemas: pins });
      const set = res.objects.find(o => o.obj.members).obj, baseline = objs.get(`https://ns.nist.gov/sp800-53/set/baseline/${b.toLowerCase()}`).obj;
      assert.deepEqual([set.members.map(m => m.ref), set.facets, res.facetSchemas, res.report["not-carried"]], [baseline.members.map(m => m.ref), baseline.facets, [], {}], b);
    }
  } finally { fs.rmSync(tmp, { recursive: true, force: true }); }
});

/* CIS preset. The catalog (tests/cis-synthetic.mjs) is written in the shape
   of the CIS OSCAL export; its text is invented. The Python converter is run
   on it in a throwaway copy of the scripts, and every object the preset makes
   must carry the semantic digest the converter's manifest states.

   Until 2026-11-13 both wrote the catalog's version as the
   `provenance.date` of a Mapping, which kernel 2.0.0 refuses since it holds
   that field to a date (DATE-3; ERRATA.md). Both now write the day of the
   catalog's `last-modified`, and the digests agree without exception. */
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

/* ====================================================================
   Whom a statement binds where the source does not say (backlog #74)
   ====================================================================
   A preset for a publisher's corpus writes one party of its own where the
   source names none, as its converter does. Since build 0.9.12 that party
   is an argument with a named default: left alone, the import writes what
   it wrote before; the caller's party takes its place; without a party
   nothing is imported; and the report says who chose. */
const PARTY_INPUTS = [
  ["bsi-gspp", () => JSON.parse(fs.readFileSync(path.join(ROOT, "converted_examples/DE.BSI/oscal-export/de.bsi-catalog.json"), "utf8")), "https://ns.bsi.bund.de/gspp/party/institution", 1360, 999,
    "95174caef603f511189b10940775b441a03cc716edbf791312d85946273d43e7"],
  ["nist-sp800-53", () => JSON.parse(fs.readFileSync(path.join(ROOT, "converted_examples/US.SP800-53/oscal-export/us.sp800-53-catalog.json"), "utf8")), "https://ns.nist.gov/sp800-53/party/organization", 1037, 1920,
    "efb526aa6a76f2008051c0bec823b34b93f05844a3a1962a54dc25ca10b3a6da"],
  ["cis-benchmark", cisSynthetic, "https://ns.cisecurity.org/benchmark/ubuntu-24.04-lts/party/system-administrator", 17, 5,
    "5fd5ccda73af5232c225b0e9fb62e5cecc71c4f4948745dba13798f08280db92"],
];
/* every file an import would write: its path, a line break, the serialized object */
const filesOf = out => out.objects.map(o => o.path + "\n" + core.jscSerialize(o.obj)).join("\n");
const bound = out => { const n = {}; for (const o of out.objects) for (const st of o.obj.statements || []) for (const p of st["obligated-parties"]) n[p] = (n[p] || 0) + 1; return n; };

test("the obligated party of a preset: with the default left as it is, an import writes the bytes recorded for it (CIS: those of build 0.9.11; Grundschutz++: those of build 0.9.14; SP 800-53: those of build 0.9.15)", () => {
  /* One SHA-256 over every file an import writes. For CIS the digest was taken with build 0.9.11, before the presets
     knew the argument, and holds that the argument changed nothing. For SP 800-53 it is that of build 0.9.15, since
     2026-11-14, by the same decision of the author as for Grundschutz++ below: the preset follows convert_nist.py v0.2
     (a withdrawn control without a successor is a Requirement, every objective names the statement it assesses, the
     formal ODP labels, the document's metadata and the back-matter resources as the source writes them are carried,
     markdown links stay), and its input here, the OSCAL export the repository carries, was regenerated from the new
     bundle. Until then: 1,035 objects, 1,918 statements, SHA-256 59cfc430…e83a (build 0.9.11). Since: 1,037 objects
     (1,016 Requirements, 21 Sets), 1,920 statements. For Grundschutz++ the digest is that of build
     0.9.14, since 2026-11-14, by the author's decision of that day that the frozen digests give way to the new state.
     Two things changed at once: the preset follows convert_bsi.py v0.3 (every control a Requirement of its own, and
     what the mapping does not read carried in the compat facet), and its input here, the OSCAL export the repository
     carries, was regenerated from the new bundle. Until then: 811 objects, 651 statements, SHA-256 a297e3f6…16b8 (build
     0.9.11). Since: 1,360 objects (999 Requirements, 361 Sets: the export writes 360 groups), 999 statements. What is
     right for this preset is decided by the committed bundle, in the first tests of this file; this digest holds that
     the party argument leaves it alone. The CIS input is written for the tests. */
  for (const [preset, doc, def, objects, statements, digest] of PARTY_INPUTS) {
    const out = oscal.jscOscalImportCatalog(doc(), { preset });
    assert.equal(out.objects.length, objects, preset);
    assert.deepEqual(bound(out), { [def]: statements }, preset + ": every statement binds the preset's default");
    assert.equal(crypto.createHash("sha256").update(filesOf(out)).digest("hex"), digest, preset + ": the bytes recorded for this preset");
    assert.equal(filesOf(oscal.jscOscalImportCatalog(doc(), { preset, party: null })), filesOf(out), preset + ": null is not given");
    assert.deepEqual(out.report["obligated-party"], { value: def, origin: "converter-default", "converter-default": def,
      ...(preset === "nist-sp800-53" ? { "source-states": "as the implementation level of a control" } : {}) }, preset + ": the report says that nobody chose");
  }
});

test("the obligated party of a preset: the caller's party takes the default's place and nothing else changes; the report says who chose; without a party, or with one that is no http(s) URI, nothing is imported", () => {
  const MINE = "https://org.example/party/operator";
  for (const [preset, doc, def, , statements] of PARTY_INPUTS) {
    assert.deepEqual(oscal.jscOscalPartyDefault(doc(), { preset }).default, def, preset + ": the default can be asked for before anything is imported");
    const before = oscal.jscOscalImportCatalog(doc(), { preset }), mine = oscal.jscOscalImportCatalog(doc(), { preset, party: MINE });
    assert.deepEqual(bound(mine), { [MINE]: statements }, preset);
    /* only `obligated-parties` differs, in every file. Since build 0.9.14 the default is replaced there and nowhere
       else, where until then the test replaced it in the whole text: the OSCAL export of the Grundschutz++ bundle
       states the party in a prop of its own (999 times), and since that build the preset carries such a prop in the
       compat facet as the source holds it. Outside that facet the default stands nowhere once another party is given. */
    const rebound = { objects: before.objects.map(o => ({ path: o.path, obj: o.obj.statements
      ? { ...o.obj, statements: o.obj.statements.map(st => ({ ...st, "obligated-parties": st["obligated-parties"].map(x => (x === def ? MINE : x)) })) } : o.obj })) };
    assert.equal(filesOf(mine), filesOf(rebound), preset + ": only the party of the statements differs, in every file");
    const own = obj => { const facets = { ...(obj.facets || {}) }; delete facets["https://ns.jascon.net/compat/oscal-1x@1"]; return { ...obj, facets }; };
    assert.equal(mine.objects.map(o => JSON.stringify(own(o.obj))).join("\n").includes(JSON.stringify(def)), false, preset + ": the default is gone from everything the preset writes of its own");
    assert.deepEqual([mine.report["obligated-party"].value, mine.report["obligated-party"].origin, mine.report["obligated-party"]["converter-default"]], [MINE, "caller", def]);
    /* typed with blanks around it: the URI as typed, trimmed */
    assert.deepEqual(bound(oscal.jscOscalImportCatalog(doc(), { preset, party: `  ${MINE} ` })), { [MINE]: statements });
    /* the default typed out is the caller's choice of the same party: the same bytes, and the report says who chose */
    const typed = oscal.jscOscalImportCatalog(doc(), { preset, party: def });
    assert.deepEqual([filesOf(typed) === filesOf(before), typed.report["obligated-party"].origin], [true, "caller"]);
    /* no party, and a party that is none: the import does not run, and the default does not come back by itself */
    assert.throws(() => oscal.jscOscalImportCatalog(doc(), { preset, party: "" }), new RegExp("^Error: no party is named that the statements bind: the kernel requires obligated-parties on every statement\\. The preset's default is " + def.replace(/[.]/g, "\\.") + "$"), preset);
    assert.throws(() => oscal.jscOscalImportCatalog(doc(), { preset, party: "   " }), /no party is named that the statements bind/, preset);
    for (const bad of ["operator", "urn:example:operator", "https://org.example/party/the operator", "org.example/party/operator"]) {
      assert.throws(() => oscal.jscOscalImportCatalog(doc(), { preset, party: bad }), /is not an http\(s\) URI of a party\. The preset's default is /, `${preset}: ${bad}`);
    }
  }
  assert.equal(oscal.jscOscalPartyDefault(cisSynthetic(), { preset: "generic" }), null, "the generic rules have no default");
  assert.equal(oscal.jscOscalPartyDefault(cisSynthetic(), { preset: "cis-benchmark", ns: "https://example.org/cis" }).default, "https://example.org/cis/party/system-administrator", "a CIS namespace chosen on the page carries the default");
  /* the generic rules: the party is always the caller's, and the report says so in the same record */
  const generic = oscal.jscOscalImportCatalog(cisSynthetic(), { preset: "generic", ns: "https://org.example/fw/x", lang: "en", key: "x", party: "all staff" });
  assert.deepEqual(generic.report["obligated-party"], { value: "https://org.example/fw/x/party/all-staff", origin: "caller", "converter-default": null });
});

test("the obligated party of the NIST preset: a level the control states is the source's and stays, whatever the caller gives", () => {
  const rmf = "http://csrc.nist.gov/ns/rmf", NS = "https://ns.nist.gov/sp800-53", MINE = "https://org.example/party/operator";
  const control = (id, label, props) => ({ id, title: label, props: [{ name: "label", value: label }, { name: "sort-id", value: id }, ...props], parts: [{ id: id + "_smt", name: "statement", prose: "Do it." }] });
  const cat = () => ({ catalog: { metadata: { title: "Electronic (OSCAL) Version of NIST SP 800-53 Rev 5 test", version: "9.9", "oscal-version": "1.1.2" },
    groups: [{ id: "ac", title: "Access Control", controls: [
      control("ac-1", "AC-1", [{ name: "implementation-level", ns: rmf, value: "system" }, { name: "implementation-level", ns: rmf, value: "organization" }]),
      control("ac-2", "AC-2", [])] }] } });
  const parties = out => Object.fromEntries(out.objects.filter(o => o.obj.statements).map(o => [o.obj.id.split("/").pop(), o.obj.statements[0]["obligated-parties"]]));
  const byDefault = oscal.jscOscalImportCatalog(cat(), { preset: "nist-sp800-53" }), mine = oscal.jscOscalImportCatalog(cat(), { preset: "nist-sp800-53", party: MINE });
  assert.deepEqual(parties(byDefault), { "AC-1": [NS + "/party/system", NS + "/party/organization"], "AC-2": [NS + "/party/organization"] });
  assert.deepEqual(parties(mine), { "AC-1": [NS + "/party/system", NS + "/party/organization"], "AC-2": [MINE] }, "the caller's party stands only where the source names none");
  assert.deepEqual([byDefault.report["controls-without-a-stated-party"], mine.report["controls-without-a-stated-party"]], [1, 1]);
  assert.deepEqual(mine.report["obligated-party"], { value: MINE, origin: "caller", "converter-default": NS + "/party/organization", "source-states": "as the implementation level of a control" });
});
