# The jascon.net site

The public site of the project: six pages (home, the model, checks, evidence,
get started, join), a legal notice, and a 404 page, in English and in four
translations (German, Hindi, Japanese, Simplified Chinese). It is static, has
no dependency beyond Python's standard library to build, and sends no request
to another host when it is read.

## Build and look at it

```bash
python3 website/build.py
```

```bash
python3 -m http.server 8000 -d _site
```

Then open `http://localhost:8000/`. The output folder `_site/` is not
committed. It holds the pages and also the app, so the links from the site
into the app work as they will on the domain:

| In the output | Comes from |
|---|---|
| `/` | `website/src/*.html` set into `_layout.html`, and `website/static/` as it is |
| `/app/` | `jascon-app/` (without its tests and tools) |
| `/reader/` | `one-page-apps/jascon-reader.html` |
| `/pack-builder/` | `one-page-apps/jascon-pack-builder.html` |
| `/converted_examples/` | the five bundles the repository may pass on, each with its `SOURCE-LICENSE.md` |
| `/jascon/` | the example bundle, the schemas and the conformance vectors |

`python3 website/build.py --pages-only` skips everything but the first row.

## Where the numbers come from

The pages do not carry typed-in counts of vectors, objects or lines. They
carry names such as `{{ n.vectors }}`, and the build fills them from
`facts.json`.

```bash
python3 website/build.py --measure
```

`--measure` runs `jascon/scripts/validate_core.py` (it needs `jsonschema`),
reads its report and rewrites `facts.json`. If the validator is not ALL GREEN
the build stops and writes nothing. The publishing workflow always measures,
so the site shows the counts of the commit it was built from.

Numbers the build cannot recompute are dated in the text: the 1.0.0
measurement of 22 July 2026 (eleven corpora, 251,591 leaf values, the
5,886-object OSCAL round trip) and the counts from the census. When one of
them changes in the repository, change it in `src/` too. The sources are
`README.md`, `PRIOR-ART.md`, `drafts/gate-4-measurement.md`, the backlog and
handbook chapters 1, 2 and 15.

The home page lets a visitor edit `jascon/examples/req-ism-1234.json` and
computes both digests in the browser. The file and its expected digests are
read from the example bundle at build time, so the demo cannot drift from the
manifest.

The Check demo (home page and `checks.html`, one partial:
`src/_check-demo.html`) does not re-implement the verdict. It loads
`app/jascon-schema.js` and `app/jascon-rules.js`, the app's port of the kernel
rules, when the demo comes near the viewport, and calls `jscCheckVerdict` and
`jscCheckAggregate`. Requirement, bound parameter, the two Checks and the
observations of the two recorded runs are read from `jascon/examples/` at
build time. In a `--pages-only` build the demo says that the rules are
missing.

## Editing

- A page is `src/<name>.html`: a header between two `---` lines (`title`,
  `description`, `nav`) and the body. Header and footer are in
  `src/_layout.html`, once.
- `{{ name }}` is replaced from the facts, `site.json` and the page header.
  An unknown name stops the build. `{{ file:path }}` sets in a file of the
  repository, `{{ include:_name.html }}` a partial of `src/`.
- `<code data-lang="json">` and `<code data-lang="sh">` are coloured by the
  build. In JSON, `«` and `»` mark the part the text points at.
