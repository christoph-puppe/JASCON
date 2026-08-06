# The JASCON Handbook
## Part Two — Authoring Content
# Chapter 8 — Mappings and Crosswalks

**Audience:** framework authorities [A] and every organization whose
product or audit practice *is* the crosswalk — mapping vendors,
certification bodies, multi-framework enterprises. Consumers learn what
a trustworthy mapping claim looks like as a side effect.
**Companions:** Specification v0.5 — D20, D16, worked example III.4;
relationship and confidence code systems in the stdlib (Appendix C/D of
this book).

---

## 8.0 The task

Two seats, one task. In the first sits a mapping vendor — the SCF
economy, whose entire product is a graph relating 1,500+ controls to
200 + frameworks, shipped today as spreadsheets because nothing better
had a first-class home. In the second sits a national authority — say
the German one — wanting to publish an official Grundschutz++ ↔
ISO 27002 crosswalk so that every auditor in the country can compute
dual-certification coverage instead of re-deriving it in Excel, client
by client.

Both seats have the same job today: turn "our control | their control |
comment" columns into **first-class objects** — with a typed
relationship, clause-level scope, a confidence grade, an author, and a
lifecycle — and publish them as a corpus somebody else's tooling can
actually reason over. On the way we settle why this is the ninth kernel
type rather than a facet or a link list, and what each relationship
code lets a consumer *compute*.

## 8.1 Why a ninth type exists: the ownership argument

Ask the simplest possible question about a crosswalk claim: *whom does
"AC-2 intersects ISO 5.16" belong to?*

Not to AC-2 — NIST didn't say it. Not to 5.16 — ISO didn't either. It
belongs to whoever asserted it: a third party with its own name, its
own date, its own methodology, its own appetite for being wrong. That
one observation kills both cheap encodings. A *facet* attaches to an
object — but this claim has no rightful host object, and parking it on
either endpoint misattributes authorship to an authority that never
spoke. A *relation entry* is worse, and the census caught the failure
in the wild: the American corpus carries **263** KSI→800-53 links as
bare lowercase identifier strings — no relationship type, no version
pin, no author, no confidence — consumable only on faith. And the old
standard's own answer, shipped March 2026, proved the demand while
demonstrating the anti-pattern one more time: an entire eighth
*document model* for mappings, with the full uuid/metadata/revisions
scaffolding and props throughout.

The JASCON's answer is the ownership argument taken literally: a
crosswalk claim is an **object** — nine flat fields with the same
identity, versioning, and lifecycle discipline as everything else in
Chapter 3. Nine fields replace a document model; a spreadsheet economy
gets a schema.

> **Don't** ship mappings as bare identifier lists. Measured: 263 such
> links in one authoritative corpus — untyped, unversioned,
> unattributed — meaning no tool can distinguish "equivalent" from
> "vaguely related," no consumer can tell whose judgment they are
> trusting, and no revision of either endpoint triggers any review.

## 8.2 The object, field by field

```json
{ "id": "https://ns.bsi.bund.de/map/gspp-iso27002/2026-1/KONF.14.1--5.x",
  "version": "2026-1",
  "lifecycle": "active",
  "source-ref": "https://ns.bsi.bund.de/gspp/req/KONF.14.1",
  "source-scope": ["statement:s1"],
  "target-ref": "https://ns.iso.example/27002/req/5.x",
  "relationship": "intersects",
  "direction": "source-to-target",
  "confidence": "reviewed",
  "rationale": "Both require transport encryption; the ISO clause additionally covers …",
  "provenance": { "author-ref": "https://ns.bsi.bund.de/party/gspp-team",
                  "date": "2026-07-01" },
  "evidence-refs": ["https://ns.bsi.bund.de/doc/mapping-analysis-2026-1"] }
```

**`source-ref` / `target-ref`** — ordinary global references, and here
the pinning advice of Chapter 6 hardens into doctrine: **pin exact
versions.** A mapping is a claim about two *texts as they stood*; an
unpinned mapping is a claim about moving targets. When an endpoint is
later revised, the Chapter 3 machinery does exactly the right thing —
the old version remains addressable, the `replaces` lineage surfaces in
tooling, and your review process (§8.5) decides whether the claim
survives the new text. Nothing auto-substitutes; nothing silently rots.

**`source-scope` / `target-scope`** — clause precision, the payoff of
Chapter 4's statement identifiers. "AC-2's clause (a) intersects 5.16;
clause (b) does not" is finally *sayable*, and half the fights in
mapping review meetings are exactly that sentence. Omit the scope and
the claim covers the whole requirement — a legitimate, coarser
statement, not a default to reach for out of laziness.

**`relationship`** — one code from the stdlib system (§8.3). This field
is the difference between a hyperlink and an assertion.

**`direction`** — the reading direction of the assessment
(`source-to-target` in the worked examples). Symmetric codes (`equal`,
`intersects`, `conflicts`) don't need it to be meaningful; the
containment codes do, and stating it explicitly costs one line and ends
one whole class of review-meeting confusion.

**`confidence`** — a small stdlib grade (the worked corpus uses
`reviewed`); its craft is honesty over marketing, and §8.4 shows why a
modest grade with real provenance beats a bold one without.

**`rationale`, `provenance`, `evidence-refs`** — the why, the who-when,
and the receipts: the analysis document, the workshop minutes, the
methodology note. These three fields are what make a mapping *citable*
in an audit rather than merely present in a database.

