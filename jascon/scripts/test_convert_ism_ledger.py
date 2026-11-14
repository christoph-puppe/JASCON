#!/usr/bin/env python3
"""The conversion ledger of convert_ism.py (backlog #41), held on a small
catalogue nobody published, in the shape of the ISM.

    python3 jascon/scripts/test_convert_ism_ledger.py

What the pinned source gives is held elsewhere: the Validators workflow
converts it again and compares the bundle, the two reports and the ledger
record byte for byte. The pinned source never takes the branches that say
no, so they are taken here:
  - a value the converter does not carry is unaccounted, not dropped: a
    sort-id that is not its place in the document, a second `label` prop,
    a part that is no statement, a heading without a part, the revision of
    a control;
  - a run ends with an error when a claim of the ledger does not hold in
    the written files, when a value is dropped where the path map does not
    say so, when a drop is of neither of the two cases, when a drop is
    declared for a whole path on which other values are carried or on a
    row that is carried, and when the record on disk is not the record of
    the run.
These change a copy of the converter's text. Each change names the line it
replaces and fails loudly if that line is no longer there.

Standard library only."""
import copy, json, os, shutil, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
IFA = "as decided for IFA on 2026-11-13: "
RES = "11111111-2222-4333-8444-555555555555"
C = "ism.catalog.groups[].groups[].groups[].controls[]"


def catalogue():
    """Two chapters. `Front matter` is a heading only and holds one group
    with an overview text that links into the back-matter. `Guidelines`
    holds a section, a topic and two controls: one with a revision and
    three markers, one with a `label` prop and one marker."""
    def sort_id(*at): return {"name": "sort-id", "value": "catalog[1]" + "".join(f".{k}[{n}]" for k, n in at)}
    def prop(name, value): return {"name": name, "ns": "https://example.org/ns/1.0", "value": value}
    def statement(cid): return [{"id": f"{cid}_smt", "name": "statement", "prose": f"What {cid} asks for is done."}]
    return {"catalog": {
        "uuid": "00000000-0000-4000-8000-000000000001",
        "metadata": {"title": "An invented manual", "published": "2026-11-14T00:00:00Z", "last-modified": "2026-11-14T00:00:00Z",
                     "version": "1.0", "oscal-version": "1.1.2",
                     "links": [{"href": f"#{RES}", "rel": "alternate"}],
                     "roles": [{"id": "prepared-by", "title": "Document creator"}],
                     "parties": [{"uuid": "00000000-0000-4000-8000-000000000002", "type": "organization", "name": "Nobody"}],
                     "responsible-parties": [{"role-id": "prepared-by", "party-uuids": ["00000000-0000-4000-8000-000000000002"]}]},
        "groups": [
            {"title": "Front matter", "props": [sort_id(("group", "1"))], "groups": [
                {"title": "Purpose", "props": [sort_id(("group", "1"), ("group", "1"))],
                 "parts": [{"name": "overview", "prose": f"See [the manual](#{RES})."}]}]},
            {"title": "Guidelines", "props": [sort_id(("group", "2"))], "groups": [
                {"title": "Governance", "props": [sort_id(("group", "2"), ("group", "1"))],
                 "parts": [{"name": "overview", "prose": "Why governance."}], "groups": [
                    {"title": "Roles", "props": [sort_id(("group", "2"), ("group", "1"), ("group", "1"))],
                     "parts": [{"name": "overview", "prose": "Who does what."}], "controls": [
                        {"id": "ism-0001", "class": "ISM-control", "title": "Control: ism-0001",
                         "props": [sort_id(("group", "2"), ("group", "1"), ("group", "1"), ("control", "1")),
                                   prop("revision", "3"), prop("updated", "Dec-23"), prop("applicability", "NC"),
                                   prop("applicability", "OS"), prop("essential-eight-applicability", "ML1")],
                         "parts": statement("ism-0001")},
                        {"id": "ism-principle-gov-01", "class": "ISM-principle", "title": "Accountability",
                         "props": [sort_id(("group", "2"), ("group", "1"), ("group", "1"), ("control", "2")),
                                   {"name": "label", "value": "GOV-01"}, prop("applicability", "NC")],
                         "parts": statement("ism-principle-gov-01")}]}]}]}],
        "back-matter": {"resources": [{"uuid": RES, "title": "The manual", "rlinks": [{"href": "https://example.org/manual.pdf"}]}]}}}

def controls(doc):
    return doc["catalog"]["groups"][1]["groups"][0]["groups"][0]["controls"]


