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

Content is never dropped (author, 2026-11-14). Every value of the source is
written into the bundle, or it is no content by one of three rules the
ledger checks: a name that only selects a field, a namespace, an id that is
rebuilt exactly. Where the kernel has no member for a value it stands in a
facet, in the source's own shape: the props of a control this mapping has
no member for and the document's metadata in the compat facet oscal-1x@1,
the back-matter resources in a references facet on the root Set.

Exit code: 1 when a claim of the ledger does not hold in the written files,
when a source value is unaccounted, or when a wiring check of this script
fails. The bundle, the reports and the record are written before that, so
that a failed run says why."""
import json, hashlib, os, re, copy, sys, collections
from oscal_conv_lib import BUNDLE_NEWLINE   # one byte spelling on every OS (D3.1)
from oscal_conv_lib import known_arguments, out_dir, obligated_party, obligated_party_line, obligated_party_record
from oscal_conv_lib import Ledger, ledger_by_path, ledger_gate, LEDGER_OUTCOMES, document_author, document_day

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
PARTIES = PARTY_DEFAULT.rsplit("/", 1)[0] + "/"                 # where the landmark URI of a party stands
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
# every leaf of the source carries its origin, the tag `ism` and its JSON
# Pointer in sources/ism.json. A value handed on unchanged is recorded as a
# copy when the bundle is accounted for at the end. A value this script
# computes is stated where it is computed, with D(rule, function,
# inputs...): the rule has a name and the function is pure, so the ledger
# applies it to the source again and compares the result with what stands
# in the written file. Where one of several equal occurrences is written,
# the others are linked to it (led.same). What is no content is declared so
# by one of three rules, each checked by the ledger: led.selector (a name
# that only says which field the value beside it goes to), led.namespace
# (the namespace this mapping is written for), led.rebuilt (an id that a
# function gives exactly). A value with no destination and no such rule is
# unaccounted, and the run ends with 1.
TAG = "ism"
led = Ledger()
D = led.derive
cat = led.source(TAG, {"catalog": cat}, typed=True)["catalog"]

# The props this mapping reads, each in the namespace it is written for. A
# prop of another name, or of one of these names in another namespace, has
# another meaning: it is carried as the source writes it, in the compat
# facet of its object.
OSCAL_NS = "http://csrc.nist.gov/ns/oscal"                  # what OSCAL means where a prop names no namespace
ISM_NS = "https://cyber.gov.au/ns/ism/oscal/3.0"
PROP_NS = {"sort-id": OSCAL_NS, "label": OSCAL_NS, "applicability": ISM_NS, "essential-eight-applicability": ISM_NS}
def reads(p):
    """-> the name under which this mapping reads the prop, or None"""
    n = p.get("name")
    return n if n in PROP_NS and p.get("ns", OSCAL_NS) == PROP_NS[n] else None

# ---------- 2) declared destination map ----------
# One row per source path: (pattern, level, destination). Levels:
#   L1, L2         written as it is: in a kernel field, in a facet
#   L1 by rule     a kernel field is made from it by a named rule
#   not-content    no content, by a rule the ledger checks: a name that only
#                  selects a field, a namespace, an id that is rebuilt exactly
#   declared-drop  not carried, for a reason that was declared before the
#                  author's rule of 2026-11-14; listed for the author to decide
#   dispatch       a prop: its own row says (PROP_ROWS)
# The report puts the ledger's measurement beside every row, and a row that
# the ledger does not confirm ends the run (rule: the path map agrees with
# the ledger). L1 and L2 are confirmed by `copied` only: a title that is in
# the bundle as a part of an id and nowhere as a title is not carried.
IFA = "as decided for IFA on 2026-11-13: "
DROP_UUID = (IFA + "the uuid of a source element identifies it inside the source document; JASCON objects get URIs "
                   "minted from names and titles, the uuid itself is not carried")
# The drops that are still declared, for the table of the report: (pattern
# over the ledger's path, the declared reason, a reading under the author's
# rule). The reading is this script's and decides nothing.
DECLARED_DROPS = [
    (r"^ism\.catalog\.uuid$", DROP_UUID,
     "content: the uuid is the identity of this version of the source document, and nothing in the bundle lets a reader "
     "rebuild it. It would stand beside the document's metadata on the root Set."),
]
G = r"^catalog(\.groups\[\])+"                # a group, at any depth
C = G + r"(\.controls\[\])+"                  # a control of a group, also one nested in a control
COMPAT_WORD = "compat facet oscal-1x@1"
RULES = [
    (r"^catalog\.uuid$", "declared-drop", "the uuid of the source document: not carried (a drop declared on 2026-11-13; "
                                          "see the table of declared drops)"),
    (r"^catalog\.metadata\.title$", "L1", "title of the root Set (set/tax/ism)"),
    (r"^catalog\.metadata\.version$", "L1", "`version` of every object; manifest provenance.source-version"),
    (r"^catalog\.metadata\.oscal-version$", "L2", f"{COMPAT_WORD} on the root Set: metadata; manifest provenance.source-oscal-version"),
    (r"^catalog\.metadata\.last-modified$", "L2", f"{COMPAT_WORD} on the root Set: metadata; its day is the manifest's provenance.date"),
    (r"^catalog\.metadata\.parties\[\]\.name$", "L2", f"{COMPAT_WORD} on the root Set: metadata; the name of the party the document "
                                                      f"names as its author makes the manifest's provenance.author-ref"),
    (r"^catalog\.metadata\.", "L2", f"{COMPAT_WORD} on the root Set: metadata, in the source's own shape"),
    (G + r"\.id$", "L1 by rule", "Set id and file name"),
    (G + r"\.title$", "L1", "Set title; with the titles of the groups above it, the Set id and file name; `group` of its "
                            "overview parts in the compat facet"),
    (G + r"\.props\[\]\.(name|ns|value)$", "dispatch", "see per-prop rows"),
    (G + r"\.parts\[\]\.name$", "L2", f"{COMPAT_WORD} on the Set of the group: group-parts[].name"),
    (G + r"\.parts\[\]\.prose$", "L2", f"{COMPAT_WORD} on the Set of the group: group-parts[].prose (language-tagged {{en}})"),
    (C + r"\.id$", "L1 by rule", "Requirement id (URI mint) and file name; label where the control has no `label` prop; `ref` "
                                 "of its entry in every Set it is a member of"),
    (C + r"\.class$", "L1 by rule", "category Sets set/tax/by-class-<class>: id, title, file name and membership"),
    (C + r"\.title$", "L1", "Requirement title"),
    (C + r"\.parts\[\]\.id$", "L1 by rule", "statement id (part-id suffix)"),
    (C + r"\.parts\[\]\.name$", "not-content", "the name `statement` selects the member `statements` for the part's prose"),
    (C + r"\.parts\[\]\.prose$", "L1", "statements[].prose.en (+ modality word-rule, documented)"),
    (C + r"\.props\[\]\.(name|ns|value)$", "dispatch", "see per-prop rows"),
    (r"^catalog\.back-matter\.resources\[\]\.", "L2", "references facet on the root Set: resources[], in the source's own shape, "
                                                      "with the uuid that a `(#uuid)` link in a text names"),
]
RULES = [(re.compile(rx), level, target) for rx, level, target in RULES]
def map_rule(path):
    return next(((level, target) for rx, level, target in RULES if rx.search(path)), (None, None))

# per-prop rows: name -> (level of the name, of the value, of the namespace, destination)
PROP_ROWS = {
    "sort-id":  ("not-content", "not-content", "not-content",
                 "no content: the parent's sort-id and the position among the siblings give it exactly; the bundle keeps "
                 "both as the hierarchy of the Sets and members[].sequence"),
    "label":    ("not-content", "L1", "not-content", "Requirement.label; the name selects that member"),
    "applicability": ("L1 by rule", "L1 by rule", "not-content",
                      "membership -> set/baseline/class-<marker>; the name gives the kind `class`"),
    "essential-eight-applicability": ("L1 by rule", "L1 by rule", "not-content",
                                      "membership -> set/baseline/e8-<level>; the name gives the kind `e8`"),
}
OTHER_PROP = ("L2", "L2", "L2", f"{COMPAT_WORD} on the object: props[], as the source writes the prop (the kernel has no member for it)")

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
# who wrote the source, and when (oscal_conv_lib.document_author, document_day)
R_AUTHOR = ("author of the source: the party its document names as its author (the role `creator`, else `prepared-by`, "
            "else the one party it names); a landmark URI from the party's name")
def _party_uri(name): return PARTIES + slug(name)
R_DAY = "date of the source: the day of the document's last-modified"
def _day(last_modified): return last_modified[:10]

# What is no content, and the rule that says so.
R_PROP_NAME = "the name of a prop selects the member its value is written to, or the rule that reads it"
R_PART_NAME = "the name `statement` of a control's part selects the member `statements` for its prose"
R_NS = "the namespace of a prop: the one this mapping reads the prop's name in"
# A sort-id says where the element stands: its parent's sort-id, its kind,
# and its position among the siblings of that kind, written with as many
# digits as their number has. The bundle keeps all of that (every group is
# a Set, a Set's members are in document order), so a reader rebuilds it;
# section 4 does, from the written files, and compares.
R_SORT_ID = ("a sort-id is its parent's sort-id, the kind of the element and its position among its siblings, written with "
             "as many digits as their number has")
def _sort_id(parent, kind, pos, n): return f"{parent}.{kind}[{pos:0{len(str(n))}d}]"
SORT_ROOT = "catalog[1]"

version = cat["metadata"]["version"]
objects = {}          # relpath -> obj
req_index = {}        # control id -> req URI
baseline_members = collections.defaultdict(list)   # marker -> [(entry ref, the source values that name the Set)]
e8_members = collections.defaultdict(list)
class_members = collections.defaultdict(list)
modality_count = collections.Counter()
sort_ids = {}                                      # id of the object an element became -> its sort-id in the source
label_from_prop = nested_controls = 0
seq_counter = 0

def sort_id(x, object_id, parent_sort_id, kind, pos, n):
    """Declares the sort-id of a group or a control as rebuilt. -> its value,
    for the elements below it (None where the element has none)."""
    own = [p for p in x.get("props", []) or [] if reads(p) == "sort-id"]
    for p in own:
        led.rebuilt(p["value"], R_SORT_ID, _sort_id, parent_sort_id, kind, pos, n)
        led.selector(p["name"], R_PROP_NAME, p["value"], among=PROP_NS)
        if "ns" in p: led.namespace(p["ns"], R_NS, (PROP_NS["sort-id"],), p["name"])
        sort_ids[str(object_id)] = str(p["value"])
    return own[0]["value"] if len(own) == 1 else None

def mint_req(c, parent=None):
    global label_from_prop
    rid = D(R_REQ_ID, _req_uri, c["id"])
    label, kept = None, []
    for p in c.get("props", []) or []:
        n = reads(p)
        if n is None: kept.append(p); continue             # no member for it: carried as it is, below
        if n == "sort-id": continue                        # declared where the control's place is known
        if "ns" in p: led.namespace(p["ns"], R_NS, (PROP_NS[n],), p["name"])
        if n == "label":
            label = p["value"]; label_from_prop += 1
            led.selector(p["name"], R_PROP_NAME, p["value"], among=PROP_NS)
        elif n == "applicability": baseline_members[p["value"]].append((D(R_BASE_MEMBER, _member, c["id"], p["name"], p["value"]), (p["name"], p["value"])))
        elif n == "essential-eight-applicability": e8_members[p["value"]].append((D(R_BASE_MEMBER, _member, c["id"], p["name"], p["value"]), (p["name"], p["value"])))
    if label is None:
        label = D(R_LABEL_ID, _label_from_id, c["id"])
    part = c["parts"][0]
    if "name" in part and "prose" in part:
        led.selector(part["name"], R_PART_NAME, part["prose"], among=("statement",))
    sid = D(R_SMT_ID, _statement_id, part["id"]) if "id" in part else f"{c['id']}_smt".rsplit("_", 1)[-1]
    prose = part.get("prose", "")
    mod = D(R_MODALITY, modality_of, prose)
    modality_count[mod] += 1
    req = {"id": rid, "version": version, "label": label,
           "lifecycle": "active", "title": c["title"],
           "statements": [{"id": sid, "modality": mod,
                           "obligated-parties": [PARTY],
                           "prose": {"en": prose}}]}
    compat = {}
    if kept: compat["props"] = kept
    if parent is not None: compat["nested-in"] = parent["id"]
    if compat: req["facets"] = {COMPAT: compat}
    if "class" in c: class_members[c["class"]].append((D(R_CLASS_MEMBER, _member, c["id"], c["class"]), (c["class"],)))
    else: class_members["unclassed"].append((rid, ("unclassed",)))
    return rid, req

def next_seq():
    global seq_counter; seq_counter += 10; return seq_counter

COMPAT = "https://ns.jascon.net/compat/oscal-1x@1"
F_REF = f"{NS}/facet/references@1"
no_members = collections.Counter()      # groups whose Set has no member, by whether they have an overview part

def own_parts(g):
    return [{"group": g.get("title", ""), "name": p.get("name"), "prose": T(p.get("prose", ""))}
            for p in (g.get("parts", []) or [])]

def add_control(c, entries, parent_sort_id, pos, n, parent=None):
    """A control is a Requirement and an entry of its group's Set. A control
    nested in a control is one too, entered after its parent; that it is
    nested, and in which control, stands in its compat facet."""
    global nested_controls
    rid, req = mint_req(c, parent)
    own = sort_id(c, rid, parent_sort_id, "control", pos, n)
    objects[D(R_REQ_FILE, _req_file, c["id"])] = req; req_index[c["id"]] = rid
    entries.append({"ref": rid, "sequence": next_seq()})
    below = c.get("controls", []) or []
    for i, sub in enumerate(below, 1):
        nested_controls += 1
        add_control(sub, entries, own, i, len(below), c)

def convert_group(g, names, parent_sort_id, pos, n):
    """Every group is a Set, in its place in the hierarchy: its members are
    the Sets of its groups and the Requirements of its controls, in document
    order. A group that holds neither is a Set with no member. Its overview
    parts and the props this mapping has no member for stand in the compat
    facet of its Set. `names`: the id, else the title, of every group from
    the top down to this one. -> the id of the Set."""
    if g.get("id"):
        sid = g["id"]
        uri, rel = D(R_SET_ID, _set_uri, sid), D(R_SET_FILE, _set_file, sid)
    else:
        sid = _names_key(*names)
        uri, rel = D(R_SET_ID_NAMES, _set_uri_names, *names), D(R_SET_FILE_NAMES, _set_file_names, *names)
    own = sort_id(g, uri, parent_sort_id, "group", pos, n)
    entries = []
    below = g.get("groups", []) or []
    for i, sub in enumerate(below, 1):
        entries.append({"ref": convert_group(sub, names + [sub.get("id") or sub.get("title")], own, i, len(below)),
                        "sequence": next_seq()})
    controls = g.get("controls", []) or []
    for i, c in enumerate(controls, 1):
        add_control(c, entries, own, i, len(controls))
    if not entries: no_members["with an overview part" if g.get("parts") else "a heading only"] += 1
    s = {"id": uri, "version": version, "lifecycle": "active",
         "title": g.get("title", sid), "members": entries}
    compat = {}
    if g.get("parts"): compat["group-parts"] = own_parts(g)
    kept = [p for p in g.get("props", []) or [] if reads(p) != "sort-id"]
    if kept: compat["props"] = kept
    if compat: s["facets"] = {COMPAT: compat}
    objects[rel] = s
    return uri

top = cat.get("groups", []) or []
ROOT_ID = f"{NS}/set/tax/ism"
top_entries = []
for i, g in enumerate(top, 1):
    top_entries.append({"ref": convert_group(g, [g.get("id") or g.get("title")], SORT_ROOT, i, len(top)), "sequence": next_seq()})
# The root Set stands for the document. Its title and its version are kernel
# members. Everything else of the document's metadata stands in the compat
# facet under `metadata`, in the source's own shape; the back-matter
# resources stand in a references facet, each with its uuid, so that a link
# `(#uuid)` in a text of the bundle names something the bundle holds.
root = {"id": ROOT_ID, "version": version, "lifecycle": "active",
        "title": cat["metadata"]["title"], "members": top_entries}
metadata_rest = {k: v for k, v in cat["metadata"].items() if k not in ("title", "version")}
resources = (cat.get("back-matter") or {}).get("resources") or []
root_facets = {}
if metadata_rest: root_facets[COMPAT] = {"metadata": metadata_rest}
if resources: root_facets[F_REF] = {"resources": resources}
if root_facets: root["facets"] = root_facets
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
led.resolve(objects)                              # a boolean of the source stands as a plain boolean from here on
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
# The pinned payload schemas. The compat facet holds what the kernel has no
# member for, in the source's own shape: the overview parts of a group, the
# props of an object this mapping has no member for, the control a control
# is nested in, and the document's metadata on the root Set.
_STRINGS = lambda *names: {n: {"type": "string"} for n in names}
SCHEMAS = {"schemas/oscal-1x-compat-1.0.0-stub.json": {
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
                                                           "additionalProperties": {"type": "string"}}}}},
                              "props": {"type": "array", "items": {
                                  "type": "object", "additionalProperties": False, "required": ["name", "value"],
                                  "properties": _STRINGS("name", "uuid", "ns", "value", "class", "group", "remarks")}},
                              "nested-in": {"type": "string"},
                              "metadata": {"type": "object"}}}}}
if resources:
    SCHEMAS["schemas/ism-references-1.0.0-stub.json"] = {
        "id": F_REF.rsplit("@", 1)[0], "version": "1.0.0",
        "note": "NORMATIVE pinned payload schema (backlog 26): the back-matter resources of the source, as the source writes "
                "them; a link `(#uuid)` in a text of the bundle names the resource with that uuid",
        "modifies-semantics": [],
        "schema": {"$schema": "https://json-schema.org/draft/2020-12/schema",
                   "type": "object", "additionalProperties": False, "required": ["resources"],
                   "properties": {"resources": {"type": "array", "items": {
                       "type": "object", "additionalProperties": False, "required": ["uuid"],
                       "properties": {**_STRINGS("uuid", "title", "description", "remarks"),
                                      "props": {"type": "array", "items": {
                                          "type": "object", "additionalProperties": False, "required": ["name", "value"],
                                          "properties": _STRINGS("name", "uuid", "ns", "value", "class", "group", "remarks")}},
                                      "citation": {"type": "object"},
                                      "rlinks": {"type": "array", "items": {
                                          "type": "object", "additionalProperties": False, "required": ["href"],
                                          "properties": _STRINGS("href", "media-type")}}}}}}}}
for _rel, _schema in SCHEMAS.items(): w(_rel, _schema)
provenance = {"source": "ACSC ISM OSCAL catalog",
              "source-version": version,
              "source-oscal-version": cat["metadata"]["oscal-version"]}
author = document_author(cat["metadata"])
if author: provenance["author-ref"] = D(R_AUTHOR, _party_uri, author["name"])
if document_day(cat["metadata"]): provenance["date"] = D(R_DAY, _day, cat["metadata"]["last-modified"])
provenance["converter"] = "convert_ism.py v0.3"
manifest = {"manifest-version": "1",
            "provenance": provenance,
            "objects": [{"id": o["id"], "version": o["version"],
                         "package-digest": sha_file(rel),
                         "semantic-digest": semantic_digest(o), "path": rel}
                        for rel, o in sorted(objects.items())],
            "facet-schemas": [{"id": s["id"], "exact-version": s["version"], "digest": sha_file(rel), "path": rel}
                              for rel, s in sorted(SCHEMAS.items())]}
w("content-manifest.json", manifest)

# ---------- 4) the ledger: every source value, followed into the files just written ----------
# The drops that are still declared (DECLARED_DROPS). No drop is added: a
# value that is content is carried, and one that is not is so by a rule.
for _pattern, _reason, _ in DECLARED_DROPS:
    led.drop(_pattern, _reason)

LEDGER_FULL = led.account(OUT, {**objects, "content-manifest.json": manifest})
LEDGER = ledger_by_path(LEDGER_FULL)
LT = LEDGER["totals"]
# the record: one row per source path and outcome. The entry of every single
# value (36,161 for the pinned source) is made and checked in this run and is
# not written: it is some thirty megabytes that say the same.
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
    for a member of a prop the row of that prop, else the row of the path.
    A path the map does not hold has no level."""
    path = e["path"][len(TAG) + 1:]
    level, _ = map_rule(path)
    if level != "dispatch": return path, level
    prop = source_at(e["source"].rsplit("/", 1)[0])
    row = PROP_ROWS.get(reads(prop), OTHER_PROP)
    return f"{path} of the prop `{prop.get('name')}`", row[("name", "value", "ns").index(path.rsplit(".", 1)[1])]
