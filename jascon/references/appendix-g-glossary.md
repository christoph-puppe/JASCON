# The JASCON Handbook
# Appendix G — Glossary

**Convention:** term — definition, with pointers (Ch. = chapter,
App. = appendix). German regulatory terms are glossed where they are
load-bearing. Where a number appears, it is a measured one.

---

**Alias** — an alternative name for an object, carried with its
scheme (`{scheme, value}`); absorbs 1.x `alt-identifier` (×1,219
measured). Distinct from *canonical-alias*. (Ch. 3, App. A.0)

**Annotation** — rendering chrome on any object: compliance-
invisible, excluded from the semantic digest, legitimately
strippable. A template that reads annotations into normative content
is non-conformant. (Ch. 7, 11, 13)

**Assessment** — the kernel object recording who checked what, how
(facet-typed method), when, with what result. (Ch. 10, App. A.7)

**assessment-criteria** — the stdlib facet carrying what assessors
check: required documentation/artifacts, examples, key tests; the
KSI shape's home; declares `[assessment]`. (App. D.6)

**Attestation** — the kernel object binding meaning (subject semantic
digests), package state (manifest digest), and paper (rendering
digest) under one signature; lives *beside* the manifest, never
inside it. (Ch. 11, App. A.9)

**attestation-binds** — the Portable-tier primitive that evaluates an
Attestation and returns Full Match, Semantic Match, or fail.
(App. B.1.7)

**Authority** — (1) an organization that mints identifiers and
publishes requirements; (2) the conformance tier carrying publication
duties (stable ids, lineage records, both digests, `.well-known`,
deprecation, calendars). (Ch. 3, 15)

**authorization** — the identified trust context on a Component
(`{id, authority-ref, scope-label, includes[]}`); the currency every
inheritance edge must name. Absence is silence, and silence is
silence. (Ch. 9, App. A.5)

**basis-ref** — the field on an `inherited-from` edge naming the
specific authorization id it leans on; the edge-local boundary rule
(D5). Delete it and validation fails closed. (Ch. 9)

**Baseline** — a RequirementSet used as a selectable scope (ISM's
five classification baselines; BSI's sec-level sets; CR26's class
sets). Membership is edges, never per-object markers. (Ch. 5)

**Bi-modal verification** — the two-honest-outcomes verdict shape:
*Full Match* (exact package as signed) or *Semantic Match* (meaning
proven, packaging changed — a report, not a defect). (Ch. 11)

**Bundle** — the unit of publication: objects, pinned facet schemas,
renderings, one content manifest, attestations beside. There are no
fixed document files. (Ch. 11, App. A.11)

**Calendar-period** — a duration counted on a named calendar
(`days · bizdays · weeks · months · years` + mandatory
`calendar-ref`); *representable* everywhere, *computable* only with
the calendar — otherwise fail-closed. (Ch. 4, 10; App. C.9)

**Canonical-alias** — the identity-event record on a new object
declaring "same content, new home" (rebrand, domain loss); the
forwarding address the old world never had. (Ch. 3)

**Canonical Reference Facet** — SP 800-53's document conventions as a
facet NIST owns, shipped by default, governed like every other
facet: "the standard library, not the constitution." (Ch. 15,
App. D.9)

**Capability** — a vendor claim on a Component (`{id, description,
parameter-bindings}`); the replacement for the component-definition
document and its duplication axis. (Ch. 9)

**Census** — this project's method: count every field in every corpus
before designing anything. "When in doubt, count." (Ch. 1; the
census file)

**Chrome** — see *Annotation*.

**Code system** — a versioned closed enumeration (`modality@1`…)
validated by `code-from`; unknown codes are errors because unpoliced
value spaces fork (measured: `normal-SdT` vs bare `erhöht`).
(App. C)

**Compatibility facet (`oscal-1x@…`)** — the Level-2 waiting room
with a clock: preserved, schema-carried, intended-deprecated, residue
tracked per release. Current measured residues: ISM 539 · BSI 179 ·
CR26 34 + 79 — every row with a named exit. (Ch. 14.6, App. D.10)

**Complexity budget** — the design's governing inversion: boring
infrastructure, sophisticated semantic contract — the opposite of the
predecessor's spend. (Ch. 1)

