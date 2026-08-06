#!/usr/bin/env python3
"""NIST SP 800-53 Rev 5 catalog + 800-53B baselines -> Semantic Core bundle.
Census: drafts/gate-3-census.md (2026-07-22). 20 families -> Sets; 1,014
live controls/enhancements -> Requirements (statement items flattened,
modality `must` corpus rule); 182 withdrawn tombstones -> dropped, lineage
inverted onto the successor's kernel `replaces[]`; SP 800-53A layer ->
sp800-53a@1 facet; two-layer ODP params -> statement-scoped kernel
parameters (declared where inserted, the 216 per-statement rule) + odp@1
admin facet; baselines -> 4 membership Sets. Coverage target: 0."""
import json, os, re, collections
from oscal_conv_lib import make_T, slug, Bundle, inventory, coverage, report, walk_controls

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SRCDIR = os.path.join(ROOT, "sources", "nist")
OUTDIR = os.path.join(ROOT, "converted_examples", "US.SP800-53")
NS = "https://ns.nist.gov/sp800-53"   # matches the corpus's existing mapping-endpoint URIs
F_NARR = f"{NS}/facet/narrative@1"
F_53A = f"{NS}/facet/sp800-53a@1"
F_ODP = f"{NS}/facet/odp@1"
F_RMF = f"{NS}/facet/rmf@1"
F_REF = f"{NS}/facet/references@1"

lang_wraps = collections.Counter()
T = make_T("en", lang_wraps)
INSERT = re.compile(r"\{\{\s*insert:\s*param,\s*([a-z0-9._-]+)\s*\}\}")
MDLINK = re.compile(r"\[([^\]]+)\]\(#[a-zA-Z0-9._-]+\)")

cat = json.load(open(os.path.join(SRCDIR, "NIST_SP-800-53_rev5_catalog.json"), encoding="utf-8"))["catalog"]
VER = cat["metadata"]["version"]
BASELINES = {b: json.load(open(os.path.join(SRCDIR, f"NIST_SP-800-53_rev5_{b}-baseline_profile.json"),
                               encoding="utf-8"))["profile"]
             for b in ("LOW", "MODERATE", "HIGH", "PRIVACY")}

def norm(p):
    p = re.sub(r"(\.controls\[\])+", ".controls[]", p)
    p = re.sub(r"(\.parts\[\])+", ".parts[]", p)
    return p

paths = collections.Counter()
inventory({"catalog": cat}, "nist", paths, normalize=norm)
for b, prof in BASELINES.items():
    inventory({"profile": prof}, b.lower(), paths, normalize=norm)

# ---------- helpers ----------
def prop(c, name, ns=None, cls=None, all_=False):
    out = [p["value"] for p in c.get("props", []) or []
           if p.get("name") == name and (ns is None or p.get("ns") == ns)
           and (cls is None or p.get("class") == cls)]
    return out if all_ else (out[0] if out else None)

def mint(src_id):
    return f"{NS}/req/{src_id.upper()}"

def rewrite(prose, used=None):
    """{{ insert: param, x }} -> {param:x}; markdown #-links -> their text."""
    def sub_ins(m):
        if used is not None: used.add(m.group(1))
        return "{param:" + m.group(1) + "}"
    n_links[0] += len(MDLINK.findall(prose or ""))
    return MDLINK.sub(r"\1", INSERT.sub(sub_ins, prose or ""))

n_links = [0]

# back-matter: uuid -> (title, citation, url)
RES = {}
for r in cat.get("back-matter", {}).get("resources", []) or []:
    RES[r["uuid"]] = {"title": r.get("title", ""),
                      "citation": (r.get("citation") or {}).get("text", ""),
                      "url": (r.get("rlinks") or [{}])[0].get("href", "")}

