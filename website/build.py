#!/usr/bin/env python3
"""Build the jascon.net site into one folder a static host can serve.

    python3 website/build.py                 # pages + assets + the app, from facts.json
    python3 website/build.py --measure       # run the reference validator first
    python3 website/build.py --out /tmp/site # another output folder (default: _site)
    python3 website/build.py --pages-only    # skip the app, the reader and the bundles

Standard library only. What it does, in order:

1. Facts. The numbers the pages print (conformance vectors, objects per
   shipped bundle, validator size) are not typed into the pages. They come
   from facts.json, and `--measure` rewrites that file from a run of
   jascon/scripts/validate_core.py on the tree it is run in. A run that is
   not ALL GREEN stops the build: the site does not publish a claim the
   validator did not make.
2. Pages. Every src/*.html without a leading underscore is a page: a small
   header (title, description, nav) and a body, set into src/_layout.html.
   `{{ name }}` is replaced from the facts, site.json and the page header;
   an unknown name stops the build. The words of the layout come from
   i18n/<lang>.json. Each further language of site.json "languages" is
   built into <lang>/ from src/<lang>/<page>.html; a page that has no
   translation is left out there, and links to it go to the English page.
   A translation records the digest of the English page it was made from
   (header line `source:`); when the English page changes, the build says
   so and the translated page tells its reader.
3. The app. jascon-app/ is copied to app/, the single-file reader to
   reader/, the redistributable bundles to converted_examples/ with the
   publishers' licence notes beside them, and the example bundle, the
   schemas and the conformance vectors to jascon/. The relative paths the
   app already uses (../converted_examples/...) keep working.
4. Checks. Every local href and src in the pages must name a file in the
   output, or the build stops.
"""
import argparse
import datetime
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "i18n"))
import check_translation  # noqa: E402  (website/i18n/check_translation.py)

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SRC = os.path.join(HERE, "src")
STATIC = os.path.join(HERE, "static")
FACTS = os.path.join(HERE, "facts.json")
SITE = os.path.join(HERE, "site.json")
I18N = os.path.join(HERE, "i18n")

VALIDATOR_PY = "jascon/scripts/validate_core.py"
VALIDATOR_PS = "jascon/scripts/validate_core.ps1"

# The bundles this repository may pass on (NOTICE, "What ships here"). The
# words shown on the site for each; the licence itself is the
# SOURCE-LICENSE.md copied beside the bundle.
CORPORA = {
    "AU.ISM": {
        "title": "Information Security Manual",
        "publisher": "Australian Signals Directorate",
        "licence": "CC BY 4.0",
        "note": "1,150 controls; classification and Essential Eight baselines as Sets",
    },
    "DE.BSI": {
        "title": "Grundschutz++ Anwenderkatalog",
        "publisher": "BSI, Germany",
        "licence": "CC BY-SA 4.0",
        "note": "German prose, statement grammar and protection goals as facets",
    },
    "US.SP800-53": {
        "title": "SP 800-53 Rev 5.2.0 with the 800-53B baselines",
        "publisher": "NIST",
        "licence": "CC0 1.0",
        "note": "Statement-scoped parameters; four baselines as membership Sets",
    },
    "US.CSF": {
        "title": "Cybersecurity Framework 2.0",
        "publisher": "NIST",
        "licence": "CC0 1.0",
        "note": "Functions, categories and subcategories as nested Sets",
    },
    "US.IFA-GoodRead": {
        "title": "OSCAL example system (SSP, plan, results, POA&M)",
        "publisher": "NIST, fictional content",
        "licence": "CC0 1.0",
        "note": "The lifecycle types: Component to Attestation, with two Risks",
    },
}

TYPE_LABELS = {
    "requirement": "Requirement", "requirementSet": "RequirementSet",
    "tailoring": "Tailoring", "mapping": "Mapping", "risk": "Risk",
    "component": "Component", "implementation": "Implementation",
    "assessment": "Assessment", "finding": "Finding",
    "attestation": "Attestation", "check": "Check",
}


def die(msg):
    sys.exit("build.py: " + msg)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


# ---------------------------------------------------------------- facts

def count_lines(path):
    """The counter of drafts/gate-4-measurement.md: non-blank lines that do
    not start with '#'."""
    n = 0
    for line in read(path).splitlines():
        s = line.strip()
        if s and not s.startswith("#"):
            n += 1
    return n


