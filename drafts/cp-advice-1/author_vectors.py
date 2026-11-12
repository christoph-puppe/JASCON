#!/usr/bin/env python3
"""Writes jascon/conformance/advice-vectors.json (CP-ADVICE-1).

    uv run --with jsonschema python drafts/cp-advice-1/author_vectors.py

The vectors are literal JSON once written; this script exists so that the
two kinds of literal that cannot be typed by hand - the digest a vendor's
Attestation binds and the Ed25519 signature over it - are computed by the
reference validator's own functions and never go stale unnoticed. Semantic
digests of listed objects are NOT literals: a vector writes "COMPUTE" and
the harness fills them from the objects as published (run_advice).

The fixture key is the one of dsse-vectors.json: seed =
sha256('jascon dsse fixture key 1')."""
import base64, copy, hashlib, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
VALIDATOR = os.path.join(ROOT, "jascon", "scripts", "validate_core.py")
OUT = os.path.join(ROOT, "jascon", "conformance", "advice-vectors.json")

# the validator's definitions, without its run
src = open(VALIDATOR, encoding="utf-8").read()
ns = {"__file__": VALIDATOR, "__name__": "validate_core_defs"}
exec(compile(src.split("# ---------------- run ----------------")[0], VALIDATOR, "exec"), ns)
canonical, sdig, fill = ns["canonical"], ns["sdig"], ns["_advice_fill"]

AUTH, VEN, ORG = "https://ns.auth.gov/fw", "https://vendor.example", "https://org.example"
Z = "sha256:" + "0" * 64

def clone(o, **changes):
    o = copy.deepcopy(o)
    for k, v in changes.items():
        k = k.replace("_", "-")
        if v is None: o.pop(k, None)
        else: o[k] = v
    return o

REQ = {"id": AUTH + "/req/1", "version": "1", "lifecycle": "active", "statements": [
    {"id": "s1", "modality": "must", "obligated-parties": [AUTH + "/p/operator"],
     "parameters": [{"name": "proto", "type": "choice", "cardinality": "one",
                     "choices": [{"value": "tls13", "label": {"en": "TLS 1.3"}},
                                 {"value": "tls12", "label": {"en": "TLS 1.2"}}]},
                    {"name": "max-tries", "type": "integer", "min": 1, "max": 10, "tightening": "lower"}],
     "prose": {"en": "Traffic is encrypted with {param:proto}; at most {param:max-tries} attempts."}},
    {"id": "s2", "modality": "should", "obligated-parties": [AUTH + "/p/operator"],
     "prose": {"en": "Keys are rotated."}}]}

CAP_TLS = {"id": "cap-tls", "requirement-ref": REQ["id"], "statement-ids": ["s1"],
           "description": {"en": "Set net.tls.mode to requireTLS and disable every protocol below TLS 1.3."},
           "parameter-bindings": {"proto": "tls13"}}
CAP_ROT = {"id": "cap-rotate", "requirement-ref": REQ["id"], "statement-ids": ["s2"],
           "description": {"en": "Rotate the server certificate with rotateCertificates; no restart is needed."}}
VC = {"id": VEN + "/component/server-7", "version": "3", "lifecycle": "active", "kind": "software",
      "title": {"en": "Example Server 7"}, "capabilities": [CAP_TLS, CAP_ROT]}
UC0 = {"id": ORG + "/component/app", "version": "1", "lifecycle": "active", "kind": "system"}
UC = clone(UC0, members=[{"component-ref": VC["id"], "context": "datastore"}])
UI = {"id": ORG + "/impl/app-req-1", "version": "1", "lifecycle": "active",
      "component-ref": UC["id"], "requirement-ref": REQ["id"], "statement-refs": ["s1"],
      "responsibility": "customer", "satisfied-by": [{"capability-ref": VC["id"] + "#cap-tls"}],
      "status": "planned"}
PACK = {"kind": "advice", "id": VEN + "/pack/server-7-advice", "version": "3",
        "title": {"en": "Server 7 hardening advice"},
        "publisher": {"ref": VEN + "/party/vendor", "name": {"en": "Vendor Inc."}}}
def manifest(objects, pack=PACK, kernel="2.0.0"):
    m = {"manifest-version": "1"}
    if kernel: m["kernel-version"] = kernel
    if pack: m["pack"] = pack
    m["objects"] = [{"id": o["id"], "semantic-digest": "COMPUTE"} for o in objects]
    return m
