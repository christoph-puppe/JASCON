#!/usr/bin/env python3
"""The conversion ledger of convert_nist.py (backlog #41, phase E), held on
an invented catalogue.

    python3 jascon/scripts/test_convert_nist_ledger.py

The converter runs when it is imported and reads its sources from a fixed
place, and the repository carries no source. So it is copied, with the
library, into a folder of its own beside five files nobody published: one
small catalogue written below, in the shapes SP 800-53 uses, and four
profiles that select from it. What the real catalogue gives is held by the
Validators workflow, which converts it again from its pinned source and
compares every byte of the folder, the ledger's record among them.

Held here:
  - every source value has one outcome and the outcomes add up;
  - each transformation is a named rule, each kind of value goes where the
    record says, and what the converter does not carry is unaccounted
    unless one of the two grounds for a drop applies;
  - an unaccounted value does not fail the run; a destination that does not
    hold what the script says it wrote does, with exit code 1;
  - so does what the ledger's own checks cannot see, each put into a copy of
    the converter on purpose: a drop that reaches further than it names or
    stands beside carried values, a drop on neither ground, a record that
    was not written; and a value lost from a withdrawn control is
    unaccounted, not dropped with the tombstone.

Standard library only."""
import collections, json, os, re, shutil, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
RMF = "http://csrc.nist.gov/ns/rmf"
PROFILES = ("LOW", "MODERATE", "HIGH", "PRIVACY")
LEDGER = "sp800-53-conversion-ledger.json"
GROUNDS = ("path map: ", "as decided for IFA on 2026-11-13: ")


def labels(plain, padded):
    return [{"name": "label", "class": "zero-padded", "value": padded}, {"name": "label", "value": plain},
            {"name": "label", "class": "sp800-53a", "value": padded}]

def invented_catalogue():
    """Three live controls, one of them an enhancement, and three withdrawn
    ones: one merged into a statement, one moved to a control, one that
    names no successor."""
    c11 = {"id": "c-1.1", "class": "SP800-53-enhancement", "title": "First, enhanced",
           "props": labels("C-1(1)", "C-01(01)") + [{"name": "sort-id", "value": "c-01.01"},
                                                     {"name": "implementation-level", "ns": RMF, "value": "system"}],
           "links": [{"href": "#c-1", "rel": "required"}],
           "params": [{"id": "cx-01.01_odp", "label": "interval",
                       "props": [{"name": "label", "class": "sp800-53a", "value": "CX-01(01)_ODP"}]}],
           "parts": [{"id": "c-1.1_smt", "name": "statement", "prose": "Do it every {{ insert: param, cx-01.01_odp }}."}]}
    c1 = {"id": "c-1", "class": "SP800-53", "title": "First",
          "props": labels("C-1", "C-01") + [{"name": "sort-id", "value": "c-01"},
                                             {"name": "implementation-level", "ns": RMF, "value": "organization"},
                                             {"name": "implementation-level", "ns": RMF, "value": "system"},
                                             {"name": "contributes-to-assurance", "ns": RMF, "value": "true"}],
          "links": [{"href": "#00000000-0000-4000-8000-00000000000a", "rel": "reference"},
                    {"href": "#c-2", "rel": "related"}, {"href": "#w-2", "rel": "related"}],
          "params": [{"id": "cx-01_odp", "label": "who decides",
                      "props": [{"name": "label", "class": "sp800-53a", "value": "CX-01_ODP"},
                                {"name": "alt-identifier", "value": "c-1_prm_1"}],
                      "select": {"how-many": "one-or-more", "choice": ["the owner", "the operator"]},
                      "guidelines": [{"prose": "who decides is selected"}]}],
          "parts": [
              {"id": "c-1_smt", "name": "statement", "parts": [
                  {"id": "c-1_smt.a", "name": "item", "props": [{"name": "label", "value": "a."}],
                   "prose": "Name {{ insert: param, cx-01_odp }}; and"},
                  {"id": "c-1_smt.b", "name": "item", "props": [{"name": "label", "value": "b."}],
                   "prose": "Write it down."}]},
              {"id": "c-1_gdn", "name": "guidance",
               "prose": "See [the paper](#00000000-0000-4000-8000-00000000000a) and [C-02](#c-2)."},
              {"id": "c-1_obj", "name": "assessment-objective", "props": [{"name": "label", "class": "sp800-53a", "value": "C-01"}],
               "parts": [{"id": "c-1_obj.a", "name": "assessment-objective",
                          "props": [{"name": "label", "class": "sp800-53a", "value": "C-01a."}],
                          "prose": "somebody is named;", "links": [{"href": "#c-1_smt.a", "rel": "assessment-for"}]}]},
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
             "props": labels(plain, padded) + [{"name": "sort-id", "value": cid}, {"name": "status", "value": "withdrawn"}]}
        if links: w["links"] = list(links)
        if parts: w["parts"] = list(parts)
        return w
    return {"catalog": {
        "uuid": "00000000-0000-4000-8000-000000000001",
        "metadata": {"title": "An invented catalogue", "last-modified": "2026-11-14T00:00:00Z", "version": "1.0",
                     "oscal-version": "1.2.2",
                     "revisions": [{"title": "An earlier one", "version": "0.9"}],
                     "props": [{"name": "keywords", "value": "invented"}],
                     "links": [{"href": "#00000000-0000-4000-8000-00000000000b", "rel": "alternate"}],
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
            {"uuid": "00000000-0000-4000-8000-00000000000a", "title": "The paper", "citation": {"text": "Nobody, The paper."},
             "rlinks": [{"href": "https://paper.example/1"}]},
            {"uuid": "00000000-0000-4000-8000-00000000000b", "title": "The catalogue as a document",
             "rlinks": [{"href": "https://paper.example/catalogue.pdf", "media-type": "application/pdf"}]}]}}}

