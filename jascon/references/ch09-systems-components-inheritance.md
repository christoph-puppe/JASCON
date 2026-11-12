# The JASCON Handbook
## Part Three — Implementation and Assurance
# Chapter 9 — Systems, Components, and Inheritance

**Audience:** [A][C] — providers who publish what their platforms do,
and the agencies and assessors who must decide whether to believe them.
Both seats get explicit time; the worked chain in §9.5 serves both.
**Companions:** Specification v0.5 — D5, D6, Appendix A (Component and
Implementation shapes); `system-context@1` in the stdlib catalog.

---

## 9.0 The task

You run a SaaS. It runs on somebody's PaaS, which runs on somebody
else's IaaS. An agency wants your authorization — and, as in every real
cloud stack, the majority of your controls are ones you do not perform
yourself: physical security, hypervisor hardening, network fabric, all
"inherited" from below, with the remainder split between you and your
customer clause by clause.

The task is to encode that reality so three things become *checkable*
instead of asserted: that every inheritance claim rests on a **named,
legitimate basis**; that responsibility is divided at the granularity
where it actually divides — the clause; and that the **liability
perimeters** — the boundaries where an authorizing official's signature
attaches — are explicit data, not diagram folklore. And for the reader
in the assessor's seat: what, exactly, you are now entitled to demand
when a provider hands you a chain like this.

## 9.1 One type to rule the stack: why System died

The old world kept two ontologies — Systems (the thing you authorize)
and Components (the things systems are made of) — plus two parallel
constructs for saying how requirements get met: component definitions
on the vendor side, implemented-requirements inside the SSP on the
system side. The stack you are encoding makes the duality absurd in one
sentence: **your system is my component.** The PaaS is a bounded,
authorized *system* to its operator and a *building block* to you — the
same object, wearing two hats, and any model that forces it into one
type per hat forces somebody to maintain a duplicate.

The field data on that duplication is unusually direct. A professional
compliance-authoring team publicly migrated its tooling *away* from
component definitions because the model's complexity exceeded its value
— the retreat is on the record in their repository history. And the
decade before that, the old flagship program encoded exactly the
missing semantics as annotation: the *historical* Rev4 extension
registry carried `implementation-status` and `control-origination`
props whose enum (sp-corporate, sp-system, customer-configured,
customer-provided, inherited) maps one-to-one onto the typed fields you
are about to meet — ten years of props standing in for fields.

So JASCON has one type:

```json
{ "id": "https://cso.example/component/acme-saas",
  "kind": "service",
  "members": [ { "component-ref": "https://paas.example/component/platform",
                 "context": "runtime" } ],
  "capabilities": [ { "id": "cap-encrypt-transit",
      "description": "TLS termination for all tenant traffic",
      "parameter-bindings": { "transport-crypto": "tls13" } } ] }
```

`kind` spans the whole vocabulary — system, service, software,
hardware, policy, process — because a paper policy satisfies
requirements the same way a load balancer does: through the same edge
(§9.3). `members` is composition, with a free-text `context` for the
role. `capabilities` are what component definitions always wanted to
be: the things this component *can do for requirements*, published
once, referenced by every implementation that leans on them.

> **Don't** maintain two descriptions of how a requirement is met — one
> in a vendor artifact, one in a system plan. The failure this
> prevents is measured in the field: a specialist team's public retreat
> from the duplicated model, and a decade of historical
> `control-origination` props re-encoding by hand what one typed edge
> now states once.

## 9.2 Authorization contexts: explicit, identified, scoped

Where, in this one-type world, did the *authorization boundary* go — 
the legal line an AO's signature attaches to? It became explicit data
on the component that holds the perimeter:

```json
"authorizations": [
  { "id": "https://iaas.example/auth/jab-high-2026",
    "authority-ref": "https://ns.fedramp.gov/party/jab",
    "scope-label": "FedRAMP High P-ATO",
    "includes": [ {"component-ref": "…/component/compute-fabric"},
                  {"component-ref": "…/component/object-store"} ] },
  { "id": "https://iaas.example/auth/agency-x-ato",
    "authority-ref": "https://agency-x.example/party/ciso",
    "scope-label": "Agency X ATO (limited services)" } ]
```

