# CP-AUTHOR-1 — Who decided, when, and until when

**Change proposal · JASCON kernel 2.0.0-rc.3 → 2.0.0 · 2026-11-13**
**Process:** Chapter 15.4 (evidence in, corpus first, implementations follow). Every rule carries a machine id, a rationale and a message that prints.
**Scope:** kernel schema (optional fields on five types and one sub-object, three typed time fields), reference validator, conformance corpus, the example folder, the PowerShell twin, the app's port. Tools that write the new fields, the specification as 2.0.0-rc.4, handbook, website: §9.
**Status: LANDED on 2026-11-13 as specification D26 in release candidate 2.0.0-rc.4; 2.0.0 is not tagged.** Backlog #65 and #66 are closed. The three main points were accepted by the author before this text was written. The points this text adds on its own are listed in §10; they are built as proposed and remain the author's to overturn. §11 says what was built and what building it changed. Where §11 and an earlier section differ, §11 is the state.

**Author statements this proposal implements (2026-11-13):**
(1) "#65 stays optional, fix it."
(2) "#66 need the author! we need authors for every part where a decision is made, a check done, a risk changed etc! fix it."
(3) On the three points `drafts/pre-2.0.0-fix-plan.md` §3.7 left open: "1 report, 2 provenance, 3 read the clock then report."

Every count below is marked **measured** (a script run on this tree), **read** (from a file) or **argued**.

---

## 1. The gap, in one sentence

The kernel records a weakening, a selection, a risk level, an implementation status and an authorization without saying who decided it or when, and an approved exception without saying until when it holds.

## 2. The counts

### 2.1 Where the kernel records who and when today

**Measured** on `jascon/schemas/jascon-2.0.0.schema.json`:

| Record | Who | When | Missing |
|---|---|---|---|
| Tailoring as a whole | none | none | both |
| A select, an exclude, an operation | none | none | both |
| Deviation | `approver-ref` | `opened` | when it was decided; until when it holds |
| Risk as a whole | `owner-ref` | none | who wrote this version, and when |
| Risk `rating`, `residual-rating` | none | none | both |
| Risk `acceptance` | `approver-ref` | `date` | nothing |
| Implementation | none | none | both |
| Finding | through `assessment-ref` | none | who changed its state, and when |
| Component authorization | `authority-ref` | none | when |
| Assessment | `performer-ref` | `time`, any string | a typed time |
| Mapping | `provenance.author-ref` | `provenance.date`, any string | a typed date |
| Check | `provenance.author-ref` | `provenance.date`, typed | nothing |
| Attestation | `signer` | `timestamp`, any string | a typed time |
| Requirement, RequirementSet | the publisher, by the origin of the id | `version` | nothing proposed |

Five spellings of "who and when", and six records with neither.

### 2.2 What the repository holds

**Measured** over the conformance vectors, the example folder, the five shipped bundles, the worked pack, the catalogue demo and the tests' fixtures:

- `Assessment.time`: 53 values, 4 dates and 49 date-times. `Attestation.timestamp`: 19 values, 2 dates and 17 date-times. `Mapping.provenance.date`: 3 values, all dates. None is free text.
- Records the rules of §5 speak about, in what ships: the example folder holds 2 Tailorings (2 selects, 3 operations), 1 Risk, 2 Findings, 2 Implementations and 1 Deviation; the IFA bundle 2 Risks, 2 Findings, 3 Implementations and 1 Deviation. The four catalogue bundles hold none.

### 2.3 Not measured

No corpus of consumer Tailorings with authors exists in the repository. How many of the IFA source's own statements of who and when (document metadata, responsible parties, origins) can become `provenance` is counted when the converter is changed (§9), not here.

## 3. What goes where

| Question | Answer | Why not the alternative |
|---|---|---|
| One spelling or several? | One: `provenance: {author-ref, date}`, the shape a Mapping and a Check carry | A sixth spelling for the same two facts |
| On the record or on each decision? | Both. The record names who wrote this version; a decision inside it may name its own author and otherwise has the record's | Only on the record: two people's decisions in one Tailoring cannot be told apart. Only on each decision: a Tailoring by one person repeats that person on every line |
| A history inside the object? | No. A change is a new version; who changed it is that version's `provenance` | OSCAL's `risk-log`: a second history inside each version can contradict the first |
| A party type? | No. `author-ref` is a URI, compared and never resolved (D2) | #16: parties are landmarks; 0 of 3 census corpora publish party objects |
| Required? | Optional in the schema. The validators report what is missing | A catalogue authority's Tailoring needs none of it |