**Component** — the kernel object for systems, services, software,
policies; carries members, capabilities, authorizations. (Ch. 9)

**conditional-apply** — the one bounded conditional: a predicate
trigger (≤1 hop) gating an enforced primitive instantiation; facets
instantiate it, never extend it. (App. B.1.8)

**Confidence** — the diligence grade on a Mapping (`draft · reviewed
· authoritative`); measured usage: 373 × draft for machine-imported
links. (App. C.7)

**Conformance corpus** — the golden bundles-with-verdicts that *are*
the specification (test-suite-as-spec); release gated on two
independent implementations agreeing with it. (Ch. 12, 15)

**Content manifest** — the bundle's resolution table and digest
ledger: per object both digests, per facet schema an exact pin;
sealed validation resolves only through it. (App. A.11)

**Core** — the passive conformance tier: validate, digest, resolve
locally, preserve — and compute nothing semantic. (Ch. 12, 15)

**Coverage report** — a converter's mandatory second artifact: every
source path, its count, its declared destination; unmapped values
listed by code. Gate target: zero unexplained. (Ch. 14, the three
reports)

**DARF NUR** — German regulatory "may only": exclusive permission;
code `may-only`, its own lattice branch. Measured occurrences in the
current corpus: 0 — anticipated, unused, honestly reported.
(Ch. 4, App. C.1, F Q12)

**Deviation** — the sub-object recording sanctioned departure: typed
(false-positive · operational-requirement · risk-adjustment ·
vendor-dependency · derogation), state-machined, approver-named. One
channel, three moments: Tailoring (ex ante), Implementation (in
operation), Finding (ex post). (Ch. 6, 10)

**Digest, package** — SHA-256 over the shipped bytes; answers "are
these the bytes." **Digest, semantic** — SHA-256 over
JCS(object − annotations); answers "is this the approved meaning."
Two digests, two jobs. (Ch. 11)

**DSSE** — Dead Simple Signing Envelope; the stdlib attestation
profile's envelope format. (Ch. 11)

**Edge-local rule** — the D5 pattern: put the obligation on the edge
where one hop suffices (inheritance names its basis), so chains of
any depth verify link by link. (Ch. 9, F Q16)

**Effectivity** — the stdlib facet for when obligations bite:
obtain/maintain/adoption/grace windows, per track. (App. D.5)

**Elapsed-duration** — a clock that runs through weekends
(`seconds · minutes · hours`); the other half of the duration split.
(App. C.9)

**Empty-omission rule** — omit empty optional arrays/objects before
canonicalization, so presence-vs-absence cannot fork digests.
(Ch. 11, App. B)

**Engine posture** — the coexistence stance: the Core is the source
of truth; valid 1.x is *generated* for regulators during the
transition; never dual-edited. (Ch. 14.7, 15.5)

**Evidence tier** — the discipline of labeling every claim measured /
designed-for / hypothesis, applied to the spec, the stdlib, and this
book's own appendices. (Ch. 15, App. A.12)

**Excludes** — Tailoring's scope-out list: **selection, never
Deviation** — narrowing applicability is not weakening a
requirement. (Ch. 6)

**Facet** — a registered extension: URI-identified, major-versioned,
schema-pinned via the manifest, semantics declared
(`modifies-semantics ⊆ {assessment, tailoring, selection,
rendering}`). Species: stdlib, framework, compatibility. (Ch. 7)

**Fail-closed** — the refusal to guess: a computation of class C
meeting an undeclared-understood facet of class C halts with a
printed rationale. Fires at the verb, not the noun. (Ch. 12, 13)

**Finding** — the kernel object for an assessment result needing
disposition: statement-scoped, action-carrying (computable due
dates), deviation-capable. (Ch. 10)

**Five-CSP clause** — the incumbent policy's own mechanism admitting
any public-domain format maintained by five certified providers;
recorded without endorsement; swings both ways. (Ch. 15.5)

**Force distribution** — a corpus's modality histogram; the health
chart. Measured signatures: BSI should-heavy (626/225/155), CR26
must-heavy (136/45/20/11/5), ISM honestly unspecified (1,149).
(Ch. 4, App. C.1)

