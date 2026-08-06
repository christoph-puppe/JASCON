# The JASCON Handbook
## Part Three — Implementation and Assurance
# Chapter 11 — Integrity, Attestation, and Air-Gaps

**Audience:** [A][C] — publishers and toolsmiths who must *deliver*
verifiable bundles, and the authorizing officials, assessors, and
agencies who must decide what a signature actually proved. §11.5 is
written for the person holding the pen.
**Companions:** Specification v0.5 — D3, D7, D18, D15; Appendix A
(content-manifest shape); the stdlib DSSE profile.

---

## 11.0 The task

Two chairs again, one package between them.

In the first chair: an authorizing official with a rendered
authorization document and a signing ceremony scheduled. The question
is brutally practical — *what exactly does my signature bind, and if
this package was altered somewhere between the assessor and me, would
anything tell us?*

In the second chair: an engineer who must move that package across a
data diode into a network that has no network — no DNS, no registry,
no "just fetch the schema" — and have **everything** verify on the
other side.

The task of this chapter is one artifact that satisfies both chairs: a
bundle whose integrity is checkable offline, whose meaning is
distinguishable from its packaging, and whose signature connects — 
cryptographically, not ceremonially — to every object this book has
built since Chapter 2.

## 11.1 Two digests, two jobs

Why not one digest per object and be done? Because two legitimate
rights point in opposite directions, and the specification's review
history proved that any single digest betrays one of them.

Chapter 7 granted tools the right to **strip annotations** in transit —
they are chrome, by definition, and hygiene demands they be removable.
But one hostile review demonstrated the forgery this enables if
annotations therefore escape the digest: an attacker edits a
rendering-steering annotation en route, the renderer produces a
compromised document, the official signs it — and verification passes,
because the hasher never saw what changed. The mirror review proved the
opposite trap: include annotations in the one digest, and every
legitimate strip shatters every signature. One digest cannot serve both
masters. So there are two, with two jobs:

**`package-digest`** — SHA-256 over the delivered bytes, annotations
and all. It answers *"is this the parcel that was sent?"* — transport
and packaging integrity, checked by the `digest-verified` primitive at
every tier including Core.

**`semantic-digest`** — SHA-256 over the canonicalized object *with
annotations removed*. It answers *"is this the meaning that was
approved?"* — stable across re-serialization, annotation hygiene, and
repackaging, and it is what attestations bind as their subjects.

Canonicalization is RFC 8785 (JCS) with two determinism guards the
conformance corpus tests explicitly, because each was a reviewer-found
fragmentation vector: **empty-omission** — structurally optional
arrays and objects with zero elements MUST be omitted before JCS, so
Tool A's `"aliases": []` and Tool B's omitted field hash identically —
and **decimal-as-canonical-string**, so no IEEE float representation
ever leaks into a hash.

> **Don't** improvise integrity by hashing files ad hoc. The failure
> this prevents came out of the design's own cross-examination: byte
> hashes shatter on legitimate re-serialization, semantic-only hashes
> license the annotation forgery, and undefined empty-versus-omitted
> handling silently forks digests between honest tools. The two
> domains plus the JCS guards are the minimal set that survived.

## 11.2 The content manifest: the bundle's table of truth

Every bundle carries one:

```json
{ "manifest-version": "1",
  "objects": [
    { "id": "https://cso.example/component/acme-saas",
      "version": "2026-07",
      "package-digest":  "sha256:…",
      "semantic-digest": "sha256:…",
      "path": "objects/acme-saas.json" }, … ],
  "facet-schemas": [
    { "id": "https://ns.bsi.bund.de/facet/gspp-taxonomy",
      "exact-version": "1.0.0", "digest": "sha256:…",
      "path": "schemas/gspp-taxonomy-1.0.0.json" } ],
  "renderings": [ { "path": "render/authorization.pdf",
                    "digest": "sha256:…" } ] }
```

