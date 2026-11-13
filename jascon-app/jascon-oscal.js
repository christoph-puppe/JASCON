/* JASCON-App: importing OSCAL catalogs and profiles.

   An OSCAL catalog becomes Requirements and RequirementSets; an OSCAL
   profile becomes a RequirementSet (what it includes) and a Tailoring (what
   it excludes and sets). Everything after the import works on JASCON.

   Four ways to read a catalog, chosen by `preset`:

   bsi-gspp   The rules of jascon/scripts/convert_bsi.py for the BSI
              Anwenderkatalog Grundschutz++: a nested control is a clause of
              its parent, the modal verb becomes the modality, the BSI props
              go to stdlib and BSI facets, sec_level becomes baseline Sets.
              tests/oscal.test.mjs compares every object this preset makes
              with the shipped bundle converted_examples/DE.BSI.
   generic    For any other catalog. Every control, nested ones included, is
              a Requirement; every part of the statement that carries prose
              is a clause; the modality is `unspecified`, because OSCAL has
              no field for it; every prop and every other part is carried in
              a holding facet, verbatim, so nothing is dropped silently.
   nist-sp800-53  The rules of convert_nist.py for NIST SP 800-53 Rev 5:
              withdrawn controls folded into `replaces`, statement items as
              clauses, SP 800-53A objectives and methods, parameter data and
              guidance in facets. On the same source file its objects equal
              the Python converter's. It makes no baseline Sets; a baseline
              is a profile and is imported as one.
   cis-benchmark  The rules of convert_cis_benchmark.py for a CIS Benchmark:
              one Requirement per rule, audit and remediation text with the
              automated/manual marking in assessment-criteria@1 (what the
              Checks tool drafts checks from), profiles as baseline Sets,
              CIS Controls cross-references as Mappings.

   What an import cannot carry is counted in the report it returns, never
   dropped without a line: a control without statement prose, a relation
   whose target is unknown, a profile's alters, its merge directive, its
   pattern matching.

   Pure functions of plain data; runs in node. The Python converters are the
   reference for the BSI preset. */
"use strict";

const jscOscalCore = (typeof module !== "undefined" && module.exports) ? require("./jascon-core.js") : { jscSha256Js, jscUtf8 };
const jscOscalSchema = (typeof module !== "undefined" && module.exports) ? require("./jascon-schema.js") : { JSC_STDLIB };

/* The converters' slug: at most 60 characters, and a longer name is cut
   with a hash suffix instead of bare truncation, so that two long names
   never collapse into one id. */
function jscOscalSlug(s) {
  const t = String(s || "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
  if (t.length <= 60) return t || "x";
  return t.slice(0, 52).replace(/-+$/, "") + "-" + jscOscalCore.jscSha256Js(jscOscalCore.jscUtf8(t)).slice(0, 7);
}
const JSC_INSERT_RE = /\{\{\s*insert:\s*param,\s*([^}\s]+)\s*\}\}/g;
const jscOscalProse = prose => String(prose || "").replace(JSC_INSERT_RE, (m, id) => `{param:${id}}`);
const jscSplitList = v => String(v).split(",").map(x => x.trim()).filter(Boolean);
const JSC_BSI_SLOT = /\{\{(?!\s*insert:)(.*?)\}\}/;
const JSC_BSI_INSERT = "\\{\\{\\s*insert:\\s*param,\\s*[^}\\s]+\\s*\\}\\}";
const JSC_BSI_LIST_PROPS = ["tags", "threats", "target_object_categories", "documentation"];
const jscReEscape = s => String(s).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const jscPropMap = list => Object.fromEntries((list || []).map(p => [p.name, p.value]));
/* #uuid -> the URL (or, failing that, the title) of the back-matter resource */
function jscBackMatter(doc) {
  return new Map((((doc["back-matter"] || {}).resources) || []).map(r => [r.uuid, ((r.rlinks || [{}])[0] || {}).href || r.title || ""]));
}
/* A pinned facet schema with a closed shape, as the converters write it. */
function jscFacetStub(name, id, modifies, properties) {
  return { path: `schemas/${name}`, def: { id, version: "1.0.0", "modifies-semantics": modifies,
    note: "NORMATIVE pinned payload schema (backlog #26): closed shape - unknown keys are rejected, never smuggled",
    schema: { $schema: "https://json-schema.org/draft/2020-12/schema", type: "object", properties, additionalProperties: false } } };
}
function jscStdlibPin(shortName) {
  const def = jscOscalSchema.JSC_STDLIB.find(d => d.id.endsWith("/" + shortName));
  if (!def) throw new Error(`stdlib facet ${shortName} is not in jascon-schema.js`);
  return { path: `schemas/${shortName}-${def.version}.json`, def };
}

/* ====================================================================
   BSI Grundschutz++ (after convert_bsi.py v0.2)
   ==================================================================== */
