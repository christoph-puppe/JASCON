# What phase E made wrong in the texts, and what became of it

Kept at the author's request (2026-11-14): "always have in mind we need
that on README, specification, handbook, website, maybe keep a list of
things to change there?" The list was worked through once, at the end of
phase E, as agreed. This is its closing state; the list as it grew is in
the history of this file.

## Done (each in the commit named)

| Where | What | Commit |
|---|---|---|
| Website, five languages: evidence, home, model pages; `build.py`; `facts.json` | Five ledger outcomes and the sentence on what holds now; the limit on backlog 46 and 55 removed (both closed); `statements` argued from addressing; facts measured again | ce74e1bb |
| README | Headline and release note on the ledgers; corpus rows (ISM, Grundschutz++, SP 800-53, CSF); statement counts; the reader's export line; the app's SP 800-53 rules; the reader's screenshot (1.16.0) | f027fcd3 |
| Handbook chapters 1, 2, 3, 4.1, 5, 14; appendices A, D.10, E.1, E.3, F; `jascon/SKILL.md` | The statement layer; nested controls; draft may be used voluntarily; "real content is never dropped" in place of "drop by class"; the CR26 playbook; the compat facet's one schema | d6419edb |
| Specification rc.4 | The convergence row on clause granularity; the Risk row's count; D17; R16; IV.5b (export), IV.6 (one row), IV.7 (objects, converters), IV.9 (what is left) | 47fccc86 |
| Register, plan, backlog, twin header | "Phase E"; section 14; #41 and #55 closed, #80 to #92 filed; the twin's runs on Windows PowerShell 5.1 | d9e56477, 87cf7698 |
| App texts (readme, import page in English and German, PROGRESS, ERRATA) | With the presets, builds 0.9.14 to 0.9.16 | d5b3ced4, 5366da04, 7450c627 |
| `SKILL_jascon.zip` | Rebuilt from the committed `jascon/` tree | with this file |

## Left, and why