PM = manifest([VC])
TAIL = {"id": VEN + "/tailoring/t", "version": "1", "lifecycle": "active",
        "selects": [{"set-ref": AUTH + "/set/base"}]}
ATT = {"id": VEN + "/attestation/server-7-advice-3", "version": "1", "lifecycle": "active",
       "subject-semantic-digests": [sdig(VC)], "content-manifest-digest": Z,
       "signer": VEN + "/party/vendor", "timestamp": "2026-11-12T12:00:00Z"}

# ---------- shapes ----------
shape = [
    {"name": "manifest-with-pack-header", "kind": "manifest", "expected": "valid",
     "document": fill(PM, [VC])},
    {"name": "manifest-without-pack-header-stays-valid", "kind": "manifest", "expected": "valid",
     "note": "a 1.0.0 manifest is a 2.0.0 manifest; a manifest without the header is not a pack",
     "document": {"manifest-version": "1", "objects": []}},
    {"name": "pack-without-publisher", "kind": "manifest", "expected": "invalid",
     "document": fill(manifest([VC], clone(PACK, publisher=None)), [VC])},
    {"name": "pack-publisher-without-ref", "kind": "manifest", "expected": "invalid",
     "document": fill(manifest([VC], clone(PACK, publisher={"name": {"en": "Vendor Inc."}})), [VC])},
    {"name": "pack-without-version", "kind": "manifest", "expected": "invalid",
     "document": fill(manifest([VC], clone(PACK, version=None)), [VC])},
    {"name": "pack-kind-outside-the-code-system", "kind": "manifest", "expected": "invalid",
     "note": "the kinds are a closed set of one; a check pack would be a new code, by process",
     "document": fill(manifest([VC], clone(PACK, kind="checks")), [VC])},
    {"name": "pack-header-is-closed", "kind": "manifest", "expected": "invalid",
     "document": fill(manifest([VC], clone(PACK, licence="CC-BY-4.0")), [VC])},
    {"name": "capability-with-statement-ids", "kind": "component", "expected": "valid", "document": VC},
    {"name": "capability-statement-ids-empty", "kind": "component", "expected": "invalid",
     "note": "an optional array is present with content or absent (D3.3)",
     "document": clone(VC, capabilities=[clone(CAP_TLS, statement_ids=[])])},
]

# ---------- a third party's advice about a vendor's product (author decision 2026-11-12) ----------
ADV = "https://advisor.example"
DESCRIBES = "https://ns.jascon.net/stdlib/relation/describes"
TPC = {"id": ADV + "/component/server-7-hardening", "version": "1", "lifecycle": "active", "kind": "software",
       "title": {"en": "Hardening advice for Example Server 7"}, "product-version": "7",
       "relations": [{"type": DESCRIBES, "ref": VC["id"]}],
       "capabilities": [clone(CAP_TLS, description={"en": "Disable every protocol below TLS 1.3, and test client drivers first."})]}
TPPACK = {"kind": "advice", "id": ADV + "/pack/server-7-hardening", "version": "1",
          "title": {"en": "Independent hardening advice for Example Server 7"},
          "publisher": {"ref": ADV + "/party/advisor", "name": {"en": "Advisor GmbH"}}}

