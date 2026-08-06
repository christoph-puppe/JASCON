# The JASCON Handbook
# Appendix E — Worked Corpora

**Purpose:** four requirements walked end to end — source form,
converted form, the decisions applied, and what a validator checks.
Unlike every earlier draft of these examples, **nothing here is
composed for the page**: every JSON excerpt is quoted from the
gate-item-1 bundles on disk (`bsi-core-bundle`, `ism-core-bundle`,
`cr26-core-bundle`), and §E.5 records what the act of extracting them
*fixed* — because worked examples that never bite are decorations.

---

## E.1 KONF.14.1 — the protagonist, in its real skin

**Source (MS-TLS catalog):** one control, `label` prop `VER.2`,
alt-identifier, taxonomy props, **two nested pseudo-controls**
(KONF.14.1.1, .2), one param whose label fuses alternatives
(`"TLS 1.3 (oder TLS 1.2 mit PFS)"`), and statement-part grammar
props carrying one of the 216 defects.

**Converted** (`objects/mstls/req-konf-14-1.json`, excerpts):
```json
{"id": "https://ns.bsi.bund.de/mstls/req/KONF.14.1",
 "label": "VER.2", "title": "Verschlüsselung beim Transport",
 "aliases": [{"scheme": "bsi-uuid", "value": "99806244-..."}],
 "statements": [
  {"id": "smt", "modality": "may",
   "parameters": [{"name": "konf.14.1-prm1", "type": "string"}],
   "prose": {"de": "Konfiguration für Anwendungen KANN Kommunikation
     beim Transport über Netze nach {param:konf.14.1-prm1} ..."}},
  {"id": "KONF.14.1.1", "modality": "must",
   "prose": {"de": "... MUSS unverschlüsselte und anfällige
     Verbindungen über Netze ..."}},
  {"id": "KONF.14.1.2", "modality": "unspecified",
   "prose": {"de": "Bei Einsatz von Webservern MUSS ..."}}]}
```
Facets on the object: `statement-grammar@1` (the KANN/verschlüsseln
decomposition, **with `{{einem anerkannten Standard}}` riding
visibly** — defect #14 of 216, preserved not repaired),
`assessment-criteria@1` (Konfigurationshistorie),
`gspp-taxonomy@1` keyed by-statement (each clause keeps its own
sec-level/effort/title/alt-id — KONF.14.1.1 carries effort 4 against
the parent's 2), `gspp-narrative@1` (guidance per clause), and the
compat waiting room holding `param-extras` — where the fused
`"TLS 1.3 (oder TLS 1.2 mit PFS)"` sits pending the choice-analysis
that Chapter 4 prescribes and the open D9 default-value decision.

**What to notice.** The nested controls are now what they always
were: identified clauses. The Chapter 6 identity-addressing demo
works against this literal object (`statement-id: "KONF.14.1.1"`).
And **statement KONF.14.1.2 is a finding**: its prose says MUSS, its
grammar props omit `modal_verb` — one of exactly **9** such clauses
corpus-wide (1,006 declared / 1,015 statements). The converter maps
the declared channel and refuses to guess from prose; the 9 join the
216 in the authors' queue. Grammar coverage: 99.1 %, now a number.

**Validator checks:** `prose-params-resolve` (the `{param:}` token
binds), `unique-within` (three statement ids), `code-from`
(modalities, `normal-SdT`), and the break-it recipe: change the
smt token to `{param:typo}` and watch B.1.5's message print.

## E.2 IEC-CSO-IIR + class tailoring — variance made explicit

**Source (CR26):** a rule that **exists only as class variants** — no
base `statement`, no base `force`; four variant objects (a: SHOULD ·
b/c/d: MUST), six defined-term references, notification duties.

**Converted** (`objects/req/iec-cso-iir.json`, excerpts):
```json
{"label": "IEC-CSO-IIR",
 "statements": [{"id": "s1", "modality": "unspecified",
   "obligated-parties": [".../cr26/party/providers"],
   "prose": {"en": "Initial Incident Report (requirement varies by
     certification class; see class tailorings and the
     class-variants payload)."}}],
 "relations": [
   {"type": "uses-term", "ref": ".../cr26/term/FRD-IIR"},
   {"type": "uses-term", "ref": ".../cr26/term/FRD-AAP"}, ...],
 "facets": {
   "reporting-obligation@1": {"notification": [
     {"party": "FedRAMP", "method": "email",
      "target": "fedramp_security@fedramp.gov"}, ...]},
   "compat oscal-1x@1": {"class-variants": {
     "a": {"force": "SHOULD", "statement": "...SHOULD responsibly
           notify all affected parties..."},
     "b": {"force": "MUST", "statement": "...MUST responsibly..."},
     "c": {"force": "MUST", ...}, "d": {"force": "MUST", ...}}}}}
```
And in the **class Tailorings** (real ops): class-b/c/d carry
`{"op": "set-modality", "requirement-ref": ".../req/IEC-CSO-IIR",
"statement-id": "s1", "modality": "must"}`; class-a sets `should`.
All monotone from `unspecified` — no Deviation needed, and across the
full corpus **none was**: 111 ops, zero easings, the channel's
emptiness measured. The synthesized base prose is flagged (one of 29)
— the converter's honesty about a source that models some
obligations *only* as variants. The prose variance itself sits in
L2, which is precisely the **open D13 ceremony question**: when the
*authority* publishes four texts, is `replace-prose(substantive)+
Deviation` the right liturgy, or does authority-variance deserve its
own shape? The corpus has now voted that the question is real (29
rules) — v0.6 decides.

Companion case with computable deltas: **VDR-TFR-PDD** — class-b op
`set-modality → should` sits beside per-class timeframes (3 months →
1 month → …) that stay in L2 because the base has *no* timeframe to
tailor — the 51 first-flagged "unit-class crossings" all turned out
to be this base-absent pattern (true crossings: **0**; correction on
the record, see E.5).

**Validator checks:** `references-resolve` (six term refs land — see
E.5), op addressing, `modality-monotonic` on all 111 ops.

## E.3 ISM-1997 — the narrative-framework pattern

**Converted** (`objects/req-ism-1997.json` + memberships):
```json
{"label": "ISM-1997", "statements": [{"id": "smt",
  "modality": "unspecified",
  "obligated-parties": [".../ism/party/organisation"],
  "prose": {"en": "The board of directors or executive committee
    defines clear roles and responsibilities for cyber
    security ..."}}]}
```
Member of **six Sets**: all five applicability baselines
(NC · OS · P · S · TS) and the ISM-control category set — the 5,301
membership props, dead and buried in `members[]`. **The pattern this
example carries:** `unspecified` is not a defect here. ISM prose is
declarative present tense; modal verbs are structurally absent
(1,149/1,150); binding force *is* baseline membership. A Core-tier
framework, converting with zero facets and zero apology — the
architecture's promise that narrative frameworks are first-class,
kept on a real corpus.

**Validator checks:** membership expansion through nested taxonomy
Sets; `sequence` monotonicity; the annotation-free semantic digest
equals the package-digest content (nothing to strip).

## E.4 The KSI mapping — §8.6 at scale, one specimen of 373

**Converted** (`objects/map/ksi-ced-rat--ir-2.json`, verbatim):
```json
{"id": ".../cr26/map/ksi-ced-rat--ir-2",
 "source-ref": ".../cr26/ksi/KSI-CED-RAT",
 "target-ref": "https://ns.nist.gov/sp800-53/req/IR-2",
 "relationship": "supports",
 "direction": "source-to-target",
 "confidence": "draft",
 "rationale": "Imported from CR26 KSI control list; the source
   carried no typed relationship (handbook 8.6).",
 "provenance": {"author-ref": ".../cr26/party/fedramp",
   "date": "2026-07-14"}}
```
One row of an untyped link list became one honest object: `supports`
not `equal` (flattery refused), `draft` not `authoritative`
(diligence graded), provenance named (whose claim), rationale stating
its own limitation. The SCF spreadsheet import — thousands of rows —
is this exact pattern at scale and is gate item 3's work; the 373
here are its proof of mechanism. The source KSI meanwhile is a
Requirement whose `uses-term` relations resolve into the glossary
(FRD-INT, FRD-PER, FRD-VLR).

---

## E.5 What working these examples fixed — the appendix's own ledger

Extracting E's excerpts from the real bundles caught, in one
afternoon, exactly the class of defects this architecture exists to
catch — in our own converter first:

1. **Broken term cross-references.** `uses-term` refs were minted
   from display *names* (spaces and all) while the glossary keys are
   FRD ids. Fixed with a term+alias index — and the fix produced a
   finding: **all 264 term references resolve, zero unresolved** —
   the FRD's 188 aliases earn their keep measurably.
2. **A mislabeled phenomenon.** The "51 unit-class crossings" were,
   on refined counting, **51 base-absent variant timeframes and 0
   true crossings** — demoting the D9 duration-union question and
   promoting the D13 authority-variance question, with Appendices A
   and C corrected on the record.
3. **A source finding.** 9 clauses whose prose says MUSS while the
   grammar layer omits `modal_verb` (E.1) — grammar coverage 99.1 %,
   queued for the authors beside the 216.

What E does **not** yet contain, by the same honesty: SSP/AP/AR/POA&M
lifecycle walks and SCF at scale (gate item 3), and a predicate-
selection or replace-prose worked case (gate item 2's conformance
corpus). The empty slots are labeled because the census taught us
what unlabeled empty slots become.
