# The JASCON Handbook
## Part Three — Implementation and Assurance
# Chapter 10 — Assessment, Findings, Deviations

**Audience:** [A][C] — assessment programs and assessors who define
what "checked" means, and the assessed (plus their agencies) who live
with the results. §10.6 walks one finding through both seats.
**Companions:** Specification v0.5 — Appendix A (Assessment, Finding,
Deviation shapes), D8, D12 (`assessment-criteria@1`), D9
(calendar-periods).

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
  "method": { "https://ns.oscal.org/stdlib/facet/assessment-criteria@1":
              { "criteria-ref": "https://ns.fedramp.gov/cr26/…" } },
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
  "risk": { "…risk facet…": {} },
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
cleanly. **`risk`** is a facet on purpose: CVSS, national risk
matrices, house scales — the kernel stays agnostic and lets your risk
model arrive under contract, exactly like assessment methods. And
**`actions[]`** is the old POA&M reduced to its load-bearing atoms —
description, due, status. The *historical* record shows how overdue
that reduction was: the Rev4-era registry carried a whole cluster of
POA&M plumbing props — planned-completion-date, priority, poam-id —
a decade of milestone tracking encoded as annotations for want of
three fields.

## 10.4 Deadlines that compute

Chapter 4 made the promise; findings are where it gets kept. An
action's `due` is either a plain date, an **elapsed-duration** (the
American six-hour incident clock — pure physics, computable anywhere),
or a **calendar-period** like the twenty business days above — which is
*representable* everywhere but **computable only with its calendar**.
No `calendar-ref`, no arithmetic: a conformant tool refuses, with a
printed reason, rather than guessing at holidays.

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

## 10.6 Worked: one finding, end to end

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

## 10.7 Where this leaves you

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
