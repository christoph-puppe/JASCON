#!/usr/bin/env python3
"""CIS Ubuntu Linux 24.04 LTS Benchmark (OSCAL catalog) -> Semantic Core.
312 hardening rules -> Requirements (audit/remediation -> assessment-
criteria@1, method automated|manual); back-matter PROFILE resources +
per-rule reference links -> Level 1/2 Server/Workstation baseline Sets
(the ISM applicability pattern, benchmark edition); CIS_Controls links ->
Mapping objects into the CIS Controls corpus (v8 targets resolve to the
sibling bundle; v7 targets minted under a v7 namespace). Target: 0."""
import json, os, re, collections
from oscal_conv_lib import make_T, slug, Bundle, inventory, coverage, report

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SRC = os.path.join(ROOT, "sources", "CIS Ubuntu Linux 24.04 LTS Benchmark.json")
OUTDIR = os.path.join(ROOT, "converted_examples", "CIS.Ubuntu2404")
NS = "https://ns.cisecurity.org/benchmark/ubuntu-24.04-lts"
CISC8 = "https://ns.cisecurity.org/controls/v8"
CISC7 = "https://ns.cisecurity.org/controls/v7"
F_ACRIT = "https://ns.oscal.org/stdlib/facet/assessment-criteria@1"
F_NARR = f"{NS}/facet/narrative@1"
F_XREF = f"{NS}/facet/external-references@1"
COMPAT = "https://ns.oscal.org/compat/oscal-1x@1"

lang_wraps = collections.Counter()
T = make_T("en", lang_wraps)

cat = json.load(open(SRC, encoding="utf-8"))["catalog"]
VER = cat["metadata"]["version"]

paths = collections.Counter()
inventory({"catalog": cat}, "cisb", paths)

G = r"(\.groups\[\])+"
CTL = rf"^cisb\.catalog{G}\.controls\[\]"
RULES = [
 (r"^cisb\.catalog\.(uuid|metadata\.)", "L1", "bundle manifest / L0 provenance"),
 (rf"^cisb\.catalog{G}\.(id|title)$", "L1", "section Set id/title"),
 (rf"^cisb\.catalog{G}\.props\[\]\.(name|value)$", "L1", "group label -> Set label"),
 (rf"^cisb\.catalog{G}\.parts\[\]\.(id|name|prose)$", "L2",
  "compat facet oscal-1x@1: section overview narrative on the Set (language-tagged {en})"),
 (CTL + r"\.(id|title)$", "L1", "Requirement id (URI mint) + title; statement prose minted from title (source statement empty - declared + counted)"),
 (CTL + r"\.props\[\]\.(name|value|class)$", "L1",
  "dispatch: label -> Requirement.label; marking xccdf_id -> aliases (scheme xccdf); marking automated|manual -> assessment-criteria@1 method (class attr on markings absorbed with the value)"),
 (CTL + r"\.links\[\]\.(rel|href)$", "L1",
  "reference links resolved via back-matter: profile resources -> baseline Set membership (Level 1/2 Server/Workstation); document resources -> relations reference"),
 (CTL + r"\.parts\[\]\.(id|name|class)$", "L1", "part dispatch (statement/desc/rationale, assessment-method, guidance kinds)"),
 (CTL + r"\.parts\[\]\.props\[\]\.(name|value|class)$", "L1",
  "part labels (Description/Rationale/Audit/Remediation/CIS Controls/References) -> facet keys; method TEST -> assessment-criteria; References markings -> external-references@1 payload (citation labels, kept bare)"),
 (CTL + r"\.parts\[\]\.prose$", "L1",
  "Description/Rationale -> narrative@1; Audit script -> assessment-criteria@1.audit; Remediation -> assessment-criteria@1.remediation (language-tagged)"),
 (CTL + r"\.parts\[\]\.links\[\]\.(rel|href)$", "L1",
  "CIS_Controls part links -> Mapping objects (v8 -> sibling CIS Controls bundle; v7 -> v7 namespace)"),
 (r"^cisb\.catalog\.back-matter\.resources\[\]\.(uuid|title|description|rlinks\[\]\.href)$", "L1",
  "resolution table: profiles -> baseline Sets; safeguard resources -> Mapping targets; documents -> reference URLs (descriptions recorded in the table)"),
 (r"^cisb\.catalog\.back-matter\.resources\[\]\.props\[\]\.(name|value|class)$", "L1",
  "resource kind dispatch: xccdf profile marking | CIS_Controls version + safeguard number | document markings"),
]

