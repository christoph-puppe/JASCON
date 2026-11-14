# ISM -> Semantic Core: Coverage Report (computed)

Source: ACSC ISM OSCAL catalog v2026.06.18 (oscal-version 1.1.2) - 1,150 controls, 570 groups.

## Totals

- Source leaf values inventoried: **36,161**
- Mapped (declared destination): **36,161**
- **UNMAPPED: 0**  ->  coverage **100.0 %**

- Objects emitted: **1,150 Requirements**, **581 Sets**, manifest with both digests per object.

- **Conversion ledger (measured per source value; the figures above are a DECLARATION)**: the path map says for every source path where its values are meant to go. The ledger follows each of the 36,161 source leaf values through the converter into the written files. **11,401 copied** (the value stands, with its type, at the destination named, read back from the written file), **14,564 transformed** (a named rule made the destination from it; the rule was applied to the source again and compared), **10,196 no content** (a name that only selects a field, a namespace, an id that is rebuilt exactly - each by a rule the ledger checked), **0 dropped for a reason declared earlier** (listed below for the author to decide), **0 unaccounted**. Claims that do not hold: 0. An equal value elsewhere in the bundle does not count: a value is traced by what the converter did with it. A run with an unaccounted value or a claim that does not hold ends with 1. `ism-conversion-ledger.json` is the record, one row per source path and outcome (58 rows; the entry of each single value is made and checked in the run and not written).

## Conversion rules (declared, counted)

