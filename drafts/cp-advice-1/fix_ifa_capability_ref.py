#!/usr/bin/env python3
"""One edge of the shipped IFA bundle, rewritten to the capability-ref grammar
of CP-ADVICE-1 (ADVICE-7).

    uv run python drafts/cp-advice-1/fix_ifa_capability_ref.py

`impl/saas-ac-2` cites the bare id `cap-consumer-ac-2a`. A bare id names a
capability of the edge's OWN component (`saas`), which declares none; the
capability is declared by `access-control-appliance`, a member of `saas`.
The edge therefore becomes `<appliance-id>#cap-consumer-ac-2a`.

convert_ifa.py carries the same change, but it cannot be re-run from a
checkout: its sources (sources/nist/) are git-ignored. This script makes the
change the converter would make, and proves it is the same bytes: before it
touches anything it re-serialises the object and the manifest the way
oscal_conv_lib.Bundle writes them (json.dump indent=1, CRLF) and refuses to
go on unless that reproduces the files on disk byte for byte."""
import copy, hashlib, io, json, os

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
B = os.path.join(ROOT, "converted_examples", "US.IFA-GoodRead", "ifa-core-bundle")
REL = "objects/impl/saas-ac-2.json"
APPLIANCE = "https://ifa.gov/goodread/component/access-control-appliance"
OLD, NEW = "cap-consumer-ac-2a", APPLIANCE + "#cap-consumer-ac-2a"

def ser(obj):
    f = io.StringIO()
    json.dump(obj, f, indent=1, ensure_ascii=False); f.write("\n")
    return f.getvalue().replace("\n", "\r\n").encode("utf-8")

def canon(o):
    if isinstance(o, dict): return {k: canon(v) for k, v in sorted(o.items()) if not (isinstance(v, (list, dict)) and len(v) == 0)}
    if isinstance(o, list): return [canon(v) for v in o]
    return o

def sdig(obj):
    o = copy.deepcopy(obj); o.pop("annotations", None)
    return "sha256:" + hashlib.sha256(json.dumps(canon(o), separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()

pkg = lambda raw: "sha256:" + hashlib.sha256(raw).hexdigest()

p, mp = os.path.join(B, REL), os.path.join(B, "content-manifest.json")
raw, mraw = open(p, "rb").read(), open(mp, "rb").read()
obj, man = json.loads(raw.decode("utf-8")), json.loads(mraw.decode("utf-8"))
assert ser(obj) == raw, "the object on disk is not what the converter's writer produces"
assert ser(man) == mraw, "the manifest on disk is not what the converter's writer produces"
entry = next(e for e in man["objects"] if e["path"] == REL)
assert entry["package-digest"] == pkg(raw) and entry["semantic-digest"] == sdig(obj), "manifest entry does not match the file"

appl = json.load(open(os.path.join(B, "objects", "component", "access-control-appliance.json"), encoding="utf-8"))
assert OLD in {c["id"] for c in appl["capabilities"]}, "the appliance does not declare the capability"
refs = [sb for sb in obj["satisfied-by"] if sb.get("capability-ref") == OLD]
if not refs:
    assert any(sb.get("capability-ref") == NEW for sb in obj["satisfied-by"]), "unexpected capability-ref"
    print("already rewritten; nothing to do")
else:
    assert len(refs) == 1
    refs[0]["capability-ref"] = NEW
    out = ser(obj)
    entry["package-digest"], entry["semantic-digest"] = pkg(out), sdig(obj)
    open(p, "wb").write(out)
    open(mp, "wb").write(ser(man))
    print("rewrote", REL, "and its manifest entry")
