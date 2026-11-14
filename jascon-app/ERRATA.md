# Errata

One entry per bug that reached a push, with its cause, its class and the
test that now covers it. Classes: algorithm, data, forgotten, mismatch,
surprise, blunder.

## 2026-11-10 · build 0.2.0 · five tool pages did not start

- **Symptom.** After the commit that ported schema matching and the Risk
  rules, `browse.html`, `tailor.html`, `map.html`, `implement.html` and
  `assess.html` stopped at load with `JSC_SCHEMA is not defined`. The pushed
  state was broken from commit `de8376d2` until the next commit.
- **Cause.** `jascon-rules.js` began to read the kernel schema from
  `jascon-schema.js`, a new script. Only the page written after that change
  loaded it; the five existing pages were not touched.
- **Class.** Mismatch: a shared file gained a dependency and its users were
  not updated. The node tests passed, because in node the rules file requires
  the schema itself.
- **Why it was not caught.** The browser checks of those pages had been run
  before the change and were not run again after it; they were scripts
  outside the repository.
- **Fix.** The five pages load `jascon-schema.js` before `jascon-rules.js`.
- **Test.** `tests/pages.test.mjs`, "every page starts without a script
  error, in English and in German": opens every page the hub lists in
  Chromium and fails on any page or console error.

## 2026-11-11 · build 0.8.1 · a Risk written in the app was a KERNEL-1 error until the export

- **Symptom.** A Risk written on the Risk page into a set whose manifest pins
  no kernel (any 1.0.0 bundle, a catalog import) made the Validate page
  report "needs kernel 2.0.0, but the manifest pins no kernel-version" as an
  error, although the export writes `kernel-version` 2.0.0. Found when the
  Checks tool wrote a Check into a freshly imported CIS set.
- **Cause.** `jscCheckGraph` held the manifest the set came with to KERNEL-1
  for every object of the set, including those the app wrote and will pin
  on export. The digests of such objects were already a note.
- **Class.** Forgotten: authored content that needs a newer kernel was a
  case nobody handled; the Risk end-to-end test loads a bundle that is
  pinned already.
- **Fix.** KERNEL-1 is judged on the imported objects; a need that comes
  only from authored content is a note that the export writes the pin.
- **Test.** `tests/rules.test.mjs`, "a whole set: content written in the app
  needs no pin before the export; imported content does"; and
  `tests/checks.test.mjs`, which writes checks into an unpinned set.

## 2026-11-12 · build 0.9.3 · every edge of a system built in the app cited a capability nobody declared

- **Symptom.** *Build a system* on the Implement page wrote
  `"capability-ref": "declared"` on every Implementation, on Components to
  which it gave no capability. Since kernel 2.0.0 reads that field (ADVICE-7:
  a capability-ref names a capability its component declares), every such
  edge is an error in the reference validator: "cites capability 'declared',
  which … does not declare". The bundle reader
  (`one-page-apps/jascon-reader.html`) wrote the same literal.
- **Cause.** Until CP-ADVICE-1 `capability-ref` was a free string no rule
  read, and the workbench filled the required field with a placeholder.
- **Class.** Mismatch: the kernel gave meaning to a field, and a writer of
  that field was not changed with it. The change proposal named the place
  (§7, §12); the app was out of its scope then.
- **Why it was not caught.** No test of the app held an edge to anything
  beyond the schema, and the schema accepts any string.
- **Fix.** Each asset declares one capability per requirement attached to
  it, with an id derived from the requirement and unique within the
  Component (`jscCapabilityId`, ADVICE-4), and the edge cites that id. The
  reader does the same since v1.9.0. A set written by an earlier build keeps
  its edges as they are; the Validate page now names each of them, and
  saving the system again from the workbench rewrites them.
- **Test.** `tests/pages.test.mjs`, "a system built on the Implement page
  validates; …": builds a system in the browser, reads the stored edge and
  runs the whole-set check; the export of that set passes
  `validate_core.py`. `tests/advice.test.mjs`, "a capability id is derived
  from the requirement and unique within its component".

