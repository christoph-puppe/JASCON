# The JASCON Handbook
## Part Two — Authoring Content
# Chapter 5 — Sets, Hierarchy, and Baselines

**Audience:** framework authorities [A]. Tool implementers get the
resolution side of this material in Chapters 6 and 12.
**Companions:** Specification v0.5 — D13, D21, Appendix A
(RequirementSet shape).

---

## 5.0 The task

Your requirements exist (Chapters 3–4). Now you owe your ecosystem three
things that, in the old world, took three different mechanisms and still
didn't work: the **taxonomy** of your framework — its functions, layers,
domains, chapters; the **display order** auditors and readers expect; and
your **baselines** — classification levels, maturity tiers, applicability
stages, the subsets people actually implement.

This chapter's claim is that all three are one mechanism, and its proof
is a funeral: by §5.3 the largest single annotation block in the census —
Australia's 5,301-entry membership matrix — will be dead, replaced by
eight small objects the publisher was effectively maintaining anyway.

## 5.1 The 5,301-entry confession

Open the Australian ISM catalog and count what its props are for. Of
8,958 total, **5,301** are one field — `applicability` — recording, per
control, which classification markers it belongs to (the catalog's codes:
NC, OS, P, S, TS), with **256** more for Essential Eight maturity levels.
Fifty-nine percent of the entire extension surface of a national
framework is a hand-inlined membership matrix.

Now the confession part: ASD *also* publishes that same information as
eight separate profile documents — one per classification level and
maturity tier. A disciplined national agency maintains identical facts
twice, in two shapes, forever, because in the old world the profile
mechanism was too expensive for consumers to use as the single source, so
the matrix moved into the catalog where tools could at least read it as
strings.

This is not an Australian eccentricity; it is the census's largest
pattern, visible on all three continents in three disguises. The American
corpus inlines its class membership as `subsets` applicability blocks and
per-class baseline lists (`rev5_controls_list`) inside the rules
themselves. And the German program performed the most expensive variant
of all — **membership by duplication**: two catalogs sharing control-ID
strings, each carrying its own copy of overlapping requirements, which
under the old identity model made the pair structurally uncombinable.
Three authorities, three workarounds, one missing mechanism.

> **Don't** encode membership as annotation or duplication. Measured
> cost: 5,557 membership props in one catalog, per-class lists threaded
> through another corpus, and two German catalogs that could not be
> safely combined at all — every instance a hand-maintained imitation of
> a set.

## 5.2 One mechanism: the RequirementSet

The replacement is almost embarrassingly small:

```json
{ "id": "https://ns.cyber.gov.au/ism/set/secret-baseline",
  "version": "2026.06.18",
  "title": "SECRET baseline",
  "members": [
    { "ref": "https://ns.cyber.gov.au/ism/req/ISM-1234", "sequence": 10 },
    { "ref": "https://ns.cyber.gov.au/ism/req/ISM-1401", "sequence": 20 } ] }
```

A set has an identity like everything else, a title, and members — and a
member may reference a requirement **or another set**. That single
allowance is the entire hierarchy story, and it does three jobs at once.

**Taxonomy is nested sets.** Your framework's structure — whatever its
native vocabulary — is sets containing sets containing requirements:

```
set: csf/function/protect
  └ set: csf/category/pr-aa   (Identity Mgmt, Authn, Access Control)
      └ req: csf/req/pr-aa-01
      └ req: csf/req/pr-aa-02
```

CSF's Functions → Categories → Subcategories, SCF's 34 domains, CIS's
Controls → Safeguards, ISO 27002's themes, the German layer-and-module
architecture — all of them are this shape and nothing but this shape.
Crucially, the nesting happens *between sets*, never inside requirements:
requirements do not contain requirements, ever. The 347 German
pseudo-controls became statements (Chapter 4); structural grouping became
sets; and the old world's group/part nesting — the attractor that
produced the #2118 dispute — has no surface left to land on.

**Order is `sequence`.** An ascending integer, unique within one members
list, meaning *presentation order and nothing else* — the specification
is deliberately blunt that no further semantics ride on it. With that
one field, the Australian catalog's 1,150 `sort-id` props evaporate.

**Membership is just… membership.** A requirement may appear in any
number of sets — five classification baselines, a maturity tier, a
thematic view — as references, never copies. Many-to-many, finally
stated honestly, with the German duplication disaster as the standing
reminder of the alternative: a requirement shared by two publications is
*one object referenced by two sets* (Chapter 3, §3.2), not a name
collision waiting for a merge strategy that cannot exist.

## 5.3 Worked migration: killing the matrix

