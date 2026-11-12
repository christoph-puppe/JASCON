# Prior art — the formats around JASCON

*State: 2026-11-10. Written during the external review of 2.0.0-rc.1
(`drafts/CP-RISK-1.md` §13), because the specification's own prior-art
section (IV.3) named OSCAL and NIST IR 8477 and nothing else. Extended
2026-11-13 with a feature-by-feature check of five neighbours against
their schemas at named versions ("Ten user-facing features", below).*

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
  XML; XCCDF profiles are select-and-refine tailoring. No mappings or risk.
  *Corrected 2026-11-13:* this entry said "no language maps", taken from a
  secondary source. XCCDF 1.2 repeats `title` and `description` per
  `xml:lang` (read in the XSD and NIST IR 7275r4); see the nine-feature
  check below.
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
| Prose as a language map | CISO Assistant `translations`; XCCDF `xml:lang` |
| Sets and baselines as membership, not markers | OSCAL profiles; XCCDF profiles |
| Tailoring as a closed list of operations | OSCAL profile `alter` / `set-parameter`; XCCDF `refine-value` |
| Typed cross-framework mappings | NIST IR 8477; SCF STRM; OSCAL 1.2 mapping model; Gemara mapping documents |
| Typed, schema-bound extensions | Typed custom fields inside CISO Assistant; CUE profiles that narrow Gemara's closed schemas (OSPS Baseline); OSCAL props with namespaces (untyped); XCCDF elements in foreign namespaces (validated laxly) |
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

## Ten user-facing features, checked against the schemas (2026-11-13)

A second pass, made for the GRC Engineering Community talk: ten features
that help the people who run compliance and the people who audit it,
checked against the schemas and code of five neighbours. Unlike the survey
above, every cell here was read from a primary source at a named version.
No neighbour's data was converted; a cell says what the schema or code
provides, not what a deployment does with it.

Versions read: **OSCAL** v1.2.3 (Metaschema sources, JSON schema and XSD) ·
**Gemara** v1.6.0 (CUE schemas, commit 14a8b1c; `main` at 5cea1b6 where it
differs) · **CycloneDX** 1.7.2 (`bom-1.7.schema.json`, `jsf-0.82`, XSD,
proto) · **CISO Assistant** community `main` at 694e32a9 (Django models and
library YAML; **T** = the tool's data model, **F** = the library exchange
format) · **SCAP** XCCDF 1.2 XSD, NIST IR 7275r4, SP 800-126r4 (SCAP 1.4,
June 2026), IR 7802, OpenSCAP SCE.

