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
(`https://ns.oscal-semantic.org/core`) for what it cannot say —
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
`drafts/oscal-semantic-core-specification-1.0.0-rc.1.md`: the normative
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
title as history. **Machine identifiers keep the `oscal-semantic-core`
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
`drafts/oscal-semantic-core-specification-1.0.0.md` (renamed from
`…-1.0.0-rc.1.md`; title and IV.6/IV.8 updated; README and the v0.5
banner repointed). Release notes:
`drafts/jascon-1.0.0-release-notes.md` (doubles as the GitHub release
body; the SKILL zip is the attachable artifact).

**The tag-time decision — machine identifiers remain
`oscal-semantic-core`.** Namespace URIs, the attestation media type
(`application/vnd.oscal-semantic-core.attestation+json` — inside every
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
**Trade-off.** The string `oscal-semantic-core` outlives the working
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
thing: a namespace URI, `application/vnd.oscal-semantic-core.attestation+json`
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
(`oscal-semantic-core-1.0.0.schema.json`), `https://ns.oscal-semantic.org/core`,
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
Schema file `oscal-semantic-core-2.0.0.schema.json`, `$id`
`https://ns.oscal.org/semantic-core/schema/2.0.0`; the working label
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
exist") — **unchanged here**; `oscal-semantic-core` stays in namespace
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
(`drafts/oscal-semantic-core-specification-2.0.0-rc.1.md`): D23 carries
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
   the schema `$id` under `ns.oscal.org`). D2 makes them opaque strings,
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

