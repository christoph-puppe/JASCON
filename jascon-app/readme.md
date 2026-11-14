# JASCON App

A set of browser pages for working with JASCON bundles. There is no server and
no build step: the pages are HTML files that share one script and one
stylesheet. A bundle you load stays in your browser, with one exception you
have to switch on yourself: the suggestions of the Risk page and the drafts
of the Checks page send text to a model service once you type a key (see
"Suggestions from a model").

State: build 0.9.9. This build has the frame (the hub, the settings page and
the shared core) and nine tool pages, in the order of the work: Import,
Browse, Risk, Tailor, Map, Implement, Checks, Assess and Validate. One view of the Risk page and
the drafting of the Checks page can ask a language model; nothing else in
the app does, and nothing needs one. Since 0.9.3 the app reads advice packs:
a vendor's recommendations as one published bundle (see "Advice packs").
Since 0.9.9 the pages write who decided and when, and the Validate page
shows where that is missing (see "Who decided, and when").

## Start

The folder works as a whole; a single file from it does not run on its own.

```bash
python -m http.server 8000
```

Run that in the repository root and open
`http://localhost:8000/jascon-app/index.html`.

Opening `index.html` straight from disk works for everything except loading a
bundle from a URL and showing this help text, because a browser does not let a
page from `file://` fetch other files.

## Sets

A set is one working bundle. Every tool reads and writes the active set, which
you choose in the header. Sets are kept in this browser, in IndexedDB under
the name `jascon-app`, on this computer. Nothing is uploaded.

## Loading a bundle

On the Home page:

- **Open bundle folder** takes a folder that holds a `content-manifest.json`.
- **Open files or ZIP** takes JSON files or a zipped bundle.
- **Load from URL** fetches a bundle folder over http, for example
  `../converted_examples/US.IFA-GoodRead/ifa-core-bundle/`.
- Dropping a folder, a ZIP or files anywhere on the page does the same.

A selection with a manifest is a bundle and replaces the content of the active
set, after a question if the set is not empty. A selection without a manifest
is added to the set. A bundle whose manifest carries a pack header is an
advice pack and replaces nothing, whichever button it came through: it is
shown under *Advice packs* on the same page and added when you confirm.

A link can load a bundle and open a tool:
`index.html#load=<bundle-url>&tool=<tool>`.

A bundle whose manifest pins a kernel version this app does not implement is
not loaded; the message names the pinned version and the versions the app
reads (1.0.0 and 2.0.0).

## The tools

Each tool is a tab in the hub and works on the active set. What a tool writes
is saved to the set at once; the other open tools reload.

| Tool | Shows | Writes |
|---|---|---|
| Import | An OSCAL catalog or profile and the report of its import | Requirements and Sets from a catalog, as a set of its own; a Set and a Tailoring from a profile |
| Browse | The catalogue as a tree of Sets, every object with type filters and with the filters found in the loaded requirements, statistics | A Requirement (every `{param:}` token is declared as a parameter), a Set |
| Risk | The register with a heat map, the scales and their matrix, the coverage of the selected requirements, the risk catalogues | A Risk; a scale; the record of catalogue entries that do not apply |
| Tailor | Each Tailoring resolved: selection, operations with before and after, lattice verdict, derived tier | A Tailoring; the decision on a Deviation it carries; the resolved requirements as a package of their own |
| Map | The mappings as a table, with targets outside the set marked | A Mapping, also to a target outside the set |
| Implement | Components and Implementation edges; whether the authorization an inherited edge names is found; the advice packs of the set and the recommendations of each product | Components with the capabilities their edges cite, a system Component that lists them, Implementations; a product as a member of one of your components, and an Implementation that adopts a recommendation |
| Checks | The rules that carry assessment criteria (audit text, automated or manual) and their machine checks; a tester that computes the verdict for an observation you paste | A Check, written in the form or drafted by a model, one at a time or for many rules |
| Assess | Assessments, Findings by state, Attestations with a Full Match / Semantic Match / Tamper verdict | An Assessment with one Finding per requirement that is not satisfied; the state of a Finding; the decision on a Deviation of a Finding |

| Validate | What the ported kernel rules say about the whole set, by area, with the object each finding is about; who is not named as an author and which review date has passed; signatures against keys you trust; what composing the set with another set would report | A report as JSON, on request |

Clicking a reference opens the object in a drawer on the right; Escape closes
it.

What the Tailor page enforces while a Tailoring is written: an easing of a
modality, a parameter value outside its declared space and a substantive
change of prose each need a Deviation with a rationale; a value of the wrong
kind is refused; a second operation on one target is refused.

Running the same check again in Assess overwrites its Assessment and removes
a Finding that no longer applies while it is still open. A Finding that was
moved on is kept.

## Who decided, and when

Since release candidate 4 the kernel has one optional place for who decided
and when: `provenance` with an `author-ref` (a party URI) and a `date`
(specification D26, `drafts/CP-AUTHOR-1.md`). A Tailoring and each of its
selects, excludes and operations may carry it, a Risk and its two ratings,
an Implementation and a Finding. A Deviation may say when it was decided
(`decided`) and when it is due for review (`review-due`). A Mapping and a
Check had `provenance` before, and must have it.