# what the path map says of a value and what the ledger found, where both hold
AGREE = {"L1": ("copied",), "L2": ("copied",), "L1 by rule": ("transformed", "copied"), "not-content": ("not-content",),
         "declared-drop": ("intentionally-dropped",), None: ()}
def outcome_text(counts):
    return ", ".join(f"{counts[k]:,} {k.replace('-', ' ')}" for k in LEDGER_OUTCOMES if counts.get(k)) or "-"
by_path = collections.defaultdict(collections.Counter)       # path of the path map -> outcome -> values
by_prop = collections.defaultdict(collections.Counter)       # prop name -> outcome -> the leaves of those props
props_seen = collections.Counter()                           # prop name -> props of groups and controls in the source
rule_use = collections.defaultdict(lambda: [set(), 0])       # rule -> [source values, destinations]
no_content = collections.Counter()                           # (kind, rule) -> values
drop_use = collections.defaultdict(lambda: [0, None])        # reason -> [values, the first of them]
disagree = {}                                                # (row, level, outcome) -> [values, the first of them]
for e in LEDGER_FULL["entries"]:
    by_path[e["path"][len(TAG) + 1:]][e["outcome"]] += 1
    if re.search(r"^ism\.catalog\.groups\[\].*\.props\[\]\.[^.\[]+$", e["path"]):
        _name = source_at(e["source"].rsplit("/", 1)[0]).get("name")
        by_prop[_name][e["outcome"]] += 1
        if e["path"].endswith(".name"): props_seen[_name] += 1
    for d in e.get("destinations", []):
        if "rule" in d: rule_use[d["rule"]][0].add(e["source"]); rule_use[d["rule"]][1] += 1
    if e["outcome"] == "not-content": no_content[e["kind"], e["rule"]] += 1
    if e["outcome"] == "intentionally-dropped":
        drop_use[e["reason"]][0] += 1
        if drop_use[e["reason"]][1] is None: drop_use[e["reason"]][1] = e["source"]
    row, level = map_row(e)
    if level is not None and e["outcome"] not in AGREE[level]:
        disagree.setdefault((row, level, e["outcome"]), [0, e["source"]])[0] += 1
