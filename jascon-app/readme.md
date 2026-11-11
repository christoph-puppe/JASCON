# JASCON App

A set of browser pages for working with JASCON bundles. There is no server and
no build step: the pages are HTML files that share one script and one
stylesheet. A bundle you load stays in your browser, with one exception you
have to switch on yourself: the suggestions of the Risk page send text to a
model service once you type a key (see "Suggestions from a model").

State: build 0.7.0. This build has the frame (the hub, the settings page and
the shared core) and eight tool pages: Import, Browse, Tailor, Map,
Implement, Risk, Assess and Validate. One view of the Risk page can ask a
language model; nothing else in the app does, and nothing needs one.

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
is added to the set.

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
| Tailor | Each Tailoring resolved: selection, operations with before and after, lattice verdict, derived tier | A Tailoring; the resolved requirements as a package of their own |
| Map | The mappings as a table, with targets outside the set marked | A Mapping, also to a target outside the set |
| Implement | Components and Implementation edges; whether the authorization an inherited edge names is found | Components, a system Component that lists them, Implementations |
| Risk | The register with a heat map, the scales and their matrix, the coverage of the selected requirements, the risk catalogues | A Risk; a scale; the record of catalogue entries that do not apply |
| Assess | Assessments, Findings by state, Attestations with a Full Match / Semantic Match / Tamper verdict | An Assessment with one Finding per requirement that is not satisfied; the state of a Finding |

| Validate | What the ported kernel rules say about the whole set, by area, with the object each finding is about; signatures against keys you trust; what composing the set with another set would report | A report as JSON, on request |

Clicking a reference opens the object in a drawer on the right; Escape closes
it.

What the Tailor page enforces while a Tailoring is written: an easing of a
modality, a parameter value outside its declared space and a substantive
change of prose each need a Deviation with a rationale; a value of the wrong
kind is refused; a second operation on one target is refused.

Running the same check again in Assess overwrites its Assessment and removes
a Finding that no longer applies while it is still open. A Finding that was
moved on is kept.

## Importing OSCAL

OSCAL enters the app on the Import page and nowhere else. The file is read in
the browser; the import runs in memory and shows its report; nothing is
written until you choose *Write to the set*.

**A catalog** becomes Requirements and Sets, written as a bundle of its own
into a set you name, with a manifest whose provenance names the source file
and the licence you state. Two sets of rules:

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

The rules of `convert_nist.py` for NIST SP 800-53 are not ported. The generic
rules read that catalog (1,196 requirements, valid for the reference
validator), but the result is not the shipped SP 800-53 bundle: withdrawn
controls are kept as requirements, and assessment objectives stay in the
holding facet.

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
never overwritten by an import. An entry that does not apply is recorded with
its reason in `risk-catalogs/not-applicable.json` beside the manifest.

## Suggestions from a model

The last view of the Risk page asks a language model for the two things no
rule can compute. Everything else on the page, and in the app, is computed.

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

## Export

**Export the set as a bundle** downloads a ZIP with the objects, the pinned
files and a `content-manifest.json`.

- A set nobody changed leaves byte for byte as it came, with its manifest.
- A set that was changed gets a new manifest with both digests per object,
  the pins for its scales and facet schemas, and `kernel-version` 2.0.0 when
  the content needs it (a Risk, a Finding that names risks, or a pinned
  scale). Its provenance gains the line `edited-with`.
- An attestation the original manifest did not list stays beside the manifest
  and is not added to it.
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
| `org:ns` | Namespace for new objects | text | `https://example.org/my` | The URI under which this app mints ids, for example https://your.example. Use a name you control. |
| `org:owner` | Default risk owner | text | (empty) | A party URI, for example https://your.example/party/ciso. Prefilled when a risk is created. |
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

- The Validate page is not the reference validator. All fifteen rule
  families of `validate_core.py` are ported and run against their conformance
  vectors: canonical form, modality, parameter, tier, tailoring (the
  operation law), reference, lifecycle, kernel, facet, attestation, risk,
  scale, DSSE signatures, the composition of two bundles and
  conditional-apply. What the page does not judge: conditional-apply
  instances (no bundle has a place to carry one; the reference validator does
  not run them on a bundle either) and the bytes of a bundle on disk (line
  ends, files the manifest does not list). In a case of doubt run the Python
  validator on the export; where the two disagree, the app is wrong.
- Signatures: Ed25519 over a DSSE envelope, verification only. A key is
  trusted because you say so on the Validate page, never because a bundle
  carries it. The app cannot sign. The reference validator looks at the
  envelope of an attestation only when the manifest lists the attestation;
  the app looks at every attestation of the set and reports a missing
  envelope of an unlisted one as a note.
- The other pages still take an object's type from its fields when a set is
  loaded; the Validate page says where the kernel schema disagrees.
- Loading from a URL fetches what the manifest lists, and the envelope a
  listed attestation names. A file beside the manifest that nothing listed
  names, such as an attestation over the manifest, is not fetched; load the
  folder or a ZIP for those.
- Predicate selects of a Tailoring are not evaluated; the selection is then
  shown as open and its count as a lower bound.
- The Tailor page applies set-modality, set-parameter and replace-prose.
  Other operations are shown, and a resolution that contains one is reported
  as incomplete.
- The Implement workbench does not write inherited edges.
- The type of an object is recognised by its fields, not by matching it
  against the kernel schema.
- Files other than text (images, PDF) in a bundle folder are not stored,
  except a file an attestation names as its envelope, and
  are missing from the export.
- The model view was run against a simulated service only. No call to a
  real service was made while it was built, and the model ids in the
  settings were not checked against Google's list on that day; a wrong id
  shows as the service's error on the first call.
- There is no second model pass that audits the first; you review each
  suggestion. There is no price estimate, no list of models to pick from, no
  search grounding, and no fallback for an endpoint that rejects a JSON
  schema.
- Suggestions exist on the Risk page only.
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
answer, the key in no storage), every page starts in a browser without a script error, every
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