const JSC_BSI = {
  ns: "https://ns.bsi.bund.de/gspp", key: "gspp", lang: "de",
  F_GRAM: "https://ns.jascon.net/stdlib/facet/statement-grammar@1", F_SECO: "https://ns.jascon.net/stdlib/facet/security-objectives@1",
  F_ACRIT: "https://ns.jascon.net/stdlib/facet/assessment-criteria@1", F_TAX: "https://ns.bsi.bund.de/facet/gspp-taxonomy@1",
  F_NARR: "https://ns.bsi.bund.de/facet/gspp-narrative@1", F_COMPAT: "https://ns.jascon.net/compat/oscal-1x@1",
  MODAL: { "MUSS": "must", "SOLLTE": "should", "KANN": "may", "DARF NICHT": "must-not", "SOLLTE NICHT": "should-not", "DARF NUR": "may-only",
    "MÜSSEN": "must", "SOLLTEN": "should", "KÖNNEN": "may", "DÜRFEN NICHT": "must-not", "DÜRFEN NUR": "may-only" },
};
function jscImportBsi(cat) {
  const B = JSC_BSI, ns = B.ns, version = cat.metadata.version, lang = B.lang;
  const objects = [], bm = jscBackMatter(cat), secValues = new Set(), baseline = new Map();
  const report = { preset: "bsi-gspp", controls: 0, statements: 0, "packed-list-values": [], "parameter-slots": 0, "parameter-slots-not-at-insert": [], "unknown-modal-verbs": {}, "parameters-unreferenced": 0 };
  let seq = 0;
  const nseq = () => (seq += 10);
  /* one statement, and its facet payloads keyed by the statement id, from control c */
  const statement = (c, sid, isChild, req) => {
    const parts = c.parts || [], smt = parts.find(p => p.name === "statement") || {}, guid = parts.find(p => p.name === "guidance");
    const text = jscOscalProse(smt.prose), pp = jscPropMap(smt.props), cp = jscPropMap(c.props);
    /* {{Label}} in a sentence-template prop marks a parameter: it must stand
       where the prose inserts one (convert_bsi.py, slot_at_insert) */
    for (const part of parts) for (const p of part.props || []) {
      const v = String(p.value || ""), texts = v.split(JSC_BSI_SLOT).filter((_, i) => i % 2 === 0);
      if (texts.length < 2) continue;
      report["parameter-slots"] += texts.length - 1;
      if (!new RegExp(texts.map(jscReEscape).join(JSC_BSI_INSERT)).test(smt.prose || "")) report["parameter-slots-not-at-insert"].push({ control: c.id, prop: p.name, value: v });
    }
    /* a list of vocabulary terms joined by commas into one value, where OSCAL
       repeats the prop once per term: split below, reported here */
    for (const p of [...(smt.props || []), ...(c.props || [])]) {
      if (JSC_BSI_LIST_PROPS.includes(p.name) && jscSplitList(p.value).length > 1) report["packed-list-values"].push({ control: c.id, prop: p.name, value: p.value });
    }
    const mv = pp.modal_verb;
    if (mv !== undefined && !(mv in B.MODAL)) report["unknown-modal-verbs"][mv] = (report["unknown-modal-verbs"][mv] || 0) + 1;
    const st = { id: sid, modality: B.MODAL[mv] || "unspecified", "obligated-parties": [`${ns}/party/institution`], prose: { [lang]: text } };
    for (const pm of c.params || []) {
      const prm = { name: pm.id, type: "string" };
      if (pm.label) prm.label = pm.label;
      if ((pm.values || []).length) prm.default = pm.values[0];
      (st.parameters = st.parameters || []).push(prm);
      if (!text.includes(`{param:${pm.id}}`)) report["parameters-unreferenced"]++;
      const alt = (pm.props || []).find(x => x.name === "alt-identifier");
      if (alt) (req._compat = req._compat || {})[pm.id] = { "alt-identifier": alt.value };
    }
    /* the payload of facet f for this statement, created on first use; the
       converter creates the grammar and taxonomy payloads for every
       statement, also when they stay empty */
    const by = f => {
      const facet = (req.facets[f] = req.facets[f] || {});
      const perStatement = (facet["by-statement"] = facet["by-statement"] || {});
      return (perStatement[sid] = perStatement[sid] || {});
    };
    const g = by(B.F_GRAM);
    for (const [src, dst] of [["action_word", "action"], ["result", "result"], ["result_specification", "result-specification"]]) if (src in pp) g[dst] = pp[src];
    if ("target_object_categories" in pp) g["target-object-categories"] = jscSplitList(pp.target_object_categories);
    if ("documentation" in pp) by(B.F_ACRIT)["required-documentation"] = jscSplitList(pp.documentation);
    const so = {};
    for (const k of ["confidentiality", "integrity", "availability", "authenticity"]) if (k in cp) so[k] = cp[k];
    if ("threats" in cp) so["threat-refs"] = jscSplitList(cp.threats).map(t => `${ns}/threat/${t.replace(/ /g, "-")}`);
    if (Object.keys(so).length) Object.assign(by(B.F_SECO), so);
    const tx = by(B.F_TAX);
    tx.class = c.class === undefined ? null : c.class;
    if ("sec_level" in cp) { tx["sec-level"] = cp.sec_level; secValues.add(cp.sec_level); }
    if ("effort_level" in cp) tx.effort = parseInt(cp.effort_level, 10);
    if ("tags" in cp) tx.tags = jscSplitList(cp.tags);
    if ("practice" in pp) tx.practice = pp.practice;
    if (isChild) {
      tx.title = c.title === undefined ? null : c.title;
      if ("alt-identifier" in cp) tx["alt-identifier"] = cp["alt-identifier"];
      if ("label" in cp) tx.label = cp.label;
    }
    if (guid && guid.prose) by(B.F_NARR).guidance = { [lang]: guid.prose };
    report.statements++;
    return st;
  };
  const requirement = c => {
    const cp = jscPropMap(c.props);
    const req = { id: `${ns}/req/${c.id}`, version, label: cp.label !== undefined ? cp.label : c.id, lifecycle: "active", title: { [lang]: c.title }, statements: [], facets: {} };
    if ("alt-identifier" in cp) req.aliases = [{ scheme: "bsi-uuid", value: cp["alt-identifier"] }];
    req.statements.push(statement(c, "smt", false, req));
    const descend = node => { for (const ch of node.controls || []) { req.statements.push(statement(ch, ch.id, true, req)); descend(ch); } };
    descend(c);
    const rels = (c.links || []).map(l => {
      const href = l.href || "", type = l.rel || "related";
      if (href.startsWith("#") && bm.has(href.slice(1))) return { type, ref: bm.get(href.slice(1)) };
      return { type, ref: href.startsWith("#") ? `${ns}/req/${href.slice(1)}` : href };
    });
    if (rels.length) req.relations = rels;
    if (req._compat) req.facets[B.F_COMPAT] = { "param-extras": req._compat };
    delete req._compat;
    if (!Object.keys(req.facets).length) delete req.facets;
    report.controls++;
    return req;
  };
  /* the order of the nseq() calls is the converter's: a subgroup's whole
     subtree is numbered before the subgroup itself gets its place */
  const group = (g, pathIds) => {
    const entries = [];
    for (const sub of g.groups || []) {
      const u = group(sub, [...pathIds, jscOscalSlug(sub.id || sub.title)]);
      if (u) entries.push({ ref: u, sequence: nseq() });
    }
    for (const c of g.controls || []) {
      const req = requirement(c), cp = jscPropMap(c.props);
      objects.push({ path: `objects/${B.key}/req-${jscOscalSlug(c.id)}.json`, obj: req });
      if ("sec_level" in cp) baseline.set(cp.sec_level, [...(baseline.get(cp.sec_level) || []), req.id]);
      entries.push({ ref: req.id, sequence: nseq() });
    }
    if (!entries.length) return null;
    const sid = g.id || pathIds.join("-"), id = `${ns}/set/tax/${jscOscalSlug(sid)}`;
    const set = { id, version, lifecycle: "active", title: { [lang]: g.title !== undefined ? g.title : sid }, members: entries };
    for (const gp of g.props || []) {
      if (gp.name === "label") {
        set.label = gp.value;
        if (gp.remarks) ((set.facets = set.facets || {})[B.F_NARR] = set.facets[B.F_NARR] || {}).description = { [lang]: gp.remarks };
      } else if (gp.name === "alt-identifier") (set.aliases = set.aliases || []).push({ scheme: "bsi-uuid", value: gp.value });
    }
    objects.push({ path: `objects/${B.key}/set-tax-${jscOscalSlug(sid)}.json`, obj: set });
    return id;
  };
  const top = [];
  for (const g of cat.groups || []) {
    const u = group(g, [jscOscalSlug(g.id || g.title)]);
    if (u) top.push({ ref: u, sequence: nseq() });
  }
  objects.push({ path: `objects/${B.key}/set-tax-root.json`, obj: { id: `${ns}/set/tax/root`, version, lifecycle: "active", title: { [lang]: cat.metadata.title }, members: top } });
  for (const lvl of [...baseline.keys()].sort()) {
    objects.push({ path: `objects/${B.key}/set-baseline-${jscOscalSlug(lvl)}.json`, obj: { id: `${ns}/set/baseline/${jscOscalSlug(lvl)}`, version, lifecycle: "active",
      title: { [lang]: `Baseline sec_level: ${lvl}` }, members: baseline.get(lvl).map((ref, i) => ({ ref, sequence: (i + 1) * 10 })) } });
  }
  const facetSchemas = [
    jscFacetStub("gspp-taxonomy-1.0.0-stub.json", "https://ns.bsi.bund.de/facet/gspp-taxonomy", ["selection"],
      { "by-statement": { type: "object" }, "observed-sec-levels": { enum: [...secValues].sort() } }),
    jscStdlibPin("statement-grammar"), jscStdlibPin("security-objectives"), jscStdlibPin("assessment-criteria"),
    jscFacetStub("gspp-narrative-1.0.0-stub.json", "https://ns.bsi.bund.de/facet/gspp-narrative", [], { "by-statement": { type: "object" }, description: { type: "object" } }),
    jscFacetStub("oscal-1x-compat-1.0.0-stub.json", "https://ns.jascon.net/compat/oscal-1x", [], { "param-extras": { type: "object" } }),
  ];
  const provenance = { sources: [{ key: B.key, title: cat.metadata.title, version, "oscal-version": cat.metadata["oscal-version"] }],
    converter: "JASCON-App OSCAL import, preset bsi-gspp (the rules of convert_bsi.py v0.2)" };
  return { objects, facetSchemas, provenance, report };
}

