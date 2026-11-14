# Plan — the open backlog before 2.0.0

### 2026-11-14 · branch `claude/sleepy-planck-g6w3h3` · phases A, B and C are built (§8, §10, §11); D and E are a plan; §9 says what another session's work on main changed in it

Input: the ten open rows of `jascon-v0.6-spec-feedback-backlog.md` and the
residue of #45, with the author's dispositions of 2026-11-13. Every
statement about the repository below is marked **measured** (a script or
a count run on this tree), **read** (from a file, not counted) or
**argued**.

## 1. The dispositions

| # | Item | Author, 2026-11-13 | In this plan |
|---|---|---|---|
| 65 | A Deviation has no expiry | fix; the field stays optional | §3, with #66 |
| 66 | No decision names its author | fix; an author wherever a decision is made, a check done, a risk changed | §3 |
| 54 | "Not applicable" for a catalogue risk has no shape | fix | §4 |
| 46 | The example attestation binds nothing | recommend, plan | §5.1 |
| 64 | The IFA report counts what is not carried | recommend, plan | §5.2 |
| 58 | The twin compares ids with `-ceq` | recommend, plan | §5.3 |
| 47b | Two OSCAL response types have no code | recommend, plan | §5.4 |
| 45 | The case-differing-ids vector is missing | recommend, plan | §5.5 |
| 41 | Path coverage is not value arrival | stays in the backlog; planned | §6.1 |
| 55 | `Assessment.method` is never validated | stays in the backlog; planned | §6.2 |
| 62 | `http-api` collector has no format | stays in the backlog | not planned |

## 2. Order of work

| Phase | What | Kernel shape changes | Depends on |
|---|---|---|---|
| A | #45, #58, #54, #47b: four small changes, one commit each | none | #47b needs the author's nod on its closing rule |
| B | #65 and #66 as one change proposal, `drafts/CP-AUTHOR-1.md`, then its landing as **2.0.0-rc.4** | yes | the three open points of §3.7 |
| C | One IFA re-run: #64, the IFA half of #46, the IFA payload of #55, and the authors that phase B makes the converter write | none | B; the IFA sources |
| D | #46: a real example attestation, and a check that keeps it real | none | B and C, because both move the digests it binds |
| E | #41 and the validator half of #55 | none | after the tag, unless the author says otherwise |

B is the reason the tag moves. Specification IV.9 item 5 says "Nothing is
left to decide before the tag"; with #65 and #66 accepted as shape
changes that sentence no longer holds, and the candidate after the
landing is rc.4. A, C and D do not block the tag. They are listed before
it because each is cheaper before the digests are final.

Every validator change is run by `.github/workflows/validators.yml` on a
push to this branch: the Python reference, the twin on Windows
PowerShell 5.1, the JavaScript port and the pages (**read**).

## 3. #65 and #66 — who, when, and until when

### 3.1 Where the kernel records who and when today

**Measured** on `jascon/schemas/jascon-2.0.0.schema.json`:

| Record | Who | When | Missing |
|---|---|---|---|
| Tailoring as a whole | none (the origin of its id; the signer of an Attestation over it) | none | both |
| A select, an exclude, an operation | none | none | both; `excludes[].rationale` is optional |
| Deviation | `approver-ref` | `opened` | when it was decided; until when it holds (#65) |
| Risk as a whole | `owner-ref` | none | who wrote this version, and when |
| Risk `rating`, `residual-rating` | none | none | both |
| Risk `acceptance` | `approver-ref` | `date` | nothing |
| Implementation | none | none | both, including for the decision `not-applicable` |
| Assessment | `performer-ref` | `time`, a free string | a typed time |
| A check result row | the Assessment's performer; the tool in `collector-id` and the evidence record's `runner` | `time`, typed | nothing |
| Finding | through `assessment-ref` | none | who changed its state, and when |
| Component authorization | `authority-ref` | none | when |
| Mapping | `provenance.author-ref` | `provenance.date`, a free string | a typed date |
| Check | `provenance.author-ref` | `provenance.date`, typed | nothing |
| Attestation | `signer` | `timestamp`, a free string | a typed time |
| Requirement, RequirementSet | the publisher, by the origin of the id | `version` | nothing proposed |

The kernel spells "who and when" five ways (`provenance`, `approver-ref`
with `opened`, `approver-ref` with `date`, `performer-ref` with `time`,
`signer` with `timestamp`) and leaves six records without either.

Three of the "when" fields accept any string. Specification D8 says a
date that any string satisfies "cannot be compared, sorted or checked",
and names `provenance.date` among the typed ones; for a Mapping it is not
(**read**).

### 3.2 The model proposed

1. **One spelling.** `provenance: {author-ref, date}`, the shape Mapping
   and Check already carry, becomes a shared definition. Nothing new is
   named.
2. **On the record.** Tailoring, Risk, Implementation and Finding gain an
   optional `provenance`. It names who wrote this version of the object
   and when. A change is a new version, so "who changed the risk" is the
   `provenance` of the version that changed it.
3. **On the decision inside a record.** Each select, exclude and
   operation of a Tailoring, and each `rating` and `residual-rating` of a
   Risk, may carry its own `provenance`. Without one it has the
   record's. A Tailoring decided by one person names that person once.
4. **Deviation** gains `decided` (a date: when it was approved or
   withdrawn) and `review-due` (#65). **A Component authorization** gains
   `date`.
5. **The three free "when" fields are typed**: `Assessment.time` and
   `Attestation.timestamp` as a date or an RFC 3339 date-time,
   `Mapping.provenance.date` as a date.

Not proposed, and why:

- **A log inside the object** (OSCAL's `risk-log`). The versions of an
  object are its history; a second history inside each version can
  contradict the first.
- **A party type.** `author-ref` stays a URI that is compared and never
  resolved (D2; parties are landmarks since #16).
- **A performer per check result row.** A run by someone else is another
  Assessment.
- **An author on Requirement and RequirementSet.** The publisher is the
  author; an Attestation proves it.

What an author field is and is not: it is a claim inside the object. It
is part of the semantic digest (**read**: `sdig` drops `annotations` and
nothing else), so an Attestation over a Tailoring binds the claim. Proof
of who signed stays the Attestation's signature.

### 3.3 The rules

The schema leaves every new field optional, because a catalogue
authority's Tailoring needs none of them. The validators hold the
consumer's records to them, as they already do for Deviation duties
(D13: duties bind at consumer tier).

| Rule | Text |
|---|---|
| AUTHOR-1 | A Tailoring at consumer tier carries `provenance`, or each of its selects, excludes and operations carries its own. |
| AUTHOR-2 | Each exclude of a Tailoring at consumer tier carries a `rationale`. Today the field is optional and `risk-coverage` reports the gap without failing. |
| AUTHOR-3 | A Risk, a Finding and an Implementation carry `provenance`. Whether a vendor's Implementation in an advice pack is exempt is settled in the proposal. |
| AUTHOR-4 | A Deviation in state `approved` or `withdrawn` carries `decided`. |
| DATE-3, 4, 5 | The names of the three newly typed fields when an object matches no type for that reason, as DATE-1 and DATE-2 do. |

### 3.4 #65 in detail

- **Shape.** `Deviation.review-due`, optional, typed like
  `Risk.review-due`: a date, a date-time, an elapsed duration, or a
  calendar period with its named calendar.
- **What a duration counts from.** `decided`; without it, `opened`. The
  rc.3 text does not say what a Risk's duration counts from (**read**, by
  search); the proposal gives both the same sentence.
- **No clock in the validator.** The reference validator reads no clock
  today (**measured**: `validate_core.py` imports neither `time` nor
  `datetime`), so a bundle's verdict does not change overnight. A
  lapse is judged only against a date the caller passes, `--as-of
  YYYY-MM-DD`. Without it the validator prints how many approved
  Deviations carry a `review-due` and judges none.
- **What a lapsed Deviation does.** With `--as-of`, an approved Deviation
  past its `review-due` is reported as lapsed and no longer licenses its
  weakening: at consumer tier the duty check fails as it does for a
  weakening with no Deviation. Resolution is unchanged; the resolver
  applies the operation either way and reads no date. A calendar period
  whose calendar the tool does not have is reported as not evaluable and
  is not a lapse.

### 3.5 What the landing touches

| Artifact | Change |
|---|---|
| `jascon/schemas/jascon-2.0.0.schema.json` | the shapes of §3.2 |
| `jascon/scripts/validate_core.py` | AUTHOR-1 to 4, DATE-3 to 5, the lapse check, `--as-of` |
| `jascon/scripts/validate_core.ps1` | the same rules; the shapes need no twin code, the twin reads the schema (**read**: backlog #63) |
| `jascon-app/` | `jascon-schema.js` regenerated by `tools/gen-schema.mjs`; the rules in `jascon-rules.js`; the Tailor, Risk, Implement and Assess pages write the author, which needs a "who am I" setting; tests |
| `one-page-apps/` | the reader shows the new fields; the pack builder is checked against AUTHOR-3 |
| `jascon/conformance/` | a new family for the AUTHOR rules and the lapse; shape vectors for every new and typed field. The total moves from 537 |
| `jascon/examples/` | 2 Tailorings (2 selects, 3 operations), 1 Risk, 2 Findings, 2 Implementations and 1 Deviation gain their fields (**measured**); the manifest is re-pinned |
| `risk-catalogs/` | the import tool writes `provenance` on the Risks it creates; demo rebuilt |
| `jascon/scripts/convert_ifa.py` | phase C: 2 Risks, 2 Findings, 3 Implementations and 1 Deviation of the IFA bundle (**measured**) get their authors from the source's parties and dates |
| Text | specification rc.4 (D8, D13, D23, a new decision, Appendix A, IV.5b, IV.9); handbook A.3, A.10, chapter 6, F.10; `PRIOR-ART.md` (the two cells where a neighbour was ahead); website `evidence.html#limits` in five languages; README; the register; the backlog rows; `SKILL_jascon.zip` |

Cost in the shipped data is small: none of the five shipped bundles
holds a Tailoring or a Mapping; the lifecycle records are in one of
them, IFA, and in the example folder (**measured**). In those two places
the three fields to be typed hold eight values, and all eight already
conform (**measured**; the conformance vectors were not surveyed).

Size: the largest item of this plan. One proposal document, then a
landing across three validators, the app, two pages, the conformance
corpus and the texts.

### 3.6 The evidence the register will want

D22 governs types. For fields the register has a precedent, "D22 — two
fields on the author's word" (CP-ADVICE-1). The proposal names what was
read and says where no count exists:

- **In the repository.** `convert_ifa.py` reads `origin.actors` of an
  OSCAL risk characterization and `metadata.responsible-parties` (lines
  299, 321, 335), so OSCAL carries who per item in its assessment layer
  and per document everywhere (**read**).
- **In the backlog rows.** CISO Assistant's `expiration_date` on a
  security exception and its change log per assessment (**read** there,
  at a named commit; not re-read for this plan).
- **From memory, to be read against the published texts before the
  register entry.** ISO/IEC 27001:2022 clause 7.5.2 asks for
  identification of documented information by, for example, title, date
  and author; clause 6.1.3 f asks for the risk owners' approval of the
  treatment plan. OSCAL's `risk-log` entries carry `logged-by`.
- **Not counted.** No corpus of consumer Tailorings with authors exists
  in the repository. The decision rests on the author's word and the
  standards named.

### 3.7 The author's answers (2026-11-13)

The three points below were open when this plan was written. The author
answered the same day, and §3.3 and §3.4 are to be read with these
answers:

1. **Report.** AUTHOR-1 to 4 are report lines. A missing author fails
   nothing by default; a flag, `--require-authors`, turns the lines into
   failures, as `--require-risk-basis` does for uncovered requirements.
2. **`provenance`.** One spelling, `provenance: {author-ref, date}`.
3. **Read the clock, then report.** The validator reads the date of the
   run and reports every approved Deviation past its `review-due`. The
   lapse is a report line and fails nothing; the Deviation keeps
   licensing its weakening until someone acts. `--as-of YYYY-MM-DD`
   stays as the way to fix the date, which the conformance vectors need
   in order to give the same answer every day.

The points as they were put:

1. **Fail or report.** The plan lets AUTHOR-1 to 4 fail a consumer's
   bundle. The alternative is the pattern of `--require-risk-basis`: a
   report line by default, a failure with `--require-authors`. Failing
   by default turns the example folder, the IFA bundle, the risk
   catalogue demo and every bundle the app has exported red until they
   name their authors.
2. **The spelling.** `provenance: {author-ref, date}` everywhere, as
   planned, or the backlog row's flat `decided-by` and `decided`.
3. **A lapsed Deviation.** With `--as-of` the duty fails, as planned, or
   the lapse is a report line and licenses the weakening until someone
   acts.

AUTHOR-4 has a consequence for imports that follows the #43 decision: a
Deviation from a source with no decision date cannot be written as
`approved` and stays `pending`. The IFA bundle has one such Deviation.

## 4. #54 — the "not applicable" record

Today the side file is a map from an entry's label to a sentence, with
the review date inside the prose (**read**:
`risk-catalogs/demo/office-it-moderate/not-applicable.json`). Not
importing a catalogue risk is a decision, so it gets the same who and
when as §3:

```json
{ "record-version": 1,
  "catalog": { "id": "https://…/risk-catalog/office-it", "version": "1.0.0" },
  "tailoring-ref": "https://…/tailoring/soa-office-it",
  "entries": [
    { "entry": "OFF-23",
      "rationale": { "en": "Public AI services are blocked at the web proxy and no licence for one exists." },
      "provenance": { "author-ref": "https://…/party/ciso", "date": "2026-11-10" },
      "review-due": { "type": "date", "value": "2027-11-10" } } ] }
```

`catalog` says which list the record answers; `tailoring-ref` and
`review-due` are optional. Work:

- `risk-catalogs/schema/not-applicable.draft.schema.json`, beside the
  draft catalogue schema; outside the kernel, as #53 decided.
- `risk-catalogs/tools/risk_catalog.py` (`load_not_applicable`) validates
  the file against it and refuses an entry the catalogue does not hold.
- `jascon-app/jascon-riskcat.js` and `risk.html` write the new shape and
  still read the old map, because exported bundles carry it.
- The demo is rebuilt; `riskcat.test.mjs` and the README follow. The
  measured result stays the oracle: 0 gaps with the record, 1 without.

Size: small. No kernel, no validator. It can be built in phase A; its
`provenance` follows point 2 of §3.7 if the author chooses the other
spelling.

## 5. Recommendations

### 5.1 #46 — make the example attestation real, and keep it real

**Measured**: of `attestation-acme-2026.json`, the rendering digest is
real (it is the digest of `authorization-summary.md`); the three subject
digests match no example object; the manifest digest is not the
manifest's; `envelope-ref` names a file that does not exist.

1. Replace the three subjects by `{id, semantic-digest}` entries for
   three example objects an authorizing official would sign: the
   Tailoring, the Implementation and the Assessment of the ACME case.
2. Set `content-manifest-digest` to the digest of the example manifest.
3. Sign it with the corpus fixture key, whose seed is public and which
   already signs the vendor's example attestation, and ship the
   envelope. Verification mode then has a second positive example.
4. In `validate_examples`, hold every Attestation beside the example
   manifest to what it binds: each subject resolves to an example object
   with that digest, the manifest digest is the manifest's, the envelope
   verifies under the fixture key. The same in the twin and the app. The
   example was wrong from before 1.0.0 because nothing checked it.
5. IFA, in phase C: move `objects/attestation/ifa-ato.json` beside the
   manifest and out of its object list (D3.1), and let it bind the real
   manifest digest. Today it digests "a deterministic mini-manifest"
   (**read**: the manifest's `attestation-note`).

Size: small to medium. Do it after B and C; both change the digests.

### 5.2 #64 — carry what the report claims

1. In `convert_ifa.py`, carry the component definition's
   `set-parameters` as `parameter-bindings` and its `statements[]` as
   `statement-ids` with their text. Both fit since rc.3, and the pack
   builder's OSCAL import already implements the mapping; the converter
   follows its rules.
2. Read the `source` of each control implementation and derive the
   namespace of `requirement-ref` from it. Today it is written as NIST's
   whatever the source says (**read**: line 253).
3. Replace the one regular expression that claims the whole
   `control-implementations[]` subtree by one claim per path, and let
   the value-arrival check fail the run when a claimed path did not
   arrive. This is the IFA slice of #41.

The sources are public and pinned (`usnistgov/oscal-content@9402f031`,
**read**: `SOURCE-LICENSE.md`). `raw.githubusercontent.com` answered
from this session (**measured**: one file at that commit, HTTP 200); the
directory layout the converter expects under `sources/nist` still has to
be rebuilt.

Size: medium, in phase C with the rest of the IFA work.

### 5.3 #58 — no culture comparison left in the twin

**Measured**: `validate_core.ps1` holds 201 uses of `-ceq`, `-cne` and
`-ccontains` on 180 lines, a few of them in comments. Many compare a type name the twin computed itself and
cannot go wrong. Sorting them into safe and unsafe is a judgement that
the next edit undoes.

1. Replace all of them by two ordinal helpers, an equality and a
   membership test. One rule, no exceptions to remember.
2. Add a step to the PowerShell job of the workflow that fails when the
   file contains one of the culture operators, so the class cannot
   return.
3. In the same pass, **check** two neighbours that were not examined for
   this plan: `switch` over data strings, and hashtable literals `@{}`
   keyed by data.
4. Vectors: two ids that differ by U+00AD, where the member reference
   must dangle; a `statement-id` that differs by a combining accent,
   where the operation must address a ghost statement.

Size: small to medium; mechanical, and CI runs it on Windows PowerShell
5.1.

### 5.4 #47b — close it with a rule and a test

No corpus holds either value (**read**: the backlog row). The
recommendation is to decide the behaviour now and test it on synthetic
input:

- `none` says no option was chosen. The converter writes no `treatment`;
  the Risk stays in the state its other fields allow. C.10 needs no
  code, because the absence of the field is that value.
- `contingency` gets no code. The response stays verbatim in the
  `risk-analysis@1` facet and the converter counts it, as it already
  counts any response type without a code.
- Two converter cases with a synthetic POA&M risk, one per value, so the
  behaviour is run and not only argued.
- C.10 says both in one paragraph. The row closes as decided: no fifth
  code without a counted instance (D22, test 3). It reopens on the first
  instance in a real corpus.

Size: small. It closes a row, so it needs the author's nod.

### 5.5 #45 — the missing vector

`reference-vectors.json` holds 13 vectors and none with ids that differ
only in case (**measured**). Add two:

- `ids-differing-in-case-are-two-objects`: `…/req/A` and `…/req/a` both
  exist, a Set names both, 0 errors.
- `member-ref-in-another-case-dangles`: only `…/req/a` exists, a Set
  names `…/req/A`, 1 error. This is the case the twin got wrong before
  #45 was closed.

Same commit as the vectors of §5.3. The totals quoted in the README, the
specification and the website's `facts.json` move with them.

## 6. Staying in the backlog, planned

### 6.1 #41 — value arrival for every corpus

1. Call `value_arrival()` from the library's report function, so every
   converter gets it without being edited one by one.
2. Tighten the measure first. It counts a value as arrived when it
   occurs anywhere in the emitted objects (**read**:
   `oscal_conv_lib.py`), so a short value such as `1` or `true` arrives
   by accident. Short values need the destination path, or a line that
   says they are not decidable this way.
3. For every absent content path: carry it, or declare it dropped with a
   reason in the converter's claim table. The run fails on an absent
   content path that is neither.
4. The five shipped corpora first, because the release's sentence is
   about what ships. The six whose bundles were removed for licence
   reasons follow; measuring them needs their sources on the machine,
   not in the repository.
5. Then re-word "converted losslessly" to what was measured: README,
   specification Status and IV.2, the website's facts.

Why it is large: IFA alone had 122 absent content paths, each a
decision. The four catalogue corpora are one document type each and
should be more regular; that is an expectation, not a count.

### 6.2 #55 — `Assessment.method` held to its schema

1. Re-measure before anything else. The row says the example's `summary`
   is a string; in today's tree it is a language map (**measured**), so
   at least one of its three findings has moved.
2. Treat the keys of `method` as facet ids and resolve them as `facets`
   are: stdlib, then pinned, then `private:`, else an error.
3. The same in the reference validator, the twin and the app.
4. Fix the payloads: the example, the sample in handbook 10.1, and the
   IFA Assessment with a real pinned schema in place of its stub. The
   IFA payload can be fixed in phase C while the converter is open; #55
   is then validators only.
5. Facet vectors: a valid method, an invalid one, an unregistered one.

Why it is not small: three implementations, one converter re-run, and a
change that turns bundles red that are green today, which belongs in the
release notes.

### 6.3 #62

Untouched, as decided. It becomes work when a runner exists.

## 7. Found on the way (not filed, not fixed)

More was found while building phase A; the register entry "Amendments —
the open backlog before 2.0.0" lists it.

- `Finding.actions[].status` is a free string; the corpus holds
  `planned`, `done` and `closed` (**measured**). An action also names
  nobody who is to carry it out.
- `Deviation.approver-ref` is required in every state, so a Deviation
  under investigation must already name its approver (**read**).
- The next decision number is D26 by count, and the register once used
  "D26" as a label for backlog #26 (P10 #33 e). The new decision needs a
  number the author is content with.
- The backlog file itself: its title says v0.6, its opening paragraphs
  are not in the order of the dates, and rows #63 to #66 stand below the
  standing rule that ends the file.

## 8. Phase A as built (2026-11-13)

The author's "start phase A" came with the three answers of §3.7. The
commits are on this branch; the register entry has the measurements.

| # | Built | Differs from the plan above |
|---|---|---|
| 54 | The record has a schema; the tool and the app (build 0.9.7) read and write it; the demo is rebuilt | No `catalog`, no `tailoring-ref`: the app keeps one file for all catalogues and nothing reads a scope, so a row names its entry by id and carries `entry-version`. No `review-due` yet: it follows the rule phase B gives a Deviation. A row without an author is reported, not refused, as answer 1 says. The tool refuses the old map; the app reads it |
| 47b | Decided as recommended; the mapping moved into the converter library, with four tests in the library's test file, which CI runs | The two synthetic cases were run once through the whole converter, on copies of the POA&M. Only the mapping is a repeatable test, because the converter runs only with its sources |
| 45 | Two vectors | none |
| 58 | No operator compares two strings; the lint parses the twin with PowerShell's parser | The class was about twice the size the row gave: `-eq`, `-ne` and `-contains` fold case as well, and they were the larger half. 371 comparisons changed, not 201. The lint is a PowerShell script in `.github/scripts/`, not a text search, and the ordering operators get a weaker test than equality. Four vectors, not two; three of the six failed on the twin before the change |

What phase A showed for the later phases:

- **The IFA sources are at hand.** The seven files are public at the
  pinned commit, and the unchanged converter reproduces the committed
  bundle and both reports byte for byte from them (**measured**). Phase
  C can run in a cloud session.
- **The twin can be run here.** PowerShell 7.4 on Linux with a stand-in
  for the one .NET Framework class gives the reference's counts in about
  a minute. It is not the proof: the first version of the lint ran green
  here and stopped on Windows PowerShell 5.1. The workflow's run stays
  the record.
- **Totals.** 543 vectors when phase A was built; 574 after the rebase
  onto main (§9). Phase B adds its own.

## 9. After the rebase onto main (2026-11-13)

While phase A was built, another session landed 29 commits on main. The
branch was rebased onto them; the register entry "The rebase onto main"
says what overlapped and how it was settled. For the plan above:

| Plan | Changed by main's work |
|---|---|
| §5.2, #64 | **Done by the other session.** The converter maps the component definition as the pack builder does. One point of §5.2 is not done and the row says so: `requirement-ref` is still written into the NIST namespace by rule |
| §6.1, #41 | **Begun.** The measure was wrong in the way step 2 suspected and is replaced: typed whole values (`global_occurrence`) and a ledger that traces every source value to where it went. The IFA corpus is accounted for value by value: 0 unaccounted, 0 failed checks (**measured** after the rebase). Three dangling references of the source are declared as source defects. The other ten converters have no ledger |
| §2, phase C | Shrinks to the IFA half of #46 (the attestation is still listed in its own manifest, **read**) and the IFA payload of #55, plus the authors phase B makes the converter write. The workflow now reproduces the IFA conversion from its pinned sources on every change, so any of these is a deliberate, visible change of the committed bundle |
| §3, phase B | NUMBER-1 landed (#67): a number in a bundle is an integer in plain digits. The shapes of §3.2 hold no number, so nothing changes. The conformance total phase B starts from is 574, and the app's build is 0.9.7 |
| §5.3, #58 | Applied again on main's twin after the rebase, by the same two scripts. Main's twin, unchanged, fails the same three vectors |

Open after the rebase: #41, #46, #55, #62, #65, #66.

## 10. Phase B as built (2026-11-13)

The author: "start phase B". The change proposal is
`drafts/CP-AUTHOR-1.md`; its §11 and the register entry "CP-AUTHOR-1
landed" hold the measurements. Against §3 of this plan:

| Plan, §3 | Built |
|---|---|
| §3.2, the model | As planned, with the three answers of §3.7. `provenance` on a Tailoring and its entries, a Risk and its ratings, an Implementation, a Finding; `decided` and `review-due` on a Deviation; `date` on an authorization; three times typed |
| §3.3, the rules | Four, not five: AUTHOR-1 (a consumer's Tailoring), AUTHOR-2 (Risk, Finding, Implementation), AUTHOR-3 (a decided Deviation), AUTHOR-4 (an authorization). The planned rule on `excludes[].rationale` was dropped: `risk-coverage` already reports it. All are report lines |
| §3.4, the review date | REVIEW-1 reads the date of the run and reports; `--as-of` sets the date. It also covers a Risk's `review-due`. The word is "overdue", because `risk-coverage` uses "lapsed" for something else |
| §3.5, what the landing touches | Schema, three validators, vectors, examples and texts are done. The tools that write the fields are not: backlog #69, which takes over the rest of this row and of phase C |
| §2, the workflow | **Read** from its logs: the twin on Windows PowerShell 5.1 at `82721959`, the lint and then 643 vectors in 18 families, the bundles, the pack and the example folder with the reference's counts and its 15 report lines, ALL GREEN in 213 s; the reference, the app's port and the pages green in the same run (43504417645) |

What phase B showed for what is left:

- **#68 is new and needs the author.** A value ending in a line break is
  a date for two validators and not for the third.
- **Phase C is now #69 with the IFA half of #46 and the IFA payload of
  #55.** One question in it is the author's: whether the IFA converter
  derives a record's author from the document's parties.
- **Counting values is not enough when a field is typed.** The CIS
  converter wrote a version into a field that now takes a date, and no
  value in the repository showed it. For #41 and #55 the same holds:
  look at the writers, not only at what they wrote here.

Open after phase B: #41, #46, #55, #62, #68, #69.

## 11. Phase C as built (2026-11-13 and 14)

The author: "#68 refuse", "all converters should pre-fil that data from
the source corpus but import tool should be able to overwrite it",
"keep", "go for phase C". The register entry "Phase C — the tools write
who decided; a line break ends no value" holds the measurements. Against
this plan:

| Plan | Built |
|---|---|
| §2, phase C: one IFA re-run with #64, the IFA half of #46, the IFA payload of #55 and the authors | One re-run. #64 was closed before it. The Attestation lies beside the manifest and binds it. The method payload already passed its pin (**measured**); the pin now says what an entry is. Authors: by rule from the source, which gives one of seven |
| §10, "#68 is new and needs the author" | Decided and closed in the same phase: specification D3.10, 22 vectors, both validators |
| §3.5, the tools that write the fields | Converters, the app (0.9.9), the risk-catalogue import and the reader (1.11.0). Two agents built the app's and the reader's part in worktrees; both were merged and run here |
| §3.5, "the pack builder is checked against AUTHOR-3" | Checked against all four: a pack holds Components only and the builder's form writes no authorizations, so no AUTHOR rule reaches what it writes (**measured** by the agent: no AUTHOR line for the worked pack) |

What phase C showed for what is left:

- **Phase D got larger by one sentence.** The check that keeps the
  example attestation real should read the Attestation beside every
  bundle's manifest, not only the example folder's: the IFA Attestation
  is checked by its converter and by no validator (#46).
- **Phase E got smaller.** #55 is the validators only: all three
  payloads pass their schemas today (**measured**).
- **A rule written twice needs a third reader.** The author rule in
  Python and in JavaScript passed the same table on both sides and
  differed on 41 of 4,000 generated documents. The kernel pin was written
  three times (validator, converter library, reader) and two of the
  copies knew two reasons. Where a rule lives in two languages, the test
  that counts is the one that puts both to the same generated input, or
  holds both to the same vectors.
- **New rows:** #70 needs the author (a placeholder party where the
  kernel requires one), #71 and #72 are work.

Open after phase C: #41, #46, #55, #62, #70, #71, #72.
