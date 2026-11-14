#!/usr/bin/env python3
"""Writes the `binds-vectors` (backlog #46, phase D of
drafts/pre-2.0.0-fix-plan.md) and the `listed-vectors` (backlog #75,
MANIFEST-1) of jascon/conformance/attestation-vectors.json. Re-running it
changes nothing.

    python3 drafts/phase-d/author_binds_vectors.py

`attestation-binds` (Appendix B.1.7) is (attestation, bundle) -> Full Match
| Semantic Match | fail. The five vectors the family had exercise the two
digests of ONE object. These exercise the primitive as it is applied to a
bundle: which manifest the Attestation binds, and what became of each
subject. A vector gives the digest of the delivered manifest (it has no
manifest bytes), the digests of the pack manifests the bundle keeps, the
bundle's objects and the Attestation; it expects the verdict, which
manifest is bound, and the status of every subject in order.

The semantic digests are computed here with the reference's own `sdig`,
so a vector cannot carry a digest that no implementation would compute.
The expectations are written by hand, below, before any implementation
ran against them."""
import copy, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
VALIDATOR = os.path.join(ROOT, "jascon", "scripts", "validate_core.py")
src = open(VALIDATOR, encoding="utf-8").read()
ns = {"__file__": VALIDATOR, "__name__": "validate_core_defs"}
exec(compile(src.split("# ---------------- run ----------------")[0], VALIDATOR, "exec"), ns)
sdig = ns["sdig"]

P = "https://agency-x.example"
REQ = {"id": f"{P}/req/1", "version": "1", "lifecycle": "active",
       "statements": [{"id": "s1", "modality": "must", "obligated-parties": [f"{P}/party/operator"], "prose": {"en": "Keys are rotated every 90 days."}}]}
COMP = {"id": f"{P}/component/app", "version": "1", "lifecycle": "active", "kind": "system", "title": {"en": "The application"},
        "capabilities": [{"id": "cap-rotation", "requirement-ref": REQ["id"]}]}
IMPL = {"id": f"{P}/impl/app--req-1", "version": "1", "lifecycle": "active", "component-ref": COMP["id"], "requirement-ref": REQ["id"],
        "responsibility": "provider", "satisfied-by": [{"capability-ref": "cap-rotation"}], "status": "implemented"}
# every object of a vector is one the kernel types: an object no implementation can type is no object of a bundle
for _o in (REQ, COMP, IMPL): assert ns["inferType_single"](_o), _o["id"]
MANIFEST = "sha256:" + "a" * 64          # the digest of the manifest as delivered
OTHER = "sha256:" + "b" * 64             # the digest of some other manifest
PACK = "sha256:" + "c" * 64              # the digest of a pack manifest the bundle keeps

def att(subjects, manifest=MANIFEST):
    return {"id": f"{P}/attestation/ato", "version": "1", "lifecycle": "active",
            "subject-semantic-digests": subjects, "content-manifest-digest": manifest,
            "signer": f"{P}/party/ao", "timestamp": "2026-11-14T09:00:00Z"}
def named(o): return {"id": o["id"], "semantic-digest": sdig(o)}

eased = copy.deepcopy(REQ); eased["statements"][0]["modality"] = "should"
annotated = copy.deepcopy(REQ); annotated["annotations"] = {"web_name": "key-rotation"}
V = []
def vec(name, objects, attestation, verdict, manifest, subjects, note, kept=None, fails=None):
    v = {"name": name, "note": note, "manifest-digest": MANIFEST}
    if kept: v["kept-packs"] = kept
    # the bundle fails when the verdict is `fail` and the Attestation is still claimed (lifecycle active)
    v.update({"objects": objects, "attestation": attestation,
              "expected": verdict, "expected-manifest": manifest, "expected-subjects": subjects,
              "expected-failure": (verdict == "fail") if fails is None else fails})
    V.append(v)
def in_state(a, lifecycle):
    a = copy.deepcopy(a); a["lifecycle"] = lifecycle; return a

ALL = [REQ, COMP, IMPL]
vec("full-match-named-subjects", ALL, att([named(REQ), named(COMP), named(IMPL)]),
    "full-match", "this", ["match", "match", "match"],
    "Every subject is an object of the bundle with the signed digest, and the Attestation binds the manifest as delivered.")
vec("full-match-bare-digests", ALL, att([sdig(REQ), sdig(IMPL)]),
    "full-match", "this", ["match", "match"],
    "A subject given as a bare digest matches when an object of the bundle carries that semantic digest.")
vec("full-match-one-of-several-objects", ALL, att([named(COMP)]),
    "full-match", "this", ["match"],
    "An Attestation need not name every object of the bundle; every subject it names is delivered and matches.")
vec("semantic-match-another-manifest", ALL, att([named(REQ), named(COMP)], OTHER),
    "semantic-match", "other", ["match", "match"],
    "The subjects match and the manifest is another one: the content is proven, the packaging was altered. Reported, never a failure and never Full (D7).")
vec("semantic-digest-ignores-annotations", [annotated, COMP, IMPL], att([named(REQ)]),
    "full-match", "this", ["match"],
    "The delivered Requirement gained an annotation after signing. Annotations are outside the semantic digest, so the subject still matches.")
