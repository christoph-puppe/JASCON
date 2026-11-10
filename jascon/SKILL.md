---
name: jascon
description: Guidelines and requirements for authoring, validating, and migrating to JASCON (JSON Attestable Semantic Compliance Object-graph Notation, formerly "Semantic OSCAL" / "OSCAL Semantic Core").
---

# JASCON Skill Requirements

When triggered, this skill guides the agent in applying the JASCON standard correctly. The chapters of the JASCON Handbook serve as the normative requirements for this skill.

## Core Directives (Chapters as Requirements)

You must strictly adhere to the guidelines detailed in the handbook chapters and companion examples linked below:

### Requirement 1: Paradigm Alignment & Motivation
- **Description:** Align all compliance data into a graph of ten shallow, globally identified objects (Requirement, RequirementSet, Tailoring, Mapping, Component, Implementation, Assessment, Finding, Attestation, Risk) and 2 sub-objects (Deviation, Authorization). Ensure strict separation of concerns between kernel semantics, registered facets, and rendering annotations.
- **Reference Document:** [Chapter 1 — Why This Exists](references/ch01-why-this-exists.md) and [Chapter 2 — The Core in One Hour](references/ch02-the-core-in-one-hour.md)
- **Companion Example:** [req-ism-1234.json](examples/req-ism-1234.json) (Zero-facet minimum requirement)

### Requirement 2: Identity, Versioning, and Lifecycle Management
- **Description:** Govern namespaces strictly. Use canonical-alias vs. replaces rules correctly to ensure revision and rebranding integrity. Every reference to an object must use its unique identifier.
- **Reference Document:** [Chapter 3 — Identity, Versions, and Lifecycle](references/ch03-identity-versions-lifecycle.md)

### Requirement 3: Writing Requirements, Statements, and Parameters
- **Description:** Requirement clauses must have statement-level granularity to allow precise tailoring, mappings, and responsibility assignment. Adhere strictly to the modality lattice (obligations vs. permissions). Deadlines must be structured using explicit, typed parameters or duration systems instead of free-text placeholders.
- **Reference Document:** [Chapter 4 — Writing Requirements: Statements, Modality, Parameters](references/ch04-writing-requirements.md)
- **Companion Examples:** [req-konf-14-1.json](examples/req-konf-14-1.json) (Multi-statement split, choice parameter), [req-iec-cso-iir.json](examples/req-iec-cso-iir.json) (Calendar period with tightening rule)

### Requirement 4: Sets, Hierarchy, and Baselines
- **Description:** Use nested `RequirementSets` as the singular taxonomy mechanism. Define baselines using membership sets rather than inline properties.
- **Reference Document:** [Chapter 5 — Sets, Hierarchy, and Baselines](references/ch05-sets-hierarchy-baselines.md)
- **Companion Examples:** [set-crypto.json](examples/set-crypto.json) (Nested sets), [set-baseline.json](examples/set-baseline.json) (Baseline membership set)

### Requirement 5: Tailoring JASCON
- **Description:** Define changes via selection rules and identity-addressed operations. Apply per-operation weakening rules and require a `Deviation` object where needed — Deviation duties bind consumer-tier Tailorings only; a Tailoring published at Authority tier is normative source and never carries one (weakening classification still computes). Follow the deterministic tailoring resolution algorithm. To amend a catalog you do not own, use the supplement pattern (§6.A): author under your own prefix as a shadow set with interleaved sequence — modifying is Tailoring, adding is authorship.
- **Reference Document:** [Chapter 6 — Tailoring Without Tears](references/ch06-tailoring-without-tears.md); resolution logic also in Chapter 12 and Appendix B.
- **Companion Example:** [tailoring-elevated.json](examples/tailoring-elevated.json) (Monotone tailoring operations)

