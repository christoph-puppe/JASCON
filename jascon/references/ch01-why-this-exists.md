# The JASCON Handbook
## Part One — Orientation
# Chapter 1 — Why This Exists

**Audience:** everyone — framework authorities, tool implementers, and the
people who have to sign what the tools produce.
**Companions:** Specification v0.5 (Part I), Decision Rationale Register.
**Figures:** corpus versions of July 2026 (ISM v2026.06.18 · BSI 2026-07-03
/ 2026-04-23 · FedRAMP CR26 v2026.07.14.01); re-verify at print per the
evidence rule in §1.6.

---

## 1.0 The task

You are holding a format decision, and it probably has a deadline attached.

Perhaps you are a cloud provider staring at FedRAMP's requirement to
deliver machine-readable authorization data by September 30, 2026, with a
final deadline a year later and loss of certification as the sanction.
Perhaps you are a national agency — in Bonn, Canberra, or anywhere the
regulatory wave of NIS2, DORA, and their siblings is landing — deciding how
to publish a framework so that a thousand downstream organizations can
consume it with software instead of interns. Perhaps you build the GRC
tooling those organizations will buy, and you need to know which format
will still exist in five years. Or perhaps you are the person who signs the
authorization at the end, and you would simply like the documents you sign
to mean what the machines checked.

The obvious answers are: use OSCAL, the NIST standard built for exactly
this; or, if that looks too heavy, publish your own JSON. This chapter is
the evidence file on both answers. It is not an opinion piece — nearly
every claim in it is a number somebody in this project counted in a
published artifact, and the few that are not are labeled. By the end you
will know why the standard built for this job received zero organic
submissions from its flagship program in a year of record volume, why the
world's most carefully authored OSCAL catalog contains 216 defects that no
validator on the planet can see, why the newest authoritative compliance
format in the United States is not OSCAL at all — and why those three facts
have the same root cause, which is fixable.

## 1.1 The verdict nobody planned

The Open Security Controls Assessment Language was not a research toy. From
its earliest milestones it was co-piloted with FedRAMP — the US federal
cloud authorization program — as the flagship consumer; FedRAMP announced
OSCAL 1.0.0 in 2021 as the shared path to standardized, machine-readable
authorization packages. If any organization on earth was going to adopt
OSCAL at scale, it was this one. A decade of investment, templates,
validation rules, and official baselines followed.

In January 2026, FedRAMP published RFC-0024, proposing to *mandate*
machine-readable authorization data. Buried in its justification is the
most damning adoption statistic ever printed about a data standard by its
own sponsor: in 2025, FedRAMP processed more than one hundred Rev5
authorizations — **and not a single submission used OSCAL**. None of the
20x Phase One pilot participants used it for their machine-readable
materials either. Read that again with the context in mind: this is the
program the standard was built with, in the year machine-readability
became the program's central theme.

RFC-0024's remedy is just as instructive as its statistic. It does not
abandon OSCAL; it places it *on probation*. OSCAL appears on the list of
approved formats conditionally — contingent on the project being
maintained and responsive to industry input — while the same document
invites industry to build competing formats and provides the mechanism:
any public-domain format that five or more certified cloud providers agree
to maintain can join the approved list. The deadlines are real
(September 30, 2026 initial; September 30, 2027 final), the sanction is
real, and the exit door is written into the policy.

Meanwhile, FedRAMP's own new content — the Consolidated Rules for 2026,
in force since July 4, 2026 — ships as bespoke JSON with its own schema,
in a repository that declares itself the source of truth, with the
human-readable website explicitly demoted to reference material. The
flagship did not merely fail to adopt the standard. It routed around it,
and then wrote the routing into policy.

A standard can survive criticism. It cannot survive its founding customer
publishing, in the same six months, proof that nobody used it and a legal
mechanism for replacing it. Understanding *why* this happened is the
purpose of the rest of this chapter — because the cause is not what most
postmortems assume, and it is not unfixable.

