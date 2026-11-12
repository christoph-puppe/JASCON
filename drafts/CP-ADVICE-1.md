# CP-ADVICE-1 — Advice packs: a vendor's recommendations as one published file

**Change proposal · JASCON kernel 2.0.0-rc.1 → 2.0.0 · 2026-11-12**
**Process:** Chapter 15.4 (evidence in, corpus first, implementations follow). Every rule carries a machine id, a rationale and a failure message that prints on failure.
**Scope:** content manifest (one optional header), kernel schema (one optional field on a capability, one string grammar), reference validator, conformance corpus, one worked pack, a converter, the app. Handbook, specification, SKILL.md, reader and PowerShell twin: §10, after the author's review.
**Status (2026-11-12, later the same day): ACCEPTED by the author for kernel 2.0.0, in release candidate 2.0.0-rc.3; 2.0.0 is not tagged.** The eight open points of §11 are decided (§14), and the specification describes advice packs as decision D25. Where §14 and an earlier section differ, §14 is the state.

**Status before that (2026-11-12): proposed, on branch `claude/cp-advice-1`.** Sections 1 to 12 are the proposal as drafted, before any code: nothing was run for them, and every count in them is read from files in the repository, with the place named. On the same day the kernel side was built: schema, reference validator, 71 vectors, a worked pack and the PowerShell twin are in the repository and green in both implementations. **§13 says what exists, what does not, and what contact with the repository changed.** Where §13 and an earlier section differ, §13 is the state.

**Author statements this proposal implements (2026-11-12):** (1) OSCAL component definitions are worth having for one thing: a vendor supplies recommendations and has no way to change the user's controls or assessments; (2) there is a file the vendor publishes; (3) the user selects it for import; (4) after the import it is clear which vendor, which version and which component; (5) the same file is not imported twice.

**Proposed by the drafter, decided since (§14):** the eight points of §11. The author's instruction of 2026-11-12 was to start implementing; none of the eight was changed, so items 1 to 6 are built as proposed and remain the author's to overturn.

---

## 1. The gap, in one sentence

JASCON can hold what a vendor says its product does for a requirement — `Component.capabilities[]` — but it has no file a vendor publishes as such, no rule that keeps such a file from carrying a Tailoring or somebody else's Requirement, and no record in the user's set of which vendor's release came in.

OSCAL 1.x gets the guarantee from its document model: a component definition has no place to define a control, it can only point at one. JASCON has no document models (D4), so the same guarantee has to be a rule on a bundle.

## 2. The counts

### 2.1 What the repository carries today

| Thing | Where | State |
|---|---|---|
| The carrier | `jascon-2.0.0.schema.json`:1084-1107 | A capability is `{id ●, requirement-ref ○, description ○, parameter-bindings ○}`, closed. |
| A converted component definition | `convert_ifa.py`:246-263 → `objects/component/mongodb.json` | 1 component, 3 capabilities, each with `requirement-ref` and `description`. |
| Adoption edge | `Implementation.satisfied-by[].capability-ref`, schema :1185 | `type: string`, no rule reads it. |
| Composition | `validate_core.py`:530-564 | Resolves facet pins; reports one id at two versions and divergent twins. Knows no kind of bundle. |
| Loading in the app | `jascon-app/index.html`:346-351 | A selection with a manifest **replaces** the set; loose files are added. No third path. |
| OSCAL import in the app | `jascon-app/readme.md` "Importing OSCAL" | Catalog and profile. No component definition. |
| OSCAL export | `export_oscal.py` header | Catalog graph only. |

### 2.2 The one component definition in the corpus

`example-component-definition.json` from usnistgov/oscal-content (fictional content by NIST), counted in `converted_examples/US.IFA-GoodRead/ifa-coverage-report.md`:174-198:

| Path under `components[].control-implementations[]` | n |
|---|---:|
| `implemented-requirements[]` | 3 |
| `implemented-requirements[].statements[]` (`statement-id`, `description`) | 2 |
| `implemented-requirements[].set-parameters[]` | 2 |
| `implemented-requirements[].statements[].responsible-roles[]` | 1 |
| `source` | 1 |

So the only measured file carries 2 clause-level entries and 2 suggested parameter values across its 3 recommendations; how they spread over the three was not counted. **Neither kind reaches the bundle** (§12, first item).

### 2.3 Not measured

**Census authorities publishing vendor recommendations: 0 of 3.** They publish catalogs. This is the same structural miss the specification records for Risk (spec :803-818) and CP-CHECK-1 records for Check.

One fictional example file is not a corpus. Before the shape of §4.3 closes, a census of public component definitions is owed: how many implemented requirements carry `statements`, how many `set-parameters`, how many components one file holds, whether `source` names a catalog or a profile. Candidate corpora are to be found and verified first; none has been looked at for this proposal.

### 2.4 The evidence against, from this project's own handbook

