#!/usr/bin/env python3
"""kube-bench census: bin_op, compare.op, set:false, regex values (I-Regexp tiers).

Usage: python3 -I kube_bench.py <scripts_dir> <cfg_version_dir> [<cfg_version_dir> ...] <out.json>
"""
import json
import os
import sys
from collections import Counter

sys.path.insert(0, sys.argv[1])
from iregexp import classify  # noqa: E402

import yaml  # noqa: E402


def analyse(vdir):
    res = {
        "files": [], "checks_total": 0, "checks_by_type": Counter(), "checks_with_tests": 0,
        "bin_op": Counter(), "test_items_per_check": Counter(), "compare_op": Counter(),
        "set_values": Counter(), "test_item_kind": Counter(), "set_false_items": 0,
        "set_true_without_compare": 0, "items_without_set_or_compare": 0,
        "checks_or_with_multiple_items": 0, "checks_and_multiple_items": 0,
        "use_multiple_values": 0, "regex_items": [], "compare_value_types": Counter(),
        "op_examples": {}, "checks_with_set_false": 0, "checks_or_mixing_set_false": 0,
    }
    for fn in sorted(os.listdir(vdir)):
        if not fn.endswith(".yaml") or fn == "config.yaml":
            continue
        res["files"].append(fn)
        doc = yaml.safe_load(open(os.path.join(vdir, fn)))
        for g in doc.get("groups", []) or []:
            for c in g.get("checks", []) or []:
                res["checks_total"] += 1
                res["checks_by_type"][c.get("type", "(automated/default)")] += 1
                if c.get("use_multiple_values"):
                    res["use_multiple_values"] += 1
                t = c.get("tests")
                if not t:
                    continue
                res["checks_with_tests"] += 1
                items = t.get("test_items", []) or []
                bop = t.get("bin_op", "(absent)")
                res["bin_op"][bop] += 1
                res["test_items_per_check"][len(items)] += 1
                if len(items) > 1 and bop == "or":
                    res["checks_or_with_multiple_items"] += 1
                if len(items) > 1 and bop in ("and", "(absent)"):
                    res["checks_and_multiple_items"] += 1
                has_false = False
                for it in items:
                    kind = "flag" if "flag" in it else "path" if "path" in it else "env" if "env" in it else "?"
                    res["test_item_kind"][kind] += 1
                    s = it.get("set", "(absent)")
                    res["set_values"][str(s)] += 1
                    cmp_ = it.get("compare")
                    if s is False:
                        res["set_false_items"] += 1
                        has_false = True
                    # kube-bench: `set` defaults to true (check/test.go UnmarshalYAML); bin_op "" == and
                    if s is not False and not cmp_:
                        res["presence_only_items(set true or default, no compare)"] = res.get(
                            "presence_only_items(set true or default, no compare)", 0) + 1
                    if s is True and not cmp_:
                        res["set_true_without_compare"] += 1
                    if cmp_:
                        op = cmp_.get("op")
                        res["compare_op"][op] += 1
                        val = cmp_.get("value")
                        res["compare_value_types"][type(val).__name__] += 1
                        res["op_examples"].setdefault(op, []).append(
                            {"check": c.get("id"), "kind": kind, "item": it.get(kind), "value": val})
                        if op == "regex":
                            r = classify(str(val))
                            r["check"] = c.get("id")
                            r["regex"] = str(val)
                            r["features_unique"] = sorted(set(r["features"]))
                            res["regex_items"].append(r)
                    elif s == "(absent)":
                        res["items_without_set_or_compare"] += 1
                sig = " + ".join(sorted(
                    ("absent" if it.get("set") is False else
                     ("cmp:" + it["compare"]["op"]) if it.get("compare") else "present") for it in items))
                res.setdefault("check_shapes", Counter())[bop + " | " + sig] += 1
                if has_false:
                    res["checks_with_set_false"] += 1
                    if bop == "or" and len(items) > 1:
                        res["checks_or_mixing_set_false"] += 1
    rx = res["regex_items"]
    res["regex_summary"] = {
        "n": len(rx), "tiers": dict(Counter(r["tier"] for r in rx)),
        "features": dict(Counter(f for r in rx for f in r["features_unique"])),
        "raw_string_valid_iregexp_syntax": sum(1 for r in rx if r["raw_string_is_valid_iregexp_syntax"]),
        "distinct": sorted({r["regex"] for r in rx}),
    }
    for k, v in list(res.items()):
        if isinstance(v, Counter):
            res[k] = dict(v.most_common())
    res["op_examples"] = {k: v[:4] for k, v in res["op_examples"].items()}
    return res


def main():
    *dirs, out = sys.argv[2:]
    result = {os.path.basename(d.rstrip("/")): analyse(d) for d in dirs}
    json.dump(result, open(out, "w"), indent=1, default=str)
    for k, v in result.items():
        print("==", k)
        for kk in ("files", "checks_total", "checks_by_type", "checks_with_tests", "bin_op",
                   "test_items_per_check", "compare_op", "set_values", "test_item_kind", "set_false_items",
                   "set_true_without_compare", "checks_or_with_multiple_items", "checks_and_multiple_items",
                   "checks_with_set_false", "checks_or_mixing_set_false", "compare_value_types", "regex_summary",
                   "presence_only_items(set true or default, no compare)", "check_shapes"):
            print("  ", kk, v[kk])


if __name__ == "__main__":
    main()
