# The JASCON Handbook
## Part Two — Authoring Content
# Chapter 4 — Writing Requirements: Statements, Modality, Parameters

**Audience:** framework authorities [A]. Assessors and tool builders will
profit from §4.2 (the lattice) and §4.6 (why prose can no longer lie).
**Companions:** Specification v0.5 — D9, D13 (author-facing parts),
Appendix A; stdlib code systems (Appendix C of this book, when it lands).

---

## 4.0 The task

On your desk is one real requirement — say the German KONF.14.1,
"Verschlüsselung beim Transport" — currently existing as a paragraph of
prose plus seven namespace-qualified props. Your job is to re-author it
as a JASCON Requirement, and doing that means answering, in order,
the only four questions statement authoring ever asks:

**How many statements?** — one clause or several. **Which modality?** —
and what that choice permits downstream. **Who is bound?** — parties,
plural, versus the thing acted upon. **What is a parameter, and what
stays prose?** — including the special honesty rules for deadlines.

This chapter is those four questions, each introduced by the corpus
artifact that forced the answer, ending with the finished object. Along
the way, the census's ugliest defect class — the 216 silent
pseudo-placeholders — becomes literally unwritable, which is the whole
point of the machinery.

## 4.1 One clause or several? The 347-control lesson

The statements field is a *list*, and the reason is a number: the German
catalog contains **347 nested pseudo-controls** (plus 10 more in its TLS
sibling) — controls inside controls, most of them one sentence long. The
authors were not confused; they needed independently addressable
*clauses* — a piece of a requirement you can tailor by itself, assign to
a different party, map to a different foreign control — and the old model
offered no unit between "whole control" and "undifferentiated prose." So
they minted fake controls. The American corpus tells the same story in
its own accent: statements that vary by certification class, and
`following_information` bullet lists that are really enumerable
sub-obligations. Meanwhile the Australians write one statement per
control, 1,150 times, and that is *also* correct — for their content.

So the craft question is real: when does one requirement carry several
statements? The heuristic that survived the corpus:

> **Split into separate statements when clauses differ in modality, in
> obligated parties, in parameters, or need independent tailoring,
> assessment, or mapping. Do not split for mere enumeration** — a list of
> examples or sub-items with one shared obligation is a GFM list inside
> one statement's prose.

Each statement gets an `id` — short and permanently stable (`s1`, or
semantic letters `a`, `b`). Stability is not cosmetic: tailoring
operations, per-clause implementations, and statement-scoped mappings all
address `requirement-ref + statement-id`, and the resolution algorithm
fails closed when an address vanishes.

> **Don't** renumber or recycle statement ids between versions. Every
> identity-addressed operation downstream — the mechanism that replaced
> position-fragile patching — depends on them; a renumbered clause is a
> broken address in every tailoring that ever cited it. Splitting a
> clause is a *revision* (Chapter 3's `replaces` discipline applies at
> statement granularity too: keep the old id on the closest survivor, or
> retire the requirement properly).

## 4.2 The modality lattice as a decision aid

Every statement declares its binding force from a closed code system —
and, for the first time in this domain, the codes come with a **normative
partial order** that machines evaluate:

```
      obligation axis                 prohibition axis

           must                          must-not
            │                               │
          should                        should-not
            │                               │
           may ──── may-only                │
            └───────────┬───────────────────┘
                   unspecified

  comparable:    only along a drawn line, upward = stronger
  incomparable:  may-only ↔ should/must · any obligation ↔ any prohibition
```

Three census facts make this section practical rather than theoretical.

**The German mapping is exact.** The corpus carries `modal_verb` on every
statement — 1,006 instances — in the BSI Verbindlichkeitssprache:
MUSS → `must`, SOLLTE → `should`, KANN → `may`, DARF NICHT → `must-not`,
SOLLTE NICHT → `should-not`. And **DARF NUR → `may-only`**, the code this
lattice exists to finally honor: a permission *with exclusivity* — "may
do X only under condition Y" — which is stronger than plain permission
(hence `may < may-only`) yet not an obligation at all (hence incomparable
with `should` and `must`). German normative drafting has distinguished
these for decades; this is the first encoding a validator can check.