**`lifecycle`** — mappings age. A target revision, a methodology
update, a withdrawn endpoint: `deprecated` and `withdrawn` mean exactly
what Chapter 3 taught, and a crosswalk corpus without a lifecycle
policy is a spreadsheet with better formatting.

## 8.3 Relationship semantics as compliance arithmetic

The six codes are not taxonomy for its own sake; each one licenses a
different **computation** in a gap analysis. Read the table as "I have
satisfied the *target* — what does this mapping let me conclude about
the *source*?"

| Code | Plain meaning (source → target) | If target is satisfied… | Gap-analysis effect |
|---|---|---|---|
| `equal` | mutual satisfaction | source is satisfied | full credit, both directions |
| `subset-of` | everything source demands, target also demands | source is satisfied | full credit toward source; *not* the reverse |
| `superset-of` | source demands more than target | source is **not** established | partial credit; residual gap on source's extras |
| `intersects` | real overlap, neither contains the other | the overlap is covered | partial credit; enumerate the residue in `rationale` |
| `supports` | contributes, no coverage claim | evidence, not satisfaction | counts as supporting evidence only |
| `conflicts` | the demands contradict | — | architecture alarm: satisfying both needs deliberate design (think retention duty versus deletion duty) |

Two failure patterns to design against, both endemic in the spreadsheet
era. The first is **marketing `equal`** — the temptation to grade every
plausible pair as equivalent because equivalence sells certifications.
The arithmetic column is the antidote: `equal` is a machine-consumable
promise that satisfying either side fully discharges the other, and an
auditor armed with this table will hold you to it; honest `intersects`
with a crisp residue rationale is worth more than brave `equal` with a
retraction. The second is **containment direction slips**: fix them
with the reading rule that `A subset-of B` means *A's demands are
contained in B's* — so B-compliance carries A, never the other way. Say
the sentence out loud before you commit the code; it is cheaper than
the correction release.

## 8.4 Contradiction is a feature

SCF grades a pair `intersects`; a certification body, mapping the same
pair for its own scheme, grades it `subset-of`. In the spreadsheet era
this was a fight about whose cell wins. Here it is two objects — two
ids, two provenances, two confidence grades, both `active` — and the
disagreement is *data*.

That is deliberate, and it is the federation logic of Chapter 7
mirrored: there is no central referee for crosswalk truth, because a
referee would be a gate, and gates are where this ecosystem goes to die
(Chapter 7's deleted-registry funeral applies verbatim). Consumers
already choose whose *catalog* to trust; now they choose whose
*crosswalk* — filtering by `provenance.author-ref` and weighting by
`confidence` is a query, not a committee. Your job as a publisher is
simply to make your objects worth choosing: pinned endpoints, honest
codes, receipts attached. The market for judgment stays open; only the
anonymity is gone.

## 8.5 Worked: publishing the German↔ISO corpus

The whole pipeline, in five moves.

**Scope and pin.** Decide the two sides precisely: which Grundschutz++
set (the elevated baseline? everything active?) against which ISO 27002
edition — and record both as exact-version references in the corpus
README and in every object. A crosswalk of unpinned editions is an
opinion about fog.

**Mint under your prefix.** One subtree per corpus,
`…/map/gspp-iso27002/<release>/…`, with speaking object names
(`KONF.14.1--5.x`). The Chapter 3 constitution covers who may mint here
and how releases are cut; a crosswalk release is a publication like any
baseline.

**One claim, one object.** Resist the row-with-five-targets habit:
five relationships from one source are five objects, each independently
gradable, deprecable, and citable. Use statement scope wherever the
truth is clause-shaped — this is where the corpus earns its precision
premium over every spreadsheet that came before it.

**Package as a bundle.** The corpus *is* the package: a content
manifest listing every mapping object with both digests, endpoints
referenced (not copied), evidence documents included or referenced.
There is no special "mapping collection" container to invent — and none
should be improvised out of RequirementSets, whose members are
requirements and sets, not claims. The manifest is the collection;
discovery is its job.

**Publish the aging policy.** State, in the corpus documentation, what
happens when an endpoint revision appears in its `replaces` lineage:
review window, who re-adjudicates, whether affected mappings drop to
`deprecated` pending review or stand until re-graded. This paragraph is
the difference between a living crosswalk and 2019's spreadsheet with a
2026 filename — and it is the paragraph auditors will read first.

## 8.6 Importing the old world

Two legacy shapes will land on your desk, and both import cleanly at
Chapter 2's migration levels.

**The 1.2.2 Mapping Model** maps *natively*: its collections unfold
into objects, its relationship terms translate into the stdlib codes,
its provenance metadata fills `provenance` — a mechanical conversion,
one legacy document model retired per corpus.

**Bare link lists** — the 263-style corpus — import honestly rather
than flatteringly: relationship `supports` (the weakest true claim),
provenance naming the original publisher, a modest confidence, and a
`rationale` noting that the source carried no typed relationship. That
is not pedantry; it is the arithmetic table protecting your consumers
from computing full credit out of what was only ever a hyperlink.

---

With mappings, Part Two is complete: you can now author requirements,
structure and baseline them, tailor them on the record, extend them
under contract, and relate them to the rest of the world with
provenance attached. Part Three crosses the aisle to the people who
must *live* under all of it — systems built from other people's
systems, responsibility split clause by clause, inheritance across
authorization boundaries. Chapter 9 opens with the sentence that
reorganized the whole model: *your system is my component* — and walks
a full SaaS-on-PaaS-on-IaaS chain to show what the boundary rule
actually checks.
