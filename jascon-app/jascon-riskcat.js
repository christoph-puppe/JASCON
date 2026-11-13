/* JASCON-App: risk catalogues.

   A risk catalogue is a published list of risk scenarios. An entry carries
   what a publisher can know (title, scenario, the requirements that
   typically treat it) and nothing only an organisation can supply (owner,
   state, rating, acceptance). That is why an entry is not a kernel Risk, and
   why catalogues stay outside the kernel.

   Import is a copy. jscCatalogImport turns entries into kernel Risk objects
   under the organisation's own ids; nothing references an entry at run time,
   so a new catalogue version cannot change a risk the organisation owns.
   Importing twice writes nothing twice: a Risk whose id exists is left as it
   is, because by then it holds the organisation's work.

   Not importing an entry is a decision too. It is recorded in a file beside
   the bundle's manifest (risk-catalogs/schema/not-applicable.draft.schema.json):
   the entry, why it does not apply, who decided and when. Inside this file
   the record is a plain object { entry id: row }; jscNaRead and jscNaWrite
   are the only two places that know the file's shape.

   Ported from risk-catalogs/tools/risk_catalog.py, which is the reference;
   tests/riskcat.test.mjs rebuilds the committed demo with this file. Pure
   functions of plain data; `objs` is a Map of id -> {type, obj}. */
"use strict";

const JSC_INSTANTIATES = "https://github.com/christoph-puppe/JASCON/risk-catalogs/relation/instantiates";
const jscRiskcatRules = (typeof module !== "undefined" && module.exports) ? require("./jascon-rules.js") : { jscSelection, jscExpandRefs };
const jscEntryLabel = e => e.label || String(e.id).split("/").pop();

/* The requirements a catalogue import may lean on: those the named Tailoring
   selects, or every requirement in force when the bundle has no Tailoring.
   -> { selected: Set, tailoring: id or null, how, error? } */
function jscCatalogSelection(objs, tailoringId) {
  const tailorings = [...objs].filter(([, r]) => r.type === "tailoring" && r.obj.lifecycle !== "withdrawn").map(([id]) => id).sort();
  if (!tailoringId) {
    if (!tailorings.length) {
      const all = new Set([...objs].filter(([, r]) => r.type === "requirement" && r.obj.lifecycle !== "withdrawn").map(([id]) => id));
      return { selected: all, tailoring: null, how: "no Tailoring in the bundle: every requirement is in play" };
    }
    if (tailorings.length > 1) return { selected: new Set(), tailoring: null, how: "", error: `the bundle holds ${tailorings.length} Tailorings - name one` };
    tailoringId = tailorings[0];
  }
  const t = objs.get(tailoringId);
  if (!t || t.type !== "tailoring") return { selected: new Set(), tailoring: null, how: "", error: `${tailoringId} is not a Tailoring of this bundle` };
  const s = jscRiskcatRules.jscSelection(t.obj, objs);
  if (s.open) return { selected: new Set(), tailoring: tailoringId, how: "", error: `${tailoringId} carries a predicate select; a catalogue import resolves set-refs only` };
  return { selected: s.selected, tailoring: tailoringId, how: `selected by ${tailoringId}` };
}

/* The file of entries that do not apply -> { entry id: row }.
   Before 2026-11-13 the file was a map from an entry's id or label to one
   sentence. Such a file is read as rows that say no author and no date,
   because none was recorded; a label is resolved through the catalogues the
   app ships. The next jscNaWrite stores the record in today's shape. */
function jscNaRead(doc, catalogs, lang) {
  if (!doc || typeof doc !== "object" || Array.isArray(doc)) return {};
  if (doc["record-version"] === 1 && Array.isArray(doc.entries)) return Object.fromEntries(doc.entries.map(row => [row.entry, row]));
  if ("record-version" in doc) return {};          // a later version of the record: not ours to guess at
  const byLabel = new Map((catalogs || []).flatMap(c => c.entries.map(e => [jscEntryLabel(e), e.id])));
  const rows = {};
  for (const [key, why] of Object.entries(doc)) {
    if (typeof why !== "string" || !why.trim()) continue;
    const entry = byLabel.get(key) || key;
    rows[entry] = { entry, rationale: { [lang || "en"]: why } };
  }
  return rows;
}

