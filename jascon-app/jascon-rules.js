/* JASCON-App kernel rules.

   The computations of the JASCON kernel that the pages need, ported from the
   Python reference validator (jascon/scripts/validate_core.py). The Python
   file is the reference; where the two disagree, this file is wrong. The
   conformance vectors under jascon/conformance/ are run against this file by
   tests/rules.test.mjs, so a disagreement shows as a failing test.

   Everything here is a function of plain data. Nothing touches the DOM or
   storage, and the file runs in node as it is.

   The argument `objs` is always a Map of id -> {type, obj}; a graph's
   `objects` map from jascon-core.js fits as it is.

   Ported, each run against its vector family: the canonical form's rule on
   empty containers, the modality lattice (B.1.6), the parameter law, Set
   expansion and a Tailoring's selection, the tier of a Tailoring in
   structural mode, the operation law per tier, the resolution of a
   Tailoring's operations, the state machines, relationship composition,
   schema matching (which type an object is), the checks of one object,
   reference closure with typed edges and the acyclic Set graph, the kernel
   pin, facet payloads, the bi-modal attestation verdict, the Risk rules
   RISK-1 to RISK-14 with risk coverage, and the scale and matrix rules
   SCALE-1 to SCALE-4. jscCheckGraph runs them over a whole set.

   Not ported: conditional-apply, the composition of two bundles, and DSSE
   signature verification. A set that passes here has not been checked for
   those; the Python validator has them. tests/rules.test.mjs names the
   vector families still missing.

   A page loads jascon-core.js, jascon-schema.js (generated from the kernel
   schema) and then this file. */
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

/* ====================================================================
   Schema matching
   ====================================================================
   The kernel has no type field: an object is of the type whose schema it
   matches, and it must match exactly one. This is a JSON Schema checker for
   the keywords the kernel schema and the stdlib facets use, plus the plain
   bounds a pinned facet schema is likely to add: $ref, type, const, enum,
   minLength, maxLength, pattern, minimum, maximum, minItems, maxItems,
   uniqueItems, items, required, minProperties, maxProperties,
   propertyNames, properties, additionalProperties, allOf, anyOf, oneOf, not,
   if/then/else and unevaluatedProperties. A schema that uses another
   keyword is refused loudly instead of being half-checked.
   -> { errors: [{path, keyword, message}], evaluated: Set of property names } */
const JSC_SCHEMA_KEYWORDS = new Set(["$ref", "$schema", "$id", "$defs", "title", "description", "note", "type", "const", "enum",
  "minLength", "maxLength", "pattern", "minimum", "maximum", "minItems", "maxItems", "uniqueItems", "items", "required",
  "minProperties", "maxProperties", "propertyNames", "properties", "additionalProperties", "allOf", "anyOf", "oneOf", "not",
  "if", "then", "else", "unevaluatedProperties", "contentEncoding"]);
const jscRulesSchema = (typeof module !== "undefined" && module.exports) ? require("./jascon-schema.js") : { JSC_SCHEMA, JSC_STDLIB };
const jscRegexCache = new Map();
const jscRegex = p => { if (!jscRegexCache.has(p)) jscRegexCache.set(p, new RegExp(p)); return jscRegexCache.get(p); };
const jscIsPlainObject = v => v !== null && typeof v === "object" && !Array.isArray(v);
function jscTypeMatches(type, v) {
  switch (type) {
    case "string": return typeof v === "string";
    case "boolean": return typeof v === "boolean";
    case "number": return typeof v === "number";
    case "integer": return typeof v === "number" && Number.isInteger(v);
    case "array": return Array.isArray(v);
    case "object": return jscIsPlainObject(v);
    case "null": return v === null;
    default: throw new Error(`schema type ${type} is not supported`);
  }
}
function jscSchemaCheck(schema, v, root, path = "") {
  const errors = [], evaluated = new Set();
  if (schema === true) return { errors, evaluated };
  const fail = (keyword, message) => errors.push({ path, keyword, message });
  if (schema === false) { fail("false", "nothing is allowed here"); return { errors, evaluated }; }
  for (const k of Object.keys(schema)) if (!JSC_SCHEMA_KEYWORDS.has(k)) throw new Error(`schema keyword ${k} is not supported`);
  const sub = (s, value, p) => jscSchemaCheck(s, value, root, p);
  const merge = r => { errors.push(...r.errors); r.evaluated.forEach(k => evaluated.add(k)); };
  if (schema.$ref) {
    const m = /^#\/\$defs\/(.+)$/.exec(schema.$ref);
    if (!m || !root.$defs || !root.$defs[m[1]]) throw new Error(`schema reference ${schema.$ref} does not resolve`);
    merge(sub(root.$defs[m[1]], v, path));
  }
  if ("type" in schema && !jscTypeMatches(schema.type, v)) fail("type", `is not of type ${schema.type}`);
  if ("const" in schema && v !== schema.const) fail("const", `is not ${JSON.stringify(schema.const)}`);
  if (schema.enum && !schema.enum.includes(v)) fail("enum", `is not one of ${JSON.stringify(schema.enum)}`);
  if (typeof v === "string") {
    if ("minLength" in schema && [...v].length < schema.minLength) fail("minLength", "is too short");
    if ("maxLength" in schema && [...v].length > schema.maxLength) fail("maxLength", "is too long");
    if ("pattern" in schema && !jscRegex(schema.pattern).test(v)) fail("pattern", `does not match ${schema.pattern}`);
  }
  if (typeof v === "number" && "minimum" in schema && v < schema.minimum) fail("minimum", `is less than ${schema.minimum}`);
  if (typeof v === "number" && "maximum" in schema && v > schema.maximum) fail("maximum", `is more than ${schema.maximum}`);
  if (Array.isArray(v)) {
    if ("minItems" in schema && v.length < schema.minItems) fail("minItems", `has fewer than ${schema.minItems} item(s)`);
    if ("maxItems" in schema && v.length > schema.maxItems) fail("maxItems", `has more than ${schema.maxItems} item(s)`);
    if (schema.uniqueItems && new Set(v.map(x => JSON.stringify(x))).size !== v.length) fail("uniqueItems", "has an item twice");
    if ("items" in schema) v.forEach((x, i) => errors.push(...sub(schema.items, x, `${path}/${i}`).errors));
  }
  if (jscIsPlainObject(v)) {
    for (const k of schema.required || []) if (!(k in v)) fail("required", `'${k}' is a required property`);
    if ("minProperties" in schema && Object.keys(v).length < schema.minProperties) fail("minProperties", "has too few properties");
    if ("maxProperties" in schema && Object.keys(v).length > schema.maxProperties) fail("maxProperties", "has too many properties");
    if ("propertyNames" in schema) for (const k of Object.keys(v)) errors.push(...sub(schema.propertyNames, k, `${path}/${k}`).errors);
    const props = schema.properties || {};
    for (const k of Object.keys(props)) if (k in v) { errors.push(...sub(props[k], v[k], `${path}/${k}`).errors); evaluated.add(k); }
    if ("additionalProperties" in schema) {
      for (const k of Object.keys(v)) {
        if (k in props) continue;
        evaluated.add(k);
        if (schema.additionalProperties === false) fail("additionalProperties", `'${k}' is not allowed`);
        else errors.push(...sub(schema.additionalProperties, v[k], `${path}/${k}`).errors);
      }
    }
  }
  for (const s of schema.allOf || []) merge(sub(s, v, path));
  if (schema.anyOf) {
    const passing = schema.anyOf.map(s => sub(s, v, path)).filter(r => !r.errors.length);
    if (!passing.length) fail("anyOf", "matches none of the allowed shapes");
    passing.forEach(r => r.evaluated.forEach(k => evaluated.add(k)));
  }
  if (schema.oneOf) {
    const passing = schema.oneOf.map(s => sub(s, v, path)).filter(r => !r.errors.length);
    if (passing.length !== 1) fail("oneOf", `matches ${passing.length} of the shapes of which exactly one is allowed`);
    passing.forEach(r => r.evaluated.forEach(k => evaluated.add(k)));
  }
  if ("not" in schema && !sub(schema.not, v, path).errors.length) fail("not", "matches a shape that is not allowed");
  if ("if" in schema) {
    const cond = sub(schema.if, v, path);
    if (!cond.errors.length) { cond.evaluated.forEach(k => evaluated.add(k)); if ("then" in schema) merge(sub(schema.then, v, path)); }
    else if ("else" in schema) merge(sub(schema.else, v, path));
  }
  if ("unevaluatedProperties" in schema && jscIsPlainObject(v)) {
    for (const k of Object.keys(v)) {
      if (evaluated.has(k)) continue;
      if (schema.unevaluatedProperties === false) fail("unevaluatedProperties", `'${k}' is not a field of this shape`);
      else errors.push(...sub(schema.unevaluatedProperties, v[k], `${path}/${k}`).errors);
      evaluated.add(k);
    }
  }
  return { errors, evaluated };
}
/* errors of `v` against the kernel shape `name` (a kernel type, "scale" or
   "contentManifest"), each as a readable line */
