# Risk catalogues — ready-made lists of risks (prototype)

*State: 2026-11-13 · version 0.1.0, released 2026-11-10 · lifecycle `draft` ·
outside the JASCON kernel, by decision (backlog #53, closed 2026-11-10).*

A risk register usually starts from an empty spreadsheet. This directory
holds two published lists of typical risks and a tool that imports them into
JASCON `Risk` objects, so that a register starts from a reviewed list and
the organisation adds what only it can know: the owner, the level, the
decision.

| Catalogue | Entries | For |
|---|---|---|
| [`office-it/`](office-it/catalog.json) | 24 (`OFF-01` … `OFF-24`) | workstations, mail, file and collaboration services, a few servers, cloud subscriptions |
| [`industrial-plant/`](industrial-plant/catalog.json) | 23 (`ICS-01` … `ICS-23`) | controllers, operator stations, a plant network, links to office IT and suppliers |

Every entry is written in English and German.

**What these lists are not.** They were written by one author with AI
assistance and have not been reviewed by a second person or tested in an
audit. They are a starting list of typical scenarios, not a complete threat
model, and "not on this list" says nothing about a risk. Treat version 0.1.0
as a draft to correct.

## What an entry carries

```json
{ "id": "https://github.com/christoph-puppe/JASCON/risk-catalogs/industrial-plant/entry/ICS-02",
  "version": "0.1.0", "lifecycle": "draft", "label": "ICS-02",
  "title":    { "en": "A vendor's remote maintenance access is misused", "de": "…" },
  "scenario": { "en": "A machine builder reaches controllers through an always-on remote connection …", "de": "…" },
  "category": "third-party",
  "impacts":  [ "integrity", "availability" ],
  "suggested-treatments": [ { "requirement-ref": "https://ns.nist.gov/sp800-53/req/AC-17" }, … ] }
```

An entry has **no owner, no state, no rating and no acceptance**. Those
belong to the organisation, and they are exactly what the kernel `Risk`
requires, which is why an entry is not a `Risk`. The shape is
[`schema/risk-catalog.draft.schema.json`](schema/risk-catalog.draft.schema.json).

The catalogue itself (`catalog.json`) lists its entries and says who
publishes it and, since 2026-11-13, on which day this version was
published:

```json
{ "id": "https://github.com/christoph-puppe/JASCON/risk-catalogs/office-it",
  "version": "0.1.0", "released": "2026-11-10", "lifecycle": "draft",
  "publisher-ref": "https://github.com/christoph-puppe", … }
```

`released` is optional and a date (`YYYY-MM-DD`). Both shipped catalogues
state 2026-11-10, the day their header files were last changed. An import
reads the two fields as the author and the day of what it writes (below).

`suggested-treatments` name controls of NIST SP 800-53 Rev 5, because that
catalogue ships in this repository under public-domain terms and every
reference can be checked. All 105 distinct controls the two lists name
resolve in the shipped bundle (`validate --bundle`). They are suggestions:
the controls that typically treat the scenario, chosen by the author.

## Import is a copy

```bash
python3 risk-catalogs/tools/risk_catalog.py import risk-catalogs/office-it \
    --bundle <bundle-dir> --org https://your.example --owner https://your.example/party/ciso \
    --out <dir> [--tailoring <tailoring-id>] [--not-applicable <file.json>] \
    [--author-ref <party-uri>] [--date <YYYY-MM-DD>]
```

For every entry the tool writes one kernel `Risk`:

- under the organisation's own id, `state: identified`, `lifecycle: draft`,
  with the owner given on the command line;
- with the suggested treatments **the bundle actually selects**: through
  the named Tailoring, or all of them in a bundle without a Tailoring; the
  others are dropped and listed in the import report;
- with `tailoring-refs` naming that Tailoring;
- with a `relations` entry pointing back at the catalogue entry, and the
  catalogue version in `annotations`;
- with `provenance`, the kernel's field for who wrote a record and when
  (specification D26): the catalogue's `publisher-ref` and its `released`.

**Who and when can be overwritten.** `--author-ref` and `--date` replace
what the catalogue states, each on its own: `--author-ref
https://your.example/party/ciso` alone keeps the catalogue's day. An empty
value says "nobody" or "no day" (`--author-ref ""`). A Risk gets
`provenance` only when both an author and a day are known. Where one is
missing nothing is made up for it: the Risks are written without, the tool
prints how many, and the import report lists them under
`without-provenance`. A `--date` that is not a date stops the import before
anything is written. The report's `provenance` says what the catalogue
stated, what was given, and how many Risks got their author from which.

What the default means: an imported Risk names the catalogue's publisher as
its author, because the scenario and the suggested controls are the
publisher's text. The organisation has decided nothing yet. Once it
assesses the risk it writes a new version, and that version is its own; the
app's Risk page then writes the author on the Risk and on the rating.

Nothing references an entry at run time. A new catalogue version cannot
change a risk the organisation already owns; it can only be compared with
it.

Two more commands: `validate <catalog-dir> [--bundle DIR]` checks the
catalogue against its schema and its suggestions against a bundle;
`completeness <catalog-dir> --risks DIR [--not-applicable FILE]` lists the
entries that no Risk instantiates and no recorded decision excludes.

## The record of entries that do not apply

Not importing an entry is a decision, and the record says who made it:

```json
{ "record-version": 1,
  "entries": [
    { "entry": "https://github.com/christoph-puppe/JASCON/risk-catalogs/office-it/entry/OFF-23",
      "entry-version": "0.1.0",
      "rationale": { "en": "Public AI services are blocked at the web proxy and no licence for one exists." },
      "provenance": { "author-ref": "https://org.example/party/ciso", "date": "2026-11-10" } } ] }
```

Its shape is `schema/not-applicable.draft.schema.json`. `entry` is the
entry's id, so one file serves every catalogue. `entry-version` is the
version that was judged; a later version of the entry is a reason to look
again. `provenance` is spelled as on a kernel Mapping and Check. A row
without it is accepted and reported: `completeness` prints `[no author
recorded]` beside it and counts such rows in a note. A row that names no
entry of the catalogue is reported too, since a misspelled id would
otherwise pass in silence. The tool refuses a file that does not fit the
schema and a file that decides one entry twice.

The record has no `review-due`. The kernel has one on a Deviation since
release candidate 4, with the rule that reports a review date that has
passed (specification D26, REVIEW-1; backlog #65, closed). The record has
not taken the field over.

## The demo, measured

`tools/build_demo.py` builds a complete bundle: the shipped SP 800-53
bundle, an organisation's Tailoring that selects the MODERATE baseline, the
office-IT catalogue imported against it with one entry recorded as not
applicable, and two risks assessed by hand to stand in for the
organisation's work.

Who decided what in the demo: the 21 risks that are only imported name the
catalogue's publisher and 2026-11-10, as the import writes them. The
Tailoring and the two assessed risks, with their ratings, name the
organisation's CISO. The organisation, its CISO and the two days
(2026-11-10 and 2026-11-12) are fixed in `build_demo.py` so that the demo
is the same on every run; nobody assessed anything.

```bash
python3 risk-catalogs/tools/build_demo.py /tmp/demo-bundle
```

```bash
python3 jascon/scripts/validate_core.py /tmp/demo-bundle
```

The bundle is not committed (about 7 MB). What the import produced is, in
[`demo/office-it-moderate/`](demo/office-it-moderate/): 23 Risk objects,
the Tailoring, the not-applicable record and the import report.

| Measured on the demo | |
|---|---|
| Reference validator on the bundle | 1,065 pass, 0 fail (1,014 requirements, 25 sets, 1 component, 1 Tailoring, 23 Risks) |
| The same with `--require-authors --as-of 2026-11-13` | 1,065 pass, 0 fail: no AUTHOR line, no review date asked |
| Risks by the author they name | 21 the catalogue's publisher, 2 the organisation's CISO, 0 nobody |
| Catalogue entries | 24: 23 imported, 1 recorded as not applicable |
| Suggested treatments dropped because MODERATE does not select them | 5, on 2 risks (`CM-14`; four privacy controls) |
| Requirements selected by the Tailoring | 287 |
| … justified by a Risk | 13 — the controls of the two risks that were assessed |
| … named only by a Risk still `identified` (pending) | 65 |
| … named by no entry at all | 209 |
| Completeness against the catalogue | 0 gaps with the not-applicable record, 1 without |

## What the prototype shows

1. **Import needs no kernel change.** `Risk`, `relations`, `annotations`
   and `tailoring-refs` are enough to copy an entry and to point back at
   it. A kernel type for the *entry* is only needed if catalogues are to be
   bundle objects themselves: digested, attestable, and a typed target for
   the back-reference. **Decided 2026-11-10: they are not.** Catalogues
   stay outside the kernel; 2.0.0 gets no entry type (backlog #53).
2. **"Not applicable" has no home.** The reason for not importing an entry
   lives in a side file here. Without it, the completeness check cannot
   tell a decision from a gap. A Tailoring records the same thing for
   requirements (`excludes[].rationale`); nothing does for risks. With
   catalogues outside the kernel the record stays a side file. **Defined
   2026-11-13** (backlog #54, closed): see "The record of entries that do
   not apply" above.
3. **A risk list does not justify a baseline.** 24 entries name 78 of 287
   selected controls. Under a policy that demands a risk basis for every
   control (`--require-risk-basis`), 209 stay uncovered however carefully
   the list is worked through. Either the list grows, or the baseline is
   justified as a baseline.
4. **Imported is not justified.** An imported risk is `identified`, so it
   justifies nothing until the organisation assesses it and chooses an
   option. The import fills the register; it does not do the analysis.
5. **Suggestions are bound to one framework.** They name SP 800-53
   controls. For another catalogue they have to be translated, which is
   what `Mapping` objects are for. Not built here.

## Scales to start from

[`scales/`](scales/) holds three starting scales — likelihood, impact and
risk level, three levels each, German codes with English labels. They are
there to be changed: copy a file, reword the levels, add or remove some,
give it your own id and version, and pin it in your bundle's manifest
under `scales`. The validator then checks every level your risks state
against your definition. The risk-level scale also carries a starting
matrix over the other two; a rating that states likelihood and impact
must then state the level the matrix gives, or say why not. Change the
cells as freely as the levels. The demo pins the three files as
published.

## Limits

- Content: one author, no second review, no audit use (above).
- No threat references: the entries carry no MITRE ATT&CK or other threat
  ids, because none were verified.
- Suggestions go down to the control, never to the statement.
- The tool resolves `set-ref` selections only and refuses a Tailoring with
  a predicate select.
- The reader does not import catalogues.
- The PowerShell validator has no part in this prototype.

## Layout

```
risk-catalogs/
  office-it/          catalog.json, entries/OFF-*.json
  industrial-plant/   catalog.json, entries/ICS-*.json
  scales/             likelihood-3.json, impact-3.json, risk-level-3.json
  schema/             risk-catalog.draft.schema.json
  tools/              risk_catalog.py, build_demo.py
  demo/office-it-moderate/   the import result of the demo
```

Licence: Apache-2.0, like the rest of the original work in this
repository.
