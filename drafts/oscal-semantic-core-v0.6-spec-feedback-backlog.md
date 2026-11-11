# JASCON — v0.6 Spec-Feedback Backlog
### Consolidated open design questions from gate item 1 and the first review round · 2026-07-19

Every item carries its evidence (measured where possible), its
proposed disposition, and its source. This file is the input queue
for the v0.6 specification revision; items leave it only via a
decision recorded in the register.

**THE BACKLOG IS OPEN AGAIN** (2026-11-10, the CP-RISK-1 landing —
register "Amendments — CP-RISK-1"): landing the Risk change proposal in
the repository filed **#40–#47**; the author's answers of the same day
closed **#40** (the release is **2.0.0** — register "Amendments — the
2.0.0 decision"), deferred #42, and added **#48 · #49**; the corpus
licence review closed **#49** and left **#50**; **#42** was then done
on the author's word, and **#43** decided ("keep"). Open: #41, #45–#48
(#44 closed — the kernel pin),
#50, **#54** (residue of #53, which is closed: risk catalogues stay outside the kernel), and **#51 · #52** from the external review of rc.1 (nine findings
fixed on the branch — `drafts/CP-RISK-1.md` §13). Two need the author (#48, #50); one needs a Windows machine
(#45); the rest are work. **CP-CHECK-1 (2026-11-11, proposed)** adds
#55-#57 and makes #48 a decision before the tag: Check would be the
second consumer-side type admitted against D22 test 1. The eight review findings against the proposal
itself (R-1…R-8) were closed in the landing pass and never entered this
file — `drafts/CP-RISK-1.md` §11.2.

| # | Item | Evidence | Proposed disposition | Source |
|---|---|---|---|---|
| 41 | **Path coverage is not value arrival** *(Major, class c — affects the "lossless" headline)*. Coverage reports count source paths with a declared destination; values are not checked. | **Measured, IFA only**: 394/835 leaf values occur verbatim in the bundle; absent 194 identity + 120 document-metadata + **122 content (63 prose ≥ 40 chars)**; before the re-run 138 — 13 under `poam.risks[]`, incl. the response `type` prop. Other ten corpora: **unmeasured** (sources not in repo) | Wire `oscal_conv_lib.value_arrival()` into every converter's report; for each absent content path either carry it or declare it dropped with a reason; then re-word the "converted losslessly" sentences (README, spec Status) to what is measured | CP-RISK-1 landing, L-2 |
| 44 | **CLOSED 2026-11-10 (author: "add the kernel-version pin to the manifest") — `kernel-version`, spec D3.6, KERNEL-1/2, 9 vectors.** ~~Nothing in a bundle pins the kernel version~~ *(Minor, class b)*. A 1.0.0 tool meeting a Risk fails closed as "matches NO type" — no version in the message. The proposal's `manifest-version: "1.1"` was an undefined second spelling and was reverted. | Demonstrated: `contentManifest` shape has no such field; 11/11 corpus manifests, the converter library and the reader write `"1"` | Open on its own now that #40 is closed. 2.0.0 is the natural window: an optional kernel pin in the manifest (itself a closed-shape change) or a written rule that `manifest-version` tracks the kernel line. Decide before the tag | CP-RISK-1 landing |
| 45 | **PowerShell twin: the CP-RISK-1 port has never run** *(blocks the two-implementation gate)*. Ported from the Python reference and the vectors without a PowerShell runtime. Also observed while porting, **unverified**: the twin keys objects in `[ordered]@{}`, which compares keys case-insensitively — two ids differing only in case would collide, where the Python reference keeps both (D2: string-compared). | Not executed. Static checks only (bracket balance, no `$var:` hazards) | Run `powershell -ExecutionPolicy Bypass -File jascon/scripts/validate_core.ps1`; expect `risk: 42 pass, 0 fail` and ALL GREEN; remove the two port guards; add a case-differing-ids reference vector to settle the observation | CP-RISK-1 landing |
| 46 | **The example attestation binds nothing** *(Minor, class c)*. Its three `subject-semantic-digests` match no example object and its `content-manifest-digest` no manifest — since before 1.0.0. Separately: the IFA bundle lists its Attestation **inside** the content manifest, which D3.1 excludes by definition. | Measured: 3/3 subject digests unmatched (also against the 1.0.0 blobs) · `objects/attestation/ifa-ato.json` is a manifest entry | Make the example attestation real and have `validate_examples` hold it to it (attestation-binds on the example bundle); move the IFA attestation beside its manifest at the next converter touch. README caveat 6 now says what is true meanwhile | CP-RISK-1 landing, L-3 |
| 47 | **Two smaller shape questions** *(Minor)*. (a) Tightening `Finding.actions[].due` to `#/$defs/due` is a breaking change — it rides a major, not a converter re-run. 2.0.0 is that major and the change was **not taken**: it would end the measured property that every 1.0.0 bundle is a 2.0.0 bundle. (b) C.10 has four treatment options; OSCAL's response `type` prop allows seven — `contingency` and `none` have no code (D22 test 3, "one vocabulary without flattening"). | (a) argued; corpus would pass (3 Findings with actions) · (b) measured vocabulary: OSCAL metaschema lists 7; corpus instances of the two unmapped values: 0 | (a) author's call before the 2.0.0 tag: superset property or a typed `due`. (b) leave until an instance appears; it then stays in the facet and is counted | CP-RISK-1 landing |
| 48 | **D22 test 1 cannot admit a consumer-side type** *(decision; residue of #40)*. Risk entered the kernel as an author-decided exception to "measured 2-of-3 in the census corpus": 0 of 3 census corpora encode a risk record, because census authorities publish catalogs and a risk register is consumer-side data. As worded the test can never be met by such a type. | Measured: 0/3 census corpora; 1 non-census corpus (IFA) supplying 3 of 6 record fields; three standards prescribing the record. Register "D22-applied — Risk and test 1" | Author decides: leave D22 as is and let this exception stand as the single precedent, or add a consumer-side clause with its own bar (e.g. N standards prescribing the record + one measured lifecycle corpus + the major) | 2.0.0 decision |
| 50 | **The removed bundles are still in history and on `main`** *(author; residue of #49)*. The licence review took six bundles out of the tree (both CIS corpora, C5, C3A, CyFun, and FedRAMP-CR26 as the doubtful case). Earlier commits and the default branch still serve them. | Measured: `git show <1.0.0 commit>:converted_examples/CIS.Controls/...` still resolves; `main` is unchanged until this branch merges | Author decides: (a) accept — merging stops future publication, history stays; (b) purge — rewrite history and force-push `main`, which invalidates every existing clone and commit id cited in the register. Not something to do without an explicit instruction | Corpus licence review, 2026-11-10 |
| 51 | **No edge from a Tailoring to the scope it is a Statement of Applicability for** *(decision; from the rc.1 review, X-2)*. `risk-coverage` now scopes a Risk through `Risk.tailoring-refs`, because a Tailoring names no Component and `Risk.component-refs` therefore has nothing to join to. | Demonstrated: two Tailorings in one bundle shared every justification until `tailoring-refs`; `tailoring` shape has no component field. | Author: either `tailoring-refs` is the model (then say so in D13), or Tailoring gains an optional `component-refs` — a change to a released shape, so it rides this major or the next. | rc.1 review (CP §13) |
| 52 | **`Deviation.opened` is a free string** *(Minor; from the rc.1 review, X-5)*. The same defect was fixed for `Risk.acceptance.date` and `review-due`, which are new in 2.0.0. `opened` is a 1.0.0 shape. | Schema: `{"type": "string", "minLength": 1}`. Corpus values not surveyed. | Decide with #47a — both end the "every 1.0.0 bundle is a 2.0.0 bundle" property if any shipped value does not conform; survey first. | rc.1 review (CP §13) |
| 53 | **CLOSED 2026-11-10 (author: "keep outside of kernel") — risk catalogues stay outside the kernel; no entry type in 2.0.0.** ~~Ready-made risk lists: does a catalogue entry become a kernel type?~~ *(decision; author idea 2026-11-10, prototyped)*. `risk-catalogs/` holds two lists (office IT ×24, industrial plant ×23, English and German), a draft entry schema outside the kernel, and an import tool that copies entries into `Risk` objects. | Measured on a demo bundle (SP 800-53 MODERATE as the Statement of Applicability): the reference validator accepts it (1,065 pass); import needed **no kernel change**; 78 of 287 selected controls are named by the 23 imported risks, 209 by none; "not applicable" for an entry has no kernel home and lives in a side file. | Author, before the 2.0.0 tag if a type is wanted (afterwards it is a 3.0.0): (a) keep catalogues outside the kernel, as now; (b) one shallow entry type so that catalogues are bundle objects and the back-reference is typed; and, either way, (c) where a recorded "not applicable" for a risk lives. | `risk-catalogs/README.md` |
| 54 | **A recorded "not applicable" for a catalogue risk has no home** *(Minor; residue of #53)*. The completeness check of a risk catalogue cannot tell a decision from a gap unless the reason for not importing an entry is written down. A Tailoring records exactly this for requirements (`excludes[].rationale`); nothing does for risks. | Demonstrated in the prototype: `risk-catalogs/demo/office-it-moderate/not-applicable.json`, a side file the tool reads — 0 gaps with it, 1 without. | With catalogues outside the kernel (#53), the record stays outside too: define the side file's shape next to the draft catalogue schema. Revisit only if catalogues ever move into the kernel. | #53 |
| 55 | **`Assessment.method` is never facet-validated** *(Minor, class c)*. `facet_errors` reads only `obj["facets"]` (`validate_core.py`, PowerShell twin likewise), so a method payload is never held to its pinned schema - and none of the three in the repository would pass. | Demonstrated 2026-11-11: `examples/assessment-2026q3.json` `summary` is a string, the normative `assessment-criteria@1` wants an object; the ch10 §10.1 sample uses `criteria-ref`, which `additionalProperties: false` rejects; the IFA `conmon-2023-06` carries `tasks` and `reviewed-controls`, which its pinned `goodread-ap-stub` rejects | Validate `method` keys as facets in both validators and fix the three payloads in the same change; IFA needs a converter re-run (sources not in the checkout) | CP-CHECK-1 §12 |
| 56 | **PowerShell twin: Check is not ported** *(blocks the two-implementation gate, with #45)*. The twin does not know the eleventh type; until ported it reports the example bundle's two Checks as matching no type, and it has no I-Regexp engine. The port must carry the state-set matcher, not translate patterns into .NET regex (CP-CHECK-1 §6.3). | Not executed. No PowerShell runtime in the authoring environment | Port with #45; expect `check: 156 pass, 0 fail` | CP-CHECK-1 §12 |
| 57 | **The reader cannot open a bundle that holds a Check** *(Minor)*. `one-page-apps/jascon-reader.html` infers ten types. | Static: type list and `inferType` name ten | Step 1b of CP-CHECK-1, after the author's review | CP-CHECK-1 §12 |

**Closed 2026-11-10** (author decision; register "Amendments — the 2.0.0
decision"): **#40** → the kernel that carries Risk is **2.0.0**; D22 rev
3 stands unamended; the schema, both validators, the vectors, the
handbook and the reader were renamed in one pass. Measured alongside:
2.0.0 is a superset — all 6,914 objects of the 1.0.0 corpus validate
unchanged. The half of D22 rev 3 that "v2" does not answer left as #48.
**#49** → the corpus licence review (register "Amendments — the corpus
licence review"): three NIST corpora, ISM and Grundschutz++ kept under
their publishers' stated terms; both CIS corpora, C5, C3A and CyFun
removed from the tree (terms forbid it, or no terms found), and
FedRAMP-CR26 removed as the doubtful case in a commit of its own (a U.S.
Government work, but no licence stated by the publisher). Converters and
coverage reports stay. Five bundles ship. Residue: #50.
**#42** → the blobs are the digested bytes (register "Amendments — raw
blobs"): bundle files are `-text` and stored CRLF, so raw blob access
verifies too — 4,527 / 4,527 staged blobs match their manifest digests.
**#43** → the Risk rules stay as written (register "Amendments — the Risk
rules stay"): no relaxation for imported OSCAL data; an import that lacks
owner, level or dated acceptance stays `identified` and says so.

<details><summary>State of this file at the 1.0.0 release (2026-07-22) — kept as written</summary>

**THE BACKLOG IS EMPTY AGAIN** (2026-07-22, the P10 fix pass — register
"Amendments — the P10 fix pass"): the P10 review of the 1.0.0-rc.1 text
filed **#29–#37** (4 Major · 4 Minor · 1 erratum; register "Amendments —
P10"), the p10-gemini external review was adjudicated (**#38 · #39** in,
4 folded, **G-3 · G-4 · G-5 REFUTED — do not resurrect**; register
"Amendments — P10b"), and the fix pass closed **all eleven** the
standing way. 157/157 vectors + 11 bundles green in BOTH validators;
export 5,886/5,886. Headline: enforcing #39 (D21 acyclicity) exposed a
converter slug collision that had silently merged **239 ISM taxonomy
sets** — recovered by re-conversion (corpus 6,675 → 6,914 objects).
Every item that ever entered this file has left it through a register
entry.

</details>

<details><summary>The P10/P10b rows as they stood (all eleven closed by the fix pass)</summary>

| # | Item | Evidence | Proposed disposition | Source |
|---|---|---|---|---|
| 29 | **Facet-op duty enforcement is stdlib-only** *(Major, class a/b)*. `tailoring_duty_errors` accepts a `pinned_decl` parameter but neither validator passes it at the bundle call site (validate_core.py:974; the PS twin builds only `$STDLIB_DECL`, ps1:220), so `detach-facet`/`attach-facet` of a **pinned** semantics-bearing facet (e.g. `cr26/scope@1`, declaring `[selection]` in its pin) carries NO Deviation duty at consumer tier — contra the D13 table rows. An **unregistered** facet in `attach-facet` yields decl = None → NO duty and no payload validation (the op payload is not on any object yet) — the **inverse** of D10 dangerous-by-default; a green bundle resolves to an invalid artifact. Register D13 rev 3's "covers the full D13 table" overstates: the attach/detach rows enforce for stdlib ids only. Conformance corpus: **zero** attach/detach vectors (0 mentions). | **Demonstrated**: synthetic bundle (consumer tier: detach-of-pinned-`[selection]` + attach-of-unregistered, no Deviations) — ALL GREEN in the reference validator | Wire pinned declarations (every pin file already ships `modifies-semantics`) in both validators; an `attach-facet` id that is neither stdlib nor pinned nor `private:` ⇒ error (closure class, any tier); add ≥4 tailoring vectors (detach-pinned ± deviation, attach-unregistered, attach-stdlib-semantics-bearing) | P10-1 |
| 30 | **Same-target op law unenforced on bundles** *(Major, class b)*. D13: "two operations addressing the same target within one Tailoring = validation error" — implemented only in the vector runner (`run_tailoring` target-tuple check); bundle validation never applies it in either validator, so a real Tailoring with two ops on one (requirement, statement, name) target validates green; two conforming resolvers may then diverge (last-wins vs error) — the profile-resolution corpse by the side door. | **Demonstrated**: bundle Tailoring with duplicate `set-modality` ops on one statement — ALL GREEN | Lift the same-target check into bundle validation (both validators); the existing `same-target-conflict` vector stays the oracle | P10-2 |
| 31 | **Selection predicates unbounded in delivery** *(Major, class b/c)*. D13 claims "set-ref or the three bounded predicates" (B.2 shared vocabulary), but the kernel schema types `selects[].predicate` as ANY object, neither validator evaluates or shape-checks it (the B.2 machinery — `eval_predicate` — exists but only conditional-apply calls it), and the only predicate vector is tier-blocking (`predicate-select-blocks-the-claim`). A Tailoring selecting on `{"frobnicate": true}` is conformant today; two Portable tools implementing selection diverge — the implementation-defined-behavior state D15 abolishes. | **Demonstrated**: bundle Tailoring with a garbage predicate — ALL GREEN | Constrain `predicate` in the kernel schema (anyOf of the three B.2 forms), shape-check in both validators, add shape vectors (3 valid + malformed/nested/boolean-composed rejections) | P10-3 |
| 32 | **rc.1 Part II prose diverges from the shipped schema — five demonstrated instances** *(Major, class b)*: (1) D5 example `includes: [{"component-ref": …}]` — schema: array of URI strings; (2) D6 "responsibility: provider\|customer\|shared" — schema adds `inherited`; (3) D6 lists `deviations[]` on Implementation and D8 attaches Deviation "on Implementation, Finding, Tailoring" — the schema has NO `deviations` on Implementation (closed shape rejects it) and instead grants it on Requirement (the App-A ex-ante channel) and Assessment, which D8's list omits; (4) D7's shape lists `provenance-map-ref?` — the closed schema rejects the property; (5) D20's inline example `"rationale": "…"` bare string — schema requires `text` (#12); (6, cosmetic — G-9) D9's shorthand `prose{lang}` predates the `text` rename — read `prose: text`. | **Demonstrated**: all five INVALID under jsonschema at HEAD (and the corrected forms VALID) | Part II errata: align D5/D7/D20 examples and the D6 enum to the delivered schema; **decide** Implementation.deviations — add to the schema (D8/D13's consumption story leans on it; zero corpus objects affected, no digest churn) or reword D6/D8 to the actual attachment points (Requirement, Tailoring, Assessment, Finding) | P10-4 |
| 33 | **Consolidation count errata** *(Minor, class c/d)*: (a) "twelve corpora" (rc.1 Status, §2, IV.7 "Twelve corpora under `converted_examples/`") vs **eleven** everywhere else (README:16, register naming entry, this file, gate-4 report) and 11 bundle dirs — recount at HEAD: **11 bundles / 6,675 objects / 251,591 leaves / UNMAPPED 0** (the three latter numbers CONFIRMED exact); "twelve" is defensible only counting 800-53 and 800-53B as separate source publications — a convention no document states; (b) LoC quoted as current are gate-4-commit numbers: HEAD recounts 941/1,113/307 vs quoted 938/1,110/280 (counter parity proven at `9b953fd`; the rerun added the lines); ~30× holds **per implementation** (32.8× / 27.8×) but the Status says "**together** ~30× smaller" (together ≈ 15×); register R8 "three decimal orders below" is arithmetically false (~1.5 orders); register R7 "×1 wrapper" → **2** at HEAD (the rerun added the CR26 wrapper); (c) IV.5.2 "129 across nine families **at HEAD**" — stale (HEAD = 149/12); (d) §2's scope statement still carries pre-gate language (CIS "disputed … verification item" — resolved as R15 in the same document); (e — G-10) register editorial: the heading "D26" jumps the D-number space (no D23–D25 exist — it is backlog #26 wearing a D-label) and the register header still reads "(v0.5)" / 2026-07-18 while serving as the rc.1 companion. "Eleven" now confirmed by two independent reviews (P10 + G-7) — unify on eleven. | Measured (recounts; git-pinned counter parity) | One erratum sweep: state the corpus-count convention once (or unify on eleven), restamp or date-stamp the measurements, reword "together ~30×" per-implementation, fix R7/R8, refresh the two stale sentences | P10-5/7/11/12 |
| 34 | **D19/IV.8 name-note contradiction** *(Minor, class b/d)*: the rename substitution left D19 reading "final name under review for 1.0.0 (the working title "JASCON" carries a trademark-optics question…)" while the title block records the name as decided 2026-07-22 — and the trademark-**optics** rationale belonged to the OLD name (using NIST's "OSCAL" mark; diff 42b4390→7199c26). JASCON's open item is the DPMA/EUIPO/USPTO screen + domain grab (register naming entry). IV.8 step 1 still lists the name as pending. Independently found by G-8. | **Demonstrated** (git diff) | Erratum: D19 → name fixed (JASCON, register entry), residual = trademark screen/domains pre-tag; IV.8 step 1 → done ✓ | P10-6 |
| 35 | **Appendix-D verification clock expired unadjudicated** *(Minor, class c)*: D.7 `system-context@1` / D.8 `assurance-levels@1` carry "still medium tier: Rev5-cycle field verification (gate 3)" — gate 3 ran and closed with no recorded verdict; no descriptors ship (IV.7's "seven" is honest) while rc.1 D22 cites `assurance-levels@1` normatively as the absorption exemplar. | Measured (appendix-d:217; the gate-3 register section is silent on D.7/D.8) | Record the post-gate-3 verdict: verify against the Rev5 corpus now in hand, or park beside `privacy-assessment@1` under the clock rule | P10-8 |
| 36 | **IV.7 inventory omits the normative companions** *(Minor, class b)*: the release-artifact list has no rows — and the rc.1 file no paths — for Appendices A–C (`jascon/references/appendix-{a,b,c}-…`), the handbook, or the Decision Rationale Register, though the rc.1 cites them normatively (D13 → "Appendix B" for THE resolution algorithm; D11 → C.9; provenance → the register). A reader of the rc.1 file alone cannot locate the resolution algorithm. | Measured (IV.7 text; zero path references in the file) | Add the documentation rows with repo paths to IV.7; give the register its path at first mention | P10-9 |
| 38 | **Corpus directory `geman.bsi` misspelled and off-convention** *(Minor, class b/d; G-1 CONFIRMED)*: the BSI bundle directory is `geman.bsi` (typo for "german") while every sibling follows `CC.NAME` (`DE.C5`, `DE.C3A`, `US.SP800-53`); the typo ships in the 1.0 release inventory and in every living reference (README, gate-4 table, reader hints). | Measured (directory listing) | `git mv` → `converted_examples/DE.BSI`; update living references (README incl. deep links, reader hint URLs — reader version bump, converter output path, gate-4 table label); dated register/census entries keep the historical spelling | P10b G-1 |
| 39 | **RequirementSet membership cycles validate green** *(Minor, class a; G-6 CONFIRMED)*: the schema cannot see cycles and `closure_errors` checks resolution only, so a bundle with Set A ∋ Set B ∋ Set A passes both validators; naive baseline expansion or `uses-term` nearest-Set search loops forever. D21 never states acyclicity (overlapping membership is legal — cycles are not). | Argued in G-6; trivially constructible | D21 sentence: membership graphs are DAGs — a membership cycle is a validation error; cycle detection in `closure_errors` + the PS twin; +2 reference vectors | P10b G-6 |
| 37 | **Canonical-form residues, latent** *(erratum, the #27 tier)*: (a) `decimalString` admits `-0`/`-0.0` — two spellings of zero, the #27 leading-zero class; (b) `text` values admit `{"en": []}` and `""` (zero-length translations — absent-vs-empty divergence on the new primitive); (c) the relation extension pattern `^https?://` admits bare `"https://"`; (d) `param_check` decimal bounds compare via `float()` (precision loss beyond 2^53); (e — G-2 CONFIRMED in substance) `text` keys are case-ambiguous: `en-US` and `en-us` are two spellings of one BCP-47 tag (tags are case-insensitive by RFC 5646) with two digests — the #27 "one value, one spelling" class on the new primitive. G-2's proposed fix (normalize at digest time) is REJECTED — never-normalize is the D3.4 discipline; the canonical spelling rides the schema instead (lowercase-only key pattern; corpus carries only `en`/`de`). Zero corpus instances of any. | **Demonstrated** (schema-accepts runs) | Tighten at the next schema touch: exclude `-0`, minLength/minItems on text values, lowercase text-key pattern, require substance after `https?://`, exact decimal compare; +3–4 vectors | P10-10 · P10b G-2 |

</details>

<details><summary>The last open rows as they stood (closed by the rerun)</summary>

| # | Item | Evidence | Proposed disposition | Source |
|---|---|---|---|---|
| 12 | **`text` primitive — DECIDED, adopt** *(author 2026-07-22; register "D9 rev 2").* `text` = `{BCP-47: string}` for all human-readable fields (`title` ×3,041, Mapping `rationale` ×373, action/capability descriptions, deviation rationale, facet free text); identifiers stay strings (`id`/`version`/codes/`label`). Generalizes the existing `langMap`. Payload harmonization **shipped for ISM + CR26** (2026-07-21). | **Rationale: EU standards must be available in all 27 official languages** (NIS2/DORA/CRA); the tagged-vs-bare inconsistency is already measured (converters disagreed) | Delivery — schema field-switch + all-converter reruns + full re-pin — **rides the converter rerun** (a transitional string-or-`text` schema MAY bridge); stays open until delivered | Review round 1, finding 3 |
| 20 | **Relations: constrain extension types to URI shape** *(round-2 partial).* Done: D13 row aligned with B.3 (`remove-relation(required) ⇒ Deviation`); C.8 `supersedes` deleted (register "C.8 rev"). Remaining: the schema types relation `type` as any non-empty string, so a typo'd base code silently becomes a carried extension (P9b-4). **Blocked on the converter rerun** migrating the corpus's bare-word `sharpens` ×28 to a namespaced URI. | P9b-4; `sharpens` ×28 measured | After the rerun: constrain extension relation `type` to a URI shape (base codes ∪ URI) in the schema; add a vector | P9 run 2 |
| 26 | **Facet enforcement: ship real pinned schemas + pin-honoring** *(round-2 partial).* Decision recorded (register "D26"): stdlib strict, non-stdlib against the pin. Remaining: bundles pin permissive illustrative stubs (`additionalProperties` defaults `true`), so framework/compat payloads are under-validated and the reference validator diverges from a pin-honoring sealed tool. | Demonstrated: `cr26/scope` stub accepts a smuggled key; stubs are ILLUSTRATIVE | **Converter rerun** ships pinned schemas with `additionalProperties:false`; fix pin-vs-descriptor precedence | P9c run (2026-07-22), Major P9c-3 |

</details>

**Closed 2026-07-21** (review round 1 decisions; register "Amendments —
v0.6 cycle" + spec changelog IV.7): **#1** → D9 rev (parameter
`label`/`default`; residue drains at next converter run) · **#2** → D13
rev (Deviation duties bind at consumption tier; authority Tailorings
exempt; `variants` carrier rejected via the D22 bar) · **#4** → **D22**
(kernel promotion rule normative) · **#5** → D20/D21 rev (supplement
pattern named; `supplements` stdlib relationship extension code) ·
**#7** → D10 rev (`by-statement` keying normative) · **#3** → closed
no-change (D9 closure note: 0 true unit-class crossings measured — the
51 first-pass flags were base-absent variants, resolved under #2's D13
rev; the elapsed/calendar unit-class boundary stays strict) · **#8** →
D10 rev 2 (declarations promoted: security-objectives/effectivity →
`[selection]`, reporting-obligation → `[assessment]`; a tool that cannot
handle a facet must stop working on that data; stubs update at next
converter run) · **#9** → closed, folded into the gate-3 scope statement
(IV.5): seed sets confirm/extend only from counted lifecycle evidence ·
**#11** → closed, delivered: reported to the BSI authors by the project
(companion to the 216/issue #58; never a spec change) · **#6** → closed
at gate 2 (2026-07-21): root-Set hosting normative in the terminology
stdlib descriptor; carrier/tenth-type rejected via the D22 absorption
clause (register "D22-applied") · **#16** → closed (2026-07-21,
register "P9-applied"): reference taxonomy normative — closure-required
(Set members, Tailoring selects/excludes/op targets + statement
existence, Implementation component/requirement + D5 basis-ref, Finding
refs, Mapping scopes when the endpoint is in-bundle) vs. landmark
(Mapping endpoints, party URIs, evidence, attestation subjects);
implemented + 9 vectors; parties stay landmark by the D22 test (0-of-3
corpora publish party objects) · **#17** → closed (2026-07-21,
register "P9-applied"): facet payloads validate against normative
stdlib descriptors or bundle-pinned schemas, `private:` ignored by
definition, unregistered ⇒ error; 7 vectors incl. the P9-1 probe; all
8 bundles green under enforcement · **#19** → closed (2026-07-21,
register "P9-applied", layered per user decision): tier DERIVED from
data — id-origin match = authority-claimed, authority Attestation over
the Tailoring (digest-verified) = authority-proven (proof beats
prefix), else consumer; duties bind at consumer tier; 8 derivation
vectors; op-duty enforcement live in bundle validation (CR26's four
class Tailorings derive authority-claimed). Numbering stays stable —
closed numbers are not reused.

**Closed 2026-07-22** (v0.6 cycle round 2; register "Amendments — v0.6
cycle, round 2" — acts on the P9c re-review + the deep-research open
items): **#13** → `calendar-context@1` stdlib code system seeded (C.9:
us-federal/de-bund/eu-target2; `calendar-ref` SHOULD cite it) · **#14**
→ canonical-alias same-content check implemented in `closure_errors` +
2 reference vectors (register "D2 rev") · **#15** → template
accreditation = declared non-goal, authority-local (register
"R6-applied") · **#21** → Sets unaddressable by operations; `sequence`
struck from the set-field whitelist (schema enum + spec D13 row +
appendix-b; register "D21 rev") · **#22** → anticipated-convergence
path scoped pre-1.0 (register "D22 rev 2") · **#23** → `uses-term`
nearest-Set = fewest membership hops, ties ⇒ Portable-tier error
(register "D22-applied rev") · **#25** → op-law completed for
`set-parameter` bounds/tightening + `remove-relation(required)` in
`tailoring_duty_errors` + 6 tailoring vectors (register "D13 rev 3") ·
**#27** → decimal no-leading-zeros + scale-significance clarified
(schema pattern + spec D3 rev) + 2 parameter vectors · **#28** → count
erratum applied (README + spec → 125; recompute via
validate_core.py). Conformance grew 115 → **125 vectors**.
**Partials (stay open above, narrowed):** #20 (schema URI-shape for
`sharpens` awaits the converter rerun), #26 (real pinned
schemas + pin-honoring await the converter rerun). **Still open (delivery pending):**
#12 (`text` primitive — DECIDED 2026-07-22; delivery rides the
converter rerun). Numbering stays stable — closed numbers
are not reused.

**Closed 2026-07-22 (gate 4;** register "Amendments — gate 4" + spec
IV.10): **#18** → both named vector families delivered WITH their
engines — D3.5 composition (`--compose`, highest-minor resolve +
re-validation, 7 vectors) and B.1.8 `conditional-apply` (one-predicate
trigger, one instantiated primitive, normative FAIL format, 8 vectors);
DSSE profile verification live · **#24** → signature verification live
(Ed25519, dependency-free, both implementations): in verification mode
(`--trusted-keys`) an unsigned attestation cannot prove — the P9c-1
forgery closed; 5 dsse vectors. Also delivered against IV.5.4: the
**bidirectional export suite** (10/10 catalog bundles → schema-valid
OSCAL 1.2.2, round-trip **5,647/5,647 objects digest-equal**) and the
**weekend-validator measurement** (`validate_core.ps1`, PowerShell 5.1,
zero installs, 149/149 vectors; ~30× below compliance-trestle's LoC —
see `drafts/gate-4-measurement.md`). Conformance 129 → **149 vectors**
across 12 families.

**Closed 2026-07-22 (gate 3;** register "Amendments — gate 3" + spec
IV.9): **#10** → **DRAINED** (D10 rev 3: an external ODP citation
addresses (requirement, parameter-name) via the DECLARING statement —
measured: no Rev 5 ODP is declared in two statements; the CR26 CTL
overlay's 16 assignments emitted as `set-parameter` ops on the
`rev5-odp-overlay` Tailoring, 14 tailored controls carried in-bundle;
guidance entries stay parked as D20 supplements territory) · **#9
confirmation delivered** (#9-applied: IFA lifecycle corpus mapped with
ZERO enum additions; five lifecycle types at document scale, both
digests — the standing Test-2 gap closed). Gate 3 additionally fixed
two reference-validator defects the corpus exposed (D13 rev 4 tier
anti-laundering; D9 rev 3 multi-select list values) and recorded eight
source findings for upstream. Conformance grew 125 → **129 vectors**;
corpus at HEAD: 11 bundles, 6,675 manifest-listed objects.

**Standing rule for this file:** items enter with counts, leave with
register entries. An item that can neither be evidenced nor closed
after two gate cycles is deleted — backlogs rot like registries do.
