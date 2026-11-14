#!/usr/bin/env python3
"""Whom a converted statement binds (backlog #74): the nine catalogue
converters, run as the scripts they are on one invented catalogue.

    python3 jascon/scripts/test_convert_obligated_party.py

A converter runs when it is imported and reads its source from a fixed
place under the repository, and the repository carries no source. So each
converter is copied, with the library, into a folder of its own beside
files that stand in for its sources: one small catalogue nobody published,
written below. What a real source gives is held elsewhere - the Validators
workflow converts the shipped corpora again from their pinned sources and
compares every byte.

Held here, for each converter:
  - without --obligated-party every statement the source says nothing about
    carries the party the converter wrote on its own until 2026-11-14, and
    both coverage reports name it as the converter's default;
  - with it those statements carry the caller's party, and the reports say
    that the caller gave it and what the default would have been;
  - a party the source states (SP 800-53: a control's implementation level)
    is written as the source states it, with or without the argument;
  - --out is the only place a run writes to;
  - an argument the converter does not know, and a party that is no URI,
    stop the run before anything is written;
  - the header of the file names the two arguments.

Standard library only."""
import ast, collections, json, os, shutil, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
MINE = "https://acme.example/party/it-operations"
NIST = "https://ns.nist.gov/sp800-53/party/"
PROFILES = [f"nist/NIST_SP-800-53_rev5_{b}-baseline_profile.json" for b in ("LOW", "MODERATE", "HIGH", "PRIVACY")]

# converter -> (the party it wrote on its own until 2026-11-14, the files it reads under sources/, the stem of its reports)
CONVERTERS = {
    "convert_bsi.py": ("https://ns.bsi.bund.de/gspp/party/institution", ["Grundschutz++-catalog.json"], "bsi"),
    "convert_c3a.py": ("https://ns.bsi.bund.de/c3a/party/cloud-dienstanbieter", ["c3a_oscal_catalog.json"], "c3a"),
    "convert_c5.py": ("https://ns.bsi.bund.de/c5/party/cloud-service-provider", ["c5-2026-oscal-catalog.json"], "c5"),
    "convert_cis_benchmark.py": ("https://ns.cisecurity.org/benchmark/ubuntu-24.04-lts/party/system-administrator",
                                 ["CIS Ubuntu Linux 24.04 LTS Benchmark.json"], "cisb"),
    "convert_cis_controls.py": ("https://ns.cisecurity.org/controls/v8/party/enterprise", ["CIS Controls.json"], "cisc"),
    "convert_csf.py": ("https://ns.nist.gov/csf/party/organization", ["nist/NIST_CSF_v2.0_catalog.json"], "csf"),
    "convert_cyfun.py": ("https://ns.ccb.belgium.be/cyfun/party/organisation",
                         ["CyFun 2025 BASIC Resolved.json", "CyFun 2025 ESSENTIAL Resolved.json"], "cyfun"),
    "convert_ism.py": ("https://ns.cyber.gov.au/ism/party/organisation", ["ism.json"], "ism"),
    "convert_nist.py": (NIST + "organization", ["nist/NIST_SP-800-53_rev5_catalog.json"] + PROFILES, "sp800-53"),
}
# the three shipped bundles in which every statement carries the converter's own party
SHIPPED = {"convert_bsi.py": "DE.BSI/bsi-core-bundle", "convert_csf.py": "US.CSF/csf-core-bundle",
           "convert_ism.py": "AU.ISM/ism-core-bundle"}


def invented_catalogue():
    """Four controls in one group, two of them nested. `c-1` and `c-1.1`
    state an implementation level as SP 800-53 does; `c-1.2` and `c-2` state
    none. To the other eight converters the level is a prop they do not read."""
    def control(cid, levels=(), subs=()):
        c = {"id": cid, "class": "basic", "title": f"Title of {cid}",
             "props": [{"name": "label", "value": cid.upper()}]
                      + [{"name": "implementation-level", "ns": "http://csrc.nist.gov/ns/rmf", "value": v} for v in levels],
             "parts": [{"id": f"{cid}_smt", "name": "statement", "prose": f"Whoever is bound does what {cid} says."}]}
        if subs: c["controls"] = list(subs)
        return c
    return {"catalog": {
        "uuid": "00000000-0000-4000-8000-000000000001",
        "metadata": {"title": "An invented catalogue", "version": "1.0", "oscal-version": "1.1.3",
                     "last-modified": "2026-11-14T00:00:00Z", "published": "2026-11-14T00:00:00Z"},
        "groups": [{"id": "g1", "title": "Group one", "controls": [
            control("c-1", ["system"], [control("c-1.1", ["organization", "system"]), control("c-1.2")]),
            control("c-2")]}]}}

