# CP-CHECK-1 — Check as the eleventh kernel type

**Change proposal · JASCON kernel 2.0.0-rc.1 → 2.0.0 · 2026-11-11**
**Process:** Chapter 15.4 (evidence in, corpus first, implementations follow). Every rule carries a machine id, a rationale and a failure message that prints on failure.
**Scope:** kernel schema, reference validator, conformance corpus, example bundle, one stdlib facet. Handbook, specification, SKILL.md, reader and PowerShell twin: §10, after the author's review of this proposal.
**Status (2026-11-11): PROPOSED, on branch `claude/focused-lovelace-rfcofx`, NOT released.** The schema, the validator, 156 vectors and the worked example are in the repository and green under `validate_core.py`. The PowerShell twin is not ported. Evidence tier of the promotion: D22 test 1 **fails** (0 of 3 census corpora), test 3 **measured on two non-census corpora** (§2.2: 481 of 510 CIS-profile rules fit; one operator gap, not-equal) — test 1 is the problem §8 puts to the author.

**Author decisions this proposal implements (2026-11-10/11):** (1) a check is a new kernel type, not a facet; (2) pass or fail is declarative only — code collects facts, a closed set of comparators decides, what does not fit stays manual; (3) **regex is part of that set**; (4) first slice Linux host via bash; (5) first deliverable is this proposal plus model, example and vectors, no runner and no generator.

---

## 1. The gap, in one sentence

JASCON can say *that* a requirement was assessed and *what* the assessor concluded, and cannot say *how a machine decides it*: `Assessment.method` is an untyped object, `assessment-criteria@1` carries the CIS audit as prose, and nothing in the graph holds the code that observes, the definition of which observation passes, or the evidence that lets a second party reach the same verdict without trusting the first.

The consequence is measured in the corpus: the CIS Ubuntu 24.04 Benchmark marks **291 of 312 rules automated** (`converted_examples/CIS.Ubuntu2404/cisb-coverage-report.md`:16), and every one of them arrives in JASCON as an `audit` string a human must read. The automation exists at the publisher; it does not survive the conversion, because there is nowhere to put it.

## 2. The counts

### 2.1 What the JASCON corpora carry today

| Corpus | Where checks live | Machine-decidable? |
|---|---|---|
| CIS Ubuntu 24.04 Benchmark (not redistributed) | `assessment-criteria@1.audit` ×312 (shell excerpts in prose), `method` automated ×291 / manual ×21 | no — prose; the pass condition is in the audit text ("verify the output is …") |
| FedRAMP CR26 (not redistributed) | `assessment-criteria@1.examples[].key-tests` ×15, `examples` ×24 | no — prose key tests |
| BSI GS++, ISM, SP 800-53 | `required-documentation`, 800-53A `objectives` / `methods` (EXAMINE · INTERVIEW · TEST) | no — methods are named, not specified |
| US IFA (OSCAL AP/AR) | `observations@1` framework facet + `evidence-refs` URIs | no — observations are results, not checks |

**Census authorities encoding a machine-decidable check: 0 of 3.** D22 test 1 fails as written (§8).

### 2.2 How declarative checks are written where they already exist

The comparator set (§6) was drafted before it was measured. The census below counts what two open, redistributable check corpora actually use. Scripts and raw counts: `drafts/cp-check-1-census/` (re-run with `run_all.sh` against the two commits named there). The kube-bench `cis-1.12` operator table was recounted independently with a separate script and matched exactly.

**Sources.** ComplianceAsCode/content at `f0d40648` (BSD-3-Clause, read from `LICENSE`), product `ubuntu2404`, the four CIS profiles (`cis_level{1,2}_{server,workstation}`, resolved through `controls/cis_ubuntu2404.yml`): L1 server 408 rules, L1 workstation 399, L2 server 510, L2 workstation 507, **union 510**. aquasecurity/kube-bench at `e278a591` (Apache-2.0), `cfg/cis-1.12`: 103 automated and 28 manual checks (`cfg/cis-2.0` identical); operator and regex counts also over all 51 `cfg` directories. Semantics from kube-bench's `check/test.go`.

**How the 510 Ubuntu rules are checked:** template 366 (31 templates — file permissions/owner/group 129, audit rules 46, package removed/installed 44, sysctl 26, service disabled 23, mount options 26, …), hand-written OVAL 126, script only (SCE) 18.

