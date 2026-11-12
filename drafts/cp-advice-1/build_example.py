#!/usr/bin/env python3
"""Builds the worked advice pack and imports it into the example bundle
(CP-ADVICE-1). Re-running it changes nothing.

    uv run --with jsonschema python drafts/cp-advice-1/build_example.py

Writes
  jascon/example-packs/dbvendor-server-7-advice/     the file a vendor publishes
      content-manifest.json                          pack header; lists the Component
      objects/component/server-7.json
      attestation-dbvendor-server-7-advice.json      beside the manifest (D3.1)
      attestation-dbvendor-server-7-advice.dsse      signed with the corpus fixture key
  jascon/examples/                                   the set after the import
      component-dbvendor-server-7.json               the vendor's object, byte for byte
      packs/sha256/<hex>                             the vendor's manifest, byte for byte
      attestation-dbvendor-server-7-advice.json/.dsse  the vendor's attestation, beside
      component-acme-saas.json                       gains the product as a member
      implementation-acme-konf-14-1-s2.json          adopts one recommendation
      content-manifest.json                          two entries more, one changed

The signing key is the FIXTURE key of conformance/dsse-vectors.json
(seed = sha256('jascon dsse fixture key 1')): the seed is public, the
signature proves the mechanism and nothing about a real vendor."""
import base64, hashlib, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
VALIDATOR = os.path.join(ROOT, "jascon", "scripts", "validate_core.py")
src = open(VALIDATOR, encoding="utf-8").read()
ns = {"__file__": VALIDATOR, "__name__": "validate_core_defs"}
exec(compile(src.split("# ---------------- run ----------------")[0], VALIDATOR, "exec"), ns)
canonical, sdig = ns["canonical"], ns["sdig"]

PACKDIR = os.path.join(ROOT, "jascon", "example-packs", "dbvendor-server-7-advice")
EX = os.path.join(ROOT, "jascon", "examples")
VEN, CSO = "https://dbvendor.example", "https://cso.example"
KONF = "https://ns.bsi.bund.de/gspp/req/KONF.14.1"

def ser(obj):                       # the example bundle's spelling: indent 1, LF
    return (json.dumps(obj, indent=1, ensure_ascii=False) + "\n").encode("utf-8")
def pkg(raw): return "sha256:" + hashlib.sha256(raw).hexdigest()
def put(path, raw):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path) and open(path, "rb").read() == raw: return False
    open(path, "wb").write(raw); return True

# ---------- the pack ----------
component = {
    "id": VEN + "/component/server-7", "version": "2026-10", "label": "Example DB Server 7",
    "lifecycle": "active", "title": {"en": "Example DB Server, release line 7"}, "kind": "software",
    "product-version": "7",       # opaque text: the product version the advice describes (author decision 2026-11-12)
    "capabilities": [
        {"id": "cap-tls", "requirement-ref": KONF, "statement-ids": ["s1"],
         "description": {"en": "Set net.tls.mode to requireTLS and net.tls.disabledProtocols to TLS1_0,TLS1_1,TLS1_2. "
                               "Clients older than driver 4.2 cannot connect afterwards."},
         "parameter-bindings": {"transport-crypto": "tls13"}},
        {"id": "cap-key-rotation", "requirement-ref": KONF, "statement-ids": ["s2"],
         "description": {"en": "Rotate the server certificate and key with the rotateCertificates command; "
                               "no restart is needed. The vendor suggests an interval of 90 days."}},
        {"id": "cap-audit-log", "requirement-ref": "https://ns.nist.gov/sp800-53/req/AU-12",
         "description": {"en": "Turn on the audit log with auditLog.destination: file and ship it off the host."}},
    ],
}
obj_rel = "objects/component/server-7.json"
obj_raw = ser(component)
pack_manifest = {
    "manifest-version": "1", "kernel-version": "2.0.0",
    "provenance": {"source": "JASCON worked example (CP-ADVICE-1); a fictional vendor and product",
                   "written-with": "drafts/cp-advice-1/build_example.py"},
    "pack": {"kind": "advice", "id": VEN + "/pack/server-7-hardening", "version": "3",
             "title": {"en": "Server 7 hardening advice"},
             "publisher": {"ref": VEN + "/party/vendor", "name": {"en": "Example DB Vendor Inc."}}},
    "objects": [{"id": component["id"], "version": component["version"],
                 "package-digest": pkg(obj_raw), "semantic-digest": sdig(component), "path": obj_rel}],
    "facet-schemas": [],
}
man_raw = ser(pack_manifest)
man_hex = hashlib.sha256(man_raw).hexdigest()
ATT_NAME = "attestation-dbvendor-server-7-advice"
attestation = {
    "id": VEN + "/attestation/server-7-hardening-3", "version": "1", "lifecycle": "active",
    "title": {"en": "Release 3 of the Server 7 hardening advice, as published"},
    "subject-semantic-digests": [{"id": component["id"], "semantic-digest": sdig(component)}],
    "content-manifest-digest": "sha256:" + man_hex,
    "signer": VEN + "/party/vendor", "timestamp": "2026-10-20T09:00:00Z",
    "envelope-ref": ATT_NAME + ".dsse",
}
seed = hashlib.sha256(b"jascon dsse fixture key 1").digest()
payload = canonical(attestation).encode("utf-8")
ptype = ns["DSSE_PAYLOAD_TYPE"]
envelope = {"payloadType": ptype, "payload": base64.b64encode(payload).decode(),
            "signatures": [{"keyid": attestation["signer"],
                            "sig": base64.b64encode(ns["ed25519_sign"](seed, ns["_pae"](ptype.encode(), payload))).decode()}]}