RULES_USED = [{"rule": r, "source-values": len(v[0]), "destinations": v[1]} for r, v in sorted(rule_use.items())]
NO_CONTENT = [{"kind": kind, "rule": rule, "values": n} for (kind, rule), n in sorted(no_content.items())]
DROPS = [{"path": rx, "values": drop_use[reason][0], "reason": reason, "example": drop_use[reason][1],
          "example-value": source_at(drop_use[reason][1]), "reading": reading}
         for rx, reason, reading in DECLARED_DROPS if drop_use[reason][0]]
DISAGREE = [{"path": row, "level": level, "ledger": outcome, "values": n, "first": first}
            for (row, level, outcome), (n, first) in sorted(disagree.items(), key=lambda x: (x[0][0], x[0][2]))]

# What the written bundle holds, read back from disk - not from this
# script's variables. A reader has these files and nothing else.
WRITTEN = {}
for _e in manifest["objects"]:
    with open(os.path.join(OUT, _e["path"]), encoding="utf-8") as f: WRITTEN[str(_e["id"])] = json.load(f)
_LINK = re.compile(r"\(#([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\)")
def strings(n):
    if isinstance(n, dict):
        for v in n.values(): yield from strings(v)
    elif isinstance(n, list):
        for v in n: yield from strings(v)
    elif isinstance(n, str): yield n
