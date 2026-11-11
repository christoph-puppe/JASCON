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
   an unknown name stops the build.
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
import html
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SRC = os.path.join(HERE, "src")
STATIC = os.path.join(HERE, "static")
FACTS = os.path.join(HERE, "facts.json")
SITE = os.path.join(HERE, "site.json")

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


def measure():
    """Run the reference validator and read its report."""
    print("build.py: running", VALIDATOR_PY, "...")
    run = subprocess.run([sys.executable, os.path.join(REPO, VALIDATOR_PY)],
                         cwd=REPO, capture_output=True, text=True)
    out = run.stdout
    if run.returncode != 0 or "ALL GREEN" not in out:
        sys.stderr.write(out[-3000:] + run.stderr[-3000:])
        die("the reference validator is not ALL GREEN; nothing was built")

    families, bundles, examples, example_types = [], [], 0, {}
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
            else:
                corpus = name.split("/")[1]
                if corpus not in CORPORA:
                    die(f"bundle {name} has no entry in CORPORA; add its title and licence")
                bundles.append({"corpus": corpus, "path": name,
                                "objects": sum(counts.values()), "types": counts})
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
        "validators": {
            "python_lines": count_lines(os.path.join(REPO, VALIDATOR_PY)),
            "powershell_lines": count_lines(os.path.join(REPO, VALIDATOR_PS)),
        },
    }


# ---------------------------------------------------------------- values

def fmt(value):
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, int):
        return f"{value:,}"
    return str(value)


def lookup(ctx, dotted):
    cur = ctx
    for part in dotted.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur


def fragments(facts):
    """HTML built from the facts: table rows and lists the pages place."""
    e = html.escape
    fam = facts["vectors"]["families"]
    family_rows = "\n".join(
        f'<tr><td><code>{e(f["name"])}</code></td><td class="num">{f["vectors"]}</td></tr>'
        for f in fam)
    family_chips = "\n".join(
        f'<li><code>{e(f["name"])}</code><span>{f["vectors"]}</span></li>' for f in fam)

    rows = []
    for b in facts["bundles"]:
        c = CORPORA[b["corpus"]]
        kinds = " · ".join(f'{n:,} {TYPE_LABELS.get(t, t)}{"" if n == 1 else "s"}' for t, n in
                           sorted(b["types"].items(), key=lambda kv: -kv[1]))
        bundle_dir = b["path"].split("/", 1)[1]
        tool = "assess" if "assessment" in b["types"] else "browse"
        rows.append(
            "<tr>"
            f'<th scope="row"><span class="corpus-id">{e(b["corpus"])}</span>'
            f'{e(c["title"])}<small>{e(c["publisher"])}</small></th>'
            f'<td class="num">{b["objects"]:,}</td>'
            f"<td>{e(kinds)}<small>{e(c['note'])}</small></td>"
            f'<td><a href="converted_examples/{e(b["corpus"])}/SOURCE-LICENSE.md">{e(c["licence"])}</a></td>'
            f'<td><a class="open" href="app/index.html#load=../converted_examples/{e(bundle_dir)}/&amp;tool={tool}">'
            "Open in the app</a></td>"
            "</tr>")
    return {
        "family_rows": family_rows,
        "family_chips": family_chips,
        "bundle_rows": "\n".join(rows),
    }


def context(facts, site):
    shipped_objects = sum(b["objects"] for b in facts["bundles"])
    ctx = {
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
        },
        "html": fragments(facts),
        "demo": demo_digests(),
        "year": str(datetime.date.today().year),
    }
    ctx["html"]["imprint"] = imprint(site)
    return ctx


DEMO_FILE = "req-ism-1234.json"


def demo_digests():
    """The two digests the example bundle's manifest records for the object
    the home page lets a visitor edit."""
    manifest = json.loads(read(os.path.join(REPO, "jascon", "examples", "content-manifest.json")))
    for entry in manifest["objects"]:
        if entry.get("path") == DEMO_FILE:
            return {"package": entry["package-digest"], "semantic": entry["semantic-digest"]}
    die(f"{DEMO_FILE} is not in the example bundle's manifest")


def imprint(site):
    """The publisher block of legal.html. An address is printed only when
    site.json holds one; nothing is invented."""
    e = html.escape
    imp = site.get("imprint", {})
    lines = [f"<strong>{e(site['publisher'])}</strong>"] + [e(x) for x in imp.get("address_lines", [])]
    out = ["<address>" + "<br>".join(lines) + "</address>"]
    if imp.get("email"):
        out.append(f'<p>E-mail: <a href="mailto:{e(imp["email"])}">{e(imp["email"])}</a></p>')
    out.append(f'<p>Questions, corrections and objections: <a href="{e(site["repo_url"])}/issues" '
               'rel="noopener">an issue in the repository</a>.</p>')
    if imp.get("responsible_for_content"):
        out.append(f"<p>Responsible for the content: {e(imp['responsible_for_content'])}</p>")
    return "\n".join(out)


# ---------------------------------------------------------------- pages

