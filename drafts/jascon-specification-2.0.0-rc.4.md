# JASCON — "Kernel + Registered Facets"
## Specification 2.0.0-rc.4
### release candidate, 2026-11-13 · the 1.0.0 text (released 2026-07-22) amended by CP-RISK-1 (Risk, the tenth kernel type), CP-CHECK-1 (Check, the eleventh), CP-ADVICE-1 (advice packs) and CP-AUTHOR-1 (who decided, and when) · NOT tagged — both reference validators are green on this candidate, the PowerShell twin on Windows PowerShell 5.1 (IV.5b); the tag is the author's decision

> **What changed since rc.3 (2026-11-13).** One decision is new — **D26**:
> who decided and when is spelled one way, `provenance`, and is optional on
> the records and decisions that had no place for it; a Deviation may say
> when it was decided and when it is due for review. No type and no
> primitive is added. D8, D13 and D23 were amended in place and marked
> *(2.0.0-rc.4)*. Fields were added to released shapes, and three fields
> that accepted any string are typed (`Mapping.provenance.date`,
> `Assessment.time`, `Attestation.timestamp`), so this is a new candidate.
> After rc.3 and before this decision, three amendments landed without a
> new candidate: the number domain (D3.9, NUMBER-1), the run rules of
> CHECK-12, 13 and 15, and the code-point comparisons of the PowerShell
> twin (IV.6). The proposal is `drafts/CP-AUTHOR-1.md`; the journal is the
> register, "Amendments — the open backlog before 2.0.0" and "CP-AUTHOR-1
> landed". The rc.3 file is gone from the tree (git keeps it).

> **What changed since rc.2 (2026-11-12, the same day).** One decision is
> new — **D25**, advice packs: a vendor's recommendations as one published
> file, with rules that keep such a file from changing what is required or
> how it is assessed. No type and no primitive is added. D3, D5, D6, D8,
> D13, D15, D22 and D24 were amended in place and marked *(2.0.0-rc.3)*.
> Three things change released shapes and make this a new candidate: a
> Component may name the product version it describes (`product-version`);
> a capability may name clauses (`statement-ids`); and two fields that
> 1.0.0 left as free text are typed (`Deviation.opened`, the `due` of a
> Finding's action), which **ends the property that every 1.0.0 bundle is
> a 2.0.0 bundle** for bundles that used free text there. The author's
> twelve decisions of that day are in `drafts/CP-ADVICE-1.md` §14 and in
> the register, "Amendments — CP-ADVICE-1 and the decisions before the
> tag". The rc.2 file is gone from the tree (git keeps it).

> **What changed since rc.1 (2026-11-12).** One decision is new — **D24**,
> `Check` as the eleventh kernel type with `check-verdict` as the tenth
> primitive. D4, D14, D15 and D22 were amended in place and marked
> *(2.0.0-rc.2)*. D22 gained the consumer-side clause under which Risk and
> Check enter the kernel; the paragraph that recorded Risk as an exception
> now refers to that clause. An eleventh kernel type is a new candidate, so
> this file is rc.2 and the rc.1 file is gone from the tree (git keeps it).
> The proposal, its census and the author's six decisions are
> `drafts/CP-CHECK-1.md` (§13); the journal is the register, "Amendments —
> CP-CHECK-1".

> **What changed since 1.0.0.** One decision is new — **D23**, `Risk` as the
> tenth kernel type with `risk-coverage` as the ninth primitive. D4, D8,
> D14, D15 and D22 were amended in place where they count types or
> primitives or state the promotion rule; §2, §3, Part III and Part IV
> follow. Nothing was renumbered and nothing in the 1.0.0 text was
> weakened. The proposal, its landing review and the author's decisions
> are `drafts/CP-RISK-1.md`; the journal is the Decision Rationale
> Register ("Amendments — CP-RISK-1" onward). The released 1.0.0 text
> stays beside this file, unchanged.

> **Amended after an external review of rc.1 (2026-11-10, same file).**
> Nine findings, each reproduced against the validator first; record in
> `drafts/CP-RISK-1.md` §13. D23 changed in substance at four points — who
> *justifies* (an assessed Risk with a chosen option, not any live one),
> *where* (`tailoring-refs`), RISK-13 (one scale) and RISK-14 (name the
> Tailoring) — and D13 gained typed `selects` / `excludes`. Nothing was
> tagged in between, so the file keeps its name.

> **Name.** **JASCON** — **J**SON **A**ttestable **S**emantic **C**ompliance
> **O**bject-graph **N**otation; *one notation for every standard, in every
> language*. Every machine identifier carries the name: namespaces under
> `https://ns.jascon.net/`, the media type
> `application/vnd.jascon.attestation+json`, the schema
> `jascon-2.0.0.schema.json` (author decision 2026-11-11, taken in this
> major — IV.9). Digests and signatures made under the earlier identifiers
> do not carry over. Naming history: register, "Amendments — v1.0.0" and
> "Amendments — 2026-11-11".
> Nothing here is endorsed
> by NIST, BSI, ACSC, CCB, CIS, or FedRAMP; the project is maintained in
> personal capacity.

**Status.** A **release candidate.** The 1.0.0 architecture stands as
released; this text adds two kernel types — **Risk** (D23) and **Check**
(D24) — and the two primitives that compute over them. It is a major version by the rule of
D22 rev 3, not because anything breaks: all 6,914 objects of the 1.0.0
corpus validate unchanged under the 2.0.0 schema. *(2.0.0-rc.3)* That is
a measurement of the corpus and no longer a property of the schema: a
1.0.0 bundle that wrote free text into `Deviation.opened` or into the
`due` of a Finding's action is not a 2.0.0 bundle (D8; the five values
in the shipped bundles conform). **Measured at rc.1:** a 258-vector conformance corpus in
fifteen families; the Python reference validator green on it and on
every bundle that ships; the first Risk corpus (two Risk objects
converted from an OSCAL POA&M), and what that corpus shows the fourth
authority's data to lack. **Measured at rc.2 (2026-11-12):** 447 vectors
in sixteen families (`check`: 188); the Python reference green on them, on
the five shipped bundles and on the example folder; the app's JavaScript
port green on the same vectors. **Measured at rc.3 (2026-11-12):** 537
vectors in seventeen families (`kernel`: 25, `advice`: 74); the Python
reference and the PowerShell twin (Windows PowerShell 5.1) green on
them, on the five shipped bundles, the worked advice pack and the example
folder; the app's JavaScript port green on the same vectors. **Not yet measured, said here rather than
below the fold:** Risk's two implementations share one author — the
PowerShell twin, green on 2026-11-11, is independent in language and
runtime only (IV.5b); Risk and Check entered the
kernel under D22's consumer-side clause, which no census authority's data
supports by construction (D22); Check has a worked example and two counted
check corpora, and no runner and no converted check corpus (D24); advice
packs have one worked pack and no pack a vendor published, and two of
their fields entered against D22 on the author's decision (D25); and the coverage figures inherited from 1.0.0 count
source *paths* with a declared destination, not values verified to
arrive (IV.2, R16). Eleven corpora were converted and measured (251,591
source leaf values at path level, UNMAPPED = 0); **five of the bundles
ship** with the repository, six were removed on licence grounds and are
reproducible with the converters (§2). Comparison baseline throughout:
**OSCAL 1.2.2** (the release the export suite was measured against —
eight models including the Control Mapping Model, which arrived with
v1.2.0 in December 2025; the current NIST release at this writing is
1.2.3, August 2026, not re-measured). *(Corrected in the rc.1 review:
this text and the 1.0.0 text dated the Mapping Model "March 2026 with
v1.2.1"; the OSCAL release notes say 1.2.0. Read "March 2026" below and in
the register as "December 2025".)*

