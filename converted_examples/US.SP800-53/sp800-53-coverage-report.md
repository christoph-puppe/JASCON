# NIST SP 800-53 Rev 5 + 800-53B -> Semantic Core: Coverage Report (computed)

Source: **Electronic (OSCAL) Version of NIST SP 800-53 Rev 5.2.0 Controls and SP 800-53A Rev 5.2.0 Assessment Procedures** v5.2.0 (OSCAL 1.2.2) + four 800-53B baseline profiles. Census: `drafts/gate-3-census.md`.

## Totals

- Source leaf values inventoried: **115,680**
- Mapped (declared destination): **115,680**
- **UNMAPPED: 0**  ->  coverage **100.0 %**
- Objects emitted: **1014 Requirements** (324+872 minus 182 withdrawn tombstones), **25 Sets** (20 families + root + 4 baselines), manifest with both digests.
- Baseline membership: LOW 149, MODERATE 287, HIGH 370, PRIVACY 96.
- **Conversion ledger** (every source value followed into the written files): **31,274 copied**, **17,008 transformed** by a named rule, **20,043 dropped** for a declared reason, **47,355 unaccounted**; checks that failed: 0. The line `UNMAPPED` above counts source paths that have a row in the path map, and a row may say that the value is not carried. The ledger is the measure of what arrived; its sections are at the end of this report.

## Conversion rules (declared, counted)

