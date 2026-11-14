#!/usr/bin/env python3
"""NIST CSF 2.0 (OSCAL catalog) -> Semantic Core bundle.
Census: drafts/gate-3-census.md §3/§6 (2026-07-22). 6 functions + 34
categories -> Sets (the C5 rule: membership decides granularity; category
statement prose -> narrative facet on the Set); 94 live subcategories ->
Requirements (outcome prose, modality `unspecified` - sixth-corpus
confirmation of the declarative pattern); 91 withdrawn (1.1->2.0
restructuring) dropped, lineage inverted onto successor `replaces[]`;
implementation examples -> examples@1; risk-party -> csf@1.
Coverage target: 0.

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
transformed by a named rule, dropped for a declared reason, or unaccounted.
Its record is `csf-conversion-ledger.json`, one row per source path and
outcome. A claim of the ledger that does not hold on the written files, or
a declared drop that reaches further than it says, ends the run with a
non-zero exit. Unaccounted values are counted and listed, and the run
exits 0: they are the queue of decisions, not a failure of the run."""
import json, os, re, sys, collections
from oscal_conv_lib import make_T, slug, Bundle, inventory, coverage, report, walk_controls
from oscal_conv_lib import known_arguments, out_dir, obligated_party, obligated_party_line, obligated_party_record
from oscal_conv_lib import Ledger, ledger_by_path

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
LEDGER_FILE = "csf-conversion-ledger.json"

lang_wraps = collections.Counter()
T = make_T("en", lang_wraps)

# The conversion ledger (oscal_conv_lib.Ledger): every string and integer of
# the source carries its origin from here on. A value handed on unchanged is
# recorded as a copy when the bundle is accounted for at the end. A value
# this script computes is stated where it is computed, with D(rule, function,
# inputs...): the function is pure, so the ledger applies it to the source
# again and compares the result with the written file. Nothing here changes
# what is written: the bundle is byte for byte the one this script wrote
# before the ledger existed.
led = Ledger()
D = led.derive
cat = led.source("csf", {"catalog": json.load(open(SRC, encoding="utf-8"))["catalog"]})["catalog"]
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

def withdrawn_ref(wid, status, href, successor):
    """Four source values meet here: the id of the withdrawn item, its status,
    the address its link gives and the id of the object the entry is written
    on. The rule gives no value - and the run stops - unless the item is
    withdrawn and the link names that object."""
    return mint(wid) if status == "withdrawn" and href.lstrip("#") == successor else None

controls = list(walk_controls(cat))
by_id = {c["id"]: c for c, _, _ in controls}
withdrawn = {c["id"] for c, _, _ in controls
             if prop(c, "status") and prop(c, "status")["value"] == "withdrawn"}

# ---------- withdrawal inversion (underscore rels - the census 7.1 finding) ----------
# A withdrawn item is not emitted. What the bundle carries of it is its
# lineage, written on the successor each of its links names: its id (as the
# `ref` of the entry), the link's relation (as `mode`), and its label, title
# and statement prose in the annotation. An entry is built where it is
# written (lineage(), below), because the rule for `ref` takes the id of the
# object that carries it.
groups_by_id = {g["id"]: g for g in cat.get("groups", []) or []}
succ_replaces = collections.defaultdict(list)   # successor id -> [(withdrawn item, link, {label, title, prose?})]
fn_replaces = collections.defaultdict(list)     # function-level successor (ID.GV -> GV)
wd_chain, wd_dangling = [], []
wd_placed = set()                               # withdrawn items that have an entry on a successor
n_hashless = n_lineage_links = 0
for c, _, _ in controls:
    if c["id"] not in withdrawn: continue
    for l in c.get("links", []) or []:
        rel, href = l.get("rel"), (l.get("href") or "")
        if rel not in MODE: continue
        n_lineage_links += 1
        if not href.startswith("#"): n_hashless += 1   # fragment marker missing (source finding)
        href = href.lstrip("#")
        lab = prop(c, "label")
        st = next((p for p in c.get("parts", []) or [] if p.get("name") == "statement"), {})
        rest = {"label": lab["value"] if lab else c["id"], "title": c.get("title", "")}
        if st.get("prose"):        # CSF tombstones keep their 1.1 outcome prose - carry it
            rest["prose"] = st["prose"]
        if href in withdrawn:
            wd_chain.append((c["id"], href)); continue
        if href in by_id:
            succ_replaces[href].append((c, l, rest)); wd_placed.add(c["id"])
        elif href in groups_by_id:
            fn_replaces[href].append((c, l, rest)); wd_placed.add(c["id"])
        else:
            wd_dangling.append((c["id"], href))
