#!/usr/bin/env python3
"""BSI Grundschutz++ (OSCAL 1.1.3) -> Semantic Core bundle.
Gate item 1, authority 2. Every control is a Requirement of its own, at
every depth: BSI nests controls for grouping only (the author, 2026-11-14),
so a nested control is a full control with its own statement, parameters
and links, and a control that has nested controls gives a Set as well,
which stands for the grouping. part-level grammar/objective/taxonomy props
-> facet payloads keyed by statement id; {{ insert: param }} -> {param:}
tokens; the {{Label}} slots in the sentence-template props are parameters
(each stands where the prose inserts one) and are checked, not reported;
list values packed into one comma-separated string are split and REPORTED,
never laundered. Pattern-based coverage: UNMAPPED target = 0.

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

Content is never dropped (the author, 2026-11-14). Every value of the
catalogue is followed into the written bundle by the conversion ledger
(oscal_conv_lib.Ledger, backlog #41), and has one of two fates: it is
carried, or it is no content by a rule the ledger checks - a name that only
selects a field, a namespace, an id that is rebuilt exactly from another
value. What this mapping does not read (a prop it does not know, a part of
another name, a member OSCAL allows and this catalogue does not use) is
carried all the same, as the source holds it, in the compat facet. The run
writes its record, `bsi-conversion-ledger.json`, beside the two reports:
one row per source path and outcome. A claim of the ledger that does not
hold on the written files, a source value that is unaccounted, or a wiring
check that fails ends the run with a non-zero exit code, after the bundle,
the reports and the record are written, so that a failed run says why."""
import json, hashlib, os, re, sys, copy, collections, decimal
from oscal_conv_lib import Bundle, BUNDLE_NEWLINE, Ledger, ledger_by_path, ledger_gate
from oscal_conv_lib import document_author, document_day
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
# Every value of the catalogue carries its origin from the moment it is
# loaded (oscal_conv_lib.Ledger). A value this script hands on unchanged is a
# copy, and the ledger finds it in the written file by itself. A value the
# script computes is stated where it is computed, with D(rule, function,
# inputs...): the rule has a name, and the function is kept, so that the
# ledger applies it to the source again and compares the result with what
# the file holds. The functions are therefore pure: they depend on their
# arguments and on the constant tables of this file, and on nothing else.
# Where a rule leaves a value as it is (a prose without a parameter token, a
# list prop with one term), the source value itself is handed on and counts
# as a copy.
led = Ledger()
D = led.derive

R_REQ = "requirement URI from the control id"
R_REQ_FILE = "file path of a Requirement from the control id"
R_LINK = "requirement URI from a link to a control (#id)"
R_RESOURCE = "a link that names a back-matter resource (#uuid): the address the resource gives"
R_SET = "taxonomy Set URI from the group id"
R_SET_FILE = "file path of a taxonomy Set from the group id"
R_GROUPING = "URI of the Set that stands for a control with nested controls, from the control id"
R_GROUPING_FILE = "file path of the Set that stands for a control with nested controls, from the control id"
R_BASE = "baseline Set URI from the sec_level of a control"
R_BASE_TITLE = "baseline Set title from the sec_level of a control"
R_BASE_FILE = "file path of a baseline Set from the sec_level of a control"
R_ENUM = "a sec_level value as an entry of the enum of observed values in the pinned taxonomy schema"
R_PROSE = "statement prose with every {{ insert: param, x }} rewritten to {param:x}"
R_MODAL = "modality code from the modal verb (MODAL)"
R_TERM = "one term of a list packed into one string (split on commas, trimmed)"
R_THREAT = "threat URI from one term of the threats list (split on commas, trimmed, spaces to hyphens)"
R_EFFORT = "effort level as an integer"
R_FIELD = "field name from the prop name (FIELD)"
R_SCHEME = "alias scheme from the prop name (ALIAS_SCHEME)"
R_AUTHOR = ("author of the document: the one party its metadata names for it (as creator, else as prepared-by, "
            "else the one party it names), as a landmark URI from the party's name")
R_DATE = "date of the document: the day of its last-modified"
R_DECIMAL = "a number that is no integer, written as a decimal string (the kernel's spelling of a fraction, NUMBER-1)"
# two occurrences of one thing, of which the bundle keeps one (Ledger.same)
SAME_BASELINE = "the controls of one sec_level name one baseline Set, written once"
SAME_ENUM = "a value observed more than once is listed once"
# What is no content (the author, 2026-11-14): "a name that merely selects a
# field, a namespace, an id that is rebuilt exactly from another value. Each
# such class needs a stated rule that the ledger checks." These are the
# rules; a value they do not cover is carried.
N_STM_ID = "the id of a statement part is its control's id and `_stm`"
N_GDN_ID = "the id of a guidance part is its control's id and `_gdn`"
N_PART = "the name `statement` of a part selects the part whose prose and props become the statement"
N_NS = "the namespace of a prop is the one this mapping is written for (PROP_NS)"
NO_CONTENT = [("rebuilt-id",N_STM_ID),("rebuilt-id",N_GDN_ID),("selector",N_PART),("namespace",N_NS)]

# The name of a prop decides the field its value is written to. As a table,
# so that the ledger follows a name to the key it selected.
FIELD = {"modal_verb":"modality","action_word":"action","result":"result",
         "result_specification":"result-specification",
         "target_object_categories":"target-object-categories",
         "documentation":"required-documentation",
         "confidentiality":"confidentiality","integrity":"integrity",
         "availability":"availability","authenticity":"authenticity","threats":"threat-refs",
         "sec_level":"sec-level","effort_level":"effort","tags":"tags",
         "alt-identifier":"alt-identifier","label":"label"}
ALIAS_SCHEME = {"alt-identifier":"bsi-uuid"}
# The namespace each prop is read in. BSI gives a prop the address of the
# CSV list its values are taken from; this mapping is written for exactly
# these, and a prop of the same name in another namespace is another prop:
# it is not read, it is carried as the source holds it. `alt-identifier`
# and `label` are read without a namespace, as the source writes them.
CSV = "https://github.com/BSI-Bund/Stand-der-Technik-Bibliothek/tree/main/Dokumentation/namespaces/"
PROP_NS = {"modal_verb":CSV+"modal_verbs.csv","action_word":CSV+"action_words.csv","result":CSV+"result.csv",
           "result_specification":CSV+"result.csv","target_object_categories":CSV+"target_object_categories.csv",
           "documentation":CSV+"documentation_guidelines.csv",
           "confidentiality":CSV+"security_targets.csv","integrity":CSV+"security_targets.csv",
           "availability":CSV+"security_targets.csv","authenticity":CSV+"security_targets.csv",
           "threats":CSV+"basethreats.csv","sec_level":CSV+"security_level.csv",
           "effort_level":CSV+"effort_level.csv","tags":CSV+"tags.csv"}
# the props this mapping reads, by the element that carries them
CONTROL_PROPS = ("alt-identifier","label","sec_level","effort_level","tags",
                 "confidentiality","integrity","availability","authenticity","threats")
PART_PROPS = ("modal_verb","action_word","result","result_specification","target_object_categories","documentation")
GROUP_PROPS = ("label","alt-identifier")
PARAM_PROPS = ("alt-identifier",)
# the members of an element this mapping reads; any other member is carried as it is
CONTROL_MEMBERS = ("id","class","title","params","props","parts","links","controls")
GROUP_MEMBERS = ("id","title","props","groups","controls")
PARAM_MEMBERS = ("id","label","values","props")
CATALOG_MEMBERS = ("uuid","metadata","groups","controls","back-matter")
# the members of the compat facet, in the order they are written
COMPAT_MEMBERS = ("metadata","back-matter","catalog","param-extras","props","parts","links","control","group")

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
def party_uri(ns,name): return f"{ns}/party/{slug(name)}"
def day_of(timestamp): return timestamp[:10]
def decimal_string(x): return format(decimal.Decimal(repr(x)),"f")
def held(x):
    """A piece of the source as the compat facet carries it: as the source
    holds it, with one difference. A number that is no integer is written
    as a decimal string, because a kernel number is an integer (NUMBER-1,
    D3.9); the catalogue format has no such number, a later one may."""
    if isinstance(x,dict): return {k:held(v) for k,v in x.items()}
    if isinstance(x,list): return [held(v) for v in x]
    if isinstance(x,float): return D(R_DECIMAL,decimal_string,x)
    return x
def stm_id(cid): return cid+"_stm"
def gdn_id(cid): return cid+"_gdn"
def any_leaf(x):
    """does this structure hold a value of the source?"""
    if isinstance(x,dict): return any(any_leaf(v) for v in x.values())
    if isinstance(x,list): return any(any_leaf(v) for v in x)
    return hasattr(x,"_origins")

