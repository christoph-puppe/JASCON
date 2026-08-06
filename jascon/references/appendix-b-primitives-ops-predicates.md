# The JASCON Handbook
# Appendix B — Primitives, Operations, Predicates

**Purpose:** the complete computational vocabulary — eight primitives,
three predicates, eight tailoring operations — one entry each, in the
format the anti-#2118 rule demands: **signature, tier, semantics,
rationale (with its corpse), and the failure message that prints.**
Nothing here is illustrative filler: a rule that cannot name what it
prevents is a rule this project deletes, and this appendix is where
every rule names it.

**Conventions.** Rule ids shown as `[name]` pending the executable
schemas (gate item 2), where they gain stable machine ids. Failure
messages are templates: `<...>` marks interpolation. Tier column per
the D15 matrix: **all** = Core, Portable, Authority; **P+** = Portable
and above (Core carries the data passively, computes nothing).

---

## B.1 The eight primitives

### 1 · `references-resolve` — *all tiers*

**Signature:** (object graph, content manifest) → verdict per reference.
**Semantics:** every reference string in every object must land on a
manifest entry (id + version); sealed mode means the manifest is the
*only* resolver — no network, no guessing, no partial credit.
**Rationale:** the old world's reference layer was UUID plumbing that
tools generated and no human audited; dangling references were
discovered at consumption time, in someone else's pipeline. Here a
bundle that doesn't close doesn't validate.
**Failure:**
```
FAIL [references-resolve] <object-id>
  reference "<ref>" has no entry in content-manifest.json
  rationale: sealed validation resolves only through the manifest;
  an unresolvable reference is the publisher's defect, surfaced now
  rather than in a consumer's pipeline.
```
**Exercised:** at scale — all nine bundles close over the
closure-required reference class: Set members resolve in-bundle 14,508/
14,508 (5,470 objects at HEAD; the original "3,066" predates the
validation corpora). Mapping endpoints and party URIs are LANDMARK
references — resolvable outside the bundle by design; the normative
reference taxonomy is normative since 2026-07-21 (register
"P9-applied"; conformance family `reference-vectors.json`, 9 cases).
The example bundle documents the break-it recipe.

### 2 · `digest-verified` — package domain · *all tiers*

**Signature:** (file bytes, manifest entry) → match | mismatch.
**Semantics:** SHA-256 over the shipped bytes equals the manifest's
`package-digest`. This is the *bytes* question only; meaning is
`attestation-binds`' job.
**Rationale:** pins are the trust anchor because published locations
rot — the flagship's own extension registry vanished with its
repository. A digest mismatch is an integrity alarm, never a
retry-with-network condition.
**Failure:**
```
FAIL [digest-verified] <path>
  computed sha256:<x> != manifest sha256:<y>
  rationale: the pin is the trust anchor; a mismatch means the
  supply chain changed the bytes, not that the tool should fetch
  a fresher copy.
```
**Exercised:** at scale — real digests on all bundle objects.

### 3 · `unique-within(scope, field)` — *all tiers*

**Signature:** (scope, field) → duplicate list (empty = pass).
**Semantics:** enforces uniqueness where the model requires it —
statement ids within a Requirement, object ids within a bundle, exact
facet versions per major line within a manifest.
**Rationale:** the twin-catalog measurement: 11 id strings shared
across two publications of one authority, only 1 prose-identical — ten
silent divergences that no tool could see because nothing checked.
Uniqueness violations are how duplicated truth begins.
**Failure:**
```
FAIL [unique-within] scope=<scope> field=<field>
  duplicate value "<v>" (first at <a>, again at <b>)
  rationale: two carriers of one identity drift independently; the
  measured case is 11 shared ids with 10 diverged texts.
```
**Exercised:** implicitly by construction in the converters; corpus
negative cases are gate-item-2 work.

### 4 · `code-from(codesystem@v)` — *all tiers*

**Signature:** (value, code system + version) → member | not-member.
**Semantics:** enum fields validate against *versioned* code systems
(Appendix C); unknown values are errors, not warnings, because the
next tool would have to guess what they mean.
**Rationale:** measured vocabulary drift in the wild: `normal-SdT`
coexisting with bare `erhöht`; `Compliance Management` with
`Compliance-Management`. Unpoliced value spaces fork silently; the
pinned code system freezes them and makes the fork visible.
**Failure:**
```
FAIL [code-from] <object-id>.<field>
  value "<v>" is not in <codesystem>@<version>
  rationale: enum drift measured in the field (sec_level, tags);
  an unknown code is a fork, and forks get reported, not guessed.
```
**Exercised:** modality/lifecycle codes at scale; drift *findings*
produced by the BSI converter are the negative corpus in waiting.

### 5 · `prose-params-resolve` — *all tiers*

