#!/usr/bin/env python3
"""Gate 4 (spec IV.5.4): the bidirectional export test suite.

Semantic Core catalog bundles -> syntactically valid OSCAL 1.2.2 catalog
JSON, validated against the OFFICIAL NIST schema, then re-imported by a
generic importer and compared object-by-object via SEMANTIC DIGEST.

The projection is honest OSCAL where OSCAL has the construct:
statements -> parts ({param:x} -> {{ insert: param, x }}), typed params ->
params (+ select for choices), relations -> links, the root-Set tree ->
groups, titles/labels natively. What OSCAL cannot say (modality,
obligated-parties, statement-scoped declarations, facets, lifecycle,
lineage, overlapping Set membership) rides namespaced props under
https://ns.oscal-semantic.org/core - the D16 compatibility channel, in
reverse. Sets additionally ride the props channel in full because the
catalog model cannot represent overlapping membership (baselines!) -
groups are the 1.x navigation view, the props channel is the exact one.

Supported corpus (declared): the catalog graph - Requirements + Sets
(4,583 + 1,066 of 6,675 objects). Mapping/Tailoring objects await the
OSCAL mapping/profile model exports; the lifecycle bundle awaits the
SSP-family exports. Skipped objects are counted, never silent.

Usage: uv run --with jsonschema python export_oscal.py
"""
import json, hashlib, os, re, sys, copy, collections, uuid
import jsonschema
import regex   # the OFFICIAL NIST JSON schema uses \p{L} Unicode property
               # escapes, which Python's stdlib `re` cannot compile - a
               # measured ecosystem cost (see gate-4-measurement.md)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
SC = "https://ns.oscal-semantic.org/core"
OSCHEMA = json.load(open(os.path.join(ROOT, "sources", "nist", "oscal_catalog_schema.json"), encoding="utf-8"))

def _pattern(validator, patrn, instance, schema):
    if validator.is_type(instance, "string") and not regex.search(patrn, instance):
        yield jsonschema.exceptions.ValidationError(f"{instance!r} does not match {patrn!r}")
OSCAL_V = jsonschema.validators.extend(jsonschema.Draft7Validator, {"pattern": _pattern})(OSCHEMA)

def _canon(o):
    if isinstance(o, dict):
        return {k: _canon(o[k]) for k in sorted(o.keys(), key=lambda s: s.encode("utf-16-be"))}
    if isinstance(o, list): return [_canon(x) for x in o]
    return o
def sdig(obj):
    o = copy.deepcopy(obj); o.pop("annotations", None)
    return "sha256:" + hashlib.sha256(json.dumps(_canon(o), separators=(",", ":"),
                                                 ensure_ascii=False).encode("utf-8")).hexdigest()
def cjson(v):
    return json.dumps(_canon(v), separators=(",", ":"), ensure_ascii=False)

INSERT_OUT = re.compile(r"\{param:([^}]+)\}")
INSERT_IN = re.compile(r"\{\{ insert: param, ([^ }]+) \}\}")

# ---------------- export ----------------
def prop(name, value, ns=SC, cls=None):
    p = {"name": name, "value": value}
    if ns: p["ns"] = ns
    if cls: p["class"] = cls
    return p

def tail(uri):
    return uri.rstrip("/").rsplit("/", 1)[-1]

def text_primary(v):
    """#12: kernel `text` = {BCP-47: string|[string]}. Returns (display, extra)
    where extra is a props list rebuilding the exact value on import."""
    if not isinstance(v, dict):
        return v, []
    langs = sorted(v.keys())
    first = v[langs[0]]
    if len(langs) == 1 and isinstance(first, str):
        if langs[0] == "en":
            return first, []
        return first, [prop("title-lang", langs[0])]
    return (first if isinstance(first, str) else " ".join(first)), [prop("title-json", cjson(v))]