Chapter 9.1 cites a professional authoring team that publicly moved its tooling away from component definitions because the complexity exceeded the value (decision register :103, "PR #8"), and D6 unified component definitions and SSP implemented-requirements into one edge for that reason. This proposal does not bring the second model back. A capability stays a **claim**; the only statement that a requirement is met remains the Implementation edge in the user's namespace. What is added is transport and a boundary for claims, not a second place where implementation is described.

## 3. What goes where

| Manifest and kernel (2.0.0) | Tool behaviour, outside |
|---|---|
| a pack header in the content manifest: kind, id, version, publisher | the import dialogue and its preview |
| what a pack may contain (ADVICE-1..3) | where the app shows the pack |
| clause precision on a capability (`statement-ids`) — separable, §4.3 | the diff shown before a release is replaced |
| the grammar of `capability-ref` and what it must resolve to | copying a suggested parameter value into an edge |
| the kept pack manifest in the user's bundle, and the rules that hold it to the objects (ADVICE-8..10) | history of earlier releases |
| what composing a pack into a bundle may touch (ADVICE-11) | |

The line is the same as in CP-CHECK-1: what two tools must agree on is in the left column. Two tools given the same pack and the same set must reach the same answer to *may this be imported*, *is it already there*, and *is what is there still what the vendor published*.

## 4. The shape

### 4.1 The file

An advice pack is **a JASCON bundle whose manifest carries a pack header and whose objects are Components**. Published as one ZIP it is one file; published as a folder over http it is the same pack. Nothing about the bundle format changes: objects, pinned facet schemas, and the vendor's Attestation with its envelope beside the manifest (D3.1).

A bare Component JSON file is not a pack. It carries no release, no publisher and no signature, and a second form would mean a second import path (§11 item 1).

### 4.2 The pack header (content manifest)

```json
"pack": {
  "kind": "advice",
  "id": "https://vendor.example/pack/server-7-hardening",
  "version": "3",
  "title": { "en": "Server 7 hardening advice" },
  "publisher": { "ref": "https://vendor.example/party/vendor", "name": { "en": "Vendor Inc." } }
}
```

| Field | | Type | Meaning |
|---|---|---|---|
| `kind` | ● | code | `advice`. A closed set of one, versioned by process like every code system. |
| `id` | ● | URI | The pack across its releases. String-compared, never resolved (D2). |
| `version` | ● | string | The release. Opaque: no order is computed from it (§4.6). |
| `title` | ○ | text | For people. |
| `publisher` | ● | {ref ● URI, name ○ text} | The party that publishes. A landmark URI, like every party. |

The header sits in the manifest because the manifest is what a signature binds: `content-manifest-digest` is the digest of the manifest's bytes (`jascon-app/assess.html`:140), so vendor and release are inside the signed state without any new mechanism. `provenance` cannot do this job; it is an open object (schema :1588) and nothing can be checked against it.

**Claimed and proven.** The publisher is *claimed* by the header and by the origin its ids share with it (ADVICE-2). It is *proven* when an Attestation beside the manifest has a signer of that origin, binds this manifest's digest, and its envelope verifies under a key the user trusts. These are the two words, and the same envelope check, that the tier rule already uses for a Tailoring (`validate_core.py`:235-297). A tool shows which of the two it is; it never shows a vendor name without it.

### 4.3 A capability gains `statement-ids` *(separable — §11 item 3)*

| Field | | Type | Meaning |
|---|---|---|---|
| `statement-ids` | ○ | [string] | The clauses of `requirement-ref` the recommendation is about. Not allowed without `requirement-ref`. |

A recommendation then has four parts, three of which exist: the requirement (`requirement-ref`), the clauses (`statement-ids`, new), the text for consideration (`description`), and suggested parameter values (`parameter-bindings`). `requirement-ref` stays **resolves-if-present**, as a Mapping endpoint and a Check's `requirement-ref` are: a pack ships without the catalog, which the vendor may have no right to redistribute.

The field name follows Check (`statement-ids`), the nearest sibling shape. Implementation says `statement-refs` and Finding `statement-ref` for the same address; the split exists already and this proposal does not widen it.

### 4.4 `capability-ref` gets a grammar

Today the field is a free string, and the repository writes it four ways (§12). Proposed:

- a bare capability id names a capability **of the edge's own component**;
- `<component-id>#<capability-id>` names a capability of that component.

The second form is how advice is adopted: the user's Implementation, on the user's component, cites the vendor's capability. `inherited-from` is not that — it says another party performs the control under an authorization (D5). A product the user runs is the user's to configure; the vendor only described how.

**The reference is closure-required, so it can always be checked.** The edge's own component is closure-required today (`validate_core.py`:110), which settles the bare form. For the second form the named component must be in the bundle too — the rule `inherited-from` already follows (`validate_core.py`:112-119, "inherited-from component does not resolve in-bundle"). The consequence is the intended one: advice that was not imported cannot be adopted, and a set exported as a bundle carries the vendor's Components and the kept manifest with it. This is unlike a capability's `requirement-ref` (§4.3), which may point at a catalog the bundle does not hold.

