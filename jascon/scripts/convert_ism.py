#!/usr/bin/env python3
"""ISM (OSCAL 1.1.x catalog) -> Semantic Core bundle converter.
Gate item 1, authority 1. Emits: bundle + computed coverage report + the
record of the conversion ledger.
Every source field path is inventoried and must have a declared destination;
UNMAPPED paths are the gate's failure signal (target: zero). The path map
says where a path is MEANT to go. The conversion ledger (backlog #41)
follows every source VALUE into the written bundle and says where it went.

    convert_ism.py [--obligated-party URI] [--out DIR]

The catalogue carries no party on a control. The converter writes one party
of its own on every statement, `<namespace>/party/organisation`;
--obligated-party writes the caller's party in its place, and the coverage
report says which of the two it was (backlog #74). Without arguments the
run reproduces the committed conversion byte for byte; the Validators
workflow holds it to that. --out writes the bundle, the two reports and the
ledger somewhere else, which is where a run with another party belongs.

Exit code: non-zero when a claim of the ledger does not hold in the written
files. Source values without a destination and without a declared reason
are counted and printed, and the run ends with 0: they are the open
questions of backlog #41, not an error of the run."""
import json, hashlib, os, re, copy, sys, collections
from oscal_conv_lib import BUNDLE_NEWLINE   # one byte spelling on every OS (D3.1)
from oscal_conv_lib import known_arguments, out_dir, obligated_party, obligated_party_line, obligated_party_record
from oscal_conv_lib import Ledger, ledger_by_path

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SRC = os.path.join(ROOT, "sources", "ism.json")
ARGV = sys.argv[1:]
known_arguments(ARGV, ("--obligated-party", "--out"))
OUTDIR = out_dir(ARGV, os.path.join(ROOT, "converted_examples", "AU.ISM"))
OUT = os.path.join(OUTDIR, "ism-core-bundle")
REPORT_MD = os.path.join(OUTDIR, "ism-coverage-report.md")
REPORT_JSON = os.path.join(OUTDIR, "ism-coverage-report.json")
LEDGER_FILE = "ism-conversion-ledger.json"
NS = "https://ns.cyber.gov.au/ism"
# Whom a statement binds is not a value of this source (backlog #74)
PARTY_DEFAULT = f"{NS}/party/organisation"
PARTY, PARTY_ORIGIN = obligated_party(ARGV, PARTY_DEFAULT)      # (party, "converter-default" | "caller")
PARTY_WHY = "ISM binds the organisation implicitly; no per-control party data in source"
LANG = "en"   # corpus language: payload free text is language-tagged {LANG: value}

def T(v):
    """Wrap payload free text in the corpus language (backlog #12 harmonization)."""
    return {LANG: v} if v or v == "" else v

# ---------- helpers ----------
def w(path, obj):
    p = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline=BUNDLE_NEWLINE) as f:
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

# The conversion ledger (oscal_conv_lib.Ledger, backlog #41): from here on
# every string of the source carries its origin, the tag `ism` and its JSON
# Pointer in sources/ism.json. A value handed on unchanged is recorded as a
# copy when the bundle is accounted for at the end. A value this script
# computes is stated where it is computed, with D(rule, function,
# inputs...): the rule has a name and the function is pure, so the ledger
# applies it to the source again and compares the result with what stands
# in the written file. Where one of several equal occurrences is written,
# the others are linked to it (led.same). What reaches no destination and
# has no declared reason is listed as unaccounted. Nothing here changes what
# is written: the bundle is byte for byte the one this script wrote before
# the ledger existed.
TAG = "ism"
led = Ledger()
D = led.derive
cat = led.source(TAG, {"catalog": cat})["catalog"]

# ---------- 2) declared destination map (path -> (level, destination)) ----------
# Levels:
#   L1, L2         carried: in a kernel field, in a facet
#   absorbed       not carried as a value; the bundle says the same by other
#                  means (document order, the kernel's own field names)
#   declared-drop  not carried, and said so
#   not-carried    not carried and not decided: nobody has said that the
#                  value may go, and the ledger lists it as unaccounted
# A row that is absorbed or a declared drop is where the ledger's drop is
# declared, and nowhere else: `drop` is (case, reason), and section 4 hands
# each to the ledger for exactly that path. There are two cases, and each
# reason names its own:
#   path-map  this map said before the ledger existed that the path is not
#             carried (a declared drop, or absorbed);
#   ifa       the class is one the author decided for the IFA corpus on
#             2026-11-13 (register, "Amendments - the value-level check of
#             the converters"); the reason starts with the words of IFA.
# A drop applies only to a value that reached no destination. Everything
# else without a destination stays unaccounted until somebody decides it.
# Sentences of this map were corrected on 2026-11-14, when the ledger showed
# that a value is not where the sentence said; the report lists them under
# "Findings of the ledger".
D_MAP = {}            # path -> (level, destination)
DROP_BY_PATH = {}     # path -> reason: every value of the path that has no destination
DROP_CASE = {}        # reason -> "path-map" | "ifa"
def declared(case, reason):
    DROP_CASE[reason] = case; return reason
def dest(path, level, target, drop=None):
    if drop and level not in ("absorbed", "declared-drop"):
        raise SystemExit(f"path map: {path} is {level}, and a drop is declared for it")
    D_MAP[path] = (level, target)
    if drop: DROP_BY_PATH[path] = drop

IFA = "as decided for IFA on 2026-11-13: "
DROP_UUID = declared("ifa", IFA + "the uuid of a source element identifies it inside the source document; JASCON objects "
                                  "get URIs minted from names and titles, the uuid itself is not carried")
DROP_DIRECTORY = declared("ifa", IFA + "the source's directory of parties and roles: a party is a landmark URI and there "
                                       "is no party object (register, backlog #16)")
DROP_BACK_MATTER = declared("path-map", "path map, declared drop: source-document references (guideline PDFs/links) - "
                                        "not requirement data")