**Who am I.** One setting, *Who am I* (`org:me`), holds your own party URI.
It is empty until you set it. Every form that writes one of these objects
shows the author it will write, taken from the setting, and you can change
it there for the page you are on. The date written is today's, in UTC.

**A missing author is never a refusal.** With the field empty a page writes
no `provenance` and saves all the same. No page makes up an author. What is
missing shows as a line on the Validate page (below). Two types are the
exception, by the kernel and not by the app: a Mapping and a Check are not
valid without `provenance`. Where the setting is empty the Map and Checks
pages fall back to a party under your namespace (`…/party/author`,
`…/party/check-author`), as they did before this build; the field shows it
before anything is saved.

**What each page writes.**

| Page | Writes |
|---|---|
| Tailor | `provenance` on the Tailoring. A Deviation the page wrote as pending is decided in the first view; the day is written as `decided`, and an approved one may get a `review-due` |
| Risk | `provenance` on the Risk, and on `rating` or `residual-rating` when that rating is set or changed |
| Implement | `provenance` on every Implementation of the workbench and on an edge that adopts a recommendation |
| Assess | `provenance` on a Finding it raises or moves; `decided` and `review-due` on a Deviation of a Finding |
| Map, Checks | `provenance` on the Mapping or Check, as before, starting from the setting |

**Nobody's decision changes hands.** `provenance` on a record names who
wrote this version. An entry of a Tailoring that has none of its own has
its Tailoring's, and a rating its Risk's. When you save a Tailoring that
somebody else saved before, or that you saved on another day, the entries
you did not change keep the author they had: the page writes the earlier
author onto each of them before it writes you on the Tailoring. An entry
that carries an author of its own keeps it. New and changed entries are
yours. The Risk page does the same for a rating you leave as it is. The
Implement workbench writes every edge of its system on each save, and a
check that is run again writes its open Findings again; an edge or a
Finding that comes out as it is stored keeps the author it names. A
version you save without an author names none; it does not keep the name of
whoever wrote the version before. A decision recorded on a Deviation is
not undone by a save from the Tailor form, which may still hold the
Deviation as it was written. One case cannot be kept apart: entries of
a Tailoring that never named anybody become yours with the first save that
names you, because the kernel cannot say "unknown" on an entry of a
Tailoring that names its author.

**A Deviation.** Where the kernel's state machine allows a next state, the
Tailor and Assess pages offer it. When a Deviation becomes approved or
withdrawn the form offers today as the day it was decided; you can change
or empty it. An approved Deviation may get a review date, on a date or
every so many units of a named calendar. A Deviation that is decided and
states no day can be given one; no day is suggested for it. Approved and
withdrawn are final. The app does not edit the authorizations of a
Component, so it has no field for the date of an authorization.

**Imports pre-fill, and you may overwrite.** An import reads who and when
from its source and shows both in two fields before anything is written.
What you type over a field replaces the source's, each field on its own;
an emptied field says "nobody" or "no day". A record gets `provenance` only
when both are known, and the report says how many records got theirs from
the source, from you, or not at all. See "Importing OSCAL" and "Risk
analysis" for what each source states.

**The two reports** are on the Validate page, each line in the words of the
reference validator:

- *Authors* (AUTHOR-1 to AUTHOR-4): a Tailoring at consumer tier with
  entries nobody signed, a Risk, Finding or Implementation without
  `provenance`, an approved or withdrawn Deviation without `decided`, an
  authorization without a date. Whether that is a failure is your
  programme's policy. The switch *Require authors* turns each line into an
  error, as `--require-authors` does for the reference; without it a line
  is a note.
- *Review dates* (REVIEW-1): every `review-due` of an approved Deviation or
  a managed Risk that has passed on the day asked about, and those that
  cannot be evaluated (a calendar period: the app has no calendar). The day
  is the field *Review dates as of*, today in UTC when you leave it alone;
  it is the reference's `--as-of`. An overdue review is never an error.

Measured for this build: on the example folder and on the IFA bundle the
page shows the lines `validate_core.py` prints, for 2026-11-13 and for
2023-06-24, with the switch off and on (the example folder: no AUTHOR line,
and one review date that cannot be evaluated; the IFA bundle: 10 AUTHOR
lines, 2 overdue reviews on the first day and 1 on the second).

## Advice packs

An advice pack is a bundle a vendor publishes (`drafts/CP-ADVICE-1.md`,
accepted for the 2.0.0 release candidate on 2026-11-12; 2.0.0 is not tagged
yet). Its manifest carries a pack header (kind `advice`, the pack's id, the
release, the publisher) and its objects are Components and nothing else. A
Component's capabilities are the recommendations: the requirement and the
clauses one is about, a text, and the parameter values the vendor suggests.
A capability is a claim. That a requirement is met is said only by an
Implementation of your own component that cites the capability. A bare
Component file is not a pack; a pack is a folder or a ZIP with its manifest.

