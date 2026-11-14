# ISM -> Semantic Core: Coverage Report (computed)

Source: ACSC ISM OSCAL catalog v2026.06.18 (oscal-version 1.1.2) - 1,150 controls, 570 groups.

## Totals

- Source leaf values inventoried: **36,161**
- Mapped (declared destination): **36,161**
- **UNMAPPED: 0**  ->  coverage **100.0 %**

- Objects emitted: **1,150 Requirements**, **561 Sets**, manifest with both digests per object.

- **Conversion ledger (measured per source value; the figures above are a DECLARATION)**: the path map says for every source path where its values are meant to go, and `UNMAPPED: 0` says that no path lacks such a sentence. The ledger follows each of the 36,161 source leaf values through the converter into the written files. **3,947 copied** (the value stands, with its type, at the destination named, read back from the written file), **14,662 transformed** (a named rule made the destination from it; the rule was applied to the source again and compared), **13,130 intentionally dropped** (a stated reason), **4,422 unaccounted** (no destination and no declared reason). Checks that failed: 0. An equal value elsewhere in the bundle does not count: a value is traced by what the converter did with it. `ism-conversion-ledger.json` is the record, one row per source path and outcome (59 rows; the entry of each single value is made and checked in the run and not written). Rules, declared drops and findings: section "Conversion ledger" below. The unaccounted values are listed by path at the end of this report; they are the work queue of backlog #41.

## Conversion rules (declared, counted)