**Signature:** (statement) → verdict per `{param:name}` token.
**Semantics:** every token in prose binds to a declared parameter of
that statement; every declared parameter is referenced or explicitly
marked display-only. Unbound token = error. Structural check only —
no evaluation, which is why Core can run it.
**Rationale:** the 216. One national corpus ships 216
`{{...}}` pseudo-placeholders inside schema-valid documents — free
text wearing parameter costume, invisible to every 1.x tool. A token
is a contract or it is a defect; this primitive is the eyes.
**Failure:**
```
FAIL [prose-params-resolve] <req>/<statement>
  token {param:<name>} has no declared parameter
  rationale: 216 pseudo-placeholders shipped invisibly in one
  national corpus; binding is checked so costume can't pass as
  contract.
```
**Exercised:** at scale (converter token conversion); the 216 are the
reported negative cases, verbatim, in the BSI coverage report.

### 6 · `modality-monotonic` — *P+*

**Signature:** (from-code, to-code, D9 partial order) → monotone |
easing | axis-change.
**Semantics:** compares two modality codes on the lattice (C.1):
same-axis moves upward are free; downward moves and axis changes
require an attached Deviation. `unspecified` sits below everything —
specifying is always monotone. Tier scope (v0.6 cycle, D13 rev): the
Deviation duty binds consumer-tier Tailorings; an Authority-tier
Tailoring is normative source and owes no Deviation — the
classification (monotone | easing | axis-change) still computes and
reports for both. The tier itself is DERIVED (layered anchor, #19):
id-origin match = claimed, authority Attestation over the Tailoring =
proven, else consumer — `tier-vectors.json` derives all three from
data alone.
**Rationale:** weakening must be *possible* (real programs ease with
justification — four FedRAMP prop-workflows existed to do it) but
never *silent*. Measured bonus: CR26's 111 published class-variant
modality moves contained **zero** easings — the channel's emptiness
is now a fact, not an assumption.
**Failure:**
```
FAIL [modality-monotonic] <req>/<stmt>  <from> -> <to>
  non-monotone move without an attached Deviation
  rationale: easing without a record is how baselines rot invisibly;
  the Deviation channel exists precisely so this edit can happen
  in the open.
```
**Exercised:** 111 monotone ops emitted (CR26 tailorings); easing
negatives in the example bundle's break-it recipes.

### 7 · `attestation-binds` — semantic domain + manifest · *P+*

**Signature:** (attestation, bundle) → Full Match | Semantic Match |
fail (+ per-subject detail).
**Semantics:** verify signature (envelope, stdlib DSSE profile); check
`content-manifest-digest` against the manifest as shipped; recompute
each subject's semantic digest (JCS canonicalization of the object
*minus annotations*, with the empty-omission and decimal-as-string
guards) and compare. All subjects match + manifest matches = **Full**;
all subjects match, manifest differs = **Semantic** (report, not
defect); anything else = fail.
**Rationale:** signatures must survive legitimate repackaging
(annotation stripping, re-serialization) while tampering has nowhere
to hide — the two-digest design exists for exactly this verdict
shape. Moved to Portable in v0.5 because JCS lives there; Core treats
Attestations as passive data.
**Failure:**
```
FAIL [attestation-binds] <attestation-id>
  subject <id>: recomputed semantic digest sha256:<x>
                signed                       sha256:<y>
  rationale: normative content changed after signing; packaging-only
  deltas would have produced Semantic Match instead.
```
**Exercised:** real two-digest computation across all bundles; the
example bundle's differing package/semantic digests are the
reproducible demo. Envelope verification awaits the DSSE profile
(gate item 2).

### 8 · `conditional-apply(trigger, enforcement)` — *P+*

**Signature:** (trigger predicate, enforced primitive-instantiation)
→ enforcement verdict where trigger holds; no-op elsewhere.
**Semantics:** the one bounded conditional. Trigger is exactly one of
the three predicates (B.2), ≤1 reference hop, no nesting on either
side; enforcement is an instantiated primitive (bounds, code-from,
uniqueness…). Facets *instantiate* this with bound arguments — they
never define new computation.
**Rationale:** parameter-conditioned allowed values are interchange
semantics on all three authorities ("if class=a then deadline ≤ X") —
refusing conditionality would push it into prose or facets-as-code.
The leash is the lesson of the caught regression: an earlier draft's
casual "selection by facet query" was an expression language wearing
a trench coat. The predicates you get are the predicates there are.
**Failure:**
```
FAIL [conditional-apply:<instance-id>] on <object-id>
  trigger: <predicate> held; enforcement [<primitive>] failed: <detail>
  rationale: <the instantiating facet's declared rationale prints
  here - authored once, read at 2 a.m.>
```
**Exercised:** declared; corpus instantiation is gate-item-2 work
(the CR26 class-conditioned timeframes are the natural first cases).

---

## B.2 The three predicates (shared vocabulary, one leash)

