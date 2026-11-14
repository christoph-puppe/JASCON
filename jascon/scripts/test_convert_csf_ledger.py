#!/usr/bin/env python3
"""The conversion ledger of convert_csf.py (backlog #41), held on a small
catalogue nobody published, in the shape of the CSF.

    python3 jascon/scripts/test_convert_csf_ledger.py

The rule the converter is held to (author, 2026-11-14): real content is
never dropped. Every source value is carried into the bundle, or is no
content by a rule the ledger checks (a name that only selects a field, a
namespace, an id that another value gives exactly), and a run with an
unaccounted value ends with a non-zero exit.

What the pinned source gives is held twice: the Validators workflow converts
it again and compares the bundle, the two reports and the ledger record byte
for byte, and the last class of this file counts the three losses of the
first ledger in the source and in the committed bundle, where the source is
at hand. The pinned source never takes the branches that say no, so they are
taken here:
  - what the mapping does not know of an element is carried as the source
    has it, and what it cannot carry ends the run;
  - thirteen deliberate defects, each a change to a copy of the converter's
    text that loses a value, states a rule that does not hold, selects a
    value that is not written, or hides a loss behind a drop. Each must end
    the run with a non-zero exit. A change names the line it replaces and
    fails loudly if that line is no longer there.

Standard library only."""
import collections, copy, json, os, shutil, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
NS = "https://ns.nist.gov/csf"
CSF = "https://csrc.nist.gov/ns/csf"
F_CSF, F_EX, F_NARR = f"{NS}/facet/csf@1", f"{NS}/facet/examples@1", f"{NS}/facet/narrative@1"
COMPAT = "https://ns.jascon.net/compat/oscal-1x@1"
RES = "11111111-2222-4333-8444-555555555555"
WHO = "00000000-0000-4000-8000-000000000002"
G, C, S = "csf.catalog.groups[]", "csf.catalog.groups[].controls[]", "csf.catalog.groups[].controls[].controls[]"
OUTCOMES = ("copied", "transformed", "not-content", "intentionally-dropped", "unaccounted")


def catalogue():
    """Two functions. AA holds a live category with five subcategories (one a
    risk of both parties, one withdrawn into two successors, one withdrawn
    without a successor), a category withdrawn into the function BB, and a
    category withdrawn without a successor. BB holds one live category."""
    def prop(name, value): return {"name": name, "value": value}
    def risk(n): return {"name": "risk-party", "ns": CSF, "value": n, "remarks": f"{n} Party Risk"}
    def element(cid, cls, title, sort, label, extra=(), withdrawn=False, links=()):
        e = {"id": cid, "class": cls, "title": title,
             "props": [*extra, prop("sort-id", sort), prop("label", label)] + ([prop("status", "withdrawn")] if withdrawn else [])}
        if links: e["links"] = [{"href": href, "rel": rel} for rel, href in links]
        return e
    def sub(cid, sort, *extra, examples=0, **kw):
        s = element(cid, "subcategory", cid, sort, cid, extra, **kw)
        s["parts"] = [{"id": f"{cid}_statement", "name": "statement", "prose": f"What {cid} states."}]
        s["parts"] += [{"id": f"{cid}.{n:03d}", "name": "example", "ns": CSF, "prose": f"Example {n} of {cid}."} for n in range(1, examples + 1)]
        return s
    def category(cid, title, sort, subs, prose=True, **kw):
        c = element(cid, "category", title, sort, f"{title} ({cid})", **kw)
        c["parts"] = [{"id": f"{cid}_statement", "name": "statement", **({"prose": f"What {title} is about."} if prose else {})}]
        c["controls"] = subs
        return c
    def function(gid, title, sort, categories):
        g = element(gid, "function", title, sort, f"{title} ({gid})")
        g["parts"] = [{"id": f"{gid}_overview", "name": "overview", "prose": f"Why {title}."}]
        g["controls"] = categories
        return g
    return {"catalog": {
        "uuid": "00000000-0000-4000-8000-000000000001",
        "metadata": {"title": "An invented framework", "published": "2026-11-14T00:00:00Z", "last-modified": "2026-11-14T09:00:00Z",
                     "version": "0.1.0", "oscal-version": "1.1.2",
                     "revisions": [{"title": "First draft", "version": "0.0.1", "links": [{"href": RES, "rel": "version-history"}],
                                    "remarks": "Nothing changed."}],
                     "props": [{"name": "framework-identifier", "ns": "https://example.org/ns", "value": "INV"},
                               {"name": "keywords", "value": "invented"}],
                     "links": [{"href": f"#{RES}", "rel": "canonical"}],
                     "roles": [{"id": "author", "title": "Author"}],
                     "parties": [{"uuid": WHO, "type": "organization", "name": "Nobody", "email-addresses": ["nobody@example.org"]}],
                     "responsible-parties": [{"role-id": "author", "party-uuids": [WHO]}],
                     "remarks": "A catalogue nobody published."},
        "groups": [
            function("AA", "ALPHA", "00001", [
                category("AA.ON", "Online", "00001.00002", [
                    sub("AA.ON-01", "00001.00002.00001", risk("1st"), examples=2),
                    sub("AA.ON-02", "00001.00002.00002", risk("1st"), risk("3rd"), examples=1),
                    sub("AA.ON-03", "00001.00002.00003", withdrawn=True,
                        links=[("incorporated_into", "AA.ON-01"), ("moved_to", "AA.ON-02")]),
                    sub("AA.ON-04", "00001.00002.00004", withdrawn=True),
                    sub("AA.ON-05", "00001.00002.00005")]),
                category("AA.OF", "Offline", "00001.00001", [
                    sub("AA.OF-01", "00001.00001.00001", withdrawn=True, links=[("incorporated_into", "AA.ON-01")])],
                    prose=False, withdrawn=True, links=[("incorporated_into", "BB")]),
                category("AA.GO", "Gone", "00001.00003", [
                    sub("AA.GO-01", "00001.00003.00001", withdrawn=True, links=[("moved_to", "AA.ON-05")])],
                    prose=False, withdrawn=True)]),
            function("BB", "BETA", "00002", [
                category("BB.ON", "Other", "00002.00001", [sub("BB.ON-01", "00002.00001.00001", risk("3rd"))])])],
        "back-matter": {"resources": [{"uuid": RES, "title": "The framework",
                                       "rlinks": [{"href": "https://example.org/framework.pdf", "media-type": "application/pdf"}]}]}}}

