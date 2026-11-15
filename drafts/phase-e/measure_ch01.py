#!/usr/bin/env python3
"""The figures of handbook chapter 1 that come from the three corpora, and
those the other texts quote with them, counted on the pinned sources.

    python3 drafts/phase-e/measure_ch01.py            # from the repository root
    python3 drafts/phase-e/measure_ch01.py <root>     # a tree that holds sources/

It reads three files under sources/, which git ignores:
  sources/ism.json                              converted_examples/AU.ISM/SOURCES.sha256
  sources/Grundschutz++-catalog.json            converted_examples/DE.BSI/SOURCES.sha256
  sources/cr_fedramp-consolidated-rules.json    converted_examples/FedRAMP-CR26/SOURCES.sha256
Each list says where its file comes from; .github/scripts/fetch-pinned-sources.sh
fetches the first two, the Validators workflow shows the third.

What it measures:
  - ISM and Grundschutz++: version and OSCAL version, controls and nested
    controls, the props of the whole catalogue and those with a namespace,
    the prop names. The census of July 2026 counted the props of CONTROLS
    (their own; for Grundschutz++ also those of their parts and parameters):
    measure_gspp.py beside this script counts that way, and for the ISM the
    line "props of controls" below does.
  - ISM: the `applicability` props and their share of the props of controls.
  - Grundschutz++: the shape of the controls' parts, the packed lists, the
    template slots (measure_gspp.py has these in full).
  - CR26: rules, KSIs, terms, overlay entries; members named `props`; the
    `force` words at rule level and in class variants; the units of
    timeframes; `alts` and `updated`; the aliases of the glossary and the
    references of rules and KSIs to its terms; the effective dates.

BSI's second catalogue (MS-TLS) is not pinned and is not measured here.
Nothing is written. Standard library only."""
import collections, json, os, re, sys

root = sys.argv[1] if len(sys.argv) > 1 else os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
def load(*p):
    path = os.path.join(root, "sources", *p)
    if not os.path.isfile(path): raise SystemExit(f"missing {path}: the source is fetched, not committed (see the head of this script)")
    with open(path, encoding="utf-8") as f: return json.load(f)

def controls(node, depth=0):
    """every control of a catalogue, a group or a control, with its depth among controls"""
    for g in node.get("groups", []) or []: yield from controls(g, depth)
    for c in node.get("controls", []) or []:
        yield c, depth
        yield from controls(c, depth + 1)

def all_props(node):
    """every prop anywhere in a document: an entry of a `props` list"""
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "props" and isinstance(v, list):
                for p in v:
                    if isinstance(p, dict): yield p
            yield from all_props(v)
    elif isinstance(node, list):
        for v in node: yield from all_props(v)

def oscal(name, doc):
    cat = doc["catalog"]; md = cat["metadata"]
    cs = list(controls(cat))
    props = list(all_props(cat))
    ns = [p for p in props if p.get("ns")]
    own = [p for c, _ in cs for p in c.get("props", []) or []]
    print(f"== {name}: title {md.get('title')!r}, version {md.get('version')!r}, last-modified {md.get('last-modified')!r}, "
          f"oscal-version {md.get('oscal-version')!r}")
    print(f"   controls: {len(cs):,}; nested in a control: {sum(1 for _, d in cs if d):,}; at the top of a group: {sum(1 for _, d in cs if not d):,}")
    print(f"   props anywhere in the catalogue: {len(props):,}; with a namespace: {len(ns):,}")
    print(f"   props of controls (their own): {len(own):,}; with a namespace: {sum(1 for p in own if p.get('ns')):,}; "
          f"names: {dict(collections.Counter(p['name'] for p in own).most_common())}")
    return cat, cs, own

# ---------------- ISM ----------------
cat, cs, own = oscal("ISM", load("ism.json"))
names = collections.Counter(p["name"] for p in own)
print(f"   prop names on controls: {len(names)}; applicability: {names['applicability']:,} = {100 * names['applicability'] / len(own):.1f} % "
      f"of the props of controls; essential-eight-applicability: {names['essential-eight-applicability']:,}")
print(f"   controls by the names of their parts: {dict(collections.Counter(tuple(p.get('name') for p in c.get('parts', []) or []) for c, _ in cs))}")

# ---------------- Grundschutz++ ----------------
cat, cs, own = oscal("Grundschutz++", load("Grundschutz++-catalog.json"))
shape = collections.Counter()
for c, _ in cs:
    ps = c.get("parts", []) or []
    shape[(tuple(sorted(p.get("name") for p in ps)), any(p.get("parts") for p in ps), any(p.get("ns") for p in ps))] += 1
