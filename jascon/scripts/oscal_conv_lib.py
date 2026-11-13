#!/usr/bin/env python3
"""Shared machinery for OSCAL-catalog -> Semantic Core converters.
House method: full source path inventory, declared destination map,
UNMAPPED = 0 as the gate signal, computed coverage report, manifest
with both digests. Every converter stays a thin corpus adapter."""
import json, hashlib, os, re, copy, collections, shutil, time

# Package digests are over DELIVERED BYTES (D3.1), so a converter must write
# the same bytes on every OS. Text-mode writes do not: "\n" becomes CRLF on
# Windows and stays LF elsewhere, and the manifests of the 1.0.0 corpus
# digest the Windows spelling. The line ending is therefore explicit; it is
# CRLF because re-spelling it would churn every published package digest for
# zero semantic gain (the identifier rule, applied to bytes). .gitattributes
# marks bundle files `-text`, so git stores and delivers exactly these bytes.
# JSON never carries a raw newline inside a string, so only structural line
# breaks are affected.
BUNDLE_NEWLINE = "\r\n"

def robust_rmtree(path, attempts=5):
    """shutil.rmtree with retries - Windows indexers/AV hold transient handles."""
    for i in range(attempts):
        try:
            shutil.rmtree(path); return
        except (PermissionError, OSError):
            if i == attempts - 1: raise
            time.sleep(0.5 * (i + 1))

def make_T(lang, counter=None):
    """Language-tag payload free text (backlog #12). Never for labels/ids."""
    def T(v, field=None):
        if v is None: return v
        if counter is not None: counter[field or "?"] += 1
        return {lang: v}
    return T

def textify(obj, lang):
    """#12 delivery (D9 rev 2): every kernel human-readable field is `text`
    ({BCP-47: string}). Applied at write time so converters keep authoring
    plain strings; identifiers/labels stay strings by decision. Returns the
    number of fields wrapped."""
    n = 0
    def wrap(container, key):
        nonlocal n
        if isinstance(container.get(key), str):
            container[key] = {lang: container[key]}; n += 1
    wrap(obj, "title")
    wrap(obj, "rationale")                                   # mapping
    wrap(obj, "scenario")                                    # risk (kernel 2.0.0)
    if isinstance(obj.get("acceptance"), dict): wrap(obj["acceptance"], "rationale")
    for ex in obj.get("excludes", []) or []: wrap(ex, "rationale")
    for cap in obj.get("capabilities", []) or []: wrap(cap, "description")
    for a in obj.get("actions", []) or []: wrap(a, "description")
    for dv in obj.get("deviations", []) or []: wrap(dv, "rationale")
    for op in obj.get("operations", []) or []:
        if isinstance(op.get("deviation"), dict): wrap(op["deviation"], "rationale")
    return n

def slug(s):
    s = re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
    if len(s) <= 60:
        return s or "x"
    # P10 #39: never bare-truncate - collided ids silently merge objects
    return s[:52].rstrip("-") + "-" + hashlib.sha256(s.encode()).hexdigest()[:7]

def _canon(o):
    """RFC 8785 member ordering: keys sorted by UTF-16 code units, not code
    points (P9b-3). Identical to sort_keys for ASCII keys - all shipped
    bundles - but correct for astral-plane keys where the two orders differ."""
    if isinstance(o, dict):
        return {k: _canon(o[k]) for k in sorted(o.keys(), key=lambda s: s.encode("utf-16-be"))}
    if isinstance(o, list):
        return [_canon(x) for x in o]
    return o

