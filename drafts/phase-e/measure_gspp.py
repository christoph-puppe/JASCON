#!/usr/bin/env python3
"""The Grundschutz++ figures the texts quote, counted on one catalogue file.

    python3 drafts/phase-e/measure_gspp.py sources/Grundschutz++-catalog.json

What it measures, with the method of the census of July 2026
(drafts/prop-census-three-authorities-v0.3-input-r2.md):
  - the controls, those nested in a control and those at the top of a group;
  - the props of the controls: their own, those of their parts and of their
    parameters (not those of groups or of the metadata), and how many carry
    a namespace;
  - the shape of every control: the names of its parts, whether a part holds
    a part, whether a part carries a namespace;
  - the statement parts and the grammar props each carries;
  - the list values packed into one string: the values of `tags`, `threats`
    (control props) and `target_object_categories` (props of the statement
    part) that contain a comma;
  - the parameter slots of the sentence template: every `{{Label}}` in a
    `result` or `result_specification` value, and the values that hold one.

The method was checked on the catalogue of 2026-07-16 (commit
39a1193f3d230828ea6614eb20c94a026c9f7df0 of the publisher's repository): it
gives the 781 packed lists (125, 616, 40) the handbook quoted for that
catalogue. The pinned catalogue is the one
converted_examples/DE.BSI/SOURCES.sha256 names;
.github/scripts/fetch-pinned-sources.sh fetches it into sources/, which git
ignores. The file is read and nothing is written. Standard library only."""
import collections, json, re, sys

if len(sys.argv) != 2:
    raise SystemExit("usage: measure_gspp.py <catalogue.json>")
with open(sys.argv[1], encoding="utf-8") as f: cat = json.load(f)["catalog"]
md = cat["metadata"]

def controls(node, depth=0):
    """every control of a catalogue, a group or a control, with its depth among controls"""
    for g in node.get("groups", []) or []: yield from controls(g, depth)
    for c in node.get("controls", []) or []:
        yield c, depth
        yield from controls(c, depth + 1)

def props_below(node, skip=("controls",)):
    """the props of one part or parameter, and of what it holds"""
    if isinstance(node, dict):
        for k, v in node.items():
            if k in skip: continue
            if k == "props" and isinstance(v, list): yield from v
            else: yield from props_below(v, skip)
    elif isinstance(node, list):
        for v in node: yield from props_below(v, skip)

cs = list(controls(cat))
print(f"version {md.get('version')!r}, last-modified {md.get('last-modified')!r}, oscal-version {md.get('oscal-version')!r}")
print(f"controls {len(cs):,}; nested in a control {sum(1 for _, d in cs if d):,}; at the top of a group {sum(1 for _, d in cs if not d):,}")

by_level = collections.Counter(); ns_by_level = collections.Counter(); names = collections.Counter()
for c, _ in cs:
    for where, ps in (("control", c.get("props", []) or []),
                      ("part", [p for part in c.get("parts", []) or [] for p in props_below(part)]),
                      ("param", [p for prm in c.get("params", []) or [] for p in props_below(prm)])):
        for p in ps:
            by_level[where] += 1; names[p["name"]] += 1
            if p.get("ns"): ns_by_level[where] += 1
print(f"props of controls: {sum(by_level.values()):,} {dict(by_level)}; with a namespace: {sum(ns_by_level.values()):,} {dict(ns_by_level)}")
print(f"prop names on controls: {len(names)}: {dict(names.most_common())}")

shape = collections.Counter()
for c, _ in cs:
    ps = c.get("parts", []) or []
    shape[(tuple(p.get("name") for p in ps), any(p.get("parts") for p in ps), any(p.get("ns") for p in ps))] += 1
print("controls by their parts (names in order, a part in a part, a part with a namespace):", dict(shape))

stm = [p for c, _ in cs for p in c.get("parts", []) or [] if p.get("name") == "statement"]
have = collections.Counter()
for p in stm:
    for n in {pp["name"] for pp in p.get("props", []) or []}: have[n] += 1
print(f"statement parts {len(stm):,}; with each prop: {dict(have)}")
verbs = collections.Counter(pp["value"] for p in stm for pp in p.get("props", []) or [] if pp["name"] == "modal_verb")
print(f"modal_verb values: {dict(verbs.most_common())}")

total = 0
control_props = [pp for c, _ in cs for pp in c.get("props", []) or []]
statement_props = [pp for p in stm for pp in p.get("props", []) or []]
for name, where in (("tags", control_props), ("threats", control_props), ("target_object_categories", statement_props)):
    values = [pp["value"] for pp in where if pp["name"] == name]
    packed = [v for v in values if "," in v]
    total += len(packed)
    print(f"`{name}`: {len(values):,} values, {len(packed):,} with a comma")
print(f"values with a comma in the three: {total:,}")

template = [pp["value"] for pp in statement_props if pp["name"] in ("result", "result_specification")]
slots = [s for v in template for s in re.findall(r"\{\{(?!\s*insert:)(.*?)\}\}", v)]
print(f"`result` / `result_specification` values with a `{{{{Label}}}}` slot: {sum(1 for v in template if '{{' in v):,}; slots: {len(slots):,}")
print(f"parameters of controls: {sum(len(c.get('params', []) or []) for c, _ in cs):,}")
for c, _ in cs:
    if c["id"] == "ASST.3.11":
        print("ASST.3.11:", [(pp["name"], pp["value"]) for pp in c.get("props", []) if pp["name"] in ("tags", "threats")])