controls = list(walk_controls(cat))
by_id = {c["id"]: c for c, _, _ in controls}
withdrawn = {c["id"] for c, _, _ in controls if prop(c, "status") == "withdrawn"}
live = [(c, par, g) for c, par, g in controls if c["id"] not in withdrawn]
groups_by_id = {g["id"]: g for g in cat.get("groups", []) or []}
params_global = {pm["id"]: pm for c, _, _ in controls for pm in c.get("params", []) or []}

# ---------- withdrawal inversion: successor.replaces[] ----------
MODE = {"incorporated-into": "merged-into", "moved-to": "renamed"}
succ_replaces = collections.defaultdict(list)   # successor cid -> entries
fam_replaces = collections.defaultdict(list)    # successor group id -> entries (moved-to a family)
wd_chain, wd_dangling = [], []
for c, _, _ in controls:
    if c["id"] not in withdrawn: continue
    for l in c.get("links", []) or []:
        rel, href = l.get("rel"), (l.get("href") or "").lstrip("#")
        if rel not in MODE: continue
        target, into = href, None
        if "_smt" in href:                       # statement-level target
            target, into = href.split("_smt")[0], "smt" + href.split("_smt")[1]
        e = {"ref": mint(c["id"]), "mode": MODE[rel], "label": prop(c, "label", cls=None) or c["id"].upper(),
             "title": c.get("title", "")}
        if into: e["into"] = into
        if target in withdrawn:
            wd_chain.append((c["id"], target)); continue
        if target in by_id:
            succ_replaces[target].append(e)
        elif target in groups_by_id:             # sa-12 -> #sr: successor is a whole family
            fam_replaces[target].append(e)
        else:
            wd_dangling.append((c["id"], href))

# ---------- parameter declarations ----------
def param_decl(pm):
    d = {"name": pm["id"]}
    if "select" in pm:
        d["type"] = "choice"
        d["choices"] = [{"value": rewrite(ch)} for ch in pm["select"].get("choice", [])]
        if pm["select"].get("how-many") == "one-or-more":
            d["cardinality"] = "many"
    else:
        d["type"] = "string"
    if pm.get("label"):
        d["label"] = pm["label"]
    return d

# formal ODP id round-trip check (prop label == uppercase transform of id)
def formal(pid):
    m = re.fullmatch(r"([a-z]{2}-[0-9]+(?:\.[0-9]+)?)_odp(?:\.([0-9]+))?", pid)
    if not m: return None
    base = m.group(1)
    fam, num = base.split("-", 1)
    num = num.split(".")
    lbl = f"{fam.upper()}-{int(num[0]):02d}" + (f".{int(num[1]):02d}" if len(num) > 1 else "")
    return f"{lbl}_ODP" + (f"[{m.group(2)}]" if m.group(2) else "")

formal_ok, formal_div = 0, []
label_eq, label_div = 0, []

# ---------- objectives / methods trees ----------
def obj_tree(pt, used):
    node = {}
    if pt.get("id"): node["id"] = pt["id"]
    lab = prop(pt, "label", cls="sp800-53a")
    if lab: node["label"] = lab
    if pt.get("prose"): node["prose"] = T(rewrite(pt["prose"], used), "objective")
    kids = [obj_tree(s, used) for s in pt.get("parts", []) or []]
    if kids: node["children"] = kids
    return node

def methods_of(c, used):
    out = []
    for pt in c.get("parts", []) or []:
        if pt.get("name") != "assessment-method": continue
        m = {"method": prop(pt, "method"), "label": prop(pt, "label", cls="sp800-53a")}
        objs = [s.get("prose", "") for s in pt.get("parts", []) or [] if s.get("name") == "assessment-objects"]
        if objs:
            m["objects"] = [T(rewrite(x.strip(), used), "assessment-objects")
                            for x in re.split(r"\n\s*\n", objs[0]) if x.strip()]
        out.append({k: v for k, v in m.items() if v})
    return out

# ---------- statements: flatten prose-bearing statement/item nodes ----------
def flat_statements(c):
    out = []
    def walk(pt):
        if pt.get("prose"):
            out.append(pt)
        for s in pt.get("parts", []) or []:
            walk(s)
    for pt in c.get("parts", []) or []:
        if pt.get("name") == "statement":
            walk(pt)
    return out

