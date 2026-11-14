#!/usr/bin/env python3
"""NIST SP 800-53 Rev 5 catalog + 800-53B baselines -> Semantic Core bundle.
Census: drafts/gate-3-census.md (2026-07-22). 20 families -> Sets; 1,014
live controls/enhancements -> Requirements (statement items flattened,
modality `must` corpus rule); 182 withdrawn tombstones -> dropped, lineage
inverted onto the successor's kernel `replaces[]`; SP 800-53A layer ->
sp800-53a@1 facet; two-layer ODP params -> statement-scoped kernel
parameters (declared where inserted, the per-statement parameter rule) + odp@1
admin facet; baselines -> 4 membership Sets. Coverage target: 0.

    convert_nist.py [--obligated-party URI] [--out DIR]

The source gives a control an `implementation-level` (organization, system,
or both), and the converter writes it as the party the control's statements
bind: that value is the source's and is written as it stands. For a control
without one the converter writes a party of its own,
`<namespace>/party/organization`; --obligated-party writes the caller's
party in that place and nowhere else, and the coverage report says which of
the two it was and on how many controls (backlog #74). Without arguments
the run reproduces the committed conversion byte for byte; the Validators
workflow holds it to that. --out writes the bundle and the two reports
somewhere else, which is where a run with another party belongs.

The conversion ledger (backlog #41, phase E). The catalogue and the four
profiles are loaded through oscal_conv_lib.Ledger, so every string and
integer of them carries its origin for as long as the script hands it on
unchanged. What the script computes is stated where it is computed, as a
named rule with a pure function the ledger applies again to the source. After
the bundle is written every source leaf value has one outcome: copied,
transformed, intentionally dropped or unaccounted. The record, one row per
source path and outcome, is `sp800-53-conversion-ledger.json` beside the
reports. A destination that does not hold what the script says it wrote
there ends the run with exit code 1, and so does a failed wiring check (a
drop that reaches further than it names, a record on disk that is not this
run's). An unaccounted value is printed and reported, and the run ends
with 0. Nothing here changes what is written: the bundle is byte for byte
the one the script wrote before the ledger existed.

A drop is declared in two cases only, and each reason says which: where the
path map of this converter already said the value is not carried ("path
map: ..."), and where the class is one the author decided for the IFA
corpus on 2026-11-13 ("as decided for IFA on 2026-11-13: ..."). Everything
else without a destination stays unaccounted, grouped into classes with a
recommendation, for the author to decide."""
import json, os, re, sys, time, collections
from oscal_conv_lib import make_T, slug, Bundle, inventory, coverage, report, walk_controls
from oscal_conv_lib import known_arguments, out_dir, obligated_party, obligated_party_line, obligated_party_record
from oscal_conv_lib import Ledger, ledger_by_path

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

lang_wraps = collections.Counter()
T = make_T("en", lang_wraps)
INSERT = re.compile(r"\{\{\s*insert:\s*param,\s*([a-z0-9._-]+)\s*\}\}")
MDLINK = re.compile(r"\[([^\]]+)\]\(#[a-zA-Z0-9._-]+\)")

led = Ledger()
D = led.derive
T_START = time.time()

def load(tag, filename, key):
    """-> the document under `key` of a source file; its string and integer leaves carry their origin"""
    with open(os.path.join(SRCDIR, filename), encoding="utf-8") as f: doc = json.load(f)
    return led.source(tag, {key: doc[key]})[key]

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

# ---------- the reasons of the declared drops (see the header) ----------
IFA = "as decided for IFA on 2026-11-13: "
B_REVISIONS = IFA + "revision history of the source document"
B_DIRECTORY = IFA + ("the source's directory of parties and roles: a party is a landmark URI and there is no party "
                     "object (register, backlog #16)")
B_BACKMATTER = IFA + ("a back-matter resource or an import link: a link to another serialisation of the source or to "
                      "an imported document; the bundle carries the Requirements themselves")
B_TYPE_TAG = IFA + "a type tag of a structural element: the bundle says by its shape what kind of thing the element is"
B_UUID = IFA + ("the uuid of a source document, which identifies it among source documents only: JASCON objects get "
                "URIs minted from ids")
B_RESOURCE_UUID = IFA + ("the uuid of a back-matter resource that no reference link of a control names; it identifies "
                         "the resource inside the catalogue only, and the resource's title and link are on the root Set")
A_TOMBSTONE = ("path map: a withdrawn control is dropped as a tombstone; its lineage is inverted onto the successor "
               "its link names, which carries its URI, a label and its title")
A_CLASS = ("path map: the class of a control is encoded structurally (membership in its family Set; the `required` "
           "edge of an enhancement to its base control)")
A_LABEL = ("path map: the zero-padded and the SP 800-53A label of a control are derivable from the label that is "
           "carried (its numbers padded to two digits; checked for this value)")
A_FORMAL_ODP = ("path map: the formal ODP label of a parameter is derivable from the parameter id (checked for this "
                "value)")
A_ITEM_LABEL = ("path map: the print label of a statement item is derivable: its letter or number is the last "
                "segment of the item id (checked for this value), its punctuation is print form")
A_PROFILE = "path map: profile resolution mechanics; the selection is the Set"

def norm(p):
    p = re.sub(r"(\.controls\[\])+", ".controls[]", p)
    p = re.sub(r"(\.parts\[\])+", ".parts[]", p)
    return p

paths = collections.Counter()
inventory({"catalog": cat}, "nist", paths, normalize=norm)
for b, prof in BASELINES.items():
    inventory({"profile": prof}, b.lower(), paths, normalize=norm)

# ---------- helpers ----------
def prop(c, name, ns=None, cls=None, all_=False):
    out = [p["value"] for p in c.get("props", []) or []
           if p.get("name") == name and (ns is None or p.get("ns") == ns)
           and (cls is None or p.get("class") == cls)]
    return out if all_ else (out[0] if out else None)

def mint(src_id):
    return f"{NS}/req/{src_id.upper()}"

# ---------- the rules: each a name and a pure function of source values ----------
R_REQ = "requirement URI from the control id"
R_LINK = "requirement URI from the control a link names"
R_REFERENCE = "a reference link resolved by uuid: the first link of the back-matter resource it names"
R_INSERT = "prose with each parameter insertion {{ insert: param, x }} written as the token {param:x}"
R_MDLINK = "prose with each markdown link into the catalogue replaced by its link text (the target is not carried)"
R_PARAGRAPH = ("assessment objects: one entry per paragraph of the part's prose, trimmed "
               "(insertions as tokens, markdown links as their text)")
R_STATEMENT = "statement id without the control prefix"
R_PARTY = "obligated party URI from the implementation level"
R_CARDINALITY = "parameter cardinality `many` from the selection's how-many `one-or-more`"
R_LINEAGE = "lineage inverted: the URI of a withdrawn control, written on the successor its link names"
R_MODE = "lineage mode from the link's rel (incorporated-into -> merged-into, moved-to -> renamed)"
R_INTO = "the statement a lineage link names, as a statement id"
R_FAMILY = "family Set URI from the group id"
R_SEQUENCE = "member sequence: ten times the control's place in its family, ordered by sort-id"
R_SAME_RELATION = "a relation the control states twice is written once"

def req_uri(cid): return D(R_REQ, mint, cid)
def _link_ref(href): return mint(href.lstrip("#"))
def _resolved(ref, uuid, url):
    """three source values meet here: the link, the uuid of the resource it names, and that resource's link"""
    return url if ref.lstrip("#") == uuid else None
def _rewrite(prose):
    return MDLINK.sub(r"\1", INSERT.sub(lambda m: "{param:" + m.group(1) + "}", prose or ""))
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
def _family_uri(gid): return f"{NS}/set/family/{gid}"

def rewrite(prose, used=None):
    """{{ insert: param, x }} -> {param:x}; markdown #-links -> their text."""
    inserted, links = INSERT.findall(prose or ""), MDTARGET.findall(prose or "")
    if used is not None: used.update(inserted)
    n_links[0] += len(links)
    for target in links:                 # what the link named, and whether the control links to it as well
        md_targets[(named_by(target), (LINKS_OF[0] or {}).get(target, ""))] += 1
    rule = "; ".join(r for r, applies in ((R_INSERT, inserted), (R_MDLINK, links)) if applies)
    return carried(rule, _rewrite, prose)

n_links = [0]
# A markdown link in prose is replaced by its text, so its target is in no leaf
# of the bundle and the ledger, which follows leaves, cannot miss it. It is
# counted here instead: what each target is, and how many of them the same
# control also names in a link of its own (which is carried as a relation).
MDTARGET = re.compile(r"\[[^\]]+\]\(#([a-zA-Z0-9._-]+)\)")
md_targets = collections.Counter()      # (what the target is, the rel of the control's own link to it or "") -> links
LINKS_OF = [None]                        # the links of the control being converted: target -> rel
def named_by(target):
    return ("a back-matter resource" if target in RES else "a withdrawn control" if target in withdrawn
            else "another control" if target in by_id else "a family" if target in groups_by_id
            else "a statement of a control" if target in part_ids else "a parameter" if target in params_global
            else "nothing the catalogue defines")

