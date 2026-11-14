# ISM -> Semantic Core: Coverage Report (computed)

Source: ACSC ISM OSCAL catalog v2026.06.18 (oscal-version 1.1.2) - 1,150 controls, 570 groups.

## Totals

- Source leaf values inventoried: **36,161**
- Mapped (declared destination): **36,161**
- **UNMAPPED: 0**  ->  coverage **100.0 %**

- Objects emitted: **1,150 Requirements**, **561 Sets**, manifest with both digests per object.

## Conversion rules (declared, counted)

- **Modality word-rule** over statement prose (first match of must not > should not > must > should > may, else unspecified): unspecified x1149, may x1.
- **Obligated party**: `https://ns.cyber.gov.au/ism/party/organisation` on every statement. This is the converter's default and not a value of the source; `--obligated-party URI` writes another. Why this default: ISM binds the organisation implicitly; no per-control party data in source.
- **Labels**: 49 from `label` props; 1101 derived from control id (`ism-1234` -> `ISM-1234`).
- **sequence**: document order (steps of 10); source `sort-id` path-strings (1,150 control + 570 group) thereby absorbed as redundant.
- **class** -> category Sets: ISM-control (1101), ISM-principle (49).
- **applicability** -> baseline Sets: NC (1024), OS (1035), P (1035), S (1099), TS (1108); **essential-eight** -> ML1 (46), ML2 (87), ML3 (123).
- **revision/updated** (x1,101 each): history -> L0 (catalog version on every object; per-release notes belong to manifests) - values not object-carried.
- **Guideline narrative** (`overview` parts on groups, x539): **Level 2** compat facet `oscal-1x@1` on the nearest emitted Set - the declared waiting room with a clock (handbook 14.6); residue KPI starts at 539.
- **Empty narrative groups skipped** (no transitive controls, no parts): 2 (front-matter chapters; declared drop).
- **Payload free text language-tagged** per corpus language (`{en: ...}` on compat `group-parts[].prose`, x539); statement prose was already tagged. Harmonized 2026-07-21 (backlog #12).

### Corpus finding (new vs. census)

ISM statement prose is **declarative present tense** ('The board ... defines', 'Passphrases are ...'): modal verbs are structurally absent, not merely unencoded. The census note 'style-guide prose' was too generous. Consequence: `unspecified` is the *honest* modality for this corpus, and binding force is carried by baseline membership (the applicability Sets) - exactly the legitimate Core-tier pattern for narrative frameworks. The single lexical hit is counted above.

## Per-prop destinations

| source prop | count | level | destination |
|---|---:|---|---|
| `props[].name = sort-id` | 1720 | L1 | absorbed: document order -> members[].sequence (path-string redundant) |
| `props[].name = label` | 49 | L1 | Requirement.label |
| `props[].name = applicability` | 5301 | L1 | membership -> set/baseline/<marker> |
| `props[].name = essential-eight-applicability` | 256 | L1 | membership -> set/baseline/e8-<level> |
| `props[].name = revision` | 1101 | L1 | history -> L0 (object versions/manifest); value not object-carried |
| `props[].name = updated` | 1101 | L1 | history -> L0 (object versions/manifest); value not object-carried |

## Full path map (every source path, its count, its destination)

| path | count | level | destination |
|---|---:|---|---|
| `catalog.back-matter.resources[].props[].name` | 2 | declared-drop | source-document references (guideline PDFs/links) - not requirement data |
| `catalog.back-matter.resources[].props[].value` | 2 | declared-drop | source-document references (guideline PDFs/links) - not requirement data |
| `catalog.back-matter.resources[].rlinks[].href` | 254 | declared-drop | source-document references (guideline PDFs/links) - not requirement data |
| `catalog.back-matter.resources[].rlinks[].media-type` | 13 | declared-drop | source-document references (guideline PDFs/links) - not requirement data |
| `catalog.back-matter.resources[].title` | 246 | declared-drop | source-document references (guideline PDFs/links) - not requirement data |
| `catalog.back-matter.resources[].uuid` | 246 | declared-drop | source-document references (guideline PDFs/links) - not requirement data |
| `catalog.groups[].groups[].groups[].controls[].class` | 1,150 | L1 | category Sets: set/tax/principles | set/tax/controls |
| `catalog.groups[].groups[].groups[].controls[].id` | 1,150 | L1 | Requirement id (URI mint) + label derivation |
| `catalog.groups[].groups[].groups[].controls[].parts[].id` | 1,150 | L1 | statement id (part-id suffix) |
| `catalog.groups[].groups[].groups[].controls[].parts[].name` | 1,150 | L1 | statement (the one part kind present) |
| `catalog.groups[].groups[].groups[].controls[].parts[].prose` | 1,150 | L1 | statements[].prose.en (+ modality word-rule, documented) |
| `catalog.groups[].groups[].groups[].controls[].props[].name` | 8,958 | L1 | dispatch (see per-prop rows) |
| `catalog.groups[].groups[].groups[].controls[].props[].ns` | 7,759 | L1 | prop namespace: absorbed (kernel fields need none) |
| `catalog.groups[].groups[].groups[].controls[].props[].value` | 8,958 | L1 | dispatch (see per-prop rows) |
| `catalog.groups[].groups[].groups[].controls[].title` | 1,150 | L1 | Requirement title |
| `catalog.groups[].groups[].groups[].parts[].name` | 470 | L2 | compat facet oscal-1x@1: guideline overview narrative on the Set |
| `catalog.groups[].groups[].groups[].parts[].prose` | 470 | L2 | compat facet oscal-1x@1: guideline overview narrative on the Set (language-tagged {en}) |
| `catalog.groups[].groups[].groups[].props[].name` | 470 | L1 | group sort-id: absorbed by document order -> sequence |
| `catalog.groups[].groups[].groups[].props[].value` | 470 | L1 | group sort-id: absorbed by document order -> sequence |
| `catalog.groups[].groups[].groups[].title` | 470 | L1 | Set title |
| `catalog.groups[].groups[].parts[].name` | 69 | L2 | compat facet oscal-1x@1: guideline overview narrative on the Set |
| `catalog.groups[].groups[].parts[].prose` | 69 | L2 | compat facet oscal-1x@1: guideline overview narrative on the Set (language-tagged {en}) |
| `catalog.groups[].groups[].props[].name` | 75 | L1 | group sort-id: absorbed by document order -> sequence |
| `catalog.groups[].groups[].props[].value` | 75 | L1 | group sort-id: absorbed by document order -> sequence |
| `catalog.groups[].groups[].title` | 75 | L1 | Set title |
| `catalog.groups[].props[].name` | 25 | L1 | group sort-id: absorbed by document order -> sequence |
| `catalog.groups[].props[].value` | 25 | L1 | group sort-id: absorbed by document order -> sequence |
| `catalog.groups[].title` | 25 | L1 | Set title |
| `catalog.metadata.last-modified` | 1 | L1 | bundle manifest / L0 provenance |
| `catalog.metadata.links[].href` | 5 | L1 | bundle manifest / L0 provenance (publisher identity) |
| `catalog.metadata.links[].rel` | 5 | L1 | bundle manifest / L0 provenance (publisher identity) |
| `catalog.metadata.oscal-version` | 1 | L1 | bundle manifest / L0 provenance |
| `catalog.metadata.parties[].addresses[].addr-lines[]` | 3 | L1 | bundle manifest / L0 provenance (publisher identity) |
| `catalog.metadata.parties[].addresses[].city` | 1 | L1 | bundle manifest / L0 provenance (publisher identity) |
| `catalog.metadata.parties[].addresses[].country` | 1 | L1 | bundle manifest / L0 provenance (publisher identity) |
| `catalog.metadata.parties[].addresses[].postal-code` | 1 | L1 | bundle manifest / L0 provenance (publisher identity) |
| `catalog.metadata.parties[].addresses[].state` | 1 | L1 | bundle manifest / L0 provenance (publisher identity) |
| `catalog.metadata.parties[].addresses[].type` | 1 | L1 | bundle manifest / L0 provenance (publisher identity) |
| `catalog.metadata.parties[].email-addresses[]` | 1 | L1 | bundle manifest / L0 provenance (publisher identity) |
| `catalog.metadata.parties[].links[].href` | 1 | L1 | bundle manifest / L0 provenance (publisher identity) |
| `catalog.metadata.parties[].links[].rel` | 1 | L1 | bundle manifest / L0 provenance (publisher identity) |
| `catalog.metadata.parties[].name` | 1 | L1 | bundle manifest / L0 provenance (publisher identity) |
| `catalog.metadata.parties[].short-name` | 1 | L1 | bundle manifest / L0 provenance (publisher identity) |
| `catalog.metadata.parties[].type` | 1 | L1 | bundle manifest / L0 provenance (publisher identity) |
| `catalog.metadata.parties[].uuid` | 1 | L1 | bundle manifest / L0 provenance (publisher identity) |
| `catalog.metadata.published` | 1 | L1 | bundle manifest / L0 provenance |
| `catalog.metadata.responsible-parties[].party-uuids[]` | 1 | L1 | bundle manifest / L0 provenance (publisher identity) |
| `catalog.metadata.responsible-parties[].role-id` | 1 | L1 | bundle manifest / L0 provenance (publisher identity) |
| `catalog.metadata.roles[].id` | 1 | L1 | bundle manifest / L0 provenance (publisher identity) |
| `catalog.metadata.roles[].title` | 1 | L1 | bundle manifest / L0 provenance (publisher identity) |
| `catalog.metadata.title` | 1 | L1 | bundle manifest / L0 provenance |
| `catalog.metadata.version` | 1 | L1 | bundle manifest / L0 provenance |
| `catalog.uuid` | 1 | L1 | bundle manifest / L0 provenance |

## UNMAPPED (gate target: zero)

*(none)*

## Notes & limits (honest)

- Modality word-rule is a **documented heuristic** over style-guided prose; its full per-code counts are printed above and every assignment is reproducible from the rule. Authority review can override per statement.
- `props[].ns` values (the exemplary versioned ISM namespace) are absorbed: kernel fields need no namespace.
- Semantic digests use a JCS-compatible canonicalization (exact here: no floats, ASCII keys); full RFC 8785 lands with the schemas.
