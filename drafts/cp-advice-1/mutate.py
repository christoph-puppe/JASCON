#!/usr/bin/env python3
"""Mutation run for the advice vectors (CP-ADVICE-1): every deliberate
defect below, put into the reference validator one at a time, must turn at
least one vector of conformance/advice-vectors.json red. A mutation the
vectors do not notice is a rule the corpus does not hold. Three guards are
not in the list because removing them crashes the code behind them (a
KeyError is not a verdict): the type of a capability's requirement-ref, the
pack header of a kept manifest, and a listed object missing from the set.
Each has a vector of its own all the same.

    uv run --with jsonschema python drafts/cp-advice-1/mutate.py

Nothing is written; the validator's source is mutated in memory."""
import io, os, sys, contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
VALIDATOR = os.path.join(ROOT, "jascon", "scripts", "validate_core.py")
SRC = open(VALIDATOR, encoding="utf-8").read().split("# ---------------- run ----------------")[0]

MUTATIONS = [
    ("ADVICE-1 off", 't = objs[oid][0]\n        if t != "component":', 't = objs[oid][0]\n        if False:'),
    ("ADVICE-2 objects off", "if uri_origin(oid) != origin:", "if False:"),
    ("ADVICE-2 publisher off", "if uri_origin(pub) != origin:", "if False:"),
    ("ADVICE-3 off", "if decl:                                     # unregistered", "if False:    #"),
    ("ADVICE-4 off", 'ids.count(n) > 1}):\n            E.append(_adv("ADVICE-4"', 'ids.count(n) > 2}):\n            E.append(_adv("ADVICE-4"'),
    ("ADVICE-5 clause not checked", 'if sid not in sids:\n                    E.append(_adv("ADVICE-5"', 'if False:\n                    E.append(_adv("ADVICE-5"'),
    ("ADVICE-5 clauses without requirement", 'if c.get("statement-ids"):\n                    E.append', 'if False:\n                    E.append'),
    ("ADVICE-6 ignores the covered clauses", 'cover = set(c.get("statement-ids") or sids)', "cover = set(sids)"),
    ("ADVICE-6 accepts values outside the space", 'if verdict != "valid":', 'if verdict == "invalid":'),
    ("ADVICE-7 component may be absent", "if cid != own:      # the edge's own", "if False:      #"),
    ("ADVICE-7 capability need not exist", 'if cap not in {c["id"] for c in comp[1].get("capabilities", []) or []}:\n                E.append', 'if False:\n                E.append'),
    ("ADVICE-7 membership off", 'cid not in {m["component-ref"] for m in owner[1].get("members", []) or []}:', "False:"),
    ("ADVICE-7 target type not checked", 'if comp[0] != "component":\n                E.append(_adv("ADVICE-7"', 'if False:\n                E.append(_adv("ADVICE-7"'),
    ("ADVICE-8 name not checked", "if hashlib.sha256(raw).hexdigest() != name:", "if False:"),
    ("ADVICE-8 listing not checked", 'if str(e.get("path", "")).startswith(PACK_STORE):', "if False:"),
    ("ADVICE-9 digest not compared", 'elif sdig(tgt[1]) != e["semantic-digest"]:', "elif False:"),
    ("ADVICE-9 version not compared", 'elif tgt[1].get("version") != e["version"]:', "elif False:"),
    ("ADVICE-10 two releases accepted", "if pid in release:", "if False:"),
    ("ADVICE-10 shared object accepted", 'if e["id"] in owner:', "if False:"),
    ("ADVICE-11 overwrites anything", 'elif oid in owned: R["replaced"].append(oid)', 'elif True: R["replaced"].append(oid)'),
    ("ADVICE-11 imports the same file again", "if any(name == b_digest for name, _ in a_kept):", "if False:"),
    ("ADVICE-11 non-pack accepted", 'if not pack:\n        R["errors"].append', 'if False:\n        R["errors"].append'),
    ("import keeps silent about dangling edges", 'R["dangling"].append(f"{iid} -> {ref}")', "pass"),
    ("import forgets dropped components", 'R["removed"] = sorted(o for o in owned if o in a_objs and o not in b_objs)', 'R["removed"] = []'),
    ("publisher: any signer proves", 'if t != "attestation" or uri_origin(o.get("signer", "")) != origin: continue\n        if o.get("content-manifest-digest")',
     'if t != "attestation": continue\n        if o.get("content-manifest-digest")'),
    ("publisher: any manifest proves", 'if o.get("content-manifest-digest") != mdigest: continue', "pass"),
    ("publisher: unverified proves", 'if notes is not None: notes.append(f"{oid}: {why}")\n                continue', 'if notes is not None: notes.append(f"{oid}: {why}")'),
    ("KERNEL-1 ignores the pack header", 'if manifest and manifest.get("pack"): return', "if False: return"),
]

def run(source):
    ns = {"__file__": VALIDATOR, "__name__": "validate_core_defs"}
    exec(compile(source, VALIDATOR, "exec"), ns)
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            ns["run_advice"]()
        except Exception as e:                # a crash is not a verdict
            return ns["counts"]["advice"], -1, [repr(e)]
    return ns["counts"]["advice"], ns["counts"]["advice:FAIL"], [f for f in ns["fails"]]

passed, failed, _ = run(SRC)
print(f"unmutated: {passed} pass, {failed} fail")
if failed: sys.exit("the unmutated validator is not green")
bad = 0
for name, old, new in MUTATIONS:
    n = SRC.count(old)
    if n != 1:
        print(f"  ?? {name}: the mutated text occurs {n} times, expected 1"); bad += 1; continue
    p, f, msgs = run(SRC.replace(old, new))
    if f == -1: print(f"  !! {name}: the mutant crashed ({msgs[0][:90]}) - not a verdict"); bad += 1
    elif f == 0: print(f"  !! {name}: NO vector noticed"); bad += 1
    else: print(f"  ok {name}: {f} vector(s) red")
print(f"{len(MUTATIONS) - bad} of {len(MUTATIONS)} mutations caught")
sys.exit(1 if bad else 0)
