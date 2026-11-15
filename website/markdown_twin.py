"""The Markdown twin of a built page, for readers that are programs.

A language model or an agent reads a page best as plain text with its
structure kept: headings, lists, tables, code. This module turns the <main>
element of a page the build has written into Markdown, with nothing but
Python's standard library. The twin is generated from the same HTML a person
reads, so the two cannot say different things.

What it keeps and what it drops:

- headings, paragraphs, lists, tables (as GFM tables), code blocks with the
  language the page gives them, inline code, bold and italic;
- links, made absolute against the page's own address, so the text stays
  usable when it is read away from the site;
- an inline SVG diagram as its <title> and <desc>, which the pages write to
  say in words what the drawing shows;
- the state chains of the pages (`a -> b -> c`) and the title bar of a code
  window as a caption above the code;
- nothing that only works on screen: scripts, styles, buttons, form fields,
  and every element marked aria-hidden.
"""

import html.parser
import re
import urllib.parse

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "source", "track", "wbr"}
SKIP = {"script", "style", "button", "select", "input", "template", "noscript", "option"}
BLOCK = {"address", "article", "aside", "blockquote", "details", "div", "dl", "fieldset",
         "figcaption", "figure", "footer", "form", "h1", "h2", "h3", "h4", "h5", "h6",
         "header", "hr", "li", "main", "nav", "ol", "p", "pre", "section", "summary",
         "svg", "table", "textarea", "ul"}


class Node:
    __slots__ = ("tag", "attrs", "children")

    def __init__(self, tag, attrs):
        self.tag = tag
        self.attrs = dict(attrs)
        self.children = []

    def cls(self):
        return self.attrs.get("class", "").split()

    def text(self):
        """Every piece of text below this node, as it stands."""
        return "".join(c if isinstance(c, str) else c.text() for c in self.children)

    def find(self, tag=None, cls=None):
        for c in self.children:
            if isinstance(c, Node):
                if (tag is None or c.tag == tag) and (cls is None or cls in c.cls()):
                    return c
                hit = c.find(tag, cls)
                if hit is not None:
                    return hit
        return None


