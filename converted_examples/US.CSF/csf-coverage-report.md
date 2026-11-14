# NIST CSF 2.0 -> Semantic Core: Coverage Report (computed)

Source: **Electronic Version of NIST Cybersecurity Framework 2.0** framework v2.0 (OSCAL rendition 1.2.0, OSCAL v1.2.2). Census: `drafts/gate-3-census.md` §3/§6.

## Totals

- Source leaf values inventoried: **4,726**
- Mapped (declared destination): **4,726**
- **UNMAPPED: 0**  ->  coverage **100.0 %**
- Objects emitted: **106 Requirements** (subcategories), **29 Sets** (6 functions + 22 categories + root), manifest with both digests.

## Conversion rules (declared, counted)

- **Functions and categories are Sets, subcategories are Requirements** - the C5 rule (membership decides granularity), D21 taxonomy nesting at 3 levels.
- **Category statement prose -> narrative@1 on the category Set** - summary prose, not an obligation; the requirement surface is the subcategory layer.
- **Modality `unspecified` x106**: CSF outcomes are declarative ('Outcomes ... are understood and communicated') - sixth-corpus confirmation of the national declarative pattern; force rides adoption, not mood.
- **Withdrawn tombstones dropped, lineage inverted**: 91 withdrawn (12 categories + 79 subcategories - the 1.1->2.0 restructuring cut at BOTH levels), 134 successor edges on Requirements/Sets + 1 on function Sets (ID.GV 'moved to GV' - the sa-12->SR pattern) (incorporated_into->merged-into, moved_to->renamed); tombstone 1.1 outcome prose carried in the annotation (CSF titles are bare ids - the prose IS the content); chains x0, dangling x0, without a successor link x4; no live subcategory sits under a withdrawn category (asserted).
- **Implementation examples -> examples@1** x363 (ids kept - the CSF example numbering is citable); **risk-party -> csf@1** x103 (remarks carried; the first risk-party prop of a subcategory only).
- **Obligated party**: `https://ns.nist.gov/csf/party/organization` on every statement. This is the converter's default and not a value of the source; `--obligated-party URI` writes another. Why this default: CSF binds the adopting organization.
- **Payload free text language-tagged**: category-statement x22, example x363, overview x6.

## Findings (computed)