### Requirement 6: Facet Extensions
- **Description:** Extend the kernel only via registered, schema-pinned facets (`modifies-semantics`, fail-closed rules) or annotations (purely styling/chrome). Never add custom top-level fields to kernel objects.
- **Reference Document:** [Chapter 7 — Facets: Extending Without Fracturing](references/ch07-facets-extending-without-fracturing.md)
- **Companion Examples:** [gspp-taxonomy-1.0.0.json](examples/gspp-taxonomy-1.0.0.json) (Custom facet schema), [assessment-criteria-1.0.0-stub.json](examples/assessment-criteria-1.0.0-stub.json) (Descriptor stub)

### Requirement 7: Mappings and Crosswalks
- **Description:** Map relationships using `Mapping` objects with IR 8477/OLIR relationship semantics plus the stdlib extension code `supplements` (supplement-pattern attachment; non-chaining). Always map at the statement-level scope for high precision.
- **Reference Document:** [Chapter 8 — Mappings and Crosswalks](references/ch08-mappings-and-crosswalks.md)
- **Companion Example:** [mapping-konf-ism.json](examples/mapping-konf-ism.json) (Third-party statement mapping)

### Requirement 8: Systems, Components, and Inheritance
- **Description:** Structure system components, composition boundaries, and responsibility matrices. Implement CRM inheritance and the edge-local boundary rule for multi-tenant chains.
- **Reference Document:** [Chapter 9 — Systems, Components, and Inheritance](references/ch09-systems-components-inheritance.md)
- **Companion Examples:** [component-paas.json](examples/component-paas.json), [component-acme-saas.json](examples/component-acme-saas.json) (Platform/SaaS components), [implementation-acme-konf.json](examples/implementation-acme-konf.json) (CRM implementation referencing upstream authorizations)

### Requirement 9: Assessment, Findings, and Deviations
- **Description:** Define assessment methods, track finding statuses and action deadlines, and manage the lifecycle of deviations as an audited weakening channel.
- **Reference Document:** [Chapter 10 — Assessment, Findings, Deviations](references/ch10-assessment-findings-deviations.md)
- **Companion Examples:** [assessment-2026q3.json](examples/assessment-2026q3.json) (Assessment result), [finding-017.json](examples/finding-017.json) (Finding with Deviation sub-object)

### Requirement 9a: Risk and the Statement of Applicability
- **Description:** Model the ex-ante risk record as a `Risk` object (kernel 2.0.0, CP-RISK-1): `scenario`, `owner-ref`, `state`, `rating` as a level on a named scale, `treatment` (modify · retain · avoid · share) and `treatments[]` naming the requirements — to the statement — that carry the decision. Risk acceptance is the `acceptance` sub-record, never a Deviation; a `risk-adjustment` Deviation references the Risk it accepts (RISK-9). Findings point back with `risk-refs`. Compute the Statement of Applicability with the `risk-coverage` primitive (B.1.9): which selected requirements are justified by a Risk, which are not. A Risk justifies only once it is published (not `draft`), `assessed` or `treated`, and carries a `treatment` option — until then it is reported as pending; a `retired` or `withdrawn` Risk justifies nothing and is reported as lapsed. Scope a Risk to its Statement of Applicability with `tailoring-refs` whenever a bundle holds more than one Tailoring (RISK-14). Risk edges are typed (RISK-12): `treatments[].requirement-ref` names a Requirement, `component-refs` name Components, `tailoring-refs` name Tailorings, and a `risk-refs` entry that resolves in-bundle names a Risk. `residual-rating` presupposes `rating` on the same scale (RISK-13); `acceptance.date` is `YYYY-MM-DD`. In a Tailoring, `selects[].set-ref` names a RequirementSet and `excludes[].ref` a Requirement or a Set. Scoring methodologies stay in facets (Appendix F Q14). When converting OSCAL risks, never invent what the source lacks: OSCAL carries no risk owner, no single level and no acceptance date — derive the owner from the SSP and declare it, keep the state at `identified` — such a Risk is pending and justifies nothing until a level and an option are recorded natively —, leave `retain` unwritten (Chapter 14).
- **Reference Document:** [Chapter 10 §10.6](references/ch10-assessment-findings-deviations.md), [Appendix A.9b](references/appendix-a-shapes.md), [CP-RISK-1](../drafts/CP-RISK-1.md) (in the repository; not part of the skill bundle)
- **Companion Examples:** [risk-acme-kms-key-rotation.json](examples/risk-acme-kms-key-rotation.json) (treated Risk treating KONF.14.1 s2), [risk-vectors.json](conformance/risk-vectors.json)

