#!/usr/bin/env python3
"""IFA GoodRead lifecycle set (SSP + AP + AR + POA&M) + leveraged/leveraging
SSP pair + component-definition example -> Semantic Core lifecycle bundle.
Census: drafts/gate-3-census.md §4 (2026-07-22). The five lifecycle types at
document scale: Components (with authorizations - the D5 anchor),
Implementations (param bindings against the REAL minted AC-6.1 ODPs;
inheritance via inherited-from{component-ref, basis-ref}), Assessment (AR
ConMon result, AP as method payload, observations as facet + landmark
evidence URIs), Findings (POA&M risks -> states/actions/deviations), and an
Attestation modeling the SSP's date-authorized ATO.
CP-RISK-1 re-run (kernel 2.0.0, 2026-11-10): the POA&M risks are also
emitted as Risk objects - the first corpus measurement of the tenth type.
What OSCAL cannot give the Risk shape is REPORTED, never filled in: no
owner field (derived from the imported SSP, declared), no single level
(likelihood + impact only - `assessed`/`treated` are unreachable), no dated
acceptance (`retain` is unreachable). Findings point at their Risk with
`risk-refs`; the risk@1 framework facet is retired. Referenced Requirements
(AC-6.1, AC-2) ride along as byte-identical copies from the US.SP800-53
bundle - an authorization package carries its baseline. Coverage target: 0.
Depends on: convert_nist.py output (run first)."""
import json, os, re, collections
from oscal_conv_lib import make_T, slug, Bundle, inventory, coverage, report, semantic_digest, global_occurrence, Ledger, props_by_name

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SRCDIR = os.path.join(ROOT, "sources", "nist")
OUTDIR = os.path.join(ROOT, "converted_examples", "US.IFA-GoodRead")
NISTB = os.path.join(ROOT, "converted_examples", "US.SP800-53", "sp800-53-core-bundle")
NS = "https://ifa.gov/goodread"          # the source's own (fictional) agency domain
F_SYS = f"{NS}/facet/system@1"
F_OBS = f"{NS}/facet/observations@1"
F_RISKA = f"{NS}/facet/risk-analysis@1"    # L2 holding pen for the parked stdlib risk-analysis@1 (App. D)
F_FTGT = f"{NS}/facet/finding-target@1"    # the Finding-side residue of the retired risk@1 facet
F_AP = f"{NS}/facet/assessment-plan@1"
F_PROTO = f"{NS}/facet/protocols@1"
F_COMP = f"{NS}/facet/component@1"        # what OSCAL says of a component and the kernel has no field for
F_IMPL = f"{NS}/facet/implementation@1"   # the narrative of a control implementation, by statement

lang_wraps = collections.Counter()
T = make_T("en", lang_wraps)

# The conversion ledger (oscal_conv_lib.Ledger): every scalar of the seven
# source documents carries its origin from here on. A value handed on
# unchanged is recorded as a copy when the bundle is accounted for at the
# end; a value this script computes is stated where it is computed, with
# D(rule, function, inputs...), so that the rule can be applied again and
# compared. What reaches no destination and has no declared reason is listed
# as unaccounted. Nothing here changes what is written: the bundle is byte
# for byte the one the script wrote before the ledger existed.
led = Ledger()
D = led.derive

SOURCE_FILES = []        # (file name, document) in the order loaded, for the manifest's provenance
def load(tag, fn, key):
    doc = json.load(open(os.path.join(SRCDIR, fn), encoding="utf-8"))
    tracked = led.source(tag, {key: doc[key]})[key]
    SOURCE_FILES.append((fn, tracked))
    return tracked

SSP = load("ssp", "ifa_ssp.json", "system-security-plan")
AP = load("ap", "ifa_assessment-plan.json", "assessment-plan")
AR = load("ar", "ifa_assessment-results.json", "assessment-results")
POAM = load("poam", "ifa_plan-of-action-and-milestones.json", "plan-of-action-and-milestones")
LEV = load("lev", "oscal_leveraged-example_ssp.json", "system-security-plan")
LVG = load("lvg", "oscal_leveraging-example_ssp.json", "system-security-plan")
CDEF = load("cdef", "example-component-definition.json", "component-definition")

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
def _stmt_norm(sid, cid):
    """pure: the ledger applies it again when it checks the destination"""
    s = sid
    if s.startswith(cid + "_"): s = s[len(cid) + 1:]
    if s.startswith("stmt"): s = "smt" + s[4:]
    return s
def stmt_norm(sid, cid):
    global n_stmt_respell
    if not sid: return None
    s = sid[len(cid) + 1:] if sid.startswith(cid + "_") else sid
    if s.startswith("stmt"): n_stmt_respell += 1
    return D("statement id without the control prefix, in the catalogue's spelling (stmt -> smt)", _stmt_norm, sid, cid)

# PUA codepoints in source text (the soware defect)
n_pua = 0
def pua_scan(v):
    global n_pua
    if isinstance(v, str):
        n_pua += sum(1 for ch in v if 0xE000 <= ord(ch) <= 0xF8FF)
    return v

# Two rules the script applies in several places, stated once. Each is a
# plain function of the source value, so the ledger can apply it again.
def kind_of(component):
    """Component.kind from the OSCAL component `type` (KIND_MAP, defined below)."""
    return D("component kind from the OSCAL component type (KIND_MAP)", lambda t: KIND_MAP[t], component["type"])
def req_of(control_id):
    """The Requirement a lower-case OSCAL control id names in the carried SP 800-53 bundle."""
    return D("requirement URI from the control id",
             lambda c: f"https://ns.nist.gov/sp800-53/req/{c.upper()}", control_id)
KIND_MAP = {"this-system": "system", "system": "system", "software": "software",
            "application": "software", "appliance": "hardware", "service": "service"}

# ---------- parties (landmark URIs by #16 - no party objects) ----------
def party_uri(doc, uuid, default_slug):
    for p in doc["metadata"].get("parties", []) or []:
        if p["uuid"] == uuid:
            # three source values meet here: the reference, the uuid of the party
            # it names, and that party's name. The rule fails if the two uuids differ.
            return D("party reference resolved by uuid; landmark URI from the party's name",
                     lambda ref, pid, name: f"{NS}/party/{slug(name)}" if ref == pid else None,
                     uuid, p["uuid"], p.get("name", default_slug))
    return f"{NS}/party/{default_slug}"

# ---------- roles: per Component and for the whole scope ----------
# OSCAL assigns roles at every level: to the document, to a component, to a
# statement, an exported capability, an activity, a task, a user. The bundle
# carries them at TWO levels only (author decision 2026-11-13): on the
# Component, in component@1, and for the whole scope, in system@1 of the
# system Component and in the method payload of the Assessment. An
# assignment made below those levels is rolled up to the Component it sits
# under, or to the scope where it has none: if that role and party is there
# already the lower occurrence is linked to it (Ledger.same), else it joins
# the list. One entry per role: {role, parties: [landmark URI, ...]}.
# A party the source defines without a name, or does not define, cannot be
# named by a landmark URI: the role is carried without it, the reference is
# declared, and the gap is counted as a finding about the source.
party_gaps = collections.Counter()
ROLE_LISTS = []        # (the facet or payload that will hold the list, the list): attached when every roll-up is done
def role_list(holder):
    roles = []; ROLE_LISTS.append((holder, roles)); return roles