function jscShapeErrors(name, v) {
  const root = jscRulesSchema.JSC_SCHEMA;
  return jscSchemaCheck({ $ref: "#/$defs/" + name }, v, root).errors.map(e => `${e.path || "/"}: ${e.message}`);
}
const JSC_KERNEL_TYPES = ["requirement", "requirementSet", "tailoring", "mapping", "component", "implementation",
  "assessment", "finding", "attestation", "risk"];
/* the kernel types whose shape `o` matches; a conformant object matches one */
const jscMatchTypes = o => JSC_KERNEL_TYPES.filter(t => !jscSchemaCheck({ $ref: "#/$defs/" + t }, o, jscRulesSchema.JSC_SCHEMA).errors.length);
const jscTypeOf = o => { const m = jscMatchTypes(o); return m.length === 1 ? m[0] : null; };
/* [objects] -> Map(id -> {type, obj}) of those that match exactly one type */
function jscTypedObjects(list) {
  const out = new Map();
  for (const o of list) { const t = jscTypeOf(o); if (t) out.set(o.id, { type: t, obj: o }); }
  return out;
}

/* ====================================================================
   Reference closure and typed edges
   ====================================================================
   Some references must resolve inside the bundle (closure-required), and
   where they do, the target has a type. The rest are landmarks: they may
   point outside, and they bind only if the target is present. Messages are
   the reference validator's, so that the same finding reads the same. */