def online(doc):
    """the subcategories of the live category AA.ON"""
    return doc["catalog"]["groups"][0]["controls"][0]["controls"]

def leaves(node, parts=()):
    if isinstance(node, dict):
        for k, v in node.items(): yield from leaves(v, parts + (k,))
    elif isinstance(node, list):
        for i, v in enumerate(node): yield from leaves(v, parts + (i,))
    else: yield parts, node

def objects_of(bundle):
    """-> {id: object} of every object file under a bundle folder"""
    out = {}
    for base, _, files in os.walk(os.path.join(bundle, "objects")):
        for fn in files:
            with open(os.path.join(base, fn), encoding="utf-8") as f: o = json.load(f)
            out[o["id"]] = o
    return out

def risk_values(objects):
    """-> how often each risk-party value stands in the Requirements"""
    seen = collections.Counter()
    for o in objects.values():
        rp = o.get("facets", {}).get(F_CSF, {}).get("risk-party")
        if rp: seen.update(rp["value"] if isinstance(rp["value"], list) else [rp["value"]])
    return seen


class Converted(unittest.TestCase):
    """Runs copies of the converter on the invented catalogue."""
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="jascon-csf-ledger-")
        cls.n = 0
        cls.plain = cls.convert(catalogue())

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    @classmethod
    def convert(cls, source, changes=(), before=None):
        """Runs a copy of the converter on `source`. changes: (text of the
        converter, what stands in its place). before(out): called before the
        run. -> {done, out, ledger, report, objects}; ledger and report are
        None where the file is not there."""
        cls.n += 1
        tree = os.path.join(cls.tmp, str(cls.n))
        scripts = os.path.join(tree, "jascon", "scripts"); os.makedirs(scripts)
        os.makedirs(os.path.join(tree, "sources", "nist"))
        with open(os.path.join(tree, "sources", "nist", "NIST_CSF_v2.0_catalog.json"), "w", encoding="utf-8") as f: json.dump(source, f)
        shutil.copy(os.path.join(HERE, "oscal_conv_lib.py"), scripts)
        with open(os.path.join(HERE, "convert_csf.py"), encoding="utf-8") as f: code = f.read()
        for old, new in changes:
            if code.count(old) != 1:
                raise AssertionError(f"convert_csf.py holds this line {code.count(old)} times, the test changes it once: {old!r}")
            code = code.replace(old, new)
        with open(os.path.join(scripts, "convert_csf.py"), "w", encoding="utf-8") as f: f.write(code)
        out = os.path.join(tree, "out")
        if before: before(out)
        done = subprocess.run([sys.executable, os.path.join(scripts, "convert_csf.py"), "--out", out], capture_output=True, text=True)
        def read(fn):
            p = os.path.join(out, fn)
            if not os.path.exists(p): return None
            with open(p, encoding="utf-8") as f: return json.load(f)
        return {"done": done, "out": out, "ledger": read("csf-conversion-ledger.json"), "report": read("csf-coverage-report.json"),
                "objects": objects_of(os.path.join(out, "csf-core-bundle"))}

    @staticmethod
    def rows(run):
        return {(r["path"], r["outcome"]): r for r in run["ledger"]["paths"]}

    def count(self, run, path, outcome):
        return self.rows(run).get((path, outcome), {}).get("count", 0)


