# JASCON — Example Bundle (one file per type)
### Companion to Specification v0.5 and the Handbook · illustrative, 2026-07-18

This bundle contains **one worked example file for every JASCON
type**, wired together as a single, closed, cross-referentially
consistent package — the same running story the Handbook tells
(KONF.14.1, the Acme SaaS on a PaaS, finding 017).

## Coverage: the ten types + sub-objects + bundle artifacts

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
| 7 | Assessment | `assessment-2026q3.json` | facet-typed method (stdlib `assessment-criteria@1`), subjects, result |
| 8 | Finding | `finding-017.json` | statement-scoped finding, calendar-aware action, **Deviation sub-object** (false-positive, approved) |
| 10 | Risk | `risk-acme-kms-key-rotation.json` | treated Risk on a BSI 200-3 scale, G 0.x threat refs, **treats KONF.14.1 s2** (the clause finding 017 is against — which now carries `risk-refs`), CISO acceptance of the residual, 12-month calendar review; `risk-coverage` on this bundle: 3 selected, 1 justified, 2 uncovered |
| 9 | Attestation | `attestation-acme-2026.json` | subject **semantic** digests (component, implementation, assessment), content-manifest binding, rendering block — *beside* the manifest, never inside |
| — | DSSE envelope | `attestation-envelope.dsse` | the attestation's canonical form as payload, signed (Ed25519) with the **fixture key** of the conformance corpus; named by `envelope-ref` |
| — | Content manifest | `content-manifest.json` | both digests per object, exact-pinned facet schemas, rendering digest |
| — | Facet descriptors | `gspp-taxonomy-1.0.0.json`, `assessment-criteria-1.0.0.json` | a custom facet descriptor, and a stdlib descriptor pinned **verbatim** (D26) |
| — | Rendering (L4) | `authorization-summary.md` | the "document as view", digest-bound by the attestation |

## Self-consistency properties (deliberate)

- **Closed object references.** Every object-to-object `ref` resolves
  inside this bundle via the manifest — sealed-mode friendly.
- **Real digests — and now checked.** All `package-digest` values are
  true SHA-256 over the file bytes as shipped (LF line endings, the bytes
  inside the skill zip; `.gitattributes` keeps a Windows checkout from
  re-spelling them). All `semantic-digest` values are SHA-256 over the
  canonicalized object **minus `annotations`**. `validate_core.py`
  verifies this manifest on every run. *Correction (2026-11-10):* it did
  not before, and at 1.0.0 the claim above was false for every checkout —
  8 of the 12 package digests matched CRLF bytes and 4 matched LF bytes.
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
5. **`assessment-criteria` is pinned verbatim.**
   `assessment-criteria-1.0.0.json` is a byte copy of the normative
   descriptor `schemas/stdlib/assessment-criteria-1.0.0.json`: a pin of a
   stdlib facet id is the descriptor, nothing else (D26). *Correction
   (2026-11-10):* until then this folder pinned an illustrative stub
   under the stdlib id, announced as a placeholder "until the v0.6 gate".
   The normative schema has since shipped (`schemas/stdlib/`), the stub
   stayed, and its schema differed from the descriptor. `validate_core.py jascon/examples`
   failed it; the default run did not, because the example pass checked
   only the pin's digest. Both now load pins with one function. The
   assessment's `summary` became a language map with it: the normative
   schema types `summary` as an object, the stub had typed it as a string.
6. **The attestation binds this folder; its signer is a fixture.** Its
   three `subject-semantic-digests` name the component, the
   implementation and the assessment of the Acme story and match them;
   its `content-manifest-digest` is the SHA-256 of `content-manifest.json`
   as delivered; its rendering digest is that of
   `authorization-summary.md`. `attestation-envelope.dsse` carries the
   attestation's canonical form and an Ed25519 signature. `validate_core.py`
   holds all of this on every run and fails the folder when one of them
   drifts. After an edit to a subject, the manifest or the rendering:

   ```bash
   python3 jascon/scripts/sign_example.py
   ```

   The signature is made with the **fixture key** of
   `conformance/dsse-vectors.json`, whose seed is printed there. Everybody
   can sign with it: the envelope shows the mechanism and proves nothing
   about an authorizing official. To see verification mode, hand the
   validator the fixture's public key — as input, because a key never
   comes from the bundle:

   ```bash
   python3 jascon/scripts/validate_core.py --trusted-keys jascon/conformance/dsse-fixture-trusted-keys.json jascon/examples
   ```

   Still illustrative: `template-ref.digest` is a marked placeholder.
   *Correction (2026-11-11):* until then the three subject digests and the
   manifest digest matched no object and no manifest in this folder, the
   envelope the attestation names did not exist, and no validator run said
   so — the reference validator read only what the manifest lists, and an
   attestation is by definition not listed (D3.1; backlog #46 and #55).
7. One rendering stands in for real deliverables; real bundles list
   as many as they ship.

## Suggested uses

Feed single files to cross-model reviewers; hand the whole bundle to a
prototype validator (Handbook Ch. 12's milestones map 1:1 onto what is
checkable here); break it on purpose using the recipes above to watch
fail-closed behave.