def compat_props(o, name):
    return [p for p in ((o.get("facets") or {}).get(COMPAT) or {}).get("props", []) if p.get("name") == name]
_root = WRITTEN[ROOT_ID]
_held = {r.get("uuid") for r in ((_root.get("facets") or {}).get(F_REF) or {}).get("resources", [])}
READ_BACK = {"requirements": sum(1 for o in WRITTEN.values() if "statements" in o),
             "sets": sum(1 for o in WRITTEN.values() if "members" in o),
             "sets-with-no-member": sum(1 for o in WRITTEN.values() if "members" in o and not o["members"]),
             "requirements-with-revision": sum(1 for o in WRITTEN.values() if compat_props(o, "revision")),
             "requirements-with-updated": sum(1 for o in WRITTEN.values() if compat_props(o, "updated")),
             "resources": len(_held),
             "links-in-texts": 0, "links-that-name-a-resource-of-the-bundle": 0, "texts-with-a-link": 0,
             "objects-with-a-link": 0, "resources-a-link-names": 0}
_named = set()
for _o in WRITTEN.values():
    _hit = False
    for _text in strings(_o):
        _links = _LINK.findall(_text)
        if not _links: continue
        _hit = True
        READ_BACK["texts-with-a-link"] += 1; READ_BACK["links-in-texts"] += len(_links)
        READ_BACK["links-that-name-a-resource-of-the-bundle"] += sum(1 for u in _links if u in _held)
        _named.update(u for u in _links if u in _held)
    READ_BACK["objects-with-a-link"] += _hit
