#!/usr/bin/env python3
"""BSI C3A (Criteria enabling Cloud Computing Autonomy) -> Semantic Core.
GS++ grammar family (modal_verb / action_word / result props, sec_level,
effort_level, tags, alt-identifier, typed params): 30 criteria in 6 SOV
domains. First converter to use the D9-rev first-class parameter
`label` + `default` - the param-extras residue class never opens here.
Coverage target: 0."""
import json, os, re, collections
from oscal_conv_lib import make_T, slug, Bundle, inventory, coverage, report

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SRC = os.path.join(ROOT, "sources", "c3a_oscal_catalog.json")
OUTDIR = os.path.join(ROOT, "converted_examples", "DE.C3A")
NS = "https://ns.bsi.bund.de/c3a"   # minted by converter; pending a BSI-published URI
F_GRAM = "https://ns.oscal.org/stdlib/facet/statement-grammar@1"
F_TAX = f"{NS}/facet/taxonomy@1"
F_NARR = f"{NS}/facet/narrative@1"
COMPAT = "https://ns.oscal.org/compat/oscal-1x@1"

lang_wraps = collections.Counter()
T = make_T("de", lang_wraps)

cat = json.load(open(SRC, encoding="utf-8"))["catalog"]
VER = cat["metadata"]["version"]

paths = collections.Counter()
inventory({"catalog": cat}, "c3a", paths)

CTL = r"^c3a\.catalog\.groups\[\]\.controls\[\]"
RULES = [
 (r"^c3a\.catalog\.(uuid|metadata\.)", "L1", "bundle manifest / L0 provenance (roles/parties -> publisher identity)"),
 (r"^c3a\.catalog\.groups\[\]\.(id|title)$", "L1", "domain Set id/title"),
 (CTL + r"\.(id|title|class)$", "L1", "Requirement id (URI mint) + title; class -> category Set"),
 (CTL + r"\.params\[\]\.(id|label|values\[\])$", "L1",
  "parameter {name, type string, label, default} - D9-rev first-class label/default (no param-extras residue)"),
 (CTL + r"\.params\[\]\.props\[\]\.(name|value|ns)$", "L2",
  "compat param-extras: parameter alt-identifier uuid (no kernel home on parameters; declared waiting room)"),
 (CTL + r"\.props\[\]\.(name|value|ns)$", "L1",
  "dispatch: alt-identifier -> aliases (scheme bsi-uuid); sec_level -> baseline Set; effort_level/tags -> "
  "taxonomy@1; CSV-link namespaces absorbed (pinned stubs replace them)"),
 (CTL + r"\.parts\[\]\.(id|name)$", "L1", "statement -> statements[0]; guidance -> narrative@1"),
 (CTL + r"\.parts\[\]\.prose$", "L1", "statements[0].prose.de | narrative guidance (language-tagged)"),
 (CTL + r"\.parts\[\]\.props\[\]\.(name|value|ns)$", "L1",
  "grammar props (modal_verb -> statements[0].modality via code map; action_word/result -> statement-grammar@1 by-statement)"),
]

MODAL = {"MUSS": "must", "DARF NICHT": "must-not", "MUSS NICHT": "must-not",
         "SOLLTE": "should", "SOLLTE NICHT": "should-not", "KANN": "may", "DARF NUR": "may-only"}

bundle = Bundle(os.path.join(OUTDIR, "c3a-core-bundle"), lang="de")
mod_count = collections.Counter()
sec_members = collections.defaultdict(list)
class_members = collections.defaultdict(list)
multi_modal = []
fused_variants = []
multi_value_params = []
req_ids = {}
seq = {"n": 0}
def nseq(): seq["n"] += 10; return seq["n"]

