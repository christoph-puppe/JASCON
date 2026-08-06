#!/usr/bin/env python3
"""CyberFundamentals (Belgium, CCB) -> Semantic Core bundle.
Reads BOTH resolved catalogs (BASIC + ESSENTIAL) as one corpus: ESSENTIAL is
the requirement superset; BASIC contributes membership evidence and a
twin-catalog drift check (shared ids compared part-by-part - the GS++/MS-TLS
lesson applied preventively). Levels become cumulative baseline Sets;
key-measures / governance-measures become marker Sets. Coverage target: 0."""
import json, os, re, collections
from oscal_conv_lib import make_T, slug, Bundle, inventory, coverage, walk_controls, report

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SRC_B = os.path.join(ROOT, "sources", "CyFun 2025 BASIC Resolved.json")
SRC_E = os.path.join(ROOT, "sources", "CyFun 2025 ESSENTIAL Resolved.json")
OUTDIR = os.path.join(ROOT, "converted_examples", "BE.CyFun")
NS = "https://ns.ccb.belgium.be/cyfun"   # minted by converter; pending an authority URI
COMPAT = "https://ns.oscal.org/compat/oscal-1x@1"

lang_wraps = collections.Counter()
T = make_T("en", lang_wraps)

cb = json.load(open(SRC_B, encoding="utf-8"))["catalog"]
ce = json.load(open(SRC_E, encoding="utf-8"))["catalog"]
VER = ce["metadata"]["version"]

# ---------- inventory (both files, one corpus) ----------
def norm(p):
    return re.sub(r"^cyfun\.(basic|essential)\.", "cyfun.*.", p)
paths = collections.Counter()
inventory({"basic": {"catalog": cb}}, "cyfun", paths, norm)
inventory({"essential": {"catalog": ce}}, "cyfun", paths, norm)

G = r"(\.groups\[\])+"
RULES = [
 (r"^cyfun\.\*\.catalog\.(uuid|metadata\.(title|version|last-modified|oscal-version|links\[\].*|props\[\].*|document-ids\[\].*))$",
  "L1", "bundle manifest / L0 provenance (incl. resolution-tool note; document-ids -> aliases on the root Set)"),
 (rf"^cyfun\.\*\.catalog{G}\.id$", "L1", "Set id"),
 (rf"^cyfun\.\*\.catalog{G}\.title$", "L1", "Set title"),
 (rf"^cyfun\.\*\.catalog{G}\.props\[\]\.(name|value)$", "L1",
  "group props: label -> Set label; sort-id absorbed by document order -> members[].sequence"),
 (rf"^cyfun\.\*\.catalog{G}\.parts\[\]\.(id|name|prose)$", "L2",
  "compat facet oscal-1x@1: function/category overview narrative on the Set (language-tagged {en})"),
 (rf"^cyfun\.\*\.catalog{G}\.controls\[\]\.id$", "L1", "Requirement id (URI mint) + label"),
 (rf"^cyfun\.\*\.catalog{G}\.controls\[\]\.title$", "L1", "Requirement title"),
 (rf"^cyfun\.\*\.catalog{G}\.controls\[\]\.parts\[\]\.(id|name|prose)$", "L1",
  "statements[0] (id suffix, prose.en + modality word-rule over shall-language)"),
 (rf"^cyfun\.\*\.catalog{G}\.controls\[\]\.props\[\]\.(name|value|ns)$", "L1",
  "dispatch: label -> Requirement.label; sort-id absorbed -> sequence; assurance-level -> "
  "cumulative baseline Sets; key-measures/governance-measures -> marker Sets; ns absorbed"),
]

# ---------- conversion (ESSENTIAL = superset corpus) ----------
MODAL = [("shall not", "must-not"), ("must not", "must-not"), ("should not", "should-not"),
         ("shall", "must"), ("must", "must"), ("should", "should"), ("may", "may")]
def modality_of(prose):
    low = " " + re.sub(r"\s+", " ", (prose or "").lower()) + " "
    for w, c in MODAL:
        if f" {w} " in low: return c
    return "unspecified"

bundle = Bundle(os.path.join(OUTDIR, "cyfun-core-bundle"))
mod_count = collections.Counter()
level_members = collections.defaultdict(list)
markers = collections.defaultdict(list)
dup_level_props = []
req_ids = {}
seq = {"n": 0}
def nseq(): seq["n"] += 10; return seq["n"]

def props_of(c):
    return {p["name"]: [q["value"] for q in c.get("props", []) or [] if q["name"] == p["name"]]
            for p in c.get("props", []) or []}