READ_BACK["resources-a-link-names"] = len(_named)
def rebuilt_sort_ids():
    """The sort-ids a reader makes from the written files alone: the Sets
    from the root down, the order of their members, and which member is a
    Set and which a Requirement. -> {object id: sort-id}"""
    out = {}
    def number(ids, parent, kind):
        for pos, x in enumerate(ids, 1):
            out[x] = _sort_id(parent, kind, pos, len(ids))
    def below_set(set_id):
        refs = [m["ref"] for m in sorted(WRITTEN[set_id]["members"], key=lambda m: m.get("sequence", 0))]
        groups = [r for r in refs if "members" in WRITTEN.get(r, {})]
        reqs = [r for r in refs if "statements" in WRITTEN.get(r, {})]
        nested = collections.defaultdict(list)
        for r in reqs:
            inside = ((WRITTEN[r].get("facets") or {}).get(COMPAT) or {}).get("nested-in")
            nested[_req_uri(inside) if inside is not None else None].append(r)
        number(groups, out.get(set_id, SORT_ROOT), "group")
        def controls(parent_req):
            number(nested[parent_req], out.get(parent_req if parent_req else set_id, SORT_ROOT), "control")
            for r in nested[parent_req]:
                if r in nested: controls(r)
        controls(None)
        for g in groups: below_set(g)
    below_set(ROOT_ID)
    return out
_rebuilt = rebuilt_sort_ids()
READ_BACK["sort-ids-in-the-source"] = len(sort_ids)
READ_BACK["sort-ids-rebuilt-from-the-bundle"] = sum(1 for oid, value in sort_ids.items() if _rebuilt.get(oid) == value)

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

# ---------- 5) coverage computation ----------
rows = []
unmapped = []
for p, n in sorted(paths.items()):
    lvl, tgt = map_rule(p)
    if lvl is None:
        unmapped.append((p, n)); continue
    rows.append((p, n, lvl, tgt))

total = sum(paths.values())
mapped = sum(n for _, n, _, _ in rows)
def prop_row(name):
    lv = PROP_ROWS.get(name, OTHER_PROP)
    level = lv[0] if lv[0] == lv[1] else f"name {lv[0]}, value {lv[1]}"
    return (f"props[].name = {name}", props_seen[name], level, lv[3], outcome_text(by_prop[name]))
prop_rows = [prop_row(k) for k in list(PROP_ROWS) + sorted(k for k in props_seen if k not in PROP_ROWS)]
n_groups = sum(n for p, n in paths.items() if re.fullmatch(G + r"\.title", p))
n_sets = sum(1 for r in objects if r.startswith("objects/set-"))
n_overview = sum(n for p, n in paths.items() if re.fullmatch(G + r"\.parts\[\]\.prose", p))
n_metadata_rest = sum(n for p, n in paths.items() if p.startswith("catalog.metadata.")
                      and p not in ("catalog.metadata.title", "catalog.metadata.version"))
n_back_matter = sum(n for p, n in paths.items() if p.startswith("catalog.back-matter."))