# ---------- convert live controls ----------
mod_count = collections.Counter()
decl_hist = collections.Counter()      # #10: statements-declaring-a-param histogram
multi_decl = []                        # params inserted in >=2 statements
no_site = collections.Counter()        # params without a statement insertion site
facet_only, nowhere = [], []           # ... of those: bound in 53A objectives / bound nowhere
cross_param = []                       # prose inserts another control's param
op_default = 0
rel_count = collections.Counter()
req_ids = {}
n_53a = 0

for c, parents, gchain in live:
    cid = c["id"]
    rid = mint(cid)
    # labels: verify zero-padded == sp800-53a
    zp, la = prop(c, "label", cls="zero-padded"), prop(c, "label", cls="sp800-53a")
    if la is not None:
        if zp == la: label_eq += 1
        else: label_div.append(cid)
    plain = next((p["value"] for p in c.get("props", [])
                  if p.get("name") == "label" and not p.get("class")), cid.upper())
    # obligated parties from implementation-level
    lvls = prop(c, "implementation-level", ns="http://csrc.nist.gov/ns/rmf", all_=True)
    if not lvls:
        lvls = ["organization"]; op_default += 1
    parties = [f"{NS}/party/{v}" for v in lvls]
    # statements + per-statement param declaration
    params = {pm["id"]: pm for pm in c.get("params", []) or []}
    stmts, declared_any = [], set()
    for pt in flat_statements(c):
        used = set()
        prose = rewrite(pt["prose"], used)
        sid = pt.get("id", f"{cid}_smt")
        sid = sid[len(cid) + 1:] if sid.startswith(cid + "_") else sid
        s = {"id": sid, "modality": "must", "obligated-parties": parties,
             "prose": {"en": prose}}
        decls = []
        for u in sorted(used):
            if u in params:
                decls.append(param_decl(params[u]))
            elif u in params_global:   # cross-control insertion (source irregularity)
                decls.append(param_decl(params_global[u]))
                cross_param.append((cid, u))
        if decls: s["parameters"] = decls
        declared_any |= used
        stmts.append(s)
        mod_count["must"] += 1
    # params without a statement insertion site -> declare on first statement (counted)
    rest = [pid for pid in params if pid not in declared_any]
    if rest and stmts:
        extra = [param_decl(params[p]) for p in sorted(rest)]
        stmts[0].setdefault("parameters", []).extend(extra)
        for p in rest: no_site[p] += 1
    # #10 measure: in how many statements is each param inserted?
    for pid in params:
        n = sum(1 for s in stmts for _ in [0]
                if ("{param:" + pid + "}") in s["prose"]["en"])
        decl_hist[n] += 1
        if n >= 2: multi_decl.append((cid, pid, n))
    # formal-ODP round-trip
    for pid, pm in params.items():
        fp = next((p["value"] for p in pm.get("props", []) if p.get("name") == "label"), None)
        if fp is not None:
            if formal(pid) == fp: formal_ok += 1
            else: formal_div.append((pid, fp))
    req = {"id": rid, "version": VER, "label": plain, "lifecycle": "active",
           "title": c.get("title", cid), "statements": stmts}
    # facets
    facets = {}
    guid = [T(rewrite(p["prose"]), "guidance") for p in c.get("parts", []) or []
            if p.get("name") == "guidance" and p.get("prose")]
    if guid: facets[F_NARR] = {"guidance": guid}
    used_f = set()
    objectives = [obj_tree(p, used_f) for p in c.get("parts", []) or []
                  if p.get("name") == "assessment-objective"]
    methods = methods_of(c, used_f)
    for p in rest:
        (facet_only if p in used_f else nowhere).append(p)
    if objectives or methods:
        f = {}
        if objectives: f["objectives"] = objectives
        if methods: f["methods"] = methods
        facets[F_53A] = f; n_53a += 1
    odp_admin = {}
    for pid, pm in params.items():
        a = {}
        if pm.get("guidelines"):
            a["guidelines"] = [T(rewrite(g.get("prose", ""))) for g in pm["guidelines"]]
        alts = [p["value"] for p in pm.get("props", []) if p.get("name") == "alt-identifier"]
        if alts: a["alt-identifiers"] = alts
        al = next((p["value"] for p in pm.get("props", []) if p.get("name") == "alt-label"), None)
        if al: a["alt-label"] = al
        aggs = [p["value"] for p in pm.get("props", []) if p.get("name") == "aggregates"]
        if aggs: a["aggregates"] = aggs
        if a: odp_admin[pid] = a
    if odp_admin: facets[F_ODP] = {"params": odp_admin}
    if prop(c, "contributes-to-assurance", ns="http://csrc.nist.gov/ns/rmf") == "true":
        facets[F_RMF] = {"contributes-to-assurance": True}
    if facets: req["facets"] = facets
    # relations
    rels = []
    for l in c.get("links", []) or []:
        rel, href = l.get("rel"), (l.get("href") or "").lstrip("#")
        if rel == "related" and href in by_id and href not in withdrawn:
            rels.append({"type": "related", "ref": mint(href)}); rel_count["related"] += 1
        elif rel == "related":
            rel_count["related-to-withdrawn-or-missing"] += 1
        elif rel == "required" and href in by_id:
            rels.append({"type": "required", "ref": mint(href)}); rel_count["required"] += 1
        elif rel == "reference" and href in RES and RES[href]["url"]:
            rels.append({"type": "reference", "ref": RES[href]["url"]}); rel_count["reference"] += 1
        elif rel == "reference":
            rel_count["reference-unresolved"] += 1
    if rels:
        seen = set(); ded = []
        for r in rels:
            k = (r["type"], r["ref"])
            if k not in seen: seen.add(k); ded.append(r)
        req["relations"] = ded
    # withdrawal inversion
    if succ_replaces.get(cid):
        entries = succ_replaces[cid]
        req["replaces"] = [{"ref": e["ref"], "mode": e["mode"]} for e in entries]
        req["annotations"] = {"nist-withdrawal": [
            {k: v for k, v in e.items() if k in ("ref", "label", "title", "into", "mode")}
            for e in entries]}
    req_ids[cid] = (rid, f"objects/req/{slug(cid)}.json", req)