## 1.2 What the catalogs actually contain

Opinions about standards are cheap; catalogs are data. In mid-2026 this
project inventoried, field by field and prop by prop, the current
authoritative machine-readable publications of three governments on three
continents — the complete population of authorities publishing at national
framework scale. Everything this book teaches was derived from what those
three artifacts actually contain, so meet them properly.

| | **ASD ISM** (Australia) | **BSI Grundschutz++ / MS-TLS** (Germany) | **FedRAMP CR26** (United States) |
|---|---|---|---|
| Format | OSCAL 1.1.3 catalog | OSCAL 1.1.3 catalogs | Bespoke JSON + own schema |
| Size | 1,150 controls | 998 + 17 controls (incl. 347 + 10 nested) | 246 rules · 46 KSIs · 75 terms · 79 overlays |
| Extension load | 8,958 props (7,759 namespaced) | 13,315 props (12,059 namespaced) | zero props — typed fields instead |
| Signature pattern | membership as annotation | grammar as annotation | green-field convergence |

**Australia** is the disciplined one. The ISM's namespace is a properly
versioned URI; its custom vocabulary is tiny — six prop names in total.
And yet 59 % of all its props are one thing: an `applicability` matrix,
5,301 entries recording which classification levels each control belongs
to, plus 256 more for Essential Eight maturity — the same information ASD
*also* publishes as eight separate profile documents. A national agency is
hand-maintaining the identical membership data twice, in two shapes,
because consuming the standard's own profile mechanism is more expensive
than inlining a matrix into the catalog. Hold that thought; it is the
single largest pattern in the census and it is not an Australian quirk.

**Germany** is the ambitious one — and the cautionary one. Grundschutz++
is, to this project's knowledge, the only national framework being
*authored natively* in OSCAL rather than converted into it after the fact.
Its authors wanted more than prose: every one of its 1,015 statements
carries a machine-readable decomposition — modal verb, action, object,
target categories — a genuine requirements grammar. OSCAL's core had no
home for any of it, so all of it lives in **12,059 namespace-qualified
props** whose "schema" is a set of CSV files behind mutable repository
links that no validator can read.

The consequence is the most important measurement in this book. The
catalogs contain **216 pseudo-placeholders** — strings like
`{{einem anerkannten Standard}}` sitting inside prop values, imitating the
standard's parameter-insertion syntax in a place where that syntax has no
meaning, several of them contradicting the actual parameter the adjacent
prose correctly references. Two machine-readable representations of the
same requirement, silently diverging, in documents that **every OSCAL
validator on earth certifies as flawless**. Nobody was careless here; the
authors are professionals and the tooling all reported green. The standard
simply has no organ that can see meaning. Schema-valid and semantically
hollow are, in OSCAL 1.x, fully compatible states — and 216 counted
instances prove it is not a theoretical risk.

> **Don't** publish vocabulary as human-readable side files and call it a
> namespace. Measured cost: 12,059 prop instances validated by nothing,
> 216 silent defects, and — as we will see — vocabulary that drifts
> between releases with no tool able to notice.

**The United States** is the control group, and an accidental gift to this
project. When FedRAMP built CR26 on a green field in 2026 — no Metaschema,
no part constraints, no props mechanism, nothing to conform to — its
authors faced the same modeling questions the Germans faced, and answered
them with typed fields: a `force` field for binding strength (its
distribution across the corpus: MUST 189, SHOULD 84, MAY 39, MUST NOT 11,
SHOULD NOT 5), typed timeframes with units including business days, inline
per-class variants, alias lists on every glossary term, a change-history
array on every object. Set the German prop names beside the American field
names and the correspondence is nearly one-to-one: `modal_verb` ↔ `force`;
`target_object_categories` ↔ `affects`; BSI's revision churn ↔ CR26's
`updated[]`. Two authoring teams, two constraint regimes, no coordination
— **one target model**, discovered twice. In evolutionary biology this is
called convergence, and it is the strongest kind of evidence a data
architect ever gets: it tells you what the domain itself demands, as
opposed to what any committee prefers.