def convert_control(c):
    rid = f"{NS}/req/{c['id'] if not c['id'][0].isdigit() else 'c-' + c['id']}"
    props = c.get("props", []) or []
    stmt = next((p for p in c.get("parts", []) or [] if p["name"] == "statement"), {})
    prose = stmt.get("prose", "")
    sid = stmt.get("id", c["id"] + "_stm").rsplit("_", 1)[-1].lower()
    modals = [p["value"] for p in stmt.get("props", []) or [] if p["name"] == "modal_verb"]
    if len(modals) > 1: multi_modal.append((c["id"], modals))
    mod = MODAL.get(modals[0], "unspecified") if modals else "unspecified"
    mod_count[mod] += 1
    if re.search(r"\bC1:", prose) and re.search(r"\bC2:", prose):
        fused_variants.append(c["id"])
    st = {"id": sid, "modality": mod,
          "obligated-parties": [f"{NS}/party/cloud-dienstanbieter"],
          "prose": {"de": prose}}
    params = []
    for p in c.get("params", []) or []:
        vals = p.get("values", []) or []
        if len(vals) > 1: multi_value_params.append((c["id"], p["id"]))
        prm = {"name": p["id"].rsplit("-", 1)[-1], "type": "string"}
        if p.get("label"): prm["label"] = p["label"]
        if vals: prm["default"] = vals[0]
        params.append(prm)
    if params: st["parameters"] = params
    req = {"id": rid, "version": VER, "label": c["id"].upper(), "lifecycle": "active",
           "title": c.get("title", c["id"]), "statements": [st]}
    aliases = [{"scheme": "bsi-uuid", "value": p["value"]} for p in props if p["name"] == "alt-identifier"]
    if aliases: req["aliases"] = aliases
    gram = {k: v for k, v in
            [("action-word", next((p["value"] for p in stmt.get("props", []) or [] if p["name"] == "action_word"), None)),
             ("result", next((p["value"] for p in stmt.get("props", []) or [] if p["name"] == "result"), None))]
            if v}
    facets = {}
    if gram: facets[F_GRAM] = {"by-statement": {sid: gram}}
    tax = {}
    for p in props:
        if p["name"] == "effort_level": tax["effort-level"] = p["value"]
        elif p["name"] == "tags": tax["tags"] = [t.strip() for t in p["value"].split(",")]
        elif p["name"] == "sec_level": sec_members[p["value"]].append(rid)
    if tax: facets[F_TAX] = tax
    guid = [T(p.get("prose", ""), "guidance") for p in c.get("parts", []) or [] if p["name"] == "guidance"]
    if guid: facets[F_NARR] = {"guidance": guid}
    pextra = [{"param": p["id"], "alt-identifier": x["value"]}
              for p in c.get("params", []) or [] for x in p.get("props", []) or []
              if x["name"] == "alt-identifier"]
    if pextra: facets[COMPAT] = {"param-extras": pextra}
    if facets: req["facets"] = facets
    class_members[c.get("class", "unclassed")].append(rid)
    bundle.add(f"objects/req/{slug(c['id'])}.json", req)
    req_ids[c["id"]] = rid
    return rid

root_members = []
for g in cat.get("groups", []):
    entries = [{"ref": convert_control(c), "sequence": nseq()} for c in g.get("controls", []) or []]
    duri = f"{NS}/set/domain/{slug(g['id'])}"
    bundle.add(f"objects/set/domain-{slug(g['id'])}.json",
               {"id": duri, "version": VER, "lifecycle": "active",
                "title": g.get("title", g["id"]), "label": g["id"].upper(), "members": entries})
    root_members.append({"ref": duri, "sequence": nseq()})
bundle.add("objects/set/root.json",
           {"id": f"{NS}/set/root", "version": VER, "lifecycle": "active",
            "title": cat["metadata"]["title"], "members": root_members})
for lv, refs in sorted(sec_members.items()):
    bundle.add(f"objects/set/baseline-{slug(lv)}.json",
               {"id": f"{NS}/set/baseline/{slug(lv)}", "version": VER, "lifecycle": "active",
                "title": f"C3A security level: {lv}",
                "members": [{"ref": r, "sequence": (i + 1) * 10} for i, r in enumerate(sorted(set(refs)))]})
for cls, refs in sorted(class_members.items()):
    if cls == "unclassed": continue
    bundle.add(f"objects/set/class-{slug(cls)}.json",
               {"id": f"{NS}/set/tax/class-{slug(cls)}", "version": VER, "lifecycle": "active",
                "title": f"C3A class: {cls}",
                "members": [{"ref": r, "sequence": (i + 1) * 10} for i, r in enumerate(sorted(set(refs)))]})

bundle.pin_stdlib("statement-grammar-1.0.0.json")   # 26: stdlib pins are VERBATIM
bundle.stub("c3a-taxonomy-stub.json", F_TAX.split("@")[0], [],
            {"effort-level": {"type": "string"}, "tags": {"type": "array"}})