### 4.5 What the user's bundle keeps

On import the vendor's objects join the set, and the vendor's manifest is kept **unchanged**, beside the set's own manifest:

```
packs/sha256/<hex>      the vendor's manifest, named by the SHA-256 of its bytes
```

The placement is that of signature envelopes and of the evidence store (`evidence/sha256/<hex>`, CP-CHECK-1 §4.4): beside the manifest, never listed in it. The name is the digest the vendor's Attestation binds, so the chain verifies offline:

```
vendor Attestation ── content-manifest-digest ──▶ packs/sha256/<hex>
packs/sha256/<hex> ── objects[].semantic-digest ──▶ the Components in the set
packs/sha256/<hex> ── pack {id, version, publisher} ──▶ what the tool shows
```

There is no separate import record. The kept manifest *is* the record: it names the vendor, the release and every object that came with it, and it is the thing the vendor signed. A second file with a different name is needed because the app takes any `content-manifest.json` in a selection as the manifest of the bundle (`index.html`:349).

**Which component it applies to** is answered twice, both in the graph. The pack's Components are the vendor's products; that is what the advice is about. Which of the user's systems runs the product is a `members[]` entry on the user's Component, and ADVICE-7 makes it a condition of adopting anything.

### 4.6 Import, and importing again

| The set holds | The file is | Result |
|---|---|---|
| no pack with this `pack.id` | — | Preview, then import: Components added, manifest kept. |
| `packs/sha256/<hex>` of this very file | the same file | Nothing is written. "Already imported: release 3." |
| a kept manifest with this `pack.id`, another digest | another release | Preview with a diff; on confirmation the pack's objects and its kept manifest are replaced. |
| an object with an id from the file that no kept manifest of this pack lists | — | Refused (ADVICE-11). |

Releases are not ordered. `version` is an opaque string, so a tool says *another* release, shows both, and leaves the direction to the user.

The diff before a replacement lists, per Component: capabilities added, removed and changed, and **every Implementation of the set that cites a removed or changed capability**. Replacing a release can leave such an edge pointing at nothing; ADVICE-7 then fails on that edge until the user decides what it should say. The preview says so before anything is written.

### 4.7 What the guarantee is, and what it is not

*Is:* after importing an advice pack, every object that was in the set has the semantic digest it had before, and no Requirement, Set, Tailoring, Mapping, Risk, Check, Implementation, Assessment, Finding or Attestation was added. The first is compared, object by object, and printed as a receipt, of the form `unchanged <n> of <n> · added <m> components`. The second is ADVICE-1. That no resolved Tailoring changed follows from the second and is stated in the receipt as following, not as measured.

*Is not:* a promise that validation output is the same. References that were landmarks now resolve. If the set already held an `inherited-from` edge to a Component the pack brings, and that Component declares an authorization, the boundary rule (D5) fires where it was silent. That is resolves-if-present working as designed, and the preview names such edges.

## 5. The rules

Rules 1–3 hold a pack to being advice; 4–7 hold capabilities and the edges that cite them, in every bundle; 8–10 hold a kept manifest to the set; 11 is import.

| Id | Rule | Rationale | Failure message (abridged) |
|---|---|---|---|
| **ADVICE-1** | Every object a pack's manifest lists is a Component. | The guarantee of §4.7 is this rule. | `<pack>: objects/tailoring/x.json is a tailoring - an advice pack holds components only (ADVICE-1: advice must not be able to change what is required or how it is assessed)` |
| **ADVICE-2** | Every object id, `pack.id` and `pack.publisher.ref` share one origin. | A pack cannot carry an object under someone else's identity, and so cannot replace one. | `<pack>: https://ns.nist.gov/… is not under the pack's origin https://vendor.example` |
| **ADVICE-3** | No facet on a pack's object declares a semantics class. `private:` payloads ride as always. | Advice must not reach a computation through a facet (D10). | `<component>: facet <id> declares modifies-semantics [assessment] - not allowed in an advice pack` |
| **ADVICE-4** | Capability ids are unique within a Component. | A `capability-ref` must name one thing. | `<component>: capability id 'cap-tls' is used twice` |
| **ADVICE-5** | An in-bundle `requirement-ref` of a capability is a Requirement; `statement-ids` name its statements. | The edge is typed when it can be; clause precision is addressable or it is prose. | `<component>#cap-tls: statement-id 's9' names no statement of <req>` |
| **ADVICE-6** | With the requirement in the bundle, each key of a capability's `parameter-bindings` is a parameter declared on the covered clauses, and the value lies in its declared space. | A suggestion the catalog cannot accept is the publisher's defect, found before a user adopts it. | `<component>#cap-tls: binds 'transport-crypto' to 'tls11', outside the declared choices` |
| **ADVICE-7** | A `capability-ref` is a capability id of the edge's component, or `<component-id>#<capability-id>`. The named component is in the bundle (closure-required), the capability exists on it, and a component other than the edge's own is one of its `members`. | An edge that leans on a capability nobody declared proves nothing; and advice applies to a system because the system contains the product, not because a tool says so. One reference hop, as D14 allows. | `<impl>: cites <vendor-component>#cap-tls, but <vendor-component> is not a member of <own-component>` |
| **ADVICE-8** | A file under `packs/sha256/` is named by the SHA-256 of its bytes, is a content manifest with a pack header, and is not listed in the bundle's manifest. | Content addressing is the whole integrity story, as for evidence. | `packs/sha256/2d66…: does not match its name` |
| **ADVICE-9** | Every object a kept pack manifest lists is in the bundle at that version with that semantic digest. | The advice in the set is what the vendor published, or the set says which object is not. | `<component>: differs from release 3 of <pack> (semantic digest) - the vendor's advice was edited after import` |
| **ADVICE-10** | One kept manifest per `pack.id`; no object is listed by two kept manifests. | One release of a pack in a set — the identity rule (one id, one version) said once more at the level of the file. | `<pack>: releases 3 and 4 are both in the bundle` |
| **ADVICE-11** | Composing a pack into a bundle adds ids the bundle does not hold and replaces ids a kept manifest of the same `pack.id` lists. Any other id the bundle already holds is refused. | Import never overwrites what the pack does not own. | `<component>: already in the set and not part of <pack> - remove it or import the pack elsewhere` |

