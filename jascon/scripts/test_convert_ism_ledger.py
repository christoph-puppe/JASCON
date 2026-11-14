#!/usr/bin/env python3
"""The conversion ledger of convert_ism.py (backlog #41), held on a small
catalogue nobody published, in the shape of the ISM.

    python3 jascon/scripts/test_convert_ism_ledger.py

What the pinned source gives is held elsewhere: the Validators workflow
converts it again and compares the bundle, the two reports and the ledger
record byte for byte. Held here is the author's rule of 2026-11-14 - "real
content is never dropped", and a run with an unaccounted value ends with 1:
  - every value of the catalogue is carried or is no content by a rule the
    ledger checked, and the bundle read back from disk holds what the
    source says: the revision of a control, a Set for a chapter that holds
    no control, the resource a link in a text names, the document's
    metadata;
  - a source the converter would lose a value of ends the run with 1: a
    second `label`, a second part, a part that is no statement, a sort-id
    that is not its place, a link that names no resource;
  - a converter that is broken in one place ends the run with 1: a value
    that is no longer written, a rule that does not give the id, a name
    that selects a value which is not written, a drop nobody listed, a
    path map that says something else than the ledger found, a record on
    disk that is not the record of the run.
The last group changes a copy of the converter's text. Each change names
the line it replaces and fails loudly if that line is no longer there.

Standard library only."""
import json, os, shutil, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
NS = "https://ns.cyber.gov.au/ism"
COMPAT = "https://ns.jascon.net/compat/oscal-1x@1"
REFERENCES = NS + "/facet/references@1"
ISM_NS = "https://cyber.gov.au/ns/ism/oscal/3.0"
IFA = "as decided for IFA on 2026-11-13: "
RES = "11111111-2222-4333-8444-555555555555"
C = "ism.catalog.groups[].groups[].groups[].controls[]"