bundle = Bundle(os.path.join(OUTDIR, "sp800-53-core-bundle"))
for cid, (rid, bp, req) in req_ids.items():
    bundle.add(bp, req)

# ---------- family Sets + root ----------
def sortkey(cid):
    return prop(by_id[cid], "sort-id") or cid

root_members, fam_sets = [], 0
for g in cat.get("groups", []):
    fam = [c["id"] for c, _, gg in live if gg and gg[0]["id"] == g["id"]]
    fam.sort(key=sortkey)
    suri = f"{NS}/set/family/{g['id']}"
    sobj = {"id": suri, "version": VER, "lifecycle": "active",
            "title": g.get("title", g["id"]),
            "label": (prop(g, "label") or g["id"].upper()),
            "members": [{"ref": mint(cid), "sequence": (i + 1) * 10} for i, cid in enumerate(fam)]}
    over = [p for p in g.get("parts", []) or [] if p.get("name") == "overview"]
    if over:
        sobj["facets"] = {F_NARR: {"guidance": [T(rewrite(p.get("prose", "")), "overview") for p in over]}}
    if fam_replaces.get(g["id"]):                # sa-12 "moved to SR family": Set-level successor
        entries = fam_replaces[g["id"]]
        sobj["replaces"] = [{"ref": e["ref"], "mode": e["mode"]} for e in entries]
        sobj["annotations"] = {"nist-withdrawal": [
            {k: v for k, v in e.items() if k in ("ref", "label", "title", "into", "mode")}
            for e in entries]}
    bundle.add(f"objects/set/family-{slug(g['id'])}.json", sobj)
    root_members.append({"ref": suri, "sequence": len(root_members) * 10 + 10})
    fam_sets += 1
