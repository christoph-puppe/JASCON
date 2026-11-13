---
name: jascon
description: Guidelines and requirements for authoring, validating, and migrating to JASCON (JSON Attestable Semantic Compliance Object-graph Notation).
---

# JASCON Skill Requirements

When triggered, this skill guides the agent in applying the JASCON standard correctly. The chapters of the JASCON Handbook serve as the normative requirements for this skill.

## Core Directives (Chapters as Requirements)

You must strictly adhere to the guidelines detailed in the handbook chapters and companion examples linked below:

### Requirement 1: Paradigm Alignment & Motivation
- **Description:** Align all compliance data into a graph of eleven shallow, globally identified objects (Requirement, RequirementSet, Tailoring, Mapping, Component, Implementation, Assessment, Finding, Attestation, Risk, Check) and 2 sub-objects (Deviation, Authorization). Ensure strict separation of concerns between kernel semantics, registered facets, and rendering annotations.
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
- **Description:** Extend the kernel only via registered, schema-pinned facets (`modifies-semantics`, fail-closed rules) or annotations (purely styling/chrome). Never add custom top-level fields to kernel objects. A bundle that pins a stdlib facet pins the normative descriptor verbatim; a pin under a stdlib id with a different schema is a validation error (D26).
- **Reference Document:** [Chapter 7 — Facets: Extending Without Fracturing](references/ch07-facets-extending-without-fracturing.md)
- **Companion Examples:** [gspp-taxonomy-1.0.0.json](examples/gspp-taxonomy-1.0.0.json) (Custom facet schema), [assessment-criteria-1.0.0.json](examples/assessment-criteria-1.0.0.json) (Stdlib descriptor, pinned verbatim)

### Requirement 7: Mappings and Crosswalks
- **Description:** Map relationships using `Mapping` objects with IR 8477/OLIR relationship semantics plus the stdlib extension code `supplements` (supplement-pattern attachment; non-chaining). Always map at the statement-level scope for high precision.
- **Reference Document:** [Chapter 8 — Mappings and Crosswalks](references/ch08-mappings-and-crosswalks.md)
- **Companion Example:** [mapping-konf-ism.json](examples/mapping-konf-ism.json) (Third-party statement mapping)

### Requirement 8: Systems, Components, and Inheritance
- **Description:** Structure system components, composition boundaries, and responsibility matrices. Implement CRM inheritance and the edge-local boundary rule for multi-tenant chains.
- **Reference Document:** [Chapter 9 — Systems, Components, and Inheritance](references/ch09-systems-components-inheritance.md)
- **Companion Examples:** [component-paas.json](examples/component-paas.json), [component-acme-saas.json](examples/component-acme-saas.json) (Platform/SaaS components), [implementation-acme-konf.json](examples/implementation-acme-konf.json) (CRM implementation referencing upstream authorizations)

