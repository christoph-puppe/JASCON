#!/usr/bin/env python3
"""NIST SP 800-53 Rev 5 catalog + 800-53B baselines -> Semantic Core bundle.
Census: drafts/gate-3-census.md (2026-07-22). 20 families -> Sets; the
controls and enhancements in force -> Requirements (statement items
flattened, modality `must` corpus rule); every withdrawn control -> a
Requirement with lifecycle `withdrawn` (E1, 2026-11-14), and where it names a
successor, the successor's kernel `replaces[]` names it and its one
statement is made from its links (R2); SP 800-53A layer -> sp800-53a@1 facet; two-layer ODP
params -> statement-scoped kernel parameters (declared where inserted, the
per-statement parameter rule) + odp@1 admin facet; baselines -> 4 membership
Sets; the metadata of the catalogue and of each profile -> the compat facet
on the Set that stands for the document, with the document's uuid (E3), a
profile's import and the resource it names (E4); the catalogue's author and
day -> the manifest's provenance; the back-matter resources something refers
to, as the source writes them -> references@1 on the root Set, an orphaned
one not at all (E4, checked). Coverage target: 0.

    convert_nist.py [--obligated-party URI] [--out DIR]

The source gives a control an `implementation-level` (organization, system,
or both), and the converter writes it as the party the control's statements
bind: that value is the source's and is written as it stands. For a control
without one the converter writes a party of its own,
`<namespace>/party/organization`; --obligated-party writes the caller's
party in that place and nowhere else, and the coverage report says which of
the two it was and on how many controls (backlog #74). Without arguments
the run reproduces the committed conversion byte for byte; the Validators
workflow holds it to that. --out writes the bundle, the two reports and the
ledger record somewhere else, which is where a run with another party
belongs.

The conversion ledger (backlog #41, phase E). The catalogue and the four
profiles are loaded through oscal_conv_lib.Ledger, so every leaf value of
them carries its origin for as long as the script hands it on unchanged.
What the script computes is stated where it is computed, as a named rule
with a pure function the ledger applies again to the source. After the
bundle is written every source leaf value has one of five outcomes: copied,
transformed, not content, intentionally dropped, unaccounted. The record,
one row per source path and outcome, is `sp800-53-conversion-ledger.json`
beside the reports.

The author's rule of 2026-11-14 governs the outcomes: content is never
dropped. What stays out of the bundle is no content by one of three rules
the ledger checks: a name that only selects the member a value is written
to, a namespace the mapping is written for, an id (or a label made of one)
that a stated function rebuilds exactly from a value the bundle holds. The
author decided the drops that were declared before that rule on
2026-11-14 (drafts/phase-e/entscheidungen-phase-e.md): every one of them is
carried now, and a back-matter resource nothing refers to is an orphan, by a
fourth rule the ledger checks. This script declares no drop.

The run ends with exit code 1 on an unaccounted value, on a claim the
written files do not bear out, and on a failed wiring check (a drop that
reaches further than its reason names, a sentence of the path map the
ledger contradicts, a record on disk that is not this run's). The bundle,
the reports and the record are written first, so a failed run says why."""
import json, os, re, sys, time, collections
from oscal_conv_lib import make_T, slug, Bundle, inventory, coverage, report, walk_controls
from oscal_conv_lib import known_arguments, out_dir, obligated_party, obligated_party_line, obligated_party_record
from oscal_conv_lib import Ledger, ledger_by_path, ledger_gate, document_author, document_day
from oscal_conv_lib import COMPAT, COMPAT_PROPERTIES, lifecycle_default_record, lifecycle_default_line

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SRCDIR = os.path.join(ROOT, "sources", "nist")
ARGV = sys.argv[1:]
known_arguments(ARGV, ("--obligated-party", "--out"))
OUTDIR = out_dir(ARGV, os.path.join(ROOT, "converted_examples", "US.SP800-53"))
NS = "https://ns.nist.gov/sp800-53"   # matches the corpus's existing mapping-endpoint URIs
# Whom a statement binds where the source gives no implementation level (backlog #74)
PARTY_DEFAULT = f"{NS}/party/organization"
PARTY, PARTY_ORIGIN = obligated_party(ARGV, PARTY_DEFAULT)      # (party, "converter-default" | "caller")
PARTY_SOURCE_STATES = "as the implementation level of a control"
F_NARR = f"{NS}/facet/narrative@1"
F_53A = f"{NS}/facet/sp800-53a@1"
F_ODP = f"{NS}/facet/odp@1"
F_RMF = f"{NS}/facet/rmf@1"
F_REF = f"{NS}/facet/references@1"
F_COMPAT = COMPAT                                       # what of an OSCAL document the kernel has no member for
RMF = "http://csrc.nist.gov/ns/rmf"                      # the one prop namespace this mapping is written for

lang_wraps = collections.Counter()
T = make_T("en", lang_wraps)
INSERT = re.compile(r"\{\{\s*insert:\s*param,\s*([a-z0-9._-]+)\s*\}\}")
MDTARGET = re.compile(r"\[[^\]]+\]\(#([a-zA-Z0-9._-]+)\)")

led = Ledger()
D = led.derive
T_START = time.time()

def load(tag, filename, key):
    """-> the document under `key` of a source file; its leaves carry their origin, a boolean too (`typed`)"""
    with open(os.path.join(SRCDIR, filename), encoding="utf-8") as f: doc = json.load(f)
    return led.source(tag, {key: doc[key]}, typed=True)[key]

def tracked(v):
    """True for a value that still is a source value or the result of a stated rule"""
    return hasattr(v, "_origins")

def carried(rule, fn, value, *more):
    """-> fn(value, *more). Where the function leaves a source value as it is, the value itself is handed
    on and the ledger records a copy; where it changes it, the result is stated as `rule`."""
    new = fn(value, *more)
    if not tracked(value): return new
    return value if new == value else D(rule, fn, value, *more)

cat = load("nist", "NIST_SP-800-53_rev5_catalog.json", "catalog")
VER = cat["metadata"]["version"]
BASELINES = {b: load(b.lower(), f"NIST_SP-800-53_rev5_{b}-baseline_profile.json", "profile")
             for b in ("LOW", "MODERATE", "HIGH", "PRIVACY")}

# ---------- no declared drop (the author's decisions of 2026-11-14) ----------
# What was declared as a drop until then is carried now: the status of a
# withdrawn control is its lifecycle (E1), the uuid of a document stands in
# its compat facet (E3), a profile's import and the resource it names on its
# baseline Set (E4), the three print labels the rule does not give in the
# compat facet of their Requirement (E7). A back-matter resource that nothing
# in the catalogue refers to is an orphan (E4/R1), a claim the ledger checks.

def norm(p):
    p = re.sub(r"(\.controls\[\])+", ".controls[]", p)
    p = re.sub(r"(\.parts\[\])+", ".parts[]", p)
    return p

paths = collections.Counter()
inventory({"catalog": cat}, "nist", paths, normalize=norm)
for b, prof in BASELINES.items():
    inventory({"profile": prof}, b.lower(), paths, normalize=norm)

# ---------- what is no content, by a rule the ledger checks ----------
# A name that only selects where a value is written, a namespace, an id (or a
# label made of one) that a function rebuilds exactly. A selector shares the
# fate of the value it selects: beside a value that is lost it is unaccounted.
N_PROP_NAME = "the name of a prop selects the member its value is written to"
N_PROP_CLASS = "the class of a prop selects which value of that name it is; the mapping reads exactly this class"
N_PROP_NS = "the namespace of a prop qualifies its name; the mapping reads the name in exactly this namespace"
N_PART_NAME = "the name of a part selects where the part's content is written"
N_LINK_REL = "the rel of a link of an assessment objective selects the member `assessment-for`"
N_GROUP_CLASS = "the class `family` of a group selects that the group is written as a family Set"
N_CLASS = "the class of a control, rebuilt from its id: `SP800-53-enhancement` where the id has a dot, else `SP800-53`"
N_LABEL_PADDED = "the zero-padded label of a control, rebuilt from its label: every number padded to two digits"
N_LABEL_53A = "the SP 800-53A label of a control, rebuilt from its label: every number padded to two digits"
N_ID_GUIDANCE = "the id of a guidance part, rebuilt from the control id: <control id>_gdn"
N_ID_STATEMENT = "the id of a statement part without text of its own, rebuilt from the control id: <control id>_smt"
N_ID_METHOD = "the id of an assessment method, rebuilt from the control id and the method: <control id>_asm-<method in lower case>"
N_ID_OVERVIEW = "the id of a family's overview part, rebuilt from the group id: <group id>_ovw"
N_ORPHAN = ("a back-matter resource that nothing in the catalogue refers to (no `#uuid` outside it) is orphaned and "
            "not carried (author, 2026-11-14)")
N_ITEM_LABEL = ("the print label of a statement item, rebuilt from the item id: its last segment, written `x.` on the "
                "first two levels of a control, `(x)` on its third level and in an enhancement")
PROP_NAMES = ("label", "sort-id", "status", "implementation-level", "contributes-to-assurance",
              "alt-identifier", "alt-label", "aggregates", "method")          # the prop names this mapping reads
PART_NAMES = ("statement", "item", "guidance", "assessment-objective", "assessment-method", "assessment-objects",
              "overview")                                                     # the part names it places

def picked(node, name, cls=None, ns=None):
    """-> the props of `node` with exactly this name, class and namespace (None: the prop has none). The mapping
    reads a prop through here and nowhere else, so the name, the class and the namespace of a prop it reads are
    what selected the rule for its value: they are declared as that, and are no content beside a value that is
    accounted for. A prop no call asks for is read by nobody; its leaves stay unaccounted."""
    out = []
    for p in node.get("props", []) or []:
        if p.get("name") != name or p.get("class") != cls or p.get("ns") != ns: continue
        if tracked(p.get("value")):
            led.selector(p["name"], N_PROP_NAME, p["value"], among=PROP_NAMES)
            if cls is not None: led.selector(p["class"], N_PROP_CLASS, p["value"], among=(cls,))
            if ns is not None: led.namespace(p["ns"], N_PROP_NS, (ns,), p["name"])
        out.append(p)
    return out

def prop(node, name, cls=None, ns=None, all_=False):
    out = [p["value"] for p in picked(node, name, cls, ns)]
    return out if all_ else (out[0] if out else None)

rebuilt_by = collections.Counter()     # rule -> source values declared as rebuilt by it
rebuilt_seen = set()

def rebuilt(value, rule, fn, *inputs):
    """Declares a source value to be an id, or a label made of one, that fn(*inputs) gives exactly. The ledger
    applies the function to the source again; a value it does not give is a claim that does not hold."""
    if not tracked(value): return
    led.rebuilt(value, rule, fn, *inputs)
    if value._origins[0] not in rebuilt_seen:
        rebuilt_seen.add(value._origins[0]); rebuilt_by[rule] += 1

def given_by(value, rule, fn, *inputs):
    """-> True where nothing has to be written: there is no value, or the rule gives it exactly (then it is
    declared and the ledger checks it). False: the rule does not give this value, and the caller writes it."""
    if value is None: return True
    if fn(*inputs) != value: return False
    rebuilt(value, rule, fn, *inputs); return True

def mint(src_id):
    return f"{NS}/req/{src_id.upper()}"

