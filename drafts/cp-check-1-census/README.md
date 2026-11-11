# CP-CHECK-1 comparator census

How declarative checks are written where they already exist, measured to
justify (or correct) the eleven comparators of `drafts/CP-CHECK-1.md` §6.
The findings are summarised in that proposal's §2.2; this folder holds the
raw counts and the scripts that produce them.

| File | Content |
|---|---|
| `census-results.json` | every count in CP-CHECK-1 §2.2, plus a fit class and a one-line reason **per rule** (510 rules) and per template |
| `scripts/run_all.sh` | re-runs the whole census into `census-results.json` |
| `scripts/fit_judgement.py` | the judgement calls (fit classes), kept apart from the mechanical counts |
| `scripts/iregexp.py` | the I-Regexp checker used to classify regexes (independent of the validator's engine) |
| `scripts/*.py` | rule selection, OVAL/template parsing, kube-bench parsing, assembly |

## Sources (not included - clone them to re-run)

| Corpus | Repository | Commit | Licence (read from `LICENSE`) |
|---|---|---|---|
| ComplianceAsCode, product `ubuntu2404`, the four CIS profiles | https://github.com/ComplianceAsCode/content | `f0d40648d1bd0818116d24cad7c88578375990ab` | BSD-3-Clause |
| kube-bench, `cfg/cis-1.12` (+ `cfg/cis-2.0`, all 51 `cfg` directories for operators and regexes) | https://github.com/aquasecurity/kube-bench | `e278a5915a982f2756026de6e2f9ca77077ef9f9` | Apache-2.0 |
| I-Regexp grammar (`iregexp.abnf`) | https://github.com/ietf-wg-jsonpath/iregexp | `edceaa5ea0c433bd3bdcbd1ddeb6a2d82d09cd25` | IETF Trust |

`run_all.sh` expects them beside `scripts/`: `src/cac`, `src/kube-bench`,
`src/rfc/iregexp.abnf`. The scripts run with `python3 -I` and never import
or run ComplianceAsCode's Python: `cacenv.py` reads its constants with
`ast.literal_eval` and renders its Jinja macros in Jinja2's
`SandboxedEnvironment`. They need PyYAML, Jinja2 and lxml.

## Evidence tiers

- **Measured, mechanical:** rule selection, check mechanism per rule, OVAL
  test types, operations, criteria operators and depth, regex counts and
  their I-Regexp classification, XCCDF Value use, kube-bench operators.
  The kube-bench `cis-1.12` operator table was recounted with a separate
  script and matched exactly (2026-11-11).
- **Judgement:** the fit class of each rule (`fits`, `needs-arithmetic`,
  `needs-OR`, cross-fact, version ordering, regex outside I-Regexp).
  Templates were judged once each. Read `fit_judgement.py` before quoting
  the 481/510.
- **Not verified:** the published RFC 9485 text (rfc-editor.org was not
  reachable from the measuring environment); the grammar is the working
  group's ABNF at the commit above.
