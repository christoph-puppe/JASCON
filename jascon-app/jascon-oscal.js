/* JASCON-App: importing OSCAL catalogs and profiles.

   An OSCAL catalog becomes Requirements and RequirementSets; an OSCAL
   profile becomes a RequirementSet (what it includes) and a Tailoring (what
   it excludes and sets). Everything after the import works on JASCON.

   Three ways to read a catalog, chosen by `preset`:

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
   The NIST SP 800-53 rules of convert_nist.py (withdrawn controls folded
   into `replaces`, assessment objectives, ODP facets) are not ported; the
   generic path reads that catalog, with a different result than the shipped
   bundle, and the report says so.

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
  F_GRAM: "https://ns.oscal.org/stdlib/facet/statement-grammar@1", F_SECO: "https://ns.oscal.org/stdlib/facet/security-objectives@1",
  F_ACRIT: "https://ns.oscal.org/stdlib/facet/assessment-criteria@1", F_TAX: "https://ns.bsi.bund.de/facet/gspp-taxonomy@1",
  F_NARR: "https://ns.bsi.bund.de/facet/gspp-narrative@1", F_COMPAT: "https://ns.oscal.org/compat/oscal-1x@1",
  MODAL: { "MUSS": "must", "SOLLTE": "should", "KANN": "may", "DARF NICHT": "must-not", "SOLLTE NICHT": "should-not", "DARF NUR": "may-only",
    "MÜSSEN": "must", "SOLLTEN": "should", "KÖNNEN": "may", "DÜRFEN NICHT": "must-not", "DÜRFEN NUR": "may-only" },
};
function jscImportBsi(cat) {
  const B = JSC_BSI, ns = B.ns, version = cat.metadata.version, lang = B.lang;
  const objects = [], bm = jscBackMatter(cat), secValues = new Set(), baseline = new Map();
  const report = { preset: "bsi-gspp", controls: 0, statements: 0, "source-defects": [], "unknown-modal-verbs": {}, "parameters-unreferenced": 0 };
  let seq = 0;
  const nseq = () => (seq += 10);
  /* one statement, and its facet payloads keyed by the statement id, from control c */
  const statement = (c, sid, isChild, req) => {
    const parts = c.parts || [], smt = parts.find(p => p.name === "statement") || {}, guid = parts.find(p => p.name === "guidance");
    const text = jscOscalProse(smt.prose), pp = jscPropMap(smt.props), cp = jscPropMap(c.props);
    for (const part of parts) for (const p of part.props || []) {
      if (String(p.value || "").includes("{{")) report["source-defects"].push({ control: c.id, part: part.name, prop: p.name, value: p.value });
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
    jscFacetStub("oscal-1x-compat-1.0.0-stub.json", "https://ns.oscal.org/compat/oscal-1x", [], { "param-extras": { type: "object" } }),
  ];
  const provenance = { sources: [{ key: B.key, title: cat.metadata.title, version, "oscal-version": cat.metadata["oscal-version"] }],
    converter: "JASCON-App OSCAL import, preset bsi-gspp (the rules of convert_bsi.py v0.2)" };
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
      const declared = tokens.map(t => { used.add(t); return params.has(t) ? paramOf(params.get(t)) : { name: t, type: "string" }; });   // every token is declared (the 216 rule)
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

/* doc: the parsed OSCAL file. -> { objects: [{path, obj}], facetSchemas: [{path, def}], provenance, report } */
function jscOscalImportCatalog(doc, opts) {
  const cat = doc && doc.catalog;
  if (!cat || !cat.metadata) throw new Error("this is not an OSCAL catalog: no catalog.metadata");
  return opts.preset === "bsi-gspp" ? jscImportBsi(cat) : jscImportGeneric(cat, opts);
}
/* A guess at the preset from the catalog itself; the user decides. */
function jscOscalGuessPreset(doc) {
  const title = (((doc || {}).catalog || {}).metadata || {}).title || "";
  return /Grundschutz\+\+/.test(title) ? "bsi-gspp" : "generic";
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
  module.exports = { jscOscalSlug, jscOscalProse, jscOscalImportCatalog, jscOscalGuessPreset, jscOscalImportProfile, jscOscalKind, JSC_BSI };
}
