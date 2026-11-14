#!/usr/bin/env python3
"""The IFA converter ends its run with 1 when a source value is unaccounted.

    python3 jascon/scripts/test_convert_ifa_ledger.py

The author's rule of 2026-11-14: "Real content is never dropped. [...] What
may stay out of a bundle is only what is not content: a name that merely
selects a field, a namespace, an id that is rebuilt exactly from another
value. Each such class needs a stated rule that the ledger checks, not an
'unaccounted' line. [...] a converter run with an unaccounted value exits
non-zero."

Each test changes one place of a copy of the converter, runs the copy on
the pinned sources into a scratch folder and reads the exit code and the
ledger record the run wrote. The copies stand in a mirror of the
repository, so the converter under test finds the sources and the
SP 800-53 bundle where it looks for them. Needs the pinned NIST sources
in sources/nist (.github/scripts/fetch-pinned-sources.sh); without them
the tests are skipped and say so. Standard library only."""
import json, os, shutil, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
SOURCES = os.path.join(ROOT, "sources", "nist")
SELECTOR = '''            if p.get("name") == "type":
                led.selector('''


@unittest.skipUnless(os.path.isdir(SOURCES), "the pinned NIST sources are not in sources/nist")
class PhaseETheIfaGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.baseline = cls.run_converter("baseline")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    @classmethod
    def run_converter(cls, name, old=None, new=None):
        """-> (exit code, stderr, the totals of the ledger record the run wrote)"""
        mirror = os.path.join(cls.tmp, name)
        os.makedirs(os.path.join(mirror, "jascon"))
        for entry in os.listdir(ROOT):                      # everything but the scripts is the repository's own
            if entry not in (".git", "jascon"): os.symlink(os.path.join(ROOT, entry), os.path.join(mirror, entry))
        for entry in os.listdir(os.path.join(ROOT, "jascon")):
            if entry != "scripts": os.symlink(os.path.join(ROOT, "jascon", entry), os.path.join(mirror, "jascon", entry))
        scripts = os.path.join(mirror, "jascon", "scripts")
        shutil.copytree(HERE, scripts, ignore=shutil.ignore_patterns("__pycache__"))
        if old is not None:
            path = os.path.join(scripts, "convert_ifa.py")
            with open(path, encoding="utf-8") as f: text = f.read()
            assert text.count(old) == 1, f"{name}: the place to change occurs {text.count(old)} times"
            with open(path, "w", encoding="utf-8") as f: f.write(text.replace(old, new))
        out = os.path.join(mirror, "out")
        done = subprocess.run([sys.executable, os.path.join(scripts, "convert_ifa.py"), "--out", out],
                              capture_output=True, text=True)
        with open(os.path.join(out, "ifa-conversion-ledger.json"), encoding="utf-8") as f: record = json.load(f)
        return done.returncode, done.stderr, record

    def test_the_run_as_it_is_ends_with_0_and_nothing_is_unaccounted(self):
        code, err, record = self.baseline
        self.assertEqual(code, 0, err)
        self.assertEqual((record["totals"]["unaccounted"], record["verification-failures"]), (0, []))
        self.assertEqual(sum(record["totals"].values()), record["leaf-values"])
        self.assertEqual(sorted(record["totals"]), ["copied", "intentionally-dropped", "not-content", "transformed", "unaccounted"])

    def test_the_prop_name_is_no_content_by_a_rule_and_not_by_a_declared_drop(self):
        record = self.baseline[2]
        names = [e for e in record["entries"] if e["path"].endswith(".risks[].remediations[].props[].name")]
        self.assertEqual([(e["outcome"], e["kind"]) for e in names], [("not-content", "selector")] * 2)
        self.assertEqual(record["totals"]["not-content"], 2)

    def test_a_name_without_its_rule_is_unaccounted_and_ends_the_run(self):
        code, err, record = self.run_converter("no-rule", SELECTOR, SELECTOR.replace('if p.get("name") == "type":', "if False:"))
        self.assertEqual(code, 1)
        self.assertIn("0 claim(s) that do not hold and 2 source value(s) unaccounted", err)
        self.assertEqual(record["totals"]["unaccounted"], 2, "the record is written before the run ends")

    def test_a_rule_that_does_not_hold_ends_the_run(self):
        code, err, record = self.run_converter("wrong-rule", 'p["value"], among=("type",))', 'p["value"], among=("kind",))')
        self.assertEqual(code, 1)
        self.assertIn("2 claim(s) that do not hold", err)
        self.assertEqual([f["claim"] for f in record["verification-failures"]], ["selector", "selector"])

    def test_a_value_that_is_not_written_takes_its_name_with_it(self):
        code, err, record = self.run_converter(
            "lost-value",
            '"responses": [{"type": next((p.get("value") for p in rm.get("props", []) or [] if p.get("name") == "type"), None),',
            '"responses": [{"type": None,')
        self.assertEqual(code, 1)
        self.assertEqual(record["totals"]["unaccounted"], 4, "two values, and the two names that select them")
        self.assertEqual(record["totals"]["copied"], self.baseline[2]["totals"]["copied"] - 2)

    def test_a_value_whose_declared_reason_is_taken_away_ends_the_run(self):
        code, err, record = self.run_converter(
            "no-reason",
            r'''led.drop(r"(\.subjects\[\]\.type|\.assessment-subjects\[\]\.type|\.actors\[\]\.type|\.target\.type|\.identifier-type)$",''',
            r'''led.drop(r"(\.subjects\[\]\.type-of-nothing)$",''')
        self.assertEqual(code, 1)
        self.assertEqual(record["totals"]["unaccounted"], 11)

    def test_without_the_gate_the_same_loss_ends_with_0(self):
        # what the gate is for: the converter of 2026-11-13 wrote the loss into its report and ended with 0
        mirror_change = ('ledger_gate(LEDGER, "convert_ifa.py")\n', "")
        code, err, record = self.run_converter("no-gate", *mirror_change)
        self.assertEqual(code, 0)
        path = os.path.join(self.tmp, "no-gate", "jascon", "scripts", "convert_ifa.py")
        with open(path, encoding="utf-8") as f: text = f.read()
        with open(path, "w", encoding="utf-8") as f: f.write(text.replace('if p.get("name") == "type":', "if False:"))
        out = os.path.join(self.tmp, "no-gate", "out2")
        done = subprocess.run([sys.executable, path, "--out", out], capture_output=True, text=True)
        with open(os.path.join(out, "ifa-conversion-ledger.json"), encoding="utf-8") as f: record = json.load(f)
        self.assertEqual((done.returncode, record["totals"]["unaccounted"]), (0, 2))


if __name__ == "__main__":
    unittest.main()