## 2026-11-12 · build 0.9.4 · the BSI import counted 213 parameters as source defects and missed the lists packed into one value

- **Symptom.** The Import page, run on the Anwenderkatalog Grundschutz++,
  reported 213 "source defects": every sentence-template prop
  (`result`, `result_specification`) that contains a `{{…}}` slot, such as
  `nach {{einem anerkannten Standard}}` in GC.1.1. The same count stood in
  `convert_bsi.py`'s coverage report, and the handbook and the website called
  them pseudo-placeholders that no validator can see. They are parameters:
  all 221 slots stand exactly where the statement prose inserts a parameter
  (`{{ insert: param, … }}`), and 219 repeat the label of the parameter the
  control declares. The source's real defect went unreported: 125 of 470
  `tags` values, 616 of 900 `threats` values and 40 of 634
  `target_object_categories` values pack several vocabulary terms into one
  comma-separated string, where OSCAL repeats the prop and JSON has arrays.
  Pointed out by the project's author.
- **Cause.** The converter took `{{` in a prop value for a broken
  placeholder without checking it against the parameters and the prose of
  the same control. The comma-split was written as a conversion rule and
  never counted as a finding.
- **Class.** Data: a reading of the source's notation that nobody checked
  against the source.
- **Why it was not caught.** The test asserted the count (213) and not what
  the counted values were; nothing compared a slot with the prose.
- **Fix.** The import, like `convert_bsi.py`, checks every `{{…}}` slot
  against the prose (it must stand where a parameter is inserted; a slot
  that does not is reported) and reports every list value packed into one
  string. The objects it writes are unchanged.
- **Test.** `tests/oscal.test.mjs`, "BSI preset: …": the packed values per
  prop (tags 125, threats 616, target_object_categories 40), 221 slots and
  none away from an insertion.

## 2026-11-13 · build 0.9.5 · four run rules skipped their comparison when a field was left out

- **Symptom.** The Validate page, like the reference validator it is ported
  from, accepted four things the specification forbids: an evidence record
  at `alternate/<hex>` instead of `evidence/sha256/<hex>`; a `collector-id`
  on a row whose Check has no `collector@1` facet; a row parameter
  (`"unbound-extra": 999`) that its Check does not read; an evidence record
  without `observation-digest` on a row that carries an observation. Reported
  from outside as issues 23 to 26 in the GitHub tracker, each with a
  reproduction on the conformance vector "CHECK-15 satisfied: row -> record
  -> raw output". Two neighbours of the same kind turned up while fixing
  them: a record that names a collector on a row that names none, and a
  record with an `observation-digest` on a row without an observation.
- **Cause.** Each comparison stood behind a guard that asked whether the
  optional field was there: the path was held to the digest only if it
  already had the store's form, the collector was looked up only if the
  facet existed, row and record were compared only where both carried the
  field, and the parameters were walked from the Check's side only.
- **Class.** Forgotten: the case "the field is absent on one side" was
  handled as "nothing to check" in four places. The port copied the
  reference line by line, so the app, the reference and the PowerShell twin
  agreed with one another and all three were wrong.
- **Why it was not caught.** Every negative vector changed a value and none
  removed a field or added a key; the engines were tested against one
  another and not against the wording of the rules.
- **Fix.** A relative evidence reference outside `evidence/sha256/` fails
  CHECK-15 before it is read. A Check without the facet declares no
  collector (CHECK-13). A row names only parameters its Check reads, with
  or without a Tailoring (CHECK-12). Row and record name the same collector
  or both none, and a row carries an observation exactly when its record
  carries an `observation-digest` (CHECK-15). The same in
  `validate_core.py` and `validate_core.ps1`.
- **Test.** `tests/rules.test.mjs`, "check: the CHECK rules every bundle
  vector names, the evidence chain included", with eleven new bundle vectors
  in `check-vectors.json` (188 to 199). Ten of them fail on the rules as
  they were; the eleventh is the legitimate case, a run that observed
  nothing.

## 2026-11-13 · build 0.9.6 · the app and the reference read the same number as two values

