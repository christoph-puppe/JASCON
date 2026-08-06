#!/usr/bin/env python3
"""CIS Controls v8.1 (OSCAL catalog) -> Semantic Core bundle.
18 Controls + 153 Safeguards -> Requirements (safeguards individually
addressable because IG baselines bind at safeguard level); per-control
taxonomy Sets; IG1/2/3 -> baseline Sets; asset-class / security-function ->
category Sets; assessment-objectives -> assessment-criteria@1; required
links -> typed relations; references resolved via back-matter. Target: 0."""
import json, os, re, collections
from oscal_conv_lib import make_T, slug, Bundle, inventory, coverage, walk_controls, report

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SRC = os.path.join(ROOT, "sources", "CIS Controls.json")
OUTDIR = os.path.join(ROOT, "converted_examples", "CIS.Controls")
NS = "https://ns.cisecurity.org/controls/v8"   # minted by converter; pending a CIS-published URI
F_ACRIT = "https://ns.oscal.org/stdlib/facet/assessment-criteria@1"
F_NARR = f"{NS}/facet/narrative@1"

lang_wraps = collections.Counter()
T = make_T("en", lang_wraps)

cat = json.load(open(SRC, encoding="utf-8"))["catalog"]
VER = cat["metadata"]["version"]

paths = collections.Counter()
def norm(p):
    return p
inventory({"catalog": cat}, "cisc", paths, norm)

C = r"^cisc\.catalog\.groups\[\]\.controls\[\](\.controls\[\])?"
RULES = [
 (r"^cisc\.catalog\.(uuid|metadata\.)", "L1", "bundle manifest / L0 provenance"),
 (r"^cisc\.catalog\.groups\[\]\.(id|title)$", "L1", "root Set id/title"),
 (C + r"\.id$", "L1", "Requirement id (URI mint) + per-control taxonomy Set id"),
 (C + r"\.title$", "L1", "Requirement title"),
 (C + r"\.parts\[\](\.parts\[\])?\.(id|name)$", "L1", "part dispatch: statement -> statements[0]; assessment-objective (incl. nested sub-objectives) -> assessment-criteria@1 objectives[]; example/guidance -> narrative@1"),
 (C + r"\.parts\[\](\.parts\[\])?\.prose$", "L1", "statement -> statements[0].prose.en; objectives/example/guidance -> facet payloads (language-tagged)"),
 (C + r"\.parts\[\]\.links\[\]\.(rel|href)$", "L1", "rel=assessment-for -> assessment-criteria@1 objectives[].assessment-for (resolved to Requirement URI)"),
 (C + r"\.props\[\]\.(name|value|ns)$", "L1",
  "dispatch: label -> Requirement.label; implementation-group -> baseline Sets ig1/ig2/ig3; "
  "asset-class/security-function -> category Sets; frequency -> assessment-criteria@1 cadence; ns absorbed"),
 (C + r"\.links\[\]\.(rel|href)$", "L1",
  "rel=required -> relations required (safeguard URIs); rel=reference -> relations reference (resolved via back-matter)"),
 (r"^cisc\.catalog\.back-matter\.resources\[\]\.(uuid|title|rlinks\[\]\.href)$", "L1",
  "reference resolution table: uuid -> title/URL for relations reference"),
]

bundle = Bundle(os.path.join(OUTDIR, "cisc-core-bundle"))
MODAL = [("must not", "must-not"), ("should not", "should-not"),
         ("must", "must"), ("should", "should"), ("may", "may")]
def modality_of(prose):
    low = " " + re.sub(r"\s+", " ", (prose or "").lower()) + " "
    for w, c in MODAL:
        if f" {w} " in low: return c
    return "unspecified"

resources = {r["uuid"]: r for r in (cat.get("back-matter", {}) or {}).get("resources", [])}
untitled_resources = sum(1 for r in resources.values() if not r.get("title"))

mod_count = collections.Counter()
ig_members = collections.defaultdict(list)
asset_members = collections.defaultdict(list)
func_members = collections.defaultdict(list)
freq_count = collections.Counter()
dangling_required = []
unresolved_refs = 0
req_ids = {}
seq = {"n": 0}
def nseq(): seq["n"] += 10; return seq["n"]