- **Withdrawn tombstones dropped, lineage inverted (kernel `replaces[]`)**: 182 withdrawn; 199 successor edges on Requirements + 1 on family Sets (sa-12 'moved to SR' - the successor is a whole family; shared base makes Set-level `replaces` legal) (incorporated-into->merged-into, moved-to->renamed); statement-precision + withdrawn label/title in `annotations['nist-withdrawal']`; withdrawn->withdrawn chains x0, dangling x0. Withdrawn controls that name no successor: x2 (cp-10.3, sc-19) - nothing of them is in the bundle.
- **Modality corpus rule `must` x1918**: Rev 5 statements are uniformly imperative and obligation binds on baseline selection - the INVERSE of the declarative national pattern (ISM/CIS/CyFun/C5). Force in the mood, selection in the baseline Sets; both confirm D13's split axes.
- **Obligated party**: `https://ns.nist.gov/sp800-53/party/organization` on every statement for which the source names no party; where it names one (as the implementation level of a control), that one is written. `https://ns.nist.gov/sp800-53/party/organization` is the converter's default and not a value of the source; `--obligated-party URI` writes another. The source gives a level on x1014 controls (organization x613, system x250, organization + system x151), written as `https://ns.nist.gov/sp800-53/party/<level>` on their x1918 statements. It gives none on x0 controls; their x0 statements are the only ones that carry the converter's default.
- **Two-layer ODP params -> statement-scoped decls**: declared on each statement whose prose inserts them (per-statement parameter rule); choice x133, string else; legacy _prm_ aggregates carried as params + odp@1 `aggregates`; params without a statement insertion site x399 declared on the first statement (326 bind only in the 53A objectives, 73 nowhere).
- **SP 800-53A layer -> sp800-53a@1** on 1014 Requirements: objective trees (53a labels kept - the #10 addressing surface) + EXAMINE/INTERVIEW/TEST methods with object lists (language-tagged).
- **Relations**: related x3510, reference x838, required x715, related-to-withdrawn-or-missing x2; reference targets resolved to publication URLs (landmark); title/citation table -> references@1 on the root Set.
- **Markdown links in prose -> their link text** x525; the target of a link is not carried. x104 name a back-matter resource, of which x40 are also a `reference` link of the same control and so a relation; x340 name another control, of which x138 are also a `related` or `required` link of the same control; x5 name a withdrawn control, x72 a statement of a control, x3 a family, x1 a parameter, x0 nothing the catalogue defines.
- **Conversion ledger (measured per source value)**: each of the 115,680 leaf values of the catalogue and the four profiles was followed into the written files. **31,274 copied** (the value stands, with its type, at the destination, read back from the written file), **17,008 transformed** (a named rule made the destination from it; the rule was applied to the source again and compared), **20,043 intentionally dropped** (a stated reason: 7,011 where the path map of this converter already said the value is not carried, 13,032 in a class the author decided for the IFA corpus on 2026-11-13), **47,355 unaccounted**. Checks that failed: 0. The record is `sp800-53-conversion-ledger.json`: one row per source path and outcome, every row a count over values that were traced one by one in the run that wrote it. An equal value elsewhere in the bundle does not count: a value is traced by what the converter did with it.
- **Label triplet**: zero-padded == sp800-53a asserted (1014 equal, divergent: none); plain -> `label`; zero-padded L3-derivable.
- **Formal ODP ids round-trip** (prop label == uppercase(param name)): ok x682, divergent x776 ([('ac-02.01_odp', 'AC-02(01)_ODP'), ('ac-02.02_odp.01', 'AC-02(02)_ODP[01]'), ('ac-02.02_odp.02', 'AC-02(02)_ODP[02]'), ('ac-02.03_odp.01', 'AC-02(03)_ODP[01]'), ('ac-02.03_odp.02', 'AC-02(03)_ODP[02]')]).
- **Payload free text language-tagged**: ? x1327, assessment-objects x14100, guidance x1014, objective x2787, overview x1.

## Findings (computed)

- **#10 measure (ODP -> statement addressing)**: insertion-count histogram {0: 399, 1: 1201}; params inserted in >=2 statements: **0** (none) - the (requirement, ODP) address resolves via the declaring statement.
- **Corpus mapping endpoints vs minted ids**: 21 citations resolve (5 distinct), 0 hit withdrawn tombstones ([]) - a resolver follows the successor's `replaces[]` backwards; 0 cite unknown labels ([]).
- **Baseline ids not emitted** (withdrawn or unknown): none.
- **Cross-control param insertions x3** ([('ia-13.3', 'ia-13_odp.01'), ('sc-42.2', 'sc-42.01_odp'), ('si-10.1', 'si-10_odp')]): prose in one control inserts another control's ODP - a source irregularity (3 of 2,945 insertions); the declaration is duplicated onto the inserting statement per the per-statement parameter rule. REPORTED upstream.
- **Params bound nowhere x73** (ODPs defined for assessment that neither control text nor 53A objectives insert) - declarations without any insertion site.
- **Path-map sentences the ledger did not confirm** (the map below is corrected; the counts are the ledger's): (1) `parts[].links[]` was described as in-prose citation links, resolved with the reference table. The x7,414 values are the `assessment-for` links of assessment objectives, and none is carried. (2) The catalogue's `uuid` and all of its `metadata` were mapped to the manifest. The manifest holds title, version and oscal-version; the other x98 values are not in the bundle. (3) The same for the four profiles: their title is the baseline Set's title and their version is in the manifest; x200 other values of `uuid`, `metadata` and `back-matter` are not in the bundle. (4) The name, class and namespace of a prop, the name of a part and the class of a group were mapped together with the values they select; x48,499 such values are not carried. (5) `parts[].id` was mapped as a whole; x4,165 ids are not carried: those of guidance, assessment-method and prose-less statement parts, and of the statements of the withdrawn controls without a successor. (6) The formal ODP label was called derivable, its round-trip asserted; the round-trip holds for x682 of 1458. (7) Of the pm overview part only the prose is carried, not its id and title. (8) The media type of a back-matter link (x2) is not on the root Set. (9) The markdown links in prose were said to ride the reference relation; x40 of 525 do.
- **Withdrawn controls without a successor x2**: `cp-10.3` (Compensating Security Controls); `sc-19` (Voice Over Internet Protocol). The catalogue gives such a control no `incorporated-into` or `moved-to` link, only a statement that says why it was withdrawn. The converter drops every withdrawn control and writes its lineage on the successor; where there is none, id, title, labels and that statement are in no object. Reported, not changed.
- **The label of a withdrawn control is taken by position, not by class x163** (reported, not fixed: the fix changes the bundle): the nist-withdrawal annotation takes the first `label` prop of the withdrawn control, whatever its class. In this source that is the zero-padded one, so an annotation says `AC-02(10)` where the Requirements carry the plain form (`AC-2(10)`). The plain label of these controls is dropped with the tombstone; first: `nist#/catalog/groups/0/controls/1/controls/9/props/1/value`.
- **Three claims of the path map, checked value by value**: a zero-padded label is the plain label with its numbers padded (holds x1014, fails x0); the SP 800-53A label of a control equals it (x1014 / x0); the class of a control is told by its `required` edge (x1014 / x0); the print label of a statement item is the last segment of its id (x1122 / x0); the formal ODP label follows from the parameter id (x682 / x776). Where a claim holds the value is a declared drop; where it fails the value is unaccounted.

## Full path map (every source path, its count, its destination)

| path | count | level | destination |
|---|---:|---|---|
| `high.profile.back-matter.resources[].description` | 1 | dropped | not carried: the resource that names the imported catalogue in its three forms (as decided for IFA) |
| `high.profile.back-matter.resources[].rlinks[].href` | 3 | dropped | not carried: the resource that names the imported catalogue in its three forms (as decided for IFA) |
| `high.profile.back-matter.resources[].rlinks[].media-type` | 3 | dropped | not carried: the resource that names the imported catalogue in its three forms (as decided for IFA) |
| `high.profile.back-matter.resources[].uuid` | 1 | dropped | not carried: the resource that names the imported catalogue in its three forms (as decided for IFA) |
| `high.profile.imports[].href` | 1 | L3 | OSCAL-profile resolution mechanics; the selection IS the Set (no semantic residue) |
| `high.profile.imports[].include-controls[].with-ids[]` | 370 | L1 | baseline Set members (minted URIs, catalog order) |
| `high.profile.merge.as-is` | 1 | L3 | OSCAL-profile resolution mechanics; the selection IS the Set (no semantic residue) |
| `high.profile.metadata.last-modified` | 1 | open | not carried and not decided: the document's last-modified and oscal-version, and who is responsible for it |
| `high.profile.metadata.oscal-version` | 1 | open | not carried and not decided: the document's last-modified and oscal-version, and who is responsible for it |
| `high.profile.metadata.parties[].addresses[].addr-lines[]` | 8 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `high.profile.metadata.parties[].addresses[].city` | 2 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `high.profile.metadata.parties[].addresses[].postal-code` | 2 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `high.profile.metadata.parties[].addresses[].state` | 2 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `high.profile.metadata.parties[].email-addresses[]` | 2 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `high.profile.metadata.parties[].name` | 2 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `high.profile.metadata.parties[].short-name` | 1 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `high.profile.metadata.parties[].type` | 2 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `high.profile.metadata.parties[].uuid` | 2 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `high.profile.metadata.responsible-parties[].party-uuids[]` | 4 | open | not carried and not decided: the document's last-modified and oscal-version, and who is responsible for it |
| `high.profile.metadata.responsible-parties[].role-id` | 4 | open | not carried and not decided: the document's last-modified and oscal-version, and who is responsible for it |
| `high.profile.metadata.roles[].id` | 4 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `high.profile.metadata.roles[].title` | 4 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `high.profile.metadata.title` | 1 | L1 | baseline Set title |
| `high.profile.metadata.version` | 1 | L1 | bundle manifest provenance (baselines) |
| `high.profile.uuid` | 1 | dropped | not carried: the uuid of the source document (as decided for IFA) |
| `low.profile.back-matter.resources[].description` | 1 | dropped | not carried: the resource that names the imported catalogue in its three forms (as decided for IFA) |
| `low.profile.back-matter.resources[].rlinks[].href` | 3 | dropped | not carried: the resource that names the imported catalogue in its three forms (as decided for IFA) |
| `low.profile.back-matter.resources[].rlinks[].media-type` | 3 | dropped | not carried: the resource that names the imported catalogue in its three forms (as decided for IFA) |
| `low.profile.back-matter.resources[].uuid` | 1 | dropped | not carried: the resource that names the imported catalogue in its three forms (as decided for IFA) |
| `low.profile.imports[].href` | 1 | L3 | OSCAL-profile resolution mechanics; the selection IS the Set (no semantic residue) |
| `low.profile.imports[].include-controls[].with-ids[]` | 149 | L1 | baseline Set members (minted URIs, catalog order) |
| `low.profile.merge.as-is` | 1 | L3 | OSCAL-profile resolution mechanics; the selection IS the Set (no semantic residue) |
| `low.profile.metadata.last-modified` | 1 | open | not carried and not decided: the document's last-modified and oscal-version, and who is responsible for it |
| `low.profile.metadata.oscal-version` | 1 | open | not carried and not decided: the document's last-modified and oscal-version, and who is responsible for it |
| `low.profile.metadata.parties[].addresses[].addr-lines[]` | 8 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `low.profile.metadata.parties[].addresses[].city` | 2 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `low.profile.metadata.parties[].addresses[].postal-code` | 2 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `low.profile.metadata.parties[].addresses[].state` | 2 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `low.profile.metadata.parties[].email-addresses[]` | 2 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `low.profile.metadata.parties[].name` | 2 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `low.profile.metadata.parties[].short-name` | 1 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `low.profile.metadata.parties[].type` | 2 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `low.profile.metadata.parties[].uuid` | 2 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `low.profile.metadata.responsible-parties[].party-uuids[]` | 4 | open | not carried and not decided: the document's last-modified and oscal-version, and who is responsible for it |
| `low.profile.metadata.responsible-parties[].role-id` | 4 | open | not carried and not decided: the document's last-modified and oscal-version, and who is responsible for it |
| `low.profile.metadata.roles[].id` | 4 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `low.profile.metadata.roles[].title` | 4 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `low.profile.metadata.title` | 1 | L1 | baseline Set title |
| `low.profile.metadata.version` | 1 | L1 | bundle manifest provenance (baselines) |
| `low.profile.uuid` | 1 | dropped | not carried: the uuid of the source document (as decided for IFA) |
| `moderate.profile.back-matter.resources[].description` | 1 | dropped | not carried: the resource that names the imported catalogue in its three forms (as decided for IFA) |
| `moderate.profile.back-matter.resources[].rlinks[].href` | 3 | dropped | not carried: the resource that names the imported catalogue in its three forms (as decided for IFA) |
| `moderate.profile.back-matter.resources[].rlinks[].media-type` | 3 | dropped | not carried: the resource that names the imported catalogue in its three forms (as decided for IFA) |
| `moderate.profile.back-matter.resources[].uuid` | 1 | dropped | not carried: the resource that names the imported catalogue in its three forms (as decided for IFA) |
| `moderate.profile.imports[].href` | 1 | L3 | OSCAL-profile resolution mechanics; the selection IS the Set (no semantic residue) |
| `moderate.profile.imports[].include-controls[].with-ids[]` | 287 | L1 | baseline Set members (minted URIs, catalog order) |
| `moderate.profile.merge.as-is` | 1 | L3 | OSCAL-profile resolution mechanics; the selection IS the Set (no semantic residue) |
| `moderate.profile.metadata.last-modified` | 1 | open | not carried and not decided: the document's last-modified and oscal-version, and who is responsible for it |
| `moderate.profile.metadata.oscal-version` | 1 | open | not carried and not decided: the document's last-modified and oscal-version, and who is responsible for it |
| `moderate.profile.metadata.parties[].addresses[].addr-lines[]` | 8 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `moderate.profile.metadata.parties[].addresses[].city` | 2 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `moderate.profile.metadata.parties[].addresses[].postal-code` | 2 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `moderate.profile.metadata.parties[].addresses[].state` | 2 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `moderate.profile.metadata.parties[].email-addresses[]` | 2 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `moderate.profile.metadata.parties[].name` | 2 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `moderate.profile.metadata.parties[].short-name` | 1 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `moderate.profile.metadata.parties[].type` | 2 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `moderate.profile.metadata.parties[].uuid` | 2 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `moderate.profile.metadata.responsible-parties[].party-uuids[]` | 4 | open | not carried and not decided: the document's last-modified and oscal-version, and who is responsible for it |
| `moderate.profile.metadata.responsible-parties[].role-id` | 4 | open | not carried and not decided: the document's last-modified and oscal-version, and who is responsible for it |
| `moderate.profile.metadata.roles[].id` | 4 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `moderate.profile.metadata.roles[].title` | 4 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `moderate.profile.metadata.title` | 1 | L1 | baseline Set title |
| `moderate.profile.metadata.version` | 1 | L1 | bundle manifest provenance (baselines) |
| `moderate.profile.uuid` | 1 | dropped | not carried: the uuid of the source document (as decided for IFA) |
| `nist.catalog.back-matter.resources[].citation.text` | 192 | L1 | references@1 facet on the root Set (title/citation/url); the link is also the target of a control's `reference` relation |
| `nist.catalog.back-matter.resources[].rlinks[].href` | 201 | L1 | references@1 facet on the root Set (title/citation/url); the link is also the target of a control's `reference` relation |
| `nist.catalog.back-matter.resources[].rlinks[].media-type` | 2 | dropped | not carried: the media type of a resource's link (as decided for IFA) |
| `nist.catalog.back-matter.resources[].title` | 201 | L1 | references@1 facet on the root Set (title/citation/url); the link is also the target of a control's `reference` relation |
| `nist.catalog.back-matter.resources[].uuid` | 201 | L1 | the key by which a control's reference link is resolved to the resource's link; not carried itself (as decided for IFA where no link names it) |
| `nist.catalog.groups[].class` | 20 | dropped | not carried: a type tag; the Set's URI and its place under the root say `family` (as decided for IFA) |
| `nist.catalog.groups[].controls[].class` | 1,196 | dropped | not carried; encoded structurally: family Set membership + `required` base edge distinguishes enhancements (checked per control) |
| `nist.catalog.groups[].controls[].id` | 1,196 | L1 | Requirement id (URI mint, dot form = corpus mapping endpoints) + title | withdrawn: dropped, lineage inverted onto the successor (URI and title in `replaces` and the nist-withdrawal annotation); a withdrawn control that names no successor leaves nothing |
| `nist.catalog.groups[].controls[].links[].href` | 5,265 | L1 | related->related; required->required; reference->reference (resolved URL); incorporated-into/moved-to->successor replaces[] (merged-into/renamed) + nist-withdrawal annotation; a `related` link to a withdrawn control is not carried |
| `nist.catalog.groups[].controls[].links[].rel` | 5,265 | L1 | related->related; required->required; reference->reference (resolved URL); incorporated-into/moved-to->successor replaces[] (merged-into/renamed) + nist-withdrawal annotation; a `related` link to a withdrawn control is not carried |
| `nist.catalog.groups[].controls[].params[].guidelines[].prose` | 1,327 | L2 | odp@1 facet params.{name}.guidelines (language-tagged) |
| `nist.catalog.groups[].controls[].params[].id` | 1,600 | L1 | statement-scoped kernel parameter decl (name, label) on each inserting statement (per-statement parameter rule) |
| `nist.catalog.groups[].controls[].params[].label` | 1,467 | L1 | statement-scoped kernel parameter decl (name, label) on each inserting statement (per-statement parameter rule) |
| `nist.catalog.groups[].controls[].params[].props[].class` | 1,564 | open | select the rule for the prop's value; not carried and not decided |
| `nist.catalog.groups[].controls[].params[].props[].name` | 3,021 | open | select the rule for the prop's value; not carried and not decided |
| `nist.catalog.groups[].controls[].params[].props[].ns` | 331 | open | select the rule for the prop's value; not carried and not decided |
| `nist.catalog.groups[].controls[].params[].props[].value` | 3,021 | L1 | alt-identifier/alt-label/aggregates -> odp@1 facet; prop label (formal ODP id) -> not carried: derivable from the parameter id where the round-trip holds (checked per value), else not decided |
| `nist.catalog.groups[].controls[].params[].select.choice[]` | 355 | L1 | choice type + choices[] + cardinality many (one-or-more) |
| `nist.catalog.groups[].controls[].params[].select.how-many` | 97 | L1 | choice type + choices[] + cardinality many (one-or-more) |
| `nist.catalog.groups[].controls[].parts[].id` | 9,798 | L1 | statement/item with prose -> statement id (control prefix removed); assessment-objective -> its id in sp800-53a@1; the ids of guidance, assessment-method and prose-less statement parts are not carried and not decided |
| `nist.catalog.groups[].controls[].parts[].links[].href` | 3,707 | open | `assessment-for`: the statement an assessment objective assesses; not carried and not decided |
| `nist.catalog.groups[].controls[].parts[].links[].rel` | 3,707 | open | `assessment-for`: the statement an assessment objective assesses; not carried and not decided |
| `nist.catalog.groups[].controls[].parts[].name` | 12,729 | dropped | not carried: a type tag that decided the place (statement/item -> statements[]; guidance -> narrative@1; assessment-* -> sp800-53a@1) (as decided for IFA) |
| `nist.catalog.groups[].controls[].parts[].props[].class` | 6,644 | open | select the rule for the prop's value; not carried and not decided |
| `nist.catalog.groups[].controls[].parts[].props[].name` | 10,697 | open | select the rule for the prop's value; not carried and not decided |
| `nist.catalog.groups[].controls[].parts[].props[].ns` | 2,931 | open | select the rule for the prop's value; not carried and not decided |
| `nist.catalog.groups[].controls[].parts[].props[].value` | 10,697 | L1 | sp800-53a objective/method labels -> sp800-53a@1; method EXAMINE/INTERVIEW/TEST -> sp800-53a@1 methods; item print labels -> not carried, derivable from the item id (checked per value) |
| `nist.catalog.groups[].controls[].parts[].prose` | 8,652 | L1 | statement prose (insertions -> {param:} tokens); guidance/objectives/objects prose -> facets (language-tagged; md #-links -> text) |
| `nist.catalog.groups[].controls[].props[].class` | 2,391 | open | select the rule for the prop's value; not carried and not decided (of a withdrawn control: dropped with the tombstone) |
| `nist.catalog.groups[].controls[].props[].name` | 6,557 | open | select the rule for the prop's value; not carried and not decided (of a withdrawn control: dropped with the tombstone) |
| `nist.catalog.groups[].controls[].props[].ns` | 1,592 | open | select the rule for the prop's value; not carried and not decided (of a withdrawn control: dropped with the tombstone) |
| `nist.catalog.groups[].controls[].props[].value` | 6,557 | L1 | label(plain)->label; zero-padded/sp800-53a label->not carried, derivable from the plain label (checked per value); sort-id->Set sequence; implementation-level->obligated-parties mint; contributes-to-assurance->rmf@1 (a JSON boolean); status->tombstone drop + successor replaces[] |
| `nist.catalog.groups[].controls[].title` | 1,196 | L1 | Requirement id (URI mint, dot form = corpus mapping endpoints) + title | withdrawn: dropped, lineage inverted onto the successor (URI and title in `replaces` and the nist-withdrawal annotation); a withdrawn control that names no successor leaves nothing |
| `nist.catalog.groups[].id` | 20 | L1 | family Set id/title (D21 nesting under root) |
| `nist.catalog.groups[].parts[].id` | 1 | open | not carried and not decided: the id and the title of the pm overview part |
| `nist.catalog.groups[].parts[].name` | 1 | dropped | not carried: a type tag (as decided for IFA) |
| `nist.catalog.groups[].parts[].prose` | 1 | L2 | pm overview part -> narrative@1 guidance on the pm family Set (language-tagged) |
| `nist.catalog.groups[].parts[].title` | 1 | open | not carried and not decided: the id and the title of the pm overview part |
| `nist.catalog.groups[].props[].name` | 20 | open | selects the label; not carried and not decided |
| `nist.catalog.groups[].props[].value` | 20 | L1 | family Set label |
| `nist.catalog.groups[].title` | 20 | L1 | family Set id/title (D21 nesting under root) |
| `nist.catalog.metadata.last-modified` | 1 | open | not carried and not decided: the document's last-modified, its keywords, its links to its other forms, and who is responsible for it |
| `nist.catalog.metadata.links[].href` | 3 | open | not carried and not decided: the document's last-modified, its keywords, its links to its other forms, and who is responsible for it |
| `nist.catalog.metadata.links[].rel` | 3 | open | not carried and not decided: the document's last-modified, its keywords, its links to its other forms, and who is responsible for it |
| `nist.catalog.metadata.oscal-version` | 1 | L1 | bundle manifest provenance (source, source-version, source-oscal-version); the title is also the root Set's, the version stands on every object |
| `nist.catalog.metadata.parties[].addresses[].addr-lines[]` | 8 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `nist.catalog.metadata.parties[].addresses[].city` | 2 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `nist.catalog.metadata.parties[].addresses[].postal-code` | 2 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `nist.catalog.metadata.parties[].addresses[].state` | 2 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `nist.catalog.metadata.parties[].email-addresses[]` | 2 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `nist.catalog.metadata.parties[].name` | 2 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `nist.catalog.metadata.parties[].short-name` | 1 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `nist.catalog.metadata.parties[].type` | 2 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `nist.catalog.metadata.parties[].uuid` | 2 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `nist.catalog.metadata.props[].name` | 1 | open | not carried and not decided: the document's last-modified, its keywords, its links to its other forms, and who is responsible for it |
| `nist.catalog.metadata.props[].value` | 1 | open | not carried and not decided: the document's last-modified, its keywords, its links to its other forms, and who is responsible for it |
| `nist.catalog.metadata.responsible-parties[].party-uuids[]` | 4 | open | not carried and not decided: the document's last-modified, its keywords, its links to its other forms, and who is responsible for it |
| `nist.catalog.metadata.responsible-parties[].role-id` | 4 | open | not carried and not decided: the document's last-modified, its keywords, its links to its other forms, and who is responsible for it |
| `nist.catalog.metadata.revisions[].last-modified` | 7 | dropped | not carried: revision history of the source document (as decided for IFA) |
| `nist.catalog.metadata.revisions[].links[].href` | 7 | dropped | not carried: revision history of the source document (as decided for IFA) |
| `nist.catalog.metadata.revisions[].links[].rel` | 7 | dropped | not carried: revision history of the source document (as decided for IFA) |
| `nist.catalog.metadata.revisions[].oscal-version` | 7 | dropped | not carried: revision history of the source document (as decided for IFA) |
| `nist.catalog.metadata.revisions[].remarks` | 7 | dropped | not carried: revision history of the source document (as decided for IFA) |
| `nist.catalog.metadata.revisions[].title` | 7 | dropped | not carried: revision history of the source document (as decided for IFA) |
| `nist.catalog.metadata.revisions[].version` | 7 | dropped | not carried: revision history of the source document (as decided for IFA) |
| `nist.catalog.metadata.roles[].id` | 4 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `nist.catalog.metadata.roles[].title` | 4 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `nist.catalog.metadata.title` | 1 | L1 | bundle manifest provenance (source, source-version, source-oscal-version); the title is also the root Set's, the version stands on every object |
| `nist.catalog.metadata.version` | 1 | L1 | bundle manifest provenance (source, source-version, source-oscal-version); the title is also the root Set's, the version stands on every object |
| `nist.catalog.uuid` | 1 | dropped | not carried: the uuid of the source document (as decided for IFA) |
| `privacy.profile.back-matter.resources[].description` | 1 | dropped | not carried: the resource that names the imported catalogue in its three forms (as decided for IFA) |
| `privacy.profile.back-matter.resources[].rlinks[].href` | 3 | dropped | not carried: the resource that names the imported catalogue in its three forms (as decided for IFA) |
| `privacy.profile.back-matter.resources[].rlinks[].media-type` | 3 | dropped | not carried: the resource that names the imported catalogue in its three forms (as decided for IFA) |
| `privacy.profile.back-matter.resources[].uuid` | 1 | dropped | not carried: the resource that names the imported catalogue in its three forms (as decided for IFA) |
| `privacy.profile.imports[].href` | 1 | L3 | OSCAL-profile resolution mechanics; the selection IS the Set (no semantic residue) |
| `privacy.profile.imports[].include-controls[].with-ids[]` | 96 | L1 | baseline Set members (minted URIs, catalog order) |
| `privacy.profile.merge.as-is` | 1 | L3 | OSCAL-profile resolution mechanics; the selection IS the Set (no semantic residue) |
| `privacy.profile.metadata.last-modified` | 1 | open | not carried and not decided: the document's last-modified and oscal-version, and who is responsible for it |
| `privacy.profile.metadata.oscal-version` | 1 | open | not carried and not decided: the document's last-modified and oscal-version, and who is responsible for it |
| `privacy.profile.metadata.parties[].addresses[].addr-lines[]` | 8 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `privacy.profile.metadata.parties[].addresses[].city` | 2 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `privacy.profile.metadata.parties[].addresses[].postal-code` | 2 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `privacy.profile.metadata.parties[].addresses[].state` | 2 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `privacy.profile.metadata.parties[].email-addresses[]` | 2 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `privacy.profile.metadata.parties[].name` | 2 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `privacy.profile.metadata.parties[].short-name` | 1 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `privacy.profile.metadata.parties[].type` | 2 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `privacy.profile.metadata.parties[].uuid` | 2 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `privacy.profile.metadata.responsible-parties[].party-uuids[]` | 4 | open | not carried and not decided: the document's last-modified and oscal-version, and who is responsible for it |
| `privacy.profile.metadata.responsible-parties[].role-id` | 4 | open | not carried and not decided: the document's last-modified and oscal-version, and who is responsible for it |
| `privacy.profile.metadata.roles[].id` | 4 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `privacy.profile.metadata.roles[].title` | 4 | dropped | not carried: the source's directory of parties and roles (as decided for IFA) |
| `privacy.profile.metadata.title` | 1 | L1 | baseline Set title |
| `privacy.profile.metadata.version` | 1 | L1 | bundle manifest provenance (baselines) |
| `privacy.profile.uuid` | 1 | dropped | not carried: the uuid of the source document (as decided for IFA) |

## UNMAPPED (gate target: zero)

*(none)*

## Conversion ledger: the rules

A value the converter computes is stated as a named rule with a pure function. After the bundle is written the function is applied to the source value again and the result is compared with what the file holds. A rule with several inputs counts each of them: the id of a control is an input of the rule that cuts it off a statement id.

| rule | source values | destinations |
|---|---:|---:|
| requirement URI from the control a link names | 4,225 | 4,225 |
| statement id without the control prefix | 2,932 | 3,836 |
| assessment objects: one entry per paragraph of the part's prose, trimmed (insertions as tokens, markdown links as their text) | 2,491 | 13,660 |
| prose with each parameter insertion {{ insert: param, x }} written as the token {param:x} | 2,422 | 2,422 |
| requirement URI from the control id | 1,916 | 3,944 |
| obligated party URI from the implementation level | 1,165 | 2,166 |
| a reference link resolved by uuid: the first link of the back-matter resource it names | 1,158 | 2,514 |
| member sequence: ten times the control's place in its family, ordered by sort-id | 1,014 | 1,014 |
| lineage inverted: the URI of a withdrawn control, written on the successor its link names | 523 | 1,200 |
| lineage mode from the link's rel (incorporated-into -> merged-into, moved-to -> renamed) | 200 | 400 |
| prose with each markdown link into the catalogue replaced by its link text (the target is not carried) | 160 | 160 |
| parameter cardinality `many` from the selection's how-many `one-or-more` | 97 | 97 |
| family Set URI from the group id | 20 | 60 |
| prose with each parameter insertion {{ insert: param, x }} written as the token {param:x}; prose with each markdown link into the catalogue replaced by its link text (the target is not carried) | 2 | 2 |
| the statement a lineage link names, as a statement id | 1 | 1 |

## Conversion ledger: the declared drops

A drop is declared on one of two grounds, and applies only to a value that reached no destination.

**(a) The path map of this converter already said the value is not carried: 7,011 values.**

| reason | values |
|---|---:|
| path map: a withdrawn control is dropped as a tombstone; its lineage is inverted onto the successor its link names, which carries its URI, a label and its title | 2,157 |
| path map: the zero-padded and the SP 800-53A label of a control are derivable from the label that is carried (its numbers padded to two digits; checked for this value) | 2,028 |
| path map: the print label of a statement item is derivable: its letter or number is the last segment of the item id (checked for this value), its punctuation is print form | 1,122 |
| path map: the class of a control is encoded structurally (membership in its family Set; the `required` edge of an enhancement to its base control) | 1,014 |
| path map: the formal ODP label of a parameter is derivable from the parameter id (checked for this value) | 682 |
| path map: profile resolution mechanics; the selection is the Set | 8 |

**(b) A class the author decided for the IFA corpus on 2026-11-13: 13,032 values.**

| reason | values |
|---|---:|
| as decided for IFA on 2026-11-13: a type tag of a structural element: the bundle says by its shape what kind of thing the element is | 12,748 |
| as decided for IFA on 2026-11-13: the source's directory of parties and roles: a party is a landmark URI and there is no party object (register, backlog #16) | 155 |
| as decided for IFA on 2026-11-13: revision history of the source document | 49 |
| as decided for IFA on 2026-11-13: the uuid of a back-matter resource that no reference link of a control names; it identifies the resource inside the catalogue only, and the resource's title and link are on the root Set | 41 |
| as decided for IFA on 2026-11-13: a back-matter resource or an import link: a link to another serialisation of the source or to an imported document; the bundle carries the Requirements themselves | 34 |
| as decided for IFA on 2026-11-13: the uuid of a source document, which identifies it among source documents only: JASCON objects get URIs minted from ids | 5 |

## Conversion ledger: the unaccounted values, by class

47,355 values have no destination and no declared reason. Nothing is decided for them: the recommendation is a proposal, and to carry a value changes the bundle.

| values | what they are | of which | example | recommendation |
|---:|---|---|---|---|
| 34,477 | the name, the class or the namespace of a prop: it selects the rule that is applied to the prop's value | name x19,387, class x10,236, ns x4,854 | `nist#/catalog/metadata/props/0/name` = `keywords` | drop, by one decision for all: so the author decided for the one selector of the IFA corpus (the prop name of a response type). What becomes of the value a selector selects is said for that value |
| 7,414 | the `assessment-for` link of an assessment objective (href and rel): the statement the objective assesses | rel x3,707, href to a statement the bundle holds x3,484, href to a statement part as a whole, whose text is in its items x217, href to a part of another control x6 | `nist#/catalog/groups/0/controls/0/parts/2/parts/0/parts/0/links/0/href` = `#ac-1_smt.a` | carry: `assessment-for` on the objective in sp800-53a@1, as the id of the statement; the CIS Controls converter carries the same link of its source. Where the link names a statement part as a whole there is no statement to name, and a link into another control is to be looked at in the source first |
| 4,164 | the id of a part that gets no id in the bundle: the guidance, an assessment method, a statement part that only groups items, the overview of a family | assessment-method x2,931, guidance x1,014, statement without prose x218, overview x1 | `nist#/catalog/groups/0/controls/0/parts/0/id` = `ac-1_smt` | drop: each is the id of its control or family with a fixed suffix (`_gdn`, `_asm-examine`, `_smt`, `_ovw`). To decide together with the `assessment-for` links: the link of a control's first objective names the statement part as a whole, which has no address in the bundle |
| 776 | the formal ODP label of a parameter where the converter's round-trip from the parameter id does not give it (parameters of enhancements: `ac-02.01_odp` is labelled `AC-02(01)_ODP`, the rule gives `AC-02.01_ODP`) | - | `nist#/catalog/groups/0/controls/1/controls/0/params/0/props/1/value` = `AC-02(01)_ODP` | drop, after the rule is corrected to write the number of the enhancement in brackets: measured on 5.2.0 on 2026-11-14, it then gives 1,455 of the 1,458 labels; or carry the label in odp@1 beside `alt-label` |
| 427 | a value carried as a JSON boolean: `contributes-to-assurance` = `true` is written as `true` in rmf@1. The ledger follows strings and integers and cannot see it arrive | - | `nist#/catalog/groups/0/controls/0/props/5/value` = `true` | nothing to decide for the bundle: the value is carried. For the ledger: a way to state a rule whose result is a boolean (oscal_conv_lib), or a declared reason |
| 40 | who is responsible for a source document in which role (role-id and party uuid): creator, publisher and their contacts | - | `nist#/catalog/metadata/responsible-parties/0/role-id` = `publisher` | drop with the directory of parties and roles; or carry the publisher as the author in the manifest's provenance, as a landmark URI |
| 36 | everything of a withdrawn control that names no successor: its id, title, labels and the one statement that says why it was withdrawn. Nothing of such a control is in the bundle | cp-10.3 x18, sc-19 x18 | `nist#/catalog/groups/5/controls/9/controls/2/id` = `cp-10.3` | carry: a Requirement with lifecycle `withdrawn` for a control no other control replaces, with its statement as the reason; or drop with that reason stated |
| 10 | document metadata the manifest does not hold: `last-modified` of the catalogue and of the four profiles, the `oscal-version` of the profiles, the catalogue's keywords | last-modified x5, oscal-version x4, props[].value x1 | `nist#/catalog/metadata/last-modified` = `2026-05-11T16:01:09.00000-00:00` | carry: `provenance.source-documents` in the manifest, as the IFA conversion does (title, version, last-modified, oscal-version per document) |
| 6 | the catalogue's links to its other forms (`alternate`: the PDF, `canonical`: the DOI, `cprt`: the reference tool) | href x3, rel x3 | `nist#/catalog/metadata/links/0/href` = `#c3397cc9-83c6-4459-adb2-836739dc1b94` | drop: a link to another serialisation of the source, a class decided for IFA; the three resources they name are on the root Set |
| 4 | a `related` link to a withdrawn control (href and rel) | href x2, rel x2 | `nist#/catalog/groups/2/controls/4/controls/3/links/1/href` = `#au-15` | carry: the relation to the successor the withdrawn control names; or drop, the target being a tombstone |
| 1 | the title of the overview part of the PM family | - | `nist#/catalog/groups/12/parts/0/title` = `Program Management Controls` | carry: beside the overview text in narrative@1; or drop, it repeats the family's title in other words |

## Unaccounted source values, by path (conversion ledger)

The same values by source path, nested controls and parts counted under one path as in the path map.

| path | count | first value |
|---|---:|---|
| `high.profile.metadata.last-modified` | 1 | `high#/profile/metadata/last-modified` |
| `high.profile.metadata.oscal-version` | 1 | `high#/profile/metadata/oscal-version` |
| `high.profile.metadata.responsible-parties[].party-uuids[]` | 4 | `high#/profile/metadata/responsible-parties/0/party-uuids/0` |
| `high.profile.metadata.responsible-parties[].role-id` | 4 | `high#/profile/metadata/responsible-parties/0/role-id` |
| `low.profile.metadata.last-modified` | 1 | `low#/profile/metadata/last-modified` |
| `low.profile.metadata.oscal-version` | 1 | `low#/profile/metadata/oscal-version` |
| `low.profile.metadata.responsible-parties[].party-uuids[]` | 4 | `low#/profile/metadata/responsible-parties/0/party-uuids/0` |
| `low.profile.metadata.responsible-parties[].role-id` | 4 | `low#/profile/metadata/responsible-parties/0/role-id` |
| `moderate.profile.metadata.last-modified` | 1 | `moderate#/profile/metadata/last-modified` |
| `moderate.profile.metadata.oscal-version` | 1 | `moderate#/profile/metadata/oscal-version` |
| `moderate.profile.metadata.responsible-parties[].party-uuids[]` | 4 | `moderate#/profile/metadata/responsible-parties/0/party-uuids/0` |
| `moderate.profile.metadata.responsible-parties[].role-id` | 4 | `moderate#/profile/metadata/responsible-parties/0/role-id` |
| `nist.catalog.groups[].controls[].class` | 2 | `nist#/catalog/groups/17/controls/18/class` |
| `nist.catalog.groups[].controls[].id` | 2 | `nist#/catalog/groups/5/controls/9/controls/2/id` |
| `nist.catalog.groups[].controls[].links[].href` | 2 | `nist#/catalog/groups/2/controls/4/controls/3/links/1/href` |
| `nist.catalog.groups[].controls[].links[].rel` | 2 | `nist#/catalog/groups/2/controls/4/controls/3/links/1/rel` |
| `nist.catalog.groups[].controls[].params[].props[].class` | 1,564 | `nist#/catalog/groups/0/controls/1/controls/0/params/0/props/1/class` |
| `nist.catalog.groups[].controls[].params[].props[].name` | 3,021 | `nist#/catalog/groups/0/controls/1/controls/0/params/0/props/0/name` |
| `nist.catalog.groups[].controls[].params[].props[].ns` | 331 | `nist#/catalog/groups/0/controls/2/controls/2/params/0/props/0/ns` |
| `nist.catalog.groups[].controls[].params[].props[].value` | 776 | `nist#/catalog/groups/0/controls/1/controls/0/params/0/props/1/value` |
| `nist.catalog.groups[].controls[].parts[].id` | 4,165 | `nist#/catalog/groups/0/controls/1/controls/0/parts/1/id` |
| `nist.catalog.groups[].controls[].parts[].links[].href` | 3,707 | `nist#/catalog/groups/0/controls/1/controls/0/parts/2/links/0/href` |
| `nist.catalog.groups[].controls[].parts[].links[].rel` | 3,707 | `nist#/catalog/groups/0/controls/1/controls/0/parts/2/links/0/rel` |
| `nist.catalog.groups[].controls[].parts[].name` | 2 | `nist#/catalog/groups/5/controls/9/controls/2/parts/0/name` |
| `nist.catalog.groups[].controls[].parts[].props[].class` | 6,644 | `nist#/catalog/groups/0/controls/18/controls/3/parts/2/parts/1/parts/3/parts/0/props/0/class` |
| `nist.catalog.groups[].controls[].parts[].props[].name` | 10,697 | `nist#/catalog/groups/0/controls/18/controls/3/parts/2/parts/1/parts/3/parts/0/props/0/name` |
| `nist.catalog.groups[].controls[].parts[].props[].ns` | 2,931 | `nist#/catalog/groups/0/controls/1/controls/0/parts/3/props/0/ns` |
| `nist.catalog.groups[].controls[].parts[].prose` | 2 | `nist#/catalog/groups/5/controls/9/controls/2/parts/0/prose` |
| `nist.catalog.groups[].controls[].props[].class` | 2,032 | `nist#/catalog/groups/0/controls/1/controls/0/props/0/class` |
| `nist.catalog.groups[].controls[].props[].name` | 5,658 | `nist#/catalog/groups/0/controls/1/controls/0/props/0/name` |
| `nist.catalog.groups[].controls[].props[].ns` | 1,592 | `nist#/catalog/groups/0/controls/1/controls/0/props/4/ns` |
| `nist.catalog.groups[].controls[].props[].value` | 437 | `nist#/catalog/groups/1/controls/1/controls/0/props/5/value` |
| `nist.catalog.groups[].controls[].title` | 2 | `nist#/catalog/groups/5/controls/9/controls/2/title` |
| `nist.catalog.groups[].parts[].id` | 1 | `nist#/catalog/groups/12/parts/0/id` |
| `nist.catalog.groups[].parts[].title` | 1 | `nist#/catalog/groups/12/parts/0/title` |
| `nist.catalog.groups[].props[].name` | 20 | `nist#/catalog/groups/0/props/0/name` |
| `nist.catalog.metadata.last-modified` | 1 | `nist#/catalog/metadata/last-modified` |
| `nist.catalog.metadata.links[].href` | 3 | `nist#/catalog/metadata/links/0/href` |
| `nist.catalog.metadata.links[].rel` | 3 | `nist#/catalog/metadata/links/0/rel` |
| `nist.catalog.metadata.props[].name` | 1 | `nist#/catalog/metadata/props/0/name` |
| `nist.catalog.metadata.props[].value` | 1 | `nist#/catalog/metadata/props/0/value` |
| `nist.catalog.metadata.responsible-parties[].party-uuids[]` | 4 | `nist#/catalog/metadata/responsible-parties/0/party-uuids/0` |
| `nist.catalog.metadata.responsible-parties[].role-id` | 4 | `nist#/catalog/metadata/responsible-parties/0/role-id` |
| `privacy.profile.metadata.last-modified` | 1 | `privacy#/profile/metadata/last-modified` |
| `privacy.profile.metadata.oscal-version` | 1 | `privacy#/profile/metadata/oscal-version` |
| `privacy.profile.metadata.responsible-parties[].party-uuids[]` | 4 | `privacy#/profile/metadata/responsible-parties/0/party-uuids/0` |
| `privacy.profile.metadata.responsible-parties[].role-id` | 4 | `privacy#/profile/metadata/responsible-parties/0/role-id` |

## What the ledger cannot see

The ledger follows source values into the bundle. A value the converter writes on its own has no entry in it. Seen from the bundle: 5,918 leaf values of the written objects are neither a source value nor the result of a stated rule. The manifest's digests and paths are computed from the written files and are not listed.

| place in an object | values | example | what stands behind it |
|---|---:|---|---|
| `/statements/[]/modality` | 1,918 | `must` | the converter's corpus rule: every statement of Rev 5 is read as `must` |
| `/statements/[]/parameters/[]/type` | 1,603 | `string` | decided by the shape of the source parameter: `choice` where it has a `select`, else `string` |
| `/lifecycle` | 1,039 | `active` | the converter's: every object it writes is `active`; a withdrawn control is not written |
| `/members/[]/sequence` | 922 | `10` | the member's position: in the catalogue (root Set) or in the profile's list (baseline Sets) |
| `/facets/https://ns.nist.gov/sp800-53/facet/rmf@1/contributes-to-assurance` | 427 | `true` | the source's `true`, written as a boolean (see the unaccounted class) |
| `/id` | 5 | `https://ns.nist.gov/sp800-53/set/baseline/high` | the URI of the root Set and of a baseline Set, the latter from the name of the profile's file |
| `/label` | 4 | `HIGH` | the label of a baseline Set, from the name of the profile's file |

A rule can also discard a part of a value, which no count of leaves shows: a markdown link in prose is replaced by its text, and its target is gone. What those targets were is counted under the conversion rules above.