root = {"id": f"{NS}/set/root", "version": VER, "lifecycle": "active",
        "title": cat["metadata"]["title"], "members": root_members,
        "facets": {F_REF: {"resources": [
            {k: v for k, v in r.items() if v} for _, r in sorted(RES.items(), key=lambda kv: kv[1]["title"])]}}}
bundle.add("objects/set/root.json", root)

# ---------- baseline Sets ----------
bl_missing = collections.defaultdict(list)
for b, prof in BASELINES.items():
    ids = prof["imports"][0]["include-controls"][0]["with-ids"]
    members = []
    for i, cid in enumerate(ids):
        if cid in withdrawn or cid not in by_id:
            bl_missing[b].append(cid); continue
        members.append({"ref": mint(cid), "sequence": (i + 1) * 10})
    bundle.add(f"objects/set/baseline-{b.lower()}.json",
               {"id": f"{NS}/set/baseline/{b.lower()}", "version": VER, "lifecycle": "active",
                "title": prof["metadata"]["title"], "label": b, "members": members})

# ---------- facet stubs ----------
bundle.stub("sp800-53-narrative-stub.json", F_NARR.split("@")[0], [], {"guidance": {"type": "array"}})
bundle.stub("sp800-53a-stub.json", F_53A.split("@")[0], [],
            {"objectives": {"type": "array"}, "methods": {"type": "array"}})
bundle.stub("sp800-53-odp-stub.json", F_ODP.split("@")[0], [], {"params": {"type": "object"}})
bundle.stub("sp800-53-rmf-stub.json", F_RMF.split("@")[0], [],
            {"contributes-to-assurance": {"type": "boolean"}})
bundle.stub("sp800-53-references-stub.json", F_REF.split("@")[0], [], {"resources": {"type": "array"}})
bundle.write({"source": cat["metadata"]["title"], "source-version": VER,
              "source-oscal-version": cat["metadata"]["oscal-version"],
              "baselines": {b: p["metadata"]["version"] for b, p in BASELINES.items()},
              "converter": "convert_nist.py v0.1",
              "namespace-note": "https://ns.nist.gov/sp800-53 minted to match the corpus's "
                                "pre-existing mapping-endpoint URIs; pending a NIST-published URI"})

# ---------- corpus cross-check: mapping endpoints vs minted ids ----------
cited = collections.Counter()
for base, _, files in os.walk(os.path.join(ROOT, "converted_examples")):
    if "US.SP800-53" in base or "oscal-export" in base: continue
    for fn in files:
        if not fn.endswith(".json"): continue
        try:
            txt = open(os.path.join(base, fn), encoding="utf-8").read()
        except OSError:
            continue
        # carried COPIES of sp800-53 objects (the authorization-package
        # pattern) are the objects themselves, not citations - skip them
        if '"id": "https://ns.nist.gov/sp800-53/' in txt[:400]: continue
        for m in re.finditer(r'"https://ns\.nist\.gov/sp800-53/req/([A-Za-z0-9.()-]+)"', txt):
            cited[m.group(1)] += 1
minted_names = {rid.rsplit("/", 1)[-1] for cid, (rid, _, _) in req_ids.items()}
wd_names = {cid.upper() for cid in withdrawn}
hit = {k: v for k, v in cited.items() if k in minted_names}
hit_wd = {k: v for k, v in cited.items() if k in wd_names}
miss = {k: v for k, v in cited.items() if k not in minted_names and k not in wd_names}