# ---------- the rules: each a name and a pure function of source values ----------
R_REQ = "requirement URI from the control id"
R_LINK = "requirement URI from the control a link names"
R_REFERENCE = "a reference link resolved by uuid: the first link of the back-matter resource it names"
R_INSERT = "prose with each parameter insertion {{ insert: param, x }} written as the token {param:x}"
R_PARAGRAPH = "assessment objects: one entry per paragraph of the part's prose, trimmed (insertions as tokens)"
R_STATEMENT = "statement id without the control prefix"
R_PARTY = "obligated party URI from the implementation level"
R_CARDINALITY = "parameter cardinality `many` from the selection's how-many `one-or-more`"
R_LINEAGE = "lineage inverted: the URI of a withdrawn control, written on the successor its link names"
R_MODE = "lineage mode from the link's rel (incorporated-into -> merged-into, moved-to -> renamed)"
R_LIFECYCLE = "lifecycle from the status the source states: `withdrawn`, the kernel's own word"
R_WITHDRAWN = ("the statement of a withdrawn control that names a successor, from its links: `Incorporated into X.` "
               "or `Moved to X.`, the targets in source order (`X and Y`, `X, Y, and Z`), each by the label the "
               "source gives it for a reader (a statement item: its control's label and the item's label without "
               "the full stop)")
R_FAMILY = "family Set URI from the group id"
R_SEQUENCE = "member sequence: ten times the control's place in its family, ordered by sort-id"
R_SAME_RELATION = "a relation the control states twice is written once"
R_ASSURANCE = "the prop value `true` or `false`, written as a JSON boolean"
R_ASSESSED = "the statement part an `assessment-for` link names, as a statement id (the part id without the control prefix)"
R_ASSESSED_REQ = "requirement URI from the control whose part an `assessment-for` link names, where that is another control"
R_AUTHOR = ("author of the catalogue: the party its metadata names as its author (the role `creator`, else `prepared-by`, "
            "else the one party it names; oscal_conv_lib.document_author), as a URI of its name under the namespace")
R_DAY = "date of the catalogue: the day of its last-modified"

def req_uri(cid): return D(R_REQ, mint, cid)
def _link_ref(href): return mint(href.lstrip("#"))
def _resolved(ref, uuid, url):
    """three source values meet here: the link, the uuid of the resource it names, and that resource's link"""
    return url if ref.lstrip("#") == uuid else None
def _rewrite(prose):
    return INSERT.sub(lambda m: "{param:" + m.group(1) + "}", prose or "")
def _paragraphs(prose): return [x.strip() for x in re.split(r"\n\s*\n", prose) if x.strip()]
def _paragraph(prose, i): return _rewrite(_paragraphs(prose)[i])
def _statement_id(sid, cid): return sid[len(cid) + 1:] if sid.startswith(cid + "_") else sid
def _party(level): return f"{NS}/party/{level}"
def _cardinality(how_many): return {"one-or-more": "many"}[how_many]
def _lineage_ref(withdrawn_id, href, successor_id):
    """the withdrawn control's URI, if the link names this successor (a control, one of its statements, or a family)"""
    return mint(withdrawn_id) if href.lstrip("#").split("_smt")[0] == successor_id else None
def _mode(rel): return MODE[rel]
def _into(href): return "smt" + href.lstrip("#").split("_smt")[1]
LIFECYCLE = {"withdrawn": "withdrawn"}
def _lifecycle(status): return LIFECYCLE[status]
def _part_req(href): return mint(href.lstrip("#").split("_smt")[0])
def _family_uri(gid): return f"{NS}/set/family/{gid}"
PARTIES = PARTY_DEFAULT.rsplit("/", 1)[0] + "/"          # where the landmark URI of a party stands (as in convert_ism.py)
def _author_uri(name): return PARTIES + slug(name)       # the author of the document: no statement is bound to it
def _day(last_modified): return last_modified[:10]
BOOLEAN = {"true": True, "false": False}
def _boolean(value): return BOOLEAN[value]
# ... and the functions of the rules that rebuild an id or a label
def zero_padded(label):
    """`AC-2(10)` -> `AC-02(10)`, `ac-2.10` -> `ac-02.10`: every number padded to two digits"""
    return re.sub(r"[0-9]+", lambda m: m.group(0).zfill(2), label)
def _class_of(cid): return "SP800-53-enhancement" if "." in cid else "SP800-53"
def _gdn_id(cid): return cid + "_gdn"
def _smt_id(cid): return cid + "_smt"
def _asm_id(cid, method): return f"{cid}_asm-{method.lower()}"
def _ovw_id(gid): return gid + "_ovw"
ITEM_FORMS = {False: ("{}.", "{}.", "({})"), True: ("({})", "({})")}      # by level, of a control / of an enhancement
def _item_label(item_id, cid):
    if not (item_id or "").startswith(cid + "_smt."): return None
    tail = item_id[len(cid) + len("_smt."):].split(".")
    forms = ITEM_FORMS["." in cid]
    return forms[len(tail) - 1].format(tail[-1]) if len(tail) <= len(forms) else None

# The ledger applies a rule again, so a rule that discards a part of a value agrees with itself and passes. The
# two rules that rewrite a text are therefore held to what they say they do: with the insertion syntax put back,
# the text is the source's (for the assessment objects: the paragraphs joined, white space aside).
INSERTED = re.compile(r"\{param:([a-z0-9._-]+)\}")
def _as_source(text, found=INSERTED): return found.sub(lambda m: "{{ insert: param, " + m.group(1) + " }}", text or "")
def _squashed(text): return re.sub(r"\s+", "", text)
text_changed = []                       # texts of which a rule changed more than the insertion syntax
def where_from(value):
    return "#/".join((value._origins[0][0], "/".join(str(x) for x in value._origins[0][1]))) if tracked(value) else repr(value[:60])

def rewrite(prose, used=None):
    """{{ insert: param, x }} -> {param:x}. A markdown link stays as the source wrote it."""
    if used is not None: used.update(INSERT.findall(prose or ""))
    new = carried(R_INSERT, _rewrite, prose)
    if _as_source(new) != _as_source(prose, INSERT): text_changed.append(where_from(prose))
    return new

def strings(node):
    if isinstance(node, dict):
        for v in node.values(): yield from strings(v)
    elif isinstance(node, list):
        for v in node: yield from strings(v)
    elif isinstance(node, str): yield node

# back-matter: the resources as the source writes them, each with its uuid, stand on the root Set (references@1;
# the convention of the ISM converter). A markdown link `(#uuid)` in a text of the bundle, and a link of the
# document metadata, names one by that uuid; a `reference` link of a control is resolved to its first link.
MD_LINKS = [t for s in strings(cat) for t in MDTARGET.findall(s)]       # the target of every markdown #-link
RESOURCES = (cat.get("back-matter") or {}).get("resources") or []
RES = {r["uuid"]: r for r in RESOURCES}                                  # uuid -> the resource as the source writes it
def res_url(uuid):
    """the first link of a resource, as the source writes it ("" where it gives none)"""
    return ((RES[uuid].get("rlinks") or [{}])[0]).get("href", "")
# E4/R1: a resource is referred to where `#uuid` stands in a string of the catalogue outside the resource. The others
# are orphans: not carried, by a claim the ledger checks against the whole document.
_OUTSIDE = "\x00".join(strings({k: v for k, v in cat.items() if k != "back-matter"}))
_RES_TEXT = ["\x00".join(strings(r)) for r in RESOURCES]
def referred_to(i, uuid):
    ref = "#" + uuid
    return ref in _OUTSIDE or any(ref in t for j, t in enumerate(_RES_TEXT) if j != i)
RESOURCES_KEPT, ORPHANS = [], []
for i, r in enumerate(RESOURCES):
    if referred_to(i, r["uuid"]): RESOURCES_KEPT.append(r)
    else: ORPHANS.append(r); led.orphan(r["uuid"], N_ORPHAN)

controls = list(walk_controls(cat))
by_id = {c["id"]: c for c, _, _ in controls}
# Rule 7 of the rework (no invented meaning): the one status this mapping knows is `withdrawn`, which is the
# kernel's own word. A control with another status is not written as something it is not called.
unknown_status = sorted({str(prop(c, "status")) for c, _, _ in controls} - {"None", "withdrawn"})
if unknown_status:
    raise SystemExit(f"convert_nist.py: the catalogue gives controls the status {unknown_status}; this mapping knows "
                     f"`withdrawn` only and writes no lifecycle the source does not state")
withdrawn = {c["id"] for c, _, _ in controls if prop(c, "status") == "withdrawn"}
groups_by_id = {g["id"]: g for g in cat.get("groups", []) or []}
params_global = {pm["id"]: pm for c, _, _ in controls for pm in c.get("params", []) or []}
def ordered(compat):
    """a compat payload with its members in the order of the library's one compat schema"""
    return {k: compat[k] for k in COMPAT_PROPERTIES if k in compat}
def all_parts(node):
    for p in node.get("parts", []) or []:
        yield p
        yield from all_parts(p)
part_text = {p["id"]: bool(p.get("prose")) for c, _, _ in controls for p in all_parts(c) if "id" in p}

# what the markdown links in the texts name; they stay in the text as the source wrote them
def named_by(target):
    return ("a back-matter resource" if target in RES else "a withdrawn control" if target in withdrawn
            else "another control" if target in by_id else "a family" if target in groups_by_id
            else "a statement of a control" if target in part_text else "a parameter" if target in params_global
            else "nothing the catalogue defines")
md_targets = collections.Counter(named_by(t) for t in MD_LINKS)

class_written = [0]                     # controls whose class the rule does not give: written in the compat facet
def class_given(c):
    """-> True where the class of a control is rebuilt from its id (or it has none); False: it has to be written"""
    return given_by(c.get("class"), N_CLASS, _class_of, c["id"])

# ---------- withdrawal inversion: successor.replaces[] ----------
MODE = {"incorporated-into": "merged-into", "moved-to": "renamed"}
succ_replaces = collections.defaultdict(list)   # successor cid -> entries
fam_replaces = collections.defaultdict(list)    # successor group id -> entries (moved-to a family)
wd_chain, wd_dangling = [], []
wd_no_successor = []                            # withdrawn controls that name no successor
for c, _, _ in controls:
    if c["id"] not in withdrawn: continue
    landed = 0
    for l in c.get("links", []) or []:
        rel, href = l.get("rel"), (l.get("href") or "").lstrip("#")
        if rel not in MODE: continue
        target = href.split("_smt")[0]           # a link to a statement names its control
        successor = None if target in withdrawn else by_id.get(target) or groups_by_id.get(target)
        e = {"ref": D(R_LINEAGE, _lineage_ref, c["id"], l["href"], successor["id"]) if successor else mint(c["id"]),
             "mode": D(R_MODE, _mode, l["rel"])}
        if target in withdrawn:
            wd_chain.append((c["id"], target)); continue
        if target in by_id:
            succ_replaces[target].append(e); landed += 1
        elif target in groups_by_id:             # sa-12 -> #sr: successor is a whole family
            fam_replaces[target].append(e); landed += 1
        else:
            wd_dangling.append((c["id"], href))
    if not landed: wd_no_successor.append(c["id"])
tombstones = withdrawn - set(wd_no_successor)    # withdrawn controls that name a successor: objects all the same (E1)
written = [(c, par, g) for c, par, g in controls]

