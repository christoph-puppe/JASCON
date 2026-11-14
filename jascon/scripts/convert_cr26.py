#!/usr/bin/env python3
"""FedRAMP CR26 (bespoke JSON) -> Semantic Core bundle. Gate item 1, authority 3.
FRR rules + KSIs -> Requirements; the control links of a KSI and of a rule ->
Mapping objects; subsets/classes/types -> nested Sets; class variance ->
Tailorings (computable deltas) + L2 class-variants payloads (full fidelity);
FRD -> terminology; CTL Rev5 overlay -> a set-parameter Tailoring over the
carried Rev 5 Requirements, its guidance parked L2. Coverage target: 0.
Depends on: convert_nist.py output (the US.SP800-53 bundle).

    convert_cr26.py [--author-ref URI] [--date YYYY-MM-DD]
                    [--obligated-party URI] [--out DIR]

The source is not in the repository and neither is the bundle: the
publisher states no licence (converted_examples/FedRAMP-CR26/
NOT-REDISTRIBUTED.md). The file is read from
sources/cr_fedramp-consolidated-rules.json; where to get it and what its
digest is stands in converted_examples/FedRAMP-CR26/SOURCES.sha256. The
Validators workflow downloads it, converts with --out, runs the reference
validator on the bundle and compares the two coverage reports with the
committed ones. The reports are the record of the conversion.

--out DIR writes the bundle (DIR/cr26-core-bundle) and the two reports to
DIR, so that a run need not touch the repository.

The conversion ledger (backlog #41). The path map above says where a source
PATH is declared to go. The ledger follows every source VALUE, a flag and a
fraction as well as a string: a value the converter hands on unchanged is a
copy, and a value it computes is stated with D(rule, function, inputs...)
so that the rule can be applied to the source again. After the bundle is
written every claim is checked against the files. Real content is never
dropped (author, 2026-11-14). Two classes were declared as drops before that
rule, the update history of an entry and the process-flow diagrams; they
stay declared until the author has decided them, and the report lists them
with the converter's reading. No other drop is declared: a source value
with no destination is unaccounted. The record is
cr26-conversion-ledger.json, one row per source path and outcome, written
beside the two reports.

Exit code: 0 only when every source leaf has a row in the path map, every
claim of the ledger holds against the written files and no source value is
unaccounted. Otherwise the run still writes the bundle, the reports and the
record, which say what is wrong, and exits 1 (backlog #73: until 2026-11-14
the run printed the count of unmapped leaves and exited 0, and nothing
noticed that a new publication had outgrown the converter)."""
import json, hashlib, os, re, sys, copy, collections, shutil, decimal
from oscal_conv_lib import BUNDLE_NEWLINE   # one byte spelling on every OS (D3.1)
from oscal_conv_lib import provenance, provenance_override
from oscal_conv_lib import obligated_party, obligated_party_line, obligated_party_record
from oscal_conv_lib import Ledger, ledger_by_path, ledger_gate, needs_kernel_2
from oscal_conv_lib import COMPAT_FILE, compat_schema, lifecycle_default_record, lifecycle_default_line

NS="https://ns.fedramp.gov/cr26"; NIST="https://ns.nist.gov/sp800-53/req"
ARGV=sys.argv[1:]
# Every argument takes a value. One the converter does not know stops the
# run: a misspelled --out would otherwise write into the repository, and a
# misspelled overwrite would be dropped without a word.
_i=0
while _i<len(ARGV):
    if ARGV[_i] not in ("--author-ref","--date","--obligated-party","--out"):
        raise SystemExit(f"unknown argument {ARGV[_i]!r} (known: --author-ref URI, --date YYYY-MM-DD, "
                         f"--obligated-party URI, --out DIR)")
    _i+=2

# A Mapping's `provenance` is pre-filled from the source (FedRAMP, the day of
# info.last_updated); --author-ref URI and --date YYYY-MM-DD overwrite either
# on every Mapping (backlog #69).
OVERRIDE=provenance_override(ARGV)

# Whom a statement binds where the source names nobody (backlog #74). A rule
# names its parties in `affects`, and those are written as the source has
# them. A KSI has no `affects`; its statement gets this party, and so would
# a rule whose `affects` is absent or empty. --obligated-party URI writes
# the caller's party in the default's place.
PARTY_DEFAULT=f"{NS}/party/provider"
PARTY,PARTY_ORIGIN=obligated_party(ARGV,PARTY_DEFAULT)
PARTY_SOURCE_STATES="in `affects` of a rule"

ROOT=os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..",".."))
SRC=os.path.join(ROOT,"sources","cr_fedramp-consolidated-rules.json")
OUTDIR=os.path.join(ROOT,"converted_examples","FedRAMP-CR26")
if "--out" in ARGV:
    if ARGV.count("--out")>1: raise SystemExit("--out is given more than once")
    if ARGV.index("--out")+1>=len(ARGV): raise SystemExit("--out needs a directory")
    OUTDIR=os.path.abspath(ARGV[ARGV.index("--out")+1])
OUT=os.path.join(OUTDIR,"cr26-core-bundle")
RMD=os.path.join(OUTDIR,"cr26-coverage-report.md")
RJS=os.path.join(OUTDIR,"cr26-coverage-report.json")
LEDGER_FILE="cr26-conversion-ledger.json"
if not os.path.isfile(SRC):
    raise SystemExit(f"missing {SRC} - the source is not in the repository; "
                     f"converted_examples/FedRAMP-CR26/SOURCES.sha256 says where to get it")
F_TERM="https://ns.jascon.net/stdlib/facet/terminology@1"
F_REP="https://ns.jascon.net/stdlib/facet/reporting-obligation@1"
F_EFF="https://ns.jascon.net/stdlib/facet/effectivity@1"
F_ACRIT="https://ns.jascon.net/stdlib/facet/assessment-criteria@1"
F_SCOPE=f"{NS}/facet/scope@1"
F_NARR=f"{NS}/facet/narrative@1"
F_COMPAT="https://ns.jascon.net/compat/oscal-1x@1"
FORCE={"MUST":"must","MUST NOT":"must-not","SHOULD":"should","SHOULD NOT":"should-not","MAY":"may"}
ORDER={"unspecified":0,"may":1,"should":2,"must":3,"should-not":1,"must-not":2,"may-only":2}
AXIS={"must":"o","should":"o","may":"o","may-only":"o","must-not":"p","should-not":"p","unspecified":"n"}
ELAPSED={"seconds","minutes","hours"}; CAL={"days","bizdays","weeks","months","years"}

def w(p,o):
    fp=os.path.join(OUT,p); os.makedirs(os.path.dirname(fp),exist_ok=True)
    with open(fp,"w",encoding="utf-8",newline=BUNDLE_NEWLINE) as f: f.write(json.dumps(o,indent=1,ensure_ascii=False)+"\n")
def shaf(p): return "sha256:"+hashlib.sha256(open(os.path.join(OUT,p),"rb").read()).hexdigest()
def _canon(o):
    if isinstance(o, dict):
        return {k: _canon(o[k]) for k in sorted(o.keys(), key=lambda s: s.encode("utf-16-be"))}
    if isinstance(o, list):
        return [_canon(x) for x in o]
    return o

