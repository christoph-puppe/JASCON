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
Schematron-class rule engine — there are ten primitives, five of
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

Load the eleven type schemas plus the sub-objects (Deviation,
authorization contexts) and the content-manifest schema. Until the
gate ships them as artifacts, hand-code them from the specification's
Appendix A — a bounded evening's work precisely because the shapes are
shallow.

One data-model decision earns its keep all weekend: implement a
generic object envelope — id, version, label, aliases, lifecycle,
`facets`, `annotations`, `relations` — shared by all eleven types, with
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
the manifest is your world model. The walk: parse the manifest; read
`kernel-version` before anything else and stop if it names a kernel
you do not implement, with the pinned version and your own in the
message (KERNEL-2; absent means 1.0.0); for
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

**`prose-params-resolve`** — the binding check, and the most satisfying
test cases in the corpus. Scan each statement's prose for `{param:…}`
tokens; every token must name a declared parameter of *that*
statement (error), and every parameter should be referenced somewhere
(lint). With this function green, a slot in the prose that names no
declared parameter is not detected later but *unwritable*: there is no
valid way to express it.

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
Where a pin carries a stdlib id, compare its schema with the descriptor
you ship and fail on any difference: the pin of a standard facet is the
standard, verbatim (D26). Do all of this in the one function that loads
pins. The reference validator had two until 2026-11-10; the one for its
own example folder checked the digest only, and that folder pinned a
stub under a stdlib id. The default run reported it green, the same
folder named as a bundle failed.
Then give your tool its **capability declaration** as ordinary
configuration:

```json
{ "understands": ["https://ns.jascon.net/stdlib/facet/assessment-criteria@1.2.0"],
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

## 12.7 A third sitting: Risk and the coverage join *(2.0.0)*

Risk is the tenth type and `risk-coverage` the ninth primitive (D23,
Appendix A.9b, B.1.9). Together they are an evening, on one condition:
the tailoring resolver of 12.6 already expands a selection. Build in
this order, because each step is the precondition of the next.

**First, type it.** The Risk shape is one more entry point for the
schema walk of 12.2, and it is the first that leans on conditionals:
RISK-2 to RISK-6 and the first half of RISK-13 are `if`/`then` pairs.
If your schema library, or your hand-written subset interpreter, has
not needed `if`, `then` and `const` so far, it needs them now. The
date formats are `pattern`s, the duration count is `integer` with
`minimum`.

**Second, name the rule.** A schema says no; it does not say which
rule said it. Keep a table from rule id to rationale and a function
that mirrors the conditionals one to one, and print both whenever an
object carries the Risk signature (`scenario` or `owner-ref`) and
matches no type:

```
FAIL [RISK-3] treated without acceptance - a treated risk names its
option and carries its owner's signature (ISO/IEC 27001 6.1.3 a, f)
```

That function never accepts an object. The schema decides; the
function explains. The vectors hold you to the id (`expected-rule`),
never to a library's message text.

One check belongs to the manifest walk and is triggered here: a bundle
in which you have just typed a Risk, or a Finding with `risk-refs`,
must pin `kernel-version` 2.0.0 (KERNEL-1). The same holds for a Check,
for a manifest with a pack header, and for a Component that carries
`product-version`. `kernel-vectors.json` has eleven cases for the pin
and fourteen `shape-vectors` for three fields 2.0.0 typed or added: a
Deviation's `opened` (DATE-1), the `due` of a Finding's action (DATE-2)
and `product-version`. The schema refuses; your code only names the
rule, as for RISK-1 to RISK-6.

**Third, close and type the edges.** Four references on a Risk are
closure-required and typed: `treatments[].requirement-ref` names a
Requirement, `component-refs` name Components, `tailoring-refs` name
Tailorings (RISK-7, RISK-12), and every `statement-ids` entry names a
statement of its target (RISK-8). `Finding.risk-refs` is landmark, but
a target that does resolve must be a Risk. Two more checks belong here
although they live outside the Risk: a Tailoring's `set-ref` names a
RequirementSet, and an `excludes` entry names a Requirement or a Set.
Skip the type half and the join below runs on a mis-aimed id and
returns an empty answer without an error. Finally RISK-13's second
half: `rating` and `residual-rating` carry the same `scale-ref`, and so
do their `likelihood` and their `impact` where both sides have one. You
never invent a way to combine the two; the matrix is the
organisation's, and you only look it up (SCALE-4, below). What you
do check, where the manifest pins a scale definition under `scales`: load
it like a facet pin (file, digest, shape, id and version as pinned, no
level twice — SCALE-1), then hold every level a Risk states on that
scale to the listed levels (SCALE-2), and note a residual that sits
above its counterpart in the list order (SCALE-3). An unpinned
`scale-ref` is opaque; check nothing. A level scale may carry a
`matrix`: check once per bundle that its two scales are pinned and that
every pair of their levels has exactly one cell holding one of the
scale's own levels, and drop a matrix that fails. Then, for a rating
that states both inputs on those two scales, look the cell up and
compare (SCALE-4): unequal fails, unless the rating carries an
`override-rationale`, which you report as a note. `scale-vectors.json`
has eighteen cases.

**Fourth, the join.** If the bundle carries no Tailoring at all,
nothing was scoped out: take every Requirement in force as one implicit
selection and go to step 5. Otherwise, for every Tailoring whose
`lifecycle` is not `withdrawn`:

1. Expand the `set-ref` selects through nested Sets to any depth, with
   a seen-set, so that a malformed cycle terminates. A fixed depth
   limit loses requirements silently.
2. Expand the excludes the same way and subtract them.
3. Drop requirements whose `lifecycle` is `withdrawn`, and say so.
4. Mark the selection *open* if any select is a predicate. This
   primitive does not evaluate predicates; the resolver does. An open
   selection is a lower bound.
5. Take the Risks that belong to this Tailoring: those whose
   `tailoring-refs` name it, and those that carry none.
6. Sort each of them into one of three buckets by one test each.
   *Justifies:* not retired, `lifecycle` neither `withdrawn` nor
   `draft`, `state` assessed or treated, a `treatment` present.
   *Pending:* live, and short of that. *Lapsed:* retired or withdrawn.
7. A selected requirement named by a justifying Risk is `covered`.
   Every other selected requirement is `uncovered`; if a pending Risk
   names it, list it under `pending` as well, else if a lapsed one
   does, under `lapsed`.

**Fifth, RISK-11.** For every live Risk and every requirement its
treatments name: is the requirement in the selection of at least one
Tailoring the Risk belongs to? If it is, done. If the requirement is
withdrawn, fail. If one of those Tailorings is open, report
*undecided* and do not fail. Otherwise fail. The rule is asked in
every bundle, including the one in which everything was excluded and
the one whose only Tailoring is withdrawn; without any Tailoring only a
withdrawn requirement can fail it.

**Sixth, the verdict.** `uncovered` is a report line. Offer the
program's policy as a switch, and under the switch print the one
normative failure per uncovered requirement:

```
FAIL [risk-coverage] <tailoring>  selected <requirement>
  justified by no Risk
  rationale: ISO/IEC 27001 6.1.3 d - inclusion in the Statement of
  Applicability carries its justification
