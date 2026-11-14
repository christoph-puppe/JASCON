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

def known_arguments(argv, takes_value):
    """Holds a converter's command line to the arguments it knows. Every
    token must be one of `takes_value`, followed by its value; anything else
    stops the run. Without this a misspelled `--obligated-party` is an
    argument nobody reads: the run writes the default and says nothing. What
    a value must be is checked by the function that reads it."""
    i = 0
    while i < len(argv):
        a = argv[i]
        if a not in takes_value:
            raise SystemExit(f"unknown argument {a!r}; this converter takes " + ", ".join(sorted(takes_value)))
        if i + 1 >= len(argv) or argv[i + 1] in takes_value:
            raise SystemExit(f"{a} needs a value")
        i += 2

def out_dir(argv, default):
    """Where a converter writes its bundle and its two coverage reports:
    `--out DIR` among its arguments -> the absolute DIR, else `default`, the
    corpus folder in the repository. A run that is not meant to change the
    committed conversion - one with `--obligated-party`, or one on a source
    whose bundle is not redistributed - belongs in a DIR of its own. The
    argument given twice, or without a value, stops the run."""
    given = [i for i, a in enumerate(argv) if a == "--out"]
    if not given: return default
    if len(given) > 1: raise SystemExit("--out is given more than once")
    if given[0] + 1 >= len(argv) or not argv[given[0] + 1]: raise SystemExit("--out needs a directory")
    return os.path.abspath(argv[given[0] + 1])

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

# The compat facet: what a source holds and neither the kernel nor a standard
# facet has a member for. Until 2026-11-14 five converters each pinned
# `https://ns.jascon.net/compat/oscal-1x` 1.0.0 with a schema of their own;
# one id and version is one schema (author, 2026-11-14), so it is written
# here once, as 1.1.0, with every member any of them uses. The order of the
# members is part of the pinned file.
COMPAT_ID = "https://ns.jascon.net/compat/oscal-1x"
COMPAT = COMPAT_ID + "@1"
COMPAT_VERSION = "1.1.0"
COMPAT_FILE = "oscal-1x-compat-1.1.0.json"
COMPAT_NOTE = ("NORMATIVE pinned payload schema (backlog #26), one for every converter of this repository since "
               "2026-11-14: closed shape - unknown keys are rejected, never smuggled")
COMPAT_PROPERTIES = {
    "metadata": {"type": "object"},        # the source document's metadata, in the source's shape
    "uuid": {"type": "string"},            # the uuid the source gives the element this object is made from
    "back-matter": {"type": "object"},     # resources something in the document refers to, in the source's shape
    "catalog": {"type": "object"},
    "imports": {"type": "array"},          # a profile's imports, as the source writes them
    "merge": {"type": "object"},           # a profile's merge directive
    "class": {"type": "string"},
    "group-parts": {"type": "array"},
    "param-extras": {"type": "object"},
    "props": {"type": "array"},
    "parts": {"type": "array"},
    "links": {"type": "array"},
    "control": {"type": "object"},
    "group": {"type": "object"},
    "nested-in": {"type": "string"},
    "unmapped": {"type": "object"},
    "history": {"type": "array"},          # the update history of an entry (CR26)
    "flows": {"type": "array"},            # process flows written out in the source (CR26)
    "class-variants": {"type": "object"},  # CR26
    "ctl": {"type": "object"},             # CR26
}

def compat_schema():
    """The pinned file of the compat facet, the same in every bundle: write it to `schemas/` + COMPAT_FILE."""
    return {"id": COMPAT_ID, "version": COMPAT_VERSION, "modifies-semantics": [], "note": COMPAT_NOTE,
            "schema": {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object",
                       "properties": copy.deepcopy(COMPAT_PROPERTIES), "additionalProperties": False}}

def referred_to(doc, element, reference="#{}"):
    """Does a string of `doc` outside `element` (a dict of it that has a `uuid`) hold a reference to the element?
    The converter's side of Ledger.orphan(): what is referred to is carried, what is not is declared an orphan."""
    needle = reference.format(element["uuid"])
    def walk(n):
        if n is element: return False
        if isinstance(n, dict): return any(walk(v) for v in n.values())
        if isinstance(n, list): return any(walk(v) for v in n)
        return isinstance(n, str) and needle in n
    return walk(doc)

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