def convert_control(c, is_parent):
    global unresolved_refs
    rid = f"{NS}/req/{c['id']}"
    props = c.get("props", []) or []
    label = next((p["value"] for p in props if p["name"] == "label"), c["id"])
    stmt = next((p for p in c.get("parts", []) or [] if p["name"] == "statement"), {})
    prose = stmt.get("prose", "")
    mod = modality_of(prose); mod_count[mod] += 1
    st = {"id": stmt.get("id", c["id"] + "_stmt").rsplit("_", 1)[-1], "modality": mod,
          "obligated-parties": [f"{NS}/party/enterprise"], "prose": {"en": prose}}
    freq = next((p["value"] for p in props if p["name"] == "frequency"), None)
    if freq: freq_count[freq] += 1
    req = {"id": rid, "version": VER, "label": label, "lifecycle": "active",
           "title": c.get("title", c["id"]), "statements": [st]}
    def objective(p):
        o = {"id": p.get("id", "").rsplit("_", 1)[-1], "prose": T(p.get("prose", ""), "objective")}
        af = next((l["href"] for l in p.get("links", []) or [] if l.get("rel") == "assessment-for"), None)
        if af:
            m = re.match(r"^#(cisc-[0-9.]+)$", af)
            o["assessment-for"] = f"{NS}/req/{m.group(1)}" if m else af
        subs = [objective(s) for s in p.get("parts", []) or [] if s["name"] == "assessment-objective"]
        if subs: o["objectives"] = subs
        return o
    objectives = [objective(p) for p in c.get("parts", []) or [] if p["name"] == "assessment-objective"]
    ac = {}
    if objectives: ac["objectives"] = objectives
    if freq: ac["frequency"] = freq
    if ac:
        req.setdefault("facets", {})[F_ACRIT] = ac
    narr = {}
    for p in c.get("parts", []) or []:
        if p["name"] in ("example", "guidance"):
            narr.setdefault(p["name"], []).append(T(p.get("prose", ""), p["name"]))
    if narr:
        req.setdefault("facets", {})[F_NARR] = narr
    rels = []
    for l in c.get("links", []) or []:
        href = l.get("href", "")
        if l.get("rel") == "required":
            m = re.match(r"^#(cisc-[0-9.]+)$", href)
            if m: rels.append({"type": "required", "ref": f"{NS}/req/{m.group(1)}"})
            else: dangling_required.append((c["id"], href))
        elif l.get("rel") == "reference":
            r = resources.get(href.lstrip("#"))
            if r:
                target = (r.get("rlinks") or [{}])[0].get("href") or r.get("title", "")
                rels.append({"type": "reference", "ref": target})
            else:
                rels.append({"type": "reference", "ref": href}); unresolved_refs += 1
    if rels: req["relations"] = rels
    for p in props:
        if p["name"] == "implementation-group": ig_members[p["value"]].append(rid)
        elif p["name"] == "asset-class": asset_members[p["value"]].append(rid)
        elif p["name"] == "security-function": func_members[p["value"]].append(rid)
    bundle.add(f"objects/req/{slug(c['id'])}.json", req)
    req_ids[c["id"]] = rid
    return rid

root_members = []
parents_without_ig = []
for g in cat.get("groups", []):
    for c in g.get("controls", []) or []:
        prid = convert_control(c, True)
        if not any(p["name"] == "implementation-group" for p in c.get("props", []) or []):
            parents_without_ig.append(c["id"])
        entries = [{"ref": prid, "sequence": nseq()}]
        for sub in c.get("controls", []) or []:
            entries.append({"ref": convert_control(sub, False), "sequence": nseq()})
        suri = f"{NS}/set/tax/{slug(c['id'])}"
        bundle.add(f"objects/set/tax-{slug(c['id'])}.json",
                   {"id": suri, "version": VER, "lifecycle": "active",
                    "title": c.get("title", c["id"]), "members": entries})
        root_members.append({"ref": suri, "sequence": nseq()})
bundle.add("objects/set/tax-root.json",
           {"id": f"{NS}/set/tax/root", "version": VER, "lifecycle": "active",
            "title": cat["metadata"]["title"], "members": root_members})

for ig, refs in sorted(ig_members.items()):
    bundle.add(f"objects/set/baseline-ig{ig}.json",
               {"id": f"{NS}/set/baseline/ig{ig}", "version": VER, "lifecycle": "active",
                "title": f"Implementation Group {ig}",
                "members": [{"ref": r, "sequence": (i + 1) * 10} for i, r in enumerate(sorted(set(refs)))]})
for kind, mem in [("asset", asset_members), ("function", func_members)]:
    for v, refs in sorted(mem.items()):
        bundle.add(f"objects/set/{kind}-{slug(v)}.json",
                   {"id": f"{NS}/set/tax/{kind}-{slug(v)}", "version": VER, "lifecycle": "active",
                    "title": f"{'Asset class' if kind == 'asset' else 'Security function'}: {v}",
                    "members": [{"ref": r, "sequence": (i + 1) * 10} for i, r in enumerate(sorted(set(refs)))]})

# cumulativity check: IG1 subset of IG2 subset of IG3
s1, s2, s3 = (set(ig_members.get(k, [])) for k in ("1", "2", "3"))
cumulative_ok = s1 <= s2 <= s3

bundle.pin_stdlib("assessment-criteria-1.0.0.json")   # 26: stdlib pins are VERBATIM
bundle.stub("cis-narrative-stub.json", F_NARR.split("@")[0], [],
            {"example": {"type": "array"}, "guidance": {"type": "array"}})
bundle.write({"source": cat["metadata"]["title"], "source-version": VER,
              "source-oscal-version": cat["metadata"]["oscal-version"],
              "converter": "convert_cis_controls.py v0.1",
              "namespace-note": "authority namespace minted by converter pending a CIS-published URI"})

