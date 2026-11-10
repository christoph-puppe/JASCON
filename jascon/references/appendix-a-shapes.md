# The JASCON Handbook
# Appendix A — Shapes Reference

**Purpose:** the ten types, two sub-objects, and bundle artifacts,
field by field — with the evidence column that makes this appendix
different from a schema dump: which measured corpus reality each field
answers to. Counts cite the three-authority census and the gate-item-1
converter runs (ISM 36,161 · BSI 49,804 · CR26 7,294 leaf values, all
at 100 % declared coverage).
**Convention:** ● required · ○ optional. Field names are normative;
prose here is explanatory, the conformance corpus is definitive.

---

## A.0 Common fields (every object)

| Field | | Type | Meaning & evidence |
|---|---|---|---|
| `id` | ● | URI string | Globally unique, authority-minted, never resolved by tools (string comparison only, D2). Evidence: the twin-catalog collision — 11 shared id strings across two BSI publications, only 1 prose-identical. |
| `version` | ● | string | Object-level version; format is the authority's (dates, semver, timestamps all observed). Absorbs `revision`/`updated` props (ISM ×2,202; CR26 `updated[]` ×377+). |
| `label` | ○ | string | Human display handle. Evidence: ISM `label` ×49 + 1,101 id-derived; BSI group labels ×162; CR26 rule ids as labels. |
| `aliases` | ○ | [{scheme, value}] | Other names, with provenance. Absorbs `alt-identifier` (BSI ×1,219 incl. params), FRD `alts` (×188, in-payload). |
| `lifecycle` | ● | code (A → C.2) | draft · active · deprecated · withdrawn. |
| `title` | ○ | text | Display title — `text` = `{BCP-47: string}` (#12 delivered; D9 rev 2: EU standards must be available in all 27 official languages). All kernel human-readable fields (title, rationale, description) are `text`; identifiers and labels stay strings. |
| `relations` | ○ | [{type, ref}] | Typed outbound links: base codes `related`, `required`, `uses-term`, `reference`, `schema` (C.8; `supersedes` removed v0.6 — backlog #20); extension types SHOULD be namespaced URIs (schema constraint pending the converter rerun that migrates the corpus's bare-word `sharpens` ×28). Evidence: BSI links ×197+67; CR26 `related` ×23, `schema` ×24, `terms` ×222. |
| `facets` | ○ | {facet-uri@major: payload} | Registered extensions; schema-pinned via manifest; semantics per declaration (D10). |
| `annotations` | ○ | {string: any} | Chrome. Compliance-invisible, digest-excluded, strippable. Evidence: `web_name`, `do_not_link` (CR26). |

**Canonical-alias & replaces** (identity events, on the *new* object):
`canonical-alias` ○ {of: URI} — same content, new home (rebrand/domain
loss). `replaces` ○ [{ref, mode}] with mode ∈ revised · split-from ·
merged-into · renamed — content-lineage events. Evidence: the
registry-rot corpse; ISM's own OCR→ISM renumbering history.

---

## A.1 Requirement

| Field | | Type | Meaning & evidence |
|---|---|---|---|
| `statements` | ● | [Statement] | The clause layer. Evidence: 347 BSI nested pseudo-controls (nesting measured to depth 3–4) → 1,015 statements in the converted bundle. |

**Statement:**

| Field | | Type | Meaning & evidence |
|---|---|---|---|
| `id` | ● | string | Unique within the Requirement; stable and citable (tailoring ops, findings, mapping scopes, statement-refs all address it). Converters mint `smt` for the own-clause, child-control ids for flattened clauses. |
| `modality` | ● | code (C.1 lattice) | unspecified · may · should · must · should-not · must-not · may-only. Evidence: BSI `modal_verb` ×1,006 (should 626 / may 225 / must 155); CR26 `force` 246 layered; ISM structurally modal-free → honest `unspecified` ×1,149. |
| `obligated-parties` | ● | [code/ref] | Who the clause binds. Evidence: CR26 `affects[]` (Providers 159 / Agencies 24 / Assessors 23 / FedRAMP 16 / Advisors 3); BSI/ISM: documented single-party defaults. |
| `parameters` | ○ | [Parameter] | Declared insertion points; prose references them as `{param:name}` — an unbound token is a validation error (the 216 lesson). |
| `prose` | ● | text | The normative text — `text` = `{BCP-47: string \| [string]}` (the #12 primitive; formerly named langMap). |

**Parameter algebra (D9/D14):** every parameter carries `name` ● and
`type` ●, optionally `label` ○ (display handle — never an identifier,
never compared) and `default` ○ (advisory, type-valid; resolution
never substitutes it silently — binding is `set-parameter`-only), plus
type-specific fields —

| type | extra fields | evidence |
|---|---|---|
| `string` | — | BSI params ×147 (label/default first-class since the v0.6 cycle — D9 rev, backlog #1; the L2 `param-extras` residue ×179 drains at the next converter run). |
| `choice` | `choices[]{value,label}` ●, `cardinality` (one \| many) | the fused-alternatives lesson ("TLS 1.3 *oder* …"). |
| `integer` | `min?`, `max?` | ODP bounds. |
| `decimal` | canonical **string** value, `min?`, `max?` | JCS float hazard (D3). |
| `elapsed-duration` | `num` ●, `unit` ● ∈ seconds·minutes·hours | CR26 clocks that run through weekends. |
| `calendar-period` | `num` ●, `unit` ● ∈ days·bizdays·weeks·months·years, `calendar-ref` ● | CR26 bizdays; fail-closed without the calendar. True unit-class crossings measured: **0** (51 first-pass flags were base-absent variants, resolved by the D13 rev — authority-tier ceremony; duration-union question closed no-change, backlog #3). |
| `uri`, `date` | — | declared; not yet corpus-exercised. |

Any parameter may declare `tightening` ∈ lower · higher · none —
which direction counts as stricter (deadlines: lower).

---

## A.2 RequirementSet

| Field | | Type | Meaning & evidence |
|---|---|---|---|
| `members` | ● | [{ref ●, sequence ○}] | Refs to Requirements **or Sets** (nesting = taxonomy & composition, D21). Evidence: membership was the #1 prop imitation — ISM applicability ×5,301 + E8 ×256; BSI sec_level ×998; CR26 subsets/classes/types — all now Sets (589 across the three bundles). `sequence` absorbs sort-id ×2,870. |

Sets-of-sets composition measured live: CR26 class Sets (a–d) and
track Sets (20x/Rev5) are built purely from subset-Set members.

---

## A.3 Tailoring

| Field | | Type | Meaning & evidence |
|---|---|---|---|
| `selects` | ● | [{set-ref} \| {predicate}] | What's in scope; predicates are the closed D14 set. A `set-ref` is closure-required and **typed: it names a RequirementSet** — anything else selected nothing, silently (rc.1 review). |
| `excludes` | ○ | [{ref, rationale?}] | **Selection, never Deviation** (D13) — scoping out is not weakening. `ref` names a Requirement **or a RequirementSet, whose members it excludes**; any other type is an error. |
| `operations` | ○ | [Operation] | Ordered; identity-addressed; same-target twice = error; chaining only via explicit `override`. |
| `deviations` | ○ | [Deviation] | Ex-ante channel — a weakening op **must** reference one. Evidence: CR26's 111 class-variant modality ops needed **zero** (every published delta tightens — measured, not assumed). |

**Operations (D13, closed set of 8):** each op carries
`requirement-ref` ● + `statement-id` ● where it touches a statement.

| op | payload | law |
|---|---|---|
| `set-parameter` | `parameter` ●, `value` ● | value must satisfy declared type **and bounds/choices**; loosening bounds ⇒ Deviation. |
| `set-modality` | `modality` ● | lattice-monotone free; easing ⇒ Deviation; axis change ⇒ Deviation. |
| `set-field` | `field` ●, `value` ● | whitelisted non-normative fields. |
| `replace-prose` | `prose` ●, `intent` ● ∈ editorial · substantive | substantive ⇒ Deviation. Misdeclared intent is forgery (14.2). |
| `add-relation` / `remove-relation` | `relation` ● | graph edits, logged. |
| `attach-facet` / `detach-facet` | `facet` ●, payload | semantics-modifying facet changes ⇒ Deviation. |

---

## A.4 Mapping

| Field | | Type | Meaning & evidence |
|---|---|---|---|
| `source-ref` / `target-ref` | ● | URI | Requirement endpoints. |
| `source-scope` / `target-scope` | ○ | ["statement:<id>"] | Clause precision. |
| `relationship` | ● | code (C.5, IR 8477/OLIR) | equal · subset-of · superset-of · intersects · supports · conflicts. |
| `direction` | ● | code | source-to-target · bidirectional. |
| `confidence` | ● | code (C.7) | draft · reviewed · authoritative. |
| `rationale` | ○ | string | Why the relationship holds. |
| `provenance` | ● | {author-ref ●, date ●} | **Whose claim this is** — the third-party-crosswalk ownership answer. Evidence: 373 Mapping objects minted from CR26 KSI links at honest `supports`/`draft` (8.6 untyped-import rule). Contradictory mappings coexist by design. |

---

## A.5 Component

| Field | | Type | Meaning & evidence |
|---|---|---|---|
| `kind` | ● | code | system · service · software · hardware · policy · process · … (C.6). |
| `members` | ○ | [{component-ref ●, context ○}] | Composition. |
| `capabilities` | ○ | [{id ●, description ○, parameter-bindings ○}] | What the vendor claims — comp-def's replacement (the PR-#8 duplication axis, deleted). |
| `authorizations` | ○ | [{id ●, authority-ref ●, scope-label ○, includes ○[]}] | **Identified** trust contexts; `includes` scopes; absence is silence, and silence is silence (Ch. 9). |

## A.6 Implementation

| Field | | Type | Meaning & evidence |
|---|---|---|---|
| `component-ref` / `requirement-ref` | ● | URI | The edge's endpoints. |
| `statement-refs` | ○ | [statement-id] | Clause-level granularity — shared responsibility per clause (KONF.14.1 s1 provider / s2 customer). |
| `responsibility` | ● | code (C.4) | provider · customer · shared · inherited. |
| `satisfied-by` | ● | [{capability-ref} \| {inherited-from}] | How. `inherited-from` = {component-ref ●, **basis-ref ●**} — the edge-local boundary rule (D5): every inheritance names the authorization it leans on; chains verify link by link. |
| `parameter-bindings` | ○ | {param: value} | Bound within declared bounds. |
| `status` | ● | code | planned · partial · implemented · not-applicable. |
| `evidence-refs` | ○ | [ref] | Pointers, not blobs. |

## A.7 Assessment · A.8 Finding

**Assessment:** `subject-refs` ● [URI] · `method` ● {facet payload —
assessment-criteria absorbs ISM/BSI documentation duties ×966 and the
CR26 artifacts/key-tests/examples shape} · `performer-ref` ● ·
`time` ● · `result` ● code · `evidence-refs` ○.

**Finding:** `assessment-ref` ● · `requirement-ref` ● ·
`statement-ref` ○ · `state` ● code (C.3) · `risk-refs` ○ [URI] — the
ex-post record points at the ex-ante Risk(s) it materialised against;
landmark (assessor bundle → organisation register, 2.0.0), but typed: a
ref that resolves in-bundle must name a Risk (RISK-12) ·
`actions` ○ [{description ●, due ○ {date | elapsed-duration |
calendar-period}, status ●}] — computable deadlines
(fail-closed without the named calendar) ·
`deviations` ○ [Deviation] — the ex-post channel; the four historical
FedRAMP deviation props are its `type` values.

## A.9 Attestation

| Field | | Type | Meaning |
|---|---|---|---|
| `subject-semantic-digests` | ● | [digest] | *Meaning* bound (JCS minus annotations). |
| `content-manifest-digest` | ● | digest | *Package state* bound — enables bi-modal verification (Full vs Semantic Match). |
| `rendering` | ● | {artifact-digest ●, media-type ●, template-ref{id,version,digest} ●, renderer ●} | *Paper* bound; templates are pinned TCB citizens; chrome-only annotation use is the renderer's law. |
| `signer` ● · `timestamp` ● · `envelope-ref` ● | | | DSSE profile (stdlib); attestations live **beside** the manifest — nothing signed contains its own signature (D3). |

## A.9b Risk *(kernel 2.0.0 — CP-RISK-1)*

The ex-ante record: why a requirement is in scope. Four authorities encode
it with the same fields (ISO/IEC 27001 6.1.2–6.1.3 / 27005, BSI 200-3,
SP 800-30, OSCAL AR/POA&M `risk`); the *scales* differ and stay in facets.
Common fields (A.0) plus:

| Field | | Type | Meaning & evidence |
|---|---|---|---|
| `scenario` | ● | text | The risk statement — event and consequence (ISO 27005 event-based; BSI 200-3 Gefährdung am Zielobjekt). Multilingual like every normative text. |
| `owner-ref` | ● | URI | The risk owner (ISO 6.1.2 c 2). Landmark ref — a party, not a bundle object. |
| `state` | ● | code (C.3c) | identified · assessed · treated · retired. |
| `threat-refs` | ○ | [URI] | Threat catalog entries (G 0.x, ATT&CK techniques, 800-30 threat events). Landmark. |
| `component-refs` | ○ | [URI] | The assets at risk — Components of this bundle. Closure-required (RISK-7) and typed: each names a Component (RISK-12). |
| `tailoring-refs` | ○ | [URI] | The Statement(s) of Applicability this risk's treatment belongs to — Tailorings of this bundle. Closure-required (RISK-7), typed (RISK-12). Present: the Risk justifies, and is held to RISK-11, only there. Absent: it applies to every Tailoring of the bundle (noted where there is more than one — RISK-14). |
| `rating` | ○ | {level ●, scale-ref ●} | Inherent/current level on a named scale. **Required** once `state` ∈ assessed · treated (RISK-2). |
| `residual-rating` | ○ | {level ●, scale-ref ●} | The level after treatment. Presupposes `rating`, on the **same** `scale-ref` (RISK-13). |
| `treatment` | ○ | code (C.10) | modify · retain · avoid · share. **Required** once treated (RISK-3). |
| `treatments` | ○ | [{requirement-ref ●, statement-ids ○}] | **The ISO 6.1.3 b edge**: the controls determined for this risk, to the clause. requirement-ref closure-required (RISK-7) and typed — it names a Requirement, never a Set (RISK-12); statement-ids must address the target (RISK-8). **Required** for `modify` (RISK-4). |
| `shared-with-ref` | ○ | URI | Who carries the shared risk. **Required** for `share` (RISK-5). |
| `acceptance` | ○ | {approver-ref ●, date ●, rationale ●} | The owner's acceptance of the residual (ISO 6.1.3 f). `date` is an ISO 8601 calendar date (`YYYY-MM-DD`), schema-checked. **Required** for `retain` (RISK-6) and once treated (RISK-3). |
| `review-due` | ○ | date \| datetime \| elapsed-duration \| calendar-period | ISO 8.2 "at planned intervals". A point in time is `{type: date \| datetime, value}` — `date` is `YYYY-MM-DD`, `datetime` is RFC 3339 with an explicit offset, both schema-checked; durations as in `Finding.actions[].due` with `num` a positive integer, fail-closed without the named calendar. `datetime` is measured, not designed: OSCAL's `deadline` is date-time-with-timezone and both corpus deadlines are (IFA ×2). |

**Shape-disjointness:** `scenario` + `owner-ref` occur in no other type.
**Closure:** `treatments[].requirement-ref`, `component-refs` and
`tailoring-refs` in-bundle (RISK-7) and typed (RISK-12); `owner-ref`, `threat-refs`,
`shared-with-ref`, `approver-ref`, `scale-ref` landmark. **Liveness:** a
Risk whose `state` is `retired` or whose `lifecycle` is `withdrawn`
justifies nothing (B.1.9). **Justification:** a live Risk justifies a
requirement only once it is published (not `draft`), `assessed` or
`treated`, and carries a `treatment` option — until then it is listed as
`pending` (B.1.9). **Evidence:** example bundle (1 Risk), 65
vectors, and the IFA lifecycle corpus — 2 Risks converted from POA&M
risks. That first corpus also measured what OSCAL cannot give this shape
(A.12): no owner field, no single level, no dated acceptance.

## A.10 Sub-object: Deviation

`type` ● ∈ false-positive · operational-requirement · risk-adjustment ·
vendor-dependency · derogation · `state` ● (C.3b: investigating →
pending → approved | withdrawn) · `rationale` ● · `approver-ref` ● ·
`opened` ● · `refs` ○. One channel, three moments (Tailoring ·
Implementation · Finding); Excel dies of enumerated states.

## A.11 Bundle artifacts

**content-manifest.json:** `manifest-version` ● · `objects[]`
{id, version, **package-digest**, **semantic-digest**, path} ● ·
`facet-schemas[]` {id, **exact-version**, digest, path} ● (exact pins,
never ranges — D3) · `renderings[]` ○ · provenance ○. The manifest is
the sealed resolver: every reference lands here or validation fails
with a rationale.

---

## A.12 What the three converters actually exercised

Honesty ledger for this appendix: **exercised at scale** — statements
& flattening, modality (full lattice minus may-only: DARF NUR ×0
measured), obligated-parties, choice/string/calendar-period/
elapsed-duration parameters, aliases, sequence, nested Sets &
sets-of-sets, relations, facets & annotations, both digests,
set-modality/set-parameter ops, Mapping at scale (×373), authorizations
+ basis-ref (example bundle). **Declared, not yet corpus-exercised** —
predicate selects, excludes, set-field/replace-prose/relation/facet
ops, uri/date/integer/decimal parameters, canonical-alias/replaces
events, Assessment/Finding/Attestation at scale (example-bundle only).
The gap list is Appendix E's and gate items 2–3's work order.

**Risk (2.0.0), first corpus measurement — IFA re-run 2026-11-10.**
*Exercised:* `scenario`, `owner-ref`, `state`, `component-refs`,
`treatment` + `treatments` (×1), `review-due` (datetime ×2),
`Finding.risk-refs` (×2), a `risk-adjustment` Deviation naming its Risk
(×1). *Declared, not corpus-exercised:* `rating`, `residual-rating`,
`acceptance`, `shared-with-ref`, `threat-refs`, `tailoring-refs`, and the states `assessed`,
`treated`, `retired`. That list is not an accident of a small corpus: an
OSCAL risk carries likelihood and impact but **no level** (so RISK-2 holds
both risks at `identified`), **no owner** (derived from the imported SSP's
`owner` role, declared in the coverage report) and **no acceptance date**
(so the one `accept` response cannot become `retain` under RISK-6). The
kernel shape and the fourth authority disagree on three required fields;
the disagreement was put to the author and decided on 2026-11-10: **the
rules stay** (specification D23). `assessed` always means "has a level",
`retain` always means "has a dated, attributed acceptance"; an import that
cannot say so stays `identified`, with its source status in a facet.
