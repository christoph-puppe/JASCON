# JASCON — Decision Rationale Register
## Every decision, justified against the four north-star tests — the living amendment journal
### opened 2026-07-18 as "OSCAL Semantic Core (v0.5)"; renamed with the project 2026-07-22 (P10 #33e). Editorial note, same item: decision numbers run D1–D22 — there are no D23–D25; the later heading "D26" is backlog item #26 wearing a D-label, kept as written because dated entries are history.

**The four tests (session directive; P9 Finding 0 erratum: this header
once said "three" — the scoring axes below FOLD tests 3 and 4 into one
complexity axis, which is a presentation choice, not a different north
star).** Every decision below is justified
against: **Customer** — a measured need of the authorities and users (ISM,
BSI, CR26 census; SCF/CIS/CSA/NIST-lifecycle evidence), never taste;
**Simplicity** — fewer concepts, fewer ambiguities, learnable and
implementable fast; **Reduced complexity** — total tool-and-ecosystem
complexity goes *down*: no props, no custom Metaschema extensions, no
bespoke JSON formats forced into existence. Where a decision *adds*
something, the register states what larger thing it removes. Trade-offs are
stated; a decision with no stated cost has not been examined.

Format per decision: **Decision · Customer · Simplicity · Complexity ↓ ·
Trade-off.**

---

## D1 — JSON only; CommonMark+GFM prose, no raw HTML
**Decision.** One conformance serialization; one prose dialect with tables.
**Customer.** CR26 (the newest authoritative content) is JSON-canonical;
ISM's XML/JSON/YAML triple-publication is a measured agency tax; compliance
prose is full of parameter matrices — tables are a customer need, not a
luxury.
**Simplicity.** One byte-form to parse, digest, and document; no
markup-mapping rules to learn.
**Complexity ↓.** Deletes the serialization-sync problem that consumed a
large share of Metaschema's existence; deletes the c14n dependency chain.
**Trade-off.** XML constituencies served only via the fenced transit
projection (D18); triple-publishers generate extras outside conformance.

## D2 — Global authority URIs; string comparison; label/aliases; alias≠lineage
**Decision.** Identity is a URI compared as an opaque string, never
resolved; `canonical-alias` (identity) is split from `replaces` (lineage).
**Customer.** BSI's twin-catalog ID collision is a measured composition
failure; all three authorities maintain parallel identifier schemes
(×1,219 / ×188 / ISM labels) — `aliases[]` is their typed home; revisions
must not silently substitute (auditor reality).
**Simplicity.** "Where does this control live?" has one answer; no
import-context namespacing to teach.
**Complexity ↓.** Deletes the entire profile merge/combine algebra and the
resolution spec — the single largest 1.x implementation cliff; kills
`alt-identifier` props before they return.
**Trade-off.** Authorities must govern stable URIs (Authority-tier duty) —
the alternative is the measured status quo: mutable `tree/main` CSV links.

## D3 — Content manifest, sealed mode, two digest domains, canonical forms
**Decision.** Manifest = local resolution table with package- and
semantic-digests per object; attestations excluded; JCS with
empty-omission; decimal as canonical string; semver-normative bundle
composition.
**Customer.** Air-gapped estates (defense) must validate offline; the
deleted FedRAMP registry is the measured cost of network-coupled trust;
CR26 references external submission schemas — signed structured bundles are
the operating reality.
**Simplicity.** One file answers "what is in this bundle and is it
intact"; verification states are enumerable; no fixed-point puzzles.
**Complexity ↓.** Replaces per-tool ad-hoc integrity conventions and 1.x's
non-answer to tamper evidence; deterministic composition replaces
dependency guesswork.
**Trade-off.** Two digests at Authority tier; JCS must be implemented
correctly (test vectors provided); one more file to ship.

## D4 — Nine shallow types; documents are renderings
**Decision.** A graph of nine shallow types; document shapes leave the
normative core.
**Customer.** #2118/#2112 are customers (CSA, BSI) being rejected by
another framework's document conventions; **CR26 already operates
documents-as-views in production**; every GRC tool normalizes documents
into a database on ingest anyway.
**Simplicity.** Nine flat records versus eight deep, positional document
trees; learnable in an afternoon.
**Complexity ↓.** Nine shallow types **replace eight deep document models**
(OSCAL 1.2.2, including its March-2026 Mapping Model); the layout-dispute
class becomes structurally impossible.
**Trade-off.** Legal document reality must be re-covered (D7); rendering
templates are real work; RMF readers relearn "System".

## D5 — Component absorbs System; identified authorizations; inductive boundary rule
**Decision.** One Component type; explicit `authorizations[]` with ids and
member scoping; inheritance across a declared authorization requires a
typed basis, checked edge-locally.
**Customer.** FedRAMP's leveraged authorizations and KRITIS supplier chains
*are* "your system is my component"; multiple concurrent ATOs per service
are the norm; the legal boundary is where liability attaches — auditors
need it addressable, and absence must never be a negative assertion.
**Simplicity.** One composition mechanism instead of two ontologies; each
boundary check is a one-hop rule.
**Complexity ↓.** Deletes the System/Component duality and multi-hop
traversal machinery (induction covers chains); the historical
interconnection-prop cluster dies into typed structure.
**Trade-off.** A component that hides its authorization evades the trigger
— policed by publication duties and assessment practice, stated as R12.