def semantic_digest(obj):
    o = copy.deepcopy(obj); o.pop("annotations", None)
    c = json.dumps(_canon(o), separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(c).hexdigest()

class Bundle:
    def __init__(self, out_dir, lang="en"):
        self.out = out_dir
        self.lang = lang           # corpus language: #12 textify at write time
        self.objects = {}          # relpath -> obj
        self.schemas = {}          # relpath -> pinned schema obj
    def add(self, relpath, obj):
        self.objects[relpath] = obj
    def stub(self, name, fid, mods, props,
             note="NORMATIVE pinned payload schema (backlog #26): closed shape - unknown keys are rejected, never smuggled"):
        # #26 delivered: pins are the normative payload contract, fail-closed.
        # (method name kept for call-site stability; these are no longer stubs)
        self.schemas[f"schemas/{name}"] = {
            "id": fid, "version": "1.0.0", "modifies-semantics": mods, "note": note,
            "schema": {"$schema": "https://json-schema.org/draft/2020-12/schema",
                       "type": "object", "properties": props,
                       "additionalProperties": False}}
    def pin_stdlib(self, filename):
        """#26: stdlib facets are pinned VERBATIM from the normative
        descriptor - the pin and the descriptor cannot diverge."""
        src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "schemas", "stdlib", filename)
        d = json.load(open(src, encoding="utf-8"))
        self.schemas[f"schemas/{filename}"] = d
    def _w(self, relpath, obj):
        p = os.path.join(self.out, relpath)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8", newline=BUNDLE_NEWLINE) as f:
            json.dump(obj, f, indent=1, ensure_ascii=False); f.write("\n")
    def _sha(self, relpath):
        return "sha256:" + hashlib.sha256(open(os.path.join(self.out, relpath), "rb").read()).hexdigest()
    def write(self, provenance):
        # overwrite in place, delete only stale files (never rmdir - Windows
        # indexers/sync clients hold transient directory handles)
        want = {os.path.normpath(rel) for rel in
                list(self.objects) + list(self.schemas) + ["content-manifest.json"]}
        if os.path.exists(self.out):
            for base, _, files in os.walk(self.out):
                for fn in files:
                    full = os.path.join(base, fn)
                    if os.path.normpath(os.path.relpath(full, self.out)) not in want:
                        for i in range(5):
                            try: os.remove(full); break
                            except OSError:
                                if i == 4: raise
                                time.sleep(0.3 * (i + 1))
            for base, dirs, files in os.walk(self.out, topdown=False):
                if not dirs and not files and base != self.out:
                    try: os.rmdir(base)
                    except OSError: pass
        for o in self.objects.values(): textify(o, self.lang)   # #12 delivery
        for rel, o in {**self.objects, **self.schemas}.items(): self._w(rel, o)
        manifest = {"manifest-version": "1"}
        # backlog #44: content beyond the 1.0.0 kernel names its kernel
        # (KERNEL-1). Bundles without it stay unpinned - byte-identical to
        # their 1.0.0 conversion and readable by a 1.0.0 tool.
        if any(("scenario" in o and "owner-ref" in o) or o.get("risk-refs") for o in self.objects.values()):
            manifest["kernel-version"] = "2.0.0"
        manifest.update({"provenance": provenance,
                    "objects": [{"id": o["id"], "version": o["version"],
                                 "package-digest": self._sha(rel),
                                 "semantic-digest": semantic_digest(o), "path": rel}
                                for rel, o in sorted(self.objects.items())],
                    "facet-schemas": [{"id": s["id"], "exact-version": s["version"],
                                       "digest": self._sha(rel), "path": rel}
                                      for rel, s in sorted(self.schemas.items())]})
        self._w("content-manifest.json", manifest)
        return manifest

def inventory(node, prefix, counter, normalize=lambda p: p):
    if isinstance(node, dict):
        for k, v in node.items(): inventory(v, f"{prefix}.{k}", counter, normalize)
    elif isinstance(node, list):
        for v in node: inventory(v, f"{prefix}[]", counter, normalize)
    else:
        counter[normalize(prefix)] += 1

def _pointer(parts):
    """RFC 6901 JSON Pointer for a path of keys and array indices."""
    return "".join("/" + str(x).replace("~", "~0").replace("/", "~1") for x in parts)

def _token(v):
    """A scalar with its JSON type, so that 1, "1", true and "true" are four
    values (in Python True == 1 and they hash alike)."""
    if v is None: return ("null", None)
    if isinstance(v, bool): return ("boolean", v)
    if isinstance(v, str): return ("string", v)
    return ("number", json.dumps(v))