# R2: the statement of a withdrawn control that names a successor, made from its links. The label of a target is the
# one the source gives it for a reader; a statement item is named by its control's label and its own.
def _reader_label(node):
    return next((str(p["value"]) for p in node.get("props", []) or [] if p.get("name") == "label" and "class" not in p), None)
READER = {**{g["id"]: _reader_label(g) for g in groups_by_id.values()}, **{cid: _reader_label(c) for cid, c in by_id.items()}}
ITEMS = {p["id"]: p for c, _, _ in controls for p in all_parts(c) if "id" in p}
VERB = {"incorporated-into": "Incorporated into", "moved-to": "Moved to"}
def _target_label(href):
    t = href.lstrip("#")
    # the statement part as a whole has no label in SP 800-53 (none of the pinned catalogue has): its control's
    if "_smt" in t: return READER[t.split("_smt")[0]] + (_reader_label(ITEMS[t]) or "").rstrip(".")
    return READER[t]
def _withdrawn_prose(*rel_href):
    """`rel, href, rel, href, ...` of a withdrawn control's lineage links -> the sentence of its one statement"""
    rels, names = rel_href[0::2], [_target_label(h) for h in rel_href[1::2]]
    if len(set(rels)) != 1: raise SystemExit(f"convert_nist.py: a withdrawn control names successors by {sorted(set(rels))}")
    joined = names[0] if len(names) == 1 else " and ".join(names) if len(names) == 2 else ", ".join(names[:-1]) + ", and " + names[-1]
    return f"{VERB[rels[0]]} {joined}."

# ---------- parameter declarations ----------
def param_decl(pm):
    d = {"name": pm["id"]}
    if "select" in pm:
        d["type"] = "choice"
        d["choices"] = [{"value": rewrite(ch)} for ch in pm["select"].get("choice", [])]
        if pm["select"].get("how-many") == "one-or-more":
            d["cardinality"] = D(R_CARDINALITY, _cardinality, pm["select"]["how-many"])
    else:
        d["type"] = "string"
    if pm.get("label"):
        d["label"] = pm["label"]
    return d

# ---------- objectives / methods trees ----------
def placed(part):
    """A part the converter puts where the bundle's shape says what it is (a statement, the guidance, an
    objective, a method, its objects, an overview): its `name` selected that place and is no content beside
    what the part holds itself. A part with a name this mapping does not place is a claim that does not hold."""
    own = {k: v for k, v in part.items() if k not in ("name", "parts")}
    if tracked(part.get("name")): led.selector(part["name"], N_PART_NAME, own or part, among=PART_NAMES)

assessed_kind = collections.Counter()   # what an `assessment-for` link names -> links
def assessed(link, cid):
    """The statement an assessment objective assesses, as the source's link states it: the id of the statement
    part by the rule for statement ids, and the Requirement where the part is another control's. A link that
    names no statement part is not written here and stays unaccounted."""
    href = link["href"]
    target = href.lstrip("#")
    if "_smt" not in target: return None
    led.selector(link["rel"], N_LINK_REL, href, among=("assessment-for",))
    a = {}
    if target.split("_smt")[0] != cid: a["requirement-ref"] = D(R_ASSESSED_REQ, _part_req, href)
    a["statement-id"] = D(R_ASSESSED, _into, href)
    assessed_kind[("nothing the catalogue defines" if target not in part_text
                   else "a statement of another control" if "requirement-ref" in a
                   else "a statement of the same control" if part_text[target]
                   else "the statement part of the same control as a whole, which has no text of its own")] += 1
    return a

assessed_apart = [0]                    # objectives that name another statement than the objective above them
def obj_tree(pt, used, cid, above=None):
    placed(pt)
    node = {}
    if pt.get("id"): node["id"] = pt["id"]
    lab = prop(pt, "label", cls="sp800-53a")
    if lab: node["label"] = lab
    links = [a for a in (assessed(l, cid) for l in pt.get("links", []) or [] if l.get("rel") == "assessment-for") if a]
    if links: node["assessment-for"] = links
    if links and above and links != above: assessed_apart[0] += 1
    if pt.get("prose"): node["prose"] = T(rewrite(pt["prose"], used), "objective")
    kids = [obj_tree(s, used, cid, links) for s in pt.get("parts", []) or []]
    if kids: node["children"] = kids
    return node

def methods_of(c, used):
    out = []
    for pt in c.get("parts", []) or []:
        if pt.get("name") != "assessment-method": continue
        placed(pt)
        m = {"method": prop(pt, "method", ns=RMF), "label": prop(pt, "label", cls="sp800-53a")}
        if m["method"] is not None: rebuilt(pt.get("id"), N_ID_METHOD, _asm_id, c["id"], m["method"])
        objs = [s for s in pt.get("parts", []) or [] if s.get("name") == "assessment-objects"]
        if objs:
            placed(objs[0])
            prose = objs[0].get("prose", "")
            m["objects"] = []
            for i, x in enumerate(_paragraphs(prose)):
                rewrite(x, used)                 # notes the parameters the paragraph inserts
                m["objects"].append(T(carried(R_PARAGRAPH, _paragraph, prose, i), "assessment-objects"))
            if _squashed(_as_source("".join(o["en"] for o in m["objects"]))) != _squashed(_as_source(prose, INSERT)):
                text_changed.append(where_from(prose))
        out.append({k: v for k, v in m.items() if v})
    return out

# ---------- statements: flatten prose-bearing statement/item nodes ----------
labels_kept = collections.defaultdict(list)    # control id -> the items whose print label the rule does not give
def item_label(pt, cid):
    """the print label of a statement item (`a.`, `1.`, `(a)`): rebuilt from the item id where the rule gives it
    exactly. Where it does not (E7), the item's id and its label prop are carried in the compat facet `parts` of the
    Requirement, in the source's own shape."""
    for p in picked(pt, "label"):
        if given_by(p["value"], N_ITEM_LABEL, _item_label, pt.get("id"), cid): continue
        labels_kept[cid].append({"id": pt["id"], "props": [p]})

def flat_statements(c):
    out = []
    def walk(pt):
        placed(pt)
        if pt.get("prose"):
            out.append(pt)
        elif pt.get("name") == "statement":      # it only groups its items: the bundle has no statement for it
            rebuilt(pt.get("id"), N_ID_STATEMENT, _smt_id, c["id"])
        if pt.get("name") == "item": item_label(pt, c["id"])
        for s in pt.get("parts", []) or []:
            walk(s)
    for pt in c.get("parts", []) or []:
        if pt.get("name") == "statement":
            walk(pt)
    return out

# ---------- convert the controls ----------
mod_count = collections.Counter()
decl_hist = collections.Counter()      # #10: statements-declaring-a-param histogram
multi_decl = []                        # params inserted in >=2 statements
no_site = collections.Counter()        # params without a statement insertion site
facet_only, nowhere = [], []           # ... of those: bound in 53A objectives / bound nowhere
cross_param = []                       # prose inserts another control's param
op_default = 0                         # controls without an implementation level
op_default_stmts = 0                   # ... and their statements, which carry PARTY
lvl_count = collections.Counter()      # implementation levels as the source combines them
rel_count = collections.Counter()
REF_NO_LINK = "reference to a resource without a link (compat `links`)"
req_ids = {}
n_53a = 0
n_formal = 0                           # formal ODP labels written
stated = []                            # Requirements whose lifecycle is the source's status (E8)
n_inserted = 0                         # parameter insertions in statement text

for c, parents, gchain in written:
    cid = c["id"]
    rid = req_uri(cid)
    # lifecycle: the source's own word where it states a status. A control it gives none is in force; the kernel
    # requires a lifecycle, and the converter writes `active` for it.
    status = prop(c, "status")
    lifecycle = D(R_LIFECYCLE, _lifecycle, status) if status is not None else "active"
    if status is not None: stated.append(rid)
    plain = prop(c, "label")
    label = plain if plain is not None else cid.upper()
    for cls, rule in (("zero-padded", N_LABEL_PADDED), ("sp800-53a", N_LABEL_53A)):
        for v in prop(c, "label", cls=cls, all_=True): rebuilt(v, rule, zero_padded, label)
    # obligated parties: the control's implementation level where the source
    # gives one; where it gives none, the converter's default or the caller's
    lvls = prop(c, "implementation-level", ns=RMF, all_=True)
    if lvls:
        parties = [D(R_PARTY, _party, v) for v in lvls]
    else:
        parties = [PARTY]; op_default += 1
    lvl_count[" + ".join(lvls) or "(none)"] += 1
    # A control in force is read as `must` (the corpus rule). The statement of a withdrawn control says why it
    # was withdrawn and states no obligation: `unspecified`.
    modality = "must" if status is None else "unspecified"
    def statement(sid, prose):
        """the one place that writes whom a statement binds (backlog #74)"""
        return {"id": sid, "modality": modality, "obligated-parties": parties, "prose": {"en": prose}}
    # statements + per-statement param declaration
    params = {pm["id"]: pm for pm in c.get("params", []) or []}
    stmts, declared_any = [], set()
    for pt in flat_statements(c):
        used = set()
        prose = rewrite(pt["prose"], used)
        n_inserted += len(INSERT.findall(pt["prose"]))
        sid = carried(R_STATEMENT, _statement_id, pt.get("id", f"{cid}_smt"), cid)
        s = statement(sid, prose)
        decls = []
        for u in sorted(used):
            if u in params:
                decls.append(param_decl(params[u]))
            elif u in params_global:   # cross-control insertion (source irregularity)
                decls.append(param_decl(params_global[u]))
                cross_param.append((cid, u))
        if decls: s["parameters"] = decls
        declared_any |= used
        stmts.append(s)
        mod_count[modality] += 1
        if not lvls: op_default_stmts += 1
    # R2: a withdrawn control the source gives no statement keeps the one the kernel requires, made from its links
    lineage = [l for l in c.get("links", []) or [] if l.get("rel") in MODE]
    if status is not None and not stmts and lineage:
        stmts.append(statement("smt", D(R_WITHDRAWN, _withdrawn_prose, *[x for l in lineage for x in (l["rel"], l["href"])])))
        mod_count[modality] += 1
        if not lvls: op_default_stmts += 1
    # params without a statement insertion site -> declare on first statement (counted)
    rest = [pid for pid in params if pid not in declared_any]
    if rest and stmts:
        extra = [param_decl(params[p]) for p in sorted(rest)]
        stmts[0].setdefault("parameters", []).extend(extra)
        for p in rest: no_site[p] += 1
    # #10 measure: in how many statements is each param inserted?
    for pid in params:
        n = sum(1 for s in stmts for _ in [0]
                if ("{param:" + pid + "}") in s["prose"]["en"])
        decl_hist[n] += 1
        if n >= 2: multi_decl.append((cid, pid, n))
    req = {"id": rid, "version": VER, "label": label, "lifecycle": lifecycle,
           "title": c.get("title", cid), "statements": stmts}
    # facets
    facets = {}
    guid = []
    for p in c.get("parts", []) or []:
        if p.get("name") == "guidance" and p.get("prose"):
            placed(p); rebuilt(p.get("id"), N_ID_GUIDANCE, _gdn_id, cid)
            guid.append(T(rewrite(p["prose"]), "guidance"))
    if guid: facets[F_NARR] = {"guidance": guid}
    used_f = set()
    objectives = [obj_tree(p, used_f, cid) for p in c.get("parts", []) or []
                  if p.get("name") == "assessment-objective"]
    methods = methods_of(c, used_f)
    for p in rest:
        (facet_only if p in used_f else nowhere).append(p)
    if objectives or methods:
        f = {}
        if objectives: f["objectives"] = objectives
        if methods: f["methods"] = methods
        facets[F_53A] = f; n_53a += 1
    odp_admin = {}
    for pid, pm in params.items():
        a = {}
        if pm.get("guidelines"):
            a["guidelines"] = [T(rewrite(g.get("prose", "")), "guideline") for g in pm["guidelines"]]
        alts = prop(pm, "alt-identifier", all_=True)
        if alts: a["alt-identifiers"] = alts
        al = prop(pm, "alt-label", cls="sp800-53")
        if al: a["alt-label"] = al
        aggs = prop(pm, "aggregates", ns=RMF, all_=True)
        if aggs: a["aggregates"] = aggs
        formal = prop(pm, "label", cls="sp800-53a")      # the formal ODP label, as the source gives it
        if formal: a["sp800-53a-label"] = formal; n_formal += 1
        if a: odp_admin[pid] = a
    if odp_admin: facets[F_ODP] = {"params": odp_admin}
    for v in prop(c, "contributes-to-assurance", ns=RMF, all_=True):
        if v in BOOLEAN: facets[F_RMF] = {"contributes-to-assurance": D(R_ASSURANCE, _boolean, v)}
    compat = {}                          # what the kernel has no member for, in the source's own shape
    if not class_given(c):               # a class the rule does not give is written as the source gives it
        compat["class"] = c["class"]; class_written[0] += 1
    if labels_kept.get(cid): compat["parts"] = labels_kept[cid]
    req["facets"] = facets               # here, so that a Requirement's members keep their order; filled up below
    # relations
    rels = []
    for l in c.get("links", []) or []:
        rel, href = l.get("rel"), (l.get("href") or "").lstrip("#")
        # the link's own `rel` is written as the relation type: it is the same word
        if rel in ("related", "required") and href in by_id:
            rels.append({"type": rel, "ref": D(R_LINK, _link_ref, l["href"])}); rel_count[rel] += 1
        elif rel == "reference" and href in RES and res_url(href):
            rels.append({"type": rel, "ref": D(R_REFERENCE, _resolved, l["href"], RES[href]["uuid"], res_url(href))})
            rel_count["reference"] += 1
        elif rel == "reference" and href in RES:  # E14: the resource gives no link to resolve to; the link as it stands
            compat.setdefault("links", []).append(l); rel_count[REF_NO_LINK] += 1
        elif rel in MODE:                        # on the successor's `replaces[]`, and in this control's statement (R2)
            rel_count[f"{rel} (the successor's `replaces[]`, and the statement of this control)"] += 1
        else:
            rel_count[f"not written ({rel})"] += 1
    if rels:
        seen = {}; ded = []
        for r in rels:
            k = (r["type"], r["ref"])
            if k not in seen: seen[k] = r; ded.append(r)
            else: led.same(r, seen[k], R_SAME_RELATION)
        req["relations"] = ded
    if compat: facets[F_COMPAT] = ordered(compat)
    if not facets: del req["facets"]
    # withdrawal inversion: the successor names the withdrawn control, which is an object of its own (E1)
    if succ_replaces.get(cid):
        req["replaces"] = [{"ref": e["ref"], "mode": e["mode"]} for e in succ_replaces[cid]]
    req_ids[cid] = (rid, f"objects/req/{slug(cid)}.json", req)