wd_no_successor = [c["id"] for c, _, _ in controls if c["id"] in withdrawn and c["id"] not in wd_placed]

def lineage(obj, entries, own_id):
    """Writes the inverted lineage on the successor `obj`, whose source id is
    `own_id`: `replaces[]`, and the same entries with label, title and prose
    as the `nist-withdrawal` annotation."""
    built = [{"ref": D(R_REF, withdrawn_ref, c["id"], prop(c, "status")["value"], l["href"], own_id),
              "mode": D(R_MODE, lineage_mode, l["rel"]), **rest} for c, l, rest in entries]
    obj["replaces"] = [{"ref": e["ref"], "mode": e["mode"]} for e in built]
    obj["annotations"] = {"nist-withdrawal": [dict(e) for e in built]}

# Declared drop, case (a): the path map itself says a withdrawn item is not
# carried. Declared value by value and not by path, because on every one of
# these paths the values of the live items ARE carried or are open: a drop
# by path would hide a live value that is lost. Named here is only what no
# withdrawn item carries. Its id, label, title, statement prose and links
# are what the lineage carries: where one of those has no destination (a
# withdrawn item that no link gives a successor) it stays unaccounted.
DROP_WITHDRAWN = ("stated by the path map (`withdrawn: dropped, lineage inverted`; `status->tombstone drop`): a withdrawn "
                  "item is not emitted; the bundle carries its lineage on its successor - id, label, title, statement "
                  "prose and each link - and this value is none of those: ")
W_CLASS, W_PROP_NAME, W_PART_ID, W_PART_NAME = "its class", "the name of one of its props", "the id of its statement part", "the name of its statement part"
W_SORT_ID = "its sort-id (a withdrawn item is a member of no Set; among live siblings its place stays empty in their sequence)"
W_STATUS = "its status, where no link names a successor"
WITHDRAWN_DROPS = {W_CLASS: ".class", W_PROP_NAME: ".props[].name", W_SORT_ID: ".props[].value", W_STATUS: ".props[].value",
                   W_PART_ID: ".parts[].id", W_PART_NAME: ".parts[].name"}       # what is dropped -> the end of the path it stands on
for c, _, _ in controls:
    if c["id"] not in withdrawn: continue
    if "class" in c: led.drop_value(c["class"], DROP_WITHDRAWN + W_CLASS)
    for p in c.get("props", []) or []:
        if p.get("name") in ("sort-id", "label", "status"): led.drop_value(p["name"], DROP_WITHDRAWN + W_PROP_NAME)
        if p.get("name") == "sort-id": led.drop_value(p["value"], DROP_WITHDRAWN + W_SORT_ID)
        # the status is dropped only where no link names a successor: elsewhere it is an input of the rule for `ref`
        if p.get("name") == "status": led.drop_value(p["value"], DROP_WITHDRAWN + W_STATUS)
    for p in c.get("parts", []) or []:
        if p.get("name") != "statement": continue
        if "id" in p: led.drop_value(p["id"], DROP_WITHDRAWN + W_PART_ID)
        led.drop_value(p["name"], DROP_WITHDRAWN + W_PART_NAME)

# ---------- convert ----------
bundle = Bundle(os.path.join(OUTDIR, "csf-core-bundle"))
mod_count = collections.Counter()
req_ids = {}
n_examples = n_riskparty = n_riskparty_more = 0

def statement_prose(c):
    """-> (the prose of the statement part, its id or None where it has none)"""
    st = next((p for p in c.get("parts", []) or [] if p.get("name") == "statement"), {})
    return st.get("prose", ""), st.get("id")