DROP_NS = declared("path-map", "path map, absorbed: the namespace of a prop; kernel fields need none")
# Two drops depend on the value and are declared value by value in section 4:
# a sort-id only where it says what its place in the document says, and the
# name of a control's part only where it is the type tag `statement`.
DROP_SORT_ID = declared("path-map", "path map, absorbed by document order -> members[].sequence: this sort-id is its parent's "
                                    "sort-id and the element's position among its siblings (checked for this value)")
DROP_TYPE_TAG = declared("ifa", IFA + "a type tag of a structural element: the bundle says by its shape what kind of thing "
                                      "the element is (the part named `statement` is the entry of `statements`)")

dest("catalog.uuid", "declared-drop", "the uuid of the source document: not carried", DROP_UUID)
dest("catalog.metadata.title", "L1", "title of the root Set (set/tax/ism)")
dest("catalog.metadata.version", "L1", "`version` of every object; manifest provenance.source-version")
dest("catalog.metadata.oscal-version", "L1", "manifest provenance.source-oscal-version")
for p in ["catalog.metadata.published", "catalog.metadata.last-modified"]:
    dest(p, "not-carried", "not carried and not decided: the manifest names the source by its version, not by its dates")
for p in list(paths):
    if p.startswith("catalog.metadata.links[]"):
        dest(p, "not-carried", "not carried and not decided: links of the document to back-matter resources "
                               "(other serialisations and neighbouring versions of the catalogue)")
    if p.startswith("catalog.metadata.responsible-parties[]"):
        dest(p, "not-carried", "not carried and not decided: who prepared the source document")
    if p.startswith("catalog.metadata.roles[]") or p.startswith("catalog.metadata.parties[]"):
        dest(p, "declared-drop", "the source's directory of parties and roles: not carried", DROP_DIRECTORY)
# groups -> Sets
for depth in ["", ".groups[]", ".groups[].groups[]"]:
    base = f"catalog.groups[]{depth}"
    for suf, lvl, tgt in [
        (".id", "L1", "Set id and file name"),
        (".title", "L1", "Set title; with the titles of the groups above it, the Set id and file name; `group` of its "
                         "overview parts in the compat facet. A group with no control below it is no Set: its title is "
                         "carried only where it has an overview part of its own"),
        (".props[].name", "absorbed", "group sort-id: absorbed by document order -> sequence; the value is not carried"),
        (".props[].value", "absorbed", "group sort-id: absorbed by document order -> sequence; the value is not carried"),
        (".parts[].name", "L2", "compat facet oscal-1x@1: guideline overview narrative on the Set"),
        (".parts[].prose", "L2", "compat facet oscal-1x@1: guideline overview narrative on the Set (language-tagged {en})"),
    ]:
        dest(base + suf, lvl, tgt)
# controls -> Requirements (controls appear at group depth 1 and 2)
for depth in [".groups[]", ".groups[].groups[]"]:
    base = f"catalog.groups[]{depth}.controls[]"
    dest(base + ".id", "L1", "Requirement id (URI mint) and file name; label where the control has no `label` prop; "
                             "`ref` of its entry in every Set it is a member of")
    dest(base + ".class", "L1", "category Sets set/tax/by-class-<class>: id, title, file name and membership")
    dest(base + ".title", "L1", "Requirement title")
    dest(base + ".parts[].id", "L1", "statement id (part-id suffix)")
    dest(base + ".parts[].name", "declared-drop", "type tag `statement` (the one part kind present): not carried as a "
                                                  "value; the part is the entry of `statements`")
    dest(base + ".parts[].prose", "L1", "statements[].prose.en (+ modality word-rule, documented)")
    dest(base + ".props[].name", "L1", "dispatch (see per-prop rows)")
    dest(base + ".props[].ns", "absorbed", "prop namespace: absorbed (kernel fields need none); the value is not carried", DROP_NS)
    dest(base + ".props[].value", "L1", "dispatch (see per-prop rows)")
# back-matter
for p in list(paths):
    if p.startswith("catalog.back-matter"):
        dest(p, "declared-drop", "source-document references (guideline PDFs/links) - not requirement data", DROP_BACK_MATTER)