- **Rel-code spelling divergence (source finding)**: CSF 2.0 uses `incorporated_into`/`moved_to` (underscores) where SP 800-53 Rev 5 uses `incorporated-into`/`moved-to` (hyphens) - same publisher, same semantic, two spellings. REPORTED upstream.
- **Fragment marker missing x135** (source finding): none of the 135 successor addresses of this rendition carries the fragment marker - DE.DP-04's is `DE.AE-06` (a relative URI reference) where a reference inside the document is `#DE.AE-06` - resolves only by lenient parsing. REPORTED upstream.
- **91 of 219 controls are withdrawn tombstones** (12 categories, 79 subcategories) - the catalog carries its 1.1-restructuring residue in-band; the successor graph (`replaces[]`) carries the migration map of every withdrawn item that names a successor.
- Declarative corpus #6: unspecified x106 of 106 - CSF states outcomes; obligation is an adoption artifact (baseline Sets in profiles), exactly the ISM/CIS/CyFun/C5 pattern.
- **Conversion ledger (measured per source value; backlog #41)**: each of the 4,726 source leaf values was followed into the written bundle. **1,599 copied** (the value stands, with its type, at the destination named, read back from the written file), **818 transformed** (one of 9 named rules made the destination from it; the rule was applied to the source again and compared), **1,317 intentionally dropped** (a declared reason), **992 unaccounted** (no destination and no declared reason). Checks that failed: 0. The path map below reads 4,726 of 4,726 for the same conversion: it counts paths with a declared destination, the ledger counts values that arrived. The record is `csf-conversion-ledger.json`: one row per source path and outcome, with its count, an example and the destinations or the reasons. The entry of each single value is not committed; every row is a count over entries that were checked in the run that wrote it.
- **Declared drops, two kinds** (the reasons and their counts are listed near the end of this report). (a) **641** stated by the converter's own path map: a withdrawn item is not emitted, and of it the bundle carries the lineage on its successor - id, label, title, statement prose and links. Dropped with it: its class x91; its sort-id (a withdrawn item is a member of no Set; among live siblings its place stays empty in their sequence) x91; its status, where no link names a successor x4; the id of its statement part x91; the name of its statement part x91; the name of one of its props x273. (b) **676** in the classes decided for the IFA corpus on 2026-11-13: uuids of the source document x7; revision history x7; directory of parties and roles x28; back-matter resources x3; type tags, the class of an element x134; type tags, the name of a part x497. Nothing else is declared: a value without a destination that is in neither kind is unaccounted and listed by path at the end of this report.
- **What the ledger cannot see**: it follows source values into the bundle, not the other way. Counted the other way for this run: of the 3,271 leaf values of the 135 objects, 2,788 are a source value or made from one by a rule; the other 483 are written by the converter with no source value behind them: `/id` x1, `/lifecycle` x135, `/statements/[]/modality` x106, `/statements/[]/obligated-parties/[]` x106, `/version` x135 (the version `2.0`, the lifecycle `active`, the modality `unspecified`, the obligated party `https://ns.nist.gov/csf/party/organization` and the id of the root Set). The namespace `https://ns.nist.gov/csf` in every minted URI, the facet names and the manifest's own fields (`source-version`, `converter`, `namespace-note`, the digests) are the converter's as well.
- **A second risk-party is not carried x22** (found by the ledger; a loss, not fixed here because the fix changes the bundle): the converter reads the first `risk-party` prop of an item, and csf@1 holds one value. Where a subcategory carries two (in the CSF: `1st` and `3rd`), the second value and its remark reach no object. The ledger lists them as unaccounted under `...props[].value` and `...props[].remarks`.
- **Withdrawn without a successor x4** (found by the ledger): no `incorporated_into` or `moved_to` link names a successor in the catalogue for PR.IP, PR.PT, DE.DP, RS.RP, so there is no object to write the lineage on. Nothing of such an item reaches the bundle: its id, title, label and, where it has one, its statement prose are unaccounted. Every other withdrawn item has an entry on at least one successor.
- **Sort-id shared by siblings x1** (source finding): ID.IM-03 and ID.IM-04 both carry `00002.00007.00003`. The sort is stable, so they keep the order of the document; the rule for the member sequence says so.

## Full path map (every source path, its count, its destination)

| path | count | level | destination |
|---|---:|---|---|
| `csf.catalog.back-matter.resources[].rlinks[].href` | 4 | L1 | references@1 facet on the root Set (title; the address of the first link as url) |
| `csf.catalog.back-matter.resources[].rlinks[].media-type` | 3 | L1 | not carried: the uuid of a resource and the media type of its link (declared drops in the ledger) |
| `csf.catalog.back-matter.resources[].title` | 4 | L1 | references@1 facet on the root Set (title; the address of the first link as url) |
| `csf.catalog.back-matter.resources[].uuid` | 4 | L1 | not carried: the uuid of a resource and the media type of its link (declared drops in the ledger) |
| `csf.catalog.groups[].class` | 6 | L1 | not carried: `function` is a type tag, the Set says it by its URI (declared drop in the ledger) |
| `csf.catalog.groups[].controls[].class` | 219 | L1 | not carried: `category` / `subcategory` is a type tag, the object says it by its type and URI (declared drop in the ledger) |
| `csf.catalog.groups[].controls[].id` | 219 | L1 | category Set / subcategory Requirement id (URI mint); withdrawn: dropped, lineage inverted - the id is the `ref` of the entry in the replaces[] and the nist-withdrawal annotation of each successor, and where no link gives a successor nothing of the item is carried |
| `csf.catalog.groups[].controls[].links[].href` | 135 | L1 | names the successor: the entry stands on the Requirement or Set with that id, and its `ref` is written by a rule that holds only if the address names that object |
| `csf.catalog.groups[].controls[].links[].rel` | 135 | L1 | incorporated_into/moved_to (UNDERSCORE spelling - source finding) -> `mode` (merged-into/renamed) of the entry in the successor's replaces[] + nist-withdrawal annotation |
| `csf.catalog.groups[].controls[].parts[].id` | 582 | L1 | subcategory statement id -> statements[0].id, without the control prefix; example id -> examples@1; not carried: the id of a category's statement part (unaccounted in the ledger) and of a withdrawn item's (declared drop) |
| `csf.catalog.groups[].controls[].parts[].name` | 582 | L1 | not carried: `statement` / `example` is a type tag of the part, the bundle says it by where the prose stands (declared drop in the ledger) |
| `csf.catalog.groups[].controls[].parts[].ns` | 363 | L1 | not carried: the namespace of the `example` part name; unaccounted in the ledger |
| `csf.catalog.groups[].controls[].parts[].prose` | 570 | L1 | subcategory statement -> statements[0] (modality unspecified); category statement -> narrative@1 on the Set; example parts -> examples@1 (language-tagged); withdrawn: statement prose -> `prose` in the nist-withdrawal annotation of each successor |
| `csf.catalog.groups[].controls[].props[].name` | 654 | L1 | not carried: the name selects the prop (`label`, `sort-id`, `risk-party`, `status`); unaccounted in the ledger, on a withdrawn item a declared drop |
| `csf.catalog.groups[].controls[].props[].ns` | 125 | L1 | not carried: the namespace of the `risk-party` prop name; unaccounted in the ledger |
| `csf.catalog.groups[].controls[].props[].remarks` | 125 | L2 | risk-party remark -> csf@1 (carried verbatim), of the FIRST risk-party prop only; the remark of a second one is not carried |
| `csf.catalog.groups[].controls[].props[].value` | 654 | L1 | label->label (withdrawn: `label` in the successor's annotation); sort-id->Set sequence (withdrawn: not carried); risk-party->csf@1, the FIRST risk-party prop of a subcategory only - a second one is not carried; status->tombstone drop + successor replaces[] (a withdrawn item is not emitted, its links become entries on its successors) |
| `csf.catalog.groups[].controls[].title` | 219 | L1 | category Set / subcategory Requirement title; withdrawn: dropped, lineage inverted - the title stands in the nist-withdrawal annotation of each successor, and nowhere where no link gives a successor |
| `csf.catalog.groups[].id` | 6 | L1 | function Set id (URI mint) |
| `csf.catalog.groups[].parts[].id` | 6 | L2 | not carried: the id of the overview part; unaccounted in the ledger |
| `csf.catalog.groups[].parts[].name` | 6 | L2 | not carried: `overview` is a type tag of the part (declared drop in the ledger) |
| `csf.catalog.groups[].parts[].prose` | 6 | L2 | function overview -> narrative@1 guidance on the function Set (language-tagged) |
| `csf.catalog.groups[].props[].name` | 12 | L1 | not carried: the name selects the prop (`label`, `sort-id`); unaccounted in the ledger |
| `csf.catalog.groups[].props[].value` | 12 | L1 | label -> function Set label; sort-id -> the sequence of the function in the root Set |
| `csf.catalog.groups[].title` | 6 | L1 | function Set title |
| `csf.catalog.metadata.last-modified` | 1 | L1 | not carried and not decided (unaccounted in the ledger): `last-modified`, the props of the document, its links to the back-matter resources, and who is its publisher, contact and author |
| `csf.catalog.metadata.links[].href` | 3 | L1 | not carried and not decided (unaccounted in the ledger): `last-modified`, the props of the document, its links to the back-matter resources, and who is its publisher, contact and author |
| `csf.catalog.metadata.links[].rel` | 3 | L1 | not carried and not decided (unaccounted in the ledger): `last-modified`, the props of the document, its links to the back-matter resources, and who is its publisher, contact and author |
| `csf.catalog.metadata.oscal-version` | 1 | L1 | bundle manifest provenance (`source`, `source-doc-version`, `source-oscal-version`, `published`); the title is the title of the root Set as well |
| `csf.catalog.metadata.parties[].addresses[].addr-lines[]` | 8 | L1 | not carried: the source's directory of parties and roles (declared drop in the ledger) |
| `csf.catalog.metadata.parties[].addresses[].city` | 2 | L1 | not carried: the source's directory of parties and roles (declared drop in the ledger) |
| `csf.catalog.metadata.parties[].addresses[].postal-code` | 2 | L1 | not carried: the source's directory of parties and roles (declared drop in the ledger) |
| `csf.catalog.metadata.parties[].addresses[].state` | 2 | L1 | not carried: the source's directory of parties and roles (declared drop in the ledger) |
| `csf.catalog.metadata.parties[].email-addresses[]` | 2 | L1 | not carried: the source's directory of parties and roles (declared drop in the ledger) |
| `csf.catalog.metadata.parties[].name` | 2 | L1 | not carried: the source's directory of parties and roles (declared drop in the ledger) |
| `csf.catalog.metadata.parties[].short-name` | 2 | L1 | not carried: the source's directory of parties and roles (declared drop in the ledger) |
| `csf.catalog.metadata.parties[].type` | 2 | L1 | not carried: the source's directory of parties and roles (declared drop in the ledger) |
| `csf.catalog.metadata.parties[].uuid` | 2 | L1 | not carried: the source's directory of parties and roles (declared drop in the ledger) |
| `csf.catalog.metadata.props[].name` | 5 | L1 | not carried and not decided (unaccounted in the ledger): `last-modified`, the props of the document, its links to the back-matter resources, and who is its publisher, contact and author |
| `csf.catalog.metadata.props[].ns` | 4 | L1 | not carried and not decided (unaccounted in the ledger): `last-modified`, the props of the document, its links to the back-matter resources, and who is its publisher, contact and author |
| `csf.catalog.metadata.props[].value` | 5 | L1 | not carried and not decided (unaccounted in the ledger): `last-modified`, the props of the document, its links to the back-matter resources, and who is its publisher, contact and author |
| `csf.catalog.metadata.published` | 1 | L1 | bundle manifest provenance (`source`, `source-doc-version`, `source-oscal-version`, `published`); the title is the title of the root Set as well |
| `csf.catalog.metadata.responsible-parties[].party-uuids[]` | 3 | L1 | not carried and not decided (unaccounted in the ledger): `last-modified`, the props of the document, its links to the back-matter resources, and who is its publisher, contact and author |
| `csf.catalog.metadata.responsible-parties[].role-id` | 3 | L1 | not carried and not decided (unaccounted in the ledger): `last-modified`, the props of the document, its links to the back-matter resources, and who is its publisher, contact and author |
| `csf.catalog.metadata.revisions[].last-modified` | 1 | L1 | not carried: revision history of the source document (declared drop in the ledger) |
| `csf.catalog.metadata.revisions[].links[].href` | 1 | L1 | not carried: revision history of the source document (declared drop in the ledger) |
| `csf.catalog.metadata.revisions[].links[].rel` | 1 | L1 | not carried: revision history of the source document (declared drop in the ledger) |
| `csf.catalog.metadata.revisions[].oscal-version` | 1 | L1 | not carried: revision history of the source document (declared drop in the ledger) |
| `csf.catalog.metadata.revisions[].remarks` | 1 | L1 | not carried: revision history of the source document (declared drop in the ledger) |
| `csf.catalog.metadata.revisions[].title` | 1 | L1 | not carried: revision history of the source document (declared drop in the ledger) |
| `csf.catalog.metadata.revisions[].version` | 1 | L1 | not carried: revision history of the source document (declared drop in the ledger) |
| `csf.catalog.metadata.roles[].id` | 3 | L1 | not carried: the source's directory of parties and roles (declared drop in the ledger) |
| `csf.catalog.metadata.roles[].title` | 3 | L1 | not carried: the source's directory of parties and roles (declared drop in the ledger) |
| `csf.catalog.metadata.title` | 1 | L1 | bundle manifest provenance (`source`, `source-doc-version`, `source-oscal-version`, `published`); the title is the title of the root Set as well |
| `csf.catalog.metadata.version` | 1 | L1 | bundle manifest provenance (`source`, `source-doc-version`, `source-oscal-version`, `published`); the title is the title of the root Set as well |
| `csf.catalog.uuid` | 1 | L1 | not carried: the uuid of the source document (declared drop in the ledger) |

## UNMAPPED (gate target: zero)

*(none)*

## Declared drops (conversion ledger)

No destination, and a declared reason. (a) is stated by the converter's own path map: a withdrawn item is not emitted; the bundle carries its lineage on its successor (id, label, title, statement prose, links) and drops the rest of it. (b) is a class the author decided for the IFA corpus on 2026-11-13. The reason of every row, in full, is in `csf-conversion-ledger.json`.

| kind | what is dropped, and why | count |
|---|---|---:|
| (a) | of a withdrawn item: its class | 91 |
| (a) | of a withdrawn item: its sort-id (a withdrawn item is a member of no Set; among live siblings its place stays empty in their sequence) | 91 |
| (a) | of a withdrawn item: its status, where no link names a successor | 4 |
| (a) | of a withdrawn item: the id of its statement part | 91 |
| (a) | of a withdrawn item: the name of its statement part | 91 |
| (a) | of a withdrawn item: the name of one of its props | 273 |
| (b) | the uuid of a source element identifies it inside the source document only; JASCON objects get URIs minted from the ids of the source, and the uuid itself is not carried | 7 |
| (b) | revision history of the source document: bookkeeping of the source, not content of the framework | 7 |
| (b) | the source's directory of parties and roles: a party is a landmark URI and there is no party object (register, backlog #16); the bundle names none of these parties | 28 |
| (b) | a back-matter resource is a link to another rendition of the source; its title and address are carried in references@1, the media type of the link is not | 3 |
| (b) | a type tag of a structural element, the class of a function, category or subcategory: the bundle says by its shape (the type of the object and its URI) what kind of thing the element is | 134 |
| (b) | a type tag of a structural element, the name of a part (statement, example, overview): the bundle says by its shape (where the prose stands) what kind of part it was | 497 |

## Unaccounted source values (conversion ledger)

No destination and no declared reason. Each is either a value the converter loses, or one it leaves out without a decision. The count of every path and outcome is in `csf-conversion-ledger.json`.

| path | count | first value |
|---|---:|---|
| `csf.catalog.groups[].controls[].controls[].parts[].ns` | 363 | `csf#/catalog/groups/0/controls/0/controls/0/parts/1/ns` |
| `csf.catalog.groups[].controls[].controls[].props[].name` | 337 | `csf#/catalog/groups/0/controls/0/controls/0/props/0/name` |
| `csf.catalog.groups[].controls[].controls[].props[].ns` | 125 | `csf#/catalog/groups/0/controls/0/controls/0/props/0/ns` |
| `csf.catalog.groups[].controls[].controls[].props[].remarks` | 22 | `csf#/catalog/groups/0/controls/0/controls/1/props/1/remarks` |
| `csf.catalog.groups[].controls[].controls[].props[].value` | 22 | `csf#/catalog/groups/0/controls/0/controls/1/props/1/value` |
| `csf.catalog.groups[].controls[].id` | 4 | `csf#/catalog/groups/2/controls/4/id` |
| `csf.catalog.groups[].controls[].parts[].id` | 22 | `csf#/catalog/groups/0/controls/0/parts/0/id` |
| `csf.catalog.groups[].controls[].props[].name` | 44 | `csf#/catalog/groups/0/controls/0/props/0/name` |
| `csf.catalog.groups[].controls[].props[].value` | 4 | `csf#/catalog/groups/2/controls/4/props/1/value` |
| `csf.catalog.groups[].controls[].title` | 4 | `csf#/catalog/groups/2/controls/4/title` |
| `csf.catalog.groups[].parts[].id` | 6 | `csf#/catalog/groups/0/parts/0/id` |
| `csf.catalog.groups[].props[].name` | 12 | `csf#/catalog/groups/0/props/0/name` |
| `csf.catalog.metadata.last-modified` | 1 | `csf#/catalog/metadata/last-modified` |
| `csf.catalog.metadata.links[].href` | 3 | `csf#/catalog/metadata/links/0/href` |
| `csf.catalog.metadata.links[].rel` | 3 | `csf#/catalog/metadata/links/0/rel` |
| `csf.catalog.metadata.props[].name` | 5 | `csf#/catalog/metadata/props/0/name` |
| `csf.catalog.metadata.props[].ns` | 4 | `csf#/catalog/metadata/props/0/ns` |
| `csf.catalog.metadata.props[].value` | 5 | `csf#/catalog/metadata/props/0/value` |
| `csf.catalog.metadata.responsible-parties[].party-uuids[]` | 3 | `csf#/catalog/metadata/responsible-parties/0/party-uuids/0` |
| `csf.catalog.metadata.responsible-parties[].role-id` | 3 | `csf#/catalog/metadata/responsible-parties/0/role-id` |