| Feature | OSCAL 1.2.3 | Gemara 1.6 | CycloneDX 1.7 | CISO Assistant | SCAP / XCCDF 1.2 | JASCON |
|---|---|---|---|---|---|---|
| 1 Risk-based control selection (ISO/IEC 27001 6.1.2–6.1.3) | no — `risk` only in assessment results and POA&M, after the fact | partial — a policy lists mitigated risks; controls join only through threats | no — a risk document can only be linked | T yes (SoA endpoint from `RiskScenario.applied_controls`) · F no | no — optional free-text `select/remark` | yes, 2.0.0 candidate — `Risk.treatments` name requirements to the clause; `risk-coverage` computes the SoA |
| 2 Risk acceptance on record | partial — assembled from props, `risk-log` and statuses; no approver or acceptance date field | partial — `#AcceptedRisk`, justification optional, no approver or date | no | T yes (`RiskAcceptance`: approver, state, `accepted_at`, expiry) · F no | yes for results — `override` with required `@authority`, `@time`, old/new result, `remark` (authority is free text) | yes, 2.0.0 candidate — `acceptance` {approver-ref, date, rationale} plus residual level on a named scale |
| 3 Every decision traceable | partial — profile changes carry no author; who/when only per document | partial — required `modification-rationale` on modifiers (removed on `main`); exclusions bare | no | partial — T audit log records who and when on every change; a justification is not enforced | partial — optional `remark` per change, who/when per Tailoring document; severity can drop unjustified | partial — every weakening needs an approved Deviation (approver, rationale, date), checked against the modality order; strengthening ops carry no individual author; exclusion rationale optional |
| 4 Vendor recommendations kept apart from the controls | yes — the component definition cannot modify catalog or profile; adoption copies into the SSP, provenance link optional | partial — separate artifacts, explicit import; no vendor type or authority boundary | partial — claims and attestations are separate objects, but one file may also define the standard's text | partial — explicit library load; a library update can rewrite existing assessments | partial — a separate Tailoring file leaves the benchmark untouched, but the vendor's checks and defaults decide the results | yes, 2.0.0 candidate — advice packs hold Components only; import can change no requirement, tailoring or assessment (ADVICE-1..11); adoption by citation; publisher labelled claimed, attested or proven |
| 5 Exceptions and findings with deadlines | yes — `risks/deadline`, deviation statuses, remediation milestones | no — no due date or expiry on findings or exemptions | partial — only `evidence.expires` | T yes (`SecurityException.expiration_date`, finding `due_date`) · F no | no — no waiver type, due date or expiry | partial — typed `due` on finding actions and typed `review-due` on risks (2.0.0 candidate); **a Deviation has no expiry** |
| 6 Automated checks as code | partial — tool and observations recordable; no check logic on a control | partial — evaluation runs recorded in detail; check logic outside the format | partial — a command line as a string in a workflow task | partial — T imports results of external tools; no logic attached; old runs pruned | partial — any engine via `check/@system`; OpenSCAP SCE runs any executable but is outside SCAP 1.4 conformance; ARF makes runs reproducible | yes, 2.0.0 candidate — `collector@1` code in sh, bash, PowerShell, Python, Ansible, HTTP or a namespaced runtime; declarative criteria; every verdict recomputed from the recorded observation; no runner exists |
| 7 Clause → implementation → check run → evidence file | yes — control → SSP → finding → observation → back-matter resource with hash | partial — clause → run → evidence with digest; no implementation record (layer 4 has no schema) | partial — clause → claim → evidence; attachments carry no hash | partial — T clause → control → evidence with SHA-256; tool results not linked to controls or evidence | partial — rule → result → collected items; references are text, items unhashed | yes — requirement → Implementation → Assessment run (`check-ref`) → `evidence/sha256/`; check runs are 2.0.0 candidate |
| 8 Several languages in one object | no | no | no | yes — F and T reference objects carry `translations`; user-created objects single-language | yes — `@xml:lang` on repeatable title and description | yes — every human-readable field is a BCP 47 language map (1.0.0) |
| 9 A signature that survives repackaging | no — byte hashes on resources only; inline signing declined (issue #245) | bytes only — signed OCI bundle via grcli and cosign, outside the schema | partial — JSF over JCS per object survives re-indentation and key order; XSD and proto carry no signature | no — byte hashes for deduplication | partial — XML-DSig; required C14N keeps whitespace, so re-indenting breaks it; countersigning in SCAP 1.4 | yes — semantic digest over canonical content without annotations, DSSE envelope; verifies after reformatting, a changed annotation and an OSCAL round trip (1.0.0, 5,886/5,886) |
| 10 Extensible by facets: a contract that is enforced, pinned, and stops a tool that does not understand it | partial — `props` with an `ns` URI on almost every object; nothing ties the namespace to a schema, no document pins a version, no consumer must stop | partial — closed CUE definitions; a third party can narrow them with a CUE profile (OSPS Baseline) but not add a field; `cue vet` rejects unknown fields; the artifact does not pin the profile | partial — `properties` as name/value strings; the property taxonomy registry is optional; no pin; unknown properties pass | T partial (typed `CustomFieldDefinition`, values checked) · F no (unknown library keys silently ignored; `validate_library` is empty) | partial — `xs:any ##other` in metadata, target facts and check content, validated laxly; no pin; an unknown check system gives `notchecked`, an unknown extended component a warning | yes — facets registered under their own namespace, schema pinned in the manifest by exact version and digest, standard-library facets pinned verbatim; a facet that changes semantics stops a tool that does not implement it; annotations stay outside the digest (1.0.0) |

What this changes in the claims above:

- **Not unique:** several languages (CISO Assistant, XCCDF), risk acceptance
  (CISO Assistant's tool, XCCDF overrides), deadlines (OSCAL, CISO
  Assistant's tool), the evidence chain (OSCAL), vendor separation (OSCAL
  component definitions). JASCON's version is stricter in places, which is
  a different claim from "only".
- **No neighbour has as a format:** risk joined to control selection
  (CISO Assistant has it only inside its application), check verdicts
  recomputed from recorded observations with the pass mark set by the
  tailoring, and an extension whose contract is pinned and which stops a
  tool that does not understand it (Gemara rejects unknown fields, but
  offers no way to add one).
- **Closest rival on signing:** CycloneDX — per-object JCS signatures
  survive reformatting, not conversion. JASCON's semantic digest also
  ignores annotations and verifies after an OSCAL round trip.
- **Where JASCON is behind:** a Deviation has no expiry (CISO Assistant's
  security exceptions and OSCAL's risk deadlines do), and no tailoring
  operation records its own author (CISO Assistant's audit log does).
  Both are candidates for the backlog.

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
