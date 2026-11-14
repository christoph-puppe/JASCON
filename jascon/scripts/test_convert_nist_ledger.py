#!/usr/bin/env python3
"""The conversion ledger of convert_nist.py (backlog #41, phase E), held on
an invented catalogue and on the committed conversion.

    python3 jascon/scripts/test_convert_nist_ledger.py

The converter runs when it is imported and reads its sources from a fixed
place, and the repository carries no source. So it is copied, with the
library, into a folder of its own beside five files nobody published: one
small catalogue written below, in the shapes SP 800-53 uses, and four
profiles that select from it. What the real catalogue gives is held by the
Validators workflow, which converts it again from its pinned source and
compares every byte of the folder, the ledger's record among them.

The author's rule of 2026-11-14: content is never dropped, and a run with
an unaccounted value ends with 1. Held here:
  - every source value has one of five outcomes, none is unaccounted, no
    claim fails, and the run ends with 0;
  - what the author's list of losses names is in the written bundle, counted
    from the files: the `assessment-for` links, a withdrawn control without
    a successor, the label of a withdrawn control as the source gives it for
    a reader, the formal ODP labels, the document metadata, `merge.as-is`;
  - what is not in the bundle is no content by a rule of one of three kinds,
    or one of the drops that were declared before that rule, each with a
    reading for the author;
  - the gate is the last statement of the converter;
  - deliberate defects, each put into a copy of the converter or of the
    catalogue, end the run with 1: a value that is lost, a rule that does
    not give the id it claims, a name that selects a value which is not
    written, a prop in a namespace or with a name the mapping is not written
    for, a boolean that is not followed, a written file that says something
    else, and what the ledger cannot see by itself (a drop that reaches
    further than its reason names, a path map that says something else, a
    record that was not written).

Standard library only."""
import ast, collections, hashlib, json, os, re, shutil, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
RMF = "http://csrc.nist.gov/ns/rmf"
NS = "https://ns.nist.gov/sp800-53"
F_53A, F_ODP, F_NARR = f"{NS}/facet/sp800-53a@1", f"{NS}/facet/odp@1", f"{NS}/facet/narrative@1"
F_REF, F_RMF = f"{NS}/facet/references@1", f"{NS}/facet/rmf@1"
F_COMPAT = "https://ns.jascon.net/compat/oscal-1x@1"
PROFILES = ("LOW", "MODERATE", "HIGH", "PRIVACY")
LEDGER = "sp800-53-conversion-ledger.json"
OUTCOMES = ("copied", "transformed", "not-content", "intentionally-dropped", "unaccounted")
# the reasons of the drops that were declared before 2026-11-14 and stay declared: how each begins
DECLARED_BEFORE = ("path map: a withdrawn control is dropped as a tombstone",
                   "path map: the print label of a statement item is derivable",
                   "path map: profile resolution mechanics",
                   "as decided for IFA on 2026-11-13: a back-matter resource or an import link",
                   "as decided for IFA on 2026-11-13: the uuid of a source document")
WITH = " - of a value that is dropped: "
RES_A, RES_B, RES_C = (f"00000000-0000-4000-8000-00000000000{x}" for x in "abc")


def labels(plain, padded):
    return [{"name": "label", "class": "zero-padded", "value": padded}, {"name": "label", "value": plain},
            {"name": "label", "class": "sp800-53a", "value": padded}]

def invented_catalogue():
    """Three controls in force, one of them an enhancement, and three
    withdrawn ones: one merged into a statement, one moved to a control, one
    that names no successor. Ids, labels and sort-ids are formed as SP 800-53
    forms them, the print labels of the statement items on every level a
    control and an enhancement have; one item of the enhancement carries the
    form of a control (`b.`), as three items of SI-2(7) do in 5.2.0."""
    def item(iid, label, prose, *below):
        it = {"id": iid, "name": "item", "props": [{"name": "label", "value": label}], "prose": prose}
        if below: it["parts"] = list(below)
        return it
    c11 = {"id": "c-1.1", "class": "SP800-53-enhancement", "title": "First, enhanced",
           "props": labels("C-1(1)", "C-01(01)") + [{"name": "sort-id", "value": "c-01.01"},
                                                     {"name": "implementation-level", "ns": RMF, "value": "system"}],
           "links": [{"href": "#c-1", "rel": "required"}],
           "params": [{"id": "c-01.01_odp", "label": "interval",
                       "props": [{"name": "label", "class": "sp800-53a", "value": "C-01(01)_ODP"}]}],
           "parts": [{"id": "c-1.1_smt", "name": "statement", "prose": "Do it every {{ insert: param, c-01.01_odp }}:",
                      "parts": [item("c-1.1_smt.a", "(a)", "On the hour;", item("c-1.1_smt.a.1", "(1)", "Sharp; and")),
                                item("c-1.1_smt.b", "b.", "On the half hour.")]}]}
    c1 = {"id": "c-1", "class": "SP800-53", "title": "First",
          "props": labels("C-1", "C-01") + [{"name": "sort-id", "value": "c-01"},
                                             {"name": "implementation-level", "ns": RMF, "value": "organization"},
                                             {"name": "implementation-level", "ns": RMF, "value": "system"},
                                             {"name": "contributes-to-assurance", "ns": RMF, "value": "true"}],
          "links": [{"href": f"#{RES_A}", "rel": "reference"},
                    {"href": "#c-2", "rel": "related"}, {"href": "#w-2", "rel": "related"}],
          "params": [{"id": "c-01_odp", "label": "who decides",
                      "props": [{"name": "label", "class": "sp800-53a", "value": "C-01_ODP"},
                                {"name": "alt-identifier", "value": "c-1_prm_1"},
                                {"name": "alt-label", "class": "sp800-53", "value": "deciders"},
                                {"name": "aggregates", "ns": RMF, "value": "c-01_odp.01"}],
                      "select": {"how-many": "one-or-more", "choice": ["the owner", "the operator"]},
                      "guidelines": [{"prose": "who decides is selected"}]}],
          "parts": [
              {"id": "c-1_smt", "name": "statement", "parts": [
                  item("c-1_smt.a", "a.", "Name {{ insert: param, c-01_odp }}:",
                       item("c-1_smt.a.1", "1.", "By name:", item("c-1_smt.a.1.a", "(a)", "In full; and"))),
                  item("c-1_smt.b", "b.", "Write it down.")]},
              {"id": "c-1_gdn", "name": "guidance",
               "prose": f"See [The paper](#{RES_A}) and [C-2](#c-2)."},
              {"id": "c-1_obj", "name": "assessment-objective", "props": [{"name": "label", "class": "sp800-53a", "value": "C-01"}],
               "links": [{"href": "#c-1_smt", "rel": "assessment-for"}],
               "parts": [{"id": "c-1_obj.a", "name": "assessment-objective",
                          "props": [{"name": "label", "class": "sp800-53a", "value": "C-01a."}],
                          "prose": "somebody is named;", "links": [{"href": "#c-1_smt.a", "rel": "assessment-for"}]},
                         {"id": "c-1_obj.b", "name": "assessment-objective",
                          "props": [{"name": "label", "class": "sp800-53a", "value": "C-01b."}],
                          "prose": "it is kept;", "links": [{"href": "#c-2_smt", "rel": "assessment-for"}]}]},
              {"id": "c-1_asm-examine", "name": "assessment-method",
               "props": [{"name": "method", "ns": RMF, "value": "EXAMINE"}, {"name": "label", "class": "sp800-53a", "value": "C-01-Examine"}],
               "parts": [{"name": "assessment-objects", "prose": "The policy\n\nthe list of names"}]}],
          "controls": [c11]}
    c2 = {"id": "c-2", "class": "SP800-53", "title": "Second",
          "props": labels("C-2", "C-02") + [{"name": "sort-id", "value": "c-02"},
                                             {"name": "implementation-level", "ns": RMF, "value": "organization"}],
          "parts": [{"id": "c-2_smt", "name": "statement", "prose": "Keep it."},
                    {"id": "c-2_gdn", "name": "guidance", "prose": "Nothing to add."}]}
    def withdrawn(cid, plain, padded, links=(), parts=()):
        w = {"id": cid, "class": "SP800-53", "title": f"Withdrawn {plain}",
             "props": labels(plain, padded) + [{"name": "sort-id", "value": padded.lower()}, {"name": "status", "value": "withdrawn"}]}
        if links: w["links"] = list(links)
        if parts: w["parts"] = list(parts)
        return w
    return {"catalog": {
        "uuid": "00000000-0000-4000-8000-000000000001",
        "metadata": {"title": "An invented catalogue", "last-modified": "2026-11-14T00:00:00Z", "version": "1.0",
                     "oscal-version": "1.2.2",
                     "revisions": [{"title": "An earlier one", "version": "0.9", "remarks": "It had two controls."}],
                     "props": [{"name": "keywords", "value": "invented"}],
                     "links": [{"href": f"#{RES_B}", "rel": "alternate"}],
                     "roles": [{"id": "publisher", "title": "Publisher"}],
                     "parties": [{"uuid": "00000000-0000-4000-8000-0000000000aa", "type": "organization", "name": "Nobody"}],
                     "responsible-parties": [{"role-id": "publisher", "party-uuids": ["00000000-0000-4000-8000-0000000000aa"]}]},
        "groups": [{"id": "g", "class": "family", "title": "Group", "props": [{"name": "label", "value": "G"}],
                    "parts": [{"id": "g_ovw", "name": "overview", "title": "About the group", "prose": "The group in a sentence."}],
                    "controls": [c1, c2,
                                 withdrawn("w-1", "W-1", "W-01", [{"href": "#c-1_smt.a", "rel": "incorporated-into"}]),
                                 withdrawn("w-2", "W-2", "W-02", [{"href": "#c-2", "rel": "moved-to"}]),
                                 withdrawn("w-3", "W-3", "W-03", (),
                                           [{"id": "w-3_smt", "name": "statement", "prose": "Addressed elsewhere."}])]}],
        "back-matter": {"resources": [
            {"uuid": RES_A, "title": "The paper", "citation": {"text": "Nobody, The paper."},
             "rlinks": [{"href": "https://paper.example/1"}]},
            {"uuid": RES_B, "title": "The catalogue as a document",
             "rlinks": [{"href": "https://paper.example/catalogue.pdf", "media-type": "application/pdf"}]},
            {"uuid": RES_C, "title": "A paper nobody cites", "rlinks": [{"href": "https://paper.example/3"}]}]}}}