**Framework facet** — an authority's own registered vocabulary
(gspp-taxonomy, cr26/scope…); the sanctioned open category. (Ch. 7,
App. D.11)

**Gate (v0.6)** — the executable exit criterion: full-corpus
converters (✓ 3/3 at 100 %), executable schemas + conformance
corpus, lifecycle corpus, measured weekend-validator test. Claims
follow evidence tier — the gate is where the tier changes. (Ch. 12,
15)

**Global identity** — authority-minted URI ids, string-compared,
never resolved; the decision that deletes merge semantics and
enables cross-authority composition. (Ch. 3)

**Guarantee levels** — migration's three labels: **L1** native
mapping, **L2** compatibility facet (clocked), **L3** opaque
preservation (no semantic claim). Summary claim:
information-preserving for the supported corpus, per a published
equivalence relation. (Ch. 14)

**Identity addressing** — operations target
`requirement-ref + statement-id`, never array positions; survives
re-issue by construction. (Ch. 6, F Q2)

**Implementation** — the kernel *edge* object: Component ×
Requirement (± statements), responsibility, satisfied-by
(capability or inherited-from + basis), status, evidence. (Ch. 9)

**JCS** — RFC 8785 JSON Canonicalization Scheme: one byte sequence
per data value; the semantic digest's foundation, with the
empty-omission and decimal-as-string guards on top. (Ch. 11)

**KSI** — Key Security Indicator (CR26): named indicator +
statement + tests + control links; converts to a Requirement plus
Mapping objects. (Ch. 10, App. E.4)

