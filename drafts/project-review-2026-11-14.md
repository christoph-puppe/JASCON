# JASCON — whole-project review, 2026-11-14

**What this is.** A review of the repository by independent sub-agents, asked for
by the author. Ten reviewers worked in parallel without seeing each other's
work: goals and claims (A), necessity (B), a cold author (C), two cold consumers
(D1, D2), a cold implementer (E), architecture and scale (F), security and trust
(G), assurance (H), governance and alternatives (I). Six checkers then tried to
refute every finding that blocks or weighs heavily and every positive result a
verdict rests on. An orchestrator prepared the yardstick, briefed, compared and
wrote this report. All of them are instances of one AI model family; the
author will have the report checked by other models.

**What was reviewed.** Commit 430cf15 on branch `claude/sleepy-planck-g6w3h3`,
which is 164 commits ahead of `origin/main` (1daae7f) and has no pull request.
The tree holds specification **2.0.0-rc.4**; the brief for this review named
rc.3, whose file is gone from the tree. The released text is 1.0.0 of
2026-07-22.

**What ran here** (Linux container, Python 3.13.18, Node 22.23.4, 2026-11-14):

| Command | Result |
|---|---|
| `python3 jascon/scripts/validate_core.py` | exit 0, `ALL GREEN`; 705 checks in 18 vector families, 0 fail; bundles AU.ISM 1,732 pass, DE.BSI 1,288, US.CSF 140, US.IFA-GoodRead 18, US.SP800-53 1,042, example pack 3, example folder 27 |
| `python3 jascon/scripts/test_oscal_conv_lib.py` | 65 tests OK |
| `python3 jascon/scripts/test_attestation_binds.py` | 15 tests OK, 1 skipped |
| `python3 jascon/scripts/test_convert_obligated_party.py` | 8 tests OK |
| `node --test "jascon-app/tests/*.test.mjs"` | 185 tests: 180 pass, 0 fail, 5 skipped |
| Four catalogue conversions from pinned sources | byte-identical to the tree (run twice, on copies) |
| PowerShell twin | **not run**: PowerShell is not installed here. Quoted instead: GitHub Actions run 43607515046 on this commit, job "PowerShell twin (Windows PowerShell 5.1)", concluded success; the two runs before it on the branch concluded failure |

**Conventions.** "spec" is `drafts/jascon-specification-2.0.0-rc.4.md`.
`<scratch>` is the session's scratch directory, where the reviewers' scripts,
built bundles and logs lie; it does not outlive the session, so every
demonstrated finding in section 6 is written as a recipe that can be rebuilt
from this text. Outside facts were checked online on 2026-11-14 where a host
was reachable and are marked where they were not.

---

## 1. The four answers

### 1.1 Has the project reached its own goals? — In part.

What it set out to prove at 1.0.0 it largely proved, and the proof re-runs: a
small typed kernel carries ten real security catalogues, the executable claims
hold, and the conversions reproduce byte for byte. Three goals are not reached
as worded, one cannot be decided, and for the 2.0.0 candidate the project set
aside the rule it had made its hallmark.

Findings that carry the answer:

- **A-1** (positive): 705 of 705 checks, every shipped bundle, and four
  conversions from pinned sources re-run true, three times over.
- **A-4**: "'valid' implies 'checkable meaning'" fails on the shipped content.
  A comma-packed `tags` string in the shipped BSI bundle validates, against the
  handbook's own example of what is "now unwritable". The notation can refuse
  it; the converters' schemas do not.
- **A-3**: the "bidirectional OSCAL export" is a lossless wrapper for two of
  eleven types, with 61 to 66 % of its bytes in JASCON's own props, and no CI
  step runs it.
- **A-6, B-2, I-3**: Risk, Check, advice packs and two fields entered the
  kernel after the promotion rule was amended to admit them, or against it.
  All of it is on the record.
- **E-2, A-9**: "implementable by a competent developer in days" is unproven.
  The only measurement is the author's own at a quarter of today's size; the
  cold implementer could not derive 11 of 173 expected results from the text.

The answer would become **yes** if: the tagline were worded as an aim or backed
by a non-security standard and a third language; the converters shipped closed
facet schemas; the export put guidance and objectives into OSCAL's native parts
and ran in CI; a stranger built a validator from the documents; and the
front-door texts said that the kernel rule changed.

### 1.2 Is the result ready to be used in large enterprises? — For a pilot, yes. As a working format beside the GRC tool, for catalogue content and under conditions. As a system of record or an exchange format, no.

The reasons at the upper levels lie less in the design than in what stands
behind it and around it: nobody else uses it, one person carries it, the
released version is not anchored, the step from "consistent" to "proven" is
not enforced, and the human side of an audit has no typed place.

Findings that carry the answer:

- **G-1, H-2, D1-24** (blocks L4): with trusted keys supplied, a bundle whose
  signature was removed, whose signed summary was replaced, or whose
  un-named requirement was weakened ends green, with "FULL MATCH" or "the
  content is proven". Reproduced by up to four agents each.
- **I-4, I-6, I-8, I-1** (blocks or weighs heavily at L3 and L4): 1.0.0 has no
  tag although the documents say it has; one human, eight active days; no
  outside user; no written governance.
- **H-5, H-6, H-8, H-10** (weighs heavily at L3 and L4): scope, period,
  sample, result per control, graded finding, root cause, separation of
  duties and history are free text, a private facet, or absent.
- **F-13, F-6** (blocks L2 for lifecycle data, L3): no exchange of systems,
  implementations, assessments or findings with existing tools; no access
  control, tenancy or party record.
- **H-1, H-7, H-9, F-1, G-14** (in favour): a machine check is re-performable
  by a second party; the risk register and the Statement of Applicability
  work as data; 170,000 objects validate in minutes; hostile content executed
  nothing in the browser apps.

The matrix in section 3 gives the answer cell by cell and the shortest list of
what is missing for each next level.

### 1.3 Is the standard overdesigned? — The released 1.0.0 core is not. The 2.0.0 candidate is, in a part that is recent and separable.

Findings that carry the answer:

- **B-8, B-9** (against overdesign): 45 field paths carry 4,198 real objects;
  like for like the schema has 59 definitions against OSCAL's 140 and about
  half the size per use case.
- **B-1, B-2**: Risk, Check, scales and advice packs are 44 of 58 named rules
  and 370 of 705 vectors, tripled the validators, are unmeasured on real
  content, and must be implemented by anyone who claims conformance. An
  optional module, neither kernel nor facet, would meet every goal on the
  yardstick and was never weighed.
- **B-3, B-4, B-5**: `conditional-apply`, six of eight tailoring operations,
  `canonical-alias` and the XML projection are specified and used by nothing;
  the last has no artefact at all.
- **B-10, H-16** (the other direction): what a large organisation asks for
  first — parties, organisation and scope, an exception as a record, the human
  audit — is thinner than what was added.

The answer would become **no** for the candidate if Risk, Check and advice
packs were optional parts with their own conformance class, or if real
converted corpora and a second implementer showed that they are used and can
be built. It would become **yes** for the core only if a census of real
lifecycle content showed large parts of the nine 1.0.0 types unused; the
shipped corpus cannot show that either way, because it is a catalogue corpus.

### 1.4 Is it too complicated? — The model is not, measured against what the domain forces and against OSCAL. Learning it from today's documents and writing it by hand are harder than they need to be, and the trust vocabulary promises more than a reader of the output can safely take from it.

Findings that carry the answer:

- **D1-1, D2-20, C-19, E-1** (against): two cold consumers agreed on 8 of 10
  questions down to ids and digests and reproduced every digest at the first
  attempt; the cold author's lifecycle objects validated first time; the cold
  implementer reached 154 of 173 on the first run.
- **E-2, E-7, E-8, C-1, C-3** (for, and repairable): eleven non-derivable
  vectors, eight contradictions between specification, schema and appendices,
  five chapter examples that do not validate, a documented exception form the
  validator refuses.
- **C-17, C-4**: hand authoring needs a digest program and a rebuild on every
  edit, and a nested mistake is reported against the wrong type.
- **G-6, C-6, D1-3**: the tier rule decides who owes an exception; both
  consumers were unsure of it, and the author met its consequence only by
  accident.
- **E-15, E-14**: for the whole of 2.0.0 the honest estimate is weeks, with a
  hand-written pattern matcher and a signature algorithm among the parts.

The experiments show gaps and ambiguities; they do not measure a person's
effort (section 5.1). The answer would become **yes** if human readers, given
the repaired documents and an editor that hides digests and manifest, still
needed materially longer than with OSCAL or a GRC export for the same ten
questions. It would become a clearer **no** if the documents were repaired and
a second team built a validator from them.
## 2. Question 1 — goals and claims, one by one

The yardstick was collected in step 1 from the README, handbook chapter 1, the
specification header and Part IV. Results are lens A's, with the corrections the
checkers made (marked *corr.*). "spec" is
`drafts/jascon-specification-2.0.0-rc.4.md`. Finding ids refer to section 6.

### 2.1 Goals