- **Modality word-rule** over statement prose (first match of must not > should not > must > should > may, else unspecified): unspecified x1149, may x1.
- **Obligated party**: `https://ns.cyber.gov.au/ism/party/organisation` on every statement. This is the converter's default and not a value of the source; `--obligated-party URI` writes another. Why this default: ISM binds the organisation implicitly; no per-control party data in source.
- **Labels**: 49 from `label` props; 1101 derived from control id (`ism-1234` -> `ISM-1234`).
- **sequence**: document order (steps of 10); source `sort-id` path-strings (1,720 on controls and groups) thereby absorbed as redundant. Checked value by value: 1,720 say their place in the document (the parent's sort-id and the position among the siblings); 0 say something else or stand where the path map has no row, and are not covered.
- **class** -> category Sets: ISM-control (1101), ISM-principle (49).
- **applicability** -> baseline Sets: NC (1024), OS (1035), P (1035), S (1099), TS (1108); **essential-eight** -> ML1 (46), ML2 (87), ML3 (123).
- **revision/updated** (x1,101 and x1,101): **not carried**. The catalogue's version stands on every object; a control's own revision number and the month of its last change stand neither on an object nor in the manifest. Not decided: unaccounted in the ledger.
- **Guideline narrative** (`overview` parts on groups, x539): **Level 2** compat facet `oscal-1x@1` on the nearest emitted Set - the declared waiting room with a clock (handbook 14.6); residue KPI starts at 539.
- **Groups that are no Set** (no control below them): 20, 2 of them at the top level. 16 have an overview part of their own: it is carried on the nearest Set above, which is the root Set where no group above is a Set, and names its group. 4 are headings only, and their titles are not carried (unaccounted in the ledger).
- **Payload free text language-tagged** per corpus language (`{en: ...}` on compat `group-parts[].prose`, x539); statement prose was already tagged. Harmonized 2026-07-21 (backlog #12).

### Corpus finding (new vs. census)

ISM statement prose is **declarative present tense** ('The board ... defines', 'Passphrases are ...'): modal verbs are structurally absent, not merely unencoded. The census note 'style-guide prose' was too generous. Consequence: `unspecified` is the *honest* modality for this corpus, and binding force is carried by baseline membership (the applicability Sets) - exactly the legitimate Core-tier pattern for narrative frameworks. The single lexical hit is counted above.

## Per-prop destinations

The last column is measured: what the ledger found for the name and the value of these props.

| source prop | count | level | destination | ledger (name and value) |
|---|---:|---|---|---|
| `props[].name = sort-id` | 1720 | absorbed | absorbed: document order -> members[].sequence (path-string redundant); the value is not carried | 3,440 intentionally dropped |
| `props[].name = label` | 49 | L1 | Requirement.label | 98 transformed |
| `props[].name = applicability` | 5301 | L1 | membership -> set/baseline/class-<marker> | 10,602 transformed |
| `props[].name = essential-eight-applicability` | 256 | L1 | membership -> set/baseline/e8-<level> | 512 transformed |
| `props[].name = revision` | 1101 | not-carried | not carried and not decided: the control's own revision number stands neither on the object nor in the manifest (the object's version is the catalogue's) | 2,202 unaccounted |
| `props[].name = updated` | 1101 | not-carried | not carried and not decided: the month of the control's last change stands neither on the object nor in the manifest | 2,202 unaccounted |

## Full path map (every source path, its count, its destination)

Levels: L1 a kernel field; L2 a facet; absorbed - not carried as a value, the bundle says the same by other means; declared-drop - not carried, and said so; not-carried - not carried and not decided. The last column is measured: the outcomes the ledger found for the values of the path.

| path | count | level | destination | ledger |
|---|---:|---|---|---|
| `catalog.back-matter.resources[].props[].name` | 2 | declared-drop | source-document references (guideline PDFs/links) - not requirement data | 2 intentionally dropped |
| `catalog.back-matter.resources[].props[].value` | 2 | declared-drop | source-document references (guideline PDFs/links) - not requirement data | 2 intentionally dropped |
| `catalog.back-matter.resources[].rlinks[].href` | 254 | declared-drop | source-document references (guideline PDFs/links) - not requirement data | 254 intentionally dropped |
| `catalog.back-matter.resources[].rlinks[].media-type` | 13 | declared-drop | source-document references (guideline PDFs/links) - not requirement data | 13 intentionally dropped |
| `catalog.back-matter.resources[].title` | 246 | declared-drop | source-document references (guideline PDFs/links) - not requirement data | 246 intentionally dropped |
| `catalog.back-matter.resources[].uuid` | 246 | declared-drop | source-document references (guideline PDFs/links) - not requirement data | 246 intentionally dropped |
| `catalog.groups[].groups[].groups[].controls[].class` | 1,150 | L1 | category Sets set/tax/by-class-<class>: id, title, file name and membership | 1,150 transformed |
| `catalog.groups[].groups[].groups[].controls[].id` | 1,150 | L1 | Requirement id (URI mint) and file name; label where the control has no `label` prop; `ref` of its entry in every Set it is a member of | 1,150 transformed |
| `catalog.groups[].groups[].groups[].controls[].parts[].id` | 1,150 | L1 | statement id (part-id suffix) | 1,150 transformed |
| `catalog.groups[].groups[].groups[].controls[].parts[].name` | 1,150 | declared-drop | type tag `statement` (the one part kind present): not carried as a value; the part is the entry of `statements` | 1,150 intentionally dropped |
| `catalog.groups[].groups[].groups[].controls[].parts[].prose` | 1,150 | L1 | statements[].prose.en (+ modality word-rule, documented) | 1,150 copied |
| `catalog.groups[].groups[].groups[].controls[].props[].name` | 8,958 | L1 | dispatch (see per-prop rows) | 5,606 transformed, 1,150 intentionally dropped, 2,202 unaccounted |
| `catalog.groups[].groups[].groups[].controls[].props[].ns` | 7,759 | absorbed | prop namespace: absorbed (kernel fields need none); the value is not carried | 7,759 intentionally dropped |
| `catalog.groups[].groups[].groups[].controls[].props[].value` | 8,958 | L1 | dispatch (see per-prop rows) | 5,606 transformed, 1,150 intentionally dropped, 2,202 unaccounted |
| `catalog.groups[].groups[].groups[].controls[].title` | 1,150 | L1 | Requirement title | 1,150 copied |
| `catalog.groups[].groups[].groups[].parts[].name` | 470 | L2 | compat facet oscal-1x@1: guideline overview narrative on the Set | 470 copied |
| `catalog.groups[].groups[].groups[].parts[].prose` | 470 | L2 | compat facet oscal-1x@1: guideline overview narrative on the Set (language-tagged {en}) | 470 copied |
| `catalog.groups[].groups[].groups[].props[].name` | 470 | absorbed | group sort-id: absorbed by document order -> sequence; the value is not carried | 470 intentionally dropped |
| `catalog.groups[].groups[].groups[].props[].value` | 470 | absorbed | group sort-id: absorbed by document order -> sequence; the value is not carried | 470 intentionally dropped |
| `catalog.groups[].groups[].groups[].title` | 470 | L1 | Set title; with the titles of the groups above it, the Set id and file name; `group` of its overview parts in the compat facet. A group with no control below it is no Set: its title is carried only where it has an overview part of its own | 470 copied |
| `catalog.groups[].groups[].parts[].name` | 69 | L2 | compat facet oscal-1x@1: guideline overview narrative on the Set | 69 copied |
| `catalog.groups[].groups[].parts[].prose` | 69 | L2 | compat facet oscal-1x@1: guideline overview narrative on the Set (language-tagged {en}) | 69 copied |
| `catalog.groups[].groups[].props[].name` | 75 | absorbed | group sort-id: absorbed by document order -> sequence; the value is not carried | 75 intentionally dropped |
| `catalog.groups[].groups[].props[].value` | 75 | absorbed | group sort-id: absorbed by document order -> sequence; the value is not carried | 75 intentionally dropped |
| `catalog.groups[].groups[].title` | 75 | L1 | Set title; with the titles of the groups above it, the Set id and file name; `group` of its overview parts in the compat facet. A group with no control below it is no Set: its title is carried only where it has an overview part of its own | 73 copied, 2 unaccounted |
| `catalog.groups[].props[].name` | 25 | absorbed | group sort-id: absorbed by document order -> sequence; the value is not carried | 25 intentionally dropped |
| `catalog.groups[].props[].value` | 25 | absorbed | group sort-id: absorbed by document order -> sequence; the value is not carried | 25 intentionally dropped |
| `catalog.groups[].title` | 25 | L1 | Set title; with the titles of the groups above it, the Set id and file name; `group` of its overview parts in the compat facet. A group with no control below it is no Set: its title is carried only where it has an overview part of its own | 23 copied, 2 unaccounted |
| `catalog.metadata.last-modified` | 1 | not-carried | not carried and not decided: the manifest names the source by its version, not by its dates | 1 unaccounted |
| `catalog.metadata.links[].href` | 5 | not-carried | not carried and not decided: links of the document to back-matter resources (other serialisations and neighbouring versions of the catalogue) | 5 unaccounted |
| `catalog.metadata.links[].rel` | 5 | not-carried | not carried and not decided: links of the document to back-matter resources (other serialisations and neighbouring versions of the catalogue) | 5 unaccounted |
| `catalog.metadata.oscal-version` | 1 | L1 | manifest provenance.source-oscal-version | 1 copied |
| `catalog.metadata.parties[].addresses[].addr-lines[]` | 3 | declared-drop | the source's directory of parties and roles: not carried | 3 intentionally dropped |
| `catalog.metadata.parties[].addresses[].city` | 1 | declared-drop | the source's directory of parties and roles: not carried | 1 intentionally dropped |
| `catalog.metadata.parties[].addresses[].country` | 1 | declared-drop | the source's directory of parties and roles: not carried | 1 intentionally dropped |
| `catalog.metadata.parties[].addresses[].postal-code` | 1 | declared-drop | the source's directory of parties and roles: not carried | 1 intentionally dropped |
| `catalog.metadata.parties[].addresses[].state` | 1 | declared-drop | the source's directory of parties and roles: not carried | 1 intentionally dropped |
| `catalog.metadata.parties[].addresses[].type` | 1 | declared-drop | the source's directory of parties and roles: not carried | 1 intentionally dropped |
| `catalog.metadata.parties[].email-addresses[]` | 1 | declared-drop | the source's directory of parties and roles: not carried | 1 intentionally dropped |
| `catalog.metadata.parties[].links[].href` | 1 | declared-drop | the source's directory of parties and roles: not carried | 1 intentionally dropped |
| `catalog.metadata.parties[].links[].rel` | 1 | declared-drop | the source's directory of parties and roles: not carried | 1 intentionally dropped |
| `catalog.metadata.parties[].name` | 1 | declared-drop | the source's directory of parties and roles: not carried | 1 intentionally dropped |
| `catalog.metadata.parties[].short-name` | 1 | declared-drop | the source's directory of parties and roles: not carried | 1 intentionally dropped |
| `catalog.metadata.parties[].type` | 1 | declared-drop | the source's directory of parties and roles: not carried | 1 intentionally dropped |
| `catalog.metadata.parties[].uuid` | 1 | declared-drop | the source's directory of parties and roles: not carried | 1 intentionally dropped |
| `catalog.metadata.published` | 1 | not-carried | not carried and not decided: the manifest names the source by its version, not by its dates | 1 unaccounted |
| `catalog.metadata.responsible-parties[].party-uuids[]` | 1 | not-carried | not carried and not decided: who prepared the source document | 1 unaccounted |
| `catalog.metadata.responsible-parties[].role-id` | 1 | not-carried | not carried and not decided: who prepared the source document | 1 unaccounted |
| `catalog.metadata.roles[].id` | 1 | declared-drop | the source's directory of parties and roles: not carried | 1 intentionally dropped |
| `catalog.metadata.roles[].title` | 1 | declared-drop | the source's directory of parties and roles: not carried | 1 intentionally dropped |
| `catalog.metadata.title` | 1 | L1 | title of the root Set (set/tax/ism) | 1 copied |
| `catalog.metadata.version` | 1 | L1 | `version` of every object; manifest provenance.source-version | 1 copied |
| `catalog.uuid` | 1 | declared-drop | the uuid of the source document: not carried | 1 intentionally dropped |

## UNMAPPED (gate target: zero)

*(none)*

## Conversion ledger

### Rules

A value the converter computes is made by a named rule. For every destination the ledger applied the rule to the source again and compared the result with the written file.

| rule | source values | destinations |
|---|---:|---:|
| Requirement id from the control id | 1,150 | 3,450 |
| baseline Set id from the prop name (its kind) and the marker | 11,114 | 22,228 |
| baseline Set title from the prop name (its kind) and the marker | 11,114 | 11,114 |
| category Set id from the class | 1,150 | 2,300 |
| category Set title from the class | 1,150 | 1,150 |
| entry in the baseline Set that the control's marker names: the Requirement of the control | 12,264 | 16,671 |
| entry in the category Set that the control's class names: the Requirement of the control | 2,300 | 2,300 |
| file name of the Requirement from the control id | 1,150 | 1,150 |
| file name of the baseline Set from the prop name (its kind) and the marker | 11,114 | 11,114 |
| file name of the category Set from the class | 1,150 | 1,150 |
| file name of the taxonomy Set from the titles of the group and of the groups above it | 550 | 1,533 |
| label from the control id (ism-1234 -> ISM-1234; an id of another form as it is) | 1,101 | 1,101 |
| label: the value of the prop that is named `label`, unchanged | 98 | 98 |
| modality word-rule over the statement prose | 1,150 | 1,150 |
| statement id: the part id after its last underscore | 1,150 | 1,150 |
| taxonomy Set id from the titles of the group and of the groups above it | 550 | 4,599 |

One of several equal occurrences: every control that carries the marker names the same Set; the Set is written once. The marker of a control does not change the value of the control's entry in the Set, it decides in which Set the entry stands; the check is that the Set id made from this control's own marker is the id of the Set the entry stands in. A label taken from a `label` prop is the prop's value unchanged; it is counted as transformed, because the rule that selects it by the prop's name carries the name and the value. Not stated as a rule, because it is no function of source values: `sequence` (a counter over document order; the `sort-id` says the same order and is absorbed) and the digests (made from the written objects).

### Declared drops

A drop is declared in two cases only. **Path map**: this converter's path map said before the ledger that the path is not carried (11,962 values). **As decided for IFA**: the class is one the author decided for the IFA corpus on 2026-11-13 (1,168 values). A drop applies only to a value that reached no destination, and it is declared on the row of the path map, for that path. Values dropped where the path map does not call the path absorbed or a declared drop: 0 (a run that has one ends with an error).

| case | values | reason |
|---|---:|---|
| path map | 3,440 | path map, absorbed by document order -> members[].sequence: this sort-id is its parent's sort-id and the element's position among its siblings (checked for this value) |
| path map | 7,759 | path map, absorbed: the namespace of a prop; kernel fields need none |
| path map | 763 | path map, declared drop: source-document references (guideline PDFs/links) - not requirement data |
| as decided for IFA | 1,150 | as decided for IFA on 2026-11-13: a type tag of a structural element: the bundle says by its shape what kind of thing the element is (the part named `statement` is the entry of `statements`) |
| as decided for IFA | 17 | as decided for IFA on 2026-11-13: the source's directory of parties and roles: a party is a landmark URI and there is no party object (register, backlog #16) |
| as decided for IFA | 1 | as decided for IFA on 2026-11-13: the uuid of a source element identifies it inside the source document; JASCON objects get URIs minted from names and titles, the uuid itself is not carried |

### Where the path map and the ledger disagree

Computed for every value: the level its row of the path map gives it (for the name and the value of a control's prop, the row of that prop) against the outcome the ledger found. L1 and L2 agree with copied and transformed, absorbed and declared-drop with intentionally dropped, not-carried with unaccounted.

| path | level | ledger | values | first value |
|---|---|---|---:|---|
| `catalog.groups[].groups[].title` | L1 | unaccounted | 2 | `ism#/catalog/groups/0/groups/0/title` |
| `catalog.groups[].title` | L1 | unaccounted | 2 | `ism#/catalog/groups/0/title` |

### What the ledger cannot see

The ledger follows source values into the bundle, not the other way round. A value the converter writes on its own has no source value behind it and no entry: the id of the root Set, the lifecycle, the sequence numbers (document order, counted), the digests, and the obligated party of every statement, which is the converter's default or the caller's and not a value of the source. Counted over the leaves of the objects and the manifest as written (the pinned facet schema is a constant of the converter):

| in | pointer | values | example |
|---|---|---:|---|
| Requirement | `/lifecycle` | 1,150 | `active` |
| Requirement | `/statements/[]/obligated-parties/[]` | 1,150 | `https://ns.cyber.gov.au/ism/party/organisation` |
| Set | `/id` | 1 | `https://ns.cyber.gov.au/ism/set/tax/ism` |
| Set | `/lifecycle` | 561 | `active` |
| Set | `/members/[]/sequence` | 8,407 | `10` |
| manifest | `/facet-schemas/[]/digest` | 1 | `sha256:6494725928e95089b6d5b63fcf6117fb1065a67be1186c7c80a1c8559e4aecdc` |
| manifest | `/facet-schemas/[]/exact-version` | 1 | `1.0.0` |
| manifest | `/facet-schemas/[]/id` | 1 | `https://ns.jascon.net/compat/oscal-1x` |
| manifest | `/facet-schemas/[]/path` | 1 | `schemas/oscal-1x-compat-1.0.0-stub.json` |
| manifest | `/manifest-version` | 1 | `1` |
| manifest | `/objects/[]/id` | 1 | `https://ns.cyber.gov.au/ism/set/tax/ism` |
| manifest | `/objects/[]/package-digest` | 1,711 | `sha256:07af7206d1d7920c632b80cd977a79d22e55f952de388313281208b1aa6d9a9f` |
| manifest | `/objects/[]/path` | 1 | `objects/set-tax-root.json` |
| manifest | `/objects/[]/semantic-digest` | 1,711 | `sha256:393ec6026a75d4dc35cbe9967607fc198fcd0ff1ae49ae08d980f748d2128ca6` |
| manifest | `/provenance/converter` | 1 | `convert_ism.py v0.2` |
| manifest | `/provenance/source` | 1 | `ACSC ISM OSCAL catalog` |

Two more limits. A value that stands at one destination is accounted for, also where another destination of it is lost: a control whose entry in a taxonomy Set was lost would still be counted, by its Requirement. The number of destinations of each rule, in the table above, is where such a loss shows. And a rule is held to what is written, not to what is right: a rule that is wrong and applied the same way twice passes.

### Findings of the ledger

- **Sentences of the path map that the ledger corrected** (2026-11-14; each said where a value goes, and the value is not there):
  1. `catalog.uuid`, `catalog.metadata.published`, `catalog.metadata.last-modified`: said "bundle manifest / L0 provenance". The manifest holds the version and the OSCAL version of the source and nothing else of its metadata.
  2. `catalog.metadata.title`: said "bundle manifest / L0 provenance". It is the title of the root Set.
  3. `catalog.metadata.links[]`, `.roles[]`, `.parties[]`, `.responsible-parties[]`: said "bundle manifest / L0 provenance (publisher identity)". None of these values is in the bundle; the manifest names the source by a text of the converter.
  4. props `revision` and `updated`: said "history -> L0 (object versions/manifest); value not object-carried". The version of an object is the catalogue's; the manifest holds neither value.
  5. `controls[].class`: said "category Sets: set/tax/principles | set/tax/controls". The Sets are `set/tax/by-class-<class>`.
  6. prop `applicability`: said "membership -> set/baseline/<marker>". The Sets are `set/baseline/class-<marker>`.
  7. `groups[].title` at every depth: said "Set title". A group with no control below it is no Set; its title is in the bundle only where the group has an overview part of its own (as `group` of that part).
  8. the rule line "Empty narrative groups skipped (no transitive controls, no parts): 2 (front-matter chapters; declared drop)". The two chapters are not empty: the groups below them hold overview texts, which are carried on the root Set. What is not carried is said in the next finding.
- **Titles that are lost x4**: a group that is no Set and has no overview part of its own is a heading only, and nothing in the bundle holds its title: `ism#/catalog/groups/0/title`, `ism#/catalog/groups/0/groups/0/title`, `ism#/catalog/groups/0/groups/1/title`, `ism#/catalog/groups/24/title`. The overview parts below such a heading stand on the root Set under the title of their own group; under which heading they stood is not carried.
- **Links of carried text into what is not carried**: 76 overview texts hold 481 markdown links `(#uuid)` to 241 of the 246 back-matter resources. The texts are carried verbatim; the resources (title and address) are a declared drop of the path map, so these links name nothing in the bundle.

## Notes & limits (honest)

- Modality word-rule is a **documented heuristic** over style-guided prose; its full per-code counts are printed above and every assignment is reproducible from the rule. Authority review can override per statement.
- `props[].ns` values (the exemplary versioned ISM namespace) are absorbed: kernel fields need no namespace.
- Semantic digests use a JCS-compatible canonicalization (exact here: no floats, ASCII keys); full RFC 8785 lands with the schemas.

## Unaccounted source values (conversion ledger)

No destination and no declared reason. Each is either carried by a rule the converter does not state yet, or dropped without a decision. `ism-conversion-ledger.json` holds the count and the first pointers of every path.

| path | count | first value |
|---|---:|---|
| `ism.catalog.groups[].groups[].groups[].controls[].props[].name` | 2,202 | `ism#/catalog/groups/2/groups/0/groups/0/controls/0/props/1/name` |
| `ism.catalog.groups[].groups[].groups[].controls[].props[].value` | 2,202 | `ism#/catalog/groups/2/groups/0/groups/0/controls/0/props/1/value` |
| `ism.catalog.groups[].groups[].title` | 2 | `ism#/catalog/groups/0/groups/0/title` |
| `ism.catalog.groups[].title` | 2 | `ism#/catalog/groups/0/title` |
| `ism.catalog.metadata.last-modified` | 1 | `ism#/catalog/metadata/last-modified` |
| `ism.catalog.metadata.links[].href` | 5 | `ism#/catalog/metadata/links/0/href` |
| `ism.catalog.metadata.links[].rel` | 5 | `ism#/catalog/metadata/links/0/rel` |
| `ism.catalog.metadata.published` | 1 | `ism#/catalog/metadata/published` |
| `ism.catalog.metadata.responsible-parties[].party-uuids[]` | 1 | `ism#/catalog/metadata/responsible-parties/0/party-uuids/0` |
| `ism.catalog.metadata.responsible-parties[].role-id` | 1 | `ism#/catalog/metadata/responsible-parties/0/role-id` |
