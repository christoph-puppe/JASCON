#!/usr/bin/env python3
"""risk_catalog.py - PROTOTYPE: ready-made risk lists for JASCON.

A risk catalogue is a published list of risk scenarios. An entry carries
what a publisher can know (title, scenario, the requirements that typically
treat it) and nothing only an organisation can supply (owner, state, rating,
acceptance). IMPORT copies entries into kernel Risk objects:

  - the Risk gets the organisation's own id, `state: identified`,
    `lifecycle: draft` and the owner given on the command line;
  - suggested treatments are kept only where the bundle selects the
    requirement - through the named Tailoring, or, in a bundle without any
    Tailoring, because every requirement is in play;
  - the Risk points back at the entry through `relations` and records the
    catalogue version in `annotations`.

Import is a copy. Nothing references an entry at run time, so a new
catalogue version cannot change a risk the organisation already owns.

Not importing an entry is a decision too. The organisation records it in a
file beside its bundle (`schema/not-applicable.draft.schema.json`): the
entry, why it does not apply, who decided and when. `completeness` reads
that record to tell a decision from a gap, and names every row that says
no author.

Commands:
  validate     <catalog-dir> [--bundle DIR]
  import       <catalog-dir> --bundle DIR --org PREFIX --owner URI --out DIR
               [--tailoring ID] [--not-applicable FILE]
  completeness <catalog-dir> --risks DIR [--not-applicable FILE]

Needs: Python 3.8+, jsonschema. Outside the kernel on purpose: the entry
shape is `schema/risk-catalog.draft.schema.json` and the record of entries
that do not apply is `schema/not-applicable.draft.schema.json`, both drafts.
"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(HERE, "..", "schema", "risk-catalog.draft.schema.json")
NA_SCHEMA_PATH = os.path.join(HERE, "..", "schema", "not-applicable.draft.schema.json")
INSTANTIATES = "https://github.com/christoph-puppe/JASCON/risk-catalogs/relation/instantiates"


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_catalog(cdir):
    """-> (catalogue, [entries in catalogue order]). Fails loudly on a member
    without a file or a file that is not a member."""
    cat = load_json(os.path.join(cdir, "catalog.json"))
    by_id = {}
    edir = os.path.join(cdir, "entries")
    for fn in sorted(os.listdir(edir)):
        if fn.endswith(".json"):
            e = load_json(os.path.join(edir, fn))
            by_id[e["id"]] = e
    members = [m["ref"] for m in sorted(cat["members"], key=lambda m: m["sequence"])]
    missing = [m for m in members if m not in by_id]
    extra = sorted(set(by_id) - set(members))
    if missing or extra:
        sys.exit(f"catalogue and entries disagree: members without a file {missing}, files that are no member {extra}")
    return cat, [by_id[m] for m in members]


def schema_errors(cat, entries):
    import jsonschema
    schema = load_json(SCHEMA_PATH)
    errs = []
    for name, obj in [("catalog", cat)] + [("entry", e) for e in entries]:
        v = jsonschema.Draft202012Validator({"$ref": f"#/$defs/{name}", "$defs": schema["$defs"]})
        for e in v.iter_errors(obj):
            errs.append(f"{obj.get('id', '?')}: {e.message[:140]}")
    seqs = [m["sequence"] for m in cat["members"]]
    if len(seqs) != len(set(seqs)):
        errs.append(f"{cat['id']}: member sequence numbers are not unique")
    for e in entries:
        if set(e["title"]) != set(e["scenario"]):
            errs.append(f"{e['id']}: title and scenario are not in the same languages")
    return errs


def load_bundle(bdir):
    """-> {id: object} for everything the content manifest lists."""
    manifest = load_json(os.path.join(bdir, "content-manifest.json"))
    objs = {}
    for entry in manifest["objects"]:
        o = load_json(os.path.join(bdir, entry["path"]))
        objs[o["id"]] = o
    return objs


def kind(o):
    if "statements" in o: return "requirement"
    if "selects" in o: return "tailoring"
    if "scenario" in o and "owner-ref" in o: return "risk"
    if "members" in o and "kind" not in o: return "set"
    return "other"


def expand(refs, objs):
    """ids -> requirement ids, through nested Sets to any depth."""
    out, seen, stack = set(), set(), list(refs)
    while stack:
        i = stack.pop()
        if i in seen: continue
        seen.add(i)
        o = objs.get(i)
        if o is None: continue
        if kind(o) == "set": stack.extend(m["ref"] for m in o["members"])
        elif kind(o) == "requirement": out.add(i)
    return out


def selection(objs, tailoring_id):
    """-> (selected requirement ids, tailoring id or None, how).
    No Tailoring in the bundle: every requirement in force is in play."""
    tailorings = sorted(i for i, o in objs.items() if kind(o) == "tailoring" and o.get("lifecycle") != "withdrawn")
    if tailoring_id is None:
        if not tailorings:
            sel = {i for i, o in objs.items() if kind(o) == "requirement" and o.get("lifecycle") != "withdrawn"}
            return sel, None, "no Tailoring in the bundle: every requirement is in play"
        if len(tailorings) > 1:
            sys.exit(f"the bundle holds {len(tailorings)} Tailorings - name one with --tailoring: {tailorings}")
        tailoring_id = tailorings[0]
    t = objs.get(tailoring_id)
    if t is None or kind(t) != "tailoring":
        sys.exit(f"--tailoring {tailoring_id} is not a Tailoring of this bundle")
    if any("set-ref" not in s for s in t["selects"]):
        sys.exit(f"{tailoring_id} carries a predicate select; this prototype resolves set-refs only")
    sel = expand([s["set-ref"] for s in t["selects"]], objs)
    sel -= expand([e["ref"] for e in t.get("excludes", [])], objs)
    sel = {i for i in sel if objs[i].get("lifecycle") != "withdrawn"}
    return sel, tailoring_id, f"selected by {tailoring_id}"


def load_not_applicable(path):
    """-> {entry id: row} - the organisation's recorded decisions NOT to
    import an entry. Without the record, 'not imported' is just a gap.
    The file is held to its schema and an entry may be decided once."""
    if not path: return {}
    import jsonschema
    doc = load_json(path)
    if not isinstance(doc, dict) or "record-version" not in doc:
        sys.exit("--not-applicable: this is not the record of schema/not-applicable.draft.schema.json. "
                 "A file written before 2026-11-13 is a map from an entry to a sentence; the record now "
                 "names the entry, the rationale, who decided and when. Rewrite the file in that shape; "
                 "the app reads the old map and writes the record when an entry is next recorded there.")
    err = next(jsonschema.Draft202012Validator(load_json(NA_SCHEMA_PATH)).iter_errors(doc), None)
    if err:
        sys.exit(f"--not-applicable: {err.message[:140]} @ {'/'.join(map(str, err.absolute_path)) or '(root)'}")
    rows = {}
    for row in doc["entries"]:
        if row["entry"] in rows: sys.exit(f"--not-applicable: {row['entry']} is decided twice")
        rows[row["entry"]] = row
    return rows


def one_language(text):
    """A text in English, else in the first language it has."""
    return text.get("en") or next(iter(text.values()))


def cmd_validate(a):
    cat, entries = load_catalog(a.catalog)
    errs = schema_errors(cat, entries)
    if a.bundle:
        objs = load_bundle(a.bundle)
        for e in entries:
            for st in e.get("suggested-treatments", []):
                tgt = objs.get(st["requirement-ref"])
                if tgt is None or kind(tgt) != "requirement":
                    errs.append(f"{e['id']}: suggested {st['requirement-ref']} is not a Requirement of the bundle")
                elif tgt.get("lifecycle") == "withdrawn":
                    errs.append(f"{e['id']}: suggested {st['requirement-ref']} is withdrawn")
                else:
                    sids = {s["id"] for s in tgt["statements"]}
                    errs += [f"{e['id']}: statement '{s}' names no statement of {st['requirement-ref']}"
                             for s in st.get("statement-ids", []) if s not in sids]
    for e in errs: print("FAIL", e)
    print(f"{cat['id']} {cat['version']}: {len(entries)} entries, {len(errs)} failure(s)")
    return 1 if errs else 0


def cmd_import(a):
    cat, entries = load_catalog(a.catalog)
    errs = schema_errors(cat, entries)
    if errs: sys.exit("catalogue does not validate - run `validate` first: " + errs[0])
    objs = load_bundle(a.bundle)
    selected, tid, how = selection(objs, a.tailoring)
    na = load_not_applicable(a.not_applicable)
    os.makedirs(a.out, exist_ok=True)
    report = {"catalog": cat["id"], "catalog-version": cat["version"],
              "selection": how, "selected-requirements": len(selected),
              "imported": [], "not-applicable": [], "suggestions-out-of-scope": {}, "without-treatment": []}
    suggested_in_scope = set()
    for e in entries:
        label = e.get("label") or e["id"].rsplit("/", 1)[-1]
        if e["id"] in na:
            report["not-applicable"].append(na[e["id"]])      # the row as it was recorded
            continue
        keep, dropped = [], []
        for st in e.get("suggested-treatments", []):
            (keep if st["requirement-ref"] in selected else dropped).append(st)
        suggested_in_scope |= {st["requirement-ref"] for st in keep}
        risk = {"id": f"{a.org.rstrip('/')}/risk/{label}", "version": "1", "lifecycle": "draft", "label": label,
                "title": e["title"], "scenario": e["scenario"], "owner-ref": a.owner, "state": "identified"}
        if tid: risk["tailoring-refs"] = [tid]
        if keep: risk["treatments"] = keep
        else: report["without-treatment"].append(risk["id"])
        risk["relations"] = [{"type": INSTANTIATES, "ref": e["id"]}]
        risk["annotations"] = {"imported-from": {"entry": e["id"], "entry-version": e["version"],
                                                  "catalog": cat["id"], "catalog-version": cat["version"]}}
        if dropped:
            report["suggestions-out-of-scope"][risk["id"]] = [st["requirement-ref"] for st in dropped]
        with open(os.path.join(a.out, f"{label}.json"), "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(risk, indent=1, ensure_ascii=False) + "\n")
        report["imported"].append(risk["id"])
    report["selected-requirements-no-entry-suggests"] = len(selected - suggested_in_scope)
    with open(os.path.join(a.out, "import-report.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(report, indent=1, ensure_ascii=False) + "\n")
    n_drop = sum(len(v) for v in report["suggestions-out-of-scope"].values())
    print(f"catalogue   {cat['id']} {cat['version']} ({len(entries)} entries)")
    print(f"selection   {how} ({len(selected)} requirements)")
    print(f"imported    {len(report['imported'])} Risk objects -> {a.out}  (state identified, lifecycle draft)")
    print(f"skipped     {len(report['not-applicable'])} recorded as not applicable")
    print(f"dropped     {n_drop} suggested treatment(s) the bundle does not select, on {len(report['suggestions-out-of-scope'])} risk(s)")
    print(f"bare        {len(report['without-treatment'])} imported risk(s) left without any treatment")
    print(f"untouched   {report['selected-requirements-no-entry-suggests']} selected requirement(s) no imported entry suggests")
    return 0


def cmd_completeness(a):
    cat, entries = load_catalog(a.catalog)
    na = load_not_applicable(a.not_applicable)
    instantiated = {}
    for base, _, files in os.walk(a.risks):
        for fn in files:
            if not fn.endswith(".json"): continue
            try: o = load_json(os.path.join(base, fn))
            except ValueError: continue
            if not isinstance(o, dict) or kind(o) != "risk" or o.get("lifecycle") == "withdrawn": continue
            for rel in o.get("relations", []):
                if rel.get("type") == INSTANTIATES:
                    instantiated.setdefault(rel["ref"], []).append(o["id"])
    gaps, unsigned = 0, []
    for e in entries:
        label = e.get("label") or e["id"].rsplit("/", 1)[-1]
        if e["id"] in instantiated: continue
        row = na.get(e["id"])
        if row:
            who = row.get("provenance")
            if not who: unsigned.append(label)
            signed = f"{who['author-ref']}, {who['date']}" if who else "no author recorded"
            print(f"n/a   {label}: {one_language(row['rationale'])} [{signed}]")
        else:
            gaps += 1
            print(f"GAP   {label}: {one_language(e['title'])}")
    # a row for an entry this catalogue does not hold belongs to another
    # catalogue, or its id is misspelled; then the entry it meant is a GAP above
    elsewhere = sorted(set(na) - {e["id"] for e in entries})
    if elsewhere: print(f"note  {len(elsewhere)} recorded row(s) name no entry of this catalogue: {elsewhere}")
    if unsigned: print(f"note  {len(unsigned)} decision(s) name no author: {unsigned}")
    print(f"{cat['id']} {cat['version']}: {len(entries)} entries, {len(instantiated)} instantiated, "
          f"{len(entries) - len(instantiated) - gaps} not applicable, {gaps} gap(s)")
    return 1 if gaps else 0


def main():
    p = argparse.ArgumentParser(description="Ready-made risk lists for JASCON (prototype).")
    sub = p.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate"); v.add_argument("catalog"); v.add_argument("--bundle")
    i = sub.add_parser("import"); i.add_argument("catalog")
    i.add_argument("--bundle", required=True); i.add_argument("--org", required=True)
    i.add_argument("--owner", required=True); i.add_argument("--out", required=True)
    i.add_argument("--tailoring"); i.add_argument("--not-applicable")
    c = sub.add_parser("completeness"); c.add_argument("catalog")
    c.add_argument("--risks", required=True); c.add_argument("--not-applicable")
    a = p.parse_args()
    sys.exit({"validate": cmd_validate, "import": cmd_import, "completeness": cmd_completeness}[a.cmd](a))


if __name__ == "__main__":
    main()
