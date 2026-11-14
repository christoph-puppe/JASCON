# BSI Grundschutz++ -> Semantic Core: Coverage Report (computed)

Source: **Anwenderkatalog Grundschutz++** v2026-07-16T05:11:52.605669+00:00 — single-catalog mode: **MS-TLS dropped by decision 2026-07-21** (its defects were reported to BSI; the twin-catalog finding — 11 shared ids, 10 silently diverged, census 2026-07-03 — stays on the record in census and handbook).

## Totals

- Source leaf values inventoried: **49,431**
- Mapped: **49,431** -> **UNMAPPED: 0** -> coverage **100.0 %**
- That is a count of source paths with a declared fate, not of values that arrived. Followed value by value (conversion ledger, below): **34,421** are in the bundle, **15,004** are no content by a rule the ledger checks, **6** are dropped for a declared reason, **0** are unaccounted.
- Emitted: **999 Requirements**, one for every control at every depth (651 top-level and 348 nested; nesting reaches depth 3), each with one statement (999); **288 Sets**: 159 of a group, 126 of a control with nested controls, 2 baselines, 1 root; manifest with both digests, 6 pinned facet stubs.

## Conversion rules (declared, counted)

- **Modality** from `modal_verb` (code map incl. DARF NUR -> may-only): should x626, may x224, must x149; no unknown verbs.
- **Obligated party**: `https://ns.bsi.bund.de/gspp/party/institution` on every statement. This is the converter's default and not a value of the source; `--obligated-party URI` writes another. Why this default: the catalogue carries no party on a control; `Institution` is the word its prose uses for the organisation that applies it. The subject a statement names before its modal verb is the practice that organisation runs, not a party (decided by the author on 2026-11-14).
- **Every control is a Requirement of its own**, at every depth, with its own statement (id `smt`), parameters, props and links. BSI nests controls for grouping only (the author, 2026-11-14), so the nesting is carried as grouping: a control that has nested controls (126) gives a Set as well, titled as the control, with the id `.../set/tax/` and the control id in lower case with hyphens. Its members are the control's own Requirement first and then what stands for each nested control in source order (a Requirement, or such a Set in turn). In the Set of the group, and of a parent control, that Set stands where the control stood. No relation is written between a control and the controls nested in it.
- **{{ insert: param, x }}** in prose -> `{param:x}` tokens; params typed `string` with **first-class `label` + `default`** (D9 rev, backlog #1) - x221 parameters, the param-extras residue drains to alt-identifier uuids only. Params never referenced by a `{param:}` token in their statement's prose: x0 (counted - source QA signal); multi-value params x0 (first value becomes default, every value is kept in compat param-extras).
- **Payload free text language-tagged** per corpus language (`{de: ...}` on statement prose, guidance, Set descriptions) - this corpus was born tagged; harmonization rule (backlog #12) verified, not applied.
- **Grammar** (action_word/result/result_specification/target_object_categories) -> `statement-grammar@1` by-statement; **documentation** -> `assessment-criteria@1` required-documentation; **C/I/A/Auth + threats** -> `security-objectives@1` (threat codes minted from 'G 0.x'); **sec_level/effort/tags/class** -> `gspp-taxonomy@1`; **guidance parts** -> `gspp-narrative@1`.
- **Baselines** from the `sec_level` of every control, nested ones included (a nested control is a full control and has a level of its own): gspp:erhöht (227), gspp:normal-SdT (772).
- **alt-identifier** -> aliases (scheme bsi-uuid) on the Requirement of every control and on the Set of every group. The namespaces of the props (the addresses of BSI's CSV lists) are no content: this mapping is written for exactly those, and the ledger checks every one of them.
- **Document metadata** -> the root Set, which stands for the document: its title, and the version on every object, are kernel members; everything else (last-modified, the OSCAL version, props, links, roles, parties, responsible parties, remarks) stands under the compat facet's `metadata` in the source's own shape. The manifest's provenance names the source with its title, version and OSCAL version, and by the rule of backlog #69 its author (the party the metadata names as creator, as a landmark URI) and its date (the day of last-modified).

## Findings (computed)

- **List values packed into one string: 781** - `tags` 125 of 470, `threats` 616 of 900, `target_object_categories` 40 of 634, `documentation` 0 of 960. Several vocabulary terms joined by commas in ONE prop value, where OSCAL repeats the prop once per value and JSON has arrays. The string is schema-valid, so no OSCAL validator sees the list, and none can check its terms against the vocabulary; every consumer has to know to split. The converter splits on `,` (rules above) and REPORTS the source form for the authors' queue (handbook 14.5). Full list in the JSON report; first three `tags` values:
    - `GC.3.1.1`: "Compliance Management, Inventories"
    - `ASST.3.10`: "Lieferketten, Shadow IT"
    - `ASST.3.11`: "Data Leak, Shadow IT"
- **Parameter slots in the sentence template: 221** `{{Label}}` in result/result_specification values - parameters, not defects: 221 stand exactly where the statement prose inserts a parameter (`{{ insert: param, x }}`), 219 repeat the label of a parameter declared on the same control (other wording: `GC.1.1` "einem anerkannten Standard", `NOT.1.1.4` "Reaktiv-, Aufbau- oder Standard-"). Carried verbatim in `statement-grammar@1`.
- **Census delta (source moved)**: catalog v2026-07-16 vs. census v2026-07-03 - controls 999 (census 998), packed `tags` values 125 (census GS++-only 125). Deltas are the authors editing the catalog between snapshots; every claim in this report re-verifies against the version named above.
- **Tag spelling drift** (space vs hyphen variants coexist): {'Compliance Management': 6} - reported, not normalized.
- **sec_level value space observed**: {'normal-SdT': 772, 'erhöht': 227} (note the bare 'erhöht' vs 'normal-SdT' asymmetry - vocabulary drift the pinned schema now freezes).

## Conversion ledger (measured per source value)

- **Totals**: the path map says where each source path goes. The ledger follows each of the 49,431 source leaf values into the written bundle and reads every claim back from the 1,294 files of the bundle. **22,626 copied** (the value stands, with its type, at the destination named), **11,795 transformed** (a named rule made the destination from it; the rule was applied to the source again and compared), **15,004 no content** (a name that only selects a field, a namespace, an id that is rebuilt exactly: each by a rule the ledger checked on the source's own values), **6 intentionally dropped** (a declared reason), **0 unaccounted**. Checks that failed: 0. A value is traced by what the converter did with it; an equal value elsewhere in the bundle does not count. A run with an unaccounted value or a failed check ends with a non-zero exit code. The record is `bsi-conversion-ledger.json`: one row per source path and outcome, with the number of values, the first of them, and where they went, by which rule they are no content, or why they were dropped.
- **No content, by 4 checked rules: 15,004.** Such a value is not written, and nothing is lost without it. The ledger applies each rule to the source's own value, and a value the rule does not cover is carried instead (or ends the run).
    - x999 (rebuilt-id): the id of a statement part is its control's id and `_stm`
    - x997 (rebuilt-id): the id of a guidance part is its control's id and `_gdn`
    - x999 (selector): the name `statement` of a part selects the part whose prose and props become the statement
    - x12,009 (namespace): the namespace of a prop is the one this mapping is written for (PROP_NS)
- **Names and values**: 14,544 of the 34,421 values in the bundle are names. The name of a prop, or of the guidance part, holds no content of its own: it selects the field its value is written to. 6,445 stand in the bundle as the key of that field, unchanged, and nowhere as a value (counted as copied); 8,099 are mapped to a field of another name or to the alias scheme (counted as transformed). The other 19,877 are ids, texts and codes.
- **Rules: 22 named, 20 applied to this catalogue.** Behind each, the number of source values it was applied to; a value can pass through more than one. Where a rule leaves a value as it is, the value counts as copied: a prose without a parameter token, a list prop with one term, a prop whose field has the prop's own name.
    - x999: requirement URI from the control id
    - x999: file path of a Requirement from the control id
    - x266: requirement URI from a link to a control (#id)
    - x0: a link that names a back-matter resource (#uuid): the address the resource gives
    - x159: taxonomy Set URI from the group id
    - x159: file path of a taxonomy Set from the group id
    - x126: URI of the Set that stands for a control with nested controls, from the control id
    - x126: file path of the Set that stands for a control with nested controls, from the control id
    - x999: baseline Set URI from the sec_level of a control
    - x999: baseline Set title from the sec_level of a control
    - x999: file path of a baseline Set from the sec_level of a control
    - x999: a sec_level value as an entry of the enum of observed values in the pinned taxonomy schema
    - x208: statement prose with every {{ insert: param, x }} rewritten to {param:x}
    - x999: modality code from the modal verb (MODAL)
    - x165: one term of a list packed into one string (split on commas, trimmed)
    - x900: threat URI from one term of the threats list (split on commas, trimmed, spaces to hyphens)
    - x999: effort level as an integer
    - x6,941: field name from the prop name (FIELD)
    - x1,158: alias scheme from the prop name (ALIAS_SCHEME)
    - x1: author of the document: the one party its metadata names for it (as creator, else as prepared-by, else the one party it names), as a landmark URI from the party's name
    - x1: date of the document: the day of its last-modified
    - x0: a number that is no integer, written as a decimal string (the kernel's spelling of a fraction, NUMBER-1)
- **Carried as the source holds it** (compat facet `oscal-1x@1`), because neither the kernel nor a standard facet has a member for it: the document metadata on the root Set; in this catalogue nothing else: the mapping reads every prop, part and member the controls and groups hold.
- **Declared drops that remain: 6**, in the table at the end of this report. They stay declared until the author has gone through them.
- **The written bundle, read back and held against the source** (counted from the files on disk and from the source as loaded): 999 controls at all depths -> 999 Requirements, 999 of them of a control, 999 with exactly one statement; 126 controls with nested controls -> 126 Sets that list the control's own Requirement first and then one member for each nested control; 266 links of controls (75 of them on nested controls) -> 266 are a relation of their own control's Requirement; 266 relations in the bundle, 0 of them name no object of the bundle; 2,283 members of Sets, 0 of them name no object.
- **The path map held against the ledger: 0 values disagree.** Every row of the path map names, beside its sentence, what may become of the values of its paths (carried, no content by a checked rule, or dropped for a declared reason) and the places at which a carried value may stand. Each run compares both with what the ledger found for every value, and a disagreement ends the run with an error. No value has an outcome its row does not allow, and none stands at a place its row does not name.
- **What the ledger cannot see**: it follows source values into the bundle, not the other way round. 5,790 of the 32,904 leaf values of the 1,287 objects have no source value behind them. The converter writes them on its own and none has a row in the ledger: `/id` x1 (the id of the root Set, and of a Set whose group has no id); `/lifecycle` x1,287 (`active`: the source states no status of a control or a group, and the kernel requires the member); `/members/[]/sequence` x2,283 (the order of the members of a Set); `/statements/[]/id` x999 (the statement id `smt`); `/statements/[]/obligated-parties/[]` x999 (the obligated party `https://ns.bsi.bund.de/gspp/party/institution`, the converter's default); `/statements/[]/parameters/[]/type` x221 (`string`, the type of every parameter). The manifest adds 2,603 values of its own (digests, the paths and versions of the pinned schemas, the converter line), the pinned schemas 92. Two more limits. The ledger checks the URI of a baseline Set against the sec_level of every control that names it; that the Requirement of that control is listed in that Set it does not check. And it checks that a rule gives what the file holds, not that the rule is the right one: a rule whose function is changed changes the bundle and no figure of the ledger. That the bundle is byte for byte the committed one is held apart from it, by the Validators workflow, which converts the pinned source again and compares.

## Full path map
| path | count | level | destination |
|---|---:|---|---|
| `catalog.back-matter.resources[].rlinks[].hashes[].algorithm` | 1 | - | a resource that a link of a control names by #uuid gives that link its address (relations[].ref) and is carried whole on the root Set (compat `back-matter`); a resource no link of a control names is not carried: a declared drop, listed in the report for the author's decision |
| `catalog.back-matter.resources[].rlinks[].hashes[].value` | 1 | - | a resource that a link of a control names by #uuid gives that link its address (relations[].ref) and is carried whole on the root Set (compat `back-matter`); a resource no link of a control names is not carried: a declared drop, listed in the report for the author's decision |
| `catalog.back-matter.resources[].rlinks[].href` | 1 | - | a resource that a link of a control names by #uuid gives that link its address (relations[].ref) and is carried whole on the root Set (compat `back-matter`); a resource no link of a control names is not carried: a declared drop, listed in the report for the author's decision |
| `catalog.back-matter.resources[].title` | 1 | - | a resource that a link of a control names by #uuid gives that link its address (relations[].ref) and is carried whole on the root Set (compat `back-matter`); a resource no link of a control names is not carried: a declared drop, listed in the report for the author's decision |
| `catalog.back-matter.resources[].uuid` | 1 | - | a resource that a link of a control names by #uuid gives that link its address (relations[].ref) and is carried whole on the root Set (compat `back-matter`); a resource no link of a control names is not carried: a declared drop, listed in the report for the author's decision |
| `catalog.groups[].groups[].controls[].class` | 651 | L1 | gspp-taxonomy: class (by-statement) |
| `catalog.groups[].groups[].controls[].controls[].class` | 327 | L1 | gspp-taxonomy: class (by-statement) |
| `catalog.groups[].groups[].controls[].controls[].controls[].class` | 19 | L1 | gspp-taxonomy: class (by-statement) |
| `catalog.groups[].groups[].controls[].controls[].controls[].controls[].class` | 2 | L1 | gspp-taxonomy: class (by-statement) |
| `catalog.groups[].groups[].controls[].controls[].controls[].controls[].id` | 2 | L1 | Requirement id, label and file of the control, at every depth, and where it is listed; a control with nested controls: also the id and the file of the Set that groups it with them |
| `catalog.groups[].groups[].controls[].controls[].controls[].controls[].parts[].id` | 4 | - | no content: rebuilt exactly, the control's id and `_stm` or `_gdn`, a rule the ledger checks. An id the rule does not give is carried (compat `parts`) |
| `catalog.groups[].groups[].controls[].controls[].controls[].controls[].parts[].name` | 4 | L1 | `guidance` -> the key of the gspp-narrative payload; `statement` -> no content: it selects the part whose prose and props become the statement, a rule the ledger checks. A part of another name is carried whole (compat `parts`) |
| `catalog.groups[].groups[].controls[].controls[].controls[].controls[].parts[].props[].name` | 7 | L1 | dispatch by part-prop name (grammar/objectives/criteria; packed lists reported); a prop the mapping does not read: compat `parts` |
| `catalog.groups[].groups[].controls[].controls[].controls[].controls[].parts[].props[].ns` | 7 | - | no content: the namespace this mapping is written for (PROP_NS), a rule the ledger checks. A prop in another namespace is not read and is carried whole (compat `parts`) |
| `catalog.groups[].groups[].controls[].controls[].controls[].controls[].parts[].props[].value` | 7 | L1 | dispatch by part-prop name (grammar/objectives/criteria; packed lists reported); a prop the mapping does not read: compat `parts` |
| `catalog.groups[].groups[].controls[].controls[].controls[].controls[].parts[].prose` | 4 | L1 | statements[].prose.de ({{insert}} -> {param:}) / gspp-narrative guidance |
| `catalog.groups[].groups[].controls[].controls[].controls[].controls[].props[].name` | 6 | L1 | dispatch by prop name (see per-prop table); a prop the mapping does not read: compat `props` |
| `catalog.groups[].groups[].controls[].controls[].controls[].controls[].props[].ns` | 4 | - | no content: the namespace this mapping is written for (PROP_NS), a rule the ledger checks. A prop in another namespace is not read and is carried whole (compat `props`) |
| `catalog.groups[].groups[].controls[].controls[].controls[].controls[].props[].value` | 6 | L1 | dispatch by prop name (see per-prop table); a prop the mapping does not read: compat `props` |
| `catalog.groups[].groups[].controls[].controls[].controls[].controls[].title` | 2 | L1 | Requirement title; a control with nested controls: also the title of its grouping Set |
| `catalog.groups[].groups[].controls[].controls[].controls[].id` | 19 | L1 | Requirement id, label and file of the control, at every depth, and where it is listed; a control with nested controls: also the id and the file of the Set that groups it with them |
| `catalog.groups[].groups[].controls[].controls[].controls[].links[].href` | 8 | L1 | relations[] {type=rel, ref} of the control's own Requirement, at every depth (#control -> req URI; #uuid -> back-matter URL) |
| `catalog.groups[].groups[].controls[].controls[].controls[].links[].rel` | 8 | L1 | relations[] {type=rel, ref} of the control's own Requirement, at every depth (#control -> req URI; #uuid -> back-matter URL) |
| `catalog.groups[].groups[].controls[].controls[].controls[].params[].id` | 4 | L1 | statement parameter name (type string); key of compat param-extras |
| `catalog.groups[].groups[].controls[].controls[].controls[].params[].label` | 4 | L1 | parameter label / default - first-class since the D9 rev (backlog #1); more than one value: all of them in compat param-extras |
| `catalog.groups[].groups[].controls[].controls[].controls[].params[].props[].name` | 4 | L2 | compat oscal-1x: param-extras (param alt-identifier only) |
| `catalog.groups[].groups[].controls[].controls[].controls[].params[].props[].value` | 4 | L2 | compat oscal-1x: param-extras (param alt-identifier only) |
| `catalog.groups[].groups[].controls[].controls[].controls[].parts[].id` | 37 | - | no content: rebuilt exactly, the control's id and `_stm` or `_gdn`, a rule the ledger checks. An id the rule does not give is carried (compat `parts`) |
| `catalog.groups[].groups[].controls[].controls[].controls[].parts[].name` | 37 | L1 | `guidance` -> the key of the gspp-narrative payload; `statement` -> no content: it selects the part whose prose and props become the statement, a rule the ledger checks. A part of another name is carried whole (compat `parts`) |
| `catalog.groups[].groups[].controls[].controls[].controls[].parts[].props[].name` | 95 | L1 | dispatch by part-prop name (grammar/objectives/criteria; packed lists reported); a prop the mapping does not read: compat `parts` |
| `catalog.groups[].groups[].controls[].controls[].controls[].parts[].props[].ns` | 95 | - | no content: the namespace this mapping is written for (PROP_NS), a rule the ledger checks. A prop in another namespace is not read and is carried whole (compat `parts`) |
| `catalog.groups[].groups[].controls[].controls[].controls[].parts[].props[].value` | 95 | L1 | dispatch by part-prop name (grammar/objectives/criteria; packed lists reported); a prop the mapping does not read: compat `parts` |
| `catalog.groups[].groups[].controls[].controls[].controls[].parts[].prose` | 37 | L1 | statements[].prose.de ({{insert}} -> {param:}) / gspp-narrative guidance |
| `catalog.groups[].groups[].controls[].controls[].controls[].props[].name` | 131 | L1 | dispatch by prop name (see per-prop table); a prop the mapping does not read: compat `props` |
| `catalog.groups[].groups[].controls[].controls[].controls[].props[].ns` | 112 | - | no content: the namespace this mapping is written for (PROP_NS), a rule the ledger checks. A prop in another namespace is not read and is carried whole (compat `props`) |
| `catalog.groups[].groups[].controls[].controls[].controls[].props[].value` | 131 | L1 | dispatch by prop name (see per-prop table); a prop the mapping does not read: compat `props` |
| `catalog.groups[].groups[].controls[].controls[].controls[].title` | 19 | L1 | Requirement title; a control with nested controls: also the title of its grouping Set |
| `catalog.groups[].groups[].controls[].controls[].id` | 327 | L1 | Requirement id, label and file of the control, at every depth, and where it is listed; a control with nested controls: also the id and the file of the Set that groups it with them |
| `catalog.groups[].groups[].controls[].controls[].links[].href` | 67 | L1 | relations[] {type=rel, ref} of the control's own Requirement, at every depth (#control -> req URI; #uuid -> back-matter URL) |
| `catalog.groups[].groups[].controls[].controls[].links[].rel` | 67 | L1 | relations[] {type=rel, ref} of the control's own Requirement, at every depth (#control -> req URI; #uuid -> back-matter URL) |
| `catalog.groups[].groups[].controls[].controls[].params[].id` | 73 | L1 | statement parameter name (type string); key of compat param-extras |
| `catalog.groups[].groups[].controls[].controls[].params[].label` | 73 | L1 | parameter label / default - first-class since the D9 rev (backlog #1); more than one value: all of them in compat param-extras |
| `catalog.groups[].groups[].controls[].controls[].params[].props[].name` | 73 | L2 | compat oscal-1x: param-extras (param alt-identifier only) |
| `catalog.groups[].groups[].controls[].controls[].params[].props[].value` | 73 | L2 | compat oscal-1x: param-extras (param alt-identifier only) |
| `catalog.groups[].groups[].controls[].controls[].params[].values[]` | 1 | L1 | parameter label / default - first-class since the D9 rev (backlog #1); more than one value: all of them in compat param-extras |
| `catalog.groups[].groups[].controls[].controls[].parts[].id` | 653 | - | no content: rebuilt exactly, the control's id and `_stm` or `_gdn`, a rule the ledger checks. An id the rule does not give is carried (compat `parts`) |
| `catalog.groups[].groups[].controls[].controls[].parts[].name` | 653 | L1 | `guidance` -> the key of the gspp-narrative payload; `statement` -> no content: it selects the part whose prose and props become the statement, a rule the ledger checks. A part of another name is carried whole (compat `parts`) |
| `catalog.groups[].groups[].controls[].controls[].parts[].props[].name` | 1,632 | L1 | dispatch by part-prop name (grammar/objectives/criteria; packed lists reported); a prop the mapping does not read: compat `parts` |
| `catalog.groups[].groups[].controls[].controls[].parts[].props[].ns` | 1,632 | - | no content: the namespace this mapping is written for (PROP_NS), a rule the ledger checks. A prop in another namespace is not read and is carried whole (compat `parts`) |
| `catalog.groups[].groups[].controls[].controls[].parts[].props[].value` | 1,632 | L1 | dispatch by part-prop name (grammar/objectives/criteria; packed lists reported); a prop the mapping does not read: compat `parts` |
| `catalog.groups[].groups[].controls[].controls[].parts[].prose` | 653 | L1 | statements[].prose.de ({{insert}} -> {param:}) / gspp-narrative guidance |
| `catalog.groups[].groups[].controls[].controls[].props[].name` | 2,589 | L1 | dispatch by prop name (see per-prop table); a prop the mapping does not read: compat `props` |
| `catalog.groups[].groups[].controls[].controls[].props[].ns` | 2,262 | - | no content: the namespace this mapping is written for (PROP_NS), a rule the ledger checks. A prop in another namespace is not read and is carried whole (compat `props`) |
| `catalog.groups[].groups[].controls[].controls[].props[].value` | 2,589 | L1 | dispatch by prop name (see per-prop table); a prop the mapping does not read: compat `props` |
| `catalog.groups[].groups[].controls[].controls[].title` | 327 | L1 | Requirement title; a control with nested controls: also the title of its grouping Set |
| `catalog.groups[].groups[].controls[].id` | 651 | L1 | Requirement id, label and file of the control, at every depth, and where it is listed; a control with nested controls: also the id and the file of the Set that groups it with them |
| `catalog.groups[].groups[].controls[].links[].href` | 191 | L1 | relations[] {type=rel, ref} of the control's own Requirement, at every depth (#control -> req URI; #uuid -> back-matter URL) |
| `catalog.groups[].groups[].controls[].links[].rel` | 191 | L1 | relations[] {type=rel, ref} of the control's own Requirement, at every depth (#control -> req URI; #uuid -> back-matter URL) |
| `catalog.groups[].groups[].controls[].params[].id` | 144 | L1 | statement parameter name (type string); key of compat param-extras |
| `catalog.groups[].groups[].controls[].params[].label` | 144 | L1 | parameter label / default - first-class since the D9 rev (backlog #1); more than one value: all of them in compat param-extras |
| `catalog.groups[].groups[].controls[].params[].props[].name` | 144 | L2 | compat oscal-1x: param-extras (param alt-identifier only) |
| `catalog.groups[].groups[].controls[].params[].props[].value` | 144 | L2 | compat oscal-1x: param-extras (param alt-identifier only) |
| `catalog.groups[].groups[].controls[].params[].values[]` | 1 | L1 | parameter label / default - first-class since the D9 rev (backlog #1); more than one value: all of them in compat param-extras |
| `catalog.groups[].groups[].controls[].parts[].id` | 1,302 | - | no content: rebuilt exactly, the control's id and `_stm` or `_gdn`, a rule the ledger checks. An id the rule does not give is carried (compat `parts`) |
| `catalog.groups[].groups[].controls[].parts[].name` | 1,302 | L1 | `guidance` -> the key of the gspp-narrative payload; `statement` -> no content: it selects the part whose prose and props become the statement, a rule the ledger checks. A part of another name is carried whole (compat `parts`) |
| `catalog.groups[].groups[].controls[].parts[].props[].name` | 3,308 | L1 | dispatch by part-prop name (grammar/objectives/criteria; packed lists reported); a prop the mapping does not read: compat `parts` |
| `catalog.groups[].groups[].controls[].parts[].props[].ns` | 3,308 | - | no content: the namespace this mapping is written for (PROP_NS), a rule the ledger checks. A prop in another namespace is not read and is carried whole (compat `parts`) |
| `catalog.groups[].groups[].controls[].parts[].props[].value` | 3,308 | L1 | dispatch by part-prop name (grammar/objectives/criteria; packed lists reported); a prop the mapping does not read: compat `parts` |
| `catalog.groups[].groups[].controls[].parts[].prose` | 1,302 | L1 | statements[].prose.de ({{insert}} -> {param:}) / gspp-narrative guidance |
| `catalog.groups[].groups[].controls[].props[].name` | 5,240 | L1 | dispatch by prop name (see per-prop table); a prop the mapping does not read: compat `props` |
| `catalog.groups[].groups[].controls[].props[].ns` | 4,589 | - | no content: the namespace this mapping is written for (PROP_NS), a rule the ledger checks. A prop in another namespace is not read and is carried whole (compat `props`) |
| `catalog.groups[].groups[].controls[].props[].value` | 5,240 | L1 | dispatch by prop name (see per-prop table); a prop the mapping does not read: compat `props` |
| `catalog.groups[].groups[].controls[].title` | 651 | L1 | Requirement title; a control with nested controls: also the title of its grouping Set |
| `catalog.groups[].groups[].id` | 139 | L1 | taxonomy Set of the group: its id, its file, and where it is listed |
| `catalog.groups[].groups[].props[].name` | 278 | L1 | Set.label / Set.aliases (bsi-uuid) |
| `catalog.groups[].groups[].props[].value` | 278 | L1 | Set.label / Set.aliases (bsi-uuid) |
| `catalog.groups[].groups[].title` | 139 | L1 | taxonomy Set of the group: its title |
| `catalog.groups[].id` | 20 | L1 | taxonomy Set of the group: its id, its file, and where it is listed |
| `catalog.groups[].props[].name` | 40 | L1 | Set.label / Set.aliases (bsi-uuid) |
| `catalog.groups[].props[].remarks` | 20 | L1 | gspp-narrative on the Set: layer/Praktik description |
| `catalog.groups[].props[].value` | 40 | L1 | Set.label / Set.aliases (bsi-uuid) |
| `catalog.groups[].title` | 20 | L1 | taxonomy Set of the group: its title |
| `catalog.metadata.last-modified` | 1 | L2 | root Set, compat oscal-1x `metadata`, as the source holds it; its day -> manifest provenance.sources[].date |
| `catalog.metadata.links[].href` | 1 | L2 | root Set, compat oscal-1x `metadata`: the member as the source holds it |
| `catalog.metadata.links[].rel` | 1 | L2 | root Set, compat oscal-1x `metadata`: the member as the source holds it |
| `catalog.metadata.links[].text` | 1 | L2 | root Set, compat oscal-1x `metadata`: the member as the source holds it |
| `catalog.metadata.oscal-version` | 1 | L2 | root Set, compat oscal-1x `metadata`, as the source holds it; manifest provenance.sources[].oscal-version |
| `catalog.metadata.parties[].email-addresses[]` | 1 | L2 | root Set, compat oscal-1x `metadata`: the member as the source holds it |
| `catalog.metadata.parties[].name` | 1 | L2 | root Set, compat oscal-1x `metadata`, as the source holds it; the name of the party the metadata names as author -> manifest provenance.sources[].author-ref (a landmark URI) |
| `catalog.metadata.parties[].type` | 1 | L2 | root Set, compat oscal-1x `metadata`: the member as the source holds it |
| `catalog.metadata.parties[].uuid` | 1 | L2 | root Set, compat oscal-1x `metadata`: the member as the source holds it |
| `catalog.metadata.props[].name` | 3 | L2 | root Set, compat oscal-1x `metadata`: the member as the source holds it |
| `catalog.metadata.props[].ns` | 1 | L2 | root Set, compat oscal-1x `metadata`: the member as the source holds it |
| `catalog.metadata.props[].value` | 3 | L2 | root Set, compat oscal-1x `metadata`: the member as the source holds it |
| `catalog.metadata.remarks` | 1 | L2 | root Set, compat oscal-1x `metadata`: the member as the source holds it |
| `catalog.metadata.responsible-parties[].party-uuids[]` | 1 | L2 | root Set, compat oscal-1x `metadata`: the member as the source holds it |
| `catalog.metadata.responsible-parties[].role-id` | 1 | L2 | root Set, compat oscal-1x `metadata`: the member as the source holds it |
| `catalog.metadata.roles[].id` | 1 | L2 | root Set, compat oscal-1x `metadata`: the member as the source holds it |
| `catalog.metadata.roles[].title` | 1 | L2 | root Set, compat oscal-1x `metadata`: the member as the source holds it |
| `catalog.metadata.title` | 1 | L1 | title of the root Set; manifest provenance.sources[].title |
| `catalog.metadata.version` | 1 | L1 | `version` of every object, and of its entry in the manifest; manifest provenance.sources[].version |
| `catalog.uuid` | 1 | - | not carried: a declared drop, listed in the report for the author's decision |

## Per-prop dispatch
| prop | level | destination |
|---|---|---|
| `alt-identifier` | L1 | Requirement.aliases (scheme bsi-uuid) |
| `label` | L1 | Requirement.label (the control id where a control has no label prop) |
| `sec_level` | L1 | gspp-taxonomy: sec-level (by-statement); the baseline Set of that level, in which the Requirement is listed: its id, title and file; the enum of observed values in the pinned taxonomy schema |
| `effort_level` | L1 | gspp-taxonomy: effort (by-statement) |
| `tags` | L1 | gspp-taxonomy: tags[] (comma-split; packed lists and inconsistencies reported) |
| `confidentiality` | L1 | security-objectives (by-statement) |
| `integrity` | L1 | security-objectives (by-statement) |
| `availability` | L1 | security-objectives (by-statement) |
| `authenticity` | L1 | security-objectives (by-statement) |
| `threats` | L1 | security-objectives threat-refs[] (comma-split, packed lists reported; minted threat code URIs) |
| `modal_verb` | L1 | statements[].modality (mapped code system) |
| `action_word` | L1 | statement-grammar: action (by-statement) |
| `result` | L1 | statement-grammar: result (by-statement) |
| `result_specification` | L1 | statement-grammar: result-specification (by-statement) |
| `target_object_categories` | L1 | statement-grammar: target-object-categories[] (by-statement; comma-split, packed lists reported) |
| `documentation` | L1 | assessment-criteria: required-documentation[] (by-statement; comma-split, packed lists reported) |

## UNMAPPED (gate target: zero)

*(none)*

## Declared drops that remain (for the author's decision)

6 values. They were declared on 2026-11-14 as classes decided for the IFA corpus and stay declared until the author has gone through them; this run adds none. The last column is this converter's reading under the author's rule of 2026-11-14 (content is never dropped; no content is only a name that selects a field, a namespace, an id that is rebuilt exactly). The decision is the author's.

| source path | count | declared reason | example value | reading |
|---|---:|---|---|---|
| `gspp.catalog.back-matter.resources[].rlinks[].hashes[].algorithm` | 1 | as decided for IFA on 2026-11-13: a back-matter resource that no link of a control names. A link that names a resource is written with the address the resource gives, and that address then has a destination | `MD5` | content: a reference of the catalogue to another document, with its title, address and digest. The root Set now carries the metadata link that names this resource by `#uuid`, and without the resource that link names nothing |
| `gspp.catalog.back-matter.resources[].rlinks[].hashes[].value` | 1 | as decided for IFA on 2026-11-13: a back-matter resource that no link of a control names. A link that names a resource is written with the address the resource gives, and that address then has a destination | `c91280d3504b9c81c5ceaf5bdaee5c7f` | content: a reference of the catalogue to another document, with its title, address and digest. The root Set now carries the metadata link that names this resource by `#uuid`, and without the resource that link names nothing |
| `gspp.catalog.back-matter.resources[].rlinks[].href` | 1 | as decided for IFA on 2026-11-13: a back-matter resource that no link of a control names. A link that names a resource is written with the address the resource gives, and that address then has a destination | `https://www.bsi.bund.de/DE/Themen/Unternehmen-und-Organisationen/Standards-und-Zertifizierung/IT-Grundschutz/it-grundschutz_node.html` | content: a reference of the catalogue to another document, with its title, address and digest. The root Set now carries the metadata link that names this resource by `#uuid`, and without the resource that link names nothing |
| `gspp.catalog.back-matter.resources[].title` | 1 | as decided for IFA on 2026-11-13: a back-matter resource that no link of a control names. A link that names a resource is written with the address the resource gives, and that address then has a destination | `BSI IT-Grundschutz Edition 2023` | content: a reference of the catalogue to another document, with its title, address and digest. The root Set now carries the metadata link that names this resource by `#uuid`, and without the resource that link names nothing |
| `gspp.catalog.back-matter.resources[].uuid` | 1 | as decided for IFA on 2026-11-13: a back-matter resource that no link of a control names. A link that names a resource is written with the address the resource gives, and that address then has a destination | `bf7510ca-fb0f-4182-af9f-b3c61db3187a` | content: a reference of the catalogue to another document, with its title, address and digest. The root Set now carries the metadata link that names this resource by `#uuid`, and without the resource that link names nothing |
| `gspp.catalog.uuid` | 1 | as decided for IFA on 2026-11-13: the uuid of a source element, here of the catalogue document itself: JASCON objects get URIs minted from ids and titles, the uuid is not carried | `73f2d8f6-5a98-4e81-b600-b709e372e9cf` | content: it identifies this document, and nothing in the bundle lets a reader rebuild it, so it is no id that is rebuilt exactly |

## Unaccounted source values (conversion ledger)

No destination, no rule by which the value is no content, and no declared reason. A run with one ends with a non-zero exit code. The first values of each path are in `bsi-conversion-ledger.json` (`unaccounted-paths`).

*(none)*
