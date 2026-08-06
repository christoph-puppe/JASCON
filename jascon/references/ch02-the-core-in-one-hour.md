# The JASCON Handbook
## Part One — Orientation
# Chapter 2 — The Core in One Hour

**Audience:** everyone. This is the one chapter every reader completes
before branching into their path (§2.6).
**Companions:** Specification v0.5 Part II (decisions D1–D21) and
Appendix A (normative shapes). Nothing in this chapter exceeds what those
define.

---

## 2.0 The task

You have one hour. At the end of it you should be able to open any
JASCON artifact and know what you are looking at — and, for your
own material, know where each piece of it belongs: kernel field, set,
tailoring, facet, annotation, or (most often, as Chapter 1's census
showed) nowhere, because the mechanism it was imitating now exists.

We will not tour nine types in the abstract. We will start with the
smallest real object in the corpus — an Australian control — and keep
asking one question: *what does reality add next?* Each honest answer
introduces exactly one type. By the end, all nine have appeared because
something measured demanded them, which is also how they got into the
specification in the first place.

## 2.1 The smallest possible artifact

Here is an ISM control, complete. Not an excerpt — complete:

```json
{ "id": "https://ns.cyber.gov.au/ism/req/ISM-1234",
  "version": "2026.06.18",
  "label": "ISM-1234",
  "lifecycle": "active",
  "statements": [
    { "id": "s1",
      "modality": "must",
      "obligated-parties": ["https://ns.cyber.gov.au/ism/party/organisation"],
      "prose": { "en": "…" } } ] }
```

Read it line by line, because every line is a decision with a body count
behind it.

The **`id`** is a URI under the authority's own domain. It is compared as
an opaque string and **never resolved** during validation — sealed,
air-gapped validation is a conformance requirement, not a mode. Global
identity is what makes two catalogs impossible to collide: the German
corpus contains two catalogs whose controls share ID strings, and under
the old instance-scoped identity there was literally no safe way to
combine them. Here the question cannot arise.

**`version`** plus (in the shipping bundle) two digests per object replace
an entire category of annotation: the Australians hand-maintain `revision`
and `updated` props — 2,202 instances, with dates encoded as strings like
"Jun-26" — and the Americans put an `updated[]` array on every object.
Change history is an identity concern, so it lives at the identity layer,
once.

**`label`** exists because all three authorities, independently, maintain
human display identifiers beside their canonical ones — and two of them
also maintain *third* schemes, which is what the (optional) `aliases[]`
field absorbs: 1,219 German `alt-identifier` props, 188 American glossary
aliases. Without a sanctioned channel, those props return on day one.

**`statements[]`** is a list even when it holds one entry, because
clauses are real: the German catalog contains **347 nested
pseudo-controls** that exist *only* because its authors needed
independently addressable clauses and the old model gave them none. Each
statement carries its own **`modality`** — the census's strongest
three-way convergence (German `modal_verb` ×1,006; the American `force`
field, distribution MUST 189 / SHOULD 84 / MAY 39 / MUST NOT 11 /
SHOULD NOT 5; Australian style-guide prose) — and its own
**`obligated-parties`**, an array because the American corpus binds
multiple parties per rule and shared responsibility is how cloud
compliance actually works.

> **Don't** encode ordering, membership, or history as annotations.
> Measured cost: `sort-id` ×1,150, `applicability` ×5,301, revision props
> ×2,202 — every one of them a kernel mechanism, hand-imitated.

That object is finished. No props. No facets. No document tree. The
sharpest single finding of the census is that the *entire* Australian
extension surface — a disciplined national framework — needs nothing this
object doesn't have. Which raises the obvious question: what do the other
two authorities force us to add?

## 2.2 Reality adds structure: the content side

**Parameters.** The German KONF.14.1 says encryption may follow "TLS 1.3
*oder* TLS 1.2 mit PFS" — an either/or that the old catalog fused into one
prose string no machine could see. A statement therefore carries typed
parameters:

```json
"parameters": [ { "name": "transport-crypto", "type": "choice",
    "cardinality": "one",
    "choices": [ {"value": "tls13"}, {"value": "tls12-pfs"} ] } ],
"prose": { "de": "… nach {param:transport-crypto} verschlüsseln." }
```

The `{param:…}` token is *bound*: a rule called `prose-params-resolve`
verifies every token against a declared parameter. That single binding
makes the census's ugliest measurement — 216 pseudo-placeholders drifting
silently inside schema-valid documents — **unwritable**. The type algebra
is deliberately small (strings, integers, canonical decimals, booleans,
dates, URIs, codes; choice/list/range containers; and durations split into
elapsed time versus calendar periods, because the American corpus counts
deadlines in business days and a business day is meaningless without a
calendar).

**RequirementSet — membership as a first-class thing.** Chapter 1's
largest pattern: Australia inlines a 5,301-entry classification matrix
into its catalog while *also* publishing the same information as eight
profiles. In the core, membership is only ever one thing:

```json
{ "id": "https://ns.cyber.gov.au/ism/set/secret-baseline",
  "members": [ {"ref": ".../req/ISM-1234", "sequence": 10}, … ] }
```

Sets nest (a set's member may be a set), which is the whole taxonomy
story — CSF's Functions→Categories→Subcategories, CIS's
Controls→Safeguards, ISM's classifications — one mechanism, and
`sequence` is a defined field, so display order stops living in `sort-id`
props.

**Tailoring — change without copies.** The American rules vary by
certification class: the same requirement, four deadline values. The old
world's answer was inline variant blocks (four near-identical statement
strings per rule) or a profile-resolution algebra so intricate it had its
own specification and, at merge time, no safe answer. Here a Tailoring is
a selection plus a closed list of operations addressed **by identity,
never by position**:

```json
{ "op": "set-parameter",
  "requirement-ref": "https://ns.fedramp.gov/cr26/req/IEC-CSO-IIR",
  "statement-id": "s1",
  "parameter": "iir-deadline",
  "value": {"type": "duration", "num": 6, "unit": "hours"} }
```

An upstream erratum that inserts a parameter cannot silently repoint this
— the positional fragility that two independent hostile reviews condemned
in general JSON Patch is unrepresentable. Weakening is governed per
operation: strengthening modality is free, weakening it (or breaking a
parameter's declared bounds) requires an attached, audited **Deviation**
— while *excluding* requirements is plain selection, deliberately
deviation-free, because baselines are made of exclusions and drowning
every baseline in pseudo-deviations would kill the mechanism that just
absorbed 5,900+ membership props.

**Mapping — the ninth type, and the newest.** Crosswalks are entire
business models (SCF maps its catalog to 200+ frameworks; CIS and CSA
ship mappings as core products; the American corpus itself carries 263
KSI→800-53 links). NIST's answer, in March 2026, was an eighth full
document model. The core's answer is nine flat fields:

```json
{ "id": "https://ns.scf.example/map/2026-2/ac-2--iso-5.16",
  "source-ref": "https://ns.nist.gov/sp800-53/req/AC-2",
  "target-ref": "https://ns.iso.example/27002/req/5.16",
  "relationship": "intersects",
  "confidence": "reviewed",
  "provenance": {"author-ref": ".../party/scf", "date": "2026-05-01"} }
```

A mapping is its own object with its own provenance because a third
party's crosswalk belongs to *neither* endpoint — and because without a
first-class home, mappings regress into relation-type strings, which are
props wearing a coat.

## 2.3 Reality adds implementation: the system side

**Component.** One type for products, services, policies, processes — and
systems, which are simply components with members. That merge is not
minimalism for its own sake: in the American program's daily reality,
*your system is my component* — a SaaS inherits from a PaaS inherits from
an IaaS, and leveraged authorization is the load-bearing mechanism.
Authorization boundaries — the lines where legal liability attaches — are
explicit, identified objects on the component (`authorizations[]`, each
with its own id and optionally the members it scopes), and their absence
asserts *nothing*, because an absent flag must never be a legal claim.

**Implementation.** One edge — *this component satisfies that
requirement (that clause), this way* — with typed responsibility
(provider/customer/shared), parameter bindings, evidence references, and
inheritance edges that must name the specific authorization they lean on.
This single relation replaces two old constructs that said the same thing
twice (component definitions and SSP implemented-requirements); the
duplication was measured in the field when a professional authoring team
publicly abandoned component definitions because the model's complexity
exceeded its value.

**Assessment and Finding.** An Assessment records who checked what, how,
when, with what result and evidence — its *method* described through a
registered facet, which is how KSI-style automated criteria plug in
without a bespoke format. A Finding carries the aftermath: state, risk,
actions with (calendar-aware) due dates — the old POA&M, as fields. Both,
like Implementation and Tailoring, can carry **Deviations**: one typed
disposition record with one state machine
(investigating → pending → approved | withdrawn), replacing the four
historical FedRAMP extensions that encoded that identical machine four
times under four names.

**Attestation.** Compliance ends with a human signing a document, and
lawyers subpoena the exact view. An Attestation cryptographically bonds
the validated graph to the rendered artifact the human signed — which
template, which renderer, which digests — so "what the machine checked"
and "what the AO signed" can never quietly diverge again. The mechanics
(two digest domains, the bi-modal verification that distinguishes *exact
package proven* from *compliance content proven, packaging altered*) get
their own chapter (11); for the hour, know that the object exists and why.

That is nine: **Requirement, RequirementSet, Tailoring, Mapping** on the
content side; **Component, Implementation, Assessment, Finding** on the
system side; **Attestation** bonding the two worlds to paper.

```
            CONTENT                      SYSTEMS
  ┌─────────────────────┐      ┌───────────────────────┐
  │ Requirement         │      │ Component             │
  │   └ statements[]    │◄─────┤   └ authorizations[]  │
  │ RequirementSet      │ Impl │ Implementation ───────┤
  │ Tailoring ──────────┤      │ Assessment            │
  │ Mapping (crosswalks)│      │ Finding               │
  └──────────┬──────────┘      └──────────┬────────────┘
             │        Attestation         │
             └────────── bonds ───────────┘
                 graph ⇄ signed rendering

  on every object:  facets{}  ·  annotations{}
  sub-objects:      Deviation ·  authorizations
```

## 2.4 The two companions, and where extension went

Every object may carry two members that are not "the rest of the data" —
they are the entire, bounded answer to extension.

**`facets{}`** hold framework-specific semantics under a contract: each
facet name resolves (at bundle-assembly time, never during validation) to
a registered JSON Schema plus a declaration of *what it modifies* —
assessment, tailoring, selection, rendering. Tools validate what they
carry; tools that don't understand a semantics-modifying facet **stop,
with an explained error**, instead of guessing. That fail-closed rule is
the difference between this and props: three tools meeting one unknown
prop today do three different things and all claim conformance. The
German requirement grammar, the security-objective ratings, the American
glossary, reporting duties, effectivity windows, KSI-style criteria — all
of it lives here, schema-checked, exactly one lookup away (the stdlib
catalog is Appendix D; writing your own is Chapter 7).

**`annotations{}`** are the pressure valve: a flat string map for tool
bookkeeping and rendering hints, **excluded from every compliance
computation and from semantic digests by definition** — strippable,
ignorable, structurally incapable of carrying smuggled semantics, because
nothing conformant can see them. The American corpus supplied the honest
use case (`web_name`, `do_not_link` — pure chrome).

> **Don't** reach for an extension mechanism until the kernel has refused
> you. Measured across three authorities, **over 70 % of all 22,000+
> counted prop instances needed no extension construct at all** — they
> were membership, ordering, history, aliases, and clause structure:
> kernel mechanics, hand-imitated for lack of a kernel.

## 2.5 For OSCAL 1.x veterans: what happened to everything

| You knew (OSCAL 1.2.2) | It became | Where |
|---|---|---|
| Catalog (groups/controls/parts) | Requirement objects + nested RequirementSets; statement parts → `statements[]`; guidance/objectives prose → prose-only statements (`modality: "unspecified"`) or Canonical-Reference/framework facet payloads | Ch. 4–5 |
| Profile + resolution spec (merge/keep/combine) | Tailoring: selection + identity-addressed ops; a half-page deterministic algorithm; merge semantics **do not exist** — global identity made them unnecessary | Ch. 6 |
| Component Definition | `Component.capabilities[]` | Ch. 9 |
| SSP | Component (+`authorizations[]`, system-context facet) + Implementation edges; the *document* is an L4 rendering, bonded by an Attestation | Ch. 9, 11 |
| Assessment Plan / Assessment Results | Assessment (methods via `assessment-criteria@1`) / `Assessment.result` + Finding | Ch. 10 |
| POA&M | `Finding.actions[]` + Deviation lifecycle | Ch. 10 |
| Control Mapping Model (2026) | the Mapping type — nine flat fields instead of a document model | Ch. 8 |
| props + `ns` | registered facets (contracted) · annotations (invisible) · **or nothing** — the >70 % that were kernel deficits | Ch. 7 |
| `label` / `alt-identifier` / `sort-id` props | kernel `label`, `aliases[]`, `sequence` | Ch. 3, 5 |
| Metaschema, XML/YAML, Schematron | JSON Schema 2020-12 · one serialization · 8 primitives with rationale-on-failure (XML survives only as a one-way transit projection for guarded networks) | Ch. 11–12 |
| party-uuid / import plumbing | L0 references + the content manifest | Ch. 3, 11 |

If a 1.x concept is not in this table, check the specification's
migration levels (D16): it maps natively, rides in a compatibility facet,
or is preserved opaquely with no semantic claim — and the level is always
declared, never implied.

## 2.6 Your path from here

The hour is over; the paths diverge.

**Framework authorities [A]** continue straight: identity and namespace
governance (3), writing statements (4), sets and baselines (5), tailoring
(6), facets (7), mappings (8) — then migration (14) when the catalog is
real. **Tool implementers [T]** may jump: identity (3) for the mental
model, then the validator chapter (12) and safe consumption (13), with
integrity (11) before anything touches signatures — noting that Chapter
12's measured numbers arrive with the v0.6 gate. **Consumers, assessors,
CISOs [C]** take the assurance spine: systems and inheritance (9),
assessment and deviations (10), integrity and what a signature actually
proves (11), then what a conformance claim entitles you to demand of a
vendor (15).

One honesty marker before you go, in the book's own evidence-tier
language: everything this chapter *showed* is measured or specified;
everything it *promised* about full corpora — that all of ISM, all of
Grundschutz++, all of CR26 re-encode with zero unexplained fields — is
**designed-for**, with the executable proof gated at v0.6 and reported in
Chapter 12 and Appendix E when it lands. The book will not blur that line,
and you should not let any vendor blur it either.

Next: Chapter 3, where the Australian namespace shows how identity
governance is done well, a deleted American registry shows what happens
otherwise, and you choose the URI prefix your framework will still be
standing behind in 2040.