class TreeBuilder(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root", [])
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.stack[-1].children.append(Node(tag, attrs))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def hidden(node):
    return (node.tag in SKIP or node.attrs.get("aria-hidden") == "true"
            or "copy" in node.cls() or "skip" in node.cls())


def squash(s):
    return re.sub(r"\s+", " ", s)


class Renderer:
    def __init__(self, page_url):
        self.page_url = page_url

    # ---- inline

    def inline(self, node):
        out = []
        for c in node.children:
            if isinstance(c, str):
                out.append(squash(c))
            elif not hidden(c):
                out.append(self.inline_node(c))
        return "".join(out)

    def inline_node(self, n):
        t = n.tag
        if t == "br":
            return "\n"
        if t == "img":
            return n.attrs.get("alt", "")
        if t == "code":
            s = squash(n.text()).strip()
            if not s:
                return ""
            tick = "``" if "`" in s else "`"
            return f"{tick}{s}{tick}"
        inner = self.inline(n)
        if t in ("b", "strong"):
            return f"**{inner.strip()}**" if inner.strip() else ""
        if t in ("em", "i"):
            return f"*{inner.strip()}*" if inner.strip() else ""
        if t == "a":
            href = n.attrs.get("href", "")
            label = inner.strip()
            if not href or not label:
                return inner
            return f"[{label}]({urllib.parse.urljoin(self.page_url, href)})"
        if t in BLOCK:  # a block inside inline content: keep its words
            return " " + inner + " "
        return inner

    def para(self, node):
        s = self.inline(node)
        s = re.sub(r"[ \t]*\n[ \t]*", "\n", s)
        s = re.sub(r" {2,}", " ", s).strip()
        # a bold label set as a block of its own runs into the next word
        return re.sub(r"\*\*([^*\n]+)\*\*(?=[^\s.,;:)\]*])", r"**\1** ", s)

    # ---- blocks

    def blocks(self, node):
        """The children of a container as a list of Markdown blocks;
        inline neighbours are gathered into one paragraph."""
        out, run = [], Node("#run", [])

        def flush():
            if run.children:
                s = self.para(run)
                if s:
                    out.append(s)
                run.children = []

        for c in node.children:
            if isinstance(c, Node) and hidden(c):
                continue
            if isinstance(c, Node) and c.tag in BLOCK:
                flush()
                out.extend(self.block(c))
            else:
                run.children.append(c)
        flush()
        return out

    def block(self, n):
        t, cls = n.tag, n.cls()
        if t in ("h1", "h2", "h3", "h4", "h5", "h6"):
            s = self.para(n)
            return [f"{'#' * int(t[1])} {s}"] if s else []
        if t == "p":
            s = self.para(n)
            return [s] if s else []
        if t in ("ul", "ol"):
            items = []
            for i, li in enumerate((c for c in n.children if isinstance(c, Node) and c.tag == "li"), 1):
                body = " ".join(b.replace("\n", " ") for b in self.blocks(li)).strip()
                if body:
                    items.append(f"{i}. {body}" if t == "ol" else f"- {body}")
            return ["\n".join(items)] if items else []
        if t == "table":
            return self.table(n)
        if t == "pre":
            return [self.code(n)]
        if t == "textarea":
            return [self.code(n)]
        if t == "svg":
            title = n.find("title")
            desc = n.find("desc")
            parts = [squash(x.text()).strip() for x in (title, desc) if x is not None]
            parts = [p for p in parts if p]
            if not parts:
                return []
            return [f"*Figure: {parts[0]}.*" + (f" {parts[1]}" if len(parts) > 1 else "")]
        if t == "hr":
            return ["---"]
        if t == "div" and "chain" in cls:
            steps = [squash(c.text()).strip() for c in n.children
                     if isinstance(c, Node) and c.tag == "span"]
            steps = [s for s in steps if s]
            return [" → ".join(f"`{s}`" for s in steps)] if steps else []
        if t == "div" and "graph-legend" in cls:
            keys = [squash(c.text()).strip() for c in n.children if isinstance(c, Node) and c.tag == "span"]
            keys = [k for k in keys if k]
            return ["*" + "; ".join(keys) + "*"] if keys else []
        if t == "div" and "window-bar" in cls:
            parts = [squash(c.text()).strip() for c in n.children
                     if isinstance(c, Node) and not hidden(c) and ("window-title" in c.cls() or "window-note" in c.cls())]
            parts = [p for p in parts if p]
            return [f"*{' — '.join(parts)}*"] if parts else []
        if t == "figcaption":
            s = self.para(n)
            return [f"*{s}*"] if s else []
        return self.blocks(n)

    def code(self, n):
        inner = n.find("code")
        lang = ""
        for node in (inner, n):
            if node is not None:
                lang = lang or node.attrs.get("data-lang", "") or next(
                    (c[len("language-"):] for c in node.cls() if c.startswith("language-")), "")
        body = n.text().strip("\n")
        fence = "````" if "```" in body else "```"
        return f"{fence}{lang}\n{body}\n{fence}"

    def table(self, n):
        rows = []

        def walk(node):
            for c in node.children:
                if not isinstance(c, Node):
                    continue
                if c.tag == "tr":
                    cells = [self.para(x).replace("\n", " ").replace("|", "\\|")
                             for x in c.children if isinstance(x, Node) and x.tag in ("th", "td")]
                    rows.append(cells)
                elif c.tag in ("thead", "tbody", "tfoot"):
                    walk(c)
        walk(n)
        rows = [r for r in rows if r]
        if not rows:
            return []
        width = max(len(r) for r in rows)
        rows = [r + [""] * (width - len(r)) for r in rows]
        lines = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * width]
        lines += ["| " + " | ".join(r) + " |" for r in rows[1:]]
        return ["\n".join(lines)]


def to_markdown(page_html, page_url, meta):
    """The Markdown twin of one built page. `meta` gives title, description,
    lang and the address of the HTML page; they open the text as front
    matter, so a reader knows what it holds and where it came from."""
    tb = TreeBuilder()
    tb.feed(page_html)
    main = tb.root.find("main")
    if main is None:
        raise ValueError(f"{page_url}: the page has no <main>")
    body = "\n\n".join(Renderer(page_url).blocks(main))
    body = re.sub(r"\n{3,}", "\n\n", body).strip()

    def q(s):
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    front = ("---\n"
             f"title: {q(meta['title'])}\n"
             f"description: {q(meta['description'])}\n"
             f"lang: {meta['lang']}\n"
             f"url: {page_url}\n"
             "---\n\n")
    return front + body + "\n"