Three roles in one file. It is the **local resolution table** — every
reference in the bundle resolves here, which is what makes sealed mode
possible at all. It is the **integrity ledger** — both digests per
object, plus digests for every rendering. And it is the **trust
anchor for extensions** — facet schemas pinned at exact version *and*
digest, Chapter 7's "trust is the pin, not the URL" made concrete
(composition of two bundles pinning different minors of one facet line
resolves deterministically to the highest pinned minor, both payload
sets re-validated — the semver promise doing its job).

And one structural rule that a reviewer's proof made non-negotiable:
**attestations and their signature envelopes are excluded from the
content manifest by definition.** Put the signature inside the
manifest and you need the manifest's digest inside the signature —
which depends on the signature's bytes — which contain the manifest's
digest: no fixed point exists. The resolution is a sentence worth
memorizing: *nothing signed contains its own signature.* Attestations
live beside the content manifest; a transport wrapper may list both,
but it is never the signed structure.

## 11.3 Sealed mode, end to end

"Sealed" is not a deployment option; it is a **Core conformance
requirement** — every validator must be able to run the following with
the network cable cut, and the reason is both principled and measured:
air-gapped estates are the daily reality of the largest prospective
consumers, and Chapter 3's cautionary tale (the national extension
registry that vanished with its repository) is what network-coupled
trust looks like in the wild.

The verifier's walk, offline: open the bundle; read the manifest;
verify every object's **package-digest** against its bytes; resolve
every reference **through the manifest** (`references-resolve` — a
reference with no manifest entry fails, with a printed reason);
validate every facet payload against its **pinned schema from inside
the bundle**; then, at Portable tier, compute semantic digests and run
the semantic rules. Not one DNS query in the sequence. Your
`.well-known` endpoint can be down for a week — not a single
validation anywhere changes its answer.

## 11.4 The Attestation: binding meaning to paper

Compliance ends with a human signing a document, and courts subpoena
the exact view. The Attestation is the object that makes "what the
machine validated" and "what the official signed" permanently
inseparable:

```json
{ "id": "https://agency-x.example/attestation/acme-ato-2026",
  "subject-semantic-digests": ["sha256:…", "sha256:…"],
  "content-manifest-digest": "sha256:…",
  "rendering": { "artifact-digest": "sha256:…",
                 "media-type": "application/pdf",
                 "template-ref": { "id": "…/template/ato-package",
                                   "version": "2.1.0", "digest": "sha256:…" },
                 "renderer": "…/tool/render-engine@3.4" },
  "signer": "https://agency-x.example/party/ao",
  "timestamp": "2026-07-18T14:00:00Z",
  "envelope-ref": "envelopes/acme-ato-2026.dsse" }
```

Three bindings, three questions answered. The
**subject-semantic-digests** pin *what was approved* — the meaning of
each subject object, immune to repackaging. The
**content-manifest-digest** pins *the exact package state at signing*
— and because the manifest carries every object's package-digest,
annotations included, this is the binding that closes the in-transit
annotation swap from §11.1. The **rendering block** pins *which paper*
— artifact digest, plus a template reference pinned by version and
digest, plus the named renderer, because the renderer is part of the
trusted computing base and the template pin is how you audit it. The
accompanying conformance rule has teeth: annotations may influence
only non-normative chrome, and **a template that reads annotations
into normative content is non-conformant** — which is what lets §11.5
reason cleanly about what a packaging change can and cannot have
touched.

The optional **provenance map** (statement-id → rendering anchor) is
the assessor's gift: *show me the paragraph that renders clause s2* —
answered by lookup, not by reading the whole document.

## 11.5 Bi-modal verification: what each state proves

Verification of an attested bundle lands in exactly one of two green
states — and the person holding the pen should know both cold.

**Full Match.** Signature valid; content-manifest digest matches the
delivered bundle. Proven: *the meaning, the packaging, and the
presentation are exactly as signed* — byte-identical package state.
This is the state for submission, archive, and evidence lockers.

