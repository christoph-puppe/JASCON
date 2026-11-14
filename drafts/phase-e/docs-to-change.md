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
| `converted_examples/DE.BSI/SOURCE-LICENSE.md:24`, `oscal-export/geman.bsi-catalog.json` | describes the export of an earlier day; an older file the export script does not write | Backlog #90 |
| `.github/workflows/validators.yml` | no step runs the OSCAL export | Backlog #90 |

## Decisions the texts wait for

Backlog #80 to #85, each with numbers and a proposal: a source
document's metadata and the manifest's provenance; an object's own
change record; the resources texts refer to; `assessment-for`; labels of
statements and parameters; what a Set stands for. When one is decided,
the specification's kernel text, the handbook's appendix A and the
converters change with it.
