# CR26 -> Semantic Core: Coverage Report (computed)

Source: **FedRAMP Consolidated Rules for 2026** v2026.07.14.01 (bespoke JSON; not OSCAL).

## Totals

- Source leaf values inventoried (id-normalized paths): **7,294**
- Mapped: **7,294** -> **UNMAPPED: 0** -> coverage **100.0 %**
- Emitted: **292 Requirements** (FRR rules + KSIs), **373 Mapping objects**, **92 Sets** (families, subsets, classes, types, KSI categories, terms, root), **5 class Tailorings**, manifest with both digests, 11 pinned stubs.

## Conversion rules (declared, counted)

- **force -> modality** (rule level): must x136, should x45, unspecified x29, may x20, must-not x11, should-not x5. Class-variant forces become **Tailoring ops**: {'set-modality': 111}; easings auto-carry a converter Deviation (approver: FedRAMP, rationale: published class variant) x0.
- **affects[] -> obligated-parties[]** (parties minted as codes); subset applicability -> scope@1 on subset Sets and composed **class Sets (a-d)** and **type Sets (20x/Rev5)** - sets-of-sets (D21).
- **timeframe_num/type -> statement parameter** 'timeframe' (elapsed vs calendar split; calendar-ref minted; tightening: lower). Class variants: set-parameter when unit-class matches; **true unit-class crossings x0** (base-absent variant timeframes x51 counted separately) stay in the L2 class-variants payload - spec-feedback: candidate D9 duration-union question.
- **varies_by_class** preserved in full as L2 `class-variants` payloads on 29 rules (+5 KSIs); computable deltas additionally emitted as ops. Variant-only rules (no base statement): synthesized base prose x29 (flagged).
- **KSI control lists -> 373 Mapping objects** (relationship `supports`, confidence `draft`, rationale per handbook 8.6 untyped-import rule; targets minted under https://ns.nist.gov/sp800-53/req/).
- **FRD -> terminology@1** hosted on the corpus root Set (glossary-info carries the FRD block metadata): 75 terms, 188 aliases, links and chrome flags in-payload.
- **CTL ODP assignments DRAINED (backlog #10, gate 3)**: 16 set-parameter ops on the `rev5-odp-overlay` Tailoring, each addressed (requirement-ref, statement-id, parameter) via the DECLARING statement of the Rev 5.2.0 ODP (measured: no ODP is declared in two statements); 14 tailored Rev 5 Requirements carried in-bundle as byte-identical copies (closure; the authorization-package pattern). CTL guidance entries stay parked L2 - supplemental prose on external controls is D20 supplements territory, not ODP addressing. Multi-select serialization normalized x3 (FedRAMP flattens many-cardinality selections into prose strings 'a; b' / 'a, b and c'; every part matches a declared NIST choice -> list value; REPORTED upstream). Residual choice conflicts: none.
- **notification/following_information -> reporting-obligation@1**; artifacts.all -> assessment-criteria@1; note/notes/danger/examples/corrective_actions -> narrative@1.
- **rule/KSI term names resolved to FRD ids** via the term+alias index (unresolved x0 kept as slugs, counted).
- **updated[] -> L0** (entries counted: 377; values not object-carried).
- **CTL Rev5 overlay (79 entries) parked L2** on /set/ctl-overlay: external-catalog ODP assignments need the NIST catalog's statement map - resolves at gate item 3.
- **flows dropped-declared** x1 (D17); dangling related refs x0.
- **Payload free text language-tagged** per corpus language (`{en: ...}`), harmonized 2026-07-21 (backlog #12): corrective-actions x8, danger x3, definition x75, description x72, guidance x66, note x81, notes x27, notification-name x31. Left bare by the label/identifier rule: term headwords x75, glossary-info block metadata, reference/schema-name citation labels, following-information sentence lists (kernel `text` decision pending, backlog #12). Left as-source by the verbatim rule: free text quoted inside L2 `class-variants` payloads (per-class descriptions/notes, e.g. pain_timeframes[].fir.description) - preserved-in-full waiting rooms are quotations, not authored payload (report, never repair); they drain with the payloads themselves. Stub-file `note` annotations are schema metadata, not corpus content.

## Findings (computed)

- **Census, layered:** rules = **246** = 225 track-independent (data.all) + 12 rev5-only + 9 20x-only. Rule-level force totals {'must': 136, 'may': 20, 'should': 45, 'must-not': 11, 'should-not': 5, 'unspecified': 29}; the census's 328 merged rule-level and class-variant forces.
- **Framework-specific subsets x9** (CSX/CSF) read from info.20x.subsets / info.rev5.subsets per FedRAMP's layering (global by default, specific when needed). CORRECTION: an earlier version of this report misreported these as undeclared - a checker bug on our side, fixed after review in FedRAMP community discussion #153.
- **Zero easings across 111 class-variant modality ops**: every published class delta tightens or specifies - the Deviation channel stayed empty by measurement, not by assumption.
- Rules without base statements exist (x29) - CR26 itself models some obligations *only* as class variants; the Set+Tailoring decomposition makes that explicit.
- **Deviation ceremony question (spec feedback):** authority-published prose variants would require replace-prose(substantive)+Deviation under D13; converter parks prose variance in L2 instead - open design question for v0.6.

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
| `cr26.FRD.data.all.*.alts[]` | 188 | L1 | terminology@1 payload per term (alts, links, chrome flags inside payload) |
| `cr26.FRD.data.all.*.definition` | 75 | L1 | terminology@1 payload per term (alts, links, chrome flags inside payload) |
| `cr26.FRD.data.all.*.do_not_link` | 4 | L1 | terminology@1 payload per term (alts, links, chrome flags inside payload) |
| `cr26.FRD.data.all.*.note` | 23 | L1 | terminology@1 payload per term (alts, links, chrome flags inside payload) |
| `cr26.FRD.data.all.*.notes[]` | 7 | L1 | terminology@1 payload per term (alts, links, chrome flags inside payload) |
| `cr26.FRD.data.all.*.reference` | 13 | L1 | terminology@1 payload per term (alts, links, chrome flags inside payload) |
| `cr26.FRD.data.all.*.reference_url` | 13 | L1 | terminology@1 payload per term (alts, links, chrome flags inside payload) |
| `cr26.FRD.data.all.*.tag` | 52 | L1 | terminology@1 payload per term (alts, links, chrome flags inside payload) |
| `cr26.FRD.data.all.*.term` | 75 | L1 | terminology@1 payload per term (alts, links, chrome flags inside payload) |
| `cr26.FRD.data.all.*.updated[].comment` | 78 | L1 | history -> L0 (values not object-carried; counted) |
| `cr26.FRD.data.all.*.updated[].date` | 78 | L1 | history -> L0 (values not object-carried; counted) |
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
| `cr26.FRR.*.data.*.*.*.affects[]` | 246 | L1 | statements[0].obligated-parties[] |
| `cr26.FRR.*.data.*.*.*.artifacts.all[]` | 79 | L1 | assessment-criteria@1: required-artifacts |
| `cr26.FRR.*.data.*.*.*.corrective_actions[]` | 12 | L1 | narrative@1 / reporting-obligation@1 payload fields |
| `cr26.FRR.*.data.*.*.*.danger` | 3 | L1 | narrative@1 / reporting-obligation@1 payload fields |
| `cr26.FRR.*.data.*.*.*.examples[].examples[]` | 24 | L1 | assessment-criteria@1: examples[] {id, examples, key-tests} - the KSI-shaped test data |
| `cr26.FRR.*.data.*.*.*.examples[].id` | 5 | L1 | assessment-criteria@1: examples[] {id, examples, key-tests} - the KSI-shaped test data |
| `cr26.FRR.*.data.*.*.*.examples[].key_tests[]` | 15 | L1 | assessment-criteria@1: examples[] {id, examples, key-tests} - the KSI-shaped test data |
| `cr26.FRR.*.data.*.*.*.following_information[]` | 206 | L1 | narrative@1 / reporting-obligation@1 payload fields |
| `cr26.FRR.*.data.*.*.*.following_information_bullets[]` | 10 | L1 | narrative@1 / reporting-obligation@1 payload fields |
| `cr26.FRR.*.data.*.*.*.force` | 217 | L1 | statements[0].modality (code map) |
| `cr26.FRR.*.data.*.*.*.name` | 246 | L1 | Requirement.title |
| `cr26.FRR.*.data.*.*.*.note` | 58 | L1 | narrative@1 / reporting-obligation@1 payload fields |
| `cr26.FRR.*.data.*.*.*.notes[]` | 56 | L1 | narrative@1 / reporting-obligation@1 payload fields |
| `cr26.FRR.*.data.*.*.*.notification[].method` | 31 | L1 | reporting-obligation@1: notification[] |
| `cr26.FRR.*.data.*.*.*.notification[].name` | 31 | L1 | reporting-obligation@1: notification[] |
| `cr26.FRR.*.data.*.*.*.notification[].party` | 31 | L1 | reporting-obligation@1: notification[] |
| `cr26.FRR.*.data.*.*.*.notification[].target` | 31 | L1 | reporting-obligation@1: notification[] |
| `cr26.FRR.*.data.*.*.*.reference` | 6 | L1 | relations schema/reference -> external URL |
| `cr26.FRR.*.data.*.*.*.reference_url` | 6 | L1 | relations schema/reference -> external URL |
| `cr26.FRR.*.data.*.*.*.related[]` | 78 | L1 | relations related -> /cr26/req/<id> (dangling counted) |
| `cr26.FRR.*.data.*.*.*.schema.name` | 24 | L1 | relations schema -> url; name kept in narrative@1 |
| `cr26.FRR.*.data.*.*.*.schema.url` | 24 | L1 | relations schema -> url; name kept in narrative@1 |
| `cr26.FRR.*.data.*.*.*.statement` | 217 | L1 | statements[0].prose.en |
| `cr26.FRR.*.data.*.*.*.terms[]` | 985 | L1 | relations uses-term -> /cr26/term/<id> |
| `cr26.FRR.*.data.*.*.*.timeframe_num` | 17 | L1 | statement parameter 'timeframe' (elapsed-duration | calendar-period by unit) |
| `cr26.FRR.*.data.*.*.*.timeframe_type` | 17 | L1 | statement parameter 'timeframe' (elapsed-duration | calendar-period by unit) |
| `cr26.FRR.*.data.*.*.*.updated[].comment` | 253 | L1 | history -> L0 (counted) |
| `cr26.FRR.*.data.*.*.*.updated[].date` | 253 | L1 | history -> L0 (counted) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.artifacts.all[]` | 31 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.following_information[]` | 57 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.force` | 111 | L1 | class Tailoring op set-modality (monotone) OR + converter Deviation when easing (counted) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.note` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.1.fir.description` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.1.fir.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.1.fir.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.1.iir.description` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.1.iir.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.1.iir.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.1.oir.description` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.1.oir.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.1.oir.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.2.fir.description` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.2.fir.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.2.fir.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.2.iir.description` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.2.iir.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.2.iir.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.2.irv_lev.description` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.2.irv_lev.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.2.irv_lev.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.2.nirv_lev.description` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.2.nirv_lev.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.2.nirv_lev.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.2.nlev.description` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.2.nlev.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.2.nlev.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.2.oir.description` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.2.oir.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.2.oir.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.3.fir.description` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.3.fir.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.3.fir.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.3.iir.description` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.3.iir.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.3.iir.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.3.irv_lev.description` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.3.irv_lev.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.3.irv_lev.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.3.nirv_lev.description` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.3.nirv_lev.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.3.nirv_lev.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.3.nlev.description` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.3.nlev.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.3.nlev.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.3.oir.description` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.3.oir.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.3.oir.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.4.fir.description` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.4.fir.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.4.fir.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.4.iir.description` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.4.iir.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.4.iir.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.4.irv_lev.description` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.4.irv_lev.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.4.irv_lev.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.4.nirv_lev.description` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.4.nirv_lev.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.4.nirv_lev.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.4.nlev.description` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.4.nlev.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.4.nlev.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.4.oir.description` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.4.oir.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.4.oir.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.5.fir.description` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.5.fir.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.5.fir.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.5.iir.description` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.5.iir.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.5.iir.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.5.irv_lev.description` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.5.irv_lev.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.5.irv_lev.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.5.nirv_lev.description` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.5.nirv_lev.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.5.nirv_lev.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.5.nlev.description` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.5.nlev.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.5.nlev.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.5.oir.description` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.5.oir.timeframe_num` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.pain_timeframes.5.oir.timeframe_type` | 4 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.rev5_controls_list.AC[]` | 141 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.rev5_controls_list.AT[]` | 17 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.rev5_controls_list.AU[]` | 92 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.rev5_controls_list.CA[]` | 42 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.rev5_controls_list.CM[]` | 91 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.rev5_controls_list.CP[]` | 67 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.rev5_controls_list.IA[]` | 98 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.rev5_controls_list.IR[]` | 58 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.rev5_controls_list.MA[]` | 28 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.rev5_controls_list.MP[]` | 21 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.rev5_controls_list.PE[]` | 58 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.rev5_controls_list.PL[]` | 21 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.rev5_controls_list.PS[]` | 30 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.rev5_controls_list.RA[]` | 40 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.rev5_controls_list.SA[]` | 60 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.rev5_controls_list.SC[]` | 114 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.rev5_controls_list.SI[]` | 87 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.rev5_controls_list.SR[]` | 37 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.statement` | 111 | L2 | class-variants payload (full variant preserved; prose/artifact variance = open D13 ceremony question) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.timeframe_num` | 51 | L1 | class Tailoring op set-parameter when unit-class matches base; else L2 (counted) |
| `cr26.FRR.*.data.*.*.*.varies_by_class.*.timeframe_type` | 51 | L1 | class Tailoring op set-parameter when unit-class matches base; else L2 (counted) |
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
| `cr26.FRR.*.info.flows[].nodes.An incident is identified` | 1 | declared-drop | process-flow diagrams: linked resources, not requirement data (D17) |
| `cr26.FRR.*.info.flows[].nodes.IEC-CSO-DPR` | 1 | declared-drop | process-flow diagrams: linked resources, not requirement data (D17) |
| `cr26.FRR.*.info.flows[].nodes.IEC-CSO-EFI` | 1 | declared-drop | process-flow diagrams: linked resources, not requirement data (D17) |
| `cr26.FRR.*.info.flows[].nodes.IEC-CSO-EFR` | 1 | declared-drop | process-flow diagrams: linked resources, not requirement data (D17) |
| `cr26.FRR.*.info.flows[].nodes.IEC-CSO-FIR` | 1 | declared-drop | process-flow diagrams: linked resources, not requirement data (D17) |
| `cr26.FRR.*.info.flows[].nodes.IEC-CSO-IIR` | 1 | declared-drop | process-flow diagrams: linked resources, not requirement data (D17) |
| `cr26.FRR.*.info.flows[].nodes.IEC-CSO-OIR` | 1 | declared-drop | process-flow diagrams: linked resources, not requirement data (D17) |
| `cr26.FRR.*.info.flows[].nodes.Incident Evaluation and Communication are complete.` | 1 | declared-drop | process-flow diagrams: linked resources, not requirement data (D17) |
| `cr26.FRR.*.info.flows[].steps[].description` | 7 | declared-drop | process-flow diagrams: linked resources, not requirement data (D17) |
| `cr26.FRR.*.info.flows[].steps[].from` | 9 | declared-drop | process-flow diagrams: linked resources, not requirement data (D17) |
| `cr26.FRR.*.info.flows[].steps[].to` | 9 | declared-drop | process-flow diagrams: linked resources, not requirement data (D17) |
| `cr26.FRR.*.info.name` | 17 | L1 | family Set: title/label/lifecycle |
| `cr26.FRR.*.info.purpose` | 17 | L1 | family Set: narrative description / scope tag |
| `cr26.FRR.*.info.rev5.effective.current_status` | 10 | L1 | effectivity@1 on family Set (default / per-track) |
| `cr26.FRR.*.info.rev5.effective.date.grace.default` | 10 | L1 | effectivity@1 on family Set (default / per-track) |
| `cr26.FRR.*.info.rev5.effective.date.grace.until_next_assessment` | 10 | L1 | effectivity@1 on family Set (default / per-track) |
| `cr26.FRR.*.info.rev5.effective.date.maintain` | 10 | L1 | effectivity@1 on family Set (default / per-track) |
| `cr26.FRR.*.info.rev5.effective.date.obtain` | 10 | L1 | effectivity@1 on family Set (default / per-track) |
| `cr26.FRR.*.info.rev5.effective.date.optional_adoption` | 10 | L1 | effectivity@1 on family Set (default / per-track) |
| `cr26.FRR.*.info.rev5.effective.is` | 10 | L1 | effectivity@1 on family Set (default / per-track) |
| `cr26.FRR.*.info.rev5.subsets.*.applicability.affects[]` | 5 | L1 | framework-specific subset declarations -> track subset Sets (title/description/scope) [corrected per FedRAMP #153] |
| `cr26.FRR.*.info.rev5.subsets.*.applicability.classes[]` | 16 | L1 | framework-specific subset declarations -> track subset Sets (title/description/scope) [corrected per FedRAMP #153] |
| `cr26.FRR.*.info.rev5.subsets.*.applicability.paths[]` | 10 | L1 | framework-specific subset declarations -> track subset Sets (title/description/scope) [corrected per FedRAMP #153] |
| `cr26.FRR.*.info.rev5.subsets.*.applicability.types[]` | 5 | L1 | framework-specific subset declarations -> track subset Sets (title/description/scope) [corrected per FedRAMP #153] |
| `cr26.FRR.*.info.rev5.subsets.*.description` | 5 | L1 | framework-specific subset declarations -> track subset Sets (title/description/scope) [corrected per FedRAMP #153] |
| `cr26.FRR.*.info.rev5.subsets.*.name` | 5 | L1 | framework-specific subset declarations -> track subset Sets (title/description/scope) [corrected per FedRAMP #153] |
| `cr26.FRR.*.info.short_name` | 17 | L1 | family Set: title/label/lifecycle |
| `cr26.FRR.*.info.status` | 17 | L1 | family Set: title/label/lifecycle |
| `cr26.FRR.*.info.subsets.*.applicability.affects[]` | 45 | L1 | scope@1 on subset Set (types/paths/classes/affects) + class & type Set composition |
| `cr26.FRR.*.info.subsets.*.applicability.classes[]` | 125 | L1 | scope@1 on subset Set (types/paths/classes/affects) + class & type Set composition |
| `cr26.FRR.*.info.subsets.*.applicability.paths[]` | 78 | L1 | scope@1 on subset Set (types/paths/classes/affects) + class & type Set composition |
| `cr26.FRR.*.info.subsets.*.applicability.types[]` | 78 | L1 | scope@1 on subset Set (types/paths/classes/affects) + class & type Set composition |
| `cr26.FRR.*.info.subsets.*.description` | 45 | L1 | subset Set: title / narrative description |
| `cr26.FRR.*.info.subsets.*.name` | 45 | L1 | subset Set: title / narrative description |
| `cr26.FRR.*.info.tag` | 17 | L1 | family Set: narrative description / scope tag |
| `cr26.FRR.*.info.web_name` | 17 | L1 | family Set annotations.web_name (chrome) |
| `cr26.KSI.*.id` | 10 | L1 | KSI category Set: id/title/label/annotations/lifecycle |
| `cr26.KSI.*.indicators.*.controls[]` | 373 | L1 | Mapping objects (relationship supports; 8.6 untyped-import rule) |
| `cr26.KSI.*.indicators.*.name` | 46 | L1 | KSI Requirement.title |
| `cr26.KSI.*.indicators.*.statement` | 41 | L1 | KSI statements[0].prose.en (modality unspecified: indicator language) |
| `cr26.KSI.*.indicators.*.terms[]` | 91 | L1 | relations uses-term |
| `cr26.KSI.*.indicators.*.updated[].comment` | 46 | L1 | history -> L0 (counted) |
| `cr26.KSI.*.indicators.*.updated[].date` | 46 | L1 | history -> L0 (counted) |
| `cr26.KSI.*.indicators.*.varies_by_class.*.statement` | 10 | L2 | class-variants payload on the KSI Requirement |
| `cr26.KSI.*.name` | 10 | L1 | KSI category Set: id/title/label/annotations/lifecycle |
| `cr26.KSI.*.short_name` | 10 | L1 | KSI category Set: id/title/label/annotations/lifecycle |
| `cr26.KSI.*.status` | 10 | L1 | KSI category Set: id/title/label/annotations/lifecycle |
| `cr26.KSI.*.web_name` | 10 | L1 | KSI category Set: id/title/label/annotations/lifecycle |
| `cr26.info.default_artifacts.FRR[]` | 5 | L1 | assessment-criteria on corpus root: default-artifacts |
| `cr26.info.default_artifacts.KSI[]` | 5 | L1 | assessment-criteria on corpus root: default-artifacts |
| `cr26.info.description` | 1 | L1 | bundle manifest / L0 provenance; description -> narrative on corpus root |
| `cr26.info.last_updated` | 1 | L1 | bundle manifest / L0 provenance; description -> narrative on corpus root |
| `cr26.info.title` | 1 | L1 | bundle manifest / L0 provenance; description -> narrative on corpus root |
| `cr26.info.version` | 1 | L1 | bundle manifest / L0 provenance; description -> narrative on corpus root |

## UNMAPPED (gate target: zero)

*(none)*