### Requirement 8a: Vendor Advice (Advice Packs) *(kernel 2.0.0, CP-ADVICE-1; accepted 2026-11-12, 2.0.0 not tagged)*
- **Description:** Model a vendor's recommendations as **capabilities on the vendor's Component** (`requirement-ref`, `statement-ids`, `description`, suggested `parameter-bindings`), never as Implementation objects: a capability is a claim, and the only statement that a requirement is met is an Implementation in the user's namespace that cites it. Name the product version the Component describes in `product-version` (one opaque string; never parse, order or compare it; `version` counts the revisions of the advice). A third party that writes about someone else's product publishes its own Component under its own origin and points at the vendor's Component with a relation of type `https://ns.jascon.net/stdlib/relation/describes`. Publish them as an **advice pack** (a bare Component file is not a pack): a bundle whose content manifest carries a `pack` header (`kind: advice`, `id`, `version`, `publisher`) and pins `kernel-version` 2.0.0, whose listed objects are Components only (ADVICE-1), all under the publisher's origin (ADVICE-2), with no facet that declares a semantics class (ADVICE-3); the vendor's Attestation and envelope sit beside the manifest. Adopt a recommendation with `capability-ref` in the form `<component-id>#<capability-id>`; the cited component must be in the bundle, declare the capability and be a member of the edge's component (ADVICE-7) - do not use `inherited-from`, which says another party performs the control. On import, keep the vendor's manifest unchanged under `packs/sha256/<hex>` (the name is the SHA-256 of its bytes; ADVICE-8..10) and never edit the vendor's objects. Import adds new ids and replaces only the ids an earlier release of the same pack brought (ADVICE-11); the same file again is a no-op. State the publisher as *claimed*, *attested, not verified* (an Attestation binds the manifest and no trusted key was used to check the signature) or *proven* (the signature verified under a trusted key), never as a bare name and never as proven without a verified signature.
- **Reference Document:** [Chapter 9, section 9.7](references/ch09-systems-components-inheritance.md); shapes in [Appendix A](references/appendix-a-shapes.md) (A.5, A.6, A.11); the specification is D25; the proposal with its counts and the author's decisions (§14) is `drafts/CP-ADVICE-1.md` in the repository. Evidence tier: designed for, one fictional file; `statement-ids` and `product-version` entered on the author's decision against the promotion test (D22).
- **Companion Examples:** the published pack [example-packs/dbvendor-server-7-advice/](example-packs/dbvendor-server-7-advice/) (manifest with pack header, one Component with three capabilities, Attestation and DSSE envelope beside the manifest); in the example bundle the result of importing it: [component-dbvendor-server-7.json](examples/component-dbvendor-server-7.json) (the vendor's object, byte for byte), `examples/packs/sha256/<hex>` (the kept manifest), [component-acme-saas.json](examples/component-acme-saas.json) (the product as a member), [implementation-acme-konf-14-1-s2.json](examples/implementation-acme-konf-14-1-s2.json) (the edge that adopts `cap-key-rotation`). Vectors: [advice-vectors.json](conformance/advice-vectors.json) (74). Dry run of an import: `validate_core.py --import-advice <set-dir> <pack-dir>`. A vendor without tooling writes and signs a pack with `one-page-apps/jascon-pack-builder.html` in the repository (offline, one file, the app's kernel rules inlined), and imports an existing OSCAL component definition there; point a human vendor there rather than hand-writing manifest digests. When converting a component definition yourself, follow the same mapping: one capability per implemented requirement, `statements[].statement-id` minus the `<control-id>_` prefix as `statement-ids` (`stmt` spelled `smt`), `set-parameters` as `parameter-bindings` under the catalogue's parameter names, and report what has no place in a pack instead of dropping it silently.

### Requirement 9: Assessment, Findings, and Deviations
- **Description:** Define assessment methods, track finding statuses and action deadlines, and manage the lifecycle of deviations as an audited weakening channel. Since kernel 2.0.0 two dates are typed: a Deviation's `opened` is `YYYY-MM-DD` (DATE-1), and the `due` of a Finding's action is one of `{type: date | datetime, value}`, `{type: elapsed-duration, num, unit}` or `{type: calendar-period, num, unit, calendar-ref}` (DATE-2). Never write free text such as "Q3" into either; convert such values when migrating a 1.0.0 bundle.
- **Reference Document:** [Chapter 10 — Assessment, Findings, Deviations](references/ch10-assessment-findings-deviations.md)
- **Companion Examples:** [assessment-2026q3.json](examples/assessment-2026q3.json) (Assessment result), [finding-017.json](examples/finding-017.json) (Finding with Deviation sub-object)

