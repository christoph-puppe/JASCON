# JASCON-App: where the build stands

A note for whoever continues the work. The plan is in the pull request text
and in `readme.md`; this file says only what is done and what is next.

## Done

- Step 0: branch restarted from `main` at 948ee9ef (includes PR #7, the matrix).
- Step 1: `jascon-core.js` and `.css`, the hub `index.html`, `config.html`,
  translation check and generated settings table. Checked in headless
  Chromium against the IFA bundle.
- Step 2: `jascon-rules.js` (modality lattice, parameter law, selection, tier,
  Tailoring resolution, state machines; run against the vectors),
  `jascon-view.js` (object rendering shared by the tool pages), and the pages
  `browse.html`, `tailor.html`, `map.html`, `implement.html`, `assess.html`.
  Each was driven in headless Chromium and its output checked with
  `validate_core.py`.

- Step 5: the rules the risk page stands on (schema matching, closure, kernel
  pin, Risk rules with coverage, scales and matrix; vector families risk,
  scale, kernel, reference and lifecycle pass), `jascon-riskcat.js` (catalogue
  import, rebuilt against the committed demo), `jascon-presets.js`, and
  `risk.html` (register with heat map, form, scale and matrix editor,
  coverage, catalogue import). Driven in headless Chromium on SP 800-53 with
  the demo Tailoring; the exported set gives `validate_core.py` 1064 pass, 0 fail.
- `tests/pages.test.mjs` opens every page in Chromium; see `ERRATA.md`.

- Step 4: `jascon-oscal.js` (BSI preset after `convert_bsi.py`, generic
  catalog rules, profile to Set and Tailoring) and `import.html`. The BSI
  preset gives all 813 objects the semantic digest of the shipped DE.BSI
  bundle; the NIST MODERATE profile selects the 287 members of the shipped
  baseline. Driven in headless Chromium; `validate_core.py`: BSI import 814
  pass, NIST generic with profile 1220 pass, 0 fail each.

- Step 3: the per-object checks, facet payloads, the operation law per tier,
  the attestation verdict and `jscCheckGraph` (a whole set) in
  `jascon-rules.js`; twelve of the fifteen vector families pass; the five
  shipped bundles pass the whole-set check and the example folder shows the
  one D26 error the Python validator shows. `validate.html` on top of it.

## Next

- The AI layer (model client with the key in memory, prompts in the
  settings, risk suggestions). The plan names it for the first version; it
  is not built.
- The three vector families still missing: conditional, composition, dsse.
- Let the pages type objects by schema at load (`jscTypeOf`) instead of by
  fields (`jscInferType`).
- A port of `convert_nist.py` as a third import preset.
- Screenshots for the repository README.

## Found on the way (not fixed here)

- A catalog imported under one's own domain makes every Tailoring of that
  domain authority-claimed over it (the tier rule compares origins). The
  import page warns; the rule itself is the kernel's.

- `jascon/examples` checked as a bundle fails D26: the stub pin of the stdlib
  assessment-criteria facet differs from the normative descriptor.
- The IFA bundle's attestation carries a stale digest for `system1234`.

## Open

- The AI layer the plan names for the first version is not built yet; it is
  due with the first page that uses it (risk suggestions in step 5).
- A key for a model must not be kept in browser storage; hold it in memory.