**Notes, not failures:** a capability whose `requirement-ref` is outside the bundle (*not typed*); a pack whose publisher is claimed and not proven; a kept manifest whose vendor Attestation is absent.

Not a rule here: a suggested value outside the space the user's **Tailoring** allows. The vendor cannot know the tailoring. It is shown at adoption and not written, as the profile import treats a `set-parameter` outside the declared space today (`jascon-app/readme.md`, "Importing OSCAL").

## 6. No new type, no new primitive

The count of kernel types and of primitives does not change. ADVICE-5 to -7 are reference and binding checks of the kinds the validator already performs for Check, Implementation and Tailoring. ADVICE-11 extends the composition engine of gate 4 (`compose()`), which already reports one id at two versions and divergent twins; an advice pack is the first case in which a replacement is lawful, and the kept manifest is what makes it decidable.

## 7. Semver: rides 2.0.0

2.0.0 is untagged, so the changes ride it, as Check does. All three are optional additions: a manifest without `pack` is not a pack; a capability without `statement-ids` is valid; every `capability-ref` that is a bare id of its own component stays valid.

**KERNEL-1** extends: a manifest with a pack header, and a bundle that holds a Component with `statement-ids`, must pin `kernel-version: "2.0.0"`. A 1.0.0 tool rejects such a manifest at the manifest, because its manifest shape is closed (schema :1575).

**ADVICE-7 can turn existing content red.** It gives meaning to a string that had none. Of the spellings in §12, the bare ids of the IFA bundle and the full form in the example bundle should pass; whether they do is unmeasured until the rule runs over the five shipped corpus bundles and the example bundle. One case is known without a run: the app writes the literal `"declared"` on every edge of a system it creates, on Components to which it gives no capability (`jascon-app/implement.html`:220-224), so every such edge fails ADVICE-7 until the app writes something else. The run comes before the rule lands, and its result decides whether ADVICE-7 is an error or, for content pinned below 2.0.0, a note.

If these changes do not land before the tag, the manifest and the capability shape are closed at 2.0.0 and a 2.0.0 tool rejects both additions. Which version they then need is a question for the governance of D3.5 and is not answered here.

## 8. D22

No type is promoted, so D22 is not invoked for a type. `statement-ids` on a capability is still a new kernel field, and the three tests are owed for it:

1. **≥ 2 of 3 census authorities encode it:** **fails**, 0 of 3 (§2.3) — the consumer-side miss again, backlog #48.
2. **One shared computation:** holds, and it is not new — resolving a statement id against a requirement, done today for Tailoring operations, Implementation, Finding, Mapping scopes and Check.
3. **One vocabulary without flattening:** holds trivially; the vocabulary is the statement id.

Evidence tier: **one fictional example file** (§2.2). That is thinner than what Check had. The field is therefore written as separable (§11 item 3): the pack, its rules and the import work without it, at the cost that a recommendation addresses a whole requirement.

**The alternative not taken:** let the vendor publish Implementation objects for its own product, which have `statement-refs`, `parameter-bindings` and `status` today and need no schema change. Rejected because an Implementation is the statement that a requirement is met. Importing a vendor's edges would change what the user's set says is implemented, which is the opposite of statement (1), and it is the duplication Chapter 9.1 names: one description of how a requirement is met in a vendor artifact, one in the system's own.

## 9. What ships, what follows

Nothing shipped with the proposal as drafted. Steps 2 to 5 and part of step 8 were built on 2026-11-12 (§13). The order Chapter 15.4 sets:

1. **The author's review** of this text and the decisions of §11.
2. **Corpus first.** `conformance/advice-vectors.json`, at least one red and one green case per rule, among them: a pack with a Tailoring (ADVICE-1); a pack with an object under a foreign origin (ADVICE-2); the same file composed twice, second time a no-op; another release replacing the first, with an edge left dangling; a foreign id collision refused (ADVICE-11); an edited Component under a kept manifest (ADVICE-9); publisher claimed versus proven, with a DSSE envelope.
3. **Schema and reference validator:** `contentManifest.pack`; `capabilities[].statement-ids` with `dependentRequired`; ADVICE-1..11; `compose()` extended; KERNEL-1 extended. Then the run over the shipped bundles (§7).
4. **A worked pack** under `jascon/examples/`, written for the example bundle's own requirements, with an Attestation and envelope, and an Implementation that adopts one capability.
5. **The PowerShell twin**, same vectors, same counts.
6. **Converter:** `convert_cdef.py`, any OSCAL component definition to a pack, carrying `statements[]` to `statement-ids` and `set-parameters` to `parameter-bindings`, with a coverage report; the component-definition part leaves `convert_ifa.py`. Export in `export_oscal.py`, with the round trip compared by semantic digest, as the catalog export does.
7. **The app:**
   - *Import:* a component definition as a third OSCAL kind (`jscOscalKind` already tells the kinds apart).
   - *Home:* a third load path, "add as advice", next to *replace* and *add loose files*; the preview and the receipt of §4.6 and §4.7; the packs of the set listed with publisher, release and claimed or proven.
   - *Implement:* on each of the user's Components, the advice of its member products next to the requirement it addresses; *adopt* writes an Implementation in the user's namespace with `capability-ref` in the full form.
   - *Validate:* ADVICE-1..11 by area.
8. **Handbook and specification** (§10).

## 10. Handbook and specification deltas (places, text after the decisions)

- **SKILL.md**, Requirement 8: capabilities as recommendations; the advice pack; adoption by `capability-ref`.
- **Chapter 9**, new §9.7 "Advice: what a vendor may tell you, and what it may not touch", with the Don't of §9.1 restated for packs.
- **Chapter 11**: the kept pack manifest beside the manifest, next to envelopes and the evidence store.
- **Chapter 13**, §13.4: composing an advice pack — the one lawful replacement.
- **Chapter 14**: the component-definition playbook.
- **Appendix A:** A.5 capability row (`statement-ids`); A.6 `capability-ref`; the manifest shape.
- **Appendix C:** the pack-kind code system.
- **Appendix F:** "Why is a pack not a document model?" and "Why not let the vendor ship Implementations?" (§8).
- **Appendix G:** advice pack · kept pack manifest · claimed and proven publisher.
- **Specification:** D3 (item 8, the pack header), D5 and D6 (capability, `capability-ref`), D15 (the tier of each rule; composition is Portable today), D22 (§8).
- **Website:** the model page, and `oscal-1x-models-and-jascon.md` §4, where "Component Definition → Component.capabilities[]" gains the pack.

## 11. Open points for the author

1. **The file form.** ZIP bundle only (proposed), or a bare Component JSON as a second form. The bare file cannot name a release or carry a signature.
2. **What a pack may hold.** Components only (proposed). Allowing Checks lets a vendor ship ways to assess, against statement (1); Check is itself still proposed. A check pack would be a second `kind`, with its own rules, later.
3. **`statement-ids` on a capability.** With this proposal at rc (proposed), or after the census of §2.3. Without it the kernel schema changes only in the manifest.
4. **Product versions.** A Component has no field for the product version it describes. Proposed: one Component per product line (`…/component/server-7`), with `version` counting the revisions of the advice. The alternative is a field, which needs its own evidence.
5. **ADVICE-3, the facet rule.** Refuse every facet that declares a semantics class (proposed), or let the fail-closed gate handle it at the verb, as for any other bundle.
6. **ADVICE-7, the membership condition.** Proposed as a rule. Dropping it keeps "applies to" a matter of what the tool shows.
7. **Third parties.** A consultancy's advice about a vendor's product is, under ADVICE-2, a Component under the consultancy's origin. How it says *which* product it describes — a `relations` edge, an alias — is not designed here.
8. **Earlier releases.** A set holds one release (ADVICE-10); history is left to whatever versions the set itself is kept in.

## 12. Found on the way (not filed, not fixed)

