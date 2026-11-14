# CR26 -> Semantic Core: Coverage Report (computed)

Source: **FedRAMP Consolidated Rules for 2026** v2026.11.02.01 (bespoke JSON; not OSCAL).

## Totals

- Source leaf values inventoried (id-normalized paths): **7,532**
- Mapped: **7,532** -> **UNMAPPED: 0** -> coverage **100.0 %**
- "Mapped" means that the path has a row in the path map below, not that its values are in the bundle. Of the 7,532: **6,540** on rows that name a destination (L1 4,718, L2 1,822), **992** on rows that declare the path not carried. What arrived, value by value, is the ledger's to say (below): 4,553 copied, 1,987 transformed, 0 no content by a checked rule, 992 dropped for a declared reason, 0 unaccounted.
- Emitted: **291 Requirements** (FRR rules + KSIs), **652 Mapping objects**, **92 Sets** (17 families, 56 subsets, 4 classes, 2 tracks, 10 KSI categories, and 3: the root, the CTL overlay, the Set of the carried Rev 5 Requirements), **5 Tailorings** (4 class variants and the Rev 5 ODP overlay), manifest with both digests, 11 pinned stubs.
- The bundle as written: `content-manifest.json` is `sha256:8cbcbb26eecfe4bef979f5121e10695de55b6210cff6f73d1ac8c2d052caf595`. The manifest lists both digests of each of its 1,054 objects (291 Requirements of the publication, 14 carried Rev 5 Requirements, the Mappings, Sets and Tailorings) and the digest of each pinned schema, so this value stands for every byte of the bundle. The bundle is not in the repository; a run that reproduces this report has reproduced the bundle.

## Conversion rules (declared, counted)

