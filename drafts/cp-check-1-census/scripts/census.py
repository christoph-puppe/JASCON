#!/usr/bin/env python3
"""Assemble census-results.json from the intermediate files.

Usage: python3 -I census.py <scripts_dir> <work_dir> <out_json> <cac_commit> <kb_commit> <iregexp_commit>
"""
import json
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, sys.argv[1])
from fit_judgement import judge, TEMPLATE  # noqa: E402

work, out_path = sys.argv[2], sys.argv[3]
cac_commit, kb_commit, ir_commit = sys.argv[4:7]
sel = json.load(open(os.path.join(work, "selection.json")))
rules = json.load(open(os.path.join(work, "rules.json")))["rules"]
rx = json.load(open(os.path.join(work, "regex_cac.json")))
kb = json.load(open(os.path.join(work, "kube_bench.json")))
kb_all = json.load(open(os.path.join(work, "kube_bench_alldirs.json")))


def resolve(vars_, product="ubuntu2404"):
    out = {k: v for k, v in (vars_ or {}).items() if "@" not in k}
    for k, v in (vars_ or {}).items():
        if "@" in k and k.split("@", 1)[1] == product:
            out[k.split("@", 1)[0]] = v
    return out


# ---------------------------------------------------------------- mechanism / templates
mech = Counter(r["mechanism"] for r in rules.values())
tmpl = Counter(r["template_name"] for r in rules.values() if r["mechanism"] == "template")
shadowed = Counter(r["template_name"] for r in rules.values() if r["mechanism"] == "static_oval" and r["template_name"])
static_files = Counter(os.path.basename(r["static_oval_file"]) for r in rules.values() if r["mechanism"] == "static_oval")

# ---------------------------------------------------------------- hand-written OVAL aggregation
keys = ["test_types", "object_types", "state_types", "op_object", "op_state", "op_state_test", "op_state_filter",
        "datatype_state_test", "check", "check_existence", "state_operator", "var_check", "criteria_operator",
        "negate_true", "extend_definition", "local_var_functions", "filter", "set_operator", "var_ref_entities"]
agg = {k: Counter() for k in keys}
depth = Counter()
rules_with = Counter()
for rid, r in rules.items():
    if r["mechanism"] != "static_oval":
        continue
    o = r["oval"]
    for k in keys:
        agg[k].update(o.get(k, {}))
    depth[o["criteria_depth_rule_def"]] += 1
    if o["criteria_operator"].get("OR") or o["criteria_operator"].get("XOR"):
        rules_with["criteria OR/XOR"] += 1
    if o["negate_true"]:
        rules_with["negate=true"] += 1
    if any(k.startswith("arithmetic") or k in ("count", "time_difference") for k in o["local_var_functions"]):
        rules_with["local_variable arithmetic/count/time_difference"] += 1
    if o["local_var_functions"]:
        rules_with["any local_variable function"] += 1
    if o["external_variables"]:
        rules_with["external_variable (XCCDF Value)"] += 1
    if o["extend_definition"]:
        rules_with["extend_definition"] += 1
    if o["op_state_test"].get("pattern match"):
        rules_with["state(test) pattern match"] += 1
    if not o["op_state_test"]:
        rules_with["no state on any test (existence-only tests)"] += 1
    if o["state_operator"].get("OR"):
        rules_with["state_operator OR"] += 1
    if o["check"].get("at least one") or o["check"].get("none satisfy"):
        rules_with["check at least one / none satisfy"] += 1
    if o["check_existence"].get("only_one_exists"):
        rules_with["check_existence only_one_exists"] += 1