def convert_control(c):
    rid = f"{NS}/req/{c['id']}"
    pr = props_of(c)
    if len(pr.get("assurance-level", [])) > 1:
        dup_level_props.append((c["id"], pr["assurance-level"]))
    part = (c.get("parts") or [{}])[0]
    prose = part.get("prose", "")
    mod = modality_of(prose); mod_count[mod] += 1
    req = {"id": rid, "version": VER, "label": pr.get("label", [c["id"]])[0],
           "lifecycle": "active", "title": c.get("title", c["id"]),
           "statements": [{"id": part.get("id", c["id"] + "_smt").rsplit("_", 1)[-1],
                           "modality": mod,
                           "obligated-parties": [f"{NS}/party/organisation"],
                           "prose": {"en": prose}}]}
    for lv in pr.get("assurance-level", []): level_members[lv].append(rid)
    for m in ("key-measures", "governance-measures"):
        if pr.get(m, ["false"])[0] == "true": markers[m].append(rid)
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
        uri, sub_carried = convert_group(sub)
        carried += sub_carried
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
for g in ce.get("groups", []):
    uri, carried = convert_group(g)
    root_carried += carried
    if uri: top.append({"ref": uri, "sequence": nseq()})
root = {"id": f"{NS}/set/tax/root", "version": VER, "lifecycle": "active",
        "title": "CyberFundamentals 2025", "members": top}
doc_ids = [{"scheme": di.get("scheme", ""), "value": di.get("identifier", "")}
           for di in ce["metadata"].get("document-ids", []) or []]
if doc_ids: root["aliases"] = doc_ids
if root_carried:
    root["facets"] = {COMPAT: {"group-parts": root_carried}}
    compat_payloads += len(root_carried)
bundle.add("objects/set/tax-root.json", root)

# cumulative baseline Sets: basic < important < essential
CUM = {"basic": ["basic"], "important": ["basic", "important"],
       "essential": ["basic", "important", "essential"]}
for name, levels in CUM.items():
    refs = [r for lv in levels for r in level_members.get(lv, [])]
    bundle.add(f"objects/set/baseline-{name}.json",
               {"id": f"{NS}/set/baseline/{name}", "version": VER, "lifecycle": "active",
                "title": f"CyFun assurance level: {name.upper()} (cumulative)",
                "members": [{"ref": r, "sequence": (i + 1) * 10} for i, r in enumerate(sorted(set(refs)))]})
for m, refs in sorted(markers.items()):
    bundle.add(f"objects/set/marker-{m}.json",
               {"id": f"{NS}/set/marker/{m}", "version": VER, "lifecycle": "active",
                "title": f"CyFun marker: {m}",
                "members": [{"ref": r, "sequence": (i + 1) * 10} for i, r in enumerate(sorted(set(refs)))]})

# ---------- twin check: BASIC file vs ESSENTIAL file ----------
def ctrl_index(cat): return {c["id"]: c for c, _, _ in walk_controls(cat)}
bi, ei = ctrl_index(cb), ctrl_index(ce)
shared = sorted(set(bi) & set(ei))
drift = [i for i in shared if bi[i].get("parts") != ei[i].get("parts") or bi[i].get("title") != ei[i].get("title")]
basic_only = sorted(set(bi) - set(ei))
basic_level_in_basic_file = sorted(i for i in bi
    if "basic" in [p["value"] for p in bi[i].get("props", []) or [] if p["name"] == "assurance-level"])
membership_mismatch = sorted(set(bi) - set(basic_level_in_basic_file))

bundle.stub("oscal-1x-compat-stub.json", "https://ns.oscal.org/compat/oscal-1x", [],
            {"group-parts": {"type": "array", "items": {"type": "object", "properties": {
                "group": {"type": "string"}, "name": {"type": "string"},
                "prose": {"type": "object", "additionalProperties": {"type": "string"}}}}}},
            note="ILLUSTRATIVE STUB - Level-2 waiting room (intended deprecation; see D16/handbook 14.6)")

manifest = bundle.write({"source": "CCB CyberFundamentals 2025 - resolved catalogs BASIC + ESSENTIAL (Comply0 resolution)",
                         "source-version": VER, "source-oscal-version": ce["metadata"]["oscal-version"],
                         "converter": "convert_cyfun.py v0.1",
                         "namespace-note": "authority namespace minted by converter pending a CCB-published URI"})

