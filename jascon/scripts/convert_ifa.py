#!/usr/bin/env python3
"""IFA GoodRead lifecycle set (SSP + AP + AR + POA&M) + leveraged/leveraging
SSP pair + component-definition example -> Semantic Core lifecycle bundle.
Census: drafts/gate-3-census.md §4 (2026-07-22). The five lifecycle types at
document scale: Components (with authorizations - the D5 anchor),
Implementations (param bindings against the REAL minted AC-6.1 ODPs;
inheritance via inherited-from{component-ref, basis-ref}), Assessment (AR
ConMon result, AP as method payload, observations as facet + landmark
evidence URIs), Findings (POA&M risks -> states/actions/deviations), and an
Attestation modeling the SSP's date-authorized ATO. Referenced Requirements
(AC-6.1, AC-2) ride along as byte-identical copies from the US.SP800-53
bundle - an authorization package carries its baseline. Coverage target: 0.
Depends on: convert_nist.py output (run first)."""
import json, os, re, collections
from oscal_conv_lib import make_T, slug, Bundle, inventory, coverage, report, semantic_digest

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SRCDIR = os.path.join(ROOT, "sources", "nist")
OUTDIR = os.path.join(ROOT, "converted_examples", "US.IFA-GoodRead")
NISTB = os.path.join(ROOT, "converted_examples", "US.SP800-53", "sp800-53-core-bundle")
NS = "https://ifa.gov/goodread"          # the source's own (fictional) agency domain
F_SYS = f"{NS}/facet/system@1"
F_OBS = f"{NS}/facet/observations@1"
F_RISK = f"{NS}/facet/risk@1"
F_AP = f"{NS}/facet/assessment-plan@1"
F_PROTO = f"{NS}/facet/protocols@1"

lang_wraps = collections.Counter()
T = make_T("en", lang_wraps)

def load(fn, key):
    return json.load(open(os.path.join(SRCDIR, fn), encoding="utf-8"))[key]

SSP = load("ifa_ssp.json", "system-security-plan")
AP = load("ifa_assessment-plan.json", "assessment-plan")
AR = load("ifa_assessment-results.json", "assessment-results")
POAM = load("ifa_plan-of-action-and-milestones.json", "plan-of-action-and-milestones")
LEV = load("oscal_leveraged-example_ssp.json", "system-security-plan")
LVG = load("oscal_leveraging-example_ssp.json", "system-security-plan")
CDEF = load("example-component-definition.json", "component-definition")

paths = collections.Counter()
for pfx, doc, key in [("ssp", SSP, "system-security-plan"), ("ap", AP, "assessment-plan"),
                      ("ar", AR, "assessment-results"), ("poam", POAM, "plan-of-action-and-milestones"),
                      ("lev", LEV, "system-security-plan"), ("lvg", LVG, "system-security-plan"),
                      ("cdef", CDEF, "component-definition")]:
    inventory({key: doc}, pfx, paths)

findings_notes = []
def note(s): findings_notes.append(s)

# ---------- carry the referenced Requirements (closure: in-bundle) ----------
bundle = Bundle(os.path.join(OUTDIR, "ifa-core-bundle"))
carried = []
for cid in ("ac-6-1", "ac-2"):
    p = os.path.join(NISTB, "objects", "req", f"{cid}.json")
    if not os.path.exists(p):
        raise SystemExit(f"missing {p} - run convert_nist.py first")
    obj = json.load(open(p, encoding="utf-8"))
    bundle.add(f"objects/req/{cid}.json", obj)
    carried.append(obj["id"])
REQ_AC61 = f"https://ns.nist.gov/sp800-53/req/AC-6.1"
REQ_AC2 = f"https://ns.nist.gov/sp800-53/req/AC-2"

# statement-id spelling: the SSP pair writes `ac-2_stmt.a`, the catalog `ac-2_smt.a`
n_stmt_respell = 0
def stmt_norm(sid, cid):
    global n_stmt_respell
    if not sid: return None
    s = sid
    if s.startswith(cid + "_"): s = s[len(cid) + 1:]
    if s.startswith("stmt"):
        s = "smt" + s[4:]; n_stmt_respell += 1
    return s

# PUA codepoints in source text (the soware defect)
n_pua = 0
def pua_scan(v):
    global n_pua
    if isinstance(v, str):
        n_pua += sum(1 for ch in v if 0xE000 <= ord(ch) <= 0xF8FF)
    return v

# ---------- parties (landmark URIs by #16 - no party objects) ----------
def party_uri(doc, uuid, default_slug):
    for p in doc["metadata"].get("parties", []) or []:
        if p["uuid"] == uuid:
            return f"{NS}/party/{slug(p.get('name', default_slug))}"
    return f"{NS}/party/{default_slug}"

