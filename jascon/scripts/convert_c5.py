#!/usr/bin/env python3
"""BSI C5:2026 (OSCAL catalog) -> Semantic Core bundle.
18 domains -> Sets; 168 criteria -> taxonomy Sets (corresponding-requirements
prose -> c5/corresponding@1, the CRM evidence); 623 class children ->
Requirements; class -> membership Sets (basic baseline, additional-sharpen,
additional-complement); sharpened-basic-criterion -> typed `sharpens`
relation; 6 title-only `gc-undefined` stubs -> parked L2 + defect finding.
Coverage target: 0."""
import json, os, re, collections
from oscal_conv_lib import make_T, slug, Bundle, inventory, coverage, report

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SRC = os.path.join(ROOT, "sources", "c5-2026-oscal-catalog.json")
OUTDIR = os.path.join(ROOT, "converted_examples", "DE.C5")
NS = "https://ns.bsi.bund.de/c5"   # minted by converter; pending a BSI-published URI
F_CORR = f"{NS}/facet/corresponding@1"
F_NARR = f"{NS}/facet/narrative@1"
COMPAT = "https://ns.oscal.org/compat/oscal-1x@1"

lang_wraps = collections.Counter()
T = make_T("en", lang_wraps)

cat = json.load(open(SRC, encoding="utf-8"))["catalog"]
VER = cat["metadata"]["version"]

paths = collections.Counter()
inventory({"catalog": cat}, "c5", paths)

RULES = [
 (r"^c5\.catalog\.(uuid|metadata\.)", "L1", "bundle manifest / L0 provenance"),
 (r"^c5\.catalog\.groups\[\]\.(id|title)$", "L1", "domain Set id/title"),
 (r"^c5\.catalog\.groups\[\]\.controls\[\]\.(id|title)$", "L1",
  "criterion Set id/title (parents) | parked-L2 stub titles (gc-undefined defect class)"),
 (r"^c5\.catalog\.groups\[\]\.controls\[\]\.class$", "L1", "criterion class (rare on parents; recorded)"),
 (r"^c5\.catalog\.groups\[\]\.controls\[\]\.parts\[\]\.(id|name|title|prose)$", "L1",
  "corresponding parts -> c5/corresponding@1 on the criterion Set (customer-side duties; CRM evidence; language-tagged)"),
 (r"^c5\.catalog\.groups\[\]\.controls\[\]\.controls\[\]\.(id|title)$", "L1",
  "Requirement id (URI mint) + label derivation + title"),
 (r"^c5\.catalog\.groups\[\]\.controls\[\]\.controls\[\]\.class$", "L1",
  "class -> membership Sets: baseline/basic | tax/additional-sharpen | tax/additional-complement"),
 (r"^c5\.catalog\.groups\[\]\.controls\[\]\.controls\[\]\.parts\[\]\.(id|name|prose)$", "L1",
  "statement -> statements[0].prose.en; guidance(-N) -> narrative@1 guidance[] (language-tagged)"),
 (r"^c5\.catalog\.groups\[\]\.controls\[\]\.controls\[\]\.props\[\]\.(name|value)$", "L1",
  "sharpened-basic-criterion -> typed relation `sharpens` -> sibling basic criterion URI"),
]

bundle = Bundle(os.path.join(OUTDIR, "c5-core-bundle"))
MODAL = [("must not", "must-not"), ("shall not", "must-not"), ("should not", "should-not"),
         ("shall", "must"), ("must", "must"), ("should", "should"), ("may", "may")]
def modality_of(prose):
    low = " " + re.sub(r"\s+", " ", (prose or "").lower()) + " "
    for w, c in MODAL:
        if f" {w} " in low: return c
    return "unspecified"

mod_count = collections.Counter()
class_members = collections.defaultdict(list)
sharpens_ok, sharpens_broken, sharpens_missing = [], [], []
req_ids = {}
undefined_stubs = []
seq = {"n": 0}
def nseq(): seq["n"] += 10; return seq["n"]