def party_ref(doc, ref):
    """-> the landmark URI of the party `ref` names in `doc`, or None."""
    party = next((p for p in doc["metadata"].get("parties", []) or [] if p["uuid"] == ref), None)
    if party is None or not party.get("name"):
        gap = "does not define" if party is None else "defines without a name"
        party_gaps[gap] += 1
        led.drop_value(ref, f"a reference to a party the source {gap}: no landmark URI can name it, "
                            f"so its role is carried without a party")
        return None
    return D("party reference resolved by uuid; landmark URI from the party's name",
             lambda r, pid, name: f"{NS}/party/{slug(name)}" if r == pid else None, ref, party["uuid"], party["name"])
def add_roles(roles, doc, assignments, where):
    """Adds OSCAL role assignments ({role-id, party-uuids?}) to a role list."""
    rule = f"a role assigned at {where}, carried once per Component or scope"
    for a in assignments or []:
        entry = next((e for e in roles if e["role"] == a["role-id"]), None)
        if entry is None:
            entry = {"role": a["role-id"]}; roles.append(entry)
        else:
            led.same(a["role-id"], entry["role"], rule)
        for ref in a.get("party-uuids", []) or []:
            uri = party_ref(doc, ref)
            if uri is None: continue
            kept = next((u for u in entry.get("parties", []) if u == uri), None)
            if kept is None: entry.setdefault("parties", []).append(uri)
            else: led.same(uri, kept, rule)
def component_facet(doc, comp, own_title=True):
    """component@1: what OSCAL says of a component and the kernel has no field
    for. -> (the facet, its role list). `own_title` is False where the
    Component's kernel title comes from elsewhere and this one would be lost."""
    f = {}
    if not own_title and comp.get("title") is not None: f["title"] = comp["title"]
    if comp.get("description") is not None: f["description"] = T(pua_scan(comp["description"]), "component")
    if comp.get("purpose") is not None: f["purpose"] = T(pua_scan(comp["purpose"]), "component")
    if comp.get("status", {}).get("state") is not None: f["status"] = comp["status"]["state"]
    props = props_by_name(comp.get("props"), led)
    if props: f["props"] = props
    roles = role_list(f)
    add_roles(roles, doc, comp.get("responsible-roles"), "the component")
    return f, roles

# ---------- the narrative of a control implementation ----------
def implementation_facet(doc, ir):
    """implementation@1: the texts an SSP writes about how one control is
    implemented, kept under the statement they belong to. An Implementation
    says THAT a requirement is met and by what; these say how, in the
    source's words: the remark on the control, per statement its remark and
    each component's response with what it exports, inherits and satisfies.
    (What is exported as a capability or as a customer responsibility has its
    kernel place and is not repeated here.) A key is written only where the
    source has the text."""
    text = lambda v: T(pua_scan(v), "implementation")
    f = {}
    if doc["control-implementation"].get("description") is not None:
        f["description"] = text(doc["control-implementation"]["description"])
    if ir.get("remarks") is not None: f["remarks"] = text(ir["remarks"])
    statements = []
    for st in ir.get("statements", []) or []:
        entry = {"statement": D("statement id without the control prefix, in the catalogue's spelling (stmt -> smt)",
                                _stmt_norm, st["statement-id"], ir["control-id"])}
        if st.get("remarks") is not None: entry["remarks"] = text(st["remarks"])
        responses = []
        for b in st.get("by-components", []) or []:
            r = {}
            if b.get("description") is not None: r["description"] = text(b["description"])
            if b.get("export", {}).get("description") is not None: r["export"] = text(b["export"]["description"])
            inherited = [text(x["description"]) for x in b.get("inherited", []) or [] if x.get("description") is not None]
            satisfied = [text(x["description"]) for x in b.get("satisfied", []) or [] if x.get("description") is not None]
            if inherited: r["inherited"] = inherited
            if satisfied: r["satisfied"] = satisfied
            responses.append(r)
        if responses: entry["responses"] = responses
        statements.append(entry)
    if statements: f["statements"] = statements
    return f

# ================= 1. the GoodRead system (SSP) =================
V_SSP = SSP["metadata"]["version"]
sc = SSP["system-characteristics"]
COMP_SYS = f"{NS}/component/system1234"
AUTH_ATO = "auth-ifa-ato"
def system_facet(doc):
    """The system@1 facet of one system security plan: what its
    system-characteristics say (ids, status, sensitivity, impact, boundary,
    the narratives) and its users with their privileges. One function for the
    main system, the leveraged and the leveraging one. Until 2026-11-13 only
    the main system got all of this, while the path map said the other two
    carried their FIPS-199 levels. A key is written only where the source has
    the value, so nothing is filled in."""
    sc, si, f = doc["system-characteristics"], doc["system-implementation"], {}
    text = lambda v: T(pua_scan(v), "system")
    def put(key, value, wrap=lambda v: v):
        if value is not None: f[key] = wrap(value)
    put("system-ids", sc.get("system-ids"))
    put("description", sc.get("description"), text)
    put("status", sc.get("status", {}).get("state"))
    put("sensitivity", sc.get("security-sensitivity-level"))
    put("date-authorized", sc.get("date-authorized"))
    f["impact"] = {"information-types": sc.get("system-information", {}).get("information-types", []),
                   "security-impact-level": sc.get("security-impact-level", {})}
    put("boundary", sc.get("authorization-boundary", {}).get("description"), text)
    put("network-architecture", sc.get("network-architecture", {}).get("description"), text)
    put("data-flow", sc.get("data-flow", {}).get("description"), text)
    put("remarks", sc.get("remarks"), text)
    users = []
    for u in si.get("users", []) or []:
        user = {}
        if u.get("title") is not None: user["title"] = u["title"]
        if u.get("description") is not None: user["description"] = pua_scan(u["description"])
        user["privileges"] = [{"title": a.get("title"), "functions": a.get("functions-performed", [])}
                              for a in u.get("authorized-privileges", []) or []]
        users.append(user)
    if users: f["users"] = users
    # `props` and `components` mean what they meant; the class of each prop
    # and the props of each implemented component stand beside them
    # (`component-props` has one entry per entry of `components`, in order)
    inventory = [{"description": pua_scan(i.get("description")),
                  "props": props_by_name(i.get("props"), led),       # a repeated name keeps every value
                  "prop-classes": props_by_name(i.get("props"), led, field="class"),
                  "components": [c["component-uuid"] for c in i.get("implemented-components", []) or []],
                  "component-props": [props_by_name(c.get("props"), led) for c in i.get("implemented-components", []) or []]}
                 for i in si.get("inventory-items", []) or []]
    if inventory: f["inventory-items"] = inventory
    return f

ssp_comp = SSP["system-implementation"]["components"][0]
sysf_ssp = system_facet(SSP)
compf_ssp, roles_ssp = component_facet(SSP, ssp_comp)
add_roles(role_list(sysf_ssp), SSP, SSP["metadata"].get("responsible-parties"), "the document")
add_roles(roles_ssp, SSP, [{"role-id": r} for u in SSP["system-implementation"].get("users", []) or []
                           for r in u.get("role-ids", []) or []], "a user")
comp_sys = {"id": COMP_SYS, "version": V_SSP, "label": sc["system-name"], "lifecycle": "active",
            "title": ssp_comp.get("title", sc["system-name"]), "kind": kind_of(ssp_comp),
            "capabilities": [],
            "authorizations": [{"id": AUTH_ATO,
                                "authority-ref": f"{NS}/party/authorizing-official",
                                "scope-label": D("ATO scope label: date authorized and sensitivity level",
                                                 lambda d, l: f"ATO {d} ({l})",
                                                 sc.get("date-authorized", "?"), sc.get("security-sensitivity-level", "?"))}],
            "facets": {F_SYS: sysf_ssp, F_COMP: compf_ssp}}

