#!/usr/bin/env python3
"""NIST CSF 2.0 (OSCAL catalog) -> Semantic Core bundle.
Census: drafts/gate-3-census.md §3/§6 (2026-07-22). Functions and
categories -> Sets (the C5 rule: membership decides granularity; category
statement prose -> narrative facet on the Set); subcategories ->
Requirements (outcome prose, modality `unspecified` - sixth-corpus
confirmation of the declarative pattern); a withdrawn item (1.1->2.0
restructuring) is an object with lifecycle `withdrawn`, and where it
names a successor the successor's `replaces[]` names it (until 2026-11-14
such an item was no object); implementation examples -> examples@1;
risk-party -> csf@1; the document metadata -> the compat facet on the root
Set. The counts are in the coverage report.

    convert_csf.py [--obligated-party URI] [--out DIR]

The CSF does not say whom an outcome binds (`risk-party` classes a risk as
first or third party; it names nobody). The converter writes one party of
its own on every statement, `<namespace>/party/organization`;
--obligated-party writes the caller's party in its place, and the coverage
report says which of the two it was (backlog #74). Without arguments the
run reproduces the committed conversion byte for byte; the Validators
workflow holds it to that. --out writes the bundle, the two reports and the
ledger somewhere else, which is where a run with another party belongs.

The conversion ledger (backlog #41). The path map of the coverage report
counts source PATHS with a declared destination. The ledger follows every
source VALUE into the written bundle and says what became of it: copied,
transformed by a named rule, no content by a rule the ledger checks (a name
that selects a field, a namespace, an id that is rebuilt exactly), dropped
for a declared reason, or unaccounted. Its record is
`csf-conversion-ledger.json`, one row per source path and outcome.

Content is never dropped (author, 2026-11-14). What this mapping has no
rule for is carried as the source has it, in the compat facet of the
object it belongs to. A run with an unaccounted value, with a claim that
does not hold on the written files, or with a declared drop that reaches
further than it says ends with a non-zero exit, after the bundle, the
reports and the record are written."""
import json, os, re, sys, collections
from oscal_conv_lib import make_T, slug, Bundle, inventory, coverage, report
from oscal_conv_lib import known_arguments, out_dir, obligated_party, obligated_party_line, obligated_party_record
from oscal_conv_lib import Ledger, ledger_by_path, ledger_gate, props_by_name, LEDGER_OUTCOMES
from oscal_conv_lib import COMPAT, referred_to, lifecycle_default_record, lifecycle_default_line

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SRC = os.path.join(ROOT, "sources", "nist", "NIST_CSF_v2.0_catalog.json")
ARGV = sys.argv[1:]
known_arguments(ARGV, ("--obligated-party", "--out"))
OUTDIR = out_dir(ARGV, os.path.join(ROOT, "converted_examples", "US.CSF"))
NS = "https://ns.nist.gov/csf"          # no version in the URI - lineage is D2's job
# Whom a statement binds is not a value of this source (backlog #74)
PARTY_DEFAULT = f"{NS}/party/organization"
PARTY, PARTY_ORIGIN = obligated_party(ARGV, PARTY_DEFAULT)      # (party, "converter-default" | "caller")
PARTY_WHY = "CSF binds the adopting organization"
F_NARR = f"{NS}/facet/narrative@1"
F_EX = f"{NS}/facet/examples@1"
F_CSF = f"{NS}/facet/csf@1"
F_REF = f"{NS}/facet/references@1"
# What the kernel and the standard facets have no place for is carried here,
# as the source has it: `metadata` (the document metadata, on the root Set)
# and `unmapped` (what this mapping does not know of an element, on the
# object the element becomes).
CSF_NS = "https://csrc.nist.gov/ns/csf"      # the namespace of the CSF's own names, `risk-party` and `example`
LEDGER_FILE = "csf-conversion-ledger.json"

lang_wraps = collections.Counter()
T = make_T("en", lang_wraps)

# The conversion ledger (oscal_conv_lib.Ledger): every scalar of the source
# carries its origin from here on. A value handed on unchanged is recorded
# as a copy when the bundle is accounted for at the end. A value this script
# computes is stated where it is computed, with D(rule, function,
# inputs...): the function is pure, so the ledger applies it to the source
# again and compares the result with the written file.
led = Ledger()
D = led.derive
cat = led.source("csf", {"catalog": json.load(open(SRC, encoding="utf-8"))["catalog"]}, typed=True)["catalog"]
VER = "2.0"          # framework version; the OSCAL rendition's doc version rides provenance

def norm(p):
    p = re.sub(r"(\.controls\[\])+", ".controls[]", p)
    p = re.sub(r"(\.parts\[\])+", ".parts[]", p)
    return p

paths = collections.Counter()
inventory({"catalog": cat}, "csf", paths, normalize=norm)

# ---------- the rules: every value this script computes from source values ----------
# Each function is pure. The names are what the ledger's record shows.
R_REQ = "Requirement URI from the subcategory id"
R_CAT = "category Set URI from the category id"
R_FN = "function Set URI from the function id"
R_PATH = "file path of the object in the bundle, from the id"
R_STMT = "statement id: the id of the statement part without the control prefix"
R_SEQ = "member sequence: ten times the place of the member among the members of its Set, in the order of the sort-ids"
R_SEQ_SUB = ("member sequence of a subcategory: ten times its place among all subcategories of its category, "
             "withdrawn ones counted, in the order of the sort-ids")
R_REF = "lineage inverted: the URI of a withdrawn item, written on the successor that its link names"
R_MODE = "lineage mode from the link relation (incorporated_into -> merged-into, moved_to -> renamed)"

def mint(src_id):
    return f"{NS}/req/{src_id}"

def category_uri(cid):
    return f"{NS}/set/category/{slug(cid)}"

def function_uri(gid):
    return f"{NS}/set/function/{slug(gid)}"

def statement_id(sid, cid):
    return sid[len(cid) + 1:] if sid.startswith(cid + "_") else sid

def place(own, keys, at):
    """Ten times the place of the sibling at position `at` of the document,
    whose sort key is `own`, when the siblings are put in the order of their
    sort keys. Siblings with an equal key keep the order of the document.
    `keys`: the sort keys of all the siblings, in document order."""
    if keys[at] != own: return None
    return (sorted(range(len(keys)), key=lambda k: keys[k]).index(at) + 1) * 10

MODE = {"incorporated_into": "merged-into", "moved_to": "renamed"}
def lineage_mode(rel):
    return MODE[rel]

