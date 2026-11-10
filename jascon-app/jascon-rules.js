/* JASCON-App kernel rules.

   The computations of the JASCON kernel that the pages need, ported from the
   Python reference validator (jascon/scripts/validate_core.py). The Python
   file is the reference; where the two disagree, this file is wrong. The
   conformance vectors under jascon/conformance/ are run against this file by
   tests/rules.test.mjs, so a disagreement shows as a failing test.

   Everything here is a function of plain data. Nothing touches the DOM or
   storage, and the file runs in node as it is. A page loads it after
   jascon-core.js, whose jscSemanticDigest and jscInferType it uses.

   The argument `objs` is always a Map of id -> {type, obj}; a graph's
   `objects` map from jascon-core.js fits as it is.

   Ported so far: the modality lattice (B.1.6), the parameter law, Set
   expansion and a Tailoring's selection, the tier of a Tailoring in
   structural mode, the resolution of a Tailoring's operations, the state
   machines of Finding, Deviation and Risk, and relationship composition. Not yet
   ported: schema matching, reference closure, the operation law per tier,
   facet payloads, conditional-apply, composition, DSSE verification, the Risk
   rules, risk coverage and the scale rules. Until they are, the Python
   validator is the only check that a bundle is valid. */
"use strict";

/* In a browser the core's functions are globals; in node they are required. */
const jscRulesCore = (typeof module !== "undefined" && module.exports) ? require("./jascon-core.js") : null;
const jscRulesSemanticDigest = jscRulesCore ? jscRulesCore.jscSemanticDigest : obj => jscSemanticDigest(obj);

/* ---------- modality lattice (B.1.6) ----------
   Two chains above `unspecified`: obligation (may < should < must) and
   prohibition (should-not < must-not). Moving up a chain is monotone, moving
   down is an easing, changing chains is an axis change. `may-only` sits
   beside `may`. */
const JSC_MODALITIES = ["must", "should", "may", "may-only", "should-not", "must-not", "unspecified"];
const JSC_OBL = { unspecified: 0, may: 1, should: 2, must: 3 };
const JSC_PRO = { unspecified: 0, "should-not": 1, "must-not": 2 };
function jscModalityVerdict(from, to) {
  if (from === to) return "monotone";
  if (from === "unspecified") return "monotone";
  if (to === "unspecified") return "easing";
  if (from === "may" && to === "may-only") return "monotone";
  if (from === "may-only" && to === "may") return "easing";
  if (from === "may-only" || to === "may-only") return "axis-change";
  if (from in JSC_OBL && to in JSC_OBL) return JSC_OBL[to] >= JSC_OBL[from] ? "monotone" : "easing";
  if (from in JSC_PRO && to in JSC_PRO) return JSC_PRO[to] >= JSC_PRO[from] ? "monotone" : "easing";
  return "axis-change";
}

/* ---------- parameter law ----------
   -> "valid" | "deviation-required" | "invalid". A value outside the declared
   space needs a Deviation; a value of the wrong kind is invalid and no
   Deviation helps. */