# per-prop dispatch (documented in report; mechanically applied below)
PROP_DEST = {
    "sort-id":  ("absorbed", "absorbed: document order -> members[].sequence (path-string redundant); the value is not carried"),
    "label":    ("L1", "Requirement.label"),
    "applicability": ("L1", "membership -> set/baseline/class-<marker>"),
    "essential-eight-applicability": ("L1", "membership -> set/baseline/e8-<level>"),
    "revision": ("not-carried", "not carried and not decided: the control's own revision number stands neither on "
                                "the object nor in the manifest (the object's version is the catalogue's)"),
    "updated":  ("not-carried", "not carried and not decided: the month of the control's last change stands neither "
                                "on the object nor in the manifest"),
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

# The rules of this conversion, by name. Each function is pure: it takes
# source values and nothing else, so the ledger can apply it again.
R_REQ_ID = "Requirement id from the control id"
def _req_uri(cid): return f"{NS}/req/{cid}"
R_REQ_FILE = "file name of the Requirement from the control id"
def _req_file(cid): return f"objects/req-{cid}.json"
R_LABEL_PROP = "label: the value of the prop that is named `label`, unchanged"
def _label_prop(name, value): return value if name == "label" else None
R_LABEL_ID = "label from the control id (ism-1234 -> ISM-1234; an id of another form as it is)"
def _label_from_id(cid):
    m = re.match(r"ism-(\d+)$", cid)
    return f"ISM-{m.group(1)}" if m else cid
R_SMT_ID = "statement id: the part id after its last underscore"
def _statement_id(part_id): return part_id.rsplit("_", 1)[-1]
R_MODALITY = "modality word-rule over the statement prose"
# a taxonomy Set of a group that has an id; of one that has none, from the
# id, else the title, of every group from the top down to it
R_SET_ID = "taxonomy Set id from the group id"
def _set_uri(gid): return f"{NS}/set/tax/{slug(gid)}"
R_SET_FILE = "file name of the taxonomy Set from the group id"
def _set_file(gid): return f"objects/set-tax-{slug(gid)}.json"
R_SET_ID_NAMES = "taxonomy Set id from the titles of the group and of the groups above it"
def _names_key(*names): return "-".join(slug(n) for n in names)
def _set_uri_names(*names): return f"{NS}/set/tax/{slug(_names_key(*names))}"
R_SET_FILE_NAMES = "file name of the taxonomy Set from the titles of the group and of the groups above it"
def _set_file_names(*names): return f"objects/set-tax-{slug(_names_key(*names))}.json"
# a Set of all controls that carry one marker: an applicability or an
# Essential Eight level (a prop: its name gives the kind, its value the
# marker), or a class
BASELINE_KIND = {"applicability": ("class", "Applicability baseline: "),
                 "essential-eight-applicability": ("e8", "Essential Eight maturity: ")}
R_BASE = ("baseline Set id from the prop name (its kind) and the marker",
          "baseline Set title from the prop name (its kind) and the marker",
          "file name of the baseline Set from the prop name (its kind) and the marker")
def _base_uri(name, marker): return f"{NS}/set/baseline/{slug(BASELINE_KIND[name][0] + '-' + marker)}"
def _base_title(name, marker): return BASELINE_KIND[name][1] + marker
def _base_file(name, marker): return f"objects/set-baseline-{slug(BASELINE_KIND[name][0] + '-' + marker)}.json"
R_CLASS = ("category Set id from the class", "category Set title from the class",
           "file name of the category Set from the class")
def _class_uri(cls): return f"{NS}/set/tax/by-class-{slug(cls)}"
def _class_title(cls): return f"Category: {cls}"
def _class_file(cls): return f"objects/set-tax-by-class-{slug(cls)}.json"
# The entry of a control in such a Set. The marker does not change the
# entry's value, it decides in which Set the entry stands; that this is the
# Set the marker names is held by the link of the marker's own Set id to the
# id of the Set that is written (KEPT_ONCE below).
R_BASE_MEMBER = "entry in the baseline Set that the control's marker names: the Requirement of the control"
R_CLASS_MEMBER = "entry in the category Set that the control's class names: the Requirement of the control"
def _member(cid, *marker): return f"{NS}/req/{cid}"
KEPT_ONCE = "every control that carries the marker names the same Set; the Set is written once"

version = cat["metadata"]["version"]
objects = {}          # relpath -> obj
req_index = {}        # control id -> req URI
baseline_members = collections.defaultdict(list)   # marker -> [(entry ref, the source values that name the Set)]
e8_members = collections.defaultdict(list)
class_members = collections.defaultdict(list)
modality_count = collections.Counter()
label_from_prop = 0
seq_counter = 0

def mint_req(c):
    global label_from_prop
    rid = D(R_REQ_ID, _req_uri, c["id"])
    label = None
    for p in c.get("props", []):
        if p["name"] == "label":
            label = D(R_LABEL_PROP, _label_prop, p["name"], p["value"]); label_from_prop += 1
    if label is None:
        label = D(R_LABEL_ID, _label_from_id, c["id"])
    part = c["parts"][0]
    sid = D(R_SMT_ID, _statement_id, part["id"]) if "id" in part else f"{c['id']}_smt".rsplit("_", 1)[-1]
    prose = part.get("prose", "")
    mod = D(R_MODALITY, modality_of, prose)
    modality_count[mod] += 1
    req = {"id": rid, "version": version, "label": label,
           "lifecycle": "active", "title": c["title"],
           "statements": [{"id": sid, "modality": mod,
                           "obligated-parties": [PARTY],
                           "prose": {"en": prose}}]}
    for p in c.get("props", []):
        n, v = p["name"], p["value"]
        if n == "applicability": baseline_members[v].append((D(R_BASE_MEMBER, _member, c["id"], n, v), (n, v)))
        elif n == "essential-eight-applicability": e8_members[v].append((D(R_BASE_MEMBER, _member, c["id"], n, v), (n, v)))
        # sort-id / revision / updated / label: see PROP_DEST
    if "class" in c: class_members[c["class"]].append((D(R_CLASS_MEMBER, _member, c["id"], c["class"]), (c["class"],)))
    else: class_members["unclassed"].append((rid, ("unclassed",)))
    return rid, req

def next_seq():
    global seq_counter; seq_counter += 10; return seq_counter

COMPAT = "https://ns.jascon.net/compat/oscal-1x@1"
compat_payloads = 0
no_set = collections.Counter()      # groups with no control below them, by whether they have a part of their own

def own_parts(g):
    return [{"group": g.get("title", ""), "name": p.get("name"), "prose": T(p.get("prose", ""))}
            for p in (g.get("parts", []) or [])]

def convert_group(g, names):
    """returns (set_uri or None, carried_parts) - narrative parts attach to the
    nearest emitted ancestor Set as a Level-2 compat payload. `names`: the
    id, else the title, of every group from the top down to this one."""
    global compat_payloads
    entries, carried = [], own_parts(g)
    for sub in g.get("groups", []) or []:
        uri, sub_carried = convert_group(sub, names + [sub.get("id") or sub.get("title")])
        carried += sub_carried
        if uri: entries.append({"ref": uri, "sequence": next_seq()})
    for c in g.get("controls", []) or []:
        rid, req = mint_req(c)
        objects[D(R_REQ_FILE, _req_file, c["id"])] = req; req_index[c["id"]] = rid
        entries.append({"ref": rid, "sequence": next_seq()})
    if not entries:
        no_set["with an overview part" if g.get("parts") else "a heading only"] += 1
        return None, carried
    if g.get("id"):
        sid = g["id"]
        uri, rel = D(R_SET_ID, _set_uri, sid), D(R_SET_FILE, _set_file, sid)
    else:
        sid = _names_key(*names)
        uri, rel = D(R_SET_ID_NAMES, _set_uri_names, *names), D(R_SET_FILE_NAMES, _set_file_names, *names)
    s = {"id": uri, "version": version, "lifecycle": "active",
         "title": g.get("title", sid), "members": entries}
    if carried:
        s["facets"] = {COMPAT: {"group-parts": carried}}
        compat_payloads += len(carried); carried = []
    objects[rel] = s
    return uri, carried

top_entries, root_carried = [], []
empty_groups = 0
for g in cat.get("groups", []):
    uri, carried = convert_group(g, [g.get("id") or g.get("title")])
    root_carried += carried
    if uri: top_entries.append({"ref": uri, "sequence": next_seq()})
    else: empty_groups += 1
root = {"id": f"{NS}/set/tax/ism", "version": version, "lifecycle": "active",
        "title": cat["metadata"]["title"], "members": top_entries}
if root_carried:
    root["facets"] = {COMPAT: {"group-parts": root_carried}}
    compat_payloads += len(root_carried)
objects["objects/set-tax-root.json"] = root

def marker_set(members, rules, fns):
    """One Set for all controls that carry one marker. Its id, title and
    file name are made from the first control's marker; the same three, made
    from every other control's marker, are linked to them."""
    made = [[D(rule, fn, *named) for rule, fn in zip(rules, fns)] for _, named in members]
    uri, title, rel = made[0]
    for twin in made[1:]:
        for dropped, kept in zip(twin, made[0]): led.same(dropped, kept, KEPT_ONCE)
    objects[rel] = {
        "id": uri, "version": version, "lifecycle": "active", "title": title,
        "members": [{"ref": r, "sequence": (i + 1) * 10} for i, (r, _) in enumerate(members)]}

for marker, members in sorted(baseline_members.items()):
    marker_set(members, R_BASE, (_base_uri, _base_title, _base_file))
for lvl, members in sorted(e8_members.items()):
    marker_set(members, R_BASE, (_base_uri, _base_title, _base_file))
for cls, members in sorted(class_members.items()):
    marker_set(members, R_CLASS, (_class_uri, _class_title, _class_file))

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
    "id": "https://ns.jascon.net/compat/oscal-1x", "version": "1.0.0",
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
            "facet-schemas": [{"id": "https://ns.jascon.net/compat/oscal-1x",
                               "exact-version": "1.0.0",
                               "digest": sha_file("schemas/oscal-1x-compat-1.0.0-stub.json"),
                               "path": "schemas/oscal-1x-compat-1.0.0-stub.json"}]}