def facets_of(c):
    global n_examples, n_riskparty, n_riskparty_more
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
        # found by the ledger, not fixed here (the fix changes the bundle): csf@1 holds one
        # risk-party, and a subcategory may carry two. The others are counted for the report.
        n_riskparty_more += len(prop(c, "risk-party", all_=True)) - 1
    return f

def convert_subcat(c):
    prose, sid = statement_prose(c)
    rid = D(R_REQ, mint, c["id"])
    lab = prop(c, "label")
    if sid is None: stmt = "statement"                                  # no id on the part: the converter's own word
    elif sid.startswith(c["id"] + "_"): stmt = D(R_STMT, statement_id, sid, c["id"])
    else: stmt = sid
    req = {"id": rid, "version": VER, "label": lab["value"] if lab else c["id"],
           "lifecycle": "active", "title": c.get("title", c["id"]),
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
    sk = prop(x, "sort-id")
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
wd_categories = [c["id"] for g in cat.get("groups", []) or []
                 for c in g.get("controls", []) or [] if c["id"] in withdrawn]
wd_subcats = [s["id"] for g in cat.get("groups", []) or [] for c in g.get("controls", []) or []
              for s in c.get("controls", []) or [] if s["id"] in withdrawn]
group_keys, groups_in_order = in_order("root", cat.get("groups", []) or [])
for gi, g in groups_in_order:
    fn_members = []
    for c in (c for c in g.get("controls", []) or [] if c["id"] in withdrawn):
        # withdrawn category: dropped, lineage inverted like any tombstone
        orphans = [s["id"] for s in c.get("controls", []) or [] if s["id"] not in withdrawn]
        if orphans:               # live subcats under a withdrawn category would be data loss - guard
            raise SystemExit(f"live subcategories under withdrawn category {c['id']}: {orphans}")
    # a function's members are its live categories; their sequence counts those only
    live_keys, live_in_order = in_order(g["id"], [c for c in g.get("controls", []) or [] if c["id"] not in withdrawn])
    for ci, c in live_in_order:
        # category: a Set; its statement prose -> narrative facet on the Set
        prose, _ = statement_prose(c)
        suri = D(R_CAT, category_uri, c["id"])
        # withdrawn subcats: lineage already inverted; dropped from membership, but counted in the sequence
        sub_keys, subs_in_order = in_order(c["id"], c.get("controls", []) or [])
        members = [{"ref": convert_subcat(s), "sequence": D(R_SEQ_SUB, place, sortkey(s), sub_keys, si)}
                   for si, s in subs_in_order if s["id"] not in withdrawn]
        lab = prop(c, "label")
        sobj = {"id": suri, "version": VER, "lifecycle": "active",
                "title": c.get("title", c["id"]), "label": lab["value"] if lab else c["id"],
                "members": members}
        fx = {}
        if prose: fx[F_NARR] = {"guidance": [T(prose, "category-statement")]}
        fx.update(facets_of(c))
        if fx: sobj["facets"] = fx
        if succ_replaces.get(c["id"]):
            lineage(sobj, succ_replaces[c["id"]], c["id"])
        bundle.add(D(R_PATH, lambda i: f"objects/set/category-{slug(i)}.json", c["id"]), sobj)
        cat_sets += 1
        fn_members.append({"ref": suri, "sequence": D(R_SEQ, place, sortkey(c), live_keys, ci)})
    furi = D(R_FN, function_uri, g["id"])
    lab = prop(g, "label")
    fobj = {"id": furi, "version": VER, "lifecycle": "active",
            "title": g.get("title", g["id"]), "label": lab["value"] if lab else g["id"],
            "members": fn_members}
    over = [p for p in g.get("parts", []) or [] if p.get("name") == "overview"]
    if over:
        fobj["facets"] = {F_NARR: {"guidance": [T(p.get("prose", ""), "overview") for p in over]}}
    if fn_replaces.get(g["id"]):                 # ID.GV "moved to GV": function-level successor
        lineage(fobj, fn_replaces[g["id"]], g["id"])
    bundle.add(D(R_PATH, lambda i: f"objects/set/function-{slug(i)}.json", g["id"]), fobj)
    root_members.append({"ref": furi, "sequence": D(R_SEQ, place, sortkey(g), group_keys, gi)})

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
manifest = bundle.write({"source": cat["metadata"]["title"], "source-version": VER,
                         "source-doc-version": cat["metadata"]["version"],
                         "source-oscal-version": cat["metadata"]["oscal-version"],
                         "published": cat["metadata"].get("published"),
                         "converter": "convert_csf.py v0.1",
                         "namespace-note": "https://ns.nist.gov/csf minted by converter (no version in the URI; "
                                           "lineage is D2's job) pending a NIST-published URI"})

# ---------- the ledger: every source value, checked against the files just written ----------
# Declared drops, case (b): the classes the author decided for the IFA corpus
# on 2026-11-13 (register, "Amendments - the value-level check of the
# converters"). Each pattern names paths on which this converter carries
# nothing, so none of them can hide a value that is lost beside carried ones;
# the run checks that below. Everything else without a destination stays
# unaccounted until somebody decides it.
AS_FOR_IFA = "as decided for IFA on 2026-11-13: "
DROP_UUID = AS_FOR_IFA + ("the uuid of a source element identifies it inside the source document only; JASCON objects "
                          "get URIs minted from the ids of the source, and the uuid itself is not carried")
DROP_REVISIONS = AS_FOR_IFA + "revision history of the source document: bookkeeping of the source, not content of the framework"
DROP_DIRECTORY = AS_FOR_IFA + ("the source's directory of parties and roles: a party is a landmark URI and there is no "
                               "party object (register, backlog #16); the bundle names none of these parties")
DROP_BACK_MATTER = AS_FOR_IFA + ("a back-matter resource is a link to another rendition of the source; its title and "
                                 "address are carried in references@1, the media type of the link is not")
DROP_CLASS = AS_FOR_IFA + ("a type tag of a structural element, the class of a function, category or subcategory: "
                           "the bundle says by its shape (the type of the object and its URI) what kind of thing the element is")
DROP_PART_NAME = AS_FOR_IFA + ("a type tag of a structural element, the name of a part (statement, example, overview): "
                               "the bundle says by its shape (where the prose stands) what kind of part it was")
PATH_DROPS = [          # (pattern over the source path, the class as the report counts it, the reason)
 (r"\.uuid$", "uuids of the source document", DROP_UUID),
 (r"^csf\.catalog\.metadata\.revisions\[\]\.", "revision history", DROP_REVISIONS),
 (r"^csf\.catalog\.metadata\.(parties|roles)\[\]\.", "directory of parties and roles", DROP_DIRECTORY),
 (r"^csf\.catalog\.back-matter\.resources\[\]\.rlinks\[\]\.media-type$", "back-matter resources", DROP_BACK_MATTER),
 (r"^csf\.catalog\.groups\[\](\.controls\[\])*\.class$", "type tags, the class of an element", DROP_CLASS),
 (r"^csf\.catalog\.groups\[\](\.controls\[\])*\.parts\[\]\.name$", "type tags, the name of a part", DROP_PART_NAME),
]
for pattern, _, reason in PATH_DROPS: led.drop(pattern, reason)
LEDGER = led.account(bundle.out, {**bundle.objects, "content-manifest.json": manifest})
LT = LEDGER["totals"]
BY_PATH = ledger_by_path(LEDGER)
with open(os.path.join(OUTDIR, LEDGER_FILE), "w", encoding="utf-8") as f:
    json.dump(BY_PATH, f, indent=1, ensure_ascii=False); f.write("\n")

# what the entries say, counted for the report
drops = collections.Counter(e["reason"] for e in LEDGER["entries"] if e["outcome"] == "intentionally-dropped")
drops_a = {r[len(DROP_WITHDRAWN):]: n for r, n in sorted(drops.items()) if r.startswith(DROP_WITHDRAWN)}
drops_b = {label: drops[reason] for _, label, reason in PATH_DROPS if drops[reason]}
rules_used = collections.Counter(rule for rule, _, _ in {(d["rule"], d["object"], d["pointer"])       # rule -> the values it wrote
                                                         for e in LEDGER["entries"] for d in e.get("destinations", []) if "rule" in d})

# Wiring checks. The ledger checks every claim of a destination; it cannot
# check a declaration that is too wide, or a record that is not this run's.
# Each of the checks below answers a defect that was put into a copy of this
# script on purpose and passed with exit code 0 before the check existed.
# A check that fails stops the run with a non-zero exit, after the reports
# are written.
wiring = []
# every declared drop is of kind (a) or (b)
if sum(drops_a.values()) + sum(drops_b.values()) != LT["intentionally-dropped"]:
    wiring.append("a declared drop is neither stated by the path map nor a class decided for IFA")
# a drop by path is declared only for paths on which nothing is carried: on a
# path with carried values it would report a lost value as dropped on purpose
carried_paths = {e["path"] for e in LEDGER["entries"] if e["outcome"] in ("copied", "transformed")}
by_pattern = {reason for _, _, reason in PATH_DROPS}
for p in sorted({e["path"] for e in LEDGER["entries"] if e.get("reason") in by_pattern} & carried_paths):
    wiring.append(f"a drop declared by path covers {p}, on which other values are carried: a value lost there would "
                  f"read as dropped on purpose; declare such a drop value by value")
# the drop of a withdrawn item reaches the values it names and no others
for what, p in sorted({(e["reason"][len(DROP_WITHDRAWN):], e["path"]) for e in LEDGER["entries"]
                       if e.get("reason", "").startswith(DROP_WITHDRAWN)}):
    if what not in WITHDRAWN_DROPS or not p.endswith(WITHDRAWN_DROPS[what]):
        wiring.append(f"the drop declared for a withdrawn item as `{what}` covers {p}, where no such value stands: the "
                      f"declaration covers more than it names (what the lineage carries of a withdrawn item - id, label, "
                      f"title, statement prose, links - is never dropped by it)")
# the file on disk is the record of this run, not one left by an earlier run or written from an earlier accounting
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
# The path map says where each source path is MEANT to go. Until the ledger
# existed it claimed a destination for every path. The sentences below say
# what the ledger found: where a value is not carried, the row says so.
CTL = r"^csf\.catalog\.groups\[\]\.controls\[\]\."
RULES = [
 (r"^csf\.catalog\.metadata\.(title|version|oscal-version|published)$", "L1",
  "bundle manifest provenance (`source`, `source-doc-version`, `source-oscal-version`, `published`); the title "
  "is the title of the root Set as well"),
 (r"^csf\.catalog\.uuid$", "L1", "not carried: the uuid of the source document (declared drop in the ledger)"),
 (r"^csf\.catalog\.metadata\.revisions\[\]\.", "L1",
  "not carried: revision history of the source document (declared drop in the ledger)"),
 (r"^csf\.catalog\.metadata\.(parties|roles)\[\]\.", "L1",
  "not carried: the source's directory of parties and roles (declared drop in the ledger)"),
 (r"^csf\.catalog\.metadata\.", "L1",
  "not carried and not decided (unaccounted in the ledger): `last-modified`, the props of the document, its links "
  "to the back-matter resources, and who is its publisher, contact and author"),
 (r"^csf\.catalog\.back-matter\.resources\[\]\.(title|rlinks\[\]\.href)$", "L1",
  "references@1 facet on the root Set (title; the address of the first link as url)"),
 (r"^csf\.catalog\.back-matter\.", "L1",
  "not carried: the uuid of a resource and the media type of its link (declared drops in the ledger)"),
 (r"^csf\.catalog\.groups\[\]\.id$", "L1", "function Set id (URI mint)"),
 (r"^csf\.catalog\.groups\[\]\.title$", "L1", "function Set title"),
 (r"^csf\.catalog\.groups\[\]\.class$", "L1",
  "not carried: `function` is a type tag, the Set says it by its URI (declared drop in the ledger)"),
 (r"^csf\.catalog\.groups\[\]\.props\[\]\.value$", "L1",
  "label -> function Set label; sort-id -> the sequence of the function in the root Set"),
 (r"^csf\.catalog\.groups\[\]\.props\[\]\.name$", "L1",
  "not carried: the name selects the prop (`label`, `sort-id`); unaccounted in the ledger"),
 (r"^csf\.catalog\.groups\[\]\.parts\[\]\.prose$", "L2",
  "function overview -> narrative@1 guidance on the function Set (language-tagged)"),
 (r"^csf\.catalog\.groups\[\]\.parts\[\]\.name$", "L2",
  "not carried: `overview` is a type tag of the part (declared drop in the ledger)"),
 (r"^csf\.catalog\.groups\[\]\.parts\[\]\.id$", "L2",
  "not carried: the id of the overview part; unaccounted in the ledger"),
 (CTL + r"id$", "L1",
  "category Set / subcategory Requirement id (URI mint); withdrawn: dropped, lineage inverted - the id is the `ref` "
  "of the entry in the replaces[] and the nist-withdrawal annotation of each successor, and where no link gives a "
  "successor nothing of the item is carried"),
 (CTL + r"title$", "L1",
  "category Set / subcategory Requirement title; withdrawn: dropped, lineage inverted - the title stands in the "
  "nist-withdrawal annotation of each successor, and nowhere where no link gives a successor"),
 (CTL + r"class$", "L1",
  "not carried: `category` / `subcategory` is a type tag, the object says it by its type and URI (declared drop "
  "in the ledger)"),
 (CTL + r"props\[\]\.value$", "L1",
  "label->label (withdrawn: `label` in the successor's annotation); sort-id->Set sequence (withdrawn: not "
  "carried); risk-party->csf@1, the FIRST risk-party prop of a subcategory only - a second one is not carried; "
  "status->tombstone drop + successor replaces[] (a withdrawn item is not emitted, its links become entries on "
  "its successors)"),
 (CTL + r"props\[\]\.name$", "L1",
  "not carried: the name selects the prop (`label`, `sort-id`, `risk-party`, `status`); unaccounted in the "
  "ledger, on a withdrawn item a declared drop"),
 (CTL + r"props\[\]\.ns$", "L1",
  "not carried: the namespace of the `risk-party` prop name; unaccounted in the ledger"),
 (CTL + r"props\[\]\.remarks$", "L2",
  "risk-party remark -> csf@1 (carried verbatim), of the FIRST risk-party prop only; the remark of a second one "
  "is not carried"),
 (CTL + r"links\[\]\.rel$", "L1",
  "incorporated_into/moved_to (UNDERSCORE spelling - source finding) -> `mode` (merged-into/renamed) of the entry "
  "in the successor's replaces[] + nist-withdrawal annotation"),
 (CTL + r"links\[\]\.href$", "L1",
  "names the successor: the entry stands on the Requirement or Set with that id, and its `ref` is written by a "
  "rule that holds only if the address names that object"),
 (CTL + r"parts\[\]\.prose$", "L1",
  "subcategory statement -> statements[0] (modality unspecified); category statement -> narrative@1 on "
  "the Set; example parts -> examples@1 (language-tagged); withdrawn: statement prose -> `prose` in the "
  "nist-withdrawal annotation of each successor"),
 (CTL + r"parts\[\]\.id$", "L1",
  "subcategory statement id -> statements[0].id, without the control prefix; example id -> examples@1; not "
  "carried: the id of a category's statement part (unaccounted in the ledger) and of a withdrawn item's (declared drop)"),
 (CTL + r"parts\[\]\.name$", "L1",
  "not carried: `statement` / `example` is a type tag of the part, the bundle says it by where the prose stands "
  "(declared drop in the ledger)"),
 (CTL + r"parts\[\]\.ns$", "L1",
  "not carried: the namespace of the `example` part name; unaccounted in the ledger"),
]
rows, unmapped = coverage(paths, RULES)

nset = sum(1 for rel in bundle.objects if "/set/" in rel)
own_fields = ", ".join(f"`{p}` x{n}" for p, n in sorted(OWN.items()))
ledger_lines = [
     f"- **Conversion ledger (measured per source value; backlog #41)**: each of the {LEDGER['leaf-values']:,} source leaf "
     f"values was followed into the written bundle. **{LT['copied']:,} copied** (the value stands, with its type, at the "
     f"destination named, read back from the written file), **{LT['transformed']:,} transformed** (one of "
     f"{len(rules_used)} named rules made the destination from it; the rule was applied to the source again and "
     f"compared), **{LT['intentionally-dropped']:,} intentionally dropped** (a declared reason), "
     f"**{LT['unaccounted']:,} unaccounted** (no destination and no declared reason). Checks that failed: "
     f"{len(LEDGER['verification-failures'])}. The path map below reads {sum(paths.values()):,} of "
     f"{sum(paths.values()):,} for the same conversion: it counts paths with a declared destination, the ledger counts "
     f"values that arrived. The record is `{LEDGER_FILE}`: one row per source path and outcome, with its count, an "
     f"example and the destinations or the reasons. The entry of each single value is not committed; every row is a "
     f"count over entries that were checked in the run that wrote it.",
     f"- **Declared drops, two kinds** (the reasons and their counts are listed near the end of this report). "
     f"(a) **{sum(drops_a.values()):,}** stated by the converter's own path map: a withdrawn item is not emitted, and "
     f"of it the bundle carries the lineage on its successor - id, label, title, statement prose and links. Dropped "
     f"with it: " + ("; ".join(f"{k} x{n}" for k, n in drops_a.items()) or "nothing, the source has no withdrawn item") + ". "
     f"(b) **{sum(drops_b.values()):,}** in the classes decided for the IFA corpus on 2026-11-13: " +
     "; ".join(f"{k} x{n}" for k, n in drops_b.items()) +
     f". Nothing else is declared: a value without a destination that is in neither kind is unaccounted and listed by "
     f"path at the end of this report.",
     f"- **What the ledger cannot see**: it follows source values into the bundle, not the other way. Counted the "
     f"other way for this run: of the {OUT_LEAVES:,} leaf values of the {len(bundle.objects)} objects, "
     f"{OUT_LEAVES - sum(OWN.values()):,} are a source value or made from one by a rule; the other "
     f"{sum(OWN.values()):,} are written by the converter with no source value behind them: {own_fields} (the "
     f"version `{VER}`, the lifecycle `active`, the modality `unspecified`, the obligated party `{PARTY}` and the id "
     f"of the root Set). The namespace `{NS}` in every minted URI, the facet names and the manifest's own fields "
     f"(`source-version`, `converter`, `namespace-note`, the digests) are the converter's as well."]
if n_riskparty_more:
    ledger_lines.append(
     f"- **A second risk-party is not carried x{n_riskparty_more}** (found by the ledger; a loss, not fixed here "
     f"because the fix changes the bundle): the converter reads the first `risk-party` prop of an item, and csf@1 holds "
     f"one value. Where a subcategory carries two (in the CSF: `1st` and `3rd`), the second value and its remark reach "
     f"no object. The ledger lists them as unaccounted under `...props[].value` and `...props[].remarks`.")
if wd_no_successor:
    ledger_lines.append(
     f"- **Withdrawn without a successor x{len(wd_no_successor)}** (found by the ledger): no `incorporated_into` or "
     f"`moved_to` link names a successor in the catalogue for {', '.join(wd_no_successor)}, so there is no object to "
     f"write the lineage on. Nothing of such an item reaches the bundle: its id, title, label and, where it has one, "
     f"its statement prose are unaccounted. Every other withdrawn item has an entry on at least one successor.")
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
     f"chains x{len(wd_chain)}, dangling x{len(wd_dangling)}, without a successor link x{len(wd_no_successor)}; "
     f"no live subcategory sits under a withdrawn category (asserted).",
     f"- **Implementation examples -> examples@1** x{n_examples} (ids kept - the CSF example numbering "
     f"is citable); **risk-party -> csf@1** x{n_riskparty} (remarks carried; the first risk-party prop of a "
     f"subcategory only).",
     obligated_party_line(PARTY, PARTY_ORIGIN, PARTY_DEFAULT, PARTY_WHY),
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
     f"- **{len(withdrawn)} of 219 controls are withdrawn tombstones** ({len(wd_categories)} categories, "
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
                   "chains": wd_chain, "dangling": wd_dangling, "without-successor": wd_no_successor},
     "modality": dict(mod_count), "examples": n_examples, "risk-party": n_riskparty,
     "risk-party-not-carried": n_riskparty_more,
     "obligated-party": obligated_party_record(PARTY, PARTY_ORIGIN, PARTY_DEFAULT),
     "lang-wraps": dict(lang_wraps),
     "ledger": {"file": LEDGER_FILE, "leaf-values": LEDGER["leaf-values"], "totals": LT,
                "verification-failures": len(LEDGER["verification-failures"]),
                "rules": dict(sorted(rules_used.items())),
                "declared-drops": {"stated-by-the-path-map": {"count": sum(drops_a.values()), "withdrawn-item": drops_a},
                                   "as-decided-for-ifa-2026-11-13": {"count": sum(drops_b.values()), "classes": drops_b}},
                "written-without-a-source": {"object-leaf-values": OUT_LEAVES, "count": sum(OWN.values()),
                                             "by-pointer": dict(sorted(OWN.items()))}}})
