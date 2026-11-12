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
