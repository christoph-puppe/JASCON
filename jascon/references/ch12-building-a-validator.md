# The JASCON Handbook
## Part Four — Building Tools
# Chapter 12 — Building a Validator (The Weekend Chapter)

**Audience:** tool implementers [T]. Authorities should skim §12.1 and
§12.7 to know what they may demand of vendors; consumers get the
user-facing consequences in Chapter 13.
**Companions:** Specification v0.5 — D14, D15, D13 + Appendix B, D3,
D10; the conformance corpus (executable schemas and golden artifacts
arrive with the v0.6 gate).

**Evidence marker, up front:** "weekend" is the architecture's
*acceptance test*, not yet a measured fact. The lines-of-code and
contributor-hours this chapter's margins are designed to hold arrive
with the v0.6 gate, measured in two independent languages. Until then,
this chapter teaches the walk and labels every number that is still a
promise — per the book's own rules.

---

## 12.0 The task

Friday evening. An empty repository, your language of choice, and a
goal with a deadline in its name: by Monday morning, your tool
correctly validates any Core-tier bundle — offline, with verdicts that
explain themselves.

The reason this is a plausible weekend rather than a quarter is the
list of things you will **not** build. No bespoke meta-language parser
— the schemas are plain JSON Schema 2020-12. No profile-resolution
algebra with merge strategies — global identity deleted the problem.
No three synchronized serializations — there is one. No
Schematron-class rule engine — there are eight primitives, five of
which are structural and yours this weekend. The old world's
implementation cliff is what produced its validator monoculture —
every constraint dispute bottlenecked on one team, every consumer
inherited one implementation's interpretations. The point of the
weekend target is ecological, not athletic: an ecosystem where
validators are cheap is an ecosystem where no single implementation's
readings become de-facto law.

## 12.1 The contract you are implementing

One sentence per tier, and the first is the one to tattoo somewhere
visible:

**Core is the passive tier.** Validate structure, verify package
digests, resolve references locally, preserve everything you do not
understand — and perform *no semantic computation whatsoever*. No
tailoring resolution, no assessment logic, no selection, no rendering
of normative content, no canonicalization. If your weekend code is
tempted to *interpret*, you have left Core. **Portable** is where
meaning begins: facet validation, capability declarations,
fail-closed, semantic digests, the semantic primitives, the tailoring
resolver — the second weekend, in §12.6. **Authority** is a
publisher's tier, not a validator's; Chapter 3 covered its duties.

And the development method is dictated by how conformance itself is
defined: **the test suite is the specification.** Like CommonMark, a
conformant implementation is one whose verdicts match the corpus of
golden artifacts — so clone the corpus first, wire it into your test
runner second, and write the validator third. You are done when the
verdicts match, not when you feel done.

## 12.2 Friday night: schemas and shapes

Load the nine type schemas plus the sub-objects (Deviation,
authorization contexts) and the content-manifest schema. Until the
gate ships them as artifacts, hand-code them from the specification's
Appendix A — a bounded evening's work precisely because the shapes are
shallow.

One data-model decision earns its keep all weekend: implement a
generic object envelope — id, version, label, aliases, lifecycle,
`facets`, `annotations`, `relations` — shared by all nine types, with
typed payloads per kind. Statements are a first-class list inside
Requirement, because half the structural rules address them by id.

> **Don't** let your parser "clean up" what it doesn't recognize. The
> preservation duty starts at deserialization: unknown registered
> facets and annotations are cargo, never noise — the old world's
> three-tools story (one preserved, one guessed, one refused, all
> claiming conformance) began with parsers that felt entitled to
> normalize. Model unknown facet payloads as opaque values you can
> emit unchanged.

## 12.3 Saturday morning: the manifest walk

The bundle is a directory (or archive) plus a content manifest, and
the manifest is your world model. The walk: parse the manifest; for
every listed object and rendering, verify the **package-digest**
against the bytes (`digest-verified` — your first primitive, and your
first passing corpus cases); build the path map `id@version → bytes`.
That map *is* local resolution: implement `references-resolve` as
"every reference string in every object lands in this map," and
sealed mode falls out by construction — the cheapest way to guarantee
zero network access is to not link an HTTP client into the Core path
at all.

Define your error shape now, because the specification makes it
load-bearing: every rule instantiation carries a machine id, a human
**rationale**, and a failure message, and *the rationale prints on
failure*. `{rule, target, rationale, message}` from the very first
verdict.

> **Don't** ship a rule without its rationale string. The old world's
> defining pathology — the dispute that opened this book — was a
> constraint rejecting valid content whose reason, by the maintainers'
> own discussion, nobody could state. In this architecture a rule that
> cannot print its *why* is non-conformant by design; your two-a.m.
> users are the beneficiaries.

## 12.4 Saturday afternoon: the structural primitives

Two are already done (`references-resolve`, `digest-verified`). Three
remain, each an hour-scale function with corpus cases attached.

**`unique-within(scope, field)`** — statement ids unique per
requirement, `sequence` unique per members list, authorization ids
unique per component. The motivating corpse is Chapter 3's: two
national catalogs sharing control-ID strings, structurally
uncombinable. Global uniqueness is the publisher's duty; *local*
uniqueness is yours to check, and it is a hash-set.

**`code-from(codesystem@version)`** — modality codes, lifecycle
states, deviation types and states, mapping relationships, duration
units: load the stdlib code systems (pinned like any facet schema) and
verify membership. Pure lookup — the deliberate boringness is the
feature.