def convert_child(c, parent_id):
    rid = f"{NS}/req/{c['id']}"
    stmt = next((p for p in c.get("parts", []) or [] if p["name"] == "statement"), {})
    prose = stmt.get("prose", "")
    mod = modality_of(prose); mod_count[mod] += 1
    req = {"id": rid, "version": VER, "label": c["id"].upper(), "lifecycle": "active",
           "title": c.get("title", c["id"]),
           "statements": [{"id": stmt.get("id", c["id"] + "_stmt").rsplit("_", 1)[-1],
                           "modality": mod,
                           "obligated-parties": [f"{NS}/party/cloud-service-provider"],
                           "prose": {"en": prose}}]}
    guid = [T(p.get("prose", ""), "guidance") for p in c.get("parts", []) or [] if p["name"].startswith("guidance")]
    if guid:
        req["facets"] = {F_NARR: {"guidance": guid}}
    cls = c.get("class", "unclassed")
    class_members[cls].append(rid)
    sharp = next((p["value"] for p in c.get("props", []) or []
                  if p["name"] == "sharpened-basic-criterion"), None)
    if sharp:
        target = f"{parent_id}-{sharp.lower()}"
        turi = f"{NS}/req/{target}"
        req.setdefault("relations", []).append({"type": f"{NS}/rel/sharpens", "ref": turi})  # #20: extension rels are URI-typed
        (sharpens_ok if True else sharpens_broken).append((c["id"], target))
    elif cls == "additional-sharpen":
        sharpens_missing.append(c["id"])
    bundle.add(f"objects/req/{slug(c['id'])}.json", req)
    req_ids[c["id"]] = rid
    return rid

root_members = []
for g in cat.get("groups", []):
    dom_members = []
    parked = []
    for c in g.get("controls", []) or []:
        subs = c.get("controls", []) or []
        if not subs and not c.get("class") and not c.get("parts"):
            undefined_stubs.append((g["id"], c["id"], c.get("title", "")))
            parked.append({"id": c["id"], "title": c.get("title", "")})
            continue
        entries = [{"ref": convert_child(s, c["id"]), "sequence": nseq()} for s in subs]
        suri = f"{NS}/set/criterion/{slug(c['id'])}"
        sobj = {"id": suri, "version": VER, "lifecycle": "active",
                "title": c.get("title", c["id"]), "label": c["id"].upper(),
                "members": entries}
        corr = [p for p in c.get("parts", []) or [] if p["name"] == "corresponding"]
        if corr:
            sobj["facets"] = {F_CORR: {"customer-requirements":
                [{"title": p.get("title", ""), "prose": T(p.get("prose", ""), "corresponding")} for p in corr]}}
        if not subs:
            convert_child(c, c["id"])   # class-bearing leaf without children (if any)
            continue
        bundle.add(f"objects/set/criterion-{slug(c['id'])}.json", sobj)
        dom_members.append({"ref": suri, "sequence": nseq()})
    duri = f"{NS}/set/domain/{slug(g['id'])}"
    dobj = {"id": duri, "version": VER, "lifecycle": "active",
            "title": g.get("title", g["id"]), "label": g["id"].upper(), "members": dom_members}
    if parked:
        dobj["facets"] = {COMPAT: {"undefined-items": parked}}
    bundle.add(f"objects/set/domain-{slug(g['id'])}.json", dobj)
    root_members.append({"ref": duri, "sequence": nseq()})
bundle.add("objects/set/root.json",
           {"id": f"{NS}/set/root", "version": VER, "lifecycle": "active",
            "title": cat["metadata"]["title"], "members": root_members})

SETNAMES = {"basic": ("baseline/basic", "C5 Basic Criteria (baseline)"),
            "additional-sharpen": ("tax/additional-sharpen", "C5 Additional Criteria - sharpening"),
            "additional-complement": ("tax/additional-complement", "C5 Additional Criteria - complementing"),
            "unclassed": ("tax/unclassed", "C5 criteria without class (recorded)")}
for cls, refs in sorted(class_members.items()):
    sub, title = SETNAMES.get(cls, (f"tax/{slug(cls)}", f"C5 class: {cls}"))
    bundle.add(f"objects/set/{slug(sub)}.json",
               {"id": f"{NS}/set/{sub}", "version": VER, "lifecycle": "active", "title": title,
                "members": [{"ref": r, "sequence": (i + 1) * 10} for i, r in enumerate(sorted(set(refs)))]})

# verify sharpens targets exist
sharpens_broken = [(cid, t) for cid, t in sharpens_ok if t not in req_ids]
sharpens_ok = [(cid, t) for cid, t in sharpens_ok if t in req_ids]

bundle.stub("c5-corresponding-stub.json", F_CORR.split("@")[0], [],
            {"customer-requirements": {"type": "array"}})
bundle.stub("c5-narrative-stub.json", F_NARR.split("@")[0], [], {"guidance": {"type": "array"}})
bundle.stub("oscal-1x-compat-stub.json", "https://ns.oscal.org/compat/oscal-1x", [],
            {"undefined-items": {"type": "array"}},
            note="ILLUSTRATIVE STUB - Level-2 waiting room (intended deprecation; see D16/handbook 14.6)")