# back-matter: uuid -> (title, citation, url)
RES, RES_UUID = {}, {}
for r in cat.get("back-matter", {}).get("resources", []) or []:
    RES[r["uuid"]] = {"title": r.get("title", ""),
                      "citation": (r.get("citation") or {}).get("text", ""),
                      "url": (r.get("rlinks") or [{}])[0].get("href", "")}
    RES_UUID[r["uuid"]] = r["uuid"]          # the uuid as the source wrote it, for the rule that resolves a link
    led.drop_value(r["uuid"], B_RESOURCE_UUID)   # applies where no reference link names the resource

controls = list(walk_controls(cat))
by_id = {c["id"]: c for c, _, _ in controls}
withdrawn = {c["id"] for c, _, _ in controls if prop(c, "status") == "withdrawn"}
live = [(c, par, g) for c, par, g in controls if c["id"] not in withdrawn]
groups_by_id = {g["id"]: g for g in cat.get("groups", []) or []}
params_global = {pm["id"]: pm for c, _, _ in controls for pm in c.get("params", []) or []}
def all_parts(node):
    for p in node.get("parts", []) or []:
        yield p
        yield from all_parts(p)
part_ids = {p["id"] for c, _, _ in controls for p in all_parts(c) if "id" in p}

# ---------- withdrawal inversion: successor.replaces[] ----------
MODE = {"incorporated-into": "merged-into", "moved-to": "renamed"}
succ_replaces = collections.defaultdict(list)   # successor cid -> entries
fam_replaces = collections.defaultdict(list)    # successor group id -> entries (moved-to a family)
wd_chain, wd_dangling = [], []
wd_no_successor = []                            # withdrawn controls of which no lineage entry was written
wd_label_not_plain = []                         # ... and those whose entry carries another label than the plain one
for c, _, _ in controls:
    if c["id"] not in withdrawn: continue
    landed = 0
    plain_label = next((p["value"] for p in c.get("props", []) or [] if p.get("name") == "label" and not p.get("class")), None)
    for l in c.get("links", []) or []:
        rel, href = l.get("rel"), (l.get("href") or "").lstrip("#")
        if rel not in MODE: continue
        target, into = href, None
        if "_smt" in href:                       # statement-level target
            target, into = href.split("_smt")[0], D(R_INTO, _into, l["href"])
        successor = None if target in withdrawn else by_id.get(target) or groups_by_id.get(target)
        e = {"ref": D(R_LINEAGE, _lineage_ref, c["id"], l["href"], successor["id"]) if successor else mint(c["id"]),
             "mode": D(R_MODE, _mode, l["rel"]), "label": prop(c, "label", cls=None) or c["id"].upper(),
             "title": c.get("title", "")}
        if into: e["into"] = into
        if target in withdrawn:
            wd_chain.append((c["id"], target)); continue
        if target in by_id:
            succ_replaces[target].append(e); landed += 1
        elif target in groups_by_id:             # sa-12 -> #sr: successor is a whole family
            fam_replaces[target].append(e); landed += 1
        else:
            wd_dangling.append((c["id"], href))
    if landed:
        # What the path map has said of a tombstone since 1.0.0, declared value by value: its class, its sort-id
        # and its status are not carried, nor the labels the annotation does not take, nor what selects a prop.
        # Its id, its title, the label the annotation takes and its links are carried by the lineage. None of
        # those is declared here, so one that got lost would be unaccounted and not read as dropped on purpose.
        taken = prop(c, "label", cls=None)
        led.drop_value(c.get("class"), A_TOMBSTONE)
        for p in c.get("props", []) or []:
            for k in ("name", "class", "ns"): led.drop_value(p.get(k), A_TOMBSTONE)
            if p.get("name") in ("sort-id", "status") or (p.get("name") == "label" and p.get("value") is not taken):
                led.drop_value(p.get("value"), A_TOMBSTONE)
        if plain_label is not None and (prop(c, "label", cls=None) or c["id"].upper()) != plain_label:
            tag, parts = plain_label._origins[0]
            wd_label_not_plain.append((c["id"], prop(c, "label", cls=None), plain_label,
                                       f"{tag}#/" + "/".join(str(x) for x in parts)))
    else:
        wd_no_successor.append(c["id"])

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

# formal ODP id round-trip check (prop label == uppercase transform of id)
def formal(pid):
    m = re.fullmatch(r"([a-z]{2}-[0-9]+(?:\.[0-9]+)?)_odp(?:\.([0-9]+))?", pid)
    if not m: return None
    base = m.group(1)
    fam, num = base.split("-", 1)
    num = num.split(".")
    lbl = f"{fam.upper()}-{int(num[0]):02d}" + (f".{int(num[1]):02d}" if len(num) > 1 else "")
    return f"{lbl}_ODP" + (f"[{m.group(2)}]" if m.group(2) else "")

formal_ok, formal_div = 0, []
label_eq, label_div = 0, []

# ---------- objectives / methods trees ----------
def placed(part):
    """A part the converter has put where the bundle's shape says what it is (a statement, the guidance,
    an objective, a method, its objects, an overview): its `name` is the type tag that decided the place."""
    led.drop_value(part.get("name"), B_TYPE_TAG)

def obj_tree(pt, used):
    placed(pt)
    node = {}
    if pt.get("id"): node["id"] = pt["id"]
    lab = prop(pt, "label", cls="sp800-53a")
    if lab: node["label"] = lab
    if pt.get("prose"): node["prose"] = T(rewrite(pt["prose"], used), "objective")
    kids = [obj_tree(s, used) for s in pt.get("parts", []) or []]
    if kids: node["children"] = kids
    return node

def methods_of(c, used):
    out = []
    for pt in c.get("parts", []) or []:
        if pt.get("name") != "assessment-method": continue
        placed(pt)
        m = {"method": prop(pt, "method"), "label": prop(pt, "label", cls="sp800-53a")}
        objs = [s for s in pt.get("parts", []) or [] if s.get("name") == "assessment-objects"]
        if objs:
            placed(objs[0])
            prose = objs[0].get("prose", "")
            m["objects"] = []
            for i, x in enumerate(_paragraphs(prose)):
                rewrite(x, used)                 # counts its markdown links and notes the parameters it inserts
                m["objects"].append(T(carried(R_PARAGRAPH, _paragraph, prose, i), "assessment-objects"))
        out.append({k: v for k, v in m.items() if v})
    return out

# ---------- three claims of the path map, checked value by value ----------
# The map calls these values derivable and does not carry them. A drop is
# declared for a value only where the derivation holds for it; where it does
# not, the value stays unaccounted and is counted.
derivable = collections.Counter()      # claim -> values for which it holds
not_derivable = collections.defaultdict(list)

def checked_drop(claim, holds, value, reason, where):
    if value is None: return
    if holds:
        derivable[claim] += 1; led.drop_value(value, reason)
    else:
        not_derivable[claim].append(where)

def item_label(pt):
    """the print label of a statement item (`a.`, `1.`, `(a)`): its letter or number is the last segment of the id"""
    label = prop(pt, "label")
    last = (pt.get("id") or "").rsplit(".", 1)[-1]
    checked_drop("item-label", label is not None and label.strip("().") == last.strip("()"), label, A_ITEM_LABEL, pt.get("id"))

def zero_padded(label):
    """`AC-2(10)` -> `AC-02(10)`: every number of the label padded to two digits"""
    return re.sub(r"[0-9]+", lambda m: m.group(0).zfill(2), label)

# ---------- statements: flatten prose-bearing statement/item nodes ----------
def flat_statements(c):
    out = []
    def walk(pt):
        placed(pt)
        if pt.get("prose"):
            out.append(pt)
        if pt.get("name") == "item": item_label(pt)
        for s in pt.get("parts", []) or []:
            walk(s)
    for pt in c.get("parts", []) or []:
        if pt.get("name") == "statement":
            walk(pt)
    return out

# ---------- convert live controls ----------
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
req_ids = {}
n_53a = 0

