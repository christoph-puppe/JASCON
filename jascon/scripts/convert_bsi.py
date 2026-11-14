#!/usr/bin/env python3
"""BSI Grundschutz++ (OSCAL 1.1.3) -> Semantic Core bundle.
Gate item 1, authority 2. Nested pseudo-controls -> statements; part-level
grammar/objective/taxonomy props -> facet payloads keyed by statement id;
{{ insert: param }} -> {param:} tokens; the {{Label}} slots in the
sentence-template props are parameters (each stands where the prose inserts
one) and are checked, not reported; list values packed into one
comma-separated string are split and REPORTED, never laundered.
Pattern-based coverage: UNMAPPED target = 0.

Single-catalog mode since 2026-07-21: MS-TLS dropped from the corpus by
decision (its defects were reported to BSI; the twin-catalog finding - 11
shared ids, 10 silently diverged, census 2026-07-03 - stays on the record
in census and handbook). Parameters carry first-class label/default since
the D9 rev (backlog #1): the param-extras residue drains to alt-ids only.

    convert_bsi.py [--obligated-party URI] [--out DIR]

The catalogue carries no party on a control. The converter writes one party
of its own on every statement, `<namespace>/party/institution`;
--obligated-party writes the caller's party in its place, and the coverage
report says which of the two it was (backlog #74). Without arguments the
run reproduces the committed conversion byte for byte; the Validators
workflow holds it to that. --out writes the bundle, the two reports and the
ledger somewhere else, which is where a run with another party belongs.

Every string of the catalogue is followed into the written bundle by the
conversion ledger (oscal_conv_lib.Ledger, backlog #41). The run writes its
record, `bsi-conversion-ledger.json`, beside the two reports: one row per
source path and outcome. A claim of the ledger that does not hold on the
written files ends the run with a non-zero exit code, and so does a wiring
check that fails: a declared drop that reaches a path the path map does not
give up, or a ledger file on disk that is not the record of this run. A
source value that reaches no destination and has no declared reason is
counted and listed in the report; it does not fail the run, because whether
to carry or to drop it is a decision and not a defect of the run."""
import json, hashlib, os, re, sys, copy, collections
from oscal_conv_lib import Bundle, BUNDLE_NEWLINE, Ledger, ledger_by_path
from oscal_conv_lib import known_arguments, out_dir, obligated_party, obligated_party_line, obligated_party_record

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
ARGV = sys.argv[1:]
known_arguments(ARGV, ("--obligated-party", "--out"))
OUTDIR = out_dir(ARGV, os.path.join(ROOT, "converted_examples", "DE.BSI"))
OUT = os.path.join(OUTDIR, "bsi-core-bundle")
RMD = os.path.join(OUTDIR, "bsi-coverage-report.md")
RJS = os.path.join(OUTDIR, "bsi-coverage-report.json")
LJS = os.path.join(OUTDIR, "bsi-conversion-ledger.json")
NS = "https://ns.bsi.bund.de/gspp"
SOURCES = [("gspp", os.path.join(ROOT, "sources", "Grundschutz++-catalog.json"), NS)]
# Whom a statement binds is not a value of this source (backlog #74). One
# party is written for the run, minted under the namespace of the one
# catalogue the converter reads (single-catalog mode).
#
# Every statement of the catalogue names a subject before its modal verb
# ("Governance und Compliance MUSS ..."): 999 of 999 statements, 123
# distinct subjects, 365 of them the title of an enclosing group (measured
# on the pinned catalogue, backlog #77). The author decided on 2026-11-14
# that this subject is the practice the institution runs and not a party.
# So it is not written to `obligated-parties`, and the party stays the
# institution, or whoever the caller names.
PARTY_DEFAULT = f"{NS}/party/institution"
PARTY, PARTY_ORIGIN = obligated_party(ARGV, PARTY_DEFAULT)      # (party, "converter-default" | "caller")
PARTY_WHY = ("the catalogue carries no party on a control; `Institution` is the word its prose uses for "
             "the organisation that applies it. The subject a statement names before its modal verb is the "
             "practice that organisation runs, not a party (decided by the author on 2026-11-14)")
if any(ns != NS for _, _, ns in SOURCES):
    raise SystemExit("one obligated party is written for the run; a catalogue under another namespace needs its own")
CENSUS = {"version": "2026-07-03", "controls": 998, "packed-tags-gspp": 125,
          "statements": 1015}   # census r2 baseline for the delta report; packed
                                # tags recounted on that snapshot 2026-11-12
F_GRAM = "https://ns.jascon.net/stdlib/facet/statement-grammar@1"
F_SECO = "https://ns.jascon.net/stdlib/facet/security-objectives@1"
F_ACRIT = "https://ns.jascon.net/stdlib/facet/assessment-criteria@1"
F_TAX  = "https://ns.bsi.bund.de/facet/gspp-taxonomy@1"
F_NARR = "https://ns.bsi.bund.de/facet/gspp-narrative@1"
F_COMPAT = "https://ns.jascon.net/compat/oscal-1x@1"
MODAL = {"MUSS":"must","SOLLTE":"should","KANN":"may","DARF NICHT":"must-not",
         "SOLLTE NICHT":"should-not","DARF NUR":"may-only",
         "MÜSSEN":"must","SOLLTEN":"should","KÖNNEN":"may",
         "DÜRFEN NICHT":"must-not","DÜRFEN NUR":"may-only"}

def w(path,obj):
    p=os.path.join(OUT,path); os.makedirs(os.path.dirname(p),exist_ok=True)
    with open(p,"w",encoding="utf-8",newline=BUNDLE_NEWLINE) as f: json.dump(obj,f,indent=1,ensure_ascii=False); f.write("\n")
