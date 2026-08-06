# The JASCON Handbook
# Appendix F — Objections and Answers

**Purpose:** the adversarial FAQ. Every question below is phrased the
way an opponent would phrase it — several *were* phrased this way, by
the eight hostile review passes whose verdicts shaped v0.5 — and the
answers cite counts, corpses, and, where the objection landed, the
correction it forced. §F.5 is the section most FAQs don't have: the
punches that connected.

---

## F.1 "Why not X" — the technology objections

**Q1. Why not CEL, Rego, or any real expression language for
constraints? Eight primitives is a toy.**
Because the toy is the point, and the language is the trap — twice
over. First, complexity: a weekend validator cannot embed a policy
engine, and the validator ecology (many cheap implementations, no
monoculture veto) is a governance control, not a nicety. Second,
rationale-rot: the defining pathology of the flagship's constraint
dispute was a rule *nobody could explain*; expression languages make
inexplicable rules cheap to write. The design's own history seals it:
an early draft casually allowed "selection by facet query" and was
caught smuggling an undefined language one decision after banning
languages. Eight primitives, versioned — the ninth ships with counts
and two implementations, never with a grammar.

**Q2. Why not JSON Patch for tailoring? It exists, it's standard.**
Because Patch addresses *positions* and compliance addresses
*identities*. Two independent tailorings of one catalog, one
legitimate re-issue that reorders an array — and every positional
path silently points at the wrong clause. Version-pinning doesn't fix
it (pinned positional patches still rot on re-issue; the register
records this rejected alternative verbatim). Identity addressing
(`requirement-ref` + `statement-id`) survives reordering by
construction, and the same-target-twice error makes conflicts loud
instead of last-wins quiet.

