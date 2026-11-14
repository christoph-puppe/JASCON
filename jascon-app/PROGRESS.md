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

- Who decided, and when (build 0.9.8; CP-AUTHOR-1): the eighteenth vector
  family in `jascon-rules.js` (`jscAuthorReport` for AUTHOR-1..4,
  `jscReviewReport` with `jscUtcDay` for REVIEW-1; all 40 vectors), the four
  new reasons of the kernel pin in `jscKernelNeeded` and in the pin the
  export writes (`jscNeedsKernel2`), DATE-1 on `decided` and DATE-3..5, and
  the 54 vectors of the kernel family. Both reports give the lines
  `validate_core.py --as-of 2026-11-13` prints for the example folder and
  the IFA bundle; the day computation gave the reference's answer on 300,000
  generated cases, in three time zones, and both reports its answer on
  20,000 generated bundles (scripts outside the repository). No page shows
  the reports yet. The CIS preset dates its Mappings (see `ERRATA.md`).

- Who decided, written (build 0.9.9; backlog #69, the app's half; author
  decisions of 2026-11-13: a missing author is a report line and never a
  refusal; an import pre-fills who and when from its source and the user
  may overwrite it):
  - One setting, *Who am I* (`org:me`), and one accessor, `jscWhoAmI`.
    `jascon-view.js` has the author field every writing form shows and the
    control that decides a Deviation.
  - What is written is decided in one place, the section "what the pages
    and the imports write" of `jascon-rules.js`: `jscProvenance` (both
    fields or nothing), `jscImportProvenance` (the caller's fields replace
    the source's one by one), `jscAuthorRecord`, `jscAuthorTailoring`,
    `jscAuthorRisk`, `jscDecideDeviation`.
  - Tailor, Risk, Implement and Assess write `provenance`; Tailor and Assess
    decide a Deviation with `decided` and an optional `review-due`. Map and
    Checks start from the setting. No page edits the authorizations of a
    Component, so no page writes the date of one.
  - The Validate page shows the two reports with a day (*Review dates as
    of*) and the switch *Require authors*; `jscCheckGraph` runs them.
  - `jascon-oscal.js` has the rule for the author of an OSCAL document
    (five steps, stated above `jscOscalAuthorParty`; the Python converters
    are written to the same text). A profile's Tailoring gets `provenance`
    from it; the CIS Mappings keep CIS. `import.html` shows both values in
    two fields before the import.
  - Risk catalogues: the header has an optional `released`; both shipped
    catalogues state 2026-11-10. `risk_catalog.py import` writes
    `provenance` and takes `--author-ref` and `--date`; `jascon-riskcat.js`
    is its port; the demo was rebuilt.

  Measured: the Tailor, Risk, Implement, Assess, Import, Map and Checks
  pages were driven in headless Chromium. Five sets exported with every
  author named give `validate_core.py --require-authors --as-of 2026-11-13`
  ALL GREEN without an AUTHOR line (26, 12, 29, 33 and 28 pass, 0 fail).
  One of them is three requirements of kernel 1.0.0 and what three pages
  wrote: its export pins no kernel while nobody is named and 2.0.0 once an
  author is. Three sets with one record left without its author give
  exactly that one AUTHOR line, on the Validate page and from the
  reference, which fails them only with `--require-authors`. The Validate
  page shows the reference's lines for the example folder and the IFA
  bundle, for 2026-11-13 and 2023-06-24, with the switch off and on, and
  for a review date decided on the page on the day it is due and the day
  after. The demo bundle gives 1,065 pass, 0 fail with `--require-authors`.
  The port of the catalogue import writes the same 24 Risks and the same
  report as `risk_catalog.py` for six combinations of `--author-ref` and
  `--date`. 67 deliberate defects in the new code were each tried once: 66
  turned a test red at once, one did not (a nameless party that falls
  through from the first step of the document-author rule), and does since
  two cases were added. Read and not measured: nothing was tried in a
  browser other than Chromium, and no real OSCAL profile with parties was
  at hand (the tests write their own). The Python converters' side of the
  document-author rule is somebody else's work and was not compared.

- No page writes a party nobody named (build 0.9.10; backlog #70; author
  decision of 2026-11-14: refuse if no party is named):
  - `jscPartyRef` in `jascon-rules.js` is the one reading of a typed party:
    a URI as it is, a short name as `<namespace>/party/<name>`, nothing as
    nothing. It has no default. `jascon-view.js` has the field for a party
    the kernel requires (`requiredParty`) and the sentence every refusal
    ends with (`missingParty`). The shared author field serves a Mapping
    and a Check as a required field and says so in its hint.
  - The placeholders are gone: `…/party/author` (Map),
    `…/party/check-author` (Checks, also on a draft a model wrote),
    `…/party/assessor` (Assess), `…/party/ciso` (Tailor),
    `…/party/organisation` (Browse), `…/party/organization` (the generic
    OSCAL import, which got a field *Who the statements bind*), and
    `<origin>/party/vendor` in the advice pack builder (its version
    1.2.1). Each of these places refuses an empty field, names it, and
    changes nothing.
  - An author and a performer start from *Who am I*. An approver starts
    empty, always, and so does the party a statement binds. An emptied
    field stays empty.
  - The Risk page never made up an owner or an approver. It now says a
    missing one in the page's words and not the schema's, reads a typed
    name as the other pages do, and keeps an emptied owner field empty in
    its catalogue and model views.
  - The optional author of a Tailoring, a Risk, an Implementation and a
    Finding is unchanged: empty writes none and stops nothing. The comment
    above `jscPartyRef` says why the two differ.
  - Left as they are, by intent: the parties the BSI, NIST and CIS presets
    write (`…/party/institution`, the implementation levels or
    `…/party/organization`, `…/party/system-administrator`,
    `…/party/cis`). They are the rules of the Python converters, which the
    presets are held equal to. Whether a converter may default a party is
    a question for the converters.

  Measured: the Map, Checks, Assess, Tailor, Browse, Import and Risk pages
  and the pack builder were driven in headless Chromium. For each required
  field a test leaves it empty, sees the refusal with the field's name,
  and compares every file of the set before and after; then names a party
  and reads it back as named. Six sets exported after that give
  `validate_core.py --require-authors --as-of 2026-11-14` ALL GREEN without
  an AUTHOR line (28, 27, 26, 26, 4 and 27 pass, 0 fail; with the reference
  as it was changed while this was built, to hold an Attestation read with
  a bundle to what it binds, the same six sets give 30, 29, 28, 28, 4 and
  29 pass, 0 fail, measured on a trial merge). Three tests of
  the app and two of the pack builder had relied on a placeholder and
  failed when it went; each now names its party. 57 deliberate defects
  were each tried: 56 turned a test red at once. One did not, an approver
  carried over from the last Deviation to the next, changed where the form
  is reset after an add; that change alone cannot be seen, because
  choosing a statement rebuilds the operation. Changed in the three places
  that carry the approver over together, it turns a test red since the
  test adds a second Deviation on the same requirement. A change that
  breaks nothing was run as a control and stayed green. Six defects of
  build 0.9.9 whose code was rewritten were run again and are red. Read
  and not measured: nothing was tried in a browser other than Chromium.
  Four tests are skipped where the BSI and NIST source files are absent,
  as they are here; one of them runs the generic rules over the NIST
  catalog and was changed to name the party the rules used to supply, so
  its result should be the one it had, and that was not run.

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
- Found with build 0.9.9, each older than it:
  - A click that follows typing is lost. Where a field redraws its form
    when it changes (the Tailor workbench, the Risk form), the first click
    on a button after typing into such a field lands on a button that is
    being replaced. Measured on the Tailor page in Chromium: type a
    parameter value, click *Add the operation*: no operation; click again:
    one. Read from the code for the Risk form, not tried there.
  - Saving an edit of a Check that an Assessment of the set has run makes
    that Assessment fail CHECK-8, because its result names the digest of
    the check as it was. The Checks page says nothing about it. Measured:
    the reference validator listed two CHECK-8 failures for the example
    folder after one of its checks was saved again. The rule is the
    kernel's (a changed check is a different check); what is missing is a
    word on the page, or a new version of the check.
  - Four parties are made up by pages where the kernel requires a party
    and the user gave none, each from a short name the form shows:
    `…/party/author` on a Mapping, `…/party/check-author` on a Check,
    `…/party/assessor` as the performer of an Assessment, `…/party/ciso` as
    the approver of a Deviation. Decided on 2026-11-14 and fixed in build
    0.9.10, with three more of the kind (see Done and `ERRATA.md`).
  - The record of catalogue entries that do not apply names the party of
    the Owner field as the one who decided, not the party of *Who am I*,
    and refuses the record without an owner, although its schema leaves
    who decided optional. Left as it was in 0.9.10 too: the party is one
    the user named, for another role, and the record is not a kernel
    object. It is the rule of 2026-11-13 (a missing author is no refusal)
    that it does not follow.
- Found with build 0.9.10:
  - A set written with an older build keeps the parties that build made
    up. `…/party/author` in a stored Mapping looks like any other party;
    the app has no list of the words and does not search for them.
  - The NIST preset writes `…/party/organization` for a control that
    states no implementation level, as `convert_nist.py` does and counts
    in its report. By the rule of #70 that is a party the source did not
    name. It is the converter's rule and was not changed here.

## Open

- The settings page opens in the same tab from the hub, which clears the key
  the hub holds. From a tool page it opens in a new tab and the key stays.
- Suggestions exist on the Risk page only; a second model pass (a checker)
  is not built.