# ---------- coverage ----------
RULES = [
 (r"^nist\.catalog\.(uuid$|metadata\.)", "L1", "bundle manifest / L0 provenance"),
 (r"^nist\.catalog\.back-matter\.", "L1",
  "reference-link resolution table + references@1 facet on the root Set (title/citation/url)"),
 (r"^nist\.catalog\.groups\[\]\.(id|class|title)$", "L1", "family Set id/title (D21 nesting under root)"),
 (r"^nist\.catalog\.groups\[\]\.props\[\]\.(name|value)$", "L1", "family Set label"),
 (r"^nist\.catalog\.groups\[\]\.parts\[\]\.", "L2",
  "pm overview part -> narrative@1 guidance on the pm family Set (language-tagged)"),
 (r"^nist\.catalog\.groups\[\]\.controls\[\]\.(id|title)$", "L1",
  "Requirement id (URI mint, dot form = corpus mapping endpoints) + title | withdrawn: dropped, lineage inverted"),
 (r"^nist\.catalog\.groups\[\]\.controls\[\]\.class$", "L1",
  "encoded structurally: family Set membership + `required` base edge distinguishes enhancements"),
 (r"^nist\.catalog\.groups\[\]\.controls\[\]\.props\[\]\.(name|value|ns|class)$", "L1",
  "label(plain)->label; zero-padded/sp800-53a->L3-derivable (equality asserted); sort-id->Set sequence; "
  "implementation-level->obligated-parties mint; contributes-to-assurance->rmf@1; status->tombstone drop + successor replaces[]"),
 (r"^nist\.catalog\.groups\[\]\.controls\[\]\.links\[\]\.(href|rel)$", "L1",
  "related->related; required->required; reference->reference (resolved URL); incorporated-into/moved-to->successor replaces[] (merged-into/renamed) + nist-withdrawal annotation"),
 (r"^nist\.catalog\.groups\[\]\.controls\[\]\.params\[\]\.(id|label)$", "L1",
  "statement-scoped kernel parameter decl (name, label) on each inserting statement (216 per-statement rule)"),
 (r"^nist\.catalog\.groups\[\]\.controls\[\]\.params\[\]\.select\.", "L1",
  "choice type + choices[] + cardinality many (one-or-more)"),
 (r"^nist\.catalog\.groups\[\]\.controls\[\]\.params\[\]\.guidelines\[\]\.prose$", "L2",
  "odp@1 facet params.{name}.guidelines (language-tagged)"),
 (r"^nist\.catalog\.groups\[\]\.controls\[\]\.params\[\]\.props\[\]\.", "L1",
  "prop label (formal ODP id) -> L3-derivable (round-trip asserted); alt-identifier/alt-label/aggregates -> odp@1 facet"),
 (r"^nist\.catalog\.groups\[\]\.controls\[\]\.parts\[\]\.(id|name)$", "L1",
  "statement/item -> flattened statements[] (id suffix); guidance -> narrative@1; assessment-* -> sp800-53a@1"),
 (r"^nist\.catalog\.groups\[\]\.controls\[\]\.parts\[\]\.prose$", "L1",
  "statement prose (insertions -> {param:} tokens); guidance/objectives/objects prose -> facets (language-tagged; md #-links -> text)"),
 (r"^nist\.catalog\.groups\[\]\.controls\[\]\.parts\[\]\.(ns|class)$", "L1",
  "part-name namespace markers; encoded by facet placement"),
 (r"^nist\.catalog\.groups\[\]\.controls\[\]\.parts\[\]\.props\[\]\.", "L1",
  "item print labels -> L3-derivable (id-encoded); sp800-53a objective/method labels -> sp800-53a@1; method EXAMINE/INTERVIEW/TEST -> sp800-53a@1 methods"),
 (r"^nist\.catalog\.groups\[\]\.controls\[\]\.parts\[\]\.links\[\]\.", "L1",
  "in-prose citation links; resolved with the same reference table (md #-links -> text; target rides control-level reference relation)"),
 (r"^(low|moderate|high|privacy)\.profile\.imports\[\]\.include-controls\[\]\.with-ids\[\]$", "L1",
  "baseline Set members (minted URIs, catalog order)"),
 (r"^(low|moderate|high|privacy)\.profile\.(uuid$|metadata\.|back-matter\.)", "L1",
  "bundle manifest / L0 provenance (baseline documents)"),
 (r"^(low|moderate|high|privacy)\.profile\.(imports\[\]\.href|merge\.as-is)$", "L3",
  "OSCAL-profile resolution mechanics; the selection IS the Set (no semantic residue)"),
]
rows, unmapped = coverage(paths, RULES)

