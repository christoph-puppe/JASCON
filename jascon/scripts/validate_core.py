#!/usr/bin/env python3
"""JASCON - gate-item-2 executable validator.

Runs, in order:
1. CONFORMANCE CORPUS: JCS vectors (canonical form + empty-omission rule),
   modality-lattice vectors, parameter vectors, tailoring vectors
   (same-target conflict, tier-scoped Deviation duties), attestation
   bi-modal vectors.
2. BUNDLE VALIDATION over every converted_examples bundle + the skill's
   example bundle: type inference (an object must match EXACTLY ONE of the
   TEN kernel shapes - shape-disjointness is a conformance property),
   closed-shape schema validation, code systems, by-statement facet keys
   vs. host statement ids (D10 rev), {param:} token binding (the 216
   rule), optional-empty-container rule (D3.3), manifest completeness +
   both digests re-verified per object.
3. RISK (CP-RISK-1, kernel 2.0.0): Risk is the tenth kernel type; the
   schema carries RISK-1..6 (named on failure by risk_rule_violations),
   this file adds the closure rules (RISK-7/8), typed Risk edges
   (RISK-12), the state machine (C.3c), the Deviation link note (RISK-9)
   and the risk-coverage primitive (B.1.9): for every Tailoring, which
   selected requirement is justified by NO live Risk - the ISO/IEC 27001
   6.1.3 d question, computed instead of audited by hand.
   `--require-risk-basis` turns uncovered selections into failures.

Exit 0 = all green. Usage: uv run --with jsonschema validate_core.py [bundle-dir ...]
"""
import json, hashlib, os, re, sys, copy, collections, base64
from decimal import Decimal
import jsonschema

# canonical decimal string (D3.4; rev P10 #37: leading zeros AND negative
# zero are non-canonical spellings — one value, one spelling)
DECIMAL_RE = r"^(-?[1-9][0-9]*(\.[0-9]+)?|0(\.[0-9]+)?|-0\.[0-9]*[1-9][0-9]*)$"

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
SKILL = os.path.join(ROOT, "jascon")
SCHEMA = json.load(open(os.path.join(SKILL, "schemas", "oscal-semantic-core-2.0.0.schema.json"), encoding="utf-8"))
CONF = os.path.join(SKILL, "conformance")

TYPES = ["requirement", "requirementSet", "tailoring", "mapping", "component",
         "implementation", "assessment", "finding", "attestation", "risk"]
REGISTRY = jsonschema.validators.Draft202012Validator
VALIDATORS = {t: REGISTRY({"$ref": f"#/$defs/{t}", "$defs": SCHEMA["$defs"]}) for t in TYPES}
VALIDATORS["contentManifest"] = REGISTRY({"$ref": "#/$defs/contentManifest", "$defs": SCHEMA["$defs"]})

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
                       "threat-refs", "component-refs", "treatments", "risk-refs", "tailoring-refs"}
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
DSSE_PAYLOAD_TYPE = "application/vnd.oscal-semantic-core.attestation+json"
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
    m = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", str(v))
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
        if not isinstance(value, int) or isinstance(value, bool): return "invalid"
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
    # shape disjointness: ten canonical minimal objects -> exactly one match each; garbage -> zero
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
    }
    for want, o in MINIMAL.items():
        m = [t for t in TYPES if VALIDATORS[t].is_valid(o)]
        if m == [want]: ok("lifecycle")
        else: fail("lifecycle", f"disjointness: minimal {want} matches {m}")
    if [t for t in TYPES if VALIDATORS[t].is_valid({"id": P+"/x", "version": "1", "lifecycle": "active"})]:
        fail("lifecycle", "disjointness: field-free object matches a type")
    else: ok("lifecycle")

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
                        fail(section, f"{path}: unbound {{param:{tok}}} in statement {s['id']} (the 216 rule)")
        for fid, payload in (obj.get("facets") or {}).items():
            if isinstance(payload, dict) and "by-statement" in payload and isinstance(payload["by-statement"], dict):
                for sid in payload["by-statement"]:
                    if sid not in sids:
                        fail(section, f"{path}: facet {fid} by-statement key '{sid}' names no statement (D10 rev)")
    return t

def validate_bundle(bdir):
    section = os.path.relpath(bdir, ROOT).replace("\\", "/")
    mpath = os.path.join(bdir, "content-manifest.json")
    if not os.path.exists(mpath):
        fail(section, "no content-manifest.json"); return
    manifest = json.load(open(mpath, encoding="utf-8"))
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
    # pinned facet schemas: files must exist, digests must verify, and they
    # form the registry for non-stdlib facet payload validation (#17)
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
    # CP-RISK-1: B.1.9 risk-coverage report (+ RISK-11 errors), RISK-9/10 notes
    cov, cerrs, cnotes = risk_coverage(bundle_objs, envelopes=envelopes, trusted=TRUSTED)
    for e in cerrs: fail(section, e)
    for n in cnotes + risk_link_notes(bundle_objs): print(f"    note: {n}")
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
    manifest = json.load(open(os.path.join(exdir, "content-manifest.json"), encoding="utf-8"))
    if VALIDATORS["contentManifest"].is_valid(manifest): ok(section)
    else: fail(section, "content-manifest.json: manifest schema violation")
    listed = {e["path"]: e for e in manifest.get("objects", [])}
    pins = {fe["path"]: fe for fe in manifest.get("facet-schemas", [])}
    for rel, fe in pins.items():
        fp = os.path.join(exdir, rel)
        if not os.path.exists(fp): fail(section, f"{rel}: pinned facet schema listed but missing"); continue
        raw = open(fp, "rb").read()
        if pkg_digest(raw) != fe["digest"]:
            fail(section, f"{rel}: pinned facet schema digest mismatch{eol_hint(raw, fe['digest'])}")
    for rel in sorted(set(listed) - set(os.listdir(exdir))):
        fail(section, f"{rel}: listed but missing")
    for fn in sorted(os.listdir(exdir)):
        if not fn.endswith(".json") or fn == "content-manifest.json" or fn in pins:
            continue
        raw = open(os.path.join(exdir, fn), "rb").read()
        obj = json.loads(raw.decode("utf-8"))
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
    cov, cerrs, cnotes = risk_coverage(exobjs)
    for e in cerrs: fail(section, e)
    for n in cnotes + risk_link_notes(exobjs): print(f"    note: {n}")
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
_argv = sys.argv[1:]
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

print("== conformance corpus ==")
run_jcs(); run_modality(); run_parameters(); run_tailoring(); run_attestation(); run_facets(); run_references(); run_lifecycle(); run_tiers(); run_dsse(); run_composition(); run_conditional(); run_risk()
for k in ("jcs", "modality", "parameter", "tailoring", "attestation", "facet", "reference", "lifecycle", "tier", "dsse", "composition", "conditional", "risk"):
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
