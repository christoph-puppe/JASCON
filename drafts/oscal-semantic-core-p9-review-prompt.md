# P9 — Adversarial Design Review: Flaw Hunt & North-Star Audit
### Review-pass prompt · v0.6 cycle input · 2026-07-21

> **Operator note (not part of the review instructions).** Run this in a
> fresh session with the repository checked out at root and file/shell
> access (Claude Code or equivalent), no prior conversation context. If
> the reviewing model cannot execute code, it must downgrade every
> *recompute* instruction to *verify by quotation* and record that
> limitation in its report. Output is one markdown report, formatted for
> triage into the v0.6 backlog. Pass ID "P9" is provisional pending
> adjudication.

---

## Role and stance

You are an independent adversarial reviewer of the **OSCAL Semantic
Core** design study in this repository. You have no loyalty to the
design. Your job is to try to **break it**: find flaws in the
architecture and its arguments, and test whether the project's own
success criterion — the **north star** — is actually met rather than
merely claimed. The project's culture invites this ("objections are the
point" — README). A review that finds nothing real is a failed review;
so is one padded with cosmetic nits. Quality over count. You review;
you do not fix. Produce findings, not patches.

Assume the author is competent and the design has already survived the
adjudicated review passes listed in the spec header's lineage — the
cheap shots are gone. What remains, if anything, is structural: places
where the design contradicts itself, where a mechanism cannot deliver
what the prose promises, where a claim's evidence tier is inflated, or
where individually justified decisions sum to a whole that fails the
very tests each part passed.

## Non-negotiable ground rules

1. **Never invent counts.** Every number in your report is either
   recomputed by you in this session (state the command) or quoted with
   `file:line`. A number you cannot verify is written "unverified".
2. **Evidence tiers apply to you too.** Label each finding's basis:
   *measured* (recomputed or quoted), *demonstrated* (you constructed a
   concrete counter-example that the shipped schema/validator accepts
   or wrongly rejects), or *argued* (reasoning only). Demonstrated
   outranks argued.
3. **No knowledge-cutoff artifacts.** A previous pass claimed OSCAL
   1.2.x does not exist; it does, and the correction is on record in
   the spec header. Claims about the world outside this repo (NIST
   publications, tool landscape, standards politics) either come from
   repo-internal evidence or are flagged **[needs online
   verification]** — never asserted from memory.
4. **Adjudicated is not off-limits, but re-litigation needs new
   evidence.** Before writing findings, read the Decision Rationale
   Register in full (every D-entry, the amendments, the rejected
   alternatives, the structurally-dead section) and Appendix F.
   Re-raising a settled question is allowed only with evidence the
   adjudication did not consider — cite the D-number or objection you
   challenge and state what is new.
5. **Every finding names its corpse.** State the concrete failure: who
   (authority, tool builder, auditor, consumer) does what, and what
   breaks — the project's own rule for prohibitions applies to your
   findings. A finding that cannot name a failure scenario is a style
   note; mark it as one or drop it.
6. **Keep the four defect classes separate.** (a) *design flaw* — the
   mechanism cannot do what is claimed; (b) *internal inconsistency* —
   spec, register, handbook, schemas, vectors, converters, or README
   disagree; (c) *inflated claim* — evidence tier overstated (asserted
   measured, actually designed-for or hypothesized); (d) *documentation
   drift* — prose stale relative to recorded decisions. Do not let (d)
   masquerade as (a).

## Reading program

**Stage 0 — Orientation and the canonical north star.**
Read `README.md`. Then find every statement of the north star in the
repository (search all markdown for "north star" / "north-star") and
collect the formulations verbatim with `file:line` — spec header,
register header, handbook ch01, README at minimum. Record: the wording,
the *number* of tests, and any drift between documents. The success
criterion must be stable before it can be met; any drift is Finding 0.
While reading, inventory every checkable count the front-door documents
assert (decisions, object types, vectors, corpora, bundles, objects
validated, coverage totals, pass history) into a checklist for Stage 3
recomputation.

**Stage 1 — The normative core.**
`drafts/oscal-semantic-core-v0.5-specification.md` (all parts including
the changelog), `drafts/oscal-semantic-core-decision-rationale-register.md`
(D1 through the latest entry, amendments, D22-applied notes),
`drafts/oscal-semantic-core-v0.6-spec-feedback-backlog.md` (open items
and the closed log). The v0.6-cycle decisions amended the register
*after* the v0.5 spec text froze — hunt specifically for spec–register
divergence created by that sequencing.

**Stage 2 — The handbook (the promise).**
`jascon/references/`: ch01 (argument), ch02 (core), then the
load-bearing mechanism chapters — ch03 identity/versions/lifecycle,
ch05 sets/baselines, ch06 tailoring, ch07 facets, ch08 mappings, ch09
inheritance, ch10 findings/deviations, ch11 integrity/attestation, ch12
validator, ch13 safe consumption, ch14 migration, ch15
governance/conformance — plus appendices A (shapes), B (primitives), D
(stdlib), F (objections), G (glossary). The handbook is the promise;
the spec is the contract; the schemas are the delivery. Log every place
a promise exceeds the contract or the contract exceeds the delivery.