def export_requirement(o, counters):
    cid = tail(o["id"]).lower()
    tdisp, textra = text_primary(o.get("title", cid))
    c = {"id": cid, "title": tdisp}
    props = [prop("canonical-id", o["id"]), prop("version", o["version"]),
             prop("lifecycle", o["lifecycle"])] + textra
    if o.get("label"): props.append({"name": "label", "value": o["label"]})
    params, parts = [], []
    for s in o["statements"]:
        pt = {"id": f"{cid}_{s['id']}", "name": "statement"}
        langs = sorted(s["prose"].keys())
        primary = s["prose"][langs[0]]
        if isinstance(primary, str) and len(langs) == 1:
            pt["prose"] = INSERT_OUT.sub(r"{{ insert: param, \1 }}", primary)
            if langs[0] != "en": pt["props"] = [prop("lang", langs[0])]
        else:   # multi-language or array prose: exact channel (counted)
            pt["props"] = [prop("prose-json", cjson(s["prose"]))]
            counters["prose-json-channel"] += 1
        pt.setdefault("props", []).append(prop("modality", s["modality"]))
        for op_ in s["obligated-parties"]:
            pt["props"].append(prop("obligated-party", op_))
        parts.append(pt)
        for d in s.get("parameters", []) or []:
            pm = {"id": d["name"], "props": [prop("statement", s["id"])]}
            if d.get("label"):
                pm["label"] = d["label"]
            elif "select" not in pm:
                # OSCAL params need label|select|values; the kernel does not.
                # Synthetic label + marker so the importer strips it back.
                pm["label"] = d["name"]
                pm["props"].append(prop("synthetic-label", "1"))
                counters["synthetic-param-labels"] += 1
            ch = d.get("choices")
            if d["type"] == "choice" and ch and all(isinstance(x.get("value"), str) and not x.get("label") for x in ch):
                pm["select"] = {"choice": [x["value"] for x in ch]}
                if d.get("cardinality") == "many": pm["select"]["how-many"] = "one-or-more"
                extra = {k: v for k, v in d.items() if k not in ("name", "label", "choices", "cardinality", "type")}
                extra["type"] = "choice"
            else:
                extra = {k: v for k, v in d.items() if k not in ("name", "label")}
                if d["type"] == "choice": counters["choice-json-channel"] += 1
            pm["props"].append(prop("decl", cjson(extra)))
            params.append(pm)
    if params: c["params"] = params
    c["props"] = props
    c["parts"] = parts
    rels = o.get("relations", []) or []
    if any(str(r["type"]).startswith("http") for r in rels):
        # OSCAL link rel is a TOKEN - URI-typed extension relations (#20)
        # cannot ride links; the whole ordered list takes the props channel
        # (order is digest-relevant). D16 asymmetry, counted.
        c["props"].append(prop("relations-json", cjson(rels)))
        counters["uri-rel-props-channel"] += 1
    else:
        links = [{"href": r["ref"], "rel": r["type"]} for r in rels]
        if links: c["links"] = links
    for k in ("facets", "annotations", "replaces", "aliases", "canonical-alias"):
        if o.get(k) is not None:
            c["props"].append(prop(k, cjson(o[k])))
    return c