def needs_kernel_2(objects):
    """True when one of the objects carries what the 1.0.0 kernel cannot
    type, so that the manifest must pin `kernel-version` 2.0.0 (KERNEL-1).
    The rule is `kernel_needed` of validate_core.py; this is its copy for a
    writer that has no schema at hand, so it tells the types apart by the
    fields only they carry. test_oscal_conv_lib.py holds it to the pin
    vectors of the conformance corpus.

    Until 2026-11-13 this test knew a Risk and `risk-refs` and nothing else:
    a converter that had written a Check, a `product-version` or a
    `provenance` on an Implementation would have shipped a bundle the
    validator refuses."""
    def deviations(o):
        out = [d for d in o.get("deviations") or [] if isinstance(d, dict)]
        if "selects" in o:                                   # a Tailoring carries them inline on an operation too
            out += [op["deviation"] for op in o.get("operations") or []
                    if isinstance(op, dict) and isinstance(op.get("deviation"), dict)]
        return out
    for o in objects:
        if "scenario" in o and "owner-ref" in o: return True                      # a Risk
        if o.get("risk-refs") or o.get("check-ref"): return True                  # a Finding that names one, or a Check
        if "criteria" in o and "observes" in o: return True                       # a Check
        if "performer-ref" in o and (o.get("check-results") or o.get("tailoring-ref")): return True
        if "kind" in o:                                                           # a Component
            if "product-version" in o: return True
            if any(c.get("statement-ids") for c in o.get("capabilities") or [] if isinstance(c, dict)): return True
            if any("date" in a for a in o.get("authorizations") or [] if isinstance(a, dict)): return True
        # `provenance` is 1.0.0 on a Mapping (which has a relationship) and came with the Check
        if "provenance" in o and "relationship" not in o: return True
        if "selects" in o and any("provenance" in e for k in ("selects", "excludes", "operations")
                                  for e in o.get(k) or [] if isinstance(e, dict)): return True
        if any("decided" in d or "review-due" in d for d in deviations(o)): return True
    return False

class Bundle:
    def __init__(self, out_dir, lang="en"):
        self.out = out_dir
        self.lang = lang           # corpus language: #12 textify at write time
        self.objects = {}          # relpath -> obj
        self.schemas = {}          # relpath -> pinned schema obj
    def add(self, relpath, obj):
        # MANIFEST-1 (backlog #75): what is added here is listed in the manifest,
        # and no manifest lists an Attestation (D3.1). An Attestation binds the
        # digest of the manifest's bytes, so it is written after the manifest
        # and beside it, as convert_ifa.py does. The IFA bundle listed its own
        # until 2026-11-13, and no validator said so.
        if isinstance(obj, dict) and "subject-semantic-digests" in obj and "content-manifest-digest" in obj:
            raise SystemExit(f"{relpath}: an Attestation is not an object of a bundle's manifest (MANIFEST-1, D3.1); "
                             f"write it beside the manifest, after the manifest is written")
        self.objects[relpath] = obj
    def stub(self, name, fid, mods, props,
             note="NORMATIVE pinned payload schema (backlog #26): closed shape - unknown keys are rejected, never smuggled",
             version="1.0.0"):
        # #26 delivered: pins are the normative payload contract, fail-closed.
        # (method name kept for call-site stability; these are no longer stubs)
        self.schemas[f"schemas/{name}"] = {
            "id": fid, "version": version, "modifies-semantics": mods, "note": note,
            "schema": {"$schema": "https://json-schema.org/draft/2020-12/schema",
                       "type": "object", "properties": props,
                       "additionalProperties": False}}
    def pin_compat(self):
        """Pins the one compat schema (compat_schema() below)."""
        self.schemas[f"schemas/{COMPAT_FILE}"] = compat_schema()
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
        if needs_kernel_2(self.objects.values()):
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
#   intentionally-dropped  no destination, and a drop() or drop_value()
#                          declaration says why
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

class _TFloat(_Tracked, float):
    def __new__(cls, value, origins=(), rule=None, fn=None, inputs=()):
        self = float.__new__(cls, value)
        self._origins, self._rule, self._fn, self._inputs = tuple(origins), rule, fn, tuple(inputs)
        return self

class _TBool(_Tracked):
    """A boolean that knows where it came from. `bool` cannot be subclassed,
    and json writes `true` and `false` for the two singletons only, so this
    stands in the objects a converter builds until Ledger.resolve() puts the
    plain boolean in its place and remembers where it stood. It is true or
    false as its value is, equal to the plain boolean, and json cannot write
    it: a converter that forgets resolve() stops instead of writing a wrong
    file."""
    __slots__ = ("_value", "_origins", "_rule", "_fn", "_inputs")
    def __init__(self, value, origins=(), rule=None, fn=None, inputs=()):
        self._value = bool(value)
        self._origins, self._rule, self._fn, self._inputs = tuple(origins), rule, fn, tuple(inputs)
    def __bool__(self): return self._value
    def __eq__(self, other): return self._value == (other._value if isinstance(other, _TBool) else other)
    def __ne__(self, other): return not self.__eq__(other)
    def __hash__(self): return hash(self._value)
    def __repr__(self): return repr(self._value)

def _track(value, origins, rule=None, fn=None, inputs=(), typed=True):
    """`typed`: also a boolean and a fraction carry their origin (a _TBool
    needs Ledger.resolve() before the objects are written)."""
    if value is None: return value                                  # states nothing
    if isinstance(value, bool): return _TBool(value, origins, rule, fn, inputs) if typed else value
    if isinstance(value, str): return _TStr(value, origins, rule, fn, inputs)
    if isinstance(value, int): return _TInt(value, origins, rule, fn, inputs)
    if isinstance(value, float): return _TFloat(value, origins, rule, fn, inputs) if typed else value
    return value

