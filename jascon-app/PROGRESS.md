# JASCON-App: where the build stands

A note for whoever continues the work. The plan is in the pull request text
and in `readme.md`; this file says only what is done and what is next.

## Done

- Step 0: branch restarted from `main` at 948ee9ef (includes PR #7, the matrix).
- Step 1: `jascon-core.js` and `.css`, the hub `index.html`, `config.html`,
  translation check and generated settings table. Checked in headless
  Chromium against the IFA bundle.
- Step 2, first part: `jascon-rules.js` with the modality lattice, the
  parameter law, selection, tier and Tailoring resolution, ported from
  `validate_core.py` and run against the modality, parameter and tier vectors.

## Next

- Step 2: `jascon-view.js` (object rendering shared by the tool pages), then
  `browse.html`, `tailor.html`, `map.html`, `implement.html`, `assess.html`
  from `one-page-apps/jascon-reader.html`. Each page is added to `APPS` in
  `index.html` when it exists.
- Step 3: the rest of the validator in `jascon-rules.js`; `tests/rules.test.mjs`
  names the vector families that are not ported yet. Then `validate.html`.
- Step 4: `import.html` (OSCAL catalog, then profile).
- Step 5: `risk.html` (register, scales with the matrix, coverage, catalogue import).
- Step 6: docs, README links, reader frozen.

## Open

- The AI layer the plan names for the first version is not built yet; it is
  due with the first page that uses it (risk suggestions in step 5).
- A key for a model must not be kept in browser storage; hold it in memory.