def global_occurrence(sources, objects):
    """For every scalar leaf of every source document: is there an EQUAL value
    anywhere in the emitted objects? sources: [(tag, document)]; -> JSON-able dict.

    What this measures, and what it does not. Path coverage says where a
    source value is DECLARED to go. This looks at values, but globally: all
    sources and all emitted objects share one search space, and one output
    value satisfies every equal source value. So
      - `exact` is an UPPER bound on what was carried. It cannot show that a
        given occurrence arrived: a description dropped from one control is
        hidden by the same text on another (GitHub issue 33).
      - `absent` is a LOWER bound on what was lost or transformed, never the
        complete work queue.
    Accounting for each source occurrence is the conversion ledger's job
    (`Ledger` below), not this function's.

    Matching is on complete, typed scalars (GitHub issue 32; until 2026-11-13
    this function was `value_arrival` and searched one joined string, so
    "open" arrived in "not-open", 1 in 10, true in "true", "" in anything,
    and a null never):
      exact      an output VALUE of the same JSON type equals it
      key-only   a string that equals an output KEY and no output value. A
                 value can become a key (a facet keyed by name), but without
                 a declared mapping that is a candidate, not an arrival
      embedded   a non-empty string that occurs only INSIDE a longer output
                 string value (a remark appended to a description). A
                 candidate too
      absent     none of these
    Only `exact` counts. Every leaf not `exact` is listed with its indexed
    JSON Pointer, grouped by its path with array positions collapsed."""
    def leaves(n, parts):
        if isinstance(n, dict):
            for k, v in n.items(): yield from leaves(v, parts + [k])
        elif isinstance(n, list):
            for i, v in enumerate(n): yield from leaves(v, parts + [i])
        else: yield parts, n
    values, keys = set(), set()
    def collect(n):
        if isinstance(n, dict):
            for k, v in n.items(): keys.add(k); collect(v)
        elif isinstance(n, list):
            for v in n: collect(v)
        else: values.add(_token(n))
    for o in objects: collect(o)
    out_strings = [v for t, v in values if t == "string"]
    # one haystack for the embedded test; the separator cannot occur in a
    # source string that is tested against it (those fall back to the loop)
    SEP = "\x00"
    hay = SEP.join(out_strings)
    def embedded(sv):
        if not sv: return False            # the empty string is inside every string and proves nothing
        if SEP in sv: return any(sv in t for t in out_strings)
        return sv in hay
    counts = collections.Counter()
    absent = {"identity": collections.Counter(), "document-metadata": collections.Counter(),
              "content": collections.Counter()}
    listed = {"key-only": collections.defaultdict(list), "embedded": collections.defaultdict(list),
              "absent-content": collections.defaultdict(list)}
    total = prose = 0
    for tag, doc in sources:
        for parts, v in leaves(doc, []):
            total += 1
            tok = _token(v)
            path = tag + "".join("[]" if isinstance(x, int) else "." + x for x in parts)
            where = f"{tag}#{_pointer(parts)}"
            if tok in values:
                counts["exact"] += 1; continue
            if tok[0] == "string" and v in keys:
                counts["key-only"] += 1; listed["key-only"][path].append(where); continue
            if tok[0] == "string" and embedded(v):
                counts["embedded"] += 1; listed["embedded"][path].append(where); continue
            if re.search(r"(uuids?(\[\])?|href|\.id|-id)$", path): kind = "identity"
            elif ".metadata." in path or ".back-matter." in path: kind = "document-metadata"
            else:
                kind = "content"
                if isinstance(v, str) and len(v) >= 40: prose += 1
                listed["absent-content"][path].append(where)
            absent[kind][path] += 1
    def rows(d): return [{"path": p, "count": len(w), "pointers": w} for p, w in sorted(d.items())]
    return {"measures": "global occurrence of equal typed values - an upper bound on what was carried, "
                        "not a trace of each source occurrence",
            "leaf-values": total, "exact": counts["exact"],
            "key-only": counts["key-only"], "embedded": counts["embedded"],
            "absent": {k: sum(c.values()) for k, c in absent.items()},
            "absent-content-prose": prose,
            "key-only-paths": rows(listed["key-only"]), "embedded-paths": rows(listed["embedded"]),
            "absent-content-paths": rows(listed["absent-content"])}

