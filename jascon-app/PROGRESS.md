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

- The model access: `jascon-ai.js` (one client for Gemini, OpenRouter and an
  own endpoint; the key in memory and relayed through the hub; editable
  prompts; an answer cache), the settings and prompt editors in
  `config.html`, and the view *Suggestions* of `risk.html` (drafts of risks,
  treatments for the risks of the register). Driven in headless Chromium
  against a simulated Gemini endpoint on SP 800-53 with the demo Tailoring;
  the exported set gives `validate_core.py` 1043 pass, 0 fail. No real
  service was called.

- The last three rule families: DSSE envelopes (Ed25519, with the tier in
  verification mode), the composition of two bundles, and conditional-apply,
  in `jascon-rules.js`; all fifteen vector families pass. `validate.html`
  takes trusted keys and has a view that composes the active set with
  another one. Driven in headless Chromium with the signed fixture of the
  dsse vectors.

## Next

- One real call per service with a key of the user's: the model ids in the
  settings and the request shape were checked against a simulated service
  only (the model documentation could not be reached from the build
  environment).
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
- The example attestation names an envelope (`attestation-envelope.dsse`)
  that the repository does not carry, and `validate_core.py` checks an
  envelope only for an attestation the manifest lists, which an attestation
  over the manifest cannot be (D3.1).
- The IFA bundle's attestation carries a stale digest for `system1234`.

## Open

- The settings page opens in the same tab from the hub, which clears the key
  the hub holds. From a tool page it opens in a new tab and the key stays.
- Suggestions exist on the Risk page only; a second model pass (a checker)
  is not built.