const JSC_DECIMAL_RE = /^(-?[1-9][0-9]*(\.[0-9]+)?|0(\.[0-9]+)?|-0\.[0-9]*[1-9][0-9]*)$/;
const JSC_ELAPSED_UNITS = ["seconds", "minutes", "hours"];
const JSC_CALENDAR_UNITS = ["days", "bizdays", "weeks", "months", "years"];
/* Compares two canonical decimal strings exactly (no float): -1, 0 or 1. */
function jscDecimalCompare(a, b) {
  const parse = s => {
    const neg = s.startsWith("-"), [int, frac = ""] = s.replace("-", "").split(".");
    return { neg, int, frac };
  };
  const x = parse(String(a)), y = parse(String(b));
  const scale = Math.max(x.frac.length, y.frac.length);
  const big = v => BigInt(v.int + v.frac.padEnd(scale, "0")) * (v.neg ? -1n : 1n);
  const d = big(x) - big(y);
  return d < 0n ? -1 : d > 0n ? 1 : 0;
}
function jscParamCheck(decl, value) {
  const t = decl.type;
  if (t === "calendar-period" && !("calendar-ref" in decl)) return "invalid";
  if (value === null || value === undefined) return "invalid";
  if (t === "choice") {
    const allowed = (decl.choices || []).map(c => c.value);
    if (Array.isArray(value)) {
      // a list is legal only on cardinality `many`, and every element is declared
      if (decl.cardinality !== "many" || !value.length) return "invalid";
      return value.every(v => allowed.includes(v)) ? "valid" : "deviation-required";
    }
    return allowed.includes(value) ? "valid" : "deviation-required";
  }
  if (t === "integer") {
    if (typeof value !== "number" || !Number.isInteger(value)) return "invalid";
    if ("min" in decl && value < decl.min) return "deviation-required";
    if ("max" in decl && value > decl.max) return "deviation-required";
    return "valid";
  }
  if (t === "decimal") {
    if (typeof value !== "string" || !JSC_DECIMAL_RE.test(value)) return "invalid";
    if ("min" in decl && jscDecimalCompare(value, decl.min) < 0) return "deviation-required";
    if ("max" in decl && jscDecimalCompare(value, decl.max) > 0) return "deviation-required";
    return "valid";
  }
  if (t === "elapsed-duration" || t === "calendar-period") {
    if (!value || typeof value !== "object" || !("num" in value) || !("unit" in value)) return "invalid";
    const units = t === "elapsed-duration" ? JSC_ELAPSED_UNITS : JSC_CALENDAR_UNITS;
    if (!units.includes(value.unit)) return "invalid";   // elapsed against calendar is a semantic boundary
    if (decl.tightening === "lower" && decl.num != null && value.unit === decl.unit && value.num > decl.num) {
      return "deviation-required";
    }
    return "valid";
  }
  return "valid";
}

/* ---------- Sets and selection ---------- */
/* ids -> Set of Requirement ids, through nested Sets to any depth. The seen
   set makes a malformed cycle terminate. */
function jscExpandRefs(refs, objs) {
  const out = new Set(), seen = new Set(), stack = [...refs];
  while (stack.length) {
    const id = stack.pop();
    if (seen.has(id)) continue;
    seen.add(id);
    const tgt = objs.get(id);
    if (!tgt) continue;
    if (tgt.type === "requirementSet") stack.push(...(tgt.obj.members || []).map(m => m.ref));
    else if (tgt.type === "requirement") out.add(id);
  }
  return out;
}
/* Map of Set id -> ids of the Sets that list it as a member */
function jscSetParents(objs) {
  const parents = new Map();
  for (const r of objs.values()) {
    if (r.type !== "requirementSet") continue;
    for (const m of r.obj.members || []) {
      const t = objs.get(m.ref);
      if (t && t.type === "requirementSet") parents.set(m.ref, [...(parents.get(m.ref) || []), r.obj.id]);
    }
  }
  return parents;
}
/* A Tailoring's selection -> { selected: Set of Requirement ids, open, notes }.
   set-refs are expanded to any depth; an exclude names a Requirement or a
   Set, and a Set excludes its members; a withdrawn Requirement is not in
   force and is dropped. A predicate select is not evaluated here, so its
   presence makes the selection OPEN: the ids are a lower bound, and nothing
   may be concluded from a requirement's absence. */
function jscSelection(tobj, objs) {
  const notes = [];
  const isSet = id => (objs.get(id) || {}).type === "requirementSet";
  const selects = tobj.selects || [];
  const selected = jscExpandRefs(selects.filter(s => "set-ref" in s && isSet(s["set-ref"])).map(s => s["set-ref"]), objs);
  const open = selects.some(s => !("set-ref" in s));
  if (open) notes.push(`${tobj.id}: predicate select not expanded (engine-resolved) - the selection is a lower bound`);
  for (const id of jscExpandRefs((tobj.excludes || []).map(e => e.ref), objs)) selected.delete(id);
  const gone = [...selected].filter(id => objs.get(id).obj.lifecycle === "withdrawn").sort();
  if (gone.length) {
    notes.push(`${tobj.id}: ${gone.length} selected requirement(s) are withdrawn and not counted (first: ${gone[0]})`);
    gone.forEach(id => selected.delete(id));
  }
  return { selected, open, notes };
}