# ---------------- the conversion ledger ----------------
# global_occurrence() above cannot say where a value went. The ledger can,
# because the converter's own values tell it: every scalar read from a source
# document carries its origin (document tag + JSON Pointer) for as long as the
# converter hands it on unchanged. After the bundle is written, every output
# leaf and key that still is such a value is a COPY, with a known source and
# a known destination. Whatever the converter computes (an id minted from a
# title, a code looked up in a table, two titles joined) loses its origin by
# itself, because Python returns a plain string from every string operation;
# the converter states those with derive(), which names the rule and keeps
# the function, so the transformation can be applied again and compared.
#
#   led = Ledger()
#   SSP = led.source("ssp", json.load(...))          # same data, origins attached
#   ...build the objects as before...
#   uri = led.derive("party-uri", lambda n: f"{NS}/party/{slug(n)}", party["name"])
#   led.drop(r"\.metadata\.last-modified$", "document bookkeeping, not content")
#   bundle.write(...)
#   result = led.account(bundle.out, bundle.objects)
#
# One entry per source leaf, in document order, with exactly one outcome:
#   copied                 the value stands, typed-equal, at each destination
#                          named (read back from the written file)
#   transformed            a named rule produced the destination from it; the
#                          rule was applied again to the source and compared
#   intentionally-dropped  no destination, and a drop() declaration says why
#   unaccounted            none of these - the work queue
# A value that was deduplicated is linked to what was kept with same(); its
# outcome is then the kept value's, marked `via`.
#
# Invariant the accounting relies on: a tracked value is immutable and is
# never rebuilt on the way (deepcopy returns the same object), so "is this
# output leaf a tracked value" is a question of object identity, never of
# equal text. That is what makes it immune to the two defects of the global
# check: an equal value elsewhere proves nothing here.
#
# Limits. Only strings and integers can carry an origin (bool and None cannot
# be subclassed); such a source leaf is `unaccounted` until a drop() covers
# it. A value used only to DECIDE something (a status compared in an `if`)
# leaves no trace either: state it with derive() on what it decided.

class _Tracked:
    """Mixin of a scalar that knows where it came from.
    _origins: ((tag, parts), ...) the source leaves it stands for
    _rule:    None for a copy, the rule's name for a derived value
    _inputs:  for a derived value, the arguments the rule was called with"""
    __slots__ = ()
    def __deepcopy__(self, memo): return self      # immutable: identity is the trace
    def __copy__(self): return self

class _TStr(_Tracked, str):
    def __new__(cls, value, origins=(), rule=None, fn=None, inputs=()):
        self = str.__new__(cls, value)
        self._origins, self._rule, self._fn, self._inputs = tuple(origins), rule, fn, tuple(inputs)
        return self

class _TInt(_Tracked, int):
    def __new__(cls, value, origins=(), rule=None, fn=None, inputs=()):
        self = int.__new__(cls, value)
        self._origins, self._rule, self._fn, self._inputs = tuple(origins), rule, fn, tuple(inputs)
        return self

def _track(value, origins, rule=None, fn=None, inputs=()):
    if isinstance(value, bool) or value is None: return value      # cannot carry an origin
    if isinstance(value, str): return _TStr(value, origins, rule, fn, inputs)
    if isinstance(value, int): return _TInt(value, origins, rule, fn, inputs)
    return value

def _plain(v):
    """A tracked value as the plain scalar it is (for typed comparison)."""
    if isinstance(v, _TStr): return str.__str__(v)
    if isinstance(v, _TInt): return int(v)
    return v

def _at(doc, parts):
    for x in parts: doc = doc[x]
    return doc