def _plain(v):
    """A tracked value as the plain scalar it is (for typed comparison)."""
    if isinstance(v, _TStr): return str.__str__(v)
    if isinstance(v, _TBool): return v._value
    if isinstance(v, _TInt): return int(v)
    if isinstance(v, _TFloat): return float(v)
    return v

def _at(doc, parts):
    for x in parts: doc = doc[x]
    return doc

# What becomes of a source leaf value. `not-content` (2026-11-14): what may
# stay out of a bundle by a rule that account() checked - a name that only
# selects a field, a namespace, an id that is rebuilt exactly, and (the
# author's fourth class of the same day) an element nothing refers to.
LEDGER_OUTCOMES = ("copied", "transformed", "not-content", "intentionally-dropped", "unaccounted")

def ledger_gate(result, converter):
    """Ends a converter's run with 1 when its ledger has a claim that does not
    hold or a source value that is unaccounted (author, 2026-11-14: "a
    converter run with an unaccounted value exits non-zero"). Call it last,
    after the bundle, the reports and the record are written: the run fails,
    and what it wrote says why."""
    bad = len(result["verification-failures"]), result["totals"]["unaccounted"]
    if any(bad):
        raise SystemExit(f"{converter}: the conversion ledger has {bad[0]} claim(s) that do not hold and {bad[1]} source "
                         f"value(s) unaccounted - content is never dropped, and what is no content is so by a rule "
                         f"the ledger checks (see the record and the report this run wrote)")