bundle = Bundle(os.path.join(OUTDIR, "sp800-53-core-bundle"))
for cid, (rid, bp, req) in req_ids.items():
    bundle.add(bp, req)

def document_metadata(md):
    """What of a document's OSCAL `metadata` no kernel member holds, in the source's own shape and with the
    source's values (the convention of all converters since 2026-11-14): the Set that stands for the document
    carries it in the compat facet. `title` and `version` are the Set's own members."""
    return {k: v for k, v in md.items() if k not in ("title", "version")}

# ---------- family Sets + root ----------
def sortkey(cid):
    return prop(by_id[cid], "sort-id") or cid

root_members, fam_sets = [], 0
for g in cat.get("groups", []):
    fam = [c["id"] for c, _, gg in written if gg and gg[0]["id"] == g["id"]]
    fam.sort(key=sortkey)
    suri = D(R_FAMILY, _family_uri, g["id"])
    if tracked(g.get("class")):
        led.selector(g["class"], N_GROUP_CLASS, {"id": g["id"], "title": g.get("title")}, among=("family",))
    def place(key, keys=tuple(str(sortkey(cid)) for cid in fam)):
        """pure: where a sort key stands among the sort keys of its family, in steps of ten"""
        return (keys.index(key) + 1) * 10
    sobj = {"id": suri, "version": VER, "lifecycle": "active",
            "title": g.get("title", g["id"]),
            "label": (prop(g, "label") or g["id"].upper()),
            "members": [{"ref": req_uri(cid),      # the rule is stated where it gives the number written: keys that differ
                         "sequence": D(R_SEQUENCE, place, sortkey(cid)) if place(sortkey(cid)) == (i + 1) * 10 else (i + 1) * 10}
                        for i, cid in enumerate(fam)]}
    over = [p for p in g.get("parts", []) or [] if p.get("name") == "overview"]
    if over:
        entries = []
        for p in over:
            placed(p); rebuilt(p.get("id"), N_ID_OVERVIEW, _ovw_id, g["id"])
            entry = {}
            if p.get("title"): entry["title"] = T(p["title"], "overview-title")
            if p.get("prose"): entry["prose"] = T(rewrite(p["prose"]), "overview")
            entries.append(entry)
        sobj["facets"] = {F_NARR: {"overview": entries}}
    if fam_replaces.get(g["id"]):                # sa-12 "moved to SR family": Set-level successor
        entries = fam_replaces[g["id"]]
        sobj["replaces"] = [{"ref": e["ref"], "mode": e["mode"]} for e in entries]
    bundle.add(f"objects/set/family-{slug(g['id'])}.json", sobj)
    root_members.append({"ref": suri, "sequence": len(root_members) * 10 + 10})
    fam_sets += 1
root = {"id": f"{NS}/set/root", "version": VER, "lifecycle": "active",
        "title": cat["metadata"]["title"], "members": root_members}
root_facets = {}
if RESOURCES_KEPT: root_facets[F_REF] = {"resources": RESOURCES_KEPT}
root_compat = {"uuid": cat["uuid"]}                                       # E3
if document_metadata(cat["metadata"]): root_compat["metadata"] = document_metadata(cat["metadata"])
root_facets[F_COMPAT] = ordered(root_compat)
root["facets"] = root_facets
bundle.add("objects/set/root.json", root)

# ---------- baseline Sets ----------
bl_missing = collections.defaultdict(list)
for b, prof in BASELINES.items():
    ids = prof["imports"][0]["include-controls"][0]["with-ids"]
    members = []
    for i, cid in enumerate(ids):
        if cid not in req_ids:
            bl_missing[b].append(cid); continue
        members.append({"ref": req_uri(cid), "sequence": (i + 1) * 10})
    bset = {"id": f"{NS}/set/baseline/{b.lower()}", "version": prof["metadata"].get("version") or VER,
            "lifecycle": "active", "title": prof["metadata"]["title"], "label": b, "members": members}
    compat = {"uuid": prof["uuid"]}                               # E3
    if document_metadata(prof["metadata"]): compat["metadata"] = document_metadata(prof["metadata"])
    # E4: the import, as the source writes it (its include list is the Set's members), and the resource it names
    compat["imports"] = [{"href": imp["href"]} for imp in prof["imports"]]
    if (prof.get("back-matter") or {}).get("resources"): compat["back-matter"] = {"resources": prof["back-matter"]["resources"]}
    if "merge" in prof: compat["merge"] = prof["merge"]          # how the profile merges what it selects (a boolean)
    bset["facets"] = {F_COMPAT: ordered(compat)}
    bundle.add(f"objects/set/baseline-{b.lower()}.json", bset)

# What the ledger cannot see. It follows source values into the bundle; a value the converter writes on its own has
# no entry. They are found from the other side: every leaf value of an object that is neither a source value nor the
# result of a stated rule, by the place it stands in. Counted here, while a boolean still carries its origin.
own_values, own_example = collections.Counter(), {}
def not_from_the_source(node, place):
    if isinstance(node, dict):
        for k, v in node.items(): not_from_the_source(v, f"{place}/{k}")
    elif isinstance(node, list):
        for v in node: not_from_the_source(v, place + "/[]")
    elif not tracked(node):
        own_values[place] += 1; own_example.setdefault(place, node)
for rel in sorted(bundle.objects): not_from_the_source(bundle.objects[rel], "")

# ---------- facet stubs ----------
bundle.stub("sp800-53-narrative-stub.json", F_NARR.split("@")[0], [],
            {"guidance": {"type": "array"}, "overview": {"type": "array"}})
bundle.stub("sp800-53a-stub.json", F_53A.split("@")[0], [],
            {"objectives": {"type": "array"}, "methods": {"type": "array"}})
bundle.stub("sp800-53-odp-stub.json", F_ODP.split("@")[0], [], {"params": {"type": "object"}})
bundle.stub("sp800-53-rmf-stub.json", F_RMF.split("@")[0], [],
            {"contributes-to-assurance": {"type": "boolean"}})
_STRINGS = lambda *names: {n: {"type": "string"} for n in names}
_RESOURCE = {"type": "object", "additionalProperties": False, "required": ["uuid"],           # an OSCAL back-matter resource
             "properties": {**_STRINGS("uuid", "title", "description", "remarks"),
                            "props": {"type": "array", "items": {
                                "type": "object", "additionalProperties": False, "required": ["name", "value"],
                                "properties": _STRINGS("name", "uuid", "ns", "value", "class", "group", "remarks")}},
                            "citation": {"type": "object"},
                            "rlinks": {"type": "array", "items": {
                                "type": "object", "additionalProperties": False, "required": ["href"],
                                "properties": _STRINGS("href", "media-type")}}}}
bundle.stub("sp800-53-references-stub.json", F_REF.split("@")[0], [], {"resources": {"type": "array", "items": _RESOURCE}},
            note="NORMATIVE pinned payload schema (backlog #26): the back-matter resources of the catalogue, as the "
                 "source writes them; a link `(#uuid)` in a text of the bundle names the resource with that uuid")
bundle.pin_compat()                          # E10: the one compat schema of the repository, 1.1.0
# The manifest's provenance names the catalogue: its title, version and OSCAL version, and - by the library's rule
# for the author of an OSCAL document, as every converter pre-fills it (backlog #69) - its author and its day.
PROVENANCE = {"source": cat["metadata"]["title"], "source-version": VER,
              "source-oscal-version": cat["metadata"]["oscal-version"]}