def invented_profile(name):
    return {"profile": {
        "uuid": "00000000-0000-4000-8000-000000000002",
        "metadata": {"title": f"An invented baseline, {name}", "last-modified": "2026-11-14T00:00:00Z", "version": "1.1",
                     "oscal-version": "1.2.2", "roles": [{"id": "publisher", "title": "Publisher"}]},
        "imports": [{"href": "#00000000-0000-4000-8000-00000000000d", "include-controls": [{"with-ids": ["c-1", "c-2"]}]}],
        "merge": {"as-is": True},
        "back-matter": {"resources": [{"uuid": "00000000-0000-4000-8000-00000000000d", "description": "the catalogue",
                                        "rlinks": [{"href": "catalogue.json", "media-type": "application/oscal.catalog+json"}]}]}}}


def norm(path):
    """nested controls and parts under one path, as the converter's path map counts them"""
    return re.sub(r"(\.parts\[\])+", ".parts[]", re.sub(r"(\.controls\[\])+", ".controls[]", path))

def objectives(node):
    """every objective of an sp800-53a@1 payload, the nested ones too"""
    for o in node if isinstance(node, list) else node.get("objectives", []):
        yield o
        yield from objectives(o.get("children", []))

def source_parts(node):
    for p in node.get("parts", []) or []:
        yield p
        yield from source_parts(p)

def source_controls(node):
    for g in node.get("groups", []) or []: yield from source_controls(g)
    for c in node.get("controls", []) or []:
        yield c
        yield from source_controls(c)

def plain_label(control):
    return next(p["value"] for p in control["props"] if p["name"] == "label" and "class" not in p)

def is_withdrawn(control):
    return any(p["name"] == "status" and p["value"] == "withdrawn" for p in control.get("props", []))

def read_bundle(bundle):
    """-> {relative path: object} of the objects of a written bundle"""
    out = {}
    for base, _, files in os.walk(os.path.join(bundle, "objects")):
        for fn in files:
            with open(os.path.join(base, fn), encoding="utf-8") as f:
                out[os.path.relpath(os.path.join(base, fn), bundle).replace(os.sep, "/")] = json.load(f)
    return out

def what_the_authors_list_names(catalogue, objects):
    """-> (counted in the source, counted in the written bundle) of each loss the author named on 2026-11-14.
    Both sides are counted from the documents, not from anything the converter says about itself."""
    controls = list(source_controls(catalogue))
    withdrawn = [c for c in controls if is_withdrawn(c)]
    reqs = {o["id"]: o for o in objects.values() if "statements" in o}
    replaced = {}                                    # URI of a withdrawn control -> the labels its annotations give
    for o in objects.values():
        for e in (o.get("annotations") or {}).get("nist-withdrawal", []): replaced.setdefault(e["ref"], set()).add(e["label"])
    uri = lambda c: f"{NS}/req/{c['id'].upper()}"
    source = {
        "assessment-for links": sum(1 for c in controls for p in source_parts(c) for l in p.get("links", []) or []
                                    if l["rel"] == "assessment-for"),
        "withdrawn controls": len(withdrawn),
        "withdrawn controls that name no successor": sorted(c["id"] for c in withdrawn if not c.get("links")),
        "labels of withdrawn controls that name a successor": sorted(plain_label(c) for c in withdrawn if c.get("links")),
        "formal ODP labels": sorted(p["value"] for c in controls for pm in c.get("params", []) or []
                                    for p in pm.get("props", []) if p["name"] == "label" and p.get("class") == "sp800-53a"),
    }
    written = {
        "assessment-for links": sum(len(o.get("assessment-for", [])) for r in reqs.values()
                                    for o in objectives((r.get("facets") or {}).get(F_53A, {}))),
        "withdrawn controls": len(replaced) + sum(1 for r in reqs.values() if r["lifecycle"] == "withdrawn"),
        "withdrawn controls that name no successor": sorted(c["id"] for c in withdrawn
                                                            if reqs.get(uri(c), {}).get("lifecycle") == "withdrawn"),
        "labels of withdrawn controls that name a successor": sorted(l for ls in replaced.values() for l in ls),
        "formal ODP labels": sorted(a["sp800-53a-label"] for r in reqs.values()
                                    for a in (r.get("facets") or {}).get(F_ODP, {}).get("params", {}).values()
                                    if "sp800-53a-label" in a),
    }
    return source, written


