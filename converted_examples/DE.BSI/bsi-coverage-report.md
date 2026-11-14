# BSI Grundschutz++ -> Semantic Core: Coverage Report (computed)

Source: **Anwenderkatalog Grundschutz++** v2026-07-16T05:11:52.605669+00:00 — single-catalog mode: **MS-TLS dropped by decision 2026-07-21** (its defects were reported to BSI; the twin-catalog finding — 11 shared ids, 10 silently diverged, census 2026-07-03 — stays on the record in census and handbook).

## Totals

- Source leaf values inventoried: **49,431**
- Mapped: **49,431** -> **UNMAPPED: 0** -> coverage **100.0 %**
- Emitted: **651 Requirements** carrying **999 statements** (all nested pseudo-controls flattened to clauses - nesting reaches depth 3), **162 Sets**, manifest with both digests, 6 pinned facet stubs.

## Conversion rules (declared, counted)

- **Modality** from `modal_verb` (code map incl. DARF NUR -> may-only): should x626, may x224, must x149; no unknown verbs.
- **Obligated party**: `https://ns.bsi.bund.de/gspp/party/institution` on every statement. This is the converter's default and not a value of the source; `--obligated-party URI` writes another. Why this default: the catalogue carries no party on a control; `Institution` is the word its prose uses for the organisation that applies it.
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

