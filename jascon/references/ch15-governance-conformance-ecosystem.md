# The JASCON Handbook
## Part Five — Adoption
# Chapter 15 — Governance, Conformance, and the Ecosystem

**Audience:** everyone [all] — buyers deciding what a vendor's claim is
worth, authorities deciding what stewardship costs, implementers
deciding how rules change, program owners deciding what to write into
policy. This is the ecosystem's contract, in prose.
**Companions:** Specification v0.5 — D15, D10, D11, D13/D14 (versioned
sets), D19; the risk register (IV.2); the v0.6 gate (IV.5).

---

## 15.0 The task

Three chairs this time, one contract. A **buyer** holds a vendor
datasheet claiming "Portable-conformant" and needs to know what that
sentence entitles them to demand. An **authority** weighs the standing
costs of stewardship — registry hygiene, semver discipline, a facet
estate to maintain. An **implementer** has hit a genuine gap — a ninth
tailoring operation, a missing modality nuance — and needs the change
path that isn't a workaround.

The task of this final chapter is to make all three literate in the
same contract: what conformance claims mean and how to audit them, how
the federated registry keeps memory without keeping gates, who stewards
the standard library and under what arrangement with NIST, how the
rules themselves change — and how this architecture intends to coexist
with, and one day retire, the world it came from.

## 15.1 Tiers as purchasable promises

A tier claim is a promise with an audit path, and the audit path is
always the same: **the conformance corpus.** Like CommonMark before
it, this specification is defined by its test suite — golden bundles
with expected verdicts — and the final release itself is gated on
**two independent reference implementations** agreeing with that
corpus. "Conformant" means *the corpus says so*, never "the datasheet
says so."

What each promise contains, and the receipts a buyer asks for:

**Core** promises passive correctness: schema validation of all nine
types, sealed-mode operation, package-digest verification, local
resolution, the structural primitives, and preservation of everything
unknown — with *zero* semantic computation. Receipts: a sealed run
with the network demonstrably absent; a round-trip showing unknown
facets and annotations survive untouched; failure output carrying
rule ids and printed rationales.

**Portable** promises meaning handled safely: facet validation against
pins, capability declarations with the fail-closed gate, semantic
digests with the JCS guards, the semantic primitives, deterministic
tailoring resolution, and lawful bundle composition. Receipts:
Chapter 13's vendor test (*show me your gate message for a facet you
don't support*); green JCS vectors including the empty-omission cases;
a composition report from a real pin conflict. **This is the tier
program owners write into policy** — the specification maps the
RFC-0024 approved-format slot to Portable, and that one sentence is
what a procurement clause cites.

**Authority** promises publication worth trusting: governed stable
identifiers, alias and lineage records on every reorganization, both
digests per object, `.well-known` facet schemas with a deprecation
lifecycle, calendars behind every calendar-period. Receipts: the
prefix constitution exists; the last reorganization shipped its
`canonical-alias`/`replaces` records; a random object verifies against
both digests.

> **Don't** accept tier claims without corpus receipts. The failure
> this prevents is the old world's quiet constitution: one validator
> lineage whose interpretations *were* the standard — every dispute
> bottlenecked on one team, every consumer inheriting one
> implementation's readings, and "conformant" meaning whatever that
> codebase happened to do. Here the corpus is public, the verdicts are
> checkable, and a claim without receipts is a datasheet, not a
> property.

## 15.2 The registry: federation with a memory

Chapter 7 taught the mechanics from the publisher's chair; here is the
ecosystem view, and it is built on two graves. The centralized
alternative — a registry you petition — died in the field: the old
flagship's extension registry vanished with its repository,
recoverable only from a fork, and its queue had already taught authors
to route around it. So this ecosystem's registry is **federated by
construction**: vocabularies live at their owners' `.well-known`
paths, under their owners' Chapter 3 governance, and *nobody* owns the
whole.

