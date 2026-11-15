#!/usr/bin/env python3
"""Writes the `path-vectors` and `bundle-vectors` of
jascon/conformance/dsse-vectors.json: where an `envelope-ref` may point.

An Attestation names its DSSE envelope in `envelope-ref`, a file beside the
content manifest (D3.1, D7). The reader and the app refused a ref that
leaves the manifest's folder; the reference and the twin joined the ref to
the folder unchecked, so `../x`, an absolute path or (on Windows) a
backslash path read a file the bundle does not hold. Since 2026-11-15 all
four apply one pattern (validate_core.py: OUTSIDE_REF). These vectors hold
them to it, and the bundle cases show that a ref which leaves the folder is
not read even where the file it names exists.

The envelopes are unsigned in effect: payload = the Attestation's canonical
form, one signature of 64 zero bytes. No vector supplies trusted keys, so a
resolved envelope is `unverified` and no failure.

    uv run --no-project python drafts/phase-d/envelope_ref_vectors.py [--check]
"""
import base64, copy, hashlib, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "jascon", "conformance", "dsse-vectors.json")
PAYLOAD_TYPE = "application/vnd.jascon.attestation+json"
BS = chr(92)


def _canon(o):
    if isinstance(o, dict):
        return {k: _canon(o[k]) for k in sorted(o, key=lambda s: s.encode("utf-16-be"))}
    if isinstance(o, list):
        return [_canon(x) for x in o]
    return o


def canonical(o):
    o = copy.deepcopy(o)
    o.pop("annotations", None)
    return json.dumps(_canon(o), separators=(",", ":"), ensure_ascii=False)


def sdig(o):
    return "sha256:" + hashlib.sha256(canonical(o).encode("utf-8")).hexdigest()


REQ = {
    "id": "https://ns.auth.gov/fw/req/1",
    "version": "1",
    "lifecycle": "active",
    "statements": [{"id": "s1", "modality": "should", "obligated-parties": ["https://ns.auth.gov/fw/p/o"],
                    "prose": {"en": "X."}}],
}


def attestation(ref):
    return {
        "id": "https://ns.auth.gov/fw/attestation/approval",
        "version": "1",
        "lifecycle": "active",
        "subject-semantic-digests": [{"id": REQ["id"], "semantic-digest": sdig(REQ)}],
        # binds another manifest: Semantic Match, reported and never a failure
        "content-manifest-digest": "sha256:" + "0" * 64,
        "signer": "https://ns.auth.gov/fw/party/ao",
        "timestamp": "2026-11-15T12:00:00Z",
        "envelope-ref": ref,
    }


def envelope(att):
    return {
        "payloadType": PAYLOAD_TYPE,
        "payload": base64.b64encode(canonical(att).encode("utf-8")).decode("ascii"),
        "signatures": [{"keyid": "fixture", "sig": base64.b64encode(bytes(64)).decode("ascii")}],
    }


def bundle_case(name, why, ref, beside=None, outside=None, fails=()):
    att = attestation(ref)
    env = envelope(att)
    case = {"name": name, "why": why, "listed": [REQ], "attestation": att}
    if beside: case["envelopes"] = {beside: env}
    if outside: case["outside"] = {outside: env}
    case["expected-fails"] = list(fails)
    case["expected-envelope"] = "missing" if fails else "unverified"
    return case


def no_resolve(ref):
    return f"envelope-ref '{ref}' does not resolve beside the manifest"


PATHS = [
    ("attestation.dsse", True, "a file name beside the manifest"),
    ("sig/attestation.dsse", True, "a file in a folder below the manifest's"),
    ("a..b.dsse", True, "two dots inside a name are no `..` segment"),
    ("..a", True, "nor at the start of a longer name"),
    ("./attestation.dsse", True, "a `.` segment stays in the folder"),
    ("../attestation.dsse", False, "`..` leaves the folder"),
    ("sig/../attestation.dsse", False, "a `..` segment anywhere is refused, also where it would come back"),
    ("sig/..", False, "a trailing `..` segment"),
    ("..", False, "`..` alone"),
    ("/etc/attestation.dsse", False, "an absolute path"),
    ("C:attestation.dsse", False, "a drive letter (it reads as a scheme)"),
    ("c:" + BS + "attestation.dsse", False, "a Windows path"),
    ("https://example.org/attestation.dsse", False, "a URL: nothing beside the manifest has a scheme"),
    ("sig" + BS + "attestation.dsse", False, "a backslash: Windows reads it as a folder, every other system as part of a name"),
    (chr(0x212A) + ":x", True, "dialect trap: the Kelvin sign is no ASCII letter, so this is no scheme (Python's re.I and .NET's IgnoreCase would read it as K)"),
    ("sig/..\n", True, "dialect trap: `..` followed by a line break is no `..` segment (Python's and .NET's `$` match before a final line break)"),
]