def read_props(node,names,unread,members=("name","ns","value")):
    """-> {name: prop} of the props of `node` this mapping reads: a name
    among `names`, in the namespace the mapping is written for (PROP_NS;
    none for a name that is not in it). For each the namespace is declared
    as no content. Every other prop goes to `unread` as the source holds
    it, and so does a prop that is read but holds a member besides
    `members`, and every earlier prop of a name that repeats: the last one
    is read, as before, and the earlier ones are not lost."""
    props=node.get("props",[]) or []
    last={}; rest=set()
    for i,p in enumerate(props):
        name=p.get("name")
        if name in names and p.get("ns")==PROP_NS.get(name):
            if name in last: rest.add(last[name])
            last[name]=i
            if set(p)-set(members): rest.add(i)
        else: rest.add(i)
    unread.extend(props[i] for i in sorted(rest))
    got={name:props[i] for name,i in last.items()}
    for p in got.values():
        if "ns" in p: led.namespace(p["ns"],N_NS,[PROP_NS[p["name"]]],p["name"])
    return got

# Declared drops. Two are left of those declared on 2026-11-14, and both
# stay declared: the author goes through every declared drop and decides
# which is content (brief of the rework, rule 4). No drop is added, and a
# value that is neither carried nor one of the three classes above is
# unaccounted and ends the run. `reading`: this script's reading under the
# author's rule, for the table in the report; the decision is the author's.
IFA = "as decided for IFA on 2026-11-13: "
DROP_RESOURCE = IFA + ("a back-matter resource that no link of a control names. A link that names a resource is "
                       "written with the address the resource gives, and that address then has a destination")
DROP_UUID = IFA + ("the uuid of a source element, here of the catalogue document itself: JASCON objects get URIs "
                   "minted from ids and titles, the uuid is not carried")
DROPS = [       # (pattern over the ledger's path or None for a drop declared value by value, reason, reading)
 (None, DROP_RESOURCE,
  "content: a reference of the catalogue to another document, with its title, address and digest. The root Set "
  "now carries the metadata link that names this resource by `#uuid`, and without the resource that link names nothing"),
 (r"^[^.]+\.catalog\.uuid$", DROP_UUID,
  "content: it identifies this document, and nothing in the bundle lets a reader rebuild it, so it is no id "
  "that is rebuilt exactly"),
]
for pattern,reason,_ in DROPS:
    if pattern: led.drop(pattern,reason)

# ---------- inventory ----------
def inventory(node,prefix,counter):
    if isinstance(node,dict):
        for k,v in node.items(): inventory(v,f"{prefix}.{k}",counter)
    elif isinstance(node,list):
        for v in node: inventory(v,f"{prefix}[]",counter)
    else: counter[prefix]+=1

# ---------- destination rules (ordered regex patterns) ----------
# The path map says where a source PATH goes; the ledger checks where each
# VALUE went. So that the two cannot drift apart, each row names, beside its
# sentence, what the ledger may find for a value of its paths:
#   - the outcome: it is carried (copied or transformed), it is no content by
#     a checked rule, or it is dropped for a declared reason;
#   - the places: a pattern over the destinations as the ledger's record
#     writes them (a JSON Pointer into the object, array positions as `[]`).
# After the account the two are held against each other, value by value. A
# value whose outcome its row does not allow, or that stands at a place its
# row does not name, ends the run: no sentence of this map says "not
# carried" of a value that is, and no value is anywhere the map does not say.
CARRIED=("copied","transformed"); NOT_CONTENT=("not-content",); DROPPED=("intentionally-dropped",)
def at(*places): return "^("+"|".join(places)+")$"
_F=r"/facets/[^/]*"
TAX_AT=_F+r"gspp-taxonomy@1/by-statement/smt"; GRAM_AT=_F+r"statement-grammar@1/by-statement/smt"
SECO_AT=_F+r"security-objectives@1/by-statement/smt"; ACRIT_AT=_F+r"assessment-criteria@1/by-statement/smt"
NARR_AT=_F+r"gspp-narrative@1"; COMPAT_AT=_F+r"oscal-1x@1"
SOURCES_AT=r"/provenance/sources/\[\]"                        # the manifest's entry for the source document
OBJECT_AT=(r"/id",r"/members/\[\]/ref",r"/objects/\[\]/id",r"/objects/\[\]/path")   # an object's id, where it is listed, its file
C = r"(catalog(\.groups\[\])*\.controls\[\](\.controls\[\])*)"   # a control: in a group at any depth, nested at any depth, or under the catalogue itself
RULES = [       # (source path, level, sentence, outcomes, places)
 (r"^catalog\.metadata\.title$", "L1", "title of the root Set; manifest provenance.sources[].title", CARRIED,
  at(r"/title/de",SOURCES_AT+r"/title")),
 (r"^catalog\.metadata\.version$", "L1",
  "`version` of every object, and of its entry in the manifest; manifest provenance.sources[].version", CARRIED,
  at(r"/version",r"/objects/\[\]/version",SOURCES_AT+r"/version")),
 (r"^catalog\.metadata\.oscal-version$", "L2",
  "root Set, compat oscal-1x `metadata`, as the source holds it; manifest provenance.sources[].oscal-version", CARRIED,
  at(COMPAT_AT+r"/metadata/oscal-version",SOURCES_AT+r"/oscal-version")),
 (r"^catalog\.metadata\.last-modified$", "L2",
  "root Set, compat oscal-1x `metadata`, as the source holds it; its day -> manifest provenance.sources[].date", CARRIED,
  at(COMPAT_AT+r"/metadata/last-modified",SOURCES_AT+r"/date")),
 (r"^catalog\.metadata\.parties\[\]\.name$", "L2",
  "root Set, compat oscal-1x `metadata`, as the source holds it; the name of the party the metadata names as "
  "author -> manifest provenance.sources[].author-ref (a landmark URI)", CARRIED,
  at(COMPAT_AT+r"/metadata/parties/\[\]/name",SOURCES_AT+r"/author-ref")),
 (r"^catalog\.metadata\.", "L2", "root Set, compat oscal-1x `metadata`: the member as the source holds it", CARRIED,
  at(COMPAT_AT+r"/metadata/.*")),
 (r"^catalog\.uuid$", "-", "not carried: a declared drop, listed in the report for the author's decision", DROPPED, None),
 (r"^catalog\.back-matter\.", "-",
  "a resource that a link of a control names by #uuid gives that link its address (relations[].ref) and is "
  "carried whole on the root Set (compat `back-matter`); a resource no link of a control names is not carried: a "
  "declared drop, listed in the report for the author's decision", CARRIED+DROPPED,
  at(r"/relations/\[\]/ref",COMPAT_AT+r"/back-matter/.*")),
 (r"^catalog(\.groups\[\])+\.id$", "L1", "taxonomy Set of the group: its id, its file, and where it is listed", CARRIED,
  at(*OBJECT_AT)),
 (r"^catalog(\.groups\[\])+\.title$", "L1", "taxonomy Set of the group: its title", CARRIED, at(r"/title/de")),
 (r"^catalog(\.groups\[\])+\.props\[\]\.remarks$", "L1", "gspp-narrative on the Set: layer/Praktik description", CARRIED,
  at(NARR_AT+r"/description/de",COMPAT_AT+r"/props/.*")),
 (r"^catalog(\.groups\[\])+\.props\[\]\.(name|value)$", "L1", "Set.label / Set.aliases (bsi-uuid)", CARRIED,
  at(r"/label",r"/aliases/\[\]/(scheme|value)",COMPAT_AT+r"/props/.*")),
 (C+r"\.id$", "L1",
  "Requirement id, label and file of the control, at every depth, and where it is listed; a control with "
  "nested controls: also the id and the file of the Set that groups it with them", CARRIED,
  at(*OBJECT_AT,r"/label")),
 (C+r"\.class$", "L1", "gspp-taxonomy: class (by-statement)", CARRIED, at(TAX_AT+r"/class")),
 (C+r"\.title$", "L1", "Requirement title; a control with nested controls: also the title of its grouping Set", CARRIED,
  at(r"/title/de")),
 (C+r"\.links\[\]\.(rel|href)$", "L1",
  "relations[] {type=rel, ref} of the control's own Requirement, at every depth (#control -> req URI; #uuid -> "
  "back-matter URL)", CARRIED, at(r"/relations/\[\]/(type|ref)",COMPAT_AT+r"/links/.*")),
 (C+r"\.params\[\]\.id$", "L1", "statement parameter name (type string); key of compat param-extras", CARRIED,
  at(r"/statements/\[\]/parameters/\[\]/name",COMPAT_AT+r"/param-extras/\{param\}")),
 (C+r"\.params\[\]\.(label|values\[\])$", "L1",
  "parameter label / default - first-class since the D9 rev (backlog #1); more than one value: all of them in "
  "compat param-extras", CARRIED,
  at(r"/statements/\[\]/parameters/\[\]/(label|default)",COMPAT_AT+r"/param-extras/\{param\}/values/\[\]")),
 (C+r"\.params\[\]\.props\[\]\.(name|value)$", "L2", "compat oscal-1x: param-extras (param alt-identifier only)", CARRIED,
  at(COMPAT_AT+r"/param-extras/\{param\}/(alt-identifier|props/.*)")),
 (C+r"\.props\[\]\.ns$", "-",
  "no content: the namespace this mapping is written for (PROP_NS), a rule the ledger checks. A prop in another "
  "namespace is not read and is carried whole (compat `props`)", NOT_CONTENT+CARRIED, at(COMPAT_AT+r"/props/.*")),
 (C+r"\.props\[\]\.(name|value)$", "L1",
  "dispatch by prop name (see per-prop table); a prop the mapping does not read: compat `props`", CARRIED,
  at(r"/label",r"/aliases/\[\]/(scheme|value)",TAX_AT+r"/(sec-level|effort|tags)(/\[\])?",
     SECO_AT+r"/(confidentiality|integrity|availability|authenticity|threat-refs)(/\[\])?",
     r"/id",r"/title/de",r"/objects/\[\]/(id|path)",                # the baseline Set a sec_level names
     r"/schema/properties/observed-sec-levels/enum/\[\]",COMPAT_AT+r"/props/.*")),
 (C+r"\.parts\[\]\.id$", "-",
  "no content: rebuilt exactly, the control's id and `_stm` or `_gdn`, a rule the ledger checks. An id the rule "
  "does not give is carried (compat `parts`)", NOT_CONTENT+CARRIED, at(COMPAT_AT+r"/parts/.*")),
 (C+r"\.parts\[\]\.name$", "L1",
  "`guidance` -> the key of the gspp-narrative payload; `statement` -> no content: it selects the part whose "
  "prose and props become the statement, a rule the ledger checks. A part of another name is carried whole "
  "(compat `parts`)", CARRIED+NOT_CONTENT, at(NARR_AT+r"/by-statement/smt/guidance",COMPAT_AT+r"/parts/.*")),
 (C+r"\.parts\[\]\.prose$", "L1", "statements[].prose.de ({{insert}} -> {param:}) / gspp-narrative guidance", CARRIED,
  at(r"/statements/\[\]/prose/de",NARR_AT+r"/by-statement/smt/guidance/de",COMPAT_AT+r"/parts/.*")),
 (C+r"\.parts\[\]\.props\[\]\.ns$", "-",
  "no content: the namespace this mapping is written for (PROP_NS), a rule the ledger checks. A prop in another "
  "namespace is not read and is carried whole (compat `parts`)", NOT_CONTENT+CARRIED, at(COMPAT_AT+r"/parts/.*")),
 (C+r"\.parts\[\]\.props\[\]\.(name|value)$", "L1",
  "dispatch by part-prop name (grammar/objectives/criteria; packed lists reported); a prop the mapping does not "
  "read: compat `parts`", CARRIED,
  at(r"/statements/\[\]/modality",GRAM_AT+r"/(action|result|result-specification|target-object-categories)(/\[\])?",
     ACRIT_AT+r"/required-documentation(/\[\])?",COMPAT_AT+r"/parts/.*")),
 # What OSCAL allows and this mapping does not read. The pinned catalogue
 # has none of it; a later one that does loses nothing.
 (C+r"\.params\[\]\.", "L2",
  "what the source says of a parameter beyond its id, label and one value: compat param-extras, as the source "
  "holds it", CARRIED, at(COMPAT_AT+r"/param-extras/\{param\}/.*")),
 (C+r"\.", "L2",
  "a member of a control, a part, a prop or a link this mapping does not read: carried as the source holds it "
  "(compat `props`, `parts`, `links`, `control`)", CARRIED, at(COMPAT_AT+r"/(props|parts|links|control)/.*")),
 (r"^catalog(\.groups\[\])+\.", "L2",
  "a member or a prop of a group this mapping does not read: carried as the source holds it on the Set of the "
  "group (compat `props`, `group`)", CARRIED, at(COMPAT_AT+r"/(props|group)/.*")),
 (r"^catalog\.", "L2",
  "a member of the catalogue this mapping does not read: carried as the source holds it on the root Set (compat "
  "`catalog`)", CARRIED, at(COMPAT_AT+r"/catalog/.*")),
]
def path_map(path):
    """the row of the path map for a source path: (level, sentence, outcomes, places), or None"""
    for pat,lvl,tgt,allowed,places in RULES:
        if re.search(pat,path): return lvl,tgt,allowed,places
    return None
