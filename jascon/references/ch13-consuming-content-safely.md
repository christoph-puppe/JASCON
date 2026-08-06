# The JASCON Handbook
## Part Four — Building Tools
# Chapter 13 — Consuming Content Safely

**Audience:** tool implementers [T] turning Chapter 12's validator into
a product people live with; consumer-side sidebars [C] mark what
buyers and assessors should demand of any tool they are sold.
**Companions:** Specification v0.5 — D10, D15, D3 (composition), D7
(template rule); Chapter 11 for the verification states this chapter
treats as everyday inputs.

---

## 13.0 The task

Your validator says *no* correctly. Monday says hello: a German
catalog carrying `gspp-taxonomy`, an American-shaped bundle full of
`assessment-criteria`, a vendor package with `private:` payloads
throughout, and two supplier bundles that pin different minor versions
of the same facet. Real consumption is the art between two failure
modes — computing what you don't understand (the old world's silent
guessing) and refusing what you could safely carry (paranoia as a
service). The task: an ingestion-to-output pipeline that never
guesses, never blocks needlessly, and converts every hard stop into a
next step somebody can actually take.

## 13.1 The permission ladder

Everything in this chapter hangs off one ladder — what you may *do*
with each species of content you hold:

| Content | validate | preserve & forward | compute class C | render normatively |
|---|---|---|---|---|
| Kernel objects | always | always | per tier | per tier |
| Registered facet, **understood** | against pinned schema | always | yes | yes |
| Registered facet, **unknown** | against pinned schema | **always** | **gate: only if its declared classes miss C** | gate likewise |
| `private:` payloads | never | always | never (by definition — and never abort over them) | never |
| Annotations | n/a | strippable | invisible to all semantics | chrome only |

Two rungs deserve their sentences. *Unknown-but-registered is safe
cargo*: you validate it against the pinned schema, you carry it
untouched, you hand it on — what you may not do is perform a
computation the facet declares itself to modify. And *private is
defined harmless*: `modifies-semantics: []` by definition, so you
ignore-and-preserve, never halt — smuggled logic in the scratchpad
punishes itself because you are *required* to look away.

The pocket version: **you may always carry what you cannot compute;
you may never compute what you cannot account for.**

## 13.2 The fail-closed gate in production

Chapter 12 built the gate as one choke-point function. Production is
about *where it sits* and *what it says*.

**Gate at the verb, not at the noun.** The rule fires when a
*computation of class C* meets an undeclared-understood facet whose
declaration includes C — not when a bundle is opened. A package
carrying ten unknown `selection`-modifying facets opens, validates,
digests, forwards, and displays its raw structure without a murmur; it
stops at the moment someone *selects*. Lazy gating is what keeps
fail-closed from becoming fail-annoying — the ladder's generous rungs
stay generous, and the stop arrives exactly where ignorance would have
become error.

**A gate message has three mandatory ingredients**, and the
specification's rationale-on-failure rule already supplies the spine:

```
HALT tailoring-resolution (class: selection)
  blocked by: https://ns.bsi.bund.de/facet/gspp-taxonomy@1 (pinned 1.0.0)
              declared modifies-semantics: [selection]
  this tool understands: [ …list… ]  — not this facet
  ways forward:
    · enable support: declare the facet in this tool's capabilities
    · narrow scope:   re-run selection excluding subjects carrying it
    · ask the source: descriptor at manifest path schemas/gspp-taxonomy-1.0.0.json
```

What was attempted (class and operation); what blocks it (facet ids,
versions, where their descriptors live *inside the bundle*); which
doors remain open. A halt with those three is a work item; a halt
without them is a support ticket.

> **Don't** downgrade the gate to a warning. The measured precedent is
> the whole reason this machinery exists: in the old model one tool
> preserved the unknown, one interpreted it by guesswork, one refused
> the file — all claiming conformance. A warning-then-proceed is the
> guessing tool wearing a seatbelt sticker; the gate's value is
> precisely that "conformant" stopped being compatible with "made it
> up."

**[C] sidebar:** ask any vendor to show you their gate message for a
facet they don't support. If the answer is a stack trace, a silent
result, or "we just skip those," you have learned which of the three
old tools you are being sold.

## 13.3 Living with the three species

**Registered and understood.** Compute freely — and treat schema
violations as what they now are: the *publisher's* defect, surfaced by
the contract. Report upstream; do not hand-patch payloads locally
(your fork of their meaning is the old shadow-vocabulary game at
retail scale). A digest mismatch on a pinned schema is not a retry
condition; it is an integrity alarm — the pin is the trust anchor, and
something is wrong with the supply chain, not your parser.

