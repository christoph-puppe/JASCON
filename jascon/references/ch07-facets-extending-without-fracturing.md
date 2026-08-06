# The JASCON Handbook
## Part Two — Authoring Content
# Chapter 7 — Facets: Extending Without Fracturing

**Audience:** framework authorities [A] with semantics of their own —
which, per the census, is most of you. Tool implementers get the
consumption side in Chapter 13; this chapter is the publisher's seat.
**Companions:** Specification v0.5 — D10, D12, D3 (pinning), D15
(capability rows); stdlib catalog in Appendix D of this book.

---

## 7.0 The task

You are in the German seat now. Your framework carries meaning the
kernel does not know: a security-level taxonomy, an effort rating,
thematic tags, documentation duties. The old world's answer was the one
Chapter 1 costed — **12,059 namespace-qualified props** whose
"vocabulary" was a set of CSV files behind mutable links, validated by
nothing, drifting silently between releases.

Today's task is to publish that same semantics *properly*: decide where
each piece belongs on the extension map, then write, schema, declare,
and publish a real framework facet — `gspp-taxonomy@1` — end to end.
By the close, three thousand props become one descriptor plus typed
payloads, and drift becomes a validation error.

## 7.1 The map: five homes and a graveyard

Every candidate piece of "extra" data answers five questions, in order.
Most never reach question three — that is the graveyard, and it is the
best destination on the map.

**1. Is it imitating a kernel mechanism?** Membership, ordering,
history, aliases, clause structure, modality, parameters, deadlines —
if your datum is any of these wearing a costume, its home is *nothing*:
use the kernel and delete the datum. Across three authorities, **over
70 % of all counted prop instances** ended here, and the Australian
catalog — after Chapter 5's migration — needs *zero* facets at all. The
graveyard is not a consolation prize; it is the architecture working.

**2. Is it already in the standard library?** Eight registered facets
ship with the core, each priced by census evidence: statement grammar
(subject/action/object decomposition), security objectives (C-I-A
ratings and threat refs), terminology (glossaries with aliases),
reporting obligations, effectivity windows, assessment criteria
(required artifacts, key tests, control mappings), system context, and
assurance levels. If your concept matches one, *use it* — a shared
schema every tool already understands beats a private twin every time.

**3. Is it framework semantics with an interoperability claim?** Your
taxonomy, your rating scales, your domain codes — things consumers of
*your* catalog should be able to validate and, where declared, compute
on. This is **framework-facet** country, this chapter's main road.

**4. Is it internal or experimental, with no interoperability claim?**
Then `private:` — preserved untouched, validated never, and **invisible
to every compliance computation by definition**. The honest scratchpad,
priced honestly: an artifact carrying private facets caps below the
Portable tier.

**5. Is it rendering or bookkeeping chrome?** Then annotations — the
flat string map the American corpus legitimized with `web_name` and
`do_not_link`: excluded from semantic digests, strippable in transit,
structurally unable to smuggle meaning because nothing conformant can
see it.

> **Don't** publish vocabulary as side files a validator cannot read.
> Measured cost, one national corpus: 12,059 prop instances bound to
> CSV links, a defect class of 216 no tool could see, and vocabulary
> that changed between releases with nothing able to notice.

## 7.2 Anatomy of a facet: the descriptor

A facet is a name plus a contract. The name is an IRI rooted in *your*
domain — collision policy comes free with DNS — cited by objects at the
major line (`…@1`) and pinned in every bundle's manifest to an **exact
version and digest**. The contract is the descriptor you publish, and
it has four load-bearing parts.

**The schema** — plain JSON Schema 2020-12 for the payload. This is the
sentence that retires the CSV era: *your vocabulary file becomes a
schema*, and a wrong value becomes a validation error in every Portable
tool on earth instead of a private convention in yours.

**The documentation** — humans still deserve prose; the schema carries
the law, the docs carry the intent.

**Version and deprecation metadata** — the lifecycle discipline of
Chapter 3, applied to the vocabulary itself (§7.4).