assert ns["verify_envelope"](envelope, attestation, {attestation["signer"]: ns["ed25519_public"](seed).hex()})[0] == "verified"
att_raw, env_raw = ser(attestation), ser(envelope)

changed = []
for path, raw in [(os.path.join(PACKDIR, *obj_rel.split("/")), obj_raw),
                  (os.path.join(PACKDIR, "content-manifest.json"), man_raw),
                  (os.path.join(PACKDIR, ATT_NAME + ".json"), att_raw),
                  (os.path.join(PACKDIR, ATT_NAME + ".dsse"), env_raw)]:
    if put(path, raw): changed.append(os.path.relpath(path, ROOT))

# ---------- the set after the import ----------
mp = os.path.join(EX, "content-manifest.json")
mraw = open(mp, "rb").read()
manifest = json.loads(mraw.decode("utf-8"))
assert ser(manifest) == mraw, "the example manifest is not spelled indent-1/LF; this script would re-spell it"

def upsert(rel, obj, raw):
    e = next((e for e in manifest["objects"] if e["path"] == rel), None)
    new = {"id": obj["id"], "version": obj["version"], "package-digest": pkg(raw),
           "semantic-digest": sdig(obj), "path": rel}
    if e is None: manifest["objects"].append(new)
    else: e.clear(); e.update(new)

# 1. the vendor's object and manifest, byte for byte
if put(os.path.join(EX, "component-dbvendor-server-7.json"), obj_raw): changed.append("jascon/examples/component-dbvendor-server-7.json")
upsert("component-dbvendor-server-7.json", component, obj_raw)
store = os.path.join(EX, "packs", "sha256")
for fn in (os.listdir(store) if os.path.isdir(store) else []):       # one release of a pack in a set (ADVICE-10)
    if fn != man_hex:
        km = json.load(open(os.path.join(store, fn), encoding="utf-8"))
        if km.get("pack", {}).get("id") == pack_manifest["pack"]["id"]:
            os.remove(os.path.join(store, fn)); changed.append("removed packs/sha256/" + fn)
if put(os.path.join(store, man_hex), man_raw): changed.append("jascon/examples/packs/sha256/" + man_hex)
for ext, raw in ((".json", att_raw), (".dsse", env_raw)):
    if put(os.path.join(EX, ATT_NAME + ext), raw): changed.append("jascon/examples/" + ATT_NAME + ext)

# 2. the user's system contains the product
sp = os.path.join(EX, "component-acme-saas.json")
saas = json.load(open(sp, encoding="utf-8"))
if component["id"] not in {m["component-ref"] for m in saas["members"]}:
    saas["members"].append({"component-ref": component["id"], "context": "datastore"})
saas_raw = ser(saas)
if put(sp, saas_raw): changed.append("jascon/examples/component-acme-saas.json")
upsert("component-acme-saas.json", saas, saas_raw)

# 3. the user's edge adopts one recommendation
impl = {
    "id": CSO + "/impl/acme--konf-14-1-s2", "version": "2026-11", "lifecycle": "active",
    "component-ref": saas["id"], "requirement-ref": KONF, "statement-refs": ["s2"],
    "responsibility": "provider",
    "satisfied-by": [{"capability-ref": component["id"] + "#cap-key-rotation"}],
    "status": "planned",
}
impl_raw = ser(impl)
if put(os.path.join(EX, "implementation-acme-konf-14-1-s2.json"), impl_raw): changed.append("jascon/examples/implementation-acme-konf-14-1-s2.json")
upsert("implementation-acme-konf-14-1-s2.json", impl, impl_raw)

if put(mp, ser(manifest)): changed.append("jascon/examples/content-manifest.json")
print("pack manifest digest:", man_hex)
print("changed:" if changed else "nothing changed", *changed, sep="\n  ")
