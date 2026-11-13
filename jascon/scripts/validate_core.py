#!/usr/bin/env python3
"""JASCON - gate-item-2 executable validator.

Runs, in order:
1. CONFORMANCE CORPUS: JCS vectors (canonical form + empty-omission rule),
   modality-lattice vectors, parameter vectors, tailoring vectors
   (same-target conflict, tier-scoped Deviation duties), attestation
   bi-modal vectors.
2. BUNDLE VALIDATION over every converted_examples bundle + the skill's
   example bundle: type inference (an object must match EXACTLY ONE of the
   ELEVEN kernel shapes - shape-disjointness is a conformance property),
   closed-shape schema validation, code systems, by-statement facet keys
   vs. host statement ids (D10 rev), {param:} token binding
   (prose-params-resolve), optional-empty-container rule (D3.3), manifest completeness +
   both digests re-verified per object.
3. RISK (CP-RISK-1, kernel 2.0.0): Risk is the tenth kernel type; the
   schema carries RISK-1..6 (named on failure by risk_rule_violations),
   this file adds the closure rules (RISK-7/8), typed Risk edges
   (RISK-12), the state machine (C.3c), the Deviation link note (RISK-9)
   and the risk-coverage primitive (B.1.9): for every Tailoring, which
   selected requirement is justified by NO live Risk - the ISO/IEC 27001
   6.1.3 d question, computed instead of audited by hand.
   `--require-risk-basis` turns uncovered selections into failures.
4. CHECK (CP-CHECK-1, kernel 2.0.0): Check is the eleventh kernel type -
   a typed fact contract plus a flat conjunction over twelve comparators
   (check-verdict, B.1.10; patterns are I-Regexp, RFC 9485, matched by a
   built-in state-set engine). CHECK-1..7 hold the Check to its
   requirement and its own contract; CHECK-8..14 recompute every verdict
   an Assessment records, its aggregate, and its parameter values
   against the Tailoring it names; CHECK-15 walks the evidence chain
   (record -> raw outputs) in the store beside the bundle.
5. ADVICE (CP-ADVICE-1, proposed): an advice pack is a bundle whose
   manifest carries a pack header and whose objects are Components - a
   vendor's recommendations as one published file. ADVICE-1..3 hold a
   pack to being advice; 4..7 hold capabilities and the edges that cite
   them (capability-ref has a grammar and is closure-required); 8..10
   hold the vendor's manifest a set keeps under packs/sha256/ to the
   objects in the set; 11 is import. `--import-advice SET PACK` prints
   what an import would do and its receipt, and writes nothing.
6. WHO DECIDED, AND WHEN (CP-AUTHOR-1): `provenance` {author-ref, date} on
   a Tailoring and its selects, excludes and operations, on a Risk and
   its ratings, on an Implementation and a Finding; `decided` and
   `review-due` on a Deviation; `date` on an authorization. The schema
   leaves all of it optional. AUTHOR-1..4 REPORT what is missing, one
   line per object and rule, and `--require-authors` turns the lines
   into failures. REVIEW-1 reports a `review-due` that has passed, on an
   approved Deviation and on a Risk still managed. It reads the date of
   the run (UTC); `--as-of YYYY-MM-DD` sets the date instead. This is the
   one place where the file reads a clock, and nothing fails by it.

Exit 0 = all green. Usage: uv run --with jsonschema validate_core.py [bundle-dir ...]
"""
import json, hashlib, os, re, sys, copy, collections, base64, datetime
from decimal import Decimal
import jsonschema

# canonical decimal string (D3.4; rev P10 #37: leading zeros AND negative
# zero are non-canonical spellings — one value, one spelling)
# `\Z`, not `$`: Python's `$` also matches before a line break that ends the
# value, so "1.5\n" would be a decimal here and in no ECMA-262 engine (#68).
DECIMAL_RE = r"^(-?[1-9][0-9]*(\.[0-9]+)?|0(\.[0-9]+)?|-0\.[0-9]*[1-9][0-9]*)\Z"

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
SKILL = os.path.join(ROOT, "jascon")
SCHEMA = json.load(open(os.path.join(SKILL, "schemas", "jascon-2.0.0.schema.json"), encoding="utf-8"))
CONF = os.path.join(SKILL, "conformance")

TYPES = ["requirement", "requirementSet", "tailoring", "mapping", "component",
         "implementation", "assessment", "finding", "attestation", "risk", "check"]

# A `pattern` of a JSON Schema is an ECMA-262 regular expression (JSON Schema
# 2020-12, Core 6.4 with Validation 6.3.3), and jsonschema hands it to
# Python's `re` unchanged. The two dialects read two things differently that
# the kernel's patterns use (backlog #68):
#   `$`  ECMA-262: the end of the value.  Python: also before one line break
#        that ends the value - so "2026-11-13\n" was a date here, and a
#        digest with a line break at its end a digest.
#   `.`  ECMA-262: any character but U+000A, U+000D, U+2028, U+2029.
#        Python: any character but U+000A.
# ecma_pattern() writes the pattern so that `re` reads both as ECMA-262 does.
# Nothing else is translated: a class escape (\d \w \s \b) keeps the meaning
# its host gives it, and no pattern of the kernel schema or of the standard
# library uses one. The PowerShell twin does the same for .NET; the app runs
# the patterns in the dialect they were written in.
def ecma_pattern(p):
    out, i, in_class = [], 0, False
    while i < len(p):
        c = p[i]
        if c == "\\":                       # an escape: the next character is not an operator
            out.append(p[i:i + 2]); i += 2; continue
        if in_class: in_class = c != "]"
        elif c == "[": in_class = True
        elif c == "$": c = r"\Z"
        elif c == ".": c = "[^\n\r\u2028\u2029]"
        out.append(c); i += 1
    return "".join(out)

_ECMA_RX = {}
def _pattern(validator, pattern, instance, schema):
    if not validator.is_type(instance, "string"): return
    rx = _ECMA_RX.get(pattern)
    if rx is None: rx = _ECMA_RX[pattern] = re.compile(ecma_pattern(pattern))
    if not rx.search(instance):
        yield jsonschema.ValidationError(f"{instance!r} does not match {pattern!r}")

REGISTRY = jsonschema.validators.extend(jsonschema.validators.Draft202012Validator, {"pattern": _pattern})
VALIDATORS = {t: REGISTRY({"$ref": f"#/$defs/{t}", "$defs": SCHEMA["$defs"]}) for t in TYPES}
VALIDATORS["contentManifest"] = REGISTRY({"$ref": "#/$defs/contentManifest", "$defs": SCHEMA["$defs"]})
VALIDATORS["scale"] = REGISTRY({"$ref": "#/$defs/scale", "$defs": SCHEMA["$defs"]})
VALIDATORS["due"] = REGISTRY({"$ref": "#/$defs/due", "$defs": SCHEMA["$defs"]})
VALIDATORS["date"] = REGISTRY({"$ref": "#/$defs/date", "$defs": SCHEMA["$defs"]})
VALIDATORS["dateTime"] = REGISTRY({"$ref": "#/$defs/dateTime", "$defs": SCHEMA["$defs"]})
# CP-CHECK-1: file shapes beside the bundle, not object types
VALIDATORS["evidenceRecord"] = REGISTRY({"$ref": "#/$defs/evidenceRecord", "$defs": SCHEMA["$defs"]})
VALIDATORS["checkObservation"] = REGISTRY({"$ref": "#/$defs/checkObservation", "$defs": SCHEMA["$defs"]})

# normative stdlib facet descriptors (gate 2); payload validation per backlog #17
STDLIB, STDLIB_RAW = {}, {}
for _fn in sorted(os.listdir(os.path.join(SKILL, "schemas", "stdlib"))):
    if _fn.endswith(".json"):
        _d = json.load(open(os.path.join(SKILL, "schemas", "stdlib", _fn), encoding="utf-8"))
        STDLIB[_d["id"]] = REGISTRY(_d["schema"])
        STDLIB_RAW[_d["id"]] = _d["schema"]

# reference taxonomy (backlog #16): closure-required refs MUST land in-bundle;
# landmark refs (Mapping endpoints, party/authority URIs, evidence, external
# schema/reference URLs, attestation subjects — self-verifying via digest)
# resolve outside the bundle by design.
def closure_errors(objs):
    """objs: id -> (type, obj). Returns list of error strings."""
    errs = []
    def need(oid, ref, what):
        if ref not in objs:
            errs.append(f"{oid}: closure-required {what} does not resolve in-bundle: {ref}")
    for oid, (t, o) in objs.items():
        for ca in o.get("canonical-alias", []) or []:   # backlog #14: same-content is checkable
            tgt = objs.get(ca.get("of"))
            if tgt and content_digest(o) != content_digest(tgt[1]):
                errs.append(f"{oid}: canonical-alias claims SAME content as {ca.get('of')} "
                            f"but content digests differ — a meaning change must use `replaces` (backlog #14)")
        if t == "requirementSet":
            for m in o.get("members", []): need(oid, m["ref"], "member ref")
        elif t == "tailoring":
            # a Tailoring edge is typed, like a Risk edge (RISK-12): a set-ref
            # that resolves to anything but a RequirementSet selects nothing,
            # silently - and an exclude that names neither a Requirement nor a
            # Set removes nothing, silently
            for s in o.get("selects", []):
                if "set-ref" in s:
                    need(oid, s["set-ref"], "selects set-ref")
                    tgt = objs.get(s["set-ref"])
                    if tgt and tgt[0] != "requirementSet":
                        errs.append(f"{oid}: selects set-ref resolves to a {tgt[0]}, not a RequirementSet: {s['set-ref']} "
                                    f"(D13: a selection names a Set - chaining runs on the resolved package, never by reference)")
            for e in o.get("excludes", []):
                need(oid, e["ref"], "excludes ref")
                tgt = objs.get(e["ref"])
                if tgt and tgt[0] not in ("requirement", "requirementSet"):
                    errs.append(f"{oid}: excludes ref resolves to a {tgt[0]}, neither a Requirement nor a RequirementSet: {e['ref']} "
                                f"(D13: an exclusion scopes out requirements - one, or a Set's members)")
            for op in o.get("operations", []):
                need(oid, op["requirement-ref"], "operation requirement-ref")
                tgt = objs.get(op["requirement-ref"])
                if tgt and op.get("statement-id") and tgt[0] == "requirement":
                    if op["statement-id"] not in {s["id"] for s in tgt[1]["statements"]}:
                        errs.append(f"{oid}: operation statement-id '{op['statement-id']}' names no statement of {op['requirement-ref']}")
        elif t == "implementation":
            need(oid, o["component-ref"], "component-ref")
            need(oid, o["requirement-ref"], "requirement-ref")
            for sb in o.get("satisfied-by", []):
                inh = sb.get("inherited-from")
                if inh:
                    comp = objs.get(inh["component-ref"])
                    if not comp:
                        errs.append(f"{oid}: inherited-from component does not resolve in-bundle: {inh['component-ref']}")
                    elif inh["basis-ref"] not in {a["id"] for a in comp[1].get("authorizations", [])}:
                        errs.append(f"{oid}: basis-ref '{inh['basis-ref']}' names no authorization of {inh['component-ref']} (D5 edge-local rule)")
        elif t == "finding":
            need(oid, o["assessment-ref"], "assessment-ref")
            need(oid, o["requirement-ref"], "requirement-ref")
            # risk-refs are LANDMARK: the assessor's Finding points into the
            # organisation's risk register, which normally lives in another
            # bundle. Like a Mapping endpoint, the edge binds IF the target is
            # present: an in-bundle target must be a Risk (RISK-12)
            for rr in o.get("risk-refs", []) or []:
                tgt = objs.get(rr)
                if tgt and tgt[0] != "risk":
                    errs.append(f"{oid}: risk-refs entry resolves in-bundle to a {tgt[0]}, not a Risk: {rr} "
                                f"(RISK-12: a Risk edge is typed - a mis-aimed ref is a wrong statement, not a loose one)")
        elif t == "risk":
            # RISK-7: the controls a risk leans on are the organisation's own
            # selected requirements - closure-required like Implementation.requirement-ref
            for tr in o.get("treatments", []) or []:
                need(oid, tr["requirement-ref"], "treatments requirement-ref (RISK-7)")
                tgt = objs.get(tr["requirement-ref"])
                if tgt and tgt[0] != "requirement":
                    # RISK-12: without the type check a Set id here passes RISK-7 and
                    # surfaces as a misleading RISK-11 ("no Tailoring selects <set>")
                    errs.append(f"{oid}: treatments requirement-ref resolves to a {tgt[0]}, not a Requirement: "
                                f"{tr['requirement-ref']} (RISK-12: a Risk edge is typed - coverage joins on Requirement ids)")
                elif tgt:
                    sids = {st["id"] for st in tgt[1]["statements"]}
                    for sid in tr.get("statement-ids", []) or []:
                        if sid not in sids:
                            errs.append(f"{oid}: treatments statement-id '{sid}' names no statement of "
                                        f"{tr['requirement-ref']} (RISK-8: clause precision is addressable or it is prose)")
            # RISK-7b: the assets at risk are Components of this bundle
            for cref in o.get("component-refs", []) or []:
                need(oid, cref, "component-refs (RISK-7)")
                tgt = objs.get(cref)
                if tgt and tgt[0] != "component":
                    errs.append(f"{oid}: component-refs entry resolves to a {tgt[0]}, not a Component: {cref} "
                                f"(RISK-12: a Risk edge is typed - the asset at risk is a Component)")
            # the Statement(s) of Applicability this risk's treatment belongs
            # to: closure-required and typed, like the other join edges
            for tref in o.get("tailoring-refs", []) or []:
                need(oid, tref, "tailoring-refs (RISK-7)")
                tgt = objs.get(tref)
                if tgt and tgt[0] != "tailoring":
                    errs.append(f"{oid}: tailoring-refs entry resolves to a {tgt[0]}, not a Tailoring: {tref} "
                                f"(RISK-12: a Risk edge is typed - the scope of a treatment is a Tailoring)")
            # RISK-13: levels compare within ONE scale and never across (D23)
            ra, rr = o.get("rating"), o.get("residual-rating")
            if ra and rr and ra.get("scale-ref") != rr.get("scale-ref"):
                errs.append(f"{oid}: residual-rating is on {rr.get('scale-ref')}, rating on {ra.get('scale-ref')} "
                            f"(RISK-13: {RISK_RULES['RISK-13']})")
            # ... and so do the two inputs of a level, where both sides carry
            # them: residual likelihood on the likelihood scale, residual
            # impact on the impact scale
            for part in ("likelihood", "impact"):
                pa, pr = (ra or {}).get(part), (rr or {}).get(part)
                if pa and pr and pa.get("scale-ref") != pr.get("scale-ref"):
                    errs.append(f"{oid}: residual-rating {part} is on {pr.get('scale-ref')}, rating {part} on "
                                f"{pa.get('scale-ref')} (RISK-13: {RISK_RULES['RISK-13']})")
            # owner-ref, threat-refs, shared-with-ref, acceptance.approver-ref,
            # rating.scale-ref are landmark (parties, threat catalogs, scales)
        elif t == "mapping":
            for side in ("source", "target"):   # endpoints are landmark; scopes bind IF the endpoint is present
                ep = objs.get(o.get(f"{side}-ref"))
                if ep and ep[0] == "requirement":
                    sids = {s["id"] for s in ep[1]["statements"]}
                    for sc in o.get(f"{side}-scope", []):
                        sid = sc.split(":", 1)[1]
                        if sid not in sids:
                            errs.append(f"{oid}: {side}-scope '{sc}' names no statement of the in-bundle endpoint")
    # membership graphs are DAGs (D21; P10 #39): overlapping membership is
    # legal, cycles are not — naive baseline expansion / nearest-Set search
    # would loop forever on a cyclic graph.
    color = {}
    for root, (rt, _ro) in list(objs.items()):
        if rt != "requirementSet" or root in color:
            continue
        stack = [[root, [m["ref"] for m in objs[root][1].get("members", [])], 0]]
        color[root] = 1
        while stack:
            sid, refs, i = stack[-1]
            if i >= len(refs):
                color[sid] = 2; stack.pop(); continue
            stack[-1][2] += 1
            adv = refs[i]
            tgt = objs.get(adv)
            if not tgt or tgt[0] != "requirementSet":
                continue
            if color.get(adv) == 1:
                errs.append(f"{sid}: RequirementSet membership cycle: "
                            f"{' -> '.join([f[0] for f in stack] + [adv])} "
                            f"(D21: membership graphs are acyclic; P10 #39)")
            elif adv not in color:
                color[adv] = 1
                stack.append([adv, [m["ref"] for m in objs[adv][1].get("members", [])], 0])
    return errs

def facet_errors(objs_or_obj, pinned, path="?"):
    """Validate facet payloads (backlog #17): stdlib facets against the
    normative descriptors, others against the bundle-pinned schemas;
    private: is ignored by definition; anything else is unregistered."""
    errs = []
    items = objs_or_obj if isinstance(objs_or_obj, list) else [(path, objs_or_obj)]
    for pth, obj in items:
        for key, payload in (obj.get("facets") or {}).items():
            base = key.rsplit("@", 1)[0]
            if key.startswith("private:") or base.startswith("private:"):
                continue   # modifies-semantics [] by definition (D10)
            v = STDLIB.get(base) or pinned.get(base)
            if v is None:
                errs.append(f"{pth}: unregistered facet '{key}' — not stdlib, not pinned in the manifest, not private: (dangerous-by-default, D10)")
                continue
            err = next(iter(v.iter_errors(payload)), None)
            if err:
                errs.append(f"{pth}: facet '{key}' payload violates its schema: {err.message[:110]} @ {'/'.join(map(str, err.absolute_path))}")
    return errs

# tier anchor (backlog #19, layered - D13 rev 2): id-prefix derivation gives
# authority-CLAIMED; an in-bundle Attestation whose signer shares the selected
# content's origin and whose subjects include the Tailoring (digest-verified)
# upgrades to authority-PROVEN; anything else is consumer. Deviation duties
# bind at consumer tier only; claimed/proven are reported distinctly.
STDLIB_DECL = {}
for _fn in sorted(os.listdir(os.path.join(SKILL, "schemas", "stdlib"))):
    if _fn.endswith(".json"):
        _d = json.load(open(os.path.join(SKILL, "schemas", "stdlib", _fn), encoding="utf-8"))
        STDLIB_DECL[_d["id"]] = _d.get("modifies-semantics", [])

def uri_origin(u):
    p = str(u).split("/")
    return "/".join(p[:3]) if str(u).startswith("http") and len(p) >= 3 else str(u)

def derive_tier(tobj, objs, sdig_fn, envelopes=None, trusted=None, notes=None):
    # Content origin resolves THROUGH selected Sets to their members (and
    # through op targets): a self-minted wrapper Set around foreign content
    # must not launder consumer into authority-claimed (gate-3 finding: the
    # CR26 rev5-odp-overlay wraps NIST controls in a FedRAMP Set).
    # Gate 4 (#24): with `trusted` supplied the validator runs in
    # VERIFICATION MODE — authority-proven additionally requires a verifying
    # DSSE envelope; an unsigned attestation can no longer prove.
    origins = set()
    def set_member_origins(sid, depth=0):
        tgt = objs.get(sid)
        if depth > 4 or not tgt or tgt[0] != "requirementSet" or not tgt[1].get("members"):
            origins.add(uri_origin(sid)); return
        for m in tgt[1]["members"]:
            mt = objs.get(m["ref"])
            if mt and mt[0] == "requirementSet":
                set_member_origins(m["ref"], depth + 1)
            else:
                origins.add(uri_origin(m["ref"]))
    for s in tobj.get("selects", []):
        if "set-ref" in s:
            set_member_origins(s["set-ref"])
        else:
            origins.add("<predicate>")
    for op in tobj.get("operations", []) or []:
        origins.add(uri_origin(op.get("requirement-ref", "")))
    origins.discard("")
    content_origin = next(iter(origins)) if len(origins) == 1 and "<predicate>" not in origins else None
    claimed = content_origin is not None and uri_origin(tobj["id"]) == content_origin
    if content_origin:
        for (t, o) in objs.values():
            if t != "attestation" or uri_origin(o.get("signer", "")) != content_origin:
                continue
            for subj in o.get("subject-semantic-digests", []):
                if isinstance(subj, dict) and subj.get("id") == tobj["id"] \
                   and subj.get("semantic-digest") == sdig_fn(tobj):
                    if trusted is not None:      # verification mode (#24)
                        env = (envelopes or {}).get(o.get("envelope-ref"))
                        if o.get("envelope-ref") and env is not None:
                            st, why = verify_envelope(env, o, trusted)
                        else:
                            st, why = "error", "unsigned attestation (no envelope) cannot prove in verification mode"
                        if st != "verified":
                            if notes is not None:
                                notes.append(f"{o.get('id')}: {why}")
                            continue
                    return "authority-proven"
    return "authority-claimed" if claimed else "consumer"

def tailoring_duty_errors(objs, pinned_decl=None, sdig_fn=None, envelopes=None, trusted=None):
    """Op-law enforcement with the derived tier (D13 + #19; #24 verification mode)."""
    errs = []
    pd = pinned_decl or {}
    for oid, (t, tobj) in objs.items():
        if t != "tailoring": continue
        tier = derive_tier(tobj, objs, sdig_fn or sdig, envelopes=envelopes, trusted=trusted)
        seen_targets = set()
        for op in tobj.get("operations", []):
            # D13: two operations addressing the same target within one
            # Tailoring = validation error (P10 #30 — was vector-only)
            tkey = (op.get("requirement-ref"), op.get("statement-id"),
                    op.get("parameter"), op.get("field"), op.get("facet"))
            if tkey in seen_targets:
                errs.append(f"{oid}: two operations address the same target "
                            f"{[x for x in tkey if x]} within one Tailoring "
                            f"(D13: override rides Tailoring-of-Tailoring chaining, never in-place; P10 #30)")
            seen_targets.add(tkey)
            has_dev = "deviation" in op or "deviation-ref" in op
            duty = None
            if op["op"] == "set-modality":
                tgt = objs.get(op["requirement-ref"])
                if tgt and tgt[0] == "requirement":
                    stmt = next((s for s in tgt[1]["statements"] if s["id"] == op.get("statement-id")), None)
                    if stmt:
                        v = modality_verdict_py(stmt["modality"], op["modality"])
                        if v != "monotone": duty = f"non-monotone set-modality ({v})"
            elif op["op"] == "replace-prose" and op.get("intent") == "substantive":
                duty = "substantive replace-prose"
            elif op["op"] in ("attach-facet", "detach-facet"):
                fid = str(op.get("facet", ""))
                base = fid.rsplit("@", 1)[0]
                if fid.startswith("private:") or base.startswith("private:"):
                    pass                     # modifies-semantics [] by definition (D10)
                elif base in STDLIB_DECL or base in pd:
                    decl = STDLIB_DECL.get(base, pd.get(base))
                    if decl: duty = f"{op['op']} of a semantics-bearing facet {decl}"
                else:                        # neither stdlib nor pinned nor private: (P10 #29)
                    errs.append(f"{oid}: {op['op']} references facet '{fid}' that is neither "
                                f"stdlib, nor pinned in the manifest, nor private: "
                                f"(dangerous-by-default, D10; P10 #29)")
            elif op["op"] == "set-parameter":
                tgt = objs.get(op["requirement-ref"])
                stmt = next((s for s in tgt[1]["statements"] if s["id"] == op.get("statement-id")), None) \
                    if tgt and tgt[0] == "requirement" else None
                pdecl = next((p for p in stmt.get("parameters", []) if p["name"] == op.get("parameter")), None) \
                    if stmt else None
                if pdecl:
                    verdict = param_check(pdecl, op.get("value"))
                    if verdict == "invalid":   # type/cardinality/choice/range failure — malformed at ANY tier, not Deviation-escapable (D13)
                        errs.append(f"{oid}: set-parameter '{op.get('parameter')}' value fails the declared type/bounds "
                                    f"(D13; not Deviation-escapable)")
                    elif verdict == "deviation-required":
                        duty = "out-of-bounds / against-tightening set-parameter"
            elif op["op"] == "remove-relation":
                rel = op.get("relation")
                if isinstance(rel, dict) and rel.get("type") == "required":
                    duty = "remove-relation of a `required` edge"
            if duty and not has_dev and tier == "consumer":
                errs.append(f"{oid}: {duty} without a Deviation at consumer tier "
                            f"(derived tier: {tier}; B.1.6/D13 rev 2)")
    return errs