## 1.3 The two-layer paradox

So why did a well-funded, well-intentioned standard end up with an
Australian membership matrix, a German shadow grammar, and an American
defection? The postmortems usually say "too complex," which is true but
not precise. The precise diagnosis is that OSCAL 1.x is rigid and loose
*at the same time, on the wrong layers* — and every pathology in the
census flows from one side of that paradox or the other.

**Too rigid where frameworks legitimately differ.** The core schemas
encode the document conventions of one framework — NIST SP 800-53's
part grammar of statements, guidance, objectives — as constraints binding
*everyone*. The tracker shows what happens on contact: when the Cloud
Security Alliance published its Cloud Controls Matrix with nested items
under guidance parts (a perfectly reasonable structure for its content),
validation rejected it, producing issue #2118 — a dispute over a
constraint that contradicts NIST's own tutorial and whose rationale, by
the maintainers' own discussion, nobody can state. Its sibling, #2112,
records that even parts in *other namespaces* get forced into NIST's
structure. And the German catalog's shape is the same story told in
negative space: all 998 controls are perfectly, identically flat — one
statement, one guidance, nothing nested, nothing namespaced — because
flat-plus-props was the only shape that validated. The fossil record of a
constraint is the structure of everything that survived it.

**Too contractless where meaning actually lives.** The extension
mechanism — props with a namespace attribute — has no contract at all.
The `ns` value is an unvalidated string; nothing requires a vocabulary to
be machine-readable, versioned, or even stable; and the official doctrine,
stated plainly by the standard's own maintainers when the German props
were raised upstream, is that prop semantics are the authors' choice and
interoperability is an issue only "if it is a concern for the authors."
The core takes formal responsibility for *parseability* and formally
disclaims *meaning*. But meaning is the entire value proposition of
compliance data. A GRC platform that can parse your catalog and
understand none of it has automated the photocopier.

Hold the two failures side by side and the tragedy is visible: the
standard is strict about the one thing frameworks genuinely need freedom
in (their document and requirement structure) and permissive about the
one thing that must be disciplined for interoperability to exist (the
semantics of extensions). Both settings are exactly backwards — and, as
Chapter 2 will show, the entire JASCON architecture is little more
than flipping both switches and then removing everything that existed
only to compensate for their being backwards.

## 1.4 Three coping strategies, three prices

Put real authorities in front of that paradox and they do one of three
things. The census caught all three in the act.

