# NIST SP 800-53 Rev 5 + 800-53B -> Semantic Core: Coverage Report (computed)

Source: **Electronic (OSCAL) Version of NIST SP 800-53 Rev 5.2.0 Controls and SP 800-53A Rev 5.2.0 Assessment Procedures** v5.2.0 (OSCAL 1.2.2) + four 800-53B baseline profiles. Census: `drafts/gate-3-census.md`.

## Totals

- Source leaf values inventoried: **115,680**
- Mapped (declared destination): **115,680**
- **UNMAPPED: 0**  ->  coverage **100.0 %**
- Objects emitted: **1014 Requirements** (324+872 minus 182 withdrawn tombstones), **25 Sets** (20 families + root + 4 baselines), manifest with both digests.
- Baseline membership: LOW 149, MODERATE 287, HIGH 370, PRIVACY 96.

## Conversion rules (declared, counted)

- **Withdrawn tombstones dropped, lineage inverted (kernel `replaces[]`)**: 182 withdrawn; 199 successor edges on Requirements + 1 on family Sets (sa-12 'moved to SR' - the successor is a whole family; shared base makes Set-level `replaces` legal) (incorporated-into->merged-into, moved-to->renamed); statement-precision + withdrawn label/title in `annotations['nist-withdrawal']`; withdrawn->withdrawn chains x0, dangling x0.
- **Modality corpus rule `must` x1918**: Rev 5 statements are uniformly imperative and obligation binds on baseline selection - the INVERSE of the declarative national pattern (ISM/CIS/CyFun/C5). Force in the mood, selection in the baseline Sets; both confirm D13's split axes.
- **Obligated parties from `implementation-level`**: organization/system party URIs; absent -> organization default x0.
- **Two-layer ODP params -> statement-scoped decls**: declared on each statement whose prose inserts them (per-statement parameter rule); choice x133, string else; legacy _prm_ aggregates carried as params + odp@1 `aggregates`; params without a statement insertion site x399 declared on the first statement (326 bind only in the 53A objectives, 73 nowhere).
- **SP 800-53A layer -> sp800-53a@1** on 1014 Requirements: objective trees (53a labels kept - the #10 addressing surface) + EXAMINE/INTERVIEW/TEST methods with object lists (language-tagged).
- **Relations**: related x3510, reference x838, required x715, related-to-withdrawn-or-missing x2; reference targets resolved to publication URLs (landmark); title/citation table -> references@1 on the root Set.
- **Markdown citation links in prose -> plain text** x525 (citation rides the reference relation).
- **Label triplet**: zero-padded == sp800-53a asserted (1014 equal, divergent: none); plain -> `label`; zero-padded L3-derivable.
- **Formal ODP ids round-trip** (prop label == uppercase(param name)): ok x682, divergent x776 ([('ac-02.01_odp', 'AC-02(01)_ODP'), ('ac-02.02_odp.01', 'AC-02(02)_ODP[01]'), ('ac-02.02_odp.02', 'AC-02(02)_ODP[02]'), ('ac-02.03_odp.01', 'AC-02(03)_ODP[01]'), ('ac-02.03_odp.02', 'AC-02(03)_ODP[02]')]).
- **Payload free text language-tagged**: ? x1327, assessment-objects x14100, guidance x1014, objective x2787, overview x1.

## Findings (computed)

- **#10 measure (ODP -> statement addressing)**: insertion-count histogram {0: 399, 1: 1201}; params inserted in >=2 statements: **0** (none) - the (requirement, ODP) address resolves via the declaring statement.
- **Corpus mapping endpoints vs minted ids**: 437 citations resolve (217 distinct), 0 hit withdrawn tombstones ([]) - a resolver follows the successor's `replaces[]` backwards; 0 cite unknown labels ([]).
- **Baseline ids not emitted** (withdrawn or unknown): none.
- **Cross-control param insertions x3** ([('ia-13.3', 'ia-13_odp.01'), ('sc-42.2', 'sc-42.01_odp'), ('si-10.1', 'si-10_odp')]): prose in one control inserts another control's ODP - a source irregularity (3 of 2,945 insertions); the declaration is duplicated onto the inserting statement per the per-statement parameter rule. REPORTED upstream.
- **Params bound nowhere x73** (ODPs defined for assessment that neither control text nor 53A objectives insert) - declarations without any insertion site.

## Full path map (every source path, its count, its destination)

| path | count | level | destination |
|---|---:|---|---|
| `high.profile.back-matter.resources[].description` | 1 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `high.profile.back-matter.resources[].rlinks[].href` | 3 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `high.profile.back-matter.resources[].rlinks[].media-type` | 3 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `high.profile.back-matter.resources[].uuid` | 1 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `high.profile.imports[].href` | 1 | L3 | OSCAL-profile resolution mechanics; the selection IS the Set (no semantic residue) |
| `high.profile.imports[].include-controls[].with-ids[]` | 370 | L1 | baseline Set members (minted URIs, catalog order) |
| `high.profile.merge.as-is` | 1 | L3 | OSCAL-profile resolution mechanics; the selection IS the Set (no semantic residue) |
| `high.profile.metadata.last-modified` | 1 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `high.profile.metadata.oscal-version` | 1 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `high.profile.metadata.parties[].addresses[].addr-lines[]` | 8 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `high.profile.metadata.parties[].addresses[].city` | 2 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `high.profile.metadata.parties[].addresses[].postal-code` | 2 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `high.profile.metadata.parties[].addresses[].state` | 2 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `high.profile.metadata.parties[].email-addresses[]` | 2 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `high.profile.metadata.parties[].name` | 2 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `high.profile.metadata.parties[].short-name` | 1 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `high.profile.metadata.parties[].type` | 2 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `high.profile.metadata.parties[].uuid` | 2 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `high.profile.metadata.responsible-parties[].party-uuids[]` | 4 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `high.profile.metadata.responsible-parties[].role-id` | 4 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `high.profile.metadata.roles[].id` | 4 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `high.profile.metadata.roles[].title` | 4 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `high.profile.metadata.title` | 1 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `high.profile.metadata.version` | 1 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `high.profile.uuid` | 1 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `low.profile.back-matter.resources[].description` | 1 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `low.profile.back-matter.resources[].rlinks[].href` | 3 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `low.profile.back-matter.resources[].rlinks[].media-type` | 3 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `low.profile.back-matter.resources[].uuid` | 1 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `low.profile.imports[].href` | 1 | L3 | OSCAL-profile resolution mechanics; the selection IS the Set (no semantic residue) |
| `low.profile.imports[].include-controls[].with-ids[]` | 149 | L1 | baseline Set members (minted URIs, catalog order) |
| `low.profile.merge.as-is` | 1 | L3 | OSCAL-profile resolution mechanics; the selection IS the Set (no semantic residue) |
| `low.profile.metadata.last-modified` | 1 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `low.profile.metadata.oscal-version` | 1 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `low.profile.metadata.parties[].addresses[].addr-lines[]` | 8 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `low.profile.metadata.parties[].addresses[].city` | 2 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `low.profile.metadata.parties[].addresses[].postal-code` | 2 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `low.profile.metadata.parties[].addresses[].state` | 2 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `low.profile.metadata.parties[].email-addresses[]` | 2 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `low.profile.metadata.parties[].name` | 2 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `low.profile.metadata.parties[].short-name` | 1 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `low.profile.metadata.parties[].type` | 2 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `low.profile.metadata.parties[].uuid` | 2 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `low.profile.metadata.responsible-parties[].party-uuids[]` | 4 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `low.profile.metadata.responsible-parties[].role-id` | 4 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `low.profile.metadata.roles[].id` | 4 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `low.profile.metadata.roles[].title` | 4 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `low.profile.metadata.title` | 1 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `low.profile.metadata.version` | 1 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `low.profile.uuid` | 1 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `moderate.profile.back-matter.resources[].description` | 1 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `moderate.profile.back-matter.resources[].rlinks[].href` | 3 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `moderate.profile.back-matter.resources[].rlinks[].media-type` | 3 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `moderate.profile.back-matter.resources[].uuid` | 1 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `moderate.profile.imports[].href` | 1 | L3 | OSCAL-profile resolution mechanics; the selection IS the Set (no semantic residue) |
| `moderate.profile.imports[].include-controls[].with-ids[]` | 287 | L1 | baseline Set members (minted URIs, catalog order) |
| `moderate.profile.merge.as-is` | 1 | L3 | OSCAL-profile resolution mechanics; the selection IS the Set (no semantic residue) |
| `moderate.profile.metadata.last-modified` | 1 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `moderate.profile.metadata.oscal-version` | 1 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `moderate.profile.metadata.parties[].addresses[].addr-lines[]` | 8 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `moderate.profile.metadata.parties[].addresses[].city` | 2 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `moderate.profile.metadata.parties[].addresses[].postal-code` | 2 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `moderate.profile.metadata.parties[].addresses[].state` | 2 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `moderate.profile.metadata.parties[].email-addresses[]` | 2 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `moderate.profile.metadata.parties[].name` | 2 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `moderate.profile.metadata.parties[].short-name` | 1 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `moderate.profile.metadata.parties[].type` | 2 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `moderate.profile.metadata.parties[].uuid` | 2 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `moderate.profile.metadata.responsible-parties[].party-uuids[]` | 4 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `moderate.profile.metadata.responsible-parties[].role-id` | 4 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `moderate.profile.metadata.roles[].id` | 4 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `moderate.profile.metadata.roles[].title` | 4 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `moderate.profile.metadata.title` | 1 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `moderate.profile.metadata.version` | 1 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `moderate.profile.uuid` | 1 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `nist.catalog.back-matter.resources[].citation.text` | 192 | L1 | reference-link resolution table + references@1 facet on the root Set (title/citation/url) |
| `nist.catalog.back-matter.resources[].rlinks[].href` | 201 | L1 | reference-link resolution table + references@1 facet on the root Set (title/citation/url) |
| `nist.catalog.back-matter.resources[].rlinks[].media-type` | 2 | L1 | reference-link resolution table + references@1 facet on the root Set (title/citation/url) |
| `nist.catalog.back-matter.resources[].title` | 201 | L1 | reference-link resolution table + references@1 facet on the root Set (title/citation/url) |
| `nist.catalog.back-matter.resources[].uuid` | 201 | L1 | reference-link resolution table + references@1 facet on the root Set (title/citation/url) |
| `nist.catalog.groups[].class` | 20 | L1 | family Set id/title (D21 nesting under root) |
| `nist.catalog.groups[].controls[].class` | 1,196 | L1 | encoded structurally: family Set membership + `required` base edge distinguishes enhancements |
| `nist.catalog.groups[].controls[].id` | 1,196 | L1 | Requirement id (URI mint, dot form = corpus mapping endpoints) + title | withdrawn: dropped, lineage inverted |
| `nist.catalog.groups[].controls[].links[].href` | 5,265 | L1 | related->related; required->required; reference->reference (resolved URL); incorporated-into/moved-to->successor replaces[] (merged-into/renamed) + nist-withdrawal annotation |
| `nist.catalog.groups[].controls[].links[].rel` | 5,265 | L1 | related->related; required->required; reference->reference (resolved URL); incorporated-into/moved-to->successor replaces[] (merged-into/renamed) + nist-withdrawal annotation |
| `nist.catalog.groups[].controls[].params[].guidelines[].prose` | 1,327 | L2 | odp@1 facet params.{name}.guidelines (language-tagged) |
| `nist.catalog.groups[].controls[].params[].id` | 1,600 | L1 | statement-scoped kernel parameter decl (name, label) on each inserting statement (per-statement parameter rule) |
| `nist.catalog.groups[].controls[].params[].label` | 1,467 | L1 | statement-scoped kernel parameter decl (name, label) on each inserting statement (per-statement parameter rule) |
| `nist.catalog.groups[].controls[].params[].props[].class` | 1,564 | L1 | prop label (formal ODP id) -> L3-derivable (round-trip asserted); alt-identifier/alt-label/aggregates -> odp@1 facet |
| `nist.catalog.groups[].controls[].params[].props[].name` | 3,021 | L1 | prop label (formal ODP id) -> L3-derivable (round-trip asserted); alt-identifier/alt-label/aggregates -> odp@1 facet |
| `nist.catalog.groups[].controls[].params[].props[].ns` | 331 | L1 | prop label (formal ODP id) -> L3-derivable (round-trip asserted); alt-identifier/alt-label/aggregates -> odp@1 facet |
| `nist.catalog.groups[].controls[].params[].props[].value` | 3,021 | L1 | prop label (formal ODP id) -> L3-derivable (round-trip asserted); alt-identifier/alt-label/aggregates -> odp@1 facet |
| `nist.catalog.groups[].controls[].params[].select.choice[]` | 355 | L1 | choice type + choices[] + cardinality many (one-or-more) |
| `nist.catalog.groups[].controls[].params[].select.how-many` | 97 | L1 | choice type + choices[] + cardinality many (one-or-more) |
| `nist.catalog.groups[].controls[].parts[].id` | 9,798 | L1 | statement/item -> flattened statements[] (id suffix); guidance -> narrative@1; assessment-* -> sp800-53a@1 |
| `nist.catalog.groups[].controls[].parts[].links[].href` | 3,707 | L1 | in-prose citation links; resolved with the same reference table (md #-links -> text; target rides control-level reference relation) |
| `nist.catalog.groups[].controls[].parts[].links[].rel` | 3,707 | L1 | in-prose citation links; resolved with the same reference table (md #-links -> text; target rides control-level reference relation) |
| `nist.catalog.groups[].controls[].parts[].name` | 12,729 | L1 | statement/item -> flattened statements[] (id suffix); guidance -> narrative@1; assessment-* -> sp800-53a@1 |
| `nist.catalog.groups[].controls[].parts[].props[].class` | 6,644 | L1 | item print labels -> L3-derivable (id-encoded); sp800-53a objective/method labels -> sp800-53a@1; method EXAMINE/INTERVIEW/TEST -> sp800-53a@1 methods |
| `nist.catalog.groups[].controls[].parts[].props[].name` | 10,697 | L1 | item print labels -> L3-derivable (id-encoded); sp800-53a objective/method labels -> sp800-53a@1; method EXAMINE/INTERVIEW/TEST -> sp800-53a@1 methods |
| `nist.catalog.groups[].controls[].parts[].props[].ns` | 2,931 | L1 | item print labels -> L3-derivable (id-encoded); sp800-53a objective/method labels -> sp800-53a@1; method EXAMINE/INTERVIEW/TEST -> sp800-53a@1 methods |
| `nist.catalog.groups[].controls[].parts[].props[].value` | 10,697 | L1 | item print labels -> L3-derivable (id-encoded); sp800-53a objective/method labels -> sp800-53a@1; method EXAMINE/INTERVIEW/TEST -> sp800-53a@1 methods |
| `nist.catalog.groups[].controls[].parts[].prose` | 8,652 | L1 | statement prose (insertions -> {param:} tokens); guidance/objectives/objects prose -> facets (language-tagged; md #-links -> text) |
| `nist.catalog.groups[].controls[].props[].class` | 2,391 | L1 | label(plain)->label; zero-padded/sp800-53a->L3-derivable (equality asserted); sort-id->Set sequence; implementation-level->obligated-parties mint; contributes-to-assurance->rmf@1; status->tombstone drop + successor replaces[] |
| `nist.catalog.groups[].controls[].props[].name` | 6,557 | L1 | label(plain)->label; zero-padded/sp800-53a->L3-derivable (equality asserted); sort-id->Set sequence; implementation-level->obligated-parties mint; contributes-to-assurance->rmf@1; status->tombstone drop + successor replaces[] |
| `nist.catalog.groups[].controls[].props[].ns` | 1,592 | L1 | label(plain)->label; zero-padded/sp800-53a->L3-derivable (equality asserted); sort-id->Set sequence; implementation-level->obligated-parties mint; contributes-to-assurance->rmf@1; status->tombstone drop + successor replaces[] |
| `nist.catalog.groups[].controls[].props[].value` | 6,557 | L1 | label(plain)->label; zero-padded/sp800-53a->L3-derivable (equality asserted); sort-id->Set sequence; implementation-level->obligated-parties mint; contributes-to-assurance->rmf@1; status->tombstone drop + successor replaces[] |
| `nist.catalog.groups[].controls[].title` | 1,196 | L1 | Requirement id (URI mint, dot form = corpus mapping endpoints) + title | withdrawn: dropped, lineage inverted |
| `nist.catalog.groups[].id` | 20 | L1 | family Set id/title (D21 nesting under root) |
| `nist.catalog.groups[].parts[].id` | 1 | L2 | pm overview part -> narrative@1 guidance on the pm family Set (language-tagged) |
| `nist.catalog.groups[].parts[].name` | 1 | L2 | pm overview part -> narrative@1 guidance on the pm family Set (language-tagged) |
| `nist.catalog.groups[].parts[].prose` | 1 | L2 | pm overview part -> narrative@1 guidance on the pm family Set (language-tagged) |
| `nist.catalog.groups[].parts[].title` | 1 | L2 | pm overview part -> narrative@1 guidance on the pm family Set (language-tagged) |
| `nist.catalog.groups[].props[].name` | 20 | L1 | family Set label |
| `nist.catalog.groups[].props[].value` | 20 | L1 | family Set label |
| `nist.catalog.groups[].title` | 20 | L1 | family Set id/title (D21 nesting under root) |
| `nist.catalog.metadata.last-modified` | 1 | L1 | bundle manifest / L0 provenance |
| `nist.catalog.metadata.links[].href` | 3 | L1 | bundle manifest / L0 provenance |
| `nist.catalog.metadata.links[].rel` | 3 | L1 | bundle manifest / L0 provenance |
| `nist.catalog.metadata.oscal-version` | 1 | L1 | bundle manifest / L0 provenance |
| `nist.catalog.metadata.parties[].addresses[].addr-lines[]` | 8 | L1 | bundle manifest / L0 provenance |
| `nist.catalog.metadata.parties[].addresses[].city` | 2 | L1 | bundle manifest / L0 provenance |
| `nist.catalog.metadata.parties[].addresses[].postal-code` | 2 | L1 | bundle manifest / L0 provenance |
| `nist.catalog.metadata.parties[].addresses[].state` | 2 | L1 | bundle manifest / L0 provenance |
| `nist.catalog.metadata.parties[].email-addresses[]` | 2 | L1 | bundle manifest / L0 provenance |
| `nist.catalog.metadata.parties[].name` | 2 | L1 | bundle manifest / L0 provenance |
| `nist.catalog.metadata.parties[].short-name` | 1 | L1 | bundle manifest / L0 provenance |
| `nist.catalog.metadata.parties[].type` | 2 | L1 | bundle manifest / L0 provenance |
| `nist.catalog.metadata.parties[].uuid` | 2 | L1 | bundle manifest / L0 provenance |
| `nist.catalog.metadata.props[].name` | 1 | L1 | bundle manifest / L0 provenance |
| `nist.catalog.metadata.props[].value` | 1 | L1 | bundle manifest / L0 provenance |
| `nist.catalog.metadata.responsible-parties[].party-uuids[]` | 4 | L1 | bundle manifest / L0 provenance |
| `nist.catalog.metadata.responsible-parties[].role-id` | 4 | L1 | bundle manifest / L0 provenance |
| `nist.catalog.metadata.revisions[].last-modified` | 7 | L1 | bundle manifest / L0 provenance |
| `nist.catalog.metadata.revisions[].links[].href` | 7 | L1 | bundle manifest / L0 provenance |
| `nist.catalog.metadata.revisions[].links[].rel` | 7 | L1 | bundle manifest / L0 provenance |
| `nist.catalog.metadata.revisions[].oscal-version` | 7 | L1 | bundle manifest / L0 provenance |
| `nist.catalog.metadata.revisions[].remarks` | 7 | L1 | bundle manifest / L0 provenance |
| `nist.catalog.metadata.revisions[].title` | 7 | L1 | bundle manifest / L0 provenance |
| `nist.catalog.metadata.revisions[].version` | 7 | L1 | bundle manifest / L0 provenance |
| `nist.catalog.metadata.roles[].id` | 4 | L1 | bundle manifest / L0 provenance |
| `nist.catalog.metadata.roles[].title` | 4 | L1 | bundle manifest / L0 provenance |
| `nist.catalog.metadata.title` | 1 | L1 | bundle manifest / L0 provenance |
| `nist.catalog.metadata.version` | 1 | L1 | bundle manifest / L0 provenance |
| `nist.catalog.uuid` | 1 | L1 | bundle manifest / L0 provenance |
| `privacy.profile.back-matter.resources[].description` | 1 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `privacy.profile.back-matter.resources[].rlinks[].href` | 3 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `privacy.profile.back-matter.resources[].rlinks[].media-type` | 3 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `privacy.profile.back-matter.resources[].uuid` | 1 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `privacy.profile.imports[].href` | 1 | L3 | OSCAL-profile resolution mechanics; the selection IS the Set (no semantic residue) |
| `privacy.profile.imports[].include-controls[].with-ids[]` | 96 | L1 | baseline Set members (minted URIs, catalog order) |
| `privacy.profile.merge.as-is` | 1 | L3 | OSCAL-profile resolution mechanics; the selection IS the Set (no semantic residue) |
| `privacy.profile.metadata.last-modified` | 1 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `privacy.profile.metadata.oscal-version` | 1 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `privacy.profile.metadata.parties[].addresses[].addr-lines[]` | 8 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `privacy.profile.metadata.parties[].addresses[].city` | 2 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `privacy.profile.metadata.parties[].addresses[].postal-code` | 2 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `privacy.profile.metadata.parties[].addresses[].state` | 2 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `privacy.profile.metadata.parties[].email-addresses[]` | 2 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `privacy.profile.metadata.parties[].name` | 2 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `privacy.profile.metadata.parties[].short-name` | 1 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `privacy.profile.metadata.parties[].type` | 2 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `privacy.profile.metadata.parties[].uuid` | 2 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `privacy.profile.metadata.responsible-parties[].party-uuids[]` | 4 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `privacy.profile.metadata.responsible-parties[].role-id` | 4 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `privacy.profile.metadata.roles[].id` | 4 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `privacy.profile.metadata.roles[].title` | 4 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `privacy.profile.metadata.title` | 1 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `privacy.profile.metadata.version` | 1 | L1 | bundle manifest / L0 provenance (baseline documents) |
| `privacy.profile.uuid` | 1 | L1 | bundle manifest / L0 provenance (baseline documents) |

## UNMAPPED (gate target: zero)

*(none)*
