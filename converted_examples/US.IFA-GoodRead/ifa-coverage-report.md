# IFA GoodRead lifecycle set -> Semantic Core: Coverage Report (computed)

Source: **OSCAL IFA GoodRead example set** (SSP v1.1.1 + AP + AR + POA&M) + leveraged/leveraging SSP pair + component-definition example (usnistgov/oscal-content; FICTIONAL example content by NIST). Census: `drafts/gate-3-census.md` §4.

## Totals

- Source leaf values inventoried: **835**
- Mapped (declared destination): **835**
- **UNMAPPED: 0**  ->  coverage **100.0 %**
- Objects emitted: 1 assessment, 1 attestation, 6 component, 2 finding, 3 impl, 2 req, 2 risk - the five lifecycle types and the Risk type (kernel 2.0.0) at document scale, manifest with both digests.
- Carried Requirements (closure): https://ns.nist.gov/sp800-53/req/AC-6.1, https://ns.nist.gov/sp800-53/req/AC-2 - byte-identical copies from the US.SP800-53 bundle; an authorization package carries its baseline.

## Conversion rules (declared, counted)

- **SSP -> Component + Implementation**: by-component -> capability + satisfied-by; 5 set-parameters bind the REAL minted AC-6.1 ODPs (unresolved bindings: ['ac-2_prm_1']).
- **date-authorized -> Component.authorizations + Attestation**: the ATO modeled as an attestation over {system Component, Implementation, AC-6.1} semantic digests; unsigned (envelope-ref absent) - signature verification is gate-4 (backlog #24).
- **Leveraged/leveraging pair -> D5 inheritance**: consumer Implementation satisfied-by inherited-from{csp-iaas, auth-csp-iaas-2018} - basis-ref names the provider Component's authorization (edge-local closure enforced by the validator); provider export.provided -> capabilities, export.responsibilities -> customer-responsibilities.
- **AR + AP -> one Assessment**: AP activities/steps ride Assessment.method (assessment-plan@1 payload); result not-satisfied from the finding target; observations (AR + POA&M, deduped by uuid) -> observations@1 facet + landmark evidence URIs.
- **POA&M risks -> Risk objects (CP-RISK-1, kernel 2.0.0)**: statement -> `scenario`; deadline -> `review-due` (datetime - OSCAL's type is date-time-with-timezone); POA&M system-id -> `component-refs`; response `type` prop -> `treatment` (observed: accept x1, mitigate x1); the AR finding's related-risks edge -> `treatments[]` (RISK-2 is modified by AC-6.1). likelihood/impact, the source status and the response narrative -> risk-analysis@1 (the L2 holding pen for the parked stdlib facet).
- **POA&M risks -> Findings**: RISK-2 (open + planned remediation) -> state in-remediation with actions[] (due = within-date-range.end); RISK-1 (status deviation-approved) -> approved `risk-adjustment` Deviation (rationale = mitigating factor, approver = the SCA division URI) whose `refs` name the Risk (RISK-9). Each Finding carries `risk-refs` to its Risk; the risk@1 framework facet is retired.
- **Finding target `ac-6.1_obj`** is a 53A OBJECTIVE id - it addresses into the sp800-53a@1 facet of the carried AC-6.1 (kept in finding-target@1.target-objective-id; kernel statement-ref stays statement-scoped).
- **Parties stay landmark** (#16, D22 0-of-3): performer/signer/approver are minted party URIs, no party objects.
- **Payload free text language-tagged**: ap x7, observation x4, risk x14, system x6.

## Findings (computed)

- **Statement-id respelling x2** (source finding): the SSP pair writes `ac-2_stmt.a` where the Rev 5 catalog writes `ac-2_smt.a` - same publisher, two spellings of the same address; normalized to the catalog form. REPORTED upstream.
- **PUA codepoints x1** (source finding): U+E0xx private-use characters embedded in IFA SSP prose (ligature artifacts, e.g. 'so\ue002ware') - carried verbatim, never patched. REPORTED upstream.
- **Placeholder uuids x4**: every export.provided/responsibility uuid in the leveraged pair is 11111111-... - the provided-uuid dereference is degenerate in source; inheritance wired via the authorization anchor instead.
- **Unresolved parameter bindings**: ['ac-2_prm_1'] - `ac-2_prm_1` is a Rev-5.1-era param id; Rev 5.2.0 declares the _odp layer instead (the binding is carried verbatim; a resolver follows the odp@1 aggregates map).
- **Kind mapping**: appliance->hardware x1 (OSCAL free-text component types vs. the kernel's closed componentKind).
- **Global occurrence (measured; path coverage above is a DECLARATION)**: 284 of 835 source leaf values have an equal value of the same type somewhere in the emitted objects. This is an **upper bound** on what was carried: all sources and all objects share one search space, so one output value satisfies every equal source value, and a value dropped in one place is hidden by an equal value in another. It does not trace an occurrence to its destination. Not counted: 29 values that equal only an output key and 80 that occur only inside a longer output text (candidates, to be argued per path). No equal value anywhere: 194 identity values (uuids/hrefs - re-minted as URIs by design), 125 document-metadata values, and **123 content values (63 of them prose of 40+ characters)** - each either transformed on purpose (a mapped code, a respelled id) or DROPPED. That list is a **lower bound** on the losses, not the complete work queue. `UNMAPPED: 0` sees none of this; the per-path lists, with the indexed pointer of every value, are in the JSON report (`global-occurrence`; backlog #41).
- **Conversion ledger (measured per source value)**: each of the 835 source leaf values has one entry in `ifa-conversion-ledger.json` saying where it went. **262 copied** (the value stands, with its type, at the destination named, read back from the written file), **33 transformed** (a named rule made the destination from it; the rule was applied to the source again and compared), **295 intentionally dropped** (a stated reason), **245 unaccounted**. Unlike the global figure above, an equal value elsewhere does not count: a value is traced by what the converter did with it. Checks that failed: 0. The unaccounted values are listed by path at the end of this report; they are the work queue of backlog #41.
- **What OSCAL cannot give the Risk shape** (model findings, REPORTED; nothing is invented - the one derived value is the owner): analysed in source (likelihood + impact) but no level: `assessed` unreachable (RISK-2) x2; owner absent in source (derived from the SSP `owner` role) x2; response `accept` without a dated acceptance: `retain` unreachable (RISK-6) x1. Owner source: the SSP `owner` role -> https://ifa.gov/goodread/party/owen-pearson.
- observation carried in both AR and POA&M (deduped): AwesomeCloud IAM Roles Test - SYSTEM1234 System Engineer Role

## Full path map (every source path, its count, its destination)

| path | count | level | destination |
|---|---:|---|---|
| `ap.assessment-plan.assessment-subjects[].description` | 1 | L2 | Assessment.method payload (assessment-plan@1): activities/steps/tasks/subjects/reviewed-controls |
| `ap.assessment-plan.assessment-subjects[].type` | 1 | L2 | Assessment.method payload (assessment-plan@1): activities/steps/tasks/subjects/reviewed-controls |
| `ap.assessment-plan.back-matter.resources[].remarks` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ap.assessment-plan.back-matter.resources[].rlinks[].href` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ap.assessment-plan.back-matter.resources[].rlinks[].media-type` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ap.assessment-plan.back-matter.resources[].title` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ap.assessment-plan.back-matter.resources[].uuid` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ap.assessment-plan.import-ssp.href` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ap.assessment-plan.local-definitions.activities[].description` | 1 | L2 | Assessment.method payload (assessment-plan@1): activities/steps/tasks/subjects/reviewed-controls |
| `ap.assessment-plan.local-definitions.activities[].props[].name` | 1 | L2 | Assessment.method payload (assessment-plan@1): activities/steps/tasks/subjects/reviewed-controls |
| `ap.assessment-plan.local-definitions.activities[].props[].value` | 1 | L2 | Assessment.method payload (assessment-plan@1): activities/steps/tasks/subjects/reviewed-controls |
| `ap.assessment-plan.local-definitions.activities[].related-controls.control-selections[].include-controls[].control-id` | 1 | L2 | Assessment.method payload (assessment-plan@1): activities/steps/tasks/subjects/reviewed-controls |
| `ap.assessment-plan.local-definitions.activities[].responsible-roles[].party-uuids[]` | 1 | L2 | Assessment.method payload (assessment-plan@1): activities/steps/tasks/subjects/reviewed-controls |
| `ap.assessment-plan.local-definitions.activities[].responsible-roles[].role-id` | 1 | L2 | Assessment.method payload (assessment-plan@1): activities/steps/tasks/subjects/reviewed-controls |
| `ap.assessment-plan.local-definitions.activities[].steps[].description` | 6 | L2 | Assessment.method payload (assessment-plan@1): activities/steps/tasks/subjects/reviewed-controls |
| `ap.assessment-plan.local-definitions.activities[].steps[].title` | 6 | L2 | Assessment.method payload (assessment-plan@1): activities/steps/tasks/subjects/reviewed-controls |
| `ap.assessment-plan.local-definitions.activities[].steps[].uuid` | 6 | L2 | Assessment.method payload (assessment-plan@1): activities/steps/tasks/subjects/reviewed-controls |
| `ap.assessment-plan.local-definitions.activities[].title` | 1 | L2 | Assessment.method payload (assessment-plan@1): activities/steps/tasks/subjects/reviewed-controls |
| `ap.assessment-plan.local-definitions.activities[].uuid` | 1 | L2 | Assessment.method payload (assessment-plan@1): activities/steps/tasks/subjects/reviewed-controls |
| `ap.assessment-plan.metadata.last-modified` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ap.assessment-plan.metadata.oscal-version` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ap.assessment-plan.metadata.parties[].links[].href` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ap.assessment-plan.metadata.parties[].links[].rel` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ap.assessment-plan.metadata.parties[].member-of-organizations[]` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ap.assessment-plan.metadata.parties[].name` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ap.assessment-plan.metadata.parties[].short-name` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ap.assessment-plan.metadata.parties[].type` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ap.assessment-plan.metadata.parties[].uuid` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ap.assessment-plan.metadata.published` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ap.assessment-plan.metadata.remarks` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ap.assessment-plan.metadata.responsible-parties[].party-uuids[]` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ap.assessment-plan.metadata.responsible-parties[].role-id` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ap.assessment-plan.metadata.revisions[].last-modified` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ap.assessment-plan.metadata.revisions[].links[].href` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ap.assessment-plan.metadata.revisions[].links[].rel` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ap.assessment-plan.metadata.revisions[].oscal-version` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ap.assessment-plan.metadata.revisions[].remarks` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ap.assessment-plan.metadata.revisions[].title` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ap.assessment-plan.metadata.revisions[].version` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ap.assessment-plan.metadata.roles[].id` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ap.assessment-plan.metadata.roles[].title` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ap.assessment-plan.metadata.title` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ap.assessment-plan.metadata.version` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ap.assessment-plan.reviewed-controls.control-selections[].include-controls[].control-id` | 1 | L2 | Assessment.method payload (assessment-plan@1): activities/steps/tasks/subjects/reviewed-controls |
| `ap.assessment-plan.tasks[].associated-activities[].activity-uuid` | 1 | L2 | Assessment.method payload (assessment-plan@1): activities/steps/tasks/subjects/reviewed-controls |
| `ap.assessment-plan.tasks[].associated-activities[].subjects[].type` | 1 | L2 | Assessment.method payload (assessment-plan@1): activities/steps/tasks/subjects/reviewed-controls |
| `ap.assessment-plan.tasks[].remarks` | 1 | L2 | Assessment.method payload (assessment-plan@1): activities/steps/tasks/subjects/reviewed-controls |
| `ap.assessment-plan.tasks[].responsible-roles[].role-id` | 1 | L2 | Assessment.method payload (assessment-plan@1): activities/steps/tasks/subjects/reviewed-controls |
| `ap.assessment-plan.tasks[].title` | 1 | L2 | Assessment.method payload (assessment-plan@1): activities/steps/tasks/subjects/reviewed-controls |
| `ap.assessment-plan.tasks[].type` | 1 | L2 | Assessment.method payload (assessment-plan@1): activities/steps/tasks/subjects/reviewed-controls |
| `ap.assessment-plan.tasks[].uuid` | 1 | L2 | Assessment.method payload (assessment-plan@1): activities/steps/tasks/subjects/reviewed-controls |
| `ap.assessment-plan.uuid` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ar.assessment-results.back-matter.resources[].rlinks[].href` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ar.assessment-results.back-matter.resources[].rlinks[].media-type` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ar.assessment-results.back-matter.resources[].title` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ar.assessment-results.back-matter.resources[].uuid` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ar.assessment-results.import-ap.href` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ar.assessment-results.local-definitions.activities[].description` | 1 | L2 | Assessment.method payload (activities duplicated from AP; carried once) |
| `ar.assessment-results.local-definitions.activities[].props[].name` | 1 | L2 | Assessment.method payload (activities duplicated from AP; carried once) |
| `ar.assessment-results.local-definitions.activities[].props[].value` | 1 | L2 | Assessment.method payload (activities duplicated from AP; carried once) |
| `ar.assessment-results.local-definitions.activities[].related-controls.control-selections[].include-controls[].control-id` | 1 | L2 | Assessment.method payload (activities duplicated from AP; carried once) |
| `ar.assessment-results.local-definitions.activities[].responsible-roles[].party-uuids[]` | 1 | L2 | Assessment.method payload (activities duplicated from AP; carried once) |
| `ar.assessment-results.local-definitions.activities[].responsible-roles[].role-id` | 1 | L2 | Assessment.method payload (activities duplicated from AP; carried once) |
| `ar.assessment-results.local-definitions.activities[].steps[].description` | 3 | L2 | Assessment.method payload (activities duplicated from AP; carried once) |
| `ar.assessment-results.local-definitions.activities[].steps[].remarks` | 2 | L2 | Assessment.method payload (activities duplicated from AP; carried once) |
| `ar.assessment-results.local-definitions.activities[].steps[].title` | 3 | L2 | Assessment.method payload (activities duplicated from AP; carried once) |
| `ar.assessment-results.local-definitions.activities[].steps[].uuid` | 3 | L2 | Assessment.method payload (activities duplicated from AP; carried once) |
| `ar.assessment-results.local-definitions.activities[].title` | 1 | L2 | Assessment.method payload (activities duplicated from AP; carried once) |
| `ar.assessment-results.local-definitions.activities[].uuid` | 1 | L2 | Assessment.method payload (activities duplicated from AP; carried once) |
| `ar.assessment-results.metadata.last-modified` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ar.assessment-results.metadata.oscal-version` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ar.assessment-results.metadata.parties[].links[].href` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ar.assessment-results.metadata.parties[].links[].rel` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ar.assessment-results.metadata.parties[].member-of-organizations[]` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ar.assessment-results.metadata.parties[].name` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ar.assessment-results.metadata.parties[].short-name` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ar.assessment-results.metadata.parties[].type` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ar.assessment-results.metadata.parties[].uuid` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ar.assessment-results.metadata.remarks` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ar.assessment-results.metadata.responsible-parties[].party-uuids[]` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ar.assessment-results.metadata.responsible-parties[].role-id` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ar.assessment-results.metadata.revisions[].last-modified` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ar.assessment-results.metadata.revisions[].links[].href` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ar.assessment-results.metadata.revisions[].links[].rel` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ar.assessment-results.metadata.revisions[].oscal-version` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ar.assessment-results.metadata.revisions[].remarks` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ar.assessment-results.metadata.revisions[].title` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ar.assessment-results.metadata.revisions[].version` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ar.assessment-results.metadata.roles[].id` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ar.assessment-results.metadata.roles[].title` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ar.assessment-results.metadata.title` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ar.assessment-results.metadata.version` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ar.assessment-results.results[].description` | 1 | L1 | Assessment id/title/time |
| `ar.assessment-results.results[].end` | 1 | L1 | Assessment id/title/time |
| `ar.assessment-results.results[].findings[].description` | 1 | L1 | Finding: target.status -> Assessment result + Finding state; target-id (53A objective) + implementation-statement-uuid -> finding-target@1 facet; related-risks -> Risk.treatments (the risk -> control edge) |
| `ar.assessment-results.results[].findings[].implementation-statement-uuid` | 1 | L1 | Finding: target.status -> Assessment result + Finding state; target-id (53A objective) + implementation-statement-uuid -> finding-target@1 facet; related-risks -> Risk.treatments (the risk -> control edge) |
| `ar.assessment-results.results[].findings[].related-observations[].observation-uuid` | 1 | L1 | Finding: target.status -> Assessment result + Finding state; target-id (53A objective) + implementation-statement-uuid -> finding-target@1 facet; related-risks -> Risk.treatments (the risk -> control edge) |
| `ar.assessment-results.results[].findings[].related-risks[].risk-uuid` | 1 | L1 | Finding: target.status -> Assessment result + Finding state; target-id (53A objective) + implementation-statement-uuid -> finding-target@1 facet; related-risks -> Risk.treatments (the risk -> control edge) |
| `ar.assessment-results.results[].findings[].target.description` | 1 | L1 | Finding: target.status -> Assessment result + Finding state; target-id (53A objective) + implementation-statement-uuid -> finding-target@1 facet; related-risks -> Risk.treatments (the risk -> control edge) |
| `ar.assessment-results.results[].findings[].target.status.state` | 1 | L1 | Finding: target.status -> Assessment result + Finding state; target-id (53A objective) + implementation-statement-uuid -> finding-target@1 facet; related-risks -> Risk.treatments (the risk -> control edge) |
| `ar.assessment-results.results[].findings[].target.target-id` | 1 | L1 | Finding: target.status -> Assessment result + Finding state; target-id (53A objective) + implementation-statement-uuid -> finding-target@1 facet; related-risks -> Risk.treatments (the risk -> control edge) |
| `ar.assessment-results.results[].findings[].target.type` | 1 | L1 | Finding: target.status -> Assessment result + Finding state; target-id (53A objective) + implementation-statement-uuid -> finding-target@1 facet; related-risks -> Risk.treatments (the risk -> control edge) |
| `ar.assessment-results.results[].findings[].title` | 1 | L1 | Finding: target.status -> Assessment result + Finding state; target-id (53A objective) + implementation-statement-uuid -> finding-target@1 facet; related-risks -> Risk.treatments (the risk -> control edge) |
| `ar.assessment-results.results[].findings[].uuid` | 1 | L1 | Finding: target.status -> Assessment result + Finding state; target-id (53A objective) + implementation-statement-uuid -> finding-target@1 facet; related-risks -> Risk.treatments (the risk -> control edge) |
| `ar.assessment-results.results[].local-definitions.tasks[].associated-activities[].activity-uuid` | 1 | L1 | risk content consolidated with the POA&M risks (same risk graph, later state) |
| `ar.assessment-results.results[].local-definitions.tasks[].associated-activities[].subjects[].type` | 1 | L1 | risk content consolidated with the POA&M risks (same risk graph, later state) |
| `ar.assessment-results.results[].local-definitions.tasks[].description` | 1 | L1 | risk content consolidated with the POA&M risks (same risk graph, later state) |
| `ar.assessment-results.results[].local-definitions.tasks[].title` | 1 | L1 | risk content consolidated with the POA&M risks (same risk graph, later state) |
| `ar.assessment-results.results[].local-definitions.tasks[].type` | 1 | L1 | risk content consolidated with the POA&M risks (same risk graph, later state) |
| `ar.assessment-results.results[].local-definitions.tasks[].uuid` | 1 | L1 | risk content consolidated with the POA&M risks (same risk graph, later state) |
| `ar.assessment-results.results[].observations[].collected` | 2 | L1 | observations@1 facet + landmark evidence URIs (methods/types/collected/expires carried) |
| `ar.assessment-results.results[].observations[].description` | 2 | L1 | observations@1 facet + landmark evidence URIs (methods/types/collected/expires carried) |
| `ar.assessment-results.results[].observations[].expires` | 2 | L1 | observations@1 facet + landmark evidence URIs (methods/types/collected/expires carried) |
| `ar.assessment-results.results[].observations[].methods[]` | 2 | L1 | observations@1 facet + landmark evidence URIs (methods/types/collected/expires carried) |
| `ar.assessment-results.results[].observations[].remarks` | 2 | L1 | observations@1 facet + landmark evidence URIs (methods/types/collected/expires carried) |
| `ar.assessment-results.results[].observations[].subjects[].subject-uuid` | 2 | L1 | observations@1 facet + landmark evidence URIs (methods/types/collected/expires carried) |
| `ar.assessment-results.results[].observations[].subjects[].type` | 2 | L1 | observations@1 facet + landmark evidence URIs (methods/types/collected/expires carried) |
| `ar.assessment-results.results[].observations[].title` | 2 | L1 | observations@1 facet + landmark evidence URIs (methods/types/collected/expires carried) |
| `ar.assessment-results.results[].observations[].types[]` | 2 | L1 | observations@1 facet + landmark evidence URIs (methods/types/collected/expires carried) |
| `ar.assessment-results.results[].observations[].uuid` | 2 | L1 | observations@1 facet + landmark evidence URIs (methods/types/collected/expires carried) |
| `ar.assessment-results.results[].reviewed-controls.control-selections[].include-controls[].control-id` | 1 | L1 | Assessment subject-refs |
| `ar.assessment-results.results[].risks[].description` | 1 | L1 | risk content consolidated with the POA&M risks (same risk graph, later state) |
| `ar.assessment-results.results[].risks[].statement` | 1 | L1 | risk content consolidated with the POA&M risks (same risk graph, later state) |
| `ar.assessment-results.results[].risks[].status` | 1 | L1 | risk content consolidated with the POA&M risks (same risk graph, later state) |
| `ar.assessment-results.results[].risks[].title` | 1 | L1 | risk content consolidated with the POA&M risks (same risk graph, later state) |
| `ar.assessment-results.results[].risks[].uuid` | 1 | L1 | risk content consolidated with the POA&M risks (same risk graph, later state) |
| `ar.assessment-results.results[].start` | 1 | L1 | Assessment id/title/time |
| `ar.assessment-results.results[].title` | 1 | L1 | Assessment id/title/time |
| `ar.assessment-results.results[].uuid` | 1 | L1 | Assessment id/title/time |
| `ar.assessment-results.uuid` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `cdef.component-definition.back-matter.resources[].description` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `cdef.component-definition.back-matter.resources[].rlinks[].href` | 3 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `cdef.component-definition.back-matter.resources[].rlinks[].media-type` | 3 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `cdef.component-definition.back-matter.resources[].uuid` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `cdef.component-definition.components[].control-implementations[].description` | 1 | L1 | capabilities with requirement-ref (landmark - the component asserts support, no system binds it) |
| `cdef.component-definition.components[].control-implementations[].implemented-requirements[].control-id` | 3 | L1 | capabilities with requirement-ref (landmark - the component asserts support, no system binds it) |
| `cdef.component-definition.components[].control-implementations[].implemented-requirements[].description` | 3 | L1 | capabilities with requirement-ref (landmark - the component asserts support, no system binds it) |
| `cdef.component-definition.components[].control-implementations[].implemented-requirements[].set-parameters[].param-id` | 2 | L1 | capabilities with requirement-ref (landmark - the component asserts support, no system binds it) |
| `cdef.component-definition.components[].control-implementations[].implemented-requirements[].set-parameters[].values[]` | 2 | L1 | capabilities with requirement-ref (landmark - the component asserts support, no system binds it) |
| `cdef.component-definition.components[].control-implementations[].implemented-requirements[].statements[].description` | 2 | L1 | capabilities with requirement-ref (landmark - the component asserts support, no system binds it) |
| `cdef.component-definition.components[].control-implementations[].implemented-requirements[].statements[].responsible-roles[].role-id` | 1 | L1 | capabilities with requirement-ref (landmark - the component asserts support, no system binds it) |
| `cdef.component-definition.components[].control-implementations[].implemented-requirements[].statements[].statement-id` | 2 | L1 | capabilities with requirement-ref (landmark - the component asserts support, no system binds it) |
| `cdef.component-definition.components[].control-implementations[].implemented-requirements[].statements[].uuid` | 2 | L1 | capabilities with requirement-ref (landmark - the component asserts support, no system binds it) |
| `cdef.component-definition.components[].control-implementations[].implemented-requirements[].uuid` | 3 | L1 | capabilities with requirement-ref (landmark - the component asserts support, no system binds it) |
| `cdef.component-definition.components[].control-implementations[].source` | 1 | L1 | capabilities with requirement-ref (landmark - the component asserts support, no system binds it) |
| `cdef.component-definition.components[].control-implementations[].uuid` | 1 | L1 | capabilities with requirement-ref (landmark - the component asserts support, no system binds it) |
| `cdef.component-definition.components[].description` | 1 | L1 | Component (kind mapped) id/title |
| `cdef.component-definition.components[].protocols[].name` | 3 | L2 | protocols@1 facet |
| `cdef.component-definition.components[].protocols[].port-ranges[].end` | 3 | L2 | protocols@1 facet |
| `cdef.component-definition.components[].protocols[].port-ranges[].start` | 3 | L2 | protocols@1 facet |
| `cdef.component-definition.components[].protocols[].port-ranges[].transport` | 3 | L2 | protocols@1 facet |
| `cdef.component-definition.components[].protocols[].title` | 3 | L2 | protocols@1 facet |
| `cdef.component-definition.components[].protocols[].uuid` | 3 | L2 | protocols@1 facet |
| `cdef.component-definition.components[].purpose` | 1 | L1 | Component (kind mapped) id/title |
| `cdef.component-definition.components[].responsible-roles[].party-uuids[]` | 1 | L1 | landmark party URIs (#16: parties stay landmark; roles ride provenance) |
| `cdef.component-definition.components[].responsible-roles[].role-id` | 2 | L1 | landmark party URIs (#16: parties stay landmark; roles ride provenance) |
| `cdef.component-definition.components[].title` | 1 | L1 | Component (kind mapped) id/title |
| `cdef.component-definition.components[].type` | 1 | L1 | Component (kind mapped) id/title |
| `cdef.component-definition.components[].uuid` | 1 | L1 | Component (kind mapped) id/title |
| `cdef.component-definition.metadata.last-modified` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `cdef.component-definition.metadata.oscal-version` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `cdef.component-definition.metadata.parties[].links[].href` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `cdef.component-definition.metadata.parties[].links[].rel` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `cdef.component-definition.metadata.parties[].name` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `cdef.component-definition.metadata.parties[].type` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `cdef.component-definition.metadata.parties[].uuid` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `cdef.component-definition.metadata.published` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `cdef.component-definition.metadata.roles[].id` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `cdef.component-definition.metadata.roles[].title` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `cdef.component-definition.metadata.title` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `cdef.component-definition.metadata.version` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `cdef.component-definition.uuid` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `lev.system-security-plan.back-matter.resources[].description` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `lev.system-security-plan.back-matter.resources[].rlinks[].href` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `lev.system-security-plan.back-matter.resources[].rlinks[].media-type` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `lev.system-security-plan.back-matter.resources[].uuid` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `lev.system-security-plan.control-implementation.description` | 1 | L1 | provider Implementation: export.provided -> capabilities (consumer-inheritable), export.responsibilities -> system@1 customer-responsibilities; statement ids respelled _stmt.->smt. (counted) |
| `lev.system-security-plan.control-implementation.implemented-requirements[].control-id` | 1 | L1 | provider Implementation: export.provided -> capabilities (consumer-inheritable), export.responsibilities -> system@1 customer-responsibilities; statement ids respelled _stmt.->smt. (counted) |
| `lev.system-security-plan.control-implementation.implemented-requirements[].remarks` | 1 | L1 | provider Implementation: export.provided -> capabilities (consumer-inheritable), export.responsibilities -> system@1 customer-responsibilities; statement ids respelled _stmt.->smt. (counted) |
| `lev.system-security-plan.control-implementation.implemented-requirements[].set-parameters[].param-id` | 1 | L1 | provider Implementation: export.provided -> capabilities (consumer-inheritable), export.responsibilities -> system@1 customer-responsibilities; statement ids respelled _stmt.->smt. (counted) |
| `lev.system-security-plan.control-implementation.implemented-requirements[].set-parameters[].values[]` | 1 | L1 | provider Implementation: export.provided -> capabilities (consumer-inheritable), export.responsibilities -> system@1 customer-responsibilities; statement ids respelled _stmt.->smt. (counted) |
| `lev.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].component-uuid` | 2 | L1 | provider Implementation: export.provided -> capabilities (consumer-inheritable), export.responsibilities -> system@1 customer-responsibilities; statement ids respelled _stmt.->smt. (counted) |
| `lev.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].description` | 2 | L1 | provider Implementation: export.provided -> capabilities (consumer-inheritable), export.responsibilities -> system@1 customer-responsibilities; statement ids respelled _stmt.->smt. (counted) |
| `lev.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].export.description` | 2 | L1 | provider Implementation: export.provided -> capabilities (consumer-inheritable), export.responsibilities -> system@1 customer-responsibilities; statement ids respelled _stmt.->smt. (counted) |
| `lev.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].export.provided[].description` | 2 | L1 | provider Implementation: export.provided -> capabilities (consumer-inheritable), export.responsibilities -> system@1 customer-responsibilities; statement ids respelled _stmt.->smt. (counted) |
| `lev.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].export.provided[].responsible-roles[].party-uuids[]` | 2 | L1 | provider Implementation: export.provided -> capabilities (consumer-inheritable), export.responsibilities -> system@1 customer-responsibilities; statement ids respelled _stmt.->smt. (counted) |
| `lev.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].export.provided[].responsible-roles[].role-id` | 2 | L1 | provider Implementation: export.provided -> capabilities (consumer-inheritable), export.responsibilities -> system@1 customer-responsibilities; statement ids respelled _stmt.->smt. (counted) |
| `lev.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].export.provided[].uuid` | 2 | L1 | provider Implementation: export.provided -> capabilities (consumer-inheritable), export.responsibilities -> system@1 customer-responsibilities; statement ids respelled _stmt.->smt. (counted) |
| `lev.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].export.responsibilities[].description` | 2 | L1 | provider Implementation: export.provided -> capabilities (consumer-inheritable), export.responsibilities -> system@1 customer-responsibilities; statement ids respelled _stmt.->smt. (counted) |
| `lev.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].export.responsibilities[].provided-uuid` | 2 | L1 | provider Implementation: export.provided -> capabilities (consumer-inheritable), export.responsibilities -> system@1 customer-responsibilities; statement ids respelled _stmt.->smt. (counted) |
| `lev.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].export.responsibilities[].responsible-roles[].party-uuids[]` | 2 | L1 | provider Implementation: export.provided -> capabilities (consumer-inheritable), export.responsibilities -> system@1 customer-responsibilities; statement ids respelled _stmt.->smt. (counted) |
| `lev.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].export.responsibilities[].responsible-roles[].role-id` | 2 | L1 | provider Implementation: export.provided -> capabilities (consumer-inheritable), export.responsibilities -> system@1 customer-responsibilities; statement ids respelled _stmt.->smt. (counted) |
| `lev.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].export.responsibilities[].uuid` | 2 | L1 | provider Implementation: export.provided -> capabilities (consumer-inheritable), export.responsibilities -> system@1 customer-responsibilities; statement ids respelled _stmt.->smt. (counted) |
| `lev.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].uuid` | 2 | L1 | provider Implementation: export.provided -> capabilities (consumer-inheritable), export.responsibilities -> system@1 customer-responsibilities; statement ids respelled _stmt.->smt. (counted) |
| `lev.system-security-plan.control-implementation.implemented-requirements[].statements[].remarks` | 1 | L1 | provider Implementation: export.provided -> capabilities (consumer-inheritable), export.responsibilities -> system@1 customer-responsibilities; statement ids respelled _stmt.->smt. (counted) |
| `lev.system-security-plan.control-implementation.implemented-requirements[].statements[].statement-id` | 1 | L1 | provider Implementation: export.provided -> capabilities (consumer-inheritable), export.responsibilities -> system@1 customer-responsibilities; statement ids respelled _stmt.->smt. (counted) |
| `lev.system-security-plan.control-implementation.implemented-requirements[].statements[].uuid` | 1 | L1 | provider Implementation: export.provided -> capabilities (consumer-inheritable), export.responsibilities -> system@1 customer-responsibilities; statement ids respelled _stmt.->smt. (counted) |
| `lev.system-security-plan.control-implementation.implemented-requirements[].uuid` | 1 | L1 | provider Implementation: export.provided -> capabilities (consumer-inheritable), export.responsibilities -> system@1 customer-responsibilities; statement ids respelled _stmt.->smt. (counted) |
| `lev.system-security-plan.import-profile.href` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `lev.system-security-plan.metadata.last-modified` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `lev.system-security-plan.metadata.oscal-version` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `lev.system-security-plan.metadata.parties[].remarks` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `lev.system-security-plan.metadata.parties[].type` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `lev.system-security-plan.metadata.parties[].uuid` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `lev.system-security-plan.metadata.published` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `lev.system-security-plan.metadata.roles[].id` | 3 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `lev.system-security-plan.metadata.roles[].title` | 3 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `lev.system-security-plan.metadata.title` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `lev.system-security-plan.metadata.version` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `lev.system-security-plan.system-characteristics.authorization-boundary.description` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lev.system-security-plan.system-characteristics.description` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lev.system-security-plan.system-characteristics.remarks` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lev.system-security-plan.system-characteristics.security-impact-level.security-objective-availability` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lev.system-security-plan.system-characteristics.security-impact-level.security-objective-confidentiality` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lev.system-security-plan.system-characteristics.security-impact-level.security-objective-integrity` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lev.system-security-plan.system-characteristics.security-sensitivity-level` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lev.system-security-plan.system-characteristics.status.state` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lev.system-security-plan.system-characteristics.system-ids[].id` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lev.system-security-plan.system-characteristics.system-information.information-types[].availability-impact.adjustment-justification` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lev.system-security-plan.system-characteristics.system-information.information-types[].availability-impact.base` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lev.system-security-plan.system-characteristics.system-information.information-types[].availability-impact.selected` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lev.system-security-plan.system-characteristics.system-information.information-types[].categorizations[].information-type-ids[]` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lev.system-security-plan.system-characteristics.system-information.information-types[].categorizations[].system` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lev.system-security-plan.system-characteristics.system-information.information-types[].confidentiality-impact.adjustment-justification` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lev.system-security-plan.system-characteristics.system-information.information-types[].confidentiality-impact.base` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lev.system-security-plan.system-characteristics.system-information.information-types[].confidentiality-impact.selected` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lev.system-security-plan.system-characteristics.system-information.information-types[].description` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lev.system-security-plan.system-characteristics.system-information.information-types[].integrity-impact.adjustment-justification` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lev.system-security-plan.system-characteristics.system-information.information-types[].integrity-impact.base` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lev.system-security-plan.system-characteristics.system-information.information-types[].integrity-impact.selected` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lev.system-security-plan.system-characteristics.system-information.information-types[].title` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lev.system-security-plan.system-characteristics.system-information.information-types[].uuid` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lev.system-security-plan.system-characteristics.system-name` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lev.system-security-plan.system-implementation.components[].description` | 2 | L1 | Components (kind mapped: appliance->hardware, application->software) |
| `lev.system-security-plan.system-implementation.components[].props[].name` | 1 | L1 | Components (kind mapped: appliance->hardware, application->software) |
| `lev.system-security-plan.system-implementation.components[].props[].value` | 1 | L1 | Components (kind mapped: appliance->hardware, application->software) |
| `lev.system-security-plan.system-implementation.components[].responsible-roles[].party-uuids[]` | 1 | L1 | Components (kind mapped: appliance->hardware, application->software) |
| `lev.system-security-plan.system-implementation.components[].responsible-roles[].role-id` | 1 | L1 | Components (kind mapped: appliance->hardware, application->software) |
| `lev.system-security-plan.system-implementation.components[].status.state` | 2 | L1 | Components (kind mapped: appliance->hardware, application->software) |
| `lev.system-security-plan.system-implementation.components[].title` | 2 | L1 | Components (kind mapped: appliance->hardware, application->software) |
| `lev.system-security-plan.system-implementation.components[].type` | 2 | L1 | Components (kind mapped: appliance->hardware, application->software) |
| `lev.system-security-plan.system-implementation.components[].uuid` | 2 | L1 | Components (kind mapped: appliance->hardware, application->software) |
| `lev.system-security-plan.system-implementation.users[].authorized-privileges[].functions-performed[]` | 1 | L2 | system@1 facet users[] |
| `lev.system-security-plan.system-implementation.users[].authorized-privileges[].title` | 1 | L2 | system@1 facet users[] |
| `lev.system-security-plan.system-implementation.users[].role-ids[]` | 1 | L2 | system@1 facet users[] |
| `lev.system-security-plan.system-implementation.users[].uuid` | 1 | L2 | system@1 facet users[] |
| `lev.system-security-plan.uuid` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `lvg.system-security-plan.back-matter.resources[].description` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `lvg.system-security-plan.back-matter.resources[].rlinks[].href` | 5 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `lvg.system-security-plan.back-matter.resources[].rlinks[].media-type` | 4 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `lvg.system-security-plan.back-matter.resources[].uuid` | 3 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `lvg.system-security-plan.control-implementation.description` | 1 | L1 | consumer Implementation: inherited -> satisfied-by inherited-from{component, basis-ref} (D5), satisfied -> consumer capability; responsibility shared |
| `lvg.system-security-plan.control-implementation.implemented-requirements[].control-id` | 1 | L1 | consumer Implementation: inherited -> satisfied-by inherited-from{component, basis-ref} (D5), satisfied -> consumer capability; responsibility shared |
| `lvg.system-security-plan.control-implementation.implemented-requirements[].remarks` | 1 | L1 | consumer Implementation: inherited -> satisfied-by inherited-from{component, basis-ref} (D5), satisfied -> consumer capability; responsibility shared |
| `lvg.system-security-plan.control-implementation.implemented-requirements[].set-parameters[].param-id` | 1 | L1 | consumer Implementation: inherited -> satisfied-by inherited-from{component, basis-ref} (D5), satisfied -> consumer capability; responsibility shared |
| `lvg.system-security-plan.control-implementation.implemented-requirements[].set-parameters[].values[]` | 1 | L1 | consumer Implementation: inherited -> satisfied-by inherited-from{component, basis-ref} (D5), satisfied -> consumer capability; responsibility shared |
| `lvg.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].component-uuid` | 3 | L1 | consumer Implementation: inherited -> satisfied-by inherited-from{component, basis-ref} (D5), satisfied -> consumer capability; responsibility shared |
| `lvg.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].description` | 3 | L1 | consumer Implementation: inherited -> satisfied-by inherited-from{component, basis-ref} (D5), satisfied -> consumer capability; responsibility shared |
| `lvg.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].inherited[].description` | 1 | L1 | consumer Implementation: inherited -> satisfied-by inherited-from{component, basis-ref} (D5), satisfied -> consumer capability; responsibility shared |
| `lvg.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].inherited[].provided-uuid` | 1 | L1 | consumer Implementation: inherited -> satisfied-by inherited-from{component, basis-ref} (D5), satisfied -> consumer capability; responsibility shared |
| `lvg.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].inherited[].uuid` | 1 | L1 | consumer Implementation: inherited -> satisfied-by inherited-from{component, basis-ref} (D5), satisfied -> consumer capability; responsibility shared |
| `lvg.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].responsible-roles[].party-uuids[]` | 1 | L1 | consumer Implementation: inherited -> satisfied-by inherited-from{component, basis-ref} (D5), satisfied -> consumer capability; responsibility shared |
| `lvg.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].responsible-roles[].role-id` | 1 | L1 | consumer Implementation: inherited -> satisfied-by inherited-from{component, basis-ref} (D5), satisfied -> consumer capability; responsibility shared |
| `lvg.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].satisfied[].description` | 2 | L1 | consumer Implementation: inherited -> satisfied-by inherited-from{component, basis-ref} (D5), satisfied -> consumer capability; responsibility shared |
| `lvg.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].satisfied[].responsibility-uuid` | 2 | L1 | consumer Implementation: inherited -> satisfied-by inherited-from{component, basis-ref} (D5), satisfied -> consumer capability; responsibility shared |
| `lvg.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].satisfied[].responsible-roles[].party-uuids[]` | 1 | L1 | consumer Implementation: inherited -> satisfied-by inherited-from{component, basis-ref} (D5), satisfied -> consumer capability; responsibility shared |
| `lvg.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].satisfied[].responsible-roles[].role-id` | 1 | L1 | consumer Implementation: inherited -> satisfied-by inherited-from{component, basis-ref} (D5), satisfied -> consumer capability; responsibility shared |
| `lvg.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].satisfied[].uuid` | 2 | L1 | consumer Implementation: inherited -> satisfied-by inherited-from{component, basis-ref} (D5), satisfied -> consumer capability; responsibility shared |
| `lvg.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].uuid` | 3 | L1 | consumer Implementation: inherited -> satisfied-by inherited-from{component, basis-ref} (D5), satisfied -> consumer capability; responsibility shared |
| `lvg.system-security-plan.control-implementation.implemented-requirements[].statements[].remarks` | 1 | L1 | consumer Implementation: inherited -> satisfied-by inherited-from{component, basis-ref} (D5), satisfied -> consumer capability; responsibility shared |
| `lvg.system-security-plan.control-implementation.implemented-requirements[].statements[].statement-id` | 1 | L1 | consumer Implementation: inherited -> satisfied-by inherited-from{component, basis-ref} (D5), satisfied -> consumer capability; responsibility shared |
| `lvg.system-security-plan.control-implementation.implemented-requirements[].statements[].uuid` | 1 | L1 | consumer Implementation: inherited -> satisfied-by inherited-from{component, basis-ref} (D5), satisfied -> consumer capability; responsibility shared |
| `lvg.system-security-plan.control-implementation.implemented-requirements[].uuid` | 1 | L1 | consumer Implementation: inherited -> satisfied-by inherited-from{component, basis-ref} (D5), satisfied -> consumer capability; responsibility shared |
| `lvg.system-security-plan.import-profile.href` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `lvg.system-security-plan.metadata.last-modified` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `lvg.system-security-plan.metadata.oscal-version` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `lvg.system-security-plan.metadata.parties[].remarks` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `lvg.system-security-plan.metadata.parties[].type` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `lvg.system-security-plan.metadata.parties[].uuid` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `lvg.system-security-plan.metadata.published` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `lvg.system-security-plan.metadata.roles[].id` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `lvg.system-security-plan.metadata.roles[].title` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `lvg.system-security-plan.metadata.title` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `lvg.system-security-plan.metadata.version` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `lvg.system-security-plan.system-characteristics.authorization-boundary.description` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lvg.system-security-plan.system-characteristics.description` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lvg.system-security-plan.system-characteristics.remarks` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lvg.system-security-plan.system-characteristics.security-impact-level.security-objective-availability` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lvg.system-security-plan.system-characteristics.security-impact-level.security-objective-confidentiality` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lvg.system-security-plan.system-characteristics.security-impact-level.security-objective-integrity` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lvg.system-security-plan.system-characteristics.security-sensitivity-level` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lvg.system-security-plan.system-characteristics.status.state` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lvg.system-security-plan.system-characteristics.system-ids[].id` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lvg.system-security-plan.system-characteristics.system-information.information-types[].availability-impact.adjustment-justification` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lvg.system-security-plan.system-characteristics.system-information.information-types[].availability-impact.base` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lvg.system-security-plan.system-characteristics.system-information.information-types[].availability-impact.selected` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lvg.system-security-plan.system-characteristics.system-information.information-types[].categorizations[].information-type-ids[]` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lvg.system-security-plan.system-characteristics.system-information.information-types[].categorizations[].system` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lvg.system-security-plan.system-characteristics.system-information.information-types[].confidentiality-impact.adjustment-justification` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lvg.system-security-plan.system-characteristics.system-information.information-types[].confidentiality-impact.base` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lvg.system-security-plan.system-characteristics.system-information.information-types[].confidentiality-impact.selected` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lvg.system-security-plan.system-characteristics.system-information.information-types[].description` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lvg.system-security-plan.system-characteristics.system-information.information-types[].integrity-impact.adjustment-justification` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lvg.system-security-plan.system-characteristics.system-information.information-types[].integrity-impact.base` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lvg.system-security-plan.system-characteristics.system-information.information-types[].integrity-impact.selected` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lvg.system-security-plan.system-characteristics.system-information.information-types[].title` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lvg.system-security-plan.system-characteristics.system-information.information-types[].uuid` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lvg.system-security-plan.system-characteristics.system-name` | 1 | L1 | provider/consumer Components: system@1 facet (description, FIPS-199 carried) |
| `lvg.system-security-plan.system-implementation.components[].description` | 4 | L1 | Components (kind mapped: appliance->hardware, application->software) |
| `lvg.system-security-plan.system-implementation.components[].props[].name` | 8 | L1 | Components (kind mapped: appliance->hardware, application->software) |
| `lvg.system-security-plan.system-implementation.components[].props[].value` | 8 | L1 | Components (kind mapped: appliance->hardware, application->software) |
| `lvg.system-security-plan.system-implementation.components[].status.state` | 4 | L1 | Components (kind mapped: appliance->hardware, application->software) |
| `lvg.system-security-plan.system-implementation.components[].title` | 4 | L1 | Components (kind mapped: appliance->hardware, application->software) |
| `lvg.system-security-plan.system-implementation.components[].type` | 4 | L1 | Components (kind mapped: appliance->hardware, application->software) |
| `lvg.system-security-plan.system-implementation.components[].uuid` | 4 | L1 | Components (kind mapped: appliance->hardware, application->software) |
| `lvg.system-security-plan.system-implementation.leveraged-authorizations[].date-authorized` | 1 | L1 | leveraged-authorizations -> provider Component authorizations[] (the basis-ref anchor); users -> system@1 |
| `lvg.system-security-plan.system-implementation.leveraged-authorizations[].links[].href` | 1 | L1 | leveraged-authorizations -> provider Component authorizations[] (the basis-ref anchor); users -> system@1 |
| `lvg.system-security-plan.system-implementation.leveraged-authorizations[].links[].rel` | 1 | L1 | leveraged-authorizations -> provider Component authorizations[] (the basis-ref anchor); users -> system@1 |
| `lvg.system-security-plan.system-implementation.leveraged-authorizations[].party-uuid` | 1 | L1 | leveraged-authorizations -> provider Component authorizations[] (the basis-ref anchor); users -> system@1 |
| `lvg.system-security-plan.system-implementation.leveraged-authorizations[].title` | 1 | L1 | leveraged-authorizations -> provider Component authorizations[] (the basis-ref anchor); users -> system@1 |
| `lvg.system-security-plan.system-implementation.leveraged-authorizations[].uuid` | 1 | L1 | leveraged-authorizations -> provider Component authorizations[] (the basis-ref anchor); users -> system@1 |
| `lvg.system-security-plan.system-implementation.users[].authorized-privileges[].functions-performed[]` | 1 | L1 | leveraged-authorizations -> provider Component authorizations[] (the basis-ref anchor); users -> system@1 |
| `lvg.system-security-plan.system-implementation.users[].authorized-privileges[].title` | 1 | L1 | leveraged-authorizations -> provider Component authorizations[] (the basis-ref anchor); users -> system@1 |
| `lvg.system-security-plan.system-implementation.users[].role-ids[]` | 1 | L1 | leveraged-authorizations -> provider Component authorizations[] (the basis-ref anchor); users -> system@1 |
| `lvg.system-security-plan.system-implementation.users[].uuid` | 1 | L1 | leveraged-authorizations -> provider Component authorizations[] (the basis-ref anchor); users -> system@1 |
| `lvg.system-security-plan.uuid` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `poam.plan-of-action-and-milestones.back-matter.resources[].rlinks[].href` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `poam.plan-of-action-and-milestones.back-matter.resources[].rlinks[].media-type` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `poam.plan-of-action-and-milestones.back-matter.resources[].title` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `poam.plan-of-action-and-milestones.back-matter.resources[].uuid` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `poam.plan-of-action-and-milestones.import-ssp.href` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `poam.plan-of-action-and-milestones.metadata.last-modified` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `poam.plan-of-action-and-milestones.metadata.oscal-version` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `poam.plan-of-action-and-milestones.metadata.published` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `poam.plan-of-action-and-milestones.metadata.revisions[].last-modified` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `poam.plan-of-action-and-milestones.metadata.revisions[].links[].href` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `poam.plan-of-action-and-milestones.metadata.revisions[].links[].rel` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `poam.plan-of-action-and-milestones.metadata.revisions[].oscal-version` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `poam.plan-of-action-and-milestones.metadata.revisions[].remarks` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `poam.plan-of-action-and-milestones.metadata.revisions[].title` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `poam.plan-of-action-and-milestones.metadata.revisions[].version` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `poam.plan-of-action-and-milestones.metadata.title` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `poam.plan-of-action-and-milestones.metadata.version` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `poam.plan-of-action-and-milestones.observations[].collected` | 2 | L1 | observations@1 facet + landmark evidence URIs (deduped against AR by uuid) |
| `poam.plan-of-action-and-milestones.observations[].description` | 2 | L1 | observations@1 facet + landmark evidence URIs (deduped against AR by uuid) |
| `poam.plan-of-action-and-milestones.observations[].expires` | 1 | L1 | observations@1 facet + landmark evidence URIs (deduped against AR by uuid) |
| `poam.plan-of-action-and-milestones.observations[].methods[]` | 2 | L1 | observations@1 facet + landmark evidence URIs (deduped against AR by uuid) |
| `poam.plan-of-action-and-milestones.observations[].remarks` | 2 | L1 | observations@1 facet + landmark evidence URIs (deduped against AR by uuid) |
| `poam.plan-of-action-and-milestones.observations[].subjects[].subject-uuid` | 2 | L1 | observations@1 facet + landmark evidence URIs (deduped against AR by uuid) |
| `poam.plan-of-action-and-milestones.observations[].subjects[].type` | 2 | L1 | observations@1 facet + landmark evidence URIs (deduped against AR by uuid) |
| `poam.plan-of-action-and-milestones.observations[].title` | 2 | L1 | observations@1 facet + landmark evidence URIs (deduped against AR by uuid) |
| `poam.plan-of-action-and-milestones.observations[].types[]` | 2 | L1 | observations@1 facet + landmark evidence URIs (deduped against AR by uuid) |
| `poam.plan-of-action-and-milestones.observations[].uuid` | 2 | L1 | observations@1 facet + landmark evidence URIs (deduped against AR by uuid) |
| `poam.plan-of-action-and-milestones.poam-items[].description` | 2 | L1 | poam-item titles ride the Finding titles; related-risks/observations resolved by uuid |
| `poam.plan-of-action-and-milestones.poam-items[].related-observations[].observation-uuid` | 2 | L1 | poam-item titles ride the Finding titles; related-risks/observations resolved by uuid |
| `poam.plan-of-action-and-milestones.poam-items[].related-risks[].risk-uuid` | 2 | L1 | poam-item titles ride the Finding titles; related-risks/observations resolved by uuid |
| `poam.plan-of-action-and-milestones.poam-items[].title` | 2 | L1 | poam-item titles ride the Finding titles; related-risks/observations resolved by uuid |
| `poam.plan-of-action-and-milestones.poam-items[].uuid` | 2 | L1 | poam-item titles ride the Finding titles; related-risks/observations resolved by uuid |
| `poam.plan-of-action-and-milestones.risks[].characterizations[].facets[].name` | 4 | L2 | risk-analysis@1 characterizations (likelihood/impact + scale system, origin actors) - scoring stays out of the kernel (App. F Q14) |
| `poam.plan-of-action-and-milestones.risks[].characterizations[].facets[].system` | 4 | L2 | risk-analysis@1 characterizations (likelihood/impact + scale system, origin actors) - scoring stays out of the kernel (App. F Q14) |
| `poam.plan-of-action-and-milestones.risks[].characterizations[].facets[].value` | 4 | L2 | risk-analysis@1 characterizations (likelihood/impact + scale system, origin actors) - scoring stays out of the kernel (App. F Q14) |
| `poam.plan-of-action-and-milestones.risks[].characterizations[].origin.actors[].actor-uuid` | 2 | L2 | risk-analysis@1 characterizations (likelihood/impact + scale system, origin actors) - scoring stays out of the kernel (App. F Q14) |
| `poam.plan-of-action-and-milestones.risks[].characterizations[].origin.actors[].type` | 2 | L2 | risk-analysis@1 characterizations (likelihood/impact + scale system, origin actors) - scoring stays out of the kernel (App. F Q14) |
| `poam.plan-of-action-and-milestones.risks[].deadline` | 2 | L1 | Risk id/title; statement -> scenario; deadline -> review-due (datetime); status -> Risk state (+ verbatim in risk-analysis@1) and Finding state (deviation-approved -> approved Deviation; open+remediation -> in-remediation) |
| `poam.plan-of-action-and-milestones.risks[].description` | 2 | L2 | risk-analysis@1 description (the kernel's `scenario` is the OSCAL statement) |
| `poam.plan-of-action-and-milestones.risks[].mitigating-factors[].description` | 1 | L1 | Deviation rationale (RISK-1) + risk-analysis@1 mitigating-factors; observation links -> evidence refs |
| `poam.plan-of-action-and-milestones.risks[].mitigating-factors[].uuid` | 1 | L1 | Deviation rationale (RISK-1) + risk-analysis@1 mitigating-factors; observation links -> evidence refs |
| `poam.plan-of-action-and-milestones.risks[].related-observations[].observation-uuid` | 2 | L1 | Deviation rationale (RISK-1) + risk-analysis@1 mitigating-factors; observation links -> evidence refs |
| `poam.plan-of-action-and-milestones.risks[].remediations[].description` | 2 | L1 | Finding.actions[] description/status + risk-analysis@1 responses[] (lifecycle, title, narrative) |
| `poam.plan-of-action-and-milestones.risks[].remediations[].lifecycle` | 2 | L1 | Finding.actions[] description/status + risk-analysis@1 responses[] (lifecycle, title, narrative) |
| `poam.plan-of-action-and-milestones.risks[].remediations[].props[].name` | 2 | L1 | response `type` -> Risk.treatment (C.10: mitigate->modify, accept->retain, transfer|share->share, avoid->avoid) + verbatim in risk-analysis@1 responses[] |
| `poam.plan-of-action-and-milestones.risks[].remediations[].props[].value` | 2 | L1 | response `type` -> Risk.treatment (C.10: mitigate->modify, accept->retain, transfer|share->share, avoid->avoid) + verbatim in risk-analysis@1 responses[] |
| `poam.plan-of-action-and-milestones.risks[].remediations[].tasks[].description` | 2 | L1 | Finding.actions[] (task title; within-date-range.end -> due); remediation/task uuids are source identity (L0) |
| `poam.plan-of-action-and-milestones.risks[].remediations[].tasks[].timing.within-date-range.end` | 2 | L1 | Finding.actions[] (task title; within-date-range.end -> due); remediation/task uuids are source identity (L0) |
| `poam.plan-of-action-and-milestones.risks[].remediations[].tasks[].timing.within-date-range.start` | 2 | L1 | Finding.actions[] (task title; within-date-range.end -> due); remediation/task uuids are source identity (L0) |
| `poam.plan-of-action-and-milestones.risks[].remediations[].tasks[].title` | 2 | L1 | Finding.actions[] (task title; within-date-range.end -> due); remediation/task uuids are source identity (L0) |
| `poam.plan-of-action-and-milestones.risks[].remediations[].tasks[].type` | 2 | L1 | Finding.actions[] (task title; within-date-range.end -> due); remediation/task uuids are source identity (L0) |
| `poam.plan-of-action-and-milestones.risks[].remediations[].tasks[].uuid` | 2 | L1 | Finding.actions[] (task title; within-date-range.end -> due); remediation/task uuids are source identity (L0) |
| `poam.plan-of-action-and-milestones.risks[].remediations[].title` | 2 | L1 | Finding.actions[] description/status + risk-analysis@1 responses[] (lifecycle, title, narrative) |
| `poam.plan-of-action-and-milestones.risks[].remediations[].uuid` | 2 | L1 | Finding.actions[] (task title; within-date-range.end -> due); remediation/task uuids are source identity (L0) |
| `poam.plan-of-action-and-milestones.risks[].statement` | 2 | L1 | Risk id/title; statement -> scenario; deadline -> review-due (datetime); status -> Risk state (+ verbatim in risk-analysis@1) and Finding state (deviation-approved -> approved Deviation; open+remediation -> in-remediation) |
| `poam.plan-of-action-and-milestones.risks[].status` | 2 | L1 | Risk id/title; statement -> scenario; deadline -> review-due (datetime); status -> Risk state (+ verbatim in risk-analysis@1) and Finding state (deviation-approved -> approved Deviation; open+remediation -> in-remediation) |
| `poam.plan-of-action-and-milestones.risks[].title` | 2 | L1 | Risk id/title; statement -> scenario; deadline -> review-due (datetime); status -> Risk state (+ verbatim in risk-analysis@1) and Finding state (deviation-approved -> approved Deviation; open+remediation -> in-remediation) |
| `poam.plan-of-action-and-milestones.risks[].uuid` | 2 | L1 | Risk id/title; statement -> scenario; deadline -> review-due (datetime); status -> Risk state (+ verbatim in risk-analysis@1) and Finding state (deviation-approved -> approved Deviation; open+remediation -> in-remediation) |
| `poam.plan-of-action-and-milestones.system-id.id` | 1 | L1 | provenance / system id (system@1) |
| `poam.plan-of-action-and-milestones.system-id.identifier-type` | 1 | L1 | provenance / system id (system@1) |
| `poam.plan-of-action-and-milestones.uuid` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ssp.system-security-plan.back-matter.resources[].description` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ssp.system-security-plan.back-matter.resources[].rlinks[].href` | 3 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ssp.system-security-plan.back-matter.resources[].rlinks[].media-type` | 3 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ssp.system-security-plan.back-matter.resources[].title` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ssp.system-security-plan.back-matter.resources[].uuid` | 3 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ssp.system-security-plan.control-implementation.description` | 1 | L1 | Implementation: requirement-ref = minted AC-6.1 (in-bundle copy), by-component -> capability + satisfied-by, set-parameters -> parameter-bindings (verified against the declared ODPs), implementation-status -> status |
| `ssp.system-security-plan.control-implementation.implemented-requirements[].by-components[].component-uuid` | 1 | L1 | Implementation: requirement-ref = minted AC-6.1 (in-bundle copy), by-component -> capability + satisfied-by, set-parameters -> parameter-bindings (verified against the declared ODPs), implementation-status -> status |
| `ssp.system-security-plan.control-implementation.implemented-requirements[].by-components[].description` | 1 | L1 | Implementation: requirement-ref = minted AC-6.1 (in-bundle copy), by-component -> capability + satisfied-by, set-parameters -> parameter-bindings (verified against the declared ODPs), implementation-status -> status |
| `ssp.system-security-plan.control-implementation.implemented-requirements[].by-components[].implementation-status.state` | 1 | L1 | Implementation: requirement-ref = minted AC-6.1 (in-bundle copy), by-component -> capability + satisfied-by, set-parameters -> parameter-bindings (verified against the declared ODPs), implementation-status -> status |
| `ssp.system-security-plan.control-implementation.implemented-requirements[].by-components[].uuid` | 1 | L1 | Implementation: requirement-ref = minted AC-6.1 (in-bundle copy), by-component -> capability + satisfied-by, set-parameters -> parameter-bindings (verified against the declared ODPs), implementation-status -> status |
| `ssp.system-security-plan.control-implementation.implemented-requirements[].control-id` | 1 | L1 | Implementation: requirement-ref = minted AC-6.1 (in-bundle copy), by-component -> capability + satisfied-by, set-parameters -> parameter-bindings (verified against the declared ODPs), implementation-status -> status |
| `ssp.system-security-plan.control-implementation.implemented-requirements[].uuid` | 1 | L1 | Implementation: requirement-ref = minted AC-6.1 (in-bundle copy), by-component -> capability + satisfied-by, set-parameters -> parameter-bindings (verified against the declared ODPs), implementation-status -> status |
| `ssp.system-security-plan.control-implementation.set-parameters[].param-id` | 5 | L1 | Implementation: requirement-ref = minted AC-6.1 (in-bundle copy), by-component -> capability + satisfied-by, set-parameters -> parameter-bindings (verified against the declared ODPs), implementation-status -> status |
| `ssp.system-security-plan.control-implementation.set-parameters[].values[]` | 5 | L1 | Implementation: requirement-ref = minted AC-6.1 (in-bundle copy), by-component -> capability + satisfied-by, set-parameters -> parameter-bindings (verified against the declared ODPs), implementation-status -> status |
| `ssp.system-security-plan.import-profile.href` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ssp.system-security-plan.metadata.last-modified` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ssp.system-security-plan.metadata.oscal-version` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ssp.system-security-plan.metadata.parties[].links[].href` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ssp.system-security-plan.metadata.parties[].links[].rel` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ssp.system-security-plan.metadata.parties[].member-of-organizations[]` | 3 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ssp.system-security-plan.metadata.parties[].name` | 4 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ssp.system-security-plan.metadata.parties[].short-name` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ssp.system-security-plan.metadata.parties[].type` | 4 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ssp.system-security-plan.metadata.parties[].uuid` | 4 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ssp.system-security-plan.metadata.published` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ssp.system-security-plan.metadata.responsible-parties[].party-uuids[]` | 3 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ssp.system-security-plan.metadata.responsible-parties[].role-id` | 3 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ssp.system-security-plan.metadata.revisions[].last-modified` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ssp.system-security-plan.metadata.revisions[].links[].href` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ssp.system-security-plan.metadata.revisions[].links[].rel` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ssp.system-security-plan.metadata.revisions[].oscal-version` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ssp.system-security-plan.metadata.revisions[].published` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ssp.system-security-plan.metadata.revisions[].title` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ssp.system-security-plan.metadata.revisions[].version` | 2 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ssp.system-security-plan.metadata.roles[].id` | 4 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ssp.system-security-plan.metadata.roles[].title` | 4 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ssp.system-security-plan.metadata.title` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ssp.system-security-plan.metadata.version` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |
| `ssp.system-security-plan.system-characteristics.authorization-boundary.description` | 1 | L1 | system Component: authorizations[] (date-authorized -> the D5 anchor + Attestation) + system@1 facet (ids, status, sensitivity, FIPS-199 impact, boundary/network/data-flow, language-tagged) |
| `ssp.system-security-plan.system-characteristics.data-flow.description` | 1 | L1 | system Component: authorizations[] (date-authorized -> the D5 anchor + Attestation) + system@1 facet (ids, status, sensitivity, FIPS-199 impact, boundary/network/data-flow, language-tagged) |
| `ssp.system-security-plan.system-characteristics.date-authorized` | 1 | L1 | system Component: authorizations[] (date-authorized -> the D5 anchor + Attestation) + system@1 facet (ids, status, sensitivity, FIPS-199 impact, boundary/network/data-flow, language-tagged) |
| `ssp.system-security-plan.system-characteristics.description` | 1 | L1 | system Component: authorizations[] (date-authorized -> the D5 anchor + Attestation) + system@1 facet (ids, status, sensitivity, FIPS-199 impact, boundary/network/data-flow, language-tagged) |
| `ssp.system-security-plan.system-characteristics.network-architecture.description` | 1 | L1 | system Component: authorizations[] (date-authorized -> the D5 anchor + Attestation) + system@1 facet (ids, status, sensitivity, FIPS-199 impact, boundary/network/data-flow, language-tagged) |
| `ssp.system-security-plan.system-characteristics.security-impact-level.security-objective-availability` | 1 | L1 | system Component: authorizations[] (date-authorized -> the D5 anchor + Attestation) + system@1 facet (ids, status, sensitivity, FIPS-199 impact, boundary/network/data-flow, language-tagged) |
| `ssp.system-security-plan.system-characteristics.security-impact-level.security-objective-confidentiality` | 1 | L1 | system Component: authorizations[] (date-authorized -> the D5 anchor + Attestation) + system@1 facet (ids, status, sensitivity, FIPS-199 impact, boundary/network/data-flow, language-tagged) |
| `ssp.system-security-plan.system-characteristics.security-impact-level.security-objective-integrity` | 1 | L1 | system Component: authorizations[] (date-authorized -> the D5 anchor + Attestation) + system@1 facet (ids, status, sensitivity, FIPS-199 impact, boundary/network/data-flow, language-tagged) |
| `ssp.system-security-plan.system-characteristics.security-sensitivity-level` | 1 | L1 | system Component: authorizations[] (date-authorized -> the D5 anchor + Attestation) + system@1 facet (ids, status, sensitivity, FIPS-199 impact, boundary/network/data-flow, language-tagged) |
| `ssp.system-security-plan.system-characteristics.status.state` | 1 | L1 | system Component: authorizations[] (date-authorized -> the D5 anchor + Attestation) + system@1 facet (ids, status, sensitivity, FIPS-199 impact, boundary/network/data-flow, language-tagged) |
| `ssp.system-security-plan.system-characteristics.system-ids[].id` | 1 | L1 | system Component: authorizations[] (date-authorized -> the D5 anchor + Attestation) + system@1 facet (ids, status, sensitivity, FIPS-199 impact, boundary/network/data-flow, language-tagged) |
| `ssp.system-security-plan.system-characteristics.system-ids[].identifier-type` | 1 | L1 | system Component: authorizations[] (date-authorized -> the D5 anchor + Attestation) + system@1 facet (ids, status, sensitivity, FIPS-199 impact, boundary/network/data-flow, language-tagged) |
| `ssp.system-security-plan.system-characteristics.system-information.information-types[].availability-impact.base` | 1 | L1 | system Component: authorizations[] (date-authorized -> the D5 anchor + Attestation) + system@1 facet (ids, status, sensitivity, FIPS-199 impact, boundary/network/data-flow, language-tagged) |
| `ssp.system-security-plan.system-characteristics.system-information.information-types[].categorizations[].information-type-ids[]` | 1 | L1 | system Component: authorizations[] (date-authorized -> the D5 anchor + Attestation) + system@1 facet (ids, status, sensitivity, FIPS-199 impact, boundary/network/data-flow, language-tagged) |
| `ssp.system-security-plan.system-characteristics.system-information.information-types[].categorizations[].system` | 1 | L1 | system Component: authorizations[] (date-authorized -> the D5 anchor + Attestation) + system@1 facet (ids, status, sensitivity, FIPS-199 impact, boundary/network/data-flow, language-tagged) |
| `ssp.system-security-plan.system-characteristics.system-information.information-types[].confidentiality-impact.base` | 1 | L1 | system Component: authorizations[] (date-authorized -> the D5 anchor + Attestation) + system@1 facet (ids, status, sensitivity, FIPS-199 impact, boundary/network/data-flow, language-tagged) |
| `ssp.system-security-plan.system-characteristics.system-information.information-types[].description` | 1 | L1 | system Component: authorizations[] (date-authorized -> the D5 anchor + Attestation) + system@1 facet (ids, status, sensitivity, FIPS-199 impact, boundary/network/data-flow, language-tagged) |
| `ssp.system-security-plan.system-characteristics.system-information.information-types[].integrity-impact.adjustment-justification` | 1 | L1 | system Component: authorizations[] (date-authorized -> the D5 anchor + Attestation) + system@1 facet (ids, status, sensitivity, FIPS-199 impact, boundary/network/data-flow, language-tagged) |
| `ssp.system-security-plan.system-characteristics.system-information.information-types[].integrity-impact.base` | 1 | L1 | system Component: authorizations[] (date-authorized -> the D5 anchor + Attestation) + system@1 facet (ids, status, sensitivity, FIPS-199 impact, boundary/network/data-flow, language-tagged) |
| `ssp.system-security-plan.system-characteristics.system-information.information-types[].integrity-impact.selected` | 1 | L1 | system Component: authorizations[] (date-authorized -> the D5 anchor + Attestation) + system@1 facet (ids, status, sensitivity, FIPS-199 impact, boundary/network/data-flow, language-tagged) |
| `ssp.system-security-plan.system-characteristics.system-information.information-types[].title` | 1 | L1 | system Component: authorizations[] (date-authorized -> the D5 anchor + Attestation) + system@1 facet (ids, status, sensitivity, FIPS-199 impact, boundary/network/data-flow, language-tagged) |
| `ssp.system-security-plan.system-characteristics.system-information.information-types[].uuid` | 1 | L1 | system Component: authorizations[] (date-authorized -> the D5 anchor + Attestation) + system@1 facet (ids, status, sensitivity, FIPS-199 impact, boundary/network/data-flow, language-tagged) |
| `ssp.system-security-plan.system-characteristics.system-name` | 1 | L1 | system Component: authorizations[] (date-authorized -> the D5 anchor + Attestation) + system@1 facet (ids, status, sensitivity, FIPS-199 impact, boundary/network/data-flow, language-tagged) |
| `ssp.system-security-plan.system-implementation.components[].description` | 1 | L1 | Component (kind system) id/title/status |
| `ssp.system-security-plan.system-implementation.components[].responsible-roles[].party-uuids[]` | 2 | L1 | Component (kind system) id/title/status |
| `ssp.system-security-plan.system-implementation.components[].responsible-roles[].role-id` | 2 | L1 | Component (kind system) id/title/status |
| `ssp.system-security-plan.system-implementation.components[].status.state` | 1 | L1 | Component (kind system) id/title/status |
| `ssp.system-security-plan.system-implementation.components[].title` | 1 | L1 | Component (kind system) id/title/status |
| `ssp.system-security-plan.system-implementation.components[].type` | 1 | L1 | Component (kind system) id/title/status |
| `ssp.system-security-plan.system-implementation.components[].uuid` | 1 | L1 | Component (kind system) id/title/status |
| `ssp.system-security-plan.system-implementation.inventory-items[].description` | 6 | L2 | system@1 facet inventory-items[] (asset props carried verbatim) |
| `ssp.system-security-plan.system-implementation.inventory-items[].implemented-components[].component-uuid` | 6 | L2 | system@1 facet inventory-items[] (asset props carried verbatim) |
| `ssp.system-security-plan.system-implementation.inventory-items[].implemented-components[].props[].name` | 6 | L2 | system@1 facet inventory-items[] (asset props carried verbatim) |
| `ssp.system-security-plan.system-implementation.inventory-items[].implemented-components[].props[].value` | 6 | L2 | system@1 facet inventory-items[] (asset props carried verbatim) |
| `ssp.system-security-plan.system-implementation.inventory-items[].props[].class` | 19 | L2 | system@1 facet inventory-items[] (asset props carried verbatim) |
| `ssp.system-security-plan.system-implementation.inventory-items[].props[].name` | 19 | L2 | system@1 facet inventory-items[] (asset props carried verbatim) |
| `ssp.system-security-plan.system-implementation.inventory-items[].props[].value` | 19 | L2 | system@1 facet inventory-items[] (asset props carried verbatim) |
| `ssp.system-security-plan.system-implementation.inventory-items[].uuid` | 6 | L2 | system@1 facet inventory-items[] (asset props carried verbatim) |
| `ssp.system-security-plan.system-implementation.users[].authorized-privileges[].functions-performed[]` | 13 | L2 | system@1 facet users[] |
| `ssp.system-security-plan.system-implementation.users[].authorized-privileges[].title` | 3 | L2 | system@1 facet users[] |
| `ssp.system-security-plan.system-implementation.users[].description` | 3 | L2 | system@1 facet users[] |
| `ssp.system-security-plan.system-implementation.users[].role-ids[]` | 2 | L2 | system@1 facet users[] |
| `ssp.system-security-plan.system-implementation.users[].title` | 3 | L2 | system@1 facet users[] |
| `ssp.system-security-plan.system-implementation.users[].uuid` | 3 | L2 | system@1 facet users[] |
| `ssp.system-security-plan.uuid` | 1 | L1 | bundle manifest / L0 provenance (doc identity, parties -> landmark party URIs, imports) |

## UNMAPPED (gate target: zero)

*(none)*

## Unaccounted source values (conversion ledger)

No destination and no declared reason. Each is either carried by a rule the converter does not state yet, or dropped without a decision. Pointers to every single value are in `ifa-conversion-ledger.json`.

| path | count | first value |
|---|---:|---|
| `ap.assessment-plan.assessment-subjects[].description` | 1 | `ap#/assessment-plan/assessment-subjects/0/description` |
| `ap.assessment-plan.local-definitions.activities[].props[].name` | 1 | `ap#/assessment-plan/local-definitions/activities/0/props/0/name` |
| `ap.assessment-plan.local-definitions.activities[].props[].value` | 1 | `ap#/assessment-plan/local-definitions/activities/0/props/0/value` |
| `ap.assessment-plan.local-definitions.activities[].related-controls.control-selections[].include-controls[].control-id` | 1 | `ap#/assessment-plan/local-definitions/activities/0/related-controls/control-selections/0/include-controls/0/control-id` |
| `ap.assessment-plan.local-definitions.activities[].responsible-roles[].party-uuids[]` | 1 | `ap#/assessment-plan/local-definitions/activities/0/responsible-roles/0/party-uuids/0` |
| `ap.assessment-plan.local-definitions.activities[].responsible-roles[].role-id` | 1 | `ap#/assessment-plan/local-definitions/activities/0/responsible-roles/0/role-id` |
| `ap.assessment-plan.metadata.responsible-parties[].party-uuids[]` | 1 | `ap#/assessment-plan/metadata/responsible-parties/0/party-uuids/0` |
| `ap.assessment-plan.metadata.responsible-parties[].role-id` | 1 | `ap#/assessment-plan/metadata/responsible-parties/0/role-id` |
| `ap.assessment-plan.tasks[].associated-activities[].activity-uuid` | 1 | `ap#/assessment-plan/tasks/0/associated-activities/0/activity-uuid` |
| `ap.assessment-plan.tasks[].remarks` | 1 | `ap#/assessment-plan/tasks/0/remarks` |
| `ap.assessment-plan.tasks[].responsible-roles[].role-id` | 1 | `ap#/assessment-plan/tasks/0/responsible-roles/0/role-id` |
| `ar.assessment-results.local-definitions.activities[].description` | 1 | `ar#/assessment-results/local-definitions/activities/0/description` |
| `ar.assessment-results.local-definitions.activities[].props[].name` | 1 | `ar#/assessment-results/local-definitions/activities/0/props/0/name` |
| `ar.assessment-results.local-definitions.activities[].props[].value` | 1 | `ar#/assessment-results/local-definitions/activities/0/props/0/value` |
| `ar.assessment-results.local-definitions.activities[].related-controls.control-selections[].include-controls[].control-id` | 1 | `ar#/assessment-results/local-definitions/activities/0/related-controls/control-selections/0/include-controls/0/control-id` |
| `ar.assessment-results.local-definitions.activities[].responsible-roles[].party-uuids[]` | 1 | `ar#/assessment-results/local-definitions/activities/0/responsible-roles/0/party-uuids/0` |
| `ar.assessment-results.local-definitions.activities[].responsible-roles[].role-id` | 1 | `ar#/assessment-results/local-definitions/activities/0/responsible-roles/0/role-id` |
| `ar.assessment-results.local-definitions.activities[].steps[].description` | 3 | `ar#/assessment-results/local-definitions/activities/0/steps/0/description` |
| `ar.assessment-results.local-definitions.activities[].steps[].remarks` | 2 | `ar#/assessment-results/local-definitions/activities/0/steps/0/remarks` |
| `ar.assessment-results.local-definitions.activities[].steps[].title` | 3 | `ar#/assessment-results/local-definitions/activities/0/steps/0/title` |
| `ar.assessment-results.local-definitions.activities[].title` | 1 | `ar#/assessment-results/local-definitions/activities/0/title` |
| `ar.assessment-results.metadata.responsible-parties[].role-id` | 1 | `ar#/assessment-results/metadata/responsible-parties/0/role-id` |
| `ar.assessment-results.results[].description` | 1 | `ar#/assessment-results/results/0/description` |
| `ar.assessment-results.results[].end` | 1 | `ar#/assessment-results/results/0/end` |
| `ar.assessment-results.results[].findings[].description` | 1 | `ar#/assessment-results/results/0/findings/0/description` |
| `ar.assessment-results.results[].findings[].related-observations[].observation-uuid` | 1 | `ar#/assessment-results/results/0/findings/0/related-observations/0/observation-uuid` |
| `ar.assessment-results.results[].findings[].related-risks[].risk-uuid` | 1 | `ar#/assessment-results/results/0/findings/0/related-risks/0/risk-uuid` |
| `ar.assessment-results.results[].findings[].target.description` | 1 | `ar#/assessment-results/results/0/findings/0/target/description` |
| `ar.assessment-results.results[].local-definitions.tasks[].associated-activities[].activity-uuid` | 1 | `ar#/assessment-results/results/0/local-definitions/tasks/0/associated-activities/0/activity-uuid` |
| `ar.assessment-results.results[].local-definitions.tasks[].description` | 1 | `ar#/assessment-results/results/0/local-definitions/tasks/0/description` |
| `ar.assessment-results.results[].local-definitions.tasks[].title` | 1 | `ar#/assessment-results/results/0/local-definitions/tasks/0/title` |
| `ar.assessment-results.results[].local-definitions.tasks[].type` | 1 | `ar#/assessment-results/results/0/local-definitions/tasks/0/type` |
| `ar.assessment-results.results[].observations[].remarks` | 2 | `ar#/assessment-results/results/0/observations/0/remarks` |
| `ar.assessment-results.results[].observations[].subjects[].subject-uuid` | 2 | `ar#/assessment-results/results/0/observations/0/subjects/0/subject-uuid` |
| `ar.assessment-results.results[].observations[].types[]` | 2 | `ar#/assessment-results/results/0/observations/0/types/0` |
| `cdef.component-definition.components[].control-implementations[].description` | 1 | `cdef#/component-definition/components/0/control-implementations/0/description` |
| `cdef.component-definition.components[].control-implementations[].implemented-requirements[].set-parameters[].param-id` | 2 | `cdef#/component-definition/components/0/control-implementations/0/implemented-requirements/0/set-parameters/0/param-id` |
| `cdef.component-definition.components[].control-implementations[].implemented-requirements[].set-parameters[].values[]` | 2 | `cdef#/component-definition/components/0/control-implementations/0/implemented-requirements/0/set-parameters/0/values/0` |
| `cdef.component-definition.components[].control-implementations[].implemented-requirements[].statements[].description` | 2 | `cdef#/component-definition/components/0/control-implementations/0/implemented-requirements/0/statements/0/description` |
| `cdef.component-definition.components[].control-implementations[].implemented-requirements[].statements[].responsible-roles[].role-id` | 1 | `cdef#/component-definition/components/0/control-implementations/0/implemented-requirements/1/statements/0/responsible-roles/0/role-id` |
| `cdef.component-definition.components[].control-implementations[].implemented-requirements[].statements[].statement-id` | 2 | `cdef#/component-definition/components/0/control-implementations/0/implemented-requirements/0/statements/0/statement-id` |
| `cdef.component-definition.components[].control-implementations[].source` | 1 | `cdef#/component-definition/components/0/control-implementations/0/source` |
| `cdef.component-definition.components[].description` | 1 | `cdef#/component-definition/components/0/description` |
| `cdef.component-definition.components[].purpose` | 1 | `cdef#/component-definition/components/0/purpose` |
| `cdef.component-definition.components[].responsible-roles[].party-uuids[]` | 1 | `cdef#/component-definition/components/0/responsible-roles/0/party-uuids/0` |
| `cdef.component-definition.components[].responsible-roles[].role-id` | 2 | `cdef#/component-definition/components/0/responsible-roles/0/role-id` |
| `lev.system-security-plan.control-implementation.description` | 1 | `lev#/system-security-plan/control-implementation/description` |
| `lev.system-security-plan.control-implementation.implemented-requirements[].remarks` | 1 | `lev#/system-security-plan/control-implementation/implemented-requirements/0/remarks` |
| `lev.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].component-uuid` | 2 | `lev#/system-security-plan/control-implementation/implemented-requirements/0/statements/0/by-components/0/component-uuid` |
| `lev.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].description` | 2 | `lev#/system-security-plan/control-implementation/implemented-requirements/0/statements/0/by-components/0/description` |
| `lev.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].export.description` | 2 | `lev#/system-security-plan/control-implementation/implemented-requirements/0/statements/0/by-components/0/export/description` |
| `lev.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].export.provided[].responsible-roles[].party-uuids[]` | 2 | `lev#/system-security-plan/control-implementation/implemented-requirements/0/statements/0/by-components/0/export/provided/0/responsible-roles/0/party-uuids/0` |
| `lev.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].export.provided[].responsible-roles[].role-id` | 2 | `lev#/system-security-plan/control-implementation/implemented-requirements/0/statements/0/by-components/0/export/provided/0/responsible-roles/0/role-id` |
| `lev.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].export.responsibilities[].provided-uuid` | 2 | `lev#/system-security-plan/control-implementation/implemented-requirements/0/statements/0/by-components/0/export/responsibilities/0/provided-uuid` |
| `lev.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].export.responsibilities[].responsible-roles[].party-uuids[]` | 2 | `lev#/system-security-plan/control-implementation/implemented-requirements/0/statements/0/by-components/0/export/responsibilities/0/responsible-roles/0/party-uuids/0` |
| `lev.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].export.responsibilities[].responsible-roles[].role-id` | 2 | `lev#/system-security-plan/control-implementation/implemented-requirements/0/statements/0/by-components/0/export/responsibilities/0/responsible-roles/0/role-id` |
| `lev.system-security-plan.control-implementation.implemented-requirements[].statements[].remarks` | 1 | `lev#/system-security-plan/control-implementation/implemented-requirements/0/statements/0/remarks` |
| `lev.system-security-plan.system-characteristics.authorization-boundary.description` | 1 | `lev#/system-security-plan/system-characteristics/authorization-boundary/description` |
| `lev.system-security-plan.system-characteristics.remarks` | 1 | `lev#/system-security-plan/system-characteristics/remarks` |
| `lev.system-security-plan.system-characteristics.security-impact-level.security-objective-availability` | 1 | `lev#/system-security-plan/system-characteristics/security-impact-level/security-objective-availability` |
| `lev.system-security-plan.system-characteristics.security-impact-level.security-objective-confidentiality` | 1 | `lev#/system-security-plan/system-characteristics/security-impact-level/security-objective-confidentiality` |
| `lev.system-security-plan.system-characteristics.security-impact-level.security-objective-integrity` | 1 | `lev#/system-security-plan/system-characteristics/security-impact-level/security-objective-integrity` |
| `lev.system-security-plan.system-characteristics.security-sensitivity-level` | 1 | `lev#/system-security-plan/system-characteristics/security-sensitivity-level` |
| `lev.system-security-plan.system-characteristics.status.state` | 1 | `lev#/system-security-plan/system-characteristics/status/state` |
| `lev.system-security-plan.system-characteristics.system-ids[].id` | 1 | `lev#/system-security-plan/system-characteristics/system-ids/0/id` |
| `lev.system-security-plan.system-characteristics.system-information.information-types[].availability-impact.adjustment-justification` | 1 | `lev#/system-security-plan/system-characteristics/system-information/information-types/0/availability-impact/adjustment-justification` |
| `lev.system-security-plan.system-characteristics.system-information.information-types[].availability-impact.base` | 1 | `lev#/system-security-plan/system-characteristics/system-information/information-types/0/availability-impact/base` |
| `lev.system-security-plan.system-characteristics.system-information.information-types[].availability-impact.selected` | 1 | `lev#/system-security-plan/system-characteristics/system-information/information-types/0/availability-impact/selected` |
| `lev.system-security-plan.system-characteristics.system-information.information-types[].categorizations[].information-type-ids[]` | 1 | `lev#/system-security-plan/system-characteristics/system-information/information-types/0/categorizations/0/information-type-ids/0` |
| `lev.system-security-plan.system-characteristics.system-information.information-types[].categorizations[].system` | 1 | `lev#/system-security-plan/system-characteristics/system-information/information-types/0/categorizations/0/system` |
| `lev.system-security-plan.system-characteristics.system-information.information-types[].confidentiality-impact.adjustment-justification` | 1 | `lev#/system-security-plan/system-characteristics/system-information/information-types/0/confidentiality-impact/adjustment-justification` |
| `lev.system-security-plan.system-characteristics.system-information.information-types[].confidentiality-impact.base` | 1 | `lev#/system-security-plan/system-characteristics/system-information/information-types/0/confidentiality-impact/base` |
| `lev.system-security-plan.system-characteristics.system-information.information-types[].confidentiality-impact.selected` | 1 | `lev#/system-security-plan/system-characteristics/system-information/information-types/0/confidentiality-impact/selected` |
| `lev.system-security-plan.system-characteristics.system-information.information-types[].description` | 1 | `lev#/system-security-plan/system-characteristics/system-information/information-types/0/description` |
| `lev.system-security-plan.system-characteristics.system-information.information-types[].integrity-impact.adjustment-justification` | 1 | `lev#/system-security-plan/system-characteristics/system-information/information-types/0/integrity-impact/adjustment-justification` |
| `lev.system-security-plan.system-characteristics.system-information.information-types[].integrity-impact.base` | 1 | `lev#/system-security-plan/system-characteristics/system-information/information-types/0/integrity-impact/base` |
| `lev.system-security-plan.system-characteristics.system-information.information-types[].integrity-impact.selected` | 1 | `lev#/system-security-plan/system-characteristics/system-information/information-types/0/integrity-impact/selected` |
| `lev.system-security-plan.system-characteristics.system-information.information-types[].title` | 1 | `lev#/system-security-plan/system-characteristics/system-information/information-types/0/title` |
| `lev.system-security-plan.system-implementation.components[].description` | 2 | `lev#/system-security-plan/system-implementation/components/0/description` |
| `lev.system-security-plan.system-implementation.components[].props[].name` | 1 | `lev#/system-security-plan/system-implementation/components/1/props/0/name` |
| `lev.system-security-plan.system-implementation.components[].props[].value` | 1 | `lev#/system-security-plan/system-implementation/components/1/props/0/value` |
| `lev.system-security-plan.system-implementation.components[].responsible-roles[].party-uuids[]` | 1 | `lev#/system-security-plan/system-implementation/components/1/responsible-roles/0/party-uuids/0` |
| `lev.system-security-plan.system-implementation.components[].responsible-roles[].role-id` | 1 | `lev#/system-security-plan/system-implementation/components/1/responsible-roles/0/role-id` |
| `lev.system-security-plan.system-implementation.components[].status.state` | 2 | `lev#/system-security-plan/system-implementation/components/0/status/state` |
| `lev.system-security-plan.system-implementation.components[].title` | 1 | `lev#/system-security-plan/system-implementation/components/0/title` |
| `lev.system-security-plan.system-implementation.users[].authorized-privileges[].functions-performed[]` | 1 | `lev#/system-security-plan/system-implementation/users/0/authorized-privileges/0/functions-performed/0` |
| `lev.system-security-plan.system-implementation.users[].authorized-privileges[].title` | 1 | `lev#/system-security-plan/system-implementation/users/0/authorized-privileges/0/title` |
| `lev.system-security-plan.system-implementation.users[].role-ids[]` | 1 | `lev#/system-security-plan/system-implementation/users/0/role-ids/0` |
| `lvg.system-security-plan.control-implementation.description` | 1 | `lvg#/system-security-plan/control-implementation/description` |
| `lvg.system-security-plan.control-implementation.implemented-requirements[].remarks` | 1 | `lvg#/system-security-plan/control-implementation/implemented-requirements/0/remarks` |
| `lvg.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].component-uuid` | 3 | `lvg#/system-security-plan/control-implementation/implemented-requirements/0/statements/0/by-components/0/component-uuid` |
| `lvg.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].description` | 3 | `lvg#/system-security-plan/control-implementation/implemented-requirements/0/statements/0/by-components/0/description` |
| `lvg.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].inherited[].description` | 1 | `lvg#/system-security-plan/control-implementation/implemented-requirements/0/statements/0/by-components/2/inherited/0/description` |
| `lvg.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].inherited[].provided-uuid` | 1 | `lvg#/system-security-plan/control-implementation/implemented-requirements/0/statements/0/by-components/2/inherited/0/provided-uuid` |
| `lvg.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].responsible-roles[].party-uuids[]` | 1 | `lvg#/system-security-plan/control-implementation/implemented-requirements/0/statements/0/by-components/0/responsible-roles/0/party-uuids/0` |
| `lvg.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].responsible-roles[].role-id` | 1 | `lvg#/system-security-plan/control-implementation/implemented-requirements/0/statements/0/by-components/0/responsible-roles/0/role-id` |
| `lvg.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].satisfied[].description` | 1 | `lvg#/system-security-plan/control-implementation/implemented-requirements/0/statements/0/by-components/2/satisfied/0/description` |
| `lvg.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].satisfied[].responsibility-uuid` | 2 | `lvg#/system-security-plan/control-implementation/implemented-requirements/0/statements/0/by-components/1/satisfied/0/responsibility-uuid` |
| `lvg.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].satisfied[].responsible-roles[].party-uuids[]` | 1 | `lvg#/system-security-plan/control-implementation/implemented-requirements/0/statements/0/by-components/1/satisfied/0/responsible-roles/0/party-uuids/0` |
| `lvg.system-security-plan.control-implementation.implemented-requirements[].statements[].by-components[].satisfied[].responsible-roles[].role-id` | 1 | `lvg#/system-security-plan/control-implementation/implemented-requirements/0/statements/0/by-components/1/satisfied/0/responsible-roles/0/role-id` |
| `lvg.system-security-plan.control-implementation.implemented-requirements[].statements[].remarks` | 1 | `lvg#/system-security-plan/control-implementation/implemented-requirements/0/statements/0/remarks` |
| `lvg.system-security-plan.system-characteristics.authorization-boundary.description` | 1 | `lvg#/system-security-plan/system-characteristics/authorization-boundary/description` |
| `lvg.system-security-plan.system-characteristics.remarks` | 1 | `lvg#/system-security-plan/system-characteristics/remarks` |
| `lvg.system-security-plan.system-characteristics.security-impact-level.security-objective-availability` | 1 | `lvg#/system-security-plan/system-characteristics/security-impact-level/security-objective-availability` |
| `lvg.system-security-plan.system-characteristics.security-impact-level.security-objective-confidentiality` | 1 | `lvg#/system-security-plan/system-characteristics/security-impact-level/security-objective-confidentiality` |
| `lvg.system-security-plan.system-characteristics.security-impact-level.security-objective-integrity` | 1 | `lvg#/system-security-plan/system-characteristics/security-impact-level/security-objective-integrity` |
| `lvg.system-security-plan.system-characteristics.security-sensitivity-level` | 1 | `lvg#/system-security-plan/system-characteristics/security-sensitivity-level` |
| `lvg.system-security-plan.system-characteristics.status.state` | 1 | `lvg#/system-security-plan/system-characteristics/status/state` |
| `lvg.system-security-plan.system-characteristics.system-ids[].id` | 1 | `lvg#/system-security-plan/system-characteristics/system-ids/0/id` |
| `lvg.system-security-plan.system-characteristics.system-information.information-types[].availability-impact.adjustment-justification` | 1 | `lvg#/system-security-plan/system-characteristics/system-information/information-types/0/availability-impact/adjustment-justification` |
| `lvg.system-security-plan.system-characteristics.system-information.information-types[].availability-impact.base` | 1 | `lvg#/system-security-plan/system-characteristics/system-information/information-types/0/availability-impact/base` |
| `lvg.system-security-plan.system-characteristics.system-information.information-types[].availability-impact.selected` | 1 | `lvg#/system-security-plan/system-characteristics/system-information/information-types/0/availability-impact/selected` |
| `lvg.system-security-plan.system-characteristics.system-information.information-types[].categorizations[].information-type-ids[]` | 1 | `lvg#/system-security-plan/system-characteristics/system-information/information-types/0/categorizations/0/information-type-ids/0` |
| `lvg.system-security-plan.system-characteristics.system-information.information-types[].categorizations[].system` | 1 | `lvg#/system-security-plan/system-characteristics/system-information/information-types/0/categorizations/0/system` |
| `lvg.system-security-plan.system-characteristics.system-information.information-types[].confidentiality-impact.adjustment-justification` | 1 | `lvg#/system-security-plan/system-characteristics/system-information/information-types/0/confidentiality-impact/adjustment-justification` |
| `lvg.system-security-plan.system-characteristics.system-information.information-types[].confidentiality-impact.base` | 1 | `lvg#/system-security-plan/system-characteristics/system-information/information-types/0/confidentiality-impact/base` |
| `lvg.system-security-plan.system-characteristics.system-information.information-types[].confidentiality-impact.selected` | 1 | `lvg#/system-security-plan/system-characteristics/system-information/information-types/0/confidentiality-impact/selected` |
| `lvg.system-security-plan.system-characteristics.system-information.information-types[].description` | 1 | `lvg#/system-security-plan/system-characteristics/system-information/information-types/0/description` |
| `lvg.system-security-plan.system-characteristics.system-information.information-types[].integrity-impact.adjustment-justification` | 1 | `lvg#/system-security-plan/system-characteristics/system-information/information-types/0/integrity-impact/adjustment-justification` |
| `lvg.system-security-plan.system-characteristics.system-information.information-types[].integrity-impact.base` | 1 | `lvg#/system-security-plan/system-characteristics/system-information/information-types/0/integrity-impact/base` |
| `lvg.system-security-plan.system-characteristics.system-information.information-types[].integrity-impact.selected` | 1 | `lvg#/system-security-plan/system-characteristics/system-information/information-types/0/integrity-impact/selected` |
| `lvg.system-security-plan.system-characteristics.system-information.information-types[].title` | 1 | `lvg#/system-security-plan/system-characteristics/system-information/information-types/0/title` |
| `lvg.system-security-plan.system-implementation.components[].description` | 4 | `lvg#/system-security-plan/system-implementation/components/0/description` |
| `lvg.system-security-plan.system-implementation.components[].props[].name` | 8 | `lvg#/system-security-plan/system-implementation/components/1/props/0/name` |
| `lvg.system-security-plan.system-implementation.components[].props[].value` | 8 | `lvg#/system-security-plan/system-implementation/components/1/props/0/value` |
| `lvg.system-security-plan.system-implementation.components[].status.state` | 4 | `lvg#/system-security-plan/system-implementation/components/0/status/state` |
| `lvg.system-security-plan.system-implementation.components[].title` | 3 | `lvg#/system-security-plan/system-implementation/components/0/title` |
| `lvg.system-security-plan.system-implementation.components[].type` | 2 | `lvg#/system-security-plan/system-implementation/components/1/type` |
| `lvg.system-security-plan.system-implementation.leveraged-authorizations[].party-uuid` | 1 | `lvg#/system-security-plan/system-implementation/leveraged-authorizations/0/party-uuid` |
| `lvg.system-security-plan.system-implementation.users[].authorized-privileges[].functions-performed[]` | 1 | `lvg#/system-security-plan/system-implementation/users/0/authorized-privileges/0/functions-performed/0` |
| `lvg.system-security-plan.system-implementation.users[].authorized-privileges[].title` | 1 | `lvg#/system-security-plan/system-implementation/users/0/authorized-privileges/0/title` |
| `lvg.system-security-plan.system-implementation.users[].role-ids[]` | 1 | `lvg#/system-security-plan/system-implementation/users/0/role-ids/0` |
| `poam.plan-of-action-and-milestones.observations[].remarks` | 2 | `poam#/plan-of-action-and-milestones/observations/0/remarks` |
| `poam.plan-of-action-and-milestones.observations[].subjects[].subject-uuid` | 2 | `poam#/plan-of-action-and-milestones/observations/0/subjects/0/subject-uuid` |
| `poam.plan-of-action-and-milestones.observations[].types[]` | 2 | `poam#/plan-of-action-and-milestones/observations/0/types/0` |
| `poam.plan-of-action-and-milestones.poam-items[].description` | 2 | `poam#/plan-of-action-and-milestones/poam-items/0/description` |
| `poam.plan-of-action-and-milestones.poam-items[].related-observations[].observation-uuid` | 2 | `poam#/plan-of-action-and-milestones/poam-items/0/related-observations/0/observation-uuid` |
| `poam.plan-of-action-and-milestones.poam-items[].related-risks[].risk-uuid` | 2 | `poam#/plan-of-action-and-milestones/poam-items/0/related-risks/0/risk-uuid` |
| `poam.plan-of-action-and-milestones.poam-items[].title` | 2 | `poam#/plan-of-action-and-milestones/poam-items/0/title` |
| `poam.plan-of-action-and-milestones.risks[].related-observations[].observation-uuid` | 2 | `poam#/plan-of-action-and-milestones/risks/0/related-observations/0/observation-uuid` |
| `ssp.system-security-plan.control-implementation.description` | 1 | `ssp#/system-security-plan/control-implementation/description` |
| `ssp.system-security-plan.control-implementation.implemented-requirements[].by-components[].component-uuid` | 1 | `ssp#/system-security-plan/control-implementation/implemented-requirements/0/by-components/0/component-uuid` |
| `ssp.system-security-plan.metadata.responsible-parties[].party-uuids[]` | 2 | `ssp#/system-security-plan/metadata/responsible-parties/1/party-uuids/0` |
| `ssp.system-security-plan.metadata.responsible-parties[].role-id` | 3 | `ssp#/system-security-plan/metadata/responsible-parties/0/role-id` |
| `ssp.system-security-plan.system-implementation.components[].description` | 1 | `ssp#/system-security-plan/system-implementation/components/0/description` |
| `ssp.system-security-plan.system-implementation.components[].responsible-roles[].party-uuids[]` | 2 | `ssp#/system-security-plan/system-implementation/components/0/responsible-roles/0/party-uuids/0` |
| `ssp.system-security-plan.system-implementation.components[].responsible-roles[].role-id` | 2 | `ssp#/system-security-plan/system-implementation/components/0/responsible-roles/0/role-id` |
| `ssp.system-security-plan.system-implementation.components[].status.state` | 1 | `ssp#/system-security-plan/system-implementation/components/0/status/state` |
| `ssp.system-security-plan.system-implementation.inventory-items[].implemented-components[].props[].name` | 6 | `ssp#/system-security-plan/system-implementation/inventory-items/0/implemented-components/0/props/0/name` |
| `ssp.system-security-plan.system-implementation.inventory-items[].implemented-components[].props[].value` | 6 | `ssp#/system-security-plan/system-implementation/inventory-items/0/implemented-components/0/props/0/value` |
| `ssp.system-security-plan.system-implementation.inventory-items[].props[].class` | 19 | `ssp#/system-security-plan/system-implementation/inventory-items/0/props/0/class` |
| `ssp.system-security-plan.system-implementation.users[].role-ids[]` | 2 | `ssp#/system-security-plan/system-implementation/users/0/role-ids/0` |