def git(*args):
    try:
        return subprocess.run(["git", "-C", REPO, *args], capture_output=True,
                              text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def listed_objects(bundle, counts):
    """(objects the manifest lists, Attestations beside it) of a bundle the
    validator found green.

    A bundle's objects, as the pages count them, are the entries of its
    manifest: those are the objects whose two digests the validator
    recomputed. Since 2026-11-14 the validator also types and counts the
    Attestations that lie beside a manifest (D3.1; backlog #46). They are no
    entry of the manifest and have no pair of digests in it, so a page that
    says "both digests of N objects" must not count them. The validator's
    report does not say where an Attestation lies, and it refuses a listed
    one in a pack only (ADVICE-1; measured 2026-11-14 on a copy of the IFA
    bundle that lists its own: 0 failures). So the manifest is read as
    well: with every Attestation of the report taken as lying beside it,
    its entries must be as many as the other objects the validator typed.
    A bundle that lists an Attestation stops the build here."""
    beside = counts.pop("attestation", 0)
    manifest = json.loads(read(os.path.join(REPO, bundle, "content-manifest.json")))
    listed = len(manifest["objects"])
    if listed != sum(counts.values()):
        die(f"{bundle}: its manifest lists {listed} objects, the validator typed "
            f"{sum(counts.values())} beside {beside} Attestation(s)")
    return listed, beside


def measure():
    """Run the reference validator and read its report."""
    print("build.py: running", VALIDATOR_PY, "...")
    run = subprocess.run([sys.executable, os.path.join(REPO, VALIDATOR_PY)],
                         cwd=REPO, capture_output=True, text=True)
    out = run.stdout
    if run.returncode != 0 or "ALL GREEN" not in out:
        sys.stderr.write(out[-3000:] + run.stderr[-3000:])
        die("the reference validator is not ALL GREEN; nothing was built")

    families, bundles, packs, examples, example_types = [], [], [], 0, {}
    section = None
    for line in out.splitlines():
        if line.startswith("== "):
            section = line.strip("= ").split()[0]
            continue
        m = re.match(r"^\s+([\w.\-/]+): (\d+) pass, (\d+) fail(?:\s+(\{.*\}))?\s*$", line)
        if not m:
            continue
        name, passed, failed, types = m.group(1), int(m.group(2)), int(m.group(3)), m.group(4)
        if failed:
            die(f"{name} reports failures although the run is green")
        if section == "conformance":
            families.append({"name": name, "vectors": passed})
        elif section == "bundles":
            counts = json.loads(types.replace("'", '"')) if types else {}
            if name == "skill-examples":
                examples = sum(counts.values())
                example_types = counts
            elif name.startswith("jascon/example-packs/"):
                # the skill's worked advice pack(s) (CP-ADVICE-1): examples, not a corpus
                listed, beside = listed_objects(name, counts)
                packs.append({"path": name, "objects": listed, "attestations": beside})
            else:
                corpus = name.split("/")[1]
                if corpus not in CORPORA:
                    die(f"bundle {name} has no entry in CORPORA; add its title and licence")
                listed, beside = listed_objects(name, counts)
                bundles.append({"corpus": corpus, "path": name, "objects": listed,
                                "attestations": beside, "types": counts})
    if not families or not bundles:
        die("could not read the validator's report; its output format changed")

    return {
        "measured": {
            "date": datetime.date.today().isoformat(),
            "commit": git("rev-parse", "--short", "HEAD") or "unknown",
            "by": VALIDATOR_PY,
        },
        "vectors": {
            "total": sum(f["vectors"] for f in families),
            "families": families,
        },
        "bundles": bundles,
        "examples": {"objects": examples, "types": example_types},
        "example_packs": packs,
        "validators": {
            "python_lines": count_lines(os.path.join(REPO, VALIDATOR_PY)),
            "powershell_lines": count_lines(os.path.join(REPO, VALIDATOR_PS)),
        },
    }


# ---------------------------------------------------------------- values

def fmt(value, sep=","):
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, int):
        return f"{value:,}".replace(",", sep)
    return str(value)


def lookup(ctx, dotted):
    cur = ctx
    for part in dotted.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur


def fragments(facts, T):
    """HTML built from the facts: table rows and lists the pages place, in
    the words of one language (T, the strings of i18n/<lang>.json)."""
    e = html.escape
    b_t = T["build"]
    sep = T["meta"]["thousands"]
    num = lambda n: f"{n:,}".replace(",", sep)
    fam = facts["vectors"]["families"]
    family_rows = "\n".join(
        f'<tr><td><code>{e(f["name"])}</code></td><td class="num">{f["vectors"]}</td></tr>'
        for f in fam)
    family_chips = "\n".join(
        f'<li><code>{e(f["name"])}</code><span>{f["vectors"]}</span></li>' for f in fam)

    rows = []
    plural = "s" if b_t["plural_s"] else ""
    for b in facts["bundles"]:
        c = dict(CORPORA[b["corpus"]], **b_t["corpora"].get(b["corpus"], {}))
        kinds = " · ".join(f'{num(n)} {TYPE_LABELS.get(t, t)}{"" if n == 1 else plural}' for t, n in
                           sorted(b["types"].items(), key=lambda kv: -kv[1]))
        bundle_dir = b["path"].split("/", 1)[1]
        tool = "assess" if "assessment" in b["types"] else "browse"
        rows.append(
            "<tr>"
            f'<th scope="row"><span class="corpus-id">{e(b["corpus"])}</span>'
            f'{e(c["title"])}<small>{e(c["publisher"])}</small></th>'
            f'<td class="num">{num(b["objects"])}</td>'
            f"<td>{e(kinds)}<small>{e(c['note'])}</small></td>"
            f'<td><a href="converted_examples/{e(b["corpus"])}/SOURCE-LICENSE.md">{e(c["licence"])}</a></td>'
            f'<td><a class="open" href="app/index.html#load=../converted_examples/{e(bundle_dir)}/&amp;tool={tool}">'
            f"{e(b_t['open_in_app'])}</a></td>"
            "</tr>")
    return {
        "family_rows": family_rows,
        "family_chips": family_chips,
        "bundle_rows": "\n".join(rows),
        "ledger_rows": ledger_rows(sep),
    }