# the source is named by its place in the repository, not by its path on
# the machine of the run: the report is the same wherever it is written
j = {"source": os.path.relpath(SRC, ROOT).replace(os.sep, "/"), "source-version": version,
     "totals": {"leaf-values": total, "mapped": mapped, "unmapped": total - mapped,
                "coverage-pct": round(100 * mapped / total, 3)},
     "objects-emitted": {"requirements": len(req_index), "sets": n_sets, "total-objects": len(objects)},
     "modality-word-rule": dict(modality_count),
     "obligated-party": obligated_party_record(PARTY, PARTY_ORIGIN, PARTY_DEFAULT),
     "labels": {"from-label-prop": label_from_prop,
                "derived-from-id": len(req_index) - label_from_prop},
     "baseline-sets": {k: len(v) for k, v in sorted(baseline_members.items())},
     "e8-sets": {k: len(v) for k, v in sorted(e8_members.items())},
     "class-sets": {k: len(v) for k, v in sorted(class_members.items())},
     "group-sets": {"groups": n_groups, "with-no-member": sum(no_members.values()),
                    "with-no-member-and-an-overview-part": no_members["with an overview part"],
                    "with-no-member-a-heading-only": no_members["a heading only"]},
     "nested-controls": nested_controls,
     "ledger": {"file": LEDGER_FILE, "leaf-values": LEDGER["leaf-values"], "totals": LT,
                "verification-failures": len(LEDGER["verification-failures"]),
                "rules": RULES_USED,
                "not-content": NO_CONTENT,
                "declared-drops": DROPS,
                "path-map-and-ledger-disagree": DISAGREE,
                "read-back-from-the-written-bundle": READ_BACK,
                "written-without-a-source-value": NO_SOURCE},
     "unmapped-paths": [{"path": p, "count": n} for p, n in unmapped],
     "path-map": [{"path": p, "count": n, "level": l, "destination": t,
                   "ledger": {k: by_path[p][k] for k in LEDGER_OUTCOMES if by_path[p].get(k)}} for p, n, l, t in rows]}
with open(REPORT_JSON, "w", encoding="utf-8") as f:
    json.dump(j, f, indent=1, ensure_ascii=False)

md = []
md.append(f"# ISM -> Semantic Core: Coverage Report (computed)\n")
md.append(f"Source: ACSC ISM OSCAL catalog v{version} (oscal-version "
          f"{cat['metadata']['oscal-version']}) - {len(req_index):,} controls, {n_groups:,} groups.\n")
md.append(f"## Totals\n")
md.append(f"- Source leaf values inventoried: **{total:,}**")
md.append(f"- Mapped (declared destination): **{mapped:,}**")
md.append(f"- **UNMAPPED: {total - mapped}**  ->  coverage **{j['totals']['coverage-pct']} %**\n")
md.append(f"- Objects emitted: **{len(req_index):,} Requirements**, "
          f"**{n_sets} Sets**, manifest with both digests per object.\n")
md.append(f"- **Conversion ledger (measured per source value; the figures above are a DECLARATION)**: the path map "
          f"says for every source path where its values are meant to go. The ledger follows each of the "
          f"{LEDGER['leaf-values']:,} source leaf values through the converter into the written files. "
          f"**{LT['copied']:,} copied** (the value stands, with its type, at the destination named, read back from "
          f"the written file), **{LT['transformed']:,} transformed** (a named rule made the destination from it; the "
          f"rule was applied to the source again and compared), **{LT['not-content']:,} no content** (a name that "
          f"only selects a field, a namespace, an id that is rebuilt exactly - each by a rule the ledger checked), "
          f"**{LT['intentionally-dropped']:,} dropped for a reason declared earlier** (listed below for the author "
          f"to decide), **{LT['unaccounted']:,} unaccounted**. Claims that do not hold: "
          f"{len(LEDGER['verification-failures'])}. An equal value elsewhere in the bundle does not count: a value "
          f"is traced by what the converter did with it. A run with an unaccounted value or a claim that does not "
          f"hold ends with 1. `{LEDGER_FILE}` is the record, one row per source path and outcome "
          f"({len(LEDGER['paths'])} rows; the entry of each single value is made and checked in the run and not "
          f"written).\n")
md.append("## Conversion rules (declared, counted)\n")
md.append(f"- **Modality word-rule** over statement prose (first match of "
          f"must not > should not > must > should > may, else unspecified): "
          + ", ".join(f"{k} x{v}" for k, v in sorted(modality_count.items(), key=lambda x:-x[1])) + ".")
md.append(obligated_party_line(PARTY, PARTY_ORIGIN, PARTY_DEFAULT, PARTY_WHY))
md.append(f"- **Labels**: {label_from_prop} from `label` props; "
          f"{len(req_index)-label_from_prop} derived from control id (`ism-1234` -> `ISM-1234`).")
md.append(f"- **Groups -> Sets**: every group is a Set, in its place in the hierarchy ({n_groups:,} groups). Its "
          f"members are the Sets of its groups and the Requirements of its controls. "
          f"{sum(no_members.values())} groups hold neither and are Sets with no member: "
          f"{no_members['with an overview part']} with an overview part, {no_members['a heading only']} a heading only.")
md.append(f"- **sequence**: document order (steps of 10). The source's `sort-id` ({props_seen['sort-id']:,} on "
          f"controls and groups) is no content: {R_SORT_ID}. The ledger checked that for every value. Read back "
          f"from the written files, a reader rebuilds "
          f"{READ_BACK['sort-ids-rebuilt-from-the-bundle']:,} of {READ_BACK['sort-ids-in-the-source']:,}.")
md.append(f"- **class** -> category Sets: "
          + ", ".join(f"{k} ({len(v)})" for k, v in sorted(class_members.items())) + ".")
md.append(f"- **applicability** -> baseline Sets: "
          + ", ".join(f"{k} ({len(v)})" for k, v in sorted(baseline_members.items()))
          + f"; **essential-eight** -> "
          + ", ".join(f"{k} ({len(v)})" for k, v in sorted(e8_members.items())) + ".")
_others = sorted(k for k in props_seen if k not in PROP_ROWS)
md.append(f"- **Props the kernel has no member for** ("
          + (", ".join(f"`{k}` x{props_seen[k]:,}" for k in _others) or "none") + f"): carried as the source writes "
          f"them (name, namespace, value) in the {COMPAT_WORD} of their object, under `props`. A control's own "
          f"revision number is not the `version` of its Requirement: that is the catalogue's, on every object.")
md.append(f"- **Guideline narrative** (`overview` parts on groups, x{n_overview}): "
          f"**Level 2** {COMPAT_WORD} on the Set of the group - the declared waiting room with a clock (handbook 14.6).")