# ---------- what a pack may hold (ADVICE-1..3, KERNEL-1) ----------
FACET = VEN + "/facet/sizing"
ASSESS = next(k for k, v in sorted(ns["STDLIB_DECL"].items()) if v)
pack = [
    {"name": "lawful-pack", "manifest": PM, "objects": [VC], "expected-rules": []},
    {"name": "pack-with-a-tailoring", "manifest": manifest([VC, TAIL]), "objects": [VC, TAIL],
     "expected-rules": ["ADVICE-1"], "expected-frags": ["is a tailoring"]},
    {"name": "pack-with-a-requirement-of-its-own", "note": "authorship under the vendor's own prefix is lawful (Ch. 6.A) - in a bundle, not in an advice pack",
     "manifest": manifest([VC, clone(REQ, id=VEN + "/req/1")]), "objects": [VC, clone(REQ, id=VEN + "/req/1")],
     "expected-rules": ["ADVICE-1"], "expected-frags": ["is a requirement"]},
    {"name": "pack-lists-its-attestation", "manifest": manifest([VC, ATT]), "objects": [VC, ATT],
     "expected-rules": ["ADVICE-1"], "expected-frags": ["beside the manifest"]},
    {"name": "object-under-a-foreign-origin", "manifest": manifest([clone(VC, id=AUTH + "/component/server-7")]),
     "objects": [clone(VC, id=AUTH + "/component/server-7")],
     "expected-rules": ["ADVICE-2"], "expected-frags": ["is not under the pack's origin"]},
    {"name": "publisher-under-a-foreign-origin",
     "manifest": manifest([VC], clone(PACK, publisher={"ref": "https://reseller.example/party/r"})), "objects": [VC],
     "expected-rules": ["ADVICE-2"], "expected-frags": ["publisher"]},
    {"name": "facet-that-declares-a-semantics-class", "declared": {FACET: ["assessment"]},
     "manifest": manifest([clone(VC, facets={FACET + "@1": {"cores": 8}})]),
     "objects": [clone(VC, facets={FACET + "@1": {"cores": 8}})],
     "expected-rules": ["ADVICE-3"], "expected-frags": ["modifies-semantics ['assessment']"]},
    {"name": "stdlib-facet-that-declares-a-semantics-class",
     "manifest": manifest([clone(VC, facets={ASSESS + "@1": {}})]), "objects": [clone(VC, facets={ASSESS + "@1": {}})],
     "expected-rules": ["ADVICE-3"]},
    {"name": "facet-that-declares-nothing", "declared": {FACET: []},
     "manifest": manifest([clone(VC, facets={FACET + "@1": {"cores": 8}})]),
     "objects": [clone(VC, facets={FACET + "@1": {"cores": 8}})], "expected-rules": []},
    {"name": "private-payload-rides", "manifest": manifest([clone(VC, facets={"private:vendor/sku@1": {"sku": "S7"}})]),
     "objects": [clone(VC, facets={"private:vendor/sku@1": {"sku": "S7"}})], "expected-rules": []},
    {"name": "pack-names-the-product-version", "note": "product-version is opaque text on a Component; nothing is ordered or parsed (author decision 2026-11-12)",
     "manifest": manifest([clone(VC, product_version="7.2")]), "objects": [clone(VC, product_version="7.2")], "expected-rules": []},
    {"name": "third-party-pack-describes-the-vendors-product",
     "note": "a consultancy publishes its own Component under its own origin (ADVICE-2) and says which product it is about with the stdlib relation `describes`; the vendor's Component need not be in the pack",
     "manifest": manifest([TPC], TPPACK), "objects": [TPC], "expected-rules": []},
    {"name": "third-party-pack-under-the-vendors-id", "note": "what `describes` is for: advice about a product is never published under the product's own id",
     "manifest": manifest([VC], TPPACK), "objects": [VC],
     "expected-rules": ["ADVICE-2"], "expected-frags": ["is not under the pack's origin"]},
    {"name": "pack-without-a-kernel-pin", "manifest": manifest([VC], kernel=None), "objects": [VC],
     "expected-rules": ["KERNEL-1"], "expected-frags": ["pack header"]},
    {"name": "pack-pinned-to-1.0.0", "manifest": manifest([VC], kernel="1.0.0"), "objects": [VC],
     "expected-rules": ["KERNEL-1"]},
]

# ---------- capabilities and the edges that cite them (ADVICE-4..7) ----------
OWN = clone(UC0, capabilities=[{"id": "cap-own", "description": {"en": "Own TLS termination."},
                                "parameter-bindings": {"proto": "tls13"}}])
def impl(ref, comp=UC["id"]):
    return clone(UI, component_ref=comp, satisfied_by=[{"capability-ref": ref}])