OBL_ORD = {"unspecified": 0, "may": 1, "should": 2, "must": 3}
PRO_ORD = {"unspecified": 0, "should-not": 1, "must-not": 2}
def modality_verdict_py(frm, to):
    if frm == to or frm == "unspecified": return "monotone"
    if to == "unspecified": return "easing"
    if frm == "may" and to == "may-only": return "monotone"
    if frm == "may-only" and to == "may": return "easing"
    if "may-only" in (frm, to): return "axis-change"
    if frm in OBL_ORD and to in OBL_ORD: return "monotone" if OBL_ORD[to] >= OBL_ORD[frm] else "easing"
    if frm in PRO_ORD and to in PRO_ORD: return "monotone" if PRO_ORD[to] >= PRO_ORD[frm] else "easing"
    return "axis-change"

# per-type optional array/object fields (D3.3: optional empties MUST be absent;
# required fields stay even when empty)
OPTIONAL_CONTAINERS = {"aliases", "canonical-alias", "replaces", "relations", "facets",
                       "annotations", "parameters", "deviations", "excludes",
                       "source-scope", "target-scope", "evidence-refs", "statement-refs",
                       "capabilities", "authorizations", "actions", "choices",
                       "threat-refs", "component-refs", "treatments", "risk-refs", "tailoring-refs",
                       "statement-ids", "applies-when", "check-results", "derived-from"}
REQUIRED_CONTAINERS = {"statements", "members", "selects", "operations", "subject-refs",
                       "satisfied-by", "subject-semantic-digests", "objects", "facet-schemas"}

fails = []
counts = collections.Counter()
def ok(section): counts[section] += 1
def fail(section, msg):
    counts[section + ":FAIL"] += 1
    fails.append(f"[{section}] {msg}")

# ---------------- canonical form ----------------
def _canon(o):
    # RFC 8785 member ordering: UTF-16 code units, not code points (P9b-3).
    if isinstance(o, dict):
        return {k: _canon(o[k]) for k in sorted(o.keys(), key=lambda s: s.encode("utf-16-be"))}
    if isinstance(o, list):
        return [_canon(x) for x in o]
    return o
def canonical(obj):
    o = copy.deepcopy(obj)
    if isinstance(o, dict): o.pop("annotations", None)
    return json.dumps(_canon(o), separators=(",", ":"), ensure_ascii=False)
def sdig(obj):
    return "sha256:" + hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()

def content_digest(obj):
    # sameness modulo identity (backlog #14): strip the fields a rebrand may
    # legitimately change, then digest what remains. canonical-alias asserts
    # SAME content at a new home; if these differ, it should be `replaces`.
    x = copy.deepcopy(obj)
    for k in ("id", "version", "label", "canonical-alias", "replaces"):
        x.pop(k, None)
    return sdig(x)

# ---------------- DSSE verification engine (gate 4, backlog #24) ----------------
# dsse-envelope@1 fixes the payload (the Attestation's canonical form,
# annotations excluded) and PAE per DSSE v1 but deliberately pins no
# algorithm; the reference engine pins Ed25519 (RFC 8032), dependency-free.
# Key distribution is authority-local (the R6 pattern): trusted keys arrive
# as INPUT (--trusted-keys file / vector fixtures), never from the bundle.
DSSE_PAYLOAD_TYPE = "application/vnd.jascon.attestation+json"
_ED_P = 2**255 - 19
_ED_L = 2**252 + 27742317777372353535851937790883648493
_ED_D = (-121665 * pow(121666, _ED_P - 2, _ED_P)) % _ED_P

def _ed_add(P, Q):
    (x1, y1, z1, t1), (x2, y2, z2, t2) = P, Q
    a = (y1 - x1) * (y2 - x2) % _ED_P
    b = (y1 + x1) * (y2 + x2) % _ED_P
    c = 2 * t1 * t2 * _ED_D % _ED_P
    d = 2 * z1 * z2 % _ED_P
    e, f, g, h = b - a, d - c, d + c, b + a
    return (e * f % _ED_P, g * h % _ED_P, f * g % _ED_P, e * h % _ED_P)

def _ed_mul(s, P):
    Q = (0, 1, 1, 0)
    while s:
        if s & 1: Q = _ed_add(Q, P)
        P = _ed_add(P, P); s >>= 1
    return Q

def _ed_compress(P):
    x, y, z, _ = P
    zi = pow(z, _ED_P - 2, _ED_P)
    x, y = x * zi % _ED_P, y * zi % _ED_P
    return (y | ((x & 1) << 255)).to_bytes(32, "little")

