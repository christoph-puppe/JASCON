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
  shipped bundles pass the whole-set check, and so does the example folder
  since its pin was repaired on `main` (PR #8). `validate.html` on top of it.

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

- The NIST SP 800-53 preset in `jascon-oscal.js` (the rules of
  `convert_nist.py`, without the baseline Sets). On the local source file all
  1,035 objects equal the output of the Python converter run on the same
  file. Driven in headless Chromium with the MODERATE profile on top;
  `validate_core.py` on the export: 1038 pass, 0 fail.

- The proposed Check type (CP-CHECK-1, merged from the branch that drafts
  it): type recognised at load, `kernel-version` 2.0.0 written when a Check,
  check results or a check-ref are in the set, the evidence store kept on
  load (folder, ZIP, URL) and export, and the sixteenth vector family ported
  to `jascon-rules.js` (I-Regexp on a state-set engine, check-verdict,
  CHECK-1..15 with the evidence chain). The example folder passes the
  whole-set check with its two Checks, and a tampered evidence blob fails it.

- The Checks tool (build 0.9.0): `checks.html` with three views (rules and
  checks, the editor with the kernel rules, lint and a verdict tester, and
  drafting with a model, one rule or many), `jascon-checks.js` (rules on
  offer, id minting, assembly of a model's answer, read-only lint), the
  check-draft prompt and schema in `jascon-ai.js` (operators and fact types
  from the kernel schema), the CIS Benchmark preset in `jascon-oscal.js`
  (equal to `convert_cis_benchmark.py` by semantic digest on a synthetic
  catalog), and the hand-over from Import to Checks. Driven in Chromium from
  a CIS import to saved checks against a simulated Gemini endpoint; the
  exported bundle passes `validate_core.py`. No real service was called.

- Advice packs (build 0.9.3; CP-ADVICE-1, accepted for the 2.0.0 release
  candidate on 2026-11-12): the seventeenth vector family in
  `jascon-rules.js` (ADVICE-1..11, the publisher verdict, the import plan;
  all 74 vectors), the extended kernel pin (a pack header, `statement-ids`
  on a capability, `product-version`) and DATE-1/DATE-2 with the 14 shape
  vectors of the kernel family. The kept pack manifests (`packs/sha256/`)
  survive load from a folder, a ZIP and, where the server lists folders, a
  URL, and the export. On the Home page a pack is previewed, imported once
  and replaced by another release with a diff; on the Implement page a
  recommendation is adopted. `jascon-view.js` renders a Component with its
  product version and capabilities. Driven in Chromium on the worked pack;
  the set after import and adoption, exported, gives `validate_core.py`
  8 pass, 0 fail. The system workbench no longer writes the literal
  `declared` (see `ERRATA.md`). The reader is at v1.9.0 with the same fix
  and shows pack headers and kept manifests.

## Next

- An OSCAL component definition as a third kind on the Import page, written
  as a pack (CP-ADVICE-1 §9 item 7); the converter it would follow
  (`convert_cdef.py`) does not exist yet.
- One real call per service with a key of the user's: the model ids in the
  settings and the request shape were checked against a simulated service
  only (the model documentation could not be reached from the build
  environment).
- Let the pages type objects by schema at load (`jscTypeOf`) instead of by
  fields (`jscInferType`).
- Screenshots for the repository README.

## Found on the way (not fixed here)

- A catalog imported under one's own domain makes every Tailoring of that
  domain authority-claimed over it (the tier rule compares origins). The
  import page warns; the rule itself is the kernel's.

- The example attestation names an envelope (`attestation-envelope.dsse`)
  that the repository does not carry, and `validate_core.py` checks an
  envelope only for an attestation the manifest lists, which an attestation
  over the manifest cannot be (D3.1).
- The IFA bundle's attestation carries a stale digest for `system1234`.
- Fixed in the reference on 2026-11-12, found while building this: for a
  bundle folder that keeps a pack, `validate_core.py` did not read the
  vendor's attestation beside the manifest and reported the kept pack's
  publisher as CLAIMED. It now reads it, as the app does, and both
  validators say ATTESTED, NOT VERIFIED where no key was given.
- Two requirements whose ids end in the same word give the system workbench
  two Implementations with one id (the id is minted from the asset's title
  and the last part of the requirement's id); the set then shows one of
  them and reports the other file as ignored. Older than this build, read
  from the code and not tried.
- The shipped `converted_examples/US.SP800-53` bundle was converted from an
  earlier revision of NIST's 5.2.0 file. In it SA-15(13) "Logging Syntax"
  carries the statement of SA-15(12); NIST's current file has it right.

## Open

- The settings page opens in the same tab from the hub, which clears the key
  the hub holds. From a tool page it opens in a new tab and the key stays.
- Suggestions exist on the Risk page only; a second model pass (a checker)
  is not built.