# implemented-requirement ac-6.1 -> capability + Implementation
ir = SSP["control-implementation"]["implemented-requirements"][0]
bc = ir["by-components"][0]
REQ_IR = req_of(ir["control-id"])        # the implemented requirement names its control: ac-6.1
assert REQ_IR == REQ_AC61, f"the SSP implements {ir['control-id']}, the bundle carries {REQ_AC61}"
comp_sys["capabilities"].append({"id": "cap-ac-6.1", "requirement-ref": REQ_IR,
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
            "component-ref": COMP_SYS, "requirement-ref": REQ_IR,
            "responsibility": "provider",
            "satisfied-by": [{"capability-ref": "cap-ac-6.1"}],
            "parameter-bindings": pbind,
            "status": bc.get("implementation-status", {}).get("state", "implemented"),
            "evidence-refs": [D("document reference from the SSP's uuid", lambda u: f"{NS}/doc/ssp-{u}", SSP["uuid"])],
            "facets": {F_IMPL: implementation_facet(SSP, ir)}})

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
lev_sys_comp = next(c for c in LEV["system-implementation"]["components"] if c["type"] == "this-system")
app_comp = next(c for c in LEV["system-implementation"]["components"] if c["type"] != "this-system")
lvg_sys_comp = next(c for c in LVG["system-implementation"]["components"] if c["type"] == "this-system")
appl = next(c for c in LVG["system-implementation"]["components"] if c["type"] == "appliance")
compf_iaas, roles_iaas = component_facet(LEV, lev_sys_comp, own_title=False)     # its title is the document's
compf_app, roles_app = component_facet(LEV, app_comp)
compf_saas, roles_saas = component_facet(LVG, lvg_sys_comp, own_title=False)
compf_appl, roles_appl = component_facet(LVG, appl)
for doc, roles in ((LEV, roles_iaas), (LVG, roles_saas)):
    add_roles(roles, doc, [{"role-id": r} for u in doc["system-implementation"].get("users", []) or []
                           for r in u.get("role-ids", []) or []], "a user")
# roles below the component: a response by a component, what it exports, what it satisfies.
# Each goes to the Component the response is by; the leveraging plan's own entries for the
# leveraged system and application are not Components here, so theirs go to the leveraging system.
for doc, fallback, lookup in ((LEV, roles_iaas, {lev_sys_comp["uuid"]: roles_iaas, app_comp["uuid"]: roles_app}),
                              (LVG, roles_saas, {lvg_sys_comp["uuid"]: roles_saas, appl["uuid"]: roles_appl})):
    for st in doc["control-implementation"]["implemented-requirements"][0].get("statements", []) or []:
        for b in st.get("by-components", []) or []:
            roles = lookup.get(b.get("component-uuid"), fallback)
            add_roles(roles, doc, b.get("responsible-roles"), "a response by the component")
            for pv in b.get("export", {}).get("provided", []) or []:
                add_roles(roles, doc, pv.get("responsible-roles"), "an exported capability")
            for rs in b.get("export", {}).get("responsibilities", []) or []:
                add_roles(roles, doc, rs.get("responsible-roles"), "an exported responsibility")
            for sa in b.get("satisfied", []) or []:
                add_roles(roles, doc, sa.get("responsible-roles"), "a satisfied responsibility")
if la.get("party-uuid") is not None: party_ref(LVG, la["party-uuid"])     # the authorization's party: named or declared
# The leveraging plan lists the leveraged system and its application as components of its
# own. The provider's Components, converted from the leveraged plan, stand for them: a value
# that equals the provider's is linked to it, the rest is declared.
for stand_in in LVG["system-implementation"]["components"]:
    inherited = props_by_name(stand_in.get("props")).get("inherited-uuid")
    provider = next((c for c in LEV["system-implementation"]["components"] if c["uuid"] == inherited), None)
    if provider is None: continue
    if stand_in.get("status", {}).get("state") == provider.get("status", {}).get("state"):
        led.same(stand_in["status"]["state"], provider["status"]["state"],
                 "the leveraging plan's entry for a leveraged component; the provider's Component stands for it")
    led.drop_value(stand_in, "the leveraging plan's own entry for a component of the leveraged system; the provider's "
                             "Component, converted from the leveraged plan, stands for it")
bundle.add("objects/component/csp-iaas.json",
           {"id": COMP_IAAS, "version": V_LEV, "label": LEV["system-characteristics"]["system-name"],
            "lifecycle": "active", "title": LEV["metadata"]["title"],
            "kind": kind_of(lev_sys_comp),
            "members": [{"component-ref": COMP_APP, "context": "application"}],
            "capabilities": lev_caps,
            "authorizations": [{"id": AUTH_CSP,
                                "authority-ref": f"{NS}/party/csp-authorizing-official",
                                "scope-label": D("leveraged authorization scope label: its title and date",
                                                 lambda t, d: f"{t} ({d})",
                                                 la.get("title", "CSP IaaS leveraged authorization"),
                                                 la.get("date-authorized", "?"))}],
            "facets": {F_SYS: {**system_facet(LEV), "customer-responsibilities": lev_resp}, F_COMP: compf_iaas}})
bundle.add("objects/component/csp-application.json",
           {"id": COMP_APP, "version": V_LEV, "label": app_comp.get("title", "Application"),
            "lifecycle": "active", "title": app_comp.get("title", "Application"), "kind": kind_of(app_comp),
            "facets": {F_COMP: compf_app}})
kind_mapped = collections.Counter()
kind_mapped["appliance->hardware"] += 1
appl_title = D("title without the decoration asterisks", lambda t: t.strip(" *"), appl.get("title", ""))
bundle.add("objects/component/access-control-appliance.json",
           {"id": COMP_APPL, "version": V_LVG, "label": appl_title,
            "lifecycle": "active", "title": appl_title,
            "kind": kind_of(appl),
            "capabilities": [{"id": "cap-consumer-ac-2a", "requirement-ref": REQ_AC2,
                              "description": pua_scan(next((sa.get("description", "")
                                  for st in LVG["control-implementation"]["implemented-requirements"][0].get("statements", [])
                                  for b in st.get("by-components", []) for sa in b.get("satisfied", []) or []), ""))}],
            "facets": {F_COMP: compf_appl}})
bundle.add("objects/component/saas.json",
           {"id": COMP_SAAS, "version": V_LVG,
            "label": LVG["system-characteristics"]["system-name"], "lifecycle": "active",
            "title": LVG["metadata"]["title"],
            "kind": kind_of(lvg_sys_comp),
            "members": [{"component-ref": COMP_IAAS, "context": "leveraged system"},
                        {"component-ref": COMP_APPL, "context": "internal appliance"}],
            "facets": {F_SYS: system_facet(LVG), F_COMP: compf_saas}})
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
                             {"capability-ref": f"{COMP_APPL}#cap-consumer-ac-2a"}],
            "parameter-bindings": lvg_bind,
            "status": "implemented",
            "evidence-refs": [D("document reference from the SSP's uuid", lambda u: f"{NS}/doc/ssp-{u}", LVG["uuid"])],
            "facets": {F_IMPL: implementation_facet(LVG, lvg_ir)}})
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
            "evidence-refs": [D("document reference from the SSP's uuid", lambda u: f"{NS}/doc/ssp-{u}", LEV["uuid"])],
            "facets": {F_IMPL: implementation_facet(LEV, lev_ir)}})

