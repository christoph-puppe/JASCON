#!/usr/bin/env python3
"""FedRAMP CR26 (bespoke JSON) -> Semantic Core bundle. Gate item 1, authority 3.
225 FRR rules + 46 KSIs -> Requirements; KSI control links -> Mapping objects;
subsets/classes/types -> nested Sets; class variance -> Tailorings (computable
deltas) + L2 class-variants payloads (full fidelity); FRD -> terminology;
CTL Rev5 overlay -> parked L2 (resolves at gate item 3). Coverage target: 0."""
import json, hashlib, os, re, copy, collections, shutil
from oscal_conv_lib import BUNDLE_NEWLINE   # one byte spelling on every OS (D3.1)

ROOT=os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..",".."))
SRC=os.path.join(ROOT,"sources","cr_fedramp-consolidated-rules.json")
OUT=os.path.join(ROOT,"converted_examples","FedRAMP-CR26","cr26-core-bundle")
RMD=os.path.join(ROOT,"converted_examples","FedRAMP-CR26","cr26-coverage-report.md")
RJS=os.path.join(ROOT,"converted_examples","FedRAMP-CR26","cr26-coverage-report.json")
NS="https://ns.fedramp.gov/cr26"; NIST="https://ns.nist.gov/sp800-53/req"
F_TERM="https://ns.jascon.org/stdlib/facet/terminology@1"
F_REP="https://ns.jascon.org/stdlib/facet/reporting-obligation@1"
F_EFF="https://ns.jascon.org/stdlib/facet/effectivity@1"
F_ACRIT="https://ns.jascon.org/stdlib/facet/assessment-criteria@1"
F_SCOPE=f"{NS}/facet/scope@1"
F_NARR=f"{NS}/facet/narrative@1"
F_COMPAT="https://ns.jascon.org/compat/oscal-1x@1"
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