**Where.** On the Home page, the card *Advice packs*: add a pack from a
folder, a ZIP or a URL. The buttons that load a bundle take a pack too and
hand it to the same card; nothing loads a pack over a set. The worked pack
of the repository is `jascon/example-packs/dbvendor-server-7-advice/`.

**Before anything is written** the card shows the pack: its id, the release,
the publisher and how far the publisher is established, every
Component with its product version, the product of somebody else it
describes (a relation of type `describes`, shown and never computed with),
and each capability with its requirement, clauses, text and suggested
values. The pack is read the way a bundle is checked: every listed file is
there and has both digests its manifest states, and the manifest pins kernel
2.0.0.

A publisher is shown with one of three words, never as a bare name:

- *proven*, in green: an attestation of the publisher's origin beside the
  pack's manifest binds the digest of the manifest, a trusted key for its
  signer is set on the Validate page, and the envelope verifies under it.
- *attested, not verified*, in amber: such an attestation binds the
  manifest, and no trusted key is set. Anyone can write an attestation in a
  vendor's name, so until a signature is checked the publisher is a claim.
- *claimed*: everything else. The header names the publisher and the ids
  share its origin; no attestation binds the manifest, or its signature did
  not verify under the key you trust, and the reason is shown.

The rules answer *claimed* or *proven* as the reference validator does, and
in a run without keys their *proven* is the second case. `validate_core.py`
prints it as "ATTESTED, NOT VERIFIED"; the app shows it the same way, on
every page and in the findings of the Validate page.

**On import** the vendor's Components join the set as the files they are,
the vendor's manifest is kept unchanged beside the set's own as
`packs/sha256/<SHA-256 of its bytes>`, and the vendor's attestation and its
envelope are kept beside the manifest. Nothing else is written. The receipt
is measured after the write and has the form
`unchanged <n> of <n> · added <m> components`: of the objects of the set
that the pack does not own, how many have the semantic digest they had
before. That no Tailoring resolves differently follows from the pack holding
Components only and is not computed.

| The set holds | The file is | What happens |
|---|---|---|
| no pack of this id | | preview, then import |
| the kept manifest of this very file | the same file | nothing is written: *Already imported: release N* |
| a kept manifest of this pack with another digest | another release | preview with what changes; on confirmation the objects and the kept manifest of the earlier release are replaced |
| an object with an id of the pack that no kept manifest of this pack lists | | refused (ADVICE-11) |

For another release the preview lists, per Component, the capabilities
added, removed and changed, and every Implementation of the set that cites a
removed or changed capability. Releases are not ordered: `version` is an
opaque text, and which release is newer is yours to say. An edge that cites
a removed capability fails ADVICE-7 after the import until you change it. A
set holds one release of a pack (ADVICE-10).

**What is refused**, each with the rule's own sentence: a pack that lists
anything but Components (ADVICE-1), an object or a publisher outside the
pack's origin (ADVICE-2), a facet that declares a semantics class
(ADVICE-3), an id the set holds already and the pack does not own
(ADVICE-11), a bundle without a pack header, a pack without the kernel pin,
a file that does not match the digests its manifest states, and a pinned
facet schema the set holds in another version.

**Adoption** is on the Implement page, view *Advice*. It lists the packs of
the set (id, release, publisher with one of the three words, components) and, for one
of your components, every other Component that declares a capability. A
product's advice applies to your component because the component contains
the product (ADVICE-7), so the view first makes the product a member of your
component. *Adopt* then writes an Implementation of your component that
cites `<product-id>#<capability-id>`, with the capability's clauses as its
`statement-refs`. A suggested parameter value is copied into the edge only
when you tick it and it fits the set: inside the parameter's declared space,
and in agreement with every Tailoring that selects the requirement and binds
the parameter (the same value, or, for a parameter that tightens, a tighter
one). Any other suggested value is shown with the reason and not written. A
capability about a requirement the set does not hold cannot be adopted,
because an Implementation needs its requirement in the bundle. The vendor's
Component is never written by the app.

**What the Validate page says** about packs: ADVICE-1 to ADVICE-10 over the
set, among them that a kept manifest is named by the digest of its bytes
(ADVICE-8) and that every object it lists is in the set at that version with
that semantic digest (ADVICE-9: the vendor's advice was not edited after the
import), and for every pack how far its publisher is established.

**What the app does not do.** It does not write or sign a pack. It does not
convert an OSCAL component definition into a pack. It keeps no earlier
release. It does not compare releases by their version text. A pack's
attestation that binds another manifest is not kept. A Component's
`product-version` is one text and is shown, never parsed or compared.

## Importing OSCAL

OSCAL enters the app on the Import page and nowhere else. The file is read in
the browser; the import runs in memory and shows its report; nothing is
written until you choose *Write to the set*.

**A catalog** becomes Requirements and Sets, written as a bundle of its own
into a set you name, with a manifest whose provenance names the source file
and the licence you state. Three sets of rules:

- *BSI Grundschutz++* follows `jascon/scripts/convert_bsi.py`: a nested
  control is a clause of its parent, the modal verb becomes the modality, the
  BSI props go to the standard facets and two BSI facets, the security level
  becomes baseline Sets. Every object it makes from the Anwenderkatalog of
  2026-07-16 has the semantic digest of the bundle under
  `converted_examples/DE.BSI`.
- *generic*, for any other catalog: every control, nested ones included, is a
  Requirement; every part of the statement that carries prose is a clause;
  the modality is `unspecified`, because OSCAL has no field for it. Props and
  other parts are held verbatim in a facet under your namespace, with a
  pinned schema. A control without statement prose is carried with its title
  and listed in the report.

- *NIST SP 800-53 Rev 5*, the rules of `convert_nist.py`: a withdrawn control
  is not converted, and its successor names it in `replaces`; every statement
  item with prose is a clause with modality `must`; SP 800-53A objectives and
  methods, the administrative data of parameters and the guidance go to
  facets under the NIST namespace. On the same source file its 1,035 objects
  equal the Python converter's. Against the shipped
  `converted_examples/US.SP800-53` bundle four objects differ, because NIST
  republished its 5.2.0 file after that bundle was converted (the statement
  of SA-15(13), objectives of SA-24, labels of SI-2(7), one back-matter
  resource). The preset makes no baseline Sets: a baseline is a profile, and
  you import it as one.

- *CIS Benchmark*, the rules of `convert_cis_benchmark.py`: every rule is a
  Requirement with one clause whose text is the rule's title (the export
  leaves the statement empty); the audit and remediation text and the
  marking automated or manual go to `assessment-criteria@1`, which is where
  the Checks tool reads them; profiles become baseline Sets, the CIS Controls
  cross-references Mappings (supports, draft), the xccdf id an alias. For the
  CIS Ubuntu 24.04 Benchmark it mints the converter's namespace, for any
  other one derived from the title, which you may change. The repository
  carries no CIS Benchmark (CIS terms); a test runs the Python converter and
  the preset on a catalog of the same shape written for the test and finds
  every object with the same semantic digest. The option *draft checks for
  the automated rules with a model* opens the Checks tool after the write
  with those rules selected; it sends nothing by itself.

The generic rules read the NIST catalog too (1,196 requirements, valid for
the reference validator), with a different result: withdrawn controls are
kept as requirements, and assessment objectives stay in the holding facet.

Choose the namespace with care. Ids under your own domain make you the
claimed authority of the catalog in the tier rule, and a Tailoring of yours
may then weaken it without a Deviation. Use the publisher's namespace where
it has one.

**A profile** is added to the active set, because it names requirements that
have to be there. A control is matched to the requirement whose id ends in
the control's id, without regard to case.

| In the profile | Becomes |
|---|---|
| `include-controls` with ids | a Set of those requirements, selected by a new Tailoring |
| `include-all` | a select of the catalogue Set you name |
| `exclude-controls` with ids | excludes of the Tailoring |
| `set-parameters` | one `set-parameter` operation per clause that declares the parameter, if the value lies in its declared space |
| a value outside the declared space | listed in the report, not written: it needs a Deviation |
| `alters`, `merge`, pattern matching, child controls | counted in the report, not carried |
| `metadata`: parties, their roles, `last-modified` | `provenance` on the Tailoring: who wrote the profile and when |

**Who wrote an OSCAL document, and when.** The page shows both before the
import, in two fields you can type over. The author is one party of the
document's `metadata`, found by this rule:

1. the one party named as `creator`, else the one named as `prepared-by`
   (the `party-uuids` of all `responsible-parties` entries of that role
   together, without those `parties` does not define);
2. else the one party that holds any role at all;
3. else the one party the document defines;
4. else its one party of type `organization`;
5. else nobody.

A party without a name cannot be named by a URI; where the rule lands on
one, the answer is nobody. The party becomes `<namespace>/party/<name>`,
under the namespace of the import, with the converters' slug. The day is
the first ten characters of `last-modified`, as the document writes them,
if they are a date. The Python converters of this repository are written
to the same rule.

A CIS Benchmark's cross-references keep the author they had: CIS
(`<namespace>/party/cis`), on the day the catalog was last changed. You can
type over either; a Mapping cannot be written without both, because the
kernel requires its `provenance`. The Requirements and Sets of a catalog
carry no `provenance`: their publisher is the origin of their ids.

## Risk analysis

The Risk tool has five views.

**Register.** Every risk with its state, level, residual level, treatment and
owner, and the number of rule errors it has. The heat map shows the risks on
the grid of a level scale's matrix, for the current or the residual rating;
a click on a cell lists its risks.

**Risk.** The form for one risk. Below it stands what the rules say, and the
risk is saved only when there is no error:

- the kernel shape, with the rule named: an assessed risk needs a rating
  (RISK-2), a treated one its option and its acceptance (RISK-3), the option
  modify needs requirements (RISK-4), share needs a party (RISK-5), retain
  needs an acceptance (RISK-6);
- the references: a treatment names a requirement of the set and statements
  that exist, a component at risk is a component, a Tailoring is a Tailoring
  (RISK-7, 8, 12);