# ---------------------------------------------------------------- variables (step 5)
TEMPLATE_VAR = {  # mechanical rule on resolved template vars -> uses an XCCDF Value in the check
    "sysctl": lambda v: not v.get("sysctlval"),
    "accounts_password": lambda v: True,
    "sshd_lineinfile": lambda v: bool(v.get("xccdf_variable")),
    "audit_rules_watch": lambda v: str(v.get("path_is_variable", "")).lower() == "true",
    "pam_account_password_faillock": lambda v: bool(v.get("ext_variable")),
    "grub2_bootloader_argument": lambda v: bool(v.get("arg_variable")),
    "sudo_defaults_option": lambda v: bool(v.get("variable_name")),
    "pam_options": lambda v: any(isinstance(a, dict) and a.get("variable_name") for a in v.get("arguments", []) or []),
}
GUARD = {"package_installed_guard_var", "service_enabled_guard_var", "service_disabled_guard_var",
         "package_removed_guard_var"}
var_rules = {"static_oval_external_variable": [], "template_threshold_or_value_param": [],
             "template_guard_var_applicability_param": [], "rule_yml_text_mentions_only": []}
for rid, r in rules.items():
    uses = False
    if r["mechanism"] == "static_oval" and r["oval"]["external_variables"]:
        var_rules["static_oval_external_variable"].append(rid)
        uses = True
    if r["mechanism"] == "template":
        v = resolve(r["template"].get("vars"))
        t = r["template_name"]
        if t in GUARD:
            var_rules["template_guard_var_applicability_param"].append(rid)
            uses = True
        elif t in TEMPLATE_VAR and TEMPLATE_VAR[t](v):
            var_rules["template_threshold_or_value_param"].append(rid)
            uses = True
    if not uses and r["xccdf_value_refs_rule_yml"]:
        var_rules["rule_yml_text_mentions_only"].append(rid)
var_counts = {k: len(v) for k, v in var_rules.items()}
check_uses_param = len(var_rules["static_oval_external_variable"]) + len(var_rules["template_threshold_or_value_param"]) + len(var_rules["template_guard_var_applicability_param"])

# ---------------------------------------------------------------- fit classes (judgement)
fit = {}
for rid, r in rules.items():
    c, why, cav = judge(rid, r)
    fit[rid] = {"class": c, "why": why, "caveat": cav, "mechanism": r["mechanism"],
                "template": r["template_name"]}
fit_counts = Counter(v["class"] for v in fit.values())
fit_by_mech = defaultdict(Counter)
for v in fit.values():
    fit_by_mech[v["mechanism"]][v["class"]] += 1
guard_caveat = sum(1 for v in fit.values() if v["template"] in GUARD and v["mechanism"] == "template")
caveated = sum(1 for v in fit.values() if v["caveat"]) + guard_caveat

# mechanical proxy: static rules whose definition uses OR/XOR, arithmetic, etc. (to compare with judgement)
mech_proxy = {
    "static_rules_with_OR_or_XOR_criteria": rules_with["criteria OR/XOR"],
    "of_which_judged_needs_OR": sum(1 for rid, r in rules.items() if r["mechanism"] == "static_oval"
                                    and (r["oval"]["criteria_operator"].get("OR") or r["oval"]["criteria_operator"].get("XOR"))
                                    and fit[rid]["class"] == "needs-OR"),
}

