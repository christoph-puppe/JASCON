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
- **Withdrawn tombstones dropped, lineage inverted**: 91 withdrawn (12 categories + 79 subcategories - the 1.1->2.0 restructuring cut at BOTH levels), 134 successor edges on Requirements/Sets + 1 on function Sets (ID.GV 'moved to GV' - the sa-12->SR pattern) (incorporated_into->merged-into, moved_to->renamed); tombstone 1.1 outcome prose carried in the annotation (CSF titles are bare ids - the prose IS the content); chains x0, dangling x0; no live subcategory sits under a withdrawn category (asserted).
- **Implementation examples -> examples@1** x363 (ids kept - the CSF example numbering is citable); **risk-party -> csf@1** x103 (remarks carried).
- **Obligated party**: `https://ns.nist.gov/csf/party/organization` on every statement. This is the converter's default and not a value of the source; `--obligated-party URI` writes another. Why this default: CSF binds the adopting organization.
- **Payload free text language-tagged**: category-statement x22, example x363, overview x6.

## Findings (computed)

- **Rel-code spelling divergence (source finding)**: CSF 2.0 uses `incorporated_into`/`moved_to` (underscores) where SP 800-53 Rev 5 uses `incorporated-into`/`moved-to` (hyphens) - same publisher, same semantic, two spellings. REPORTED upstream.
- **Fragment marker missing x135** (source finding): DE.DP-04's successor href is `DE.AE-06` (a relative URI reference) where every sibling writes `#DE.AE-06` - resolves only by lenient parsing. REPORTED upstream.
- **91 of 219 controls are withdrawn tombstones** (12 categories, 79 subcategories) - the catalog carries its 1.1-restructuring residue in-band; the successor graph (`replaces[]`) carries the full migration map.
- Declarative corpus #6: unspecified x106 of 106 - CSF states outcomes; obligation is an adoption artifact (baseline Sets in profiles), exactly the ISM/CIS/CyFun/C5 pattern.

## Full path map (every source path, its count, its destination)

