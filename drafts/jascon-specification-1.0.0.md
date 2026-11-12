# JASCON — "Kernel + Registered Facets"
## Specification 1.0.0
### released 2026-07-22 at tag `v1.0.0` · consolidated from the v0.5 draft + the v0.6-cycle amendment journal · hardened by the P10 double review + fix pass

> **Name.** **JASCON** — **J**SON **A**ttestable **S**emantic **C**ompliance
> **O**bject-graph **N**otation; *one notation for every standard, in every
> language*. Renamed from the working title "OSCAL Semantic Core" on
> 2026-07-22 (decision recorded in the rationale register; uniqueness
> verified by collision scan the same day). Machine identifiers — namespace
> URIs, the attestation media type
> `application/vnd.jascon.attestation+json`, schema filenames —
> deliberately retain the working-title string for digest stability.
> **Decided at the tag: they remain.** Identifiers are opaque strings (D2);
> the brand lives in prose; churning every digest and signature for a
> spelling would contradict the stability the identifiers exist to provide
> (register "Amendments — v1.0.0"; revisit only with a D3.5 major).
> *(Reversed in 2.0.0 for the media type and the schema filenames —
> register, "Amendments — 2026-11-11".)*
> Nothing here is endorsed
> by NIST, BSI, ACSC, CCB, CIS, or FedRAMP; the project is maintained in
> personal capacity.

**Status.** A **measured architecture**: every claim in this document has
survived contact with real catalogs or is explicitly tiered below
*measured*. The v0.6 executable gate is **delivered in full** (IV.5):
eleven corpora converted losslessly (251,591 source leaf values,
UNMAPPED = 0 everywhere; twelve source publications when the 800-53B
baselines are counted separately), a 157-vector conformance corpus in
twelve families, two independent-runtime reference validators (Python;
a zero-dependency PowerShell 5.1 twin — **each** ≈30× smaller than the
OSCAL 1.x toolchain with the crypto engines included), DSSE
verification, bundle composition, conditional-apply, and a
bidirectional OSCAL 1.2.2 export that round-trips 5,886/5,886 catalog
objects to semantic-digest equality against the official NIST schema.
The spec-feedback backlog is **empty** — every item that ever entered
it left through a register entry. Comparison baseline throughout:
**OSCAL 1.2.2** (current NIST line, eight models including the Control
Mapping Model introduced March 2026 with v1.2.1).

**Provenance of this text.** The normative sections (Parts I–II,
Appendices A–C) were amended in place through six adversarial review
passes, three external review rounds, the P9 twin red-team runs, and
four evidence gates; the full amendment journal lives in the
**Decision Rationale Register** (companion document) and the git
history. This release candidate is that text, consolidated: journals
compacted to IV.6, gate results recorded in IV.5, nothing renumbered.

**North star (session directive, governs every verdict):** *more simple ·
closer to the needs of the customers · no more props · less need for custom
Metaschema extensions or bespoke JSON.* Every decision below cites at least
one measured customer need; the companion **Decision Rationale Register**
scores each decision explicitly against customer / simplicity / reduced
complexity.

**Lineage.** v0.1 → pass 1 → v0.2 → pass 2 + census r1/r2 → v0.3 → passes
3 (SOL) + 4 (H) → v0.4 → passes 5 (Grok, validating), 6 (P6-F1…4),
7 (P7-B1…4, gaps, mapping), 8 (P8-E1…4, gaps) → **v0.5** → v0.6 cycle:
review rounds 1–2 (adjudicated, F.6/F.7) + P9 twin adversarial runs
(adjudicated, F.8) + gates 1–4 delivered + the converter rerun →
1.0.0-rc.1 → P10 twice (in-repo + external, adjudicated) + the fix
pass → **1.0.0**.

---

# Part I — The Evidence Base

## 1. Method

Admitted sources of design authority — every normative element traces to at
least one: (1) **measured 1.x failures** (F1–F10); (2) **adjudicated
adversarial findings** (G, SOL/H, P6/P7/P8 — rejections documented);
(3) **the three-authority census** (ISM v2026.06.18 · BSI GS++/MS-TLS
2026-07 · FedRAMP CR26 v2026.07.14.01).

