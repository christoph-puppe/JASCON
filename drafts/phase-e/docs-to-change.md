# What the phase E rework makes wrong in README, specification, handbook and website

Kept at the author's request (2026-11-14): "always have in mind we need
that on README, specification, handbook, website, maybe keep a list of
things to change there?" Nothing here is changed yet. Each entry says
where, what is wrong, and where the entry comes from:

- **read**: I read the line myself;
- **reported**: an agent's report named it; not checked by me yet.

Entries are added as each rework is merged (SP 800-53 and CR26 pending).
New counts are those of the merged bundles; the totals change again when
SP 800-53 and CR26 land, so totals are written only at the end.

## 1. Decisions for the author before the texts can be written

- **The statement layer loses its headline evidence.** Correction 2
  ("a nested control is a full control") means the "347 nested
  pseudo-controls" are no longer clauses. The handbook (chapters 1-5,
  14, appendices A and E), the specification's convergence table (row
  "Clause granularity") and the website's model page argue that
  `statements` is a list *because* of them. After the rework every
  Grundschutz++ Requirement has one statement (999 of 999), as have
  all of the ISM (1,150) and CSF (106). Of SP 800-53's 1,014
  Requirements, 284 have more than one statement, as the bundle stood
  before its rework (**measured**). How the statement layer is argued
  now is the author's decision.
- **Lifecycle without a source word.** Every rework reports that
  `lifecycle: active` stands on objects whose source states no status,
  because the kernel requires a lifecycle (ISM 1,731, Grundschutz++
  1,287, CSF 135 objects). The texts that say a converter writes
  nothing the source does not state need the author's word first.
- **Findings about the kernel and the standard facets** (each with the
  place the converter carries the values meanwhile), to be decided
  before the specification says what the kernel holds:
  - document metadata: no kernel member (all corpora; compat
    `metadata` on the root Set);
  - an object's own revision and the date of its last change (ISM,
    2,202 values; compat `props`);
  - resources that texts refer to, and how a link `(#uuid)` in a text
    resolves (ISM 246 resources; converter-pinned references facet);
  - `replaces[]` closed to `{ref, mode}`, so the label, title and prose
    of a withdrawn item without an object stand in an annotation
    outside the semantic digest (CSF, 87 items);
  - risk-party (CSF, 125 values; converter facet csf@1);
  - a parameter has no member for an alternative identifier
    (Grundschutz++, 221 uuids; compat `param-extras`);
  - a kernel number is an integer, so a fraction in a facet is written
    as a decimal string (Grundschutz++ rule, no fraction in the source;
    CR26 has 3);
  - nothing says what a Set stands for (Grundschutz++: a group and a
    control with nested controls both give `/set/tax/<slug>`);
  - the mapping of CR26's status `placeholder` to `draft` (the
    converter's own; family AGU, 28 objects). AGU's effectivity reads
    `required` like the stable families, the handbook defines draft as
    "must not be cited by anything claiming conformance" (ch03 §3.6),
    and seven `active` Sets hold AGU's draft Sets as members, which the
    validator passes;
  - no kernel place for a source's own status word (CR26 keeps it in
    `narrative@1`, 27 values); a facet has no lifecycle, so a glossary
    whose source is not stable could not say so (CR26 `terminology@1`);
  - no convention for alias schemes (`bsi-uuid`, `fedramp-cr26:KSI.id`);
  - the ledger checks that a rule was applied, not that the rule is
    right: mapping `placeholder` to `active` in the converter's table
    passes the ledger and only the converter's test catches it. The
    CR26 agent suggests a library check that each destination a
    path-map row names is reached;
  - SP 800-53: `assessment-for` does not fit the standard
    assessment-criteria@1 (`by-statement` keys only the host
    Requirement's kernel statements; 217 links name a statement part as
    a whole, 6 leave the control, 1,087 objectives name another
    statement than their parent; its `objectives` are untyped and it
    has no member for the methods). D10 requires a payload that
    addresses single statements to be keyed `by-statement`; the pinned
    sp800-53a@1 writes `statement-id` inside a tree, so neither D10 nor
    the standard facet has a form for it (3,707 links);
  - SP 800-53: a withdrawn control without a successor must carry a
    statement with modality and obligated party; cp-10.3 and sc-19 get
    `unspecified` and the converter's default party;
  - SP 800-53: a statement has no label member (1,122 item print
    labels); a parameter has one `label` only (1,458 formal ODP labels
    in odp@1);
  - SP 800-53: two `related` relations name an object that does not
    exist (au-9 and au-5.4 to AU-15, which moved to AU-5(5)); relations
    are not closure-required, so the validator passes;
  - the compat facet `https://ns.jascon.net/compat/oscal-1x`, version
    1.0.0, is pinned with four different closed schemas (ISM,
    Grundschutz++, CSF, SP 800-53); in the app, a profile imported into
    a Grundschutz++ set keeps its metadata but not its merge directive,
    because that set's schema has no `merge`;
  - a manifest has one provenance: the four SP 800-53 profiles' author
    and day stand only in their compat metadata;
  - the ledger has no checked class for "a value that decides the
    representation" (the 180 `withdrawn` status words of SP 800-53);
  - SP 800-53: the brief I wrote made its agent carry the catalogue's
    back-matter uuids and media types (25 values) that CSF and
    Grundschutz++ still declare as drops: one decision on class B of
    the declared-drops list settles all three.