**The comparison side is small; the logic is on the collection side.** In the 126 hand-written OVAL definitions (280 tests), the operations on *states* — what is compared — are: equals 99, pattern match 23, ≥ 18, ≤ 16, > 4, < 3, bitwise and/or 5, not equal 2, case-insensitive equals 1. The operations on *objects and filters* — how the value is found — are: equals 441, pattern match 398, ≥ 116, not equal 9. Criteria: AND 155, OR 57, XOR 2; `negate` 37 times in 23 rules; nesting depth 1 in 90 rules, up to 5 in one. 38 of the 43 rules that use OR or XOR use it for an applicability guard or for alternative configuration sources — collector work.

**Regex (491 patterns).**

| Side | n | inside I-Regexp | mechanically rewritable | outside | unresolved |
|---|---:|---:|---:|---:|---:|
| comparison (state used by a test) | 23 | 16 | 7 | **0** | 0 |
| extraction (object `<pattern>`) | 235 | 30 | 119 | 66 | 20 |
| file selection, filters, captures, template parameters | 233 | 180 | 46 | 2 | 5 |

Features outside I-Regexp, all on the extraction side: `\s` 142, `(?:` 86, `\d` 66, `\b` 35, `(?i)` 33, `\/` 29, `\S` 29, lookahead 24, lazy quantifiers 24. Of the 23 comparison patterns, 13 are unanchored (search semantics; whole-value needs `.*` padding) and 10 are an equals, substring or one-of written as a regex. kube-bench `cis-1.12` uses no regex at all; across all 51 directories, 15 (2 inside, 13 rewritable, 0 outside). **No comparison in either corpus needs a regex outside I-Regexp.** The regex power people miss lives where this design puts it: in the collector.

**Parameters.** 89 of 510 rules feed an XCCDF Value into the check: 36 through an OVAL external variable, 39 through a template threshold (sysctl 20, password policy 11, faillock 3, other 5), 14 as an applicability guard. The other 421 use literals or presence. This is the set the converter must turn into kernel parameters (§9 item 3).

**kube-bench `cis-1.12`.** `bin_op`: absent (= and) 77, or 21, and 5. Operators: eq 30, bitmask 16, has 7, nothave 7, gte 4, valid_elements 3, noteq 2; `set: false` (absence) 18, presence only 40. Of the 21 OR checks, 16 are "flag absent OR flag = value" — the default is compliant, which a collector reporting the *effective* value removes — 3 have a single item, 1 is "file not found OR root:root", and 1 (5.1.3) is a genuine OR across two facts. Across all 51 directories: noteq 85, gt 22, lte 1.

**Mapping onto the eleven comparators.** eq/equals → `equals`; gte/≥ → `at-least`; ≤ → `at-most`; valid_elements → `subset-of`; bitmask/bitwise → `subset-of` over a flag set the collector emits; `set: false`/none_exist → `absent`; existence → `present`; regex/pattern match → `matches`; "none satisfy" → `matches-not`. With a workaround: has/nothave → `includes-all`/`excludes-all` if the collector splits the list (in kube-bench they are substring tests); gt/lt → bound ± 1, integers only. **No equivalent:** not-equal, case-insensitive equals, "exactly one exists", OR/XOR/negate across facts, arithmetic. Zero *native* instances in both corpora: `one-of` and `matches-not` — both occur as idioms (`state_operator` OR, literal alternations; `check="none satisfy"`), so neither is deleted.

**Fit per rule (judgement, recorded rule by rule in the census JSON).**