# ================= 1. the GoodRead system (SSP) =================
V_SSP = SSP["metadata"]["version"]
sc = SSP["system-characteristics"]
COMP_SYS = f"{NS}/component/system1234"
AUTH_ATO = "auth-ifa-ato"
sys_users = [{"title": u.get("title"), "description": pua_scan(u.get("description")),
              "privileges": [{"title": a.get("title"), "functions": a.get("functions-performed", [])}
                             for a in u.get("authorized-privileges", []) or []]}
             for u in SSP["system-implementation"].get("users", []) or []]
sys_inv = [{"description": pua_scan(i.get("description")),
            "props": {p["name"]: p["value"] for p in i.get("props", []) or []},
            "components": [c["component-uuid"] for c in i.get("implemented-components", []) or []]}
           for i in SSP["system-implementation"].get("inventory-items", []) or []]
ssp_comp = SSP["system-implementation"]["components"][0]
comp_sys = {"id": COMP_SYS, "version": V_SSP, "label": sc["system-name"], "lifecycle": "active",
            "title": ssp_comp.get("title", sc["system-name"]), "kind": "system",
            "capabilities": [],
            "authorizations": [{"id": AUTH_ATO,
                                "authority-ref": f"{NS}/party/authorizing-official",
                                "scope-label": f"ATO {sc.get('date-authorized', '?')} "
                                               f"({sc.get('security-sensitivity-level', '?')})"}],
            "facets": {F_SYS: {
                "system-ids": sc.get("system-ids", []),
                "description": T(pua_scan(sc.get("description", "")), "system"),
                "status": sc.get("status", {}).get("state"),
                "sensitivity": sc.get("security-sensitivity-level"),
                "date-authorized": sc.get("date-authorized"),
                "impact": {"information-types": sc.get("system-information", {}).get("information-types", []),
                           "security-impact-level": sc.get("security-impact-level", {})},
                "boundary": T(pua_scan(sc.get("authorization-boundary", {}).get("description", "")), "system"),
                "network-architecture": T(pua_scan(sc.get("network-architecture", {}).get("description", "")), "system"),
                "data-flow": T(pua_scan(sc.get("data-flow", {}).get("description", "")), "system"),
                "users": sys_users,
                "inventory-items": sys_inv}}}

# implemented-requirement ac-6.1 -> capability + Implementation
ir = SSP["control-implementation"]["implemented-requirements"][0]
bc = ir["by-components"][0]
comp_sys["capabilities"].append({"id": "cap-ac-6.1", "requirement-ref": REQ_AC61,
                                 "description": pua_scan(bc.get("description", ""))})
pbind = {sp["param-id"]: (sp["values"][0] if len(sp["values"]) == 1 else sp["values"])
         for sp in SSP["control-implementation"].get("set-parameters", [])}
for v in pbind.values(): pua_scan(v if isinstance(v, str) else " ".join(v))
# verify bindings name declared params of the carried AC-6.1
ac61 = json.load(open(os.path.join(NISTB, "objects", "req", "ac-6-1.json"), encoding="utf-8"))
declared_61 = {p["name"] for s in ac61["statements"] for p in s.get("parameters", [])}
unresolved_bind = sorted(set(pbind) - declared_61)
bundle.add("objects/component/system1234.json", comp_sys)
IMPL_SYS = f"{NS}/impl/system1234-ac-6.1"
bundle.add("objects/impl/system1234-ac-6-1.json",
           {"id": IMPL_SYS, "version": V_SSP, "lifecycle": "active",
            "component-ref": COMP_SYS, "requirement-ref": REQ_AC61,
            "responsibility": "provider",
            "satisfied-by": [{"capability-ref": "cap-ac-6.1"}],
            "parameter-bindings": pbind,
            "status": bc.get("implementation-status", {}).get("state", "implemented"),
            "evidence-refs": [f"{NS}/doc/ssp-{SSP['uuid']}"]})

# ================= 2. leveraged / leveraging pair (D5) =================
V_LEV, V_LVG = LEV["metadata"]["version"], LVG["metadata"]["version"]
COMP_IAAS = f"{NS}/component/csp-iaas"
COMP_APP = f"{NS}/component/csp-application"
COMP_SAAS = f"{NS}/component/saas"
COMP_APPL = f"{NS}/component/access-control-appliance"
AUTH_CSP = "auth-csp-iaas-2018"