class PhaseEEveryValueIsCarriedOrIsNoContent(Converted):
    def test_phase_e_no_value_is_unaccounted_and_no_check_fails(self):
        r = self.plain
        self.assertEqual(r["done"].returncode, 0, r["done"].stderr[-800:])
        led, rep = r["ledger"], r["report"]["ledger"]
        self.assertEqual(tuple(led["totals"]), OUTCOMES)
        self.assertEqual((led["totals"]["unaccounted"], led["verification-failures"], led["unaccounted-paths"]), (0, [], []))
        self.assertEqual(led["leaf-values"], sum(1 for _ in leaves(catalogue())))
        self.assertEqual(sum(led["totals"].values()), led["leaf-values"])
        self.assertEqual(sum(row["count"] for row in led["paths"]), led["leaf-values"])
        self.assertEqual((rep["file"], rep["totals"], rep["leaf-values"], rep["verification-failures"]),
                         ("csf-conversion-ledger.json", led["totals"], led["leaf-values"], 0))
        self.assertIn("unaccounted 0; failed checks 0", r["done"].stdout)
        self.assertEqual(sorted(os.listdir(r["out"])),
                         ["csf-conversion-ledger.json", "csf-core-bundle", "csf-coverage-report.json", "csf-coverage-report.md"])

    def test_phase_e_a_run_is_repeated_byte_for_byte(self):
        again = self.convert(catalogue())
        for fn in ("csf-conversion-ledger.json", "csf-coverage-report.json", "csf-coverage-report.md",
                   os.path.join("csf-core-bundle", "content-manifest.json")):
            with open(os.path.join(self.plain["out"], fn), "rb") as a, open(os.path.join(again["out"], fn), "rb") as b:
                self.assertEqual(a.read(), b.read(), fn)

    def test_phase_e_a_subcategory_that_is_a_risk_of_both_parties_carries_both(self):
        # counted in the source and in the written files, not in the converter
        source = collections.Counter(p["value"] for c in doc_controls(catalogue()) for p in c.get("props", []) if p["name"] == "risk-party")
        self.assertEqual(source, {"1st": 2, "3rd": 2})
        self.assertEqual(risk_values(self.plain["objects"]), source)
        self.assertEqual(self.plain["objects"][f"{NS}/req/AA.ON-02"]["facets"][F_CSF],
                         {"risk-party": {"value": ["1st", "3rd"], "remark": ["1st Party Risk", "3rd Party Risk"]}})
        self.assertEqual(self.plain["objects"][f"{NS}/req/AA.ON-01"]["facets"][F_CSF],
                         {"risk-party": {"value": "1st", "remark": "1st Party Risk"}}, "one value is written as it is")
        rows = self.rows(self.plain)
        self.assertEqual((self.count(self.plain, f"{S}.props[].value", "unaccounted"), self.count(self.plain, f"{S}.props[].remarks", "copied")), (0, 4))
        # the name of the prop is the key csf@1 holds the value under; the name that repeats is linked to that key
        names = rows[f"{S}.props[].name", "copied"]
        self.assertEqual(names["count"], 4)
        self.assertEqual(sorted((d["count"], d["as"], "via" in d) for d in names["to"]), [(1, "key", True), (3, "key", False)])

    def test_phase_e_a_withdrawn_item_without_a_successor_is_an_object_with_lifecycle_withdrawn(self):
        objs = self.plain["objects"]
        gone = objs[f"{NS}/set/category/aa-go"]
        self.assertEqual((gone["lifecycle"], gone["title"], gone["label"], gone["members"]), ("withdrawn", {"en": "Gone"}, "Gone (AA.GO)", []))
        old = objs[f"{NS}/req/AA.ON-04"]
        self.assertEqual((old["lifecycle"], old["label"], old["statements"][0]["prose"]), ("withdrawn", "AA.ON-04", {"en": "What AA.ON-04 states."}))
        # each is a member of the Set of its parent, at the place its sort-id gives
        self.assertEqual(objs[f"{NS}/set/function/aa"]["members"],
                         [{"ref": f"{NS}/set/category/aa-on", "sequence": 10}, {"ref": f"{NS}/set/category/aa-go", "sequence": 20}])
        self.assertEqual([(m["ref"].rsplit("/", 1)[1], m["sequence"]) for m in objs[f"{NS}/set/category/aa-on"]["members"]],
                         [("AA.ON-01", 10), ("AA.ON-02", 20), ("AA.ON-04", 40), ("AA.ON-05", 50)], "the place of AA.ON-03 stays empty")
        # `withdrawn` is the source's word: the status prop's value stands as the lifecycle
        self.assertEqual([d["pointer"] for d in self.rows(self.plain)[f"{C}.props[].value", "copied"]["to"]].count("/lifecycle"), 1)
        self.assertEqual({o["lifecycle"] for i, o in objs.items() if i not in (gone["id"], old["id"])}, {"active"})

    def test_phase_e_every_withdrawn_item_of_the_source_is_in_the_bundle(self):
        objs = self.plain["objects"]
        entries = collections.Counter(r["ref"] for o in objs.values() for r in o.get("replaces", []))
        found = collections.defaultdict(collections.Counter)
        for level, uri, items in (("category", lambda i: f"{NS}/set/category/{i.lower().replace('.', '-')}", doc_categories(catalogue())),
                                  ("subcategory", lambda i: f"{NS}/req/{i}", [s for c in doc_categories(catalogue()) for s in c["controls"]])):
            for e in items:
                if not any(p["name"] == "status" and p["value"] == "withdrawn" for p in e["props"]): continue
                found[level]["source"] += 1
                found[level]["object"] += objs.get(uri(e["id"]), {}).get("lifecycle") == "withdrawn"
                found[level]["lineage"] += uri(e["id"]) in entries
                self.assertEqual(entries[uri(e["id"])], len(e.get("links", [])), f"{e['id']}: one entry for each link")
        self.assertEqual({k: dict(v) for k, v in found.items()},
                         {"category": {"source": 2, "object": 1, "lineage": 1}, "subcategory": {"source": 4, "object": 1, "lineage": 3}})
        # a withdrawn category is named as a category Set is, a withdrawn subcategory as a Requirement is
        self.assertEqual(objs[f"{NS}/set/function/bb"]["replaces"], [{"ref": f"{NS}/set/category/aa-of", "mode": "merged-into"}])
        self.assertEqual(objs[f"{NS}/req/AA.ON-02"]["replaces"], [{"ref": f"{NS}/req/AA.ON-03", "mode": "renamed"}])
        self.assertEqual(objs[f"{NS}/req/AA.ON-01"]["annotations"]["nist-withdrawal"][0],
                         {"ref": f"{NS}/req/AA.ON-03", "mode": "merged-into", "label": "AA.ON-03", "title": "AA.ON-03", "prose": "What AA.ON-03 states."})

    def test_phase_e_the_document_metadata_stands_on_the_root_set_as_the_source_has_it(self):
        meta = catalogue()["catalog"]["metadata"]
        root = self.plain["objects"][f"{NS}/set/root"]
        elsewhere = ("title", "version", "oscal-version", "published")
        self.assertEqual(root["facets"][COMPAT], {"metadata": {k: v for k, v in meta.items() if k not in elsewhere}})
        with open(os.path.join(self.plain["out"], "csf-core-bundle", "content-manifest.json"), encoding="utf-8") as f: prov = json.load(f)["provenance"]
        self.assertEqual((root["title"], prov["source"], prov["source-doc-version"], prov["source-oscal-version"], prov["published"]),
                         ({"en": meta["title"]}, meta["title"], meta["version"], meta["oscal-version"], meta["published"]))
        rows = self.rows(self.plain)
        in_metadata = [r for (path, _), r in rows.items() if path.startswith("csf.catalog.metadata.")]
        self.assertEqual({r["outcome"] for r in in_metadata}, {"copied"})
        self.assertEqual(sum(r["count"] for r in in_metadata), sum(1 for _ in leaves(meta)))

    def test_phase_e_what_is_no_content_is_so_by_a_rule_the_ledger_checked(self):
        r = self.plain
        n = lambda path: self.count(r, path, "not-content")
        kinds = lambda path: {(x["kind"], x["count"]) for x in self.rows(r)[path, "not-content"]["rules"]}
        self.assertEqual((n(f"{G}.class"), n(f"{C}.class"), n(f"{S}.class")), (2, 4, 8), "the class says the level the element stands on")
        self.assertEqual(kinds(f"{S}.class"), {("selector", 8)})
        # the names label, sort-id and status select a field; the name of the sort-id of a withdrawn item with a
        # successor goes with its value (below)
        self.assertEqual((n(f"{G}.props[].name"), n(f"{C}.props[].name"), n(f"{S}.props[].name")), (4, 4 * 2 + 2 - 1, 8 * 2 + 4 - 3))
        self.assertEqual((n(f"{G}.parts[].name"), n(f"{C}.parts[].name"), n(f"{S}.parts[].name")), (2, 4, 8 + 3))
        self.assertEqual((n(f"{S}.parts[].ns"), n(f"{S}.props[].ns")), (3, 4))
        self.assertEqual(kinds(f"{S}.props[].ns"), {("namespace", 4)})
        # an id that is rebuilt: the overview parts, the statement parts of the categories and of the three
        # withdrawn subcategories that are no objects
        self.assertEqual((n(f"{G}.parts[].id"), n(f"{C}.parts[].id"), n(f"{S}.parts[].id")), (2, 4, 3))
        self.assertEqual(kinds(f"{C}.parts[].id"), {("rebuilt-id", 4)})
        listed = {(x["kind"], x["rule"]): x["count"] for x in r["report"]["ledger"]["not-content"]}
        self.assertEqual(sum(listed.values()), r["ledger"]["totals"]["not-content"])
        self.assertEqual(sorted(k for k, _ in listed), ["namespace", "rebuilt-id", "rebuilt-id", "selector", "selector", "selector"])

    def test_phase_e_the_drops_that_remain_are_listed_with_a_reading_and_none_is_added(self):
        r = self.plain
        drops = r["report"]["ledger"]["declared-drops"]
        self.assertEqual(sum(d["count"] for d in drops), r["ledger"]["totals"]["intentionally-dropped"])
        self.assertEqual({(d["path"], d["count"], d["example"]) for d in drops},
                         {("csf.catalog.uuid", 1, "00000000-0000-4000-8000-000000000001"),
                          ("csf.catalog.back-matter.resources[].uuid", 1, RES),
                          ("csf.catalog.back-matter.resources[].rlinks[].media-type", 1, "application/pdf"),
                          # the sort-id of the four withdrawn items that name a successor (the first in the document is
                          # AA.ON-03), and the name that selects it; the path is the path map's, one for both levels
                          (f"{C}.props[].value", 4, "00001.00002.00003"), (f"{C}.props[].name", 4, "sort-id")})
        for d in drops:
            self.assertTrue(d["reading"].startswith("content: ") or d["reading"].startswith("not content, because "), d)
            self.assertTrue(d["reason"])
        with open(os.path.join(r["out"], "csf-coverage-report.md"), encoding="utf-8") as f: text = f.read()
        for heading in ("## What is no content (conversion ledger)", "## Declared drops that remain (conversion ledger)",
                        "## Unaccounted source values (conversion ledger)"):
            self.assertIn(heading, text)
        self.assertIn("| source path | count | declared reason | example | reading |", text)

    def test_phase_e_the_path_map_says_of_every_row_what_the_ledger_found(self):
        r = self.plain
        found = collections.defaultdict(collections.Counter)
        for row in r["ledger"]["paths"]:
            found[row["path"].replace(".controls[].controls[]", ".controls[]")][row["outcome"]] += row["count"]
        words = {"copied": "copied", "transformed": "transformed", "not-content": "no content", "intentionally-dropped": "dropped"}
        for row in r["report"]["path-map"]:
            want = "[ledger: " + ", ".join(f"{found[row['path']][k]:,} {words[k]}" for k in OUTCOMES[:4] if found[row["path"]][k]) + "]"
            self.assertTrue(row["destination"].endswith(want), (row["path"], row["destination"][-80:], want))
            self.assertEqual(sum(found[row["path"]].values()), row["count"])
            self.assertEqual("no content" in row["destination"].split("[ledger:")[0], found[row["path"]]["not-content"] > 0, row["path"])