class Ledger:
    def __init__(self):
        self.docs = {}          # tag -> the source document as loaded (never tracked)
        self.leaves = []        # (tag, parts) of every source leaf, in document order
        self._drops = []        # (compiled regex over the collapsed path, reason)
        self._value_drops = {}  # (tag, parts) -> reason, for a single source leaf
        self._same = []         # (dropped tracked value, kept tracked value, rule)
        self._placed = []       # (tracked boolean, destination) noted by resolve()
        self._not_content = {}  # (tag, parts) -> (kind, rule, check, origins it depends on)
        self._refs = {}         # (tag, uuid, prefix) -> is the element referred to from outside itself

    def source(self, tag, doc, typed=False):
        """-> a copy of `doc` whose string and integer leaves carry their origin.
        `typed=True`: its booleans and fractions carry theirs too. A converter
        that asks for it calls resolve() on its objects before it writes them;
        without it a boolean and a fraction stay plain, as they were until
        2026-11-14, and a value the converter carries reads as unaccounted."""
        assert tag not in self.docs, f"source tag {tag} used twice"
        self.docs[tag] = doc
        def walk(n, parts):
            if isinstance(n, dict): return {k: walk(v, parts + (k,)) for k, v in n.items()}
            if isinstance(n, list): return [walk(v, parts + (i,)) for i, v in enumerate(n)]
            self.leaves.append((tag, parts))
            return _track(n, [(tag, parts)], typed=typed)
        return walk(doc, ())

    def resolve(self, objects):
        """objects: {relpath: object}, as account() takes them, BEFORE they are
        written and before a digest is taken of them. Puts the plain boolean in
        the place of every tracked one and remembers where it stood, so that
        account() can hold the claim against the file. A tracked boolean that
        is left in an object makes json refuse to write it."""
        def note(v, rel, oid, parts):
            self._placed.append((v, {"object": oid, "file": rel, "pointer": _pointer(parts), "as": "value"}))
            return v._value
        def walk(n, rel, oid, parts):
            if isinstance(n, dict):
                for k in list(n):
                    if isinstance(n[k], _TBool): n[k] = note(n[k], rel, oid, parts + [k])
                    else: walk(n[k], rel, oid, parts + [k])
            elif isinstance(n, list):
                for i, v in enumerate(n):
                    if isinstance(v, _TBool): n[i] = note(v, rel, oid, parts + [i])
                    else: walk(v, rel, oid, parts + [i])
        for rel, obj in sorted(objects.items()):
            walk(obj, rel, (obj.get("id") if isinstance(obj, dict) else None) or rel, [])

    def derive(self, rule, fn, *inputs):
        """-> fn(*inputs), carrying the origins of every tracked input. The
        function is kept: account() calls it again on the source's own values."""
        value = fn(*inputs)
        if not isinstance(value, (str, int, float, _TBool)):        # bool is an int
            raise TypeError(f"rule {rule}: a derived value must be a string, a number or a boolean to carry its "
                            f"origin, got {type(value).__name__}")
        origins = [o for x in inputs if isinstance(x, _Tracked) for o in x._origins]
        return _track(_plain(value), origins, rule, fn, inputs)       # a boolean result needs resolve() before the write

    def drop(self, pattern, reason):
        """Declare that source leaves whose collapsed path matches `pattern`
        are not carried, and why. Applies only where no destination exists."""
        self._drops.append((re.compile(pattern), reason))

    def drop_value(self, value, reason):
        """Declare that THIS source value (a tracked value, or a structure of
        them) is not carried, and why. For a decision that depends on the
        value and not on its path: one party reference among many names a
        party without a name. Like drop(), it applies only where no
        destination exists."""
        if isinstance(value, dict):
            for v in value.values(): self.drop_value(v, reason)
        elif isinstance(value, list):
            for v in value: self.drop_value(v, reason)
        elif isinstance(value, _Tracked) and value._rule is None:
            for origin in value._origins: self._value_drops.setdefault(origin, reason)

    # ---- what is no content (author, 2026-11-14) -------------------------
    # "Real content is never dropped. What may stay out of a bundle is only
    # what is not content: a name that merely selects a field, a namespace,
    # an id that is rebuilt exactly from another value. Each such class
    # needs a stated rule that the ledger checks." The three methods below
    # are those three classes. Each claim is checked by account(): against
    # the source's own values, and against what became of the values the
    # claim rests on. A name that selects a value which is not in the bundle
    # selects nothing, and an id rebuilt from a value the bundle does not
    # hold cannot be rebuilt from the bundle; such a leaf is not "no
    # content", it is unaccounted (or dropped, where what it rests on is a
    # declared drop). A leaf that has a destination is carried, whatever is
    # declared for it here.
    @staticmethod
    def _leaf_origins(x):
        out = []
        def walk(n):
            if isinstance(n, dict):
                for k, v in n.items(): walk(k); walk(v)
            elif isinstance(n, (list, tuple)):
                for v in n: walk(v)
            elif isinstance(n, _Tracked): out.extend(n._origins)
        walk(x)
        return out

    def _declare(self, value, kind, rule, check, rests_on, needs=True):
        if not isinstance(value, _Tracked) or value._rule is not None or len(value._origins) != 1:
            raise TypeError(f"{kind} ({rule}): the value must be one leaf of a source, as source() gave it")
        me = value._origins[0]
        rests = tuple(o for o in rests_on if o != me)                # a prop handed over whole holds its own name
        if needs and not rests: raise ValueError(f"{kind} ({rule}): it stands beside no other source value")
        self._not_content.setdefault(me, (kind, rule, check, rests))

    def selector(self, name, rule, selects, among=None):
        """`name` (the name of a prop or of a part, a class) is no content: it
        only says which field the value beside it belongs in. `selects`: that
        value, or the structure of values it selects; there must be one.
        `among`: the names this converter's mapping knows, if the claim is to
        be held to them. It shares the fate of what it selects: unaccounted
        while one of those values is, dropped when all of them are dropped,
        and no content otherwise."""
        check = (lambda v: v in among) if among is not None else (lambda v: True)
        self._declare(name, "selector", rule, check, self._leaf_origins(selects))

    def namespace(self, ns, rule, allowed, of):
        """`ns` is the namespace that qualifies the name `of` (or a structure
        of names): no content when its value is one of `allowed` - the
        namespaces this converter's mapping is written for - and what it
        qualifies is accounted for (as for a selector). Another namespace is
        another meaning of the name, and is not covered: the claim is
        reported as one that does not hold."""
        allowed = frozenset(allowed)
        self._declare(ns, "namespace", rule, lambda v: v in allowed, self._leaf_origins(of))

    def rebuilt(self, value, rule, fn, *inputs):
        """`value` is an id (or a label made from one) that fn(*inputs) gives
        exactly: no content, because nothing is lost without it. Checked: the
        function, applied to the source's own values, gives the source value;
        and every source value among the inputs is accounted for, so that the
        bundle still holds what the id is rebuilt from (one input that is
        dropped, and the id is dropped with it). A value that the function
        does not give is not covered, and the claim is reported as one that
        does not hold. The inputs are single values, a source's or plain."""
        self._declare(value, "rebuilt-id", rule, (fn, tuple(inputs)), self._leaf_origins(inputs), needs=False)

    def orphan(self, uuid, rule, reference="#{}"):
        """The element that holds `uuid` (a back-matter resource) is orphaned:
        nothing else in its document refers to it, so nobody can reach it
        and it is not carried (author, 2026-11-14: "orphaned elemente
        braucht niemand"). `uuid`: the element's own uuid, as source() gave
        it; every leaf of the element is covered. `reference`: how the
        document refers to such an element, with {} for the uuid (OSCAL
        writes a link to a back-matter resource as `#uuid`). Checked by
        account(): no string of the same document outside the element
        contains that reference. Where one does, the claim does not hold and
        the leaves are unaccounted. A leaf that has a destination is carried
        all the same."""
        if not isinstance(uuid, _Tracked) or uuid._rule is not None or len(uuid._origins) != 1:
            raise TypeError(f"orphan ({rule}): the uuid must be one leaf of a source, as source() gave it")
        tag, parts = uuid._origins[0]
        prefix, value = parts[:-1], reference.format(_plain(uuid))
        if not prefix: raise ValueError(f"orphan ({rule}): the uuid of the document itself is no element of it")
        check = lambda _v, tag=tag, prefix=prefix, value=value: not self._referred_to(tag, value, prefix)
        for t, leaf in self.leaves:
            if t == tag and leaf[:len(prefix)] == prefix:
                self._not_content.setdefault((t, leaf), ("orphan", rule, check, ()))

    def _referred_to(self, tag, value, prefix):
        """Does a string of document `tag` outside the element at `prefix` contain `value`?"""
        key = (tag, value, prefix)
        if key not in self._refs:
            def walk(n, parts):
                if parts[:len(prefix)] == prefix and len(parts) >= len(prefix): return False
                if isinstance(n, dict): return any(walk(v, parts + (k,)) for k, v in n.items())
                if isinstance(n, list): return any(walk(v, parts + (i,)) for i, v in enumerate(n))
                return isinstance(n, str) and value in n
            self._refs[key] = walk(self.docs[tag], ())
        return self._refs[key]

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
        for value, dest in self._placed:                   # the booleans resolve() took out of the objects
            if dest["file"] in written: found[id(value)].append((value, dest))
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
        # 3a. every leaf with a destination that holds is carried
        carried = {}                                # origin -> [destination]
        for tag, parts in self.leaves:
            origin, dests = (tag, parts), []
            for value, dest, via in by_origin.get(origin, []):
                d = {"object": dest["object"], "pointer": dest["pointer"]}
                if dest["as"] == "key": d["as"] = "key"
                if value._rule: d["rule"] = value._rule
                if via: d["via"] = via
                if not holds(value, origin, dest):
                    failures.append({"source": f"{tag}#{_pointer(parts)}", **d}); continue
                dests.append(d)
            if dests: carried[origin] = dests
        # 3b. what became of a leaf: carried, no content by a rule that holds, dropped for a declared reason, or
        #     unaccounted. A leaf declared no content rests on other leaves and shares their fate.
        def declared_drop(origin):
            reason = self._value_drops.get(origin)
            if reason is None:
                path = self.collapsed(*origin)
                reason = next((why for rx, why in self._drops if rx.search(path)), None)
            return reason
        state = {}                                  # origin -> (outcome, detail)
        def fate(origin, seen=()):
            if origin in state: return state[origin]
            if origin in carried: r = ("carried", None)
            elif origin in self._not_content and origin not in seen:
                kind, rule, check, rests = self._not_content[origin]
                here = _at(self.docs[origin[0]], origin[1])
                if isinstance(check, tuple): ok = _token(check[0](*[fresh(i) for i in check[1]])) == _token(here)
                else: ok = bool(check(here))
                if not ok:
                    failures.append({"source": f"{origin[0]}#{_pointer(origin[1])}", "claim": kind, "rule": rule})
                    r = ("unaccounted", None)
                else:
                    below = [fate(o, seen + (origin,)) for o in rests]
                    gone = [b[1] for b in below if b[0] == "intentionally-dropped"]
                    if any(b[0] == "unaccounted" for b in below): r = ("unaccounted", None)
                    elif gone and (kind == "rebuilt-id" or len(gone) == len(below)):
                        r = ("intentionally-dropped", f"{rule} - of a value that is dropped: {gone[0]}")
                    else: r = ("not-content", {"kind": kind, "rule": rule})
            else:
                reason = declared_drop(origin)
                r = ("intentionally-dropped", reason) if reason is not None else ("unaccounted", None)
            state[origin] = r
            return r
        entries, totals = [], collections.Counter()
        unaccounted = collections.defaultdict(list)
        for tag, parts in self.leaves:
            origin, path = (tag, parts), self.collapsed(tag, parts)
            entry = {"source": f"{tag}#{_pointer(parts)}", "path": path}
            outcome, detail = fate(origin)
            if outcome == "carried":
                dests = carried[origin]
                outcome = "copied" if any("rule" not in d for d in dests) else "transformed"
                entry["destinations"] = sorted(dests, key=lambda d: (d["object"] or "", d["pointer"]))
            elif outcome == "not-content": entry.update(detail)
            elif outcome == "intentionally-dropped": entry["reason"] = detail
            else: unaccounted[path].append(entry["source"])
            entry["outcome"] = outcome; totals[outcome] += 1
            entries.append(entry)
        return {"measures": "one entry per source leaf value: where it went, checked against the written files",
                "leaf-values": len(self.leaves),
                "totals": {k: totals[k] for k in LEDGER_OUTCOMES},
                "verification-failures": failures,
                "unaccounted-paths": [{"path": p, "count": len(w), "pointers": w} for p, w in sorted(unaccounted.items())],
                "entries": entries}