def sha_file(path): return "sha256:"+hashlib.sha256(open(os.path.join(OUT,path),"rb").read()).hexdigest()
def semantic_digest(o):
    o=copy.deepcopy(o); o.pop("annotations",None)
    return "sha256:"+hashlib.sha256(json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def slug(s):
    s = re.sub(r"[^a-z0-9]+","-",(s or "").lower()).strip("-")
    if len(s) <= 60: return s or "x"
    return s[:52].rstrip("-") + "-" + hashlib.sha256(s.encode()).hexdigest()[:7]   # P10 #39: no bare truncation
def split_list(v): return [x.strip() for x in v.split(",") if x.strip()]

# ---------- the conversion ledger (backlog #41) ----------
# Every string of the catalogue carries its origin from the moment it is
# loaded (oscal_conv_lib.Ledger). A value this script hands on unchanged is a
# copy, and the ledger finds it in the written file by itself. A value the
# script computes is stated where it is computed, with D(rule, function,
# inputs...): the rule has a name, and the function is kept, so that the
# ledger applies it to the source again and compares the result with what
# the file holds. The functions are therefore pure: they depend on their
# arguments and on the constant tables of this file, and on nothing else.
# Where a rule leaves a value as it is (a prose without a parameter token, a
# list prop with one term), the source value itself is handed on and counts
# as a copy. Nothing here changes what is written: the bundle is byte for
# byte the one the script wrote before the ledger existed.
led = Ledger()
D = led.derive

R_REQ = "requirement URI from the control id"
R_REQ_FILE = "file path of a Requirement from the control id"
R_LINK = "requirement URI from a link to a control (#id)"
R_RESOURCE = "a link that names a back-matter resource (#uuid): the address the resource gives"
R_SET = "taxonomy Set URI from the group id"
R_SET_FILE = "file path of a taxonomy Set from the group id"
R_BASE = "baseline Set URI from the sec_level of a top-level control"
R_BASE_TITLE = "baseline Set title from the sec_level of a top-level control"
R_BASE_FILE = "file path of a baseline Set from the sec_level of a top-level control"
R_ENUM = "a sec_level value as an entry of the enum of observed values in the pinned taxonomy schema"
R_PROSE = "statement prose with every {{ insert: param, x }} rewritten to {param:x}"
R_MODAL = "modality code from the modal verb (MODAL)"
R_TERM = "one term of a list packed into one string (split on commas, trimmed)"
R_THREAT = "threat URI from one term of the threats list (split on commas, trimmed, spaces to hyphens)"
R_EFFORT = "effort level as an integer"
R_FIELD = "field name from the prop name (FIELD)"
R_SCHEME = "alias scheme from the prop name (ALIAS_SCHEME)"
# two occurrences of one thing, of which the bundle keeps one (Ledger.same)
SAME_BASELINE = "the top-level controls of one sec_level name one baseline Set, written once"
SAME_ENUM = "a value observed more than once is listed once"

# The name of a prop decides the field its value is written to. As a table,
# so that the ledger follows a name to the key it selected.
FIELD = {"modal_verb":"modality","action_word":"action","result":"result",
         "result_specification":"result-specification",
         "target_object_categories":"target-object-categories",
         "documentation":"required-documentation","practice":"practice",
         "confidentiality":"confidentiality","integrity":"integrity",
         "availability":"availability","authenticity":"authenticity","threats":"threat-refs",
         "sec_level":"sec-level","effort_level":"effort","tags":"tags",
         "alt-identifier":"alt-identifier","label":"label"}
ALIAS_SCHEME = {"alt-identifier":"bsi-uuid"}

def props_of(node):
    """{name: prop} of an OSCAL props list. The prop itself is kept, not only
    its value, because its name is a source value too. A name that repeats
    keeps the last prop, as the dict of values did that stood here before;
    the ledger then lists the earlier name and value as unaccounted."""
    return {p["name"]:p for p in node.get("props",[]) or []}
def field(prop):
    """the key a prop's value is written under: the name itself where the
    field has the same name, else the name mapped by FIELD"""
    name=prop["name"]
    return name if FIELD[name]==name else D(R_FIELD,FIELD.__getitem__,name)
def scheme(prop): return D(R_SCHEME,ALIAS_SCHEME.__getitem__,prop["name"])
def same_value(v): return v
def nth_term(v,i): return split_list(v)[i]
def terms(v):
    """the terms of a list prop: the value itself where it is one term
    already, else one derived value for each term"""
    got=split_list(v)
    if got==[v]: return [v]
    return [D(R_TERM,nth_term,v,i) for i in range(len(got))]
def threat_uri(ns,v,i): return f"{ns}/threat/{split_list(v)[i].replace(' ','-')}"
def req_uri(ns,cid): return f"{ns}/req/{cid}"
def req_file(key,cid): return f"objects/{key}/req-{slug(cid)}.json"
def link_uri(ns,href): return f"{ns}/req/{href[1:]}"
def resource_address(href,uuid,address): return address if href[1:]==uuid else None
def set_uri(ns,gid): return f"{ns}/set/tax/{slug(gid)}"
def set_file(key,gid): return f"objects/{key}/set-tax-{slug(gid)}.json"
def baseline_uri(ns,lvl): return f"{ns}/set/baseline/{slug(lvl)}"
def baseline_title(lvl): return f"Baseline sec_level: {lvl}"
def baseline_file(key,lvl): return f"objects/{key}/set-baseline-{slug(lvl)}.json"

# Declared drops: source values that are not carried, each with its reason.
# A drop is declared in two cases only, and the report counts them apart.
#   "path-map"  the path map of this converter said, before the ledger
#               existed, that the path is not carried;
#   "ifa"       the value is of a class the author decided for the IFA
#               corpus on 2026-11-13 (backlog #41; register, "Amendments -
#               the value-level check of the converters"). Of those classes
#               this catalogue has four: the directory of parties and roles,
#               back-matter resources, type tags of structural elements, and
#               uuids that identify elements of the source document. It has
#               no revision history and no import link.
# A drop applies only to a value that reached no destination. Everything
# else without a destination stays unaccounted: whether to carry or to drop
# it is the author's decision, and no reason is made up here to close it.
IFA = "as decided for IFA on 2026-11-13: "
DROP_NS = ("the path map of this converter says so (absorbed): the namespace of a prop is the address of the CSV "
           "list its value is taken from; the pinned facet schema stands in its place, the address is not carried")
DROP_DIRECTORY = IFA + ("the source's directory of parties and roles: a party is a landmark URI and there is no "
                        "party object (register, backlog #16)")
DROP_RESOURCE = IFA + ("a back-matter resource that no link of a control names. A link that names a resource is "
                       "written with the address the resource gives, and that address then has a destination")
DROP_TYPE_TAG = IFA + ("a type tag of a structural element: the part named `statement` is an entry of "
                       "`statements[]`, and the bundle says by its shape what kind of thing it is")
DROP_UUID = IFA + ("the uuid of a source element, here of the catalogue document itself: JASCON objects get URIs "
                   "minted from ids and titles, the uuid is not carried")
# (case, pattern over the ledger's path or None for a drop declared value by
# value, reason). A drop is declared by path only where nothing on the path
# is ever carried; on a path with carried values a pattern would report a
# lost value as dropped on purpose, so there the drop names the value. The
# patterns are as narrow as the rows of the path map that give a path up: a
# uuid elsewhere in a later catalogue is not dropped by a rule written for
# this one, it is listed as unaccounted.
DROPS = [
 ("path-map", r"\.controls\[\](\.parts\[\])?\.props\[\]\.ns$", DROP_NS),
 ("ifa", r"\.catalog\.metadata\.(parties|roles)\[\]\.", DROP_DIRECTORY),
 ("ifa", None, DROP_RESOURCE),               # value by value: the resources no link names, after the conversion
 ("ifa", None, DROP_TYPE_TAG),               # value by value: the name of each statement part, in collect_stmt
 ("ifa", r"^[^.]+\.catalog\.uuid$", DROP_UUID),
]
for _,pattern,reason in DROPS:
    if pattern: led.drop(pattern,reason)

# ---------- inventory ----------
def inventory(node,prefix,counter):
    if isinstance(node,dict):
        for k,v in node.items(): inventory(v,f"{prefix}.{k}",counter)
    elif isinstance(node,list):
        for v in node: inventory(v,f"{prefix}[]",counter)
    else: counter[prefix]+=1

# ---------- destination rules (ordered regex patterns) ----------
# The path map says where a source PATH is meant to go; the ledger checks
# where each VALUE went. Four sentences of this map claimed a destination at
# which the ledger found no value (2026-11-14). Each now says what happens
# to the values of its path, and a path that is not carried has the level
# "-". The table holds, for the report, the paths (and a pattern over the
# ledger's paths, to count the values that are not in the bundle), what the
# sentence said and what the ledger found. One sentence of the per-prop
# table was incomplete and is completed: sec_level said "top: baseline Set
# membership; nested: taxonomy by-statement", and the value is by-statement
# at every depth.
PATH_MAP_CORRECTED = [
 ("catalog.uuid, catalog.metadata.*", r"\.catalog\.(uuid$|metadata\.)", "bundle manifest / L0 provenance",
  "only title, version and oscal-version reach the manifest"),
 ("catalog.back-matter.*", r"\.catalog\.back-matter\.",
  "resolution key for #uuid links -> external URL; resolved into relations / dropped-declared",
  "a resource that no link of a control names is not resolved, and nothing of it is carried"),
 ("links[] of a nested control", r"\.controls\[\]\.controls\[\]\.links\[\]\.", "relations[] {type=rel, ref}",
  "only the links of a top-level control are read; those of a nested control are lost"),
 ("parts[].id, parts[].name", r"\.parts\[\]\.(id|name)$", "statement/guidance part identity -> statement id / narrative key",
  "the id of a part is written nowhere; of the names, `guidance` becomes a key and `statement` does not"),
]
# Each row also names what the ledger may find for a value of its paths: it
# is carried (copied or transformed), dropped for a declared reason, or open
# (not carried and not decided, so unaccounted). After the account the two
# are held against each other, value by value: a sentence of this map cannot
# claim again what the ledger does not find, and a declared drop cannot
# reach a path this map does not give up (see "the path map held against
# the ledger" below).
CARRIED=("copied","transformed"); DROPPED=("intentionally-dropped",); OPEN=("unaccounted",)
C = r"(catalog(\.groups\[\])+\.controls\[\](\.controls\[\])*)"
TOP = r"^catalog(\.groups\[\])+\.controls\[\]"
RULES = [
 (r"^catalog\.metadata\.(title|version|oscal-version)$", "L1",
  "manifest provenance.sources[] (title, version, oscal-version); version -> `version` of every object; "
  "title -> title of the root Set", CARRIED),
 (r"^catalog\.uuid$", "-", "not carried: the uuid of the source document (declared drop in the ledger)", DROPPED),
 (r"^catalog\.metadata\.(parties|roles)\[\]\.", "-",
  "not carried: the source's directory of parties and roles (declared drop in the ledger)", DROPPED),
 (r"^catalog\.metadata\.", "-",
  "not carried and not decided: last-modified, props, links, remarks, responsible-parties (unaccounted in the ledger)", OPEN),
 (r"^catalog\.back-matter\.", "-",
  "a resource that a link of a control names by #uuid gives that link its address (relations[].ref); a resource "
  "no link of a control names is not carried (declared drop in the ledger)", CARRIED+DROPPED),
 (r"^catalog(\.groups\[\])+\.(id|title)$", "L1", "taxonomy Set id/title (per-catalog subtree)", CARRIED),
 (r"^catalog(\.groups\[\])+\.props\[\]\.remarks$", "L1", "gspp-narrative on the Set: layer/Praktik description", CARRIED),
 (r"^catalog(\.groups\[\])+\.props\[\]\.(name|value)$", "L1", "Set.label / Set.aliases (bsi-uuid)", CARRIED),
 (C+r"\.id$", "L1", "Requirement id (top) / statement id (nested)", CARRIED),
 (C+r"\.class$", "L1", "gspp-taxonomy: class (by-statement)", CARRIED),
 (C+r"\.title$", "L1", "Requirement title (top) / kept in taxonomy by-statement (nested)", CARRIED),
 (TOP+r"\.links\[\]\.(rel|href)$", "L1", "relations[] {type=rel, ref} (#control -> req URI; #uuid -> back-matter URL)", CARRIED),
 (C+r"\.links\[\]\.(rel|href)$", "-",
  "NOT CARRIED: the links of a nested control are not read (found by the ledger; unaccounted)", OPEN),
 (C+r"\.params\[\]\.id$", "L1", "statement parameter name (type string)", CARRIED),
 (C+r"\.params\[\]\.(label|values\[\])$", "L1", "parameter label / default - first-class since the D9 rev (backlog #1); residue drained", CARRIED),
 (C+r"\.params\[\]\.props\[\]\.(name|value)$", "L2", "compat oscal-1x: param-extras (param alt-identifier only)", CARRIED),
 (C+r"\.props\[\]\.ns$", "-", "not carried (absorbed): CSV-link namespaces replaced by pinned facet schemas (declared drop in the ledger)", DROPPED),
 (C+r"\.props\[\]\.(name|value)$", "L1", "dispatch by prop name (see per-prop table)", CARRIED),
 (C+r"\.parts\[\]\.id$", "-",
  "not carried and not decided: the id of a part (the control id with `_stm` or `_gdn`) is written nowhere; "
  "the statement id is `smt` or the id of the nested control (unaccounted in the ledger)", OPEN),
 (C+r"\.parts\[\]\.name$", "L1",
  "`guidance` -> the key of the gspp-narrative payload; `statement` -> not carried, the part is an entry of "
  "statements[] (declared drop in the ledger)", CARRIED+DROPPED),
 (C+r"\.parts\[\]\.prose$", "L1", "statements[].prose.de ({{insert}} -> {param:}) / gspp-narrative guidance", CARRIED),
 (C+r"\.parts\[\]\.props\[\]\.ns$", "-", "not carried (absorbed): CSV-link namespaces replaced by pinned facet schemas (declared drop in the ledger)", DROPPED),
 (C+r"\.parts\[\]\.props\[\]\.(name|value)$", "L1", "dispatch by part-prop name (grammar/objectives/criteria; packed lists reported)", CARRIED),
]
def destination(path):
    for pat,lvl,tgt,_ in RULES:
        if re.search(pat,path): return lvl,tgt
    return None,None
def may_become(path):
    """the outcomes the path map allows for a value of this path, or None for a path it does not know"""
    for pat,_,_,allowed in RULES:
        if re.search(pat,path): return allowed
    return None

PROP_DEST = {
 "alt-identifier": ("L1","Requirement.aliases (top) / taxonomy by-statement (nested)"),
 "label": ("L1","Requirement.label (top) / taxonomy by-statement label (nested)"),
 "sec_level": ("L1","gspp-taxonomy: sec-level (by-statement, at every depth); top: also the baseline Set the Requirement is listed in"),
 "effort_level": ("L1","gspp-taxonomy: effort (by-statement)"),
 "tags": ("L1","gspp-taxonomy: tags[] (comma-split; packed lists and inconsistencies reported)"),
 "confidentiality": ("L1","security-objectives (by-statement)"),
 "integrity": ("L1","security-objectives (by-statement)"),
 "availability": ("L1","security-objectives (by-statement)"),
 "authenticity": ("L1","security-objectives (by-statement)"),
 "threats": ("L1","security-objectives threat-refs[] (comma-split, packed lists reported; minted threat code URIs)"),
 "modal_verb": ("L1","statements[].modality (mapped code system)"),
 "action_word": ("L1","statement-grammar: action (by-statement)"),
 "result": ("L1","statement-grammar: result (by-statement)"),
 "result_specification": ("L1","statement-grammar: result-specification (by-statement)"),
 "target_object_categories": ("L1","statement-grammar: target-object-categories[] (by-statement; comma-split, packed lists reported)"),
 "documentation": ("L1","assessment-criteria: required-documentation[] (by-statement; comma-split, packed lists reported)"),
 "practice": ("L1","gspp-taxonomy: practice (by-statement)"),
}
assert set(FIELD)==set(PROP_DEST), "FIELD and the per-prop table name the same props"

INSERT_RE = re.compile(r"\{\{\s*insert:\s*param,\s*([^}\s]+)\s*\}\}")
# {{Label}} in a sentence-template prop (result, result_specification) marks
# the place of a parameter; the prose inserts the same parameter there
SLOT_RE = re.compile(r"\{\{(?!\s*insert:)(.*?)\}\}")
INSERT_PAT = r"\{\{\s*insert:\s*param,\s*[^}\s]+\s*\}\}"
# props whose value is a list of vocabulary terms; the source joins several
# terms with commas into ONE string instead of repeating the prop
LIST_PROPS = ("tags", "threats", "target_object_categories", "documentation")

stats = collections.defaultdict(collections.Counter)
packed=collections.defaultdict(list); list_props=collections.Counter()
slots=[]; unknown_modal=collections.Counter(); modality_count=collections.Counter()
objects={}; unresolved_links=0
params_unref=0; params_total=0; multi_value_params=[]
tag_values=collections.Counter(); sec_values=collections.Counter()

sec_enum={}        # sec_level value -> its entry in the enum of the pinned taxonomy schema
resources_named=set()   # uuids of the back-matter resources that a link of a control names
link_targets=[]    # (top-level control, rel, id the link names) of every link written as a Requirement URI
top_ids=set()      # ids of the top-level controls: the controls that become Requirements

def convert_prose(pr): return INSERT_RE.sub(lambda m:"{param:"+m.group(1)+"}", pr or "")
def statement_prose(pr):
    """the prose of a statement: the source value itself where it holds no
    parameter token, else the value R_PROSE makes of it"""
    return pr if convert_prose(pr)==pr else D(R_PROSE,convert_prose,pr)

def slot_at_insert(value, prose):
    """True if the prose reads like the template value with every {{Label}}
    slot replaced by a parameter insertion"""
    texts = SLOT_RE.split(value)[0::2]
    return re.search(INSERT_PAT.join(re.escape(t) for t in texts), prose or "") is not None

def part_props_of(c):
    smt=[p for p in c.get("parts",[]) or [] if p.get("name")=="statement"]
    gd=[p for p in c.get("parts",[]) or [] if p.get("name")=="guidance"]
    return (smt[0] if smt else {}), (gd[0] if gd else None)

def collect_stmt(prefix_ns, c, sid, is_child, req):
    """fills one statement + facet by-statement payloads from control c"""
    smt, guid = part_props_of(c)
    prose = statement_prose(smt.get("prose",""))
    pp = props_of(smt)
    # the name of the statement part selects it and is written nowhere
    if "name" in smt: led.drop_value(smt["name"], DROP_TYPE_TAG)
    # parameter slots in ALL part-prop values: each {{Label}} must stand where
    # the prose inserts a parameter; the label normally repeats the parameter's
    labels={pm.get("label") for pm in c.get("params",[]) or []}
    for part in c.get("parts",[]) or []:
        for p in part.get("props",[]) or []:
            v=p.get("value") or ""
            found=SLOT_RE.findall(v)
            if not found: continue
            at_insert=slot_at_insert(v, smt.get("prose",""))
            for label in found:
                slots.append({"control":c["id"],"prop":p["name"],"slot":label,
                              "at-insert":at_insert,"label-of-a-parameter":label in labels})
    # list values: one prop per term is the OSCAL form; count the packed ones
    for p in (smt.get("props",[]) or []) + (c.get("props",[]) or []):
        if p["name"] in LIST_PROPS:
            list_props[p["name"]]+=1
            if len(split_list(p["value"]))>1:
                packed[p["name"]].append({"control":c["id"],"value":p["value"]})
    # a verb outside MODAL is counted and not stated as a rule: `unspecified`
    # does not carry it, and the ledger lists the verb as unaccounted
    mv = pp["modal_verb"]["value"] if "modal_verb" in pp else None
    if mv is None: mod="unspecified"
    elif mv in MODAL: mod=D(R_MODAL,MODAL.__getitem__,mv)
    else: mod="unspecified"; unknown_modal[mv]+=1
    modality_count[mod]+=1
    st={"id":sid,(field(pp["modal_verb"]) if "modal_verb" in pp else "modality"):mod,
        "obligated-parties":[PARTY],
        "prose":{"de":prose}}
    # params: label/default first-class (D9 rev, backlog #1); attach to the
    # statement of the control that declares them; unreferenced tokens counted
    global params_unref, params_total, multi_value_params
    for pm in c.get("params",[]) or []:
        pid=pm["id"]
        prm={"name":pid,"type":"string"}
        if pm.get("label"): prm["label"]=pm["label"]
        vals=pm.get("values") or []
        if vals:
            prm["default"]=vals[0]
            if len(vals)>1: multi_value_params.append((c["id"],pid,len(vals)))
        st.setdefault("parameters",[]).append(prm)
        params_total+=1
        if "{param:"+pid+"}" not in prose:
            params_unref+=1
        extras={}
        for xp in pm.get("props",[]) or []:
            if xp["name"]=="alt-identifier": extras[field(xp)]=xp["value"]
        if extras:
            req.setdefault("_compat_params",{})[pid]=extras
    # facets by-statement. Every key that a prop selects is field(prop): the
    # prop's own name, or the name FIELD maps it to.
    def by(fname): return req["facets"].setdefault(fname,{}).setdefault("by-statement",{}).setdefault(sid,{})
    g=by(F_GRAM)
    for src in ("action_word","result","result_specification"):
        if src in pp: g[field(pp[src])]=pp[src]["value"]
    if "target_object_categories" in pp:
        g[field(pp["target_object_categories"])]=terms(pp["target_object_categories"]["value"])
    if "documentation" in pp: by(F_ACRIT)[field(pp["documentation"])]=terms(pp["documentation"]["value"])
    cp=props_of(c)
    so={}
    for k in ("confidentiality","integrity","availability","authenticity"):
        if k in cp: so[field(cp[k])]=cp[k]["value"]
    if "threats" in cp:
        tv=cp["threats"]["value"]
        so[field(cp["threats"])]=[D(R_THREAT,threat_uri,prefix_ns,tv,i) for i in range(len(split_list(tv)))]
    if so: by(F_SECO).update(so)
    tx=by(F_TAX); tx["class"]=c.get("class")
    if "sec_level" in cp:
        lv=cp["sec_level"]["value"]
        tx[field(cp["sec_level"])]=lv; sec_values[lv]+=1
        # the pinned schema lists every observed value once: the first
        # occurrence stands in the enum, every later one is linked to it
        seen=D(R_ENUM,same_value,lv)
        if lv in sec_enum: led.same(seen,sec_enum[lv],SAME_ENUM)
        else: sec_enum[lv]=seen
    if "effort_level" in cp: tx[field(cp["effort_level"])]=D(R_EFFORT,int,cp["effort_level"]["value"])
    if "tags" in cp:
        tl=terms(cp["tags"]["value"]); tx[field(cp["tags"])]=tl
        for t in tl: tag_values[t]+=1
    if "practice" in pp: tx[field(pp["practice"])]=pp["practice"]["value"]
    if is_child:
        tx["title"]=c.get("title")
        if "alt-identifier" in cp: tx[field(cp["alt-identifier"])]=cp["alt-identifier"]["value"]
        if "label" in cp: tx[field(cp["label"])]=cp["label"]["value"]
    if guid and guid.get("prose"):
        by(F_NARR)[guid["name"]]={"de":guid["prose"]}      # the part's name is the key: `guidance`
    for k in pp: stats["part-props"][k]+=1
    for k in cp: stats["ctrl-props"][k]+=1
    return st

def mint_requirement(prefix_ns, c, version, bm_map):
    rid=D(R_REQ,req_uri,prefix_ns,c["id"])
    cp=props_of(c)
    req={"id":rid,"version":version,
         (field(cp["label"]) if "label" in cp else "label"):(cp["label"]["value"] if "label" in cp else c["id"]),
         "lifecycle":"active","title":c["title"],
         "statements":[],"facets":{}}
    if "alt-identifier" in cp:
        req["aliases"]=[{"scheme":scheme(cp["alt-identifier"]),"value":cp["alt-identifier"]["value"]}]
    req["statements"].append(collect_stmt(prefix_ns,c,"smt",False,req))
    def descend(node):
        for ch in node.get("controls",[]) or []:
            req["statements"].append(collect_stmt(prefix_ns,ch,ch["id"],True,req))
            descend(ch)
    descend(c)
    # Only the links of the top-level control are read. Those of a nested
    # control reach no object: the ledger lists them as unaccounted, and the
    # report counts them as lost. Carrying them changes the bundle.
    rels=[]
    for l in c.get("links",[]) or []:
        href=l.get("href","")
        if href.startswith("#") and href[1:] in bm_map:
            uuid,address=bm_map[href[1:]]
            rels.append({"type":l.get("rel","related"),"ref":D(R_RESOURCE,resource_address,href,uuid,address)})
            resources_named.add(uuid)
        elif href.startswith("#"):
            rels.append({"type":l.get("rel","related"),"ref":D(R_LINK,link_uri,prefix_ns,href)})
            link_targets.append((c["id"],l.get("rel","related"),href[1:]))
        else:
            rels.append({"type":l.get("rel","related"),"ref":href})
    if rels: req["relations"]=rels
    return rid,req

# rebuild output (lib Bundle: Windows-safe in-place writes)
bundle=Bundle(OUT,lang="de")
paths=collections.Counter(); catalogs_meta=[]
baseline={}        # (key, sec_level) -> {"set": its id, title and file, "refs": the Requirements listed in it}
seq={"n":0}
def nseq(): seq["n"]+=10; return seq["n"]

all_ids={}
for key,fn,ns in SOURCES:
    # the whole file under the source's key: a pointer of the ledger reads `gspp#/catalog/...`
    cat=led.source(key,json.load(open(fn,encoding="utf-8")))["catalog"]
    inventory(cat,"catalog",paths)
    version=cat["metadata"]["version"]
    catalogs_meta.append((key,cat["metadata"]["title"],version,cat["metadata"]["oscal-version"]))
    # resource uuid -> (the uuid as the source holds it, the address the resource gives)
    bm_map={r["uuid"]:(r["uuid"],r.get("rlinks",[{}])[0].get("href") or r.get("title",""))
            for r in cat.get("back-matter",{}).get("resources",[]) or []}
    ids=set()
    def conv_group(g,path_ids):
        entries=[]
        for sub in g.get("groups",[]) or []:
            u=conv_group(sub,path_ids+[slug(sub.get("id") or sub.get("title"))])
            if u: entries.append({"ref":u,"sequence":nseq()})
        def all_desc_ids(node):
            ids.add(node["id"])
            for ch in node.get("controls",[]) or []: all_desc_ids(ch)
        for c in g.get("controls",[]) or []:
            all_desc_ids(c); top_ids.add(c["id"])
            rid,req=mint_requirement(ns,c,version,bm_map)
            # param-extras -> compat facet on the requirement
            extras=req.pop("_compat_params",None)
            if extras: req["facets"][F_COMPAT]={"param-extras":extras}
            if not req["facets"]: req.pop("facets")
            objects[D(R_REQ_FILE,req_file,key,c["id"])]=req
            cp=props_of(c)
            if "sec_level" in cp:
                # Every top-level control names the baseline Set of its
                # sec_level. The Set is written once, from the first control
                # that names it; every later one is linked to it, and the
                # ledger checks that its own value gives the same Set.
                lv=cp["sec_level"]["value"]
                mine={"id":D(R_BASE,baseline_uri,ns,lv),"title":D(R_BASE_TITLE,baseline_title,lv),
                      "file":D(R_BASE_FILE,baseline_file,key,lv)}
                b=baseline.setdefault((key,lv),{"set":mine,"refs":[]})
                if b["set"] is not mine: led.same(mine,b["set"],SAME_BASELINE)
                b["refs"].append(rid)
            entries.append({"ref":rid,"sequence":nseq()})
        if not entries: return None
        # a group without an id is named by the titles on its path; that name
        # is not stated as a rule (no group of the catalogue is without an id)
        gid=g.get("id")
        sid=gid or "-".join(path_ids)
        u=D(R_SET,set_uri,ns,gid) if gid else set_uri(ns,sid)
        sobj={"id":u,"version":version,"lifecycle":"active",
              "title":g.get("title",sid),"members":entries}
        for gp in g.get("props",[]) or []:
            if gp["name"]=="label":
                sobj[field(gp)]=gp["value"]
                if gp.get("remarks"):
                    sobj.setdefault("facets",{}).setdefault(F_NARR,{})["description"]={"de":gp["remarks"]}
            elif gp["name"]=="alt-identifier":
                sobj.setdefault("aliases",[]).append({"scheme":scheme(gp),"value":gp["value"]})
        objects[D(R_SET_FILE,set_file,key,gid) if gid else set_file(key,sid)]=sobj
        return u
    top=[]
    for g in cat.get("groups",[]) or []:
        u=conv_group(g,[slug(g.get("id") or g.get("title"))])
        if u: top.append({"ref":u,"sequence":nseq()})
    objects[f"objects/{key}/set-tax-root.json"]={
        "id":f"{ns}/set/tax/root","version":version,"lifecycle":"active",
        "title":cat["metadata"]["title"],"members":top}
    all_ids[key]=ids
    # a back-matter resource that no link of a control named is dropped, value by value
    for r in cat.get("back-matter",{}).get("resources",[]) or []:
        if r.get("uuid") not in resources_named: led.drop_value(r,DROP_RESOURCE)

for (key,lvl),b in sorted(baseline.items()):
    objects[b["set"]["file"]]={
        "id":b["set"]["id"],"version":[v for k2,_,v,_ in catalogs_meta if k2==key][0],
        "lifecycle":"active","title":b["set"]["title"],
        "members":[{"ref":r,"sequence":(i+1)*10} for i,r in enumerate(b["refs"])]}

# facet schema stubs (enums generated from observed values); declaration
# promotions per D10 rev 2 (backlog #8): security-objectives -> [selection]
bundle.stub("gspp-taxonomy-1.0.0-stub.json","https://ns.bsi.bund.de/facet/gspp-taxonomy",["selection"],
     {"by-statement":{"type":"object"},"observed-sec-levels":{"enum":sorted(sec_enum.values())}})
bundle.pin_stdlib("statement-grammar-1.0.0.json")   # 26: stdlib pins are VERBATIM
bundle.pin_stdlib("security-objectives-1.0.0.json")
bundle.pin_stdlib("assessment-criteria-1.0.0.json")
bundle.stub("gspp-narrative-1.0.0-stub.json","https://ns.bsi.bund.de/facet/gspp-narrative",[],
     {"by-statement":{"type":"object"},"description":{"type":"object"}})
bundle.stub("oscal-1x-compat-1.0.0-stub.json","https://ns.jascon.net/compat/oscal-1x",[],
     {"param-extras":{"type":"object"}})

for rel,o in objects.items(): bundle.add(rel,o)
manifest=bundle.write({"sources":[{"key":k,"title":t,"version":v,"oscal-version":o}
               for k,t,v,o in catalogs_meta],
               "converter":"convert_bsi.py v0.2 (single-catalog: MS-TLS dropped by decision 2026-07-21)"})

# ---------- the ledger's account ----------
# Every file of the bundle is read back and every claim is checked against
# it: the objects, the pinned schemas (the taxonomy stub lists the observed
# sec_level values) and the manifest. ACCOUNT has one entry per source value
# and lasts as long as the run. The record that is written and committed has
# one row per source path and outcome (ledger_by_path).
#
# ledger_by_path collapses the array positions of a destination pointer. In
# this bundle a payload is also keyed by ids of the source: `by-statement`
# by the id of a nested control, `param-extras` by the id of a parameter.
# Left as they are, each of them is a destination of its own, and the record
# lists the nested controls one by one. They are collapsed like an array
# position, to `{statement}` and `{param}`; `smt`, the id this script gives
# the statement of a top-level control, is no id of the source and stays.
def keyed_by_source_ids(account):
    def collapsed(pointer):
        pointer=re.sub(r"/by-statement/(?!smt(/|$))[^/]+","/by-statement/{statement}",pointer)
        return re.sub(r"/param-extras/[^/]+","/param-extras/{param}",pointer)
    return {**account,"entries":[{**e,"destinations":[{**d,"pointer":collapsed(d["pointer"])} for d in e["destinations"]]}
                                 if "destinations" in e else e for e in account["entries"]]}
ACCOUNT=led.account(OUT,{**bundle.objects,**bundle.schemas,"content-manifest.json":manifest})
LEDGER=ledger_by_path(keyed_by_source_ids(ACCOUNT))
with open(LJS,"w",encoding="utf-8") as f:
    json.dump(LEDGER,f,indent=1,ensure_ascii=False); f.write("\n")
LT=LEDGER["totals"]; LFAIL=LEDGER["verification-failures"]
FILES_READ=len(bundle.objects)+len(bundle.schemas)+1

# rule -> the source values it was applied to; reason -> the values dropped for it
RULE_NAMES=[R_REQ,R_REQ_FILE,R_LINK,R_RESOURCE,R_SET,R_SET_FILE,R_BASE,R_BASE_TITLE,R_BASE_FILE,R_ENUM,
            R_PROSE,R_MODAL,R_TERM,R_THREAT,R_EFFORT,R_FIELD,R_SCHEME]
rule_use=collections.Counter(); drop_use=collections.Counter()
for e in ACCOUNT["entries"]:
    for r in {d["rule"] for d in e.get("destinations",[]) if "rule" in d}: rule_use[r]+=1
    if e["outcome"]=="intentionally-dropped": drop_use[e["reason"]]+=1
# Wiring checks. The ledger checks every claim of a destination. It cannot
# check a declaration of this script that is too wide, or a record that is
# not this run's. Each check answers a defect that was put into a copy of
# this script on purpose and ran through with exit code 0 before the check
# existed. A check that fails ends the run with a non-zero exit code, after
# the reports are written.
wiring=[]
if not set(rule_use)<=set(RULE_NAMES): wiring.append("a rule is applied that the report does not list")
if not set(drop_use)<={r for _,_,r in DROPS}: wiring.append("a value is dropped for a reason that DROPS does not hold")
# Among the values that reached the bundle are names: the name of a prop (or
# of the guidance part) holds no content of its own, it selects the field
# the value is written to. Such a name is in the bundle as a key, or as the
# alias scheme. The report counts them apart from the values.
names_as_key=sum(1 for e in ACCOUNT["entries"] if e["outcome"]=="copied"
                 and all(d.get("as")=="key" for d in e["destinations"] if "rule" not in d))
names_by_rule=sum(1 for e in ACCOUNT["entries"] if e["outcome"]=="transformed"
                  and {d["rule"] for d in e["destinations"]}<={R_FIELD,R_SCHEME})
DROP_CASE={"path-map":"the path map of this converter already said that the path is not carried",
           "ifa":"a class the author decided for the IFA corpus on 2026-11-13"}
drops={case:[(reason,drop_use[reason]) for c2,_,reason in DROPS if c2==case and drop_use[reason]] for case in DROP_CASE}

# The path map held against the ledger. Every row of the map names what may
# become of the values of its paths (CARRIED, DROPPED, OPEN). A value whose
# outcome its row does not allow is a disagreement between what this script
# declares and what it does. Two kinds:
#   - dropped where the map allows no drop: a drop rule reaches further than
#     the map gives up. That is a defect of this script, whatever the source
#     holds: a wiring check, and the run ends with a non-zero exit code.
#   - unaccounted where the map says carried or dropped, or carried where it
#     says not carried: the map claims what the ledger does not find. That
#     is reported and counted, and the run goes on like every run with
#     unaccounted values: a later catalogue may bring a prop this script
#     does not read, and that is the source's news, not a defect of the run.
disagree=[]       # (ledger path, outcome, values, first value, what the map allows)
for row in LEDGER["paths"]:
    allowed=may_become(row["path"].split(".",1)[1])
    if allowed is not None and row["outcome"] not in allowed:
        disagree.append((row["path"],row["outcome"],row["count"],row["example"],allowed))
for p,o,n,x,a in disagree:
    if o=="intentionally-dropped":
        wiring.append(f"{n:,} value(s) of {p} are dropped by declaration, and the path map does not give that path up "
                      f"(first {x}): a drop reaches further than the map says")

# the sentences of the path map that were corrected, each with the values of
# its paths that are not in the bundle (dropped or unaccounted)
corrected=[(p,said,found,sum(r["count"] for r in LEDGER["paths"]
                             if re.search(rx,r["path"]) and r["outcome"] in DROPPED+OPEN))
           for p,rx,said,found in PATH_MAP_CORRECTED]

def source_at(pointer):
    """the source value a pointer of the ledger names (`gspp#/catalog/groups/0/id`)"""
    tag,_,ptr=pointer.partition("#")
    node=led.docs[tag]
    for x in ptr.split("/")[1:]:
        x=x.replace("~1","/").replace("~0","~")
        node=node[int(x)] if isinstance(node,list) else node[x]
    return node

# Lost: the links of nested controls. Counted from the ledger's own list of
# unaccounted values, not from the code that skips them.
lost=[u for u in ACCOUNT["unaccounted-paths"] if re.search(r"\.controls\[\]\.controls\[\]\.links\[\]\.(href|rel)$",u["path"])]
lost_link_values=sum(u["count"] for u in lost)
lost_links=[p for u in lost if u["path"].endswith(".href") for p in u["pointers"]]
lost_link_controls=sorted({p.rsplit("/links/",1)[0] for p in lost_links})
# A link to a control is written as the URI of a Requirement. A nested control
# is a statement of its top-level control's Requirement and no Requirement
# itself, so such a URI names no object of the bundle. The ledger checks that
# the rule was applied; it does not check that the URI resolves.
all_control_ids=set().union(*all_ids.values())
links_to_nested=[t for t in link_targets if t[2] in all_control_ids and t[2] not in top_ids]
links_to_nothing=[t for t in link_targets if t[2] not in all_control_ids]

def no_source(node,where,count):
    """counts the leaf values of a written file behind which no source value
    stands, by their place (array positions and keys taken from the source
    collapsed)"""
    if isinstance(node,dict):
        for k,v in node.items():
            no_source(v,where+"/"+("*" if hasattr(k,"_origins") else k.replace("~","~0").replace("/","~1")),count)
    elif isinstance(node,list):
        for v in node: no_source(v,where+"/[]",count)
    else:
        count["leaf values"]+=1
        if not hasattr(node,"_origins"): count[where]+=1
written={"objects":collections.Counter(),"schemas":collections.Counter(),"manifest":collections.Counter()}
for o in bundle.objects.values(): no_source(o,"",written["objects"])
for o in bundle.schemas.values(): no_source(o,"",written["schemas"])
no_source(manifest,"",written["manifest"])
def plain(count): return {k:v for k,v in sorted(count.items()) if k!="leaf values"}

# ---------- coverage ----------
rows=[]; unmapped=[]
for p,n in sorted(paths.items()):
    lvl,tgt=destination(p)
    (rows if lvl else unmapped).append((p,n,lvl,tgt) if lvl else (p,n))
total=sum(paths.values()); mapped=sum(n for _,n,_,_ in rows)
reqs=sum(1 for r in objects.values() if "/req/" in r["id"])
sets=sum(1 for r in objects.values() if "/set/" in r["id"])
nstmt=sum(len(r.get("statements",[])) for r in objects.values() if "statements" in r)

j={"sources":[{"key":k,"title":t,"version":v} for k,t,v,_ in catalogs_meta],
   "totals":{"leaf-values":total,"mapped":mapped,"unmapped":total-mapped,
             "coverage-pct":round(100*mapped/total,3)},
   "objects":{"requirements":reqs,"statements":nstmt,"sets":sets,"total":len(objects)},
   "modality":dict(modality_count),"unknown-modal-verbs":dict(unknown_modal),
   "obligated-party":obligated_party_record(PARTY,PARTY_ORIGIN,PARTY_DEFAULT),
   "packed-list-values":{n:{"props":list_props[n],"packed":len(packed[n]),"values":packed[n]}
                         for n in LIST_PROPS},
   "parameter-slots":{"slots":len(slots),
                      "at-insert":sum(s["at-insert"] for s in slots),
                      "label-of-a-parameter":sum(s["label-of-a-parameter"] for s in slots),
                      "other-wording":[s for s in slots if not s["label-of-a-parameter"]],
                      "not-at-insert":[s for s in slots if not s["at-insert"]]},
   "census-delta":{"census-version":CENSUS["version"],"this-version":catalogs_meta[0][2],
                   "controls":{"census":CENSUS["controls"],"now":len(all_ids["gspp"])},
                   "packed-tags":{"census-gspp":CENSUS["packed-tags-gspp"],"now":len(packed["tags"])}},
   "parameters":{"total":params_total,"unreferenced-in-prose":params_unref,
                 "multi-value":multi_value_params},
   "mstls":"dropped by decision 2026-07-21 (reported to BSI; twin-catalog finding stays in census/handbook)",
   "baselines":{f"{k}:{l}":len(v["refs"]) for (k,l),v in sorted(baseline.items())},
   "tag-value-inconsistencies":{t:c for t,c in tag_values.items()
        if t.replace(" ","-") in tag_values and " " in t},
   "ledger":{"file":os.path.basename(LJS),"leaf-values":LEDGER["leaf-values"],"totals":LT,
             "verification-failures":len(LFAIL),"files-read-back":FILES_READ,
             "names-that-select-a-field":{"copied-as-a-key-only":names_as_key,"transformed-to-a-field-name-or-scheme":names_by_rule},
             "rules":[{"rule":r,"source-values":rule_use[r]} for r in RULE_NAMES],
             "declared-drops":{case:{"case":DROP_CASE[case],"count":sum(n for _,n in drops[case]),
                                     "reasons":[{"reason":r,"count":n} for r,n in drops[case]]} for case in DROP_CASE},
             "path-map-corrected":[{"paths":p,"said":s,"found":f,"values-not-in-the-bundle":n} for p,s,f,n in corrected],
             "path-map-against-ledger":{"values-that-disagree":sum(d[2] for d in disagree),
                                        "rows":[{"path":p,"outcome":o,"count":n,"first":x,"path-map-allows":list(a)}
                                                for p,o,n,x,a in disagree]},
             "lost":{"links-of-nested-controls":{"links":len(lost_links),"controls":len(lost_link_controls),
                                                 "source-values":lost_link_values,
                                                 "first":lost_links[0] if lost_links else None}},
             "links-to-a-nested-control":{"links":len(links_to_nested),"of":len(link_targets),
                                          "first":list(links_to_nested[0]) if links_to_nested else None,
                                          "links-to-no-control":len(links_to_nothing)},
             "written-without-a-source-value":{k:{"leaf-values":c["leaf values"],
                                                  "without-a-source-value":sum(plain(c).values()),
                                                  **({"by-place":plain(c)} if k!="schemas" else {})}
                                               for k,c in written.items()}},
   "unmapped-paths":[{"path":p,"count":n} for p,n in unmapped],
   "path-map":[{"path":p,"count":n,"level":l,"destination":t} for p,n,l,t in rows]}
json.dump(j,open(RJS,"w",encoding="utf-8"),ensure_ascii=False,indent=1)

md=[f"# BSI Grundschutz++ -> Semantic Core: Coverage Report (computed)\n"]
md.append("Source: " + " · ".join(f"**{t}** v{v}" for _,t,v,_ in catalogs_meta)
          + " — single-catalog mode: **MS-TLS dropped by decision 2026-07-21** "
          "(its defects were reported to BSI; the twin-catalog finding — 11 shared ids, "
          "10 silently diverged, census 2026-07-03 — stays on the record in census and handbook).\n")
md.append("## Totals\n")
md.append(f"- Source leaf values inventoried: **{total:,}**")
md.append(f"- Mapped: **{mapped:,}** -> **UNMAPPED: {total-mapped}** -> coverage **{j['totals']['coverage-pct']} %**")
md.append(f"- That is a count of source paths with a declared fate, not of values that arrived. Followed value by "
          f"value (conversion ledger, below): **{LT['copied']+LT['transformed']:,}** are in the bundle, "
          f"**{LT['intentionally-dropped']:,}** are dropped for a declared reason, **{LT['unaccounted']:,}** are unaccounted.")
md.append(f"- Emitted: **{reqs} Requirements** carrying **{nstmt} statements** "
          f"(all nested pseudo-controls flattened to clauses - nesting reaches depth 3), **{sets} Sets**, "
          f"manifest with both digests, {len(manifest['facet-schemas'])} pinned facet stubs.\n")
md.append("## Conversion rules (declared, counted)\n")
md.append(f"- **Modality** from `modal_verb` (code map incl. DARF NUR -> may-only): "
          + ", ".join(f"{k} x{v}" for k,v in sorted(modality_count.items(),key=lambda x:-x[1]))
          + (f"; unknown verbs: {dict(unknown_modal)}" if unknown_modal else "; no unknown verbs") + ".")
md.append(obligated_party_line(PARTY,PARTY_ORIGIN,PARTY_DEFAULT,PARTY_WHY))
md.append("- **Nested controls -> statements** of the parent; statement id = child control id "
          "(stable, citable); child-level props keyed `by-statement` in the facets.")
md.append(f"- **{{{{ insert: param, x }}}}** in prose -> `{{param:x}}` tokens; params typed `string` "
          f"with **first-class `label` + `default`** (D9 rev, backlog #1) - x{params_total} parameters, "
          f"the param-extras residue drains to alt-identifier uuids only. Params never referenced by a "
          f"`{{param:}}` token in their statement's prose: x{params_unref} (counted - source QA signal); "
          f"multi-value params x{len(multi_value_params)} (first value becomes default, all values kept in source).")
md.append("- **Payload free text language-tagged** per corpus language (`{de: ...}` on statement prose, "
          "guidance, Set descriptions) - this corpus was born tagged; harmonization rule (backlog #12) "
          "verified, not applied.")
md.append("- **Grammar** (action_word/result/result_specification/target_object_categories) -> "
          "`statement-grammar@1` by-statement; **documentation** -> `assessment-criteria@1` "
          "required-documentation; **C/I/A/Auth + threats** -> `security-objectives@1` "
          "(threat codes minted from 'G 0.x'); **sec_level/effort/tags/class/practice** -> "
          "`gspp-taxonomy@1`; **guidance parts** -> `gspp-narrative@1`.")
md.append(f"- **Baselines** from top-control `sec_level`: "
          + ", ".join(f"{k}:{l} ({len(v['refs'])})" for (k,l),v in sorted(baseline.items()))
          + ". Child-level sec_level stays informational by-statement "
          "(clause-level baselining = Tailoring concern, not Set membership).")
md.append("- **alt-identifier** -> aliases (scheme bsi-uuid) on Requirements; child alt-ids "
          "by-statement. CSV-link namespaces absorbed: pinned schemas replace them.\n")
md.append("## Findings (computed)\n")
npacked=sum(len(v) for v in packed.values())
md.append(f"- **List values packed into one string: {npacked}** - "
          + ", ".join(f"`{n}` {len(packed[n])} of {list_props[n]}" for n in LIST_PROPS)
          + ". Several vocabulary terms joined by commas in ONE prop value, where OSCAL repeats the "
          "prop once per value and JSON has arrays. The string is schema-valid, so no OSCAL validator "
          "sees the list, and none can check its terms against the vocabulary; every consumer has to "
          "know to split. The converter splits on `,` (rules above) and REPORTS the source form for the "
          "authors' queue (handbook 14.5). Full list in the JSON report; first three `tags` values:")
for d in packed["tags"][:3]:
    md.append(f"    - `{d['control']}`: \"{d['value']}\"")
ps=j["parameter-slots"]
md.append(f"- **Parameter slots in the sentence template: {ps['slots']}** `{{{{Label}}}}` in "
          f"result/result_specification values - parameters, not defects: {ps['at-insert']} stand exactly "
          f"where the statement prose inserts a parameter (`{{{{ insert: param, x }}}}`), "
          f"{ps['label-of-a-parameter']} repeat the label of a parameter declared on the same control"
          + (" (other wording: " + ", ".join(f"`{s['control']}` \"{s['slot']}\"" for s in ps["other-wording"]) + ")"
             if ps["other-wording"] else "")
          + ". Carried verbatim in `statement-grammar@1`."
          + (f" **Not at an insertion: {len(ps['not-at-insert'])}** - reported." if ps["not-at-insert"] else ""))
md.append(f"- **Census delta (source moved)**: catalog v{catalogs_meta[0][2][:10]} vs. census v{CENSUS['version']} - "
          f"controls {len(all_ids['gspp'])} (census {CENSUS['controls']}), packed `tags` values "
          f"{len(packed['tags'])} (census GS++-only {CENSUS['packed-tags-gspp']}). Deltas are the authors editing the "
          f"catalog between snapshots; every claim in this report re-verifies against the version named above.")
inc = j["tag-value-inconsistencies"]
if inc: md.append(f"- **Tag spelling drift** (space vs hyphen variants coexist): {inc} - "
                  "reported, not normalized.")
md.append(f"- **sec_level value space observed**: {dict(sec_values)} "
          "(note the bare 'erhöht' vs 'normal-SdT' asymmetry - vocabulary drift the "
          "pinned schema now freezes).\n")
LNAME=os.path.basename(LJS)
md.append("## Conversion ledger (measured per source value)\n")
md.append(f"- **Totals**: the path map says where each source path is meant to go. The ledger follows each of the "
          f"{LEDGER['leaf-values']:,} source leaf values into the written bundle and reads every claim back from "
          f"the {FILES_READ} files of the bundle. **{LT['copied']:,} copied** (the value stands, with its type, at "
          f"the destination named), **{LT['transformed']:,} transformed** (a named rule made the destination from "
          f"it; the rule was applied to the source again and compared), **{LT['intentionally-dropped']:,} "
          f"intentionally dropped** (a declared reason), **{LT['unaccounted']:,} unaccounted** (no destination and "
          f"no declared reason). Checks that failed: {len(LFAIL)}. A value is traced by what the converter did with "
          f"it; an equal value elsewhere in the bundle does not count. The record is `{LNAME}`: one row per source "
          f"path and outcome, with the number of values, the first of them, and where they went or why they were "
          f"dropped. A destination keyed by the id of a nested control or of a parameter reads `{{statement}}` or "
          f"`{{param}}` there.")
md.append(f"- **Names and values**: {names_as_key+names_by_rule:,} of the {LT['copied']+LT['transformed']:,} values "
          f"in the bundle are names. The name of a prop, or of the guidance part, holds no content of its own: it "
          f"selects the field its value is written to. {names_as_key:,} stand in the bundle as the key of that "
          f"field, unchanged, and nowhere as a value (counted as copied); {names_by_rule:,} are mapped to a field of "
          f"another name or to the alias scheme (counted as transformed). The other "
          f"{LT['copied']+LT['transformed']-names_as_key-names_by_rule:,} are ids, texts and codes.")
md.append(f"- **Declared drops: {LT['intentionally-dropped']:,}, of two kinds.** A drop is declared only where the "
          f"path map of this converter already said that the path is not carried, or where the value is of a class "
          f"the author decided for the IFA corpus on 2026-11-13. It applies only to a value that reached no "
          f"destination.")
for case,label in (("path-map","(a) the path map already said so"),("ifa","(b) a class decided for IFA on 2026-11-13")):
    md.append(f"    - {label}: **{sum(n for _,n in drops[case]):,}**")
    for reason,n in drops[case]: md.append(f"        - x{n:,}: {reason}")
md.append(f"- **Rules: {len(RULE_NAMES)} named, {sum(1 for r in RULE_NAMES if rule_use[r])} applied to this "
          f"catalogue.** Behind each, the number of source values it was applied to; a value can pass through more "
          f"than one. Where a rule leaves a value as it is, the value counts as copied: a prose without a parameter "
          f"token, a list prop with one term, a prop whose field has the prop's own name.")
for r in RULE_NAMES: md.append(f"    - x{rule_use[r]:,}: {r}")
if lost_links:
    first=lost_links[0]; ctl=source_at(first.rsplit("/links/",1)[0]); lk=source_at(first.rsplit("/",1)[0])
    md.append(f"- **Lost: the links of nested controls, {len(lost_links)} links on {len(lost_link_controls)} controls "
              f"({lost_link_values} source values).** The converter reads the links of a top-level control and not "
              f"those of a control nested in it; the path map said `relations[]` for a control at any depth. "
              f"First: `{first}` - `{ctl['id']}` {lk.get('rel')} `{lk.get('href')}`. Not repaired here: carrying "
              f"them changes the bundle.")
if links_to_nested:
    a,rel,b=links_to_nested[0]
    md.append(f"- **A link to a nested control names no object: {len(links_to_nested)} of the {len(link_targets)} "
              f"`relations[]` written.** A link to a control is written as the URI of a Requirement. A nested "
              f"control is a statement of the Requirement of its top-level control, so `.../req/` with its id is "
              f"the id of no object of the bundle. First: `{a}` {rel} `#{b}`. The ledger checks that the rule was "
              f"applied, not that the URI resolves. Not repaired here: it changes the bundle.")
if links_to_nothing:
    md.append(f"- **A link names a control the catalogue does not define: {len(links_to_nothing)}.** First: "
              f"`{links_to_nothing[0][0]}` {links_to_nothing[0][1]} `#{links_to_nothing[0][2]}`.")
md.append(f"- **Path map corrected: {len(corrected)} sentences claimed a destination at which the ledger found no "
          f"value, for {sum(n for _,_,_,n in corrected):,} values in all.**")
for p,s,f,n in corrected: md.append(f"    - `{p}` said \"{s}\"; found: {f}. Not in the bundle: x{n:,}.")
md.append(f"- **The path map held against the ledger: {sum(d[2] for d in disagree):,} values disagree.** Every row "
          f"of the path map names what may become of the values of its paths: carried, dropped for a declared "
          f"reason, or open (not carried and not decided). Each run compares that with the outcome the ledger "
          f"found for every value, so a sentence of the map cannot claim again what the ledger does not find. "
          f"A value dropped on a path the map does not give up ends the run with an error."
          + ("" if disagree else " No value has an outcome its row does not allow."))
for p,o,n,x,a in disagree:
    md.append(f"    - `{p}`: x{n:,} {o}, where the path map allows {' or '.join(a)}; first `{x}`")
wo=written["objects"]
party_from="the converter's default" if PARTY_ORIGIN=="converter-default" else "given by the caller"
WHAT={"/statements/[]/obligated-parties/[]":f"the obligated party `{PARTY}`, {party_from}",
      "/statements/[]/id":"the statement id `smt` of a top-level control",
      "/statements/[]/parameters/[]/type":"`string`, the type of every parameter",
      "/statements/[]/modality":"`unspecified`, where a statement has no modal verb the code map knows",
      "/lifecycle":"`active`","/members/[]/sequence":"the order of the members of a Set",
      "/id":"the id of the root Set, and of a Set whose group has no id"}
md.append(f"- **What the ledger cannot see**: it follows source values into the bundle, not the other way round. "
          f"{sum(plain(wo).values()):,} of the {wo['leaf values']:,} leaf values of the {len(bundle.objects)} objects "
          f"have no source value behind them. The converter writes them on its own and none has a row in the "
          f"ledger: " + "; ".join(f"`{k}` x{v:,}" + (f" ({WHAT[k]})" if k in WHAT else "") for k,v in plain(wo).items())
          + f". The manifest adds {sum(plain(written['manifest']).values()):,} values of its own (digests, the "
          f"paths and versions of the pinned schemas, the converter line), the pinned schemas "
          f"{sum(plain(written['schemas']).values()):,}. Two more limits. The ledger checks the URI of a baseline "
          f"Set against the sec_level of every control that names it; that the Requirement of that control is "
          f"listed in that Set it does not check. And it checks that a rule gives what the file holds, not that "
          f"the rule is the right one: a rule whose function is changed changes the bundle and no figure of the "
          f"ledger. That the bundle is byte for byte the committed one is held apart from it, by the Validators "
          f"workflow, which converts the pinned source again and compares.")
md.append(f"- **Unaccounted: {LT['unaccounted']:,}.** Listed by path at the end of this report. Each is either "
          f"carried, which changes the bundle, or dropped for a reason. Both are decisions of the author "
          f"(backlog #41), and neither is taken here.\n")
md.append("## Full path map\n| path | count | level | destination |\n|---|---:|---|---|")
for p,n,l,t in rows: md.append(f"| `{p}` | {n:,} | {l} | {t} |")
md.append("\n## Per-prop dispatch\n| prop | level | destination |\n|---|---|---|")
for k,(l,t) in PROP_DEST.items(): md.append(f"| `{k}` | {l} | {t} |")
md.append("\n## UNMAPPED (gate target: zero)\n")
if unmapped:
    md.append("| path | count |\n|---|---:|")
    for p,n in unmapped: md.append(f"| `{p}` | {n} |")
else: md.append("*(none)*")
md.append("\n## Unaccounted source values (conversion ledger)\n")
md.append(f"No destination and no declared reason. The first values of each path are in `{LNAME}` "
          f"(`unaccounted-paths`).\n")
if LEDGER["unaccounted-paths"]:
    md.append("| path | count | first value |\n|---|---:|---|")
    for u in LEDGER["unaccounted-paths"]: md.append(f"| `{u['path']}` | {u['count']:,} | `{u['pointers'][0]}` |")
else: md.append("*(none)*")
open(RMD,"w",encoding="utf-8").write("\n".join(md)+"\n")

print(f"requirements: {reqs} (statements: {nstmt})  sets: {sets}  objects: {len(objects)}")
print(f"leaf values: {total:,}  mapped: {mapped:,}  UNMAPPED: {total-mapped}")
print("modality:",dict(modality_count)," unknown:",dict(unknown_modal))
compat_n=sum(1 for o in objects.values() if "facets" in o and F_COMPAT in o.get("facets",{}))
print(f"params: {params_total} (label/default first-class; unreferenced-in-prose: {params_unref})  "
      f"L2 param-extras residue (alt-ids only): {compat_n} requirements")
print("packed list values: " + ", ".join(f"{n} {len(packed[n])}/{list_props[n]}" for n in LIST_PROPS)
      + f" (census gspp tags {CENSUS['packed-tags-gspp']})  controls: {len(all_ids['gspp'])} (census {CENSUS['controls']})")
print(f"parameter slots {{{{Label}}}}: {len(slots)}  at an insertion: {sum(s['at-insert'] for s in slots)}  "
      f"label of a parameter: {sum(s['label-of-a-parameter'] for s in slots)}")
if unmapped:
    print("UNMAPPED:"); [print("  ",p,"x",n) for p,n in unmapped[:30]]
print(f"ledger: {LEDGER['leaf-values']:,} source values - copied {LT['copied']:,}, transformed {LT['transformed']:,}, "
      f"intentionally dropped {LT['intentionally-dropped']:,}, unaccounted {LT['unaccounted']:,}; "
      f"failed checks {len(LFAIL)}")
if disagree:
    print(f"path map against ledger: {sum(d[2] for d in disagree):,} values have an outcome their row of the path map does not allow")
    for p,o,n,x,a in disagree[:30]: print(f"   {p} x{n} {o} (path map: {' or '.join(a)})")
# the path map and the ledger read one source
if total!=LEDGER["leaf-values"]:
    wiring.append(f"the path map counts {total:,} source leaf values and the ledger {LEDGER['leaf-values']:,}")
# the file on disk is the record of this run, not one an earlier run left there
try:
    with open(LJS,encoding="utf-8") as f: on_disk=json.load(f)
except (OSError,ValueError): on_disk=None
if on_disk!=json.loads(json.dumps(LEDGER)): wiring.append(f"{LNAME} on disk is not the record of this run")
# A claim that does not hold on the written files is a defect of the run:
# the bundle and the record disagree. So is a wiring check that fails.
# Unaccounted values are not: they wait for a decision, and the run says
# how many there are.
if LFAIL or wiring:
    for x in LFAIL[:20]: print("  LEDGER CHECK FAILED",json.dumps(x,ensure_ascii=False),file=sys.stderr)
    for x in wiring: print("  LEDGER WIRING",x,file=sys.stderr)
    raise SystemExit(f"convert_bsi.py: {len(LFAIL)} claim(s) of the conversion ledger do not hold on the written "
                     f"files, {len(wiring)} wiring check(s) failed")