const JSC_RISK_RULES = {
  "RISK-1": "a risk without an owner is a worry, not a managed risk (ISO/IEC 27001 6.1.2 c 2)",
  "RISK-2": "an assessed risk has a level on a named scale (ISO/IEC 27001 6.1.2 d-e; BSI 200-3 Risikoeinstufung; SP 800-30)",
  "RISK-3": "a treated risk names its option and carries its owner's signature (ISO/IEC 27001 6.1.3 a, f)",
  "RISK-4": "a modification with no controls is nothing (ISO/IEC 27001 6.1.3 b)",
  "RISK-5": "sharing names who carries it (ISO/IEC 27005 8.6; BSI 200-3 Transfer)",
  "RISK-6": "retention IS acceptance - no silent retention (ISO/IEC 27001 6.1.3 f)",
  "RISK-13": "a residual level is what remains of a level - it presupposes a rating, on the same scale (D23: levels never compare across scales)",
};
/* Sameness of content apart from identity: what a canonical-alias claims. */
function jscContentCanonical(obj) {
  const x = { ...obj };
  for (const k of ["id", "version", "label", "canonical-alias", "replaces"]) delete x[k];
  return jscRulesCanonical(x);
}
const jscRulesCanonical = jscRulesCore ? jscRulesCore.jscCanonical : o => jscCanonical(o);
function jscClosureErrors(objs) {
  const errs = [];
  const need = (oid, ref, what) => { if (!objs.has(ref)) errs.push(`${oid}: closure-required ${what} does not resolve in-bundle: ${ref}`); };
  const typeOf = ref => (objs.get(ref) || {}).type;
  const statementIds = ref => new Set(objs.get(ref).obj.statements.map(s => s.id));
  for (const [oid, { type: t, obj: o }] of objs) {
    for (const ca of o["canonical-alias"] || []) {
      const tgt = objs.get(ca.of);
      if (tgt && jscContentCanonical(o) !== jscContentCanonical(tgt.obj)) {
        errs.push(`${oid}: canonical-alias claims SAME content as ${ca.of} but content digests differ — a meaning change must use \`replaces\` (backlog #14)`);
      }
    }
    if (t === "requirementSet") {
      for (const m of o.members || []) need(oid, m.ref, "member ref");
    } else if (t === "tailoring") {
      for (const s of o.selects || []) {
        if (!("set-ref" in s)) continue;
        need(oid, s["set-ref"], "selects set-ref");
        if (objs.has(s["set-ref"]) && typeOf(s["set-ref"]) !== "requirementSet") {
          errs.push(`${oid}: selects set-ref resolves to a ${typeOf(s["set-ref"])}, not a RequirementSet: ${s["set-ref"]} ` +
            `(D13: a selection names a Set - chaining runs on the resolved package, never by reference)`);
        }
      }
      for (const e of o.excludes || []) {
        need(oid, e.ref, "excludes ref");
        if (objs.has(e.ref) && !["requirement", "requirementSet"].includes(typeOf(e.ref))) {
          errs.push(`${oid}: excludes ref resolves to a ${typeOf(e.ref)}, neither a Requirement nor a RequirementSet: ${e.ref} ` +
            `(D13: an exclusion scopes out requirements - one, or a Set's members)`);
        }
      }
      for (const op of o.operations || []) {
        need(oid, op["requirement-ref"], "operation requirement-ref");
        if (op["statement-id"] && typeOf(op["requirement-ref"]) === "requirement" && !statementIds(op["requirement-ref"]).has(op["statement-id"])) {
          errs.push(`${oid}: operation statement-id '${op["statement-id"]}' names no statement of ${op["requirement-ref"]}`);
        }
      }
    } else if (t === "implementation") {
      need(oid, o["component-ref"], "component-ref");
      need(oid, o["requirement-ref"], "requirement-ref");
      for (const sb of o["satisfied-by"] || []) {
        const inh = sb["inherited-from"];
        if (!inh) continue;
        const comp = objs.get(inh["component-ref"]);
        if (!comp) errs.push(`${oid}: inherited-from component does not resolve in-bundle: ${inh["component-ref"]}`);
        else if (!(comp.obj.authorizations || []).some(a => a.id === inh["basis-ref"])) {
          errs.push(`${oid}: basis-ref '${inh["basis-ref"]}' names no authorization of ${inh["component-ref"]} (D5 edge-local rule)`);
        }
      }
    } else if (t === "finding") {
      need(oid, o["assessment-ref"], "assessment-ref");
      need(oid, o["requirement-ref"], "requirement-ref");
      for (const rr of o["risk-refs"] || []) {
        if (objs.has(rr) && typeOf(rr) !== "risk") {
          errs.push(`${oid}: risk-refs entry resolves in-bundle to a ${typeOf(rr)}, not a Risk: ${rr} ` +
            `(RISK-12: a Risk edge is typed - a mis-aimed ref is a wrong statement, not a loose one)`);
        }
      }
    } else if (t === "risk") {
      for (const tr of o.treatments || []) {
        const ref = tr["requirement-ref"];
        need(oid, ref, "treatments requirement-ref (RISK-7)");
        if (objs.has(ref) && typeOf(ref) !== "requirement") {
          errs.push(`${oid}: treatments requirement-ref resolves to a ${typeOf(ref)}, not a Requirement: ${ref} ` +
            `(RISK-12: a Risk edge is typed - coverage joins on Requirement ids)`);
        } else if (objs.has(ref)) {
          const sids = statementIds(ref);
          for (const sid of tr["statement-ids"] || []) {
            if (!sids.has(sid)) errs.push(`${oid}: treatments statement-id '${sid}' names no statement of ${ref} (RISK-8: clause precision is addressable or it is prose)`);
          }
        }
      }
      for (const [field, want, what] of [["component-refs", "component", "the asset at risk is a Component"], ["tailoring-refs", "tailoring", "the scope of a treatment is a Tailoring"]]) {
        for (const ref of o[field] || []) {
          need(oid, ref, `${field} (RISK-7)`);
          if (objs.has(ref) && typeOf(ref) !== want) {
            errs.push(`${oid}: ${field} entry resolves to a ${typeOf(ref)}, not a ${want[0].toUpperCase() + want.slice(1)}: ${ref} (RISK-12: a Risk edge is typed - ${what})`);
          }
        }
      }
      const ra = o.rating, rr = o["residual-rating"];
      if (ra && rr && ra["scale-ref"] !== rr["scale-ref"]) {
        errs.push(`${oid}: residual-rating is on ${rr["scale-ref"]}, rating on ${ra["scale-ref"]} (RISK-13: ${JSC_RISK_RULES["RISK-13"]})`);
      }
      for (const part of ["likelihood", "impact"]) {
        const pa = (ra || {})[part], pr = (rr || {})[part];
        if (pa && pr && pa["scale-ref"] !== pr["scale-ref"]) {
          errs.push(`${oid}: residual-rating ${part} is on ${pr["scale-ref"]}, rating ${part} on ${pa["scale-ref"]} (RISK-13: ${JSC_RISK_RULES["RISK-13"]})`);
        }
      }
    } else if (t === "mapping") {
      for (const side of ["source", "target"]) {   // endpoints are landmarks; a scope binds if the endpoint is present
        const ref = o[side + "-ref"];
        if (typeOf(ref) !== "requirement") continue;
        const sids = statementIds(ref);
        for (const sc of o[side + "-scope"] || []) {
          if (!sids.has(sc.slice(sc.indexOf(":") + 1))) errs.push(`${oid}: ${side}-scope '${sc}' names no statement of the in-bundle endpoint`);
        }
      }
    }
  }
  /* Set membership is a DAG: overlap is legal, a cycle is not. Depth-first
     with three colours; an edge into a Set that is still open closes a cycle. */
  const color = new Map();
  const setMembers = id => (objs.get(id).obj.members || []).map(m => m.ref);
  for (const [root, r] of objs) {
    if (r.type !== "requirementSet" || color.has(root)) continue;
    const stack = [{ id: root, refs: setMembers(root), i: 0 }];
    color.set(root, 1);
    while (stack.length) {
      const top = stack[stack.length - 1];
      if (top.i >= top.refs.length) { color.set(top.id, 2); stack.pop(); continue; }
      const adv = top.refs[top.i++];
      if (typeOf(adv) !== "requirementSet") continue;
      if (color.get(adv) === 1) {
        errs.push(`${top.id}: RequirementSet membership cycle: ${[...stack.map(f => f.id), adv].join(" -> ")} (D21: membership graphs are acyclic; P10 #39)`);
      } else if (!color.has(adv)) {
        color.set(adv, 1);
        stack.push({ id: adv, refs: setMembers(adv), i: 0 });
      }
    }
  }
  return errs;
}

/* ====================================================================
   Kernel pin (KERNEL-1, KERNEL-2)
   ==================================================================== */
