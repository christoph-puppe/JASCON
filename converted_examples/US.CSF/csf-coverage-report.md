# NIST CSF 2.0 -> Semantic Core: Coverage Report (computed)

Source: **Electronic Version of NIST Cybersecurity Framework 2.0** framework v2.0 (OSCAL rendition 1.2.0, OSCAL v1.2.2). Census: `drafts/gate-3-census.md` §3/§6.

## Totals

- Source leaf values inventoried: **4,726**
- Mapped (declared destination): **4,726**
- **UNMAPPED: 0**  ->  coverage **100.0 %**
- Objects emitted: **106 Requirements** (subcategories), **33 Sets** (6 functions + 26 categories, 4 of them with lifecycle `withdrawn`, + root), manifest with both digests.

## Conversion rules (declared, counted)

- **Functions and categories are Sets, subcategories are Requirements** - the C5 rule (membership decides granularity), D21 taxonomy nesting at 3 levels.
- **Category statement prose -> narrative@1 on the category Set** - summary prose, not an obligation; the requirement surface is the subcategory layer.
- **Modality `unspecified` x106**: CSF outcomes are declarative ('Outcomes ... are understood and communicated') - sixth-corpus confirmation of the national declarative pattern; force rides adoption, not mood.
- **Withdrawn items: lineage inverted, or an object with lifecycle `withdrawn`**: 91 withdrawn (12 categories + 79 subcategories - the 1.1->2.0 restructuring cut at BOTH levels). 87 name a successor and are no objects: 134 successor edges on Requirements/Sets + 1 on function Sets (ID.GV, incorporated into the function GV - the sa-12->SR pattern) (incorporated_into->merged-into, moved_to->renamed); tombstone 1.1 outcome prose carried in the annotation (CSF titles are bare ids - the prose IS the content). 4 name none and are objects with lifecycle `withdrawn`, members of the Set of their parent (4 category Sets: PR.IP, PR.PT, DE.DP, RS.RP; 0 Requirements). Chains x0, dangling x0; no live subcategory sits under a withdrawn category that is no object (asserted).
- **Implementation examples -> examples@1** x363 (ids kept - the CSF example numbering is citable); **risk-party -> csf@1** x125 values on x103 items (remarks carried; an item that is a risk of the first and of the third party carries both, as a list).
- **Obligated party**: `https://ns.nist.gov/csf/party/organization` on every statement. This is the converter's default and not a value of the source; `--obligated-party URI` writes another. Why this default: CSF binds the adopting organization.
- **Payload free text language-tagged**: category-statement x22, example x363, overview x6.

## Findings (computed)