# ================= 3. component-definition example =================
# The mapping is the one of the pack builder's OSCAL import
# (one-page-apps/jascon-pack-builder.html, importOscal; CP-ADVICE-1 section 9):
# one capability per implemented requirement; its statements become
# `statement-ids` in the catalogue's spelling and their texts follow the
# requirement's text, each under its clause id; `set-parameters` become
# `parameter-bindings` under the name the catalogue declares; OSCAL's
# `{{ insert: param, x }}` becomes `{param:<that name>}`. The catalogue is
# the SP 800-53 conversion in this repository. Until 2026-11-13 this section
# read the control id and the description and nothing below them, while the
# path map counted the rest as carried (backlog #64).
INSERT = re.compile(r"\{\{\s*insert:\s*param,\s*([^}\s]+)\s*\}\}")
def nist_req(control_id):
    """The Requirement the SP 800-53 conversion holds for an OSCAL control id, or None."""
    p = os.path.join(NISTB, "objects", "req", slug(control_id) + ".json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None
def param_name(req, pid):
    """A parameter name as the catalogue declares it: the id itself, or the
    declared name whose alt-identifiers list it (the Rev 4 `_prm_` ids)."""
    if not req: return pid
    names = [p["name"] for st in req.get("statements", []) for p in st.get("parameters", [])]
    if pid in names: return pid
    def walk(v):
        if isinstance(v, dict):
            for k, x in v.items():
                if k in names and isinstance(x, dict) and pid in (x.get("alt-identifiers") or []): return k
                hit = walk(x)
                if hit: return hit
        elif isinstance(v, list):
            for x in v:
                hit = walk(x)
                if hit: return hit
        return None
    return walk(req.get("facets")) or pid
def capability_text(req):
    """-> the pure rule that writes a capability's text from the implemented
    requirement's description, its control id, and (statement-id, text) pairs."""
    unmark = lambda t: INSERT.sub(lambda m: "{param:%s}" % param_name(req, m.group(1)), t)
    def text(description, control_id, *pairs):
        parts = [unmark(description)] if description else []
        parts += [f"{_stmt_norm(sid, control_id)}: {unmark(d)}" for sid, d in zip(pairs[0::2], pairs[1::2]) if d]
        return "\n\n".join(parts)
    return text
V_CDEF = CDEF["metadata"]["version"]
cdef_resources = {r["uuid"]: r for r in CDEF.get("back-matter", {}).get("resources", []) or []}
cdef_stats = collections.Counter()
for c in CDEF.get("components", []) or []:
    caps, control_impls = [], []
    for ci in c.get("control-implementations", []) or []:
        entry = {"description": T(pua_scan(ci.get("description", "")), "component")}
        # `source` is a link into the back-matter; what it names is carried, by its JSON link
        res = cdef_resources.get(ci.get("source", "")[1:]) if ci.get("source", "").startswith("#") else None
        if res and res.get("rlinks"):
            href = next((l["href"] for l in res["rlinks"] if l["href"].lower().endswith(".json")), res["rlinks"][0]["href"])
            entry["source"] = D("control-implementation source: the back-matter resource it names, by its JSON link",
                                lambda ref, rid, h: h if ref == "#" + rid else None, ci["source"], res["uuid"], href)
            if not re.search(r"800-53", href):
                note(f"control implementation of {c.get('title')} names {href}; its requirement-refs are minted in the "
                     f"SP 800-53 namespace all the same")
        elif ci.get("source"):
            entry["source"] = ci["source"]
        control_impls.append(entry)
        if ci.get("set-parameters"):
            note(f"{len(ci['set-parameters'])} set-parameters on a whole control implementation are not placed "
                 f"(the pack builder puts them where the catalogue declares the parameter)")
        for cir in ci.get("implemented-requirements", []) or []:
            cid = cir.get("control-id", "")
            req = nist_req(cid)
            statements = [st for st in cir.get("statements", []) or [] if st.get("statement-id")]
            sids = []
            for st in statements:
                sid = stmt_norm(st["statement-id"], cid)
                if sid not in sids: sids.append(sid)
            description = cir.get("description", "")
            rule = capability_text(req)
            pairs = [x for st in statements for x in (st["statement-id"], st.get("description", ""))]
            if rule(description, cid, *pairs) != description:      # something is joined or respelled: say so
                description = D("capability text: the requirement's description, then each statement's text under "
                                "its clause id; OSCAL parameter insertions respelled {param:<catalogue name>}",
                                rule, description, cid, *pairs)
            bindings = {}
            for sp in cir.get("set-parameters", []) or []:
                pid, values = sp["param-id"], sp.get("values", [])
                name = pid if param_name(req, pid) == pid else \
                    D("parameter name as the catalogue declares it (the OSCAL param-id is one of its alt-identifiers)",
                      lambda p, req=req: param_name(req, p), pid)
                decl = next((p for st in (req or {}).get("statements", []) for p in st.get("parameters", [])
                             if p["name"] == name), None)
                many = bool(decl and decl.get("type") == "choice" and decl.get("cardinality") == "many")
                bindings[name] = values if many or len(values) != 1 else values[0]
                cdef_stats["bindings"] += 1
                if req is None or decl is None: cdef_stats["bindings the catalogue does not declare"] += 1
            cap = {"id": D("capability id from the control id", lambda c: f"cap-{slug(c)}", cir.get("control-id", "x")),
                   "requirement-ref": req_of(cid)}
            if sids: cap["statement-ids"] = sids
            cap["description"] = pua_scan(description)
            if bindings: cap["parameter-bindings"] = bindings
            caps.append(cap)
            cdef_stats["clauses"] += len(sids)
    kind = D("component kind from the OSCAL component type (KIND_MAP)", lambda t: KIND_MAP.get(t, "software"),
             c.get("type", "software"))
    obj = {"id": D("component id from its title", lambda t: f"{NS}/component/{slug(t)}", c.get("title", "component")),
           "version": V_CDEF, "label": c.get("title", ""), "lifecycle": "active",
           "title": c.get("title", ""), "kind": kind}
    if caps: obj["capabilities"] = caps
    protos = [{"name": p.get("name"), "title": p.get("title"),
               "port-ranges": p.get("port-ranges", [])} for p in c.get("protocols", []) or []]
    if protos: obj.setdefault("facets", {})[F_PROTO] = {"protocols": protos}
    compf, roles = component_facet(CDEF, c)
    for ci in c.get("control-implementations", []) or []:
        for cir in ci.get("implemented-requirements", []) or []:
            for st in cir.get("statements", []) or []:
                add_roles(roles, CDEF, st.get("responsible-roles"), "a statement")
    if control_impls: compf["control-implementations"] = control_impls
    obj.setdefault("facets", {})[F_COMP] = compf
    bundle.add(f"objects/component/{slug(c.get('title', 'component'))}.json", obj)

# ================= 4. Assessment (AR result; AP as method) =================
V_AR = AR["metadata"]["version"]
res = AR["results"][0]
ASSESS = f"{NS}/assessment/conmon-2023-06"
observations = []
for src, tag in ((res.get("observations", []), "ar"), (POAM.get("observations", []), "poam")):
    for o in src:
        observations.append({"id": D("evidence URI from the first eight characters of the observation uuid",
                                     lambda u: f"{NS}/evidence/obs-{u[:8]}", o["uuid"]),
                             "title": o.get("title"), "description": T(pua_scan(o.get("description", "")), "observation"),
                             "methods": o.get("methods", []), "collected": o.get("collected"),
                             **({"expires": o["expires"]} if o.get("expires") else {}),
                             "source-doc": tag})
# dedupe by uuid (the engineer-role observation appears in both AR and POA&M)
seen, obs_dedup = {}, []
for o in observations:
    if o["id"] in seen:
        note(f"observation carried in both AR and POA&M (deduped): {o['title']}")
        # the ledger links every value of the dropped twin to the kept one, and
        # checks that the two are equal where they are linked
        led.same(o, seen[o["id"]], "the same observation in AR and POA&M (one uuid), kept once")
        continue
    seen[o["id"]] = o; obs_dedup.append(o)
ap_payload = {"activities": [{"title": a.get("title"),
                              "description": T(pua_scan(a.get("description", "")), "ap"),
                              "steps": [{"title": s.get("title"),
                                         "description": T(pua_scan(s.get("description", "")), "ap")}
                                        for s in a.get("steps", []) or []]}
                             for a in AP.get("local-definitions", {}).get("activities", []) or []],
              "tasks": [{"title": t.get("title"), "type": t.get("type")} for t in AP.get("tasks", []) or []],
              "reviewed-controls": [ic["control-id"] for cs in AP["reviewed-controls"]["control-selections"]
                                    for ic in cs["include-controls"]]}
# who assesses: one list for the Assessment, from the plan and the results and from
# every activity and task below them
roles_assessment = role_list(ap_payload)
for doc, what in ((AP, "the assessment plan"), (AR, "the assessment results")):
    add_roles(roles_assessment, doc, doc["metadata"].get("responsible-parties"), what)
    for a in doc.get("local-definitions", {}).get("activities", []) or []:
        add_roles(roles_assessment, doc, a.get("responsible-roles"), "an activity")
for t in (AP.get("tasks", []) or []) + (res.get("local-definitions", {}).get("tasks", []) or []):
    add_roles(roles_assessment, AP, t.get("responsible-roles"), "a task")
finding_src = res["findings"][0]
# the result reviews one control, and it is the one the Assessment is about
reviewed = [req_of(ic["control-id"]) for cs in res["reviewed-controls"]["control-selections"]
            for ic in cs["include-controls"]]
assert reviewed == [REQ_AC61], f"the assessment result reviews {reviewed}, the bundle carries {REQ_AC61}"
bundle.add("objects/assessment/conmon-2023-06.json",
           {"id": ASSESS, "version": V_AR, "lifecycle": "active",
            "title": res.get("title", AR["metadata"]["title"]),
            "subject-refs": [COMP_SYS, *reviewed],
            "method": {F_AP: ap_payload},
            "performer-ref": party_uri(AR, AR["metadata"]["responsible-parties"][0]["party-uuids"][0], "assessor")
                             if AR["metadata"].get("responsible-parties") else f"{NS}/party/assessor",
            "time": res.get("start", "2023-06-02"),
            "result": D("assessment result from the finding's target status",
                        lambda st: "not-satisfied" if st == "not-satisfied" else "satisfied",
                        finding_src["target"]["status"]["state"]),
            "evidence-refs": [o["id"] for o in obs_dedup],
            "facets": {F_OBS: {"observations": obs_dedup}}})

# ================= 5. Risks + Findings (POA&M risks, AR finding) =================
V_POAM = POAM["metadata"]["version"]
risks = {r["uuid"]: r for r in POAM.get("risks", [])}
items = POAM.get("poam-items", [])
target_obj = finding_src["target"]["target-id"]           # ac-6.1_obj - the 53A objective address

# --- CP-RISK-1: the ex-ante record. Every field below names its source; what
# --- the source cannot supply is counted in risk_gaps and printed in the report.
# OSCAL response `type` prop (allowed: avoid mitigate transfer accept share
# contingency none) -> C.10 treatment option. `contingency` and `none` have no
# JASCON code; they stay in the facet and are counted.
RESPONSE_TREATMENT = {"avoid": "avoid", "mitigate": "modify", "transfer": "share",
                      "share": "share", "accept": "retain"}
risk_gaps = collections.Counter()
response_types = collections.Counter()
_owner = next((rp["party-uuids"][0] for rp in SSP["metadata"].get("responsible-parties", []) or []
               if rp.get("role-id") == "owner" and rp.get("party-uuids")), None)
RISK_OWNER = party_uri(SSP, _owner, "system-owner")
_poam_sys = (POAM.get("system-id") or {}).get("id")
_ssp_sys = {x.get("id") for x in sc.get("system-ids", []) or []}

def risk_analysis(rk):
    """Everything App. F Q14 keeps out of the kernel: how the level would be
    computed (likelihood, impact, their scale system, who rated), plus the
    source's own status and response narrative, verbatim."""
    f = {"risk-status": rk.get("status"),
         "description": T(pua_scan(rk.get("description", "")), "risk"),
         "characterizations": [{"facets": [{"name": x["name"], "value": x["value"], "system": x["system"]}
                                           for x in ch.get("facets", [])],
                                "origin-actors": [a.get("actor-uuid") for a in ch.get("origin", {}).get("actors", [])]}
                               for ch in rk.get("characterizations", []) or []],
         "responses": [{"type": next((p.get("value") for p in rm.get("props", []) or [] if p.get("name") == "type"), None),
                        "lifecycle": rm.get("lifecycle"), "title": rm.get("title"),
                        "description": T(pua_scan(rm.get("description", "")), "risk"),
                        # Finding.actions[] is {description, due, status}; the task's type,
                        # narrative and START have no kernel field and ride here verbatim
                        "tasks": [{"type": t.get("type"), "title": t.get("title"),
                                   "description": T(pua_scan(t.get("description", "")), "risk"),
                                   **{k: v for k, v in (t.get("timing", {}).get("within-date-range", {}) or {}).items()}}
                                  for t in rm.get("tasks", []) or []]}
                       for rm in rk.get("remediations", []) or []]}
    mit = [T(pua_scan(m.get("description", "")), "risk") for m in rk.get("mitigating-factors", []) or []]
    if mit: f["mitigating-factors"] = mit
    return f

def risk_object(rk, name, treats):
    """One POA&M risk -> one Risk. `treats`: the requirement the paired
    Finding is against (the control the response modifies), or None."""
    o = {"id": f"{NS}/risk/{name}", "version": V_POAM, "lifecycle": "active",
         "title": rk.get("title", ""),
         "scenario": pua_scan(rk.get("statement", "")),            # OSCAL `statement` IS the risk statement
         "owner-ref": RISK_OWNER}
    risk_gaps["owner absent in source (derived from the SSP `owner` role)"] += 1
    # state: `closed` retires; every other OSCAL status is at most `identified`,
    # because assessed/treated require a rating (RISK-2) and an OSCAL
    # characterization carries likelihood and impact, never the level.
    o["state"] = D("Risk state from the OSCAL risk status (closed -> retired, anything else -> identified)",
                   lambda st: "retired" if st == "closed" else "identified", rk.get("status"))
    if o["state"] == "identified":
        if rk.get("characterizations"):
            risk_gaps["analysed in source (likelihood + impact) but no level: `assessed` unreachable (RISK-2)"] += 1
    if _poam_sys and _poam_sys in _ssp_sys:                        # POA&M system-id == the SSP's system id
        o["component-refs"] = [D("the system Component, because the POA&M's system-id is an id of the SSP's system",
                                 lambda sid: COMP_SYS if sid in _ssp_sys else None, _poam_sys)]
    rtypes = [r["type"] for r in risk_analysis(rk)["responses"] if r["type"]]
    for rt in rtypes: response_types[rt] += 1
    tcode = RESPONSE_TREATMENT.get(rtypes[0]) if rtypes else None
    if rtypes and tcode is None:
        risk_gaps[f"response type `{rtypes[0]}` has no treatment code (C.10)"] += 1
    treatment = lambda: D("treatment option from the response type (C.10)", lambda t: RESPONSE_TREATMENT[t], rtypes[0])
    if tcode == "modify" and treats:
        o["treatment"] = treatment()
        o["treatments"] = [{"requirement-ref": treats}]
    elif tcode == "avoid":
        o["treatment"] = treatment()
    elif tcode == "retain":
        # RISK-6: retain requires acceptance{approver-ref, date, rationale}. The
        # source has the rationale (the response narrative) and names the
        # approver only in prose; it has NO acceptance date. A date is not
        # invented: the option stays in the facet, the approval stays on the
        # Finding's Deviation, and the gap is reported.
        risk_gaps["response `accept` without a dated acceptance: `retain` unreachable (RISK-6)"] += 1
    elif tcode == "share":
        risk_gaps["response `transfer`/`share` names no party: `share` unreachable (RISK-5)"] += 1
    elif tcode == "modify":
        risk_gaps["response `mitigate` with no control linked in source: `modify` unreachable (RISK-4)"] += 1
    if rk.get("deadline"):
        o["review-due"] = {"type": "datetime", "value": rk["deadline"]}   # OSCAL deadline: date-time-with-timezone
    o["facets"] = {F_RISKA: risk_analysis(rk)}
    return o

def actions_of(rk):
    out = []
    for rm in rk.get("remediations", []) or []:
        for t in rm.get("tasks", []) or []:
            due = t.get("timing", {}).get("within-date-range", {}).get("end")
            a = {"description": D("action description: remediation title, then task title",
                                  lambda r, k: f"{r}: {k}", rm.get("title", ""), t.get("title", "")),
                 "status": rm.get("lifecycle", "planned")}
            if due: a["due"] = {"type": "datetime", "value": due}
            out.append(a)
    return out or [{"description": rk.get("title", "remediation"), "status": "planned"}]

# RISK-2 continues the AR finding (same observation); RISK-1 is POA&M-only (Django panel)
rk2 = next(r for r in risks.values() if "Engineers" in r["title"])
rk1 = next(r for r in risks.values() if r is not rk2)
# The assessment results carry the same risk in its earlier state (the path
# map: "consolidated with the POA&M risks"). Where its text equals the POA&M
# risk's, the ledger links it to what is kept; where it differs (the title
# gained a prefix, the status moved on), a drop below says why.
for ar_risk in res.get("risks", []) or []:
    for field in ("title", "statement", "description"):
        if field in ar_risk and ar_risk[field] == rk2.get(field):
            led.same(ar_risk[field], rk2[field], "the same risk in the assessment results and in the POA&M, kept once")
sca = rk1["characterizations"][0]["facets"][0]["system"]   # https://ifa.gov/division/ociso/sca
# The AR finding (target: an AC-6(1) objective) names this risk through
# related-risks - that is the source's own risk -> control edge.
RISK2 = risk_object(rk2, "goodread-risk-2", REQ_AC61)
RISK1 = risk_object(rk1, "goodread-risk-1", None)
bundle.add("objects/risk/goodread-risk-2.json", RISK2)
bundle.add("objects/risk/goodread-risk-1.json", RISK1)
bundle.add("objects/finding/goodread-risk-2.json",
           {"id": f"{NS}/finding/goodread-risk-2", "version": V_POAM, "lifecycle": "active",
            "title": finding_src.get("title", rk2["title"]),
            "assessment-ref": ASSESS, "requirement-ref": REQ_AC61,
            "state": "in-remediation",
            "risk-refs": [RISK2["id"]],
            "actions": actions_of(rk2),
            "facets": {F_FTGT: {"target-objective-id": target_obj,
                                "implementation-statement-uuid": finding_src.get("implementation-statement-uuid")}}})
bundle.add("objects/finding/goodread-risk-1.json",
           {"id": f"{NS}/finding/goodread-risk-1", "version": V_POAM, "lifecycle": "active",
            "title": rk1.get("title", ""),
            "assessment-ref": ASSESS, "requirement-ref": REQ_AC61,
            "state": "in-remediation",
            "risk-refs": [RISK1["id"]],
            "actions": actions_of(rk1),
            # RISK-9: the risk-adjustment Deviation names the Risk it adjusts for
            "deviations": [{"type": "risk-adjustment", "state": "approved",
                            "rationale": pua_scan(rk1.get("mitigating-factors", [{}])[0].get("description",
                                          "Risk accepted per POA&M deviation approval.")),
                            "approver-ref": sca,
                            "opened": D("date part of the observation's collected timestamp", lambda c: c[:10],
                                        POAM.get("observations", [{}])[0].get("collected", "2023-05-19")),
                            "refs": [D("evidence URI from the first eight characters of the observation uuid",
                                       lambda u: f"{NS}/evidence/obs-{u[:8]}", POAM["observations"][0]["uuid"]),
                                     RISK1["id"]]}]})

# every role list is complete now: attach the ones that hold something, before
# the Attestation digests the system Component
for holder, roles in ROLE_LISTS:
    if roles: holder["responsible-roles"] = roles
for gap, n in sorted(party_gaps.items()):
    note(f"**Parties the source {gap} x{n}** (source finding): a role assignment names a party by uuid, and the "
         f"document {'has no such party' if gap == 'does not define' else 'gives that party no name'} - the leveraged "
         f"pair's parties carry a type and at most a remark. The role is carried without a party; the reference is "
         f"declared in the ledger.")

# ================= 6. Attestation (the ATO as attestation) =================
ato_subjects = [{"id": o["id"], "semantic-digest": semantic_digest(o)}
                for rel, o in sorted(bundle.objects.items())
                if o["id"] in (COMP_SYS, IMPL_SYS, REQ_AC61)]
mini_manifest = json.dumps(ato_subjects, separators=(",", ":"), ensure_ascii=False).encode()
import hashlib
bundle.add("objects/attestation/ifa-ato.json",
           {"id": f"{NS}/attestation/ifa-ato", "version": V_SSP, "lifecycle": "active",
            "title": D("attestation title naming the system",
                       lambda n: f"IFA ATO for {n} (modeled from SSP date-authorized)", sc["system-name"]),
            "subject-semantic-digests": ato_subjects,
            "content-manifest-digest": "sha256:" + hashlib.sha256(mini_manifest).hexdigest(),
            "signer": f"{NS}/party/authorizing-official",
            "timestamp": D("ATO timestamp: midnight UTC of the date authorized", lambda d: f"{d}T00:00:00Z",
                           sc.get("date-authorized", "2025-05-19"))})

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
             "inventory-items": {"type": "array"}, "customer-responsibilities": {"type": "array"},
             "remarks": {"type": "object"}, "responsible-roles": {"type": "array"}})
