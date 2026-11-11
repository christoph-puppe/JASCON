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

   Also ported, each against its vector family: the verification of DSSE
   envelopes (Ed25519) with the tier of a Tailoring in verification mode,
   the composition of two bundles (D3.5), and the conditional-apply engine
   (B.1.8). All fifteen vector families run against this file. The
   conditional-apply engine is run by nothing but its vectors, here as in
   the reference: no bundle has a place to carry an instance yet.

   Not ported: the reading of a bundle from disk with its end-of-line and
   file checks (jascon-core.js reads sets from the browser's store instead),
   and the command line. The Python validator stays the reference.

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
   authority-proven. With `verify` = { envelopes: Map(envelope-ref -> envelope),
   trusted: {signer: public key hex}, notes: [] or null } the tier is derived
   in verification mode: the matching attestation must also carry an envelope
   that verifies under the signer's trusted key, and the reason an
   attestation did not prove is pushed to notes. */
function jscUriOrigin(u) {
  const s = String(u), p = s.split("/");
  return s.startsWith("http") && p.length >= 3 ? p.slice(0, 3).join("/") : s;
}
async function jscDeriveTier(tobj, objs, verify) {
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
        if (subj["semantic-digest"] !== digest) continue;
        if (verify && verify.trusted) {   // verification mode (#24): the digest match must also be signed
          const env = r.obj["envelope-ref"] ? (verify.envelopes || new Map()).get(r.obj["envelope-ref"]) : undefined;
          const res = env !== undefined ? await jscVerifyEnvelope(env, r.obj, verify.trusted)
            : { status: "error", detail: "unsigned attestation (no envelope) cannot prove in verification mode" };
          if (res.status !== "verified") { if (verify.notes) verify.notes.push(`${r.obj.id}: ${res.detail}`); continue; }
        }
        return "authority-proven";
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
async function jscRiskCoverage(objs, verify) {
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
      tier = await jscDeriveTier(tobj, objs, verify && { ...verify, notes: null });
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
async function jscTailoringDutyErrors(objs, pinnedDecl, verify) {
  const errs = [], pd = pinnedDecl || new Map();
  for (const [oid, { type, obj: tobj }] of objs) {
    if (type !== "tailoring") continue;
    const tier = await jscDeriveTier(tobj, objs, verify && { ...verify, notes: null }), seen = new Set();
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
   Signatures: DSSE envelopes over attestations (backlog #24)
   ====================================================================
   The standard facet dsse-envelope@1 fixes what is signed (the
   Attestation's canonical form, annotations left out) and how the input of
   the signature is built (PAE of DSSE v1), but names no algorithm. The
   reference validator pins Ed25519 (RFC 8032) and so does this port, as the
   same arithmetic on big integers, so that both accept and reject the same
   inputs. Only SHA-512 is taken from the platform (WebCrypto).

   Trusted keys are an input: a map of signer URI to public key in hex. They
   never come from the bundle. Without a key for the signer an envelope is
   "unverified", which is not an error and proves nothing.

   Verification only. Nothing here can sign. */
const JSC_DSSE_PAYLOAD_TYPE = "application/vnd.oscal-semantic-core.attestation+json";
const JSC_ED_P = 2n ** 255n - 19n;
const JSC_ED_L = 2n ** 252n + 27742317777372353535851937790883648493n;
const jscEdMod = a => ((a % JSC_ED_P) + JSC_ED_P) % JSC_ED_P;
function jscEdPow(base, exp) {
  let r = 1n, b = jscEdMod(base);
  for (let e = exp; e > 0n; e >>= 1n) { if (e & 1n) r = r * b % JSC_ED_P; b = b * b % JSC_ED_P; }
  return r;
}
const JSC_ED_D = jscEdMod(-121665n * jscEdPow(121666n, JSC_ED_P - 2n));
/* points are [x, y, z, t] in extended coordinates */
function jscEdAdd(P, Q) {
  const [x1, y1, z1, t1] = P, [x2, y2, z2, t2] = Q;
  const a = jscEdMod((y1 - x1) * (y2 - x2)), b = jscEdMod((y1 + x1) * (y2 + x2));
  const c = jscEdMod(2n * t1 * t2 * JSC_ED_D), d = jscEdMod(2n * z1 * z2);
  const e = b - a, f = d - c, g = d + c, h = b + a;
  return [jscEdMod(e * f), jscEdMod(g * h), jscEdMod(f * g), jscEdMod(e * h)];
}
function jscEdMul(s, P) {
  let Q = [0n, 1n, 1n, 0n];
  for (; s > 0n; s >>= 1n) { if (s & 1n) Q = jscEdAdd(Q, P); P = jscEdAdd(P, P); }
  return Q;
}
const jscLeInt = bytes => { let n = 0n; for (let i = bytes.length - 1; i >= 0; i--) n = (n << 8n) | BigInt(bytes[i]); return n; };
const jscLeBytes = n => { const out = new Uint8Array(32); for (let i = 0; i < 32; i++) { out[i] = Number(n & 255n); n >>= 8n; } return out; };
function jscEdCompress(P) {
  const zi = jscEdPow(P[2], JSC_ED_P - 2n), x = P[0] * zi % JSC_ED_P, y = P[1] * zi % JSC_ED_P;
  return jscLeBytes(y | ((x & 1n) << 255n));
}
function jscEdDecompress(bytes) {
  let y = jscLeInt(bytes);
  const sign = y >> 255n;
  y &= (1n << 255n) - 1n;
  if (y >= JSC_ED_P) return null;
  const xx = jscEdMod((y * y - 1n) * jscEdPow(JSC_ED_D * y * y + 1n, JSC_ED_P - 2n));
  let x = jscEdPow(xx, (JSC_ED_P + 3n) / 8n);
  if (jscEdMod(x * x - xx) !== 0n) {
    x = x * jscEdPow(2n, (JSC_ED_P - 1n) / 4n) % JSC_ED_P;
    if (jscEdMod(x * x - xx) !== 0n) return null;
  }
  if (x % 2n !== sign) x = JSC_ED_P - x;
  return [x, y, 1n, x * y % JSC_ED_P];
}
const JSC_ED_B = jscEdDecompress(jscLeBytes(4n * jscEdPow(5n, JSC_ED_P - 2n) % JSC_ED_P));
async function jscSha512(bytes) {
  const subtle = typeof crypto !== "undefined" && crypto.subtle;
  if (!subtle) throw new Error("this page has no WebCrypto (open the app from localhost or over https)");
  return new Uint8Array(await subtle.digest("SHA-512", bytes));
}
const jscConcat = (...parts) => { const out = new Uint8Array(parts.reduce((n, p) => n + p.length, 0)); let at = 0; for (const p of parts) { out.set(p, at); at += p.length; } return out; };
const jscSameBytes = (a, b) => a.length === b.length && a.every((v, i) => v === b[i]);
/* pub, msg, sig: Uint8Array -> true when sig is an Ed25519 signature of msg under pub */
async function jscEd25519Verify(pub, msg, sig) {
  if (sig.length !== 64 || pub.length !== 32) return false;
  const A = jscEdDecompress(pub);
  if (!A) return false;
  const Rb = sig.slice(0, 32), s = jscLeInt(sig.slice(32));
  if (s >= JSC_ED_L) return false;
  const R = jscEdDecompress(Rb);
  if (!R) return false;
  const k = jscLeInt(await jscSha512(jscConcat(Rb, pub, msg))) % JSC_ED_L;
  return jscSameBytes(jscEdCompress(jscEdMul(s, JSC_ED_B)), jscEdCompress(jscEdAdd(R, jscEdMul(k, A))));
}
/* strict base64 and hex: anything outside the alphabet is an error, as in the reference */
function jscBase64Bytes(text) {
  const s = String(text);
  if (s.length % 4 || !/^[A-Za-z0-9+/]*={0,2}$/.test(s)) throw new Error("not valid base64");
  return Uint8Array.from(atob(s), c => c.charCodeAt(0));
}
function jscHexBytes(text) {
  const s = String(text);
  if (s.length % 2 || !/^[0-9a-fA-F]*$/.test(s)) throw new Error("not valid hex");
  return Uint8Array.from(s.match(/../g) || [], h => parseInt(h, 16));
}
const jscUtf8Bytes = text => new TextEncoder().encode(text);
const jscPae = (type, payload) => jscConcat(jscUtf8Bytes(`DSSEv1 ${type.length} `), type, jscUtf8Bytes(` ${payload.length} `), payload);
/* -> { status: "verified" | "unverified" | "error", detail }.
   The payload must be the Attestation's canonical form; the signature is
   over PAE(payloadType, payload). */
async function jscVerifyEnvelope(env, att, trusted) {
  const out = (status, detail) => ({ status, detail });
  if (!jscIsPlainObject(env)) return out("error", "envelope unreadable");
  if (env.payloadType !== JSC_DSSE_PAYLOAD_TYPE) return out("error", "wrong payloadType");
  let payload;
  try { payload = jscBase64Bytes(env.payload ?? ""); } catch (e) { return out("error", "payload is not valid base64"); }
  if (!jscSameBytes(payload, jscUtf8Bytes(jscRulesCanonical(att)))) return out("error", "payload != the Attestation's canonical form (attestation-binds)");
  const key = (trusted || {})[att.signer];
  if (key === undefined || key === null) return out("unverified", "no trusted key supplied for the signer");
  const pae = jscPae(jscUtf8Bytes(env.payloadType), payload);
  for (const sg of Array.isArray(env.signatures) ? env.signatures : []) {
    try {
      if (await jscEd25519Verify(jscHexBytes(key), pae, jscBase64Bytes((sg && sg.sig) ?? ""))) return out("verified", "");
    } catch (e) {
      if (/WebCrypto/.test(e.message)) return out("error", "the signature cannot be checked here: " + e.message);
      /* a signature or key that cannot be read does not verify; the next one is tried */
    }
  }
  return out("error", "no signature verifies under the trusted key (Ed25519)");
}

/* ====================================================================
   Composition of two bundles (D3.5, backlog #18)
   ====================================================================
   Two bundles that pin different minors of one major line of a facet
   resolve to the highest pinned minor, and the payloads of both are checked
   again under it. What does not fit is reported and never picked silently:
   pins that are not semver, two major lines, a payload that fails under the
   winner, one id at two versions, and one id and version with two meanings.
   objs: [[id, object]]; pins: {facet id: {version, schema}}.
   -> { resolutions: {facet id: version}, errors } */
function jscSemver(v) {
  const m = /^(\d+)\.(\d+)\.(\d+)$/.exec(String(v));
  return m ? m.slice(1).map(Number) : null;
}
function jscCompose(aObjs, aPins, bObjs, bPins) {
  const errors = [], resolutions = {};
  for (const fid of [...new Set([...Object.keys(aPins), ...Object.keys(bPins)])].sort()) {
    const pa = aPins[fid], pb = bPins[fid];
    if (!pa || !pb) { resolutions[fid] = (pa || pb).version; continue; }
    const sa = jscSemver(pa.version), sb = jscSemver(pb.version);
    if (!sa || !sb) { errors.push(`${fid}: non-semver pin (${pa.version} / ${pb.version}) — the registry policy is semver (D3.5)`); continue; }
    if (sa[0] !== sb[0]) { errors.push(`${fid}: major lines ${pa.version} vs ${pb.version} are incompatible (D3.5; reported, never a silent pick)`); continue; }
    const aWins = sa[1] > sb[1] || (sa[1] === sb[1] && sa[2] >= sb[2]), win = aWins ? pa : pb, schema = win.schema || { type: "object" };
    resolutions[fid] = win.version;
    for (const [side, objs] of [["A", aObjs], ["B", bObjs]]) {
      for (const [oid, o] of objs) {
        for (const [key, payload] of Object.entries((o && o.facets) || {})) {
          if (jscFacetBase(key) !== fid) continue;
          let found;
          try { found = jscSchemaCheck(schema, payload, schema).errors; }
          catch (e) { errors.push(`${fid}: ${side} ${oid}: payload cannot be re-validated under the resolved ${win.version}: ${e.message}`); continue; }
          if (found.length) errors.push(`${fid}: ${side} ${oid}: payload fails re-validation under the resolved ${win.version}: ${found[0].message.slice(0, 90)}`);
        }
      }
    }
  }
  const inA = new Map(aObjs);
  for (const [oid, o] of bObjs) {
    if (!inA.has(oid)) continue;
    const oa = inA.get(oid);
    if (oa.version !== o.version) errors.push(`${oid}: composed at two versions (${oa.version} vs ${o.version}) — cross-version resolution needs the lineage machinery, REPORTED`);
    else if (jscRulesCanonical(oa) !== jscRulesCanonical(o)) errors.push(`${oid}: same id + version but DIFFERENT semantic digests — divergent twins (reported, never silently picked)`);
  }
  return { resolutions, errors };
}
/* one side of a composition from a loaded graph */
function jscComposeSide(g) {
  const pins = {};
  for (const f of g.facetSchemas) if (f.def && f.def.id) pins[f.def.id] = { version: (f.pin && f.pin["exact-version"]) || f.def.version, schema: f.def.schema };
  return { objs: [...g.objects].map(([id, r]) => [id, r.obj]), pins };
}

/* ====================================================================
   Conditional apply (B.1.8, backlog #18)
   ====================================================================
   The one bounded conditional of the kernel: a trigger that is exactly one
   predicate (field-equals, param-equals or present; no nesting, at most one
   reference hop written "a->b") and an enforcement that is one primitive
   (param-bounds or code-from). Where the trigger holds on an object the
   enforcement is judged; elsewhere nothing happens. A trigger over a
   parameter that is declared but not bound is an error of its own, never
   "does not hold". The text of a failure is normative and kept. */
/* Python's json.dumps with its default separators, for the messages */
function jscPyJson(v) {
  if (Array.isArray(v)) return "[" + v.map(jscPyJson).join(", ") + "]";
  if (jscIsPlainObject(v)) return "{" + Object.entries(v).map(([k, x]) => jscPyJson(k) + ": " + jscPyJson(x)).join(", ") + "}";
  return JSON.stringify(v === undefined ? null : v).replace(/[\u0080-￿]/g, c => "\\u" + c.charCodeAt(0).toString(16).padStart(4, "0"));
}
const jscSameValue = (a, b) => jscRulesCanonical({ v: a }) === jscRulesCanonical({ v: b });
function jscPathGet(obj, path, objs) {
  const hops = String(path).split("->");
  if (hops.length > 2) return { st: "error", v: `path '${path}' exceeds the one-hop budget (B.2)` };
  let cur = obj;
  for (let i = 0; i < hops.length; i++) {
    if (i === 1) {   // follow the reference
      const tgt = typeof cur === "string" ? objs.get(cur) : null;
      if (!tgt) return { st: "error", v: `reference hop '${hops[0]}' does not resolve in-bundle` };
      cur = tgt.obj;
    }
    for (const part of hops[i].trim().split(".")) {
      if (!part) continue;
      if (jscIsPlainObject(cur) && Object.prototype.hasOwnProperty.call(cur, part)) cur = cur[part];
      else return { st: "absent", v: null };
    }
  }
  return { st: "ok", v: cur };
}
/* -> { verdict: "holds" | "holds-not" | "error", detail } */
function jscEvalPredicate(pred, obj, objs) {
  const out = (verdict, detail) => ({ verdict, detail });
  const kinds = ["field-equals", "param-equals", "present"].filter(k => k in pred);
  if (kinds.length !== 1 || ["and", "or", "not"].some(k => k in pred)) return out("error", "trigger must be exactly ONE predicate — no nesting, no boolean composition (B.2)");
  const k = kinds[0], a = pred[k];
  if (k === "field-equals") {
    const { st, v } = jscPathGet(obj, a.path, objs);
    if (st === "error") return out("error", v);
    if (st === "absent") return out("holds-not", `path '${a.path}' absent`);
    return out(jscSameValue(v, a.value) ? "holds" : "holds-not", `path '${a.path}' = ${jscPyJson(v).slice(0, 40)}, expected ${jscPyJson(a.value).slice(0, 40)}`);
  }
  if (k === "param-equals") {
    for (const s of obj.statements || []) {
      for (const p of s.parameters || []) {
        if (p.name !== a.name) continue;
        if (!("default" in p)) return out("error", `parameter '${a.name}' declared but UNBOUND — its own error via prose-params-resolve, never silently false (B.2)`);
        return out(jscSameValue(p.default, a.value) ? "holds" : "holds-not", `param '${a.name}' = ${jscPyJson(p.default).slice(0, 40)}`);
      }
    }
    return out("holds-not", `no parameter '${a.name}' declared`);
  }
  const { st, v } = jscPathGet(obj, a.path, objs);
  if (st === "error") return out("error", v);
  return out(st === "ok" ? "holds" : "holds-not", `path '${a.path}' ${st === "ok" ? "present" : "absent"}`);
}
/* -> the failures of one instance over the objects, each in the normative form */
function jscConditionalApply(inst, objs) {
  const errs = [], enf = inst.enforcement || {}, prim = enf.primitive;
  const rationale = inst.rationale === undefined ? "(none declared)" : inst.rationale;
  const id = inst["instance-id"] === undefined ? "None" : inst["instance-id"];
  for (const oid of [...objs.keys()].sort()) {
    const o = objs.get(oid).obj, { verdict, detail: why } = jscEvalPredicate(inst.trigger || {}, o, objs);
    if (verdict === "error") { errs.push(`FAIL [conditional-apply:${id}] on ${oid}\n  trigger: malformed/unevaluable: ${why}\n  rationale: ${rationale}`); continue; }
    if (verdict !== "holds") continue;
    let detail = null;
    if (prim === "param-bounds") {
      const decl = { type: enf.type === undefined ? "integer" : enf.type };
      for (const key of ["min", "max", "unit", "num", "tightening", "calendar-ref", "choices", "cardinality"]) if (key in enf) decl[key] = enf[key];
      let found = false;
      for (const s of o.statements || []) {
        for (const p of s.parameters || []) {
          if (p.name !== enf.parameter || !("default" in p)) continue;
          found = true;
          const v = jscParamCheck(decl, p.default);
          if (v !== "valid") detail = `parameter '${enf.parameter}' value ${jscPyJson(p.default).slice(0, 40)} outside the enforced bounds (${v})`;
        }
      }
      if (!found && (enf.required === undefined ? true : enf.required)) detail = `parameter '${enf.parameter}' not bound on any statement`;
    } else if (prim === "code-from") {
      const { st, v } = jscPathGet(o, enf.path === undefined ? "" : enf.path, objs);
      if (st !== "ok" || !(enf.codes || []).some(c => jscSameValue(c, v))) detail = `path '${enf.path}' = ${st === "ok" ? jscPyJson(v).slice(0, 40) : "absent"} not in the declared code list`;
    } else detail = `unknown enforcement primitive '${prim}' (the predicates you get are the predicates there are)`;
    if (detail) errs.push(`FAIL [conditional-apply:${id}] on ${oid}\n  trigger: ${why} held; enforcement [${prim}] failed: ${detail}\n  rationale: ${rationale}`);
  }
  return errs;
}

/* ====================================================================
   A whole set
   ====================================================================
   Everything this file can say about a loaded graph, in the order the
   reference validator works: the manifest, each object, the digests, the
   pinned files, references, the operation law, the kernel pin, the scales,
   risk coverage, facet payloads. `verified` is the result of jscVerify.
   opts.trusted, a map of signer URI to public key in hex, puts the check in
   verification mode: an envelope is then judged against the signer's key,
   and a Tailoring is authority-proven only through a verifying envelope.
   -> { findings: [{ kind: "error"|"note", area, object: id or null, message }],
        types: {type: count}, tiers: {tailoring id: tier}, coverage: report,
        signatures: {attestation id: "verified"|"unverified"|"error"|"missing"|"unsigned"} } */
async function jscCheckGraph(g, verified, opts) {
  const trusted = (opts && opts.trusted) || null;
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
  /* Envelopes: an attestation names a file beside the manifest; nothing signed contains its own signature.
     An attestation over the manifest cannot be listed in it (D3.1), so this check looks at every
     attestation of the set, listed or not, as the reference validator does since 2026-11-11 (before, it
     read only what the manifest lists and skipped every conformant attestation). A named envelope that
     does not resolve is an error in both cases. envelope-ref is a path in the manifest's directory or
     below it: an absolute path, a scheme or a ".." segment does not resolve. An attestation the manifest
     lists all the same is checked like any other, and its place is a note. */
  const envelopes = new Map(), signatures = {};
  for (const id of [...objs.keys()].sort()) {
    const r = objs.get(id), ref = r.obj["envelope-ref"];
    if (r.type !== "attestation") continue;
    if ((g.objects.get(id) || {}).entry) add("note", "manifest", id, "listed in the content manifest; an Attestation lies beside it (D3.1) - checked all the same");
    if (!ref) { signatures[id] = "unsigned"; add("note", "signature", id, "no envelope (unsigned attestation)"); continue; }
    const file = jscEnvelopeRefInside(ref) ? g.aux.find(a => a.path === ref) : undefined;
    if (!file) {
      signatures[id] = "missing";
      add("error", "signature", id, `envelope-ref '${ref}' does not resolve beside the manifest`);
      continue;
    }
    let env;
    try { env = JSON.parse(file.text); } catch (e) { signatures[id] = "error"; add("error", "signature", id, `${ref}: envelope unreadable: ${e.message}`); continue; }
    envelopes.set(ref, env);
    const res = await jscVerifyEnvelope(env, r.obj, trusted);
    signatures[id] = res.status;
    if (res.status === "error") add("error", "signature", id, `dsse: ${res.detail}`);
    else add("note", "signature", id, res.status === "verified" ? "signature VERIFIED (Ed25519)" : `signature UNVERIFIED - ${res.detail}`);
  }
  const verify = trusted ? { envelopes, trusted } : null;
  pass("reference", "error")(jscClosureErrors(objs));
  const pinnedSchemas = new Map(), pinnedDecl = new Map();
  for (const f of g.facetSchemas) {
    if (!f.def || !f.def.id) continue;
    pinnedSchemas.set(f.def.id, f.def.schema || { type: "object" });
    pinnedDecl.set(f.def.id, f.def["modifies-semantics"] || ["assessment", "tailoring", "selection", "rendering"]);   // a pin that omits it is dangerous by default
    const std = JSC_STDLIB_BY_ID.get(f.def.id);
    if (std && jscRulesCanonical(f.def.schema || {}) !== jscRulesCanonical(std.schema)) add("error", "facet", null, `${f.path}: pin of stdlib facet ${f.def.id} DIVERGES from the normative descriptor (D26)`);
  }
  pass("tailoring", "error")(await jscTailoringDutyErrors(objs, pinnedDecl, verify));
  const pins = new Map([...g.scales.values()].filter(x => x.pin).map(x => [x.def.id, x.pin]));
  const sc = jscCheckScales([...g.scales.values()].map(x => x.def), objs, pins);
  pass("scale", "error")(sc.errors); pass("scale", "note")(sc.notes);
  const cov = await jscRiskCoverage(objs, verify);
  pass("risk", "error")(cov.errors); pass("risk", "note")([...cov.notes, ...jscRiskLinkNotes(objs)]);
  pass("facet", "error")(jscFacetErrors([...objs].map(([id, r]) => [id, r.obj]), pinnedSchemas));
  const tiers = {};
  for (const [id, r] of objs) {
    if (r.type !== "tailoring") continue;
    const why = [];
    tiers[id] = await jscDeriveTier(r.obj, objs, verify && { ...verify, notes: why });
    why.forEach(m => add("note", "tailoring", id, "not proven by " + m));
    if (tiers[id] === "authority-proven" && !trusted) add("note", "tailoring", id, "authority-proven by a digest match; the signature is UNVERIFIED without trusted keys");
  }
  return { findings, types, tiers, coverage: cov.report, signatures };
}
const jscRulesBeside = r => r.type === "attestation" && !r.entry;
/* envelope-ref stays inside the bundle: relative, no scheme or drive letter, no ".." segment */
const jscEnvelopeRefInside = ref => typeof ref === "string" && ref !== "" && !/^[A-Za-z][A-Za-z0-9+.-]*:/.test(ref)
  && !/^[\/\\]/.test(ref) && !ref.split(/[\/\\]/).includes("..");

if (typeof module !== "undefined" && module.exports) {
  module.exports = { JSC_MODALITIES, JSC_ELAPSED_UNITS, JSC_CALENDAR_UNITS, jscModalityVerdict, jscParamCheck,
    jscDecimalCompare, jscExpandRefs, jscSetParents, jscSelection, jscUriOrigin, jscDeriveTier, jscTargetKey,
    jscResolveTailoring, jscTextify, JSC_NEXT, jscCanMove, jscComposeRelationship,
    jscSchemaCheck, jscShapeErrors, jscMatchTypes, jscTypeOf, jscTypedObjects, JSC_KERNEL_TYPES, JSC_RISK_RULES, jscClosureErrors,
    jscKernelNeeded, jscKernelPinErrors, jscRiskRuleViolations, jscRiskIsLive, jscRiskJustifies, JSC_NO_TAILORING, jscRiskCoverage,
    jscRiskLinkNotes, jscScaleDefinitionErrors, jscMatrixErrors, jscRiskLevels, jscMatrixCell, jscScaleErrors, jscCheckScales,
    jscOptionalEmptyViolations, jscObjectErrors, jscFacetErrors, jscTailoringDutyErrors, jscAttestationVerdict, jscCheckGraph,
    JSC_DSSE_PAYLOAD_TYPE, jscEd25519Verify, jscVerifyEnvelope, jscSemver, jscCompose, jscComposeSide, jscPathGet, jscEvalPredicate, jscConditionalApply };
}