def withdrawn_ref(uri):
    """-> the rule that writes the `ref` of a lineage entry. Four source
    values meet in it: the id of the withdrawn item, its status, the address
    its link gives and the id of the object the entry is written on. It
    gives no value - and the run stops - unless the item is withdrawn and
    the link names that object. `uri`: the rule that mints the URI an item
    of that level has, so that a withdrawn category is named as a category
    Set is, and a withdrawn subcategory as a Requirement is."""
    def ref(wid, status, href, successor):
        return uri(wid) if status == "withdrawn" and href.lstrip("#") == successor else None
    return ref
LINEAGE_REF = {"category": withdrawn_ref(category_uri), "subcategory": withdrawn_ref(mint)}

# ---------- what is no content: three kinds of rule, each checked by the ledger ----------
# A name that only selects the field its value is written to, the namespace
# of such a name, an id that another value gives exactly (author,
# 2026-11-14). Each is stated where the element is read (take(), below). A
# rule that does not hold for a value is not stated for it: that value is
# carried as the source has it, in `unmapped`.
N_CLASS = ("the class of an element says on which level it stands (function, category, subcategory); the level is "
           "what makes it a function Set, a category Set or a Requirement")
N_PROP = "the name of a prop selects the field its value is written to (label, sort-id, status)"
N_PART = "the name of a part selects the member its prose is written to (statement, example, overview)"
N_NS = f"the namespace of the CSF's own names `risk-party` and `example` ({CSF_NS})"
N_PART_ID = {"statement": "the id of a statement part is the id of its item and `_statement`",
             "overview": "the id of an overview part is the id of its function and `_overview`"}
def statement_part_id(eid): return f"{eid}_statement"
def overview_part_id(eid): return f"{eid}_overview"
PART_ID = {"statement": statement_part_id, "overview": overview_part_id}

# What this mapping knows of an element, by the level it stands on, and the
# members of a prop or part that it reads. Whatever else an element holds is
# carried whole, as the source has it.
KNOWN_PROPS = {"function": ("label", "sort-id", "status"), "category": ("label", "sort-id", "status", "risk-party"),
               "subcategory": ("label", "sort-id", "status", "risk-party")}
PROP_MEMBERS = {"label": {"name", "value"}, "sort-id": {"name", "value"}, "status": {"name", "value"},
                "risk-party": {"name", "ns", "value", "remarks"}}
KNOWN_PARTS = {"function": ("overview",), "category": ("statement", "example"), "subcategory": ("statement", "example")}
PART_MEMBERS = {"overview": {"id", "name", "prose"}, "statement": {"id", "name", "prose"},
                "example": {"id", "name", "ns", "prose"}}
ELEMENT_MEMBERS = ("id", "class", "title", "props", "parts", "links", "controls", "groups")

# ---------- the elements: functions, categories, subcategories ----------
ELEMENTS = []           # (element, its level, its parent) in document order
for g in cat.get("groups", []) or []:
    ELEMENTS.append((g, "function", None))
    for c in g.get("controls", []) or []:
        ELEMENTS.append((c, "category", g))
        for s in c.get("controls", []) or []:
            ELEMENTS.append((s, "subcategory", c))
LEVEL = {id(e): level for e, level, _ in ELEMENTS}
groups_by_id = {e["id"]: e for e, level, _ in ELEMENTS if level == "function"}
by_id = {e["id"]: e for e, level, _ in ELEMENTS if level != "function"}

def status_prop(e):
    """-> the first prop that states a status of the element, or None"""
    return next((p for p in e.get("props", []) or [] if p.get("name") == "status" and "value" in p), None)
# A withdrawn category or subcategory has a lineage. A function is an object whatever its status says.
withdrawn = {e["id"] for e, level, _ in ELEMENTS if level != "function" and (status_prop(e) or {}).get("value") == "withdrawn"}

# ---------- withdrawal inversion (underscore rels - the census 7.1 finding) ----------
# A withdrawn item that names a successor is not emitted. What the bundle
# carries of it is its lineage, written on the successor each of its links
# names: its id (as the `ref` of the entry), the link's relation (as `mode`),
# and its label, title and statement prose in the annotation. A withdrawn
# item that no link gives a successor has nowhere to be written but as an
# object of its own: a Set or a Requirement with lifecycle `withdrawn`.
succ_replaces = collections.defaultdict(list)   # successor id -> [(withdrawn item, link)]
fn_replaces = collections.defaultdict(list)     # function-level successor (ID.GV -> GV)
lineage_links = collections.defaultdict(list)   # id(withdrawn item) -> the links that are written as lineage
wd_chain, wd_dangling = [], []
n_hashless = n_lineage_links = 0
for e, level, _ in ELEMENTS:
    if e["id"] not in withdrawn: continue
    for l in e.get("links", []) or []:
        rel, href = l.get("rel"), (l.get("href") or "")
        if rel not in MODE: continue
        n_lineage_links += 1
        if not href.startswith("#"): n_hashless += 1   # fragment marker missing (source finding)
        href = href.lstrip("#")
        if href in withdrawn:
            wd_chain.append((e["id"], href)); continue
        if href in by_id:
            succ_replaces[href].append((e, l)); lineage_links[id(e)].append(l)
        elif href in groups_by_id:
            fn_replaces[href].append((e, l)); lineage_links[id(e)].append(l)
        else:
            wd_dangling.append((e["id"], href))

def is_object(e):
    """Every element is an object since 2026-11-14 (the author's decision: a withdrawn item is an object with
    lifecycle `withdrawn`, whether it names a successor or not). Until then a withdrawn item that names a
    successor was none: only its lineage was written, on the successor."""
    return True
wd_objects = [e for e, _, _ in ELEMENTS if e["id"] in withdrawn and is_object(e)]

