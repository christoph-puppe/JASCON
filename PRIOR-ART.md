# Prior art — the formats around JASCON

*State: 2026-11-10. Written during the external review of 2.0.0-rc.1
(`drafts/CP-RISK-1.md` §13), because the specification's own prior-art
section (IV.3) named OSCAL and NIST IR 8477 and nothing else.*

This file answers three questions: which machine-readable formats already
cover the ground JASCON covers, which JASCON features are therefore **not**
new, and what is left that no neighbour was found to combine.

## How to read the sources

Every entry carries one of two marks.

- **[repo]** — read from the project's own public repository or release
  page on the date above.
- **[secondary]** — taken from search results, announcements or third-party
  descriptions; the primary site was not reachable when this was written
  (`csrc.nist.gov`, `pages.nist.gov`, `cyclonedx.org` and
  `oscalfoundation.org` among them). Verify before citing.

Nothing here was measured the way the corpora in this repository were
measured. No neighbour's data was converted, and no feature claim was tested
against an implementation. Feature cells say what a project's schema or
documentation shows, not what its tools do.

## The neighbours

### OSCAL (NIST) — the incumbent

- **Releases [repo]:** v1.2.0 (12 December; the release notes read "a minor
  release which provides an additional OSCAL Model: Control Mapping"),
  v1.2.1 (6 March 2026), v1.2.2 (30 April 2026), v1.2.3 (7 August 2026,
  marked latest). The year of v1.2.0 is 2025 by sequence; the release page
  shows no year for it. <https://github.com/usnistgov/OSCAL/releases>
- **What it models:** catalog, profile (tailoring), component definition,
  system security plan, assessment plan, assessment results, plan of action
  and milestones, and since 1.2.0 control mapping. XML, JSON and YAML,
  generated from Metaschema.
- **Risk:** a `risk` assembly in assessment results and POA&M — tied to
  findings and observations, not to control selection. This is the gap
  JASCON's Risk type addresses (D23).
- **Not present [secondary]:** a language-map construct for prose, and
  native signing (back-matter resource hashes only).
- **Governance [secondary]:** NIST owns the specification and repository.
  An OSCAL Foundation was founded in 2025 as an industry body; no transfer
  of stewardship was found. NIST published a draft strategy paper (CSWP 53,
  "Charting the Course for NIST OSCAL") in December 2025.

### Gemara (OpenSSF) — the closest non-OSCAL notation

- **[repo]** <https://github.com/gemaraproj/gemara>. The README describes
  it as "a standardized, machine-readable data model designed to bridge the
  gap between high-level compliance requirements" and their implementation.
  Schemas are written in CUE over YAML/JSON; the repository's file list
  includes `riskcatalog.cue` and `mappingdocument.cue`.
- **[secondary]** A layered model with guidance, control, threat, risk and
  capability catalogs, policy, evaluation and audit logs, and mapping
  documents with typed relationships (implements, supports, equivalent,
  subsumes and others) carrying strength and confidence. Versioned 1.x
  releases during 2026.
- **Used by [repo]:** FINOS Common Cloud Controls
  (<https://github.com/finos/common-cloud-controls>) and the OpenSSF OSPS
  Baseline (<https://github.com/ossf/security-baseline>), which also
  exports OSCAL.
- **Overlap with JASCON:** typed mappings, a risk catalog, structured
  requirement keywords, results. **Not seen:** signing, multilingual prose,
  content addressing.

### CycloneDX Attestations (OWASP, ECMA-424) — the closest attestation model

- **[repo]** <https://github.com/CycloneDX/specification>; latest release
  1.7.2 (17 September; year not shown on the release page).
- **[secondary]** Introduced with CycloneDX 1.6. `definitions.standards[]`
  carries standards as data — requirements and levels. `declarations`
  carries assessors, attestations mapping a requirement to claims and
  counter-claims with a conformance score, evidence with author and
  expiry, and an affirmation with signatories. Signatures are enveloped at
  several levels (JSON Signature Format).
- **Overlap with JASCON:** requirement → claim → evidence → signed
  affirmation is the ground of Assessment, Finding and Attestation.
  **Not seen:** tailoring operations, typed cross-framework mappings, a
  risk object, language maps. References are document-internal, not
  content hashes; signatures are JSF, not DSSE.

### CISO Assistant library format (intuitem)

- **[repo]** <https://github.com/intuitem/ciso-assistant-community> — an
  AGPL governance tool with a YAML library format and more than 200
  frameworks.
- **[secondary]** Objects carry URN identifiers and integer versions;
  frameworks are requirement trees; libraries also hold reference controls,
  threats and risk matrices; `requirement_mapping_set` uses set-theory
  relationships with a strength; objects carry a `translations` map keyed
  by locale.
- **Overlap with JASCON:** the per-object translations map is the nearest
  existing analogue of the `text` language map; set-theory mappings; risk
  matrices. **Not seen:** attestations. The format is bound to one tool.

### Regulator-specific plain JSON / YAML

- **FedRAMP rules [repo]:** <https://github.com/FedRAMP/rules> — one
  consolidated rules JSON with a JSON Schema; definitions, rules and key
  security indicators; requirement keywords are structured. Deliberately
  not OSCAL. This is the "CR26" source of this repository's census.
- **BSI C5:2026 [secondary]:** a first machine-readable release as YAML,
  German and English as separate files.
- **BSI Grundschutz++ [repo]:**
  <https://github.com/BSI-Bund/Stand-der-Technik-Bibliothek> — OSCAL
  catalogs, profiles and mappings under CC BY-SA 4.0, with BSI's own
  namespaced vocabularies (modal verbs, target-object categories, security
  levels, base threats) carried as OSCAL props and links.
- **ACSC ISM [secondary]:** quarterly OSCAL releases with profiles for the
  Essential Eight and the classification levels.

What these show is the pattern the JASCON census is built on: publishers
structure modality, deadlines and applicability themselves, each in its own
way, inside OSCAL props or outside OSCAL altogether.

### Mapping semantics

- **NIST IR 8477 [secondary]** defines the relationship styles — concept
  crosswalk, supportive, set theory, structural. JASCON's `Mapping`
  relationship codes are taken from it (D20).
- **Secure Controls Framework, STRM [secondary]:** set-theory relationship
  mapping across 200+ frameworks, published as spreadsheets and PDF, with
  an OSCAL JSON export of the catalog.
- **OpenCRE (OWASP) [repo]:** <https://github.com/OWASP/OpenCRE> — a
  hub-and-spoke requirement graph, not a catalog format.

### Attestation and transparency layer

- **in-toto attestations [repo]:**
  <https://github.com/in-toto/attestation/tree/main/spec/predicates>. The
  vetted predicates cover provenance, verification summaries, test results
  and SBOMs. None attests a control or a requirement; the Simple
  Verification Result and the SLSA Verification Summary are the nearest.
- **DSSE** is the envelope JASCON's attestation profile uses; it is
  in-toto's, not JASCON's.
- **SCITT (IETF) [secondary]:** an architecture for transparency services
  over signed statements, published as an RFC in 2026.

### Older and adjacent

- **SCAP / XCCDF / OVAL [secondary]:** checklist and check languages in
  XML; XCCDF profiles are select-and-refine tailoring. No mappings, risk or
  language maps.
- **OpenControl / Compliance Masonry [repo]:** YAML standards and component
  narratives; no meaningful activity since 2023.
- **MITRE Heimdall Data Format, OCSF compliance findings, SARIF
  [secondary]:** result formats. They carry what a check found, not what a
  standard requires.
- **NIST IR 8286 [secondary]:** risk register and risk detail record
  schemas — the nearest prior shape for a risk *register*, with no edge to
  control selection.
- **ISO/IEC 27001, 27002, IEC 62443, PCI DSS:** no official
  machine-readable edition was found. Third-party renderings exist in SCF
  and CISO Assistant.

## Feature by feature: what is not new

| JASCON feature | Nearest prior art |
|---|---|
| Structured modality per statement (must / should / may) | BSI Grundschutz++ modal-verb vocabulary; FedRAMP rules keywords; OSPS Baseline |
| Prose as a language map | CISO Assistant `translations` |
| Sets and baselines as membership, not markers | OSCAL profiles; XCCDF profiles |
| Tailoring as a closed list of operations | OSCAL profile `alter` / `set-parameter`; XCCDF `refine-value` |
| Typed cross-framework mappings | NIST IR 8477; SCF STRM; OSCAL 1.2 mapping model; Gemara mapping documents |
| Typed, schema-bound extensions | Gemara (CUE); OSCAL props with namespaces (untyped) |
| Component / implementation / assessment / finding chain | OSCAL lifecycle models; CycloneDX declarations |
| Signed attestation over requirements | CycloneDX affirmations and signatures; DSSE envelope |
| A risk record | OSCAL `risk` (ex post); Gemara risk catalog; CISO Assistant risk matrices; IR 8286 |
| Plain JSON with JSON Schema instead of a metaschema | FedRAMP rules; CycloneDX |

## What no neighbour was found to combine

Within the limits stated at the top, no format was found that has all of:

1. **Content-addressed objects with two digests** — one over the delivered
   bytes, one over the canonical content without annotations — so that an
   attestation survives re-packaging.
2. **A modality partial order** against which tailoring is checked, with
   weakening routed through a recorded Deviation.
3. **A risk record joined to control selection**, so that "which selected
   requirements rest on no risk" is computed (`risk-coverage`).
4. **Fail-closed extension declarations**: an extension states which
   computations it changes, and a tool that does not understand it must
   stop.

Each of the four has partial precedent. The claim is about the combination,
and it is only as strong as this survey.

## What follows for JASCON

- **Gemara and CycloneDX Attestations belong in the specification's
  prior-art section and in the handbook's objections chapter.** A reader
  from either community will ask why not extend theirs.
- **The attestation niche is real and narrow.** in-toto has no predicate
  that attests a requirement; a JASCON attestation expressed as an in-toto
  predicate would reach an existing verifier ecosystem instead of asking
  for a new media type.
- **Mapping codes should stay aligned with IR 8477**, which SCF, OSCAL and
  CISO Assistant already follow.
- **The risk-to-selection join is the feature with the least precedent.**
  The upstream issue the proposal cites (usnistgov/OSCAL #2292) is the
  place where it can be tested against people who did not write it.
- **Public footprint:** a search on the date above found no third-party
  mention of JASCON or its former working titles outside this repository.
  The measured conversions and the specific findings against published
  catalogs are the part of this work that other projects can use without
  adopting the format.