lev_ir = LEV["control-implementation"]["implemented-requirements"][0]
lev_caps, lev_resp, uuid_placeholder = [], [], 0
for st in lev_ir.get("statements", []) or []:
    for b in st.get("by-components", []) or []:
        exp = b.get("export", {})
        for i, pv in enumerate(exp.get("provided", []) or []):
            if pv["uuid"].startswith("11111111"): uuid_placeholder += 1
            lev_caps.append({"id": f"cap-provided-{len(lev_caps) + 1}",
                             "requirement-ref": REQ_AC2,
                             "description": pua_scan(pv.get("description", ""))})
        for rs in exp.get("responsibilities", []) or []:
            if rs["uuid"].startswith("11111111"): uuid_placeholder += 1
            lev_resp.append({"description": pua_scan(rs.get("description", ""))})
la = (LVG["system-implementation"].get("leveraged-authorizations") or [{}])[0]
bundle.add("objects/component/csp-iaas.json",
           {"id": COMP_IAAS, "version": V_LEV, "label": LEV["system-characteristics"]["system-name"],
            "lifecycle": "active", "title": LEV["metadata"]["title"], "kind": "system",
            "members": [{"component-ref": COMP_APP, "context": "application"}],
            "capabilities": lev_caps,
            "authorizations": [{"id": AUTH_CSP,
                                "authority-ref": f"{NS}/party/csp-authorizing-official",
                                "scope-label": f"{la.get('title', 'CSP IaaS leveraged authorization')} "
                                               f"({la.get('date-authorized', '?')})"}],
            "facets": {F_SYS: {"customer-responsibilities": lev_resp,
                               "description": T(pua_scan(LEV["system-characteristics"].get("description", "")), "system")}}})
app_comp = next(c for c in LEV["system-implementation"]["components"] if c["type"] != "this-system")
bundle.add("objects/component/csp-application.json",
           {"id": COMP_APP, "version": V_LEV, "label": app_comp.get("title", "Application"),
            "lifecycle": "active", "title": app_comp.get("title", "Application"), "kind": "software"})
KIND_MAP = {"this-system": "system", "system": "system", "software": "software",
            "application": "software", "appliance": "hardware", "service": "service"}
kind_mapped = collections.Counter()
appl = next(c for c in LVG["system-implementation"]["components"] if c["type"] == "appliance")
kind_mapped["appliance->hardware"] += 1
bundle.add("objects/component/access-control-appliance.json",
           {"id": COMP_APPL, "version": V_LVG, "label": appl.get("title", "").strip(" *"),
            "lifecycle": "active", "title": appl.get("title", "").strip(" *"), "kind": "hardware",
            "capabilities": [{"id": "cap-consumer-ac-2a", "requirement-ref": REQ_AC2,
                              "description": pua_scan(next((sa.get("description", "")
                                  for st in LVG["control-implementation"]["implemented-requirements"][0].get("statements", [])
                                  for b in st.get("by-components", []) for sa in b.get("satisfied", []) or []), ""))}]})
bundle.add("objects/component/saas.json",
           {"id": COMP_SAAS, "version": V_LVG,
            "label": LVG["system-characteristics"]["system-name"], "lifecycle": "active",
            "title": LVG["metadata"]["title"], "kind": "system",
            "members": [{"component-ref": COMP_IAAS, "context": "leveraged system"},
                        {"component-ref": COMP_APPL, "context": "internal appliance"}],
            "facets": {F_SYS: {"description": T(pua_scan(LVG["system-characteristics"].get("description", "")), "system")}}})
lvg_ir = LVG["control-implementation"]["implemented-requirements"][0]
lvg_sids = sorted({stmt_norm(st.get("statement-id"), lvg_ir["control-id"])
                   for st in lvg_ir.get("statements", []) or [] if st.get("statement-id")})
lvg_bind = {sp["param-id"]: (sp["values"][0] if len(sp["values"]) == 1 else sp["values"])
            for sp in lvg_ir.get("set-parameters", [])}
ac2 = json.load(open(os.path.join(NISTB, "objects", "req", "ac-2.json"), encoding="utf-8"))
declared_2 = {p["name"] for s in ac2["statements"] for p in s.get("parameters", [])}
unresolved_bind = sorted(set(unresolved_bind) | (set(lvg_bind) - declared_2))
bundle.add("objects/impl/saas-ac-2.json",
           {"id": f"{NS}/impl/saas-ac-2", "version": V_LVG, "lifecycle": "active",
            "component-ref": COMP_SAAS, "requirement-ref": REQ_AC2,
            "statement-refs": lvg_sids,
            "responsibility": "shared",
            "satisfied-by": [{"inherited-from": {"component-ref": COMP_IAAS, "basis-ref": AUTH_CSP}},
                             {"capability-ref": "cap-consumer-ac-2a"}],
            "parameter-bindings": lvg_bind,
            "status": "implemented",
            "evidence-refs": [f"{NS}/doc/ssp-{LVG['uuid']}"]})