- **The IFA coverage report claims more than the converter carries.** `ifa-coverage-report.md`:177-181 lists `set-parameters` (×2), `statements[].description` (×2) and `statements[].statement-id` (×2) as L1, "capabilities with requirement-ref". `convert_ifa.py`:250-254 reads `control-id` and `description` of an implemented requirement and nothing below it, and `objects/component/mongodb.json` carries neither a binding nor clause text. The claim comes from one regex over the whole `control-implementations[]` subtree (`convert_ifa.py`:560). The same converter writes `requirement-ref` into the NIST namespace without reading the `source` of the control implementation (:253). **The converter has to change either way:** `set-parameters` fit `parameter-bindings` today, with no schema change; the clause-level text needs §4.3; and the claim table must stop counting what is not carried, whatever §11 item 3 decides. None of it can be done from a checkout alone: the converter reads `sources/nist/`, which is git-ignored and absent here, and its output, the report and the manifest digests change together. It is step 6 of §9.
- **Appendix A.5 omitted `requirement-ref` of a capability**, which the schema has (:1097) and the IFA bundle uses. *Fixed 2026-11-12 in `jascon/references/appendix-a-shapes.md`; `SKILL_jascon.zip` still holds the old text until it is rebuilt.*
- **`capability-ref` is written four ways:** a full URI with fragment (`examples/implementation-acme-konf.json`:13), bare ids (four references on three edges of the IFA bundle), the literal `"declared"` the app writes on the edges of a system it creates, whose Components it gives no capability (`jascon-app/implement.html`:220-224), and `"cap"` in validator fixtures. No rule reads the field in `validate_core.py`.

## 13. Landing addendum (2026-11-12) — what was built, and what contact with the repository changed

### 13.1 What is in the repository, green in both implementations

| Artifact | Change |
|---|---|
| `schemas/jascon-2.0.0.schema.json` | `contentManifest.pack` (closed: `kind`, `id`, `version`, `title`, `publisher {ref, name}`); `capabilities[].statement-ids` |
| `scripts/validate_core.py` | ADVICE-1..11 (`pack_errors`, `capability_errors`, `capability_ref_errors`, `kept_pack_errors`, `compose_advice`), `pack_publisher` (claimed or proven), KERNEL-1 extended, attestations beside a pack's manifest are read, `run_advice`, the default run takes every folder under `jascon/example-packs/`, `--import-advice SET PACK` prints the plan and the receipt and writes nothing |
| `scripts/validate_core.ps1` | the same rules and the same harness; not the `--import-advice` dry run |
| `conformance/advice-vectors.json` | **71 vectors**: 9 shape, 12 pack, 21 graph, 11 kept manifest, 8 publisher, 10 import |
| `example-packs/dbvendor-server-7-advice/` | the file a vendor publishes: pack header, one Component with three capabilities, Attestation and DSSE envelope beside the manifest |
| `examples/` | the set after the import: the vendor's Component byte for byte, the kept manifest under `packs/sha256/`, the vendor's Attestation and envelope, the product as a member of `acme-saas`, one Implementation that adopts `cap-key-rotation` |
| `references/`, `SKILL.md`, `examples/README_1.md` | Chapter 9.7 (new), 11.2, 13.4, 14.3; Appendix A.5, A.6, A.11; C.10; F Q24 and Q25; G; SKILL Requirement 8a |
| `website/` | a card on the model page, the OSCAL row, a gate and a limit on the evidence page, a gate on the home page; `build.py --measure` reads the worked pack and copies it to the site; `facts.json` re-measured |
| `drafts/cp-advice-1/` | `author_vectors.py` (writes the vectors), `build_example.py` (writes the pack and the example set; a second run changes nothing), `mutate.py`, `fix_ifa_capability_ref.py`, `regen_app_schema.py` |
| `.gitattributes` | the pack, the kept manifest and the envelopes are `-text` |

**Measured on 2026-11-12, one machine, before the merge with `main`:** `validate_core.py` — 486 of 486 vectors in 17 families (`advice: 71`), the five corpus bundles, the worked pack and the example folder, ALL GREEN. `validate_core.ps1` on Windows PowerShell 5.1 — the same 486 vectors and, bundle by bundle, the same pass counts (1,712 · 814 · 136 · 18 · 1,040 · pack 2 · examples 27), ALL GREEN, 191 s. The counts after the merge are in §13.4. Both report the pack's publisher *proven*; with the fixture key as trusted key the reference validator reports the signature verified.

**Mutations.** 28 deliberate defects, put into the reference validator one at a time, each turn at least one advice vector red (`mutate.py`). Three further guards are not counted: removing them crashes the code behind them, which is not a verdict.

**The signing key of the worked pack is the corpus fixture key**, whose seed is public (`dsse-vectors.json`). The signature shows the mechanism and says nothing about a vendor.

### 13.2 What contact with the repository changed