def sdig(o):
    o=copy.deepcopy(o); o.pop("annotations",None)
    return "sha256:"+hashlib.sha256(json.dumps(_canon(o),separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def slug(s):
    s = re.sub(r"[^a-z0-9]+","-",(s or "").lower()).strip("-")
    if len(s) <= 60: return s or "x"
    return s[:52].rstrip("-") + "-" + hashlib.sha256(s.encode()).hexdigest()[:7]   # P10 #39: no bare truncation

LANG="en"   # corpus language: payload free text is language-tagged {LANG: value}
lang_wraps=collections.Counter()
def T(v,field=None):
    """Wrap payload free text (str or list of str) in the corpus language
    (backlog #12 harmonization). Identifiers/labels are never passed here."""
    if v is None: return v
    lang_wraps[field or "?"]+=1
    return {LANG:v}

# The conversion ledger. Every string and integer of the source carries its
# origin from here on (document tag and JSON Pointer), for as long as it is
# handed on unchanged; a computed value loses it, and D() states the rule that
# made it. The source keys everything by id (a family, a subset, a rule, a
# term), so its paths are collapsed as the path map collapses them: the
# ledger and the path map then count the same paths.
class _Ledger(Ledger):
    @staticmethod
    def collapsed(tag,parts): return normalize(Ledger.collapsed(tag,parts))
led=_Ledger(); D=led.derive

# The source is loaded with its flags and its fractions followed too
# (typed=True): a flag stands in the objects as a value that knows its origin
# until led.resolve() puts the plain boolean in its place, before anything is
# written or digested.
#
# A number of the source that is no integer is a float here, because a float
# is what the ledger can follow, and it is written as a decimal string, the
# kernel's spelling of a fraction (NUMBER-1, D3.9): the shortest one that
# gives the number back. The same file is read a second time with the digits
# as the source wrote them, and the run stops if a float does not hold one of
# its numbers exactly.
with open(SRC,encoding="utf-8") as _f: _text=_f.read()
def _exact(a,b,where):
    if isinstance(a,dict):
        for k in a: _exact(a[k],b[k],f"{where}/{k}")
    elif isinstance(a,list):
        for i,x in enumerate(a): _exact(x,b[i],f"{where}/{i}")
    elif isinstance(a,decimal.Decimal) and decimal.Decimal(repr(b))!=a:
        raise SystemExit(f"{where}: the number {a} of the source has more digits than a float holds ({b!r}); "
                         f"the converter would write another number")
_loaded=json.loads(_text)
_exact(json.loads(_text,parse_float=decimal.Decimal),_loaded,"cr26#")
d=led.source("cr26",_loaded,typed=True)
VER=d["info"]["version"]

def flag(v):
    """-> True or False for a boolean of the source, as the ledger hands it on
    or plain; None for any other value. (A flag that is followed is not the
    object `True`, so `v is True` does not know it; 1 and "true" are no flags.)"""
    if isinstance(v,bool): return v
    if isinstance(v,(int,float,str,decimal.Decimal,dict,list)) or v is None: return None
    return True if v==True else False if v==False else None

DECIMAL=re.compile(r"(-?[1-9][0-9]*(\.[0-9]+)?|0(\.[0-9]+)?|-0\.[0-9]*[1-9][0-9]*)\Z")   # the kernel's decimalString
def _decimal_string(number):
    s=format(decimal.Decimal(repr(float(number))),"f")
    if not DECIMAL.match(s): raise SystemExit(f"the number {number!r} has no decimal spelling of the kernel (D3.9)")
    return s
R_DECIMAL="decimal string of a number that is no integer (the kernel's spelling of a fraction, D3.9)"
fraction_paths=collections.Counter()
def park(n,path):
    """A payload parked as the source has it (L2), with one difference: a
    number that is no integer is written as a decimal string, the kernel's
    spelling of a fraction (D3.9). Counted by source path. -> a new structure."""
    if isinstance(n,dict): return {k:park(v,f"{path}.{k}") for k,v in n.items()}
    if isinstance(n,list): return [park(v,f"{path}[]") for v in n]
    if isinstance(n,float):
        fraction_paths[normalize(path)]+=1
        return D(R_DECIMAL,_decimal_string,n)
    return n
def no_fraction(n,where):
    """Stops the run at a number that is no integer anywhere but in a parked
    payload: a kernel number is an integer (NUMBER-1), and no destination
    is declared for a fraction there."""
    if isinstance(n,dict):
        for k,v in n.items(): no_fraction(v,f"{where}/{k}")
    elif isinstance(n,list):
        for i,v in enumerate(n): no_fraction(v,f"{where}/{i}")
    elif isinstance(n,(decimal.Decimal,float)):
        raise SystemExit(f"{where}: the number {n} is no integer and this place has no decimal spelling "
                         f"(NUMBER-1, D3.9); the converter declares no destination for it")

# ---------------- coverage inventory with path normalization ----------------
def normalize(p):
    p=re.sub(r"^cr26\.FRR\.[A-Z0-9]{2,4}(?=\.)","cr26.FRR.*",p)
    p=re.sub(r"(FRR\.\*\.data)\.(all|20x|rev5)","\\1.*",p,count=1)
    p=re.sub(r"(FRR\.\*\.data\.\*)\.[^.]+","\\1.*",p,count=1)
    p=re.sub(r"(FRR\.\*\.data\.\*\.\*)\.[^.]+","\\1.*",p,count=1)
    p=re.sub(r"^cr26\.KSI\.[A-Z]{2,4}(?=\.)","cr26.KSI.*",p)
    p=re.sub(r"(KSI\.\*\.indicators)\.[^.]+","\\1.*",p,count=1)
    p=re.sub(r"^cr26\.FRD\.data\.all\.[^.]+","cr26.FRD.data.all.*",p)
    p=re.sub(r"^cr26\.CTL\.[A-Z]{2}\.[^.]+","cr26.CTL.*.*",p)
    p=re.sub(r"\.varies_by_class\.[a-d](?=\.|$)",".varies_by_class.*",p)
    p=re.sub(r"\.subsets\.[A-Z0-9]+(?=\.|$)",".subsets.*",p)
    # the nodes of a flow diagram are keyed by a rule id or by a phrase of the
    # publication; until 2026-11-14 the path map printed each key, two phrases
    # among them, and the reports are to reproduce no text of the publication
    p=re.sub(r"(\.info\.flows\[\]\.nodes)\..*$","\\1.*",p,flags=re.S)
    return p
paths=collections.Counter()
def inv(n,pref):
    if isinstance(n,dict):
        for k,v in n.items(): inv(v,f"{pref}.{k}")
    elif isinstance(n,list):
        for v in n: inv(v,f"{pref}[]")
    else: paths[normalize(pref)]+=1
inv(d,"cr26")

RULE="cr26.FRR.*.data.*.*.*"; VAR=RULE+".varies_by_class.*"
ESC=lambda x:re.escape(x)
KSI="cr26.KSI.*.indicators.*"; KVAR=KSI+".varies_by_class.*"
# The path map: (pattern over a collapsed source path, level, destination).
# Levels: L1 a kernel field or a facet with a schema; L2 a payload parked as
# the source has it; DROP the path is not carried, and the destination column
# says why - the ledger declares exactly these rows as drops, with that
# reason. Since 2026-11-14 the ledger holds the map to what is written: a row
# that is L1 or L2 while a value of its path reaches no file is reported as a
# claim that does not hold, and the run ends with 1 on a value that is
# neither carried nor dropped for a declared reason (backlog #41).
#
# No drop is declared since 2026-11-14: the author decided the two that were
# left. The update history of an entry is carried with the entry, and the
# process flow of a family, which the source writes out, on the family's Set.
DROP="declared-drop"
DROP_READING={}
def add_history(obj,entries):
    """The update history of a rule or an indicator (date, comment, issue), as the source writes it: the kernel
    has the version of an object and no member for what changed when, so it stands in the compat facet."""
    if entries: obj.setdefault("facets",{}).setdefault(F_COMPAT,{})["history"]=entries
RULES=[
 (r"^cr26\.info\.title$","L1","the manifest's provenance (source) and the title of the corpus root Set"),
 (r"^cr26\.info\.description$","L1","narrative@1 on the corpus root Set: description"),
 (r"^cr26\.info\.version$","L1","the manifest's provenance (source-version) and `version` of every object made from the publication"),
 (r"^cr26\.info\.last_updated$","L1","the manifest's provenance (last_updated) and the date of every Mapping's provenance"),
 (r"^cr26\.info\.default_artifacts\.","L1","assessment-criteria on corpus root: default-artifacts"),
 (r"^cr26\.FRD\.info\.","L1","terminology@1 glossary-info on the corpus root Set"),
 (r"^cr26\.FRD\.data\.all\.\*\.(term|definition|tag|alts\[\]|note|notes\[\]|do_not_link|reference|reference_url)$","L1","terminology@1 payload per term (alts, links, chrome flags inside payload)"),
 (r"^cr26\.FRD\.data\.all\.\*\.ignore_in_terms$","L1","narrative@1 on the corpus root Set: ignore-in-terms {term id: flag} (terminology@1 has do-not-link and no member for this one)"),
 (r"^cr26\.FRD\.data\.all\.\*\.updated\[\]\.","L2","narrative@1 on the corpus root Set: term-updated {term id: the entries as the source writes them} (terminology@1 has no member for the history of a term)"),
 (r"^cr26\.FRR\.\*\.info\.(name|short_name)$","L1","family Set: title/label"),
 (r"^cr26\.FRR\.\*\.info\.status$","L1","the family Set's `lifecycle` by the rule for a document's status, the lifecycle of every object made from the family (subset Sets, rules, Mappings of their control links), and the word itself in narrative@1 of the family Set: status"),
 (r"^cr26\.FRR\.\*\.info\.web_name$","L1","family Set annotations.web_name (chrome)"),
 (r"^cr26\.FRR\.\*\.info\.(purpose|tag)$","L1","family Set: narrative description / scope tag"),
 (r"^cr26\.FRR\.\*\.info\.(20x|rev5)\.subsets\.","L1","framework-specific subset declarations -> track subset Sets (title/description/scope) [corrected per FedRAMP #153]"),
 (r"^cr26\.FRR\.\*\.info\.(effective|20x|rev5)\.","L1","effectivity@1 on family Set (default / per-track)"),
 (r"^cr26\.FRR\.\*\.info\.flows\[\]","L2","compat facet on the family Set: flows, as the source writes them (D17 as amended on 2026-11-14: a flow the source writes out is carried)"),
 (r"^cr26\.FRR\.\*\.info\.subsets\.\*\.(name|description)$","L1","subset Set: title / narrative description"),
 (r"^cr26\.FRR\.\*\.info\.subsets\.\*\.applicability\.","L1","scope@1 on subset Set (types/paths/classes/affects) + class & type Set composition"),
 (re.escape(RULE)+r"\.name$","L1","Requirement.title"),
 (re.escape(RULE)+r"\.statement$","L1","statements[0].prose.en"),
 (re.escape(RULE)+r"\.force$","L1","statements[0].modality (code map)"),
 (re.escape(RULE)+r"\.affects\[\]$","L1","statements[0].obligated-parties[]"),
 (re.escape(RULE)+r"\.terms\[\]$","L1","relations uses-term -> /cr26/term/<id>"),
 (re.escape(RULE)+r"\.(timeframe_num|timeframe_type)$","L1","statement parameter 'timeframe' (elapsed-duration or calendar-period, by unit); timeframe_type is the unit of every timeframe parameter of the rule"),
 (re.escape(RULE)+r"\.timeframe_num_(min|max)$","L1","statement parameters 'timeframe-min' / 'timeframe-max': a range is its two bounds, each a duration of the kernel (unit from timeframe_type)"),
 (re.escape(RULE)+r"\.controls\[\]$","L1","Mapping objects (relationship supports; 8.6 untyped-import rule), as for a KSI"),
 (re.escape(RULE)+r"\.updated\[\]\.","L2","compat facet on the rule's Requirement: history, the entries as the source writes them"),
 (re.escape(RULE)+r"\.(note|notes\[\]|danger|corrective_actions\[\])$","L1","narrative@1: note / notes / danger / corrective-actions"),
 (re.escape(RULE)+r"\.(following_information\[\]|following_information_bullets\[\])$","L1","reporting-obligation@1: following-information / following-information-bullets"),
 (re.escape(RULE)+r"\.examples\[\]\.(id|examples\[\]|key_tests\[\])$","L1","assessment-criteria@1: examples[] {id, examples, key-tests} - the KSI-shaped test data"),
 (re.escape(RULE)+r"\.schema\.(name|url)$","L1","relations schema -> url; name kept in narrative@1"),
 (re.escape(RULE)+r"\.notification\[\]\.(party|method|target|name)$","L1","reporting-obligation@1: notification[]; of an entry the source marks optional: narrative@1 optional-notification[]"),
 (re.escape(RULE)+r"\.notification\[\]\.optional$","L1","narrative@1: optional-notification[] - the entry goes there whole, with its flag (reporting-obligation@1 lists duties and has no member for an optional one)"),
 (re.escape(RULE)+r"\.artifacts\.all\[\]$","L1","assessment-criteria@1: required-artifacts"),
 (re.escape(RULE)+r"\.artifacts\.[a-d]\[\]$","L2","class-variants payload (per-class artifacts)"),
 (re.escape(RULE)+r"\.related\[\]$","L1","relations related -> /cr26/req/<id> (dangling counted)"),
 (re.escape(RULE)+r"\.(schema|reference_url)$","L1","relation `schema` / `reference` -> the external URL"),
 (re.escape(RULE)+r"\.reference$","L1","narrative@1: reference, the label of the citation (the map read \"relations ... -> external URL\" until 2026-11-14; the URL of the relation is reference_url)"),
 (re.escape(VAR)+r"\.force$","L1","class Tailoring op set-modality (monotone) OR + converter Deviation when easing (counted)"),
 (re.escape(VAR)+r"\.(timeframe_num|timeframe_type)$","L2","class-variants payload; and a class Tailoring op set-parameter where the rule itself states a timeframe of the same unit class - the conversion rules above count the ops (the row was marked L1 until 2026-11-14, though a value reaches an operation only in that case)"),
 (re.escape(VAR)+r"\.","L2","class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question)"),
 (re.escape(KSI)+r"\.name$","L1","KSI Requirement.title"),
 (re.escape(KSI)+r"\.statement$","L1","KSI statements[0].prose.en (modality unspecified: indicator language)"),
 (re.escape(KSI)+r"\.controls\[\]$","L1","Mapping objects (relationship supports; 8.6 untyped-import rule)"),
 (re.escape(KSI)+r"\.terms\[\]$","L1","relations uses-term"),
 (re.escape(KSI)+r"\.updated\[\]\.","L2","compat facet on the indicator's Requirement: history, the entries as the source writes them"),
 (re.escape(KVAR)+r"\.","L2","class-variants payload on the KSI Requirement"),
 (r"^cr26\.KSI\.\*\.(name|web_name|short_name)$","L1","KSI category Set: title / annotations.web_name / label"),
 (r"^cr26\.KSI\.\*\.id$","L1","KSI category Set: aliases[] (the theme's own id; the Set's URI is minted from the key the theme stands under)"),
 (r"^cr26\.KSI\.\*\.status$","L1","the KSI category Set's `lifecycle` by the rule for a document's status, the lifecycle of its indicators and of the Mappings of their control links, and the word itself in narrative@1 of the category Set: status"),
 (r"^cr26\.CTL\.\*\.\*\.parameters\[\]\.","L1","CTL ODP assignments -> set-parameter ops on the rev5-odp-overlay Tailoring, statement-addressed via the declaring statement; tailored Rev 5 Requirements carried in-bundle (backlog #10 DRAINED, gate 3)"),
 (r"^cr26\.CTL\.\*\.\*\.","L2","CTL guidance/variants: parked payload on /cr26/set/ctl-overlay - FedRAMP supplemental prose on external controls (D20 supplements territory, not ODP addressing)"),
]
def dest(p):
    for pat,l,t in RULES:
        if re.search(pat,p): return l,t
    return None,None

# ---------------- conversion ----------------
objects={}; counters=collections.Counter(); dev_records=0; ops_emitted=collections.Counter()
mod_hist=collections.Counter(); synth_prose=0; dangling_related=0; mappings=0
# ---- the rules of the ledger: what the converter computes from a source
# value. Each is a pure function of source values and of tables that do not
# change during a run; the ledger applies it to the source again after the
# bundle is written and compares the result with the file. A rule's name is
# what the record prints.
def _modality(force): return FORCE.get(force,"unspecified")
def _party(name): return f"{NS}/party/{slug(name)}"
def _related_uri(rid): return f"{NS}/req/{rid}"
def _map_id(owner,ctl): return f"{NS}/map/{slug(owner)}--{slug(ctl)}"
def _control_uri(ctl): return f"{NIST}/{ctl.upper()}"
def _duration_type(unit): return "elapsed-duration" if unit in ELAPSED else "calendar-period"
def _selections(value): return [x.strip() for x in re.split(r";|,| and ",value) if x.strip()]
def _rule_prose(name): return f"{name} (requirement varies by certification class; see class tailorings and the class-variants payload)."
def _ksi_prose(name): return f"{name} (indicator varies by certification class; see class-variants payload)."
R_MODALITY="modality from the force word (code map)"
R_PARTY="party URI from a name in affects"
R_TERM="term URI from the term's name, by the glossary's headwords and alternatives"
R_RELATED="Requirement URI from the id of a related rule"
R_MAP_ID="Mapping id from its owner's id and the control id"
R_CONTROL="SP 800-53 Requirement URI from the control id"
R_DURATION="duration type from the unit of the timeframe"
R_SELECTION="one selection of a multi-select that the source writes as one string"
R_RULE_PROSE="base prose of a rule that states its text by class only, from its name"
R_KSI_PROSE="base prose of an indicator that states its text by class only, from its name"
R_TRACK_TITLE="title of one track's share of a subset, from the subset's name"

# The status of a document, and the kernel's lifecycle. The publisher gives a
# family, the glossary and a KSI theme a status of three words (its schema:
# `document_status`: stable, placeholder, empty; its AGENTS.md: "FRD and FRR
# status is under their document info.status; KSI status is
# KSI.<theme>.status", read 2026-11-14 at the publication's tag). The kernel's
# lifecycle knows draft, active, deprecated, withdrawn. Until 2026-11-14 the
# converter read no status and wrote `active` on everything, a family the
# source marks `placeholder` and its rules among them.
#
# The mapping is the converter's and is stated as a rule: `stable` is the
# source's word for a document that is settled and is written `active`;
# `placeholder` and `empty` are its words for a document that is not, and
# `draft` is the only state of the kernel that says so (deprecated and
# withdrawn say that something has ended). The source's own word is kept
# beside the mapped state, in narrative@1 of the Set that stands for the
# document: the kernel has no place for it. A word outside the three stops
# the run.
#
# Whose status it is. The status is the document's, and a document of this
# source is its `info` and its `data`: the rules, or a theme's indicators.
# No rule and no indicator has a status of its own. The publisher tells a
# reader to check the document's status before reading an entry of it. So
# the lifecycle of every object made from a document follows the document's
# status: the Set of the family or theme, its subset Sets, its rules or
# indicators, and the Mappings made of their control links. A rule of a
# placeholder family is not written `active`: the source does not call it so.
KSI_ID_SCHEME="fedramp-cr26:KSI.id"        # the alias scheme: the member of the publication the value is read from
STATUS_LIFECYCLE={"stable":"active","placeholder":"draft","empty":"draft"}
def _lifecycle(status):
    if status not in STATUS_LIFECYCLE:
        raise SystemExit(f"a document has the status {status!r}: the converter maps stable, placeholder and empty to a "
                         f"lifecycle and guesses at no other word")
    return STATUS_LIFECYCLE[status]
R_LIFECYCLE="lifecycle of the Set that stands for a document, from the document's status (stable: active; placeholder, empty: draft)"
R_MEMBER_LIFECYCLE=("lifecycle of an object made from a document (a subset Set, a rule or an indicator, a Mapping of "
                    "its control links), from the document's status (stable: active; placeholder, empty: draft)")
def lifecycle_of(status,rule):
    """-> the lifecycle for an object of a document with this status. A
    document that states none is not known to be settled: `draft`, counted."""
    if status is None:
        counters["objects-of-a-document-without-status"]+=1
        return "draft"
    return D(rule,_lifecycle,status)

def tf_param(num,typ,name="timeframe",tightening="lower"):
    t=D(R_DURATION,_duration_type,typ)
    p={"name":name,"type":t,"num":num,"unit":typ,"tightening":tightening}
    if t=="calendar-period": p["calendar-ref"]=f"{NS}/calendar/us-federal"
    return p,t
# A rule states either one timeframe (timeframe_num) or a range
# (timeframe_num_min and timeframe_num_max, both in timeframe_type). The
# kernel's durations have one `num`, and its `range` is a container of
# scalars, which a duration is not (D9). A range is therefore written as its
# two bounds, each a duration with its unit and calendar. The window narrows
# when its floor rises or its ceiling falls: that is the tightening declared.
TF_BOUNDS=(("timeframe_num_min","timeframe-min","higher"),("timeframe_num_max","timeframe-max","lower"))

def control_mappings(owner,uri,controls,rationale,status):
    """The control links of a KSI or of a rule -> one Mapping each. The source
    types both lists alike (an array of control ids) and states no
    relationship, so the untyped-import rule applies to both. `status`: of
    the document the owner stands in."""
    global mappings
    for ctl in controls or []:
        rel=f"objects/map/{slug(owner)}--{slug(ctl)}.json"
        if rel in objects: raise SystemExit(f"{owner}: the control link {ctl!r} is written twice; two links would become one Mapping")
        objects[rel]={"id":D(R_MAP_ID,_map_id,owner,ctl),"version":VER,"lifecycle":lifecycle_of(status,R_MEMBER_LIFECYCLE),
           "source-ref":uri,"target-ref":D(R_CONTROL,_control_uri,ctl),
           "relationship":"supports","direction":"source-to-target","confidence":"draft",
           "rationale":rationale,
           "provenance":provenance(f"{NS}/party/fedramp",d["info"]["last_updated"],OVERRIDE)}
        mappings+=1

TERMIDX={}
for _tid,_t in d["FRD"]["data"]["all"].items():
    for _n in [_t["term"]]+list(_t.get("alts",[]) or []):
        TERMIDX.setdefault(_n.lower().strip(),_tid)
def _term_uri(name):
    tid=TERMIDX.get(name.lower().strip())
    return f"{NS}/term/{tid}" if tid else f"{NS}/term/{slug(name)}"
def term_ref(name):
    if not TERMIDX.get(name.lower().strip()): counters["unresolved-terms"]+=1    # counted here: the rule itself is applied twice
    return D(R_TERM,_term_uri,name)

class_tailorings={c:{"id":f"{NS}/tailoring/class-{c}","version":VER,"lifecycle":"active",
    "label":f"Class {c.upper()}","title":f"Class {c.upper()} certification variant",
    "selects":[{"set-ref":f"{NS}/set/class/{c}"}],"operations":[]} for c in "abcd"}

def add_narr(req,key,val):
    req.setdefault("facets",{}).setdefault(F_NARR,{})[key]=val

def convert_rule(fam,trk,subk,rid,r,status):
    global synth_prose,dangling_related,dev_records
    uri=f"{NS}/req/{rid}"
    req={"id":uri,"version":VER,"label":rid,"lifecycle":lifecycle_of(status,R_MEMBER_LIFECYCLE),
         "title":r.get("name",rid),"statements":[]}
    base_force=r.get("force"); mod=D(R_MODALITY,_modality,base_force) if base_force is not None else "unspecified"
    prose=r.get("statement")
    if prose is None:
        prose=D(R_RULE_PROSE,_rule_prose,r.get("name",rid))
        synth_prose+=1
    stated=[D(R_PARTY,_party,a) for a in r.get("affects") or []]
    counters["statements-party-from-affects" if stated else "statements-party-fallback"]+=1
    st={"id":"s1","modality":mod,
        "obligated-parties":stated or [PARTY],
        "prose":{"en":prose}}
    mod_hist[mod]+=1
    base_tf=None; params=[]
    if "timeframe_num" in r:
        p,base_tf=tf_param(r["timeframe_num"],r["timeframe_type"]); params.append(p)
    for key,name,tightening in TF_BOUNDS:
        if key in r:
            params.append(tf_param(r[key],r["timeframe_type"],name,tightening)[0])
            counters["timeframe-range-bounds"]+=1
    if params: st["parameters"]=params
    req["statements"].append(st)
    rels=[{"type":"uses-term","ref":term_ref(t)} for t in r.get("terms",[])]
    for rl in r.get("related",[]) or []:
        if re.match(r"^[A-Z]{2,4}-[A-Z]{2,4}-[A-Z0-9]{2,4}$",rl):
            rels.append({"type":"related","ref":D(R_RELATED,_related_uri,rl)})
        else:
            rels.append({"type":"related","ref":rl}); dangling_related+=1
    if isinstance(r.get("schema"),dict):
        rels.append({"type":"schema","ref":r["schema"].get("url","")})
        add_narr(req,"schema-name",r["schema"].get("name"))
    elif r.get("schema"): rels.append({"type":"schema","ref":r["schema"]})
    if r.get("reference_url"): rels.append({"type":"reference","ref":r["reference_url"]})
    if rels: req["relations"]=rels
    # reporting-obligation@1 lists notification duties (it declares that it
    # alters what passing means) and its entries have no member `optional`.
    # An entry the source marks optional is no duty. It goes whole, with its
    # flag, to the converter's narrative@1, so that the standard facet states
    # the duties and nothing else. The source writes the flag only as `true`;
    # any other value has no declared destination and stops the run.
    rep={}; duties=[]; optional=[]
    for n in copy.deepcopy(r.get("notification") or []):
        if n.get("name"): n["name"]=T(n["name"],"notification-name")
        if "optional" not in n: duties.append(n)
        elif flag(n["optional"]) is True: optional.append(n)
        else: raise SystemExit(f"{rid}: notification.optional is {n['optional']!r}; the converter knows only `true`")
    if duties: rep["notification"]=duties
    if optional:
        add_narr(req,"optional-notification",optional); counters["optional-notifications"]+=len(optional)
    if r.get("following_information"): rep["following-information"]=r["following_information"]
    if r.get("following_information_bullets"): rep["following-information-bullets"]=r["following_information_bullets"]
    if rep: req.setdefault("facets",{})[F_REP]=rep
    ac={}
    if isinstance(r.get("artifacts"),dict) and r["artifacts"].get("all"):
        ac["required-artifacts"]=r["artifacts"]["all"]
    if r.get("examples"):
        ac["examples"]=[{"id":e.get("id"),"examples":e.get("examples",[]),
                         "key-tests":e.get("key_tests",[])} for e in r["examples"]]
    if ac: req.setdefault("facets",{})[F_ACRIT]=ac
    for k,fld in [("note","note"),("notes","notes"),("danger","danger"),
                  ("corrective_actions","corrective-actions")]:
        if r.get(k): add_narr(req,fld,T(r[k],fld))
    if r.get("reference"): add_narr(req,"reference",r["reference"])
    counters["updated-entries"]+=len(r.get("updated",[]) or [])
    # class variance
    var=r.get("varies_by_class")
    if var:
        req.setdefault("facets",{})[F_COMPAT]={"class-variants":
            park(var,f"cr26.FRR.{fam}.data.{trk}.{subk}.{rid}.varies_by_class")}
        counters["class-variant-rules"]+=1
        for cls,v in var.items():
            OPS=class_tailorings[cls]["operations"]
            vf=FORCE.get(v.get("force"))
            if vf and vf!=mod:
                op={"op":"set-modality","requirement-ref":uri,"statement-id":"s1","modality":D(R_MODALITY,_modality,v["force"])}
                easing = AXIS[vf]!=AXIS[mod] or ORDER[vf]<ORDER[mod] or mod=="unspecified" and False
                monotone = AXIS[vf]==AXIS[mod] and ORDER[vf]>=ORDER[mod] or mod=="unspecified"
                if not monotone:
                    op["deviation"]={"type":"derogation","state":"approved",
                        "rationale":"Authority-published class variant (CR26 varies_by_class).",
                        "approver-ref":f"{NS}/party/fedramp","opened":d["info"]["last_updated"]}
                    dev_records+=1
                OPS.append(op); ops_emitted["set-modality"]+=1
            if "timeframe_num" in v:
                _,vt=tf_param(v["timeframe_num"],v["timeframe_type"])
                if base_tf is None:
                    counters["timeframe-variant-only"]+=1
                elif base_tf==vt:
                    OPS.append({"op":"set-parameter","requirement-ref":uri,"statement-id":"s1",
                              "parameter":"timeframe",
                              "value":{"type":vt,"num":v["timeframe_num"],"unit":v["timeframe_type"]}})
                    ops_emitted["set-parameter"]+=1
                else:
                    counters["timeframe-unitclass-crossings"]+=1
    add_history(req,r.get("updated"))
    objects[f"objects/req/{slug(rid)}.json"]=req
    n=mappings
    control_mappings(rid,uri,r.get("controls"),
        "Imported from the control list of a CR26 rule; the source carried no typed relationship (handbook 8.6).",status)
    counters["rule-control-mappings"]+=mappings-n
    return uri

def convert_ksi(catid,cat,iid,ind):
    global mappings
    uri=f"{NS}/ksi/{iid}"
    prose=ind.get("statement")
    if prose is None:
        prose=D(R_KSI_PROSE,_ksi_prose,ind.get("name",iid))
    status=cat.get("status")
    req={"id":uri,"version":VER,"label":iid,"lifecycle":lifecycle_of(status,R_MEMBER_LIFECYCLE),
         "title":ind.get("name",iid),
         "statements":[{"id":"s1","modality":"unspecified",
             "obligated-parties":[PARTY],"prose":{"en":prose}}]}
    counters["statements-party-fallback"]+=1
    rels=[{"type":"uses-term","ref":term_ref(t)} for t in ind.get("terms",[])]
    if rels: req["relations"]=rels
    if ind.get("varies_by_class"):
        req["facets"]={F_COMPAT:{"class-variants":
            park(ind["varies_by_class"],f"cr26.KSI.{catid}.indicators.{iid}.varies_by_class")}}
        counters["ksi-class-variant"]+=1
    counters["updated-entries"]+=len(ind.get("updated",[]) or [])
    add_history(req,ind.get("updated"))
    objects[f"objects/ksi/{slug(iid)}.json"]=req
    n=mappings
    control_mappings(iid,uri,ind.get("controls"),
        "Imported from CR26 KSI control list; the source carried no typed relationship (handbook 8.6).",status)
    counters["ksi-control-mappings"]+=mappings-n
    return uri

# in-place overwrite; stale-file cleanup happens after the write set is known
# (house rule: never rmtree/rmdir - OneDrive/indexers hold transient dir handles)
seq={"n":0}
def nseq(): seq["n"]+=10; return seq["n"]
class_members=collections.defaultdict(list); type_members=collections.defaultdict(list)
fam_entries=[]
for fk,f in d["FRR"].items():
    fi=f["info"]; sub_entries=[]
    status=fi.get("status")        # of the family as a document; every object made from it follows it
    common=fi.get("subsets",{})
    # FedRAMP layering (global by default, specific when needed): framework-
    # specific subsets are declared in info.20x.subsets / info.rev5.subsets.
    # Corrected after review in FedRAMP community discussion #153.
    track_decl={trk:((fi.get(trk) or {}).get("subsets") or {}) for trk in ("20x","rev5")}
    all_sks=list(dict.fromkeys(list(common)
        +[sk for td in track_decl.values() for sk in td]
        +[sk for tv in f["data"].values() for sk in tv]))
    for sk in all_sks:
        sinfo=common.get(sk)
        t_infos={trk:td[sk] for trk,td in track_decl.items() if sk in td}
        if t_infos and sinfo is None:
            counters["track-declared-subsets"]+=len(t_infos)
        members=[]
        for rid,r in f["data"].get("all",{}).get(sk,{}).items():
            members.append({"ref":convert_rule(fk,"all",sk,rid,r,status),"sequence":nseq()})
        track_set_uris=[]
        for trk in ("20x","rev5"):
            tr_rules=f["data"].get(trk,{}).get(sk,{})
            if not tr_rules: continue
            tinfo=t_infos.get(trk,{})
            turi=f"{NS}/set/subset/{slug(fk)}-{slug(sk)}-{trk}"
            tmem=[{"ref":convert_rule(fk,trk,sk,rid,r,status),"sequence":(i+1)*10}
                  for i,(rid,r) in enumerate(tr_rules.items())]
            tset={"id":turi,"version":VER,"lifecycle":lifecycle_of(status,R_MEMBER_LIFECYCLE),
                "title":tinfo["name"] if "name" in tinfo else
                        D(R_TRACK_TITLE,lambda n,t=trk: f"{n} ({t}-specific)",(sinfo or {}).get("name",sk)),
                "label":sk if tinfo else f"{sk}-{trk}",
                "members":tmem}
            tap=tinfo.get("applicability",{})
            if tinfo.get("description"):
                tset.setdefault("facets",{}).setdefault(F_NARR,{})["description"]=T(tinfo["description"],"description")
            if tap: tset.setdefault("facets",{})[F_SCOPE]=dict(tap)
            objects[f"objects/set/subset-{slug(fk)}-{slug(sk)}-{trk}.json"]=tset
            track_set_uris.append(turi)
            type_members[slug(trk)].append(turi)
            for c in tap.get("classes",[]) or []: class_members[c.lower()].append(turi)
            counters[f"track-rules-{trk}"]+=len(tmem)
        if sinfo is None and track_set_uris and not members:
            # purely framework-specific subset: the track Sets stand alone,
            # attached directly to the family - no synthetic parent Set
            for turi in track_set_uris:
                sub_entries.append({"ref":turi,"sequence":nseq()})
            continue
        for turi in track_set_uris:
            members.append({"ref":turi,"sequence":nseq()})
        if not members: counters["empty-subsets"]+=1; continue
        suri=f"{NS}/set/subset/{slug(fk)}-{slug(sk)}"
        sinfo=sinfo or {}
        sobj={"id":suri,"version":VER,"lifecycle":lifecycle_of(status,R_MEMBER_LIFECYCLE),
              "title":sinfo.get("name",sk),"label":sk,"members":members}
        ap=sinfo.get("applicability",{})
        if sinfo.get("description"): sobj.setdefault("facets",{}).setdefault(F_NARR,{})["description"]=T(sinfo["description"],"description")
        if ap: sobj.setdefault("facets",{})[F_SCOPE]=dict(ap)
        objects[f"objects/set/subset-{slug(fk)}-{slug(sk)}.json"]=sobj
        sub_entries.append({"ref":suri,"sequence":nseq()})
        for c in ap.get("classes",[]) or []: class_members[c.lower()].append(suri)
        for t in ap.get("types",[]) or []: type_members[slug(t)].append(suri)
    furi=f"{NS}/set/tax/{slug(fk)}"
    fobj={"id":furi,"version":VER,"lifecycle":lifecycle_of(status,R_LIFECYCLE),
          "title":fi.get("name",fk),"label":fi.get("short_name",fk),
          "members":sub_entries,"annotations":{"web_name":fi.get("web_name","")}}
    narr={"description":T(fi.get("purpose",""),"description")}
    if status is not None: narr["status"]=status        # the source's own word, beside the lifecycle it was mapped to
    fobj["facets"]={F_NARR:narr,F_SCOPE:{"tag":fi.get("tag")}}
    eff={}
    if fi.get("effective"): eff["default"]=fi["effective"]
    for trk in ("20x","rev5"):
        if fi.get(trk): eff[trk]=fi[trk].get("effective",fi[trk])
    if eff: fobj["facets"][F_EFF]=eff
    if fi.get("flows"):
        fobj["facets"][F_COMPAT]={"flows":fi["flows"]}; counters["flows"]+=len(fi["flows"])
    objects[f"objects/set/tax-{slug(fk)}.json"]=fobj
    fam_entries.append({"ref":furi,"sequence":nseq()})
for c,mem in sorted(class_members.items()):
    objects[f"objects/set/class-{c}.json"]={"id":f"{NS}/set/class/{c}","version":VER,
        "lifecycle":"active","title":f"Class {c.upper()} scope",
        "members":[{"ref":m,"sequence":(i+1)*10} for i,m in enumerate(sorted(set(mem)))]}
for t,mem in sorted(type_members.items()):
    objects[f"objects/set/type-{t}.json"]={"id":f"{NS}/set/type/{t}","version":VER,
        "lifecycle":"active","title":f"Track: {t}",
        "members":[{"ref":m,"sequence":(i+1)*10} for i,m in enumerate(sorted(set(mem)))]}
ksi_cat_entries=[]
for ck,cat in d["KSI"].items():
    entries=[{"ref":convert_ksi(ck,cat,iid,ind),"sequence":nseq()}
             for iid,ind in cat["indicators"].items()]
    curi=f"{NS}/set/ksi/{slug(ck)}"
    cobj={"id":curi,"version":VER,"lifecycle":lifecycle_of(cat.get("status"),R_LIFECYCLE),
        "title":cat.get("name",ck),"label":cat.get("short_name",ck),
        "annotations":{"web_name":cat.get("web_name","")},"members":entries}
    # The theme's own id (KSI-CED for the theme under the key CED). The Set's
    # URI is minted from the key, as every id of this bundle is; the source's
    # id is carried as what the kernel has for another name of an object.
    if cat.get("id") is not None: cobj["aliases"]=[{"scheme":KSI_ID_SCHEME,"value":cat["id"]}]
    if cat.get("status") is not None: cobj["facets"]={F_NARR:{"status":cat["status"]}}
    objects[f"objects/set/ksi-{slug(ck)}.json"]=cobj
    ksi_cat_entries.append({"ref":curi,"sequence":nseq()})
# terminology container
terms_payload={}; ignore_in_terms={}; term_updated={}
for tid,t in d["FRD"]["data"]["all"].items():
    e={"term":t["term"],"definition":T(t["definition"],"definition")}
    for k,dk in [("tag","tag"),("alts","aliases"),
                 ("do_not_link","do-not-link"),("reference","reference"),
                 ("reference_url","reference-url")]:
        # an empty container is left out (the kernel has one spelling of "nothing": absent)
        if t.get(k) is not None and t[k]!=[]: e[dk]=t[k]
    for k,dk in [("note","note"),("notes","notes")]:
        if t.get(k) is not None: e[dk]=T(t[k],dk)
    # terminology@1 has `do-not-link` and no member for the source's second
    # flag. It is carried beside the glossary, in the converter's own facet
    # on the same Set, keyed by the term's id, with the value the source wrote.
    if "ignore_in_terms" in t:
        if flag(t["ignore_in_terms"]) is None:
            raise SystemExit(f"{tid}: ignore_in_terms is {t['ignore_in_terms']!r}; the converter knows a boolean")
        ignore_in_terms[tid]=t["ignore_in_terms"]
    counters["updated-entries"]+=len(t.get("updated",[]) or [])
    if t.get("updated"): term_updated[tid]=t["updated"]
    counters["term-alts"]+=len(t.get("alts",[]) or [])
    terms_payload[tid]=e
frd_i=d["FRD"]["info"]
glossary={"terms":terms_payload,
    "glossary-info":{k:frd_i[k] for k in ("name","short_name","web_name","purpose","status","effective") if frd_i.get(k) is not None}}
# CTL parked (guidance free text language-tagged; structure otherwise verbatim)
ctl_payload=park(d["CTL"],"cr26.CTL")
def _wrap_ctl_guidance(n):
    if isinstance(n,dict):
        for k,v in list(n.items()):
            if k=="guidance" and isinstance(v,(str,list)): n[k]=T(v,"guidance")
            else: _wrap_ctl_guidance(v)
    elif isinstance(n,list):
        for x in n: _wrap_ctl_guidance(x)
_wrap_ctl_guidance(ctl_payload)

# ---- backlog #10 drain (gate 3): CTL ODP assignments -> set-parameter Tailoring ----
# The parameterIds are the Rev 5.2.0 ODP ids verbatim; the (requirement, ODP)
# address resolves via the DECLARING statement (measured: no ODP is inserted
# in >=2 statements). The tailored NIST Requirements ride along in-bundle
# (closure; the IFA pattern: a tailoring package carries what it tailors).
NISTB=os.path.join(ROOT,"converted_examples","US.SP800-53","sp800-53-core-bundle")
def _ctl_cid(label):   # AC-06-01 -> ac-6.1; AU-10 -> au-10
    ps=label.split("-")
    cid=f"{ps[0].lower()}-{int(ps[1])}"
    return cid+(f".{int(ps[2])}" if len(ps)>2 else "")
ctl_ops=[]; ctl_carried={}; ctl_choice_conflicts=[]
for fam,entries in d["CTL"].items():
    for label,e in entries.items():
        if not e.get("parameters"): continue
        cid=_ctl_cid(label)
        fp=os.path.join(NISTB,"objects","req",cid.replace(".","-")+".json")
        if not os.path.exists(fp):
            raise SystemExit(f"missing {fp} - run convert_nist.py first (backlog #10 drain)")
        robj=json.load(open(fp,encoding="utf-8"))
        for pa in e["parameters"]:
            pid,val=pa["parameterId"],pa["value"]
            sid=next((s["id"] for s in robj["statements"]
                      for p in s.get("parameters",[]) if p["name"]==pid),None)
            decl=next((p for s in robj["statements"] for p in s.get("parameters",[]) if p["name"]==pid),None)
            if sid is None:
                ctl_choice_conflicts.append((label,pid,"no such ODP on the Rev 5.2.0 control")); continue
            if decl.get("type")=="choice" and val not in {c["value"] for c in decl.get("choices",[])}:
                # FedRAMP flattens multi-selections into prose strings ("a; b",
                # "a, b and c"); NIST declares cardinality-many choices. Split;
                # if EVERY part is a declared choice it is pure serialization ->
                # list value (counted); anything else is a real conflict (parked).
                parts=_selections(val)
                allowed={c["value"] for c in decl.get("choices",[])}
                if decl.get("cardinality")=="many" and parts and all(x in allowed for x in parts):
                    ctl_ops.append({"op":"set-parameter","requirement-ref":robj["id"],
                                    "statement-id":sid,"parameter":pid,
                                    "value":[D(R_SELECTION,lambda v,i=i: _selections(v)[i],val) for i in range(len(parts))]})
                    ctl_carried[cid]=robj
                    counters["ctl-multiselect-normalized"]+=1
                    continue
                ctl_choice_conflicts.append((label,pid,"value outside the declared choices")); continue
            ctl_ops.append({"op":"set-parameter","requirement-ref":robj["id"],
                            "statement-id":sid,"parameter":pid,"value":val})
            ctl_carried[cid]=robj
        # drained: strip the parameters from the parked payload (guidance stays L2)
        ctl_payload[fam][label].pop("parameters",None)
        if not ctl_payload[fam][label]: del ctl_payload[fam][label]
for cid,robj in sorted(ctl_carried.items()):
    objects[f"objects/req/nist-{cid.replace('.','-')}.json"]=robj
objects["objects/set/rev5-tailored.json"]={"id":f"{NS}/set/rev5-tailored","version":VER,
    "lifecycle":"active","title":"Rev 5 controls tailored by the CTL ODP overlay (carried in-bundle)",
    "members":[{"ref":o["id"],"sequence":(i+1)*10} for i,(c,o) in enumerate(sorted(ctl_carried.items()))]}
objects["objects/tailoring/rev5-odp-overlay.json"]={"id":f"{NS}/tailoring/rev5-odp-overlay",
    "version":VER,"lifecycle":"active",
    "title":"FedRAMP CTL ODP assignments over NIST SP 800-53 Rev 5 (backlog #10 drained)",
    "selects":[{"set-ref":f"{NS}/set/rev5-tailored"}],"operations":ctl_ops}
counters["ctl-odp-ops"]=len(ctl_ops); counters["ctl-carried-reqs"]=len(ctl_carried)

objects["objects/set/ctl-overlay.json"]={"id":f"{NS}/set/ctl-overlay","version":VER,
    "lifecycle":"active","title":"Rev5 control overlay (guidance parked L2; ODP assignments drained to the rev5-odp-overlay Tailoring)",
    "members":[{"ref":f"{NS}/set/type/rev5","sequence":10}],
    "facets":{F_COMPAT:{"ctl":ctl_payload}}}
counters["ctl-overlays"]=sum(len(v) for v in d["CTL"].values())
# roots + tailorings
objects["objects/set/root.json"]={"id":f"{NS}/set/root","version":VER,"lifecycle":"active",
    "title":d["info"]["title"],
    "members":fam_entries+ksi_cat_entries+[
        {"ref":f"{NS}/set/ctl-overlay","sequence":nseq()}],
    "facets":{F_NARR:{"description":T(d["info"]["description"],"description"),
                      **({"ignore-in-terms":ignore_in_terms} if ignore_in_terms else {}),
                      **({"term-updated":term_updated} if term_updated else {})},
              F_ACRIT:{"default-artifacts":d["info"]["default_artifacts"]},
              F_TERM:glossary}}
for c,t in class_tailorings.items():
    if t["operations"]: objects[f"objects/tailoring/class-{c}.json"]=t

# ---- checks on what is about to be written; nothing is on disk yet ----
# The flags of the source stand in the objects as values that know their
# origin. The plain booleans take their place here, before a file is written
# or a digest taken; the ledger remembers where each stood.
led.resolve(objects)
for rel,o in objects.items(): no_fraction(o,rel)
# The census of the report is counted on the source, the objects on what was
# built. An id that occurs twice would overwrite its first object, and the
# two counts would differ.
n_rules={trk:sum(len(sv) for f in d["FRR"].values() for sv in f["data"].get(trk,{}).values()) for trk in ("all","rev5","20x")}
n_ksi=sum(len(cat["indicators"]) for cat in d["KSI"].values())
n_built=sum(1 for o in objects.values() if o["id"].startswith((f"{NS}/req/",f"{NS}/ksi/")))
if n_built!=sum(n_rules.values())+n_ksi:
    raise SystemExit(f"the source has {sum(n_rules.values())} rules and {n_ksi} KSIs, the conversion built {n_built} "
                     f"Requirements for them: an id occurs twice")

# The carried Rev 5 Requirements bring the pins of their facets (#17
# fail-closed): each is the pinned schema of the SP 800-53 bundle itself, as
# that bundle's manifest lists it. Until 2026-11-14 this converter wrote four
# such schemas from its own text; a change of the SP 800-53 conversion (a new
# member of a facet, another facet on a control) would have left this bundle
# with a pin that no longer fits the objects it carries.
with open(os.path.join(NISTB,"content-manifest.json"),encoding="utf-8") as _f: _nist_pins={s["id"]:s for s in json.load(_f)["facet-schemas"]}
carried_pins={}        # facet id -> the pinned schema descriptor of the SP 800-53 bundle
for _cid,_robj in sorted(ctl_carried.items()):
    for _key in _robj.get("facets",{}):
        _fid=_key.rsplit("@",1)[0]
        if _fid in carried_pins: continue
        if _fid not in _nist_pins:
            raise SystemExit(f"the carried Requirement {_robj['id']} has the facet {_key}, and the manifest of the SP 800-53 "
                             f"bundle pins no schema for it")
        with open(os.path.join(NISTB,*_nist_pins[_fid]["path"].split("/")),encoding="utf-8") as _f: carried_pins[_fid]=(_nist_pins[_fid]["path"],json.load(_f))

pinned=[]              # the schema files this run writes, for the manifest and the cleanup
def stub(path,fid,mods,props):
    # 26 delivered: pins are the normative payload contract, fail-closed
    if fid in carried_pins:
        # a facet this converter writes itself and a carried Requirement uses too: one schema that knows both shapes
        _theirs=carried_pins.pop(fid)[1]["schema"].get("properties",{})
        for k,v in _theirs.items():
            if props.setdefault(k,v)!=v:
                raise SystemExit(f"the facet {fid}: this converter and the SP 800-53 bundle type the member {k!r} differently")
    w(path,{"id":fid,"version":"1.0.0","modifies-semantics":mods,
        "note":"NORMATIVE pinned payload schema (backlog 26): closed shape - unknown keys are rejected, never smuggled",
        "schema":{"$schema":"https://json-schema.org/draft/2020-12/schema","type":"object","properties":props,
                  "additionalProperties":False}})
    pinned.append(path)
def pin_stdlib(fn):
    src=os.path.join(ROOT,"jascon","schemas","stdlib",fn)
    with open(src,encoding="utf-8") as f: desc=json.load(f)
    carried_pins.pop(desc["id"],None)        # the standard library's descriptor is the pin, whoever uses the facet
    w(f"schemas/{fn}",desc)
    pinned.append(f"schemas/{fn}")
pin_stdlib("terminology-1.0.0.json")   # 26: stdlib pins are VERBATIM
pin_stdlib("reporting-obligation-1.0.0.json")
pin_stdlib("effectivity-1.0.0.json")
pin_stdlib("assessment-criteria-1.0.0.json")
stub("schemas/cr26-scope-stub.json",F_SCOPE.split("@")[0],["selection"],
     {"classes":{"type":"array"},"types":{"type":"array"},"paths":{"type":"array"},"affects":{"type":"array"},"tag":{"type":"string"}})
stub("schemas/cr26-narrative-stub.json",F_NARR.split("@")[0],[],
     {"description":{"type":"object"},"note":{"type":"object"},"notes":{"type":"object"},
      "schema-name":{"type":"string"},"reference":{"type":"string"},"danger":{"type":"object"},
      "corrective-actions":{"type":"object"},
      # the source's own word for the status of a document, beside the kernel's lifecycle it was mapped to
      "status":{"type":"string"},
      # a notification the source marks optional: the entry of reporting-obligation@1, and its flag
      "optional-notification":{"type":"array","minItems":1,"items":{"type":"object","additionalProperties":False,
          "required":["optional"],
          "properties":{"party":{"type":"string"},"method":{"type":"string"},"target":{"type":"string"},
                        "name":{"type":"object","additionalProperties":{"type":"string"}},
                        "optional":{"const":True}}}},
      # the glossary's second flag, by term id (on the Set that hosts terminology@1)
      "ignore-in-terms":{"type":"object","minProperties":1,"additionalProperties":{"type":"boolean"}},
      # the update history of a term, by term id, the entries as the source writes them
      "term-updated":{"type":"object","minProperties":1,"additionalProperties":{"type":"array"}}})
# the one compat schema of every converter (1.1.0); until 2026-11-14 this converter pinned one of its own
_theirs=carried_pins.pop(F_COMPAT.split("@")[0],None)     # a carried Requirement that uses the compat facet brings its pin
if _theirs is not None and _theirs[1]!=compat_schema():
    raise SystemExit("the SP 800-53 bundle pins a compat schema that is not the one schema of this repository's converters "
                     "(oscal_conv_lib.compat_schema, 1.1.0): a carried Requirement would be held to two schemas of one id")
w("schemas/"+COMPAT_FILE,compat_schema()); pinned.append("schemas/"+COMPAT_FILE)
# the pins the carried Rev 5 Requirements bring, as the SP 800-53 bundle holds them
for _fid,(_path,_desc) in sorted(carried_pins.items()):
    if _path in pinned: raise SystemExit(f"two pinned schemas would be written to {_path}")
    w(_path,_desc); pinned.append(_path)

# stale-file cleanup (files only, never rmdir): everything not re-emitted goes
want={os.path.normpath(r) for r in objects}|{"content-manifest.json"}|{os.path.normpath(p) for p in pinned}
if os.path.exists(OUT):
    import time as _t
    for base,_,files in os.walk(OUT):
        for fn in files:
            full=os.path.join(base,fn)
            if os.path.normpath(os.path.relpath(full,OUT)) not in want:
                for i in range(5):
                    try: os.remove(full); break
                    except OSError:
                        if i==4: raise
                        _t.sleep(0.3*(i+1))
from oscal_conv_lib import textify
for o in objects.values(): textify(o,LANG)   # 12 delivery
for rel,o in objects.items(): w(rel,o)
manifest={"manifest-version":"1"}
# A carried Requirement may hold what the 1.0.0 kernel cannot type; the
# manifest then names the kernel it needs (KERNEL-1), as the library's own
# writer does. The objects this converter makes itself need none.
if needs_kernel_2(objects.values()): manifest["kernel-version"]="2.0.0"
manifest.update({
 "provenance":{"source":d["info"]["title"],"source-version":VER,
               "last_updated":d["info"]["last_updated"],"converter":"convert_cr26.py v0.2"},
 "objects":[{"id":o["id"],"version":o["version"],"package-digest":shaf(rel),
             "semantic-digest":sdig(o),"path":rel} for rel,o in sorted(objects.items())],
 "facet-schemas":[]})
for s in sorted(os.listdir(os.path.join(OUT,"schemas"))):
    with open(os.path.join(OUT,"schemas",s),encoding="utf-8") as _f: sd=json.load(_f)
    manifest["facet-schemas"].append({"id":sd["id"],"exact-version":sd["version"],
        "digest":shaf(f"schemas/{s}"),"path":f"schemas/{s}"})
w("content-manifest.json",manifest)
# The bundle is not committed, the coverage reports are. The manifest lists
# both digests of every object and the digest of every pinned schema, so its
# own digest stands for every byte of the bundle. The reports state it: a
# run that reproduces the committed reports has reproduced the bundle, and a
# change that alters one object alters the reports.
MANIFEST_DIGEST=shaf("content-manifest.json")

# ---------------- the ledger: every source value, checked against the files just written ----------------
# A drop is declared for exactly the paths the path map says are not carried,
# with the reason the map gives: the two classes that were declared before
# 2026-11-14. No other drop is declared, and none is added: a value that
# reaches no file is unaccounted, and the run ends with 1 (ledger_gate, the
# last statement of this script).
for _pat,_level,_why in RULES:
    if _level==DROP: led.drop(_pat,_why)
LEDGER=led.account(OUT,{**objects,"content-manifest.json":manifest})
LT=LEDGER["totals"]; LFAIL=LEDGER["verification-failures"]

# The ledger follows strings, numbers and flags. A null of the source states
# nothing and has no origin to carry; it would read as unaccounted. Counted,
# so that the report says so if a publication ever has one.
def _nulls(n):
    if isinstance(n,dict): return sum(_nulls(v) for v in n.values())
    if isinstance(n,list): return sum(_nulls(v) for v in n)
    return 1 if n is None else 0
n_null=_nulls(led.docs["cr26"])

# The ledger by path, and the path map held to it. For every path: how many
# of its values were copied, transformed, are no content by a checked rule,
# were dropped for a declared reason, or are unaccounted.
by_path=collections.defaultdict(collections.Counter)
for _e in LEDGER["entries"]: by_path[_e["path"]][_e["outcome"]]+=1
if {p:sum(c.values()) for p,c in by_path.items()}!=dict(paths):
    raise SystemExit("the ledger and the path map count different source paths: one of the two inventories is wrong")
rules_used=collections.Counter()        # rule -> source values it accounts for
for _e in LEDGER["entries"]:
    for _r in {_d["rule"] for _d in _e.get("destinations",[]) if "rule" in _d}: rules_used[_r]+=1
not_content=collections.Counter((_e["kind"],_e["rule"]) for _e in LEDGER["entries"] if _e["outcome"]=="not-content")
# Three ways a row of the path map can be contradicted by what was written:
# it names a destination (L1, L2) and a value of its path reached no file;
# it says "not carried" (a declared drop) and a value of its path was
# written; it is L1, a kernel field or a facet with a schema, and no value of
# its path stands anywhere but in the parked payload, which is L2.
_parked="/facets/"+F_COMPAT.replace("~","~0").replace("/","~1")+"/"
outside_parked=collections.Counter()        # path -> values with a destination outside the parked payload
for _e in LEDGER["entries"]:
    if any(not _d["pointer"].startswith(_parked) for _d in _e.get("destinations",[])): outside_parked[_e["path"]]+=1
claims=[]
for _p,_c in sorted(by_path.items()):
    _level=dest(_p)[0]
    if _level in ("L1","L2") and _c["unaccounted"]+_c["intentionally-dropped"]+_c["not-content"]:
        claims.append({"path":_p,"level":_level,"values":sum(_c.values()),
                       "without-a-destination":_c["unaccounted"]+_c["intentionally-dropped"]+_c["not-content"]})
    if _level==DROP and _c["copied"]+_c["transformed"]:
        claims.append({"path":_p,"level":_level,"values":sum(_c.values()),"written-all-the-same":_c["copied"]+_c["transformed"]})
    if _level=="L1" and _c["copied"]+_c["transformed"] and not outside_parked[_p]:
        claims.append({"path":_p,"level":_level,"values":sum(_c.values()),"only-in-the-parked-payload":_c["copied"]+_c["transformed"]})
def _no_phrase(pointer):
    """A pointer segment with a space in it is a key of the source that is a
    phrase of the publication (two nodes of a flow diagram). The reports and
    the record reproduce no text of it and print `*` for such a segment."""
    return "/".join("*" if " " in seg else seg for seg in pointer.split("/"))
unacc=[{"path":u["path"],"count":u["count"],"example":_no_phrase(u["pointers"][0])} for u in LEDGER["unaccounted-paths"]]

# The drops that are declared, for the table the author asked for: per
# reason the source paths, the count, one example and the converter's reading
# under the rule "real content is never dropped". The example is a value that
# is no text (a date, an id) where the class has one, with its pointer; a
# report of this conversion reproduces no prose of the publication.
def _plain_example(source):
    node=led.docs["cr26"]
    for seg in source.split("#",1)[1].split("/")[1:]:
        seg=seg.replace("~1","/").replace("~0","~")
        node=node[int(seg)] if isinstance(node,list) else node[seg]
    return node if not isinstance(node,str) or (" " not in node and len(node)<=40) else None
declared_drops=[]
for _why in sorted({_e["reason"] for _e in LEDGER["entries"] if _e["outcome"]=="intentionally-dropped"}):
    _mine=[_e for _e in LEDGER["entries"] if _e["outcome"]=="intentionally-dropped" and _e["reason"]==_why]
    _ex=next(((_e["source"],_plain_example(_e["source"])) for _e in _mine if _plain_example(_e["source"]) is not None),
             (_mine[0]["source"],None))
    declared_drops.append({"reason":_why,"source-values":len(_mine),
                           "paths":[{"path":p,"count":n} for p,n in sorted(collections.Counter(_e["path"] for _e in _mine).items())],
                           "example":{"source":_no_phrase(_ex[0]),**({"value":_ex[1]} if _ex[1] is not None else {})},
                           "reading":DROP_READING.get(_why,"no reading stated")})

# What the ledger cannot see: it follows source values into the bundle, not
# the bundle back to the source. A value the converter writes on its own (a
# constant, an id minted from a KEY of the source, a sequence number, an
# object copied from the SP 800-53 bundle) has no source value behind it.
# Counted here: every leaf value of the written objects and the manifest
# that is no destination of a source value.
_claimed=collections.defaultdict(set)
for _e in LEDGER["entries"]:
    for _d in _e.get("destinations",[]):
        if _d.get("as")!="key": _claimed[_d["object"]].add(_d["pointer"])
bundle_leaves=collections.Counter(); own_values=collections.Counter()
def _own(n,oid,kind,parts):
    if isinstance(n,dict):
        for k,v in n.items(): _own(v,oid,kind,parts+[str(k).replace("~","~0").replace("/","~1")])
    elif isinstance(n,list):
        for i,v in enumerate(n): _own(v,oid,kind,parts+[str(i)])
    else:
        bundle_leaves[kind]+=1
        if "/"+"/".join(parts) not in _claimed.get(oid,()): own_values[kind]+=1
for _rel,_o in sorted(objects.items()):
    _kind=("carried Rev 5 Requirement" if _o["id"].startswith(NIST+"/") else
           {"req":"Requirement (rule)","ksi":"Requirement (KSI)","map":"Mapping","set":"Set","tailoring":"Tailoring"}[_rel.split("/")[1]])
    _own(_o,_o["id"],_kind,[])
_own(manifest,"content-manifest.json","manifest",[])

# The record: one row per source path and outcome, as the library makes it
# from the per-leaf ledger (which has one entry for each source value and is
# not written). A payload that is keyed by an id of the source (a term, a
# control of the overlay, a class) is one row and not one per id. The one
# thing done to the library's result here: no pointer prints a phrase.
def _facet(f): return "/facets/"+re.escape(f.replace("~","~0").replace("/","~1"))
LEDGER_RECORD=ledger_by_path(LEDGER,collapse=[
    (rf"^({_facet(F_TERM)}/terms)/[^/]+",r"\1/{term-id}"),
    (rf"^({_facet(F_NARR)}/ignore-in-terms)/[^/]+",r"\1/{term-id}"),
    (rf"^({_facet(F_COMPAT)}/ctl)/[^/]+/[^/]+",r"\1/{control-family}/{control}"),
    (rf"^({_facet(F_COMPAT)}/class-variants)/[^/]+",r"\1/{class}")])
for _row in LEDGER_RECORD["paths"]:
    _row["example"]=_no_phrase(_row["example"])
    for _d in _row.get("to",[]): _d["pointer"]=_no_phrase(_d["pointer"])
for _u in LEDGER_RECORD["unaccounted-paths"]: _u["pointers"]=[_no_phrase(x) for x in _u["pointers"]]
os.makedirs(OUTDIR,exist_ok=True)
with open(os.path.join(OUTDIR,LEDGER_FILE),"w",encoding="utf-8",newline="\n") as f:
    json.dump(LEDGER_RECORD,f,indent=1,ensure_ascii=False); f.write("\n")

# ---------------- coverage ----------------
rows=[];unmapped=[]
for p,n in sorted(paths.items()):
    l,t=dest(p)
    (rows if l else unmapped).append((p,n,l,t) if l else (p,n))
total=sum(paths.values()); mapped=sum(n for _,n,_,_ in rows)
nreq=sum(1 for o in objects.values() if o["id"].startswith(f"{NS}/req/") or o["id"].startswith(f"{NS}/ksi/"))
nset=sum(1 for o in objects.values() if "/set/" in o["id"])
ntail=sum(1 for o in objects.values() if "/tailoring/" in o["id"])
nclass=sum(1 for t in class_tailorings.values() if t["operations"])
# the Sets by what they are, read from the file names the converter gives them
set_kinds=collections.Counter(re.match(r"objects/set/([a-z0-9]+)",rel).group(1)
                              for rel in objects if rel.startswith("objects/set/"))
n_force=paths[RULE+".force"]; n_vforce=paths[VAR+".force"]
fractions=[{"path":p,"count":n} for p,n in sorted(fraction_paths.items())]
by_level=collections.Counter()
for _p,_n,_l,_t in rows: by_level[_l]+=_n
# The lifecycle of every object, and where it comes from: a document's status
# by rule (the ledger names those objects), the SP 800-53 bundle for a carried
# Requirement, or the converter itself for an object it makes for the
# publication as a whole, for which the source states no status.
_from_status={_d["object"] for _e in LEDGER["entries"] for _d in _e.get("destinations",[]) if _d["pointer"]=="/lifecycle"}
lifecycle_by_origin=collections.Counter()
for _o in objects.values():
    _origin=("from the status of a document" if _o["id"] in _from_status else
             "as the SP 800-53 bundle has it" if _o["id"].startswith(NIST+"/") else "the converter's own")
    lifecycle_by_origin[(_origin,_o["lifecycle"])]+=1
# `active` on an object whose status no document of the source states is the converter's default (the author's
# decision of 2026-11-14): the objects made for the publication as a whole, and the carried Rev 5 Requirements,
# on which the SP 800-53 converter wrote it as its own default
LIFECYCLE_DEFAULT=lifecycle_default_record(objects,_from_status)
status_words=collections.Counter()
for _f in led.docs["cr26"]["FRR"].values(): status_words[("family",_f["info"].get("status"))]+=1
for _c in led.docs["cr26"]["KSI"].values(): status_words[("KSI category",_c.get("status"))]+=1
j={"source":d["info"]["title"],"version":VER,
   "totals":{"leaf-values":total,"mapped":mapped,"unmapped":total-mapped,
             "coverage-pct":round(100*mapped/total,3),
             "mapped-by-level":{l:by_level[l] for l in ("L1","L2",DROP) if by_level[l]}},
   "ledger":{"file":LEDGER_FILE,"leaf-values":LEDGER["leaf-values"],"totals":dict(LT),
             "verification-failures":len(LFAIL),
             "rules":[{"rule":r,"source-values":n} for r,n in sorted(rules_used.items())],
             "not-content":[{"kind":k,"rule":r,"source-values":n} for (k,r),n in sorted(not_content.items())],
             "declared-drops":declared_drops,
             "unaccounted":unacc,
             "nulls-in-the-source":n_null,
             "path-map-rows-the-ledger-contradicts":claims,
             "written-values-with-no-source-value":[{"written-as":k,"leaf-values":bundle_leaves[k],
                                                     "no-source-value":own_values[k]} for k in sorted(bundle_leaves)]},
   "objects":{"requirements(rules+ksi)":nreq,"mappings":mappings,"sets":nset,
              "tailorings":ntail,"total":len(objects)},
   "lifecycle-default":LIFECYCLE_DEFAULT,
   "lifecycle":{"status-of-the-source":[{"document":k,"status":s,"count":n} for (k,s),n in sorted(status_words.items(),key=str)],
                "rule":dict(STATUS_LIFECYCLE),
                "objects":[{"lifecycle":l,"origin":o,"count":n} for (o,l),n in sorted(lifecycle_by_origin.items())]},
   "bundle":{"content-manifest-digest":MANIFEST_DIGEST,"objects":len(manifest["objects"]),
             "facet-schemas":len(manifest["facet-schemas"])},
   "modality(rule-level)":dict(mod_hist),
   "tailoring-ops":dict(ops_emitted),"converter-deviations(easings)":dev_records,
   "counters":dict(counters),"lang-wraps":dict(lang_wraps),
   "synthesized-prose(variant-only-rules)":synth_prose,
   "dangling-related":dangling_related,
   "obligated-party":obligated_party_record(PARTY,PARTY_ORIGIN,PARTY_DEFAULT,PARTY_SOURCE_STATES),
   "fractions-as-decimal-strings":fractions,
   "unmapped":[{"path":p,"count":n} for p,n in unmapped],
   "path-map":[{"path":p,"count":n,"level":l,"destination":t} for p,n,l,t in rows]}
# The reports are compared byte for byte with the committed ones (Validators
# workflow), so their line ending is stated and not left to the platform.
os.makedirs(OUTDIR,exist_ok=True)
with open(RJS,"w",encoding="utf-8",newline="\n") as f: json.dump(j,f,ensure_ascii=False,indent=1)

md=[f"# CR26 -> Semantic Core: Coverage Report (computed)\n",
 f"Source: **{d['info']['title']}** v{VER} (bespoke JSON; not OSCAL).\n",
 "## Totals\n",
 f"- Source leaf values inventoried (id-normalized paths): **{total:,}**",
 f"- Mapped: **{mapped:,}** -> **UNMAPPED: {total-mapped}** -> coverage **{j['totals']['coverage-pct']} %**",
 f"- \"Mapped\" means that the path has a row in the path map below, not that its values are in the bundle. Of the "
 f"{mapped:,}: **{by_level['L1']+by_level['L2']:,}** on rows that name a destination (L1 {by_level['L1']:,}, L2 "
 f"{by_level['L2']:,}), **{by_level[DROP]:,}** on rows that declare the path not carried. What arrived, value by "
 f"value, is the ledger's to say (below): {LT['copied']:,} copied, {LT['transformed']:,} transformed, "
 f"{LT['not-content']:,} no content by a checked rule, {LT['intentionally-dropped']:,} dropped for a declared "
 f"reason, {LT['unaccounted']:,} unaccounted.",
 f"- Emitted: **{nreq} Requirements** (FRR rules + KSIs), **{mappings} Mapping objects**, "
 f"**{nset} Sets** ({set_kinds['tax']} families, {set_kinds['subset']} subsets, {set_kinds['class']} classes, "
 f"{set_kinds['type']} tracks, {set_kinds['ksi']} KSI categories, and "
 f"{nset-sum(set_kinds[k] for k in ('tax','subset','class','type','ksi'))}: the root, the CTL overlay, the Set of the "
 f"carried Rev 5 Requirements), "
 f"**{ntail} Tailorings** ({nclass} class variants and the Rev 5 ODP overlay), manifest with both digests, "
 f"{len(manifest['facet-schemas'])} pinned stubs.",
 f"- The bundle as written: `content-manifest.json` is `{MANIFEST_DIGEST}`. The manifest lists both digests of "
 f"each of its {len(manifest['objects']):,} objects ({nreq} Requirements of the publication, "
 f"{counters.get('ctl-carried-reqs',0)} carried Rev 5 Requirements, the Mappings, Sets and Tailorings) and the digest "
 f"of each pinned schema, so this value stands for every byte of the bundle. The bundle is not in the repository; "
 f"a run that reproduces this report has reproduced the bundle.\n",
 "## Conversion rules (declared, counted)\n",
 f"- **force -> modality** (rule level): "+", ".join(f"{k} x{v}" for k,v in sorted(mod_hist.items(),key=lambda x:-x[1]))
 +f". Class-variant forces become **Tailoring ops**: {dict(ops_emitted)}; easings auto-carry a converter Deviation "
 f"(approver: FedRAMP, rationale: published class variant) x{dev_records}.",
 f"- **status -> lifecycle**, by rule. The source gives a family and a KSI category the status of a document, in "
 f"three words (its schema: stable, placeholder, empty): "
 +"; ".join(f"{k} `{s}` x{n}" for (k,s),n in sorted(status_words.items(),key=str))
 +f". The kernel's lifecycle knows draft, active, deprecated, withdrawn. The converter's mapping: "
 +", ".join(f"`{s}` -> `{l}`" for s,l in STATUS_LIFECYCLE.items())
 +f"; a word outside the three stops the run. `stable` is the source's word for a document that is settled; "
 f"`placeholder` and `empty` say that it is not, and `draft` is the only state of the kernel that says so. The "
 f"source's own word is kept beside the mapped state, in narrative@1 of the Set that stands for the document "
 f"(`status`): the kernel has no place for it. The status is the document's, and a document of this source is its "
 f"rules or indicators, none of which has a status of its own; the lifecycle of every object made from a document "
 f"therefore follows the document's status - its Set, its subset Sets, its rules or indicators and the Mappings of "
 f"their control links. Objects by lifecycle and where it comes from: "
 +"; ".join(f"`{l}` x{n} {o}" for (o,l),n in sorted(lifecycle_by_origin.items()))
 +f". Until 2026-11-14 the converter read no status and wrote `active` on every object. The converter's own "
 f"`active` stands on the objects it makes for the publication as a whole (the root, the class and track Sets, the "
 f"CTL overlay and the Set of the carried Rev 5 Requirements, the Tailorings), for which the source states no status."
 +(f" Objects of a document that states no status, written `draft`: "
   f"x{counters['objects-of-a-document-without-status']}." if counters.get("objects-of-a-document-without-status") else ""),
 f"- **The id of a KSI category** (x{paths['cr26.KSI.*.id']}) is carried as an alias of the category's Set "
 f"(`aliases`, scheme `{KSI_ID_SCHEME}`). The Set's own URI is minted from the key the category stands under, as "
 f"every id of this bundle is minted from a key of the source.",
 f"- **affects[] -> obligated-parties[]** (parties minted as codes); subset applicability -> scope@1 on subset Sets "
 f"and composed **class Sets (a-d)** and **type Sets (20x/Rev5)** - sets-of-sets (D21).",
 lifecycle_default_line(LIFECYCLE_DEFAULT),
 obligated_party_line(PARTY,PARTY_ORIGIN,PARTY_DEFAULT,
     why="a KSI has no `affects` and its statement names no actor; the converter reads an indicator as a "
         "statement about the cloud service offering, which is its provider's to meet",
     source_states=PARTY_SOURCE_STATES)
 +f" Statements with a party from `affects`: x{counters.get('statements-party-from-affects',0)}; with this party: "
  f"x{counters.get('statements-party-fallback',0)} (every KSI, and a rule only if it names nobody).",
 f"- **timeframe_num/type -> statement parameter** 'timeframe' (elapsed vs calendar split; calendar-ref minted; "
 f"tightening: lower). Class variants: set-parameter when unit-class matches; "
 f"**true unit-class crossings x{counters.get('timeframe-unitclass-crossings',0)}** (base-absent variant timeframes x{counters.get('timeframe-variant-only',0)} counted separately) stay in the L2 class-variants payload "
 f"- spec-feedback: candidate D9 duration-union question.",
 f"- **timeframe_num_min / timeframe_num_max -> statement parameters** 'timeframe-min' and 'timeframe-max' "
 f"(bounds written: x{counters.get('timeframe-range-bounds',0)}). A rule states one timeframe or a range. The kernel's "
 f"durations have one `num`, and its `range` is a container of scalars, which a duration is not (D9); a range is "
 f"therefore its two bounds, each a duration with the unit of timeframe_type and, for a calendar unit, the "
 f"calendar. Tightening is declared `higher` for the floor and `lower` for the ceiling: a window narrows when its "
 f"floor rises or its ceiling falls. The two directions are the converter's reading, as `lower` is for a single "
 f"timeframe; the source states none.",
 f"- **A number that is no integer** (x{sum(fraction_paths.values())}) is written as a decimal string, the kernel's "
 f"spelling of a fraction (NUMBER-1, D3.9): "
 +("; ".join(f"`{p}` x{n}" for p,n in sorted(fraction_paths.items())) or "none in this publication")
 +". It is done in the parked L2 payloads, which are otherwise as the source has them. Anywhere else a fraction "
 f"stops the run: a duration's `num` is a kernel number, and a kernel number is an integer.",
 f"- **varies_by_class** preserved in full as L2 `class-variants` payloads on {counters.get('class-variant-rules',0)} rules "
 f"(+{counters.get('ksi-class-variant',0)} KSIs); computable deltas additionally emitted as ops. "
 f"Variant-only rules (no base statement): synthesized base prose x{synth_prose} (flagged).",
 f"- **Control lists -> {mappings} Mapping objects**: x{counters.get('ksi-control-mappings',0)} from KSIs, "
 f"x{counters.get('rule-control-mappings',0)} from rules (relationship `supports`, confidence `draft`, "
 f"rationale per handbook 8.6 untyped-import rule; targets minted under {NIST}/). A rule's `controls` are converted "
 f"by the rule for a KSI's: the publisher's schema types the two lists alike, as an array of control ids, and "
 f"states no relationship for either (read 2026-11-14 at the publication's tag).",
 f"- **FRD -> terminology@1** hosted on the corpus root Set (glossary-info carries the FRD block metadata): "
 f"{len(terms_payload)} terms, {counters.get('term-alts',0)} aliases, links and chrome flags in-payload; a term "
 f"without alternatives gets no `aliases` (an empty container is left out). **ignore_in_terms** "
 f"(x{len(ignore_in_terms)}) has no member in terminology@1, which knows `do-not-link` only; it is carried in "
 f"narrative@1 on the same Set as `ignore-in-terms`, by term id, with the value the source wrote.",
 f"- **CTL ODP assignments DRAINED (backlog #10, gate 3)**: {counters.get('ctl-odp-ops',0)} set-parameter ops on the "
 f"`rev5-odp-overlay` Tailoring, each addressed (requirement-ref, statement-id, parameter) via the DECLARING "
 f"statement of the Rev 5.2.0 ODP (measured: no ODP is declared in two statements); {counters.get('ctl-carried-reqs',0)} "
 f"tailored Rev 5 Requirements carried in-bundle as byte-identical copies (closure; the authorization-package "
 f"pattern). CTL guidance entries stay parked L2 - supplemental prose on external controls is D20 supplements "
 f"territory, not ODP addressing. Multi-select serialization normalized x{counters.get('ctl-multiselect-normalized',0)} "
 f"(FedRAMP flattens many-cardinality selections into prose strings 'a; b' / 'a, b and c'; every part matches a "
 f"declared NIST choice -> list value; REPORTED upstream). Residual choice conflicts: {ctl_choice_conflicts or 'none'}.",
 f"- **notification/following_information -> reporting-obligation@1**; artifacts.all and examples -> "
 f"assessment-criteria@1; note/notes/danger/corrective_actions -> narrative@1. **A notification the source marks "
 f"`optional`** (x{counters.get('optional-notifications',0)}) is no duty, and reporting-obligation@1 lists duties "
 f"(it declares that it alters what passing means) and has no member for the flag. The entry goes whole, with its "
 f"flag, to narrative@1 as `optional-notification`; reporting-obligation@1 keeps the other entries of the rule.",
 f"- **rule/KSI term names resolved to FRD ids** via the term+alias index (unresolved x{counters.get('unresolved-terms',0)} kept as slugs, counted).",
 f"- **updated[]** (entries counted: {counters.get('updated-entries',0)}): the update history of a rule or an indicator "
 f"stands on its Requirement, in the compat facet under `history`; that of a term on the corpus root Set, in "
 f"narrative@1 under `term-updated`, by term id; each entry as the source writes it. Until 2026-11-14 it was a "
 f"declared drop; the author decided that it is carried.",
 f"- **CTL Rev5 overlay ({counters.get('ctl-overlays',0)} entries)**: the guidance and the update history of an entry "
 f"are parked L2 on /set/ctl-overlay. Its ODP assignments are not parked: they are the operations of the "
 f"`rev5-odp-overlay` Tailoring (the line on the drained assignments above). Until 2026-11-14 this line read as if "
 f"the assignments were parked too and waited for gate item 3; the ledger finds each of them in an operation.",
 f"- **flows** x{counters.get('flows',0)}: a process flow the source writes out (activity, nodes, steps) stands on "
 f"its family's Set, in the compat facet under `flows`, as the source writes it (until 2026-11-14 a declared drop, "
 f"by D17); dangling related refs x{dangling_related}.",
 f"- **Payload free text language-tagged** per corpus language (`{{en: ...}}`), harmonized 2026-07-21 (backlog #12): "
 +", ".join(f"{k} x{v}" for k,v in sorted(lang_wraps.items()))+". "
 f"Left bare by the label/identifier rule: term headwords x{len(terms_payload)}, glossary-info block metadata, "
 f"reference/schema-name citation labels, following-information sentence lists (kernel `text` decision pending, backlog #12). "
 f"Left as-source by the verbatim rule: free text quoted inside L2 `class-variants` payloads (per-class "
 f"descriptions/notes, e.g. pain_timeframes[].fir.description) - preserved-in-full waiting rooms are quotations, "
 f"not authored payload (report, never repair); they drain with the payloads themselves. "
 f"Stub-file `note` annotations are schema metadata, not corpus content.\n",
 "## Findings (computed)\n",
 f"- **Census, layered:** rules = **{sum(n_rules.values())}** = {n_rules['all']} track-independent (data.all) + "
 f"{n_rules['rev5']} rev5-only + {n_rules['20x']} 20x-only. "
 f"Rule-level force totals {dict(mod_hist)}; the {n_force} forces stated at rule level and the {n_vforce} stated "
 f"in class variants are {n_force+n_vforce} force values, the number a census gets that counts the two together.",
 f"- **Framework-specific subsets x{counters.get('track-declared-subsets',0)}** (CSX/CSF) read from info.20x.subsets / "
 f"info.rev5.subsets per FedRAMP's layering (global by default, specific when needed). CORRECTION: an earlier "
 f"version of this report misreported these as undeclared - a checker bug on our side, fixed after review in "
 f"FedRAMP community discussion #153.",
 (f"- **Zero easings across {sum(ops_emitted.values())} class-variant modality ops**: every published class delta tightens "
  f"or specifies - the Deviation channel stayed empty by measurement, not by assumption." if dev_records==0 else
  f"- **{dev_records} easings among {sum(ops_emitted.values())} class-variant ops**: each carries a converter "
  f"Deviation (approver: FedRAMP, rationale: published class variant)."),
 f"- Rules without base statements exist (x{synth_prose}) - CR26 itself models some obligations *only* as class "
 f"variants; the Set+Tailoring decomposition makes that explicit.",
 f"- **Deviation ceremony question (spec feedback):** authority-published prose variants would require "
 f"replace-prose(substantive)+Deviation under D13; converter parks prose variance in L2 instead - "
 f"open design question for v0.6."]
md+=["\n## Conversion ledger (measured per source value)\n",
 f"The path map says where a source path is declared to go. The ledger follows each of the "
 f"{LEDGER['leaf-values']:,} source leaf values, flags and fractions among them: a value the converter hands on "
 f"unchanged carries its origin into the bundle, a value it computes is stated as a named rule, and after the "
 f"bundle is written every claim is read back from the files. `{LEDGER_FILE}` holds the result, one row per source "
 f"path and outcome (backlog #41). Real content is never dropped (author, 2026-11-14): a value is carried, or it is "
 f"no content by a rule the ledger checks, and a run with one unaccounted value ends with 1.\n",
 f"- **{LT['copied']:,} copied**: the value stands, with its type, at the destination named.",
 f"- **{LT['transformed']:,} transformed** by a named rule; the rule was applied to the source again and the result "
 f"compared with the file. A value that is copied to one place and transformed for another counts as copied.",
 f"- **{LT['not-content']:,} no content** by a checked rule (a name that only selects a field, a namespace, an id "
 f"that is rebuilt exactly from another value)."
 +(" This source has no value of the three kinds, and the converter declares none." if not not_content else ""),
 f"- **{LT['intentionally-dropped']:,} dropped for a declared reason**: the two classes that were declared before "
 f"the author's rule, exactly the paths the path map marks `{DROP}`. Neither is one of the three kinds above. "
 f"Whether they are content is the author's to decide; they are listed below with the converter's reading.",
 f"- **{LT['unaccounted']:,} unaccounted**: no destination and no declared reason.",
 f"- Claims that did not hold against the written files: **{len(LFAIL)}**.",
 f"- Rows of the path map that the ledger contradicts (a destination named and a value of the path written "
 f"nowhere; a path declared not carried and written all the same; a row marked L1 whose values stand only in the "
 f"parked L2 payload): **{len(claims)}**"
 +("." if not claims else ": "+"; ".join(f"`{c['path']}` ({c['level']})" for c in claims)+"."),
 "\n### Rules\n",
 "Each rule is a function of source values; a rule's count is the number of source values it accounts for.\n",
 "| rule | source values |\n|---|---:|"]
md+=[f"| {r} | {n:,} |" for r,n in sorted(rules_used.items())]
md+=["\n### No content, by a checked rule\n","| kind | rule | source values |\n|---|---|---:|"]
md+=[f"| {k} | {r} | {n:,} |" for (k,r),n in sorted(not_content.items())] or ["| *(none)* | | 0 |"]
md+=["\n### Declared drops, and the converter's reading of each\n",
 "Declared before 2026-11-14 and left declared: the author decides whether a class is content. The reading is the "
 "converter's and decides nothing. The example is a value of the class that is no prose (a date, an id), with "
 "its pointer.\n",
 "| source paths | values | declared reason | example | reading |\n|---|---:|---|---|---|"]
md+=[f"| {'<br>'.join('`'+x['path']+'` x'+str(x['count']) for x in dd['paths'])} | {dd['source-values']:,} | {dd['reason']} | "
     f"`{dd['example']['source']}`"+(f" = `{dd['example']['value']}`" if "value" in dd["example"] else "")
     +f" | {dd['reading']} |" for dd in declared_drops] or ["| *(none)* | 0 | | | |"]
md+=["\n### Unaccounted\n",
 "No destination, no checked rule and no declared reason. A run with one such value ends with 1.\n",
 "| path | values | first value |\n|---|---:|---|"]
md+=[f"| `{u['path']}` | {u['count']} | `{u['example']}` |" for u in unacc] or ["| *(none)* | 0 | |"]
if n_null: md+=[f"\nThe source has {n_null} null value(s). A null states nothing and carries no origin; the ledger reads it as unaccounted."]
md+=["\n### What the ledger cannot see\n",
 "The ledger follows source values into the bundle, not the bundle back to the source. A value the converter writes "
 "on its own has no source value behind it and no entry: a constant (a lifecycle, a relationship, a tightening, the "
 "rationale of a Mapping), an id, a label or a file name minted from a KEY of the source (the id of a rule, a term, "
 "a family, a subset; keys are not leaf values), the membership and the order of a Set, the party written where the "
 "source names nobody, and the Requirements copied from the SP 800-53 bundle. Counted on the written objects and "
 "the manifest:\n",
 "| written as | leaf values | with no source value behind them |\n|---|---:|---:|"]
md+=[f"| {k} | {bundle_leaves[k]:,} | {own_values[k]:,} |" for k in sorted(bundle_leaves)]
md+=[f"| **all** | **{sum(bundle_leaves.values()):,}** | **{sum(own_values.values()):,}** |"]
md+=["\n## Full path map\n| path | count | level | destination |\n|---|---:|---|---|"]
for p,n,l,t in rows: md.append(f"| `{p}` | {n:,} | {l} | {t} |")
md.append("\n## UNMAPPED (gate target: zero)\n")
if unmapped:
    md.append("| path | count |\n|---|---:|")
    for p,n in unmapped: md.append(f"| `{p}` | {n} |")
else: md.append("*(none)*")
with open(RMD,"w",encoding="utf-8",newline="\n") as f: f.write("\n".join(md)+"\n")
print(f"reqs(rules+ksi): {nreq}  mappings: {mappings}  sets: {nset}  tailorings: {ntail}  objects: {len(objects)}")
print(f"leaves: {total:,}  mapped: {mapped:,}  UNMAPPED: {total-mapped}")
print("modality:",dict(mod_hist)," ops:",dict(ops_emitted)," conv-deviations:",dev_records)
print("counters:",dict(counters)," synth:",synth_prose)
print(f"ledger: copied {LT['copied']:,}, transformed {LT['transformed']:,}, no content {LT['not-content']:,}, dropped for a "
      f"declared reason {LT['intentionally-dropped']:,}, unaccounted {LT['unaccounted']:,}; failed checks {len(LFAIL)}; "
      f"path-map rows contradicted {len(claims)}")
if unacc:
    print("UNACCOUNTED:")
    for u in unacc: print("  ",u["path"],"x",u["count"],"- first:",u["example"])
for c in claims: print("PATH MAP CONTRADICTED:",c)
if LFAIL:
    print("LEDGER CLAIMS THAT DO NOT HOLD:"); [print("  ",x) for x in LFAIL[:30]]
print("written:",OUTDIR)
# The exit code says what the gates say. The bundle, the reports and the
# ledger record are on disk either way: they say what is wrong.
#   UNMAPPED = 0: every source leaf has a row in the path map.
#   The ledger: no claim fails against the written files, and no source value
#   is unaccounted (ledger_gate; author, 2026-11-14: "a converter run with an
#   unaccounted value exits non-zero").
if unmapped:
    print("UNMAPPED:"); [print("  ",p,"x",n) for p,n in unmapped]
    sys.stdout.flush()
    raise SystemExit(f"convert_cr26.py: {total-mapped} source leaf value(s) on {len(unmapped)} path(s) have no declared "
                     f"destination (gate: UNMAPPED = 0). The bundle is not a complete conversion of this source. The "
                     f"conversion ledger of this run: {len(LFAIL)} claim(s) that do not hold, {LT['unaccounted']} source "
                     f"value(s) unaccounted.")
sys.stdout.flush()
ledger_gate(LEDGER,"convert_cr26.py")