graph = [
    {"name": "adopted-advice", "note": "the user's edge, on the user's component, cites the vendor's capability; the product is a member",
     "objects": [REQ, VC, UC, UI], "expected-rules": []},
    {"name": "capability-id-twice", "objects": [REQ, clone(VC, capabilities=[CAP_TLS, clone(CAP_ROT, id="cap-tls")])],
     "expected-rules": ["ADVICE-4"], "expected-frags": ["'cap-tls' is used twice"]},
    {"name": "statement-id-names-no-clause", "objects": [REQ, clone(VC, capabilities=[clone(CAP_ROT, statement_ids=["s9"])])],
     "expected-rules": ["ADVICE-5"], "expected-frags": ["'s9' names no statement"]},
    {"name": "statement-ids-without-requirement", "objects": [REQ, clone(VC, capabilities=[clone(CAP_ROT, requirement_ref=None)])],
     "expected-rules": ["ADVICE-5"], "expected-frags": ["without a requirement-ref"]},
    {"name": "requirement-ref-resolves-to-a-component",
     "objects": [UC0, clone(VC, capabilities=[clone(CAP_ROT, requirement_ref=UC0["id"], statement_ids=None)])],
     "expected-rules": ["ADVICE-5"], "expected-frags": ["not a Requirement"]},
    {"name": "requirement-outside-the-bundle", "note": "resolves-if-present: a pack ships without the catalog",
     "objects": [VC], "expected-rules": [], "expected-notes": ["2 capability requirement-ref(s) outside the bundle"]},
    {"name": "binding-names-no-parameter", "objects": [REQ, clone(VC, capabilities=[clone(CAP_TLS, parameter_bindings={"cipher": "aes"})])],
     "expected-rules": ["ADVICE-6"], "expected-frags": ["declared 0 times"]},
    {"name": "binding-outside-the-declared-choices", "objects": [REQ, clone(VC, capabilities=[clone(CAP_TLS, parameter_bindings={"proto": "tls11"})])],
     "expected-rules": ["ADVICE-6"], "expected-frags": ["outside the declared space"]},
    {"name": "binding-above-the-declared-maximum", "objects": [REQ, clone(VC, capabilities=[clone(CAP_TLS, parameter_bindings={"max-tries": 11})])],
     "expected-rules": ["ADVICE-6"], "expected-frags": ["outside the declared space"]},
    {"name": "binding-of-the-wrong-kind", "objects": [REQ, clone(VC, capabilities=[clone(CAP_TLS, parameter_bindings={"max-tries": "four"})])],
     "expected-rules": ["ADVICE-6"], "expected-frags": ["of the wrong kind"]},
    {"name": "binding-on-a-clause-not-covered", "note": "proto is declared on s1; the capability covers s2",
     "objects": [REQ, clone(VC, capabilities=[clone(CAP_ROT, parameter_bindings={"proto": "tls13"})])],
     "expected-rules": ["ADVICE-6"], "expected-frags": ["declared 0 times"]},
    {"name": "binding-without-statement-ids-covers-every-clause",
     "objects": [REQ, clone(VC, capabilities=[clone(CAP_TLS, statement_ids=None)])], "expected-rules": []},
    {"name": "binding-without-requirement-ref", "note": "nothing to check it against: a 1.0.0 capability stays valid",
     "objects": [OWN], "expected-rules": []},
    {"name": "bare-id-of-the-own-component", "objects": [REQ, OWN, impl("cap-own")], "expected-rules": []},
    {"name": "bare-id-nobody-declared", "note": "the literal a tool wrote when it had nothing to cite",
     "objects": [REQ, OWN, impl("declared")], "expected-rules": ["ADVICE-7"], "expected-frags": ["does not declare"]},
    {"name": "full-form-to-the-own-component", "objects": [REQ, OWN, impl(OWN["id"] + "#cap-own")], "expected-rules": []},
    {"name": "cited-component-not-in-the-bundle", "note": "closure-required: advice that was not imported cannot be adopted",
     "objects": [REQ, UC, UI], "expected-rules": ["ADVICE-7"], "expected-frags": ["is not in the bundle"]},
    {"name": "cited-component-is-not-a-member", "objects": [REQ, VC, UC0, UI],
     "expected-rules": ["ADVICE-7"], "expected-frags": ["is not a member of"]},
    {"name": "cited-capability-not-declared", "objects": [REQ, VC, UC, impl(VC["id"] + "#cap-gone")],
     "expected-rules": ["ADVICE-7"], "expected-frags": ["'cap-gone', which"]},
    {"name": "cited-thing-is-not-a-component", "objects": [REQ, VC, UC, impl(REQ["id"] + "#s1")],
     "expected-rules": ["ADVICE-7"], "expected-frags": ["not a Component"]},
    {"name": "inherited-edge-is-not-a-capability-ref",
     "objects": [REQ, VC, UC, clone(UI, satisfied_by=[{"inherited-from": {"component-ref": VC["id"], "basis-ref": VEN + "/auth/x"}}])],
     "expected-rules": []},
]

