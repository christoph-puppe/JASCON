#!/usr/bin/env python3
"""Issues the example folder's Attestation from the folder as it lies
(backlog #46, phase D). Re-running it changes nothing; run it after any
change to an object or to the manifest of jascon/examples/.

    python3 drafts/phase-d/attest_example.py            write
    python3 drafts/phase-d/attest_example.py --check    exit 1 if the two files are not what this would write

Writes, beside the example manifest (D3.1: never listed in it)
    attestation-acme-2026.json    three subjects by id and semantic digest, and the
                                  SHA-256 of content-manifest.json as it lies on disk
    attestation-acme-2026.dsse    a DSSE envelope over the Attestation's canonical form

From before 1.0.0 until 2026-11-14 the Attestation carried three subject
digests that matched no object, a manifest digest that matched no
manifest, and an `envelope-ref` to a file that did not exist. Nothing
checked it. The validators now apply `attestation-binds` (Appendix B.1.7)
to every Attestation they read with a bundle; this script is how the
example stays what it claims when the folder changes.

What an authorizing official signs for a system: the system, how it meets
the requirement, and the assessment of that. Here: the Acme SaaS Component,
its Implementation of KONF.14.1 and the 2026 Q3 Assessment - the case the
rendering (authorization-summary.md) is about.

The signing key is the FIXTURE key of conformance/dsse-vectors.json
(seed = sha256('jascon dsse fixture key 1')). The seed is public: the
signature shows the mechanism and proves nothing about an agency.
conformance/fixture-trusted-keys.json holds its public key for the two
signers of the example folder, for a run in verification mode."""
import base64, hashlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
VALIDATOR = os.path.join(ROOT, "jascon", "scripts", "validate_core.py")
src = open(VALIDATOR, encoding="utf-8").read()
ns = {"__file__": VALIDATOR, "__name__": "validate_core_defs"}
exec(compile(src.split("# ---------------- run ----------------")[0], VALIDATOR, "exec"), ns)
canonical, sdig, pkg_digest = ns["canonical"], ns["sdig"], ns["pkg_digest"]

EX = os.path.join(ROOT, "jascon", "examples")
ATT, ENV = "attestation-acme-2026.json", "attestation-acme-2026.dsse"
SIGNER = "https://agency-x.example/party/ao"
SUBJECTS = ["component-acme-saas.json", "implementation-acme-konf.json", "assessment-2026q3.json"]
# The day this version of the Attestation was issued. Fixed, so that a re-run
# writes the same bytes; it is later than every subject, and later than the
# vendor's advice the Component adopted (2026-10-20).
TIMESTAMP = "2026-11-14T09:00:00Z"

def load(fn): return json.load(open(os.path.join(EX, fn), encoding="utf-8"))
manifest_raw = open(os.path.join(EX, "content-manifest.json"), "rb").read()
manifest = json.loads(manifest_raw.decode("utf-8"))
listed = {e["path"]: e for e in manifest["objects"]}
assert ATT not in listed, "the manifest lists the Attestation (D3.1)"

subjects = []
for fn in SUBJECTS:
    o = load(fn)
    assert fn in listed and listed[fn]["semantic-digest"] == sdig(o), f"{fn}: the manifest does not pin this object as it lies - re-pin the manifest first"
    subjects.append({"id": o["id"], "semantic-digest": sdig(o)})

rendering_raw = open(os.path.join(EX, "authorization-summary.md"), "rb").read()
attestation = {
    "id": "https://agency-x.example/attestation/acme-2026", "version": "2", "lifecycle": "active",
    "title": {"en": "Authorization of Acme SaaS, 2026"},
    "subject-semantic-digests": subjects,
    "content-manifest-digest": pkg_digest(manifest_raw),
    "rendering": {"artifact-digest": pkg_digest(rendering_raw), "media-type": "text/markdown",
                  "template-ref": {"id": "https://ns.jascon.net/stdlib/template/summary", "version": "1.0.0",
                                   "digest": "sha256:ILLUSTRATIVE-SEE-README"},
                  "renderer": "https://tools.example/render-engine@0.1"},
    "signer": SIGNER, "timestamp": TIMESTAMP, "envelope-ref": ENV}
assert ns["inferType_single"](attestation) == "attestation"

seed = hashlib.sha256(b"jascon dsse fixture key 1").digest()
pub = ns["ed25519_public"](seed).hex()
fixture = json.load(open(os.path.join(ROOT, "jascon", "conformance", "dsse-vectors.json"), encoding="utf-8"))
assert pub == fixture["fixture-public-key"], "fixture key drifted"
payload = canonical(attestation).encode("utf-8")
ptype = ns["DSSE_PAYLOAD_TYPE"]
envelope = {"payloadType": ptype, "payload": base64.b64encode(payload).decode(),
            "signatures": [{"keyid": SIGNER, "sig": base64.b64encode(ns["ed25519_sign"](seed, ns["_pae"](ptype.encode(), payload))).decode()}]}
assert ns["verify_envelope"](envelope, attestation, {SIGNER: pub})[0] == "verified"

def ser(obj, indent): return (json.dumps(obj, indent=indent, ensure_ascii=False) + "\n").encode("utf-8")
want = {ATT: ser(attestation, 2), ENV: ser(envelope, 1)}       # the Attestation keeps the indent its file has had
if "--check" in sys.argv[1:]:
    stale = [fn for fn, b in want.items() if not os.path.exists(os.path.join(EX, fn)) or open(os.path.join(EX, fn), "rb").read() != b]
    if stale: sys.exit("the example folder changed after its Attestation was issued: " + ", ".join(stale) + " - run drafts/phase-d/attest_example.py")
    print("the example Attestation is what this script would write"); sys.exit(0)
for fn, b in want.items():
    with open(os.path.join(EX, fn), "wb") as f: f.write(b)
print(f"{ATT}: 3 subjects, binds content-manifest.json {pkg_digest(manifest_raw)[:19]}..., signed with the fixture key")