**Provenance of this text.** The normative sections (Parts I–II,
Appendices A–C) were amended in place through six adversarial review
passes, three external review rounds, the P9 twin red-team runs, and
four evidence gates; the full amendment journal lives in the
**Decision Rationale Register** (companion document) and the git
history. This release candidate is that text, consolidated: journals
compacted to IV.6, gate results recorded in IV.5, nothing renumbered.
For 2.0.0-rc.1 the same discipline: D23 added, five decisions amended in
place and marked *(2.0.0)*, the gate state in IV.5b. For 2.0.0-rc.2: D24
added, four decisions amended in place and marked *(2.0.0-rc.2)*. For
2.0.0-rc.3: D25 added, eight decisions amended in place and marked
*(2.0.0-rc.3)*.

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
pass → **1.0.0** → CP-RISK-1 (proposal 2026-11-05; landing review, first
Risk corpus and the author's decisions 2026-11-10) → 2.0.0-rc.1 →
CP-CHECK-1 (proposal and census 2026-11-11; the author's decisions
2026-11-12) → 2.0.0-rc.2 → CP-ADVICE-1 (proposal 2026-11-12; the
author's decisions on it and on the open points before the tag, the same
day) → **2.0.0-rc.3**.

---

# Part I — The Evidence Base

## 1. Method

Admitted sources of design authority — every normative element traces to at
least one: (1) **measured 1.x failures** (F1–F10); (2) **adjudicated
adversarial findings** (G, SOL/H, P6/P7/P8 — rejections documented);
(3) **the three-authority census** (ISM v2026.06.18 · BSI GS++/MS-TLS
2026-07 · FedRAMP CR26 v2026.07.14.01).

Principles: **failures unrepresentable, not forbidden** (the 781 list
values that schema-valid BSI documents pack into comma-separated strings
remain the standing proof — register, "Amendments — 2026-11-12: the
packed lists"); **complexity-budget reallocation** (1.x spent the budget on
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

**Measured is not the same as redistributed *(2.0.0)*.** Converting a
publication and shipping the conversion are different rights. A licence
review on 2026-11-10 kept in the repository only the bundles whose
publishers' own terms clearly allow redistributing an adapted form: ACSC
ISM (CC BY 4.0), BSI Grundschutz++ (CC BY-SA 4.0 — the converted bundle
is ShareAlike material) and the three NIST corpora (public domain / CC0).
The bundles of CIS Controls and the CIS Ubuntu Benchmark (terms forbid
derivative works and re-posting), of C5, C3A and CyFun (no licence
statement found) and of FedRAMP CR26 (a U.S. Government work whose
repository states no licence — the doubtful case) were removed. Their
converters and coverage reports remain, and every measurement this text
cites stands as made; it is no longer reproducible from the repository
alone. Register "Amendments — the corpus licence review".

**ISO/IEC 27001 *(2.0.0)*.** The Risk type (D23) encodes the record
clauses 6.1.2–6.1.3 prescribe. It is *designed-for*: no official
machine-readable ISO publication exists to measure against, and none is
claimed.

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
| **Cross-framework mappings** *(new row)* | — | — | KSI→800-53 ×263 | **Kernel `Mapping`** (D20) — external evidence: SCF ×200+ frameworks, CIS/CSA mapping products, NIST OLIR, and NIST's own Mapping Model (OSCAL 1.2.0) |
| **Ex-ante risk record** *(new row, 2.0.0)* | — | threat linkage only (authority side: threat references on 595 of 651 requirements, in `security-objectives@1`) | — | **Kernel `Risk`** (D23) — census **0-of-3**: admitted as an author-decided exception to D22 test 1. Evidence outside the census: three standards prescribing the record (ISO/IEC 27001 with 27005, BSI 200-3, SP 800-30) and one lifecycle corpus (OSCAL POA&M risks ×2) |
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
   domain. *(rev. 2026-11-13: the domain this sentence names was stated
   nowhere and no vector covered it; item 9 states it, backlog #67.)*
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

6. **The kernel-version pin *(2.0.0 — backlog #44, author 2026-11-10)*.**
   The manifest MAY carry `kernel-version` (`MAJOR.MINOR.PATCH`): the
   kernel the bundle's objects were written against. `manifest-version`
   is unchanged — it names the format of the manifest, not the kernel.
   **Absent means 1.0.0**, so every 1.0.0 manifest stays valid and a
   bundle of 1.0.0 content stays readable by a 1.0.0 tool. Two rules:
   **KERNEL-1** — a bundle that carries content the 1.0.0 kernel cannot
   type (at 2.0.0: a Risk, a Finding with `risk-refs` or `check-ref`, a
   Check, an Assessment with `check-results` or `tailoring-ref`, a
   manifest with a pack header, a Component with `product-version` or
   with `statement-ids` on a capability) MUST pin the kernel that can; **KERNEL-2** — a tool that meets a pin it does not
   implement MUST stop and name the pinned version and the versions it
   reads. A 1.0.0 tool, whose manifest shape is closed, rejects a pinned
   manifest at the manifest — one file earlier than before, though still
   without a version in its message; the version appears from 2.0.0 tools
   on. The pin is deliberately not required everywhere: a bundle of
   1.0.0 content stays unpinned and readable by a 1.0.0 tool.

7. **Pinned scale definitions *(2.0.0 — author, 2026-11-10)*.** The
   manifest MAY pin scale definitions under `scales`, entry for entry
   like `facet-schemas`: `{id, exact-version, digest, path}`. A scale
   definition is a small file — `id`, `version`, optional `title` and
   `description`, and `levels`, **listed from lowest to highest**, each a
   `level` code with an optional multilingual `label` and `description`.
   How many levels a scale has and what they are called is the
   organisation's choice; the kernel fixes neither. A scale is a pinned
   artifact, not an object and not a kernel type: it has no lifecycle and
   is not attested on its own, and the count of types stays ten. Three
   rules: **SCALE-1** — a pinned definition has the scale shape, the id
   and version its pin states, and no level twice; **SCALE-2** — a level
   a Risk states on a pinned scale is one of that scale's levels;
   **SCALE-3** *(SHOULD)* — a residual level is not above the level it
   remains of, which the order makes visible; noted, never failed;
   **SCALE-4** — the definition of a level scale MAY carry the
   organisation's `matrix` over two other pinned scales (one cell for
   every pair of their levels, each cell one of its own levels — part of
   SCALE-1), and a rating that states both inputs then states the level
   of their cell or an `override-rationale` (D23). A
   `scale-ref` that no pin answers stays a landmark and its levels
   opaque, exactly as before. A manifest that pins scales names kernel
   2.0.0 (KERNEL-1).
8. **The pack header *(2.0.0-rc.3 — D25)*.** The manifest MAY carry
   `pack`: `{kind ● (code; today the one value `advice`), id ● URI,
   version ● string (opaque, never ordered), title ○ text, publisher ●
   {ref ● URI, name ○ text}}`, closed. A manifest with a pack header is
   the manifest of a pack and pins kernel 2.0.0 (KERNEL-1). The header
   sits in the manifest because the manifest is what a signature binds:
   vendor and release are inside the signed state without a new
   mechanism. A bundle that imported a pack keeps the pack's manifest,
   unchanged, beside its own: `packs/sha256/<hex>`, named by the SHA-256
   of its bytes and never listed, the placement of signature envelopes
   and of the evidence store (D24).

9. **The number domain *(2.0.0 — backlog #67, author 2026-11-13; found
   by an outside report)*.** A JSON number in a bundle is an **integer
   written in plain digits, of magnitude at most 2^53 − 1**
   (9007199254740991): an optional minus, then `0` or a digit other than
   zero followed by digits. No fraction, no exponent, no `-0`.
   **NUMBER-1** — any other number is a validation error: in the content
   manifest, in every object, in every pinned definition and in every
   evidence record and observation file, annotations included, and before
   a digest is compared or a verdict computed. Two reasons, one rule.
   *Range:* beyond 2^53 an IEEE double no longer holds every integer; a
   JavaScript tool reads `9007199254740993` as `…992`, a tool with exact
   integers reads it as written, and the same file has two semantic
   digests and two verdicts. *Spelling:* `1.0`, `1e3` and `-0` are second
   spellings of 1, 1000 and 0; one tool hashes `1.0` as written, another
   hashes `1`. The rule **rejects and never rewrites** (item 4's
   discipline: one value, one spelling, and the spelling is held by
   validation, not repaired at digest time). A tool checks the spelling on
   the text of a file, because a parser forgets it, and the value wherever
   it holds a value without its text. The rule is on the file and not on
   the semantic domain, so that a tool can check it without knowing where
   `annotations` are; a fraction in an annotation is written as a string.
   A quantity that does not fit (a count in nanoseconds, a 64-bit
   identifier, a fraction) is a `decimal`, which is a string and compares
   exactly (item 4). Raw outputs in the evidence store are bytes to the
   kernel; the rule does not reach them. Inside the domain the canonical
   form of every implementation agrees without help, which is why the
   canonical form itself is unchanged. No shipped object carried a number
   outside the domain (measured before the rule was written, on 3,871
   files, and by the validators after it).

**Evidence.** Air-gapped estates; registry link-rot; P7's fixed-point proof;
P6's omitted-vs-empty hash fragmentation; the two-digest necessity
established in v0.4 (H1/SOL-9) now made cycle-free.
**Rejected.** Attestation inside the signed manifest (no fixed point);
single digest domain (either breaks stripping or enables the H1 forgery);
IEEE decimals (canonicalization hazard).

## D4 — Eleven shallow kernel types; documents are renderings. *(rev. 2.0.0 — D23; rev. 2.0.0-rc.2 — D24)*
*(count updated by D20, by D23 at 2.0.0 and by D24 at 2.0.0-rc.2)*
Requirement, RequirementSet,
Tailoring, Component, Implementation, Assessment, Finding, Attestation,
**Mapping**, **Risk**, **Check** — shallow,
typed, referenced; no parts, no document tree, no positional semantics.
Documents are L4 renderings. Evidence unchanged (the #2118/#2112 class; 998
flat BSI controls as fossil record; **CR26 is documents-as-views in
production**). The type-count dogma is formally retired (P7's closing
argument accepted): **semantic completeness beats winning the type-count
argument** — and the ledger claim becomes *nine shallow types replace eight
deep document models* (1.2.2's, including the Mapping Model of 1.2.0).
*(2.0.0)* The tenth type replaces no 1.x model: the predecessor format keeps
`risk` inside assessment-results and POA&M — ex post, a thing an assessor
finds. D23 is the ex-ante record 1.x has no home for.
*(2.0.0-rc.2)* The eleventh type replaces no 1.x model either: the
predecessor's assessment plan names methods and its results carry
observations, and nothing in either holds the condition under which an
observation passes. D24 is that condition, as data.

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
*(2.0.0-rc.3)* Two optional fields. **`product-version`** on a Component:
opaque text for the product version the Component describes (`"7"`,
`"7.2"`). Nothing is ordered or parsed from it; no tool can order the
version strings of arbitrary vendors. It entered on the author's decision
of 2026-11-12, without counted evidence: the alternative, one Component
per product line with the line in the id, needs no field and was the
drafter's proposal. **`statement-ids`** on a capability: the clauses of
its `requirement-ref` that the capability is about (ADVICE-5; D25).
**Rejected (recorded).** Boolean flag (v0.3), defaulted boolean (v0.4 →
dead), separate System type, multi-hop traversal. *(2.0.0-rc.3)* A
structured product block (name, version, vendor) and a list of versions:
both larger shapes for a question nothing computes on.

## D6 — One `Implementation` edge (comp-def + SSP implemented-requirements unified).
Unchanged: `{component-ref, requirement-ref, statement-refs[]?,
satisfied-by[] (capability-ref | inherited-from{component-ref, basis-ref →
authorization id}), responsibility: provider|customer|shared|inherited,
parameter-bindings, status, evidence-refs[], deviations[]}` *(enum and
`deviations[]` aligned with the delivered schema — P10 #32)*. Evidence: the
public PR #8 retreat; historical Rev4 enums mapping 1:1. Per-clause
responsibility via `statement-refs` is how shared responsibility actually
works.
*(2.0.0-rc.3)* **`capability-ref` has a grammar.** Until now it was a
free string, written four ways in this repository. A bare capability id
names a capability of the edge's own component; `<component-id>#<capability-id>`
names a capability of that component. The reference is closure-required:
the named component is in the bundle, the capability exists on it, and a
component other than the edge's own is one of its `members` (ADVICE-7).
The second form is how a vendor's advice is adopted (D25). It is not
`inherited-from`, which says that another party performs the control
under an authorization: a product the user runs is the user's to
configure, and the vendor only described how.

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
*(2.0.0)* A `risk-adjustment` Deviation SHOULD name, in `refs`, the Risk
whose acceptance it rests on (RISK-9, D23). Accepting a risk and weakening
a requirement are two acts by two roles; they stay two records that
reference each other.
*(2.0.0-rc.3 — author decision 2026-11-12; backlog #52 and #47a)* Two
fields that 1.0.0 left as free text are typed. `opened` is a date,
`YYYY-MM-DD` (**DATE-1**), as `Risk.acceptance.date` and
`provenance.date` are. The `due` of a Finding's action is a typed point
in time or duration: `date`, `datetime`, `elapsed-duration` or
`calendar-period` with its calendar (**DATE-2**). The schema enforces
both; a validator names the rule when an object matches no type for
this reason. This is the one place where 2.0.0 refuses something 1.0.0
accepted. Surveyed first: the shipped bundles hold two `opened` values
and three `due` values, and all five conform. A date that any string
satisfies cannot be compared, sorted or checked, which is the defect
this specification counts in others' catalogues.
*(2.0.0-rc.4 — author decision 2026-11-13; backlog #65; D26)* Two
optional fields. `decided` is the day the Deviation was approved or
withdrawn, a date; `opened` stays the day it was asked for (AUTHOR-3
reports an approved or withdrawn Deviation without it). `review-due` says
when the exception is to be looked at again, typed as on a Risk: a date,
a date-time, an elapsed duration, or a calendar period with its
calendar. A validator reports an approved Deviation whose `review-due`
has passed (**REVIEW-1**, D26). The report fails nothing and changes
nothing: the Deviation keeps licensing its weakening until someone acts.
An exception approved once used to stay approved with no date ahead of
it; the one record that licenses a weakening now has one.

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

## D11 — SP 800-53 as Canonical Reference Facet; the JASCON stdlib.
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

**A Tailoring names no Component *(2.0.0-rc.3 — author decision
2026-11-12; closes backlog #51)*.** The Statement of Applicability is
joined to what it is for from the other side: a Risk names its Tailoring
in `tailoring-refs` (D23), and a check run names both its Tailoring
(`tailoring-ref`) and its subjects (D24). Those are the joins that exist,
and they are the model. An optional `component-refs` on a Tailoring was
considered and not added: no corpus demands it.

**Selection edges are typed *(rc.1 review)*.** `selects[].set-ref` names a
RequirementSet; `excludes[].ref` names a Requirement or a RequirementSet,
and a Set there excludes its members. Any other target is a validation
error. Before this rule a `set-ref` aimed at a Tailoring — the natural
misreading of "chaining" — validated, selected nothing, and derived as
authority-claimed; an exclude aimed at a Set removed nothing. Chaining
stays what it was: the algorithm run again on the resolved package.

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

**Who decided an entry *(2.0.0-rc.4 — author decision 2026-11-13;
backlog #66; D26)*.** A Tailoring MAY carry `provenance: {author-ref,
date}`, and so MAY each select, each exclude and each operation. Who
decided an entry is a function of the object alone: the entry's
`provenance`, else the Tailoring's, else nobody. A Tailoring written by
one person names that person once. **AUTHOR-1** reports a Tailoring at
consumer tier that leaves an entry without an author; an authority's
Tailoring is attributed by its origin and its Attestation and is not
asked. `excludes[].rationale` stays optional; `risk-coverage` reports an
exclude without one at consumer tier, as before.

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

## D14 — Rules: ten primitives, one bounded conditional, **no general-purpose expression language.** *(rev. v0.5 — wording P8; tier P8-E1)* *(rev. 2.0.0 — the ninth primitive, D23)* *(rev. 2.0.0-rc.2 — the tenth, D24)*
Unchanged in substance. `attestation-binds` evaluation moves to **Portable**
(Core treats Attestation objects as schema-valid data) — resolving P8-E1's
Core/JCS contradiction. The ledger phrase is corrected to the defensible
form: primitives + ops + predicates are a small closed DSL; what the design
excludes is a *general-purpose* expression language — the distinction that
matters for complexity re-inflation.
**The ninth primitive *(2.0.0)*.** `risk-coverage` (Appendix B.1.9) is the
first use of the escape path the closed set was given at 1.0.0: a
versioned addition that arrived with counts, corpus cases and a normative
failure format. It computes one fixed join; it defines no expression, no
predicate and no operation.
**The tenth primitive *(2.0.0-rc.2)*.** `check-verdict` (Appendix B.1.10)
evaluates a flat conjunction of twelve comparators over the facts one
observation reports. It has no OR, no NOT, no nesting, no arithmetic, no
paths and no comparison between two facts; what needs one of these is a
manual check and is counted as one (D24). Two of the twelve, `matches` and
`matches-not`, take a regular expression. A regular expression is a
membership test over one string and not a language for rules, and the
kernel already relies on one in every JSON Schema `pattern`. The danger
D14 names is real for it all the same — two conformant tools, two
verdicts — so the dialect is I-Regexp (RFC 9485), the match is against the
whole value, pattern and input are bounded, and no implementation may
hand the pattern to its host's engine (D24).

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
| Kernel schemas incl. statements[], all eleven types | Required | Required | Required |
| Local (manifest) resolution · sealed mode · package-digest verification | Required | Required | Required |
| Structural primitives (`references-resolve`, `digest-verified`, `unique-within`, `code-from`, `prose-params-resolve`) | Required | Required | Required |
| Preservation of unknown registered facets & annotations | Required | Required | Required |
| **Any semantic computation** (tailoring, assessment, selection, normative rendering) | **Forbidden** | Required (fail-closed rules apply) | Required |
| Registered-facet schema validation · capability declarations · fail-closed | — | Required | Required |
| Semantic digests (JCS) · `attestation-binds` · `modality-monotonic` · `conditional-apply` · `risk-coverage` *(2.0.0: the report is required; failing on `uncovered` is program policy)* · `check-verdict` *(2.0.0-rc.2: every recorded verdict is recomputed from its recorded observation; running a collector is outside every tier)* | — | Required | Required |
| Exact facet version+digest pinning; bundle-composition resolution | — | Required | Required |
| *(2.0.0-rc.3)* Advice packs: what a pack may hold and the kept manifest (ADVICE-1 to ADVICE-3, ADVICE-8 to ADVICE-10, structural, no semantic computation) | Required | Required | Required |
| *(2.0.0-rc.3)* Capabilities and the edges that cite them (ADVICE-4 to ADVICE-7) · composing a pack into a bundle (ADVICE-11) · the publisher verdict, claimed or proven | — | Required | Required |
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
shipped an **entire eighth document model** for mappings (OSCAL 1.2.0,
December 2025) —
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

**The consumer-side clause *(rev 4, 2.0.0-rc.2 — author decision
2026-11-12; closes backlog #48)*.** Test 1 counts what catalogue
authorities publish. A risk register and a machine check are data of the
organisation that consumes a catalogue; no authority ships them, so test 1
as worded can never be met by such a type, whatever the evidence. For
these, and only for these:

> A type that catalogue authorities do not publish may be promoted to the
> kernel when (a) a recognised standard of the weight of ISO/IEC 27001, or
> one of the same standing, requires the record, or the record is
> established practice, shown by at least two independent open
> implementations whose content was counted; (b) tests 2 and 3 hold, with
> test 3 measured on at least one corpus; and (c) it rides a major. The
> standard or the counted implementations are named in the decision
> register.

Test 1 stays as it is for everything authorities do publish. The clause
is narrower than the anticipated-convergence path that closed unused at
1.0: it admits no anticipation, it asks for a named standard or for
counted content, and it leaves tests 2 and 3 in force.

**Applied at 2.0.0 — Risk and Check, under the consumer-side clause.**
**Risk** (D23) enters under the first branch of (a): ISO/IEC 27001 6.1.2
and 6.1.3, BSI-Standard 200-3 and NIST SP 800-30 require the record. (b):
one shared computation, `risk-coverage`; one vocabulary, in that the four
treatment options fit ISO and BSI one to one, while OSCAL's seven response
types do not (two have no code), measured on the IFA corpus. (c): 2.0.0.
**Check** (D24) enters under the second branch of (a): machine-decidable
checks are established practice in posture management and configuration
scanning, counted so far on ComplianceAsCode (the four CIS profiles for
Ubuntu 24.04: 510 rules, 481 fit) and on kube-bench (`cis-1.12`: 103
automated checks). (b): one shared computation, `check-verdict`; one
vocabulary, the twelve comparators, onto which every comparison operator
of both corpora maps. (c): 2.0.0. What the clause does not supply is a
third counted platform: the fit is measured on Linux hosts and on
Kubernetes, and on no cloud API (D24, "Cons, stated").

**Applied at 2.0.0-rc.3 — two fields, on the author's word.** The clause
above is written for types. Advice packs (D25) add no type; they add a
manifest header and one field on a capability, `statement-ids`, and the
author added a second field, `product-version` on a Component. For a
field the three tests are owed all the same. `statement-ids`: test 1
fails (no census authority publishes vendor recommendations); test 2
holds (resolving a statement id against a requirement, done today for
five other shapes); test 3 holds trivially. Read against the consumer-side
clause it is **not met**: no standard is named, and the counted content
is one fictional example file where the clause asks for two
implementations. **The author overruled D22 for this field on
2026-11-12** ("I see great use for it"). `product-version` has no
counted evidence at all and is the author's decision of the same day.
Both are recorded here as what they are: fields that entered the kernel
against the rule, by the one person who may decide that, with the
missing evidence named. A census of public component definitions would
be the evidence; it has not been made.

## D23 — **`Risk` as the tenth kernel type; `risk-coverage` as the ninth primitive.** *(new, 2.0.0 — CP-RISK-1; author decisions 2026-11-10)*
**Decision.** A shallow first-class object for the ex-ante risk record —
the answer to *why is this requirement in scope at all?*

```json
{ "id": "https://cso.example/risk/R-2026-007",
  "version": "2026-11", "lifecycle": "active",
  "scenario": { "en": "A KMS key compromised through an export path stays valid for years because keys are never rotated; every tenant record encrypted under it is exposed retroactively." },
  "owner-ref": "https://cso.example/party/ciso",
  "state": "treated",                     // identified → assessed → treated → retired
  "threat-refs": [ "https://ns.bsi.bund.de/gspp/threat/G-0.19" ],
  "component-refs": [ "https://cso.example/component/acme-saas" ],
  "tailoring-refs": [ "https://cso.example/tailoring/soa-2026" ],   // optional: the SoA this belongs to
  "rating": { "level": "hoch", "scale-ref": "https://cso.example/scale/bsi-200-3-matrix",
              "likelihood": { "level": "mittel", "scale-ref": "https://cso.example/scale/bsi-200-3-eintrittshaeufigkeit" },
              "impact": { "level": "existenzbedrohend", "scale-ref": "https://cso.example/scale/bsi-200-3-schadenshoehe" } },
  "residual-rating": { "level": "gering", "scale-ref": "https://cso.example/scale/bsi-200-3-matrix",
              "likelihood": { "level": "selten", "scale-ref": "https://cso.example/scale/bsi-200-3-eintrittshaeufigkeit" },
              "impact": { "level": "begrenzt", "scale-ref": "https://cso.example/scale/bsi-200-3-schadenshoehe" } },
  "treatment": "modify",                  // modify | retain | avoid | share
  "treatments": [ { "requirement-ref": "https://ns.bsi.bund.de/gspp/req/KONF.14.1",
                    "statement-ids": ["s2"] } ],
  "acceptance": { "approver-ref": "https://cso.example/party/ciso", "date": "2026-11-05",
                  "rationale": { "en": "Monthly rotation brings the residual to 'gering', within appetite." } },
  "review-due": { "type": "calendar-period", "num": 12, "unit": "months",
                  "calendar-ref": "https://cso.example/calendar/isms" } }
```

*(2.0.0-rc.4; D26)* A Risk MAY carry `provenance`, and so MAY its
`rating` and its `residual-rating`; a rating without one has the Risk's.
A change of a Risk is a new version, and who changed it is that
version's `provenance`: the kernel keeps no log inside the object.
`owner-ref` stays who answers for the risk, which is another question.
**REVIEW-1** reports a Risk still managed whose `review-due` has passed;
a duration there counts from `acceptance.date`.

Required: `scenario`, `owner-ref`, `state`. `review-due` is a point in
time (`{type: date | datetime, value}` — `YYYY-MM-DD`, or RFC 3339 with an
explicit offset) or a duration (elapsed, or calendar — fail-closed
without the named calendar, D9; `num` a positive integer).
`acceptance.date` is `YYYY-MM-DD`. These formats are schema-checked
*(rc.1 review)*: a "dated acceptance" that any string satisfies is not
dated. `tailoring-refs` is optional and scopes the Risk (below). Finding gains one
optional field, `risk-refs[]`: the ex-post record points at the ex-ante
one. Shape-disjointness holds: `scenario` + `owner-ref` occur in no other
type. Field table: Appendix A.9b.

**What is kernel, and what is not.** Kernel: that a risk exists, who owns
it, what it says, its state, a level *as an opaque label on a named
scale*, the treatment option, the requirements — to the statement — that
carry the decision, who accepted what remains, and when it is reviewed.
Not kernel: a scoring *method*. CVSS vectors, FAIR distributions and
impact per dimension differ by framework and by fashion and stay in
facets (`risk-analysis@1`, parked — Appendix D). The organisation's own
*matrix* — which likelihood and impact yield which level — is neither
kernel nor facet: it is part of the pinned definition of the level scale
(D3.7, below).
`rating.level` values compare as strings within one `scale-ref` and never
across scales (D2: identifiers are opaque); a validator checks presence
and consistency, never magnitude.

**Likelihood and impact *(author decision, 2026-11-10)*.** `rating` and
`residual-rating` MAY each carry `likelihood` and `impact`, and each of
those is what the rating itself is: an opaque level on a named scale,
`{level, scale-ref}`. As first landed they were facet material, on the
argument that scoring differs by method. The argument holds for the
computation and not for its two inputs: ISO/IEC 27001 6.1.2 d asks for
the consequences and the likelihood to be assessed before the level is
determined, BSI 200-3 names Eintrittshäufigkeit and Schadenshöhe,
SP 800-30 likelihood and impact, and OSCAL's risk data carries exactly
these two. Nested in the rating they come with a residual pair for free
and add no top-level field. The kernel prescribes no way of
combining them; where the organisation has pinned its matrix, the level
is held to it (SCALE-4, below). One impact per rating; impact per dimension (confidentiality,
integrity, availability, safety) is the facet's. One consequence, stated:
both sit *inside* a rating, and a rating needs a level — so OSCAL's
likelihood and impact, which come without a level, still cannot land in
the kernel and stay in the holding facet with the Risk at `identified`.

**Scales are the organisation's *(author decision, 2026-11-10)*.**
"Likelihood should be editable, wording and how many levels; same for
impact." A level is still an opaque string to the kernel, and a
`scale-ref` still a URI. What is new is that the bundle can carry the
scale's definition as a pinned file (D3.7): the levels in order, in the
organisation's own words and number. Where it does, the validator checks
every level against it (SCALE-2) — a typo is no longer a new level — and
notes a residual that sits above what it remains of (SCALE-3). 

**The matrix lives in the level scale *(author decision, 2026-11-10)*.**
As landed, this text assigned the matrix "to a facet". No such facet is
registered, and a facet is the wrong home in any case: it attaches to an
object, and a matrix belongs to a method and three scales, not to any
one Risk. The matrix is therefore an optional member of the definition
of the scale it produces levels on: `matrix {likelihood-scale,
impact-scale, cells}`, `cells` giving, for every likelihood level, the
level for every impact level. It is digested with the scale's pin and
covered by an Attestation exactly as far as the pin is (a Full Match
covers it, a Semantic Match does not — the limit all pins share). A
rating's `scale-ref` already names that scale, so no new reference is
needed. **SCALE-4:** on a scale that carries a matrix, a rating or
residual rating that states both likelihood and impact on the matrix's
two scales states the level of their cell. A mismatch **fails**. The one
way to depart from the table is to say why: `override-rationale` on the
rating turns the failure into a note. A level without inputs is not
checked. This is a lookup in the organisation's own pinned table, not a
kernel scoring method — the kernel still defines no matrix.

**Rules (normative).** RISK-1…6 and the first half of RISK-13 are schema
conditionals — any JSON-Schema validator enforces them; a conformant tool
names the violated rule and prints its rationale. RISK-7…12, the second
half of RISK-13 and RISK-14 are graph rules.

| Id | Rule | Why |
|---|---|---|
| RISK-1 | A Risk is `scenario` + `owner-ref` + `state` at minimum. | A risk without an owner is a worry, not a managed risk (ISO/IEC 27001 6.1.2 c 2). |
| RISK-2 | `state` ∈ assessed · treated ⇒ `rating`. | Analysed means a level was determined (6.1.2 d–e; BSI 200-3 Risikoeinstufung; SP 800-30). |
| RISK-3 | `state` = treated ⇒ `treatment` and `acceptance`. | Treated means an option was chosen and the owner signed the residual (6.1.3 a, f). |
| RISK-4 | `treatment` = modify ⇒ `treatments` non-empty. | A modification with no controls is nothing (6.1.3 b). |
| RISK-5 | `treatment` = share ⇒ `shared-with-ref`. | Sharing names who carries it. |
| RISK-6 | `treatment` = retain ⇒ `acceptance`. | Retention *is* acceptance; silent retention is the oldest ISMS defect (6.1.3 f). |
| RISK-7 | `treatments[].requirement-ref`, `component-refs[]` and `tailoring-refs[]` resolve in-bundle. | Closure-required, like `Implementation.requirement-ref` (the #16 taxonomy). |
| RISK-8 | `treatments[].statement-ids` name statements of the target. | Clause precision is addressable or it is prose. |
| RISK-9 *(SHOULD)* | A `risk-adjustment` Deviation names the Risk in `refs`. | The weakening and its justification meet in data (D8). |
| RISK-10 *(SHOULD)* | At consumer tier every `excludes[]` entry carries a `rationale`. | An exclusion without justification is a list, not a Statement of Applicability (6.1.3 d). |
| RISK-11 | A **live** Risk's treatment may not name a requirement that none of *its* Tailorings selects — those in `tailoring-refs`, else every Tailoring in force in the bundle. A withdrawn Tailoring selects nothing; a withdrawn Requirement is selected by none. *Undecided* — reported, never failed — where one of those Tailorings has an open selection (a predicate select). | The treatment plan and the SoA disagree: the risk leans on a control the SoA dropped. |
| RISK-12 | A Risk edge is typed: `treatments[].requirement-ref` names a Requirement, `component-refs` name Components, `tailoring-refs` name Tailorings, and a `Finding.risk-refs` entry that resolves in-bundle names a Risk (the edge itself stays landmark). | Coverage joins on Requirement ids; a mis-aimed reference is a wrong statement, not a loose one. |
| RISK-13 *(rc.1 review)* | `residual-rating` presupposes `rating`, and both name the same `scale-ref`; where both carry a `likelihood`, or both an `impact`, those name the same scale too. | A residual level is what remains of a level; levels never compare across scales, so a residual on another scale says nothing about the reduction. |
| RISK-14 *(SHOULD; rc.1 review)* | Where a bundle holds more than one Tailoring in force, a Risk with `treatments` names its Tailoring(s) in `tailoring-refs`. | Unscoped, a risk about system A justifies the control in system B's Statement of Applicability. |

**States and options (code systems, Appendix C).** C.3c: `identified →
assessed → treated → retired` — forward only, skipping allowed, `retired`
terminal (a recurrence is a new Risk). C.10: `modify · retain · avoid ·
share` — adopted, not invented (ISO 31000 §6.5.2 / ISO/IEC 27005; BSI
200-3's Reduktion · Akzeptanz · Vermeidung · Transfer one-to-one).

**Liveness.** A Risk justifies a requirement only while it is managed: a
Risk whose `state` is `retired` or whose `lifecycle` is `withdrawn`
justifies nothing and is exempt from RISK-11. Without this, coverage only
ever grows — a control justified once would stay justified for ever — and
the ordinary end of a treatment (retire the risk, then drop its control)
would be a permanent failure.

**Justification *(rc.1 review)*.** Being live is necessary, not
sufficient. A Risk justifies the requirements its `treatments` name once a
treatment *decision* rests on an *assessed* risk: `lifecycle` is not
`draft`, `state` is `assessed` or `treated`, and a `treatment` option is
present (ISO/IEC 27001 6.1.3 a–b: controls are determined to implement the
option chosen for an analysed risk). A live Risk short of that is
*pending*: reported with the requirement it names, counted as uncovered.
As first landed, any live Risk with `treatments` justified — so a
three-field stub satisfied the policy switch, and RISK-2/3/6 were strict
about fields the coverage join never read. The consequence for imported
data is stated, not softened: an OSCAL risk stays `identified` (below) and
therefore justifies nothing until a level and an option are recorded
natively. RISK-11 still binds a pending Risk — a plan that leans on a
control the Statement of Applicability dropped is already a contradiction.

**Scope *(rc.1 review)*.** `tailoring-refs` name the Statement(s) of
Applicability a Risk's treatment belongs to. Present: the Risk justifies,
and is held to RISK-11, only in those Tailorings. Absent: it applies to
every Tailoring in force in the bundle — correct for the one-SoA bundle,
and noted (RISK-14) wherever there is more than one. `component-refs` do
not do this job: a Tailoring carries no component, and the kernel has no
edge from a Statement of Applicability to the system it is for (open —
IV.9).

**`risk-coverage` — the ninth primitive (Appendix B.1.9; tier: Portable).**
A bundle with no Tailoring at all has scoped nothing out: every
Requirement in force is in play, and that implicit selection is reported
like a Tailoring's *(author, 2026-11-10: "if there is no tailoring, all
controls are in play")*. A bundle whose Tailorings are all withdrawn
selects nothing.
For each Tailoring in force (`lifecycle` ≠ `withdrawn`): the selected
requirements (set-refs expanded through nested Sets to any depth,
excludes removed — a Set there removes its members —, withdrawn
Requirements dropped) joined to the Risks that justify them and belong to
that Tailoring. Output per Tailoring: `covered`, `uncovered`, and two
subsets of `uncovered` that say why — `pending` (named only by live Risks
without an assessed treatment decision) and `lapsed` (named only by
retired or withdrawn Risks) —, `open-selection`,
`excludes-without-rationale`; per bundle: `treatment-out-of-scope`. A predicate select is resolved by the
tailoring engine, not by this primitive; a Tailoring that carries one has
an *open* selection — a lower bound from which nothing is concluded by
absence. **Verdict discipline:** `uncovered` is a report line, never a
failure by default. Whether a selected control needs a risk basis is the
program's policy — ISO/IEC 27001 6.1.3 d says yes for every row of the
Statement of Applicability; BSI 200-2 lets the baseline justify its
Basis- and Standard-Anforderungen. A conformant Portable tool MUST compute
the report and MUST offer the policy as a switch; the reference
validators call it `--require-risk-basis`. The switch applies to every
Tailoring, not only to consumer tier: an organisation's Statement of
Applicability over its own catalog derives as authority-claimed (D13),
and exempting that would exempt exactly the case the primitive exists
for. It applies equally to a bundle that carries no Risk at all — the
empty register is the limiting case, not an exemption — and to the
implicit selection of a bundle without a Tailoring.

```
FAIL [risk-coverage] <tailoring>  selected <requirement>
  justified by no Risk
  rationale: ISO/IEC 27001 6.1.3 d — inclusion in the Statement of
  Applicability carries its justification
```

**The rules stay strict toward imported data *(author decision,
2026-11-10)*.** The first Risk corpus showed that OSCAL's risk data has no
owner field, no single level (likelihood and impact only) and no dated
acceptance; under RISK-2 both converted risks stay `identified` although
both were analysed, and under RISK-6 the one accepted risk cannot be
written as `retain`. The rules are kept as written — no import-only
variant, no facet in place of a field. `assessed` means "has a level" and
`retain` means "has a dated, attributed acceptance" for every bundle,
readable without opening a facet; loosening later never invalidates data
already written, while tightening later would; and one fictional example
with two risks is a measurement, not a population. A converter derives
the owner where the source names one elsewhere (declared in its coverage
report), leaves the state at `identified`, carries the source's own
status and scoring verbatim in a facet, and reports the gap. It invents
nothing.

**Evidence — and its tier.** Three standards prescribe this record with
the same fields: ISO/IEC 27001:2022 6.1.2–6.1.3 with ISO/IEC 27005,
BSI-Standard 200-3, and NIST SP 800-30 / 800-39. One corpus encodes it:
the OSCAL POA&M of the IFA lifecycle set, converted to two Risk objects —
supplying three of the record's six shared fields (scenario, treatment
option, treating controls) and lacking three (owner, level, dated
acceptance). The census corpora encode none of it. Tier: **designed-for,
with one partial measurement**; the promotion rests on D22's
consumer-side clause, first branch *(2.0.0-rc.2; this sentence used to
call it an exception to test 1)*. Corpus-exercised so far: `scenario`,
`owner-ref`, `state`, `component-refs`, `treatment` + `treatments`,
`review-due`, `Finding.risk-refs`, RISK-9. Vector-exercised only:
`rating`, `residual-rating`, `acceptance`, `shared-with-ref`,
`threat-refs`, `tailoring-refs`, the states beyond `identified`, and `risk-coverage` at
corpus scale (the one corpus with Risks carries no Tailoring).

**Version.** A tenth kernel type is a kernel-shape change, and by D22
rev 3 it rides a major: **2.0.0**. Measured at rc.1, every object of the
1.0.0 corpus validated unchanged (6,914 / 6,914; since rc.3 two fields
are typed, D8, and the shipped values conform) — and
the reverse does not hold: a 1.0.0 tool cannot type a Risk. The
manifest names the kernel since the rc.1 review (D3.6): a bundle that
carries a Risk pins `kernel-version` 2.0.0, and a tool that does not
implement the pinned kernel stops and says so. Before, a 1.0.0 tool
reported "matches NO type" and no version (backlog #44, closed).

**Rationale (north star applied).** *Customer:* every organisation that
runs an ISMS, and the auditor who asks which selected controls rest on no
risk — a question 1.x cannot answer in data (usnistgov/OSCAL #2292).
*Simplicity:* one shallow object and one fixed join turn the Statement of
Applicability from a hand-reconciled document into a computation. *No
props / no bespoke:* without a kernel home the risk register stays a
spreadsheet, or a framework facet no second tool can read — which is
where the 1.0.0 conversion of the IFA corpus had left it.
**Cons, stated.** Every validator carries a tenth type for ever; the
promotion needed a clause that D22 did not have when the type was drafted
(the consumer-side clause, written two days later); the evidence is three standards and one partial
corpus; and until the second implementation runs, the primitive has one.

**Rejected.** *Risk as a facet* (the 1.0.0 answer of Appendix F Q14 —
right for scoring, wrong for the record: a facet attaches to an object,
and a risk belongs to none of the objects it connects). *A Mapping from
Risk to Requirement* (a Mapping is a third party's claim about two
requirements; "this control treats this risk" is the owner's decision
and belongs on the object whose owner made it). *Acceptance as a
Deviation* (two acts, two roles — D8). *Scoring fields in the kernel*
(Q14 holds for the computation; its two inputs, likelihood and impact, are
kernel since the author's decision of 2026-11-10 — above). *Relaxed rules for imported data* (above). *Counting every live Risk as
a justification* (the first landing — rc.1 review). *Scoping by
`component-refs`* (a Tailoring names no component; `tailoring-refs` is the
edge that exists). *A tier-scoped
policy switch* (above). *A `treats-risk` selection predicate* that would
derive the Tailoring from the register — deferred: it widens the
one-leash budget (D13) and needs its own evidence. *A selection-basis
field on Tailoring* (`baseline · risk · legal`) — the policy switch does
the same job without a shape change until a corpus shows the field being
authored.

## D24 — **`Check` as the eleventh kernel type; `check-verdict` as the tenth primitive.** *(new, 2.0.0-rc.2 — CP-CHECK-1; author decisions 2026-11-10 to 2026-11-12)*
**Decision.** A shallow first-class object for the machine check: the
facts a collector must report, and the comparisons that decide. Code
observes and decides nothing. The verdict is a pure function of the
Check, one recorded observation and the parameter values the run was
bound to, so any tool recomputes it without running anything.

```json
{ "id": "https://cso.example/check/LNX-SSH-1-maxauthtries",
  "version": "1.0.0", "lifecycle": "active",
  "requirement-ref": "https://cso.example/req/LNX-SSH-1",
  "statement-ids": ["s1"],
  "platform": "https://cso.example/platform/linux-host",
  "observes": [ { "name": "sshd.maxauthtries", "type": "integer" } ],
  "criteria": [ { "fact": "sshd.maxauthtries", "op": "at-most",
                  "expected": { "param": "max-auth-tries" } } ],
  "validity": { "num": 24, "unit": "hours" },
  "confidence": "reviewed",
  "provenance": { "author-ref": "https://cso.example/party/secops",
                  "date": "2026-11-11" } }
```

Shape (Appendix A.9c): `requirement-ref` and optional `statement-ids`;
`platform`, an opaque URI; `observes`, the fact contract (name, type
`string · integer · decimal · boolean · code`, cardinality `one` or
`many`); `criteria`, a flat conjunction of assertions `{fact, op,
expected}` whose `expected` is a literal or `{"param": name}`; optional
`applies-when` (same shape) and `each` (`{resource, allow-empty}`: the
facts repeat per resource); `validity`; `confidence`; `provenance`. Two
existing types gain optional fields: an Assessment `check-results` (one
row per check run, with the observation inline) and `tailoring-ref`; a
Finding `check-ref`.

**What is kernel, and what is not.** The line is drawn where tools must
agree. Kernel: the requirement and clauses a check discharges, the
platform, the fact contract, the criteria, applicability and per-resource
repetition, confidence and provenance, and a run's row. Outside: the
**collector code**, in the stdlib facet `collector@1` on the Check, so that
the Check's semantic digest covers the exact source; the runner, its
schedule and its credentials, which never appear in a bundle; target
inventory; the evidence store's backend; the raw evidence bytes, which lie
beside the bundle under their own hash. `collector@1` declares
`modifies-semantics: []`: nothing in it changes what passing means, and a
tool that cannot run a runtime still validates, recomputes and renders.

**The comparators (code system C.13; twelve).** `equals` · `not-equals` ·
`one-of` · `at-least` · `at-most` · `present` · `absent` · `includes-all` ·
`excludes-all` · `subset-of` · `matches` · `matches-not`. The first five
take one value, the next two any fact, the three after them a list, and
the last two a string or code, single or listed. There is no OR, no NOT,
no nesting, no arithmetic, no path and no comparison between two facts;
alternatives of a value are `one-of`, and negation lives in the operator
pairs. `not-equals` is the twelfth *(author decision 2026-11-12)*: the
census found it 85 times across kube-bench and twice in OVAL states, and
for a number nothing else says it.

**`check-verdict` — the tenth primitive (Appendix B.1.10; tier:
Portable).** Input: a Check, one observation (`{facts}` or `{resources:
[{id, facts}]}`), the bound parameter values. Output: `satisfied ·
not-satisfied · inconclusive · not-applicable`, with reasons.

1. No observation: `inconclusive`.
2. `applies-when` false: `not-applicable`; unknown: `inconclusive`.
3. An undeclared or unobserved fact, a mistyped value, an unbound
   parameter or a mistyped bound value: `inconclusive`. A default is never
   substituted (D9). An `integer` fact outside the number domain (D3.9)
   is mistyped: no engine returns `satisfied` or `not-satisfied` from a
   value another engine reads differently *(rev. 2026-11-13)*.
4. The assertions combine by strong Kleene AND: one `not-satisfied`
   decides; else one `inconclusive` decides; else `satisfied`.
5. With `each`, **every resource is evaluated** and none is skipped after
   the first failure *(author decision 2026-11-12)*. The outcome stays
   for-all, by step 4 over the applicable resources; with none applicable
   it is `satisfied` if `allow-empty`, else `inconclusive`. Beside the
   outcome a tool reports the counts `applicable`, `not-satisfied`,
   `inconclusive` and `not-applicable`, and the share of not-satisfied
   among applicable resources as a whole percentage in integer arithmetic:
   rounded half up, never 0 while one resource fails, never 100 while one
   passes. The counts are recomputed from the recorded observation, which
   holds every resource with its facts; a row stores none of them.
6. An Assessment's `result` is the aggregate of its rows (CHECK-10):
   not-applicable rows are dropped; with none left it is `inconclusive`.

An absent key means *observed absent*: the collector looked and did not
find it. A collector that could not look prints nothing. A collector
reports **effective** values, with defaults resolved, because most ORs
across facts in the counted corpora read "setting absent or setting equals
value", which an effective value turns into one comparison.

**Regular expressions.** `matches` and `matches-not` take a pattern in
**I-Regexp, RFC 9485**. The kernel fixes three things the dialect leaves
to the host. The pattern matches the **whole value**; `^` and `$` are
ordinary characters, and `.` excludes `\n` and `\r`. **Size limits**: a
pattern of at most 256 characters, a compiled program of at most 1,000
states, a value of at most 4,096 characters, beyond which the assertion
is `inconclusive`. **No host engine**: an implementation parses the
grammar itself and matches without backtracking, so that a verdict does
not depend on Python, .NET or ECMAScript and a pattern cannot stall a
validator. The grammar is that of the RFC **as published** (compared on
2026-11-12): it keeps the surrogate code points U+D800 to U+DFFF out of
`NormalChar` and `CCchar`, which the working group's file did not, and a
pattern that holds one is refused. **Categories follow the host
*(2.0.0-rc.3 — author decision 2026-11-12; closes backlog #59)*:** a
general category `\p{..}` is read from the Unicode database of the
implementation's host. RFC 9485 pins no Unicode version, and the kernel
does not either. A character assigned between two versions of the
database can therefore match in one tool and not in another; a check
whose verdict depends on such a character is fragile, and its author is
told so here. The vectors use long-assigned characters only. A pattern is
never a parameter (CHECK-4).

**Rules (normative; Appendix B.1.10 carries the failure messages).**

| Id | Rule |
|---|---|
| CHECK-1 | An in-bundle `requirement-ref` is a Requirement, and `statement-ids` name its statements. The reference **resolves if present**: a Check may ship without the catalogue it refers to *(author decision 2026-11-12)*. |
| CHECK-2 | Fact names are unique; every assertion reads a declared fact. |
| CHECK-3 | The operator fits the fact's type and cardinality; a literal has the fact's type. |
| CHECK-4 | `{param}` names a parameter declared exactly once on the covered clauses, with a fitting type; the requirement is in the bundle; a pattern is never a parameter. |
| CHECK-5 | `at-most` never binds a parameter that tightens `higher`, `at-least` never one that tightens `lower`: tightening a parameter must not loosen a check. |
| CHECK-6 | A pattern is I-Regexp within the size limits. |
| CHECK-7 | `collector@1` matches its schema; collector ids are unique. |
| CHECK-8 | A row's `check-ref` is a Check, and `check-digest` is its semantic digest: a changed check is a different check. |
| CHECK-9 | A row's outcome equals `check-verdict` over its observation and parameters. |
| CHECK-10 | One row per check; `Assessment.result` is the aggregate of the rows. |
| CHECK-11 | A row without an observation is `inconclusive` and carries a `reason`. |
| CHECK-12 | `tailoring-ref` resolves to a Tailoring. A row names only parameters its Check reads through `{"param": …}`, with or without a `tailoring-ref`; with one, their values equal what the Tailoring binds: an implementer does not set its own pass mark. *(rev. 2026-11-13: a name the Check does not read fails; before, it was ignored.)* |
| CHECK-13 | A row's `collector-id` names a collector the Check declares. A Check without `collector@1` declares none. *(rev. 2026-11-13)* |
| CHECK-14 | A Finding's in-bundle `check-ref` is a Check about the same requirement and a covered clause. |
| CHECK-15 | Evidence references stay in the store beside the manifest: a relative reference is `evidence/sha256/<hex>`, with `<hex>` the digest it records, and every digest verifies. A reference with a URI scheme is a landmark, noted and not resolved. Row and record describe one run: they name the same check, digest and collector, the record's subject is a subject of the Assessment, and a row carries an observation exactly when its record carries an `observation-digest`, which is that observation's semantic digest. A missing blob is reported as withheld and is no failure. *(rev. 2026-11-13: the store layout, the collector and the observation binding are enforced in both directions.)* |

**The run record is kernel *(author decision 2026-11-12)*.** The rows are
a field of Assessment and not a facet under `method`. A declarative
verdict is new computation, and Appendix B.4 lets facets bind arguments
and never define computation; under a facet every tool that did not know
it would have to stop on every such assessment. The observation sits
inline by default, so the Assessment's semantic digest covers it and an
Attestation over the Assessment binds what was observed.

**Evidence.** A directory beside the content manifest,
`evidence/sha256/<hex>`, every file named by the SHA-256 of its bytes and
none listed in the manifest. An evidence record (`$defs/evidenceRecord`)
names check, digest, collector, subject, times and exit status, and
carries the digest of the same observation and of each raw output.
A run that observed nothing has a record without `observation-digest`
and a row without an observation; the field is optional in the schema
for that case alone (CHECK-15).
Redaction happens before hashing.

**The kernel pin.** KERNEL-1 extends: a bundle that carries a Check, an
Assessment with `check-results` or `tailoring-ref`, or a Finding with
`check-ref` pins `kernel-version: "2.0.0"`.

**Evidence — and its tier.** No census authority encodes a
machine-decidable check: the CIS Ubuntu 24.04 Benchmark marks 291 of 312
rules automated and carries every one as an `audit` string; the others
name methods. The type enters under D22's consumer-side clause, second
branch. Counted for it: ComplianceAsCode at `f0d40648`, the four CIS
profiles for Ubuntu 24.04, 510 rules, of which **481 fit** the declarative
form (23 only if the collector resolves effective values and reports mode
bits as flag sets), 12 need arithmetic, 9 a comparison between two facts,
6 an OR across facts, 2 a version ordering, and **none a regular
expression outside I-Regexp**; kube-bench at `e278a591`, `cis-1.12`, 103
automated checks, whose operators map onto the set. The fit classes are a
judgement, recorded rule by rule (`drafts/cp-check-1-census/`). Tier:
**measured on two corpora outside the census, fit by judgement**.
Exercised by the worked example and by vectors: every field and every
rule. Exercised by nothing yet: a collector run on a real system. The
example's two runs executed the bash collector against a stub `sshd`.

**Version.** An eleventh kernel type rides the same major as the tenth:
2.0.0 is untagged, and the author set Check up to go live with it
*(2026-11-12)*. Every object of the five shipped bundles and the example
folder validates unchanged. A tool that
implemented rc.1 claims 2.0.0 and reports a Check as "matches NO type";
that is tolerable only because nothing was released under 2.0.0.

**Rationale (north star applied).** *Customer:* the operator who runs
checks every night, and the auditor who has to believe them. An exit code
hides its threshold, cannot be reached by a tailored parameter, and leaves
a bit where an observation should be. *Simplicity:* twelve comparators
and one conjunction, small enough for the weekend validator. *No props /
no bespoke:* without a kernel home the pass condition stays a sentence in
an `audit` string, which is where 291 automated rules of one benchmark
are today.
**Cons, stated.** Every validator carries an eleventh type and an I-Regexp
engine for ever. The shape closes on two counted platforms, Linux hosts
and Kubernetes; no cloud API was counted, and a correction after the tag
costs a major. 29 of 510 counted rules stay manual. Nothing in the
repository runs a collector, and `collector@1` carries the source of an
`http-api` collector as free text, which a runner cannot execute as it
stands. Both validators were written by one author.

**Rejected.** *Criteria in a facet on a Requirement the check author
owns, promoted later* (an independent design review during planning):
it keeps the kernel smaller, and it leaves `check-verdict` either a
kernel primitive whose input shape is kernel in all but name, or a
computation in a facet, which B.4 forbids. *The script's exit code as
the verdict*: the threshold then lives in code nobody reviews against the
requirement. *A quantifier beside for-all* ("at least one", "exactly
one": 12 counted cases): a count the collector reports and `at-least 1`
or `equals 1` say it. *Closure-required `requirement-ref`*: a check pack
for a catalogue that may not be passed on could not validate. *A general
regular-expression dialect*: two conformant tools, two verdicts. *OR,
NOT, arithmetic*: the leash of B.4; what needs them is manual and
counted.

## D25 — **Advice packs: a vendor's recommendations as one published file.** *(new, 2.0.0-rc.3 — CP-ADVICE-1; author statements and decisions 2026-11-12)*
**Decision.** A vendor says how its product can meet a requirement, and
has no way to change the user's requirements or assessments by saying
so. The carrier exists since 1.0.0: `Component.capabilities[]`. What is
added is the file a vendor publishes as such, the rules that hold that
file to being advice, and the record in the user's bundle of which
vendor's release came in. No kernel type and no primitive is added.

**The file.** An advice pack is a bundle whose manifest carries a pack
header (D3 item 8) and whose objects are Components. Published as one
ZIP it is one file; published as a folder it is the same pack. A bare
Component file is not a pack *(author decision)*: it names no release
and no publisher and cannot be signed.

```json
"pack": { "kind": "advice",
          "id": "https://vendor.example/pack/server-7-hardening",
          "version": "3",
          "title": { "en": "Server 7 hardening advice" },
          "publisher": { "ref": "https://vendor.example/party/vendor",
                         "name": { "en": "Vendor Inc." } } }
```

**A recommendation** is a capability with four parts: the requirement
(`requirement-ref`, resolves if present: a pack ships without the
catalogue, which the vendor may have no right to pass on), the clauses
(`statement-ids`), the text for consideration (`description`) and
suggested parameter values (`parameter-bindings`). The Component may say
which product version it describes (`product-version`, D5).

**Claimed and proven.** The publisher is *claimed* by the header and by
the origin its ids share with it. It is *proven* when an Attestation
beside the manifest has a signer of that origin, binds this manifest's
digest, and its envelope verifies under a key the user trusts: the two
words, and the envelope check, that the tier rule uses for a Tailoring
(D13). As there, a validator that was given no keys reports the binding
and marks it UNVERIFIED; that is no proof, because anyone can write an
Attestation that names the vendor as signer. A tool for people shows
three states and never a vendor's name without one of them: *claimed*,
*attested, not verified* (the binding without a checked signature) and
*proven*. Only the last may look like a confirmation.

**Adoption.** The user's Implementation, on the user's component, cites
the vendor's capability: `<component-id>#<capability-id>` (D6). A
capability stays a claim. The only statement that a requirement is met
remains the Implementation edge in the user's namespace.

**Import.** The vendor's Components join the set, and the vendor's
manifest is kept unchanged as `packs/sha256/<hex>`. There is no separate
import record: the kept manifest names the vendor, the release and every
object that came with it, and it is the thing the vendor signed.

| The set holds | Result |
|---|---|
| no pack with this `pack.id` | the Components are added, the manifest is kept |
| the kept manifest of this very file | nothing is written: already imported |
| a kept manifest with this `pack.id` and another digest | another release: after a preview with a diff, the pack's objects and its kept manifest are replaced |
| an object with an id from the file that no kept manifest of this pack lists | refused (ADVICE-11) |

Releases are not ordered; a tool says *another* release and shows both.
One release of a pack is in a set at a time *(author decision)*; history
is whatever versioning the set itself is kept in.

**The guarantee.** After the import of an advice pack, every object that
was in the set has the semantic digest it had before, and no Requirement,
Set, Tailoring, Mapping, Risk, Check, Implementation, Assessment, Finding
or Attestation was added. The first is compared object by object and
printed as a receipt; the second is ADVICE-1. It is no promise that
validation output is the same: references that were landmarks now
resolve.

**Rules (normative).**

| Id | Rule |
|---|---|
| ADVICE-1 | Every object a pack's manifest lists is a Component *(author decision: Components only; a pack of Checks would be a second kind with rules of its own)*. |
| ADVICE-2 | Every object id, `pack.id` and `pack.publisher.ref` share one origin: a pack cannot carry an object under someone else's identity, and so cannot replace one. |
| ADVICE-3 | No facet on a pack's object declares a semantics class *(author decision)*; `private:` payloads ride as always. Advice must not reach a computation through a facet. |
| ADVICE-4 | Capability ids are unique within a Component. |
| ADVICE-5 | An in-bundle `requirement-ref` of a capability is a Requirement, and `statement-ids` name its statements; `statement-ids` are not allowed without `requirement-ref`. |
| ADVICE-6 | With the requirement in the bundle, each key of a capability's `parameter-bindings` is a parameter declared on the covered clauses, and the value lies in its declared space. |
| ADVICE-7 | A `capability-ref` is a capability id of the edge's component, or `<component-id>#<capability-id>`; the named component is in the bundle, the capability exists on it, and a component other than the edge's own is one of its `members` *(author decision: a rule, not a matter of display)*. |
| ADVICE-8 | A file under `packs/sha256/` is named by the SHA-256 of its bytes, is a content manifest with a pack header, and is not listed in the bundle's manifest. |
| ADVICE-9 | Every object a kept pack manifest lists is in the bundle at that version with that semantic digest: the advice in the set is what the vendor published, or the set says which object is not. |
| ADVICE-10 | One kept manifest per `pack.id`; no object is listed by two kept manifests. |
| ADVICE-11 | Composing a pack into a bundle adds ids the bundle does not hold and replaces ids a kept manifest of the same `pack.id` lists; any other id the bundle already holds is refused. |

Notes, never failures: a capability whose `requirement-ref` is outside
the bundle (not typed); a publisher that is claimed and not proven; a
kept manifest whose vendor Attestation is absent. No rule here: a
suggested value outside what the user's Tailoring allows. The vendor
cannot know the tailoring; a tool shows the value at adoption and does
not write it.

**A third party's advice *(author decision)*.** A consultancy or a
benchmark publisher that writes about someone else's product publishes
its own Component under its own origin (ADVICE-2 leaves it no other
way). It says which product it is about with a relation of the stdlib
type `https://ns.jascon.net/stdlib/relation/describes`, whose `ref` is
the vendor's Component id. Relation types are the one extensible code
surface (C.8): tools carry and show the edge and compute nothing from it.

**Evidence — and its tier.** No census authority publishes vendor
recommendations; they publish catalogues. One component definition is in
the corpus, a fictional example file by NIST with three recommendations,
two clause-level entries and two suggested parameter values. The
handbook's own evidence speaks against a second place where
implementation is described (Chapter 9.1, the public retreat from
component definitions), and this decision does not bring one back: a
capability is a claim, an Implementation is the statement. Tier:
**designed-for, with one fictional file**. The promotion of
`statement-ids` rests on the author's decision against D22 (there);
`product-version` on the author's decision alone. Exercised by vectors
and by one worked pack signed with the public fixture key: every rule.
ADVICE-7, run over the shipped bundles, found one defect in a converted
bundle, which was corrected. Exercised by nothing yet: a pack a vendor
published.

**Version.** The changes ride 2.0.0. A manifest without `pack` is not a
pack; a capability without `statement-ids` and a Component without
`product-version` are valid as before; a `capability-ref` that is a bare
id of its own component stays valid. ADVICE-7 gives meaning to a string
that had none and can turn existing content red; it did once.

**Rationale (north star applied).** *Customer:* the operator who buys a
product and wants the vendor's hardening advice in the same graph as the
requirement it serves, without the vendor's file being able to move a
pass mark. *Simplicity:* a header, two fields, eleven rules; the import
is the composition engine of gate 4 with one lawful replacement. *No
props / no bespoke:* the document model that gave OSCAL this guarantee is
replaced by a rule on a bundle.
**Cons, stated.** Two kernel fields entered without counted evidence.
The only pack there is was written for this purpose; the pack builder
imports OSCAL component definitions (IV.7). NIST's example component
definitions import without loss of anything a pack can hold
(`drafts/cp-advice-1-census/`); none published by a vendor has been
imported yet, and that census is what could change the evidence for the
two fields above. What the app and the reader do
with a pack is stated in IV.7.

**Rejected.** *The vendor publishes Implementation objects*: an
Implementation says that a requirement is met, so importing a vendor's
edges would change what the user's set says is implemented. *Checks in
an advice pack*: a vendor would ship ways to assess. *A bare Component
file as a second form*. *A list of product versions, or a product
block* (D5). *Keeping the manifests of earlier releases in the set*.
*Leaving membership (ADVICE-7) to what a tool shows*.

---

# Part III — Worked examples

III.1 (BSI KONF.14.1), III.2 (CR26 IEC rule + class Tailoring), III.3
(ISM, zero facets) carry over from v0.4 unchanged in substance, with two
corrections: III.2's effectivity dates differentiated
(`optional-adoption: 2025-11-01`, `must-obtain-by: 2026-07-04`,
`grace-until: 2027-01-01` — illustrative), and the class Tailoring now
demonstrates the parameter-bounds rule (setting `iir-deadline` to a value
outside a declared range would fail without a Deviation). New:

## D26 — **Who decided, and when: one `provenance`; a decision date and a review date on a Deviation.** *(new, 2.0.0-rc.4 — CP-AUTHOR-1; author decisions 2026-11-13; backlog #65 and #66)*

Through rc.3 the kernel recorded a weakening, a selection, a risk level,
an implementation status and an authorization without a place for who
decided it or when, and it spelled "who and when" five ways where it did
have one (`provenance`, `approver-ref` with `opened`, `approver-ref` with
`date`, `performer-ref` with `time`, `signer` with `timestamp`).

**One spelling.** `provenance: {author-ref, date}`: a URI, compared and
never resolved (D2), and a date `YYYY-MM-DD`. The shape is closed and
both members are required when it is present. It is the shape a Mapping
and a Check already carried.

| Where | Field | Since |
|---|---|---|
| Mapping, Check | `provenance`, required | 1.0.0, rc.2 |
| Tailoring; each select, exclude and operation | `provenance`, optional | rc.4 |
| Risk; its `rating` and `residual-rating` | `provenance`, optional | rc.4 |
| Implementation, Finding | `provenance`, optional | rc.4 |
| Deviation | `decided` (a date) and `review-due`, optional; `approver-ref` and `opened` as before | rc.4 |
| Component authorization | `date`, optional; `authority-ref` as before | rc.4 |
| Assessment | `performer-ref`, `time`: a date or an RFC 3339 date-time with an offset | typed in rc.4 |
| Attestation | `signer`, `timestamp`: the same | typed in rc.4 |
| Requirement, RequirementSet | none: the publisher is the origin of the id | |

**Two levels.** On a record, `provenance` names who wrote this version
and when. On a decision inside a record (an entry of a Tailoring, a
rating of a Risk) it names who decided that entry; an entry without one
has its record's. A change is a new version. The kernel keeps no log
inside an object, because a second history inside each version can
contradict the first.

**A claim, bound by the digest.** `provenance` is part of the semantic
digest, so an Attestation over a Tailoring binds what the Tailoring says
about its authors. Proof of who signed stays the signature (D7).

**Reported, not required.** The schema leaves every one of these fields
optional: a catalogue authority's content needs none of them. A
validator reports what is missing, one line per object and rule, and
MUST offer a switch that turns the lines into failures (reference:
`--require-authors`), as it does for uncovered requirements.

| Rule | Reported when |
|---|---|
| **AUTHOR-1** | a Tailoring at consumer tier has a select, an exclude or an operation with no `provenance` of its own and none on the Tailoring |
| **AUTHOR-2** | a Risk, a Finding or an Implementation carries no `provenance` |
| **AUTHOR-3** | a Deviation in state `approved` or `withdrawn` carries no `decided` |
| **AUTHOR-4** | a Component authorization carries no `date` |
| **REVIEW-1** | the `review-due` of an approved Deviation, or of a Risk still managed, has passed |

**REVIEW-1.** The validator reads the date of the run in UTC; it MUST
accept a date given by the caller instead (reference: `--as-of
YYYY-MM-DD`), which is what makes the conformance vectors give the same
answer every day. A point in time has passed when its UTC calendar day is
before that date; due today is not overdue. A duration counts from
`decided`, else `opened`, on a Deviation and from `acceptance.date` on a
Risk; an elapsed duration is added to the start of that day in UTC. A
calendar period is not evaluated without its calendar (D9) and is
reported as such. REVIEW-1 never fails a bundle, with any switch. This is
the one rule of this specification whose answer depends on the day it is
asked; no verdict, no digest and no resolution depends on it.

**Three times that any string satisfied are typed.**
`Mapping.provenance.date` is a date (**DATE-3**); `Assessment.time`
(**DATE-4**) and `Attestation.timestamp` (**DATE-5**) are a date or an
RFC 3339 date-time with an offset. DATE-1 now names a Deviation's
`decided` beside `opened`. As with DATE-1 and DATE-2, the schema refuses
and the validator names the rule. No value in the repository had to
change: 53 assessment times, 19 timestamps and 3 mapping dates conform.

**The pin.** A bundle that uses a field added here needs
`kernel-version: 2.0.0` (KERNEL-1, D3.6).

**Not done, and why.** No requester on a Deviation: asking is not
deciding. No performer per check result row: a run by someone else is
another Assessment. No party type (#16). No rule that makes
`excludes[].rationale` required.

**Evidence tier.** Fields on existing types, entered on the author's
decision (the precedent is D25's two fields). Read, not counted: OSCAL
states who per item in its assessment layer and per document everywhere;
CISO Assistant carries an expiry on a security exception and logs each
change. No corpus of consumer Tailorings with authors exists. Measured:
40 vectors for the two reports and 29 for the pin and the shapes;
nineteen deliberate defects in the reference each turn one red.

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

## III.5 — A risk, the clause that treats it, and the finding against that clause *(2.0.0)*

The Risk of D23 treats `KONF.14.1`, statement `s2` (the customer rotates
keys). The Implementation says `s1` is the provider's and `s2` the
customer's (D6); the assessment's finding is against `s2` and points back:

```json
{ "id": "https://assessor.example/finding/2026-q3-acme-017",
  "version": "1", "lifecycle": "active",
  "assessment-ref": "https://assessor.example/assessment/2026-q3-acme",
  "requirement-ref": "https://ns.bsi.bund.de/gspp/req/KONF.14.1",
  "statement-ref": "s2", "state": "closed",
  "risk-refs": [ "https://cso.example/risk/R-2026-007" ] }
```

Statement of Applicability, responsibility matrix and risk register agree
to the clause without anyone reconciling three documents — and
`risk-coverage` on the example bundle reports what a spreadsheet hides:
three requirements selected, one justified by a Risk, two by none.

## III.6 — A check, two runs and the finding between them *(2.0.0-rc.2)*

`LNX-SSH-1` has two clauses: at most `{param:max-auth-tries}`
authentication attempts, and no cipher in CBC mode. The Tailoring for
production hosts binds the parameter to 4. Two Checks discharge the two
clauses; the second reads

```json
"observes": [ { "name": "sshd.ciphers", "type": "code", "cardinality": "many" } ],
"criteria": [ { "fact": "sshd.ciphers", "op": "matches-not", "expected": ".*-cbc" } ]
```

The run of 3 November records `"sshd.maxauthtries": 4` (satisfied against
the bound 4) and a cipher list that contains `aes128-cbc` (not satisfied),
so the Assessment's result is not-satisfied. The Finding against clause
`s2` names the check that raised it. The run of 10 November records the
list without that cipher, both rows are satisfied, and the Finding is
closed with a relation to that run. The validator recomputes all four
verdicts from the recorded observations and holds both runs to the value
the Tailoring binds; bind 3 instead, and the unchanged observation of 4
fails. The example assessed no real host: each run executed the Check's
bash collector against a stub `sshd`, and every evidence record says so.

## III.7 — A vendor's advice, imported and adopted *(2.0.0-rc.3)*

The pack `…/pack/server-7-hardening`, release 3, holds one Component,
`…/component/server-7` with `product-version: "7"` and three
capabilities. `cap-key-rotation` names `KONF.14.1`, clause `s2`, and
says how the server rotates its certificate. The vendor's Attestation
and its envelope lie beside the manifest; with the vendor's key trusted,
the publisher is proven.

After the import the example set holds the vendor's Component byte for
byte, the vendor's manifest under `packs/sha256/`, and the Attestation.
Nothing else changed: the receipt reads *unchanged n of n · added 1
components*. The SaaS lists the server as a member, and one
Implementation adopts the recommendation:

```json
"satisfied-by": [ { "capability-ref":
    "https://dbvendor.example/component/server-7#cap-key-rotation" } ]
```

Remove the server from the members of the SaaS and that edge fails
ADVICE-7. Edit the vendor's Component in the set and ADVICE-9 says that
the advice differs from release 3. Import the same file again and
nothing is written. The signing key of the worked pack is the corpus
fixture key, whose seed is public: the example shows the mechanism and
says nothing about a vendor.

---

# Part IV — Ledger, risks, gate, changelog

## IV.1 Complexity ledger

**Removed vs. the predecessor format (1.2.2):** eight deep document models (incl. the
Mapping Model of 1.2.0) · Metaschema · profile-resolution algebra + merge
strategies · XML/YAML conformance + serialization mapping · Schematron ·
anonymous inline constraints · comp-def/SSP duplication · general JSON
Patch. **Kernel:** 11 shallow types *(9 at 1.0.0, 10 at rc.1)* · 2
sub-objects · 1 serialization · JSON Schema 2020-12 · 10 primitives *(8 at
1.0.0, 9 at rc.1)* + a closed op vocabulary + 3 predicates + 12
comparators ·
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
predecessor format's validator+resolver toolchain (tests excluded) — **≈30×
each** (31×/27×), ~14× combined. Measured
size deltas versus the OSCAL sources: ISM −29 %, GS++ −50 %,
CR26 +55 % — smaller where sources are redundant, larger where a
bespoke format was terse.
*(2.0.0-rc.1)* The size figures above are the 1.0.0 measurement. Both
validators grew with Risk (closure, liveness, the coverage join, 42
vectors); they were **not** re-measured with the gate-4 counter for this
candidate, and the ≈30× claim is therefore a 1.0.0 claim until they are.
*(2.0.0-rc.2)* Re-measured on 2026-11-12 with the gate-4 counter
(non-blank lines that do not start with `#`): `validate_core.py` **2,228**
lines, `validate_core.ps1` **2,963**. Against the 30,905 lines of the
toolchain counted at gate 4 that is ≈14× and ≈10×. Risk, Check, the
I-Regexp engine, scales and the kernel pin more than doubled both files;
the ≈30× of 1.0.0 is history. Each validator is still one file.
*(2.0.0-rc.3)* Advice packs add eleven rules and no type or primitive;
the files grew again and were not re-counted for this candidate.

## IV.2 Risk register (delta)

R1–R12 carry over with status updates (R4 softened by pinning+composition
rule). New: **R13** — IR 8477/OLIR relationship code-system governance
(stdlib ownership); **R14** — calendar-context dependency: calendar-periods
are honest but push a real-world dependency (holiday calendars) into
Authority publication duties; **R15** — CIS corpus status unverified — **RESOLVED 2026-07-21**: both
CIS corpora converted and measured (Controls v8.1; Ubuntu 24.04
Benchmark with 635 mappings and recovered profile baselines).
*(2.0.0)* **R16** — coverage is path-level: the conversion reports count
source paths with a declared destination, not values verified to arrive.
A value-level check on the one corpus measured so far (IFA) finds 124
content values, 63 of them prose, that have no equal value anywhere in
the bundle; under `poam.risks[]` alone thirteen had never arrived at
1.0.0, the risk response type among them. Some absences are deliberate
transformations; the other ten corpora are unmeasured. *(rev.
2026-11-13, two outside reports: the check had matched substrings and
read 122 absent and 394 of 835 arrived; with typed, whole values it
reads 124 and 283. And it is a global check: 283 is an upper bound on
what was carried, since one value in the bundle answers for every equal
value in the source. The same day a **ledger** traced every source value
of this corpus through the converter. After the author's decisions it
reads 441 copied, 95 transformed by a named rule, 299 dropped for a
declared reason, **none unaccounted**. Three of the drops are references
that name nothing their source defines, declared as defects of the
source. The path map reads 835 of 835 for the same conversion.
The first run read 232 copied and 473 unaccounted and found a value the
converter had overwritten, one of two addresses of an inventory item;
that is fixed. The author then decided the unaccounted values class by
class. Revision history, the directory of parties and roles, back-matter
and import links and type tags are declared drops. Seven classes are
carried and changed 15 of the bundle's 17 objects: the detail of the
leveraged and the leveraging system, of the components, of the control
implementations and of the assessment, in facets; roles at two levels,
the Component and the whole scope. References by uuid are resolved to
the objects they name, which showed two edges the converter had wired
against its source; both follow the source now. The three values left
are references that name nothing their source defines.)* "Converted
losslessly" is established at path level only (backlog #41). **R17** —
redistribution: six of the eleven measured bundles cannot be shipped
(§2); the shipped evidence base no longer exercises Tailoring or Mapping
at scale, and the removed bundles remain in the repository's history
(backlog #50). **R18** — the fourth authority's data does not hold the
whole Risk record (D23): every OSCAL import stays `identified` until a
level and an acceptance are added natively. Accepted by decision; watched
at the next Risk corpus.

## IV.3 Prior art (delta)
Add: **NIST OSCAL 1.2.2 Control Mapping Model** — as demand evidence *and*
as the negative pattern (deep document model, props throughout) D20
replaces; NIST IR 8477 / OLIR (relationship semantics).
*(rc.1 review)* This delta never named the formats closest to JASCON.
`PRIOR-ART.md` (repository root) does: Gemara, CycloneDX Attestations,
the CISO Assistant library format, FedRAMP's rules JSON, SCF STRM,
in-toto / SCITT — what each already does, and which JASCON features are
therefore not new.

## IV.4 Coverage table (P7/P8 verdicts adopted)

| User | Verdict | Basis |
|---|---|---|
| BSI, ASD, FedRAMP CR26 | Designed-for, **measured corpora**, proof at gate | census |
| NIST 800-53 | **Measured** (gate 3): Rev 5.2.0 + four 800-53B baselines, 115,680 leaves, zero kernel changes; all 373 pre-existing corpus mapping endpoints resolve | `US.SP800-53` |
| NIST 800-171 | Designed-for (D11 + sets/tailoring) | catalog layer |
| NIST CSF 2.0 | **Measured** (gate 3): 3-level D21 nesting, sixth declarative corpus, the 1.1→2.0 tombstone graph on `replaces[]` | `US.CSF` |
| NIST full lifecycle (SSP/AP/AR/POA&M) | **Measured** (gate 3): the five lifecycle types at document scale with both digests; D5 inheritance via the leveraged pair; #9 seeds confirmed with zero enum additions. *(2.0.0)* POA&M risks → 2 Risk objects, Findings carry `risk-refs`; the source lacks owner, level and dated acceptance (D23) | `US.IFA-GoodRead` |
| CIS | **Measured**: Controls v8.1 + Ubuntu 24.04 Benchmark (635 D20 mappings; recovered profile baselines) | `CIS.Controls` · `CIS.Ubuntu2404` |
| SCF | Catalog + **D20 mappings** (its central use case now first-class) | |
| CSA CCM | Controls + CAIQ→assessment-criteria plausible; mappings via D20; full STAR package not claimed | |
| ISO 27001/27002 | Structurally adaptable (attributes → framework facet; sealed manifests help licensed distribution). *(2.0.0)* The risk assessment and treatment record of 6.1.2–6.1.3 and the Statement of Applicability as a computation: **designed-for** (D23) — no ISO corpus exists to measure. **The other management-system clauses remain not covered** — named target | |
| PCI DSS | Testing procedures → assessment-criteria; compensating controls → Deviation; **customized approach encoding undefined** — named target | |

*(2.0.0)* "Measured" in this table describes the measurement, not what
ships: the bundles for CIS, CR26, C5, C3A and CyFun are not redistributed
(§2); ISM, Grundschutz++ and the NIST corpora are.

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

## IV.5b The 2.0.0 gate — state at rc.3 (2026-11-12), with what rc.4 added (2026-11-13)

The 1.0.0 gate asked for converters, an executable kernel, a lifecycle
corpus and two implementations. The same four questions, asked of Risk,
of Check and of advice packs:

1. **Executable kernel + conformance.** ✓ Schema 2.0.0 (eleven types);
   **537 vectors, 17 families** — the twelve of 1.0.0 (lifecycle 36 → 38
   with the tenth and the eleventh disjointness case) plus `risk` 73,
   `kernel` 25 (the manifest pin, D3.6: 11; the shapes of the typed date
   fields and of `product-version`: 14), `scale` 18, `check` 188 (42
   regex · 63 verdict · 7 aggregate · 12 share · 20 object · 44 bundle)
   and `advice` 74 (9 shape · 15 pack · 21 graph · 11 kept manifest · 8
   publisher · 10 import). Every review correction is pinned by a vector
   that fails on the validator as first proposed; 28 deliberate defects
   in the advice rules and 5 in the check rules each turn a vector red.
   *(After rc.3, 2026-11-13: `reference` 13 → 18 and `tier` 9 → 10:
   ids that differ in case, by U+00AD or by normal form are different
   ids (D2; backlog #45 and #58). No kernel shape and no rule changed by
   these six. With the vectors of the run rules and of NUMBER-1 (IV.6),
   574 in all; both validators and the app's port are green on them.)*
   *(rc.4, 2026-11-13: an eighteenth family, `author`, with 40 vectors
   for the two reports of D26, and `kernel` 25 → 54 for the pin and the
   shapes of its fields: **643 vectors, 18 families**. Nineteen
   deliberate defects in the reference's new code each turn one red.)*
2. **First implementation.** ✓ `validate_core.py`: 537 / 537, the five
   shipped bundles (3,715 objects, both digests each), the worked advice
   pack and the example folder — ALL GREEN on 2026-11-12.
   *(rc.4, 2026-11-13: 643 / 643, the same bundles, pack and folder, ALL
   GREEN in the workflow run of item 3.)*
3. **Second implementation.** ✓ `validate_core.ps1` ran on Windows
   PowerShell 5.1 on 2026-11-12 on this candidate: 537 / 537 in
   seventeen families (`kernel: 25`, `advice: 74`), the five bundles,
   the worked pack and the example folder, every count equal to the
   Python reference's, ALL GREEN in 64 s (backlog #63, closed). The
   machine was a hosted Windows runner of GitHub Actions, commit
   `5a75454b`; the run is public (`https://github.com/christoph-puppe/JASCON/actions/runs/43204019670`).
   Since that commit the workflow `.github/workflows/validators.yml`
   runs both validators and the app's port on every change, so this item
   is a standing measurement and no longer a run somebody has to
   remember. Earlier the same day the twin had run on a second Windows
   machine on rc.2 with the advice rules (518 / 518; backlog #60). Both
   implementations have one author: their independence is language and
   runtime. A third,
   the JavaScript port in `jascon-app/`, passes the same vectors in the
   same workflow; what it leaves to the reference is in its readme.
   *(rc.4, 2026-11-13: the workflow ran the twin on Windows PowerShell
   5.1 twice. At commit `e4031a84`: the lint, then 637 / 637 in eighteen
   families, ALL GREEN in 218 s (`https://github.com/christoph-puppe/JASCON/actions/runs/43502988692`).
   At commit `82721959`, with the six vectors that the ports' deliberate
   defects had shown missing: 643 / 643 (`kernel: 54`, `author: 40`),
   the five bundles, the worked pack and the example folder, every
   count and each of the 15 AUTHOR and REVIEW lines equal to the Python
   reference's, ALL GREEN in 213 s (`https://github.com/christoph-puppe/JASCON/actions/runs/43504417645`).)*
4. **Corpus.** ◐ Risk: one, IFA, two Risk objects — enough to exercise
   the record's sourced half and to measure what the source lacks; not
   enough to exercise `rating`, `acceptance`, the later states, or
   `risk-coverage` at scale (D23). The second corpus is named, not
   delivered: a BSI 200-3 risk analysis, or BSI's `Risikomanagement`
   catalogue, or a real POA&M. Check: none converted; two check corpora
   were counted for fit (D24), the worked example ran against a stub, no
   runner exists. Advice: one worked pack, written for this purpose; no
   converter from component definitions, no census of public ones (D25).

Not re-run for this candidate: the OSCAL export suite (its inputs among
the shipped bundles are byte-identical to 1.0.0; the NIST release schema
it validates against is not in the repository). Risk, Check and advice
have no place in a 1.x *catalog* export; a POA&M-side, an
assessment-results and a component-definition export belong to the
pending lifecycle-export work.

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
| CP-RISK-1 landing | 2026-11-10 | The Risk proposal applied, reviewed and corrected (eight findings, each pinned by a vector; RISK-12 added); the first Risk corpus (IFA re-run) and what OSCAL's data lacks; found on the way — the 1.0.0 corpus did not verify off Windows (line endings), and coverage is path-level, not value arrival | "Amendments — CP-RISK-1" |
| The 2.0.0 decision | 2026-11-10 | The release that carries Risk is a major (D22 rev 3 stands); recorded as an exception to D22 test 1; Apache-2.0 | "Amendments — the 2.0.0 decision" |
| Corpus licence review | 2026-11-10 | Five bundles kept under their publishers' stated terms, six removed (terms forbid it, or none established); converters and coverage reports stay | "Amendments — the corpus licence review" |
| Raw blobs · the Risk rules stay | 2026-11-10 | Bundle files stored as the digested bytes (every delivery channel verifies); RISK-1/2/3/6 kept strict toward imported data | "Amendments — raw blobs" · "… the Risk rules stay" |
| **2.0.0-rc.1** | 2026-11-10 | This text: D23 new; D4, D8, D14, D15, D22 amended in place; gate state in IV.5b | this row |
| Likelihood and impact | 2026-11-10 | `rating` and `residual-rating` may carry `likelihood` and `impact`, each a level on a named scale; RISK-13 extended to them; the matrix, CVSS, FAIR and impact per dimension stay in facets; 6 vectors | D23 · "Amendments — likelihood and impact" |
| The matrix | 2026-11-10 | The organisation's matrix is an optional part of the level scale's pinned definition, not a facet; SCALE-4: a rating that states both inputs states the level of their cell, or an `override-rationale`; a mismatch fails; 9 vectors | D3.7 · D23 · "Amendments — the matrix" |
| Scale definitions | 2026-11-10 | `scales` pins in the manifest: a scale's levels in order, the organisation's wording and number; SCALE-1/2/3; not a kernel type; 9 vectors, a fifteenth family | D3.7 · D23 · "Amendments — scale definitions" |
| The kernel pin | 2026-11-10 | `kernel-version` in the content manifest: optional, absent = 1.0.0, required for content beyond 1.0.0 (KERNEL-1), fail-closed on an unimplemented kernel (KERNEL-2); 9 vectors, a fourteenth family; IFA and example manifests pinned | D3.6 · "Amendments — the kernel pin" |
| rc.1 review | 2026-11-10 | External review: nine findings reproduced and fixed — justification needs an assessed treatment decision, `tailoring-refs`, RISK-13/14, typed Tailoring selection edges, withdrawn Tailorings/Requirements, checked dates; the Mapping Model date corrected; `PRIOR-ART.md` | CP-RISK-1 §13 · "Amendments — the rc.1 review" |
| CP-CHECK-1 | 2026-11-11 | The Check proposal: schema, reference validator, 156 vectors, a worked example with an evidence store, a census of two open check corpora; the PowerShell twin ported and run (415 / 415, #56) | `drafts/CP-CHECK-1.md` |
| Check accepted | 2026-11-12 | The grammar compared with the published RFC 9485 (surrogate code points refused, #61 closed). Six author decisions: a consumer-side clause for D22 (#48 closed); run rows stay kernel; `requirement-ref` resolves if present; Check goes live with 2.0.0; no new quantifier, but every resource is evaluated and the failing share reported; `not-equals` as the twelfth comparator. 156 → 188 vectors; the reader reads the type (#57 closed) | CP-CHECK-1 §13 · "Amendments — CP-CHECK-1" |
| **2.0.0-rc.2** | 2026-11-12 | D24 new; D4, D14, D15, D22 amended in place; Risk's exception paragraph replaced by the clause | "Amendments — CP-CHECK-1" |
| CP-ADVICE-1 | 2026-11-12 | The advice-pack proposal: manifest header, `statement-ids`, the `capability-ref` grammar, ADVICE-1 to ADVICE-11, 71 vectors, a worked pack, the PowerShell twin run on Windows (518 vectors, which also closed #60). ADVICE-7 found one defect in the converted IFA bundle | `drafts/CP-ADVICE-1.md` §13 |
| Advice accepted · the decisions before the tag | 2026-11-12 | Twelve author decisions. Advice: bundle only; Components only; `statement-ids` kept against D22; `product-version` added; ADVICE-3 and ADVICE-7 kept; a `describes` relation for third parties; one release per set. Before the tag: `Deviation.opened` and the `due` of an action typed (#47a, #52: the superset property ends for free-text dates); history is left as it is (#50); a Tailoring names no Component (#51); Unicode categories follow the host (#59) | CP-ADVICE-1 §14 · "Amendments — CP-ADVICE-1 and the decisions before the tag" |
| **2.0.0-rc.3** | 2026-11-12 | This text: D25 new; D3, D5, D6, D8, D13, D15, D22, D24 amended in place; gate state in IV.5b | this row |
| The number domain | 2026-11-13 | A fifth outside report (issue 27 in the GitHub tracker) showed the reference and the app computing two verdicts and two semantic digests for integers beyond 2^53 and for `1.0`. D3 item 3 had named a "permitted number domain" that no text defined. **D3.9 new, NUMBER-1:** integers in plain digits, of magnitude at most 2^53 − 1; rejected, never rewritten; D24's evaluation step 3 amended. `jcs` 8 → 22 vectors, `parameter` 19 → 21, `check` 199 → 203; 568 in all. Backlog #67 closed. After rc.3 | D3.9 · "Amendments — the number domain" |
| The value-level check of the converters | 2026-11-13 | Two more outside reports (issues 32 and 33 in the GitHub tracker): `value_arrival()` matched substrings across one joined string, so the IFA figure of 394 of 835 was too high; and any global check hides a dropped value behind an equal one elsewhere. The helper is `global_occurrence()` now, on typed whole values, with key-only and embedded matches listed apart and not counted: **283 of 835**, 124 content values without an equal, stated as an upper and a lower bound. R16 and IV.5b item 6 amended; backlog #41 re-planned to a ledger of source occurrences per converter. No kernel rule, vector or bundle object changes | "Amendments — the value-level check of the converters" |
| Outside reports on the run rules | 2026-11-13 | Four reports from outside (issues 23 to 26 in the GitHub tracker), each reproduced: the reference accepted an evidence record outside `evidence/sha256/`, a `collector-id` on a Check without collectors, a row parameter its Check does not read, and a record that binds no observation. CHECK-12, CHECK-13 and CHECK-15 amended in place (D24); the three engines follow; `check` 188 → 199 vectors. After rc.3; the counts in the Status and in IV.5b and IV.7 are those of rc.3 | "Amendments — the outside reports of 2026-11-13" |
| Code points in the twin · the open backlog | 2026-11-13 | The PowerShell twin compared strings with PowerShell's operators, which fold case and compare under a culture; a Tailoring whose id differed from its content's origin by one U+00AD was read as the authority's own. No operator compares two strings there any more, and a lint that parses the twin keeps it so (#58 closed, with the residue of #45). `reference` 13 → 18 vectors, `tier` 9 → 10; 574 in all. No shape and no rule changed. The same day: the record of catalogue entries that do not apply got a schema, outside the kernel (#54 closed); the two OSCAL response types without a treatment code stay without one (#47b closed, C.10); #65 and #66 accepted for 2.0.0 and not yet landed. After rc.3 | D2 · C.10 · "Amendments — the open backlog before 2.0.0" |
| **2.0.0-rc.4** | 2026-11-13 | This text: D26 new (who decided, and when); D8, D13 and D23 amended in place. `provenance` optional on a Tailoring and its entries, a Risk and its ratings, an Implementation and a Finding; `decided` and `review-due` on a Deviation; `date` on an authorization; AUTHOR-1 to 4 and REVIEW-1 as reports; three times typed (DATE-3 to 5). A new vector family, `author` (40), and `kernel` 25 → 54; 643 in all, 18 families. Backlog #65 and #66 | D26 · "CP-AUTHOR-1 landed" |

## IV.7 Release artifacts (what this candidate ships with)

In the repository at the rc.4 commit. "Green" below means the Python
reference validator; the PowerShell twin's state is IV.5b item 3.

- **Kernel schema** `jascon-2.0.0.schema.json` — closed
  shapes, shape-disjoint type inference, 11 types + Deviation + manifest
  (with the pack header) + the evidence record;
  the `text` primitive on every human-readable field. A superset of the
  1.0.0 schema except in two fields, which it types (D8).
- **Eight stdlib facet descriptors**: the seven of 1.0.0 (incl. the
  normative DSSE envelope profile), unchanged and pinned VERBATIM wherever
  bundled, and `collector@1` *(2.0.0-rc.2)*, which carries collector code
  on a Check and declares `modifies-semantics: []`.
  `risk-analysis@1` is parked, with one measured payload (Appendix D).
- **Conformance corpus**: **537 vectors, 17 families** (jcs 8 ·
  modality 21 · parameter 19 · tailoring 19 · attestation 5 · facet 7 ·
  reference 13 · lifecycle 38 · tier 9 · dsse 5 · composition 7 ·
  conditional 8 · risk 73 · kernel 25 · scale 18 · check 188 · advice
  74; with the amendments after rc.3 in IV.6 and the vectors of rc.4, **643 in 18 families**: `author` 40, `kernel` 54, `reference` 18, `tier` 10, `jcs` 22, `parameter` 21, `check` 203). In `risk-vectors.json`, `expected-rule` is the portable assertion; in `author-vectors.json`, the rule, the object and the count of each report line;
  in `check-vectors.json` and `advice-vectors.json`, the outcome and the
  named rules.
- **A worked advice pack** under `jascon/example-packs/`, and the example
  folder after importing it.
- **Two reference validators**: `validate_core.py` (Python, jsonschema
  only) — green; `validate_core.ps1` (PowerShell 5.1, zero dependencies)
  — green on 2026-11-13 on all 643 vectors of this candidate, on Windows
  PowerShell 5.1 (IV.5b item 3). A workflow runs both, and the app's
  port, on every change (`.github/workflows/validators.yml`).
- **Bidirectional export**: `export_oscal.py` — as at 1.0.0 (OSCAL 1.2.2
  out, generic re-import, 5,886/5,886 round-trip measured on the ten
  catalog bundles then present); not re-run.
- **Converters for all eleven corpora** under `jascon/scripts/`, writing
  one byte spelling on every OS; `oscal_conv_lib.global_occurrence()` for
  the value-level check (wired into the IFA report so far). *(rev.
  2026-11-13: until then `value_arrival()`, which matched substrings and
  overstated the figure; and the check is global, an upper bound on what
  was carried, not a trace of each value — backlog #41. `Ledger` in the
  same file traces each source value to its destination; wired into the
  IFA converter, which writes `ifa-conversion-ledger.json`.)*
- **Five corpus bundles** under `converted_examples/` — AU.ISM, DE.BSI,
  US.SP800-53, US.CSF, US.IFA-GoodRead: 3,715 manifest-listed objects,
  both SHA-256 digests re-verified per object, stored as the digested
  bytes, each with its publisher's terms in `SOURCE-LICENSE.md`. **Six
  measured, not redistributed** — CIS.Controls, CIS.Ubuntu2404, DE.C5,
  DE.C3A, BE.CyFun, FedRAMP-CR26: coverage report and
  `NOT-REDISTRIBUTED.md` only.
- **The normative appendices** — A (shapes, with A.9b Risk) · B
  (primitives incl. B.1.9 and B.1.10, operations, predicates) · C (code
  systems, with C.3c, the treatment options and C.12 to C.15 for Check) — at
  `jascon/references/appendix-{a,b,c}-*.md`, with the handbook chapters
  ch01–ch15 and appendices D–G beside them.
- **The Decision Rationale Register** —
  `drafts/jascon-decision-rationale-register.md` — and the two
  change proposals with their records, `drafts/CP-RISK-1.md`,
  `drafts/CP-CHECK-1.md` (with its census under
  `drafts/cp-check-1-census/`) and `drafts/CP-ADVICE-1.md` (with the
  scripts that write its vectors and its worked example under
  `drafts/cp-advice-1/`).
- **The reader** (`one-page-apps/jascon-reader.html`, v1.9.0) —
  recognises Risk and Check; it shows recorded verdicts and recomputes
  none. It shows a pack's header, the pack manifests a set keeps and a
  Component's `product-version`, and checks a kept manifest against its
  name; it runs no ADVICE rule and checks no signature. **The app**
  (`jascon-app/`, build 0.9.3) writes Checks, drafts them with a model
  on request and recomputes every recorded verdict; it runs no
  collector. It ports ADVICE-1 to ADVICE-11 and passes the 74 advice
  vectors and the 14 kernel shape vectors (115 tests). It imports a pack
  from a folder, a ZIP or a URL after a preview, prints the receipt,
  shows what another release changes and which edges it leaves without
  a target, and writes an adoption as `<component-id>#<capability-id>`.
  A publisher is shown as claimed, as attested and not verified, or as
  proven (D25). Driven in a browser: import, a second import, another
  release, a refused pack, the three publisher states, adoption, and
  two exports through the reference validator. Not driven: drag and
  drop of a pack, and the German texts of the new views on screen.
- **The pack builder** (`one-page-apps/jascon-pack-builder.html`,
  v1.2.0) — the vendor's side of D25: one offline HTML file that writes
  a pack from a form and judges it with the app's kernel code, inlined
  and held equal to the app's by `one-page-apps/tools/sync-inlined.mjs`
  in CI. It signs a release with Ed25519 in the browser or prepares the
  bytes for an external signer, and refuses changed content under the
  version of an opened release and a changed Component under its old
  version. Measured by four browser tests: the worked pack, typed in,
  comes out with its Component byte for byte and its manifest equal but
  for the provenance line, and the reference reports its signature
  VERIFIED; signed by `openssl` from the prepared bytes, the same. Since
  v1.1.0 it imports an OSCAL component definition: one recommendation
  per implemented requirement, `statements` to clauses, `set-parameters`
  to suggested values, control ids through the loaded catalogue, the
  rule of the NIST SP 800-53 conversion or a prefix the vendor gives,
  and a report of what it could not place and what a pack cannot carry.
  Measured on a test component definition: with the SP 800-53 catalogue
  loaded, every clause and suggested value passes ADVICE-5 and ADVICE-6,
  values set for a whole control implementation land where the catalogue
  declares them, and Rev 4 parameter ids take the catalogue's names.
  Run over NIST's example component definitions
  (`drafts/cp-advice-1-census/`): 10 of 10 implemented requirements
  resolved without a catalogue, every clause and value carried, Rev 4
  sources and a control implemented twice named. Seven browser tests;
  sixteen deliberate defects in the builder each turn one of them red.
- **License**: Apache-2.0 for the original work (`LICENSE`, `NOTICE`);
  the shipped bundles under their publishers' terms.

## IV.8 From rc.1 to 1.0.0 *(history, as released)*

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

## IV.9 From 2.0.0-rc.4 to 2.0.0

1. **The version** — ✓ decided: 2.0.0 (author, 2026-11-10); it carries
   Risk, Check and advice packs (author, 2026-11-12).
2. **The Risk rules toward imported data** — ✓ decided: kept strict (D23).
3. **Licence** — ✓ Apache-2.0; corpus terms reviewed (§2).
4. **The second implementation** — ✓ ran green on 2026-11-11 (415
   vectors), on 2026-11-12 on rc.2 with the advice rules (518 vectors;
   backlog #60, closed) and on 2026-11-12 on this candidate (537
   vectors, Windows PowerShell 5.1 on a hosted runner; backlog #63,
   closed). It now runs on every change.
5. **Decided** — ✓ a kernel-version pin in the manifest (#44, D3.6); ✓
   D22 has a consumer-side clause (#48); ✓ the six open points of
   CP-CHECK-1; ✓ the eight of CP-ADVICE-1; ✓ `Deviation.opened` and the
   `due` of a Finding's action are typed, and the superset property
   yields to that (#47a, #52; D8); ✓ the removed bundles stay in the
   history (#50): merging stopped their publication, old commits and the
   `v1.0.0` tag keep them, and every commit id cited in the register
   stays valid; ✓ a Tailoring names no Component (#51; D13); ✓ Unicode
   categories follow the host (#59; D24); ✓ every machine identifier
   carries `jascon` (register, "Amendments — 2026-11-11"); ✓ a Deviation
   may say when it was decided and when it is due for review, and the
   records and decisions that named no author may name one (#65, #66;
   D26; author, 2026-11-13). **Nothing is left to decide before the
   tag.**
6. **Work, not decisions** — ✓ the implemented I-Regexp grammar was
   compared with the published text of RFC 9485 on 2026-11-12 (#61,
   closed); ☐ a ledger of source occurrences per converter, and the
   re-wording of "converted losslessly" that follows from it (#41,
   re-planned on 2026-11-13: the global check that was to be rolled out
   cannot show that a single value arrived; ✓ the ledger exists and the
   IFA converter is wired; ✓ its unaccounted values were decided class by
   class on 2026-11-13, none of its 835 source values is unaccounted,
   and the three references that name nothing their source defines are
   declared as defects of the source; ☐ the other ten converters); ☐ a real
   attestation in the example bundle (#46); ☐ `Assessment.method`
   payloads held to their pinned schema (#55); ☐ a second Risk corpus
   (IV.5b item 4).
7. **Not part of this candidate, named so that nobody reads it as more
   than it is** — a runner that executes collectors and writes evidence;
   a declared request format for `http-api` collectors in `collector@1`
   (#62); a census of checks against cloud APIs; a census of OSCAL
   component definitions vendors published (NIST's own examples are
   counted, `drafts/cp-advice-1-census/`).
8. **Tag `v2.0.0`** — on the author's go. Nothing in this list blocks it.