w("content-manifest.json", manifest)

# ---------- 4) the ledger: every source value, followed into the files just written ----------
# The drops the path map declares for a whole path, each for exactly that path.
for _path, _reason in DROP_BY_PATH.items():
    led.drop("^" + re.escape(f"{TAG}.{_path}") + "$", _reason)
# The two drops that depend on the value. A sort-id is absorbed where it says
# what its place in the document says: its parent's sort-id and the position
# of the element among its siblings. The path map calls it redundant with
# document order; here that is checked for every single value, and a sort-id
# that says anything else is not covered and stays unaccounted. The name of
# a control's part is a type tag where it is `statement`; another name is
# not covered. Neither is declared for a path the map does not hold.
sort_ids = collections.Counter()
def _is_position(value, parent, kind, pos):
    m = re.fullmatch(re.escape(parent) + r"\." + kind + r"\[0*([0-9]+)\]", value)
    return bool(m) and int(m.group(1)) == pos
def declare_by_value(node, at, parent_sort_id):
    """`at`: the path of `node` as the path map writes it"""
    for kind, key in (("group", "groups"), ("control", "controls")):
        here = f"{at}.{key}[]"
        level = D_MAP.get(f"{here}.props[].value", (None,))[0]
        if kind == "control" and level is not None: level = PROP_DEST["sort-id"][0]      # a dispatch row: the prop's own
        for pos, x in enumerate(node.get(key, []) or [], 1):
            own = [p for p in x.get("props", []) or [] if p["name"] == "sort-id"]
            for p in own:
                if level == "absorbed" and parent_sort_id is not None and _is_position(p["value"], parent_sort_id, kind, pos):
                    led.drop_value([p["name"], p["value"]], DROP_SORT_ID); sort_ids["equal-to-position"] += 1
                else: sort_ids["other"] += 1
            if kind == "group":
                declare_by_value(x, here, own[0]["value"] if len(own) == 1 else None)
            elif D_MAP.get(f"{here}.parts[].name", (None,))[0] == "declared-drop":
                part = (x.get("parts") or [{}])[0]
                if part.get("name") == "statement": led.drop_value(part["name"], DROP_TYPE_TAG)
declare_by_value(cat, "catalog", "catalog[1]")

LEDGER_FULL = led.account(OUT, {**objects, "content-manifest.json": manifest})
LEDGER = ledger_by_path(LEDGER_FULL)
LT = LEDGER["totals"]
# the record: one row per source path and outcome. The entry of every single
# value (36,161 for the pinned source) is made and checked in this run and is
# not written: written the same way it is 30.7 megabytes (measured 2026-11-14).
with open(os.path.join(OUTDIR, LEDGER_FILE), "w", encoding="utf-8") as f:
    json.dump(LEDGER, f, indent=1, ensure_ascii=False); f.write("\n")

def source_at(pointer):
    """the node of the source a ledger pointer names (`ism#/catalog/...`)"""
    node = led.docs[TAG]
    for x in pointer.split("#", 1)[1].split("/")[1:]:
        x = x.replace("~1", "/").replace("~0", "~")
        node = node[int(x)] if isinstance(node, list) else node[x]
    return node