INVENTED_PROFILE = {"profile": {"uuid": "00000000-0000-4000-8000-000000000002",
                                "metadata": {"title": "An invented baseline", "version": "1.0"},
                                "imports": [{"href": "#catalogue", "include-controls": [{"with-ids": ["c-1", "c-2"]}]}]}}


def parties_of(out):
    """-> how often each list of obligated parties stands on a statement of the bundle under `out`."""
    seen = collections.Counter()
    for base, _, files in os.walk(out):
        if os.sep + "objects" not in base: continue
        for fn in files:
            if not fn.endswith(".json"): continue
            with open(os.path.join(base, fn), encoding="utf-8") as f: o = json.load(f)
            for s in o.get("statements") or []: seen[tuple(s["obligated-parties"])] += 1
    return seen


class Backlog74TheNineConverters(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="jascon-obligated-party-")
        scripts = os.path.join(cls.tmp, "jascon", "scripts")
        os.makedirs(scripts)
        for fn in list(CONVERTERS) + ["oscal_conv_lib.py"]: shutil.copy(os.path.join(HERE, fn), scripts)
        shutil.copytree(os.path.join(HERE, "..", "schemas", "stdlib"), os.path.join(cls.tmp, "jascon", "schemas", "stdlib"))
        for _, sources, _ in CONVERTERS.values():
            for rel in sources:
                p = os.path.join(cls.tmp, "sources", *rel.split("/"))
                os.makedirs(os.path.dirname(p), exist_ok=True)
                with open(p, "w", encoding="utf-8") as f:
                    json.dump(INVENTED_PROFILE if rel in PROFILES else invented_catalogue(), f)
        cls.ran = {}
        for conv in CONVERTERS:
            cls.ran[conv, "default"] = cls.run_converter(conv, "default")
            cls.ran[conv, "caller"] = cls.run_converter(conv, "caller", "--obligated-party", MINE)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    @classmethod
    def run_converter(cls, conv, name, *args):
        """-> (the finished process, the folder it was told to write to)"""
        out = os.path.join(cls.tmp, "out", conv, name)
        done = subprocess.run([sys.executable, os.path.join(cls.tmp, "jascon", "scripts", conv), "--out", out, *args],
                              capture_output=True, text=True)
        return done, out

    def reports(self, conv, out):
        stem = CONVERTERS[conv][2]
        with open(os.path.join(out, f"{stem}-coverage-report.json"), encoding="utf-8") as f: record = json.load(f)
        with open(os.path.join(out, f"{stem}-coverage-report.md"), encoding="utf-8") as f: text = f.read()
        lines = [l for l in text.splitlines() if l.startswith("- **Obligated part")]
        self.assertEqual(len(lines), 1, f"{conv}: one line of the report says whom the statements bind")
        self.assertNotIn("documented default", text, conv)
        return record, lines[0]

    def expected(self, conv, party):
        """what stands on the four statements: the source's level on two of them for SP 800-53, `party` elsewhere"""
        if conv != "convert_nist.py": return {(party,)}
        return {(NIST + "system",), (NIST + "organization", NIST + "system"), (party,)}

    def test_backlog_74_without_the_argument_the_converters_own_party_is_written_and_named_as_such(self):
        for conv, (default, _, _) in CONVERTERS.items():
            done, out = self.ran[conv, "default"]
            self.assertEqual(done.returncode, 0, f"{conv}: {done.stderr[-400:]}")
            seen = parties_of(out)
            self.assertEqual(set(seen), self.expected(conv, default), conv)
            if conv == "convert_nist.py": self.assertEqual(seen[(default,)], 2, "c-1.2 and c-2 state no level")
            record, line = self.reports(conv, out)
            self.assertEqual({k: record["obligated-party"].get(k) for k in ("value", "origin", "converter-default")},
                             {"value": default, "origin": "converter-default", "converter-default": default}, conv)
            self.assertIn(f"`{default}` on every statement", line, conv)
            self.assertIn("the converter's default and not a value of the source", line, conv)
            self.assertNotIn("given by the caller", line, conv)

    def test_backlog_74_the_callers_party_takes_the_place_of_the_default_and_no_other(self):
        for conv, (default, _, _) in CONVERTERS.items():
            done, out = self.ran[conv, "caller"]
            self.assertEqual(done.returncode, 0, f"{conv}: {done.stderr[-400:]}")
            seen = parties_of(out)
            self.assertEqual(set(seen), self.expected(conv, MINE), conv)                 # the default is written nowhere
            self.assertEqual(sum(seen.values()), sum(parties_of(self.ran[conv, "default"][1]).values()), conv)
            record, line = self.reports(conv, out)
            self.assertEqual({k: record["obligated-party"].get(k) for k in ("value", "origin", "converter-default")},
                             {"value": MINE, "origin": "caller", "converter-default": default}, conv)
            self.assertIn(f"`{MINE}` on every statement", line, conv)
            self.assertIn("given by the caller with `--obligated-party`", line, conv)
            self.assertIn(f"default is `{default}`", line, conv)
            self.assertNotIn("not a value of the source", line, conv)

    def test_backlog_74_a_party_the_source_states_is_the_sources_with_or_without_the_argument(self):
        for name, party in (("default", NIST + "organization"), ("caller", MINE)):
            done, out = self.ran["convert_nist.py", name]
            seen = parties_of(out)
            self.assertEqual(seen, {(NIST + "system",): 1, (NIST + "organization", NIST + "system"): 1, (party,): 2}, name)
            record, line = self.reports("convert_nist.py", out)
            self.assertEqual(record["obligated-party"]["source-states"], "as the implementation level of a control")
            self.assertEqual(record["obligated-party-use"]["controls"], {"source-states": 2, "not-stated": 2})
            self.assertEqual(record["obligated-party-use"]["statements"], {"source-states": 2, "not-stated": 2})
            self.assertIn("for which the source names no party; where it names one", line)
            self.assertIn("It gives none on x2 controls", line)

    def test_backlog_74_out_is_the_only_place_a_run_writes_to(self):
        for conv, (_, _, stem) in CONVERTERS.items():
            # a converter wired to the conversion ledger (backlog #41) writes its record beside the two reports,
            # as convert_ifa.py does; it is the one file a run may write besides the three
            ledger = f"{stem}-conversion-ledger.json"
            wrote = {name: sorted(os.listdir(self.ran[conv, name][1])) for name in ("default", "caller")}
            self.assertEqual(ledger in wrote["default"], ledger in wrote["caller"], f"{conv}: the ledger is written with one party and not the other")
            for name in ("default", "caller"):
                out = self.ran[conv, name][1]
                self.assertEqual([x for x in wrote[name] if x != ledger],
                                 [f"{stem}-core-bundle", f"{stem}-coverage-report.json", f"{stem}-coverage-report.md"], conv)
                self.assertTrue(os.path.isfile(os.path.join(out, f"{stem}-core-bundle", "content-manifest.json")), conv)
        self.assertEqual(sorted(os.listdir(self.tmp)), ["jascon", "out", "sources"],
                         "a converter told --out wrote into the corpus folder of the repository as well")

    def test_backlog_74_an_argument_nobody_reads_or_a_party_that_is_no_uri_stops_the_run_before_it_writes(self):
        for conv in CONVERTERS:
            for name, args, word in (("misspelled", ("--obligated-partie", MINE), "unknown argument '--obligated-partie'"),
                                     ("no-uri", ("--obligated-party", "organisation"), "not an http(s) URI"),
                                     ("twice", ("--obligated-party", MINE, "--obligated-party", MINE), "more than once")):
                done, out = self.run_converter(conv, name, *args)
                self.assertNotEqual(done.returncode, 0, f"{conv} {name}")
                self.assertIn(word, done.stderr, f"{conv} {name}")
                self.assertFalse(os.path.exists(out), f"{conv} {name}: something was written")

    def test_backlog_74_the_header_of_each_converter_names_the_two_arguments(self):
        for conv in CONVERTERS:
            with open(os.path.join(HERE, conv), encoding="utf-8") as f: header = ast.get_docstring(ast.parse(f.read())) or ""
            for word in ("--obligated-party URI", "--out DIR", "backlog #74"):
                self.assertIn(word, header, conv)

    def test_backlog_74_one_place_writes_the_party_and_no_converter_is_left_out(self):
        """Read, not run: the invented catalogue does not reach every branch
        of a converter, and a converter added later is in no table here."""
        # what each file mints under `{NS}/party/` besides its default: SP 800-53 writes the source's level (and
        # names the pattern in its report), the benchmark names CIS as the author of its Mappings
        beside_the_default = {"convert_nist.py": 2, "convert_cis_benchmark.py": 1}
        for conv in CONVERTERS:
            with open(os.path.join(HERE, conv), encoding="utf-8") as f: code = f.read().replace(" ", "")
            wrote = [l for l in code.splitlines() if '"obligated-parties":' in l]
            self.assertEqual(len(wrote), 1, f"{conv}: one place writes whom a statement binds")
            self.assertIn('"obligated-parties":parties' if conv == "convert_nist.py" else '"obligated-parties":[PARTY]', wrote[0], conv)
            self.assertEqual(code.count('f"{NS}/party/') + code.count("`{NS}/party/"), 1 + beside_the_default.get(conv, 0),
                             f"{conv}: a party is minted where the argument does not reach")
            self.assertIn("PARTY,PARTY_ORIGIN=obligated_party(ARGV,PARTY_DEFAULT)", code, conv)
            self.assertEqual(code.count("\nPARTY="), 0, f"{conv}: the party is what obligated_party() returned")
        with open(os.path.join(HERE, "convert_nist.py"), encoding="utf-8") as f: code = f.read().replace(" ", "")
        # the level, else the argument; since the conversion ledger (#41) the party of a level is a stated rule
        self.assertIn('iflvls:\nparties=[D(R_PARTY,_party,v)forvinlvls]\nelse:\nparties=[PARTY]', code)
        self.assertIn('def_party(level):returnf"{NS}/party/{level}"', code)
        self.assertEqual(code.count("\nparties="), 2)
        # convert_cr26.py writes parties too (`affects`, else its own); it takes the argument in a change of its own
        elsewhere = {"convert_cr26.py"}
        for fn in sorted(os.listdir(HERE)):
            if not (fn.startswith("convert_") and fn.endswith(".py")) or fn in CONVERTERS or fn in elsewhere: continue
            with open(os.path.join(HERE, fn), encoding="utf-8") as f: code = f.read().replace(" ", "")
            self.assertNotIn('"obligated-parties":', code, f"{fn} writes obligated parties and is held by no test of #74")

    def test_backlog_74_the_default_is_the_party_the_shipped_bundles_carry(self):
        """The table at the top of this file was typed. The shipped bundles
        were written before the party became an argument, so they say what
        each converter wrote on its own."""
        if not os.path.isdir(os.path.join(ROOT, "converted_examples")):
            self.skipTest("no converted_examples/ beside jascon/ (the skill unpacked on its own)")
        for conv, rel in SHIPPED.items():
            bundle = os.path.join(ROOT, "converted_examples", *rel.split("/"))
            seen = parties_of(bundle)
            self.assertGreater(sum(seen.values()), 100, f"{rel}: the bundle was not found")
            self.assertEqual(set(seen), {(CONVERTERS[conv][0],)}, rel)
        # SP 800-53 5.2.0 states a level on every control: its bundle holds the two levels and nothing else
        seen = parties_of(os.path.join(ROOT, "converted_examples", "US.SP800-53", "sp800-53-core-bundle"))
        self.assertEqual({p for ps in seen for p in ps}, {NIST + "organization", NIST + "system"})
        self.assertIn(CONVERTERS["convert_nist.py"][0], {p for ps in seen for p in ps})


if __name__ == "__main__":
    unittest.main()
