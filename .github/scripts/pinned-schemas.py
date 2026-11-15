#!/usr/bin/env python3
"""One id and version is one schema (backlog #88).

    python3 .github/scripts/pinned-schemas.py [--write] [<bundle folder> ...]

Run from the repository root. Reads every facet schema a converted bundle
under converted_examples/ pins, every descriptor of the standard library
(jascon/schemas/stdlib), the schemas the manifest of the example folder and
of each example pack pins (jascon/examples, jascon/example-packs/*; since
2026-11-14, backlog #94: until then the example folder pinned
gspp-taxonomy 1.0.0 with another schema than the Grundschutz++ bundle and
this check did not look there), and the pins of any bundle folder named as
an argument (the CR26 bundle, which is converted in the workflow and not
committed). Each is held to the record .github/pinned-schemas.json: for
every id and version, the digest of what the schema says (its `schema` and
its `modifies-semantics`, in canonical form).

It fails when
- two files give one id and version two schemas;
- a file's id and version stand in the record with another digest: the
  schema changed and kept its version;
- a file's id and version are not in the record: a new schema, or a new
  version, that nobody entered.

`--write` enters what is new. It never changes a line that is there: a
schema that changes needs a new version, and then a new line. A line whose
schema no bundle pins any more stays; the version was published.

The author decided it for the compat facet on 2026-11-14 ("one id and
version is one schema"); the converters' own facets had done the same thing
in small (four schemas of the IFA converter and one of the CR26 converter
gained members under the version they had). Standard library only."""
import glob, hashlib, json, os, sys

RECORD = os.path.join(".github", "pinned-schemas.json")

def canon(o):
    if isinstance(o, dict): return {k: canon(o[k]) for k in sorted(o)}
    if isinstance(o, list): return [canon(x) for x in o]
    return o

def says(descriptor):
    body = {"schema": descriptor.get("schema"), "modifies-semantics": descriptor.get("modifies-semantics")}
    return "sha256:" + hashlib.sha256(json.dumps(canon(body), separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()

def main(argv):
    write = "--write" in argv
    extra = [a for a in argv if a != "--write"]
    files = sorted(glob.glob(os.path.join("converted_examples", "*", "*-bundle", "schemas", "*.json"))
                   + glob.glob(os.path.join("jascon", "schemas", "stdlib", "*.json")))
    # a folder whose manifest names its pins by path: the example folder and the example packs
    for folder in [os.path.join("jascon", "examples")] + sorted(glob.glob(os.path.join("jascon", "example-packs", "*"))):
        mp = os.path.join(folder, "content-manifest.json")
        if not os.path.exists(mp): continue
        with open(mp, encoding="utf-8") as fh: pins = json.load(fh).get("facet-schemas", []) or []
        files += sorted(os.path.join(folder, e["path"]) for e in pins)
    for folder in extra:
        found = sorted(glob.glob(os.path.join(folder, "schemas", "*.json")))
        if not found: print(f"{folder}: no pinned schema found under schemas/"); return 1
        files += found
    seen, problems = {}, []          # "<id> <version>" -> (digest, first file)
    for f in files:
        with open(f, encoding="utf-8") as fh: d = json.load(fh)
        if not isinstance(d, dict) or "id" not in d or "version" not in d:
            problems.append(f"{f}: no id and version"); continue
        key, digest = f"{d['id']} {d['version']}", says(d)
        if key in seen and seen[key][0] != digest:
            problems.append(f"{key}: two schemas under one id and version: {seen[key][1]} and {f}")
        seen.setdefault(key, (digest, f))
    record = {}
    if os.path.exists(RECORD):
        with open(RECORD, encoding="utf-8") as fh: record = json.load(fh)["schemas"]
    new = []
    for key, (digest, f) in sorted(seen.items()):
        if key not in record: new.append((key, digest, f))
        elif record[key] != digest:
            problems.append(f"{key}: the schema changed and kept its version ({f}); a schema that changes gets a new version")
    if write and not problems:
        for key, digest, _ in new: record[key] = digest
        with open(RECORD, "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"about": "One id and version is one schema (backlog #88). Written by .github/scripts/pinned-schemas.py "
                                "--write, which adds lines and never changes one; held by the Validators workflow.",
                       "schemas": dict(sorted(record.items()))}, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
        print(f"pinned-schemas: {len(new)} line(s) entered, {len(record)} in the record")
        return 0
    for key, _, f in new: problems.append(f"{key}: not in {RECORD} ({f}); enter it with --write and commit the record")
    for p in problems: print("pinned-schemas: " + p)
    if not problems: print(f"pinned-schemas: {len(files)} file(s), {len(seen)} id and version pair(s), each one schema, each as recorded")
    return 1 if problems else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