# ---------- reading an element ----------
def take(e, level):
    """Reads the element `e` as this mapping knows it, and states for the
    ledger what of it is no content. -> {label, sort, status, risk: the props
    read; statement, examples, overviews: the parts read; unmapped: what the
    mapping does not know of the element, in the source's own shape}."""
    eid, rest = e["id"], {}
    if "class" in e:
        if e["class"] == level: led.selector(e["class"], N_CLASS, [eid, e.get("title")], among=(level,))
        else: rest["class"] = e["class"]
    # props: the first of a name the level knows, and every risk-party in the CSF's namespace
    props, names = e.get("props", []) or [], KNOWN_PROPS[level]
    def first(name):
        return next((p for p in props if name in names and p.get("name") == name and "value" in p), None)
    t = {"label": first("label"), "sort": first("sort-id"), "status": first("status"),
         "risk": [p for p in props if "risk-party" in names and p.get("name") == "risk-party" and "value" in p
                  and p.get("ns", CSF_NS) == CSF_NS]}
    read = [p for p in (t["label"], t["sort"], t["status"]) if p is not None]
    for p in read: led.selector(p["name"], N_PROP, p["value"], among=names)
    for p in t["risk"]:                                # its name is the key under which csf@1 holds the value
        if "ns" in p: led.namespace(p["ns"], N_NS, (CSF_NS,), p["name"])
    read += t["risk"]
    for p in props:
        if not any(p is r for r in read) or set(p) - PROP_MEMBERS[p["name"]]: rest.setdefault("props", []).append(p)
    # parts: the first statement, every example in the CSF's namespace, every overview of a function
    parts, names = e.get("parts", []) or [], KNOWN_PARTS[level]
    def named(name):
        return [p for p in parts if name in names and p.get("name") == name and ("id" in p or "prose" in p)]
    stmts = named("statement")[:1]
    t["statement"] = stmts[0] if stmts else None
    t["examples"] = [p for p in named("example") if p.get("ns", CSF_NS) == CSF_NS]
    t["overviews"] = named("overview")
    read = stmts + t["examples"] + t["overviews"]
    for p in parts:
        whole = not any(p is r for r in read)          # a part the mapping does not read is carried whole
        if not whole:
            name, whole = p["name"], bool(set(p) - PART_MEMBERS[p["name"]])      # and so is one with a member it does not know
            led.selector(p["name"], N_PART, [p[k] for k in ("id", "prose") if k in p], among=names)
            if "ns" in p and name == "example": led.namespace(p["ns"], N_NS, (CSF_NS,), p["name"])
            # the id of a statement or an overview part: written (the statement of a subcategory that is an
            # object), else rebuilt exactly from the id of its element, else carried with the part
            if name in PART_ID and "id" in p and not (level == "subcategory" and is_object(e)):
                if p["id"] == PART_ID[name](eid): led.rebuilt(p["id"], N_PART_ID[name], PART_ID[name], eid)
                else: whole = True
        if whole: rest.setdefault("parts", []).append(p)
    # links: the mapping knows the lineage of a withdrawn item and no other link
    for l in e.get("links", []) or []:
        if not any(l is u for u in lineage_links.get(id(e), ())) or set(l) - {"href", "rel"}:
            rest.setdefault("links", []).append(l)
    for k, v in e.items():                             # a member this mapping has no rule for
        if k not in ELEMENT_MEMBERS: rest[k] = v
    t["unmapped"] = rest
    return t
TAKEN = {id(e): take(e, level) for e, level, _ in ELEMENTS}
def taken(e): return TAKEN[id(e)]

def lineage(obj, entries, own_id):
    """Writes the lineage on the successor `obj`, whose source id is
    `own_id`: `replaces[]`, one entry for each withdrawn item whose link
    names it. The `ref` names the withdrawn item's own object. Until
    2026-11-14 the item was no object, and its label, title and prose stood
    beside the entry in a `nist-withdrawal` annotation; they stand in the
    object now. An entry is built where it is written, because the rule for
    `ref` takes the id of the object that carries it."""
    obj["replaces"] = [{"ref": D(R_REF, LINEAGE_REF[LEVEL[id(w)]], w["id"], taken(w)["status"]["value"], l["href"], own_id),
                        "mode": D(R_MODE, lineage_mode, l["rel"])} for w, l in entries]

# A declared drop that remains (it is listed in the report for the author to
# decide, with the reading of this converter): the sort-id of a withdrawn
# item that names a successor. Such an item is a member of no Set, so its
# place among its siblings has no destination. Declared value by value: on
# the same path the sort-ids of the objects are carried.
# (until 2026-11-14 the sort-id of a withdrawn item that names a successor was a declared drop: the item was a
#  member of no Set. It is an object and a member now, and its sort-id gives its place like any other.)

# ---------- convert ----------
bundle = Bundle(os.path.join(OUTDIR, "csf-core-bundle"))
mod_count = collections.Counter()
req_ids = {}
n_examples = n_riskparty = n_riskparty_values = n_riskparty_unpaired = n_unmapped = 0

def facets_of(e):
    """examples@1 and csf@1 of a category or subcategory, and what the mapping does not know of it"""
    global n_examples, n_riskparty, n_riskparty_values, n_riskparty_unpaired
    t, f = taken(e), {}
    ex = [{"id": p.get("id"), "prose": T(p.get("prose", ""), "example")} for p in t["examples"]]
    if ex:
        f[F_EX] = {"examples": ex}; n_examples += len(ex)
    if t["risk"]:
        # a subcategory may be a risk of the first AND of the third party: two props of one name. One value
        # is written as it is, several as a list in source order, under the name of the prop (props_by_name).
        values, remarks = props_by_name(t["risk"], led), props_by_name(t["risk"], field="remarks")
        f[F_CSF] = {name: {"value": v, **({"remark": remarks[name]} if name in remarks else {})} for name, v in values.items()}
        n_riskparty += 1; n_riskparty_values += len(t["risk"])
        if len(t["risk"]) > 1 and len([p for p in t["risk"] if "remarks" in p]) not in (0, len(t["risk"])):
            n_riskparty_unpaired += 1          # a remark for some of the values only: the two lists do not pair
    return with_unmapped(e, f)

def with_unmapped(e, facets):
    global n_unmapped
    if taken(e)["unmapped"]:
        facets[COMPAT] = {"unmapped": taken(e)["unmapped"]}; n_unmapped += 1
    return facets

LIFECYCLE = ("draft", "active", "deprecated", "withdrawn")       # the words the kernel knows
def lifecycle_of(e):
    """The status the source states is written as it is where it is a word of the kernel's lifecycle
    (`withdrawn` is the only one the CSF uses). An element without a status prop is `active` by this
    converter's word: the source states no status for it. A word the kernel does not know is given no
    meaning here: the run stops and says which."""
    status = taken(e)["status"]
    if status is None: return "active"
    if status["value"] not in LIFECYCLE:
        raise SystemExit(f"convert_csf.py: the source states the status `{status['value']}` for {e['id']}; the kernel's lifecycle "
                         f"knows {', '.join(LIFECYCLE)}, and this converter has no rule that maps another word onto one of them")
    return status["value"]