```

The switch applies to every Tailoring at every tier, and to the bundle
that carries no Risk at all: an empty register fails for every selected
requirement.

**The traps, each one a defect the reference validators shipped and a
vector now pins.** Counting every live Risk as a justification, so
that a three-field stub satisfies the switch. Joining bundle-wide, so
that a risk about one system justifies the control in another system's
Statement of Applicability. Letting a retired Risk justify for ever.
Failing RISK-11 under an open selection, a hard verdict from knowledge
the primitive does not have. Letting one open Tailoring anywhere make
the rule undecided for every Risk. Skipping the report when the bundle
holds no Risk, which exempts the emptiest register from the strictest
policy. Skipping it when the bundle holds no Tailoring, as if an
untailored catalogue had no controls in play.

**What the corpus hands you:** `risk-vectors.json`, 73 cases. The
object vectors exercise typing and rule naming, the bundle vectors
closure, the three buckets, scope and RISK-11, and eight transitions
the state machine of C.3c. What it does not hand you is scale: the one
converted corpus with Risks holds two of them and no Tailoring, so
your join will meet its first real Statement of Applicability in your
own data. The reference implementation of this section is about 160
lines of Python, the closure checks aside; the PowerShell twin carries the same logic and
passes the same 73 risk vectors (first run on Windows PowerShell 5.1, 2026-11-11).

## 12.8 A fourth sitting: Check and the verdict *(2.0.0)*

Check is the eleventh type and `check-verdict` the tenth primitive (D24,
Appendix A.9c, B.1.10). It is the largest addition since Core, and most
of it is one small engine you must write yourself.

**First, type it.** The Check shape adds three schema keywords to what
12.7 needed: `oneOf`, `not` and `else`. An assertion with `present` or
`absent` must carry no `expected`, every other one must, and the
observation is either `{facts}` or `{resources}`. The PowerShell twin
stopped at exactly this point before its port, with `schema keyword
'not' outside the documented subset`.

**Second, write the regular-expression engine. Do not borrow one.**
`matches` and `matches-not` take I-Regexp (RFC 9485). The temptation is
to translate the pattern and hand it to your language's engine. That is
the one thing the specification forbids, because Python, .NET and
ECMAScript disagree on `\d`, `\w`, `.`, anchors and flags, and a
backtracking engine can be stalled by a pattern. Parse the grammar
(a page of ABNF), compile to states, and match by simulating the set of
live states: linear in program times input. In the reference, parser and
matcher together are about 200 lines. Three things are the kernel's and
not the RFC's: the pattern matches the whole value, `^` and `$` are
ordinary characters, and the limits are 256 characters per pattern,
1,000 states and 4,096 characters per value. Work from the RFC as
published: its grammar keeps surrogate code points out of patterns,
which the working group's file did not, and the three engines here
were wrong on that until they were compared with it. The 42 regex
vectors include the traps where a host engine answers differently.

**Third, the verdict.** One function over a Check, an observation and
the bound parameters. An undeclared or unobserved fact, a mistyped
value or an unbound parameter is `inconclusive`. Never substitute a
default. Combine by strong Kleene AND: a definite failure decides
before an unknown does. Decimals compare by value and never as floats.
With `each`, evaluate every resource, do not stop at the first
failure, and report the counts and the share:

```
3 of 4 applicable file resources not satisfied (75 %)
```

Compute the percentage in integers, `(200·part + whole) div
(2·whole)`, clamped to 1 and 99 while some but not all resources fail.
Twelve vectors pin it, so that three implementations print one number.

**Fourth, the rows.** CHECK-8 to CHECK-14 hold a run to its Check: the
digest, the recomputed outcome, the aggregate, the parameters against
the named Tailoring, the collector id, the Finding that points back.
Recompute; do not trust a recorded outcome. Compare key sets, not only
the keys you came for: a row names only parameters its Check reads, with
or without a Tailoring, and a `collector-id` on a Check that declares no
collector names nothing.

**Fifth, the evidence chain.** CHECK-15 walks from the row to the
record to the raw outputs in `evidence/sha256/` beside the manifest. A
file whose name is not the SHA-256 of its bytes fails, and so does a
relative reference to any other place, before you read it. A reference
with a URI scheme is a note. A missing raw output is a note, withheld,
and no failure. Row and record agree on the collector and on the
observation: a row with an observation needs a record with its
`observation-digest`, a row without one a record without.

> **Don't** let an optional field switch a comparison off. The first
> reference validator compared collector and observation digest only
> when both sides carried them, and looked up a collector only when the
> Check had the facet. Four outside reports of 2026-11-13 were this one
> mistake: a field left out is a difference to report, never a reason to
> skip.

You never run a collector. A validator that executes code from a bundle
it was asked to check has stopped being a validator.

The corpus for this sitting is `check-vectors.json`: 199 cases, of
which 42 are for the engine alone.

## 12.8b A short fifth sitting: advice packs *(2.0.0)*

No type and no primitive (D25, Chapter 9.7): eleven rules over things
you already load. Three places need code.

**The manifest walk.** A manifest with a `pack` header is an advice
pack. Every object it lists is a Component (ADVICE-1), every id shares
one origin with `pack.id` and `publisher.ref` (ADVICE-2), no facet
declares a semantics class (ADVICE-3). Read the Attestations that lie
beside a pack's manifest: the pack may not list them, and without them
you cannot say whether the publisher is claimed or proven.

**The graph.** Capability ids are unique (ADVICE-4); clause ids and
suggested values are checked only where the requirement is in the bundle
(ADVICE-5, ADVICE-6); a `capability-ref` is a bare id of the edge's own
component or `<component-id>#<capability-id>` of a member (ADVICE-7).
Run ADVICE-7 over old content before you trust it: on the shipped
bundles it found one edge that cited a capability its own component did
not declare.