lev_sids = sorted({stmt_norm(st.get("statement-id"), lev_ir["control-id"])
                   for st in lev_ir.get("statements", []) or [] if st.get("statement-id")})
lev_bind = {sp["param-id"]: (sp["values"][0] if len(sp["values"]) == 1 else sp["values"])
            for sp in lev_ir.get("set-parameters", [])}
unresolved_bind = sorted(set(unresolved_bind) | (set(lev_bind) - declared_2))
bundle.add("objects/impl/csp-iaas-ac-2.json",
           {"id": f"{NS}/impl/csp-iaas-ac-2", "version": V_LEV, "lifecycle": "active",
            "component-ref": COMP_IAAS, "requirement-ref": REQ_AC2,
            "statement-refs": lev_sids,
            "responsibility": "provider",
            "satisfied-by": [{"capability-ref": c["id"]} for c in lev_caps],
            "parameter-bindings": lev_bind,
            "status": "implemented",
            "evidence-refs": [f"{NS}/doc/ssp-{LEV['uuid']}"]})

# ================= 3. component-definition example =================
V_CDEF = CDEF["metadata"]["version"]
for c in CDEF.get("components", []) or []:
    caps = []
    for ci in c.get("control-implementations", []) or []:
        for cir in ci.get("implemented-requirements", []) or []:
            caps.append({"id": f"cap-{slug(cir.get('control-id', 'x'))}",
                         "requirement-ref": f"https://ns.nist.gov/sp800-53/req/{cir.get('control-id', '').upper()}",
                         "description": pua_scan(cir.get("description", ""))})
    kind = KIND_MAP.get(c.get("type", "software"), "software")
    obj = {"id": f"{NS}/component/{slug(c.get('title', 'component'))}",
           "version": V_CDEF, "label": c.get("title", ""), "lifecycle": "active",
           "title": c.get("title", ""), "kind": kind}
    if caps: obj["capabilities"] = caps
    protos = [{"name": p.get("name"), "title": p.get("title"),
               "port-ranges": p.get("port-ranges", [])} for p in c.get("protocols", []) or []]
    if protos: obj["facets"] = {F_PROTO: {"protocols": protos}}
    bundle.add(f"objects/component/{slug(c.get('title', 'component'))}.json", obj)

# ================= 4. Assessment (AR result; AP as method) =================
V_AR = AR["metadata"]["version"]
res = AR["results"][0]
ASSESS = f"{NS}/assessment/conmon-2023-06"
observations = []
for src, tag in ((res.get("observations", []), "ar"), (POAM.get("observations", []), "poam")):
    for o in src:
        observations.append({"id": f"{NS}/evidence/obs-{o['uuid'][:8]}",
                             "title": o.get("title"), "description": T(pua_scan(o.get("description", "")), "observation"),
                             "methods": o.get("methods", []), "collected": o.get("collected"),
                             **({"expires": o["expires"]} if o.get("expires") else {}),
                             "source-doc": tag})
# dedupe by uuid (the engineer-role observation appears in both AR and POA&M)
seen, obs_dedup = set(), []
for o in observations:
    if o["id"] in seen:
        note(f"observation carried in both AR and POA&M (deduped): {o['title']}")
        continue
    seen.add(o["id"]); obs_dedup.append(o)
ap_payload = {"activities": [{"title": a.get("title"),
                              "description": T(pua_scan(a.get("description", "")), "ap"),
                              "steps": [{"title": s.get("title"),
                                         "description": T(pua_scan(s.get("description", "")), "ap")}
                                        for s in a.get("steps", []) or []]}
                             for a in AP.get("local-definitions", {}).get("activities", []) or []],
              "tasks": [{"title": t.get("title"), "type": t.get("type")} for t in AP.get("tasks", []) or []],
              "reviewed-controls": [ic["control-id"] for cs in AP["reviewed-controls"]["control-selections"]
                                    for ic in cs["include-controls"]]}
finding_src = res["findings"][0]
bundle.add("objects/assessment/conmon-2023-06.json",
           {"id": ASSESS, "version": V_AR, "lifecycle": "active",
            "title": res.get("title", AR["metadata"]["title"]),
            "subject-refs": [COMP_SYS, REQ_AC61],
            "method": {F_AP: ap_payload},
            "performer-ref": party_uri(AR, AR["metadata"]["responsible-parties"][0]["party-uuids"][0], "assessor")
                             if AR["metadata"].get("responsible-parties") else f"{NS}/party/assessor",
            "time": res.get("start", "2023-06-02"),
            "result": "not-satisfied" if finding_src["target"]["status"]["state"] == "not-satisfied" else "satisfied",
            "evidence-refs": [o["id"] for o in obs_dedup],
            "facets": {F_OBS: {"observations": obs_dedup}}})

