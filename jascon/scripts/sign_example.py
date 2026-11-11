#!/usr/bin/env python3
"""JASCON - re-binds and re-signs the Attestation of the example folder.

jascon/examples/attestation-acme-2026.json binds three things (D7): the
semantic digest of each subject, the digest of the content manifest as
delivered, and the digest of the rendering. Its DSSE envelope
(attestation-envelope.dsse) signs the Attestation's canonical form. An edit
to a subject, to the manifest or to the rendering therefore leaves both
files stale, and validate_core.py fails the folder until this script has
run. It recomputes the three bindings, signs, and writes both files.

The key is the FIXTURE key of the dsse vectors: its seed is
sha256('oscal-semantic-core dsse fixture key 1'), printed in
conformance/dsse-vectors.json. Everybody can sign with it. The envelope
shows the mechanism and proves nothing about a signer.

Usage:  python3 jascon/scripts/sign_example.py           rewrite what is stale
        python3 jascon/scripts/sign_example.py --check   exit 1 if stale
Ed25519 is deterministic: a second run changes nothing.
"""
import base64, hashlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import validate_core as vc      # the engines only; the run is behind main()

EXDIR = os.path.join(vc.SKILL, "examples")
ATTESTATION = "attestation-acme-2026.json"
FIXTURE_SEED = hashlib.sha256(b"oscal-semantic-core dsse fixture key 1").digest()
KEYID = "fixture-1"


def read(name):
    with open(os.path.join(EXDIR, name), "rb") as f:
        return f.read()


def build():
    """-> {file name: bytes} for the Attestation and its envelope."""
    att = json.loads(read(ATTESTATION).decode("utf-8"))
    manifest_raw = read("content-manifest.json")
    manifest = json.loads(manifest_raw.decode("utf-8"))
    by_id = {}
    for entry in manifest["objects"]:
        by_id[entry["id"]] = json.loads(read(entry["path"]).decode("utf-8"))
    for subj in att["subject-semantic-digests"]:
        if not isinstance(subj, dict) or subj["id"] not in by_id:
            sys.exit(f"subject {subj!r} names no object of the example manifest")
        subj["semantic-digest"] = vc.sdig(by_id[subj["id"]])
    att["content-manifest-digest"] = vc.pkg_digest(manifest_raw)
    renderings = manifest.get("renderings") or []
    if len(renderings) != 1:
        sys.exit("the example manifest is expected to list exactly one rendering")
    artifact = vc.pkg_digest(read(renderings[0]["path"]))
    if artifact != renderings[0]["digest"]:
        sys.exit(f"{renderings[0]['path']}: its bytes do not have the digest the manifest lists")
    att["rendering"]["artifact-digest"] = artifact
    if not vc.VALIDATORS["attestation"].is_valid(att):
        sys.exit("the result is not an Attestation by the kernel schema")

    payload = vc.canonical(att).encode("utf-8")
    sig = vc.ed25519_sign(FIXTURE_SEED, vc._pae(vc.DSSE_PAYLOAD_TYPE.encode(), payload))
    envelope = {"payload": base64.b64encode(payload).decode("ascii"),
                "payloadType": vc.DSSE_PAYLOAD_TYPE,
                "signatures": [{"keyid": KEYID, "sig": base64.b64encode(sig).decode("ascii")}]}
    trusted = {att["signer"]: vc.ed25519_public(FIXTURE_SEED).hex()}
    status, why = vc.verify_envelope(envelope, att, trusted)
    if status != "verified":
        sys.exit(f"the envelope just written does not verify: {status} {why}")

    def text(obj):          # the folder's spelling: two spaces, LF, one final newline
        return (json.dumps(obj, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    return {ATTESTATION: text(att), att["envelope-ref"]: text(envelope)}


def main(argv):
    check = "--check" in argv
    stale = []
    for name, want in build().items():
        path = os.path.join(EXDIR, name)
        have = open(path, "rb").read() if os.path.isfile(path) else None
        if have == want:
            continue
        stale.append(name)
        if not check:
            with open(path, "wb") as f:
                f.write(want)
    for name in stale:
        print(f"{name}: {'STALE' if check else 'rewritten'}")
    if not stale:
        print("the example attestation and its envelope are up to date")
    return 1 if (check and stale) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