1. **ADVICE-7 found a defect in a shipped bundle, as §7 said it might.** `impl/saas-ac-2` of the IFA bundle cited the bare id `cap-consumer-ac-2a`. Its own component, `saas`, declares no capability; the capability is declared by `access-control-appliance`, a member of `saas`. That is exactly the case the full form exists for, so the edge now reads `<appliance-id>#cap-consumer-ac-2a`, and `convert_ifa.py` writes it that way. The converter could not be re-run (its sources are git-ignored), so `fix_ifa_capability_ref.py` makes the one change and proves it is the converter's bytes: it first re-serialises the object and the manifest the way the converter's writer does and requires byte identity with the files on disk. The edge is no subject of the bundle's Attestation, so nothing else moved. **ADVICE-7 stays an error.** All other references in the shipped bundles and the example bundle passed unchanged.
2. **`statement-ids` without `requirement-ref` is a graph rule, not a schema keyword.** §9 item 3 said `dependentRequired`. It is part of ADVICE-5 instead, so that no implementation's schema subset has to grow a keyword for one rule.
3. **The published pack is not inside `jascon/examples/`.** It is `jascon/example-packs/<name>/`, a bundle folder of its own. A second `content-manifest.json` inside the example folder would be read by the app as the manifest of that folder (§4.5). §9 item 4 is corrected by this.
4. **An Attestation beside a pack's manifest had no reader.** In a bundle folder the validators loaded listed objects only, and ADVICE-1 forbids a pack to list its Attestation. For a pack, both now read the JSON files of the manifest's own folder that it does not list and that type as an Attestation.
5. **The receipt does not recompute a Tailoring.** It prints how many objects of the set are untouched and that only Components were added; that no resolved Tailoring changed follows from ADVICE-1 and is said to follow, as §4.7 has it.
6. **A facet key carries its major line.** The schema requires `@<n>` on every facet key, `private:` ones included; ADVICE-3 skips keys that start with `private:`.

### 13.3 What does not exist

- **The app does not read packs.** No import path, no preview, no adoption, no ADVICE rule in its port. Only `jascon-app/jascon-schema.js` was regenerated, by `regen_app_schema.py`, which stands in for `tools/gen-schema.mjs` and first proves it reproduces the committed file from the committed schemas byte for byte. **No app test was run:** the machine has no Node. Read from the code and not tried: the app keeps text files and the evidence store when it loads a folder (`jascon-core.js`, `jscKeepFiles`), so a set that goes through the app loses `packs/sha256/`. No rule fails then: the kept manifest is simply gone, and with it the record of the import.
- **No converter.** `convert_cdef.py` and the component-definition export are not written. The IFA conversion still drops clause-level text and suggested values, and its coverage report still counts them as carried (§12).
- **No census** of public component definitions (§2.3). The evidence for `statement-ids` is still one fictional file.
- **No specification text** (D3, D5, D6, D15, D22) and no change to the reader.
- **`SKILL_jascon.zip`** was not rebuilt on the branch: at that time the archive was held at the state before CP-CHECK-1. That changed on `main` the same day; see §13.4.
- **The findings of §12 are not filed in the backlog.**

### 13.4 After the merge with `main` (2026-11-12)