/* ---------- tier of a Tailoring (structural mode) ----------
   Content origin resolves through selected Sets to their members and through
   operation targets: a self-minted wrapper Set around foreign content must
   not turn a consumer into an authority. One origin that is also the
   Tailoring's own is authority-claimed; an in-bundle Attestation by that
   origin whose subjects include the Tailoring, digest-matched, makes it
   authority-proven. Signatures are not verified here. */
function jscUriOrigin(u) {
  const s = String(u), p = s.split("/");
  return s.startsWith("http") && p.length >= 3 ? p.slice(0, 3).join("/") : s;
}
async function jscDeriveTier(tobj, objs) {
  const origins = new Set();
  const memberOrigins = (sid, depth) => {
    const tgt = objs.get(sid);
    if (depth > 4 || !tgt || tgt.type !== "requirementSet" || !(tgt.obj.members || []).length) { origins.add(jscUriOrigin(sid)); return; }
    for (const m of tgt.obj.members) {
      const mt = objs.get(m.ref);
      if (mt && mt.type === "requirementSet") memberOrigins(m.ref, depth + 1);
      else origins.add(jscUriOrigin(m.ref));
    }
  };
  for (const s of tobj.selects || []) {
    if ("set-ref" in s) memberOrigins(s["set-ref"], 0); else origins.add("<predicate>");
  }
  for (const op of tobj.operations || []) origins.add(jscUriOrigin(op["requirement-ref"] || ""));
  origins.delete("");
  const origin = origins.size === 1 && !origins.has("<predicate>") ? [...origins][0] : null;
  const claimed = origin !== null && jscUriOrigin(tobj.id) === origin;
  if (origin) {
    let digest = null;
    for (const r of objs.values()) {
      if (r.type !== "attestation" || jscUriOrigin(r.obj.signer || "") !== origin) continue;
      for (const subj of r.obj["subject-semantic-digests"] || []) {
        if (!subj || typeof subj !== "object" || subj.id !== tobj.id) continue;
        digest = digest || await jscRulesSemanticDigest(tobj);
        if (subj["semantic-digest"] === digest) return "authority-proven";
      }
    }
  }
  return claimed ? "authority-claimed" : "consumer";
}

/* ---------- resolving a Tailoring (Appendix B, steps 3 and 4) ----------
   Operations are applied in list order to deep copies of the requirements
   they name. Two operations on one target in one Tailoring are an error;
   an override happens by chaining Tailorings, never silently.
   -> { selected, open, resolved: Map(id -> changed copy),
        touched: Map(id -> [{what, from, to, verdict?}]), errors, notes }
   Applied here: set-modality, set-parameter, replace-prose. An operation of
   another kind is reported in `errors`, so that a resolution with a gap is
   never mistaken for a complete one. */