def context(facts, site, T):
    shipped_objects = sum(b["objects"] for b in facts["bundles"])
    ctx = {
        "lang": T["meta"],
        "t": T["layout"],
        "script": T["script"],
        "sep": T["meta"]["thousands"],
        "facts": facts,
        "site": site,
        "repo": site["repo_url"],
        "blob": site["repo_url"] + "/blob/main",
        "tree": site["repo_url"] + "/tree/main",
        "n": {
            "vectors": facts["vectors"]["total"],
            "families": len(facts["vectors"]["families"]),
            "bundles": len(facts["bundles"]),
            "shipped_objects": shipped_objects,
            "example_objects": facts["examples"]["objects"],
            "python_lines": facts["validators"]["python_lines"],
            "powershell_lines": facts["validators"]["powershell_lines"],
            "check_vectors": next((f["vectors"] for f in facts["vectors"]["families"]
                                   if f["name"] == "check"), 0),
            "advice_vectors": next((f["vectors"] for f in facts["vectors"]["families"]
                                    if f["name"] == "advice"), 0),
            "author_vectors": next((f["vectors"] for f in facts["vectors"]["families"]
                                    if f["name"] == "author"), 0),
            **ledger_counts(),
        },
        "html": fragments(facts, T),
        "demo": demo_digests(),
        "checkdemo": check_demo(),
        "year": str(datetime.date.today().year),
    }
    ctx["html"]["imprint"] = imprint(site, T["build"])
    return ctx




def ledgers():
    """The conversion ledgers (backlog #41), read from the coverage reports the
    converters wrote: one per corpus whose converter follows every source
    value into the bundle. -> [(corpus, ledger)], and the number of corpora
    whose report has none."""
    found, without = [], 0
    root = os.path.join(REPO, "converted_examples")
    for corpus in sorted(os.listdir(root)):
        reports = [f for f in sorted(os.listdir(os.path.join(root, corpus))) if f.endswith("-coverage-report.json")]
        if not reports:
            continue
        ledger = json.loads(read(os.path.join(root, corpus, reports[0]))).get("ledger")
        if ledger is None:
            without += 1
            continue
        t = ledger["totals"]
        if sum(t.values()) != ledger["leaf-values"]:
            die(f"{corpus}: the ledger's totals do not add up to its leaf values")
        if ledger["verification-failures"]:
            die(f"{corpus}: the ledger records {ledger['verification-failures']} failed check(s)")
        found.append((corpus, ledger))
    if not found:
        die("no coverage report carries a ledger")
    return found, without


def ledger_counts():
    """What the pages say about the ledgers, summed over the corpora that
    have one. The pages name these counts and never type them, so a decision
    about an unaccounted value changes no page and no translation."""
    found, without = ledgers()
    t = {k: sum(l["totals"][k] for _, l in found) for k in ("copied", "transformed", "intentionally-dropped", "unaccounted")}
    return {"ledger_corpora": len(found), "ledger_unmeasured": without,
            "ledger_values": sum(l["leaf-values"] for _, l in found), "ledger_copied": t["copied"],
            "ledger_transformed": t["transformed"], "ledger_carried": t["copied"] + t["transformed"],
            "ledger_dropped": t["intentionally-dropped"], "ledger_unaccounted": t["unaccounted"]}


def ledger_rows(sep):
    """One table row per corpus with a ledger; the header is in each page."""
    rows = []
    for corpus, l in ledgers()[0]:
        t = l["totals"]
        cells = [l["leaf-values"], t["copied"], t["transformed"], t["intentionally-dropped"], t["unaccounted"]]
        rows.append('<tr><th scope="row"><span class="corpus-id">' + html.escape(corpus) + "</span></th>"
                    + "".join('<td class="num">' + f"{n:,}".replace(",", sep) + "</td>" for n in cells) + "</tr>")
    return "\n".join(rows)


DEMO_FILE = "req-ism-1234.json"


def demo_digests():
    """The two digests the example bundle's manifest records for the object
    the home page lets a visitor edit."""
    manifest = json.loads(read(os.path.join(REPO, "jascon", "examples", "content-manifest.json")))
    for entry in manifest["objects"]:
        if entry.get("path") == DEMO_FILE:
            return {"package": entry["package-digest"], "semantic": entry["semantic-digest"]}
    die(f"{DEMO_FILE} is not in the example bundle's manifest")


