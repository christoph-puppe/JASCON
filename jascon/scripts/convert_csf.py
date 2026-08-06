#!/usr/bin/env python3
"""NIST CSF 2.0 (OSCAL catalog) -> Semantic Core bundle.
Census: drafts/gate-3-census.md §3/§6 (2026-07-22). 6 functions + 34
categories -> Sets (the C5 rule: membership decides granularity; category
statement prose -> narrative facet on the Set); 94 live subcategories ->
Requirements (outcome prose, modality `unspecified` - sixth-corpus
confirmation of the declarative pattern); 91 withdrawn (1.1->2.0
restructuring) dropped, lineage inverted onto successor `replaces[]`;
implementation examples -> examples@1; risk-party -> csf@1.
Coverage target: 0."""
import json, os, re, collections
from oscal_conv_lib import make_T, slug, Bundle, inventory, coverage, report, walk_controls

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SRC = os.path.join(ROOT, "sources", "nist", "NIST_CSF_v2.0_catalog.json")
OUTDIR = os.path.join(ROOT, "converted_examples", "US.CSF")
NS = "https://ns.nist.gov/csf"          # no version in the URI - lineage is D2's job
F_NARR = f"{NS}/facet/narrative@1"
F_EX = f"{NS}/facet/examples@1"
F_CSF = f"{NS}/facet/csf@1"
F_REF = f"{NS}/facet/references@1"

lang_wraps = collections.Counter()
T = make_T("en", lang_wraps)

cat = json.load(open(SRC, encoding="utf-8"))["catalog"]
VER = "2.0"          # framework version; the OSCAL rendition's doc version rides provenance

def norm(p):
    p = re.sub(r"(\.controls\[\])+", ".controls[]", p)
    p = re.sub(r"(\.parts\[\])+", ".parts[]", p)
    return p

paths = collections.Counter()
inventory({"catalog": cat}, "csf", paths, normalize=norm)

def prop(c, name, all_=False):
    out = [p for p in c.get("props", []) or [] if p.get("name") == name]
    return out if all_ else (out[0] if out else None)

def mint(src_id):
    return f"{NS}/req/{src_id}"

controls = list(walk_controls(cat))
by_id = {c["id"]: c for c, _, _ in controls}
withdrawn = {c["id"] for c, _, _ in controls
             if prop(c, "status") and prop(c, "status")["value"] == "withdrawn"}

# ---------- withdrawal inversion (underscore rels - the census 7.1 finding) ----------
MODE = {"incorporated_into": "merged-into", "moved_to": "renamed"}
groups_by_id = {g["id"]: g for g in cat.get("groups", []) or []}
succ_replaces = collections.defaultdict(list)
fn_replaces = collections.defaultdict(list)     # function-level successor (ID.GV -> GV)
wd_chain, wd_dangling = [], []
n_hashless = 0
for c, _, _ in controls:
    if c["id"] not in withdrawn: continue
    for l in c.get("links", []) or []:
        rel, href = l.get("rel"), (l.get("href") or "")
        if rel not in MODE: continue
        if not href.startswith("#"): n_hashless += 1   # DE.DP-04: fragment marker missing (source finding)
        href = href.lstrip("#")
        lab = prop(c, "label")
        st = next((p for p in c.get("parts", []) or [] if p.get("name") == "statement"), {})
        e = {"ref": mint(c["id"]), "mode": MODE[rel],
             "label": lab["value"] if lab else c["id"], "title": c.get("title", "")}
        if st.get("prose"):        # CSF tombstones keep their 1.1 outcome prose - carry it
            e["prose"] = st["prose"]
        if href in withdrawn:
            wd_chain.append((c["id"], href)); continue
        if href in by_id:
            succ_replaces[href].append(e)
        elif href in groups_by_id:
            fn_replaces[href].append(e)
        else:
            wd_dangling.append((c["id"], href))

# ---------- convert ----------
bundle = Bundle(os.path.join(OUTDIR, "csf-core-bundle"))
mod_count = collections.Counter()
req_ids = {}
n_examples = n_riskparty = 0

def statement_prose(c):
    st = next((p for p in c.get("parts", []) or [] if p.get("name") == "statement"), {})
    return st.get("prose", ""), st.get("id", f"{c['id']}_statement")

