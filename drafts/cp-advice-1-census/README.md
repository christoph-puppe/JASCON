# Census: NIST's example component definitions through the pack builder's import

**2026-11-12 · CP-ADVICE-1 §2.3 · specification D22 and D25**

The pack builder (`one-page-apps/jascon-pack-builder.html`) imports OSCAL
component definitions. This census runs every component definition NIST
publishes in `usnistgov/oscal-content` through that import, once without a
catalogue and once with the SP 800-53 Rev 5 catalogue of
`converted_examples/` loaded, and records what the import made of each file
next to what the file holds. The measurement is the builder's own code, so
the numbers are what a vendor would see.

## Inputs

`sources/`: the four JSON files of `examples/component-definition/json/` in
`usnistgov/oscal-content`, commit `f0de6d8d8c059d374f15e0ae07508d82e370fc1d`
(2026-10-22), copied unchanged. NIST's content is in the public domain and
dedicated under CC0 1.0 (the repository's `LICENSE.md`).

| File | SHA-256 | OSCAL | Components | Implemented requirements | Statements | set-parameters |
|---|---|---|---|---|---|---|
| `example-component-definition.json` | `52f14288…` | 1.2.3 | 1 (service, "MongoDB") | 3: sc-8, sc-8.1, sa-4.9 | 2 | 2 |
| `example-component-definition-min.json` | `03b13ac8…` | 1.2.3 | the same content, minified | | | |
| `example-component.json` | `c6cb4b70…` | 1.2.3 | 1 (software, "test component 1") | 2: ac-2.3 twice | 0 | 0 |
| `example-component-min.json` | `6ff5cfc6…` | 1.2.3 | the same content, minified | | | |

Each `-min` file has the same canonical form as its full twin
(`canonical-sha256` in `census.json`). **Two distinct component
definitions**, both written by NIST as examples: the MongoDB file is the
one the IFA lifecycle corpus already holds (CP-ADVICE-1 §2.2), the other is
a test file.

## What the import found, and what was changed because of it

The first run used the builder as merged (v1.1.0). Every finding below was
fixed in v1.2.0, has a test, and the census was run again.

| Finding in NIST's files | v1.1.0 | v1.2.0 |
|---|---|---|
| `source` is `#<uuid>`, a reference into the back-matter, in every control implementation of both files. The URL is in the resource's `rlinks`. | Not recognised as SP 800-53: **0 of 10** implemented requirements resolved without a catalogue | Read through the back-matter: **10 of 10** resolved by the rule of the SP 800-53 conversion, without a catalogue |
| `example-component.json` cites the **Rev 4** catalogue and a **FedRAMP Rev 4** baseline. The SP 800-53 conversion is Rev 5. | With a catalogue, mapped onto Rev 5 ids without a word. The FedRAMP baseline's links never say "800-53", so the rule would not have known it | FedRAMP baselines count as SP 800-53 sources; each Rev 4 source is named in the report: "a control Rev 5 withdrew or changed needs a look by hand" |
| Statement texts carry OSCAL markup: `{{ insert: param, sc-8_prm_1 }}` | Copied as literal braces (4 in the full and min files together) | Rewritten as JASCON prose writes it, `{param:sc-08_odp}`, under the catalogue's parameter name |
| Parameters use Rev 4 ids (`sc-8_prm_1`, `sc-8.1_prm_1`) | Without a catalogue kept as they are: a customer whose set holds SP 800-53 would see ADVICE-6 fail | Same values, now named in the report with the remedy: load the catalogue and import again |
| One component implements `ac-2.3` twice, from two sources | Two recommendations for one requirement, silently | The same, named in the report |

With the catalogue loaded, both versions resolve every control through it.
Both clause-level statements arrive as `statement-ids` (`smt` of SC-8 and of
SC-8(1)), and both values arrive under the catalogue's names:
`sc-08_odp: ["confidentiality"]` and `sc-08.01_odp: ["prevent unauthorized
disclosure of information"]`, many-choice lists as the catalogue declares.
No ADVICE rule fails on any of the four files.

## What a pack has no place for (counted per run, both files)

| OSCAL content | MongoDB file | test file | Where it could go |
|---|---|---|---|
| `components[].protocols` | 3 | 0 | Ports and protocols are technical facts a customer would want. No kernel field; a facet or recommendation text, if a corpus asks for it |
| `components[].responsible-roles` | 2 | 1 | The vendor's internal roles; no consumer use |
| `components[].purpose`, `description` | 1, 1 | 0, 1 | A Component has no description field |
| `control-implementations[].description` | 1 | 2 | Text about the mapping, not advice |
| `statements[].responsible-roles` | 1 | 0 | as above |
| `back-matter.resources` other than sources | 1 | 1 | The file's own provenance link |

## What the census says about D22, and what it does not

It does **not** change the standing of `statement-ids` or `product-version`
(specification D22, "Applied at 2.0.0-rc.3"). The clause-level evidence is
still one fictional NIST file with 2 clause entries and 2 values, the same
file counted in CP-ADVICE-1 §2.2. NIST's second example carries no clause,
no value and no product version. Both are examples written by the format's
own maintainers, not component definitions a vendor published. Neither
carries a product version in any form, so `product-version` remains without
counted evidence.

What it does show: on the files that exist, the import loses nothing a pack
can hold, and it names everything else.

## Not counted

Component definitions published by vendors or by other projects (for
example in FedRAMP's or a cloud provider's repositories) have not been
gathered. That census is still owed (CP-ADVICE-1 §2.3) and is the one that
could change D22.

## Run it again

```sh
node drafts/cp-advice-1-census/run_census.mjs
```

Needs Playwright with Chromium. It writes `census.json` here and prints one
line per file and run. A second run gives the same `census.json` apart from
its date. The browser test
`one-page-apps/tests/pack-builder.test.mjs` ("NIST's example component
definitions …") holds the import to these results in CI.
