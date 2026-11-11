#!/usr/bin/env python3
"""Step 4: classify every regex from selected rules (static OVAL + template parameters).

Usage: python3 -I cac_regex.py <scripts_dir> <rules.json> <out_regex.json> <cac_root> <selection.json>

Regexes given by var_ref: if the OVAL variable is an external_variable, the XCCDF Value's
option selected by the CIS controls (or its default) is looked up in <id>.var and classified;
if it is a local_variable (derived at collection time), it is counted as derived.

Sides:
  state            : `operation="pattern match"` on an OVAL state entity  -> the comparison
  object:pattern   : textfilecontent54 <pattern> etc. -> extraction (collector side)
  object:filesel   : filepath/path/filename pattern match -> file selection (collector side)
  object:other     : other object entities with pattern match (collector-side selection)
  variable         : regex_capture patterns in local_variables (collector-side derivation)
  template_param   : template vars whose key contains 'regex' (pattern params visible in rule.yml)
"""
import json
import sys
from collections import Counter, defaultdict

sys.path.insert(0, sys.argv[1])
from iregexp import classify  # noqa: E402


def resolve_product_vars(vars_, product="ubuntu2404"):
    out = {}
    for k, v in (vars_ or {}).items():
        if "@" not in k:
            out.setdefault(k, v)
    for k, v in (vars_ or {}).items():
        if "@" in k:
            base, prod = k.split("@", 1)
            if prod == product:
                out[base] = v
    return out


def side_of(r):
    s = r["side"]
    if s.startswith("state"):
        return s
    if s.startswith("variable"):
        return "variable"
    ent = r.get("entity")
    if ent in ("pattern",):
        return "object:pattern"
    if ent in ("filepath", "path", "filename"):
        return "object:filesel"
    return "object:other"


def find_var_files(root):
    import os
    out = {}
    for dp, dns, fns in os.walk(os.path.join(root, "linux_os")):
        for fn in fns:
            if fn.endswith(".var"):
                out[fn[:-4]] = os.path.join(dp, fn)
    return out


def xccdf_value(var_files, name, selections):
    import re
    import yaml
    path = var_files.get(name)
    if not path:
        return None, None
    txt = open(path).read()
    try:
        opts = (yaml.safe_load(txt) or {}).get("options", {})
    except Exception:
        return None, None
    key = selections.get(name, "default")
    val = opts.get(key, opts.get("default"))
    return (str(val) if val is not None else None), key


def main():
    rules = json.load(open(sys.argv[2]))["rules"]
    var_files = find_var_files(sys.argv[4])
    selections = json.load(open(sys.argv[5]))["variable_selections_union"]
    items = []
    for rid, rec in rules.items():
        if rec.get("mechanism") == "static_oval":
            for r in rec["oval"]["regexes"]:
                if r.get("regex") is None:
                    items.append({"rule": rid, "side": side_of(r), "entity": r.get("entity"),
                                  "regex": None, "var_ref": r.get("var_ref")})
                    continue
                items.append({"rule": rid, "side": side_of(r), "entity": r.get("entity"), "regex": r["regex"]})
        if rec.get("mechanism") == "template" and rec.get("template"):
            v = resolve_product_vars(rec["template"].get("vars"))
            for k, val in v.items():
                if "regex" in k.lower() and isinstance(val, str) and val:
                    items.append({"rule": rid, "side": "template_param", "entity": rec["template_name"] + "." + k,
                                  "regex": val})
    out_items = []
    for it in items:
        if it["regex"] is None:
            o = rules[it["rule"]]["oval"]
            if it["var_ref"] in o["external_variables"]:
                val, key = xccdf_value(var_files, it["var_ref"], selections)
                if val is None:
                    it["tier"] = "var_ref:external(unresolved)"
                    out_items.append(it)
                    continue
                it["regex"], it["xccdf_option"], it["via"] = val, key, "external_variable"
            elif it["var_ref"] in o.get("simple_concat_vars", {}):
                parts, ok = [], True
                for kind, val in o["simple_concat_vars"][it["var_ref"]]:
                    if kind == "literal":
                        parts.append(val)
                    elif val in o["external_variables"]:
                        v2, _ = xccdf_value(var_files, val, selections)
                        if v2 is None:
                            ok = False
                        parts.append(v2 or "")
                    else:
                        ok = False
                if not ok:
                    it["tier"] = "var_ref:not_external(local_variable or defined elsewhere; not classified)"
                    out_items.append(it)
                    continue
                it["regex"], it["via"] = "".join(parts), "local concat(literal, XCCDF value)"
            else:
                it["tier"] = "var_ref:not_external(local_variable or defined elsewhere; not classified)"
                out_items.append(it)
                continue
        c = classify(it["regex"])
        it.update(c)
        it["features_unique"] = sorted(set(c["features"]))
        out_items.append(it)

    def summarise(sel):
        tiers = Counter(i["tier"] for i in sel)
        feats = Counter(f for i in sel for f in i.get("features_unique", []))
        block = Counter(b for i in sel for b in i.get("blocking", []))
        raw_ok = sum(1 for i in sel if i.get("raw_string_is_valid_iregexp_syntax"))
        uniq = len({i["regex"] for i in sel if i["regex"] is not None})
        return {"n": len(sel), "distinct_strings": uniq, "tiers": dict(tiers),
                "raw_string_valid_iregexp_syntax_without_anchor_normalisation": raw_ok,
                "regexes_using_feature": dict(feats.most_common()),
                "blocking_reasons": dict(block.most_common())}

    by_side = defaultdict(list)
    for i in out_items:
        by_side[i["side"]].append(i)
    summary = {side: summarise(lst) for side, lst in sorted(by_side.items())}
    summary["ALL"] = summarise(out_items)
    summary["collector_side_all_except_state_test"] = summarise(
        [i for i in out_items if not i["side"].startswith("state(test")])
    json.dump({"summary": summary, "items": out_items}, open(sys.argv[3], "w"), indent=1)
    for k, v in summary.items():
        print("==", k, json.dumps({kk: vv for kk, vv in v.items() if kk != "regexes_using_feature"}))
        print("   features:", list(v["regexes_using_feature"].items())[:14])


if __name__ == "__main__":
    main()
