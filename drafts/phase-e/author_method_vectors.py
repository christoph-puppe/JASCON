#!/usr/bin/env python3
"""Writes the `method-vectors` of jascon/conformance/facet-vectors.json
(backlog #55, phase E of drafts/pre-2.0.0-fix-plan.md). Re-running it
changes nothing.

    python3 drafts/phase-e/author_method_vectors.py

An Assessment's `method` is a facet payload (handbook 10.1, appendix A.7):
its keys are facet ids, and each payload is held to the schema of its facet
as a payload under `facets` is - a standard-library facet to the normative
descriptor, any other to the schema the bundle pins, `private:` ignored by
definition, anything else an error (D10: fail closed). Until 2026-11-14 no
implementation read `method` at all: the kernel schema says it is an
object, and the facet check looked at `facets` only.

A vector gives one object, the schemas a bundle would pin (`pinned`, keyed
by the facet id without its version, as in the older vectors of this file)
and expects the number of errors and a fragment of each. The expectations
are written by hand, below, before any implementation ran against them.
The seven older vectors of the file are kept byte for byte."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
CRITERIA = "https://ns.jascon.net/stdlib/facet/assessment-criteria@1"
OWN = "https://assessor.example/facet/review"            # a facet of the assessor's own, pinned by the bundle
OWN_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["standard"],
              "properties": {"standard": {"type": "string"}, "sample-size": {"type": "integer"}}}

def assessment(method, facets=None):
    o = {"id": "https://assessor.example/assessment/a1", "version": "1", "lifecycle": "active",
         "subject-refs": ["https://org.example/component/app"], "method": method,
         "performer-ref": "https://assessor.example/party/lead", "time": "2026-11-14", "result": "satisfied"}
    if facets is not None: o["facets"] = facets
    return o

V = []
def vec(name, obj, errors, frags, note, pinned=None):
    v = {"name": name, "note": note, "object": obj}
    if pinned: v["pinned"] = pinned
    v.update({"expected": "invalid" if errors else "valid", "expected-errors": errors, "expected-frags": frags})
    V.append(v)

vec("method-stdlib-valid", assessment({CRITERIA: {"method": "manual", "summary": {"en": "Document review of the rotation records."}}}), 0, [],
    "The standard assessment-criteria facet, a payload its descriptor accepts.")
vec("method-stdlib-payload-violates-its-schema", assessment({CRITERIA: {"method": "by-ear"}}), 1, [f"method '{CRITERIA}'"],
    "`method` inside the payload is `automated` or `manual`. The descriptor refuses anything else, under `method` as under `facets`.")
vec("method-stdlib-payload-with-a-member-the-facet-does-not-know", assessment({CRITERIA: {"kind": "review"}}), 1, [f"method '{CRITERIA}'"],
    "The descriptor is closed.")
vec("method-plain-key-is-no-facet", assessment({"kind": "review"}), 1, ["method 'kind'"],
    "The spelling older fixtures of this corpus used. `kind` is no facet id: not of the standard library, not pinned, not private. "
    "A tool that does not know what a method means must not guess at the verdict it produced (handbook 10.1).")
vec("method-unregistered-facet-uri", assessment({"https://example.org/facet/our-method@1": {"steps": 3}}), 1, ["method 'https://example.org/facet/our-method@1'"],
    "A facet id nobody registered: the bundle pins no schema for it.")
vec("method-pinned-valid", assessment({OWN + "@1": {"standard": "ISAE 3402", "sample-size": 25}}), 0, [],
    "The assessor's own facet, pinned by the bundle; the payload is what the pin says.", pinned={OWN: OWN_SCHEMA})
vec("method-pinned-payload-violates-the-pin", assessment({OWN + "@1": {"sample-size": "twenty-five"}}), 1, [f"method '{OWN}@1'"],
    "The pinned schema requires `standard` and types `sample-size`.", pinned={OWN: OWN_SCHEMA})
vec("method-private-is-ignored-by-definition", assessment({"private:lab-notes@1": {"whatever": [1, 2, 3]}}), 0, [],
    "`private:` declares that it changes no semantics; it is kept and never validated, under `method` as under `facets`.")
vec("method-two-facets-one-wrong", assessment({CRITERIA: {"method": "automated"}, "kind": "review"}), 1, ["method 'kind'"],
    "Every key is held, and one error is reported for the one that is wrong.")
vec("method-and-facets-are-both-held", assessment({"kind": "review"}, facets={"https://example.org/unregistered-facet@9": {"x": 1}}), 2,
    ["method 'kind'", "facet 'https://example.org/unregistered-facet@9'"],
    "An Assessment whose method and whose facets are both unregistered has two errors: the check of the one does not stand in for the other.")
vec("a-member-called-method-inside-a-payload-is-no-assessments-method",
    {"id": "https://ex.org/req/1", "version": "1", "lifecycle": "active",
     "statements": [{"id": "s1", "modality": "must", "obligated-parties": ["https://ex.org/party/org"], "prose": {"en": "X."}}],
     "facets": {CRITERIA: {"method": "automated"}}}, 0, [],
    "A Requirement that carries assessment criteria. The `method` inside that payload is a member of the facet, not the method of an Assessment.")
vec("an-empty-method-names-no-facet", assessment({}), 0, [],
    "The rule holds the keys there are. Whether an Assessment may state no method at all is not this rule's question: the kernel schema asks for "
    "an object and accepts an empty one.")

path = os.path.join(ROOT, "jascon", "conformance", "facet-vectors.json")
raw = open(path, encoding="utf-8").read()
ADD = (" method-vectors (backlog #55, 2026-11-14): an Assessment's `method` is a facet payload. Its keys are facet ids, resolved as the keys of "
       "`facets` are - the standard library, then the schemas the bundle pins, then `private:`, else an error - and each payload is held to its "
       "schema. `expected-errors` is the number of errors for the object. Each of `expected-frags` must occur in some error: an error about a method "
       "names it as method '<key>', one about a facet as facet '<key>'. The name of a vector is no part of an error.")
MARK = ',\n "method-vectors": '         # this file indents by one space
if MARK in raw: raw = raw[:raw.index(MARK)] + "\n}\n"            # written by an earlier run: replaced below
old = json.loads(raw)
end = '",\n "vectors": ['
assert raw.count(end) == 1, raw.count(end)
head = old["description"].split(" method-vectors (backlog #55")[0]
a = raw.index('"description": "') + len('"description": "')
raw = raw[:a] + json.dumps(head + ADD, ensure_ascii=False)[1:-1] + raw[raw.index(end):]
body = json.dumps(V, indent=1, ensure_ascii=False).replace("\n", "\n ")
raw = raw.rstrip()[:-1].rstrip() + MARK + body + "\n}\n"
doc = json.loads(raw)
assert doc["vectors"] == old["vectors"] and doc["method-vectors"] == V and doc["description"].endswith(ADD)
with open(path, "w", encoding="utf-8", newline="\n") as f: f.write(raw)
print(f"facet-vectors.json: {len(doc['vectors'])} vectors, {len(V)} method-vectors")