bundle.stub("goodread-observations-stub.json", F_OBS.split("@")[0], [], {"observations": {"type": "array"}})
bundle.stub("goodread-risk-analysis-stub.json", F_RISKA.split("@")[0], [],
            {"risk-status": {"type": "string"}, "description": {"type": "object"},
             "characterizations": {"type": "array"}, "responses": {"type": "array"},
             "mitigating-factors": {"type": "array"}})
bundle.stub("goodread-finding-target-stub.json", F_FTGT.split("@")[0], [],
            {"target-objective-id": {"type": "string"},
             "implementation-statement-uuid": {"type": "string"}})
# `tasks` and `reviewed-controls` were written since 1.0.0 and missing from this pin (backlog #55)
bundle.stub("goodread-ap-stub.json", F_AP.split("@")[0], [],
            {"activities": {"type": "array"}, "tasks": {"type": "array"}, "reviewed-controls": {"type": "array"},
             "responsible-roles": {"type": "array"}})
bundle.stub("goodread-protocols-stub.json", F_PROTO.split("@")[0], [], {"protocols": {"type": "array"}})
bundle.stub("goodread-implementation-stub.json", F_IMPL.split("@")[0], [],
            {"description": {"type": "object"}, "remarks": {"type": "object"}, "statements": {"type": "array"}})
