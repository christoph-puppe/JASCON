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

## Next

- Step 4: `import.html` (OSCAL catalog, then profile).
- Step 3: the rest of the validator; `tests/rules.test.mjs` names the six
  vector families that are not ported yet. Then `validate.html`. The tool
  pages still type an object by its fields (`jscInferType`); `jscTypeOf`
  (schema matching) is ready to replace it at load.
- Step 6: docs, README links of the repository, reader frozen.

## Found on the way (not fixed here)

- `jascon/examples` checked as a bundle fails D26: the stub pin of the stdlib
  assessment-criteria facet differs from the normative descriptor.
- The IFA bundle's attestation carries a stale digest for `system1234`.

## Open

- The AI layer the plan names for the first version is not built yet; it is
  due with the first page that uses it (risk suggestions in step 5).
- A key for a model must not be kept in browser storage; hold it in memory.