- **Symptom.** For the same JSON text the Validate page and `validate_core.py`
  disagreed. A Check that expects `9007199254740992`, on an observation of
  `9007199254740993`: the reference said `not-satisfied`, the app
  `satisfied`. `1.0` or `1e3` on an `integer` fact: the reference said
  `inconclusive`, the app `satisfied`. The semantic digest differed as well:
  the reference hashed `{"n":9007199254740993}` and `{"n":1.0}` as written,
  the app as `...992` and `1`. So an Attestation could verify in one tool
  and fail in the other. Reported from outside as issue 27 in the GitHub
  tracker, for the first of these; the other two were found while
  reproducing it.
- **Cause.** `JSON.parse` returns doubles: an integer beyond 2^53 is rounded
  and the fraction of `1.0` is gone before any rule sees the value. The
  specification named a "permitted number domain" (D3 item 3) and defined
  none, and `jcs-vectors.json` held no number. The comment on
  `jscCanonical` said the two engines "agree on everything the schema
  allows"; the schema type `integer` allows both `1.0` and large values.
- **Class.** Mismatch: two modules disagreed on a contract, here on what a
  JSON number is. The contract was missing from the specification, so
  neither side was wrong against it.
- **Why it was not caught.** The canonical form of the app was tested
  against the reference's vectors, and no vector held a number outside the
  small integers. A vector file could not have held `1.0` as a number
  anyway: the test's own parser would have read it as 1.
- **Fix.** The specification states the domain (D3 item 9, NUMBER-1): a JSON
  number is an integer in plain digits, of magnitude at most 2^53 - 1; it is
  refused, never rewritten. `jascon-rules.js` checks the text of every file
  of a set (`jscNumberSpellingViolations`, where `1.0`, `1e3` and `-0` are
  still visible) and the value of every object (`jscNumberViolations`); an
  `integer` fact or parameter outside the domain is mistyped, so
  `check-verdict` is `inconclusive`. Evidence records and observation files
  are held to the same rule. The reader (v1.10.0) reports it when it
  verifies digests. The canonical form itself is unchanged: inside the
  domain the engines agree. The comment on `jscCanonical` is corrected.
- **Test.** `tests/rules.test.mjs`: "jcs: canonical form, optional
  containers that must be absent instead of empty, and the number domain"
  (14 `number-text` vectors, which carry JSON texts), "NUMBER-1 (errata
  2026-11-13): JSON.parse alone would let every spelling and the reported
  integer through", and "NUMBER-1 (errata 2026-11-13): a whole set - a file
  that writes 10.0 is an error although the parsed object is fine"; three
  verdict vectors, two parameter vectors and one bundle vector in the
  shared corpus.

## 2026-11-13 · build 0.9.8 · a CIS import wrote the benchmark's version as the date of every Mapping

- **Symptom.** With the kernel schema of CP-AUTHOR-1 a CIS Benchmark import
  made Mappings that match no type: `provenance.date is '0.0.0-synthetic'`
  on the test catalog, the benchmark's version on a real one (DATE-3). The
  app's own rules reported each as an error and `validate_core.py` refused
  the exported set. Found when the regenerated schema turned two tests red:
  the Checks tool's walk from a CIS import to an export, and the CIS test
  of the import.
- **Cause.** The preset follows `convert_cis_benchmark.py` line by line, and
  the converter writes `"date": VER`, the catalog's `metadata.version`.
  Until CP-AUTHOR-1 a Mapping's `provenance.date` was any non-empty string
  and no rule read it.
- **Class.** Mismatch: the kernel typed a field, and a writer of that field
  was not changed with it, as with `capability-ref` on 2026-11-12. The
  change proposal counted the values the repository holds (§2.2, all
  conform); the repository carries no CIS bundle (CIS terms), so this
  writer was not among them.
- **Why it was not caught.** The preset was tested for agreement with its
  converter by semantic digest, and the two agreed. That every object is
  one kernel type was asserted too, and held for as long as the date was
  free text.
- **Fix.** The preset writes the day of the catalog's
  `metadata.last-modified`, the date OSCAL gives a release
  (`convert_cr26.py` dates its Mappings with its source's `last_updated` in
  the same way). A catalog that has cross-references and no such date is
  refused with the reason. `convert_cis_benchmark.py` was changed the same
  day and writes the same day, with the same refusal; preset and converter
  agree again by semantic digest.