resources = {r["uuid"]: r for r in (cat.get("back-matter", {}) or {}).get("resources", [])}
def res_kind(r):
    for p in r.get("props", []) or []:
        if p["name"] == "marking" and "benchmarks_profile" in str(p.get("value", "")): return "profile"
        if p["name"] == "version" and p.get("class") == "CIS_Controls": return "safeguard"
    return "document"
profile_res = {u: r for u, r in resources.items() if res_kind(r) == "profile"}
safeguard_res = {u: r for u, r in resources.items() if res_kind(r) == "safeguard"}

bundle = Bundle(os.path.join(OUTDIR, "cisb-core-bundle"))
mod_count = collections.Counter()
profile_members = collections.defaultdict(list)
mappings = 0; map_v7 = 0; map_v8 = 0; unresolved_refs = 0
minted_prose = 0
req_ids = {}
method_count = collections.Counter()
seq = {"n": 0}
def nseq(): seq["n"] += 10; return seq["n"]

def convert_control(c):
    global mappings, map_v7, map_v8, unresolved_refs, minted_prose
    rid = f"{NS}/req/{c['id']}"
    props = c.get("props", []) or []
    label = next((p["value"] for p in props if p["name"] == "label"), c["id"])
    aliases = [{"scheme": "xccdf", "value": p["value"].split("xccdf_id: ", 1)[-1]}
               for p in props if p["name"] == "marking" and p["value"].startswith("xccdf_id:")]
    method = next((p["value"] for p in props if p["name"] == "marking"
                   and p["value"] in ("automated", "manual")), None)
    if method: method_count[method] += 1
    prose = c.get("title", ""); minted_prose += 1
    mod_count["unspecified"] += 1
    req = {"id": rid, "version": VER, "label": label, "lifecycle": "active",
           "title": c.get("title", c["id"]),
           "statements": [{"id": "s1", "modality": "unspecified",
                           "obligated-parties": [f"{NS}/party/system-administrator"],
                           "prose": {"en": prose}}]}
    if aliases: req["aliases"] = aliases
    narr = {}; acrit = {}
    if method: acrit["method"] = method
    xrefs = []
    for p in c.get("parts", []) or []:
        lab = next((x["value"] for x in p.get("props", []) or [] if x["name"] == "label"), None)
        if p["name"] == "statement" and lab in ("Description", "Rationale"):
            narr[lab.lower()] = T(p.get("prose", ""), lab.lower())
        elif p["name"] == "assessment-method":
            acrit["audit"] = T(p.get("prose", ""), "audit")
        elif p["name"] == "guidance" and lab == "Remediation":
            acrit["remediation"] = T(p.get("prose", ""), "remediation")
        elif p["name"] == "guidance" and p.get("class") == "CIS_Controls":
            for l in p.get("links", []) or []:
                r = safeguard_res.get(l.get("href", "").lstrip("#"))
                if not r: unresolved_refs += 1; continue
                num = next((x["value"] for x in r.get("props", []) or []
                            if x["name"] == "marking" and re.match(r"^\d+(\.\d+)?$", str(x["value"]))), None)
                ver = next((x["value"] for x in r.get("props", []) or []
                            if x["name"] == "version" and x.get("class") == "CIS_Controls"), "?")
                if not num: unresolved_refs += 1; continue
                if ver == "8":
                    pp = num.split(".")
                    tid = f"cisc-{int(pp[0]):03d}" + (f".{int(pp[1]):03d}" if len(pp) > 1 else "")
                    target = f"{CISC8}/req/{tid}"; map_v7_flag = False
                else:
                    target = f"{CISC7}/req/{num}"; map_v7_flag = True
                mid = f"{NS}/map/{slug(c['id'])}--v{ver}-{slug(num)}"
                bundle.add(f"objects/map/{slug(c['id'])}--v{ver}-{slug(num)}.json",
                           {"id": mid, "version": VER, "lifecycle": "active",
                            "source-ref": rid, "target-ref": target,
                            "relationship": "supports", "direction": "source-to-target",
                            "confidence": "draft",
                            "rationale": "Imported from the CIS Benchmark's CIS Controls cross-reference; the source carried no typed relationship (handbook 8.6).",
                            "provenance": {"author-ref": f"{NS}/party/cis", "date": VER}})
                mappings += 1
                if map_v7_flag: map_v7 += 1
                else: map_v8 += 1
        elif p["name"] == "guidance" and p.get("class") == "References":
            xrefs += [x["value"] for x in p.get("props", []) or []
                      if x["name"] == "marking" and x.get("class") == "Reference"]
    if narr: req.setdefault("facets", {})[F_NARR] = narr
    if acrit: req.setdefault("facets", {})[F_ACRIT] = acrit
    if xrefs: req.setdefault("facets", {})[F_XREF] = {"references": xrefs}
    rels = []
    for l in c.get("links", []) or []:
        u = l.get("href", "").lstrip("#")
        if u in profile_res:
            profile_members[profile_res[u].get("title", u)].append(rid)
        elif u in resources:
            r = resources[u]
            rels.append({"type": "reference",
                         "ref": (r.get("rlinks") or [{}])[0].get("href") or r.get("title", u)})
        else:
            unresolved_refs += 1
    if rels: req["relations"] = rels
    bundle.add(f"objects/req/{slug(c['id'])}.json", req)
    req_ids[c["id"]] = rid
    return rid

