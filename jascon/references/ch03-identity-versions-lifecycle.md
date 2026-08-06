# The JASCON Handbook
## Part Two — Authoring Content
# Chapter 3 — Identity, Versions, and the Life of an Object

**Audience:** framework authorities [A] — the people who mint identifiers
others will depend on. Tool implementers should skim §3.1 and §3.5 for the
mental model.
**Companions:** Specification v0.5 — D2, D3, D15, Appendix A (common
fields).

---

## 3.0 The task

Your catalog goes live in a few weeks. Before the first requirement ID
exists — before, ideally, the first draft control is written — five
governance decisions must be made, because every one of them is nearly
impossible to change after downstream implementations, findings, and
attestations start referencing your objects:

the **prefix** you will mint under; the **ID scheme** below it; your
**version and history policy**; your **alias policy** for the second and
third naming schemes your organization already has (it has them — every
measured authority does); and the **publication duties** you are signing
up for at the Authority tier.

This chapter walks the five decisions in order, each with a worked
positive example from the corpus and at least one measured corpse. The
short version, if you read nothing else: identity is a promise, not a
pointer — and the census contains the full price list for confusing the
two.

## 3.1 The address you will still stand behind in 2040

Every object's `id` is a URI under a DNS-rooted prefix your organization
controls. Two properties of that URI do all the work, and both are easy
to misread:

**It is compared as an opaque string.** Two references are the same
object if and only if their id strings are identical (or bridged by a
`canonical-alias` — §3.5). No normalization, no case-folding cleverness,
no path semantics.

**It is never resolved during validation.** Sealed, zero-network
validation is a Core conformance requirement; content travels in bundles
whose manifest maps every id to bytes and digests. The URI's job is to be
*unique and yours* — resolvability is a courtesy for humans and
bundle-assembly tooling, never a dependency.

The positive example is Australian. The ISM's namespace is
`https://cyber.gov.au/ns/ism/oscal/3.0`: the agency's own long-lived
domain, a dedicated `/ns/` path signaling "this is an identifier space,
not a download directory," and an explicit version segment. Whatever else
one might redesign about the ISM's catalog, its authors understood that a
namespace is infrastructure. Copy the shape:

```
https://<your-durable-domain>/ns/<framework>/…
```

The negative examples are the census's two loudest findings. The German
catalogs use, as their `ns` values, GitHub file paths of the form
`…/tree/main/Dokumentation/namespaces/<file>.csv` — mutable branch
locators pointing at spreadsheet files. Every repository reorganization,
rename, or branch policy change silently breaks the identifier layer
under **12,059 prop instances**. And the cautionary tale that should hang
over every prefix decision: the authoritative registry of FedRAMP's own
OSCAL extensions — the canonical definition of a national program's
vocabulary — was **deleted along with its repository** in 2025. This
project recovered it only from a surviving fork. When the flagship's own
definitions cannot keep a stable address, "just link to it" is exposed
for what it is.

> **Don't** use a locator as an identifier. Measured cost: 12,059
> instances bound to mutable file paths in one national corpus, and one
> national extension registry unreachable at its published address. An
> id must outlive the server, the repository, the org chart, and — per
> §3.5 — even the domain.

Two practical rules complete the decision. First, choose a domain with
institutional, not project, lifespan: the agency's primary domain, not a
product site, a vendor, or a code-hosting namespace. Second, write the
**prefix constitution** — a one-page internal document naming who may
mint below the prefix, how path segments are allocated, and what the
change process is. It sounds bureaucratic; it is the cheapest insurance
in this entire book, and it is implicitly required by the Authority-tier
duties you will meet in §3.7.

## 3.2 Minting below the prefix

Below the prefix, structure your id paths by *meaning*, not by storage:
`…/ns/gspp/req/KONF.14.1`, `…/ns/ism/set/secret-baseline`,
`…/ns/cr26/tailoring/class-a`. Human-readable, framework-native ids
(KONF.14.1, ISM-1234, IEC-CSO-IIR) are the right default — they are what
your community already speaks, and the alias mechanism (§3.4) exists
precisely so legacy UUIDs need not pollute the canonical layer.