def map_row(e):
    """-> (the row of the path map that speaks for a ledger entry, its level):
    for the name and the value of a control's prop the row of that prop, else
    the row of the path. A path or a prop the map does not hold has no level."""
    path = e["path"][len(TAG) + 1:]
    if path in D_MAP and re.search(r"\.controls\[\]\.props\[\]\.(name|value)$", path):
        name = source_at(e["source"].rsplit("/", 1)[0])["name"]
        return f"{path} of the prop `{name}`", PROP_DEST.get(name, (None,))[0]
    return path, D_MAP.get(path, (None,))[0]
OUTCOMES = ("copied", "transformed", "intentionally-dropped", "unaccounted")
# what the path map says of a value and what the ledger found, where both hold
AGREE = {"L1": ("copied", "transformed"), "L2": ("copied", "transformed"), "absorbed": ("intentionally-dropped",),
         "declared-drop": ("intentionally-dropped",), "not-carried": ("unaccounted",), None: ("unaccounted",)}
def outcome_text(counts):
    return ", ".join(f"{counts[k]:,} {k.replace('-', ' ')}" for k in OUTCOMES if counts.get(k)) or "-"
by_path = collections.defaultdict(collections.Counter)       # path of the path map -> outcome -> values
by_prop = collections.defaultdict(collections.Counter)       # prop name -> outcome -> its name and value leaves
props_seen = collections.Counter()                           # prop name -> props of groups and controls in the source
rule_use = collections.defaultdict(lambda: [set(), 0])       # rule -> [source values, destinations]
drop_use = collections.Counter()                             # reason -> values
disagree = {}                                                # (row, level, outcome) -> [values, the first of them]
UNDECLARED_DROPS = []                                        # dropped, and the path map does not say so
for e in LEDGER_FULL["entries"]:
    by_path[e["path"][len(TAG) + 1:]][e["outcome"]] += 1
    if re.search(r"^ism\.catalog\.groups\[\].*\.props\[\]\.(name|value)$", e["path"]):
        _name = source_at(e["source"].rsplit("/", 1)[0])["name"]
        by_prop[_name][e["outcome"]] += 1
        if e["path"].endswith(".name"): props_seen[_name] += 1
    for d in e.get("destinations", []):
        if "rule" in d: rule_use[d["rule"]][0].add(e["source"]); rule_use[d["rule"]][1] += 1
    if "reason" in e: drop_use[e["reason"]] += 1
    row, level = map_row(e)
    if e["outcome"] not in AGREE[level]:
        disagree.setdefault((row, level, e["outcome"]), [0, e["source"]])[0] += 1
        if e["outcome"] == "intentionally-dropped": UNDECLARED_DROPS.append(e["source"])
RULES_USED = [{"rule": r, "source-values": len(v[0]), "destinations": v[1]} for r, v in sorted(rule_use.items())]
DROPS = [{"case": DROP_CASE[r], "reason": r, "values": n}
         for r, n in sorted(drop_use.items(), key=lambda x: (DROP_CASE[x[0]] != "path-map", x[0]))]
DROP_TOTAL = {case: sum(d["values"] for d in DROPS if d["case"] == case) for case in ("path-map", "ifa")}
DISAGREE = [{"path": row, "level": level or "none", "ledger": outcome, "values": n, "first": first}
            for (row, level, outcome), (n, first) in sorted(disagree.items(), key=lambda x: (x[0][0], x[0][2]))]
LOST_TITLES = [e["source"] for e in LEDGER_FULL["entries"] if e["outcome"] == "unaccounted"
               and re.fullmatch(r"ism\.catalog\.groups\[\](\.groups\[\])*\.title", e["path"])]

# What the ledger cannot see: it follows source values into the bundle, not
# the other way round. A value this script writes on its own has no source
# value behind it and no entry. They are counted here, by where they stand.
def written_without_source():
    seen, example = collections.Counter(), {}
    def walk(n, kind, at):
        if isinstance(n, dict):
            for k, v in n.items(): walk(v, kind, f"{at}/{k}")
        elif isinstance(n, list):
            for v in n: walk(v, kind, f"{at}/[]")
        elif not getattr(n, "_origins", ()):
            seen[kind, at] += 1; example.setdefault((kind, at), n)
    for rel, o in sorted(objects.items()):
        walk(o, "Requirement" if "statements" in o else "Set", "")
    walk(manifest, "manifest", "")
    return [{"in": kind, "pointer": at, "count": n, "example": example[kind, at]} for (kind, at), n in sorted(seen.items())]
NO_SOURCE = written_without_source()

# Links of carried text into what is not carried: the overview prose writes
# a reference as a markdown link to the uuid of a back-matter resource.
_LINK = re.compile(r"\(#([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\)")
resource_ids = {r.get("uuid") for r in (cat.get("back-matter", {}) or {}).get("resources", []) or []}
link_texts = link_count = 0
link_targets = set()
def scan_links(node):
    global link_texts, link_count
    for x in (node.get("groups", []) or []) + (node.get("controls", []) or []):
        for p in x.get("parts", []) or []:
            hits = [u for u in _LINK.findall(p.get("prose", "")) if u in resource_ids]
            if hits: link_texts += 1; link_count += len(hits); link_targets.update(hits)
        scan_links(x)
scan_links(cat)

# ---------- 5) coverage computation ----------
rows = []
unmapped = []
for p, n in sorted(paths.items()):
    if p in D_MAP:
        lvl, tgt = D_MAP[p]
    else:
        unmapped.append((p, n)); continue
    rows.append((p, n, lvl, tgt))

total = sum(paths.values())
mapped = sum(n for _, n, _, _ in rows)
prop_rows = [(f"props[].name = {k}", props_seen[k], PROP_DEST[k][0], PROP_DEST[k][1], outcome_text(by_prop[k]))
             for k in PROP_DEST]
prop_unknown = sorted((k, n) for k, n in props_seen.items() if k not in PROP_DEST)
n_groups = sum(n for p, n in paths.items() if re.fullmatch(r"catalog\.groups\[\](\.groups\[\])*\.title", p))