| Class | Rules of 510 |
|---|---:|
| fits (23 of them only if the collector resolves effective values and emits mode bits as flag sets) | 481 (94 %) |
| needs arithmetic (counts, uniqueness, umask against a parameter, time against now, uid against UID_MIN) | 12 |
| needs a comparison between two facts (owner equals the user's uid; open ports covered by firewall rules) | 9 |
| needs OR across facts (sshd Allow/Deny ×4, server-or-pool, audit-log mode depends on log_group) | 6 |
| needs version ordering (dpkg EVR) | 2 |
| needs a regex outside I-Regexp | **0** |

The 29 misfits stay manual under decision (2), or a collector computes a derived fact — which moves logic out of the recomputable part and is therefore counted, not encouraged.

**What the census contradicts, and the answer this proposal gives:**

| Finding | Count | Answer |
|---|---:|---|
| No not-equal | OVAL state 2; kube-bench 85 across all directories (2 in cis-1.12) | **Open — author decision (§11 item 7).** For text, `matches-not` with the escaped literal already says it; for numbers nothing does. A twelfth comparator `not-equals` is measured and cheap. |
| No "exactly one exists" | 7 rules + 2 "exactly one service" | The collector emits a count; `equals 1`. Counting is extraction. |
| No version type | 2 rules (dpkg EVR) | Manual. A `version` fact type needs a second corpus and an ordering every tool implements identically. |
| Applicability by parameter | 14 rules (guard variables) | A parameter that switches a check on or off is **selection**: the Tailoring excludes the clause. Not `applies-when`. |
| List-valued parameters written as regex alternation (`"syslog\|single\|halt"`) | in the 89 | A `choice` parameter with `cardinality: many` and `one-of`, which CHECK-4 already accepts; the converter splits the alternation. |
| Per-resource implication ("invalid shell → account locked") | — | Already expressible: `each` + `applies-when` filters resources, the criteria hold for the rest (verdict vector "each + applies-when filters resources"). |
| Compliant defaults ("flag absent OR value") | 16 kube-bench, 6 sshd | The collector reports **effective** values (`sshd -T`, not the config file). This becomes a written part of the collector contract in `collector@1`. |
| Multi-line values | banners | `.` excludes `\n` and `\r`; whole-value over lines is `(.\|\n\|\r)*`. Stated in B.1.10. |

## 3. What goes in the kernel and what stays out

The line is drawn where tools must agree. Two conformant tools given the same Check and the same observation must return the same verdict; everything that can differ between honest tools without changing the verdict stays outside.

| Kernel (2.0.0) | Facet / outside |
|---|---|
| the requirement and clauses a check discharges | **collector code** — stdlib facet `collector@1`, on the Check |
| the platform under test (opaque URI) | runner, scheduler, retries, timeouts in practice |
| the fact contract: names, types, cardinality | target inventory, hostnames, credentials (never in a bundle) |
| the criteria: a flat AND over 11 comparators | evidence store backend (directory today, object store later) |
| applicability (`applies-when`), per-resource repetition (`each`) | LLM generation, review workflow, generator provenance detail |
| confidence + provenance of the check | scanner result import (SARIF, HDF, OCSF) |
| a run's rows: observation, outcome, parameters used, evidence digest | raw evidence bytes (beside the bundle, content-addressed) |

The decisive split is **collector versus criteria**. A collector is code and decides nothing; it prints one observation. The verdict is a pure function of the Check, the observation and the bound parameter values. That buys three things the exit-code style of most scanners cannot: a tailored parameter retunes the check without touching code; a verdict can be recomputed by anyone from the stored record; and the record shows *what was observed*, not only *that something failed*.

## 4. The shape (App. A.9c)

### 4.1 Check

Common A.0 fields plus:

| Field | | Type | Meaning |
|---|---|---|---|
| `requirement-ref` | ● | URI | The requirement the check discharges. **Resolves-if-present** (like a Mapping endpoint): a check pack may ship without a catalog it may not redistribute. When present in the bundle, the edge is typed and `statement-ids` must exist (CHECK-1). |
| `statement-ids` | ○ | [string] | The clauses covered. |
| `platform` | ● | URI | Platform under test, opaque. No closed platform list: platforms change faster than kernels. |
| `observes` | ● | [{name ●, type ●, cardinality ○, description ○}] | The fact contract. Types `string · integer · decimal · boolean · code`; `cardinality` `one` (default) or `many` (a list). Names unique (CHECK-2). |
| `criteria` | ● | [{fact ●, op ●, expected ○}] | Flat conjunction. `expected` is a literal of the fact's type or `{"param": "<name>"}`; `present` / `absent` take none (schema). |
| `applies-when` | ○ | same as `criteria` | False → not applicable. With `each`, a per-resource filter. |
| `each` | ○ | {resource ●, allow-empty ●} | The facts repeat per resource (accounts, files, buckets); the criteria hold for every one. `allow-empty` must be stated: an empty set passes only where the author said so. |
| `validity` | ○ | {num ●, unit ●} elapsed | How long a result stays fresh. Read-time only; nothing is mutated. |
| `confidence` | ● | code C.7 | `draft` (generated) · `reviewed` · `authoritative` (published by the requirement's authority). |
| `provenance` | ● | {author-ref ●, date ● (ISO 8601), derived-from ○ [{ref, digest}]} | Whose check this is; `derived-from` pins the source text a generator worked from. |

**Shape-disjointness:** `observes` + `criteria` occur in no other type; the eleven minimal objects each match one entry point (`run_lifecycle` MINIMAL).

### 4.2 Assessment gains two optional fields

- **`check-results`** ○ [row] — one row per check run: `check-ref` ●, `check-digest` ● (semantic digest of the Check), `collector-id` ○, `outcome` ● (`satisfied · not-satisfied · inconclusive · not-applicable`), `time` ● (RFC 3339), `parameters` ○ (the values the run was bound to), **`observation`** ○ inline *or* `observation-ref` ○ {ref, digest}, `evidence-record` ○ {ref, digest}, `reason` ○ text.
- **`tailoring-ref`** ○ URI — the Tailoring whose bound parameter values the run used (closure-required, typed: CHECK-12).

The observation sits inline by default, so the Assessment's semantic digest covers it and an Attestation that binds the Assessment binds what was observed. A large per-resource observation goes by reference with a digest.

### 4.3 Finding gains one optional field

**`check-ref`** ○ URI — the check that raised it. Typed if in-bundle and held to the same requirement and clause (CHECK-14).

### 4.4 The evidence record (a file, not an object)

`$defs/evidenceRecord`, in the kernel schema next to `scale` and `contentManifest`: `record-version` "1", `check-ref`, `check-digest`, `collector-id`, `subject-ref`, `target` (non-secret descriptor), `runner`, `started`, `finished`, `exit-status`, `observation-digest`, `outputs[]` {name, digest, media-type, size, redacted}, `redactions`, `note`.

The store is a directory beside the manifest, `evidence/sha256/<hex>`, every file named by the SHA-256 of its bytes. It is never listed in the manifest — the same placement as signature envelopes. The chain is:

```
Attestation ── subject semantic digest ──▶ Assessment
Assessment.check-results[i] ── observation (inline, covered by that digest)
                            └─ evidence-record {digest} ──▶ record
record ── observation-digest ──▶ the same observation
       └─ outputs[].digest ──▶ raw bytes (stdout, API responses)
```

Every link verifies offline. Redaction happens before hashing; raw output is a separate blob, so a retention delete leaves the record verifiable and the blob reported **withheld**, not failed.

### 4.5 `collector@1` (stdlib facet, declares `[]`)

`{collectors: [{id ●, runtime ●, source ●, privileges ○, timeout-seconds ○, description ○}]}`. `runtime` is `sh · bash · powershell · python · ansible · http-api` or a namespaced URI. Source is inline so the Check's digest covers the exact code. Declaration `[]` because nothing in it changes what passing means — the criteria do, and they are kernel; a tool that cannot run a runtime still validates, recomputes and renders.

## 5. The rules

Rules 1–7 hold a Check to its requirement and to itself; 8–14 hold a run to its Check; 15 is the evidence chain. All are graph rules in the reference validator; the shapes they rest on are schema.

| Id | Rule | Rationale | Failure message (abridged) |
|---|---|---|---|
| **CHECK-1** | An in-bundle `requirement-ref` is a Requirement; `statement-ids` name its statements. | The edge is typed; clause precision is addressable or it is prose. | `<check>: statement-id 's9' names no statement of <req> (CHECK-1: …)` |
| **CHECK-2** | Fact names are unique; every assertion reads a declared fact. | The fact contract is all a collector promises. | `<check>: criteria[1] reads fact 'sshd.permitrootlogin', which observes does not declare` |
| **CHECK-3** | The operator fits the fact's type and cardinality; a literal has the fact's type. | Ordering on numbers, patterns on text, set operators on lists. | `criteria[0]: at-least does not fit a code fact` |
| **CHECK-4** | `{param}` names a parameter declared exactly once on the covered clauses, with a fitting type; the requirement is in the bundle; a pattern is never a parameter. | Tailoring the requirement retunes the check (D9). A tailored pattern has no tightening direction anyone could verify. | `criteria[0]: binds parameter 'max-tries', declared 0 times on the covered statements` |
| **CHECK-5** | `at-most` never binds a parameter that tightens `higher`; `at-least` never one that tightens `lower`. | Tightening a parameter must never loosen the check. | `at-most against parameter 'max-auth-tries', which tightens higher - tightening it would loosen the check` |
| **CHECK-6** | `matches` / `matches-not` patterns are I-Regexp within the size limits. | Two conformant tools, one verdict, in bounded time. | `criteria[0]: escape \w is not I-Regexp (no \d \w \s \b, no back-references) at position 0 of '\\w+-cbc'` |
| **CHECK-7** | `collector@1` matches its schema; collector ids are unique. | A result row must be able to say which code observed. | `collector id 'bash' is used twice` |
| **CHECK-8** | A row's `check-ref` is a Check; `check-digest` matches it. | A changed check is a different check. | `check-results[0]: check-digest does not match <check> - the check changed after the run` |
| **CHECK-9** | A row's outcome equals `check-verdict` over its observation and parameters. | Verdicts are recomputed, never taken on trust. | `recorded satisfied, check-verdict computes not-satisfied (sshd.maxauthtries at-most 4: observed 5)` |
| **CHECK-10** | One row per check; `Assessment.result` is the aggregate of the rows. | An assessment mixing machine and human judgement is two assessments. | `result is satisfied, the aggregate of its check results is not-satisfied` |
| **CHECK-11** | A row without an observation is `inconclusive` and carries a `reason`. | No observation, no verdict. | `check-results[0]: no observation, yet the outcome is satisfied and no reason is given` |
| **CHECK-12** | `tailoring-ref` resolves to a Tailoring; each row's `parameters` equal what it binds. | An implementer does not set its own pass mark. | `the run used max-auth-tries=6, <tailoring> binds 4` |
| **CHECK-13** | A row's `collector-id` names a collector of the Check. | — | `collector-id 'python' names no collector of <check>` |
| **CHECK-14** | A Finding's in-bundle `check-ref` is a Check about the same requirement and a covered clause. | A finding raised by a check is about what that check discharges. | `statement-ref 's2' is not a clause check <check> covers` |
| **CHECK-15** | Evidence refs stay in the store; each digest verifies; a record names the row's check, digest, collector and an assessment subject, and binds the row's observation. Missing blobs are *withheld* (note), not failures. | Content addressing is the whole integrity story of evidence. | `output 'stdout' evidence/sha256/2d66… does not match its digest` |

**Notes, not failures:** a row whose Check is outside the bundle (*not recomputed*); a row with `parameters` but no `tailoring-ref` (*the performer's statement*); a withheld blob; a URI evidence ref (*not resolvable offline*).

## 6. The tenth primitive: `check-verdict` (B.1.10)

**Input:** a Check, one observation (`{facts}` or `{resources: [{id, facts}]}`), the bound parameter values. **Output:** `satisfied · not-satisfied · inconclusive · not-applicable`, with reasons.

### 6.1 The comparators

| Op | Fact | `expected` | Holds when |
|---|---|---|---|
| `equals` | one; any type | scalar or param | value equals expected (decimals by value) |
| `one-of` | one; string, code, integer, decimal | non-empty list or list param | value is in the list |
| `at-least` / `at-most` | one; integer, decimal | scalar or param | ordering; decimals by value, never as floats |
| `present` / `absent` | any | — | the key is / is not in the observation |
| `includes-all` | many | non-empty list | every listed value occurs |
| `excludes-all` | many | non-empty list | no listed value occurs |
| `subset-of` | many | list (may be empty) | every observed value is listed; `[]` means "must be empty" |
| `matches` / `matches-not` | string, code; one or many | I-Regexp literal | whole value matches / does not; on a list every element / no element |

No OR, no NOT, no nesting, no arithmetic, no paths, no cross-fact comparison — the leash of App. B.4 applied once more. Value alternatives are `one-of`; negation lives in the operator pairs.

### 6.2 Evaluation

1. No observation → `inconclusive`.
2. `applies-when`: false → `not-applicable`; unknown → `inconclusive`.
3. Each assertion: undeclared fact, unobserved fact, mistyped value, unbound parameter or mistyped bound value → `inconclusive`. **A default is never substituted** (D9).
4. Combination is **strong Kleene AND**: one `not-satisfied` decides; else one `inconclusive` decides; else `satisfied`. A definite failure is never hidden behind an unknown elsewhere.
5. `each`: resources whose `applies-when` is false are skipped; the rest combine by step 4. No applicable resource: `satisfied` if `allow-empty`, else `inconclusive`.
6. Aggregate over rows (CHECK-10): not-applicable rows are dropped; none left → `inconclusive`.

An absent key means *observed absent*: the collector looked and did not find it. A collector that could not look prints nothing, and the row has no observation. A collector reports **effective** values — defaults resolved, drop-in files merged — because the census shows that most cross-fact ORs in the wild are "setting absent OR setting = value", which an effective value collapses into one comparison.

Whole-value matching over several lines needs `(.|\n|\r)*`, since `.` excludes both line breaks.

### 6.3 Regex: I-Regexp, with the kernel fixing what dialects leave open

The author's decision is regex in the criteria. The risk it must not reintroduce is the old one from Appendix F Q1: two conformant tools, two verdicts. Python `re`, .NET and ECMAScript disagree on exactly the constructs people reach for — `\d` (ASCII or Unicode digits), `\w`, `\s`, `.` and `\r`, `^`/`$`, flags, lookaround — and backtracking engines can be stalled by a pattern.

The dialect is **I-Regexp, RFC 9485**: XSD regular expressions without class subtraction, multi-character escapes or Unicode blocks — built by the IETF for this purpose and already used by JSONPath (RFC 9535). The grammar implemented is the ABNF from the IETF JSONPath working group's repository (`iregexp.abnf`, commit `edceaa5e`); rfc-editor.org was not reachable from the build environment, so the RFC text itself was not compared line by line — §11 item 1.

The kernel fixes three things the RFC leaves to the host:

- **Whole value.** XSD semantics: the pattern must match the entire value. `^` and `$` are ordinary characters. `.` is any character except `\n` and `\r`.
- **Size limits.** Pattern ≤ 256 characters; compiled program ≤ 1,000 states (after `{m,n}` expansion); value ≤ 4,096 characters, else `inconclusive`.
- **No host engine.** The reference validator parses the ABNF itself and matches with a Thompson state-set simulation: linear in program × input, no backtracking. `(a*)*b` against 4,096 `a`s takes 0.01 s. The second implementation must not translate patterns into `System.Text.RegularExpressions` either; it ports the ~150-line engine. This is what makes the verdict independent of the host, not the syntax check alone.

One residual divergence is stated rather than hidden: `\p{…}` categories come from the host's Unicode database (Python 3.13: Unicode 15.1). A character assigned between two Unicode versions can be categorised differently by two tools. The vectors avoid such characters; a check that depends on them is fragile by construction.

## 7. Semver: rides 2.0.0

2.0.0 is untagged (spec IV.9 item 7), so Check rides the same major as Risk. The superset property holds and is measured: **every object of the five shipped corpus bundles and the example bundle validates unchanged** under the extended schema (ALL GREEN; the 3,729 objects of the baseline run, before the example gained its new files).

**KERNEL-1** extends: a bundle that carries a Check, an Assessment with `check-results` or `tailoring-ref`, or a Finding with `check-ref` must pin `kernel-version: "2.0.0"`. The pinned version does not change. Consequence, stated: a tool that implements **2.0.0-rc.1** claims 2.0.0 and will report a Check as "matches NO type". That is tolerable only because nothing has been released under 2.0.0. If Check does not land before the tag, it rides 3.0.0, and the pin does its job then.

## 8. D22 — a second exception, and the alternative not taken

### 8.1 The three tests, for the record

1. **≥ 2 of 3 census authorities encode it:** **fails** — 0 of 3 (§2.1).
2. **One shared computation every generic tool must perform:** **holds** — `check-verdict`, and it is the reason the kernel route exists at all (8.3).
3. **One vocabulary fits all corpora without flattening:** **holds with one recorded gap**, at evidence tier *measured on two non-census corpora, fit classes by judgement* (§2.2). 481 of 510 Ubuntu rules fit; every comparison operator both corpora use maps onto the set except not-equal (85 uses in kube-bench, 2 in OVAL), which is §11 item 7.

The specification records the Risk exception as "the precedent, and it is exactly one" (spec :807-822). Admitting Check makes it two in one release. That turns D22 from a rule with one recorded exception into a rule the author overrides when the consumer side needs it — which is the honest description, and the reason backlog #48 (a consumer-side clause for D22) can no longer stay open past the tag. **The author decides #48 before Check lands.**

### 8.2 The alternative

An independent design review during planning argued against a kernel type: put the criteria in a facet on a Requirement the check author owns, link it to the upstream catalog by a statement-scoped Mapping, carry collectors in a Component of kind `software`, and promote to the kernel once measured. That route costs the kernel nothing and keeps D22 intact.

### 8.3 Why the kernel route anyway

The spec answers it. Appendix B.4: *facets instantiate primitives with bound arguments and **never define new computation**.* A declarative verdict is new computation. Under the facet route, `check-verdict` would either be a kernel primitive anyway — at which point its input shape is kernel in all but name — or it would live in a facet, and every tool that does not know that facet must halt on every assessment (`modifies-semantics: ["assessment"]`), which is the opposite of interoperable automated assessment. The facet route also leaves the run record (`check-results`) without a home that the validator reads: `Assessment.method` payloads are not facet-validated today, and all three in the repository fail their own pinned schema (§12, backlog #55).

What the kernel route costs is real and belongs in the decision: a shape closed before a census covers more than one platform, so every correction after the tag costs a major.

## 9. What ships, what follows

**Ships with this proposal (green under `validate_core.py`):**

| Artifact | Change |
|---|---|
| `schemas/oscal-semantic-core-2.0.0.schema.json` | `$defs/check`, `checkFact`, `checkFactType`, `checkOp`, `checkAssertion`, `checkExpected`, `checkScalar`, `checkObservation`, `checkOutcome`, `checkResult`, `evidenceRecord`, `digestRef`, `date`, `dateTime`; `assessment.check-results`, `assessment.tailoring-ref`; `finding.check-ref`; title and description |
| `schemas/stdlib/collector-1.0.0.json` | the collector facet, `modifies-semantics: []` |
| `scripts/validate_core.py` | `check` in TYPES and MINIMAL; I-Regexp parser and state-set matcher; `check_verdict` (B.1.10); `check_aggregate`; CHECK-1..15; evidence chain over the store beside the bundle; KERNEL-1 extended; `run_check` |
| `conformance/check-vectors.json` | 37 regex, 51 verdict, 7 aggregate, 18 shape, 43 bundle vectors; each CHECK rule expected by at least one; 9 deliberate engine mutations each turn at least one vector red |
| `examples/` | LNX-SSH-1 (two clauses, one parameter), Set, production Tailoring, bastion host, two Checks (`at-most {param}`; `matches-not ".*-cbc"` on a list; bash + python collectors), two daily runs, the Finding, 7 evidence blobs, the pinned collector descriptor; the Risk gains `tailoring-refs` (RISK-14) |
| `.gitattributes` | evidence blobs are `-text` |

The worked example assessed no real host. Each run executed the Check's bash collector source unchanged against a stub `sshd` that prints a fixed configuration; every evidence record says so.

**Follows (named exits):**

1. **Step 1b, after the author's review:** handbook and specification deltas (§10), SKILL.md, `SKILL_jascon.zip`, README type count, the reader, the PowerShell twin.
2. **Phase 2 — runner and store, bash.** A prototype directory `assessments/` beside `risk-catalogs/`, so `jascon/scripts` stays free of subprocess and LLM code. `run` executes collectors on a target and writes evidence; `evaluate` recomputes verdicts; `verify-chain` walks the store. Verified in throwaway Ubuntu containers. Artifacts beyond stdout and stderr (a collector saving the full `sshd -T` dump) are designed there.
3. **Phase 3 — import.** From `assessment-criteria@1.audit` or prose. Deterministic first: join by reference id to an open corpus, translate its declarative tests, take XCCDF Values as parameters (the CIS converter mints none today — `convert_cis_benchmark.py`:91-93). LLM Maker only for the residual, schema-constrained; Checker in order: schema and lint, one compliant and one non-compliant fixture (a check that cannot fail is rejected), an empty filesystem diff (the real read-only guard; lint cannot prove it and audits often need root), agreement with an existing scanner, a second model without the Maker's reasoning, a human. Output lands as `confidence: draft`. KPI: the false-pass rate on held-out rules with known truth. CIS-derived output stays local.
4. **Phase 4 — more runtimes and platforms,** one at a time: Ansible and Python collectors for Linux, then Kubernetes (kind), AWS, GCP, Azure.
5. **Phase 5 — around it:** signed attestations over runs (also closes #46), OSCAL assessment-results export, scanner result import, freshness reporting from `validity`.

## 10. Handbook and specification deltas (step 1b, insert text)

### 10.1 SKILL.md
Requirement 1: "**eleven** shallow, globally identified objects (…, Risk, **Check**)". New **Requirement 9b: Automated assessment** — "Model a machine check as a `Check`: a typed fact contract (`observes`) and a flat conjunction over the eleven comparators (`criteria`, B.1.10), bound to the requirement's parameters with `{"param": …}`. Collector code rides the Check in `collector@1` and decides nothing. Record runs as `Assessment.check-results` with the observation inline; the validator recomputes every verdict (CHECK-9) and holds the parameters to the named Tailoring (CHECK-12). Patterns are I-Regexp (RFC 9485), whole-value. Evidence is content-addressed beside the bundle (CHECK-15)." Companion: the LNX-SSH-1 files, `conformance/check-vectors.json`.

### 10.2 Chapter 10 — new §10.7 "Checks: when the assessor is a machine"
> §10.2 said a verdict without published criteria is an opinion with a stamp. A machine verdict without published criteria is worse: an exit code. The `Check` publishes both halves. `observes` is the contract a collector must honour — fact names and types, nothing about how they are obtained. `criteria` is the pass condition, written in eleven comparators every conformant tool evaluates identically. Between them sits the collector: a shell script, an Ansible task, an API call, carried on the Check in `collector@1` so the check's digest covers the exact code, and deciding nothing.
>
> The payoff is in the run record. An Assessment carries one row per check, and the row carries the observation itself — `{"sshd.ciphers": ["…", "aes128-cbc"]}` — not just the outcome. A second party recomputes the verdict from that row without running anything, and the validator does exactly that for every row (CHECK-9). The parameter the row was bound to is held to the Tailoring the Assessment names (CHECK-12): tighten `max-auth-tries` from 6 to 4 in the Tailoring, and yesterday's observation of 5 turns from satisfied to not-satisfied without one line of code changing.
>
> > **Don't** let the code decide. A script that exits 0 or 1 hides its threshold, ignores the tailoring and leaves nothing to re-examine. The measured neighbour: 291 automated CIS rules whose pass condition reached JASCON as a sentence in an `audit` string.

### 10.3 Appendix A — A.9c (§4 above), plus A.7 `check-results`, `tailoring-ref`; A.8 `check-ref`; A.11 the evidence store.

### 10.4 Appendix B — B.1.10 `check-verdict` (§6), and B.4: "nine, eight and three" becomes "ten, eight and three"; the tenth arrived with vectors and one implementation.

### 10.5 Appendix C
- **C.12 Fact types:** `string · integer · decimal · boolean · code`, cardinality `one · many`.
- **C.13 Comparators:** the eleven of §6.1.
- **C.14 Check outcomes:** `satisfied · not-satisfied · inconclusive · not-applicable` — the three assessment results plus the one a single check needs and an assessment does not.
- **C.15 Collector runtimes** (in `collector@1`): `sh · bash · powershell · python · ansible · http-api` + URIs.

### 10.6 Appendix F — two new questions
> **Q-a. Why not let the script's exit code decide, as scanners do?** Because the threshold then lives in code nobody reviews against the requirement, a tailored parameter cannot reach it, and the record holds a bit instead of an observation. The comparator set is small on purpose; what does not fit stays manual and is counted.
>
> **Q-b. Q1 rejected expression languages. Why is regex allowed?** A regular expression is a membership test over one string, not a language for rules — and the kernel already relies on one in every JSON Schema `pattern`. What Q1 feared is real for regex too, so the dialect is I-Regexp, the match is whole-value, the sizes are bounded and the reference engine does not backtrack.

### 10.7 Appendix G — glossary
**Check** · **collector** · **fact contract** · **observation** · **check-verdict** · **evidence record** · **I-Regexp**, each one line pointing at §4/§6.

### 10.8 Specification
D4 (eleven types), D14 (one sentence: a regular expression in the I-Regexp dialect, whole-value, is a comparator, not an expression language), D15 (check-verdict is Portable tier, like assessment), D22 (the Check paragraph after the Risk paragraph, or the consumer-side clause #48 decides), new **D24 Check**.

## 11. Open points for the author

1. **The I-Regexp text.** The implemented grammar is the WG repository's ABNF; the published RFC 9485 text could not be fetched here. Compare before the tag.
2. **D22 / backlog #48** — a second exception, or a consumer-side clause with its own bar (§8.1).
3. **Run rows as a kernel field** (implemented) or a stdlib facet under `method` (§8.3 argues the kernel; the facet variant would need #55 first).
4. **`requirement-ref` resolves-if-present** (implemented) or closure-required. Closure-required means a CIS check pack cannot validate without the CIS bundle, which may not be redistributed.
5. **Timing.** §2.2 was measured after the shape was drafted; it covers two platforms (Linux host, Kubernetes). Land the shape at rc with this census, or wait for a cloud-API corpus (Prowler is the obvious third).
6. **`each` quantifier.** Only for-all is implemented. The census found "at least one" (3 OVAL tests) and "exactly one" (7 + 2 rules); both are answered by a collector-emitted count, so no quantifier was added.
7. **A twelfth comparator `not-equals`.** Measured: 85 uses across kube-bench, 2 OVAL states. Not added without your word, because the set is the shape. Adding it is one enum value, one table row, one evaluation line and about six vectors.

## 12. Found on the way (filed in the backlog, not fixed here)

- **#55** `Assessment.method` is never facet-validated, and all three method payloads in the repository fail their own pinned schema: the example's `summary` is a string where the normative schema wants an object; the ch10 sample uses `criteria-ref`, which `additionalProperties: false` rejects; the IFA bundle's `tasks` and `reviewed-controls` are not in its pinned `goodread-ap-stub`. Turning validation on fixes all three in one change; IFA needs a converter re-run whose sources are not in this checkout.
- **#56** The PowerShell twin does not know Check. Until it is ported, it reports the example bundle's two Checks as matching no type. Joins #45 as a blocker of the tag.
- **#57** The reader cannot open a bundle that holds a Check.