# ================= 5. Findings (AR finding + POA&M risks) =================
V_POAM = POAM["metadata"]["version"]
risks = {r["uuid"]: r for r in POAM.get("risks", [])}
items = POAM.get("poam-items", [])
target_obj = finding_src["target"]["target-id"]           # ac-6.1_obj - the 53A objective address
def risk_facet(rk):
    f = {"risk-status": rk.get("status"), "deadline": rk.get("deadline"),
         "statement": T(pua_scan(rk.get("statement", "")), "risk"),
         "characterizations": [{"facets": [{"name": x["name"], "value": x["value"], "system": x["system"]}
                                           for x in ch.get("facets", [])],
                                "origin-actors": [a.get("actor-uuid") for a in ch.get("origin", {}).get("actors", [])]}
                               for ch in rk.get("characterizations", []) or []]}
    mit = [T(pua_scan(m.get("description", "")), "risk") for m in rk.get("mitigating-factors", []) or []]
    if mit: f["mitigating-factors"] = mit
    return f
def actions_of(rk):
    out = []
    for rm in rk.get("remediations", []) or []:
        for t in rm.get("tasks", []) or []:
            due = t.get("timing", {}).get("within-date-range", {}).get("end")
            a = {"description": f"{rm.get('title', '')}: {t.get('title', '')}",
                 "status": rm.get("lifecycle", "planned")}
            if due: a["due"] = {"type": "datetime", "value": due}
            out.append(a)
    return out or [{"description": rk.get("title", "remediation"), "status": "planned"}]

# RISK-2 continues the AR finding (same observation); RISK-1 is POA&M-only (Django panel)
rk2 = next(r for r in risks.values() if "Engineers" in r["title"])
rk1 = next(r for r in risks.values() if r is not rk2)
sca = rk1["characterizations"][0]["facets"][0]["system"]   # https://ifa.gov/division/ociso/sca
bundle.add("objects/finding/goodread-risk-2.json",
           {"id": f"{NS}/finding/goodread-risk-2", "version": V_POAM, "lifecycle": "active",
            "title": finding_src.get("title", rk2["title"]),
            "assessment-ref": ASSESS, "requirement-ref": REQ_AC61,
            "state": "in-remediation",
            "actions": actions_of(rk2),
            "facets": {F_RISK: {**risk_facet(rk2), "target-objective-id": target_obj,
                                "implementation-statement-uuid": finding_src.get("implementation-statement-uuid")}}})
bundle.add("objects/finding/goodread-risk-1.json",
           {"id": f"{NS}/finding/goodread-risk-1", "version": V_POAM, "lifecycle": "active",
            "title": rk1.get("title", ""),
            "assessment-ref": ASSESS, "requirement-ref": REQ_AC61,
            "state": "in-remediation",
            "actions": actions_of(rk1),
            "deviations": [{"type": "risk-adjustment", "state": "approved",
                            "rationale": pua_scan(rk1.get("mitigating-factors", [{}])[0].get("description",
                                          "Risk accepted per POA&M deviation approval.")),
                            "approver-ref": sca,
                            "opened": (POAM.get("observations", [{}])[0].get("collected", "2023-05-19"))[:10],
                            "refs": [f"{NS}/evidence/obs-{POAM['observations'][0]['uuid'][:8]}"]}],
            "facets": {F_RISK: risk_facet(rk1)}})

# ================= 6. Attestation (the ATO as attestation) =================
ato_subjects = [{"id": o["id"], "semantic-digest": semantic_digest(o)}
                for rel, o in sorted(bundle.objects.items())
                if o["id"] in (COMP_SYS, IMPL_SYS, REQ_AC61)]
mini_manifest = json.dumps(ato_subjects, separators=(",", ":"), ensure_ascii=False).encode()
import hashlib
bundle.add("objects/attestation/ifa-ato.json",
           {"id": f"{NS}/attestation/ifa-ato", "version": V_SSP, "lifecycle": "active",
            "title": f"IFA ATO for {sc['system-name']} (modeled from SSP date-authorized)",
            "subject-semantic-digests": ato_subjects,
            "content-manifest-digest": "sha256:" + hashlib.sha256(mini_manifest).hexdigest(),
            "signer": f"{NS}/party/authorizing-official",
            "timestamp": f"{sc.get('date-authorized', '2025-05-19')}T00:00:00Z"})

