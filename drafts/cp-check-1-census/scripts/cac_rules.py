#!/usr/bin/env python3
"""Step 2/3/5: per selected rule, decide the check mechanism and extract OVAL features.

Usage: python3 -I cac_rules.py <scripts_dir> <cac_root> <selection.json> <out_rules.json>

Check mechanism, following CaC build precedence (docs/manual/developer/06_contributing_with_content.md):
  static OVAL (oval/<product>.xml > oval/<family>.xml > oval/shared.xml, applicable by its
  <affected> metadata) shadows the template; otherwise the template's OVAL if the template
  supports OVAL and the rule does not switch the oval backend off; otherwise SCE if present.
"""
import json
import os
import re
import sys
from collections import Counter

sys.path.insert(0, sys.argv[1])
from cacenv import CacEnv  # noqa: E402

import yaml  # noqa: E402
from lxml import etree  # noqa: E402

PRODUCT = "ubuntu2404"
FAMILIES = ["ubuntu", "debian-like"]
APPLICABLE_PLATFORMS = {"Ubuntu 24.04", "multi_platform_all", "multi_platform_ubuntu"}


def oval_candidates(rule_dir):
    od = os.path.join(rule_dir, "oval")
    if not os.path.isdir(od):
        return []
    files = sorted(f for f in os.listdir(od) if f.endswith(".xml"))
    order = []
    for name in [PRODUCT + ".xml"] + [f + ".xml" for f in FAMILIES] + ["shared.xml"]:
        if name in files:
            order.append(os.path.join(od, name))
    return order


def wrap_xml(text):
    prefixes = set(re.findall(r"<\/?([A-Za-z_][\w.-]*):", text)) | set(
        re.findall(r"\s([A-Za-z_][\w.-]*):[\w.-]+\s*=", text))
    prefixes.discard("xmlns")
    decl = " ".join('xmlns:%s="urn:prefix:%s"' % (p, p) for p in sorted(prefixes))
    body = re.sub(r"<\?xml[^>]*\?>", "", text)
    return "<wrapper %s>%s</wrapper>" % (decl, body)


def lname(el):
    q = etree.QName(el)
    pfx = q.namespace.rsplit(":", 1)[-1] if q.namespace and q.namespace.startswith("urn:prefix:") else ""
    return (pfx + ":" if pfx else "") + q.localname


def criteria_depth(el):
    best = 0
    for ch in el:
        if not isinstance(ch.tag, str):
            continue
        if etree.QName(ch).localname == "criteria":
            best = max(best, 1 + criteria_depth(ch))
    return best