Read the design off the example. Each context is an **identified
object** — Chapter 3 discipline applies, because inheritance edges will
cite these ids by name. **Plural is the normal case**: a real platform
holds a JAB P-ATO *and* several agency ATOs simultaneously, and a
model with one boundary slot would be lying by omission. `includes[]`
scopes which members fall inside a given perimeter (default: the whole
composition) — because "authorized" and "sold" are rarely the same
list.

And one rule the specification's own review history paid for twice:
**absence asserts nothing.** An early design used a boundary boolean; a
later one made it default-false; both died, because a component that
simply hasn't declared its contexts must not thereby be making the
legally significant claim "no authorization exists here." Silence is
silence. The honest cost rides along as a named risk in the
specification: a component that *hides* a real authorization evades the
boundary trigger you are about to meet — kernel mathematics cannot
force candor. What polices it is the Authority tier's publication
duties and, bluntly, the assessor's seat: §9.5 ends with exactly the
questions that flush hidden perimeters out.

## 9.3 The Implementation edge: responsibility, clause by clause

One relation carries the entire "how requirements get met" story:

```json
{ "component-ref": "https://cso.example/component/acme-saas",
  "requirement-ref": "https://ns.bsi.bund.de/gspp/req/KONF.14.1",
  "statement-refs": ["s1"],
  "responsibility": "shared",
  "satisfied-by": [
    { "capability-ref": "https://cso.example/component/acme-saas#cap-encrypt-transit" },
    { "inherited-from": {
        "component-ref": "https://paas.example/component/platform",
        "basis-ref": "https://paas.example/auth/jab-moderate-2026" } } ],
  "parameter-bindings": { "transport-crypto": "tls13" },
  "status": "implemented",
  "evidence-refs": ["…"],
  "deviations": [] }
```

Walk the fields with both seats in mind. **`statement-refs`** is the
quiet revolution: shared responsibility is *clause-shaped* — the
provider encrypts (statement s1), the customer configures key rotation
(statement s2) — and Chapter 4's statement identifiers are what let one
requirement carry two edges with two owners instead of one blurred
paragraph. This is the implementation-side mirror of the authoring-side
`obligated-parties`: the author said *who is bound*; the edge says *who
actually does it here*. **`responsibility`** (provider | customer |
shared) plus those clause refs turns the customer responsibility
matrix from a PDF appendix into **queryable edges** — an agency can ask
"show me every shared clause where no customer-side edge exists" and
get an answer instead of a reading assignment. **`parameter-bindings`**
records the choices Chapter 4 parameterized: this deployment picked
`tls13`, auditable against the declared choice set and, via Chapter 6,
against any tailoring's tightening rules. **`satisfied-by`** lists the
mechanisms — own capabilities and inherited ones — and its
`inherited-from` entries carry the field the next section is entirely
about. **`deviations`** attach here too: an approved risk adjustment on
one clause of one system is exactly this object plus one Chapter 6
record, visible where it applies.

## 9.4 The boundary rule: edge-local, inductive, one hop

Here is the entire inheritance law of JASCON, and it fits in
one sentence:

> **Every `inherited-from` edge whose target component declares any
> authorization MUST carry a `basis-ref` naming the specific
> authorization context it leans on.**

Mechanically it is one `conditional-apply` instance — trigger:
the target (one reference hop from the edge) has `authorizations`
present; enforcement: the edge has `basis-ref` present — with the
standard rationale-on-failure, so a violation names itself at two in
the morning.

Three design choices hide in that sentence, each answering an objection
the specification's reviews actually raised.

**Why one hop suffices: induction.** A hostile review objected that a
one-hop rule cannot police a SaaS→PaaS→IaaS chain. The answer was
redesign, not concession: the rule is *edge-local*, and every link in
the chain is somebody's edge. The SaaS's edge to the PaaS is checked at
that edge; the PaaS's edge to the IaaS is checked at *that* edge; the
chain is covered link by link, by induction, and no rule ever needs to
traverse a graph — which is also why the primitive layer's one-hop
budget survived intact.

**Why laundering fails.** Suppose the PaaS tried to "wash" its IaaS
inheritance — absorb it quietly and re-export the controls as its own.
The wash happens *at the PaaS's own edges*, and those edges point at a
component (the IaaS) that declares an authorization: trigger fires,
basis required, the launderer is caught at the launderer's own link.