/* ====================================================================
   NIST SP 800-53 Rev 5 (after convert_nist.py v0.1)
   ====================================================================
   Families become Sets under one root Set. A live control or enhancement
   becomes a Requirement: its statement and every item below it that has
   prose becomes one statement, modality `must` by the corpus rule, bound to
   the parties its implementation-level props name. A parameter is declared
   on the statement whose prose inserts it; one that no statement inserts is
   declared on the first. Guidance, the SP 800-53A objectives and methods,
   the administrative data of parameters and the RMF marker go into facets.
   A withdrawn control is not converted; its successor names it in
   `replaces`, with the withdrawn label and title kept as an annotation.

   The baselines are profiles of their own and are imported as profiles;
   this preset makes no baseline Set. */
const JSC_NIST = { ns: "https://ns.nist.gov/sp800-53", key: "sp800-53", lang: "en", rmf: "http://csrc.nist.gov/ns/rmf" };
function jscImportNist(cat) {
  const NS = JSC_NIST.ns, version = cat.metadata.version;
  const F = { narr: `${NS}/facet/narrative@1`, a: `${NS}/facet/sp800-53a@1`, odp: `${NS}/facet/odp@1`, rmf: `${NS}/facet/rmf@1`, ref: `${NS}/facet/references@1` };
  const T = v => ({ en: v });
  const props = (c, name, ns, cls) => (c.props || []).filter(p => p.name === name && (ns === undefined || p.ns === ns) && (cls === undefined || p.class === cls)).map(p => p.value);
  const prop = (c, name, ns, cls) => { const v = props(c, name, ns, cls); return v.length ? v[0] : null; };
  const mint = id => `${NS}/req/${String(id).toUpperCase()}`;
  /* {{ insert: param, x }} -> {param:x}; a markdown link to an anchor -> its text */
  const rewrite = (prose, used) => String(prose || "")
    .replace(/\{\{\s*insert:\s*param,\s*([a-z0-9._-]+)\s*\}\}/g, (m, id) => { if (used) used.add(id); return `{param:${id}}`; })
    .replace(/\[([^\]]+)\]\(#[a-zA-Z0-9._-]+\)/g, "$1");
  const byCode = (a, b) => (a < b ? -1 : a > b ? 1 : 0);
  const report = { preset: "nist-sp800-53", controls: 0, statements: 0, "withdrawn-not-converted": 0, "parameters-from-another-control": [],
    "parameters-without-insertion": 0, "related-to-withdrawn-or-missing": 0, "references-unresolved": 0, "withdrawn-into-withdrawn": [], "withdrawn-target-missing": [] };

  const res = new Map((((cat["back-matter"] || {}).resources) || []).map(r => [r.uuid,
    { title: r.title || "", citation: (r.citation || {}).text || "", url: ((r.rlinks || [{}])[0] || {}).href || "" }]));
  /* every control at any depth, with the top group it stands under */
  const controls = [];
  const walkControl = (c, top) => { controls.push({ c, top }); for (const s of c.controls || []) walkControl(s, top); };
  const walkGroup = (g, top) => { for (const c of g.controls || []) walkControl(c, top || g); for (const s of g.groups || []) walkGroup(s, top || g); };
  for (const g of cat.groups || []) walkGroup(g, null);
  for (const c of cat.controls || []) walkControl(c, null);
  const byId = new Map(controls.map(x => [x.c.id, x.c]));
  const withdrawn = new Set(controls.filter(x => prop(x.c, "status") === "withdrawn").map(x => x.c.id));
  const live = controls.filter(x => !withdrawn.has(x.c.id));
  const groupsById = new Map((cat.groups || []).map(g => [g.id, g]));
  const paramsGlobal = new Map(controls.flatMap(x => (x.c.params || []).map(pm => [pm.id, pm])));
  report["withdrawn-not-converted"] = withdrawn.size;

  /* a withdrawn control points at its successor; the kernel records it on the successor */
  const MODE = { "incorporated-into": "merged-into", "moved-to": "renamed" };
  const succ = new Map(), famSucc = new Map();
  const push = (map, key, e) => map.set(key, [...(map.get(key) || []), e]);
  for (const { c } of controls) {
    if (!withdrawn.has(c.id)) continue;
    for (const l of c.links || []) {
      const href = String(l.href || "").replace(/^#+/, "");
      if (!(l.rel in MODE)) continue;
      let target = href, into = null;
      if (href.includes("_smt")) { const at = href.indexOf("_smt"); target = href.slice(0, at); into = "smt" + href.split("_smt")[1]; }   // a statement of the successor
      const e = { ref: mint(c.id), mode: MODE[l.rel], label: prop(c, "label") || c.id.toUpperCase(), title: c.title || "" };
      if (into) e.into = into;
      if (withdrawn.has(target)) report["withdrawn-into-withdrawn"].push([c.id, target]);
      else if (byId.has(target)) push(succ, target, e);
      else if (groupsById.has(target)) push(famSucc, target, e);   // moved to a whole family
      else report["withdrawn-target-missing"].push([c.id, href]);
    }
  }
  const lineage = (o, entries) => {
    o.replaces = entries.map(e => ({ ref: e.ref, mode: e.mode }));
    o.annotations = { "nist-withdrawal": entries.map(e => Object.fromEntries(Object.entries(e).filter(([k]) => ["ref", "label", "title", "into", "mode"].includes(k)))) };
  };
  const paramDecl = pm => {
    const d = { name: pm.id };
    if ("select" in pm) {
      d.type = "choice";
      d.choices = ((pm.select || {}).choice || []).map(ch => ({ value: rewrite(ch) }));
      if ((pm.select || {})["how-many"] === "one-or-more") d.cardinality = "many";
    } else d.type = "string";
    if (pm.label) d.label = pm.label;
    return d;
  };
  const objTree = (pt, used) => {
    const node = {};
    if (pt.id) node.id = pt.id;
    const lab = prop(pt, "label", undefined, "sp800-53a");
    if (lab) node.label = lab;
    if (pt.prose) node.prose = T(rewrite(pt.prose, used));
    const kids = (pt.parts || []).map(s => objTree(s, used));
    if (kids.length) node.children = kids;
    return node;
  };
  const methodsOf = (c, used) => (c.parts || []).filter(pt => pt.name === "assessment-method").map(pt => {
    const m = { method: prop(pt, "method"), label: prop(pt, "label", undefined, "sp800-53a") };
    const objs = (pt.parts || []).filter(s => s.name === "assessment-objects").map(s => s.prose || "");
    if (objs.length) m.objects = objs[0].split(/\n\s*\n/).filter(x => x.trim()).map(x => T(rewrite(x.trim(), used)));
    return Object.fromEntries(Object.entries(m).filter(([, v]) => (Array.isArray(v) ? v.length : v)));
  });
  /* the statement part and every part below it that has prose, in document order */
  const flatStatements = c => {
    const out = [], walk = pt => { if (pt.prose) out.push(pt); for (const s of pt.parts || []) walk(s); };
    for (const pt of c.parts || []) if (pt.name === "statement") walk(pt);
    return out;
  };

  const objects = [];
  for (const { c } of live) {
    const cid = c.id, params = new Map((c.params || []).map(pm => [pm.id, pm]));
    const plain = ((c.props || []).find(p => p.name === "label" && !p.class) || { value: cid.toUpperCase() }).value;
    let levels = props(c, "implementation-level", JSC_NIST.rmf);
    if (!levels.length) levels = ["organization"];
    const parties = levels.map(v => `${NS}/party/${v}`), stmts = [], declared = new Set();
    for (const pt of flatStatements(c)) {
      const used = new Set(), prose = rewrite(pt.prose, used);
      let sid = pt.id === undefined ? `${cid}_smt` : pt.id;
      if (sid.startsWith(cid + "_")) sid = sid.slice(cid.length + 1);
      const s = { id: sid, modality: "must", "obligated-parties": parties, prose: { en: prose } }, decls = [];
      for (const u of [...used].sort(byCode)) {
        if (params.has(u)) decls.push(paramDecl(params.get(u)));
        else if (paramsGlobal.has(u)) { decls.push(paramDecl(paramsGlobal.get(u))); report["parameters-from-another-control"].push([cid, u]); }   // the source inserts another control's parameter
      }
      if (decls.length) s.parameters = decls;
      used.forEach(u => declared.add(u));
      stmts.push(s);
    }
    const rest = [...params.keys()].filter(pid => !declared.has(pid));
    if (rest.length && stmts.length) {
      stmts[0].parameters = [...(stmts[0].parameters || []), ...[...rest].sort(byCode).map(p => paramDecl(params.get(p)))];
      report["parameters-without-insertion"] += rest.length;
    }
    const req = { id: mint(cid), version, label: plain, lifecycle: "active", title: T(c.title === undefined ? cid : c.title), statements: stmts };
    const facets = {};
    const guidance = (c.parts || []).filter(p => p.name === "guidance" && p.prose).map(p => T(rewrite(p.prose)));
    if (guidance.length) facets[F.narr] = { guidance };
    const usedF = new Set();
    const objectives = (c.parts || []).filter(p => p.name === "assessment-objective").map(p => objTree(p, usedF)), methods = methodsOf(c, usedF);
    if (objectives.length || methods.length) facets[F.a] = { ...(objectives.length ? { objectives } : {}), ...(methods.length ? { methods } : {}) };
    const admin = {};
    for (const [pid, pm] of params) {
      const a = {}, pv = name => (pm.props || []).filter(p => p.name === name).map(p => p.value);
      if ((pm.guidelines || []).length) a.guidelines = pm.guidelines.map(g => T(rewrite(g.prose || "")));
      if (pv("alt-identifier").length) a["alt-identifiers"] = pv("alt-identifier");
      if (pv("alt-label")[0]) a["alt-label"] = pv("alt-label")[0];
      if (pv("aggregates").length) a.aggregates = pv("aggregates");
      if (Object.keys(a).length) admin[pid] = a;
    }
    if (Object.keys(admin).length) facets[F.odp] = { params: admin };
    if (prop(c, "contributes-to-assurance", JSC_NIST.rmf) === "true") facets[F.rmf] = { "contributes-to-assurance": true };
    if (Object.keys(facets).length) req.facets = facets;
    const rels = [], seen = new Set();
    const rel = (type, ref) => { if (!seen.has(type + "\n" + ref)) { seen.add(type + "\n" + ref); rels.push({ type, ref }); } };
    for (const l of c.links || []) {
      const href = String(l.href || "").replace(/^#+/, "");
      if (l.rel === "related" && byId.has(href) && !withdrawn.has(href)) rel("related", mint(href));
      else if (l.rel === "related") report["related-to-withdrawn-or-missing"]++;
      else if (l.rel === "required" && byId.has(href)) rel("required", mint(href));
      else if (l.rel === "reference" && res.has(href) && res.get(href).url) rel("reference", res.get(href).url);
      else if (l.rel === "reference") report["references-unresolved"]++;
    }
    if (rels.length) req.relations = rels;
    if (succ.has(cid)) lineage(req, succ.get(cid));
    objects.push({ path: `objects/req/${jscOscalSlug(cid)}.json`, obj: req });
    report.controls++; report.statements += stmts.length;
  }

  const rootMembers = [];
  for (const g of cat.groups || []) {
    const sortId = id => prop(byId.get(id), "sort-id") || id;
    const fam = live.filter(x => x.top && x.top.id === g.id).map(x => x.c.id).sort((a, b) => byCode(sortId(a), sortId(b)));
    const id = `${NS}/set/family/${g.id}`;
    const set = { id, version, lifecycle: "active", title: T(g.title === undefined ? g.id : g.title), label: prop(g, "label") || g.id.toUpperCase(),
      members: fam.map((cid, i) => ({ ref: mint(cid), sequence: (i + 1) * 10 })) };
    const overview = (g.parts || []).filter(p => p.name === "overview");
    if (overview.length) set.facets = { [F.narr]: { guidance: overview.map(p => T(rewrite(p.prose || ""))) } };
    if (famSucc.has(g.id)) lineage(set, famSucc.get(g.id));
    objects.push({ path: `objects/set/family-${jscOscalSlug(g.id)}.json`, obj: set });
    rootMembers.push({ ref: id, sequence: rootMembers.length * 10 + 10 });
  }
  const resources = [...res.values()].sort((a, b) => byCode(a.title, b.title)).map(r => Object.fromEntries(Object.entries(r).filter(([, v]) => v)));
  objects.push({ path: "objects/set/root.json", obj: { id: `${NS}/set/root`, version, lifecycle: "active", title: T(cat.metadata.title), members: rootMembers,
    facets: { [F.ref]: { resources } } } });

  const base = f => f.replace(/@1$/, "");
  const facetSchemas = [
    jscFacetStub("sp800-53-narrative-stub.json", base(F.narr), [], { guidance: { type: "array" } }),
    jscFacetStub("sp800-53a-stub.json", base(F.a), [], { objectives: { type: "array" }, methods: { type: "array" } }),
    jscFacetStub("sp800-53-odp-stub.json", base(F.odp), [], { params: { type: "object" } }),
    jscFacetStub("sp800-53-rmf-stub.json", base(F.rmf), [], { "contributes-to-assurance": { type: "boolean" } }),
    jscFacetStub("sp800-53-references-stub.json", base(F.ref), [], { resources: { type: "array" } }),
  ];
  const provenance = { sources: [{ key: JSC_NIST.key, title: cat.metadata.title, version, "oscal-version": cat.metadata["oscal-version"] }],
    converter: "JASCON-App OSCAL import, preset nist-sp800-53 (the rules of convert_nist.py v0.1, without the baseline Sets)",
    "namespace-note": "https://ns.nist.gov/sp800-53 is minted to match the mapping endpoints of the corpus; pending a URI published by NIST" };
  return { objects, facetSchemas, provenance, report };
}

/* ====================================================================
   Any other catalog
   ==================================================================== */
/* opts: { ns, lang, key } - the namespace the ids are minted under, the
   language of the catalog's prose, and a short name for the paths. */
function jscImportGeneric(cat, opts) {
  const ns = String(opts.ns).replace(/\/+$/, ""), lang = opts.lang || "en", key = jscOscalSlug(opts.key || "catalog");
  const version = String(cat.metadata.version || "1"), bm = jscBackMatter(cat), objects = [];
  const F_HOLD = `${ns}/facet/oscal-import@1`, KNOWN_REL = ["related", "required", "uses-term", "reference", "schema"];
  const report = { preset: "generic", controls: 0, statements: 0, "controls-without-prose": [], "props-held": {}, "parts-held": {},
    "relations-with-minted-type": {}, "parameters-unreferenced": 0, "links-without-target": 0 };
  const controlIds = new Set();
  const walkIds = node => { for (const c of node.controls || []) { controlIds.add(c.id); walkIds(c); } for (const g of node.groups || []) walkIds(g); };
  walkIds(cat);
  let seq = 0;
  const nseq = () => (seq += 10);
  const count = (map, k) => { map[k] = (map[k] || 0) + 1; };
  const paramOf = pm => {
    const prm = { name: pm.id, type: "string" };
    if (pm.label) prm.label = pm.label;
    if (pm.select && (pm.select.choice || []).length) {
      prm.type = "choice"; prm.choices = pm.select.choice.map(v => ({ value: jscOscalProse(v) }));
      if (pm.select["how-many"] === "one-or-more") prm.cardinality = "many";
    } else if ((pm.values || []).length) prm.default = pm.values[0];
    return prm;
  };
  const requirement = (c, parentId) => {
    const id = `${ns}/req/${c.id}`, cp = jscPropMap(c.props), params = new Map((c.params || []).map(pm => [pm.id, pm]));
    const req = { id, version, label: cp.label !== undefined ? String(cp.label) : c.id, lifecycle: "active", statements: [] };
    if (c.title) req.title = { [lang]: c.title };
    /* every part of the statement tree that carries prose is a clause */
    const clauses = [];
    const collect = part => {
      if (part.prose) clauses.push({ id: part.id && part.id.startsWith(c.id + "_") ? part.id.slice(c.id.length + 1) : (part.id || `s${clauses.length + 1}`), prose: jscOscalProse(part.prose) });
      for (const sub of part.parts || []) collect(sub);
    };
    (c.parts || []).filter(p => p.name === "statement").forEach(collect);
    if (!clauses.length) {
      /* a clause needs prose; a control without any is carried with its title and named in the report */
      clauses.push({ id: "smt", prose: c.title || c.id });
      report["controls-without-prose"].push(c.id);
    }
    const used = new Set(), seen = new Set();
    for (const cl of clauses) {
      let sid = cl.id;
      for (let n = 2; seen.has(sid); n++) sid = `${cl.id}-${n}`;
      seen.add(sid);
      const st = { id: sid, modality: "unspecified", "obligated-parties": [`${ns}/party/organization`], prose: { [lang]: cl.prose } };
      const tokens = [...new Set([...cl.prose.matchAll(/\{param:([^}]+)\}/g)].map(m => m[1]))];
      const declared = tokens.map(t => { used.add(t); return params.has(t) ? paramOf(params.get(t)) : { name: t, type: "string" }; });   // every token is declared (prose-params-resolve)
      if (declared.length) st.parameters = declared;
      req.statements.push(st);
    }
    const unused = [...params.keys()].filter(pid => !used.has(pid));   // a parameter no clause names is kept on the first clause
    if (unused.length) {
      report["parameters-unreferenced"] += unused.length;
      req.statements[0].parameters = [...(req.statements[0].parameters || []), ...unused.map(pid => paramOf(params.get(pid)))];
    }
    report.statements += req.statements.length;
    const rels = [];
    if (parentId) rels.push({ type: `${ns}/relation/enhancement-of`, ref: parentId });
    for (const l of c.links || []) {
      const href = l.href || "", rel = l.rel || "related";
      let type = rel;
      if (!KNOWN_REL.includes(rel)) { type = `${ns}/relation/${jscOscalSlug(rel)}`; count(report["relations-with-minted-type"], rel); }
      const ref = href.startsWith("#") ? (bm.has(href.slice(1)) ? bm.get(href.slice(1)) : controlIds.has(href.slice(1)) ? `${ns}/req/${href.slice(1)}` : "") : href;
      if (ref) rels.push({ type, ref }); else report["links-without-target"]++;
    }
    if (rels.length) req.relations = rels;
    /* what the kernel has no field for is held verbatim, not dropped */
    const held = {};
    const props = (c.props || []).filter(p => p.name !== "label");
    if (props.length) { held.props = props; props.forEach(p => count(report["props-held"], p.name)); }
    const otherParts = (c.parts || []).filter(p => p.name !== "statement");
    if (otherParts.length) { held.parts = otherParts; otherParts.forEach(p => count(report["parts-held"], p.name)); }
    if (c.class) held.class = c.class;
    if (Object.keys(held).length) req.facets = { [F_HOLD]: held };
    report.controls++;
    return req;
  };
  const emit = (c, parentId, entries) => {
    const req = requirement(c, parentId);
    objects.push({ path: `objects/${key}/req-${jscOscalSlug(c.id)}.json`, obj: req });
    entries.push({ ref: req.id, sequence: nseq() });
    for (const ch of c.controls || []) emit(ch, req.id, entries);
  };
  const group = (g, pathIds) => {
    const entries = [];
    for (const sub of g.groups || []) { const u = group(sub, [...pathIds, jscOscalSlug(sub.id || sub.title)]); if (u) entries.push({ ref: u, sequence: nseq() }); }
    for (const c of g.controls || []) emit(c, null, entries);
    if (!entries.length) return null;
    const sid = g.id || pathIds.join("-"), id = `${ns}/set/tax/${jscOscalSlug(sid)}`;
    const set = { id, version, lifecycle: "active", title: { [lang]: g.title || sid }, members: entries };
    const label = (g.props || []).find(p => p.name === "label");
    if (label) set.label = String(label.value);
    objects.push({ path: `objects/${key}/set-tax-${jscOscalSlug(sid)}.json`, obj: set });
    return id;
  };
  const top = [];
  for (const g of cat.groups || []) { const u = group(g, [jscOscalSlug(g.id || g.title)]); if (u) top.push({ ref: u, sequence: nseq() }); }
  for (const c of cat.controls || []) emit(c, null, top);   // controls outside any group
  objects.push({ path: `objects/${key}/set-tax-root.json`, obj: { id: `${ns}/set/tax/root`, version, lifecycle: "active", title: { [lang]: cat.metadata.title || key }, members: top } });
  const anyHeld = objects.some(o => o.obj.facets);
  const facetSchemas = anyHeld ? [jscFacetStub(`${key}-oscal-import-1.0.0.json`, `${ns}/facet/oscal-import`, [],
    { props: { type: "array" }, parts: { type: "array" }, class: { type: "string" } })] : [];
  const provenance = { sources: [{ key, title: cat.metadata.title, version, "oscal-version": cat.metadata["oscal-version"] }],
    converter: "JASCON-App OSCAL import, generic rules", "namespace-note": `${ns} was chosen at import; it is not the publisher's` };
  return { objects, facetSchemas, provenance, report };
}

/* ====================================================================
   CIS Benchmark (after convert_cis_benchmark.py v0.1)
   ====================================================================
   One hardening rule becomes one Requirement with one clause: the CIS
   export leaves the statement part empty and carries the norm in the title,
   so the clause prose is minted from the title and counted. The audit and
   remediation text, and the automated/manual marking, go to the stdlib facet
   assessment-criteria@1 - which is where the Checks tool reads them. Profile
   links in the back-matter become one baseline Set per profile, the CIS
   Controls cross-references become Mapping objects (supports, draft: the
   source types no relationship), the xccdf id an alias.

   The Python converter mints the namespace of the one benchmark it reads;
   for that title this preset mints the same, and tests/oscal.test.mjs
   compares every object by semantic digest with the converter's output on a
   synthetic catalog of the same shape. For any other benchmark the
   namespace is derived from the title and can be changed on the page.

   The `provenance.date` of a Mapping is the day of the catalog's
   `last-modified`, the date OSCAL gives a release; a catalog that has
   cross-references and no such date is refused with that reason. Until
   2026-11-13 preset and converter wrote the catalog's version there, which
   kernel 2.0.0 refuses since it holds that field to a date (DATE-3;
   ERRATA.md). */
const JSC_CIS = { cisc8: "https://ns.cisecurity.org/controls/v8", cisc7: "https://ns.cisecurity.org/controls/v7", key: "cisb", lang: "en",
  F_ACRIT: "https://ns.jascon.net/stdlib/facet/assessment-criteria@1", COMPAT: "https://ns.jascon.net/compat/oscal-1x@1",
  KNOWN: { "CIS Ubuntu Linux 24.04 LTS Benchmark": "https://ns.cisecurity.org/benchmark/ubuntu-24.04-lts" } };
function jscCisNamespace(cat) {
  const title = String((cat.metadata || {}).title || "").trim();
  if (JSC_CIS.KNOWN[title]) return JSC_CIS.KNOWN[title];
  const name = title.replace(/^CIS\s+/i, "").replace(/\s+Benchmark\b.*$/i, "").toLowerCase().replace(/[^a-z0-9.]+/g, "-").replace(/^-+|-+$/g, "");
  return "https://ns.cisecurity.org/benchmark/" + (name || "benchmark");
}
function jscImportCis(cat, opts) {
  const C = JSC_CIS, version = cat.metadata.version, lang = C.lang;
  const ns = (opts && opts.ns) || jscCisNamespace(cat);
  const F_NARR = `${ns}/facet/narrative@1`, F_XREF = `${ns}/facet/external-references@1`;
  const L = v => (v === undefined || v === null ? v : { [lang]: v });
  const objects = [], report = { preset: "cis-benchmark", controls: 0, statements: 0, methods: {}, mappings: { v7: 0, v8: 0 },
    "unresolved-links": 0, "minted-prose": 0, profiles: {}, namespace: ns };
  const resources = new Map((((cat["back-matter"] || {}).resources) || []).map(r => [r.uuid, r]));
  const kindOf = r => {
    for (const p of r.props || []) {
      if (p.name === "marking" && String(p.value || "").includes("benchmarks_profile")) return "profile";
      if (p.name === "version" && p.class === "CIS_Controls") return "safeguard";
    }
    return "document";
  };
  const profileMembers = new Map();
  /* the day CIS stated its cross-references: the release's last-modified, a date-time, cut to its date */
  const released = String(cat.metadata["last-modified"] || "").slice(0, 10);
  let seq = 0;
  const nseq = () => (seq += 10);
  function control(c) {
    const rid = `${ns}/req/${c.id}`, props = c.props || [];
    const labelProp = props.find(p => p.name === "label");
    const afterSep = v => { const i = v.indexOf("xccdf_id: "); return i >= 0 ? v.slice(i + 10) : v; };   // Python's split(sep, 1)[-1]
    const aliases = props.filter(p => p.name === "marking" && String(p.value).startsWith("xccdf_id:"))
      .map(p => ({ scheme: "xccdf", value: afterSep(String(p.value)) }));
    const methodProp = props.find(p => p.name === "marking" && (p.value === "automated" || p.value === "manual"));
    if (methodProp) report.methods[methodProp.value] = (report.methods[methodProp.value] || 0) + 1;
    report.controls++; report.statements++; report["minted-prose"]++;
    const req = { id: rid, version, label: labelProp ? labelProp.value : c.id, lifecycle: "active", title: L(c.title === undefined ? c.id : c.title),
      statements: [{ id: "s1", modality: "unspecified", "obligated-parties": [`${ns}/party/system-administrator`],
        prose: { [lang]: c.title === undefined ? "" : c.title } }] };
    if (aliases.length) req.aliases = aliases;
    const narr = {}, acrit = {}, xrefs = [];
    if (methodProp) acrit.method = methodProp.value;
    for (const p of c.parts || []) {
      const lab = ((p.props || []).find(x => x.name === "label") || {}).value;
      if (p.name === "statement" && (lab === "Description" || lab === "Rationale")) narr[lab.toLowerCase()] = L(p.prose === undefined ? "" : p.prose);
      else if (p.name === "assessment-method") acrit.audit = L(p.prose === undefined ? "" : p.prose);
      else if (p.name === "guidance" && lab === "Remediation") acrit.remediation = L(p.prose === undefined ? "" : p.prose);
      else if (p.name === "guidance" && p.class === "CIS_Controls") {
        for (const l of p.links || []) {
          const r = resources.get(String(l.href || "").replace(/^#+/, ""));
          if (!r || kindOf(r) !== "safeguard") { report["unresolved-links"]++; continue; }
          const num = ((r.props || []).find(x => x.name === "marking" && /^\d+(\.\d+)?$/.test(String(x.value))) || {}).value;
          const ver = ((r.props || []).find(x => x.name === "version" && x.class === "CIS_Controls") || {}).value || "?";
          if (!num) { report["unresolved-links"]++; continue; }
          let target;
          if (ver === "8") {
            const pp = String(num).split(".");
            target = `${C.cisc8}/req/cisc-${String(Number(pp[0])).padStart(3, "0")}${pp.length > 1 ? "." + String(Number(pp[1])).padStart(3, "0") : ""}`;
            report.mappings.v8++;
          } else { target = `${C.cisc7}/req/${num}`; report.mappings.v7++; }
          if (!/^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$/.test(released)) {
            throw new Error("the catalog's metadata.last-modified does not begin with a date, so its CIS Controls cross-references cannot be dated (a Mapping's provenance.date is a date, DATE-3)");
          }
          const tail = `${jscOscalSlug(c.id)}--v${ver}-${jscOscalSlug(num)}`;
          objects.push({ path: `objects/map/${tail}.json`, obj: { id: `${ns}/map/${tail}`, version, lifecycle: "active",
            "source-ref": rid, "target-ref": target, relationship: "supports", direction: "source-to-target", confidence: "draft",
            rationale: L("Imported from the CIS Benchmark's CIS Controls cross-reference; the source carried no typed relationship (handbook 8.6)."),
            provenance: { "author-ref": `${ns}/party/cis`, date: released } } });
        }
      } else if (p.name === "guidance" && p.class === "References") {
        xrefs.push(...(p.props || []).filter(x => x.name === "marking" && x.class === "Reference").map(x => x.value));
      }
    }
    const facets = {};
    if (Object.keys(narr).length) facets[F_NARR] = narr;
    if (Object.keys(acrit).length) facets[C.F_ACRIT] = acrit;
    if (xrefs.length) facets[F_XREF] = { references: xrefs };
    if (Object.keys(facets).length) req.facets = facets;
    const rels = [];
    for (const l of c.links || []) {
      const u = String(l.href || "").replace(/^#+/, ""), r = resources.get(u);
      if (r && kindOf(r) === "profile") {
        const t = r.title || u;
        if (!profileMembers.has(t)) profileMembers.set(t, []);
        profileMembers.get(t).push(rid);
      } else if (r) rels.push({ type: "reference", ref: ((r.rlinks || [{}])[0] || {}).href || r.title || u });
      else report["unresolved-links"]++;
    }
    if (rels.length) req.relations = rels;
    objects.push({ path: `objects/req/${jscOscalSlug(c.id)}.json`, obj: req });
    return rid;
  }
  /* Sequence numbers follow the converter: a sub-group's entry is numbered
     after its own members, a control's after it was converted. */
  function group(g) {
    const entries = [];
    let carried = (g.parts || []).map(p => ({ group: g.title === undefined ? "" : g.title, name: p.name, prose: L(p.prose === undefined ? "" : p.prose) }));
    for (const sub of g.groups || []) {
      const [uri, sc] = group(sub);
      carried = carried.concat(sc);
      if (uri) entries.push({ ref: uri, sequence: nseq() });
    }
    for (const c of g.controls || []) { const ref = control(c); entries.push({ ref, sequence: nseq() }); }
    if (!entries.length) return [null, carried];
    const label = ((g.props || []).find(p => p.name === "label") || {}).value;
    const name = jscOscalSlug(g.id || g.title);
    const set = { id: `${ns}/set/tax/${name}`, version, lifecycle: "active", title: L(g.title === undefined ? "" : g.title), members: entries };
    if (label) set.label = label;
    if (carried.length) { set.facets = { [C.COMPAT]: { "group-parts": carried } }; carried = []; }
    objects.push({ path: `objects/set/tax-${name}.json`, obj: set });
    return [set.id, carried];
  }
  const top = [];
  let rootCarried = [];
  for (const g of cat.groups || []) {
    const [uri, carried] = group(g);
    rootCarried = rootCarried.concat(carried);
    if (uri) top.push({ ref: uri, sequence: nseq() });
  }
  const root = { id: `${ns}/set/tax/root`, version, lifecycle: "active", title: L(cat.metadata.title), members: top };
  if (rootCarried.length) root.facets = { [C.COMPAT]: { "group-parts": rootCarried } };
  objects.push({ path: "objects/set/tax-root.json", obj: root });
  const byCodePoint = (a, b) => (a < b ? -1 : a > b ? 1 : 0);
  for (const title of [...profileMembers.keys()].sort(byCodePoint)) {
    const clean = title.replace(/\\+/g, " "), name = jscOscalSlug(clean), refs = [...new Set(profileMembers.get(title))].sort(byCodePoint);
    report.profiles[clean] = refs.length;
    objects.push({ path: `objects/set/profile-${name}.json`, obj: { id: `${ns}/set/profile/${name}`, version, lifecycle: "active",
      title: L(`Benchmark profile: ${clean}`), members: refs.map((ref, i) => ({ ref, sequence: (i + 1) * 10 })) } });
  }
  const stub = (file, id, props, note) => ({ path: `schemas/${file}`, def: { id, version: "1.0.0", "modifies-semantics": [],
    note: note || "NORMATIVE pinned payload schema (backlog #26): closed shape - unknown keys are rejected, never smuggled",
    schema: { $schema: "https://json-schema.org/draft/2020-12/schema", type: "object", properties: props, additionalProperties: false } } });
  const facetSchemas = [
    jscStdlibPin("assessment-criteria"),
    stub("cisb-narrative-stub.json", F_NARR.split("@")[0], { description: { type: "object" }, rationale: { type: "object" } }),
    stub("cisb-external-references-stub.json", F_XREF.split("@")[0], { references: { type: "array", items: { type: "string" } } }),
    stub("oscal-1x-compat-stub.json", "https://ns.jascon.net/compat/oscal-1x", { "group-parts": { type: "array" } },
      "ILLUSTRATIVE STUB - Level-2 waiting room (intended deprecation; see D16/handbook 14.6)"),
  ];
  const provenance = { sources: [{ key: C.key, title: cat.metadata.title, version, "oscal-version": cat.metadata["oscal-version"] }],
    converter: "JASCON-App OSCAL import, preset cis-benchmark (the rules of convert_cis_benchmark.py v0.1)",
    "namespace-note": "authority namespace minted by converter pending a CIS-published URI" };
  return { objects, facetSchemas, provenance, report };
}

/* doc: the parsed OSCAL file. -> { objects: [{path, obj}], facetSchemas: [{path, def}], provenance, report } */
function jscOscalImportCatalog(doc, opts) {
  const cat = doc && doc.catalog;
  if (!cat || !cat.metadata) throw new Error("this is not an OSCAL catalog: no catalog.metadata");
  return opts.preset === "bsi-gspp" ? jscImportBsi(cat) : opts.preset === "nist-sp800-53" ? jscImportNist(cat)
    : opts.preset === "cis-benchmark" ? jscImportCis(cat, opts) : jscImportGeneric(cat, opts);
}
/* A guess at the preset from the catalog itself; the user decides. */
function jscOscalGuessPreset(doc) {
  const title = (((doc || {}).catalog || {}).metadata || {}).title || "";
  return /Grundschutz\+\+/.test(title) ? "bsi-gspp" : /SP 800-53 Rev(ision)? 5/i.test(title) ? "nist-sp800-53"
    : /^\s*CIS\b.*\bBenchmark\b/i.test(title) ? "cis-benchmark" : "generic";
}

/* ====================================================================
   Profile -> RequirementSet + Tailoring
   ====================================================================
   opts: { ns, lang, objs: Map(id -> {type, obj}) of the set the profile is
   imported into, catalogSet: id of the Set an include-all stands for }.
   A profile names controls by their OSCAL id. The Requirement it means is
   the one of the set whose id ends in that control id (compared without
   case, because converters differ in it).
   Carried: include-controls.with-ids, include-all, exclude-controls.with-ids,
   set-parameters. Reported and not carried: matching patterns,
   with-child-controls, alters, merge - the kernel has no place for a merge
   directive, and an alter is a change of text that somebody has to decide
   is editorial or substantive.
   -> { objects: [{path, obj}], report } */
function jscOscalImportProfile(doc, opts) {
  const p = doc && doc.profile;
  if (!p || !p.metadata) throw new Error("this is not an OSCAL profile: no profile.metadata");
  const ns = String(opts.ns).replace(/\/+$/, ""), lang = opts.lang || "en", objs = opts.objs;
  const title = p.metadata.title || "profile", name = jscOscalSlug(title), version = String(p.metadata.version || "1");
  const report = { imports: (p.imports || []).length, included: 0, "not-found": [], ambiguous: [], excluded: 0, "parameters-set": 0, "parameters-not-found": [],
    "parameters-outside-declared-space": [], "include-all": 0, "not-carried": {} };
  const note = k => { report["not-carried"][k] = (report["not-carried"][k] || 0) + 1; };
  const bySuffix = new Map();
  for (const [id, r] of objs) {
    if (r.type !== "requirement") continue;
    const k = id.split("/").pop().toLowerCase();
    bySuffix.set(k, [...(bySuffix.get(k) || []), id]);
  }
  const resolve = cid => {
    const hit = bySuffix.get(String(cid).toLowerCase()) || [];
    if (!hit.length) report["not-found"].push(cid);
    if (hit.length > 1) report.ambiguous.push(cid);
    return hit.length === 1 ? hit[0] : null;
  };
  const withIds = list => (list || []).flatMap(sel => {
    if (sel.matching) note("matching patterns");
    if (sel["with-child-controls"] === "yes") note("with-child-controls");
    return sel["with-ids"] || [];
  });
  const members = [], excludes = [], selects = [];
  for (const imp of p.imports || []) {
    if (imp["include-all"]) {
      report["include-all"]++;
      if (opts.catalogSet && !selects.some(s => s["set-ref"] === opts.catalogSet)) selects.push({ "set-ref": opts.catalogSet });
    }
    for (const cid of withIds(imp["include-controls"])) { const id = resolve(cid); if (id && !members.includes(id)) members.push(id); }
    for (const cid of withIds(imp["exclude-controls"])) { const id = resolve(cid); if (id && !excludes.includes(id)) excludes.push(id); }
  }
  report.included = members.length; report.excluded = excludes.length;
  const out = [];
  if (members.length) {
    const setId = `${ns}/set/profile/${name}`;
    out.push({ path: `objects/set/profile-${name}.json`, obj: { id: setId, version, lifecycle: "active", title: { [lang]: title },
      members: members.map((ref, i) => ({ ref, sequence: (i + 1) * 10 })) } });
    selects.unshift({ "set-ref": setId });
  }
  /* set-parameters: one operation for every clause that declares the parameter */
  const inScope = new Set(members);
  for (const s of selects) if (objs.has(s["set-ref"])) for (const id of jscOscalRules.jscExpandRefs([s["set-ref"]], objs)) inScope.add(id);
  const operations = [];
  for (const sp of (p.modify || {})["set-parameters"] || []) {
    const pid = sp["param-id"], value = (sp.values || [])[0];
    if (value === undefined) { note("set-parameters without a value"); continue; }
    let found = 0;
    for (const rid of inScope) {
      for (const st of objs.get(rid).obj.statements) {
        const decl = (st.parameters || []).find(x => x.name === pid);
        if (!decl) continue;
        found++;
        const verdict = jscOscalRules.jscParamCheck(decl, value);
        if (verdict !== "valid") { report["parameters-outside-declared-space"].push({ parameter: pid, requirement: rid, statement: st.id, value, verdict }); continue; }
        operations.push({ op: "set-parameter", "requirement-ref": rid, "statement-id": st.id, parameter: pid, value });
      }
    }
    if (!found) report["parameters-not-found"].push(pid);
  }
  report["parameters-set"] = operations.length;
  for (const a of (p.modify || {}).alters || []) note((a.adds ? "alters with adds" : "") + (a.adds && a.removes ? " and " : "") + (a.removes ? "alters with removes" : "") || "alters");
  if (p.merge) note("merge (" + Object.keys(p.merge).join(", ") + ")");
  if (selects.length) {
    const t = { id: `${ns}/tailoring/${name}`, version, label: name, lifecycle: "draft", title: { [lang]: title }, selects };
    if (excludes.length) t.excludes = excludes.map(ref => ({ ref }));
    t.operations = operations;
    out.push({ path: `objects/tailoring/${name}.json`, obj: t });
  }
  return { objects: out, report };
}
const jscOscalRules = (typeof module !== "undefined" && module.exports) ? require("./jascon-rules.js") : { jscExpandRefs, jscParamCheck };

/* What kind of OSCAL document a parsed file is: its single root key. */
function jscOscalKind(doc) {
  const keys = doc && typeof doc === "object" && !Array.isArray(doc) ? Object.keys(doc) : [];
  return keys.length === 1 ? keys[0] : null;
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { jscOscalSlug, jscOscalProse, jscOscalImportCatalog, jscOscalGuessPreset, jscOscalImportProfile, jscOscalKind, JSC_BSI, JSC_NIST,
    JSC_CIS, jscCisNamespace };
}