# ---------------------------------------------------------------- op mapping
op_map_cac = {
    "equals": "equals",
    "not equal": "no equivalent (matches-not on an escaped literal, or a numeric bound)",
    "case insensitive equals": "no equivalent (collector lower-cases, then equals)",
    "greater than": "at-least n+1 (integers only); no equivalent for decimals",
    "greater than or equal": "at-least",
    "less than": "at-most n-1 (integers only)",
    "less than or equal": "at-most",
    "pattern match (state used by test)": "matches (whole-value; edge anchors dropped, unanchored ends padded with .*)",
    "pattern match (object / filter state / regex_capture)": "collector side: no comparator needed",
    "bitwise and / bitwise or": "subset-of / includes-all on a permission-flag set the collector emits; with a parameter mask: no equivalent",
    "check_existence none_exist": "absent",
    "check_existence at_least_one_exists / any_exist / all_exist": "present",
    "check_existence only_one_exists": "no equivalent (cardinality = 1)",
    "check all": "implicit (assertion holds for every repeated fact)",
    "check at least one": "no equivalent (existential over repeated facts)",
    "check none satisfy": "matches-not / excludes-all",
    "state_operator OR": "one-of when the entities are the same fact; else no equivalent",
    "criteria OR / XOR": "no equivalent (applies-when or collector normalisation absorbs most)",
    "negate=true": "no equivalent (absent / matches-not / excludes-all cover negated atoms)",
    "local_variable arithmetic / count / time_difference / unique": "no equivalent",
}
op_map_kb = {
    "eq": "equals", "noteq": "no equivalent (matches-not on an escaped literal)",
    "gt": "at-least n+1 (integers)", "gte": "at-least", "lt": "at-most n-1 (integers)", "lte": "at-most",
    "has": "includes-all [v] if the collector splits the comma list; strictly it is substring (strings.Contains) = matches .*v.*",
    "nothave": "excludes-all [v] (list) / matches-not .*v.* (substring)",
    "regex": "matches (Go RE2 MatchString is a search: pad unanchored ends)",
    "valid_elements": "subset-of", "bitmask": "subset-of on permission flags ((max & actual) == actual)",
    "set: false": "absent", "set: true / default, no compare": "present",
    "bin_op and / absent": "conjunction", "bin_op or": "no equivalent",
}

# what comparison-side (state used by a test) regexes actually express (mechanical)
import re as _re
intent = Counter()
intent_rules = defaultdict(set)
for it in rx["items"]:
    if not it["side"].startswith("state(test") or it.get("regex") is None:
        continue
    core = _re.sub(r"^\(\?i\)", "", it["regex"])
    anchored = core.startswith("^") and core.endswith("$") and not core.endswith("\\$")
    core = core[1:] if core.startswith("^") else core
    core = core[:-1] if core.endswith("$") and not core.endswith("\\$") else core
    core = core[1:-1] if core.startswith("(") and core.endswith(")") and core.count("(") == 1 else core
    lit = r"(?:[A-Za-z0-9_@!,=/ -]|\\[.*+?])+"
    if _re.fullmatch(lit, core):
        k = "single literal, anchored (= equals)" if anchored else "single literal, unanchored (= substring)"
    elif _re.fullmatch(lit + r"(?:\|" + lit + ")+", core):
        k = "literal alternation, anchored (= one-of)" if anchored else "literal alternation, unanchored (= substring one-of)"
    else:
        k = "genuine pattern"
    intent[k] += 1
    intent_rules[k].add(it["rule"])
regex_intent = {"entities": dict(intent), "rules": {k: sorted(v) for k, v in intent_rules.items()}}

kb12 = kb["cis-1.12"]
kb_ops_all = Counter()
kb_binop_all = Counter()
for v in kb_all.values():
    kb_ops_all.update(v["compare_op"])
    kb_binop_all.update(v["bin_op"])
kb_regex_all = [r for v in kb_all.values() for r in v["regex_items"]]