## 2. README.md

| Where | What is wrong | Source |
|---|---|---|
| 482 | AU.ISM row: "1,150 Requirements · 561 Sets": now 581 Sets | read |
| 482 (DE.BSI row) | "651 Requirements carrying 999 statements · 221 params · 162 Sets": now 999 Requirements, one statement each, 288 Sets (126 of them the grouping of a control with nested controls) | read |
| 504 | US.SP800-53: "1,014 Requirements ... 182 withdrawn tombstones": now 1,016 Requirements (cp-10.3 and sc-19 with lifecycle `withdrawn`), 180 withdrawn controls inverted | reported |
| 600-601 | "the NIST SP 800-53 rules give what `convert_nist.py` gives": true again only once the app's SP 800-53 preset follows the rework | reported |
| 21-25, 27 | "traced on one corpus so far"; "5,886/5,886": today's export run gives 4,198 of 4,198 on four corpora (measured). Wrong before phase E | reported (count measured) |
| 505 | US.CSF: "106 Requirements · 29 Sets ... 91 withdrawn ... inverted": now 33 Sets; 87 withdrawn items inverted, 4 categories objects with lifecycle `withdrawn` | reported |
| 261 | "6,916 objects in eleven bundles": ISM +20, CSF +4, Grundschutz++ +474, SP 800-53 and CR26 pending | reported |
| 397-399 | totals over the bundles (6,914 objects, 4,583 Requirements, 1,066 Sets) | reported |
| 407 | "ISM −29 %" against the source: the ISM bundle's objects grew from 2,124,074 to 2,564,741 bytes; not re-measured by that sentence's method | reported |
| 276-279 | the ledger sentences (four outcomes; "unaccounted" values; "the other ten corpora have no ledger") | reported |
| 408 | "CR26 +55 %": the source is now 588,800 bytes and the bundle changed; not re-measured by that sentence's method. Wrong before phase E | reported |
| the paragraph on value arrival | to say: 0 unaccounted in every corpus with a ledger, the three no-content rules, the gate | (to write) |

## 3. Specification (drafts/jascon-specification-2.0.0-rc.4.md)

| Where | What is wrong | Source |
|---|---|---|
| 240 | convergence table, "Clause granularity: 347 nested pseudo-controls" (see section 1) | read |
| 254 | "threat references on 595 of 651 requirements": the agent counts 900 of 999 | read (the line); reported (the new count) |
| 756, 1797 | "ISM = zero facets", if meant of the conversion: every ISM Requirement now carries the compat facet | reported |
| 2002 | "ISM −29 %" | reported |
| 2390 | "3,714 manifest-listed objects" | reported |
| 2003 | "CR26 +55 %" (as README 408). Wrong before phase E | reported |
| 930, 2149, 2375 | "5,886" round trip: 4,198 on four corpora today. Wrong before phase E | reported |
| 2029-2033, 2059 | "the one corpus measured so far ... the other ten corpora are unmeasured"; "established at path level only": six corpora have a ledger now | reported |
| 2276-2277, 2401-2402 | "two reports": the CR26 step compares three files, the two reports and the ledger record. Wrong before phase E | reported |
| IV.5b, IV.6, IV.7, IV.9 | the phase E state: the ledger, the gate, R16 "converted losslessly", the twin's runs on Windows PowerShell 5.1 for #55 | (to write) |
| older versions (`jascon-specification-1.0.0.md:125`, `jascon-v0.5-specification.md:90, 821`) | the same clause-granularity row; "106 Requirements + 29 Sets". Historical documents: the author decides whether they change | reported |

## 4. Handbook (jascon/references/)

| Where | What is wrong | Source |
|---|---|---|
| ch14-migration-playbooks.md:134-135 | "nested controls become statements of their parent" | read |
| ch01-why-this-exists.md:306 | statements arrive via the 347 German pseudo-controls | read |
| ch02-the-core-in-one-hour.md:70 | "347 nested pseudo-controls that exist only because ... clauses" | read |
| ch03-identity-versions-lifecycle.md:267 | "the 347 German pseudo-controls demonstrate exactly when one requirement should become several statements" | read |
| ch04-writing-requirements.md:34 | "the reason is a number: 347 nested pseudo-controls" | read |
| ch05-sets-hierarchy-baselines.md:91 | "The 347 German pseudo-controls became statements" | read |
| appendix-a-shapes.md:41 | "347 BSI nested pseudo-controls → 1,015 statements" | read |
| appendix-e-worked-corpora.md:17, 51 | the MS-TLS example: nested controls as clauses (`statement-id: "KONF.14.1.1"`) | read |
| appendix-e-worked-corpora.md:116-134 (E.3) | ISM-1997 "converting with zero facets": it carries the compat facet now (revision, updated) | reported |
| appendix-f-objections.md:167 | "convert at Core tier with zero facets" | reported |
| appendix-f-objections.md:374 | "CR26 +55 %". Wrong before phase E | reported |
| ch14-migration-playbooks.md §14.4 (298-318) | CR26: no word on status → lifecycle or on the KSI category ids; line 307 "`updated[]` → L0 versions plus manifest release notes" is wrong (the history is a declared drop); line 313 "`do_not_link` → annotations" is wrong (it goes to `terminology@1`) | reported |
| appendix-a-shapes.md:20, 27 (and 21, 23) | 20: CR26 `updated[]` "absorbed" by `version`: it is dropped (475 entries, 957 values); 27: `do_not_link` cited as an annotation; 21 (aliases) and 23 (lifecycle) could cite the new CR26 cases | reported |
| ch14-migration-playbooks.md:71-72, 80, 104-106 | "four outcomes"; "its one corpus"; revision history and the directory of parties are dropped by class (SP 800-53 now carries them) | reported |
| appendix-d-stdlib-catalog.md D.10 | the compat residue table has no SP 800-53 row (5 Sets) | reported |
| appendix-d-stdlib-catalog.md:222 | the CTL overlay "parked until...": drained into operations since gate 3. Wrong before phase E | reported |