### Requirement 10: Integrity, Attestation, and Air-Gaps
- **Description:** Apply both package digests (for byte transport) and semantic digests (for meaning preservation). Follow the DSSE profile checklist and attestation structures for air-gapped security assurance.
- **Reference Document:** [Chapter 11 — Integrity, Attestation, and Air-Gaps](references/ch11-integrity-attestation-airgaps.md)
- **Companion Examples:** [attestation-acme-2026.json](examples/attestation-acme-2026.json) (Attestation signatures), [content-manifest.json](examples/content-manifest.json) (Package integrity manifest), [authorization-summary.md](examples/authorization-summary.md) (L4 rendering report)

### Requirement 11: Validator Implementation
- **Description:** Ensure structural validation, facet schema checking, and resolution conformance. Adhere to JCS (JSON Canonicalization Schema) and tailoring resolution logic. The normative kernel schema, stdlib facet descriptors, and conformance vectors ship with this skill and are the definitive contract.
- **Reference Document:** [Chapter 12 — Building a Validator (The Weekend Chapter)](references/ch12-building-a-validator.md)
- **Normative Artifacts:** [oscal-semantic-core-2.0.0.schema.json](schemas/oscal-semantic-core-2.0.0.schema.json) (kernel shapes, closed; shape-disjoint type inference). The schema filename, its `$id` (`https://ns.oscal.org/semantic-core/schema/2.0.0`), the D16 compatibility namespace `https://ns.oscal-semantic.org/core`, and the attestation media type `application/vnd.oscal-semantic-core.attestation+json` deliberately keep the working-title spelling: identifiers are opaque (D2), and re-spelling them would churn every digest and signature for zero semantic gain. Also normative: [schemas/stdlib/](schemas/stdlib/) (six facet descriptors with declared semantics), [conformance/](conformance/) (223 vectors in 13 families — JCS, modality lattice, parameters, tailoring, attestation, facets, references, lifecycle, tiers, DSSE, composition, conditional-apply, risk). In `risk-vectors.json`, `expected-rule` is the portable assertion (every implementation names the violated rule id); `expected-frag` is advisory.
- **Reference Implementation:** [validate_core.py](scripts/validate_core.py) — runs the conformance corpus and validates any bundle (schemas, digests, by-statement keys, `{param:}` bindings, manifest completeness).

### Requirement 12: Safe Consumption
- **Description:** Handle unknown facets and annotations with standard fail-closed / warnings. Manage rendering, templates, and actionable error UX gracefully.
- **Reference Document:** [Chapter 13 — Consuming Content Safely](references/ch13-consuming-content-safely.md)

### Requirement 13: Migration Playbooks
- **Description:** Translate OSCAL 1.x structures (catalogs, profiles, SSPs, etc.) or legacy formats to JASCON objects preserving semantic equivalence.
- **Reference Document:** [Chapter 14 — Migration Playbooks](references/ch14-migration-playbooks.md)
- **Migration Scripts:**
  - [convert_ism.py](scripts/convert_ism.py) — ISM (OSCAL 1.1.x catalog) to JASCON bundle converter.
  - [convert_bsi.py](scripts/convert_bsi.py) — BSI Grundschutz++ + MS-TLS (OSCAL 1.1.3) to JASCON bundle converter.
  - [convert_cr26.py](scripts/convert_cr26.py) — FedRAMP CR26 (bespoke JSON) to JASCON bundle converter.

### Requirement 14: Governance and Ecosystem
- **Description:** Adhere to conformance tiers, deprecation policies, registry usage, and the anti-#2118 change proposal workflow.
- **Reference Document:** [Chapter 15 — Governance, Conformance, and the Ecosystem](references/ch15-governance-conformance-ecosystem.md)

## Appendices Reference