def destination(path):
    row=path_map(path)
    return (row[0],row[1]) if row else (None,None)

PROP_DEST = {
 "alt-identifier": ("L1","Requirement.aliases (scheme bsi-uuid)"),
 "label": ("L1","Requirement.label (the control id where a control has no label prop)"),
 "sec_level": ("L1","gspp-taxonomy: sec-level (by-statement); the baseline Set of that level, in which the Requirement "
                    "is listed: its id, title and file; the enum of observed values in the pinned taxonomy schema"),
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
}
assert set(FIELD)==set(PROP_DEST), "FIELD and the per-prop table name the same props"
assert set(PROP_NS)|{"alt-identifier","label"}==set(FIELD), "every prop the mapping reads has its namespace, or none"

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
objects={}
params_unref=0; params_total=0; multi_value_params=[]
tag_values=collections.Counter(); sec_values=collections.Counter()

sec_enum={}        # sec_level value -> its entry in the enum of the pinned taxonomy schema
resources_named=set()   # uuids of the back-matter resources that a link of a control names
link_targets=[]    # (control, rel, id the link names) of every link written as a Requirement URI
as_held=collections.Counter()   # member of the compat facet -> the objects that carry something there as the source holds it
made=collections.Counter()      # kind of Set -> how many were made
resource_address_of={}          # uuid of a back-matter resource -> the address it gives (plain, for the read-back)

def add_object(rel,obj):
    """two controls, or a control and a group, whose ids give one file name would overwrite each other"""
    if rel in objects: raise SystemExit(f"two objects would be written to {rel}: their ids give the same file name")
    objects[rel]=obj

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

def part_rest(part,read,unread_props):
    """What this mapping does not read of a part it reads, in the part's own
    shape: its name, to say which part, and every member that is left
    (`unread_props`: the props of it that are not read). None where nothing
    is left."""
    left={k:(unread_props if k=="props" and "props" in read else v) for k,v in part.items()
          if k=="name" or (k not in read) or (k=="props" and unread_props)}
    return left if set(left)-{"name"} else None

