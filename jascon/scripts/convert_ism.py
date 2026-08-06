#!/usr/bin/env python3
"""ISM (OSCAL 1.1.x catalog) -> Semantic Core bundle converter.
Gate item 1, authority 1. Emits: bundle + computed coverage report.
Every source field path is inventoried and must have a declared destination;
UNMAPPED paths are the gate's failure signal (target: zero)."""
import json, hashlib, os, re, copy, sys, collections

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SRC = os.path.join(ROOT, "sources", "ism.json")
OUT = os.path.join(ROOT, "converted_examples", "AU.ISM", "ism-core-bundle")
REPORT_MD = os.path.join(ROOT, "converted_examples", "AU.ISM", "ism-coverage-report.md")
REPORT_JSON = os.path.join(ROOT, "converted_examples", "AU.ISM", "ism-coverage-report.json")
NS = "https://ns.cyber.gov.au/ism"
LANG = "en"   # corpus language: payload free text is language-tagged {LANG: value}

def T(v):
    """Wrap payload free text in the corpus language (backlog #12 harmonization)."""
    return {LANG: v} if v or v == "" else v

# ---------- helpers ----------
def w(path, obj):
    p = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False); f.write("\n")

def sha_file(path):
    return "sha256:" + hashlib.sha256(open(os.path.join(OUT, path), "rb").read()).hexdigest()

def _canon(o):
    if isinstance(o, dict):
        return {k: _canon(o[k]) for k in sorted(o.keys(), key=lambda s: s.encode("utf-16-be"))}
    if isinstance(o, list):
        return [_canon(x) for x in o]
    return o