vec("fail-a-subject-was-changed", [eased, COMP, IMPL], att([named(REQ), named(COMP)]),
    "fail", "this", ["differs", "match"],
    "The delivered Requirement says `should` where the signed one said `must`: normative content changed after signing. One subject that differs fails the Attestation, whatever the others do.")
vec("fail-a-subject-was-changed-under-another-manifest", [eased, COMP, IMPL], att([named(REQ), named(COMP)], OTHER),
    "fail", "other", ["differs", "match"],
    "A changed subject is no Semantic Match: Semantic Match needs every subject to match.")
vec("fail-a-named-subject-is-not-delivered", [COMP, IMPL], att([named(REQ), named(COMP)]),
    "fail", "this", ["absent", "match"],
    "The Attestation names a Requirement the bundle does not hold. What is not delivered cannot be recomputed, so the Attestation does not bind what is delivered.")
vec("fail-a-bare-digest-no-object-carries", ALL, att([sdig(eased)]),
    "fail", "this", ["absent"],
    "A bare digest that no object of the bundle carries names nothing here. This is what the example folder's Attestation did from before 1.0.0 until 2026-11-14 (backlog #46).")
vec("fail-binds-nothing-here", ALL, att([sdig(eased), "sha256:" + "0" * 64], OTHER),
    "fail", "other", ["absent", "absent"],
    "Another manifest and no subject of this bundle: an Attestation that lies beside a manifest and binds nothing of it.")
vec("a-named-subject-is-looked-up-by-its-id", ALL, att([{"id": COMP["id"], "semantic-digest": sdig(REQ)}]),
    "fail", "this", ["differs"],
    "The digest is the Requirement's, the id is the Component's. A named subject is compared with the object of that id, not with any object that happens to carry the digest.")
vec("the-attestation-is-no-subject-of-itself", ALL + [att([named(REQ)])], att([named(REQ)]),
    "full-match", "this", ["match"],
    "An Attestation that a manifest lists (which D3.1 excludes) is still held to its subjects; listing it changes nothing about them.")
vec("full-match-the-kept-pack-manifest", ALL, att([named(COMP)], PACK),
    "full-match", "kept-pack", ["match"],
    "A vendor's Attestation binds the vendor's manifest, which the bundle keeps under packs/sha256/ (D25). That is the manifest as the vendor delivered it.",
    kept=[PACK])
vec("a-pack-manifest-the-bundle-does-not-keep-is-another-manifest", ALL, att([named(COMP)], PACK),
    "semantic-match", "other", ["match"],
    "The same Attestation where the bundle keeps no such manifest: nothing here shows what it binds.")
vec("the-same-subject-twice", ALL, att([named(REQ), sdig(REQ)]),
    "full-match", "this", ["match", "match"],
    "A subject named once by id and once by its bare digest is judged twice and matches twice.")

# The file's five older vectors are written by hand, several members to a
# line. They are kept byte for byte: this script edits the text - it adds a
# sentence to the description and replaces the `binds-vectors` member - and
# then checks that the result parses to what it meant to write.
# An Attestation that is no longer claimed, or not yet, fails no bundle: the verdict stands and is reported.
changed = att([named(REQ), named(COMP)])
vec("a-withdrawn-attestation-that-no-longer-binds-fails-no-bundle", [eased, COMP, IMPL], in_state(changed, "withdrawn"),
    "fail", "this", ["differs", "match"],
    "The Requirement changed after signing and the Attestation was withdrawn. The verdict is still `fail`, and it is reported; the bundle does not fail, "
    "because nobody claims the Attestation any more. This is how an attested object is changed without leaving a bundle that cannot validate: change it, "
    "and withdraw or re-issue the Attestation.", fails=False)
vec("a-deprecated-attestation-that-no-longer-binds-fails-no-bundle", [eased, COMP, IMPL], in_state(changed, "deprecated"),
    "fail", "this", ["differs", "match"], "As for `withdrawn`: deprecated is on its way out.", fails=False)
vec("a-draft-attestation-that-does-not-bind-yet-fails-no-bundle", [COMP, IMPL], in_state(changed, "draft"),
    "fail", "this", ["absent", "match"], "A draft is not issued; what it will bind may not be there yet.", fails=False)
vec("a-withdrawn-attestation-that-still-binds-is-a-full-match", ALL, in_state(att([named(REQ)]), "withdrawn"),
    "full-match", "this", ["match"], "The lifecycle changes what a failing verdict does, never the verdict.")

# ---- listed-vectors (backlog #75; author, 2026-11-14: "refusal in all") ----
# D3.1: "Attestations and signature envelopes are excluded from the content
# manifest by definition". MANIFEST-1 makes that a rule of every bundle: an
# object the manifest lists is no Attestation. A vector gives the objects a
# manifest lists and expects one failure per Attestation among them, each
# naming the rule and the Attestation's id. What the Attestation binds, whether
# it is signed and whether it is still claimed change nothing: the rule is
# about where it lies. The expectations were written before the rule was.
L = []
def listed(name, objects, ids, note):
    L.append({"name": name, "note": note, "objects": objects, "expected-fails": len(ids), "expected-ids": ids})
