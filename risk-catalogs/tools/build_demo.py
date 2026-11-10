#!/usr/bin/env python3
"""build_demo.py - end-to-end check of the risk-catalogue prototype.

Builds a complete JASCON bundle that the reference validator accepts:

  1. copies the shipped NIST SP 800-53 bundle (1,014 requirements, 25 sets);
  2. adds what an organisation would add: a Component (its office IT) and a
     Tailoring that selects the MODERATE baseline - its Statement of
     Applicability;
  3. imports the office-IT risk catalogue against that Tailoring, with one
     entry recorded as not applicable (see demo/office-it-moderate/);
  4. plays the organisation for two of the imported risks - assesses them
     and chooses a treatment option - so that the coverage report shows
     covered, pending and uncovered requirements side by side;
  5. writes the content manifest, pinned to kernel 2.0.0.

Usage:
  python3 risk-catalogs/tools/build_demo.py OUT_DIR
  python3 jascon/scripts/validate_core.py OUT_DIR

The bundle (about 7 MB) is not committed; the imported Risk objects, the
Tailoring and the import report are, under demo/office-it-moderate/.
"""
import hashlib, importlib.util, json, os, shutil, sys, types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
SOURCE = os.path.join(ROOT, "converted_examples", "US.SP800-53", "sp800-53-core-bundle")
CATALOG = os.path.join(ROOT, "risk-catalogs", "office-it")
DEMO = os.path.join(ROOT, "risk-catalogs", "demo", "office-it-moderate")
ORG = "https://org.example"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    out = sys.argv[1]
    rc = load_module("risk_catalog", os.path.join(HERE, "risk_catalog.py"))
    lib = load_module("oscal_conv_lib", os.path.join(ROOT, "jascon", "scripts", "oscal_conv_lib.py"))

    if os.path.exists(out): shutil.rmtree(out)
    shutil.copytree(SOURCE, out)
    mpath = os.path.join(out, "content-manifest.json")
    manifest = json.load(open(mpath, encoding="utf-8"))

    def add(rel, obj):
        raw = (json.dumps(obj, indent=1, ensure_ascii=False) + "\n").encode("utf-8")
        full = os.path.join(out, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "wb") as f: f.write(raw)
        manifest["objects"].append({"id": obj["id"], "version": obj["version"],
                                    "package-digest": "sha256:" + hashlib.sha256(raw).hexdigest(),
                                    "semantic-digest": lib.semantic_digest(obj), "path": rel})

    def write_manifest():
        pinned = {"manifest-version": manifest["manifest-version"], "kernel-version": "2.0.0"}
        pinned.update({k: v for k, v in manifest.items() if k not in pinned})
        with open(mpath, "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(pinned, indent=1, ensure_ascii=False) + "\n")

    component = {"id": f"{ORG}/component/office-it", "version": "1", "lifecycle": "active", "kind": "system",
                 "title": {"en": "Office IT", "de": "Büro-IT"}}
    tailoring = {"id": f"{ORG}/tailoring/soa-office-it", "version": "1", "lifecycle": "active",
                 "title": {"en": "Statement of Applicability - office IT", "de": "Erklärung zur Anwendbarkeit - Büro-IT"},
                 "selects": [{"set-ref": "https://ns.nist.gov/sp800-53/set/baseline/moderate"}]}
    add("objects/component/office-it.json", component)
    add("objects/tailoring/soa-office-it.json", tailoring)
    write_manifest()                      # the import reads the bundle through its manifest

    risks_dir = os.path.join(out, "_imported")
    na_path = os.path.join(DEMO, "not-applicable.json")
    rc.cmd_import(types.SimpleNamespace(catalog=CATALOG, bundle=out, org=ORG, owner=f"{ORG}/party/ciso",
                                        out=risks_dir, tailoring=tailoring["id"], not_applicable=na_path))

    # the organisation's own work, played here for two risks so that the
    # report has something in every column
    decided = {"OFF-02": ("hoch", "mittel"), "OFF-04": ("hoch", "gering")}
    scale = f"{ORG}/scale/3x3"
    committed = os.path.join(DEMO, "risks")
    if os.path.exists(committed): shutil.rmtree(committed)
    os.makedirs(committed)
    for fn in sorted(os.listdir(risks_dir)):
        if fn == "import-report.json":
            shutil.copy(os.path.join(risks_dir, fn), os.path.join(DEMO, fn)); continue
        risk = json.load(open(os.path.join(risks_dir, fn), encoding="utf-8"))
        risk["component-refs"] = [component["id"]]
        if risk["label"] in decided:
            level, residual = decided[risk["label"]]
            risk.update({"lifecycle": "active", "state": "assessed", "treatment": "modify",
                         "rating": {"level": level, "scale-ref": scale},
                         "residual-rating": {"level": residual, "scale-ref": scale}})
        add(f"objects/risk/{fn}", risk)
        with open(os.path.join(committed, fn), "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(risk, indent=1, ensure_ascii=False) + "\n")
    shutil.rmtree(risks_dir)
    with open(os.path.join(DEMO, "tailoring-soa-office-it.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(tailoring, indent=1, ensure_ascii=False) + "\n")
    write_manifest()
    print(f"\nbundle      {out}  ({len(manifest['objects'])} objects, kernel-version 2.0.0)")
    print(f"validate    python3 jascon/scripts/validate_core.py {out}")


if __name__ == "__main__":
    main()
