#!/usr/bin/env python3
"""Shared machinery for OSCAL-catalog -> Semantic Core converters.
House method: full source path inventory, declared destination map,
UNMAPPED = 0 as the gate signal, computed coverage report, manifest
with both digests. Every converter stays a thin corpus adapter."""
import json, hashlib, os, re, copy, collections, shutil, time

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
        with open(p, "w", encoding="utf-8") as f:
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
        manifest = {"manifest-version": "1", "provenance": provenance,
                    "objects": [{"id": o["id"], "version": o["version"],
                                 "package-digest": self._sha(rel),
                                 "semantic-digest": semantic_digest(o), "path": rel}
                                for rel, o in sorted(self.objects.items())],
                    "facet-schemas": [{"id": s["id"], "exact-version": s["version"],
                                       "digest": self._sha(rel), "path": rel}
                                      for rel, s in sorted(self.schemas.items())]}
        self._w("content-manifest.json", manifest)
        return manifest

def inventory(node, prefix, counter, normalize=lambda p: p):
    if isinstance(node, dict):
        for k, v in node.items(): inventory(v, f"{prefix}.{k}", counter, normalize)
    elif isinstance(node, list):
        for v in node: inventory(v, f"{prefix}[]", counter, normalize)
    else:
        counter[normalize(prefix)] += 1

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