def collect_stmt(prefix_ns, c, cp, cunread, req, found):
    """Fills the one statement of control c and the facet payloads keyed by
    it. cp: the props of the control this mapping reads; cunread: those it
    does not; found: what goes into the compat facet as the source holds it."""
    sid="smt"
    parts=c.get("parts",[]) or []
    smt=next((p for p in parts if p.get("name")=="statement"),{})
    guid=next((p for p in parts if p.get("name")=="guidance"),None)
    if guid is not None and not guid.get("prose"): guid=None         # a guidance without a prose is not read: carried whole
    prose = statement_prose(smt.get("prose",""))
    punread=[]; pp = read_props(smt,PART_PROPS,punread)
    def unread(prop,of,rest):
        """a prop that was taken as read and whose value this mapping cannot write after all"""
        rest.append(of.pop(prop["name"]))
    # a verb outside MODAL is counted, `unspecified` is written, and the prop is carried as the source holds it
    if "modal_verb" in pp and pp["modal_verb"]["value"] not in MODAL:
        unknown_modal[pp["modal_verb"]["value"]]+=1; unread(pp["modal_verb"],pp,punread)
    # a list prop whose value holds no term gives an empty list; the value is carried as the source holds it
    for name in ("target_object_categories","documentation"):
        if name in pp and not split_list(pp[name]["value"]): punread.append(pp[name])
    for name in ("tags","threats"):
        if name in cp and not split_list(cp[name]["value"]): cunread.append(cp[name])
    # parameter slots in ALL part-prop values: each {{Label}} must stand where
    # the prose inserts a parameter; the label normally repeats the parameter's
    labels={pm.get("label") for pm in c.get("params",[]) or []}
    for part in parts:
        for p in part.get("props",[]) or []:
            v=p.get("value") or ""
            got=SLOT_RE.findall(v)
            if not got: continue
            at_insert=slot_at_insert(v, smt.get("prose",""))
            for label in got:
                slots.append({"control":c["id"],"prop":p["name"],"slot":label,
                              "at-insert":at_insert,"label-of-a-parameter":label in labels})
    # list values: one prop per term is the OSCAL form; count the packed ones
    for p in (smt.get("props",[]) or []) + (c.get("props",[]) or []):
        if p["name"] in LIST_PROPS:
            list_props[p["name"]]+=1
            if len(split_list(p["value"]))>1:
                packed[p["name"]].append({"control":c["id"],"value":p["value"]})
    mv = pp.get("modal_verb")
    mod = D(R_MODAL,MODAL.__getitem__,mv["value"]) if mv else "unspecified"
    modality_count[mod]+=1
    st={"id":sid,(field(mv) if mv else "modality"):mod,
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
        # what the kernel's parameter has no member for: the alt-identifier, every value where there is more
        # than one (`default` holds the first), and whatever else the source says of the parameter
        extras={}
        xunread=[]; xp=read_props(pm,PARAM_PROPS,xunread)
        if "alt-identifier" in xp: extras[field(xp["alt-identifier"])]=xp["alt-identifier"]["value"]
        if len(vals)>1: extras["values"]=vals
        if "label" in pm and not pm["label"]: extras["label"]=pm["label"]      # an empty label is no label of the kernel
        if xunread: extras["props"]=xunread
        for k,v in pm.items():
            if k not in PARAM_MEMBERS: extras[k]=v
        if extras:
            found.setdefault("param-extras",{})[pid]=extras
            if set(extras)-{"alt-identifier"}: as_held["param-extras beyond the alt-identifier"]+=1
    # facets by-statement. Every key that a prop selects is field(prop): the
    # prop's own name, or the name FIELD maps it to.
    def by(fname): return req["facets"].setdefault(fname,{}).setdefault("by-statement",{}).setdefault(sid,{})
    g=by(F_GRAM)
    for src in ("action_word","result","result_specification"):
        if src in pp: g[field(pp[src])]=pp[src]["value"]
    if "target_object_categories" in pp:
        g[field(pp["target_object_categories"])]=terms(pp["target_object_categories"]["value"])
    if "documentation" in pp: by(F_ACRIT)[field(pp["documentation"])]=terms(pp["documentation"]["value"])
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
    if guid: by(F_NARR)[guid["name"]]={"de":guid["prose"]}      # the part's name is the key: `guidance`
    # The parts. Of the statement part and the guidance part this mapping
    # reads the prose (and the statement's props); the name `statement`
    # selects, and the id is no content where it is the control's id and the
    # suffix. Whatever else a part holds, and every other part, is carried
    # as the source holds it.
    prest=[]
    for part in parts:
        if part is smt and any_leaf([part.get("prose"),part.get("props")]):
            led.selector(part["name"],N_PART,[part.get("prose"),part.get("props")],among=("statement",))
            rebuilt="id" in part and part["id"]==stm_id(c["id"])
            if rebuilt: led.rebuilt(part["id"],N_STM_ID,stm_id,c["id"])
            left=part_rest(part,("name","prose","props")+(("id",) if rebuilt else ()),punread)
        elif part is guid:
            rebuilt="id" in part and part["id"]==gdn_id(c["id"])
            if rebuilt: led.rebuilt(part["id"],N_GDN_ID,gdn_id,c["id"])
            left=part_rest(part,("name","prose")+(("id",) if rebuilt else ()),None)
        else: left=part
        if left: prest.append(left)
    if prest: found["parts"]=prest
    for k in pp: stats["part-props"][k]+=1
    for k in cp: stats["ctrl-props"][k]+=1
    return st

def mint_requirement(prefix_ns, c, version, bm_map):
    """the Requirement of one control: of a top-level control and of a nested
    one alike, with its own statement, parameters, props and links"""
    rid=D(R_REQ,req_uri,prefix_ns,c["id"])
    found={}
    cunread=[]; cp=read_props(c,CONTROL_PROPS,cunread)
    req={"id":rid,"version":version,
         (field(cp["label"]) if "label" in cp else "label"):(cp["label"]["value"] if "label" in cp else c["id"]),
         "lifecycle":"active","title":c["title"],
         "statements":[],"facets":{}}
    if "alt-identifier" in cp:
        req["aliases"]=[{"scheme":scheme(cp["alt-identifier"]),"value":cp["alt-identifier"]["value"]}]
    req["statements"].append(collect_stmt(prefix_ns,c,cp,cunread,req,found))
    rels=[]; lrest=[]
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
        if set(l)-{"href","rel"}: lrest.append(l)       # a relation has a type and a ref; a link that says more is carried whole
    if rels: req["relations"]=rels
    if cunread: found["props"]=cunread
    if lrest: found["links"]=lrest
    crest={k:v for k,v in c.items() if k not in CONTROL_MEMBERS}
    if crest: found["control"]=crest
    compat={k:held(found[k]) for k in COMPAT_MEMBERS if k in found}
    for k in compat:
        if k!="param-extras": as_held[k]+=1
    if compat: req["facets"][F_COMPAT]=compat
    if not req["facets"]: req.pop("facets")
    return rid,req,cp

# rebuild output (lib Bundle: Windows-safe in-place writes)
bundle=Bundle(OUT,lang="de")
paths=collections.Counter(); catalogs_meta=[]; provenance_of={}
baseline={}        # (key, sec_level) -> {"set": its id, title and file, "refs": the Requirements listed in it}
seq={"n":0}
def nseq(): seq["n"]+=10; return seq["n"]

all_ids={}
for key,fn,ns in SOURCES:
    # the whole file under the source's key: a pointer of the ledger reads `gspp#/catalog/...`
    cat=led.source(key,json.load(open(fn,encoding="utf-8")),typed=True)["catalog"]
    inventory(cat,"catalog",paths)
    meta=cat["metadata"]
    version=meta["version"]
    catalogs_meta.append((key,meta["title"],version,meta["oscal-version"]))
    # who wrote the document and when, by the rule of backlog #69: the party the metadata names as creator,
    # and the day of last-modified. Nothing is made up where the source names nobody or no day.
    provenance_of[key]={}
    author=document_author(meta)
    if author: provenance_of[key]["author-ref"]=D(R_AUTHOR,party_uri,ns,author["name"])
    if document_day(meta): provenance_of[key]["date"]=D(R_DATE,day_of,meta["last-modified"])
    # resource uuid -> (the uuid as the source holds it, the address the resource gives)
    resources=cat.get("back-matter",{}).get("resources",[]) or []
    bm_map={r["uuid"]:(r["uuid"],r.get("rlinks",[{}])[0].get("href") or r.get("title","")) for r in resources}
    resource_address_of.update({str(u):str(a) for u,a in bm_map.values()})
    ids=set()
    def conv_control(c):
        """-> the id of what stands for control c in the Set of its group or
        of its parent control: its Requirement, or, where it has nested
        controls, the Set that groups it with them. Nesting is grouping and
        nothing else: no relation is written between a control and the
        controls nested in it."""
        ids.add(c["id"])
        rid,req,cp=mint_requirement(ns,c,version,bm_map)
        add_object(D(R_REQ_FILE,req_file,key,c["id"]),req)
        if "sec_level" in cp:
            # Every control names the baseline Set of its sec_level. The
            # Set is written once, from the first control that names it;
            # every later one is linked to it, and the ledger checks that
            # its own value gives the same Set.
            lv=cp["sec_level"]["value"]
            mine={"id":D(R_BASE,baseline_uri,ns,lv),"title":D(R_BASE_TITLE,baseline_title,lv),
                  "file":D(R_BASE_FILE,baseline_file,key,lv)}
            b=baseline.setdefault((key,lv),{"set":mine,"refs":[]})
            if b["set"] is not mine: led.same(mine,b["set"],SAME_BASELINE)
            b["refs"].append(rid)
        nested=c.get("controls",[]) or []
        if not nested: return rid
        # the grouping: the control's own Requirement first, then what stands for each nested control
        members=[{"ref":rid,"sequence":nseq()}]
        for ch in nested:
            ref=conv_control(ch)
            members.append({"ref":ref,"sequence":nseq()})
        u=D(R_GROUPING,set_uri,ns,c["id"])
        add_object(D(R_GROUPING_FILE,set_file,key,c["id"]),
                   {"id":u,"version":version,"lifecycle":"active","title":c["title"],"members":members})
        made["of a control with nested controls"]+=1
        return u
    def conv_group(g,path_ids):
        entries=[]
        for sub in g.get("groups",[]) or []:
            u=conv_group(sub,path_ids+[slug(sub.get("id") or sub.get("title"))])
            if u: entries.append({"ref":u,"sequence":nseq()})
        for c in g.get("controls",[]) or []:
            ref=conv_control(c)
            entries.append({"ref":ref,"sequence":nseq()})
        # A group that holds nothing gives a Set without members: its id,
        # its title and its props are content all the same. A group without
        # an id is named by the titles on its path; that name is not stated
        # as a rule (no group of the catalogue is without an id).
        gid=g.get("id")
        sid=gid or "-".join(path_ids)
        u=D(R_SET,set_uri,ns,gid) if gid else set_uri(ns,sid)
        sobj={"id":u,"version":version,"lifecycle":"active",
              "title":g.get("title",sid),"members":entries}
        # The props of a group: its label (with the description of the
        # practice in `remarks`) and its alt-identifier, both without a
        # namespace. Of a label that repeats the last is read. Every other
        # prop, and one that holds a member this mapping does not read, is
        # carried as the source holds it.
        gprops=g.get("props",[]) or []
        labels=[p for p in gprops if p.get("name")=="label" and "ns" not in p]
        gfound={}
        for gp in gprops:
            mine=gp.get("name") in GROUP_PROPS and "ns" not in gp
            read=set()
            if mine and gp["name"]=="label" and gp is labels[-1]:
                sobj[field(gp)]=gp["value"]; read={"name","value"}
                if gp.get("remarks"):
                    sobj.setdefault("facets",{}).setdefault(F_NARR,{})["description"]={"de":gp["remarks"]}; read.add("remarks")
            elif mine and gp["name"]=="alt-identifier":
                sobj.setdefault("aliases",[]).append({"scheme":scheme(gp),"value":gp["value"]}); read={"name","value"}
            if set(gp)-read: gfound.setdefault("props",[]).append(gp)
        grest={k:v for k,v in g.items() if k not in GROUP_MEMBERS}
        if grest: gfound["group"]=grest
        if gfound:
            sobj.setdefault("facets",{})[F_COMPAT]={k:held(gfound[k]) for k in COMPAT_MEMBERS if k in gfound}
            for k in gfound: as_held[k]+=1
        add_object(D(R_SET_FILE,set_file,key,gid) if gid else set_file(key,sid),sobj)
        made["of a group"]+=1
        return u
    top=[]
    for g in cat.get("groups",[]) or []:
        u=conv_group(g,[slug(g.get("id") or g.get("title"))])
        if u: top.append({"ref":u,"sequence":nseq()})
    for c in cat.get("controls",[]) or []:      # a control that stands in no group (the pinned catalogue has none)
        ref=conv_control(c)
        top.append({"ref":ref,"sequence":nseq()})
    # The root Set stands for the document. Its title and the version of
    # every object are kernel members. Everything else the document says of
    # itself (dates, the OSCAL version, props, links, roles, parties,
    # responsible parties, remarks) has no member in the kernel and stands
    # under the compat facet's `metadata`, in the source's own shape, the
    # source's values as they are. A back-matter resource that a link of a
    # control names is carried whole beside it.
    root={"id":f"{ns}/set/tax/root","version":version,"lifecycle":"active","title":meta["title"],"members":top}
    rfound={}
    mrest={k:v for k,v in meta.items() if k not in ("title","version")}
    if mrest: rfound["metadata"]=mrest
    named=[r for r in resources if r["uuid"] in resources_named]
    if named: rfound["back-matter"]={"resources":named}
    crest={k:v for k,v in cat.items() if k not in CATALOG_MEMBERS}
    if crest: rfound["catalog"]=crest
    if rfound:
        root["facets"]={F_COMPAT:{k:held(rfound[k]) for k in COMPAT_MEMBERS if k in rfound}}
        for k in rfound: as_held[k]+=1
    add_object(f"objects/{key}/set-tax-root.json",root)
    all_ids[key]=ids
    # a back-matter resource that no link of a control named: the declared drop, value by value
    for r in resources:
        if r.get("uuid") not in resources_named: led.drop_value(r,DROP_RESOURCE)

for (key,lvl),b in sorted(baseline.items()):
    add_object(b["set"]["file"],{
        "id":b["set"]["id"],"version":[v for k2,_,v,_ in catalogs_meta if k2==key][0],
        "lifecycle":"active","title":b["set"]["title"],
        "members":[{"ref":r,"sequence":(i+1)*10} for i,r in enumerate(b["refs"])]})

# facet schema stubs (enums generated from observed values); declaration
# promotions per D10 rev 2 (backlog #8): security-objectives -> [selection]
bundle.stub("gspp-taxonomy-1.0.0-stub.json","https://ns.bsi.bund.de/facet/gspp-taxonomy",["selection"],
     {"by-statement":{"type":"object"},"observed-sec-levels":{"enum":sorted(sec_enum.values())}})
bundle.pin_stdlib("statement-grammar-1.0.0.json")   # 26: stdlib pins are VERBATIM
bundle.pin_stdlib("security-objectives-1.0.0.json")
bundle.pin_stdlib("assessment-criteria-1.0.0.json")
bundle.stub("gspp-narrative-1.0.0-stub.json","https://ns.bsi.bund.de/facet/gspp-narrative",[],
     {"by-statement":{"type":"object"},"description":{"type":"object"}})
# the compat facet: what OSCAL says and neither the kernel nor a standard facet has a member for
bundle.stub("oscal-1x-compat-1.0.0-stub.json","https://ns.jascon.net/compat/oscal-1x",[],
     {"metadata":{"type":"object"},"back-matter":{"type":"object"},"catalog":{"type":"object"},
      "param-extras":{"type":"object"},"props":{"type":"array"},"parts":{"type":"array"},
      "links":{"type":"array"},"control":{"type":"object"},"group":{"type":"object"}})

led.resolve(objects)        # a boolean of the source is written as a plain boolean, and the ledger knows where
for rel,o in objects.items(): bundle.add(rel,o)
manifest=bundle.write({"sources":[{"key":k,"title":t,"version":v,"oscal-version":o,**provenance_of[k]}
               for k,t,v,o in catalogs_meta],
               "converter":"convert_bsi.py v0.3 (single-catalog: MS-TLS dropped by decision 2026-07-21; "
                           "every control is a Requirement of its own since 2026-11-14)"})

# ---------- the ledger's account ----------
# Every file of the bundle is read back and every claim is checked against
# it: the objects, the pinned schemas (the taxonomy stub lists the observed
# sec_level values) and the manifest. ACCOUNT has one entry per source value
# and lasts as long as the run. The record that is written and committed has
# one row per source path and outcome (ledger_by_path); the payload keyed by
# the id of a parameter is one row, not one for every parameter.
ACCOUNT=led.account(OUT,{**bundle.objects,**bundle.schemas,"content-manifest.json":manifest})
LEDGER=ledger_by_path(ACCOUNT,collapse=[(r"/param-extras/[^/]+",r"/param-extras/{param}")])
with open(LJS,"w",encoding="utf-8") as f:
    json.dump(LEDGER,f,indent=1,ensure_ascii=False); f.write("\n")
LT=LEDGER["totals"]; LFAIL=LEDGER["verification-failures"]
FILES_READ=len(bundle.objects)+len(bundle.schemas)+1

# rule -> the source values it was applied to; reason -> the values dropped
# for it; rule of what is no content -> the values it covers
RULE_NAMES=[R_REQ,R_REQ_FILE,R_LINK,R_RESOURCE,R_SET,R_SET_FILE,R_GROUPING,R_GROUPING_FILE,R_BASE,R_BASE_TITLE,
            R_BASE_FILE,R_ENUM,R_PROSE,R_MODAL,R_TERM,R_THREAT,R_EFFORT,R_FIELD,R_SCHEME,R_AUTHOR,R_DATE,R_DECIMAL]
rule_use=collections.Counter(); drop_use=collections.Counter(); no_content_use=collections.Counter()
for e in ACCOUNT["entries"]:
    for r in {d["rule"] for d in e.get("destinations",[]) if "rule" in d}: rule_use[r]+=1
    if e["outcome"]=="intentionally-dropped": drop_use[e["reason"]]+=1
    if e["outcome"]=="not-content": no_content_use[(e["kind"],e["rule"])]+=1
# Wiring checks. The ledger checks every claim of a destination and every
# rule of what is no content. It cannot check a declaration of this script
# that is too wide, or a record that is not this run's. Each check answers a
# defect that was put into a copy of this script on purpose and ran through
# with exit code 0 before the check existed. A check that fails ends the run
# with a non-zero exit code, after the reports are written.
wiring=[]
if not set(rule_use)<=set(RULE_NAMES): wiring.append("a rule is applied that the report does not list")
if not set(no_content_use)<=set(NO_CONTENT): wiring.append("a value is no content by a rule that the report does not list")
if not set(drop_use)<={r for _,r,_ in DROPS}: wiring.append("a value is dropped for a reason that DROPS does not hold")
# Among the values that reached the bundle are names: the name of a prop (or
# of the guidance part) holds no content of its own, it selects the field
# the value is written to. Such a name is in the bundle as a key, or as the
# alias scheme. The report counts them apart from the values.
names_as_key=sum(1 for e in ACCOUNT["entries"] if e["outcome"]=="copied"
                 and all(d.get("as")=="key" for d in e["destinations"] if "rule" not in d))
names_by_rule=sum(1 for e in ACCOUNT["entries"] if e["outcome"]=="transformed"
                  and {d["rule"] for d in e["destinations"]}<={R_FIELD,R_SCHEME})

# The path map held against the ledger, row by row of the record: a value
# whose outcome its row of the map does not allow, and a value that stands
# at a place its row does not name. A value that is unaccounted is the
# gate's (the last statement of this script); every other disagreement is a
# wiring check: a drop that reaches a path the map does not give up, a
# sentence of the map that says "not carried" of a value that is, a value
# that went somewhere the map does not say.
disagree=[]       # (ledger path, outcome, values, first value, what the map allows)
elsewhere=[]      # (ledger path, place, values): a value stands where the map does not name a place for its path
for row in LEDGER["paths"]:
    mapped_to=path_map(row["path"].split(".",1)[1])
    if mapped_to is None: continue                                  # a path without a row is reported as UNMAPPED
    _,_,allowed,places=mapped_to
    if row["outcome"]!="unaccounted" and row["outcome"] not in allowed:
        disagree.append((row["path"],row["outcome"],row["count"],row["example"],allowed))
    for t in row.get("to",[]):
        if places is None or not re.search(places,t["pointer"]): elsewhere.append((row["path"],t["pointer"],t["count"]))
for p,o,n,x,a in disagree:
    wiring.append(f"{n:,} value(s) of {p} are {o}, and the path map allows {' or '.join(a)} there (first {x})")
for p,place,n in elsewhere:
    wiring.append(f"{n:,} value(s) of {p} stand at {place}, a place the path map does not name for that path")

def source_at(pointer):
    """the source value a pointer of the ledger names (`gspp#/catalog/groups/0/id`)"""
    tag,_,ptr=pointer.partition("#")
    node=led.docs[tag]
    for x in ptr.split("/")[1:]:
        x=x.replace("~1","/").replace("~0","~")
        node=node[int(x)] if isinstance(node,list) else node[x]
    return node

# the declared drops that remain, one row for every source path: for the author's decision
reading_of={reason:reading for _,reason,reading in DROPS}
dropped_rows=[{"path":r["path"],"count":w["count"],"reason":w["reason"],"example":r["example"],
               "example-value":source_at(r["example"]),"reading":reading_of.get(w["reason"],"")}
              for r in LEDGER["paths"] if r["outcome"]=="intentionally-dropped" for w in r["reasons"]]

# ---------- the written bundle, read back and held against the source ----------
# Counted from the files on disk and from the source as it was loaded, not
# from the variables of the conversion above: every control of the source,
# at every depth, is a Requirement; every link of a control is a relation of
# that control's own Requirement; and what a relation or a member of a Set
# names is an object of the bundle.
def source_controls(doc):
    """-> [(control, depth)] of the catalogue, read from the plain source"""
    out=[]
    def of(cs,depth):
        for c in cs or []: out.append((c,depth)); of(c.get("controls"),depth+1)
    def groups(gs):
        for g in gs or []: of(g.get("controls"),0); groups(g.get("groups"))
    groups(doc["catalog"].get("groups")); of(doc["catalog"].get("controls"),0)
    return out
on_disk={}
for rel in bundle.objects:
    with open(os.path.join(OUT,rel),encoding="utf-8") as f: o=json.load(f)
    on_disk[o["id"]]=o
src_controls=[(c,d,ns) for key,_,ns in SOURCES for c,d in source_controls(led.docs[key])]
src_links=[(ns,c["id"],l.get("rel","related"),l.get("href","")) for c,_,ns in src_controls for l in c.get("links") or []]
disk_reqs={i:o for i,o in on_disk.items() if "statements" in o}
disk_sets={i:o for i,o in on_disk.items() if "members" in o}
disk_relations=[(i,r["type"],r["ref"]) for i,o in on_disk.items() for r in o.get("relations") or []]
def is_own_relation(ns,cid,rel,href):
    """is this link of the source a relation of the Requirement of its own control?"""
    if href.startswith("#") and href[1:] in resource_address_of: want=resource_address_of[href[1:]]
    else: want=req_uri(ns,href[1:]) if href.startswith("#") else href
    return any(r["type"]==rel and r["ref"]==want for r in (disk_reqs.get(req_uri(ns,cid)) or {}).get("relations") or [])
BACK={"controls":len(src_controls),"controls-top-level":sum(1 for _,d,_ in src_controls if d==0),
      "controls-nested":sum(1 for _,d,_ in src_controls if d>0),
      "deepest-nesting":max([d for _,d,_ in src_controls] or [0]),
      "controls-with-nested-controls":sum(1 for c,_,_ in src_controls if c.get("controls")),
      "requirements":len(disk_reqs),
      "requirements-of-a-control":sum(1 for c,_,ns in src_controls if req_uri(ns,c["id"]) in disk_reqs),
      "requirements-with-one-statement":sum(1 for o in disk_reqs.values() if len(o["statements"])==1),
      "sets":len(disk_sets),
      "sets-that-group-a-control-with-its-nested-controls":sum(
          1 for c,_,ns in src_controls if c.get("controls")
          and [m["ref"] for m in (disk_sets.get(set_uri(ns,c["id"])) or {}).get("members",[])][:1]==[req_uri(ns,c["id"])]
          and len(disk_sets[set_uri(ns,c["id"])]["members"])==1+len(c["controls"])),
      "links":len(src_links),"links-of-nested-controls":sum(1 for c,d,_ in src_controls if d>0 for _ in c.get("links") or []),
      "links-that-are-a-relation-of-their-own-requirement":sum(1 for l in src_links if is_own_relation(*l)),
      "relations":len(disk_relations),
      "relations-that-name-no-object":sum(1 for _,_,ref in disk_relations if ref.startswith(NS+"/") and ref not in on_disk),
      "set-members":sum(len(o["members"]) for o in disk_sets.values()),
      "set-members-that-name-no-object":sum(1 for o in disk_sets.values() for m in o["members"] if m["ref"] not in on_disk)}
if BACK["requirements"]!=BACK["controls"] or BACK["requirements-of-a-control"]!=BACK["controls"]:
    wiring.append(f"the source has {BACK['controls']:,} controls and the bundle {BACK['requirements']:,} Requirements, "
                  f"{BACK['requirements-of-a-control']:,} of them of a control")
if BACK["links-that-are-a-relation-of-their-own-requirement"]!=BACK["links"]:
    wiring.append(f"{BACK['links']-BACK['links-that-are-a-relation-of-their-own-requirement']:,} link(s) of a control are "
                  f"no relation of that control's own Requirement")
if BACK["relations"]!=BACK["links"]:
    wiring.append(f"the bundle holds {BACK['relations']:,} relations and the source {BACK['links']:,} links of controls: "
                  f"a relation was written that no link states (nesting is grouping, not a relation), or a link was lost")
if BACK["sets-that-group-a-control-with-its-nested-controls"]!=BACK["controls-with-nested-controls"]:
    wiring.append("a control with nested controls has no Set that lists its own Requirement first and then one member for each nested control")
if BACK["set-members-that-name-no-object"]: wiring.append(f"{BACK['set-members-that-name-no-object']:,} member(s) of a Set name no object of the bundle")
# a link to a control the catalogue does not define is the source's defect: the relation names no object, and the report says so
all_control_ids=set().union(*all_ids.values())
links_to_nothing=[t for t in link_targets if t[2] not in all_control_ids]
if BACK["relations-that-name-no-object"]!=len(links_to_nothing):
    wiring.append(f"{BACK['relations-that-name-no-object']:,} relation(s) name no object of the bundle, and the source has "
                  f"{len(links_to_nothing):,} link(s) to a control it does not define")

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
reqs=sum(1 for r in objects.values() if "statements" in r)
sets=sum(1 for r in objects.values() if "members" in r)
nstmt=sum(len(r.get("statements",[])) for r in objects.values() if "statements" in r)
ngroupsets=made["of a group"]; ngroupings=made["of a control with nested controls"]

j={"sources":[{"key":k,"title":t,"version":v} for k,t,v,_ in catalogs_meta],
   "totals":{"leaf-values":total,"mapped":mapped,"unmapped":total-mapped,
             "coverage-pct":round(100*mapped/total,3)},
   "objects":{"requirements":reqs,"statements":nstmt,"sets":sets,"total":len(objects),
              "sets-of-a-group":ngroupsets,"sets-of-a-control-with-nested-controls":ngroupings,
              "baseline-sets":len(baseline),"root-sets":len(SOURCES)},
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
             "not-content":[{"kind":k,"rule":r,"source-values":no_content_use[(k,r)]} for k,r in NO_CONTENT],
             "declared-drops":dropped_rows,
             "carried-as-the-source-holds-it":dict(sorted(as_held.items())),
             "bundle-read-back":BACK,
             "links-to-a-control-the-catalogue-does-not-define":len(links_to_nothing),
             "path-map-against-ledger":{"values-whose-outcome-the-map-does-not-allow":sum(d[2] for d in disagree),
                                        "rows":[{"path":p,"outcome":o,"count":n,"first":x,"path-map-allows":list(a)}
                                                for p,o,n,x,a in disagree],
                                        "values-at-a-place-the-map-does-not-name":sum(e[2] for e in elsewhere),
                                        "places":[{"path":p,"pointer":place,"count":n} for p,place,n in elsewhere]},
             "written-without-a-source-value":{k:{"leaf-values":c["leaf values"],
                                                  "without-a-source-value":sum(plain(c).values()),
                                                  **({"by-place":plain(c)} if k!="schemas" else {})}
                                               for k,c in written.items()},
             "wiring-checks-failed":wiring},
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
          f"**{LT['not-content']:,}** are no content by a rule the ledger checks, "
          f"**{LT['intentionally-dropped']:,}** are dropped for a declared reason, **{LT['unaccounted']:,}** are unaccounted.")