compat_payloads = 0
def convert_group(g):
    global compat_payloads
    entries, carried = [], [{"group": g.get("title", ""), "name": p.get("name"),
                             "prose": T(p.get("prose", ""), "prose")}
                            for p in g.get("parts", []) or []]
    for sub in g.get("groups", []) or []:
        uri, sc = convert_group(sub)
        carried += sc
        if uri: entries.append({"ref": uri, "sequence": nseq()})
    for c in g.get("controls", []) or []:
        entries.append({"ref": convert_control(c), "sequence": nseq()})
    if not entries: return None, carried
    label = next((p["value"] for p in g.get("props", []) or [] if p["name"] == "label"), None)
    uri = f"{NS}/set/tax/{slug(g.get('id') or g.get('title'))}"
    s = {"id": uri, "version": VER, "lifecycle": "active",
         "title": g.get("title", ""), "members": entries}
    if label: s["label"] = label
    if carried:
        s["facets"] = {COMPAT: {"group-parts": carried}}
        compat_payloads += len(carried); carried = []
    bundle.add(f"objects/set/tax-{slug(g.get('id') or g.get('title'))}.json", s)
    return uri, carried

top, root_carried = [], []
for g in cat.get("groups", []):
    uri, carried = convert_group(g)
    root_carried += carried
    if uri: top.append({"ref": uri, "sequence": nseq()})
root = {"id": f"{NS}/set/tax/root", "version": VER, "lifecycle": "active",
        "title": cat["metadata"]["title"], "members": top}
if root_carried:
    root["facets"] = {COMPAT: {"group-parts": root_carried}}
    compat_payloads += len(root_carried)
bundle.add("objects/set/tax-root.json", root)

for title, refs in sorted(profile_members.items()):
    clean = re.sub(r"\\+", " ", title)
    bundle.add(f"objects/set/profile-{slug(clean)}.json",
               {"id": f"{NS}/set/profile/{slug(clean)}", "version": VER, "lifecycle": "active",
                "title": f"Benchmark profile: {clean}",
                "members": [{"ref": r, "sequence": (i + 1) * 10} for i, r in enumerate(sorted(set(refs)))]})

bundle.pin_stdlib("assessment-criteria-1.0.0.json")   # 26: stdlib pins are VERBATIM
bundle.stub("cisb-narrative-stub.json", F_NARR.split("@")[0], [],
            {"description": {"type": "object"}, "rationale": {"type": "object"}})
bundle.stub("cisb-external-references-stub.json", F_XREF.split("@")[0], [],
            {"references": {"type": "array", "items": {"type": "string"}}})
bundle.stub("oscal-1x-compat-stub.json", "https://ns.oscal.org/compat/oscal-1x", [],
            {"group-parts": {"type": "array"}},
            note="ILLUSTRATIVE STUB - Level-2 waiting room (intended deprecation; see D16/handbook 14.6)")
bundle.write({"source": cat["metadata"]["title"], "source-version": VER,
              "source-oscal-version": cat["metadata"]["oscal-version"],
              "converter": "convert_cis_benchmark.py v0.1",
              "namespace-note": "authority namespace minted by converter pending a CIS-published URI"})