def analyse_oval(text, rule_id):
    root = etree.fromstring(wrap_xml(text).encode("utf-8"), parser=etree.XMLParser(recover=False))
    f = {
        "test_types": Counter(), "object_types": Counter(), "state_types": Counter(),
        "op_object": Counter(), "op_state": Counter(), "op_other": Counter(),
        "datatype_state": Counter(), "check": Counter(), "check_existence": Counter(),
        "state_operator": Counter(), "entity_check": Counter(), "var_check": Counter(),
        "criteria_operator": Counter(), "negate_true": Counter(), "extend_definition": Counter(),
        "local_var_functions": Counter(), "external_variables": [], "var_ref_entities": Counter(),
        "filter": Counter(), "set_operator": Counter(), "regexes": [],
        "criteria_depth_rule_def": 0, "criteria_depth_max": 0, "definitions": [],
    }
    # which states are used by tests (comparison) vs by object <filter> (collector-side selection)
    test_states, filter_states = set(), set()
    for el in root.iter():
        if not isinstance(el.tag, str):
            continue
        loc = etree.QName(el).localname
        if loc == "state" and el.get("state_ref"):
            test_states.add(el.get("state_ref"))
        if loc == "filter" and el.text:
            filter_states.add(el.text.strip())
    f["states_used_by_tests"] = len(test_states)
    f["states_used_by_filters"] = len(filter_states)
    for k in ("op_state_test", "op_state_filter", "datatype_state_test"):
        f[k] = Counter()
    for el in root.iter():
        if not isinstance(el.tag, str):
            continue
        ln = lname(el)
        local = etree.QName(el).localname
        if local == "definition":
            f["definitions"].append(el.get("id"))
            crit = [c for c in el if isinstance(c.tag, str) and etree.QName(c).localname == "criteria"]
            d = (1 + criteria_depth(crit[0])) if crit else 0
            f["criteria_depth_max"] = max(f["criteria_depth_max"], d)
            if el.get("id") == rule_id:
                f["criteria_depth_rule_def"] = d
        if local.endswith("_test"):
            f["test_types"][ln] += 1
            f["check"][el.get("check", "(absent)")] += 1
            f["check_existence"][el.get("check_existence", "(absent=at_least_one_exists)")] += 1
            if el.get("state_operator"):
                f["state_operator"][el.get("state_operator")] += 1
        elif local.endswith("_object"):
            f["object_types"][ln] += 1
        elif local.endswith("_state"):
            f["state_types"][ln] += 1
        elif local == "criteria":
            f["criteria_operator"][el.get("operator", "AND(default)")] += 1
        if el.get("negate") == "true":
            f["negate_true"][local] += 1
        if local == "extend_definition":
            f["extend_definition"][el.get("definition_ref")] += 1
        if local == "external_variable":
            f["external_variables"].append(el.get("id"))
        if local == "local_variable":
            f.setdefault("local_variables", []).append(el.get("id"))
            # record simple concat(literal|external var) definitions so regexes can be resolved
            kids = [k for k in el if isinstance(k.tag, str)]
            if len(kids) == 1 and etree.QName(kids[0]).localname == "concat":
                comps = []
                for k in kids[0]:
                    if not isinstance(k.tag, str):
                        continue
                    kl = etree.QName(k).localname
                    if kl == "literal_component":
                        comps.append(["literal", k.text or ""])
                    elif kl == "variable_component":
                        comps.append(["var", k.get("var_ref")])
                    else:
                        comps = None
                        break
                if comps is not None:
                    f.setdefault("simple_concat_vars", {})[el.get("id")] = comps
        if local == "filter":
            f["filter"][el.get("action", "exclude(default)")] += 1
        if local == "set" and el.get("set_operator"):
            f["set_operator"][el.get("set_operator")] += 1
        # local_variable function elements
        anc = [etree.QName(a).localname for a in el.iterancestors() if isinstance(a.tag, str)]
        if "local_variable" in anc and local in {
                "arithmetic", "concat", "count", "regex_capture", "substring", "split", "unique",
                "time_difference", "escape_regex", "begin", "end", "glob_to_regex"}:
            f["local_var_functions"][local + (":" + el.get("arithmetic_operation") if el.get("arithmetic_operation") else "")] += 1
            if local == "regex_capture" and el.get("pattern") is not None:
                f["regexes"].append({"side": "variable(regex_capture)", "entity": "regex_capture",
                                     "regex": el.get("pattern")})
        # entity-level attributes
        parent = el.getparent()
        if parent is not None and isinstance(parent.tag, str):
            pl = etree.QName(parent).localname
            side = "object" if pl.endswith("_object") else "state" if pl.endswith("_state") else None
            st_use = None
            if side == "state":
                sid = parent.get("id")
                st_use = "test" if sid in test_states else "filter" if sid in filter_states else "unused"
            if el.get("operation") and side:
                op = el.get("operation")
                (f["op_object"] if side == "object" else f["op_state"])[op] += 1
                if side == "state":
                    f["datatype_state"][el.get("datatype", "string(default)")] += 1
                    if st_use in ("test", "filter"):
                        f["op_state_" + st_use][op] += 1
                    if st_use == "test":
                        f["datatype_state_test"][el.get("datatype", "string(default)")] += 1
                if el.get("var_ref"):
                    f["var_ref_entities"][side] += 1
                rside = side if side == "object" else "state(" + st_use + ")"
                if op == "pattern match" and not el.get("var_ref") and el.text is not None:
                    f["regexes"].append({"side": rside, "entity": local, "parent": lname(parent),
                                         "regex": el.text})
                elif op == "pattern match" and el.get("var_ref"):
                    f["regexes"].append({"side": rside, "entity": local, "parent": lname(parent),
                                         "regex": None, "var_ref": el.get("var_ref")})
            elif el.get("operation"):
                f["op_other"][pl + ":" + local + ":" + el.get("operation")] += 1
            elif side == "state" and len(el) == 0 and (el.text is not None or el.get("var_ref")):
                f["op_state"]["equals(default)"] += 1
                f["datatype_state"][el.get("datatype", "string(default)")] += 1
                if st_use in ("test", "filter"):
                    f["op_state_" + st_use]["equals(default)"] += 1
                if st_use == "test":
                    f["datatype_state_test"][el.get("datatype", "string(default)")] += 1
                if el.get("var_ref"):
                    f["var_ref_entities"][side] += 1
            elif side == "object" and len(el) == 0 and (el.text or el.get("var_ref")) and local not in ("filter", "set", "behaviors"):
                f["op_object"]["equals(default)"] += 1
            if side and el.get("entity_check"):
                f["entity_check"][el.get("entity_check")] += 1
            if side and el.get("var_check"):
                f["var_check"][el.get("var_check")] += 1
    return f