BUNDLES = [
    bundle_case("envelope-beside-the-manifest-resolves",
                "the envelope lies beside the manifest under the name the Attestation gives",
                "attestation.dsse", beside="attestation.dsse"),
    bundle_case("envelope-in-a-folder-below-resolves",
                "a relative path that stays in the manifest's folder",
                "sig/attestation.dsse", beside="sig/attestation.dsse"),
    bundle_case("missing-envelope-fails",
                "a named envelope that is not there fails, for an Attestation beside the manifest as for a listed one",
                "attestation.dsse", fails=[no_resolve("attestation.dsse")]),
    bundle_case("dotdot-ref-is-not-read-though-the-file-exists",
                "the file lies in the folder ABOVE the bundle; until 2026-11-15 the reference read it and found the envelope good",
                "../attestation.dsse", outside="attestation.dsse", fails=[no_resolve("../attestation.dsse")]),
    bundle_case("dotdot-segment-is-refused-even-where-it-comes-back",
                "`sig/../attestation.dsse` names the file beside the manifest by a detour; the rule is about the ref, not about where it lands",
                "sig/../attestation.dsse", beside="attestation.dsse", fails=[no_resolve("sig/../attestation.dsse")]),
    bundle_case("backslash-ref-is-not-read-though-the-file-exists",
                "on Windows the reference read `sig\\attestation.dsse` as sig/attestation.dsse; the app never did - one answer now",
                "sig" + BS + "attestation.dsse", beside="sig/attestation.dsse",
                fails=[no_resolve("sig" + BS + "attestation.dsse")]),
]

DESCRIPTION_ADD = (
    " path-vectors (2026-11-15): where an `envelope-ref` may point - a relative path that stays in the manifest's"
    " folder (`beside`: true), or one that leaves it (false): a scheme or drive letter, a leading slash, a backslash or a"
    " `..` segment. A ref that leaves the folder does not resolve, whether or not the file it names exists. One pattern"
    " in the reference (OUTSIDE_REF), the twin, the app (jscPlainPath) and the reader (besideName)."
    " bundle-vectors: a bundle on disk - `listed` objects under objects/ in a manifest the harness writes,"
    " `attestation` beside the manifest as attestation.json, `envelopes` by relative path in the manifest's folder,"
    " `outside` in the folder above it. `expected-fails` are fragments, one per failure, and no other failure;"
    " `expected-envelope` is unverified (read, payload good, no trusted key) or missing (not read). Written by"
    " drafts/phase-d/envelope_ref_vectors.py."
)


def build(v):
    v = copy.deepcopy(v)
    if "path-vectors" not in v.get("description", ""):
        v["description"] += DESCRIPTION_ADD
    v["path-vectors"] = [{"ref": r, "beside": b, "why": w} for r, b, w in PATHS]
    v["bundle-vectors"] = BUNDLES
    return v


def main():
    raw = open(PATH, "rb").read().replace(b"\r\n", b"\n")
    new = (json.dumps(build(json.loads(raw)), indent=1, ensure_ascii=False) + "\n").encode("utf-8")
    if "--check" in sys.argv:
        print("dsse-vectors.json: " + ("up to date" if new == raw else "OUT OF DATE"))
        return 0 if new == raw else 1
    open(PATH, "wb").write(new)
    print(f"dsse-vectors.json: {len(PATHS)} path vectors, {len(BUNDLES)} bundle vectors")
    return 0


if __name__ == "__main__":
    sys.exit(main())