| path | count | level | destination |
|---|---:|---|---|
| `csf.catalog.back-matter.resources[].rlinks[].href` | 4 | L1 | references@1 facet on the root Set (title/url) |
| `csf.catalog.back-matter.resources[].rlinks[].media-type` | 3 | L1 | references@1 facet on the root Set (title/url) |
| `csf.catalog.back-matter.resources[].title` | 4 | L1 | references@1 facet on the root Set (title/url) |
| `csf.catalog.back-matter.resources[].uuid` | 4 | L1 | references@1 facet on the root Set (title/url) |
| `csf.catalog.groups[].class` | 6 | L1 | function Set id/title |
| `csf.catalog.groups[].controls[].class` | 219 | L1 | category Set / subcategory Requirement id (URI mint) + title | withdrawn: dropped, lineage inverted |
| `csf.catalog.groups[].controls[].id` | 219 | L1 | category Set / subcategory Requirement id (URI mint) + title | withdrawn: dropped, lineage inverted |
| `csf.catalog.groups[].controls[].links[].href` | 135 | L1 | incorporated_into/moved_to (UNDERSCORE spelling - source finding) -> successor replaces[] (merged-into/renamed) + nist-withdrawal annotation |
| `csf.catalog.groups[].controls[].links[].rel` | 135 | L1 | incorporated_into/moved_to (UNDERSCORE spelling - source finding) -> successor replaces[] (merged-into/renamed) + nist-withdrawal annotation |
| `csf.catalog.groups[].controls[].parts[].id` | 582 | L1 | subcategory statement -> statements[0] (modality unspecified); category statement -> narrative@1 on the Set; example parts -> examples@1 (language-tagged) |
| `csf.catalog.groups[].controls[].parts[].name` | 582 | L1 | subcategory statement -> statements[0] (modality unspecified); category statement -> narrative@1 on the Set; example parts -> examples@1 (language-tagged) |
| `csf.catalog.groups[].controls[].parts[].ns` | 363 | L1 | subcategory statement -> statements[0] (modality unspecified); category statement -> narrative@1 on the Set; example parts -> examples@1 (language-tagged) |
| `csf.catalog.groups[].controls[].parts[].prose` | 570 | L1 | subcategory statement -> statements[0] (modality unspecified); category statement -> narrative@1 on the Set; example parts -> examples@1 (language-tagged) |
| `csf.catalog.groups[].controls[].props[].name` | 654 | L1 | label->label; sort-id->Set sequence; risk-party->csf@1; status->tombstone drop + successor replaces[] |
| `csf.catalog.groups[].controls[].props[].ns` | 125 | L1 | label->label; sort-id->Set sequence; risk-party->csf@1; status->tombstone drop + successor replaces[] |
| `csf.catalog.groups[].controls[].props[].remarks` | 125 | L2 | risk-party remark -> csf@1 (carried verbatim) |
| `csf.catalog.groups[].controls[].props[].value` | 654 | L1 | label->label; sort-id->Set sequence; risk-party->csf@1; status->tombstone drop + successor replaces[] |
| `csf.catalog.groups[].controls[].title` | 219 | L1 | category Set / subcategory Requirement id (URI mint) + title | withdrawn: dropped, lineage inverted |
| `csf.catalog.groups[].id` | 6 | L1 | function Set id/title |
| `csf.catalog.groups[].parts[].id` | 6 | L2 | function overview -> narrative@1 guidance on the function Set (language-tagged) |
| `csf.catalog.groups[].parts[].name` | 6 | L2 | function overview -> narrative@1 guidance on the function Set (language-tagged) |
| `csf.catalog.groups[].parts[].prose` | 6 | L2 | function overview -> narrative@1 guidance on the function Set (language-tagged) |
| `csf.catalog.groups[].props[].name` | 12 | L1 | function Set label; sort-id -> member order |
| `csf.catalog.groups[].props[].value` | 12 | L1 | function Set label; sort-id -> member order |
| `csf.catalog.groups[].title` | 6 | L1 | function Set id/title |
| `csf.catalog.metadata.last-modified` | 1 | L1 | bundle manifest / L0 provenance |
| `csf.catalog.metadata.links[].href` | 3 | L1 | bundle manifest / L0 provenance |
| `csf.catalog.metadata.links[].rel` | 3 | L1 | bundle manifest / L0 provenance |
| `csf.catalog.metadata.oscal-version` | 1 | L1 | bundle manifest / L0 provenance |
| `csf.catalog.metadata.parties[].addresses[].addr-lines[]` | 8 | L1 | bundle manifest / L0 provenance |
| `csf.catalog.metadata.parties[].addresses[].city` | 2 | L1 | bundle manifest / L0 provenance |
| `csf.catalog.metadata.parties[].addresses[].postal-code` | 2 | L1 | bundle manifest / L0 provenance |
| `csf.catalog.metadata.parties[].addresses[].state` | 2 | L1 | bundle manifest / L0 provenance |
| `csf.catalog.metadata.parties[].email-addresses[]` | 2 | L1 | bundle manifest / L0 provenance |
| `csf.catalog.metadata.parties[].name` | 2 | L1 | bundle manifest / L0 provenance |
| `csf.catalog.metadata.parties[].short-name` | 2 | L1 | bundle manifest / L0 provenance |
| `csf.catalog.metadata.parties[].type` | 2 | L1 | bundle manifest / L0 provenance |
| `csf.catalog.metadata.parties[].uuid` | 2 | L1 | bundle manifest / L0 provenance |
| `csf.catalog.metadata.props[].name` | 5 | L1 | bundle manifest / L0 provenance |
| `csf.catalog.metadata.props[].ns` | 4 | L1 | bundle manifest / L0 provenance |
| `csf.catalog.metadata.props[].value` | 5 | L1 | bundle manifest / L0 provenance |
| `csf.catalog.metadata.published` | 1 | L1 | bundle manifest / L0 provenance |
| `csf.catalog.metadata.responsible-parties[].party-uuids[]` | 3 | L1 | bundle manifest / L0 provenance |
| `csf.catalog.metadata.responsible-parties[].role-id` | 3 | L1 | bundle manifest / L0 provenance |
| `csf.catalog.metadata.revisions[].last-modified` | 1 | L1 | bundle manifest / L0 provenance |
| `csf.catalog.metadata.revisions[].links[].href` | 1 | L1 | bundle manifest / L0 provenance |
| `csf.catalog.metadata.revisions[].links[].rel` | 1 | L1 | bundle manifest / L0 provenance |
| `csf.catalog.metadata.revisions[].oscal-version` | 1 | L1 | bundle manifest / L0 provenance |
| `csf.catalog.metadata.revisions[].remarks` | 1 | L1 | bundle manifest / L0 provenance |
| `csf.catalog.metadata.revisions[].title` | 1 | L1 | bundle manifest / L0 provenance |
| `csf.catalog.metadata.revisions[].version` | 1 | L1 | bundle manifest / L0 provenance |
| `csf.catalog.metadata.roles[].id` | 3 | L1 | bundle manifest / L0 provenance |
| `csf.catalog.metadata.roles[].title` | 3 | L1 | bundle manifest / L0 provenance |
| `csf.catalog.metadata.title` | 1 | L1 | bundle manifest / L0 provenance |
| `csf.catalog.metadata.version` | 1 | L1 | bundle manifest / L0 provenance |
| `csf.catalog.uuid` | 1 | L1 | bundle manifest / L0 provenance |

## UNMAPPED (gate target: zero)

*(none)*