**Violate.** CSA structured its guidance the way its content demanded and
failed validation — the honest collision, paid for in an open dispute
(#2118) that has consumed maintainer attention for months and left the
CCM's official artifact failing the official validator.

**Flatten.** BSI kept its documents validator-shaped and moved the truth
into props — the compliant workaround, paid for in a 12,059-instance
shadow vocabulary that no generic tool can interpret, a defect class no
validator can detect, and (a finding from this project's own scans)
vocabulary that drifted between catalog releases with nothing able to
flag it.

**Route around.** FedRAMP built its own format — the exit, paid for by
everyone else: the community now maintains converters to drag CR26 back
toward the standard ecosystem, every tool vendor implements one more
bespoke schema, and the precedent stands in policy for the next regulator
to follow. If each of Europe's incoming regimes — NIS2 technical
guidance, DORA, the CRA, EUCS — makes the same rational choice, the
2030 landscape is a dozen incompatible national JSON dialects, and the
entire premise of machine-readable compliance (write once, satisfy many)
dies not from opposition but from defaults.

Three strategies, three prices, one root cause. And one more bill worth
itemizing, because it falls on *you*: the tooling economics. A standard
this heavy — a bespoke meta-language, seven-then-eight document models,
a profile-resolution algebra intricate enough to need its own
specification — supports essentially one full validator lineage. Every
constraint dispute bottlenecks on one team; every consumer inherits one
implementation's interpretations; and the surrounding artifacts rot: the
authoritative registry of FedRAMP's own OSCAL extensions was deleted
along with its repository in 2025, and this project could recover it only
from a fork. When even the standard's flagship extensions cannot keep a
stable address, "just link to the definition" is not an interoperability
strategy. It is a prayer.

## 1.5 What would have to be true instead

Reverse every measured failure and you get, almost mechanically, a
requirements list. It is worth stating here in plain language, because
Chapters 2 through 15 are nothing but its systematic execution:

Identity would have to be global, so two catalogs can never collide and
composition never needs merge heuristics (the German twin-catalog
problem). Membership and variants would have to be so cheap to express
that no agency ever again hand-maintains a 5,301-entry matrix beside its
own profiles (the Australian problem). The things every framework
demonstrably needs — binding strength, clause structure, typed
parameters, deadlines, secondary identifiers, revision history — would
have to live in the core, because the census shows them converging across
three continents (the American proof). Everything framework-specific
would still need a home, but one with a machine-readable contract, so
that "valid" finally implies "checkable meaning" and the 216-defect class
becomes *unrepresentable* rather than undetectable. The document
conventions of any one framework — including NIST's — would have to
leave the core and bind only their own content. And all of it would have
to be implementable by a competent developer in days, in any language,
offline, because the alternative is the monoculture we just costed —
a *designed-for* claim until the gate-4 measurement lands, and labeled
so here (P9 erratum).

That list has a name in this book: the **north star**, four tests every
design decision must pass — *simpler; closer to the measured needs of the
customers; no more props; less need for custom meta-language extensions
or bespoke JSON.* The Decision Rationale Register scores all
twenty-two architectural decisions against exactly those four tests
(presented there as three scoring axes — the two complexity tests fold
into one), and
the specification documents every alternative that failed them, including
the reviewer suggestions this project rejected and why.

## 1.6 The rules this book runs on

Three working rules govern every page that follows; they are the same
rules that governed the design, and you should hold the book to them.

**Evidence tiers, always labeled.** Every claim is *measured* (counted in
a published artifact — the census numbers, the RFC-0024 statistic),
*designed-for* (the architecture provably provides for it, executable
proof pending — for example, full round-trip coverage of all three
corpora, gated on the v0.6 converter run), or *hypothesized* (clearly
flagged, rare). Where this book's own earlier drafts overclaimed, the
corrections are on the record — including a public erratum culture: when
this project's first published scan undercounted the German corpus (651
controls instead of 998, because nested controls were missed), the
correction shipped with the same prominence as the original claim.

**Concepts enter through the corpus.** No mechanism is introduced
abstractly. Statements arrive via the 347 German pseudo-controls that
exist only because clauses had no home; the modality lattice arrives via
the American `force` distribution and the German *DARF NUR*; mappings
arrive via the crosswalk economies of SCF and CSA. If a concept cannot be
motivated by something an authority actually shipped, it did not survive
into the specification, and it will not appear here.

**Every "don't" names its corpse.** Prohibitions in this book are never
etiquette. Each one cites the measured failure it prevents, with the
number attached — the way §1.2's box carries its 12,059 and its 216. A
rule that cannot name what it prevents is a rule this project would
delete, and the specification's change process is built so that such
rules *can* be deleted: every constraint ships with a recorded rationale
that prints on failure, because the single most corrosive sentence in the
old world's issue tracker was "nobody can say why this rule exists."

That is why this exists. Not because OSCAL 1.x was a bad idea — it was
the right idea with its complexity budget spent on the wrong layer — but
because three governments' own artifacts, read closely, describe both the
failure and its remedy with a precision no design committee could match.
The next chapter puts the remedy in front of you whole: nine shallow
object types, one serialization, and an Australian control encoded so
simply it needs nothing else — the entire core, in about an hour.

---

*Production note: all figures in this chapter re-verify against source
artifacts at print time (corpus versions in the header; RFC-0024 and
issue-tracker states as of July 2026). The census methodology and raw
counts are published alongside the specification.*