One discipline becomes *yours* the moment identity goes global: **no
string may be minted twice under your prefix.** The old world learned
this the expensive way. The German program published two catalogs —
Grundschutz++ and the TLS Mindeststandard — whose controls share
identical ID strings; under 1.x's instance-scoped identity that was
legal, and it made the two catalogs structurally uncombinable, with no
merge strategy that didn't lose or corrupt data. Under global identity
the same mistake would be worse — identical strings would *claim to be
the same object* — which is why the fix is organizational, not
technical: allocate disjoint subtrees per publication
(`…/gspp/req/…` vs. `…/mstls/req/…`) in the prefix constitution, and let
your build pipeline enforce uniqueness across everything you have ever
published. If two publications genuinely share a requirement, that is
not a name collision — that is *one object*, referenced by both sets,
which is exactly what the architecture wants you to say.

## 3.3 Versions, digests, and the death of "Jun-26"

Every object carries a `version` string. The specification does not
impose a scheme; it imposes a *policy obligation*: pick one, document it
in the prefix constitution, and never mix. The corpus shows three sane
choices in the wild — CR26's dotted date-serial (`2026.07.14.01`), ISM's
release date (`v2026.06.18`), the German ISO date — and any of them
works, because addressability, not arithmetic, is the point: `id@version`
names an immutable thing, forever.

What must die is history-as-annotation. The Australian catalog carries
`revision` and `updated` props on 1,101 controls each — **2,202
instances** — with the dates encoded as strings like `"Jun-26"`: no day,
no timezone, no machine meaning, hand-maintained beside the very
`version` metadata that should own the job. The American corpus does the
richer version of the same thing, an `updated[]{date, comment}` array on
every object. In JASCON, both patterns collapse into the
identity layer: each change is a new addressable version; the bundle's
content manifest carries the release-notes narrative; `replaces` records
(§3.5) carry structural lineage. Your authoring pipeline generates all of
it — nobody hand-edits a month-string ever again.

> **Don't** encode change history as object annotations. Measured cost:
> 2,202 prop instances in one national catalog, with dates a machine
> cannot even parse — duplicating information the identity layer holds
> natively.

Publication at the Authority tier also means shipping **two digests per
object** in your content manifest: the `package-digest` over the
delivered bytes, and the `semantic-digest` over the canonicalized object
minus annotations. For this chapter's purposes you need only the
authoring consequences — your pipeline computes both, your JCS
implementation must pass the published test vectors (including the
empty-array-omission cases), and `decimal` values must be written as
canonical strings. Why there are two domains, and what each proves to a
verifier, is Chapter 11's story.

## 3.4 Labels, aliases, and everyone's second name

Three fields, three jobs, one rule.

**`id`** is for machines and is forever. **`label`** is the human display
identifier — `KONF.14.1`, `ISM-1234` — the thing auditors say out loud.
**`aliases[] {scheme, value}`** absorbs every *other* naming scheme your
organization maintains, and the census says you maintain more than you
think: the German corpus carries **1,219** `alt-identifier` props
(internal UUIDs) plus a parallel `VER.x` numbering; the American glossary
carries **188** alias entries; the Australians keep legacy ISM numbers
beside new-style labels. Give each scheme a name and a home:

```json
"label": "KONF.14.1",
"aliases": [ {"scheme": "bsi-uuid", "value": "…-6219b9704724"},
             {"scheme": "sdt-ver",  "value": "VER.2"} ]
```

The one rule: **aliases are lookup keys, never reference targets.**
Every `ref` in every object — implementations, mappings, tailorings —
points at the canonical `id`. Tools may *find* by alias; they must
*cite* by id. Break this and you have rebuilt the alt-identifier prop
economy (1,407 combined instances across two authorities) with better
syntax.

## 3.5 Rebrands, revisions, splits: what may claim identity

This is the section to read twice, because it protects everyone
downstream of you, and because the distinction it draws was one of the
hardest-won corrections in the specification's review history.

Two mechanisms exist, with sharply different powers.