- the scales: a level is one its scale defines (SCALE-2), and a treatment
  must not name a requirement the Tailoring dropped (RISK-11);
- a state moves forward only: identified, assessed, treated, retired.

Where the level scale carries a matrix and likelihood and impact are chosen,
the level is the matrix cell. Another level needs the box *depart from the
matrix* and a reason; the reason is stored as the rating's
`override-rationale`. Without it the rule SCALE-4 refuses the risk. The
residual rating uses the same scales as the rating.

**Scales and matrix.** A scale is a file the manifest pins, not an object. It
lists its levels from lowest to highest. The scale of the combined level may
carry a matrix over a likelihood scale and an impact scale, one level for
every pair. Two starting sets can be added, as published or as a copy under
your namespace: three levels each with a 3 x 3 matrix, and a set in the style
of BSI 200-3 with a 4 x 4 matrix. Their level names and cells were written
from memory of the methods they follow and were not checked against the
standards; change them to your method.

Changing a scale that risks use: the risks left on a level that no longer
exists are listed before you save, and they stay wrong until you rate them
again. A level that is renamed keeps its cells in the matrices that use the
scale; a level that is removed loses them; a level that is added leaves the
matrix incomplete until its cells are filled in.

**Coverage.** For each Tailoring in force, or for every requirement when the
set has no Tailoring: how many selected requirements are justified by a risk,
pending (named only by a risk that is not yet assessed with an option
chosen), lapsed (named only by a retired or withdrawn risk), or named by no
risk. The switch *Require a risk basis* turns the unjustified ones into
failures; without it they are a line of the report.

**Risk catalogues.** The two catalogues the repository ships, office IT and
industrial plant. Importing an entry copies it into a risk of your own with
state identified and lifecycle draft, keeps the suggested requirements the
selection contains and names the entry it came from. A risk that exists is
never overwritten by an import. An imported risk says who wrote it and
when: the catalogue's publisher and the day the catalogue says this version
was released (2026-11-10 for both shipped catalogues). The two fields
*Author of the imported risks* and *Day* show them; what you type over a
field replaces it, and with one of them empty the risk is imported without
an author. The log says how many imported risks got theirs from the
catalogue, from you, or not at all. Once you assess an imported risk and
save it, that version and its rating are yours.

An entry that does not apply is recorded in
`risk-catalogs/not-applicable.json` beside the manifest: the entry and its
version, the reason, and who decided on which day. The party in the Owner
field of the view is written as the one who decided. A file from before
build 0.9.7, a map from an entry to a sentence, is still read; its rows show
"no author recorded" until they are recorded again.

## Checks

The Check type belongs to the 2.0.0 release candidate (`drafts/CP-CHECK-1.md`,
accepted on 2026-11-12); 2.0.0 is not tagged yet. A check has two parts: a
collector, code that reports facts and decides nothing, and criteria, a flat
list of comparisons from twelve fixed operators that must all hold. Because the verdict is computed from the
facts, anyone can recompute it from a recorded observation; the Validate
page does so for every check result an Assessment carries.

The tool has three views.

**Rules and checks.** Every requirement that carries assessment criteria
(a CIS import puts its audit text there) or has a check, with the marking
automated or manual and the checks it has. A check for any other
requirement is written from the editor.

**Edit a check.** The form of one check: requirement and clauses, platform,
confidence, the facts with their types, the criteria and the conditions
under which the rule applies, per-resource repetition, how long a result
stays fresh, and the collectors with their code. Below it stands what the
kernel rules say (the shape and CHECK-1 to CHECK-7: a fact is declared once,
an operator fits its fact, a parameter is declared on the clause and
tightening it never loosens the check, a pattern is an I-Regexp), and what
the read-only lint finds in the code. A check the rules refuse cannot be
saved. *Try the criteria* computes the verdict for an observation you paste,
with parameter values typed or taken from a Tailoring. *Ask a model for this
check* sends this one rule, with an optional description of your own, and
fills the form with the answer; nothing is saved until you save.

**Draft with a model.** The same question for many rules: by default the
rules marked automated, or every rule with audit text. Resolved in code and
never sent: a rule marked manual, a rule without audit text, and a rule that
has a check with a collector in the chosen language already. The log states
that split before the run. Answers are kept as they arrive; a draft is
saved only when you tick it and save, and only if the rules pass it again.

What the lint is: a list of patterns for commands that write, install,
restart or reach the network, per language. A warning asks for a look; no
warning proves a script harmless. The app does not run a collector.

## Suggestions from a model

Two places ask a language model for what no rule can compute: the last view
of the Risk page (risks and their treatments) and the Checks page (facts,
criteria and collector code for a technical rule). Everything else in the
app is computed.