| Where | What | Why it is left |
|---|---|---|
| README, the gate records (about lines 386 to 440) | "6,914 objects across all eleven bundles", "Current totals: 4,583 Requirements · 1,066 Sets …", "5,886/5,886 objects round-trip", "Converters for all eleven corpora" | Dated measurements of 1.0.0, some in the present tense. Wrong before phase E; they belong to the clean-up the author named (E16) |
| README, the history bullets of rc.1 to rc.4 | versions of the app and the reader at earlier dates (0.9.11, 0.9.12, 1.14.0) | Dated records of those days |
| Website, "The 1.0.0 measurement, 22 July 2026" | Eleven bundles, 6,914 objects, 5,886 round-trip, sizes against the sources (ISM 29 % smaller, CR26 55 % larger) | A dated block; the sizes were not measured again after phase E (the ISM bundle grew from 2.1 to 2.6 MB of objects by its agent's count) |
| README:407, specification IV.1 | "ISM −29 %, GS++ −50 %, CR26 +55 %" | As above: the 1.0.0 measurement, not repeated |
| Specification D12's summary and Part III | "ISM = zero facets" | Speaks of the example and of what the kernel needs, not of the conversion; the handbook's E.3 and F say what the conversion writes |
| Specification, older versions (`jascon-specification-1.0.0.md`, `jascon-v0.5-specification.md`) | The clause-granularity row with "347 nested pseudo-controls" | Released or superseded texts; not rewritten |
| `drafts/gate-3-census.md`, `drafts/gate-4-measurement.md`, `DEEP_RESEARCH_REVIEW.md` | "tombstone inversion", "ISM round-trips 1,711/1,711", nested controls as statements | Records of their day |
| `website/src/start.html:108` | "what OSCAL cannot hold returns on import" | Wrong before phase E if it means the app's Import page (reported by the app's agent); not checked by me |
| `converted_examples/DE.BSI/oscal-export/geman.bsi-catalog.json`, `.github/workflows/validators.yml` | an older file the export script does not write; no step ran the OSCAL export | Done on 2026-11-14 (f54df1aa, backlog #90): the file is removed and a step runs the export. `SOURCE-LICENSE.md:24` says "`oscal-export/` is a re-export of the converted bundle to OSCAL 1.2.2", which holds |

## Decisions the texts wait for

Backlog #80 to #85, each with numbers and a proposal: a source
document's metadata and the manifest's provenance; an object's own
change record; the resources texts refer to; `assessment-for`; labels of
statements and parameters; what a Set stands for. When one is decided,
the specification's kernel text, the handbook's appendix A and the
converters change with it.

## The round after phase E (2026-11-14: backlog #86, #87, #90, #92)

| Where | What | Commit |
|---|---|---|
| README | 709 vectors in 18 families (twice); the reader's version in the caption (1.17.0) and its screenshot; what the reader checks of an export and of a loaded bundle | 1d276fe5, and the commit of this file |
| `jascon/SKILL.md` | 709 vectors; the lifecycle family names the report of draft members | the commit of this file |
| Handbook §3.6 and chapter 12 | DRAFT-1: a validator says where a Set in force lists a draft, and fails nothing | the commit of this file |
| Specification IV.5 (the record of the vectors), IV.6 (one row) | 709 vectors; DRAFT-1 | the commit of this file |
| App `readme.md`, `PROGRESS.md` | builds 0.9.17 and 0.9.18 | fa7a7b8f, 4a30d80b |
| Website `facts.json` and the five languages | measured again after the commit of this file | the commit after it |
| `SKILL_jascon.zip` | rebuilt from the committed `jascon/` tree | with the website's commit |

Left: handbook §3.6 says that new references to a withdrawn object fail
validation; no validator has that rule (backlog #93, needs the author).
The texts for #80 to #84 are written when those are built.

## The kernel round (2026-11-14: backlog #80 to #84, #88, #91; specification D27)

| Where | What | State |
|---|---|---|
| Specification | D27 new; D26 moved into Part II and its sentence on a log inside an object withdrawn; pointers in D9, D10, D12; the banner; IV.5b (753 vectors), IV.6 (one row), IV.9 | done |
| Handbook | chapter 2 (version and history), 3.3 rewritten, 12 (HISTORY-1, DATE-6, the statement-id rule, library versions), 14.2 and 14.4, appendix A (`history`, a statement's `label`, `provenance.sources`), D.6 (1.1.0), D.6a (`references@1`), D.10 (compat 1.2.0), E.3, F | done |
| README | 753 vectors; the ledger sums (71,212 copied, 51,605 by rule, 91,548 no content); a note on the round; the ISM and SP 800-53 rows; the reader's version and screenshot | done |
| `jascon/SKILL.md` | counts; requirements 2, 3 and 13 | done |
| App `readme.md`, `PROGRESS.md` | build 0.9.19 | done |
| Website `facts.json` | measured after the commits of the round | with the last commit |
| Register, backlog, plan, decisions, twin header | "After phase E"; #80 to #94; section 15; the author's answers and what was built otherwise | done |

The website's model page said that `version` and the two digests carry
the history; it says now, in the five languages, that `version` is the
object's own version and `history` its publisher's record of its
changes (the four translations checked for structure and stamped).

Left: handbook 3.6 on references to a withdrawn object (#93) and the
example folder's `gspp-taxonomy` schema (#94), both for the author. The
website's other pages say nothing of labels or sources beyond the
numbers they print.

## What `#id` names, and what may lean on a withdrawn object (2026-11-14, later: backlog #82 and #93)

| Where | What | State |
|---|---|---|
| Specification | D9 (what `#id` names); D27 point 4 rewritten and point 7 new, its heading and evidence tier; the banner; IV.5b (783 vectors), IV.6 (one row), IV.9 | done |
| Handbook | 3.6 (what "new" means for a validator, what is held and what keeps the record), chapter 12 (WITHDRAWN-1 with its table of edges, FRAGMENT-1), appendix A (`lifecycle`), C.2 | done |
| README | 783 vectors; a note on the two rules; the reader's version and screenshot | done |
| `jascon/SKILL.md` | 783 vectors; the two rules named in the families | done |
| App `readme.md`, `PROGRESS.md` | build 0.9.20 | done |
| Website `facts.json` | measured after the commits | with the last commit |
| Register, backlog, plan, decisions, twin header | the author's four answers; #82 and #93 closed; #94 measured; what was built otherwise | done |

The website's pages name neither rule; they print the numbers of
`facts.json`.

Left: the example folder's `gspp-taxonomy` schema (#94), with a
proposal, and #89, both for the author.

## Grundschutz++ on the catalogue of 2026-10-29, one taxonomy schema, the place check (2026-11-14, last round: backlog #89 and #94)

| Where | What | State |
|---|---|---|
| Specification | IV.6 (one row), IV.9; the counts in I (251,681 leaf values), IV.2 (214,455), IV.5b and IV.7 (4,467 exported objects, 1,289) | done |
| Handbook | 7.3 rewritten around the pinned descriptor and the payload by statement, with what the hand-written one had wrong; 11 and 13 (the pin's version and path); 14 (the ledger sum); appendix D (the sample) | done |
| README | the Grundschutz++ row (v2026-10-29; 1,000 Requirements, 224 parameters, 289 Sets, 49,521 values); the ledger sums; the leaf-value total | done |
| `jascon/SKILL.md`, `jascon/examples/README_1.md` | the schema file's name | done |
| App `readme.md`, `PROGRESS.md` | build 0.9.21 (the agent's commit) | done |
| Website | the first page's code sample and the evidence page's leaf-value total, five languages, stamped; `facts.json` measured after the commits | done, the facts with the last commit |
| Register, backlog, plan, decisions | the author's five answers; #89 and #94 closed; #95 filed; what was built otherwise | done |

#95, the two findings filed with it, is built since 2026-11-15 (two converters, their tests, the backlog, the register); no text of the specification or the handbook speaks of either.

## Before the tag (2026-11-15: backlog #72, #79 and #71 in part)

| Where | What | State |
|---|---|---|
| Specification | the banner (one sentence); D3.5 (a pin's version is three numbers of the number domain); IV.5b (785 vectors); IV.6 (one row); IV.9 | done |
| Handbook | no text speaks of a pin version's numbers, of the CR26 converter's arguments or of the reader's resolved preview | nothing to change |
| README | the vector count (785), the reader's version under the screenshot | done |
| `jascon/SKILL.md` | the vector count | done |
| `validate_core.ps1` | the header's note on `Semver` and the run of 2026-11-15 | done |
| App `PROGRESS.md` | build 0.9.22 | done |
| Reader | 1.20.0; the screenshot in `docs/img/` taken again | done |
| Website | `facts.json` measured after the commits | done with the last commit |
| Register, backlog, plan, decisions | the author's word; #72 closed; #79 and #71 in part; #96 filed | done |

## OPERATION-1 and the reader's resolved scope (2026-11-15: backlog #96 and #71 points 13 and 14)

| Where | What | State |
|---|---|---|
| Specification | the banner; D13 (an operation names what it changes); IV.5b (800 vectors); IV.6 (one row); IV.9 | done |
| Handbook | 6.2 (which operations carry a `statement-id`); appendix A (the sentence it had, and who holds it); chapter 12 (the rule for an implementer, the vectors) | done |
| README | the vector count (800), one entry in the list of what was decided, the reader's version | done |
| `jascon/SKILL.md` | the vector count and the rule's name | done |
| `validate_core.py`, `validate_core.ps1` | the header's entry on the rule | done |
| App `readme.md`, `PROGRESS.md` | build 0.9.23 | done |
| Reader | 1.21.0; the screenshot in `docs/img/` taken again | done |
| Website | no page names the rules; `facts.json` measured after the commits | done with the last commit |
| Register, backlog, plan, decisions | the author's word; #96 closed; #71 points 13 and 14 | done |