const JSC_RULES_KERNEL = "2.0.0", JSC_RULES_KERNEL_READS = ["1.0.0", "2.0.0"];
/* -> [version the content needs, why] */
function jscKernelNeeded(objs, manifest) {
  if (manifest && (manifest.scales || []).length) return ["2.0.0", "the manifest pins scale definitions"];
  for (const oid of [...objs.keys()].sort()) {
    const { type, obj } = objs.get(oid);
    if (type === "risk") return ["2.0.0", `${oid} is a Risk`];
    if (type === "finding" && (obj["risk-refs"] || []).length) return ["2.0.0", `${oid} carries risk-refs`];
  }
  return ["1.0.0", null];
}
function jscKernelPinErrors(manifest, objs) {
  const pin = manifest["kernel-version"];
  if (pin !== undefined && pin !== null && !JSC_RULES_KERNEL_READS.includes(pin)) {
    return [`manifest pins kernel-version ${pin}; this validator implements ${JSC_RULES_KERNEL} and reads ${JSC_RULES_KERNEL_READS.join(", ")} ` +
      `(KERNEL-2: a tool stops at a kernel it does not implement, and says which)`];
  }
  const [needed, why] = jscKernelNeeded(objs, manifest);
  if (needed !== "1.0.0" && pin !== needed) {
    return [`${why}, which needs kernel ${needed}, but the manifest ${pin ? "pins kernel-version " + pin : "pins no kernel-version"} ` +
      `(KERNEL-1: content beyond 1.0.0 names its kernel, so that an older tool can say what it is missing)`];
  }
  return [];
}

/* ====================================================================
   Risk: the shape rules by name, coverage, links
   ==================================================================== */
/* RISK-1..6 and the first half of RISK-13 are conditionals of the schema,
   which refuses the object with a bare "no". This names the rule.
   -> [[rule id, what is wrong]]. It explains a refusal; it never accepts. */
function jscRiskRuleViolations(o) {
  const out = [];
  if (!jscIsPlainObject(o)) return out;
  let miss = ["scenario", "owner-ref", "state"].filter(k => !(k in o));
  if (miss.length) out.push(["RISK-1", `missing ${miss.join(", ")}`]);
  const st = o.state, tr = o.treatment;
  if ((st === "assessed" || st === "treated") && !("rating" in o)) out.push(["RISK-2", `state=${st} without rating`]);
  if (st === "treated") {
    miss = ["treatment", "acceptance"].filter(k => !(k in o));
    if (miss.length) out.push(["RISK-3", `treated without ${miss.join(" and ")}`]);
  }
  if (tr === "modify" && !("treatments" in o)) out.push(["RISK-4", "modify names no controls"]);
  if (tr === "share" && !("shared-with-ref" in o)) out.push(["RISK-5", "share without shared-with-ref"]);
  if (tr === "retain" && !("acceptance" in o)) out.push(["RISK-6", "retain without acceptance"]);
  if ("residual-rating" in o && !("rating" in o)) out.push(["RISK-13", "residual-rating without rating"]);
  return out;
}
/* A Risk justifies a control only while it is managed: `retired` is
   terminal and lifecycle `withdrawn` unpublishes the object. */
const jscRiskIsLive = r => r.state !== "retired" && r.lifecycle !== "withdrawn";
/* ... and only once a treatment decision rests on an assessed risk: live,
   published (not draft), assessed or treated, and an option chosen. */
const jscRiskJustifies = r => jscRiskIsLive(r) && r.lifecycle !== "draft" && (r.state === "assessed" || r.state === "treated") && "treatment" in r;
const JSC_NO_TAILORING = "*";   // report key of the implicit selection: every requirement of the bundle

/* B.1.9 risk coverage. For each Tailoring in force: which selected
   requirements are justified by a Risk (covered), which are not (uncovered),
   and of those which are named only by Risks that do not justify yet
   (pending) or no longer (lapsed). A bundle with no Tailoring has every
   requirement in play, reported under "*". A Risk's tailoring-refs scope it;
   without them it applies to every Tailoring. Uncovered is a report line:
   whether a control needs a risk basis is the programme's policy.
   -> { report: { tailorings: {id: {tier, selected, open-selection, covered,
        uncovered, pending, lapsed, excludes-without-rationale}}, risks,
        treatment-out-of-scope }, errors (RISK-11), notes } */