md.append(f"- Emitted: **{reqs:,} Requirements**, one for every control at every depth "
          f"({BACK['controls-top-level']:,} top-level and {BACK['controls-nested']:,} nested; nesting reaches depth "
          f"{BACK['deepest-nesting']}), each with one statement ({nstmt:,}); **{sets} Sets**: {ngroupsets} of a group, "
          f"{ngroupings} of a control with nested controls, {len(baseline)} baselines, {len(SOURCES)} root; "
          f"manifest with both digests, {len(manifest['facet-schemas'])} pinned facet stubs.\n")
md.append("## Conversion rules (declared, counted)\n")
md.append(f"- **Modality** from `modal_verb` (code map incl. DARF NUR -> may-only): "
          + ", ".join(f"{k} x{v}" for k,v in sorted(modality_count.items(),key=lambda x:-x[1]))
          + (f"; unknown verbs: {dict(unknown_modal)}" if unknown_modal else "; no unknown verbs") + ".")
md.append(obligated_party_line(PARTY,PARTY_ORIGIN,PARTY_DEFAULT,PARTY_WHY))
md.append(f"- **Every control is a Requirement of its own**, at every depth, with its own statement (id `smt`), "
          f"parameters, props and links. BSI nests controls for grouping only (the author, 2026-11-14), so the "
          f"nesting is carried as grouping: a control that has nested controls ({BACK['controls-with-nested-controls']}) "
          f"gives a Set as well, titled as the control, with the id `.../set/tax/` and the control id in lower case "
          f"with hyphens. Its members are the control's own Requirement first and then what stands for each nested "
          f"control in source order (a Requirement, or such a Set in turn). In the Set of the group, and of a parent "
          f"control, that Set stands where the control stood. No relation is written between a control and the "
          f"controls nested in it.")