_author_word = f"`{provenance['author-ref']}`" if "author-ref" in provenance else "not written (the document names no author)"
_date_word = f"`{provenance['date']}`" if "date" in provenance else "not written (no last-modified that is a date)"
md.append(f"- **Document metadata**: title and version are the root Set's; the rest of `metadata` "
          f"({n_metadata_rest} values) stands in the {COMPAT_WORD} of the root Set under `metadata`, in the "
          f"source's own shape. Manifest provenance: author-ref {_author_word}, date {_date_word}.")
md.append(f"- **Back-matter**: {len(resources):,} resources in the references facet of the root Set, each with its "
          f"uuid. Read back from the written files: {READ_BACK['links-in-texts']:,} links `(#uuid)` stand in "
          f"{READ_BACK['texts-with-a-link']:,} texts of {READ_BACK['objects-with-a-link']:,} objects; "
          f"{READ_BACK['links-that-name-a-resource-of-the-bundle']:,} of them name a resource the bundle holds "
          f"({READ_BACK['resources-a-link-names']:,} of its {READ_BACK['resources']:,} resources).")
if nested_controls:
    md.append(f"- **Nested controls x{nested_controls}**: a control nested in a control is a Requirement of its own, "
              f"entered in the Set of its group after its parent; the id of the control it is nested in stands in "
              f"its {COMPAT_WORD} under `nested-in`.")
md.append(f"- **Payload free text language-tagged** per corpus language (`{{en: ...}}` on compat "
          f"`group-parts[].prose`); statement prose was already tagged. Harmonized 2026-07-21 (backlog #12).\n")
md.append("### Corpus finding (new vs. census)\n")
md.append("ISM statement prose is **declarative present tense** ('The board ... defines', "
          "'Passphrases are ...'): modal verbs are structurally absent, not merely unencoded. "
          "The census note 'style-guide prose' was too generous. Consequence: `unspecified` is "
          "the *honest* modality for this corpus, and binding force is carried by baseline "
          "membership (the applicability Sets) - exactly the legitimate Core-tier pattern for "
          "narrative frameworks. The single lexical hit is counted above.\n")
md.append("## Per-prop destinations\n")
md.append("The last column is measured: what the ledger found for the leaves of these props (name, value and, where "
          "the prop has one, namespace).\n")
md.append("| source prop | count | level | destination | ledger |\n|---|---:|---|---|---|")
for k, v, l, t, m in prop_rows:
    md.append(f"| `{k}` | {v} | {l} | {t} | {m} |")
md.append("\n## Full path map (every source path, its count, its destination)\n")
md.append("Levels: L1 - written as it is in a kernel field; L2 - written as it is in a facet; L1 by rule - a kernel "
          "field is made from it by a named rule; not-content - no content, by a rule the ledger checks; "
          "declared-drop - not carried, for a reason declared before 2026-11-14; dispatch - a prop, see its own row "
          "above. The last column is measured: the outcomes the ledger found for the values of the path.\n")
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
          f"made from this control's own marker is the id of the Set the entry stands in. Not stated as a rule, "
          f"because it is no function of source values: `sequence` (a counter over document order) and the digests "
          f"(made from the written objects).\n")
md.append("### What is no content\n")
md.append("A value that is not written and is no content, by one of three rules. The ledger checked each: a name "
          "against the names this mapping reads, and against what became of the value it selects; a namespace "
          "against the one the mapping is written for; a rebuilt id by applying the function to the source's own "
          "values.\n")
md.append("| kind | values | rule |\n|---|---:|---|")
for x in NO_CONTENT:
    md.append(f"| {x['kind']} | {x['values']:,} | {x['rule']} |")
if not NO_CONTENT: md.append("| - | 0 | - |")
md.append("\n### Declared drops that remain\n")
md.append("Declared before the author's rule of 2026-11-14 (\"real content is never dropped\") and not one of the "
          "three classes above. They stay declared until the author decides; the reading is the converter's and "
          "decides nothing.\n")
if DROPS:
    md.append("| source path | values | declared reason | example | reading under the author's rule |\n|---|---:|---|---|---|")
    for d in DROPS:
        md.append(f"| `{d['path']}` | {d['values']:,} | {d['reason']} | `{d['example']}` = `{d['example-value']}` | {d['reading']} |")
else:
    md.append("*(none)*")
md.append("\n### Where the path map and the ledger disagree\n")
md.append("Computed for every value: the level its row of the path map gives it (for a leaf of a prop, the row of "
          "that prop) against the outcome the ledger found. L1 and L2 agree with copied only, L1 by rule with "
          "transformed (and with copied, where the value also stands somewhere as it is), not-content with no "
          "content, declared-drop with dropped. A row that disagrees ends the run.\n")
if DISAGREE:
    md.append("| path | level | ledger | values | first value |\n|---|---|---|---:|---|")
    for x in DISAGREE:
        md.append(f"| `{x['path']}` | {x['level']} | {x['ledger'].replace('-', ' ')} | {x['values']:,} | `{x['first']}` |")
else:
    md.append("*(nowhere)*")
md.append("\n### Read back from the written bundle\n")
md.append("Counted over the files of the bundle after they were written, not over the converter's variables.\n")
md.append("| what | count |\n|---|---:|")
for k, v in READ_BACK.items():
    md.append(f"| {k.replace('-', ' ')} | {v:,} |")
md.append("\n### What the kernel has no member for\n")
md.append(f"Carried all the same, in a facet, in the source's own shape; each is a finding about the kernel or the "
          f"standard facets.\n")
md.append(f"- A control's own revision number and the month of its last change (props `revision` and `updated`): "
          f"{props_seen['revision']:,} and {props_seen['updated']:,}. `version` is the catalogue's on every object. "
          f"In the {COMPAT_WORD} of the Requirement, `props`.")
md.append(f"- The document's metadata beyond title and version (dates, OSCAL version, links, roles, parties, "
          f"responsible parties): {n_metadata_rest} values. In the {COMPAT_WORD} of the root Set, `metadata`.")