An author field is a claim inside the object. It is part of the semantic digest (**read**: the canonical form drops `annotations` and nothing else), so an Attestation over a Tailoring binds the claim. Proof of who signed stays the signature.

## 4. The shapes

All additions are optional. `provenance` is closed: `author-ref` (a URI) and `date` (`YYYY-MM-DD`), both required when it is present.

| # | Where | Field | Type |
|---|---|---|---|
| S1 | `$defs` | `provenance` | `{author-ref, date}`; `Mapping.provenance` refers to it |
| S2 | Tailoring; each `selects[]`, `excludes[]`, `operations[]` entry | `provenance` | S1 |
| S3 | Deviation | `decided` | date: the day it was approved or withdrawn |
| S3 | Deviation | `review-due` | as `Risk.review-due`: date, date-time, elapsed duration, or calendar period with its calendar |
| S4 | Risk; `rating`, `residual-rating` | `provenance` | S1 |
| S5 | Implementation, Finding | `provenance` | S1 |
| S6 | Component `authorizations[]` entry | `date` | date |
| S7 | `Assessment.time`, `Attestation.timestamp` | (typed) | a date or an RFC 3339 date-time with an offset |

```json
{ "id": "https://cso.example/tailoring/linux-prod", "version": "3", "lifecycle": "active",
  "provenance": { "author-ref": "https://cso.example/party/ciso", "date": "2026-11-05" },
  "selects": [ { "set-ref": "https://cso.example/set/linux" } ],
  "operations": [
    { "op": "set-parameter", "requirement-ref": "https://cso.example/req/LNX-SSH-1",
      "statement-id": "s1", "parameter": "max-auth-tries", "value": 3 },
    { "op": "set-modality", "requirement-ref": "https://cso.example/req/LNX-SSH-1",
      "statement-id": "s2", "modality": "should",
      "provenance": { "author-ref": "https://cso.example/party/head-of-ops", "date": "2026-11-12" },
      "deviation": { "type": "operational-requirement", "state": "approved",
                     "rationale": { "en": "The legacy jump host cannot negotiate the cipher." },
                     "approver-ref": "https://cso.example/party/ciso",
                     "opened": "2026-11-10", "decided": "2026-11-12",
                     "review-due": { "type": "date", "value": "2027-05-12" } } } ] }
```

The first operation was decided by the CISO on 5 November, as the Tailoring says. The second names its own author. The Deviation says who approved it, when, and when it is due for review.

**Who decided an entry** is therefore a function of the object alone: the entry's `provenance`, else the Tailoring's, else nobody. The same holds for a rating and its Risk.

**S7 and the date of S1 on a Mapping are tightenings**, not additions. D8 says of a date that any string satisfies that it "cannot be compared, sorted or checked", and already names `provenance.date` among the typed ones; for a Mapping it was not (**read**). All 75 values of §2.2 conform.

## 5. The rules

A missing author fails nothing (author, point 1). The validator prints one line per object and rule, and `--require-authors` turns the lines into failures, as `--require-risk-basis` does for uncovered requirements.

| Rule | Reported when | Rationale |
|---|---|---|
| AUTHOR-1 | a Tailoring at consumer tier has a select, an exclude or an operation without an author: no `provenance` of its own and none on the Tailoring | the consumer's decisions are the ones nobody else can attribute; an authority's Tailoring is attributed by its origin and its Attestation (D13: duties bind at consumer tier) |
| AUTHOR-2 | a Risk, a Finding or an Implementation carries no `provenance` | each records a judgement: a level, a state, a status |
| AUTHOR-3 | a Deviation in state `approved` or `withdrawn` carries no `decided` | `opened` is when it was asked for |
| AUTHOR-4 | a Component authorization carries no `date` | it names the authority and not the day |
| REVIEW-1 | the `review-due` of an approved Deviation, or of a Risk that is still managed, has passed | the date exists to be looked at |
| DATE-3, DATE-4, DATE-5 | (names only) `Mapping.provenance.date`, `Assessment.time`, `Attestation.timestamp` are not of their type | as DATE-1 and DATE-2: the schema refuses, the validator names the reason |