**Why the basis names an id, not a yes.** Because §9.2's plural is
real: the platform below you holds a JAB P-ATO *and* agency ATOs with
different scopes. "I inherit from that platform" is not yet a claim; "I
inherit under *that* authorization" is — and it is checkable against
the context's `includes[]` scope.

> **Don't** accept — or publish — inheritance without a named basis.
> The failure this prevents is the oldest trick in shared-
> infrastructure compliance: authority laundering, where controls
> performed under one perimeter are silently re-sold as satisfied under
> another. Here the claim without its basis is not weak; it is a
> validation error with a printed reason.

## 9.5 Worked: the full chain

Three components, bottom up — heavily abridged, the shape is the point:

```json
{ "id": "https://iaas.example/component/cloud",
  "kind": "system",
  "authorizations": [ { "id": "https://iaas.example/auth/jab-high-2026", "…": "…" } ] }

{ "id": "https://paas.example/component/platform",
  "kind": "system",
  "members": [ { "component-ref": "https://iaas.example/component/cloud" } ],
  "authorizations": [ { "id": "https://paas.example/auth/jab-moderate-2026", "…": "…" } ] }
  // PaaS implementation edges for physical/fabric requirements:
  //   satisfied-by: inherited-from{ …/component/cloud,
  //                 basis-ref: …/auth/jab-high-2026 }   ← checked HERE

{ "id": "https://cso.example/component/acme-saas",
  "kind": "service",
  "members": [ { "component-ref": "https://paas.example/component/platform" } ] }
  // SaaS implementation edges for platform-layer requirements:
  //   satisfied-by: inherited-from{ …/component/platform,
  //                 basis-ref: …/auth/jab-moderate-2026 } ← checked HERE
```

Follow one physical-security requirement up the stack. The SaaS's edge
leans on the PaaS and names the PaaS's authorization — one hop, one
check, green. The PaaS's own edge for that requirement leans on the
IaaS and names the IaaS's P-ATO — one hop, one check, green. Two local
checks, and the two-level inheritance is legitimate end to end without
any rule ever seeing more than one link.

Now break it deliberately: delete the PaaS's `basis-ref`. The failure
appears **at the PaaS's edge**, with the rule's printed rationale —
not as a diffuse "something in this stack is unsound" but as a precise
address: *this* link, *this* missing basis. Everything above inherits
the visibility of the break, which is exactly what an authorizing
official signing at the top needs: a chain that is green because every
link proved itself, or red at the link that didn't.