def check_demo():
    """The worked example the Check demo evaluates, read from the example
    bundle: the requirement, the Tailoring that binds its parameter, the two
    Checks, and the observations of the two recorded runs."""
    ex = os.path.join(REPO, "jascon", "examples")
    load = lambda name: json.loads(read(os.path.join(ex, name)))
    checks = [load("check-acme-ssh-maxauthtries.json"), load("check-acme-ssh-ciphers.json")]
    tailoring = load("tailoring-acme-linux-prod.json")
    runs = []
    for name in ("assessment-acme-bastion-2026-11-03.json", "assessment-acme-bastion-2026-11-10.json"):
        a = load(name)
        facts = {}
        for row in a["check-results"]:
            facts.update(row["observation"]["facts"])
        date = re.search(r"\d{4}-\d{2}-\d{2}", a["label"])
        runs.append({"label": a["label"], "date": date.group(0) if date else "",
                     "result": a["result"], "facts": facts})
    bound = {op["parameter"]: op["value"] for op in tailoring["operations"] if op["op"] == "set-parameter"}
    return {"checks": [{k: c[k] for k in ("id", "title", "statement-ids", "observes", "criteria")} for c in checks],
            "requirement": load("req-acme-lnx-ssh-1.json"), "bound": bound, "runs": runs}


def imprint(site, words):
    """The publisher block of legal.html. An address is printed only when
    site.json holds one; nothing is invented. The country line is written
    in the page's language (words: the "build" strings of i18n/<lang>.json)."""
    e = html.escape
    imp = site.get("imprint", {})
    address = [words["imprint_country"] if x == "Germany" else x for x in imp.get("address_lines", [])]
    lines = [f"<strong>{e(site['publisher'])}</strong>"] + [e(x) for x in address]
    out = ["<address>" + "<br>".join(lines) + "</address>"]
    colon, stop = e(words["colon"]), e(words["full_stop"])
    if imp.get("email"):
        out.append(f'<p>{e(words["imprint_email"])}{colon}<a href="mailto:{e(imp["email"])}">{e(imp["email"])}</a></p>')
    out.append(f'<p>{e(words["imprint_questions"])}{colon}<a href="{e(site["repo_url"])}/issues" '
               f'rel="noopener">{e(words["imprint_issue"])}</a>{stop}</p>')
    if imp.get("responsible_for_content"):
        out.append(f"<p>{e(words['imprint_responsible'])}{colon}{e(imp['responsible_for_content'])}</p>")
    return "\n".join(out)


# ---------------------------------------------------------------- pages

TOKEN = re.compile(r"\{\{\s*([^{}]+?)\s*\}\}")
INCLUDE = re.compile(r"\{\{\s*include:([^{}]+?)\s*\}\}")


def partial(name, lang):
    """A partial of src/, in the language's folder when it has one there."""
    own = os.path.join(SRC, lang, name)
    return own if lang != "en" and os.path.isfile(own) else os.path.join(SRC, name)


def render(text, ctx, where):
    def sub(m):
        key = m.group(1)
        if key.startswith("include:"):
            return render(read(partial(key[8:], ctx["lang"]["code"])), ctx, key[8:])
        if key.startswith("file:"):
            return html.escape(read(os.path.join(REPO, key[5:])).rstrip("\n"), quote=False)
        if key.startswith("json:"):
            # a value for a <script type="application/json"> block
            return json.dumps(lookup(ctx, key[5:]), ensure_ascii=False).replace("</", "<\\/")
        value = lookup(ctx, key)
        if value is None:
            die(f"{where}: unknown name {{{{ {key} }}}}")
        if key.startswith("html.") or key in ("content",):
            return value
        if key.endswith("_html"):
            # markup kept in i18n/<lang>.json; its own names are filled in here
            return render(value, ctx, where + " (" + key + ")")
        return html.escape(fmt(value, ctx.get("sep", ",")), quote=True)
    return TOKEN.sub(sub, text)


CODE = re.compile(r'<code data-lang="(json|sh)">(.*?)</code>', re.S)
JSON_TOKEN = re.compile(
    r'(?P<mark>[«»])|(?P<str>"(?:[^"\\\n]|\\.)*")(?P<colon>\s*:)?'
    r'|(?P<num>-?\b\d+(?:\.\d+)?\b)|(?P<kw>\b(?:true|false|null)\b)')


def highlight(text):
    """Colour the code blocks. JSON: member names, strings, numbers,
    literals; « and » set a mark around what the surrounding text points
    at. Shell: one span per line, so that the copy button can leave the
    comment lines out."""
    def json_block(body):
        out, pos = [], 0
        for m in JSON_TOKEN.finditer(body):
            out.append(body[pos:m.start()])
            pos = m.end()
            if m.group("mark"):
                out.append('<span class="mk">' if m.group("mark") == "«" else "</span>")
            elif m.group("str"):
                string = m.group("str")
                if m.group("colon"):
                    out.append(f'<span class="k">{string}</span>{m.group("colon")}')
                else:
                    # a mark may open or close inside a string
                    string = string.replace("«", '</span><span class="mk"><span class="s">') \
                                   .replace("»", '</span></span><span class="s">')
                    out.append(f'<span class="s">{string}</span>')
            elif m.group("num"):
                out.append(f'<span class="n">{m.group("num")}</span>')
            else:
                out.append(f'<span class="b">{m.group("kw")}</span>')
        out.append(body[pos:])
        return "".join(out)

    def sh_block(body):
        lines = []
        for line in body.strip("\n").split("\n"):
            cls = "c" if line.lstrip().startswith("#") else "line"
            lines.append(f'<span class="{cls}">{line}</span>')
        return "\n".join(lines)

    def sub(m):
        body = json_block(m.group(2)) if m.group(1) == "json" else sh_block(m.group(2))
        return f"<code>{body}</code>"
    return CODE.sub(sub, text)