# the source is named by its place in the repository, not by its path on
# the machine of the run: the report is the same wherever it is written
j = {"source": os.path.relpath(SRC, ROOT).replace(os.sep, "/"), "source-version": version,
     "totals": {"leaf-values": total, "mapped": mapped, "unmapped": total - mapped,
                "coverage-pct": round(100 * mapped / total, 3)},
     "objects-emitted": {"requirements": len(req_index),
                         "sets": sum(1 for r in objects if r.startswith("objects/set-")),
                         "total-objects": len(objects)},
     "modality-word-rule": dict(modality_count),
     "obligated-party": obligated_party_record(PARTY, PARTY_ORIGIN, PARTY_DEFAULT),
     "labels": {"from-label-prop": label_from_prop,
                "derived-from-id": len(req_index) - label_from_prop},
     "baseline-sets": {k: len(v) for k, v in sorted(baseline_members.items())},
     "e8-sets": {k: len(v) for k, v in sorted(e8_members.items())},
     "class-sets": {k: len(v) for k, v in sorted(class_members.items())},
     "empty-narrative-groups-skipped": empty_groups,
     "groups-that-are-no-set": {"with-an-overview-part": no_set["with an overview part"], "a-heading-only": no_set["a heading only"]},
     "ledger": {"file": LEDGER_FILE, "leaf-values": LEDGER["leaf-values"], "totals": LT,
                "verification-failures": len(LEDGER["verification-failures"]),
                "rules": RULES_USED,
                "declared-drops": {"path-map": DROP_TOTAL["path-map"], "as-decided-for-ifa": DROP_TOTAL["ifa"], "reasons": DROPS,
                                   "not-declared-by-the-path-map": len(UNDECLARED_DROPS)},
                "sort-ids": {k: sort_ids[k] for k in ("equal-to-position", "other")},
                "path-map-and-ledger-disagree": DISAGREE,
                "written-without-a-source-value": NO_SOURCE,
                "group-titles-not-carried": LOST_TITLES,
                "links-into-the-back-matter": {"texts": link_texts, "links": link_count, "resources": len(link_targets),
                                               "resources-in-the-source": len(resource_ids)}},
     "unmapped-paths": [{"path": p, "count": n} for p, n in unmapped],
     "path-map": [{"path": p, "count": n, "level": l, "destination": t,
                   "ledger": {k: by_path[p][k] for k in OUTCOMES if by_path[p].get(k)}} for p, n, l, t in rows]}