nset = sum(1 for rel in bundle.objects if "/set/" in rel)
j = report(
    os.path.join(OUTDIR, "sp800-53-coverage-report.md"),
    os.path.join(OUTDIR, "sp800-53-coverage-report.json"),
    "NIST SP 800-53 Rev 5 + 800-53B -> Semantic Core: Coverage Report (computed)",
    f"Source: **{cat['metadata']['title']}** v{VER} (OSCAL {cat['metadata']['oscal-version']}) "
    f"+ four 800-53B baseline profiles. Census: `drafts/gate-3-census.md`.",
    [f"- Objects emitted: **{len(req_ids)} Requirements** (324+872 minus {len(withdrawn)} withdrawn tombstones), "
     f"**{nset} Sets** ({fam_sets} families + root + 4 baselines), manifest with both digests.",
     f"- Baseline membership: " + ", ".join(f"{b} {len(BASELINES[b]['imports'][0]['include-controls'][0]['with-ids'])}"
                                            for b in BASELINES) + "."],
    [f"- **Withdrawn tombstones dropped, lineage inverted (kernel `replaces[]`)**: {len(withdrawn)} withdrawn; "
     f"{sum(len(v) for v in succ_replaces.values())} successor edges on Requirements + "
     f"{sum(len(v) for v in fam_replaces.values())} on family Sets (sa-12 'moved to SR' - the successor is a "
     f"whole family; shared base makes Set-level `replaces` legal) "
     f"(incorporated-into->merged-into, moved-to->renamed); statement-precision + withdrawn label/title in "
     f"`annotations['nist-withdrawal']`; withdrawn->withdrawn chains x{len(wd_chain)}, dangling x{len(wd_dangling)}.",
     f"- **Modality corpus rule `must` x{mod_count['must']}**: Rev 5 statements are uniformly imperative and "
     f"obligation binds on baseline selection - the INVERSE of the declarative national pattern "
     f"(ISM/CIS/CyFun/C5). Force in the mood, selection in the baseline Sets; both confirm D13's split axes.",
     f"- **Obligated parties from `implementation-level`**: organization/system party URIs; "
     f"absent -> organization default x{op_default}.",
     f"- **Two-layer ODP params -> statement-scoped decls**: declared on each statement whose prose inserts "
     f"them (216 per-statement rule); choice x{sum(1 for cid, (rid, _, r) in req_ids.items() for s in r['statements'] for p in s.get('parameters', []) if p['type'] == 'choice')}, "
     f"string else; legacy _prm_ aggregates carried as params + odp@1 `aggregates`; params without a "
     f"statement insertion site x{sum(no_site.values())} declared on the first statement "
     f"({len(facet_only)} bind only in the 53A objectives, {len(nowhere)} nowhere).",
     f"- **SP 800-53A layer -> sp800-53a@1** on {n_53a} Requirements: objective trees (53a labels kept - "
     f"the #10 addressing surface) + EXAMINE/INTERVIEW/TEST methods with object lists (language-tagged).",
     f"- **Relations**: " + ", ".join(f"{k} x{v}" for k, v in sorted(rel_count.items(), key=lambda x: -x[1])) +
     f"; reference targets resolved to publication URLs (landmark); title/citation table -> references@1 on the root Set.",
     f"- **Markdown citation links in prose -> plain text** x{n_links[0]} (citation rides the reference relation).",
     f"- **Label triplet**: zero-padded == sp800-53a asserted ({label_eq} equal, divergent: {label_div or 'none'}); "
     f"plain -> `label`; zero-padded L3-derivable.",
     f"- **Formal ODP ids round-trip** (prop label == uppercase(param name)): ok x{formal_ok}, "
     f"divergent x{len(formal_div)}" + (f" ({formal_div[:5]})" if formal_div else "") + ".",
     f"- **Payload free text language-tagged**: " + ", ".join(f"{k} x{v}" for k, v in sorted(lang_wraps.items())) + "."],
    [f"- **#10 measure (ODP -> statement addressing)**: insertion-count histogram "
     f"{dict(sorted(decl_hist.items()))}; params inserted in >=2 statements: **{len(multi_decl)}** "
     + (f"({[(c, p) for c, p, n in multi_decl[:6]]}...)" if multi_decl else "(none)") +
     f" - the (requirement, ODP) address resolves via the declaring statement"
     + ("" if not multi_decl else "; ambiguous cases need the statement map") + ".",
     f"- **Corpus mapping endpoints vs minted ids**: {sum(hit.values())} citations resolve "
     f"({len(hit)} distinct), {sum(hit_wd.values())} hit withdrawn tombstones "
     f"({sorted(hit_wd)[:8] if hit_wd else []}) - a resolver follows the successor's `replaces[]` backwards; "
     f"{sum(miss.values())} cite unknown labels ({sorted(miss)[:8] if miss else []}).",
     f"- **Baseline ids not emitted** (withdrawn or unknown): " +
     ("; ".join(f"{b}: {v}" for b, v in bl_missing.items()) if bl_missing else "none") + ".",
     f"- **Cross-control param insertions x{len(cross_param)}** ({cross_param}): prose in one control "
     f"inserts another control's ODP - a source irregularity (3 of 2,945 insertions); the declaration is "
     f"duplicated onto the inserting statement per the 216 per-statement rule. REPORTED upstream.",
     f"- **Params bound nowhere x{len(nowhere)}** (ODPs defined for assessment that neither control text "
     f"nor 53A objectives insert) - declarations without any insertion site."],
    rows, unmapped,
    {"source-version": VER,
     "objects-emitted": {"requirements": len(req_ids), "sets": nset},
     "withdrawn": {"count": len(withdrawn), "successor-edges": sum(len(v) for v in succ_replaces.values()),
                   "family-set-edges": sum(len(v) for v in fam_replaces.values()),
                   "chains": wd_chain, "dangling": wd_dangling},
     "cross-control-params": [{"control": c, "param": p} for c, p in cross_param],
     "no-statement-site": {"total": sum(no_site.values()), "facet-only": len(facet_only),
                           "nowhere": len(nowhere)},
     "modality": dict(mod_count),
     "backlog-10": {"insertion-histogram": {str(k): v for k, v in sorted(decl_hist.items())},
                    "multi-declared": [{"control": c, "param": p, "statements": n} for c, p, n in multi_decl]},
     "endpoint-crosscheck": {"resolved": sum(hit.values()), "distinct": len(hit),
                             "withdrawn-hits": hit_wd, "unknown": miss},
     "baseline-missing": dict(bl_missing),
     "lang-wraps": dict(lang_wraps)})
print(f"reqs: {len(req_ids)}  sets: {nset}  leaves: {j['totals']['leaf-values']:,}  "
      f"mapped: {j['totals']['mapped']:,}  UNMAPPED: {j['totals']['unmapped']}")
print(f"withdrawn: {len(withdrawn)}  successor-edges: {sum(len(v) for v in succ_replaces.values())}  "
      f"chains: {len(wd_chain)}  dangling: {len(wd_dangling)}")
print(f"#10 multi-declared params: {len(multi_decl)}  histogram: {dict(sorted(decl_hist.items()))}")
print(f"endpoint crosscheck: resolved {sum(hit.values())}  withdrawn-hits {dict(hit_wd)}  unknown {dict(miss)}")
if unmapped:
    for p, n in unmapped[:30]: print("  UNMAPPED", p, "x", n)