def convert_subcat(c):
    t = taken(c)
    st = t["statement"] or {}
    prose, sid = st.get("prose", ""), st.get("id")
    rid = D(R_REQ, mint, c["id"])
    if sid is None: stmt = "statement"                                  # no id on the part: the converter's own word
    elif sid.startswith(c["id"] + "_"): stmt = D(R_STMT, statement_id, sid, c["id"])
    else: stmt = sid
    req = {"id": rid, "version": VER, "label": t["label"]["value"] if t["label"] else c["id"],
           "lifecycle": lifecycle_of(c), "title": c.get("title", c["id"]),
           "statements": [{"id": stmt,
                           "modality": "unspecified",
                           "obligated-parties": [PARTY],
                           "prose": {"en": prose}}]}
    mod_count["unspecified"] += 1
    f = facets_of(c)
    if f: req["facets"] = f
    if succ_replaces.get(c["id"]):
        lineage(req, succ_replaces[c["id"]], c["id"])
    bundle.add(D(R_PATH, lambda i: f"objects/req/{slug(i)}.json", c["id"]), req)
    req_ids[c["id"]] = rid
    return rid

def sortkey(x):
    sk = taken(x)["sort"]
    return sk["value"] if sk else x["id"]

sort_ties = []       # (the Set, the sort key, the members that share it)
def in_order(owner, items):
    """-> (the sort keys of `items` in document order, [(position in the
    document, item)] in the order of the sort keys). The sort is stable:
    items with an equal key keep the order of the document."""
    keys = tuple(sortkey(x) for x in items)
    for k, n in collections.Counter(str(k) for k in keys).items():
        if n > 1: sort_ties.append((owner, k, [x["id"] for x in items if sortkey(x) == k]))
    return keys, sorted(enumerate(items), key=lambda t: sortkey(t[1]))

root_members = []
cat_sets = 0
wd_categories = [e["id"] for e, level, _ in ELEMENTS if level == "category" and e["id"] in withdrawn]
wd_subcats = [e["id"] for e, level, _ in ELEMENTS if level == "subcategory" and e["id"] in withdrawn]
group_keys, groups_in_order = in_order("root", cat.get("groups", []) or [])
for gi, g in groups_in_order:
    fn_members = []
    # a function's members are its categories that are objects; their sequence counts those only
    member_keys, members_in_order = in_order(g["id"], [c for c in g.get("controls", []) or [] if is_object(c)])
    for ci, c in members_in_order:
        # category: a Set; its statement prose -> narrative facet on the Set
        t = taken(c)
        prose = (t["statement"] or {}).get("prose", "")
        suri = D(R_CAT, category_uri, c["id"])
        # a subcategory that is no object: lineage already inverted; no member, but counted in the sequence
        sub_keys, subs_in_order = in_order(c["id"], c.get("controls", []) or [])
        members = [{"ref": convert_subcat(s), "sequence": D(R_SEQ_SUB, place, sortkey(s), sub_keys, si)}
                   for si, s in subs_in_order if is_object(s)]
        sobj = {"id": suri, "version": VER, "lifecycle": lifecycle_of(c),
                "title": c.get("title", c["id"]), "label": t["label"]["value"] if t["label"] else c["id"],
                "members": members}
        fx = {}
        if prose: fx[F_NARR] = {"guidance": [T(prose, "category-statement")]}
        fx.update(facets_of(c))
        if fx: sobj["facets"] = fx
        if succ_replaces.get(c["id"]):
            lineage(sobj, succ_replaces[c["id"]], c["id"])
        bundle.add(D(R_PATH, lambda i: f"objects/set/category-{slug(i)}.json", c["id"]), sobj)
        cat_sets += 1
        fn_members.append({"ref": suri, "sequence": D(R_SEQ, place, sortkey(c), member_keys, ci)})
    t = taken(g)
    furi = D(R_FN, function_uri, g["id"])
    fobj = {"id": furi, "version": VER, "lifecycle": lifecycle_of(g),
            "title": g.get("title", g["id"]), "label": t["label"]["value"] if t["label"] else g["id"],
            "members": fn_members}
    fx = {}
    if t["overviews"]:
        fx[F_NARR] = {"guidance": [T(p.get("prose", ""), "overview") for p in t["overviews"]]}
    with_unmapped(g, fx)
    if fx: fobj["facets"] = fx
    if fn_replaces.get(g["id"]):                 # ID.GV, incorporated into GV: function-level successor
        lineage(fobj, fn_replaces[g["id"]], g["id"])
    bundle.add(D(R_PATH, lambda i: f"objects/set/function-{slug(i)}.json", g["id"]), fobj)
    root_members.append({"ref": furi, "sequence": D(R_SEQ, place, sortkey(g), group_keys, gi)})

# The root Set stands for the document. Its title is the document's; version,
# OSCAL version and the date of publication are written to the manifest's
# provenance. Every other member of the document metadata has no kernel
# member and no standard facet: it stands in the compat facet, under
# `metadata`, in the source's own shape and with the source's own values.
METADATA_ELSEWHERE = ("title", "version", "oscal-version", "published")
metadata_rest = {k: v for k, v in cat["metadata"].items() if k not in METADATA_ELSEWHERE}
# The back-matter (the author's decisions of 2026-11-14): a resource that something in the document refers to
# is carried as the source writes it, with its uuid, so that the link resolves inside the bundle; a resource
# nothing refers to is an orphan and stays out, by a rule the ledger checks. The uuid of the document itself
# stands beside its metadata.
R_ORPHAN = "a back-matter resource that nothing in the document refers to: nobody can reach it, and it is not carried"
RES, ORPHANS = [], []
for r in cat.get("back-matter", {}).get("resources", []) or []:
    if "uuid" in r and not referred_to(cat, r): led.orphan(r["uuid"], R_ORPHAN); ORPHANS.append(r)
    else: RES.append(r)
root_facets = {F_REF: {"resources": RES}}
root_facets[COMPAT] = {**({"metadata": metadata_rest} if metadata_rest else {}), "uuid": cat["uuid"]}
bundle.add("objects/set/root.json",
           {"id": f"{NS}/set/root", "version": VER, "lifecycle": "active",
            "title": cat["metadata"]["title"], "members": root_members,
            "facets": root_facets})