**Lattice** — the modality partial order (App. C.1's diagram):
upward monotone and free; downward or cross-branch ⇒ Deviation.

**Layers (L0–L4)** — the book's shorthand strata: L0 identity &
versioning · L1 objects · L2 composition/tailoring · L3 facets ·
L4 rendering. Documents live at L4; truth lives below. (Ch. 2)

**Lifecycle** — `draft · active · deprecated · withdrawn`; identity
events are separate records, not states. (App. C.2)

**Mapping** — the kernel object for a crosswalk claim: typed
relationship (IR 8477/OLIR codes), direction, confidence, provenance
— ownership answered, contradictions coexisting. (Ch. 8)

**may-only** — see *DARF NUR*.

**Modality** — a statement's binding force, one code from the
lattice; `unspecified` is legitimate (narrative frameworks) and
below everything. (Ch. 4)

**Monotone move** — a modality change upward along one lattice
branch; free in tailoring. Everything else needs a Deviation.
Measured: 111 class-variant ops, zero non-monotone. (Ch. 6, App. B)

**Obligated party** — who a statement binds (`obligated-parties[]`,
code-or-ref); absorbs CR26 `affects[]`. (Ch. 4)

**Operation** — one of the eight closed tailoring edits
(set-parameter, set-modality, set-field, replace-prose,
add/remove-relation, attach/detach-facet), identity-addressed,
per-op weakening law. (Ch. 6, App. B.3)

**Parameter** — a statement's typed insertion point; prose references
it as `{param:name}`; an unbound token is a validation error — the
216's negation. (Ch. 4)

**Pin** — an exact facet-schema version + digest in the manifest;
the trust anchor that makes sealed validation and lawful composition
possible. Never a range, never "latest." (Ch. 7, 13)

**Portable** — the conformance tier where meaning is handled:
facet validation, capabilities + fail-closed, JCS digests,
deterministic tailoring, composition. The RFC-0024 slot. (Ch. 15)

**Predicate** — one of three (`field-equals · param-equals ·
present`), one ≤1-hop leash, shared by selection and
conditional-apply. (App. B.2)

**Preservation** — the duty to carry what you don't compute:
byte-faithful, unreordered, visibly inventoried. "You may always
carry what you cannot compute." (Ch. 12, 13)

**Primitive** — one of the eight closed computations (App. B.1);
versioned set, never a language.

**Props (historical)** — 1.x's untyped name/value annotations; the
measured 22,000+ across three corpora, >70 % kernel imitations. The
architecture's origin corpse. (Ch. 1, 7)

**Provenance** — whose claim, when — mandatory on Mappings, recorded
on manifests and resolutions. (Ch. 8, 11)

**Pseudo-placeholder** — free text costumed as a parameter
(`{{...}}`); the 216 (213 + 3) found, listed, and queued — never
repaired, passed through, or dropped. (Ch. 1, 14.5, App. E)

**Rationale-on-failure** — every rule carries machine id, human
reason, failure message; the reason *prints* when the rule fires.
The anti-#2118 mechanism. (Ch. 12, 15, App. B)

**Registry** — the federated vocabulary ecosystem: self-publication
at `.well-known`, Foundation-curated index, append-only transparency
log — memory without gatekeeping; burnable without breaking a single
validation. (Ch. 7, 15)

**Relations** — typed object-to-object links; the one deliberately
extensible code surface (carry-don't-compute for unknown types).
(App. C.8)

**Rendering** — a document as a *view* (L4): pinned template, named
renderer, digest-bound by attestation; provenance map for
paragraph↔statement navigation. (Ch. 11, 13)

**Requirement / RequirementSet** — the atom (statements within) and
the membership object (nestable; sequence-ordered). (Ch. 4, 5)

**Responsibility** — `provider · customer · shared · inherited` on
Implementation edges; clause-splittable via statement-refs. (Ch. 9)

**Round-trip** — up-convert, down-convert, compare — against a
*published equivalence relation* with corpus vectors; a defined
relation, never a magic word. (Ch. 14.7)

**Sealed mode** — validation with the network absent: manifest-only
resolution, pin-anchored trust; the air-gap first-class citizen.
(Ch. 11, 12)

**Semantic Match** — see *Bi-modal verification*; information, not
injury.

**Sequence** — explicit ordering on Set members; absorbs sort-id
(×2,870). (Ch. 5)

**Shadow set (supplement pattern)** — amending a catalog you don't
own by authorship instead of injection: your new Requirements under
your prefix, composed with the upstream in a Set you publish,
interleaved by sequence; clause-level attachment by reference.
What profile resolution produced, the shadow Set *is*. (Ch. 6.A,
App. F Q23)

**Statement** — the identified clause: id, modality, parties,
parameters, prose. The shared fine-grained address of the whole
model. (Ch. 4)

**stdlib** — the Foundation-stewarded standard library: eight facets,
the code systems, the DSSE profile, transit projection, reference
templates. (App. D)

**Sunset trigger** — the declared, measurable state ending the dual
window (authorities native at scale, Portable implementations in
multiple languages, corpus green). v0.6 is its first milestone.
(Ch. 15.5)

**Tailoring** — the kernel object for lawful adaptation: bounded
selection, identity-addressed operations, per-op weakening law,
deterministic resolution, no auto-merge. (Ch. 6)

**Terminology** — the stdlib facet for defined terms + aliases;
"when a defined term appears in a rule, the definition is part of
the rule." Measured: 75 terms, 188 aliases, 264 references, all
resolving. (App. D.3, E.5)

**Three coping strategies** — violate, flatten, route around: what
authorities do when the change path costs more than the detour; the
governance design inverts the price. (Ch. 1, 15)

**Tightening** — a parameter's declared stricter direction
(`lower · higher · none`); bounds moves against it ⇒ Deviation.
(Ch. 4, App. C.9)

**Track** — CR26's `20x` / `Rev5` dimension; track-specific rules
measured: 9 + 12, composed as sets-of-sets. (App. E.2, the CR26
report)

**Twin-catalog collision** — the measured duplicated-truth hazard:
11 shared id strings across two publications, 1 prose-identical, 10
silently diverged. (Ch. 3, App. B.1.3)

**unspecified** — the honest modality for prose that declines to
encode force; below everything on the lattice; a narrative
framework's dignity, not its defect. (Ch. 4, App. E.3)

**Validator ecology** — many cheap independent implementations as a
governance control: no monoculture, no de-facto constitution.
The weekend validator is its unit. (Ch. 12, 15)

**Variant-only rule** — a CR26 rule existing solely as class
variants (×29 measured); base synthesized and flagged; the D13
ceremony question's constituency. (App. E.2)

**Weekend validator** — the acceptance test made of time: a
competent engineer, a weekend, a conformant Core validator; measured
at the gate, not asserted. (Ch. 12)

---

*End of the appendices — and of the manuscript: fifteen chapters,
seven appendices, one method. When in doubt, count.*