print(f"   controls by their parts (names, a part in a part, a part with a namespace): {dict(shape)}")
stm = [p for c, _ in cs for p in c.get("parts", []) or [] if p.get("name") == "statement"]
stm_props = [pp for p in stm for pp in p.get("props", []) or []]
print(f"   statement parts: {len(stm):,}; with a modal verb and an action word: "
      f"{sum(1 for p in stm if {'modal_verb', 'action_word'} <= {pp.get('name') for pp in p.get('props', []) or []}):,}")
total = 0
for name, where in (("tags", own), ("threats", own), ("target_object_categories", stm_props)):
    values = [pp["value"] for pp in where if pp.get("name") == name]
    packed = [v for v in values if "," in v]
    total += len(packed)
    print(f"   `{name}`: {len(values):,} values, {len(packed):,} with a comma; e.g. {packed[:2]}")
print(f"   values with a comma in the three: {total:,}")
slots = [s for pp in stm_props if pp.get("name") in ("result", "result_specification")
         for s in re.findall(r"\{\{(?!\s*insert:)(.*?)\}\}", pp.get("value", ""))]
print(f"   template slots `{{{{Label}}}}` in result / result_specification: {len(slots):,}")

# ---------------- CR26 ----------------
d = load("cr_fedramp-consolidated-rules.json")
print(f"== CR26: {d['info']['title']!r}, version {d['info']['version']!r}, last_updated {d['info']['last_updated']!r}")
rules = [r for fam in d["FRR"].values() for trk in fam["data"].values() for sub in trk.values() for r in sub.values()]
ksi = [i for th in d["KSI"].values() for i in th["indicators"].values()]
terms = d["FRD"]["data"]["all"]
print(f"   rules: {len(rules):,}; KSIs: {len(ksi):,}; terms: {len(terms):,}; CTL overlay entries: {sum(len(v) for v in d['CTL'].values()):,}; "
      f"families: {len(d['FRR'])}; KSI themes: {len(d['KSI'])}")
def count_key(n, key):
    if isinstance(n, dict): return (key in n) + sum(count_key(v, key) for v in n.values())
    if isinstance(n, list): return sum(count_key(v, key) for v in n)
    return 0
print(f"   members named `props` anywhere: {count_key(d, 'props')}")
force = collections.Counter(r["force"] for r in rules if "force" in r)
vforce = collections.Counter(v["force"] for r in rules for v in (r.get("varies_by_class") or {}).values() if "force" in v)
both = force + vforce
print(f"   force at rule level: {dict(force)} = {sum(force.values())}; in class variants of rules: {dict(vforce)} = {sum(vforce.values())}")
print(f"   force, rule level and class variants together: {dict(both)} = {sum(both.values())}; "
      f"prohibitions (MUST NOT, SHOULD NOT): {100 * (both['MUST NOT'] + both['SHOULD NOT']) / sum(both.values()):.1f} %")
units = collections.Counter()
def walk_units(n):
    if isinstance(n, dict):
        if "timeframe_type" in n: units[n["timeframe_type"]] += 1
        for v in n.values(): walk_units(v)
    elif isinstance(n, list):
        for v in n: walk_units(v)
walk_units(d)
print(f"   timeframe_type values: {dict(units)}")
print(f"   rules with varies_by_class: {sum(1 for r in rules if r.get('varies_by_class'))}; "
      f"terms with `alts`: {sum(1 for t in terms.values() if 'alts' in t)} of {len(terms)} (not empty: {sum(1 for t in terms.values() if t.get('alts'))}); "
      f"with `updated`: rules {sum(1 for r in rules if r.get('updated'))} of {len(rules)}, KSIs {sum(1 for r in ksi if r.get('updated'))} of {len(ksi)}, "
      f"terms {sum(1 for t in terms.values() if t.get('updated'))} of {len(terms)}")
aliases = sum(len(t.get("alts") or []) for t in terms.values())
refs = [x for r in rules + ksi for x in r.get("terms", []) or []]
known = {t["term"].lower() for t in terms.values()} | {a.lower() for t in terms.values() for a in t.get("alts") or []}
print(f"   glossary: {len(terms)} terms, {aliases} alias entries (`alts`); references of rules and KSIs to terms (`terms[]`): {len(refs):,} "
      f"({sum(len(r.get('terms', []) or []) for r in rules):,} of rules, {sum(len(r.get('terms', []) or []) for r in ksi):,} of KSIs); "
      f"naming a term or an alias of the glossary: {sum(1 for x in refs if x.lower() in known):,}")
obtain = collections.Counter()
def walk_obtain(n):
    if isinstance(n, dict):
        for k, v in n.items():
            if k == "obtain" and isinstance(v, str): obtain[v] += 1
            walk_obtain(v)
    elif isinstance(n, list):
        for v in n: walk_obtain(v)
walk_obtain(d)
print(f"   effective `obtain` dates: {dict(obtain.most_common(5))}")