**The assessor's checklist,** falling straight out of the model: ask
for the `basis-ref` documents behind every inheritance edge; check each
cited authorization's `includes[]` actually covers the members being
leaned on; query the shared-responsibility clauses for missing
customer-side edges; and treat any suspiciously authorization-silent
platform component (§9.2's honest gap) as a question, not an answer —
the model made hiding *detectable by absence of the expected*, and your
job is to expect it.

## 9.6 What the kernel leaves to the facet

Deliberately absent from everything above: user populations, data-type
inventories, interconnection diagrams, network topology — the
descriptive context an SSP narrates for pages. That material lives in
the stdlib `system-context@1` facet, and the book's evidence rule
obliges a flag: that facet currently rests on *historical* Rev4-era
evidence (medium confidence, Rev5-era confirmation pending at the
executable gate). The kernel keeps only what liability and inheritance
*compute* on — perimeters, edges, bases — and stays small enough that
the chain above fits on one page.

## 9.7 Advice: what a vendor may tell you, and what it may not touch *(CP-ADVICE-1, proposed)*

A vendor knows how its product is hardened. You want that knowledge next
to your requirements — and you want to be certain that taking it in
changes nothing you decided: no requirement, no tailoring, no assessment.
The old world gave that certainty through a document model: a component
definition has no place to define a control. Here there are no document
models, so the certainty is a rule on a bundle.

**The file.** An *advice pack* is a bundle whose manifest carries a pack
header and whose objects are Components — nothing else (ADVICE-1), all
under the publisher's own origin (ADVICE-2), with no facet that declares
a semantics class (ADVICE-3):

```json
"pack": { "kind": "advice",
          "id": "https://dbvendor.example/pack/server-7-hardening",
          "version": "3",
          "publisher": { "ref": "https://dbvendor.example/party/vendor" } }
```

Shipped as one ZIP it is one file. The header sits in the manifest
because the manifest is what a signature binds (Chapter 11): vendor and
release are inside the signed state with no new mechanism. The publisher
is **claimed** by the header and the origin its ids share with it, and
**proven** when the vendor's Attestation binds this manifest and its
envelope verifies — the two words, and the envelope check, you met at the
Tailoring tier.

**A recommendation is a capability.** §9.1 said capabilities are what
component definitions always wanted to be. A capability may now say which
requirement it is about, which clauses, what to do, and which parameter
values the vendor suggests:

```json
{ "id": "cap-tls",
  "requirement-ref": "https://ns.bsi.bund.de/gspp/req/KONF.14.1",
  "statement-ids": ["s1"],
  "description": { "en": "Set net.tls.mode to requireTLS and disable every protocol below TLS 1.3." },
  "parameter-bindings": { "transport-crypto": "tls13" } }
```

`requirement-ref` resolves if present: the pack ships without the
catalog, which the vendor may have no right to pass on. Where the catalog
*is* in your set, the clauses must exist (ADVICE-5) and a suggested value
must lie in the declared space (ADVICE-6) — a suggestion the catalog
cannot accept is the publisher's defect, found before you adopt it.

**Adopting is yours.** A capability is a claim. Nothing computes on it
until an Implementation in *your* namespace cites it:

```json
"satisfied-by": [
  { "capability-ref": "https://dbvendor.example/component/server-7#cap-key-rotation" } ]
```

A bare `capability-ref` names a capability of the edge's own component;
`<component-id>#<capability-id>` names one of that component. Either way
the component is in the bundle and declares the capability, and a
component other than the edge's own is one of its `members` (ADVICE-7).
That last clause is what makes "this advice applies to this system" a
fact in the graph: the system contains the product. This is not
`inherited-from` — that edge says another party *performs* the control
under an authorization. A product you run is yours to configure; the
vendor only described how.

**What your set keeps.** On import the vendor's Components join your set,
and the vendor's manifest is kept unchanged beside your own, named by the
SHA-256 of its bytes — `packs/sha256/<hex>`, the placement of signature
envelopes and of the evidence store. That file *is* the import record: it
names the vendor, the release and every object that came with it, and it
is what the vendor signed. Three rules hold it to the set: the name is
the digest (ADVICE-8); every object it lists is in the set at that
version with that semantic digest, so vendor advice edited after import
is reported as such (ADVICE-9); one release of a pack, and one pack per
object (ADVICE-10).

**Importing again.** The same file a second time writes nothing — its
digest is already a file name in the store. Another release replaces the
ids the earlier release brought, and only those; any other id your set
already holds is refused (ADVICE-11). Releases are not ordered — `version`
is an opaque string — so a tool shows both and leaves the direction to
you. Before a replacement it lists the capabilities added, removed and
changed, and every edge of yours that cites one the new release drops.

**What the guarantee is — and is not.** After importing an advice pack
every object that was in your set has the semantic digest it had, and
only Components were added. It is *not* a promise that validation output
stays the same: references that were landmarks now resolve. An
`inherited-from` edge that already pointed at a Component the pack
brings will meet §9.4's boundary rule if that Component declares an
authorization. That is resolves-if-present working as designed.

> **Don't** take a vendor's Implementation objects in place of its
> advice. The failure this prevents is the one §9.1 opened with: two
> descriptions of how a requirement is met, one in a vendor artifact and
> one in your system's own — and, on import, a set that says more is
> implemented than you implemented. A claim stays a claim until your own
> edge cites it.

*Evidence tier, stated: one fictional example component definition in the
corpus (3 recommendations, 2 clause-level entries, 2 suggested
parameter values); no census authority publishes vendor advice. The
proposal, its counts and its open points: `drafts/CP-ADVICE-1.md`. Worked
files: `example-packs/dbvendor-server-7-advice/` and, in the example
bundle, the kept manifest, the vendor's Component and the edge that
adopts `cap-key-rotation`.*

The edges now exist; next, someone tests them. Chapter 10 is where
Assessments run (including the KSI-style automated criteria the
`assessment-criteria` facet absorbed), Findings accumulate their
actions and calendar-aware deadlines, and the Deviation lifecycle —
already met twice in this book — becomes the one audited channel
through which a system is allowed to be honestly imperfect.