bundle.stub("csf-narrative-stub.json", F_NARR.split("@")[0], [], {"guidance": {"type": "array"}})
bundle.stub("csf-examples-stub.json", F_EX.split("@")[0], [], {"examples": {"type": "array"}})
bundle.stub("csf-stub.json", F_CSF.split("@")[0], [], {"risk-party": {"type": "object"}})
bundle.stub("csf-references-stub.json", F_REF.split("@")[0], [], {"resources": {"type": "array"}})
bundle.pin_compat()                  # the one compat schema of every converter (1.1.0), not one of this converter's own
led.resolve(bundle.objects)          # a boolean of the source is written as the plain boolean, and its place is kept
# `active` where the source states no status is this converter's default, counted for the report; the ids of the
# objects whose lifecycle is the source's own word are those of the elements with a status prop
_uri_of = {"function": function_uri, "category": category_uri, "subcategory": mint}
LIFECYCLE_DEFAULT = lifecycle_default_record(bundle.objects, [_uri_of[level](e["id"]) for e, level, _ in ELEMENTS
                                                              if taken(e)["status"] is not None])
manifest = bundle.write({"source": cat["metadata"]["title"], "source-version": VER,
                         "source-doc-version": cat["metadata"]["version"],
                         "source-oscal-version": cat["metadata"]["oscal-version"],
                         "published": cat["metadata"].get("published"),
                         "converter": "convert_csf.py v0.3",
                         "namespace-note": "https://ns.nist.gov/csf minted by converter (no version in the URI; "
                                           "lineage is D2's job) pending a NIST-published URI"})

# ---------- the ledger: every source value, checked against the files just written ----------
# The drops that the first ledger of this converter declared (commit
# 20eec54b) and that are not decided yet. No drop is added. Each pattern
# names one path on which this converter carries nothing, so none of them
# can hide a value that is lost beside carried ones; the run checks that
# below. `reading`: what this converter makes of the value under the author's
# rule (content is never dropped; no content is a name that selects, a
# namespace, an id that is rebuilt exactly). The author decides; the report
# lists them.
# None since 2026-11-14. The author decided each drop the first ledger had declared: the uuid of the document
# and the back-matter resources something refers to are carried, the sort-id of a withdrawn item gives its
# place in a Set, and a resource nothing refers to stays out by the ledger's rule for an orphan.
PATH_DROPS = []         # (the source path, the reason, the reading)
READING = {}
for path, reason, _ in PATH_DROPS: led.drop("^" + re.escape(path) + "$", reason)
LEDGER = led.account(bundle.out, {**bundle.objects, "content-manifest.json": manifest})
LT = LEDGER["totals"]
BY_PATH = ledger_by_path(LEDGER)
with open(os.path.join(OUTDIR, LEDGER_FILE), "w", encoding="utf-8") as f:
    json.dump(BY_PATH, f, indent=1, ensure_ascii=False); f.write("\n")

# what the entries say, counted for the report
def source_value(pointer):
    node = led.docs["csf"]
    for x in pointer.split("#", 1)[1].split("/")[1:]:
        x = x.replace("~1", "/").replace("~0", "~")
        node = node[int(x)] if isinstance(node, list) else node[x]
    return node
not_content = collections.Counter((e["kind"], e["rule"]) for e in LEDGER["entries"] if e["outcome"] == "not-content")
drops = collections.OrderedDict()          # (path as the path map has it, reason) -> [count, the first value]
for e in LEDGER["entries"]:
    if e["outcome"] != "intentionally-dropped": continue
    row = drops.setdefault((norm(e["path"]), e["reason"]), [0, source_value(e["source"])])
    row[0] += 1
rules_used = collections.Counter(rule for rule, _, _ in {(d["rule"], d["object"], d["pointer"])       # rule -> the values it wrote
                                                         for e in LEDGER["entries"] for d in e.get("destinations", []) if "rule" in d})

# Wiring checks. The ledger checks every claim of a destination and every
# rule of what is no content; it cannot check a declared drop that is too
# wide, or a record that is not this run's. Each of the checks below answers
# a defect that was put into a copy of this script on purpose and passed
# before the check existed. A check that fails ends the run with a non-zero
# exit, after the reports are written.
wiring = []
# every declared drop is one of those listed above: none is added
for (path, reason), (n, _) in drops.items():
    if (path, reason) not in READING:
        wiring.append(f"{n} value(s) under {path} are dropped, and no declared drop of this converter covers that path "
                      f"with this reason: {reason}")
# a drop by path is declared only for a path on which nothing is carried: on a
# path with carried values it would report a lost value as dropped on purpose
carried_paths = {e["path"] for e in LEDGER["entries"] if e["outcome"] in ("copied", "transformed")}
by_pattern = {reason for _, reason, _ in PATH_DROPS}
for p in sorted({e["path"] for e in LEDGER["entries"] if e.get("reason") in by_pattern} & carried_paths):
    wiring.append(f"a drop declared by path covers {p}, on which other values are carried: a value lost there would "
                  f"read as dropped on purpose")
# the file on disk is the record of this run, not one left by an earlier run or written from an earlier accounting
if not os.path.exists(os.path.join(OUTDIR, LEDGER_FILE)): wiring.append(f"{LEDGER_FILE} was not written")
else:
    with open(os.path.join(OUTDIR, LEDGER_FILE), encoding="utf-8") as f:
        if json.load(f) != json.loads(json.dumps(BY_PATH)): wiring.append(f"{LEDGER_FILE} on disk is not the record of this run")

def without_a_source(result, objects):
    """The other direction, which the ledger does not take: the leaf values
    of the written objects that are NOT the destination of a source value.
    -> (leaf values in all, Counter of those without a source by JSON
    Pointer, array positions collapsed to `[]`)"""
    arrived = {(d["object"], d["pointer"]) for e in result["entries"] for d in e.get("destinations", []) if d.get("as") != "key"}
    total, own = 0, collections.Counter()
    def walk(node, oid, parts):
        nonlocal total
        if isinstance(node, dict):
            for k, v in node.items(): walk(v, oid, parts + [k])
        elif isinstance(node, list):
            for i, v in enumerate(node): walk(v, oid, parts + [i])
        else:
            total += 1
            pointer = "".join("/" + str(x).replace("~", "~0").replace("/", "~1") for x in parts)
            if (oid, pointer) not in arrived: own[re.sub(r"/[0-9]+(?=/|$)", "/[]", pointer)] += 1
    for rel, o in objects.items(): walk(o, o.get("id") or rel, [])
    return total, own
OUT_LEAVES, OWN = without_a_source(LEDGER, bundle.objects)