| Goal | Wording and place | Result | Evidence |
|---|---|---|---|
| G1 tagline | "one notation for every standard, in every language" (README.md:8; spec:74-76) | **Not reached as worded** | Eleven corpora, ten of them security catalogues, nine from OSCAL sources, plus one example system; language tags `en` and `de` only; ISO management-system clauses and PCI's customized approach are declared "named extension targets, not covered claims" (spec:940-945). A-7 |
| G2.1 simpler | north star (spec:141-145) | **Partly** | Against OSCAL: yes on schema size (59 definitions against 140, B-9 *corr.*). Against itself: kernel 9 → 11 types, validators 994 → 3,144 and 1,163 → 4,301 counted lines since 1.0.0. A-9, B-1 |
| G2.2 closer to (measured) customer needs | spec:141-145; ch01:279-282 adds "measured" | **Partly** | The 1.0.0 kernel is census-derived. Risk, Check, advice packs and two fields entered on the author's decision, with no census support by the spec's own words (spec:104-116). A-6, B-2 |
| G2.3 no more props | spec:141-145 | **Partly** | Typed kernel fields carry 55 % of the converted values by count and 35 % by bytes; facets carry 44 % and 64 % (*corr.* by checker 2; lens A's 71 % counted facet keys). 2,202 raw OSCAL props survive in the ISM bundle's compat facet (declared). A-4 |
| G2.4 less bespoke JSON / meta-language extensions | spec:141-145 | **Partly** | One kernel schema, no meta-language. But 27 of 30 bundle-pinned facet schemas are converter "stubs", and an enterprise has to write its own facets for parties, organisation, findings detail and audit work (B-10, H-5, H-6). |
| G3a global identity, no collisions | ch01:260-262 | **Partly** | No collision in 4,214 objects. All ids are minted by this project's converters inside the authorities' namespaces (`ns.nist.gov`, `ns.bsi.bund.de`, …), which the authorities have not published. A-8 |
| G3b cheap membership and variants | ch01:262-264 | **Reached** in converted data | ISM baselines and Essential Eight levels are Sets (581 Sets in the bundle); the four SP 800-53B baselines are four Sets. A-13 |
| G3c binding strength, clauses, typed parameters, deadlines, aliases, history in the core | ch01:264-268 | **Partly** | The fields exist. In the shipped bundles modality is `unspecified` on 1,149 of 1,150 ISM and 106 of 106 CSF statements; typed deadlines occur in no shipped catalogue (the evidence is FedRAMP CR26, not in the tree). A-5, B-11 |
| G3d "'valid' implies 'checkable meaning'"; a packed list "unrepresentable" | ch01:268-271 | **Not reached for the converted content; reachable by the notation** | In the shipped BSI bundle the `tags` array replaced by the string "Lateral Movement, Separation of Concerns, Zero Trust" validates ALL GREEN, against ch07:165-168 ("now unwritable"). A strict facet schema refuses the same input: the stubs are the converters' choice. A-4 |
| G3e NIST's document conventions leave the core | ch01:271-273 | **Reached** | No OSCAL document construct among the schema's definitions; leftovers sit in the facet `compat/oscal-1x@1`. |
| G3f implementable by a competent developer in days | ch01:273-277; README.md:19 calls the weekend validator "measured" | **Not decidable; the evidence points to weeks for the whole** | The measurement was the author's own, at 157 vectors. Experiment E: a 173-vector subset in one sitting, 11 results not derivable from the text; estimate for the remaining 532 vectors three to four times the code. E-1, E-2, E-15, A-9 |
| G4 kernel "normative, fixed" | README.md:360 | **Reached at 1.0.0, given up for the candidate** | D22 amended on 2026-11-12 to admit Risk and Check; `statement-ids` and `product-version` entered "against the rule" (spec:1141-1158). A-6, I-3 |
| G4 facets registered, pinned, machine-checked, fail-closed | README.md:361 | **Partly** | Unknown fields, unknown kernel versions and unregistered facets are refused (G-15). The registry is the sender's own manifest, and most pinned schemas check the first key level only (A-4). |
| G4 failures "unrepresentable rather than forbidden" | README.md:364-365 | **Partly** | Holds for `{param:}` tokens and identity-addressed operations. Does not hold for the Deviation duty: any string in `deviation-ref`, or a withdrawn Deviation, satisfies it (C-2, check 1 N3). |
| G4 two digests, "signatures survive repackaging" | README.md:366-368 | **Reached as mechanism; overstated as proof** | Both digests recompute on every shipped object; two independent cold readers reproduced them from the handbook. But a verified Attestation says nothing about objects it does not name, an unsigned one reads FULL MATCH, and the rendering digest is checked by no tool (D1-23, D1-24, H-2, G-1). |
| G4 "carry it or stop with a reason, never guess" | README.md:368-369 | **Partly** | Converters exit 1 on an unaccounted value. They do write defaults (a party on 2,255 of 4,173 statements, three officials in the IFA bundle), named as defaults in the reports beside the bundles, not in the bundles. A-5, D2-7 |
| G5 house rule: claims survive contact with real catalogues; concepts enter through the corpus | README.md:10-13; ch01 §1.6 | **Reached at 1.0.0; not for the 2.0.0 additions; broken in ch15** | Risk rests on two objects from one example POA&M, Check on no runner and no converted corpus, advice packs on one fictional pack (all declared). Handbook ch15 describes a Foundation and a NIST arrangement in the present tense without an evidence label (I-2). |
| G6 "engine that compiles to 1.x"; migration "information-preserving for the supported corpus" | spec D19, D16 | **Partly** | The export is schema-valid OSCAL with real groups, statements, parameters and links. Guidance, SP 800-53A objectives and Sets ride JASCON-namespaced props (61–66 % of the compact bytes). It covers Requirement and RequirementSet only and is not run in CI. A-3 |
| G6 declared non-goals (D17) | spec:940-945 | **Kept as declared** | Wording unchanged since v0.5. |
| G7 complexity ledger: "narrower and more boring"; no expression language; one file each | spec IV.1 | **Partly** | One file each and no general expression language hold. The margin against compliance-trestle fell from ≈30× to ≈9.8× (Python) and ≈7.2× (PowerShell) by the spec's own counter. A-10 |

### 2.2 Checkable claims

| Claim | Wording and place | Result | Evidence |
|---|---|---|---|
| C1 vectors | "157-vector conformance corpus (705 in 18 families in the 2.0.0 candidate)" (README.md:16) | 705 in 18 families: **reached** (re-run). 157: not decidable, no 1.0.0 tree | `python3 jascon/scripts/validate_core.py` → 18 families, sum 705, 0 fail, ALL GREEN (orchestrator, 2026-11-14). The spec header still says 537 in seventeen at rc.3. |
| C2 two validators green; twin on Windows PowerShell 5.1 | README.md:17-20; spec:3 | Python: **reached** (re-run). Twin: **quoted, not re-run** | GitHub Actions run 43607515046 on commit 430cf15, job "PowerShell twin (Windows PowerShell 5.1)": success. PowerShell is not installed in the review container. |
| C3 coverage | "eleven … corpora converted at 100 % declared path coverage (251,591 source leaf values …)" (README.md:21-25) | **Reached as defined; the headline and the footnote are stale** | The eleven reports now sum to 251,829. Value level, six ledgers, 214,365 values: 58.0 % carried, 41.1 % "not-content", 0.9 % dropped, 0 unaccounted (recomputed twice). The 41 % is OSCAL's own encoding overhead (namespaces, prop names, part names), not lost content (checker 2, sample of 30 plus a full breakdown). A-2 |
| C4 round trip | "round-trips 5,886/5,886 objects to semantic-digest equality"; "10/10 catalog bundles schema-valid" | **Partly; not reproducible as stated** | The tree reproduces 4,198/4,198 on four bundles. The round trip is JASCON → OSCAL → JASCON. A-3 |
| C5 6,914 objects in eleven bundles | README.md:397-402 | **Not decidable** | Five bundles ship; they hold 4,214 objects. |
| C6 "Zero kernel-schema changes forced" at gate 3 | README.md:410-413 | **Not decidable; weakened by the project's own later record** | spec:2035-2037: thirteen POA&M risk values "had never arrived at 1.0.0". A-6 |
| C7 weekend validator "~30× smaller than compliance-trestle" | README.md:426-430 | **Stale** | 3,144 and 4,301 counted lines → ≈9.8× and ≈7.2× against the quoted 30,905 (trestle's count not re-measured). The spec says "the ≈30× of 1.0.0 is history" (spec:2005-2016); the README does not. A-11 |
| C8 size deltas "ISM −29 %, GS++ −50 %, CR26 +55 %" | README.md:407-409 | **Stale; ISM wrong in sign** | Against the pinned sources: ISM +0.8 % (objects only) to +25.7 % (whole bundle); GS++ −43.4 % to −34.7 %. CR26 not in the tree. A-11 |
| C9 the 1.0.0 corpus validates unchanged under 2.0.0 | spec:89-95 | **False as written for rc.4** | Re-measured from commit 0b949fa3 by lens F and checker 6: 6,279 of 6,914 objects match a type under the rc.4 schema; the 635 that do not are the CIS Ubuntu Mappings, whose `provenance.date` holds a version string. True at rc.1 and for the five bundles that ship. I-5, F-11 |
| C10 "The spec-feedback backlog is empty" | README.md:440-441 | **Stale** (true of 1.0.0) | Open today: #41, #55, #62, #71, #72, #79. |
| C11 second implementation | spec:106-109; README.md:449-450 | **Reached as declared**: independent in language and runtime only | One author and the same AI assistant wrote all three ports; no third-party build exists. A-9, I-6 |
| C12 shipped conversions reproducible | README.md:110-116 | **Reached** for the four catalogue bundles | Re-run from pinned sources twice (lens A, checker 2): `diff -rq` empty. IFA and CR26 not re-run here (CI does). A-1 |
| C13 "the kernel is what all three were measured to need" | README.md:387-389 | **Partly** | Holds for nine types. Risk: "0 of the 3 census corpora" (register:1619-1626). A-6 |
| C14 "Nine kernel objects"; "22 decisions" | README.md:354-362, 376 | **Stale** | Eleven types; D1–D26. |
| (added) "Released: `v1.0.0`"; "✓ tagged 2026-07-22" | README.md:443; spec:2470, 2315; register:1328 | **Not reached** | No tag and no release on the public repository; the "unchanged" 1.0.0 text was edited after release (16 insertions, 11 deletions; it now names identifiers that did not exist at 1.0.0). I-4 |

### 2.3 Did the goals move?

| Topic | v0.5 (2026-07-18) | 1.0.0 (2026-07-22) | 2.0.0-rc.4 (2026-11-13/14) |
|---|---|---|---|
| Aim | "OSCAL Semantic Core (working name)", "a well-supported architecture hypothesis" | JASCON; the tagline arrives with the rename | Same tagline |
| North star | Four tests | Identical | Identical in the spec; README and ch01 wordings drift |
| Kernel | 9 types, 8 primitives, 3 predicates | Same | 11 types, 10 primitives, 3 predicates, 12 comparators, an I-Regexp engine, scale pins, pack manifests, `provenance` |
| Promotion rule D22 | 2-of-3 census | "Post-1.0 … requires measured 2-of-3 and a major" | Risk first a recorded exception (11-10); a consumer-side clause added (11-12) admits Risk and Check; two fields enter against the rule |
| Scope | What catalogue authorities publish, plus lifecycle types | Same | Adds the consumer's risk register, machine checks, vendor advice packs, authorship and review dates |
| Non-goals D17 | Flows, template accreditation, PCI customized approach, ISO clauses | Unchanged | Unchanged |
| Compatibility | — | — | "every 1.0.0 bundle is a 2.0.0 bundle" ended at rc.3 |

The north star did not move. What moved is the scope (from "what authorities
publish" to "what an organisation records about itself") and the rule that
guarded the kernel. Both moves are on the record in the specification and the
register. The README's bet and handbook chapter 1 still lead with the rule as
it stood at 1.0.0.
## 3. Question 2 — ready for large enterprises?

The reference enterprise of lens F: tens of thousands of employees, dozens of
legal entities, some thousands of systems, a dozen frameworks, an established
GRC tool, a CMDB, ticketing, internal audit. Each cell names the findings that
decide it (section 6).

### 3.1 The matrix

| | L1 — a pilot in one team | L2 — a working format beside the GRC tool | L3 — the system of record | L4 — exchanged with auditors, regulators, suppliers |
|---|---|---|---|---|
| **The specification** | **Ready.** The core model fits the work and is small (B-8, B-9); risk register, Statement of Applicability and machine checks work as data (H-1, H-7, H-9). | **Ready under conditions:** pin a commit, because "rc.4" names more than one rule set (I-3, F-12); keep to catalogue, tailoring, risk and check content; write house facets for findings and manual assessments from the first day (H-5, H-6); know that a single-origin organisation gets no exception duty from the tools (G-6, C-6). | **Not ready.** No tenancy, access, ownership or party record (F-6); no link from baseline to system (D1-2); an exception has no identity and no end (D1-13); no history (H-10, F-9); separation of duties not expressible (H-8); released shapes changed within four months (I-5, F-11). | **Not ready.** No key lifecycle (G-5); an Attestation proves only what it names while the text says "proven" (D1-24); the rendering is unbound (H-2); nothing links an authorization to what it rested on (D1-25); not a qualified signature (H-4); no anchored release, no body, no counterparty (I-4, I-11, I-8). |
| **The reference tooling** | **Ready.** Strict, fast enough, offline (F-1, F-17, I-7); the app is a workbench for one person (F-15); hostile content executed nothing (G-14). Expect misleading messages on nested mistakes (C-4). | **Ready under conditions:** make one implementation the judge, because the port and the reference disagree on some digests and on pack import (G-7, G-12); read a green run as "consistent", not "approved" or "proven" (C-2, G-1); build the bridges yourself, since there is no library, no machine-readable result and no lifecycle exchange (F-3, F-14, F-13). For lifecycle data moving to and from the GRC tool: **not ready** (F-13). | **Not ready.** An executable specification, not deployable software (F-14); crashes and two verdicts on malformed input, paths that leave the folder, patterns that stall (G-8, G-9, G-10) make it unfit as a service on third-party input; one manifest for all editors (F-9). An enterprise would replace it; the vectors make that feasible, with the gaps of E-2. | **Not ready.** Green without a valid signature when keys are supplied (G-1); rendering never checked (H-2); a damaged Attestation skipped silently (H-3); no switch to refuse a claimed authority (G-6). |
| **The converted content** | **Ready** for the four shipped catalogue bundles: reproducible from pinned sources, licences stated (A-1, I-10). | **Ready under conditions:** the ids are this project's, in the authorities' namespaces (A-8); modality is empty for ISM and CSF and the obligated party is a default (A-5); facet content is checked at the first key level only (A-4); six further corpora have to be converted by the adopter, licences permitting (I-10); DE.BSI is ShareAlike. | **Not ready**, and mostly not applicable: the content is catalogues. The one lifecycle corpus has 16 objects, an unsigned Attestation and three converter-written officials (D2-7, H-12). An enterprise's own lifecycle data would be the content at this level, and nothing converts it (F-13). | **Not ready.** No authority has published these ids or bundles; the OSCAL export, the way back to what counterparties read, covers catalogues only and carries most content in JASCON props (A-3). |

### 3.2 What is missing for the next level, shortest list

**From L1 to L2 as shipped, without conditions**

1. A tagged 2.0.0, and no rule change inside a candidate without a new number.
2. The exception duty made real: `deviation-ref` resolved or removed, only an
   approved Deviation counts, the handbook's form and the validator's agree.
3. A machine-readable result and exit codes that separate the caller's bundle
   from the tool's self-test; file-naming error messages; no tracebacks.
4. One canonical form in all ports, with vectors for integer-like names and
   `__proto__`; duplicate member names refused.
5. An import and an export for systems, implementations, assessments and
   findings (OSCAL SSP, assessment results, POA&M, or plain CSV), not tied to
   one example.
6. Published stdlib facets for what every adopter will otherwise invent:
   finding detail and manual assessment (scope, period, sample, result per
   control).
7. The handbook repaired where the cold readers failed (section 5.5).

**From L2 to L3**

8. A party record, an organisation and scope, a link from baseline to system,
   an exception with an identity and an end.
9. A defined way of working for many editors and a history: either in the
   notation or as a documented contract with the repository around it.
10. A stated compatibility promise between versions, and a migration tool when
    it is broken.
11. A statement of what the format leaves to the surrounding system: access,
    tenancy, confidentiality, retention, separation of duties.

**From L3 to L4**

12. An option that fails a run unless a verified Attestation covers the bundle,
    with a completeness rule for what it must name; the rendering digest
    checked; a claimed authority refusable.
13. A signature profile that answers the seven questions of chapter 11 (key
    identity, trust roots, time, expiry, revocation), and a position on
    qualified signatures.
14. An anchored release (tag, archive), written governance, a security
    contact, a second maintainer.
15. One implementation by somebody else, one counterparty who reads the
    format, and a path into a body — or the measured findings carried into
    OSCAL or Gemara, where the readers already are.

### 3.3 The alternatives open to the same enterprise (lens I)

| | L1 | L2 | L3 | L4 |
|---|---|---|---|---|
| **Adopt JASCON** | Reasonable: cheap, offline, useful defect findings. | Possible for a team that accepts being the only user and keeps OSCAL as the exit for catalogues. | Not ready. | Not available: no counterparty reads it. |
| **Stay with OSCAL 1.x** (1.2.3 current, checked online) | Same pilot with heavier tooling; national content in props. | Vendors import and export it; BSI, ACSC, NIST and CSA publish in it. Meaning sits in untyped props; no signing, no language map. | The one open format a GRC vendor will contract on. | Named in FedRAMP's rules in force; yet FedRAMP's RFC-0024 records that of 100+ Rev5 authorizations in 2025 none used it (quote verified). |
| **The GRC tool's own model** | Nothing to do, nothing learned. | Supported, with workflow and audit log; content locked in. | This is what a system of record is today. | PDF and spreadsheet exports. Only ServiceNow's OSCAL support was verified, through search results. |
| **Wait** | Learns nothing. | Avoids rework while the formats move. | Rational today. | Rational today: the counterparty picks the format. |

At L1 JASCON is as good a choice as any. At L2 it wins on semantics and loses
on tool support. At L3 and L4 the alternatives are not better formats; they
are formats with somebody behind them, and at those levels that is the
criterion.

### 3.4 Recommendations

*These are recommendations, not findings. They follow from the findings named
and are the orchestrator's selection.*

1. **Close the gap between "consistent" and "proven" before anything else**
   (G-1, H-2, H-3, D1-24, C-2). It is the one place where the tools say more
   than they checked, and five reviewers found it independently. Print one
   verdict word for digests and another for signatures; add
   `--require-verified`; check the rendering digest or drop the field; fail on
   an Attestation-like file that does not parse.
2. **Tag 1.0.0 at 0b949fa3 and restore its text** (I-4). An afternoon.
3. **Decide where Risk, Check and advice packs live** (B-2). Weighing an
   optional module with its own conformance class is the alternative the
   record lacks. If they stay in the kernel, say in the README that the
   promotion rule changed.
4. **Repair the documents from the experiments' lists** (E-2, E-8, C-1, C-3,
   D1-21): the eleven vectors, the eight contradictions, the five examples,
   the Deviation form, a written signature profile, a vector format
   description. The cold readers can be run again afterwards as a regression
   test of the documentation.
5. **Refresh the front door** (A-11, I-2, I-11): the stale numbers, chapter
   15's Foundation, the FedRAMP clause.
6. **Close the converters' facet schemas** (A-4), so that the handbook's own
   example holds on the shipped bundle.
7. **Put the scarce design budget where the enterprise and the auditor ask
   first** (B-10, H-5, H-6, D1-2): party, scope, baseline-to-system, an
   exception with identity and end, and two published facets for findings and
   manual assessments.

### 3.5 Scale, measured (lens F)

Synthetic bundles generated by `<scratch>/F/gen.py`; every run ended
`ALL GREEN`, exit 0. Wall time and peak memory by `os.wait4`. The fixed cost of
a run (vectors and the example folder) is 2.1 s. Checker 6 re-timed the rows
marked * and got 46.3 s, 43.6 s and 107.2 s with the same peak memory.

| Bundle | Objects | Shape | Python reference: wall, peak | JavaScript port: total |
|---|---:|---|---|---|
| AU.ISM as shipped | 1,731 | largest shipped bundle | 6.1 s, 48 MiB | 0.9 s |
| catalogue ×10 * | 17,310 | ISM copies under rewritten namespaces | 44.7 s, 154 MiB | 6.7 s |
| catalogue ×100 | 173,100 | same | 419.1 s, 1,222 MiB | 63.0 s |
| enterprise, 1,000 systems * | 22,771 | each system: 15 Implementations, 1 Assessment, 3 Findings, 1 Risk; 40 Tailorings | 38.6 s, 130 MiB | 18.2 s |
| enterprise, 8,000 systems | 169,771 | same | 264.1 s, 675 MiB | 679.3 s |
| one Tailoring per system, 2,000 * | 45,731 | | 99.3 s, 298 MiB | 67.9 s |
| one Tailoring per system, 8,000 | 177,731 | | 654.3 s, 1,052 MiB | not run |

The reference is roughly linear at 1.5 to 2.5 ms per object and keeps the whole
bundle in memory; there is no incremental mode. With one Tailoring per system
the output grows to 8.3 million lines, most of them `uncovered:` lines. The
port is faster on catalogues and slower on the enterprise shape (F-2). The
PowerShell twin was not run; its standard run takes 81 s on the CI machine
against 16.7 s for the Python reference here, on different hardware.
## 4. Question 3 — is the standard overdesigned?

Lens B built the inventory from the schema, the specification and the shipped
data, then designed the smallest JASCON that still meets the yardstick. Checker 2
re-measured the numbers with its own scripts. Scripts:
`<scratch>/B/usage.py`, `slots.py`, `v1check.py`, `mkmin.py`, `closure.py`;
checker: `<scratch>/check/c2/f5.py`, `f8.py`.

### 4.1 What the measurements say

| Measurement | Result | Kind |
|---|---|---|
| Objects in the five shipped bundles | 4,214, of which 4,200 are Requirements (3,273) and Sets (927). The other 14 (6 Components, 3 Implementations, 1 Assessment, 2 Findings, 2 Risks) are all in the IFA example. No converted Tailoring, Mapping or Check ships. | measured twice |
| Schema field paths (532 over eleven types) | 45 filled by the four catalogue bundles, 88 more only by the 16-object IFA bundle, 134 only by the hand-written example folder, 265 by nothing that ships | measured (B) |
| Shipped objects typed by the released 1.0.0 schema | 4,206 of 4,214; the 8 failures are in IFA (2 Risks, 2 Findings with `risk-refs`, 1 Implementation with `provenance`, 3 Components with a dated authorization or `statement-ids`) | measured twice |
| Growth from 1.0.0 to rc.4 | specification 7,563 → 26,396 words; schema 37 → 59 definitions, 179 → 327 property slots; reference validator 994 → 3,144 counted lines; twin 1,163 → 4,301; vectors 157 → 705; named rules 0 → 58 | measured |
| Share of the growth that is Risk, Check, scales and advice packs | 2 of 11 types, 2 of 10 primitives, 44 of 58 named rules, 370 of 705 vectors | measured (B) |
| Schema size against OSCAL 1.2.3 (complete JSON schema), same walker | 59 definitions against 140; 327 property slots against 970; 47,887 bytes against 267,764. OSCAL's Metaschema holds about 348 further constraints; JASCON has 58 named rules outside its schema | measured twice (*corr.*: lens B's "45" left out 14 root definitions) |
| Per use case (definitions / slots) | catalogue with baselines 19/98 against OSCAL catalog 39/193; plus tailoring 22/145 against OSCAL profile 47/248; system and implementation 18/98 against OSCAL SSP 65/329 | measured (B) |

Two readings of these numbers have to be kept apart, and the checker insisted on
it. The 1.0.0 schema typing 4,206 of 4,214 objects does **not** show that the
2.0.0 additions are unneeded. It shows that the shipped converted corpus is a
catalogue corpus: Assessment has one converted instance, Tailoring and Mapping
none, and they are 1.0.0 types. What the number does show is that the 2.0.0
additions are unmeasured on real content, which the specification concedes
(spec:104-116; D24 "Cons, stated"; Appendix F Q26: "This answer is a bet, and it
is labelled as one").

### 4.2 The inventory

"Shipped" means the five bundles, the example folder and the example pack.
Counts for FedRAMP CR26 are quoted from its coverage report; its bundle is not
in the tree.

**Carried by real converted content.** Keep.

| Mechanism | What demanded it | Used today |
|---|---|---|
| Requirement with `statements[]` (id, modality, prose) | census of three authorities | 3,273 Requirements; more than one statement per Requirement only in SP 800-53 (284 of 1,016) |
| RequirementSet, `members[{ref, sequence}]` | the ISM's 5,301-entry matrix | 927 Sets |
| Identity (`id`, `version`, `label`, `lifecycle`) | D2 | every object |
| `aliases[]` | BSI secondary ids | 1,158 objects, all DE.BSI |
| `replaces[]` | withdrawn controls | 221 objects |
| `relations[]` | BSI dependency links | 1,218 objects |
| Seven modality codes | BSI verbs, CR26 keywords | must 1,165 · should 626 · may 225 · unspecified 1,257 Requirements; `must-not`, `should-not` only in CR26 (quoted); `may-only` nowhere |
| Parameters (`name`, `type`, `label`, `choices`, `default`) | SP 800-53 ODPs, BSI | 890 Requirements; types `string` 865 and `choice` 121; 11 of 13 parameter types in no shipped converted object |
| Language-tagged text | the "EU-27 languages" decision | every text field; no converted object carries two languages |
| Facets: registered, pinned, capability-declared, fail-closed | the answer to props | 3,222 of 3,273 Requirements; 27 facet ids |
| Annotations | layer 3 | 221 objects |
| Content manifest, package digest, sealed mode | D3 | every bundle, every tool |
| Semantic digest and the canonical-form law | "signatures survive repackaging" | computed everywhere; consumed by three Attestations and the OSCAL round trip |
| OSCAL export, compat facet | D19 | 1,856 objects carry the compat facet |
| DATE-1..5, KERNEL-1/2, MANIFEST-1, NUMBER-1 | defects found in the 2.0.0 cycle | all tools |

**Carried by CR26 (quoted) or by the 16-object IFA bundle.** Keep, except Risk.

| Mechanism | What demanded it | Used today |
|---|---|---|
| Tailoring: select by set, `set-modality`, `set-parameter`; the monotonicity law | OSCAL profiles, CR26 classes | no shipped converted Tailoring; 2 in the examples; CR26: 5 Tailorings, 107 `set-modality`, 16 parameter operations |
| Mapping | crosswalks | none shipped converted; 1 example; CR26 652, CIS Benchmark 635 |
| Typed durations (elapsed, calendar) | CR26 deadlines | none in the shipped catalogues |
| Component, Implementation, Assessment, Finding, actions, Deviation | OSCAL SSP, AR, POA&M | IFA 6 + 3 + 1 + 2, one Deviation; examples 4 + 2 + 3 + 2 |
| Attestation, DSSE profile | D7 | IFA 1 (unsigned); examples 2 |
| `provenance`, `decided`, `review-due`, AUTHOR-1..4, REVIEW-1 | author decision 2026-11-13 after a comparison with five formats | IFA 1 object; 10 example objects |
| Risk core (scenario, owner, state, treatment) | author decision under the amended D22 | IFA 2; examples 1 |

**Carried only by the example folder and the vectors, or by nothing.**

| Mechanism | What demanded it | Used today | Lens B's call |
|---|---|---|---|
| Check, `check-verdict`, 12 comparators, an own I-Regexp engine, evidence store, `collector@1`, CHECK-1..15 | author decision; "Census authorities encoding a machine-decidable check: 0 of 3" (CP-CHECK-1 §2.1) | 2 example Checks, 2 runs; 205 vectors; no runner | move to an optional module |
| Risk rating, residual rating, acceptance, `risk-coverage`, scales, matrix, SCALE-1..4 | same; spec:1390-1393 "Vector-exercised only" | 1 example Risk, 3 scales; 91 vectors | move with Risk |
| Advice packs: header, ADVICE-1..11, `statement-ids`, `product-version` | author decision; "One fictional example file is not a corpus" (CP-ADVICE-1 §2.3) | 1 example pack; 74 vectors | move to a profile |
| `conditional-apply` | 1.0.0 design | no bundle can carry an instance (`jascon-app/jascon-rules.js:37-38`); 8 vectors | remove until a carrier exists |
| The three predicates | 1.0.0 design | carrier exists (`Tailoring.selects[].predicate`), 0 uses in anything shipped (*corr.* by checker 2: lens B said "no carrier") | postpone |
| Tailoring operations `set-field`, `replace-prose`, `add-relation`, `remove-relation`, `attach-facet`, `detach-facet` | OSCAL `alter` | 0 shipped, 0 in CR26 | postpone |
| Tier derivation (authority-claimed, authority-proven, consumer) | D13 | 10 vectors; decides who owes a Deviation | see below |
| `canonical-alias` | D2 | 0 shipped; 2 vectors | postpone |
| XML transit projection (D18, "guaranteed strict XSD") | data diodes | no XSD and no tool in the tree; the kernel schema uses `anyOf`, `not`, `if/then`, which ch11:333-337 says have no faithful XSD image | postpone |
| Attestation `rendering`, manifest `renderings` | D7 | read by no validator | postpone, or check it |
| Authority-tier publication duties (`.well-known`) | D15 | no tool | postpone |
| `obligated-parties` required | CR26 | one converter-written constant on every statement of AU.ISM, DE.BSI, US.CSF | make optional |
| Parameter types decimal, boolean, date, datetime, uri, code, list, range | D9 | 0 shipped converted | postpone |

On tier derivation the reviewers disagree with lens B's "postpone". It is not
dead weight: it is the rule that decides whether a weakening needs a recorded
exception, and lenses C, D and G each ran into it (C-6, D1-3, G-6). The
problem with it is the opposite of overdesign: its consequence is large and its
proof is weak. It stays in section 6 as a finding about trust, not as a removal
candidate.

### 4.3 The smallest JASCON

Lens B's design, which is close to the released 1.0.0 kernel plus the small
repairs of the 2.0.0 cycle:

- **Kernel:** nine types (Requirement, RequirementSet, Tailoring, Mapping,
  Component, Implementation, Assessment, Finding, Attestation) and Deviation;
  statements with seven modality codes; parameter types string, choice,
  integer, elapsed duration, calendar period; identity, aliases, `replaces`,
  relations, lifecycle; language-tagged text; facets and annotations; manifest,
  both digests, sealed mode, the DSSE profile; Tailoring with select, exclude,
  `set-parameter`, `set-modality` and one law (an easing needs a Deviation);
  seven primitives; `provenance`, `decided`, `review-due`; fourteen named rules.
- **Optional modules**, each with its own version, vectors and conformance
  class: a Risk module (Risk, scales, `risk-coverage`), a Check module (Check,
  `check-verdict`, the comparators, the pattern engine, the evidence store), an
  advice-pack profile.
- **Postponed** until a corpus or a tool needs them: the rows marked so above.

| | Specified (rc.4) | Smallest | Basis |
|---|---:|---:|---|
| Kernel types | 11 | 9 | — |
| Primitives | 10 | 7 | — |
| Comparators | 12 | 0 | — |
| Tailoring operations | 8 | 2 | — |
| Named rules in the kernel | 58 | 14 | counted |
| Schema | 59 definitions, 327 slots, 47,887 bytes | 40 definitions, 168 slots, 27,358 bytes | demonstrated: `<scratch>/B/jascon-min.schema.json` types 4,210 of 4,214 shipped objects; an upper bound, it still holds all 13 parameter types |
| Specification text | 26,396 words | about the 1.0.0 text (7,563 words) plus D26 | estimate |
| Reference validator | 3,144 counted lines | about 1,000 plus the author, date and number rules | estimate |
| Vectors | 705 | roughly 270 | estimate |

**Who would miss what.** The Risk module: users of ISO/IEC 27001 and BSI 200-3
and the app's risk page; lens H found Risk to be the one lifecycle type that
holds what its regime prescribes (H-7), and the Tailoring-plus-risk-coverage
pair to work as a Statement of Applicability (H-9). The Check module: anyone
automating configuration checks inside JASCON, the app's checks page and the
reader; lenses D and H found the recomputable check run to be the strongest
evidence the notation carries (D1-18, H-1). The advice profile: the pack
builder and a vendor who publishes recommendations; none has. So the candidates
for removal from the kernel are not worthless. The argument is about where they
live and who must implement them.

**What the author already answered.** D22 rev 4, D23, CP-CHECK-1 §8 and
Appendix F Q7, Q24–Q26 argue that a verdict is a computation, facets "never
define new computation", therefore Risk and Check must be kernel. Checker 2
searched the register, the four change proposals and Appendix F for a third
option — an optional, separately versioned part that is neither kernel nor
facet — and found none weighed. The answer therefore holds as a ruling inside
the kernel-or-facet choice and does not show necessity. Two existing
mechanisms soften the cost and belong in the picture: the conformance tiers
make `risk-coverage` and `check-verdict` Portable-tier computations, which a
Core tool need not perform (spec:917), and the kernel pin lets content without
2.0.0 features be read by a 1.0.0 tool (D3.6). Neither frees an implementer
from the shapes: "all eleven types" is required at every tier (spec:909).

### 4.4 The other direction: what a large organisation does not find

| Need | What JASCON has | Gap |
|---|---|---|
| Organisation, legal entities, scope of the ISMS | Component kinds, `members`, a `scope-label` string | no organisation or scope object |
| Parties, roles, ownership | bare URIs in `owner-ref`, `approver-ref`, `author-ref`, `signer` | no party record ("No party type (#16)", spec:1879), no role, no check that an approver may approve |
| Which baseline governs which system | `Assessment.tailoring-ref`, `Risk.tailoring-refs` | "A Tailoring names no Component" (spec:781-788, a decision); a system with no risk and no check run has no recorded baseline (D1-2, C-11) |
| An exception as a record | Deviation as a sub-object without an id, without an end date | one exception across ten systems is ten copies; `review-due` never fails a run (D1-13, C-5) |
| The human audit | one `result` and one instant per Assessment; a Finding with title, actions, state | no period, scope, sample, result per control; no grade, root cause, action owner, completion, verification (H-5, H-6) |
| Evidence lifecycle | digest-bound evidence for machine checks; bare URIs otherwise | no retention, expiry or revision chain; manual evidence unbound (H-10) |
| History | one version per id in a bundle; one `provenance` per version | no change log (declared, spec:1832-1834) |
| Access and partial disclosure | none | see lens F |

Lens H put the same observation from the auditor's side: the kernel is uneven.
The part an ISO, C5 or SOC 2 engagement uses least, the machine check, has a
type, a primitive and 205 vectors; the part it uses most, the human test, the
finding and the report, is the thinnest (H-16).
## 5. Question 4 — is it too complicated?

### 5.1 What the three experiments can and cannot show

Each cold reader was a language model started with nothing but its brief and a
restricted set of files. A model reads thousands of lines in minutes and already
knows JSON Schema, RFC 8785 and OSCAL. Its speed therefore says almost nothing
about the hours a person needs. What the experiments do show is where the
documents leave a careful reader without an answer, with a wrong answer, or
with two answers, because those gaps do not depend on reading speed. Every gap
below was then checked by a reader allowed to open everything (checker 4).

Two breaches of the cold condition are on record. Reader E ran one grep that
touched three appendices outside its permission and used nothing from it.
Reader D1 notes that the example folder's own README states several answers in
prose before any script ran.

### 5.2 Experiment C — the cold author

Brief: record a company with two subsidiaries, a hardening policy of eight
requirements, two baselines, an exception with an end date, inheritance from a
cloud platform, an assessment with one failed and one passed requirement, a
risk, an automated check and an attestation, using the skill file, the
handbook, the example folder and the validator as a black box. Files:
`<scratch>/C/report.md`, `log.md`, `bundle/`, `runs/`, `probes/`.

| Measure | Result |
|---|---|
| Final bundle | 36 files, 30 objects, `ALL GREEN`, also with `--require-authors` and `--trusted-keys` |
| Validator runs | 32 in all: 12 to build the bundle, of which 2 failed; 20 probes |
| First object valid | run 1 |
| Whole case valid | run 11 |
| Concepts before the first object / before the whole bundle | 6 / 25 |
| Schema opened although the brief discouraged it | three times, each time because the handbook had no answer |
| Helper program the author had to write | 33 lines, for the two digests and the manifest |

What worked first time: a Requirement with a typed parameter; Components,
inheritance, Assessment, Finding, Risk and a Check with its run record, each
from Appendix A and the example files (C-18 to C-22).

Where the documents failed the author:

- The handbook shows a Deviation in a list on the Tailoring (appendix-a:91,
  ch06:108-112). The validator accepts it only inside the operation. Checker 4
  confirmed that the documented form fails and the working form is in no
  document (C-1).
- Five chapter examples print text fields as plain strings; the validator
  requires a language map (C-3, 5 of 5 confirmed).
- An error nested inside a Tailoring, Finding, Risk or Component is reported as
  "matches NO type (closest requirement: 'statements' is a required property)":
  the wrong type and no field. Top-level errors are reported correctly
  (C-4, *corr.*).
- Signing could not be done from the handbook: the algorithm, the signing input
  and the key-file format are in the validator's source and a stdlib note
  (C-13, D1-21).

What the case needed and the notation has no place for: which company owns
which subsidiary; which system is under which baseline; that one baseline
builds on another; an end date for an exception; the result per requirement
inside one audit. The author recorded three of these through relations of its
own invention, weakened one (the end date became a review date) and split one
audit into two objects.

What the rules gave that a spreadsheet or home-made JSON would not, each seen
in a run: a recorded check outcome is recomputed from the observation; a
subsidiary's weakening without an approval record is refused; references must
close; a list of selected requirements that rest on no risk; a signature bound
to named objects. And what a green result did **not** mean, found by probing:
any text in `deviation-ref` satisfies the exception duty (C-2); under the
company's own id origin the same weakening needs no exception at all (C-6).

### 5.3 Experiment D — two cold consumers

Brief: answer ten questions an internal auditor or CISO asks, with scripts of
their own, from the converted NIST example (IFA GoodRead) and the handbook's
example folder. Run twice, independently. Files: `<scratch>/D1/`, `<scratch>/D2/`
(`answers.json`, scripts, tamper copies), questions in
`<scratch>/prep/lens-d-questions.md`.

| Measure | D1 | D2 |
|---|---|---|
| Handbook files needed for all ten | 13 (about 2,900 of 7,973 lines) | 9 in substance, 5 more by search |
| Concepts before the first answer / for all ten | 14 / about 45 | about 12 / about 48 |
| Script size | about 1,200 lines | 989 lines |
| Objects whose two digests matched at the first attempt | 40 of 40 | 40 of 40 |

**Agreement.** Checker 4 compared the two `answers.json` files. On 8 of 10
questions (1, 2, 3, 4, 5, 6, 8, 9) the ids, dates, values, digests and verdicts
are identical. Five differences remain, on questions 7 and 10: two are one
reader's mistakes (D2 attached a Deviation to a finding that has none, and
called a risk "pending" that has no treatment), one is a passage D2 missed (the
anchor of a review period), one is presentation, and one is a real ambiguity:
whether a provenance date a converter filled in is the date of a decision.
Wherever a reader cross-checked against the reference validator, the answers
agreed.

So the data can be read consistently from the handbook alone. Where both
readers reported low confidence, they reported it on the same points, which
makes these properties of the documents or the notation:

| Both readers were unsure or stuck | Why |
|---|---|
| Which tier a Tailoring has (question 2) | ch06:176-180 reads two ways; the tier names appear nowhere in the handbook; the normative rule is spec:836-861 (D1-3, D2-3) |
| Which part of a shared clause is inherited (3, 4) | the edge lists mechanisms, not parts (D1-6, D2-5) |
| Which system a finding is against (5) | a Finding has no such field (D1-10, D2-8) |
| Whether an exception is "in force", and until when (6) | no end date; "in force" only by implication (D1-13, D2-12) |
| Which clause a risk justifies (7) | coverage is computed per requirement (D1-15, D2-13) |
| What the authorization rested on (10) | an authorization refers to nothing; the Attestation does not name it (D1-25, D2-23) |
| How to verify a signature (9) | the profile is not in the handbook; both guessed from general knowledge and happened to be right (D1-21, D2-19) |

Both readers also found, independently, that the reference validator reports
`FULL MATCH` and exits 0 for the unsigned Attestation after its content and
digests were rewritten (D1-23, D2-22).

### 5.4 Experiment E — the cold implementer

Brief: write a validator from the specification, the schema, handbook chapter
12, Appendices A and B and the vectors, for six of the eighteen vector families
(canonical form and digests, kernel shapes, reference closure, modality,
parameters, tailoring), without opening the reference validators. Files:
`<scratch>/E/jv.py`, `harness.py`, `first-run.txt`, `final-run.txt`.

| Family | First complete run | Final | Final passes not derivable from the text |
|---|---|---|---|
| jcs | 15 / 22 | 22 / 22 | 1 |
| kernel | 67 / 71 | 71 / 71 | 4 |
| reference | 15 / 18 | 18 / 18 | 1 |
| modality | 21 / 21 | 21 / 21 | 0 |
| parameter | 20 / 22 | 22 / 22 | 2 |
| tailoring | 16 / 19 | 19 / 19 | 3 |
| **all** | **154 / 173** | **173 / 173** | **11** |

Size: 573 lines of Python plus a 95-line harness, with `jsonschema` for the
schema step. Reading: about 1,200 of the specification's 2,539 lines plus
chapter 12 and both appendices in full, roughly 2,700 lines of prose.

Checker 4 opened all eleven vectors and tried to derive them from the permitted
documents. All eleven stand. For seven the verdict itself cannot be derived: in
four the vector's own data violates the schema and is labelled valid, one rule
exists only in the register and the validator, two are ambiguous in the text
and unambiguous only in the register. For four the failure count is derivable
and only an expected message substring is missing, which contradicts chapter
12's statement that vectors never hold to message text (E-2, E-3, E-6).

Eight disagreements between specification, schema and appendices were
confirmed, 8 of 8 (E-8): `canonical-alias` as object or array, `replaces` with
`relationship` or `mode`, `calendar-ref` optional or required,
`Mapping.rationale` string or language map, eight or ten primitives, chapter 12
as companion to "Specification v0.5", Attestation fields marked required that
the schema does not require, three or four responsibility codes.

What the experiment does not cover: the subset is 173 of 705 vectors and the
easier ones. There is no tailoring resolver in it (the tailoring vectors test
single operations on fragments, E-13), no risk join, no check engine with its
hand-written pattern matcher, no signatures. Reader E estimates 1,600 to 2,300
further lines and "two to three weeks for one developer" for the whole. That is
an estimate, not a measurement.

### 5.5 The complexity, sorted

**What the domain forces.** All three experiments, and lens H from the
auditor's side, name the same list: requirements addressed clause by clause;
binding strength; typed parameters and deadlines; a baseline as a selection
plus recorded changes; an exception with an approver; shared responsibility and
inheritance on a named basis; results with dated actions; a risk that names the
controls it justifies; evidence a second party can re-perform; a signature over
a defined state. Each cold reader's own sketch of a spreadsheet or home-made
JSON needed the same things. OSCAL 1.x carries them in seven to eight document
models; a GRC tool's export carries them as columns whose meaning lives in the
tool.

**What the design adds, and what it buys.**

| Addition | Cost seen in the experiments | What it buys |
|---|---|---|
| Global URIs for everything, one file per object, a manifest between every reference and its file | 36 files for a small case; every question is a join over two to four files | objects from several authorities combine without merge rules |
| No type field; type follows from shape | every consumer script starts with a classifier (11 rules, of which the handbook states 2); a nested mistake is reported against the wrong type | nothing the experiments could see |
| Two digests, a canonical form, a regenerated manifest | a helper program and a build step per edit; re-issuing the Attestation after any change; the canonical-form law is where the implementations diverge (G-7) | a second party can recheck integrity; two cold readers did so at the first attempt |
| Tier derived from the origin of an id | both consumers unsure; the author got the exception duty only by inventing a second origin | lets an authority amend its own content without recording exceptions |
| Facets with pinned schemas | in the converted bundle most of what an auditor reads sits in eleven private facets; bundle-specific code needed | the kernel stays small; framework detail has a contract when the schema is strict |
| The verdict vocabulary (Full Match, Semantic Match, claimed, proven, attested, verified, the bracketed qualifiers) | easy to over-read: the best verdict word is reached by an unsigned file | precise distinctions for a reader who knows them |
| One result per Assessment, a spare Finding | one audit becomes many objects or loses information | the kernel "refuses to pick a methodology" (ch10:50-57) |
| A specification written as a decision register with amendments | rules for one topic spread over several decisions; reading dominates coding (E-9) | every rule has its reason on record |

**What is neither domain nor design, but the state of the documents.** A large
share of what the experiments tripped over is repairable without touching the
standard: chapter examples that do not validate, appendix tables that disagree
with the schema, stale counts, a documented Deviation form that fails, a
signature profile that is not written down, vector files without a format
description, four vectors whose own data is invalid, an error message that
names the wrong type. Checker 4 confirmed these item by item.
## 6. All findings, by weight

**How to read this section.** Ids are the reviewers' (lens letter and number;
D1 and D2 are the two consumer runs). Where several reviewers found the same
thing independently, the ids share a row; that independence is itself evidence.
Evidence kinds: *measured* (recomputed in this run), *demonstrated* (a built
input the tools accept or refuse), *quoted* (file and line), *argued*.
"Check" gives the result of the refutation attempt by an agent that did not
produce the finding: *survives*, *survives, corr.* (with the correction worked
into the statement), or *not checked*. V stands for
`python3 jascon/scripts/validate_core.py`; K for
`jascon/conformance/fixture-trusted-keys.json`; "spec" for
`drafts/jascon-specification-2.0.0-rc.4.md`; "register" for
`drafts/jascon-decision-rationale-register.md`. Levels of use: L1 pilot in one
team, L2 working format beside the GRC tool, L3 system of record, L4 exchange
with auditors, regulators and suppliers.