def ledger_by_path(result, examples=3, collapse=()):
    """The ledger of a large corpus in the size of its path map: one row per
    source path and outcome, where Ledger.account() gives one entry per
    source leaf value (backlog #41, phase E).

    account() traces and checks every leaf; for the IFA corpus its 835
    entries are the committed record. SP 800-53 has 115,680 leaf values, and
    a record of one entry each would be some fifty megabytes. This keeps what
    the entries say and drops what repeats: for every source path and
    outcome the number of leaf values, the first of them as an example, and
    where they went - the destination pointers with their array indices
    collapsed to `[]`, each with its count and, for a transformed value, its
    rule - or why they were dropped. Nothing is estimated: every row is a
    count over entries that account() checked against the written files, and
    the counts add up to `leaf-values`.

    `unaccounted-paths` keeps the first `examples` pointers of each path and
    the count; the per-leaf list is in the run that wrote it, not in the
    record. `collapse`: (pattern, replacement) pairs applied to a destination
    pointer before its array indices are collapsed, for a payload that is
    keyed by a source value (a statement id, a parameter name) and would
    otherwise give one row per key. -> a JSON-able dict."""
    collapse = [(re.compile(p), r) for p, r in collapse]
    rows, order = {}, []
    for e in result["entries"]:
        key = (e["path"], e["outcome"])
        r = rows.get(key)
        if r is None:
            r = rows[key] = {"path": e["path"], "outcome": e["outcome"], "count": 0, "example": e["source"],
                             "_to": collections.Counter(), "_why": collections.Counter(), "_rule": collections.Counter()}
            order.append(key)
        r["count"] += 1
        if "reason" in e: r["_why"][e["reason"]] += 1
        if e["outcome"] == "not-content": r["_rule"][(e["kind"], e["rule"])] += 1
        for d in e.get("destinations", []):
            where = d["pointer"]
            for rx, to in collapse: where = rx.sub(to, where)
            where = re.sub(r"/[0-9]+(?=/|$)", "/[]", where)
            r["_to"][(where, d.get("as", "value"), d.get("rule", ""), d.get("via", ""))] += 1
    paths = []
    for key in sorted(order):
        r = rows[key]
        row = {"path": r["path"], "outcome": r["outcome"], "count": r["count"], "example": r["example"]}
        if r["_to"]:
            row["to"] = []
            for (where, as_, rule, via), n in sorted(r["_to"].items()):
                d = {"pointer": where, "count": n}
                if as_ != "value": d["as"] = as_
                if rule: d["rule"] = rule
                if via: d["via"] = via
                row["to"].append(d)
        if r["_why"]:
            row["reasons"] = [{"reason": why, "count": n} for why, n in sorted(r["_why"].items())]
        if r["_rule"]:
            row["rules"] = [{"kind": kind, "rule": rule, "count": n} for (kind, rule), n in sorted(r["_rule"].items())]
        paths.append(row)
    assert sum(r["count"] for r in paths) == result["leaf-values"]
    return {"measures": "one row per source path and outcome; every source leaf value was traced and checked "
                        "against the written files in the run that wrote this record, and is counted in one row",
            "leaf-values": result["leaf-values"],
            "totals": dict(result["totals"]),
            "verification-failures": list(result["verification-failures"]),
            "unaccounted-paths": [{"path": u["path"], "count": u["count"], "pointers": u["pointers"][:examples]}
                                  for u in result["unaccounted-paths"]],
            "paths": paths}