# ---------- coverage ----------
# The path map says where each source path is MEANT to go, for any catalogue
# of this shape. What the ledger found for this run stands behind each
# sentence, counted (`[ledger: ...]`), so that no sentence names a
# destination the ledger does not confirm.
CTL = r"^csf\.catalog\.groups\[\]\.controls\[\]\."
ELSE = "; what the mapping does not know is carried as it is in the compat facet (`unmapped`)"
RULES = [
 (r"^csf\.catalog\.metadata\.(title|version|oscal-version|published)$", "L1",
  "bundle manifest provenance (`source`, `source-doc-version`, `source-oscal-version`, `published`); the title "
  "is the title of the root Set as well"),
 (r"^csf\.catalog\.uuid$", "L2", "compat facet on the root Set, member `uuid`"),
 (r"^csf\.catalog\.metadata\.", "L2",
  "compat facet on the root Set, member `metadata`, in the source's own shape and with its own values "
  "(`last-modified`, revisions, props, links, roles, parties, responsible-parties)"),
 (r"^csf\.catalog\.back-matter\.", "L1",
  "references@1 facet on the root Set: a resource that something in the document refers to, as the source writes "
  "it (uuid, title, links with their media type); a resource nothing refers to is an orphan and is not carried "
  "(a rule the ledger checks)"),
 (r"^csf\.catalog\.groups\[\]\.id$", "L1", "function Set id (URI mint)"),
 (r"^csf\.catalog\.groups\[\]\.title$", "L1", "function Set title"),
 (r"^csf\.catalog\.groups\[\]\.class$", "L1",
  "no content: `function` says on which level the element stands, and the Set says it by its URI (a rule the "
  "ledger checks)" + ELSE),
 (r"^csf\.catalog\.groups\[\]\.props\[\]\.value$", "L1",
  "label -> function Set label; sort-id -> the sequence of the function in the root Set" + ELSE),
 (r"^csf\.catalog\.groups\[\]\.props\[\]\.name$", "L1",
  "no content: the name selects the field its value is written to (`label`, `sort-id`; a rule the ledger checks)" + ELSE),
 (r"^csf\.catalog\.groups\[\]\.parts\[\]\.prose$", "L2",
  "function overview -> narrative@1 guidance on the function Set (language-tagged)" + ELSE),
 (r"^csf\.catalog\.groups\[\]\.parts\[\]\.name$", "L2",
  "no content: `overview` selects the member its prose is written to (a rule the ledger checks)" + ELSE),
 (r"^csf\.catalog\.groups\[\]\.parts\[\]\.id$", "L2",
  "no content: rebuilt exactly, the id of the function and `_overview` (a rule the ledger checks)" + ELSE),
 (CTL + r"id$", "L1",
  "category Set / subcategory Requirement id (URI mint); withdrawn with a successor: also the `ref` of the entry "
  "in the replaces[] of each successor"),
 (CTL + r"title$", "L1",
  "category Set / subcategory Requirement title"),
 (CTL + r"class$", "L1",
  "no content: `category` / `subcategory` says on which level the element stands, and the object says it by its "
  "type and URI (a rule the ledger checks)" + ELSE),
 (CTL + r"props\[\]\.value$", "L1",
  "label->label; sort-id->Set sequence; risk-party->csf@1, every value, a list where an "
  "item has two; status `withdrawn`->lifecycle `withdrawn` of the object, and for an item with a successor an "
  "input of the rule that writes its entry on the successor" + ELSE),
 (CTL + r"props\[\]\.name$", "L1",
  "risk-party: the key under which csf@1 holds the value; label, sort-id, status: no content, the name selects "
  "the field its value is written to (a rule the ledger checks)" + ELSE),
 (CTL + r"props\[\]\.ns$", "L1",
  "no content: the CSF's own namespace of the `risk-party` prop name (a rule the ledger checks)" + ELSE),
 (CTL + r"props\[\]\.remarks$", "L2",
  "risk-party remark -> csf@1 (carried verbatim), one for every value" + ELSE),
 (CTL + r"links\[\]\.rel$", "L1",
  "incorporated_into/moved_to (UNDERSCORE spelling - source finding) -> `mode` (merged-into/renamed) of the entry "
  "in the successor's replaces[]" + ELSE),
 (CTL + r"links\[\]\.href$", "L1",
  "names the successor: the entry stands on the Requirement or Set with that id, and its `ref` is written by a "
  "rule that holds only if the address names that object" + ELSE),
 (CTL + r"parts\[\]\.prose$", "L1",
  "subcategory statement -> statements[0] (modality unspecified); category statement -> narrative@1 on "
  "the Set; example parts -> examples@1 (language-tagged)" + ELSE),
 (CTL + r"parts\[\]\.id$", "L1",
  "subcategory statement id -> statements[0].id, without the control prefix; example id -> examples@1; the id of a "
  "category's statement part and of the statement part of a withdrawn item with a successor: no content, rebuilt "
  "exactly, the id of the item and `_statement` (a rule the ledger checks)" + ELSE),
 (CTL + r"parts\[\]\.name$", "L1",
  "no content: `statement` / `example` selects the member the prose is written to (a rule the ledger checks)" + ELSE),
 (CTL + r"parts\[\]\.ns$", "L1",
  "no content: the CSF's own namespace of the `example` part name (a rule the ledger checks)" + ELSE),
]
rows, unmapped = coverage(paths, RULES)
WORDS = {"copied": "copied", "transformed": "transformed", "not-content": "no content", "intentionally-dropped": "dropped",
         "unaccounted": "UNACCOUNTED"}
found = collections.defaultdict(collections.Counter)          # path as the path map has it -> what became of its values
for e in LEDGER["entries"]: found[norm(e["path"])][e["outcome"]] += 1
rows = [(p, n, l, f"{t} [ledger: " + ", ".join(f"{found[p][k]:,} {WORDS[k]}" for k in LEDGER_OUTCOMES if found[p][k]) + "]")
        for p, n, l, t in rows]