class Tree:
    """A folder of its own with the converter, the library and five source files."""
    def __init__(self, catalogue=None):
        self.tmp = tempfile.mkdtemp(prefix="jascon-nist-ledger-")
        self.scripts = os.path.join(self.tmp, "jascon", "scripts")
        os.makedirs(self.scripts)
        for fn in ("convert_nist.py", "oscal_conv_lib.py"): shutil.copy(os.path.join(HERE, fn), self.scripts)
        os.makedirs(os.path.join(self.tmp, "sources", "nist"))
        self.write("NIST_SP-800-53_rev5_catalog.json", catalogue or invented_catalogue())
        for b in PROFILES: self.write(f"NIST_SP-800-53_rev5_{b}-baseline_profile.json", invented_profile(b))

    def write(self, name, doc):
        with open(os.path.join(self.tmp, "sources", "nist", name), "w", encoding="utf-8") as f: json.dump(doc, f)

    def run(self, script, name):
        """-> (the finished process, its --out, the ledger record it wrote or None)"""
        out = os.path.join(self.tmp, "out", name)
        done = subprocess.run([sys.executable, os.path.join(self.scripts, script), "--out", out], capture_output=True, text=True)
        try:
            with open(os.path.join(out, LEDGER), encoding="utf-8") as f: record = json.load(f)
        except (OSError, ValueError): record = None
        return done, out, record

    def changed(self, name, *changes):
        """-> run() of a copy of the converter in which each `old` reads `new`"""
        with open(os.path.join(self.scripts, "convert_nist.py"), encoding="utf-8") as f: code = f.read()
        for old, new in zip(changes[0::2], changes[1::2]):
            assert code.count(old) == 1, f"{name}: the line the defect is put into is there {code.count(old)} times: {old!r}"
            code = code.replace(old, new)
        with open(os.path.join(self.scripts, f"convert_nist_{name}.py"), "w", encoding="utf-8") as f: f.write(code)
        return self.run(f"convert_nist_{name}.py", name)

    def remove(self):
        shutil.rmtree(self.tmp, ignore_errors=True)


def by_path(record, tag="nist.catalog."):
    """-> {(path below the tag, outcome): count}"""
    rows = collections.Counter()
    for r in record["paths"]:
        if r["path"].startswith(tag): rows[(norm(r["path"])[len(tag):], r["outcome"])] += r["count"]
    return rows