def catalogue():
    """Two chapters. `Front matter` is a heading only and holds one group
    with an overview text that links into the back-matter. `Guidelines`
    holds a section, a topic and two controls: one with a revision and
    three markers, one with a `label` prop and one marker."""
    def sort_id(*at): return {"name": "sort-id", "value": "catalog[1]" + "".join(f".{k}[{n}]" for k, n in at)}
    def prop(name, value): return {"name": name, "ns": ISM_NS, "value": value}
    def statement(cid): return [{"id": f"{cid}_smt", "name": "statement", "prose": f"What {cid} asks for is done."}]
    return {"catalog": {
        "uuid": "00000000-0000-4000-8000-000000000001",
        "metadata": {"title": "An invented manual", "published": "2026-11-13T00:00:00Z", "last-modified": "2026-11-14T00:00:00Z",
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
        run. -> {done, out, ledger, report, objects}; ledger and report are
        None where the file is not there, objects is {id: object} as the
        manifest of the written bundle lists them."""
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
        def read(*rel):
            p = os.path.join(out, *rel)
            if not os.path.exists(p): return None
            with open(p, encoding="utf-8") as f: return json.load(f)
        manifest = read("ism-core-bundle", "content-manifest.json")
        objects = {e["id"]: read("ism-core-bundle", e["path"]) for e in manifest["objects"]} if manifest else {}
        return {"done": done, "out": out, "ledger": read("ism-conversion-ledger.json"), "report": read("ism-coverage-report.json"),
                "manifest": manifest, "objects": objects}

    @staticmethod
    def rows(run):
        return {(r["path"], r["outcome"]): r for r in run["ledger"]["paths"]}

    def count(self, run, path, outcome):
        return self.rows(run).get((path, outcome), {}).get("count", 0)

    # ---- the catalogue as it is: nothing is lost ----
    def test_backlog_41_every_value_is_carried_or_is_no_content_and_the_run_ends_with_0(self):
        r = self.plain
        self.assertEqual(r["done"].returncode, 0, r["done"].stderr[-600:])
        led, rep = r["ledger"], r["report"]["ledger"]
        self.assertEqual(led["verification-failures"], [])
        self.assertEqual(sorted(led["totals"]), ["copied", "intentionally-dropped", "not-content", "transformed", "unaccounted"])
        self.assertEqual(led["totals"]["unaccounted"], 0)
        self.assertEqual(led["unaccounted-paths"], [])
        self.assertEqual(sum(led["totals"].values()), led["leaf-values"])
        self.assertEqual(sum(row["count"] for row in led["paths"]), led["leaf-values"])
        self.assertEqual((rep["file"], rep["totals"], rep["leaf-values"]), ("ism-conversion-ledger.json", led["totals"], led["leaf-values"]))
        self.assertEqual(rep["path-map-and-ledger-disagree"], [])
        self.assertEqual(r["report"]["totals"]["unmapped"], 0)

    def test_backlog_41_what_is_copied_what_is_made_by_a_rule_and_what_is_no_content(self):
        r = self.plain
        self.assertEqual(self.count(r, f"{C}.title", "copied"), 2)
        self.assertEqual(self.count(r, f"{C}.parts[].prose", "copied"), 2)
        self.assertEqual(self.count(r, f"{C}.id", "transformed"), 2)
        # the values of the props: label, revision and updated as they are; four markers by a rule; two sort-ids rebuilt
        self.assertEqual({o: self.count(r, f"{C}.props[].value", o) for o in ("copied", "transformed", "not-content")},
                         {"copied": 3, "transformed": 4, "not-content": 2})
        # their names: revision and updated are written; a marker's name gives the kind of its Set; label and sort-id select
        self.assertEqual({o: self.count(r, f"{C}.props[].name", o) for o in ("copied", "transformed", "not-content")},
                         {"copied": 2, "transformed": 4, "not-content": 3})
        # their namespaces: written with revision and updated; the one the mapping reads the markers in is no content
        self.assertEqual({o: self.count(r, f"{C}.props[].ns", o) for o in ("copied", "not-content")}, {"copied": 2, "not-content": 4})
        self.assertEqual(self.count(r, f"{C}.parts[].name", "not-content"), 2)
        rules = {(x["kind"], x["rule"][:22]): x["values"] for x in r["report"]["ledger"]["not-content"]}
        self.assertEqual(rules, {("namespace", "the namespace of a pro"): 4, ("rebuilt-id", "a sort-id is its paren"): 7,
                                 ("selector", "the name `statement` o"): 2, ("selector", "the name of a prop sel"): 8})
        self.assertEqual(sum(rules.values()), r["ledger"]["totals"]["not-content"])
        self.assertEqual(self.rows(r)[f"{C}.props[].value", "not-content"]["rules"][0]["kind"], "rebuilt-id")
        # every title of a group is the title of a Set, the heading's too
        for path, n in (("ism.catalog.groups[].title", 2), ("ism.catalog.groups[].groups[].title", 2),
                        ("ism.catalog.groups[].groups[].groups[].title", 1)):
            self.assertEqual(self.count(r, path, "copied"), n, path)
        for path in ("ism.catalog.metadata.published", "ism.catalog.metadata.links[].href", "ism.catalog.metadata.parties[].name",
                     "ism.catalog.metadata.responsible-parties[].role-id", "ism.catalog.back-matter.resources[].uuid",
                     "ism.catalog.back-matter.resources[].rlinks[].href"):
            self.assertEqual(self.count(r, path, "copied"), 1, path)

    def test_backlog_41_the_bundle_read_back_holds_what_the_source_says(self):
        o, src = self.plain["objects"], catalogue()["catalog"]
        self.assertEqual(sum(1 for x in o.values() if "statements" in x), 2)
        self.assertEqual(sum(1 for x in o.values() if "members" in x), 11, "5 groups, the root, 3 markers, 2 classes")
        # a control's revision and the month of its change, as the source writes the props
        props = o[NS + "/req/ism-0001"]["facets"][COMPAT]["props"]
        self.assertEqual(props, [{"name": "revision", "ns": ISM_NS, "value": "3"}, {"name": "updated", "ns": ISM_NS, "value": "Dec-23"}])
        self.assertEqual(o[NS + "/req/ism-0001"]["version"], "1.0", "the version is the catalogue's; the revision is not put in its place")
        self.assertNotIn("facets", o[NS + "/req/ism-principle-gov-01"])
        self.assertEqual(o[NS + "/req/ism-principle-gov-01"]["label"], "GOV-01")
        # the chapter that holds no control is a Set in its place, and the group below it a Set with no member
        root = o[NS + "/set/tax/ism"]
        front = o[NS + "/set/tax/front-matter"]
        self.assertEqual([m["ref"] for m in root["members"]], [NS + "/set/tax/front-matter", NS + "/set/tax/guidelines"])
        self.assertEqual((front["title"], [m["ref"] for m in front["members"]]), ({"en": "Front matter"}, [NS + "/set/tax/front-matter-purpose"]))
        purpose = o[NS + "/set/tax/front-matter-purpose"]
        self.assertEqual(purpose["members"], [])
        self.assertEqual(purpose["facets"][COMPAT]["group-parts"], [{"group": "Purpose", "name": "overview", "prose": {"en": f"See [the manual](#{RES})."}}])
        self.assertNotIn("group-parts", root["facets"][COMPAT], "an overview text stands on the Set of its own group")
        # the resource the link names, and the document's metadata
        self.assertEqual(root["facets"][REFERENCES]["resources"], src["back-matter"]["resources"])
        self.assertEqual(root["facets"][COMPAT]["metadata"], {k: v for k, v in src["metadata"].items() if k not in ("title", "version")})
        self.assertEqual((root["title"], root["version"]), ({"en": "An invented manual"}, "1.0"))
        self.assertEqual({k: self.plain["manifest"]["provenance"].get(k) for k in ("source-version", "source-oscal-version", "author-ref", "date")},
                         {"source-version": "1.0", "source-oscal-version": "1.1.2", "author-ref": NS + "/party/nobody", "date": "2026-11-14"})
        self.assertEqual(sorted(s["id"] for s in self.plain["manifest"]["facet-schemas"]),
                         [NS + "/facet/references", "https://ns.jascon.net/compat/oscal-1x"])
        back = self.plain["report"]["ledger"]["read-back-from-the-written-bundle"]
        self.assertEqual({k: back[k] for k in ("sets-with-no-member", "requirements-with-revision", "resources", "links-in-texts",
                                               "links-that-name-a-resource-of-the-bundle", "sort-ids-in-the-source",
                                               "sort-ids-rebuilt-from-the-bundle")},
                         {"sets-with-no-member": 1, "requirements-with-revision": 1, "resources": 1, "links-in-texts": 1,
                          "links-that-name-a-resource-of-the-bundle": 1, "sort-ids-in-the-source": 7, "sort-ids-rebuilt-from-the-bundle": 7})

    def test_backlog_41_no_drop_is_declared_and_the_documents_uuid_is_carried(self):
        # until 2026-11-14 one drop was declared, the uuid of the source document; the author decided that it is carried
        self.assertEqual(self.plain["report"]["ledger"]["declared-drops"], [])
        self.assertEqual(self.plain["ledger"]["totals"]["intentionally-dropped"], 0)
        uuid = [r for r in self.plain["ledger"]["paths"] if r["path"] == "ism.catalog.uuid"]
        self.assertEqual([(r["outcome"], r["count"], r["to"]) for r in uuid],
                         [("copied", 1, [{"pointer": "/facets/https:~1~1ns.jascon.net~1compat~1oscal-1x@1/uuid", "count": 1}])])
        self.assertEqual(self.plain["report"]["lifecycle-default"]["origin"], "converter-default")
        with open(os.path.join(self.plain["out"], "ism-coverage-report.md"), encoding="utf-8") as f: text = f.read()
        self.assertIn("### Declared drops that remain", text)
        self.assertIn("### What is no content", text)

    def test_backlog_41_a_run_is_repeated_byte_for_byte(self):
        again = self.convert(catalogue())
        for fn in ("ism-conversion-ledger.json", "ism-coverage-report.json", "ism-coverage-report.md",
                   os.path.join("ism-core-bundle", "content-manifest.json")):
            with open(os.path.join(self.plain["out"], fn), "rb") as a, open(os.path.join(again["out"], fn), "rb") as b:
                self.assertEqual(a.read(), b.read(), fn)

    # ---- another shape of the source that the converter carries ----
    def carried(self, change):
        doc = catalogue(); change(doc)
        r = self.convert(doc)
        self.assertEqual(r["done"].returncode, 0, r["done"].stderr[-600:])
        self.assertEqual((r["ledger"]["totals"]["unaccounted"], r["ledger"]["verification-failures"]), (0, []))
        return r

    def test_backlog_41_a_prop_the_mapping_has_no_member_for_is_written_as_it_is(self):
        other = {"name": "implementation-level", "ns": "http://csrc.nist.gov/ns/rmf", "value": "system"}
        foreign = {"name": "applicability", "ns": "https://example.org/another-meaning", "value": "NC"}
        def change(doc): controls(doc)[1]["props"] += [other, foreign]
        r = self.carried(change)
        self.assertEqual(r["objects"][NS + "/req/ism-principle-gov-01"]["facets"][COMPAT]["props"], [other, foreign])
        members = [m["ref"] for m in r["objects"][NS + "/set/baseline/class-nc"]["members"]]
        self.assertEqual(members.count(NS + "/req/ism-principle-gov-01"), 1, "a name in another namespace is another meaning: no second entry")

    def test_backlog_41_a_control_nested_in_a_control_is_a_requirement_of_its_own(self):
        def change(doc):
            controls(doc)[0]["controls"] = [{"id": "ism-0001.1", "class": "ISM-control", "title": "Nested",
                                             "parts": [{"id": "ism-0001.1_smt", "name": "statement", "prose": "Nested too."}]}]
        r = self.carried(change)
        nested = r["objects"][NS + "/req/ism-0001.1"]
        self.assertEqual(nested["facets"][COMPAT], {"nested-in": "ism-0001"})
        refs = [m["ref"] for m in r["objects"][NS + "/set/tax/guidelines-governance-roles"]["members"]]
        self.assertEqual(refs, [NS + "/req/ism-0001", NS + "/req/ism-0001.1", NS + "/req/ism-principle-gov-01"])
        self.assertEqual(r["report"]["nested-controls"], 1)

    # ---- a source the converter would lose a value of: the run ends with 1 and says which ----
    def lost(self, change, word):
        doc = catalogue(); change(doc)
        r = self.convert(doc)
        self.assertEqual(r["done"].returncode, 1, r["done"].stdout[-300:])
        self.assertIn(word, r["done"].stderr)
        self.assertIn("convert_ism.py", r["done"].stderr.strip().splitlines()[-1])
        self.assertIsNotNone(r["report"], "the reports are written before the run ends")
        return r

    def test_backlog_41_a_second_label_would_overwrite_the_first_and_the_run_ends_with_1(self):
        def change(doc): controls(doc)[1]["props"].insert(1, {"name": "label", "value": "GOV-01-OLD"})
        r = self.lost(change, "2 source value(s) unaccounted")
        self.assertEqual([(u["path"], u["pointers"]) for u in r["ledger"]["unaccounted-paths"]],
                         [(f"{C}.props[].name", ["ism#/catalog/groups/1/groups/0/groups/0/controls/1/props/1/name"]),
                          (f"{C}.props[].value", ["ism#/catalog/groups/1/groups/0/groups/0/controls/1/props/1/value"])])
        self.assertEqual(r["ledger"]["verification-failures"], [], "the value is lost; no claim about it was false")

    def test_backlog_41_a_second_part_is_not_read_and_the_run_ends_with_1(self):
        def change(doc): controls(doc)[0]["parts"].append({"id": "ism-0001_gdn", "name": "guidance", "prose": "Not read."})
        r = self.lost(change, "3 source value(s) unaccounted")
        self.assertEqual(self.count(r, f"{C}.parts[].prose", "unaccounted"), 1)

    def test_backlog_41_a_part_that_is_no_statement_is_a_claim_that_does_not_hold(self):
        def change(doc): controls(doc)[0]["parts"][0]["name"] = "guidance"
        r = self.lost(change, "1 claim(s) that do not hold")
        self.assertEqual([(f["source"], f["claim"]) for f in r["ledger"]["verification-failures"]],
                         [("ism#/catalog/groups/1/groups/0/groups/0/controls/0/parts/0/name", "selector")])

    def test_backlog_41_a_sort_id_that_is_not_its_place_is_not_rebuilt(self):
        def change(doc): controls(doc)[0]["props"][0]["value"] = "catalog[1].group[2].group[1].group[1].control[7]"
        r = self.lost(change, "1 claim(s) that do not hold")
        self.assertEqual([(f["source"], f["claim"]) for f in r["ledger"]["verification-failures"]],
                         [("ism#/catalog/groups/1/groups/0/groups/0/controls/0/props/0/value", "rebuilt-id")])
        self.assertEqual(r["ledger"]["totals"]["unaccounted"], 2, "the sort-id, and the name that selects it")

    def test_backlog_41_a_link_that_names_no_resource_of_the_bundle_ends_the_run(self):
        def change(doc): doc["catalog"]["groups"][0]["groups"][0]["parts"][0]["prose"] += " And [another](#99999999-2222-4333-8444-555555555555)."
        r = self.lost(change, "1 link(s) `(#uuid)` in a text of the bundle name no resource the bundle holds")
        self.assertEqual(r["ledger"]["totals"]["unaccounted"], 0, "no value is lost: the source itself names what it does not hold")

    # ---- a converter broken in one place: the run ends with 1 ----
    def broken(self, changes, word, source=None, before=None):
        r = self.convert(source or catalogue(), changes, before)
        self.assertEqual(r["done"].returncode, 1, r["done"].stdout[-300:] + r["done"].stderr[-300:])
        self.assertIn(word, r["done"].stderr)
        return r

    def test_backlog_41_a_value_that_is_no_longer_written_ends_the_run(self):
        # the props the kernel has no member for are not put on the Requirement
        r = self.broken([('    if kept: compat["props"] = kept\n    if parent is not None', '    if parent is not None')],
                        "6 source value(s) unaccounted")
        self.assertEqual({u["path"].rsplit(".", 1)[1]: u["count"] for u in r["ledger"]["unaccounted-paths"]}, {"name": 2, "ns": 2, "value": 2})
        # the resources of the back-matter are not written: three values are lost, and the link in the text names nothing
        r = self.broken([('if resources: root_facets[F_REF] = {"resources": resources}\n', '')], "3 source value(s) unaccounted")
        self.assertIn("1 link(s) `(#uuid)` in a text of the bundle name no resource the bundle holds", r["done"].stderr)
        # the Set of the chapter that holds no control is not written. Its title is still a part of the id of the Set
        # below it, so the ledger calls it transformed and nothing is unaccounted; the path map says the title is
        # written as it is, and that is what ends the run
        r = self.broken([('    objects[rel] = s\n', '    if g.get("title") != "Front matter": objects[rel] = s\n')],
                        "the path map calls catalog.groups[].title L1, and the ledger found 1 value(s) transformed")
        self.assertEqual(r["ledger"]["totals"]["unaccounted"], 0)
        self.assertIn("sort-id(s) are not what a reader rebuilds from the written bundle", r["done"].stderr)

    def test_backlog_41_a_rule_that_does_not_give_the_id_ends_the_run(self):
        # the rule of the sort-id counts from 0: it gives none of the seven
        r = self.broken([('def _sort_id(parent, kind, pos, n): return f"{parent}.{kind}[{pos:0{len(str(n))}d}]"',
                          'def _sort_id(parent, kind, pos, n): return f"{parent}.{kind}[{pos - 1:0{len(str(n))}d}]"')],
                        "7 claim(s) that do not hold")
        self.assertEqual({f["claim"] for f in r["ledger"]["verification-failures"]}, {"rebuilt-id"})
        self.assertEqual(r["ledger"]["totals"]["unaccounted"], 14, "seven sort-ids and the seven names that select them")
        # the label of one Requirement is changed on disk after it is written and before the accounting
        r = self.broken([('w("content-manifest.json", manifest)\n',
                          'w("content-manifest.json", manifest)\n'
                          '_o = json.load(open(os.path.join(OUT, "objects/req-ism-0001.json"), encoding="utf-8"))\n'
                          '_o["label"] = "ISM-9999"; w("objects/req-ism-0001.json", _o)\n')], "1 claim(s) that do not hold")
        self.assertEqual([(f["pointer"], f["rule"][:10]) for f in r["ledger"]["verification-failures"]], [("/label", "label from")])

    def test_backlog_41_a_name_that_selects_a_value_which_is_not_written_ends_the_run(self):
        # the value of the `label` prop is read and not written; its name selects nothing
        r = self.broken([('            label = p["value"]; label_from_prop += 1\n', '            label_from_prop += 1\n')],
                        "2 source value(s) unaccounted")
        self.assertEqual([u["path"] for u in r["ledger"]["unaccounted-paths"]], [f"{C}.props[].name", f"{C}.props[].value"])
        self.assertEqual(r["objects"][NS + "/req/ism-principle-gov-01"]["label"], "ism-principle-gov-01", "the label is made from the id instead")

    def test_backlog_41_a_drop_nobody_listed_ends_the_run(self):
        # a date of the document is left out of the metadata and declared dropped where the declaration is made
        r = self.broken([('if k not in ("title", "version")}', 'if k not in ("title", "version", "published")}'),
                         ('for _pattern, _reason, _ in DECLARED_DROPS:\n', 'led.drop(r"\\.metadata\\.published$", "bookkeeping")\n'
                                                                           'for _pattern, _reason, _ in DECLARED_DROPS:\n')],
                        "1 value(s) are dropped by a declaration that is not in the table of declared drops")
        self.assertEqual(r["ledger"]["totals"]["unaccounted"], 0, "without the check the run would end with 0")

    def test_backlog_41_a_path_map_that_says_something_else_than_the_ledger_found_ends_the_run(self):
        r = self.broken([('(C + r"\\.title$", "L1", "Requirement title")', '(C + r"\\.title$", "not-content", "Requirement title")')],
                        "the path map calls catalog.groups[].groups[].groups[].controls[].title not-content, and the ledger found 2 value(s) copied")
        # and a row that says "written as it is" of a value that only a rule carries
        r = self.broken([('(C + r"\\.class$", "L1 by rule",', '(C + r"\\.class$", "L1",')],
                        "the path map calls catalog.groups[].groups[].groups[].controls[].class L1, and the ledger found 2 value(s) transformed")

    def test_backlog_41_a_record_on_disk_that_is_not_the_record_of_the_run_ends_the_run(self):
        not_written = ('with open(os.path.join(OUTDIR, LEDGER_FILE), "w", encoding="utf-8") as f:',
                       'with open(os.devnull, "w", encoding="utf-8") as f:')
        self.broken([not_written], "ism-conversion-ledger.json was not written")
        # the record of another run lies in the folder, as a committed one does in a checkout
        def seed(out):
            os.makedirs(out)
            shutil.copy(os.path.join(self.plain["out"], "ism-conversion-ledger.json"), out)
        doc = catalogue(); controls(doc)[1]["props"].append({"name": "note", "value": "another source"})
        self.broken([not_written], "ism-conversion-ledger.json on disk is not the record of this run", source=doc, before=seed)
        self.assertEqual(self.convert(catalogue(), [not_written], before=seed)["done"].returncode, 0,
                         "the same record, left by an equal run, is the record of this run")


if __name__ == "__main__":
    unittest.main()