nset = sum(1 for rel in bundle.objects if "/set/" in rel)
n_withdrawn_objects = collections.Counter(LEVEL[id(e)] for e in wd_objects)
own_fields = ", ".join(f"`{p}` x{n}" for p, n in sorted(OWN.items()))
ledger_lines = [
     f"- **Conversion ledger (measured per source value; backlog #41)**: each of the {LEDGER['leaf-values']:,} source leaf "
     f"values was followed into the written bundle. **{LT['copied']:,} copied** (the value stands, with its type, at the "
     f"destination named, read back from the written file), **{LT['transformed']:,} transformed** (one of "
     f"{len(rules_used)} named rules made the destination from it; the rule was applied to the source again and "
     f"compared), **{LT['not-content']:,} no content** (a name that only selects a field, a namespace, an id that "
     f"another value gives exactly - each by a rule the ledger checked on the value; the rules are listed near the end "
     f"of this report), **{LT['intentionally-dropped']:,} dropped for a reason the first ledger declared** (not "
     f"decided: listed near the end of this report with what this converter makes of each), "
     f"**{LT['unaccounted']:,} unaccounted**. Checks that failed: {len(LEDGER['verification-failures'])}. The path map "
     f"below reads {sum(paths.values()):,} of {sum(paths.values()):,} for the same conversion: it counts paths with a "
     f"declared destination, the ledger counts values. The record is `{LEDGER_FILE}`: one row per source path and "
     f"outcome, with its count, an example and the destinations, the rules or the reasons. A run with an unaccounted "
     f"value or a failed check ends with a non-zero exit.",
     f"- **What the kernel and the standard facets have no place for** (carried all the same, in a facet this "
     f"converter pins): the document metadata beyond title, version, OSCAL version and date of publication - "
     f"`{COMPAT}`, member `metadata`, on the root Set; the first-party / third-party class of a subcategory "
     f"(`risk-party`, x{n_riskparty_values}) and its remark - csf@1; the examples of a subcategory - examples@1; what "
     f"this mapping does not know of an element - `{COMPAT}`, member `unmapped`, on x{n_unmapped} objects of this run.",
     f"- **What the ledger cannot see**: it follows source values into the bundle, not the other way. Counted the "
     f"other way for this run: of the {OUT_LEAVES:,} leaf values of the {len(bundle.objects)} objects, "
     f"{OUT_LEAVES - sum(OWN.values()):,} are a source value or made from one by a rule; the other "
     f"{sum(OWN.values()):,} are written by the converter with no source value behind them: {own_fields} (the "
     f"version `{VER}`; the lifecycle `active` of every item that carries no status prop - the source states none "
     f"for it; the modality `unspecified`; the obligated party `{PARTY}`; the id of the root Set). The namespace "
     f"`{NS}` in every minted URI, the facet names and the manifest's own fields (`source-version`, `converter`, "
     f"`namespace-note`, the digests) are the converter's as well."]
if n_riskparty_unpaired:
    ledger_lines.append(
     f"- **Risk-party remarks that do not pair x{n_riskparty_unpaired}**: an item carries several `risk-party` props "
     f"and a remark on some of them only. Values and remarks are carried, each list in source order; which remark "
     f"belongs to which value is not said by the lists.")
shared_uuid = [r.get("title", "") for r in cat.get("back-matter", {}).get("resources", []) or [] if "uuid" in cat and r.get("uuid") == cat["uuid"]]
if shared_uuid:
    ledger_lines.append(
     f"- **The document and one of its resources share a uuid x{len(shared_uuid)}** (source finding): `catalog.uuid` is "
     f"`{cat['uuid']}`, and so is the uuid of the back-matter resource `{shared_uuid[0]}`. A link that names this "
     f"uuid names both.")
if sort_ties:
    ledger_lines.append(
     f"- **Sort-id shared by siblings x{len(sort_ties)}** (source finding): " +
     "; ".join(f"{' and '.join(ids)} both carry `{k}`" for _, k, ids in sort_ties) +
     f". The sort is stable, so they keep the order of the document; the rule for the member sequence says so.")