bundle.write({"source": cat["metadata"]["title"], "source-version": VER,
              "source-oscal-version": cat["metadata"]["oscal-version"],
              "published": cat["metadata"].get("published"),
              "converter": "convert_c5.py v0.1",
              "namespace-note": "authority namespace minted by converter pending a BSI-published URI"})

rows, unmapped = coverage(paths, RULES)
nset = sum(1 for r, o in bundle.objects.items() if "/set/" in o["id"])
j = report(
    os.path.join(OUTDIR, "c5-coverage-report.md"),
    os.path.join(OUTDIR, "c5-coverage-report.json"),
    "C5:2026 -> Semantic Core: Coverage Report (computed)",
    f"Source: **{cat['metadata']['title']}** v{VER} (OSCAL {cat['metadata']['oscal-version']}, "
    f"published {cat['metadata'].get('published', '?')[:10]}).",
    [f"- Objects emitted: **{len(req_ids)} Requirements**, **{nset} Sets** (18 domains + "
     f"{sum(1 for o in bundle.objects.values() if '/set/criterion/' in o['id'])} criteria + root + "
     f"{len(class_members)} class Sets), manifest with both digests."],
    [f"- **Criteria are Sets, class children are Requirements** - the basic/additional split binds per "
     f"child, so membership decides granularity (the CIS-safeguard argument, second confirmation).",
     f"- **class -> membership Sets**: " + ", ".join(f"{k} ({len(set(v))})" for k, v in sorted(class_members.items()))
     + "; Basic is the certification baseline Set.",
     f"- **Modality word-rule**: " + ", ".join(f"{k} x{v}" for k, v in sorted(mod_count.items(), key=lambda x: -x[1]))
     + ". C5 prose is declarative present tense ('The cloud service provider maintains ...') - the ISM "
     f"pattern, fourth corpus confirmation; force rides the class Sets.",
     f"- **sharpened-basic-criterion -> typed `sharpens` relation**: resolved x{len(sharpens_ok)}, "
     f"broken targets x{len(sharpens_broken)}; sharpen-class children WITHOUT the pointer prop "
     f"x{len(sharpens_missing)} ({sharpens_missing}).",
     f"- **corresponding parts (x{sum(1 for o in bundle.objects.values() if o.get('facets', {}).get(F_CORR))}) -> "
     f"c5/corresponding@1** on the criterion Set: customer-side duties - measured CRM evidence for the "
     f"shared-responsibility model (handbook ch09).",
     f"- **guidance(-N) parts -> narrative@1** guidance[] (children with 2+ guidance parts exist; all carried).",
     f"- **Obligated party**: documented default {NS}/party/cloud-service-provider (C5 binds the provider; "
     f"customer duties live in the corresponding facet, deliberately NOT as obligated-parties).",
     f"- **Payload free text language-tagged** ({{en: ...}}): "
     + ", ".join(f"{k} x{v}" for k, v in sorted(lang_wraps.items())) + ". Harmonized from the start (backlog #12)."],
    [f"- **Defective source ids: 6 x `gc-undefined`** - six title-only stubs in the GC group share one id "
     f"(an id collision inside a single authoritative publication; the twin-catalog corpse in miniature). "
     f"Parked as a Level-2 compat payload on the GC domain Set, REPORTED for the C5 authors' queue: "
     + "; ".join(t[:60] for _, _, t in undefined_stubs) + ".",
     f"- **Sharpening pointer gap x{len(sharpens_missing)}**: {sharpens_missing} is additional-sharpen class "
     f"but carries no sharpened-basic-criterion prop - the machine-readable sharpening graph has one "
     f"missing edge; REPORTED.",
     f"- Declarative corpus #4: unspecified x{mod_count.get('unspecified', 0)} of {len(req_ids)} - "
     f"convergent with ISM/CIS/CyFun-partial: national frameworks state duties declaratively and bind "
     f"force via membership."],
    rows, unmapped,
    {"source": cat["metadata"]["title"], "source-version": VER,
     "objects-emitted": {"requirements": len(req_ids), "sets": nset},
     "modality-word-rule": dict(mod_count),
     "class-sets": {k: len(set(v)) for k, v in class_members.items()},
     "sharpens": {"resolved": len(sharpens_ok), "broken": sharpens_broken, "missing-prop": sharpens_missing},
     "gc-undefined-stubs": [{"group": g, "id": i, "title": t} for g, i, t in undefined_stubs],
     "lang-wraps": dict(lang_wraps)})
print(f"reqs: {len(req_ids)}  sets: {nset}  leaves: {j['totals']['leaf-values']:,}  "
      f"mapped: {j['totals']['mapped']:,}  UNMAPPED: {j['totals']['unmapped']}")
if unmapped:
    for p, n in unmapped[:20]: print("  UNMAPPED", p, "x", n)