- **Modality word-rule** over statement prose (first match of must not > should not > must > should > may, else unspecified): unspecified x1149, may x1.
- **Obligated party**: `https://ns.cyber.gov.au/ism/party/organisation` on every statement. This is the converter's default and not a value of the source; `--obligated-party URI` writes another. Why this default: ISM binds the organisation implicitly; no per-control party data in source.
- **Lifecycle**: `active` on 1,731 object(s) is the converter's default and not a value of the source: the kernel requires a lifecycle on every object, and a published catalogue is taken to be in force. The source states no status on any object.
- **Labels**: 49 from `label` props; 1101 derived from control id (`ism-1234` -> `ISM-1234`).
- **Groups -> Sets**: every group is a Set, in its place in the hierarchy (570 groups). Its members are the Sets of its groups and the Requirements of its controls. 16 groups hold neither and are Sets with no member: 16 with an overview part, 0 a heading only.
- **sequence**: document order (steps of 10). The source's `sort-id` (1,720 on controls and groups) is no content: a sort-id is its parent's sort-id, the kind of the element and its position among its siblings, written with as many digits as their number has. The ledger checked that for every value. Read back from the written files, a reader rebuilds 1,720 of 1,720.
- **class** -> category Sets: ISM-control (1101), ISM-principle (49).
- **applicability** -> baseline Sets: NC (1024), OS (1035), P (1035), S (1099), TS (1108); **essential-eight** -> ML1 (46), ML2 (87), ML3 (123).
- **Props the kernel has no member for** (`revision` x1,101, `updated` x1,101): carried as the source writes them (name, namespace, value) in the compat facet oscal-1x@1 of their object, under `props`. A control's own revision number is not the `version` of its Requirement: that is the catalogue's, on every object.
- **Guideline narrative** (`overview` parts on groups, x539): **Level 2** compat facet oscal-1x@1 on the Set of the group - the declared waiting room with a clock (handbook 14.6).
- **Document metadata**: title and version are the root Set's; the rest of `metadata` (32 values) stands in the compat facet oscal-1x@1 of the root Set under `metadata`, in the source's own shape. Manifest provenance: author-ref `https://ns.cyber.gov.au/ism/party/australian-cyber-security-centre`, date `2026-06-18`.
- **Back-matter**: 246 resources in the references facet of the root Set, each with its uuid. Read back from the written files: 481 links `(#uuid)` stand in 76 texts of 76 objects; 481 of them name a resource the bundle holds (241 of its 246 resources).
- **Payload free text language-tagged** per corpus language (`{en: ...}` on compat `group-parts[].prose`); statement prose was already tagged. Harmonized 2026-07-21 (backlog #12).

### Corpus finding (new vs. census)

ISM statement prose is **declarative present tense** ('The board ... defines', 'Passphrases are ...'): modal verbs are structurally absent, not merely unencoded. The census note 'style-guide prose' was too generous. Consequence: `unspecified` is the *honest* modality for this corpus, and binding force is carried by baseline membership (the applicability Sets) - exactly the legitimate Core-tier pattern for narrative frameworks. The single lexical hit is counted above.

## Per-prop destinations

The last column is measured: what the ledger found for the leaves of these props (name, value and, where the prop has one, namespace).

| source prop | count | level | destination | ledger |
|---|---:|---|---|---|
| `props[].name = sort-id` | 1720 | not-content | no content: the parent's sort-id and the position among the siblings give it exactly; the bundle keeps both as the hierarchy of the Sets and members[].sequence | 3,440 not content |
| `props[].name = label` | 49 | name not-content, value L1 | Requirement.label; the name selects that member | 49 copied, 49 not content |
| `props[].name = applicability` | 5301 | L1 by rule | membership -> set/baseline/class-<marker>; the name gives the kind `class` | 10,602 transformed, 5,301 not content |
| `props[].name = essential-eight-applicability` | 256 | L1 by rule | membership -> set/baseline/e8-<level>; the name gives the kind `e8` | 512 transformed, 256 not content |
| `props[].name = revision` | 1101 | L2 | compat facet oscal-1x@1 on the object: props[], as the source writes the prop (the kernel has no member for it) | 3,303 copied |
| `props[].name = updated` | 1101 | L2 | compat facet oscal-1x@1 on the object: props[], as the source writes the prop (the kernel has no member for it) | 3,303 copied |

## Full path map (every source path, its count, its destination)

Levels: L1 - written as it is in a kernel field; L2 - written as it is in a facet; L1 by rule - a kernel field is made from it by a named rule; not-content - no content, by a rule the ledger checks; declared-drop - not carried, for a reason declared before 2026-11-14; dispatch - a prop, see its own row above. The last column is measured: the outcomes the ledger found for the values of the path.

| path | count | level | destination | ledger |
|---|---:|---|---|---|
| `catalog.back-matter.resources[].props[].name` | 2 | L2 | references facet on the root Set: resources[], in the source's own shape, with the uuid that a `(#uuid)` link in a text names | 2 copied |
| `catalog.back-matter.resources[].props[].value` | 2 | L2 | references facet on the root Set: resources[], in the source's own shape, with the uuid that a `(#uuid)` link in a text names | 2 copied |
| `catalog.back-matter.resources[].rlinks[].href` | 254 | L2 | references facet on the root Set: resources[], in the source's own shape, with the uuid that a `(#uuid)` link in a text names | 254 copied |
| `catalog.back-matter.resources[].rlinks[].media-type` | 13 | L2 | references facet on the root Set: resources[], in the source's own shape, with the uuid that a `(#uuid)` link in a text names | 13 copied |
| `catalog.back-matter.resources[].title` | 246 | L2 | references facet on the root Set: resources[], in the source's own shape, with the uuid that a `(#uuid)` link in a text names | 246 copied |
| `catalog.back-matter.resources[].uuid` | 246 | L2 | references facet on the root Set: resources[], in the source's own shape, with the uuid that a `(#uuid)` link in a text names | 246 copied |
| `catalog.groups[].groups[].groups[].controls[].class` | 1,150 | L1 by rule | category Sets set/tax/by-class-<class>: id, title, file name and membership | 1,150 transformed |
| `catalog.groups[].groups[].groups[].controls[].id` | 1,150 | L1 by rule | Requirement id (URI mint) and file name; label where the control has no `label` prop; `ref` of its entry in every Set it is a member of | 1,150 transformed |
| `catalog.groups[].groups[].groups[].controls[].parts[].id` | 1,150 | L1 by rule | statement id (part-id suffix) | 1,150 transformed |
| `catalog.groups[].groups[].groups[].controls[].parts[].name` | 1,150 | not-content | the name `statement` selects the member `statements` for the part's prose | 1,150 not content |
| `catalog.groups[].groups[].groups[].controls[].parts[].prose` | 1,150 | L1 | statements[].prose.en (+ modality word-rule, documented) | 1,150 copied |
| `catalog.groups[].groups[].groups[].controls[].props[].name` | 8,958 | dispatch | see per-prop rows | 2,202 copied, 5,557 transformed, 1,199 not content |
| `catalog.groups[].groups[].groups[].controls[].props[].ns` | 7,759 | dispatch | see per-prop rows | 2,202 copied, 5,557 not content |
| `catalog.groups[].groups[].groups[].controls[].props[].value` | 8,958 | dispatch | see per-prop rows | 2,251 copied, 5,557 transformed, 1,150 not content |
| `catalog.groups[].groups[].groups[].controls[].title` | 1,150 | L1 | Requirement title | 1,150 copied |
| `catalog.groups[].groups[].groups[].parts[].name` | 470 | L2 | compat facet oscal-1x@1 on the Set of the group: group-parts[].name | 470 copied |
| `catalog.groups[].groups[].groups[].parts[].prose` | 470 | L2 | compat facet oscal-1x@1 on the Set of the group: group-parts[].prose (language-tagged {en}) | 470 copied |
| `catalog.groups[].groups[].groups[].props[].name` | 470 | dispatch | see per-prop rows | 470 not content |
| `catalog.groups[].groups[].groups[].props[].value` | 470 | dispatch | see per-prop rows | 470 not content |
| `catalog.groups[].groups[].groups[].title` | 470 | L1 | Set title; with the titles of the groups above it, the Set id and file name; `group` of its overview parts in the compat facet | 470 copied |
| `catalog.groups[].groups[].parts[].name` | 69 | L2 | compat facet oscal-1x@1 on the Set of the group: group-parts[].name | 69 copied |
| `catalog.groups[].groups[].parts[].prose` | 69 | L2 | compat facet oscal-1x@1 on the Set of the group: group-parts[].prose (language-tagged {en}) | 69 copied |
| `catalog.groups[].groups[].props[].name` | 75 | dispatch | see per-prop rows | 75 not content |
| `catalog.groups[].groups[].props[].value` | 75 | dispatch | see per-prop rows | 75 not content |
| `catalog.groups[].groups[].title` | 75 | L1 | Set title; with the titles of the groups above it, the Set id and file name; `group` of its overview parts in the compat facet | 75 copied |
| `catalog.groups[].props[].name` | 25 | dispatch | see per-prop rows | 25 not content |
| `catalog.groups[].props[].value` | 25 | dispatch | see per-prop rows | 25 not content |
| `catalog.groups[].title` | 25 | L1 | Set title; with the titles of the groups above it, the Set id and file name; `group` of its overview parts in the compat facet | 25 copied |
| `catalog.metadata.last-modified` | 1 | L2 | compat facet oscal-1x@1 on the root Set: metadata; its day is the manifest's provenance.date | 1 copied |
| `catalog.metadata.links[].href` | 5 | L2 | compat facet oscal-1x@1 on the root Set: metadata, in the source's own shape | 5 copied |
| `catalog.metadata.links[].rel` | 5 | L2 | compat facet oscal-1x@1 on the root Set: metadata, in the source's own shape | 5 copied |
| `catalog.metadata.oscal-version` | 1 | L2 | compat facet oscal-1x@1 on the root Set: metadata; manifest provenance.source-oscal-version | 1 copied |
| `catalog.metadata.parties[].addresses[].addr-lines[]` | 3 | L2 | compat facet oscal-1x@1 on the root Set: metadata, in the source's own shape | 3 copied |
| `catalog.metadata.parties[].addresses[].city` | 1 | L2 | compat facet oscal-1x@1 on the root Set: metadata, in the source's own shape | 1 copied |
| `catalog.metadata.parties[].addresses[].country` | 1 | L2 | compat facet oscal-1x@1 on the root Set: metadata, in the source's own shape | 1 copied |
| `catalog.metadata.parties[].addresses[].postal-code` | 1 | L2 | compat facet oscal-1x@1 on the root Set: metadata, in the source's own shape | 1 copied |
| `catalog.metadata.parties[].addresses[].state` | 1 | L2 | compat facet oscal-1x@1 on the root Set: metadata, in the source's own shape | 1 copied |
| `catalog.metadata.parties[].addresses[].type` | 1 | L2 | compat facet oscal-1x@1 on the root Set: metadata, in the source's own shape | 1 copied |
| `catalog.metadata.parties[].email-addresses[]` | 1 | L2 | compat facet oscal-1x@1 on the root Set: metadata, in the source's own shape | 1 copied |
| `catalog.metadata.parties[].links[].href` | 1 | L2 | compat facet oscal-1x@1 on the root Set: metadata, in the source's own shape | 1 copied |
| `catalog.metadata.parties[].links[].rel` | 1 | L2 | compat facet oscal-1x@1 on the root Set: metadata, in the source's own shape | 1 copied |
| `catalog.metadata.parties[].name` | 1 | L2 | compat facet oscal-1x@1 on the root Set: metadata; the name of the party the document names as its author makes the manifest's provenance.author-ref | 1 copied |
| `catalog.metadata.parties[].short-name` | 1 | L2 | compat facet oscal-1x@1 on the root Set: metadata, in the source's own shape | 1 copied |
| `catalog.metadata.parties[].type` | 1 | L2 | compat facet oscal-1x@1 on the root Set: metadata, in the source's own shape | 1 copied |
| `catalog.metadata.parties[].uuid` | 1 | L2 | compat facet oscal-1x@1 on the root Set: metadata, in the source's own shape | 1 copied |
| `catalog.metadata.published` | 1 | L2 | compat facet oscal-1x@1 on the root Set: metadata, in the source's own shape | 1 copied |
| `catalog.metadata.responsible-parties[].party-uuids[]` | 1 | L2 | compat facet oscal-1x@1 on the root Set: metadata, in the source's own shape | 1 copied |
| `catalog.metadata.responsible-parties[].role-id` | 1 | L2 | compat facet oscal-1x@1 on the root Set: metadata, in the source's own shape | 1 copied |
| `catalog.metadata.roles[].id` | 1 | L2 | compat facet oscal-1x@1 on the root Set: metadata, in the source's own shape | 1 copied |
| `catalog.metadata.roles[].title` | 1 | L2 | compat facet oscal-1x@1 on the root Set: metadata, in the source's own shape | 1 copied |
| `catalog.metadata.title` | 1 | L1 | title of the root Set (set/tax/ism) | 1 copied |
| `catalog.metadata.version` | 1 | L1 | `version` of every object; manifest provenance.source-version | 1 copied |
| `catalog.uuid` | 1 | L2 | compat facet oscal-1x@1 on the root Set: uuid (the uuid of the source document) | 1 copied |

## UNMAPPED (gate target: zero)

*(none)*

## Conversion ledger

### Rules

A value the converter computes is made by a named rule. For every destination the ledger applied the rule to the source again and compared the result with the written file.

| rule | source values | destinations |
|---|---:|---:|
| Requirement id from the control id | 1,150 | 3,450 |
| author of the source: the party its document names as its author (the role `creator`, else `prepared-by`, else the one party it names); a landmark URI from the party's name | 1 | 1 |
| baseline Set id from the prop name (its kind) and the marker | 11,114 | 22,228 |
| baseline Set title from the prop name (its kind) and the marker | 11,114 | 11,114 |
| category Set id from the class | 1,150 | 2,300 |
| category Set title from the class | 1,150 | 1,150 |
| date of the source: the day of the document's last-modified | 1 | 1 |
| entry in the baseline Set that the control's marker names: the Requirement of the control | 12,264 | 16,671 |
| entry in the category Set that the control's class names: the Requirement of the control | 2,300 | 2,300 |
| file name of the Requirement from the control id | 1,150 | 1,150 |
| file name of the baseline Set from the prop name (its kind) and the marker | 11,114 | 11,114 |
| file name of the category Set from the class | 1,150 | 1,150 |
| file name of the taxonomy Set from the titles of the group and of the groups above it | 570 | 1,585 |
| label from the control id (ism-1234 -> ISM-1234; an id of another form as it is) | 1,101 | 1,101 |
| modality word-rule over the statement prose | 1,150 | 1,150 |
| statement id: the part id after its last underscore | 1,150 | 1,150 |
| taxonomy Set id from the titles of the group and of the groups above it | 570 | 4,755 |

One of several equal occurrences: every control that carries the marker names the same Set; the Set is written once. The marker of a control does not change the value of the control's entry in the Set, it decides in which Set the entry stands; the check is that the Set id made from this control's own marker is the id of the Set the entry stands in. Not stated as a rule, because it is no function of source values: `sequence` (a counter over document order) and the digests (made from the written objects).

### What is no content

A value that is not written and is no content, by one of three rules. The ledger checked each: a name against the names this mapping reads, and against what became of the value it selects; a namespace against the one the mapping is written for; a rebuilt id by applying the function to the source's own values.

| kind | values | rule |
|---|---:|---|
| namespace | 5,557 | the namespace of a prop: the one this mapping reads the prop's name in |
| rebuilt-id | 1,720 | a sort-id is its parent's sort-id, the kind of the element and its position among its siblings, written with as many digits as their number has |
| selector | 1,150 | the name `statement` of a control's part selects the member `statements` for its prose |
| selector | 1,769 | the name of a prop selects the member its value is written to, or the rule that reads it |

### Declared drops that remain

A value that reached no destination, for a declared reason. Since the author's decisions of 2026-11-14 none is left: the uuid of the source document, the last one, is carried on the root Set.

*(none)*

### Where the path map and the ledger disagree

Computed for every value: the level its row of the path map gives it (for a leaf of a prop, the row of that prop) against the outcome the ledger found. L1 and L2 agree with copied only, L1 by rule with transformed (and with copied, where the value also stands somewhere as it is), not-content with no content, declared-drop with dropped. A row that disagrees ends the run.

*(nowhere)*

### Read back from the written bundle

Counted over the files of the bundle after they were written, not over the converter's variables.

| what | count |
|---|---:|
| requirements | 1,150 |
| sets | 581 |
| sets with no member | 16 |
| requirements with revision | 1,101 |
| requirements with updated | 1,101 |
| resources | 246 |
| links in texts | 481 |
| links that name a resource of the bundle | 481 |
| texts with a link | 76 |
| objects with a link | 76 |
| resources a link names | 241 |
| sort ids in the source | 1,720 |
| sort ids rebuilt from the bundle | 1,720 |

### What the kernel has no member for

Carried all the same, in a facet, in the source's own shape; each is a finding about the kernel or the standard facets.

- A control's own revision number and the month of its last change (props `revision` and `updated`): 1,101 and 1,101. `version` is the catalogue's on every object. In the compat facet oscal-1x@1 of the Requirement, `props`.
- The document's metadata beyond title and version (dates, OSCAL version, links, roles, parties, responsible parties): 32 values. In the compat facet oscal-1x@1 of the root Set, `metadata`.
- The resources a text refers to (back-matter): 246 resources, 763 values. In a references facet this converter pins, on the root Set; a link in a text names its target by the resource's uuid.
- The overview text of a group: 539 texts. In the compat facet oscal-1x@1 of the group's Set, `group-parts`.

### What the ledger cannot see

The ledger follows source values into the bundle, not the other way round. A value the converter writes on its own has no source value behind it and no entry: the id of the root Set, the lifecycle, the sequence numbers (document order, counted), the digests, and the obligated party of every statement, which is the converter's default or the caller's and not a value of the source. Counted over the leaves of the objects and the manifest as written (the pinned facet schemas are constants of the converter):

| in | pointer | values | example |
|---|---|---:|---|
| Requirement | `/lifecycle` | 1,150 | `active` |
| Requirement | `/statements/[]/obligated-parties/[]` | 1,150 | `https://ns.cyber.gov.au/ism/party/organisation` |
| Set | `/id` | 1 | `https://ns.cyber.gov.au/ism/set/tax/ism` |
| Set | `/lifecycle` | 581 | `active` |
| Set | `/members/[]/sequence` | 8,427 | `10` |
| manifest | `/facet-schemas/[]/digest` | 2 | `sha256:f233c492c958532e40caad8f9e8010d0a224ad556ec5a27a16f3cc5bd9793c09` |
| manifest | `/facet-schemas/[]/exact-version` | 2 | `1.0.0` |
| manifest | `/facet-schemas/[]/id` | 2 | `https://ns.cyber.gov.au/ism/facet/references` |
| manifest | `/facet-schemas/[]/path` | 2 | `schemas/ism-references-1.0.0-stub.json` |
| manifest | `/manifest-version` | 1 | `1` |
| manifest | `/objects/[]/id` | 1 | `https://ns.cyber.gov.au/ism/set/tax/ism` |
| manifest | `/objects/[]/package-digest` | 1,731 | `sha256:9a179baec6f33f5d4b40194d9ea6ae799601c2a9dc561748ebac1f678b76b2ad` |
| manifest | `/objects/[]/path` | 1 | `objects/set-tax-root.json` |
| manifest | `/objects/[]/semantic-digest` | 1,731 | `sha256:cd9473584bf6bc05c3606cb5124af788e8e8213fe95341bcfbe9419bbd1d00d3` |
| manifest | `/provenance/converter` | 1 | `convert_ism.py v0.4` |
| manifest | `/provenance/source` | 1 | `ACSC ISM OSCAL catalog` |

Two more limits. A value that stands at one destination is accounted for, also where another destination of it is lost: a control whose entry in a taxonomy Set was lost would still be counted, by its Requirement. The number of destinations of each rule, in the table above, is where such a loss shows. And a rule is held to what is written, not to what is right: a rule that is wrong and applied the same way twice passes.

## Notes & limits (honest)

- Modality word-rule is a **documented heuristic** over style-guided prose; its full per-code counts are printed above and every assignment is reproducible from the rule. Authority review can override per statement.
- Semantic digests use a JCS-compatible canonicalization (exact here: no floats, ASCII keys); full RFC 8785 lands with the schemas.

## Unaccounted source values (conversion ledger)

No destination, no rule that says it is no content, no declared reason: a value the converter loses. A run that has one ends with 1. `ism-conversion-ledger.json` holds the count and the first pointers of every path.

*(none)*