- **Draft a check.** One call per rule. The app sends the rule (title,
  clauses, parameters with their bounds, audit and remediation text, your
  description), the target language and the contract of a check: the
  twelve operators and five fact types, taken from the kernel schema, and
  the rules for collectors (read only, effective values, one line of JSON).
  The answer schema restricts operators and fact types to the kernel's. The
  app assembles the answer: it mints the id, sets the requirement and
  clauses, writes confidence and lifecycle draft and names the service in
  the annotations. An answer whose expected value is not JSON, that names a
  parameter the rule does not have, or that writes a decimal as a float is
  refused with its reason; a rule the model says does not fit (judgement,
  two facts compared, arithmetic) gets no check.

- **Suggest risks.** You describe the scope. The app adds the components of
  the set, the risks the register has already and the levels of the pinned
  likelihood and impact scales, and asks for drafts in one call. A draft has
  a title, a scenario, the components it concerns, a likelihood and an
  impact. The level is not asked for: it is the matrix cell, computed.
- **Suggest treatments.** For each risk in scope (by default those without a
  treatment) the app sends the requirements the Tailoring selects and asks
  which of them act on the risk. One call per risk, several at a time; a
  selection larger than the setting *Requirements per call* is cut into
  several calls per risk.

What you can rely on:

- **Nothing is sent without a key and a click.** The view shows the exact
  text of a call before it is sent, and its size in calls and tokens.
- **The key is not stored.** It is held in the memory of the page and of the
  hub and travels in a request header. It is not written to localStorage,
  sessionStorage, IndexedDB, a set, an export, the log or a URL. Reloading
  the hub, or opening the settings in the same tab, clears it and you type it
  again. The hub shows while it holds one and forgets it on a click.
- **The model sees keys, not your ids, and mints none.** Components and
  requirements are sent as C1, Q7 and so on. A key in the answer that was not
  sent is dropped and counted; a level that the scale does not define gives a
  draft without a rating; a draft with the title of an existing risk is not
  shown.
- **An answer is a suggestion.** A risk is written only when you take a draft
  or tick requirements, and by the same rules as the form: what the rules
  reject is not saved and the reason is shown. A risk drafted this way is
  saved with state identified and lifecycle draft, and says so in its
  `annotations` (service, model, date), which are outside the semantic
  digest.
- **An answer is paid for once.** Answers are kept in this browser, keyed by
  service, model, prompt and content; running again after a cancel or an
  error sends only the calls that have no answer. Tick *ask again* to
  override it.

The service, the model and the limits of a run are settings; the two prompts
can be edited on the settings page and in the view, with a reset. Three
services are supported: Google Gemini, OpenRouter, and an endpoint of your
own that speaks the OpenAI chat-completions protocol. A call is repeated
after a rate limit, a server error, a timeout or an answer of the wrong
shape, at most five times; an error such as a rejected key is shown at once
with the service's own message.

Opened as a file (`file://`) a call may be refused by the browser; serve the
folder with `python -m http.server` instead. Whether a call costs money is
between you and the service: of the Gemini models named in the settings,
`gemini-4-argon` has no free tier.

## Integrity

**Verify all digests** recomputes two SHA-256 digests for every object and
compares them with the manifest the bundle came with: the package digest over
the bytes of the file, and the semantic digest over the canonical form of the
object without its annotations. Pinned facet schemas and scale definitions are
checked against their pins.

A mismatch on an object you edited in the app is reported as an edit. A
mismatch on an object you did not touch means the file is not the one the
manifest describes.

A pack manifest the set keeps under `packs/sha256/` is named by the SHA-256
of its bytes; the same button checks each one against its name, and the
Validate page reports a mismatch as ADVICE-8.

## Export

**Export the set as a bundle** downloads a ZIP with the objects, the pinned
files and a `content-manifest.json`.

- A set nobody changed leaves byte for byte as it came, with its manifest.
- A set that was changed gets a new manifest with both digests per object,
  the pins for its scales and facet schemas, and `kernel-version` 2.0.0 when
  the content needs it (a Risk, a Check, check results, a Finding that names
  risks or a check, a pinned scale, a Component with `product-version` or
  with clauses on a capability; `provenance` on a Tailoring, on one of its
  selects, excludes or operations, on an Implementation or a Finding; a
  Deviation with `decided` or `review-due`; an authorization with a `date`).
  Its provenance gains the line `edited-with`.
- An attestation the original manifest did not list stays beside the manifest
  and is not added to it.
- The pack manifests under `packs/sha256/`, a pack's attestation and its
  envelope leave as they came, beside the manifest; none of them is listed
  in it, and the manifest of a set never carries a pack header.
- Exporting twice gives the same archive.

The Python reference validator checks an exported bundle after unzipping:

```bash
python3 jascon/scripts/validate_core.py <unzipped-folder>
```

## Settings

Settings are kept in this browser's localStorage and hold no secret. The key
of a model service is not a setting.