# ---------- the manifest a set keeps (ADVICE-8..10) ----------
VC_EDITED = clone(VC, capabilities=[clone(CAP_TLS, description={"en": "Set net.tls.mode to preferTLS."}), CAP_ROT])
PACK2 = clone(PACK, id=VEN + "/pack/server-7-extras", version="1")
kept = [
    {"name": "kept-manifest-matches-the-set", "objects": [VC, UC], "kept": [{"manifest": PM, "published": [VC]}],
     "expected-rules": [], "expected-packs": 1},
    {"name": "name-is-not-the-digest", "objects": [VC], "kept": [{"name": "0" * 64, "manifest": PM, "published": [VC]}],
     "expected-rules": ["ADVICE-8"], "expected-frags": ["does not match its name"], "expected-packs": 0},
    {"name": "kept-file-is-not-json", "objects": [VC], "kept": [{"raw": "not json"}],
     "expected-rules": ["ADVICE-8"], "expected-frags": ["not readable JSON"], "expected-packs": 0},
    {"name": "kept-file-is-not-a-manifest", "objects": [VC], "kept": [{"raw": "{\"hello\":1}"}],
     "expected-rules": ["ADVICE-8"], "expected-frags": ["not a content manifest with a pack header"], "expected-packs": 0},
    {"name": "kept-manifest-without-pack-header", "objects": [VC], "kept": [{"manifest": manifest([VC], pack=None), "published": [VC]}],
     "expected-rules": ["ADVICE-8"], "expected-packs": 0},
    {"name": "kept-manifest-listed-in-the-bundle-manifest", "objects": [VC],
     "manifest": {"manifest-version": "1", "objects": [{"id": VC["id"], "path": "packs/sha256/" + "a" * 64}]},
     "kept": [{"manifest": PM, "published": [VC]}],
     "expected-rules": ["ADVICE-8"], "expected-frags": ["is listed in the bundle's manifest"], "expected-packs": 1},
    {"name": "listed-object-not-in-the-set", "objects": [UC], "kept": [{"manifest": PM, "published": [VC]}],
     "expected-rules": ["ADVICE-9"], "expected-frags": ["is not in the bundle"]},
    {"name": "advice-edited-after-import", "objects": [VC_EDITED, UC], "kept": [{"manifest": PM, "published": [VC]}],
     "expected-rules": ["ADVICE-9"], "expected-frags": ["edited after import"]},
    {"name": "object-at-another-version", "objects": [clone(VC, version="4"), UC], "kept": [{"manifest": PM, "published": [VC]}],
     "expected-rules": ["ADVICE-9"], "expected-frags": ["is at version 4"]},
    {"name": "two-releases-of-one-pack", "objects": [VC, UC],
     "kept": [{"manifest": PM, "published": [VC]}, {"manifest": manifest([VC], clone(PACK, version="4")), "published": [VC]}],
     "expected-rules": ["ADVICE-10"], "expected-frags": ["are both in the bundle"]},
    {"name": "one-object-in-two-packs", "objects": [VC, UC],
     "kept": [{"manifest": PM, "published": [VC]}, {"manifest": manifest([VC], PACK2), "published": [VC]}],
     "expected-rules": ["ADVICE-10"], "expected-frags": ["is listed by two kept manifests"]},
]

# ---------- claimed and proven ----------
seed = hashlib.sha256(b"jascon dsse fixture key 1").digest()
pub = ns["ed25519_public"](seed).hex()
dsse = json.load(open(os.path.join(ROOT, "jascon", "conformance", "dsse-vectors.json"), encoding="utf-8"))
assert pub == dsse["fixture-public-key"], "fixture key drifted"
mdig = "sha256:" + hashlib.sha256(canonical(fill(PM, [VC])).encode("utf-8")).hexdigest()
def envelope(att, tamper=False):
    payload = canonical(att).encode("utf-8")
    ptype = ns["DSSE_PAYLOAD_TYPE"]
    sig = ns["ed25519_sign"](seed, ns["_pae"](ptype.encode(), payload))
    if tamper: sig = bytes([sig[0] ^ 1]) + sig[1:]
    return {"payloadType": ptype, "payload": base64.b64encode(payload).decode(),
            "signatures": [{"keyid": att["signer"], "sig": base64.b64encode(sig).decode()}]}
