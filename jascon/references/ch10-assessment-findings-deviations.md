# The JASCON Handbook
## Part Three — Implementation and Assurance
# Chapter 10 — Assessment, Findings, Deviations

**Audience:** [A][C] — assessment programs and assessors who define
what "checked" means, and the assessed (plus their agencies) who live
with the results. §10.8 walks one finding through both seats; §10.7 is
for whoever lets a machine do the checking.
**Companions:** Specification v0.5 — Appendix A (Assessment, Finding,
Deviation shapes), D8, D12 (`assessment-criteria@1`), D9
(calendar-periods); for §10.7 the 2.0.0 candidate — D24, Appendix A.9c
and B.1.10.

---

## 10.0 The task

Chapter 9 left you a chain of implementation edges that *claims* to
satisfy requirements. Now somebody has to test the claims — and the
task splits three ways.

First, define the **method** machine-readably: what counts as passing,
which artifacts must exist, which tests must run — the question the
American KSI program answered on a green field, in exactly the shape
this chapter teaches. Second, record the aftermath as **Findings**
whose corrective actions carry deadlines a machine can actually
compute. Third — and this is where most programs are weakest — give
imperfection a legal, typed channel: the **Deviation**, the one
structure this book has now met twice and finally gets to explain in
full.

The consumer's parallel question runs throughout: what does a
*trustworthy* assessment package look like, and which fields do you
read first?

## 10.1 Assessment: who checked what, how

The object is deliberately spare:

```json
{ "id": "https://assessor.example/assessment/2026-q3-acme",
  "subject-refs": ["https://cso.example/component/acme-saas"],
  "method": { "https://ns.jascon.net/stdlib/facet/assessment-criteria@1":
    { "summary": { "en": "Document review of KONF.14.1 evidence duties; key test: rotation artifacts present." } } },
  "performer-ref": "https://assessor.example/party/lead-assessor",
  "time": "2026-07-15",
  "result": "satisfied",
  "evidence-refs": ["…"] }
```

The design's one big opinion hides in `method`: the kernel refuses to
pick a methodology. Interviews, document review, penetration tests,
continuous automated checks — the field genuinely varies, and a core
that blessed one style would be re-committing the original sin of
Chapter 1 (one framework's conventions enforced on everyone). So the
method is **facet-typed**: whatever methodology you use, it arrives
under a registered contract that declares itself assessment-modifying —
which means, via Chapter 7's fail-closed rule, that no tool can
half-understand your method and *guess* at your verdicts. Subjects
point at components and implementation edges (Chapter 9's chain is
literally what gets tested, basis-refs and all); the performer is a
party reference, with accreditation context living where party context
lives; `result` draws from the small stdlib code system.

## 10.2 Criteria before verdicts: the KSI shape

A verdict without published criteria is an opinion with a stamp. The
stdlib's `assessment-criteria@1` facet carries the *should-side* of
assessment — and its field list was not invented, it was measured. The
American corpus attaches to its rules exactly this bundle: required
artifacts (~60 `artifacts` entries naming the evidence a provider owes),
worked examples with **key tests**, and reference mappings back to
800-53 — and its 46 Key Security Indicators are precisely
statement + tests + artifacts + control-mappings, the automated-
assessment future built green-field. The facet absorbs that shape
whole: the KSI era arrives as a registered facet, not a fork.

The authoring craft, for the [A] seat: publish criteria **on the
requirements**, where the American corpus puts them — the authority
states, next to each rule, what evidence discharges it — and let each
Assessment's `method` cite those criteria rather than restate them.
One source of truth for "what passing means," per requirement, versioned
with the requirement.

> **Don't** bury required evidence in prose. The measured neighbor: one
> national corpus carried its documentation duties as 959 prop
> instances — "keep a configuration history," "log the review" —
> machine-invisible, unqueryable, and un-checkable by any tool. Criteria
> are data; the facet is their home; an assessor's checklist should be
> a *query*, not a close reading.

## 10.3 Findings: the aftermath, typed

```json
{ "id": "https://assessor.example/finding/2026-q3-acme-017",
  "assessment-ref": "https://assessor.example/assessment/2026-q3-acme",
  "requirement-ref": "https://ns.bsi.bund.de/gspp/req/KONF.14.1",
  "statement-ref": "s2",
  "state": "open",
  "risk-refs": [ "https://cso.example/risk/R-2026-007" ],
  "actions": [
    { "description": "Provide key-rotation runbook and rotation evidence",
      "due": { "type": "calendar-period", "num": 20, "unit": "bizdays",
               "calendar-ref": "https://ns.fedramp.gov/cr26/calendar/us-federal" },
      "status": "open" } ] }
```

Three fields carry the chapter's weight. **`statement-ref`** is
clause-precision paying off a third time (after tailoring and shared
responsibility): the finding is against *statement s2* — the customer's
key-rotation clause — not smeared across a requirement whose s1 passed
cleanly. **`risk-refs`** closes the loop the old POA&M never could: the
finding points at the Risk it materialised against (§10.6), and that Risk
points at the clause that was supposed to treat it — the same `s2`. Risk
*scoring* stays a facet: CVSS, national matrices, house scales arrive
under contract, exactly like assessment methods. And
**`actions[]`** is the old POA&M reduced to its load-bearing atoms —
description, due, status. The *historical* record shows how overdue
that reduction was: the Rev4-era registry carried a whole cluster of
POA&M plumbing props — planned-completion-date, priority, poam-id —
a decade of milestone tracking encoded as annotations for want of
three fields.

## 10.4 Deadlines that compute

Chapter 4 made the promise; findings are where it gets kept. An
action's `due` is either a point in time (`date` or `datetime`, each
written `{type, value}`), an **elapsed-duration** (the
American six-hour incident clock — pure physics, computable anywhere),
or a **calendar-period** like the twenty business days above — which is
*representable* everywhere but **computable only with its calendar**.
No `calendar-ref`, no arithmetic: a conformant tool refuses, with a
printed reason, rather than guessing at holidays. Since 2.0.0 the schema
accepts nothing else in `due` (DATE-2). 1.0.0 let any string through,
and "end of Q3" is a deadline no machine can read.