bundle.stub("goodread-component-stub.json", F_COMP.split("@")[0], [],
            {"title": {"type": "string"}, "description": {"type": "object"}, "purpose": {"type": "object"},
             "status": {"type": "string"}, "props": {"type": "object"}, "responsible-roles": {"type": "array"},
             "control-implementations": {"type": "array"}})
# what each source document says about itself, handed on as it stands: the
# bundle's objects come from seven documents, and the manifest names them
DOC_META = ("title", "version", "oscal-version", "last-modified", "published", "remarks")
source_documents = [{"file": fn, **{k: doc["metadata"][k] for k in DOC_META if k in doc["metadata"]}}
                    for fn, doc in SOURCE_FILES]
manifest = bundle.write({"source": "OSCAL IFA GoodRead example set (SSP 1.1.1, AP, AR, POA&M) + leveraged/"
                        "leveraging SSP pair + component-definition example (usnistgov/oscal-content)",
              "source-note": "FICTIONAL example content by NIST; converted as the gate-3 lifecycle corpus",
              "source-oscal-version": SSP["metadata"]["oscal-version"],
              "source-commit": "usnistgov/oscal-content@9402f031 (2026-07-14; the state fetched 2026-07-22)",
              "source-documents": source_documents,
              "converter": "convert_ifa.py v0.3 (a repeated prop name keeps every value; conversion ledger)",
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
  "system@1 facet inventory-items[] (props by name, their classes in `prop-classes`, the props of each "
  "implemented component in `component-props`)"),
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
  "implementation-statement-uuid -> finding-target@1 facet; related-risks -> Risk.treatments (the risk -> control edge)"),
 (r"^ar\.assessment-results\.results\[\]\.(risks|local-definitions)", "L1",
  "risk content consolidated with the POA&M risks (same risk graph, later state)"),
 (r"^ar\.assessment-results\.local-definitions\.", "L2",
  "Assessment.method payload (activities duplicated from AP; carried once)"),
 (r"^poam\.plan-of-action-and-milestones\.(uuid$|system-id)", "L1", "provenance / system id (system@1)"),
 (r"^poam\.plan-of-action-and-milestones\.observations\[\]\.", "L1",
  "observations@1 facet + landmark evidence URIs (deduped against AR by uuid)"),
 (r"^poam\.plan-of-action-and-milestones\.risks\[\]\.(uuid|title|statement|status|deadline)$", "L1",
  "Risk id/title; statement -> scenario; deadline -> review-due (datetime); status -> Risk state "
  "(+ verbatim in risk-analysis@1) and Finding state (deviation-approved -> approved Deviation; "
  "open+remediation -> in-remediation)"),
 (r"^poam\.plan-of-action-and-milestones\.risks\[\]\.description$", "L2",
  "risk-analysis@1 description (the kernel's `scenario` is the OSCAL statement)"),
 (r"^poam\.plan-of-action-and-milestones\.risks\[\]\.characterizations\[\]\.", "L2",
  "risk-analysis@1 characterizations (likelihood/impact + scale system, origin actors) - scoring stays out of the kernel (App. F Q14)"),
 (r"^poam\.plan-of-action-and-milestones\.risks\[\]\.remediations\[\]\.props\[\]\.", "L1",
  "response `type` -> Risk.treatment (C.10: mitigate->modify, accept->retain, transfer|share->share, avoid->avoid) "
  "+ verbatim in risk-analysis@1 responses[]"),
 (r"^poam\.plan-of-action-and-milestones\.risks\[\]\.remediations\[\]\.(lifecycle|title|description)$", "L1",
  "Finding.actions[] description/status + risk-analysis@1 responses[] (lifecycle, title, narrative)"),
 (r"^poam\.plan-of-action-and-milestones\.risks\[\]\.remediations\[\]\.", "L1",
  "Finding.actions[] (task title; within-date-range.end -> due); remediation/task uuids are source identity (L0)"),
 (r"^poam\.plan-of-action-and-milestones\.risks\[\]\.(mitigating-factors|related-observations)\[?\]?\.", "L1",
  "Deviation rationale (RISK-1) + risk-analysis@1 mitigating-factors; observation links -> evidence refs"),
 (r"^poam\.plan-of-action-and-milestones\.poam-items\[\]\.", "L1",
  "poam-item titles ride the Finding titles; related-risks/observations resolved by uuid"),
 (r"^(lev|lvg)\.system-security-plan\.system-characteristics\.", "L1",
  "provider/consumer Components: system@1 facet, the same content as for the main system "
  "(ids, status, sensitivity, FIPS-199 impact, boundary, remarks)"),
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
  "capabilities with requirement-ref (landmark - the component asserts support, no system binds it): statements -> "
  "statement-ids and clause texts, set-parameters -> parameter-bindings under the catalogue's names; the control "
  "implementation's description and source -> component@1"),
 (r"^cdef\.component-definition\.components\[\]\.(uuid|type|title|description|purpose)$", "L1",
  "Component (kind mapped) id/title"),
]
rows, unmapped = coverage(paths, RULES)
# global occurrence (measured, not declared): the path map above says where
# each source path is MEANT to go; this counts the source values that have an
# equal value SOMEWHERE in the output. It is an upper bound on what was
# carried and does not trace an occurrence to its destination (see
# oscal_conv_lib.global_occurrence).
VA = global_occurrence(list(led.docs.items()), list(bundle.objects.values()))