with open(os.path.join(OUTDIR, "csf-coverage-report.md"), "a", encoding="utf-8") as f:
    f.write("\n## Declared drops (conversion ledger)\n\n"
            "No destination, and a declared reason. (a) is stated by the converter's own path map: a withdrawn item is "
            "not emitted; the bundle carries its lineage on its successor (id, label, title, statement prose, links) and "
            "drops the rest of it. (b) is a class the author decided for the IFA corpus on 2026-11-13. The reason of "
            f"every row, in full, is in `{LEDGER_FILE}`.\n\n"
            "| kind | what is dropped, and why | count |\n|---|---|---:|\n" +
            "".join(f"| (a) | of a withdrawn item: {what} | {n:,} |\n" for what, n in drops_a.items()) +
            "".join(f"| (b) | {reason[len(AS_FOR_IFA):]} | {drops[reason]:,} |\n" for _, _, reason in PATH_DROPS if drops[reason]) +
            "\n## Unaccounted source values (conversion ledger)\n\n"
            "No destination and no declared reason. Each is either a value the converter loses, or one it leaves out "
            f"without a decision. The count of every path and outcome is in `{LEDGER_FILE}`.\n\n" +
            ("| path | count | first value |\n|---|---:|---|\n" +
             "".join(f"| `{u['path']}` | {u['count']:,} | `{u['pointers'][0]}` |\n" for u in BY_PATH["unaccounted-paths"])
             if BY_PATH["unaccounted-paths"] else "*(none)*\n"))