md.append(f"- **{{{{ insert: param, x }}}}** in prose -> `{{param:x}}` tokens; params typed `string` "
          f"with **first-class `label` + `default`** (D9 rev, backlog #1) - x{params_total} parameters, "
          f"the param-extras residue drains to alt-identifier uuids only. Params never referenced by a "
          f"`{{param:}}` token in their statement's prose: x{params_unref} (counted - source QA signal); "
          f"multi-value params x{len(multi_value_params)} (first value becomes default, every value is kept in "
          f"compat param-extras).")
md.append("- **Payload free text language-tagged** per corpus language (`{de: ...}` on statement prose, "
          "guidance, Set descriptions) - this corpus was born tagged; harmonization rule (backlog #12) "
          "verified, not applied.")
md.append("- **Grammar** (action_word/result/result_specification/target_object_categories) -> "
          "`statement-grammar@1` by-statement; **documentation** -> `assessment-criteria@1` "
          "required-documentation; **C/I/A/Auth + threats** -> `security-objectives@1` "
          "(threat codes minted from 'G 0.x'); **sec_level/effort/tags/class** -> "
          "`gspp-taxonomy@1`; **guidance parts** -> `gspp-narrative@1`.")
md.append(f"- **Baselines** from the `sec_level` of every control, nested ones included (a nested control is a "
          f"full control and has a level of its own): "
          + ", ".join(f"{k}:{l} ({len(v['refs'])})" for (k,l),v in sorted(baseline.items())) + ".")