**Semantic Match.** Signature valid; every subject's semantic digest
matches; the content-manifest digest does **not**. Proven: *the
compliance content is exactly as approved; the packaging changed in
transit.* The everyday cause is legitimate: a tool stripped
tool-tracker annotations, a bundle was re-assembled. Conformant tools
MUST report this state as itself — never as failure, never silently
promoted to Full. For the assessor, a Semantic Match is not an alarm
but an information with one follow-up question — *who repackaged, and
why?* — whose answer lives in the transport chain, not in the content.
And the two mechanisms interlock precisely here: because templates may
read only chrome from annotations, a packaging-only delta provably
*cannot* have altered what the normative rendering said — the forgery
of §11.1 has no state to hide in: it breaks Full and gains nothing.

Everything else — bad signature, missing subjects, unverifiable
envelope — is failure, with the DSSE profile (next) defining exactly
what "verifiable" means.

## 11.6 The DSSE-profile checklist

The signature envelope format lives in the stdlib as a DSSE profile,
and the profile is normative about seven questions. They double as the
acceptance checklist for anyone *receiving* an attested package — and
as the build sheet for anyone producing one:

*Where is the envelope?* (`envelope-ref`, resolvable in the bundle's
transport wrapper.) *Exactly which digest set is signed?* (The
attestation's three bindings — no ambiguity about bytes-versus-
canonical.) *In what format is the signer's identity expressed?*
*How are trust roots expressed and distributed* — sealed environments
included? *What timestamps exist*, and is a trusted timestamp among
them? *How are expiry and revocation handled* — what does this
signature mean in five years? *Are all subjects present in the bundle*
— the completeness check that stops an attestation from quietly
referencing objects you were never given?

> **Don't** accept a signature whose seven answers you cannot state. A
> signature without a stated envelope location, digest set, identity
> format, trust root, time basis, revocation story, and completeness
> check is decoration with mathematics-flavored confidence — the
> profile exists so that "it's signed" is a claim with contents.

## 11.7 Through the diode: the transit projection

Guarded cross-domain gateways — the hardware on defense air-gaps —
often inspect XML against strict XSDs and nothing else. The stdlib's
answer is `transit-projection@1`: a deterministic, **one-way**
JSON→XML projection (canonical JCS ordering becomes element order;
prose transits as text content, no markup mapping), positioned exactly
like an encoding — never an authoring format, never 1.x XML, no
reverse direction within conformance scope.

Its honesty clause matters operationally. A strict XSD is
**guaranteed only for the kernel and the stdlib facets**, which are
authored in a transit-safe schema subset for exactly this reason —
arbitrary JSON Schema constructs (`anyOf`, `not`) have no faithful XSD
image, and a projection that degraded them to `xs:any` would hand the
guard a wrapper around opacity. Third-party facets therefore project
as opaque payloads *unless their publisher ships a mapped XSD*. Stated
plainly, as the specification's risk register does: deep inspection
covers kernel plus stdlib; third-party facet transit is
guard-policy-dependent. If your deployment crosses a diode, that
sentence is your agenda for two conversations — one with the guard's
policy owner, one with each facet publisher whose payloads must be
inspectable rather than opaque.

## 11.8 One run, both chairs satisfied

Close the loop on the package this Part has been building. The
Chapter 9 chain and Chapter 10 findings are bundled; the manifest
lists every object with both digests and pins the German taxonomy
facet at 1.0.0; the AO's attestation binds subjects, manifest, and the
rendered PDF via its pinned template; the DSSE envelope answers its
seven questions. In transit, a hygiene tool strips the `tracker`
annotations: on arrival, verification reports **Semantic Match** —
compliance content proven, packaging changed, transport chain asked
one polite question. In the counterfactual where someone instead edits
`web_name` hoping to steer the rendering: the package digests diverge,
Full is unreachable, and the template rule guarantees the tampering
could not have reached normative content anyway. Both chairs got what
they sat down for — offline.

That completes Part Three: content authored, systems composed, claims
assessed, imperfection channeled, and the whole edifice bound to paper
a court can trust. Part Four changes the reader: now *you* are the one
writing the validator. Chapter 12 builds it tier by tier — Core in a
weekend is the design target, and per this book's evidence rule, the
measured lines-of-code and contributor-hours arrive with the v0.6
executable gate; until then the chapter teaches the walk and labels
every number that is still a promise.