def doc_categories(doc): return [c for g in doc["catalog"]["groups"] for c in g["controls"]]
def doc_controls(doc): return [x for c in doc_categories(doc) for x in [c] + c["controls"]]


class PhaseEWhatTheMappingDoesNotKnow(Converted):
    """A catalogue of this shape may hold what the CSF does not. On an
    element that becomes an object it is carried as the source has it, in
    the compat facet; anywhere else it ends the run."""
    def changed(self, change):
        doc = catalogue(); change(doc)
        return self.convert(doc)

    def test_phase_e_it_is_carried_as_the_source_has_it_on_the_object_it_belongs_to(self):
        other = {"name": "implementation-level", "ns": "http://csrc.nist.gov/ns/rmf", "value": "system"}
        second = {"name": "label", "value": "AA.ON-01 (old)"}
        foreign = {"name": "risk-party", "ns": "https://example.org/ns", "value": "2nd"}
        guidance = {"id": "AA.ON-01_gdn", "name": "guidance", "prose": "Not an outcome."}
        see = {"href": "#AA.ON-05", "rel": "related"}
        def change(doc):
            one = online(doc)[0]
            one["class"] = "basic"
            one["props"] += [other, second, foreign]
            one["parts"].append(guidance)
            one["links"] = [see]
            one["remarks"] = "A remark on the item."
            doc["catalog"]["groups"][1]["parts"][0]["id"] = "BB_ovw"          # an id the rule does not give
        r = self.changed(change)
        self.assertEqual(r["done"].returncode, 0, r["done"].stderr[-800:])
        self.assertEqual((r["ledger"]["totals"]["unaccounted"], r["ledger"]["verification-failures"]), (0, []))
        self.assertEqual(r["objects"][f"{NS}/req/AA.ON-01"]["facets"][COMPAT],
                         {"unmapped": {"class": "basic", "props": [other, second, foreign], "parts": [guidance], "links": [see],
                                       "remarks": "A remark on the item."}})
        self.assertEqual(r["objects"][f"{NS}/req/AA.ON-01"]["label"], "AA.ON-01", "the first label is the label")
        self.assertEqual(r["objects"][f"{NS}/req/AA.ON-01"]["facets"][F_CSF]["risk-party"]["value"], "1st", "a risk-party of another namespace is another prop")
        self.assertEqual(r["objects"][f"{NS}/set/function/bb"]["facets"][COMPAT],
                         {"unmapped": {"parts": [{"id": "BB_ovw", "name": "overview", "prose": "Why BETA."}]}})
        moved = {k: r["ledger"]["totals"][k] - self.plain["ledger"]["totals"][k] for k in OUTCOMES}
        # 14 values more in the source (3 + 2 + 3 of the props, 3 of the part, 2 of the link, the remark), all copied;
        # the class, and the id and the name of the overview part that is carried whole, are no longer no content:
        # they stand in the bundle
        self.assertEqual(moved, {"copied": 14 + 3, "transformed": 0, "not-content": -3, "intentionally-dropped": 0, "unaccounted": 0})
        self.assertNotIn(COMPAT, self.plain["objects"][f"{NS}/req/AA.ON-01"]["facets"], "nothing is unmapped in the plain catalogue")

    def test_phase_e_a_status_is_the_lifecycle_where_the_kernel_knows_the_word_and_is_given_no_meaning_where_it_does_not(self):
        def deprecated(doc): online(doc)[0]["props"].append({"name": "status", "value": "deprecated"})
        r = self.changed(deprecated)
        self.assertEqual(r["done"].returncode, 0, r["done"].stderr[-800:])
        self.assertEqual(r["objects"][f"{NS}/req/AA.ON-01"]["lifecycle"], "deprecated", "the source's word, which is the kernel's too")
        self.assertEqual(r["ledger"]["totals"]["unaccounted"], 0)
        self.assertIn("/lifecycle", [d["pointer"] for d in self.rows(r)[f"{S}.props[].value", "copied"]["to"]])
        def placeholder(doc): online(doc)[0]["props"].append({"name": "status", "value": "placeholder"})
        r = self.changed(placeholder)
        self.assertNotEqual(r["done"].returncode, 0)
        self.assertIn("the source states the status `placeholder` for AA.ON-01", r["done"].stderr)
        self.assertFalse(os.path.exists(r["out"]), "nothing is written as `active` that the source calls something else")

    def gate(self, change, path):
        r = self.changed(change)
        self.assertEqual(r["done"].returncode, 1, r["done"].stdout[-300:])
        self.assertIn("source value(s) unaccounted", r["done"].stderr)
        self.assertGreater(self.count(r, path, "unaccounted"), 0, path)
        self.assertEqual(r["report"]["ledger"]["totals"]["unaccounted"], r["ledger"]["totals"]["unaccounted"], "the reports are written before the run ends")
        return r

    def test_phase_e_a_withdrawn_item_with_a_successor_is_no_object_and_what_its_entry_cannot_hold_ends_the_run(self):
        def change(doc): online(doc)[2]["parts"].append({"id": "AA.ON-03.001", "name": "example", "ns": CSF, "prose": "An example of a withdrawn item."})
        r = self.gate(change, f"{S}.parts[].prose")
        self.assertEqual(r["ledger"]["totals"]["unaccounted"], 4, "id, name, namespace and prose of the example")

    def test_phase_e_a_second_address_of_a_resource_ends_the_run(self):
        def change(doc): doc["catalog"]["back-matter"]["resources"][0]["rlinks"].append({"href": "https://example.org/framework.html"})
        self.gate(change, "csf.catalog.back-matter.resources[].rlinks[].href")

    def test_phase_e_a_third_level_of_controls_ends_the_run(self):
        def change(doc): online(doc)[0]["controls"] = [{"id": "AA.ON-01.a", "title": "Deeper"}]
        self.gate(change, f"{S}.controls[].title")