# the ledger: one entry per source value, each checked against the files just
# written. The one declared drop restates what the coverage report has said
# since 1.0.0 (identity is re-minted); everything else without a destination
# stays unaccounted until somebody decides it, path by path.
led.drop(r"\.uuid$", "the uuid of a source element: JASCON objects get URIs minted from names and titles, "
                     "the uuid itself is not carried (uuids that ARE carried or resolved have a destination above)")
# Decided by the author on 2026-11-13, class by class (register, "Amendments -
# the value-level check of the converters"). A drop applies only to a value
# that reached no destination, so a party name that became a landmark URI
# stays a transformation. Role assignments and references by uuid are NOT
# covered here: they are open and stay unaccounted.
led.drop(r"\.metadata\.revisions\[\]\.",
         "revision history of the source document: bookkeeping of the source, which the manifest pins by commit")
led.drop(r"\.metadata\.(parties|roles)\[\]\.",
         "the source's directory of parties and roles: a party is a landmark URI and there is no party object "
         "(register, backlog #16); the name of a party the bundle refers to has a destination above")
led.drop(r"\.back-matter\.|\.import-(ap|ssp|profile)\.href$|\.leveraged-authorizations\[\]\.links\[\]\.",
         "a link to another serialisation of the source, to an imported document or to the catalogue: the bundle "
         "carries the Requirements themselves and its objects refer to one another by id")
led.drop(r"(\.subjects\[\]\.type|\.assessment-subjects\[\]\.type|\.actors\[\]\.type|\.target\.type|\.identifier-type)$",
         "a type tag of a structural element: the bundle says by its shape what kind of thing the element is")
led.drop(r"\.risks\[\]\.remediations\[\]\.props\[\]\.name$",
         "the prop name `type` is the selector by which the response type is found; the value is carried, "
         "under the field the converter names `type`")