## D6 — One Implementation edge
**Decision.** comp-def linkage and SSP implemented-requirements collapse
into one typed relation with per-clause scoping.
**Customer.** A professional authoring team publicly abandoned component
definitions because complexity exceeded value (PR #8); FedRAMP's daily CRM
and inheritance are exactly this edge's fields; shared responsibility is
per-clause in reality.
**Simplicity.** One relation to learn; responsibility and inheritance are
fields, not conventions.
**Complexity ↓.** Deletes a whole duplication axis and its
synchronization problem.
**Trade-off.** Comp-def marketplaces republish as Component+capabilities —
mechanical migration.

## D7 — Attestation with bi-modal verification
**Decision.** Attestation binds the content-manifest digest; verification
yields Full Match or Semantic Match; DSSE profile contract; provenance map.
**Customer.** Authorizing officials sign documents; lawyers subpoena the
exact view; annotation stripping is a legitimate hygiene right — both
truths are customer facts and the state machine serves both.
**Simplicity.** Two named verification outcomes instead of undefined
"signature broke, nobody knows why".
**Complexity ↓.** Replaces per-vendor signing conventions with one
contract; the H1 forgery vector and the P7 hash cycle are unrepresentable.
**Trade-off.** DSSE-profile maintenance; provenance maps are renderer work.

## D8 — Deviation sub-object
**Decision.** One typed disposition record with a state machine, attachable
where deviations occur; the audited channel for every recognized weakening.
**Customer.** Four historical FedRAMP extensions encoded the identical
state machine four times; CR26 carries corrective actions; BSI audit
practice runs on documented Abweichungen — regulators want weakening
*auditable*, not forbidden.
**Simplicity.** One concept, one state machine, one place to look.
**Complexity ↓.** Replaces five prop-based workflow encodings and ad-hoc
exception fields.
**Trade-off.** State-machine governance lives in stdlib; richer workflows
extend via facets.

## D9 — Statements collection; modality lattice; parties array; honest durations; small parameter algebra
**Decision.** Identified clauses with per-clause modality/parties/
parameters; a normative modality partial order (incl. may-only/DARF NUR);
elapsed vs. calendar durations; a closed scalar algebra.
**Customer.** 3/3 authorities converge on modality (BSI ×1,006, CR26 force
×328 with exactly this code set, ISM style guide); BSI's **347 nested
pseudo-controls** are the measured cost of missing clause granularity;
CR26's `affects[]` is an array (shared responsibility is bedrock); CR26's
`bizdays` is a real deadline unit whose meaning depends on calendars —
pretending otherwise computes wrong deadlines for the customer; DARF NUR is
German normative language, now machine-checkable for the first time.
**Simplicity.** One statement shape for every framework; a printable
lattice instead of folklore about which modality changes are "weaker".
**Complexity ↓.** The single largest prop consumer (BSI grammar, 100 % of
statements) and the 216-defect class disappear; control-splitting
workarounds become unnecessary; no schemas-in-parameters ever.
**Trade-off.** Multi-statement rendering is slightly harder than one blob;
calendar-periods introduce an explicit calendar dependency — honest, and
fail-closed rather than silently divergent.

## D10 — Registered facets; capability declarations; fail-closed; private: harmless by definition
**Decision.** Extensions are schema-validated, federated, exact-pinned;
semantic effect is declared; undeclared registered facets are dangerous by
default; `private:` facets are compliance-invisible by definition.
**Customer.** BSI's 12,059 ns-qualified props with CSV "schemas" are the
measured cost of contractless extension; three tools treating one facet
three ways (preserve/interpret/refuse) is the interoperability failure GRC
buyers actually hit; internal tool bookkeeping needs a legal outlet.
**Simplicity.** "What does this extension mean to my tool" has a decidable
answer; smuggling semantics into the escape valves is self-defeating
rather than policed.
**Complexity ↓.** Kills the props mechanism *and* the incentive to fork
custom Metaschema extensions: the sanctioned path (publish a JSON Schema at
your own domain) is cheaper than either; no central approval queue to
route around.
**Trade-off.** Fail-closed produces hard stops where 1.x guessed (R9) —
deliberate; facet semver is real governance (softened by pinning).

## D11 — SP 800-53 as Canonical Reference Facet; oscal-stdlib
**Decision.** NIST's conventions become the shipped-by-default standard
library, registered under the same rules as everyone.
**Customer.** Every non-NIST authority (CSA in #2118, BSI in the census)
is a customer harmed by 800-53 conventions in core; NIST itself keeps
out-of-the-box primacy and visible leadership.
**Simplicity.** One rulebook for all frameworks — no privileged ontology to
special-case.
**Complexity ↓.** Core carries zero document conventions forever; #2050's
externalization direction completed rather than patched.
**Trade-off.** stdlib release engineering needs an owner; launch optics
(R5).

## D12 — The complete, bounded extension surface
**Decision.** Eight evidence-priced stdlib facets + an open framework-facet
category + annotations; one candidate parked pending verification; ISM
needs zero.
**Customer.** Every stdlib facet cites counted instances (terminology 75/
188, reporting ~40, effectivity 17×paths, security-objectives ×4,494 …);
nothing was invented for elegance.
**Simplicity.** The whole extension surface fits on one page; "where does
my data go" is a lookup, not a debate.
**Complexity ↓.** >70 % of all counted prop instances vanish into kernel
mechanics with **no** replacement facet — the largest single simplification
in the design; unverified reviewer deletions are parked, not executed
(complexity of churn also counts).
**Trade-off.** Medium-confidence facets carry an explicit verification
debt.

## D13 — Bounded selection; identity-addressed ops; per-operation weakening rules; deterministic resolution
**Decision.** Selection by set-ref or three predicates; a closed op
vocabulary addressed by ids; weakening rules per operation with Deviation
as the audited escape; ordered application, same-target conflict = error,
chaining as the only override, no auto-merge.
**Customer.** ISM's 5,557 membership props and CR26's class variants exist
*because* 1.x tailoring was too expensive to be the single source —
baselines are the customer's daily bread, which is exactly why "exclude ⇒
Deviation" was **rejected**: it would drown every ISM classification
baseline and FedRAMP class in pseudo-deviations. CR26's deadline
tightening is the measured case for declared tightening directions.
**Simplicity.** Eight operations you can list from memory; a resolution
algorithm that fits on half a page (Appendix B); failures explain
themselves.
**Complexity ↓.** Replaces the profile-resolution spec *and* general JSON
Patch (whose positional fragility both hostile passes condemned) —
upstream errata can no longer silently repoint downstream tailorings.
**Trade-off.** Less expressive than arbitrary patching by design (R10);
authoring UX must make clause-level edits fluid.

## D14 — Eight primitives, one bounded conditional, no general-purpose expression language
**Decision.** A closed rule set with mandatory rationale-on-failure; one
≤1-hop predicate vocabulary shared with selection.
**Customer.** #2118's defining pathology — a rule nobody can justify —
is a customer-facing failure; parameter-conditioned allowed values are
real interchange semantics in all three corpora.
**Simplicity.** A rule interpreter, not a language runtime; 2-a.m.
failures print their reason.
**Complexity ↓.** CEL (and every future DSL negotiation) stays out; the
complexity balloon has no dark corner to re-inflate into.
**Trade-off.** Genuinely complex framework logic lives in the framework's
own tooling — if it cannot be a primitive, it is not an interchange rule.

## D15 — Core passive; normative feature × tier matrix
**Decision.** Core validates and preserves, computes nothing semantic;
Portable computes with fail-closed; Authority publishes with duties; one
normative matrix.
**Customer.** The customer-facing disaster is a tool that half-understands
a bundle and proceeds — P7-B3's silent-ignore state; RFC-0024's
approved-format slot needs one checkable tier to point at (Portable).
**Simplicity.** "What may this tool do" is a table lookup; the two v0.4
tier contradictions are gone.
**Complexity ↓.** Prose-allocated conformance (the 1.x pattern of
implementation-defined behavior) is abolished.
**Trade-off.** Corpus maintenance is standing engineering.

## D16 — Three migration guarantee levels
**Decision.** Native / compatibility-facet / opaque-preservation, per
element; "information-preserving for the supported corpus."
**Customer.** Adopters must know exactly what survives conversion — a
false "lossless" costs them at audit time.
**Simplicity.** "What did I lose" becomes a query over declared levels.
**Complexity ↓.** Replaces an unprovable universal claim with three
checkable ones; route-around formats (CR26) get absorbed instead of
competed with.
**Trade-off.** Three levels are more documentation than one lie.

## D17 — Declared non-goals
**Decision.** Flows, template accreditation, narrative grammar, PCI
customized approach, ISO management-system clauses, and executable proof
are named as *not covered here*.
**Customer.** Customers are harmed more by silent gaps than by declared
ones; each named gap has a stated home or a stated owner.
**Simplicity.** The spec's edge is drawn, so nobody argues about fog.
**Complexity ↓.** Kernel growth toward BPMN/ISO-MSS territory is refused
explicitly.
**Trade-off.** Coverage tables must be re-earned as targets are taken on.

## D18 — Fenced XML transit projection
**Decision.** One-way JSON→XML with strict XSD guaranteed for
kernel+stdlib only (transit-safe schema subset); third-party facets opaque
unless publisher-mapped.
**Customer.** Defense data diodes with XSD deep inspection are an
installed base; a promise of universal strict XSD would be a lie (P4-H5's
math is right).
**Simplicity.** XML is an encoding, like Base64 — never authored, never
round-tripped.
**Complexity ↓.** JSON-only conformance survives intact; no second
authoring format re-enters.
**Trade-off.** Third-party facet transit is guard-policy-dependent (R11) —
stated, not hidden.

## D19 — Engine positioning; accurate on-ramps; sunset trigger
**Decision.** Ship as a semantic core compiling to 1.x during transition;
name avoids 2.0/profile/kernel; #58 and #2050 cited as live, #2115/#2116
as closed positions; RFC-0024's five-CSP clause recorded.
**Customer.** The RFC-0024 wave (deadlines 2026/2027) is customers'
sunk-cost reality — freezing it would harm the very adopters this design
serves.
**Simplicity.** One public story: an engine under your existing
obligations.
**Complexity ↓.** Avoids a fork of the ecosystem's attention; the
dual-model window is bounded by a declared trigger.
**Trade-off.** Dual-model maintenance until sunset (R8).

## D20 — Mapping as the ninth kernel type
**Decision.** A shallow first-class crosswalk object with IR 8477/OLIR
relationship codes, statement-level scope, provenance, confidence.
**Customer.** SCF's entire product is a 200+-framework mapping graph; CIS
and CSA ship mappings as core artifacts; CR26 itself carries 263
KSI→800-53 links; NIST just shipped a whole eighth model for this (March
2026) — demand could not be better attested.
**Simplicity.** Nine flat fields versus a full mapping document model with
uuid/metadata/revisions/props scaffolding.
**Complexity ↓.** Replaces the 1.2.2 Mapping Model; prevents the two exact
north-star violations that otherwise follow — mappings as relation-string
**props**, and SCF/CSA staying on **bespoke** Excel/JSON.
**Trade-off.** Ninth type (dogma retired with reasons); relationship
code-system governance (R13).

## D21 — Nested sets and normative sequence
**Decision.** Sets nest; `sequence` is a defined presentation-order field.
**Customer.** CSF's Functions→Categories→Subcategories, SCF's 34 domains,
ISO themes, CIS Controls→Safeguards, and ISM's `sort-id` ×1,150 are all
the same customer need: taxonomy and order.
**Simplicity.** One mechanism (sets-of-sets + integer order) for every
hierarchy in the corpus.
**Complexity ↓.** No return of group/part nesting on Requirements — the
#2118 attractor stays dead; order-as-prop stays dead.
**Trade-off.** Deep taxonomies mean set indirection instead of inline
nesting — deliberate.

---

## Rejected alternatives — same three tests, failed

| Rejected | Customer | Simplicity | Complexity |
|---|---|---|---|
| Normative XML / YAML conformance | serves toolchains, not content needs | two more byte-forms to teach | resurrects mapping + c14n |
| URN identity scheme | same DNS rot on rebrand | loses the documentation affordance | adds IANA friction for nothing |
| CEL / sandboxed CEL | no authority asked for a language | a runtime to embed and secure | the historical re-inflation site |
| General JSON Patch (RFC 6902) | breaks customers on upstream errata | positional paths are unreadable | recreates baseline-shatter — convergently condemned |
| Central approval registry | months-long queues drive flight to private: | one more gatekeeper to petition | the Rev4 registry died exactly this way |
| Grammar in the kernel | Procrustean for CSF/ISO/privacy customers | forces linguistics on everyone | replaces NIST's bias with BSI's |
| "exclude ⇒ Deviation" (P7-B2 part) | drowns every baseline customer in pseudo-deviations | thousands of records nobody reads | kills the mechanism absorbing 5,900+ membership props |
| Mapping as stdlib facet (P8) | third-party crosswalks own neither endpoint | facet-on-whose-object debates | regresses to relation-string props |
| Universal weakening detector | promises the customer what cannot be computed | undecidable "is this weaker" arguments | requires exactly the semantics engine we refuse to build |
| Separate System type · defaulted boundary boolean | overlapping ATOs unrepresentable · absence became a legal claim | two ontologies · silent negatives | duplication + negative-assertion hazard |
| Authority `variants` carrier on Requirement (v0.6 cycle) | authority-variance is 1-of-3 (CR26 only) and its mechanism — Tailoring — exists | a second way to say "per-class differs" | fails the D22 promotion bar on tests 1 and 2; new kernel structure taxing every validator |

## The structurally-dead category — the north star's largest win

Membership matrices (ISM ×5,557; CR26 subsets + per-class lists), inline
class variants (`varies_by_class`, 79 CTL overlays), sort-ids (×1,150),
per-object revision props (×2,202 + CR26 `updated[]` everywhere), UUID/
attachment/import plumbing, and 216 pseudo-placeholders — **over 70 % of
all counted prop instances across three authorities** — disappear with no
replacement construct at all, because the kernel mechanism they were
imitating (sets, tailorings, L0 versioning, manifests, typed parameters)
now exists and is cheap. That is the measurable meaning of "no more props,
less bespoke": most extension was never extension — it was a core deficit,
and the deficit is closed.

---

# Amendments — v0.6 cycle, review round 1 (2026-07-21)

Backlog items #1, #2, #4, #5, #7 decided; rows leave the backlog per its
standing rule. Spec changelog IV.7 carries the same table; normative text
in the specification's D9/D10/D13/D20/D21/D22.

## D22 — Kernel promotion rule *(new)*
**Decision.** Promotion from facet space into the kernel requires all
three: **≥ 2-of-3 independent authority encodings** · **one shared
computation** every generic tool must perform · **one vocabulary that fits
all corpora without flattening**; and a candidate whose kernel *mechanism*
already exists is absorbed by that mechanism, never by a new field
(assurance levels: 3-of-3 encoded, yet level-as-a-Set — level-as-a-field
is the 5,301-marker corpse).
**Customer.** Every kernel field is a permanent tax on every Core
validator; only the census may levy it. The rule was implicit until App. F
Q22 forced it into words — and "why isn't X kernel" disputes are customer-
facing friction (the #2118 class: rules nobody can justify).
**Simplicity.** The bar is three countable questions; a promotion PR that
cannot show its three passes is rejected without further argument.
**Complexity ↓.** Ends promotion-by-advocacy, the historical re-inflation
channel by which cores grow until they need a metaschema.
**Trade-off.** A genuinely novel semantic with one national encoding waits
in a facet for a second authority — the kernel lags evidence, never leads
taste.

### D22 (rev, same cycle) — The anticipated-convergence path
**Decision.** Promotion is also permitted at 1-of-3 when a major census
authority ships and depends on the semantic, general use is credibly
anticipated (argued here, in the register), and the absorption clause
holds. Such promotions carry evidence tier **anticipated**, are re-verified
at every corpus addition, and demote back to facet space after two gate
cycles without materialized convergence.
**Customer.** The census population is three; treating its consensus as a
ceiling would make the kernel hostage to the historical accident of which
three authorities published first. FedRAMP wanting a thing, plus a credible
argument everyone else will too, is customer evidence — one tier below
measured, and labeled as exactly that.
**Simplicity.** One extra clause, same three-question shape, plus a clock.
**Complexity ↓.** Without the path, anticipated-general semantics ship as
facets, harden in tooling, and cost a migration when convergence arrives.
**Trade-off.** The kernel can now be wrong in a new way — which is why the
tier label and the demotion clock are not optional.

### The anticipated-path re-audit of the facet space (2026-07-21)

Every stdlib facet re-checked under the amended rule:

| Facet | Today | Anticipation case | Verdict |
|---|---|---|---|
| `terminology@1` | 1-of-3 (CR26 FRD: 75 terms, 188 aliases; alias-resolution computation measured, 264/264) | every national framework publishes terminology | **Kernel candidate** — the strongest anticipated case; final shape (carrier object vs. root-Set hosting) decides with the gate-2 schemas → backlog #6 re-scoped |
| `reporting-obligation@1` | 1-of-3 (CR26 `notification[]`) | NIS2 / DORA / CRA are notification-duty regimes — the incoming EU wave is *made of* reporting deadlines | **Anticipated candidate** — revisit at gate 2 with the declaration promotion (backlog #8) in place; promote when an EU corpus lands |
| `effectivity@1` | 1-of-3 (CR26 `info.effective`) | every regulation has effective dates and transition periods | Absorption check first: lifecycle + L0 versioning cover part of it; what remains is a gate-2 question, not a promotion yet |
| `security-objectives@1` | 1-of-3 (BSI C/I/A/Auth) | C/I/A is universal in theory | Stays facet — fails test 3 measured: values ("1"/"0") share no scale with anyone; anticipation cannot cure a vocabulary that already flattens |
| `statement-grammar@1` | 1-of-3 encoded (BSI ×1,006) | grammar is universal in theory | Stays facet — the rejected-alternatives table already names the corpse: kernel grammar replaces NIST's bias with BSI's |
| `assessment-criteria@1` | 2-of-3 (BSI `documentation` ×959 + CR26 artifacts/key_tests) | — | Stays facet — passes test 1, fails test 3: free-text document names vs. per-class artifact lists vs. KSI tests are irreconcilable shapes |

## D22-applied — Terminology hosting: root-Set normative, carrier rejected *(backlog #6, gate 2)*
**Decision.** A glossary is hosted as `terminology@1` on a RequirementSet —
typically the corpus root — whose id, version, and lifecycle govern it; a
dedicated carrier object (or tenth kernel type) is rejected. Normative in
the stdlib descriptor: `uses-term` relations resolve against the nearest
hosting Set; an unresolvable term ref is a Portable-tier validation error.
**Customer.** The D22 anticipated path opened the kernel door; the
absorption clause walked through it first: the existing mechanism (facet
on a Set) measured 264/264 reference resolution with zero new structure.
**Simplicity.** No tenth type; the ledger claim "nine shallow types"
survives its strongest challenger.
**Complexity ↓.** Identity, versioning, lifecycle, and digests come free
from the host Set — a carrier would reimplement all four.
**Trade-off.** A glossary shared by several corpora needs its own hosting
Set (a one-member Set is legal and cheap) — accepted; re-opens only if a
measured multi-corpus glossary corpus arrives (D22 clock discipline).

## P9-applied — Reference taxonomy: closure vs. landmark *(backlog #16, closed 2026-07-21)*
**Decision.** Two reference classes, normative: **closure-required**
references MUST resolve in-bundle (Set `members[].ref`; Tailoring
`selects[].set-ref`, `excludes[].ref`, operation `requirement-ref` +
statement existence; Implementation `component-ref`/`requirement-ref` +
the D5 `basis-ref` against the component's authorizations; Finding
`assessment-ref`/`requirement-ref`; Mapping `source/target-scope`
statement ids WHEN the endpoint is in-bundle). **Landmark** references
resolve outside the bundle by design (Mapping endpoints, party/authority
URIs, evidence refs, external schema/reference URLs, attestation
subjects — self-verifying via their digests). Parties get no kernel
type: the D22 test scores 0-of-3 (no census corpus publishes party
objects; CR26 `affects[]` are strings).
**Customer.** P9b-1 measured the contradiction: 1,008 Mapping endpoints
+ every party URI in the shipped corpus resolve to nothing, under a
primitive whose text said "a bundle that doesn't close doesn't
validate." Crosswalks own neither endpoint — external endpoints are the
normal case, not a defect.
**Simplicity.** One question per reference: does the bundle promise it?
**Complexity ↓.** No party plumbing; no forced vendoring of foreign
catalogs into every bundle that maps to them.
**Trade-off.** A consumer resolving a landmark ref needs the other
bundle — exactly what Mapping provenance and pinning are for.

## P9-applied — The layered tier anchor *(backlog #19, closed 2026-07-21)*
**Decision.** Tier is derived, never stipulated: id-origin match against
the selected content = authority-CLAIMED; an in-bundle Attestation by
the content's authority covering the Tailoring (digest-verified) =
authority-PROVEN, and proof beats prefix; else consumer. Deviation
duties bind at consumer tier; claimed/proven are reported distinctly.
**Customer.** P9b-6 proved two conformant tools could disagree on one
bundle's validity because the duty hinged on a tier no artifact carried
— the implementation-defined-behavior pattern D15 exists to abolish.
**Simplicity.** One string comparison for the claim; one digest + one
origin comparison for the proof. Both offline, both sealed-mode.
**Complexity ↓.** No tier field to author, forge, or forget — the data
already says who selected whose content and who signed.
**Trade-off.** Prefix claims are honest-publisher signals (anyone can
mint under a URI they don't control) — which is exactly why the proven
layer exists and why tools MUST report the difference.

## P9-applied — Facet enforcement executable *(backlog #17, closed 2026-07-21)*
**Decision.** The Portable-tier rule runs: stdlib facet payloads
validate against the normative descriptors; non-stdlib facets validate
against the bundle-pinned schemas (the manifest pin is the registry);
`private:` is ignored by definition; anything else is unregistered ⇒
error. Pinned facet-schema files are themselves existence- and
digest-verified.
**Customer.** P9-1's probe: a corrupt payload plus
`unregistered-dangerous-facet@99` validated green — the 1.x
valid-and-meaningless pathology reborn. Now both are vectors, both fail.
**Simplicity.** The manifest already carried the registry; enforcement
is a lookup plus a schema check.
**Complexity ↓.** No warning tier, no guessing tool: the three legal
states (validated, pinned-validated, ignored-private) are exhaustive.
**Trade-off.** Publishing a facet now genuinely requires publishing its
schema — which was always the contract.

## D10 (rev 2) — Declaration-audit promotions *(backlog #8)*
**Decision.** The three under-declared stdlib facets promote their
`modifies-semantics` declarations: `security-objectives@1` → `[selection]`,
`effectivity@1` → `[selection]`, `reporting-obligation@1` → `[assessment]`.
`cr26/scope@1` remains the exemplar that already declares `[selection]`.
The normative schemas at gate 2 ship these declarations; bundle stubs
update at the next converter run.
**Customer.** The user directive states the principle plainly: **a tool
that cannot handle a facet must stop working on that data.** Fail-closed
only engages when the declaration is honest — a facet declaring `[]` while
actually carrying selection or assessment semantics is the silent-ignore
corpse (P7-B3) wearing a conformance badge.
**Simplicity.** The declaration says what the payload does; no consumer
guesses.
**Complexity ↓.** Under-declaration is the cheap lie that reintroduces
props semantics (meaning invisible to the contract); this closes it for
the shipped stdlib.
**Trade-off.** Real fail-closed stops in tools that ignored these facets —
deliberate, and exactly the stops the user directive demands.

## D9 (closure note) — No duration union; unit-class boundary stays strict *(backlog #3)*
**Decision.** Closed without change. The elapsed-duration vs.
calendar-period split keeps its strict unit-class boundary; no union type
enters the algebra.
**Customer.** Zero measured crossings — the 51 first-pass flags were
base-absent authority variants, a ceremony question resolved under the
D13 rev (backlog #2), not a typing question.
**Simplicity.** A union type would exist to serve zero counted cases.
**Complexity ↓.** The fail-closed calendar rule stays the only rule;
nothing new to implement.
**Trade-off.** If a future corpus ships a genuine crossing, the item
re-enters the backlog with its count — the standing rule works in both
directions.

## D9 (rev) — Parameter `label` + `default` *(backlog #1)*
**Decision.** Optional `label` (display handle, never an identifier) and
`default` (advisory, type-valid) on parameter declarations. Resolution
never substitutes a default silently; binding remains `set-parameter`-only.
**Customer.** BSI labels ("regelmäßig") + `values[]` on 179 requirements,
exiled to L2 `param-extras` for want of two optional fields.
**Simplicity.** Two scalars; no resolution semantics touched.
**Complexity ↓.** Empties a whole L2 residue class (drains at the next
converter run).
**Trade-off.** A default that consumers *expect* to auto-apply will
surprise them once — the silent-substitution corpse says surprise them.

## D10 (rev) — `by-statement` payload keying *(backlog #7)*
**Decision.** Facet payloads addressing individual statements MUST key
them `by-statement: {sid: payload}`; a key naming no statement of the host
is a validation error.
**Customer.** 1,015 statements' payloads across six facets already ride
this converter convention; a second producer inventing divergent keying
would fracture per-clause alignment for every consumer.
**Simplicity.** One shape to learn; checkable without facet knowledge.
**Complexity ↓.** Pre-empts a per-facet addressing zoo.
**Trade-off.** Facets with exotic addressing needs (ranges, pairs) must
model them inside the payload — deliberate.

## D13 (rev) — Deviation duties bind at consumption tier *(backlog #2)*
**Decision.** Authority-tier Tailorings are normative source: the
per-operation Deviation requirements do not apply to them; weakening
classification is still computed and reportable. Consumer-tier Tailorings
keep the full table.
**Customer.** 29 variant-only CR26 rules + 5 KSI variants forced the
converter to synthesize base prose to have something to "deviate" from —
ceremony without a wronged party; the authority publishing variance *is*
the norm being varied.
**Simplicity.** One question decides the duty: who published the
Tailoring?
**Complexity ↓.** No `variants` carrier enters the kernel (rejected — see
table above; fails D22 on tests 1 and 2); synthesized-prose flags and
converter pseudo-Deviations disappear.
**Trade-off.** "Which class eases the base" becomes a report a tool runs,
not a record the authority writes — acceptable because the measured easing
count across 111 CR26 class-variant moves is zero.

## D20/D21 (rev) — Supplement pattern named; `supplements` registered *(backlog #5)*
**Decision.** D21 names the supplement pattern normatively (own-prefix
authorship + shadow set with interleaved sequence + attachment by
reference); D20 registers `supplements` as a stdlib relationship extension
code beyond IR 8477 — non-chaining, OLIR exports MAY down-translate to
`supports`.
**Customer.** Q23's asker ("where did profile add/alter go?") speaks for
every 1.x profile author; multi-authority membership is proven in the
bundles.
**Simplicity.** The verb split is teachable in one line: modifying is
Tailoring, adding is authorship.
**Complexity ↓.** No injection mechanism, no merge provenance, no resolved
artifacts with tool-run lineage.
**Trade-off.** One code added to an adopted external vocabulary — fenced
by the extension marking and the down-translation rule.

---

# Amendments — v0.6 cycle, round 2 (2026-07-22)

Backlog items decided per the standing rule (counts in, register entries
out). Round 2 acts on the P9c re-review (which found the P9-cycle
enforcement narrower than the register's prose) plus the deep-research
open items. Normative text lands in the specification's D3/D9/D13, the
schema, Appendices A–C, and the validator; conformance grew 115 → **125
vectors** (jcs 8 · modality 21 · parameter 14 · tailoring 15 · attestation
5 · facet 7 · reference 11 · lifecycle 36 · tier 8).

## D13 (rev 3) — Op-law completed: `set-parameter` bounds + `remove-relation` *(backlog #25)*
**Decision.** Bundle-level op-duty enforcement now covers the full D13
table, not three of its rows: a `set-parameter` whose value fails the
declared type is a hard error at any tier; out-of-bounds / against-
tightening is a consumer-tier Deviation duty; `remove-relation` of a
`required` edge is a consumer-tier Deviation duty (B.3). The
`param_check` verdict function is now called on real Tailoring ops, not
only on abstract vectors.
**Customer.** P6-F2's "evasion backdoor" was accepted-to-close at v0.5
but shipped unenforced on the workhorse operation — a consumer could
loosen a `tightening:lower` deadline 6h→24h with no Deviation and
validate green (P9c-2, demonstrated). The audited-weakening channel now
holds for every weakening op.
**Simplicity.** One verdict function, called everywhere a duty can arise.
**Complexity ↓.** Closes the gap between "op-duty enforcement live"
(#19's claim) and what shipped. **Trade-off.** None — the machinery
already existed; it was one branch short. Six negative/positive
tailoring vectors added.

## D13 (rev 3) — Tier reported distinctly; signature verification is gate-4 *(backlog #24, partial)*
**Decision.** The reference validator now emits each Tailoring's derived
tier — `authority-claimed [prefix — UNPROVEN]`, `authority-proven`, or
`consumer` — honoring spec:399's "report claimed and proven distinctly."
The residual: `authority-proven` still digest-matches an attestation
without verifying its signature (`derive_tier`), so both authority tiers
remain forgeable by a party minting under the content origin. **Full
resolution — signature verification of the proven tier — is deferred to
the gate-4 DSSE engine** and stays open as the crypto half of #24.
**Customer.** P9c-1: a prefix claim is an honest-publisher signal, not
proof; a tool that never surfaces the distinction lets a consumer-tier
easing escape the Deviation duty by string choice with no signal. The
report is the mandated interim mitigation.
**Trade-off.** Reporting without enforcement is half a loaf — labeled as
such, with the enforcement gated where the crypto lives.

## D3 (rev) — Canonical decimal string: no leading zeros; scale is significant *(backlog #27)*
**Decision.** `decimalString` = `^-?(0|[1-9][0-9]*)(\.[0-9]+)?$`. Leading
zeros are rejected (a non-canonical spelling of one value). Trailing
zeros are **scale-significant by design** ("lexically defined scale/
precision", D3.4): `1.5` and `1.50` are DISTINCT values and their
differing digests are correct, not the divergence P9c-4 first framed.
Re-scaling a value is forbidden.
**Customer.** Two Authority tools must derive identical digests for one
authored decimal (D3.4 MUST); the leading-zero hole let `01.5` and `1.5`
diverge for identical meaning. Latent (decimals not yet corpus-
exercised), fixed before it bites. **Trade-off.** Converters must
preserve the source's exact decimal spelling (scale), never re-scale.
Two decimal vectors added.

## D2 (rev) — `canonical-alias` is self-policing *(backlog #14)*
**Decision.** A validator holding both objects MUST verify a
`canonical-alias` same-content claim: compare content digests modulo the
identity fields (`id`, `version`, `label`, `canonical-alias`,
`replaces`); a mismatch is a reported error — the rebrand should have
been `replaces`. Implemented in `closure_errors`; two reference vectors.
**Customer.** D2's v0.5 trade-off ("authorities must govern stable URIs")
left a mis-issued alias for a changed-meaning revision to silently
misalign every consumer; the check costs one digest comparison and makes
the assertion self-policing instead of trusted. **Trade-off.** The check
needs both objects in hand; cross-bundle aliases verify when the other
bundle is present (exactly what pinning is for).

## C.8 (rev) — Relations channel aligned; `supersedes` removed *(backlog #20, partial)*
**Decision.** The D13 table row now states the computed semantics B.3
already carried (`remove-relation(required) ⇒ Deviation`), ending the
three-way spec/handbook contradiction P9b-4 measured. C.8 base code
`supersedes` is **deleted** — D2 split that concept into
`canonical-alias`/`replaces` after P7-B4 proved it unsafe; a second
un-split lineage carrier would resurrect the hazard (0 corpus
instances). **Remaining (open):** constraining extension relation types
to a namespaced-URI shape in the schema is **blocked on the converter
rerun** — the corpus carries `sharpens` ×28, a bare-word extension
(exactly P9b-4's "typo'd base code silently becomes a carried
extension" corpse); migrating it to a URI code rides the rerun, then the
schema constraint lands.
**Trade-off.** One measured corpse (`sharpens`) stays live until the
rerun; noted, not hidden.

## D21 (rev) — Sets are unaddressable by operations; `sequence` struck *(backlog #21)*
**Decision.** Operations address `requirement-ref` (+ statement-id);
Sets are **not** operation targets in v0.6 — Set membership and order
are *authorship* (publish a new Set / shadow Set), never *tailoring*.
`sequence` is therefore struck from the `set-field` whitelist (it lives
on Set members, which operations cannot reach; 0 corpus uses). Target
version-pinning rides the `requirement-ref` URI as `id@version` (D3), so
no new operation field is needed and ch06's SHOULD is satisfiable as
written.
**Customer.** P9b-5: an unreachable whitelist entry is a promise the
mechanism can't keep. **Complexity ↓.** No Set-addressing sublanguage
enters the op vocabulary (no corpus demands member reordering via
tailoring). **Trade-off.** Reordering a Set's members is a new
publication, not an operation — deliberate, matching the
authorship-vs-tailoring line (D13/D21).

## D22 (rev 2) — The anticipated-convergence path is scoped pre-1.0 *(backlog #22)*
**Decision.** The anticipated-convergence promotion path (1-of-3 with
credible general use, tier `anticipated`, demote after two dry cycles)
is **available only pre-1.0.** Rationale: demotion would make content
authored during the anticipation window schema-invalid against the
closed kernel shapes (`unevaluatedProperties:false`) with no migration
rule (P9b-10). Pre-1.0 there is no compatibility promise to break;
at 1.0 the path closes (a post-1.0 anticipated promotion would need the
compat-facet-on-demotion machinery, deferred until a real candidate
demands it). Latent today — zero anticipated promotions shipped
(terminology landed via the absorption clause, not this path).
**Trade-off.** The kernel's "lag evidence, never lead taste" discipline
keeps a one-cycle window; after 1.0 it must wait for measured 2-of-3.

## D22-applied (rev) — `uses-term` nearest-Set = fewest membership hops *(backlog #23)*
**Decision.** "Nearest hosting Set" is defined: the hosting Set reachable
in the **fewest membership hops** from the Requirement; a tie (a
Requirement that is a direct member of two glossary-hosting Sets — the
supplement-pattern collision) is a **Portable-tier validation error**,
not a silent pick. An authority avoids the tie by hosting its glossary
on a single dominating Set or by explicit precedence in the payload.
**Customer.** P9b-11: two conformant tools resolving one term to two
definitions is the implementation-defined-behavior pattern D15 abolishes.
**Trade-off.** Multi-glossary corpora must structure hosting to avoid
ties — cheap, and the error makes the ambiguity loud.

## R6-applied — Renderer-template accreditation is a declared non-goal *(backlog #15)*
**Decision.** The kernel makes render-tampering **detectable** (templates
named, version+digest-pinned, attestation-bound; D7) but does not
**accredit** templates. Accreditation is an **authority-local governance
choice**, recorded as an explicit non-goal (ch15's "one governance seat
left deliberately empty" made normative): an authority MAY accredit
templates for its own corpora and list accredited digests in its
registry; the core neither blesses nor requires it.
**Customer.** Deep-research vuln 4: the rendering TCB is pinned but
unowned. Naming a single ecosystem accreditor would be a gate (the
registry corpse); making it authority-local keeps federation intact.
**Trade-off.** No portable "this template is faithful" claim — detection
plus publisher reputation is the interim, stated not hidden.

## D26 — Facet enforcement: stdlib strict, pin-honoring; delivery on the rerun *(backlog #26, partial)*
**Decision recorded.** stdlib facet payloads validate against the
normative descriptors (`additionalProperties:false`); non-stdlib against
the bundle-pinned schema. The **real** pinned schemas (with
`additionalProperties:false`) and the pin-vs-descriptor precedence rule
ship with the **converter rerun** — today the bundles pin permissive
illustrative stubs, so framework/compat payloads are under-validated
(P9c-3, demonstrated smuggle). Until the rerun, the reference validator's
use of the hard-coded strict stdlib descriptors is the interim (stricter
than the pinned stub, and divergent from a pin-honoring sealed tool —
the gap #26 tracks). **Open**, tied to the rerun.

## D9 (rev 2) — The `text` primitive: human-readable fields are language maps *(backlog #12; author decision 2026-07-22)*
**Decision.** Adopt a `text` primitive — `{BCP-47: string}` — for every
kernel human-readable field (`title` on all nine types, Mapping
`rationale`, Finding/action and capability `description`,
`deviation.rationale`) and, normatively, for facet-payload free text.
Identifiers stay plain strings (`id`, `version`, codes, and `label` — a
display handle, never a translation target). This **generalizes and
names the existing `langMap`** (already carried by `prose` and choice
labels); it is not new machinery. **Delivery** — the schema field-switch
+ all-converter reruns + full re-pin — rides the converter rerun (the
digest churn folds into one re-pin, not two); a transitional
string-or-`text` schema MAY bridge the window. Stays open until delivered.
**Customer.** **EU standards must be available in all 27 official
languages** — the incoming NIS2 / DORA / CRA wave is published in 27
languages by law, and a `title` or `rationale` that cannot declare its
language is unrenderable for that reality. The defect is already
measured: the converters disagreed for want of a rule (BSI guidance
tagged ×1,004 vs. CR26 `description` bare ×180; ISM shipped 300 bare
`prose` beside 1,150 tagged), and `title` ×3,041 + Mapping `rationale`
×373 are bare today. `prose` already committed the design to
language-tagging; leaving the rest bare was the inconsistency, not a
considered exception.
**Simplicity.** One text type everywhere: human-readable → `text`,
identifier/code → string. Nothing new to learn — `langMap` promoted.
**Complexity ↓.** Ends the tagged-vs-bare ambiguity the converters kept
re-litigating; "which language is this, and what still needs
translating?" becomes a checkable question, not a guess — the same
make-the-failure-unrepresentable discipline the rest of the kernel runs on.
**Trade-off.** A full re-pin (nearly every object carries a `title`),
folded into the converter rerun. Single-language authorities write
`{"en": "…"}` for titles — the ceremony `prose` already imposes, now
uniform.

## Round-2 backlog dispositions

| Backlog | Disposition |
|---|---|
| #13 | **Close** — `calendar-context@1` stdlib code system seeded (C.9): us-federal/de-bund/eu-target2; `calendar-ref` SHOULD cite it; CR26 ad-hoc migrates at rerun |
| #14 | **Close** — canonical-alias same-content check implemented + 2 vectors (D2 rev) |
| #15 | **Close** — template accreditation = declared non-goal (authority-local); R6-applied |
| #20 | **Partial** — D13 row aligned, `supersedes` deleted; **stays open** for the schema URI-shape constraint (blocked on the `sharpens` migration at converter rerun) |
| #21 | **Close** — Sets unaddressable; `sequence` struck from the set-field whitelist (D21 rev) |
| #22 | **Close** — anticipated path scoped pre-1.0 (D22 rev 2) |
| #23 | **Close** — nearest-Set = fewest membership hops; ties ⇒ Portable error (D22-applied rev) |
| #24 | **Partial** — tier reported distinctly (done); **stays open** for signature verification of the proven tier (gate-4 DSSE) |
| #25 | **Close** — op-law completed for set-parameter + remove-relation (D13 rev 3) + 6 vectors |
| #26 | **Partial** — decision recorded; real pinned schemas + pin-honoring **stay open** on the converter rerun |
| #27 | **Close** — decimal no-leading-zeros + scale-significance (D3 rev) + 2 vectors |
| #28 | **Close** — count erratum applied (README/spec → 125; recompute via validate_core.py) |
| #12 | **DECIDED — adopt** (author decision 2026-07-22; register "D9 rev 2"). Rationale: **EU standards must be available in all 27 official languages.** `text` = `{BCP-47: string}` for all human-readable fields; identifiers stay strings. Delivery (schema field-switch + all-converter reruns + full re-pin) rides the converter rerun — stays open until delivered. |
| #10 | **Open** — gate 3 (NIST catalog); see `drafts/gate-3-plan.md` |
| #18 | **Open** — gate 4 (engines: bundle-composition semver + conditional-apply vectors) |

# Amendments — gate 3 (2026-07-22)

Gate 3 delivered (spec IV.9; census `drafts/gate-3-census.md`; plan
`drafts/gate-3-plan.md`). Three corpora converted census-first
(US.SP800-53 · US.CSF · US.IFA-GoodRead), backlog #10 drained, #9
confirmed. **The customer test passed: zero kernel-schema changes.**
Two reference-validator defects were exposed by the corpus and fixed;
conformance grew 125 → **129 vectors** (parameter 14 → 17, tier 8 → 9).

## D10 (rev 3) — #10 CLOSED: ODP addressing = the declaring statement
**Decision.** An external overlay citing an ODP addresses it as
**(requirement, parameter-name) resolved via the DECLARING statement**
— the statement whose `parameters[]` carries the declaration (D10
by-statement keying). No separate statement map is needed.
**Evidence (measured, the whole point).** Rev 5.2.0 conversion: no ODP
is inserted in ≥ 2 statements (histogram 0×399 / 1×1,201); the formal
ODP ids (`AC-01_ODP[01]`) round-trip mechanically to param names
(1,327/1,327). The CR26 CTL overlay's 16 assignments over 14 controls
all resolved to unique declaring statements — emitted as
`set-parameter` operations on the `rev5-odp-overlay` Tailoring with the
tailored Requirements carried in-bundle (closure; the
authorization-package pattern). Params without a statement insertion
site (399: 326 bind only in 53A objectives, 73 nowhere) declare on the
first statement — the declaration site stays deterministic.
**Alternative rejected.** A statement-scoped Mapping per ODP — heavier,
and the measurement shows the ambiguity it would disambiguate does not
exist in the wild. Revisit only if a catalog ships duplicate ODP names
across statements (that catalog earns a finding first).

## D13 (rev 4) — Tier derivation resolves through Sets: no wrapper laundering
**Decision.** The tier anchor's content origin resolves **through**
selected Sets to their member ids (transitively) and through the
operations' `requirement-ref` targets — never stopping at a wrapper
Set's own id.
**Evidence.** The CR26 `rev5-odp-overlay` (FedRAMP-minted Set around
NIST controls) derived authority-claimed under the shortcut — a
self-minted wrapper laundered consumer into authority. The corpus
falsified the reference implementation; spec:396 revised, validator
fixed, vector `wrapper-set-does-not-launder-origin` locks it. The same
resolution symmetrically recognizes an authority's own content behind a
foreign-minted wrapper (vector `mixed-origin-content-blocks-the-claim`
revised: its old data wrapped same-origin content in a foreign Set —
the intent said "content", the data said "wrapper"; data now matches
intent).

## D9 (rev 3) — Multi-select values: a list is legal exactly on `many`
**Decision.** A choice parameter with `cardinality: many` accepts a
**list** value; every element must be a declared choice. A list on
`one` is a type error (invalid, not Deviation-escapable); a foreign
element in the list is out-of-set (Deviation duty at consumer tier).
**Evidence.** `param_check` had no legal form for multi-select values —
exposed when the FedRAMP CTL binds NIST many-cardinality ODPs.
FedRAMP flattens multi-selections into prose strings ("privileged
accounts; non-privileged accounts", "local, network and remote"); every
split part matches a declared NIST choice exactly, so the converter
normalizes the serialization (×3, counted, REPORTED upstream). 3
vectors.

## D2-applied — Withdrawal lineage inverts onto the successor's `replaces[]`
**Decision.** Withdrawn tombstone controls (labels + status + lineage
links, no normative content) are **dropped**; their lineage inverts
onto the successor's kernel `replaces[]` — `incorporated-into` → mode
`merged-into`, `moved-to` → mode `renamed` — with statement-precision
targets and the tombstone's label/title (CSF: its 1.1 outcome prose)
carried in the successor's `annotations["nist-withdrawal"]`. A
successor may be a **Set** (sa-12 → the SR family; ID.GV → the GV
function): the shared base makes Set-level `replaces` legal.
**Evidence.** Rev 5: 182 tombstones, 199 + 1 successor edges; CSF: 91
(12 categories + 79 subcategories), 134 + 1 edges; chains 0, dangling
0. Zero corpus mapping endpoints hit withdrawn ids (measured), so no
resolver regression. **Rejected:** emitting tombstones as Requirements
— the kernel demands ≥ 1 statement with an obligated party, which a
tombstone cannot honestly supply; fabricating either fails the
statements-are-real rule.

## #9-applied — Lifecycle seeds CONFIRMED against the IFA corpus
**Decision.** The shipped enums stand unchanged. Finding
`open · in-remediation · closed`; assessment
`satisfied · not-satisfied · inconclusive`; deviation types/states as
shipped.
**Evidence (counted).** Every IFA source state mapped with zero
additions: AR target `not-satisfied` → assessment result; POA&M risk
`open`+planned remediation → `in-remediation` with `actions[]`
(due = task window end); risk `deviation-approved` → approved
`risk-adjustment` Deviation (rationale = the mitigating factor,
approver = the SCA division URI); risk `investigating` → the deviation
state enum already carries it. The five lifecycle types validate at
document scale with both digests — the standing Test-2 gap is closed.

## Gate-3 source findings (all REPORTED upstream)
NIST rel-code spelling split (`incorporated_into` CSF vs
`incorporated-into` Rev 5) · fragment-marker-less href (CSF DE.DP-04)
· 3 cross-control param insertions (ia-13.3, sc-42.2, si-10.1 insert a
foreign control's ODP; declaration duplicated onto the inserting
statement per the 216 per-statement rule) · 71 ODPs bound nowhere ·
`_stmt.` vs `_smt.` statement-id spellings (SSP examples vs catalog) ·
FedRAMP multi-select flattening (normalized ×3) · PUA codepoint in IFA
prose (`soware`) · placeholder uuids ×4 in the leveraged pair
(provided-uuid dereference degenerate; inheritance wired via the
authorization anchor).

## Gate-3 backlog dispositions

| Backlog | Disposition |
|---|---|
| #10 | **Close, DRAINED** — D10 rev 3: (requirement, ODP) resolves via the declaring statement; 16 CTL assignments → `rev5-odp-overlay` Tailoring; 14 controls carried in-bundle; guidance stays parked (D20 supplements territory, not ODP addressing) |
| #9 | **Confirmation delivered** — #9-applied: zero enum additions; five lifecycle types at document scale, both digests |

# Amendments — gate 4 (2026-07-22)

Gate 4 delivered same-day (spec IV.10; plan `drafts/gate-4-plan.md`;
measurement `drafts/gate-4-measurement.md`). The engines the conformance
corpus had named gaps for now exist; the two economic claims are
measured. Conformance grew 129 → **149 vectors** (12 families: + dsse 5,
composition 7, conditional 8).

## D7-applied — DSSE verification engine; the reference pins Ed25519 *(backlog #24 CLOSED)*
**Decision.** `dsse-envelope@1` deliberately pins no algorithm; the
reference engine pins **Ed25519 (RFC 8032)**, implemented
dependency-free in both validators (pure Python; PowerShell over
`System.Numerics.BigInteger`). Key distribution is authority-local (the
R6 pattern): trusted keys arrive as INPUT (`--trusted-keys` /
`-TrustedKeys` / vector fixtures), never from the bundle being
verified. **Verification mode** (keys supplied): `authority-proven`
additionally requires a VERIFYING envelope — an unsigned attestation
can no longer prove (the P9c-1 forgery closed); structural mode (no
keys) reports `UNVERIFIED` distinctly and grants nothing extra.
**Evidence.** 5 vectors: signed→proven · unsigned-cannot-prove ·
tampered-payload→attestation-binds FAIL · wrong-key→consumer ·
missing-key→unverified-not-proven. Envelope payload = the Attestation's
canonical form; signature input = PAE per DSSE v1.
**Rejected.** Keys discovered from bundle content — the bundle would
attest itself; `.well-known` key discovery stays an Authority-tier
publication duty (D14 territory), not a validator default.

## D3.5-applied — The composition engine *(backlog #18, half 1)*
**Decision.** `--compose A B` implements the D3.5 sentence literally:
facet pins in one major line resolve to the highest pinned minor with
BOTH payload sets re-validated under the winner; major clashes,
non-semver pins, re-validation failures, divergent twins (same
id+version, different semantic digests), and cross-version id
collisions are **reported errors, never silent picks**.
**Evidence.** 7 vectors; real smoke: US.SP800-53 + US.IFA-GoodRead
compose clean (the carried AC-6.1/AC-2 are byte-identical — the
authorization-package pattern holds under composition).

## B.1.8-applied — The conditional-apply engine *(backlog #18, half 2)*
**Decision.** Instances = {instance-id, trigger: exactly one B.2
predicate, enforcement: one instantiated primitive, rationale}. The
one-hop budget is enforced structurally (a two-hop path is an error,
not false); boolean composition is rejected; an unbound trigger
parameter is its own error, never silently false; the FAIL format is
normative and vector-locked. Reference primitives: `param-bounds`,
`code-from` — additions arrive the Ch.15 way. `param-equals` compares
the DECLARED default (bindings live in Implementations; a
binding-aware trigger is an engine extension, recorded as future).
**Evidence.** 8 vectors incl. the CR26 class-deadline pattern and the
normative-format lock.

## R7 — The bidirectional export suite: down-conversion measured *(IV.5.4)*
**Decision.** `export_oscal.py` projects catalog bundles to OSCAL 1.2.2
validated against the OFFICIAL NIST release schema, with a generic
importer and per-object semantic-digest round-trip. Real OSCAL where
OSCAL has the construct (statements→parts, params→params+select,
relations→links, root-Set tree→groups); the D16 props channel
(`https://ns.jascon.net/core`) for what it cannot say —
including Sets in full, because the catalog model cannot represent
overlapping membership (baselines).
**Evidence (measured).** 10/10 catalog bundles schema-valid; round-trip
**5,647/5,647 objects digest-equal (100 %)**. D16 asymmetries measured:
groups cannot mix subgroups+controls (exclusive anyOf — why CIS
contorts sections into controls-in-controls) ×1 wrapper; params require
label|select ×154 synthetic labels; 3 empty groups dropped; NIST's own
JSON schema needs `\p{}` regexes Python's stdlib cannot compile.
**Declared scope.** The catalog graph; Mapping/Tailoring ride the
OSCAL mapping/profile models at a later expansion; the lifecycle bundle
awaits SSP-family exports. Skips counted, never silent.

## R8 — The weekend-validator measurement *(IV.5.4)*
**Decision + evidence.** Second implementation `validate_core.ps1`:
PowerShell 5.1, ZERO installs, a stock Windows box — the auditor's
machine. All 149 vectors pass with full parity to the Python reference
(one authoring-time count divergence, fixed within minutes). Sizes,
one counter (non-blank, non-comment): reference **938** lines Python
(+ jsonschema), weekend impl **1,110** lines PowerShell (+ nothing),
export suite 280 — vs **30,905 lines / 162 files** for
compliance-trestle 4.2.0, the OSCAL 1.x validator+resolver toolchain
(tests excluded) — a ~30× gap with the crypto engines INCLUDED.
**Authorship, honestly:** both implementations by the project author
with AI assistance from the same normative sources; the independence
claim is limited to LANGUAGE and RUNTIME, not authorship — a
third-party clean-room build remains the strongest form and is the
standing invitation. What the measurement DOES establish: the spec +
appendices + vectors suffice to reimplement without reading the
reference (divergences would have surfaced as vector failures), and
the implementation burden is three decimal orders below the 1.x
toolchain.

## Gate-4 backlog dispositions

| Backlog | Disposition |
|---|---|
| #18 | **Close** — both named families delivered with their engines (composition 7 + conditional 8 vectors); B.1.3 negative corpus folded into the lifecycle family's disjointness cases (measured equivalent); DSSE profile verification live (D7-applied) |
| #24 | **Close** — signature verification live behind trusted-key input; unsigned attestations cannot prove in verification mode; prefix-spoof + unsigned negative vectors shipped (dsse family) |

# Amendments — the converter rerun (2026-07-22): the backlog reaches zero

The release-train step the 1.0 decision required: the three
decided-but-undelivered items land in one digest churn across all 11
bundles. **The v0.6 spec-feedback backlog is now EMPTY.** All 149
vectors and all bundles green in both validators after the rerun; the
bidirectional export holds at 5,647/5,647.

## D9 rev 2 — #12 DELIVERED: the `text` primitive is live
**Delivery.** Schema: `langMap` renamed `text`; `title` (base),
`rationale` (Deviation, Mapping, Tailoring excludes), `description`
(Component capabilities, Finding actions) flip from string to `text` =
`{BCP-47: string | [string]}`. Identifiers and labels stay strings by
decision (choice labels were already language-tagged and stay so).
Converters author plain strings; `oscal_conv_lib.textify()` wraps at
write time in each corpus's language (`de` for GS++ and C3A, `en`
elsewhere) — one central point, no per-site edits. Conformance
fixtures and the 13 examples re-shaped; the examples manifest
re-pinned. The reader (v1.6.1) renders `text` via a display accessor
and textifies authored objects at workspace export. The OSCAL export
carries single-language titles natively (+`title-lang`) and
multi-language via the props channel — round-trip stays 100 %.

## C.8/#20 DELIVERED — extension relation types are URI-shaped
**Delivery.** Schema: relation `type` = base codes
(`related · required · uses-term · reference · schema`) ∪ `^https?://`
— a typo'd base code can no longer smuggle as a carried extension.
C5's bare-word `sharpens` ×28 migrated to
`https://ns.bsi.bund.de/c5/rel/sharpens`. Measured on the way (D16):
OSCAL 1.2.2 link `rel` is a TOKEN — URI-typed relation vocabularies
cannot ride links at all; the export carries them on the ordered props
channel (×28, counted).

## D26 DELIVERED — #26: pins are normative, fail-closed, and stdlib pins are verbatim
**Delivery.** Every pinned payload schema now closes its shape
(`additionalProperties: false`) and drops the ILLUSTRATIVE note — the
`cr26/scope` smuggle demo is dead. Stdlib facet ids are pinned
VERBATIM from the normative descriptors (`Bundle.pin_stdlib`), and
both validators enforce it: a pin of a stdlib id that diverges from
the descriptor is an error (the pin-vs-descriptor precedence question
dissolves — they cannot differ). The strict pins immediately earned
their keep: first validation surfaced every undeclared payload key
(cr26 narrative ×6 keys, scope ×4, ifa system ×12, risk ×7, gspp
narrative ×1) — each now a declared contract, none smuggled.

# Amendments — 1.0.0-rc.1 consolidation (2026-07-22)

## The release candidate document
**Decision.** The specification is consolidated into
`drafts/jascon-specification-1.0.0-rc.1.md`: the normative
Parts I–III as amended in place through every cycle, the corpus/coverage
/ledger claims updated from *designed-for* to *measured* where the gates
measured them, IV.5 marked delivered item by item, and the amendment
journals (old IV.6–IV.11) compacted to one history table — the full
journal remains THIS register + git history. The v0.5 file stays as the
bannered working journal. The title page carries the name-pending note;
naming candidates under review: KERN, SCON, CANON, CRUX (author
decides; trademark/domain sweep before the tag).

## D22 (rev 3) — The anticipated-convergence path closes at 1.0, unused
**Decision.** As scheduled by D22 rev 2: the path expires with the 1.0
line. It closes **unused** — zero promotions ever rode it (terminology
landed via the absorption clause). Post-1.0, kernel promotion requires
measured 2-of-3 and a major version under D3.5 governance. Recorded in
the rc.1 spec text (D22, closing clause).

## Naming — JASCON (2026-07-22)
**Decision.** The project is named **JASCON** — **J**SON **A**ttestable
**S**emantic **C**ompliance **O**bject-graph **N**otation; strapline *one
notation for every standard, in every language*. Author's call, from a
collision-scanned shortlist; supersedes the candidate list in the rc.1
consolidation entry above (KERN, SCON, CANON, CRUX — none both scanned
clean and letter-true to the architecture).
**Why.** (1) Every letter is load-bearing: JSON (the encoding, RFC 8785
canonical form), Attestable (two digests, DSSE envelopes), Semantic
(meaning as the contract), Compliance (the domain), Object-graph (nine
shallow objects — documents are renderings), Notation (the honest
heritage of "object notation"). (2) Uniqueness, measured (web collision
scan 2026-07-22): clean in the software/standards/compliance space; known
distant homonyms are an Australian construction firm and a Qatari
engineering company; the nearest software brand is Jasc (Paint Shop Pro,
absorbed by Corel 2004, one letter off). Rejected on measured collisions:
SEMBLE (healthcare EHR), CRAG (Meta's RAG benchmark), GRAPHEME (iChrome
data-viz product), KERNWERK (fitness app, DE ®), GraphSON (Apache
TinkerPop's JSON graph format), COGS (cost of goods sold); the working
title "Semantic Core" is itself established SEO jargon for keyword
clusters — it pointed searchers at the wrong literature. (3) The
strapline's claims are measured, not aspirational: eleven corpora
converted at 100 % coverage; every prose field a language map.
**Scope.** Brand rename across the living documents and the reader
(file renamed `jascon-reader.html`, v1.7.0). Superseded drafts, dated
register entries, review records, and census files retain the working
title as history. **Machine identifiers keep the working-title
string** — namespace URIs, the attestation media type, schema
filenames — for digest stability; their migration is decided with the
`v1.0.0` tag. Trademark screen (DPMA/EUIPO/USPTO) and domain
registration remain on the author's pre-tag checklist.

# Amendments — P10 (2026-07-22): the adversarial review of 1.0.0-rc.1

One review round against the CONSOLIDATED rc.1 text (IV.8 step 2), run
at HEAD `7199c26` under the P9 ground rules: every count recomputed or
git-pinned, demonstrated outranks argued, the four defect classes kept
separate. Method: full recount of every headline number; **both
validators and the export suite re-run at HEAD**; the kernel schema read
field-by-field against Part II; the enforcement code read against the
D10/D13 tables; adversarial constructions run against the reference
validator. Verdict: **no Blockers** — the P9-cycle holes stayed closed;
what P10 found is enforcement completeness at the edges of the D10/D13
tables plus consolidation drift.

## What held (recomputed at HEAD, measured)
149/149 vectors in **both** validators, family-exact (jcs 8 · modality
21 · parameter 17 · tailoring 15 · attestation 5 · facet 7 · reference
11 · lifecycle 36 · tier 9 · dsse 5 · composition 7 · conditional 8);
**11 bundles / 6,675 manifest objects / 251,591 leaves / UNMAPPED 0 —
exact**; SP800-53 115,680 leaves; the CR26 census row exact from the
pinned source (force MUST 189 / SHOULD 84 / MAY 39 / MUST NOT 11 /
SHOULD NOT 5 = 328); export 10/10 schema-valid + **5,647/5,647**
round-trip at HEAD; composition smoke (US.SP800-53 + US.IFA-GoodRead)
clean; tier reporting distinct incl. `rev5-odp-overlay` = consumer (the
anti-laundering result); stdlib-pin VERBATIM enforcement live; decimal
leading-zero rejection live; canonical-alias same-content check live;
LoC counter parity reproduced exactly at the gate-4 commit (`9b953fd`:
938/1,110/280); reader v1.7.0; seven stdlib descriptors; 13 examples;
F.6/F.7/F.8 and C.9 present as cited; the backlog was EMPTY as claimed.
External facts not re-verified this round (register-recorded, quoted
tier): compliance-trestle 30,905 LoC / 162 files; the OSCAL 1.2.2 /
Mapping-Model landscape; the JASCON collision scan.

## Findings — 4 Major · 4 Minor · 1 erratum → backlog #29–#37 (counts in)
- **#29 (Major, DEMONSTRATED)** — facet-op duty enforcement is
  stdlib-only: `pinned_decl` exists but no call site passes it
  (validate_core.py:974; ps1:220 builds only stdlib declarations), so
  detach/attach of a pinned semantics-bearing facet carries no duty; an
  unregistered facet in `attach-facet` gets decl = None → **no** duty —
  D10 dangerous-by-default inverted. A constructed green bundle proves
  it. D13 rev 3's "covers the full D13 table" is hereby narrowed:
  the attach/detach rows enforced for stdlib ids only.
- **#30 (Major, DEMONSTRATED)** — the D13 same-target law lives only in
  the vector runner; bundle validation applies it in neither validator.
- **#31 (Major, DEMONSTRATED)** — selection predicates: schema types
  `selects[].predicate` as ANY object; no shape validation anywhere; the
  B.2 machinery exists (`eval_predicate`) but only conditional-apply
  uses it; zero shape vectors.
- **#32 (Major, DEMONSTRATED)** — five Part II prose↔schema
  divergences: D5 `includes` example; D6 responsibility enum missing
  `inherited`; D6/D8 Implementation.deviations (schema rejects; schema
  instead has Requirement + Assessment, unnamed in D8); D7
  `provenance-map-ref` (schema rejects); D20 example's bare-string
  `rationale` (schema: `text`).
- **#33 (Minor)** — count errata: "twelve corpora" (rc.1 ×3) vs eleven
  everywhere else incl. this register's naming entry; HEAD LoC
  941/1,113/307 vs quoted 938/1,110/280; "**together** ~30×" is ~30×
  **each**, ~15× together; R8 "three decimal orders" false (~1.5); R7
  "×1 wrapper" is 2 at HEAD; IV.5.2 "129 … at HEAD" stale; §2 scope
  statement pre-gate language (CIS "disputed" vs R15 resolved).
- **#34 (Minor)** — D19/IV.8 name-note contradiction: D19 still says
  "final name under review", calls JASCON "the working title", and
  mis-attributes the trademark-OPTICS rationale that belonged to the
  OSCAL-bearing old name (diff 42b4390→7199c26); the open item is the
  trademark screen, not optics.
- **#35 (Minor)** — appendix-D D.7/D.8 "(gate 3)" verification clock
  expired with no recorded verdict while D22 cites `assurance-levels@1`
  normatively.
- **#36 (Minor)** — IV.7 ships no rows/paths for Appendices A–C, the
  handbook, or this register — all cited normatively by the rc.1.
- **#37 (erratum, latent)** — canonical-form residues: `-0` decimals;
  empty `text` values (`{"en": []}`, `""`); bare `"https://"` relation
  codes; float-compare decimal bounds. Zero corpus instances.

**Standing-way note.** rc.1 froze with the backlog empty; P10 refills it
by design; the pre-tag erratum/enforcement pass empties it again. Tag
gate: **#29–#32** fixed (or explicitly waived by the author) before
`v1.0.0`; #33–#37 ride the same pass.

# Amendments — P10b (2026-07-22): the external-review adjudication

A second, independent P10 report arrived on branch `review/p10-gemini`
(commit 57bdb72, "P10 in-depth adversarial design review by Gemini 3.6
Flash", 10 findings G-1…G-10). Adjudicated finding-by-finding at HEAD
under the standing rules — nothing enters the backlog unverified, and
refuted findings are recorded so they are not resurrected.

**CONFIRMED, new → backlog:**
- **G-1 → #38** — corpus directory `geman.bsi` is misspelled and
  off-convention (`CC.NAME` siblings). Rename to `DE.BSI` in the fix
  pass; dated records keep the historical spelling.
- **G-6 → #39** — RequirementSet membership cycles validate green:
  schema cannot see cycles, `closure_errors` checks resolution only,
  and D21 never states acyclicity. Real consumer corpse (baseline
  expansion / nearest-Set search loops). Fix: D21 DAG sentence + cycle
  detection in both validators + vectors.

**CONFIRMED in substance, folded:**
- **G-2 → #37(e)** — `text` keys are case-ambiguous (`en-US` vs
  `en-us`: one BCP-47 tag, two digests — the #27 one-value-one-spelling
  class). G-2's proposed fix (lowercase normalization before digest
  computation) is **rejected**: never-normalize is the D3.4 discipline
  and digest-time rewriting would break every shipped digest. The
  canonical spelling rides the schema (lowercase-only key pattern;
  corpus carries only `en`/`de`).
- **G-7 → #33(a)** — the twelve-vs-eleven corpora count, independently
  confirmed; two reviews now say eleven — unify on eleven.
- **G-8 → #34** — D19/IV.8 stale naming status, independently
  confirmed (P10's #34 additionally records the mis-attributed
  trademark-optics rationale).
- **G-9 → #32(6)** — D9's `prose{lang}` shorthand predates the `text`
  rename; cosmetic wording, same shape.
- **G-10 → #33(e)** — the register's "D26" heading jumps the D-number
  space (no D23–D25 exist; it is backlog #26 wearing a D-label); add
  the editorial note, and retire the stale "(v0.5)" register header.

**REFUTED (do not resurrect):**
- **G-3** ("zero-dependency PowerShell claim inflated — fails on
  non-Windows"): the claim is Windows-5.1-scoped at every occurrence
  (README:14 "on a stock Windows box"; gate-4 §2 "the stock-Windows
  story is the point"; R8 "a stock Windows box — the auditor's
  machine"), and the technical premise is wrong — the script's SHA-2
  comes from the .NET BCL (`System.Security.Cryptography.SHA256/512`,
  ps1:91/448), which is cross-platform in .NET Core; nothing binds to
  Windows CNG. Cross-platform consumers have the Python reference.
- **G-4** ("DSSE verification grants authority-proven without binding
  the key to the authority URI"): misreads the implementation. Trusted
  keys are looked up **by signer URI** (validate_core.py:370), and
  `derive_tier` only considers attestations whose signer origin equals
  the selected content's origin (py:161) — a third-party signer never
  reaches verification for a foreign origin, and a consumer who
  registers a stranger's key under the authority's URI is corrupting
  their own authority-local trust store, which D7-applied/R6 place
  outside the threat model ("keys arrive as INPUT … never from the
  bundle"). No `authority` field exists on Attestation (the report
  cites one), and the shipped `wrong-key → consumer` dsse vector covers
  exactly the described attack.
- **G-5** ("SKILL/handbook naming drift, no old→new mapping"): the
  requested mapping already ships verbatim — SKILL.md's description
  reads 'JASCON (… formerly "Semantic OSCAL" / "OSCAL Semantic
  Core")', which is the **only** occurrence of the old name under
  `semantic-oscal/` (the folder itself renamed to `jascon/` post-1.0.0);
  remaining `semantic-oscal`/schema-filename strings
  are machine identifiers retained by the title-block rule.

**Report-internal errata (for the record):** the report's census table
contradicts the measured bundles and itself — CR26 row "292 Reqs · 91
Sets · 4 Tailorings" vs the measured 306 · 92 · 5 (its own totals line
says 5 Tailorings), and "999 statements" mislabels GS++ (999 source
controls → 651 Requirements + 162 Sets). The P10 recount above stands.

# Amendments — the P10 fix pass (2026-07-22): the backlog empties again

All eleven P10/P10b items closed in one pass; **157/157 vectors and all
11 bundles green in both validators; export 5,886/5,886.** The pass also
falsified a converter: enforcing D21 acyclicity (#39) surfaced a
slug-collision defect in `convert_ism.py` that had silently merged
**239 ISM taxonomy sets** — a bare `[:60]` id cut made nested set slugs
collide, so parents listed themselves as members (the 167 cycle errors
on first run) and colliding siblings overwrote each other in the output.
The ISM re-conversion recovered them: ISM 1,472 → **1,711 objects**
(561 sets), corpus 6,675 → **6,914**, export round-trip 5,647 →
**5,886/5,886**, and the export's ISM `stray-controls` channel went 42 →
**0** — the strays were exactly the orphans of the swallowed sets. The
truncation fix (stable 7-hex hash suffix on over-long slugs) landed in
all four slug implementations (`convert_ism/bsi/cr26.py`,
`oscal_conv_lib.py`); measured: no other bundle carried a truncated id.

Closures:
- **#29** — pinned `modifies-semantics` now feeds the attach/detach
  op-law in BOTH validators (a pin omitting the declaration is
  dangerous-by-default: all four classes); an attach/detach facet id
  that is neither stdlib, nor pinned, nor `private:` is an error at any
  tier. +4 tailoring vectors (incl. private:-is-free).
- **#30** — the D13 same-target law now runs in bundle validation in
  both validators, not only the vector runner.
- **#31** — `selects[].predicate` schema-bound to B.2's three forms
  (exactly one of `field-equals` / `param-equals` / `present`). The
  tier vector that itself carried an invented fourth form
  (`facet-equals`) is corrected — the finding validated against the
  corpus's own vectors.
- **#32** — Part II aligned with the delivered schema: D5 `includes`
  example (URI strings); D6 responsibility enum (+`inherited`);
  Implementation.`deviations[]` decided INTO the schema (the D8/D13
  consumption story needs the ex-post channel on the edge; zero corpus
  objects affected, no digest churn); D7 `provenance-map-ref` added to
  the schema; D8 attachment list corrected (Requirement, Tailoring,
  Implementation, Assessment, Finding); D20 example `rationale` as
  `text`; D9 `prose: text` wording (G-9).
- **#33** — eleven-vs-twelve resolved: **eleven bundles**, with the
  twelve-source-publications convention stated once (§2); LoC restamped
  at the fix pass (994 py / 1,163 PS / 307 export — ≈30× per
  implementation, 31×/27×, ~14× combined; the Status's "together ~30×"
  corrected; the PS twin also gained a per-bundle progress line — a big
  bundle runs minutes with no output and reads as a hang, user report); erratum on R7: the wrapper count is 2 at HEAD (the rerun
  added the CR26 wrapper); erratum on R8: "three decimal orders below"
  was arithmetically wrong — the measured gap is ~1.5 orders (~30×);
  IV.5.2 "at HEAD" → "at gate 3"; §2's CIS clause records the R15
  resolution; the register header renamed + the D23–D25 editorial note
  added (G-10); `gate-4-measurement.md` carries a dated-measurement
  banner.
- **#34** — D19 records the fixed name (JASCON) with the
  trademark-optics rationale correctly attributed to the OSCAL-bearing
  old title; IV.8 steps 1–2 marked done.
- **#35** — appendix-D D.7/D.8 verdict recorded: **parked** beside
  `privacy-assessment@1` (the gate-3 corpus surfaced the need as a
  framework facet — `ifa …/facet/system` — and as levels-as-Sets, not
  as stdlib payloads).
- **#36** — IV.7 now ships rows and repo paths for Appendices A–C, the
  handbook, and THIS register.
- **#37** — canonical-form residues closed in the schema: the decimal
  pattern excludes negative zero (+2 parameter vectors;
  Decimal/`[decimal]`-exact bounds compare replaces float in both
  validators); `text` keys are lowercase-only BCP-47 and values
  non-empty (G-2's substance — the digest-time-normalization fix it
  proposed stays rejected); the relation extension pattern requires
  substance after `https?://`. Scope note, measured: facet-payload free
  text stays descriptor-governed — the 94 empty-prose values in CIS
  `assessment-criteria` payloads are source-faithful facet-space data,
  outside the kernel `text` rule.
- **#38** — `converted_examples/geman.bsi` → **`DE.BSI`** (converter
  output path, README incl. links, reader comment; reader v1.7.1);
  dated records keep the historical spelling.
- **#39** — D21 acyclicity normative ("membership graphs are DAGs");
  cycle detection in `closure_errors` in both validators; +2 reference
  vectors; the ISM recovery above is its first catch.

Refuted stays refuted: G-3 · G-4 · G-5 (P10b entry) — none acted on.

# Amendments — v1.0.0 (2026-07-22): the release

**Tagged `v1.0.0` on the author's go** ("create the 1.0.0 and do a
release"). The spec file promoted in place:
`drafts/jascon-specification-1.0.0.md` (renamed from
`…-1.0.0-rc.1.md`; title and IV.6/IV.8 updated; README and the v0.5
banner repointed). Release notes:
`drafts/jascon-1.0.0-release-notes.md` (doubles as the GitHub release
body; the SKILL zip is the attachable artifact).

**The tag-time decision — machine identifiers remain
in the working-title spelling.** Namespace URIs, the attestation media type
(`application/vnd.jascon.attestation+json` — inside every
DSSE PAE), schema filenames and `$id`s, and the skill's machine name
keep the working-title string. *(The skill's machine name and folder
were carved out of this list post-1.0.0 — see "Amendments — post-1.0.0
(2026-08-06)"; the hashed identifiers below stand unchanged.)* Rationale: identifiers are opaque
strings (D2) — their spelling carries no meaning by the kernel's own
doctrine; the brand lives in prose and filenames of prose; migrating
would churn every digest, every signature, and every pinned manifest in
existence for zero semantic gain — the exact instability the
identifiers exist to prevent. Revisit only with a D3.5 major version,
should one ever exist.
**Customer.** Every shipped bundle, attestation, and third-party pin
stays verifiable forever against 1.0.0 artifacts.
**Simplicity.** One rule: brands may move, identifiers do not.
**Trade-off.** The working-title string outlives the working
title inside URIs — cosmetic, documented in the spec's title block.

Residual on the author (outside the repo): the DPMA/EUIPO/USPTO
trademark screen and domain registrations for JASCON — noted here so
the record shows the tag consciously preceded them. Also noted: the
repository carries **no LICENSE file** — flagged to the author at
release time; a license choice is the author's call and rides a
follow-up commit.

# Amendments — post-1.0.0 (2026-08-06): the skill folder follows the brand

**Author decision: the skill directory and its skill name move to
JASCON.** `semantic-oscal/` → `jascon/`, `SKILL_semantic-oscal.zip` →
`SKILL_jascon.zip`, and SKILL.md's frontmatter `name: semantic-oscal` →
`name: jascon` (heading and the two validator docstring titles follow).
Every path reference in the repo — README, the release notes, the
specification, the gate documents, `.agents/skills.json`, and the
`$SKILL`/`SKILL` constants in `validate_core.ps1`, `validate_core.py`
and `convert_cr26.py` — repointed in the same pass.

**This narrows the v1.0.0 tag-time decision, it does not reverse it.**
That entry listed "the skill's machine name" alongside namespace URIs,
the media type, and schema `$id`s. The four are not the same kind of
thing: a namespace URI, `application/vnd.jascon.attestation+json`
and a schema `$id` are **inside the digested bytes** — PAE payloads,
pinned manifests, signatures. A directory name and a skill invocation
handle are **not inputs to any digest**; nothing verifiable depends on
their spelling. The rule holds where it was load-bearing: *identifiers
that are hashed do not move.* The skill handle was filed under it by
proximity, not by consequence.
**Customer.** The agent-facing surface answers to the name on the box;
`/jascon` is what a reader of the README will type.
**Simplicity.** The old→new mapping still ships verbatim in SKILL.md's
description ("formerly 'Semantic OSCAL' / 'OSCAL Semantic Core'"), and
Requirement 11 now states in-line *why* the schema filename, `$id`,
namespace and media type keep the working-title string — the question a
renamed folder invites, answered where it is asked.
**Trade-off.** Anyone who installed the skill as `semantic-oscal/`
re-installs under the new path; the 1.0.0 release notes now cite
`jascon/` paths that the `v1.0.0` tag itself does not contain.

**Unchanged, deliberately:** the kernel schema filename and `$id`
(`jascon-1.0.0.schema.json`), `https://ns.jascon.net/core`,
and the DSSE payload type. Both validators reproduce the pre-rename
result byte-for-byte modulo the directory name; the rebuilt bundle
carries the same 76 entries.

## The train, complete
Name ✓ JASCON → P10 ✓ → P10b ✓ → fix pass ✓ → **`v1.0.0` tagged
2026-07-22**. The backlog is EMPTY; both validators, the export suite,
and 157/157 vectors are green at the release commit. Post-1.0 work
rides the pending queue (OSCAL mapping/profile exports, SSP-family
lifecycle exports, the clean-room invitation).

# Amendments — CP-RISK-1 (2026-11-10): Risk as the tenth kernel type — landed on a branch, NOT released

**What this section is.** `drafts/CP-RISK-1.md` proposes Risk as a tenth
kernel type (schema 1.1.0), written 2026-11-05 against the synced skill
bundle, without sight of this register, the specification, the corpora
or the PowerShell twin. On 2026-11-10 it was applied to the repository,
reviewed adversarially, corrected, and measured against the first Risk
corpus. This section records that landing. **Nothing is tagged**: one
entry below is an open contradiction with D22 rev 3 that only the author
can close, and the second implementation has not run. The backlog is
open again (#40–#47).

## The landing — what held (measured)
The patch applied without a rejected hunk. Under the 1.1.0 schema **all
6,914 objects of the 1.0.0 corpus match exactly one kernel shape — zero
new failures in eleven bundles**; the proposal's compatibility claim is
measured. Conformance after the landing: **200 vectors in 13 families**
(risk 42: 16 object · 18 bundle · 8 transitions; lifecycle 36 → 37 by the
tenth disjointness case); corpus **6,916 manifest-listed objects** (IFA
15 → 17), ALL GREEN in `validate_core.py` on Linux.

## L-1 — Package digests and line endings: the 1.0.0 corpus did not verify off Windows *(found on the way)*
**Finding (measured).** On a fresh clone under Linux, the 1.0.0
validator reports **6,963 failures, every one a digest-of-bytes
mismatch** (6,914 objects + 49 pinned facet schemas); semantic digests:
0 failures. The manifests digest CRLF bytes — the converters wrote in
text mode on Windows — and git stored the blobs LF-normalised. Every
file matches once `\r` is restored. "Reproduce the whole verdict in one
line" was true on the machine that wrote it and on no other; a `git
archive` of the 1.0.0 commit (what a ZIP download is) fails the same way.
**Decision.** `.gitattributes` gives the bundle directories
`text eol=crlf`, and the converters write that line ending explicitly
(`oscal_conv_lib.BUNDLE_NEWLINE`) instead of inheriting the platform's.
No published digest is re-spelled.
**Verified.** Fresh clones under `core.autocrlf` true / false / input, an
existing Windows-style tree that receives the change, and `git archive`:
6,914/6,914 objects and 49/49 pins each. The converter claim is proven
on the one corpus whose sources were at hand: `convert_ifa.py`, run on
Linux from `usnistgov/oscal-content@9402f031`, reproduces the committed
1.0.0 IFA bundle with zero diff.
**Customer.** Anyone who is not the author. **Simplicity.** One
attributes file; the two-digest design did its job — meaning verified
throughout, only packaging differed — and the validator now says *why*
on such a mismatch instead of printing 6,963 bare lines.
**Trade-off / known limit.** The blobs stay LF, so a consumer that
bypasses checkout (`git show`, raw blob URLs, a client that ignores eol
attributes) still sees a package mismatch: 0/15 on the IFA bundle.
Storing the CRLF bytes as blobs under `-text` cures that channel too
(measured: 15/15; a 6,975-file commit; pack +0.02 MiB) and was not done
because nothing in the repository reads blobs that way and the commit
would bury the review. **Rejected:** re-digesting to LF — it re-spells
6,963 published digests for zero semantic gain, the tag-time identifier
rule applied to bytes. Backlog #42.
**Also:** the skill's example bundle is pinned `eol=lf` (the bytes inside
the skill zip), and its manifest — never verified by either validator —
is now verified on every Python run. At 1.0.0 it could not have passed
on any checkout: 8 of 12 package digests matched CRLF bytes, 4 matched LF.

## CP-RISK-1 review — eight findings, all closed with vectors
Each was demonstrated failing against the validator as proposed
(the current `risk-vectors.json` under the 2026-11-05 validator: 33 pass,
9 fail). Full table: `drafts/CP-RISK-1.md` §11.2. In one line each:
**R-1** RISK-11 failed falsely under a predicate select — now "undecided"
under an open selection · **R-2** a retired or withdrawn Risk justified
its control for ever — only live Risks justify, the rest are `lapsed` ·
**R-3** retiring a risk then dropping its control failed RISK-11
permanently — the rule binds live Risks · **R-4** Set expansion stopped
silently at depth 8 — any depth · **R-4b** RISK-11 was skipped on an
empty selection — applies wherever a Tailoring exists · **R-5** Risk
edges were untyped — **RISK-12** · **R-6** the proposal's `FAIL [RISK-n]`
messages were not implemented and the vectors asserted jsonschema's
wording — rule naming + the portable `expected-rule` · **R-7/R-8**
B.1.9's failure format, a docstring, dead code.
**Customer.** An ISO 27001 auditor asking "which controls rest on no
risk?" must not be answered with a false failure (R-1, R-3) or a stale
yes (R-2). **Simplicity.** One liveness predicate, one typing rule.
**Trade-off.** Under a predicate select the primitive now says less
(a lower bound, an "undecided") rather than more — deliberate: say, do
not guess.

## RISK-12 — a Risk edge is typed *(new rule)*
**Decision.** `treatments[].requirement-ref` names a Requirement,
`component-refs` name Components, and a `Finding.risk-refs` entry that
resolves in-bundle names a Risk (it stays landmark: unresolved is legal).
**Rationale.** Coverage joins on Requirement ids; a Set id in a treatment
passed RISK-7 and resurfaced as a misleading RISK-11. The Mapping
precedent (scopes bind if the endpoint is present) applied to the new
edges. **Scope note.** The older closure rules (Implementation, Finding)
still check resolution only, not target type — unchanged here, an
observation for whoever next touches #16.

## `due` — a point in time is `{type: date | datetime, value}` *(schema, pre-release)*
**Decision.** The proposal's `#/$defs/due` spelled the date branch
`{type: "date", date}`. Zero instances existed; the corpus already
spells Finding action deadlines `{type: "datetime", value}` (×2), and
OSCAL's `deadline` is date-time-with-timezone. The branch now accepts
both kinds under the measured spelling; `Risk.review-due` uses it (×2).
**Not done:** tightening `Finding.actions[].due` to this union — by the
proposal's own compatibility promise that is a *breaking* change
(backlog #47).

## The IFA re-run — the first Risk corpus *(follow-up 2 of the handoff)*
**Delivered.** POA&M risks → 2 Risk objects; Findings carry `risk-refs`;
the `risk-adjustment` Deviation names its Risk (RISK-9 at corpus scale);
the `risk@1` framework facet is retired in favour of a `risk-analysis@1`
holding pen on the Risk; the response `type` prop — dropped by the 1.0.0
conversion — is now the source of `treatment` (`mitigate` ×1, `accept`
×1). 835/835 paths, bundle green, reader v1.7.2 shows them.
**Measured, and it cuts against the proposal's fourth authority.** OSCAL's
risk carries **no owner** (×2 — derived from the imported SSP's `owner`
role, declared), **no level** (×2 — likelihood and impact only, so RISK-2
holds both at `identified`) and **no dated acceptance** (×1 — so the one
`accept` response cannot be written as `retain` under RISK-6; no date was
invented). Of the six fields the proposal says four authorities share,
OSCAL data supplies three. Whether RISK-2/RISK-6 are right to refuse or
one notch too strict for imported data is backlog #43 — the corpus
supplies the counts, not the verdict.
**Source pin.** `usnistgov/oscal-content@9402f031` (2026-07-14), the
state the 1.0.0 conversion fetched. Upstream changed the IFA files on
2026-10-18/22; against current upstream the converter still maps
919/919 paths, but adopting that is a separate measurement.

## L-2 — Path coverage is not value arrival *(found on the way; OPEN, #41)*
**Finding (measured, IFA only).** The coverage reports count source
*paths* that match a rule with a declared destination. They do not check
that the value got there. `oscal_conv_lib.value_arrival()` — added with
this landing and printed in the IFA report — finds that of 835 source
leaf values, 394 occur verbatim in the emitted objects; absent are 194
identity values (uuids/hrefs, re-minted by design), 120
document-metadata values, and **122 content values, 63 of them prose of
40+ characters** (component and implementation descriptions,
observation remarks, POA&M item descriptions, the assessment finding's
own description). Before this re-run the count was 138: under
`poam.risks[]` alone 13 content values had never arrived, the risk
response type among them, while the report read "835 / 835, UNMAPPED 0".
**What this does and does not say.** Some absences are deliberate
transformations (a mapped code, a respelled id); the check cannot tell
those from drops, which is why it lists paths instead of issuing a
verdict. It does say that "converted losslessly, coverage computed
rather than asserted" is established at path level only, for this corpus;
the other ten are unmeasured (their sources are not in the repository).
No headline number was changed here — that is the author's sentence to
re-word once the other corpora are measured.

## ~~OPEN~~ CLOSED the same day — the version number contradicts D22 rev 3 *(#40; decided: 2.0.0 — see "Amendments — the 2.0.0 decision")*
The proposal ships as "1.1.0, minor" on the argument that every
1.0.0-valid object stays valid. This register says, at the 1.0.0-rc.1
consolidation: *"Post-1.0, kernel promotion requires measured 2-of-3 and
a major version under D3.5 governance"* (D22 rev 3), and the
specification repeats it (IV.8: "kernel-shape changes ride major
versions"). Two further points sharpen it: D22's first test asks for
2-of-3 authority encodings **in the census corpus**, and the proposal's
count is of standards, with the one corpus encoding (OSCAL) supplying
half the record; and a 1.0.0 tool cannot read a 1.1.0 bundle that
carries a Risk at all (closed shapes — it reports "matches NO type",
with no version in the message, because nothing in a bundle pins the
kernel version: #44).
**Not decided here.** The two consistent outcomes: (a) the release is
**2.0.0**; (b) **D22 rev 4** amends the rule on the record — e.g.
"a kernel addition under which every previously valid object stays valid
rides a minor; anything else a major" — and says what replaces the
census test for a type no national catalog can encode (a risk register
is consumer-side by nature). The schema file keeps the name the proposal
gave it until then; no tag, no release notes.

## State at the end of the landing
Python reference: 200/200, eleven bundles, ALL GREEN. **PowerShell twin:
ported, not executed** — no PowerShell runtime was available where the
port was written; its header says so, the two new call sites are
guarded, and until it runs green on Windows PowerShell 5.1 the risk
family has one implementation (#45). Export suite: not re-run (its ten
input bundles are byte-identical; the NIST schema it needs is not in the
repository). Handbook, SKILL.md and the skill zip (78 entries) follow
the landed state; the specification file is untouched — it is the
released 1.0.0 text, and what replaces it waits on #40.

# Amendments — the 2.0.0 decision (2026-11-10)

## #40 CLOSED — the kernel that carries Risk is 2.0.0 *(author decision)*
**Decision.** "v2" — the author, 2026-11-10, on being shown the
contradiction recorded above. The release is **2.0.0**, a major version,
as D22 rev 3 and specification IV.8 require. **D22 is not amended.**
Schema file `jascon-2.0.0.schema.json`, `$id`
`https://ns.jascon.net/schema/2.0.0`; the working label
"1.1.0" was replaced in the schema, both validators, the vectors, the
handbook, SKILL.md, the reader and the converter in one pass. It
survives in the proposal's §1–§11 and in the landing record above, both
kept as written.
**A major by rule, a superset in fact (measured).** Nothing in 2.0.0
invalidates 1.0.0 content: all 6,914 objects of the 1.0.0 corpus
validate unchanged, so a 1.0.0 bundle is a 2.0.0 bundle. The reverse
does not hold — a 1.0.0 tool meets a Risk and reports "matches NO type"
— and that asymmetry is what a major number tells a consumer.
**Customer.** A consumer who reads "2.0.0" upgrades the tool before the
data. "1.1.0" on a closed-shape kernel would have promised a forward
compatibility the format cannot give.
**Simplicity.** The rule stands as written: no rev 4, no carve-out.
**Trade-off.** A "2.0" sixteen weeks after 1.0.0.
**What the major opens, and what this entry does NOT take.** The 1.0.0
record tied two things to a major: (1) re-spelling the machine
identifiers ("Revisit only with a D3.5 major version, should one ever
exist") — **unchanged here**; the working-title string stays in namespace
URIs, the media type and schema filenames until the author says
otherwise; (2) tightening `Finding.actions[].due` (#47a) — **not
taken**, so that the superset property stays true. Both windows are open
until the tag.
**Not yet a release.** No tag. Before one: the PowerShell twin must run
(#45), #43 must be decided, and the specification needs its 2.0.0 text
(D4's count, a decision entry for Risk, D14's primitive count, D15's
matrix, IV.1/IV.6/IV.7) — deliberately not written before #43, which
decides normative wording.

## D22-applied — Risk and test 1: an exception on the record, not a pass *(#48 filed)*
D22 rev 3 asks two things of a post-1.0 promotion: a major version — now
met — and *measured 2-of-3*, independent authority encodings in the
census corpus. Risk does not meet the second as written. **0 of the 3
census corpora** (ISM, Grundschutz++, CR26) encode a risk record; the one
corpus that does (IFA, OSCAL POA&M — not a census corpus) supplies three
of the record's six fields. The promotion rests on the author's decision
("kernel type, not facet" in the proposal, confirmed by "v2"), argued
from three standards that prescribe the same record (ISO/IEC 27001 with
27005, BSI-Standard 200-3, SP 800-30). Evidence tier, labeled as house
rule 1 demands: **designed-for, with one partial measurement** — not
*measured 2-of-3*. Tests 2 and 3 for the record: one shared computation
— yes (`risk-coverage`); one vocabulary without flattening — the four
options fit ISO and BSI one-to-one, OSCAL's seven do not (#47b).
**Why an exception and not a quiet pass.** D22 says a promotion "that
cannot show its three passes is rejected without further argument". This
one was admitted by its author against test 1, for a reason the rule did
not foresee: census authorities publish catalogs, and a risk register is
consumer-side data that no catalog publisher ships — test 1 as worded
can never be met by a consumer-side type, whatever the evidence. Whether
D22 should carry a consumer-side clause with its own evidence bar is
**#48**. Until that is decided this entry is the precedent, and it is
exactly one.

## License — Apache-2.0 *(author decision, 2026-11-10; closes the 1.0.0 release note "no LICENSE file")*
**Decision.** The repository is licensed under the **Apache License,
Version 2.0**. `LICENSE` at the root is the canonical text, byte for
byte (apache.org `LICENSE-2.0.txt`: 11,358 bytes, SHA-256
`cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`); a
copy rides in the skill folder, so the installable zip states its own
terms (79 entries). `NOTICE` names the copyright holder and says what
the grant covers.
**Scope — the part that needed care.** The license can only cover what
is the author's to license: the specification, register, handbook,
schemas, vectors, software and reader. The eleven bundles under
`converted_examples/` are conversions of publications by ACSC, BSI, CCB,
CIS, FedRAMP and NIST; `NOTICE` says they stay subject to their
publishers' terms and that the Apache grant adds nothing to those.
**Not done, and it matters.** Nobody has checked those terms corpus by
corpus. Nothing in the repository records the license any source was
published under — not the bundles, not the coverage reports. NIST and
FedRAMP material is U.S. government work; the others are not, and
whether each permits redistributing a *converted* form is unverified.
Backlog **#49**.
**Customer.** Anyone who wants to build on the format now has explicit
copyright and patent grants (Apache-2.0 §2–§3) — the precondition for
the standing clean-room-validator invitation to be taken up by an
organisation with a legal department.
**Trade-off.** A permissive license lets a vendor ship a closed
derivative; accepted — adoption is the point, and the conformance corpus,
not the license, is what keeps "conformant" honest (Ch. 15.1).

# Amendments — the corpus licence review (2026-11-10)

## #49 CLOSED — which converted corpora may be redistributed *(author rule: "keep the code, but remove the results where in doubt")*
**Method.** For each of the eleven corpora: find the publisher's own
statement of terms, in the publisher's own repository, and keep the
converted bundle only where that statement clearly allows redistributing
an adapted form. Everything was read on 2026-11-10. Where no statement
could be found the bundle was removed — absence of a licence is not a
licence.

| Corpus | Publisher's terms — where read | Verdict |
|---|---|---|
| US.SP800-53 · US.CSF · US.IFA-GoodRead | Public domain in the U.S., CC0 1.0 worldwide — `LICENSE.md`, usnistgov/oscal-content | **kept** |
| AU.ISM | CC BY 4.0, © Commonwealth of Australia — README "Copyright", AustralianCyberSecurityCentre/ism-oscal | **kept**, with attribution |
| DE.BSI | CC BY-SA 4.0 — `LICENSE` and README, BSI-Bund/Stand-der-Technik-Bibliothek (the catalogue is in that repository: title confirmed) | **kept**; the bundle is ShareAlike material and is itself CC BY-SA 4.0, not Apache-2.0 |
| FedRAMP-CR26 | **No licence file**; README and AGENTS.md silent — FedRAMP/rules. A U.S. Government work (17 U.S.C. § 105), but without the CC0 dedication NIST adds for the rest of the world | **kept** on the statutory basis; see the next entry |
| CIS.Controls | CC BY-NC-**ND** 4.0; "Terms of Use for Non-Member CIS Products" forbid posting a product on any website and creating derivative works — `LICENSE.md`, CISecurity/CISControls_OSCAL | **removed** — forbidden |
| CIS.Ubuntu2404 | The same Terms of Use cover CIS products; the benchmark's own page was not reachable | **removed** — forbidden / in doubt |
| DE.C5 · DE.C3A | No statement found: not in BSI's CC BY-SA repository; no published OSCAL edition with terms found; bsi.bund.de unreachable from the review session | **removed** — in doubt |
| BE.CyFun | No statement found for the machine-readable form or the third-party resolution converted from; CCB's PDFs carry a plain © notice | **removed** — in doubt |

**What "removed" means.** The bundle and its OSCAL re-export left the
tree; the converter stays; the coverage report stays (source paths, counts
and rules — no text of the publication); a `NOT-REDISTRIBUTED.md` in each
directory gives the reason and the way back. **The measurements stand** —
they were made, and anyone entitled to the publisher's file can remake
them — but they are no longer reproducible *from this repository alone*,
and the README says so where it gives the one-line verdict.
**What "kept" obliges.** Each kept directory carries a
`SOURCE-LICENSE.md`: source, licence with the place it was read, changes
made, no endorsement. `NOTICE` carries the same as a table and scopes the
Apache-2.0 grant to the original work.
**What the shipped evidence base loses.** With the two CIS corpora gone,
no shipped corpus carries Mapping objects except FedRAMP-CR26's 373; C5's
`sharpens` relations, C3A's first use of parameter `label`/`default` and
CyFun's cumulative baselines are measured-but-not-shipped. After this
entry the tree holds six bundles, 4,491 objects.
**Also changed.** Two README screenshots showed CIS content; one was
re-shot on NIST CSF 2.0, the other replaced by the Assess stage on the IFA
corpus (which also shows the Risk type). The reader's Assess view printed
`[object Object]` for an Assessment title since the `text` re-run; fixed.
**Not done — #50.** The removed bundles are still in the git history and
on `main`. Taking them out of the tree stops this branch from publishing
them going forward; it does not unpublish what is already public.

# Amendments — raw blobs (2026-11-10)

## #42 CLOSED — the blobs are the digested bytes *(author: "do it")*
**Decision.** Bundle files are `-text`: git never converts them, and the
blobs hold exactly the bytes the manifests digest (CRLF). The
`text eol=crlf` rule of L-1 is replaced; no digest is re-spelled.
**Why.** L-1 repaired every channel that goes through a checkout and left
one that does not: a consumer reading blobs directly — `git show`, a raw
URL, a client that ignores eol attributes — still received LF bytes and a
package mismatch (measured then: 0 of 15 on the IFA bundle).
**Scope.** The six bundles then in the tree: 4,533 files (4,527 objects
and pinned schemas + 6 manifests), one commit, whitespace-only.
**Verified.** Staged blobs against manifest digests: 4,527 / 4,527. Then,
from the commit: fresh clones under `core.autocrlf` true / false / input,
an existing Windows-style tree that receives the commit, `git archive`,
and raw blob reads — every channel verifies every object.
**Customer.** A reader deep-linked at a raw URL, a mirror, a CI cache —
anyone who never ran `git checkout`.
**Simplicity.** One rule, and the one the two-digest design implies:
delivered bytes are stored bytes.
**Trade-off.** One large mechanical commit; diffs of bundle files show
`^M`. Taken after the licence review on purpose, so that only bundles
that stay were rewritten.

## FedRAMP-CR26 — removed as the doubtful case, in a commit of its own
**Decision.** By the author's rule the FedRAMP bundle goes too. The table
above kept it "on the statutory basis"; this entry takes that back, and
says why the two readings differ.
**For keeping.** It is a publication of a U.S. federal program, and 17
U.S.C. § 105 withholds U.S. copyright from works of the U.S. Government.
The repository's README invites readers to "read, analyze, and integrate"
the dataset.
**For removing.** § 105 is a statute about the United States, not a
statement by the publisher. NIST adds a CC0 dedication precisely because
§ 105 does not reach the rest of the world; FedRAMP's repository has no
licence file at all, and this repository is published from Germany.
"Integrate" is a description of use, not a grant. fedramp.gov and gsa.gov
could not be reached from the review session, so no site-level statement
was read. The rule says: in doubt, remove.
**Cost, stated.** CR26 is one of the three census corpora, the only
shipped corpus with Tailorings (5) and — after the CIS removals — the only
one with Mappings (373). With it gone, **no shipped corpus exercises
Tailoring or Mapping at scale**; the example bundle and the vectors still
do. The README's opening screenshot and its deep link showed CR26; both
now show the IFA lifecycle corpus. The tree holds **five bundles, 3,715
objects**.
**Reversible on purpose.** The removal is one commit touching nothing
else. If FedRAMP states a licence, or the author judges § 105 sufficient,
`git revert` of that commit restores the bundle (as CRLF blobs — the
raw-blob fix was applied before the removal for exactly this reason), its
export, the screenshot and the link.

# Amendments — the Risk rules stay (2026-11-10)

## #43 CLOSED — RISK-1, RISK-2, RISK-3 and RISK-6 are kept as written *(author decision: "keep")*
**The question.** The first Risk corpus (IFA, OSCAL POA&M) showed that
OSCAL's risk data has no owner field, no single level (likelihood and
impact only) and no dated acceptance. Under the rules both risks stay
`identified` although both were analysed, and the one formally accepted
risk cannot be written as `retain`. Keep the rules, or relax them for
imported data?
**Decision.** Keep. Every Risk has an owner (RISK-1); `assessed` and
`treated` require a `rating` (RISK-2); `treated` and `retain` require an
`acceptance` with approver, date and rationale (RISK-3, RISK-6). No
import-only variant, no facet-in-place-of-a-field.
**Customer.** The auditor the type was built for. A state that sometimes
means "has a level" is a state that has to be re-checked every time; the
ISO 27001 clauses behind the rules (6.1.2 c, 6.1.2 d–e, 6.1.3 f) are the
reason the record is kernel at all.
**Simplicity.** One meaning per state, for every bundle, readable without
opening a facet — and no kernel rule that depends on a facet's content
(the layering D10 exists to protect).
**Reasons recorded with the decision.** (1) Asymmetry: loosening a rule
later never invalidates data already written; tightening one later would.
Start strict. (2) Evidence: one fictional example with two risks is a
measurement, not a population; a second corpus (a BSI 200-3 export —
BSI's own `Risikomanagement` catalogue now sits in the
Stand-der-Technik-Bibliothek repository — or a real POA&M) comes before
any change. (3) Nothing is lost: the source status, likelihood, impact
and the response narrative ride verbatim in the `risk-analysis@1` holding
pen.
**Trade-off, accepted.** An OSCAL import looks less mature than it is
until someone adds the level and the acceptance natively. That is the
converter reporting a gap in the source, not repairing it — house rule,
applied to the fourth authority.
**Follow-on.** With this decided the 2.0.0 specification text was written
as a release candidate
(`drafts/jascon-specification-2.0.0-rc.1.md`; since 2026-11-12 `…-rc.3.md`): D23 carries
Risk, the rules and this decision.

## Amendments — the rc.1 review (2026-11-10)

**Trigger.** An external review of the pull request that carries
2.0.0-rc.1 and of the concept as a whole. Nine findings against the
branch, each reproduced before the fix (`drafts/CP-RISK-1.md` §13), and
five observations about the design that no patch answers.

**Decided by the fix (D23, D13).**
- *Who justifies.* A Risk justifies a requirement once it is live,
  published, `assessed` or `treated`, and carries a `treatment` option.
  **Customer:** the auditor who runs `--require-risk-basis` and must not
  be answered by a stub. **Simplicity:** one predicate over four kernel
  fields; no facet is read. **Trade-off, accepted:** every OSCAL import
  justifies nothing until levelled natively — the "rules stay strict"
  decision above, followed through. **Rejected:** `treated` only (the
  decision of 6.1.3 a–b precedes the acceptance of 6.1.3 f); any live Risk
  (the landing — a stub passes).
- *Where.* `tailoring-refs` on Risk. **Rejected:** scoping through
  `component-refs` — a Tailoring names no component, so there is nothing
  to join to; a `component-ref` on Tailoring — the right edge, and a
  change to a released shape (backlog #51).
- *RISK-13, RISK-14, typed selection edges, withdrawn Tailorings and
  Requirements, checked dates.* Each closes a case where the validator
  said less than the text.

**Observed, not decided — the author's.**
1. **No extension point for object types.** Facets attach to existing
   objects; a new *entity* forces a major and, as D22 is worded, an
   exception. Party, Threat, Scale and Evidence are bare landmark URIs
   today and are the next candidates. #48 asks the narrow question; this
   is the wide one.
2. **No type discriminator, no kernel-version pin.** An unknown type and a
   malformed object both report "matches NO type" (#44).
3. **Identifiers under other organisations' domain names**
   (`ns.bsi.bund.de`, `ns.nist.gov`, `ns.cyber.gov.au`, `ns.fedramp.gov`;
   the schema `$id` under `ns.jascon.net`). D2 makes them opaque strings,
   but D13 derives *authority-claimed* from the URI origin, so a
   third-party conversion is authority-shaped until an authority signs —
   and collides or diverges the day the authority publishes its own.
4. **Version numbers.** 0.1 to 1.0.0 in eight days, 2.0.0 as an additive
   superset. Under "closed shapes ⇒ every addition is a major" the number
   stops telling a consumer how much changed.
5. **Prior art.** IV.3 named OSCAL and IR 8477 only. `PRIOR-ART.md` now
   lists the neighbours; Gemara and CycloneDX Attestations are the closest
   and were not mentioned anywhere in the repository.

**Erratum.** This register (D4 note, D20) and the 1.0.0 specification date
OSCAL's Control Mapping Model "March 2026 (v1.2.1)". It shipped with
v1.2.0 in December 2025. The journal above is left as written; the
2.0.0 candidate and the handbook are corrected.

## Amendments — the kernel pin (2026-11-10)

**Trigger.** Backlog #44, and the author's instruction: "add the
kernel-version pin to the manifest."
**Decision (D3.6).** `kernel-version` in the content manifest, optional,
`MAJOR.MINOR.PATCH`. Absent means 1.0.0. KERNEL-1: content beyond 1.0.0
pins the kernel it needs. KERNEL-2: a tool stops at a kernel it does not
implement and names both versions.
**Customer.** The operator of an older tool who is handed a newer bundle
and today reads "matches NO type".
**Simplicity.** One string, two rules, no negotiation: a tool carries the
list of kernels it reads.
**Rejected.** *A required pin* — every 1.0.0 manifest would become
invalid, ending the superset property the 2.0.0 decision kept. *Re-using
`manifest-version`* — the proposal's `"1.1"` was exactly that and was
reverted: it conflates the format of one file with the shapes of all the
others. *Pinning every shipped bundle* — the manifest shape of a 1.0.0
tool is closed, so a pin on the four catalogue bundles would lock out
tools that can read them perfectly well; only the two bundles that carry
a Risk (IFA, the example bundle) are pinned.
**Trade-off, stated.** A 1.0.0 tool still prints no version: it rejects
the pinned manifest as a schema violation. The message improves only from
2.0.0 tools on — the earliest point at which it could.
**Shipped with it.** Schema, both validators (PowerShell by reading, not
executed), `kernel-vectors.json` (9 — the fourteenth family), the
converter library (pins automatically when the content needs it; bundles
without such content reproduce byte for byte), the reader (v1.7.3).

## Amendments — risk catalogues stay outside the kernel (2026-11-10)

**Trigger.** The author's idea of ready-made risk lists that an
organisation imports, the prototype built for it (`risk-catalogs/`), and
backlog #53: does a catalogue entry become a kernel type before the 2.0.0
tag?
**Decision (author).** "Keep outside of kernel." Catalogues, their draft
schema and the import tool stay in `risk-catalogs/`. 2.0.0 gets no entry
type.
**Evidence.** The prototype imported 23 entries into kernel `Risk` objects
and the reference validator accepted the resulting bundle (1,065 pass)
without any kernel change: `Risk`, `relations`, `annotations` and
`tailoring-refs` were enough. A kernel type would have bought digests,
attestation and a typed back-reference for catalogues, and nothing the
import needs.
**Customer.** The organisation that wants a starting list. It gets one
today, and no validator carries an eleventh type for it.
**Simplicity.** The kernel stays at ten types; D22 is not asked for a
second exception.
**Trade-off, accepted.** A catalogue is not a bundle object: it has no
package or semantic digest, cannot be the subject of an Attestation, and
the back-reference from an imported Risk is an untyped `relations` entry
with a URI the validator does not resolve.
**Left open.** Where a recorded "not applicable" for a catalogue risk
lives (backlog #54) — outside the kernel, like the catalogues.

## Amendments — likelihood and impact (2026-11-10)

**Trigger.** The author: "JASCON's kernel Risk has only an opaque rating
{level, scale-ref}; likelihood and impact are deliberately not kernel
fields. Think we need those."
**Decision (D23).** `rating` and `residual-rating` may each carry
`likelihood` and `impact`, each `{level, scale-ref}`. RISK-13 holds a
likelihood or impact carried on both sides to one scale.
**Customer.** Whoever reads a register: the level alone does not say
whether a risk is rare and ruinous or frequent and cheap, and the residual
level alone does not say which of the two the treatment changed.
**Evidence.** ISO/IEC 27001 6.1.2 d, BSI 200-3 and SP 800-30 name the two
inputs; OSCAL's risk characterizations carry them (IFA ×2). Appendix F
Q14 kept them out together with the computation; only the computation
differs by method.
**Simplicity.** No new top-level field; the residual pair comes with the
nesting; the kernel still compares nothing and computes nothing.
**Rejected.** *Top-level fields* — four of them, and a likelihood without
a rating would then be writable, a half-assessed state the rules have no
word for. *Impact per dimension* — a third standard-specific vocabulary;
stays in the facet until a corpus shows one shape. *Checking that the
level follows from the inputs* — that is the matrix, and the matrix is not
kernel. *Letting likelihood plus impact count as assessed* — RISK-2 keeps
its one meaning.
**Trade-off, stated.** OSCAL imports gain nothing: their likelihood and
impact come without a level and stay in the holding facet.
**Shipped with it.** Schema, both validators (PowerShell by reading, not
executed), 6 vectors (risk 73, corpus 240), the example Risk and the
catalogue demo.

## Amendments — scale definitions (2026-11-10)

**Trigger.** The author: "Likelihood should be editable, wording and how
many levels. Same as Auswirkung." Asked where the definitions should
live, the author chose "pinned in manifest" over a new kernel type and
over keeping them outside the kernel.
**Decision (D3.7, D23).** A scale definition is a file the content
manifest pins under `scales`: id, version, and levels listed lowest
first, each a code with optional label and description. SCALE-1/2/3.
**Customer.** The organisation whose method has five likelihood levels
and three impact levels, in its own words — and the reader of its
register, who can now see that.
**Simplicity.** The pin mechanism already exists for facet schemas; the
manifest gains one optional list and the kernel no type.
**Rejected.** *A kernel type Scale* — an eleventh type and a second
exception to D22 for something that needs neither lifecycle nor
attestation of its own. *Outside the kernel* — the kernel validator would
keep treating levels as free strings while the kernel carries the fields
that use them. *A fixed kernel scale* — the request itself.
**Trade-off, accepted.** A scale cannot be signed or superseded on its
own; a new version is a new pin. The order is all the kernel knows: it
does not say how likelihood and impact combine.
**Shipped with it.** Schema, both validators (PowerShell by reading, not
executed), `scale-vectors.json` (9 — the fifteenth family, corpus 249),
three scales in the example bundle, three starting scales in
`risk-catalogs/scales/` pinned by the catalogue demo.

## Amendments — the matrix (2026-11-10)

**Trigger.** The author: "Where does the matrix table itself live? The
kernel deliberately leaves it out, PR #5 assigns it to a facet, and no
such facet is registered. I planned a workspace file outside the manifest
for the first version, which means it is neither digested nor attested."
**Decision (D3.7, D23).** `matrix` is an optional member of the pinned
definition of the level scale. SCALE-4: a rating that states both inputs
states the level of their cell; a mismatch fails (author: "fail on
mismatch"); `override-rationale` on the rating turns it into a note.
**Correction on the record.** "The matrix is the facet's business" (D23
as landed, Chapter 10, Appendix F) named a home that did not exist and
could not: a facet attaches to an object. The sentences are replaced.
**Customer.** The auditor who reads "hoch" beside "selten" and
"begrenzt" and wants to know whether that is the organisation's method
or a slip.
**Simplicity.** No new pin list, no new reference field: the rating's
`scale-ref` already names the file.
**Rejected.** *A workspace file outside the manifest* — undigested,
unattested, and free to change under an accepted risk. *A registered
facet* — nothing to attach it to. *A note instead of a failure* — a
register that contradicts its own table is wrong, not untidy. *A failure
without escape* — an organisation that departs from the table for one
risk would have to falsify an input.
**Trade-off, accepted.** The validator now performs a lookup over
kernel fields, where D23 used to say it computes nothing. It is the
organisation's table, pinned by the organisation; the kernel defines no
matrix. Methods that are more than a table stay facet material.
**Shipped with it.** Schema, both validators (PowerShell by reading, not
executed), 9 vectors (scale 18, corpus 258), a 4×4 matrix in the example
bundle and a 3×3 starting matrix in `risk-catalogs/scales/`.


## Amendments — the example pin (2026-11-10)

**Trigger.** One folder, two verdicts: `validate_core.py jascon/examples`
reported `14 pass, 1 fail` (the D26 line: the pin of
`…/stdlib/facet/assessment-criteria` DIVERGES from the normative
descriptor), the default run reported the same folder ALL GREEN.
**Cause.** The example bundle pinned `assessment-criteria-1.0.0-stub.json`
under the stdlib id — a placeholder from before the normative descriptor
existed, never replaced. `validate_examples()` carried its own copy of the
pin loop and checked existence and digest only; `validate_bundle()` also
applies D26.
**Decision.** The example pins the descriptor **verbatim**: the file is a
byte copy of `schemas/stdlib/assessment-criteria-1.0.0.json`, named
`assessment-criteria-1.0.0.json`. Both passes load pins with one function
(`load_facet_pins`), so the rule cannot be applied in one and missed in
the other. The example pass now also validates facet payloads against the
pins it loads; it had loaded them and applied none.
**Correction on the record.** The stub never had an effect: for a stdlib
id the validator takes the normative schema, whatever the bundle pins. And
the example's own payload did not fit that schema — `summary` was a string
where the descriptor requires an object. It is now a language map; the
assessment's two digests in the example manifest changed with it.
**Rejected.** *Give the stub an id outside the stdlib namespace* — the
example Assessment exists to show the stdlib facet in `method` (Chapter
10); under a private id it would show something else, and the stub was
announced as temporary.
**Open, found on the way.** No validator checks an Assessment's `method`
payload against a facet schema: facet enforcement reads `facets` only. The
mismatch above was therefore invisible to both passes and was checked by
hand. Whether `method` keys must be registered facets is a rule question
(the lifecycle fixtures and two risk vectors use
`"method": {"kind": "review"}`), not decided here.
**Shipped with it.** `validate_core.py`; `validate_core.ps1` gains the
example bundle in its default run through its one bundle path (it had no
example pass) — **by reading, not executed**; example README and SKILL.md;
skill zip rebuilt. Handbook: Chapters 7 and 12 now state the rule, which
stood in the specification and this register only; Chapter 10's
Assessment example carried a `criteria-ref` the descriptor does not have
and shows the shipped payload instead; Appendix D.6 lists the
descriptor's payload completely. Python: 258 vectors, five bundles and the examples,
ALL GREEN, with and without the `jascon/examples` argument.

# Amendments — 2026-11-11: the media type and the schema filenames follow the brand

**Author decision.** The working-title string leaves the repository's
file names and the attestation media type: the kernel schema is
`jascon/schemas/jascon-2.0.0.schema.json`, the drafts under `drafts/`
are named `jascon-…`, and the DSSE payload type is
`application/vnd.jascon.attestation+json`. This takes, for these two
identifiers, the window the 1.0.0 record tied to a major (D3.5) and
2.0.0 left open (IV.9).
**Second step, same day (author decision).** The namespaces follow, onto
`jascon.net`, the domain the author registered for the project that day:

| Before | Now |
|---|---|
| `https://ns.oscal.org/stdlib/…` (stdlib facets, templates) | `https://ns.jascon.net/stdlib/…` |
| `https://ns.oscal.org/compat/oscal-1x` (source-format facet) | `https://ns.jascon.net/compat/oscal-1x` |
| `https://ns.oscal.org/semantic-core/schema/2.0.0` (schema `$id`) | `https://ns.jascon.net/schema/2.0.0` |
| `https://ns.oscal-semantic.org/core` (D16 compatibility namespace) | `https://ns.jascon.net/core` |

Facet ids are inside semantic digests, so every literal digest that
depended on them was recomputed to a fixpoint: object and manifest
digests of the ISM and BSI bundles and the skill examples, check
digests, attestation subject digests, and the content-addressed
evidence records (four renamed to their new digest). Conformance and
bundle counts are unchanged and ALL GREEN; the app suite is unchanged.
A bundle authored against the earlier namespaces has to be migrated
with the table above; its digests change with it.
**Consequence.** The media type is an input to every DSSE signature
(PAE). An envelope signed under the old type no longer verifies and must
be re-signed. The conformance fixture key is now derived from
sha256('jascon dsse fixture key 1'); all DSSE vectors are re-signed, and
`wrong-key-fails-signature` now carries a real signature by a second key
(sha256('jascon dsse wrong key 1')). The schema filename is not hashed;
the app's generated `jascon-schema.js` and both validators follow it.

# Amendments — CP-CHECK-1 (2026-11-12): Check enters the kernel, D22 gains a consumer-side clause

The change proposal `drafts/CP-CHECK-1.md` put seven points to the
author. Six were decisions and were answered on 2026-11-12; the seventh
was a comparison, done the same day (#61, below). This section is the record;
the specification was `drafts/jascon-specification-2.0.0-rc.2.md`
(D24 new; D4, D14, D15, D22 amended) and is, since the next section,
`…-rc.3.md`.

## D22 rev 4 — the consumer-side clause *(closes #48)*

**Author decision, in the author's words.** "Amend D22 with a
consumer-side clause and close backlog #48: a type that catalogue
authorities do not publish may be promoted to the kernel when (a) a
recognised standard of the weight of ISO/IEC 27001, or one of the same
standing, requires the record, or the record is established practice,
shown by at least two independent open implementations whose content was
counted; (b) tests 2 and 3 hold, with test 3 measured on at least one
corpus; and (c) it rides a major. Name the standard or the counted
implementations in the decision register. […] Replace the 'exception'
wording for Risk in the specification by a reference to the clause. Test
1 stays as it is for everything authorities do publish."

**Named, as the clause requires.**

| Type | Branch of (a) | The standard, or the counted implementations | (b) | (c) |
|---|---|---|---|---|
| Risk (D23) | a recognised standard requires the record | ISO/IEC 27001 6.1.2 and 6.1.3; BSI-Standard 200-3; NIST SP 800-30 | test 2: `risk-coverage`. Test 3: four treatment options, measured on the IFA corpus (ISO and BSI fit one to one; two of OSCAL's seven response types have no code) | 2.0.0 |
| Check (D24) | established practice, two independent open implementations, content counted | ComplianceAsCode/content at `f0d40648`, the four CIS profiles for Ubuntu 24.04: 510 rules, 481 fit. aquasecurity/kube-bench at `e278a591`, `cfg/cis-1.12`: 103 automated checks, every operator mapped | test 2: `check-verdict`. Test 3: twelve comparators, measured on both | 2.0.0 |

**Rejected.** A second recorded exception: it would have left D22 a
rule the author overrides, which the proposal's §8.1 called the honest
description of two exceptions in one release. **Scored.** *Customer:*
the organisations that keep a risk register and run checks are the
customers of every catalogue; a rule that could never admit their data
had a blind side. *Simplicity:* one clause, three conditions, each with
a countable answer. *Complexity:* the clause is a second door into the
kernel, and it is narrower than the anticipated-convergence path that
closed unused at 1.0: no anticipation, a named standard or counted
content, tests 2 and 3 in force.
**What it does not settle.** "Of the weight of ISO/IEC 27001" and
"established practice" are judgements. The clause makes them visible by
requiring names and counts in this register; it does not make them
mechanical.

## The six decisions

| Point (CP-CHECK-1 §11) | Decision | Recorded effect |
|---|---|---|
| 2 · D22 | a consumer-side clause | above |
| 3 · run rows | kernel field `Assessment.check-results`, as implemented | none; D24 states the reason (B.4: a facet never defines computation) |
| 4 · `requirement-ref` | resolves if present, as implemented | none; CHECK-1 |
| 5 · timing | "we set it up to become live in 2.0.0" | Check is in release candidate rc.2 and in 2.0.0. No cloud-API census is a condition of the tag. The price is in D24, "Cons, stated": the shape closes on Linux hosts and Kubernetes |
| 6 · quantifier | none added; "record all ressources and their results, present a % of fails and then fail" | B.1.10 step 5: every resource is evaluated; counts and the failing share as a whole percentage; the outcome stays for-all |
| 7 · `not-equals` | added, the twelfth comparator | schema, three implementations, vectors |

**How decision 6 was read.** The row's observation already records
every resource with its facts. The per-resource outcomes and the share
are recomputed from it, as every verdict is (CHECK-9); a stored copy
would be a second thing to hold to the computation. No field was added
to the row. If the author meant a stored per-resource result, that is a
shape change and belongs in before the tag.

**The percentage.** Integer arithmetic, so that three implementations
print one number: `(200·part + whole) div (2·whole)`, clamped to 1…99
while `0 < part < whole`. One failing resource in 300 reads 1 %, 299 in
300 read 99 %. Twelve `share-vectors` pin it.

## What was built and measured on 2026-11-12

- `not-equals`: fits one value of any type; a literal or a parameter;
  `inconclusive` on a missing fact; CHECK-3 refuses it on a list.
- `check_each` / `jscCheckEach` / `Check-Each`: the counts of a
  per-resource check; the first reason of a failing one is the count.
- Vectors: `check` 156 → 188, the corpus 415 → 447. Five deliberate
  breaks of the reference each turn at least one new vector red.
- Python reference: ALL GREEN, 447 vectors, five bundles, the example
  folder. App: its suite green with the same vectors (build 0.9.2).
- PowerShell twin: both changes ported, **not executed** (#60).
- Reader v1.8.0 reads the eleventh type (#57).
- Handbook: chapter 2, chapter 10 §10.7, appendices A (A.9c), B
  (B.1.10), C (C.12 to C.15), F (two questions), G; SKILL.md
  (requirement 9b). Specification 2.0.0-rc.2.

## #61 CLOSED — the grammar against the published RFC 9485

The engines were written from the IETF working group's `iregexp.abnf`
(commit `edceaa5e`), because rfc-editor.org could not be reached. On
2026-11-12 it could. The grammar figure of the RFC (October 2023) and
the group's file are equal line for line except in two rules: the RFC
writes `%x7E-D7FF / %xE000-10FFFF` where the file has `%x7E-10FFFF`
(`NormalChar`), and `%x5E-D7FF / %xE000-10FFFF` for `%x5E-10FFFF`
(`CCchar`), each with the comment "skip surrogate code points". The
group's file is unchanged at `main`, so the difference arose on the way
to publication. The three engines accepted a lone surrogate as a
pattern character; they now refuse it with a message that names the
rule. Five regex vectors: three refusals, the two neighbours of the
block, one character beyond U+FFFF. A pattern with a lone surrogate
cannot stand in JSON text that every parser accepts, so such a vector
carries `pattern-codepoints`. The RFC's additional restriction that
`[^]` is no class was already met. Semantics: the RFC defers to XSD,
which matches the whole string, as the kernel says.
**What it shows.** The difference was invisible to 183 green vectors in
two engines, because both were written from the same file. Only the
published text could show it.

**Open after this section:** #60 blocks the tag. #62: an
`http-api` collector has no declared format, which a runner needs first.

## #60 CLOSED — the twin ran with the changes of 2026-11-12

The three changes of that day (the twelfth comparator, the per-resource
counts, the surrogate rule) were ported to `validate_core.ps1` without a
PowerShell runtime and filed as #60. The same day another session, which
had a Windows machine, merged this state into the advice-pack branch and
ran the twin on Windows PowerShell 5.1: 518 vectors in 17 families,
`check: 188 pass, 0 fail`, the five bundles, the worked pack and the
example folder, bundle by bundle the reference's counts
(`drafts/CP-ADVICE-1.md` §13.4). That run is what #60 asked for. The
header of the twin says so now. Nothing from CP-CHECK-1 blocks the tag
any more.
**What is open instead.** The advice-pack proposal is on `main` as
proposed: its manifest header and one capability field are in the 2.0.0
schema, its eight points for the author are unanswered, the
specification does not describe it, and the app neither ports its rules
nor reads a pack (the app's suite names the family as not ported since
this commit; before, one test failed on `main`, unnoticed because the
advice session had no Node).

---

# Amendments — CP-ADVICE-1 and the decisions before the tag (2026-11-12): advice packs enter 2.0.0, two dates are typed, four open points close

The author's instruction: "I want CP-ADVICE-1 on track for 2.0.0", and
to be asked every open question. Twelve were asked: the eight of
`drafts/CP-ADVICE-1.md` §11 and the four the backlog still held for the
author (#47a with #52, #50, #51, #59). One follow-up settled the shape of
the new field. This section is the record; the specification is
`drafts/jascon-specification-2.0.0-rc.3.md` (D25 new; D3, D5, D6, D8,
D13, D15, D22, D24 amended).

## The eight decisions on advice packs

| Point | Author | What follows |
|---|---|---|
| 1 · the file form | "Bundle only" | A pack is a bundle with a pack header. A bare Component file is not a pack |
| 2 · what a pack holds | "Components only" | ADVICE-1 as proposed. A pack of Checks would be a second `kind` with rules of its own, later |
| 3 · `statement-ids` | "Keep it, I overrule D22 because I see great use for it" | The field is in 2.0.0. The specification records it as entered on the author's word, against D22 (below) |
| 4 · product versions | "A product-version field", then "One opaque string" | `Component.product-version`, a non-empty string. No tool parses, orders or compares it. A Component that carries it needs kernel 2.0.0 (KERNEL-1) |
| 5 · facets in a pack | "Refuse them in a pack" | ADVICE-3 as proposed |
| 6 · membership | "Yes, a rule" | ADVICE-7 as proposed, an error |
| 7 · third parties | "A named relation, defined now" | Stdlib relation type `https://ns.jascon.net/stdlib/relation/describes`: a third party's Component, under its own origin, points at the vendor's Component. Carried and shown, computed by nothing |
| 8 · earlier releases | "One release per set" | ADVICE-10 as proposed |

## D22 — two fields on the author's word

**What the tests say.** `statement-ids` on a capability and
`product-version` on a Component are consumer-side data. Test 1 fails:
no census authority publishes them. The consumer-side clause of rev 4
is written for types and, read for a field, is not met either: no
standard is named, and the counted content is one fictional component
definition by NIST with two clause-level entries. For `product-version`
nothing was counted.
**What was decided.** The author keeps `statement-ids` against the
drafter's recommendation to wait for a census, and adds
`product-version`. The specification says so in D22 under "Applied at
2.0.0-rc.3" and does not present either field as passing a test.
**Why this is recorded as an override and not as a new clause.** One
decision by the author about two optional fields is no pattern. A clause
written from it would admit any field anyone finds useful. If a third
field arrives the same way, the question of a clause is due.
**Cons, stated.** D22 exists to keep the kernel from growing by
plausibility. Both fields are plausible and unmeasured. What could
repair that: a census of public component definitions (CP-ADVICE-1
§2.3), which nobody has run.

## The four decisions before the tag

| Item | Author | What follows |
|---|---|---|
| #47a · #52, the two date fields | "Tighten both now" | `Deviation.opened` is a date (`YYYY-MM-DD`); `Finding.actions[].due` is one of the four typed forms that `review-due` of a Risk already uses: `date`, `datetime`, `elapsed-duration`, or `calendar-period` with its calendar. Refusals are named DATE-1 and DATE-2. The sentence "every 1.0.0 bundle is a 2.0.0 bundle" no longer holds as a property of the schema: it is now a measurement on the five shipped bundles and the example folder, whose five `opened` values and whose `due` values conform |
| #50, the removed bundles | "Leave history as it is" | No rewrite. Old commits and the `v1.0.0` tag keep the six bundles; every commit id this register cites stays valid |
| #51, a Tailoring's scope | "No, keep the model" | A Tailoring names no Component. Spec D13 says where scope is recorded instead |
| #59, Unicode categories | "Follow the host, and say so" | No pinned Unicode version. Spec D24 names the consequence and the way around it |

**Why 2.0.0 is the place for the date change.** Typing a released
free-text field is a breaking change and rides a major. 2.0.0 is that
major and is not tagged; after the tag the same change would need 3.0.0.
**What it costs.** A tool that wrote "Q3" or "next audit" into either
field under 1.0.0 has to convert the value before its bundle validates
under 2.0.0. The error names the rule and the field. No such bundle is
known; none of the shipped ones is affected.

## What was built and measured on 2026-11-12

- **Schema 2.0.0**: `component.product-version`; `finding.actions[].due`
  and `deviation.opened` typed.
- **Reference validator**: KERNEL-1 for `product-version`; DATE-1 and
  DATE-2 named when an object matches no type; a runner for
  `shape-vectors`. **537 of 537 vectors in 17 families** (`kernel` 11
  → 25, `advice` 71 → 74), the five bundles, the worked pack and the
  example folder, ALL GREEN.
- **Vectors**: two for the pin, fourteen for the shapes, three for a
  pack with `product-version` and for a third party's pack with and
  without an id of its own origin.
- **Mutations**: 28 of 28 in the advice rules still turn a vector red
  (`drafts/cp-advice-1/mutate.py`); removing the pin for
  `product-version` turns one kernel vector red.
- **Worked pack**: the vendor's Component carries `product-version:
  "7"`, so its semantic digest, the pack's manifest, the kept manifest
  (`packs/sha256/27bed546…`, before `433f4124…`) and the Attestation
  were regenerated by `build_example.py`. The signing key is the public
  fixture key, as before.
- **PowerShell twin**: ported without a runtime and filed as #63, then
  executed the same day (next section).

## #63 CLOSED — the twin on Windows PowerShell 5.1, on every change

**What was done.** The port of the three changes was first executed
under PowerShell 7.4 on Linux, with a stand-in for
`JavaScriptSerializer`, which exists only in the .NET Framework: 537 of
537, ALL GREEN, and two deliberate breaks of the new lines turned four
kernel vectors red. That run shows the port is exercised. It is not the
runtime the twin is written for.
**The run that counts.** A workflow, `.github/workflows/validators.yml`,
runs `validate_core.ps1` on a hosted Windows runner with `powershell.exe`,
which is Windows PowerShell 5.1. First run, commit `5a75454b`: 537
vectors in 17 families, `kernel: 25 pass`, `advice: 74 pass`, the five
bundles, the worked pack and the example folder with the reference's
counts, ALL GREEN in 64 s
(https://github.com/christoph-puppe/JASCON/actions/runs/43204019670).
**Why a workflow and not one more manual run.** #45, #56, #60 and #63
were the same item four times: a port written without a runtime, waiting
for someone with a Windows machine. The workflow runs the Python
reference, the twin and the app's port on every change to what they
read. A port that was never executed can no longer reach `main`
unnoticed.
**Cons, stated.** The measurement now depends on a hosted runner image
that GitHub changes over time. The summary of each run names the
PowerShell version it found; the job fails if it is not 5.x.

## The app and the reader, and what building them changed

App build 0.9.3 ports ADVICE-1 to ADVICE-11 (74 vectors, 115 tests in
its suite) and imports, replaces, refuses and adopts; reader v1.9.0
shows packs and runs no rule (`drafts/CP-ADVICE-1.md` §14.3;
specification IV.7).
**Three states on a screen, two in the rules.** With no trusted key, an
Attestation that binds a pack's manifest was printed as PROVEN with the
word UNVERIFIED behind it. On a screen that is a green word over an
unchecked signature, and such an Attestation costs nothing to forge.
D25 now names a third display state, *attested, not verified*; the
validators print it, the result values and the vectors stay as they
were. **Rejected:** a third result value in `pack_publisher`. It would
change eight vectors and the tier rule's vocabulary for a distinction
that only matters where a person reads the output.
**A defect in the reference.** `validate_bundle` read attestations
beside the manifest only for a pack's own manifest, so a set that kept a
pack reported its publisher as claimed although the vendor's Attestation
lay beside it. Found by the app's port, which reads every attestation
of a set; fixed in both validators.

**Open after this section.** Nothing blocks the tag, and nothing is left
for the author to decide before it. Four choices the app made are listed
for confirmation in `drafts/CP-ADVICE-1.md` §14.3. Work that does not block: #41, #46,
#47b, #54, #55, #58, #62, #64.

## Census of NIST's example component definitions (2026-11-12)

**What was done.** The four JSON component definitions NIST publishes in
`usnistgov/oscal-content` (commit `f0de6d8d`, two distinct definitions and
their minified twins) were run through the pack builder's import, with and
without the SP 800-53 catalogue (`drafts/cp-advice-1-census/`, by the
builder's own code in Chromium).
**What it found.** Five things the first version of the import got wrong or
kept quiet about: every `source` is a `#uuid` into the back-matter (0 of
10 implemented requirements resolved without a catalogue); one file cites
the Rev 4 catalogue and a FedRAMP Rev 4 baseline, whose ids the Rev 5
conversion does not share; texts carry `{{ insert: param, … }}` markup;
parameters use Rev 4 ids; one control is implemented twice. Builder 1.2.0
reads the back-matter (10 of 10 resolved), rewrites the markup, counts
FedRAMP baselines as SP 800-53 sources and names the rest in its report.
Each fix has a test and a deliberate defect that turns it red.
**What it does not change.** D22's record for `statement-ids` and
`product-version`. The clause-level evidence is the same MongoDB example
counted before (2 clause entries, 2 values); NIST's second example carries
neither, and no file carries a product version. Both are examples by the
format's maintainers. The census that could change D22 is of component
definitions vendors published, and it is still owed (CP-ADVICE-1 §2.3).

# Amendments — 2026-11-12: the packed lists (the "216" withdrawn)

**What was wrong.** Since the census of 2026-07-03 the project counted 216
prop values in the BSI corpus (213 in Grundschutz++, 3 in MS-TLS) as
"pseudo-placeholders": `{{einem anerkannten Standard}}` in a `result` or
`result_specification` prop, read as free text imitating parameter syntax.
The handbook, the website, the README, the specification's principles and
the converter's coverage report carried the number, and the validators
named the `{param:}` binding check "the 216 rule". The author pointed out
that these are valid parameters.
**What the source says.** Checked on the catalogue of 2026-07-16 (the one
the shipped bundle was converted from), on the census snapshot of
2026-07-03 and on the build of 2026-10-29: all `{{…}}` slots in the
sentence-template props (221 in Grundschutz++ of 2026-07-16, 3 in
MS-TLS) stand exactly where the statement prose of the same control
inserts a parameter with `{{ insert: param, … }}`; 219 of the 221 repeat
the label of that parameter, two (GC.1.1, NOT.1.1.4) use other wording at
the same place. The sentence template marks its parameter slots by label.
They are parameters, not defects, and there is nothing to report.
**The real defect.** Several props hold a list of vocabulary terms and
pack it into ONE comma-separated string instead of repeating the prop (the
OSCAL form) or using an array (the JSON form): in the catalogue of
2026-07-16, 125 of 470 `tags` values (`"Data Leak, Shadow IT"`, ASST.3.11),
616 of 900 `threats` values (`"G 0.18, G 0.30"`) and 40 of 634
`target_object_categories` values — 781 in all. Each is a well-formed
string, so no OSCAL validator sees the list, nothing checks its terms
against the CSV vocabulary, and every consumer has to know from outside the
document to split. The converter already split them (a declared rule) but
never counted them as a finding. Recounts: census snapshot 2026-07-03 —
125 of 468 `tags`; build 2026-10-29 — 125 of 470 `tags`, 635 of 901
`threats`, 39 of 636 `target_object_categories`.
**What changed.** `convert_bsi.py` reports the packed lists per prop and
checks every `{{…}}` slot against the prose (a slot away from an insertion
would be reported; there is none); the coverage report is regenerated, the
bundle is byte-identical. The app's BSI import does the same (build 0.9.4,
`jascon-app/ERRATA.md`), with the counts in its test. The binding check
keeps its rule and its predicate name, `prose-params-resolve`, in all five
implementations; NIST's "216 per-statement rule" is the per-statement
parameter rule. The handbook (ch01, 02, 04, 07, 12, 14; appendices A, B,
D, E, F, G), the website, the README, rc.3's principles and the source
licence note now cite the packed lists; ch01 and §14.5 say what was
wrong. The 1.0.0 specification and the deep-research review carry an
erratum note; the historical drafts (v0.5, the gate-3 census and plan,
the prop census r2) and the entries above stay as written and are
corrected by this section — including "the 216-defect class" under D9,
"216 pseudo-placeholders" in "The structurally-dead category" (they are
carried as published in `statement-grammar@1`, not made dead) and "the
216 per-statement rule" in the NIST findings.
**What it does not change.** No kernel shape, rule or vector. The bundle's
objects and digests are unchanged.
**Lesson, for §14.5.** A finding about a source is tested against the
source's own notation before it goes to the authors' queue. This one was
not, for four months.

# Amendments — the outside reports of 2026-11-13: four gaps in the run rules

On 2026-11-13 eight issues arrived in the GitHub tracker of the
repository from one outside reporter, written against commit `9e84c2ca`:
five defects (issues 23 to 27) and three requests (28 to 30). GitHub's
numbers are not the numbers of the backlog. This section records the four
defects in CHECK-12, CHECK-13 and CHECK-15. The fifth, the number domain,
is backlog #67 and has its own entry when it closes.

## What was reported, and what the reproduction showed

All four were reproduced on the reference validator before anything was
answered, each on the conformance vector "CHECK-15 satisfied: row ->
record -> raw output, every digest verifies":

| Issue | The reference accepted | The rule as written |
|---|---|---|
| 23 | an evidence record at `alternate/<hex>`, its digest intact | CHECK-15: evidence references stay in the store, `evidence/sha256/<hex>` |
| 24 | `collector-id: "bash"` on a row whose Check has no `collector@1` | CHECK-13: the id names a collector of the Check |
| 25 | `"unbound-extra": 999` among a row's `parameters` | CHECK-12: the row's parameters equal what the Tailoring binds |
| 26 | a record without `observation-digest` on a row with an observation | CHECK-15: the record binds the row's observation |

None of them changes a recomputed verdict or lets a digest pass that
does not verify. Each lets a run record claim something no rule holds it
to, inside the digest an Attestation signs.

## The author's decisions (2026-11-13)

1. **Issue 23.** A relative reference is `evidence/sha256/<hex>` or it
   fails. A reference with a URI scheme stays a note: it was in the code
   and pinned by a vector, and the specification now says so.
2. **Issue 24.** A Check without the facet declares no collector. A
   runner that brings its own collector leaves `collector-id` out.
3. **Issue 25, wider than asked.** A row names only parameters its Check
   reads, with or without `tailoring-ref`. The report asked for the case
   with a Tailoring. A name no assertion reads cannot be verified in
   either case, and two tools would record one run with two digests.
4. **Issue 26, in both directions.** A row with an observation needs a
   record with its `observation-digest`; a row without one needs a record
   without. The second direction was not reported and is the more serious:
   a failing observation could be dropped and the run reported as
   `inconclusive` while the record showed that something was observed.
   `observation-digest` stays optional in the schema, because a run that
   observed nothing has nothing to digest.
5. **The collector, found while testing issue 24.** A record that names
   a collector on a row that names none passed. Row and record now name
   the same collector, or both none. Closed with issue 26.

## What changed

- `validate_core.py`, `jascon-rules.js` (app build 0.9.5, and the pack
  builder's inlined copy), `validate_core.ps1`: the four rules and their
  messages. The twin was ported without a runtime; a PowerShell runtime
  could not be installed in the session that wrote it, so its run is the
  workflow's: Windows PowerShell 5.1 on a hosted runner, commit
  `33901767`, `check: 199 pass, 0 fail`, the bundles, the pack and the
  example folder with the reference's counts, ALL GREEN in 183 s
  (https://github.com/christoph-puppe/JASCON/actions/runs/43423027413).
- `check-vectors.json`: 188 → **199**, eleven bundle vectors (44 → 55).
  Ten fail on the reference as it was. The eleventh is the legitimate
  case: a run that observed nothing, with a record that binds nothing.
- Specification: CHECK-12, CHECK-13, CHECK-15 and the evidence paragraph
  of D24, amended in place with the date. Handbook: Chapter 10 §10.7,
  Chapter 12 (the fourth and fifth sitting, with a "Don't"), Appendix A
  (A.7, the evidence store), Appendix B (the rule table), Appendix D
  (`collector@1`). `jascon-app/ERRATA.md` has the entry.

## What it does not change

No shape and no schema. No shipped object: the five bundles, the worked
pack and the example folder pass as before, because none of their rows
carries an unread parameter, an undeclared collector, a reference outside
the store or a record that disagrees with its row (scanned before the
change, validated after it).

## Open after this section

Backlog #67 (the number domain; blocks the tag by the author's word of
2026-11-13). Issues 28 to 30 are requests and were answered in the
tracker: history for the manual check and a read-only comparison of runs,
a coverage view built from existing primitives, and the runner of
CP-CHECK-1 §9 phase 2, which follows the fixes.

## Lesson

The three engines agreed and all three were wrong, because two are
ports of the first. Agreement between ports measures the port. What
found the gaps was a reader holding the code to the sentences of the
rule table: "equal" means the key sets too, and "names a collector of
the Check" has an answer when the Check has none. Every negative vector
before this day changed a value; none removed a field or added a key.

# Amendments — the number domain (2026-11-13): D3 item 9, NUMBER-1 (#67 closed)

The fifth of the outside reports of 2026-11-13 (issue 27 in the GitHub
tracker of the repository; not #27 of the backlog) was filed as a defect
of `check-verdict`. Reproducing it showed a hole in D3.

## What was reported, and what the reproduction added

Reported: a Check that expects `9007199254740992`, on an observation of
`9007199254740993`. The reference says `not-satisfied`; the app says
`satisfied`, because `JSON.parse` rounds the fact to the expected value.

Found while reproducing it, same JSON text in both engines:

| Input | Reference (Python) | App (JavaScript) |
|---|---|---|
| `1.0` or `1e3` on an `integer` fact | `inconclusive` | `satisfied` |
| canonical form of `{"n":9007199254740993}` | `…993` | `…992` |
| canonical form of `{"n":1.0}` | `{"n":1.0}` | `{"n":1}` |

So the defect is not in the tenth primitive. Every integer of the kernel
had two readings, and with them every semantic digest that covers one: an
Attestation could verify in one tool and fail in the other. D3 item 3 has
said since v0.5 that the vectors cover "the permitted number domain". No
text defined a domain, and `jcs-vectors.json` held no number. The comment
on `jscCanonical` in the app claimed the two engines "agree on everything
the schema allows"; the schema type `integer` allows `1.0` and any size.

## The author's decisions (2026-11-13)

1. **Declare the domain.** A JSON number in a bundle is an integer of
   magnitude at most 2^53 − 1. Not taken: exact integer parsing in the
   app. It needs a parser of its own in every JavaScript tool and goes
   against RFC 8785, which rests on IEEE doubles.
2. **One spelling: plain digits.** `1.0`, `1e3` and `-0` are refused.
   The first answer in the tracker had `1.0` read as the integer 1 and
   written `1` in the canonical form, as RFC 8785 serialises it. That is
   a rewrite at digest time. This register rejected exactly that for
   #37(e): "never-normalize is the D3.4 discipline", and the canonical
   spelling is held by validation. There is a second reason. A reading by
   value depends on how each engine turns a text into a float: Python and
   JavaScript read `0.99999999999999999` as 1, and the twin's parser
   is expected to return a decimal that is not 1 (inferred from how that
   parser types numbers; not run). A rule on the text has no such edge. The answer
   in the tracker was amended, with the reason.
3. **The whole file, annotations included.** The rule exists for digests
   and verdicts, and annotations are in neither. It still covers them,
   so that a tool can check a file without knowing where annotations
   are, and so that five engines implement one pattern. A fraction in an
   annotation is written as a string.
4. **It blocks the tag.** After 2.0.0, narrowing the domain would change
   which objects are valid.

## The rule

D3 item 9. **NUMBER-1:** a JSON number is an integer in plain digits, of
magnitude at most 2^53 − 1 (9007199254740991): no fraction, no exponent,
no `-0`. It holds for the content manifest, every object, every pinned
definition, every evidence record and observation file. It is refused,
never rewritten. A quantity that does not fit is a `decimal`, a string,
which the comparators compare exactly. D24, evaluation step 3: an
`integer` fact outside the domain is mistyped, so `check-verdict` is
`inconclusive` in every engine.

Two checks in every engine, because a parser forgets the spelling: the
text of a file where it is read, and the value of an object wherever it
is held without its text. Which one does the work differs by language.
JavaScript sees neither `1.0` nor `-0` after parsing and needs the text
for both. Python keeps `1.0` as a float and needs the text only for
`-0`. The pattern is the same in all: strings are consumed whole, the
remaining number tokens are compared as text, and no float takes part.

## What changed, and what was measured

- `validate_core.py`, `validate_core.ps1`, the app's `jascon-rules.js`
  (build 0.9.6; the pack builder carries the same code), the reader
  (v1.10.0, on the files it verifies). The canonical form is unchanged in
  all of them: inside the domain they agree without help.
- Vectors: `jcs` 8 → **22** (14 `number-text` vectors, which carry JSON
  texts, because a vector file cannot hold `1.0` as a number: the
  harness's own parser would have read it), `parameter` 19 → **21**,
  `check` 199 → **203** (three verdicts, among them the reported pair, and
  one bundle with an observation file that writes `4.0`). **568 vectors
  in 17 families.**
- Deliberate breaks of the reference: accepting `-0`; a range one wider;
  an integer fact without the range; an integer parameter without the
  range; a tokenizer that looks into strings; evidence files left out.
  Each turns at least one vector red. A seventh, accepting a fraction in
  the text, stays green in the reference, where the value check catches
  the float; the app's test "JSON.parse alone would let every spelling
  and the reported integer through" covers it where it matters.
- Shipped content: no object changes. Before the rule was written, a
  scan of 3,871 JSON files found 11 numbers outside the domain, all
  `coverage-pct: 100.0` in the converters' coverage reports, which are
  not JASCON objects. With the rule on, the five bundles, the worked pack
  and the example folder validate as before.
- The PowerShell twin, ported without a runtime, ran on Windows PowerShell 5.1 on a hosted runner at commit `30892353`: 568 vectors in 17 families (`jcs: 22`, `parameter: 21`, `check: 203`), the five bundles, the worked pack and the example folder with the counts of the reference, ALL GREEN in 118 s (https://github.com/christoph-puppe/JASCON/actions/runs/43426147785).
- Specification D3 (items 3 and 9) and D24; handbook Chapters 10, 11 and
  12 and Appendices A, B, C and G; SKILL.md, whose vector count had
  stood at "258 in 15 families" since rc.1; the app's errata.

## Cons, stated

- A tool that writes JSON through a float type (`json.dumps(1.0)`, and
  the defaults of several languages) now produces invalid bundles. That
  is the point of the rule, and it will be met in the field.
- A JavaScript tool cannot enforce the rule on parsed values alone. It
  has to keep the text, or accept that it checks the range and not the
  spelling.
- An annotation cannot hold a fraction as a number.
- The rule is not expressible in JSON Schema, so the kernel schema does
  not carry it; it is a rule of the validator, like empty-omission.

## Lesson

The reference and its port agreed on every vector for four months. They
were tested against one another, with vectors that held no number larger
than a sequence. A sentence in the specification promised a domain and a
vector for it, and nobody had held the corpus to that sentence. The
report came from someone who asked what the schema allows instead of
what the examples contain.

# Amendments — the value-level check of the converters (2026-11-13): #41 re-planned

Two more reports from the same outside reporter, issues 32 and 33 in the
GitHub tracker, both about `oscal_conv_lib.value_arrival()`: the helper
behind L-2 above and the sentence "394 of 835 leaf values occur verbatim"
in the IFA coverage report, on the website and in backlog #41. Neither
touches the kernel, a validator or a bundle.

## Issue 32 — the helper counted what had not arrived

`value_arrival()` joined every output key and scalar into one string,
turned every scalar into text, left nulls out and tested substring
membership. Six one-leaf cases, reproduced as reported:

| Source | Output | Old result | Why |
|---|---|---|---|
| `"open"` | `"not-open"` | arrived | a substring of another value |
| `1` | `10` | arrived | a number as text, inside a longer number |
| `true` | `"true"` | arrived | a boolean as text, against a string |
| `"alpha\nnext"` | value `"alpha"`, key `"next"` | arrived | the match spans two tokens across the joining newline |
| `""` | no output | arrived | the empty string is in every string |
| `null` | `null` | absent | nulls never entered the search text |

Five of the six make the figure too high. Class: algorithm. The helper
had no test; it was written during the CP-RISK-1 landing to expose a
weakness of the path-level reports and was itself never held to a case
with a known answer.

## Issue 33 — what no global check can show

All sources and all emitted objects share one search space, and one
output value satisfies every equal source value. Two controls with the
same description, the second dropped: 4 of 4 arrived, nothing absent. The
reporter is exact about it: the helper did what its docstring said, and
the fault is in the words around it. `convert_ifa.py` called the result
"how many values actually got there" and the report called its absent
list "the work queue". Backlog #41 planned to wire this helper into every
converter and to re-word "converted losslessly" from it. That plan would
have replaced one overstatement with another.

## The author's decisions (2026-11-13)

1. **Exact, typed, whole values.** Strings, numbers, booleans and null
   match only their own type and only as a whole.
2. **Keep what a substring match knows, apart.** A value that occurs
   only inside a longer output text (a remark appended to a description)
   and a value that equals only an output key (a prop name that became a
   facet key) are listed as candidates and not counted.
3. **Name the measure for what it is.** `global_occurrence()`. Its count
   is an upper bound on what was carried; its absent list is a lower
   bound on the losses and not the complete queue. Diagnostics keep the
   array index (indexed JSON Pointers).
4. **Correct the figure where it is published, then measure again.**
5. **A ledger of source occurrences is the measurement a lossless claim
   needs**: one entry per source leaf with its destination and outcome.
   The IFA converter first; the others corpus by corpus. Not taken: a
   count of occurrences on both sides. It would flag the fixture without
   saying which occurrence is gone, and every legitimate deduplication
   would read as a loss.
6. **Tracked in #41**, re-planned, not in a new entry. **It does not
   block the tag**: no kernel rule depends on it.

## What changed, and what was measured

- `oscal_conv_lib.py`: `value_arrival()` is `global_occurrence()`.
  `test_oscal_conv_lib.py`, twelve tests named after the two issues, among
  them one that asserts the known limit (the dropped description still
  reads 4 of 4); the workflow's Python job runs them.
- The IFA sources were fetched again from the pinned commit
  (`usnistgov/oscal-content@9402f031`, seven files). **The unchanged
  converter first reproduced the committed bundle and both reports byte
  for byte**, 394 of 835 included, so the re-measurement is of the same
  input.
- Re-measured: **283 of 835** source leaf values have an equal typed
  value somewhere in the bundle. 29 equal only a key of the output, all
  of them prop names under five paths; whether such a name became that
  key is for the ledger to say. 80 occur only inside a longer text. Without any equal: 194 identity
  values, 125 document-metadata values, **124 content values, 63 of them
  prose of 40 characters or more**. The old reading was 111 too high.
- The bundle is unchanged: 17 objects, the same digests. Only the two
  coverage reports differ.
- Corrected where the figure stood: the IFA coverage report, the website
  (`evidence.html`, in five languages), specification R16, IV.5b item 6
  and IV.7, backlog #41.
- L-2 above and backlog #41 said 120 document-metadata values were
  absent. The generated report said 125, and 394 + 194 + 125 + 122 is
  835; 120 was a slip in the prose. L-2 stays as written and is corrected
  by this section.

## The ledger, and its first run (the same day)

**How it works.** `oscal_conv_lib.Ledger` does not search for values. A
converter loads its sources through it, and every string and integer leaf
then carries its origin (document and indexed JSON Pointer) for as long
as the converter hands it on unchanged. After the bundle is written,
every output leaf and every output key that still is such a value is a
copy with a known source and a known destination. Any computation
returns a plain value and so loses the origin by itself; the converter
states those at the place they happen, with `derive(rule, function,
inputs)`, and the ledger applies the function to the source again and
compares. A deduplication is declared with `same(dropped, kept, rule)`
and holds only if the two are equal. A drop is declared with a pattern
and a reason. Every entry is checked against the files on disk. What is
left is `unaccounted`. Tracing is by object identity, so an equal value
elsewhere cannot stand in for a lost one: the reporter's fixture names
`/controls/1/description`, with an unrelated equal value and an equal
key in the output, and is a test.

**What it cost.** The IFA converter keeps its structure: one changed
loader, 22 places where a computed value is now stated with its
rule, one `same()` at the existing deduplication, one declared drop. The
bundle and its manifest are byte for byte what they were.

**First run, IFA (835 source leaf values):**

| Outcome | Count | |
|---|---:|---|
| copied | 232 | 265 destinations, 25 of them keys, 5 of them through the deduplicated observation |
| transformed | 26 | 18 named rules, each applied again to the source and compared |
| intentionally dropped | 104 | one declared rule: the uuid of a source element is not carried (the report's standing statement since 1.0.0) |
| **unaccounted** | **473** | 296 paths; the work queue |
| failed checks | 0 | |

The path map of the same conversion reads 835 of 835, UNMAPPED 0. The
corrected global check reads 283. The ledger reads 258 carried. 61 of
the unaccounted values have an equal value somewhere in the bundle,
which is exactly what the global check counted and the second report
predicted: the impact levels of the leveraged and the leveraging system
equal those of the main system, and only the main system's are carried.

**What the first run found, beyond the number:**

1. **The path map declares destinations the converter does not write.**
   Its rule for the system characteristics of the leveraged and the
   leveraging SSP says "system@1 facet (description, FIPS-199 carried)";
   the code carries the description. Its rule for inventory items says
   "asset props carried verbatim"; the props of `implemented-components`
   (6 names, 6 values) are not carried.
2. **A value is lost in the shipped bundle.** Inventory item 4 has two
   props named `ipv4-address`. The converter builds a dict from prop
   names, so `172.1.2.3` is overwritten by `1.1.2.3`. No earlier report
   could see it. It is not fixed here: the fix changes a bundle object
   and its digests, which is the author's call.
3. Most of the 473 are document metadata (revisions, parties, roles),
   back-matter resources, role and party references, and component
   status and type. Many will be deliberate. None is declared, and the
   ledger does not guess.

**The lost address, fixed (the same day, on the author's word).**
`oscal_conv_lib.props_by_name`: a prop name that repeats keeps every
value, as a list in source order, which is what parameter bindings
already do with several values. Item 4 now carries `["172.1.2.3",
"1.1.2.3"]`. Three files of the IFA bundle changed: the system Component,
the Attestation whose subject it is, and the manifest. The Component
keeps its id and its version (the SSP's `1.1.1`), as every re-run of
this converter has; whoever pinned its earlier semantic digest holds a digest
of the object with the address missing. The ledger reads 234 copied and
471 unaccounted since. The website's sentence now takes the ledger's
counts from the converter's report at build time, so the 471 can be
decided path by path without touching a page or a translation.

**Not done, on purpose.** Only one drop is declared, the one the report
already stated. Declaring the rest "intentional" would have produced a
small number and no knowledge.

**The first decisions on the unaccounted values (2026-11-13, the
author; applied the same day).** The 471 were put to the author in
fifteen classes, each with a recommended outcome. Accepted as
recommended and applied, none of them with a change to the bundle:

| Class | Values | Outcome |
|---|---:|---|
| Revision history of the source documents | 56 | declared drop: bookkeeping of the source, which the manifest pins by commit |
| Directory of parties and roles | 61 | declared drop: a party is a landmark URI and there is no party object (#16); a party name the bundle refers to stays a transformation |
| Back-matter resources and import links | 58 | declared drop: links to other serialisations, to imported documents and to the catalogue the bundle carries as Requirements |
| Type tags of structural elements | 11 | declared drop: the bundle says by its shape what the element is |
| The prop name that selects a response type | 2 | declared drop: the value is carried under the field the converter names `type` |
| The risk in the assessment results | 4 | its description equals the POA&M risk's and is linked to it; title, statement and status are the earlier state and are dropped as superseded (the POA&M title gained a prefix, its statement lost a misspelt word) |
| Values the converter already used | 7 | stated as rules: component `type` to `kind` for the four Components that had a constant kind, the control id of the SSP's implemented requirement and of the reviewed controls to the Requirement, the POA&M `system-id` to `component-refs` |

**The ledger since: 235 copied, 33 transformed, 295 dropped for a
declared reason, 272 unaccounted, 0 failed checks.** A drop applies only
to a value without a destination; the comparison of the ledger before
and after shows no value of another class among the newly dropped.

Four values of the "already used" class turned out not to be used and
stay unaccounted: the `related-controls` control id of the activities
in the assessment plan and the assessment results, and the `type` of
two components of the leveraging SSP (its copy of the leveraged system
and of the leveraged application), which the converter does not emit.

**Open.** Seven classes to carry (the characteristics of the leveraged
and the leveraging system, the component definition's control detail,
component descriptions and props, inventory prop classes, the
implementation narrative, assessment detail, document metadata into the
manifest's provenance): accepted in principle, each changes the bundle
and is applied class by class. Two classes are under discussion with
the author: role assignments without a kernel field (40 values) and
references by uuid whose edge the converter builds by hand (25).

## The carry classes and the references (2026-11-13, later the same day)

The author decided the 272: the seven carry classes as recommended;
roles at two levels only, on the Component and for the whole scope,
never per statement, activity, task, capability or user ("each role
assignment per element would blow up things"); and for the references
by uuid the recommended solution, resolve where the bundle has the edge,
carry where it has none. The decisions were applied in steps, one commit
each. After each step the converter ran twice (identical files), the
ledger had no failed check, and the reference validator, the converter
tests and the app's OSCAL tests were green.

**Before the first step, a guard.** The author's observation: the
converter's report is a historical document, and a breaking change in
the kernel or the library would go unnoticed. `SOURCES.sha256` in the
IFA folder pins the seven source files; a CI step downloads them at the
pinned commit, checks the digests, runs the converter and fails if the
committed folder is not reproduced byte for byte.

| Step | What was carried, and where | Copied | Transformed | Dropped | Unaccounted |
|---|---|---:|---:|---:|---:|
| before | | 235 | 33 | 295 | 272 |
| Document metadata | title, version, OSCAL version, last-modified, published and remarks of each of the seven documents, as `provenance.source-documents` in the manifest | 262 | 33 | 295 | 245 |
| Leveraged and leveraging system | one function builds `system@1` for all three plans: ids, status, sensitivity, FIPS-199 impact and information types, boundary, remarks, users | 310 | 33 | 293 | 199 |
| Inventory | beside `props` and `components`: `prop-classes` (the class of each prop, by name) and `component-props` (the props of each implemented component) | 341 | 33 | 293 | 168 |
| Component definition (#64) | per capability `statement-ids`, the statement texts under their clause ids, `parameter-bindings` under the catalogue's parameter names; the control implementation's description and source in `component@1` | 342 | 44 | 291 | 158 |
| Components and roles | `component@1` on every Component: description, purpose, status, props, `responsible-roles`; the scope's roles in `system@1` and in the Assessment's method payload | 388 | 60 | 309 | 78 |
| Implementation narrative | `implementation@1` on the Implementation: description, remarks, and per statement each component's response with what it says of the export, of what is inherited and of what is satisfied | 404 | 60 | 309 | 62 |
| Assessment detail | method payload: activities with steps, method and related controls, the results' own activity beside the plan's, tasks, subjects; `observations@1`: description, end, types, subjects, remarks; `finding-target@1`: descriptions and the POA&M item | 441 | 67 | 308 | 19 |
| References by uuid | lookup maps from source uuid to minted id; each edge is the result of resolving the reference the source gives | 441 | 95 | 296 | 3 |

**Shapes.** Two new facets, one per object type, each with a pinned
stub schema: `component@1` (`title`, `description`, `purpose`, `status`,
`props`, `control-implementations[]`, `responsible-roles[]`) and
`implementation@1` (`description`, `remarks`, `statements[]` of
`{statement, remarks, responses[]}`, a response being `{component,
description, export, inherited[], satisfied[]}`). Everything else went
into facets the corpus had. A role entry is `{role, parties: [landmark
URI]}`. An assignment the source makes below the two levels is rolled
up: where its role and party are on the Component or the scope already
it is linked to them in the ledger, else it joins the list.

**Declared in these steps**, and nothing else: eight role references to
parties the source defines without a name (the leveraged pair's parties
have a type and at most a remark; the role is carried without a party),
and twenty values of the leveraging plan's own entries for the leveraged
system and its application, for which the provider's Components stand.

**What the steps found.**

1. *The path map, again.* Beside the three claims known from the first
   run and #64 it said that the activity of the assessment results was
   "duplicated from AP; carried once" (it is a different activity, a
   TEST where the plan has an EXAMINE, and was not carried) and that the
   titles of the POA&M items "ride the Finding titles" (they did not).
   The texts now say what is written.
2. *Two edges were wrong.* Resolved from the source, the exported
   capability `cap-provided-2` belongs to the application component of
   the leveraged system; the converter had put it on the system
   Component `csp-iaas`. And the appliance's capability
   `cap-consumer-ac-2a` carried the `satisfied` text of another
   component of the same statement. Both follow the source now; the
   Implementation `csp-iaas-ac-2` cites the capability on
   `csp-application`. The other hand-wired edges resolved to the value
   they had.
3. *One observation, two texts.* The assessment results and the POA&M
   hold the same observation under one uuid, and its remarks differ by
   one space before a line break. The deduplication had kept the first
   and dropped the second unseen. The second is carried under `variants`.
4. *Source defects, reported and not repaired.* Eight parties without a
   name. A plan task names an activity by a uuid the plan does not
   define. The first POA&M item names a risk by a uuid the POA&M does not
   define (the item is matched to its risk through the observation they
   share). A `satisfied` entry of the leveraging plan names, as its
   responsibility, the uuid of an exported capability.
5. The stub schema of the method payload had not named `tasks` and
   `reviewed-controls`, which the payload has carried since 1.0.0 (part
   of #55).

**Still unaccounted: three**, the three dangling references of item 4
(`ap…tasks[].associated-activities[].activity-uuid`,
`poam…poam-items[].related-risks[].risk-uuid`,
`lvg…by-components[].satisfied[].responsibility-uuid`). Nothing is
invented for them and no drop is declared; that is the author's to
decide. 15 of the bundle's 17 objects changed in these steps, the two
Requirements did not; ids and versions are those of the source
documents, as on every re-run of this converter.

**Not done.** `requirement-ref` of the component definition's
capabilities is written into the NIST namespace by rule; the `source`
of the control implementation is carried and does not choose it. The
converter still writes a party URI `authorizing-official` for the
authorization that no source value names. The other ten converters have
no ledger.

## The last three, and what the ledger cannot see (2026-11-13, the author's two decisions)

1. **The three dangling references are declared as defects of the
   source.** The activity a task of the assessment plan names, the risk
   the first POA&M item names, and the responsibility one `satisfied`
   entry names do not exist in their documents. No edge is derived and
   none is invented; the ledger gives each the reason, and the report
   lists them as source findings. **The ledger reads 441 copied, 95
   transformed, 299 dropped for a declared reason, 0 unaccounted, 0
   failed checks.**
2. **The party URIs without a source stay, and the report says so.**
   `authority-ref` of the two authorizations and the Attestation's
   `signer` are written as `authorizing-official` and
   `csp-authorizing-official`. None of the plans defines such a role.
   The ledger follows source values into the bundle; it has no entry for
   a value the converter writes on its own. That direction, every bundle
   value traced back to a source value or to a stated constant, is not
   measured.

"0 unaccounted" therefore means: every source value has a destination,
a named rule or a stated reason. It does not mean lossless. 299 values
are not in the bundle, by decisions that are now written down, and three
values are in the bundle that no source gave.

## What it does not change

No kernel shape, rule or vector and no validator. The first decisions
changed no bundle object; the carry classes, later the same day, changed
15 of the IFA bundle's 17. And no
claim of losslessness is added: the specification already said that
"converted losslessly" is established at path level only.

## Lesson

A check written to expose an unverified claim was itself unverified. It
was believed because it brought bad news: 394 of 835 looked like a harsh
number, so nobody asked whether it was too kind. A measurement gets a
test with a known answer before its first number is published.
## Amendments — the open backlog before 2.0.0 (2026-11-13)

**Author decisions, in the author's words.** On the ten open rows and
the residue of #45: "#65 stays optional, fix it. #66 need the author! we
need authors for every part where a decision is made, a check done, a
risk changed etc! fix it. #41 keep in backlog, this is complex, but
include in Plan. #55 keep in backlog, this is complex, but include in
Plan. #46 recommend something to fix it, plan. #64 recommend something
to fix it, plan. #58 recommend something to fix it, plan. #62 keep in
backlog. #54 fix it. #47 recommend something to fix it, plan. #45
recommend something to fix it, plan." On the three points the plan left
open for #65 and #66: "1 report, 2 provenance, 3 read the clock then
report. start phase A".

**What the three answers settle.** (1) A missing author is a report
line; a flag turns the lines into failures, as `--require-risk-basis`
does for uncovered requirements. (2) Who and when is spelled one way,
`provenance: {author-ref, date}`, the shape a Mapping and a Check
already carry. (3) The validator reads the date of the run and reports
an approved Deviation past its `review-due`; the lapse fails nothing and
the Deviation keeps licensing its weakening. The plan is
`drafts/pre-2.0.0-fix-plan.md`. #65 and #66 change kernel shapes and
land together as one change proposal; until then both rows stay open and
the tag waits. Nothing of the two is built.

**Rejected.** For #66, the backlog row's option (b), "no field: the
history of a Tailoring is its versions". The author wants the author of
a decision in the record. For a lapsed Deviation, the plan's proposal to
judge a lapse only against a date the caller passes and to let it fail
the Deviation duty: the author wants the clock read and the lapse
reported.

### #54 CLOSED — the record of entries that do not apply

The side file was a map from an entry's label to a sentence. It is a
record with a schema now,
`risk-catalogs/schema/not-applicable.draft.schema.json`: per row the
entry's id and version, the rationale as a text, and `provenance`. One
file serves every catalogue, because a row names its entry by id.
**Built.** `risk_catalog.py` holds the file to the schema, refuses an
entry decided twice, and reports a row without an author and a row that
names no entry of the catalogue. The app (build 0.9.7) writes the record
with the party of the Owner field and the day, and reads the old map as
rows that say no author. **Measured.** The demo, rebuilt: 24 entries, 23
imported, 1 not applicable, 0 gaps with the record and 1 without, as
before; the imported Risks are byte-identical. Five refusals and reports
tried on the command line; the page driven in a browser (record, refuse
without a reason, refuse without a party, undo, an old map).
**Departures from the plan's sketch.** No `catalog` at the top and no
`tailoring-ref`: the app keeps one file for all catalogues, and nothing
reads a scope. No `review-due`: how a date of review is evaluated is
being decided for the Deviation (#65), and the record takes the field
over once that rule exists.

### #47b CLOSED — `none` and `contingency`

OSCAL allows seven values for the type of a risk response; C.10 has four
treatment options. `none` says that no option was chosen, and a Risk
says the same by carrying no `treatment`. `contingency` is a plan for
the day the risk materialises, none of the four options; a fifth code
needs a counted instance (D22, test 3) and no corpus holds one. Neither
gets a code. **Built.** The mapping moved from `convert_ifa.py` into
`oscal_conv_lib.py` (`response_treatment`), with four tests in
`test_oscal_conv_lib.py`, which the workflow runs. **Measured.** The
IFA converter, run from the public sources at the pinned commit
`usnistgov/oscal-content@9402f031`, reproduces the committed bundle,
both reports and the ledger byte for byte, before the change and after
it. Run on two copies of the POA&M with the one
`mitigate` changed to `none` and to `contingency`: the Risk carries no
`treatment`, the facet carries the type, the report counts it, the
bundle validates. **What it shows on the side.** The IFA sources can be
fetched and the conversion repeated in a cloud session; rows #41, #46
and #64 said the sources were not at hand. The session that built the
IFA ledger the same day found the same and made it a guard in the
workflow (`SOURCES.sha256`).

### #58 CLOSED, and the residue of #45 — the twin compares no two strings with a PowerShell operator

**The class was larger than the row.** The row named `-ceq`, `-cne` and
`-ccontains` on ids: 201 uses. Counted with PowerShell's own parser,
403 comparisons were not provably free of strings: 371 tests of
equality or membership and 32 ordering comparisons, which all order
numbers. `-eq`, `-ne` and `-contains` are the larger half of the 371
and the worse one: they fold case and compare under a culture. Three neighbours belong to the class: lookup
tables written as `@{}`, whose keys fold case; a `switch` over a
schema's type names; and a membership test on choice values that let
the number 1 pass for the string "1".
**Built.** 354 comparisons became `[string]::Equals(a, b, $ORD)` where
one side is a literal, `Str-Eq` or `Str-In` elsewhere; 17 more were
changed by hand (booleans and integers compared as what they are, the
choice values), and so were the tables and the `switch`. The rewrite was done by a
script that walks the syntax tree, innermost expression first. A helper
function was measured before it was chosen against: about 15 µs a call
on PowerShell 7.4, 27 times the operator; the inline call costs less
than `-eq`. `.github/scripts/lint-twin.ps1` parses the twin and fails
the build when an operator could meet two strings; the PowerShell job
runs it before the validator.
**Measured.** Six vectors (reference 13 → 18, tier 9 → 10), 543 in all
when they were written and 574 on main as it stands now.
The reference and the app's port passed all six unchanged. The twin
failed three before the change: an operation addressing statement `s1`
followed by U+00AD, one addressing a statement id in another normal
form, and a Tailoring whose id differs from its content's origin by one
U+00AD. It read that Tailoring as authority-claimed, which exempts it
from the Deviation duty. After the change the twin's output is the
earlier output line for line, apart from the two family counts. Four
deliberate breaks were each caught: two by the lint and by vectors, one
by vectors alone (the helper made culture-aware inside, which no lint of
operators can see), one by the lint alone (the `switch` put back, which
no vector exercises). On Windows PowerShell 5.1, in the workflow, on
the branch as it stood before it was rebased onto main: the lint, then
543 vectors in 17 families
(`reference: 18`, `tier: 10`), bundle by bundle the reference's counts
(1,712 · 814 · 136 · 18 · 1,040 · pack 2 · examples 27), ALL GREEN in
72 s (https://github.com/christoph-puppe/JASCON/actions/runs/43451843097).
The run of 2026-11-12 took 64 s. Timed here once each on PowerShell
7.4, the whole run went from 59 s to 64 s; the inline comparison is
faster than `-eq` and slower than `-ceq`.
**What it does not show.** The lint cannot see what a variable holds.
`$a -eq $b` is refused even for two numbers; `$x -eq 5` is accepted
although PowerShell compares as strings when `$x` is one; two string
variables compared with `-lt` would pass, since the ordering operators
are refused only on a literal or a `[string]` cast. The lint's header
says so.
**Found while testing.** The first version of the lint took its default
path from `$PSScriptRoot` inside `param()`. PowerShell 7.4 has set the
variable there; Windows PowerShell 5.1 has not, and the job stopped
before the lint read a line. A second-implementation check that had
only run on the wrong runtime: the mistake of #45 and #60, repeated
within the hour and caught by the workflow those rows left behind.

**Found on the way (not filed, not fixed).**
- A `set-parameter` operation that names a parameter its statement does
  not declare is accepted by all three implementations; closure checks
  the statement, not the parameter.
- The reference compares choice values with Python's `in`, which counts
  `true` as 1. The twin now does the same on purpose.
- `Finding.actions[].status` is a free string (`planned`, `done` and
  `closed` in the shipped data), and an action names nobody who is to
  carry it out.
- `Deviation.approver-ref` is required in every state, so a Deviation
  under investigation must already name its approver.
- `Mapping.provenance.date`, `Assessment.time` and
  `Attestation.timestamp` accept any string. D8 names `provenance.date`
  among the typed dates; for a Mapping it is not. The plan types all
  three with #66.
- The backlog row of #55 says the example's `summary` is a string; in
  today's tree it is a language map.

### The rebase onto main (2026-11-13)

While phase A was built, another session landed 29 commits on main: the
run rules of CHECK-12, 13 and 15, NUMBER-1 (#67), the value-level check
of the converters and the IFA ledger (#64 closed, #41 narrowed). Fifteen
files were changed on both sides. The author: "origin has moved, rebase
and check if our work here is touched. the other session is finished
now, so we take lead."

**What was touched, and how it was settled.**

| File | Main | Here | Settled |
|---|---|---|---|
| `validate_core.ps1` | NUMBER-1, the run rules | 371 comparisons made ordinal | main's file taken as it is, the change applied again by its two scripts; every anchor of the hand edits was still there once, and the rewrite again changed 354 |
| `convert_ifa.py`, `oscal_conv_lib.py` | the ledger | `response_treatment` | both kept; the treatment's ledger rule now derives through `response_treatment` |
| the library's tests | `test_oscal_conv_lib.py`, run by the workflow | a self-test inside the library | our four cases moved into main's file; the self-test and its workflow step are gone |
| the app's build | 0.9.5 and 0.9.6 | 0.9.5 | ours is 0.9.7 |
| totals, the skill archive, the website's facts | 568 vectors | 543 | 574; the archive and the facts rebuilt from the rebased tree |
| backlog, register, README, rc.3 | their records | ours | both kept, in the order of the events |

**Measured after the rebase.** Both validators green on 574 vectors with
equal counts per family, on the five bundles, the worked pack and the
example folder. Main's twin, unchanged, fails the same three of the six
vectors as the twin of the old base; apart from those two family counts
its output equals the rewritten twin's line for line. The IFA converter
reproduces the committed bundle, reports and ledger byte for byte, and
the seven sources match `SOURCES.sha256`. The library's tests: 27, of
which 4 are ours. The app's tests, the catalogue demo and the lint as
before.

**What the other session's work changes in our plan.** #64 is closed, so
§5.2 of the plan is done by other hands, and phase C shrinks to the IFA
half of #46 and the IFA payload of #55. #41 has its first corpus
accounted for value by value; the other ten converters have no ledger.
The plan's remark that the old measure counts a short value as arrived
by accident was the defect issue 32 reported and main fixed.

### The fixes of pull request 35 after the rebase, and where they are written down (2026-11-13)

The author, after the rebase: "in #35 we fixed a lot, make sure those
fixes stand and are covered in skill, handbook and website!"

**They stand.** Pull request 35 changed 44 files. On the rebased branch
35 of them are byte for byte main's: the IFA bundle, its ledger, both
coverage reports, the seven pinned stub schemas, `SOURCES.sha256`, the
website's build script. The other nine differ where this branch meant
them to (the workflow, the converter's three lines on the treatment
option, the library and its tests, the twin, the records, the archive).
Run on the rebased tree: the ledger reads 441 copied, 95 transformed,
299 dropped, 0 unaccounted, 0 failed checks; the conversion is
reproduced from the pinned sources without a changed byte; the
library's 27 tests pass, the repeated prop name among them. The pull
request named three overlaps with this branch in advance: the lint
against the twin's new code, the treatment table joined by hand, and
the build number and totals. Each came out as it said.

**Where they were not written down.**

| Place | Before | Now |
|---|---|---|
| The skill (`SKILL.md`, requirement 13) | three converters; no ledger, no library, no test file | the two depths of a coverage report and their gates, "none unaccounted is not lossless", `props_by_name`, references resolved and not typed in, pinned sources; `convert_ifa.py`, `oscal_conv_lib.py` and its tests listed |
| Handbook 14.1 | the ledger's first reading, 473 unaccounted | what became of the 473: carry, resolve, drop with the reason, declare; roles at two levels; two rules, on "lossless" and on a conversion nobody reproduces |
| Handbook 14.2 | #64 open: "leaves 2 clause-level texts and 2 parameter values behind" | closed, with the one difference that remains |
| Website, home page | "122 content values did not" arrive, a figure of the measure issue 32 refuted | the ledger's counts, filled by the build |
| Website, join page | "there it does not hold"; start at `oscal_conv_lib.value_arrival()`, a function removed in pull request 34 | the ledger; start at `oscal_conv_lib.Ledger` and `convert_ifa.py` |
| Website, evidence page | the ledger counts, without what they do not say | accounted for is not carried; the conversion is reproduced on every change |
| README | "does not hold there"; "122 content values do not" | the ledger's counts and the guard |

The website's changes are in all five languages; each translation has
the structure of its English page and is stamped against it.

**Stale for another reason, and corrected on the way.** The evidence
page dated the twin's run to 12 November and let the build fill in the
vector count of today; that day it was 537. The sentence now carries no
date. The same page and the README said that nothing is left to decide
before the tag and that items 65 and 66 need the author's decision; both
were decided on 13 November and neither is built.