class PhaseEDeliberateDefects(Converted):
    """Thirteen changes to a copy of the converter. Each must end the run
    with a non-zero exit: a value that is lost is unaccounted, a rule that
    does not hold is a failed check, and a drop cannot stand in for either."""
    FIRST_ONLY = ('values, remarks = props_by_name(t["risk"], led), props_by_name(t["risk"], field="remarks")',
                  'values, remarks = props_by_name(t["risk"][:1], led), props_by_name(t["risk"][:1], field="remarks")')
    DROPS = "for path, reason, _ in PATH_DROPS: led.drop(\"^\" + re.escape(path) + \"$\", reason)\n"

    def red(self, changes, source=None, before=None):
        r = self.convert(source or catalogue(), changes, before)
        self.assertNotEqual(r["done"].returncode, 0, "the defect passed: " + r["done"].stdout[-300:])
        return r

    def test_defect_01_a_value_lost_the_second_risk_party_is_not_read(self):
        r = self.red([self.FIRST_ONLY])
        self.assertEqual(r["done"].returncode, 1)
        # value and remark of the second prop, and with them its name and its namespace
        self.assertEqual({u["path"]: u["count"] for u in r["ledger"]["unaccounted-paths"]},
                         {f"{S}.props[].{k}": 1 for k in ("name", "ns", "remarks", "value")})
        self.assertEqual(r["ledger"]["unaccounted-paths"][3]["pointers"], ["csf#/catalog/groups/0/controls/0/controls/1/props/1/value"])
        self.assertIn("4 source value(s) unaccounted", r["done"].stderr)
        self.assertEqual(risk_values(r["objects"]), {"1st": 2, "3rd": 1}, "the bundle of the failed run is there to be read")

    def test_defect_02_a_rule_that_does_not_hold_an_id_the_rule_does_not_give(self):
        r = self.red([('led.rebuilt(p["id"], N_PART_ID[name], PART_ID[name], eid)', 'led.rebuilt(p["id"], N_PART_ID[name], overview_part_id, eid)')])
        failed = [f for f in r["ledger"]["verification-failures"]]
        self.assertEqual({f["claim"] for f in failed}, {"rebuilt-id"})
        self.assertEqual(len(failed), 4 + 3, "the statement parts of the categories and of the withdrawn subcategories with a successor")
        self.assertIn("7 claim(s) that do not hold", r["done"].stderr)
        self.assertEqual(self.count(r, f"{G}.parts[].id", "not-content"), 2, "the overview ids are what the rule gives")

    def test_defect_03_a_name_that_selects_a_value_that_is_not_written(self):
        r = self.red([('req = {"id": rid, "version": VER, "label": t["label"]["value"] if t["label"] else c["id"],',
                       'req = {"id": rid, "version": VER, "label": c["id"],')])
        # the labels of the five Requirements are written nowhere: the values are unaccounted, and so are the names that select them
        self.assertEqual((self.count(r, f"{S}.props[].value", "unaccounted"), self.count(r, f"{S}.props[].name", "unaccounted")), (5, 5))
        self.assertEqual(r["ledger"]["verification-failures"], [], "no claim was false; the values are missing")

    def test_defect_04_a_namespace_the_mapping_is_not_written_for(self):
        r = self.red([('if "ns" in p and name == "example": led.namespace(p["ns"], N_NS, (CSF_NS,), p["name"])',
                       'if "ns" in p and name == "example": led.namespace(p["ns"], N_NS, ("https://example.org/ns",), p["name"])')])
        self.assertEqual([f["claim"] for f in r["ledger"]["verification-failures"]], ["namespace"] * 3)
        self.assertEqual(self.count(r, f"{S}.parts[].ns", "unaccounted"), 3)

    def test_defect_05_a_class_of_another_level_is_taken_for_the_tag_of_this_one(self):
        doc = catalogue(); online(doc)[0]["class"] = "basic"
        r = self.red([('        if e["class"] == level: led.selector(', '        if True: led.selector(')], source=doc)
        self.assertEqual([(f["source"], f["claim"]) for f in r["ledger"]["verification-failures"]],
                         [("csf#/catalog/groups/0/controls/0/controls/0/class", "selector")])

    def test_defect_06_a_new_drop_declared_over_the_lost_values(self):
        # the loss of defect 01, and a drop that covers every prop: unaccounted reads 0, and the run fails all the same
        r = self.red([self.FIRST_ONLY, (self.DROPS, self.DROPS + 'led.drop(r"\\.props\\[\\]\\.", "not needed")\n')])
        self.assertEqual(r["ledger"]["totals"]["unaccounted"], 0)
        self.assertIn("no declared drop of this converter covers that path with this reason: not needed", r["done"].stderr)

    def test_defect_07_a_declared_drop_widened_over_a_path_on_which_values_are_carried(self):
        # the same loss, hidden behind a reason the converter does list
        wide = "".join(f' ("{S}.props[].{k}", DROP_UUID, "content: x"),\n' for k in ("value", "remarks", "name"))
        head = "PATH_DROPS = [          # (the source path, the reason, the reading)\n"
        r = self.red([self.FIRST_ONLY, (head, head + wide)])
        self.assertEqual(r["ledger"]["totals"]["unaccounted"], 0, "the gate alone would let it pass")
        for k in ("value", "remarks", "name"):
            self.assertIn(f"a drop declared by path covers {S}.props[].{k}, on which other values are carried", r["done"].stderr)

    def test_defect_08_a_withdrawn_item_without_a_successor_is_not_written(self):
        r = self.red([('    return e["id"] not in withdrawn or id(e) not in lineage_links', '    return e["id"] not in withdrawn')])
        self.assertNotIn(f"{NS}/set/category/aa-go", r["objects"])
        self.assertNotIn(f"{NS}/req/AA.ON-04", r["objects"])
        # id, title, label and status of the category; id, title, label, status and statement prose of the subcategory
        self.assertEqual(r["ledger"]["totals"]["unaccounted"], 4 + 5 + 2 * 2 + 2 + 2 + 2,
                         "and what rests on them, for each of the two: the names of label and status, the class, the name "
                         "and the id of the statement part")

    def test_defect_09_the_document_metadata_is_not_written(self):
        r = self.red([('if metadata_rest: root_facets[COMPAT] = {"metadata": metadata_rest}', 'if False: root_facets[COMPAT] = {"metadata": metadata_rest}')])
        meta = catalogue()["catalog"]["metadata"]
        self.assertEqual(r["ledger"]["totals"]["unaccounted"], sum(1 for _ in leaves(meta)) - 4)

    def test_defect_10_a_written_file_is_not_what_the_object_says(self):
        r = self.red([(self.DROPS, '_p = os.path.join(bundle.out, "objects", "req", "aa-on-01.json")\n'
                                   '_o = json.load(open(_p, encoding="utf-8")); _o["label"] = "AA.ON-1"\n'
                                   'json.dump(_o, open(_p, "w", encoding="utf-8"))\n' + self.DROPS)])
        self.assertEqual([(f["object"], f["pointer"]) for f in r["ledger"]["verification-failures"]], [(f"{NS}/req/AA.ON-01", "/label")])
        self.assertIn("1 claim(s) that do not hold", r["done"].stderr)

    def test_defect_11_a_rule_that_gives_another_value_when_it_is_applied_again(self):
        r = self.red([(self.DROPS, 'MODE["moved_to"] = "moved"\n' + self.DROPS)])
        self.assertEqual({f["rule"][:12] for f in r["ledger"]["verification-failures"]}, {"lineage mode"})
        self.assertEqual(len(r["ledger"]["verification-failures"]), 2 * 2, "two links say moved_to; each mode stands twice")

    def test_defect_12_a_lineage_entry_on_an_object_its_link_does_not_name(self):
        r = self.red([('succ_replaces[href].append((e, l)); lineage_links[id(e)].append(l)',
                       'succ_replaces["AA.ON-05" if href == "AA.ON-02" else href].append((e, l)); lineage_links[id(e)].append(l)')])
        self.assertIn("rule lineage inverted", r["done"].stderr)
        self.assertFalse(os.path.exists(r["out"]), "the rule gives no value, and the run stops before it writes")

    def test_defect_13_a_record_on_disk_that_is_not_the_record_of_the_run(self):
        not_written = ('with open(os.path.join(OUTDIR, LEDGER_FILE), "w", encoding="utf-8") as f:\n    json.dump(BY_PATH',
                       'with open(os.devnull, "w", encoding="utf-8") as f:\n    json.dump(BY_PATH')
        r = self.red([not_written])
        self.assertIn("csf-conversion-ledger.json was not written", r["done"].stderr)
        def seed(out):                       # the record of another run lies in the folder, as a committed one does in a checkout
            os.makedirs(out)
            shutil.copy(os.path.join(self.plain["out"], "csf-conversion-ledger.json"), out)
        doc = catalogue(); online(doc)[4]["props"].insert(0, {"name": "risk-party", "ns": CSF, "value": "3rd", "remarks": "3rd Party Risk"})
        r = self.red([not_written], source=doc, before=seed)
        self.assertIn("csf-conversion-ledger.json on disk is not the record of this run", r["done"].stderr)
        self.assertEqual(self.convert(catalogue(), [not_written], before=seed)["done"].returncode, 0,
                         "the same record, left by an equal run, is the record of this run")