### Requirement 9a: Risk and the Statement of Applicability
- **Description:** Model the ex-ante risk record as a `Risk` object (kernel 2.0.0, CP-RISK-1): `scenario`, `owner-ref`, `state`, `rating` as a level on a named scale, `treatment` (modify · retain · avoid · share) and `treatments[]` naming the requirements — to the statement — that carry the decision. Risk acceptance is the `acceptance` sub-record, never a Deviation; a `risk-adjustment` Deviation references the Risk it accepts (RISK-9). Findings point back with `risk-refs`. Compute the Statement of Applicability with the `risk-coverage` primitive (B.1.9): which selected requirements are justified by a Risk, which are not. A control kept because a law, a regulator or a contract demands it is justified by a compliance Risk, never by a field (D23 rejects a selection-basis field): one Risk per obligation, with the article or clause named in `scenario` and its source in `relations`, the duty's owner in `owner-ref`, assessed with real levels and an option chosen, and `treatments` naming only the controls that discharge that duty — never one catch-all compliance Risk naming every uncovered row (Chapter 10 §10.6). A Risk justifies only once it is published (not `draft`), `assessed` or `treated`, and carries a `treatment` option — until then it is reported as pending; a `retired` or `withdrawn` Risk justifies nothing and is reported as lapsed. A bundle without any Tailoring has every Requirement in play. Scope a Risk to its Statement of Applicability with `tailoring-refs` whenever a bundle holds more than one Tailoring (RISK-14). Risk edges are typed (RISK-12): `treatments[].requirement-ref` names a Requirement, `component-refs` name Components, `tailoring-refs` name Tailorings, and a `risk-refs` entry that resolves in-bundle names a Risk. `rating` and `residual-rating` may carry `likelihood` and `impact`, each `{level, scale-ref}`; never compute the level from them. Scales are the organisation's: define each as a small file (`id`, `version`, `levels` lowest first, each with a `level` code and optional `label`), pin it in the manifest under `scales`, and use only levels it lists (SCALE-2). Put the likelihood-impact matrix into the definition of the level scale (`matrix`: the two scales and one cell per pair); a rating that states both inputs must then state the level of their cell, or carry `override-rationale` (SCALE-4). `residual-rating` presupposes `rating` on the same scale, and so do the likelihood and impact both sides carry (RISK-13); `acceptance.date` is `YYYY-MM-DD`. In a Tailoring, `selects[].set-ref` names a RequirementSet and `excludes[].ref` a Requirement or a Set. Scoring methodologies stay in facets (Appendix F Q14). When converting OSCAL risks, never invent what the source lacks: OSCAL carries no risk owner, no single level and no acceptance date — derive the owner from the SSP and declare it, keep the state at `identified` — such a Risk is pending and justifies nothing until a level and an option are recorded natively —, leave `retain` unwritten (Chapter 14).
- **Reference Document:** [Chapter 10 §10.6](references/ch10-assessment-findings-deviations.md), [Appendix A.9b](references/appendix-a-shapes.md), [CP-RISK-1](../drafts/CP-RISK-1.md) (in the repository; not part of the skill bundle)
- **Companion Examples:** [risk-acme-kms-key-rotation.json](examples/risk-acme-kms-key-rotation.json) (treated Risk treating KONF.14.1 s2), [risk-vectors.json](conformance/risk-vectors.json)

### Requirement 9b: Automated assessment with Checks
- **Description:** Model a machine check as a `Check` object (kernel 2.0.0, CP-CHECK-1): a typed fact contract (`observes`) and a flat conjunction over the twelve comparators (`criteria`: equals · not-equals · one-of · at-least · at-most · present · absent · includes-all · excludes-all · subset-of · matches · matches-not), bound to the requirement's parameters with `{"param": …}`. There is no OR, NOT, nesting or arithmetic; what does not fit stays a manual check. Collector code rides the Check in the stdlib facet `collector@1`, reports effective values, and decides nothing. Record runs as `Assessment.check-results` with the observation inline; the validator recomputes every verdict (CHECK-9) and holds the parameters to the Tailoring named in `tailoring-ref` (CHECK-12). A per-resource check (`each`) passes only if every applicable resource passes; every resource is evaluated, and the count and share of failing ones are reported with the verdict. Patterns are I-Regexp (RFC 9485), whole-value, never a parameter. Evidence is content-addressed in `evidence/sha256/` beside the manifest (CHECK-15). A relative evidence reference is `evidence/sha256/<hex>` and nothing else; a row names only parameters its Check reads and a `collector-id` its Check declares; a row carries an observation exactly when its evidence record carries `observation-digest`. An `integer` fact is a plain integer of magnitude at most 2^53 − 1 (NUMBER-1); declare a larger or fractional fact as `decimal`. A bundle with a Check pins `kernel-version` 2.0.0. Never execute collector code from a bundle you were asked to validate.
- **Reference Document:** [Chapter 10 §10.7](references/ch10-assessment-findings-deviations.md), [Appendix A.9c](references/appendix-a-shapes.md), [Appendix B.1.10](references/appendix-b-primitives-ops-predicates.md), [CP-CHECK-1](../drafts/CP-CHECK-1.md) (in the repository; not part of the skill bundle)
- **Companion Examples:** [check-acme-ssh-maxauthtries.json](examples/check-acme-ssh-maxauthtries.json) (`at-most` against a parameter, bash and python collectors), [check-acme-ssh-ciphers.json](examples/check-acme-ssh-ciphers.json) (`matches-not` on a list), [assessment-acme-bastion-2026-11-03.json](examples/assessment-acme-bastion-2026-11-03.json) (two rows, one failing), [finding-acme-bastion-ssh-cbc.json](examples/finding-acme-bastion-ssh-cbc.json) (`check-ref`), [check-vectors.json](conformance/check-vectors.json)

