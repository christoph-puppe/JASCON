# CP-RISK-1 — Risk as the tenth kernel type

**Change proposal · JASCON kernel 1.0.0 → 1.1.0 · 2026-11-05** — *version decided by the author on 2026-11-10: **2.0.0** (§12)*
**Process:** Chapter 15.4 (evidence in, corpus first, implementations follow). Every rule below carries a machine id, a human rationale and a failure message that prints on failure.
**Scope:** kernel schema, reference validator, conformance corpus, example bundle, handbook text (Ch. 2, 10, 14; App. A, B, C, D, F, G; SKILL.md). Converters: follow-up (§8).
**Status (2026-11-10): landed in the repository on a branch — NOT released. The version is decided: 2.0.0 (§12).** §1–§10 are the proposal as written on 2026-11-05 against the synced skill bundle. §11 records what happened on contact with the repository: what held, what was corrected (each correction demonstrated failing first), which claims below do not hold, and what the first corpus measurement said. §12 records the author's decisions of the same day. **Where the sections disagree, the later one is the state — and wherever §1–§11 write "1.1.0", read "2.0.0":** the schema file, its `$id` and every label were renamed. §13 records an external review of the release candidate (same day): nine findings, each reproduced first; four change what §5, §6 and §11.2 say. Open items: backlog #41–#52.

---

## 1. The gap, in one sentence

A consumer who selects a requirement cannot say, in data, *why*. ISO/IEC 27001:2022 6.1.3 d requires exactly that sentence for every control in the Statement of Applicability — included *because of* a treatment decision, excluded *with* a justification — and 6.1.3 f requires the risk owner's acceptance of what remains. JASCON 1.0.0 has `Tailoring.excludes[].rationale` for the second half and nothing for the first: the graph can carry "KONF.14.1 s2 is in scope" and "finding 017 is against s2", and cannot carry "s2 is in scope because key compromise R-2026-007 is treated by it". Appendix F Q14 parked *risk scoring* in facets, correctly. It parked the *risk object* with it, and that is the defect this proposal repairs.

The same gap was filed upstream against OSCAL 1.x as usnistgov/OSCAL #2292: OSCAL's `risk` lives in assessment-results and POA&M only — ex post, a thing an assessor finds — while an ISMS runs the other way round: the risk comes first and *justifies* the requirement. A format that cannot say which risk a selected control treats cannot represent an ISO 27001 catalog, however many controls it holds.

## 2. The counts

The Chapter 15 test is "three authorities encode this independently". Four do, and they agree on the shape:

| Authority | Where risk is encoded | Fields it insists on |
|---|---|---|
| **ISO/IEC 27001:2022** 6.1.2–6.1.3, 8.2–8.3; ISO/IEC 27005:2022 | risk assessment → treatment plan → SoA | risk owner (6.1.2 c 2), consequences + likelihood + level (6.1.2 d), evaluation against criteria (6.1.2 e), treatment option (6.1.3 a), *all controls necessary* (6.1.3 b), SoA justification for inclusion and exclusion (6.1.3 d), owner's approval and residual acceptance (6.1.3 f); four options: **avoid · modify · share · retain** (ISO 31000 §6.5.2 / 27005 §8.6) |
| **BSI-Standard 200-3** (Risikoanalyse auf der Basis von IT-Grundschutz) | Gefährdungsübersicht → Risikoeinstufung → Risikobehandlung → Konsolidierung | threat list per Zielobjekt (elementare Gefährdungen G 0.1–G 0.47), Eintrittshäufigkeit × Auswirkung → Risikokategorie, four options **Vermeidung · Reduktion · Transfer · Akzeptanz** — the ISO four, one-to-one; result: additional or strengthened Anforderungen in the Sicherheitskonzept |
| **NIST SP 800-30 Rev. 1 / 800-39 / 800-37 RMF** | risk assessment feeding the Select step | threat source + event, vulnerability, likelihood, impact, risk level; responses **accept · avoid · mitigate · share · transfer** (800-39 §2.4 — share/transfer collapse into ISO's `share`) |
| **OSCAL 1.1.x** (assessment-results, POA&M) | `risk` with `characterizations`, `mitigating-factors`, `deadline`, `remediations`, `related-observations`, `threat-ids`, `status` | the ex-post half only — the #2292 critique; the IFA/GoodRead corpus already converts it (`convert_ifa.py`: POA&M risks → Findings + a `risk@1` framework facet carrying `risk-status`, `deadline`, `statement`, `characterizations`, `mitigating-factors`) |

Measured in the JASCON corpora today: **899 threat-linked clauses** in the BSI bundle (`security-objectives@1.threat-refs`, authority side), **2 POA&M risks** converted in the IFA bundle (consumer side, as a framework facet because no kernel home existed), **0** places where a selected requirement can name the risk it treats. The gap is measured, the shape is cross-authority, the vocabulary (four treatment options) is literally identical in two of the four sources.

## 3. What goes in the kernel and what stays out

The Q14 argument — scoring methodologies differ by framework and by fashion — holds and is kept: **how** a level was computed (likelihood × impact grid, CVSS, FAIR, the BSI 4×4 matrix) stays in facets. **That** a risk exists, who owns it, what it says, what was decided, which controls carry the decision, and who accepted what remains — these four authorities encode identically, and that is the kernel profile.

| Kernel (1.1.0) | Facet (unchanged discipline) |
|---|---|
| identity, version, lifecycle, title, aliases, relations (A.0) | likelihood, impact, consequence scales, CVSS vectors, FAIR distributions |
| `scenario` — the risk statement | asset valuation, threat-source attributes |
| `owner-ref` — ISO 6.1.2 c 2 | risk criteria / appetite definitions |
| `state` — identified · assessed · treated · retired | review history, KRIs |
| `rating`, `residual-rating` — an opaque **level on a named scale** | the scale's definition |
| `treatment` — modify · retain · avoid · share | |
| `treatments[]` — the controls, to the statement | |
| `shared-with-ref`, `acceptance`, `review-due` | |
| `threat-refs`, `component-refs` — the edges to catalogs and assets | |

`rating` follows the `security-objectives@1` precedent (App. D.2: "rating values are the authority's own scale, frozen by the pinned schema, not normalized") lifted one level: `{level, scale-ref}`. Levels compare as strings within one `scale-ref` and never across scales (D2 — identifiers are opaque). A validator can therefore check *presence* and *consistency*, never *magnitude*; magnitude is the facet's business.

## 4. The shape (App. A.9b)

Common A.0 fields plus:

| Field | | Type | Meaning & evidence |
|---|---|---|---|
| `scenario` | ● | text | The risk statement — event and consequence (ISO 27005 event-based; BSI 200-3 Gefährdung am Zielobjekt). Multilingual like every normative text. |
| `owner-ref` | ● | URI | The risk owner (ISO 6.1.2 c 2). Landmark ref — a party, not a bundle object. |
| `state` | ● | code (C.3c) | identified · assessed · treated · retired. |
| `threat-refs` | ○ | [URI] | Threat catalog entries (G 0.x, ATT&CK techniques, 800-30 threat events). Landmark. |
| `component-refs` | ○ | [URI] | The assets at risk — Components of this bundle. Closure-required. |
| `rating` | ○ | {level ●, scale-ref ●} | Inherent/current level on a named scale. **Required** once `state` ∈ assessed · treated (RISK-2). |
| `residual-rating` | ○ | {level ●, scale-ref ●} | The level after treatment. |
| `treatment` | ○ | code (C.10) | modify · retain · avoid · share. **Required** once treated (RISK-3). |
| `treatments` | ○ | [{requirement-ref ●, statement-ids ○}] | **The ISO 6.1.3 b edge**: the controls determined for this risk, to the clause. requirement-ref closure-required (RISK-7); statement-ids must address the target (RISK-8). **Required** for `modify` (RISK-4). |
| `shared-with-ref` | ○ | URI | Who carries the shared risk. **Required** for `share` (RISK-5). |
| `acceptance` | ○ | {approver-ref ●, date ●, rationale ●} | The owner's acceptance of the residual (ISO 6.1.3 f). **Required** for `retain` (RISK-6) and once treated (RISK-3). |
| `review-due` | ○ | date \| elapsed-duration \| calendar-period | ISO 8.2 "at planned intervals" — the same computable union as `Finding.actions[].due`, fail-closed without the named calendar. |

**Shape-disjointness** (the no-discriminator contract): `scenario` + `owner-ref` occur in no other type; the ten minimal objects each match exactly one entry point; the field-free object matches none. Exercised by `run_tiers` (MINIMAL) and `risk-vectors.json`.

**Finding gains one optional field:** `risk-refs` ○ [URI] — the ex-post record points at the ex-ante one it materialised against. Landmark: the assessor's Finding and the organisation's register normally live in different bundles.

**Deviation is untouched.** `risk-adjustment` stays a Deviation type (weakening a requirement because a risk was accepted); the new SHOULD (RISK-9) is that such a Deviation names the Risk in `refs`. Acceptance *of a risk* and *weakening of a requirement* are two acts by two roles; the kernel keeps them as two records that reference each other.

## 5. The rules

Format per Chapter 15.4 and Appendix B: id · what it refuses · why · the message. RISK-2…6 are schema conditionals (any JSON-Schema validator enforces them for free); RISK-7…11 are graph rules in the reference validator.

| Id | Rule | Rationale | Failure message |
|---|---|---|---|
| **RISK-1** | A Risk is `scenario` + `owner-ref` + `state` at minimum. | A risk without an owner is a worry, not a managed risk (ISO 6.1.2 c 2). | schema: required `owner-ref` |
| **RISK-2** | `state` ∈ assessed · treated ⇒ `rating` present. | Analysed means a level was determined (ISO 6.1.2 d–e; BSI Risikoeinstufung; 800-30 determine risk). | `FAIL [RISK-2] <risk> state=assessed without rating — an assessed risk has a level on a named scale` |
| **RISK-3** | `state` = treated ⇒ `treatment` and `acceptance` present. | Treated means an option was chosen and the owner signed the residual (ISO 6.1.3 a, f). | `FAIL [RISK-3] <risk> treated without acceptance — a treated risk carries its owner's signature` |
| **RISK-4** | `treatment` = modify ⇒ `treatments` non-empty. | A modification with no controls is nothing (ISO 6.1.3 b). | `FAIL [RISK-4] <risk> modify names no controls` |
| **RISK-5** | `treatment` = share ⇒ `shared-with-ref`. | Sharing names who carries it (27005 8.6.2; BSI Transfer). | `FAIL [RISK-5] <risk> share without shared-with-ref` |
| **RISK-6** | `treatment` = retain ⇒ `acceptance`. | Retention *is* acceptance; silent retention is the oldest ISMS defect (ISO 6.1.3 f). | `FAIL [RISK-6] <risk> retain without acceptance` |
| **RISK-7** | `treatments[].requirement-ref` and `component-refs[]` resolve in-bundle. | The organisation's own selected controls and assets — closure-required like `Implementation.requirement-ref` (#16 taxonomy). | `FAIL [RISK-7] <risk> treatments requirement-ref does not resolve in-bundle: <uri>` |
| **RISK-8** | `treatments[].statement-ids` name statements of the target. | Clause precision is addressable or it is prose (B.1.3). | `FAIL [RISK-8] <risk> statement-id 's9' names no statement of <req>` |
| **RISK-9** *(SHOULD)* | A `risk-adjustment` Deviation references a Risk in `refs`. | The weakening and its justification meet in data. | `note [RISK-9] <object>: risk-adjustment Deviation references no Risk of this bundle` |
| **RISK-10** *(SHOULD)* | At consumer tier, every `Tailoring.excludes[]` carries a `rationale`. | An exclusion without justification is a list, not an SoA (ISO 6.1.3 d). | `note [RISK-10] <tailoring>: n exclude(s) without rationale at consumer tier` |
| **RISK-11** | A Risk's treatment may not name a requirement that no Tailoring in the bundle selects. | The treatment plan and the SoA disagree: the risk leans on a control the SoA dropped. | `FAIL [RISK-11] <risk>: treatment names <req>, which no Tailoring in this bundle selects` |

**C.3c Risk states:** identified → assessed → treated → retired. Forward only; skipping allowed (RISK-2/3 make the skipped content mandatory anyway); `retired` is terminal — a recurring risk is a new Risk, the Finding `closed` rule applied once more.

## 6. The ninth primitive: `risk-coverage` (B.1.9)

Appendix B.4 reserved the slot: "the ninth primitive, when its evidence arrives, ships as a set version through the Chapter 15 process". This is it.

**Input:** a bundle. **Computation:** for every Tailoring, resolve the selection (set-refs through nested Sets, minus excludes; predicate selects are noted as engine-resolved), then for every selected requirement collect the Risks whose `treatments` name it. **Output:** per Tailoring — `selected`, `covered` {requirement → [risk ids]}, `uncovered` [requirement ids], `excludes-without-rationale`; per bundle — `treatment-out-of-scope` (RISK-11 errors).

**Verdict discipline:** `uncovered` is a **report line**, never a failure by default. Whether a selected control needs a risk basis is the program's policy: ISO 27001 6.1.3 d says yes for every SoA row; BSI 200-2 says the Basis- and Standard-Anforderungen are justified by the baseline and only Zielobjekte with hoher/sehr hoher Schutzbedarf go through 200-3. The reference validator exposes the policy as `--require-risk-basis`, which turns `uncovered` into failures. Portable tier **MUST** compute the report; failing on it is the program's clause, written into policy the way §15.1 recommends.

Run against the shipped example bundle the primitive already says something true: the `erhoeht` Tailoring selects three requirements from three authorities, **one** (KONF.14.1) is justified by a Risk, **two** (ISM-1234, IEC-CSO-IIR) are selected by nobody's risk. With `--require-risk-basis` that is two failures with the clause printed. That is the answer to "does each control rest on a risk?" — computed, not audited by hand.

## 7. Semver decision: 1.1.0

Kernel shapes are closed (`unevaluatedProperties: false`), so *any* additive change — a new optional field as much as a new type — is forward-incompatible: a 1.0.0 validator rejects a 1.1.0 bundle that uses the addition. The semver promise in §15.2 is therefore backward compatibility only: **every 1.0.0-valid object validates under 1.1.0 unchanged.** It does (the full 1.0.0 corpus and the example bundle pass the 1.1.0 schema before the Risk object is added). New type + new optional field + two new code systems + one new primitive = minor. ~~Manifests pin exact schema versions (D3), so nothing moves silently; a bundle that carries a Risk pins 1.1.0 and a 1.0.0 consumer fails closed with the schema version in the message, which is the designed behaviour.~~ *Struck on landing (§11.3): a content manifest pins **facet** schema versions; nothing in a bundle pins the kernel version. A 1.0.0 consumer does fail closed on a Risk, but with "matches NO type", not with a version. And the released specification (D22 rev 3, IV.8) says kernel-shape changes ride **major** versions — this section argues for a minor without knowing that sentence existed. **Decided 2026-11-10: the release is 2.0.0 (§12).***

Identifiers keep the working-title spelling (`https://ns.oscal.org/semantic-core/schema/1.1.0`) for the reason SKILL.md gives: re-spelling them churns every digest for zero semantic gain.

## 8. What ships, what follows

**Ships with this CP (all green under `validate_core.py`, 31/31 risk vectors, 14/14 example objects):**

| Artifact | Change |
|---|---|
| `schemas/oscal-semantic-core-1.1.0.schema.json` | `$defs/risk`, `riskState`, `riskTreatment`, `riskRating`, `due`; `finding.risk-refs`; `$id`/title/description |
| `scripts/validate_core.py` | `risk` in TYPES + MINIMAL; closure rules RISK-7/8; `RISK_NEXT`; `risk_coverage()` (B.1.9), `risk_link_notes()` (RISK-9/10/11); `run_risk()`; `--require-risk-basis`; coverage report in bundle and example runs |
| `conformance/risk-vectors.json` | 15 object vectors, 8 bundle vectors, 8 state transitions |
| `examples/risk-acme-kms-key-rotation.json` | R-2026-007: treated, BSI 200-3 scale, G 0.19/G 0.28, treats KONF.14.1 s2, CISO acceptance, 12-month review |
| `examples/finding-017.json` | `risk-refs` → R-2026-007 |
| `examples/content-manifest.json` | `manifest-version` 1.1, 13 objects, digests regenerated |
| Handbook deltas | §9 below |

**Follows (named exits, the D.10 way):**

1. **`risk-analysis@1` stdlib facet** — likelihood, impact, method, characterizations, mitigating factors. *Parked until measured*: the IFA `risk@1` framework facet (2 risks, characterizations + mitigating-factors) is the first corpus; a BSI 200-3 Risikoanalyse export (Eintrittshäufigkeit × Auswirkung matrix) the second. No facet designed from memory — the book's only method.
2. **Converter re-run:** `convert_ifa.py` POA&M risks → Risk objects (`risk-status` → `state`, `statement` → `scenario`, `deadline` → `review-due`, remediations stay Finding actions, characterizations → the parked facet); Findings gain `risk-refs`. The BSI `threat-refs` stay where they are — authority-side threat linkage is `security-objectives@1`, consumer-side risk is the Risk object; the two meet when a Risk's `threat-refs` cite the same G 0.x URIs.
3. **Selection predicate `treats-risk`** (B.2, fourth predicate) — "select everything a Risk in this bundle treats" would let the SoA be *derived* from the register rather than written beside it. Deferred: it widens the one-leash budget and needs its own evidence.
4. **`Finding.actions[].due` tightening** to `#/$defs/due` — correct per A.8, deferred to the converter re-run so no shipped bundle breaks.
5. **Tailoring-level selection basis** (`baseline · risk · legal`) — rejected for now; the policy switch does the same job without a shape change until a corpus shows the field is authored.

## 9. Handbook deltas (insert text)

### 9.1 SKILL.md — Requirement 1
> Align all compliance data into a graph of **ten** shallow, globally identified objects (Requirement, RequirementSet, Tailoring, Mapping, Component, Implementation, Assessment, Finding, Attestation, **Risk**) and 2 sub-objects (Deviation, Authorization).

Add **Requirement 9a: Risk and the Statement of Applicability** — "Model the ex-ante risk record as a `Risk` object: scenario, owner, state, rating on a named scale, treatment option, and `treatments[]` naming the requirements (to the statement) that carry the decision. Risk acceptance is the `acceptance` sub-record, never a Deviation; a `risk-adjustment` Deviation references the Risk it accepts (RISK-9). Compute the SoA with the `risk-coverage` primitive (B.1.9); scoring methodologies stay in facets (App. F Q14)." Reference: Chapter 10 §10.6; companion `examples/risk-acme-kms-key-rotation.json`, `conformance/risk-vectors.json`.

### 9.2 Chapter 2 — §2.3, after "Assessment and Finding"
> **Risk.** Everything above answers *what is required, what is in place, what was found*. An ISMS asks one question before all of those: *why is this requirement in scope at all?* ISO/IEC 27001 answers it with a risk owner, a treatment decision and a Statement of Applicability; BSI-Standard 200-3 and NIST SP 800-30 answer it the same way under other names. A Risk records that answer as data: a `scenario`, an `owner-ref`, a `state`, a `rating` as an opaque level on a named scale, a `treatment` from four codes the standards share verbatim, and `treatments[]` — the requirements, to the clause, that carry the decision. Scoring methodology stays in facets; the fact that this control exists *because of* that risk is kernel. A Finding may point back with `risk-refs`; a `risk-adjustment` Deviation names the Risk it accepts. The SoA is then a computation (`risk-coverage`), not a spreadsheet.

Replace "That is nine:" with "That is ten:" and append **Risk** to the list, with the sentence "on the organisation's side between content and system".

### 9.3 Chapter 10 — §10.3 correction and new §10.6
In §10.3, the example's `"risk": { "…risk facet…": {} }` is not a kernel field; replace with `"risk-refs": ["https://cso.example/risk/R-2026-007"]` and the sentence: **`risk-refs`** closes the loop the old POA&M never could: the finding points at the Risk it materialised against, and the Risk points at the clause that was supposed to treat it — the same `s2`.

New **§10.6 Risk: the record that comes first** (renumber worked example to 10.7, "where this leaves you" to 10.8):

> Chapters 6, 9 and 10 so far run in the direction an auditor reads: requirement → implementation → assessment → finding → deviation. An ISMS is written in the other direction, and ISO/IEC 27001 is explicit about the order: identify risks and their owners (6.1.2 c), analyse and evaluate them (6.1.2 d–e), choose a treatment option (6.1.3 a), determine *all* controls necessary (6.1.3 b), compare with Annex A, write the Statement of Applicability with a justification for every inclusion and exclusion (6.1.3 d), obtain the owners' acceptance of the residual (6.1.3 f). BSI-Standard 200-3 is the same procedure with German names — Gefährdungsübersicht, Risikoeinstufung, Risikobehandlung, Konsolidierung — and the same four treatment options. OSCAL 1.x had a `risk` only where an assessor found one; usnistgov/OSCAL #2292 records why that cannot represent an ISO 27001 catalog. The Risk type (App. A.9b) is the missing first record.
>
> ```json
> { "id": "https://cso.example/risk/R-2026-007",
>   "scenario": { "en": "A KMS key compromised through an export path stays valid for years because keys are never rotated; every tenant record encrypted under it is exposed retroactively." },
>   "owner-ref": "https://cso.example/party/ciso",
>   "state": "treated",
>   "threat-refs": [ "https://ns.bsi.bund.de/gspp/threat/G-0.19" ],
>   "component-refs": [ "https://cso.example/component/acme-saas" ],
>   "rating": { "level": "hoch", "scale-ref": "https://cso.example/scale/bsi-200-3-matrix" },
>   "residual-rating": { "level": "gering", "scale-ref": "https://cso.example/scale/bsi-200-3-matrix" },
>   "treatment": "modify",
>   "treatments": [ { "requirement-ref": "https://ns.bsi.bund.de/gspp/req/KONF.14.1", "statement-ids": ["s2"] } ],
>   "acceptance": { "approver-ref": "https://cso.example/party/ciso", "date": "2026-11-05",
>                   "rationale": { "en": "Monthly rotation brings the residual to 'gering', within appetite." } },
>   "review-due": { "type": "calendar-period", "num": 12, "unit": "months", "calendar-ref": "https://cso.example/calendar/isms" } }
> ```
>
> Four fields carry the chapter's weight. **`treatments[].statement-ids`** is clause precision paying off a fourth time: the risk is treated by *s2*, the customer's rotation clause, and the Implementation (Ch. 9) says s1 is the provider's — so the SoA, the responsibility matrix and the risk register agree to the clause without anyone reconciling three documents. **`rating.scale-ref`** keeps Appendix F Q14's promise: the kernel carries a level and the identity of the scale it is on, and refuses to compare across scales; how `hoch` was computed is the facet's business. **`acceptance`** is the owner's signature on the residual — required the moment the risk is `treated` or `retain`ed, because silent retention is the oldest ISMS defect and a required field is the cheapest cure. **`treatment`** is the one code system two authorities publish verbatim: ISO 31000's avoid · modify · share · retain and 200-3's Vermeidung · Reduktion · Transfer · Akzeptanz are the same four words.
>
> What this makes computable is the sentence every ISO 27001 auditor asks and every ISMS answers with a spreadsheet: *which selected controls rest on no risk?* The `risk-coverage` primitive (B.1.9) resolves each Tailoring's selection and lists, per requirement, the Risks whose treatments name it. Run on this book's example bundle it reports: three selected, one justified (KONF.14.1 by R-2026-007), two uncovered (ISM-1234, IEC-CSO-IIR). Whether *uncovered* is an error is the program's policy — ISO says yes for every SoA row, BSI says the baseline justifies itself — so the primitive reports and the policy switch (`--require-risk-basis`) decides.
>
> > **Don't** encode risk acceptance as a Deviation, and don't encode a weakened requirement as a Risk. They are two acts by two roles: the owner accepts a residual (`Risk.acceptance`); an implementer weakens a clause because of it (`Deviation` of type `risk-adjustment`, which SHOULD name the Risk in `refs` — RISK-9). The corpse this honours is OSCAL's `deviation-approved` risk status, which fused the two into one state and lost the owner.

### 9.4 Chapter 14 — OSCAL 1.x migration, new row
| OSCAL 1.x | JASCON | Notes |
|---|---|---|
| `assessment-results` / `poam` `risks[]` | **Risk** object (`risk-status` → `state`, `statement` → `scenario`, `deadline` → `review-due`, `threat-ids` → `threat-refs`, `related-observations` → evidence on the Finding) + `Finding.risk-refs` | `characterizations`, `mitigating-factors` → the parked `risk-analysis@1` facet (L2 holding pen until measured); `remediations` stay `Finding.actions[]`; `deviation-approved` status splits into `Risk.acceptance` + a `risk-adjustment` Deviation |

### 9.5 Appendix A — insert A.9b (table in §4 above), plus
- A.8 Finding: add `risk-refs` ○ [URI] — "the ex-post record points at the ex-ante one; landmark".
- A.0 footnote: the ten-type disjointness set is MINIMAL in `validate_core.py`.
- A.12 ledger: **exercised** — Risk in the example bundle and 31 vectors; **declared, not corpus-exercised** — Risk at scale (IFA re-run is the work order).

### 9.6 Appendix B — B.1.9 `risk-coverage`
> **What it computes:** for each Tailoring, the selected requirements (set-refs expanded, excludes removed) joined to the Risks whose `treatments` name them. **Output:** `covered`, `uncovered`, `excludes-without-rationale`, `treatment-out-of-scope`. **Verdict:** report by default; `uncovered` fails only under the program's policy; `treatment-out-of-scope` always fails (RISK-11). **Rationale:** ISO 27001 6.1.3 b/d make "every control rests on a treatment decision" a documented property; a property that can be computed must not be audited by hand. **Failure:** `FAIL [risk-coverage] <tailoring> selected <req> is named by no Risk — ISO/IEC 27001 6.1.3 d: inclusion carries its justification`.

B.4: "nine, eight, and three — every one carrying the reason it exists". The ninth arrived with its counts (§2), its corpus cases (`risk-vectors.json`) and one implementation; the second implementation is the release gate, as for everything else.

### 9.7 Appendix C
- **C.3c Risk states:** `identified · assessed · treated · retired` — forward only, skipping allowed, `retired` terminal (a recurrence is a new Risk). Rationale: the Finding smallness rule; dispositions are the `treatment` code, not extra states.
- **C.10 Small sets**, add: **Risk treatment options:** `modify · retain · avoid · share` — adopted, not invented: ISO 31000 §6.5.2 / ISO 27005 §8.6, identical one-to-one with BSI 200-3 (Reduktion · Akzeptanz · Vermeidung · Transfer); SP 800-39's share + transfer both map to `share`. Observed in the corpora: 0 — the gate-3 IFA re-run is the first measurement.

### 9.8 Appendix D — new parked entry
> **`risk-analysis@1`** — *parked, named exit*: likelihood, impact, method-ref, characterizations, mitigating factors — everything Q14 keeps out of the kernel. First corpus: the IFA `risk@1` framework facet (shipped, 2 risks); second: a BSI 200-3 Risikoanalyse export. Ships when measured, not before.

### 9.9 Appendix F — Q14 rewrite
> **Q14. Where's risk modeling — likelihood, impact, scoring?**
> Scoring is in facets; the risk is in the kernel (1.1.0). The split is the measured one: four authorities (ISO 27001/27005, BSI 200-3, SP 800-30, OSCAL's own AR/POA&M) encode *the same* risk record — owner, scenario, level, treatment option, treating controls, residual acceptance — and *different* ways of computing the level. The record is a kernel type (A.9b) so that a selected requirement can name the risk that justifies it (ISO 6.1.3 b/d — the question OSCAL #2292 found unanswerable in 1.x); the computation is a facet (`risk-analysis@1`, parked until measured) so that CVSS, FAIR and the 4×4 matrix coexist under contract. `rating` carries only a level on a named scale and compares nothing across scales. `privacy-assessment@1` stays parked for the same discipline.

### 9.10 Appendix G — glossary
- **Risk** — the ex-ante record: a scenario with an owner, a state, a level on a named scale, a treatment decision and the requirements that carry it. Tenth kernel type (1.1.0). (Ch. 10 §10.6, App. A.9b)
- **Risk owner** — the party accountable for a Risk and the signer of its `acceptance` (ISO 27001 6.1.2 c 2).
- **Treatment option** — one of `modify · retain · avoid · share`; the ISO 31000 set, identical with BSI 200-3's. (App. C.10)
- **risk-coverage** — the ninth primitive: which selected requirements are justified by a Risk, which are not. (App. B.1.9)
- **Statement of Applicability (SoA)** — in JASCON a *computation*, not a document: a Tailoring's selection and excludes (with rationale) joined to the Risks that justify them.

### 9.11 examples/README_1.md — new row
| 10 | Risk | `risk-acme-kms-key-rotation.json` | treated risk on a BSI 200-3 scale, G 0.x threat refs, **treats KONF.14.1 s2** (the same clause finding 017 is against, which now carries `risk-refs`), CISO acceptance of the residual, 12-month calendar review |

---

## 10. Objections anticipated

**"This is scope creep into GRC-tool territory."** The kernel takes nine fields that four authorities agree on and refuses everything they disagree on. A GRC tool's heat map is a facet plus a rendering; the kernel only guarantees that the map's cells point at real requirements.

**"BSI doesn't need it; the Bausteine are the risk analysis."** For normal Schutzbedarf, yes — and that is why `uncovered` is a report, not an error. For hoch/sehr hoch, 200-3 produces exactly this record and today has nowhere in JASCON to put it except a facet nobody else can read.

**"Why not a Mapping from Risk to Requirement?"** Mapping is a *claim about two requirements* with IR 8477 semantics and third-party provenance. "This control treats this risk" is a *decision* by the risk owner, not a claim about equivalence; it belongs on the object whose owner made it.

**"The owner field will be a role URI, not a person."** Correct, and intended — the same convention as `obligated-parties` and `approver-ref`.

**"Two implementations?"** One ships here; the gate is unchanged. The vectors are the contract.

---

## 11. Landing addendum (2026-11-10) — what contact with the repository changed

The proposal was written against the synced skill bundle. The repository holds four things that bundle does not: the released specification and its decision register, the eleven converted corpora, the PowerShell twin validator, and the reader. This section is the record of meeting them.

### 11.1 What held

- `CP-RISK-1.patch` applied to the repository without a single rejected hunk; the result was byte-identical to the shipped bundle.
- **The compatibility promise of §7 is measured, not asserted:** under the 1.1.0 schema all 6,914 objects of the 1.0.0 corpus still match exactly one kernel shape — zero new failures across eleven bundles.
- The design of §3–§6 survived review unchanged in its structure: record in the kernel, computation in a facet, coverage as a report with a policy switch.

### 11.2 Corrected on landing

Each row was demonstrated failing against the validator as proposed, then fixed, then pinned by a vector. Run the current `risk-vectors.json` against the validator from the 2026-11-05 archive: 33 pass, 9 fail — the nine behavioural rows below.

| # | Defect in the proposal's implementation | Why it matters | Landed fix | Vector |
|---|---|---|---|---|
| R-1 | **RISK-11 fails falsely under a predicate select.** The primitive does not expand predicate selects (§6 says so), then fails any treatment whose requirement it did not find. | A hard failure computed from knowledge the primitive admits it lacks. | A Tailoring with a predicate select has an *open* selection; RISK-11 is reported "undecided", never failed. | `predicate-select-leaves-risk-11-undecided` |
| R-2 | **A retired Risk justifies its control for ever.** Coverage counted every Risk whose treatments name the requirement, whatever its state. | Coverage could only grow; "retired is terminal" (C.3c) had no consequence. | Only *live* Risks justify (`state` ≠ retired, `lifecycle` ≠ withdrawn); the others are listed as `lapsed`. | `retired-risk-justifies-nothing`, `withdrawn-risk-justifies-nothing` |
| R-3 | **Retiring a risk and then dropping its control fails RISK-11 permanently.** | The ordinary end of a treatment became an unfixable failure — or an incentive to falsify the retired record. | RISK-11 binds live Risks only. | `retired-risk-outside-the-soa-is-history` |
| R-4 | **Set expansion stopped silently at depth 8.** | A requirement under deeper nesting vanished from the selection without a word (D21 sets no depth limit). | Iterative expansion to any depth; the seen-set terminates malformed cycles. | `deeply-nested-sets-are-expanded` |
| R-4b | **RISK-11 was skipped when the selection was empty.** | The fully-descoped SoA — the worst case — passed. | The rule applies wherever a Tailoring exists. | `everything-excluded-then-treated` |
| R-5 | **Risk edges were untyped.** `treatments[].requirement-ref` accepted a Set id (and then produced a misleading RISK-11); `component-refs` accepted a Requirement; an in-bundle `risk-refs` target could be anything. | Coverage joins on Requirement ids — a mistyped edge silently justifies nothing. | **RISK-12** (new): a Risk edge is typed. `risk-refs` stays landmark but binds if the target is present, like a Mapping scope. | `treatment-names-a-set-not-a-requirement`, `component-ref-names-a-non-component`, `finding-risk-ref-names-a-non-risk` (+ `finding-risk-ref-is-landmark`) |
| R-6 | **§5's failure messages were not implemented.** A Risk violating RISK-3 printed jsonschema's "'acceptance' is a required property", not `FAIL [RISK-3] …` with its rationale; the vectors asserted that library's wording. | Chapter 15.4: the rationale prints on failure. And a second implementation cannot be held to another library's message text. | `risk_rule_violations()` names the rule and prints its why; vectors gain the portable `expected-rule` (`expected-frag` stays, advisory). New negative vector for RISK-1. | `risk-without-owner` + `expected-rule` on six existing vectors |
| R-7 | The B.1.9 failure was printed in a different format than B.1.9 specifies. | One normative FAIL format (the conditional-apply precedent). | Printed as specified, reading "named by no live Risk". | — (message format) |
| R-8 | Docstring said "for every consumer Tailoring"; code and B.1.9 say every Tailoring. A dead `risk-transitions` loop sat in `run_lifecycle`. | Tier-scoping the policy switch would exempt an organisation's SoA over its own catalog (authority-claimed). | Docstring aligned to the code; dead loop removed. | — |

**Rule table as landed:** RISK-1…RISK-11 as in §5, with RISK-11 reading "*a live* Risk's treatment may not name a requirement that no Tailoring in the bundle selects (undecided under an open selection)", plus **RISK-12** — *a Risk edge is typed: `treatments[].requirement-ref` names a Requirement, `component-refs` name Components, and a `Finding.risk-refs` entry that resolves in-bundle names a Risk* — rationale: coverage joins on Requirement ids; a mis-aimed reference is a wrong statement, not a loose one.

**Shape as landed:** §4 with one change — `review-due` is `date | datetime | elapsed-duration | calendar-period`, the two points in time spelled `{type, value}`. Reason: OSCAL's `deadline` is date-time-with-timezone, both corpus deadlines are date-times, and the proposal's `{type: "date", date}` spelling had zero instances anywhere while the corpus already spelled Finding action deadlines `{type: "datetime", value}`.

**Vectors as landed:** 42 (16 object · 18 bundle · 8 transitions), up from 31. Conformance corpus: **200 vectors, 13 families**.

### 11.3 Claims in §1–§10 that do not hold

1. **§7, the manifest pin** — struck in place. Nothing in a bundle pins the kernel version. The example manifest's `manifest-version: "1.1"` was reverted to `"1"`: it versions the manifest *format*, which did not change, and all eleven corpus manifests, the converter library and the reader write `"1"`. Whether a kernel pin should exist is backlog #44 — *decided and built the same day: `kernel-version`, specification D3.6.*
2. **§7, "minor".** The released specification says otherwise, twice: D22 rev 3 — "Post-1.0, kernel promotion requires measured 2-of-3 and a **major** version under D3.5 governance"; IV.8 — "kernel-shape changes ride major versions". §7's argument (additive, every prior object stays valid) is a coherent definition of a minor and agrees with D3.5's own wording for facets, but it contradicts those two sentences, and D22's first test ("≥ 2 of 3 independent authority encodings *in the census corpus*") is not what §2 counts — §2 counts standards. This was the author's decision (backlog #40), and it is taken: **2.0.0, D22 unamended** — §12.
3. **§2, "four authorities … agree on the shape."** True of ISO 27001/27005, BSI 200-3 and SP 800-30 as standards. Of OSCAL *as data* it is half true: the corpus (§11.4) shows three of the six record fields arriving (scenario, treatment option, treating controls) and three absent (owner, level, dated acceptance).
4. **§8 item 4, tightening `Finding.actions[].due`** is described as "correct per A.8, deferred so no shipped bundle breaks". By §7's own promise it is a *breaking* change — a 1.0.0-valid Finding with any other `due` object would stop validating — so it belongs to the major-version decision, not to a converter re-run. Not done.
5. **§9.7, "Observed in the corpora: 0"** for treatment options — now 2 (§11.4), and the OSCAL side of the mapping is wider than §2 says: seven response types, of which `contingency` and `none` have no JASCON code.

### 11.4 The first corpus measurement — IFA re-run

Sources: `usnistgov/oscal-content@9402f031` (2026-07-14 — the state the 1.0.0 conversion fetched; upstream has since changed the IFA files). The unchanged converter reproduces the committed 1.0.0 bundle from that commit with zero diff, on Linux — so every difference below is attributable to this change.

- **Emitted:** 17 objects (15 + 2 Risks), 835/835 source paths mapped, bundle green. Findings carry `risk-refs`; the `risk-adjustment` Deviation names its Risk (RISK-9 at corpus scale, ×1); the `risk@1` framework facet is retired.
- **Sourced fields:** `statement` → `scenario` ×2 · `deadline` → `review-due` ×2 (date-time) · POA&M `system-id` → `component-refs` ×2 · response `type` prop → `treatment` (`mitigate` ×1 → `modify`; `accept` ×1 → see below) · the AR finding's `related-risks` edge → `treatments[]` ×1.
- **What OSCAL cannot give the shape — reported, not filled in:**
  - **No owner** (×2). OSCAL's risk assembly has no owner field. `owner-ref` is derived from the imported SSP's `owner` role and the derivation is declared in the coverage report. RISK-1 makes this the one field a converter *must* derive.
  - **No level** (×2). A characterization carries `likelihood` and `impact` under a scale `system`; the combined level is not in the data. RISK-2 therefore holds both risks at `identified`, although both were demonstrably analysed. `assessed` and `treated` are unreachable from OSCAL without computing a level — which §3 says is the facet's business.
  - **No dated acceptance** (×1). The `deviation-approved` risk has an `accept` response whose narrative is the rationale and names the approver in prose; there is no date. RISK-6 therefore forbids `treatment: retain`. A date was not invented; the option is carried in the facet and the approval stays on the Finding's Deviation.
- **Consequence for §3/§5 (backlog #43 — decided, §12: the rules stay):** the kernel requires three things the fourth authority's data does not hold. Either that is the kernel being right (ISO 6.1.2 c–e and 6.1.3 f do require an owner, an evaluated level and a recorded acceptance, and an OSCAL export of an ISMS register *should* fail to round-trip silently), or RISK-2/RISK-6 are one notch too strict for imported data. The corpus says which fields; the author says which reading.

### 11.5 Found on the way (outside this proposal's scope, recorded in the register)

- **L-1 — the 1.0.0 corpus does not verify on a non-Windows clone.** 6,963 package-digest failures (6,914 objects + 49 pinned schemas): the manifests digest CRLF bytes, git stores LF. Fixed by `.gitattributes` and explicit converter line endings, with no digest re-spelled; limits and the alternative are in the file and backlog #42.
- **L-2 — path coverage is not value arrival.** The coverage reports count source *paths* that have a declared destination. A value-level check on the IFA corpus finds 122 content values (63 of them prose) that do not occur in the 1.0.0 bundle, including — under `poam.risks[]` alone — 13 that this re-run now carries, the risk response type among them. The other ten corpora are unmeasured. Backlog #41.
- **L-3 — the example bundle's manifest was never verified**, and at 1.0.0 its package digests were a mix (8 CRLF, 4 LF). Now verified on every run. Its attestation's subject digests bind nothing (backlog #46).

### 11.6 State of the gate

| Check | State |
|---|---|
| Python reference validator | 200/200 vectors · 11 bundles · 6,916 objects · both digests · **ALL GREEN** (Linux) |
| PowerShell twin | Ported (Risk type, RISK-7/8/12, risk-coverage, 42 vectors, `-RequireRiskBasis`). **Not executed** — no PowerShell runtime was available where the port was written. One implementation, not two, until a run on Windows PowerShell 5.1 is green. **2026-11-11: executed and green** — 258/258 vectors, five bundles and the example folder, every count equal to the Python reference's (spec IV.5b item 3). |
| OSCAL export suite | Not re-run: its inputs (the ten catalog bundles) are byte-identical; the NIST schema it needs is not in the repository. |
| Reader | v1.7.2 recognises the Risk type; verified in headless Chromium on the re-converted IFA bundle (17 objects, 2 typed `risk`, no page errors). |
| Release | **Not yet.** Version decided: 2.0.0 (§12). No tag — the PowerShell run comes first. The 2.0.0 specification text exists as a release candidate (`drafts/oscal-semantic-core-specification-2.0.0-rc.1.md`). |

---

## 12. Decisions of 2026-11-10 (author)

Put before the author with §11: *"The register (D22 rev 3) and spec IV.8 say post-1.0 kernel changes need a major version. Either release as 2.0.0 or amend D22 on the record."* Answered the same day.

1. **Version — "v2". The kernel that carries Risk is 2.0.0.** D22 rev 3 stands as written; no rev 4. The schema is `oscal-semantic-core-2.0.0.schema.json` with `$id` `https://ns.oscal.org/semantic-core/schema/2.0.0`; the working label "1.1.0" was replaced in the schema, both validators, the vectors, the handbook, SKILL.md, the reader and the converter in one pass, and survives only in §1–§11 above, kept as written.
   - **A major by rule, a superset in fact.** Nothing in 2.0.0 invalidates 1.0.0 content — all 6,914 objects of the 1.0.0 corpus validate unchanged, so a 1.0.0 bundle *is* a 2.0.0 bundle. The reverse does not hold (a 1.0.0 tool cannot type a Risk), and that asymmetry is exactly what a major number tells a consumer. §7's compatibility argument is therefore kept as a measured *property* of 2.0.0, and dropped as an argument for the number.
   - **What "v2" does not settle.** D22 rev 3 asks two things of a post-1.0 promotion: a major version — now met — and *measured 2-of-3* authority encodings in the census corpus. Risk does not meet the second as written: none of the three census corpora encodes a risk record, and the one corpus that does (IFA) supplies half of it (§11.4). The register records the promotion as an **author-decided exception to test 1**, not as a pass, and files the question the exception raises — a risk register is consumer-side data no catalog publisher ships, so test 1 as worded can never admit a consumer-side type — as backlog #48.
   - **What the major opens and was not taken.** The 1.0.0 record tied two things to "a major version, should one ever exist": re-spelling the machine identifiers (`oscal-semantic-core` in namespace URIs, the media type, schema filenames), and — by this document's own §8 — tightening `Finding.actions[].due`. Neither was done: identifiers are unchanged ("identifiers that are hashed do not move"), and the tightening would end the superset property above. Both stay open until the tag.
2. **RISK-1/2/6 against OSCAL data (backlog #43) — "keep".** The rules stay as written: `assessed`/`treated` require a `rating`, `retain`/`treated` require a dated, attributed `acceptance`, every Risk has an owner. An OSCAL import that lacks them stays `identified` and carries its source status in a facet. Reasons on the record (register "Amendments — the Risk rules stay"): the states keep one meaning for every bundle; loosening later never invalidates data already written, tightening later would; and the evidence for change is one fictional example with two risks.
3. **Raw-blob line endings (backlog #42)** — first deferred, then done the same day: bundle files are `-text` and the blobs hold the digested CRLF bytes, so raw blob access verifies as well (§11.5 L-1 described the gap).
4. **License — Apache-2.0.** `LICENSE` and `NOTICE` at the repository root, a copy of the license in the skill folder.

---

## 13. External review of 2.0.0-rc.1 (2026-11-10) — nine findings

A review of the pull request and of the concept, done against the branch
as pushed. Each behavioural finding was reproduced with a crafted bundle
against `validate_core.py` before anything was changed, and is now pinned
by vectors: run the current `risk-vectors.json` against the validator of
commit `6b71647e` — 42 pass, 23 fail.

| # | Finding | Why it matters | Fix | Vectors |
|---|---|---|---|---|
| X-1 | **Any live Risk with `treatments` counted as a justification.** A `draft`, `identified` Risk with no level, no option and no acceptance covered its requirement. | `--require-risk-basis` was satisfied by a three-field stub, while RISK-2/3/6 were strict about fields the coverage join never read. Both IFA risks were exactly this case. | A Risk **justifies** only when it is live, not `draft`, `assessed` or `treated`, and carries a `treatment`. Others are reported as `pending`. The normative failure now reads "justified by no Risk". | `identified-risk-justifies-nothing`, `assessed-risk-without-option-justifies-nothing`, `draft-risk-justifies-nothing` |
| X-2 | **Coverage was not scoped.** With two Tailorings in a bundle, one Risk justified the same control in both; RISK-11 used the union of all selections. | A risk about system A justified the control in system B's Statement of Applicability. | New optional field **`tailoring-refs`** on Risk (closure-required, typed): the Risk justifies, and is held to RISK-11, only there. Unscoped Risks behave as before; **RISK-14** (SHOULD) notes them where more than one Tailoring is in force. | `scoped-risk-justifies-only-in-its-tailoring`, `unscoped-risk-among-two-tailorings-noted`, `scoped-risk-outside-its-own-tailoring`, `tailoring-ref-names-a-non-tailoring`, `tailoring-ref-not-in-bundle` |
| X-3 | **Withdrawn Tailorings and withdrawn Requirements still counted** as selecting and selected. | Liveness had been applied to Risks only: a withdrawn SoA kept a control "in scope", and a withdrawn requirement demanded a risk basis. | A withdrawn Tailoring is not reported and selects nothing; a withdrawn Requirement is dropped from the selection, and a live Risk that names it fails RISK-11. | `withdrawn-tailoring-selects-nothing`, `withdrawn-requirement-is-not-selected`, `risk-leans-on-a-withdrawn-requirement` |
| X-4 | **`selects[].set-ref` and `excludes[].ref` were untyped** — the defect R-5 fixed for Risk edges. A `set-ref` aimed at a Tailoring selected nothing and derived as authority-claimed; an exclude aimed at a Set removed nothing. | Silent empty selections. | Closure rule: `set-ref` names a RequirementSet; an exclude names a Requirement or a Set, and a Set excludes its members. No 1.0.0 object is affected (checked: all six Tailorings of the 1.0.0 corpus select Sets, none carries an exclude). | `select-names-a-tailoring-not-a-set`, `exclude-names-a-set-and-excludes-its-members`, `exclude-names-a-component` |
| X-5 | **"Dated acceptance" was not dated.** `acceptance.date: "neulich"` validated, as did a `review-due` of −3.7 months. | §12.2 keeps RISK-6 strict for the sake of a *dated* acceptance. | Schema: `acceptance.date` and `review-due` dates are `YYYY-MM-DD`; `datetime` is RFC 3339 with an offset; duration `num` is a positive integer. Risk is new in this candidate, so nothing released is affected; both IFA deadlines conform. | `acceptance-date-is-not-a-date`, `review-due-negative-period`, `review-due-fractional-duration`, `review-due-date-is-not-a-date`, `review-due-datetime-needs-time-and-offset` |
| X-6 | **Rating consistency was claimed and not checked** (D23: "a validator checks presence and consistency"). A residual on another scale than the rating passed; so did a residual without a rating. | Levels never compare across scales — a residual on another scale says nothing about the reduction. | **RISK-13**: `residual-rating` presupposes `rating` (schema conditional), on the same `scale-ref` (graph rule). | `residual-rating-without-rating`, `residual-rating-on-another-scale` |
| X-7 | **One open selection anywhere disabled RISK-11 for the whole bundle.** | An unrelated predicate-select Tailoring turned every failure into "undecided". | Follows from X-2: RISK-11 is asked of the Tailorings a Risk belongs to; only an open selection among *those* leaves it undecided. For an unscoped Risk the bundle-wide reading stays — there it is the honest answer. | `open-tailoring-elsewhere-decides-nothing` |
| X-8 | **The README headline contradicted the branch**: "nine object types", "157-vector", "pre-1.0", "converted losslessly" — the last against this document's own L-2. | The first screen is what a reader believes. | Headline reworded; "losslessly" replaced by what was measured (100 % declared path coverage; value arrival measured on one corpus, and not holding there). The GitHub repository description still carries the old sentence — it is not in the tree and has to be edited by the owner. | — |
| X-9 | **The Mapping Model was dated "March 2026 with v1.2.1".** The OSCAL release notes say: "OSCAL 1.2.0 is a minor release which provides an additional OSCAL Model: Control Mapping" (v1.2.0, 12 December; v1.2.1 followed on 6 March, v1.2.2 on 30 April, v1.2.3 on 7 August 2026 and is the current release). | A wrong date in the comparison baseline, repeated in the handbook. | Corrected in the 2.0.0 candidate, Chapters 2 and 8 and the model overview. The released 1.0.0 text and the register journal are left as written; the candidate carries the erratum. | — |

| X-10 *(found after the merge)* | **Under `--require-risk-basis` a bundle with a Tailoring and no Risk at all passed.** Bundle validation printed and enforced the report only where at least one Risk existed. | The emptiest register satisfied the strictest policy. | The switch applies regardless of the number of Risks; without it, a Risk-free bundle stays silent as before. Reproduced on a four-object bundle (two requirements, a Set, a Tailoring): 0 failures before, 2 after. | — (bundle-run behaviour, outside the vector format) |

| X-11 *(author, after the merge)* | **A bundle without any Tailoring produced no coverage report at all.** "If there is no tailoring, all controls are in play." | A register beside an untailored catalogue was never asked which controls rest on no risk. | With no Tailoring in the bundle every Requirement in force is selected implicitly (report key `*`); the policy switch and RISK-11 apply to it. A bundle whose Tailorings are all withdrawn still selects nothing. The IFA bundle now reports: 2 in play, 0 justified, both pending. | `no-tailoring-every-requirement-is-in-play`, `no-tailoring-risk-leans-on-a-withdrawn-requirement` |

| X-12 *(author, after the merge)* | **Likelihood and impact were facet-only.** "Think we need those." | Three standards and OSCAL's data name exactly these two inputs; §3 kept them out together with the computation. | `rating` and `residual-rating` may carry `likelihood` and `impact`, each `{level, scale-ref}`. RISK-13 extended to them. The matrix, CVSS, FAIR and impact per dimension stay in the facet. An OSCAL risk still cannot use them: they sit inside a rating, and it has no level. | `rating-with-likelihood-and-impact`, `likelihood-without-scale`, `rating-with-an-unknown-input`, `impact-with-a-dimension`, `residual-impact-on-another-scale`, `residual-carries-only-one-input` |

| X-13 *(author, after the merge)* | **Scales were names without definitions.** "Likelihood should be editable, wording and how many levels; same for impact." | A `scale-ref` was a bare URI and a level a free string: a typo was a new level, and nobody could read how many levels a scale had. | Scale definitions as files the manifest pins under `scales` (not a kernel type): levels in order, the organisation's wording and number. SCALE-1 (the definition), SCALE-2 (a stated level is a defined one), SCALE-3 *(SHOULD)* (a residual is not above what it remains of). | `scale-vectors.json` ×9 |

| X-14 *(author, after the merge)* | **The matrix had no home.** The kernel left it out, the text assigned it "to a facet", and no such facet is registered; a workspace file would have been neither digested nor attested. | A register stated a level, a likelihood and an impact that nothing could check against each other. | `matrix` in the pinned definition of the level scale. **SCALE-4**: a rating that states both inputs states the level of their cell; a mismatch fails ("fail on mismatch"), unless the rating carries `override-rationale`. | `scale-vectors.json`, the nine matrix cases |

**Rule table after the review:** RISK-1…RISK-12 as in §11.2, with RISK-7
and RISK-12 extended to `tailoring-refs` and RISK-11 asked per Tailoring;
**RISK-13** — *`residual-rating` presupposes `rating`, on the same scale*;
**RISK-14** *(SHOULD)* — *where more than one Tailoring is in force, a Risk
names the Tailoring its treatment belongs to*.

**Vectors after the review:** 73 (27 object · 38 bundle · 8 transitions).
Conformance corpus: **225 vectors, 13 families** (258 in 15 with the
kernel-pin and scale families, D3.6, D3.7). Python reference
validator: 258/258 and all shipped bundles, ALL GREEN.

**What the review did not settle.**

1. **The PowerShell twin is still unexecuted**, and now carries more
   unexecuted code: every change above was ported to it by reading. The
   expected line is `risk: 73 pass, 0 fail`. Backlog #45 stands.
   *(2026-11-11: run on Windows PowerShell 5.1 — `risk: 73 pass, 0
   fail` and ALL GREEN; #45 closed.)*
2. **X-1 makes the first Risk corpus justify nothing.** Both IFA risks are
   `identified` (§11.4), hence `pending`. That is §12.2 followed to its
   consequence. *(Since X-11 the IFA bundle is reported: two requirements
   in play, none justified.)*
3. **`tailoring-refs` is the join that exists, not the one ISO describes.**
   A Statement of Applicability belongs to a scope; the kernel has no edge
   from a Tailoring to a Component. Adding one is a 1.0.0-shape change and
   an author decision (backlog #51).
4. **Not changed, deliberately:** `Deviation.opened` is as free a string as
   `acceptance.date` was, but it is a released shape (backlog #52, with
   #47a); a single `treatment` code cannot say "modify and share", which
   ISO/IEC 27005 allows (not in the backlog yet); `treated` does not look at the
   Implementation status or open Findings of the treating controls; and
   whether a legal or contractual duty may justify an SoA row without a
   Risk is still the policy switch's business (§8 item 5).
5. **Concept-level findings of the same review**, recorded in the register
   and not acted on here: no extension point for new object types, no type
   discriminator and no kernel-version pin (#44), identifiers minted under
   other organisations' domain names, and the prior art the specification
   never named — now `PRIOR-ART.md`.
