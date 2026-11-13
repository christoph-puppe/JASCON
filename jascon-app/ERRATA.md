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