### Requirement 10: Integrity, Attestation, and Air-Gaps
- **Description:** Apply both package digests (for byte transport) and semantic digests (for meaning preservation). Follow the DSSE profile checklist and attestation structures for air-gapped security assurance.
- **Reference Document:** [Chapter 11 — Integrity, Attestation, and Air-Gaps](references/ch11-integrity-attestation-airgaps.md)
- **Companion Examples:** [attestation-acme-2026.json](examples/attestation-acme-2026.json) (Attestation signatures), [content-manifest.json](examples/content-manifest.json) (Package integrity manifest), [authorization-summary.md](examples/authorization-summary.md) (L4 rendering report)

### Requirement 11: Validator Implementation
- **Description:** Ensure structural validation, facet schema checking, and resolution conformance. Adhere to JCS (JSON Canonicalization Schema) and tailoring resolution logic. Write every JSON number as an integer in plain digits, of magnitude at most 2^53 − 1: no fraction, no exponent, no `-0` (NUMBER-1, kernel 2.0.0); `1.0` is a validation error, not the integer 1, and a validator refuses it without rewriting it. Anything else, such as a fraction, a count in nanoseconds or a 64-bit identifier, is a `decimal`, which is a string. Check the rule on the text of a file as well as on parsed values, because a parser forgets how a number was written. The normative kernel schema, stdlib facet descriptors, and conformance vectors ship with this skill and are the definitive contract.
- **Reference Document:** [Chapter 12 — Building a Validator (The Weekend Chapter)](references/ch12-building-a-validator.md)
- **Normative Artifacts:** [jascon-2.0.0.schema.json](schemas/jascon-2.0.0.schema.json) (kernel shapes, closed; shape-disjoint type inference). The schema `$id` is `https://ns.jascon.net/schema/2.0.0`, stdlib facets live under `https://ns.jascon.net/stdlib/`, the D16 compatibility namespace is `https://ns.jascon.net/core`, and the attestation media type is `application/vnd.jascon.attestation+json` (all moved on 2026-11-11, author decision; semantic digests and DSSE signatures made under the earlier identifiers do not carry over - register, "Amendments - 2026-11-11"). Also normative: [schemas/stdlib/](schemas/stdlib/) (six facet descriptors with declared semantics), [conformance/](conformance/) (568 vectors in 17 families — JCS with the number domain, modality lattice, parameters, tailoring, attestation, facets, references, lifecycle, tiers, DSSE, composition, conditional-apply, risk, kernel pin, scale definitions, check, advice). When a bundle carries a Risk or a Finding with `risk-refs`, its content manifest MUST carry `"kernel-version": "2.0.0"` (KERNEL-1); a bundle of 1.0.0 content leaves the field out and stays readable by 1.0.0 tools. In `risk-vectors.json`, `expected-rule` is the portable assertion (every implementation names the violated rule id); `expected-frag` is advisory.
- **Reference Implementation:** [validate_core.py](scripts/validate_core.py) — runs the conformance corpus and validates any bundle (schemas, digests, by-statement keys, `{param:}` bindings, manifest completeness, stdlib pins equal to their descriptors). Its default run includes the example bundle in `examples/`.

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