**REVIEW-1 in full** (author, point 3: "read the clock then report").

- The validator reads the date of the run, in UTC. `--as-of YYYY-MM-DD` sets the date instead; the conformance vectors use it, so that they give the same answer every day.
- A point in time has passed when its UTC calendar day is before that date. Due today is not overdue.
- A duration counts from `decided`, else `opened`, on a Deviation; from `acceptance.date` on a Risk. An elapsed duration is added to the start of that day in UTC. Without the starting date the line says "not evaluable".
- A calendar period is not evaluated: the tool has no calendar (D9: fail-closed without the named calendar). The line says so and names the calendar.
- REVIEW-1 never fails a bundle, with or without `--require-authors`. A Deviation past its review keeps licensing its weakening until someone acts; the report is how someone finds out.
- The word is "overdue". `risk-coverage` already uses "lapsed" for a requirement named only by retired risks.

**The kernel pin.** A bundle that uses a field of S2 to S6 needs `kernel-version: 2.0.0` (KERNEL-1): a 1.0.0 tool would refuse the object as matching no type.

## 6. No new type, no new primitive

Five types and one sub-object gain optional fields. The report is computed by the validator from fields alone; it resolves nothing and applies nothing, so it is not a primitive of Appendix B.

## 7. Semver: rides 2.0.0

2.0.0 is not tagged. The additions are optional, so every rc.3 bundle that does not use them is unchanged. The three tightenings refuse what rc.3 accepted: free text in `Mapping.provenance.date`, `Assessment.time` or `Attestation.timestamp`. Nothing in the repository holds such a value (§2.2). The candidate after the landing is 2.0.0-rc.4.

## 8. D22

D22 governs types. For fields on existing types the register has a precedent, "D22 — two fields on the author's word" (CP-ADVICE-1), and this proposal follows it: the fields enter on the author's decision, and the register names what was read.

