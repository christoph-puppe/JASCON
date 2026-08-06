# Gate 3 — Lifecycle Corpus + NIST/CSF Conversion Plan
### v0.6 gate item 3 (spec IV.5.3) · prepared 2026-07-22

> **DELIVERED 2026-07-22, same day** — every §6 criterion met: corpora
> 1–5 converted at 100 % / UNMAPPED 0 (US.SP800-53 · US.CSF ·
> US.IFA-GoodRead + the CR26 #10 drain), **zero kernel-schema changes
> forced**, #10 decided AND drained (16 ops, D10 rev 3), lifecycle
> bundle green with both digests (five types, #9 confirmed with zero
> enum additions), 125 → 129 vectors. Outcomes: census §9, spec IV.9,
> register "Amendments — gate 3". Bonus: two reference-validator
> defects exposed by the corpus and fixed (D13 rev 4 tier
> anti-laundering, D9 rev 3 multi-select lists).

**Purpose.** Gate 3 is the corpus expansion that (a) moves the NIST
coverage claims from *designed-for* to *measured*, (b) exercises the
five lifecycle types (Assessment · Finding · Implementation ·
Component · Attestation) at scale instead of via the 13 hand-authored
example objects, and (c) resolves the backlog items that were folded
into gate-3 scope: **#10** (CTL/ODP statement addressing) and **#9**
(seed code sets confirmed/extended from counted lifecycle evidence).

This plan follows the project's own method (ch14.4): **field census
first, converter second.** No converter is written before its source's
key-path inventory exists — the census *is* the converter's spec.

---

## 1. Corpora, in dependency order

| # | Corpus | Source (public domain) | Why this order | Resolves |
|---|---|---|---|---|
| 1 | **NIST SP 800-53 Rev 5 catalog** | `usnistgov/oscal-content` (OSCAL 1.x JSON catalog) | The reference catalog; makes minted `ns.nist.gov/sp800-53/...` mapping targets *real* (today they resolve to nothing — Mapping endpoints are landmark refs by #16) | census customer test; the SCF/CR26 mapping endpoints |
| 2 | **NIST SP 800-53B baselines** (Low/Moderate/High) | `usnistgov/oscal-content` (OSCAL profiles) | Baselines become Sets over corpus 1; profile→Set/Tailoring migration at real scale (ch14.2) | validates D21 nesting + D13 tailoring on NIST content |
| 3 | **CTL / ODP overlay** (the 79 CR26 entries parked L2) | already in the CR26 bundle (`oscal-1x@1` compat, D.10) | needs corpus 1's statement ids to address; decide control-level params vs. statement map | **#10** |
| 4 | **NIST CSF 2.0** | `usnistgov/oscal-content` (OSCAL 1.2.2) | Functions→Categories→Subcategories is the D21 taxonomy stress test; prose-only statements (`modality: unspecified`) at scale | confirms D21 + the narrative-framework pattern (E.3) beyond ISM |
| 5 | **A lifecycle bundle** — one representative SSP + AP/AR + POA&M (+ one 1.2.2 Mapping doc) | FedRAMP public example / `usnistgov/oscal-content` examples | The only path to exercising Assessment/Finding/Implementation/Component/Attestation **with digest verification** at scale (today: 13 example objects, shape-checked only — the standing Test-2 gap) | **#9** seed code sets (finding/assessment/deviation states); the D5 basis-ref induction on real inheritance |

## 2. Source acquisition (blocking prerequisite)

All five sources are **public domain** (NIST) or public FedRAMP
examples — none carry the publisher-rights constraint that keeps
`sources/` gitignored for BSI/ISM/CR26. Acquisition step, to run once:

- Clone/fetch `github.com/usnistgov/oscal-content` (Rev5 catalog +
  800-53B baselines + CSF 2.0 under `nist.gov/SP800-53/rev5/json/` and
  `…/csf/`), place under `sources/nist/` (gitignored like the rest).
- **Requires the user's action or explicit go-ahead** — this repo's
  agent does not download files without it. Once present, the census
  harness below runs offline.

## 3. Census-first method (per corpus, before any converter line)

Run the existing inventory harness (`oscal_conv_lib.inventory()`),
which already produces every leaf key-path + frequency:

```
uv run python -c "import json,collections,sys; \
sys.path.insert(0,'jascon/scripts'); import oscal_conv_lib as L; \
c=collections.Counter(); L.inventory(json.load(open('sources/nist/…rev5-catalog.json',encoding='utf-8')),'', c); \
[print(f'{n:6d}  {p}') for p,n in c.most_common()]"
```

Adjudicate each key-path against the convergence-table pattern rows
(membership? modality? aliases? history? deadlines? params?) — the
same five-question map ch7/ch14 use. **Only then** write
`scripts/convert_nist.py` as a thin corpus adapter over
`oscal_conv_lib` (`walk_controls` already handles OSCAL catalog
group/control/part nesting at any depth), emitting the three mandatory
artifacts: bundle · coverage report (UNMAPPED = 0 gate) · per-element
level declarations.

## 4. The load-bearing decisions gate 3 must record

1. **#10 — CTL/ODP addressing.** Once corpus 1 gives statement ids for
   800-53 controls, decide: model ODP assignments as **control-level
   typed parameters** (kernel `parameters[]` with `set-parameter`
   Tailorings — now bounds-enforced, backlog #25) **or** a
   statement-scoped **Mapping**. The 79 parked entries drain from L2
   either way. *Recommendation to test first:* control-level parameters,
   because ODP is parameter-shaped (a value bound per baseline) and the
   Set+Tailoring machinery already absorbs it — reserve Mapping for
   genuine cross-catalog overlays.
2. **#9 — seed code sets.** Confirm or extend the Finding
   (`open · in-remediation · closed`) and Assessment-result
   (`satisfied · not-satisfied · inconclusive`) seeds against the
   lifecycle corpus's actual states; any addition ships the Ch.15 way
   (counts + register entry), never by guess.
3. **Mapping targets become closure-required where in-bundle.** Once
   800-53 requirements are in a bundle, the CR26/SCF mappings that point
   at them cross from *landmark* to *closure-required* (#16 taxonomy) —
   re-run `closure_errors` over the combined bundle and expect the
   scope checks to newly bite (a good thing: they now *can* verify).

## 5. Risks / watch-items (pre-registered)

- **Enhancements structure.** 800-53 control enhancements are the
  nested-control case (ch14.2): they convert to `statements[]` or child
  Requirements by the split heuristic (ch4.1) — census will show which.
- **ODP `{{insertion}}` syntax** must convert to bound `{param:}`
  tokens (`prose-params-resolve`), never pass through — the 216 lesson
  applied to NIST.
- **Baseline count explosion.** 800-53B is three baselines over ~1000
  controls; Sets stay cheap (references, not copies), but the coverage
  report must show membership-as-Sets, not inlined markers (the ISM
  5,301 corpse).
- **Lifecycle digest verification.** The lifecycle bundle is the first
  time Assessment/Finding/etc. get *both digests* re-verified in a
  manifest — expect to shake out shape issues the 13 shape-only
  examples never exercised (e.g., Finding `actions[].due` typed
  `object`, schema:311 — a bare date string is currently schema-invalid
  though spec-legal; fix rides this corpus).

## 6. Definition of done (gate 3)

- ≥ corpora 1–3 converted at 100 % declared coverage, UNMAPPED = 0,
  L1/L2/L3 split reported; **zero kernel-schema changes forced** (the
  real customer test — a schema change here is a finding, not a fix).
- #10 decided and recorded in the register; the 79 CTL entries drained
  from L2.
- One lifecycle bundle validates green with both digests per object;
  the five lifecycle types exercised at scale; #9 seeds confirmed.
- `validate_core.py` green across the expanded corpus; new negative
  vectors for anything the conversion newly exercises.