def facets_of(c):
    global n_examples, n_riskparty
    f = {}
    ex = [{"id": p.get("id"), "prose": T(p.get("prose", ""), "example")}
          for p in c.get("parts", []) or [] if p.get("name") == "example"]
    if ex:
        f[F_EX] = {"examples": ex}; n_examples += len(ex)
    rp = prop(c, "risk-party")
    if rp:
        f[F_CSF] = {"risk-party": {"value": rp["value"],
                                   **({"remark": rp["remarks"]} if rp.get("remarks") else {})}}
        n_riskparty += 1
    return f

def convert_subcat(c):
    prose, sid = statement_prose(c)
    rid = mint(c["id"])
    lab = prop(c, "label")
    req = {"id": rid, "version": VER, "label": lab["value"] if lab else c["id"],
           "lifecycle": "active", "title": c.get("title", c["id"]),
           "statements": [{"id": sid[len(c["id"]) + 1:] if sid.startswith(c["id"] + "_") else sid,
                           "modality": "unspecified",
                           "obligated-parties": [f"{NS}/party/organization"],
                           "prose": {"en": prose}}]}
    mod_count["unspecified"] += 1
    f = facets_of(c)
    if f: req["facets"] = f
    if succ_replaces.get(c["id"]):
        entries = succ_replaces[c["id"]]
        req["replaces"] = [{"ref": e["ref"], "mode": e["mode"]} for e in entries]
        req["annotations"] = {"nist-withdrawal": [dict(e) for e in entries]}
    bundle.add(f"objects/req/{slug(c['id'])}.json", req)
    req_ids[c["id"]] = rid
    return rid

def sortkey(x):
    sk = prop(x, "sort-id")
    return sk["value"] if sk else x["id"]

root_members = []
cat_sets = 0
wd_categories = [c["id"] for g in cat.get("groups", []) or []
                 for c in g.get("controls", []) or [] if c["id"] in withdrawn]
wd_subcats = [s["id"] for g in cat.get("groups", []) or [] for c in g.get("controls", []) or []
              for s in c.get("controls", []) or [] if s["id"] in withdrawn]
for g in sorted(cat.get("groups", []) or [], key=sortkey):
    fn_members = []
    for c in sorted(g.get("controls", []) or [], key=sortkey):
        if c["id"] in withdrawn:      # withdrawn category: dropped, lineage inverted like any tombstone
            orphans = [s["id"] for s in c.get("controls", []) or [] if s["id"] not in withdrawn]
            if orphans:               # live subcats under a withdrawn category would be data loss - guard
                raise SystemExit(f"live subcategories under withdrawn category {c['id']}: {orphans}")
            continue
        # category: a Set; its statement prose -> narrative facet on the Set
        prose, _ = statement_prose(c)
        suri = f"{NS}/set/category/{slug(c['id'])}"
        subs = [s for s in c.get("controls", []) or []]
        members = [{"ref": convert_subcat(s), "sequence": (i + 1) * 10}
                   for i, s in enumerate(sorted(subs, key=sortkey)) if s["id"] not in withdrawn]
        # withdrawn subcats: lineage already inverted; drop from membership
        lab = prop(c, "label")
        sobj = {"id": suri, "version": VER, "lifecycle": "active",
                "title": c.get("title", c["id"]), "label": lab["value"] if lab else c["id"],
                "members": members}
        fx = {}
        if prose: fx[F_NARR] = {"guidance": [T(prose, "category-statement")]}
        fx.update(facets_of(c))
        if fx: sobj["facets"] = fx
        if succ_replaces.get(c["id"]):
            entries = succ_replaces[c["id"]]
            sobj["replaces"] = [{"ref": e["ref"], "mode": e["mode"]} for e in entries]
            sobj["annotations"] = {"nist-withdrawal": [dict(e) for e in entries]}
        bundle.add(f"objects/set/category-{slug(c['id'])}.json", sobj)
        cat_sets += 1
        fn_members.append({"ref": suri, "sequence": len(fn_members) * 10 + 10})
    furi = f"{NS}/set/function/{slug(g['id'])}"
    lab = prop(g, "label")
    fobj = {"id": furi, "version": VER, "lifecycle": "active",
            "title": g.get("title", g["id"]), "label": lab["value"] if lab else g["id"],
            "members": fn_members}
    over = [p for p in g.get("parts", []) or [] if p.get("name") == "overview"]
    if over:
        fobj["facets"] = {F_NARR: {"guidance": [T(p.get("prose", ""), "overview") for p in over]}}
    if fn_replaces.get(g["id"]):                 # ID.GV "moved to GV": function-level successor
        entries = fn_replaces[g["id"]]
        fobj["replaces"] = [{"ref": e["ref"], "mode": e["mode"]} for e in entries]
        fobj["annotations"] = {"nist-withdrawal": [dict(e) for e in entries]}
    bundle.add(f"objects/set/function-{slug(g['id'])}.json", fobj)
    root_members.append({"ref": furi, "sequence": len(root_members) * 10 + 10})