## Full path map
| path | count | level | destination |
|---|---:|---|---|
| `catalog.back-matter.resources[].rlinks[].hashes[].algorithm` | 1 | L1 | source-document reference (title/rlink) -> resolved into relations / dropped-declared |
| `catalog.back-matter.resources[].rlinks[].hashes[].value` | 1 | L1 | source-document reference (title/rlink) -> resolved into relations / dropped-declared |
| `catalog.back-matter.resources[].rlinks[].href` | 1 | L1 | source-document reference (title/rlink) -> resolved into relations / dropped-declared |
| `catalog.back-matter.resources[].title` | 1 | L1 | source-document reference (title/rlink) -> resolved into relations / dropped-declared |
| `catalog.back-matter.resources[].uuid` | 1 | L1 | resolution key for #uuid links -> external URL |
| `catalog.groups[].groups[].controls[].class` | 651 | L1 | gspp-taxonomy: class (by-statement) |
| `catalog.groups[].groups[].controls[].controls[].class` | 327 | L1 | gspp-taxonomy: class (by-statement) |
| `catalog.groups[].groups[].controls[].controls[].controls[].class` | 19 | L1 | gspp-taxonomy: class (by-statement) |
| `catalog.groups[].groups[].controls[].controls[].controls[].controls[].class` | 2 | L1 | gspp-taxonomy: class (by-statement) |
| `catalog.groups[].groups[].controls[].controls[].controls[].controls[].id` | 2 | L1 | Requirement id (top) / statement id (nested) |
| `catalog.groups[].groups[].controls[].controls[].controls[].controls[].parts[].id` | 4 | L1 | statement/guidance part identity -> statement id / narrative key |
| `catalog.groups[].groups[].controls[].controls[].controls[].controls[].parts[].name` | 4 | L1 | statement/guidance part identity -> statement id / narrative key |
| `catalog.groups[].groups[].controls[].controls[].controls[].controls[].parts[].props[].name` | 7 | L1 | dispatch by part-prop name (grammar/objectives/criteria; packed lists reported) |
| `catalog.groups[].groups[].controls[].controls[].controls[].controls[].parts[].props[].ns` | 7 | L1 | absorbed: CSV-link namespaces replaced by pinned facet schemas |
| `catalog.groups[].groups[].controls[].controls[].controls[].controls[].parts[].props[].value` | 7 | L1 | dispatch by part-prop name (grammar/objectives/criteria; packed lists reported) |
| `catalog.groups[].groups[].controls[].controls[].controls[].controls[].parts[].prose` | 4 | L1 | statements[].prose.de ({{insert}} -> {param:}) / gspp-narrative guidance |
| `catalog.groups[].groups[].controls[].controls[].controls[].controls[].props[].name` | 6 | L1 | dispatch by prop name (see per-prop table) |
| `catalog.groups[].groups[].controls[].controls[].controls[].controls[].props[].ns` | 4 | L1 | absorbed: CSV-link namespaces replaced by pinned facet schemas |
| `catalog.groups[].groups[].controls[].controls[].controls[].controls[].props[].value` | 6 | L1 | dispatch by prop name (see per-prop table) |
| `catalog.groups[].groups[].controls[].controls[].controls[].controls[].title` | 2 | L1 | Requirement title (top) / kept in taxonomy by-statement (nested) |
| `catalog.groups[].groups[].controls[].controls[].controls[].id` | 19 | L1 | Requirement id (top) / statement id (nested) |
| `catalog.groups[].groups[].controls[].controls[].controls[].links[].href` | 8 | L1 | relations[] {type=rel, ref} (#control -> req URI; #uuid -> back-matter URL) |
| `catalog.groups[].groups[].controls[].controls[].controls[].links[].rel` | 8 | L1 | relations[] {type=rel, ref} (#control -> req URI; #uuid -> back-matter URL) |
| `catalog.groups[].groups[].controls[].controls[].controls[].params[].id` | 4 | L1 | statement parameter name (type string) |
| `catalog.groups[].groups[].controls[].controls[].controls[].params[].label` | 4 | L1 | parameter label / default - first-class since the D9 rev (backlog #1); residue drained |
| `catalog.groups[].groups[].controls[].controls[].controls[].params[].props[].name` | 4 | L2 | compat oscal-1x: param-extras (param alt-identifier only) |
| `catalog.groups[].groups[].controls[].controls[].controls[].params[].props[].value` | 4 | L2 | compat oscal-1x: param-extras (param alt-identifier only) |
| `catalog.groups[].groups[].controls[].controls[].controls[].parts[].id` | 37 | L1 | statement/guidance part identity -> statement id / narrative key |
| `catalog.groups[].groups[].controls[].controls[].controls[].parts[].name` | 37 | L1 | statement/guidance part identity -> statement id / narrative key |
| `catalog.groups[].groups[].controls[].controls[].controls[].parts[].props[].name` | 95 | L1 | dispatch by part-prop name (grammar/objectives/criteria; packed lists reported) |
| `catalog.groups[].groups[].controls[].controls[].controls[].parts[].props[].ns` | 95 | L1 | absorbed: CSV-link namespaces replaced by pinned facet schemas |
| `catalog.groups[].groups[].controls[].controls[].controls[].parts[].props[].value` | 95 | L1 | dispatch by part-prop name (grammar/objectives/criteria; packed lists reported) |
| `catalog.groups[].groups[].controls[].controls[].controls[].parts[].prose` | 37 | L1 | statements[].prose.de ({{insert}} -> {param:}) / gspp-narrative guidance |
| `catalog.groups[].groups[].controls[].controls[].controls[].props[].name` | 131 | L1 | dispatch by prop name (see per-prop table) |
| `catalog.groups[].groups[].controls[].controls[].controls[].props[].ns` | 112 | L1 | absorbed: CSV-link namespaces replaced by pinned facet schemas |
| `catalog.groups[].groups[].controls[].controls[].controls[].props[].value` | 131 | L1 | dispatch by prop name (see per-prop table) |
| `catalog.groups[].groups[].controls[].controls[].controls[].title` | 19 | L1 | Requirement title (top) / kept in taxonomy by-statement (nested) |
| `catalog.groups[].groups[].controls[].controls[].id` | 327 | L1 | Requirement id (top) / statement id (nested) |
| `catalog.groups[].groups[].controls[].controls[].links[].href` | 67 | L1 | relations[] {type=rel, ref} (#control -> req URI; #uuid -> back-matter URL) |
| `catalog.groups[].groups[].controls[].controls[].links[].rel` | 67 | L1 | relations[] {type=rel, ref} (#control -> req URI; #uuid -> back-matter URL) |
| `catalog.groups[].groups[].controls[].controls[].params[].id` | 73 | L1 | statement parameter name (type string) |
| `catalog.groups[].groups[].controls[].controls[].params[].label` | 73 | L1 | parameter label / default - first-class since the D9 rev (backlog #1); residue drained |
| `catalog.groups[].groups[].controls[].controls[].params[].props[].name` | 73 | L2 | compat oscal-1x: param-extras (param alt-identifier only) |
| `catalog.groups[].groups[].controls[].controls[].params[].props[].value` | 73 | L2 | compat oscal-1x: param-extras (param alt-identifier only) |
| `catalog.groups[].groups[].controls[].controls[].params[].values[]` | 1 | L1 | parameter label / default - first-class since the D9 rev (backlog #1); residue drained |
| `catalog.groups[].groups[].controls[].controls[].parts[].id` | 653 | L1 | statement/guidance part identity -> statement id / narrative key |
| `catalog.groups[].groups[].controls[].controls[].parts[].name` | 653 | L1 | statement/guidance part identity -> statement id / narrative key |
| `catalog.groups[].groups[].controls[].controls[].parts[].props[].name` | 1,632 | L1 | dispatch by part-prop name (grammar/objectives/criteria; packed lists reported) |
| `catalog.groups[].groups[].controls[].controls[].parts[].props[].ns` | 1,632 | L1 | absorbed: CSV-link namespaces replaced by pinned facet schemas |
| `catalog.groups[].groups[].controls[].controls[].parts[].props[].value` | 1,632 | L1 | dispatch by part-prop name (grammar/objectives/criteria; packed lists reported) |
| `catalog.groups[].groups[].controls[].controls[].parts[].prose` | 653 | L1 | statements[].prose.de ({{insert}} -> {param:}) / gspp-narrative guidance |
| `catalog.groups[].groups[].controls[].controls[].props[].name` | 2,589 | L1 | dispatch by prop name (see per-prop table) |
| `catalog.groups[].groups[].controls[].controls[].props[].ns` | 2,262 | L1 | absorbed: CSV-link namespaces replaced by pinned facet schemas |
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
| `catalog.groups[].groups[].controls[].parts[].id` | 1,302 | L1 | statement/guidance part identity -> statement id / narrative key |
| `catalog.groups[].groups[].controls[].parts[].name` | 1,302 | L1 | statement/guidance part identity -> statement id / narrative key |
| `catalog.groups[].groups[].controls[].parts[].props[].name` | 3,308 | L1 | dispatch by part-prop name (grammar/objectives/criteria; packed lists reported) |
| `catalog.groups[].groups[].controls[].parts[].props[].ns` | 3,308 | L1 | absorbed: CSV-link namespaces replaced by pinned facet schemas |
| `catalog.groups[].groups[].controls[].parts[].props[].value` | 3,308 | L1 | dispatch by part-prop name (grammar/objectives/criteria; packed lists reported) |
| `catalog.groups[].groups[].controls[].parts[].prose` | 1,302 | L1 | statements[].prose.de ({{insert}} -> {param:}) / gspp-narrative guidance |
| `catalog.groups[].groups[].controls[].props[].name` | 5,240 | L1 | dispatch by prop name (see per-prop table) |
| `catalog.groups[].groups[].controls[].props[].ns` | 4,589 | L1 | absorbed: CSV-link namespaces replaced by pinned facet schemas |
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
| `catalog.metadata.last-modified` | 1 | L1 | bundle manifest / L0 provenance |
| `catalog.metadata.links[].href` | 1 | L1 | bundle manifest / L0 provenance |
| `catalog.metadata.links[].rel` | 1 | L1 | bundle manifest / L0 provenance |
| `catalog.metadata.links[].text` | 1 | L1 | bundle manifest / L0 provenance |
| `catalog.metadata.oscal-version` | 1 | L1 | bundle manifest / L0 provenance |
| `catalog.metadata.parties[].email-addresses[]` | 1 | L1 | bundle manifest / L0 provenance |
| `catalog.metadata.parties[].name` | 1 | L1 | bundle manifest / L0 provenance |
| `catalog.metadata.parties[].type` | 1 | L1 | bundle manifest / L0 provenance |
| `catalog.metadata.parties[].uuid` | 1 | L1 | bundle manifest / L0 provenance |
| `catalog.metadata.props[].name` | 3 | L1 | bundle manifest / L0 provenance |
| `catalog.metadata.props[].ns` | 1 | L1 | bundle manifest / L0 provenance |
| `catalog.metadata.props[].value` | 3 | L1 | bundle manifest / L0 provenance |
| `catalog.metadata.remarks` | 1 | L1 | bundle manifest / L0 provenance |
| `catalog.metadata.responsible-parties[].party-uuids[]` | 1 | L1 | bundle manifest / L0 provenance |
| `catalog.metadata.responsible-parties[].role-id` | 1 | L1 | bundle manifest / L0 provenance |
| `catalog.metadata.roles[].id` | 1 | L1 | bundle manifest / L0 provenance |
| `catalog.metadata.roles[].title` | 1 | L1 | bundle manifest / L0 provenance |
| `catalog.metadata.title` | 1 | L1 | bundle manifest / L0 provenance |
| `catalog.metadata.version` | 1 | L1 | bundle manifest / L0 provenance |
| `catalog.uuid` | 1 | L1 | bundle manifest / L0 provenance |

## Per-prop dispatch
| prop | level | destination |
|---|---|---|
| `alt-identifier` | L1 | Requirement.aliases (top) / taxonomy by-statement (nested) |
| `label` | L1 | Requirement.label (top) / taxonomy by-statement label (nested) |
| `sec_level` | L1 | top: baseline Set membership; nested: taxonomy by-statement |
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
