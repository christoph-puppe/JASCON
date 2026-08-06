# JASCON — Example Bundle (one file per type)
### Companion to Specification v0.5 and the Handbook · illustrative, 2026-07-18

This bundle contains **one worked example file for every JASCON
type**, wired together as a single, closed, cross-referentially
consistent package — the same running story the Handbook tells
(KONF.14.1, the Acme SaaS on a PaaS, finding 017).

## Coverage: the nine types + sub-objects + bundle artifacts

| # | Type | File | Demonstrates |
|---|---|---|---|
| 1 | Requirement | `req-konf-14-1.json` | multi-statement clause split (s1 provider / s2 customer), choice parameter + bound `{param:}` token, aliases, framework facet, annotations |
| 1b | Requirement (pure kernel) | `req-ism-1234.json` | the zero-facet minimum |
| 1c | Requirement (deadline) | `req-iec-cso-iir.json` | `calendar-period` parameter with `tightening: lower`, relations, annotations |
| 2 | RequirementSet | `set-crypto.json`, `set-baseline.json` | nesting (set-in-set), `sequence`, **multi-authority membership** (safe under global identity) |
| 3 | Tailoring | `tailoring-elevated.json` | set selection; identity-addressed ops: monotone `set-modality` (KANN→MUSS, no Deviation needed) and in-bounds `set-parameter` |
| 4 | Mapping | `mapping-konf-ism.json` | third-party crosswalk with statement scope, honest `supports`, provenance |
| 5 | Component | `component-paas.json`, `component-acme-saas.json` | identified `authorizations[]`; members + capabilities |
| 6 | Implementation | `implementation-acme-konf.json` | per-clause `statement-refs`, shared responsibility, capability + `inherited-from` with **basis-ref → authorization id** |
| 7 | Assessment | `assessment-2026q3.json` | facet-typed method (stdlib stub), subjects, result |
| 8 | Finding | `finding-017.json` | statement-scoped finding, calendar-aware action, **Deviation sub-object** (false-positive, approved) |
| 9 | Attestation | `attestation-acme-2026.json` | subject **semantic** digests, content-manifest binding, rendering block — *beside* the manifest, never inside |
| — | Content manifest | `content-manifest.json` | both digests per object, exact-pinned facet schemas, rendering digest |
| — | Facet descriptors | `gspp-taxonomy-1.0.0.json`, `assessment-criteria-1.0.0-stub.json` | custom facet descriptors and stubs |
| — | Rendering (L4) | `authorization-summary.md` | the "document as view", digest-bound by the attestation |

## Self-consistency properties (deliberate)

- **Closed object references.** Every object-to-object `ref` resolves
  inside this bundle via the manifest — sealed-mode friendly.
- **Real digests.** All `package-digest` values are true SHA-256 over
  the file bytes as shipped. All `semantic-digest` values are SHA-256
  over the canonicalized object **minus `annotations`**.
  Canonicalization note: computed with a JCS-compatible serialization
  (sorted keys, minimal separators, UTF-8, no escaping of non-ASCII)
  — exact for this content, which contains **no floating-point
  numbers and only ASCII keys**; a full RFC 8785 implementation is a
  v0.6-gate deliverable. Empty-omission is satisfied by construction:
  no empty optional arrays/objects were authored.
- **The digests teach.** `req-konf-14-1` and `req-iec-cso-iir` carry
  annotations, so their package- and semantic-digests differ —
  strip the annotations, and the semantic digest still matches
  (Chapter 11's Semantic Match, reproducible by hand).
- **The boundary rule is satisfied.** The implementation's
  `inherited-from` names the PaaS's specific authorization id;
  delete `basis-ref` to reproduce the Chapter 9 fail-closed case.
- **The tailoring is deviation-free on purpose.** Both operations are
  lawful without a Deviation (monotone modality move; in-choice-set
  parameter). Change `set-modality` to `may` against a `must` source,
  or `value` to `"md5"`, to produce the Chapter 6 violations.

## Illustrative caveats (read before reuse)

1. **Namespaces mirror the Handbook's worked examples** (BSI, ACSC,
   FedRAMP, example.org hosts). They are *illustrative*, not official
   publications of those authorities.
2. **ISM-1234's prose is invented** for the example; the real ISM
   control text is not reproduced here.
3. **Party / authority / performer identifiers are used as codes**
   (spec: code-or-ref) — no party objects are bundled.
4. **The calendar is deliberately not bundled.** `calendar-period`
   values are *representable* here but not *computable* — a conformant
   tool asked to do date arithmetic must fail closed (Handbook §10.4).
   This is pedagogy, not an omission.
5. **`assessment-criteria` schema is a stub**; the normative stdlib
   schema ships with the v0.6 gate.
6. **The attestation's `template-ref.digest` is a marked placeholder**
   and the DSSE **envelope is out of scope** of these examples
   (`envelope-ref` points at a path not included) — envelope bytes are
   defined by the stdlib DSSE profile, not by example files.
7. One rendering stands in for real deliverables; real bundles list
   as many as they ship.

## Suggested uses

Feed single files to cross-model reviewers; hand the whole bundle to a
prototype validator (Handbook Ch. 12's milestones map 1:1 onto what is
checkable here); break it on purpose using the recipes above to watch
fail-closed behave.