What the Foundation operates is not a gate but a **memory**: a curated
search index, and an append-only transparency log in the checksum-
database tradition — tamper-evidence without permission-granting. Both
are SHOULD, not MUST, and deliberately so: sealed environments trust
manifest pins, not network services, so the index can burn down
tomorrow and not a single validation anywhere changes its answer.
What *is* normative is the semver contract — minors
backward-compatible, breaking changes as new major lines with
deprecation lifecycles — because deterministic composition (Chapter
13's pin resolution) is arithmetic only if publishers keep that
promise. The honest ledger entry: semver policing is social work, and
the risk register carries it as such. The transparency log makes
violations *visible*; making them *rare* is community hygiene, the
same as it is in every package ecosystem that works.

## 15.3 The standard library and the NIST arrangement

Somebody must steward the shared floor: the stdlib facets and their
schemas, the code systems (the modality lattice, deviation states,
mapping relationships per IR 8477/OLIR — whose curation the risk
register names as standing work — duration units, confidence grades),
the DSSE attestation profile, the transit projection and its
transit-safe schema subset, and the reference rendering templates.
That is the Foundation's estate, released with the same semver
discipline it asks of everyone.

Inside that estate sits the arrangement that made the whole
architecture politically survivable: the **Canonical Reference
Facet**. SP 800-53's document conventions, assessment objectives, and
ODP practices live in a facet NIST owns and maintains — shipped by
default in every stdlib bundle, first among equals in visibility — 
*under exactly the same rules as every other authority's facet*. The
sentence to remember: **800-53 is the standard library, not the
constitution.** NIST keeps the out-of-the-box primacy its content has
earned; what ends is the structural privilege that let one framework's
conventions constrain every other framework's documents — the privilege
whose measured cost was Chapter 1's dispute class and a national
catalog flattened into props. Both sides of that trade are stated
plainly because both are real; the launch-optics risk is in the
register, not under the rug.

One governance seat is left **deliberately empty**, and honesty
requires the sign on the door: rendering-template *accreditation* —
who certifies that a template renders faithfully — is an open problem.
The architecture made divergence *detectable* (templates named,
pinned, hashed; attestations binding them); who *blesses* them is
unowned, with pins-plus-publisher-reputation as the interim practice.
A governance chapter that lists no unsolved problems is marketing.

## 15.4 Changing the rules: the anti-#2118 machine

The dispute that opened this book had a signature pathology: a
constraint rejecting legitimate content, whose rationale — by the
maintainers' own discussion — nobody could state, sitting immovable
because the change process was heavier than the workaround. The whole
governance design here is the negation of that sentence, in three
mechanisms.

**Everything closed is versioned.** Primitives, tailoring operations,
selection predicates, code systems — all are *closed sets by design*
and *versioned sets by process*. The escape path from any genuine gap
is a **version, never a workaround**: propose the ninth operation,
don't smuggle it through a facet; propose the modality nuance, don't
overload prose. Closure is what keeps weekend validators possible;
versioning is what keeps closure from becoming a cage.

**Every rule carries its why.** Machine id, human rationale, failure
message — and the rationale *prints on failure*. A proposed rule that
cannot name what it prevents is rejectable on its face; an existing
rule whose rationale has rotted is deletable by the same standard.
The two-a.m. engineer reads the reason in the error output; the
standards meeting reads the same reason in the proposal. Nobody ever
again archaeologizes an issue thread to learn why a constraint
exists.

**Evidence in, corpus first, implementations follow.** A change
proposal leads with counts, not vibes — the census method as
governance culture ("three authorities encode this independently" is
an argument; "it would be elegant" is not). Because the test suite
*is* the specification, a change is concretely a set of new golden
cases plus a semver decision; both reference implementations must go
green before release. And the ecology Chapter 12 built on purpose —
validators cheap enough that many exist — is itself a governance
control: no single implementation's convenience can veto or
constitute the standard again.

> **Don't** extend by workaround what the process can version.
> Chapter 1 measured the three coping strategies — violate, flatten,
> route around — that authorities adopt when the change path costs
> more than the detour: an open dispute, a 12,059-prop shadow
> vocabulary, a national program's exit. This process exists to
> invert that price; use it, and the counts stay on your side.

## 15.5 Coexistence and the sunset

For years, both worlds run. The posture is the engine's: the Semantic
Core is the source of truth; valid OSCAL 1.x is *generated* for every
regulator that requires it (Chapter 14's dual-running rules apply —
one authoritative direction, flattening declared, never dual-edited).
The name avoids "2.0" on purpose — announcing a successor freezes the
very adoption wave the RFC-0024 deadlines are driving, and this
project has no interest in an Osborne moment against its own future
users. The upstream on-ramps are cited as they actually stand:
framework-owned external constraints and core-constraint
externalization are live paths today; the namespace-scoped part
proposals are closed pull requests — documented design positions,
evidence of the need, not routes.

The dual window ends at a **declared sunset trigger** — not a date but
a measurable state: authorities authoring natively at framework scale,
Portable implementations in multiple languages, the conformance corpus
green across them. The v0.6 executable gate is deliberately the first
milestone of exactly that chain: full-corpus converters with computed
coverage, executable schemas, the weekend-validator harness with its
numbers finally measured. At the trigger, the kernel becomes the
ecosystem's source of truth and 1.x export becomes a legacy service
with a deprecation lifecycle of its own — the same discipline this
book demands of every facet, applied to the transition itself.

And the realpolitik, recorded here as it is in the specification —
without endorsement, because it needs none: the current federal policy
admits to its approved-formats list any public-domain format that five
or more certified providers agree to maintain. That clause is a door
that swings both ways. It is the mechanism by which an architecture
like this one becomes an approved format without anyone's permission —
and equally the mechanism by which the incumbent is replaced by
something worse if its second act does not do what this book
describes. The deadline environment is nobody's rhetoric; it is the
publishing schedule.

## 15.6 Where this leaves you

Chapter 1 opened with your format decision and a deadline. Fifteen
chapters later, the decision has vocabulary, and each chair has a
first move that costs a day, not a quarter.

If you publish a framework: write the prefix constitution, mint one
set, and re-encode ten requirements — the Australian playbook says
your annotations will mostly just die, and the census says that is
the architecture working. If you build tools: clone the corpus and
take the weekend — the ecology needs your validator precisely so that
no one validator is ever the law again. If you buy or assess: ask the
receipt questions from §15.1 and Chapter 13, and treat every claim
without corpus verdicts as the datasheet it is. If you run a program:
write "Portable" where your policy says "approved format," and let
the tiers do the enforcement your prose never could.

The book's method is its last advice: **when in doubt, count.** This
architecture was not designed so much as *derived* — from three
governments on three continents who, under different constraints and
without coordination, kept building the same model: typed modality,
cheap membership, honest deadlines, aliases for everyone, weakness on
the record. Two of them discovered it independently. The standard's
job — this book's job — was only ever to write down what the field
had already decided, carefully enough that the third discovery can be
a shared one.

The appendices carry the reference tables; Chapter 12's margins and
Appendix E wait, honestly empty, for the v0.6 numbers. Everything
else is in your hands — which is, per the census, exactly where it
was all along.

---

*End of Part Five. Appendices A–G follow as reference material.*