**`prose-params-resolve`** — the 216-killer, and the most satisfying
test cases in the corpus. Scan each statement's prose for `{param:…}`
tokens; every token must name a declared parameter of *that*
statement (error), and every parameter should be referenced somewhere
(lint). With this function green, the census's ugliest defect class —
216 pseudo-placeholders drifting silently inside schema-valid national
documents — is not detected but *unwritable*: there is no valid way to
express it.

Note what is *absent* from Saturday: `conditional-apply`,
`modality-monotonic`, `attestation-binds`. They are semantic — 
Portable's problem, deliberately outside your weekend.

## 12.5 Sunday: ship Core

What remains is discipline, not invention. Finish the preservation
behavior: a Core tool that *verifies* only reads; a Core tool that
*forwards* copies bytes — because re-serialization changes package
digests, and Core, which computes no semantic digests, has no
vocabulary to explain the difference (Chapter 11's Semantic Match
belongs to Portable). Wire the CLI — `validate <bundle>` emitting the
verdict list in your error shape — and run the full Core corpus:
schema cases, digest cases, resolution cases, uniqueness cases, code
cases, prose-token cases. Green corpus, shipped Core.

Then permit yourself the structural comparison (numbers at the gate,
structure already true): the minimal *old-world* equivalent — validate
one catalog and resolve one profile — required understanding a bespoke
meta-language, handling three serializations with a markup-mapping
layer, and implementing a resolution algebra with merge semantics that
had its own specification. Your weekend build required JSON Schema, a
digest loop, a hash map, and five small functions with printable
reasons. That asymmetry *is* the complexity-budget reallocation,
experienced from the implementer's chair.

## 12.6 The second weekend: Portable, where meaning begins

Portable is a different kind of work — smaller in code than Core's
schemas, heavier in care — and its build order matters.

**First, canonicalization.** RFC 8785 (JCS) plus the two determinism
guards, test-vector-driven: the **empty-omission** normalization
(structurally optional arrays/objects with zero elements are omitted
before JCS — the corpus vectors exist because two honest tools
otherwise fork digests on `"aliases": []` versus absence) and
**decimal-as-canonical-string**. With JCS green, semantic digests are
one function.

**Second, the facet layer and the gate.** Load facet schemas from the
manifest's pins — verifying *exact version and digest*, because the
pin, not the URL, is the trust anchor — and validate every payload.
Then give your tool its **capability declaration** as ordinary
configuration:

```json
{ "understands": ["https://ns.oscal.org/stdlib/facet/assessment-criteria@1.2.0"],
  "preserves-unknown": true,
  "fails-closed-for": ["assessment", "tailoring", "selection"] }
```

…and implement the **fail-closed gate** as one choke-point function
called before *every* semantic computation: collect the
`modifies-semantics` declarations of all facets present on the
subject; if any declared class intersects the computation you are
about to perform and the facet is not in `understands`, abort — with
the offending facets named in the error. Two definitional edges keep
the gate decidable: `private:` facets are `[]` by definition (ignore,
preserve, never abort), and a registered facet whose descriptor omits
the declaration counts as modifying *all four* classes — dangerous by
default, exactly as Chapter 7 warned publishers.

**Third, the semantic primitives.** `modality-monotonic` is the
Chapter 4 lattice as a small reachability table — new ≥ old along a
drawn line passes, everything else (including every axis change)
demands an attached Deviation. `conditional-apply` is a three-predicate
interpreter (`field-equals`, `param-equals`, `present`) with at most
one reference hop through your manifest map and no nesting — an
afternoon, by construction, because the vocabulary was fenced to make
it one. `attestation-binds` is Chapter 11's bi-modal state function:
verify the envelope per the DSSE profile's seven answers, then return
Full Match, Semantic Match, or failure — never a boolean, because the
two green states mean different things and your callers must see
which.

**Fourth, the tailoring resolver** — Appendix B, implemented
literally: expand `selects` through set nesting and apply `excludes`;
validate every operation's address (missing target: fail closed;
**two operations on one target in one Tailoring: error**, not
last-wins); apply in list order to deep copies, enforcing the D13
rule table — parameter bounds against declared types and choices,
tightening directions, the prose intent flag, Deviation checks for
weakening moves and semantic detaches; emit the resolved package with
a fresh manifest and provenance naming the Tailoring. The corpus
hands you the adversarial cases by name: bounds violations, same-
target conflicts, lattice edges, chained overrides.

## 12.7 The harness, and the honest numbers

The specification converted "weekend validator" from slogan to
**acceptance test**, and the harness is its instrument: two
implementations in different languages, written independently;
lines of code counted excluding generated schemas and tests;
implementation time for a fresh contributor, clocked; the full
conformance corpus executed by both; and a comparison run against a
minimal old-world validator-plus-resolver as the baseline. Release
of the specification's final version is gated on two independent
implementations agreeing with the corpus — the CommonMark discipline,
adopted whole.

Until the v0.6 gate runs, every number this chapter implies is
**designed-for** — and the margin where the measured LoC and hours
will sit stays honestly empty. The harness is how the project keeps
itself honest; running it yourself is how you keep the project
honest. Both are the point.

Your validator now says *no* correctly, offline, with reasons
attached. What it cannot yet do is be pleasant to live with: turning
fail-closed halts into actionable next steps, deciding what a consumer
may safely do with half-understood bundles, handling pin conflicts
when two suppliers' packages meet, and rendering without crossing the
chrome line. That operational craft — consuming safely — is
Chapter 13.