For the consumer seat, this is a one-line acceptance test worth
running on any toolchain you are sold: two conformant tools, one
calendar-period, must produce **one date — or one explained refusal.**
Never two dates. The old world's silent divergence (your tracker says
Thursday, the agency's says Monday) is the failure this small honesty
was built to kill; the calendar itself is an Authority-tier deliverable
(§3.7), published once, cited everywhere.

## 10.5 The Deviation: one channel, three moments

You have met this object twice — as tailoring's audited weakening
record (Chapter 6) and attached to implementation edges (Chapter 9).
Here is the full picture: **one structure, three moments in a
requirement's life.**

*Ex ante* — a Tailoring weakens a rule for a class or a context: the
Deviation records the derogation before anyone implements. *In
operation* — an Implementation cannot or should not meet a clause as
written (the vendor dependency, the compensating control): the
Deviation rides the edge. *Ex post* — an assessment surfaces a gap, and
its disposition needs adjudicating: the Deviation attaches to the
Finding.

The type code system reads like a field guide because it *is* one —
`derogation`, `risk-adjustment`, `false-positive`,
`operational-requirement`, `vendor-dependency` — and its origin story
is the strongest evidence in this Part: the historical Rev4 registry
contained **four separate extensions** — false-positive, operational-
requirement, risk-adjustment, vendor-dependency — each hand-carrying
the *identical* state machine. One missing concept, encoded four times
by one program: the census's cleanest proof that a concept belongs in
the kernel.

The state machine is small and means exactly what it says:

```
investigating ─→ pending ─→ approved
                        └──→ withdrawn
```

`investigating`: claimed, being examined. `pending`: adjudication
requested, evidence attached. `approved`: the weakness is now *legal* —
carried by a named `approver-ref`, a standing `rationale`, and `refs`
to the supporting analysis. `withdrawn`: the claim died honestly.
Nothing here forbids imperfection; everything here makes imperfection
**citable** — which is what regulators actually want, and what the
four-times-reinvented state machine proves programs will build with or
without you.

For the assessor's seat, the review of a Deviation is four questions
in order: does the *type* fit the facts (a scanner artifact is a
false-positive, not a risk-adjustment); does the *rationale* carry its
weight without the meeting that produced it; is the *approver*
actually competent to approve this class of weakness; and do the
*refs* lead to evidence a stranger could re-examine.

> **Don't** run deviations through email and meeting minutes. The
> measured precedent: four parallel prop-based workflows in the
> historical registry, and `corrective_actions` threading through the
> current American corpus — programs *will* build this channel; the
> only question is whether it is typed, queryable, and attached where
> the weakness lives, or reconstructed from inboxes at audit time.

## 10.6 Risk: the record that comes first