<!-- settings:start (generated by tools/gen-docs.mjs, do not edit) -->
| Key | Setting | Values | Default | Note |
|---|---|---|---|---|
| `ui:lang` | Language of the interface | (empty), `en`, `de` | (empty) | Empty follows the browser. |
| `ui:contentlang` | Language of the content | text | (empty) | BCP-47 tag picked from the language maps of a bundle, for example de. Empty follows the interface. |
| `ui:theme` | Colour scheme | `dark`, `light`, `system` | `dark` | System follows the operating system. |
| `ui:style` | Style | (empty), `classic`, `ledger`, `engraving`, `still-life` | (empty) | Empty follows the style picked on jascon.net in this browser. Classic is the original look; the other three take the palette and type of the website's styles. |
| `org:ns` | Namespace for new objects | text | `https://example.org/my` | The URI under which this app mints ids, for example https://your.example. Use a name you control. |
| `org:owner` | Default risk owner | text | (empty) | A party URI, for example https://your.example/party/ciso. Prefilled when a risk is created. |
| `org:me` | Who am I | text | (empty) | Your own party URI, for example https://your.example/party/jane-doe. Prefilled as the author of what you write: a Tailoring, a Risk, an Implementation, a Finding, a Mapping, a Check. Each form shows it and lets you change it. Empty: a page names no author unless you type one, and saves all the same. |
| `ai:backend` | Model service | `gemini`, `openrouter`, `openai` | `gemini` | gemini is Google's API, openrouter is OpenRouter, openai is an endpoint of your own that speaks the OpenAI chat-completions protocol. No model is called until you type a key on a page that offers suggestions. |
| `ai:model:gemini` | Model at Google Gemini | text | `gemini-3.8-flash` | A model id of the Gemini API, for example gemini-3.8-flash, gemini-3.5-flash-lite or gemini-4-argon (no free tier). Check the id against Google's model list; ids are retired. |
| `ai:model:openrouter` | Model at OpenRouter | text | (empty) | A model slug in the form vendor/model. The model must support structured outputs. |
| `ai:model:openai` | Model at your own endpoint | text | (empty) | The model name your endpoint expects. |
| `ai:base:openai` | Base URL of your own endpoint | text | (empty) | For example https://llm.your.example/v1. The app calls /chat/completions under it and sends the key as a bearer token. |
| `ai:thinking` | Thinking level | `low`, `medium`, `high`, `minimal` | `medium` | Gemini only. minimal exists on gemini-3.6-flash and gemini-3.5-flash-lite; on every other model it is sent as low. |
| `ai:retries` | Retries per call | text | `2` | How often a call is repeated after a rate limit, a server error, a timeout or an answer of the wrong shape. 0 to 5. |
| `ai:concurrency` | Calls at the same time | text | `3` | 1 to 8. Lower it when the service answers with rate limits. |
| `ai:chunk` | Requirements per call | text | `400` | How many candidate requirements one call carries when treatments are suggested. A larger selection is cut into several calls per risk. 20 to 2000. |
<!-- settings:end -->

## Languages

The interface is in English and German; the button in the header switches.
The content of a bundle carries its own language maps, and the setting
*Language of the content* says which entry is shown. Where a bundle has no
text in that language, the English text is shown, then whatever is there.

## Limits of this build

- The Validate page is not the reference validator. All eighteen rule
  families of `validate_core.py` are ported and run against their conformance
  vectors: canonical form (with the number domain, NUMBER-1: the text of
  every file is held to it, because the browser's parser reads `1.0` as 1
  and rounds an integer beyond 2^53), modality, parameter, tier, tailoring (the
  operation law), reference, lifecycle, kernel (with the typed dates and
  times, from `Finding.actions[].due` to `Attestation.timestamp`, named
  DATE-1 to DATE-5 when an object matches no type), facet, attestation, risk,
  scale, DSSE signatures, the composition of two bundles,
  conditional-apply, the Check type of `drafts/CP-CHECK-1.md`
  (I-Regexp, check-verdict, CHECK-1 to CHECK-15 with the evidence chain),
  advice packs of `drafts/CP-ADVICE-1.md` (ADVICE-1 to ADVICE-11 with
  the publisher verdict and the import plan), and who decided and when of
  `drafts/CP-AUTHOR-1.md` (AUTHOR-1 to AUTHOR-4, what is missing, and
  REVIEW-1, which review date has passed on a given day; two reports, shown
  on the page since build 0.9.9). What the page does not judge:
  conditional-apply
  instances (no bundle has a place to carry one; the reference validator does
  not run them on a bundle either) and the bytes of a bundle on disk (line
  ends, files the manifest does not list). In
  a case of doubt run the Python validator on the export; where the two
  disagree, the app is wrong.
- Who decided: the app knows who you are only from the setting *Who am I*;
  it does not log anybody in, and an author is a claim inside the object,
  not a proof. The pages do not raise an object's `version` when they save
  it, so "this version" is the stored object. A Tailoring is written from
  the form of the second view, which does not load a stored Tailoring; a
  save under the same label replaces it, and the entries that are the same
  keep their authors. The authorizations of a Component, and a Deviation on
  anything but a Tailoring's operation or a Finding, are shown and not
  edited. A review date is offered on a date or as a calendar period, not as
  an elapsed duration.
- Signatures: Ed25519 over a DSSE envelope, verification only. A key is
  trusted because you say so on the Validate page, never because a bundle
  carries it. The app cannot sign. The reference validator looks at the
  envelope of an attestation only when the manifest lists the attestation;
  the app looks at every attestation of the set and reports a missing
  envelope of an unlisted one as a note.