- **Test.** `tests/oscal.test.mjs`, "ERRATA 2026-11-13 (DATE-3): a CIS
  import dates its Mappings with the day of the catalog's last-modified,
  never with its version". The comparison with the converter in the same
  file holds every object to the converter's semantic digest, as before.
  `tests/checks.test.mjs` runs the reference validator on the exported set.

## 2026-11-13 · build 0.9.9 · an edited check was saved under its first author's name with today's date

- **Symptom.** A Check that one party wrote, opened on the Checks page and
  saved by somebody else, kept `provenance.author-ref` and got today's
  date. The object then said that its first author wrote this version
  today. Read from the code while the pages were given the setting "Who am
  I". Measured for the case that remains, a browser without the setting:
  the example folder's check by `…/party/secops`, dated 2026-11-11, saved
  without a change, is stored as secops with the day of the save.
- **Cause.** The editor took the author from the stored check and the date
  from the clock (`jscToday()`), one field from each version. The app had
  no notion of who uses it, so there was nobody else to offer.
- **Class.** Mismatch: two fields that state one fact together, who and
  when, were filled from two sources.
- **Why it was not caught.** The tests of the editor write new checks.
  None opened a check that another party had written.
- **Fix.** A check opened for editing offers the party of the setting "Who
  am I" as the author. The field is shown and can be changed, as before.
  Not fixed where the setting is empty: the form then shows the author the
  check names, and a save still writes today's date beside it. The page
  cannot know better; the field is there to be corrected.
- **Test.** `tests/pages.test.mjs`, "Import, Map and Checks: …", the part
  marked ERRATA 2026-11-13: with the setting, the example check by secops
  opens with the setting's party and is saved under it with today's date;
  without the setting it opens with secops.

## 2026-11-14 · build 0.9.9 · the author of a document whose party is defined twice: this file and the converters gave two answers

- **Symptom.** `jscOscalAuthorParty` and `document_author()` of
  `jascon/scripts/oscal_conv_lib.py` are written to one text. Put to 4,000
  generated documents, they named a different author for 41. In every one
  of them `metadata.parties` defined one uuid twice: this file answered
  with that party, the converter library with nobody.
- **Cause.** The text said "the one party the document defines" and did
  not say what a party defined twice is. This file kept parties in a Map
  built from pairs, which counts a uuid once and keeps its last
  definition; the library counted list entries and looked a uuid up by its
  first definition.
- **Class.** Mismatch: one rule, two implementations, an input neither
  author thought of.
- **Why it was not caught.** Both sides had the same table of thirteen
  cases, and none of them defined a party twice. Each side passed its own
  tests.
- **Fix.** In both: a party is an entry of `parties` with a uuid, and
  where a uuid is defined twice its first definition is the party. An
  entry without a uuid is no party. After it, 0 differences on the same
  4,000 documents (author and day).
- **Test.** `tests/oscal.test.mjs`, "the author of an OSCAL document: what
  the table does not say", the four cases after the comment that names
  this erratum's date; the same four in
  `jascon/scripts/test_oscal_conv_lib.py`. The comparison itself was run
  from scripts outside the repository.

## 2026-11-14 · build 0.9.10 · where the kernel requires a party and nobody was named, a page wrote one of its own