Chapters 6, 9 and 10 so far run in the direction an auditor reads: requirement → implementation → assessment → finding → deviation. An ISMS is written in the other direction, and ISO/IEC 27001 is explicit about the order: identify risks and their owners (6.1.2 c), analyse and evaluate them (6.1.2 d–e), choose a treatment option (6.1.3 a), determine *all* controls necessary (6.1.3 b), compare with Annex A, write the Statement of Applicability with a justification for every inclusion and exclusion (6.1.3 d), obtain the owners' acceptance of the residual (6.1.3 f). BSI-Standard 200-3 is the same procedure with German names — Gefährdungsübersicht, Risikoeinstufung, Risikobehandlung, Konsolidierung — and the same four treatment options. OSCAL 1.x had a `risk` only where an assessor found one; usnistgov/OSCAL #2292 records why that cannot represent an ISO 27001 catalog. The Risk type (App. A.9b) is the missing first record.

```json
{ "id": "https://cso.example/risk/R-2026-007",
  "scenario": { "en": "A KMS key compromised through an export path stays valid for years because keys are never rotated; every tenant record encrypted under it is exposed retroactively." },
  "owner-ref": "https://cso.example/party/ciso",
  "state": "treated",
  "threat-refs": [ "https://ns.bsi.bund.de/gspp/threat/G-0.19" ],
  "component-refs": [ "https://cso.example/component/acme-saas" ],
  "rating": { "level": "hoch", "scale-ref": "https://cso.example/scale/bsi-200-3-matrix",
              "likelihood": { "level": "mittel", "scale-ref": "https://cso.example/scale/bsi-200-3-eintrittshaeufigkeit" },
              "impact": { "level": "existenzbedrohend", "scale-ref": "https://cso.example/scale/bsi-200-3-schadenshoehe" } },
  "residual-rating": { "level": "gering", "scale-ref": "https://cso.example/scale/bsi-200-3-matrix",
              "likelihood": { "level": "selten", "scale-ref": "https://cso.example/scale/bsi-200-3-eintrittshaeufigkeit" },
              "impact": { "level": "begrenzt", "scale-ref": "https://cso.example/scale/bsi-200-3-schadenshoehe" } },
  "treatment": "modify",
  "treatments": [ { "requirement-ref": "https://ns.bsi.bund.de/gspp/req/KONF.14.1", "statement-ids": ["s2"] } ],
  "acceptance": { "approver-ref": "https://cso.example/party/ciso", "date": "2026-11-05",
                  "rationale": { "en": "Monthly rotation brings the residual to 'gering', within appetite." } },
  "review-due": { "type": "calendar-period", "num": 12, "unit": "months", "calendar-ref": "https://cso.example/calendar/isms" } }
```

Four fields carry the chapter's weight. **`treatments[].statement-ids`** is clause precision paying off a fourth time: the risk is treated by *s2*, the customer's rotation clause, and the Implementation (Ch. 9) says s1 is the provider's — so the SoA, the responsibility matrix and the risk register agree to the clause without anyone reconciling three documents. **`rating.scale-ref`** keeps Appendix F Q14's promise: the kernel carries a level and the identity of the scale it is on, and refuses to compare across scales. `likelihood` and `impact` inside the rating are the two inputs every one of the standards names, each again a level on its own named scale; the residual rating carries its own pair, so the register shows what the treatment changed (here: likelihood from `mittel` to `selten`, impact from `existenzbedrohend` to `begrenzt`). How `mittel` and `existenzbedrohend` become `hoch` is the organisation's matrix. It is part of the pinned definition of the level scale, and the validator holds the stated level to it: a rating that contradicts its own table fails, unless it carries an `override-rationale` that says why this one risk departs from it. The scales themselves are the organisation's: the bundle pins a small definition file per scale that lists its levels from lowest to highest, as many as the organisation uses and in its own words, and the validator then refuses a level the scale does not define. **`acceptance`** is the owner's signature on the residual — required the moment the risk is `treated` or `retain`ed, because silent retention is the oldest ISMS defect and a required field is the cheapest cure. **`treatment`** is the one code system two authorities publish verbatim: ISO 31000's avoid · modify · share · retain and 200-3's Vermeidung · Reduktion · Transfer · Akzeptanz are the same four words.