def props_by_name(props, ledger=None, field="value"):
    """OSCAL props [{name, value}, ...] -> {name: value}. A name that repeats
    keeps EVERY value, as a list in source order - the rule parameter
    bindings already follow (one value as it is, several as a list).
    `field` picks another member of the prop instead of its value (`class`);
    a prop without that member is left out.

    Until 2026-11-13 the IFA converter wrote `{p["name"]: p["value"] for p in
    props}`. A dict keeps one value per key, so of two `ipv4-address` props of
    one inventory item the first address was overwritten and the bundle
    shipped without it. The conversion ledger found it: one value with no
    destination. With a ledger, the repeated name is linked to the key that
    stands for it."""
    out = {}
    for p in props or []:
        if field not in p: continue
        name, value = p["name"], p[field]
        if name not in out:
            out[name] = value; continue
        if ledger is not None:
            key = next(k for k in out if k == name)          # the key object the dict already holds
            ledger.same(name, key, "a prop name that repeats is one key; its values are listed in source order")
        out[name] = out[name] + [value] if isinstance(out[name], list) else [out[name], value]
    return out

# OSCAL's risk response carries a `type` prop with seven allowed values:
# avoid, mitigate, transfer, accept, share, contingency, none. C.10 has four
# treatment options (ISO 31000 6.5.2; one to one with BSI 200-3). Five of
# the seven are one of the four. The other two are decided (backlog #47b,
# 2026-11-13) and neither gets a code:
#   none         the source says that no option was chosen. A Risk says the
#                same by carrying no `treatment`, so nothing is lost.
#   contingency  a plan for the day the risk materialises. It is none of the
#                four options, and no corpus instance has been counted
#                (D22, test 3: a code needs one).
# In both cases the response itself stays verbatim in the converter's facet.
RESPONSE_TREATMENT = {"avoid": "avoid", "mitigate": "modify", "transfer": "share",
                      "share": "share", "accept": "retain"}