def counter_json(obj):
    if isinstance(obj, Counter):
        return dict(obj)
    if isinstance(obj, dict):
        return {k: counter_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [counter_json(x) for x in obj]
    return obj


def main():
    scripts_dir, root, sel_path, out_path = sys.argv[1:5]
    env = CacEnv(root, PRODUCT)
    sel = json.load(open(sel_path))
    templates_dir = os.path.join(root, "shared/templates")
    records = {}
    for rid in sel["union_rules"]:
        rdir = os.path.join(root, sel["rule_dirs"][rid][0])
        rec = {"rule_dir": sel["rule_dirs"][rid][0], "controls": sel["control_ids_per_rule"][rid]}
        raw_rule = open(os.path.join(rdir, "rule.yml")).read()
        rendered = env.render_file(os.path.join(rdir, "rule.yml"), {"rule_id": rid})
        try:
            ry = yaml.safe_load(rendered)
        except Exception as e:
            ry = {}
            rec["rule_yaml_error"] = repr(e)[:200]
        rec["title"] = ry.get("title")
        tpl = ry.get("template") or None
        rec["template"] = tpl
        rec["platform"] = ry.get("platform") or ry.get("platforms")
        rec["xccdf_value_refs_rule_yml"] = sorted(set(
            re.findall(r"xccdf_value\(\s*[\"']([\w-]+)[\"']", raw_rule)
            + re.findall(r'<sub idref="([\w-]+)"', rendered)))
        # templated OVAL availability
        tpl_oval = False
        if tpl:
            tname = tpl.get("name")
            tdir = os.path.join(templates_dir, tname)
            tyml = os.path.join(tdir, "template.yml")
            langs = []
            if os.path.exists(tyml):
                langs = (yaml.safe_load(open(tyml)) or {}).get("supported_languages", [])
            backends = (tpl.get("backends") or {})
            oval_off = str(backends.get("oval", "on")).lower() == "off"
            tpl_oval = ("oval" in langs) and not oval_off
            rec["template_supports_oval"] = "oval" in langs
            rec["template_oval_backend_off"] = oval_off
        # static OVAL
        static = None
        for cand in oval_candidates(rdir):
            text = env.render_file(cand, {"rule_id": rid, "rule_title": rec["title"], "products": {PRODUCT}})
            if "<definition" not in text:  # renders empty for this product -> no applicable definition
                rec.setdefault("static_oval_not_applicable", []).append(os.path.relpath(cand, root) + " (renders empty)")
                continue
            plats = set(re.findall(r"<platform>\s*([^<]+?)\s*</platform>", text))
            if plats and not (plats & APPLICABLE_PLATFORMS):
                rec.setdefault("static_oval_not_applicable", []).append(os.path.relpath(cand, root))
                continue
            static = (cand, text)
            break
        sce = os.path.isdir(os.path.join(rdir, "sce"))
        rec["has_sce"] = sce
        if static:
            rec["mechanism"] = "static_oval"
            rec["static_oval_file"] = os.path.relpath(static[0], root)
            try:
                rec["oval"] = counter_json(analyse_oval(static[1], rid))
            except Exception as e:
                rec["oval_parse_error"] = repr(e)[:300]
        elif tpl_oval:
            rec["mechanism"] = "template"
        elif sce:
            rec["mechanism"] = "sce_only"
        else:
            rec["mechanism"] = "no_automated_check"
        rec["template_name"] = tpl.get("name") if tpl else None
        records[rid] = rec
    json.dump({"macro_errors": env.macro_errors, "rules": records}, open(out_path, "w"), indent=1)
    c = Counter(r["mechanism"] for r in records.values())
    print(c)
    print("parse errors:", [k for k, r in records.items() if "oval_parse_error" in r])
    print("yaml errors:", [k for k, r in records.items() if "rule_yaml_error" in r])
    print(Counter(r["template_name"] for r in records.values() if r["mechanism"] == "template").most_common())


if __name__ == "__main__":
    main()