rows, unmapped = coverage(paths, RULES)
nset = sum(1 for r in bundle.objects if "/set/" in bundle.objects[r]["id"])
j = report(
    os.path.join(OUTDIR, "cyfun-coverage-report.md"),
    os.path.join(OUTDIR, "cyfun-coverage-report.json"),
    "CyFun (BASIC + ESSENTIAL) -> Semantic Core: Coverage Report (computed)",
    f"Sources: **CyFun 2025 BASIC Resolved** + **CyFun 2025 ESSENTIAL Resolved** v{VER} "
    f"(OSCAL {ce['metadata']['oscal-version']}, resolved by Comply0) - one corpus, two membership levels.",
    [f"- Objects emitted: **{len(req_ids)} Requirements**, **{nset} Sets** "
     f"(taxonomy + 3 cumulative baselines + {len(markers)} marker Sets), manifest with both digests."],
    [f"- **Modality word-rule** over shall-language statements (shall->must per ISO convention): "
     + ", ".join(f"{k} x{v}" for k, v in sorted(mod_count.items(), key=lambda x: -x[1])) + ".",
     f"- **ESSENTIAL is the requirement superset** ({len(ei)} controls); BASIC ({len(bi)}) contributes "
     f"membership evidence only - no duplicate objects, no twin ids (the GS++/MS-TLS lesson applied preventively).",
     f"- **assurance-level -> cumulative baseline Sets** basic ({len(set(level_members['basic']))}) < important "
     f"(+{len(set(level_members['important']))}) < essential (+{len(set(level_members['essential']))}); "
     f"key-measures ({len(markers.get('key-measures', []))}) and governance-measures "
     f"({len(markers.get('governance-measures', []))}) -> marker Sets.",
     f"- **Group narrative** (overview parts x{compat_payloads}) -> Level 2 compat facet oscal-1x@1 on the "
     f"nearest Set (ISM pattern); residue KPI starts at {compat_payloads}.",
     f"- **Obligated party**: documented default {NS}/party/organisation (CyFun binds the organisation implicitly).",
     f"- **Payload free text language-tagged** per corpus language ({{en: ...}}): "
     + ", ".join(f"{k} x{v}" for k, v in sorted(lang_wraps.items())) + ". Harmonized from the start (backlog #12).",
     f"- `sort-id` absorbed by document order -> members[].sequence; `label` props -> kernel labels; "
     f"cyfun.eu prop namespace absorbed (kernel fields need none)."],
    [f"- **Twin-catalog check (preventive): {len(shared)} shared ids, {len(shared) - len(drift)} identical, "
     f"drift {len(drift)}** - " + ("no silent divergence between the two published resolutions; the corpse "
     "stayed dead." if not drift else f"DRIFTED: {drift}"),
     f"- **BASIC-only controls: {len(basic_only)}** (memberships beyond ESSENTIAL would be a resolution defect): "
     + (str(basic_only) if basic_only else "none."),
     f"- **Duplicated assurance-level props x{len(dup_level_props)}**: {dup_level_props} - one control carries "
     f"two level declarations; REPORTED for the CCB/tooling queue (source defect class: duplicated prop).",
     f"- **BASIC-file membership vs. declared level**: {len(membership_mismatch)} controls sit in the BASIC "
     f"resolution without carrying assurance-level=basic: {membership_mismatch} - membership and level "
     f"declaration disagree; REPORTED (the applicability-vs-profile split, CyFun edition).",
     f"- **Declarative/imperative modality**: unspecified x{mod_count.get('unspecified', 0)} of {len(req_ids)} - "
     f"binding force rides the assurance-level baseline Sets where prose carries no modal verb (ISM pattern)."],
    rows, unmapped,
    {"source": "CyFun 2025 BASIC+ESSENTIAL", "source-version": VER,
     "objects-emitted": {"requirements": len(req_ids), "sets": nset},
     "modality-word-rule": dict(mod_count),
     "levels": {k: len(set(v)) for k, v in level_members.items()},
     "markers": {k: len(v) for k, v in markers.items()},
     "twin-check": {"shared": len(shared), "drift": drift, "basic-only": basic_only},
     "dup-assurance-level-props": dup_level_props,
     "basic-membership-vs-level-mismatch": membership_mismatch,
     "lang-wraps": dict(lang_wraps)})
print(f"reqs: {len(req_ids)}  sets: {nset}  leaves: {j['totals']['leaf-values']:,}  "
      f"mapped: {j['totals']['mapped']:,}  UNMAPPED: {j['totals']['unmapped']}")
if unmapped:
    for p, n in unmapped[:20]: print("  UNMAPPED", p, "x", n)