- [Appendix A: Shapes reference](references/appendix-a-shapes.md) — The eleven types + sub-objects, field by field.
- [Appendix B: Primitives, operations, predicates](references/appendix-b-primitives-ops-predicates.md) — One page each, with rationale and failure messages.
- [Appendix C: Code systems](references/appendix-c-code-systems.md) — Modality (with the lattice diagram), lifecycle, deviation states, responsibility, mapping relationships, duration units, confidence, and the fact types, comparators, outcomes and collector runtimes of Check.
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
- **Advice pack** *(kernel 2.0.0, CP-ADVICE-1)*:
  - [example-packs/dbvendor-server-7-advice/](example-packs/dbvendor-server-7-advice/) — The file a vendor publishes: pack header, one Component, Attestation and envelope beside the manifest.
  - [component-dbvendor-server-7.json](examples/component-dbvendor-server-7.json) — The vendor's Component in the importing set; three recommendations, one against a requirement the set does not hold.
  - [implementation-acme-konf-14-1-s2.json](examples/implementation-acme-konf-14-1-s2.json) — Adoption: the user's edge cites `<component-id>#cap-key-rotation`.
- **Assessment:**
  - [assessment-2026q3.json](examples/assessment-2026q3.json) — Assessment execution details.
- **Finding & Deviation:**
  - [finding-017.json](examples/finding-017.json) — Auditable finding with Deviation sub-object.
- **Check, runs and evidence (kernel 2.0.0):**
  - [req-acme-lnx-ssh-1.json](examples/req-acme-lnx-ssh-1.json) — Requirement with two clauses and one integer parameter.
  - [tailoring-acme-linux-prod.json](examples/tailoring-acme-linux-prod.json) — Binds the parameter the check reads.
  - [check-acme-ssh-maxauthtries.json](examples/check-acme-ssh-maxauthtries.json), [check-acme-ssh-ciphers.json](examples/check-acme-ssh-ciphers.json) — The two Checks, with collectors.
  - [assessment-acme-bastion-2026-11-03.json](examples/assessment-acme-bastion-2026-11-03.json), [assessment-acme-bastion-2026-11-10.json](examples/assessment-acme-bastion-2026-11-10.json) — Two daily runs with their observations.
  - [finding-acme-bastion-ssh-cbc.json](examples/finding-acme-bastion-ssh-cbc.json) — The finding the first run raised, closed by the second.
  - `examples/evidence/sha256/` — Seven evidence files, each named by its digest.
- **Attestation & Package Integrity:**
  - [attestation-acme-2026.json](examples/attestation-acme-2026.json) — Attestation with semantic digests.
  - [content-manifest.json](examples/content-manifest.json) — Package integrity manifest pinning schemas.
  - [authorization-summary.md](examples/authorization-summary.md) — L4 markdown report.
- **Descriptors & Custom Facets:**
  - [gspp-taxonomy-1.0.0.json](examples/gspp-taxonomy-1.0.0.json) — Custom facet descriptor schema.
  - [assessment-criteria-1.0.0.json](examples/assessment-criteria-1.0.0.json) — Stdlib descriptor, pinned verbatim (D26).

## Migration Scripts Reference

The [scripts/](scripts/) directory contains automated scripts for migrating legacy/external compliance schemas to JASCON:

- [convert_ism.py](scripts/convert_ism.py) — Translates ISM OSCAL 1.1.x catalogs into a JASCON bundle and generates a computed coverage report.
- [convert_bsi.py](scripts/convert_bsi.py) — Converts BSI Grundschutz++ + MS-TLS OSCAL 1.1.3 content into JASCON. Handles nested pseudo-controls, splitting them into statements and mapping grammar, security objectives, assessment criteria, and taxonomy facets.
- [convert_cr26.py](scripts/convert_cr26.py) — Processes FedRAMP CR26 bespoke JSON into a JASCON bundle, converting rules and KSIs into Requirements and Mapping objects.