async function jscRiskCoverage(objs) {
  const notes = [], errs = [];
  const of = type => new Map([...objs].filter(([, r]) => r.type === type).map(([id, r]) => [id, r.obj]));
  const risks = of("risk"), tailorings = of("tailoring");
  let inForce = [...tailorings.keys()].filter(tid => tailorings.get(tid).lifecycle !== "withdrawn").sort();
  for (const tid of [...tailorings.keys()].filter(t => !inForce.includes(t)).sort()) {
    notes.push(`${tid}: withdrawn - selects nothing and is not reported (a withdrawn Statement of Applicability is history)`);
  }
  const applies = (r, tid) => !(r["tailoring-refs"] || []).length || r["tailoring-refs"].includes(tid);
  const report = { tailorings: {}, risks: risks.size, "treatment-out-of-scope": [] };
  const selections = new Map();
  if (!tailorings.size) inForce = [JSC_NO_TAILORING];
  for (const tid of inForce) {
    let tobj = {}, tier = "none", open = false, sel;
    if (tid === JSC_NO_TAILORING) {
      sel = new Set([...objs].filter(([, r]) => r.type === "requirement" && r.obj.lifecycle !== "withdrawn").map(([id]) => id));
    } else {
      tobj = tailorings.get(tid);
      tier = await jscDeriveTier(tobj, objs);
      const s = jscSelection(tobj, objs);
      sel = s.selected; open = s.open; notes.push(...s.notes);
    }
    selections.set(tid, { sel, open });
    const treats = new Map(), pending = new Map(), lapsed = new Map();
    for (const [rid, r] of risks) {
      if (!applies(r, tid)) continue;
      const bucket = jscRiskJustifies(r) ? treats : jscRiskIsLive(r) ? pending : lapsed;
      for (const tr of r.treatments || []) {
        if (!bucket.has(tr["requirement-ref"])) bucket.set(tr["requirement-ref"], new Set());
        bucket.get(tr["requirement-ref"]).add(rid);
      }
    }
    const sorted = [...sel].sort(), ids = (map, q) => [...map.get(q)].sort();
    const covered = Object.fromEntries(sorted.filter(q => treats.has(q)).map(q => [q, ids(treats, q)]));
    const uncovered = sorted.filter(q => !treats.has(q));
    const pendingOnly = Object.fromEntries(uncovered.filter(q => pending.has(q)).map(q => [q, ids(pending, q)]));
    const lapsedOnly = Object.fromEntries(uncovered.filter(q => lapsed.has(q) && !pending.has(q)).map(q => [q, ids(lapsed, q)]));
    const noRationale = (tobj.excludes || []).filter(e => !e.rationale).map(e => e.ref);
    report.tailorings[tid] = { tier, selected: sel.size, "open-selection": open, covered, uncovered,
      pending: pendingOnly, lapsed: lapsedOnly, "excludes-without-rationale": noRationale };
    const lab = tid === JSC_NO_TAILORING ? "(no Tailoring)" : tid;
    const list = a => "[" + a.map(x => `'${x}'`).join(", ") + "]";
    for (const [q, rids] of Object.entries(pendingOnly)) {
      notes.push(`${lab}: selected ${q} is named only by Risk(s) without an assessed treatment decision ${list(rids)} - counted as uncovered (a risk justifies once it is assessed and its option chosen)`);
    }
    for (const [q, rids] of Object.entries(lapsedOnly)) {
      notes.push(`${lab}: selected ${q} is named only by retired/withdrawn Risk(s) ${list(rids)} - counted as uncovered (C.3c: a retired risk justifies nothing)`);
    }
    if (tier === "consumer" && noRationale.length) {
      notes.push(`${tid}: ${noRationale.length} exclude(s) without rationale at consumer tier (RISK-10, SHOULD: an SoA exclusion carries its justification)`);
    }
  }
  /* RISK-14 (SHOULD): with more than one Tailoring in force an unscoped Risk
     justifies in each. */
  if (inForce.length > 1) {
    for (const rid of [...risks.keys()].sort()) {
      const r = risks.get(rid);
      if (jscRiskIsLive(r) && (r.treatments || []).length && !(r["tailoring-refs"] || []).length) {
        notes.push(`${rid}: no tailoring-refs in a bundle with ${inForce.length} Tailorings - its treatment counts in each (RISK-14, SHOULD: a Risk names the Tailoring its treatment belongs to)`);
      }
    }
  }
  /* RISK-11 binds live risks only and is asked of the Tailorings the risk
     belongs to. Where one of those selections is open the question cannot be
     decided from here, and that is said instead of guessed. */
  const outOfScope = new Map(), undecided = new Map();
  const add = (map, q, rid) => { if (!map.has(q)) map.set(q, new Set()); map.get(q).add(rid); };
  for (const [rid, r] of risks) {
    if (!jscRiskIsLive(r)) continue;
    const mine = inForce.filter(tid => applies(r, tid));
    for (const tr of r.treatments || []) {
      const q = tr["requirement-ref"], tgt = objs.get(q);
      if (!tgt || tgt.type !== "requirement") continue;
      if (mine.some(tid => selections.get(tid).sel.has(q))) continue;
      if (tgt.obj.lifecycle !== "withdrawn" && mine.some(tid => selections.get(tid).open)) add(undecided, q, rid);
      else add(outOfScope, q, rid);
    }
  }
  for (const q of [...undecided.keys()].sort()) {
    notes.push(`${[...undecided.get(q)].sort()[0]}: treatment names ${q}, which no set-ref select reaches - RISK-11 undecided: a predicate select of its Tailoring(s) may select it`);
  }
  for (const q of [...outOfScope.keys()].sort()) {
    const rids = [...outOfScope.get(q)].sort();
    report["treatment-out-of-scope"].push({ requirement: q, risks: rids });
    const why = objs.get(q).obj.lifecycle === "withdrawn" ? "which is withdrawn"
      : !rids.some(x => (risks.get(x)["tailoring-refs"] || []).length) ? "which no Tailoring in this bundle selects"
      : "which the Tailoring(s) it belongs to do not select";
    errs.push(`${rids[0]}: treatment names ${q}, ${why} (RISK-11: a risk cannot lean on a control the SoA dropped)`);
  }
  return { report, errors: errs, notes };
}
/* RISK-9 (SHOULD): a risk-adjustment Deviation names the Risk it adjusts for. */
function jscRiskLinkNotes(objs) {
  const notes = [], riskIds = new Set([...objs].filter(([, r]) => r.type === "risk").map(([id]) => id));
  if (!riskIds.size) return notes;
  for (const [oid, { type, obj }] of objs) {
    const devs = [...(obj.deviations || [])];
    if (type === "tailoring") devs.push(...(obj.operations || []).map(op => op.deviation).filter(jscIsPlainObject));
    for (const d of devs) {
      if (d.type === "risk-adjustment" && !(d.refs || []).some(x => riskIds.has(x))) {
        notes.push(`${oid}: risk-adjustment Deviation references no Risk of this bundle (RISK-9, SHOULD: the adjustment names the risk it accepts)`);
      }
    }
  }
  return notes;
}

/* ====================================================================
   Scales and the matrix (SCALE-1..4)
   ====================================================================
   A scale is the organisation's own: how many levels, and what they are
   called. Its definition is a file the manifest pins, not an object. Levels
   are listed lowest first. The scale of the combined level may carry a
   matrix over a likelihood scale and an impact scale. `scales` is always a
   Map of scale id -> definition. */
/* SCALE-1, first half: the definition has the scale shape, no level twice,
   and the id and version its pin states. */
function jscScaleDefinitionErrors(sd, pin) {
  const name = (pin && pin.path) || (jscIsPlainObject(sd) ? sd.id : "?");
  const shape = jscShapeErrors("scale", sd);
  if (shape.length) return [`${name}: not a scale definition: ${shape[0].slice(0, 110)} (SCALE-1)`];
  const errs = [], codes = sd.levels.map(l => l.level);
  const dup = [...new Set(codes.filter((c, i) => codes.indexOf(c) !== i))].sort();
  if (dup.length) errs.push(`${name}: level(s) [${dup.map(d => `'${d}'`).join(", ")}] listed twice - a level has one place in the order (SCALE-1)`);
  if (pin && (pin.id !== sd.id || pin["exact-version"] !== sd.version)) {
    errs.push(`${name}: pinned as ${pin.id} ${pin["exact-version"]}, the file says ${sd.id} ${sd.version} (SCALE-1: the pin and the definition agree)`);
  }
  return errs;
}
/* SCALE-1, second half: a matrix names two scales of the same bundle, has
   exactly one cell for every pair of their levels, and every cell is a level
   of its own scale. -> { errors, usable: Map without the matrices that
   failed }: SCALE-4 is not asked of a broken table. */