While this branch was written, `main` moved to **2.0.0-rc.2**: Check was accepted into the candidate with six author decisions, D22 gained a consumer-side clause (backlog #48 closed), a twelfth comparator and per-resource counts came in, and the specification draft was renamed to `jascon-specification-2.0.0-rc.2.md`. The branch was merged with that state. Four files conflicted — two generated (`jascon-schema.js`, `facts.json`; regenerated and re-measured) and two hand-written (`examples/README_1.md`, `website/src/evidence.html`; both sides kept).

**Measured on the merged tree, one machine:** `validate_core.py` — 518 of 518 vectors in 17 families (`check: 188`, `advice: 71`), the five corpus bundles, the worked pack and the example folder, ALL GREEN. `validate_core.ps1` on Windows PowerShell 5.1 — the same 518 vectors and, bundle by bundle, the same pass counts (1,712 · 814 · 136 · 18 · 1,040 · pack 2 · examples 27), ALL GREEN, 184 s. The 28 mutations are caught as before, the vectors and the worked example come out byte-identical from their scripts, and the site builds.

**A by-product for backlog #60.** That item says the twin's port of `not-equals`, the per-resource counts and the surrogate rule "have never run". They ran in the two runs above: `check: 188 pass, 0 fail`, and the example folder with its two Checks green. The item is not closed here; whether this run settles it is its owner's call.

What the merge makes of earlier sections:

- **§8 and §2.3, D22.** Backlog #48 is closed by the consumer-side clause (D22 rev 4): data that catalogue authorities do not publish may enter the kernel when a recognised standard requires the record, or when it is established practice shown by at least two independent open implementations whose content was counted — with tests 2 and 3 in force and on a major. The clause is written for *types*; this proposal adds a field and a manifest header, and no type. Read for the field all the same, it is **not met**: no standard is named here, and the counted content is one fictional file, where the clause asks for two implementations. The census of §2.3 is what could change that. `statement-ids` therefore stays separable (§11 item 3).
- **§11 item 2.** "Check is itself still proposed" no longer holds: Check is in the 2.0.0 candidate. The recommendation stands for its other reason — a vendor shipping Checks ships ways to assess.
- **Line references into the specification** (§2.3, §8) name `jascon-specification-2.0.0-rc.1.md`, which is now `-rc.2.md`; the lines moved.
- **`SKILL_jascon.zip`.** `main` rebuilt the archive with Check in it. Compared entry by entry, the archive of that commit is exactly the 103 files git tracks under `jascon/`, as blobs. With the rule known, the archive is rebuilt from the merged tree by `drafts/cp-advice-1/build_skill_zip.py`, which makes that comparison first and writes nothing if it fails. The archive now carries the advice pack, its vectors and the handbook text, marked proposed as in the tree.
- **The website** no longer calls Check proposed. The advice pack is the one entry under "Proposed" on the model page, and its limit on the evidence page is worded against the consumer-side clause.

## 14. The author's decisions (2026-11-12) — accepted for 2.0.0

### 14.1 The eight points of §11

| # | Point | Decision | Effect on the proposal |
|---|---|---|---|
| 1 | The file form | **"Bundle only"** | As proposed |
| 2 | What a pack may hold | **"Components only"** | As proposed |
| 3 | `statement-ids` | **"Keep it, I overrule D22 because I see great use for it"** | In 2.0.0. Recorded in D22 as entered on the author's word; the census of §2.3 is still not run |
| 4 | Product versions | **"A product-version field"**, shape **"One opaque string"** | New: `Component.product-version`. The proposal had recommended one Component per product line and no field |
| 5 | ADVICE-3 | **"Refuse them in a pack"** | As proposed |
| 6 | ADVICE-7 | **"Yes, a rule"** | As proposed |
| 7 | Third parties | **"A named relation, defined now"** | New: stdlib relation type `https://ns.jascon.net/stdlib/relation/describes` |
| 8 | Earlier releases | **"One release per set"** | As proposed |

### 14.2 What changed in the repository

- **`product-version`.** Schema: an optional non-empty string on a Component. KERNEL-1: a Component that carries it needs kernel 2.0.0. No rule reads the value. The worked pack's Component says `"product-version": "7"`; its digest, both manifests, the kept manifest and the Attestation were regenerated.
- **`describes`.** No schema change: `relations[].type` is the extensible code surface (handbook C.8). Two vectors show a third party's pack about a vendor's product, valid under its own origin and refused (ADVICE-2) under the vendor's.
- **Vectors.** 71 → **74** (pack 12 → 15).
- **Specification.** D25 is the decision; D3 item 8 the pack header and the kept manifest; D5 the two fields; D6 the grammar of `capability-ref`; D15 the rules in the matrix; D22 the override; III.7 the worked example.
- **Measured:** `validate_core.py` 537 of 537 vectors in 17 families, ALL GREEN; 28 of 28 mutations caught. `validate_core.ps1` on Windows PowerShell 5.1, a hosted runner of GitHub Actions: the same 537 vectors and the same bundle counts, ALL GREEN, 64 s (backlog #63, closed; https://github.com/christoph-puppe/JASCON/actions/runs/43204019670).

### 14.3 What §13.3 said does not exist, now

- **The app and the reader**: built on 2026-11-12 (app build 0.9.3, reader v1.9.0). The app ports ADVICE-1 to ADVICE-11 and passes all 74 vectors; it imports a pack from a folder, a ZIP or a URL after a preview and prints the receipt of §4.7; another release shows the capabilities added, removed and changed and the edges of the set that lose their target; adoption on the Implement page writes the full form of §4.4; `packs/sha256/` survives load and export, which §13.3 had found it would not. The literal `"declared"` of §12 is no longer written; sets written by earlier builds keep it until they are saved again, and Validate names each such edge. The reader shows the pack header, kept manifests and `product-version` and runs no ADVICE rule.
- **Claimed, attested, proven.** §4.2 has two words. Building the app showed that two are one too few for a screen: an Attestation that binds the manifest, with no trusted key to check its signature, is neither a bare claim nor proof, and anyone can write one. The validators keep the two result values and print such a case as ATTESTED, NOT VERIFIED; the app shows three states (specification D25).
- **A defect in the reference, found by the app's port:** for a bundle folder that keeps a pack, `validate_core.py` and the twin read no attestation beside the manifest and reported the kept pack's publisher as claimed; the example folder, read file by file, was reported correctly. Both read it now.
- **Choices the app made that the proposal does not settle**, for the author to confirm or overturn: (1) a pack loaded from a URL finds its attestation, and a set its kept manifests, only where the server lists the folder, because a manifest names neither; the website writes such listings for its example folders; (2) the import also refuses a pack whose files do not match its own manifest, a pack without the kernel pin, and a pinned facet schema the set holds at another version; (3) a suggested value is offered for adoption only if it lies in the declared space and on the tight side of what a Tailoring in force binds, otherwise it is shown with the reason and not written; (4) adoption amends an existing edge of the same component, requirement and clauses, and writes a new edge otherwise.
- **No converter, no census**: unchanged. The findings of §12 on `convert_ifa.py` are filed as backlog #64.
- **Specification text**: written (rc.3).
- **`SKILL_jascon.zip`**: rebuilt from the tree of this state.