def response_treatment(rtype):
    """OSCAL risk response type -> (C.10 treatment option or None, a report
    line saying why there is none, or None). Never guesses: a value outside
    the five mapped ones gives no option, and the caller counts the line."""
    if rtype in RESPONSE_TREATMENT:
        return RESPONSE_TREATMENT[rtype], None
    if rtype == "none":
        return None, "response type `none`: the source chose no option, so no `treatment` is written (C.10)"
    return None, f"response type `{rtype}` has no treatment code (C.10)"

# ---------- who wrote a record, and when (backlog #69) ----------
# The kernel has one place for it since 2.0.0-rc.4: `provenance`
# {author-ref, date}, optional on a Tailoring and its entries, a Risk and
# its ratings, an Implementation, a Finding, a Mapping and a Check. A
# converter pre-fills it from what the source says and lets the caller
# overwrite it (author decision 2026-11-13: "all converters should pre-fill
# that data from the source corpus but import tool should be able to
# overwrite it"). Nothing is invented: where the source names nobody, or no
# day, the record gets no `provenance` and the validator reports it
# (AUTHOR-1 to 4).
#
# An OSCAL document says who is responsible for it in its metadata, by role,
# and when it was last changed. It does not say who wrote one statement of
# it. The author of the document is therefore the most a converter can
# pre-fill for a record taken from it, and the day of `last-modified` the
# latest day the record can have been written. The rule below is the same
# rule in jascon-app/jascon-oscal.js; the test table is shared.
# What it rests on: OSCAL 1.1.3 defines the role ids `creator` ("the person
# or organization that created this content") and `prepared-by` ("... that
# prepared this content") for a document's metadata (read 2026-11-13:
# oscal_metadata_metaschema.xml at tag v1.1.3). Steps 2 to 4 are not
# OSCAL's: they are this library's reading of a document that uses neither
# role, and they give an answer only where exactly one candidate exists.
_DAY = re.compile(r"[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])\Z")

def document_author(metadata):
    """-> the party (the entry of `metadata.parties`) an OSCAL document names
    as its author, or None.
      1. the one party named for the role `creator`, else for `prepared-by`;
      2. else the one party that the responsible-parties name at all;
      3. else the one party the document defines;
      4. else the one organization among the parties it defines;
      5. else nobody.
    "The one" is exact: two candidates are no answer, and the next step is
    asked. A uuid the document does not define names nobody. A party without
    a name cannot be named by a landmark URI, so it is nobody too. A party is
    an entry of `parties` with a uuid; where a uuid is defined twice, the
    first definition is the party (the two rules agreed on everything but
    this when 4,000 generated documents were put to both, 2026-11-14)."""
    plist = []
    for x in metadata.get("parties", []) or []:
        if isinstance(x, dict) and isinstance(x.get("uuid"), str) and all(x["uuid"] != y["uuid"] for y in plist):
            plist.append(x)
    def defined(uuid): return next((x for x in plist if x["uuid"] == uuid), None)
    def named(role=None):
        seen = []
        for rp in metadata.get("responsible-parties", []) or []:
            if role is None or rp.get("role-id") == role:
                for u in rp.get("party-uuids", []) or []:
                    if defined(u) is not None and u not in seen: seen.append(u)
        return seen
    pick = None
    for got in (named("creator"), named("prepared-by"), named()):
        if len(got) == 1: pick = defined(got[0]); break
    if pick is None and len(plist) == 1: pick = plist[0]
    if pick is None:
        orgs = [x for x in plist if x.get("type") == "organization"]
        if len(orgs) == 1: pick = orgs[0]
    return pick if pick is not None and pick.get("name") else None

def is_day(value):
    """True for a string that is a date as the kernel writes one, YYYY-MM-DD."""
    return isinstance(value, str) and bool(_DAY.match(value))

def document_day(metadata):
    """-> the day of the document's `last-modified`, as the document wrote it
    (its first ten characters), or None when they are not a date."""
    lm = metadata.get("last-modified")
    return lm[:10] if isinstance(lm, str) and _DAY.match(lm[:10]) else None

def provenance(author, date, override=(None, None)):
    """What the source states, overwritten field by field by what the caller
    gave. -> {author-ref, date}, or None unless both are known: the kernel's
    `provenance` is closed and requires both."""
    a, d = override[0] or author, override[1] or date
    return {"author-ref": a, "date": d} if a and d else None

def provenance_override(argv):
    """Reads `--author-ref URI` and `--date YYYY-MM-DD` from a converter's
    arguments -> (author or None, date or None). Other arguments are left to
    the converter. A value that is not what it must be stops the run: an
    overwrite the caller asked for is never dropped silently."""
    author = date = None
    for i, a in enumerate(argv):
        if a not in ("--author-ref", "--date"): continue
        if i + 1 >= len(argv): raise SystemExit(f"{a} needs a value")
        v = argv[i + 1]
        if a == "--author-ref":
            if not re.match(r"https?://[^\s]+\Z", v): raise SystemExit(f"--author-ref {v!r} is not an http(s) URI of a party")
            author = v
        else:
            if not _DAY.match(v): raise SystemExit(f"--date {v!r} is not a date, YYYY-MM-DD")
            try: time.strptime(v, "%Y-%m-%d")
            except ValueError: raise SystemExit(f"--date {v!r} is not a day of the calendar")
            date = v
    return author, date