BOUND = clone(ATT, content_manifest_digest=mdig)
SIGNED = clone(BOUND, envelope_ref="env-1")
KEY = {SIGNED["signer"]: pub}
publisher = [
    {"name": "no-attestation", "manifest": PM, "published": [VC], "objects": [], "expected": "claimed"},
    {"name": "attestation-binds-the-manifest", "note": "structural mode: no trusted keys, the digest match proves - as for a Tailoring's tier",
     "manifest": PM, "published": [VC], "objects": [BOUND], "expected": "proven"},
    {"name": "attestation-of-a-foreign-signer", "manifest": PM, "published": [VC],
     "objects": [clone(BOUND, signer="https://reseller.example/party/r")], "expected": "claimed"},
    {"name": "attestation-binds-another-manifest", "manifest": PM, "published": [VC], "objects": [ATT], "expected": "claimed"},
    {"name": "verification-mode-unsigned", "note": "with trusted keys an unsigned attestation no longer proves",
     "manifest": PM, "published": [VC], "objects": [BOUND], "trusted-keys": KEY, "expected": "claimed"},
    {"name": "verification-mode-signed", "manifest": PM, "published": [VC], "objects": [SIGNED],
     "envelopes": {"env-1": envelope(SIGNED)}, "trusted-keys": KEY, "expected": "proven"},
    {"name": "verification-mode-no-key-for-the-signer", "manifest": PM, "published": [VC], "objects": [SIGNED],
     "envelopes": {"env-1": envelope(SIGNED)}, "trusted-keys": {"https://other.example/party/x": pub}, "expected": "claimed"},
    {"name": "verification-mode-signature-does-not-verify", "manifest": PM, "published": [VC], "objects": [SIGNED],
     "envelopes": {"env-1": envelope(SIGNED, tamper=True)}, "trusted-keys": KEY, "expected": "claimed"},
]

# ---------- import (ADVICE-11) ----------
VC4 = clone(VC, version="4", capabilities=[
    clone(CAP_TLS, description={"en": "Set net.tls.mode to requireTLS; TLS 1.2 is off by default from 7.2."}), CAP_ROT,
    {"id": "cap-audit", "description": {"en": "Turn on the audit log."}}])
VC4_DROPPED = clone(VC, version="4", capabilities=[CAP_ROT])
PM4 = manifest([VC4], clone(PACK, version="4"))
VC6 = clone(VC, id=VEN + "/component/server-6", title={"en": "Example Server 6"})
UC6 = clone(UC0, members=[{"component-ref": VC["id"]}, {"component-ref": VC6["id"]}])
UI6 = clone(UI, id=ORG + "/impl/app-req-1-legacy", component_ref=UC6["id"],
            satisfied_by=[{"capability-ref": VC6["id"] + "#cap-rotate"}], statement_refs=["s2"])