TOKEN = re.compile(r"\{\{\s*([^{}]+?)\s*\}\}")


def render(text, ctx, where):
    def sub(m):
        key = m.group(1)
        if key.startswith("file:"):
            return html.escape(read(os.path.join(REPO, key[5:])).rstrip("\n"), quote=False)
        if key.startswith("json:"):
            # a value for a <script type="application/json"> block
            return json.dumps(lookup(ctx, key[5:]), ensure_ascii=False).replace("</", "<\\/")
        value = lookup(ctx, key)
        if value is None:
            die(f"{where}: unknown name {{{{ {key} }}}}")
        if key.startswith("html.") or key == "content":
            return value
        return html.escape(fmt(value), quote=True)
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


def build_pages(out, ctx):
    layout = read(os.path.join(SRC, "_layout.html"))
    pages = []
    for name in sorted(os.listdir(SRC)):
        if name.startswith("_") or not name.endswith(".html"):
            continue
        head, body = parse_page(os.path.join(SRC, name))
        page_ctx = dict(ctx)
        page_ctx["page"] = {
            "title": head["title"],
            "description": head["description"],
            "file": name,
            "url": ctx["site"]["base_url"].rstrip("/") + "/" + ("" if name == "index.html" else name),
            "body_class": head.get("class", ""),
            "robots": head.get("robots", "index, follow"),
        }
        page_ctx["html"] = dict(ctx["html"], base_tag='<base href="/">' if head.get("base") else "")
        page_ctx["content"] = highlight(render(body, page_ctx, name))
        page = render(layout, page_ctx, "_layout.html")
        # the current page in the navigation
        nav = head.get("nav", "")
        page = re.sub(r'\sdata-nav="([^"]*)"',
                      lambda m: ' aria-current="page"' if m.group(1) == nav and nav else "",
                      page)
        write(os.path.join(out, name), page)
        pages.append((name, head))
    return pages


# ---------------------------------------------------------------- copies

def copy_tree(src, dst, ignore=None):
    shutil.copytree(src, dst, ignore=ignore, dirs_exist_ok=True)


def copy_apps(out, facts):
    copy_tree(os.path.join(REPO, "jascon-app"), os.path.join(out, "app"),
              ignore=shutil.ignore_patterns("tests", "tools", "PROGRESS.md", "ERRATA.md"))
    os.makedirs(os.path.join(out, "reader"), exist_ok=True)
    shutil.copy2(os.path.join(REPO, "one-page-apps", "jascon-reader.html"),
                 os.path.join(out, "reader", "index.html"))
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
    for part in ("examples", "schemas", "conformance"):
        copy_tree(os.path.join(REPO, "jascon", part), os.path.join(out, "jascon", part))
    for name in ("LICENSE", "NOTICE"):
        shutil.copy2(os.path.join(REPO, name), os.path.join(out, name + ".txt"))


def write_meta(out, pages, site):
    base = site["base_url"].rstrip("/")
    today = datetime.date.today().isoformat()
    urls = []
    for name, head in pages:
        if head.get("robots", "").startswith("noindex") or name == "404.html":
            continue
        loc = base + "/" + ("" if name == "index.html" else name)
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
    skipped = ("app/", "reader/", "converted_examples/", "jascon/", "LICENSE.txt", "NOTICE.txt")
    broken = []
    for name, _ in pages:
        text = read(os.path.join(out, name))
        ids = set(re.findall(r'\sid="([^"]+)"', text))
        for target in LINK.findall(text):
            if target == "/" or re.match(r"^(https?:|mailto:|data:|#$)", target):  # "/" is the <base> of 404.html
                continue
            path, _, frag = target.partition("#")
            if not path:
                if frag and frag not in ids:
                    broken.append(f"{name}: #{frag} names no id on the page")
                continue
            if pages_only and path.startswith(skipped):
                continue
            full = os.path.join(out, path)
            if os.path.isdir(full):
                full = os.path.join(full, "index.html")
            if not os.path.isfile(full):
                broken.append(f"{name}: {target} names no file in the output")
            elif frag and path.endswith(".html") and not path.startswith(("app/", "reader/")):
                if f'id="{frag}"' not in read(full):
                    broken.append(f"{name}: {target} names no id in {path}")
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
    args = ap.parse_args()
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
        shutil.rmtree(out)
    os.makedirs(out)
    copy_tree(STATIC, out)
    ctx = context(facts, site)
    pages = build_pages(out, ctx)
    if not args.pages_only:
        copy_apps(out, facts)
    write_meta(out, pages, site)
    check_links(out, pages, args.pages_only)

    if not site.get("imprint", {}).get("address_lines"):
        print("build.py: note - site.json has no imprint address; legal.html names the "
              "publisher and the contact only (see website/README.md, 'Before going live')")
    size = sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(out) for f in fs)
    print(f"build.py: {len(pages)} pages, {size / 1e6:.1f} MB in {out} "
          f"(facts of {facts['measured']['date']}, commit {facts['measured']['commit']})")


if __name__ == "__main__":
    main()
