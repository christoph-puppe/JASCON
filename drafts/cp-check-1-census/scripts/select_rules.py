#!/usr/bin/env python3
"""Step 1: resolve which ComplianceAsCode rules the Ubuntu 24.04 CIS profiles select.

Usage: python3 -I select_rules.py <cac_root> <out_json>

Reads products/ubuntu2404/profiles/cis_*.profile, resolves `<policy>:all:<level>`
selections against controls/<policy>.yml (with level inheritance), applies `!rule`
exclusions, separates `var=value` variable selections from rule ids, and locates each
rule's directory (any rule.yml whose parent dir name equals the rule id).
"""
import json
import os
import sys

import yaml


def walk_controls(ctrls, out):
    for c in ctrls or []:
        out.append(c)
        if isinstance(c.get("controls"), list):
            walk_controls(c["controls"], out)


def main():
    root, out_path = sys.argv[1], sys.argv[2]
    prof_dir = os.path.join(root, "products/ubuntu2404/profiles")
    profiles = {}
    for fn in sorted(os.listdir(prof_dir)):
        if fn.startswith("cis") and fn.endswith(".profile"):
            with open(os.path.join(prof_dir, fn)) as f:
                profiles[fn] = yaml.safe_load(f)

    policies = {}
    level_parents = {}
    per_profile = {}
    var_selections = {}
    control_of_rule = {}
    status_counts = {}
    for fn, prof in profiles.items():
        rules, excluded, vars_ = set(), set(), {}
        for sel in prof.get("selections", []):
            sel = str(sel)
            if sel.startswith("!"):
                excluded.add(sel[1:])
                continue
            if ":" in sel:
                pol, cid, lvl = sel.split(":")
                if pol not in policies:
                    cpath = os.path.join(root, "controls", pol + ".yml")
                    with open(cpath) as f:
                        policies[pol] = (cpath, yaml.safe_load(f))
                cpath, cdoc = policies[pol]
                parents = {l["id"]: l.get("inherits_from", []) for l in cdoc["levels"]}
                level_parents[pol] = parents
                wanted = set()
                stack = [lvl]
                while stack:
                    l = stack.pop()
                    if l not in wanted:
                        wanted.add(l)
                        stack.extend(parents.get(l, []))
                flat = []
                walk_controls(cdoc["controls"], flat)
                for c in flat:
                    if cid != "all" and c["id"] != cid:
                        continue
                    if not set(c.get("levels", [])) & wanted:
                        continue
                    st = c.get("status", "?")
                    status_counts.setdefault(fn, {}).setdefault(st, 0)
                    status_counts[fn][st] += 1
                    for r in c.get("rules", []) or []:
                        r = str(r)
                        if "=" in r:
                            k, v = r.split("=", 1)
                            vars_[k.strip()] = v.strip()
                        else:
                            rules.add(r)
                            control_of_rule.setdefault(r, set()).add(str(c["id"]))
            elif "=" in sel:
                k, v = sel.split("=", 1)
                vars_[k] = v
            else:
                rules.add(sel)
        per_profile[fn] = sorted(rules - excluded)
        var_selections[fn] = vars_

    union = sorted(set().union(*per_profile.values()))

    # locate rule directories
    rule_dirs = {}
    for dp, dns, fns in os.walk(root):
        if "/.git" in dp or "/build" in dp:
            continue
        if "rule.yml" in fns:
            rid = os.path.basename(dp)
            rule_dirs.setdefault(rid, []).append(os.path.relpath(dp, root))
    located = {r: rule_dirs.get(r, []) for r in union}
    missing = [r for r, d in located.items() if not d]

    all_vars = {}
    for v in var_selections.values():
        all_vars.update(v)
    out = {
        "profiles": {fn: os.path.join("products/ubuntu2404/profiles", fn) for fn in profiles},
        "controls_files": {p: os.path.relpath(v[0], root) for p, v in policies.items()},
        "control_status_counts_per_profile": status_counts,
        "rules_per_profile_count": {k: len(v) for k, v in per_profile.items()},
        "rules_per_profile": per_profile,
        "union_rule_count": len(union),
        "union_rules": union,
        "rule_dirs": located,
        "missing_rule_dirs": missing,
        "control_ids_per_rule": {r: sorted(control_of_rule.get(r, [])) for r in union},
        "variable_selections_union": all_vars,
    }
    with open(out_path, "w") as f:
        json.dump(out, f, indent=1)
    print("profiles:", out["rules_per_profile_count"])
    print("union:", len(union), "missing dirs:", len(missing), missing[:20])
    print("multi-located:", {r: d for r, d in located.items() if len(d) > 1})


if __name__ == "__main__":
    main()