def parse_page(path):
    text = read(path)
    m = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    if not m:
        die(f"{path}: a page starts with a header between two --- lines")
    head = {}
    for line in m.group(1).splitlines():
        if line.strip():
            k, _, v = line.partition(":")
            head[k.strip()] = v.strip()
    for need in ("title", "description"):
        if need not in head:
            die(f"{path}: the header has no '{need}'")
    return head, text[m.end():]


# ---------------------------------------------------------------- languages

def merge(base, over):
    """over on top of base, key by key; what over lacks stays English."""
    out = dict(base)
    for k, v in over.items():
        out[k] = merge(base[k], v) if isinstance(v, dict) and isinstance(base.get(k), dict) else v
    return out


def load_languages(site):
    codes = site.get("languages", ["en"])
    if codes[0] != "en":
        die('site.json: "languages" starts with "en", the language the pages are written in')
    english = json.loads(read(os.path.join(I18N, "en.json")))
    langs = {}
    for code in codes:
        path = os.path.join(I18N, code + ".json")
        if not os.path.isfile(path):
            die(f"site.json names the language {code}, but i18n/{code}.json is missing")
        own = json.loads(read(path))
        if own.get("meta", {}).get("code") != code:
            die(f"i18n/{code}.json: meta.code is not {code!r}")
        langs[code] = merge(english, own)
    return langs


def source_digest(name, lang="en"):
    """What a translation records in its `source:` line: the first twelve
    hex digits of SHA-256 over the English page with its partials set in,
    as written, before any name is filled."""
    text = INCLUDE.sub(lambda m: read(partial(m.group(1), "en")), read(os.path.join(SRC, name)))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def page_names():
    return sorted(n for n in os.listdir(SRC) if n.endswith(".html") and not n.startswith("_"))


def translated(lang):
    folder = os.path.join(SRC, lang)
    if lang == "en":
        return set(page_names())
    if not os.path.isdir(folder):
        return set()
    return {n for n in page_names() if os.path.isfile(os.path.join(folder, n))}


def stamp(spec):
    """--stamp de, --stamp de/index.html: record in the translation that it
    now follows the English page as it stands."""
    lang, _, only = spec.partition("/")
    names = [only] if only else sorted(translated(lang))
    if lang == "en" or not names:
        die(f"--stamp {spec}: no translated page there")
    for name in names:
        path = os.path.join(SRC, lang, name)
        if not os.path.isfile(path):
            die(f"--stamp {spec}: src/{lang}/{name} does not exist")
        text = read(path)
        m = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
        if not m:
            die(f"src/{lang}/{name}: no header")
        lines = [l for l in m.group(1).splitlines() if not l.startswith("source:")]
        lines.append("source: " + source_digest(name))
        write(path, "---\n" + "\n".join(lines) + "\n---\n" + text[m.end():])
        print(f"build.py: src/{lang}/{name} follows the English page {source_digest(name)}")


ABSOLUTE = re.compile(r"^(?:[a-zA-Z][a-zA-Z0-9+.-]*:|#|/|\.\./)")
ATTR = re.compile(r'\b(href|src)="([^"]*)"')


def relink(page, lang, own_pages):
    """Pages of a language live one folder down. A link to a page that
    exists in that language stays as it is; every other relative link
    (assets, the app, the bundles, an untranslated page) goes one folder up.
    "@root/" is the site root, for the language links."""
    up = "" if lang == "en" else "../"

    def fix(m):
        attr, url = m.group(1), m.group(2)
        if url.startswith("@root/"):
            return f'{attr}="{up}{url[6:]}"'
        if lang == "en" or not url or ABSOLUTE.match(url):
            return m.group(0)
        if re.split(r"[#?]", url, maxsplit=1)[0] in own_pages:
            return m.group(0)
        return f'{attr}="../{url}"'
    return ATTR.sub(fix, page)