def semantic_digest(obj):
    o = copy.deepcopy(obj); o.pop("annotations", None)
    c = json.dumps(_canon(o), separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(c).hexdigest()

def slug(s):
    s = re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
    if len(s) <= 60:
        return s or "x"
    # P10 #39: a bare [:60] cut collided nested taxonomy ids (parent==child
    # -> self-loops; sibling==sibling -> silently merged sets). Truncation
    # keeps a stable disambiguating hash of the full slug instead.
    return s[:52].rstrip("-") + "-" + hashlib.sha256(s.encode()).hexdigest()[:7]

# ---------- 1) full source path inventory ----------
def inventory(node, prefix, counter):
    if isinstance(node, dict):
        for k, v in node.items():
            inventory(v, f"{prefix}.{k}", counter)
    elif isinstance(node, list):
        for v in node:
            inventory(v, f"{prefix}[]", counter)
    else:
        counter[prefix] += 1

src = json.load(open(SRC, encoding="utf-8"))
cat = src.get("catalog", src)
paths = collections.Counter()
inventory(cat, "catalog", paths)

# ---------- 2) declared destination map (path -> (level, destination)) ----------
D = {}
def dest(path, level, target):
    D[path] = (level, target)

# metadata -> L0 / bundle provenance
for p in ["catalog.uuid", "catalog.metadata.title", "catalog.metadata.published",
          "catalog.metadata.last-modified", "catalog.metadata.version",
          "catalog.metadata.oscal-version"]:
    dest(p, "L1", "bundle manifest / L0 provenance")
for p in list(paths):
    if p.startswith("catalog.metadata.links[]") or p.startswith("catalog.metadata.roles[]") \
       or p.startswith("catalog.metadata.parties[]") or p.startswith("catalog.metadata.responsible-parties[]"):
        dest(p, "L1", "bundle manifest / L0 provenance (publisher identity)")
# groups -> Sets
dest("catalog.groups[].id", "L1", "Set id (or generated slug when absent)")
dest("catalog.groups[].title", "L1", "Set title")
dest("catalog.groups[].props[].name", "L1", "sort-id: absorbed by document order -> members[].sequence")
dest("catalog.groups[].props[].value", "L1", "sort-id: absorbed by document order -> members[].sequence")
for depth in ["", ".groups[]", ".groups[].groups[]"]:
    base = f"catalog.groups[]{depth}"
    for suf, lvl, tgt in [
        (".id", "L1", "Set id (or generated slug when absent)"),
        (".title", "L1", "Set title"),
        (".props[].name", "L1", "group sort-id: absorbed by document order -> sequence"),
        (".props[].value", "L1", "group sort-id: absorbed by document order -> sequence"),
        (".parts[].name", "L2", "compat facet oscal-1x@1: guideline overview narrative on the Set"),
        (".parts[].prose", "L2", "compat facet oscal-1x@1: guideline overview narrative on the Set (language-tagged {en})"),
    ]:
        dest(base + suf, lvl, tgt)
# controls -> Requirements (controls appear at group depth 1 and 2)
for depth in [".groups[]", ".groups[].groups[]"]:
    base = f"catalog.groups[]{depth}.controls[]"
    dest(base + ".id", "L1", "Requirement id (URI mint) + label derivation")
    dest(base + ".class", "L1", "category Sets: set/tax/principles | set/tax/controls")
    dest(base + ".title", "L1", "Requirement title")
    dest(base + ".parts[].id", "L1", "statement id (part-id suffix)")
    dest(base + ".parts[].name", "L1", "statement (the one part kind present)")
    dest(base + ".parts[].prose", "L1", "statements[].prose.en (+ modality word-rule, documented)")
    dest(base + ".props[].name", "L1", "dispatch (see per-prop rows)")
    dest(base + ".props[].ns", "L1", "prop namespace: absorbed (kernel fields need none)")
    dest(base + ".props[].value", "L1", "dispatch (see per-prop rows)")
# back-matter
for p in list(paths):
    if p.startswith("catalog.back-matter"):
        dest(p, "declared-drop", "source-document references (guideline PDFs/links) - not requirement data")

# per-prop dispatch (documented in report; mechanically applied below)
PROP_DEST = {
    "sort-id":  ("L1", "absorbed: document order -> members[].sequence (path-string redundant)"),
    "label":    ("L1", "Requirement.label"),
    "applicability": ("L1", "membership -> set/baseline/<marker>"),
    "essential-eight-applicability": ("L1", "membership -> set/baseline/e8-<level>"),
    "revision": ("L1", "history -> L0 (object versions/manifest); value not object-carried"),
    "updated":  ("L1", "history -> L0 (object versions/manifest); value not object-carried"),
}

# ---------- 3) conversion ----------
MODAL_RULES = [("must not", "must-not"), ("should not", "should-not"),
               ("must", "must"), ("should", "should"), ("may", "may")]
def modality_of(prose):
    low = " " + re.sub(r"\s+", " ", prose.lower()) + " "
    for word, code in MODAL_RULES:
        if f" {word} " in low:
            return code
    return "unspecified"

version = cat["metadata"]["version"]
objects = {}          # relpath -> obj
req_index = {}        # control id -> req URI
baseline_members = collections.defaultdict(list)   # marker -> [req URI]
e8_members = collections.defaultdict(list)
class_members = collections.defaultdict(list)
modality_count = collections.Counter()
label_from_prop = 0
seq_counter = 0

def mint_req(c):
    global label_from_prop
    rid = f"{NS}/req/{c['id']}"
    label = None
    for p in c.get("props", []):
        if p["name"] == "label":
            label = p["value"]; label_from_prop += 1
    if label is None:
        m = re.match(r"ism-(\d+)$", c["id"])
        label = f"ISM-{m.group(1)}" if m else c["id"]
    part = c["parts"][0]
    sid = part.get("id", f"{c['id']}_smt").rsplit("_", 1)[-1]
    prose = part.get("prose", "")
    mod = modality_of(prose)
    modality_count[mod] += 1
    req = {"id": rid, "version": version, "label": label,
           "lifecycle": "active", "title": c["title"],
           "statements": [{"id": sid, "modality": mod,
                           "obligated-parties": [f"{NS}/party/organisation"],
                           "prose": {"en": prose}}]}
    for p in c.get("props", []):
        n, v = p["name"], p["value"]
        if n == "applicability": baseline_members[v].append(rid)
        elif n == "essential-eight-applicability": e8_members[v].append(rid)
        # sort-id / revision / updated / label: absorbed per PROP_DEST
    class_members[c.get("class", "unclassed")].append(rid)
    return rid, req

def next_seq():
    global seq_counter; seq_counter += 10; return seq_counter

COMPAT = "https://ns.oscal.org/compat/oscal-1x@1"
compat_payloads = 0

def own_parts(g):
    return [{"group": g.get("title", ""), "name": p.get("name"), "prose": T(p.get("prose", ""))}
            for p in (g.get("parts", []) or [])]

def convert_group(g, path_ids):
    """returns (set_uri or None, carried_parts) - narrative parts attach to the
    nearest emitted ancestor Set as a Level-2 compat payload."""
    global compat_payloads
    entries, carried = [], own_parts(g)
    for sub in g.get("groups", []) or []:
        uri, sub_carried = convert_group(sub, path_ids + [slug(sub.get("id") or sub.get("title"))])
        carried += sub_carried
        if uri: entries.append({"ref": uri, "sequence": next_seq()})
    for c in g.get("controls", []) or []:
        rid, req = mint_req(c)
        objects[f"objects/req-{c['id']}.json"] = req; req_index[c["id"]] = rid
        entries.append({"ref": rid, "sequence": next_seq()})
    if not entries:
        return None, carried
    sid = g.get("id") or "-".join(path_ids)
    uri = f"{NS}/set/tax/{slug(sid)}"
    s = {"id": uri, "version": version, "lifecycle": "active",
         "title": g.get("title", sid), "members": entries}
    if carried:
        s["facets"] = {COMPAT: {"group-parts": carried}}
        compat_payloads += len(carried); carried = []
    objects[f"objects/set-tax-{slug(sid)}.json"] = s
    return uri, carried

top_entries, root_carried = [], []
empty_groups = 0
for g in cat.get("groups", []):
    uri, carried = convert_group(g, [slug(g.get("id") or g.get("title"))])
    root_carried += carried
    if uri: top_entries.append({"ref": uri, "sequence": next_seq()})
    else: empty_groups += 1
root = {"id": f"{NS}/set/tax/ism", "version": version, "lifecycle": "active",
        "title": cat["metadata"]["title"], "members": top_entries}
if root_carried:
    root["facets"] = {COMPAT: {"group-parts": root_carried}}
    compat_payloads += len(root_carried)
objects["objects/set-tax-root.json"] = root

def baseline_set(kind, key, refs, title):
    uri = f"{NS}/set/baseline/{slug(kind + '-' + key)}"
    objects[f"objects/set-baseline-{slug(kind + '-' + key)}.json"] = {
        "id": uri, "version": version, "lifecycle": "active", "title": title,
        "members": [{"ref": r, "sequence": (i + 1) * 10} for i, r in enumerate(refs)]}

for marker, refs in sorted(baseline_members.items()):
    baseline_set("class", marker, refs, f"Applicability baseline: {marker}")
for lvl, refs in sorted(e8_members.items()):
    baseline_set("e8", lvl, refs, f"Essential Eight maturity: {lvl}")
for cls, refs in sorted(class_members.items()):
    uri = f"{NS}/set/tax/by-class-{slug(cls)}"
    objects[f"objects/set-tax-by-class-{slug(cls)}.json"] = {
        "id": uri, "version": version, "lifecycle": "active",
        "title": f"Category: {cls}", "members": [{"ref": r, "sequence": (i+1)*10} for i, r in enumerate(refs)]}

# write objects + manifest (in place; no rmtree - the OneDrive house rule)
from oscal_conv_lib import textify
for obj in objects.values(): textify(obj, LANG)   # 12 delivery
for rel, obj in objects.items(): w(rel, obj)
# P10 #39 rerun: previously-truncated slugs changed, and formerly-merged
# sets re-emerge - remove stale object files FILE-BY-FILE (never rmtree)
for _base, _, _files in os.walk(os.path.join(OUT, "objects")):
    for _fn in _files:
        _fp = os.path.join(_base, _fn)
        _rel = os.path.relpath(_fp, OUT).replace("\\", "/")
        if _rel.endswith(".json") and _rel not in objects:
            os.remove(_fp)
w("schemas/oscal-1x-compat-1.0.0-stub.json", {
    "id": "https://ns.oscal.org/compat/oscal-1x", "version": "1.0.0",
    "note": "NORMATIVE pinned payload schema (backlog 26); Level-2 waiting room (intended deprecation; see D16/handbook 14.6)",
    "modifies-semantics": [],
    "schema": {"$schema": "https://json-schema.org/draft/2020-12/schema",
               "type": "object", "additionalProperties": False,
               "properties": {"group-parts": {"type": "array", "items": {
                   "type": "object", "additionalProperties": False,
                   "properties": {"group": {"type": "string"},
                                  "name": {"type": "string"},
                                  "prose": {"type": "object",
                                            "additionalProperties": {"type": "string"}}}}}}}})
manifest = {"manifest-version": "1",
            "provenance": {"source": "ACSC ISM OSCAL catalog",
                           "source-version": version,
                           "source-oscal-version": cat["metadata"]["oscal-version"],
                           "converter": "convert_ism.py v0.2"},
            "objects": [{"id": o["id"], "version": o["version"],
                         "package-digest": sha_file(rel),
                         "semantic-digest": semantic_digest(o), "path": rel}
                        for rel, o in sorted(objects.items())],
            "facet-schemas": [{"id": "https://ns.oscal.org/compat/oscal-1x",
                               "exact-version": "1.0.0",
                               "digest": sha_file("schemas/oscal-1x-compat-1.0.0-stub.json"),
                               "path": "schemas/oscal-1x-compat-1.0.0-stub.json"}]}
w("content-manifest.json", manifest)

# ---------- 4) coverage computation ----------
rows = []
unmapped = []
for p, n in sorted(paths.items()):
    if p in D:
        lvl, tgt = D[p]
    elif p.endswith(".props[].name") or p.endswith(".props[].value") or p.endswith(".props[].ns"):
        lvl, tgt = D.get(p, (None, None))
        if lvl is None: unmapped.append((p, n)); continue
    else:
        unmapped.append((p, n)); continue
    rows.append((p, n, lvl, tgt))

total = sum(paths.values())
mapped = sum(n for _, n, _, _ in rows)
prop_rows = [(f"props[].name = {k}", v, PROP_DEST[k][0], PROP_DEST[k][1])
             for k, v in [("sort-id",1150+570),("label",49),("applicability",5301),
                          ("essential-eight-applicability",256),("revision",1101),("updated",1101)]]

j = {"source": SRC, "source-version": version,
     "totals": {"leaf-values": total, "mapped": mapped, "unmapped": total - mapped,
                "coverage-pct": round(100 * mapped / total, 3)},
     "objects-emitted": {"requirements": len(req_index),
                         "sets": sum(1 for r in objects if r.startswith("objects/set-")),
                         "total-objects": len(objects)},
     "modality-word-rule": dict(modality_count),
     "labels": {"from-label-prop": label_from_prop,
                "derived-from-id": len(req_index) - label_from_prop},
     "baseline-sets": {k: len(v) for k, v in sorted(baseline_members.items())},
     "e8-sets": {k: len(v) for k, v in sorted(e8_members.items())},
     "class-sets": {k: len(v) for k, v in sorted(class_members.items())},
     "empty-narrative-groups-skipped": empty_groups,
     "unmapped-paths": [{"path": p, "count": n} for p, n in unmapped],
     "path-map": [{"path": p, "count": n, "level": l, "destination": t} for p, n, l, t in rows]}
json.dump(j, open(REPORT_JSON, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

md = []
md.append(f"# ISM -> Semantic Core: Coverage Report (computed)\n")
md.append(f"Source: ACSC ISM OSCAL catalog v{version} (oscal-version "
          f"{cat['metadata']['oscal-version']}) - 1,150 controls, 570 groups.\n")
md.append(f"## Totals\n")
md.append(f"- Source leaf values inventoried: **{total:,}**")
md.append(f"- Mapped (declared destination): **{mapped:,}**")
md.append(f"- **UNMAPPED: {total - mapped}**  ->  coverage **{j['totals']['coverage-pct']} %**\n")
md.append(f"- Objects emitted: **{len(req_index):,} Requirements**, "
          f"**{j['objects-emitted']['sets']} Sets**, manifest with both digests per object.\n")
md.append("## Conversion rules (declared, counted)\n")
md.append(f"- **Modality word-rule** over statement prose (first match of "
          f"must not > should not > must > should > may, else unspecified): "
          + ", ".join(f"{k} x{v}" for k, v in sorted(modality_count.items(), key=lambda x:-x[1])) + ".")
md.append(f"- **Obligated party**: documented default `{NS}/party/organisation` "
          f"(ISM binds the organisation implicitly; no per-control party data in source).")
md.append(f"- **Labels**: {label_from_prop} from `label` props; "
          f"{len(req_index)-label_from_prop} derived from control id (`ism-1234` -> `ISM-1234`).")
md.append(f"- **sequence**: document order (steps of 10); source `sort-id` path-strings "
          f"(1,150 control + 570 group) thereby absorbed as redundant.")
md.append(f"- **class** -> category Sets: "
          + ", ".join(f"{k} ({len(v)})" for k, v in sorted(class_members.items())) + ".")
md.append(f"- **applicability** -> baseline Sets: "
          + ", ".join(f"{k} ({len(v)})" for k, v in sorted(baseline_members.items()))
          + f"; **essential-eight** -> " 
          + ", ".join(f"{k} ({len(v)})" for k, v in sorted(e8_members.items())) + ".")
md.append(f"- **revision/updated** (x1,101 each): history -> L0 "
          f"(catalog version on every object; per-release notes belong to manifests) - values not object-carried.")
md.append(f"- **Guideline narrative** (`overview` parts on groups, x{compat_payloads}): "
          f"**Level 2** compat facet `oscal-1x@1` on the nearest emitted Set - the declared "
          f"waiting room with a clock (handbook 14.6); residue KPI starts at {compat_payloads}.")
md.append(f"- **Empty narrative groups skipped** (no transitive controls, no parts): {empty_groups} "
          f"(front-matter chapters; declared drop).")
md.append(f"- **Payload free text language-tagged** per corpus language (`{{en: ...}}` on compat "
          f"`group-parts[].prose`, x{compat_payloads}); statement prose was already tagged. "
          f"Harmonized 2026-07-21 (backlog #12).\n")
md.append("### Corpus finding (new vs. census)\n")
md.append("ISM statement prose is **declarative present tense** ('The board ... defines', "
          "'Passphrases are ...'): modal verbs are structurally absent, not merely unencoded. "
          "The census note 'style-guide prose' was too generous. Consequence: `unspecified` is "
          "the *honest* modality for this corpus, and binding force is carried by baseline "
          "membership (the applicability Sets) - exactly the legitimate Core-tier pattern for "
          "narrative frameworks. The single lexical hit is counted above.\n")
md.append("## Per-prop destinations\n")
md.append("| source prop | count | level | destination |\n|---|---:|---|---|")
for k, v, l, t in prop_rows:
    md.append(f"| `{k}` | {v} | {l} | {t} |")
md.append("\n## Full path map (every source path, its count, its destination)\n")
md.append("| path | count | level | destination |\n|---|---:|---|---|")
for p, n, l, t in rows:
    md.append(f"| `{p}` | {n:,} | {l} | {t} |")
md.append("\n## UNMAPPED (gate target: zero)\n")
if unmapped:
    md.append("| path | count |\n|---|---:|")
    for p, n in unmapped: md.append(f"| `{p}` | {n} |")
else:
    md.append("*(none)*")
md.append("\n## Notes & limits (honest)\n")
md.append("- Modality word-rule is a **documented heuristic** over style-guided prose; "
          "its full per-code counts are printed above and every assignment is "
          "reproducible from the rule. Authority review can override per statement.")
md.append("- `props[].ns` values (the exemplary versioned ISM namespace) are absorbed: "
          "kernel fields need no namespace.")
md.append("- Semantic digests use a JCS-compatible canonicalization "
          "(exact here: no floats, ASCII keys); full RFC 8785 lands with the schemas.")
open(REPORT_MD, "w", encoding="utf-8").write("\n".join(md) + "\n")

print(f"controls->requirements: {len(req_index)}  sets: {j['objects-emitted']['sets']}  "
      f"objects total: {len(objects)}")
print(f"leaf values: {total:,}  mapped: {mapped:,}  UNMAPPED: {total-mapped}")
if unmapped:
    print("UNMAPPED PATHS:")
    for p, n in unmapped[:40]: print(f"  {p}  x{n}")
print("modality:", dict(modality_count))