**`canonical-alias` asserts identity.** Use it for exactly one
situation: *the same content at a new address* — your agency rebrands,
the domain migrates, a path subtree moves. You publish records bridging
old URI to new; validators substitute freely and forever; nothing
downstream needs to change or even notice. This is how the 2040 promise
of §3.1 survives even a domain change: the *identifier* rots only if you
let the *equivalence record* lapse.

**`replaces` asserts lineage — and nothing more.** Use it whenever the
content changed: `revised`, `split-from`, `merged-into`, `renamed`. A
replaces record is history for humans and tooling to *surface*, never a
license to substitute. The reasoning is worth internalizing, because a
reviewer's first instinct — "supersedes means the new one stands in for
the old" — was exactly the design error the specification had to walk
back: a revision may be narrower, broader, split in two, or merged with
a neighbor. Auto-substituting it would silently corrupt every existing
Implementation edge (which attested to the *old* text), every Finding,
every Attestation (whose digests bind the old object), every Mapping
(whose relationship was assessed against the old semantics), and every
Tailoring (whose operations address the old statement ids). The
downstream owner must *decide* to move — your job is to make the
decision visible, not to make it for them.

A worked pair, both from plausible German futures. The rebrand:
`/ns/gspp/…` migrates to `/ns/grundschutz/…` — publish canonical-alias
records for every object; done; nobody downstream lifts a finger. The
revision: KONF.14.1 is split into two successor requirements — mint two
new objects carrying `replaces: [{ref: …KONF.14.1, relationship:
"split-from"}]`, set the old object's lifecycle to `deprecated` with the
successors discoverable, and let every implementer migrate deliberately,
on their own audit clock.

The heuristic, suitable for printing above the release manager's desk:

> **Would every existing Implementation, Finding, and Attestation remain
> exactly as true against the new object as against the old?**
> Yes, byte-for-byte-meaning — `canonical-alias`. Any hesitation at all —
> `replaces`, with the honest relationship code.

## 3.6 Lifecycle: four states, and whom each protects

`draft → active → deprecated → withdrawn`, with one meaning each:
**draft** may change without lineage records and must not be cited by
anything claiming conformance; **active** is the promise in force;
**deprecated** remains fully consumable — implementations against it stay
valid — but tools surface the warning and the `replaces` trail to
successors; **withdrawn** exists for historical reference only, and new
references to it fail validation. Deprecation windows are policy you owe
your ecosystem (put the default in the prefix constitution); the state
machine is how a thousand downstream organizations learn about your
changes from their tooling instead of from your newsletter.

## 3.7 The Authority tier: what publishing obligates you to

The conformance matrix (Specification D15) reserves a set of duties for
publishers, and this chapter has now met most of them. As a checklist,
with the honest cost attached:

**Stable ids under a governed prefix** — the constitution document, an
afternoon to write, priceless thereafter. **Alias and lineage records on
every reorganization** — generated by your pipeline the moment §3.5's
heuristic is answered. **Both digests for every object, JCS-conformant**
— a one-time tooling investment against published test vectors.
**Facet schemas at your `.well-known` location with a deprecation
lifecycle** — Chapter 7's subject; budget for it if you extend.
**Calendar references wherever you publish calendar-period durations** —
if, like the American corpus, your deadlines count business days, you owe
your consumers the calendar that makes them computable; Chapter 4 takes
this up with the parameter algebra.

It is more than OSCAL 1.x ever asked of a publisher — and that is the
point stated plainly. 1.x asked nothing, and the measured result was
identifier spaces made of spreadsheet links, history in month-strings,
and a national registry that evaporated. The Authority tier's duties are
the exact price of the promise this architecture makes on your behalf:
that a consumer on an air-gapped network, holding nothing but your
bundle, can trust every reference in it — offline, byte-verified, and
still in 2040.

Next: Chapter 4 — writing the requirements themselves. The modality
lattice finally gives *DARF NUR* a machine-checkable meaning, the
American force-field distribution shows you what a healthy modality mix
looks like, and the 347 German pseudo-controls demonstrate exactly when
one requirement should become several statements.