/* { entry id: row } -> the file, rows in the order of their entry ids so that
   the same decisions always give the same bytes. */
function jscNaWrite(rows) {
  return { "record-version": 1, entries: Object.keys(rows).sort().map(k => rows[k]) };
}

/* entries -> Risk objects and a report.
   opts: { org, owner, tailoring, notApplicable: { entry id: row }, only: Set of entry ids or null }
   Suggested treatments are kept only where the selection has the
   requirement; the others are named in the report. An entry with a recorded
   reason is not imported. An entry whose Risk id exists is skipped.
   -> { risks: [Risk], report, error? } */
function jscCatalogImport(catalog, entries, objs, opts) {
  const sel = jscCatalogSelection(objs, opts.tailoring);
  if (sel.error) return { risks: [], report: null, error: sel.error };
  const na = opts.notApplicable || {}, risks = [], inScope = new Set();
  const report = { catalog: catalog.id, "catalog-version": catalog.version, selection: sel.how, "selected-requirements": sel.selected.size,
    imported: [], "not-applicable": [], "suggestions-out-of-scope": {}, "without-treatment": [], "already-there": [] };
  for (const e of entries) {
    if (opts.only && !opts.only.has(e.id)) continue;
    const label = jscEntryLabel(e);
    if (na[e.id]) { report["not-applicable"].push(na[e.id]); continue; }      // the row as it was recorded
    const id = `${String(opts.org).replace(/\/+$/, "")}/risk/${label}`;
    if (objs.has(id)) { report["already-there"].push(id); continue; }
    const keep = [], dropped = [];
    for (const st of e["suggested-treatments"] || []) (sel.selected.has(st["requirement-ref"]) ? keep : dropped).push(st);
    keep.forEach(st => inScope.add(st["requirement-ref"]));
    const risk = { id, version: "1", lifecycle: "draft", label, title: e.title, scenario: e.scenario, "owner-ref": opts.owner, state: "identified" };
    if (sel.tailoring) risk["tailoring-refs"] = [sel.tailoring];
    if (keep.length) risk.treatments = keep; else report["without-treatment"].push(id);
    risk.relations = [{ type: JSC_INSTANTIATES, ref: e.id }];
    risk.annotations = { "imported-from": { entry: e.id, "entry-version": e.version, catalog: catalog.id, "catalog-version": catalog.version } };
    if (dropped.length) report["suggestions-out-of-scope"][id] = dropped.map(st => st["requirement-ref"]);
    risks.push(risk);
    report.imported.push(id);
  }
  report["selected-requirements-no-entry-suggests"] = [...sel.selected].filter(q => !inScope.has(q)).length;
  return { risks, report };
}

/* Which entries does a Risk of the bundle instantiate, which carry a
   recorded reason for not being imported, and which are neither: a gap.
   -> [{ entry, label, status: "instantiated" | "not-applicable" | "gap", risks: [id], row }]
   `row` is the recorded decision of a "not-applicable" entry, else null. */
function jscCatalogCompleteness(entries, objs, notApplicable) {
  const instantiated = new Map(), na = notApplicable || {};
  for (const [id, r] of objs) {
    if (r.type !== "risk" || r.obj.lifecycle === "withdrawn") continue;
    for (const rel of r.obj.relations || []) {
      if (rel.type === JSC_INSTANTIATES) instantiated.set(rel.ref, [...(instantiated.get(rel.ref) || []), id]);
    }
  }
  return entries.map(e => {
    const row = na[e.id] || null;
    const status = instantiated.has(e.id) ? "instantiated" : row ? "not-applicable" : "gap";
    return { entry: e, label: jscEntryLabel(e), status, risks: instantiated.get(e.id) || [], row: status === "not-applicable" ? row : null };
  });
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { JSC_INSTANTIATES, jscEntryLabel, jscNaRead, jscNaWrite, jscCatalogSelection, jscCatalogImport, jscCatalogCompleteness };
}