**Q3. Why abandon XML and Metaschema? Half of government runs on
XML.**
Abandon is the wrong verb; *fence* is the right one. The census
answer first: the authorities themselves author in JSON and bespoke
JSON — the American program's current rules are not OSCAL XML, they
are a custom JSON file. The kernel therefore has one authoring
serialization, and XML becomes a **one-way transit projection** with
a guaranteed strict XSD for the kernel+stdlib subset (D18) — XML
consumers keep validation, XML pipelines keep working, and nobody
maintains dual authoring truth (the corpse: every dual-format
ecosystem's drift). Metaschema dies for the complexity-budget reason:
a meta-language that generates three bindings is infrastructure spend
the census showed nobody's *semantics* ever needed.

**Q4. Why exactly one serialization? YAML is friendlier.**
Because digests. Semantic integrity rests on canonical bytes (JCS),
and every additional authoring format is another canonicalization
seam — the empty-omission and float rules were hard enough to pin
for *one* format (the conformance vectors exist because reviewers
found real fragmentation cases). YAML remains fine as a local
authoring convenience that *compiles* to the JSON — what it can't be
is a second truth.

**Q5. Why not fix 1.x profiles instead of replacing merge?**
Merge strategies exist to arbitrate identity collisions; global
identity makes the collisions unconstructible; a fix for an
impossible problem is dead code with a specification. The measured
history: merge/keep/combine semantics generated a dispute class and
implementation divergence for a decade. Legacy profiles that
genuinely depended on merge get §14.2's honest instruction — resolve
in the old world, migrate the result.

**Q6. Why not RDF/OWL — this is obviously a knowledge graph?**
It is a graph; it is not a *Semantic Web deliverable*, and the
difference is the complexity budget's whole thesis. The failure mode
this architecture answers is not "insufficient ontological
expressiveness" — it is 22,000 annotation props and three national
authorities routing around a standard that spent its budget on
infrastructure. Nine shallow types with typed edges give the graph;
JSON Schema gives the weekend validator; a triple store gives
neither. Anyone who wants RDF can project it — losslessly, from a
model this simple.

## F.2 "You went too far" — the architecture objections

**Q7. Nine types is arbitrary. Why not one generic node with typed
properties?**
Because "one generic node with typed properties" is the 1.x prop
system with better marketing — the exact architecture whose measured
cost opened the book. The nine types are not invented; they are the
convergence table's output: the shapes three governments
independently built. Fewer types pushes semantics back into
string-keyed soup; more types failed the census test (no third
authority needed them).

**Q8. A Core tier that computes *nothing* is useless.**
It is the most load-bearing tier in the design, and it exists because
a reviewer proved the alternative broken: a Core allowed to "partially
understand" semantics has a silent-ignore state — the tool that
validates a bundle while skipping the facet that changes its meaning.
v0.5's answer (P7-B3, accepted): Core is *passive* — validate,
digest, resolve, **preserve** — and every semantic computation begins
at Portable, behind the capability gate. Useless is what the old
world's "conformant" was; passive is honest.

**Q9. Two digests is crypto-overengineering.**
One digest forces a choice between two lies: bind bytes (and every
legitimate re-serialization or annotation-strip breaks signatures) or
bind some ad-hoc "meaning" (and tampering hides in the gap). The
Rev4-era answer was hash-plumbing props nobody could verify across
tools. Two digests, two jobs: the package digest answers "are these
the bytes," the semantic digest answers "is this the approved
meaning" — and bi-modal verification (Full/Semantic Match) is the
verdict shape auditors actually need. The cost is one extra SHA-256
per object; the converters paid it 3,066 times without noticing.

**Q10. Fail-closed will drive users to fork or lie.**
It would — if it fired at the noun. It fires at the *verb*: a bundle
full of unknown selection facets opens, validates, forwards, and
displays; it halts at the moment someone selects, with a three-part
message naming the blocker and the doors. The alternative is on the
record: three real tools, one preserving, one guessing, one
refusing, all "conformant." A warning-then-proceed is the guessing
tool with a seatbelt sticker. Forks come from *unpredictable* stops;
gate-at-the-verb plus printed rationale is the anti-fork design.

**Q11. Global URIs — so you've centralized naming. And URIs rot.**
Neither. Nothing resolves: identifiers are compared as strings,
never dereferenced (D2), so sealed environments and dead domains
change no verdict. Nobody grants prefixes: authorities mint under
names they already control, and the transparency log remembers
without gatekeeping. Rot is handled where it actually occurs — as an
identity *event*, with `canonical-alias` carrying the forwarding
address the old world never had. The corpse on this grave is the
registry that vanished with its repository.

**Q12. `may-only` is a Germanism the world doesn't need.**
The gate measured it: DARF NUR ×0 in the current German corpus — the
lattice anticipates it, nobody has used it yet, and this appendix
says so out loud. It stays because it is lattice-clean, costs one
code, and encodes a real regulatory move (exclusive permission) that
prose otherwise smuggles. If the corpus never votes for it, the
versioned code system has a removal path — that is what "closed but
versioned" is *for*.

## F.3 "You didn't go far enough" — the scope objections

**Q13. Where's the process/workflow model? Compliance is workflows.**
Declared non-goal (D17), with a corpse: the one process-flow
structure in the census (`flows[]`, ×1) is a *diagram*, and diagrams
are linked resources, not requirement data. The state machines the
model does own — Deviation, Finding — are the ones three authorities
encode as data. BPM engines exist; this is their input, not their
competitor.

**Q14. Where's risk modeling — likelihood, impact, scoring?**
In facets, where legitimate methodological diversity belongs.
`security-objectives@1` carries the ratings authorities actually
ship (measured: C/I/A/Auth ×4,494); scoring *methodologies* differ
by framework and by fashion, which is the exact profile of a facet
and the exact anti-profile of a kernel field. `privacy-assessment@1`
is parked for the same discipline: no facet designed from memory.

**Q15. Statements without mandatory grammar are just prose with
extra steps.**
The German corpus answers in both directions. With grammar: 1,006
machine-decomposed clauses, QA-checkable, defect-findable (the 216
and the 9 were found *because* grammar is data). Without: ISM's
1,149 declarative statements convert at Core tier with zero facets
and zero loss. Mandatory grammar would have made the second corpus a
second-class citizen — R2 accepts the bifurcation because the
alternative excludes half the world's authoring cultures.

**Q16. One reference hop can't express real inheritance chains.**
The objection (H4, on the record) was answered by *moving the rule*,
not denying the need: the boundary rule is edge-local and inductive —
each inheritance edge names its basis, each link verifies its link —
so chains of any depth check with one hop per step. Multi-hop
*expressions* stay banned; multi-hop *chains* work fine. The SaaS→
PaaS→IaaS walk in Chapter 9 is the constructive proof.

## F.4 The political objections

**Q17. NIST will never bless its own demotion.**
The arrangement demotes nothing NIST earned and everything the
structure imposed. 800-53's content keeps default primacy — shipped
in every stdlib bundle, first among equals — as the **Canonical
Reference Facet NIST owns**. What ends is one framework's document
conventions constraining every other framework's documents, whose
measured cost was a national catalog flattened into props. "Standard
library, not constitution" is a *promotion* to the role the content
actually plays; the optics risk is in the register (R5), not denied.

**Q18. Publishing this Osbornes the 1.x adoption wave.**
Which is why the name avoids "2.0," the posture is *engine*
(kernel-authoritative, valid 1.x generated for every regulator that
asks), and the dual window ends at a declared, measurable sunset
trigger rather than an announcement. The deadline wave is real and
useful; freezing it would be strategic self-harm, and D19 exists to
not commit it.

**Q19. The five-provider clause is a cute loophole, not a strategy.**
It is recorded without endorsement because it needs none: it is the
incumbent policy's *own* mechanism, and it swings both ways — the
door through which a format like this becomes approved without
permission, and equally the door through which something worse
replaces the incumbent if its second act disappoints. Quoting a
published rule is not a gimmick; it is reading the terrain.

**Q20. You have zero users and a hypothesis.**
Correct, and the specification says so on its cover — "well-supported
architecture hypothesis," claims narrowed to evidence tier, with the
v0.6 gate defining exactly what execution must prove. What exists is
not users but *user-shaped data*: three governments' complete corpora
at 100 % declared coverage — 92,886 values across the three current
census bundles (the oft-cited 93,259 was the pre-MS-TLS-drop census
total; the eight-corpus total is 130,350) — and every design decision
traceable to something an authority shipped. That is more empirical
grounding than most 1.0s carry; it is still a hypothesis, and the
gate is where hypotheses go to become claims or die.

**Q21. The compat facet is just props with a registration number.**
It is exactly that *if the clock stops* — which is why the clock is
the contract: intended deprecation in the descriptor, residue as a
per-release KPI, and every current row with a named exit (ISM 539 →
narrative decision; BSI 179 → the D9 default question; CR26 29+5 →
the D13 ceremony question; CTL 79 → gate-3 catalog resolution). A
waiting room with a clock and exits is a migration tool; the same
room without them is the smell §14.6 names.

## F.5 The punches that landed — objections that changed the text

The credibility section. **"Your weakening rule is a slogan"**
(P7-B2): correct — "weakening ⇒ Deviation" was only enforced for
modality; v0.5 replaced it with per-operation laws. **"Core can't do
JCS and be minimal"** (P8-E1): correct — `attestation-binds` moved
to Portable; Core went fully passive. **"Lossless is unprovable and
your export claim is false"** (P6): correct — three guarantee levels
and a published equivalence relation replaced both adjectives.
**"Your canonicalization fragments on empty arrays"**: correct —
empty-omission became a normative rule with test vectors.
**"651 controls"**: wrong by 347 — the nested-control recount and
the public erratum. And this very week, our own converter's **"51
unit-class crossings"** dissolved under a refined counter into 0
true crossings and 51 base-absent variants — Appendices A and C
corrected on the record. The pattern is the point: this project's
answer to a good objection is a diff, and its answer to a bad one is
a count. To file yours: Chapter 15's door — bring corpus cases,
bring numbers, expect both in return.

---

## F.6 First external-review round — objections that arrived after the manuscript closed

*The first human review of the complete manuscript produced two
objections within a day. Both partially landed; per F.5 house rules,
the diffs are on the record (Ch. 6.A; the v0.6 backlog).*

**Q22. I expected more first-class fields — force/modal-verb got
promoted to the kernel, so why not security objectives, evidence
duties, assurance levels?**
Because promotion has a price and therefore had a bar — implicit
until this question forced it into words: a semantic goes kernel when
**at least two of three authorities encode it independently**, there
is **one shared computation** every generic tool must perform on it,
and **one vocabulary fits all corpora without flattening**. Modality
passes all three (three encodings counting ISM's honest structural
absence; monotonicity as the computation; one lattice). The expected
candidates fail measurably: security objectives are 1-of-3, and even
the one corpus's values ("1"/"0") share no scale with anyone;
evidence duties are 2-of-3 with irreconcilable shapes (free-text
document names vs. per-class artifact lists vs. KSI tests); and
assurance *levels* — genuinely 3-of-3 — are the instructive case,
because their kernel *mechanism* already exists: **membership**.
Level-as-a-field is the 5,301-marker corpse; level-as-a-Set composes,
while the incommensurable vocabularies stay in `assurance-levels@1`.
The second half of the answer: stdlib facets *are* first-class
ecosystem citizens — default-shipped, schema-pinned, fail-closed —
and a kernel field is a tax on every Core validator forever. **What
landed:** the promotion rule was nowhere normative. It is now a v0.6
backlog item, and this entry is its first public statement. *(Decided
2026-07-21: normative as spec D22 — backlog #4 closed.)*

**Q23. In 1.x I amend a catalog — add controls, possibly nested — via
profile and resolution. Where did that go?**
The verb split in two, and the handbook had only documented one half.
*Modifying* upstream content is Tailoring, under Chapter 6's
operation laws. *Adding* content is **authorship**: new Requirements
under your own prefix, composed with the upstream via a **shadow
set** (interleaved `sequence`, multi-authority membership), with
clause-level attachment by reference — a minted `supplements`
relation or a statement-scoped Mapping — never by injection, because
foreign statements live inside the owner's object and digest. What
resolution used to *produce*, the shadow Set *is*: explicit
references instead of merge provenance. The corpse: resolved
artifacts whose lineage was a tool run, and the twin-catalog's ten
silent divergences — forking-to-amend at any scale. **What landed:**
the supplement pattern was genuinely missing from the book. It is now
§6.A, a glossary entry, and a backlog item to give the pattern a
normative name in the specification. *(Decided 2026-07-21: named in spec
D21; `supplements` registered as a stdlib relationship extension code,
D20/C.5 — backlog #5 closed.)*

---

**Field addendum (2026-07-20) — the first punch from the field.** Hours
after the CR26 findings went to the FedRAMP community (discussion
#153), the program's director replied personally: the "nine undeclared
subsets" were a structural misunderstanding on our side — framework-
specific subsets are declared in `info.20x.subsets` /
`info.rev5.subsets`, exactly as the repository's own AGENTS.md
instructs ("global by default, specific when needed"), an instruction
our post had cited without following. Verified by re-run: zero
undeclared; all nine carry full names, descriptions, and
applicability. The diff shipped the same day — the converter now reads
the framework-specific declarations, which *improved* the bundle
(real titles and scope facets on the track Sets, class Sets enriched
by their declared applicability) — and the withdrawn finding, the
downgraded statistics, and the correction are on the public record in
the thread. The house rule survived first contact with the field:
the answer to a good objection is a diff — including when the
objection comes from the director of the program you measured.

## F.7 Second external-review round — the deep-research pass (2026-07-21)

A full-repository deep-research review (on the record as
`DEEP_RESEARCH_REVIEW.md` at the repo root, eleven dimensions) arrived
the same day gate item 2 shipped. Adjudicated the standing way — every
punch that lands becomes a diff, every miss gets a count:

**Landed (four items).** (1) `calendar-period`'s fail-closed rule is
correct but *lonely*: no shared calendar registry exists — the CR26
converter minted `us-federal` ad hoc on 16 objects → backlog #13, a
stdlib `calendar-context` code system. (2) `canonical-alias` asserts
same-content and same-content is *checkable* (semantic digests
compared modulo the identity fields), yet nothing required the check
→ backlog #14, the rebrand claim becomes self-policing. (3)
Down-conversion to OSCAL 1.2.2 was designed-for, unmeasured → folded
into the gate-4 scope as a mechanical export test suite. (4) Template
pins make render-tampering detectable, but nobody *accredits*
templates → backlog #15, ch15 names an owner or an explicit non-goal.

**Refuted by measurement (one claim pair).** The review's Dimension 8
asserts a "50–70 % payload reduction" and "~60 % fewer LLM tokens."
Neither number appears in this project's evidence, and the size claim
was measured false the same evening: ISM source 2,545,493 B → bundle
objects 1,808,397 B (−29 %); GS++ 5,389,844 B → 2,694,940 B (−50 %);
CR26 567,435 B → 877,640 B (**+55 %** — bespoke JSON becomes 760
objects each carrying identity boilerplate). What this project claims,
measured: >70 % of legacy prop *instances* are structurally dead.
Byte size is mixed by construction; token counts are unmeasured.
Neither Dimension-8 figure may be quoted as a project claim — the
erratum culture applies to flattering numbers most of all.

**Already overtaken at arrival.** The review listed the executable
schemas and backlog #6 as pending; both had shipped hours earlier
(gate item 2). Timing artifact, not error.

## F.8 Third round — the P9 twin adversarial runs (2026-07-21)

The project's own P9 prompt (`drafts/oscal-semantic-core-p9-review-prompt.md`)
ran twice, independently — run 1 fresh, run 2 with disclosed limitations
and a concordance section. Two runs of one prompt make agreements
replication evidence; both were adjudicated same-day, their reports
since consolidated into the v0.6 backlog. The joint verdict, in their
own words: *the executable layer
currently proves less than the prose says it proves; none of it is
architectural; every item has a named corpse and a countable fix.*

**Fixed in the P9 cycle (same day):**
canonicalization moved to RFC 8785 UTF-16 member ordering in validator,
converter lib, and both legacy converters — with a regression vector;
digests re-pinned (ASCII keys made old and new orders coincide, so only
code changed, not shipped digests) [P9b-3, which overturned run 1's
"attack surface 10 — no finding"]. Validator gains `unique-within`
(duplicate statement ids; duplicate object ids — the twin-catalog corpse)
and Set-member closure (14,508/14,508 close) [P9b-2, P9b-1 corner].
Schema gains the four missing operation conditionals and the set-field
whitelist as an enum; spec D13 table gains its two missing rows
[P9b-2/P9b-5]. CR26 bundle re-pinned with the promoted declarations
[P9b-9]. B.3's detach corpse re-named to assessment-criteria
[P9b-8 — the D.12 audit's `[]` for grammar stands]. The erratum sweep
landed: register arity three→four with the folding made explicit
[P9-0/P9b-14], 5,470-vs-5,478 decomposition [P9-6/P9b-12], 216→213
census/corpus split, 93,259→92,886, twenty-one→twenty-two, ch01's
"days" labeled designed-for [P9-7], B.1.1's closure claim re-scoped,
IV.5.2's orphaned parked items re-parked, and the deep-research file
now opens with its own erratum banner [P9b-13]. Bonus find by the
triage itself: `bsi-coverage-report.json` had been written in cp1252
(a Windows default-encoding bug in three converters) — fixed, rerun.

**Entered the backlog with counts:** #16 reference taxonomy [P9b-1 —
the round's Blocker: B.1.1's normative text condemned the shipped
corpus], #17 facet-payload validation + unregistered-facet fail-closed
[run 1's Blocker P9-1: the valid-and-meaningless rebirth demonstration],
#18 conformance expansion + the missing DSSE profile [P9-2 + P9b-7],
#19 tailoring tier anchor [P9b-6], #20 relations coherence incl. C.8
`supersedes` vs. the D2 split [P9b-4], #21 Set addressing [P9b-5
remainder], #22 D22 demotion vs. closed shapes [P9b-10], #23
nearest-Set tiebreak [P9b-11].

**Adjudicated against the reviews:** run 1's P9-5 re-raises adjudicated
backlog #13 with no new evidence — a priority statement, not a finding
(run 2's concordance says the same). Run 2's P9b-5 sub-claim that
`override` "appears in no spec/handbook text" is wrong — Appendix A.3
documents it ("chaining only via explicit `override`"); the row stands
for the D13-side gap only. Run 1's P9-3 ("model held without kernel
changes" overstated) is accepted with one correction: the D9-rev
label/default decision predates the validation conversions and was
evidenced by the census corpus (BSI ×179), not forced by the validation
targets — the README line now says exactly that.

The pattern across three rounds holds: the punches that land get diffs
the same day, the misses get counts, and each round's sharpest finding
came from running code against the repo — which is the whole thesis,
applied to the thesis.