What this makes computable is the sentence every ISO 27001 auditor asks and every ISMS answers with a spreadsheet: *which selected controls rest on no risk?* The `risk-coverage` primitive (B.1.9) resolves each Tailoring's selection and lists, per requirement, the Risks that justify it. A Risk justifies once a treatment decision rests on an assessed risk — `assessed` or `treated`, an option chosen, not a draft — so a three-field stub justifies nothing and is listed as *pending*; a `retired` Risk no longer justifies anything, or a control justified once would stay justified for ever. Where a bundle holds more than one Statement of Applicability, `tailoring-refs` say which one a Risk belongs to. Run on this book's example bundle it reports: three selected, one justified (KONF.14.1 by R-2026-007), two uncovered (ISM-1234, IEC-CSO-IIR). Whether *uncovered* is an error is the program's policy — ISO says yes for every SoA row, BSI says the baseline justifies itself — so the primitive reports and the policy switch (`--require-risk-basis`) decides.

**Controls a law or a contract keeps.** Under the strict switch, a control that is in the Statement of Applicability because a law, a regulator or a customer contract demands it shows as uncovered, and no field on the Tailoring changes that: the specification rejects a selection-basis field until a corpus shows one authored (D23). None is needed. Failing a legal, regulatory or contractual duty is a risk every organisation carries, the one ISO/IEC 27001 Annex A 5.31 exists for, and it is recorded like any other:

```json
{ "id": "https://cso.example/risk/R-2026-011", "version": "1", "lifecycle": "active",
  "scenario": { "en": "An incident is identified, but the initial report reaches the agency customers after the deadline their contracts and the authorization set. Missing it breaches that duty and puts the contracts and the authorization at risk." },
  "owner-ref": "https://cso.example/party/head-of-compliance",
  "state": "assessed",
  "tailoring-refs": [ "https://ns.bsi.bund.de/gspp/tailoring/erhoeht" ],
  "relations": [ { "type": "reference", "ref": "https://cso.example/contract/agency-msa-2026#incident-reporting" } ],
  "rating": { "level": "hoch", "scale-ref": "https://cso.example/scale/bsi-200-3-matrix",
              "likelihood": { "level": "mittel", "scale-ref": "https://cso.example/scale/bsi-200-3-eintrittshaeufigkeit" },
              "impact": { "level": "existenzbedrohend", "scale-ref": "https://cso.example/scale/bsi-200-3-schadenshoehe" } },
  "treatment": "modify",
  "treatments": [ { "requirement-ref": "https://ns.fedramp.gov/cr26/req/IEC-CSO-IIR" } ] }
```

Added to this book's example bundle, it moves the `erhoeht` report to two justified of three. ISM-1234 stays uncovered, and should: no contract clause here asks for limits on privileged access, and a compliance risk that named the control anyway would justify it with words. Three rules keep the pattern honest:

- **One Risk per obligation.** A single "we might breach some law" Risk whose treatments name every uncovered row satisfies the switch and says nothing; the validator cannot tell, a reviewer can. Name the article or the clause in `scenario` and point `relations` at its source: at the law's Requirement if the law is converted into the bundle, at the contract otherwise.
- **Assessed, with an option.** Like any Risk it justifies only once it is `assessed` or `treated` and carries a `treatment`. Its likelihood is that of the breach being noticed or enforced; its impact is the fine, the penalty clause, the lost customer: real levels on the organisation's scales, not placeholders.
- **The owner of the duty.** `owner-ref` names whoever answers for the obligation, usually legal or contract management rather than the security team, and it is that owner who accepts the residual.

> **Don't** encode risk acceptance as a Deviation, and don't encode a weakened requirement as a Risk. They are two acts by two roles: the owner accepts a residual (`Risk.acceptance`); an implementer weakens a clause because of it (`Deviation` of type `risk-adjustment`, which SHOULD name the Risk in `refs` — RISK-9). The corpse this honours is OSCAL's `deviation-approved` risk status, which fused the two into one state and lost the owner.

## 10.7 Checks: when the assessor is a machine *(2.0.0)*

§10.2 said a verdict without published criteria is an opinion with a
stamp. A machine verdict without published criteria is worse: it is an
exit code. The measured case is the CIS Ubuntu 24.04 Benchmark, which
marks 291 of its 312 rules as automated and carries the pass condition
of every one as a sentence in an `audit` string.

A **Check** publishes both halves. `observes` is the contract a
collector must honour: fact names and types, and nothing about how the
facts are obtained. `criteria` is the pass condition, written in twelve
comparators that every conformant tool evaluates identically, joined by
one AND. Between the two sits the collector, a shell script, an Ansible
task or an API call. It is carried on the Check in the facet
`collector@1`, so that the Check's digest covers the exact code, and it
decides nothing.