class Ledger:
    def __init__(self):
        self.docs = {}          # tag -> the source document as loaded (never tracked)
        self.leaves = []        # (tag, parts) of every source leaf, in document order
        self._drops = []        # (compiled regex over the collapsed path, reason)
        self._same = []         # (dropped tracked value, kept tracked value, rule)

    def source(self, tag, doc):
        """-> a copy of `doc` whose string and integer leaves carry their origin."""
        assert tag not in self.docs, f"source tag {tag} used twice"
        self.docs[tag] = doc
        def walk(n, parts):
            if isinstance(n, dict): return {k: walk(v, parts + (k,)) for k, v in n.items()}
            if isinstance(n, list): return [walk(v, parts + (i,)) for i, v in enumerate(n)]
            self.leaves.append((tag, parts))
            return _track(n, [(tag, parts)])
        return walk(doc, ())

    def derive(self, rule, fn, *inputs):
        """-> fn(*inputs), carrying the origins of every tracked input. The
        function is kept: account() calls it again on the source's own values."""
        value = fn(*inputs)
        if isinstance(value, bool) or not isinstance(value, (str, int)):
            raise TypeError(f"rule {rule}: a derived value must be a string or an integer to carry its origin, "
                            f"got {type(value).__name__}")
        origins = [o for x in inputs if isinstance(x, _Tracked) for o in x._origins]
        return _track(_plain(value), origins, rule, fn, inputs)

    def drop(self, pattern, reason):
        """Declare that source leaves whose collapsed path matches `pattern`
        are not carried, and why. Applies only where no destination exists."""
        self._drops.append((re.compile(pattern), reason))

    def same(self, dropped, kept, rule):
        """Deduplication: `dropped` and `kept` are two structures the converter
        built from two source occurrences of one thing, and only `kept` goes
        into the bundle. Links every tracked leaf of `dropped` to its
        counterpart in `kept`, so the dropped occurrence is accounted for by
        the retained one - if the two are equal, which account() checks."""
        def walk(a, b, at):
            if isinstance(a, dict) and isinstance(b, dict):
                for k in a:
                    if k in b: walk(a[k], b[k], f"{at}/{k}")
            elif isinstance(a, list) and isinstance(b, list):
                for i, (x, y) in enumerate(zip(a, b)): walk(x, y, f"{at}/{i}")
            elif isinstance(a, _Tracked) and isinstance(b, _Tracked):
                self._same.append((a, b, rule))
        walk(dropped, kept, "")

    @staticmethod
    def collapsed(tag, parts):
        return tag + "".join("[]" if isinstance(x, int) else "." + x for x in parts)

    def account(self, out_dir, objects):
        """objects: {relpath: object} as written under out_dir. Reads every
        file back and checks each claim against it. -> JSON-able dict."""
        # 1. where does every tracked value stand in the written bundle?
        found = collections.defaultdict(list)       # id(tracked value) -> [(value, destination)]
        written = {}
        def walk(n, rel, oid, parts):
            if isinstance(n, dict):
                for k, v in n.items():
                    if isinstance(k, _Tracked):
                        found[id(k)].append((k, {"object": oid, "file": rel, "pointer": _pointer(parts + [k]), "as": "key"}))
                    walk(v, rel, oid, parts + [k])
            elif isinstance(n, list):
                for i, v in enumerate(n): walk(v, rel, oid, parts + [i])
            elif isinstance(n, _Tracked):
                found[id(n)].append((n, {"object": oid, "file": rel, "pointer": _pointer(parts), "as": "value"}))
        for rel, obj in sorted(objects.items()):
            with open(os.path.join(out_dir, rel), encoding="utf-8") as f: written[rel] = json.load(f)
            walk(obj, rel, obj.get("id") or rel, [])       # the manifest has no id: it is named by its path
        # 2. per source leaf: the tracked values that stand for it, directly or through same()
        by_origin = collections.defaultdict(list)   # (tag, parts) -> [(tracked value, destination, via)]
        for hits in found.values():
            for value, dest in hits:
                for origin in value._origins: by_origin[origin].append((value, dest, None))
        for dropped, kept, rule in self._same:
            for value, dest in found.get(id(kept), []):
                for origin in dropped._origins:
                    by_origin[origin].append((dropped if dropped._rule else value, dest, rule))
        # 3. check every claim against the file on disk, and classify
        failures = []
        def on_disk(dest):
            parts = [x.replace("~1", "/").replace("~0", "~") for x in dest["pointer"].split("/")[1:]]
            node = written[dest["file"]]
            for i, x in enumerate(parts):
                if dest["as"] == "key" and i == len(parts) - 1:
                    return x if isinstance(node, dict) and x in node else KeyError
                node = node[int(x)] if isinstance(node, list) else node[x]
            return node
        def holds(value, origin, dest):
            """does the destination hold what this tracked value claims?"""
            there = on_disk(dest)
            if value._rule is None:
                want = _at(self.docs[origin[0]], origin[1])               # a copy: the source's own value
            else:
                want = fresh(value)                                       # a rule: applied to the source again
            return _token(_plain(want)) == _token(there)
        def fresh(x):
            """the value of x recomputed from the source documents alone"""
            if not isinstance(x, _Tracked): return x
            if x._rule is None: return _at(self.docs[x._origins[0][0]], x._origins[0][1])
            return x._fn(*[fresh(i) for i in x._inputs])
        entries, totals = [], collections.Counter()
        unaccounted = collections.defaultdict(list)
        for tag, parts in self.leaves:
            origin, path = (tag, parts), self.collapsed(tag, parts)
            entry = {"source": f"{tag}#{_pointer(parts)}", "path": path}
            dests, outcome = [], None
            for value, dest, via in by_origin.get(origin, []):
                d = {"object": dest["object"], "pointer": dest["pointer"]}
                if dest["as"] == "key": d["as"] = "key"
                if value._rule: d["rule"] = value._rule
                if via: d["via"] = via
                if not holds(value, origin, dest):
                    failures.append({"source": entry["source"], **d}); continue
                dests.append(d)
            if dests:
                outcome = "copied" if any("rule" not in d for d in dests) else "transformed"
                entry["destinations"] = sorted(dests, key=lambda d: (d["object"] or "", d["pointer"]))
            else:
                reason = next((why for rx, why in self._drops if rx.search(path)), None)
                if reason is not None:
                    outcome, entry["reason"] = "intentionally-dropped", reason
                else:
                    outcome = "unaccounted"; unaccounted[path].append(entry["source"])
            entry["outcome"] = outcome; totals[outcome] += 1
            entries.append(entry)
        return {"measures": "one entry per source leaf value: where it went, checked against the written files",
                "leaf-values": len(self.leaves),
                "totals": {k: totals[k] for k in ("copied", "transformed", "intentionally-dropped", "unaccounted")},
                "verification-failures": failures,
                "unaccounted-paths": [{"path": p, "count": len(w), "pointers": w} for p, w in sorted(unaccounted.items())],
                "entries": entries}