def language_links(name, lang, langs, site):
    """The language menu, the footer list and the alternate links of a page."""
    e = html.escape
    base = site["base_url"].rstrip("/")
    here = langs[lang]["meta"]
    items, foot, alts = [], [], []
    for code, T in langs.items():
        m = T["meta"]
        has = name in translated(code)
        target = name if has else "index.html"
        folder = "" if code == "en" else code + "/"
        href = "@root/" + folder + target
        current = ' aria-current="true"' if code == lang else ""
        items.append(f'<li><a href="{href}" hreflang="{e(m["hreflang"])}" lang="{e(m["hreflang"])}" data-lang="{code}"{current}>'
                     f'<span>{e(m["name"])}</span><small>{e(m["short"])}</small></a></li>')
        foot.append(f'<a href="{href}" hreflang="{e(m["hreflang"])}" lang="{e(m["hreflang"])}" data-lang="{code}"{current}>{e(m["name"])}</a>')
        if has:
            alts.append(f'<link rel="alternate" hreflang="{e(m["hreflang"])}" '
                        f'href="{base}/{folder}{"" if target == "index.html" else target}">')
    if len(alts) > 1:
        alts.append(f'<link rel="alternate" hreflang="x-default" href="{base}/{"" if name == "index.html" else name}">')
    else:
        alts = []
    if len(langs) == 1:
        return {"lang_menu": "", "lang_foot": "", "alternates": "", "lang_auto": ""}
    menu = ('<details class="lang-pick" id="lang">'
            f'<summary aria-label="{e(langs[lang]["layout"]["lang_label"])}" title="{e(langs[lang]["layout"]["lang_label"])}">'
            '<svg viewBox="0 0 24 24" width="17" height="17" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none" '
            'stroke="currentColor" stroke-width="1.6"/><path d="M3 12h18M12 3c2.6 2.6 3.9 5.6 3.9 9s-1.3 6.4-3.9 9c-2.6-2.6'
            '-3.9-5.6-3.9-9s1.3-6.4 3.9-9z" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/></svg>'
            f'<span>{e(here["short"])}</span></summary>'
            '<ul>' + "".join(items) + "</ul></details>")
    foot = (f'<nav class="foot-langs" aria-label="{e(langs[lang]["layout"]["foot_languages"])}">'
            + " ".join(foot) + "</nav>")
    return {"lang_menu": menu, "lang_foot": foot, "alternates": "\n".join(alts),
            "lang_auto": auto_language(name, lang, langs)}


# The language a visit opens in. Only an English page moves, and only to a
# translation of itself: to the language picked in the menu (stored by
# site.js), or, before any pick and on arrival from another site, to the
# first language of the browser's list that the site offers. English, or no
# match, keeps the page. A translated page never moves, so a shared link
# stays in its language; a link within the site never moves either.
# Traditional Chinese (zh-Hant, -TW, -HK, -MO) is not taken for zh.
AUTO_LANGUAGE = (
    '<script>/* language: the one picked in the menu, else the browser\'s; English if none */'
    '(function(){var to=%s,pick=null;'
    'try{pick=localStorage.getItem("jascon-site:lang")}catch(e){}'
    'if(!pick){try{if(document.referrer&&new URL(document.referrer).origin===location.origin)return}catch(e){}'
    'var ls=navigator.languages&&navigator.languages.length?navigator.languages:[navigator.language||""];'
    'for(var i=0;i<ls.length&&!pick;i++){var l=String(ls[i]).toLowerCase(),p=l.split("-")[0];'
    'if(p==="en")pick="en";else if(p==="zh"){if(!/hant|-tw|-hk|-mo/.test(l))pick="zh"}else if(to[p])pick=p}}'
    'if(pick&&to[pick])location.replace(to[pick]+location.hash)})()</script>')


def auto_language(name, lang, langs):
    if lang != "en" or len(langs) == 1:
        return ""
    targets = {code: f"{code}/{name}" for code in langs if code != "en" and name in translated(code)}
    if not targets:
        return ""
    return AUTO_LANGUAGE % json.dumps(targets, separators=(",", ":"))


def build_pages(out, langs, facts, site):
    layout = read(os.path.join(SRC, "_layout.html"))
    english = {n: parse_page(os.path.join(SRC, n)) for n in page_names()}
    pages, stale = [], []
    for lang, T in langs.items():
        ctx = context(facts, site, T)
        own_pages = translated(lang)
        folder = "" if lang == "en" else lang + "/"
        for name in page_names():
            if name not in own_pages:
                continue
            head, body = english[name]
            behind = False
            if lang != "en":
                own_head, body = parse_page(os.path.join(SRC, lang, name))
                head = dict(head, title=own_head["title"], description=own_head["description"])
                behind = own_head.get("source") != source_digest(name)
                if behind:
                    stale.append(f"{lang}/{name}")
                else:
                    problems = check_translation.compare(lang, name)
                    if problems:
                        die(f"src/{lang}/{name} does not have the structure of src/{name} "
                            "(python3 website/i18n/check_translation.py " + lang + " " + name + "):\n  "
                            + "\n  ".join(problems))
            page_ctx = dict(ctx)
            page_ctx["page"] = {
                "title": head["title"],
                "description": head["description"],
                "file": name,
                "url": ctx["site"]["base_url"].rstrip("/") + "/" + folder + ("" if name == "index.html" else name),
                "body_class": head.get("class", ""),
                "robots": head.get("robots", "index, follow"),
                "en_href": "@root/" + name,
            }
            notes = {
                "base_tag": '<base href="/">' if head.get("base") else "",
                "root_attr": "" if lang == "en" else ' data-root="../"',
                "translated": "" if lang == "en" else
                    '<p class="foot-i18n">' + render(T["layout"]["translated_html"], page_ctx, name) + "</p>",
                "stale": "" if not behind else
                    '<div class="i18n-note" role="note"><div class="wrap"><p>'
                    + render(T["layout"]["stale_html"], page_ctx, name) + "</p></div></div>",
            }
            links = language_links(name, lang, langs, site)
            if head.get("base") or head.get("robots", "").startswith("noindex"):
                links["lang_auto"] = ""  # the 404 page stays where the visitor is
            page_ctx["html"] = dict(ctx["html"], **notes, **links)
            page_ctx["content"] = highlight(render(body, page_ctx, folder + name))
            page = render(layout, page_ctx, "_layout.html")
            # the current page in the navigation
            nav = head.get("nav", "")
            page = re.sub(r'\sdata-nav="([^"]*)"',
                          lambda m: ' aria-current="page"' if m.group(1) == nav and nav else "",
                          page)
            page = relink(page, lang, own_pages)
            write(os.path.join(out, folder, name), page)
            pages.append((folder + name, head))
    if stale:
        print("build.py: note - these translations are older than their English page; they say so "
              "to the reader until they are brought up to date and stamped (build.py --stamp):\n  "
              + "\n  ".join(stale))
    return pages