- [Appendix A: Shapes reference](references/appendix-a-shapes.md) — The ten types + sub-objects, field by field.
- [Appendix B: Primitives, operations, predicates](references/appendix-b-primitives-ops-predicates.md) — One page each, with rationale and failure messages.
- [Appendix C: Code systems](references/appendix-c-code-systems.md) — Modality (with the lattice diagram), lifecycle, deviation states, responsibility, mapping relationships, duration units, confidence.
- [Appendix D: stdlib facet catalog](references/appendix-d-stdlib-catalog.md) — The eight standard facets with schemas, examples, and candidates.
- [Appendix E: Worked corpora](references/appendix-e-worked-corpora.md) — KONF.14.1, IEC-CSO-IIR + class tailoring, ISM control, SCF mapping.
- [Appendix F: Objections and answers](references/appendix-f-objections.md) — Adversarial FAQ (why not CEL / XML / JSON Patch, etc.).
- [Appendix G: Glossary](references/appendix-g-glossary.md).

## Worked Examples Reference

The [examples/](examples/) directory contains a complete, self-consistent bundle of illustrative JASCON files:

- **Index/Overview:** [examples/README_1.md](examples/README_1.md)
- **Requirement:**
  - [req-konf-14-1.json](examples/req-konf-14-1.json) — Multi-statement clause split, choice parameter, annotations.
  - [req-ism-1234.json](examples/req-ism-1234.json) — Zero-facet minimum kernel requirement.
  - [req-iec-cso-iir.json](examples/req-iec-cso-iir.json) — Requirement with calendar-period and tightening rule.
- **RequirementSet:**
  - [set-crypto.json](examples/set-crypto.json) — Nested requirement sets.
  - [set-baseline.json](examples/set-baseline.json) — Baseline membership set.
- **Tailoring:**
  - [tailoring-elevated.json](examples/tailoring-elevated.json) — Monotone modality shifts and parameter settings.
- **Mapping:**
  - [mapping-konf-ism.json](examples/mapping-konf-ism.json) — Third-party statement-level mapping.
- **Component:**
  - [component-paas.json](examples/component-paas.json) — Upstream platform component.
  - [component-acme-saas.json](examples/component-acme-saas.json) — Downstream SaaS component.
- **Implementation:**
  - [implementation-acme-konf.json](examples/implementation-acme-konf.json) — Implementation with CRM responsibility sharing.
- **Assessment:**
  - [assessment-2026q3.json](examples/assessment-2026q3.json) — Assessment execution details.
- **Finding & Deviation:**
  - [finding-017.json](examples/finding-017.json) — Auditable finding with Deviation sub-object.
- **Attestation & Package Integrity:**
  - [attestation-acme-2026.json](examples/attestation-acme-2026.json) — Attestation with semantic digests.
  - [content-manifest.json](examples/content-manifest.json) — Package integrity manifest pinning schemas.
  - [authorization-summary.md](examples/authorization-summary.md) — L4 markdown report.
- **Descriptors & Custom Facets:**
  - [gspp-taxonomy-1.0.0.json](examples/gspp-taxonomy-1.0.0.json) — Custom facet descriptor schema.
  - [assessment-criteria-1.0.0-stub.json](examples/assessment-criteria-1.0.0-stub.json) — Extension descriptor stub.

## Migration Scripts Reference

The [scripts/](scripts/) directory contains automated scripts for migrating legacy/external compliance schemas to JASCON:

- [convert_ism.py](scripts/convert_ism.py) — Translates ISM OSCAL 1.1.x catalogs into a JASCON bundle and generates a computed coverage report.
- [convert_bsi.py](scripts/convert_bsi.py) — Converts BSI Grundschutz++ + MS-TLS OSCAL 1.1.3 content into JASCON. Handles nested pseudo-controls, splitting them into statements and mapping grammar, security objectives, assessment criteria, and taxonomy facets.
- [convert_cr26.py](scripts/convert_cr26.py) — Processes FedRAMP CR26 bespoke JSON into a JASCON bundle, converting rules and KSIs into Requirements and Mapping objects.