AUTHOR = document_author(cat["metadata"])
if AUTHOR: PROVENANCE["author-ref"] = D(R_AUTHOR, _author_uri, AUTHOR["name"])
if document_day(cat["metadata"]): PROVENANCE["date"] = D(R_DAY, _day, cat["metadata"]["last-modified"])
PROVENANCE.update({"baselines": {b: p["metadata"]["version"] for b, p in BASELINES.items()},
                   "converter": "convert_nist.py v0.2",
                   "namespace-note": "https://ns.nist.gov/sp800-53 minted to match the corpus's "
                                     "pre-existing mapping-endpoint URIs; pending a NIST-published URI"})
led.resolve(bundle.objects)      # a boolean that carries its origin becomes the plain one, and its place is noted
MANIFEST = bundle.write(PROVENANCE)
LIFECYCLE_DEFAULT = lifecycle_default_record(bundle.objects, stated)      # E8

# ---------- corpus cross-check: mapping endpoints vs minted ids ----------
cited = collections.Counter()
for base, _, files in os.walk(os.path.join(ROOT, "converted_examples")):
    if "US.SP800-53" in base or "oscal-export" in base: continue
    for fn in files:
        if not fn.endswith(".json"): continue
        try:
            txt = open(os.path.join(base, fn), encoding="utf-8").read()
        except OSError:
            continue
        # carried COPIES of sp800-53 objects (the authorization-package
        # pattern) are the objects themselves, not citations - skip them
        if '"id": "https://ns.nist.gov/sp800-53/' in txt[:400]: continue
        for m in re.finditer(r'"https://ns\.nist\.gov/sp800-53/req/([A-Za-z0-9.()-]+)"', txt):
            cited[m.group(1)] += 1
minted_names = {rid.rsplit("/", 1)[-1] for cid, (rid, _, _) in req_ids.items()}
wd_names = {cid.upper() for cid in withdrawn} - minted_names       # since E1 every withdrawn control is an object
hit = {k: v for k, v in cited.items() if k in minted_names}
hit_wd = {k: v for k, v in cited.items() if k in wd_names}
miss = {k: v for k, v in cited.items() if k not in minted_names and k not in wd_names}

# ---------- the conversion ledger: where every source value went ----------
# The drops by path. Each names paths on which this converter carries
# nothing, so none of them can make a value that was lost beside carried ones
# read as dropped on purpose; the run checks that below. Where values of one
# path are carried and others are not, the drop is declared value by value at
# the place the script decides it (the status of a tombstone, an item label
# the rule does not give).
PATH_DROPS = []          # none since the author's decisions of 2026-11-14 (see the head of this script)
for pattern, reason in PATH_DROPS: led.drop(pattern, reason)
# What each reason may be declared for: the source paths a drop with that reason stands on. A declaration that
# reaches further (a whole control where its status was meant) would swallow a value that was lost.
DROP_REACH = {}
# A selector beside a value that is a declared drop is dropped with it; the ledger words its reason with this
WITH = " - of a value that is dropped: "
WITH_REACH = r"\.props\[\]\.(name|class|ns)$"
# The reading of each drop that stays declared, under the author's rule of 2026-11-14: `content`, or `not
# content, because ...`. The author decides them; the converter only lists them. (path, reason, reading)
READINGS = []
READING_WITH = "not content, because it is the name that selects a value which is a declared drop, and shares its fate"
def root_reason(reason): return reason.split(WITH)[-1]
def reading_of(path, reason):
    if WITH in reason: return READING_WITH
    return next((text for rx, why, text in READINGS if why == reason and re.search(rx, path)), None)

T_WRITTEN = time.time()
LEDGER = led.account(bundle.out, {**bundle.objects, "content-manifest.json": MANIFEST})
T_ACCOUNTED = time.time()
LT = LEDGER["totals"]
# The record. account() gives one entry per source leaf value; for 115,680 values that is some fifty megabytes,
# so what is written is one row per source path and outcome, with counts over the entries just checked. The
# payload of odp@1 is keyed by the parameter id, a source value: the key is folded, or every parameter is a row.
LEDGER_FILE = "sp800-53-conversion-ledger.json"
COLLAPSE = [(r"(odp@1/params)/[^/]+", r"\1/{parameter id}")]
RECORD = ledger_by_path(LEDGER, collapse=COLLAPSE)
with open(os.path.join(OUTDIR, LEDGER_FILE), "w", encoding="utf-8") as f:
    json.dump(RECORD, f, indent=1, ensure_ascii=False); f.write("\n")
print(f"ledger: copied {LT['copied']}, transformed {LT['transformed']}, not content {LT['not-content']}, intentionally "
      f"dropped {LT['intentionally-dropped']}, unaccounted {LT['unaccounted']}; failed checks "
      f"{len(LEDGER['verification-failures'])}  ({T_ACCOUNTED - T_WRITTEN:.1f} s to account for {LEDGER['leaf-values']:,} values)")

# ---------- what the ledger says, for the report ----------
def source_value(entry):
    """-> the source value a ledger entry is about"""
    tag, pointer = entry["source"].split("#", 1)
    node = led.docs[tag]
    for x in (p.replace("~1", "/").replace("~0", "~") for p in pointer.split("/")[1:]):
        node = node[int(x)] if isinstance(node, list) else node[x]
    return node

def pattern_of(path):
    """a source path as the reports show it: nested controls and parts under one path, the four profiles under one"""
    return re.sub(r"^(low|moderate|high|privacy)\.profile", "*.profile", norm(path))

# the rules by how many source values each accounts for, and what is no content by which rule
rule_values, rule_destinations = collections.Counter(), collections.Counter()
not_content = collections.Counter()          # (kind, rule) -> source values
declared = {}                                # (path, reason) -> the drops that stay declared
for e in LEDGER["entries"]:
    rules_here = [d["rule"] for d in e.get("destinations", []) if "rule" in d]
    rule_destinations.update(rules_here)
    rule_values.update(set(rules_here))
    if e["outcome"] == "not-content": not_content[(e["kind"], e["rule"])] += 1
    if e["outcome"] == "intentionally-dropped":
        row = declared.setdefault((pattern_of(e["path"]), e["reason"]),
                                  {"count": 0, "example": e["source"], "value": source_value(e)})
        row["count"] += 1
KIND = {"selector": "a name that selects", "namespace": "a namespace", "rebuilt-id": "an id rebuilt exactly",
        "orphan": "an orphaned element"}
declared_rows = [{"path": p, "count": row["count"], "reason": reason, "example": row["example"],
                  "example-value": row["value"], "reading": reading_of(p, reason)}
                 for (p, reason), row in sorted(declared.items(), key=lambda x: (WITH in x[0][1], -x[1]["count"], x[0]))]

# Wiring checks. The ledger checks every claim of a destination and every rule against the source and the written
# file. It cannot check a declaration that reaches too far, a path map that says something else, or a record that
# is not this run's. Each check below stands against a defect that was put into a copy of this script on purpose
# (test_convert_nist_ledger.py holds them). A check that fails stops the run with a non-zero exit, after the
# reports are written.
wiring = []
# a drop is declared with one of the reasons above, only for the paths that reason names, and has a reading
for (path, reason), row in sorted(declared.items()):
    reach = WITH_REACH if WITH in reason else DROP_REACH.get(reason)
    if root_reason(reason) not in DROP_REACH:
        wiring.append(f"a drop is declared with a reason this converter does not state: {reason!r} for {path}")
    elif not re.search(reach, path.replace("*.profile", "low.profile")):
        wiring.append(f"a drop reaches further than it names: {path} is declared as {reason!r}")
    elif reading_of(path, reason) is None:
        wiring.append(f"a declared drop has no reading for the author: {path}, {reason!r}")
# a rule that rewrites a text changes the insertion syntax and nothing else
if text_changed:
    wiring.append(f"a rule that rewrites a text changed more than the insertion syntax in {len(text_changed)} text(s): "
                  f"what it left out is in no leaf and in no count; first {text_changed[0]}")
# a drop by path is declared only for paths on which nothing is carried
carried_paths ={e["path"] for e in LEDGER["entries"] if e["outcome"] in ("copied", "transformed")}
for p in sorted({e["path"] for e in LEDGER["entries"] if e.get("reason") in {r for _, r in PATH_DROPS}} & carried_paths):
    wiring.append(f"a drop declared by path covers {p}, on which other values are carried: a value lost there would "
                  f"read as dropped on purpose; declare such a drop value by value")

OWN_WHY = [   # place pattern -> what stands behind the value, if not a source value
 (r"/lifecycle$", "the converter's default: `active` on an object the source gives no status (the kernel requires a "
                  "lifecycle; E8). The source's own `withdrawn` is written by a rule and is not counted here"),
 (r"^/statements/\[\]/id$", "`smt`: the one statement of a withdrawn control the source gives no statement part (R2)"),
 (r"/modality$", "the converter's: a statement of a control in force is read as `must` (corpus rule); the statement "
                 "of a withdrawn control states no obligation and is `unspecified`"),
 (r"/parameters/\[\]/type$", "decided by the shape of the source parameter: `choice` where it has a `select`, else `string`"),
 (r"/members/\[\]/sequence$", "the member's position: in the catalogue (root Set) or in the profile's list (baseline Sets)"),
 (r"/obligated-parties/\[\]$", "the converter's default party or the caller's, where the source gives no implementation level"),
 (r"^/id$", "the URI of the root Set and of a baseline Set, the latter from the name of the profile's file"),
 (r"^/label$", "the label of a baseline Set, from the name of the profile's file"),
]
def own_why(place): return next((why for rx, why in OWN_WHY if re.search(rx, place)), "the converter's")

