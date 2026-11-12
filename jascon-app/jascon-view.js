/* JASCON-App shared view code for the tool pages.

   What more than one tool page shows the same way: an object rendered for a
   human, a reference that can be clicked, a picker that finds an object by
   typing, small charts, and the index of filter dimensions. A page loads
   jascon-core.js, jascon-rules.js and then this file.

   Rendering rules, the same as in the bundle reader this derives from:
   - kernel fields are shown plain, facets in a tinted box, annotations in a
     dashed one, so the three layers of an object stay apart;
   - every text of a bundle goes through jscEsc before it becomes markup;
   - a reference to an object of the set is a link, a reference to something
     outside it is shown greyed and is not a link.

   Clicking a reference opens the object in a drawer on the right of the page,
   so a page never loses its place. A page that has its own detail area
   (Browse) sets jscView.onOpen and gets the id instead.

   Not here: anything only one page needs. */
"use strict";
(() => {

jscI18n.add("de", {
  "One requirement of a framework with its clauses: statements, each with a binding force (modality), the parties it binds, typed parameters and prose in several languages.":
    "Eine Anforderung eines Regelwerks mit ihren Klauseln: Statements, jedes mit Bindungswirkung (Modalität), verpflichteten Parteien, typisierten Parametern und Prosa in mehreren Sprachen.",
  "Membership: chapters, baselines and profiles are all Sets of references. Nesting Sets is the only hierarchy.":
    "Mitgliedschaft: Kapitel, Baselines und Profile sind alle Sets von Verweisen. Geschachtelte Sets sind die einzige Hierarchie.",
  "A selection plus change operations addressed by identity. A weakening needs a Deviation, unless the authority itself publishes the Tailoring.":
    "Eine Auswahl plus identitätsadressierte Änderungsoperationen. Eine Abschwächung braucht eine Deviation, außer die Autorität selbst veröffentlicht das Tailoring.",
  "A typed claim that two requirements relate, with a relationship code, a confidence grade and its author. Contradicting mappings may coexist.":
    "Eine typisierte Aussage über die Beziehung zweier Anforderungen, mit Beziehungscode, Vertrauensgrad und Autor. Widersprüchliche Mappings dürfen nebeneinander bestehen.",
  "A system, service or product with its capabilities and authorizations.":
    "Ein System, Dienst oder Produkt mit seinen Fähigkeiten und Autorisierungen.",
  "The edge that says: this component satisfies this requirement, with the responsibility per clause and, where inherited, the authorization it rests on.":
    "Die Kante, die sagt: Diese Komponente erfüllt diese Anforderung, mit der Verantwortung je Klausel und, wo geerbt, der Autorisierung, auf der das beruht.",
  "The record made before the fact: a scenario with an owner, a state, a level on a named scale, a treatment decision and the requirements that carry it.":
    "Der Eintrag vor dem Ereignis: ein Szenario mit Eigner, Zustand, Stufe auf einer benannten Skala, Behandlungsentscheidung und den Anforderungen, die sie tragen.",
  "An assessment run: subjects, method, performer, result.": "Ein Prüfdurchlauf: Gegenstände, Methode, Prüfer, Ergebnis.",
  "A finding against a requirement, down to the statement, with states, actions that carry deadlines, and Deviations.":
    "Eine Feststellung gegen eine Anforderung, bis zum Statement, mit Zuständen, Maßnahmen mit Fristen und Deviations.",
  "The signature layer: semantic digests of the subjects, the digest of the manifest and the pinned rendering.":
    "Die Signaturschicht: Semantic-Digests der Gegenstände, der Digest des Manifests und das gepinnte Rendering.",
  "binding obligation": "bindende Pflicht", "expected unless justified": "erwartet, sofern nicht begründet abgewichen wird",
  "explicit permission": "ausdrückliche Erlaubnis", "permitted only under the stated condition": "nur unter der genannten Bedingung erlaubt",
  "discouraged": "nicht empfohlen", "prohibition": "Verbot",
  "no modal verb in the source; the binding force comes from baseline membership": "kein Modalverb in der Quelle; die Bindungswirkung kommt aus der Baseline-Mitgliedschaft",
  "not in this set": "nicht in diesem Set", "statement {id}": "Statement {id}", "obligated party": "verpflichtete Partei",
  "Members ({n})": "Mitglieder ({n})", "first {n} shown": "die ersten {n} gezeigt", "empty": "leer",
  "Selects": "Auswahl", "Excludes": "Ausschlüsse", "Operations ({n})": "Operationen ({n})", "carries a Deviation": "trägt eine Deviation",
  "source": "Quelle", "relationship": "Beziehung", "target": "Ziel", "direction": "Richtung", "confidence": "Vertrauensgrad",
  "rationale": "Begründung", "provenance": "Herkunft", "Fields": "Felder",
  "Aliases": "Aliase", "Relations": "Beziehungen", "Facets (registered extensions, schema-pinned)": "Facets (registrierte Erweiterungen, schemagepinnt)",
  "keyed by statement": "nach Statement geschlüsselt", "Annotations (not part of the signed meaning)": "Annotationen (nicht Teil der signierten Bedeutung)",
  "Integrity (from the manifest)": "Integrität (aus dem Manifest)", "raw JSON": "rohes JSON", "Deviations": "Deviations",
  "state": "Zustand", "owner": "Eigner", "Scenario": "Szenario", "Rating": "Bewertung", "Residual rating": "Restrisiko-Bewertung",
  "level": "Stufe", "likelihood": "Eintrittswahrscheinlichkeit", "impact": "Auswirkung", "scale": "Skala",
  "override rationale": "Begründung der Abweichung von der Matrix", "treatment": "Behandlung", "Treated by": "Behandelt durch",
  "shared with": "geteilt mit", "Acceptance": "Akzeptanz", "approver": "genehmigt von", "date": "Datum", "review due": "Überprüfung fällig",
  "Threats": "Gefährdungen", "Components at risk": "Betroffene Komponenten", "Belongs to the Tailorings": "Gehört zu den Tailorings",
  "Close": "Schließen", "no match": "kein Treffer", "edited in this app": "in dieser App bearbeitet",
  "{n} dimensions offered as filters: {list}": "{n} Dimensionen als Filter angeboten: {list}",
  "not offered as filters (free text, values do not repeat): {list}": "nicht als Filter angeboten (Freitext, Werte wiederholen sich nicht): {list}",
});

jscI18n.add("de", {
  "A machine check: the facts a collector reports and the comparisons they must pass. The code that collects rides along and decides nothing.":
    "Eine maschinelle Prüfung: die Fakten, die ein Kollektor meldet, und die Vergleiche, die sie bestehen müssen. Der Code, der sammelt, reist mit und entscheidet nichts.",
  "discharges": "erfüllt", "platform": "Plattform", "confidence": "Vertrauensgrad", "per resource": "je Ressource",
  "none observed passes": "keine beobachtet gilt als bestanden", "none observed is inconclusive": "keine beobachtet ist unbestimmt",
  "fresh for": "gültig für", "author": "Autor", "Facts the collector reports": "Fakten, die der Kollektor meldet", "Applies when": "Gilt, wenn",
  "Passes when all of these hold": "Bestanden, wenn alle diese gelten", "Collectors": "Kollektoren",
});

jscI18n.add("de", {
  "names no requirement": "nennt keine Anforderung", "suggested values": "vorgeschlagene Werte", "kind": "Art",
  "product version": "Produktversion", "describes": "beschreibt", "Capabilities ({n})": "Fähigkeiten ({n})",
  "Authorizations": "Autorisierungen", "from an advice pack": "aus einem Advice Pack",
});

const esc = jscEsc;
const TYPE_VIEW = {
  requirement:    { glyph: "◇", color: "var(--accent)", what: N("One requirement of a framework with its clauses: statements, each with a binding force (modality), the parties it binds, typed parameters and prose in several languages.") },
  requirementSet: { glyph: "▣", color: "var(--blue)", what: N("Membership: chapters, baselines and profiles are all Sets of references. Nesting Sets is the only hierarchy.") },
  tailoring:      { glyph: "◬", color: "var(--amber)", what: N("A selection plus change operations addressed by identity. A weakening needs a Deviation, unless the authority itself publishes the Tailoring.") },
  mapping:        { glyph: "⇄", color: "var(--teal)", what: N("A typed claim that two requirements relate, with a relationship code, a confidence grade and its author. Contradicting mappings may coexist.") },
  component:      { glyph: "⬡", color: "var(--green)", what: N("A system, service or product with its capabilities and authorizations.") },
  implementation: { glyph: "◈", color: "var(--green)", what: N("The edge that says: this component satisfies this requirement, with the responsibility per clause and, where inherited, the authorization it rests on.") },
  risk:           { glyph: "△", color: "color-mix(in oklab, var(--red) 55%, var(--amber))", what: N("The record made before the fact: a scenario with an owner, a state, a level on a named scale, a treatment decision and the requirements that carry it.") },
  check:          { glyph: "⊨", color: "color-mix(in oklab, var(--green) 60%, var(--blue))", what: N("A machine check: the facts a collector reports and the comparisons they must pass. The code that collects rides along and decides nothing.") },
  assessment:     { glyph: "◉", color: "var(--red)", what: N("An assessment run: subjects, method, performer, result.") },
  finding:        { glyph: "◎", color: "var(--red)", what: N("A finding against a requirement, down to the statement, with states, actions that carry deadlines, and Deviations.") },
  attestation:    { glyph: "✦", color: "var(--text-primary)", what: N("The signature layer: semantic digests of the subjects, the digest of the manifest and the pinned rendering.") },
};
const MODALITY_COLOR = { must: "var(--accent)", should: "var(--blue)", may: "var(--green)", "may-only": "var(--teal)",
  "should-not": "var(--amber)", "must-not": "var(--red)", unspecified: "var(--text-quiet)" };
const MODALITY_EXPLAIN = { must: N("binding obligation"), should: N("expected unless justified"), may: N("explicit permission"),
  "may-only": N("permitted only under the stated condition"), "should-not": N("discouraged"), "must-not": N("prohibition"),
  unspecified: N("no modal verb in the source; the binding force comes from baseline membership") };
const VERDICT_CLASS = { monotone: "verdict-ok", easing: "verdict-warn", "axis-change": "verdict-bad" };

const objs = () => jscSet.graph.objects;
const last = uri => String(uri).split("/").filter(Boolean).pop() || String(uri);
const labelOf = r => r.obj.label || TT(r.obj.title) || last(r.obj.id);
const titleOf = r => TT(r.obj.title) || r.obj.label || last(r.obj.id);
const typeGlyph = type => `<span style="color:${TYPE_VIEW[type].color}">${TYPE_VIEW[type].glyph}</span>`;
const typeBadge = type => `<span class="badge" style="border-color:${TYPE_VIEW[type].color};color:${TYPE_VIEW[type].color}">${TYPE_VIEW[type].glyph} ${esc(type)}</span>`;
const badge = (text, title) => `<span class="badge"${title ? ` title="${esc(title)}"` : ""}>${esc(text)}</span>`;
const modBadge = m => `<span class="badge" style="border-color:${MODALITY_COLOR[m] || "var(--text-quiet)"};color:${MODALITY_COLOR[m] || "var(--text-quiet)"}" title="${esc(T(MODALITY_EXPLAIN[m] || ""))}">${esc(m)}</span>`;

/* A reference: a link when the object is in the set, greyed text otherwise.
   `text` replaces the URI as the visible text. */
function refLink(uri, text) {
  const shown = esc(text === undefined ? uri : text);
  return objs().has(uri)
    ? `<a class="reflink" data-ref="${esc(uri)}" tabindex="0" role="link">${shown}</a>`
    : `<span class="reflink dead" title="${esc(T("not in this set"))}">${shown}</span>`;
}
function wireRefs(root) {
  root.querySelectorAll("[data-ref]").forEach(a => {
    const go = () => jscView.open(a.dataset.ref);
    a.addEventListener("click", go);
    a.addEventListener("keydown", e => { if (e.key === "Enter") go(); });
  });
}
const prose = txt => esc(txt).replace(/\{param:([^}]+)\}/g, (m, p) => `<span class="paramtok">{param:${p}}</span>`);
function langBlocks(map, cls) {
  return Object.entries(map || {}).map(([lang, txt]) => `<div class="${cls || ""}">${badge(lang)}` +
    (Array.isArray(txt) ? "<ul style='margin-left:18px'>" + txt.map(x => `<li>${prose(x)}</li>`).join("") + "</ul>" : prose(txt)) + "</div>").join("");
}
const kv = (k, vHtml) => `<div class="k">${esc(k)}</div><div class="v">${vHtml}</div>`;
const isLangMap = v => v && typeof v === "object" && !Array.isArray(v) && Object.keys(v).length > 0 &&
  Object.keys(v).every(k => /^[a-z]{2,3}(-|$)/i.test(k) && (typeof v[k] === "string" || Array.isArray(v[k])));
/* Any value, readable: scalars as text, lists of scalars as badges, language
   maps as tagged prose, everything else as a nested key-value grid. */
function prettyVal(v, depth = 0) {
  if (v === null || v === undefined) return `<span class="hint">—</span>`;
  if (typeof v !== "object") return esc(String(v));
  if (Array.isArray(v)) {
    if (!v.length) return `<span class="hint">[]</span>`;
    if (v.every(x => typeof x !== "object")) return v.map(x => badge(String(x))).join(" ");
    return v.map(x => `<div style="margin:3px 0 3px ${depth ? 10 : 0}px;border-left:2px solid var(--border-2);padding-left:8px">${prettyVal(x, depth + 1)}</div>`).join("");
  }
  if (isLangMap(v)) return langBlocks(v);
  return `<div class="kv" style="grid-template-columns:${depth ? 130 : 150}px 1fr">` +
    Object.entries(v).map(([k, x]) => kv(k, prettyVal(x, depth + 1))).join("") + `</div>`;
}
const section = (title, html) => html ? `<div class="nano sectionlabel">${esc(title)}</div>${html}` : "";

/* ---------- per-type bodies ---------- */
function requirementBody(o) {
  return (o.statements || []).map(s => {
    const params = (s.parameters || []).map(p => {
      const bits = [p.type, p.label && TT(p.label), p.default !== undefined && "default " + JSON.stringify(p.default),
        p.unit && `${p.num} ${p.unit}`, p.tightening && "tightening " + p.tightening,
        p.choices && p.choices.map(c => c.value).join(" | ")].filter(Boolean);
      return badge("⚙ " + p.name, bits.join(" · "));
    }).join(" ");
    return `<div class="stmt"><div>${badge(T("statement {id}", { id: s.id }))}${modBadge(s.modality)}
      ${(s["obligated-parties"] || []).map(p => badge("◈ " + last(p), T("obligated party") + ": " + p)).join("")}${params}</div>
      ${langBlocks(s.prose, "prose")}</div>`;
  }).join("") + section(T("Deviations"), o.deviations ? prettyVal(o.deviations) : "");
}
function setBody(o) {
  const mem = o.members || [], cap = 300;
  const rows = mem.slice(0, cap).map(m => {
    const t = objs().get(m.ref);
    return `<div style="display:flex;gap:10px;align-items:baseline;margin:3px 0">
      <span class="mono" style="font-size:10px;color:var(--text-quiet);width:44px;text-align:right">${esc(m.sequence ?? "")}</span>
      <span>${t ? typeGlyph(t.type) + " " : ""}${refLink(m.ref, t ? labelOf(t) : m.ref)}</span></div>`;
  }).join("");
  return section(T("Members ({n})", { n: mem.length }) + (mem.length > cap ? " · " + T("first {n} shown", { n: cap }) : ""),
    rows || `<div class="hint">${esc(T("empty"))}</div>`);
}
function tailoringBody(o) {
  const sel = (o.selects || []).map(s => s["set-ref"] ? refLink(s["set-ref"]) : `<span class="mono">${esc(JSON.stringify(s.predicate))}</span>`).join("<br>");
  const ops = (o.operations || []).map(op => `<div class="stmt">
    <span class="badge" style="border-color:var(--amber);color:var(--amber)">${esc(op.op)}</span>
    ${op["statement-id"] ? badge(T("statement {id}", { id: op["statement-id"] })) : ""}${op.modality ? modBadge(op.modality) : ""}
    ${op.parameter ? badge(`⚙ ${op.parameter} = ${JSON.stringify(op.value)}`) : ""}
    ${op.deviation || op["deviation-ref"] ? `<span class="badge" style="border-color:var(--red);color:var(--red)">${esc(T("carries a Deviation"))}</span>` : ""}
    <div style="margin-top:5px">${refLink(op["requirement-ref"])}</div></div>`).join("");
  return section(T("Selects"), `<div>${sel || "—"}</div>`) +
    section(T("Excludes"), o.excludes ? prettyVal(o.excludes.map(e => ({ ...e }))) : "") +
    section(T("Operations ({n})", { n: (o.operations || []).length }), ops || `<div class="hint">—</div>`) +
    section(T("Deviations"), o.deviations ? prettyVal(o.deviations) : "");
}
function mappingBody(o) {
  const scope = s => (s || []).map(x => badge(x)).join("");
  return `<div class="kv">
    ${kv(T("source"), refLink(o["source-ref"]) + " " + scope(o["source-scope"]))}
    ${kv(T("relationship"), `<span class="badge" style="border-color:var(--teal);color:var(--teal)">${esc(o.relationship)}</span>`)}
    ${kv(T("target"), refLink(o["target-ref"]) + " " + scope(o["target-scope"]))}
    ${kv(T("direction"), esc(o.direction))}${kv(T("confidence"), badge(o.confidence))}
    ${o.rationale ? kv(T("rationale"), prettyVal(o.rationale)) : ""}
    ${kv(T("provenance"), esc(((o.provenance || {})["author-ref"] || "") + " · " + ((o.provenance || {}).date || "")))}</div>`;
}
/* A rating: the level, and the two inputs it was read from where stated. */
function ratingHtml(r) {
  if (!r) return "";
  const lv = x => `${badge(x.level)} <span class="hint mono">${esc(last(x["scale-ref"]))}</span>`;
  return `<div class="kv">${kv(T("level"), lv(r))}
    ${r.likelihood ? kv(T("likelihood"), lv(r.likelihood)) : ""}${r.impact ? kv(T("impact"), lv(r.impact)) : ""}
    ${r["override-rationale"] ? kv(T("override rationale"), prettyVal(r["override-rationale"])) : ""}</div>`;
}
function riskBody(o) {
  const refs = list => (list || []).map(u => `<div>${refLink(u)}</div>`).join("");
  const acc = o.acceptance;
  return `<div class="kv">${kv(T("state"), badge(o.state))}${kv(T("owner"), esc(o["owner-ref"]))}
      ${o.treatment ? kv(T("treatment"), badge(o.treatment)) : ""}
      ${o["shared-with-ref"] ? kv(T("shared with"), esc(o["shared-with-ref"])) : ""}
      ${o["review-due"] ? kv(T("review due"), prettyVal(o["review-due"], 1)) : ""}</div>` +
    section(T("Scenario"), `<div class="stmt">${langBlocks(o.scenario, "prose")}</div>`) +
    section(T("Rating"), ratingHtml(o.rating)) + section(T("Residual rating"), ratingHtml(o["residual-rating"])) +
    section(T("Treated by"), (o.treatments || []).map(t => `<div>${refLink(t["requirement-ref"])} ${(t["statement-ids"] || []).map(s => badge(T("statement {id}", { id: s }))).join("")}</div>`).join("")) +
    section(T("Acceptance"), acc ? `<div class="kv">${kv(T("approver"), esc(acc["approver-ref"]))}${kv(T("date"), esc(acc.date))}${kv(T("rationale"), prettyVal(acc.rationale))}</div>` : "") +
    section(T("Threats"), (o["threat-refs"] || []).map(u => badge(last(u), u)).join(" ")) +
    section(T("Components at risk"), refs(o["component-refs"])) + section(T("Belongs to the Tailorings"), refs(o["tailoring-refs"]));
}
/* A Check: the requirement it discharges, the fact contract, the comparisons
   that decide, and the collector code (shown, never run here). */
function checkBody(o) {
  const expected = e => (e && typeof e === "object" && !Array.isArray(e) ? `<span class="paramtok">{param:${esc(e.param)}}</span>` : `<span class="mono">${esc(JSON.stringify(e))}</span>`);
  const assertion = a => `<div class="mono" style="font-size:12px">${esc(a.fact)} <b>${esc(a.op)}</b> ${a.expected === undefined ? "" : expected(a.expected)}</div>`;
  const cols = (((o.facets || {})["https://ns.jascon.net/stdlib/facet/collector@1"] || {}).collectors) || [], p = o.provenance || {};
  return `<div class="kv">${kv(T("discharges"), (o["requirement-ref"] ? refLink(o["requirement-ref"]) : "") + (o["statement-ids"] || []).map(s => " " + badge(T("statement {id}", { id: s }))).join(""))}
      ${kv(T("platform"), esc(o.platform || ""))}${kv(T("confidence"), badge(o.confidence || "?"))}
      ${o.each ? kv(T("per resource"), esc(o.each.resource) + " " + badge(T(o.each["allow-empty"] ? "none observed passes" : "none observed is inconclusive"))) : ""}
      ${o.validity ? kv(T("fresh for"), esc(`${o.validity.num} ${o.validity.unit}`)) : ""}
      ${kv(T("author"), esc(p["author-ref"] || "") + (p.date ? " · " + esc(p.date) : ""))}</div>` +
    section(T("Facts the collector reports"), (o.observes || []).map(f => `<div>${badge(f.type + (f.cardinality === "many" ? "[]" : ""))} <span class="mono">${esc(f.name)}</span> <span class="hint">${esc(TT(f.description))}</span></div>`).join("")) +
    section(T("Applies when"), (o["applies-when"] || []).map(assertion).join("")) +
    section(T("Passes when all of these hold"), (o.criteria || []).map(assertion).join("")) +
    section(T("Collectors"), cols.map(c => `<div style="margin:6px 0">${badge(c.id)}${badge(c.runtime)}${c.privileges ? badge(c.privileges) : ""}<pre class="raw" style="max-height:240px">${esc(c.source)}</pre></div>`).join(""));
}
/* One capability of a Component: its id, the requirement and clauses it is
   about, the text, and the parameter values it suggests. A capability is a
   claim; nothing here says a requirement is met. `mark` is markup a page
   puts behind the id (added, changed, a verdict). */
function capabilityHtml(c, mark) {
  const req = c["requirement-ref"], bound = Object.entries(c["parameter-bindings"] || {});
  return `<div class="stmt"><div>${badge("⚙ " + c.id)}${mark || ""}
      ${req ? refLink(req, objs().has(req) ? labelOf(objs().get(req)) : req) : `<span class="hint">${esc(T("names no requirement"))}</span>`}
      ${(c["statement-ids"] || []).map(s => badge(T("statement {id}", { id: s }))).join("")}</div>
    ${typeof c.description === "string" ? `<div class="prose">${prose(c.description)}</div>` : c.description ? langBlocks(c.description, "prose") : ""}
    ${bound.length ? `<div class="hint" style="margin-top:4px">${esc(T("suggested values"))}: ${bound.map(([k, v]) => `<span class="paramtok">${esc(k)} = ${esc(JSON.stringify(v))}</span>`).join(" ")}</div>` : ""}</div>`;
}
/* A Component: what it is, the version of the product it describes, the
   product of somebody else it is about (a relation of type describes, shown
   and never computed with), its members, capabilities and authorizations. */
function componentBody(o) {
  const about = (o.relations || []).filter(r => r.type === JSC_DESCRIBES);
  return `<div class="kv">${kv(T("kind"), badge(o.kind || "?"))}
      ${o["product-version"] !== undefined ? kv(T("product version"), `<span class="mono">${esc(o["product-version"])}</span>`) : ""}
      ${about.map(r => kv(T("describes"), refLink(r.ref))).join("")}</div>` +
    section(T("Members ({n})", { n: (o.members || []).length }), (o.members || []).map(m =>
      `<div>${refLink(m["component-ref"], objs().has(m["component-ref"]) ? titleOf(objs().get(m["component-ref"])) : m["component-ref"])}${m.context ? ` <span class="hint">(${esc(m.context)})</span>` : ""}</div>`).join("")) +
    section(T("Capabilities ({n})", { n: (o.capabilities || []).length }), (o.capabilities || []).map(c => capabilityHtml(c)).join("")) +
    section(T("Authorizations"), o.authorizations ? prettyVal(o.authorizations) : "");
}
const GENERIC_SKIP = new Set(["id", "version", "label", "title", "lifecycle", "aliases", "relations", "facets", "annotations"]);
function genericBody(o) {
  const rest = Object.fromEntries(Object.entries(o).filter(([k]) => !GENERIC_SKIP.has(k)));
  return Object.keys(rest).length ? section(T("Fields"), prettyVal(rest)) : "";
}
const BODY = { requirement: requirementBody, requirementSet: setBody, tailoring: tailoringBody, mapping: mappingBody, component: componentBody, risk: riskBody, check: checkBody };

/* The whole object as markup. `verified` is the row jscVerify gave for it. */
function objectHtml(r, verified) {
  const o = r.obj, view = TYPE_VIEW[r.type];
  const head = `<div style="margin-bottom:10px">${typeBadge(r.type)}${badge(o.lifecycle || "?")}${o.label ? badge(o.label) : ""}${badge("v " + (o.version || "?"))}
      ${r.origin === "authored" ? `<span class="badge" style="border-color:var(--amber);color:var(--amber)">${esc(T("edited in this app"))}</span>` : ""}
      ${r.origin === "pack" ? `<span class="badge" style="border-color:var(--green);color:var(--green)">${esc(T("from an advice pack"))}</span>` : ""}</div>
    <h3 style="font-size:15px;margin-bottom:2px">${esc(titleOf(r))}</h3>
    <div class="mono" style="font-size:10.5px;color:var(--text-quiet);word-break:break-all">${esc(o.id)}</div>
    <div class="hint" style="margin-top:6px">${esc(T(view.what))}</div>`;
  const facets = o.facets ? section(T("Facets (registered extensions, schema-pinned)"), Object.entries(o.facets).map(([fid, payload]) => {
    const inner = payload && payload["by-statement"]
      ? `<div class="hint" style="margin-bottom:4px">${esc(T("keyed by statement"))}</div>` +
        Object.entries(payload["by-statement"]).map(([sid, pv]) => `<div style="margin:6px 0">${badge(T("statement {id}", { id: sid }))}${prettyVal(pv, 1)}</div>`).join("")
      : prettyVal(payload, 1);
    return `<div class="facetbox"><div class="mono" style="font-size:10.5px;color:var(--accent);margin-bottom:6px">${esc(fid)}</div>${inner}</div>`;
  }).join("")) : "";
  const mark = ok => verified ? (ok ? ` <span class="verdict-ok">✓</span>` : ` <span class="verdict-bad">✗</span>`) : "";
  const digests = r.entry ? section(T("Integrity (from the manifest)"), `<div class="kv">
      ${kv("package-digest", `<span class="mono" style="font-size:10.5px">${esc(r.entry["package-digest"])}</span>${mark(verified && verified.pkg)}`)}
      ${kv("semantic-digest", `<span class="mono" style="font-size:10.5px">${esc(r.entry["semantic-digest"])}</span>${mark(verified && verified.sem)}`)}</div>`) : "";
  return head + (BODY[r.type] || genericBody)(o) +
    section(T("Aliases"), o.aliases ? o.aliases.map(a => badge(`${a.scheme}: ${a.value}`)).join(" ") : "") +
    section(T("Relations"), o.relations ? `<div class="kv">${o.relations.map(rel => kv(rel.type, refLink(rel.ref))).join("")}</div>` : "") +
    facets + section(T("Annotations (not part of the signed meaning)"), o.annotations ? `<div class="annbox">${prettyVal(o.annotations, 1)}</div>` : "") +
    digests + `<details style="margin-top:12px"><summary>${esc(T("raw JSON"))}</summary><pre class="raw">${esc(JSON.stringify(o, null, 1))}</pre></details>`;
}

/* ---------- drawer ---------- */
function openDrawer(id) {
  const r = objs().get(id);
  if (!r) return;
  let d = document.getElementById("jsc-drawer");
  if (!d) {
    d = document.createElement("aside");
    d.id = "jsc-drawer"; d.setAttribute("role", "dialog"); d.setAttribute("aria-modal", "false");
    d.style.cssText = "position:fixed;top:0;right:0;bottom:0;width:min(560px,92vw);z-index:60;overflow-y:auto;padding:16px 18px;" +
      "background:var(--bg-pop);border-left:1px solid var(--border-2);box-shadow:-12px 0 40px oklch(0 0 0 / .35)";
    document.body.appendChild(d);
    document.addEventListener("keydown", e => { if (e.key === "Escape") d.classList.add("hidden"); });
  }
  d.classList.remove("hidden");
  d.innerHTML = `<div style="display:flex;justify-content:flex-end;margin-bottom:6px"><button type="button" class="small" id="jsc-drawer-close">✕ ${esc(T("Close"))}</button></div>` + objectHtml(r);
  d.querySelector("#jsc-drawer-close").addEventListener("click", () => d.classList.add("hidden"));
  wireRefs(d);
  d.scrollTop = 0;
  d.querySelector("#jsc-drawer-close").focus();
}

/* ---------- picker: find an object of given types by typing ---------- */
const pickerHtml = (id, placeholder) =>
  `<span class="picker"><input type="text" id="${id}" placeholder="${esc(placeholder)}" autocomplete="off"><div class="sugg hidden" id="${id}-sugg"></div></span>`;
function wirePicker(root, id, types, onPick) {
  const inp = root.querySelector("#" + id), sugg = root.querySelector("#" + id + "-sugg");
  if (!inp) return;
  inp.addEventListener("input", () => {
    const q = inp.value.toLowerCase();
    if (q.length < 2) { sugg.classList.add("hidden"); return; }
    const hits = [];
    for (const oid of jscSet.graph.order) {
      const r = objs().get(oid);
      if (types.includes(r.type) && (oid.toLowerCase().includes(q) || (r.obj.label || "").toLowerCase().includes(q) || TT(r.obj.title).toLowerCase().includes(q))) hits.push(r);
      if (hits.length === 12) break;
    }
    sugg.innerHTML = hits.map(r => `<div data-pick="${esc(r.obj.id)}">${typeGlyph(r.type)} ${esc(labelOf(r))}<div class="s">${esc(r.obj.id)}</div></div>`).join("") ||
      `<div class="s" style="padding:6px 10px">${esc(T("no match"))}</div>`;
    sugg.classList.remove("hidden");
    sugg.querySelectorAll("[data-pick]").forEach(d => d.addEventListener("mousedown", e => {
      e.preventDefault(); sugg.classList.add("hidden"); inp.value = ""; onPick(d.dataset.pick);
    }));
  });
  inp.addEventListener("blur", () => setTimeout(() => sugg.classList.add("hidden"), 200));
}

/* ---------- charts (plain SVG and CSS) ---------- */
function donut(slices, caption, size = 160) {
  const total = slices.reduce((s, x) => s + x.value, 0);
  if (!total) return "";
  const c = size / 2, r = c - 8, ri = r * 0.6;
  let a = -Math.PI / 2;
  const paths = slices.filter(s => s.value > 0).map(s => {
    const sweep = (s.value / total) * Math.PI * 2, a1 = a, a2 = a + sweep * 0.99999;
    a += sweep;
    const pt = (rad, ang) => `${c + rad * Math.cos(ang)} ${c + rad * Math.sin(ang)}`, large = sweep > Math.PI ? 1 : 0;
    return `<path d="M ${pt(r, a1)} A ${r} ${r} 0 ${large} 1 ${pt(r, a2)} L ${pt(ri, a2)} A ${ri} ${ri} 0 ${large} 0 ${pt(ri, a1)} Z" fill="${s.color}"><title>${esc(s.label)}: ${s.value}</title></path>`;
  }).join("");
  return `<svg viewBox="0 0 ${size} ${size}" width="${size}" height="${size}" role="img" aria-label="${esc(caption)}: ${total}">${paths}
    <text x="${c}" y="${c - 2}" text-anchor="middle" dominant-baseline="central" fill="currentColor" font-size="22" font-weight="600">${total}</text>
    <text x="${c}" y="${c + 18}" text-anchor="middle" fill="currentColor" opacity="0.55" font-size="9" letter-spacing="1.5">${esc(caption.toUpperCase())}</text></svg>`;
}
function hbars(items) {
  const max = Math.max(1, ...items.map(i => i.value));
  return items.map(i => `<div class="hbar-row"><div class="hbar-label" title="${esc(i.title || i.label)}">${esc(i.label)}</div>
    <div class="hbar-track"><div class="hbar-fill" style="width:${(i.value / max) * 100}%;background:${i.color}"></div></div>
    <div class="hbar-value">${i.value}</div></div>`).join("");
}

/* ---------- filter dimensions ----------
   Every kernel field and facet value of the requirements that behaves like a
   vocabulary becomes a filter. A dimension is a vocabulary when its values
   repeat over a bounded space: at most 12 distinct values, or at most 100
   with every value used 1.5 times on average. Free text never repeats and is
   left out; the log says which dimensions were left out. The bounds were
   measured on the shipped corpora (see the reader this derives from).
   -> { reqDims: Map(id -> Map(dim -> Set(value))), usable: [[dim, Map(value -> count)]], sets } */
const dimCache = new WeakMap();
function collectDims(obj) {
  const out = [];
  const scalar = v => (typeof v === "string" || typeof v === "number" || typeof v === "boolean") && String(v).length <= 80;
  out.push(["lifecycle", obj.lifecycle]);
  for (const s of obj.statements || []) {
    out.push(["modality", s.modality]);
    for (const p of s["obligated-parties"] || []) out.push(["party", last(p)]);
  }
  const walk = (name, payload, depth) => {
    if (!payload || typeof payload !== "object" || depth > 2) return;
    for (const [k, v] of Object.entries(payload)) {
      if (/^[a-z]{2}(-[A-Z]{2})?$/.test(k)) continue;   // a language tag: prose, never a vocabulary
      if (k === "by-statement" && v && typeof v === "object") { for (const sub of Object.values(v)) walk(name, sub, depth + 1); }
      else if (scalar(v)) out.push([name + "." + k, String(v)]);
      else if (Array.isArray(v)) { for (const x of v) if (scalar(x)) out.push([name + "." + k, String(x)]); }
      else if (v && typeof v === "object" && depth < 2) walk(name + "." + k, v, depth + 1);
    }
  };
  for (const [fid, payload] of Object.entries(obj.facets || {})) walk(last(fid).replace(/@[0-9]+$/, ""), payload, 0);
  return out;
}
function dimIndex() {
  const g = jscSet.graph;
  if (dimCache.has(g)) return dimCache.get(g);
  const reqDims = new Map(), dims = new Map();
  for (const r of g.objects.values()) {
    if (r.type !== "requirement") continue;
    const mine = new Map();
    for (const [k, v] of collectDims(r.obj)) {
      if (!mine.has(k)) mine.set(k, new Set());
      mine.get(k).add(v);
      if (!dims.has(k)) dims.set(k, new Map());
      dims.get(k).set(v, (dims.get(k).get(v) || 0) + 1);
    }
    reqDims.set(r.obj.id, mine);
  }
  const KERNEL = ["modality", "lifecycle", "party"], dropped = [];
  const uses = vals => [...vals.values()].reduce((a, b) => a + b, 0);
  const usable = [...dims.entries()].filter(([k, vals]) => {
    const total = uses(vals);
    const ok = total >= 2 && (vals.size <= 12 || (total / vals.size >= 1.5 && vals.size <= 100));
    if (!ok && total >= 2) dropped.push(`${k} (${vals.size}/${total})`);
    return ok;
  }).sort((a, b) => {
    const ka = KERNEL.indexOf(a[0]) >= 0, kb = KERNEL.indexOf(b[0]) >= 0;
    return ka !== kb ? (ka ? -1 : 1) : uses(b[1]) - uses(a[1]);
  });
  const sets = [...g.objects.values()].filter(r => r.type === "requirementSet")
    .map(r => ({ id: r.obj.id, title: titleOf(r) })).sort((a, b) => a.title.localeCompare(b.title)).slice(0, 200);
  const idx = { reqDims, usable, sets, setCache: new Map() };
  dimCache.set(g, idx);
  if (usable.length) jscLog.debug(T("{n} dimensions offered as filters: {list}", { n: usable.length, list: usable.map(u => u[0]).join(", ") }));
  if (dropped.length) jscLog.debug(T("not offered as filters (free text, values do not repeat): {list}", { list: dropped.join(" · ") }));
  return idx;
}
const dimOptLabel = v => { const s = /^https?:\/\//.test(v) ? last(v) : v; return s.length > 44 ? s.slice(0, 42) + "…" : s; };
/* f: { q, set, dims: {dim: value} } */
function reqMatches(id, f, idx) {
  const r = objs().get(id);
  if (!r || r.type !== "requirement") return false;
  if (f.q) {
    const q = f.q.toLowerCase();
    if (!id.toLowerCase().includes(q) && !(r.obj.label || "").toLowerCase().includes(q) && !TT(r.obj.title).toLowerCase().includes(q)) return false;
  }
  if (f.set) {
    if (!idx.setCache.has(f.set)) idx.setCache.set(f.set, jscExpandRefs([f.set], objs()));
    if (!idx.setCache.get(f.set).has(id)) return false;
  }
  for (const [k, v] of Object.entries(f.dims || {})) {
    if (v && !((idx.reqDims.get(id) || new Map()).get(k) || new Set()).has(v)) return false;
  }
  return true;
}

/* ---------- a page's draft ----------
   What a workbench holds before it becomes an object: kept in localStorage
   per tool and set, so a reload does not lose it. Not a secret, not part of
   the bundle. */
function draft(tool, initial) {
  const key = () => `jsc:cfg:draft:${tool}:${jscStore.activeSet()}`;
  let data;
  try { data = JSON.parse(localStorage.getItem(key())) || initial(); } catch (e) { data = initial(); }
  return {
    get data() { return data; },
    save() { localStorage.setItem(key(), JSON.stringify(data)); },
    reset() { data = initial(); this.save(); },
  };
}

window.jscView = {
  TYPE_VIEW, MODALITY_COLOR, VERDICT_CLASS, onOpen: null,
  open(id) { (this.onOpen || openDrawer)(id); },
  last, labelOf, titleOf, typeGlyph, typeBadge, badge, modBadge, refLink, wireRefs, prose, langBlocks, kv, prettyVal, section,
  objectHtml, capabilityHtml, pickerHtml, wirePicker, donut, hbars, dimIndex, dimOptLabel, reqMatches, draft,
};

})();