Used identically as `conditional-apply` triggers and in
`Tailoring.selects` — one grammar, one **≤1-hop, no-nesting** budget
(the P8-E3 harmonization: two dialects of "conditional" were one too
many).

**`field-equals(path, value)`** — kernel field comparison, one hop
allowed to follow a single reference. *Selects all Requirements where
`lifecycle` = `active`.* Failure names path, observed value, expected.

**`param-equals(name, value)`** — declared-parameter comparison on
statements. *Trigger for class-conditioned bounds.* Failure names the
statement address and the binding state (unbound is its own error via
prose-params-resolve, not silently false).

**`present(path)`** — existence, nothing more. *Selects Requirements
carrying a given facet.* The deliberately boring one; boring is the
point.

What there deliberately isn't: negation chains, boolean composition,
regex, arithmetic, path wildcards. Every one of those is a real
request someone will make; every one is answered by the escape path
(B.4), not by a grammar extension in place.

---

## B.3 The eight operations (addressing + law + failure)

All operations address by **identity**: `requirement-ref` +
`statement-id` (+ field name) — never by position. Two ops on one
target in one Tailoring = validation error (override happens by
chaining Tailorings, where auditors can see it). Order is list order;
application is on deep copies; every halt prints its rationale.

**`set-parameter`** — law: value satisfies the declared type *and*
bounds/choices; loosening bounds ⇒ Deviation. Corpse: the fused
alternative that hid "oder" inside prose; the md5-outside-choices
demo. Failure:
```
FAIL [op:set-parameter] <req>/<stmt>/<param>
  value "<v>" outside declared <choices|bounds>
  rationale: parameters are contracts with edges; an out-of-bounds
  assignment is either a typo or a weakening - both need daylight.
```

**`set-modality`** — law: `modality-monotonic` (B.1.6) with Deviation
on easing/axis-change. Failure: as B.1.6, prefixed with the op
address. Measured: 111 emitted, zero easings.

**`set-field`** — law: whitelisted non-normative fields only (title,
label, annotations); normative fields have their own ops precisely so
this one stays harmless (`sequence` struck v0.6 — it lives on Set
members, unaddressable by operations; backlog #21). Failure names the
field and the whitelist.

**`replace-prose`** — law: `intent` ∈ editorial | substantive is
mandatory; substantive ⇒ Deviation. Misdeclared intent is forgery
(the migration chapter's word, kept). Corpse: 1.x `alters` that
changed meaning while looking like formatting. Failure:
```
FAIL [op:replace-prose] <req>/<stmt>
  intent "substantive" requires an attached Deviation
  rationale: prose is the normative payload; changing what it
  obligates without a record is the silent-baseline-rot pattern.
```

**`add-relation` / `remove-relation`** — law: typed edges only
(C.8 codes); removal of `required` edges ⇒ Deviation (removing a
dependency is a weakening of the graph). Corpse: BSI's 67 `required`
links — real dependency semantics that props could only gesture at.
Failure names edge, type, and — for removals — the missing Deviation.

**`attach-facet` / `detach-facet`** — law: attaching or detaching a
facet whose declared `modifies-semantics` is non-empty ⇒ Deviation;
chrome-class facets move freely. Corpse: detaching the
assessment-criteria facet from a German requirement *changes what
assessors check* — that's a semantic act wearing a housekeeping
costume. (P9b-8 erratum: an earlier draft named the grammar facet here;
`statement-grammar@1` declares `[]` per the D.12 audit —
chrome-for-computation — so this law never fires on it. The corpse
belongs to a declared `[assessment]` facet.) Failure:
```
FAIL [op:detach-facet] <req>  facet <uri>@<major>
  facet declares modifies-semantics [<classes>]; detach without
  Deviation refused
  rationale: removing declared semantics changes the object's
  meaning for every downstream computation of those classes.
```

---

## B.4 The budget and the escape path (one page, load-bearing)

Three sentences govern everything above. **One leash:** every
conditional construct in the model — predicate selects and
conditional-apply triggers alike — shares one vocabulary and one
≤1-hop, no-nesting budget; needs that exceed it are answered by
moving the rule to where one hop suffices (the D5 edge-local lesson:
the inheritance-boundary rule works *because* it was relocated, not
because the need was denied). **One instantiation rule:** facets
instantiate primitives with bound arguments — machine id, human
rationale, failure message, rationale printing on failure — and never
define new computation; that is the entire difference between a
semantic contract and an embedded language. **One escape path:**
primitives, operations, and predicates are *versioned closed sets*
(R3: contained, never a language) — the ninth primitive, when its
evidence arrives, ships as a set version through the Chapter 15
process, with counts, corpus cases, and two implementations. Until
then, the honest inventory stands: eight, eight, and three — every
one carrying the reason it exists, printed at the moment it says no.