**`modifies-semantics`** — the field that makes the whole system
decidable. You declare which computation classes your payload can
change: `assessment` (it alters what passing means), `tailoring` (it
alters how requirements may be modified), `selection` (it is a
legitimate basis for choosing requirements), `rendering` (it changes
normative presentation). Two defaults guard the edges, and both are
deliberate: a **registered** facet that *omits* the declaration is
treated as modifying **all four** classes — dangerous by default, the
burden of harmlessness on the publisher, enforced by fail-closed
everywhere. A **`private:`** facet carries `modifies-semantics: []` *by
definition* — smuggling compliance math into the scratchpad is
self-defeating, because conformant tools are required to look away.

And one payload convention is not yours to choose (normative since the
v0.6 cycle — D10 rev, backlog #7): **when your payload addresses
individual statements of its host Requirement, it MUST key them
`by-statement: { <statement-id>: <payload> }`**, using ids from the
host's own `statements[]`. A key naming no statement of the host is a
validation error — checkable by every Portable tool with zero
knowledge of your facet, which is the point: 1,015 statements'
payloads across six facets already align on this shape, and a second
producer free to invent its own keying would fracture per-clause
alignment for every consumer downstream. Addressing needs the pattern
cannot express (ranges, statement pairs) belong *inside* your payload
schema, where your contract governs them.

## 7.3 Worked: `gspp-taxonomy@1`

The German taxonomy cluster, by the numbers: `sec_level` ×998,
`effort_level` ×998, `tags` ×468, `documentation` ×959, `practice` ×8 —
3,431 prop instances across two catalogs. Here is their replacement,
whole.

**The descriptor**, published at
`https://ns.bsi.bund.de/.well-known/oscal-facets/gspp-taxonomy/1.0.0/`:

```json
{ "id": "https://ns.bsi.bund.de/facet/gspp-taxonomy",
  "version": "1.0.0",
  "modifies-semantics": ["selection"],
  "schema": { "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object", "additionalProperties": false,
    "properties": {
      "sec-level":     { "enum": ["normal-sdt", "erhoeht-sdt"] },
      "effort":        { "type": "integer", "minimum": 1, "maximum": 5 },
      "tags":          { "type": "array", "items": {"type": "string"} },
      "documentation": { "type": "array",
                         "items": {"enum": ["konfigurationshistorie", "…"]} } } } }
```

**The declaration, reasoned.** Why `["selection"]` and nothing else?
Because the security level is precisely what German baselines select by
— an elevated-protection tailoring picks requirements *via* this facet,
so a tool that does not understand it must not pretend to perform that
selection. But the facet changes nothing about how a requirement is
assessed, tailored in value, or rendered — so Portable tools that have
never heard of BSI may still validate, resolve, render, and tailor
these catalogs freely, stopping only at the one operation where
ignorance would mean error. That is declaration craft in one example:
**as narrow as honesty allows** (§7.5 returns to why).

**The payload**, on the requirement you have carried since Chapter 2:

```json
"facets": {
  "https://ns.bsi.bund.de/facet/gspp-taxonomy@1": {
    "sec-level": "normal-sdt", "effort": 2,
    "tags": ["produktbeschreibung", "cryptography", "zero-trust"] } }
```

**The before/after ledger.** 3,431 props → one descriptor plus typed
payloads. `tags` is an *array* — the corpus's comma-joined strings
("Produktbeschreibung, Cryptography, Zero Trust" as one value, split by
convention and corrupted by the first comma-bearing tag) are now
unwritable, because the schema says array and the schema is enforced.
And the silent drift Chapter 1 flagged — `label` and `practice` props
appearing in one release and vanishing in the next with nothing able to
notice — is structurally over: the vocabulary *is* the schema, the
schema is versioned and digest-pinned, and a payload against the wrong
vocabulary fails in every Portable tool on earth.

> **Don't** pack multiple values into one delimited string. Measured:
> the corpus's `tags` props carried comma-joined lists that any
> comma-bearing value would silently corrupt — an array field costs
> nothing and makes the failure unwritable.

## 7.4 Publishing, pinning, and the federation

Where does your facet *live*, and who approves it? The answers are "at
your own well-known path" and "nobody" — and both are lessons paid for
in full.

**Self-publication, no gate.** You place the descriptor under
`https://<your-domain>/.well-known/oscal-facets/<name>/<version>/`;
existence plus validity makes it a registered facet. The ecosystem's
index — a curated search surface with an append-only transparency log —
helps the world *find* it and notice tampering, but it is an index, not
a checkpoint. The anti-model is historical and specific: the old
world's central extension registry — the canonical definitions of the
flagship program's own vocabulary — required petitioning to enter and
then **vanished when its repository was deleted**, recoverable only
from a fork. A registry you must petition is a registry authors route
around; a registry that can vanish takes your vocabulary with it.
Federation removes both failure modes: your vocabulary lives where your
identity lives, under your Chapter 3 governance.

**Trust is the pin, not the URL.** Availability of your `.well-known`
path is a courtesy for bundle assemblers; it is never a validation
dependency. Every bundle's manifest pins your facet at an exact version
*and digest*, and sealed-mode consumers verify against the pin,
offline. Your server can be down for a week and not a single validation
anywhere changes its answer.

**Semver with teeth.** The registry policy makes minor versions
**normatively backward-compatible**: within a major line, you may add —
new optional fields, new enum values — never remove or repurpose.
Breaking changes mean a new major line and a deprecation lifecycle on
the old one (announce, overlap, retire — the Chapter 3 discipline,
applied to vocabulary). This is also what makes bundle composition
deterministic: two bundles pinning different minors of your `@1`
resolve to the highest pinned minor with both payload sets re-validated
— possible only because you kept the compatibility promise.

## 7.5 What fail-closed means for *your* consumers

Flip the chair. You have declared; now a thousand tools you will never
meet consume your catalog. The rule that governs them — and therefore
shapes your declaration — exists because of a three-tools story the
specification's reviewers told with precision: in the old model, one
tool *preserved* an unknown prop, one *interpreted* it by guesswork,
one *refused* the document — and all three claimed conformance, which
is another way of saying conformance claimed nothing about meaning.

Here the states are decidable. A **Portable** tool must validate your
payloads against your pinned schema and must *preserve* facets it does
not understand — unknown-but-registered content is safe cargo, never
silently dropped. Whether a tool may *compute* on your facet is a
declared capability, facet by facet — and the hard rule is the one that
protects you: any computation of a class your facet declares itself to
modify, performed by a tool that has not declared understanding, **must
halt with an explained error**. Never guess, never silently ignore.

Three publisher consequences follow, and they are the craft of this
chapter's craft:

**Declare narrowly — every unnecessary class is a stop sign.** If you
had declared `gspp-taxonomy` as modifying `assessment`, every
assessment run over a German catalog by a non-German tool would halt.
Selection-only means the ecosystem flows everywhere except the one
place ignorance is dangerous.

**But never narrower than true.** Your declaration is digest-pinned
alongside your schema; a facet that quietly changes assessment while
declaring itself presentation-grade is auditable publisher misconduct,
with your name on the pin.

**Expect visible halts, and call them the feature.** Your consumers
will sometimes see a tool stop where the old world would have muddled
through. That stop is a correct answer arriving early — the alternative
was three tools, three meanings, one conformance claim. (The UX of
turning halts into actionable messages is Chapter 13's problem, and the
specification's rationale-on-failure rule already did half the work:
every halt prints *why*.)

And the scratchpad, from the consumer's side: `private:` payloads ride
along untouched and unconsulted. If a vendor tells you their compliance
logic lives in a private facet, you now know exactly what that means —
it lives outside the contract, by definition, visibly.

## 7.6 The map, folded for your pocket

*Is it a kernel mechanism in costume? Delete it — 70 % odds say yes.
Is it in the stdlib? Reuse it. Framework semantics with an interop
claim? Publish a facet: schema, narrow-but-true declaration, well-known
path, semver with teeth. No interop claim? `private:`, and it caps your
tier. Chrome? Annotation, and it is invisible.*

One kind of extension deliberately never appeared on this map:
statements *about other people's frameworks*. "Our control AC-2
intersects ISO's 5.16" is not a facet on either object — it belongs to
neither endpoint, carries its own author, its own confidence, its own
lifecycle, and often contradicts somebody else's opinion about the same
pair. Cross-framework claims are first-class objects with first-class
provenance — the mapping economy that SCF built a business on and NIST
just built an eighth document model for. That object, and how to
publish a crosswalk corpus with it, is Chapter 8.