class PhaseETheCommittedConversion(unittest.TestCase):
    """The three losses the first ledger found in the CSF, counted in the
    committed bundle - and in the pinned source, where it is at hand (the
    Validators workflow fetches it; the repository does not carry it)."""
    FOLDER = os.path.join(ROOT, "converted_examples", "US.CSF")
    SOURCE = os.path.join(ROOT, "sources", "nist", "NIST_CSF_v2.0_catalog.json")

    def setUp(self):
        if not os.path.isdir(os.path.join(self.FOLDER, "csf-core-bundle")):
            self.skipTest("no converted_examples/ beside jascon/ (the skill unpacked on its own)")
        self.objects = objects_of(os.path.join(self.FOLDER, "csf-core-bundle"))

    def source(self):
        if not os.path.exists(self.SOURCE): self.skipTest("the pinned source is not at hand")
        with open(self.SOURCE, encoding="utf-8") as f: return json.load(f)

    def test_phase_e_the_committed_record_has_no_unaccounted_value_and_no_failed_check(self):
        with open(os.path.join(self.FOLDER, "csf-conversion-ledger.json"), encoding="utf-8") as f: led = json.load(f)
        with open(os.path.join(self.FOLDER, "csf-coverage-report.json"), encoding="utf-8") as f: rep = json.load(f)["ledger"]
        self.assertEqual((led["totals"]["unaccounted"], led["verification-failures"]), (0, []))
        self.assertEqual(sum(led["totals"].values()), led["leaf-values"])
        self.assertEqual((rep["totals"], rep["verification-failures"]), (led["totals"], 0))
        self.assertEqual(sum(d["count"] for d in rep["declared-drops"]), led["totals"]["intentionally-dropped"])
        self.assertEqual(sum(x["count"] for x in rep["not-content"]), led["totals"]["not-content"])

    def test_phase_e_the_bundle_carries_every_risk_party_value(self):
        self.assertEqual(risk_values(self.objects), {"1st": 88, "3rd": 37})
        doc = self.source()
        self.assertEqual(collections.Counter(p["value"] for c in doc_controls(doc) for p in c.get("props", []) if p["name"] == "risk-party"),
                         risk_values(self.objects))

    def test_phase_e_the_bundle_holds_every_withdrawn_item(self):
        withdrawn = {i: o for i, o in self.objects.items() if o["lifecycle"] == "withdrawn"}
        self.assertEqual(sorted(i.rsplit("/", 1)[1] for i in withdrawn), ["de-dp", "pr-ip", "pr-pt", "rs-rp"])
        entries = {r["ref"] for o in self.objects.values() for r in o.get("replaces", [])}
        self.assertEqual((len(entries), len(entries & set(withdrawn))), (87, 0), "an item is an object or a lineage entry, not both")
        doc = self.source()
        gone = [(level, e["id"]) for level, items in (("category", doc_categories(doc)), ("subcategory", [s for c in doc_categories(doc) for s in c.get("controls", [])]))
                for e in items if any(p["name"] == "status" and p["value"] == "withdrawn" for p in e.get("props", []))]
        self.assertEqual(collections.Counter(level for level, _ in gone), {"category": 12, "subcategory": 79})
        uri = {"category": lambda i: f"{NS}/set/category/{i.lower().replace('.', '-')}", "subcategory": lambda i: f"{NS}/req/{i}"}
        self.assertEqual([i for level, i in gone if uri[level](i) not in entries and uri[level](i) not in withdrawn], [])

    def test_phase_e_the_bundle_holds_the_document_metadata(self):
        compat = self.objects[f"{NS}/set/root"]["facets"][COMPAT]["metadata"]
        self.assertEqual(list(compat), ["last-modified", "revisions", "props", "links", "roles", "parties", "responsible-parties"])
        meta = self.source()["catalog"]["metadata"]
        self.assertEqual(compat, {k: v for k, v in meta.items() if k not in ("title", "version", "oscal-version", "published")})
        self.assertEqual(sum(1 for _ in leaves(compat)) + 4, sum(1 for _ in leaves(meta)))


if __name__ == "__main__":
    unittest.main()