- The other pages still take an object's type from its fields when a set is
  loaded; the Validate page says where the kernel schema disagrees.
- Loading from a URL fetches what the manifest lists, the envelope a
  listed attestation names, and the evidence store the check results of an
  Assessment name (`evidence/sha256/<hex>`: the records and the outputs they
  list). A file beside the manifest that nothing listed names, such as an
  attestation over the manifest, is not fetched; load the folder or a ZIP for
  those.
- The pack manifests a set keeps (`packs/sha256/`) and the attestation of a
  pack's publisher are named by nothing a manifest lists, and a URL names
  files, not folders. Loading from a URL finds them only where the server
  lists the folder, as `python -m http.server` does. A request for a listing
  that is not there shows as an error in the browser's console, so the app
  asks only where it has a reason: the manifest carries a pack header, or it
  lists Components under an origin from which it lists nothing else (a pack
  brings Components and nothing else, all under its publisher's origin).
  Without a listing nothing is found, a pack from a URL is then *claimed*,
  and a folder or a ZIP carries these files.
- Predicate selects of a Tailoring are not evaluated; the selection is then
  shown as open and its count as a lower bound.
- The Tailor page applies set-modality, set-parameter and replace-prose.
  Other operations are shown, and a resolution that contains one is reported
  as incomplete.
- The Implement workbench does not write inherited edges.
- The type of an object is recognised by its fields, not by matching it
  against the kernel schema.
- Files other than text (images, PDF) in a bundle folder are not stored,
  except a file an attestation names as its envelope and the pack manifests
  under `packs/sha256/`, and
  are missing from the export. Evidence blobs are kept when they are text
  (and at most 256 KiB when a folder is picked); a blob that is not UTF-8
  text is reported by the Validate page as one it cannot verify, and the
  reference validator can.
- The model view was run against a simulated service only. No call to a
  real service was made while it was built, and the model ids in the
  settings were not checked against Google's list on that day; a wrong id
  shows as the service's error on the first call.
- There is no second model pass that audits the first; you review each
  suggestion. There is no price estimate, no list of models to pick from, no
  search grounding, and no fallback for an endpoint that rejects a JSON
  schema.
- Suggestions exist on the Risk page and the Checks page.
- The app does not run collectors and does not record runs; a check is
  written, drafted and tried against an observation you paste.
- No web font is fetched and no script is loaded from another host. The only
  requests to another host are the calls to the model service you chose.

## For developers

```bash
node --test "jascon-app/tests/*.test.mjs"
```

```bash
node jascon-app/tools/check-i18n.mjs
```

```bash
node jascon-app/tools/gen-docs.mjs
```

The first runs the tests: every shipped bundle round-trips unchanged, an
edited bundle passes the reference validator, the ported rules pass the
conformance vectors of their families, the catalogue import rebuilds the
committed demo, the model access behaves as described above against a
simulated service (what a request carries, the retry limit, the checks on an
answer, the key in no storage), the Checks tool goes from a CIS import to
saved checks against a simulated model and the exported bundle passes the
reference validator, an advice pack goes from its preview through import and
adoption to an export the reference validator accepts (in node on the files,
and in a browser through the pages), the pages that write who decided are
driven in a browser and each exported set is handed to the reference
validator with `--require-authors`, the Validate page shows the reference's
AUTHOR and REVIEW lines for the example folder and the IFA bundle, the
author of an OSCAL document follows the table of its rule, every page starts in a browser without a script error, every
interface string has a German text, and what is generated (the settings table
above, `jascon-schema.js`, `jascon-presets.js`) matches its source. The second lists
strings without a German text. The third rewrites the settings table from
`JSC_CFG` in `jascon-core.js`.

Three tests of the OSCAL import compare with the publishers' source files,
which the repository does not carry (`sources/` is ignored); without the
files they are skipped. The files are the Anwenderkatalog Grundschutz++ of
2026-07-16 from `BSI-Bund/Stand-der-Technik-Bibliothek` (commit `39a1193`,
`Anwenderkataloge/Grundschutz++/Grundschutz++-catalog.json`) as
`sources/Grundschutz++-catalog.json`, and from `usnistgov/oscal-content`
(`nist.gov/SP800-53/rev5/json/`) the catalog and the MODERATE baseline
profile under `sources/nist/`.

`jascon-schema.js` and `jascon-presets.js` are generated; after a change to
the kernel schema, the shipped scales or the risk catalogues run:

```bash
node jascon-app/tools/gen-schema.mjs
```

```bash
node jascon-app/tools/gen-presets.mjs
```

Bugs that reached a push are recorded in `ERRATA.md` with the test that now
covers them.

The part of `jascon-core.js` between `JSC-PURE-START` and `JSC-PURE-END`
touches neither the DOM nor storage; the tests load it in node.

Licence: Apache-2.0. Parts derive from the Grundschutz++ OSCAL tools of NTT
DATA, see `NOTICE` in the repository root.