def coverage(paths, rules):
    """rules: list of (regex, level, target). Returns (rows, unmapped)."""
    rows, unmapped = [], []
    compiled = [(re.compile(pat), l, t) for pat, l, t in rules]
    for p, n in sorted(paths.items()):
        for rx, l, t in compiled:
            if rx.search(p):
                rows.append((p, n, l, t)); break
        else:
            unmapped.append((p, n))
    return rows, unmapped

def walk_controls(cat):
    """Yield (control, parents, group_chain) for every control at any depth."""
    def wc(c, parents, gchain):
        yield c, parents, gchain
        for s in c.get("controls", []) or []:
            yield from wc(s, parents + [c], gchain)
    def wg(g, gchain):
        for c in g.get("controls", []) or []:
            yield from wc(c, [], gchain + [g])
        for s in g.get("groups", []) or []:
            yield from wg(s, gchain + [g])
    for g in cat.get("groups", []) or []:
        yield from wg(g, [])
    for c in cat.get("controls", []) or []:
        yield from wc(c, [], [])

def report(md_path, json_path, title, source_line, totals_extra, rule_lines,
           finding_lines, rows, unmapped, jextra):
    total = sum(n for _, n, _, _ in rows) + sum(n for _, n in unmapped)
    mapped = sum(n for _, n, _, _ in rows)
    pct = round(100 * mapped / total, 3) if total else 0.0
    j = {"totals": {"leaf-values": total, "mapped": mapped,
                    "unmapped": total - mapped, "coverage-pct": pct},
         "unmapped-paths": [{"path": p, "count": n} for p, n in unmapped],
         "path-map": [{"path": p, "count": n, "level": l, "destination": t}
                      for p, n, l, t in rows], **jextra}
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(j, f, indent=1, ensure_ascii=False)
    md = [f"# {title}\n", source_line + "\n", "## Totals\n",
          f"- Source leaf values inventoried: **{total:,}**",
          f"- Mapped (declared destination): **{mapped:,}**",
          f"- **UNMAPPED: {total - mapped}**  ->  coverage **{pct} %**"]
    md += totals_extra + ["\n## Conversion rules (declared, counted)\n"] + rule_lines
    if finding_lines:
        md += ["\n## Findings (computed)\n"] + finding_lines
    md += ["\n## Full path map (every source path, its count, its destination)\n",
           "| path | count | level | destination |\n|---|---:|---|---|"]
    md += [f"| `{p}` | {n:,} | {l} | {t} |" for p, n, l, t in rows]
    md += ["\n## UNMAPPED (gate target: zero)\n"]
    md += (["| path | count |\n|---|---:|"] + [f"| `{p}` | {n} |" for p, n in unmapped]) if unmapped else ["*(none)*"]
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    return j