- **Rel-code spelling divergence (source finding)**: CSF 2.0 uses `incorporated_into`/`moved_to` (underscores) where SP 800-53 Rev 5 uses `incorporated-into`/`moved-to` (hyphens) - same publisher, same semantic, two spellings. REPORTED upstream.
- **Fragment marker missing x135** (source finding): none of the 135 successor addresses of this rendition carries the fragment marker - DE.DP-04's is `DE.AE-06` (a relative URI reference) where a reference inside the document is `#DE.AE-06` - resolves only by lenient parsing. REPORTED upstream.
- **91 of 219 controls are withdrawn** (12 categories, 79 subcategories) - the catalog carries its 1.1-restructuring residue in-band; the successor graph (`replaces[]`) carries the migration map of every withdrawn item that names a successor.
- Declarative corpus #6: unspecified x106 of 106 - CSF states outcomes; obligation is an adoption artifact (baseline Sets in profiles), exactly the ISM/CIS/CyFun/C5 pattern.
- **Conversion ledger (measured per source value; backlog #41)**: each of the 4,726 source leaf values was followed into the written bundle. **1,844 copied** (the value stands, with its type, at the destination named, read back from the written file), **826 transformed** (one of 9 named rules made the destination from it; the rule was applied to the source again and compared), **1,874 no content** (a name that only selects a field, a namespace, an id that another value gives exactly - each by a rule the ledger checked on the value; the rules are listed near the end of this report), **182 dropped for a reason the first ledger declared** (not decided: listed near the end of this report with what this converter makes of each), **0 unaccounted**. Checks that failed: 0. The path map below reads 4,726 of 4,726 for the same conversion: it counts paths with a declared destination, the ledger counts values. The record is `csf-conversion-ledger.json`: one row per source path and outcome, with its count, an example and the destinations, the rules or the reasons. A run with an unaccounted value or a failed check ends with a non-zero exit.
- **What the kernel and the standard facets have no place for** (carried all the same, in a facet this converter pins): the document metadata beyond title, version, OSCAL version and date of publication - `https://ns.jascon.net/compat/oscal-1x@1`, member `metadata`, on the root Set; the first-party / third-party class of a subcategory (`risk-party`, x125) and its remark - csf@1; the examples of a subcategory - examples@1; what this mapping does not know of an element - `https://ns.jascon.net/compat/oscal-1x@1`, member `unmapped`, on x0 objects of this run.
- **What the ledger cannot see**: it follows source values into the bundle, not the other way. Counted the other way for this run: of the 3,407 leaf values of the 139 objects, 2,920 are a source value or made from one by a rule; the other 487 are written by the converter with no source value behind them: `/id` x1, `/lifecycle` x135, `/statements/[]/modality` x106, `/statements/[]/obligated-parties/[]` x106, `/version` x139 (the version `2.0`; the lifecycle `active` of every item that carries no status prop - the source states none for it; the modality `unspecified`; the obligated party `https://ns.nist.gov/csf/party/organization`; the id of the root Set). The namespace `https://ns.nist.gov/csf` in every minted URI, the facet names and the manifest's own fields (`source-version`, `converter`, `namespace-note`, the digests) are the converter's as well.
- **The document and one of its resources share a uuid x1** (source finding): `catalog.uuid` is `720a010b-253c-4a94-bb65-cb58400966f5`, and so is the uuid of the back-matter resource `NIST CSF v2.0 content in OSCAL 1.1.3`. A link that names this uuid names both.
- **Sort-id shared by siblings x1** (source finding): ID.IM-03 and ID.IM-04 both carry `00002.00007.00003`. The sort is stable, so they keep the order of the document; the rule for the member sequence says so.

## Full path map (every source path, its count, its destination)

| path | count | level | destination |
|---|---:|---|---|
| `csf.catalog.back-matter.resources[].rlinks[].href` | 4 | L1 | references@1 facet on the root Set (title; the address of the first link as url) [ledger: 4 copied] |
| `csf.catalog.back-matter.resources[].rlinks[].media-type` | 3 | L1 | declared drops, not decided: the uuid of a resource and the media type of its link [ledger: 3 dropped] |
| `csf.catalog.back-matter.resources[].title` | 4 | L1 | references@1 facet on the root Set (title; the address of the first link as url) [ledger: 4 copied] |
| `csf.catalog.back-matter.resources[].uuid` | 4 | L1 | declared drops, not decided: the uuid of a resource and the media type of its link [ledger: 4 dropped] |
| `csf.catalog.groups[].class` | 6 | L1 | no content: `function` says on which level the element stands, and the Set says it by its URI (a rule the ledger checks); what the mapping does not know is carried as it is in the compat facet (`unmapped`) [ledger: 6 no content] |
| `csf.catalog.groups[].controls[].class` | 219 | L1 | no content: `category` / `subcategory` says on which level the element stands, and the object says it by its type and URI (a rule the ledger checks); what the mapping does not know is carried as it is in the compat facet (`unmapped`) [ledger: 219 no content] |
| `csf.catalog.groups[].controls[].id` | 219 | L1 | category Set / subcategory Requirement id (URI mint); withdrawn with a successor: the `ref` of the entry in the replaces[] and the nist-withdrawal annotation of each successor; withdrawn without one: the id of a Set or Requirement with lifecycle `withdrawn` [ledger: 219 transformed] |
| `csf.catalog.groups[].controls[].links[].href` | 135 | L1 | names the successor: the entry stands on the Requirement or Set with that id, and its `ref` is written by a rule that holds only if the address names that object; what the mapping does not know is carried as it is in the compat facet (`unmapped`) [ledger: 135 transformed] |
| `csf.catalog.groups[].controls[].links[].rel` | 135 | L1 | incorporated_into/moved_to (UNDERSCORE spelling - source finding) -> `mode` (merged-into/renamed) of the entry in the successor's replaces[] + nist-withdrawal annotation; what the mapping does not know is carried as it is in the compat facet (`unmapped`) [ledger: 135 transformed] |
| `csf.catalog.groups[].controls[].parts[].id` | 582 | L1 | subcategory statement id -> statements[0].id, without the control prefix; example id -> examples@1; the id of a category's statement part and of the statement part of a withdrawn item with a successor: no content, rebuilt exactly, the id of the item and `_statement` (a rule the ledger checks); what the mapping does not know is carried as it is in the compat facet (`unmapped`) [ledger: 363 copied, 106 transformed, 113 no content] |
| `csf.catalog.groups[].controls[].parts[].name` | 582 | L1 | no content: `statement` / `example` selects the member the prose is written to (a rule the ledger checks); what the mapping does not know is carried as it is in the compat facet (`unmapped`) [ledger: 582 no content] |
| `csf.catalog.groups[].controls[].parts[].ns` | 363 | L1 | no content: the CSF's own namespace of the `example` part name (a rule the ledger checks); what the mapping does not know is carried as it is in the compat facet (`unmapped`) [ledger: 363 no content] |
| `csf.catalog.groups[].controls[].parts[].prose` | 570 | L1 | subcategory statement -> statements[0] (modality unspecified); category statement -> narrative@1 on the Set; example parts -> examples@1 (language-tagged); withdrawn with a successor: statement prose -> `prose` in the nist-withdrawal annotation of each successor; what the mapping does not know is carried as it is in the compat facet (`unmapped`) [ledger: 570 copied] |
| `csf.catalog.groups[].controls[].props[].name` | 654 | L1 | risk-party: the key under which csf@1 holds the value; label, sort-id, status: no content, the name selects the field its value is written to (a rule the ledger checks); the name of a sort-id that is dropped is dropped with it; what the mapping does not know is carried as it is in the compat facet (`unmapped`) [ledger: 125 copied, 442 no content, 87 dropped] |
| `csf.catalog.groups[].controls[].props[].ns` | 125 | L1 | no content: the CSF's own namespace of the `risk-party` prop name (a rule the ledger checks); what the mapping does not know is carried as it is in the compat facet (`unmapped`) [ledger: 125 no content] |
| `csf.catalog.groups[].controls[].props[].remarks` | 125 | L2 | risk-party remark -> csf@1 (carried verbatim), one for every value; what the mapping does not know is carried as it is in the compat facet (`unmapped`) [ledger: 125 copied] |
| `csf.catalog.groups[].controls[].props[].value` | 654 | L1 | label->label (withdrawn with a successor: `label` in the successor's annotation); sort-id->Set sequence (withdrawn with a successor: a declared drop, not decided); risk-party->csf@1, every value, a list where an item has two; status `withdrawn`->lifecycle `withdrawn` of the object, and for an item with a successor an input of the rule that writes its entry on the successor; what the mapping does not know is carried as it is in the compat facet (`unmapped`) [ledger: 348 copied, 219 transformed, 87 dropped] |
| `csf.catalog.groups[].controls[].title` | 219 | L1 | category Set / subcategory Requirement title; withdrawn with a successor: `title` in the nist-withdrawal annotation of each successor [ledger: 219 copied] |
| `csf.catalog.groups[].id` | 6 | L1 | function Set id (URI mint) [ledger: 6 transformed] |
| `csf.catalog.groups[].parts[].id` | 6 | L2 | no content: rebuilt exactly, the id of the function and `_overview` (a rule the ledger checks); what the mapping does not know is carried as it is in the compat facet (`unmapped`) [ledger: 6 no content] |
| `csf.catalog.groups[].parts[].name` | 6 | L2 | no content: `overview` selects the member its prose is written to (a rule the ledger checks); what the mapping does not know is carried as it is in the compat facet (`unmapped`) [ledger: 6 no content] |
| `csf.catalog.groups[].parts[].prose` | 6 | L2 | function overview -> narrative@1 guidance on the function Set (language-tagged); what the mapping does not know is carried as it is in the compat facet (`unmapped`) [ledger: 6 copied] |
| `csf.catalog.groups[].props[].name` | 12 | L1 | no content: the name selects the field its value is written to (`label`, `sort-id`; a rule the ledger checks); what the mapping does not know is carried as it is in the compat facet (`unmapped`) [ledger: 12 no content] |
| `csf.catalog.groups[].props[].value` | 12 | L1 | label -> function Set label; sort-id -> the sequence of the function in the root Set; what the mapping does not know is carried as it is in the compat facet (`unmapped`) [ledger: 6 copied, 6 transformed] |
| `csf.catalog.groups[].title` | 6 | L1 | function Set title [ledger: 6 copied] |
| `csf.catalog.metadata.last-modified` | 1 | L2 | compat facet on the root Set, member `metadata`, in the source's own shape and with its own values (`last-modified`, revisions, props, links, roles, parties, responsible-parties) [ledger: 1 copied] |
| `csf.catalog.metadata.links[].href` | 3 | L2 | compat facet on the root Set, member `metadata`, in the source's own shape and with its own values (`last-modified`, revisions, props, links, roles, parties, responsible-parties) [ledger: 3 copied] |
| `csf.catalog.metadata.links[].rel` | 3 | L2 | compat facet on the root Set, member `metadata`, in the source's own shape and with its own values (`last-modified`, revisions, props, links, roles, parties, responsible-parties) [ledger: 3 copied] |
| `csf.catalog.metadata.oscal-version` | 1 | L1 | bundle manifest provenance (`source`, `source-doc-version`, `source-oscal-version`, `published`); the title is the title of the root Set as well [ledger: 1 copied] |
| `csf.catalog.metadata.parties[].addresses[].addr-lines[]` | 8 | L2 | compat facet on the root Set, member `metadata`, in the source's own shape and with its own values (`last-modified`, revisions, props, links, roles, parties, responsible-parties) [ledger: 8 copied] |
| `csf.catalog.metadata.parties[].addresses[].city` | 2 | L2 | compat facet on the root Set, member `metadata`, in the source's own shape and with its own values (`last-modified`, revisions, props, links, roles, parties, responsible-parties) [ledger: 2 copied] |
| `csf.catalog.metadata.parties[].addresses[].postal-code` | 2 | L2 | compat facet on the root Set, member `metadata`, in the source's own shape and with its own values (`last-modified`, revisions, props, links, roles, parties, responsible-parties) [ledger: 2 copied] |
| `csf.catalog.metadata.parties[].addresses[].state` | 2 | L2 | compat facet on the root Set, member `metadata`, in the source's own shape and with its own values (`last-modified`, revisions, props, links, roles, parties, responsible-parties) [ledger: 2 copied] |
| `csf.catalog.metadata.parties[].email-addresses[]` | 2 | L2 | compat facet on the root Set, member `metadata`, in the source's own shape and with its own values (`last-modified`, revisions, props, links, roles, parties, responsible-parties) [ledger: 2 copied] |
| `csf.catalog.metadata.parties[].name` | 2 | L2 | compat facet on the root Set, member `metadata`, in the source's own shape and with its own values (`last-modified`, revisions, props, links, roles, parties, responsible-parties) [ledger: 2 copied] |
| `csf.catalog.metadata.parties[].short-name` | 2 | L2 | compat facet on the root Set, member `metadata`, in the source's own shape and with its own values (`last-modified`, revisions, props, links, roles, parties, responsible-parties) [ledger: 2 copied] |
| `csf.catalog.metadata.parties[].type` | 2 | L2 | compat facet on the root Set, member `metadata`, in the source's own shape and with its own values (`last-modified`, revisions, props, links, roles, parties, responsible-parties) [ledger: 2 copied] |
| `csf.catalog.metadata.parties[].uuid` | 2 | L2 | compat facet on the root Set, member `metadata`, in the source's own shape and with its own values (`last-modified`, revisions, props, links, roles, parties, responsible-parties) [ledger: 2 copied] |
| `csf.catalog.metadata.props[].name` | 5 | L2 | compat facet on the root Set, member `metadata`, in the source's own shape and with its own values (`last-modified`, revisions, props, links, roles, parties, responsible-parties) [ledger: 5 copied] |
| `csf.catalog.metadata.props[].ns` | 4 | L2 | compat facet on the root Set, member `metadata`, in the source's own shape and with its own values (`last-modified`, revisions, props, links, roles, parties, responsible-parties) [ledger: 4 copied] |
| `csf.catalog.metadata.props[].value` | 5 | L2 | compat facet on the root Set, member `metadata`, in the source's own shape and with its own values (`last-modified`, revisions, props, links, roles, parties, responsible-parties) [ledger: 5 copied] |
| `csf.catalog.metadata.published` | 1 | L1 | bundle manifest provenance (`source`, `source-doc-version`, `source-oscal-version`, `published`); the title is the title of the root Set as well [ledger: 1 copied] |
| `csf.catalog.metadata.responsible-parties[].party-uuids[]` | 3 | L2 | compat facet on the root Set, member `metadata`, in the source's own shape and with its own values (`last-modified`, revisions, props, links, roles, parties, responsible-parties) [ledger: 3 copied] |
| `csf.catalog.metadata.responsible-parties[].role-id` | 3 | L2 | compat facet on the root Set, member `metadata`, in the source's own shape and with its own values (`last-modified`, revisions, props, links, roles, parties, responsible-parties) [ledger: 3 copied] |
| `csf.catalog.metadata.revisions[].last-modified` | 1 | L2 | compat facet on the root Set, member `metadata`, in the source's own shape and with its own values (`last-modified`, revisions, props, links, roles, parties, responsible-parties) [ledger: 1 copied] |
| `csf.catalog.metadata.revisions[].links[].href` | 1 | L2 | compat facet on the root Set, member `metadata`, in the source's own shape and with its own values (`last-modified`, revisions, props, links, roles, parties, responsible-parties) [ledger: 1 copied] |
| `csf.catalog.metadata.revisions[].links[].rel` | 1 | L2 | compat facet on the root Set, member `metadata`, in the source's own shape and with its own values (`last-modified`, revisions, props, links, roles, parties, responsible-parties) [ledger: 1 copied] |
| `csf.catalog.metadata.revisions[].oscal-version` | 1 | L2 | compat facet on the root Set, member `metadata`, in the source's own shape and with its own values (`last-modified`, revisions, props, links, roles, parties, responsible-parties) [ledger: 1 copied] |
| `csf.catalog.metadata.revisions[].remarks` | 1 | L2 | compat facet on the root Set, member `metadata`, in the source's own shape and with its own values (`last-modified`, revisions, props, links, roles, parties, responsible-parties) [ledger: 1 copied] |
| `csf.catalog.metadata.revisions[].title` | 1 | L2 | compat facet on the root Set, member `metadata`, in the source's own shape and with its own values (`last-modified`, revisions, props, links, roles, parties, responsible-parties) [ledger: 1 copied] |
| `csf.catalog.metadata.revisions[].version` | 1 | L2 | compat facet on the root Set, member `metadata`, in the source's own shape and with its own values (`last-modified`, revisions, props, links, roles, parties, responsible-parties) [ledger: 1 copied] |
| `csf.catalog.metadata.roles[].id` | 3 | L2 | compat facet on the root Set, member `metadata`, in the source's own shape and with its own values (`last-modified`, revisions, props, links, roles, parties, responsible-parties) [ledger: 3 copied] |
| `csf.catalog.metadata.roles[].title` | 3 | L2 | compat facet on the root Set, member `metadata`, in the source's own shape and with its own values (`last-modified`, revisions, props, links, roles, parties, responsible-parties) [ledger: 3 copied] |
| `csf.catalog.metadata.title` | 1 | L1 | bundle manifest provenance (`source`, `source-doc-version`, `source-oscal-version`, `published`); the title is the title of the root Set as well [ledger: 1 copied] |
| `csf.catalog.metadata.version` | 1 | L1 | bundle manifest provenance (`source`, `source-doc-version`, `source-oscal-version`, `published`); the title is the title of the root Set as well [ledger: 1 copied] |
| `csf.catalog.uuid` | 1 | L1 | declared drop, not decided: the uuid of the source document [ledger: 1 dropped] |

## UNMAPPED (gate target: zero)

*(none)*

## What is no content (conversion ledger)

A name that only selects a field, a namespace, an id that another value gives exactly. Each rule was checked on every value it is stated for, and a value shares the fate of what it rests on.

| kind | rule | count |
|---|---|---:|
| namespace | the namespace of the CSF's own names `risk-party` and `example` (https://csrc.nist.gov/ns/csf) | 488 |
| rebuilt-id | the id of a statement part is the id of its item and `_statement` | 113 |
| rebuilt-id | the id of an overview part is the id of its function and `_overview` | 6 |
| selector | the class of an element says on which level it stands (function, category, subcategory); the level is what makes it a function Set, a category Set or a Requirement | 225 |
| selector | the name of a part selects the member its prose is written to (statement, example, overview) | 588 |
| selector | the name of a prop selects the field its value is written to (label, sort-id, status) | 454 |

## Declared drops that remain (conversion ledger)

Declared when the ledger was first wired, before the rule that content is never dropped, and not decided since. No drop was added. `reading` is what this converter makes of the value under the rule that content is never dropped; the decision is the author's.

| source path | count | declared reason | example | reading |
|---|---:|---|---|---|
| `csf.catalog.uuid` | 1 | as decided for IFA on 2026-11-13: the uuid of a source element identifies it inside the source document only; JASCON objects get URIs minted from the ids of the source, and the uuid itself is not carried | `720a010b-253c-4a94-bb65-cb58400966f5` | content: it identifies the source document, and nothing in the bundle lets a reader rebuild it |
| `csf.catalog.groups[].controls[].props[].name` | 87 | the name of a prop selects the field its value is written to (label, sort-id, status) - of a value that is dropped: a withdrawn item that names a successor is not emitted; the bundle carries its lineage on the successor - id, label, title, statement prose and each link. Its sort-id, the place among its siblings, is none of those: a withdrawn item of this kind is a member of no Set | `sort-id` | not content, because the name `sort-id` only selects the value beside it; it shares the fate of that value |
| `csf.catalog.groups[].controls[].props[].value` | 87 | a withdrawn item that names a successor is not emitted; the bundle carries its lineage on the successor - id, label, title, statement prose and each link. Its sort-id, the place among its siblings, is none of those: a withdrawn item of this kind is a member of no Set | `00002.00001.00006` | content: the order of the withdrawn items among their siblings. Where the siblings are members of a Set the place stays empty in their sequence; of a withdrawn item under a withdrawn category nothing in the bundle shows it |
| `csf.catalog.back-matter.resources[].uuid` | 4 | as decided for IFA on 2026-11-13: the uuid of a source element identifies it inside the source document only; JASCON objects get URIs minted from the ids of the source, and the uuid itself is not carried | `3ab41d8a-66e3-4732-ae28-07405dad5127` | content: the links of the document metadata, carried in the compat facet, name a resource by this uuid; without it a reader cannot tell which resource is the canonical and which an alternate one |
| `csf.catalog.back-matter.resources[].rlinks[].media-type` | 3 | as decided for IFA on 2026-11-13: a back-matter resource is a link to another rendition of the source; its title and address are carried in references@1, the media type of the link is not | `application/pdf` | content: it says what the address leads to (a PDF, a web page) |

## Unaccounted source values (conversion ledger)

No destination, no rule and no declared reason. A run that lists a value here ends with a non-zero exit.

*(none)*