Here is the entire pipeline that retires Australia's matrix, and by
extension yours.

**Step 1 — mint the sets.** Eight objects under the authority prefix:
five classification baselines (one per marker the catalog uses) and
three Essential Eight maturity sets. Each gets an id, a version, a
lifecycle — they are publication artifacts now, with all of Chapter 3's
machinery: a baseline can be deprecated, superseded, given lineage.

**Step 2 — invert the matrix.** For every control, for every
`applicability` value it carries, emit one member entry in the matching
set; carry the old `sort-id` into `sequence`. This is a twenty-line
transformation in any language, run once.

**Step 3 — delete.** The 5,301 applicability props, the 256 maturity
props, and the 1,150 sort-ids — 5,807 annotations in all — are gone from
the catalog, replaced by eight small set objects. Nothing was lost;
every fact moved to the mechanism that owns it.

**Step 4 — notice what you no longer maintain.** The eight sets *are*
the eight profiles ASD already publishes. Matrix and profiles were two
projections of one truth; now the truth has exactly one home, and both
old projections are renderings of it. And the catalog itself? After this
migration it is the object Chapter 2 opened with: pure kernel, **zero
facets, zero props** — the cleanest national framework in the corpus, by
subtraction alone.

## 5.4 Sets versus Tailorings: the decision line

One boundary question decides everything in this part of the
architecture, so put it on the wall:

> **A Set answers *who belongs*. A Tailoring answers *what changes for
> those who belong*.**

Pure selection — a subset with unmodified requirements — is a Set, full
stop. Australia's classification baselines qualify; so do CIS's
Implementation Groups (IG1 ⊂ IG2 ⊂ IG3 as three sets, or nested ones);
so does every thematic reading view you will ever publish. The moment
values change per tier — different deadlines, strengthened modality,
altered parameters — you have crossed into Tailoring territory, and the
two mechanisms *compose*: the Tailoring selects **from** a set and then
applies its identity-addressed operations.

The American corpus is the perfect worked contrast because it needs
both. Its `subsets` applicability blocks and per-class baseline lists
are pure membership — Sets. Its `varies_by_class` blocks — Class A gets
a six-hour incident deadline where Class D gets a business day — are
modifications — four Tailorings, each selecting from the 20x set and
issuing a handful of `set-parameter` and `set-modality` operations. One
last preview of Chapter 6, because authors worry about it here:
**exclusion is selection, not weakening.** Building a baseline by
excluding requirements needs no Deviations — a rule the specification
defends explicitly, because the alternative (a deviation record per
exclusion) would bury exactly the baselines this chapter just liberated
under thousands of ceremonial entries.

| You are publishing… | Mechanism |
|---|---|
| Chapter structure, domains, reading order | nested Sets + `sequence` |
| Classification / applicability / maturity tiers (unmodified) | Sets |
| Tiers whose requirements change per tier | Sets + Tailorings selecting from them |
| A one-off customer or system scoping | a Tailoring (Chapter 6) |

## 5.5 Designing your set landscape

Five working rules, learned from the corpus's scars.

**Sets are publications.** Give them the same identity discipline as
requirements — governed ids, versions, lifecycle, lineage. "The SECRET
baseline, 2026.06.18" is a citable, deprecable, supersedable thing, and
your auditors will cite it.

**Separate taxonomy sets from baseline sets.** Your chapter structure
and your compliance tiers have different owners, different change
cadences, and different consumers; entangling them means every editorial
reshuffle looks like a compliance change. Two subtrees under the prefix
(`…/set/tax/…`, `…/set/baseline/…`) keeps the blast radii apart.

**References, never copies.** The n:m freedom is the point; the German
duplication corpse is the cost of forgetting it.

**Leave sequence gaps.** Number 10, 20, 30 — insertions then cost one
entry, not a renumbering cascade across a thousand members. (The
specification demands only ascending-and-unique; the gaps are craft.)

**Draft what isn't ready.** An announced-but-unfinished baseline is a
set with `lifecycle: draft` — visible, uncitable, honest.

## 5.6 Where this leaves you

Your framework now has structure without nesting-in-requirements, order
without sort-props, and baselines without matrices — and the Australian
worked example shows the end state is not merely cleaner but *smaller*:
5,807 annotations became eight objects the publisher was already
maintaining in disguise.

What sets cannot do — by design — is change a requirement for a tier.
The American classes need their six-hour deadline; your elevated
protection level needs its SOLLTE hardened to MUSS. That is the
Tailoring layer: identity-addressed operations, the per-operation
weakening rules, the honest line between selection and softening, and a
resolution algorithm short enough to memorize. Chapter 6.
