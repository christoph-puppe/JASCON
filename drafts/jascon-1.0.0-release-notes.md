# JASCON v1.0.0 — first release

**JASCON** — **J**SON **A**ttestable **S**emantic **C**ompliance
**O**bject-graph **N**otation. *One notation for every standard, in
every language.*

Machine-readable compliance, rebuilt around meaning: nine shallow
object types, two digest domains, a closed operation vocabulary, and
one house rule — **every claim in the spec must survive contact with
real catalogs before it may stay**. JASCON was derived by census from
three national corpora (ACSC ISM, BSI Grundschutz++, FedRAMP CR26) and
then made to earn each mechanism against eight more.

## Measured, at this tag

- **Eleven corpora converted losslessly** (twelve source publications
  counting the 800-53B baselines separately): ISM, Grundschutz++,
  FedRAMP CR26, CyFun, CIS Controls v8.1, CIS Ubuntu 24.04, C5, C3A,
  NIST SP 800-53 Rev 5.2.0 + 800-53B, CSF 2.0, and a full
  SSP/AP/AR/POA&M lifecycle set — **251,591 source leaf values,
  UNMAPPED = 0 everywhere**, 6,914 objects with both SHA-256 digests
  re-verified per object.
- **A 157-vector conformance corpus in twelve families** —
  canonicalization (RFC 8785), modality lattice, parameter law,
  tailoring op-law, bi-modal attestation, facet fail-closed, reference
  closure incl. cycle detection, lifecycle, tier derivation,
  DSSE/Ed25519, bundle composition, conditional-apply.
- **Two reference validators, full parity**: `validate_core.py`
  (Python, jsonschema only) and `validate_core.ps1` (Windows
  PowerShell 5.1, **zero dependencies** — the stock Windows box every
  auditor already has). 994 / 1,163 non-blank non-comment lines —
  each ≈30× smaller than the incumbent OSCAL toolchain, crypto
  engines included.
- **Bidirectional OSCAL 1.2.2 export**: schema-valid against the
  official NIST release schema, generic re-import, **5,886/5,886
  catalog objects round-trip to semantic-digest equality**.
- **DSSE attestations verified end-to-end** (dependency-free Ed25519 in
  both validators; unsigned attestations cannot prove authority).

## Reviewed like it says on the tin

The consolidated text survived six adversarial passes, three external
review rounds, the P9 twin red-team runs, four evidence gates — and,
for this release, **P10 twice**: an in-repo adversarial round and an
independent external review, both adjudicated finding-by-finding on the
public record (Decision Rationale Register, "Amendments — P10 / P10b /
the P10 fix pass"). Every confirmed finding was fixed before the tag;
every refuted one is recorded so it stays refuted. The fix pass's
acyclicity rule promptly caught real corruption in our own shipped
corpus — a converter slug collision had silently merged **239 ISM
taxonomy sets** — and the re-conversion recovered them. Objections are
the point; bring more.

## What ships

| Artifact | Where |
|---|---|
| Specification 1.0.0 | `drafts/jascon-specification-1.0.0.md` |
| Decision Rationale Register (the full amendment journal) | `drafts/jascon-decision-rationale-register.md` |
| Kernel JSON Schema (closed shapes, shape-disjoint inference) | `jascon/schemas/jascon-1.0.0.schema.json` |
| Seven stdlib facet descriptors incl. the DSSE profile | `jascon/schemas/stdlib/` |
| Conformance corpus (157 vectors, 12 families) | `jascon/conformance/` |
| Both reference validators + export suite + converters | `jascon/scripts/` |
| Handbook (15 chapters) + normative appendices A–G | `jascon/references/` |
| Eleven converted corpora with computed coverage reports | `converted_examples/` |
| The reader — zero-dependency browser/workbench/verifier (v1.7.1) | `one-page-apps/jascon-reader.html` |
| Skill bundle (everything under `jascon/`, 76 entries) | `SKILL_jascon.zip` |

## Verify it yourself

```
uv run --with jsonschema python jascon/scripts/validate_core.py
uv run --with jsonschema --with regex python jascon/scripts/export_oscal.py
powershell -ExecutionPolicy Bypass -File jascon/scripts/validate_core.ps1
```

The third line needs nothing installed at all. A third-party clean-room
validator build against `jascon/conformance/` is the standing
invitation — the corpus is the referee.

## Notes

- **Machine identifiers** (namespace URIs, the attestation media type,
  schema filenames) deliberately retain the working-title string:
  identifiers are opaque (D2), and re-spelling
  them would churn every digest and signature for zero semantic gain.
  The decision is recorded in the register ("Amendments — v1.0.0").
  *(Reversed on 2026-11-11 for the media type and the schema filenames;
  register, "Amendments — 2026-11-11".)*
- JASCON is maintained in **personal capacity**. Nothing here is
  endorsed by NIST, BSI, ACSC, CCB, CIS, or FedRAMP.
