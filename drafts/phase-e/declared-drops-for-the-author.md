# Declared drops, for the author's decision (phase E, 2026-11-14)

The author's rule of 2026-11-14: "Real content is never dropped. [...]
What may stay out of a bundle is only what is not content: a name that
merely selects a field, a namespace, an id that is rebuilt exactly from
another value. [...] Go through every drop that is declared today, in all
six ledgers (IFA included), and list for me which of them are content
under this rule. Do not decide those yourself."

Every row below is a drop that a converter still declares. Counts are
read from the committed ledger records (**measured**). The column
"reading" is the reading of the agent that reworked the converter, or
mine for IFA (**argued**); it decides nothing. The column "decision" is
the author's.

What is no longer here: every value the rework carried, and every value
that is now no content by a rule the ledger checks (a name that selects,
a namespace, an id rebuilt exactly). Those are counted in each ledger
record under `not-content`, with the rule.

Status: IFA, ISM, CSF and Grundschutz++ are final on the session
branch. SP 800-53 and CR26 follow when their reworks are merged.

## Summary

| Corpus | Source values | Declared drops | Of which the reading says content |
|---|---:|---:|---:|
| US.IFA-GoodRead | 835 | 296 | see table: most |
| AU.ISM | 36,161 | 1 | 1 |
| US.CSF | 4,726 | 182 | 95, and the 87 names that go with 87 of them |
| DE.BSI | 49,431 | 6 | 6 |
| US.SP800-53 | 115,680 | *pending* | |
| FedRAMP-CR26 | 7,532 | *pending* | |

Three classes recur across corpora, so one decision may settle several
rows:

- **A. The uuid of the source document** (`catalog.uuid`): ISM, CSF,
  Grundschutz++, and the documents' own uuids among IFA's 84.
- **B. Back-matter resources that no link of a control names** (CSF 4
  uuids and 3 media types; Grundschutz++ one whole resource). In both
  corpora the root Set now carries the metadata links that name these
  resources by uuid, so without them the links resolve to nothing in the
  bundle.
- **C. IFA's classes decided on 2026-11-13** (revision history,
  directory of parties and roles, links to other serialisations, type
  tags, uuids). They were decided before the rule of 2026-11-14; under
  that rule most of them read as content.

## US.IFA-GoodRead (835 values; 296 declared drops)

| Values | Paths | Declared reason (shortened) | Example | Reading | Decision |
|---:|---:|---|---|---|---|
| 84 | 48 | the uuid of a source element; objects get URIs minted from names and titles | `ssp#/system-security-plan/metadata/parties/3/uuid` | content: a uuid is not rebuilt from any value of the bundle; some are the targets of references in the source | |
| 57 | 31 | a link to another serialisation of the source, to an imported document or to the catalogue (back-matter, `import-*`) | `ssp#/system-security-plan/import-profile/href` | content: titles and addresses of documents the source refers to | |
| 56 | 28 | revision history of the source document | `ssp#/system-security-plan/metadata/revisions/0/title` | content: dates, versions and titles of earlier revisions | |
| 56 | 36 | the source's directory of parties and roles | `ssp#/system-security-plan/metadata/roles/0/id` | content: names and roles of the parties the documents name | |
| 18 | 6 | the leveraging plan's own entry for a component of the leveraged system; the provider's Component stands for it | `lvg#/.../components/1/type` | content where it differs from the provider's Component; where equal it could be a checked duplicate (`same()`). Not measured which | |
| 11 | 8 | a type tag of a structural element (`subjects[].type`, `actors[].type`, ...) | `ap#/assessment-plan/assessment-subjects/0/type` = `component` | possibly no content, as an id rebuilt exactly: the type equals the kind of the object the reference resolves to. Not checked by the ledger today, so it stays a drop | |
| 8 | 6 | a reference to a party the source defines without a name | `lev#/.../responsible-roles/0/party-uuids/0` | content: it says that a party is responsible, though it cannot be named by a landmark URI | |
| 3 | 3 | the assessment results' earlier state of a risk the POA&M carries in its later state | `ar#/assessment-results/results/0/risks/0/title` | content: the history of the risk | |
| 1 | 1 | a defect of the source: a task names an activity its document does not define | `ap#/assessment-plan/tasks/0/associated-activities/0/activity-uuid` | a reference that resolves to nothing. Could be carried verbatim and reported. The author decides whether a broken reference is content | |
| 1 | 1 | a defect of the source: a POA&M item names a risk the POA&M does not define | `poam#/.../related-risks/0/risk-uuid` | as above | |
| 1 | 1 | a defect of the source: a satisfied entry names a responsibility the leveraged plan does not define | `lvg#/.../satisfied/0/responsibility-uuid` | as above | |

## AU.ISM (36,161 values; 1 declared drop)

| Values | Path | Declared reason | Example | Reading (agent) | Decision |
|---:|---|---|---|---|---|
| 1 | `ism.catalog.uuid` | the uuid of a source element (as decided for IFA) | `36766a6f-e174-4292-a03e-fcb3b4b09201` | content: the identity of this version of the source document; nothing in the bundle rebuilds it | |

## US.CSF (4,726 values; 182 declared drops)

| Values | Path | Declared reason | Example | Reading (agent) | Decision |
|---:|---|---|---|---|---|
| 87 | `...controls[].props[].value` (79 subcategories, 8 categories) | the sort-id of a withdrawn item that names a successor; the item is no object, its lineage stands on the successor | `00002.00001.00006` | content: the order of withdrawn items among their siblings | |
| 87 | `...controls[].props[].name` (79 + 8) | goes with the value above (a name that selects a value that is dropped) | `sort-id` | not content, because the name only selects that value. It follows the decision on the row above | |
| 4 | `csf.catalog.back-matter.resources[].uuid` | the uuid of a source element (as decided for IFA) | `3ab41d8a-...` | content: the metadata links, now carried, name a resource by it | |
| 3 | `csf.catalog.back-matter.resources[].rlinks[].media-type` | a link to another rendition of the source (as decided for IFA) | `application/pdf` | content: it says what the address leads to | |
| 1 | `csf.catalog.uuid` | the uuid of a source element (as decided for IFA) | `720a010b-...` | content: identifies the source document; cannot be rebuilt. (Measured by the agent: it equals the uuid of the fourth back-matter resource) | |

## DE.BSI, Grundschutz++ (49,431 values; 6 declared drops)

| Values | Path | Declared reason | Example | Reading (agent) | Decision |
|---:|---|---|---|---|---|
| 1 | `gspp.catalog.uuid` | the uuid of the catalogue document (as decided for IFA) | `73f2d8f6-...` | content: identifies this document; nothing in the bundle rebuilds it | |
| 5 | `gspp.catalog.back-matter.resources[]` (`uuid`, `title`, `rlinks[].href`, `rlinks[].hashes[].algorithm`, `rlinks[].hashes[].value`) | a back-matter resource that no link of a control names (as decided for IFA) | `BSI IT-Grundschutz Edition 2023` | content: the root Set now carries the metadata link `#bf7510ca-...`, which names nothing without this resource | |

## US.SP800-53 and FedRAMP-CR26

Pending: the reworks are being finished. The two rows of CR26 that its
earlier agent reported are the update history of an entry (957 values)
and the process-flow diagrams (35); its reading of both was "content".