# ---------- coverage ----------
# The path map: where each source path goes, in words. Each row also names
# the outcomes its sentence speaks of; the ledger's outcomes for the path are
# held against them below, and written beside the sentence. Levels: L1 a
# kernel member, L2 a facet, `not content` by a checked rule, `dropped` a
# drop that stays declared for the author to decide.
CTL = r"^nist\.catalog\.groups\[\]\.controls\[\]"
PROF = r"^(low|moderate|high|privacy)\.profile"
DROPPED, NOT_CONTENT = "dropped", "not content"
C, X, N, DR = "copied", "transformed", "not-content", "intentionally-dropped"
SEE = "see the table of declared drops"
RULES = [
 (r"^nist\.catalog\.metadata\.title$", "L1", "root Set `title`; manifest `provenance.source`", {C}),
 (r"^nist\.catalog\.metadata\.version$", "L1",
  "`version` of the root Set, of every family Set and of every Requirement; manifest `provenance.source-version`", {C}),
 (r"^nist\.catalog\.metadata\.", "L2",
  "compat facet oscal-1x@1 on the root Set, member `metadata`, in the source's own shape: last-modified, "
  "oscal-version, revisions, props, links, roles, parties, responsible-parties and whatever else the document "
  "states; oscal-version also manifest `provenance.source-oscal-version`; the name of the party the metadata names "
  "as the author -> manifest `provenance.author-ref` (a landmark URI), the day of last-modified -> manifest "
  "`provenance.date`", {C}),
 (r"^nist\.catalog\.uuid$", "L2", "compat facet oscal-1x@1 on the root Set, member `uuid` (E3)", {C}),
 (r"^nist\.catalog\.back-matter\.resources\[\]\.", "L2",
  "references@1 on the root Set: the resources something in the catalogue refers to, in the source's own shape "
  "(uuid, title, citation, rlinks with href and media-type); a markdown link `(#uuid)` in a text names one by its "
  "uuid, and a control's `reference` link is resolved to its first link (the uuid and the link are then also inputs "
  "of that rule); a resource nothing refers to -> not content, an orphan (E4)", {C, N}),
 (r"^nist\.catalog\.groups\[\]\.id$", "L1", "family Set URI (D21 nesting under root)", {X}),
 (r"^nist\.catalog\.groups\[\]\.title$", "L1", "family Set title", {C}),
 (r"^nist\.catalog\.groups\[\]\.class$", NOT_CONTENT, "`family`: selects that the group is written as a family Set", {N}),
 (r"^nist\.catalog\.groups\[\]\.props\[\]\.value$", "L1", "family Set label", {C}),
 (r"^nist\.catalog\.groups\[\]\.props\[\]\.name$", NOT_CONTENT, "selects the member the value is written to (the label)", {N}),
 (r"^nist\.catalog\.groups\[\]\.parts\[\]\.(prose|title)$", "L2",
  "pm overview part -> narrative@1 `overview` on the pm family Set: title and prose (language-tagged; a markdown "
  "link stays as the source wrote it)", {C}),
 (r"^nist\.catalog\.groups\[\]\.parts\[\]\.name$", NOT_CONTENT, "`overview`: selects where the part is written", {N}),
 (r"^nist\.catalog\.groups\[\]\.parts\[\]\.id$", NOT_CONTENT, "rebuilt from the group id (<group id>_ovw)", {N}),
 (CTL + r"\.id$", "L1",
  "Requirement URI (dot form = corpus mapping endpoints); of a withdrawn control that names a successor also its URI "
  "in the successor's `replaces`", {X}),
 (CTL + r"\.title$", "L1", "Requirement title", {C}),
 (CTL + r"\.class$", NOT_CONTENT if not class_written[0] else "L2",
  "rebuilt from the control id (an id with a dot is an enhancement)"
  + ("" if not class_written[0] else "; where that rule does not give it: compat facet oscal-1x@1 `class` on the "
     "Requirement"),
  {N} | ({C} if class_written[0] else set())),
 (CTL + r"\.props\[\]\.value$", "L1",
  "label (no class) -> `label` of the Requirement; zero-padded and sp800-53a label -> not content, rebuilt from that "
  "label; sort-id -> member sequence in the family Set; implementation-level -> obligated-parties; "
  "contributes-to-assurance -> rmf@1 (a JSON boolean); status -> `lifecycle` (E1)", {C, X, N}),
 (CTL + r"\.props\[\]\.(name|ns|class)$", NOT_CONTENT,
  "select the rule for the prop's value: the name the member, the class which label, the namespace "
  "(http://csrc.nist.gov/ns/rmf) the meaning of the name", {N}),
 (CTL + r"\.links\[\]\.href$", "L1",
  "related, required -> relation to the Requirement the link names; reference -> relation to the link of the "
  "back-matter resource, or, where the resource gives none, compat facet `links` as the source writes it (E14); "
  "incorporated-into, moved-to -> the successor's `replaces[]` and the statement of the withdrawn control (R2)",
  {X} | ({C} if rel_count[REF_NO_LINK] else set())),
 (CTL + r"\.links\[\]\.rel$", "L1",
  "related, required, reference -> the relation type, the same word; incorporated-into, moved-to -> `mode` "
  "merged-into, renamed, and the verb of the withdrawn control's statement (R2)", {C, X}),
 (CTL + r"\.params\[\]\.(id|label)$", "L1",
  "statement-scoped kernel parameter (name, label) on each inserting statement (per-statement parameter rule); the "
  "id is also the key of the parameter in odp@1", {C}),
 (CTL + r"\.params\[\]\.select\.choice\[\]$", "L1", "parameter type `choice` with `choices[]` (insertions as tokens)", {C, X}),
 (CTL + r"\.params\[\]\.select\.how-many$", "L1", "parameter `cardinality` many (one-or-more)", {X}),
 (CTL + r"\.params\[\]\.guidelines\[\]\.prose$", "L2", "odp@1 params.{id}.guidelines (language-tagged)", {C, X}),
 (CTL + r"\.params\[\]\.props\[\]\.value$", "L2",
  "odp@1 params.{id}: alt-identifier -> alt-identifiers, alt-label (class sp800-53) -> alt-label, aggregates -> "
  "aggregates, label (class sp800-53a, the formal ODP label) -> sp800-53a-label", {C}),
 (CTL + r"\.params\[\]\.props\[\]\.(name|ns|class)$", NOT_CONTENT, "select the rule for the prop's value", {N}),
 (CTL + r"\.parts\[\]\.id$", "L1",
  "statement or item with text -> statement id (control prefix removed); assessment-objective -> its id in "
  "sp800-53a@1; guidance, assessment-method and a statement part without text of its own -> not content, rebuilt "
  "from the control id", {C, X, N}),
 (CTL + r"\.parts\[\]\.name$", NOT_CONTENT,
  "selects where the part is written (statement, item -> statements[]; guidance -> narrative@1; assessment-* -> "
  "sp800-53a@1)", {N}),
 (CTL + r"\.parts\[\]\.prose$", "L1",
  "statement prose (insertions -> {param:} tokens); guidance, objectives, assessment objects -> facets "
  "(language-tagged); a markdown link stays as the source wrote it", {C, X}),
 (CTL + r"\.parts\[\]\.props\[\]\.value$", "L2",
  "sp800-53a label of an objective or a method -> sp800-53a@1 `label`; method -> sp800-53a@1 `method`; print label "
  "of a statement item -> not content, rebuilt from the item id; where the rule does not give it: compat facet "
  "`parts` of the Requirement, the item's id with its label prop as the source writes them (E7)", {C, N}),
 (CTL + r"\.parts\[\]\.props\[\]\.(name|ns|class)$", "L2",
  "select the rule for the prop's value; the name of an item label the rule does not give is carried with it (E7)", {C, N}),
 (CTL + r"\.parts\[\]\.links\[\]\.href$", "L2",
  "`assessment-for` of an assessment objective -> sp800-53a@1 objective `assessment-for[]`: `statement-id` (the "
  "statement part by the statement-id rule) and, where the part is another control's, `requirement-ref`", {X}),
 (CTL + r"\.parts\[\]\.links\[\]\.rel$", NOT_CONTENT, "`assessment-for`: selects the member of that name", {N}),
 (PROF + r"\.imports\[\]\.include-controls\[\]\.with-ids\[\]$", "L1", "baseline Set members (minted URIs, in the profile's order)", {X}),
 (PROF + r"\.metadata\.title$", "L1", "baseline Set title", {C}),
 (PROF + r"\.metadata\.version$", "L1", "baseline Set `version`; manifest `provenance.baselines`", {C}),
 (PROF + r"\.metadata\.", "L2",
  "compat facet oscal-1x@1 on the baseline Set, member `metadata`, in the source's own shape: last-modified, "
  "oscal-version, roles, parties, responsible-parties and whatever else the document states", {C}),
 (PROF + r"\.merge\.", "L2", "compat facet oscal-1x@1 on the baseline Set, member `merge` (`as-is`, a JSON boolean)", {C}),
 (PROF + r"\.uuid$", "L2", "compat facet oscal-1x@1 on the baseline Set, member `uuid` (E3)", {C}),
 (PROF + r"\.imports\[\]\.href$", "L2", "compat facet oscal-1x@1 on the baseline Set, member `imports` (E4)", {C}),
 (PROF + r"\.back-matter\.", "L2",
  "compat facet oscal-1x@1 on the baseline Set, member `back-matter`, in the source's own shape: the resource its "
  "import names (E4)", {C}),
]
rows, unmapped = coverage(paths, [(rx, level, text) for rx, level, text, _ in RULES])

# The path map against the ledger: an outcome the ledger measured on a path and the row's sentence does not speak
# of fails the run (the sentence says something else than what happened). An outcome a sentence speaks of and
# this source does not show is listed; on the pinned catalogue that list is empty.
by_path = collections.Counter()
for r in RECORD["paths"]: by_path[(norm(r["path"]), r["outcome"])] += r["count"]
map_rows = [(re.compile(rx), level, text, says) for rx, level, text, says in RULES]
measured_of_row = collections.defaultdict(set)
for (p, outcome), n in sorted(by_path.items()):
    row = next((i for i, (rx, _, _, _) in enumerate(map_rows) if rx.search(p)), None)
    if row is None or outcome == "unaccounted": continue         # no row: UNMAPPED; unaccounted: the gate
    measured_of_row[row].add(outcome)
    if outcome not in map_rows[row][3]:
        wiring.append(f"the path map does not say `{outcome}` of {p} (x{n}); its sentence speaks of {sorted(map_rows[row][3])}")
map_not_confirmed = [{"paths": RULES[i][0], "sentence-speaks-of": sorted(RULES[i][3] - seen)}
                     for i, seen in sorted(measured_of_row.items()) if RULES[i][3] - seen]
def measured(p):
    got = [(o, by_path[(p, o)]) for o in ("copied", "transformed", "not-content", "intentionally-dropped", "unaccounted")
           if by_path[(p, o)]]
    return " [ledger: " + ", ".join(f"{o} {n:,}" for o, n in got) + "]"
rows = [(p, n, level, text + measured(p)) for p, n, level, text in rows]

def count_in(pattern, *outcomes):
    """the source values under paths that match with one of the outcomes"""
    return sum(n for (p, o), n in by_path.items() if o in outcomes and re.search(pattern, p))
F_CATALOG_META = count_in(r"^nist\.catalog\.metadata\.(?!title$|version$)", C)
F_PROFILE_META = count_in(PROF + r"\.metadata\.(?!title$|version$)", C)
F_MERGE = count_in(PROF + r"\.merge\.", C)