- **Read in the repository:** `convert_ifa.py` carries the `origin` actors of an OSCAL risk characterization and reads `metadata.responsible-parties`; OSCAL states who per item in its assessment layer and per document everywhere.
- **Read for the backlog rows, not again for this text:** CISO Assistant's `expiration_date` on a security exception and its change log per assessment, at a named commit.
- **From memory, to be read against the published texts before the register entry:** ISO/IEC 27001:2022 clause 7.5.2 (identification of documented information, for example by title, date and author) and clause 6.1.3 f (the risk owners' approval); OSCAL's `risk-log` entries with `logged-by`.
- **Not counted:** authored consumer Tailorings. None exists here.

## 9. What ships, what follows

| Step | What | State |
|---|---|---|
| 1 | Schema, reference validator, the vectors, the example folder | this landing |
| 2 | PowerShell twin, the app's port of the rules | this landing; run on Windows PowerShell 5.1 by the workflow (§11) |
| 3 | Specification 2.0.0-rc.4, handbook, website, README, register, backlog | this landing |
| 4 | Tools that write the fields: the app's pages (a "who am I" setting), the reader's display, the catalogue import, the IFA converter | follows; until then the IFA bundle and the catalogue demo show AUTHOR lines, which is what the rule is for |

## 10. Points this text adds on its own

Built as proposed; each is the author's to overturn before the tag.

1. **REVIEW-1 covers a Risk's `review-due` too.** The author's point 3 was about the Deviation. The field is the same on both, and the plan promised both the same sentence. The IFA bundle's two Risks carry deadlines of 2023 and will be reported.
2. **The three time fields are typed (S7, and the Mapping's date).** In the accepted plan (§3.2, item 5); stated here because it refuses what rc.3 accepted.
3. **AUTHOR-4**, the date of an authorization.
4. **No rule on `excludes[].rationale`.** The backlog row asked whether it becomes required. It stays optional; `risk-coverage` already reports an exclude without one at consumer tier.
5. **No requester on a Deviation, no performer per check result row, no log.** A Deviation's request is not a decision; a run by someone else is another Assessment; the history is the versions.
6. **An entry without `provenance` has its record's.** The alternative, every entry names its author, repeats one name down a Tailoring.
7. **The decision's number.** D26 by count. The register once used "D26" as a label for backlog #26 (P10 #33 e); the specification never did.

## 11. Landing addendum (2026-11-13) — what was built, and what contact with the repository changed

### 11.1 What is in the repository

| Step of §9 | Built | Measured |
|---|---|---|
| 1 | Schema, reference, vectors, the example folder | 63 new vectors at the landing (34 in the new family `author`, 29 in `kernel`). All expectations were written before the first run, which passed all 63. 19 deliberate defects in the reference's new code each turn a vector red. Six more vectors followed the ports (§11.2): 40 in `author`, 643 in all in 18 families |
| 2 | The PowerShell twin and the app's port (build 0.9.8) | Both give the reference's counts per family and per bundle and its report lines for the example folder and the IFA bundle. The twin was run on PowerShell 7.4 here, and by the workflow on Windows PowerShell 5.1: 637 vectors at `e4031a84` in 218 s, 643 at `82721959` in 213 s, ALL GREEN both times with the reference's counts and report lines |
| 3 | Specification 2.0.0-rc.4 (D26; D8, D13, D23 amended), handbook (appendix A, chapters 6, 10, 12, F.10), the skill (requirement 9c), PRIOR-ART, README, the website in five languages, register, backlog | |
| 4 | Not built: no tool writes the fields | backlog #69 |

### 11.2 What contact with the repository changed

- **A writer the count had missed.** §2.2 counted the values the repository holds and found none to change. `convert_cis_benchmark.py` and the app's CIS preset wrote the catalogue's version as the `provenance.date` of a Mapping; the repository holds no CIS bundle, so no such value was counted. Both now write the day of the catalogue's `last-modified`. A count of values answers "what is there"; a typed field also needs "who writes it".
- **A line break at the end of a value.** `$` in a pattern matches before a final line break in Python and in .NET and not in JavaScript, so the reference and the twin accept `"2026-11-13\n"` as a date and the app does not. This is older than the proposal and reaches every pattern that ends in `$`. Filed as backlog #68; the author's to decide.
- **Four defects no vector caught.** The twin's port was tested with 37 deliberate defects; four left every vector green: a second counted as a minute, a minute as an hour, a duration rounded up to the next day, and a vector case with an untyped object. No vector used seconds or minutes, and every duration ended at midnight. Five review vectors and one author vector were added; the first three defects now turn one red each in the reference (the fourth is a guard of the runner, not a rule).
- **The order of the report.** The vectors said "in the order of the ids, compared as strings". Python orders strings by code point, .NET and JavaScript by UTF-16 code unit; the two differ for characters beyond U+FFFF. The reports now follow the canonical form (RFC 8785), by code unit, in all three; the reference was changed, and two vectors hold it.
- **`--as-of`** accepted `20261113` and `2026-W46-5` in the reference, on Python 3.11 and later. It takes `YYYY-MM-DD` only now, as the twin and the app do.
- **§5 on the website.** The first English text said neither report fails a bundle unless the caller asks. REVIEW-1 never fails. The translating agent caught it.
- **§8, the citations.** OSCAL's `risk-log` with `logged-by`, its `origin` with actors and its `deadline` were read in the 1.1.3 metaschema. ISO/IEC 27001 was not read and stays from memory.

### 11.3 What does not exist

- A tool that writes `provenance`, `decided`, `review-due` or an authorization's `date` (#69). The example folder was given its authors by hand.
- A page of the app that shows the two reports. The rules compute them.
- A corpus of authored consumer Tailorings.
- Authors in the IFA bundle: it shows 10 AUTHOR lines and 2 overdue reviews. Its sources state the day of two authorizations and, per document, responsible parties and a last-modified date; they name no author per implementation, finding or risk. Whether the converter derives one from the document's parties is the author's to decide.