def invented_profile(name):
    return {"profile": {
        "uuid": "00000000-0000-4000-8000-000000000002",
        "metadata": {"title": f"An invented baseline, {name}", "last-modified": "2026-11-14T00:00:00Z", "version": "1.0",
                     "oscal-version": "1.2.2", "roles": [{"id": "publisher", "title": "Publisher"}]},
        "imports": [{"href": "#00000000-0000-4000-8000-00000000000c", "include-controls": [{"with-ids": ["c-1", "c-2"]}]}],
        "merge": {"as-is": True},
        "back-matter": {"resources": [{"uuid": "00000000-0000-4000-8000-00000000000c", "description": "the catalogue",
                                        "rlinks": [{"href": "catalogue.json", "media-type": "application/oscal.catalog+json"}]}]}}}


def norm(path):
    """nested controls and parts under one path, as the converter's path map counts them"""
    return re.sub(r"(\.parts\[\])+", ".parts[]", re.sub(r"(\.controls\[\])+", ".controls[]", path))


class Backlog41TheLedgerOfSP80053(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="jascon-nist-ledger-")
        cls.scripts = os.path.join(cls.tmp, "jascon", "scripts")
        os.makedirs(cls.scripts)
        for fn in ("convert_nist.py", "oscal_conv_lib.py"): shutil.copy(os.path.join(HERE, fn), cls.scripts)
        os.makedirs(os.path.join(cls.tmp, "sources", "nist"))
        def write(name, doc):
            with open(os.path.join(cls.tmp, "sources", "nist", name), "w", encoding="utf-8") as f: json.dump(doc, f)
        write("NIST_SP-800-53_rev5_catalog.json", invented_catalogue())
        for b in PROFILES: write(f"NIST_SP-800-53_rev5_{b}-baseline_profile.json", invented_profile(b))
        cls.done, cls.out = cls.run_converter("convert_nist.py", "as-it-is")
        with open(os.path.join(cls.out, LEDGER), encoding="utf-8") as f: cls.record = json.load(f)
        cls.rows = collections.Counter()
        for r in cls.record["paths"]: cls.rows[(norm(r["path"]), r["outcome"])] += r["count"]

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    @classmethod
    def run_converter(cls, script, name):
        out = os.path.join(cls.tmp, "out", name)
        done = subprocess.run([sys.executable, os.path.join(cls.scripts, script), "--out", out], capture_output=True, text=True)
        return done, out

    def outcomes(self, path):
        """-> {outcome: count} of the source values under one path of the catalogue"""
        return {o: n for (p, o), n in self.rows.items() if p == "nist.catalog." + path}

    def rules(self):
        """-> {rule: destinations} over the whole record"""
        seen = collections.Counter()
        for r in self.record["paths"]:
            for d in r.get("to", []):
                if "rule" in d: seen[d["rule"]] += d["count"]
        return seen

    def test_backlog_41_every_source_value_has_one_outcome_and_the_run_ends_with_0(self):
        self.assertEqual(self.done.returncode, 0, self.done.stderr[-600:])
        t = self.record["totals"]
        self.assertEqual(sum(t.values()), self.record["leaf-values"])
        self.assertEqual(sum(r["count"] for r in self.record["paths"]), self.record["leaf-values"])
        self.assertEqual(self.record["verification-failures"], [])
        self.assertGreater(t["unaccounted"], 0, "an unaccounted value is reported and does not fail the run")
        self.assertIn(f"unaccounted {t['unaccounted']}", self.done.stdout)
        with open(os.path.join(self.out, "sp800-53-coverage-report.json"), encoding="utf-8") as f: report = json.load(f)
        self.assertEqual(report["ledger"]["totals"], t, "the report and the record are of one run")
        self.assertEqual(sum(c["count"] for c in report["ledger"]["unaccounted-classes"]), t["unaccounted"])

    def test_backlog_41_a_drop_rests_on_one_of_two_grounds(self):
        reasons = collections.Counter()
        for r in self.record["paths"]:
            for w in r.get("reasons", []): reasons[w["reason"]] += w["count"]
        self.assertEqual(sum(reasons.values()), self.record["totals"]["intentionally-dropped"])
        for reason in reasons:
            self.assertTrue(reason.startswith(GROUNDS), reason)
        self.assertEqual({g: sum(n for r, n in reasons.items() if r.startswith(g)) > 0 for g in GROUNDS}, dict.fromkeys(GROUNDS, True))

    def test_backlog_41_what_is_copied_and_what_a_named_rule_made(self):
        o = self.outcomes
        self.assertEqual(o("groups[].controls[].title"), {"copied": 5, "unaccounted": 1})           # 3 live, 2 on a successor; w-3 nowhere
        self.assertEqual(o("groups[].controls[].id"), {"transformed": 5, "unaccounted": 1})
        self.assertEqual(o("groups[].controls[].params[].id"), {"copied": 2})
        self.assertEqual(o("groups[].controls[].params[].select.choice[]"), {"copied": 2})
        self.assertEqual(o("groups[].controls[].params[].select.how-many"), {"transformed": 1})
        self.assertEqual(o("back-matter.resources[].title"), {"copied": 2})
        self.assertEqual(o("back-matter.resources[].uuid"), {"transformed": 1, "intentionally-dropped": 1})   # one a link names, one no link names
        # prose: an insertion (item a, the enhancement), a markdown link (the guidance of c-1) or two paragraphs (the
        # assessment objects) make it a transformation; item b, the objective and both parts of c-2 are copies
        self.assertEqual(o("groups[].controls[].parts[].prose"), {"copied": 4, "transformed": 4, "unaccounted": 1})
        self.assertEqual(o("groups[].controls[].links[].rel"), {"copied": 3, "transformed": 2, "unaccounted": 1})
        self.assertEqual(o("groups[].controls[].links[].href"), {"transformed": 5, "unaccounted": 1})
        rules = self.rules()
        for rule, destinations in (
                ("requirement URI from the control id", 3 * 3 + 4 * 2),      # id, manifest, family Set; two members in each of four baselines
                ("requirement URI from the control a link names", 2),        # required, related
                ("a reference link resolved by uuid: the first link of the back-matter resource it names", 3),   # three inputs, one relation
                ("statement id without the control prefix", 4 * 2),          # four statements; the part id and the control id
                ("obligated party URI from the implementation level", 2 + 2 + 1 + 1),   # c-1: two levels on two statements
                ("parameter cardinality `many` from the selection's how-many `one-or-more`", 1),
                ("lineage inverted: the URI of a withdrawn control, written on the successor its link names", 2 * 2 * 3),
                ("lineage mode from the link's rel (incorporated-into -> merged-into, moved-to -> renamed)", 2 * 2),
                ("the statement a lineage link names, as a statement id", 1),
                ("family Set URI from the group id", 3),
                ("member sequence: ten times the control's place in its family, ordered by sort-id", 3)):
            self.assertEqual(rules[rule], destinations, rule)
        self.assertEqual(sum(n for r, n in rules.items() if r.startswith("assessment objects: one entry per paragraph")), 2)
        self.assertEqual(sum(n for r, n in rules.items() if "parameter insertion" in r), 2)
        self.assertEqual(sum(n for r, n in rules.items() if "markdown link" in r and "assessment objects" not in r), 1)

    def test_backlog_41_what_is_not_carried_is_unaccounted_unless_a_ground_applies(self):
        o = self.outcomes
        # not carried and not decided
        self.assertEqual(o("groups[].controls[].parts[].links[].href"), {"unaccounted": 1})            # assessment-for
        self.assertEqual(o("groups[].controls[].parts[].links[].rel"), {"unaccounted": 1})
        self.assertEqual(o("groups[].controls[].parts[].id"),                                          # objectives copied, statements cut;
                         {"copied": 2, "transformed": 4, "unaccounted": 5})                            # guidance x2, method, container, w-3's
        self.assertEqual(o("metadata.last-modified"), {"unaccounted": 1})
        self.assertEqual(o("metadata.links[].href"), {"unaccounted": 1})
        self.assertEqual(o("metadata.responsible-parties[].role-id"), {"unaccounted": 1})
        self.assertEqual(o("groups[].parts[].title"), {"unaccounted": 1})
        # a selector is nobody's decision yet; of a withdrawn control it goes with the tombstone
        self.assertEqual(o("groups[].controls[].props[].ns"), {"unaccounted": 5})
        self.assertEqual(o("groups[].controls[].props[].name"), {"unaccounted": 17 + 5, "intentionally-dropped": 2 * 5})
        # carried as a boolean, which the ledger cannot follow; a formal label the rule does not give
        values = o("groups[].controls[].props[].value")
        self.assertEqual(values["unaccounted"], 1 + 5, "contributes-to-assurance, and the five props of w-3")
        self.assertEqual(o("groups[].controls[].params[].props[].value"), {"copied": 1, "intentionally-dropped": 1, "unaccounted": 1})
        # the two grounds
        self.assertEqual(o("groups[].controls[].class"), {"intentionally-dropped": 5, "unaccounted": 1})
        self.assertEqual(o("groups[].controls[].parts[].name"), {"intentionally-dropped": 11, "unaccounted": 1})
        self.assertEqual(o("groups[].class"), {"intentionally-dropped": 1})
        self.assertEqual(o("metadata.revisions[].title"), {"intentionally-dropped": 1})
        self.assertEqual(o("metadata.parties[].name"), {"intentionally-dropped": 1})
        self.assertEqual(o("uuid"), {"intentionally-dropped": 1})
        self.assertEqual(o("back-matter.resources[].rlinks[].media-type"), {"intentionally-dropped": 1})
        self.assertEqual({o: n for (p, o), n in self.rows.items() if p == "low.profile.merge.as-is"}, {"intentionally-dropped": 1})
        # a withdrawn control that names no successor: nothing of it is declared, nothing is in the bundle
        with open(os.path.join(self.out, "sp800-53-coverage-report.json"), encoding="utf-8") as f: report = json.load(f)
        self.assertEqual(report["withdrawn-without-successor"], ["w-3"])
        by_class = {c["class"]: c for c in report["ledger"]["unaccounted-classes"]}
        self.assertEqual(by_class["withdrawn-without-successor"]["count"], 18)
        self.assertEqual(by_class["related-to-withdrawn"]["count"], 2)
        self.assertEqual(by_class["assessment-for"]["count"], 2)
        self.assertEqual(by_class["boolean"]["count"], 1)
        self.assertEqual(by_class["formal-odp-label"]["count"], 1)
        self.assertNotIn("other", by_class, "a value in no class")

    def run_changed(self, name, *changes):
        """-> (the finished process, its --out) of a copy of the converter in which each `old` reads `new`"""
        with open(os.path.join(self.scripts, "convert_nist.py"), encoding="utf-8") as f: code = f.read()
        for old, new in zip(changes[0::2], changes[1::2]):
            self.assertEqual(code.count(old), 1, f"{name}: the line the defect is put into")
            code = code.replace(old, new)
        with open(os.path.join(self.scripts, f"convert_nist_{name}.py"), "w", encoding="utf-8") as f: f.write(code)
        return self.run_converter(f"convert_nist_{name}.py", name)

    def test_backlog_41_a_destination_that_does_not_hold_what_was_written_ends_the_run_with_1(self):
        # one written file is changed between the writing and the accounting
        marker = "T_WRITTEN = time.time()\n"
        done, out = self.run_changed("tampered", marker, marker +
                                     '_p = os.path.join(bundle.out, "objects", "req", "c-2.json")\n'
                                     '_o = json.load(open(_p, encoding="utf-8")); _o["title"]["en"] = "Seconds"\n'
                                     'json.dump(_o, open(_p, "w", encoding="utf-8"))\n')
        self.assertEqual(done.returncode, 1, done.stdout[-300:] + done.stderr[-300:])
        self.assertIn("1 claim(s) of the conversion ledger do not hold on the written files, 0 wiring check(s) failed", done.stderr)
        self.assertIn("LEDGER CHECK FAILED", done.stderr)
        with open(os.path.join(out, LEDGER), encoding="utf-8") as f: record = json.load(f)
        self.assertEqual([x["source"] for x in record["verification-failures"]], ["nist#/catalog/groups/0/controls/1/title"])

    def test_backlog_41_a_drop_that_reaches_too_far_or_a_record_of_another_run_ends_the_run_with_1(self):
        """What the ledger's own checks cannot see. Each of these passed with
        exit code 0 before the converter checked its wiring."""
        for name, old, new, word in (
                # every prop name, class and namespace declared by its path: on that path a withdrawn control's are dropped
                # value by value and a live control's are nobody's decision yet
                ("too-wide", ' (r"\\.metadata\\.revisions\\[\\]\\.", B_REVISIONS),\n',
                 ' (r"\\.metadata\\.revisions\\[\\]\\.", B_REVISIONS),\n (r"\\.props\\[\\]\\.(name|class|ns)$", B_REVISIONS),\n',
                 "a drop reaches further than it names"),
                # a path on which other values are carried: the title of w-3, which is in no object, would read as dropped
                ("beside-carried", ' (r"^(nist\\.catalog|[a-z]+\\.profile)\\.uuid$", B_UUID),\n',
                 ' (r"^(nist\\.catalog|[a-z]+\\.profile)\\.uuid$|\\.controls\\[\\]\\.title$", B_UUID),\n',
                 "on which other values are carried"),
                ("neither-ground", ' (r"\\.metadata\\.revisions\\[\\]\\.", B_REVISIONS),\n',
                 ' (r"\\.metadata\\.revisions\\[\\]\\.", "not needed"),\n', "on neither of the two grounds"),
                ("not-written", "    json.dump(RECORD, f, indent=1, ensure_ascii=False); f.write(\"\\n\")\n", "    pass\n",
                 f"{LEDGER} on disk is not the record of this run")):
            done, _ = self.run_changed(name, old, new)
            self.assertEqual(done.returncode, 1, f"{name}: {done.stdout[-200:]}{done.stderr[-300:]}")
            self.assertIn("LEDGER WIRING", done.stderr, name)
            self.assertIn(word, done.stderr, name)
            self.assertIn("0 claim(s) of the conversion ledger do not hold on the written files", done.stderr, name)

    TITLE_LOST = ('             "title": c.get("title", "")}\n', '             "title": ""}\n')
    WHOLE_TOMBSTONE = ("        led.drop_value(c.get(\"class\"), A_TOMBSTONE)\n",
                       "        led.drop_value({k: v for k, v in c.items() if k != \"controls\"}, A_TOMBSTONE)\n")

    def test_backlog_41_a_value_lost_from_a_tombstone_is_unaccounted_and_not_dropped_with_it(self):
        # the annotation loses the title of the withdrawn control: no declaration covers a title, so it is unaccounted
        done, out = self.run_changed("title-lost", *self.TITLE_LOST)
        self.assertEqual(done.returncode, 0, done.stderr[-300:])
        with open(os.path.join(out, LEDGER), encoding="utf-8") as f: record = json.load(f)
        titles = collections.Counter()
        for r in record["paths"]:
            if norm(r["path"]) == "nist.catalog.groups[].controls[].title": titles[r["outcome"]] += r["count"]
        self.assertEqual(titles, {"copied": 3, "unaccounted": 3}, "the titles of w-1 and w-2 are lost, and say so")
        # declared for the whole control, the drop would cover the lost titles; the run refuses a drop that reaches that far
        done, _ = self.run_changed("title-lost-under-a-whole-tombstone", *self.TITLE_LOST, *self.WHOLE_TOMBSTONE)
        self.assertEqual(done.returncode, 1, done.stdout[-200:] + done.stderr[-300:])
        self.assertIn("a drop reaches further than it names: nist.catalog.groups[].controls[].title", done.stderr)


if __name__ == "__main__":
    unittest.main()
