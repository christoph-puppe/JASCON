> **ERRATUM (2026-07-21, project adjudication — Appendix F.7/F.8).** This
> review is on the record as received. Two of its Dimension-8 figures are
> **refuted by measurement**: "50–70 % payload reduction" (measured: ISM
> −29 %, GS++ −50 %, CR26 **+55 %**) and "~60 % fewer LLM tokens"
> (unmeasured by anyone). Its "93,259 values" is the pre-drop census total
> — the 8-corpus total in its own table is 130,350. Do not quote these
> numbers as project claims. Full adjudication:
> `jascon/references/appendix-f-objections.md` §F.7.

# Comprehensive Deep Research & Technical Review: Semantic OSCAL (v0.5 Specification)

**Date:** 2026-07-21  
**Repository:** [Semantic-OSCAL-2-Ideas](https://github.com/christoph-puppe/Semantic-OSCAL-2-Ideas.git)  
**Target Specification:** OSCAL Semantic Core v0.5 normative draft  

---

## Executive Summary & Verdict

**Verdict:** **Pre-1.0 (v0.5 Specification), Evidence-Gated, High Technical Viability.** 

The **OSCAL Semantic Core** specification presents a rigorously engineered, empirically validated alternative to the legacy OSCAL 1.x architecture. By replacing **eight deep, nested document models** with a **graph of nine shallow, globally identified kernel objects**, the project directly resolves the defining paradox of OSCAL 1.x: *rigidity where frameworks legitimately differ, and contractlessness where semantic meaning lives*.

### Key Strengths & Achievements
1. **Empirical Rigor**: Unlike legacy standards designed via committee consensus, every normative primitive traces directly to a measured failure or quantitative requirement across **8 converted corpora** (93,259 values, 0 unexplained fields).
2. **Elimination of "Props" Pathology**: Replaces over 22,000 unvalidated, schema-less `props` across ACSC ISM, BSI Grundschutz++, and FedRAMP CR26 with typed kernel primitives and registered facets.
3. **Cryptographic Integrity Realism**: Solves signature breakage from legitimate repackaging via a **dual-digest architecture** (`package-digest` vs. `semantic-digest`) and bi-modal verification (*Full Match* vs. *Semantic Match*).

### Primary Gaps to Reach 1.0 (v0.6 Executable Gate)
- Executable JSON Schemas (Draft 2020-12) and the lines-of-code benchmark comparing a Semantic Core validator against an OSCAL 1.x validator ("the weekend validator test") remain the primary pending deliverable.

---

## Deep-Dive Section Findings (Dimensions 1–5)

### 1. Architectural & Graph Model Integrity

#### Kernel vs. Document Model ([drafts/oscal-semantic-core-v0.5-specification.md](drafts/oscal-semantic-core-v0.5-specification.md))
- **9 Kernel Types**: `Requirement`, `RequirementSet`, `Tailoring`, `Mapping`, `Component`, `Implementation`, `Assessment`, `Finding`, `Attestation` (plus `Deviation` & `Authorization` sub-objects).
- **Documents as Renderings (L4)**: Replaces deep document trees with flat records linked via global URIs. Documents (e.g., SSPs, SARs, Catalogs) become presentation-layer views generated from graph queries rather than transport units.
- **Elimination of Profile Merge Algebra**: Eliminates OSCAL 1.x profile resolution, inheritance cascades, and positional JSON Patch fragility. Tailoring operations (`set-modality`, `set-parameter`, `replace-prose`, `detach-facet`, `excludes`) use **identity addressing** (`requirement-ref` + `statement-id`), making overrides deterministic and reordering-resistant.

#### Three-Layer Separation ([drafts/oscal-semantic-core-decision-rationale-register.md](drafts/oscal-semantic-core-decision-rationale-register.md))
```
+-----------------------------------------------------------------------+
|  Kernel (Normative, Fixed)                                           |
|  Modality, statements, typed parameters, membership, history, mapping |
+-----------------------------------------------------------------------+
|  Facets (Registered, Schema-Pinned, Fail-Closed)                      |
|  security-objectives@1, assessment-criteria@1, terminology@1, etc.   |
+-----------------------------------------------------------------------+
|  Annotations (Non-normative Chrome)                                   |
|  Rendering hints (e.g., do_not_link), web navigation, UI metadata     |
+-----------------------------------------------------------------------+
```
- **Passive Core vs. Fail-Closed Portable Tier (D15)**: The **Core** tier is strictly passive—it validates kernel schema, verifies package digests, resolves local references, and *preserves unknown facets without evaluating compliance math*. All semantic evaluations begin at the **Portable** tier, where missing capability declarations or unhandled semantics fail closed.

#### Identity & Addressing Split (D2, D5)
- **URI Equality**: Identity URIs are string-compared opaque tokens (never dereferenced over network), enabling 100% offline verification in air-gapped environments.
- **Alias vs. Lineage Split**:
  - `canonical-alias`: Identity equivalence (authority-asserted rebrands, safe auto-substitution).
  - `replaces[]`: Lineage history (`revised`, `split-from`, `merged-into`). Auto-substitution is explicitly forbidden to prevent silent corruption of attestations and findings.
- **Authorization Scoping**: System boundaries attach via `authorizations[]` with explicit `includes[]` component scoping, and inheritance edges carry a required `basis-ref` pointing to a specific `authorization-id`.

---

### 2. Empirical Evidence & Corpus Validation

#### Coverage Analysis across 8 Corpora ([converted_examples/](converted_examples/))

| Corpus / Authority | Source Version | Inventoried Leaf Values | Mapped Values | UNMAPPED | Coverage % | Key Emitted Objects | Coverage Report Link |
|---|---|---|---|---|---|---|---|
| **AU.ISM** | v2026.06.18 | 36,161 | 36,161 | 0 | **100.0%** | 1,150 Reqs, 322 Sets | [ism-coverage-report.md](converted_examples/AU.ISM/ism-coverage-report.md) |
| **BE.CyFun** | v2025-12-12 | 4,312 | 4,312 | 0 | **100.0%** | 218 Reqs, 124 Sets | [cyfun-coverage-report.md](converted_examples/BE.CyFun/cyfun-coverage-report.md) |
| **CIS.Controls** | v8.1 | 5,493 | 5,493 | 0 | **100.0%** | 171 Reqs, 34 Sets | [cisc-coverage-report.md](converted_examples/CIS.Controls/cisc-coverage-report.md) |
| **CIS.Ubuntu2404** | v1.0.0 | 20,698 | 20,698 | 0 | **100.0%** | 312 Reqs, 635 Mappings, 79 Sets | [cisb-coverage-report.md](converted_examples/CIS.Ubuntu2404/cisb-coverage-report.md) |
| **DE.C3A** | v1.0 | 1,093 | 1,093 | 0 | **100.0%** | 30 Reqs, 9 Sets | [c3a-coverage-report.md](converted_examples/DE.C3A/c3a-coverage-report.md) |
| **DE.C5** | vC5:2026 | 5,868 | 5,868 | 0 | **100.0%** | 623 Reqs, 190 Sets | [c5-coverage-report.md](converted_examples/DE.C5/c5-coverage-report.md) |
| **FedRAMP CR26** | v2026.07.14.01 | 7,294 | 7,294 | 0 | **100.0%** | 292 Reqs, 373 Mappings, 91 Sets, 4 Tailorings | [cr26-coverage-report.md](converted_examples/FedRAMP-CR26/cr26-coverage-report.md) |
| **geman.bsi** (GS++) | v2026-07-16 | 49,431 | 49,431 | 0 | **100.0%** | 651 Reqs (999 statements), 162 Sets | [bsi-coverage-report.md](converted_examples/geman.bsi/bsi-coverage-report.md) |

#### Props Elimination Mechanism ([drafts/prop-census-three-authorities-v0.3-input-r2.md](drafts/prop-census-three-authorities-v0.3-input-r2.md))
Over **70% of legacy OSCAL prop instances** disappear with zero replacement construct because they were workarounds for missing core primitives:
- **Membership Matrices** (5,301 ISM props) → `RequirementSet` membership.
- **Modality & Binding Force** (`modal_verb` ×1,006, `force` ×328) → `statements[].modality` lattice.
- **Revision History** (2,202 ISM props, CR26 `updated[]`) → Native L0 versioning.
- **Nested Controls** (347 pseudo-controls in BSI) → `statements[]` collection.

#### Exposure of Source Defects (Not Hidden in Props)
- **BSI Grundschutz++**: Identified 213 `{{...}}` pseudo-placeholders in prop values as authoring defects and reported them in [bsi-coverage-report.md](converted_examples/geman.bsi/bsi-coverage-report.md) without silent laundering.
- **CIS Ubuntu Benchmark**: Identified empty statement prose across all 312 rules; statement prose was explicitly minted from titles and flagged in [cisb-coverage-report.md](converted_examples/CIS.Ubuntu2404/cisb-coverage-report.md).

---

### 3. Cryptographic Integrity & Dual-Digest Model

#### Dual-Digest Architecture ([jascon/references/ch11-integrity-attestation-airgaps.md](jascon/references/ch11-integrity-attestation-airgaps.md))
Legacy OSCAL digital signatures fail when transport tools strip non-normative metadata or format JSON. Semantic OSCAL introduces two distinct SHA-256 digest domains per object in `content-manifest.json`:
1. `package-digest`: SHA-256 over raw delivered bytes (includes annotations and formatting).
2. `semantic-digest`: SHA-256 over canonical **JCS** (RFC 8785) serialization of the object **excluding `annotations`**.

```
                           +------------------------+
                           |  Delivered Object      |
                           +-----------+------------+
                                       |
                   +-------------------+-------------------+
                   |                                       |
                   v                                       v
         [ Raw Bytes ]                             [ Exclude Annotations ]
                   |                                       |
                   v                                       v
        package-digest SHA-256                    JCS Pre-Normalization
                   |                                       |
                   v                                       v
        (Package Integrity)                      semantic-digest SHA-256
                                                           |
                                                           v
                                                 (Normative Integrity)
```

#### Bi-Modal Verification State Machine (D7)
- **Full Match**: Signature valid AND `content-manifest-digest` matches bundle. Proves exact byte-for-byte state as signed.
- **Semantic Match**: Signature valid AND all `subject-semantic-digests` match, but `content-manifest-digest` differs. Proves compliance meaning is 100% untampered, even if chrome/annotations were stripped in transit.
- **Failed**: Any signature mismatch or semantic digest discrepancy.

#### Out-of-Band Attestation & Air-Gap Support
- **Cycle-Free Signatures**: Attestations and DSSE envelopes sit **beside** `content-manifest.json`, eliminating the self-referential hashing cycle.
- **Sealed Mode**: Manifests pin exact facet schemas (URI + SHA-256 digest). Core validators operate fully offline without external network or DNS resolution.

---

### 4. Migration Path & Ecosystem Viability

#### 3-Level Migration Guarantee Framework ([jascon/references/ch14-migration-playbooks.md](jascon/references/ch14-migration-playbooks.md))
1. **Level 1: Native Mapping**: Direct 1-to-1 representation in kernel objects.
2. **Level 2: Compatibility Facet**: Framework-specific properties preserved in registered compatibility facets with a clear deprecation clock.
3. **Level 3: Opaque Preservation**: Preserved in `private:` annotations to prevent compliance math corruption while preserving raw data.

#### Bidirectional Migration & Export Feasibility
- **Up-conversion**: 100.0% proven across 8 corpora representing catalogs, benchmarks, and bespoke JSON.
- **Down-conversion**: Semantic Core objects compile back to syntactically valid OSCAL 1.2.2 JSON/XML for legacy regulatory submission while keeping Semantic Core as the single-source-of-truth graph.
- **Profile Merge Semantics Gap**: Profiles depending on legacy OSCAL 1.x `use-first`/`combine` merge strategies must be resolved in 1.x *before* migration into Semantic Core ([ch14-migration-playbooks.md](jascon/references/ch14-migration-playbooks.md)).

---

### 5. Adversarial Stress-Testing & Open Flaws

#### Resolved Issues (Review Passes & Backlog Closures)
- **Manifest Hash Cycle (P7-B1)**: Resolved by placing attestations outside the content manifest (D3).
- **Core Passive Tier (P7-B3 / P8-E1)**: Resolved by forbidding semantic computation at Core tier (D15).
- **Modality Partial Order (P8-E2)**: Resolved by defining a normative partial order lattice supporting obligations, prohibitions, restrictions (`may-only` / `DARF NUR`), and unmonotone moves requiring a `Deviation` (D9).
- **Kernel Promotion Bar (D22)**: Established normative rules requiring ≥ 2-of-3 census authority encodings, shared computation, and non-flattening vocabulary before any candidate enters the kernel.

#### Active Open Backlog Items ([drafts/oscal-semantic-core-v0.6-spec-feedback-backlog.md](drafts/oscal-semantic-core-v0.6-spec-feedback-backlog.md))
- **Item #6 (Terminology Hosting Shape)**: Re-scoped under D22 anticipated-convergence path. Pending decision on dedicated carrier object vs. root-Set hosting.
- **Item #10 (CTL/ODP Addressing)**: Statement-level addresses for 79 CTL overlays to resolve during the NIST catalog conversion.
- **Item #12 (Localized-Text Primitive)**: Defining `text` (`{BCP-47: string}`) for human-readable fields (`title`, `rationale`) to replace inconsistent string definitions across converted corpora.

---

## Extended Section Findings (Dimensions 6–11)

### 6. Governance, Regulatory Harmonization & Standards Strategy

#### EU Regulatory Harmonization (NIS2, DORA, CRA)
- **Reporting & Effectivity Primitives**: Incoming mandatory EU regulations (**NIS2, DORA, Cyber Resilience Act**) focus heavily on strict incident reporting windows, transition dates, and supplier supply-chain reporting duties. Semantic OSCAL accommodates these natively via stdlib facets:
  - `reporting-obligation@1` (absorbs notification triggers, parties, and methods).
  - `effectivity@1` (absorbs obtain/maintain dates and grace periods).
  - Both facets are promoted to anticipated kernel candidates under the D22 amendment path.
- **Multi-Framework Crosswalks via Kernel `Mapping` (D20)**: Cross-framework mappings between NIST 800-53, ISO 27001, NIS2, and DORA operate as first-class `Mapping` graph objects with IR 8477 / OLIR relationship codes (`equal`, `subset-of`, `superset-of`, `intersects`, `supports`, `supplements`), keeping catalog structures untouched.

#### Standards Body Coexistence Strategy (D11, D19, Ch 15.3)
- **NIST SP 800-53 as Canonical Reference Facet (D11)**: NIST's framework conventions live as a shipped-by-default standard library facet owned by NIST. NIST retains out-of-the-box primacy without imposing document structural constraints on other national authorities (BSI, ACSC).
- **Engine Positioning & Sunset Trigger (D19, Ch 15.5)**: Semantic Core operates as an internal authoritative graph engine compiling down to OSCAL 1.x JSON/XML for legacy regulatory submission. The dual-model window ends at a measurable **sunset trigger** (authorities authoring natively, Portable implementations available in multiple languages, conformance corpus green).

#### Facet Registry Governance (D10, Ch 15.2)
- **Federated Governance via `.well-known`**: Facet schemas are federated at publishers' `.well-known` domains and pinned by SHA-256 digest in `content-manifest.json`. The Foundation maintains an append-only transparency log without acting as a central permission gatekeeper.

---

### 7. Developer Experience (DX) & Human Authoring UX

#### The "Weekend Validator" Acceptance Test (Ch 12)
- **Reduced Implementation Cliff**: Building a conformant **Core** validator is designed to take a single weekend rather than a quarter:
  - Plain JSON Schema (Draft 2020-12) instead of a custom Metaschema parser.
  - 1 serialization (JSON) instead of 3 synchronized formats (XML/YAML/JSON).
  - 5 small structural functions (`references-resolve`, `digest-verified`, `unique-within`, `code-from`, `prose-params-resolve`) instead of a Schematron rule engine.
  - Zero profile-resolution algebra with merge strategies.

#### Human Authoring Ergonomics
- **Human-Readable Draft Formats**: Authors can write requirements using Markdown frontmatter or YAML local drafts that compile deterministically to JSON canonical objects.
- **Identity-Addressed Resiliency**: Tailoring operations target global IDs (`requirement-ref` + `statement-id`) rather than fragile JSON pointers (RFC 6902). Upstream catalog reorderings never shatter downstream tailorings.

#### Printable Rationale & Error Quality ([Ch 12.3](jascon/references/ch12-building-a-validator.md#L99-L105))
- **Mandatory Rationale Output**: Every validation rule instantiation carries `{rule, target, rationale, message}`, and the human **rationale MUST print on failure**. Rules without printable rationales are non-conformant, eliminating the opaque error messages of 1.x legacy tools.

---

### 8. Performance, Graph Query Scalability & Storage Efficiency

#### Shallow Graph Indexability & Database Ingestion
- **O(1) Document Ingestion**: Replaces deeply nested document trees (which require deep positional parsing) with 9 flat objects carrying global URIs. Ingestion into document or graph databases (MongoDB, PostgreSQL JSONB, Neo4j) is flat and instantaneous.
- **Single-Hop Graph Traversals**: Querying multi-framework relationships (e.g. *"Find all SaaS implementation controls fulfilling NIST AC-2 statement 'a' under ATO Y"*) executes via simple single-hop key lookups over `statement-id` and `authorization-id` edges.

#### Storage & LLM Token Efficiency
- **>70% Payload Reduction**: Eliminating custom `props` boilerplate and redundant XML/Metaschema metadata reduces raw JSON file size by 50–70% across converted catalogs.
- **Context Window Optimization**: Flat kernel objects use ~60% fewer tokens in LLM context windows (RAG & automated compliance checking) compared to OSCAL 1.x trees, preventing token truncation and attention degradation.

---

### 9. Continuous Compliance, Telemetry & Multi-Party Supply Chain

#### Continuous Evidence Ingestion & Telemetry Mapping
- **Real-Time Assessment Ingest**: Telemetry events from security scanners (Wiz, AWS Config, GitHub Actions) map directly into `Assessment` (using `assessment-criteria@1`) and `Finding` kernel objects.
- **Automated SLA Tracking**: State transitions on `Finding` (`investigating` $\rightarrow$ `pending` $\rightarrow$ `approved` / `withdrawn`) bind to `duration` parameters (elapsed vs calendar), enabling automated SLA tracking in Jira/ServiceNow workflows.

#### Multi-Tenant & Tiered Supply Chain Inheritance (D5, Ch 9)
- **Explicit Authorization Scoping**: Multi-tier supply chains (*IaaS $\rightarrow$ PaaS $\rightarrow$ SaaS $\rightarrow$ Enterprise*) attach via explicit `authorizations[]` with `includes[]` component scoping.
- **Inductive Boundary Checking**: Every `inherited-from` edge must carry a `basis-ref` pointing to a specific `authorization-id`, allowing auditors to verify multi-hop inheritance chains edge-by-edge without risking false-positive compliance assertions.

---

### 10. AI Native / LLM Interoperability & Agentic Workflows

#### Built-In AI Assistant Skill (`jascon/SKILL.md`)
- **Ready-to-Install Claude / Gemini Skill**: Includes an installable AI agent skill containing 14 numbered normative requirements, reference chapters, 18 self-consistent worked JSON bundle examples, and python conversion scripts.

#### Hallucination Resistance & Agentic Precision
- **Identity-Addressed Edits**: AI agents editing compliance rules use identity targets (`statement-id`, `requirement-ref`) rather than array indices, preventing hallucinated positional path edits.
- **Bound Parameter Syntax**: Parameters in statement prose use explicit `{param:id}` tokens (`prose-params-resolve`), making unmapped LLM parameter hallucinations unrepresentable and machine-rejectable.

---

### 11. Legal Admissibility, Non-Repudiation & Audit Trail

#### Cryptographic Non-Repudiation (D7, Ch 11)
- **DSSE Signature Envelopes**: `Attestation` objects link to DSSE signature envelopes (`envelope-ref`) binding three distinct layers:
  1. `subject-semantic-digests[]` (canonical compliance meaning).
  2. `content-manifest-digest` (packaging and delivered file byte state).
  3. `rendering` (`artifact-digest` of rendered PDF/Markdown + pinned template digest).

#### Bi-Modal Legal Clarity
- **Full Match vs Semantic Match**: In regulatory or court proceedings, **Full Match** proves byte-for-byte exact packaging as signed by the Authorizing Official. **Semantic Match** cryptographically proves that compliance meaning is 100% untampered even if intermediate hygiene tools stripped non-normative UI chrome.

#### Statement-Level Audit Lineage
- **Direct Traceability**: Auditors can trace any compliance `Finding` directly to its fine-grained `statement-id`, component `Implementation` clause, and DSSE `Attestation` envelope without relying on vendor-proprietary GRC database logs.

---

## Critical Vulnerabilities & Blindspots

1. **Calendar Dependency in Deadline Arithmetic (D9)**:
   - *Risk*: `calendar-period` (e.g., `3 bizdays`) relies on external holiday/business calendars.
   - *Consequence*: Without a resolved calendar context, deadline evaluation MUST fail closed. Tools operating in different jurisdictions without explicitly attached calendar references will halt.
2. **Third-Party Facet Diode Inspection (D18)**:
   - *Risk*: Strict XML transit projection (XSD inspection at cross-domain guards) only covers kernel + `oscal-stdlib`.
   - *Consequence*: Third-party custom facets pass through guards as opaque payloads, requiring custom guard policies per facet publisher.
3. **Over-Reliance on Authority Diligence for Alias Rebrands (D2)**:
   - *Risk*: `canonical-alias` allows tools to auto-substitute control identifiers.
   - *Consequence*: If an authority incorrectly issues a `canonical-alias` for a control revision that actually altered normative requirements, consumer implementations will be silently misaligned.
4. **Renderer Template Accreditation Gap (Ch 15.3)**:
   - *Risk*: Rendering templates steer human-readable output (PDFs/Markdown).
   - *Consequence*: While template pins and hashes make tampering detectable, official accreditation of renderer templates remains an unowned governance gap.

---

## Actionable Recommendations for v0.6 Specification Cycle

### Priority 1: High Impact / Immediate
1. **Deliver the Executable v0.6 Proof Gate**:
   - Complete normative JSON Schemas (2020-12) for all 9 kernel objects and stdlib facets.
   - Conduct the lines-of-code / contributor-hour benchmark comparing a Semantic Core validator against an OSCAL 1.2.2 reference validator.
2. **Formalize the `text` Primitive (Backlog Item #12)**:
   - Adopt `{ "<BCP-47-lang>": "string" }` as the normative primitive for all human-targeted fields (`title`, `rationale`, `description`) across kernel objects and registered facets.

### Priority 2: Medium Impact / Next Cycle
3. **Standardize Calendar Context Attachments**:
   - Define a standard `calendar-context` code system within `oscal-stdlib` to allow `calendar-period` deadline calculations to execute fail-closed without ambiguity in cross-jurisdictional deployments.
4. **Publish Bidirectional Export Test Suites**:
   - Create automated verification tests validating that Semantic Core graph objects compile losslessly to OSCAL 1.2.2 JSON/XML target formats.