# ---------------------------------------------------------------- copies

def copy_tree(src, dst, ignore=None):
    shutil.copytree(src, dst, ignore=ignore, dirs_exist_ok=True)


def remove_tree(path):
    """rmtree that also removes read-only entries.

    On Windows a folder of the repository can carry the read-only attribute;
    copytree copies it into the output (copystat), and the next build's
    rmtree then fails with "access denied" on that folder. Clear the mark
    and try once more."""
    def clear_and_retry(func, p, _exc):
        os.chmod(p, 0o700)
        func(p)
    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=clear_and_retry)
    else:
        shutil.rmtree(path, onerror=clear_and_retry)


def copy_apps(out, facts):
    copy_tree(os.path.join(REPO, "jascon-app"), os.path.join(out, "app"),
              ignore=shutil.ignore_patterns("tests", "tools", "PROGRESS.md", "ERRATA.md"))
    os.makedirs(os.path.join(out, "reader"), exist_ok=True)
    shutil.copy2(os.path.join(REPO, "one-page-apps", "jascon-reader.html"),
                 os.path.join(out, "reader", "index.html"))
    os.makedirs(os.path.join(out, "pack-builder"), exist_ok=True)
    shutil.copy2(os.path.join(REPO, "one-page-apps", "jascon-pack-builder.html"),
                 os.path.join(out, "pack-builder", "index.html"))
    for b in facts["bundles"]:
        corpus_src = os.path.join(REPO, "converted_examples", b["corpus"])
        corpus_dst = os.path.join(out, "converted_examples", b["corpus"])
        licence = os.path.join(corpus_src, "SOURCE-LICENSE.md")
        if not os.path.isfile(licence):
            die(f"{b['corpus']} has no SOURCE-LICENSE.md; a bundle is not published without its terms")
        os.makedirs(corpus_dst, exist_ok=True)
        for name in os.listdir(corpus_src):
            path = os.path.join(corpus_src, name)
            if name.endswith("-core-bundle"):
                copy_tree(path, os.path.join(corpus_dst, name))
            elif os.path.isfile(path) and name.endswith(".md"):
                shutil.copy2(path, os.path.join(corpus_dst, name))
    for part in ("examples", "example-packs", "schemas", "conformance"):
        if os.path.isdir(os.path.join(REPO, "jascon", part)):
            copy_tree(os.path.join(REPO, "jascon", part), os.path.join(out, "jascon", part))
    for name in ("LICENSE", "NOTICE"):
        shutil.copy2(os.path.join(REPO, name), os.path.join(out, name + ".txt"))
    # Folder listings for what a manifest does not name. A pack manifest a set
    # keeps (packs/sha256/<hex>) and an Attestation lie beside the manifest;
    # the app and the reader find them by asking the server for the folder,
    # which a static host answers only with an index.html. Every bundle served
    # is listed: since 2026-11-14 the reader asks for the folder of whatever
    # bundle it loads from a URL (backlog #46), and the IFA bundle has its
    # Attestation there.
    listed = [os.path.join(out, "jascon", "examples"),
              os.path.join(out, "jascon", "examples", "packs", "sha256")]
    listed += [os.path.join(out, *b["path"].split("/")) for b in facts["bundles"]]
    packs_dir = os.path.join(out, "jascon", "example-packs")
    if os.path.isdir(packs_dir):
        listed += [os.path.join(packs_dir, d) for d in sorted(os.listdir(packs_dir))
                   if os.path.isdir(os.path.join(packs_dir, d))]
    for folder in listed:
        if os.path.isdir(folder):
            write_listing(folder)