def export_bundle(bdir, out_path, counters):
    manifest = json.load(open(os.path.join(bdir, "content-manifest.json"), encoding="utf-8"))
    objs, skipped = {}, collections.Counter()
    for e in manifest["objects"]:
        o = json.load(open(os.path.join(bdir, e["path"]), encoding="utf-8"))
        kind = "req" if "statements" in o else ("set" if "members" in o else None)
        if kind is None:
            skipped[e["path"].split("/")[1]] += 1; continue
        objs[o["id"]] = (kind, o)
    reqs = {i: o for i, (k, o) in objs.items() if k == "req"}
    sets = {i: o for i, (k, o) in objs.items() if k == "set"}
    # primary tree: prefer the set no other set references, id ending /root;
    # else the unreferenced set with the largest transitive cover
    referenced = {m["ref"] for s in sets.values() for m in s.get("members", [])}
    roots = [i for i in sets if i not in referenced]
    def cover(i, seen):
        if i in seen: return 0
        seen.add(i)
        n = 1
        for m in sets.get(i, {}).get("members", []) or []:
            if m["ref"] in sets: n += cover(m["ref"], seen)
            else: n += 1
        return n
    primary = next((i for i in roots if i.endswith("/root")), None) \
        or (max(roots, key=lambda i: cover(i, set())) if roots else None)
    placed = set()
    def build_group(sid):
        s = sets[sid]
        gt, _ = text_primary(s.get("title", tail(sid)))   # display only; the
        g = {"id": tail(sid).lower() or "g", "title": gt,  # exact Set rides props
             "props": [prop("canonical-id", sid)]}
        ctrls, subgroups = [], []
        for m in s.get("members", []) or []:
            r = m["ref"]
            if r in sets and r not in placed:
                placed.add(r)
                sub = build_group(r)
                if sub is not None: subgroups.append(sub)
            elif r in reqs and r not in placed:
                placed.add(r); ctrls.append(export_requirement(reqs[r], counters))
        # OSCAL 1.2.2 groups may carry EITHER subgroups OR controls, never
        # both (the anyOf is exclusive) - kernel Sets mix freely, so mixed
        # children get a synthetic wrapper group (navigation only; the exact
        # Set rides the props channel). D16 asymmetry, counted + reported.
        if subgroups and ctrls:
            subgroups.append({"id": g["id"] + "--controls", "title": g["title"],
                              "props": [prop("synthetic", "controls-wrapper")],
                              "controls": ctrls})
            ctrls = []
            counters["mixed-group-wrappers"] += 1
        if subgroups: g["groups"] = subgroups
        elif ctrls: g["controls"] = ctrls
        else:
            counters["empty-groups-dropped"] += 1
            return None      # a Set whose members all live outside the
                             # catalog model; it stays in the props channel
        return g
    groups, top_controls = [], []
    if primary is not None:
        placed.add(primary)
        root_group = build_group(primary) or {}
        groups = root_group.get("groups", [])
        top_controls = root_group.get("controls", [])
    stray = [export_requirement(reqs[i], counters) for i in sorted(reqs) if i not in placed]
    counters["stray-controls"] += len(stray)
    top_controls += stray
    cat = {"uuid": str(uuid.uuid5(uuid.NAMESPACE_URL, primary or bdir)),
           "metadata": {"title": manifest["provenance"].get("source", os.path.basename(bdir)),
                        "last-modified": "2026-07-22T00:00:00Z",
                        "version": str(manifest["provenance"].get("source-version", "1")),
                        "oscal-version": "1.2.2",
                        "props": [prop("exporter", "export_oscal.py v0.1")]},
           "groups": groups}
    if top_controls: cat["controls"] = top_controls
    if not groups: cat.pop("groups")
    # ALL sets ride the props channel in full (overlapping membership)
    cat["metadata"]["props"] += [prop("set", cjson(s)) for i, s in sorted(sets.items())]
    doc = {"catalog": cat}
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False); f.write("\n")
    return doc, manifest, len(reqs), len(sets), skipped

# ---------------- import (generic; no corpus knowledge) ----------------
def pget(props, name, ns=SC, all_=False):
    out = [p["value"] for p in props or [] if p.get("name") == name and p.get("ns") == ns]
    return out if all_ else (out[0] if out else None)

def import_requirement(c):
    props = c.get("props", [])
    o = {"id": pget(props, "canonical-id"), "version": pget(props, "version"),
         "lifecycle": pget(props, "lifecycle")}
    lab = next((p["value"] for p in props if p.get("name") == "label" and "ns" not in p), None)
    if lab: o["label"] = lab
    tj = pget(props, "title-json")
    if tj is not None:
        o["title"] = json.loads(tj)
    elif c.get("title") and c["title"] != c["id"]:
        o["title"] = {pget(props, "title-lang") or "en": c["title"]}
    # params indexed by declaring statement
    by_stmt = collections.defaultdict(list)
    for pm in c.get("params", []) or []:
        sid = pget(pm.get("props"), "statement")
        d = {"name": pm["id"]}
        if pm.get("label") and not pget(pm.get("props"), "synthetic-label"):
            d["label"] = pm["label"]
        extra = json.loads(pget(pm.get("props"), "decl") or "{}")
        if "select" in pm and extra.get("type") == "choice":
            d["type"] = "choice"
            d["choices"] = [{"value": x} for x in pm["select"].get("choice", [])]
            if pm["select"].get("how-many") == "one-or-more": d["cardinality"] = "many"
            extra.pop("type", None)
        d.update(extra)
        by_stmt[sid].append(d)
    stmts = []
    cid = c["id"]
    for pt in c.get("parts", []) or []:
        if pt.get("name") != "statement": continue
        sid = pt["id"][len(cid) + 1:] if pt["id"].startswith(cid + "_") else pt["id"]
        pp = pt.get("props", [])
        s = {"id": sid, "modality": pget(pp, "modality"),
             "obligated-parties": pget(pp, "obligated-party", all_=True)}
        pj = pget(pp, "prose-json")
        if pj is not None:
            s["prose"] = json.loads(pj)
        else:
            lang = pget(pp, "lang") or "en"
            s["prose"] = {lang: INSERT_IN.sub(r"{param:\1}", pt.get("prose", ""))}
        if by_stmt.get(sid): s["parameters"] = by_stmt[sid]
        stmts.append(s)
    o["statements"] = stmts
    rj = pget(props, "relations-json")
    if rj is not None:
        o["relations"] = json.loads(rj)
    else:
        links = c.get("links", [])
        if links: o["relations"] = [{"type": l["rel"], "ref": l["href"]} for l in links]
    for k in ("facets", "annotations", "replaces", "aliases", "canonical-alias"):
        v = pget(props, k)
        if v is not None: o[k] = json.loads(v)
    return {k: v for k, v in o.items() if v is not None}