bundle.stub("c3a-narrative-stub.json", F_NARR.split("@")[0], [], {"guidance": {"type": "array"}})
bundle.stub("oscal-1x-compat-stub.json", "https://ns.oscal.org/compat/oscal-1x", [],
            {"param-extras": {"type": "array"}},
            note="ILLUSTRATIVE STUB - Level-2 waiting room (intended deprecation; see D16/handbook 14.6)")
bundle.write({"source": cat["metadata"]["title"], "source-version": VER,
              "source-oscal-version": cat["metadata"]["oscal-version"],
              "published": cat["metadata"].get("published"),
              "converter": "convert_c3a.py v0.1",
              "namespace-note": "authority namespace minted by converter pending a BSI-published URI"})

rows, unmapped = coverage(paths, RULES)
nset = sum(1 for r, o in bundle.objects.items() if "/set/" in o["id"])
nparams = sum(len(s.get("parameters", [])) for o in bundle.objects.values()
              for s in o.get("statements", []))
j = report(
    os.path.join(OUTDIR, "c3a-coverage-report.md"),
    os.path.join(OUTDIR, "c3a-coverage-report.json"),
    "C3A -> Semantic Core: Coverage Report (computed)",
    f"Source: **{cat['metadata']['title']}** v{VER} (OSCAL {cat['metadata']['oscal-version']}, "
    f"published {str(cat['metadata'].get('published', '?'))[:10]}) - GS++ grammar family.",
    [f"- Objects emitted: **{len(req_ids)} Requirements** carrying **{nparams} typed parameters**, "
     f"**{nset} Sets**, manifest with both digests."],
    [f"- **Modality from `modal_verb` code map** (GS++ Verbindlichkeitssprache): "
     + ", ".join(f"{k} x{v}" for k, v in sorted(mod_count.items(), key=lambda x: -x[1])) + ".",
     f"- **Parameters carry first-class `label` + `default`** (D9 rev, backlog #1) - the x{nparams} "
     f"params land with labels ('Normreferenzen') and default values in the kernel; the param-extras "
     f"residue class never opens for this corpus (only the parameter alt-identifier uuids wait there, "
     f"x{sum(1 for o in bundle.objects.values() if o.get('facets', {}).get(COMPAT))} objects).",
     f"- **Grammar props -> statement-grammar@1** by-statement (action-word/result); sec_level -> "
     f"baseline Set ({', '.join(f'{k} ({len(set(v))})' for k, v in sorted(sec_members.items()))}); "
     f"effort_level/tags -> c3a/taxonomy@1; alt-identifier -> aliases (scheme bsi-uuid); CSV-link prop "
     f"namespaces absorbed - pinned stubs replace them (the GS++ lesson).",
     f"- **Obligated party**: documented default {NS}/party/cloud-dienstanbieter.",
     f"- **Payload free text language-tagged** per corpus language ({{de: ...}}): "
     + ", ".join(f"{k} x{v}" for k, v in sorted(lang_wraps.items())) + ". Harmonized from the start (backlog #12)."],
    [f"- **Fused class variants x{len(fused_variants)}**: statement prose interleaves 'C1: ... C2: ...' "
     f"cloud-class variants inside ONE statement string ({fused_variants}) - the CR26 varies_by_class "
     f"need, encoded as prose fusion; candidate for statement split or class Tailorings at source. REPORTED.",
     f"- **Multiple modal_verb props on one statement x{len(multi_modal)}**: {multi_modal} - a statement "
     f"carrying two binding strengths is the fusion's machine-readable shadow; converter takes the first, "
     f"declared. REPORTED.",
     f"- **Multi-value params x{len(multi_value_params)}** ({multi_value_params or 'none'}) - first value "
     f"becomes `default`, rest would need `choice`; counted."],
    rows, unmapped,
    {"source": cat["metadata"]["title"], "source-version": VER,
     "objects-emitted": {"requirements": len(req_ids), "sets": nset, "parameters": nparams},
     "modality": dict(mod_count),
     "sec-level-baselines": {k: len(set(v)) for k, v in sec_members.items()},
     "fused-class-variants": fused_variants, "multi-modal-statements": multi_modal,
     "multi-value-params": multi_value_params, "lang-wraps": dict(lang_wraps)})
print(f"reqs: {len(req_ids)}  sets: {nset}  params: {nparams}  leaves: {j['totals']['leaf-values']:,}  "
      f"mapped: {j['totals']['mapped']:,}  UNMAPPED: {j['totals']['unmapped']}")
if unmapped:
    for p, n in unmapped[:20]: print("  UNMAPPED", p, "x", n)