```json
{ "id": "https://cso.example/check/LNX-SSH-1-maxauthtries",
  "requirement-ref": "https://cso.example/req/LNX-SSH-1",
  "statement-ids": ["s1"],
  "platform": "https://cso.example/platform/linux-host",
  "observes": [ { "name": "sshd.maxauthtries", "type": "integer" } ],
  "criteria": [ { "fact": "sshd.maxauthtries", "op": "at-most",
                  "expected": { "param": "max-auth-tries" } } ],
  "confidence": "reviewed",
  "provenance": { "author-ref": "https://cso.example/party/secops",
                  "date": "2026-11-11" } }
```

The payoff is in the run record. An Assessment carries one row per
check in `check-results`, and the row carries the observation itself,
`{"sshd.maxauthtries": 4}`, beside the outcome. A second party
recomputes the verdict from that row without running anything, and the
validator does so for every row (CHECK-9). The parameter value the run
used is held to the Tailoring the Assessment names (CHECK-12). Tighten
`max-auth-tries` from 6 to 4 in the Tailoring, and yesterday's
observation of 5 turns from satisfied to not-satisfied without one line
of code changing.

Four outcomes exist: `satisfied`, `not-satisfied`, `inconclusive` and
`not-applicable`. A missing fact, an unbound parameter or a collector
that printed nothing gives `inconclusive`; a default is never
substituted. One definite failure decides over an unknown elsewhere,
never the other way round. An Assessment's `result` is the aggregate of
its rows, so an assessment that mixes machine and human judgement is
two assessments.

A check over many resources (`each`: accounts, files, buckets) holds
only if every applicable resource passes. Every resource is evaluated
all the same, none is skipped after the first failure, and a tool
reports the count and the share with the verdict: "12 of 200 applicable
bucket resources not satisfied (6 %)". The share tells an operator how
far from done a fleet is. It never softens the verdict.

What does not fit stays manual, and is counted. Of 510 rules in the CIS
profiles for Ubuntu 24.04 of ComplianceAsCode, 481 fit this form; 12
need arithmetic, 9 a comparison between two facts, 6 an OR across
facts, 2 a version ordering. The set has no OR, no NOT and no nesting on
purpose (Appendix F, Q24 to Q26).

Evidence lies beside the bundle, every file named by the SHA-256 of its
bytes. The row points to an evidence record, the record carries the
digest of the same observation and of each raw output, and an
Attestation over the Assessment covers the row. Every link verifies
offline. Row and record are two statements about one run and must
agree: a record that binds an observation the row does not carry fails,
and so does a row whose record binds none. Otherwise a failing
observation could be dropped and the run reported as inconclusive. A raw output deleted under a retention rule is reported as
withheld; the record stays verifiable.

> **Don't** let the code decide. A script that exits 0 or 1 hides its
> threshold, ignores the tailoring and leaves nothing to re-examine.
> The measured neighbour: 291 automated CIS rules whose pass condition
> reached this format as a sentence.

Two limits belong here. Nothing in this repository runs a collector:
the worked example executed its bash collector against a stub that
prints a fixed configuration, and its evidence records say so. And the
fit was counted on Linux hosts and Kubernetes; no cloud API was counted
before the shape was closed.

## 10.8 Worked: one finding, end to end

The SaaS from Chapter 9, under a criteria-driven assessment. The
transport-encryption requirement's clause s1 (provider encrypts)
passes — capability cited, artifact present. Clause s2 (customer
rotates keys) fails its key test: no rotation evidence. One Finding is
minted — `statement-ref: s2`, action "provide rotation runbook," due
twenty business days on the published federal calendar, state `open`.

The customer answers with receipts: rotation runs monthly; the
scanner misread the KMS export. The disposition is a Deviation on the
Finding — `type: false-positive`, `state: investigating`, refs to the
KMS logs — moving to `approved` under the lead assessor's
`approver-ref` once the logs check out. The Finding closes; the
Deviation *remains*, a permanent, typed, one-object answer to the
auditor who asks next year why 2026-Q3's finding 017 ended without a
fix.

Three objects, one story, every step citable by id — and not one email
thread subpoenaed.

## 10.9 Where this leaves you

The chain is built (9), tested, and honest about its gaps (10). What
nothing so far explains is why anyone *outside* your organization
should believe a byte of it: what stops a package from being altered
in transit, what an authorizing official's signature actually binds,
how verification works on a network with no network, and the exact
difference between "the bytes are intact" and "the meaning is intact"
— which turn out to be two different digests with two different jobs.
That is Chapter 11: integrity, attestation, and air-gaps — the chapter
where the signature on the last page finally connects, cryptographically,
to every object this book has built since page one.
