# The JASCON Handbook
## Part Five — Adoption
# Chapter 14 — Migration Playbooks

**Audience:** [A][T] — authorities carrying legacy corpora and the tool
teams building their converters. Consumers should read §14.1 and §14.6
to know what a converted bundle's labels entitle them to believe.
**Companions:** Specification v0.5 — D16, D19; the v0.6 gate (IV.5),
whose full-corpus converters are this chapter run at scale.

---

## 14.0 The task

You hold inventory. Perhaps a 1.x estate — catalogs, profiles, an SSP
landscape, POA&Ms with years of history. Perhaps CR26-shaped bespoke
JSON. Perhaps the honest worst case: CSV vocabularies and mapping
spreadsheets that were never a standard at all. The task is to move it
— **with bookkeeping**. Migration in this architecture is bookkeeping
first and transformation second: every source element receives one of
three guarantee labels, and a conforming converter emits three
artifacts, not one — the converted bundle, a **coverage report**
(every source field's destination, every unmapped value, percentages
computed by code), and the per-element **level declaration**. A
migration whose losses are enumerated is an engineering act; one whose
losses are vibes is a liability transfer.

## 14.1 The three guarantees — and why "lossless" died

The specification's own history disciplines this section. An early
draft claimed "lossless" migration and "total" export; hostile review
demonstrated both were unprovable and the second currently false, and
the correction is on the record — the same erratum culture that
republished the census counts. What replaced the adjective is a
three-level vocabulary, declared per element:

**Level 1 — native mapping.** The element becomes a normal target
concept: a control becomes a Requirement, membership becomes a Set,
`force` becomes modality. Full semantics, full tooling, no asterisk.

**Level 2 — compatibility mapping.** The element is preserved in a
versioned compatibility facet (the `oscal-1x-prop`-style holding pen):
schema-carried, digest-pinned, visible — but its *meaning* awaits
adjudication. A promise to decide, not a decision.

**Level 3 — opaque preservation.** The canonical source payload rides
along with **no semantic claim whatsoever** — exotic part structures,
process-flow graphs, anything the model deliberately does not speak.
Present, hashable, honest about being cargo.

The honest summary claim, verbatim from the specification:
*information-preserving for the supported corpus*, verified by a
round-trip conformance corpus against a **published equivalence
relation** — a defined relation, never a magic word (§14.7).

> **Don't** ship a converter without its coverage report. The failure
> this prevents is silent smoothing: this project's own first scan
> undercounted a national corpus (651 for 998) until nested controls
> were caught, and the same corpus carries 216 defective values that a
> "helpful" converter would either launder into false structure or
> drop without a trace. Unmapped and defective source values are
> *findings about the source* — they belong in a generated list, not
> in the void.

## 14.2 Playbook: OSCAL 1.x catalogs and profiles

**Controls.** Each becomes a Requirement; **nested controls become
statements** of their parent — the 347 German pseudo-controls convert
into what they always were, identified clauses (Chapter 4's split
heuristic applies where nesting was structural rather than clausal).
Statement parts feed `statements[].prose`, with ODP-style insertion
points analyzed into typed parameters — the fused-alternatives lesson
("TLS 1.3 *oder* …") means this step is analysis, not string
substitution. Guidance and objectives prose takes one of two Level-1
homes by a single rule: NIST-conventioned content (800-53's
statement/guidance/objective grammar) lands in the Canonical Reference
Facet where those conventions now live; framework-own narrative
becomes prose-only statements with `modality: "unspecified"` — 
first-class at Core, losing nothing it had.

**The identity block.** `label` props → kernel `label`;
`alt-identifier` (×1,219 in the German corpus alone) → `aliases[]`
with schemes; `sort-id` (×1,150 Australian) → `sequence`; groups →
nested Sets. This whole row is Level 1 and mechanical — Chapter 5's
§5.3 pipeline *is* the worked playbook, twenty lines of code and a
funeral.

**Props.** Run each prop name through Chapter 7's five-question map.
The census's standing odds: **over 70 %** are kernel imitations —
Level 1 into mechanics, no facet at all. Semantically real clusters go
Level 1 into stdlib or framework facets (grammar, security
objectives, taxonomy — Chapters 4 and 7 carry the worked German
cases). What resists adjudication goes Level 2 into the compatibility
facet — *visibly*, with §14.6's clock ticking. Level 3 is rarely
needed for props; it exists for structures, not values.

**Profiles.** `import` + selection becomes a Tailoring's `selects`
and `excludes`; `set-parameters` becomes `set-parameter` operations;
`alters` become `replace-prose` (with the intent flag honestly set —
a 1.x alter that changed meaning is `substantive`, and converting it
as `editorial` is forgery by migration) or `attach-facet`. One thing
has **no target**: merge strategies. Use-first, keep, combine — the
concepts do not exist, because identity collisions cannot. Where a
legacy profile's semantics genuinely depended on merge behavior,
resolve it *in the old world first* and migrate the resolved catalog;
importing an ambiguity is not preservation, it is contagion.

## 14.3 Playbook: SSPs, component definitions, assessments, POA&Ms

