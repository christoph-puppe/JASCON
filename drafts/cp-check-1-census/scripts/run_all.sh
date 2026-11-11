#!/usr/bin/env bash
# Reproduce census-results.json. Run from anywhere; paths are relative to this script's parent.
# Sources (already cloned, sparse): src/cac @ ComplianceAsCode/content, src/kube-bench @ aquasecurity/kube-bench,
# src/rfc/iregexp.abnf from ietf-wg-jsonpath/iregexp.
set -euo pipefail
C="$(cd "$(dirname "$0")/.." && pwd)"
S="$C/scripts"; W="$C/work"; mkdir -p "$W"
CAC_COMMIT=$(git -C "$C/src/cac" rev-parse HEAD)
KB_COMMIT=$(git -C "$C/src/kube-bench" rev-parse HEAD)
IR_COMMIT=edceaa5ea0c433bd3bdcbd1ddeb6a2d82d09cd25   # git ls-remote of ietf-wg-jsonpath/iregexp HEAD at fetch time
python3 -I "$S/select_rules.py" "$C/src/cac" "$W/selection.json"
python3 -I "$S/cac_rules.py" "$S" "$C/src/cac" "$W/selection.json" "$W/rules.json"
python3 -I "$S/cac_regex.py" "$S" "$W/rules.json" "$W/regex_cac.json" "$C/src/cac" "$W/selection.json"
python3 -I "$S/kube_bench.py" "$S" "$C/src/kube-bench/cfg/cis-1.12" "$C/src/kube-bench/cfg/cis-2.0" "$W/kube_bench.json"
python3 -I "$S/kube_bench.py" "$S" $(ls -d "$C"/src/kube-bench/cfg/*/) "$W/kube_bench_alldirs.json" >/dev/null
python3 -I "$S/census.py" "$S" "$W" "$C/census-results.json" "$CAC_COMMIT" "$KB_COMMIT" "$IR_COMMIT"