**Registered and unknown.** Cargo rules: emit byte-faithful, never
reorder, never normalize (Chapter 12's parser discipline, now an
operating policy). And be *transparent* about the cargo in your UI —
"2 facets not understood by this tool: gspp-taxonomy@1 (selection)" —
because a consumer deciding whether to enable support deserves the
inventory. Forwarding unknown content silently is fine; *holding* it
silently invites the day someone assumes your green checkmark covered
it.

**`private:` and annotations.** Mark private payloads visibly as
*outside the contract* — a badge, not a warning. If a workflow in your
organization turns out to *depend* on a vendor's private payloads,
that dependency is the smell of contract-bypass: the vendor is doing
registry-worthy semantics without the registry, and the fix is a
conversation about publishing a real facet, not deeper integration
with the scratchpad. Annotations never appear in compliance diffs and
never in digest expectations — which is also why an arriving bundle
whose packaging digest changed but whose semantic digests hold
(Chapter 11's Semantic Match) is a *report*, not a defect: somebody
stripped chrome in transit, exactly as the rules allow.

## 13.4 When two bundles meet: pins, composition, refusal

The supplier case: Bundle A pins `assessment-criteria` at 1.2.0,
Bundle B at 1.4.0, and your job is one combined workspace.

The registry's semver promise is what makes this decidable — minor
versions within a major line are *normatively* backward-compatible —
so composition resolves to the **highest pinned minor**, then
**re-validates both payload sets** against it. Both green: proceed,
and record the decision. Anything breaks: stop with a report naming
both pins, both manifests, and the failing payloads — never a silent
pick, never "newest wins" by reflex. Two adjacent cases complete the
matrix: two *exact* versions of one major line inside a *single*
bundle is that bundle's validation error — a publisher problem, not a
composition puzzle; and a *major*-line conflict (A pins `@1`, B pins
`@2`) has no automatic bridge, because different majors are different
vocabularies — consume separately, or wait for the publisher's
migration path.

Make the **composition report** a standard artifact of every merge:
which pins met, what was chosen, what was re-validated, what refused.
It is ten lines of output and the difference between an auditable
workspace and archaeology.

> **Don't** resolve pin conflicts by fetching "the latest" from the
> network. The pin is the trust anchor precisely because published
> locations rot — the census's own registry corpse made the case — and
> sealed-mode consumers have no network to ask. Composition is decided
> by the manifests in hand and the semver promise, offline, or it is
> refused with a report.

## 13.5 Rendering without crossing the line

Rendering is where consumption touches paper, and two disciplines keep
it inside the contract.

**Templates are pinned citizens.** A normative rendering names its
template by version and digest and its renderer by name — Chapter 11
made them part of the trusted computing base, and your product should
treat template selection with the same gravity as schema selection.
Use the provenance map when present: *click the paragraph, land on the
statement* is the cheapest assessor delight in the whole architecture.

**Chrome stays chrome.** Annotations may influence only non-normative
presentation — the corpus-legitimated cases are the pattern: a
`web_name` becomes a URL slug, a `do_not_link` suppresses a hyperlink.
A template that interpolates an annotation into requirement text is
**non-conformant**, full stop — and the reason is load-bearing rather
than aesthetic: the whole bi-modal verification story of Chapter 11
rests on the guarantee that a packaging-only delta *cannot* have
altered normative content. Renderers that respect the line are what
make that guarantee true. And when a *rendering*-modifying facet you
don't understand sits on the subject: the gate applies to normative
rendering like any other class — while the raw structural view, ladder
rung one, remains always available. Show the data; decline to *style
it authoritatively*.

## 13.6 The operating checklist

Respect the ladder — carry what you can't compute, never compute what
you can't account for. Gate at the verb; every halt ships its three
ingredients. Cargo travels byte-faithful and visibly inventoried.
`private:` gets a badge, and dependencies on it get a conversation.
Pin conflicts resolve by semver and re-validation or refuse with a
report — never by network, never by reflex. Templates are pinned;
chrome stays chrome; Semantic Match is information, not injury.

One species of input remains that none of this handles: content that
was never a Core bundle at all. The world you actually inherit is
OSCAL 1.x catalogs and SSPs, CR26's bespoke JSON, CSV vocabularies,
and mapping spreadsheets — and "safely" there means knowing exactly
which guarantee each converted element carries: mapped natively,
carried in a compatibility facet, or preserved opaquely with no
semantic claim. That three-level honesty, and the playbooks per source
format, are Chapter 14: Migration.
