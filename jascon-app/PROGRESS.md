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
  pass, NIST generic with profile 1220 pass, 0 fail each. (The 813 objects
  are those of `convert_bsi.py` v0.2, in which a nested control was a
  clause of its parent; since build 0.9.14 the preset writes the 1,287 of
  v0.3, see below.)

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
  `validate_core.py` on the export: 1038 pass, 0 fail. (That was
  `convert_nist.py` v0.1; since build 0.9.15 the preset writes the 1,037
  objects of v0.2, see below.)

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

- An Attestation is held to what it binds (build 0.9.11; backlog #46, the
  app's port of the check the reference got on 2026-11-14):
  - `jscAttestationBinds` in `jascon-rules.js` is the primitive
    (attestation, bundle) -> full-match, semantic-match or fail, with which
    manifest is bound and what became of every subject; `jscBindsReport`
    makes the reference's lines; `jscSetBinds` applies both to a set.
  - A set is a bundle that was loaded and may have been written to. As
    loaded it is held to the manifest it came with and the objects that
    manifest lists. Written to since, or without a manifest, it is held to
    the bundle an export would write now. The page says which. The reasons
    are above `jscSetBinds` and in the readme ("What an Attestation
    binds").
  - `jscCheckGraph` carries the result (`binds`) and files each line as a
    finding; the Validate page shows the lines, the Assess page one
    Attestation at a time through the same function.
  - A missing envelope of an Attestation beside the manifest is an error
    now, as for the reference; it was a note while the reference did not
    look.
  - The Assess page can take an Attestation out of the set, with its
    envelope, and set an unsigned one to withdrawn. A signed one cannot be
    withdrawn here: any change of it breaks its envelope.
  - How the app held a bundle before this build, found by reading and by
    the probe below: the set keeps the bytes of the manifest it was loaded
    with and never rewrites them; a folder or ZIP brings every text file
    beside the manifest, so an Attestation there was already an object of
    the set (17 for the IFA bundle, where the reference now counts 18 with
    the manifest), with its envelope and the kept pack manifests; the
    export already left an Attestation out of the manifest and wrote it
    beside it. Nothing held an Attestation to its subjects except the
    button of the Assess page, which was wrong (`ERRATA.md`).
  - From a URL the folder is read only for a pack or a set that keeps one.
    Where it is read, every Attestation beside the manifest is taken now,
    the set's own too. Where it is not, the hub says that no Attestation
    was looked for.

  Measured: the primitive passes the 19 `binds-vectors`, each by verdict,
  manifest bound, every subject and failure. For three folders as they lie
  (`jascon/examples`, the IFA bundle and
  `jascon/example-packs/dbvendor-server-7-advice`) the check gives the
  lines `validate_core.py --as-of 2026-11-14` prints for what binds and for
  the envelopes, the same counts by type and no error, without keys and
  with `fixture-trusted-keys.json`. The reference counts 27, 18 and 3,
  which is the objects and the manifest. There are four Full Matches,
  three against this manifest and one against a kept pack manifest; under
  the fixture keys both signatures of the example folder verify, and the
  pack's. The Validate page was driven in headless Chromium for the first
  two folders. The hub does not load a pack over a set, so the pack folder
  was held on the rules and, in the browser, imported and exported. From a
  URL, with a server that lists folders, the example folder arrives with
  both Attestations and the page shows the reference's lines. For a set
  that was changed, the page's lines were compared with what the reference
  prints for the exported folder in six states: unchanged; another object
  changed (Semantic Match); a subject changed (one failure, the reference
  not green); the Attestation taken out (green); for the IFA bundle a
  subject changed (failure), and its unsigned Attestation withdrawn
  (reported, green, 18 counted). No export listed an Attestation, and each
  left beside the manifest with its envelope. 41 deliberate defects were
  each tried on the final code and each turned a test red, the twelve of
  the brief among them; a change that breaks nothing stayed green. Read
  and not measured: a manifest that lists an Attestation; a set of a
  thousand objects; any browser but Chromium. The four tests that need the
  BSI and NIST source files are skipped here, as before.

- MANIFEST-1, and the obligated party of a preset (build 0.9.12; backlog
  #75 and #74, both decided by the author on 2026-11-14):
  - `jscListedAttestationErrors` in `jascon-rules.js`: one failure per
    Attestation among the objects a manifest lists, in the reference's
    words. `jscSetBinds` asks it of the manifest in question, which follows
    the two bases of build 0.9.11. As loaded, a listed Attestation is the
    failure. Written to since, the manifest in question is the export's,
    which lists none; the Attestation is then marked as left out, and the
    pages say so.
  - The export (`jscBuildBundle`): no manifest written here lists an
    Attestation. One that the earlier manifest listed leaves beside the
    manifest, moved out of its folder, and the export's log says so. A set
    nobody changed still leaves as it came, with the manifest that lists
    the Attestation: nothing is repaired in silence, and the Validate page
    reports the failure. The hub says it when such a bundle arrives.
  - Whether a manifest "says the same" as the one a set came with is now
    asked of its canonical form; the order of the keys in a line no longer
    counts (`ERRATA.md`).
  - `jscOscalPartyDefault` and `jscOscalPartyChoice` in `jascon-oscal.js`:
    the party a preset writes where its source names none is a named
    default (BSI the institution, CIS the system administrator, NIST the
    organization), and `opts.party` puts an http(s) URI in its place.
    Empty or no such URI, the import is refused. A level an SP 800-53
    control states stays. The report carries the converters' record
    (`obligated-party`: value, origin, converter-default).
  - The Import page shows the default before the import and names it as
    the preset's, takes another party, refuses in its own words, and keeps
    an entered party in the manifest of the new set.

  Measured for MANIFEST-1: the rule passes the 8 `listed-vectors` (7
  failures among them), each by the number of failures and the id each
  starts with. Two copies were built as the reference's own test builds
  them, the IFA bundle and the worked pack with their Attestation moved
  under `objects/` and entered in the manifest. For both the errors of the
  whole-set check are the failures `validate_core.py --as-of 2026-11-14`
  lists, all of them: one for the bundle (MANIFEST-1; 18 counted), two for
  the pack (ADVICE-1 and MANIFEST-1; 3 counted), and the Attestation is a
  Semantic Match in both. In headless Chromium, on the copy of the IFA
  bundle: the hub says it when the bundle arrives; the Validate and the
  Assess page show the reference's failure; the unchanged set exports with
  the manifest it came with, text for text, and the reference fails the
  export as it fails the folder; after another object was changed the page
  shows no failure and says that the export leaves the Attestation out,
  the export's log says the same, the file lies beside the manifest, and
  the reference finds the exported folder green with the lines the page
  showed (18 counted).

  Measured for the obligated party: with the default left alone the three
  presets write the objects build 0.9.11 wrote, by one SHA-256 over every
  file of an import, taken before the change: 811 objects and 651
  statements for the BSI catalog under `converted_examples`, 1,035 and
  1,918 for the NIST catalog there, 17 and 5 for a catalog of a CIS
  Benchmark's shape. (For BSI the digest was taken anew with build 0.9.14,
  for NIST with build 0.9.15, each when the preset and its catalog changed;
  see below.) With another party every statement binds it and
  nothing else differs in any file. Empty, blank, a short name, a URN and a
  URI with a blank are each refused. A level that an SP 800-53 control
  states stays, on a catalog written for the test. The Import page was
  driven in Chromium for all of it, and the set imported with an entered
  party exports to a folder the reference finds green.

  44 deliberate defects, 20 for MANIFEST-1 and 24 for the party, were each
  tried on the final code and each turned a test red at once; a change that
  breaks nothing stayed green. One of them, a preset's party carried over
  when the rules are switched, would have passed unnoticed: no test
  switched the rules, and a step was added before the defects were run.
  The app's tests: 179, of which 175 pass and 4 are skipped for the BSI and
  NIST source files. Read and not measured: the presets on the publishers'
  own source files; any browser but Chromium. One test of the reader under
  `one-page-apps/` fails on this branch (26 of 27 pass): the reader shows
  no failure for a manifest that lists its Attestation, and the reference
  now does. The reader, its test and the reference are not touched by this
  build, so the failure does not come from it; that was read, the test was
  not run on the branch without this build.

- An Assessment's method is held to its facet (build 0.9.13; backlog #55,
  phase E, on the author's word of 2026-11-14):
  - `jscFacetErrors` in `jascon-rules.js` reads the keys of a `method` as
    it reads the keys of `facets`: the standard library, then the schemas
    the bundle pins, then `private:`, else an error; each payload is held
    to its schema. The two sentences are the reference's.
  - The Assess page, the one place where the app writes an Assessment,
    writes the standard facet `assessment-criteria@1` with `method:
    "manual"` (`jscManualMethod`). The name of the tool is no longer in the
    object; the manifest of an export names it.
  - An Assessment with the method the app wrote before (`{kind, tool}`) is
    recognised (`jscIsAppMethodBefore0913`) and never rewritten by itself.
    The Validate page fails it and adds a line on what can be done; the
    Assess page shows the errors at the Assessment and rewrites the method
    when asked (`jscRewriteAppMethod`). A failing method of another making
    is reported and left alone.
  - Read, for every other place: no import writes an Assessment (OSCAL
    catalog and profile, the three presets, risk catalogues, advice packs),
    and the Checks page writes Checks only.

  Measured: the rule passes the 13 `method-vectors` (8 errors among
  them; twelve when this build was made, and a thirteenth added at the
  merge for the defect below that the twelve did not catch), each by the number of errors and a fragment of each error, with
  the object labelled by its id so that no vector's name can stand in for
  a fragment. The three tests that were red against the reference of
  2026-11-14 pass again; each hands a set with a check from the Assess
  page to `validate_core.py`, and one of them now asserts the method the
  page wrote. For Assessments that exist already, in headless Chromium: a
  set with one Assessment of the app's old method and one whose method and
  one of whose facets name a facet nobody registered was exported, and the
  reference lists four failures for the folder (two for `kind` and `tool`,
  two for the other Assessment). Loaded again in another browser, the
  Validate page shows those four and no other error, and a line on what
  can be done for the first Assessment only. The stored text of that
  Assessment is the same after loading, checking and opening the Assess
  page. After the rewrite was asked for on the Assess page the Assessment
  differs in its method and in nothing else, and page and reference agree
  on the two failures that are left. 26 deliberate defects were each
  tried: 24 turned a test red at once. Two were caught by nothing at
  first, a `method` inside a facet payload that is itself an object taken
  for an Assessment's method (the vector for it has a string there), and
  the Assess page showing a facet's error under the method (no test had an
  Assessment with both); each is red since one assertion was added. A
  change that breaks nothing stayed green. The app's tests: 181, of which
  177 pass and 4 are skipped for the BSI and NIST source files. Read and
  not measured: that no import writes an Assessment; any browser but
  Chromium. Two tests of the reader under `one-page-apps/` fail on this
  branch (28 of 30 pass); both export a set and hand it to the reference.
  The reader and its tests are not touched by this build, and the tests
  were not run on the branch without it.

- The Grundschutz++ preset follows `convert_bsi.py` v0.3 (build 0.9.14;
  the author's decision of 2026-11-14, "A. Bring both presets in line with
  the Python converters"; the SP 800-53 preset follows in a task of its
  own):
  - `jscImportBsi` in `jascon-oscal.js`: every control at every depth is a
    Requirement of its own, with one statement `smt`, its alias, its own
    parameters and its own links as relations. A control with nested
    controls also gives a Set that groups it with them (its own Requirement
    first, then what stands for each nested control in source order); no
    relation is made from the nesting. One sequence counter for the run, as
    the converter takes it. A baseline lists the controls of its level in
    document order, a nested control in the baseline of its own level.
  - A prop is read only in its BSI namespace (`JSC_BSI.PROP_NS`). What the
    rules do not read is carried as the source holds it in the compat facet
    (`metadata`, `back-matter`, `catalog`, `param-extras`, `props`,
    `parts`, `links`, `control`, `group`, in that order, and the pinned
    stub names all nine); a fraction is written as a decimal string.
  - The source entry of the provenance names the author and the day, as the
    converter's manifest does; a German name is written in ASCII before the
    slug. One function mints a party URI from a name (`jscOscalPartyUri`).
  - The report counts the controls with nested controls and what is
    carried, by member; the Import page shows both, in English and German.

  Measured on the Anwenderkatalog of 2026-07-16: 1,287 of 1,287 objects
  (999 Requirements, 288 Sets) have the semantic digest of the committed
  bundle, and its bytes but for the line ends (the converter writes CRLF);
  the six pinned schemas and the source entry of the provenance are the
  converter's. 266 relations, one for each link, none naming no object;
  build 0.9.13 wrote 813 objects and 191 relations, 34 of them naming no
  object (`ERRATA.md`). On a catalogue written for the tests,
  `convert_bsi.py` run in a tree of its own gives the same 9 objects, by
  digest and by bytes. On the OSCAL export the repository carries (the
  input of the party tests, regenerated from the new bundle) the preset
  writes 1,360 objects and 999 statements; the SHA-256 recorded with build
  0.9.11 (811 and 651) gives way to the one of this build, by the author's
  decision. In Chromium, in English and in German, the Import page guesses
  the preset for the pinned catalogue, shows 999 requirements, 288 sets and
  the two new rows, and writes 1,287 objects and 6 schemas without a script
  error. 32 deliberate defects were run against the final code: 31 turned a
  test red, among them the five of the brief (nested controls not
  converted, a nested control's links not carried, a relation made between
  a nested control and its parent, the grouping Set's members in another
  order, a nested control in its parent's baseline). One stayed green: a
  link whose `rel` is empty typed `related` (the converter keeps the empty
  type); no catalogue of the tests has such a link. Two flaws of the
  unfinished draft this build started from, both for a modal verb that is
  the name of a member every JavaScript object has (`constructor`): it was
  taken for a verb of the table (found by reading), and it was counted in
  the report as text (found by the test written for the first). Both are
  fixed, and each is one of the defects that turn a test red. The app's
  tests: 184, of which 181 pass and 3 are skipped for the NIST source
  files; with those files present the 22 tests of `oscal.test.mjs` pass.
  `pages.test.mjs` with the tests under `one-page-apps/`: 53 of 53. Read
  and not measured: the set imported on the page, exported and handed to
  `validate_core.py`.

- The SP 800-53 preset follows `convert_nist.py` v0.2, and the profile
  import carries a profile's metadata and merge directive (build 0.9.15;
  the second half of the author's decision of 2026-11-14, "A. Bring both
  presets in line with the Python converters"):
  - `jscImportNist` in `jascon-oscal.js`: a withdrawn control that names
    no successor is a Requirement with lifecycle `withdrawn` and an
    `unspecified` statement that binds the preset's party; every objective
    names the statement it assesses (`assessment-for`, with
    `requirement-ref` for another control's); the formal SP 800-53A labels
    of the parameters in odp@1; the lineage annotation carries the label a
    reader sees; markdown links stay; the back-matter resources as the
    source writes them, in its order, on the root Set (references@1), and
    the catalogue's metadata there in the compat facet; the PM family's
    overview with its title; a `related` link to a withdrawn control is a
    relation; `contributes-to-assurance` false is written. A prop is read
    in exactly the class and namespace the converter reads, and every
    other prop is counted in the report (`props-not-read`), where the
    converter's ledger fails its run. A status other than `withdrawn` is
    refused, as by the converter. The source entry of the provenance names
    the author and the day.
  - `jscOscalImportProfile`: the profile's metadata (beside title and
    version) and its merge directive stand on the profile's Set in the
    compat facet, as on the converter's baseline Set. A set that pins no
    schema for that facet gets the one `convert_nist.py` pins
    (`jscSet.saveFacetSchemas`, new); one that pins it without `merge`
    keeps the metadata, and the report says why the merge is not carried.
  - The Import page: rows for the withdrawn controls without successor,
    the links that become no relation, the props not read, and what a
    profile's Set carries; the texts of the NIST preset and of the profile
    import in English and German.

  Measured on the pinned catalogue (`SOURCES.sha256`): 1,037 of 1,037
  objects have the semantic digest and the bytes (line ends aside) of the
  committed bundle, which has 1,041 with its four baseline Sets; the six
  pinned schemas and the author and day are the converter's; 3,707
  `assessment-for` links, 1,458 formal labels, 1,920 statements, every link
  and every prop read. Build 0.9.14 wrote 1,035 objects and lost what
  `ERRATA.md` lists. The MODERATE profile, imported into the committed
  bundle, selects the 287 members of its baseline Set in their order, and
  its Set carries the same compat facet; no schema is brought. On a
  catalogue and four profiles written for the tests, `convert_nist.py` run
  in a tree of its own gives the same 6 objects by digest and bytes, and
  the profile import the same members and compat facet as its four
  baseline Sets; the converter exits 1 there for one reference to a
  resource without a link (see Found). On the OSCAL export the repository
  carries the preset writes 1,037 objects and 1,920 statements, and the
  SHA-256 of build 0.9.11 (1,035 and 1,918) gives way to the one of this
  build, by the author's decision. In Chromium, in English and in German:
  the catalogue imported with the preset (1,016 requirements, 21 sets,
  1,920 clauses, 6 schemas, the new rows), the MODERATE profile on top
  (287 included, metadata and merge carried, no seventh schema), the set
  exported through the hub: `validate_core.py` 1040 pass, 0 fail, ALL
  GREEN.

  29 deliberate defects were run against the final code, among them the
  four of the brief (`assessment-for` links not written, a withdrawn
  control without successor not written, the zero-padded label in the
  annotation, a formal ODP label not carried): 28 turned a test red at
  once. The one that stayed green (a classless prop of a name the rules
  read only with a class, counted as read) is red since the test holds
  such a prop; the four defects on reading props were run again then, and
  all four were red. In a first round two defects had stayed green (a prop
  read whatever its class, whatever its namespace), because no catalogue
  of the tests had such a prop; that is why the preset now counts every
  prop it does not read, and the test holds two of them. The app's tests:
  185, all pass, with the NIST source files present (3 of them are skipped
  without); `pages.test.mjs` with the tests under `one-page-apps/`: 53 of
  53. Read and not measured: the page test that imports a profile into the
  example folder now brings the compat schema with it (its profile has
  metadata), and the reference finds that export green as before.

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
  Settled on 2026-11-14: the bundle is converted from the pinned file
  (`SOURCES.sha256`), and the preset's 1,037 objects all equal it
  (measured with build 0.9.15).
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
    name. Decided on 2026-11-14 (backlog #74) and built in 0.9.12: the
    party is a named default that the user may replace (see Done).
- Found with build 0.9.11:
  - A bundle that keeps no pack does not bring its Attestation when it is
    loaded from a URL. A URL names files; the Attestation is named by
    nothing the manifest lists, so it is found only through a listing of
    the folder, and the app asks a server for one only where a pack gives
    it a reason (an earlier decision: a listing that is not there is an
    error line in the browser's console). The hub now says that no
    Attestation was looked for. Whether every server should be asked is the
    author's to decide; it costs one request and, on a host that does not
    list folders, that console line.
  - A manifest that lists an Attestation, against D3.1: the export kept
    the listing as it came, also where it wrote a new manifest. Decided on
    2026-11-14 (backlog #75, MANIFEST-1) and built in 0.9.12: such a
    manifest is refused, and a manifest written here leaves the Attestation
    out (see Done).
  - An object removed in the app leaves no trace in the set, so a set from
    which only something was removed is read as loaded: the comparison
    names the manifest the set came with, where the reference will say
    "another manifest" about the export. No verdict turns into a failure
    or out of one by this; the missing object is an error of its own.
  - *Verify* on the Assess page types every object of the set by schema
    before it answers. Not measured on a set of a thousand objects.
- Found with build 0.9.13:
  - `sync-inlined --check` is out of date again, for the same reason as
    with build 0.9.12: the rules changed, and `one-page-apps/` is
    regenerated at the merge.
  - The rewrite of an old method changes the Assessment's semantic digest.
    The pages say so, and an Attestation that named it then fails as any
    changed subject does. The app does not look for such an Attestation
    before it rewrites.
- Found with build 0.9.14:
  - `convert_bsi.py` carries an empty parameter label in compat
    `param-extras`, as the preset does, but its path map names no place
    there for `params[].label`, so on a catalogue with such a label the
    converter writes its bundle and ends with exit code 1 (one wiring
    check). Measured on the catalogue of the tests; the pinned catalogue has
    none. The converter is not this build's to change; the test that runs it
    accepts that one failure and no other.
  - A number the source writes with a zero after the point (`1.0`) reaches
    the preset as the integer 1, because `JSON.parse` has read it; the
    converter writes the string "1.0". The same for a float without a
    fraction such as `1e16`. Read, not measured: no catalogue at hand has
    such a number, and the kernel spells a fraction as a decimal string.
  - The OSCAL export of the Grundschutz++ bundle, read by the preset, gives
    1,360 objects and modality `unspecified` on every statement: the export
    writes the modality and the obligated party in props of its own names
    (`modality`, `obligated-party`) and the facets as JSON in a prop of
    JASCON's namespace, none of which the preset reads; it carries them in
    the compat facet. The preset is for the BSI's catalogue; that export is
    only the input of the party tests.
- Found with build 0.9.15:
  - `convert_nist.py` writes no relation for a `reference` link to a
    back-matter resource that gives no link, and its ledger then finds the
    link's two values unaccounted and ends the run with exit code 1, after
    the bundle is written. Measured on the catalogue of the tests; the
    pinned catalogue has none. The preset counts such a link in
    `links-not-written`. The converter is not this build's to change.
  - Three bundles pin a schema under one id and version,
    `https://ns.jascon.net/compat/oscal-1x` 1.0.0, each with other members:
    DE.BSI nine (`metadata`, `back-matter`, `catalog`, `param-extras`,
    `props`, `parts`, `links`, `control`, `group`), US.SP800-53 three
    (`metadata`, `merge`, `class`), AU.ISM four (`group-parts`, `props`,
    `nested-in`, `metadata`). Measured on the committed files. A profile
    imported into a BSI set therefore keeps its metadata and not its merge
    directive. Which schema that facet has is the converters' to settle.
  - On the OSCAL export of the SP 800-53 bundle the preset reads none of
    JASCON's own props (11,793) and none of the 5,065 links of its
    controls: the export writes them in a shape of its own. The report
    counts both; that export is only the input of the party tests.
- Found with build 0.9.12:
  - `node one-page-apps/tools/sync-inlined.mjs --check` reports the pack
    builder's inlined copy of the rules as out of date, because the rules
    changed and `one-page-apps/` was not to be edited in this round. The
    command without `--check` brings it up to date. No test of either
    suite depends on it.
  - A set nobody changed, whose manifest lists an Attestation, cannot be
    put right in the app except by changing something else in it. The
    export has no switch that writes a new manifest on request.
  - The BSI and NIST source files the two presets were written against are
    not in this checkout. The digests of the objects were taken on the
    catalogs under `converted_examples/*/oscal-export/`, which the presets
    read; none of those NIST controls states an implementation level, so
    the case where the source names the party is held by a catalog written
    for the test.

## Open

- The settings page opens in the same tab from the hub, which clears the key
  the hub holds. From a tool page it opens in a new tab and the key stays.
- Suggestions exist on the Risk page only; a second model pass (a checker)
  is not built.