class Backlog41TheLedgerOfSP80053(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tree = Tree()
        cls.done, cls.out, cls.record = cls.tree.run("convert_nist.py", "as-it-is")
        cls.rows = by_path(cls.record)
        cls.objects = read_bundle(os.path.join(cls.out, "sp800-53-core-bundle"))
        with open(os.path.join(cls.out, "sp800-53-coverage-report.json"), encoding="utf-8") as f: cls.report = json.load(f)

    @classmethod
    def tearDownClass(cls):
        cls.tree.remove()

    def outcomes(self, path):
        """-> {outcome: count} of the source values under one path of the catalogue"""
        return {o: n for (p, o), n in self.rows.items() if p == path}

    def rules(self):
        """-> {rule: destinations} over the whole record"""
        seen = collections.Counter()
        for r in self.record["paths"]:
            for d in r.get("to", []):
                if "rule" in d: seen[d["rule"]] += d["count"]
        return seen

    def req(self, cid):
        return self.objects[f"objects/req/{cid.replace('.', '-')}.json"]

    # ---------- the state the author asked for ----------
    def test_backlog_41_every_source_value_has_one_of_five_outcomes_none_is_unaccounted_and_the_run_ends_with_0(self):
        self.assertEqual(self.done.returncode, 0, self.done.stderr[-600:])
        t = self.record["totals"]
        self.assertEqual(tuple(t), OUTCOMES)
        self.assertEqual(sum(t.values()), self.record["leaf-values"])
        self.assertEqual(sum(r["count"] for r in self.record["paths"]), self.record["leaf-values"])
        self.assertEqual(t["unaccounted"], 0)
        self.assertEqual(self.record["unaccounted-paths"], [])
        self.assertEqual(self.record["verification-failures"], [])
        self.assertIn("unaccounted 0; failed checks 0", self.done.stdout)
        self.assertEqual(self.report["ledger"]["totals"], t, "the report and the record are of one run")
        self.assertEqual(self.report["totals"]["unmapped"], 0)
        with open(os.path.join(self.out, "sp800-53-coverage-report.md"), encoding="utf-8") as f: text = f.read()
        for heading in ("## Conversion ledger: the five outcomes", "## Conversion ledger: what is no content, and by which rule",
                        "## Conversion ledger: the drops that stay declared"):
            self.assertIn(heading, text)
        for k in OUTCOMES: self.assertIn(f"| {k} | {t[k]:,} |", text)

    def test_backlog_41_the_gate_is_the_last_statement_of_the_converter(self):
        with open(os.path.join(HERE, "convert_nist.py"), encoding="utf-8") as f: last = ast.parse(f.read()).body[-1]
        self.assertEqual(ast.unparse(last), "ledger_gate(LEDGER, 'convert_nist.py')")

    def test_backlog_41_what_the_authors_list_names_is_in_the_written_bundle(self):
        source, written = what_the_authors_list_names(invented_catalogue()["catalog"], self.objects)
        self.assertEqual(source, written)
        self.assertEqual(source["assessment-for links"], 3)
        self.assertEqual(source["withdrawn controls"], 3)
        self.assertEqual(source["withdrawn controls that name no successor"], ["w-3"])
        # the label of a withdrawn control is the one the source gives for a reader, not the zero-padded one
        self.assertEqual(source["labels of withdrawn controls that name a successor"], ["W-1", "W-2"])
        self.assertEqual(source["formal ODP labels"], ["C-01(01)_ODP", "C-01_ODP"])
        # the links as the source states them: a statement, the statement part as a whole, a statement of another control
        seen = {o["id"]: o.get("assessment-for") for o in objectives(self.req("c-1")["facets"][F_53A])}
        self.assertEqual(seen, {"c-1_obj": [{"statement-id": "smt"}], "c-1_obj.a": [{"statement-id": "smt.a"}],
                                "c-1_obj.b": [{"requirement-ref": f"{NS}/req/C-2", "statement-id": "smt"}]})
        self.assertEqual(self.report["assessment-for"]["links"], 3)
        self.assertEqual(sorted(self.report["assessment-for"]["names"].values()), [1, 1, 1])

    def test_backlog_41_a_withdrawn_control_without_a_successor_is_an_object_with_the_sources_own_status(self):
        w3 = self.req("w-3")
        self.assertEqual({k: w3[k] for k in ("id", "label", "lifecycle", "title")},
                         {"id": f"{NS}/req/W-3", "label": "W-3", "lifecycle": "withdrawn", "title": {"en": "Withdrawn W-3"}})
        self.assertEqual(w3["statements"], [{"id": "smt", "modality": "unspecified",        # it states no obligation
                                             "obligated-parties": [f"{NS}/party/organization"],
                                             "prose": {"en": "Addressed elsewhere."}}])
        self.assertIn({"ref": f"{NS}/req/W-3", "sequence": 40}, self.objects["objects/set/family-g.json"]["members"])
        self.assertEqual(self.outcomes("groups[].controls[].props[].value").get("intentionally-dropped"), 2,
                         "the status of w-1 and w-2, which name a successor, stays the drop it was declared as; w-3's is its lifecycle")
        self.assertEqual({o["lifecycle"] for o in self.objects.values()}, {"active", "withdrawn"})
        self.assertEqual(self.report["withdrawn"]["objects"], ["w-3"])
        self.assertEqual(self.report["objects-emitted"], {"requirements": 4, "sets": 6, "requirements-in-force": 3,
                                                          "requirements-withdrawn": 1})
        # a control in force is still read as `must`
        self.assertEqual({s["modality"] for cid in ("c-1", "c-1.1", "c-2") for s in self.req(cid)["statements"]}, {"must"})
        # a relation to a withdrawn control that is no object is written as the source states it
        self.assertIn({"type": "related", "ref": f"{NS}/req/W-2"}, self.req("c-1")["relations"])

    def test_backlog_41_the_document_metadata_stands_on_the_set_of_the_document_in_the_sources_shape(self):
        cat, root = invented_catalogue()["catalog"], self.objects["objects/set/root.json"]
        want = {k: v for k, v in cat["metadata"].items() if k not in ("title", "version")}
        self.assertEqual(root["facets"][F_COMPAT], {"metadata": want})
        self.assertEqual((root["title"], root["version"]), ({"en": cat["metadata"]["title"]}, cat["metadata"]["version"]))
        for b in PROFILES:
            prof, bset = invented_profile(b)["profile"], self.objects[f"objects/set/baseline-{b.lower()}.json"]
            want = {k: v for k, v in prof["metadata"].items() if k not in ("title", "version")}
            self.assertEqual(bset["facets"][F_COMPAT], {"metadata": want, "merge": {"as-is": True}})
            self.assertIs(bset["facets"][F_COMPAT]["merge"]["as-is"], True, "a JSON boolean, not the number 1")
            self.assertEqual((bset["title"], bset["version"]), ({"en": prof["metadata"]["title"]}, "1.1"))
        # every value of a document's metadata is a copy; none is dropped, none is unaccounted
        meta = collections.Counter()
        for r in self.record["paths"]:
            if ".metadata." in r["path"]: meta[r["outcome"]] += r["count"]
        self.assertEqual(meta, {"copied": 18 + 4 * 6})
        self.assertEqual(collections.Counter(r["outcome"] for r in self.record["paths"] if r["path"].endswith(".merge.as-is")),
                         {"copied": 4})
        # the back-matter resources stand on the root Set as the source writes them, each with its uuid: the guidance
        # of c-1 names the first, the document metadata the second, nothing the third
        self.assertEqual(root["facets"][F_REF], {"resources": cat["back-matter"]["resources"]})
        self.assertEqual([r["uuid"] for r in root["facets"][F_REF]["resources"]], [RES_A, RES_B, RES_C])
        # the manifest names the author and the day of the catalogue, by the library's rule (the one party it defines)
        with open(os.path.join(self.out, "sp800-53-core-bundle", "content-manifest.json"), encoding="utf-8") as f:
            provenance = json.load(f)["provenance"]
        self.assertEqual((provenance["author-ref"], provenance["date"]), (f"{NS}/party/nobody", "2026-11-14"))
        self.assertEqual(self.req("c-1")["facets"][F_NARR]["guidance"], [{"en": f"See [The paper](#{RES_A}) and [C-2](#c-2)."}])
        self.assertEqual(self.objects["objects/set/family-g.json"]["facets"][F_NARR],
                         {"overview": [{"title": {"en": "About the group"}, "prose": {"en": "The group in a sentence."}}]})

    def test_backlog_41_what_is_copied_and_what_a_named_rule_made(self):
        o = self.outcomes
        self.assertEqual(o("groups[].controls[].title"), {"copied": 6})                # 4 objects, 2 on a successor
        self.assertEqual(o("groups[].controls[].id"), {"transformed": 6})
        self.assertEqual(o("groups[].controls[].params[].id"), {"copied": 2})
        self.assertEqual(o("groups[].controls[].params[].props[].value"), {"copied": 5})
        self.assertEqual(o("groups[].controls[].params[].select.choice[]"), {"copied": 2})
        self.assertEqual(o("groups[].controls[].params[].select.how-many"), {"transformed": 1})
        self.assertEqual(o("back-matter.resources[].title"), {"copied": 3})
        # every value of a resource is a copy, its uuid and the media type of its link too
        self.assertEqual(o("back-matter.resources[].uuid"), {"copied": 3})
        self.assertEqual(o("back-matter.resources[].rlinks[].media-type"), {"copied": 1})
        self.assertEqual(o("back-matter.resources[].citation.text"), {"copied": 1})
        # prose: an insertion (item a, the statement of the enhancement) or two paragraphs (the assessment objects)
        # make it a transformation; a markdown link does not, it stays as the source wrote it
        self.assertEqual(o("groups[].controls[].parts[].prose"), {"copied": 12, "transformed": 3})
        self.assertEqual(o("groups[].controls[].links[].rel"), {"copied": 4, "transformed": 2})
        self.assertEqual(o("groups[].controls[].links[].href"), {"transformed": 6})
        self.assertEqual(o("groups[].controls[].parts[].links[].href"), {"transformed": 3})
        self.assertEqual(o("groups[].parts[].title"), {"copied": 1})
        rules = self.rules()
        for rule, destinations in (
                ("requirement URI from the control id", 4 * 3 + 4 * 2),      # id, manifest, family Set; two members in each of four baselines
                ("requirement URI from the control a link names", 3),        # required, related, related to a withdrawn control
                ("a reference link resolved by uuid: the first link of the back-matter resource it names", 3),   # three inputs, one relation
                ("statement id without the control prefix", 10 * 2),         # ten statements; the part id and the control id
                ("obligated party URI from the implementation level", 2 * 4 + 4 + 1),   # c-1: two levels on four statements
                ("parameter cardinality `many` from the selection's how-many `one-or-more`", 1),
                ("lineage inverted: the URI of a withdrawn control, written on the successor its link names", 2 * 2 * 3),
                ("lineage mode from the link's rel (incorporated-into -> merged-into, moved-to -> renamed)", 2 * 2),
                ("the statement a lineage link names, as a statement id", 1),
                ("family Set URI from the group id", 3),
                ("member sequence: ten times the control's place in its family, ordered by sort-id", 4),
                ("the prop value `true` or `false`, written as a JSON boolean", 1),
                ("the statement part an `assessment-for` link names, as a statement id (the part id without the control prefix)", 3),
                ("requirement URI from the control whose part an `assessment-for` link names, where that is another control", 1),
                ("date of the catalogue: the day of its last-modified", 1)):
            self.assertEqual(rules[rule], destinations, rule)
        self.assertEqual(sum(n for r, n in rules.items() if r.startswith("assessment objects: one entry per paragraph")), 2)
        self.assertEqual(sum(n for r, n in rules.items() if r.startswith("author of the catalogue")), 1)
        self.assertEqual(sum(n for r, n in rules.items() if "parameter insertion" in r), 2)
        self.assertIs(self.req("c-1")["facets"][F_RMF]["contributes-to-assurance"], True)

    def test_backlog_41_what_is_not_in_the_bundle_is_no_content_by_a_rule_of_one_of_three_kinds(self):
        o = self.outcomes
        # a name that selects: of a prop, of a part, of a link, the class of a prop and of a group
        self.assertEqual(o("groups[].controls[].parts[].name"), {"not-content": 18})
        self.assertEqual(o("groups[].controls[].parts[].links[].rel"), {"not-content": 3})
        self.assertEqual(o("groups[].class"), {"not-content": 1})
        self.assertEqual(o("groups[].props[].name"), {"not-content": 1})
        self.assertEqual(o("groups[].parts[].name"), {"not-content": 1})
        self.assertEqual(o("groups[].controls[].params[].props[].name"), {"not-content": 5})
        self.assertEqual(o("groups[].controls[].params[].props[].class"), {"not-content": 3})
        # ... a namespace
        self.assertEqual(o("groups[].controls[].props[].ns"), {"not-content": 5})
        self.assertEqual(o("groups[].controls[].params[].props[].ns"), {"not-content": 1})
        self.assertEqual(o("groups[].controls[].parts[].props[].ns"), {"not-content": 1})
        # ... an id or a label that a rule rebuilds: class, zero-padded and SP 800-53A label of every control, the
        # sort-id of the two that are no objects; guidance x2, method, the statement part of c-1; the item labels
        self.assertEqual(o("groups[].controls[].class"), {"not-content": 6})
        self.assertEqual(o("groups[].controls[].props[].value"),
                         {"copied": 6 + 1, "transformed": 4 + 4 + 1, "not-content": 12 + 2, "intentionally-dropped": 2})
        self.assertEqual(o("groups[].controls[].parts[].id"), {"copied": 3, "transformed": 10, "not-content": 4})
        # the print label of an item on each level of a control (`a.`, `1.`, `(a)`, `b.`) and of an enhancement
        # (`(a)`, `(1)`) is rebuilt; `b.` on an item of the enhancement is a form the rule does not give, and
        # stays the drop it was declared as, with the name that selects it
        self.assertEqual(o("groups[].controls[].parts[].props[].value"), {"copied": 5, "not-content": 6, "intentionally-dropped": 1})
        self.assertEqual(o("groups[].controls[].parts[].props[].name"), {"not-content": 11, "intentionally-dropped": 1})
        self.assertEqual(self.report["item-labels"], {"rebuilt": 6, "declared-drop": ["c-1.1_smt.b"]})
        self.assertEqual(o("groups[].parts[].id"), {"not-content": 1})
        # the name of the status of w-1 and w-2 goes with its value, which is a declared drop
        self.assertEqual(o("groups[].controls[].props[].name"), {"not-content": 6 * 4 + 4 + 1 + 1, "intentionally-dropped": 2})
        kinds = collections.Counter()
        for r in self.record["paths"]:
            if r["outcome"] == "not-content":
                self.assertEqual(sum(x["count"] for x in r["rules"]), r["count"], r["path"])
                for x in r["rules"]: kinds[x["kind"]] += x["count"]
        self.assertEqual(set(kinds), {"selector", "namespace", "rebuilt-id"})
        self.assertEqual(sum(kinds.values()), self.record["totals"]["not-content"])
        listed = self.report["ledger"]["not-content"]
        self.assertEqual(sum(x["count"] for x in listed), self.record["totals"]["not-content"], "the report lists every rule with its count")
        self.assertEqual({x["kind"] for x in listed}, set(kinds))

    def test_backlog_41_the_drops_that_stay_are_the_ones_declared_before_and_each_has_a_reading(self):
        rows = self.report["ledger"]["declared-drops"]
        self.assertEqual(sum(r["count"] for r in rows), self.record["totals"]["intentionally-dropped"])
        for r in rows:
            self.assertTrue(r["reason"].split(WITH)[-1].startswith(DECLARED_BEFORE), r["reason"])
            self.assertTrue(r["reading"].startswith(("content: ", "not content, because ")), r)
            self.assertIn("example-value", r)
        got = {(r["path"], r["reason"].split(WITH)[-1][:40], WITH in r["reason"]): r["count"] for r in rows}
        self.assertEqual(got, {
            ("nist.catalog.groups[].controls[].props[].value", "path map: a withdrawn control is dropped", False): 2,
            ("nist.catalog.groups[].controls[].props[].name", "path map: a withdrawn control is dropped", True): 2,
            ("nist.catalog.uuid", "as decided for IFA on 2026-11-13: the uu", False): 1,
            ("nist.catalog.groups[].controls[].parts[].props[].value", "path map: the print label of a statement", False): 1,
            ("nist.catalog.groups[].controls[].parts[].props[].name", "path map: the print label of a statement", True): 1,
            ("*.profile.uuid", "as decided for IFA on 2026-11-13: the uu", False): 4,
            ("*.profile.imports[].href", "path map: profile resolution mechanics; ", False): 4,
            ("*.profile.back-matter.resources[].uuid", "as decided for IFA on 2026-11-13: a back", False): 4,
            ("*.profile.back-matter.resources[].description", "as decided for IFA on 2026-11-13: a back", False): 4,
            ("*.profile.back-matter.resources[].rlinks[].href", "as decided for IFA on 2026-11-13: a back", False): 4,
            ("*.profile.back-matter.resources[].rlinks[].media-type", "as decided for IFA on 2026-11-13: a back", False): 4})
        # the converter declares no drop of its own: every call is one of the five reasons, by name
        with open(os.path.join(HERE, "convert_nist.py"), encoding="utf-8") as f: code = f.read()
        reasons = re.findall(r"led\.drop(?:_value)?\(.*?, ([A-Za-z_]+)\)", code)
        self.assertEqual(sorted(reasons), ["A_ITEM_LABEL", "A_TOMBSTONE", "reason"])

    def test_backlog_41_the_path_map_says_what_the_ledger_measured(self):
        self.assertEqual(self.report["unmapped-paths"], [])
        for row in self.report["path-map"]:
            self.assertRegex(row["destination"], r" \[ledger: [a-z-]+ [0-9,]+(, [a-z-]+ [0-9,]+)*\]$", row["path"])
            self.assertNotIn("unaccounted", row["destination"], row["path"])

    # ---------- deliberate defects: each ends the run with 1 ----------
    def fails(self, name, done, word=None):
        self.assertEqual(done.returncode, 1, f"{name}: exit {done.returncode}\n{done.stdout[-300:]}\n{done.stderr[-400:]}")
        if word: self.assertIn(word, done.stderr, name)

    GATE = "convert_nist.py: the conversion ledger has {} claim(s) that do not hold and {} source value(s) unaccounted"

    def test_backlog_41_a_value_that_is_lost_ends_the_run_with_1(self):
        for name, old, new, path, lost in (
                # the annotation loses the title of the withdrawn control
                ("title-lost", '"label": label, "title": c.get("title", "")}\n', '"label": label, "title": ""}\n',
                 "groups[].controls[].title", 2),
                # the annotation takes the zero-padded label again: the label the source gives for a reader is in no object
                ("padded-label", '    label = prop(c, "label")                    #', '    label = prop(c, "label", cls="zero-padded")   #',
                 "groups[].controls[].props[].value", 2),
                # the `assessment-for` links are built and not written
                ("links-lost", '    if links: node["assessment-for"] = links\n', "    pass\n",
                 "groups[].controls[].parts[].links[].href", 3),
                # a withdrawn control without a successor is left out again
                ("withdrawn-left-out", "written = [(c, par, g) for c, par, g in controls if c[\"id\"] not in tombstones]",
                 "written = [(c, par, g) for c, par, g in controls if c[\"id\"] not in withdrawn]",
                 "groups[].controls[].title", 1),
                # the metadata of the profiles is not written
                ("profile-metadata", '    if document_metadata(prof["metadata"]): compat["metadata"] = document_metadata(prof["metadata"])\n', "",
                 None, 4 * 4),
                # the back-matter resources are not written: their titles are in no object. The uuid and the link of
                # the resource a `reference` link names are still inputs of a rule, so the path map's sentence
                # (`copied`) no longer holds either, and that wiring check stops the run before the gate
                ("resources-lost", 'if RESOURCES: root_facets[F_REF] = {"resources": RESOURCES}\n', "",
                 "back-matter.resources[].title", 3)):
            done, _, record = self.tree.changed(name, old, new)
            self.fails(name, done)
            self.assertEqual(record["totals"]["unaccounted"] >= lost, True, name)
            if name == "resources-lost":
                self.assertEqual(record["totals"]["unaccounted"], 9, name)      # 3 titles, 1 citation, 2 links, 1 media type, 2 uuids
                self.assertIn("the path map does not say `transformed` of nist.catalog.back-matter.resources[].uuid", done.stderr)
            else:
                self.assertIn(self.GATE.format(0, record["totals"]["unaccounted"]), done.stderr, name)
            if path: self.assertEqual(by_path(record)[(path, "unaccounted")], lost, name)

    def test_backlog_41_a_name_that_selects_a_value_which_is_not_written_is_unaccounted_with_it(self):
        # the formal ODP label is read and not written: its name and its class select nothing
        done, _, record = self.tree.changed("formal-label", '        if formal: a["sp800-53a-label"] = formal; n_formal += 1\n',
                                            "        if formal: n_formal += 1\n")
        self.fails("formal-label", done, self.GATE.format(0, 6))
        rows = by_path(record)
        for leaf in ("value", "name", "class"):
            self.assertEqual(rows[(f"groups[].controls[].params[].props[].{leaf}", "unaccounted")], 2, leaf)
        # the boolean is read and not written: the name and the namespace of the prop go with it
        done, _, record = self.tree.changed("assurance", "        if v in BOOLEAN: facets[F_RMF] =", "        if v in BOOLEAN and False: facets[F_RMF] =")
        self.fails("assurance", done, self.GATE.format(0, 3))
        rows = by_path(record)
        for leaf in ("value", "name", "ns"):
            self.assertEqual(rows[(f"groups[].controls[].props[].{leaf}", "unaccounted")], 1, leaf)

    def test_backlog_41_a_rule_that_does_not_give_the_id_it_claims_ends_the_run_with_1(self):
        # in the converter: the rule for the id of a guidance part gives another id than the source has
        done, _, record = self.tree.changed("guidance-id", 'def _gdn_id(cid): return cid + "_gdn"', 'def _gdn_id(cid): return cid + "_gd"')
        self.fails("guidance-id", done, self.GATE.format(2, 4))        # the two ids, and the two part names beside them
        self.assertEqual([(x["claim"], x["source"]) for x in record["verification-failures"]],
                         [("rebuilt-id", "nist#/catalog/groups/0/controls/0/parts/1/id"),
                          ("rebuilt-id", "nist#/catalog/groups/0/controls/1/parts/1/id")])
        # in the source: an id, a label and a sort-id that the rules do not give
        for name, change, claims in (
                ("method-id", lambda c: c["groups"][0]["controls"][0]["parts"][3].update(id="c-1_examine"), 1),
                ("padded-label", lambda c: c["groups"][0]["controls"][1]["props"][0].update(value="C-002"), 1),
                ("sort-id", lambda c: c["groups"][0]["controls"][3]["props"][3].update(value="w-2"), 1),
                ("statement-id", lambda c: c["groups"][0]["controls"][0]["parts"][0].update(id="c-1_statement"), 1)):
            cat = invented_catalogue(); change(cat["catalog"])
            tree = Tree(cat)
            try:
                done, _, record = tree.run("convert_nist.py", name)
                self.fails(name, done)
                self.assertEqual([x.get("claim") for x in record["verification-failures"]], ["rebuilt-id"] * claims, name)
                self.assertGreaterEqual(record["totals"]["unaccounted"], claims, name)
            finally: tree.remove()

    def test_backlog_41_a_name_or_a_namespace_the_mapping_is_not_written_for_is_not_passed_over(self):
        def another_namespace(c): c["groups"][0]["controls"][1]["props"][4]["ns"] = "https://elsewhere.example/ns"
        def unknown_prop(c): c["groups"][0]["controls"][1]["props"].append({"name": "priority", "value": "P1"})
        def unknown_part(c): c["groups"][0]["controls"][1]["parts"].append({"id": "c-2_note", "name": "note", "prose": "A note."})
        def unknown_item(c): c["groups"][0]["controls"][0]["parts"][0]["parts"].append({"id": "c-1_smt.c", "name": "remark", "prose": "A remark."})
        def unknown_class(c): c["groups"][0]["controls"][1]["props"][0]["class"] = "padded"
        def unknown_link(c): c["groups"][0]["controls"][0]["parts"][2]["links"][0]["rel"] = "assessed-with"
        def unknown_status(c): c["groups"][0]["controls"][1]["props"].append({"name": "status", "value": "placeholder"})
        for name, change, unaccounted, claims in (
                ("another-namespace", another_namespace, 3, 0),      # the level of c-2: name, ns, value; c-2 gets the default party
                ("unknown-prop", unknown_prop, 2, 0),
                ("unknown-part", unknown_part, 3, 0),
                ("unknown-item", unknown_item, 1, 1),                # placed as a statement by its text; its name is none the mapping places
                ("unknown-class", unknown_class, 3, 0),
                ("unknown-link", unknown_link, 3, 0)):               # href, rel, and the name of the objective beside them
            cat = invented_catalogue(); change(cat["catalog"])
            tree = Tree(cat)
            try:
                done, out, record = tree.run("convert_nist.py", name)
                self.fails(name, done, self.GATE.format(claims, unaccounted))
                if name == "another-namespace":
                    c2 = read_bundle(os.path.join(out, "sp800-53-core-bundle"))["objects/req/c-2.json"]
                    self.assertEqual(c2["statements"][0]["obligated-parties"], [f"{NS}/party/organization"])
                    self.assertEqual(by_path(record)[("groups[].controls[].props[].ns", "unaccounted")], 1)
            finally: tree.remove()
        # a status the kernel's lifecycle does not know is not written as something else: the run stops before it writes
        cat = invented_catalogue(); unknown_status(cat["catalog"])
        tree = Tree(cat)
        try:
            done, out, record = tree.run("convert_nist.py", "unknown-status")
            self.fails("unknown-status", done, "this mapping knows `withdrawn` only")
            self.assertFalse(os.path.exists(out))
        finally: tree.remove()

    def test_backlog_41_a_boolean_is_followed_by_type(self):
        # read without `typed`, the boolean of a profile is written and no longer traced
        done, _, record = self.tree.changed("untyped", "led.source(tag, {key: doc[key]}, typed=True)", "led.source(tag, {key: doc[key]})")
        self.fails("untyped", done, self.GATE.format(0, 4))
        self.assertEqual(sum(r["count"] for r in record["paths"] if r["path"].endswith(".merge.as-is") and r["outcome"] == "unaccounted"), 4)
        # without resolve() a boolean that carries its origin cannot be written: the run stops, no bundle is half right
        done, out, record = self.tree.changed("unresolved", "led.resolve(bundle.objects)", "pass")
        self.fails("unresolved", done, "is not JSON serializable")
        self.assertIsNone(record)

    def test_backlog_41_a_written_file_that_says_something_else_ends_the_run_with_1(self):
        # one written file is changed between the writing and the accounting
        marker = "T_WRITTEN = time.time()\n"
        done, _, record = self.tree.changed("tampered", marker, marker +
                                            '_p = os.path.join(bundle.out, "objects", "req", "c-2.json")\n'
                                            '_o = json.load(open(_p, encoding="utf-8")); _o["title"]["en"] = "Seconds"\n'
                                            'json.dump(_o, open(_p, "w", encoding="utf-8"))\n')
        self.fails("tampered", done, self.GATE.format(1, 1))
        self.assertIn("LEDGER CHECK FAILED", done.stderr)
        self.assertEqual([x["source"] for x in record["verification-failures"]], ["nist#/catalog/groups/0/controls/1/title"])

    TITLE_LOST = ('"label": label, "title": c.get("title", "")}\n', '"label": label, "title": ""}\n')

    def test_backlog_41_what_the_ledger_cannot_see_by_itself_ends_the_run_with_1(self):
        """A declaration that reaches too far, a path map that says something
        else, a record that is not this run's: the ledger's own checks pass
        on each of these, the converter's wiring checks do not."""
        for name, changes, word in (
                # the status of a tombstone declared for the whole control: the lost titles would read as dropped on purpose
                ("whole-tombstone", self.TITLE_LOST + ('        led.drop_value(prop(c, "status"), A_TOMBSTONE)\n',
                                                       '        led.drop_value({k: v for k, v in c.items() if k != "controls"}, A_TOMBSTONE)\n'),
                 "a drop reaches further than it names: nist.catalog.groups[].controls[].title"),
                # a drop by path on a path where other values are carried
                ("beside-carried", self.TITLE_LOST + (' (r"^(nist\\.catalog|[a-z]+\\.profile)\\.uuid$", B_UUID),\n',
                                                      ' (r"^(nist\\.catalog|[a-z]+\\.profile)\\.uuid$|\\.controls\\[\\]\\.title$", B_UUID),\n'),
                 "on which other values are carried"),
                # a drop this converter did not declare before: the lost titles get a reason of their own
                ("a-new-drop", self.TITLE_LOST + (' (r"\\.profile\\.imports\\[\\]\\.href$", A_PROFILE),\n',
                                                  ' (r"\\.profile\\.imports\\[\\]\\.href$", A_PROFILE),\n (r"\\.controls\\[\\]\\.title$", "not needed"),\n'),
                 "a drop is declared with a reason this converter does not state: 'not needed'"),
                # a drop that stays declared and has no reading for the author
                ("no-reading", (' (r"\\.uuid$", B_UUID, "content: the identifier', ' (r"\\.uuid-of-nothing$", B_UUID, "content: the identifier'),
                 "a declared drop has no reading for the author: *.profile.uuid"),
                # the path map says `transformed` of a title, which is copied
                ("path-map", ('`title` in the nist-withdrawal annotation", {C}),', '`title` in the nist-withdrawal annotation", {X}),'),
                 "the path map does not say `copied` of nist.catalog.groups[].controls[].title (x6)"),
                # a source path without a row in the path map
                ("no-row", (' (r"^nist\\.catalog\\.groups\\[\\]\\.title$", "L1", "family Set title", {C}),\n', ""),
                 "1 source path(s) have no row in the path map"),
                # a rule that rewrites a text cuts a markdown link to its text again. The ledger applies the same rule
                # to the source and agrees with it: what the rule left out is in no leaf
                ("links-cut", ('def _rewrite(prose):\n    return INSERT.sub(',
                               'def _rewrite(prose):\n    prose = re.sub(r"\\[([^\\]]+)\\]\\(#[^)]+\\)", r"\\1", prose or "")\n    return INSERT.sub('),
                 "a rule that rewrites a text changed more than the insertion syntax in 1 text(s)"),
                # ... or drops a paragraph of the assessment objects
                ("paragraph-lost", ("def _paragraphs(prose): return [x.strip() for x in re.split(r\"\\n\\s*\\n\", prose) if x.strip()]",
                                    "def _paragraphs(prose): return [x.strip() for x in re.split(r\"\\n\\s*\\n\", prose) if x.strip()][:1]"),
                 "a rule that rewrites a text changed more than the insertion syntax in 1 text(s)"),
                ("not-written", ("    json.dump(RECORD, f, indent=1, ensure_ascii=False); f.write(\"\\n\")\n", "    pass\n"),
                 f"{LEDGER} on disk is not the record of this run")):
            done, _, _ = self.tree.changed(name, *changes)
            self.fails(name, done, word)
            self.assertIn("LEDGER WIRING", done.stderr, name)
            self.assertIn("wiring check(s) of the conversion ledger failed", done.stderr, name)


class Backlog41TheCommittedConversion(unittest.TestCase):
    """The conversion in converted_examples/US.SP800-53, as it is committed.
    The Validators workflow holds its bytes against the pinned source; here
    its files are counted for what the author's list of 2026-11-14 names."""
    CORPUS = os.path.join(ROOT, "converted_examples", "US.SP800-53")
    SOURCE = os.path.join(ROOT, "sources", "nist", "NIST_SP-800-53_rev5_catalog.json")

    def setUp(self):
        if not os.path.isdir(os.path.join(self.CORPUS, "sp800-53-core-bundle")):
            self.skipTest("no converted_examples/US.SP800-53 beside jascon/ (the skill unpacked on its own)")

    def test_backlog_41_the_committed_record_has_nothing_unaccounted_and_no_claim_that_fails(self):
        with open(os.path.join(self.CORPUS, LEDGER), encoding="utf-8") as f: record = json.load(f)
        self.assertEqual(tuple(record["totals"]), OUTCOMES)
        self.assertEqual((record["totals"]["unaccounted"], record["verification-failures"]), (0, []))
        self.assertEqual(sum(record["totals"].values()), record["leaf-values"])
        with open(os.path.join(self.CORPUS, "sp800-53-coverage-report.json"), encoding="utf-8") as f: report = json.load(f)
        self.assertEqual(report["ledger"]["totals"], record["totals"])
        self.assertEqual(report["ledger"]["path-map-not-confirmed"], [], "a sentence of the path map names an outcome this source does not show")
        self.assertEqual(sum(r["count"] for r in report["ledger"]["declared-drops"]), record["totals"]["intentionally-dropped"])
        for r in report["ledger"]["declared-drops"]:
            self.assertTrue(r["reason"].split(WITH)[-1].startswith(DECLARED_BEFORE), r["reason"])
            self.assertTrue(r["reading"].startswith(("content: ", "not content, because ")), r)
        # a rule that stops giving a value must not move it among the declared drops unseen: 5.2.0 has three item
        # labels the rule does not give, and no control whose class it does not give
        self.assertEqual(report["item-labels"], {"rebuilt": 1119, "declared-drop": ["si-2.7_smt.a", "si-2.7_smt.b", "si-2.7_smt.c"]})
        self.assertEqual(report["class-written"], 0)
        self.assertEqual(record["totals"]["intentionally-dropped"], 407)

    def test_backlog_41_the_committed_bundle_holds_what_the_authors_list_names(self):
        """Counted from the committed files alone (measured on SP 800-53
        5.2.0 at the pinned commit, 2026-11-14)."""
        objects = read_bundle(os.path.join(self.CORPUS, "sp800-53-core-bundle"))
        reqs = {o["id"]: o for o in objects.values() if "statements" in o}
        self.assertEqual(sum(len(o.get("assessment-for", [])) for r in reqs.values()
                             for o in objectives((r.get("facets") or {}).get(F_53A, {}))), 3707)
        gone = {cid: reqs[f"{NS}/req/{cid}"] for cid in ("CP-10.3", "SC-19")}
        self.assertEqual({cid: (r["lifecycle"], r["label"], [s["modality"] for s in r["statements"]]) for cid, r in gone.items()},
                         {"CP-10.3": ("withdrawn", "CP-10(3)", ["unspecified"]), "SC-19": ("withdrawn", "SC-19", ["unspecified"])})
        self.assertEqual(sorted(r["id"] for r in reqs.values() if r["lifecycle"] != "active"), sorted(r["id"] for r in gone.values()))
        replaced = {e["ref"]: e["label"] for o in objects.values() for e in (o.get("annotations") or {}).get("nist-withdrawal", [])}
        self.assertEqual(len(replaced) + len(gone), 182, "the withdrawn controls of the source: named in a lineage, or objects")
        # the label the source gives for a reader: no number of it is padded
        self.assertEqual([l for l in replaced.values() if re.search(r"(?<![0-9])0[0-9]", l)], [])
        self.assertEqual(sorted(replaced.items())[0], (f"{NS}/req/AC-13", "AC-13"))
        self.assertEqual(replaced[f"{NS}/req/AC-2.10"], "AC-2(10)")
        self.assertEqual(sum(1 for r in reqs.values() for a in (r.get("facets") or {}).get(F_ODP, {}).get("params", {}).values()
                             if "sp800-53a-label" in a), 1458)
        root = objects["objects/set/root.json"]
        self.assertEqual(sorted(root["facets"][F_COMPAT]["metadata"]),
                         ["last-modified", "links", "oscal-version", "parties", "props", "responsible-parties", "revisions", "roles"])
        for b in PROFILES:
            compat = objects[f"objects/set/baseline-{b.lower()}.json"]["facets"][F_COMPAT]
            self.assertEqual(sorted(compat["metadata"]), ["last-modified", "oscal-version", "parties", "responsible-parties", "roles"])
            self.assertIs(compat["merge"]["as-is"], True)
        # the back-matter on the root Set, every resource with its uuid; the catalogue's author and day in the manifest
        self.assertEqual(len(root["facets"][F_REF]["resources"]), 201)
        self.assertTrue(all("uuid" in r for r in root["facets"][F_REF]["resources"]))
        with open(os.path.join(self.CORPUS, "sp800-53-core-bundle", "content-manifest.json"), encoding="utf-8") as f:
            provenance = json.load(f)["provenance"]
        self.assertEqual((provenance["author-ref"], provenance["date"]), (f"{NS}/party/oscal-program", "2026-05-11"))

    def test_backlog_41_the_committed_bundle_against_the_pinned_source(self):
        if not os.path.isfile(self.SOURCE): self.skipTest("the pinned source is not in sources/nist (it is fetched, not committed)")
        with open(os.path.join(self.CORPUS, "SOURCES.sha256"), encoding="utf-8") as f:
            pinned = dict(reversed(l.split()) for l in f if l.strip() and not l.startswith("#"))
        with open(self.SOURCE, "rb") as f: raw = f.read()
        if hashlib.sha256(raw).hexdigest() != pinned[os.path.basename(self.SOURCE)]:
            self.skipTest("the catalogue in sources/nist is not the file SOURCES.sha256 pins")
        catalogue = json.loads(raw)["catalog"]
        source, written = what_the_authors_list_names(catalogue, read_bundle(os.path.join(self.CORPUS, "sp800-53-core-bundle")))
        self.assertEqual(source, written)
        self.assertEqual((source["assessment-for links"], source["withdrawn controls"], len(source["formal ODP labels"])), (3707, 182, 1458))
        self.assertEqual(source["withdrawn controls that name no successor"], ["cp-10.3", "sc-19"])
        self.assertEqual(len(source["labels of withdrawn controls that name a successor"]), 180)
        root = read_bundle(os.path.join(self.CORPUS, "sp800-53-core-bundle"))["objects/set/root.json"]
        self.assertEqual(root["facets"][F_COMPAT]["metadata"], {k: v for k, v in catalogue["metadata"].items() if k not in ("title", "version")})
        self.assertEqual(root["facets"][F_REF], {"resources": catalogue["back-matter"]["resources"]})
        self.assertEqual(len(root["facets"][F_REF]["resources"]), 201)


if __name__ == "__main__":
    unittest.main()