ATT = att([named(REQ), named(COMP), named(IMPL)])
ATT2 = dict(att([named(REQ)], OTHER), id=f"{P}/attestation/review-2026")
SIGNED = dict(ATT, **{"envelope-ref": "attestation-ato.dsse"})
NOT_ONE = dict(copy.deepcopy(COMP), id=f"{P}/attestation/not-one")       # a Component whose id says "attestation"
for _o in (ATT, ATT2, SIGNED): assert ns["inferType_single"](_o) == "attestation", _o["id"]
assert ns["inferType_single"](NOT_ONE) == "component"
listed("no-attestation-listed", ALL, [],
       "A manifest that lists a Requirement, a Component and an Implementation lists no Attestation.")
listed("an-attestation-listed-among-its-subjects", ALL + [ATT], [ATT["id"]],
       "The Attestation's three subjects are listed beside it and carry the signed digests. It is refused all the same: "
       "a manifest that lists an Attestation cannot be the manifest that Attestation binds.")
listed("two-attestations-listed", [REQ, ATT2, ATT], [ATT["id"], ATT2["id"]],
       "One failure for each, named in the order of their ids.")
listed("a-withdrawn-attestation-listed", ALL + [in_state(ATT, "withdrawn")], [ATT["id"]],
       "The lifecycle decides whether an Attestation that does not bind fails a bundle (D7). It does not decide where an Attestation lies.")
listed("a-draft-attestation-listed", ALL + [in_state(ATT, "draft")], [ATT["id"]],
       "A draft is an Attestation too.")
listed("a-signed-attestation-listed", ALL + [SIGNED], [ATT["id"]],
       "With an envelope or without one.")
listed("nothing-but-an-attestation-listed", [ATT2], [ATT2["id"]],
       "Its subjects need not be there for the rule to speak.")
listed("an-id-that-says-attestation-is-no-attestation", ALL + [NOT_ONE], [],
       "The type decides, not the id and not a path: a Component under .../attestation/... is a Component.")

path = os.path.join(ROOT, "jascon", "conformance", "attestation-vectors.json")
raw = open(path, encoding="utf-8").read()
ADD = (" binds-vectors (backlog #46, 2026-11-14): the primitive applied to a bundle, as a validator applies it to every Attestation it reads with one - "
       "those beside the manifest (D3.1) and any a manifest lists. `manifest-digest` is the digest of the delivered manifest, `kept-packs` the digests of "
       "the pack manifests the bundle keeps. Each subject is `match` (an object of the bundle carries the signed semantic digest: the object of that id "
       "when the subject names one, any object when it is a bare digest), `differs` (the object of that id carries another digest) or `absent` (no such "
       "object, or no object with that digest). `expected-manifest` is `this`, `kept-pack` or `other`. All subjects match and the manifest is this one "
       "or a kept pack's = full-match; all match and the manifest is another = semantic-match; anything else = fail. `expected-failure` says whether "
       "the bundle fails: it does when the verdict is `fail` and the Attestation's lifecycle is `active` - a draft, deprecated or withdrawn Attestation "
       "that does not bind is reported and fails nothing. An implementation is held to the verdict, to which manifest is bound, to the status of every "
       "subject in order, and to whether the bundle fails."
       " listed-vectors (backlog #75, 2026-11-14; MANIFEST-1): `objects` are the objects a content manifest lists. An Attestation is excluded from "
       "the content manifest by definition (D3.1), in every bundle and not only in a pack: `expected-fails` is the number of Attestations among the "
       "objects, and each failure names the rule and one of `expected-ids`. What the Attestation binds, whether it names an envelope and what its "
       "lifecycle is change nothing.")
MARK = ',\n  "binds-vectors": '
if MARK in raw: raw = raw[:raw.index(MARK)] + "\n}\n"            # written by an earlier run: replaced below
old = json.loads(raw)
end = '",\n  "vectors": ['
assert raw.count(end) == 1
head = old["description"].split(" binds-vectors (backlog #46")[0]      # the description as it was before this script
a = raw.index('"description": "') + len('"description": "')
raw = raw[:a] + json.dumps(head + ADD, ensure_ascii=False)[1:-1] + raw[raw.index(end):]
assert raw.rstrip().endswith("}")
body = json.dumps(V, indent=1, ensure_ascii=False).replace("\n", "\n  ")
body2 = json.dumps(L, indent=1, ensure_ascii=False).replace("\n", "\n  ")
raw = raw.rstrip()[:-1].rstrip() + MARK + body + ',\n  "listed-vectors": ' + body2 + "\n}\n"
doc = json.loads(raw)
assert doc["vectors"] == old["vectors"] and doc["binds-vectors"] == V and doc["listed-vectors"] == L and doc["description"].endswith(ADD)
with open(path, "w", encoding="utf-8", newline="\n") as f: f.write(raw)
print(f"attestation-vectors.json: {len(doc['vectors'])} vectors, {len(V)} binds-vectors, {len(L)} listed-vectors")