def _ed_decompress(b):
    y = int.from_bytes(b, "little")
    sign = y >> 255; y &= (1 << 255) - 1
    if y >= _ED_P: return None
    xx = (y * y - 1) * pow(_ED_D * y * y + 1, _ED_P - 2, _ED_P) % _ED_P
    x = pow(xx, (_ED_P + 3) // 8, _ED_P)
    if (x * x - xx) % _ED_P:
        x = x * pow(2, (_ED_P - 1) // 4, _ED_P) % _ED_P
        if (x * x - xx) % _ED_P: return None
    if x % 2 != sign: x = _ED_P - x
    return (x, y, 1, x * y % _ED_P)

_ED_B = _ed_decompress((4 * pow(5, _ED_P - 2, _ED_P) % _ED_P).to_bytes(32, "little"))

def _ed_expand(seed):
    h = hashlib.sha512(seed).digest()
    a = int.from_bytes(h[:32], "little")
    a &= (1 << 254) - 8; a |= (1 << 254)
    return a, h[32:]

def ed25519_public(seed):
    a, _ = _ed_expand(seed)
    return _ed_compress(_ed_mul(a, _ED_B))

def ed25519_sign(seed, msg):
    a, prefix = _ed_expand(seed)
    A = _ed_compress(_ed_mul(a, _ED_B))
    r = int.from_bytes(hashlib.sha512(prefix + msg).digest(), "little") % _ED_L
    R = _ed_compress(_ed_mul(r, _ED_B))
    k = int.from_bytes(hashlib.sha512(R + A + msg).digest(), "little") % _ED_L
    return R + ((r + k * a) % _ED_L).to_bytes(32, "little")

def ed25519_verify(pub, msg, sig):
    if len(sig) != 64 or len(pub) != 32: return False
    A = _ed_decompress(pub)
    if A is None: return False
    Rb, s = sig[:32], int.from_bytes(sig[32:], "little")
    if s >= _ED_L: return False
    R = _ed_decompress(Rb)
    if R is None: return False
    k = int.from_bytes(hashlib.sha512(Rb + pub + msg).digest(), "little") % _ED_L
    return _ed_compress(_ed_mul(s, _ED_B)) == _ed_compress(_ed_add(R, _ed_mul(k, A)))

def _pae(ptype, payload):
    return (b"DSSEv1 " + str(len(ptype)).encode() + b" " + ptype +
            b" " + str(len(payload)).encode() + b" " + payload)

def verify_envelope(env, att, trusted):
    """-> (status, detail): verified | unverified (no key for signer) |
    error (binds / signature). Payload MUST equal the Attestation's
    canonical form; signature input is PAE(payloadType, payload)."""
    if not isinstance(env, dict):
        return ("error", "envelope unreadable")
    if env.get("payloadType") != DSSE_PAYLOAD_TYPE:
        return ("error", "wrong payloadType")
    try:
        payload = base64.b64decode(env.get("payload", ""), validate=True)
    except Exception:
        return ("error", "payload is not valid base64")
    if payload != canonical(att).encode("utf-8"):
        return ("error", "payload != the Attestation's canonical form (attestation-binds)")
    key = (trusted or {}).get(att.get("signer"))
    if key is None:
        return ("unverified", "no trusted key supplied for the signer")
    pae = _pae(env["payloadType"].encode(), payload)
    for sg in env.get("signatures", []) or []:
        try:
            if ed25519_verify(bytes.fromhex(key), pae, base64.b64decode(sg.get("sig", ""), validate=True)):
                return ("verified", "")
        except Exception:
            continue
    return ("error", "no signature verifies under the trusted key (Ed25519)")

# ---------------- bundle-composition engine (gate 4, D3.5 / backlog #18) ----------------
# "Composing two bundles pinning different minors of one major line resolves
# deterministically to the highest pinned minor with both payload sets
# re-validated — incompatibility is a reported error, never a silent pick."
def _semver(v):
    m = re.fullmatch(r"([0-9]+)\.([0-9]+)\.([0-9]+)", str(v))
    return tuple(int(x) for x in m.groups()) if m else None

def compose(a_objs, a_pins, b_objs, b_pins):
    """objs: [(oid, obj)]; pins: {facet-base-id: {"version", "schema"}}.
    Returns (resolutions, errors)."""
    errors, resolutions = [], {}
    for fid in sorted(set(a_pins) | set(b_pins)):
        pa, pb = a_pins.get(fid), b_pins.get(fid)
        if pa and pb:
            sa, sb = _semver(pa["version"]), _semver(pb["version"])
            if sa is None or sb is None:
                errors.append(f"{fid}: non-semver pin ({pa['version']} / {pb['version']}) — the registry policy is semver (D3.5)")
                continue
            if sa[0] != sb[0]:
                errors.append(f"{fid}: major lines {pa['version']} vs {pb['version']} are incompatible (D3.5; reported, never a silent pick)")
                continue
            win = pa if sa >= sb else pb
            resolutions[fid] = win["version"]
            v = REGISTRY(win.get("schema") or {"type": "object"})
            for side, objs in (("A", a_objs), ("B", b_objs)):
                for oid, o in objs:
                    for key, payload in (o.get("facets") or {}).items():
                        if key.rsplit("@", 1)[0] == fid:
                            err = next(iter(v.iter_errors(payload)), None)
                            if err:
                                errors.append(f"{fid}: {side} {oid}: payload fails re-validation under the resolved {win['version']}: {err.message[:90]}")
        else:
            resolutions[fid] = (pa or pb)["version"]
    a_ids = {oid: o for oid, o in a_objs}
    for oid, o in b_objs:
        if oid in a_ids:
            oa = a_ids[oid]
            if oa.get("version") != o.get("version"):
                errors.append(f"{oid}: composed at two versions ({oa.get('version')} vs {o.get('version')}) — cross-version resolution needs the lineage machinery, REPORTED")
            elif sdig(oa) != sdig(o):
                errors.append(f"{oid}: same id + version but DIFFERENT semantic digests — divergent twins (reported, never silently picked)")
    return resolutions, errors

def _load_compose_side(bdir):
    m = json.load(open(os.path.join(bdir, "content-manifest.json"), encoding="utf-8"))
    objs = []
    for e in m.get("objects", []):
        o = json.load(open(os.path.join(bdir, e["path"]), encoding="utf-8"))
        objs.append((o["id"], o))
    pins = {}
    for fe in m.get("facet-schemas", []):
        sd = json.load(open(os.path.join(bdir, fe["path"]), encoding="utf-8"))
        pins[sd["id"]] = {"version": fe.get("exact-version", sd.get("version")), "schema": sd.get("schema")}
    return objs, pins

# ---------------- conditional-apply engine (gate 4, B.1.8 / backlog #18) ----------------
# The one bounded conditional: trigger = exactly one B.2 predicate (≤1
# reference hop, no nesting on either side); enforcement = one instantiated
# primitive. Facets instantiate; they never define new computation.
def _path_get(obj, path, objs):
    """Dotted kernel-field path; ONE '->' segment may dereference a
    URI-valued field to another in-bundle object (the ≤1-hop budget)."""
    hops = path.split("->")
    if len(hops) > 2:
        return ("error", f"path '{path}' exceeds the one-hop budget (B.2)")
    cur = obj
    for i, seg in enumerate(hops):
        if i == 1:                       # follow the reference
            tgt = objs.get(cur) if isinstance(cur, str) else None
            if tgt is None:
                return ("error", f"reference hop '{hops[0]}' does not resolve in-bundle")
            cur = tgt[1]
        for part in seg.strip().split("."):
            if not part: continue
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                return ("absent", None)
    return ("ok", cur)

def eval_predicate(pred, obj, objs):
    """-> (verdict, detail): holds | holds-not | error."""
    kinds = [k for k in ("field-equals", "param-equals", "present") if k in pred]
    if len(kinds) != 1 or any(k in pred for k in ("and", "or", "not")):
        return ("error", "trigger must be exactly ONE predicate — no nesting, no boolean composition (B.2)")
    k = kinds[0]
    a = pred[k]
    if k == "field-equals":
        st, v = _path_get(obj, a["path"], objs)
        if st == "error": return ("error", v)
        if st == "absent": return ("holds-not", f"path '{a['path']}' absent")
        return ("holds" if v == a["value"] else "holds-not",
                f"path '{a['path']}' = {json.dumps(v)[:40]}, expected {json.dumps(a['value'])[:40]}")
    if k == "param-equals":
        for s in obj.get("statements", []) or []:
            for p in s.get("parameters", []) or []:
                if p.get("name") == a["name"]:
                    if "default" not in p:
                        return ("error", f"parameter '{a['name']}' declared but UNBOUND — its own error via prose-params-resolve, never silently false (B.2)")
                    return ("holds" if p["default"] == a["value"] else "holds-not",
                            f"param '{a['name']}' = {json.dumps(p.get('default'))[:40]}")
        return ("holds-not", f"no parameter '{a['name']}' declared")
    st, v = _path_get(obj, a["path"], objs)
    if st == "error": return ("error", v)
    return ("holds" if st == "ok" else "holds-not", f"path '{a['path']}' {'present' if st == 'ok' else 'absent'}")

def conditional_apply(inst, objs):
    """B.1.8: enforcement verdict where the trigger holds; no-op elsewhere.
    Returns error strings in the normative FAIL format."""
    errs = []
    enf = inst.get("enforcement", {})
    prim = enf.get("primitive")
    for oid, (t, o) in sorted(objs.items()):
        verdict, why = eval_predicate(inst.get("trigger", {}), o, objs)
        if verdict == "error":
            errs.append(f"FAIL [conditional-apply:{inst.get('instance-id')}] on {oid}\n"
                        f"  trigger: malformed/unevaluable: {why}\n"
                        f"  rationale: {inst.get('rationale', '(none declared)')}")
            continue
        if verdict != "holds":
            continue
        detail = None
        if prim == "param-bounds":
            decl = {"type": enf.get("type", "integer")}
            for kk in ("min", "max", "unit", "num", "tightening", "calendar-ref", "choices", "cardinality"):
                if kk in enf: decl[kk] = enf[kk]
            found = False
            for s in o.get("statements", []) or []:
                for p in s.get("parameters", []) or []:
                    if p.get("name") == enf.get("parameter") and "default" in p:
                        found = True
                        v = param_check(decl, p["default"])
                        if v != "valid":
                            detail = f"parameter '{enf.get('parameter')}' value {json.dumps(p['default'])[:40]} outside the enforced bounds ({v})"
            if not found and enf.get("required", True):
                detail = f"parameter '{enf.get('parameter')}' not bound on any statement"
        elif prim == "code-from":
            st, v = _path_get(o, enf.get("path", ""), objs)
            if st != "ok" or v not in enf.get("codes", []):
                detail = f"path '{enf.get('path')}' = {json.dumps(v)[:40] if st == 'ok' else 'absent'} not in the declared code list"
        else:
            detail = f"unknown enforcement primitive '{prim}' (the predicates you get are the predicates there are)"
        if detail:
            errs.append(f"FAIL [conditional-apply:{inst.get('instance-id')}] on {oid}\n"
                        f"  trigger: {why} held; enforcement [{prim}] failed: {detail}\n"
                        f"  rationale: {inst.get('rationale', '(none declared)')}")
    return errs

def optional_empty_violations(obj, path="$"):
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in OPTIONAL_CONTAINERS and isinstance(v, (list, dict)) and len(v) == 0:
                out.append(f"{path}.{k}")
            out += optional_empty_violations(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out += optional_empty_violations(v, f"{path}[{i}]")
    return out

# ---------------- the number domain (D3.9, NUMBER-1) ----------------
# A JSON number in a bundle is an integer written in plain digits, of
# magnitude at most 2^53 - 1. Two reasons, one rule. RANGE: beyond 2^53 an
# IEEE double no longer holds every integer, so a JavaScript tool reads
# 9007199254740993 as ...992 while Python reads it exactly - two digests,
# two verdicts for one file. SPELLING: `1.0`, `1e3` and `-0` are second
# spellings of 1, 1000 and 0; this validator would hash `1.0` as written,
# a JavaScript one as `1`. The rule rejects; it never rewrites (D3.4: one
# value, one spelling, and the spelling rides validation, not the digest).
#
# Two checks, because the spelling is gone once a text is parsed:
#   number_spelling_violations(text)  wherever a bundle file is read
#   number_violations(value)          on every object, and in check-verdict
# A fraction is a `decimal`, which is a string.
NUMBER_MAX = 2 ** 53 - 1
NUMBER_RULES = {
    "NUMBER-1": "a JSON number is an integer in plain digits, of magnitude at most 2^53 - 1 (9007199254740991) - "
                "no fraction, no exponent, no -0; a number two tools read differently has two digests and two verdicts",
}
# one pass over a text that already parsed as JSON: strings are consumed
# whole (so digits inside them are never looked at), everything else that
# starts like a number is a number token
_NUMBER_TOKEN = re.compile(r'"[^"\\]*(?:\\.[^"\\]*)*"|-?[0-9][0-9.eE+-]*')
_NUMBER_PLAIN = re.compile(r"-?(?:0|[1-9][0-9]*)\Z")
_NUMBER_MAX_DIGITS = str(NUMBER_MAX)

def number_spelling_violations(text):
    """text: a JSON text. -> the number tokens that break NUMBER-1, as written.
    Compares digits as text, so no float ever takes part in the decision."""
    out = []
    for m in _NUMBER_TOKEN.finditer(text):
        tok = m.group(0)
        if tok[0] == '"': continue
        digits = tok.lstrip("-")
        if (not _NUMBER_PLAIN.match(tok) or tok == "-0" or len(digits) > len(_NUMBER_MAX_DIGITS)
                or (len(digits) == len(_NUMBER_MAX_DIGITS) and digits > _NUMBER_MAX_DIGITS)):
            out.append(tok)
    return out

def in_number_domain(x):
    return isinstance(x, int) and not isinstance(x, bool) and -NUMBER_MAX <= x <= NUMBER_MAX

def number_violations(obj, path="$"):
    """-> where a parsed value holds a number outside the domain. The backstop
    for values that never were a text here (vectors, objects a tool built)."""
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items(): out += number_violations(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj): out += number_violations(v, f"{path}[{i}]")
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool) and not in_number_domain(obj):
        out.append(f"{path} = {obj!r}")
    return out

def number_failures(section, rel, raw=None, obj=None):
    """Reports NUMBER-1 for one bundle file: its text if given, its value if given."""
    bad = []
    if raw is not None:
        bad = [f"written as {t}" for t in number_spelling_violations(raw.decode("utf-8", "replace"))]
    if not bad and obj is not None:
        bad = number_violations(obj)
    if bad:
        more = f" (and {len(bad) - 1} more)" if len(bad) > 1 else ""
        fail(section, f"{rel}: [NUMBER-1] {bad[0]}{more} - {NUMBER_RULES['NUMBER-1']}")

# ---------------- modality lattice ----------------
OBL = {"unspecified": 0, "may": 1, "should": 2, "must": 3}
PRO = {"unspecified": 0, "should-not": 1, "must-not": 2}
def modality_verdict(frm, to):
    if frm == to: return "monotone"
    if frm == "unspecified": return "monotone"
    if to == "unspecified": return "easing"
    if frm == "may" and to == "may-only": return "monotone"
    if frm == "may-only" and to == "may": return "easing"
    if "may-only" in (frm, to): return "axis-change"
    fo, to_o = frm in OBL, to in OBL
    fp, tp = frm in PRO, to in PRO
    if fo and to_o: return "monotone" if OBL[to] >= OBL[frm] else "easing"
    if fp and tp: return "monotone" if PRO[to] >= PRO[frm] else "easing"
    return "axis-change"

# ---------------- parameter law ----------------
def param_check(decl, value):
    t = decl.get("type")
    if t == "calendar-period" and "calendar-ref" not in decl: return "invalid"
    if value is None: return "invalid"
    if t == "choice":
        allowed = [c["value"] for c in decl.get("choices", [])]
        if isinstance(value, list):
            # multi-select: legal only on cardinality `many`, every element declared
            # (gate-3: the CR26 CTL overlay binds NIST many-cardinality ODPs as lists)
            if decl.get("cardinality") != "many" or not value:
                return "invalid"
            return "valid" if all(v in allowed for v in value) else "deviation-required"
        return "valid" if value in allowed else "deviation-required"
    if t == "integer":
        if not in_number_domain(value): return "invalid"      # NUMBER-1: beyond 2^53 two tools read two values
        if "min" in decl and value < decl["min"]: return "deviation-required"
        if "max" in decl and value > decl["max"]: return "deviation-required"
        return "valid"
    if t == "decimal":
        # canonical decimal STRING (D3.4): no leading zeros, no negative zero
        # (P10 #37); scale is lexically significant (trailing zeros
        # distinguish "1.5" from "1.50" by design). Bounds compare exactly
        # via Decimal — float() loses precision beyond 2^53 (P10 #37d).
        if not isinstance(value, str) or not re.match(DECIMAL_RE, value): return "invalid"
        v = Decimal(value)
        if "min" in decl and v < Decimal(str(decl["min"])): return "deviation-required"
        if "max" in decl and v > Decimal(str(decl["max"])): return "deviation-required"
        return "valid"
    if t in ("elapsed-duration", "calendar-period"):
        ELAPSED = {"seconds", "minutes", "hours"}; CAL = {"days", "bizdays", "weeks", "months", "years"}
        if not isinstance(value, dict) or "num" not in value or "unit" not in value: return "invalid"
        cls = ELAPSED if t == "elapsed-duration" else CAL
        if value["unit"] not in cls: return "invalid"   # unit-class boundary is semantic
        if decl.get("tightening") == "lower":
            base = decl.get("num")
            if base is not None and value["unit"] == decl.get("unit") and value["num"] > base:
                return "deviation-required"
        return "valid"
    return "valid"

# ---------------- 1) conformance corpus ----------------
def run_jcs():
    v = json.load(open(os.path.join(CONF, "jcs-vectors.json"), encoding="utf-8"))
    for case in v["vectors"]:
        name = case["name"]
        if "canonical" in case and case.get("canonical") is not None:
            got = canonical(case["input"])
            if got == case["canonical"]: ok("jcs")
            else: fail("jcs", f"{name}: got {got!r}")
        elif "authoring-input" in case:
            viol = optional_empty_violations(case["authoring-input"])
            verdict = "invalid" if viol else "valid"
            if verdict == case["expected"]: ok("jcs")
            else: fail("jcs", f"{name}: expected {case['expected']}, got {verdict} ({viol})")
        elif "number-text" in case:
            # NUMBER-1 on a JSON text (a vector file cannot carry `1.0` as a
            # number: its own parser would have read it already)
            text = case["number-text"]
            viol = number_spelling_violations(text) or number_violations(json.loads(text))
            verdict = "invalid" if viol else "valid"
            got = canonical(json.loads(text)) if verdict == "valid" else None
            if verdict == case["expected"] and (verdict == "invalid" or got == case["canonical-text"]): ok("jcs")
            else: fail("jcs", f"{name}: expected {case['expected']} {case.get('canonical-text', '')}, got {verdict} {got or viol}")

def run_modality():
    v = json.load(open(os.path.join(CONF, "modality-vectors.json"), encoding="utf-8"))
    for case in v["vectors"]:
        got = modality_verdict(case["from"], case["to"])
        if got == case["verdict"]: ok("modality")
        else: fail("modality", f"{case['from']} -> {case['to']}: expected {case['verdict']}, got {got}")

def run_parameters():
    v = json.load(open(os.path.join(CONF, "parameter-vectors.json"), encoding="utf-8"))
    for case in v["vectors"]:
        got = param_check(case["parameter"], case["value"])
        if got == case["verdict"]: ok("parameter")
        else: fail("parameter", f"{case['name']}: expected {case['verdict']}, got {got}")

def run_tailoring():
    v = json.load(open(os.path.join(CONF, "tailoring-vectors.json"), encoding="utf-8"))
    for case in v["vectors"]:
        ops = case.get("operations", [])
        verdict = "valid"
        seen = set()
        for op in ops:
            key = (op.get("requirement-ref"), op.get("statement-id"),
                   op.get("parameter"), op.get("field"), op.get("facet"), op.get("op"))
            tkey = key[:5]
            if tkey in seen: verdict = "error"
            seen.add(tkey)
        if verdict != "error":
            for op in ops:
                needs_dev = False
                if op["op"] == "set-modality" and "base-modality" in case:
                    needs_dev = modality_verdict(case["base-modality"], op["modality"]) != "monotone"
                if op["op"] == "replace-prose" and op.get("intent") == "substantive":
                    needs_dev = True
                if op["op"] == "set-parameter" and "parameter-decl" in case:   # backlog #25
                    pv = param_check(case["parameter-decl"], op.get("value"))
                    if pv == "invalid": verdict = "error"                       # malformed at any tier
                    elif pv == "deviation-required": needs_dev = True
                if op["op"] == "remove-relation" and isinstance(op.get("relation"), dict) \
                        and op["relation"].get("type") == "required":           # backlog #25 (B.3)
                    needs_dev = True
                if op["op"] in ("attach-facet", "detach-facet"):                # P10 #29
                    fid = str(op.get("facet", "")); base = fid.rsplit("@", 1)[0]
                    fdecls = case.get("facet-decls", {})
                    if fid.startswith("private:") or base.startswith("private:"):
                        pass                                # [] by definition (D10)
                    elif base in fdecls:
                        if fdecls[base]: needs_dev = True   # semantics-bearing
                    else:
                        verdict = "error"                   # unknown facet id, any tier
                if needs_dev and case.get("tier") == "consumer" and "deviation" not in op and "deviation-ref" not in op:
                    verdict = "error"
        if verdict == case["verdict"]: ok("tailoring")
        else: fail("tailoring", f"{case['name']}: expected {case['verdict']}, got {verdict}")

def run_attestation():
    v = json.load(open(os.path.join(CONF, "attestation-vectors.json"), encoding="utf-8"))
    for case in v["vectors"]:
        sc = case["scenario"]
        signed = sc["subject"]
        signed_sem = sdig(signed)
        signed_pkg = "sha256:" + hashlib.sha256(json.dumps(signed, indent=1, ensure_ascii=False).encode()).hexdigest()
        delivered = copy.deepcopy(sc.get("delivered-subject", signed))
        mut = sc["delivered-mutation"]
        if mut == "reindent":
            delivered_bytes = json.dumps(delivered, indent=4, ensure_ascii=False).encode()
        elif mut == "annotation-added":
            delivered["annotations"] = {"web_name": "chrome"}
            delivered_bytes = json.dumps(delivered, indent=1, ensure_ascii=False).encode()
        else:
            delivered_bytes = json.dumps(delivered, indent=1, ensure_ascii=False).encode()
        del_pkg = "sha256:" + hashlib.sha256(delivered_bytes).hexdigest()
        del_sem = sdig(json.loads(delivered_bytes.decode()))
        if del_sem != signed_sem: got = "tamper"
        elif del_pkg == signed_pkg: got = "full-match"
        else: got = "semantic-match"
        if got == case["expected"]: ok("attestation")
        else: fail("attestation", f"{case['name']}: expected {case['expected']}, got {got}")

def run_facets():
    v = json.load(open(os.path.join(CONF, "facet-vectors.json"), encoding="utf-8"))
    for case in v["vectors"]:
        pinned = {k: REGISTRY(s) for k, s in (case.get("pinned") or {}).items()}
        errs = facet_errors(case["object"], pinned, case["name"])
        got = "invalid" if errs else "valid"
        if got == case["expected"]: ok("facet")
        else: fail("facet", f"{case['name']}: expected {case['expected']}, got {got} ({errs[:1]})")

def run_references():
    v = json.load(open(os.path.join(CONF, "reference-vectors.json"), encoding="utf-8"))
    for case in v["vectors"]:
        objs = {}
        for o in case["objects"]:
            t = inferType_single(o)
            if t: objs[o["id"]] = (t, o)
        errs = closure_errors(objs)
        if len(errs) == case["expected-errors"]: ok("reference")
        else: fail("reference", f"{case['name']}: expected {case['expected-errors']} errors, got {len(errs)} ({errs[:2]})")

def inferType_single(o):
    m = [t for t in TYPES if VALIDATORS[t].is_valid(o)]
    return m[0] if len(m) == 1 else None

DEV_NEXT = {"investigating": {"pending", "withdrawn"}, "pending": {"approved", "withdrawn"},
            "approved": set(), "withdrawn": set()}
FIND_NEXT = {"open": {"in-remediation", "closed"}, "in-remediation": {"closed"}, "closed": set()}
# C.3c Risk states: identified -> assessed -> treated -> retired; forward only,
# skipping allowed (RISK-2/3 make the skipped fields mandatory anyway);
# retired is terminal - a recurring risk is a NEW Risk, like a recurring Finding
RISK_NEXT = {"identified": {"assessed", "treated", "retired"}, "assessed": {"treated", "retired"},
             "treated": {"retired"}, "retired": set()}
def run_tiers():
    v = json.load(open(os.path.join(CONF, "tier-vectors.json"), encoding="utf-8"))
    for case in v["vectors"]:
        # substitute live-computed digests BEFORE type inference — the
        # COMPUTE placeholder would otherwise fail the digest pattern
        by_id = {o["id"]: o for o in case["objects"]}
        for o in case["objects"]:
            for subj in o.get("subject-semantic-digests", []) or []:
                if isinstance(subj, dict) and subj.get("semantic-digest") == "COMPUTE":
                    tgt = by_id.get(subj["id"])
                    if tgt: subj["semantic-digest"] = sdig(tgt)
        objs = {}
        for o in case["objects"]:
            t = inferType_single(o)
            if t: objs[o["id"]] = (t, o)
        tobj = next(o for (t, o) in objs.values() if t == "tailoring")
        tier = derive_tier(tobj, objs, sdig)
        errs = tailoring_duty_errors(objs)
        got = "invalid" if errs else "valid"
        okv = tier == case["expected-tier"] and got == case["expected"]
        if okv: ok("tier")
        else: fail("tier", f"{case['name']}: expected {case['expected-tier']}/{case['expected']}, got {tier}/{got} ({errs[:1]})")

def run_composition():
    v = json.load(open(os.path.join(CONF, "composition-vectors.json"), encoding="utf-8"))
    for case in v["vectors"]:
        a, b = case["a"], case["b"]
        res, errs = compose([(o["id"], o) for o in a.get("objects", [])], a.get("pins", {}),
                            [(o["id"], o) for o in b.get("objects", [])], b.get("pins", {}))
        okc = True
        exp = case.get("expected-errors", [])
        if len(errs) != len(exp):
            okc = False
        else:
            for frag in exp:
                if not any(frag in e for e in errs): okc = False
        for fid, ver in (case.get("expected-resolutions") or {}).items():
            if res.get(fid) != ver: okc = False
        if okc: ok("composition")
        else: fail("composition", f"{case['name']}: expected {exp}/{case.get('expected-resolutions')}, "
                                  f"got {[e[:80] for e in errs]}/{res}")

# ---------------- the kernel-version pin (backlog #44) ----------------
# A content manifest MAY carry `kernel-version`. Absent, the bundle is
# 1.0.0 content - every 1.0.0 manifest stays valid, and a 1.0.0 tool keeps
# reading it. A bundle that carries anything the 1.0.0 kernel cannot type
# MUST pin the kernel that can (KERNEL-1), and a tool meeting a pin it does
# not implement stops there, with both versions in the message (KERNEL-2) -
# instead of "matches NO type" on the first object it cannot read.
KERNEL_VERSION = "2.0.0"
KERNEL_SUPPORTED = ("1.0.0", "2.0.0")      # 2.0.0 is a superset of 1.0.0, measured

def deviations_of(t, o):
    """-> [(where, Deviation)]: every Deviation an object carries - in its
    `deviations` list and, on a Tailoring, inline on an operation."""
    out = [(f"deviations[{i}]", d) for i, d in enumerate(o.get("deviations") or []) if isinstance(d, dict)]
    if t == "tailoring":
        out += [(f"operations[{i}].deviation", op["deviation"]) for i, op in enumerate(o.get("operations") or [])
                if isinstance(op, dict) and isinstance(op.get("deviation"), dict)]
    return out

def kernel_needed(objs, manifest=None):
    """-> (minimum kernel version the content needs, the first object that
    needs it). 2.0.0 added the Risk type, Finding.risk-refs, pinned
    scale definitions, the Check type, Assessment.check-results and
    .tailoring-ref, Finding.check-ref, the pack header of a manifest,
    statement-ids on a capability (CP-ADVICE-1), product-version on a
    Component (author decision 2026-11-12), and the fields of CP-AUTHOR-1:
    `provenance` where 1.0.0 had none, `decided` and `review-due` on a
    Deviation, `date` on an authorization."""
    if manifest and manifest.get("scales"): return "2.0.0", "the manifest pins scale definitions"
    if manifest and manifest.get("pack"): return "2.0.0", "the manifest carries a pack header"
    for oid in sorted(objs):
        t, o = objs[oid]
        if t == "risk": return "2.0.0", f"{oid} is a Risk"
        if t == "finding" and o.get("risk-refs"): return "2.0.0", f"{oid} carries risk-refs"
        if t == "check": return "2.0.0", f"{oid} is a Check"
        if t == "assessment" and (o.get("check-results") or o.get("tailoring-ref")):
            return "2.0.0", f"{oid} carries check results"
        if t == "finding" and o.get("check-ref"): return "2.0.0", f"{oid} carries a check-ref"
        if t == "component" and any(c.get("statement-ids") for c in o.get("capabilities", []) or []):
            return "2.0.0", f"{oid} names clauses on a capability (statement-ids)"
        if t == "component" and "product-version" in o:
            return "2.0.0", f"{oid} names the product version it describes (product-version)"
        if t in ("tailoring", "implementation", "finding") and "provenance" in o:
            return "2.0.0", f"{oid} names its author (provenance)"
        if t == "tailoring" and any("provenance" in e for k in ("selects", "excludes", "operations")
                                    for e in o.get(k, []) or [] if isinstance(e, dict)):
            return "2.0.0", f"{oid} names the author of a select, an exclude or an operation (provenance)"
        if any("decided" in d or "review-due" in d for _, d in deviations_of(t, o)):
            return "2.0.0", f"{oid} carries a Deviation with `decided` or `review-due`"
        if t == "component" and any("date" in a for a in o.get("authorizations", []) or [] if isinstance(a, dict)):
            return "2.0.0", f"{oid} dates an authorization"
    return "1.0.0", None

def kernel_pin_errors(manifest, objs):
    """-> [error] for the manifest's kernel-version pin against this tool
    and against the bundle's own content."""
    pin = manifest.get("kernel-version")
    if pin is not None and pin not in KERNEL_SUPPORTED:
        return [f"manifest pins kernel-version {pin}; this validator implements {KERNEL_VERSION} "
                f"and reads {', '.join(KERNEL_SUPPORTED)} (KERNEL-2: a tool stops at a kernel it does not "
                f"implement, and says which)"]
    need, why = kernel_needed(objs, manifest)
    if need != "1.0.0" and pin != need:
        return [f"{why}, which needs kernel {need}, but the manifest "
                f"{'pins kernel-version ' + pin if pin else 'pins no kernel-version'} "
                f"(KERNEL-1: content beyond 1.0.0 names its kernel, so that an older tool can say "
                f"what it is missing)"]
    return []

def run_kernel():
    v = json.load(open(os.path.join(CONF, "kernel-vectors.json"), encoding="utf-8"))
    for case in v["vectors"]:
        objs = {}
        for o in case["objects"]:
            t = inferType_single(o)
            if t: objs[o["id"]] = (t, o)
        errs = [] if VALIDATORS["contentManifest"].is_valid(case["manifest"]) else ["manifest schema violation"]
        if not errs: errs = kernel_pin_errors(case["manifest"], objs)
        okc = len(errs) == case.get("expected-fails", 0) and len(objs) == len(case["objects"])
        for frag in case.get("expected-frags", []):
            if not any(frag in e for e in errs): okc = False
        if okc: ok("kernel")
        else: fail("kernel", f"{case['name']}: expected {case.get('expected-fails', 0)} {case.get('expected-frags')}, got {errs}")
    for case in v.get("shape-vectors", []):
        # closed shapes of fields that 2.0.0 typed or added; an invalid one names its rule
        m = [t for t in TYPES if VALIDATORS[t].is_valid(case["document"])]
        got = "valid" if m == [case["kind"]] else "invalid"
        named = sorted({r for r, _ in date_rule_violations(case["document"])})
        if got == case["expected"] and named == sorted(case.get("expected-rules", [])): ok("kernel")
        else: fail("kernel", f"shape {case['name']}: expected {case['expected']} {case.get('expected-rules', [])}, got {got} {named}")

# ---------------- pinned scale definitions (SCALE-1..3) ----------------
# A scale is the organisation's own: how many levels, and what they are
# called. Its definition is a small file the manifest pins by digest, the
# way it pins facet schemas - not an object, not a kernel type. Levels are
# listed from lowest to highest. A `scale-ref` that no pin answers stays
# what it was: a landmark, its levels opaque.
def scale_definition_errors(sd, pin=None):
    """SCALE-1: a pinned definition has the scale shape, the id and version
    its pin states, and no level twice."""
    name = (pin or {}).get("path") or (sd.get("id") if isinstance(sd, dict) else "?")
    if not VALIDATORS["scale"].is_valid(sd):
        e = next(VALIDATORS["scale"].iter_errors(sd))
        return [f"{name}: not a scale definition: {e.message[:110]} (SCALE-1)"]
    errs = []
    codes = [lv["level"] for lv in sd["levels"]]
    dup = sorted({c for c in codes if codes.count(c) > 1})
    if dup: errs.append(f"{name}: level(s) {dup} listed twice - a level has one place in the order (SCALE-1)")
    if pin and (pin.get("id") != sd["id"] or pin.get("exact-version") != sd["version"]):
        errs.append(f"{name}: pinned as {pin.get('id')} {pin.get('exact-version')}, the file says "
                    f"{sd['id']} {sd['version']} (SCALE-1: the pin and the definition agree)")
    return errs

def matrix_errors(scales):
    """SCALE-1, second half: a scale that carries a `matrix` names the two
    pinned scales it combines, has exactly one cell for every pair of their
    levels, and every cell is one of its own levels. A matrix that fails is
    reported and then ignored (SCALE-4 is not asked of a broken table)."""
    errs = []
    for sid in sorted(scales):
        sd = scales[sid]; mx = sd.get("matrix")
        if not mx: continue
        mine = [lv["level"] for lv in sd["levels"]]
        bad = []
        ls, is_ = scales.get(mx["likelihood-scale"]), scales.get(mx["impact-scale"])
        for role, ref, tgt in (("likelihood-scale", mx["likelihood-scale"], ls), ("impact-scale", mx["impact-scale"], is_)):
            if tgt is None: bad.append(f"its {role} {ref} is not pinned in this bundle")
        if not bad:
            lk = [lv["level"] for lv in ls["levels"]]; ik = [lv["level"] for lv in is_["levels"]]
            cells = mx["cells"]
            extra = sorted(set(cells) - set(lk))
            if extra: bad.append(f"rows {extra} are no levels of the likelihood scale")
            for l in lk:
                row = cells.get(l)
                if row is None: bad.append(f"no row for likelihood '{l}'"); continue
                miss = [i for i in ik if i not in row]; more = sorted(set(row) - set(ik))
                if miss: bad.append(f"row '{l}' has no cell for impact {miss}")
                if more: bad.append(f"row '{l}' has cells {more} that are no levels of the impact scale")
                wrong = sorted({v for v in row.values() if v not in mine})
                if wrong: bad.append(f"row '{l}' yields {wrong}, no level(s) of this scale")
        if bad:
            errs.append(f"{sid}: matrix is not usable: {'; '.join(bad[:4])} (SCALE-1: a matrix has one cell per "
                        f"pair of levels of its two pinned scales, each cell a level of its own scale)")
            sd.pop("matrix")
    return errs

def _risk_levels(o):
    """every level a Risk states: (where, level, scale-ref)"""
    for field in ("rating", "residual-rating"):
        r = o.get(field)
        if not isinstance(r, dict): continue
        yield field, r.get("level"), r.get("scale-ref")
        for part in ("likelihood", "impact"):
            p = r.get(part)
            if isinstance(p, dict): yield f"{field}.{part}", p.get("level"), p.get("scale-ref")

def scale_errors(scales, objs):
    """scales: {scale id: definition}. -> (errors, notes).
    SCALE-2: a level stated on a pinned scale is one of that scale's levels.
    SCALE-3 (SHOULD): a residual level is not above the level it remains of."""
    errs, notes = [], []
    order = {sid: {lv["level"]: i for i, lv in enumerate(sd["levels"])} for sid, sd in scales.items()}
    for oid in sorted(objs):
        t, o = objs[oid]
        if t != "risk": continue
        seen = {}
        for where, level, sref in _risk_levels(o):
            if sref not in order: continue
            if level not in order[sref]:
                errs.append(f"{oid}: {where} level '{level}' is not a level of {sref} "
                            f"(its levels: {', '.join(order[sref])}) (SCALE-2: a level is one the scale defines)")
            else:
                seen[where] = (order[sref][level], sref, level)
        for part in ("", ".likelihood", ".impact"):
            a, b = seen.get("rating" + part), seen.get("residual-rating" + part)
            if a and b and a[1] == b[1] and b[0] > a[0]:
                notes.append(f"{oid}: residual{part or ' level'} '{b[2]}' is above '{a[2]}' on {a[1]} "
                             f"(SCALE-3, SHOULD: what remains after treatment is not more than what was there)")
        # SCALE-4: where the scale of a rating carries a matrix and the
        # rating states both inputs, the level is the matrix cell - or the
        # rating says why it is not
        for field in ("rating", "residual-rating"):
            r = o.get(field)
            if not isinstance(r, dict): continue
            mx = (scales.get(r.get("scale-ref")) or {}).get("matrix")
            lk, im = r.get("likelihood"), r.get("impact")
            if not mx or not (isinstance(lk, dict) and isinstance(im, dict)): continue
            if lk.get("scale-ref") != mx["likelihood-scale"] or im.get("scale-ref") != mx["impact-scale"]:
                errs.append(f"{oid}: {field} is on {r.get('scale-ref')}, whose matrix combines {mx['likelihood-scale']} "
                            f"and {mx['impact-scale']}, but states its likelihood and impact on other scales "
                            f"(SCALE-4: a level and its inputs belong to one method)")
                continue
            want = (mx["cells"].get(lk.get("level")) or {}).get(im.get("level"))
            if want is None or r.get("level") == want: continue      # an undefined input level is SCALE-2's failure
            said = (f"{oid}: {field} states '{r.get('level')}'; the matrix of {r.get('scale-ref')} yields '{want}' "
                    f"for likelihood '{lk.get('level')}' and impact '{im.get('level')}'")
            if r.get("override-rationale"):
                notes.append(f"{said} - overridden with a rationale (SCALE-4)")
            else:
                errs.append(f"{said} (SCALE-4: a level follows from its matrix, or the rating carries an "
                            f"override-rationale)")
    return errs, notes

def load_scale_pins(bdir, manifest, section):
    """-> {scale id: definition} for the manifest's `scales` pins; failures
    (missing file, digest, SCALE-1) are reported on `section`."""
    scales = {}
    for pin in manifest.get("scales", []) or []:
        fp = os.path.join(bdir, pin["path"])
        if not os.path.exists(fp):
            fail(section, f"{pin['path']}: pinned scale definition listed but missing"); continue
        raw = open(fp, "rb").read()
        if pkg_digest(raw) != pin["digest"]:
            fail(section, f"{pin['path']}: pinned scale definition digest mismatch{eol_hint(raw, pin['digest'])}")
        try: sd = json.loads(raw.decode("utf-8"))
        except Exception as e:
            fail(section, f"{pin['path']}: pinned scale definition unreadable: {e}"); continue
        number_failures(section, pin["path"], raw, sd)
        errs = scale_definition_errors(sd, pin)
        for e in errs: fail(section, e)
        if not errs: scales[sd["id"]] = sd
    for e in matrix_errors(scales): fail(section, e)
    return scales

def run_scale():
    v = json.load(open(os.path.join(CONF, "scale-vectors.json"), encoding="utf-8"))
    for case in v["vectors"]:
        errs, scales = [], {}
        for sd in case["scales"]:
            e = scale_definition_errors(sd)
            errs += e
            if not e: scales[sd["id"]] = copy.deepcopy(sd)
        errs += matrix_errors(scales)
        objs = {}
        for o in case["objects"]:
            t = inferType_single(o)
            if t: objs[o["id"]] = (t, o)
        e2, notes = scale_errors(scales, objs)
        errs += e2
        okc = len(errs) == case.get("expected-fails", 0) and len(objs) == len(case["objects"])
        for frag in case.get("expected-frags", []):
            if not any(frag in e for e in errs): okc = False
        for frag in case.get("expected-notes", []):
            if not any(frag in n for n in notes): okc = False
        if case.get("expected-notes") == [] and notes: okc = False
        if okc: ok("scale")
        else: fail("scale", f"{case['name']}: expected {case.get('expected-fails', 0)} {case.get('expected-frags')} "
                            f"notes {case.get('expected-notes')}, got {errs} notes {notes}")

# ---------------- RISK-1..6: the schema enforces, this names (CP-RISK-1) ----------------
# The six shape rules are JSON-Schema conditionals, so ANY schema validator
# refuses the object. A schema verdict is a bare "no" (or one library's
# wording of it); Chapter 15.4 wants the machine id and the rationale to
# print on failure, and a second implementation needs something it can be
# held to that is not jsonschema's message text. This table is that: rule
# id -> (what it refuses, why). risk-vectors.json pins both layers per case
# - the schema says invalid AND this function names the expected rule.
RISK_RULES = {
    "RISK-1": "a risk without an owner is a worry, not a managed risk (ISO/IEC 27001 6.1.2 c 2)",
    "RISK-2": "an assessed risk has a level on a named scale (ISO/IEC 27001 6.1.2 d-e; BSI 200-3 Risikoeinstufung; SP 800-30)",
    "RISK-3": "a treated risk names its option and carries its owner's signature (ISO/IEC 27001 6.1.3 a, f)",
    "RISK-4": "a modification with no controls is nothing (ISO/IEC 27001 6.1.3 b)",
    "RISK-5": "sharing names who carries it (ISO/IEC 27005 8.6; BSI 200-3 Transfer)",
    "RISK-6": "retention IS acceptance - no silent retention (ISO/IEC 27001 6.1.3 f)",
    "RISK-13": "a residual level is what remains of a level - it presupposes a rating, on the same scale (D23: levels never compare across scales)",
}
# ---------------- DATE-1..5: fields 1.0.0 left as free text ----------------
# 2.0.0 types them (author decision 2026-11-12, backlog #47a and #52). The
# schema enforces; this names the rule when an object matches no type, so
# that a 1.0.0 bundle with a free-text date is told what to correct.
DATE_RULES = {
    "DATE-1": "a Deviation's `opened` and `decided` are dates, YYYY-MM-DD - a date that any string satisfies cannot be compared, sorted or checked",
    "DATE-2": "the `due` of a Finding's action is a typed point in time or duration (date, datetime, elapsed-duration, calendar-period) - a deadline a machine cannot read is prose",
    # CP-AUTHOR-1: the "when" of who-and-when
    "DATE-3": "the `date` of a Mapping's provenance is a date, YYYY-MM-DD",
    "DATE-4": "the `time` of an Assessment is a date or an RFC 3339 date-time with an offset",
    "DATE-5": "the `timestamp` of an Attestation is a date or an RFC 3339 date-time with an offset",
}
def is_when(v):
    """a date, or an RFC 3339 date-time with an offset"""
    return VALIDATORS["date"].is_valid(v) or VALIDATORS["dateTime"].is_valid(v)
def date_rule_violations(o):
    """-> [(rule id, what is wrong)] for an object that carries Deviations or
    actions. Never used to ACCEPT an object (the schema decides), only to
    explain a refusal."""
    out = []
    if not isinstance(o, dict): return out
    def deviations(x, at):
        if isinstance(x, dict):
            for i, dv in enumerate(x.get("deviations") or [] if isinstance(x.get("deviations"), list) else []):
                for field in ("opened", "decided"):
                    if isinstance(dv, dict) and field in dv and not VALIDATORS["date"].is_valid(dv[field]):
                        out.append(("DATE-1", f"{at}deviations[{i}].{field} is {dv[field]!r}"))
            for k, v in x.items():
                if k != "deviations": deviations(v, f"{at}{k}.")
        elif isinstance(x, list):
            for i, v in enumerate(x): deviations(v, f"{at[:-1]}[{i}]." if at else f"[{i}].")
    deviations(o, "")
    for i, a in enumerate(o.get("actions") or [] if isinstance(o.get("actions"), list) else []):
        if isinstance(a, dict) and "due" in a and not VALIDATORS["due"].is_valid(a["due"]):
            out.append(("DATE-2", f"actions[{i}].due is {json.dumps(a['due'], ensure_ascii=False)}"))
    # the three fields are told apart by the signature of their type
    prov = o.get("provenance")
    if "relationship" in o and isinstance(prov, dict) and "date" in prov and not VALIDATORS["date"].is_valid(prov["date"]):
        out.append(("DATE-3", f"provenance.date is {prov['date']!r}"))
    if "performer-ref" in o and "time" in o and not is_when(o["time"]):
        out.append(("DATE-4", f"time is {o['time']!r}"))
    if "signer" in o and "timestamp" in o and not is_when(o["timestamp"]):
        out.append(("DATE-5", f"timestamp is {o['timestamp']!r}"))
    return out

def risk_rule_violations(o):
    """-> [(rule id, what is wrong)] for an object carrying the Risk
    signature. Mirrors the schema conditionals one-to-one; never used to
    ACCEPT an object (the schema decides), only to explain a refusal."""
    out = []
    if not isinstance(o, dict): return out
    miss = [k for k in ("scenario", "owner-ref", "state") if k not in o]
    if miss: out.append(("RISK-1", f"missing {', '.join(miss)}"))
    st, tr = o.get("state"), o.get("treatment")
    if st in ("assessed", "treated") and "rating" not in o:
        out.append(("RISK-2", f"state={st} without rating"))
    if st == "treated":
        miss = [k for k in ("treatment", "acceptance") if k not in o]
        if miss: out.append(("RISK-3", f"treated without {' and '.join(miss)}"))
    if tr == "modify" and "treatments" not in o: out.append(("RISK-4", "modify names no controls"))
    if tr == "share" and "shared-with-ref" not in o: out.append(("RISK-5", "share without shared-with-ref"))
    if tr == "retain" and "acceptance" not in o: out.append(("RISK-6", "retain without acceptance"))
    if "residual-rating" in o and "rating" not in o: out.append(("RISK-13", "residual-rating without rating"))
    return out

# ---------------- B.1.9 risk-coverage (CP-RISK-1) ----------------
def risk_is_live(r):
    """A Risk justifies a control only while it is being managed. `retired`
    is terminal (C.3c) and lifecycle `withdrawn` unpublishes the object;
    either way the justification has lapsed. Without this, coverage only
    ever grows: a control justified once would stay justified for ever."""
    return r.get("state") != "retired" and r.get("lifecycle") != "withdrawn"

NO_TAILORING = "*"      # report key of the implicit selection: every Requirement of the bundle

def risk_justifies(r):
    """A Risk justifies a requirement once a treatment DECISION rests on an
    ASSESSED risk: live, published (not `draft`), `state` assessed or
    treated (so it has a level - RISK-2), and a `treatment` option chosen.
    ISO/IEC 27001 6.1.3 a-b: controls are determined to implement the
    treatment option chosen for an analysed risk. Without this a three-field
    stub (scenario, owner, treatments) would satisfy --require-risk-basis
    while RISK-2/3/6 stay strict on fields coverage never reads."""
    return (risk_is_live(r) and r.get("lifecycle") != "draft"
            and r.get("state") in ("assessed", "treated") and "treatment" in r)

def _expand_refs(refs, objs):
    """ids -> Requirement ids, through nested Sets to any depth (D21: a DAG;
    the seen-set makes a malformed cycle terminate, closure_errors reports
    it). A ref that is neither is closure_errors' failure, not ours."""
    out, seen, stack = set(), set(), list(refs)
    while stack:
        sid = stack.pop()
        if sid in seen: continue
        seen.add(sid)
        tgt = objs.get(sid)
        if not tgt: continue
        if tgt[0] == "requirementSet":
            stack.extend(m["ref"] for m in tgt[1].get("members", []))
        elif tgt[0] == "requirement":
            out.add(sid)
    return out

def _selected_requirements(tobj, objs, notes):
    """Resolve a Tailoring's selection -> (requirement ids, open?).
    set-refs name Sets (typed in closure_errors) and are expanded to any
    depth; an exclude names a Requirement or a Set, and a Set excludes its
    members. A `withdrawn` Requirement is not in force: it is dropped from
    the selection and said so. A predicate select is resolved by the
    tailoring engine, not here, so its presence makes the selection OPEN:
    the returned ids are a lower bound and nothing may be concluded from a
    requirement's absence."""
    sel = _expand_refs([s["set-ref"] for s in tobj.get("selects", [])
                        if "set-ref" in s and (objs.get(s["set-ref"]) or ("",))[0] == "requirementSet"], objs)
    open_sel = any("set-ref" not in s for s in tobj.get("selects", []))
    if open_sel:
        notes.append(f"{tobj['id']}: predicate select not expanded by risk-coverage (engine-resolved) - "
                     f"the selection is a lower bound")
    sel -= _expand_refs([e["ref"] for e in tobj.get("excludes", []) or []], objs)
    gone = sorted(q for q in sel if objs[q][1].get("lifecycle") == "withdrawn")
    if gone:
        notes.append(f"{tobj['id']}: {len(gone)} selected requirement(s) are withdrawn and not counted "
                     f"(first: {gone[0]})")
        sel -= set(gone)
    return sel, open_sel

def risk_coverage(objs, sdig_fn=None, envelopes=None, trusted=None):
    """B.1.9: for each Tailoring in force, which selected requirements are
    justified by a Risk (covered), which are not (uncovered) and why not
    (`pending`: named only by Risks without an assessed treatment decision;
    `lapsed`: named only by retired / withdrawn Risks), which excludes lack
    a rationale, and which treatments point at requirements the Tailoring(s)
    they belong to do not select (treatment-out-of-scope, RISK-11).
    A bundle with NO Tailoring has every Requirement in play (reported
    under NO_TAILORING). A Risk's `tailoring-refs` scope it: it justifies, and is held to
    RISK-11, only there; without them it applies to every Tailoring of the
    bundle. Returns (report, errors, notes). Uncovered is a REPORT line:
    whether a control needs a risk basis is the program's policy."""
    notes, errs = [], []
    risks = {oid: o for oid, (t, o) in objs.items() if t == "risk"}
    tailorings = {oid: o for oid, (t, o) in objs.items() if t == "tailoring"}
    in_force = sorted(tid for tid, o in tailorings.items() if o.get("lifecycle") != "withdrawn")
    for tid in sorted(set(tailorings) - set(in_force)):
        notes.append(f"{tid}: withdrawn - selects nothing and is not reported (a withdrawn Statement of "
                     f"Applicability is history)")
    def applies(r, tid):
        scope = r.get("tailoring-refs")
        return not scope or tid in scope
    report = {"tailorings": {}, "risks": len(risks), "treatment-out-of-scope": []}
    selections = {}
    # No Tailoring at all: nothing was scoped out, so every Requirement of
    # the bundle is in play - the catalogue applies as published. The
    # implicit selection is reported under NO_TAILORING. (A bundle whose
    # Tailorings are all WITHDRAWN is a different statement: there was a
    # Statement of Applicability, and it is no longer in force.)
    if not tailorings:
        in_force = [NO_TAILORING]
    for tid in in_force:
        if tid == NO_TAILORING:
            tobj, tier, open_sel = {}, "none", False
            sel = {q for q, (t, o) in objs.items() if t == "requirement" and o.get("lifecycle") != "withdrawn"}
        else:
            tobj = tailorings[tid]
            tier = derive_tier(tobj, objs, sdig_fn or sdig, envelopes=envelopes, trusted=trusted)
            sel, open_sel = _selected_requirements(tobj, objs, notes)
        selections[tid] = (sel, open_sel)
        treats, pending, lapsed = (collections.defaultdict(set) for _ in range(3))
        for rid, r in risks.items():
            if not applies(r, tid): continue
            bucket = treats if risk_justifies(r) else pending if risk_is_live(r) else lapsed
            for tr in r.get("treatments", []) or []:
                bucket[tr["requirement-ref"]].add(rid)
        covered = {q: sorted(treats[q]) for q in sorted(sel) if treats.get(q)}
        uncovered = sorted(q for q in sel if not treats.get(q))
        pending_only = {q: sorted(pending[q]) for q in uncovered if pending.get(q)}
        lapsed_only = {q: sorted(lapsed[q]) for q in uncovered if lapsed.get(q) and not pending.get(q)}
        excl_no_rationale = [e["ref"] for e in tobj.get("excludes", []) or [] if not e.get("rationale")]
        report["tailorings"][tid] = {"tier": tier, "selected": len(sel), "open-selection": open_sel,
                                     "covered": covered, "uncovered": uncovered, "pending": pending_only,
                                     "lapsed": lapsed_only, "excludes-without-rationale": excl_no_rationale}
        lab = "(no Tailoring)" if tid == NO_TAILORING else tid
        for q, rids in pending_only.items():
            notes.append(f"{lab}: selected {q} is named only by Risk(s) without an assessed treatment decision "
                         f"{rids} - counted as uncovered (a risk justifies once it is assessed and its option chosen)")
        for q, rids in lapsed_only.items():
            notes.append(f"{lab}: selected {q} is named only by retired/withdrawn Risk(s) {rids} - "
                         f"counted as uncovered (C.3c: a retired risk justifies nothing)")
        if tier == "consumer" and excl_no_rationale:
            # ISO 27001 6.1.3 d: exclusion is justified or it is not a Statement of Applicability
            notes.append(f"{tid}: {len(excl_no_rationale)} exclude(s) without rationale at consumer tier "
                         f"(RISK-10, SHOULD: an SoA exclusion carries its justification)")
    # RISK-14 (SHOULD): with more than one Tailoring in force an unscoped
    # Risk justifies in each - a risk about system A would justify the
    # control in system B's Statement of Applicability
    if len(in_force) > 1:
        for rid in sorted(risks):
            r = risks[rid]
            if risk_is_live(r) and r.get("treatments") and not r.get("tailoring-refs"):
                notes.append(f"{rid}: no tailoring-refs in a bundle with {len(in_force)} Tailorings - its treatment "
                             f"counts in each (RISK-14, SHOULD: a Risk names the Tailoring its treatment belongs to)")
    # RISK-11 binds LIVE risks only (a retired risk whose control later left
    # the SoA is history, not a contradiction), and is asked of the
    # Tailorings the risk belongs to: its tailoring-refs, else all in force.
    # An unresolved or mistyped target is RISK-7/12's failure, not a second
    # one here. Where one of THOSE selections is open the question is
    # undecidable from this side, so it is said and not guessed - an open
    # Tailoring the risk does not belong to decides nothing.
    out_of_scope, undecided = collections.defaultdict(set), collections.defaultdict(set)
    for rid, r in risks.items():
        if not risk_is_live(r): continue
        mine = [tid for tid in in_force if applies(r, tid)]
        for tr in r.get("treatments", []) or []:
            q = tr["requirement-ref"]
            tgt = objs.get(q)
            if not tgt or tgt[0] != "requirement": continue
            if any(q in selections[tid][0] for tid in mine): continue
            if tgt[1].get("lifecycle") != "withdrawn" and any(selections[tid][1] for tid in mine):
                undecided[q].add(rid)
            else:
                out_of_scope[q].add(rid)
    for q, rids in sorted(undecided.items()):
        notes.append(f"{sorted(rids)[0]}: treatment names {q}, which no set-ref select reaches - "
                     f"RISK-11 undecided: a predicate select of its Tailoring(s) may select it")
    for q, rids in sorted(out_of_scope.items()):
        report["treatment-out-of-scope"].append({"requirement": q, "risks": sorted(rids)})
        why = ("which is withdrawn" if objs[q][1].get("lifecycle") == "withdrawn"
               else "which no Tailoring in this bundle selects" if not any(risks[x].get("tailoring-refs") for x in rids)
               else "which the Tailoring(s) it belongs to do not select")
        errs.append(f"{sorted(rids)[0]}: treatment names {q}, {why} "
                    f"(RISK-11: a risk cannot lean on a control the SoA dropped)")
    return report, errs, notes

def risk_basis_fail(tid, q):
    """The normative B.1.9 failure, printed under the policy switch."""
    return (f"FAIL [risk-coverage] {tid}  selected {q}\n"
            f"  justified by no Risk\n"
            f"  rationale: ISO/IEC 27001 6.1.3 d - inclusion in the Statement of "
            f"Applicability carries its justification")

def risk_link_notes(objs):
    """RISK-9 (SHOULD): a `risk-adjustment` Deviation references the Risk it
    adjusts for in `refs`, so the weakening and its justification meet."""
    notes = []
    risk_ids = {oid for oid, (t, o) in objs.items() if t == "risk"}
    if not risk_ids: return notes
    for oid, (t, o) in objs.items():
        devs = list(o.get("deviations", []) or [])
        if t == "tailoring":
            devs += [op["deviation"] for op in o.get("operations", []) or [] if isinstance(op.get("deviation"), dict)]
        for d in devs:
            if d.get("type") == "risk-adjustment" and not (set(d.get("refs", []) or []) & risk_ids):
                notes.append(f"{oid}: risk-adjustment Deviation references no Risk of this bundle "
                             f"(RISK-9, SHOULD: the adjustment names the risk it accepts)")
    return notes

# ---------------- who decided, and when (CP-AUTHOR-1) ----------------
# The schema leaves every one of these fields optional: a catalogue
# authority's content needs none. What is missing is REPORTED, one line per
# object and rule, and fails nothing unless --require-authors asks for it.
AUTHOR_RULES = {
    "AUTHOR-1": "a consumer's Tailoring says who decided each select, exclude and operation - on the entry, or once on the Tailoring",
    "AUTHOR-2": "a Risk, a Finding and an Implementation say who wrote this version and when (provenance): each records a judgement",
    "AUTHOR-3": "an approved or withdrawn Deviation says when it was decided (decided); `opened` is when it was asked for",
    "AUTHOR-4": "an authorization says on which day it was given (date); it already names the authority",
    "REVIEW-1": "a review-due that has passed is reported, on an approved Deviation and on a Risk still managed - the date exists to be looked at",
}

def by_code_unit(ids):
    """ids in the order of their UTF-16 code units - the order RFC 8785 gives
    the members of the canonical form, and the one a JavaScript or a .NET
    tool gets from an ordinal sort. Python's own order is by code point,
    which differs for ids with characters beyond U+FFFF."""
    return sorted(ids, key=lambda s: s.encode("utf-16-be"))

def author_report(objs, sdig_fn=None, envelopes=None, trusted=None):
    """-> [(rule, object id, count, message)], in the order of the ids.
    AUTHOR-1 asks only a Tailoring at consumer tier (D13: duties bind
    there; an authority's Tailoring is attributed by its origin and its
    Attestation). An entry without `provenance` has its Tailoring's."""
    out = []
    for oid in by_code_unit(objs):
        t, o = objs[oid]
        if t == "tailoring":
            tier = derive_tier(o, objs, sdig_fn or sdig, envelopes=envelopes, trusted=trusted)
            if tier == "consumer" and "provenance" not in o:
                parts, n = [], 0
                for key, word in (("selects", "select"), ("excludes", "exclude"), ("operations", "operation")):
                    entries = [e for e in o.get(key, []) or [] if isinstance(e, dict)]
                    bare = sum(1 for e in entries if "provenance" not in e)
                    if bare:
                        n += bare
                        parts.append(f"{bare} of {len(entries)} {word}(s)")
                if n:
                    out.append(("AUTHOR-1", oid, n, f"{oid}: {', '.join(parts)} name no author, and the Tailoring names none (AUTHOR-1)"))
        if t in ("risk", "finding", "implementation") and "provenance" not in o:
            out.append(("AUTHOR-2", oid, 1, f"{oid}: this {t.capitalize()} does not say who wrote it and when (AUTHOR-2)"))
        undated = [w for w, d in deviations_of(t, o) if d.get("state") in ("approved", "withdrawn") and "decided" not in d]
        if undated:
            out.append(("AUTHOR-3", oid, len(undated), f"{oid}: {len(undated)} Deviation(s) approved or withdrawn without `decided`: {', '.join(undated)} (AUTHOR-3)"))
        if t == "component":
            auths = [a for a in o.get("authorizations", []) or [] if isinstance(a, dict)]
            bare = [str(a.get("id")) for a in auths if "date" not in a]
            if bare:
                out.append(("AUTHOR-4", oid, len(bare), f"{oid}: {len(bare)} authorization(s) without a date: {', '.join(bare)} (AUTHOR-4)"))
    return out

_DT = re.compile(r"^([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})(?:\.[0-9]+)?(Z|[+-][0-9]{2}:[0-9]{2})\Z")
_ELAPSED = {"seconds": 1, "minutes": 60, "hours": 3600}

def _utc_day(due, start):
    """-> (the UTC calendar day a `review-due` falls on, None) or (None, why
    it cannot be evaluated). `start` is the date a duration counts from."""
    kind = due.get("type")
    try:
        if kind == "date":
            return datetime.date.fromisoformat(due["value"]), None
        if kind == "datetime":
            y, mo, d, h, mi, sec, off = _DT.match(due["value"]).groups()
            minutes = 0 if off == "Z" else (1 if off[0] == "+" else -1) * (int(off[1:3]) * 60 + int(off[4:6]))
            at = datetime.datetime(int(y), int(mo), int(d), int(h), int(mi), int(sec),
                                   tzinfo=datetime.timezone(datetime.timedelta(minutes=minutes)))
            return at.astimezone(datetime.timezone.utc).date(), None
        if kind == "elapsed-duration":
            if start is None: return None, "a duration, and no date to count it from"
            at = datetime.datetime.combine(datetime.date.fromisoformat(start), datetime.time(0), tzinfo=datetime.timezone.utc)
            return (at + datetime.timedelta(seconds=due["num"] * _ELAPSED[due["unit"]])).date(), None
        if kind == "calendar-period":
            return None, f"a calendar period, and this tool has no calendar {due.get('calendar-ref')} (D9: fail-closed without the named calendar)"
    except (ValueError, OverflowError):
        return None, "not a day of the calendar"
    return None, "not a typed review-due"

def review_report(objs, as_of):
    """REVIEW-1 -> {"dated": n, "overdue": [(object id, where, day)],
    "not-evaluable": [(object id, where, why)]}. A point in time has passed
    when its UTC calendar day is before `as_of`; due today is not overdue.
    A duration counts from `decided`, else `opened`, on a Deviation, and
    from `acceptance.date` on a Risk. Asked of an approved Deviation and of
    a Risk still managed; nothing fails by it."""
    dated, overdue, blind = 0, [], []
    for oid in by_code_unit(objs):
        t, o = objs[oid]
        asked = [(w, d["review-due"], d.get("decided") or d.get("opened")) for w, d in deviations_of(t, o)
                 if d.get("state") == "approved" and isinstance(d.get("review-due"), dict)]
        if t == "risk" and risk_is_live(o) and isinstance(o.get("review-due"), dict):
            asked.append(("review-due", o["review-due"], (o.get("acceptance") or {}).get("date")))
        for where, due, start in asked:
            dated += 1
            day, why = _utc_day(due, start)
            if day is None: blind.append((oid, where, why))
            elif day < as_of: overdue.append((oid, where, day.isoformat()))
    return {"dated": dated, "overdue": overdue, "not-evaluable": blind}

def report_authors_and_reviews(section, objs, envelopes=None):
    """Prints the two reports for one bundle. AUTHOR lines are notes, or
    failures under --require-authors; REVIEW lines are always notes."""
    for rule, _, _, msg in author_report(objs, envelopes=envelopes, trusted=TRUSTED):
        if REQUIRE_AUTHORS: fail(section, msg)
        else: print(f"    note: {msg}")
    r = review_report(objs, AS_OF)
    if r["dated"]:
        print(f"    review: {r['dated']} review date(s) asked as of {AS_OF.isoformat()}: "
              f"{len(r['overdue'])} overdue, {len(r['not-evaluable'])} not evaluable (REVIEW-1)")
    for oid, where, day in r["overdue"]:
        print(f"    note: {oid}: {where} was due on {day} (REVIEW-1: overdue; it still holds until someone acts)")
    for oid, where, why in r["not-evaluable"]:
        print(f"    note: {oid}: {where} is not evaluated: {why} (REVIEW-1)")

def run_author():
    v = json.load(open(os.path.join(CONF, "author-vectors.json"), encoding="utf-8"))
    def typed(case):
        objs = {}
        for o in case["objects"]:
            t = inferType_single(o)
            if t: objs[o["id"]] = (t, o)
        return objs if len(objs) == len(case["objects"]) else None
    for case in v["author-vectors"]:
        objs = typed(case)
        got = None if objs is None else [[rule, oid, n] for rule, oid, n, _ in author_report(objs)]
        if got == case["expected"]: ok("author")
        else: fail("author", f"{case['name']}: expected {case['expected']}, got {got}")
    for case in v["review-vectors"]:
        objs = typed(case)
        r = None if objs is None else review_report(objs, datetime.date.fromisoformat(case["as-of"]))
        got = None if r is None else ([[o, w] for o, w, _ in r["overdue"]], [[o, w] for o, w, _ in r["not-evaluable"]])
        if got == (case.get("expected-overdue", []), case.get("expected-not-evaluable", [])): ok("author")
        else: fail("author", f"{case['name']}: expected overdue {case.get('expected-overdue', [])} / not evaluable {case.get('expected-not-evaluable', [])}, got {got}")

def run_risk():
    v = json.load(open(os.path.join(CONF, "risk-vectors.json"), encoding="utf-8"))
    for case in v.get("risk-transitions", []):          # C.3c state machine
        got = case["to"] in RISK_NEXT[case["from"]]
        if got == case["valid"]: ok("risk")
        else: fail("risk", f"risk {case['from']}->{case['to']}: expected valid={case['valid']}")
    for case in v["object-vectors"]:
        o = case["object"]
        m = [t for t in TYPES if VALIDATORS[t].is_valid(o)]
        viol = [rid for rid, _ in risk_rule_violations(o)]
        if case["expected"] == "valid":
            okc = m == ["risk"] and not viol          # the two layers agree on "valid"
        else:
            okc = m == []
            # expected-rule is the portable assertion (every implementation
            # names the rule); expected-frag is advisory - it checks that THIS
            # schema library's diagnostic mentions the offending field
            if okc and case.get("expected-rule"):
                okc = case["expected-rule"] in viol
            if okc and case.get("expected-frag"):
                okc = any(case["expected-frag"] in (e.message + "/" + "/".join(map(str, e.absolute_path)))
                          for e in VALIDATORS["risk"].iter_errors(o))
        if okc: ok("risk")
        else: fail("risk", f"{case['name']}: expected {case['expected']} {case.get('expected-rule', '')} "
                           f"{case.get('expected-frag', '')}, matched {m}, rules named {viol}")
    for case in v["bundle-vectors"]:
        objs = {}
        for o in case["objects"]:
            t = inferType_single(o)
            if t: objs[o["id"]] = (t, o)
        errs = closure_errors(objs)
        rep_, cerrs, notes = risk_coverage(objs)
        errs += cerrs
        notes += risk_link_notes(objs)
        okc = len(errs) == case.get("expected-fails", 0)
        for frag in case.get("expected-frags", []):
            if not any(frag in e for e in errs): okc = False
        for frag in case.get("expected-notes", []):
            if not any(frag in n for n in notes): okc = False
        exp = case.get("expected-coverage")
        if exp:
            for tid, want in exp.items():
                got = rep_["tailorings"].get(tid, {})
                if sorted(got.get("uncovered", [])) != sorted(want.get("uncovered", [])): okc = False
                if sorted(got.get("covered", {}).keys()) != sorted(want.get("covered", [])): okc = False
                if "lapsed" in want and sorted(got.get("lapsed", {}).keys()) != sorted(want["lapsed"]): okc = False
                if "pending" in want and sorted(got.get("pending", {}).keys()) != sorted(want["pending"]): okc = False
        if okc: ok("risk")
        else: fail("risk", f"{case['name']}: expected {case.get('expected-fails',0)} fails {case.get('expected-frags')} "
                           f"notes {case.get('expected-notes')} cov {exp}; got errs {[e[:80] for e in errs]} "
                           f"notes {[n[:80] for n in notes]} cov {rep_['tailorings']}")

# ---------------- CHECK (CP-CHECK-1, kernel 2.0.0) ----------------
# A Check states what to observe on a platform (`observes`, a typed fact
# contract) and what the observation must satisfy (`criteria`, a flat
# conjunction over a CLOSED set of twelve comparators - primitive
# check-verdict, App. B.1.10). The code that collects the facts rides the
# Check in the stdlib facet collector@1 and decides nothing: every verdict
# an Assessment records is recomputed here from the observation it records.
# Three-valued throughout (strong Kleene AND): one not-satisfied decides,
# else one inconclusive decides, else satisfied. An unbound parameter is
# inconclusive - a default is never substituted (D9).
SAT, NOT, INC, NA = "satisfied", "not-satisfied", "inconclusive", "not-applicable"
COLLECTOR_FACET = "https://ns.jascon.net/stdlib/facet/collector"
CHECK_RULES = {
    "CHECK-1": "a check discharges a requirement; when that requirement is in the bundle the edge is typed and the clauses it names exist",
    "CHECK-2": "every assertion reads a fact the check declares, and a fact is declared once - the fact contract is all a collector promises",
    "CHECK-3": "an operator compares what it can compare - ordering on numbers, patterns on text, set operators on lists - and a literal has the fact's type",
    "CHECK-4": "a bound value comes from a parameter the requirement declares exactly once on the covered clauses, with a fitting type - so tailoring the requirement retunes the check; a pattern is never a parameter",
    "CHECK-5": "tightening a parameter must never loosen the check: at-most needs a parameter that tightens lower, at-least one that tightens higher",
    "CHECK-6": "a pattern is an I-Regexp (RFC 9485) within the kernel's size limits, so two conformant tools return one verdict, in bounded time",
    "CHECK-7": "collectors are well-formed and each is named once, so a result row can say which code observed",
    "CHECK-8": "a result names the check it ran and that check's semantic digest - a changed check is a different check",
    "CHECK-9": "a recorded outcome is the one check-verdict computes from the recorded observation - verdicts are recomputed, never taken on trust",
    "CHECK-10": "an assessment that carries check results has one row per check, and its result is their aggregate: any not-satisfied, else any inconclusive or none applicable, else satisfied",
    "CHECK-11": "no observation, no verdict: a row without one is inconclusive and says why",
    "CHECK-12": "a row names only parameters its check reads, and their values are the ones the Tailoring it names binds - an implementer does not set its own pass mark",
    "CHECK-13": "a result's collector-id names a collector the check declares",
    "CHECK-14": "a Finding raised by a check is about the requirement - and the clause - that check discharges",
    "CHECK-15": "evidence is content-addressed and stays inside the bundle's store, evidence/sha256/: every digest in the chain verifies against the bytes, and a record describes the run it is attached to - its check, its collector and its observation",
}

# -- I-Regexp (RFC 9485) for matches / matches-not --
# The dialect is the ABNF of RFC 9485 (iregexp.abnf of the IETF JSONPath WG):
# XSD regexps without character-class subtraction, without multi-character
# escapes (\d \w \s ...) and without Unicode blocks. Matching is always the
# WHOLE value (XSD semantics), case-sensitive, by code point; `^` and `$`
# are ordinary characters; `.` is any character but \n and \r. The engine
# does not hand the pattern to a host regex library - Python re, .NET and
# ECMAScript disagree on exactly those constructs - it parses the ABNF and
# runs a Thompson state-set simulation: linear in program x input, no
# backtracking, so no pattern can stall a validator.
IRE_MAX_PATTERN = 256      # characters
IRE_MAX_STATES = 1000      # compiled program, after {m,n} expansion
IRE_MAX_INPUT = 4096       # characters per matched value; longer -> inconclusive
_IRE_CATS = {"L", "Lu", "Ll", "Lm", "Lo", "Lt", "M", "Mc", "Me", "Mn", "N", "Nd", "Nl", "No",
             "P", "Pc", "Pd", "Pe", "Pf", "Pi", "Po", "Ps", "Z", "Zl", "Zp", "Zs",
             "S", "Sc", "Sk", "Sm", "So", "C", "Cc", "Cf", "Cn", "Co"}
_IRE_CAT_CACHE = {}

class IRegexpError(ValueError):
    pass

def _ire_norm(rs):
    out = []
    for lo, hi in sorted(rs):
        if out and lo <= out[-1][1] + 1: out[-1] = (out[-1][0], max(out[-1][1], hi))
        else: out.append((lo, hi))
    return out

def _ire_compl(rs):
    out, nxt = [], 0
    for lo, hi in _ire_norm(rs):
        if lo > nxt: out.append((nxt, lo - 1))
        nxt = hi + 1
    if nxt <= 0x10FFFF: out.append((nxt, 0x10FFFF))
    return out

_IRE_DOT = _ire_compl([(10, 10), (13, 13)])

def _ire_cat(prop):
    """Code-point ranges of a Unicode general category (host Unicode database)."""
    if prop not in _IRE_CAT_CACHE:
        import unicodedata
        out, start = [], None
        for cp in range(0x110000):
            hit = unicodedata.category(chr(cp)).startswith(prop)
            if hit and start is None: start = cp
            elif not hit and start is not None: out.append((start, cp - 1)); start = None
        if start is not None: out.append((start, 0x10FFFF))
        _IRE_CAT_CACHE[prop] = out
    return _IRE_CAT_CACHE[prop]

def _ire_surrogate(c):
    return c is not None and 0xD800 <= ord(c) <= 0xDFFF
IRE_SURROGATE = "a surrogate code point (U+D800 to U+DFFF) is not a character of I-Regexp (RFC 9485, NormalChar and CCchar)"

def _ire_normal(c):
    o = ord(c)     # NormalChar of the ABNF as PUBLISHED in RFC 9485: it skips the
                   # surrogate code points, which the working group's file did not (backlog #61)
    return (o <= 0x27 or c in ",-" or 0x2F <= o <= 0x3E or 0x40 <= o <= 0x5A
            or 0x5E <= o <= 0x7A or (o >= 0x7E and not 0xD800 <= o <= 0xDFFF))

def ire_parse(p):
    """-> AST of an I-Regexp; raises IRegexpError naming the construct and position."""
    if not isinstance(p, str): raise IRegexpError("a pattern is a string")
    if len(p) > IRE_MAX_PATTERN:
        raise IRegexpError(f"pattern is {len(p)} characters long; the limit is {IRE_MAX_PATTERN}")
    pos = 0
    def peek(k=0): return p[pos + k] if pos + k < len(p) else None
    def err(what): raise IRegexpError(f"{what} at position {pos} of {p!r}")
    def regexp():
        nonlocal pos
        br = [branch()]
        while peek() == "|":
            pos += 1; br.append(branch())
        return ("alt", br)
    def branch():
        items = []
        while peek() is not None and peek() not in "|)":
            items.append(piece())
        return ("cat", items)
    def piece():
        nonlocal pos
        a = atom()
        c = peek()
        if c == "*": pos += 1; return ("rep", a, 0, None)
        if c == "+": pos += 1; return ("rep", a, 1, None)
        if c == "?": pos += 1; return ("rep", a, 0, 1)
        if c == "{":
            m = re.match(r"\{([0-9]+)(,([0-9]*))?\}", p[pos:])
            if not m: err("malformed range quantifier (I-Regexp has {n}, {n,} and {n,m})")
            lo = int(m.group(1))
            hi = lo if m.group(2) is None else (int(m.group(3)) if m.group(3) else None)
            if hi is not None and hi < lo: err(f"range quantifier {m.group(0)} has its bounds reversed")
            if lo > IRE_MAX_STATES or (hi or 0) > IRE_MAX_STATES: err("range quantifier exceeds the size limit")
            pos += m.end(); return ("rep", a, lo, hi)
        return a
    def escape():
        nonlocal pos
        n = peek(1)
        if n in ("p", "P") and peek(2) == "{":
            end = p.find("}", pos + 3)
            prop = p[pos + 3:end] if end > 0 else None
            if prop not in _IRE_CATS:
                err(f"\\{n}{{{prop}}} is not a Unicode general category (I-Regexp has categories, not blocks)")
            pos = end + 1
            rs = _ire_cat(prop)
            return _ire_compl(rs) if n == "P" else rs
        if n is not None and n in "()*+-.?[\\]^{|}":
            pos += 2; return [(ord(n), ord(n))]
        if n in ("n", "r", "t"):
            pos += 2; o = {"n": 10, "r": 13, "t": 9}[n]; return [(o, o)]
        err(f"escape \\{n or ''} is not I-Regexp (no \\d \\w \\s \\b, no back-references)")
    def cc_char():
        nonlocal pos
        c = peek()
        if c == "\\":
            if peek(1) in ("p", "P"): err("a category escape cannot bound a range")
            return escape()[0][0]
        if c is None or c in "-[]": err(f"{c!r} must be escaped inside a character class")
        if _ire_surrogate(c): err(IRE_SURROGATE)
        pos += 1; return ord(c)
    def char_class():
        nonlocal pos
        pos += 1
        neg = peek() == "^"
        if neg: pos += 1
        items, first = [], True
        while True:
            c = peek()
            if c is None: err("unclosed character class")
            if c == "]":
                if first: err("empty character class")
                pos += 1; break
            if c == "-":
                if first or peek(1) == "]":
                    items.append((45, 45)); pos += 1; first = False; continue
                err("'-' inside a character class only first or last (no class subtraction)")
            if c == "\\" and peek(1) in ("p", "P"):
                items += escape(); first = False; continue
            lo = cc_char()
            if peek() == "-" and peek(1) not in ("]", None):
                pos += 1
                hi = cc_char()
                if hi < lo: err("character range out of order")
                items.append((lo, hi))
            else:
                items.append((lo, lo))
            first = False
        rs = _ire_norm(items)
        return _ire_compl(rs) if neg else rs
    def atom():
        nonlocal pos
        c = peek()
        if c == "(":
            pos += 1
            r = regexp()
            if peek() != ")": err("unclosed group")
            pos += 1; return r
        if c == ".": pos += 1; return ("set", _IRE_DOT)
        if c == "\\": return ("set", escape())
        if c == "[": return ("set", char_class())
        if c is not None and _ire_normal(c): pos += 1; return ("set", [(ord(c), ord(c))])
        if _ire_surrogate(c): err(IRE_SURROGATE)
        err(f"{c!r} cannot start an atom here" if c else "the pattern ends where an atom is expected")
    ast = regexp()
    if pos != len(p): err(f"unbalanced {p[pos]!r}")
    return ast

_IRE_PROGS = {}
def ire_compile(p):
    """-> (states, start). A state is ["c", ranges, next] | ["s", a, b] | ["m"]."""
    if p in _IRE_PROGS: return _IRE_PROGS[p]
    ast = ire_parse(p)
    st = []
    def new(s):
        st.append(s)
        if len(st) > IRE_MAX_STATES:
            raise IRegexpError(f"pattern {p!r} compiles to more than {IRE_MAX_STATES} states")
        return len(st) - 1
    def comp(n, nxt):
        if n[0] == "set": return new(["c", n[1], nxt])
        if n[0] == "cat":
            for it in reversed(n[1]): nxt = comp(it, nxt)
            return nxt
        if n[0] == "alt":
            starts = [comp(b, nxt) for b in n[1]]
            s = starts[-1]
            for b in reversed(starts[:-1]): s = new(["s", b, s])
            return s
        _, a, lo, hi = n
        t = nxt
        if hi is None:
            loop = new(["s", None, nxt]); st[loop][1] = comp(a, loop); t = loop
        else:
            for _ in range(hi - lo): t = new(["s", comp(a, t), nxt])
        for _ in range(lo): t = comp(a, t)
        return t
    end = new(["m"])
    _IRE_PROGS[p] = (st, comp(ast, end))
    return _IRE_PROGS[p]

def _ire_in(rs, o):
    import bisect
    i = bisect.bisect_right(rs, (o, 0x110000)) - 1
    return i >= 0 and rs[i][0] <= o <= rs[i][1]

def _ire_closure(st, seeds):
    seen, out, stack = set(), [], list(seeds)
    while stack:
        s = stack.pop()
        if s in seen: continue
        seen.add(s)
        if st[s][0] == "s": stack.append(st[s][2]); stack.append(st[s][1])
        else: out.append(s)
    return out

def ire_fullmatch(p, text):
    st, start = ire_compile(p)
    cur = _ire_closure(st, [start])
    for ch in text:
        o = ord(ch)
        nxt = [st[s][2] for s in cur if st[s][0] == "c" and _ire_in(st[s][1], o)]
        if not nxt: return False
        cur = _ire_closure(st, nxt)
    return any(st[s][0] == "m" for s in cur)

# -- check-verdict (B.1.10) --
CHECK_OPS = {   # which comparators fit which fact (present / absent fit every fact)
    "one": {"string": {"equals", "not-equals", "one-of", "matches", "matches-not"},
            "code": {"equals", "not-equals", "one-of", "matches", "matches-not"},
            "integer": {"equals", "not-equals", "one-of", "at-least", "at-most"},
            "decimal": {"equals", "not-equals", "one-of", "at-least", "at-most"},
            "boolean": {"equals", "not-equals"}},
    "many": {"string": {"includes-all", "excludes-all", "subset-of", "matches", "matches-not"},
             "code": {"includes-all", "excludes-all", "subset-of", "matches", "matches-not"},
             "integer": {"includes-all", "excludes-all", "subset-of"},
             "decimal": {"includes-all", "excludes-all", "subset-of"},
             "boolean": set()},
}
CHECK_LIST_OPS = {"one-of", "includes-all", "excludes-all", "subset-of"}
CHECK_PATTERN_OPS = {"matches", "matches-not"}

def _fact_ok(ftype, x):
    if ftype == "integer": return in_number_domain(x)     # NUMBER-1: no verdict from a value two tools read differently
    if ftype == "decimal": return isinstance(x, str) and re.match(DECIMAL_RE, x) is not None
    if ftype == "boolean": return isinstance(x, bool)
    return isinstance(x, str)          # string, code

def _fact_value_ok(decl, v):
    if decl.get("cardinality") == "many":
        return isinstance(v, list) and all(_fact_ok(decl["type"], x) for x in v)
    return _fact_ok(decl["type"], v)

def _expected_ok(op, ftype, e):
    if op in CHECK_LIST_OPS:
        return isinstance(e, list) and all(_fact_ok(ftype, x) for x in e) and (op == "subset-of" or len(e) > 0)
    if op in CHECK_PATTERN_OPS: return isinstance(e, str)
    return _fact_ok(ftype, e)

def _check_assert(a, facts, decls, params):
    """-> (outcome, reason) of one assertion over one set of facts."""
    f, op = a["fact"], a["op"]
    d = decls.get(f)
    if d is None: return INC, f"fact '{f}' is not declared in observes"
    if op == "present": return (SAT, f"{f} is present") if f in facts else (NOT, f"{f} is not present")
    if op == "absent": return (SAT, f"{f} is absent") if f not in facts else (NOT, f"{f} is present")
    t, many = d["type"], d.get("cardinality") == "many"
    if op not in CHECK_OPS["many" if many else "one"][t]:
        return INC, f"{op} does not fit a {t}{' list' if many else ''} fact"
    if f not in facts: return INC, f"fact '{f}' was not observed"
    v = facts[f]
    if not _fact_value_ok(d, v): return INC, f"fact '{f}' is not a {t}{' list' if many else ''}: {v!r}"
    e, src = a.get("expected"), "the literal"
    if isinstance(e, dict):
        pn = e.get("param")
        if pn not in params: return INC, f"parameter '{pn}' is unbound - a default is never substituted (D9)"
        e, src = params[pn], f"parameter '{pn}'"
    if not _expected_ok(op, t, e): return INC, f"{src} {e!r} does not fit {op} on a {t} fact"
    N = (lambda x: Decimal(x)) if t == "decimal" else (lambda x: x)
    if op == "equals": hit = N(v) == N(e)
    elif op == "not-equals": hit = N(v) != N(e)
    elif op == "one-of": hit = N(v) in [N(x) for x in e]
    elif op == "at-least": hit = N(v) >= N(e)
    elif op == "at-most": hit = N(v) <= N(e)
    elif op == "includes-all": hit = all(N(x) in {N(y) for y in v} for x in e)
    elif op == "excludes-all": hit = not any(N(x) in {N(y) for y in v} for x in e)
    elif op == "subset-of": hit = all(N(x) in {N(y) for y in e} for x in v)
    else:                               # matches / matches-not: whole value, every element of a list
        vals = v if many else [v]
        if any(len(x) > IRE_MAX_INPUT for x in vals):
            return INC, f"a value of '{f}' is longer than {IRE_MAX_INPUT} characters - not matched"
        try:
            hits = [ire_fullmatch(e, x) for x in vals]
        except IRegexpError as ex:
            return INC, f"pattern rejected: {ex}"
        hit = all(hits) if op == "matches" else not any(hits)
    return (SAT if hit else NOT), f"{f} {op} {e!r}: observed {v!r}"

def _kleene(results):
    """[(outcome, [reason])] -> (outcome, reasons): strong Kleene AND."""
    for want in (NOT, INC):
        if any(o == want for o, _ in results):
            return want, [r for o, rs in results if o == want for r in rs]
    return SAT, []

def _check_on(check, facts, params):
    """-> (outcome, reasons) of one Check over one set of facts."""
    decls = {d["name"]: d for d in check.get("observes", [])}
    def run(assertions):
        return _kleene([(o, [w]) for o, w in (_check_assert(a, facts, decls, params) for a in assertions)])
    if check.get("applies-when"):
        aw, why = run(check["applies-when"])
        if aw == NOT: return NA, ["applies-when does not hold: " + "; ".join(why)]
        if aw == INC: return INC, ["applicability unknown: " + "; ".join(why)]
    return run(check["criteria"])

def percent_share(part, whole):
    """A share as a whole percentage, in integer arithmetic so that every
    implementation prints the same number: rounded half up, but never 0 while
    part > 0 and never 100 while part < whole."""
    if whole <= 0 or part <= 0: return 0
    if part >= whole: return 100
    return min(99, max(1, (200 * part + whole) // (2 * whole)))

def check_each(check, observation, params=None):
    """B.1.10 step 5, for a per-resource Check: EVERY resource is evaluated,
    none is skipped after the first failure. -> {results: [(id, outcome,
    reasons)], applicable, not-satisfied, inconclusive, not-applicable,
    percent-not-satisfied}, or None when the Check is not per-resource or the
    observation carries no resources. The outcome stays for-all; the counts
    say how far from it a run is."""
    if not check.get("each") or not isinstance(observation, dict) or not isinstance(observation.get("resources"), list):
        return None
    params = params or {}
    results = []
    for r in observation["resources"]:
        facts = r.get("facts") if isinstance(r, dict) else None
        o, why = _check_on(check, facts if isinstance(facts, dict) else {}, params)
        results.append((r.get("id") if isinstance(r, dict) else None, o, why))
    n = {k: sum(1 for _, o, _ in results if o == k) for k in (SAT, NOT, INC, NA)}
    applicable = len(results) - n[NA]
    return {"results": results, "applicable": applicable, "not-satisfied": n[NOT], "inconclusive": n[INC],
            "not-applicable": n[NA], "percent-not-satisfied": percent_share(n[NOT], applicable)}

def check_each_summary(kind, each):
    """One line a person reads first: how many resources, and what share, fail."""
    if each["not-satisfied"]:
        return (f"{each['not-satisfied']} of {each['applicable']} applicable {kind} resources not satisfied "
                f"({each['percent-not-satisfied']} %)")
    if each["inconclusive"]:
        return f"{each['inconclusive']} of {each['applicable']} applicable {kind} resources inconclusive"
    return f"all {each['applicable']} applicable {kind} resources satisfied"

def check_verdict(check, observation, params=None):
    """B.1.10 check-verdict: (outcome, reasons) of one Check over one recorded
    observation, with the parameter values the run was bound to."""
    params = params or {}
    if observation is None:
        return INC, ["no observation: the collector did not report"]
    if check.get("each"):
        kind = check["each"]["resource"]
        each = check_each(check, observation, params)
        if each is None:
            return INC, [f"the check runs per {kind}, but the observation carries no resources"]
        if not each["applicable"]:
            if check["each"]["allow-empty"]: return SAT, [f"no applicable {kind} observed, and allow-empty holds"]
            return INC, [f"no applicable {kind} observed, and allow-empty is false"]
        got, why = _kleene([(o, [f"{rid}: {w}" for w in ws]) for rid, o, ws in each["results"] if o != NA])
        return got, ([check_each_summary(kind, each)] + why if got != SAT else why)
    facts = observation.get("facts")
    if not isinstance(facts, dict): return INC, ["the observation carries no facts"]
    return _check_on(check, facts, params)

def check_aggregate(outcomes):
    app = [o for o in outcomes if o != NA]
    if not app: return INC
    if NOT in app: return NOT
    if INC in app: return INC
    return SAT

def _check_param_decls(check, objs):
    """-> {name: [(statement-id, declaration)]} over the covered clauses, or None
    when the requirement is not in the bundle."""
    req = objs.get(check["requirement-ref"])
    if not req or req[0] != "requirement": return None
    cover = set(check.get("statement-ids") or [s["id"] for s in req[1]["statements"]])
    out = {}
    for s in req[1]["statements"]:
        if s["id"] in cover:
            for pd in s.get("parameters", []) or []:
                out.setdefault(pd["name"], []).append((s["id"], pd))
    return out

def _param_fits(pd, fdecl, op):
    pt, ft = pd.get("type"), fdecl["type"]
    if op in CHECK_LIST_OPS:
        return pt == "list" or (pt == "choice" and pd.get("cardinality") == "many")
    if ft in ("integer", "decimal", "boolean"): return pt == ft
    return pt in ("string", "code") or (pt == "choice" and pd.get("cardinality") != "many")

def check_object_errors(oid, o, objs):
    """CHECK-1..7 over one Check -> [(rule, message)]."""
    E = []
    def bad(rule, msg): E.append((rule, f"{oid}: {msg} ({rule}: {CHECK_RULES[rule]})"))
    req = objs.get(o["requirement-ref"])
    if req and req[0] != "requirement":
        bad("CHECK-1", f"requirement-ref resolves to a {req[0]}, not a Requirement: {o['requirement-ref']}")
    elif req:
        sids = {s["id"] for s in req[1]["statements"]}
        for sid in o.get("statement-ids", []) or []:
            if sid not in sids: bad("CHECK-1", f"statement-id '{sid}' names no statement of {o['requirement-ref']}")
    names = [d["name"] for d in o["observes"]]
    for n in sorted({n for n in names if names.count(n) > 1}):
        bad("CHECK-2", f"fact '{n}' is declared twice")
    decls = {d["name"]: d for d in o["observes"]}
    params = _check_param_decls(o, objs)
    for where in ("criteria", "applies-when"):
        for i, a in enumerate(o.get(where, []) or []):
            at, op = f"{where}[{i}]", a["op"]
            d = decls.get(a["fact"])
            if d is None:
                bad("CHECK-2", f"{at} reads fact '{a['fact']}', which observes does not declare"); continue
            card, t = d.get("cardinality", "one"), d["type"]
            if op in ("present", "absent"): continue
            if op not in CHECK_OPS[card][t]:
                bad("CHECK-3", f"{at}: {op} does not fit a {t}{' list' if card == 'many' else ''} fact"); continue
            e = a.get("expected")
            if isinstance(e, dict):
                pn = e["param"]
                if op in CHECK_PATTERN_OPS:
                    bad("CHECK-4", f"{at}: binds parameter '{pn}' as a pattern"); continue
                if params is None:
                    bad("CHECK-4", f"{at}: binds parameter '{pn}', but requirement {o['requirement-ref']} "
                                   f"is not in the bundle, so the binding cannot be checked"); continue
                found = params.get(pn, [])
                if len(found) != 1:
                    bad("CHECK-4", f"{at}: parameter '{pn}' is declared {len(found)} times on the covered statements"); continue
                pd = found[0][1]
                if not _param_fits(pd, d, op):
                    bad("CHECK-4", f"{at}: parameter '{pn}' is a {pd.get('type')}, which does not fit {op} on a {t} fact")
                tg = pd.get("tightening")
                if (op == "at-most" and tg == "higher") or (op == "at-least" and tg == "lower"):
                    bad("CHECK-5", f"{at}: {op} against parameter '{pn}', which tightens {tg} - tightening it would loosen the check")
            elif op in CHECK_PATTERN_OPS and isinstance(e, str):
                try:
                    ire_compile(e)
                except IRegexpError as ex:
                    bad("CHECK-6", f"{at}: {ex}")
            elif not _expected_ok(op, t, e):
                bad("CHECK-3", f"{at}: {e!r} does not fit {op} on a {t}{' list' if card == 'many' else ''} fact")
    col = (o.get("facets") or {}).get(COLLECTOR_FACET + "@1")
    if col is not None:
        if COLLECTOR_FACET in STDLIB and not STDLIB[COLLECTOR_FACET].is_valid(col):
            e = next(STDLIB[COLLECTOR_FACET].iter_errors(col))
            bad("CHECK-7", f"collector@1 payload: {e.message[:110]} @ {'/'.join(map(str, e.absolute_path))}")
        else:
            ids = [c["id"] for c in col.get("collectors", [])]
            for n in sorted({n for n in ids if ids.count(n) > 1}):
                bad("CHECK-7", f"collector id '{n}' is used twice")
    return E

MISSING = object()       # "this Tailoring binds no value" - distinct from any JSON value

def _check_reads(check):
    """-> the parameter names the check's assertions bind with {"param": ...}"""
    return {a["expected"]["param"] for a in check["criteria"] + (check.get("applies-when") or [])
            if isinstance(a.get("expected"), dict)}

def _tailoring_bindings(check, tail, objs):
    """-> {parameter: value or MISSING} that the Tailoring binds for the
    parameters this check reads."""
    out = {}
    decls = _check_param_decls(check, objs) or {}
    for a in check["criteria"] + (check.get("applies-when") or []):
        e = a.get("expected")
        if not isinstance(e, dict) or len(decls.get(e["param"], [])) != 1: continue
        pn = e["param"]; sid = decls[pn][0][0]
        out[pn] = MISSING
        for op in tail.get("operations", []) or []:
            if (op.get("op") == "set-parameter" and op.get("requirement-ref") == check["requirement-ref"]
                    and op.get("parameter") == pn and op.get("statement-id") in (None, sid)):
                out[pn] = op["value"]
    return out

def _named(v, what):
    return f"{what} '{v}'" if v else f"no {what}"

def _evidence_chain(oid, at, a, row, read):
    """CHECK-15: row -> evidence record -> raw outputs, and observation-ref.
    read(ref) -> bytes, or None when the store does not hold it.
    -> (observation loaded from observation-ref or None, [(rule, msg)], [note])"""
    E, notes, obs = [], [], None
    def bad(msg): E.append(("CHECK-15", f"{oid}: {at}: {msg} (CHECK-15: {CHECK_RULES['CHECK-15']})"))
    def numbers(raw, value, what):
        """NUMBER-1 on an evidence file -> True when it holds; a file that breaks it is not used"""
        wrong = [f"written as {t}" for t in number_spelling_violations(raw.decode("utf-8", "replace"))] or number_violations(value)
        if wrong: E.append(("NUMBER-1", f"{oid}: {at}: {what}: {wrong[0]} (NUMBER-1: {NUMBER_RULES['NUMBER-1']})"))
        return not wrong
    def load(dref, what):
        ref, want = dref["ref"], dref["digest"]
        if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", ref):
            notes.append(f"{oid}: {at}: {what} {ref} is a URI - not resolvable offline"); return None
        if ref.startswith("/") or ".." in ref.replace("\\", "/").split("/"):
            bad(f"{what} ref {ref} leaves the bundle"); return None
        # the store has one layout: a file is named by the SHA-256 of its bytes.
        # A relative ref anywhere else is refused before it is read, so no tool
        # that walks the store can miss a blob another tool accepted.
        m = re.match(r"^evidence/sha256/([0-9a-f]{64})\Z", ref)      # \Z: a ref that ends in a line break is another ref (#68)
        if not m:
            bad(f"{what} ref {ref} is outside the store - a ref is evidence/sha256/<the 64 hex digits of its digest>"); return None
        if "sha256:" + m.group(1) != want:
            bad(f"{what} {ref} is stored under another digest than the recorded {want}"); return None
        raw = read(ref)
        if raw is None:
            notes.append(f"{oid}: {at}: {what} {ref} withheld - not in the bundle's store"); return None
        if pkg_digest(raw) != want:
            bad(f"{what} {ref} does not match its digest"); return None
        return raw
    if row.get("observation-ref"):
        raw = load(row["observation-ref"], "observation")
        if raw is not None:
            try:
                obs = json.loads(raw.decode("utf-8"))
            except Exception as ex:
                bad(f"observation file unreadable: {ex}")
            if obs is not None and not numbers(raw, obs, "observation file"): obs = None
            if obs is not None and not VALIDATORS["checkObservation"].is_valid(obs):
                bad("the observation file is not an observation"); obs = None
    if row.get("evidence-record"):
        raw = load(row["evidence-record"], "evidence record")
        rec = None
        if raw is not None:
            try:
                rec = json.loads(raw.decode("utf-8"))
            except Exception as ex:
                bad(f"evidence record unreadable: {ex}")
        if rec is not None and not numbers(raw, rec, "evidence record"): rec = None
        if rec is not None and not VALIDATORS["evidenceRecord"].is_valid(rec):
            e = next(VALIDATORS["evidenceRecord"].iter_errors(rec))
            bad(f"evidence record: {e.message[:100]} @ {'/'.join(map(str, e.absolute_path))}"); rec = None
        if rec is not None:
            if rec["check-ref"] != row["check-ref"] or rec["check-digest"] != row["check-digest"]:
                bad("the evidence record is about another check, or another version of it")
            # row and record are two statements about one run: what one says of
            # the collector and of the observation, the other says too. A field
            # left out on one side is a difference, never a reason to skip.
            rc, wc = rec.get("collector-id"), row.get("collector-id")
            if (rc or wc) and rc != wc:
                bad(f"the evidence record names {_named(rc, 'collector')}, the row {_named(wc, 'collector')}")
            if rec["subject-ref"] not in a["subject-refs"]:
                bad(f"the evidence record's subject {rec['subject-ref']} is not a subject of the assessment")
            seen = row.get("observation") if row.get("observation") is not None else obs
            row_has = row.get("observation") is not None or row.get("observation-ref") is not None
            bound = rec.get("observation-digest")
            if row_has and not bound:
                bad("the row records an observation, the evidence record binds none (no observation-digest)")
            elif bound and not row_has:
                bad("the evidence record binds an observation, the row records none")
            elif bound and seen is None:
                notes.append(f"{oid}: {at}: the observation is not available here - the evidence record's binding to it is not verified")
            elif bound and sdig(seen) != bound:
                bad("the evidence record binds another observation than the row records")
            for out in rec["outputs"]:
                load({"ref": "evidence/sha256/" + out["digest"].split(":", 1)[1], "digest": out["digest"]},
                     f"output '{out['name']}'")
    return obs, E, notes

def check_errors(objs, read=None):
    """CHECK-1..15 over a bundle -> ([(rule, message)], [note]).
    read: the evidence store reader (CHECK-15); None skips the chain."""
    E, notes = [], []
    def bad(rule, oid, msg): E.append((rule, f"{oid}: {msg} ({rule}: {CHECK_RULES[rule]})"))
    for oid, (t, o) in sorted(objs.items()):
        if t == "check":
            E += check_object_errors(oid, o, objs)
        elif t == "finding" and o.get("check-ref"):
            c = objs.get(o["check-ref"])
            if c and c[0] != "check":
                bad("CHECK-14", oid, f"check-ref resolves to a {c[0]}, not a Check: {o['check-ref']}")
            elif c:
                if c[1]["requirement-ref"] != o["requirement-ref"]:
                    bad("CHECK-14", oid, f"check {o['check-ref']} discharges {c[1]['requirement-ref']}, "
                                         f"the Finding is against {o['requirement-ref']}")
                sids = c[1].get("statement-ids")
                if sids and o.get("statement-ref") and o["statement-ref"] not in sids:
                    bad("CHECK-14", oid, f"statement-ref '{o['statement-ref']}' is not a clause check {o['check-ref']} covers")
        elif t == "assessment" and (o.get("check-results") or o.get("tailoring-ref")):
            tail = None
            if o.get("tailoring-ref"):
                tg = objs.get(o["tailoring-ref"])
                if not tg: bad("CHECK-12", oid, f"tailoring-ref does not resolve in-bundle: {o['tailoring-ref']}")
                elif tg[0] != "tailoring": bad("CHECK-12", oid, f"tailoring-ref resolves to a {tg[0]}, not a Tailoring")
                else: tail = tg[1]
            outcomes, seen = [], set()
            for i, row in enumerate(o.get("check-results", []) or []):
                at, cref = f"check-results[{i}]", row["check-ref"]
                if cref in seen: bad("CHECK-10", oid, f"{at}: check {cref} has a second row")
                seen.add(cref)
                outcomes.append(row["outcome"])
                obs = row.get("observation")
                if obs is None and row.get("observation-ref") is None and (row["outcome"] != INC or not row.get("reason")):
                    bad("CHECK-11", oid, f"{at}: no observation, yet the outcome is {row['outcome']}"
                                         f"{'' if row.get('reason') else ' and no reason is given'}")
                if read is not None:
                    o2, e2, n2 = _evidence_chain(oid, at, o, row, read)
                    E += e2; notes += n2
                    if obs is None: obs = o2
                c = objs.get(cref)
                if c is None:
                    notes.append(f"{oid}: {at}: check {cref} is not in this bundle - verdict not recomputed"); continue
                if c[0] != "check":
                    bad("CHECK-8", oid, f"{at}: check-ref resolves to a {c[0]}, not a Check"); continue
                if row["check-digest"] != sdig(c[1]):
                    bad("CHECK-8", oid, f"{at}: check-digest does not match {cref} - the check changed after the run")
                # a check without the collector facet declares no collector, so
                # any collector-id on its rows names code the check's digest does not cover
                cols = ((c[1].get("facets") or {}).get(COLLECTOR_FACET + "@1") or {}).get("collectors")
                declared = {x.get("id") for x in cols if isinstance(x, dict)} if isinstance(cols, list) else set()
                if row.get("collector-id") and row["collector-id"] not in declared:
                    bad("CHECK-13", oid, f"{at}: collector-id '{row['collector-id']}' names no collector of {cref}"
                                         f"{'' if declared else ' - the check declares none'}")
                # a name no assertion reads cannot be verified, with or without a
                # Tailoring - and the row is inside the digest an Attestation signs
                have = row.get("parameters") or {}
                for pn in sorted(set(have) - _check_reads(c[1])):
                    bad("CHECK-12", oid, f"{at}: the row records parameter '{pn}', which {cref} does not read")
                if tail is not None:
                    for pn, want in _tailoring_bindings(c[1], tail, objs).items():
                        if want is MISSING and pn in have:
                            bad("CHECK-12", oid, f"{at}: the run used {pn}={have[pn]!r}, but {o['tailoring-ref']} binds no value for it")
                        elif want is not MISSING and (pn not in have or canonical(have[pn]) != canonical(want)):
                            bad("CHECK-12", oid, f"{at}: the run used {pn}={have.get(pn, '(unbound)')!r}, "
                                                 f"{o['tailoring-ref']} binds {want!r}")
                elif row.get("parameters"):
                    notes.append(f"{oid}: {at}: parameter values are the performer's statement - no tailoring-ref to hold them to")
                if obs is None and row.get("observation-ref"):
                    notes.append(f"{oid}: {at}: observation not available here - verdict not recomputed"); continue
                got, why = check_verdict(c[1], obs, row.get("parameters"))
                each = check_each(c[1], obs, row.get("parameters"))
                if each is not None and each["applicable"]:
                    notes.append(f"{oid}: {at}: {check_each_summary(c[1]['each']['resource'], each)}")
                if got != row["outcome"]:
                    bad("CHECK-9", oid, f"{at}: recorded {row['outcome']}, check-verdict computes {got}"
                                        f"{' (' + '; '.join(why)[:200] + ')' if why else ''}")
            if o.get("check-results"):
                agg = check_aggregate(outcomes)
                if o["result"] != agg:
                    bad("CHECK-10", oid, f"result is {o['result']}, the aggregate of its check results is {agg}")
    return E, notes

def store_reader(bdir):
    """The bundle's evidence store: files beside the manifest, by relative path."""
    def read(ref):
        fp = os.path.join(bdir, *ref.split("/"))
        return open(fp, "rb").read() if os.path.isfile(fp) else None
    return read

def run_check():
    v = json.load(open(os.path.join(CONF, "check-vectors.json"), encoding="utf-8"))
    for case in v["regex-vectors"]:
        # a pattern that no JSON text may carry (a lone surrogate) is given as code points
        pat = "".join(map(chr, case["pattern-codepoints"])) if "pattern-codepoints" in case else case["pattern"]
        try:
            ire_compile(pat); valid, why = True, ""
        except IRegexpError as ex:
            valid, why = False, str(ex)
        okc = valid == case["valid"]
        bad_m = [s for s in case.get("match", []) if not (valid and ire_fullmatch(pat, s))]
        bad_n = [s for s in case.get("no-match", []) if valid and ire_fullmatch(pat, s)]
        if okc and not bad_m and not bad_n: ok("check")
        else: fail("check", f"regex {pat!r}: expected valid={case['valid']}, got {valid} {why}; "
                            f"should match but did not {bad_m}; should not match but did {bad_n}")
    for case in v["verdict-vectors"]:
        got, why = check_verdict(case["check"], case.get("observation"), case.get("parameters"))
        each = check_each(case["check"], case.get("observation"), case.get("parameters"))
        counts = None if each is None else {k: each[k] for k in each if k != "results"}
        want = case.get("expected-resources")
        if got == case["expected"] and (want is None or counts == want): ok("check")
        else: fail("check", f"verdict {case['name']}: expected {case['expected']} {want or ''}, got {got} {counts or ''} {why}")
    for case in v["aggregate-vectors"]:
        got = check_aggregate(case["outcomes"])
        if got == case["expected"]: ok("check")
        else: fail("check", f"aggregate {case['outcomes']}: expected {case['expected']}, got {got}")
    for case in v["share-vectors"]:
        got = percent_share(case["part"], case["whole"])
        if got == case["expected"]: ok("check")
        else: fail("check", f"share {case['part']} of {case['whole']}: expected {case['expected']} %, got {got} %")
    for case in v["object-vectors"]:
        m = [t for t in TYPES if VALIDATORS[t].is_valid(case["object"])]
        want = [case["type"]] if case["expected"] == "valid" else []
        if m == want: ok("check")
        else: fail("check", f"object {case['name']}: expected {case['expected']} {want}, matched {m}")
    for case in v["bundle-vectors"]:
        objs, untyped = {}, []
        for o in case["objects"]:
            t = inferType_single(o)
            if t: objs[o["id"]] = (t, o)
            else: untyped.append(o.get("id"))
        store = {k: val.encode("utf-8") for k, val in (case.get("store") or {}).items()}
        errs, notes = check_errors(objs, read=(store.get if "store" in case else None))
        named = sorted({r for r, _ in errs})
        okc = not untyped and named == sorted(set(case["expected-rules"]))
        for frag in case.get("expected-notes", []):
            if not any(frag in n for n in notes): okc = False
        if okc: ok("check")
        else: fail("check", f"bundle {case['name']}: expected rules {case['expected-rules']} notes "
                            f"{case.get('expected-notes', [])}, got {named} untyped {untyped} "
                            f"{[e[:150] for _, e in errs]} notes {[n[:100] for n in notes]}")

def run_conditional():
    v = json.load(open(os.path.join(CONF, "conditional-vectors.json"), encoding="utf-8"))
    for case in v["vectors"]:
        objs = {}
        for o in case["objects"]:
            t = inferType_single(o)
            if t: objs[o["id"]] = (t, o)
        errs = conditional_apply(case["instance"], objs)
        okc = len(errs) == case.get("expected-fails", 0)
        for frag in case.get("expected-frags", []):
            if not any(frag in e for e in errs): okc = False
        if okc: ok("conditional")
        else: fail("conditional", f"{case['name']}: expected {case.get('expected-fails')} fails "
                                  f"{case.get('expected-frags')}, got {len(errs)}: {[e[:90] for e in errs]}")

def run_dsse():
    v = json.load(open(os.path.join(CONF, "dsse-vectors.json"), encoding="utf-8"))
    for case in v["vectors"]:
        objs = {}
        for o in case["objects"]:
            t = inferType_single(o)
            if t: objs[o["id"]] = (t, o)
        att = next(o for (t, o) in objs.values() if t == "attestation")
        envs = case.get("envelopes", {})
        trusted = case.get("trusted-keys", {})
        env = envs.get(att.get("envelope-ref"))
        if att.get("envelope-ref") and env is not None:
            st, why = verify_envelope(env, att, trusted)
        else:
            st, why = "absent", ""
        tobj = next((o for (t, o) in objs.values() if t == "tailoring"), None)
        tier = derive_tier(tobj, objs, sdig, envelopes=envs, trusted=trusted) if tobj else None
        okc = True
        exp_env, exp_tier = case.get("expected-envelope"), case.get("expected-tier")
        if exp_env is not None:
            if ":" in exp_env:
                w, frag = exp_env.split(":", 1)
                okc = st == w and frag in why
            else:
                okc = st == exp_env
        if okc and exp_tier is not None:
            okc = tier == exp_tier
        if okc: ok("dsse")
        else: fail("dsse", f"{case['name']}: expected {exp_env}/{exp_tier}, got {st}({why[:70]})/{tier}")

def run_lifecycle():
    v = json.load(open(os.path.join(CONF, "lifecycle-vectors.json"), encoding="utf-8"))
    for case in v["deviation-transitions"]:
        got = case["to"] in DEV_NEXT[case["from"]]
        if got == case["valid"]: ok("lifecycle")
        else: fail("lifecycle", f"deviation {case['from']}->{case['to']}: expected valid={case['valid']}")
    for case in v["finding-transitions"]:
        got = case["to"] in FIND_NEXT[case["from"]]
        if got == case["valid"]: ok("lifecycle")
        else: fail("lifecycle", f"finding {case['from']}->{case['to']}: expected valid={case['valid']}")
    for case in v["identity-events"]:
        allowed = case["record"] == "canonical-alias"
        want = case["substitution"] == "allowed"
        if allowed == want: ok("lifecycle")
        else: fail("lifecycle", f"identity {case['record']}: substitution rule mismatch")
    def compose(a, b):
        if "supplements" in (a, b): return None
        if a == b == "equal": return "equal"
        if a == "equal": return b
        if b == "equal" and a != "equal": return a if a == "supports" else "supports"
        return "supports"
    for case in v["relationship-composition"]:
        got = compose(case["a"], case["b"])
        # floor semantics: composed claim must never be STRONGER than expected
        okv = got == case["composed"] or (case["composed"] == "supports" and got in ("supports", "intersects"))
        if okv: ok("lifecycle")
        else: fail("lifecycle", f"compose({case['a']},{case['b']}): expected {case['composed']}, got {got}")
    # shape disjointness: eleven canonical minimal objects -> exactly one match each; garbage -> zero
    P = "https://ex.org"
    MINIMAL = {
        "requirement": {"id": P+"/r", "version": "1", "lifecycle": "active",
            "statements": [{"id": "s1", "modality": "must", "obligated-parties": [P+"/p"], "prose": {"en": "X."}}]},
        "requirementSet": {"id": P+"/s", "version": "1", "lifecycle": "active", "members": [{"ref": P+"/r", "sequence": 10}]},
        "tailoring": {"id": P+"/t", "version": "1", "lifecycle": "active", "selects": [{"set-ref": P+"/s"}]},
        "mapping": {"id": P+"/m", "version": "1", "lifecycle": "active", "source-ref": P+"/r", "target-ref": P+"/r2",
            "relationship": "supports", "direction": "source-to-target", "confidence": "draft",
            "provenance": {"author-ref": P+"/p", "date": "2026-07-21"}},
        "component": {"id": P+"/c", "version": "1", "lifecycle": "active", "kind": "service"},
        "implementation": {"id": P+"/i", "version": "1", "lifecycle": "active", "component-ref": P+"/c",
            "requirement-ref": P+"/r", "responsibility": "provider",
            "satisfied-by": [{"capability-ref": "cap"}], "status": "implemented"},
        "assessment": {"id": P+"/a", "version": "1", "lifecycle": "active", "subject-refs": [P+"/r"],
            "method": {"kind": "review"}, "performer-ref": P+"/p", "time": "2026-07-21", "result": "satisfied"},
        "finding": {"id": P+"/f", "version": "1", "lifecycle": "active", "assessment-ref": P+"/a",
            "requirement-ref": P+"/r", "state": "open"},
        "attestation": {"id": P+"/at", "version": "1", "lifecycle": "active",
            "subject-semantic-digests": ["sha256:" + "0"*64], "content-manifest-digest": "sha256:" + "0"*64,
            "signer": P+"/p", "timestamp": "2026-07-21"},
        "risk": {"id": P+"/rk", "version": "1", "lifecycle": "active", "scenario": {"en": "X."},
            "owner-ref": P+"/p", "state": "identified"},
        "check": {"id": P+"/ck", "version": "1", "lifecycle": "active", "requirement-ref": P+"/r",
            "platform": P+"/platform/linux", "observes": [{"name": "x", "type": "integer"}],
            "criteria": [{"fact": "x", "op": "at-most", "expected": 4}], "confidence": "draft",
            "provenance": {"author-ref": P+"/p", "date": "2026-11-11"}},
    }
    for want, o in MINIMAL.items():
        m = [t for t in TYPES if VALIDATORS[t].is_valid(o)]
        if m == [want]: ok("lifecycle")
        else: fail("lifecycle", f"disjointness: minimal {want} matches {m}")
    if [t for t in TYPES if VALIDATORS[t].is_valid({"id": P+"/x", "version": "1", "lifecycle": "active"})]:
        fail("lifecycle", "disjointness: field-free object matches a type")
    else: ok("lifecycle")

# ---------------- ADVICE (CP-ADVICE-1, kernel 2.0.0) ----------------
# An advice pack is a bundle whose manifest carries a pack header and whose
# objects are Components: a vendor's recommendations as one published file.
# A capability is a CLAIM (requirement, clauses, text, suggested parameter
# values); the only statement that a requirement is met stays the
# Implementation in the user's namespace, which cites the capability.
# ADVICE-1..3 hold a pack to being advice; 4..7 hold capabilities and the
# edges that cite them, in every bundle; 8..10 hold the vendor's manifest a
# set keeps (packs/sha256/<hex>, beside the manifest like an envelope) to
# the objects in the set; 11 is import - the one lawful replacement the
# composition engine knows.
PACK_STORE = "packs/sha256/"
ADVICE_RULES = {
    "ADVICE-1": "advice must not be able to change what is required or how it is assessed - a pack holds Components and nothing else",
    "ADVICE-2": "a pack cannot carry an object under someone else's identity, and so cannot replace one: its ids, its own id and its publisher share one origin",
    "ADVICE-3": "advice must not reach a computation through a facet: no facet on a pack's object declares a semantics class",
    "ADVICE-4": "a capability-ref must name one thing: capability ids are unique within a Component",
    "ADVICE-5": "a recommendation is about a requirement; when that requirement is in the bundle the edge is typed and the clauses it names exist",
    "ADVICE-6": "a suggested value the catalog cannot accept is the publisher's defect, found before a user adopts it",
    "ADVICE-7": "an edge that leans on a capability nobody declared proves nothing, and advice applies to a system because the system contains the product - the cited component is in the bundle, declares the capability, and is the edge's own or one of its members",
    "ADVICE-8": "a kept pack manifest is content-addressed and lives beside the manifest: its name is the SHA-256 of its bytes, it carries a pack header, and the bundle's manifest does not list it",
    "ADVICE-9": "the advice in the set is what the vendor published: every object a kept pack manifest lists is in the bundle at that version with that semantic digest",
    "ADVICE-10": "one release of a pack in a set, and one pack per object",
    "ADVICE-11": "import never overwrites what the pack does not own: it adds ids the bundle does not hold and replaces ids an earlier release of the same pack brought",
}

def _adv(rule, where, msg):
    return (rule, f"{where}: {msg} ({rule}: {ADVICE_RULES[rule]})")

def pack_errors(manifest, objs, pinned_decl=None):
    """ADVICE-1..3 over a published pack -> [(rule, message)]. objs: the
    objects the manifest lists, id -> (type, obj). A manifest without a
    pack header is not a pack and is held to nothing here."""
    pack = manifest.get("pack")
    if not pack: return []
    E, pid = [], pack["id"]
    origin = uri_origin(pid)
    for oid in sorted(objs):
        t = objs[oid][0]
        if t != "component":
            E.append(_adv("ADVICE-1", pid, f"{oid} is a {t} - an advice pack holds components only"
                          f"{' (an attestation travels beside the manifest, D3.1)' if t == 'attestation' else ''}"))
    pub = pack["publisher"]["ref"]
    if uri_origin(pub) != origin:
        E.append(_adv("ADVICE-2", pid, f"publisher {pub} is not under the pack's origin {origin}"))
    for oid in sorted(objs):
        if uri_origin(oid) != origin:
            E.append(_adv("ADVICE-2", pid, f"{oid} is not under the pack's origin {origin}"))
    for oid in sorted(objs):
        for key in sorted((objs[oid][1].get("facets") or {})):
            base = key.rsplit("@", 1)[0]
            if key.startswith("private:"): continue      # declares [] by definition (D10)
            decl = STDLIB_DECL[base] if base in STDLIB_DECL else (pinned_decl or {}).get(base)
            if decl:                                     # unregistered is facet_errors' failure, not ours
                E.append(_adv("ADVICE-3", oid, f"facet {key} declares modifies-semantics {sorted(decl)} - "
                                               f"not allowed in an advice pack"))
    return E

def capability_errors(objs):
    """ADVICE-4..6 over every Component -> ([(rule, message)], notes)."""
    E, notes = [], []
    for oid in sorted(objs):
        t, o = objs[oid]
        if t != "component": continue
        caps = o.get("capabilities") or []
        ids = [c["id"] for c in caps]
        for n in sorted({n for n in ids if ids.count(n) > 1}):
            E.append(_adv("ADVICE-4", oid, f"capability id '{n}' is used twice"))
        untyped = 0
        for c in caps:
            at, rref = f"{oid}#{c['id']}", c.get("requirement-ref")
            if rref is None:
                if c.get("statement-ids"):
                    E.append(_adv("ADVICE-5", at, "statement-ids without a requirement-ref"))
                continue
            req = objs.get(rref)
            if not req:
                untyped += 1; continue
            if req[0] != "requirement":
                E.append(_adv("ADVICE-5", at, f"requirement-ref resolves to a {req[0]}, not a Requirement: {rref}")); continue
            sids = [s["id"] for s in req[1]["statements"]]
            for sid in c.get("statement-ids") or []:
                if sid not in sids:
                    E.append(_adv("ADVICE-5", at, f"statement-id '{sid}' names no statement of {rref}"))
            cover = set(c.get("statement-ids") or sids)
            decls = {}
            for s in req[1]["statements"]:
                if s["id"] in cover:
                    for pd in s.get("parameters", []) or []:
                        decls.setdefault(pd["name"], []).append(pd)
            for pn in sorted(c.get("parameter-bindings") or {}):
                found = decls.get(pn, [])
                if len(found) != 1:
                    E.append(_adv("ADVICE-6", at, f"binds parameter '{pn}', which is declared {len(found)} times "
                                                  f"on the covered statements of {rref}")); continue
                verdict = param_check(found[0], c["parameter-bindings"][pn])
                if verdict != "valid":
                    E.append(_adv("ADVICE-6", at, f"binds parameter '{pn}' to a value "
                                                  f"{'of the wrong kind' if verdict == 'invalid' else 'outside the declared space'}"))
        if untyped:
            notes.append(f"{oid}: {untyped} capability requirement-ref(s) outside the bundle - not typed (resolves-if-present)")
    return E, notes

def split_capability_ref(ref, own):
    """-> (component id, capability id). A bare id names a capability of the
    edge's own component; `<component-id>#<capability-id>` names one of that
    component."""
    if "#" in ref:
        cid, cap = ref.rsplit("#", 1)
        return cid, cap
    return own, ref

def capability_ref_errors(objs):
    """ADVICE-7 over every Implementation -> [(rule, message)]."""
    E = []
    for oid in sorted(objs):
        t, o = objs[oid]
        if t != "implementation": continue
        own = o["component-ref"]
        for sb in o.get("satisfied-by", []):
            ref = sb.get("capability-ref")
            if ref is None: continue
            cid, cap = split_capability_ref(ref, own)
            comp = objs.get(cid)
            if not comp:
                if cid != own:      # the edge's own component is closure_errors' failure
                    E.append(_adv("ADVICE-7", oid, f"cites {ref}, but component {cid or '(none)'} is not in the bundle"))
                continue
            if comp[0] != "component":
                E.append(_adv("ADVICE-7", oid, f"cites {ref}, which resolves to a {comp[0]}, not a Component")); continue
            if cap not in {c["id"] for c in comp[1].get("capabilities", []) or []}:
                E.append(_adv("ADVICE-7", oid, f"cites capability '{cap}', which {cid} does not declare")); continue
            if cid != own:
                owner = objs.get(own)
                if owner and owner[0] == "component" and \
                   cid not in {m["component-ref"] for m in owner[1].get("members", []) or []}:
                    E.append(_adv("ADVICE-7", oid, f"cites {ref}, but {cid} is not a member of {own}"))
    return E

def read_kept_packs(bdir):
    """-> [(file name, bytes)] of the pack manifests a bundle keeps."""
    d = os.path.join(bdir, *PACK_STORE.strip("/").split("/"))
    if not os.path.isdir(d): return []
    return [(fn, open(os.path.join(d, fn), "rb").read()) for fn in sorted(os.listdir(d))
            if os.path.isfile(os.path.join(d, fn))]

def kept_pack_errors(kept, manifest, objs):
    """ADVICE-8..10 -> ([(rule, message)], [(name, kept manifest)] that are
    well-formed). kept: [(file name, bytes)] under packs/sha256/."""
    E, packs = [], []
    for name, raw in sorted(kept):
        where = PACK_STORE + name
        if hashlib.sha256(raw).hexdigest() != name:
            E.append(_adv("ADVICE-8", where, "does not match its name")); continue
        try:
            km = json.loads(raw.decode("utf-8"))
        except Exception:
            E.append(_adv("ADVICE-8", where, "is not readable JSON")); continue
        if not VALIDATORS["contentManifest"].is_valid(km) or "pack" not in km:
            E.append(_adv("ADVICE-8", where, "is not a content manifest with a pack header")); continue
        packs.append((name, km))
    for e in (manifest or {}).get("objects", []) or []:
        if str(e.get("path", "")).startswith(PACK_STORE):
            E.append(_adv("ADVICE-8", e["path"], "is listed in the bundle's manifest"))
    release, owner = {}, {}
    for name, km in packs:
        pid, rel = km["pack"]["id"], km["pack"]["version"]
        if pid in release:
            E.append(_adv("ADVICE-10", pid, f"releases {release[pid]} and {rel} are both in the bundle"))
            continue
        release[pid] = rel
        for e in km.get("objects", []):
            if e["id"] in owner:
                E.append(_adv("ADVICE-10", e["id"], f"is listed by two kept manifests: {owner[e['id']]} and {pid}"))
                continue
            owner[e["id"]] = pid
            tgt = objs.get(e["id"])
            if not tgt:
                E.append(_adv("ADVICE-9", e["id"], f"is listed by release {rel} of {pid} and is not in the bundle"))
            elif tgt[1].get("version") != e["version"]:
                E.append(_adv("ADVICE-9", e["id"], f"is at version {tgt[1].get('version')}, release {rel} of {pid} lists {e['version']}"))
            elif sdig(tgt[1]) != e["semantic-digest"]:
                E.append(_adv("ADVICE-9", e["id"], f"differs from release {rel} of {pid} (semantic digest) - "
                                                   f"the vendor's advice was edited after import"))
    return E, packs

def pack_publisher(pack, mdigest, objs, envelopes=None, trusted=None, notes=None):
    """claimed | proven. The publisher is CLAIMED by the header and the
    origin its ids share with it (ADVICE-2). It is PROVEN when an
    Attestation whose signer has that origin binds this manifest's digest -
    and, in verification mode, its envelope verifies under a trusted key.
    The same two words, and the same envelope check, as the Tailoring tier
    (derive_tier)."""
    origin = uri_origin(pack["id"])
    for oid in sorted(objs):
        t, o = objs[oid]
        if t != "attestation" or uri_origin(o.get("signer", "")) != origin: continue
        if o.get("content-manifest-digest") != mdigest: continue
        if trusted is not None:
            env = (envelopes or {}).get(o.get("envelope-ref"))
            if o.get("envelope-ref") and env is not None:
                st, why = verify_envelope(env, o, trusted)
            else:
                st, why = "error", "unsigned attestation (no envelope) cannot prove in verification mode"
            if st != "verified":
                if notes is not None: notes.append(f"{oid}: {why}")
                continue
        return "proven"
    return "claimed"

def compose_advice(a_objs, a_kept, b_manifest, b_digest, b_objs, pinned_decl=None):
    """ADVICE-11: what importing pack B into bundle A does. a_objs / b_objs:
    id -> (type, obj); a_kept: [(name, kept manifest)] of A; b_digest: the
    hex SHA-256 of B's manifest bytes. Nothing is written; the result is the
    plan and its receipt:
      result    import | replace | already-imported | refused
      added / replaced / removed   object ids
      dangling  the edges of A that cite a capability the new release drops
      unchanged how many objects of A the import leaves as they are"""
    R = {"result": "refused", "added": [], "replaced": [], "removed": [], "dangling": [],
         "capabilities": {}, "unchanged": len(a_objs), "errors": []}
    pack = b_manifest.get("pack")
    if not pack:
        R["errors"].append(_adv("ADVICE-11", "(import)", "the manifest carries no pack header - this is not an advice pack"))
        return R
    R["errors"] += pack_errors(b_manifest, b_objs, pinned_decl)
    if any(name == b_digest for name, _ in a_kept):
        R["result"] = "already-imported"; R["errors"] = []
        return R
    prev = [km for _, km in a_kept if km["pack"]["id"] == pack["id"]]
    owned = {e["id"] for km in prev for e in km.get("objects", [])}
    other = {e["id"]: km["pack"]["id"] for _, km in a_kept if km["pack"]["id"] != pack["id"]
             for e in km.get("objects", [])}
    for oid in sorted(b_objs):
        if oid not in a_objs: R["added"].append(oid)
        elif oid in owned: R["replaced"].append(oid)
        else:
            R["errors"].append(_adv("ADVICE-11", oid, f"is already in the set and "
                               f"{'belongs to ' + other[oid] if oid in other else 'not part of ' + pack['id']}"))
    R["removed"] = sorted(o for o in owned if o in a_objs and o not in b_objs)
    for oid in R["replaced"]:
        old = {c["id"]: c for c in a_objs[oid][1].get("capabilities", []) or []}
        new = {c["id"]: c for c in b_objs[oid][1].get("capabilities", []) or []}
        d = {"added": sorted(set(new) - set(old)), "removed": sorted(set(old) - set(new)),
             "changed": sorted(k for k in set(old) & set(new) if canonical(old[k]) != canonical(new[k]))}
        if any(d.values()): R["capabilities"][oid] = d
    for iid in sorted(a_objs):
        t, o = a_objs[iid]
        if t != "implementation": continue
        for sb in o.get("satisfied-by", []):
            ref = sb.get("capability-ref")
            if ref is None: continue
            cid, cap = split_capability_ref(ref, o["component-ref"])
            if cid in R["removed"] or (cid in R["replaced"] and
                                       cap not in {c["id"] for c in b_objs[cid][1].get("capabilities", []) or []}):
                R["dangling"].append(f"{iid} -> {ref}")
    if R["errors"]:
        return R
    R["result"] = "replace" if prev else "import"
    R["unchanged"] = len(a_objs) - len(R["replaced"]) - len(R["removed"])
    return R

def advice_errors(manifest, objs, pinned_decl=None, kept=None):
    """Everything ADVICE-1..10 says about one bundle -> ([(rule, message)], notes, kept packs)."""
    listed = {e["id"] for e in (manifest or {}).get("objects", []) or []}
    E = pack_errors(manifest or {}, {i: v for i, v in objs.items() if i in listed}, pinned_decl)
    ce, notes = capability_errors(objs)
    ke, packs = kept_pack_errors(kept or [], manifest, objs)
    return E + ce + capability_ref_errors(objs) + ke, notes, packs

def _advice_typed(objects):
    objs, untyped = {}, []
    for o in objects:
        t = inferType_single(o)
        if t: objs[o["id"]] = (t, o)
        else: untyped.append(o.get("id"))
    return objs, untyped

def _advice_fill(manifest, published):
    """A vector's manifest lists its objects by id; version and digests are
    COMPUTEd from the objects as published, so no literal goes stale."""
    by_id = {o["id"]: o for o in published}
    m = copy.deepcopy(manifest)
    for e in m.get("objects", []):
        src = by_id.get(e["id"])
        if e.get("semantic-digest") == "COMPUTE" and src is not None:
            e["semantic-digest"] = sdig(src)
        e.setdefault("version", src["version"] if src else "1")
        e.setdefault("package-digest", "sha256:" + "0" * 64)
        e.setdefault("path", "objects/" + e["id"].rsplit("/", 1)[-1] + ".json")
    return m

def _advice_kept(case_kept):
    """-> [(file name, bytes)] for a vector's kept manifests. The bytes are
    the manifest's canonical form; `name` overrides the computed name."""
    out = []
    for k in case_kept or []:
        raw = k["raw"].encode("utf-8") if "raw" in k else canonical(_advice_fill(k["manifest"], k.get("published", []))).encode("utf-8")
        out.append((k.get("name") or hashlib.sha256(raw).hexdigest(), raw))
    return out

def run_advice():
    v = json.load(open(os.path.join(CONF, "advice-vectors.json"), encoding="utf-8"))
    def judge(kind, case, errs, notes=(), extra_ok=True, untyped=()):
        named = sorted({r for r, _ in errs})
        okc = extra_ok and not untyped and named == sorted(set(case.get("expected-rules", [])))
        for frag in case.get("expected-frags", []):
            if not any(frag in m for _, m in errs): okc = False
        for frag in case.get("expected-notes", []):
            if not any(frag in n for n in notes): okc = False
        if okc: ok("advice")
        else: fail("advice", f"{kind} {case['name']}: expected rules {case.get('expected-rules', [])} "
                             f"frags {case.get('expected-frags', [])}, got {named} untyped {list(untyped)} "
                             f"{[m[:150] for _, m in errs]} notes {[n[:100] for n in notes]}")
    for case in v["shape-vectors"]:
        if case["kind"] == "manifest":
            got = "valid" if VALIDATORS["contentManifest"].is_valid(case["document"]) else "invalid"
        else:
            m = [t for t in TYPES if VALIDATORS[t].is_valid(case["document"])]
            got = "valid" if m == [case["kind"]] else "invalid"
        if got == case["expected"]: ok("advice")
        else: fail("advice", f"shape {case['name']}: expected {case['expected']}, got {got}")
    for case in v["pack-vectors"]:
        objs, untyped = _advice_typed(case["objects"])
        m = _advice_fill(case["manifest"], case["objects"])
        errs = [] if VALIDATORS["contentManifest"].is_valid(m) else [("SCHEMA", "manifest schema violation")]
        if not errs:
            errs = pack_errors(m, objs, case.get("declared")) + [("KERNEL-1", e) for e in kernel_pin_errors(m, objs)]
        judge("pack", case, errs, untyped=untyped)
    for case in v["graph-vectors"]:
        objs, untyped = _advice_typed(case["objects"])
        ce, notes = capability_errors(objs)
        judge("graph", case, ce + capability_ref_errors(objs), notes, untyped=untyped)
    for case in v["kept-vectors"]:
        objs, untyped = _advice_typed(case["objects"])
        errs, packs = kept_pack_errors(_advice_kept(case["kept"]), case.get("manifest"), objs)
        judge("kept", case, errs, extra_ok=len(packs) == case.get("expected-packs", len(packs)), untyped=untyped)
    for case in v["publisher-vectors"]:
        m = _advice_fill(case["manifest"], case.get("published", []))
        mdig = "sha256:" + hashlib.sha256(canonical(m).encode("utf-8")).hexdigest()
        subjects = copy.deepcopy(case["objects"])
        for o in subjects:
            if o.get("content-manifest-digest") == "COMPUTE": o["content-manifest-digest"] = mdig
        objs, untyped = _advice_typed(subjects)
        got = pack_publisher(m["pack"], mdig, objs, envelopes=case.get("envelopes"),
                             trusted=case.get("trusted-keys"))
        if got == case["expected"] and not untyped: ok("advice")
        else: fail("advice", f"publisher {case['name']}: expected {case['expected']}, got {got} untyped {untyped}")
    for case in v["import-vectors"]:
        a_objs, ua = _advice_typed(case["a"]["objects"])
        _, a_packs = kept_pack_errors(_advice_kept(case["a"].get("kept")), None, {})
        b_objs, ub = _advice_typed(case["b"]["objects"])
        bm = _advice_fill(case["b"]["manifest"], case["b"]["objects"])
        bdig = hashlib.sha256(canonical(bm).encode("utf-8")).hexdigest()
        R = compose_advice(a_objs, a_packs, bm, bdig, b_objs)
        exp = case["expected"]
        same = all(R[k] == exp[k] for k in ("result", "added", "replaced", "removed", "dangling") if k in exp) \
               and ("unchanged" not in exp or R["unchanged"] == exp["unchanged"])
        judge("import", case, R["errors"], extra_ok=same, untyped=ua + ub)

# ---------------- 2) bundle validation ----------------
PARAM_TOKEN = re.compile(r"\{param:([^}]+)\}")

def pkg_digest(raw):
    return "sha256:" + hashlib.sha256(raw).hexdigest()

def eol_hint(raw, want):
    """A package digest is over delivered BYTES (D3.1), so a checkout that
    re-spells line endings fails it - correctly. The verdict stands; this
    only names the cause, because 6,963 bare 'package-digest mismatch'
    lines (the 1.0.0 corpus on any non-Windows clone) explain nothing."""
    if b"\r\n" in raw and pkg_digest(raw.replace(b"\r\n", b"\n")) == want:
        return " - the bytes differ ONLY in line endings: CRLF on disk, LF digested (re-checkout the path; see .gitattributes)"
    if b"\r\n" not in raw and pkg_digest(raw.replace(b"\n", b"\r\n")) == want:
        return " - the bytes differ ONLY in line endings: LF on disk, CRLF digested (re-checkout the path; see .gitattributes)"
    return ""

def infer_type(obj):
    matches = [t for t in TYPES if VALIDATORS[t].is_valid(obj)]
    return matches

def validate_object(section, path, obj):
    number_failures(section, path, obj=obj)
    matches = infer_type(obj)
    if len(matches) != 1:
        best = ""
        if not matches:
            errs = sorted(VALIDATORS["requirement"].iter_errors(obj), key=lambda e: -len(e.absolute_path))
            guess = {t: len(list(VALIDATORS[t].iter_errors(obj))) for t in TYPES}
            t0 = min(guess, key=guess.get)
            e0 = next(iter(VALIDATORS[t0].iter_errors(obj)), None)
            best = f" (closest {t0}: {e0.message[:110] if e0 else '?'} @ {'/'.join(map(str, e0.absolute_path)) if e0 else ''})"
            if isinstance(obj, dict) and ("scenario" in obj or "owner-ref" in obj):
                # the Risk signature: name the violated rule and print its why
                best += "".join(f"\n      FAIL [{rid}] {what} - {RISK_RULES[rid]}"
                                for rid, what in risk_rule_violations(obj))
            # two fields that 1.0.0 left as free text and 2.0.0 types
            best += "".join(f"\n      FAIL [{rid}] {what} - {DATE_RULES[rid]}"
                            for rid, what in date_rule_violations(obj))
        fail(section, f"{path}: matches {matches or 'NO type'}{best}")
        return None
    ok(section)
    t = matches[0]
    viol = optional_empty_violations(obj)
    if viol: fail(section, f"{path}: optional empty containers present: {viol}")
    if t == "requirement":
        sids = {s["id"] for s in obj["statements"]}
        if len(sids) != len(obj["statements"]):
            fail(section, f"{path}: duplicate statement ids (unique-within, B.1.3) — identity addressing becomes ambiguous")
        for s in obj["statements"]:
            declared = {p["name"] for p in s.get("parameters", [])}
            for lang, txt in s["prose"].items():
                for tok in PARAM_TOKEN.findall(txt if isinstance(txt, str) else " ".join(txt)):
                    if tok not in declared:
                        fail(section, f"{path}: unbound {{param:{tok}}} in statement {s['id']} (prose-params-resolve)")
        for fid, payload in (obj.get("facets") or {}).items():
            if isinstance(payload, dict) and "by-statement" in payload and isinstance(payload["by-statement"], dict):
                for sid in payload["by-statement"]:
                    if sid not in sids:
                        fail(section, f"{path}: facet {fid} by-statement key '{sid}' names no statement (D10 rev)")
    return t

def load_facet_pins(bdir, manifest, section):
    """The facet schemas a manifest pins: files must exist, digests must
    verify, and they form the registry for non-stdlib facet payload
    validation (#17). ONE loader for validate_bundle and validate_examples:
    the example pass had its own copy that checked existence and digest
    only, so a stub pinned under a stdlib id passed the default run and
    failed `validate_core.py jascon/examples` (D26) - two verdicts on one
    folder. Returns (pinned: id -> validator, pinned_decl: id -> classes)."""
    pinned = {}
    pinned_decl = {}
    for fe in manifest.get("facet-schemas", []):
        fp = os.path.join(bdir, fe["path"])
        if not os.path.exists(fp):
            fail(section, f"{fe['path']}: pinned facet schema listed but missing"); continue
        raw = open(fp, "rb").read()
        if pkg_digest(raw) != fe["digest"]:
            fail(section, f"{fe['path']}: pinned facet schema digest mismatch{eol_hint(raw, fe['digest'])}")
        try:
            sd = json.loads(raw.decode("utf-8"))
            number_failures(section, fe["path"], raw, sd)
            pinned[sd["id"]] = REGISTRY(sd.get("schema", {"type": "object"}))
            # P10 #29: the pin's declaration feeds the attach/detach op-law;
            # a pin that omits it is dangerous-by-default (D10: all four)
            pinned_decl[sd["id"]] = sd.get("modifies-semantics",
                                           ["assessment", "tailoring", "selection", "rendering"])
            # #26 (D26 final): a pin of a STDLIB id must be the descriptor
            # VERBATIM - the pin and the normative schema cannot diverge
            if sd["id"] in STDLIB_RAW and canonical(sd.get("schema")) != canonical(STDLIB_RAW[sd["id"]]):
                fail(section, f"{fe['path']}: pin of stdlib facet {sd['id']} DIVERGES from the normative descriptor (D26)")
        except Exception as e:
            fail(section, f"{fe['path']}: pinned facet schema unreadable: {e}")
    return pinned, pinned_decl

def beside_attestations(bdir, listed_paths):
    """Attestations BESIDE the manifest (D3.1): JSON files in the manifest's
    own folder that it does not list and that type as an Attestation. A pack
    lists Components only (ADVICE-1), so its vendor's Attestation is here."""
    out = {}
    for fn in sorted(os.listdir(bdir)):
        if not fn.endswith(".json") or fn == "content-manifest.json" or fn in listed_paths: continue
        try:
            o = json.load(open(os.path.join(bdir, fn), encoding="utf-8"))
        except Exception:
            continue
        if isinstance(o, dict) and inferType_single(o) == "attestation": out[o["id"]] = ("attestation", o)
    return out

def advice_report(section, bdir, manifest, raw_manifest, objs, pinned_decl, envelopes):
    """CP-ADVICE-1 for one bundle: ADVICE-1..10, and who published what."""
    a_errs, a_notes, packs = advice_errors(manifest, objs, pinned_decl, read_kept_packs(bdir))
    for _, e in a_errs: fail(section, e)
    for n in a_notes: print(f"    note: {n}")
    atts = {i: v for i, v in objs.items() if v[0] == "attestation"}
    def status(pack, mdig, where):
        envs = dict(envelopes or {})
        for _, (_, a) in sorted(atts.items()):
            ref = a.get("envelope-ref")
            if ref and ref not in envs and os.path.isfile(os.path.join(bdir, ref)):
                try: envs[ref] = json.load(open(os.path.join(bdir, ref), encoding="utf-8"))
                except Exception: pass
        pn = []
        st = pack_publisher(pack, mdig, atts, envelopes=envs, trusted=TRUSTED, notes=pn)
        tag = {"claimed": "publisher CLAIMED [header and prefix - UNPROVEN]",
               "proven": ("publisher PROVEN [attestation binds the manifest + signature VERIFIED]" if TRUSTED is not None
                          else "publisher ATTESTED, NOT VERIFIED [an attestation binds the manifest; no proof without --trusted-keys]")}[st]
        print(f"    {where}: {pack['id']} release {pack['version']} by {pack['publisher']['ref']} = {tag}")
        for n in pn: print(f"          {n}")
    is_pack = bool(manifest.get("pack")) and VALIDATORS["contentManifest"].is_valid(manifest)
    if is_pack or packs:
        # a pack's own Attestation, and the vendor's beside a set that kept a pack's manifest
        atts.update(beside_attestations(bdir, {e["path"] for e in manifest.get("objects", [])}))
    if is_pack:
        status(manifest["pack"], pkg_digest(raw_manifest), "pack")
    for name, km in packs:
        status(km["pack"], "sha256:" + name, f"kept pack ({len(km.get('objects', []))} object(s))")

def validate_bundle(bdir):
    section = os.path.relpath(bdir, ROOT).replace("\\", "/")
    mpath = os.path.join(bdir, "content-manifest.json")
    if not os.path.exists(mpath):
        fail(section, "no content-manifest.json"); return
    raw_manifest = open(mpath, "rb").read()
    manifest = json.loads(raw_manifest.decode("utf-8"))
    number_failures(section, "content-manifest.json", raw_manifest, manifest)
    if not VALIDATORS["contentManifest"].is_valid(manifest):
        e = next(VALIDATORS["contentManifest"].iter_errors(manifest))
        fail(section, f"manifest schema: {e.message[:120]} @ {'/'.join(map(str, e.absolute_path))}")
    else:
        ok(section)
    listed = {e["path"]: e for e in manifest.get("objects", [])}
    typec = collections.Counter()
    seen_ids = {}
    bundle_objs = {}
    for rel, entry in listed.items():
        fp = os.path.join(bdir, rel)
        if not os.path.exists(fp):
            fail(section, f"{rel}: listed but missing"); continue
        raw = open(fp, "rb").read()
        if pkg_digest(raw) != entry["package-digest"]:
            fail(section, f"{rel}: package-digest mismatch{eol_hint(raw, entry['package-digest'])}")
        obj = json.loads(raw.decode("utf-8"))
        number_failures(section, rel, raw)       # the spelling; validate_object holds the value
        if sdig(obj) != entry["semantic-digest"]:
            fail(section, f"{rel}: semantic-digest mismatch")
        t = validate_object(section, rel, obj)
        if t: typec[t] += 1
        if obj.get("id") != entry["id"]:
            fail(section, f"{rel}: manifest id != object id")
        if obj.get("id") in seen_ids:
            fail(section, f"{rel}: object id already used by {seen_ids[obj['id']]} (unique-within — the twin-catalog corpse)")
        seen_ids[obj.get("id")] = rel
        if t: bundle_objs[obj["id"]] = (t, obj)
    pinned, pinned_decl = load_facet_pins(bdir, manifest, section)
    # DSSE envelopes (#24): envelope-ref resolves to a file BESIDE the
    # manifest (nothing signed contains its own signature, D3); with
    # --trusted-keys the run is in verification mode.
    envelopes = {}
    for oid, (t2, o2) in bundle_objs.items():
        if t2 != "attestation" or not o2.get("envelope-ref"): continue
        ep = os.path.join(bdir, o2["envelope-ref"])
        if os.path.exists(ep):
            try:
                envelopes[o2["envelope-ref"]] = json.load(open(ep, encoding="utf-8"))
            except Exception as e:
                fail(section, f"{o2['envelope-ref']}: envelope unreadable: {e}")
        else:
            fail(section, f"{oid}: envelope-ref '{o2['envelope-ref']}' does not resolve beside the manifest")
    for oid, (t2, o2) in sorted(bundle_objs.items()):
        if t2 != "attestation": continue
        if o2.get("envelope-ref"):
            env = envelopes.get(o2["envelope-ref"])
            if env is not None:
                st, why = verify_envelope(env, o2, TRUSTED)
                tag = {"verified": "signature VERIFIED (Ed25519)",
                       "unverified": f"signature UNVERIFIED - {why}"}.get(st, f"FAIL - {why}")
                if st == "error": fail(section, f"{oid}: dsse: {why}")
                print(f"    dsse: {oid} = {tag}")
        else:
            print(f"    dsse: {oid} = no envelope (unsigned attestation)")
    # reference taxonomy (#16) + facet payloads (#17) + tier duties (#19/#24)
    for e in closure_errors(bundle_objs):
        fail(section, e)
    for e in tailoring_duty_errors(bundle_objs, pinned_decl=pinned_decl,
                                   envelopes=envelopes, trusted=TRUSTED):
        fail(section, e)
    for e in kernel_pin_errors(manifest, bundle_objs): fail(section, e)
    s_errs, s_notes = scale_errors(load_scale_pins(bdir, manifest, section), bundle_objs)
    for e in s_errs: fail(section, e)
    for n in s_notes: print(f"    note: {n}")
    # CP-RISK-1: B.1.9 risk-coverage report (+ RISK-11 errors), RISK-9/10 notes
    cov, cerrs, cnotes = risk_coverage(bundle_objs, envelopes=envelopes, trusted=TRUSTED)
    for e in cerrs: fail(section, e)
    for n in cnotes + risk_link_notes(bundle_objs): print(f"    note: {n}")
    report_authors_and_reviews(section, bundle_objs, envelopes)
    # the report is printed where there is a register to report on; the
    # policy switch applies regardless - a bundle with a Tailoring and NO
    # Risk at all is the limiting case of "justified by no Risk", not an
    # exemption from it
    if cov["risks"] or REQUIRE_RISK_BASIS:
        for tid, r in cov["tailorings"].items():
            if tid == NO_TAILORING: tid = "(no Tailoring: every requirement is in play)"
            print(f"    risk-coverage: {tid} [{r['tier']}] selected={r['selected']}"
                  f"{'+ (open: predicate select)' if r['open-selection'] else ''} "
                  f"justified={len(r['covered'])} uncovered={len(r['uncovered'])}")
            for q in r["uncovered"]:
                if REQUIRE_RISK_BASIS: fail(section, risk_basis_fail(tid, q))
                else: print(f"      uncovered: {q}")
    for e in facet_errors([(oid, o) for oid, (t, o) in bundle_objs.items()], pinned):
        fail(section, e)
    # CP-CHECK-1: check shapes, recomputed verdicts, the evidence chain
    c_errs, c_notes = check_errors(bundle_objs, read=store_reader(bdir))
    for _, e in c_errs: fail(section, e)
    for n in c_notes: print(f"    note: {n}")
    # CP-ADVICE-1: pack rules, capabilities and the edges that cite them, kept manifests
    advice_report(section, bdir, manifest, raw_manifest, bundle_objs, pinned_decl, envelopes)
    # #24: report the derived Tailoring tier DISTINCTLY (spec:399) — a prefix
    # claim is an honest-publisher signal, not proof; in verification mode
    # (--trusted-keys) proven additionally requires a verifying envelope.
    for tid, (tt, tobj2) in sorted(bundle_objs.items()):
        if tt == "tailoring":
            tnotes = []
            tr = derive_tier(tobj2, bundle_objs, sdig, envelopes=envelopes, trusted=TRUSTED, notes=tnotes)
            note = {"authority-claimed": " [prefix claim - UNPROVEN]",
                    "authority-proven": (" [attestation digest-matched + signature VERIFIED]"
                                         if TRUSTED is not None else
                                         " [attestation digest-matched; UNVERIFIED - run with --trusted-keys]")}.get(tr, "")
            print(f"    tier: {tid} = {tr}{note}")
            for n in tnotes:
                print(f"          {n}")
    on_disk = set()
    for base, _, files in os.walk(bdir):
        for fn in files:
            rel = os.path.relpath(os.path.join(base, fn), bdir).replace("\\", "/")
            if rel.startswith("objects/") and rel.endswith(".json"): on_disk.add(rel)
    for rel in sorted(on_disk - set(listed)):
        fail(section, f"{rel}: on disk but not in manifest")
    return typec

def validate_examples():
    exdir = os.path.join(SKILL, "examples")
    section = "skill-examples"
    typec = collections.Counter()
    exobjs = {}
    # The example manifest is checked like any other (it was not, and at
    # 1.0.0 its package digests were a mix of CRLF and LF spellings - 8 of
    # 12 failed on an LF tree, the other 4 on a CRLF tree, unnoticed).
    # Attestations live BESIDE the manifest (D3.1) and are not listed.
    raw_manifest = open(os.path.join(exdir, "content-manifest.json"), "rb").read()
    manifest = json.loads(raw_manifest.decode("utf-8"))
    number_failures(section, "content-manifest.json", raw_manifest, manifest)
    if VALIDATORS["contentManifest"].is_valid(manifest): ok(section)
    else: fail(section, "content-manifest.json: manifest schema violation")
    listed = {e["path"]: e for e in manifest.get("objects", [])}
    pins = {fe["path"]: fe for fe in manifest.get("facet-schemas", [])}
    scale_paths = {sp["path"] for sp in manifest.get("scales", []) or []}
    pinned, pinned_decl = load_facet_pins(exdir, manifest, section)   # the same loader as validate_bundle (D26 included)
    for rel in sorted(set(listed) - set(os.listdir(exdir))):
        fail(section, f"{rel}: listed but missing")
    for fn in sorted(os.listdir(exdir)):
        if not fn.endswith(".json") or fn == "content-manifest.json" or fn in pins or fn in scale_paths:
            continue
        raw = open(os.path.join(exdir, fn), "rb").read()
        obj = json.loads(raw.decode("utf-8"))
        number_failures(section, fn, raw)
        t = validate_object(section, fn, obj)
        if t:
            typec[t] += 1
            exobjs[obj["id"]] = (t, obj)
        entry = listed.get(fn)
        if entry is None:
            if t != "attestation":
                fail(section, f"{fn}: on disk but not in manifest")
            continue
        if pkg_digest(raw) != entry["package-digest"]:
            fail(section, f"{fn}: package-digest mismatch{eol_hint(raw, entry['package-digest'])}")
        if sdig(obj) != entry["semantic-digest"]:
            fail(section, f"{fn}: semantic-digest mismatch")
        if obj.get("id") != entry["id"]:
            fail(section, f"{fn}: manifest id != object id")
    for e in closure_errors(exobjs): fail(section, e)
    # facet payloads against stdlib / the pins just loaded (#17) - the
    # example pass loaded the pins and never applied them
    for e in facet_errors([(oid, o) for oid, (t, o) in exobjs.items()], pinned): fail(section, e)
    for e in kernel_pin_errors(manifest, exobjs): fail(section, e)
    s_errs, s_notes = scale_errors(load_scale_pins(exdir, manifest, section), exobjs)
    for e in s_errs: fail(section, e)
    for n in s_notes: print(f"    note: {n}")
    c_errs, c_notes = check_errors(exobjs, read=store_reader(exdir))
    for _, e in c_errs: fail(section, e)
    for n in c_notes: print(f"    note: {n}")
    advice_report(section, exdir, manifest, raw_manifest, exobjs, pinned_decl, None)
    cov, cerrs, cnotes = risk_coverage(exobjs)
    for e in cerrs: fail(section, e)
    for n in cnotes + risk_link_notes(exobjs): print(f"    note: {n}")
    report_authors_and_reviews(section, exobjs)
    for tid, r in cov["tailorings"].items():
        print(f"    risk-coverage: {tid} [{r['tier']}] selected={r['selected']}"
              f"{'+ (open: predicate select)' if r['open-selection'] else ''} "
              f"justified={len(r['covered'])} uncovered={r['uncovered']}")
        if REQUIRE_RISK_BASIS:
            for q in r["uncovered"]:
                fail(section, risk_basis_fail(tid, q))
    return typec

# ---------------- run ----------------
# --trusted-keys FILE puts the run in verification mode (#24): a JSON map
# of signer URI -> Ed25519 public key (hex). Without it, structural mode.
# --compose DIR_A DIR_B runs the D3.5 composition engine over two bundles.
TRUSTED = None
REQUIRE_RISK_BASIS = False
REQUIRE_AUTHORS = False
AS_OF = datetime.datetime.now(datetime.timezone.utc).date()    # REVIEW-1: the date of the run, unless --as-of sets it
_argv = sys.argv[1:]
if "--require-authors" in _argv:         # policy switch: AUTHOR-1..4 lines become failures
    REQUIRE_AUTHORS = True
    _argv.remove("--require-authors")
if "--as-of" in _argv:
    _i = _argv.index("--as-of")
    if not VALIDATORS["date"].is_valid(_argv[_i + 1]): sys.exit(f"--as-of {_argv[_i + 1]!r} is not a date, YYYY-MM-DD")
    try: AS_OF = datetime.date.fromisoformat(_argv[_i + 1])
    except ValueError: sys.exit(f"--as-of {_argv[_i + 1]!r} is not a day of the calendar")
    _argv = _argv[:_i] + _argv[_i + 2:]
if "--require-risk-basis" in _argv:      # policy switch: uncovered selections become failures
    REQUIRE_RISK_BASIS = True
    _argv.remove("--require-risk-basis")
if "--trusted-keys" in _argv:
    _i = _argv.index("--trusted-keys")
    TRUSTED = json.load(open(_argv[_i + 1], encoding="utf-8"))
    _argv = _argv[:_i] + _argv[_i + 2:]
if "--compose" in _argv:
    _i = _argv.index("--compose")
    da, db = _argv[_i + 1], _argv[_i + 2]
    (ao, ap), (bo, bp) = _load_compose_side(da), _load_compose_side(db)
    res, errs = compose(ao, ap, bo, bp)
    print(f"== compose {da} + {db} ==")
    for fid, ver in sorted(res.items()):
        print(f"  resolved: {fid} @ {ver}")
    for e in errs:
        print(f"  ERROR: {e}")
    sys.exit(1 if errs else 0)

def _load_listed(bdir):
    """-> (manifest, raw manifest bytes, id -> (type, obj)) for the objects a bundle's manifest lists."""
    raw = open(os.path.join(bdir, "content-manifest.json"), "rb").read()
    m = json.loads(raw.decode("utf-8"))
    objs = {}
    for e in m.get("objects", []):
        o = json.load(open(os.path.join(bdir, e["path"]), encoding="utf-8"))
        t = inferType_single(o)
        if t: objs[o["id"]] = (t, o)
    return m, raw, objs

if "--import-advice" in _argv:
    _i = _argv.index("--import-advice")
    dset, dpack = _argv[_i + 1], _argv[_i + 2]
    am, _, ao = _load_listed(dset)
    bm, braw, bo = _load_listed(dpack)
    _, a_packs = kept_pack_errors(read_kept_packs(dset), am, ao)
    R = compose_advice(ao, a_packs, bm, hashlib.sha256(braw).hexdigest(), bo)
    pk = bm.get("pack") or {}
    print(f"== import-advice {dpack} -> {dset} (dry run, nothing is written) ==")
    if pk: print(f"  pack: {pk['id']} release {pk['version']} by {pk['publisher']['ref']}")
    print(f"  result: {R['result']}")
    for k in ("added", "replaced", "removed"):
        for oid in R[k]: print(f"  {k}: {oid}")
    for oid, d in sorted(R["capabilities"].items()):
        print(f"  capabilities of {oid}: added {d['added']} removed {d['removed']} changed {d['changed']}")
    for d in R["dangling"]: print(f"  dangling edge: {d}")
    if R["result"] in ("import", "replace"):
        print(f"  receipt: unchanged {R['unchanged']} of {len(ao) - len(R['replaced']) - len(R['removed'])} "
              f"- added {len(R['added'])} component(s); the pack holds components only (ADVICE-1), "
              f"so no requirement, tailoring or assessment is touched")
    for _, e in R["errors"]: print(f"  ERROR: {e}")
    sys.exit(1 if R["result"] == "refused" else 0)

print("== conformance corpus ==")
run_jcs(); run_modality(); run_parameters(); run_tailoring(); run_attestation(); run_facets(); run_references(); run_lifecycle(); run_tiers(); run_dsse(); run_composition(); run_conditional(); run_risk(); run_kernel(); run_scale(); run_check(); run_advice(); run_author()
for k in ("jcs", "modality", "parameter", "tailoring", "attestation", "facet", "reference", "lifecycle", "tier", "dsse", "composition", "conditional", "risk", "kernel", "scale", "check", "advice", "author"):
    print(f"  {k}: {counts[k]} pass, {counts[k + ':FAIL']} fail")

print("== bundles ==")
targets = _argv
if not targets:
    ce = os.path.join(ROOT, "converted_examples")
    targets = []
    for corpus in sorted(os.listdir(ce)):
        cdir = os.path.join(ce, corpus)
        if not os.path.isdir(cdir): continue
        for d in sorted(os.listdir(cdir)):
            if d.endswith("-bundle") and os.path.isdir(os.path.join(cdir, d)):
                targets.append(os.path.join(cdir, d))
    ep = os.path.join(SKILL, "example-packs")      # CP-ADVICE-1: the worked advice pack(s)
    if os.path.isdir(ep):
        targets += [os.path.join(ep, d) for d in sorted(os.listdir(ep)) if os.path.isdir(os.path.join(ep, d))]
total_types = collections.Counter()
for b in targets:
    tc = validate_bundle(b) or collections.Counter()
    total_types += tc
    sec = os.path.relpath(b, ROOT).replace("\\", "/")
    print(f"  {sec}: {counts[sec]} pass, {counts[sec + ':FAIL']} fail  {dict(tc)}")
tc = validate_examples()
total_types += tc
print(f"  skill-examples: {counts['skill-examples']} pass, {counts['skill-examples:FAIL']} fail  {dict(tc)}")
print("== type coverage ==", dict(total_types))

if fails:
    print(f"\n{len(fails)} FAILURES:")
    for f in fails[:60]: print("  -", f)
    sys.exit(1)
print("\nALL GREEN")