md.append(f"- The resources a text refers to (back-matter): {len(resources):,} resources, {n_back_matter:,} values. "
          f"In a references facet this converter pins, on the root Set; a link in a text names its target by the "
          f"resource's uuid.")
md.append(f"- The overview text of a group: {n_overview:,} texts. In the {COMPAT_WORD} of the group's Set, "
          f"`group-parts`.")
md.append("\n### What the ledger cannot see\n")
md.append("The ledger follows source values into the bundle, not the other way round. A value the converter writes "
          "on its own has no source value behind it and no entry: the id of the root Set, the lifecycle, the "
          "sequence numbers (document order, counted), the digests, and the obligated party of every statement, "
          "which is the converter's default or the caller's and not a value of the source. Counted over the leaves "
          "of the objects and the manifest as written (the pinned facet schemas are constants of the converter):\n")
md.append("| in | pointer | values | example |\n|---|---|---:|---|")
for x in NO_SOURCE:
    md.append(f"| {x['in']} | `{x['pointer']}` | {x['count']:,} | `{x['example']}` |")
md.append("\nTwo more limits. A value that stands at one destination is accounted for, also where another destination "
          "of it is lost: a control whose entry in a taxonomy Set was lost would still be counted, by its "
          "Requirement. The number of destinations of each rule, in the table above, is where such a loss shows. And "
          "a rule is held to what is written, not to what is right: a rule that is wrong and applied the same way "
          "twice passes.")
md.append("\n## Notes & limits (honest)\n")
md.append("- Modality word-rule is a **documented heuristic** over style-guided prose; "
          "its full per-code counts are printed above and every assignment is "
          "reproducible from the rule. Authority review can override per statement.")
md.append("- Semantic digests use a JCS-compatible canonicalization "
          "(exact here: no floats, ASCII keys); full RFC 8785 lands with the schemas.")
md.append("\n## Unaccounted source values (conversion ledger)\n")
md.append(f"No destination, no rule that says it is no content, no declared reason: a value the converter loses. A "
          f"run that has one ends with 1. `{LEDGER_FILE}` holds the count and the first pointers of every path.\n")
if LEDGER["unaccounted-paths"]:
    md.append("| path | count | first value |\n|---|---:|---|")
    for u in LEDGER["unaccounted-paths"]:
        md.append(f"| `{u['path']}` | {u['count']:,} | `{u['pointers'][0]}` |")
else:
    md.append("*(none)*")
with open(REPORT_MD, "w", encoding="utf-8") as f:
    f.write("\n".join(md) + "\n")

print(f"controls->requirements: {len(req_index)}  sets: {n_sets}  "
      f"objects total: {len(objects)}")
print(f"leaf values: {total:,}  mapped: {mapped:,}  UNMAPPED: {total-mapped}")
if unmapped:
    print("UNMAPPED PATHS:")
    for p, n in unmapped[:40]: print(f"  {p}  x{n}")
print("modality:", dict(modality_count))
print(f"ledger: copied {LT['copied']:,}, transformed {LT['transformed']:,}, no content {LT['not-content']:,}, dropped "
      f"{LT['intentionally-dropped']:,}, unaccounted {LT['unaccounted']:,}; claims that do not hold "
      f"{len(LEDGER['verification-failures'])}")
for f in LEDGER["verification-failures"][:20]: print("  CLAIM THAT DOES NOT HOLD", json.dumps(f, ensure_ascii=False), file=sys.stderr)
for u in LEDGER["unaccounted-paths"][:20]: print(f"  UNACCOUNTED {u['path']} x{u['count']}, first {u['pointers'][0]}", file=sys.stderr)

# Wiring checks. The ledger checks every claim of a destination and every
# rule; it cannot check a declaration that reaches too far, a path map that
# says something else than it found, or a record that is not this run's.
# Each of the checks below answers a change that was made to a copy of this
# script on purpose and that ended with 0 before the check existed, here or
# in convert_csf.py. A check that fails ends the run with 1, after
# everything is written.
wiring = []
if sum(d["values"] for d in DROPS) != LT["intentionally-dropped"]:
    wiring.append(f"{LT['intentionally-dropped'] - sum(d['values'] for d in DROPS)} value(s) are dropped by a declaration "
                  f"that is not in the table of declared drops")
for x in DISAGREE:
    wiring.append(f"the path map calls {x['path']} {x['level']}, and the ledger found {x['values']} value(s) "
                  f"{x['ledger']} there (first: {x['first']})")
if total != LEDGER["leaf-values"]:
    wiring.append(f"the path map counts {total} source leaf values and the ledger {LEDGER['leaf-values']}")
if READ_BACK["sort-ids-rebuilt-from-the-bundle"] != READ_BACK["sort-ids-in-the-source"]:
    wiring.append(f"{READ_BACK['sort-ids-in-the-source'] - READ_BACK['sort-ids-rebuilt-from-the-bundle']} sort-id(s) are "
                  f"not what a reader rebuilds from the written bundle")
if READ_BACK["links-that-name-a-resource-of-the-bundle"] != READ_BACK["links-in-texts"]:
    wiring.append(f"{READ_BACK['links-in-texts'] - READ_BACK['links-that-name-a-resource-of-the-bundle']} link(s) `(#uuid)` "
                  f"in a text of the bundle name no resource the bundle holds")
_record = os.path.join(OUTDIR, LEDGER_FILE)
if not os.path.exists(_record):
    wiring.append(f"{LEDGER_FILE} was not written")
else:
    with open(_record, encoding="utf-8") as f:
        if json.load(f) != json.loads(json.dumps(LEDGER)):
            wiring.append(f"{LEDGER_FILE} on disk is not the record of this run")
for x in wiring: print("  WIRING CHECK FAILED:", x, file=sys.stderr)
if wiring and not (LEDGER["verification-failures"] or LT["unaccounted"]):
    sys.exit(f"convert_ism.py: {len(wiring)} wiring check(s) failed")
ledger_gate(LEDGER_FULL, "convert_ism.py")