results = {
    "generated_by": "scripts/run_all.sh",
    "sources": {
        "complianceascode": {"repo": "https://github.com/ComplianceAsCode/content", "commit": cac_commit,
                             "licence_file": "LICENSE", "licence_read": "SPDX license identifier: BSD-3-Clause (first line of LICENSE)",
                             "profiles": sel["profiles"], "controls_files": sel["controls_files"],
                             "rule_paths": "linux_os/guide/**/<rule_id>/rule.yml, oval/{ubuntu2404,ubuntu,shared}.xml, sce/",
                             "templates": "shared/templates/<name>/"},
        "kube_bench": {"repo": "https://github.com/aquasecurity/kube-bench", "commit": kb_commit,
                       "licence_file": "LICENSE", "licence_read": "Apache License, Version 2.0, January 2004",
                       "measured_dir": "cfg/cis-1.12", "also_measured": "cfg/cis-2.0 and all 51 cfg dirs (ops/regex only)",
                       "semantics_from": "check/test.go, check/check.go"},
        "iregexp": {"rfc": "RFC 9485", "note": "www.rfc-editor.org refused by the sandbox egress proxy (403); grammar taken from the RFC's source repo",
                    "repo": "https://github.com/ietf-wg-jsonpath/iregexp", "commit": ir_commit,
                    "files": ["iregexp.abnf", "draft-ietf-jsonpath-iregexp.md"]},
    },
    "cac": {
        "selection": {"rules_per_profile": sel["rules_per_profile_count"], "union_rules": sel["union_rule_count"],
                      "control_status_counts_per_profile": sel["control_status_counts_per_profile"],
                      "excluded_by_profile": ["zipl_audit_argument", "zipl_audit_backlog_limit_argument"]},
        "check_mechanism_rules": dict(mech),
        "rules_per_template": dict(tmpl.most_common()),
        "templates_used": len(tmpl),
        "static_oval_shadowing_a_template": dict(shadowed),
        "static_oval_file_used": dict(static_files),
        "static_rules_with_both_static_oval_and_sce": sum(1 for r in rules.values() if r["mechanism"] == "static_oval" and r["has_sce"]),
        "hand_written_oval": {k: dict(v.most_common()) for k, v in agg.items()},
        "hand_written_oval_criteria_depth_of_rule_definition": dict(sorted(depth.items())),
        "hand_written_oval_rules_with": dict(rules_with),
        "regex": rx["summary"],
        "regex_comparison_side_intent": regex_intent,
        "variables": {"counts": var_counts, "rules_whose_check_uses_a_parameter": check_uses_param,
                      "rules_with_literal_expected_only": len(rules) - check_uses_param,
                      "rule_lists": var_rules},
        "fit_classes_JUDGEMENT": {"counts": dict(fit_counts), "by_mechanism": {k: dict(v) for k, v in fit_by_mech.items()},
                                  "fits_verdicts_with_caveat": caveated,
                                  "template_reasoning": {k: v[1] for k, v in TEMPLATE.items()},
                                  "mechanical_proxy": mech_proxy, "per_rule": fit},
        "op_mapping": op_map_cac,
    },
    "kube_bench": {
        "cis-1.12": {k: kb12[k] for k in kb12 if k not in ("regex_items",)},
        "cis-2.0_identical_counts": {k: kb["cis-2.0"][k] == kb12[k] for k in ("bin_op", "compare_op", "set_values", "check_shapes")},
        "all_cfg_dirs": {"dirs": len(kb_all), "compare_op": dict(kb_ops_all.most_common()), "bin_op": dict(kb_binop_all.most_common()),
                         "regex": {"n": len(kb_regex_all), "tiers": dict(Counter(r["tier"] for r in kb_regex_all)),
                                   "features": dict(Counter(f for r in kb_regex_all for f in r["features_unique"])),
                                   "dirs_with_regex": [k for k, v in kb_all.items() if v["regex_items"]]}},
        "op_mapping": op_map_kb,
    },
}
json.dump(results, open(out_path, "w"), indent=1, default=str)
print("mechanism", dict(mech))
print("fit", dict(fit_counts), {k: dict(v) for k, v in fit_by_mech.items()}, "caveated", caveated)
print("vars", var_counts, "check uses param", check_uses_param)
print("rules_with", dict(rules_with))
print("mech proxy", mech_proxy)
print("regex intent", regex_intent)
print("UNJUDGED", [k for k, v in fit.items() if v["class"] == "UNJUDGED"])
print("static defaulted to fits:", sorted(k for k, v in fit.items() if v["mechanism"] == "static_oval" and v["class"] == "fits"))
