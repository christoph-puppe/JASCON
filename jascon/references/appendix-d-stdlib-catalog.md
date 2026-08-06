# The JASCON Handbook
# Appendix D — stdlib Facet Catalog

**Purpose:** the standard library's facets — what each is for, what it
declares, what its payload looks like **in the field**. Every example
below is quoted verbatim from the gate-item-1 bundles (ISM, BSI,
CR26), not composed for the page: this catalog describes facets that
have already carried 93,259 values.

**Status convention.** The normative JSON Schemas shipped with gate
item 2 (2026-07-21): `schemas/stdlib/` carries the six descriptors,
`scripts/validate_core.py` is the executable, and the bundles'
in-place stubs are superseded (re-pinning lands with the next
converter run). Both converter-established shape conventions are now
decided: (a) the `by-statement` keying pattern is **normative** (D10
rev, backlog #7 — a payload key naming no statement of the host is a
validation error); (b) glossary hosting on a Set — typically the
corpus root — is **normative** (backlog #6, closed at gate 2; carrier
rejected via the D22 absorption clause). The D.12 audit promotions
shipped in the descriptors (backlog #8).

---

## D.1 `statement-grammar@1`

**Purpose:** the controlled-grammar decomposition of a clause —
action, result, specification, target categories — the authoring/QA
vocabulary behind BSI-style requirements engineering.
**Declares:** `[]` (chrome for computation; assessment semantics live
in D.6). **Payload:** `by-statement: {sid: {action, result,
result-specification?, target-object-categories[]}}`.
**Field sample** (BSI MS-TLS, KONF.14.1/smt):
```json
{"action": "verschlüsseln",
 "result": "Kommunikation beim Transport",
 "result-specification": "über Netze nach {{einem anerkannten Standard}}",
 "target-object-categories": ["Anwendungen"]}
```
Note the visible passenger: one of the 216 pseudo-placeholders rides
*inside* the grammar payload — preserved, reported, unrepaired
(§14.5). **Absorbs:** modal_verb/action_word/result/… ×~4,000 grammar
props. **Status:** high confidence; exercised at 1,015 statements.

## D.2 `security-objectives@1`

**Purpose:** protection-goal ratings and threat linkage per clause.
**Declares:** `[]` as shipped; **open question:** selection-class
candidacy (baselining by objective is a real selection use).
**Payload:** `by-statement: {sid: {confidentiality, integrity,
availability, authenticity, threat-refs[]}}` — rating values are the
authority's own scale, frozen by the pinned schema, not normalized.
**Field sample** (GS++, REA.1.2):
```json
{"confidentiality": "1", "integrity": "1", "availability": "1",
 "authenticity": "0",
 "threat-refs": ["https://ns.bsi.bund.de/gspp/threat/G-0.18"]}
```
**Absorbs:** C/I/A/Auth + threats ×4,494. **Status:** high;
exercised (899 threat-linked clauses).

## D.3 `terminology@1`

**Purpose:** defined terms with aliases — because, in the source's
own framing, when a defined term appears in a rule the definition is
part of the rule. **Declares:** `[]`. **Payload:** `terms: {id:
{term, definition, tag?, aliases[], note?, reference(+url)?,
do-not-link?}}` (+ `glossary-info` carrying the source block's
metadata). **Field sample** (CR26, FRD-IIR):
```json
{"term": "Initial Incident Report (IIR)",
 "definition": "An initial report about an incident that is supplied
  by FedRAMP Certified cloud service providers to FedRAMP and agency
  customers, ...", "tag": "Incident",
 "aliases": ["initial incident report", "IIR", ...]}
```
**Absorbs:** 75 FRD terms, 188 aliases; `uses-term` relations ×264
point in. **Hosting rule (decided at gate 2, backlog #6):** the glossary is
hosted on a **Set** — typically the corpus root — whose identity,
version, and lifecycle govern it; a dedicated carrier was rejected via
the D22 absorption clause (264/264 resolution measured with zero new
structure). **Status:** high; exercised; normative descriptor shipped.

## D.4 `reporting-obligation@1`

**Purpose:** who must be told what, where, how — the notification
duties that rules attach. **Declares:** `[]` as shipped; **open
question:** assessment-class candidacy (report duties are checkable).
**Payload:** `{notification[]: {party, method, target, name},
following-information[], following-information-bullets[]}`.
**Field sample** (CR26, IEC-CSO-IIR):
```json
{"notification": [
  {"party": "FedRAMP", "method": "email",
   "target": "fedramp_security@fedramp.gov", ...},
  {"party": "Agency Customers", "method": "varies",
   "target": "varies by agency",
   "name": "Follow agency-specific incident reporting procedures"}]}
```
That second entry is the honest kind: `varies` is data, not a gap.
**Absorbs:** notification ×23, following_information ×32+2.
**Status:** high; exercised.

## D.5 `effectivity@1`

**Purpose:** when obligations bite — enactment, maintenance,
adoption, grace. **Declares:** `[]` as shipped; **open question:**
selection-class candidacy (time-gated applicability is selection by
calendar). **Payload:** `{default?: window, <track>?: window}` with
window = `{is, current_status, date{obtain, maintain,
optional_adoption, grace{...}}}`. **Field sample** (CR26, family CCM,
per-track):
```json
{"20x":  {"is": "required", "date": {"obtain": "2026-07-04",
          "maintain": "2027-01-01", "grace": {"default": "2027-01-01",
          "until_next_assessment": true}}},
 "rev5": {"is": "required", "date": {"obtain": "2027-01-01", ...}}}
```
**Absorbs:** family effective ×7 + per-track ×20 — the RFC-0024
deadline machinery, machine-readable. **Status:** high; exercised.

## D.6 `assessment-criteria@1`

**Purpose:** what an assessor checks — required documentation,
artifacts, examples, key tests. The KSI shape's home. **Declares:**
`["assessment"]` — the one stdlib facet with computation semantics
from day one: tools that assess must understand or halt.
**Payload:** `{required-documentation[]?, required-artifacts[]?,
default-artifacts?, examples[]: {id, examples[], key-tests[]}?,
summary?}` (by-statement keyed where per-clause).
**Field samples** — GS++ (REA.1.2): `{"required-documentation":
["Übungs- und Prüfplan"]}` · CR26 (SCN-TRF-TPR):
```json
{"id": "Tips on transformative changes",
 "examples": ["The addition, removal, or replacement of a critical
   third party service ...", "Increasing the security categorization ..."],
 "key-tests": [...]}
```
**Absorbs:** documentation ×966, artifacts ×53+, examples/key-tests,
the corpus default-artifacts block. **Status:** high; exercised
across all three corpora.

## D.7 `system-context@1` — *medium confidence*

**Purpose:** the SSP's system-characteristics residue — deployment
model, data types, boundary narrative — as a facet on Components.
**Declares (planned):** `[]`. **Status:** medium, **pending Rev5-era
verification** of the field inventory; concept-exercised in the
example bundle only, not yet corpus-driven. The honesty rule: this
entry ships as a placeholder with its evidence gap named, or it
doesn't ship.

## D.8 `assurance-levels@1` — *medium confidence*

**Purpose:** graded assurance/impact levels (Low/Moderate/High
families and kin) as declared vocabulary rather than magic strings.
**Declares (planned):** `["selection"]`. **Status:** medium, pending
the same Rev5-cycle confirmation; unexercised. Candidate first
corpus: the CR26 class system's interplay with impact levels.

## D.9 The Canonical Reference Facet (`sp800-53@…`) — NIST-owned

**Purpose:** SP 800-53's document conventions — statement/guidance/
objective structure, ODP practices — as a facet **NIST owns and
maintains**, shipped by default, first among equals in visibility,
governed by the same rules as everyone (D11: "the standard library,
not the constitution"). **Status:** the arrangement is decided; the
schema is NIST-side work aligned with gate items 2–3 (the CTL
overlay's ODP assignments are its first waiting customer — see
D.10).

## D.10 The compat facet (`oscal-1x@1`) — the waiting room, clocked

**Purpose:** Level-2 migration holding pen (D16): preserved,
schema-carried, visibly *undecided* — with intended deprecation in
its descriptor and a residue KPI per release (§14.6).
**The clock started at these measured numbers:**

| Corpus | Residue | Content |
|---|---:|---|
| ISM | 539 payload entries | guideline `overview` narratives on Sets |
| BSI | 179 requirements | `param-extras` (label/default/alt-id) — feeds the open D9 scalar-default question |
| CR26 | 29 + 5 objects | rule & KSI `class-variants` (full variant fidelity; feeds the open D13 ceremony question) |
| CR26 | 79 entries | the CTL Rev5 overlay — parked until the NIST catalog conversion (gate 3) supplies statement addresses |

Every row has a named exit: a spec decision, a facet graduation, or a
gate-3 dependency. A row without an exit would be a prop with a
registration number — the smell §14.6 warns about.

## D.11 Framework facets (the sanctioned open category — not stdlib)

Authorities mint their own, registered and pinned like anything else.
The gate produced five real ones: **`gspp-taxonomy@1`**
(sec-level/effort/tags/class/practice — sample from KONF.14.1:
`{"sec-level": "normal-SdT", "effort": 2, "tags": ["Produktbeschreibung",
"Cryptography", "Zero Trust"], ...}`), **`gspp-narrative@1`**
(guidance + layer descriptions), **`cr26/scope@1`** (subset
applicability — sample: `{"types": ["20x","Rev5"], "paths":
["Program","Agency"], "classes": ["B","C","D"], "affects":
["Providers"]}` — declares `["selection"]`, and earns it: the class
Sets are computed from it), and **`cr26/narrative@1`** (notes,
danger, corrective actions). The five-question routing map that
decides kernel-vs-stdlib-vs-framework-vs-annotation-vs-nothing is
Chapter 7's; the measured base rate stands: >70 % of legacy props
needed **no** facet at all.

## D.12 Declaration audit & the parked list

| Facet | Normative declaration (gate 2) | Disposition |
|---|---|---|
| statement-grammar | `[]` | chrome-for-computation confirmed |
| security-objectives | `[selection]` | **promoted** (backlog #8): objective-driven baselining is selection |
| terminology | `[]` | **hosting decided** (backlog #6): Set-hosted, typically corpus root; carrier rejected (D22 absorption) |
| reporting-obligation | `[assessment]` | **promoted** (backlog #8): notification duties are checkable; anticipated kernel candidate when an EU corpus lands |
| effectivity | `[selection]` | **promoted** (backlog #8): time-gated applicability is selection by calendar |
| assessment-criteria | `[assessment]` | confirmed by use; gains `frequency` (CIS cadence) and audit/remediation/method (benchmark shape) |
| cr26/scope (framework) | `[selection]` | the exemplar the promotions followed |
| system-context · assurance-levels | — | **parked** (P10 #35, 2026-07-22 — the gate-3 clock ran out and the verdict is recorded): the Rev5/IFA corpus surfaced the need as a *framework* facet (`https://ifa.gov/goodread/facet/system`) and as levels-as-Sets, not as stdlib payloads; both park beside `privacy-assessment@1` and ship when a corpus demands the stdlib shape |

The governing principle, quoted from the user directive that decided
#8: **a tool that cannot handle a facet must stop working on that
data** — fail-closed engages only when declarations are honest.

**Parked:** `privacy-assessment@1` — deliberately not shipped until
the Rev5-era privacy corpus is measured; a privacy facet designed
from memory would violate the book's only method. The audit table
above *is* the candidate list: no facet is proposed here that the
corpora haven't already asked for.