# ---------- stubs + write ----------
# carried Requirements bring their facet pins along (#17 fail-closed:
# a bundle pins every facet schema its objects use)
bundle.stub("sp800-53-narrative-stub.json", "https://ns.nist.gov/sp800-53/facet/narrative", [],
            {"guidance": {"type": "array"}})
bundle.stub("sp800-53a-stub.json", "https://ns.nist.gov/sp800-53/facet/sp800-53a", [],
            {"objectives": {"type": "array"}, "methods": {"type": "array"}})
bundle.stub("sp800-53-odp-stub.json", "https://ns.nist.gov/sp800-53/facet/odp", [],
            {"params": {"type": "object"}})
bundle.stub("goodread-system-stub.json", F_SYS.split("@")[0], [],
            {"system-ids": {"type": "array"}, "description": {"type": "object"},
             "status": {"type": "string"}, "sensitivity": {"type": "string"},
             "date-authorized": {"type": "string"}, "impact": {"type": "object"},
             "boundary": {"type": "object"}, "network-architecture": {"type": "object"},
             "data-flow": {"type": "object"}, "users": {"type": "array"},
             "inventory-items": {"type": "array"}, "customer-responsibilities": {"type": "array"}})
bundle.stub("goodread-observations-stub.json", F_OBS.split("@")[0], [], {"observations": {"type": "array"}})
bundle.stub("goodread-risk-stub.json", F_RISK.split("@")[0], [],
            {"risk-status": {"type": "string"}, "deadline": {"type": "string"},
             "statement": {"type": "object"}, "characterizations": {"type": "array"},
             "mitigating-factors": {"type": "array"}, "target-objective-id": {"type": "string"},
             "implementation-statement-uuid": {"type": "string"}})
bundle.stub("goodread-ap-stub.json", F_AP.split("@")[0], [], {"activities": {"type": "array"}})
bundle.stub("goodread-protocols-stub.json", F_PROTO.split("@")[0], [], {"protocols": {"type": "array"}})
bundle.write({"source": "OSCAL IFA GoodRead example set (SSP 1.1.1, AP, AR, POA&M) + leveraged/"
                        "leveraging SSP pair + component-definition example (usnistgov/oscal-content)",
              "source-note": "FICTIONAL example content by NIST; converted as the gate-3 lifecycle corpus",
              "source-oscal-version": SSP["metadata"]["oscal-version"],
              "converter": "convert_ifa.py v0.1",
              "carried-requirements": carried,
              "attestation-note": "content-manifest-digest = sha256 over the JSON array of "
                                  "{id, semantic-digest} subject entries (deterministic mini-manifest)"})