## 5. Website (website/)

| Where | What is wrong | Source |
|---|---|---|
| build.py `ledger_counts()`, `ledger_rows()` | four outcomes; the fifth, `not-content`, is in no cell (Grundschutz++ alone has 15,004) | read |
| src/evidence.html:85 | "CR26 +55 %". Wrong before phase E | reported |
| src/evidence.html:154-159 and the four translations | the ledger sentence ("the ledgers found values that are lost all the same", "unaccounted, with no destination") and the table header need the fifth outcome and the new state | read |
| src/index.html:144 and the four translations | the stats note on the ledger | read |
| src/model.html:26 and the four translations | "Grundschutz++ contains 347 nested pseudo-controls that exist only to make clauses addressable" (see section 1) | read |
| src/evidence.html:84, src/index.html:139-140 and the translations | the export round-trip figure and the ledger lines (reported by the SP 800-53 agent) | reported |
| facts.json | AU.ISM 1,711 / 561 → 1,731 / 581; DE.BSI 813 / 651 / 162 → 1,287 / 999 / 288; US.CSF 135 / 29 → 139 / 33; US.SP800-53 1,039 / 1,014 → 1,041 / 1,016; re-measure with `python3 website/build.py --measure` after the last merge | reported (numbers checked against the bundles by me) |

## 6. Elsewhere in the repository

| Where | What is wrong | Source |
|---|---|---|
| .github/workflows/validators.yml:194-196 | the CR26 step's comment names four ledger outcomes; `not-content` is missing | reported |
| jascon/SKILL.md:96, 102 | "four outcomes"; "the one converter with a ledger" (convert_nist.py not listed) | reported |
| jascon/SKILL.md:168 | convert_bsi.py "Handles nested pseudo-controls, splitting them into statements" | read |
| SKILL_jascon.zip | stale against the converters and tests | read |
| drafts/gate-4-measurement.md:14 | "ISM round-trips 1,711/1,711": now 1,731/1,731 (measured, c310ab37) | reported (new count measured) |
| drafts/gate-3-census.md:74, 155 | "tombstone inversion" for all withdrawn CSF items: four are objects now | reported |
| converted_examples/DE.BSI/SOURCE-LICENSE.md:24 | describes the old export | reported |
| converted_examples/DE.BSI/oscal-export/geman.bsi-catalog.json | an older file the export script does not write | read |
| drafts/jascon-decision-rationale-register.md:144; backlog row #41 | nested controls as statements; the BSI figures | reported |
| DEEP_RESEARCH_REVIEW.md:90, 97 | nested controls as statements | reported |
| jascon-app/readme.md:361-367, 426-427 | withdrawn controls not converted; "1,035 objects equal"; 1,035 objects, 1,918 statements (the SP 800-53 preset) | reported |
| jascon-app (both presets) | done: Grundschutz++ in build 0.9.14, SP 800-53 in build 0.9.15 (merged), with their texts, ERRATA and tests | read |
| README.md:600-601 | "the NIST SP 800-53 rules give what `convert_nist.py` gives": right again since build 0.9.15 (baseline Sets aside: the preset makes none) | reported |
| README.md:117-118 | counts of the bundles' statements (SP 800-53 has 1,920 statements now) | reported |
| jascon/scripts/convert_nist.py | a converter defect, found by the app's agent: on a catalogue where a `reference` link names a back-matter resource that has no link (not the pinned one), it writes no relation and its ledger ends the run with 1 on the two values | reported |
| website/src/start.html:108 | "what OSCAL cannot hold returns on import": if it means the app's Import page, it was wrong before phase E too (the presets carry those props in the compat facet, they do not read them back) | reported |
| jascon/scripts/convert_bsi.py | a converter defect, found by the app's agent: on a catalogue with an empty parameter label (not the pinned one) it writes the bundle and then ends with 1 on a wiring check, because the path map does not name `param-extras/{param}/label` for `params[].label`; the app's comparison test accepts that one failure | reported |