**The SSP** unbundles along Chapter 9's seams: system-characteristics
→ a Component with identified `authorizations[]` plus the
`system-context` facet (carrying, per the book's evidence rule, its
medium-confidence flag); implemented-requirements → Implementation
edges, with by-component granularity landing in `statement-refs` and
`responsibility`; leveraged-authorizations → `inherited-from` edges
whose `basis-ref` names the specific authorization id — the
conversion *forces* the question 1.x let slide ("inherited under
*which* authorization?"), and a source SSP that cannot answer it has
found a real gap, not a converter bug. **Component definitions**
become `capabilities[]` on vendor Components — the duplication axis
whose complexity drove a professional team's public retreat (PR #8)
simply ceases to exist as a second document. **Assessment plans and
results** become Assessment objects (methods via
`assessment-criteria`) and Findings; **POA&M items** become
`Finding.actions[]` with computable due dates; and the four
historical deviation-workflow props — false-positive,
operational-requirement, risk-adjustment, vendor-dependency, each
hand-carrying the identical state machine — convert one-to-one into
typed Deviations, their four names now values of one field. The
UUID-plumbing cluster (party-uuid, import-profile, attachment
hashes) dies into L0 references and the content manifest: Level 1 by
deletion.

## 14.4 Playbook: CR26 and other bespoke JSON

The American corpus converts almost by table lookup, because
Chapter 6 already worked the hard part: `force` → modality; `affects[]`
→ `obligated-parties[]`; timeframes → durations, split honestly into
elapsed and calendar (with the calendar reference becoming a
publication duty); `varies_by_class` and the `pain_timeframes`
matrices → one base Set plus four class Tailorings, by the matrix rule
(*rows become parameters, columns become Tailorings*); `subsets` and
per-class baseline lists → Sets; `updated[]` → L0 versions plus
manifest release notes; the FRD glossary → `terminology@1`;
notifications and required-information → `reporting-obligation@1`;
artifacts, key tests, examples, and the KSI shape →
`assessment-criteria@1`; `effective` windows → `effectivity@1`;
schema and legal references → typed links; `web_name` and
`do_not_link` → annotations; the 263 bare control links → Mapping
objects imported at honest strength (`supports`, provenance named,
per §8.6). Two entries are deliberate non-conversions: `flows[]` is
**Level 3 by declaration** — process graphs are linked diagram
resources, not requirement data — and anything else that resists is
Level 2 with a ticket, never a silent prop.

For bespoke formats that are *not* CR26, the meta-playbook is this
book's own method: run a **field census first** — every key path,
frequency, enum candidates — then adjudicate each field against the
convergence table's pattern rows (membership? modality? aliases? history?
deadlines?) before writing a line of converter. The census is the
converter's specification; everything else is typing.

## 14.5 Playbook: spreadsheets and shadow vocabularies

The CSV vocabulary behind a props estate converts by Chapter 7's
worked example: the value list becomes a facet schema, the schema
becomes the vocabulary, drift becomes a validation error — 3,431
German taxonomy props into one descriptor is the measured
before/after. Mapping spreadsheets convert by Chapter 8's §8.5–8.6:
one row, one Mapping object, honest relationship codes, and imported
link-lists graded `supports` rather than flattered into `equal`.

And the 216 pseudo-placeholders deserve their explicit converter
policy, because every option except one is a trap: repairing them
silently invents authorial intent; passing them through as prose
launders a defect into the new world; dropping them hides evidence.
The one correct behavior: **report them** — a coverage-report section
of defective source values, queued for the *authors*, because they
were always authoring defects that no tool had eyes to see. The
converter's job is to give them eyes, not amnesia.

## 14.6 The compatibility facet's half-life

Level 2 is a waiting room with a clock, and the clock is the point.
The compatibility facet exists so migration never blocks on
adjudicating every last prop — but a compatibility payload that
*stays* is just a prop with a registration number, and the smell is
the same. Two disciplines keep the room from becoming a residence:
publish the facet with **intended deprecation** in its descriptor
metadata from day one; and track **compatibility residue per
release** as a first-class migration KPI — the number should fall
toward zero, each line either graduating to a Level-1 home (a real
facet, a kernel field, the graveyard) or dying a documented death.
An authority's migration is *finished* when the residue is zero, not
when the converter first ran.

## 14.7 Round trips and dual running

For the transition years, the engine posture (Chapter 15 owns the
politics) means many of you will run dual: the Core as source of
truth, 1.x artifacts generated for regulators who still require them.
Three honesty rules make dual running survivable.

**Export flattens, and says so.** Kernel-native concepts degrade on
the way down: global identities and typed Deviations become props and
links — syntactically valid 1.x, semantically reduced; Mappings
alone export *natively*, into the 1.2.2 Mapping Model they
supersede. Consumers of your generated 1.x deserve the same level
labels your imports carry.

**Round-trip is a defined relation.** Up-convert, down-convert,
compare — against the *published equivalence relation*, verified by
the corpus at the v0.6 gate. Not byte identity, not "looks the
same": a relation you can read, with test cases you can run.

**Never dual-edit.** One direction is authoritative; the other is
generated. The moment both worlds accept edits, you have rebuilt the
duplicated-truth architecture whose measured cost — a professional
team's public retreat, a decade of sync props — opened this book.

> **Don't** edit generated artifacts. The failure this prevents is
> the oldest one in the census: two representations of one truth,
> drifting — the twin-catalog collision and the comp-def/SSP
> duplication were both this mistake wearing different clothes, and
> both required this architecture to un-make them.

---

Your estate now has a path: three labels, per-source playbooks, a
waiting room with a clock, and round trips you can test instead of
trust. What remains is the part no single organization controls — the
tiers a vendor may claim and what each claim entitles you to demand,
the registry and its transparency log, who stewards the standard
library, how primitives and operations evolve without re-growing a
committee bottleneck, and the sunset trigger that one day ends dual
running. That ecosystem contract — governance, conformance, and how
this architecture intends to coexist with, and eventually retire, the
world it came from — is Chapter 15, the last.