**The American distribution is your health chart.** CR26's `force` field,
across 328 occurrences: **MUST 189 · SHOULD 84 · MAY 39 · MUST NOT 11 ·
SHOULD NOT 5.** Read it as editorial guidance: prohibitions are rare and
precious (5 % of the corpus); a healthy framework keeps real room in
`should` and `may` — a catalog that is wall-to-wall MUST is usually a
framework that doesn't trust its own tailoring layer and will be
"tailored" in spreadsheets instead.

**Your choice sets the downstream rules.** Whatever you declare, the
`modality-monotonic` rule lets tailorings *strengthen* freely (any move
upward along a drawn line — `should → must`, `may → may-only`) and
requires an audited **Deviation** for anything else: weakening, axis
reversals (`may → must-not` is not a strengthening, it is a semantic
about-face), and every incomparable move. You are not just labeling a
sentence; you are defining the free space of every baseline built on it.

`unspecified` is the honest code for narrative content — outcome-style
frameworks (CSF, ISO management clauses) publish prose-only statements at
Core tier and lose nothing they had.

> **Don't** leave binding force in prose alone. Measured: 1,006 German
> modality props and an entire Australian corpus where force lives only
> in sentence style — unqueryable, untailorable, and, until this lattice,
> governed by folklore about which changes count as "weaker."

## 4.3 Who is bound — parties, plural, versus targets

Two concepts hide inside the everyday question "who does this apply to,"
and the census forced the specification to keep them apart.

**`obligated-parties[]`** answers *who must act* — and it is an array
because reality is: the American corpus binds rules to combinations of
Providers, Agencies, Assessors, Advisors, and the program itself via its
`affects[]` field. Shared responsibility is the bedrock of cloud
compliance; a requirement binding provider *and* customer is one
statement with two party refs, not two duplicated requirements. (An
earlier specification draft made this field a scalar and was corrected
against its own census table — a useful reminder that the corpus, not
elegance, is the referee.) Mint your parties as small identified objects
under your prefix — `…/party/betreiber`, `…/party/provider` — and
reference them; per-clause responsibility splitting on the
implementation side (Chapter 9) depends on these refs.

**The target of the action is a different thing.** The German corpus
carries `target_object_categories` on 623 statements — *Anwendungen*,
*IT-Systeme* — the object acted *upon*, not the actor obligated. That
concept belongs to the statement-grammar facet (Chapter 7), alongside
action and object decomposition. Conflate the two and you will either
"obligate" an application or lose the ability to say who actually owes
the work.

## 4.4 Parameters: the algebra, and what stays prose

The German KONF.14.1 taught the specification its parameter lesson by
counterexample. Its old form fused an either/or into one prose string —
"TLS 1.3 (oder TLS 1.2 mit PFS)" — invisible to every machine that might
want to offer the choice, validate a selection, or compare two tailored
baselines. The statement form makes the alternative structural:

```json
"parameters": [ { "name": "transport-crypto", "type": "choice",
    "cardinality": "one",
    "choices": [ {"value": "tls13",     "label": {"de": "TLS 1.3"}},
                 {"value": "tls12-pfs", "label": {"de": "TLS 1.2 mit PFS"}} ] } ]
```

The algebra is deliberately small — scalars `string · integer · decimal
(written as a canonical string, for digest determinism; Chapter 11) ·
boolean · date · datetime · uri · code(codesystem@version)`, and three
containers: `choice{cardinality, choices[]}`, `list<scalar>`,
`range<scalar>`. The standing escape for anything the algebra cannot
type is a `string` plus a facet — **never** a schema inside a parameter;
that door stays welded shut by design.

The authoring decision rule: **make it a parameter if downstream should
be able to tailor it, assess against it, or compare it across
baselines** — everything else is prose. And when you do make it a
parameter, consider declaring its **tightening direction**
(`tightening: lower | higher | none`): you, the authority, are the only
one who knows whether smaller is stricter (deadlines: `lower`) or larger
is (key lengths: `higher`). The declaration is what lets a downstream
hardening pass without a Deviation while an easing is forced through the
audited channel — governance encoded in one word.

## 4.5 Deadlines: elapsed time versus calendar honesty

The American corpus counts incident-report deadlines in `bizdays`, and
that one unit forced an honesty split the whole industry has been
fudging. "One business day" is not a length of time — it depends on a
jurisdiction's holidays, a working-week definition, a timezone, and a
cutoff hour. Two tools computing a deadline from the same value *will*
disagree unless the calendar is part of the data. So durations come in
two types with different powers:

**`elapsed-duration`** (`seconds | minutes | hours`) — pure physics,
computable everywhere, no context needed.

**`calendar-period`** (`days | bizdays | months | years`, with optional
`calendar-ref`, `timezone`, `cutoff`) — **representable without context,
computable only with it.** A conformant tool asked to do deadline
arithmetic on a calendar-period without a resolvable calendar context
MUST refuse with an explained error rather than guess. If you publish
calendar-periods — and if your framework has reporting deadlines, you
will — the Authority tier (§3.7) obliges you to publish or reference the
calendar that makes them mean one thing.

```json
{ "name": "iir-deadline", "type": "calendar-period",
  "num": 1, "unit": "bizdays",
  "calendar-ref": "https://ns.fedramp.gov/cr26/calendar/us-federal" }
```

> **Don't** ship bare business-day or month deadlines. The failure this
> prevents is silent divergence: two conformant tools, one value, two
> different dates on the compliance clock — with fail-closed refusal as
> the designed alternative to a wrong deadline confidently computed.

## 4.6 Prose that cannot lie

Prose remains where nuance lives — language-tagged CommonMark with GFM
tables, no raw HTML. Two rules keep it honest.

**Tables carry narrative, never data.** A parameter matrix or a RACI
chart rendered as a prose table is unqueryable decoration; the data
belongs in parameters and facets, and the table — if you want one — is a
rendering of them. (The census's grim version of ignoring this: entire
questionnaires flattened into yes/no annotations.)

**Parameter references are bound tokens.** Prose cites parameters as
`{param:transport-crypto}`, and the `prose-params-resolve` rule verifies
every token against a declared parameter of that statement — token
without parameter is a validation error; parameter never referenced is a
lint. This is the mechanism that retires the census's ugliest exhibit.
The old German catalog contained **216 values** like
`{{einem anerkannten Standard}}` — strings *imitating* the standard's
insertion syntax in places where that syntax had no meaning, several of
them contradicting the real parameter the adjacent prose correctly
referenced, all of them invisible to every validator on earth. In the
statement model that entire class is **unwritable**: the only insertion
syntax that exists is checked, and prose that disagrees with its
parameters does not validate. Multilingual authoring falls out for free
— modality and parameters are language-neutral; `prose{de: …, en: …}`
renders MUSS or MUST as display, and the machine-readable truth is
identical in every language.

> **Don't** invent prose-level pseudo-syntax. Measured cost: 216 silent
> defects in one professionally authored national corpus — two
> machine-readable representations of the same requirement, diverging for
> months inside documents every tool certified as flawless.

## 4.7 The four questions, answered: KONF.14.1 finished

```json
{ "id": "https://ns.bsi.bund.de/gspp/req/KONF.14.1",
  "version": "2026-07", "label": "KONF.14.1", "lifecycle": "active",
  "title": "Verschlüsselung beim Transport",
  "statements": [
    { "id": "s1",
      "modality": "may",
      "obligated-parties": ["https://ns.bsi.bund.de/gspp/party/betreiber"],
      "parameters": [ { "name": "transport-crypto", "type": "choice",
          "cardinality": "one",
          "choices": [ {"value": "tls13"}, {"value": "tls12-pfs"} ] } ],
      "prose": { "de": "Konfiguration für Anwendungen KANN Kommunikation beim Transport über Netze nach {param:transport-crypto} verschlüsseln." } } ] }
```

One clause (nothing here differs in modality, party, or tailoring need).
Modality `may` — KANN, honestly, leaving the strengthening to the
security-level tailorings where it belongs. One obligated party, minted
under the authority's prefix; the *Anwendungen* target waits for the
grammar facet. One choice parameter, bound into prose by a token a
validator checks. Seven props became zero; the pseudo-placeholder that
haunted this very control's sibling field cannot be expressed at all.

The checklist, for the wall: *How many clauses — and would each survive
alone? Which modality — and what does the lattice then permit without a
Deviation? Who is bound — and is the target hiding among the parties?
What must downstream tailor or assess — and does every deadline carry
its calendar?*

Next: Chapter 5 — where the 5,301-entry Australian membership matrix
finally dies, sets learn to nest, and your classification levels,
maturity tiers, and chapter structure all turn out to be the same one
mechanism.
