#!/usr/bin/env python3
"""Check that a translated page has the structure of its English page.

    python3 website/i18n/check_translation.py de index.html
    python3 website/i18n/check_translation.py de          # every page of de

A translation changes words, not the page. Compared with src/<page>:

1. the sequence of block elements (sections, paragraphs, list items, table
   cells, form parts) with their attributes;
2. the multiset of every element with its attributes, inline ones included
   (their order inside a block may change with the word order);
3. the multiset of {{ names }};
4. the text of <pre>, <code>, <kbd>, <script> and <textarea>, which stays
   English (the comment lines of a shell block may be translated).

Attributes a reader sees (title, aria-label, alt, placeholder) are left out
of the comparison. build.py runs this check on every translation that is
current and stops when one fails. Standard library only.
"""
import collections
import html.parser
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(HERE), "src")

TRANSLATABLE_ATTRS = {"title", "aria-label", "alt", "placeholder"}
BLOCK = {"section", "div", "header", "footer", "nav", "article", "aside", "figure", "figcaption",
         "p", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "li", "dl", "dt", "dd",
         "table", "thead", "tbody", "tfoot", "tr", "th", "td", "pre", "blockquote",
         "details", "summary", "form", "fieldset", "legend", "label", "input", "button",
         "select", "option", "textarea", "script", "img", "svg", "g", "picture", "source"}
VERBATIM = {"pre", "code", "kbd", "script", "textarea"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source",
        "track", "wbr", "path", "rect", "circle", "line", "polyline", "polygon", "ellipse", "use", "stop"}
NAME = re.compile(r"\{\{\s*([^{}]+?)\s*\}\}")


class Shape(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks, self.tags, self.verbatim = [], collections.Counter(), collections.Counter()
        self.stack, self.buf = [], None

    def handle_starttag(self, tag, attrs):
        kept = tuple(sorted((k, v) for k, v in attrs if k not in TRANSLATABLE_ATTRS))
        self.tags[(tag, kept)] += 1
        if tag in BLOCK:
            self.blocks.append((tag, kept))
        if tag in VERBATIM and self.buf is None:
            self.buf = [tag, [], False]
        if self.buf is not None and tag == "code" and ("data-lang", "sh") in kept:
            self.buf[2] = True  # a shell block, also when a <pre> holds it
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        if tag in self.stack:
            while self.stack and self.stack.pop() != tag:
                pass
        if self.buf is not None and tag == self.buf[0] and tag not in self.stack:
            kind, parts, shell = self.buf
            text = "".join(parts)
            if shell:
                text = "\n".join(l for l in text.split("\n") if not l.lstrip().startswith("#"))
            self.verbatim[(kind, text.strip())] += 1
            self.buf = None

    def handle_data(self, data):
        if self.buf is not None:
            self.buf[1].append(data)


def shape(path):
    text = open(path, encoding="utf-8").read()
    m = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    body = text[m.end():] if m else text
    p = Shape()
    p.feed(body)
    p.close()
    return p, collections.Counter(NAME.findall(body))


def diff_counter(a, b):
    out = []
    for k in sorted(set(a) | set(b), key=repr):
        if a[k] != b[k]:
            out.append(f"{a[k]} in English, {b[k]} in the translation: {k!r}"[:300])
    return out


def compare(lang, name):
    english, names_en = shape(os.path.join(SRC, name))
    other, names_t = shape(os.path.join(SRC, lang, name))
    problems = []
    if english.blocks != other.blocks:
        for i, (a, b) in enumerate(zip(english.blocks, other.blocks)):
            if a != b:
                problems.append(f"block {i}: English {a!r}, translation {b!r}"[:400])
                break
        else:
            problems.append(f"{len(english.blocks)} block elements in English, {len(other.blocks)} in the translation")
    problems += ["element " + d for d in diff_counter(english.tags, other.tags)][:12]
    problems += ["name " + d for d in diff_counter(names_en, names_t)]
    problems += ["code " + d for d in diff_counter(english.verbatim, other.verbatim)][:12]
    return problems


def main(argv):
    if not argv or len(argv) > 2:
        sys.exit(__doc__)
    lang = argv[0]
    names = [argv[1]] if len(argv) == 2 else sorted(
        n for n in os.listdir(os.path.join(SRC, lang)) if n.endswith(".html"))
    bad = 0
    for name in names:
        problems = compare(lang, name)
        print(f"{lang}/{name}: " + ("same structure" if not problems else f"{len(problems)} problem(s)"))
        for p in problems:
            print("   ", p)
        bad += bool(problems)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
