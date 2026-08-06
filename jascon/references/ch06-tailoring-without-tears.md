# The JASCON Handbook
## Part Two — Authoring Content
# Chapter 6 — Tailoring Without Tears

**Audience:** framework authorities [A] building tiers and overlays;
equally load-bearing for consultants and agencies who tailor other
people's catalogs. Tool implementers meet the resolver again in
Chapter 12.
**Companions:** Specification v0.5 — D13, D8, D9 (lattice), Appendix B
(the resolution algorithm this chapter paraphrases).

---

## 6.0 The task

The American corpus hands us today's job in its rawest form. One rule —
the Initial Incident Report — four certification classes, four deadlines
(six hours for Class A down to a business day elsewhere), and in places
even a different binding force per class. The old format solved this by
**inlining**: a `varies_by_class` block on the rule, four near-identical
statement copies, maintained forever in parallel — the same pattern, at
larger scale, that gave 1.x a profile-resolution algebra so intricate it
needed its own specification and still had no safe answer at merge time.

Your task: build Class A as a **Tailoring** — and collect, on the way,
everything the tailoring layer is: how selection works, what the eight
operations are, which changes are free and which ride the audited
channel, how resolution runs, how overrides chain, and whose job the
"show me all four classes at once" view really is.

## 6.1 What a Tailoring is — and the two fears it retires

A Tailoring is a small object: *what it selects, what it excludes, and an
ordered list of operations to apply to the survivors.*

```json
{ "id": "https://ns.fedramp.gov/cr26/tailoring/class-a",
  "version": "2026.07.14.01",
  "selects":  [ {"set-ref": "https://ns.fedramp.gov/cr26/set/all-20x"} ],
  "excludes": [ ],
  "operations": [ … ] }
```

Selection is a set reference (the normal case, composing directly with
Chapter 5's baselines) or one of exactly three bounded predicates —
`field-equals`, `param-equals`, `present` — with at most one reference
hop and no nesting. That short leash is deliberate: an earlier draft
casually allowed "selection by facet query" and was caught smuggling an
undefined expression language into the layer one decision after banning
expression languages. The predicates you get are the predicates there
are.

Two historical fears made 1.x tailoring miserable, and both are
structurally gone. **Merge semantics** — use-first, keep, combine, the
whole apparatus — do not exist here, because global identity (Chapter 3)
means two sources can never collide into an ambiguity that needs a
strategy. And **positional fragility**: the old temptation was generic
JSON Patch, whose paths address array *positions* — and two independent
hostile reviews of this architecture converged, without coordination, on
the same condemnation: one upstream erratum inserting a parameter shifts
every index after it, and every downstream tailoring silently patches
the wrong target. Baseline-shatter, recreated. Here every operation
addresses **identity** — requirement id, statement id, parameter name —
and an address that no longer resolves is a **fail-closed error with a
printed rationale**, never a nearest-index guess.

> **Don't** patch by position, ever, in a distributed ecosystem. The
> failure this prevents: an upstream insertion silently repointing every
> downstream tailoring — condemned independently by both adversarial
> reviews of this design, and unrepresentable in the operation
> vocabulary you are about to meet.

## 6.2 The eight operations

The vocabulary is closed, versioned, and short enough to memorize:

**`set-parameter`** — the workhorse: bind or change a parameter value,
per statement. **`set-modality`** — move a clause along the lattice.
**`set-field`** — whitelisted scalar fields (title and friends).
**`replace-prose`** — swap a language's prose, carrying an intent flag
(§6.3). **`add-relation` / `remove-relation`** — informative links.
**`attach-facet` / `detach-facet`** — add or remove facet payloads.

Every operation shares the address shape:

```json
{ "op": "set-parameter",
  "requirement-ref": "https://ns.fedramp.gov/cr26/req/IEC-CSO-IIR",
  "statement-id": "s1",
  "parameter": "iir-deadline",
  "value": {"type": "elapsed-duration", "num": 6, "unit": "hours"} }
```

Pin the target's exact version when you can (the specification says
SHOULD); pinned or not, a vanished address fails closed. And if you find
yourself wishing for a ninth operation: that is a change request against
the versioned vocabulary, not a license to improvise — the escape
discipline is identical to the primitives', because an open-ended op set
is just an expression language on a payment plan.

## 6.3 Strengthen freely, weaken on the record

The governing idea of this section is worth stating before the rules:
**regulators do not want weakening forbidden — they want it auditable.**
The Deviation sub-object is that audit record: a typed disposition with
a real state machine —

```json
"deviations": [ { "type": "risk-adjustment",
  "state": "pending",
  "rationale": "…", "approver-ref": "…", "opened": "2026-07-01" } ]
```

— `investigating → pending → approved | withdrawn`, a lineage that comes
straight from the field: four separate historical FedRAMP extensions
once encoded this *identical* machine under four different names, the
strongest possible evidence of one missing concept. Here it is one
concept, and the tailoring rules below decide when an operation must
carry one.

