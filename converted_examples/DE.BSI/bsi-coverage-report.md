# BSI Grundschutz++ -> Semantic Core: Coverage Report (computed)

Source: **Anwenderkatalog Grundschutz++** v2026-07-16T05:11:52.605669+00:00 — single-catalog mode: **MS-TLS dropped by decision 2026-07-21** (its defects were reported to BSI; the twin-catalog finding — 11 shared ids, 10 silently diverged, census 2026-07-03 — stays on the record in census and handbook).

## Totals

- Source leaf values inventoried: **49,431**
- Mapped: **49,431** -> **UNMAPPED: 0** -> coverage **100.0 %**
- That is a count of source paths with a declared fate, not of values that arrived. Followed value by value (conversion ledger, below): **34,251** are in the bundle, **13,020** are dropped for a declared reason, **2,160** are unaccounted.
- Emitted: **651 Requirements** carrying **999 statements** (all nested pseudo-controls flattened to clauses - nesting reaches depth 3), **162 Sets**, manifest with both digests, 6 pinned facet stubs.

## Conversion rules (declared, counted)

- **Modality** from `modal_verb` (code map incl. DARF NUR -> may-only): should x626, may x224, must x149; no unknown verbs.
- **Obligated party**: `https://ns.bsi.bund.de/gspp/party/institution` on every statement. This is the converter's default and not a value of the source; `--obligated-party URI` writes another. Why this default: the catalogue carries no party on a control; `Institution` is the word its prose uses for the organisation that applies it. The subject a statement names before its modal verb is the practice that organisation runs, not a party (decided by the author on 2026-11-14).
- **Nested controls -> statements** of the parent; statement id = child control id (stable, citable); child-level props keyed `by-statement` in the facets.
- **{{ insert: param, x }}** in prose -> `{param:x}` tokens; params typed `string` with **first-class `label` + `default`** (D9 rev, backlog #1) - x221 parameters, the param-extras residue drains to alt-identifier uuids only. Params never referenced by a `{param:}` token in their statement's prose: x0 (counted - source QA signal); multi-value params x0 (first value becomes default, all values kept in source).
- **Payload free text language-tagged** per corpus language (`{de: ...}` on statement prose, guidance, Set descriptions) - this corpus was born tagged; harmonization rule (backlog #12) verified, not applied.
- **Grammar** (action_word/result/result_specification/target_object_categories) -> `statement-grammar@1` by-statement; **documentation** -> `assessment-criteria@1` required-documentation; **C/I/A/Auth + threats** -> `security-objectives@1` (threat codes minted from 'G 0.x'); **sec_level/effort/tags/class/practice** -> `gspp-taxonomy@1`; **guidance parts** -> `gspp-narrative@1`.
- **Baselines** from top-control `sec_level`: gspp:erhöht (134), gspp:normal-SdT (517). Child-level sec_level stays informational by-statement (clause-level baselining = Tailoring concern, not Set membership).
- **alt-identifier** -> aliases (scheme bsi-uuid) on Requirements; child alt-ids by-statement. CSV-link namespaces absorbed: pinned schemas replace them.

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

- **Totals**: the path map says where each source path is meant to go. The ledger follows each of the 49,431 source leaf values into the written bundle and reads every claim back from the 820 files of the bundle. **22,879 copied** (the value stands, with its type, at the destination named), **11,372 transformed** (a named rule made the destination from it; the rule was applied to the source again and compared), **13,020 intentionally dropped** (a declared reason), **2,160 unaccounted** (no destination and no declared reason). Checks that failed: 0. A value is traced by what the converter did with it; an equal value elsewhere in the bundle does not count. The record is `bsi-conversion-ledger.json`: one row per source path and outcome, with the number of values, the first of them, and where they went or why they were dropped. A destination keyed by the id of a nested control or of a parameter reads `{statement}` or `{param}` there.
- **Names and values**: 14,544 of the 34,251 values in the bundle are names. The name of a prop, or of the guidance part, holds no content of its own: it selects the field its value is written to. 6,793 stand in the bundle as the key of that field, unchanged, and nowhere as a value (counted as copied); 7,751 are mapped to a field of another name or to the alias scheme (counted as transformed). The other 19,707 are ids, texts and codes.
- **Declared drops: 13,020, of two kinds.** A drop is declared only where the path map of this converter already said that the path is not carried, or where the value is of a class the author decided for the IFA corpus on 2026-11-13. It applies only to a value that reached no destination.
    - (a) the path map already said so: **12,009**
        - x12,009: the path map of this converter says so (absorbed): the namespace of a prop is the address of the CSV list its value is taken from; the pinned facet schema stands in its place, the address is not carried
    - (b) a class decided for IFA on 2026-11-13: **1,011**
        - x6: as decided for IFA on 2026-11-13: the source's directory of parties and roles: a party is a landmark URI and there is no party object (register, backlog #16)
        - x5: as decided for IFA on 2026-11-13: a back-matter resource that no link of a control names. A link that names a resource is written with the address the resource gives, and that address then has a destination
        - x999: as decided for IFA on 2026-11-13: a type tag of a structural element: the part named `statement` is an entry of `statements[]`, and the bundle says by its shape what kind of thing it is
        - x1: as decided for IFA on 2026-11-13: the uuid of a source element, here of the catalogue document itself: JASCON objects get URIs minted from ids and titles, the uuid is not carried
- **Rules: 17 named, 16 applied to this catalogue.** Behind each, the number of source values it was applied to; a value can pass through more than one. Where a rule leaves a value as it is, the value counts as copied: a prose without a parameter token, a list prop with one term, a prop whose field has the prop's own name.
    - x651: requirement URI from the control id
    - x651: file path of a Requirement from the control id
    - x191: requirement URI from a link to a control (#id)
    - x0: a link that names a back-matter resource (#uuid): the address the resource gives
    - x159: taxonomy Set URI from the group id
    - x159: file path of a taxonomy Set from the group id
    - x651: baseline Set URI from the sec_level of a top-level control
    - x651: baseline Set title from the sec_level of a top-level control
    - x651: file path of a baseline Set from the sec_level of a top-level control
    - x999: a sec_level value as an entry of the enum of observed values in the pinned taxonomy schema
    - x208: statement prose with every {{ insert: param, x }} rewritten to {param:x}
    - x999: modality code from the modal verb (MODAL)
    - x165: one term of a list packed into one string (split on commas, trimmed)
    - x900: threat URI from one term of the threats list (split on commas, trimmed, spaces to hyphens)
    - x999: effort level as an integer
    - x6,941: field name from the prop name (FIELD)
    - x810: alias scheme from the prop name (ALIAS_SCHEME)
- **Lost: the links of nested controls, 75 links on 60 controls (150 source values).** The converter reads the links of a top-level control and not those of a control nested in it; the path map said `relations[]` for a control at any depth. First: `gspp#/catalog/groups/1/groups/1/controls/0/controls/3/controls/0/links/0/href` - `STM.2.1.4.1` related `#STM.2.1.4`. Not repaired here: carrying them changes the bundle.
- **A link to a nested control names no object: 34 of the 191 `relations[]` written.** A link to a control is written as the URI of a Requirement. A nested control is a statement of the Requirement of its top-level control, so `.../req/` with its id is the id of no object of the bundle. First: `GC.7.2` required `#GC.7.1.2`. The ledger checks that the rule was applied, not that the URI resolves. Not repaired here: it changes the bundle.
- **Path map corrected: 4 sentences claimed a destination at which the ledger found no value, for 3,171 values in all.**
    - `catalog.uuid, catalog.metadata.*` said "bundle manifest / L0 provenance"; found: only title, version and oscal-version reach the manifest. Not in the bundle: x21.
    - `catalog.back-matter.*` said "resolution key for #uuid links -> external URL; resolved into relations / dropped-declared"; found: a resource that no link of a control names is not resolved, and nothing of it is carried. Not in the bundle: x5.
    - `links[] of a nested control` said "relations[] {type=rel, ref}"; found: only the links of a top-level control are read; those of a nested control are lost. Not in the bundle: x150.
    - `parts[].id, parts[].name` said "statement/guidance part identity -> statement id / narrative key"; found: the id of a part is written nowhere; of the names, `guidance` becomes a key and `statement` does not. Not in the bundle: x2,995.
- **The path map held against the ledger: 0 values disagree.** Every row of the path map names what may become of the values of its paths: carried, dropped for a declared reason, or open (not carried and not decided). Each run compares that with the outcome the ledger found for every value, so a sentence of the map cannot claim again what the ledger does not find. A value dropped on a path the map does not give up ends the run with an error. No value has an outcome its row does not allow.
- **What the ledger cannot see**: it follows source values into the bundle, not the other way round. 4,146 of the 28,845 leaf values of the 813 objects have no source value behind them. The converter writes them on its own and none has a row in the ledger: `/id` x1 (the id of the root Set, and of a Set whose group has no id); `/lifecycle` x813 (`active`); `/members/[]/sequence` x1,461 (the order of the members of a Set); `/statements/[]/id` x651 (the statement id `smt` of a top-level control); `/statements/[]/obligated-parties/[]` x999 (the obligated party `https://ns.bsi.bund.de/gspp/party/institution`, the converter's default); `/statements/[]/parameters/[]/type` x221 (`string`, the type of every parameter). The manifest adds 1,655 values of its own (digests, the paths and versions of the pinned schemas, the converter line), the pinned schemas 84. Two more limits. The ledger checks the URI of a baseline Set against the sec_level of every control that names it; that the Requirement of that control is listed in that Set it does not check. And it checks that a rule gives what the file holds, not that the rule is the right one: a rule whose function is changed changes the bundle and no figure of the ledger. That the bundle is byte for byte the committed one is held apart from it, by the Validators workflow, which converts the pinned source again and compares.
- **Unaccounted: 2,160.** Listed by path at the end of this report. Each is either carried, which changes the bundle, or dropped for a reason. Both are decisions of the author (backlog #41), and neither is taken here.

## Full path map
| path | count | level | destination |
|---|---:|---|---|
| `catalog.back-matter.resources[].rlinks[].hashes[].algorithm` | 1 | - | a resource that a link of a control names by #uuid gives that link its address (relations[].ref); a resource no link of a control names is not carried (declared drop in the ledger) |
| `catalog.back-matter.resources[].rlinks[].hashes[].value` | 1 | - | a resource that a link of a control names by #uuid gives that link its address (relations[].ref); a resource no link of a control names is not carried (declared drop in the ledger) |
| `catalog.back-matter.resources[].rlinks[].href` | 1 | - | a resource that a link of a control names by #uuid gives that link its address (relations[].ref); a resource no link of a control names is not carried (declared drop in the ledger) |
| `catalog.back-matter.resources[].title` | 1 | - | a resource that a link of a control names by #uuid gives that link its address (relations[].ref); a resource no link of a control names is not carried (declared drop in the ledger) |
| `catalog.back-matter.resources[].uuid` | 1 | - | a resource that a link of a control names by #uuid gives that link its address (relations[].ref); a resource no link of a control names is not carried (declared drop in the ledger) |
| `catalog.groups[].groups[].controls[].class` | 651 | L1 | gspp-taxonomy: class (by-statement) |
| `catalog.groups[].groups[].controls[].controls[].class` | 327 | L1 | gspp-taxonomy: class (by-statement) |
| `catalog.groups[].groups[].controls[].controls[].controls[].class` | 19 | L1 | gspp-taxonomy: class (by-statement) |
| `catalog.groups[].groups[].controls[].controls[].controls[].controls[].class` | 2 | L1 | gspp-taxonomy: class (by-statement) |
| `catalog.groups[].groups[].controls[].controls[].controls[].controls[].id` | 2 | L1 | Requirement id (top) / statement id (nested) |
| `catalog.groups[].groups[].controls[].controls[].controls[].controls[].parts[].id` | 4 | - | not carried and not decided: the id of a part (the control id with `_stm` or `_gdn`) is written nowhere; the statement id is `smt` or the id of the nested control (unaccounted in the ledger) |
| `catalog.groups[].groups[].controls[].controls[].controls[].controls[].parts[].name` | 4 | L1 | `guidance` -> the key of the gspp-narrative payload; `statement` -> not carried, the part is an entry of statements[] (declared drop in the ledger) |
| `catalog.groups[].groups[].controls[].controls[].controls[].controls[].parts[].props[].name` | 7 | L1 | dispatch by part-prop name (grammar/objectives/criteria; packed lists reported) |
| `catalog.groups[].groups[].controls[].controls[].controls[].controls[].parts[].props[].ns` | 7 | - | not carried (absorbed): CSV-link namespaces replaced by pinned facet schemas (declared drop in the ledger) |
| `catalog.groups[].groups[].controls[].controls[].controls[].controls[].parts[].props[].value` | 7 | L1 | dispatch by part-prop name (grammar/objectives/criteria; packed lists reported) |
| `catalog.groups[].groups[].controls[].controls[].controls[].controls[].parts[].prose` | 4 | L1 | statements[].prose.de ({{insert}} -> {param:}) / gspp-narrative guidance |
| `catalog.groups[].groups[].controls[].controls[].controls[].controls[].props[].name` | 6 | L1 | dispatch by prop name (see per-prop table) |
| `catalog.groups[].groups[].controls[].controls[].controls[].controls[].props[].ns` | 4 | - | not carried (absorbed): CSV-link namespaces replaced by pinned facet schemas (declared drop in the ledger) |
| `catalog.groups[].groups[].controls[].controls[].controls[].controls[].props[].value` | 6 | L1 | dispatch by prop name (see per-prop table) |
| `catalog.groups[].groups[].controls[].controls[].controls[].controls[].title` | 2 | L1 | Requirement title (top) / kept in taxonomy by-statement (nested) |
| `catalog.groups[].groups[].controls[].controls[].controls[].id` | 19 | L1 | Requirement id (top) / statement id (nested) |
| `catalog.groups[].groups[].controls[].controls[].controls[].links[].href` | 8 | - | NOT CARRIED: the links of a nested control are not read (found by the ledger; unaccounted) |
| `catalog.groups[].groups[].controls[].controls[].controls[].links[].rel` | 8 | - | NOT CARRIED: the links of a nested control are not read (found by the ledger; unaccounted) |
| `catalog.groups[].groups[].controls[].controls[].controls[].params[].id` | 4 | L1 | statement parameter name (type string) |
| `catalog.groups[].groups[].controls[].controls[].controls[].params[].label` | 4 | L1 | parameter label / default - first-class since the D9 rev (backlog #1); residue drained |
| `catalog.groups[].groups[].controls[].controls[].controls[].params[].props[].name` | 4 | L2 | compat oscal-1x: param-extras (param alt-identifier only) |
| `catalog.groups[].groups[].controls[].controls[].controls[].params[].props[].value` | 4 | L2 | compat oscal-1x: param-extras (param alt-identifier only) |
| `catalog.groups[].groups[].controls[].controls[].controls[].parts[].id` | 37 | - | not carried and not decided: the id of a part (the control id with `_stm` or `_gdn`) is written nowhere; the statement id is `smt` or the id of the nested control (unaccounted in the ledger) |
| `catalog.groups[].groups[].controls[].controls[].controls[].parts[].name` | 37 | L1 | `guidance` -> the key of the gspp-narrative payload; `statement` -> not carried, the part is an entry of statements[] (declared drop in the ledger) |
| `catalog.groups[].groups[].controls[].controls[].controls[].parts[].props[].name` | 95 | L1 | dispatch by part-prop name (grammar/objectives/criteria; packed lists reported) |
| `catalog.groups[].groups[].controls[].controls[].controls[].parts[].props[].ns` | 95 | - | not carried (absorbed): CSV-link namespaces replaced by pinned facet schemas (declared drop in the ledger) |
| `catalog.groups[].groups[].controls[].controls[].controls[].parts[].props[].value` | 95 | L1 | dispatch by part-prop name (grammar/objectives/criteria; packed lists reported) |
| `catalog.groups[].groups[].controls[].controls[].controls[].parts[].prose` | 37 | L1 | statements[].prose.de ({{insert}} -> {param:}) / gspp-narrative guidance |
| `catalog.groups[].groups[].controls[].controls[].controls[].props[].name` | 131 | L1 | dispatch by prop name (see per-prop table) |
| `catalog.groups[].groups[].controls[].controls[].controls[].props[].ns` | 112 | - | not carried (absorbed): CSV-link namespaces replaced by pinned facet schemas (declared drop in the ledger) |
| `catalog.groups[].groups[].controls[].controls[].controls[].props[].value` | 131 | L1 | dispatch by prop name (see per-prop table) |
| `catalog.groups[].groups[].controls[].controls[].controls[].title` | 19 | L1 | Requirement title (top) / kept in taxonomy by-statement (nested) |
| `catalog.groups[].groups[].controls[].controls[].id` | 327 | L1 | Requirement id (top) / statement id (nested) |
| `catalog.groups[].groups[].controls[].controls[].links[].href` | 67 | - | NOT CARRIED: the links of a nested control are not read (found by the ledger; unaccounted) |
| `catalog.groups[].groups[].controls[].controls[].links[].rel` | 67 | - | NOT CARRIED: the links of a nested control are not read (found by the ledger; unaccounted) |
| `catalog.groups[].groups[].controls[].controls[].params[].id` | 73 | L1 | statement parameter name (type string) |
| `catalog.groups[].groups[].controls[].controls[].params[].label` | 73 | L1 | parameter label / default - first-class since the D9 rev (backlog #1); residue drained |
| `catalog.groups[].groups[].controls[].controls[].params[].props[].name` | 73 | L2 | compat oscal-1x: param-extras (param alt-identifier only) |
| `catalog.groups[].groups[].controls[].controls[].params[].props[].value` | 73 | L2 | compat oscal-1x: param-extras (param alt-identifier only) |
| `catalog.groups[].groups[].controls[].controls[].params[].values[]` | 1 | L1 | parameter label / default - first-class since the D9 rev (backlog #1); residue drained |
| `catalog.groups[].groups[].controls[].controls[].parts[].id` | 653 | - | not carried and not decided: the id of a part (the control id with `_stm` or `_gdn`) is written nowhere; the statement id is `smt` or the id of the nested control (unaccounted in the ledger) |
| `catalog.groups[].groups[].controls[].controls[].parts[].name` | 653 | L1 | `guidance` -> the key of the gspp-narrative payload; `statement` -> not carried, the part is an entry of statements[] (declared drop in the ledger) |
| `catalog.groups[].groups[].controls[].controls[].parts[].props[].name` | 1,632 | L1 | dispatch by part-prop name (grammar/objectives/criteria; packed lists reported) |
| `catalog.groups[].groups[].controls[].controls[].parts[].props[].ns` | 1,632 | - | not carried (absorbed): CSV-link namespaces replaced by pinned facet schemas (declared drop in the ledger) |
| `catalog.groups[].groups[].controls[].controls[].parts[].props[].value` | 1,632 | L1 | dispatch by part-prop name (grammar/objectives/criteria; packed lists reported) |
| `catalog.groups[].groups[].controls[].controls[].parts[].prose` | 653 | L1 | statements[].prose.de ({{insert}} -> {param:}) / gspp-narrative guidance |
| `catalog.groups[].groups[].controls[].controls[].props[].name` | 2,589 | L1 | dispatch by prop name (see per-prop table) |
| `catalog.groups[].groups[].controls[].controls[].props[].ns` | 2,262 | - | not carried (absorbed): CSV-link namespaces replaced by pinned facet schemas (declared drop in the ledger) |
| `catalog.groups[].groups[].controls[].controls[].props[].value` | 2,589 | L1 | dispatch by prop name (see per-prop table) |
| `catalog.groups[].groups[].controls[].controls[].title` | 327 | L1 | Requirement title (top) / kept in taxonomy by-statement (nested) |
| `catalog.groups[].groups[].controls[].id` | 651 | L1 | Requirement id (top) / statement id (nested) |
| `catalog.groups[].groups[].controls[].links[].href` | 191 | L1 | relations[] {type=rel, ref} (#control -> req URI; #uuid -> back-matter URL) |
| `catalog.groups[].groups[].controls[].links[].rel` | 191 | L1 | relations[] {type=rel, ref} (#control -> req URI; #uuid -> back-matter URL) |
| `catalog.groups[].groups[].controls[].params[].id` | 144 | L1 | statement parameter name (type string) |
| `catalog.groups[].groups[].controls[].params[].label` | 144 | L1 | parameter label / default - first-class since the D9 rev (backlog #1); residue drained |
| `catalog.groups[].groups[].controls[].params[].props[].name` | 144 | L2 | compat oscal-1x: param-extras (param alt-identifier only) |
| `catalog.groups[].groups[].controls[].params[].props[].value` | 144 | L2 | compat oscal-1x: param-extras (param alt-identifier only) |
| `catalog.groups[].groups[].controls[].params[].values[]` | 1 | L1 | parameter label / default - first-class since the D9 rev (backlog #1); residue drained |
| `catalog.groups[].groups[].controls[].parts[].id` | 1,302 | - | not carried and not decided: the id of a part (the control id with `_stm` or `_gdn`) is written nowhere; the statement id is `smt` or the id of the nested control (unaccounted in the ledger) |
| `catalog.groups[].groups[].controls[].parts[].name` | 1,302 | L1 | `guidance` -> the key of the gspp-narrative payload; `statement` -> not carried, the part is an entry of statements[] (declared drop in the ledger) |
| `catalog.groups[].groups[].controls[].parts[].props[].name` | 3,308 | L1 | dispatch by part-prop name (grammar/objectives/criteria; packed lists reported) |
| `catalog.groups[].groups[].controls[].parts[].props[].ns` | 3,308 | - | not carried (absorbed): CSV-link namespaces replaced by pinned facet schemas (declared drop in the ledger) |
| `catalog.groups[].groups[].controls[].parts[].props[].value` | 3,308 | L1 | dispatch by part-prop name (grammar/objectives/criteria; packed lists reported) |
| `catalog.groups[].groups[].controls[].parts[].prose` | 1,302 | L1 | statements[].prose.de ({{insert}} -> {param:}) / gspp-narrative guidance |
| `catalog.groups[].groups[].controls[].props[].name` | 5,240 | L1 | dispatch by prop name (see per-prop table) |
| `catalog.groups[].groups[].controls[].props[].ns` | 4,589 | - | not carried (absorbed): CSV-link namespaces replaced by pinned facet schemas (declared drop in the ledger) |
| `catalog.groups[].groups[].controls[].props[].value` | 5,240 | L1 | dispatch by prop name (see per-prop table) |
| `catalog.groups[].groups[].controls[].title` | 651 | L1 | Requirement title (top) / kept in taxonomy by-statement (nested) |
| `catalog.groups[].groups[].id` | 139 | L1 | taxonomy Set id/title (per-catalog subtree) |
| `catalog.groups[].groups[].props[].name` | 278 | L1 | Set.label / Set.aliases (bsi-uuid) |
| `catalog.groups[].groups[].props[].value` | 278 | L1 | Set.label / Set.aliases (bsi-uuid) |
| `catalog.groups[].groups[].title` | 139 | L1 | taxonomy Set id/title (per-catalog subtree) |
| `catalog.groups[].id` | 20 | L1 | taxonomy Set id/title (per-catalog subtree) |
| `catalog.groups[].props[].name` | 40 | L1 | Set.label / Set.aliases (bsi-uuid) |
| `catalog.groups[].props[].remarks` | 20 | L1 | gspp-narrative on the Set: layer/Praktik description |
| `catalog.groups[].props[].value` | 40 | L1 | Set.label / Set.aliases (bsi-uuid) |
| `catalog.groups[].title` | 20 | L1 | taxonomy Set id/title (per-catalog subtree) |
| `catalog.metadata.last-modified` | 1 | - | not carried and not decided: last-modified, props, links, remarks, responsible-parties (unaccounted in the ledger) |
| `catalog.metadata.links[].href` | 1 | - | not carried and not decided: last-modified, props, links, remarks, responsible-parties (unaccounted in the ledger) |
| `catalog.metadata.links[].rel` | 1 | - | not carried and not decided: last-modified, props, links, remarks, responsible-parties (unaccounted in the ledger) |
| `catalog.metadata.links[].text` | 1 | - | not carried and not decided: last-modified, props, links, remarks, responsible-parties (unaccounted in the ledger) |
| `catalog.metadata.oscal-version` | 1 | L1 | manifest provenance.sources[] (title, version, oscal-version); version -> `version` of every object; title -> title of the root Set |
| `catalog.metadata.parties[].email-addresses[]` | 1 | - | not carried: the source's directory of parties and roles (declared drop in the ledger) |
| `catalog.metadata.parties[].name` | 1 | - | not carried: the source's directory of parties and roles (declared drop in the ledger) |
| `catalog.metadata.parties[].type` | 1 | - | not carried: the source's directory of parties and roles (declared drop in the ledger) |
| `catalog.metadata.parties[].uuid` | 1 | - | not carried: the source's directory of parties and roles (declared drop in the ledger) |
| `catalog.metadata.props[].name` | 3 | - | not carried and not decided: last-modified, props, links, remarks, responsible-parties (unaccounted in the ledger) |
| `catalog.metadata.props[].ns` | 1 | - | not carried and not decided: last-modified, props, links, remarks, responsible-parties (unaccounted in the ledger) |
| `catalog.metadata.props[].value` | 3 | - | not carried and not decided: last-modified, props, links, remarks, responsible-parties (unaccounted in the ledger) |
| `catalog.metadata.remarks` | 1 | - | not carried and not decided: last-modified, props, links, remarks, responsible-parties (unaccounted in the ledger) |
| `catalog.metadata.responsible-parties[].party-uuids[]` | 1 | - | not carried and not decided: last-modified, props, links, remarks, responsible-parties (unaccounted in the ledger) |
| `catalog.metadata.responsible-parties[].role-id` | 1 | - | not carried and not decided: last-modified, props, links, remarks, responsible-parties (unaccounted in the ledger) |
| `catalog.metadata.roles[].id` | 1 | - | not carried: the source's directory of parties and roles (declared drop in the ledger) |
| `catalog.metadata.roles[].title` | 1 | - | not carried: the source's directory of parties and roles (declared drop in the ledger) |
| `catalog.metadata.title` | 1 | L1 | manifest provenance.sources[] (title, version, oscal-version); version -> `version` of every object; title -> title of the root Set |
| `catalog.metadata.version` | 1 | L1 | manifest provenance.sources[] (title, version, oscal-version); version -> `version` of every object; title -> title of the root Set |
| `catalog.uuid` | 1 | - | not carried: the uuid of the source document (declared drop in the ledger) |

## Per-prop dispatch
| prop | level | destination |
|---|---|---|
| `alt-identifier` | L1 | Requirement.aliases (top) / taxonomy by-statement (nested) |
| `label` | L1 | Requirement.label (top) / taxonomy by-statement label (nested) |
| `sec_level` | L1 | gspp-taxonomy: sec-level (by-statement, at every depth); top: also the baseline Set the Requirement is listed in |
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
| `practice` | L1 | gspp-taxonomy: practice (by-statement) |

## UNMAPPED (gate target: zero)

*(none)*

## Unaccounted source values (conversion ledger)

No destination and no declared reason. The first values of each path are in `bsi-conversion-ledger.json` (`unaccounted-paths`).

| path | count | first value |
|---|---:|---|
| `gspp.catalog.groups[].groups[].controls[].controls[].controls[].controls[].parts[].id` | 4 | `gspp#/catalog/groups/0/groups/8/controls/0/controls/0/controls/0/controls/0/parts/0/id` |
| `gspp.catalog.groups[].groups[].controls[].controls[].controls[].links[].href` | 8 | `gspp#/catalog/groups/1/groups/1/controls/0/controls/3/controls/0/links/0/href` |
| `gspp.catalog.groups[].groups[].controls[].controls[].controls[].links[].rel` | 8 | `gspp#/catalog/groups/1/groups/1/controls/0/controls/3/controls/0/links/0/rel` |
| `gspp.catalog.groups[].groups[].controls[].controls[].controls[].parts[].id` | 37 | `gspp#/catalog/groups/0/groups/8/controls/0/controls/0/controls/0/parts/0/id` |
| `gspp.catalog.groups[].groups[].controls[].controls[].links[].href` | 67 | `gspp#/catalog/groups/0/groups/4/controls/0/controls/3/links/0/href` |
| `gspp.catalog.groups[].groups[].controls[].controls[].links[].rel` | 67 | `gspp#/catalog/groups/0/groups/4/controls/0/controls/3/links/0/rel` |
| `gspp.catalog.groups[].groups[].controls[].controls[].parts[].id` | 653 | `gspp#/catalog/groups/0/groups/2/controls/0/controls/0/parts/0/id` |
| `gspp.catalog.groups[].groups[].controls[].parts[].id` | 1,302 | `gspp#/catalog/groups/0/groups/0/controls/0/parts/0/id` |
| `gspp.catalog.metadata.last-modified` | 1 | `gspp#/catalog/metadata/last-modified` |
| `gspp.catalog.metadata.links[].href` | 1 | `gspp#/catalog/metadata/links/0/href` |
| `gspp.catalog.metadata.links[].rel` | 1 | `gspp#/catalog/metadata/links/0/rel` |
| `gspp.catalog.metadata.links[].text` | 1 | `gspp#/catalog/metadata/links/0/text` |
| `gspp.catalog.metadata.props[].name` | 3 | `gspp#/catalog/metadata/props/0/name` |
| `gspp.catalog.metadata.props[].ns` | 1 | `gspp#/catalog/metadata/props/1/ns` |
| `gspp.catalog.metadata.props[].value` | 3 | `gspp#/catalog/metadata/props/0/value` |
| `gspp.catalog.metadata.remarks` | 1 | `gspp#/catalog/metadata/remarks` |
| `gspp.catalog.metadata.responsible-parties[].party-uuids[]` | 1 | `gspp#/catalog/metadata/responsible-parties/0/party-uuids/0` |
| `gspp.catalog.metadata.responsible-parties[].role-id` | 1 | `gspp#/catalog/metadata/responsible-parties/0/role-id` |