function jscMatrixErrors(scales) {
  const errors = [], usable = new Map(scales);
  for (const sid of [...scales.keys()].sort()) {
    const sd = scales.get(sid), mx = sd.matrix;
    if (!mx) continue;
    const mine = sd.levels.map(l => l.level), bad = [];
    const ls = scales.get(mx["likelihood-scale"]), is = scales.get(mx["impact-scale"]);
    if (!ls) bad.push(`its likelihood-scale ${mx["likelihood-scale"]} is not pinned in this bundle`);
    if (!is) bad.push(`its impact-scale ${mx["impact-scale"]} is not pinned in this bundle`);
    if (!bad.length) {
      const lk = ls.levels.map(l => l.level), ik = is.levels.map(l => l.level), cells = mx.cells;
      const quoted = a => "[" + a.map(x => `'${x}'`).join(", ") + "]";
      const extra = Object.keys(cells).filter(k => !lk.includes(k)).sort();
      if (extra.length) bad.push(`rows ${quoted(extra)} are no levels of the likelihood scale`);
      for (const l of lk) {
        const row = cells[l];
        if (row === undefined) { bad.push(`no row for likelihood '${l}'`); continue; }
        const miss = ik.filter(i => !(i in row)), more = Object.keys(row).filter(k => !ik.includes(k)).sort();
        if (miss.length) bad.push(`row '${l}' has no cell for impact ${quoted(miss)}`);
        if (more.length) bad.push(`row '${l}' has cells ${quoted(more)} that are no levels of the impact scale`);
        const wrong = [...new Set(Object.values(row).filter(v => !mine.includes(v)))].sort();
        if (wrong.length) bad.push(`row '${l}' yields ${quoted(wrong)}, no level(s) of this scale`);
      }
    }
    if (bad.length) {
      errors.push(`${sid}: matrix is not usable: ${bad.slice(0, 4).join("; ")} (SCALE-1: a matrix has one cell per pair of levels of its two pinned scales, each cell a level of its own scale)`);
      const { matrix, ...rest } = sd;
      usable.set(sid, rest);
    }
  }
  return { errors, usable };
}
/* every level a Risk states: [where, level, scale-ref] */
function jscRiskLevels(o) {
  const out = [];
  for (const field of ["rating", "residual-rating"]) {
    const r = o[field];
    if (!jscIsPlainObject(r)) continue;
    out.push([field, r.level, r["scale-ref"]]);
    for (const part of ["likelihood", "impact"]) if (jscIsPlainObject(r[part])) out.push([`${field}.${part}`, r[part].level, r[part]["scale-ref"]]);
  }
  return out;
}
/* The cell of a scale's matrix for two input levels, or undefined. */
const jscMatrixCell = (sd, likelihood, impact) => ((((sd || {}).matrix || {}).cells || {})[likelihood] || {})[impact];
/* SCALE-2: a level stated on a pinned scale is one of that scale's levels.
   SCALE-3 (SHOULD): a residual level is not above the level it remains of.
   SCALE-4: on a scale with a matrix, a rating that states both inputs
   states the level of their cell, or says why not (override-rationale).
   An unpinned scale-ref stays a landmark; nothing is checked on it.
   -> { errors, notes } */
function jscScaleErrors(scales, objs) {
  const errors = [], notes = [];
  const order = new Map([...scales].map(([sid, sd]) => [sid, new Map(sd.levels.map((l, i) => [l.level, i]))]));
  for (const oid of [...objs.keys()].sort()) {
    const { type, obj: o } = objs.get(oid);
    if (type !== "risk") continue;
    const seen = new Map();
    for (const [where, level, sref] of jscRiskLevels(o)) {
      if (!order.has(sref)) continue;
      if (!order.get(sref).has(level)) {
        errors.push(`${oid}: ${where} level '${level}' is not a level of ${sref} (its levels: ${[...order.get(sref).keys()].join(", ")}) (SCALE-2: a level is one the scale defines)`);
      } else seen.set(where, [order.get(sref).get(level), sref, level]);
    }
    for (const part of ["", ".likelihood", ".impact"]) {
      const a = seen.get("rating" + part), b = seen.get("residual-rating" + part);
      if (a && b && a[1] === b[1] && b[0] > a[0]) {
        notes.push(`${oid}: residual${part || " level"} '${b[2]}' is above '${a[2]}' on ${a[1]} (SCALE-3, SHOULD: what remains after treatment is not more than what was there)`);
      }
    }
    for (const field of ["rating", "residual-rating"]) {
      const r = o[field];
      if (!jscIsPlainObject(r)) continue;
      const mx = (scales.get(r["scale-ref"]) || {}).matrix, lk = r.likelihood, im = r.impact;
      if (!mx || !jscIsPlainObject(lk) || !jscIsPlainObject(im)) continue;
      if (lk["scale-ref"] !== mx["likelihood-scale"] || im["scale-ref"] !== mx["impact-scale"]) {
        errors.push(`${oid}: ${field} is on ${r["scale-ref"]}, whose matrix combines ${mx["likelihood-scale"]} and ${mx["impact-scale"]}, but states its likelihood and impact on other scales (SCALE-4: a level and its inputs belong to one method)`);
        continue;
      }
      const want = (mx.cells[lk.level] || {})[im.level];
      if (want === undefined || r.level === want) continue;   // an undefined input level is SCALE-2's failure
      const said = `${oid}: ${field} states '${r.level}'; the matrix of ${r["scale-ref"]} yields '${want}' for likelihood '${lk.level}' and impact '${im.level}'`;
      if (r["override-rationale"]) notes.push(`${said} - overridden with a rationale (SCALE-4)`);
      else errors.push(`${said} (SCALE-4: a level follows from its matrix, or the rating carries an override-rationale)`);
    }
  }
  return { errors, notes };
}
/* The scale rules over a list of definitions, as a bundle is checked:
   -> { errors, notes, scales: the usable Map } */
function jscCheckScales(definitions, objs, pins) {
  const errors = [], scales = new Map();
  for (const sd of definitions) {
    const e = jscScaleDefinitionErrors(sd, pins && pins.get(sd && sd.id));
    errors.push(...e);
    if (!e.length) scales.set(sd.id, sd);
  }
  const mx = jscMatrixErrors(scales);
  const lv = jscScaleErrors(mx.usable, objs);
  return { errors: [...errors, ...mx.errors, ...lv.errors], notes: lv.notes, scales: mx.usable };
}


/* ====================================================================
   One object on its own
   ==================================================================== */
/* Optional containers must be absent, not empty (D3.3): an empty list and a
   missing list would otherwise be two spellings of one meaning with two
   semantic digests. -> the paths of the empty ones */
const JSC_OPTIONAL_CONTAINERS = new Set(["aliases", "canonical-alias", "replaces", "relations", "facets", "annotations", "parameters",
  "deviations", "excludes", "source-scope", "target-scope", "evidence-refs", "statement-refs", "capabilities", "authorizations",
  "actions", "choices", "threat-refs", "component-refs", "treatments", "risk-refs", "tailoring-refs"]);
function jscOptionalEmptyViolations(obj, path = "$") {
  const out = [];
  if (Array.isArray(obj)) obj.forEach((v, i) => out.push(...jscOptionalEmptyViolations(v, `${path}[${i}]`)));
  else if (jscIsPlainObject(obj)) {
    for (const [k, v] of Object.entries(obj)) {
      if (JSC_OPTIONAL_CONTAINERS.has(k) && v !== null && typeof v === "object" && !Object.keys(v).length) out.push(`${path}.${k}`);
      out.push(...jscOptionalEmptyViolations(v, `${path}.${k}`));
    }
  }
  return out;
}
/* What is wrong with one object, without looking at any other.
   -> { type: its one kernel type or null, errors: [string] } */