md.append("- **alt-identifier** -> aliases (scheme bsi-uuid) on the Requirement of every control and on the Set "
          "of every group. The namespaces of the props (the addresses of BSI's CSV lists) are no content: this "
          "mapping is written for exactly those, and the ledger checks every one of them.")
md.append("- **Document metadata** -> the root Set, which stands for the document: its title, and the version "
          "on every object, are kernel members; everything else (last-modified, the OSCAL version, props, links, "
          "roles, parties, responsible parties, remarks) stands under the compat facet's `metadata` in the "
          "source's own shape. The manifest's provenance names the source with its title, version and OSCAL "
          "version, and by the rule of backlog #69 its author (the party the metadata names as creator, as a "
          "landmark URI) and its date (the day of last-modified).\n")
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
          "pinned schema now freezes).")
if links_to_nothing:
    md.append(f"- **A link names a control the catalogue does not define: {len(links_to_nothing)}.** First: "
              f"`{links_to_nothing[0][0]}` {links_to_nothing[0][1]} `#{links_to_nothing[0][2]}`. The relation is "
              f"written as the source says it and names no object of the bundle.")
md.append("")
LNAME=os.path.basename(LJS)
md.append("## Conversion ledger (measured per source value)\n")
md.append(f"- **Totals**: the path map says where each source path goes. The ledger follows each of the "
          f"{LEDGER['leaf-values']:,} source leaf values into the written bundle and reads every claim back from "
          f"the {FILES_READ:,} files of the bundle. **{LT['copied']:,} copied** (the value stands, with its type, at "
          f"the destination named), **{LT['transformed']:,} transformed** (a named rule made the destination from "
          f"it; the rule was applied to the source again and compared), **{LT['not-content']:,} no content** (a "
          f"name that only selects a field, a namespace, an id that is rebuilt exactly: each by a rule the ledger "
          f"checked on the source's own values), **{LT['intentionally-dropped']:,} intentionally dropped** (a "
          f"declared reason), **{LT['unaccounted']:,} unaccounted**. Checks that failed: {len(LFAIL)}. A value is "
          f"traced by what the converter did with it; an equal value elsewhere in the bundle does not count. A run "
          f"with an unaccounted value or a failed check ends with a non-zero exit code. The record is `{LNAME}`: "
          f"one row per source path and outcome, with the number of values, the first of them, and where they "
          f"went, by which rule they are no content, or why they were dropped.")
md.append(f"- **No content, by {sum(1 for k in NO_CONTENT if no_content_use[k])} checked rules: "
          f"{LT['not-content']:,}.** Such a value is not written, and nothing is lost without it. The ledger "
          f"applies each rule to the source's own value, and a value the rule does not cover is carried instead "
          f"(or ends the run).")
for k,r in NO_CONTENT: md.append(f"    - x{no_content_use[(k,r)]:,} ({k}): {r}")
md.append(f"- **Names and values**: {names_as_key+names_by_rule:,} of the {LT['copied']+LT['transformed']:,} values "
          f"in the bundle are names. The name of a prop, or of the guidance part, holds no content of its own: it "
          f"selects the field its value is written to. {names_as_key:,} stand in the bundle as the key of that "
          f"field, unchanged, and nowhere as a value (counted as copied); {names_by_rule:,} are mapped to a field of "
          f"another name or to the alias scheme (counted as transformed). The other "
          f"{LT['copied']+LT['transformed']-names_as_key-names_by_rule:,} are ids, texts and codes.")
md.append(f"- **Rules: {len(RULE_NAMES)} named, {sum(1 for r in RULE_NAMES if rule_use[r])} applied to this "
          f"catalogue.** Behind each, the number of source values it was applied to; a value can pass through more "
          f"than one. Where a rule leaves a value as it is, the value counts as copied: a prose without a parameter "
          f"token, a list prop with one term, a prop whose field has the prop's own name.")
for r in RULE_NAMES: md.append(f"    - x{rule_use[r]:,}: {r}")
md.append(f"- **Carried as the source holds it** (compat facet `oscal-1x@1`), because neither the kernel nor a "
          f"standard facet has a member for it: the document metadata on the root Set"
          + (", and on x" + ", x".join(f"{n} object(s) `{k}`" for k,n in sorted(as_held.items()) if k!="metadata")
             if set(as_held)-{"metadata"} else "; in this catalogue nothing else: the mapping reads every prop, "
             "part and member the controls and groups hold") + ".")