RES = [{"title": r.get("title", ""), "url": (r.get("rlinks") or [{}])[0].get("href", "")}
       for r in cat.get("back-matter", {}).get("resources", []) or []]
bundle.add("objects/set/root.json",
           {"id": f"{NS}/set/root", "version": VER, "lifecycle": "active",
            "title": cat["metadata"]["title"], "members": root_members,
            "facets": {F_REF: {"resources": RES}}})

bundle.stub("csf-narrative-stub.json", F_NARR.split("@")[0], [], {"guidance": {"type": "array"}})
bundle.stub("csf-examples-stub.json", F_EX.split("@")[0], [], {"examples": {"type": "array"}})
bundle.stub("csf-stub.json", F_CSF.split("@")[0], [], {"risk-party": {"type": "object"}})
bundle.stub("csf-references-stub.json", F_REF.split("@")[0], [], {"resources": {"type": "array"}})
bundle.write({"source": cat["metadata"]["title"], "source-version": VER,
              "source-doc-version": cat["metadata"]["version"],
              "source-oscal-version": cat["metadata"]["oscal-version"],
              "published": cat["metadata"].get("published"),
              "converter": "convert_csf.py v0.1",
              "namespace-note": "https://ns.nist.gov/csf minted by converter (no version in the URI; "
                                "lineage is D2's job) pending a NIST-published URI"})

# ---------- coverage ----------
RULES = [
 (r"^csf\.catalog\.(uuid$|metadata\.)", "L1", "bundle manifest / L0 provenance"),
 (r"^csf\.catalog\.back-matter\.", "L1", "references@1 facet on the root Set (title/url)"),
 (r"^csf\.catalog\.groups\[\]\.(id|class|title)$", "L1", "function Set id/title"),
 (r"^csf\.catalog\.groups\[\]\.props\[\]\.(name|value)$", "L1", "function Set label; sort-id -> member order"),
 (r"^csf\.catalog\.groups\[\]\.parts\[\]\.(id|name|prose)$", "L2",
  "function overview -> narrative@1 guidance on the function Set (language-tagged)"),
 (r"^csf\.catalog\.groups\[\]\.controls\[\]\.(id|class|title)$", "L1",
  "category Set / subcategory Requirement id (URI mint) + title | withdrawn: dropped, lineage inverted"),
 (r"^csf\.catalog\.groups\[\]\.controls\[\]\.props\[\]\.(name|value|ns)$", "L1",
  "label->label; sort-id->Set sequence; risk-party->csf@1; status->tombstone drop + successor replaces[]"),
 (r"^csf\.catalog\.groups\[\]\.controls\[\]\.props\[\]\.remarks$", "L2",
  "risk-party remark -> csf@1 (carried verbatim)"),
 (r"^csf\.catalog\.groups\[\]\.controls\[\]\.links\[\]\.(href|rel)$", "L1",
  "incorporated_into/moved_to (UNDERSCORE spelling - source finding) -> successor replaces[] "
  "(merged-into/renamed) + nist-withdrawal annotation"),
 (r"^csf\.catalog\.groups\[\]\.controls\[\]\.parts\[\]\.(id|name|ns|prose)$", "L1",
  "subcategory statement -> statements[0] (modality unspecified); category statement -> narrative@1 on "
  "the Set; example parts -> examples@1 (language-tagged)"),
]
rows, unmapped = coverage(paths, RULES)