- **Symptom.** Objects written in the app named parties nobody had named.
  A Mapping saved with an empty author field carried
  `<namespace>/party/author`, a Check `<namespace>/party/check-author`, an
  Assessment `<namespace>/party/assessor` as its performer, a Deviation
  `<namespace>/party/ciso` as its approver, a Requirement written on the
  Browse page `<namespace>/party/organisation` as the party it binds, and
  every clause of a catalog imported by the generic OSCAL rules
  `<namespace>/party/organization`. The advice pack builder filled an
  empty publisher id with `<origin>/party/vendor` when an origin was
  typed, and that party went into the header and into the signature. Every
  one of these objects was valid. Found by reading the pages while the
  setting "Who am I" was built (backlog #70); the first four were read in
  the pages then, the last three were found by searching every page for a
  party made from a fixed word. Measured for four of the seven by the
  tests that failed when the words were removed: one test saved a model's
  drafts of checks, one added a Deviation, one wrote an Assessment and two
  built an advice pack, and none of them had named the party that was
  written.
- **Cause.** The kernel requires these fields, a form field can be empty,
  and the pages closed the gap with a default: a word in the form's draft
  (`author`, `assessor`, `ciso`, `organisation`) that was minted into a
  party id on save, or a literal in the code. The word was shown in the
  field, so it looked like a value somebody had chosen.
- **Class.** A made-up value in a required field: the object is valid, the
  statement in it is false, and no validator can tell, because a
  placeholder party has the shape of a real one.
- **Why it was not caught.** Every check the app and the reference run
  asks whether a party is there, and it was. The tests of the pages left
  these fields alone and compared what came out with what the page had
  put in. For the optional `provenance` the question had been asked and
  answered the day before (nothing is made up, a missing author is a
  report line); nobody had asked it for the fields the kernel requires.
- **Fix.** Author decision of 2026-11-14: refuse if no party is named.
  A page writes a party only from what was typed or from a setting the
  user made. With the field empty it refuses the save, says which field is
  empty and that the kernel requires it, and changes nothing. An author
  and a performer start from the setting "Who am I", a Risk's owner from
  the setting "Default risk owner"; an approver and an obligated party
  start empty, always. What is typed is read by one function for every
  party field (`jscPartyRef`): a URI as it is, a short name as
  `<namespace>/party/<name>`. The function has no default. The Risk page
  never made up an owner or an approver; it now says a missing one in the
  same words as the other pages and not in the schema's. A draft check a
  model wrote is saved under the author named when it is taken. Not fixed,
  and not fixable from inside the app: a set written with an older build
  keeps the parties that build made up, and nothing in the object marks
  them. Left as they are: the parties the three import presets write for a
  publisher's corpus, which are the Python converters' rules.
- **Test.** `tests/pages.test.mjs`, the five tests after the comment "No
  page writes a party nobody named (backlog #70)": for each field an empty
  one refuses the save and the set is the same file for file, a named
  party is written as named, an emptied field stays empty, and the
  approver starts empty with "Who am I" set. Each exports its set and runs
  `validate_core.py --require-authors --as-of 2026-11-14` on it.
  `tests/authors.test.mjs`, "no page mints a party from a word of its own
  (backlog #70)", reads the sources: no party id is built from a literal
  word outside the converter presets, which it lists by name.
  `tests/checks.test.mjs` (no draft is asked for or taken without an
  author), `tests/ai.test.mjs` (a model's draft of a risk without an
  owner), `tests/oscal.test.mjs` (the generic rules refuse without a
  party), `one-page-apps/tests/pack-builder.test.mjs` (an origin typed
  makes no publisher).

## 2026-11-14 · build 0.9.11 · the Assess page called an Attestation a Full Match while one of its subjects was not in the set

- **Symptom.** Measured with build 0.9.10 on the IFA bundle, whose
  Attestation names three subjects. With one of them, the Requirement
  AC-6.1, removed from the set, *Verify* on the Assess page said "Full
  Match: bytes and meaning as signed", and under it "subjects: 2 intact, 0
  changed, 1 not in this set". With all three removed it said "Unknown".
  A subject given as a bare digest was counted as not in the set, whatever
  the set held. For the reference validator a subject that is not
  delivered does not bind, and the bundle fails while the Attestation is
  active.
- **Cause.** The page had a judgement of its own, written before any tool
  applied attestation-binds to a bundle. It counted the subjects that were
  intact, changed and missing and decided from the first two: no subject
  changed and at least one intact was a match. A missing subject was
  printed and weighed nothing.
- **Class.** A second implementation of one rule, with a case left out:
  three things can become of a subject, and two were looked at.
- **Why it was not caught.** No test pressed the button. Until 2026-11-14
  there was no vector for the primitive on a bundle, and the reference did
  not apply it to one either (backlog #46), so nothing existed to hold the
  page to. The line under the verdict stated the fact and the verdict
  ignored it.
- **Fix.** The page has no judgement of its own any more. It shows what
  `jscSetBinds` says, the rule the Validate page runs, through the function
  both pages share (`jscView.bindsHtml`), in the reference's words. The
  rule is held to the nineteen `binds-vectors`.
- **Test.** `tests/pages.test.mjs`, "Attestations of a set that was
  changed: …", the part marked ERRATA 2026-11-14: with AC-6.1 removed the
  page shows the reference's failure, "not an object of this bundle".
  `tests/rules.test.mjs`, "attestation-binds on a bundle: all 19 vectors
  …".

## 2026-11-14 · build 0.9.12 · an unchanged set got a new manifest on export when its manifest had the keys of a line in another order

- **Symptom.** A bundle whose manifest listed one object as `id`,
  `version`, `path`, then the two digests, loaded and exported without a
  change, left with a manifest written by the app and the log line "new
  manifest with both digests per object". Measured while MANIFEST-1 was
  built: a test loaded such a bundle (the reference's own test writes its
  changed copies in that order) and expected the manifest to leave as it
  came; it did not. With build 0.9.12 that would also have taken a listed
  Attestation out of the manifest of a set nobody had touched.
- **Cause.** The export asks whether the manifest it computes "says the
  same" as the one the set came with, and passes the old one through if
  so. It compared the two as `JSON.stringify` writes them, and that keeps
  the order in which keys were written. The app writes the digests before
  `path`.
- **Class.** Equality asked of a spelling where it was meant of a value.
- **Why it was not caught.** Every bundle of the repository and every
  bundle the app writes has its lines in the app's order, so the two
  spellings always agreed. No test loaded a manifest written by another
  hand.
- **Fix.** The comparison is made on the canonical form (keys sorted). The
  order of the lines still counts; the order of the keys in a line does
  not.
- **Test.** `tests/rules.test.mjs`, "attestation-binds on a set: …", the
  part on MANIFEST-1: the unchanged set leaves with its manifest, text for
  text. `tests/pages.test.mjs`, "MANIFEST-1: …": the exported manifest is
  the one that was loaded.

## 2026-11-14 · build 0.9.12 · a preset wrote a party its source does not state, and did not say that the party was its own

- **Symptom.** A catalog imported with the BSI, NIST or CIS preset bound
  every statement to one party (`…/party/institution`,
  `…/party/organization` where a control states no level,
  `…/party/system-administrator`). The source names none of them. The
  form showed nothing about it, the report did not mention it, and no
  field could put another party there. Recorded in build 0.9.10 as left
  alone, because the presets follow their converters (backlog #70).
- **Cause.** The kernel requires `obligated-parties`, a catalog seldom
  says whom it binds, and the converters each settled on one party for
  their corpus. The presets are ports of the converters and took the party
  over as a literal in the code.
- **Class.** A made-up value in a required field, as in the erratum of
  build 0.9.10, in the one place that was then left: the value is
  reasonable, and it is the tool's and not the source's.
- **Why it was not caught.** The presets are held to their converters by
  semantic digest, so they could not differ from them, and the converters
  did the same. It took a decision, not a test.
- **Fix.** Author decision of 2026-11-14 (backlog #74): an argument with a
  named default. The Import page shows the party before the import and
  calls it the preset's default; another party, an http(s) URI, takes its
  place; an empty or malformed field refuses the import; a level a control
  states stays the source's; the report and, for an entered party, the
  manifest of the new set say who chose.
- **Test.** `tests/oscal.test.mjs`, the three tests that begin "the
  obligated party of": the bytes of build 0.9.11 with the default left
  alone, the caller's party and the refusals, and the NIST level that
  stays. `tests/pages.test.mjs`, "Import: a preset's party …".

## 2026-11-14 · build 0.9.13 · the Assess page wrote a method that names no facet

- **Symptom.** Every Assessment the Assess page wrote carried `method:
  {kind: "manual-check", tool: "JASCON-App <build>"}`. A method is a facet
  payload (handbook 10.1), and neither `kind` nor `tool` is a facet. With
  the reference of 2026-11-14 an exported set that holds such an Assessment
  fails twice per Assessment ("method 'kind' is no registered facet",
  "method 'tool' …"). Measured by the coordinator on this app's own tests:
  three of them exported a set after a check on the Assess page and turned
  red against the new reference.
- **Cause.** The kernel schema says of `method` only that it is an object.
  The page was written to the schema, the validators read the member in no
  rule, and so two plain keys looked as good as a facet id. The name of
  the tool went there because the page had no other place in mind for it.
- **Class.** A member typed by convention and held by nothing: the schema
  allows anything, the rule lived in the handbook, and every tool was
  open. The same class as the Attestation nothing checked (backlog #46).
- **Why it was not caught.** No vector had an Assessment's method in it
  until 2026-11-14. The app's tests handed their exports to the reference,
  which accepted them, and the app's own check is a port of the reference.
- **Fix.** The page writes the standard facet `assessment-criteria@1`
  with `method: "manual"`, and the tool is not written into the object.
  The rule is ported (`jscFacetErrors`) and held to the twelve
  `method-vectors`. An Assessment written before this build is not
  rewritten by itself: the Validate page fails it and says what can be
  done, and the Assess page rewrites the method when asked, for the shape
  this app wrote and for no other.
- **Test.** `tests/rules.test.mjs`, "facets: an Assessment's method is held
  to its facet, all 13 vectors …". `tests/pages.test.mjs`, "an Assessment
  with the method this app wrote before build 0.9.13: …", and the
  assertion on the method in "Assess: an empty performer …"; the three
  tests that were red export their sets to the reference as before.

## 2026-11-14 · build 0.9.14 · the Grundschutz++ preset turned a nested control into a statement of its parent and lost its links

- **Symptom.** Measured with build 0.9.13 on the Anwenderkatalog of
  2026-07-16: 813 objects (651 Requirements, 162 Sets) for 999 controls.
  Each of the 348 nested controls became a second statement of the
  Requirement of its top-level control, with its title, label and
  alt-identifier in that statement's taxonomy payload. Its own links were
  not read: 75 links on 60 nested controls were lost, so the import wrote
  191 relations for the 266 links of the catalogue. A link that named a
  nested control became a relation to `…/req/<id>`, an id that was no
  object: 34 of the 191 relations (32 ids). What the preset did not read was
  dropped without a line: of the pinned catalogue, everything its metadata
  says beside the title and the version (last-modified, the OSCAL version,
  props, links, roles, parties, responsible parties, remarks); of any other
  catalogue, a prop or a part of a name it did not know, and a prop of a
  known name in another namespace was read as if it were BSI's.
- **Cause.** The preset is a port of `convert_bsi.py`, and v0.2 of the
  converter read the nesting as clauses of the parent. BSI nests controls
  for grouping only (the author, 2026-11-14): a nested control is a full
  control. The rule that content is never dropped was not yet written into
  either.
- **Class.** Algorithm: the mapping read the structure of the source as
  something it does not mean, and lost content on the way.
- **Why it was not caught.** The preset was held to the converter's bundle
  by semantic digest, and the converter made the same reading, so the test
  showed that the two agreed and not that either was right. No test counted
  the links of the source against the relations written, or asked whether a
  relation names an object.
- **Fix.** The preset follows `convert_bsi.py` v0.3: every control at every
  depth is a Requirement of its own with its own statement, parameters,
  props and links; a control with nested controls also gives a Set that
  groups it with them, and no relation is made from the nesting. A prop is
  read only in its BSI namespace, and what the rules do not read is carried
  in the compat facet as the source holds it. Measured: 1,287 objects (999
  Requirements, 288 Sets), each with the semantic digest of the committed
  bundle; 266 relations, none of which names no object.
- **Test.** `tests/oscal.test.mjs`, "BSI preset: a nested control is a
  Requirement of its own with its own links; …": reads the source itself
  and holds every Requirement's relations to its control's own links, one
  for one, besides the grouping Sets, their order and the baselines. "BSI
  preset: every object has the semantic digest of the committed DE.BSI
  bundle, 1,287 of 1,287", and two tests on a catalogue written for the
  tests, one of them against `convert_bsi.py` run on it.

## 2026-11-14 · build 0.9.15 · the SP 800-53 preset and the profile import dropped content without a line

- **Symptom.** Measured with build 0.9.14 on the pinned SP 800-53 5.2.0
  catalogue, against this build: 1,035 objects for 1,037. The two withdrawn
  controls that name no successor, CP-10(3) and SC-19, were written nowhere,
  with their titles, labels and statements. Not read: the 3,707
  `assessment-for` links by which an objective names the statement it
  assesses, and the 1,458 formal SP 800-53A labels of the parameters. 525
  markdown links in 159 objects were cut to their text, so their targets
  were lost. The 201 back-matter resources were written in a shape of the
  app's own (title, citation, first link), sorted by title, without their
  uuids, so that no `(#uuid)` could name one. The overview of the PM family
  became `guidance` without its title. What the catalogue says of itself
  beside its title and version was not carried. Two `related` links to a
  withdrawn control were dropped. 172 lineage annotations carried the
  zero-padded label (`AC-02(10)`) instead of the one a reader sees
  (`AC-2(10)`), because a prop was read by its name whatever its class.
  The profile import did not carry a profile's metadata beside the author
  and the day, and only counted its merge directive.
- **Cause.** The preset followed `convert_nist.py` v0.1, which read the same
  less and dropped the same. The rule that content is never dropped
  (2026-11-14) was not yet written into either.
- **Class.** Algorithm: the mapping read less than the source states and
  dropped the rest without a line.
- **Why it was not caught.** The preset was held to the converter's bundle
  by semantic digest, and the converter lost the same; the test let four
  objects differ besides, because the bundle had been converted from an
  earlier file than the one at hand.
- **Fix.** The preset follows `convert_nist.py` v0.2 (see `readme.md`,
  "Importing OSCAL"); a prop is read in exactly the class and namespace the
  converter reads. The profile import writes a profile's metadata and merge
  directive on its Set in the compat facet, as the converter does on a
  baseline Set. Measured: 1,037 of 1,037 objects have the semantic digest
  and the bytes of the committed bundle, which is converted from the pinned
  file since 2026-11-14.
- **Test.** `tests/oscal.test.mjs`, "NIST preset: the objects of the
  committed SP 800-53 bundle, 1,037 of 1,037 …", "NIST preset: the rules on
  a small catalog", "NIST preset and profile import: … convert_nist.py"
  (the converter run on a catalogue written for the tests), "profile: NIST
  MODERATE selects the members … and its Set carries what the converter's
  baseline Set carries", and the part of "profile: excludes, …" on a
  profile's own Set.


## 2026-11-14 · build 0.9.16 · both presets left out what the converters had declared as drops

- **Symptom.** Measured with build 0.9.15 against this build, on the pinned
  sources. Grundschutz++: the uuid of the catalogue and its one back-matter
  resource, which a link of the metadata names, were not carried. SP
  800-53: the uuid of the catalogue and the three print labels `a.` of
  SI-2(7) were not carried, and the status of the 180 withdrawn controls
  that name a successor stood nowhere; a profile's uuid, its imports and
  its back-matter were not carried by the profile import. The report said
  nothing of it.
- **Cause.** The converters had declared these values as drops for the
  author's decision; the presets followed them. The author decided on
  2026-11-14 that all of them are content (`drafts/phase-e/`).
- **Class.** Forgotten: a drop that was declared in the converter and had
  no line in the app.
- **Fix.** The presets and the profile import follow the converters' new
  round (see `readme.md`, "Importing OSCAL"). Measured: Grundschutz++ 1,287
  of 1,287 objects, SP 800-53 1,217 of 1,217, each by semantic digest and
  by bytes.
- **Test.** `tests/oscal.test.mjs`, the two digest tests, "NIST preset: the
  rules on a small catalog", and the two tests that run a converter on a
  catalogue written for the tests, now without a tolerated failure.