function jscObjectErrors(obj) {
  const matches = jscMatchTypes(obj), errors = [];
  if (matches.length !== 1) {
    let best = "";
    if (!matches.length) {
      /* the closest shape, by the number of things wrong with it, and its first complaint */
      const counted = JSC_KERNEL_TYPES.map(t => [t, jscShapeErrors(t, obj)]).sort((a, b) => a[1].length - b[1].length)[0];
      best = ` (closest ${counted[0]}: ${counted[1][0] || "?"})`;
      if (jscIsPlainObject(obj) && ("scenario" in obj || "owner-ref" in obj)) {
        best += jscRiskRuleViolations(obj).map(([rule, what]) => ` [${rule}] ${what} - ${JSC_RISK_RULES[rule]}`).join("");
      }
    }
    return { type: null, errors: [`matches ${matches.length ? matches.join(" and ") : "NO type"}${best}`] };
  }
  const empty = jscOptionalEmptyViolations(obj);
  if (empty.length) errors.push(`optional empty containers present: ${empty.join(", ")}`);
  if (matches[0] === "requirement") {
    const sids = new Set(obj.statements.map(s => s.id));
    if (sids.size !== obj.statements.length) errors.push("duplicate statement ids (unique-within, B.1.3) — identity addressing becomes ambiguous");
    for (const st of obj.statements) {
      const declared = new Set((st.parameters || []).map(p => p.name));
      for (const txt of Object.values(st.prose)) {
        for (const m of (Array.isArray(txt) ? txt.join(" ") : txt).matchAll(/\{param:([^}]+)\}/g)) {
          if (!declared.has(m[1])) errors.push(`unbound {param:${m[1]}} in statement ${st.id} (the 216 rule)`);
        }
      }
    }
    for (const [fid, payload] of Object.entries(obj.facets || {})) {
      if (!jscIsPlainObject(payload) || !jscIsPlainObject(payload["by-statement"])) continue;
      for (const sid of Object.keys(payload["by-statement"])) if (!sids.has(sid)) errors.push(`facet ${fid} by-statement key '${sid}' names no statement (D10 rev)`);
    }
  }
  return { type: matches[0], errors };
}

/* ====================================================================
   Facet payloads and the operation law
   ==================================================================== */
const jscFacetBase = key => String(key).replace(/@[^@]*$/, "");
const jscIsPrivateFacet = key => String(key).startsWith("private:");
/* stdlib facet id -> its descriptor */
const JSC_STDLIB_BY_ID = new Map(jscRulesSchema.JSC_STDLIB.map(d => [d.id, d]));
/* A facet payload is checked against the stdlib descriptor of its id, or
   against the schema the bundle pins for it. A `private:` facet is not
   checked by definition. Anything else is unregistered and fails closed.
   items: [[label, object]]; pinned: Map(facet id without version -> schema). */
function jscFacetErrors(items, pinned) {
  const errs = [];
  for (const [label, obj] of items) {
    for (const [key, payload] of Object.entries((obj && obj.facets) || {})) {
      const base = jscFacetBase(key);
      if (jscIsPrivateFacet(key)) continue;
      const schema = JSC_STDLIB_BY_ID.has(base) ? JSC_STDLIB_BY_ID.get(base).schema : pinned.get(base);
      if (schema === undefined) { errs.push(`${label}: unregistered facet '${key}' — not stdlib, not pinned in the manifest, not private: (dangerous-by-default, D10)`); continue; }
      let found;
      try { found = jscSchemaCheck(schema, payload, schema).errors; }
      catch (e) { errs.push(`${label}: facet '${key}' cannot be checked: ${e.message}`); continue; }
      if (found.length) errs.push(`${label}: facet '${key}' payload violates its schema: ${found[0].message} @ ${found[0].path.replace(/^\//, "")}`);
    }
  }
  return errs;
}
/* What an operation owes, by the tier of its Tailoring (D13, B.1.6). A
   weakening needs a Deviation at consumer tier: a non-monotone change of
   modality, a substantive change of prose, a parameter value outside its
   declared space, the attaching or detaching of a facet that changes
   semantics, the removal of a `required` relation. Wrong at any tier: two
   operations on one target, a parameter value of the wrong kind, a facet
   nobody registered. pinnedDecl: Map(facet id -> its modifies-semantics). */
async function jscTailoringDutyErrors(objs, pinnedDecl) {
  const errs = [], pd = pinnedDecl || new Map();
  for (const [oid, { type, obj: tobj }] of objs) {
    if (type !== "tailoring") continue;
    const tier = await jscDeriveTier(tobj, objs), seen = new Set();
    for (const op of tobj.operations || []) {
      const key = jscTargetKey(op);
      if (seen.has(key)) {
        const named = [op["requirement-ref"], op["statement-id"], op.parameter, op.field, op.facet].filter(Boolean).map(x => `'${x}'`).join(", ");
        errs.push(`${oid}: two operations address the same target [${named}] within one Tailoring (D13: override rides Tailoring-of-Tailoring chaining, never in-place; P10 #30)`);
      }
      seen.add(key);
      const tgt = objs.get(op["requirement-ref"]);
      const stmt = tgt && tgt.type === "requirement" ? tgt.obj.statements.find(s => s.id === op["statement-id"]) : null;
      let duty = null;
      if (op.op === "set-modality") {
        if (stmt) { const v = jscModalityVerdict(stmt.modality, op.modality); if (v !== "monotone") duty = `non-monotone set-modality (${v})`; }
      } else if (op.op === "replace-prose" && op.intent === "substantive") {
        duty = "substantive replace-prose";
      } else if (op.op === "attach-facet" || op.op === "detach-facet") {
        const fid = String(op.facet || ""), base = jscFacetBase(fid);
        if (!jscIsPrivateFacet(fid)) {
          const decl = JSC_STDLIB_BY_ID.has(base) ? JSC_STDLIB_BY_ID.get(base)["modifies-semantics"] || [] : pd.get(base);
          if (decl === undefined) errs.push(`${oid}: ${op.op} references facet '${fid}' that is neither stdlib, nor pinned in the manifest, nor private: (dangerous-by-default, D10; P10 #29)`);
          else if (decl.length) duty = `${op.op} of a semantics-bearing facet [${decl.map(x => `'${x}'`).join(", ")}]`;
        }
      } else if (op.op === "set-parameter") {
        const decl = stmt ? (stmt.parameters || []).find(p => p.name === op.parameter) : null;
        if (decl) {
          const verdict = jscParamCheck(decl, op.value);
          if (verdict === "invalid") errs.push(`${oid}: set-parameter '${op.parameter}' value fails the declared type/bounds (D13; not Deviation-escapable)`);
          else if (verdict === "deviation-required") duty = "out-of-bounds / against-tightening set-parameter";
        }
      } else if (op.op === "remove-relation") {
        if (jscIsPlainObject(op.relation) && op.relation.type === "required") duty = "remove-relation of a `required` edge";
      }
      if (duty && !("deviation" in op) && !("deviation-ref" in op) && tier === "consumer") {
        errs.push(`${oid}: ${duty} without a Deviation at consumer tier (derived tier: ${tier}; B.1.6/D13 rev 2)`);
      }
    }
  }
  return errs;
}
/* The verdict of an attestation over one subject: the meaning differs
   (tamper), bytes and meaning are as signed (full-match), or the meaning is
   intact and the bytes are not (semantic-match). */
