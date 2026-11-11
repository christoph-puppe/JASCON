# Gate 4 — The Measurement Report
### The weekend-validator acceptance test + the bidirectional export suite · 2026-07-22

Spec IV.5.4 asks for numbers, not narrative: a measured complexity
comparison against an OSCAL 1.2.2 validator + resolver (two languages,
LoC, contributor-hours), and a mechanically verified round-trip to
OSCAL 1.2.2. This file is those numbers. Every count is reproducible
from this repository; the counter is stated with each table.

> **Dated measurement (P10 #33).** All figures below are as measured at
> the gate-4 commit (`9b953fd`). The P10 fix pass then grew the suite
> (157 vectors; validators 994/1,163 non-blank non-comment lines) and
> repaired the ISM taxonomy (the `geman.bsi` directory is now `DE.BSI`;
> ISM round-trips 1,711/1,711 with stray-controls 0; corpus total
> 5,886/5,886) — §5 re-measures at HEAD.

## 1. Implementation sizes

One counter for every row: total lines and non-blank non-comment lines
(`#`-only lines excluded), tests/docs/`__pycache__` excluded.

| Implementation | Language | Files | Lines | Non-blank non-comment | Runtime dependencies |
|---|---|---:|---:|---:|---|
| `validate_core.py` — the full reference: 12 vector families, both digests, shape-disjoint inference, closure, facet fail-closed, tier derivation, op-law, **Ed25519/DSSE**, D3.5 composition, B.1.8 conditional-apply | Python 3 | 1 | 1,061 | **938** | `jsonschema` |
| `validate_core.ps1` — the same coverage, second language | PowerShell 5.1 | 1 | 1,156 | **1,110** | **none** (stock Windows) |
| `export_oscal.py` — bidirectional export + generic import + round-trip | Python 3 | 1 | 315 | 280 | `jsonschema`, `regex`* |
| **compliance-trestle 4.2.0** — the OSCAL 1.x validator + resolver toolchain (PyPI sdist, `tests/` and `docs/` excluded) | Python 3 | **162** | 41,295 | **30,905** | pydantic + tree |

\* `regex` is needed solely because **NIST's own official JSON schema**
for OSCAL 1.2.2 uses `\p{L}` Unicode property escapes that Python's
stdlib `re` cannot compile — an ecosystem-cost data point in itself:
the reference schema of the incumbent format is not consumable by the
standard library of the language most compliance tooling is written in.

**Reading.** The complete JASCON reference validator — including
a dependency-free Ed25519, a composition engine, and a conditional
engine — is **~30× smaller** than the incumbent toolchain, and the
zero-dependency PowerShell twin runs on the stock Windows box every
auditor already has. Scope note, honestly: trestle also ships
authoring/CLI machinery beyond validate+resolve; no smaller published
subset implements OSCAL validation + profile resolution, so the
toolchain is the honest comparison unit — it is what a consumer must
actually install.

## 2. Conformance parity (the second implementation)

| Suite | Python | PowerShell |
|---|---:|---:|
| jcs 8 · modality 21 · parameter 17 · tailoring 15 · attestation 5 · facet 7 · reference 11 · lifecycle 36 · tier 9 · dsse 5 · composition 7 · conditional 8 | **149/149** | **149/149** |
| Vector wall-clock | ~1 s | 5.8 s |
| Full corpus (11 bundles, 6,675 objects, both digests re-verified per object) | ~50 s | 759 s (12.7 min) |

The PowerShell twin pays ~15× in wall-clock for its zero-install
property — an overnight-coffee number for an audit verification run,
and the stock-Windows story is the point: the machine every German
auditor already has can re-verify the entire corpus, both digests per
object, without installing anything.

Divergences during authoring: exactly **one** — the PowerShell port
initially skipped the `ok()` on the field-free disjointness check
(35/36 lifecycle), visible immediately as a count difference and fixed
in minutes. Everything else — canonicalization down to UTF-16 member
ordering and float formatting, digest equality across 6,675 objects,
tier derivation, op-law — matched on the first run. That is the actual
weekend-validator claim: **the specification + appendices + conformance
corpus determine the implementation**; where they didn't, the vectors
said so.

## 3. Authorship, stated plainly

Both implementations are by the project author with AI assistance, from
the same normative sources (specification, appendices A–C, the vector
corpus as oracle), in one working session (2026-07-22). The
independence of the second implementation is therefore limited to
**language and runtime** — PowerShell 5.1 shares no JSON library, no
schema validator, no crypto library, and no line of code with the
Python reference. What this measures: spec sufficiency and
implementation burden. What it does not measure: a stranger's weekend.
A third-party clean-room build against `jascon/conformance/`
is the standing invitation, and the corpus is the referee.

## 4. The bidirectional export suite (down-conversion measured)

`export_oscal.py` per catalog bundle: project → validate against the
**official NIST v1.2.2 release schema** (`oscal_catalog_schema.json`)
→ re-import with a generic importer (no corpus knowledge) → compare
every object by **semantic digest**.

| Corpus | Schema-valid | Round-trip (objects digest-equal) |
|---|---|---:|
| AU.ISM | yes | 1,472/1,472 |
| BE.CyFun | yes | 342/342 |
| CIS.Controls | yes | 205/205 |
| CIS.Ubuntu2404 | yes | 391/391 (635 Mappings out of catalog scope) |
| DE.C3A | yes | 39/39 |
| DE.C5 | yes | 813/813 |
| FedRAMP-CR26 | yes | 398/398 (373 Mappings, 5 Tailorings out of scope) |
| US.CSF | yes | 135/135 |
| US.SP800-53 | yes | 1,039/1,039 |
| geman.bsi | yes | 813/813 |
| **Total** | **10/10** | **5,647/5,647 (100 %)** |

The projection is real OSCAL where OSCAL has the construct
(statements→parts, `{param:}`↔`{{ insert: param }}`, typed
params→params+select, relations→links, the root-Set tree→groups) and a
namespaced props channel (`https://ns.jascon.org/core`) for
what it cannot say — the D16 compatibility mechanism, in reverse.

**D16 asymmetries measured on the way (all counted in the exports):**

1. OSCAL 1.2.2 groups may carry subgroups OR controls, never both (the
   `anyOf` is exclusive) — kernel Sets mix freely; 1 synthetic wrapper
   emitted. This limitation is plausibly why the CIS benchmark's own
   OSCAL rendition contorts sections into controls-in-controls.
2. OSCAL params require `label|select|values`; kernel declarations do
   not — 154 synthetic labels (marker-prop'd, stripped on import).
3. 3 empty groups dropped (Sets whose members live outside the catalog
   model: mappings, tailored externals).
4. Overlapping Set membership (baselines!) has no catalog-model
   representation at all — Sets ride the props channel in full.

Declared scope: the catalog graph (Requirements + Sets = 5,647 of 6,675
objects). Mappings/Tailorings await OSCAL mapping/profile-model
exports; the IFA lifecycle bundle awaits SSP-family exports. Skips are
counted in every report, never silent.

## 5. Reproduce

```
uv run --with jsonschema python jascon/scripts/validate_core.py
uv run --with jsonschema --with regex python jascon/scripts/export_oscal.py
powershell -ExecutionPolicy Bypass -File jascon/scripts/validate_core.ps1
```