rows, unmapped = coverage(paths, RULES)
nset = sum(1 for r, o in bundle.objects.items() if "/set/" in o["id"])
parents = [i for i in req_ids if "." not in i]
j = report(
    os.path.join(OUTDIR, "cisc-coverage-report.md"),
    os.path.join(OUTDIR, "cisc-coverage-report.json"),
    "CIS Controls v8.1 -> Semantic Core: Coverage Report (computed)",
    f"Source: **CIS Controls** v{VER} (OSCAL {cat['metadata']['oscal-version']}) - "
    f"{len(parents)} Controls + {len(req_ids) - len(parents)} Safeguards.",
    [f"- Objects emitted: **{len(req_ids)} Requirements** ({len(parents)} Controls + "
     f"{len(req_ids) - len(parents)} Safeguards), **{nset} Sets** (per-control taxonomy + root + "
     f"3 IG baselines + {len(asset_members)} asset-class + {len(func_members)} security-function), "
     f"manifest with both digests."],
    [f"- **Safeguards are Requirements, not statements** - IG baselines bind at safeguard level, and Set "
     f"members reference objects, never statements (the membership argument decides the granularity).",
     f"- **Modality word-rule**: " + ", ".join(f"{k} x{v}" for k, v in sorted(mod_count.items(), key=lambda x: -x[1]))
     + ". CIS prose is imperative ('Establish and maintain ...'): modal verbs are structurally absent; "
     f"binding force rides IG membership (the ISM pattern, third confirmation).",
     f"- **implementation-group -> baseline Sets** ig1 ({len(s1)}) / ig2 ({len(s2)}) / ig3 ({len(s3)}); "
     f"declared cumulative in-source: **{'holds' if cumulative_ok else 'VIOLATED'}** (checked, not assumed).",
     f"- **asset-class / security-function -> category Sets** ("
     + ", ".join(f"{k} {len(set(v))}" for k, v in sorted(asset_members.items())) + " | "
     + ", ".join(f"{k} {len(set(v))}" for k, v in sorted(func_members.items())) + ").",
     f"- **frequency -> assessment-criteria@1 `frequency`** (assessment cadence, gate-2 schema alignment - "
     f"a fixed stipulation is not an insertion point, so it is facet payload, not a parameter): "
     + ", ".join(f"{k} x{v}" for k, v in sorted(freq_count.items(), key=lambda x: -x[1]))
     + ". Typed-duration mapping deferred: 'bi-annually' is lexically ambiguous (two readings); a code "
     f"is the honest encoding until CIS defines the period (candidate authors'-queue item).",
     f"- **assessment-objective parts -> assessment-criteria@1** objectives[] (top-level x"
     + str(sum(len(o['facets'][F_ACRIT]['objectives']) for o in bundle.objects.values()
               if o.get('facets', {}).get(F_ACRIT)))
     + ", nested sub-objectives carried recursively; per-safeguard `assessment-for` links resolved to "
     f"Requirement URIs); example/guidance -> narrative@1.",
     f"- **links rel=required -> typed relations** (safeguard dependencies; dangling x{len(dangling_required)}); "
     f"rel=reference resolved via back-matter ({len(resources)} resources, untitled x{untitled_resources}, "
     f"unresolved x{unresolved_refs}).",
     f"- **Payload free text language-tagged** ({{en: ...}}): "
     + ", ".join(f"{k} x{v}" for k, v in sorted(lang_wraps.items())) + ". Harmonized from the start (backlog #12).",
     f"- **Obligated party**: documented default {NS}/party/enterprise (CIS binds 'the enterprise' implicitly)."],
    [f"- **Controls carry no implementation-group** (x{len(parents_without_ig)}: all {len(parents)} parents): IG "
     f"membership exists only at safeguard level - a consumer selecting 'IG1' gets safeguards, never the "
     f"parent prose; parent Requirements ride along via the taxonomy Sets. Structural fact, REPORTED.",
     f"- **IG cumulativity measured**: IG1 < IG2 < IG3 {'holds exactly' if cumulative_ok else 'is violated'} "
     f"({len(s1)}/{len(s2)}/{len(s3)}).",
     f"- Declarative/imperative corpus #3: unspecified x{mod_count.get('unspecified', 0)} of {len(req_ids)} - "
     f"the ISM finding generalizes (imperative English, force via membership)."],
    rows, unmapped,
    {"source": cat["metadata"]["title"], "source-version": VER,
     "objects-emitted": {"requirements": len(req_ids), "sets": nset},
     "modality-word-rule": dict(mod_count),
     "ig-baselines": {k: len(set(v)) for k, v in ig_members.items()},
     "ig-cumulative": cumulative_ok,
     "asset-classes": {k: len(set(v)) for k, v in asset_members.items()},
     "security-functions": {k: len(set(v)) for k, v in func_members.items()},
     "frequency": dict(freq_count), "parents-without-ig": parents_without_ig,
     "dangling-required": dangling_required, "unresolved-references": unresolved_refs,
     "lang-wraps": dict(lang_wraps)})
print(f"reqs: {len(req_ids)}  sets: {nset}  leaves: {j['totals']['leaf-values']:,}  "
      f"mapped: {j['totals']['mapped']:,}  UNMAPPED: {j['totals']['unmapped']}")
if unmapped:
    for p, n in unmapped[:20]: print("  UNMAPPED", p, "x", n)