# ---------- coverage ----------
RULES = [
 (r"^(ssp|ap|ar|poam|lev|lvg|cdef)\.[a-z-]+\.(uuid$|metadata\.|import-profile|import-ssp|import-ap|back-matter\.)", "L1",
  "bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports)"),
 (r"^ssp\.system-security-plan\.system-characteristics\.", "L1",
  "system Component: authorizations[] (date-authorized -> the D5 anchor + Attestation) + system@1 facet "
  "(ids, status, sensitivity, FIPS-199 impact, boundary/network/data-flow, language-tagged)"),
 (r"^ssp\.system-security-plan\.system-implementation\.users\[\]\.", "L2", "system@1 facet users[]"),
 (r"^ssp\.system-security-plan\.system-implementation\.inventory-items\[\]\.", "L2",
  "system@1 facet inventory-items[] (asset props carried verbatim)"),
 (r"^ssp\.system-security-plan\.system-implementation\.components\[\]\.", "L1",
  "Component (kind system) id/title/status"),
 (r"^ssp\.system-security-plan\.control-implementation\.", "L1",
  "Implementation: requirement-ref = minted AC-6.1 (in-bundle copy), by-component -> capability + "
  "satisfied-by, set-parameters -> parameter-bindings (verified against the declared ODPs), "
  "implementation-status -> status"),
 (r"^ap\.assessment-plan\.(local-definitions|tasks|assessment-subjects|reviewed-controls)", "L2",
  "Assessment.method payload (assessment-plan@1): activities/steps/tasks/subjects/reviewed-controls"),
 (r"^ar\.assessment-results\.results\[\]\.(uuid|title|description|start|end)$", "L1",
  "Assessment id/title/time"),
 (r"^ar\.assessment-results\.results\[\]\.reviewed-controls\.", "L1", "Assessment subject-refs"),
 (r"^ar\.assessment-results\.results\[\]\.observations\[\]\.", "L1",
  "observations@1 facet + landmark evidence URIs (methods/types/collected/expires carried)"),
 (r"^ar\.assessment-results\.results\[\]\.findings\[\]\.", "L1",
  "Finding: target.status -> Assessment result + Finding state; target-id (53A objective) + "
  "implementation-statement-uuid -> risk@1 facet"),
 (r"^ar\.assessment-results\.results\[\]\.(risks|local-definitions)", "L1",
  "risk content consolidated with the POA&M risks (same risk graph, later state)"),
 (r"^ar\.assessment-results\.local-definitions\.", "L2",
  "Assessment.method payload (activities duplicated from AP; carried once)"),
 (r"^poam\.plan-of-action-and-milestones\.(uuid$|system-id)", "L1", "provenance / system id (system@1)"),
 (r"^poam\.plan-of-action-and-milestones\.observations\[\]\.", "L1",
  "observations@1 facet + landmark evidence URIs (deduped against AR by uuid)"),
 (r"^poam\.plan-of-action-and-milestones\.risks\[\]\.(uuid|title|description|statement|status|deadline)$", "L1",
  "Finding id/title/state (deviation-approved -> approved Deviation; open+remediation -> in-remediation); "
  "deadline -> risk@1"),
 (r"^poam\.plan-of-action-and-milestones\.risks\[\]\.characterizations\[\]\.", "L2",
  "risk@1 facet characterizations (likelihood/impact, origin actors)"),
 (r"^poam\.plan-of-action-and-milestones\.risks\[\]\.remediations\[\]\.", "L1",
  "Finding.actions[] (task title/status; within-date-range.end -> due)"),
 (r"^poam\.plan-of-action-and-milestones\.risks\[\]\.(mitigating-factors|related-observations)\[?\]?\.", "L1",
  "Deviation rationale (RISK-1) / risk@1 mitigating-factors; observation links -> evidence refs"),
 (r"^poam\.plan-of-action-and-milestones\.poam-items\[\]\.", "L1",
  "poam-item titles ride the Finding titles; related-risks/observations resolved by uuid"),
 (r"^(lev|lvg)\.system-security-plan\.system-characteristics\.", "L1",
  "provider/consumer Components: system@1 facet (description, FIPS-199 carried)"),
 (r"^(lev|lvg)\.system-security-plan\.system-implementation\.components\[\]\.", "L1",
  "Components (kind mapped: appliance->hardware, application->software)"),
 (r"^lvg\.system-security-plan\.system-implementation\.(users|leveraged-authorizations)\[\]\.", "L1",
  "leveraged-authorizations -> provider Component authorizations[] (the basis-ref anchor); users -> system@1"),
 (r"^lev\.system-security-plan\.system-implementation\.users\[\]\.", "L2", "system@1 facet users[]"),
 (r"^lev\.system-security-plan\.control-implementation\.", "L1",
  "provider Implementation: export.provided -> capabilities (consumer-inheritable), "
  "export.responsibilities -> system@1 customer-responsibilities; statement ids respelled _stmt.->smt. (counted)"),
 (r"^lvg\.system-security-plan\.control-implementation\.", "L1",
  "consumer Implementation: inherited -> satisfied-by inherited-from{component, basis-ref} (D5), "
  "satisfied -> consumer capability; responsibility shared"),
 (r"^cdef\.component-definition\.(uuid$|metadata\.)", "L1", "bundle manifest / L0 provenance"),
 (r"^cdef\.component-definition\.components\[\]\.protocols\[\]\.", "L2", "protocols@1 facet"),
 (r"^cdef\.component-definition\.components\[\]\.responsible-roles\[\]\.", "L1",
  "landmark party URIs (#16: parties stay landmark; roles ride provenance)"),
 (r"^cdef\.component-definition\.components\[\]\.control-implementations\[\]\.", "L1",
  "capabilities with requirement-ref (landmark - the component asserts support, no system binds it)"),
 (r"^cdef\.component-definition\.components\[\]\.(uuid|type|title|description|purpose)$", "L1",
  "Component (kind mapped) id/title"),
]
rows, unmapped = coverage(paths, RULES)