def write_listing(folder):
    """A plain index.html that lists a folder, as a web server with directory
    listings would: one link per entry, folders with a trailing slash."""
    entries = []
    for name in sorted(os.listdir(folder)):
        if name == "index.html":
            continue
        entries.append(name + "/" if os.path.isdir(os.path.join(folder, name)) else name)
    links = "\n".join(f'<li><a href="{html.escape(urllib.parse.quote(n))}">{html.escape(n)}</a></li>'
                      for n in entries)
    with open(os.path.join(folder, "index.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
                "<meta name=\"robots\" content=\"noindex\"><title>Files</title></head>\n"
                f"<body><h1>Files in this folder</h1>\n<ul>\n{links}\n</ul>\n</body></html>\n")


def write_meta(out, pages, site):
    base = site["base_url"].rstrip("/")
    today = datetime.date.today().isoformat()
    urls = []
    for name, head in pages:
        if head.get("robots", "").startswith("noindex") or name == "404.html":
            continue
        loc = base + "/" + re.sub(r"(^|/)index\.html$", r"\1", name)
        urls.append(f"  <url><loc>{loc}</loc><lastmod>{today}</lastmod></url>")
    write(os.path.join(out, "sitemap.xml"),
          '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + "\n".join(urls) + "\n</urlset>\n")
    write(os.path.join(out, "robots.txt"),
          "User-agent: *\nAllow: /\nDisallow: /converted_examples/\nDisallow: /jascon/\n\n"
          f"Sitemap: {base}/sitemap.xml\n")
    # GitHub Pages: serve folders and files as they are, no Jekyll pass
    write(os.path.join(out, ".nojekyll"), "")


# ---------------------------------------------------------------- checks

LINK = re.compile(r'(?:href|src)="([^"]+)"')


def check_links(out, pages, pages_only):
    skipped = ("app/", "reader/", "pack-builder/", "converted_examples/", "jascon/", "LICENSE.txt", "NOTICE.txt")
    broken = []
    for name, _ in pages:
        text = read(os.path.join(out, name))
        here = os.path.dirname(name)
        ids = set(re.findall(r'\sid="([^"]+)"', text))
        for target in LINK.findall(text):
            if target == "/" or re.match(r"^(https?:|mailto:|data:|#$)", target):  # "/" is the <base> of 404.html
                continue
            path, _, frag = target.partition("#")
            if not path:
                if frag and frag not in ids:
                    broken.append(f"{name}: #{frag} names no id on the page")
                continue
            # relative to the page's folder (a language's pages are one down)
            path = os.path.normpath(os.path.join(here, path)).replace(os.sep, "/")
            if path.startswith("../"):
                broken.append(f"{name}: {target} leaves the site")
                continue
            if pages_only and path.startswith(skipped):
                continue
            full = os.path.join(out, path)
            if os.path.isdir(full):
                full = os.path.join(full, "index.html")
            if not os.path.isfile(full):
                broken.append(f"{name}: {target} names no file in the output")
            elif frag and path.endswith(".html") and not path.startswith(("app/", "reader/", "pack-builder/")):
                if f'id="{frag}"' not in read(full):
                    broken.append(f"{name}: {target} names no id in {path}")
    if not pages_only:
        for engine in ("app/jascon-schema.js", "app/jascon-rules.js"):
            if not os.path.isfile(os.path.join(out, engine)):
                broken.append(f"{engine} is missing; the Check demo loads it")
    if broken:
        die("broken links:\n  " + "\n  ".join(broken))


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", default=os.path.join(REPO, "_site"))
    ap.add_argument("--measure", action="store_true",
                    help="run the reference validator and rewrite facts.json")
    ap.add_argument("--pages-only", action="store_true",
                    help="skip the app, the reader and the bundles")
    ap.add_argument("--stamp", metavar="LANG[/PAGE]",
                    help="record that the translations of LANG (or one page) follow the English pages "
                         "as they stand now, then stop")
    args = ap.parse_args()
    if args.stamp:
        stamp(args.stamp)
        return
    out = os.path.abspath(args.out)
    if out in (REPO, HERE) or REPO.startswith(out + os.sep):
        die("--out must not be the repository or a folder above it")

    if args.measure:
        facts = measure()
        write(FACTS, json.dumps(facts, indent=1, ensure_ascii=False) + "\n")
    elif os.path.isfile(FACTS):
        facts = json.loads(read(FACTS))
    else:
        die("facts.json is missing; run with --measure")
    site = json.loads(read(SITE))

    if os.path.isdir(out):
        remove_tree(out)
    os.makedirs(out)
    copy_tree(STATIC, out)
    langs = load_languages(site)
    pages = build_pages(out, langs, facts, site)
    if not args.pages_only:
        copy_apps(out, facts)
    write_meta(out, pages, site)
    check_links(out, pages, args.pages_only)

    if not site.get("imprint", {}).get("address_lines"):
        print("build.py: note - site.json has no imprint address; legal.html names the "
              "publisher and the contact only (see website/README.md, 'Before going live')")
    size = sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(out) for f in fs)
    print(f"build.py: {len(pages)} pages in {len(langs)} languages, {size / 1e6:.1f} MB in {out} "
          f"(facts of {facts['measured']['date']}, commit {facts['measured']['commit']})")


if __name__ == "__main__":
    main()