md.append(f"- **Declared drops that remain: {LT['intentionally-dropped']:,}**, in the table at the end of this "
          f"report. They stay declared until the author has gone through them.")
md.append(f"- **The written bundle, read back and held against the source** (counted from the files on disk and "
          f"from the source as loaded): {BACK['controls']:,} controls at all depths -> {BACK['requirements']:,} "
          f"Requirements, {BACK['requirements-of-a-control']:,} of them of a control, "
          f"{BACK['requirements-with-one-statement']:,} with exactly one statement; "
          f"{BACK['controls-with-nested-controls']:,} controls with nested controls -> "
          f"{BACK['sets-that-group-a-control-with-its-nested-controls']:,} Sets that list the control's own "
          f"Requirement first and then one member for each nested control; {BACK['links']:,} links of controls "
          f"({BACK['links-of-nested-controls']:,} of them on nested controls) -> "
          f"{BACK['links-that-are-a-relation-of-their-own-requirement']:,} are a relation of their own control's "
          f"Requirement; {BACK['relations']:,} relations in the bundle, {BACK['relations-that-name-no-object']:,} "
          f"of them name no object of the bundle; {BACK['set-members']:,} members of Sets, "
          f"{BACK['set-members-that-name-no-object']:,} of them name no object.")
md.append(f"- **The path map held against the ledger: {sum(d[2] for d in disagree)+sum(e[2] for e in elsewhere):,} "
          f"values disagree.** Every row of the path map names, beside its sentence, what may become of the values "
          f"of its paths (carried, no content by a checked rule, or dropped for a declared reason) and the places "
          f"at which a carried value may stand. Each run compares both with what the ledger found for every value, "
          f"and a disagreement ends the run with an error."
          + ("" if disagree or elsewhere else " No value has an outcome its row does not allow, and none stands at "
             "a place its row does not name."))
for p,o,n,x,a in disagree:
    md.append(f"    - `{p}`: x{n:,} {o}, where the path map allows {' or '.join(a)}; first `{x}`")
for p,place,n in elsewhere:
    md.append(f"    - `{p}`: x{n:,} at `{place}`, a place the path map does not name for that path")
wo=written["objects"]
party_from="the converter's default" if PARTY_ORIGIN=="converter-default" else "given by the caller"
WHAT={"/statements/[]/obligated-parties/[]":f"the obligated party `{PARTY}`, {party_from}",
      "/statements/[]/id":"the statement id `smt`",
      "/statements/[]/parameters/[]/type":"`string`, the type of every parameter",
      "/statements/[]/modality":"`unspecified`, where a statement has no modal verb the code map knows",
      "/lifecycle":"`active`: the source states no status of a control or a group, and the kernel requires the member",
      "/members/[]/sequence":"the order of the members of a Set",
      "/id":"the id of the root Set, and of a Set whose group has no id"}
md.append(f"- **What the ledger cannot see**: it follows source values into the bundle, not the other way round. "
          f"{sum(plain(wo).values()):,} of the {wo['leaf values']:,} leaf values of the {len(bundle.objects):,} objects "
          f"have no source value behind them. The converter writes them on its own and none has a row in the "
          f"ledger: " + "; ".join(f"`{k}` x{v:,}" + (f" ({WHAT[k]})" if k in WHAT else "") for k,v in plain(wo).items())
          + f". The manifest adds {sum(plain(written['manifest']).values()):,} values of its own (digests, the "
          f"paths and versions of the pinned schemas, the converter line), the pinned schemas "
          f"{sum(plain(written['schemas']).values()):,}. Two more limits. The ledger checks the URI of a baseline "
          f"Set against the sec_level of every control that names it; that the Requirement of that control is "
          f"listed in that Set it does not check. And it checks that a rule gives what the file holds, not that "
          f"the rule is the right one: a rule whose function is changed changes the bundle and no figure of the "
          f"ledger. That the bundle is byte for byte the committed one is held apart from it, by the Validators "
          f"workflow, which converts the pinned source again and compares.\n")
md.append("## Full path map\n| path | count | level | destination |\n|---|---:|---|---|")
for p,n,l,t in rows: md.append(f"| `{p}` | {n:,} | {l} | {t} |")
md.append("\n## Per-prop dispatch\n| prop | level | destination |\n|---|---|---|")
for k,(l,t) in PROP_DEST.items(): md.append(f"| `{k}` | {l} | {t} |")
md.append("\n## UNMAPPED (gate target: zero)\n")
if unmapped:
    md.append("| path | count |\n|---|---:|")
    for p,n in unmapped: md.append(f"| `{p}` | {n} |")
else: md.append("*(none)*")
md.append("\n## Declared drops that remain (for the author's decision)\n")
md.append(f"{LT['intentionally-dropped']:,} values. They were declared on 2026-11-14 as classes decided for the IFA "
          f"corpus and stay declared until the author has gone through them; this run adds none. The last column "
          f"is this converter's reading under the author's rule of 2026-11-14 (content is never dropped; no "
          f"content is only a name that selects a field, a namespace, an id that is rebuilt exactly). The decision "
          f"is the author's.\n")
if dropped_rows:
    md.append("| source path | count | declared reason | example value | reading |\n|---|---:|---|---|---|")
    for d in dropped_rows:
        md.append(f"| `{d['path']}` | {d['count']:,} | {d['reason']} | `{d['example-value']}` | {d['reading']} |")
else: md.append("*(none)*")
md.append("\n## Unaccounted source values (conversion ledger)\n")
md.append(f"No destination, no rule by which the value is no content, and no declared reason. A run with one ends "
          f"with a non-zero exit code. The first values of each path are in `{LNAME}` (`unaccounted-paths`).\n")
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
      f"compat oscal-1x on {compat_n} objects")
print("packed list values: " + ", ".join(f"{n} {len(packed[n])}/{list_props[n]}" for n in LIST_PROPS)
      + f" (census gspp tags {CENSUS['packed-tags-gspp']})  controls: {len(all_ids['gspp'])} (census {CENSUS['controls']})")
print(f"parameter slots {{{{Label}}}}: {len(slots)}  at an insertion: {sum(s['at-insert'] for s in slots)}  "
      f"label of a parameter: {sum(s['label-of-a-parameter'] for s in slots)}")
if unmapped:
    print("UNMAPPED:"); [print("  ",p,"x",n) for p,n in unmapped[:30]]
print(f"bundle read back: {BACK['controls']:,} controls -> {BACK['requirements']:,} Requirements; {BACK['links']:,} links -> "
      f"{BACK['links-that-are-a-relation-of-their-own-requirement']:,} relations of their own Requirement; "
      f"{BACK['relations-that-name-no-object']:,} of {BACK['relations']:,} relations name no object")
print(f"ledger: {LEDGER['leaf-values']:,} source values - copied {LT['copied']:,}, transformed {LT['transformed']:,}, "
      f"no content {LT['not-content']:,}, intentionally dropped {LT['intentionally-dropped']:,}, "
      f"unaccounted {LT['unaccounted']:,}; failed checks {len(LFAIL)}")
# the path map and the ledger read one source
if total!=LEDGER["leaf-values"]:
    wiring.append(f"the path map counts {total:,} source leaf values and the ledger {LEDGER['leaf-values']:,}")
# the file on disk is the record of this run, not one an earlier run left there
try:
    with open(LJS,encoding="utf-8") as f: on_disk_record=json.load(f)
except (OSError,ValueError): on_disk_record=None
if on_disk_record!=json.loads(json.dumps(LEDGER)): wiring.append(f"{LNAME} on disk is not the record of this run")
# A claim that does not hold on the written files is a defect of the run:
# the bundle and the record disagree. So is a wiring check that fails, and
# so is a source value that is unaccounted: content is never dropped. The
# bundle, the reports and the record are written by now, and say why.
for x in LFAIL[:20]: print("  LEDGER CHECK FAILED",json.dumps(x,ensure_ascii=False),file=sys.stderr)
for u in LEDGER["unaccounted-paths"][:30]: print(f"  LEDGER UNACCOUNTED {u['path']} x{u['count']}, first {u['pointers'][0]}",file=sys.stderr)
for x in wiring: print("  LEDGER WIRING",x,file=sys.stderr)
if wiring:
    raise SystemExit(f"convert_bsi.py: {len(wiring)} wiring check(s) failed, {len(LFAIL)} claim(s) of the conversion "
                     f"ledger do not hold on the written files, {LT['unaccounted']:,} source value(s) are unaccounted")
ledger_gate(LEDGER,"convert_bsi.py")