**`set-modality`** consults Chapter 4's lattice. Upward along a drawn
line is free — SOLLTE → MUSS, `may → may-only`, the everyday hardening
of every elevated baseline. Downward requires a Deviation. And axis
changes — `may → must-not` — are never "monotone" in either direction:
a semantic about-face always rides the audited channel.

**`set-parameter`** validates against the parameter's declared type,
cardinality, choices, and range — always. This closes what a reviewer
correctly called the evasion backdoor: without bounds enforcement,
tailoring could set a `choice` of {tls12, tls13} to `md5` and the typed
algebra would be theater. Out-of-bounds is a validation error, or a
deliberate act carried by a Deviation. Within bounds, the **tightening
direction** you learned to declare in §4.4 does its work: with
`tightening: lower` on a deadline, Class A's move from one business day
to six hours passes silently, while any easing is forced onto the
record. Undeclared direction means undeclared freedom — your call as
the authority, made explicit either way.

**`detach-facet`** requires a Deviation whenever the facet declares
itself semantics-modifying — removing the assessment criteria from a
requirement is weakening by amputation, and the machinery treats it as
such. **`replace-prose`** carries `intent: editorial | substantive`;
editorial (typo, translation) is free, substantive requires a Deviation
— the honest handling of the one weakening no machine can adjudicate:
whether new prose is softer than old is undecidable, so the *author's
declaration* is what gets audited. **Relations** stay free — they are
informative; normative cross-framework claims are Mapping objects with
their own lifecycle (Chapter 8).

And the deliberate exception, defended in the specification against a
reviewer who wanted it otherwise: **excluding is selection, never
weakening — no Deviation.** Baselines are *made of* exclusions: five
Australian classification tiers, four American classes, every scoped
subset Chapter 5 just taught you to build. A deviation record per
exclusion would bury those baselines under thousands of ceremonial
entries and kill the mechanism that just absorbed 5,900+ membership
props. Weakening means softening an obligation you *kept*; deciding
what is in scope is a different act, and the model refuses to confuse
them.

One more boundary, decided in the v0.6 cycle (D13 rev): **whose record
is a Deviation?** The consumer's. A Deviation documents an
*implementation's* departure from its governing resolved set — so the
duties in this section bind Tailorings at consumption, and **an
authority tailoring at Authority tier owes none of them.** When FedRAMP
publishes four class variants of its own rules, that is not FedRAMP
deviating from FedRAMP; the published Tailoring *is* the norm, its
audit record is the publication itself — versioned, signed, lifecycled
like every authored object. The converter corpse that forced the
question: 29 variant-only CR26 rules whose base prose had to be
*synthesized* so a pseudo-Deviation had something to point at —
ceremony without a wronged party. The weakening classification still
computes, so any consumer can ask "which classes ease the base?"
(CR26's measured answer across 111 class-variant modality moves:
zero); what disappears is only the obligation to mint a record where
nothing was departed from. And "whose Tailoring is it" is derived, not
declared (the layered anchor, v0.6 cycle): id origin matching the
selected content's origin claims authority; the authority's own
Attestation over the Tailoring proves it — proof beats prefix; mixed
or predicate selection is consumer work by definition.

## 6.4 Resolution you can memorize

The entire resolution algorithm — the successor to a specification-sized
algebra — fits in four steps:

**One:** expand `selects` (set references unfold through Chapter 5's
nesting; predicates evaluate on their one-hop leash), then apply
`excludes`. **Two:** validate every operation's address — unresolvable
targets fail closed; and **two operations addressing the same target
within one Tailoring are a validation error**, full stop. Not last-wins:
determinism you get either way, but silence you don't — if you want to
override, you do it where auditors can see it (step four). **Three:**
apply operations in list order to deep copies, enforcing §6.3's rules;
any violation without its Deviation halts with the rule's printed
rationale — the two-a.m. pipeline failure explains itself. **Four:**
emit a resolved package with a fresh content manifest, its provenance
recording the Tailoring's id and version.

**Chaining is the override path.** A Tailoring of a Tailoring is simply
the algorithm run again on the emitted package — each layer visible,
versioned, and attributable in the provenance chain. What does *not*
exist, by design and by memory of the corpse in 1.x's basement:
**auto-merging independent Tailorings.** Two parallel tailorings of one
catalog are two artifacts; combining them is an authoring decision made
by a human who writes a third, not a strategy enum that silently picks
a winner.

## 6.5 Worked: the four classes of CR26

Now the task from §6.0, end to end. The old shape: every rule carrying a
`varies_by_class` block — four embedded variants of force, statement
text, timeframes, artifacts — plus `pain_timeframes` matrices crossing
incident severity against report types. The JASCON shape:

**One base set** (`…/cr26/set/all-20x`) holding the rules once, with the
matrix *rows* modeled where Chapter 4 put them — as named parameters on
the relevant statements (one deadline parameter per report type, each
with `tightening: lower`).

**Four small Tailorings**, one per class, each selecting the base set
and issuing a handful of operations. Class A, abridged:

```json
{ "id": "https://ns.fedramp.gov/cr26/tailoring/class-a",
  "selects": [ {"set-ref": "https://ns.fedramp.gov/cr26/set/all-20x"} ],
  "operations": [
    { "op": "set-parameter",
      "requirement-ref": "https://ns.fedramp.gov/cr26/req/IEC-CSO-IIR",
      "statement-id": "s1", "parameter": "iir-deadline",
      "value": {"type": "elapsed-duration", "num": 6, "unit": "hours"} },
    { "op": "set-parameter", "…": "… one per report-type parameter …" } ] }
```

Where the old format varied `force` for a class, the class Tailoring
issues a `set-modality` — monotone moves pass, any easing rides a
Deviation, and for the first time a class that *relaxes* a federal rule
would be visible as exactly that, in a typed record with an approver.

The bookkeeping of the migration: four near-identical statement copies
per varying rule collapse into one statement plus four short operation
lists; an upstream erratum can no longer repoint a class's deadline;
and every class's delta is a diffable, citable artifact instead of a
block buried inside every rule it touches.

## 6.6 The all-classes view — real need, wrong storage

Be fair to the people who built `varies_by_class`: the ergonomics were
legitimate. An editor maintaining a rule, and a provider reading one,
both want *a single view with all four classes side by side* — that is
why the variants were inlined. The architecture keeps the view and
relocates it: rendering the comparison is an **L4 obligation over the
four resolved packages** — tools resolve each class and present the
matrix, while the data underneath stays deduplicated and
erratum-proof. The convenience was real; only its storage location was
wrong. (And because each class resolution is its own package with its
own manifest, each is independently attestable — which is exactly what
Chapter 11 will want when a class-specific authorization gets signed.)

## 6.7 The line you must not cross

One closing boundary, and it hands you the next chapter. Tailoring
changes *values of things that exist*: modality on the lattice,
parameters within their bounds or on the record, prose with declared
intent, membership by selection. What tailoring must never do is invent
**new semantics** — a new field, a new vocabulary, a new kind of claim.
The moment your overlay needs to *say something the kernel has no word
for*, you have left the tailoring layer and entered facet country: the
registered, schema-checked, capability-declared extension contract that
replaced the props economy. That contract — how to use the standard
library, when to write your own, and why unknown-but-registered content
is safe to carry while undeclared semantics fail closed — is Chapter 7.

---

## 6.A Addendum (first external review round): Amending a catalog you don't own — the supplement pattern

*Added after manuscript completion; the reviewer's question: "In 1.x I
amend a catalog — adding controls, possibly nested, to existing ones —
via profile and resolution. How is this done here?"*

The Core's answer inverts the mechanism: **you never inject into
someone else's objects — you author under your own prefix and compose
by reference.** Amendment is authorship, and authorship needs a
namespace. Three moves cover every 1.x add/alter case:

**Move 1 — new controls are new Requirements, yours.** Your
organization's supplementary control extending the intent of KONF.14
is a Requirement under *your* authority prefix
(`https://ns.your-org.example/req/ORG-KONF-14-A`), with its own
statements, lifecycle, and digests. Nothing about the upstream object
changes — which is the point.

**Move 2 — the amended catalog is a shadow set.** Publish
`your-org/set/konf-14-extended` whose members interleave the upstream
and your additions by `sequence`:
upstream `bsi/set/…konf-14` at 10, `ORG-KONF-14-A` at 20, and so on.
Consumers who want the amended view select *your* Set; consumers of
the pristine upstream are untouched. Multi-authority membership is
safe under global identity — the example bundle demonstrates a Set
spanning three authorities. Nesting works the same way: a shadow set
can wrap any taxonomy node at any depth.

**Move 3 — clause-level additions bind by reference, not injection.**
Adding a statement *inside* someone else's Requirement is impossible
by design: statements live within the owner's object and its semantic
digest. Instead, publish your own Requirement and declare the
attachment point — a `relations` edge (relation types are the one
extensible surface), or, for clause precision, a statement-scoped
Mapping (`target-scope: ["statement:s2"]`, relationship
`supplements` — since the v0.6 cycle a registered stdlib extension
code, C.5, no longer merely minted; non-chaining, degrades to
`supports`). The graph carries what injection used to smuggle.

The verb split that replaces profile semantics: **modifying** upstream
content (parameters, modality, prose) is Tailoring, under the
operation laws of this chapter; **adding** content is authorship,
under this addendum. What profile *resolution* used to produce — a
merged artifact whose lineage was a tool run — the shadow Set simply
*is*: explicit references instead of merge provenance, and the
interleaved reading view is a rendering (L4, with the provenance map
keeping whose-is-whose visible).

> **Don't** republish upstream objects with your additions baked in.
> The corpse is measured: eleven shared id strings across two
> publications of a single authority, ten silently diverged. Forking
> someone's objects to amend them recreates that hazard at
> inter-organizational scale — the shadow set exists so the amended
> view and the upstream truth never compete for one identity.

*See also: Appendix F Q23; Glossary, "Shadow set."*