j = report(
    os.path.join(OUTDIR, "csf-coverage-report.md"),
    os.path.join(OUTDIR, "csf-coverage-report.json"),
    "NIST CSF 2.0 -> Semantic Core: Coverage Report (computed)",
    f"Source: **{cat['metadata']['title']}** framework v{VER} (OSCAL rendition "
    f"{cat['metadata']['version']}, OSCAL {cat['metadata']['oscal-version']}). "
    f"Census: `drafts/gate-3-census.md` §3/§6.",
    [f"- Objects emitted: **{len(req_ids)} Requirements** (subcategories), **{nset} Sets** "
     f"({len(groups_by_id)} functions + {cat_sets} categories, {n_withdrawn_objects['category']} of them with lifecycle "
     f"`withdrawn`, + root), manifest with both digests."],
    [f"- **Functions and categories are Sets, subcategories are Requirements** - the C5 rule "
     f"(membership decides granularity), D21 taxonomy nesting at 3 levels.",
     f"- **Category statement prose -> narrative@1 on the category Set** - summary prose, not an "
     f"obligation; the requirement surface is the subcategory layer.",
     f"- **Modality `unspecified` x{mod_count['unspecified']}**: CSF outcomes are declarative "
     f"('Outcomes ... are understood and communicated') - sixth-corpus confirmation of the national "
     f"declarative pattern; force rides adoption, not mood.",
     f"- **Withdrawn items are objects with lifecycle `withdrawn`** (the author's decision of 2026-11-14; until then "
     f"an item that names a successor was no object): {len(withdrawn)} withdrawn ({len(wd_categories)} categories + "
     f"{len(wd_subcats)} subcategories - the 1.1->2.0 restructuring cut at BOTH levels), "
     f"{n_withdrawn_objects['category']} category Sets and {n_withdrawn_objects['subcategory']} Requirements, each a "
     f"member of the Set of its parent at the place its sort-id gives, with its label, title and 1.1 outcome prose. "
     f"{len(lineage_links)} of them name a successor: {sum(len(v) for v in succ_replaces.values())} `replaces` entries on "
     f"Requirements/Sets + {sum(len(v) for v in fn_replaces.values())} on function Sets (ID.GV, incorporated into "
     f"the function GV - the sa-12->SR pattern) (incorporated_into->merged-into, moved_to->renamed), each naming "
     f"the withdrawn item's own object. Chains x{len(wd_chain)}, dangling x{len(wd_dangling)}.",
     f"- **Implementation examples -> examples@1** x{n_examples} (ids kept - the CSF example numbering "
     f"is citable); **risk-party -> csf@1** x{n_riskparty_values} values on x{n_riskparty} items (remarks carried; "
     f"an item that is a risk of the first and of the third party carries both, as a list).",
     obligated_party_line(PARTY, PARTY_ORIGIN, PARTY_DEFAULT, PARTY_WHY),
     lifecycle_default_line(LIFECYCLE_DEFAULT),
     f"- **Payload free text language-tagged**: " + ", ".join(f"{k} x{v}" for k, v in sorted(lang_wraps.items())) + "."],
    [f"- **Rel-code spelling divergence (source finding)**: CSF 2.0 uses `incorporated_into`/`moved_to` "
     f"(underscores) where SP 800-53 Rev 5 uses `incorporated-into`/`moved-to` (hyphens) - same "
     f"publisher, same semantic, two spellings. REPORTED upstream.",
     f"- **Fragment marker missing x{n_hashless}** (source finding): " +
     (f"none of the {n_lineage_links} successor addresses of this rendition carries the fragment marker - DE.DP-04's "
      f"is `DE.AE-06` (a relative URI reference) where a reference inside the document is `#DE.AE-06`"
      if n_hashless and n_hashless == n_lineage_links else
      f"DE.DP-04's successor href is `DE.AE-06` (a relative URI reference) where every sibling writes `#DE.AE-06`") +
     f" - resolves only by lenient parsing. REPORTED upstream.",
     f"- **{len(withdrawn)} of {len(by_id)} controls are withdrawn** ({len(wd_categories)} categories, "
     f"{len(wd_subcats)} subcategories) - the catalog carries its 1.1-restructuring residue in-band; the "
     f"successor graph (`replaces[]`) carries the migration map of every withdrawn item that names a successor.",
     f"- Declarative corpus #6: unspecified x{mod_count['unspecified']} of {len(req_ids)} - CSF states "
     f"outcomes; obligation is an adoption artifact (baseline Sets in profiles), exactly the "
     f"ISM/CIS/CyFun/C5 pattern.",
     *ledger_lines],
    rows, unmapped,
    {"source-version": VER,
     "objects-emitted": {"requirements": len(req_ids), "sets": nset},
     "withdrawn": {"count": len(withdrawn), "categories": wd_categories, "subcategories": len(wd_subcats),
                   "successor-edges": sum(len(v) for v in succ_replaces.values()),
                   "function-set-edges": sum(len(v) for v in fn_replaces.values()),
                   "hashless-hrefs": n_hashless,
                   "chains": wd_chain, "dangling": wd_dangling,
                   "objects-with-lifecycle-withdrawn": [e["id"] for e in wd_objects]},
     "modality": dict(mod_count), "examples": n_examples,
     "risk-party": n_riskparty, "risk-party-values": n_riskparty_values,
     "obligated-party": obligated_party_record(PARTY, PARTY_ORIGIN, PARTY_DEFAULT),
     "lifecycle-default": LIFECYCLE_DEFAULT,
     "lang-wraps": dict(lang_wraps),
     "ledger": {"file": LEDGER_FILE, "leaf-values": LEDGER["leaf-values"], "totals": LT,
                "verification-failures": len(LEDGER["verification-failures"]),
                "rules": dict(sorted(rules_used.items())),
                "not-content": [{"kind": kind, "rule": rule, "count": n} for (kind, rule), n in sorted(not_content.items())],
                "declared-drops": [{"path": path, "count": n, "reason": reason, "example": value, "reading": READING.get((path, reason), "")}
                                   for (path, reason), (n, value) in drops.items()],
                "written-without-a-source": {"object-leaf-values": OUT_LEAVES, "count": sum(OWN.values()),
                                             "by-pointer": dict(sorted(OWN.items()))}}})
with open(os.path.join(OUTDIR, "csf-coverage-report.md"), "a", encoding="utf-8") as f:
    f.write("\n## What is no content (conversion ledger)\n\n"
            "A name that only selects a field, a namespace, an id that another value gives exactly. Each rule was "
            "checked on every value it is stated for, and a value shares the fate of what it rests on.\n\n"
            "| kind | rule | count |\n|---|---|---:|\n" +
            ("".join(f"| {kind} | {rule} | {n:,} |\n" for (kind, rule), n in sorted(not_content.items())) or "| | *(none)* | 0 |\n") +
            "\n## Declared drops that remain (conversion ledger)\n\n"
            "A value that reached no destination, for a declared reason. None is left since the author's decisions of "
            "2026-11-14: each drop the first ledger had declared is carried now, or stays out as an orphan by a rule the ledger checks.\n\n" +
            ("| source path | count | declared reason | example | reading |\n|---|---:|---|---|---|\n" +
             "".join(f"| `{path}` | {n:,} | {reason} | `{value}` | {READING.get((path, reason), '')} |\n" for (path, reason), (n, value) in drops.items())
             if drops else "*(none)*\n") +
            "\n## Unaccounted source values (conversion ledger)\n\n"
            "No destination, no rule and no declared reason. A run that lists a value here ends with a non-zero exit.\n\n" +
            ("| path | count | first value |\n|---|---:|---|\n" +
             "".join(f"| `{u['path']}` | {u['count']:,} | `{u['pointers'][0]}` |\n" for u in BY_PATH["unaccounted-paths"])
             if BY_PATH["unaccounted-paths"] else "*(none)*\n"))
if j["totals"]["leaf-values"] != LEDGER["leaf-values"]:        # the path map and the ledger read one source
    wiring.append(f"the path map counts {j['totals']['leaf-values']} source leaf values and the ledger {LEDGER['leaf-values']}")
print(f"reqs: {len(req_ids)}  sets: {nset}  leaves: {j['totals']['leaf-values']:,}  "
      f"mapped: {j['totals']['mapped']:,}  UNMAPPED: {j['totals']['unmapped']}")
print(f"withdrawn: {len(withdrawn)}  edges: {sum(len(v) for v in succ_replaces.values())}  "
      f"objects: {len(wd_objects)}  chains: {len(wd_chain)}  dangling: {len(wd_dangling)}")
print(f"ledger: copied {LT['copied']}, transformed {LT['transformed']}, no content {LT['not-content']}, dropped "
      f"{LT['intentionally-dropped']}, unaccounted {LT['unaccounted']}; "
      f"failed checks {len(LEDGER['verification-failures'])}")
if unmapped:
    for p, n in unmapped[:30]: print("  UNMAPPED", p, "x", n)
for x in LEDGER["verification-failures"][:20]: print("  LEDGER CHECK FAILED", json.dumps(x, ensure_ascii=False), file=sys.stderr)
for u in BY_PATH["unaccounted-paths"][:20]: print(f"  UNACCOUNTED {u['path']} x{u['count']}, first {u['pointers'][0]}", file=sys.stderr)
for x in wiring: print("  LEDGER WIRING", x, file=sys.stderr)
if wiring:
    raise SystemExit(f"convert_csf.py: {len(wiring)} wiring check(s) of the conversion ledger failed")
ledger_gate(LEDGER, "convert_csf.py")