Every demonstrated finding is stated so that it can be rebuilt from this text:
take the named folder, make the named change, recompute the manifest digests
(package digest: SHA-256 of the file's bytes; semantic digest: SHA-256 of the
canonical JSON of the object without `annotations`), run the command.

### 6.1 Blocks

| Id | Q | Statement | Evidence (kind) | Consequence | Declared by the project? | Conf. | Check |
|---|---|---|---|---|---|---|---|
| G-1, D1-23, D2-22, H-3 | Q2 (L4; weighs heavily L3) | A run with `--trusted-keys` ends `ALL GREEN`, exit 0, for a tampered bundle whose Attestation was deleted, stripped of its envelope, re-signed under a signer absent from the key file, or made unparseable. Only a wrong signature under a known signer fails. No option requires that a verified Attestation exist. | demonstrated four times independently. Recipe: in a copy of `jascon/examples` change `implementation-acme-konf.json` `status` to `planned`, recompute the manifest, write the new digests into `attestation-acme-2026.json`, delete the `.dsse` file and the `envelope-ref` member; `V <copy> --trusted-keys K` → `no envelope (unsigned attestation)`, `FULL MATCH`, `27 pass, 0 fail`, `ALL GREEN`, exit 0. With the envelope kept: `dsse: FAIL`, exit 1. | A supplier's bundle is altered on the way. The attacker removes the signature instead of forging one. The receiver's pipeline, which gates on the exit code with keys supplied, passes it. | Partly. The output line says "unsigned" or "UNVERIFIED" (register:912-921). Two texts say the opposite of the behaviour: spec:552-553 defines Full Match as "signature valid, …"; ch11:238-240 says "unverifiable envelope — is failure". | high | survives (checks 1 and 5) |
| G-5 | Q2 (L4; weighs L3) | There is no key lifecycle. The trusted-keys file is a flat map from signer URI to public key; nothing in the notation or the tools expresses expiry, revocation, rotation or trusted time. An Attestation dated 2099 verifies. Authority is matched by origin (scheme and host), so a trusted key of any party under a host proves publisher and tier for every party of that host. | quoted: spec:561-563 calls the stdlib DSSE profile "normative about … signer identity, trust roots, timestamps, expiry/revocation"; `jascon/schemas/stdlib/dsse-envelope-1.0.0.json` contains none of these; ch11:299-320 lists them as questions for the receiver. Demonstrated: timestamp `2099-01-01T00:00:00Z` → `signature VERIFIED (Ed25519)`, `publisher PROVEN`. | A supplier's key leaks. Nobody can say so in the format, and every Attestation made with it verifies for ever, with any date. | Key distribution is declared "authority-local" (register:915). That the promised items are not delivered is not declared. | high | survives, corr.: the verifying key is bound to the Attestation's `signer` (`validate_core.py:611`); one party's key verifies another's statement only if the key file lists the same key for both, as the shipped fixture file does. Ignoring `keyid` follows the DSSE specification. |
| H-2, G-3 | Q2 (L4; weighs L3), Q1 | The rendering, the paper a person reads and signs, is not bound in practice. The Attestation carries `rendering.artifact-digest` and the manifest lists `renderings` with a digest; no tool reads either. A replaced or deleted rendering passes as verified. No renderer exists, and the template the example names exists nowhere. | demonstrated twice. Recipe: append a sentence to `authorization-summary.md` in a copy of `jascon/examples` (or delete the file); `V <copy> --trusted-keys K` → `signature VERIFIED (Ed25519)`, `FULL MATCH`, `ALL GREEN`, exit 0. Measured: `grep -n "rendering\|artifact-digest" jascon/scripts/validate_core.py` → one unrelated line (3135). | An official signs over the digest of a summary. Someone replaces the summary. The receiver's tool says verified and full match, and the document read is not the one signed. | No. spec:461 says only that the manifest's `renderings` is "read by no validator". Against it: spec:553-554 ("exact packaging and presentation state proven"), appendix-f:365-366 ("pins make render-tampering detectable"), `jascon/examples/README_1.md:42`. | high | survives (check 1) |
| I-4, A-14 | Q2 (L3, L4; weighs L2), Q1 | The released 1.0.0 is not anchored. The public repository has no tag and no release, though the documents say "✓ tagged 2026-07-22" (spec:2470; register:1328, 1401; README.md:443). The 1.0.0 schema is not in the tree. The 1.0.0 specification file, described as "unchanged", was edited after release and now names a media type and a schema file that did not exist at 1.0.0. | measured: `git ls-remote --tags origin` → empty; GitHub tags and releases lists → `[]`; `git diff 0b949fa3:drafts/oscal-semantic-core-specification-1.0.0.md HEAD:drafts/jascon-specification-1.0.0.md` → 16 insertions, 11 deletions. | "Use the released 1.0.0" cannot be carried out without knowing that commit 0b949fa3 is meant. An auditor cannot cite an immutable artefact. Cheap to repair. | No; the documents state the opposite. Whether a tag once existed locally cannot be told. | high | survives, stronger (check 3) |
| I-8 | Q2 (L4; weighs heavily L3) | No use outside the project was found. No fork, no outside repository containing the namespace, schema name or media type; one outside star. Ten of twelve issues came from one outside account on one day. The project's only outside exposure found is the author's draft pull request 2267 against OSCAL, which proposes the facet idea there, with one outside reply. | measured: GitHub repository data (2 stars, one of them the author's second account; 0 forks); code search for `ns.jascon.net` → 1,226 hits, all in this repository. Not reachable: other hosts, private repositories. | At L4 the counterparty chooses the format. No auditor, regulator, supplier or tool vendor reads this one. | Yes: `website/src/join.html` ("no known user outside its repository"); Appendix F Q20. | high (GitHub), medium (elsewhere) | survives, corr. (check 3) |
| F-6 | Q2 (L3; weighs L2) | The notation has no tenancy, access control, ownership of objects or party record. Parties are URIs nothing resolves; authorship is a claim. | quoted: spec:1877-1880 ("No party type (#16)"), spec:1836-1838 (`provenance` is "a claim"); appendix-f:602 places the format at "the file that goes to the auditor" while ch15:188 says "source of truth". | A system of record for dozens of legal entities needs to say who may write and read what. All of that has to come from the system around the bundle. | Partly (the missing party type and log are declared; access and tenancy are not discussed). | high | survives, corr.: accountability is carried (`owner-ref`, `author-ref`), as unresolved URIs; "source of truth" in ch15 is said of the direction relative to OSCAL; access control and tenancy are declared a non-goal nowhere |
| F-13 | Q2 (L2 for lifecycle data; weighs heavily L4) | Lifecycle data cannot be exchanged with existing tools. The OSCAL export covers Requirements and Sets only; the one lifecycle import is a converter written for one example; nothing exists for spreadsheets, a GRC tool's interface, a CMDB or ticketing. | quoted: `jascon/scripts/export_oscal.py:19-22, 297-311`; README.md:444-445 lists the lifecycle exports as "Next". | Beside a GRC tool, the systems, implementations, assessments and findings are exactly what would have to move. The adopter builds every bridge. | Partly (README "Next"). ch14:384-386 claims a Mapping export no code performs. | high | survives, corr.: the pack builder imports any OSCAL component definition into Components; nothing imports SSP, assessment results or POA&M beyond the example converter, and nothing exports lifecycle objects. The export script also fails here without the `regex` package and a schema file CI downloads |

### 6.2 Weighs heavily

| Id | Q | Statement | Evidence (kind) | Consequence | Declared? | Conf. | Check |
|---|---|---|---|---|---|---|---|
| D1-24, G-4 | Q2 (L4) | A verified Attestation covers only the objects it names, and the tool's message says more. After a change to a requirement the attested Implementation points to, and after removal of a Finding, the run prints "SEMANTIC MATCH [… the content is proven, the packaging was altered]", exit 0. | demonstrated twice. Recipe: in a copy of `jascon/examples` replace `SOLLTEN` by `KÖNNEN` in `req-konf-14-1.json`, recompute the manifest; `V <copy> --trusted-keys K`. | An official signs three objects. The receiver reads "proven" for a bundle in which the requirement behind them was weakened. | The two-state design is declared (spec:551-559). The wording comes from the spec itself ("compliance content proven; packaging altered in transit"); ch11:224-236 says a packaging-only change "provably cannot have altered what the normative rendering said". The "subjects-in-bundle completeness" promised at spec:561-563 is implemented nowhere. | high | survives, corr.: the defect is in D7 and ch11 as much as in the message |
| H-3 (second half), check 1 | Q2 (L3, L4) | An Attestation file that the schema refuses, or that is not valid JSON, is skipped without a word. This removes a failure: an Attestation that would fail `attestation-binds` passes once any unknown member is added to it. | demonstrated. Recipe: in a copy of the IFA bundle set one subject digest in `attestation-ifa-ato.json` to zeros → exit 1; add `"opinion": "unqualified"` to the same file → no `dsse` or `binds` line, `17 pass, 0 fail`, `ALL GREEN`, exit 0. Cause: `validate_core.py:3153-3158`. | A certification body adds a field of its own, or a file is damaged; every run stays green and the receiver assumes an attested package. | Known to the project (register:3802-3806, backlog #71 item 9), filed as a difference between reader and reference, not as a hole. | high | survives, corr. (more severe than reported) |
| G-6, C-6, D1-3, D2-3 | Q2 (L4; weighs L3), Q4 | Who owes a recorded exception is decided by the origin of an id. A Tailoring minted under the requirement's own host is "authority-claimed" and may weaken without a Deviation, also with keys supplied; the same Tailoring under another host fails. At the claimed tier a parameter value above its declared maximum is accepted without a note. An organisation that keeps its requirements and its Tailorings under one origin has no Deviation duty and no author duty at all. | demonstrated three times. Recipe: a Requirement, a one-member Set and a Tailoring with `set-modality` to `may` and no Deviation; Tailoring id under another host → `tier … = consumer`, exit 1; under the requirement's host → `authority-claimed [prefix claim - UNPROVEN]`, `ALL GREEN`, exit 0. | The duty binds only the honest. A company's internal policy, the commonest case, gets none of the checks the handbook describes for tailoring. | The origin rule is declared (spec:835-858; register:471-473: "anyone can mint under a URI they don't control"; Appendix F Q11). Not covered by it: the out-of-range value (ch06:127-132 says the range is validated "always"). No switch lets a receiver refuse a claimed tier. The handbook never states the consequence for a single-origin organisation; its tier rule (ch06:176-180) reads two ways and the tier names do not occur in it. | high | survives, corr. (checks 1, 4, 5) |
| C-2, C-1, check 1, check 4 | Q2, Q4 | The exception duty can be met without an exception. Any string in an operation's `deviation-ref` satisfies it; so does an inline Deviation in state `withdrawn` or `investigating`. The form the handbook documents (a `deviations` list on the Tailoring) does not satisfy it. | demonstrated. Recipe: in `tailoring-elevated.json` add `set-modality` on KONF.14.1 s2 to `may`: no Deviation → exit 1; with `"deviation-ref": "nonsense"` → exit 0; with the handbook's Tailoring-level list → exit 1; inline with `"state": "withdrawn"` → exit 0. Cause: `validate_core.py:418` tests presence only. | A green run does not show that a weakening was approved. An author following the handbook is refused and has to read the schema. | No. `deviation-ref` occurs in the schema and the validators and in no document. ch10:185 and appendix-f:544-545 say only an approved Deviation licenses a weakening. | high | survives (two checkers) |
| H-5, C-7 | Q2 (L3, L4), Q1 | An Assessment of manual audit work cannot say what was in scope, over which period, from which population and sample, or what the result per control was: one `result`, one instant, untyped subjects. Per-control results exist only for machine check rows. | demonstrated: six fields refused; one audit with a failed and a passed requirement had to be split into two objects. Schema properties listed by checker 4. | A type 2 test of controls or an ISO 19011 sample becomes one object per control with a free-text method, or one object that says `satisfied` about everything. Two audit firms will write two private facets. | The spareness is declared as a choice (ch10:38, 50-57). Its cost for period-of-time assurance is discussed nowhere. | high | survives |
| H-6, D1-10, D2-8, D1-11 | Q2 (L3, L4), Q4 | A Finding has no typed place for the condition found, a grade or severity, the root cause, the owner of an action, its completion, or verification of the fix. It names no system. The status of an action is free text. | demonstrated: the fields are refused; they fit a facet the bundle pins itself. | A certification body and its client can exchange nonconformities only after agreeing a facet. None is published, so each will write its own, which is what the project holds against OSCAL's props. "Open majors past due, by owner" cannot be computed from kernel fields. | ch10:122-129 presents the reduction to "description, due, status" as a gain. | high | survives |
| D1-25, D2-23 | Q2 (L4) | Nothing in the data links an authorization decision to the assessment, findings and risks it rested on. The authorization sub-object holds id, authority, date and a label; the Attestation does not name it. | quoted: schema properties of `authorization`; demonstrated on the IFA bundle (question 10 of experiment D, both readers). | The chain an external auditor asks for breaks at its last link. In the IFA bundle the authorization of 2025 stands beside an assessment of 2023 that says `not-satisfied` and two findings with overdue actions, and no object says the official knew. | No. | high | survives |
| D1-13, C-5, H-7, D2-12 | Q2, Q4 | An approved exception has no end date and a risk acceptance has no expiry. `review-due` is optional; an overdue review is reported and never fails a run under any option; a missing review date is reported by nothing. | quoted: spec:626-634, 1862; demonstrated (`review-due` 2020-01-01 → exit 0). | The converted NIST example carries an exception approved in 2023, in force without limit. "Accepted until" has to be read as "review due". | Yes (appendix-f:608-621, as an open limit). The reason given is thin. | high | survives |
| D1-2, C-11 | Q2, Q4 | No field says which baseline (Tailoring) governs which system. The joins the design intends run through a Risk or an Assessment. | quoted: spec:781-788 ("A Tailoring names no Component", author decision 2026-11-12; `component-refs` "considered and not added: no corpus demands it"). | "Which requirements apply to system X" is the first question of experiment D. For a system with no risk and no check run the data has no answer; the cold author invented a relation for it. | Yes, in the specification; not in the handbook. | high | survives |
| H-8 | Q2 (L3, L4) | Separation of duties cannot be shown and is not checked. Assessor equal to implementer, and the author of a weakening equal to its approver, both pass without a note. There is no requester, no second approver and no party record. The shipped example models one person as author, assessor and approver. | demonstrated; quoted: spec:1877-1880. | A test of independence is at best a comparison of self-declared URIs. The real answer still comes from the access log of the system around the bundle. | The missing fields are declared. The consequence is not drawn. | high | survives |
| H-10, F-9 | Q2 (L3) | A bundle holds the present state only: one version per id, one manifest, no change log, nothing on retention. Two editors who each add an object collide in the manifest. Evidence for manual work is a URI without a digest, and a reference to a file that does not exist passes. | demonstrated (dangling `evidence-refs` → `ALL GREEN`; second version of a Finding → refused; the merge conflict in `<scratch>/F/gitdemo.sh`); quoted: spec:1832-1834. | "Who closed this finding, and when" is answered by a pile of earlier bundles somebody has to keep. A system of record needs a repository with its own audit trail around the format. | The no-log decision is declared. The difference between machine evidence (three digests) and manual evidence (none) is not. | high | survives (checks 1 and 6), corr.: the manifest conflict arises when both editors append at the same place; composing two bundles (`--compose`) reconciles facet pins only and closes no references across them |
| H-4 | Q2 (L4) | The defined signature is Ed25519 in a DSSE envelope with a locally supplied key. It is not a qualified electronic signature. | quoted: ch11:302-320; the stdlib descriptor. Outside fact (eIDAS Art. 25(2)): confirmed through secondary sources only. | Where a signature has to stand for a handwritten one, an EU reader needs a qualified signature or ink on the rendered PDF. The document, not the graph, is then the legal object. | Not as a limit. | medium-high | not checked beyond G-5 |
| H-13 | Q2 (L4), Q1 | "Documents become renderings of the graph rather than the unit of exchange" (README.md:356-357) does not hold today for the five assurance readers lens H walked. The auditor's report, the management statement, the Statement of Applicability as a table, policies and minutes, and regulator returns such as the DORA register are still required as documents, and JASCON can render none of them. | argued, on H-2, H-4, H-5, H-6. What each regime prescribes was confirmed through secondary sources only; the standards bodies' and regulators' own pages were not reachable. | An enterprise that adopts JASCON for exchange with auditors keeps producing every document and adds a bundle. | D17 declares the management-system clauses out. The README states the bet without that limit. | medium-high | not checked |
| A-4 | Q1 (G2, G3d) | For the converted content, "valid" does not imply "checkable meaning". 25 of 27 converter-written facet schemas constrain only the first key level. In the shipped BSI bundle, a `tags` array replaced by one comma-packed string validates. | demonstrated twice. Recipe: in a copy of `converted_examples/DE.BSI/bsi-core-bundle`, in the Requirement ARCH.2.1, replace the taxonomy facet's `tags` array by the string "Lateral Movement, Separation of Concerns, Zero Trust"; recompute the manifest; `V <copy>` → `1288 pass, 0 fail`, `ALL GREEN`. | A consumer who relies on "facet-valid" for the 64 % of converted bytes that sit in facets gets a check on one key name. ch07:165-168 says of exactly this case that such strings "are now unwritable". | The three layers are declared. That the stubs are open below the first level is not; register:1033-1043 ("the smuggle demo is dead") and each stub's own note say the opposite. | high | survives, corr.: it is the converters' choice, not a limit of the notation (a strict schema refuses the same input); the split is 64 % of bytes and 44 % of values, not 71 % |
| A-3, I-16 | Q1 (G6), Q2 | The OSCAL export is a lossless wrapper, not a compilation an OSCAL tool can fully use. Groups, titles, statements, parameters and links are native; guidance, the SP 800-53A objectives and all Sets ride props in JASCON's namespace (61 to 66 % of the compact bytes), although OSCAL has native parts for guidance and objectives. The round trip runs JASCON → OSCAL → JASCON; it covers two of eleven types; no CI step runs it. | measured twice: export re-run on a copy, 4,198 of 4,198 objects digest-equal on four bundles; `grep -c export_oscal .github/workflows/validators.yml` → 0. | A team that exports to feed an OSCAL tool gets ids, titles, statements and parameters, and loses guidance, baselines and everything about systems. The exit towards OSCAL exists for catalogues only. | The wrapper nature is declared (`export_oscal.py:8-17`; `drafts/gate-4-measurement.md` §4; D16). The share is not, nor that OSCAL-expressible content takes the props route. | high | survives, corr. |
| A-6, B-2, I-3 | Q1 (G4, G5), Q3, Q2 | The rule that guarded the kernel was set aside when it was needed. Risk entered on 2026-11-10 as a recorded exception; on 2026-11-12 D22 was amended with a clause that admits Risk and Check; `statement-ids` and `product-version` then entered against the amended rule. Four candidates appeared in four days; proposals became candidates in 16 hours, 9.6 hours and 15 minutes; rule changes that fail formerly valid bundles landed "without a new candidate". An optional module, neither kernel nor facet, was never weighed. | quoted: spec:12-28, 1097-1158, 2503-2506; register:1619-1641, 2087-2121; measured: commit timestamps. | Kernel stability cannot be planned on: the bar is the author's decision. "rc.4" names at least three rule sets, so only a commit pin identifies one. There is no window in which anyone else could comment. | Yes, each step, plainly. That is a strength of the record. What it means for someone who depends on the kernel is not said. | high | survives, corr. (quotes attributed correctly; the kernel pin and the conformance tiers soften the cost for consumers, not for implementers) |
| B-1 | Q3, Q1 | What 2.0.0 added to the kernel is unmeasured on real content. The released 1.0.0 schema types 4,206 of the 4,214 shipped objects; the additions account for 44 of 58 named rules and 370 of 705 vectors and tripled the validators. | measured twice. | A second implementer has to build a risk join, a check engine and a hand-written pattern matcher to be conformant, for content that exists in an example folder. | Partly (spec IV.1; spec:104-116). | high | survives, meaning corrected: the shipped corpus is a catalogue corpus that exercises hardly any lifecycle type, old or new; the number does not show the additions are unneeded |
| I-5, F-11, F-12 | Q2 (L3, L4; weighs L2) | Released content did not survive the next major. Between 2026-07-22 and 2026-11-14 the namespace of every identifier changed twice (26 minutes apart), the media type and the schema file were renamed, five fields were tightened and kernel-wide rules were added. The bundles as released at 1.0.0 (commit 0b949fa3), run through the rc.4 validator with their line endings restored: eight of eleven pass; CIS Ubuntu fails 635 times, CR26 twice, IFA four times, the example folder twice. All 635 are one cause: the 1.0.0 converter wrote the catalogue version into `Mapping.provenance.date`, which rc.4 types as a date. The renamed identifiers cause no failure. No migration tool exists. | measured twice (lens F, checker 6): `git archive 0b949fa3`, restore the digested line endings, `V <bundle>`; schema only: 6,279 of 6,914 objects match a type. quoted: register:2067-2068. | For a design study this is the right priority. For a system of record it is the record an enterprise looks at first. | Each change is declared, and the project's own rules allow all of it inside an untagged major with no known outside holder (register:2263-2269). The total, and the missing tool, are not stated. The sentence at spec:89-95, "all 6,914 objects of the 1.0.0 corpus validate unchanged under the 2.0.0 schema", is false as written for rc.4 (635 objects, 9.2 %, match no type); it was true at rc.1 and holds for the bundles that still ship. README.md:256-258 repeats it. | high | survives, corr. (checks 3 and 6): a stability record, not a rule violation; as checked out from git every 1.0.0 bundle also fails on line endings, which `.gitattributes` declares |
| I-6 | Q2 (L3, L4) | One person carries the project. The public history has one human identity and eight active days; 74 % of the 395 commits are authored by an AI assistant and 86 % carry its co-author trailer; all 25 pull requests were opened and merged by the owner, half of them within 17 seconds. The commit under review is 164 commits ahead of `main` on a branch without a pull request. | measured twice on a full clone. | No second person has committed, reviewed or held rights. The three implementations that define conformance share one author and one assistant. | "Personal capacity": yes. | high | survives, corr. |
| I-1 | Q2 (L3, L4) | There is no written change process, versioning or deprecation policy for the specification, security contact, code of conduct or contribution agreement. | measured: no such file; README "Contributing" is five lines. | An architect filling in a technology approval has nothing to cite. A flaw in the signature check has no private channel. | Partly. | high | survives, corr.: `website/src/join.html` has a section on how a change gets in |
| I-11 | Q2 (L4) | No standards body is named as a path, and the one route to recognition the handbook cites does not exist in the form cited. ch15:210-214 and Appendix F Q19 present as "current federal policy" a clause from FedRAMP's RFC-0024, a proposal that closed on 2026-03-11. The clause says providers "agree to use", not "maintain", requires a public-domain format, and is absent from FedRAMP's rules in force. | online, 2026-11-14: the RFC discussion (FedRAMP/community 114); `fedramp-consolidated-rules.json` v2026.11.02.01 fetched afresh, no occurrence. The README's quotation of the same RFC ("100+ Rev5 authorizations … without a single submission that used OSCAL") is accurate. | An adopter who plans on that route plans on a rule that is not in force and would not admit an Apache-licensed format. | No. ch01:52 says "proposing"; ch01:66-69 says "the exit door is written into the policy". | high / medium | survives, corr. |
| E-2, E-3, E-6 | Q1 (G3f), Q4 | The documents are not sufficient to derive the conformance results. Of 173 vectors in six families, 11 expected results cannot be derived from specification, schema, chapter 12 and Appendices A and B. | measured: `<scratch>/E/final-run.txt`; each of the 11 re-examined by a reader with access to everything. | An independent implementer has to fit to expected values, and in four cases to the reference's message wording. | Partly (ch12:59-63: the corpus is the specification). | high | survives, corr.: 7 verdicts not derivable (4 of them because the vector's own data violates the schema), 4 only a message substring |
| E-7 | Q4 | Which references must resolve inside a bundle and which need not is normative and nowhere listed in full in the specification or the handbook. | quoted: appendix-b:24-27 and ch12:114-115 say every reference must land in the manifest; the full list is in the register (434-446) and in a vector file's description. | Following the appendix literally rejects every Mapping endpoint and every party. | Partly (appendix-b:41-46 names the split and points to the register). | high | survives, corr. |
| E-13 | Q1 (G3f) | The tailoring vectors test single operations on fragments. Selection, set expansion and the resolved result are exercised by no vector in that family. | measured: key census of `jascon/conformance/tailoring-vectors.json`. | A validator can pass the family without a resolver. | No. | high | not checked |
| C-4, H-15, F-4 | Q4 | A mistake nested inside a Tailoring, Finding, Risk or Component is reported as "matches NO type (closest requirement: 'statements' is a required property)". The now untyped object then causes follow-on failures that point elsewhere. Invalid JSON in a listed file gives a traceback that names no file. | demonstrated by three reviewers and the checker. Cause: `validate_core.py:3077-3078`. | The author is sent to the wrong type with no field named. | No. | high | survives, corr.: top-level mistakes are reported against the right type |
| D1-21, D2-19, C-13 | Q4, Q2 | What is needed to produce or verify a signature independently is not in the handbook or the specification: the algorithm is in the validator's source, the signing input in a note of a stdlib file that points to the DSSE specification, the key-file format in a source comment. | quoted: `validate_core.py:519-521, 593-595, 3507-3508`. | Three cold readers guessed from general knowledge. One fed a base64 key and got "no signature verifies" instead of a complaint about the key. | No. | high | survives |
| D2-7, D1-9, H-12 | Q2 | In the converted NIST example the authority of both authorizations and the signer of the Attestation were written by the converter with no source value, and the bundle does not mark them. | quoted: `converted_examples/US.IFA-GoodRead/ifa-coverage-report.md` ("Values without a source x3"). | A consumer of the bundle reports an authorizing official no source names. | Yes, in the report beside the bundle; not in the bundle. | high | not checked |

### 6.3 Weighs

| Id | Q | Statement | Evidence (kind) | Declared? | Check |
|---|---|---|---|---|---|
| G-7 | Q1, Q2 (L2–L4) | The JavaScript port computes a different canonical form, and so a different semantic digest, for member names that look like integers and for a member named `__proto__`. A Requirement with clause ids "2" and "10" and a per-clause facet that the reference accepts is refused by the app, and the app's own export of it is refused by the reference. No vector covers the case. RFC 8785 sides with the reference. | demonstrated twice: `{"id":"x","m":{"10":"a","9":"b","a":"c"}}` → JavaScript `…{"9":"b","10":"a","a":"c"}`, Python `…{"10":"a","9":"b","a":"c"}`. Cause: `jascon-app/jascon-core.js:156-170`. | No; the code comment claims the orders agree. | survives |
| G-8 | Q2 (L3, L4) | Malformed input. Duplicate member names are accepted by both ports (a reader sees `must`, the tools compute `should`). A byte-order mark, a lone surrogate, nesting from depth 900, a file that is an array, and several malformed manifests end the Python reference with a traceback that aborts the whole run; deep nesting also crashes the port. The number rule (NUMBER-1) holds on seven spellings in both. | demonstrated twice. RFC 8785 requires refusal of duplicate names (checked online). | NUMBER-1 yes; the rest no. | survives, corr. |
| G-9 | Q2 (L3, L4) | A manifest `path` may leave the bundle folder (`../x.json`, absolute paths, symlinks); the reference reads such files and counts them as bundle content, the port reports them missing. | demonstrated twice. Cause: `validate_core.py:3288`. | No. | survives (scope: the outside file must match the listed digests) |
| G-10 | Q2 (L3, L4) | A `pattern` in a facet schema the bundle pins itself runs on the host's backtracking engine: `^(a+)+$` against 27 a's and "!" costs about 6.5 s over baseline in both ports and four times that per two more characters. The pattern engine for Check criteria is bounded (G-11). | measured twice. | No. | survives, corr. (absolute time) |
| G-12 | Q2, Q1 | The reference's `--import-advice` dry run clears a pack whose files do not match its own manifest; the app and a plain validation refuse the same pack. | demonstrated twice. Cause: `validate_core.py:3543-3552`. | No. | survives, corr. |
| G-2 | Q2 | `FULL MATCH` and, without keys, `authority-proven` are printed for a self-made unsigned Attestation; the qualifier follows in brackets. | demonstrated; quoted spec:553-554. | The bracket text is the declared mitigation. | survives |
| G-15 | Q1, Q2 | The facet registry is the sender's own manifest: a self-pinned facet that declares itself harmless and reads like a waiver validates, and the reference prints no inventory of facets it does not understand, which ch13:108-110 asks tools to do. | demonstrated twice. | Yes (spec:712-715 names the limit itself). | survives |
| H-11 | Q2 | An Assessment may say `satisfied` while an open Finding stands against it. | demonstrated twice. | No. | survives |
| D1-12, D2-10 | Q2 | Overdue review dates are reported; overdue action dates of findings are not, although ch10 §10.4 is titled "Deadlines that compute". | demonstrated on the IFA bundle (actions due 2024-01-01 and 2024-06-23). | The report's scope is declared by enumeration (spec:1852). | survives, corr. |
| D1-15, D2-13 | Q4, Q2 | Risk coverage counts a requirement as justified when a Risk names one of its clauses. | quoted: appendix-b:254-255; spec:1284. | Declared, without a reason. | survives |
| F-5 | Q2 | An Implementation may cite a clause its Requirement does not have. | demonstrated (`<scratch>/F/mist/10-statement-id-typo`). | No. | survives, wider: `Finding.statement-ref` is unchecked too; a Risk's `statement-ids` are checked (RISK-8) |
| F-10 | Q2 (L3, L4) | `canonical-alias`, of which D2 says "validators substitute freely", is not applied to reference closure: a renamed Component with an alias gives closure failures. | demonstrated twice: give `component-paas.json` a new id and `canonical-alias: [{"of": <old id>}]`, leave the Implementation on the old id → `inherited-from component does not resolve in-bundle`, exit 1. ch03:185-191: "nothing downstream needs to change or even notice". | No. | survives |
| F-3, F-14, G-17 | Q2 (L2, L3) | The reference tooling is an executable specification, not deployable software: no package, version, library entry or machine-readable result; exit code 0 or 1; the first 60 failures only; no `--help`; every run also judges the repository's example folder and folds it into the exit code, so an operator's own key file turns a clean target red. | demonstrated (`V --help` is read as a folder name, orchestrator's run); quoted `validate_core.py:3505-3611`. | Partly. | survives (checks 5 and 6): a crash, a mistyped option and an invalid bundle share exit code 1 |
| F-2 | Q2 (L3) | Two quadratic spots: tier derivation per Tailoring in the reference; a scan of all ids per message in the port (8,000 systems: 679 s). | measured (profiles in `<scratch>/F/`). | No. | partly: three points re-timed and confirmed; in the 2,000-Tailoring profile tier derivation is 36 of 309 s, so the slower shape rests on the one 8,000-Tailoring run, not re-run |
| F-7 | Q2 (L4) | A bundle from which leaf objects (two findings, a risk) were removed stays green and its Attestation turns from Full Match to Semantic Match, the same mark as for a stripped annotation, with the text "the packaging was altered". There is no redaction below the object. Useful for partial disclosure, and the reverse of G-4. | demonstrated twice. | Not found. | survives, corr. |
| F-8 | Q2 (L3) | Findings and risks are clear-text files; "sealed" means offline, not encrypted. | quoted: spec:1566, 1584; ch11:153-155. | Yes. | not checked |
| A-2 | Q1 | "100 % coverage" is a statement about source paths. At value level, on six corpora: 58.0 % carried, 41.1 % ruled not content, 0.9 % dropped, none unaccounted. | measured twice. | Partly (spec IV.2 R16; README.md:22-25). | survives; the 41 % is encoding overhead, not lost content |
| A-5, B-6, B-11 | Q1, Q3 | Two required kernel fields carry little in the shipped catalogues: modality is `unspecified` on all but one ISM statement and on every CSF statement; the obligated party is one converter-written constant in three of four catalogues. | measured twice. | Yes, in the coverage reports. | survives |
| A-7 | Q1 | The tagline rests on ten security catalogues and one example system, in English and German. | quoted: spec:197-228, 940-945. | Limits yes; tagline unqualified. | not checked |
| A-8 | Q1, Q2 | Every shipped id sits in an authority's namespace and was minted by this project's converters. If an authority publishes its own ids, every Mapping, Tailoring and Attestation has to be re-pointed. | measured. | Yes (manifest notes). | not checked |
| A-9, E-15 | Q1 | The "weekend validator" was measured by its author at 157 vectors and 994 lines. The reference now has 3,144 counted lines and 705 vectors; the three ports share one author. | measured; quoted `drafts/gate-4-measurement.md:72-82`. | Yes for independence; the size only in spec IV.1. | survives |
| A-11 | Q1 | Front-door numbers are stale in both directions: ≈30×, ISM −29 % (now +0.8 % to +25.7 %), GS++ −50 %, four rows of the corpus table, "22 decisions", "nine kernel objects", "value tracing on one corpus" (six ledgers exist), "backlog empty", 5,886 round-tripped objects (4,198 reproducible). A superseded export file ships beside the current one (`converted_examples/DE.BSI/oscal-export/geman.bsi-catalog.json`). | measured twice. | Partly. | survives, corr. |
| I-2 | Q2, Q1 | Handbook chapter 15 describes, in the present tense and without an evidence label, a Foundation that operates a registry and a facet "NIST owns and maintains". Neither exists. | quoted: ch15:92, 115, 121. | No; the chapter breaks the book's own labelling rule (ch01:294-298). | survives |
| I-10 | Q2 (L4) | The licence judgements on the converted content hold today. The bundles derived from CIS material, whose terms forbid derivative works and re-posting, were removed from the tree and remain in the public history (1,245 files), as do four bundles removed for lack of a licence. spec:2491-2494 says merging "stopped their publication". | measured (git); CIS licence fetched 2026-11-14. Legal weight not judged. | Decided and recorded (register:2259). | survives |
| I-9 | Q2 (L4) | Apache-2.0 is adequate for use. There is no IPR policy for contributions, the trademark screen is open, and the rights in AI-written text are not addressed. | quoted: spec:956-957; argued. | Partly. | not checked |
| I-13, I-14 | Q2 | `PRIOR-ART.md` compares ten features the project chose and leaves out installed base, tools, recognition and governance, where every neighbour leads; missing neighbours include the CSA CCM machine-readable bundle, regulator formats and the OSCAL toolchain the specification measures itself against. | online, partly through search summaries. | F.10 says the features were chosen by the project. | not checked |
| B-3, B-4, B-5 | Q3 | Mechanisms specified and unused: `conditional-apply` (no bundle can carry an instance, yet listed as required at the Portable tier and under "Gate 4 — done"); six of eight tailoring operations; `canonical-alias`; the XML projection, whose "guaranteed strict XSD" does not exist and which the kernel schema's own constructs contradict. | measured twice. | Partly (appendix-b:238-239). | survives, corr.: the three predicates do have a carrier, with no use |
| B-10 | Q2, Q3 | While the kernel grew by Risk and Check, the records an enterprise deployment asks for first stayed strings: party, organisation, scope, an identified exception, retention. | measured (grep); section 4.4. | Partly. | not checked |
| E-8, C-3, C-8, C-9, D1-20, D2-21, D1-5 | Q4 | The documents contradict each other and the schema: eight shape disagreements (8 of 8 confirmed), five chapter examples that do not validate (5 of 5), a responsibility example that contradicts the text, stale counts in three places. | quoted, each line confirmed. | No. | survives |
| E-4, E-5 | Q1 | The vector files have no format description (seven layouts for six families); the canonical-form family carries no digest values, and nothing in the six families tests the package digest. | measured. | No. | not checked |
| E-9, E-14 | Q4 | The specification is a decision register with amendments: about 2,700 lines read for 573 lines of code. Outside the subset, a hand-written pattern matcher, Ed25519 and Unicode data need engineering or a dependency. | measured / quoted. | Partly. | not checked |
| C-17, D1-28, D2-25 | Q4 | Hand authoring needs a program for digests and manifest on every edit; objects carry no type, so every consumer starts with a classifier. | demonstrated. | Partly. | not checked |
| D1-6, D2-5, D1-7 | Q4 | Inheritance stops at the clause and does not say which part is inherited; the absence of an edge means nothing. | demonstrated on both bundles. | Partly. | not checked |
| D2-2 | Q4 | After a Tailoring raises a clause to `must`, the resolved clause's prose still says "KANN"; which governs is not stated. | demonstrated. | No. | not checked |
| D1-17, D2-15, D1-18 | Q4, Q2 | A review period on a calendar that is not in the bundle cannot be turned into a date; the 24-hour validity of a check is reported by nothing. | demonstrated. | Yes. | not checked |
| G-14 (gaps) | Q2 | No Content-Security-Policy on the app's pages or the reader; the reader loads Google Fonts while telling the user nothing is uploaded; a link can fill an empty set. | quoted. | Partly. | survives, corr.: the pack builder has a policy |

### 6.4 Positive findings the verdicts rest on

| Id | Q | Statement | Evidence (kind) | Check |
|---|---|---|---|---|
| A-1, C12 | Q1 | The executable claims re-run true: 705 of 705 checks, every shipped bundle with both digests, and four catalogue conversions byte-identical from pinned sources. | measured three times (orchestrator, lens A, checker 2). | survives |
| B-8 | Q3 | The core of statements, sets, identity, facets and manifest is not overdesigned: 45 field paths carry 4,198 real objects, and removing any part loses measured content. | measured. | not checked separately |
| B-9 | Q3 | Like for like the schema is about two fifths of OSCAL's in definitions and a third in property slots, and about half per use case. | measured twice. | survives, corr. |
| A-13 | Q1 | Sets replace the ISM's hand-maintained applicability matrix and the SP 800-53B profiles. | measured. | not checked |
| D1-1, D2-20, D2-1, F-17 | Q4, Q1 | Two cold readers reproduced both digests on 40 of 40 objects at the first attempt and resolved a Tailoring from the handbook alone; lens F wrote valid bundles from the documentation in about 90 lines. | demonstrated three times. | consistent across three reviewers |
| C-19, E-1, E-10, E-11 | Q4, Q1 | Ten of twelve building runs of the cold author passed at once; the cold implementer reached 154 of 173 on the first run; modality, the number domain, key ordering and the pattern dialect are stated completely. | measured. | E-2's check confirms the split |
| H-1, D1-18, D2-16 | Q2 | A machine check run is re-performable by a second party: the observation is in the record, the verdict is recomputed, the evidence is bound by digest. Limit, declared: no runner exists and the example ran against a stub. | measured by three reviewers. | consistent |
| H-7, H-9 | Q2 | Risk holds what ISO/IEC 27001 6.1.2 and 6.1.3 and BSI 200-3 ask of a register row; a consumer Tailoring with `risk-coverage` works as a Statement of Applicability as data. Limits: no expiry, approver need not be owner, no scope, no rendering. | demonstrated; the regimes' requirements from secondary sources. | not checked |
| H-14 | Q2 | The tools say what they did not prove (UNVERIFIED, UNPROVEN, withheld, not evaluated). The blocks in 6.1 are where this habit stops short of the exit code. | measured. | consistent with checks 1 and 5 |
| G-11, G-13, G-14 | Q2 | The pattern engine for Check criteria is bounded; well-formed attempts to carry more than advice in a pack are refused; 106 script and markup payloads in a hostile bundle executed nothing in the app or the reader; model-service keys are kept in memory and sent in a header only. | measured / demonstrated. | survives (sources read, browser run not repeated) |
| F-1, F-16 | Q2 | The reference validates about 170,000 objects, the shape of 8,000 systems, in 4.4 to 11 minutes with 0.7 to 1.2 GB, roughly linear at 1.5 to 2.5 ms per object. The enterprise shape fits the eleven types. | measured (`<scratch>/F/scale-results.tsv`); table in section 3.5. | survives for the three points re-timed (17,310, 22,771 and 45,731 objects, peak memory equal to the megabyte); the 170,000-object runs were not repeated |
| I-7 | Q2 | What an adopter holds keeps working if the project stops: the validators need no network, ids are never fetched, the licence allows a fork. | measured (no network call in the validators). | not checked |
| I-12 | Q2 | `PRIOR-ART.md` states the neighbours' current versions correctly, and its feature table was right on the sampled cells. | online, 2026-11-14. | survives (one cell arguable) |

### 6.5 Notes

A-10, A-12, A-15 · B-7 · C-10, C-12, C-14, C-15, C-16, C-18, C-20, C-21, C-22 ·
D1-4, D1-8, D1-14, D1-16, D1-19, D1-22, D1-26, D1-27, D1-29, D1-30 · D2-4,
D2-6, D2-9, D2-11, D2-14, D2-17, D2-18, D2-24, D2-26 to D2-31 · E-12 · F-15,
F-18 · G-16 · H-16 · I-15. These are recorded in the reviewers' reports and
ledgers under `<scratch>/`; none changes an answer. Two are worth a line here:
ids are arbitrary strings, so look-alike ids (Unicode normalisation twins,
invisible characters) pass (G-16); and a calendar-period parameter's
declaration carries `num` and `unit`, which reads like a bound value (D2-29).

### 6.6 Withdrawn or corrected

| Id | What was claimed | What the check found |
|---|---|---|
| B-3 (part) | The three predicates have no carrier in any bundle. | **Withdrawn.** `Tailoring.selects[].predicate` carries them (schema; appendix-b:414-417). No shipped object uses it. The claim stands for `conditional-apply`. |
| A-4 (number) | 70.7 % of value bytes sit in facets. | **Corrected** to 64.0 % of leaf bytes and 43.9 % of values; lens A had counted keys and punctuation for facets only. |
| B-9 (number) | 45 schema definitions. | **Corrected** to 59; the walker had left out the root definitions. |
| B-1 (meaning) | The 2.0.0 additions are used by 8 converted objects, so they are not needed. | **Meaning withdrawn, number kept.** The 1.0.0 lifecycle types fare no better on the shipped corpus. |
| G-5 (part) | A vendor's key verifies an Attestation in the agency's name. | **Narrowed.** Only when the key file lists one key for both parties, as the fixture file does. |
| G-10 (number) | 17.1 s at 28 characters. | **Corrected** to about 8.5 s wall, 6.5 s over baseline, on the checker's run; the growth rate stands. |
| G-12 (detail) | The dry run answers `import` for a stale pack. | **Corrected:** against the example folder it answers `already-imported`; against a set without the pack, `import`. |
| G-14 (part) | No Content-Security-Policy on any page. | **Corrected:** the pack builder has one. |
| H-3 (severity) | A malformed Attestation is skipped silently. | **Raised:** the skip removes an existing failure. |
| C-4 (scope) | Shape errors are reported against the wrong type. | **Narrowed** to nested errors. |
| D1-3 (detail) | The handbook calls the example Tailoring a consumer's. | **Corrected:** it does not say so literally; the ambiguity of the tier rule stands. |
| I-1 (part) | No contribution guidance anywhere. | **Corrected:** the website sources hold a section on it. |
| F-11 (number) | The 1.0.0 example folder fails 8 times under rc.4. | **Corrected** to 2; six were line-ending artefacts of the checkout. |
| F-13 (part) | The only lifecycle import is the IFA converter. | **Narrowed:** the pack builder imports component definitions generically. |
| F-7 (part) | Nothing marks a trimmed bundle. | **Corrected:** the verdict changes to Semantic Match; the mark does not distinguish trimming from repackaging. |
| F-6 (part) | Chapter 15 claims the format as "source of truth" against Appendix F. | **Weakened:** chapter 15 speaks of the direction relative to OSCAL. |
| A, G (reports) | Lenses A and G named a `report.md` in their scratch folders. | The files were never written; both reviewers resent their findings as text, which is what this report uses. |
| Orchestrator | "121 commits ahead of `main`" (status note during the run). | **Corrected** to 164; the first count came from a shallow checkout. |
## 7. What was not examined, and what could not be run

**Could not be run here**

- The PowerShell twin (`validate_core.ps1`): PowerShell is not installed. All
  statements about it are quoted from CI or from its source.
- The 1.0.0 measurements (157 vectors, 6,914 objects, 994 and 1,163 lines, the
  ≈30× comparison): there is no 1.0.0 tag, and six of eleven bundles are not
  in the tree. Lens F re-ran the 1.0.0 bundles from commit 0b949fa3 under the
  rc.4 validator; the 1.0.0 validator itself was not re-run.
- The IFA and CR26 conversions were not re-run here (CI runs them).
- compliance-trestle's 30,905 lines were quoted, not recounted.

**Hosts that could not be reached** from the session: `fedramp.gov`,
`csrc.nist.gov`, `nvlpubs.nist.gov`, `bsi.bund.de`, `eba.europa.eu`,
`eur-lex.europa.eu`, `cisecurity.org`, `jascon.net`. Consequences:

- What ISO/IEC 27001, 27006, 17021-1, 19011, ISAE 3000, AT-C 205, the C5
  catalogue, BSI 200-3, the IIA standards, DORA and eIDAS prescribe (lens H) is
  confirmed through search results and secondary sources at best, and in three
  places rests on training knowledge. None was read in the standard's own
  text. H-4, H-5, H-6 and H-13 depend on it in their weight, not in what the
  schema holds.
- FedRAMP notice NTC-0009 and the NIST workshop talk are search summaries.
- Whether the project's website is live was not seen.

**Not examined**

- The app's pages in a browser beyond the hostile-bundle run (lens G drove hub,
  ten tool pages and the reader; forms and the pack builder with a loaded
  bundle were not driven). ZIP reading in the app. The `file://` case.
- The converters as an attack surface for hostile source files.
- Ed25519 edge encodings; `--compose` under hostile input.
- GRC products other than ServiceNow; neighbours EUCS/EUCC, GovRAMP, Open-RMF;
  Gemara's constraint layer; trademark registers.
- Scale above 178,000 objects, and bundles heavy in Mappings, Checks with
  evidence or Attestations.
- The decision register (4,256 lines) was searched by keyword by every
  reviewer and read through by none. A ruling under words nobody searched
  could exist; the checkers searched again for each heavy finding.
- Legal questions (ShareAlike boundary, AI authorship, material in git
  history) are stated as facts found, not judged.

**Limits of the method**

- Reviewers, checkers and orchestrator are instances of one model family.
  Independence between them is independence of context, not of kind. Shared
  blind spots are possible; the author's check by other models addresses that.
- Each checker made one attempt at refutation. Findings marked "not checked"
  in section 6 rest on one reviewer.
- The cold experiments measure the documents, not human effort (section 5.1).
  Two breaches of the cold condition are recorded there.
- The reviewers could not write their report files in every case; lenses A, B,
  D1, D2, E, G, H and I returned their reports as messages, which the
  orchestrator kept as ledgers under `<scratch>/`. Lenses C and F wrote
  `report.md` in their folders.
- The scratch directory (about 4 GB, most of it lens F's synthetic bundles)
  is bound to the session. This report is written so that its demonstrated
  findings can be rebuilt without it.