const jscTargetKey = op => [op["requirement-ref"], op["statement-id"], op.parameter, op.field, op.facet].join("|");
function jscResolveTailoring(tobj, objs) {
  const { selected, open, notes } = jscSelection(tobj, objs);
  const resolved = new Map(), touched = new Map(), errors = [], seen = new Set();
  for (const op of tobj.operations || []) {
    const key = jscTargetKey(op);
    if (seen.has(key)) { errors.push(`same-target conflict on ${key}`); continue; }
    seen.add(key);
    const base = objs.get(op["requirement-ref"]);
    if (!base || base.type !== "requirement") { errors.push(`operation targets unknown requirement ${op["requirement-ref"]}`); continue; }
    if (!resolved.has(base.obj.id)) resolved.set(base.obj.id, JSON.parse(JSON.stringify(base.obj)));
    const copy = resolved.get(base.obj.id);
    const stmt = (copy.statements || []).find(s => s.id === op["statement-id"]);
    if (!stmt) { errors.push(`operation targets unknown statement ${op["statement-id"]} of ${copy.id}`); continue; }
    const log = touched.get(copy.id) || [];
    touched.set(copy.id, log);
    if (op.op === "set-modality") {
      log.push({ what: "modality", statement: stmt.id, from: stmt.modality, to: op.modality,
        verdict: jscModalityVerdict(stmt.modality, op.modality) });
      stmt.modality = op.modality;
    } else if (op.op === "set-parameter") {
      const p = (stmt.parameters || []).find(x => x.name === op.parameter);
      if (!p) { errors.push(`operation sets unknown parameter ${op.parameter} of ${copy.id} ${stmt.id}`); continue; }
      const before = p.default !== undefined ? p.default : (p.num !== undefined ? { num: p.num, unit: p.unit } : null);
      log.push({ what: "parameter", statement: stmt.id, parameter: op.parameter, from: before, to: op.value });
      if (op.value && typeof op.value === "object" && !Array.isArray(op.value) && op.value.num !== undefined) { p.num = op.value.num; p.unit = op.value.unit; }
      else p.default = op.value;
    } else if (op.op === "replace-prose") {
      const lang = Object.keys(op.prose || {})[0];
      log.push({ what: "prose", statement: stmt.id, lang, intent: op.intent, from: stmt.prose[lang], to: op.prose[lang] });
      Object.assign(stmt.prose, op.prose);
    } else {
      errors.push(`operation ${op.op} on ${copy.id} is not applied by this app`);
    }
  }
  return { selected, open, resolved, touched, errors, notes };
}

/* ---------- state machines (C.3) ----------
   A state moves only along these edges. Terminal states are terminal: a
   closed Finding that recurs is a new Finding, a decided Deviation that is
   reopened is a new Deviation, a retired Risk stays retired. A Risk may skip
   forward (identified to treated), never back. */
const JSC_NEXT = {
  finding: { open: ["in-remediation", "closed"], "in-remediation": ["closed"], closed: [] },
  deviation: { investigating: ["pending", "withdrawn"], pending: ["approved", "withdrawn"], approved: [], withdrawn: [] },
  risk: { identified: ["assessed", "treated", "retired"], assessed: ["treated", "retired"], treated: ["retired"], retired: [] },
};
const jscCanMove = (machine, from, to) => ((JSC_NEXT[machine] || {})[from] || []).includes(to);

/* Composing two mapping relationships along a chain (C.5), at the
   conformance floor: only equal chains at full strength, everything else
   degrades to supports, and supplements does not chain at all (null). */
function jscComposeRelationship(a, b) {
  if (a === "supplements" || b === "supplements") return null;
  if (a === "equal") return b;
  if (b === "equal") return a === "supports" ? a : "supports";
  return "supports";
}

/* ---------- authoring helper ----------
   Kernel prose is a language map. A page collects plain strings; this wraps
   the fields that are text in the kernel into {lang: string}, in place. */
function jscTextify(o, lang) {
  const wrap = (c, k) => { if (c && typeof c[k] === "string") c[k] = { [lang]: c[k] }; };
  wrap(o, "title"); wrap(o, "rationale"); wrap(o, "scenario");
  wrap(o.acceptance, "rationale"); wrap(o.rating, "override-rationale"); wrap(o["residual-rating"], "override-rationale");
  (o.excludes || []).forEach(e => wrap(e, "rationale"));
  (o.capabilities || []).forEach(c => wrap(c, "description"));
  (o.actions || []).forEach(a => wrap(a, "description"));
  (o.deviations || []).forEach(d => wrap(d, "rationale"));
  (o.operations || []).forEach(op => wrap(op.deviation, "rationale"));
  return o;
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { JSC_MODALITIES, JSC_ELAPSED_UNITS, JSC_CALENDAR_UNITS, jscModalityVerdict, jscParamCheck,
    jscDecimalCompare, jscExpandRefs, jscSetParents, jscSelection, jscUriOrigin, jscDeriveTier, jscTargetKey,
    jscResolveTailoring, jscTextify, JSC_NEXT, jscCanMove, jscComposeRelationship };
}