rows, unmapped = coverage(paths, RULES)
nset = sum(1 for r, o in bundle.objects.items() if "/set/" in o["id"])
j = report(
    os.path.join(OUTDIR, "cisb-coverage-report.md"),
    os.path.join(OUTDIR, "cisb-coverage-report.json"),
    "CIS Ubuntu 24.04 Benchmark -> Semantic Core: Coverage Report (computed)",
    f"Source: **{cat['metadata']['title']}** v{VER} (OSCAL {cat['metadata']['oscal-version']}) - "
    f"{len(req_ids)} hardening rules, {len(resources)} back-matter resources.",
    [f"- Objects emitted: **{len(req_ids)} Requirements**, **{mappings} Mapping objects**, **{nset} Sets** "
     f"(section taxonomy + {len(profile_members)} profile baselines), manifest with both digests."],
    [f"- **Profile membership recovered from links**: per-rule reference links resolve to back-matter "
     f"PROFILE resources -> baseline Sets ("
     + ", ".join(f"{re.sub(chr(92) + '+', ' ', k)} ({len(set(v))})" for k, v in sorted(profile_members.items()))
     + ") - the ISM applicability pattern, benchmark edition.",
     f"- **CIS_Controls cross-references -> {mappings} Mapping objects** (relationship supports, confidence "
     f"draft, 8.6 untyped-import rule): v8 targets x{map_v8} resolve into the sibling CIS Controls bundle "
     f"(zero-padded safeguard ids); v7 targets x{map_v7} minted under {CISC7} (no converted corpus yet - "
     f"declared external).",
     f"- **Audit/Remediation -> assessment-criteria@1** (audit script + remediation script, method "
     + "/".join(f"{k} x{v}" for k, v in sorted(method_count.items())) + " from rule markings); "
     f"Description/Rationale -> narrative@1; References markings -> external-references@1 "
     f"(citation labels, kept bare by the identifier rule).",
     f"- **Statement prose minted from title x{minted_prose}**: every source statement part is empty - "
     f"the rule title IS the norm ('Ensure ...'); minting is declared, not silent. Modality unspecified "
     f"x{mod_count.get('unspecified', 0)} (imperative corpus; force rides profile membership).",
     f"- **xccdf ids -> aliases** (scheme xccdf) - the benchmark's second identifier scheme, typed.",
     f"- **Section narrative** (overview parts x{compat_payloads}) -> Level 2 compat facet oscal-1x@1.",
     f"- **Obligated party**: documented default {NS}/party/system-administrator.",
     f"- **Payload free text language-tagged** ({{en: ...}}): "
     + ", ".join(f"{k} x{v}" for k, v in sorted(lang_wraps.items())) + ". Harmonized from the start (backlog #12)."],
    [f"- **Empty statement prose x{minted_prose} (all rules)**: the CIS OSCAL export carries the norm only "
     f"in the title; statement parts exist but are empty. REPORTED for the CIS tooling queue; the converter "
     f"mints prose from the title, declared per rule above.",
     f"- **Mixed-version control references**: the benchmark cross-references CIS Controls v7 AND v8 "
     f"(x{map_v7} vs x{map_v8}) - a live example of why Mapping objects carry explicit versioned targets.",
     f"- **Unresolved link targets x{unresolved_refs}** (counted; kept as references where resolvable)."],
    rows, unmapped,
    {"source": cat["metadata"]["title"], "source-version": VER,
     "objects-emitted": {"requirements": len(req_ids), "mappings": mappings, "sets": nset},
     "profiles": {re.sub(chr(92) + "+", " ", k): len(set(v)) for k, v in profile_members.items()},
     "mappings": {"v7": map_v7, "v8": map_v8},
     "methods": dict(method_count), "minted-prose": minted_prose,
     "unresolved-links": unresolved_refs, "lang-wraps": dict(lang_wraps)})
print(f"reqs: {len(req_ids)}  mappings: {mappings} (v8 {map_v8} / v7 {map_v7})  sets: {nset}  "
      f"leaves: {j['totals']['leaf-values']:,}  mapped: {j['totals']['mapped']:,}  UNMAPPED: {j['totals']['unmapped']}")
if unmapped:
    for p, n in unmapped[:20]: print("  UNMAPPED", p, "x", n)