for c, parents, gchain in live:
    cid = c["id"]
    LINKS_OF[0] = {(l.get("href") or "").lstrip("#"): l.get("rel") for l in c.get("links", []) or []}
    rid = req_uri(cid)
    # labels: verify zero-padded == sp800-53a
    zp, la = prop(c, "label", cls="zero-padded"), prop(c, "label", cls="sp800-53a")
    if la is not None:
        if zp == la: label_eq += 1
        else: label_div.append(cid)
    plain = next((p["value"] for p in c.get("props", [])
                  if p.get("name") == "label" and not p.get("class")), cid.upper())
    checked_drop("zero-padded-label", zp is not None and zp == zero_padded(plain), zp, A_LABEL, cid)
    checked_drop("sp800-53a-label", la is not None and la == zero_padded(plain), la, A_LABEL, cid)
    # the class of a control: an enhancement is the control that has a `required` edge, a base control has none
    is_enhancement = any(l.get("rel") == "required" and (l.get("href") or "").lstrip("#") in by_id
                         for l in c.get("links", []) or [])
    checked_drop("class", c.get("class") == ("SP800-53-enhancement" if is_enhancement else "SP800-53"),
                 c.get("class"), A_CLASS, cid)
    # obligated parties: the control's implementation level where the source
    # gives one; where it gives none, the converter's default or the caller's
    lvls = prop(c, "implementation-level", ns="http://csrc.nist.gov/ns/rmf", all_=True)
    if lvls:
        parties = [D(R_PARTY, _party, v) for v in lvls]
    else:
        parties = [PARTY]; op_default += 1
    lvl_count[" + ".join(lvls) or "(none)"] += 1
    # statements + per-statement param declaration
    params = {pm["id"]: pm for pm in c.get("params", []) or []}
    stmts, declared_any = [], set()
    for pt in flat_statements(c):
        used = set()
        prose = rewrite(pt["prose"], used)
        sid = carried(R_STATEMENT, _statement_id, pt.get("id", f"{cid}_smt"), cid)
        s = {"id": sid, "modality": "must", "obligated-parties": parties,
             "prose": {"en": prose}}
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
        mod_count["must"] += 1
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
    # formal-ODP round-trip
    for pid, pm in params.items():
        fp = next((p["value"] for p in pm.get("props", []) if p.get("name") == "label"), None)
        if fp is not None:
            if formal(pid) == fp: formal_ok += 1
            else: formal_div.append((pid, fp))
            checked_drop("formal-odp-label", formal(pid) == fp, fp, A_FORMAL_ODP, pid)
    req = {"id": rid, "version": VER, "label": plain, "lifecycle": "active",
           "title": c.get("title", cid), "statements": stmts}
    # facets
    facets = {}
    guid = [T(rewrite(p["prose"]), "guidance") for p in c.get("parts", []) or []
            if p.get("name") == "guidance" and p.get("prose")]
    for p in c.get("parts", []) or []:
        if p.get("name") == "guidance" and p.get("prose"): placed(p)
    if guid: facets[F_NARR] = {"guidance": guid}
    used_f = set()
    objectives = [obj_tree(p, used_f) for p in c.get("parts", []) or []
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
            a["guidelines"] = [T(rewrite(g.get("prose", ""))) for g in pm["guidelines"]]
        alts = [p["value"] for p in pm.get("props", []) if p.get("name") == "alt-identifier"]
        if alts: a["alt-identifiers"] = alts
        al = next((p["value"] for p in pm.get("props", []) if p.get("name") == "alt-label"), None)
        if al: a["alt-label"] = al
        aggs = [p["value"] for p in pm.get("props", []) if p.get("name") == "aggregates"]
        if aggs: a["aggregates"] = aggs
        if a: odp_admin[pid] = a
    if odp_admin: facets[F_ODP] = {"params": odp_admin}
    if prop(c, "contributes-to-assurance", ns="http://csrc.nist.gov/ns/rmf") == "true":
        facets[F_RMF] = {"contributes-to-assurance": True}
    if facets: req["facets"] = facets
    # relations
    rels = []
    for l in c.get("links", []) or []:
        rel, href = l.get("rel"), (l.get("href") or "").lstrip("#")
        # the link's own `rel` is written as the relation type: it is the same word
        if rel == "related" and href in by_id and href not in withdrawn:
            rels.append({"type": rel, "ref": D(R_LINK, _link_ref, l["href"])}); rel_count["related"] += 1
        elif rel == "related":
            rel_count["related-to-withdrawn-or-missing"] += 1
        elif rel == "required" and href in by_id:
            rels.append({"type": rel, "ref": D(R_LINK, _link_ref, l["href"])}); rel_count["required"] += 1
        elif rel == "reference" and href in RES and RES[href]["url"]:
            rels.append({"type": rel, "ref": D(R_REFERENCE, _resolved, l["href"], RES_UUID[href], RES[href]["url"])})
            rel_count["reference"] += 1
        elif rel == "reference":
            rel_count["reference-unresolved"] += 1
    if rels:
        seen = {}; ded = []
        for r in rels:
            k = (r["type"], r["ref"])
            if k not in seen: seen[k] = r; ded.append(r)
            else: led.same(r, seen[k], R_SAME_RELATION)
        req["relations"] = ded
    # withdrawal inversion
    if succ_replaces.get(cid):
        entries = succ_replaces[cid]
        req["replaces"] = [{"ref": e["ref"], "mode": e["mode"]} for e in entries]
        req["annotations"] = {"nist-withdrawal": [
            {k: v for k, v in e.items() if k in ("ref", "label", "title", "into", "mode")}
            for e in entries]}
    req_ids[cid] = (rid, f"objects/req/{slug(cid)}.json", req)
LINKS_OF[0] = None

bundle = Bundle(os.path.join(OUTDIR, "sp800-53-core-bundle"))
for cid, (rid, bp, req) in req_ids.items():
    bundle.add(bp, req)

# ---------- family Sets + root ----------
def sortkey(cid):
    return prop(by_id[cid], "sort-id") or cid

root_members, fam_sets = [], 0
for g in cat.get("groups", []):
    fam = [c["id"] for c, _, gg in live if gg and gg[0]["id"] == g["id"]]
    fam.sort(key=sortkey)
    suri = D(R_FAMILY, _family_uri, g["id"])
    led.drop_value(g.get("class"), B_TYPE_TAG)       # `family`: the Set's URI and place under the root say it
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
        for p in over: placed(p)
        sobj["facets"] = {F_NARR: {"guidance": [T(rewrite(p.get("prose", "")), "overview") for p in over]}}
    if fam_replaces.get(g["id"]):                # sa-12 "moved to SR family": Set-level successor
        entries = fam_replaces[g["id"]]
        sobj["replaces"] = [{"ref": e["ref"], "mode": e["mode"]} for e in entries]
        sobj["annotations"] = {"nist-withdrawal": [
            {k: v for k, v in e.items() if k in ("ref", "label", "title", "into", "mode")}
            for e in entries]}
    bundle.add(f"objects/set/family-{slug(g['id'])}.json", sobj)
    root_members.append({"ref": suri, "sequence": len(root_members) * 10 + 10})
    fam_sets += 1
root = {"id": f"{NS}/set/root", "version": VER, "lifecycle": "active",
        "title": cat["metadata"]["title"], "members": root_members,
        "facets": {F_REF: {"resources": [
            {k: v for k, v in r.items() if v} for _, r in sorted(RES.items(), key=lambda kv: kv[1]["title"])]}}}
bundle.add("objects/set/root.json", root)

# ---------- baseline Sets ----------
bl_missing = collections.defaultdict(list)
for b, prof in BASELINES.items():
    ids = prof["imports"][0]["include-controls"][0]["with-ids"]
    members = []
    for i, cid in enumerate(ids):
        if cid in withdrawn or cid not in by_id:
            bl_missing[b].append(cid); continue
        members.append({"ref": req_uri(cid), "sequence": (i + 1) * 10})
    bundle.add(f"objects/set/baseline-{b.lower()}.json",
               {"id": f"{NS}/set/baseline/{b.lower()}", "version": VER, "lifecycle": "active",
                "title": prof["metadata"]["title"], "label": b, "members": members})

# ---------- facet stubs ----------
bundle.stub("sp800-53-narrative-stub.json", F_NARR.split("@")[0], [], {"guidance": {"type": "array"}})
bundle.stub("sp800-53a-stub.json", F_53A.split("@")[0], [],
            {"objectives": {"type": "array"}, "methods": {"type": "array"}})
bundle.stub("sp800-53-odp-stub.json", F_ODP.split("@")[0], [], {"params": {"type": "object"}})
bundle.stub("sp800-53-rmf-stub.json", F_RMF.split("@")[0], [],
            {"contributes-to-assurance": {"type": "boolean"}})
bundle.stub("sp800-53-references-stub.json", F_REF.split("@")[0], [], {"resources": {"type": "array"}})
MANIFEST = bundle.write({"source": cat["metadata"]["title"], "source-version": VER,
              "source-oscal-version": cat["metadata"]["oscal-version"],
              "baselines": {b: p["metadata"]["version"] for b, p in BASELINES.items()},
              "converter": "convert_nist.py v0.1",
              "namespace-note": "https://ns.nist.gov/sp800-53 minted to match the corpus's "
                                "pre-existing mapping-endpoint URIs; pending a NIST-published URI"})

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
wd_names = {cid.upper() for cid in withdrawn}
hit = {k: v for k, v in cited.items() if k in minted_names}
hit_wd = {k: v for k, v in cited.items() if k in wd_names}
miss = {k: v for k, v in cited.items() if k not in minted_names and k not in wd_names}

# ---------- the conversion ledger: where every source value went ----------
# The drops by path. Each names paths on which this converter carries
# nothing, so none of them can make a value that was lost beside carried ones
# read as dropped on purpose; the run checks that below. Where values of one
# path are carried and others are not, the drop is declared value by value at
# the place the script decides it (a tombstone, a type tag, a checked claim).
PATH_DROPS = [
 (r"\.metadata\.revisions\[\]\.", B_REVISIONS),
 (r"\.metadata\.(parties|roles)\[\]\.", B_DIRECTORY),
 (r"\.profile\.back-matter\.|^nist\.catalog\.back-matter\.resources\[\]\.rlinks\[\]\.media-type$", B_BACKMATTER),
 (r"\.profile\.(imports\[\]\.href|merge\.as-is)$", A_PROFILE),
 (r"^(nist\.catalog|[a-z]+\.profile)\.uuid$", B_UUID),
]
for pattern, reason in PATH_DROPS: led.drop(pattern, reason)
# What each reason may be declared for: the source paths a drop with that reason stands on. A declaration that
# reaches further (a whole control where its class was meant) would swallow a value that was lost.
DROP_REACH = {
 A_TOMBSTONE: r"\.controls\[\]\.(class|props\[\]\.(name|class|ns|value))$",
 A_CLASS: r"\.controls\[\]\.class$",
 A_LABEL: r"\.controls\[\]\.props\[\]\.value$",
 A_FORMAL_ODP: r"\.params\[\]\.props\[\]\.value$",
 A_ITEM_LABEL: r"\.parts\[\]\.props\[\]\.value$",
 A_PROFILE: r"\.profile\.(imports\[\]\.href|merge\.as-is)$",
 B_TYPE_TAG: r"(\.parts\[\]\.name|\.groups\[\]\.class)$",
 B_UUID: r"^(nist\.catalog|[a-z]+\.profile)\.uuid$",
 B_RESOURCE_UUID: r"^nist\.catalog\.back-matter\.resources\[\]\.uuid$",
 B_REVISIONS: r"\.metadata\.revisions\[\]\.",
 B_DIRECTORY: r"\.metadata\.(parties|roles)\[\]\.",
 B_BACKMATTER: r"(\.profile\.back-matter\.|\.back-matter\.resources\[\]\.rlinks\[\]\.media-type$)",
}
T_WRITTEN = time.time()
LEDGER = led.account(bundle.out, {**bundle.objects, "content-manifest.json": MANIFEST})
T_ACCOUNTED = time.time()
LT = LEDGER["totals"]
# The record. account() gives one entry per source leaf value; for 115,680 values that is some fifty megabytes,
# so what is written is one row per source path and outcome, with counts over the entries just checked.
LEDGER_FILE = "sp800-53-conversion-ledger.json"
RECORD = ledger_by_path(LEDGER)
with open(os.path.join(OUTDIR, LEDGER_FILE), "w", encoding="utf-8") as f:
    json.dump(RECORD, f, indent=1, ensure_ascii=False); f.write("\n")
print(f"ledger: copied {LT['copied']}, transformed {LT['transformed']}, intentionally dropped "
      f"{LT['intentionally-dropped']}, unaccounted {LT['unaccounted']}; failed checks {len(LEDGER['verification-failures'])}"
      f"  ({T_ACCOUNTED - T_WRITTEN:.1f} s to account for {LEDGER['leaf-values']:,} values)")

# ---------- what the ledger says, for the report ----------
def source_chain(entry):
    """-> [(key, node), ...] from the root of its source document down to the leaf a ledger entry is about"""
    tag, pointer = entry["source"].split("#", 1)
    node, chain = led.docs[tag], []
    for x in (p.replace("~1", "/").replace("~0", "~") for p in pointer.split("/")[1:]):
        node = node[int(x)] if isinstance(node, list) else node[x]
        chain.append((x, node))
    return chain

def enclosing(chain, kind):
    """-> the innermost element of an array `kind` (controls, parts, props, params, links) the leaf lies in"""
    found = None
    for i in range(1, len(chain)):
        if chain[i - 1][0] == kind and isinstance(chain[i][1], dict): found = chain[i][1]
    return found

# The unaccounted values in classes: what each is, and a recommendation. To carry
# a value changes the bundle; that and every drop is the author's to decide.
CLASSES = {
 "prop-selector": (
   "the name, the class or the namespace of a prop: it selects the rule that is applied to the prop's value",
   "drop, by one decision for all: so the author decided for the one selector of the IFA corpus (the prop name of a "
   "response type). What becomes of the value a selector selects is said for that value"),
 "assessment-for": (
   "the `assessment-for` link of an assessment objective (href and rel): the statement the objective assesses",
   "carry: `assessment-for` on the objective in sp800-53a@1, as the id of the statement; the CIS Controls converter "
   "carries the same link of its source. Where the link names a statement part as a whole there is no statement to "
   "name, and a link into another control is to be looked at in the source first"),
 "part-id": (
   "the id of a part that gets no id in the bundle: the guidance, an assessment method, a statement part that only "
   "groups items, the overview of a family",
   "drop: each is the id of its control or family with a fixed suffix (`_gdn`, `_asm-examine`, `_smt`, `_ovw`). To "
   "decide together with the `assessment-for` links: the link of a control's first objective names the statement "
   "part as a whole, which has no address in the bundle"),
 "boolean": (
   "a value carried as a JSON boolean: `contributes-to-assurance` = `true` is written as `true` in rmf@1. The ledger "
   "follows strings and integers and cannot see it arrive",
   "nothing to decide for the bundle: the value is carried. For the ledger: a way to state a rule whose result is a "
   "boolean (oscal_conv_lib), or a declared reason"),
 "formal-odp-label": (
   "the formal ODP label of a parameter where the converter's round-trip from the parameter id does not give it "
   "(parameters of enhancements: `ac-02.01_odp` is labelled `AC-02(01)_ODP`, the rule gives `AC-02.01_ODP`)",
   "drop, after the rule is corrected to write the number of the enhancement in brackets: measured on 5.2.0 on "
   "2026-11-14, it then gives 1,455 of the 1,458 labels; or carry the label in odp@1 beside `alt-label`"),
 "withdrawn-without-successor": (
   "everything of a withdrawn control that names no successor: its id, title, labels and the one statement that says "
   "why it was withdrawn. Nothing of such a control is in the bundle",
   "carry: a Requirement with lifecycle `withdrawn` for a control no other control replaces, with its statement as "
   "the reason; or drop with that reason stated"),
 "related-to-withdrawn": (
   "a `related` link to a withdrawn control (href and rel)",
   "carry: the relation to the successor the withdrawn control names; or drop, the target being a tombstone"),
 "document-metadata": (
   "document metadata the manifest does not hold: `last-modified` of the catalogue and of the four profiles, the "
   "`oscal-version` of the profiles, the catalogue's keywords",
   "carry: `provenance.source-documents` in the manifest, as the IFA conversion does (title, version, last-modified, "
   "oscal-version per document)"),
 "metadata-links": (
   "the catalogue's links to its other forms (`alternate`: the PDF, `canonical`: the DOI, `cprt`: the reference tool)",
   "drop: a link to another serialisation of the source, a class decided for IFA; the three resources they name are "
   "on the root Set"),
 "responsible-parties": (
   "who is responsible for a source document in which role (role-id and party uuid): creator, publisher and their contacts",
   "drop with the directory of parties and roles; or carry the publisher as the author in the manifest's provenance, as a landmark URI"),
 "part-title": (
   "the title of the overview part of the PM family",
   "carry: beside the overview text in narrative@1; or drop, it repeats the family's title in other words"),
}
unaccounted_classes = {}
for e in LEDGER["entries"]:
    if e["outcome"] != "unaccounted": continue
    chain = source_chain(e)
    leaf, control, part = chain[-1][0], enclosing(chain, "controls"), enclosing(chain, "parts")
    a_prop, a_param, a_link = enclosing(chain, "props"), enclosing(chain, "params"), enclosing(chain, "links")
    sub = None
    if control is not None and control.get("id") in wd_no_successor: k = "withdrawn-without-successor"; sub = control["id"]
    elif a_prop is not None and leaf in ("name", "class", "ns"): k = "prop-selector"; sub = leaf
    elif part is not None and a_link is not None:
        k = "assessment-for"; sub = leaf
        if leaf == "href" and control is not None:             # what the link names, among the parts of its own control
            named = next((p for p in all_parts(control) if p.get("id") == chain[-1][1].lstrip("#")), None)
            sub = ("href to a statement the bundle holds" if named is not None and named.get("prose")
                   else "href to a statement part as a whole, whose text is in its items" if named is not None
                   else "href to a part of another control")
    elif part is not None and leaf == "id":
        k = "part-id"; sub = str(part.get("name")) + ("" if part.get("prose") or part.get("name") != "statement" else " without prose")
    elif part is not None and leaf == "title": k = "part-title"
    elif a_prop is not None and a_param is not None and a_prop.get("name") == "label": k = "formal-odp-label"
    elif a_prop is not None and control is not None and a_prop.get("name") == "contributes-to-assurance": k = "boolean"
    elif a_link is not None and control is not None: k = "related-to-withdrawn"; sub = leaf
    elif ".metadata.links[]" in e["path"]: k = "metadata-links"; sub = leaf
    elif ".metadata.responsible-parties[]" in e["path"]: k = "responsible-parties"
    elif ".metadata." in e["path"]: k = "document-metadata"; sub = e["path"].split(".metadata.")[1]
    else: k = "other"
    c = unaccounted_classes.setdefault(k, {"count": 0, "example": e["source"], "value": chain[-1][1], "of": collections.Counter()})
    c["count"] += 1
    if sub: c["of"][str(sub)] += 1
assert sum(c["count"] for c in unaccounted_classes.values()) == LT["unaccounted"]

# the declared drops by what they rest on, and the rules by how many source values each accounts for
drop_reasons = collections.Counter(e["reason"] for e in LEDGER["entries"] if e["outcome"] == "intentionally-dropped")
drops_by_map = sorted(((r, n) for r, n in drop_reasons.items() if r.startswith("path map: ")), key=lambda x: -x[1])
drops_by_ifa = sorted(((r, n) for r, n in drop_reasons.items() if r.startswith(IFA)), key=lambda x: -x[1])

# Wiring checks. The ledger checks every claim of a destination against the written file. It cannot check a
# declaration that reaches too far, or a record that is not this run's. Each check below stands against a defect
# that was put into a copy of this script on purpose: without the check such a run ends with exit code 0
# (test_convert_nist_ledger.py holds them). A check that fails stops the run with a non-zero exit, after the
# reports are written. The first two follow the checks of convert_csf.py.
wiring = []
# a drop is declared with one of the reasons above, and only for the paths that reason names
for reason, path in sorted({(e["reason"], norm(e["path"])) for e in LEDGER["entries"] if e["outcome"] == "intentionally-dropped"}):
    if reason not in DROP_REACH or not reason.startswith(("path map: ", IFA)):
        wiring.append(f"a drop is declared on neither of the two grounds: {reason!r} for {path}")
    elif not re.search(DROP_REACH[reason], path):
        wiring.append(f"a drop reaches further than it names: {path} is declared as {reason!r}")
# a drop by path is declared only for paths on which nothing is carried
carried_paths = {e["path"] for e in LEDGER["entries"] if e["outcome"] in ("copied", "transformed")}
for p in sorted({e["path"] for e in LEDGER["entries"] if e.get("reason") in {r for _, r in PATH_DROPS}} & carried_paths):
    wiring.append(f"a drop declared by path covers {p}, on which other values are carried: a value lost there would "
                  f"read as dropped on purpose; declare such a drop value by value")
rule_values, rule_destinations = collections.Counter(), collections.Counter()
for e in LEDGER["entries"]:
    rules_here = [d["rule"] for d in e.get("destinations", []) if "rule" in d]
    rule_destinations.update(rules_here)
    rule_values.update(set(rules_here))

# What the ledger cannot see. It follows source values into the bundle; a value the converter writes on its own has
# no entry. They are found from the other side: every leaf value of a written object that is neither a source value
# nor the result of a stated rule, by the place it stands in.
own_values, own_example = collections.Counter(), {}
def not_from_the_source(node, place):
    if isinstance(node, dict):
        for k, v in node.items(): not_from_the_source(v, f"{place}/{k}")
    elif isinstance(node, list):
        for v in node: not_from_the_source(v, place + "/[]")
    elif not tracked(node):
        own_values[place] += 1; own_example.setdefault(place, node)
for rel in sorted(bundle.objects): not_from_the_source(bundle.objects[rel], "")
OWN_WHY = [   # place pattern -> what stands behind the value, if not a source value
 (r"/lifecycle$", "the converter's: every object it writes is `active`; a withdrawn control is not written"),
 (r"/modality$", "the converter's corpus rule: every statement of Rev 5 is read as `must`"),
 (r"/parameters/\[\]/type$", "decided by the shape of the source parameter: `choice` where it has a `select`, else `string`"),
 (r"/contributes-to-assurance$", "the source's `true`, written as a boolean (see the unaccounted class)"),
 (r"/members/\[\]/sequence$", "the member's position: in the catalogue (root Set) or in the profile's list (baseline Sets)"),
 (r"/obligated-parties/\[\]$", "the converter's default party or the caller's, where the source gives no implementation level"),
 (r"^/id$", "the URI of the root Set and of a baseline Set, the latter from the name of the profile's file"),
 (r"^/label$", "the label of a baseline Set, from the name of the profile's file"),
]
def own_why(place): return next((why for rx, why in OWN_WHY if re.search(rx, place)), "the converter's")

def md_count(kind, also=None):
    return sum(n for (k, rel), n in md_targets.items() if k == kind and (also is None or (rel in also)))

# ---------- coverage ----------
# The path map: where each source path is MEANT to go. Rows that say "not
# carried" name a level of their own: `dropped` where the ledger holds a
# declared reason, `open` where nothing is decided. The ledger's totals are
# what was measured; a path with a row here counts as mapped either way.
CTL = r"^nist\.catalog\.groups\[\]\.controls\[\]"
PROF = r"^(low|moderate|high|privacy)\.profile"
DROPPED, OPEN = "dropped", "open"
RULES = [
 (r"^nist\.catalog\.metadata\.(title|version|oscal-version)$", "L1",
  "bundle manifest provenance (source, source-version, source-oscal-version); the title is also the root Set's, "
  "the version stands on every object"),
 (r"^nist\.catalog\.metadata\.revisions\[\]\.", DROPPED, "not carried: revision history of the source document (as decided for IFA)"),
 (r"^nist\.catalog\.metadata\.(parties|roles)\[\]\.", DROPPED,
  "not carried: the source's directory of parties and roles (as decided for IFA)"),
 (r"^nist\.catalog\.uuid$", DROPPED, "not carried: the uuid of the source document (as decided for IFA)"),
 (r"^nist\.catalog\.metadata\.", OPEN,
  "not carried and not decided: the document's last-modified, its keywords, its links to its other forms, and who is "
  "responsible for it"),
 (r"^nist\.catalog\.back-matter\.resources\[\]\.(title|citation\.text|rlinks\[\]\.href)$", "L1",
  "references@1 facet on the root Set (title/citation/url); the link is also the target of a control's `reference` relation"),
 (r"^nist\.catalog\.back-matter\.resources\[\]\.uuid$", "L1",
  "the key by which a control's reference link is resolved to the resource's link; not carried itself (as decided "
  "for IFA where no link names it)"),
 (r"^nist\.catalog\.back-matter\.", DROPPED, "not carried: the media type of a resource's link (as decided for IFA)"),
 (r"^nist\.catalog\.groups\[\]\.(id|title)$", "L1", "family Set id/title (D21 nesting under root)"),
 (r"^nist\.catalog\.groups\[\]\.class$", DROPPED,
  "not carried: a type tag; the Set's URI and its place under the root say `family` (as decided for IFA)"),
 (r"^nist\.catalog\.groups\[\]\.props\[\]\.value$", "L1", "family Set label"),
 (r"^nist\.catalog\.groups\[\]\.props\[\]\.name$", OPEN, "selects the label; not carried and not decided"),
 (r"^nist\.catalog\.groups\[\]\.parts\[\]\.prose$", "L2",
  "pm overview part -> narrative@1 guidance on the pm family Set (language-tagged)"),
 (r"^nist\.catalog\.groups\[\]\.parts\[\]\.name$", DROPPED, "not carried: a type tag (as decided for IFA)"),
 (r"^nist\.catalog\.groups\[\]\.parts\[\]\.", OPEN, "not carried and not decided: the id and the title of the pm overview part"),
 (CTL + r"\.(id|title)$", "L1",
  "Requirement id (URI mint, dot form = corpus mapping endpoints) + title | withdrawn: dropped, lineage inverted onto "
  "the successor (URI and title in `replaces` and the nist-withdrawal annotation); a withdrawn control that names no "
  "successor leaves nothing"),
 (CTL + r"\.class$", DROPPED,
  "not carried; encoded structurally: family Set membership + `required` base edge distinguishes enhancements "
  "(checked per control)"),
 (CTL + r"\.props\[\]\.value$", "L1",
  "label(plain)->label; zero-padded/sp800-53a label->not carried, derivable from the plain label (checked per value); "
  "sort-id->Set sequence; implementation-level->obligated-parties mint; contributes-to-assurance->rmf@1 (a JSON "
  "boolean); status->tombstone drop + successor replaces[]"),
 (CTL + r"\.props\[\]\.(name|ns|class)$", OPEN,
  "select the rule for the prop's value; not carried and not decided (of a withdrawn control: dropped with the tombstone)"),
 (CTL + r"\.links\[\]\.(href|rel)$", "L1",
  "related->related; required->required; reference->reference (resolved URL); incorporated-into/moved-to->successor "
  "replaces[] (merged-into/renamed) + nist-withdrawal annotation; a `related` link to a withdrawn control is not carried"),
 (CTL + r"\.params\[\]\.(id|label)$", "L1",
  "statement-scoped kernel parameter decl (name, label) on each inserting statement (per-statement parameter rule)"),
 (CTL + r"\.params\[\]\.select\.", "L1",
  "choice type + choices[] + cardinality many (one-or-more)"),
 (CTL + r"\.params\[\]\.guidelines\[\]\.prose$", "L2",
  "odp@1 facet params.{name}.guidelines (language-tagged)"),
 (CTL + r"\.params\[\]\.props\[\]\.value$", "L1",
  "alt-identifier/alt-label/aggregates -> odp@1 facet; prop label (formal ODP id) -> not carried: derivable from the "
  "parameter id where the round-trip holds (checked per value), else not decided"),
 (CTL + r"\.params\[\]\.props\[\]\.", OPEN, "select the rule for the prop's value; not carried and not decided"),
 (CTL + r"\.parts\[\]\.id$", "L1",
  "statement/item with prose -> statement id (control prefix removed); assessment-objective -> its id in sp800-53a@1; "
  "the ids of guidance, assessment-method and prose-less statement parts are not carried and not decided"),
 (CTL + r"\.parts\[\]\.name$", DROPPED,
  "not carried: a type tag that decided the place (statement/item -> statements[]; guidance -> narrative@1; "
  "assessment-* -> sp800-53a@1) (as decided for IFA)"),
 (CTL + r"\.parts\[\]\.prose$", "L1",
  "statement prose (insertions -> {param:} tokens); guidance/objectives/objects prose -> facets (language-tagged; md #-links -> text)"),
 (CTL + r"\.parts\[\]\.(ns|class)$", "L1",
  "part-name namespace markers; encoded by facet placement"),
 (CTL + r"\.parts\[\]\.props\[\]\.value$", "L1",
  "sp800-53a objective/method labels -> sp800-53a@1; method EXAMINE/INTERVIEW/TEST -> sp800-53a@1 methods; item print "
  "labels -> not carried, derivable from the item id (checked per value)"),
 (CTL + r"\.parts\[\]\.props\[\]\.", OPEN, "select the rule for the prop's value; not carried and not decided"),
 (CTL + r"\.parts\[\]\.links\[\]\.", OPEN,
  "`assessment-for`: the statement an assessment objective assesses; not carried and not decided"),
 (PROF + r"\.imports\[\]\.include-controls\[\]\.with-ids\[\]$", "L1",
  "baseline Set members (minted URIs, catalog order)"),
 (PROF + r"\.metadata\.title$", "L1", "baseline Set title"),
 (PROF + r"\.metadata\.version$", "L1", "bundle manifest provenance (baselines)"),
 (PROF + r"\.metadata\.(parties|roles)\[\]\.", DROPPED,
  "not carried: the source's directory of parties and roles (as decided for IFA)"),
 (PROF + r"\.uuid$", DROPPED, "not carried: the uuid of the source document (as decided for IFA)"),
 (PROF + r"\.back-matter\.", DROPPED,
  "not carried: the resource that names the imported catalogue in its three forms (as decided for IFA)"),
 (PROF + r"\.metadata\.", OPEN,
  "not carried and not decided: the document's last-modified and oscal-version, and who is responsible for it"),
 (PROF + r"\.(imports\[\]\.href|merge\.as-is)$", "L3",
  "OSCAL-profile resolution mechanics; the selection IS the Set (no semantic residue)"),
]
rows, unmapped = coverage(paths, RULES)

# what the ledger found under the paths whose sentence in the map claimed a destination
by_path = collections.Counter()
for r in RECORD["paths"]: by_path[(norm(r["path"]), r["outcome"])] += r["count"]
def not_carried(pattern):
    """the source values under paths that match which have no destination, declared or not"""
    return sum(n for (p, o), n in by_path.items() if o in ("intentionally-dropped", "unaccounted") and re.search(pattern, p))
F_ASSESSMENT_FOR = not_carried(CTL + r"\.parts\[\]\.links\[\]\.")
F_CATALOG_META = not_carried(r"^nist\.catalog\.(uuid$|metadata\.)")
F_PROFILE_META = not_carried(PROF + r"\.(uuid$|metadata\.|back-matter\.)")
F_TAGS = not_carried(r"\.props\[\]\.(name|class|ns)$|\.parts\[\]\.name$|\.groups\[\]\.class$")
F_PART_IDS = not_carried(CTL + r"\.parts\[\]\.id$")
F_MEDIA = not_carried(r"^nist\.catalog\.back-matter\..*media-type$")

nset = sum(1 for rel in bundle.objects if "/set/" in rel)
j = report(
    os.path.join(OUTDIR, "sp800-53-coverage-report.md"),
    os.path.join(OUTDIR, "sp800-53-coverage-report.json"),
    "NIST SP 800-53 Rev 5 + 800-53B -> Semantic Core: Coverage Report (computed)",
    f"Source: **{cat['metadata']['title']}** v{VER} (OSCAL {cat['metadata']['oscal-version']}) "
    f"+ four 800-53B baseline profiles. Census: `drafts/gate-3-census.md`.",
    [f"- Objects emitted: **{len(req_ids)} Requirements** (324+872 minus {len(withdrawn)} withdrawn tombstones), "
     f"**{nset} Sets** ({fam_sets} families + root + 4 baselines), manifest with both digests.",
     f"- Baseline membership: " + ", ".join(f"{b} {len(BASELINES[b]['imports'][0]['include-controls'][0]['with-ids'])}"
                                            for b in BASELINES) + ".",
     f"- **Conversion ledger** (every source value followed into the written files): **{LT['copied']:,} copied**, "
     f"**{LT['transformed']:,} transformed** by a named rule, **{LT['intentionally-dropped']:,} dropped** for a declared "
     f"reason, **{LT['unaccounted']:,} unaccounted**; checks that failed: {len(LEDGER['verification-failures'])}. The "
     f"line `UNMAPPED` above counts source paths that have a row in the path map, and a row may say that the value is "
     f"not carried. The ledger is the measure of what arrived; its sections are at the end of this report."],
    [f"- **Withdrawn tombstones dropped, lineage inverted (kernel `replaces[]`)**: {len(withdrawn)} withdrawn; "
     f"{sum(len(v) for v in succ_replaces.values())} successor edges on Requirements + "
     f"{sum(len(v) for v in fam_replaces.values())} on family Sets (sa-12 'moved to SR' - the successor is a "
     f"whole family; shared base makes Set-level `replaces` legal) "
     f"(incorporated-into->merged-into, moved-to->renamed); statement-precision + withdrawn label/title in "
     f"`annotations['nist-withdrawal']`; withdrawn->withdrawn chains x{len(wd_chain)}, dangling x{len(wd_dangling)}. "
     f"Withdrawn controls that name no successor: x{len(wd_no_successor)}"
     + (f" ({', '.join(wd_no_successor)}) - nothing of them is in the bundle" if wd_no_successor else "") + ".",
     f"- **Modality corpus rule `must` x{mod_count['must']}**: Rev 5 statements are uniformly imperative and "
     f"obligation binds on baseline selection - the INVERSE of the declarative national pattern "
     f"(ISM/CIS/CyFun/C5). Force in the mood, selection in the baseline Sets; both confirm D13's split axes.",
     obligated_party_line(PARTY, PARTY_ORIGIN, PARTY_DEFAULT, source_states=PARTY_SOURCE_STATES)
     + f" The source gives a level on x{len(req_ids) - op_default} controls ("
     + ", ".join(f"{k} x{v}" for k, v in sorted(lvl_count.items(), key=lambda x: -x[1]) if k != "(none)")
     + f"), written as `{NS}/party/<level>` on their x{mod_count['must'] - op_default_stmts} statements. It gives "
     f"none on x{op_default} controls; their x{op_default_stmts} statements are the only ones that carry the "
     + ("caller's party." if PARTY_ORIGIN == "caller" else "converter's default."),
     f"- **Two-layer ODP params -> statement-scoped decls**: declared on each statement whose prose inserts "
     f"them (per-statement parameter rule); choice x{sum(1 for cid, (rid, _, r) in req_ids.items() for s in r['statements'] for p in s.get('parameters', []) if p['type'] == 'choice')}, "
     f"string else; legacy _prm_ aggregates carried as params + odp@1 `aggregates`; params without a "
     f"statement insertion site x{sum(no_site.values())} declared on the first statement "
     f"({len(facet_only)} bind only in the 53A objectives, {len(nowhere)} nowhere).",
     f"- **SP 800-53A layer -> sp800-53a@1** on {n_53a} Requirements: objective trees (53a labels kept - "
     f"the #10 addressing surface) + EXAMINE/INTERVIEW/TEST methods with object lists (language-tagged).",
     f"- **Relations**: " + ", ".join(f"{k} x{v}" for k, v in sorted(rel_count.items(), key=lambda x: -x[1])) +
     f"; reference targets resolved to publication URLs (landmark); title/citation table -> references@1 on the root Set.",
     f"- **Markdown links in prose -> their link text** x{n_links[0]}; the target of a link is not carried. "
     f"x{md_count('a back-matter resource')} name a back-matter resource, of which x{md_count('a back-matter resource', ('reference',))} "
     f"are also a `reference` link of the same control and so a relation; x{md_count('another control')} name another "
     f"control, of which x{md_count('another control', ('related', 'required'))} are also a `related` or `required` link of "
     f"the same control; x{md_count('a withdrawn control')} name a withdrawn control, x{md_count('a statement of a control')} "
     f"a statement of a control, x{md_count('a family')} a family, x{md_count('a parameter')} a parameter, "
     f"x{md_count('nothing the catalogue defines')} nothing the catalogue defines.",
     f"- **Conversion ledger (measured per source value)**: each of the {LEDGER['leaf-values']:,} leaf values of the "
     f"catalogue and the four profiles was followed into the written files. **{LT['copied']:,} copied** (the value "
     f"stands, with its type, at the destination, read back from the written file), **{LT['transformed']:,} "
     f"transformed** (a named rule made the destination from it; the rule was applied to the source again and "
     f"compared), **{LT['intentionally-dropped']:,} intentionally dropped** (a stated reason: "
     f"{sum(n for _, n in drops_by_map):,} where the path map of this converter already said the value is not "
     f"carried, {sum(n for _, n in drops_by_ifa):,} in a class the author decided for the IFA corpus on 2026-11-13), "
     f"**{LT['unaccounted']:,} unaccounted**. Checks that failed: {len(LEDGER['verification-failures'])}. The record is "
     f"`{LEDGER_FILE}`: one row per source path and outcome, every row a count over values that were traced one by "
     f"one in the run that wrote it. An equal value elsewhere in the bundle does not count: a value is traced by "
     f"what the converter did with it.",
     f"- **Label triplet**: zero-padded == sp800-53a asserted ({label_eq} equal, divergent: {label_div or 'none'}); "
     f"plain -> `label`; zero-padded L3-derivable.",
     f"- **Formal ODP ids round-trip** (prop label == uppercase(param name)): ok x{formal_ok}, "
     f"divergent x{len(formal_div)}" + (f" ({formal_div[:5]})" if formal_div else "") + ".",
     f"- **Payload free text language-tagged**: " + ", ".join(f"{k} x{v}" for k, v in sorted(lang_wraps.items())) + "."],
    [f"- **#10 measure (ODP -> statement addressing)**: insertion-count histogram "
     f"{dict(sorted(decl_hist.items()))}; params inserted in >=2 statements: **{len(multi_decl)}** "
     + (f"({[(c, p) for c, p, n in multi_decl[:6]]}...)" if multi_decl else "(none)") +
     f" - the (requirement, ODP) address resolves via the declaring statement"
     + ("" if not multi_decl else "; ambiguous cases need the statement map") + ".",
     f"- **Corpus mapping endpoints vs minted ids**: {sum(hit.values())} citations resolve "
     f"({len(hit)} distinct), {sum(hit_wd.values())} hit withdrawn tombstones "
     f"({sorted(hit_wd)[:8] if hit_wd else []}) - a resolver follows the successor's `replaces[]` backwards; "
     f"{sum(miss.values())} cite unknown labels ({sorted(miss)[:8] if miss else []}).",
     f"- **Baseline ids not emitted** (withdrawn or unknown): " +
     ("; ".join(f"{b}: {v}" for b, v in bl_missing.items()) if bl_missing else "none") + ".",
     f"- **Cross-control param insertions x{len(cross_param)}** ({cross_param}): prose in one control "
     f"inserts another control's ODP - a source irregularity (3 of 2,945 insertions); the declaration is "
     f"duplicated onto the inserting statement per the per-statement parameter rule. REPORTED upstream.",
     f"- **Params bound nowhere x{len(nowhere)}** (ODPs defined for assessment that neither control text "
     f"nor 53A objectives insert) - declarations without any insertion site.",
     f"- **Path-map sentences the ledger did not confirm** (the map below is corrected; the counts are the ledger's): "
     f"(1) `parts[].links[]` was described as in-prose citation links, resolved with the reference table. The "
     f"x{F_ASSESSMENT_FOR:,} values are the `assessment-for` links of assessment objectives, and none is carried. "
     f"(2) The catalogue's `uuid` and all of its `metadata` were mapped to the manifest. The manifest holds title, "
     f"version and oscal-version; the other x{F_CATALOG_META} values are not in the bundle. "
     f"(3) The same for the four profiles: their title is the baseline Set's title and their version is in the "
     f"manifest; x{F_PROFILE_META} other values of `uuid`, `metadata` and `back-matter` are not in the bundle. "
     f"(4) The name, class and namespace of a prop, the name of a part and the class of a group were mapped together "
     f"with the values they select; x{F_TAGS:,} such values are not carried. "
     f"(5) `parts[].id` was mapped as a whole; x{F_PART_IDS:,} ids are not carried: those of guidance, assessment-method "
     f"and prose-less statement parts, and of the statements of the withdrawn controls without a successor. "
     f"(6) The formal ODP label was called derivable, its round-trip asserted; the round-trip holds for "
     f"x{formal_ok} of {formal_ok + len(formal_div)}. "
     f"(7) Of the pm overview part only the prose is carried, not its id and title. "
     f"(8) The media type of a back-matter link (x{F_MEDIA}) is not on the root Set. "
     f"(9) The markdown links in prose were said to ride the reference relation; "
     f"x{md_count('a back-matter resource', ('reference',))} of {n_links[0]} do.",
     f"- **Withdrawn controls without a successor x{len(wd_no_successor)}**: " +
     ("; ".join(f"`{i}` ({by_id[i].get('title')})" for i in wd_no_successor) or "none") +
     ". The catalogue gives such a control no `incorporated-into` or `moved-to` link, only a statement that says "
     "why it was withdrawn. The converter drops every withdrawn control and writes its lineage on the successor; "
     "where there is none, id, title, labels and that statement are in no object. Reported, not changed.",
     f"- **The label of a withdrawn control is taken by position, not by class x{len(wd_label_not_plain)}** "
     f"(reported, not fixed: the fix changes the bundle): the nist-withdrawal annotation takes the first `label` prop "
     f"of the withdrawn control, whatever its class. In this source that is the zero-padded one, so an annotation "
     f"says `{wd_label_not_plain[0][1] if wd_label_not_plain else '-'}` where the Requirements carry the plain form "
     f"(`{wd_label_not_plain[0][2] if wd_label_not_plain else '-'}`). The plain label of these controls is dropped "
     f"with the tombstone; first: `{wd_label_not_plain[0][3] if wd_label_not_plain else '-'}`.",
     f"- **Three claims of the path map, checked value by value**: a zero-padded label is the plain label with its "
     f"numbers padded (holds x{derivable['zero-padded-label']}, fails x{len(not_derivable['zero-padded-label'])}); the "
     f"SP 800-53A label of a control equals it (x{derivable['sp800-53a-label']} / x{len(not_derivable['sp800-53a-label'])}); "
     f"the class of a control is told by its `required` edge (x{derivable['class']} / x{len(not_derivable['class'])}); "
     f"the print label of a statement item is the last segment of its id (x{derivable['item-label']} / "
     f"x{len(not_derivable['item-label'])}); the formal ODP label follows from the parameter id "
     f"(x{derivable['formal-odp-label']} / x{len(not_derivable['formal-odp-label'])}). Where a claim holds the value is a "
     f"declared drop; where it fails the value is unaccounted."],
    rows, unmapped,
    {"source-version": VER,
     "objects-emitted": {"requirements": len(req_ids), "sets": nset},
     "withdrawn": {"count": len(withdrawn), "successor-edges": sum(len(v) for v in succ_replaces.values()),
                   "family-set-edges": sum(len(v) for v in fam_replaces.values()),
                   "chains": wd_chain, "dangling": wd_dangling},
     "cross-control-params": [{"control": c, "param": p} for c, p in cross_param],
     "no-statement-site": {"total": sum(no_site.values()), "facet-only": len(facet_only),
                           "nowhere": len(nowhere)},
     "modality": dict(mod_count),
     "obligated-party": obligated_party_record(PARTY, PARTY_ORIGIN, PARTY_DEFAULT, PARTY_SOURCE_STATES),
     "obligated-party-use": {"controls": {"source-states": len(req_ids) - op_default, "not-stated": op_default},
                             "statements": {"source-states": mod_count["must"] - op_default_stmts,
                                            "not-stated": op_default_stmts},
                             "implementation-levels": dict(lvl_count)},
     "backlog-10": {"insertion-histogram": {str(k): v for k, v in sorted(decl_hist.items())},
                    "multi-declared": [{"control": c, "param": p, "statements": n} for c, p, n in multi_decl]},
     "endpoint-crosscheck": {"resolved": sum(hit.values()), "distinct": len(hit),
                             "withdrawn-hits": hit_wd, "unknown": miss},
     "baseline-missing": dict(bl_missing),
     "lang-wraps": dict(lang_wraps),
     "withdrawn-without-successor": wd_no_successor,
     "withdrawn-label-not-plain": [{"control": i, "written": w, "plain": p, "source": s} for i, w, p, s in wd_label_not_plain],
     "markdown-link-targets": [{"names": k, "also-a-link-of-the-control": rel or None, "count": n}
                               for (k, rel), n in sorted(md_targets.items(), key=lambda x: (-x[1], x[0]))],
     "ledger": {"file": LEDGER_FILE, "leaf-values": LEDGER["leaf-values"], "totals": LT,
                "verification-failures": len(LEDGER["verification-failures"]),
                "rules": [{"rule": r, "source-values": rule_values[r], "destinations": rule_destinations[r]}
                          for r, _ in sorted(rule_values.items(), key=lambda x: (-x[1], x[0]))],
                "declared-drops": {
                    "the-path-map-said-not-carried": [{"reason": r, "count": n} for r, n in drops_by_map],
                    "a-class-decided-for-ifa-2026-11-13": [{"reason": r, "count": n} for r, n in drops_by_ifa]},
                "unaccounted-classes": [{"class": k, "count": c["count"], "of-which": dict(c["of"].most_common()),
                                         "is": CLASSES.get(k, ("not classified", ""))[0], "example": c["example"],
                                         "recommendation": CLASSES.get(k, ("", "to be looked at"))[1]}
                                        for k, c in sorted(unaccounted_classes.items(), key=lambda x: -x[1]["count"])],
                "checked-claims": {k: {"holds": derivable[k], "fails": len(not_derivable[k])}
                                   for k in ("zero-padded-label", "sp800-53a-label", "class", "item-label", "formal-odp-label")},
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
    f.write("\n## Conversion ledger: the rules\n\n"
            "A value the converter computes is stated as a named rule with a pure function. After the bundle is "
            "written the function is applied to the source value again and the result is compared with what the "
            "file holds. A rule with several inputs counts each of them: the id of a control is an input of the "
            "rule that cuts it off a statement id.\n\n"
            "| rule | source values | destinations |\n|---|---:|---:|\n" +
            "".join(f"| {r} | {rule_values[r]:,} | {rule_destinations[r]:,} |\n"
                    for r, _ in sorted(rule_values.items(), key=lambda x: (-x[1], x[0]))))
    f.write(f"\n## Conversion ledger: the declared drops\n\n"
            f"A drop is declared on one of two grounds, and applies only to a value that reached no destination.\n\n"
            f"**(a) The path map of this converter already said the value is not carried: "
            f"{sum(n for _, n in drops_by_map):,} values.**\n\n| reason | values |\n|---|---:|\n" +
            "".join(f"| {r} | {n:,} |\n" for r, n in drops_by_map) +
            f"\n**(b) A class the author decided for the IFA corpus on 2026-11-13: "
            f"{sum(n for _, n in drops_by_ifa):,} values.**\n\n| reason | values |\n|---|---:|\n" +
            "".join(f"| {r} | {n:,} |\n" for r, n in drops_by_ifa))
    f.write(f"\n## Conversion ledger: the unaccounted values, by class\n\n"
            f"{LT['unaccounted']:,} values have no destination and no declared reason. Nothing is decided for them: "
            f"the recommendation is a proposal, and to carry a value changes the bundle.\n\n"
            f"| values | what they are | of which | example | recommendation |\n|---:|---|---|---|---|\n" +
            "".join(f"| {c['count']:,} | {CLASSES.get(k, ('not classified', ''))[0]} | "
                    f"{', '.join(f'{s} x{n:,}' for s, n in c['of'].most_common()) or '-'} | "
                    f"`{c['example']}` = `{cell(c['value'], 60)}` | {CLASSES.get(k, ('', 'to be looked at'))[1]} |\n"
                    for k, c in sorted(unaccounted_classes.items(), key=lambda x: -x[1]["count"])))
    f.write("\n## Unaccounted source values, by path (conversion ledger)\n\n"
            "The same values by source path, nested controls and parts counted under one path as in the path map.\n\n"
            "| path | count | first value |\n|---|---:|---|\n" +
            "".join(f"| `{p}` | {u['count']:,} | `{u['first']}` |\n" for p, u in sorted(unaccounted_by_path.items())))
    f.write(f"\n## What the ledger cannot see\n\n"
            f"The ledger follows source values into the bundle. A value the converter writes on its own has no "
            f"entry in it. Seen from the bundle: {sum(own_values.values()):,} leaf values of the written objects are "
            f"neither a source value nor the result of a stated rule. The manifest's digests and paths are computed "
            f"from the written files and are not listed.\n\n"
            f"| place in an object | values | example | what stands behind it |\n|---|---:|---|---|\n" +
            "".join(f"| `{p}` | {n:,} | `{cell(own_example[p], 60)}` | {own_why(p)} |\n"
                    for p, n in sorted(own_values.items(), key=lambda x: (-x[1], x[0]))) +
            "\nA rule can also discard a part of a value, which no count of leaves shows: a markdown link in prose is "
            "replaced by its text, and its target is gone. What those targets were is counted under the conversion "
            "rules above.\n")
print(f"reqs: {len(req_ids)}  sets: {nset}  leaves: {j['totals']['leaf-values']:,}  "
      f"mapped: {j['totals']['mapped']:,}  UNMAPPED: {j['totals']['unmapped']}")
print(f"withdrawn: {len(withdrawn)}  successor-edges: {sum(len(v) for v in succ_replaces.values())}  "
      f"chains: {len(wd_chain)}  dangling: {len(wd_dangling)}")
print(f"#10 multi-declared params: {len(multi_decl)}  histogram: {dict(sorted(decl_hist.items()))}")
print(f"endpoint crosscheck: resolved {sum(hit.values())}  withdrawn-hits {dict(hit_wd)}  unknown {dict(miss)}")
if unmapped:
    for p, n in unmapped[:30]: print("  UNMAPPED", p, "x", n)
# The ledger's signals. An unaccounted value is work for the author and is reported; the run ends with 0. A claim of
# this script that the written file does not bear out, or a wiring check that fails, ends the run with 1.
for k, c in sorted(unaccounted_classes.items(), key=lambda x: -x[1]["count"]):
    print(f"  unaccounted {c['count']:>6,}  {k}  e.g. {c['example']}")
print(f"run: {time.time() - T_START:.1f} s in all")
if j["totals"]["leaf-values"] != LEDGER["leaf-values"]:        # the path map and the ledger read one source
    wiring.append(f"the path map counts {j['totals']['leaf-values']} source leaf values and the ledger {LEDGER['leaf-values']}")
# the file on disk is the record of this run, not one an earlier run left or one written from an earlier accounting
try:
    with open(os.path.join(OUTDIR, LEDGER_FILE), encoding="utf-8") as f: on_disk = json.load(f)
except (OSError, ValueError): on_disk = None
if on_disk != json.loads(json.dumps(ledger_by_path(LEDGER))): wiring.append(f"{LEDGER_FILE} on disk is not the record of this run")
if LEDGER["verification-failures"] or wiring:
    for x in LEDGER["verification-failures"][:20]: print("  LEDGER CHECK FAILED", json.dumps(x, ensure_ascii=False), file=sys.stderr)
    for x in wiring: print("  LEDGER WIRING", x, file=sys.stderr)
    raise SystemExit(f"convert_nist.py: {len(LEDGER['verification-failures'])} claim(s) of the conversion ledger do not hold "
                     f"on the written files, {len(wiring)} wiring check(s) failed")