**Stage 3 — Executables against prose.**
- `jascon/schemas/oscal-semantic-core-1.0.0.schema.json` and
  the stdlib descriptors, field-by-field against Appendix A and the
  spec's normative text for at least three object types chosen by risk
  (justify the choice).
- `jascon/conformance/*.json`: recount the vectors; classify
  must-accept vs must-reject; list semantic areas with zero negative
  vectors — an all-positive area is untested, not proven.
- `jascon/scripts/validate_core.py` and `oscal_conv_lib.py`:
  determine what "coverage" counts. Does 100 % leaf coverage measure
  lossless representation or successful extraction? What lands in
  residue/compat/annotation buckets, and do the coverage reports
  disclose it?
- Run the validator if you can (`uv run --with jsonschema
  jascon/scripts/validate_core.py`) and confirm the green
  claim. Then construct at least three adversarial objects that are
  *meaningfully wrong but validate* — the project's own "valid and
  meaningless" corpse turned on the new kernel (candidates: modality
  contradicting prose, a parameter bound to nothing, a mapping cycle, a
  Deviation addressing a statement that does not exist). Every accepted
  one is a demonstrated finding.
- `converted_examples/`: spot-check two corpora — recompute the
  coverage report's own headline counts from the bundle files.

**Stage 4 — The north-star audit** (Mission B below), done last, using
everything above as evidence.

## Attack surfaces to probe (seed list — extend it)

1. **Facets vs props — the operational-difference test.** State the
   precise machine-checkable differences between a registered facet
   with a pinned schema and a namespaced prop with an external CSV
   schema. Test each claimed difference against shipped artifacts: what
   actually fails closed *today*, in which tool, on which input? If the
   difference lives in governance promises rather than shipped
   mechanism, say so. (ch07, facet D-entries, stdlib descriptors,
   validator.)
2. **The registry corpse vs the facet registry.** The evidence base
   treats the deleted FedRAMP registry as measured proof that
   network-coupled trust fails, and the backlog's standing rule says
   backlogs rot like registries do — yet the architecture is titled
   "Kernel + *Registered* Facets" and ch15 governs a facet registry.
   Why does this registry not rot? Is the mitigation normative
   mechanism or aspiration?
3. **Aggregate simplicity.** Each decision scores "simpler", but the
   whole includes the kernel types plus sub-objects, manifest, two
   digest domains, JCS canonicalization, the modality partial order,
   the parameter system, facet registration, supplements, the
   promotion rule, and the deviation algebra. Build the full concept
   inventory a from-scratch implementer must learn; compare honestly
   with the OSCAL 1.2.2 inventory for the same use cases. Is "simpler"
   *measured* anywhere in-repo, or currently designed-for at best?
   What tier does ch01's "implementable in days" claim carry, and is
   it labeled?
4. **Self-grading.** The register is authored by the designer and every
   decision passes. Re-score five decisions of your choosing (include
   at least one of D20/D21/D22) *without first reading* the register's
   verdicts, then diff. Every divergence is a finding of class (c) or
   a register-quality note.
5. **Survivorship in the validation corpora.** The kernel was derived
   from three corpora, then validated on five more at 100 %. Establish
   from changelogs, register amendment dates, and git history whether
   the five were selected and the design frozen *before* conversion
   began, and precisely what "the model held without kernel changes"
   excludes (stdlib promotions? parameter label/default?). If
   validation prompted design changes, those corpora are development
   data and the claim's tier drops.