Principles: **failures unrepresentable, not forbidden** (the 216
pseudo-placeholders inside schema-valid BSI documents remain the standing
proof *[erratum 2026-11-12: the 216 values hold the parameter slots of the
sentence template and are not defects; the standing proof is the 781 list values packed
into comma-separated strings — register, "Amendments — 2026-11-12: the
packed lists"]*); **complexity-budget reallocation** (1.x spent the budget on
infrastructure — RFC-0024 records the verdict: 100+ Rev5 authorizations in
2025, zero OSCAL); **claims follow evidence tier** (measured / designed-for /
hypothesized, always labeled).

## 2. Corpus and adopter scope (corrected per P7/P8)

Authoritative machine-readable publications are one category; conversions
and mappings are another. The defensible scope statement:

> The design targets official machine-readable publications from **NIST**
> (800-53, 800-171, CSF 2.0 in OSCAL 1.2.2), **BSI** (Stand-der-Technik /
> Grundschutz++ catalogs — not the entire traditional Kompendium), **ASD**
> (ISM OSCAL releases), **CSA** (CCM v4 OSCAL bundle — a conversion
> artifact, version to be re-checked at corpus time), **SCF** (official
> OSCAL JSON — pinned to OSCAL **1.0.4**, itself a data point for version
> fragmentation), and **FedRAMP CR26** (bespoke JSON, not OSCAL); plus the
> **CIS** OSCAL corpus (repository status disputed between passes —
> archived vs. maintained v8.1 — verification item, treated as test corpus
> either way — since settled by measurement: both CIS corpora converted
> at 100 % on 2026-07-21, R15 resolved); plus **licensed or independently modeled targets** for
> ISO/IEC 27001/27002 and PCI DSS, which have **no official OSCAL
> publications** and must never be attributed as such.

The census covered three corpora (ISM, BSI, CR26). At rc.1 the
**measured** set is **eleven bundles** — twelve source publications when
NIST SP 800-53 and the 800-53B baselines are counted separately (the
counting convention, stated once here): the census three, five
validation corpora (BE.CyFun, CIS Controls v8.1, CIS Ubuntu 24.04
Benchmark, DE.C5, DE.C3A), and the gate-3 additions (NIST SP 800-53
Rev 5.2.0 + all four 800-53B baselines, CSF 2.0, and the IFA GoodRead
lifecycle set — SSP/AP/AR/POA&M + the leveraged pair), each converted
census-first at 100 % declared coverage with UNMAPPED = 0. CSA CCM, SCF, ISO and PCI
targets remain *designed-for*, exactly as labeled in IV.4.

## 3. The convergence table

Decision rule: **3-way convergence → kernel; real but framework-shaped →
stdlib facet; workaround for a missing kernel mechanism → structurally
dead.** (Unchanged from v0.4 except the rows noted; full table retained for
self-containment.)

| Concept | ISM | BSI | FedRAMP CR26 | v0.5 home |
|---|---|---|---|---|
| Modality | prose (style-guide) | `modal_verb` ×1,006 | `force` ×328 (MUST 189/SHOULD 84/MAY 39/MUST NOT 11/SHOULD NOT 5) | Kernel `statements[].modality` + **normative partial order** (D9) |
| Clause granularity | 1 statement/control | **347 nested pseudo-controls** | class variants + info bullets | Kernel `statements[]` (D9) |
| Obligated party | implicit | `target_object_categories` (distinct concept → grammar facet) | `affects[]` (array) | Kernel `obligated-parties[]` (D9) |
| Membership / baselines | `applicability` ×5,301 + E8 ×256 | twin catalogs | `subsets` + per-class lists | dead → RequirementSet (D13, D21) |
| Secondary identifiers | labels + legacy nos. | `alt-identifier` ×1,219 | `alts[]` ×188 | Kernel `label` + `aliases[]` (D2) |
| Revision history | ×2,202 | silent drift | `updated[]` everywhere | dead → L0 (D2/D3) |
| Deadlines | — | — | typed timeframes, bizdays | Kernel `duration` **split elapsed/calendar** (D9) |
| Requirement grammar | — | ×~2,450 | house grammar in prose | stdlib `statement-grammar@1` |
| Class variants | separate profiles | `sec_level` | `varies_by_class` | dead → Tailoring (D13) |
| Evidence / key tests | — | `documentation` ×959 | artifacts, key_tests | stdlib `assessment-criteria@1` |
| Glossary | — | — | FRD 75 terms/188 aliases | stdlib `terminology@1` |
| Reporting duties | — | — | `notification[]` | stdlib `reporting-obligation@1` |
| Effectivity | — | — | `info.effective` | stdlib `effectivity@1` |
| Deviations | — | audit practice | `corrective_actions`; hist. 4× state machine | Kernel `Deviation` (D8) |
| **Cross-framework mappings** *(new row)* | — | — | KSI→800-53 ×263 | **Kernel `Mapping`** (D20) — external evidence: SCF ×200+ frameworks, CIS/CSA mapping products, NIST OLIR, and NIST's own March-2026 Mapping Model |
| Rendering hints | — | — | `do_not_link`, `web_name` | Annotations (D10) |
| Process flows | — | — | `info.flows[]` | out of scope (D17) |

---

# Part II — The Decision Register

Format: **Decision → Evidence → Rationale → Pros → Cons → Rejected.**
Stable numbering; `(rev. v0.5 — finding)` marks changes since v0.4.

## D1 — One serialization: JSON; prose = CommonMark + GFM tables, no raw HTML.
Unchanged from v0.4. Evidence: CR26 is JSON-canonical; ISM triple-publishing
is an agency tax; the fabricated "#2118 wanted tables" justification remains
documented and discarded — GFM tables stand on the parameter-matrix reality
of compliance prose. Data-bearing tables belong in typed fields; prose
tables are narrative. Rejected: normative XML, YAML conformance, raw HTML.

## D2 — Identity: authority URIs, string-compared, never resolved; `label` + `aliases[]`; **alias vs. lineage split.** *(rev. v0.5 — P7-B4)*
**Decision.** As v0.4, with the supersession mechanism split into two
relations with different powers:

- `canonical-alias` — **identity equivalence**, authority-asserted, only for
  rebrands of the *same* content (old URI ⇄ new URI). Validators substitute
  freely.
- `replaces[] {ref, relationship: revised | split-from | merged-into |
  renamed}` — **lineage only**. Never automatic substitution: a revision,
  split, or merge is a different object with history, and auto-substituting
  it would silently corrupt implementations, findings, attestations,
  mappings, and tailorings.

**Evidence.** BSI twin-catalog collisions; the deleted FedRAMP registry
(locator rot); ×1,219/×188/legacy alias practice across all three; P7's
demonstration that "supersedes = equivalence" is unsafe for revised content.
**Rejected.** URN scheme; UUID-primary identity; one conflated supersedes
relation (v0.4 — corrected).

## D3 — **Content manifest**, sealed mode, two integrity domains, deterministic canonical form. *(rev. v0.5 — P7-B1, P6-F3, P8-E4, P7-G3/G5)*
**Decision.**

1. The **content manifest** lists all substantive objects and renderings
   with **both digests each** (`package-digest` over delivered bytes,
   annotations included; `semantic-digest` = SHA-256 over JCS of the object
   minus `annotations`). **Attestations and signature envelopes are
   excluded from the content manifest by definition** — they live beside
   it (a transport manifest MAY list both but is never the signed
   structure). This dissolves the manifest↔attestation hash cycle P7-B1
   proved: nothing signed contains its own signature.
2. **Sealed mode** remains a Core conformance requirement: full validation
   with zero network access, resolution via the manifest only.
3. **JCS pre-normalization (P6-F3):** before JCS serialization, all
   structurally optional arrays/objects containing zero elements MUST be
   omitted. Normative test vectors cover this and the permitted number
   domain.
4. **`decimal` is a canonical decimal string** (lexically defined scale/
   precision), never an IEEE-754 number — two tools MUST derive identical
   digests and values (P7-G on decimals). **Canonical form (rev. v0.6 cycle
   — backlog #27):** no leading zeros (`01.5` is rejected — it is a
   non-canonical spelling of one value); **no negative zero** (`-0`,
   `-0.0` are second spellings of zero — rev. P10 #37; a negative
   fraction such as `-0.5` stays legal); scale IS significant, so `1.5` and
   `1.50` are DISTINCT values by design (the lexical form defines the scale)
   and their differing digests are correct, not a divergence. Re-scaling a
   value is forbidden. Schema pattern:
   `^(-?[1-9][0-9]*(\.[0-9]+)?|0(\.[0-9]+)?|-0\.[0-9]*[1-9][0-9]*)$`.
5. **Facet pinning and bundle composition (P8-E4/P7-G5):** manifests pin
   exact facet versions + digests; objects may cite the major line. Registry
   semver policy makes minor versions backward-compatible **normatively**;
   composing two bundles pinning different minors of one major line
   resolves deterministically to the highest pinned minor with both
   payload sets re-validated — incompatibility is a reported error, never a
   silent pick.

**Evidence.** Air-gapped estates; registry link-rot; P7's fixed-point proof;
P6's omitted-vs-empty hash fragmentation; the two-digest necessity
established in v0.4 (H1/SOL-9) now made cycle-free.
**Rejected.** Attestation inside the signed manifest (no fixed point);
single digest domain (either breaks stripping or enables the H1 forgery);
IEEE decimals (canonicalization hazard).

## D4 — Nine shallow kernel types; documents are renderings.
*(count updated by D20)* Requirement, RequirementSet, Tailoring, Component,
Implementation, Assessment, Finding, Attestation, **Mapping** — shallow,
typed, referenced; no parts, no document tree, no positional semantics.
Documents are L4 renderings. Evidence unchanged (the #2118/#2112 class; 998
flat BSI controls as fossil record; **CR26 is documents-as-views in
production**). The type-count dogma is formally retired (P7's closing
argument accepted): **semantic completeness beats winning the type-count
argument** — and the ledger claim becomes *nine shallow types replace eight
deep document models* (1.2.2's, including its March-2026 Mapping Model).

## D5 — Component (absorbs System); **identified authorization contexts**; edge-local inductive boundary rule. *(rev. v0.5 — P7-G on authorization scoping)*
**Decision.** As v0.4, with authorization contexts made addressable:

```json
"authorizations": [
  { "id": "https://cso.example/auth/fedramp-high",
    "authority-ref": "https://ns.fedramp.gov/party/jab",
    "scope-label": "FedRAMP High P-ATO",
    "includes": [ "https://cso.example/comp/db", "https://cso.example/comp/api" ] } ]
```

`includes[]` scopes which members belong to this context (default: the
component's full members graph). Absence of `authorizations` remains
**structurally silent** — never a negative assertion. The boundary rule is
unchanged and edge-local: every `inherited-from` edge whose target declares
any authorization MUST carry `basis-ref` — which now points at a specific
**authorization id**, so a service holding both a JAB P-ATO and an agency
ATO can be inherited against the right one. Multi-hop chains remain covered
by induction; D14's one-hop budget intact.
**Rejected (recorded).** Boolean flag (v0.3), defaulted boolean (v0.4 →
dead), separate System type, multi-hop traversal.

## D6 — One `Implementation` edge (comp-def + SSP implemented-requirements unified).
Unchanged: `{component-ref, requirement-ref, statement-refs[]?,
satisfied-by[] (capability-ref | inherited-from{component-ref, basis-ref →
authorization id}), responsibility: provider|customer|shared|inherited,
parameter-bindings, status, evidence-refs[], deviations[]}` *(enum and
`deviations[]` aligned with the delivered schema — P10 #32)*. Evidence: the
public PR #8 retreat; historical Rev4 enums mapping 1:1. Per-clause
responsibility via `statement-refs` is how shared responsibility actually
works.

## D7 — Attestation: content-manifest binding, **bi-modal verification**, verification contract, provenance map. *(rev. v0.5 — P7-B1 + P6-F1 merged)*
**Decision.**
`{subject-semantic-digests[], content-manifest-digest, rendering
{artifact-digest, media-type, template-ref (pinned), renderer}, signer,
timestamp, envelope-ref, provenance-map-ref?}` — the attestation binds the
**content-manifest digest** (which covers every object's package- and
semantic-digest at signing time) and is itself outside that manifest (D3).
Verification is a **normative two-state machine**:

1. **Full Match** — signature valid, content-manifest digest matches the
   delivered bundle: exact packaging and presentation state proven.
2. **Semantic Match** — signature valid, all `subject-semantic-digests`
   match, but the content-manifest digest does not (e.g., annotations
   legitimately stripped, bundle re-packaged): **compliance content proven;
   packaging altered in transit** — reported as such, never as failure and
   never as Full.

The stdlib DSSE profile remains normative about envelope location, exact
signed digest set, signer identity, trust roots, timestamps,
expiry/revocation, and subjects-in-bundle completeness. Template rule
unchanged: annotations may influence only non-normative chrome. Optional
provenance map: statement-id/object-id → rendering anchor.
**Rejected.** Hashing annotation-inclusive semantic payloads; P6's binary as
originally posed — the manifest split plus bi-modal states preserves *both*
the anti-tamper guarantee and the stripping right.

## D8 — `Deviation` sub-object.
Unchanged: `{type (code system), state (investigating → pending → approved |
withdrawn), rationale, approver-ref, opened, refs[]}` on Requirement (the
ex-ante channel, App. A), Tailoring, Implementation, Assessment, and
Finding *(attachment list corrected to the delivered shapes — P10 #32)*. Evidence: four identical historical state machines; CR26
`corrective_actions`; BSI Abweichungspraxis. Its role widens in D13: it is
the audited channel for *every* recognized weakening, not only modality.

## D9 — Statements: identified collection; **normative modality order**; obligated-parties; **elapsed vs. calendar durations**; parameter algebra. *(rev. v0.5 — P8-E2, P7-G on calendars/decimal)* *(rev. v0.6 cycle — R1 #1)*
**Decision.** As v0.4 (`statements[] {id, modality, obligated-parties[],
parameters[], prose: text}` — the `text` language map, née `langMap`;
rev. P10 #37: `text` keys are **lowercase BCP-47** — one tag, one
spelling, the D3.4 discipline — and values are non-empty), completed
where the passes proved it unevaluatable:

**Modality partial order (normative — the lattice `modality-monotonic`
evaluates against):**

```
obligation axis:   unspecified < may < should < must
prohibition axis:  unspecified < should-not < must-not
restriction:       may < may-only          (a permission narrowed is stronger)
incomparable:      {may-only vs should/must} · {any obligation vs any prohibition}
```

`set-modality` without a Deviation is permitted **iff** new ≥ old in this
partial order. Axis reversals (e.g., may → must-not) and all incomparable
moves are never monotone ⇒ Deviation. Design note recorded for the German
customer: **DARF NUR** (may-only) is a restriction — stronger than may,
incomparable with must — exactly as BSI Verbindlichkeitssprache treats it;
the lattice is the first machine-checkable encoding of that distinction.

**Durations split (calendar honesty):**

- `elapsed-duration {num, unit ∈ seconds|minutes|hours}` — computable
  everywhere.
- `calendar-period {num, unit ∈ days|bizdays|weeks|months|years, calendar-ref?,
  timezone?, cutoff?}` — **representable without context, computable only
  with it**: deadline arithmetic over a calendar-period without a resolvable
  calendar context MUST fail closed with an explained error. CR26's
  `bizdays` is the customer evidence; two conformant tools must never
  compute different deadlines from one value (P7's exact objection).

Scalar algebra otherwise unchanged (`string | integer | decimal(canonical
string, D3) | boolean | date | datetime | uri | code`, containers
`choice | list | range`), with the standing escape: what the algebra cannot
type is a `string` plus a facet — never a schema-in-parameter.

**`label` and `default` (rev. v0.6 cycle — R1 #1).** Every parameter
declaration MAY carry `label` (human display handle — never an identifier,
never compared) and `default` (an advisory value, type-valid against the
declaration). Resolution **never substitutes a default silently**: an
unbound parameter stays unbound — binding happens only through
`set-parameter` (D13) — because silent substitution is the two-diverging-
representations corpse in miniature. The measured customer: BSI parameter
labels ("regelmäßig") and suggested `values[]` on 179 requirements, exiled
to the L2 `param-extras` residue solely because the algebra was two
optional fields too spare; the residue drains at the next converter run.

## D10 — Facets: registered, federated, capability-declared, fail-closed; **private: defined harmless; undeclared registered = dangerous.** *(rev. v0.5 — P6-F4 + P7-G4 merged)* *(rev. v0.6 cycle — R1 #7)*
**Decision.** As v0.4 (Portable/Computable split, `modifies-semantics` ⊆
{assessment, tailoring, selection, rendering}, capability declarations,
normative fail-closed), with the two open edges closed in one consistent
rule pair:

1. **`private:` facets carry `modifies-semantics: []` by definition.** They
   are preserved, never validated, and **ignored by every compliance
   computation** — exactly the annotations discipline with structure.
   Smuggling compliance math into `private:` is self-defeating: conformant
   tools are *required* to look away. No fail-closed abort on sight
   (P6-F4's paradox dissolved); the artifact remains capped below Portable.
2. **A registered facet whose descriptor omits the declaration is treated
   as modifying all four classes** — dangerous-by-default, fail-closed
   everywhere (P7-G4's direction adopted for the registered space). The
   burden is on the publisher to declare harmlessness, not on consumers to
   assume it.

`.well-known` stays discovery-only; identity and trust are manifest pins
(D3). Annotations unchanged.

**Declaration-audit promotions (rev. v0.6 cycle — R1 #8).** Three stdlib
facets promote their `modifies-semantics` declarations to what the corpora
show they actually do: `security-objectives@1` → `[selection]`,
`effectivity@1` → `[selection]`, `reporting-obligation@1` → `[assessment]`
(`cr26/scope@1` already declares `[selection]`). The governing directive:
a tool that cannot handle a facet must stop working on that data —
fail-closed only engages when declarations are honest, and a
semantics-bearing facet declaring `[]` is the silent-ignore corpse
(P7-B3) wearing a conformance badge. Gate-2 schemas ship these
declarations; bundle stubs update at the next converter run.

**Per-clause payload keying (rev. v0.6 cycle — R1 #7).** A facet payload
that addresses individual statements of its host Requirement MUST key those
entries as `by-statement: { <statement-id>: <payload> }`, using ids from
the host's `statements[]`; a key naming no statement of the host is a
validation error (checkable by every Portable tool, no facet knowledge
required). Converter-established across 1,015 statements' payloads in six
facets; normative so that a second independent producer cannot legally
invent a divergent keying and fracture per-clause alignment.
**Rejected.** Uniform fail-closed including `private:` (kills the valve);
uniform trust-the-publisher default (props with extra steps).

## D11 — SP 800-53 as Canonical Reference Facet; `oscal-stdlib`.
Unchanged. The stdlib now also carries the **IR 8477 / OLIR relationship
code system** for D20 and the calendar code systems for D9.

## D12 — The extension surface, complete.
Unchanged in structure (eight stdlib facets high/medium confidence;
`privacy-assessment@1` parked pending Rev5-era verification; framework
facets as an open sanctioned category; annotations; ISM = zero facets). One
addition: **`mapping` is *not* here** — mappings are kernel objects (D20),
precisely so that they cannot regress into relation-string props.

## D13 — Tailoring: bounded selection; identity-addressed operations; **weakening rules per operation**; deterministic resolution. *(rev. v0.5 — P6-F2, P7-B2, P8-E3, P7-U)* *(rev. v0.6 cycle — R1 #2)*
**Decision.** As v0.4 (set-ref or the three bounded predicates — B.2's
`field-equals` · `param-equals` · `present`, exactly one, schema-bound
since P10 #31; closed op vocabulary addressed by requirement-ref +
statement-id + name), completed:

**Operation-level weakening rules (replacing the overbroad v0.4 claim
"weakening ⇒ Deviation", which P7-B2 correctly showed was only enforced for
modality):**

| Operation | Rule |
|---|---|
| `set-modality` | monotone per the D9 order, else Deviation |
| `set-parameter` | MUST validate against the parameter's declared type / cardinality / choices / range (P6-F2); out-of-bounds only via Deviation. Additionally, an authority MAY declare per parameter `tightening: lower | higher | none`; a change against the declared direction ⇒ Deviation (CR26 deadlines would declare `lower`) |
| `detach-facet` | Deviation when the facet's `modifies-semantics` ≠ [] — the declaration read from the stdlib descriptor **or the manifest pin**; a facet id that is neither stdlib, nor pinned, nor `private:` is an **error at any tier** (dangerous-by-default, D10; P10 #29) |
| `replace-prose` | carries `intent: editorial | substantive`; substantive ⇒ Deviation |
| `set-field` | whitelisted non-normative fields only (`title`, `label`, `annotations`) — the whitelist is a schema enum since the P9 cycle; `sequence` struck v0.6 (it lives on Set members, which operations cannot address — backlog #21); anything normative goes through its own operation |
| `attach-facet` | Deviation when the attached facet's `modifies-semantics` ≠ [] (symmetric with detach — B.3; same registration rule — P10 #29) |
| `add-relation` / `remove-relation` | informative edges are free; **removing a `required` edge ⇒ Deviation** (B.3 — dropping a dependency weakens the graph; enforced since backlog #25). Normative cross-framework claims are Mapping objects, D20, with their own lifecycle |
| `excludes` | **selection, never weakening — no Deviation** |

The last row is a documented **rejection of P7-B2's "exclude always
requires Deviation"**: excludes define scope — ISM's five classification
baselines and FedRAMP's classes are *made of* excludes; requiring a
Deviation per exclusion would drown every baseline in thousands of
pseudo-deviations and kill the mechanism that absorbs 5,900+ membership
props. Weakening means softening a *selected* obligation; selection is not
softening. (P7 itself conceded a universal weakening detector is
infeasible; this table is the honest bounded substitute.)

**Deviation duties bind at consumption, not authorship (rev. v0.6 cycle —
R1 #2).** A Deviation records an *implementation's* departure from its
governing resolved set. A Tailoring **published at Authority tier is
itself normative source**: its operations are authorship variance, and the
per-operation Deviation requirements in the table above do not apply to it
— FedRAMP publishing four class variants is not FedRAMP deviating from
FedRAMP. The weakening classification itself is still computed and
reportable (a consumer may always ask "which classes ease the base?" —
CR26's measured answer across 111 class-variant modality moves: zero),
but no Deviation object is required, synthesized, or implied. Consumer-
tier Tailorings keep the full table; the audited-escape channel is theirs.
The measured customer: 29 variant-only CR26 rules + 5 KSI variants whose
converter had to synthesize base prose just to have something to
"deviate" from — ceremony without a wronged party. **Rejected:** a
`variants` carrier on Requirement — authority-published variance is 1-of-3
in the census and its mechanism (Tailoring) already exists, so it fails
the D22 promotion bar on tests 1 and 2.

**The tier anchor — layered (rev. v0.6 cycle — R3 #19; rev 4 at gate
3).** The tier that decides Deviation duties is DERIVED from data,
never stipulated: (1) **authority-claimed** iff the Tailoring's id URI
origin (scheme + host) equals the single origin of the selected
**content** — resolved *through* selected Sets to their member ids
(transitively, D21) and through the operations' `requirement-ref`
targets, never stopping at a wrapper Set's own id: gate 3's CR26
`rev5-odp-overlay` (a FedRAMP-minted Set around NIST controls) proved
the wrapper shortcut launders consumer into authority-claimed, and the
same resolution equally recognizes an authority's own content behind a
foreign-minted wrapper. A predicate select or mixed-origin content
blocks the claim, because tailoring across authorities' content is
consumer work by definition; (2) **authority-proven** iff additionally
(or instead — proof beats prefix) an in-bundle Attestation whose signer
shares the selected content's origin lists the Tailoring among its
subjects with a verifying semantic digest — and, **in verification mode
(gate 4, #24: trusted keys supplied), iff that Attestation's DSSE
envelope verifies**; an unsigned attestation proves nothing to a
verifying consumer, and a validator without keys reports the digest
match as UNVERIFIED rather than granting proof; (3) otherwise
**consumer**.
Duties bind at consumer tier only; conformant tools report claimed and
proven distinctly, because a prefix is an honest-publisher signal while
a signature is evidence — the same layering as the two digest domains.
Derivation vectors: `tier-vectors.json` (9 cases, incl. proof rescuing
a cross-origin id, an authority attestation over the wrong subject
proving nothing, and the wrapper-Set laundering case).

**Deterministic resolution (normative algorithm, Appendix B):** operations
are an **ordered list**, applied sequentially after selection; **two
operations addressing the same target within one Tailoring = validation
error** (overrides happen auditable via Tailoring-of-Tailoring chaining,
never silently; enforced in bundle validation since the P10 fix pass —
#30); independent Tailorings over one catalog are separate
artifacts — there is **no auto-merge**, by design and by history (1.x
merge semantics are the corpse in the basement). Hop budget harmonized with
D14 (P8-E3): one shared predicate vocabulary, one budget — at most one
reference hop, everywhere.

## D14 — Rules: eight primitives, one bounded conditional, **no general-purpose expression language.** *(rev. v0.5 — wording P8; tier P8-E1)*
Unchanged in substance. `attestation-binds` evaluation moves to **Portable**
(Core treats Attestation objects as schema-valid data) — resolving P8-E1's
Core/JCS contradiction. The ledger phrase is corrected to the defensible
form: primitives + ops + predicates are a small closed DSL; what the design
excludes is a *general-purpose* expression language — the distinction that
matters for complexity re-inflation.

## D15 — Conformance: **Core is the passive tier**; normative feature × tier matrix. *(rev. v0.5 — P7-B3 + P8-E1)*
**Decision.** Core is redefined as **passive**: validate kernel structure,
verify package digests, resolve references locally, **preserve everything
unknown** — and perform **no semantic computation whatsoever**. All
computations of the four classes (tailoring resolution, assessment,
selection, normative rendering) plus JCS/semantic digests and
`attestation-binds` begin at **Portable**. A Core processor encountering
facets preserves them and refuses semantic computation over affected
objects — the silent-ignore state P7-B3 exposed is unrepresentable.

| Feature | Core | Portable | Authority |
|---|---:|---:|---:|
| Kernel schemas incl. statements[], all nine types | Required | Required | Required |
| Local (manifest) resolution · sealed mode · package-digest verification | Required | Required | Required |
| Structural primitives (`references-resolve`, `digest-verified`, `unique-within`, `code-from`, `prose-params-resolve`) | Required | Required | Required |
| Preservation of unknown registered facets & annotations | Required | Required | Required |
| **Any semantic computation** (tailoring, assessment, selection, normative rendering) | **Forbidden** | Required (fail-closed rules apply) | Required |
| Registered-facet schema validation · capability declarations · fail-closed | — | Required | Required |
| Semantic digests (JCS) · `attestation-binds` · `modality-monotonic` · `conditional-apply` | — | Required | Required |
| Exact facet version+digest pinning; bundle-composition resolution | — | Required | Required |
| Publication duties (stable ids, alias/lineage records, both digests, `.well-known`, deprecation lifecycle, calendar refs for calendar-periods) | — | — | Required |

RFC-0024's approved-format slot maps to **Portable**.

## D16 — Migration: three guarantee levels; "information-preserving for the supported corpus."
Unchanged in structure (native / compatibility-facet /
opaque-preservation) — and **measured at gate 4**: the kernel→1.x
export exists as `export_oscal.py`, validated against the official NIST
1.2.2 catalog schema, with a generic re-importer proving
**5,886/5,886 catalog objects round-trip to semantic-digest equality**
(5,647 at gate 4; the P10 ISM-taxonomy repair added the recovered sets).
The D16 asymmetries are now counted rather than predicted: OSCAL groups
cannot mix subgroups and controls; params require label|select; link
`rel` is a token, so URI-typed relation vocabularies cannot ride 1.x
links; overlapping Set membership (baselines) has no catalog-model
representation at all. The 1.2.2 Mapping Model becomes a native-mapping
source/target for D20 objects (mapping/profile-model exports are the
next expansion).

## D17 — Declared non-goals.
Unchanged (flows as linked resources; template accreditation open (R6);
narrative grammar optional; executable proof deferred to the gate) — plus:
**PCI's customized approach and ISO's management-system clauses are named
extension targets, not covered claims** (P7/P8 coverage verdicts adopted
verbatim into the coverage table).

## D18 — XML transit projection, strictly fenced.
Unchanged: kernel+stdlib authored in a transit-safe schema subset with
guaranteed strict XSD; third-party facets opaque unless publisher-mapped;
one-way, never authoring; consequence documented (R11).

## D19 — Positioning.
Unchanged: engine that compiles to 1.x during transition; sunset trigger;
name avoids "2.0"/"profile" — **fixed 2026-07-22: JASCON** (register
naming entry; the trademark-optics question that shaped the old working
title — "OSCAL" is NIST's mark — is retired by the rename; residual
pre-tag items are the author's DPMA/EUIPO/USPTO screen and domain
registration); on-ramps stated accurately (#58 and #2050 live; #2115/#2116 closed
design positions); RFC-0024's five-CSP clause recorded without endorsement.

## D20 — **`Mapping` as the ninth kernel type.** *(new, v0.5 — P7 mapping analysis accepted over P8's facet alternative)* *(rev. v0.6 cycle — R1 #5)*
**Decision.** A shallow first-class object:

```json
{ "id": "https://scf.example/map/nist-ac2--iso-a5.16",
  "version": "2026.2",
  "lifecycle": "active",
  "source-ref": "https://ns.nist.gov/sp800-53/req/AC-2",
  "source-scope": ["statement:a"],
  "target-ref": "https://ns.iso.example/27002/req/5.16",
  "relationship": "subset-of",        // stdlib code system: IR 8477 / OLIR
                                       // equal | subset-of | superset-of |
                                       // intersects | supports | conflicts
                                       // + supplements (JASCON
                                       //   extension code, v0.6 cycle)
  "direction": "source-to-target",
  "confidence": "reviewed",
  "rationale": {"en": "…"},
  "provenance": { "author-ref": "…", "date": "…" },
  "evidence-refs": ["…"] }
```

Many-to-many is many objects; statement-level scoping via `source-scope`/
`target-scope`; version pinning via normal L0 references; contradictory
mappings from different authorities coexist as distinct objects with
distinct provenance — consumers choose by authority, exactly as they do
with catalogs.

**`supplements` (rev. v0.6 cycle — R1 #5).** One relationship code added
beyond the adopted IR 8477 set, clearly marked as a JASCON stdlib
extension: *source attaches additional normative content to target* — the
clause-precision attachment of the supplement pattern (D21), e.g.
`target-scope: ["statement:s2"]` on the upstream anchor. It is not a
crosswalk claim: `supplements` does **not** chain in the Chapter 8
composition arithmetic (degrade as `supports`), and OLIR-facing exports
MAY down-translate it to `supports` losslessly for that reason.

**Evidence.** SCF's raison d'être is mapping 1,500+ controls to 200+
frameworks; CIS and CSA ship mapping documents as core products; NIST
publishes OLIR; CR26 itself carries 263 KSI→800-53 mappings; and NIST just
shipped an **entire eighth document model** for mappings (March 2026) —
proof of demand, and proof of the 1.x pattern (a deep document tree with
uuid/metadata/revisions and props throughout) this kernel exists to
replace.

**Rationale (north star applied).** *Customer:* the mapping graph **is** the
product for SCF/CSA/CIS and the multi-framework reality of every regulated
enterprise. *Simplicity:* one nine-field shallow object replaces a full
document model. *No props / no bespoke:* without a first-class home,
mappings regress into `relations`-type strings (props by another name) and
SCF stays on bespoke Excel/JSON — the two exact failure modes the north
star forbids. **Rejected:** P8's stdlib-facet variant — facets attach *to*
objects, but a third-party crosswalk (SCF mapping NIST↔ISO) belongs to
neither endpoint and needs its own identity, lifecycle, and provenance;
the type-count argument (retired in D4).

## D21 — **Hierarchy and ordering, normatively.** *(new, v0.5 — P8 hierarchy gap)* *(rev. v0.6 cycle — R1 #5)*
**Decision.** RequirementSets nest: `members[]` entries are
`{ref (requirement **or set**), sequence}`; `sequence` is a defined kernel
field (ascending integer, unique within one members list, presentation
order — no normative semantics beyond order). Taxonomies are nested sets:
CSF Functions → Categories → Subcategories, SCF's 34 domains, ISO 27002
themes, CIS Controls → Safeguards — all sets-of-sets with sequence; ISM's
`sort-id` ×1,150 absorption is thereby *specified*, not just asserted.
Membership graphs are **DAGs** (rev. P10 #39): overlapping membership is
legal — baselines are made of it — but a membership **cycle is a
validation error**; the rule's first enforcement run recovered 239 ISM
taxonomy sets that a converter slug collision had silently merged.
**Rejected.** Reintroducing group/part nesting on Requirements (the #2118
attractor); order-as-annotation (props by another name).

**Named pattern (rev. v0.6 cycle — R1 #5): the supplement pattern.**
Amending a catalog you do not own is composition, never injection: the
supplement author publishes new Requirements under their **own** prefix and
composes them with the upstream via a **shadow set** — a Set under the
supplement author's identity whose `members[]` interleave upstream refs and
additions by `sequence`, with multi-authority membership safe under D2
global identity. Clause-level attachment binds by reference (a `relations`
edge or a statement-scoped Mapping speaking `supplements`, D20), because
foreign statements live inside the owner's object and semantic digest. What
profile resolution used to *produce*, the shadow Set *is*; the interleaved
reading view is an L4 rendering per D4. The corpse is measured: eleven
shared ids across two publications of one authority, ten silently diverged
— forking-to-amend at inter-organizational scale. (Handbook §6.A; Appendix
F Q23.)

## D22 — **Kernel promotion rule.** *(new, v0.6 cycle — review round 1, backlog #4)*
**Decision.** A semantic is promoted from facet space into the kernel
**only** when all three tests hold:

1. **≥ 2 of 3 independent authority encodings** in the census corpus
   (convergence, not committee preference);
2. **one shared computation** every generic tool must perform on it
   (modality: monotonicity checking);
3. **one vocabulary fits all corpora without flattening** (modality: one
   lattice; counter-example: security-objective values "1"/"0" share no
   scale with anyone).

A candidate that passes test 1 but whose kernel *mechanism* already exists
is absorbed by that mechanism, not by a new field — assurance levels are
the instructive case: genuinely 3-of-3, yet level-as-a-field is the
5,301-marker corpse; level-as-a-Set composes, while the incommensurable
vocabularies stay in `assurance-levels@1` (a cataloged, parked stdlib
design — appendix D.8; it ships when a corpus demands the payload shape,
per the P10 #35 verdict). Future "why isn't X kernel"
disputes cite this rule; a promotion PR that cannot show its three passes
is rejected without further argument — the anti-#2118 discipline applied
to the kernel itself.

**The anticipated-convergence path (second clause, same cycle).** The
census population is three; a consensus of the *current* customers is a
floor, not a ceiling. Promotion is therefore also permitted when (1) a
major authority in the census ships the semantic and depends on it, (2)
general use by other frameworks is credibly anticipated, with the
anticipation argued in the register, and (3) the absorption clause above
still holds. The discipline that keeps this honest: such a promotion
carries evidence tier **anticipated** — below measured, explicitly
labeled — and is re-verified against every corpus addition; an
anticipation that fails to materialize after two gate cycles demotes the
semantic back to a facet, the backlog standing rule applied to the kernel.
The motivating example: a glossary is 1-of-3 today (CR26's FRD — 75
terms, 188 aliases, 264 references resolving), yet every national
framework publishes terminology; the computation (alias-aware term
resolution) is already measured. The re-audit of the facet space under
this clause is recorded in the register amendment.
**Closed at 1.0 (D22 rev 3, rc.1 consolidation).** As scheduled by
D22 rev 2, the anticipated-convergence path expires with this release:
it was available only pre-1.0 (demotion would strand content against
closed kernel shapes with no migration rule), and it closes **unused** —
zero promotions ever rode it (terminology landed via the absorption
clause). Post-1.0, kernel promotion requires measured 2-of-3 and a
major version under D3.5 governance.
**Customer.** Every authority pays for every kernel field forever (a tax on
each Core validator); the census is the only party that may levy it.
**Simplicity.** The bar is three questions with countable answers.
**Complexity ↓.** Ends promotion-by-advocacy — the historical re-inflation
channel by which cores grow until they require a metaschema.
**Trade-off.** A genuinely novel semantic with only one national encoding
waits in a facet until a second authority ships it — deliberate: the
kernel lags evidence, never leads taste. First stated publicly in Appendix
F Q22; normative here.

---

# Part III — Worked examples

III.1 (BSI KONF.14.1), III.2 (CR26 IEC rule + class Tailoring), III.3
(ISM, zero facets) carry over from v0.4 unchanged in substance, with two
corrections: III.2's effectivity dates differentiated
(`optional-adoption: 2025-11-01`, `must-obtain-by: 2026-07-04`,
`grace-until: 2027-01-01` — illustrative), and the class Tailoring now
demonstrates the parameter-bounds rule (setting `iir-deadline` to a value
outside a declared range would fail without a Deviation). New:

## III.4 — A cross-framework mapping (SCF-shaped)

```json
{ "id": "https://ns.scf.example/map/2026-2/ac-2--iso-5.16",
  "version": "2026.2", "lifecycle": "active",
  "source-ref": "https://ns.nist.gov/sp800-53/req/AC-2",
  "target-ref": "https://ns.iso.example/27002/req/5.16",
  "relationship": "intersects", "direction": "source-to-target",
  "confidence": "reviewed",
  "provenance": {"author-ref": "https://ns.scf.example/party/scf", "date": "2026-05-01"} }
```

Props: 0. Bespoke spreadsheet columns: 0. The SCF corpus becomes a package
of such objects plus its framework facet.

---

# Part IV — Ledger, risks, gate, changelog

## IV.1 Complexity ledger

**Removed vs. OSCAL 1.2.2:** eight deep document models (incl. the
March-2026 Mapping Model) · Metaschema · profile-resolution algebra + merge
strategies · XML/YAML conformance + serialization mapping · Schematron ·
anonymous inline constraints · comp-def/SSP duplication · general JSON
Patch. **Kernel:** 9 shallow types · 2 sub-objects · 1 serialization · JSON
Schema 2020-12 · 8 primitives + a closed op vocabulary + 3 predicates ·
**no general-purpose expression language** · 0 document conventions. The
six retained subsystems (kernel schemas; content-manifest protocol; facet
system; rule interpreter; tailoring resolver; attestation protocol) are
each narrower and more boring than what they replace — a claim now
**measured** (gate 4, `drafts/gate-4-measurement.md`): the complete
reference validator — twelve vector families, both digests, closure,
facet enforcement, tier derivation, op-law, Ed25519/DSSE, composition,
conditional-apply — is **994 non-blank, non-comment lines of Python**
(+ jsonschema) and **1,163 lines of zero-dependency PowerShell 5.1**
(at the P10 fix-pass commit; the gate-4-commit figures were 938/1,110),
against **30,905 lines / 162 files** for compliance-trestle 4.2.0, the
OSCAL 1.x validator+resolver toolchain (tests excluded) — **≈30×
each** (31×/27×), ~14× combined. Measured
size deltas versus the OSCAL sources: ISM −29 %, GS++ −50 %,
CR26 +55 % — smaller where sources are redundant, larger where a
bespoke format was terse.

## IV.2 Risk register (delta)

R1–R12 carry over with status updates (R4 softened by pinning+composition
rule). New: **R13** — IR 8477/OLIR relationship code-system governance
(stdlib ownership); **R14** — calendar-context dependency: calendar-periods
are honest but push a real-world dependency (holiday calendars) into
Authority publication duties; **R15** — CIS corpus status unverified — **RESOLVED 2026-07-21**: both
CIS corpora converted and measured (Controls v8.1; Ubuntu 24.04
Benchmark with 635 mappings and recovered profile baselines).

## IV.3 Prior art (delta)
Add: **NIST OSCAL 1.2.2 Control Mapping Model** — as demand evidence *and*
as the negative pattern (deep document model, props throughout) D20
replaces; NIST IR 8477 / OLIR (relationship semantics).

## IV.4 Coverage table (P7/P8 verdicts adopted)

| User | Verdict | Basis |
|---|---|---|
| BSI, ASD, FedRAMP CR26 | Designed-for, **measured corpora**, proof at gate | census |
| NIST 800-53 | **Measured** (gate 3): Rev 5.2.0 + four 800-53B baselines, 115,680 leaves, zero kernel changes; all 373 pre-existing corpus mapping endpoints resolve | `US.SP800-53` |
| NIST 800-171 | Designed-for (D11 + sets/tailoring) | catalog layer |
| NIST CSF 2.0 | **Measured** (gate 3): 3-level D21 nesting, sixth declarative corpus, the 1.1→2.0 tombstone graph on `replaces[]` | `US.CSF` |
| NIST full lifecycle (SSP/AP/AR/POA&M) | **Measured** (gate 3): the five lifecycle types at document scale with both digests; D5 inheritance via the leveraged pair; #9 seeds confirmed with zero enum additions | `US.IFA-GoodRead` |
| CIS | **Measured**: Controls v8.1 + Ubuntu 24.04 Benchmark (635 D20 mappings; recovered profile baselines) | `CIS.Controls` · `CIS.Ubuntu2404` |
| SCF | Catalog + **D20 mappings** (its central use case now first-class) | |
| CSA CCM | Controls + CAIQ→assessment-criteria plausible; mappings via D20; full STAR package not claimed | |
| ISO 27001/27002 | Structurally adaptable (attributes → framework facet; sealed manifests help licensed distribution); **management-system clauses not covered** — named target | |
| PCI DSS | Testing procedures → assessment-criteria; compensating controls → Deviation; **customized approach encoding undefined** — named target | |

## IV.5 The v0.6 gate — DELIVERED IN FULL (items 1–4, 2026-07-21/22)

1. Full-corpus converters + computed coverage for ISM, BSI, CR26 — zero
   unexplained fields.
2. Executable kernel + stdlib JSON Schemas; conformance corpus incl. JCS
   vectors (with empty-omission cases), modality-lattice cases,
   parameter-bounds cases, tailoring-conflict cases, bi-modal attestation
   cases. **DELIVERED 2026-07-21:** `jascon/schemas/` (kernel
   schema, closed shapes, shape-disjoint type inference + six normative
   stdlib descriptors with the D10-rev-2 declarations) ·
   `jascon/conformance/` (54 vectors across five families at first
   delivery; **129 across nine families at gate 3** after the P9 +
   v0.6-round-2 + gate-3 additions — recompute via `validate_core.py`,
   backlog #28) ·
   `jascon/scripts/validate_core.py` (the executable). Measured
   result: all vectors pass; all 8 corpus bundles + the example bundle
   validate green — 5,478 object validations, both digests re-verified
   per object, by-statement keys and `{param:}` bindings checked, every
   object matching exactly one kernel shape; all nine types exercised.
   P9 scope correction: 5,478 = 5,470 manifest-listed objects + 8
   manifest checks; the example bundle's 13 objects (the only instances
   of the five lifecycle types) are shape-checked without digest
   verification. Appendix-B items parked "at gate item 2" (B.1.3 negative corpus,
   B.1.8 conditional instantiation, B.1.7 DSSE profile) were re-parked
   in backlog #18 rather than silently closing — and **closed at gate 4**
   (dsse 5 · composition 7 · conditional 8 vector families with their
   engines; disjointness cases cover B.1.3). Vector count at rc.1: 149;
   **157 after the P10 fix pass** (parameter 17→19, tailoring 15→19,
   reference 11→13).
3. **Lifecycle corpus** beyond catalogs. **DELIVERED 2026-07-22 (gate
   3, IV.6 row):** the IFA GoodRead set (SSP/AP/AR/POA&M + the
   leveraged/leveraging pair + component-definition) exercises all five
   lifecycle types at document scale with both digests; #9 seeds
   CONFIRMED with zero enum additions; #10 CTL/ODP addressing decided
   by measurement and DRAINED (16 set-parameter ops on the
   `rev5-odp-overlay` Tailoring). The wishlist residue is scoped, not
   silent: CSA CAIQ, SCF mappings, and PCI customized-approach cases
   remain *designed-for* corpus expansions (IV.4).
4. Measured complexity comparison — the weekend-validator acceptance
   test + the bidirectional export suite. **DELIVERED 2026-07-22 (gate
   4, `drafts/gate-4-measurement.md`):** two languages (Python 938 LoC
   + jsonschema; PowerShell 5.1 1,110 LoC + nothing) vs
   compliance-trestle 4.2.0 (30,905 LoC / 162 files) — ~30× with the
   crypto engines included; 149/149 vector parity; full-corpus
   wall-clocks stated (py ~50 s, PS 759 s — the zero-install tax).
   Export: 10/10 catalog bundles schema-valid against the official NIST
   1.2.2 release schema, round-trip **5,647/5,647** objects to
   semantic-digest equality — down-conversion is *measured*.
   Authorship recorded honestly (register R8): same author + AI;
   independence = language/runtime; the third-party clean-room build
   is the standing invitation. *(At the P10 fix pass the suite is 157
   vectors and the repaired ISM taxonomy lifts the round-trip to
   **5,886/5,886** — re-measured, ALL GREEN in both validators.)*

## IV.6 Amendment history (compact)

The full journal — every finding, adjudication, and rejected
alternative — lives in the **Decision Rationale Register** and the git
history. The compact line:

| Cycle | Date | What happened | Register section |
|---|---|---|---|
| v0.1 → v0.5 | 2026-07-14…18 | Six adversarial passes + census r1/r2; the architecture stabilized; Mapping promoted (D20), hierarchy normative (D21), promotion rule (D22) | D1–D22 |
| v0.6 round 1 | 2026-07-19…21 | External review round 1 adjudicated: parameter `label`/`default` (D9 rev), consumption-tier duties (D13 rev), by-statement keying (D10 rev), supplement pattern (D20/D21 rev) | "Amendments — v0.6 cycle" |
| Gate 1 + validation corpora | 2026-07-19…21 | 3 census + 5 validation corpora at 100 % / UNMAPPED 0 | conversion reports |
| Gate 2 | 2026-07-21 | Kernel schema + stdlib descriptors + validator + 54→115 vectors; P9 twin red-team runs adjudicated (#16/#17/#19 closed) | "P9-applied" |
| v0.6 round 2 | 2026-07-22 | P9c re-review + deep-research items: op-law completed, tier reported, canonical-alias self-policing, decimal canonical form; #12 `text` decided (EU-27 rationale) | "Amendments — round 2" |
| Gate 3 | 2026-07-22 | NIST Rev 5.2.0 + 800-53B + CSF 2.0 + IFA lifecycle; zero kernel-schema changes; #10 drained by measurement; two validator shortcuts falsified and fixed (D13 rev 4, D9 rev 3) | "Amendments — gate 3" |
| Gate 4 | 2026-07-22 | DSSE/composition/conditional engines; the weekend validator (PS 5.1, 149/149); bidirectional export 5,647/5,647; #18/#24 closed | "Amendments — gate 4" |
| Converter rerun | 2026-07-22 | #12 `text` primitive delivered · #20 URI relations · #26 fail-closed pins — **the backlog reached zero** | "Amendments — the converter rerun" |
| **1.0.0-rc.1** | 2026-07-22 | This consolidation; D22's anticipated path closed unused (rev 3) | this row |
| P10 + P10b | 2026-07-22 | Adversarial review of THIS text (no Blockers; #29–#37 filed) + external Gemini review adjudicated (#38–#39 in; G-3/G-4/G-5 refuted) | "Amendments — P10" / "P10b" |
| P10 fix pass | 2026-07-22 | All eleven items closed: op-law completed (pinned declarations, same-target on bundles, predicates schema-bound), D21 acyclicity — whose first run recovered **239 silently-merged ISM taxonomy sets** (corpus 6,675 → 6,914 objects; export 5,886/5,886); Part II aligned to the delivered schema; vectors 149 → 157; `DE.BSI` rename; errata swept | "Amendments — the P10 fix pass" |
| **1.0.0** | 2026-07-22 | Released at tag `v1.0.0`; machine identifiers keep the working-title string by the tag-time decision (opaque strings, D2) | "Amendments — v1.0.0" |

## IV.7 Release artifacts (what this specification ships with)

Everything below is in the repository, reproducible, and green at the
rc.1 commit:

- **Kernel schema** `jascon-1.0.0.schema.json` — closed
  shapes, shape-disjoint type inference, 9 types + Deviation + manifest;
  the `text` primitive (`{BCP-47: string | [string]}`) on every
  human-readable field.
- **Seven stdlib facet descriptors** (incl. the normative DSSE envelope
  profile) — pinned VERBATIM wherever bundled; divergence is a
  validation error.
- **Conformance corpus**: **157 vectors, 12 families** (jcs 8 ·
  modality 21 · parameter 19 · tailoring 19 · attestation 5 · facet 7 ·
  reference 13 · lifecycle 36 · tier 9 · dsse 5 · composition 7 ·
  conditional 8).
- **Two reference validators**: `validate_core.py` (Python, jsonschema
  only) and `validate_core.ps1` (PowerShell 5.1, zero dependencies —
  the stock Windows box every auditor already has). Full parity;
  numbers in `drafts/gate-4-measurement.md`.
- **Bidirectional export**: `export_oscal.py` — OSCAL 1.2.2 out,
  validated against the official NIST release schema; generic
  re-import; 5,886/5,886 round-trip.
- **Eleven corpus bundles** under `converted_examples/` (twelve source
  publications counting 800-53B separately, §2) — 6,914
  manifest-listed objects, both SHA-256 digests re-verified per object,
  each with a computed coverage report (UNMAPPED = 0) that declares
  every rule and reports source defects rather than repairing them.
- **The normative appendices** — A (shapes) · B (primitives,
  operations, predicates — the deterministic resolution algorithm) ·
  C (code systems) — at `jascon/references/appendix-{a,b,c}-*.md`,
  with the handbook chapters ch01–ch15 and appendices D–G beside them.
- **The Decision Rationale Register** —
  `drafts/jascon-decision-rationale-register.md`: the full
  amendment journal this text compacts (IV.6).
- **The reader** (`one-page-apps/jascon-reader.html`, v1.7.1) —
  a zero-dependency single-file browser, authoring workbench, and
  digest verifier.

## IV.8 From rc.1 to 1.0.0

1. **The name** — ✓ fixed: **JASCON** (2026-07-22, register naming
   entry; machine-identifier migration is decided with the tag).
2. **P10** — ✓ done twice over (2026-07-22): the in-repo adversarial
   round (findings #29–#37, no Blockers) plus the external Gemini
   round, adjudicated (#38–#39 in; three findings refuted); the fix
   pass closed all eleven items the standing way — register
   "Amendments — P10 / P10b / the P10 fix pass".
3. **Tag `v1.0.0`** — ✓ tagged 2026-07-22 on the author's go. Machine
   identifiers remain in the working-title spelling by the tag-time decision
   (title block; register "Amendments — v1.0.0"). From here,
   kernel-shape changes ride major versions under D3.5 governance, and
   the anticipated-convergence path stays closed (D22 rev 3).