const jscAttestationVerdict = (signed, delivered) =>
  delivered.semantic !== signed.semantic ? "tamper" : delivered.package === signed.package ? "full-match" : "semantic-match";

/* ====================================================================
   A whole set
   ====================================================================
   Everything this file can say about a loaded graph, in the order the
   reference validator works: the manifest, each object, the digests, the
   pinned files, references, the operation law, the kernel pin, the scales,
   risk coverage, facet payloads. `verified` is the result of jscVerify.
   -> { findings: [{ kind: "error"|"note", area, object: id or null, message }],
        types: {type: count}, tiers: {tailoring id: tier}, coverage: report } */
async function jscCheckGraph(g, verified) {
  const findings = [], types = {};
  const add = (kind, area, object, message) => findings.push({ kind, area, object, message });
  const ids = [...g.objects.keys()];
  /* a message of the reference validator starts with the object it is about */
  const about = m => ids.find(id => m.startsWith(id + ":")) || null;
  const strip = m => { const id = about(m); return id ? m.slice(id.length + 2) : m; };
  const pass = (area, kind) => list => list.forEach(m => add(kind, area, about(m), strip(m)));

  if (g.manifest) {
    jscShapeErrors("contentManifest", g.manifest).slice(0, 5).forEach(m => add("error", "manifest", null, `manifest schema: ${m}`));
    jscKernelPinErrors(g.manifest, g.objects).forEach(m => add("error", "manifest", null, m));
  } else add("note", "manifest", null, "the set has no content manifest; digests and pins cannot be checked until it is exported");
  g.problems.forEach(m => add("error", "files", null, m));

  const objs = new Map();
  for (const [id, r] of g.objects) {
    const res = jscObjectErrors(r.obj);
    res.errors.forEach(m => add("error", "object", id, m));
    if (res.type) { objs.set(id, { type: res.type, obj: r.obj }); types[res.type] = (types[res.type] || 0) + 1; }
    if (g.manifest && r.entry && r.entry.id !== r.obj.id) add("error", "manifest", id, "manifest id != object id");
  }
  if (verified) {
    for (const [id, v] of verified.objects) {
      const r = g.objects.get(id);
      if (v === null) { if (!jscRulesBeside(r) && g.manifest) add(r.origin === "authored" ? "note" : "error", "digest", id, r.origin === "authored" ? "written in this app; not in the manifest until the set is exported" : "on disk but not in manifest"); continue; }
      const edited = r.origin === "authored" ? " (edited in this app; the export writes a new manifest)" : "";
      if (!v.pkg) add(edited ? "note" : "error", "digest", id, "package-digest mismatch" + edited);
      if (!v.sem) add(edited ? "note" : "error", "digest", id, "semantic-digest mismatch" + edited);
    }
    verified.pins.filter(p => !p.ok).forEach(p => add("error", "digest", null, `${p.path}: pinned file digest mismatch`));
    if (verified.counts.missing) add("error", "manifest", null, `${verified.counts.missing} object(s) listed but missing`);
  }
  pass("reference", "error")(jscClosureErrors(objs));
  const pinnedSchemas = new Map(), pinnedDecl = new Map();
  for (const f of g.facetSchemas) {
    if (!f.def || !f.def.id) continue;
    pinnedSchemas.set(f.def.id, f.def.schema || { type: "object" });
    pinnedDecl.set(f.def.id, f.def["modifies-semantics"] || ["assessment", "tailoring", "selection", "rendering"]);   // a pin that omits it is dangerous by default
    const std = JSC_STDLIB_BY_ID.get(f.def.id);
    if (std && jscRulesCanonical(f.def.schema || {}) !== jscRulesCanonical(std.schema)) add("error", "facet", null, `${f.path}: pin of stdlib facet ${f.def.id} DIVERGES from the normative descriptor (D26)`);
  }
  pass("tailoring", "error")(await jscTailoringDutyErrors(objs, pinnedDecl));
  const pins = new Map([...g.scales.values()].filter(x => x.pin).map(x => [x.def.id, x.pin]));
  const sc = jscCheckScales([...g.scales.values()].map(x => x.def), objs, pins);
  pass("scale", "error")(sc.errors); pass("scale", "note")(sc.notes);
  const cov = await jscRiskCoverage(objs);
  pass("risk", "error")(cov.errors); pass("risk", "note")([...cov.notes, ...jscRiskLinkNotes(objs)]);
  pass("facet", "error")(jscFacetErrors([...objs].map(([id, r]) => [id, r.obj]), pinnedSchemas));
  const tiers = {};
  for (const [id, r] of objs) if (r.type === "tailoring") tiers[id] = await jscDeriveTier(r.obj, objs);
  return { findings, types, tiers, coverage: cov.report };
}
const jscRulesBeside = r => r.type === "attestation" && !r.entry;

if (typeof module !== "undefined" && module.exports) {
  module.exports = { JSC_MODALITIES, JSC_ELAPSED_UNITS, JSC_CALENDAR_UNITS, jscModalityVerdict, jscParamCheck,
    jscDecimalCompare, jscExpandRefs, jscSetParents, jscSelection, jscUriOrigin, jscDeriveTier, jscTargetKey,
    jscResolveTailoring, jscTextify, JSC_NEXT, jscCanMove, jscComposeRelationship,
    jscSchemaCheck, jscShapeErrors, jscMatchTypes, jscTypeOf, jscTypedObjects, JSC_KERNEL_TYPES, JSC_RISK_RULES, jscClosureErrors,
    jscKernelNeeded, jscKernelPinErrors, jscRiskRuleViolations, jscRiskIsLive, jscRiskJustifies, JSC_NO_TAILORING, jscRiskCoverage,
    jscRiskLinkNotes, jscScaleDefinitionErrors, jscMatrixErrors, jscRiskLevels, jscMatrixCell, jscScaleErrors, jscCheckScales,
    jscOptionalEmptyViolations, jscObjectErrors, jscFacetErrors, jscTailoringDutyErrors, jscAttestationVerdict, jscCheckGraph };
}