nset = sum(1 for rel in bundle.objects if "/set/" in rel)
n_wd_objects = sum(1 for cid in req_ids if cid in withdrawn)
lineage_uris = {e["ref"] for entries in list(succ_replaces.values()) + list(fam_replaces.values()) for e in entries}
af_total = sum(assessed_kind.values())
j = report(
    os.path.join(OUTDIR, "sp800-53-coverage-report.md"),
    os.path.join(OUTDIR, "sp800-53-coverage-report.json"),
    "NIST SP 800-53 Rev 5 + 800-53B -> Semantic Core: Coverage Report (computed)",
    f"Source: **{cat['metadata']['title']}** v{VER} (OSCAL {cat['metadata']['oscal-version']}) "
    f"+ four 800-53B baseline profiles. Census: `drafts/gate-3-census.md`.",
    [f"- Objects emitted: **{len(req_ids)} Requirements** ({len(req_ids) - n_wd_objects} controls and enhancements in "
     f"force, {n_wd_objects} withdrawn), **{nset} Sets** ({fam_sets} families + root + 4 baselines), manifest with "
     f"both digests.",
     f"- Baseline membership: " + ", ".join(f"{b} {len(BASELINES[b]['imports'][0]['include-controls'][0]['with-ids'])}"
                                            for b in BASELINES) + ".",
     f"- **Conversion ledger** (every source value followed into the written files): **{LT['copied']:,} copied**, "
     f"**{LT['transformed']:,} transformed** by a named rule, **{LT['not-content']:,} not content** by a checked rule, "
     f"**{LT['intentionally-dropped']:,} dropped** for a declared reason, "
     f"**{LT['unaccounted']:,} unaccounted**; claims that do not hold: {len(LEDGER['verification-failures'])}. The "
     f"line `UNMAPPED` above counts source paths that have a row in the path map. The ledger is the measure of what "
     f"arrived; its sections are at the end of this report."],
    [f"- **Withdrawn controls x{len(withdrawn)}**: every one is a Requirement with lifecycle `withdrawn` (the "
     f"source's status, by a rule; E1), with its id, label, title, its place in its family Set and its links. "
     f"x{len(tombstones)} name a successor: the successor names them in kernel `replaces[]` "
     f"({sum(len(v) for v in succ_replaces.values())} edges on Requirements + {sum(len(v) for v in fam_replaces.values())} "
     f"on family Sets: sa-12 'incorporated into SR', the successor is a whole family; incorporated-into->merged-into, "
     f"moved-to->renamed), and their one statement is made from those links (R2), e.g. "
     f"{next((repr(s['prose']['en']) for cid in sorted(tombstones) for s in req_ids[cid][2]['statements']), 'none')}; "
     f"withdrawn->withdrawn chains x{len(wd_chain)}, dangling x{len(wd_dangling)}. x{len(wd_no_successor)} name no "
     f"successor" + (f" ({', '.join(wd_no_successor)})" if wd_no_successor else "") + " and keep the one statement "
     f"the source gives them.",
     f"- **Modality**: " + ", ".join(f"`{k}` x{v}" for k, v in sorted(mod_count.items())) + ". Rev 5 statements are "
     f"uniformly imperative and obligation binds on baseline selection - the INVERSE of the declarative national "
     f"pattern (ISM/CIS/CyFun/C5): corpus rule `must` for a control in force. Force in the mood, selection in the "
     f"baseline Sets; both confirm D13's split axes. The statement of a withdrawn control says why it was withdrawn "
     f"and states no obligation: `unspecified`.",
     lifecycle_default_line(LIFECYCLE_DEFAULT),
     obligated_party_line(PARTY, PARTY_ORIGIN, PARTY_DEFAULT, source_states=PARTY_SOURCE_STATES)
     + f" The source gives a level on x{len(req_ids) - op_default} controls ("
     + ", ".join(f"{k} x{v}" for k, v in sorted(lvl_count.items(), key=lambda x: -x[1]) if k != "(none)")
     + f"), written as `{NS}/party/<level>` on their x{sum(mod_count.values()) - op_default_stmts} statements. It gives "
     f"none on x{op_default} controls; their x{op_default_stmts} statements are the only ones that carry the "
     + ("caller's party." if PARTY_ORIGIN == "caller" else "converter's default."),
     f"- **Two-layer ODP params -> statement-scoped decls**: declared on each statement whose prose inserts "
     f"them (per-statement parameter rule); choice x{sum(1 for cid, (rid, _, r) in req_ids.items() for s in r['statements'] for p in s.get('parameters', []) if p['type'] == 'choice')}, "
     f"string else; legacy _prm_ aggregates carried as params + odp@1 `aggregates`; params without a "
     f"statement insertion site x{sum(no_site.values())} declared on the first statement "
     f"({len(facet_only)} bind only in the 53A objectives, {len(nowhere)} nowhere). The formal ODP label of a "
     f"parameter (prop `label`, class sp800-53a) is written as the source gives it: odp@1 `sp800-53a-label` x{n_formal}.",
     f"- **SP 800-53A layer -> sp800-53a@1** on {n_53a} Requirements: objective trees (53a labels kept - "
     f"the #10 addressing surface) + EXAMINE/INTERVIEW/TEST methods with object lists (language-tagged). The "
     f"`assessment-for` link of an objective is written on the objective, x{af_total}: "
     + ("; ".join(f"x{n} name {k}" for k, n in sorted(assessed_kind.items(), key=lambda x: -x[1])) or "none") + ".",
     f"- **Relations**: " + ", ".join(f"{k} x{v}" for k, v in sorted(rel_count.items(), key=lambda x: -x[1])) +
     f"; reference targets resolved to publication URLs (landmark); the back-matter resources, as the source writes "
     f"them, -> references@1 on the root Set.",
     f"- **Back-matter -> references@1 on the root Set** x{len(RESOURCES_KEPT)} of {len(RESOURCES)} resources in the "
     f"source's own shape, each with its uuid (the convention of the ISM converter): uuid, title, citation, rlinks "
     f"with href and media-type. x{len(ORPHANS)} are orphans, which nothing in the catalogue refers to (no `#uuid` "
     f"outside them): not carried, a claim the ledger checks (E4). A profile's one resource, which its import names, "
     f"stands with the import in the compat facet of its baseline Set.",
     f"- **Markdown links in the texts stay as the source wrote them** x{len(MD_LINKS)}; the target of a link is an "
     f"id of the source. x{md_targets['a back-matter resource']} name a back-matter resource by its uuid "
     f"(x{len({t for t in MD_LINKS if t in RES})} distinct resources), which references@1 carries; "
     f"x{md_targets['another control']} name "
     f"another control and x{md_targets['a withdrawn control']} a withdrawn one (the Requirement URI ends in the id "
     f"in upper case), x{md_targets['a statement of a control']} a statement of a control (control id, `_`, "
     f"statement id), x{md_targets['a family']} a family, x{md_targets['a parameter']} a parameter, "
     f"x{md_targets['nothing the catalogue defines']} nothing the catalogue defines.",
     f"- **Document metadata -> compat facet oscal-1x@1, member `metadata`**, on the Set that stands for the "
     f"document, in the source's own shape: x{F_CATALOG_META} values of the catalogue on the root Set, "
     f"x{F_PROFILE_META} values of the four profiles on their baseline Sets. `title` and `version` are the Set's own "
     f"members; the document's `uuid` stands beside it (E3). A profile's `merge` directive and its `imports` stand "
     f"there too (x{F_MERGE}, a JSON boolean). The manifest's "
     f"`provenance` names the catalogue's author and day by the library's rule for an OSCAL document (backlog #69): "
     f"`author-ref` {PROVENANCE.get('author-ref', 'none: the metadata names no author')}, `date` "
     f"{PROVENANCE.get('date', 'none: last-modified does not begin with a day')}. The manifest has one provenance; "
     f"the author and the day of a profile stand in its metadata on its baseline Set ("
     + ", ".join(f"{b}: {(document_author(p['metadata']) or {}).get('name', 'no author')}, "
                 f"{document_day(p['metadata']) or 'no day'}" for b, p in BASELINES.items()) + ").",
     f"- **Conversion ledger (measured per source value)**: each of the {LEDGER['leaf-values']:,} leaf values of the "
     f"catalogue and the four profiles was followed into the written files. **{LT['copied']:,} copied** (the value "
     f"stands, with its type, at the destination, read back from the written file), **{LT['transformed']:,} "
     f"transformed** (a named rule made the destination from it; the rule was applied to the source again and "
     f"compared), **{LT['not-content']:,} not content** (a name that only selects where a value is written, a "
     f"namespace, an id or label a function rebuilds exactly, an orphaned resource; each claim checked against the "
     f"source, and against what became of the value it rests on), **{LT['intentionally-dropped']:,} intentionally "
     f"dropped** (a declared reason), "
     f"**{LT['unaccounted']:,} unaccounted**. Claims that do not hold: {len(LEDGER['verification-failures'])}. The "
     f"record is `{LEDGER_FILE}`: one row per source path and outcome, every row a count over values that were "
     f"traced one by one in the run that wrote it. An equal value elsewhere in the bundle does not count: a value is "
     f"traced by what the converter did with it.",
     f"- **Labels of a control**: the label without a class -> `label`; the zero-padded and the SP 800-53A label "
     f"are no content, each rebuilt from that label by padding its numbers (x{rebuilt_by[N_LABEL_PADDED]} and "
     f"x{rebuilt_by[N_LABEL_53A]}, every one checked by the ledger).",
     f"- **Payload free text language-tagged**: " + ", ".join(f"{k} x{v}" for k, v in sorted(lang_wraps.items())) + "."],
    [f"- **#10 measure (ODP -> statement addressing)**: insertion-count histogram "
     f"{dict(sorted(decl_hist.items()))}; params inserted in >=2 statements: **{len(multi_decl)}** "
     + (f"({[(c, p) for c, p, n in multi_decl[:6]]}...)" if multi_decl else "(none)") +
     f" - the (requirement, ODP) address resolves via the declaring statement"
     + ("" if not multi_decl else "; ambiguous cases need the statement map") + ".",
     f"- **Corpus mapping endpoints vs minted ids**: {sum(hit.values())} citations resolve "
     f"({len(hit)} distinct); {sum(miss.values())} cite unknown labels ({sorted(miss)[:8] if miss else []}).",
     f"- **Baseline ids not emitted** (an id the catalogue does not define): " +
     ("; ".join(f"{b}: {v}" for b, v in bl_missing.items()) if bl_missing else "none") + ".",
     f"- **Cross-control param insertions x{len(cross_param)}** ({cross_param}): prose in one control "
     f"inserts another control's ODP - a source irregularity (of x{n_inserted:,} insertions in statement text); the declaration is "
     f"duplicated onto the inserting statement per the per-statement parameter rule. REPORTED upstream.",
     f"- **Params bound nowhere x{len(nowhere)}** (ODPs defined for assessment that neither control text "
     f"nor 53A objectives insert) - declarations without any insertion site.",
     f"- **Kernel and standard facets: where the source has a value and they have no place** (carried all the same; "
     f"each is a finding for the author). "
     f"(1) `assessment-for` x{af_total}: the standard facet assessment-criteria@1 keys `by-statement` by a statement "
     f"of the Requirement, and cannot hold these links as the source states them: "
     f"x{assessed_kind['the statement part of the same control as a whole, which has no text of its own']} name the "
     f"statement part as a whole, which is no statement where its text is in its items; "
     f"x{assessed_kind['a statement of another control'] + assessed_kind['nothing the catalogue defines']} leave "
     f"the control (x{assessed_kind['nothing the catalogue defines']} of them name nothing the catalogue defines); "
     f"and x{assessed_apart[0]} objectives name another statement than the objective above them, so a tree cut by "
     f"statement is no tree. Its `objectives` is an array of untyped objects and has no member for the methods of "
     f"the same layer. D10 (per-clause keying, rev. v0.6) asks a payload that addresses single statements to key "
     f"them `by-statement`; a tree whose nodes name statements at different depths, of the same Requirement or of "
     f"another, has no keyed form. Written in the pinned facet sp800-53a@1, on the objective, as a list of "
     f"{{statement-id}} with `requirement-ref` where the statement is another control's: the address the source "
     f"gives, without the keying D10 asks for. "
     f"(2) Document metadata x{F_CATALOG_META + F_PROFILE_META}: a Set has `title` and `version` and no member for "
     f"dates, the OSCAL version, revisions, keywords, links, roles, parties and who is responsible. Written in the "
     f"compat facet, member `metadata`. (3) A profile's `merge` x{F_MERGE}: a Set does not say how a selection is "
     f"merged. Compat facet, member `merge`. "
     f"(4) A withdrawn control x{n_wd_objects}: the kernel requires a statement with a modality and an obligated "
     f"party on every Requirement (R2: the statement stays). The source gives x{len(wd_no_successor)} of them one "
     f"sentence on why they were withdrawn and the other x{len(tombstones)} only links; theirs is made from the links. "
     f"Written with modality `unspecified` and the party of a control without an implementation level. "
     f"(5) The print label of a statement item x{rebuilt_by[N_ITEM_LABEL] + sum(len(v) for v in labels_kept.values())}: "
     f"a statement has an id and no label. x{rebuilt_by[N_ITEM_LABEL]} are rebuilt from the item id; "
     f"x{sum(len(v) for v in labels_kept.values())} the rule does not give stand in the compat facet `parts` of their "
     f"Requirement, the item's id with its label prop (E7)"
     + (f" ({', '.join(e['id'] for v in labels_kept.values() for e in v)})" if labels_kept else "") + ". "
     f"(6) The formal ODP label x{n_formal}: a kernel parameter has one `label`, which holds the parameter's own. "
     f"Written in odp@1.",
     f"- **Path map and ledger**: every outcome the ledger measured on a path is one the sentence of its row speaks "
     f"of (a sentence that says something else ends the run). Outcomes a sentence speaks of and this source does "
     f"not show: " + ("; ".join(f"`{m['paths']}` {m['sentence-speaks-of']}" for m in map_not_confirmed) or "none") + "."],
    rows, unmapped,
    {"source-version": VER,
     "objects-emitted": {"requirements": len(req_ids), "sets": nset,
                         "requirements-in-force": len(req_ids) - n_wd_objects, "requirements-withdrawn": n_wd_objects},
     "withdrawn": {"count": len(withdrawn), "name-a-successor": len(tombstones), "named-in-lineage": len(lineage_uris),
                   "successor-edges": sum(len(v) for v in succ_replaces.values()),
                   "family-set-edges": sum(len(v) for v in fam_replaces.values()),
                   "chains": wd_chain, "dangling": wd_dangling, "objects": wd_no_successor},
     "cross-control-params": [{"control": c, "param": p} for c, p in cross_param],
     "no-statement-site": {"total": sum(no_site.values()), "facet-only": len(facet_only),
                           "nowhere": len(nowhere)},
     "modality": dict(mod_count),
     "obligated-party": obligated_party_record(PARTY, PARTY_ORIGIN, PARTY_DEFAULT, PARTY_SOURCE_STATES),
     "obligated-party-use": {"controls": {"source-states": len(req_ids) - op_default, "not-stated": op_default},
                             "statements": {"source-states": sum(mod_count.values()) - op_default_stmts,
                                            "not-stated": op_default_stmts},
                             "implementation-levels": dict(lvl_count)},
     "backlog-10": {"insertion-histogram": {str(k): v for k, v in sorted(decl_hist.items())},
                    "multi-declared": [{"control": c, "param": p, "statements": n} for c, p, n in multi_decl]},
     "endpoint-crosscheck": {"resolved": sum(hit.values()), "distinct": len(hit),
                             "withdrawn-hits": hit_wd, "unknown": miss},
     "baseline-missing": dict(bl_missing),
     "lang-wraps": dict(lang_wraps),
     "assessment-for": {"links": af_total, "names": dict(assessed_kind),
                        "objectives-that-name-another-statement-than-the-one-above": assessed_apart[0]},
     "formal-odp-labels": n_formal,
     "item-labels": {"rebuilt": rebuilt_by[N_ITEM_LABEL], "compat-parts": [e["id"] for v in labels_kept.values() for e in v]},
     "lifecycle-default": LIFECYCLE_DEFAULT,
     "class-written": class_written[0],
     "document-metadata": {"catalogue": F_CATALOG_META, "profiles": F_PROFILE_META, "merge": F_MERGE},
     "markdown-links": {"links": len(MD_LINKS), "names": dict(md_targets),
                        "resources-named": len({t for t in MD_LINKS if t in RES}), "resources": len(RES)},
     "ledger": {"file": LEDGER_FILE, "leaf-values": LEDGER["leaf-values"], "totals": LT,
                "verification-failures": len(LEDGER["verification-failures"]),
                "rules": [{"rule": r, "source-values": rule_values[r], "destinations": rule_destinations[r]}
                          for r, _ in sorted(rule_values.items(), key=lambda x: (-x[1], x[0]))],
                "not-content": [{"kind": kind, "rule": rule, "count": n}
                                for (kind, rule), n in sorted(not_content.items(), key=lambda x: (-x[1], x[0]))],
                "declared-drops": declared_rows,
                "path-map-not-confirmed": map_not_confirmed,
                "written-without-a-source-value": [{"place": p, "count": n, "example": own_example[p], "from": own_why(p)}
                                                   for p, n in sorted(own_values.items(), key=lambda x: (-x[1], x[0]))]}})