nset = sum(1 for rel in bundle.objects if "/set/" in rel)
j = report(
    os.path.join(OUTDIR, "csf-coverage-report.md"),
    os.path.join(OUTDIR, "csf-coverage-report.json"),
    "NIST CSF 2.0 -> Semantic Core: Coverage Report (computed)",
    f"Source: **{cat['metadata']['title']}** framework v{VER} (OSCAL rendition "
    f"{cat['metadata']['version']}, OSCAL {cat['metadata']['oscal-version']}). "
    f"Census: `drafts/gate-3-census.md` §3/§6.",
    [f"- Objects emitted: **{len(req_ids)} Requirements** (subcategories), **{nset} Sets** "
     f"(6 functions + {cat_sets} categories + root), manifest with both digests."],
    [f"- **Functions and categories are Sets, subcategories are Requirements** - the C5 rule "
     f"(membership decides granularity), D21 taxonomy nesting at 3 levels.",
     f"- **Category statement prose -> narrative@1 on the category Set** - summary prose, not an "
     f"obligation; the requirement surface is the subcategory layer.",
     f"- **Modality `unspecified` x{mod_count['unspecified']}**: CSF outcomes are declarative "
     f"('Outcomes ... are understood and communicated') - sixth-corpus confirmation of the national "
     f"declarative pattern; force rides adoption, not mood.",
     f"- **Withdrawn tombstones dropped, lineage inverted**: {len(withdrawn)} withdrawn "
     f"({len(wd_categories)} categories + {len(wd_subcats)} subcategories - the 1.1->2.0 restructuring "
     f"cut at BOTH levels), {sum(len(v) for v in succ_replaces.values())} successor edges on "
     f"Requirements/Sets + {sum(len(v) for v in fn_replaces.values())} on function Sets (ID.GV 'moved to "
     f"GV' - the sa-12->SR pattern) (incorporated_into->merged-into, moved_to->renamed); tombstone 1.1 "
     f"outcome prose carried in the annotation (CSF titles are bare ids - the prose IS the content); "
     f"chains x{len(wd_chain)}, dangling x{len(wd_dangling)}; no live subcategory sits under a withdrawn "
     f"category (asserted).",
     f"- **Implementation examples -> examples@1** x{n_examples} (ids kept - the CSF example numbering "
     f"is citable); **risk-party -> csf@1** x{n_riskparty} (remarks carried).",
     f"- **Obligated party**: documented default {NS}/party/organization (CSF binds the adopting "
     f"organization).",
     f"- **Payload free text language-tagged**: " + ", ".join(f"{k} x{v}" for k, v in sorted(lang_wraps.items())) + "."],
    [f"- **Rel-code spelling divergence (source finding)**: CSF 2.0 uses `incorporated_into`/`moved_to` "
     f"(underscores) where SP 800-53 Rev 5 uses `incorporated-into`/`moved-to` (hyphens) - same "
     f"publisher, same semantic, two spellings. REPORTED upstream.",
     f"- **Fragment marker missing x{n_hashless}** (source finding): DE.DP-04's successor href is "
     f"`DE.AE-06` (a relative URI reference) where every sibling writes `#DE.AE-06` - resolves only by "
     f"lenient parsing. REPORTED upstream.",
     f"- **{len(withdrawn)} of 219 controls are withdrawn tombstones** ({len(wd_categories)} categories, "
     f"{len(wd_subcats)} subcategories) - the catalog carries its 1.1-restructuring residue in-band; the "
     f"successor graph (`replaces[]`) carries the full migration map.",
     f"- Declarative corpus #6: unspecified x{mod_count['unspecified']} of {len(req_ids)} - CSF states "
     f"outcomes; obligation is an adoption artifact (baseline Sets in profiles), exactly the "
     f"ISM/CIS/CyFun/C5 pattern."],
    rows, unmapped,
    {"source-version": VER,
     "objects-emitted": {"requirements": len(req_ids), "sets": nset},
     "withdrawn": {"count": len(withdrawn), "categories": wd_categories, "subcategories": len(wd_subcats),
                   "successor-edges": sum(len(v) for v in succ_replaces.values()),
                   "function-set-edges": sum(len(v) for v in fn_replaces.values()),
                   "hashless-hrefs": n_hashless,
                   "chains": wd_chain, "dangling": wd_dangling},
     "modality": dict(mod_count), "examples": n_examples, "risk-party": n_riskparty,
     "lang-wraps": dict(lang_wraps)})
print(f"reqs: {len(req_ids)}  sets: {nset}  leaves: {j['totals']['leaf-values']:,}  "
      f"mapped: {j['totals']['mapped']:,}  UNMAPPED: {j['totals']['unmapped']}")
print(f"withdrawn: {len(withdrawn)}  edges: {sum(len(v) for v in succ_replaces.values())}  "
      f"chains: {len(wd_chain)}  dangling: {len(wd_dangling)}")
if unmapped:
    for p, n in unmapped[:30]: print("  UNMAPPED", p, "x", n)