- The build checks every local link and anchor and stops on a broken one.
- Styles are `static/assets/css/site.css`, with the colour tokens for light
  and dark at the top (the classic look; the violet is the app's accent), and
  `static/assets/css/styles.css`, three alternative styles a visitor picks in
  the header: Ledger (`data-style="ledger"`, after Hanne Darboven),
  Engraving (`engraving`, after Albrecht Dürer) and Still life
  (`still-life`, after Giorgio Morandi). Each redefines every token of
  `site.css` and adds its own ground, type and shapes; the choice is stored
  like the colour scheme. The painters are named here only, not on the site.
- The app screenshots under `static/assets/img/` are taken from the built
  site at 1280 by 750, device scale 2, and stored as WebP.

The tone of the text follows the project's house rules: a claim is measured,
designed for or proposed and says which; limits are stated where the claim is
made.

## Languages

English is the source. `site.json` lists the languages that are built
(`"languages"`); each has the words of the layout in `i18n/<lang>.json` and
its pages in `src/<lang>/`, and is served under `/<lang>/` (`/de/`, `/hi/`,
`/ja/`, `/zh/`). The header carries a language menu (a `<details>`, so it
works without scripts), the footer the same links, and every page names its
translations with `hreflang` links. The app, the reader and the documents in
the repository stay English.

Which language a visit opens in: an English page moves to its translation in
the language last picked in the menu (stored in the browser), or, before any
pick and only on arrival from another site, in the first language of the
browser's list that the site offers. English, no match, or no translation of
that page keeps the English page. A translated page never moves, so a shared
link stays in its language, and a link within the site never moves either.
The script is in the head of each English page (`AUTO_LANGUAGE` in
`build.py`); traditional Chinese (`zh-Hant`, `zh-TW`, `zh-HK`) is not taken
for the simplified pages.

- A translated page keeps the markup of the English one and changes words
  only. `i18n/check_translation.py <lang> [page]` compares the two (blocks,
  elements, `{{ names }}`, code), and the build runs the same check.
- A translation records in its header the digest of the English page it
  follows (`source:`). When the English page changes, the build lists the
  translation as older and the page shows its reader a note with a link to
  the English page. After the translation is brought up to date:
  `python3 website/build.py --stamp <lang>/<page>`.
- Rules and glossary for translators: `i18n/TRANSLATING.md`.
- The site's faces are Latin subsets. Devanagari and Han/Kana are set in the
  reader's system faces; `styles.css` names them per language at its end.

## Publishing on jascon.net with GitHub Pages

`.github/workflows/website.yml` builds and publishes on every push to `main`
that touches the site or what it is made from.

1. In the repository: **Settings, Pages, Source: GitHub Actions**. Do this
   before the workflow first runs on `main`, or that run fails at the deploy
   step.
2. Same page: custom domain `jascon.net`, then "Enforce HTTPS" once the
   certificate is issued.
3. At the registrar, point the domain at GitHub Pages: four `A` records and
   four `AAAA` records for the apex, and a `CNAME` for `www` to
   `christoph-puppe.github.io`. Take the current addresses from GitHub's
   documentation, "Managing a custom domain for your GitHub Pages site".
4. Verify the domain for the account (Settings, Pages, "Verified domains") so
   that nobody else can claim it for a Pages site.

Any other static host works as well: build, then upload `_site/`. The pages
use relative links only, so they also work under a path such as
`https://christoph-puppe.github.io/JASCON/` before the domain is attached.
The one exception is `404.html`, which assumes the site root.

`ns.jascon.net`, the host in the namespace URIs of the schema and the standard
library, is a different name and is not served by this site. Identifiers are
never fetched during validation, so nothing breaks while it serves nothing.

## Before going live

- **Legal notice.** `site.json` has an `imprint` block. It is empty, and
  `legal.html` then names the publisher and the issue tracker only. A site
  operated from Germany that is not purely private needs a postal address and
  a fast contact (§ 5 DDG); fill in `address_lines` and `email` if that
  applies. This is a pointer to the rule, no legal advice.
- **Hosting sentence.** The privacy section says in general terms that the
  host processes IP addresses. Name the host once it is chosen.
- **Contact.** The site offers GitHub issues as the only contact. Add an
  address at the domain in `site.json` if one exists.
- **The statements on the site are the project's own.** Read the home page
  and `evidence.html#limits` once as the person who signs them. They say,
  among other things, that the project has one maintainer and no third-party
  user.

## Licences

The site's own text, markup, styles and script: Apache-2.0, like the rest of
the repository. The typefaces under `static/assets/fonts/` (Inter, Source
Serif 4 and JetBrains Mono for the classic look; Barlow, Barlow Condensed,
Courier Prime, EB Garamond, Bodoni Moda and Titillium Web for the three
alternative styles; Latin subsets as packaged by Fontsource) are under the
SIL Open Font License 1.1, in `LICENSE.txt` beside them.