if j["totals"]["leaf-values"] != LEDGER["leaf-values"]:        # the path map and the ledger read one source
    wiring.append(f"the path map counts {j['totals']['leaf-values']} source leaf values and the ledger {LEDGER['leaf-values']}")
print(f"reqs: {len(req_ids)}  sets: {nset}  leaves: {j['totals']['leaf-values']:,}  "
      f"mapped: {j['totals']['mapped']:,}  UNMAPPED: {j['totals']['unmapped']}")
print(f"withdrawn: {len(withdrawn)}  edges: {sum(len(v) for v in succ_replaces.values())}  "
      f"chains: {len(wd_chain)}  dangling: {len(wd_dangling)}")
print(f"ledger: copied {LT['copied']}, transformed {LT['transformed']}, intentionally dropped "
      f"{LT['intentionally-dropped']} ({sum(drops_a.values())} stated by the path map, {sum(drops_b.values())} as decided "
      f"for IFA), unaccounted {LT['unaccounted']}; failed checks {len(LEDGER['verification-failures'])}")
if unmapped:
    for p, n in unmapped[:30]: print("  UNMAPPED", p, "x", n)
if LEDGER["verification-failures"] or wiring:
    for x in LEDGER["verification-failures"][:20]: print("  LEDGER CHECK FAILED", json.dumps(x, ensure_ascii=False), file=sys.stderr)
    for x in wiring: print("  LEDGER WIRING", x, file=sys.stderr)
    raise SystemExit(f"convert_csf.py: {len(LEDGER['verification-failures'])} claim(s) of the conversion ledger do not hold "
                     f"on the written files, {len(wiring)} wiring check(s) failed")