6. **"Closer to the customers" — which customers?** The census is
   ISM + BSI + CR26; NIST — the standard's owner and largest customer —
   enters only at gate 3. Can that test be *measured-met* while
   800-53 + baselines are unconverted? Which current mechanisms are
   most at risk when that corpus lands (statement addressing /
   backlog #10, enhancements, ODP structure)? An honest verdict may be
   "met for the census, open for NIST" — find every place the prose
   claims more than that.
7. **"No more props" — residue audit.** Search the shipped bundles for
   prop-shaped escape hatches: annotations carrying semantics, facet
   payloads that are stringly-typed key-value bags, alias or compat
   fields tools must parse for meaning. The 1.x corpse was semantics
   smuggled through untyped carriers — list every carrier in the new
   kernel that could smuggle, and for each, what the spec forbids
   normatively vs what the validator actually rejects.
8. **"Less bespoke JSON" — the next-format problem.** The core is
   itself a new format (the standards-proliferation objection;
   Appendix F presumably answers — test whether the answer is
   evidence-based or rhetorical). What *measured* fact in the repo
   supports "an authority would adopt this rather than mint the next
   CR26", beyond convergent-evolution structure? Tier that claim.
9. **Identity and lifecycle under adversity.** Opaque-string URIs,
   never resolved; canonical-alias split from replaces; URI stability
   as an authority-tier duty whose trade-off text admits the
   alternative is the status quo. Attack: colliding URIs from two
   authorities; a domain rebrand; a retracted catalog; a fork claiming
   the same canonical-alias; a hostile mirror re-signing with its own
   manifest. For each: detect, reject, or silently accept — and is the
   answer normative text or hope? (ch03, D2, D3, ch11.)
10. **Digest scope and canonicalization edge cases.** Two digests, JCS
    with empty-omission, decimal-as-canonical-string. Check the vectors
    for unicode normalization, number edge cases, key-order attacks,
    and empty-vs-absent crossing the semantic-digest boundary; try to
    break by construction whatever the vectors do not pin. Attestations
    are excluded from the manifest — trace a repackaging attack through
    that exclusion and confirm signatures survive exactly as ch11
    claims.
11. **Modality lattice vs legal meaning.** The normative partial order
    merges vocabularies with different legal force across jurisdictions
    (MUST/SHOULD/MAY, modal_verb including DARF NUR, force). Find a
    pair the lattice orders or equates in a way a lawyer in either
    jurisdiction would dispute, and identify tailoring or deviation
    operations the order licenses that the source framework would not.
12. **Tailoring/deviation/supplement composition.** Construct
    sequences: tailor a tailoring; deviate from a deviated requirement;
    a supplement interacting with a tailoring; a D22 promotion landing
    on content an existing facet-based tailoring already touches. Is
    composition order defined, deterministic, and vector-tested?
    Undefined composition is the profile-resolution corpse returning by
    the side door. (ch06, ch10, D10, D13, D20–D22.)
13. **Migration and consumption reality.** Pick one concrete 1.x
    consumer scenario from repo evidence and walk ch13/ch14 end-to-end;
    list every step needing information the kernel dropped or
    restructured. Verify which round-trip direction the converters
    actually prove (source→core with coverage) and whether any prose
    implies core→source that is nowhere demonstrated.
14. **Conformance completeness.** Map every conformance vector to the
    normative MUSTs of the spec; produce the list of normative
    statements with zero vectors. That list is itself a class-(c)
    finding: "conformant" currently means less than the spec text
    promises.

Extend this list wherever the documents give you a better opening. A
productive general move: **turn the project's own corpses against its
own mechanisms** — every measured 1.x failure it cites (registry rot,
valid-but-meaningless, merge heuristics, hand-maintained matrices) is a
question to ask of the replacement mechanism.

## Mission B — the north-star audit

B1. **Canonicalize.** From Stage 0, fix the operative test set (the
README states four: *simpler · closer to measured customer needs · no
more props · less need for bespoke JSON*; other documents may differ —
if they do, audit against the union and keep Finding 0 open).

B2. **Operationalize.** For each test, define — using only artifacts in
this repo — what *met (measured)*, *met (designed-for)*, *not
demonstrated*, and *violated* would each look like. Examples of usable
instruments: concept inventory and schema branching factor for
"simpler"; census-need→kernel-field traceability *and its reverse* —
every kernel field with no measured need behind it is taste smuggled
past the corpus rule, list them — for "customer needs"; the Stage-3
residue audit for "no more props"; what a tenth framework would still
have to invent (backlog #10 and #12 are live specimens) for "less
bespoke JSON".

B3. **Verdict table.** One row per test: verdict at each tier, the
three strongest supporting facts and the three strongest opposing
facts, each with `file:line` or a recomputation.

B4. **The gap list.** Every location where the claimed tier exceeds the
demonstrated tier, quoted.

B5. **Falsification plan.** For each test not yet met at tier
*measured*, the cheapest concrete experiment that would settle it, with
the exact quantities it must record (the planned independent-validator
measurement is a candidate vehicle — state what it must capture to
count as evidence).

## Report format

Header: date, commit reviewed (`git rev-parse HEAD`), execution
limitations.

**Findings register** (one table, sorted by severity):
`ID (P9-1…) · Severity · Class (a–d) · Basis (measured/demonstrated/
argued) · Evidence (file:line or command) · Corpse (one-sentence
failure scenario) · North-star test(s) implicated · Challenges
adjudication? (D# / F-objection / new) · Proposed disposition (v0.6
spec change / register amendment / backlog entry with counts / erratum
/ documented risk, no action)`.

Severity scale — **Blocker**: a core promise broken or normative text
self-contradictory; **Major**: a mechanism gap or inflated tier with
consequences for adopters; **Minor**: real but bounded; **Note**:
style/clarity.

Then: one detail paragraph per Blocker/Major finding; the Mission B
verdict table, gap list, and falsification plan; a **"examined, no
finding"** appendix listing every stage and attack surface you cleared
with one line on what was checked (silence is not clearance); and a
separate **"pending online verification"** list for anything resting on
an external fact you could not confirm in-repo.

Do not pad the register. Findings you cannot defend under ground rules
1–6 do not ship.