class Backlog41TheLedgerOfTheIsmConverter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="jascon-ism-ledger-")
        cls.n = 0
        cls.plain = cls.convert(catalogue())

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    @classmethod
    def convert(cls, source, changes=(), before=None):
        """Runs a copy of the converter on `source`. changes: (text of the
        converter, what stands in its place). before(out): called before the
        run. -> {done, out, ledger, report}, the last two None where the file
        is not there."""
        cls.n += 1
        tree = os.path.join(cls.tmp, str(cls.n))
        scripts = os.path.join(tree, "jascon", "scripts"); os.makedirs(scripts)
        os.makedirs(os.path.join(tree, "sources"))
        with open(os.path.join(tree, "sources", "ism.json"), "w", encoding="utf-8") as f: json.dump(source, f)
        shutil.copy(os.path.join(HERE, "oscal_conv_lib.py"), scripts)
        with open(os.path.join(HERE, "convert_ism.py"), encoding="utf-8") as f: code = f.read()
        for old, new in changes:
            if code.count(old) != 1:
                raise AssertionError(f"convert_ism.py holds this line {code.count(old)} times, the test changes it once: {old!r}")
            code = code.replace(old, new)
        with open(os.path.join(scripts, "convert_ism.py"), "w", encoding="utf-8") as f: f.write(code)
        out = os.path.join(tree, "out")
        if before: before(out)
        done = subprocess.run([sys.executable, os.path.join(scripts, "convert_ism.py"), "--out", out], capture_output=True, text=True)
        def read(fn):
            p = os.path.join(out, fn)
            if not os.path.exists(p): return None
            with open(p, encoding="utf-8") as f: return json.load(f)
        return {"done": done, "out": out, "ledger": read("ism-conversion-ledger.json"), "report": read("ism-coverage-report.json")}

    @staticmethod
    def rows(run):
        return {(r["path"], r["outcome"]): r for r in run["ledger"]["paths"]}

    def test_backlog_41_every_value_is_in_one_row_and_no_check_fails(self):
        r = self.plain
        self.assertEqual(r["done"].returncode, 0, r["done"].stderr[-600:])
        led, rep = r["ledger"], r["report"]["ledger"]
        self.assertEqual(led["verification-failures"], [])
        self.assertEqual(sum(led["totals"].values()), led["leaf-values"])
        self.assertEqual(sum(row["count"] for row in led["paths"]), led["leaf-values"])
        self.assertEqual((rep["file"], rep["totals"], rep["leaf-values"]), ("ism-conversion-ledger.json", led["totals"], led["leaf-values"]))
        self.assertEqual(rep["declared-drops"]["not-declared-by-the-path-map"], 0)
        self.assertIn(f"unaccounted {led['totals']['unaccounted']}", r["done"].stdout, "the count is printed, and the run ends with 0")
        self.assertGreater(led["totals"]["unaccounted"], 0)

    def test_backlog_41_what_is_carried_what_is_made_by_a_rule_and_what_is_neither(self):
        rows = self.rows(self.plain)
        count = lambda path, outcome: rows.get((path, outcome), {}).get("count", 0)
        self.assertEqual(count(f"{C}.title", "copied"), 2)
        self.assertEqual(count(f"{C}.parts[].prose", "copied"), 2)
        self.assertEqual(count(f"{C}.id", "transformed"), 2)
        # the values of the props: a label and four markers by a rule, two sort-ids absorbed, revision and updated neither
        self.assertEqual({o: count(f"{C}.props[].value", o) for o in ("transformed", "intentionally-dropped", "unaccounted")},
                         {"transformed": 5, "intentionally-dropped": 2, "unaccounted": 2})
        rules = {d["rule"] for d in rows[f"{C}.props[].value", "transformed"]["to"]}
        self.assertIn("label: the value of the prop that is named `label`, unchanged", rules)
        self.assertIn("baseline Set id from the prop name (its kind) and the marker", rules)
        # the second control that carries NC is linked to the Set the first one made
        self.assertTrue(any(d.get("via") for d in rows[f"{C}.props[].value", "transformed"]["to"]))
        # a heading without a part of its own: its title is in no object
        self.assertEqual((count("ism.catalog.groups[].title", "copied"), count("ism.catalog.groups[].title", "unaccounted")), (1, 1))
        self.assertEqual(self.plain["report"]["ledger"]["group-titles-not-carried"], ["ism#/catalog/groups/0/title"])
        self.assertEqual(count("ism.catalog.groups[].groups[].title", "copied"), 2, "`Purpose` rides its overview part on the root Set")
        for path in ("ism.catalog.metadata.published", "ism.catalog.metadata.links[].href", "ism.catalog.metadata.responsible-parties[].role-id"):
            self.assertEqual(count(path, "unaccounted"), 1, path)
        self.assertEqual(self.plain["report"]["ledger"]["links-into-the-back-matter"],
                         {"texts": 1, "links": 1, "resources": 1, "resources-in-the-source": 1})

    def test_backlog_41_a_drop_is_one_of_two_cases_and_says_which(self):
        rows, drops = self.rows(self.plain), self.plain["report"]["ledger"]["declared-drops"]
        reason = lambda path: [x["reason"] for x in rows[path, "intentionally-dropped"]["reasons"]]
        self.assertTrue(reason("ism.catalog.uuid")[0].startswith(IFA))
        self.assertTrue(reason("ism.catalog.metadata.parties[].name")[0].startswith(IFA))
        self.assertTrue(reason(f"{C}.parts[].name")[0].startswith(IFA))
        self.assertTrue(reason("ism.catalog.back-matter.resources[].title")[0].startswith("path map, declared drop"))
        self.assertTrue(reason(f"{C}.props[].ns")[0].startswith("path map, absorbed"))
        self.assertEqual({d["case"] for d in drops["reasons"]}, {"path-map", "ifa"})
        self.assertEqual(drops["path-map"] + drops["as-decided-for-ifa"], self.plain["ledger"]["totals"]["intentionally-dropped"])
        for d in drops["reasons"]:
            self.assertEqual(d["reason"].startswith(IFA), d["case"] == "ifa", d["reason"])
        # 3 back-matter values, 6 namespaces, the sort-ids of 5 groups and 2 controls with their names |
        # the uuid, 2 role and 3 party values, 2 type tags
        self.assertEqual((drops["path-map"], drops["as-decided-for-ifa"]), (3 + 6 + 14, 1 + 5 + 2))

    def test_backlog_41_a_run_is_repeated_byte_for_byte(self):
        again = self.convert(catalogue())
        for fn in ("ism-conversion-ledger.json", "ism-coverage-report.json", "ism-coverage-report.md"):
            with open(os.path.join(self.plain["out"], fn), "rb") as a, open(os.path.join(again["out"], fn), "rb") as b:
                self.assertEqual(a.read(), b.read(), fn)

    def changed(self, change):
        """-> (the run on a changed catalogue, by how much each total moved)"""
        doc = catalogue(); change(doc)
        r = self.convert(doc)
        self.assertEqual(r["done"].returncode, 0, r["done"].stderr[-600:])
        self.assertEqual(r["ledger"]["verification-failures"], [])
        return r, {k: r["ledger"]["totals"][k] - self.plain["ledger"]["totals"][k] for k in r["ledger"]["totals"]}

    def test_backlog_41_a_sort_id_that_is_not_its_place_is_not_absorbed(self):
        def change(doc): controls(doc)[0]["props"][0]["value"] = "catalog[1].group[2].group[1].group[1].control[7]"
        r, moved = self.changed(change)
        self.assertEqual(moved, {"copied": 0, "transformed": 0, "intentionally-dropped": -2, "unaccounted": 2})
        self.assertEqual(r["report"]["ledger"]["sort-ids"], {"equal-to-position": 6, "other": 1})

    def test_backlog_41_a_second_label_overwrites_the_first_and_the_ledger_says_so(self):
        def change(doc): controls(doc)[1]["props"].insert(1, {"name": "label", "value": "GOV-01-OLD"})
        r, moved = self.changed(change)
        self.assertEqual(moved, {"copied": 0, "transformed": 0, "intentionally-dropped": 0, "unaccounted": 2})
        self.assertEqual([u["pointers"][0] for u in r["ledger"]["unaccounted-paths"] if u["path"] == f"{C}.props[].value"][0],
                         "ism#/catalog/groups/1/groups/0/groups/0/controls/0/props/1/value")       # the revision comes first
        lost = [x for x in r["report"]["ledger"]["path-map-and-ledger-disagree"] if "`label`" in x["path"]]
        self.assertEqual([(x["level"], x["ledger"], x["values"]) for x in lost], [("L1", "unaccounted", 1)] * 2)

    def test_backlog_41_a_part_that_is_no_statement_is_no_type_tag_and_a_second_part_is_not_read(self):
        def renamed(doc): controls(doc)[0]["parts"][0]["name"] = "guidance"
        _, moved = self.changed(renamed)
        self.assertEqual(moved, {"copied": 0, "transformed": 0, "intentionally-dropped": -1, "unaccounted": 1})
        def second(doc): controls(doc)[0]["parts"].append({"id": "ism-0001_gdn", "name": "guidance", "prose": "Not read."})
        _, moved = self.changed(second)
        self.assertEqual(moved, {"copied": 0, "transformed": 0, "intentionally-dropped": 0, "unaccounted": 3})

    def test_backlog_41_a_claim_that_does_not_hold_in_the_written_file_ends_the_run(self):
        # the label of one Requirement is changed on disk after it is written and before the accounting
        r = self.convert(catalogue(), [('w("content-manifest.json", manifest)\n',
                                        'w("content-manifest.json", manifest)\n'
                                        '_o = json.load(open(os.path.join(OUT, "objects/req-ism-0001.json"), encoding="utf-8"))\n'
                                        '_o["label"] = "ISM-9999"; w("objects/req-ism-0001.json", _o)\n')])
        self.assertNotEqual(r["done"].returncode, 0)
        self.assertIn("1 claim(s) of the ledger do not hold in the written files", r["done"].stderr)
        self.assertEqual([(f["pointer"], f["rule"][:10]) for f in r["ledger"]["verification-failures"]], [("/label", "label from")])
        self.assertEqual(r["report"]["ledger"]["verification-failures"], 1, "the reports are written before the run ends")

    def test_backlog_41_a_drop_the_path_map_does_not_declare_ends_the_run(self):
        # every drop of the path map widened to the whole catalogue: without the check, unaccounted would read 0
        r = self.convert(catalogue(), [('    led.drop("^" + re.escape(f"{TAG}.{_path}") + "$", _reason)',
                                        '    led.drop("^" + re.escape(f"{TAG}.catalog."), _reason)')])
        self.assertNotEqual(r["done"].returncode, 0)
        self.assertIn("dropped where the path map does not call the path absorbed or a declared drop", r["done"].stderr)
        self.assertEqual(r["ledger"]["totals"]["unaccounted"], 0)
        self.assertEqual(r["report"]["ledger"]["declared-drops"]["not-declared-by-the-path-map"], self.plain["ledger"]["totals"]["unaccounted"])

    def test_backlog_41_a_drop_for_a_whole_path_on_which_other_values_are_carried_ends_the_run(self):
        # the titles of the chapters are declared a drop: `Guidelines` is carried, and `Front matter`, which is
        # lost, would read as dropped on purpose
        r = self.convert(catalogue(), [('# controls -> Requirements (controls appear at group depth 1 and 2)\n',
                                        'dest("catalog.groups[].title", "declared-drop", "not carried", DROP_UUID)\n')])
        self.assertNotEqual(r["done"].returncode, 0)
        self.assertIn("the drop declared for the path catalog.groups[].title covers values of a path on which others are carried",
                      r["done"].stderr)
        self.assertEqual(r["report"]["ledger"]["declared-drops"]["not-declared-by-the-path-map"], 0, "the row says drop: only this check sees it")

    def test_backlog_41_a_drop_of_neither_case_ends_the_run(self):
        r = self.convert(catalogue(), [('    led.drop("^" + re.escape(f"{TAG}.{_path}") + "$", _reason)',
                                        '    led.drop("^" + re.escape(f"{TAG}.{_path}") + "$", "because")')])
        self.assertNotEqual(r["done"].returncode, 0)
        self.assertIn("a declared drop is neither stated by the path map nor of a class decided for IFA", r["done"].stderr)

    def test_backlog_41_a_drop_declared_on_a_row_that_is_carried_stops_the_run_before_it_writes(self):
        r = self.convert(catalogue(), [('    dest(base + ".title", "L1", "Requirement title")',
                                        '    dest(base + ".title", "L1", "Requirement title", DROP_NS)')])
        self.assertNotEqual(r["done"].returncode, 0)
        self.assertIn("is L1, and a drop is declared for it", r["done"].stderr)
        self.assertFalse(os.path.exists(r["out"]))

    def test_backlog_41_a_record_on_disk_that_is_not_the_record_of_the_run_ends_the_run(self):
        not_written = ('with open(os.path.join(OUTDIR, LEDGER_FILE), "w", encoding="utf-8") as f:',
                       'with open(os.devnull, "w", encoding="utf-8") as f:')
        r = self.convert(catalogue(), [not_written])
        self.assertNotEqual(r["done"].returncode, 0)
        self.assertIn("ism-conversion-ledger.json was not written", r["done"].stderr)
        # the record of another run lies in the folder, as a committed one does in a checkout
        def seed(out):
            os.makedirs(out)
            shutil.copy(os.path.join(self.plain["out"], "ism-conversion-ledger.json"), out)
        doc = catalogue(); controls(doc)[1]["props"].insert(1, {"name": "label", "value": "GOV-01-OLD"})
        r = self.convert(doc, [not_written], before=seed)
        self.assertNotEqual(r["done"].returncode, 0)
        self.assertIn("ism-conversion-ledger.json on disk is not the record of this run", r["done"].stderr)
        self.assertEqual(self.convert(catalogue(), [not_written], before=seed)["done"].returncode, 0,
                         "the same record, left by an equal run, is the record of this run")


if __name__ == "__main__":
    unittest.main()