led.drop(r"^ar\.assessment-results\.results\[\]\.risks\[\]\.",
         "the assessment results hold the earlier state of a risk the POA&M carries in its later state; "
         "text equal to the POA&M's is linked to it above, the rest is superseded")
LEDGER = led.account(bundle.out, {**bundle.objects, "content-manifest.json": manifest})
with open(os.path.join(OUTDIR, "ifa-conversion-ledger.json"), "w", encoding="utf-8") as f:
    json.dump(LEDGER, f, indent=1, ensure_ascii=False); f.write("\n")
LT = LEDGER["totals"]

types = collections.Counter(rel.split("/")[1] for rel in bundle.objects)
j = report(
    os.path.join(OUTDIR, "ifa-coverage-report.md"),
    os.path.join(OUTDIR, "ifa-coverage-report.json"),
    "IFA GoodRead lifecycle set -> Semantic Core: Coverage Report (computed)",
    f"Source: **OSCAL IFA GoodRead example set** (SSP v{V_SSP} + AP + AR + POA&M) + "
    f"leveraged/leveraging SSP pair + component-definition example (usnistgov/oscal-content; "
    f"FICTIONAL example content by NIST). Census: `drafts/gate-3-census.md` §4.",
    [f"- Objects emitted: " + ", ".join(f"{v} {k}" for k, v in sorted(types.items())) +
     f" - the five lifecycle types and the Risk type (kernel 2.0.0) at document scale, manifest with both digests.",
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
     f"- **POA&M risks -> Risk objects (CP-RISK-1, kernel 2.0.0)**: statement -> `scenario`; "
     f"deadline -> `review-due` (datetime - OSCAL's type is date-time-with-timezone); POA&M system-id -> "
     f"`component-refs`; response `type` prop -> `treatment` (observed: "
     f"{', '.join(f'{k} x{v}' for k, v in sorted(response_types.items())) or 'none'}); the AR finding's "
     f"related-risks edge -> `treatments[]` (RISK-2 is modified by AC-6.1). likelihood/impact, the source "
     f"status and the response narrative -> risk-analysis@1 (the L2 holding pen for the parked stdlib facet).",
     f"- **POA&M risks -> Findings**: RISK-2 (open + planned remediation) -> state in-remediation with "
     f"actions[] (due = within-date-range.end); RISK-1 (status deviation-approved) -> approved "
     f"`risk-adjustment` Deviation (rationale = mitigating factor, approver = the SCA division URI) whose "
     f"`refs` name the Risk (RISK-9). Each Finding carries `risk-refs` to its Risk; the risk@1 framework "
     f"facet is retired.",
     f"- **Finding target `{target_obj}`** is a 53A OBJECTIVE id - it addresses into the sp800-53a@1 "
     f"facet of the carried AC-6.1 (kept in finding-target@1.target-objective-id; kernel statement-ref "
     f"stays statement-scoped).",
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
     f"- **Global occurrence (measured; path coverage above is a DECLARATION)**: {VA['exact']:,} of "
     f"{VA['leaf-values']:,} source leaf values have an equal value of the same type somewhere in the emitted "
     f"objects. This is an **upper bound** on what was carried: all sources and all objects share one search "
     f"space, so one output value satisfies every equal source value, and a value dropped in one place is hidden "
     f"by an equal value in another. It does not trace an occurrence to its destination. Not counted: "
     f"{VA['key-only']} values that equal only an output key and {VA['embedded']} that occur only inside a longer "
     f"output text (candidates, to be argued per path). No equal value anywhere: "
     f"{VA['absent']['identity']} identity values (uuids/hrefs - re-minted as URIs by design), "
     f"{VA['absent']['document-metadata']} document-metadata values, and **{VA['absent']['content']} content "
     f"values ({VA['absent-content-prose']} of them prose of 40+ characters)** - each either transformed on "
     f"purpose (a mapped code, a respelled id) or DROPPED. That list is a **lower bound** on the losses, not "
     f"the complete work queue. `UNMAPPED: 0` sees none of this; the per-path lists, with the indexed pointer "
     f"of every value, are in the JSON report (`global-occurrence`; backlog #41).",
     f"- **Conversion ledger (measured per source value)**: each of the {LEDGER['leaf-values']:,} source leaf values "
     f"has one entry in `ifa-conversion-ledger.json` saying where it went. **{LT['copied']} copied** (the value "
     f"stands, with its type, at the destination named, read back from the written file), "
     f"**{LT['transformed']} transformed** (a named rule made the destination from it; the rule was applied to the "
     f"source again and compared), **{LT['intentionally-dropped']} intentionally dropped** (a stated reason), "
     f"**{LT['unaccounted']} unaccounted**. Unlike the global figure above, an equal value elsewhere does not count: "
     f"a value is traced by what the converter did with it. Checks that failed: {len(LEDGER['verification-failures'])}. "
     f"The unaccounted values are listed by path at the end of this report; they are the work queue of backlog #41.",
     f"- **What OSCAL cannot give the Risk shape** (model findings, REPORTED; nothing is invented - the one derived value is the owner): " +
     "; ".join(f"{k} x{v}" for k, v in sorted(risk_gaps.items())) +
     f". Owner source: the SSP `owner` role -> {RISK_OWNER}.",
     *(f"- {n}" for n in findings_notes)],
    rows, unmapped,
    {"objects-emitted": dict(types), "carried-requirements": carried,
     "stmt-respell": n_stmt_respell, "pua-codepoints": n_pua,
     "placeholder-uuids": uuid_placeholder, "unresolved-bindings": unresolved_bind,
     "lang-wraps": dict(lang_wraps),
     "risk-shape-gaps": dict(risk_gaps), "response-types": dict(response_types),
     "global-occurrence": VA,
     "ledger": {"file": "ifa-conversion-ledger.json", "leaf-values": LEDGER["leaf-values"], "totals": LT,
                "verification-failures": len(LEDGER["verification-failures"])}})
with open(os.path.join(OUTDIR, "ifa-coverage-report.md"), "a", encoding="utf-8") as f:
    f.write("\n## Unaccounted source values (conversion ledger)\n\n"
            "No destination and no declared reason. Each is either carried by a rule the converter does not state "
            "yet, or dropped without a decision. Pointers to every single value are in `ifa-conversion-ledger.json`.\n\n"
            "| path | count | first value |\n|---|---:|---|\n" +
            "".join(f"| `{u['path']}` | {u['count']} | `{u['pointers'][0]}` |\n" for u in LEDGER["unaccounted-paths"]))
print(f"objects: {sum(types.values())} {dict(types)}")
print(f"leaves: {j['totals']['leaf-values']:,}  mapped: {j['totals']['mapped']:,}  "
      f"UNMAPPED: {j['totals']['unmapped']}")
print(f"global occurrence: {VA['exact']}/{VA['leaf-values']} exact (upper bound); key-only {VA['key-only']}, "
      f"embedded {VA['embedded']}; absent content values: {VA['absent']['content']} ({VA['absent-content-prose']} prose)")
print(f"ledger: copied {LT['copied']}, transformed {LT['transformed']}, intentionally dropped "
      f"{LT['intentionally-dropped']}, unaccounted {LT['unaccounted']}; failed checks {len(LEDGER['verification-failures'])}")
print(f"respell: {n_stmt_respell}  pua: {n_pua}  placeholder-uuids: {uuid_placeholder}  "
      f"unresolved-bindings: {unresolved_bind}")
if unmapped:
    for p, n in unmapped[:40]: print("  UNMAPPED", p, "x", n)