imp = [
    {"name": "first-import", "a": {"objects": [REQ, UC0]}, "b": {"manifest": PM, "objects": [VC]},
     "expected": {"result": "import", "added": [VC["id"]], "replaced": [], "removed": [], "dangling": [], "unchanged": 2},
     "expected-rules": []},
    {"name": "the-same-file-again", "note": "the kept manifest has the digest of the file: nothing is written",
     "a": {"objects": [REQ, UC, VC, UI], "kept": [{"manifest": PM, "published": [VC]}]}, "b": {"manifest": PM, "objects": [VC]},
     "expected": {"result": "already-imported", "added": [], "replaced": [], "removed": [], "unchanged": 4},
     "expected-rules": []},
    {"name": "another-release-replaces", "note": "the one lawful replacement: the ids an earlier release of the same pack brought",
     "a": {"objects": [REQ, UC, VC, UI], "kept": [{"manifest": PM, "published": [VC]}]},
     "b": {"manifest": PM4, "objects": [VC4]},
     "expected": {"result": "replace", "added": [], "replaced": [VC["id"]], "removed": [], "dangling": [], "unchanged": 3},
     "expected-rules": []},
    {"name": "release-drops-an-adopted-capability", "note": "not refused: reported before anything is written; ADVICE-7 then holds the edge",
     "a": {"objects": [REQ, UC, VC, UI], "kept": [{"manifest": PM, "published": [VC]}]},
     "b": {"manifest": manifest([VC4_DROPPED], clone(PACK, version="4")), "objects": [VC4_DROPPED]},
     "expected": {"result": "replace", "replaced": [VC["id"]], "dangling": [UI["id"] + " -> " + VC["id"] + "#cap-tls"], "unchanged": 3},
     "expected-rules": []},
    {"name": "release-drops-a-component",
     "a": {"objects": [REQ, UC6, VC, VC6, UI6], "kept": [{"manifest": manifest([VC, VC6]), "published": [VC, VC6]}]},
     "b": {"manifest": PM4, "objects": [VC4]},
     "expected": {"result": "replace", "replaced": [VC["id"]], "removed": [VC6["id"]],
                  "dangling": [UI6["id"] + " -> " + VC6["id"] + "#cap-rotate"], "unchanged": 3},
     "expected-rules": []},
    {"name": "id-in-the-set-that-no-pack-brought", "note": "the component was loaded as a loose file: import does not overwrite it",
     "a": {"objects": [REQ, UC, VC]}, "b": {"manifest": PM, "objects": [VC]},
     "expected": {"result": "refused", "unchanged": 3}, "expected-rules": ["ADVICE-11"], "expected-frags": ["not part of"]},
    {"name": "id-that-another-pack-brought",
     "a": {"objects": [REQ, UC, VC], "kept": [{"manifest": manifest([VC], PACK2), "published": [VC]}]},
     "b": {"manifest": PM, "objects": [VC]},
     "expected": {"result": "refused"}, "expected-rules": ["ADVICE-11"], "expected-frags": ["belongs to"]},
    {"name": "not-a-pack", "a": {"objects": [REQ, UC0]}, "b": {"manifest": manifest([VC], pack=None), "objects": [VC]},
     "expected": {"result": "refused", "added": []}, "expected-rules": ["ADVICE-11"], "expected-frags": ["no pack header"]},
    {"name": "pack-that-is-not-advice", "a": {"objects": [REQ, UC0]}, "b": {"manifest": manifest([VC, TAIL]), "objects": [VC, TAIL]},
     "expected": {"result": "refused"}, "expected-rules": ["ADVICE-1"]},
    {"name": "pack-with-an-object-under-the-users-origin",
     "a": {"objects": [REQ, UC0]}, "b": {"manifest": manifest([VC, clone(UC0, id=ORG + "/component/other")]),
                                         "objects": [VC, clone(UC0, id=ORG + "/component/other")]},
     "expected": {"result": "refused"}, "expected-rules": ["ADVICE-2"]},
]

doc = {
    "description": "Advice packs (CP-ADVICE-1, kernel 2.0.0). An advice pack is a bundle whose manifest carries a pack header and whose objects are Components: a vendor's recommendations as one published file. shape-vectors: the header and a capability's statement-ids, by schema. pack-vectors: what a pack may hold (ADVICE-1..3) and the kernel pin it needs (KERNEL-1); `declared` gives the modifies-semantics classes of facets the pack pins. graph-vectors: capabilities and the edges that cite them, in any bundle (ADVICE-4..7). kept-vectors: the vendor's manifest a set keeps under packs/sha256/ (ADVICE-8..10); a kept entry is {manifest, published} - the file's bytes are the manifest's canonical form and its name the SHA-256 of them unless `name` or `raw` says otherwise. publisher-vectors: claimed or proven, the words and the envelope check of the Tailoring tier. import-vectors: what importing pack b into set a does (ADVICE-11). In every manifest of this file an objects entry gives the id and \"semantic-digest\": \"COMPUTE\"; the harness fills version, digests and path from the objects as published. Each case names the rules that must fire, exactly (`expected-rules`), and fragments their messages must contain. The digest an Attestation binds and its signature are LITERALS written by drafts/cp-advice-1/author_vectors.py with the fixture key of dsse-vectors.json.",
    "fixture-public-key": pub,
    "shape-vectors": shape, "pack-vectors": pack, "graph-vectors": graph, "kept-vectors": kept,
    "publisher-vectors": publisher, "import-vectors": imp,
}
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
print("wrote", os.path.relpath(OUT, ROOT), {k: len(v) for k, v in doc.items() if isinstance(v, list)},
      "total", sum(len(v) for v in doc.values() if isinstance(v, list)))