types = collections.Counter(rel.split("/")[1] for rel in bundle.objects)
j = report(
    os.path.join(OUTDIR, "ifa-coverage-report.md"),
    os.path.join(OUTDIR, "ifa-coverage-report.json"),
    "IFA GoodRead lifecycle set -> Semantic Core: Coverage Report (computed)",
    f"Source: **OSCAL IFA GoodRead example set** (SSP v{V_SSP} + AP + AR + POA&M) + "
    f"leveraged/leveraging SSP pair + component-definition example (usnistgov/oscal-content; "
    f"FICTIONAL example content by NIST). Census: `drafts/gate-3-census.md` §4.",
    [f"- Objects emitted: " + ", ".join(f"{v} {k}" for k, v in sorted(types.items())) +
     f" - the five lifecycle types at document scale, manifest with both digests.",
     f"- Carried Requirements (closure): {', '.join(carried)} - byte-identical copies from the "
     f"US.SP800-53 bundle; an authorization package carries its baseline."],
    [f"- **SSP -> Component + Implementation**: by-component -> capability + satisfied-by; "
     f"5 set-parameters bind the REAL minted AC-6.1 ODPs (unresolved bindings: {unresolved_bind or 'none'}).",
     f"- **date-authorized -> Component.authorizations + Attestation**: the ATO modeled as an "
     f"attestation over {{system Component, Implementation, AC-6.1}} semantic digests; unsigned "
     f"(envelope-ref absent) - signature verification is gate-4 (backlog #24).",
     f"- **Leveraged/leveraging pair -> D5 inheritance**: consumer Implementation satisfied-by "
     f"inherited-from{{csp-iaas, {AUTH_CSP}}} - basis-ref names the provider Component's authorization "
     f"(edge-local closure enforced by the validator); provider export.provided -> capabilities, "
     f"export.responsibilities -> customer-responsibilities.",
     f"- **AR + AP -> one Assessment**: AP activities/steps ride Assessment.method "
     f"(assessment-plan@1 payload); result not-satisfied from the finding target; observations "
     f"(AR + POA&M, deduped by uuid) -> observations@1 facet + landmark evidence URIs.",
     f"- **POA&M risks -> Findings**: RISK-2 (open + planned remediation) -> state in-remediation with "
     f"actions[] (due = within-date-range.end); RISK-1 (status deviation-approved) -> approved "
     f"`risk-adjustment` Deviation (rationale = mitigating factor, approver = the SCA division URI); "
     f"characterizations (likelihood/impact) -> risk@1 facet.",
     f"- **Finding target `{target_obj}`** is a 53A OBJECTIVE id - it addresses into the sp800-53a@1 "
     f"facet of the carried AC-6.1 (kept in risk@1.target-objective-id; kernel statement-ref stays "
     f"statement-scoped).",
     f"- **Parties stay landmark** (#16, D22 0-of-3): performer/signer/approver are minted party URIs, "
     f"no party objects.",
     f"- **Payload free text language-tagged**: " + ", ".join(f"{k} x{v}" for k, v in sorted(lang_wraps.items())) + "."],
    [f"- **Statement-id respelling x{n_stmt_respell}** (source finding): the SSP pair writes "
     f"`ac-2_stmt.a` where the Rev 5 catalog writes `ac-2_smt.a` - same publisher, two spellings of "
     f"the same address; normalized to the catalog form. REPORTED upstream.",
     f"- **PUA codepoints x{n_pua}** (source finding): U+E0xx private-use characters embedded in IFA "
     f"SSP prose (ligature artifacts, e.g. 'so\\ue002ware') - carried verbatim, never patched. "
     f"REPORTED upstream.",
     f"- **Placeholder uuids x{uuid_placeholder}**: every export.provided/responsibility uuid in the "
     f"leveraged pair is 11111111-... - the provided-uuid dereference is degenerate in source; "
     f"inheritance wired via the authorization anchor instead.",
     f"- **Unresolved parameter bindings**: {unresolved_bind or 'none'}" +
     (f" - `ac-2_prm_1` is a Rev-5.1-era param id; Rev 5.2.0 declares the _odp layer instead "
      f"(the binding is carried verbatim; a resolver follows the odp@1 aggregates map)." if unresolved_bind else "."),
     f"- **Kind mapping**: " + (", ".join(f"{k} x{v}" for k, v in kind_mapped.items()) or "none") +
     f" (OSCAL free-text component types vs. the kernel's closed componentKind).",
     *(f"- {n}" for n in findings_notes)],
    rows, unmapped,
    {"objects-emitted": dict(types), "carried-requirements": carried,
     "stmt-respell": n_stmt_respell, "pua-codepoints": n_pua,
     "placeholder-uuids": uuid_placeholder, "unresolved-bindings": unresolved_bind,
     "lang-wraps": dict(lang_wraps)})
print(f"objects: {sum(types.values())} {dict(types)}")
print(f"leaves: {j['totals']['leaf-values']:,}  mapped: {j['totals']['mapped']:,}  "
      f"UNMAPPED: {j['totals']['unmapped']}")
print(f"respell: {n_stmt_respell}  pua: {n_pua}  placeholder-uuids: {uuid_placeholder}  "
      f"unresolved-bindings: {unresolved_bind}")
if unmapped:
    for p, n in unmapped[:40]: print("  UNMAPPED", p, "x", n)