json.dump(j, open(REPORT_JSON, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

md = []
md.append(f"# ISM -> Semantic Core: Coverage Report (computed)\n")
md.append(f"Source: ACSC ISM OSCAL catalog v{version} (oscal-version "
          f"{cat['metadata']['oscal-version']}) - {len(req_index):,} controls, {n_groups:,} groups.\n")
md.append(f"## Totals\n")
md.append(f"- Source leaf values inventoried: **{total:,}**")
md.append(f"- Mapped (declared destination): **{mapped:,}**")
md.append(f"- **UNMAPPED: {total - mapped}**  ->  coverage **{j['totals']['coverage-pct']} %**\n")
md.append(f"- Objects emitted: **{len(req_index):,} Requirements**, "
          f"**{j['objects-emitted']['sets']} Sets**, manifest with both digests per object.\n")
md.append(f"- **Conversion ledger (measured per source value; the figures above are a DECLARATION)**: the path map "
          f"says for every source path where its values are meant to go, and `UNMAPPED: 0` says that no path lacks "
          f"such a sentence. The ledger follows each of the {LEDGER['leaf-values']:,} source leaf values through the "
          f"converter into the written files. **{LT['copied']:,} copied** (the value stands, with its type, at the "
          f"destination named, read back from the written file), **{LT['transformed']:,} transformed** (a named rule "
          f"made the destination from it; the rule was applied to the source again and compared), "
          f"**{LT['intentionally-dropped']:,} intentionally dropped** (a stated reason), "
          f"**{LT['unaccounted']:,} unaccounted** (no destination and no declared reason). Checks that failed: "
          f"{len(LEDGER['verification-failures'])}. An equal value elsewhere in the bundle does not count: a value is "
          f"traced by what the converter did with it. `{LEDGER_FILE}` is the record, one row per source path and "
          f"outcome ({len(LEDGER['paths'])} rows; the entry of each single value is made and checked in the run and "
          f"not written). Rules, declared drops and findings: section \"Conversion ledger\" below. The unaccounted "
          f"values are listed by path at the end of this report; they are the work queue of backlog #41.\n")
md.append("## Conversion rules (declared, counted)\n")
md.append(f"- **Modality word-rule** over statement prose (first match of "
          f"must not > should not > must > should > may, else unspecified): "
          + ", ".join(f"{k} x{v}" for k, v in sorted(modality_count.items(), key=lambda x:-x[1])) + ".")
md.append(obligated_party_line(PARTY, PARTY_ORIGIN, PARTY_DEFAULT, PARTY_WHY))
md.append(f"- **Labels**: {label_from_prop} from `label` props; "
          f"{len(req_index)-label_from_prop} derived from control id (`ism-1234` -> `ISM-1234`).")
md.append(f"- **sequence**: document order (steps of 10); source `sort-id` path-strings "
          f"({props_seen['sort-id']:,} on controls and groups) thereby absorbed as redundant. Checked value by value: "
          f"{sort_ids['equal-to-position']:,} say their place in the document (the parent's sort-id and the position "
          f"among the siblings); {sort_ids['other']:,} say something else or stand where the path map has no row, and "
          f"are not covered.")
md.append(f"- **class** -> category Sets: "
          + ", ".join(f"{k} ({len(v)})" for k, v in sorted(class_members.items())) + ".")
md.append(f"- **applicability** -> baseline Sets: "
          + ", ".join(f"{k} ({len(v)})" for k, v in sorted(baseline_members.items()))
          + f"; **essential-eight** -> "
          + ", ".join(f"{k} ({len(v)})" for k, v in sorted(e8_members.items())) + ".")
md.append(f"- **revision/updated** (x{props_seen['revision']:,} and x{props_seen['updated']:,}): **not carried**. The "
          f"catalogue's version stands on every object; a control's own revision number and the month of its last "
          f"change stand neither on an object nor in the manifest. Not decided: unaccounted in the ledger.")
md.append(f"- **Guideline narrative** (`overview` parts on groups, x{compat_payloads}): "
          f"**Level 2** compat facet `oscal-1x@1` on the nearest emitted Set - the declared "
          f"waiting room with a clock (handbook 14.6); residue KPI starts at {compat_payloads}.")
md.append(f"- **Groups that are no Set** (no control below them): {sum(no_set.values())}, {empty_groups} of them at "
          f"the top level. {no_set['with an overview part']} have an overview part of their own: it is carried on "
          f"the nearest Set above, which is the root Set where no group above is a Set, and names its group. "
          f"{no_set['a heading only']} are headings only, and their titles are not carried (unaccounted in the ledger).")
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
md.append("The last column is measured: what the ledger found for the name and the value of these props.\n")
md.append("| source prop | count | level | destination | ledger (name and value) |\n|---|---:|---|---|---|")
for k, v, l, t, m in prop_rows:
    md.append(f"| `{k}` | {v} | {l} | {t} | {m} |")
for k, v in prop_unknown:
    md.append(f"| `props[].name = {k}` | {v} | - | a prop this converter does not read | {outcome_text(by_prop[k])} |")
md.append("\n## Full path map (every source path, its count, its destination)\n")
md.append("Levels: L1 a kernel field; L2 a facet; absorbed - not carried as a value, the bundle says the same by "
          "other means; declared-drop - not carried, and said so; not-carried - not carried and not decided. The last "
          "column is measured: the outcomes the ledger found for the values of the path.\n")
md.append("| path | count | level | destination | ledger |\n|---|---:|---|---|---|")
for p, n, l, t in rows:
    md.append(f"| `{p}` | {n:,} | {l} | {t} | {outcome_text(by_path[p])} |")
md.append("\n## UNMAPPED (gate target: zero)\n")
if unmapped:
    md.append("| path | count |\n|---|---:|")
    for p, n in unmapped: md.append(f"| `{p}` | {n} |")
else:
    md.append("*(none)*")
md.append("\n## Conversion ledger\n")
md.append("### Rules\n")
md.append("A value the converter computes is made by a named rule. For every destination the ledger applied the "
          "rule to the source again and compared the result with the written file.\n")
md.append("| rule | source values | destinations |\n|---|---:|---:|")
for r in RULES_USED:
    md.append(f"| {r['rule']} | {r['source-values']:,} | {r['destinations']:,} |")
md.append(f"\nOne of several equal occurrences: {KEPT_ONCE}. The marker of a control does not change the value of "
          f"the control's entry in the Set, it decides in which Set the entry stands; the check is that the Set id "
          f"made from this control's own marker is the id of the Set the entry stands in. A label taken from a "
          f"`label` prop is the prop's value unchanged; it is counted as transformed, because the rule that selects "
          f"it by the prop's name carries the name and the value. Not stated as a rule, because it is no function "
          f"of source values: `sequence` (a counter over document order; the `sort-id` says the same order and is "
          f"absorbed) and the digests (made from the written objects).\n")
md.append("### Declared drops\n")
md.append(f"A drop is declared in two cases only. **Path map**: this converter's path map said before the ledger "
          f"that the path is not carried ({DROP_TOTAL['path-map']:,} values). **As decided for IFA**: the class is "
          f"one the author decided for the IFA corpus on 2026-11-13 ({DROP_TOTAL['ifa']:,} values). A drop applies "
          f"only to a value that reached no destination, and it is declared on the row of the path map, for that "
          f"path. Values dropped where the path map does not call the path absorbed or a declared drop: "
          f"{len(UNDECLARED_DROPS)} (a run that has one ends with an error).\n")
md.append("| case | values | reason |\n|---|---:|---|")
for d in DROPS:
    md.append(f"| {'path map' if d['case'] == 'path-map' else 'as decided for IFA'} | {d['values']:,} | {d['reason']} |")
md.append("\n### Where the path map and the ledger disagree\n")
md.append("Computed for every value: the level its row of the path map gives it (for the name and the value of a "
          "control's prop, the row of that prop) against the outcome the ledger found. L1 and L2 agree with copied "
          "and transformed, absorbed and declared-drop with intentionally dropped, not-carried with unaccounted.\n")
if DISAGREE:
    md.append("| path | level | ledger | values | first value |\n|---|---|---|---:|---|")
    for x in DISAGREE:
        md.append(f"| `{x['path']}` | {x['level']} | {x['ledger'].replace('-', ' ')} | {x['values']:,} | `{x['first']}` |")
else:
    md.append("*(nowhere)*")
md.append("\n### What the ledger cannot see\n")
md.append("The ledger follows source values into the bundle, not the other way round. A value the converter writes "
          "on its own has no source value behind it and no entry: the id of the root Set, the lifecycle, the "
          "sequence numbers (document order, counted), the digests, and the obligated party of every statement, "
          "which is the converter's default or the caller's and not a value of the source. Counted over the leaves "
          "of the objects and the manifest as written (the pinned facet schema is a constant of the converter):\n")
md.append("| in | pointer | values | example |\n|---|---|---:|---|")
for x in NO_SOURCE:
    md.append(f"| {x['in']} | `{x['pointer']}` | {x['count']:,} | `{x['example']}` |")
md.append("\nTwo more limits. A value that stands at one destination is accounted for, also where another destination "
          "of it is lost: a control whose entry in a taxonomy Set was lost would still be counted, by its "
          "Requirement. The number of destinations of each rule, in the table above, is where such a loss shows. And "
          "a rule is held to what is written, not to what is right: a rule that is wrong and applied the same way "
          "twice passes.")
md.append("\n### Findings of the ledger\n")
md.append("- **Sentences of the path map that the ledger corrected** (2026-11-14; each said where a value goes, "
          "and the value is not there):\n"
          "  1. `catalog.uuid`, `catalog.metadata.published`, `catalog.metadata.last-modified`: said \"bundle "
          "manifest / L0 provenance\". The manifest holds the version and the OSCAL version of the source and "
          "nothing else of its metadata.\n"
          "  2. `catalog.metadata.title`: said \"bundle manifest / L0 provenance\". It is the title of the root Set.\n"
          "  3. `catalog.metadata.links[]`, `.roles[]`, `.parties[]`, `.responsible-parties[]`: said \"bundle "
          "manifest / L0 provenance (publisher identity)\". None of these values is in the bundle; the manifest "
          "names the source by a text of the converter.\n"
          "  4. props `revision` and `updated`: said \"history -> L0 (object versions/manifest); value not "
          "object-carried\". The version of an object is the catalogue's; the manifest holds neither value.\n"
          "  5. `controls[].class`: said \"category Sets: set/tax/principles | set/tax/controls\". The Sets are "
          "`set/tax/by-class-<class>`.\n"
          "  6. prop `applicability`: said \"membership -> set/baseline/<marker>\". The Sets are "
          "`set/baseline/class-<marker>`.\n"
          "  7. `groups[].title` at every depth: said \"Set title\". A group with no control below it is no Set; "
          "its title is in the bundle only where the group has an overview part of its own (as `group` of that "
          "part).\n"
          "  8. the rule line \"Empty narrative groups skipped (no transitive controls, no parts): 2 (front-matter "
          "chapters; declared drop)\". The two chapters are not empty: the groups below them hold overview texts, "
          "which are carried on the root Set. What is not carried is said in the next finding.")
if LOST_TITLES:
    md.append(f"- **Titles that are lost x{len(LOST_TITLES)}**: a group that is no Set and has no overview part of "
              f"its own is a heading only, and nothing in the bundle holds its title: "
              + ", ".join(f"`{x}`" for x in LOST_TITLES) + ". The overview parts below such a heading stand on the "
              "root Set under the title of their own group; under which heading they stood is not carried.")
if link_count:
    md.append(f"- **Links of carried text into what is not carried**: {link_texts:,} overview texts hold "
              f"{link_count:,} markdown links `(#uuid)` to {len(link_targets):,} of the {len(resource_ids):,} "
              f"back-matter resources. The texts are carried verbatim; the resources (title and address) are a "
              f"declared drop of the path map, so these links name nothing in the bundle.")
md.append("\n## Notes & limits (honest)\n")
md.append("- Modality word-rule is a **documented heuristic** over style-guided prose; "
          "its full per-code counts are printed above and every assignment is "
          "reproducible from the rule. Authority review can override per statement.")
md.append("- `props[].ns` values (the exemplary versioned ISM namespace) are absorbed: "
          "kernel fields need no namespace.")
md.append("- Semantic digests use a JCS-compatible canonicalization "
          "(exact here: no floats, ASCII keys); full RFC 8785 lands with the schemas.")
md.append("\n## Unaccounted source values (conversion ledger)\n")
md.append(f"No destination and no declared reason. Each is either carried by a rule the converter does not state "
          f"yet, or dropped without a decision. `{LEDGER_FILE}` holds the count and the first pointers of every path.\n")
if LEDGER["unaccounted-paths"]:
    md.append("| path | count | first value |\n|---|---:|---|")
    for u in LEDGER["unaccounted-paths"]:
        md.append(f"| `{u['path']}` | {u['count']:,} | `{u['pointers'][0]}` |")
else:
    md.append("*(none)*")
open(REPORT_MD, "w", encoding="utf-8").write("\n".join(md) + "\n")

print(f"controls->requirements: {len(req_index)}  sets: {j['objects-emitted']['sets']}  "
      f"objects total: {len(objects)}")
print(f"leaf values: {total:,}  mapped: {mapped:,}  UNMAPPED: {total-mapped}")
if unmapped:
    print("UNMAPPED PATHS:")
    for p, n in unmapped[:40]: print(f"  {p}  x{n}")
print("modality:", dict(modality_count))
print(f"ledger: copied {LT['copied']:,}, transformed {LT['transformed']:,}, intentionally dropped "
      f"{LT['intentionally-dropped']:,}, unaccounted {LT['unaccounted']:,}; failed checks {len(LEDGER['verification-failures'])}")
# What ends the run with an error, after everything is written so that it
# can be read: a claim of the ledger that does not hold in the written
# files; a drop the path map does not declare; a record on disk that is not
# the record of this run. Unaccounted values do not: they are counted above.
wrong = []
if LEDGER["verification-failures"]:
    for f in LEDGER["verification-failures"][:20]: print("  FAILED CHECK", json.dumps(f, ensure_ascii=False))
    wrong.append(f"{len(LEDGER['verification-failures'])} claim(s) of the ledger do not hold in the written files")
if UNDECLARED_DROPS:
    for x in UNDECLARED_DROPS[:20]: print("  DROPPED, AND THE PATH MAP DOES NOT SAY SO", x)
    wrong.append(f"{len(UNDECLARED_DROPS)} value(s) are dropped where the path map does not call the path absorbed or a declared drop")
_record = os.path.join(OUTDIR, LEDGER_FILE)
if not os.path.exists(_record):
    wrong.append(f"{LEDGER_FILE} was not written")
else:
    with open(_record, encoding="utf-8") as f:
        if json.load(f) != json.loads(json.dumps(LEDGER)):
            wrong.append(f"{LEDGER_FILE} on disk is not the record of this run")
if wrong: sys.exit("convert_ism.py: " + "; ".join(wrong))