# ---------- the ledger's sections of the report ----------
def cell(v, width=90):
    """a value for a table cell: one line, no pipe, cut to a width"""
    s = " ".join((v if isinstance(v, str) else json.dumps(v)).split()).replace("|", "/")
    return s if len(s) <= width else s[:width - 1] + "…"
unaccounted_by_path = {}
for u in LEDGER["unaccounted-paths"]:
    row = unaccounted_by_path.setdefault(norm(u["path"]), {"count": 0, "first": u["pointers"][0]})
    row["count"] += u["count"]
with open(os.path.join(OUTDIR, "sp800-53-coverage-report.md"), "a", encoding="utf-8") as f:
    f.write(f"\n## Conversion ledger: the five outcomes\n\n"
            f"| outcome | source values |\n|---|---:|\n" +
            "".join(f"| {k} | {LT[k]:,} |\n" for k in ("copied", "transformed", "not-content", "intentionally-dropped", "unaccounted")) +
            f"| all | {LEDGER['leaf-values']:,} |\n\nClaims that do not hold on the written files or on the source: "
            f"{len(LEDGER['verification-failures'])}.\n")
    f.write("\n## Conversion ledger: the rules\n\n"
            "A value the converter computes is stated as a named rule with a pure function. After the bundle is "
            "written the function is applied to the source value again and the result is compared with what the "
            "file holds. A rule with several inputs counts each of them: the id of a control is an input of the "
            "rule that cuts it off a statement id.\n\n"
            "| rule | source values | destinations |\n|---|---:|---:|\n" +
            "".join(f"| {r} | {rule_values[r]:,} | {rule_destinations[r]:,} |\n"
                    for r, _ in sorted(rule_values.items(), key=lambda x: (-x[1], x[0]))))
    f.write(f"\n## Conversion ledger: what is no content, and by which rule\n\n"
            f"{LT['not-content']:,} source values are not in the bundle and are no content, each by a rule of one of "
            f"three kinds that the ledger checked: the claim itself against the source (a rebuilt id is the value the "
            f"function gives; a name is one the mapping knows; a namespace is the one the mapping is written for), and "
            f"what became of the value the claim rests on. A selector beside a value that is unaccounted is "
            f"unaccounted, and beside a value that is a declared drop it is dropped with it.\n\n"
            f"| kind | rule | source values |\n|---|---|---:|\n" +
            "".join(f"| {KIND.get(kind, kind)} | {rule} | {n:,} |\n"
                    for (kind, rule), n in sorted(not_content.items(), key=lambda x: (-x[1], x[0]))))
    f.write(f"\n## Conversion ledger: the drops that stay declared\n\n"
            f"{LT['intentionally-dropped']:,} source values have no destination and a reason that was declared before "
            f"the author's rule of 2026-11-14 (content is never dropped). None of these values is one of the three "
            f"classes above; a name that selects one of them is dropped with it and stands in the last rows. They "
            f"stay declared until the author decides; the last column is the converter's reading under that rule, "
            f"not a decision.\n\n"
            f"| source path | values | declared reason | example | reading |\n|---|---:|---|---|---|\n" +
            "".join(f"| `{r['path']}` | {r['count']:,} | {cell(r['reason'], 400)} | `{r['example']}` = "
                    f"`{cell(r['example-value'], 60)}` | {r['reading']} |\n" for r in declared_rows))
    f.write("\n## Unaccounted source values, by path (conversion ledger)\n\n" +
            ("None.\n" if not unaccounted_by_path else
             "A run with a row here ends with exit code 1.\n\n| path | count | first value |\n|---|---:|---|\n" +
             "".join(f"| `{p}` | {u['count']:,} | `{u['first']}` |\n" for p, u in sorted(unaccounted_by_path.items()))))
    f.write(f"\n## What the ledger cannot see\n\n"
            f"The ledger follows source values into the bundle. A value the converter writes on its own has no "
            f"entry in it. Seen from the bundle: {sum(own_values.values()):,} leaf values of the written objects are "
            f"neither a source value nor the result of a stated rule. The manifest's digests and paths are computed "
            f"from the written files and are not listed.\n\n"
            f"| place in an object | values | example | what stands behind it |\n|---|---:|---|---|\n" +
            "".join(f"| `{p}` | {n:,} | `{cell(own_example[p], 60)}` | {own_why(p)} |\n"
                    for p, n in sorted(own_values.items(), key=lambda x: (-x[1], x[0]))))
print(f"reqs: {len(req_ids)}  sets: {nset}  leaves: {j['totals']['leaf-values']:,}  "
      f"mapped: {j['totals']['mapped']:,}  UNMAPPED: {j['totals']['unmapped']}")
print(f"withdrawn: {len(withdrawn)}  successor-edges: {sum(len(v) for v in succ_replaces.values())}  "
      f"objects: {len(wd_no_successor)}  chains: {len(wd_chain)}  dangling: {len(wd_dangling)}")
print(f"#10 multi-declared params: {len(multi_decl)}  histogram: {dict(sorted(decl_hist.items()))}")
print(f"endpoint crosscheck: resolved {sum(hit.values())}  withdrawn-hits {dict(hit_wd)}  unknown {dict(miss)}")
if unmapped:
    for p, n in unmapped[:30]: print("  UNMAPPED", p, "x", n)
for p, u in sorted(unaccounted_by_path.items()):
    print(f"  unaccounted {u['count']:>6,}  {p}  e.g. {u['first']}", file=sys.stderr)
for x in LEDGER["verification-failures"][:20]: print("  LEDGER CHECK FAILED", json.dumps(x, ensure_ascii=False), file=sys.stderr)
print(f"run: {time.time() - T_START:.1f} s in all")
if j["totals"]["leaf-values"] != LEDGER["leaf-values"]:        # the path map and the ledger read one source
    wiring.append(f"the path map counts {j['totals']['leaf-values']} source leaf values and the ledger {LEDGER['leaf-values']}")
if unmapped: wiring.append(f"{len(unmapped)} source path(s) have no row in the path map")
# the file on disk is the record of this run, not one an earlier run left or one written from an earlier accounting
try:
    with open(os.path.join(OUTDIR, LEDGER_FILE), encoding="utf-8") as f: on_disk = json.load(f)
except (OSError, ValueError): on_disk = None
if on_disk != json.loads(json.dumps(ledger_by_path(LEDGER, collapse=COLLAPSE))):
    wiring.append(f"{LEDGER_FILE} on disk is not the record of this run")
if wiring:
    for x in wiring: print("  LEDGER WIRING", x, file=sys.stderr)
    raise SystemExit(f"convert_nist.py: {len(wiring)} wiring check(s) of the conversion ledger failed")
# The gate (author, 2026-11-14): a claim that does not hold or an unaccounted value ends the run with 1.
ledger_gate(LEDGER, "convert_nist.py")