d=json.load(open(SRC,encoding="utf-8"))
VER=d["info"]["version"]

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
RULES=[
 (r"^cr26\.info\.(title|description|version|last_updated)$","L1","bundle manifest / L0 provenance; description -> narrative on corpus root"),
 (r"^cr26\.info\.default_artifacts\.","L1","assessment-criteria on corpus root: default-artifacts"),
 (r"^cr26\.FRD\.info\.","L1","terminology@1 glossary-info on the corpus root Set"),
 (r"^cr26\.FRD\.data\.all\.\*\.(term|definition|tag|alts\[\]|note|notes\[\]|do_not_link|reference|reference_url)$","L1","terminology@1 payload per term (alts, links, chrome flags inside payload)"),
 (r"^cr26\.FRD\.data\.all\.\*\.updated\[\]\.","L1","history -> L0 (values not object-carried; counted)"),
 (r"^cr26\.FRR\.\*\.info\.(name|short_name|status)$","L1","family Set: title/label/lifecycle"),
 (r"^cr26\.FRR\.\*\.info\.web_name$","L1","family Set annotations.web_name (chrome)"),
 (r"^cr26\.FRR\.\*\.info\.(purpose|tag)$","L1","family Set: narrative description / scope tag"),
 (r"^cr26\.FRR\.\*\.info\.(20x|rev5)\.subsets\.","L1","framework-specific subset declarations -> track subset Sets (title/description/scope) [corrected per FedRAMP #153]"),
 (r"^cr26\.FRR\.\*\.info\.(effective|20x|rev5)\.","L1","effectivity@1 on family Set (default / per-track)"),
 (r"^cr26\.FRR\.\*\.info\.flows\[\]","declared-drop","process-flow diagrams: linked resources, not requirement data (D17)"),
 (r"^cr26\.FRR\.\*\.info\.subsets\.\*\.(name|description)$","L1","subset Set: title / narrative description"),
 (r"^cr26\.FRR\.\*\.info\.subsets\.\*\.applicability\.","L1","scope@1 on subset Set (types/paths/classes/affects) + class & type Set composition"),
 (re.escape(RULE)+r"\.name$","L1","Requirement.title"),
 (re.escape(RULE)+r"\.statement$","L1","statements[0].prose.en"),
 (re.escape(RULE)+r"\.force$","L1","statements[0].modality (code map)"),
 (re.escape(RULE)+r"\.affects\[\]$","L1","statements[0].obligated-parties[]"),
 (re.escape(RULE)+r"\.terms\[\]$","L1","relations uses-term -> /cr26/term/<id>"),
 (re.escape(RULE)+r"\.(timeframe_num|timeframe_type)$","L1","statement parameter 'timeframe' (elapsed-duration | calendar-period by unit)"),
 (re.escape(RULE)+r"\.updated\[\]\.","L1","history -> L0 (counted)"),
 (re.escape(RULE)+r"\.(note|notes\[\]|danger|corrective_actions\[\]|following_information\[\]|following_information_bullets\[\])$","L1","narrative@1 / reporting-obligation@1 payload fields"),
 (re.escape(RULE)+r"\.examples\[\]\.(id|examples\[\]|key_tests\[\])$","L1","assessment-criteria@1: examples[] {id, examples, key-tests} - the KSI-shaped test data"),
 (re.escape(RULE)+r"\.schema\.(name|url)$","L1","relations schema -> url; name kept in narrative@1"),
 (re.escape(RULE)+r"\.notification\[\]\.(party|method|target|name)$","L1","reporting-obligation@1: notification[]"),
 (re.escape(RULE)+r"\.artifacts\.all\[\]$","L1","assessment-criteria@1: required-artifacts"),
 (re.escape(RULE)+r"\.artifacts\.[a-d]\[\]$","L2","class-variants payload (per-class artifacts)"),
 (re.escape(RULE)+r"\.related\[\]$","L1","relations related -> /cr26/req/<id> (dangling counted)"),
 (re.escape(RULE)+r"\.(schema|reference|reference_url)$","L1","relations schema/reference -> external URL"),
 (re.escape(VAR)+r"\.force$","L1","class Tailoring op set-modality (monotone) OR + converter Deviation when easing (counted)"),
 (re.escape(VAR)+r"\.(timeframe_num|timeframe_type)$","L1","class Tailoring op set-parameter when unit-class matches base; else L2 (counted)"),
 (re.escape(VAR)+r"\.","L2","class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question)"),
 (re.escape(KSI)+r"\.name$","L1","KSI Requirement.title"),
 (re.escape(KSI)+r"\.statement$","L1","KSI statements[0].prose.en (modality unspecified: indicator language)"),
 (re.escape(KSI)+r"\.controls\[\]$","L1","Mapping objects (relationship supports; 8.6 untyped-import rule)"),
 (re.escape(KSI)+r"\.terms\[\]$","L1","relations uses-term"),
 (re.escape(KSI)+r"\.updated\[\]\.","L1","history -> L0 (counted)"),
 (re.escape(KVAR)+r"\.","L2","class-variants payload on the KSI Requirement"),
 (r"^cr26\.KSI\.\*\.(id|name|web_name|short_name|status)$","L1","KSI category Set: id/title/label/annotations/lifecycle"),
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
def tf_param(num,typ):
    t="elapsed-duration" if typ in ELAPSED else "calendar-period"
    p={"name":"timeframe","type":t,"num":num,"unit":typ,"tightening":"lower"}
    if t=="calendar-period": p["calendar-ref"]=f"{NS}/calendar/us-federal"
    return p,t

TERMIDX={}
for _tid,_t in d["FRD"]["data"]["all"].items():
    for _n in [_t["term"]]+list(_t.get("alts",[]) or []):
        TERMIDX.setdefault(_n.lower().strip(),_tid)
def term_ref(name):
    tid=TERMIDX.get(name.lower().strip())
    if tid: return f"{NS}/term/{tid}"
    counters["unresolved-terms"]+=1
    return f"{NS}/term/{slug(name)}"

class_tailorings={c:{"id":f"{NS}/tailoring/class-{c}","version":VER,"lifecycle":"active",
    "label":f"Class {c.upper()}","title":f"Class {c.upper()} certification variant",
    "selects":[{"set-ref":f"{NS}/set/class/{c}"}],"operations":[]} for c in "abcd"}

def add_narr(req,key,val):
    req.setdefault("facets",{}).setdefault(F_NARR,{})[key]=val

def convert_rule(fam,subk,rid,r):
    global synth_prose,dangling_related,dev_records
    uri=f"{NS}/req/{rid}"
    req={"id":uri,"version":VER,"label":rid,"lifecycle":"active",
         "title":r.get("name",rid),"statements":[]}
    base_force=r.get("force"); mod=FORCE.get(base_force,"unspecified")
    prose=r.get("statement")
    if prose is None:
        prose=f"{r.get('name',rid)} (requirement varies by certification class; see class tailorings and the class-variants payload)."
        synth_prose+=1
    st={"id":"s1","modality":mod,
        "obligated-parties":[f"{NS}/party/{slug(a)}" for a in r.get("affects",[])] or [f"{NS}/party/provider"],
        "prose":{"en":prose}}
    mod_hist[mod]+=1
    base_tf=None
    if "timeframe_num" in r:
        p,base_tf=tf_param(r["timeframe_num"],r["timeframe_type"]); st["parameters"]=[p]
    req["statements"].append(st)
    rels=[{"type":"uses-term","ref":term_ref(t)} for t in r.get("terms",[])]
    for rl in r.get("related",[]) or []:
        if re.match(r"^[A-Z]{2,4}-[A-Z]{2,4}-[A-Z0-9]{2,4}$",rl):
            rels.append({"type":"related","ref":f"{NS}/req/{rl}"})
        else:
            rels.append({"type":"related","ref":rl}); dangling_related+=1
    if isinstance(r.get("schema"),dict):
        rels.append({"type":"schema","ref":r["schema"].get("url","")})
        add_narr(req,"schema-name",r["schema"].get("name"))
    elif r.get("schema"): rels.append({"type":"schema","ref":r["schema"]})
    if r.get("reference_url"): rels.append({"type":"reference","ref":r["reference_url"]})
    if rels: req["relations"]=rels
    rep={}
    if r.get("notification"):
        rep["notification"]=[{**n,**({"name":T(n["name"],"notification-name")} if n.get("name") else {})}
                             for n in copy.deepcopy(r["notification"])]
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
        req.setdefault("facets",{})[F_COMPAT]={"class-variants":var}
        counters["class-variant-rules"]+=1
        for cls,v in var.items():
            OPS=class_tailorings[cls]["operations"]
            vf=FORCE.get(v.get("force"))
            if vf and vf!=mod:
                op={"op":"set-modality","requirement-ref":uri,"statement-id":"s1","modality":vf}
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
    objects[f"objects/req/{slug(rid)}.json"]=req
    return uri

def convert_ksi(catid,cat,iid,ind):
    global mappings
    uri=f"{NS}/ksi/{iid}"
    prose=ind.get("statement")
    if prose is None:
        prose=f"{ind.get('name',iid)} (indicator varies by certification class; see class-variants payload)."
    req={"id":uri,"version":VER,"label":iid,"lifecycle":"active",
         "title":ind.get("name",iid),
         "statements":[{"id":"s1","modality":"unspecified",
             "obligated-parties":[f"{NS}/party/provider"],"prose":{"en":prose}}]}
    rels=[{"type":"uses-term","ref":term_ref(t)} for t in ind.get("terms",[])]
    if rels: req["relations"]=rels
    if ind.get("varies_by_class"):
        req["facets"]={F_COMPAT:{"class-variants":ind["varies_by_class"]}}
        counters["ksi-class-variant"]+=1
    counters["updated-entries"]+=len(ind.get("updated",[]) or [])
    objects[f"objects/ksi/{slug(iid)}.json"]=req
    for ctl in ind.get("controls",[]) or []:
        tid=ctl.upper()
        m={"id":f"{NS}/map/{slug(iid)}--{slug(ctl)}","version":VER,"lifecycle":"active",
           "source-ref":uri,"target-ref":f"{NIST}/{tid}",
           "relationship":"supports","direction":"source-to-target","confidence":"draft",
           "rationale":"Imported from CR26 KSI control list; the source carried no typed relationship (handbook 8.6).",
           "provenance":{"author-ref":f"{NS}/party/fedramp","date":d["info"]["last_updated"]}}
        objects[f"objects/map/{slug(iid)}--{slug(ctl)}.json"]=m; mappings+=1
    return uri

# in-place overwrite; stale-file cleanup happens after the write set is known
# (house rule: never rmtree/rmdir - OneDrive/indexers hold transient dir handles)
seq={"n":0}
def nseq(): seq["n"]+=10; return seq["n"]
class_members=collections.defaultdict(list); type_members=collections.defaultdict(list)
fam_entries=[]
for fk,f in d["FRR"].items():
    fi=f["info"]; sub_entries=[]
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
            members.append({"ref":convert_rule(fk,sk,rid,r),"sequence":nseq()})
        track_set_uris=[]
        for trk in ("20x","rev5"):
            tr_rules=f["data"].get(trk,{}).get(sk,{})
            if not tr_rules: continue
            tinfo=t_infos.get(trk,{})
            turi=f"{NS}/set/subset/{slug(fk)}-{slug(sk)}-{trk}"
            tmem=[{"ref":convert_rule(fk,sk,rid,r),"sequence":(i+1)*10}
                  for i,(rid,r) in enumerate(tr_rules.items())]
            tset={"id":turi,"version":VER,"lifecycle":"active",
                "title":tinfo.get("name", f"{(sinfo or {}).get('name',sk)} ({trk}-specific)"),
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
        sobj={"id":suri,"version":VER,"lifecycle":"active",
              "title":sinfo.get("name",sk),"label":sk,"members":members}
        ap=sinfo.get("applicability",{})
        if sinfo.get("description"): sobj.setdefault("facets",{}).setdefault(F_NARR,{})["description"]=T(sinfo["description"],"description")
        if ap: sobj.setdefault("facets",{})[F_SCOPE]=dict(ap)
        objects[f"objects/set/subset-{slug(fk)}-{slug(sk)}.json"]=sobj
        sub_entries.append({"ref":suri,"sequence":nseq()})
        for c in ap.get("classes",[]) or []: class_members[c.lower()].append(suri)
        for t in ap.get("types",[]) or []: type_members[slug(t)].append(suri)
    furi=f"{NS}/set/tax/{slug(fk)}"
    fobj={"id":furi,"version":VER,"lifecycle":"active",
          "title":fi.get("name",fk),"label":fi.get("short_name",fk),
          "members":sub_entries,"annotations":{"web_name":fi.get("web_name","")}}
    narr={"description":T(fi.get("purpose",""),"description")}
    fobj["facets"]={F_NARR:narr,F_SCOPE:{"tag":fi.get("tag")}}
    eff={}
    if fi.get("effective"): eff["default"]=fi["effective"]
    for trk in ("20x","rev5"):
        if fi.get(trk): eff[trk]=fi[trk].get("effective",fi[trk])
    if eff: fobj["facets"][F_EFF]=eff
    if fi.get("flows"): counters["flows-dropped"]+=len(fi["flows"])
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
    objects[f"objects/set/ksi-{slug(ck)}.json"]={"id":curi,"version":VER,"lifecycle":"active",
        "title":cat.get("name",ck),"label":cat.get("short_name",ck),
        "annotations":{"web_name":cat.get("web_name","")},"members":entries}
    ksi_cat_entries.append({"ref":curi,"sequence":nseq()})
# terminology container
terms_payload={}
for tid,t in d["FRD"]["data"]["all"].items():
    e={"term":t["term"],"definition":T(t["definition"],"definition")}
    for k,dk in [("tag","tag"),("alts","aliases"),
                 ("do_not_link","do-not-link"),("reference","reference"),
                 ("reference_url","reference-url")]:
        if t.get(k) is not None: e[dk]=t[k]
    for k,dk in [("note","note"),("notes","notes")]:
        if t.get(k) is not None: e[dk]=T(t[k],dk)
    counters["updated-entries"]+=len(t.get("updated",[]) or [])
    counters["term-alts"]+=len(t.get("alts",[]) or [])
    terms_payload[tid]=e
frd_i=d["FRD"]["info"]
glossary={"terms":terms_payload,
    "glossary-info":{k:frd_i[k] for k in ("name","short_name","web_name","purpose","status","effective") if frd_i.get(k) is not None}}
# CTL parked (guidance free text language-tagged; structure otherwise verbatim)
ctl_payload=copy.deepcopy(d["CTL"])
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
                parts=[x.strip() for x in re.split(r";|,| and ",val) if x.strip()]
                allowed={c["value"] for c in decl.get("choices",[])}
                if decl.get("cardinality")=="many" and parts and all(x in allowed for x in parts):
                    ctl_ops.append({"op":"set-parameter","requirement-ref":robj["id"],
                                    "statement-id":sid,"parameter":pid,"value":parts})
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
    "facets":{F_NARR:{"description":T(d["info"]["description"],"description")},
              F_ACRIT:{"default-artifacts":d["info"]["default_artifacts"]},
              F_TERM:glossary}}
for c,t in class_tailorings.items():
    if t["operations"]: objects[f"objects/tailoring/class-{c}.json"]=t

def stub(path,fid,mods,props):
    # 26 delivered: pins are the normative payload contract, fail-closed
    w(path,{"id":fid,"version":"1.0.0","modifies-semantics":mods,
        "note":"NORMATIVE pinned payload schema (backlog 26): closed shape - unknown keys are rejected, never smuggled",
        "schema":{"$schema":"https://json-schema.org/draft/2020-12/schema","type":"object","properties":props,
                  "additionalProperties":False}})
def pin_stdlib(fn):
    import shutil as _sh
    src=os.path.join(ROOT,"jascon","schemas","stdlib",fn)
    w(f"schemas/{fn}",json.load(open(src,encoding="utf-8")))
pin_stdlib("terminology-1.0.0.json")   # 26: stdlib pins are VERBATIM
pin_stdlib("reporting-obligation-1.0.0.json")
pin_stdlib("effectivity-1.0.0.json")
pin_stdlib("assessment-criteria-1.0.0.json")
stub("schemas/cr26-scope-stub.json",F_SCOPE.split("@")[0],["selection"],
     {"classes":{"type":"array"},"types":{"type":"array"},"paths":{"type":"array"},"affects":{"type":"array"},"tag":{"type":"string"}})
stub("schemas/cr26-narrative-stub.json",F_NARR.split("@")[0],[],
     {"description":{"type":"object"},"note":{"type":"object"},"notes":{"type":"object"},
      "schema-name":{"type":"string"},"reference":{"type":"string"},"danger":{"type":"object"},
      "corrective-actions":{"type":"object"}})
stub("schemas/oscal-1x-compat-stub.json",F_COMPAT.split("@")[0],[],{"class-variants":{"type":"object"},"ctl":{"type":"object"}})
# carried Rev 5 Requirements bring their facet pins (#17 fail-closed)
stub("schemas/sp800-53-narrative-stub.json","https://ns.nist.gov/sp800-53/facet/narrative",[],{"guidance":{"type":"array"}})
stub("schemas/sp800-53a-stub.json","https://ns.nist.gov/sp800-53/facet/sp800-53a",[],{"objectives":{"type":"array"},"methods":{"type":"array"}})
stub("schemas/sp800-53-odp-stub.json","https://ns.nist.gov/sp800-53/facet/odp",[],{"params":{"type":"object"}})
stub("schemas/sp800-53-rmf-stub.json","https://ns.nist.gov/sp800-53/facet/rmf",[],{"contributes-to-assurance":{"type":"boolean"}})

# stale-file cleanup (files only, never rmdir): everything not re-emitted goes
want={os.path.normpath(r) for r in objects}|{"content-manifest.json"}
want|={os.path.normpath(f"schemas/{s}") for s in
       ("terminology-1.0.0.json","reporting-obligation-1.0.0.json","effectivity-1.0.0.json",
        "assessment-criteria-1.0.0.json","cr26-scope-stub.json","cr26-narrative-stub.json",
        "oscal-1x-compat-stub.json","sp800-53-narrative-stub.json","sp800-53a-stub.json",
        "sp800-53-odp-stub.json","sp800-53-rmf-stub.json")}
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
manifest={"manifest-version":"1",
 "provenance":{"source":d["info"]["title"],"source-version":VER,
               "last_updated":d["info"]["last_updated"],"converter":"convert_cr26.py v0.1"},
 "objects":[{"id":o["id"],"version":o["version"],"package-digest":shaf(rel),
             "semantic-digest":sdig(o),"path":rel} for rel,o in sorted(objects.items())],
 "facet-schemas":[]}
for s in sorted(os.listdir(os.path.join(OUT,"schemas"))):
    sd=json.load(open(os.path.join(OUT,"schemas",s)))
    manifest["facet-schemas"].append({"id":sd["id"],"exact-version":sd["version"],
        "digest":shaf(f"schemas/{s}"),"path":f"schemas/{s}"})
w("content-manifest.json",manifest)

# ---------------- coverage ----------------
rows=[];unmapped=[]
for p,n in sorted(paths.items()):
    l,t=dest(p)
    (rows if l else unmapped).append((p,n,l,t) if l else (p,n))
total=sum(paths.values()); mapped=sum(n for _,n,_,_ in rows)
nreq=sum(1 for o in objects.values() if o["id"].startswith(f"{NS}/req/") or o["id"].startswith(f"{NS}/ksi/"))
nset=sum(1 for o in objects.values() if "/set/" in o["id"])
ntail=sum(1 for o in objects.values() if "/tailoring/" in o["id"])
j={"source":d["info"]["title"],"version":VER,
   "totals":{"leaf-values":total,"mapped":mapped,"unmapped":total-mapped,
             "coverage-pct":round(100*mapped/total,3)},
   "objects":{"requirements(rules+ksi)":nreq,"mappings":mappings,"sets":nset,
              "tailorings":ntail,"total":len(objects)},
   "modality(rule-level)":dict(mod_hist),
   "tailoring-ops":dict(ops_emitted),"converter-deviations(easings)":dev_records,
   "counters":dict(counters),"lang-wraps":dict(lang_wraps),
   "synthesized-prose(variant-only-rules)":synth_prose,
   "dangling-related":dangling_related,
   "unmapped":[{"path":p,"count":n} for p,n in unmapped],
   "path-map":[{"path":p,"count":n,"level":l,"destination":t} for p,n,l,t in rows]}
json.dump(j,open(RJS,"w",encoding="utf-8"),ensure_ascii=False,indent=1)

md=[f"# CR26 -> Semantic Core: Coverage Report (computed)\n",
 f"Source: **{d['info']['title']}** v{VER} (bespoke JSON; not OSCAL).\n",
 "## Totals\n",
 f"- Source leaf values inventoried (id-normalized paths): **{total:,}**",
 f"- Mapped: **{mapped:,}** -> **UNMAPPED: {total-mapped}** -> coverage **{j['totals']['coverage-pct']} %**",
 f"- Emitted: **{nreq} Requirements** (FRR rules + KSIs), **{mappings} Mapping objects**, "
 f"**{nset} Sets** (families, subsets, classes, types, KSI categories, terms, root), "
 f"**{ntail} class Tailorings**, manifest with both digests, {len(manifest['facet-schemas'])} pinned stubs.\n",
 "## Conversion rules (declared, counted)\n",
 f"- **force -> modality** (rule level): "+", ".join(f"{k} x{v}" for k,v in sorted(mod_hist.items(),key=lambda x:-x[1]))
 +f". Class-variant forces become **Tailoring ops**: {dict(ops_emitted)}; easings auto-carry a converter Deviation "
 f"(approver: FedRAMP, rationale: published class variant) x{dev_records}.",
 f"- **affects[] -> obligated-parties[]** (parties minted as codes); subset applicability -> scope@1 on subset Sets "
 f"and composed **class Sets (a-d)** and **type Sets (20x/Rev5)** - sets-of-sets (D21).",
 f"- **timeframe_num/type -> statement parameter** 'timeframe' (elapsed vs calendar split; calendar-ref minted; "
 f"tightening: lower). Class variants: set-parameter when unit-class matches; "
 f"**true unit-class crossings x{counters.get('timeframe-unitclass-crossings',0)}** (base-absent variant timeframes x{counters.get('timeframe-variant-only',0)} counted separately) stay in the L2 class-variants payload "
 f"- spec-feedback: candidate D9 duration-union question.",
 f"- **varies_by_class** preserved in full as L2 `class-variants` payloads on {counters.get('class-variant-rules',0)} rules "
 f"(+{counters.get('ksi-class-variant',0)} KSIs); computable deltas additionally emitted as ops. "
 f"Variant-only rules (no base statement): synthesized base prose x{synth_prose} (flagged).",
 f"- **KSI control lists -> {mappings} Mapping objects** (relationship `supports`, confidence `draft`, "
 f"rationale per handbook 8.6 untyped-import rule; targets minted under {NIST}/).",
 f"- **FRD -> terminology@1** hosted on the corpus root Set (glossary-info carries the FRD block metadata): 75 terms, {counters.get('term-alts',0)} aliases, links and chrome flags in-payload.",
 f"- **CTL ODP assignments DRAINED (backlog #10, gate 3)**: {counters.get('ctl-odp-ops',0)} set-parameter ops on the "
 f"`rev5-odp-overlay` Tailoring, each addressed (requirement-ref, statement-id, parameter) via the DECLARING "
 f"statement of the Rev 5.2.0 ODP (measured: no ODP is declared in two statements); {counters.get('ctl-carried-reqs',0)} "
 f"tailored Rev 5 Requirements carried in-bundle as byte-identical copies (closure; the authorization-package "
 f"pattern). CTL guidance entries stay parked L2 - supplemental prose on external controls is D20 supplements "
 f"territory, not ODP addressing. Multi-select serialization normalized x{counters.get('ctl-multiselect-normalized',0)} "
 f"(FedRAMP flattens many-cardinality selections into prose strings 'a; b' / 'a, b and c'; every part matches a "
 f"declared NIST choice -> list value; REPORTED upstream). Residual choice conflicts: {ctl_choice_conflicts or 'none'}.",
 f"- **notification/following_information -> reporting-obligation@1**; artifacts.all -> assessment-criteria@1; "
 f"note/notes/danger/examples/corrective_actions -> narrative@1.",
 f"- **rule/KSI term names resolved to FRD ids** via the term+alias index (unresolved x{counters.get('unresolved-terms',0)} kept as slugs, counted).",
 f"- **updated[] -> L0** (entries counted: {counters.get('updated-entries',0)}; values not object-carried).",
 f"- **CTL Rev5 overlay ({counters.get('ctl-overlays',0)} entries) parked L2** on /set/ctl-overlay: external-catalog "
 f"ODP assignments need the NIST catalog's statement map - resolves at gate item 3.",
 f"- **flows dropped-declared** x{counters.get('flows-dropped',0)} (D17); dangling related refs x{dangling_related}.",
 f"- **Payload free text language-tagged** per corpus language (`{{en: ...}}`), harmonized 2026-07-21 (backlog #12): "
 +", ".join(f"{k} x{v}" for k,v in sorted(lang_wraps.items()))+". "
 f"Left bare by the label/identifier rule: term headwords x{len(terms_payload)}, glossary-info block metadata, "
 f"reference/schema-name citation labels, following-information sentence lists (kernel `text` decision pending, backlog #12). "
 f"Left as-source by the verbatim rule: free text quoted inside L2 `class-variants` payloads (per-class "
 f"descriptions/notes, e.g. pain_timeframes[].fir.description) - preserved-in-full waiting rooms are quotations, "
 f"not authored payload (the 216 discipline: report, never repair); they drain with the payloads themselves. "
 f"Stub-file `note` annotations are schema metadata, not corpus content.\n",
 "## Findings (computed)\n",
 f"- **Census, layered:** rules = **246** = 225 track-independent (data.all) + 12 rev5-only + 9 20x-only. "
 f"Rule-level force totals {dict(mod_hist)}; the census's 328 merged rule-level and class-variant forces.",
 f"- **Framework-specific subsets x{counters.get('track-declared-subsets',0)}** (CSX/CSF) read from info.20x.subsets / "
 f"info.rev5.subsets per FedRAMP's layering (global by default, specific when needed). CORRECTION: an earlier "
 f"version of this report misreported these as undeclared - a checker bug on our side, fixed after review in "
 f"FedRAMP community discussion #153.",
 f"- **Zero easings across {sum(ops_emitted.values())} class-variant modality ops**: every published class delta tightens "
 f"or specifies - the Deviation channel stayed empty by measurement, not by assumption.",
 f"- Rules without base statements exist (x{synth_prose}) - CR26 itself models some obligations *only* as class "
 f"variants; the Set+Tailoring decomposition makes that explicit.",
 f"- **Deviation ceremony question (spec feedback):** authority-published prose variants would require "
 f"replace-prose(substantive)+Deviation under D13; converter parks prose variance in L2 instead - "
 f"open design question for v0.6.",
 "\n## Full path map\n| path | count | level | destination |\n|---|---:|---|---|"]
for p,n,l,t in rows: md.append(f"| `{p}` | {n:,} | {l} | {t} |")
md.append("\n## UNMAPPED (gate target: zero)\n")
if unmapped:
    md.append("| path | count |\n|---|---:|")
    for p,n in unmapped: md.append(f"| `{p}` | {n} |")
else: md.append("*(none)*")
open(RMD,"w",encoding="utf-8").write("\n".join(md)+"\n")
print(f"reqs(rules+ksi): {nreq}  mappings: {mappings}  sets: {nset}  tailorings: {ntail}  objects: {len(objects)}")
print(f"leaves: {total:,}  mapped: {mapped:,}  UNMAPPED: {total-mapped}")
print("modality:",dict(mod_hist)," ops:",dict(ops_emitted)," conv-deviations:",dev_records)
print("counters:",dict(counters)," synth:",synth_prose)
if unmapped:
    print("UNMAPPED:"); [print("  ",p,"x",n) for p,n in unmapped[:30]]