def import_catalog(doc):
    cat = doc["catalog"]
    out = {}
    for sj in pget(cat["metadata"].get("props"), "set", all_=True) or []:
        s = json.loads(sj); out[s["id"]] = s
    def walk(node):
        for c in node.get("controls", []) or []:
            o = import_requirement(c); out[o["id"]] = o
        for g in node.get("groups", []) or []:
            walk(g)
    walk(cat)
    return out

# ---------------- the suite ----------------
def main():
    results = []
    ce = os.path.join(ROOT, "converted_examples")
    for corpus in sorted(os.listdir(ce)):
        cdir = os.path.join(ce, corpus)
        if not os.path.isdir(cdir): continue
        for d in sorted(os.listdir(cdir)):
            bdir = os.path.join(cdir, d)
            if not (d.endswith("-bundle") and os.path.isdir(bdir)): continue
            manifest = json.load(open(os.path.join(bdir, "content-manifest.json"), encoding="utf-8"))
            kinds = collections.Counter(e["path"].split("/")[1] for e in manifest["objects"])
            if any(k in kinds for k in ("component", "impl", "assessment", "finding", "attestation")):
                results.append((corpus, "SKIPPED (lifecycle bundle - SSP-family export is future scope)",
                                None, None, None, None))
                continue
            counters = collections.Counter()
            out_path = os.path.join(cdir, "oscal-export", f"{corpus.lower()}-catalog.json")
            doc, mf, nreq, nset, skipped = export_bundle(bdir, out_path, counters)
            errs = sorted(OSCAL_V.iter_errors(doc), key=lambda e: len(e.absolute_path))
            schema_ok = not errs
            # round-trip
            re_objs = import_catalog(doc)
            listed = {e["id"]: e["semantic-digest"] for e in mf["objects"]}
            match = mismatch = 0
            bad = []
            for oid, ro in re_objs.items():
                if oid not in listed: continue
                if sdig(ro) == listed[oid]: match += 1
                else:
                    mismatch += 1
                    if len(bad) < 3: bad.append(oid)
            covered = nreq + nset
            results.append((corpus, "ok" if schema_ok and mismatch == 0 else "FAIL",
                            f"{match}/{covered}", dict(skipped),
                            (errs[0].message[:100] + " @ " + "/".join(map(str, errs[0].absolute_path))[:80]) if errs else None,
                            (bad, dict(counters)) if (mismatch or counters) else None))
    print(f"{'corpus':22} {'status':44} round-trip")
    fails = 0
    for corpus, status, rt, skipped, serr, extra in results:
        print(f"{corpus:22} {status:44} {rt or '-'}"
              + (f"  skipped: {skipped}" if skipped else ""))
        if serr: print(f"    schema: {serr}"); fails += 1
        if extra and extra[0]: print(f"    digest mismatches: {extra[0]}"); fails += 1
        if extra and extra[1]: print(f"    channels: {extra[1]}")
        if status.startswith("FAIL"): fails += 1
    print("ALL GREEN" if fails == 0 else f"{fails} FAILURES")
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