- **force -> modality** (rule level): must x136, should x45, unspecified x28, may x20, must-not x11, should-not x5. Class-variant forces become **Tailoring ops**: {'set-modality': 107}; easings auto-carry a converter Deviation (approver: FedRAMP, rationale: published class variant) x0.
- **status -> lifecycle**, by rule. The source gives a family and a KSI category the status of a document, in three words (its schema: stable, placeholder, empty): KSI category `stable` x10; family `placeholder` x1; family `stable` x16. The kernel's lifecycle knows draft, active, deprecated, withdrawn. The converter's mapping: `stable` -> `active`, `placeholder` -> `draft`, `empty` -> `draft`; a word outside the three stops the run. `stable` is the source's word for a document that is settled; `placeholder` and `empty` say that it is not, and `draft` is the only state of the kernel that says so. The source's own word is kept beside the mapped state, in narrative@1 of the Set that stands for the document (`status`): the kernel has no place for it. The status is the document's, and a document of this source is its rules or indicators, none of which has a status of its own; the lifecycle of every object made from a document therefore follows the document's status - its Set, its subset Sets, its rules or indicators and the Mappings of their control links. Objects by lifecycle and where it comes from: `active` x14 as the SP 800-53 bundle has it; `active` x998 from the status of a document; `draft` x28 from the status of a document; `active` x14 the converter's own. Until 2026-11-14 the converter read no status and wrote `active` on every object. The converter's own `active` stands on the objects it makes for the publication as a whole (the root, the class and track Sets, the CTL overlay and the Set of the carried Rev 5 Requirements, the Tailorings), for which the source states no status.
- **The id of a KSI category** (x10) is carried as an alias of the category's Set (`aliases`, scheme `fedramp-cr26:KSI.id`). The Set's own URI is minted from the key the category stands under, as every id of this bundle is minted from a key of the source.
- **affects[] -> obligated-parties[]** (parties minted as codes); subset applicability -> scope@1 on subset Sets and composed **class Sets (a-d)** and **type Sets (20x/Rev5)** - sets-of-sets (D21).
- **Obligated party**: `https://ns.fedramp.gov/cr26/party/provider` on every statement for which the source names no party; where it names one (in `affects` of a rule), that one is written. `https://ns.fedramp.gov/cr26/party/provider` is the converter's default and not a value of the source; `--obligated-party URI` writes another. Why this default: a KSI has no `affects` and its statement names no actor; the converter reads an indicator as a statement about the cloud service offering, which is its provider's to meet. Statements with a party from `affects`: x245; with this party: x46 (every KSI, and a rule only if it names nobody).
- **timeframe_num/type -> statement parameter** 'timeframe' (elapsed vs calendar split; calendar-ref minted; tightening: lower). Class variants: set-parameter when unit-class matches; **true unit-class crossings x0** (base-absent variant timeframes x51 counted separately) stay in the L2 class-variants payload - spec-feedback: candidate D9 duration-union question.
- **timeframe_num_min / timeframe_num_max -> statement parameters** 'timeframe-min' and 'timeframe-max' (bounds written: x2). A rule states one timeframe or a range. The kernel's durations have one `num`, and its `range` is a container of scalars, which a duration is not (D9); a range is therefore its two bounds, each a duration with the unit of timeframe_type and, for a calendar unit, the calendar. Tightening is declared `higher` for the floor and `lower` for the ceiling: a window narrows when its floor rises or its ceiling falls. The two directions are the converter's reading, as `lower` is for a single timeframe; the source states none.
- **A number that is no integer** (x3) is written as a decimal string, the kernel's spelling of a fraction (NUMBER-1, D3.9): `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.3.iir.timeframe_num` x1; `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.4.iir.timeframe_num` x1; `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.5.iir.timeframe_num` x1. It is done in the parked L2 payloads, which are otherwise as the source has them. Anywhere else a fraction stops the run: a duration's `num` is a kernel number, and a kernel number is an integer.
- **varies_by_class** preserved in full as L2 `class-variants` payloads on 28 rules (+5 KSIs); computable deltas additionally emitted as ops. Variant-only rules (no base statement): synthesized base prose x28 (flagged).
- **Control lists -> 652 Mapping objects**: x558 from KSIs, x94 from rules (relationship `supports`, confidence `draft`, rationale per handbook 8.6 untyped-import rule; targets minted under https://ns.nist.gov/sp800-53/req/). A rule's `controls` are converted by the rule for a KSI's: the publisher's schema types the two lists alike, as an array of control ids, and states no relationship for either (read 2026-11-14 at the publication's tag).
- **FRD -> terminology@1** hosted on the corpus root Set (glossary-info carries the FRD block metadata): 81 terms, 190 aliases, links and chrome flags in-payload; a term without alternatives gets no `aliases` (an empty container is left out). **ignore_in_terms** (x9) has no member in terminology@1, which knows `do-not-link` only; it is carried in narrative@1 on the same Set as `ignore-in-terms`, by term id, with the value the source wrote.
- **CTL ODP assignments DRAINED (backlog #10, gate 3)**: 16 set-parameter ops on the `rev5-odp-overlay` Tailoring, each addressed (requirement-ref, statement-id, parameter) via the DECLARING statement of the Rev 5.2.0 ODP (measured: no ODP is declared in two statements); 14 tailored Rev 5 Requirements carried in-bundle as byte-identical copies (closure; the authorization-package pattern). CTL guidance entries stay parked L2 - supplemental prose on external controls is D20 supplements territory, not ODP addressing. Multi-select serialization normalized x3 (FedRAMP flattens many-cardinality selections into prose strings 'a; b' / 'a, b and c'; every part matches a declared NIST choice -> list value; REPORTED upstream). Residual choice conflicts: none.
- **notification/following_information -> reporting-obligation@1**; artifacts.all and examples -> assessment-criteria@1; note/notes/danger/corrective_actions -> narrative@1. **A notification the source marks `optional`** (x3) is no duty, and reporting-obligation@1 lists duties (it declares that it alters what passing means) and has no member for the flag. The entry goes whole, with its flag, to narrative@1 as `optional-notification`; reporting-obligation@1 keeps the other entries of the rule.
- **rule/KSI term names resolved to FRD ids** via the term+alias index (unresolved x0 kept as slugs, counted).
- **updated[]** (entries counted: 475): the update history of a term, a rule or an indicator is not carried, in no object and not in the manifest. The path map declares the drop. Until 2026-11-14 this line read "updated[] -> L0" and the rows were marked L1; the ledger found none of the values written.
- **CTL Rev5 overlay (79 entries)**: the guidance and the update history of an entry are parked L2 on /set/ctl-overlay. Its ODP assignments are not parked: they are the operations of the `rev5-odp-overlay` Tailoring (the line on the drained assignments above). Until 2026-11-14 this line read as if the assignments were parked too and waited for gate item 3; the ledger finds each of them in an operation.
- **flows dropped-declared** x1 (D17); dangling related refs x0.
- **Payload free text language-tagged** per corpus language (`{en: ...}`), harmonized 2026-07-21 (backlog #12): corrective-actions x8, danger x3, definition x81, description x72, guidance x66, note x86, notes x29, notification-name x31. Left bare by the label/identifier rule: term headwords x81, glossary-info block metadata, reference/schema-name citation labels, following-information sentence lists (kernel `text` decision pending, backlog #12). Left as-source by the verbatim rule: free text quoted inside L2 `class-variants` payloads (per-class descriptions/notes, e.g. pain_timeframes[].fir.description) - preserved-in-full waiting rooms are quotations, not authored payload (report, never repair); they drain with the payloads themselves. Stub-file `note` annotations are schema metadata, not corpus content.

## Findings (computed)

- **Census, layered:** rules = **245** = 225 track-independent (data.all) + 12 rev5-only + 8 20x-only. Rule-level force totals {'must': 136, 'may': 20, 'should': 45, 'must-not': 11, 'should-not': 5, 'unspecified': 28}; the 217 forces stated at rule level and the 107 stated in class variants are 324 force values, the number a census gets that counts the two together.
- **Framework-specific subsets x9** (CSX/CSF) read from info.20x.subsets / info.rev5.subsets per FedRAMP's layering (global by default, specific when needed). CORRECTION: an earlier version of this report misreported these as undeclared - a checker bug on our side, fixed after review in FedRAMP community discussion #153.
- **Zero easings across 107 class-variant modality ops**: every published class delta tightens or specifies - the Deviation channel stayed empty by measurement, not by assumption.
- Rules without base statements exist (x28) - CR26 itself models some obligations *only* as class variants; the Set+Tailoring decomposition makes that explicit.
- **Deviation ceremony question (spec feedback):** authority-published prose variants would require replace-prose(substantive)+Deviation under D13; converter parks prose variance in L2 instead - open design question for v0.6.

## Conversion ledger (measured per source value)

The path map says where a source path is declared to go. The ledger follows each of the 7,532 source leaf values, flags and fractions among them: a value the converter hands on unchanged carries its origin into the bundle, a value it computes is stated as a named rule, and after the bundle is written every claim is read back from the files. `cr26-conversion-ledger.json` holds the result, one row per source path and outcome (backlog #41). Real content is never dropped (author, 2026-11-14): a value is carried, or it is no content by a rule the ledger checks, and a run with one unaccounted value ends with 1.

- **4,553 copied**: the value stands, with its type, at the destination named.
- **1,987 transformed** by a named rule; the rule was applied to the source again and the result compared with the file. A value that is copied to one place and transformed for another counts as copied.
- **0 no content** by a checked rule (a name that only selects a field, a namespace, an id that is rebuilt exactly from another value). This source has no value of the three kinds, and the converter declares none.
- **992 dropped for a declared reason**: the two classes that were declared before the author's rule, exactly the paths the path map marks `declared-drop`. Neither is one of the three kinds above. Whether they are content is the author's to decide; they are listed below with the converter's reading.
- **0 unaccounted**: no destination and no declared reason.
- Claims that did not hold against the written files: **0**.
- Rows of the path map that the ledger contradicts (a destination named and a value of the path written nowhere; a path declared not carried and written all the same; a row marked L1 whose values stand only in the parked L2 payload): **0**.

### Rules

Each rule is a function of source values; a rule's count is the number of source values it accounts for.

| rule | source values |
|---|---:|
| Mapping id from its owner's id and the control id | 652 |
| Requirement URI from the id of a related rule | 78 |
| SP 800-53 Requirement URI from the control id | 652 |
| base prose of a rule that states its text by class only, from its name | 28 |
| base prose of an indicator that states its text by class only, from its name | 5 |
| decimal string of a number that is no integer (the kernel's spelling of a fraction, D3.9) | 3 |
| duration type from the unit of the timeframe | 23 |
| lifecycle of an object made from a document (a subset Set, a rule or an indicator, a Mapping of its control links), from the document's status (stable: active; placeholder, empty: draft) | 27 |
| lifecycle of the Set that stands for a document, from the document's status (stable: active; placeholder, empty: draft) | 27 |
| modality from the force word (code map) | 324 |
| one selection of a multi-select that the source writes as one string | 3 |
| party URI from a name in affects | 245 |
| term URI from the term's name, by the glossary's headwords and alternatives | 789 |
| title of one track's share of a subset, from the subset's name | 1 |

### No content, by a checked rule

| kind | rule | source values |
|---|---|---:|
| *(none)* | | 0 |

### Declared drops, and the converter's reading of each

Declared before 2026-11-14 and left declared: the author decides whether a class is content. The reading is the converter's and decides nothing. The example is a value of the class that is no prose (a date, an id), with its pointer.

| source paths | values | declared reason | example | reading |
|---|---:|---|---|---|
| `cr26.FRR.*.info.flows[].activity` x1<br>`cr26.FRR.*.info.flows[].description` x1<br>`cr26.FRR.*.info.flows[].nodes.*` x8<br>`cr26.FRR.*.info.flows[].steps[].description` x7<br>`cr26.FRR.*.info.flows[].steps[].from` x9<br>`cr26.FRR.*.info.flows[].steps[].to` x9 | 35 | process-flow diagrams: linked resources, not requirement data (D17) | `cr26#/FRR/IEC/info/flows/0/steps/0/to` = `IEC-CSO-EFR` | content: the diagram is written out in the source itself (an activity, its description, nodes and steps that name rules in their order and say on which answer one follows the other) and nothing in the bundle holds it |
| `cr26.FRD.data.all.*.updated[].comment` x85<br>`cr26.FRD.data.all.*.updated[].date` x85<br>`cr26.FRD.data.all.*.updated[].issue` x1<br>`cr26.FRR.*.data.*.*.*.updated[].comment` x303<br>`cr26.FRR.*.data.*.*.*.updated[].date` x303<br>`cr26.FRR.*.data.*.*.*.updated[].issue` x5<br>`cr26.KSI.*.indicators.*.updated[].comment` x87<br>`cr26.KSI.*.indicators.*.updated[].date` x87<br>`cr26.KSI.*.indicators.*.updated[].issue` x1 | 957 | update history of the entry (date, comment, issue): its entries are counted in the report, the values are carried in no object and not in the manifest (the map read "history -> L0" until 2026-11-14) | `cr26#/FRD/data/all/FRD-ACV/updated/0/date` = `2026-06-24` | content: an entry says on which day a term, a rule or an indicator was changed and why, some with the number of an issue; the bundle holds the day of the publication and nothing of an entry's own history |

### Unaccounted

No destination, no checked rule and no declared reason. A run with one such value ends with 1.

| path | values | first value |
|---|---:|---|
| *(none)* | 0 | |

### What the ledger cannot see

The ledger follows source values into the bundle, not the bundle back to the source. A value the converter writes on its own has no source value behind it and no entry: a constant (a lifecycle, a relationship, a tightening, the rationale of a Mapping), an id, a label or a file name minted from a KEY of the source (the id of a rule, a term, a family, a subset; keys are not leaf values), the membership and the order of a Set, the party written where the source names nobody, and the Requirements copied from the SP 800-53 bundle. Counted on the written objects and the manifest:

| written as | leaf values | with no source value behind them |
|---|---:|---:|
| Mapping | 7,172 | 3,912 |
| Requirement (KSI) | 594 | 315 |
| Requirement (rule) | 6,439 | 1,646 |
| Set | 3,036 | 1,437 |
| Tailoring | 541 | 393 |
| carried Rev 5 Requirement | 1,040 | 1,040 |
| manifest | 5,319 | 3,624 |
| **all** | **24,141** | **12,367** |

## Full path map
| path | count | level | destination |
|---|---:|---|---|
| `cr26.CTL.*.*.guidance[]` | 67 | L2 | CTL guidance/variants: parked payload on /cr26/set/ctl-overlay - FedRAMP supplemental prose on external controls (D20 supplements territory, not ODP addressing) |
| `cr26.CTL.*.*.parameters[].parameterId` | 16 | L1 | CTL ODP assignments -> set-parameter ops on the rev5-odp-overlay Tailoring, statement-addressed via the declaring statement; tailored Rev 5 Requirements carried in-bundle (backlog #10 DRAINED, gate 3) |
| `cr26.CTL.*.*.parameters[].value` | 16 | L1 | CTL ODP assignments -> set-parameter ops on the rev5-odp-overlay Tailoring, statement-addressed via the declaring statement; tailored Rev 5 Requirements carried in-bundle (backlog #10 DRAINED, gate 3) |
| `cr26.CTL.*.*.updated[].comment` | 1 | L2 | CTL guidance/variants: parked payload on /cr26/set/ctl-overlay - FedRAMP supplemental prose on external controls (D20 supplements territory, not ODP addressing) |
| `cr26.CTL.*.*.updated[].date` | 1 | L2 | CTL guidance/variants: parked payload on /cr26/set/ctl-overlay - FedRAMP supplemental prose on external controls (D20 supplements territory, not ODP addressing) |
| `cr26.CTL.*.*.varies_by_class.*.guidance[]` | 6 | L2 | CTL guidance/variants: parked payload on /cr26/set/ctl-overlay - FedRAMP supplemental prose on external controls (D20 supplements territory, not ODP addressing) |
| `cr26.CTL.*.*.varies_by_class.*.parameters[].parameterId` | 5 | L2 | CTL guidance/variants: parked payload on /cr26/set/ctl-overlay - FedRAMP supplemental prose on external controls (D20 supplements territory, not ODP addressing) |
| `cr26.CTL.*.*.varies_by_class.*.parameters[].value` | 5 | L2 | CTL guidance/variants: parked payload on /cr26/set/ctl-overlay - FedRAMP supplemental prose on external controls (D20 supplements territory, not ODP addressing) |
| `cr26.FRD.data.all.*.alts[]` | 190 | L1 | terminology@1 payload per term (alts, links, chrome flags inside payload) |
| `cr26.FRD.data.all.*.definition` | 81 | L1 | terminology@1 payload per term (alts, links, chrome flags inside payload) |
| `cr26.FRD.data.all.*.do_not_link` | 9 | L1 | terminology@1 payload per term (alts, links, chrome flags inside payload) |
| `cr26.FRD.data.all.*.ignore_in_terms` | 9 | L1 | narrative@1 on the corpus root Set: ignore-in-terms {term id: flag} (terminology@1 has do-not-link and no member for this one) |
| `cr26.FRD.data.all.*.note` | 29 | L1 | terminology@1 payload per term (alts, links, chrome flags inside payload) |
| `cr26.FRD.data.all.*.notes[]` | 7 | L1 | terminology@1 payload per term (alts, links, chrome flags inside payload) |
| `cr26.FRD.data.all.*.reference` | 9 | L1 | terminology@1 payload per term (alts, links, chrome flags inside payload) |
| `cr26.FRD.data.all.*.reference_url` | 9 | L1 | terminology@1 payload per term (alts, links, chrome flags inside payload) |
| `cr26.FRD.data.all.*.tag` | 57 | L1 | terminology@1 payload per term (alts, links, chrome flags inside payload) |
| `cr26.FRD.data.all.*.term` | 81 | L1 | terminology@1 payload per term (alts, links, chrome flags inside payload) |
| `cr26.FRD.data.all.*.updated[].comment` | 85 | declared-drop | update history of the entry (date, comment, issue): its entries are counted in the report, the values are carried in no object and not in the manifest (the map read "history -> L0" until 2026-11-14) |
| `cr26.FRD.data.all.*.updated[].date` | 85 | declared-drop | update history of the entry (date, comment, issue): its entries are counted in the report, the values are carried in no object and not in the manifest (the map read "history -> L0" until 2026-11-14) |
| `cr26.FRD.data.all.*.updated[].issue` | 1 | declared-drop | update history of the entry (date, comment, issue): its entries are counted in the report, the values are carried in no object and not in the manifest (the map read "history -> L0" until 2026-11-14) |
| `cr26.FRD.info.effective.current_status` | 1 | L1 | terminology@1 glossary-info on the corpus root Set |
| `cr26.FRD.info.effective.date.grace.default` | 1 | L1 | terminology@1 glossary-info on the corpus root Set |
| `cr26.FRD.info.effective.date.grace.until_next_assessment` | 1 | L1 | terminology@1 glossary-info on the corpus root Set |
| `cr26.FRD.info.effective.date.maintain` | 1 | L1 | terminology@1 glossary-info on the corpus root Set |
| `cr26.FRD.info.effective.date.obtain` | 1 | L1 | terminology@1 glossary-info on the corpus root Set |
| `cr26.FRD.info.effective.date.optional_adoption` | 1 | L1 | terminology@1 glossary-info on the corpus root Set |
| `cr26.FRD.info.effective.is` | 1 | L1 | terminology@1 glossary-info on the corpus root Set |
| `cr26.FRD.info.name` | 1 | L1 | terminology@1 glossary-info on the corpus root Set |
| `cr26.FRD.info.purpose` | 1 | L1 | terminology@1 glossary-info on the corpus root Set |
| `cr26.FRD.info.short_name` | 1 | L1 | terminology@1 glossary-info on the corpus root Set |
| `cr26.FRD.info.status` | 1 | L1 | terminology@1 glossary-info on the corpus root Set |
| `cr26.FRD.info.web_name` | 1 | L1 | terminology@1 glossary-info on the corpus root Set |
| `cr26.FRR.*.data.*.*.*.affects[]` | 245 | L1 | statements[0].obligated-parties[] |
| `cr26.FRR.*.data.*.*.*.artifacts.all[]` | 79 | L1 | assessment-criteria@1: required-artifacts |
| `cr26.FRR.*.data.*.*.*.controls[]` | 94 | L1 | Mapping objects (relationship supports; 8.6 untyped-import rule), as for a KSI |
| `cr26.FRR.*.data.*.*.*.corrective_actions[]` | 12 | L1 | narrative@1: note / notes / danger / corrective-actions |
| `cr26.FRR.*.data.*.*.*.danger` | 3 | L1 | narrative@1: note / notes / danger / corrective-actions |
| `cr26.FRR.*.data.*.*.*.examples[].examples[]` | 24 | L1 | assessment-criteria@1: examples[] {id, examples, key-tests} - the KSI-shaped test data |
| `cr26.FRR.*.data.*.*.*.examples[].id` | 5 | L1 | assessment-criteria@1: examples[] {id, examples, key-tests} - the KSI-shaped test data |
| `cr26.FRR.*.data.*.*.*.examples[].key_tests[]` | 15 | L1 | assessment-criteria@1: examples[] {id, examples, key-tests} - the KSI-shaped test data |
| `cr26.FRR.*.data.*.*.*.following_information[]` | 208 | L1 | reporting-obligation@1: following-information / following-information-bullets |
| `cr26.FRR.*.data.*.*.*.following_information_bullets[]` | 11 | L1 | reporting-obligation@1: following-information / following-information-bullets |
| `cr26.FRR.*.data.*.*.*.force` | 217 | L1 | statements[0].modality (code map) |
| `cr26.FRR.*.data.*.*.*.name` | 245 | L1 | Requirement.title |
| `cr26.FRR.*.data.*.*.*.note` | 57 | L1 | narrative@1: note / notes / danger / corrective-actions |
| `cr26.FRR.*.data.*.*.*.notes[]` | 62 | L1 | narrative@1: note / notes / danger / corrective-actions |
| `cr26.FRR.*.data.*.*.*.notification[].method` | 31 | L1 | reporting-obligation@1: notification[]; of an entry the source marks optional: narrative@1 optional-notification[] |
| `cr26.FRR.*.data.*.*.*.notification[].name` | 31 | L1 | reporting-obligation@1: notification[]; of an entry the source marks optional: narrative@1 optional-notification[] |
| `cr26.FRR.*.data.*.*.*.notification[].optional` | 3 | L1 | narrative@1: optional-notification[] - the entry goes there whole, with its flag (reporting-obligation@1 lists duties and has no member for an optional one) |
| `cr26.FRR.*.data.*.*.*.notification[].party` | 31 | L1 | reporting-obligation@1: notification[]; of an entry the source marks optional: narrative@1 optional-notification[] |
| `cr26.FRR.*.data.*.*.*.notification[].target` | 31 | L1 | reporting-obligation@1: notification[]; of an entry the source marks optional: narrative@1 optional-notification[] |
| `cr26.FRR.*.data.*.*.*.reference` | 6 | L1 | narrative@1: reference, the label of the citation (the map read "relations ... -> external URL" until 2026-11-14; the URL of the relation is reference_url) |
| `cr26.FRR.*.data.*.*.*.reference_url` | 6 | L1 | relation `schema` / `reference` -> the external URL |
| `cr26.FRR.*.data.*.*.*.related[]` | 78 | L1 | relations related -> /cr26/req/<id> (dangling counted) |
| `cr26.FRR.*.data.*.*.*.schema.name` | 24 | L1 | relations schema -> url; name kept in narrative@1 |
| `cr26.FRR.*.data.*.*.*.schema.url` | 24 | L1 | relations schema -> url; name kept in narrative@1 |
| `cr26.FRR.*.data.*.*.*.statement` | 217 | L1 | statements[0].prose.en |
| `cr26.FRR.*.data.*.*.*.terms[]` | 704 | L1 | relations uses-term -> /cr26/term/<id> |
| `cr26.FRR.*.data.*.*.*.timeframe_num` | 22 | L1 | statement parameter 'timeframe' (elapsed-duration or calendar-period, by unit); timeframe_type is the unit of every timeframe parameter of the rule |
| `cr26.FRR.*.data.*.*.*.timeframe_num_max` | 1 | L1 | statement parameters 'timeframe-min' / 'timeframe-max': a range is its two bounds, each a duration of the kernel (unit from timeframe_type) |
| `cr26.FRR.*.data.*.*.*.timeframe_num_min` | 1 | L1 | statement parameters 'timeframe-min' / 'timeframe-max': a range is its two bounds, each a duration of the kernel (unit from timeframe_type) |
| `cr26.FRR.*.data.*.*.*.timeframe_type` | 23 | L1 | statement parameter 'timeframe' (elapsed-duration or calendar-period, by unit); timeframe_type is the unit of every timeframe parameter of the rule |
| `cr26.FRR.*.data.*.*.*.updated[].comment` | 303 | declared-drop | update history of the entry (date, comment, issue): its entries are counted in the report, the values are carried in no object and not in the manifest (the map read "history -> L0" until 2026-11-14) |
| `cr26.FRR.*.data.*.*.*.updated[].date` | 303 | declared-drop | update history of the entry (date, comment, issue): its entries are counted in the report, the values are carried in no object and not in the manifest (the map read "history -> L0" until 2026-11-14) |
| `cr26.FRR.*.data.*.*.*.updated[].issue` | 5 | declared-drop | update history of the entry (date, comment, issue): its entries are counted in the report, the values are carried in no object and not in the manifest (the map read "history -> L0" until 2026-11-14) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.artifacts.all[]` | 31 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.following_information[]` | 57 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.force` | 107 | L1 | class Tailoring op set-modality (monotone) OR + converter Deviation when easing (counted) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.note` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.1.fir.description` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.1.fir.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.1.fir.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.1.iir.description` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.1.iir.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.1.iir.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.1.oir.description` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.1.oir.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.1.oir.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.2.fir.description` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.2.fir.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.2.fir.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.2.iir.description` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.2.iir.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.2.iir.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.2.irv_lev.description` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.2.irv_lev.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.2.irv_lev.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.2.nirv_lev.description` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.2.nirv_lev.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.2.nirv_lev.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.2.nlev.description` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.2.nlev.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.2.nlev.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.2.oir.description` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.2.oir.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.2.oir.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.3.fir.description` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.3.fir.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.3.fir.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.3.iir.description` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.3.iir.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.3.iir.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.3.irv_lev.description` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.3.irv_lev.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.3.irv_lev.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.3.nirv_lev.description` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.3.nirv_lev.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.3.nirv_lev.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.3.nlev.description` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.3.nlev.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.3.nlev.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.3.oir.description` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.3.oir.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.3.oir.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.4.fir.description` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.4.fir.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.4.fir.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.4.iir.description` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.4.iir.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.4.iir.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.4.irv_lev.description` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.4.irv_lev.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.4.irv_lev.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.4.nirv_lev.description` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.4.nirv_lev.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.4.nirv_lev.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.4.nlev.description` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.4.nlev.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.4.nlev.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.4.oir.description` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.4.oir.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.4.oir.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.5.fir.description` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.5.fir.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.5.fir.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.5.iir.description` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.5.iir.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.5.iir.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.5.irv_lev.description` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.5.irv_lev.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.5.irv_lev.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.5.nirv_lev.description` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.5.nirv_lev.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.5.nirv_lev.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.5.nlev.description` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.5.nlev.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.5.nlev.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.5.oir.description` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.5.oir.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.5.oir.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.rev5_controls_list.AC[]` | 141 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.rev5_controls_list.AT[]` | 17 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.rev5_controls_list.AU[]` | 92 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.rev5_controls_list.CA[]` | 42 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.rev5_controls_list.CM[]` | 91 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.rev5_controls_list.CP[]` | 67 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.rev5_controls_list.IA[]` | 98 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.rev5_controls_list.IR[]` | 58 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.rev5_controls_list.MA[]` | 28 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.rev5_controls_list.MP[]` | 21 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.rev5_controls_list.PE[]` | 58 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.rev5_controls_list.PL[]` | 21 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.rev5_controls_list.PS[]` | 30 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.rev5_controls_list.RA[]` | 40 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.rev5_controls_list.SA[]` | 60 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.rev5_controls_list.SC[]` | 114 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.rev5_controls_list.SI[]` | 87 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.rev5_controls_list.SR[]` | 37 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.statement` | 107 | L2 | class-variants payload (full variant preserved, a fraction as a decimal string; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.timeframe_num` | 51 | L2 | class-variants payload; and a class Tailoring op set-parameter where the rule itself states a timeframe of the same unit class - the conversion rules above count the ops (the row was marked L1 until 2026-11-14, though a value reaches an operation only in that case) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.timeframe_type` | 51 | L2 | class-variants payload; and a class Tailoring op set-parameter where the rule itself states a timeframe of the same unit class - the conversion rules above count the ops (the row was marked L1 until 2026-11-14, though a value reaches an operation only in that case) |
| `cr26.FRR.*.info.20x.effective.current_status` | 10 | L1 | effectivity@1 on family Set (default / per-track) |
| `cr26.FRR.*.info.20x.effective.date.grace.default` | 10 | L1 | effectivity@1 on family Set (default / per-track) |
| `cr26.FRR.*.info.20x.effective.date.grace.until_next_assessment` | 10 | L1 | effectivity@1 on family Set (default / per-track) |
| `cr26.FRR.*.info.20x.effective.date.maintain` | 10 | L1 | effectivity@1 on family Set (default / per-track) |
| `cr26.FRR.*.info.20x.effective.date.obtain` | 10 | L1 | effectivity@1 on family Set (default / per-track) |
| `cr26.FRR.*.info.20x.effective.date.optional_adoption` | 10 | L1 | effectivity@1 on family Set (default / per-track) |
| `cr26.FRR.*.info.20x.effective.is` | 10 | L1 | effectivity@1 on family Set (default / per-track) |
| `cr26.FRR.*.info.20x.subsets.*.applicability.affects[]` | 4 | L1 | framework-specific subset declarations -> track subset Sets (title/description/scope) [corrected per FedRAMP #153] |
| `cr26.FRR.*.info.20x.subsets.*.applicability.classes[]` | 13 | L1 | framework-specific subset declarations -> track subset Sets (title/description/scope) [corrected per FedRAMP #153] |
| `cr26.FRR.*.info.20x.subsets.*.applicability.paths[]` | 4 | L1 | framework-specific subset declarations -> track subset Sets (title/description/scope) [corrected per FedRAMP #153] |
| `cr26.FRR.*.info.20x.subsets.*.applicability.types[]` | 4 | L1 | framework-specific subset declarations -> track subset Sets (title/description/scope) [corrected per FedRAMP #153] |
| `cr26.FRR.*.info.20x.subsets.*.description` | 4 | L1 | framework-specific subset declarations -> track subset Sets (title/description/scope) [corrected per FedRAMP #153] |
| `cr26.FRR.*.info.20x.subsets.*.name` | 4 | L1 | framework-specific subset declarations -> track subset Sets (title/description/scope) [corrected per FedRAMP #153] |
| `cr26.FRR.*.info.effective.current_status` | 7 | L1 | effectivity@1 on family Set (default / per-track) |
| `cr26.FRR.*.info.effective.date.grace.default` | 7 | L1 | effectivity@1 on family Set (default / per-track) |
| `cr26.FRR.*.info.effective.date.grace.until_next_assessment` | 7 | L1 | effectivity@1 on family Set (default / per-track) |
| `cr26.FRR.*.info.effective.date.maintain` | 7 | L1 | effectivity@1 on family Set (default / per-track) |
| `cr26.FRR.*.info.effective.date.obtain` | 7 | L1 | effectivity@1 on family Set (default / per-track) |
| `cr26.FRR.*.info.effective.date.optional_adoption` | 5 | L1 | effectivity@1 on family Set (default / per-track) |
| `cr26.FRR.*.info.effective.is` | 7 | L1 | effectivity@1 on family Set (default / per-track) |
| `cr26.FRR.*.info.flows[].activity` | 1 | declared-drop | process-flow diagrams: linked resources, not requirement data (D17) |
| `cr26.FRR.*.info.flows[].description` | 1 | declared-drop | process-flow diagrams: linked resources, not requirement data (D17) |
| `cr26.FRR.*.info.flows[].nodes.*` | 8 | declared-drop | process-flow diagrams: linked resources, not requirement data (D17) |
| `cr26.FRR.*.info.flows[].steps[].description` | 7 | declared-drop | process-flow diagrams: linked resources, not requirement data (D17) |
| `cr26.FRR.*.info.flows[].steps[].from` | 9 | declared-drop | process-flow diagrams: linked resources, not requirement data (D17) |
| `cr26.FRR.*.info.flows[].steps[].to` | 9 | declared-drop | process-flow diagrams: linked resources, not requirement data (D17) |
| `cr26.FRR.*.info.name` | 17 | L1 | family Set: title/label |
| `cr26.FRR.*.info.purpose` | 17 | L1 | family Set: narrative description / scope tag |
| `cr26.FRR.*.info.rev5.effective.current_status` | 10 | L1 | effectivity@1 on family Set (default / per-track) |
| `cr26.FRR.*.info.rev5.effective.date.grace.default` | 10 | L1 | effectivity@1 on family Set (default / per-track) |
| `cr26.FRR.*.info.rev5.effective.date.grace.until_next_assessment` | 10 | L1 | effectivity@1 on family Set (default / per-track) |
| `cr26.FRR.*.info.rev5.effective.date.maintain` | 10 | L1 | effectivity@1 on family Set (default / per-track) |
| `cr26.FRR.*.info.rev5.effective.date.obtain` | 10 | L1 | effectivity@1 on family Set (default / per-track) |
| `cr26.FRR.*.info.rev5.effective.date.optional_adoption` | 10 | L1 | effectivity@1 on family Set (default / per-track) |
| `cr26.FRR.*.info.rev5.effective.is` | 10 | L1 | effectivity@1 on family Set (default / per-track) |
| `cr26.FRR.*.info.rev5.subsets.*.applicability.affects[]` | 5 | L1 | framework-specific subset declarations -> track subset Sets (title/description/scope) [corrected per FedRAMP #153] |
| `cr26.FRR.*.info.rev5.subsets.*.applicability.classes[]` | 15 | L1 | framework-specific subset declarations -> track subset Sets (title/description/scope) [corrected per FedRAMP #153] |
| `cr26.FRR.*.info.rev5.subsets.*.applicability.paths[]` | 10 | L1 | framework-specific subset declarations -> track subset Sets (title/description/scope) [corrected per FedRAMP #153] |
| `cr26.FRR.*.info.rev5.subsets.*.applicability.types[]` | 5 | L1 | framework-specific subset declarations -> track subset Sets (title/description/scope) [corrected per FedRAMP #153] |
| `cr26.FRR.*.info.rev5.subsets.*.description` | 5 | L1 | framework-specific subset declarations -> track subset Sets (title/description/scope) [corrected per FedRAMP #153] |
| `cr26.FRR.*.info.rev5.subsets.*.name` | 5 | L1 | framework-specific subset declarations -> track subset Sets (title/description/scope) [corrected per FedRAMP #153] |
| `cr26.FRR.*.info.short_name` | 17 | L1 | family Set: title/label |
| `cr26.FRR.*.info.status` | 17 | L1 | the family Set's `lifecycle` by the rule for a document's status, the lifecycle of every object made from the family (subset Sets, rules, Mappings of their control links), and the word itself in narrative@1 of the family Set: status |
| `cr26.FRR.*.info.subsets.*.applicability.affects[]` | 45 | L1 | scope@1 on subset Set (types/paths/classes/affects) + class & type Set composition |
| `cr26.FRR.*.info.subsets.*.applicability.classes[]` | 124 | L1 | scope@1 on subset Set (types/paths/classes/affects) + class & type Set composition |
| `cr26.FRR.*.info.subsets.*.applicability.paths[]` | 78 | L1 | scope@1 on subset Set (types/paths/classes/affects) + class & type Set composition |
| `cr26.FRR.*.info.subsets.*.applicability.types[]` | 78 | L1 | scope@1 on subset Set (types/paths/classes/affects) + class & type Set composition |
| `cr26.FRR.*.info.subsets.*.description` | 45 | L1 | subset Set: title / narrative description |
| `cr26.FRR.*.info.subsets.*.name` | 45 | L1 | subset Set: title / narrative description |
| `cr26.FRR.*.info.tag` | 17 | L1 | family Set: narrative description / scope tag |
| `cr26.FRR.*.info.web_name` | 17 | L1 | family Set annotations.web_name (chrome) |
| `cr26.KSI.*.id` | 10 | L1 | KSI category Set: aliases[] (the theme's own id; the Set's URI is minted from the key the theme stands under) |
| `cr26.KSI.*.indicators.*.controls[]` | 558 | L1 | Mapping objects (relationship supports; 8.6 untyped-import rule) |
| `cr26.KSI.*.indicators.*.name` | 46 | L1 | KSI Requirement.title |
| `cr26.KSI.*.indicators.*.statement` | 41 | L1 | KSI statements[0].prose.en (modality unspecified: indicator language) |
| `cr26.KSI.*.indicators.*.terms[]` | 85 | L1 | relations uses-term |
| `cr26.KSI.*.indicators.*.updated[].comment` | 87 | declared-drop | update history of the entry (date, comment, issue): its entries are counted in the report, the values are carried in no object and not in the manifest (the map read "history -> L0" until 2026-11-14) |
| `cr26.KSI.*.indicators.*.updated[].date` | 87 | declared-drop | update history of the entry (date, comment, issue): its entries are counted in the report, the values are carried in no object and not in the manifest (the map read "history -> L0" until 2026-11-14) |
| `cr26.KSI.*.indicators.*.updated[].issue` | 1 | declared-drop | update history of the entry (date, comment, issue): its entries are counted in the report, the values are carried in no object and not in the manifest (the map read "history -> L0" until 2026-11-14) |
| `cr26.KSI.*.indicators.*.varies_by_class.*.statement` | 10 | L2 | class-variants payload on the KSI Requirement |
| `cr26.KSI.*.name` | 10 | L1 | KSI category Set: title / annotations.web_name / label |
| `cr26.KSI.*.short_name` | 10 | L1 | KSI category Set: title / annotations.web_name / label |
| `cr26.KSI.*.status` | 10 | L1 | the KSI category Set's `lifecycle` by the rule for a document's status, the lifecycle of its indicators and of the Mappings of their control links, and the word itself in narrative@1 of the category Set: status |
| `cr26.KSI.*.web_name` | 10 | L1 | KSI category Set: title / annotations.web_name / label |
| `cr26.info.default_artifacts.FRR[]` | 5 | L1 | assessment-criteria on corpus root: default-artifacts |
| `cr26.info.default_artifacts.KSI[]` | 5 | L1 | assessment-criteria on corpus root: default-artifacts |
| `cr26.info.description` | 1 | L1 | narrative@1 on the corpus root Set: description |
| `cr26.info.last_updated` | 1 | L1 | the manifest's provenance (last_updated) and the date of every Mapping's provenance |
| `cr26.info.title` | 1 | L1 | the manifest's provenance (source) and the title of the corpus root Set |
| `cr26.info.version` | 1 | L1 | the manifest's provenance (source-version) and `version` of every object made from the publication |

## UNMAPPED (gate target: zero)

*(none)*