**The store.** Files under `packs/sha256/` are kept manifests: the name
is the SHA-256 of the bytes, the content is a manifest with a pack
header, and the bundle's own manifest does not list them (ADVICE-8).
Each object a kept manifest lists is in the bundle at that version and
semantic digest (ADVICE-9); one kept manifest per pack, one pack per
object (ADVICE-10). Composing a pack into a set is the composition
engine of 12.6 with one lawful replacement (ADVICE-11).

`advice-vectors.json` has 74 cases: 9 shape, 15 pack, 21 graph, 11 kept
manifest, 8 publisher, 10 import.

## 12.9 The harness, and the honest numbers

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

The harness ran in July 2026 (specification IV.5). The measured
numbers at 1.0.0:
994 non-blank, non-comment lines of Python plus one schema library,
1,163 lines of dependency-free PowerShell 5.1, both green on the same
157 vectors, against 30,905 lines for the predecessor format's toolchain it was
compared with, which also authors and resolves and therefore does
more. Three things are not measured: the hours of a fresh contributor,
an implementation by someone other than the author, and the size of
both validators since Risk was added. The harness is how the project keeps
itself honest; running it yourself is how you keep the project
honest. Both are the point.

Your validator now says *no* correctly, offline, with reasons
attached. What it cannot yet do is be pleasant to live with: turning
fail-closed halts into actionable next steps, deciding what a consumer
may safely do with half-understood bundles, handling pin conflicts
when two suppliers' packages meet, and rendering without crossing the
chrome line. That operational craft — consuming safely — is
Chapter 13.