def obligated_party(argv, default):
    """Whom a statement binds where the source does not say (backlog #74)
    -> (party URI, "converter-default" | "caller").

    The kernel requires `obligated-parties` on every statement. A catalogue
    seldom says whom its controls bind, so each converter names one party
    for its corpus. That party is the converter's reading of the framework
    and not a value of the source; the author decided on 2026-11-14 that it
    is an argument with a named default. `--obligated-party URI` among a
    converter's arguments puts the caller's party in the default's place.

    Where a source does name a party for a statement (an implementation
    level in SP 800-53, `affects` in CR26), a converter writes what the
    source says and uses this party only where the source is silent.

    A value that is no http(s) URI stops the run, and so does the argument
    given twice: an overwrite the caller asked for is never dropped or
    guessed. There is no way to ask for no party at all: the kernel requires
    one, and no tool writes a party nobody named (#70)."""
    if not re.match(r"https?://[^\s]+\Z", default or ""):
        raise SystemExit(f"the converter's default obligated party {default!r} is not an http(s) URI")
    given = [i for i, a in enumerate(argv) if a == "--obligated-party"]
    if not given: return default, "converter-default"
    if len(given) > 1: raise SystemExit("--obligated-party is given more than once")
    if given[0] + 1 >= len(argv): raise SystemExit("--obligated-party needs a value")
    v = argv[given[0] + 1]
    if not re.match(r"https?://[^\s]+\Z", v): raise SystemExit(f"--obligated-party {v!r} is not an http(s) URI of a party")
    return v, "caller"

def lifecycle_default_record(objects, stated):
    """What a coverage report's JSON says under `lifecycle-default`: the
    kernel requires a lifecycle on every object, and where the source states
    no status the converter writes `active` as its own, named default
    (author, 2026-11-14). objects: {relpath: object} of the bundle; stated:
    the ids of the objects whose lifecycle is the source's word (a status
    mapped by a rule)."""
    stated = set(stated)
    own = [o for o in objects.values() if isinstance(o, dict) and "lifecycle" in o and o.get("id") not in stated]
    other = sorted({o["lifecycle"] for o in own} - {"active"})
    if other: raise SystemExit(f"lifecycle {other} is written on an object whose status the source does not state: "
                               f"the converter's default is `active` and nothing else")
    return {"value": "active", "origin": "converter-default", "objects": len(own),
            "source-states": sum(1 for o in objects.values() if isinstance(o, dict) and o.get("id") in stated)}

def lifecycle_default_line(record, why="a published catalogue is taken to be in force", tail=None):
    """The line of a coverage report (markdown) for lifecycle_default_record().
    `why`: the converter's reason for the default, as a clause. `tail`: what
    the source says of status, where neither of the two sentences below fits
    (a source that states a status no rule maps to a lifecycle)."""
    n, m = record["objects"], record["source-states"]
    if tail is None:
        tail = (f" On {m:,} object(s) the lifecycle is the source's own status, mapped by a rule." if m
                else " The source states no status on any object.")
    return (f"- **Lifecycle**: `active` on {n:,} object(s) is the converter's default and not a value of the source: "
            f"the kernel requires a lifecycle on every object, and {why}." + tail)

def obligated_party_record(party, origin, default, source_states=None):
    """What a coverage report's JSON says about it, under `obligated-party`:
    the party written, who chose it, the converter's default, and - where a
    source names parties itself - how (`source_states`: a phrase that
    completes "the source names a party ...", e.g. "as the implementation
    level of a control")."""
    r = {"value": party, "origin": origin, "converter-default": default}
    if source_states: r["source-states"] = source_states
    return r

def obligated_party_line(party, origin, default, why="", source_states=None):
    """The line of a coverage report (markdown) that says whom the statements
    bind and who said so. `why`: the converter's reason for its default, as a
    sentence without a full stop. `source_states`: see obligated_party_record."""
    where = (f"on every statement for which the source names no party; where it names one ({source_states}), "
             f"that one is written. `{party}` is" if source_states else "on every statement")
    reason = f" Why this default: {why}." if why else ""
    if source_states:
        if origin == "caller":
            return (f"- **Obligated party**: `{party}` {where} given by the caller with `--obligated-party`; "
                    f"the converter's own default is `{default}`.{reason}")
        return (f"- **Obligated party**: `{party}` {where} the converter's default and not a value of the "
                f"source; `--obligated-party URI` writes another.{reason}")
    if origin == "caller":
        return (f"- **Obligated party**: `{party}` {where}, given by the caller with `--obligated-party`. "
                f"The converter's own default is `{default}`.{reason}")
    return (f"- **Obligated party**: `{party}` {where}. This is the converter's default and not a value of "
            f"the source; `--obligated-party URI` writes another.{reason}")

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
