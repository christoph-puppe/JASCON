#!/usr/bin/env python3
"""convert_cr26.py on its pinned source, end to end (backlog #73).

    python3 jascon/scripts/test_convert_cr26.py

The source is not in the repository. The test reads it where the converter
does, sources/cr_fedramp-consolidated-rules.json; where to get it stands in
converted_examples/FedRAMP-CR26/SOURCES.sha256. Without the file nothing is
tested, and the run says so and exits 2: a test that did not run has not
passed. The Validators workflow downloads the file first.

Why this file exists beside the coverage report. The report says where a
source PATH is declared to go. The declaration is the converter's own, and
it stays true when nothing is written: until 2026-11-14 the unit of a
timeframe range was declared mapped and stood nowhere in the bundle. This
file looks at VALUES. For the path kinds publication 2026.11.02.01 brought
(a rule's control links, a timeframe range, an optional notification, the
glossary's second flag, a fraction) it derives from the source what must
stand where, with no code of the converter, and reads the written bundle.
It then runs the converter with each of its arguments, and on sources that
were changed in one place, to see the run stop where it must.

Since 2026-11-14 the converter keeps a ledger of every source value
(backlog #41), and its record is compared with the committed one by the
workflow. What this file holds of it: that the record counts every source
value once and under the path map's paths; that nothing is unaccounted and
no claim fails; that a drop is declared only where the path map says the
path is not carried, and a row which names a destination has every value
there; that a flag and a fraction stand in the bundle, each read at its
place; and that a value the converter does not write, or a claim that does
not hold against the written files, ends the run with 1.

And of the losses the ledger found (author, 2026-11-14): the status of a
family or of a KSI category is mapped to the kernel's lifecycle by one rule,
on the document's Set and on every object made from the document, with the
source's word beside it on the Set; no object of a document the source does
not call stable is written active; the id of a KSI category is carried.

Standard library only. Every run writes into a temporary directory."""
import copy, decimal, hashlib, json, os, re, shutil, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
CONVERTER = os.path.join(HERE, "convert_cr26.py")
SOURCE = os.path.join(ROOT, "sources", "cr_fedramp-consolidated-rules.json")
NS = "https://ns.fedramp.gov/cr26"; NIST = "https://ns.nist.gov/sp800-53/req"
NARR = NS + "/facet/narrative@1"
REP = "https://ns.jascon.net/stdlib/facet/reporting-obligation@1"
TERM = "https://ns.jascon.net/stdlib/facet/terminology@1"
COMPAT = "https://ns.jascon.net/compat/oscal-1x@1"
EFF = "https://ns.jascon.net/stdlib/facet/effectivity@1"
DEFAULT_PARTY = NS + "/party/provider"
TMP = None          # one temporary directory for the whole run

def read_json(path):
    # a number that is no integer is kept as the digits written, so that a float cannot hide one
    with open(path, encoding="utf-8") as f: return json.load(f, parse_float=decimal.Decimal)

def convert(*args, converter=CONVERTER):
    """-> (exit code, stdout, stderr) of one run of the converter."""
    p = subprocess.run([sys.executable, converter, *args], capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr

def files(bundle):
    """{relative path: bytes} of every file of a written bundle."""
    out = {}
    for base, _, names in os.walk(bundle):
        for n in names:
            full = os.path.join(base, n)
            with open(full, "rb") as f: out[os.path.relpath(full, bundle).replace(os.sep, "/")] = f.read()
    return out

def objects(bundle):
    """{object id: object} of a written bundle, read through its manifest."""
    return {e["id"]: read_json(os.path.join(bundle, *e["path"].split("/")))
            for e in read_json(os.path.join(bundle, "content-manifest.json"))["objects"]}

def slug(s): return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def rules(src):
    for fam in src["FRR"].values():
        for track in fam["data"].values():
            for subset in track.values():
                yield from subset.items()

def indicators(src):
    for theme in src["KSI"].values(): yield from theme["indicators"].items()

class Converted(unittest.TestCase):
    """One run without arguments other than --out; every test reads its result."""
    @classmethod
    def setUpClass(cls):
        cls.src = read_json(SOURCE)
        cls.out = os.path.join(TMP, "default")
        cls.code, cls.stdout, cls.stderr = convert("--out", cls.out)
        cls.bundle = os.path.join(cls.out, "cr26-core-bundle")
        cls.objs = objects(cls.bundle) if cls.code == 0 else {}
        cls.report = read_json(os.path.join(cls.out, "cr26-coverage-report.json")) if cls.code == 0 else {}
        cls.ledger = read_json(os.path.join(cls.out, "cr26-conversion-ledger.json")) if cls.code == 0 else {}
    def setUp(self):
        self.assertEqual(self.code, 0, self.stderr or self.stdout)

    def req(self, rid): return self.objs[f"{NS}/req/{rid}"]

    def same(self, a, b, where, seen):
        """`b`, read from the bundle, is the source's `a`: every value with its
        type, and a number that is no integer as the decimal string of its
        digits (the kernel's spelling of a fraction, D3.9). Each such number
        and each boolean met is noted in `seen`, as (where, what it is)."""
        if isinstance(a, dict):
            self.assertIsInstance(b, dict, where); self.assertEqual(list(a), list(b), where)
            for k in a: self.same(a[k], b[k], f"{where}/{k}", seen)
        elif isinstance(a, list):
            self.assertIsInstance(b, list, where); self.assertEqual(len(a), len(b), where)
            for i, (x, y) in enumerate(zip(a, b)): self.same(x, y, f"{where}/{i}", seen)
        elif isinstance(a, decimal.Decimal):
            self.assertIsInstance(b, str, where); self.assertEqual(b, format(a, "f"), where)
            self.assertRegex(b, r"^(-?[1-9][0-9]*(\.[0-9]+)?|0(\.[0-9]+)?|-0\.[0-9]*[1-9][0-9]*)$", where)   # the kernel's decimalString
            seen.append((where, "fraction"))
        else:
            self.assertIs(type(b), type(a), where); self.assertEqual(a, b, where)
            if isinstance(a, bool): seen.append((where, "boolean"))


class ExitCodeAndRecord(Converted):
    def test_every_leaf_has_a_destination_and_the_run_says_so(self):
        self.assertEqual(self.report["totals"]["unmapped"], 0)
        self.assertEqual(self.report["unmapped"], [])
        self.assertIn("UNMAPPED: 0", self.stdout)

    def test_the_report_states_the_digest_of_the_manifest_it_was_written_with(self):
        with open(os.path.join(self.bundle, "content-manifest.json"), "rb") as f:
            digest = "sha256:" + hashlib.sha256(f.read()).hexdigest()
        self.assertEqual(self.report["bundle"]["content-manifest-digest"], digest)
        with open(os.path.join(self.out, "cr26-coverage-report.md"), encoding="utf-8") as f:
            self.assertIn(digest, f.read())

    def test_one_requirement_for_every_rule_and_every_indicator(self):
        want = {f"{NS}/req/{rid}" for rid, _ in rules(self.src)} | {f"{NS}/ksi/{iid}" for iid, _ in indicators(self.src)}
        got = {i for i in self.objs if i.startswith((f"{NS}/req/", f"{NS}/ksi/"))}
        self.assertEqual(got, want)
        self.assertEqual(self.report["objects"]["requirements(rules+ksi)"], len(want))


class ControlLinks(Converted):
    """A rule's `controls` are converted as a KSI's are: one Mapping a link."""
    def links(self):
        for kind, items in (("req", rules(self.src)), ("ksi", indicators(self.src))):
            for oid, o in items:
                for c in o.get("controls") or []: yield kind, oid, c

    def test_every_link_is_a_mapping_from_its_requirement_to_the_control(self):
        n = 0
        for kind, oid, c in self.links():
            m = self.objs.get(f"{NS}/map/{slug(oid)}--{slug(c)}")
            self.assertIsNotNone(m, (oid, c))
            self.assertEqual((m["source-ref"], m["target-ref"]), (f"{NS}/{kind}/{oid}", f"{NIST}/{c.upper()}"), (oid, c))
            self.assertEqual((m["relationship"], m["direction"], m["confidence"]), ("supports", "source-to-target", "draft"))
            n += 1
        self.assertGreater(sum(1 for k, _, _ in self.links() if k == "req"), 0, "the source has no rule with controls: nothing was tested")
        self.assertEqual(self.report["objects"]["mappings"], n)

    def test_no_mapping_without_a_link(self):
        want = {f"{NS}/map/{slug(oid)}--{slug(c)}" for _, oid, c in self.links()}
        self.assertEqual({i for i, o in self.objs.items() if "relationship" in o}, want)

    def test_a_mapping_says_who_wrote_it_and_when_as_the_source_does(self):
        day = self.src["info"]["last_updated"]
        for i, o in self.objs.items():
            if "relationship" in o:
                self.assertEqual(o["provenance"], {"author-ref": f"{NS}/party/fedramp", "date": day}, i)


class Timeframes(Converted):
    """One timeframe is the parameter `timeframe`; a range is its two bounds."""
    NAMES = (("timeframe_num", "timeframe", "lower"), ("timeframe_num_min", "timeframe-min", "higher"),
             ("timeframe_num_max", "timeframe-max", "lower"))

    def test_a_statement_has_the_parameters_the_rule_states_and_no_other(self):
        ranges = 0
        for rid, r in rules(self.src):
            got = {p["name"]: p for p in self.req(rid)["statements"][0].get("parameters", [])}
            self.assertEqual(set(got), {name for key, name, _ in self.NAMES if key in r}, rid)
            for key, name, tightening in self.NAMES:
                if key not in r: continue
                p, unit = got[name], r["timeframe_type"]
                self.assertIs(type(p["num"]), int, (rid, name))
                self.assertEqual((p["num"], p["unit"], p["tightening"]), (r[key], unit, tightening), (rid, name))
                if unit in ("seconds", "minutes", "hours"):
                    self.assertEqual(p["type"], "elapsed-duration", (rid, name)); self.assertNotIn("calendar-ref", p)
                else:
                    self.assertEqual((p["type"], p.get("calendar-ref")), ("calendar-period", f"{NS}/calendar/us-federal"), (rid, name))
            ranges += "timeframe_num_min" in r or "timeframe_num_max" in r
        self.assertGreater(ranges, 0, "the source has no rule with a timeframe range: nothing was tested")


class Notifications(Converted):
    """reporting-obligation@1 lists the duties; an entry the source marks
    optional stands whole, with its flag, in the converter's narrative@1."""
    @staticmethod
    def written(entry):
        return {k: ({"en": v} if k == "name" else v) for k, v in entry.items()}

    def test_duties_and_optional_entries_stand_where_they_belong(self):
        optional = 0
        for rid, r in rules(self.src):
            facets = self.req(rid).get("facets", {})
            entries = r.get("notification") or []
            duties = [self.written(e) for e in entries if "optional" not in e]
            marked = [self.written(e) for e in entries if "optional" in e]
            self.assertEqual(facets.get(REP, {}).get("notification", []), duties, rid)
            self.assertEqual(facets.get(NARR, {}).get("optional-notification", []), marked, rid)
            for e in marked: self.assertIs(e["optional"], True, rid)
            optional += len(marked)
        self.assertGreater(optional, 0, "the source marks no notification optional: nothing was tested")


class Glossary(Converted):
    def setUp(self):
        super().setUp()
        self.root = self.objs[f"{NS}/set/root"]["facets"]
        self.terms = self.src["FRD"]["data"]["all"]

    def test_ignore_in_terms_stands_beside_the_glossary_by_term_id(self):
        want = {tid: t["ignore_in_terms"] for tid, t in self.terms.items() if "ignore_in_terms" in t}
        self.assertGreater(len(want), 0, "the source has no ignore_in_terms: nothing was tested")
        got = self.root[NARR].get("ignore-in-terms")
        self.assertEqual(got, want)
        for v in got.values(): self.assertIs(type(v), bool)

    def test_a_term_without_alternatives_has_no_aliases(self):
        written, empty = self.root[TERM]["terms"], 0
        self.assertEqual(set(written), set(self.terms))
        for tid, t in self.terms.items():
            if t.get("alts"): self.assertEqual(written[tid].get("aliases"), t["alts"], tid)
            else:
                self.assertNotIn("aliases", written[tid], tid); empty += 1
        self.assertGreater(empty, 0, "the source has no term without alternatives: nothing was tested")


class Fractions(Converted):
    """A number that is no integer is a decimal string in a parked payload
    and stands nowhere else (NUMBER-1, D3.9)."""
    def test_class_variants_are_the_source_with_fractions_as_decimal_strings(self):
        seen = []
        for kind, items in (("req", rules(self.src)), ("ksi", indicators(self.src))):
            for oid, o in items:
                if o.get("varies_by_class"):
                    self.same(o["varies_by_class"], self.objs[f"{NS}/{kind}/{oid}"]["facets"][COMPAT]["class-variants"], oid, seen)
        fractions = [w for w, kind in seen if kind == "fraction"]
        self.assertGreater(len(fractions), 0, "the source has no fraction in a class variant: nothing was tested")
        self.assertEqual(sum(e["count"] for e in self.report["fractions-as-decimal-strings"]), len(fractions))

    def test_no_file_of_the_bundle_holds_a_number_that_is_no_integer(self):
        def walk(n, where):
            if isinstance(n, dict):
                for k, v in n.items(): walk(v, f"{where}/{k}")
            elif isinstance(n, list):
                for i, v in enumerate(n): walk(v, f"{where}/{i}")
            else: self.assertNotIsInstance(n, (decimal.Decimal, float), where)
        for rel, raw in files(self.bundle).items():
            walk(json.loads(raw.decode("utf-8"), parse_float=decimal.Decimal), rel)


class ObligatedParty(Converted):
    """A rule's parties are what `affects` says. The fallback, the converter's
    default or the caller's party, stands where the source names nobody."""
    def check(self, objs, fallback):
        stated = silent = 0
        for rid, r in rules(self.src):
            want = [f"{NS}/party/{slug(a)}" for a in r.get("affects") or []]
            self.assertEqual(objs[f"{NS}/req/{rid}"]["statements"][0]["obligated-parties"], want or [fallback], rid)
            stated += bool(want); silent += not want
        for iid, _ in indicators(self.src):
            self.assertEqual(objs[f"{NS}/ksi/{iid}"]["statements"][0]["obligated-parties"], [fallback], iid)
            silent += 1
        self.assertGreater(stated, 0); self.assertGreater(silent, 0)
        return stated, silent

    def test_the_default(self):
        stated, silent = self.check(self.objs, DEFAULT_PARTY)
        self.assertEqual(self.report["obligated-party"], {"value": DEFAULT_PARTY, "origin": "converter-default",
                         "converter-default": DEFAULT_PARTY, "source-states": "in `affects` of a rule"})
        self.assertEqual((self.report["counters"]["statements-party-from-affects"],
                          self.report["counters"]["statements-party-fallback"]), (stated, silent))

    def test_the_callers_party_replaces_the_fallback_and_nothing_else(self):
        mine, out = "https://caller.example/party/csp", os.path.join(TMP, "party")
        code, _, err = convert("--out", out, "--obligated-party", mine)
        self.assertEqual(code, 0, err)
        bundle = os.path.join(out, "cr26-core-bundle")
        self.check(objects(bundle), mine)
        a, b = files(self.bundle), files(bundle)
        self.assertEqual(set(a), set(b))
        changed = {rel for rel in a if a[rel] != b[rel]}
        man = read_json(os.path.join(bundle, "content-manifest.json"))
        ksi = {e["path"] for e in man["objects"] if e["id"].startswith(f"{NS}/ksi/")}
        silent_rules = {e["path"] for e in man["objects"] for rid, r in rules(self.src)
                        if e["id"] == f"{NS}/req/{rid}" and not r.get("affects")}
        self.assertEqual(changed, ksi | silent_rules | {"content-manifest.json"})
        report = read_json(os.path.join(out, "cr26-coverage-report.json"))
        self.assertEqual(report["obligated-party"], {"value": mine, "origin": "caller", "converter-default": DEFAULT_PARTY,
                                                      "source-states": "in `affects` of a rule"})
        with open(os.path.join(out, "cr26-coverage-report.md"), encoding="utf-8") as f: md = f.read()
        self.assertIn(f"`{mine}`", md); self.assertIn("given by the caller with `--obligated-party`", md)

    def test_the_default_given_by_the_caller_is_the_same_bundle(self):
        out = os.path.join(TMP, "party-default")
        code, _, err = convert("--out", out, "--obligated-party", DEFAULT_PARTY)
        self.assertEqual(code, 0, err)
        self.assertEqual(files(os.path.join(out, "cr26-core-bundle")), files(self.bundle))
        self.assertEqual(read_json(os.path.join(out, "cr26-coverage-report.json"))["obligated-party"]["origin"], "caller")


class Provenance(Converted):
    """--author-ref and --date overwrite what the source says on every Mapping (backlog #69)."""
    def run_with(self, name, *args):
        out = os.path.join(TMP, name)
        code, _, err = convert("--out", out, *args)
        self.assertEqual(code, 0, err)
        return os.path.join(out, "cr26-core-bundle")

    def test_both_are_written_on_every_mapping_and_nothing_else_changes(self):
        bundle = self.run_with("prov", "--author-ref", "https://caller.example/party/me", "--date", "2026-01-31")
        objs = objects(bundle)
        maps = {i for i, o in objs.items() if "relationship" in o}
        self.assertEqual(maps, {i for i, o in self.objs.items() if "relationship" in o})
        for i in maps:
            self.assertEqual(objs[i]["provenance"], {"author-ref": "https://caller.example/party/me", "date": "2026-01-31"}, i)
        a, b = files(self.bundle), files(bundle)
        man = read_json(os.path.join(bundle, "content-manifest.json"))
        self.assertEqual({rel for rel in a if a[rel] != b.get(rel)},
                         {e["path"] for e in man["objects"] if e["id"] in maps} | {"content-manifest.json"})

    def test_one_alone_leaves_the_other_as_the_source_has_it(self):
        day = self.src["info"]["last_updated"]
        for name, args, want in (("prov-date", ("--date", "2026-01-31"), {"author-ref": f"{NS}/party/fedramp", "date": "2026-01-31"}),
                                 ("prov-author", ("--author-ref", "https://caller.example/party/me"),
                                  {"author-ref": "https://caller.example/party/me", "date": day})):
            for i, o in objects(self.run_with(name, *args)).items():
                if "relationship" in o: self.assertEqual(o["provenance"], want, (name, i))


def leaf_values(node):
    """every leaf value of a JSON document, in document order"""
    if isinstance(node, dict):
        for v in node.values(): yield from leaf_values(v)
    elif isinstance(node, list):
        for v in node: yield from leaf_values(v)
    else: yield node

class TheLedger(Converted):
    """The conversion ledger (backlog #41). Its record is compared with the
    committed one by the workflow; here it is held to the source and to the
    path map by counts this file makes itself."""
    def setUp(self):
        super().setUp()
        self.rows = self.ledger["paths"]
        self.map = {r["path"]: r for r in self.report["path-map"]}
        with open(os.path.join(self.out, "cr26-coverage-report.md"), encoding="utf-8") as f: self.md = f.read()

    def at(self, pointer):
        """the source value a pointer of the record names (tag#/a/b/0/c, RFC 6901)"""
        node = self.src
        for seg in pointer.split("#", 1)[1].split("/")[1:]:
            seg = seg.replace("~1", "/").replace("~0", "~")
            node = node[int(seg)] if isinstance(node, list) else node[seg]
        return node

    def test_the_record_counts_every_source_value_once_under_the_paths_of_the_path_map(self):
        n = sum(1 for _ in leaf_values(self.src))
        self.assertEqual(self.ledger["leaf-values"], n)
        self.assertEqual(sum(self.ledger["totals"].values()), n)
        self.assertEqual(len({(r["path"], r["outcome"]) for r in self.rows}), len(self.rows), "one row per path and outcome")
        by_path = {}
        for r in self.rows: by_path[r["path"]] = by_path.get(r["path"], 0) + r["count"]
        self.assertEqual(by_path, {p: r["count"] for p, r in self.map.items()}, "the ledger and the path map count the same paths")

    def test_no_claim_of_the_ledger_fails(self):
        self.assertEqual(self.ledger["verification-failures"], [])
        self.assertEqual(self.report["ledger"]["verification-failures"], 0)
        self.assertIn("failed checks 0", self.stdout)

    def test_no_drop_is_declared_and_the_history_and_the_flow_are_carried(self):
        # until 2026-11-14 the path map declared two drops (the update history of an entry, 957 values, and the one
        # process flow, 35); the author decided that both are carried
        for r in self.rows:
            self.assertNotEqual(self.map[r["path"]]["level"], "declared-drop", r["path"])
            self.assertNotEqual(r["outcome"], "intentionally-dropped", r["path"])
        self.assertEqual(self.ledger["totals"]["intentionally-dropped"], 0)
        carried = lambda part: sum(r["count"] for r in self.rows if part in r["path"] and r["outcome"] == "copied")
        # 957 of terms, rules and indicators, and the 2 of the one CTL entry with a history, which were carried before
        self.assertEqual((carried(".updated[]."), carried(".info.flows[]")), (957 + 2, 35))

    def test_a_row_that_names_a_destination_has_every_value_there(self):
        for r in self.rows:
            level = self.map[r["path"]]["level"]
            self.assertIn(level, ("L1", "L2", "declared-drop"), r["path"])
            if level in ("L1", "L2"):
                self.assertIn(r["outcome"], ("copied", "transformed"), f"{r['path']}: the path map names a destination")
                self.assertGreater(len(r["to"]), 0, r["path"])
        self.assertEqual(self.report["ledger"]["path-map-rows-the-ledger-contradicts"], [])
        self.assertIn("path-map rows contradicted 0", self.stdout)

    def test_nothing_is_unaccounted_and_nothing_is_called_no_content(self):
        t = self.ledger["totals"]
        self.assertEqual(list(t), ["copied", "transformed", "not-content", "intentionally-dropped", "unaccounted"])
        self.assertEqual((t["unaccounted"], self.ledger["unaccounted-paths"], self.report["ledger"]["unaccounted"]), (0, [], []))
        # this source has no name that only selects a field, no namespace and no id that is rebuilt: nothing may hide there
        self.assertEqual((t["not-content"], self.report["ledger"]["not-content"]), (0, []))
        self.assertNotIn("UNACCOUNTED", self.stdout)

    def test_the_declared_drops_are_listed_with_a_reading_and_an_example_that_is_no_prose(self):
        drops = self.report["ledger"]["declared-drops"]
        self.assertEqual(sum(x["source-values"] for x in drops), self.ledger["totals"]["intentionally-dropped"])
        self.assertEqual({x["reason"] for x in drops}, {r["destination"] for r in self.report["path-map"] if r["level"] == "declared-drop"})
        for x in drops:
            self.assertEqual(sum(q["count"] for q in x["paths"]), x["source-values"], x["reason"])
            self.assertTrue(x["reading"].startswith(("content", "not content, because")), x["reading"])
            self.assertIn(x["reading"], self.md)
            if "value" in x["example"]:
                self.assertEqual(self.at(x["example"]["source"]), x["example"]["value"])
                self.assertNotIn(" ", str(x["example"]["value"]))

    def test_the_report_says_what_the_record_says(self):
        L, t = self.report["ledger"], self.ledger["totals"]
        self.assertEqual((L["file"], L["leaf-values"], L["totals"]), ("cr26-conversion-ledger.json", self.ledger["leaf-values"], t))
        self.assertEqual(sum(u["count"] for u in L["unaccounted"]), t["unaccounted"])
        self.assertEqual(sum(x["source-values"] for x in L["not-content"]), t["not-content"])
        self.assertEqual({x["rule"] for x in L["rules"]}, {d["rule"] for r in self.rows for d in r.get("to", []) if "rule" in d})
        for words in (f"**{t['copied']:,} copied**", f"**{t['transformed']:,} transformed**", f"**{t['not-content']:,} no content**",
                      f"**{t['intentionally-dropped']:,} dropped for a declared reason**", f"**{t['unaccounted']:,} unaccounted**"):
            self.assertIn(words, self.md)
        for x in L["rules"]: self.assertIn(f"| {x['rule']} | {x['source-values']:,} |", self.md)

    def test_the_reports_and_the_record_print_no_phrase_of_the_publication(self):
        phrases = set()        # a key of the source with a space in it: the label of a node of a flow diagram
        def keys(n):
            if isinstance(n, dict):
                for k, v in n.items():
                    if " " in k: phrases.add(k)
                    keys(v)
            elif isinstance(n, list):
                for v in n: keys(v)
        keys(self.src)
        self.assertGreater(len(phrases), 0, "the source has no key that is a phrase: nothing was tested")
        for name in ("cr26-coverage-report.md", "cr26-coverage-report.json", "cr26-conversion-ledger.json"):
            with open(os.path.join(self.out, name), encoding="utf-8") as f: text = f.read()
            for p in phrases: self.assertNotIn(p, text, name)
        for r in self.rows:
            for pointer in [r["example"]] + [d["pointer"] for d in r.get("to", [])]: self.assertNotIn(" ", pointer, r["path"])

    def test_the_values_with_no_source_value_are_counted_on_the_whole_bundle(self):
        written = sum(1 for o in self.objs.values() for _ in leaf_values(o))
        written += sum(1 for _ in leaf_values(read_json(os.path.join(self.bundle, "content-manifest.json"))))
        rows = self.report["ledger"]["written-values-with-no-source-value"]
        self.assertEqual(sum(r["leaf-values"] for r in rows), written)
        for r in rows: self.assertLessEqual(r["no-source-value"], r["leaf-values"], r["written-as"])
        carried = next(r for r in rows if r["written-as"] == "carried Rev 5 Requirement")
        self.assertEqual(carried["no-source-value"], carried["leaf-values"], "an object copied from another bundle has no value of this source")


class FlagsAndFractions(Converted):
    """A flag and a fraction are content like a string. Until 2026-11-14 the
    ledger could not follow them and read all 52 as unaccounted. Each of them
    is read here at the place the converter writes it, with no help of the
    ledger; a flag or a fraction this class does not read fails the count at
    the end. That the ledger follows them too is the total of the record."""
    def test_every_flag_and_every_fraction_of_the_source_stands_in_the_bundle(self):
        seen, root = [], self.objs[f"{NS}/set/root"]["facets"]
        # the glossary: do_not_link in terminology@1, ignore_in_terms beside it, the block's own members in glossary-info
        for tid, t in self.src["FRD"]["data"]["all"].items():
            if "do_not_link" in t:
                self.same(t["do_not_link"], root[TERM]["terms"][tid].get("do-not-link"), f"FRD/{tid}/do_not_link", seen)
            if "ignore_in_terms" in t:
                self.same(t["ignore_in_terms"], root[NARR]["ignore-in-terms"].get(tid), f"FRD/{tid}/ignore_in_terms", seen)
        self.same(self.src["FRD"]["info"], root[TERM]["glossary-info"], "FRD/info", seen)
        # a family: when it takes effect, by default and for each track
        for fk, fam in self.src["FRR"].items():
            eff, info = self.objs[f"{NS}/set/tax/{slug(fk)}"]["facets"].get(EFF, {}), fam["info"]
            if "effective" in info: self.same(info["effective"], eff.get("default"), f"FRR/{fk}/info/effective", seen)
            for track in ("20x", "rev5"):
                if track in info: self.same(info[track]["effective"], eff.get(track), f"FRR/{fk}/info/{track}/effective", seen)
        # a rule or an indicator: a notification marked optional, and the class variants
        for rid, r in rules(self.src):
            facets = self.req(rid).get("facets", {})
            marked = [e for e in r.get("notification") or [] if "optional" in e]
            written = facets.get(NARR, {}).get("optional-notification", [])
            self.assertEqual(len(written), len(marked), rid)
            for e, w in zip(marked, written): self.same(e["optional"], w.get("optional"), f"{rid}/notification/optional", seen)
            if r.get("varies_by_class"): self.same(r["varies_by_class"], facets[COMPAT]["class-variants"], f"{rid}/varies_by_class", seen)
        for iid, ind in indicators(self.src):
            if ind.get("varies_by_class"):
                self.same(ind["varies_by_class"], self.objs[f"{NS}/ksi/{iid}"]["facets"][COMPAT]["class-variants"], f"{iid}/varies_by_class", seen)
        # and that is every one of them: the count of what was read is the count of the source
        every = {"boolean": 0, "number that is no integer": 0, "null": 0}
        for v in leaf_values(self.src):
            if isinstance(v, bool): every["boolean"] += 1
            elif v is None: every["null"] += 1
            elif not isinstance(v, (str, int)): every["number that is no integer"] += 1
        read = {"boolean": sum(1 for _, what in seen if what == "boolean"),
                "number that is no integer": sum(1 for _, what in seen if what == "fraction"), "null": 0}
        self.assertEqual(read, every, "a flag or a fraction of the source stands on a path this test does not read")
        self.assertGreater(every["boolean"], 0); self.assertGreater(every["number that is no integer"], 0)
        self.assertEqual(self.report["ledger"]["nulls-in-the-source"], every["null"])
        self.assertEqual(self.ledger["totals"]["unaccounted"], 0)
        decimal_rule = [d for r in self.ledger["paths"] for d in r.get("to", []) if d.get("rule", "").startswith("decimal string")]
        self.assertEqual(sum(d["count"] for d in decimal_rule), every["number that is no integer"], "a fraction is written by the rule the ledger checks")


class StatusAndLifecycle(Converted):
    """The publisher gives a family and a KSI category the status of a
    document: stable, placeholder or empty. The kernel's lifecycle knows
    draft, active, deprecated, withdrawn. The converter maps by one rule and
    keeps the source's word; the rule is stated here a second time, from the
    author's decision and not from the converter's table."""
    RULE = {"stable": "active", "placeholder": "draft", "empty": "draft"}

    def documents(self):
        """(the document's Set, its status, the ids of the objects made from the document)"""
        for fk, fam in self.src["FRR"].items():
            made = set()
            for track in fam["data"].values():
                for subset in track.values():
                    for rid, r in subset.items():
                        made.add(f"{NS}/req/{rid}")
                        made.update(f"{NS}/map/{slug(rid)}--{slug(c)}" for c in r.get("controls") or [])
            made.update(i for i in self.objs if i.startswith(f"{NS}/set/subset/{slug(fk)}-"))
            yield f"{NS}/set/tax/{slug(fk)}", fam["info"].get("status"), made
        for ck, theme in self.src["KSI"].items():
            made = set()
            for iid, ind in theme["indicators"].items():
                made.add(f"{NS}/ksi/{iid}")
                made.update(f"{NS}/map/{slug(iid)}--{slug(c)}" for c in ind.get("controls") or [])
            yield f"{NS}/set/ksi/{slug(ck)}", theme.get("status"), made

    def test_the_set_of_a_document_has_the_lifecycle_of_the_rule_and_the_sources_word_beside_it(self):
        n = 0
        for set_id, status, _ in self.documents():
            self.assertIn(status, self.RULE, set_id)
            o = self.objs[set_id]
            self.assertEqual(o["lifecycle"], self.RULE[status], set_id)
            self.assertEqual(o["facets"][NARR].get("status"), status, set_id)
            n += 1
        self.assertEqual(n, len(self.src["FRR"]) + len(self.src["KSI"]))

    def test_every_object_made_from_a_document_follows_the_documents_status(self):
        covered = set()
        for set_id, status, made in self.documents():
            self.assertGreater(len(made), 0, set_id)
            for i in made:
                self.assertEqual(self.objs[i]["lifecycle"], self.RULE[status], f"{i}: its document is {status}")
            self.assertEqual(covered & made, set(), "an object is made from one document")
            covered |= made | {set_id}
        # every Requirement and every Mapping of the publication is an object of a document
        for i, o in self.objs.items():
            if i.startswith((f"{NS}/req/", f"{NS}/ksi/", f"{NS}/map/")): self.assertIn(i, covered)

    def test_nothing_of_a_document_the_source_does_not_call_stable_is_written_active(self):
        for set_id, status, made in self.documents():
            if status != "stable":
                for i in made | {set_id}: self.assertNotEqual(self.objs[i]["lifecycle"], "active", i)

    def test_the_report_counts_the_lifecycles_as_the_bundle_has_them(self):
        got = {}
        for o in self.objs.values(): got[o["lifecycle"]] = got.get(o["lifecycle"], 0) + 1
        said = {}
        for x in self.report["lifecycle"]["objects"]: said[x["lifecycle"]] = said.get(x["lifecycle"], 0) + x["count"]
        self.assertEqual(said, got)
        self.assertEqual(self.report["lifecycle"]["rule"], self.RULE)
        from_status = sum(x["count"] for x in self.report["lifecycle"]["objects"] if x["origin"] == "from the status of a document")
        self.assertEqual(from_status, sum(len(made) + 1 for _, _, made in self.documents()))


class KsiCategoryIds(Converted):
    def test_the_id_of_a_ksi_category_is_an_alias_of_its_set(self):
        n = 0
        for ck, theme in self.src["KSI"].items():
            aliases = self.objs[f"{NS}/set/ksi/{slug(ck)}"].get("aliases", [])
            self.assertEqual([a["value"] for a in aliases], [theme["id"]], ck)
            self.assertEqual({a["scheme"] for a in aliases}, {"fedramp-cr26:KSI.id"}, ck)
            n += 1
        self.assertGreater(n, 0, "the source has no KSI category: nothing was tested")


class CarriedRequirements(Converted):
    """The Rev 5 Requirements the overlay tailors are carried as the SP 800-53
    bundle has them, and so are the pins of their facets."""
    NIST_BUNDLE = os.path.join(ROOT, "converted_examples", "US.SP800-53", "sp800-53-core-bundle")

    def test_a_carried_requirement_and_the_pins_of_its_facets_are_the_sp800_53_bundles_own(self):
        theirs = read_json(os.path.join(self.NIST_BUNDLE, "content-manifest.json"))
        their_path = {e["id"]: e["path"] for e in theirs["objects"]}
        their_pin = {s["id"]: s["path"] for s in theirs["facet-schemas"]}
        mine = read_json(os.path.join(self.bundle, "content-manifest.json"))
        my_pin = {s["id"]: s["path"] for s in mine["facet-schemas"]}
        carried = [i for i in self.objs if i.startswith(NIST + "/")]
        self.assertGreater(len(carried), 0, "no Requirement is carried: nothing was tested")
        for i in carried:
            self.assertEqual(self.objs[i], read_json(os.path.join(self.NIST_BUNDLE, *their_path[i].split("/"))), i)
            for key in self.objs[i].get("facets", {}):
                fid = key.rsplit("@", 1)[0]
                self.assertIn(fid, my_pin, f"{i}: no pin for {key}")
                with open(os.path.join(self.bundle, *my_pin[fid].split("/")), "rb") as a, \
                     open(os.path.join(self.NIST_BUNDLE, *their_pin[fid].split("/")), "rb") as b:
                    self.assertEqual(a.read(), b.read(), f"{fid}: the pin is not the SP 800-53 bundle's")


class Arguments(unittest.TestCase):
    """An argument the converter cannot honour stops the run before anything is written."""
    def test_a_run_that_cannot_be_honoured_writes_nothing(self):
        cases = ((["--out"], "needs a directory"),
                 (["--out", "{d}", "--out", "{d}"], "more than once"),
                 (["--outt", "{d}"], "unknown argument"),
                 (["--out", "{d}", "--obligated_party", "https://a.example/p"], "unknown argument"),
                 (["--out", "{d}", "stray"], "unknown argument"),
                 (["--out", "{d}", "--obligated-party", "provider"], "not an http(s) URI"),
                 (["--out", "{d}", "--obligated-party", "https://a.example/p", "--obligated-party", "https://b.example/p"], "more than once"),
                 (["--out", "{d}", "--obligated-party"], "needs a value"),
                 (["--out", "{d}", "--author-ref", "me"], "not an http(s) URI"),
                 (["--out", "{d}", "--date", "2026-02-30"], "not a day of the calendar"),
                 (["--out", "{d}", "--date", "tomorrow"], "not a date"))
        for n, (args, word) in enumerate(cases):
            d = os.path.join(TMP, f"refused-{n}")
            code, out, err = convert(*[a.replace("{d}", d) for a in args])
            self.assertNotEqual(code, 0, args); self.assertIn(word, err, args)
            self.assertFalse(os.path.exists(d), args)


class ChangedSource(unittest.TestCase):
    """The converter on a source that was changed in one place. It finds what
    it reads relative to its own file, so it is run from a copy of that
    layout whose source is the changed one."""
    @classmethod
    def setUpClass(cls):
        cls.root = os.path.join(TMP, "root")
        scripts = os.path.join(cls.root, "jascon", "scripts"); os.makedirs(scripts)
        for name in ("convert_cr26.py", "oscal_conv_lib.py"): shutil.copy(os.path.join(HERE, name), scripts)
        shutil.copytree(os.path.join(ROOT, "jascon", "schemas", "stdlib"), os.path.join(cls.root, "jascon", "schemas", "stdlib"))
        # of the SP 800-53 bundle the converter reads the Requirements, the manifest and the pinned schemas
        nist = ("converted_examples", "US.SP800-53", "sp800-53-core-bundle")
        shutil.copytree(os.path.join(ROOT, *nist, "objects", "req"), os.path.join(cls.root, *nist, "objects", "req"))
        shutil.copytree(os.path.join(ROOT, *nist, "schemas"), os.path.join(cls.root, *nist, "schemas"))
        shutil.copy(os.path.join(ROOT, *nist, "content-manifest.json"), os.path.join(cls.root, *nist))
        os.makedirs(os.path.join(cls.root, "sources"))
        cls.converter = os.path.join(scripts, "convert_cr26.py")
        cls.source = os.path.join(cls.root, "sources", "cr_fedramp-consolidated-rules.json")
        with open(SOURCE, encoding="utf-8") as f: cls.original = json.load(f)
        cls.n = 0

    def run_on(self, change, converter=None):
        """-> (exit code, stdout, stderr, the --out directory) of a run on the source after change(source)."""
        src = copy.deepcopy(self.original)
        if change is not None:
            change(src)
            with open(self.source, "w", encoding="utf-8") as f: json.dump(src, f, ensure_ascii=False, indent=1)
        elif os.path.exists(self.source): os.remove(self.source)
        type(self).n += 1
        out = os.path.join(TMP, f"changed-{self.n}")
        return (*convert("--out", out, converter=converter or self.converter), out)

    @staticmethod
    def rule(src, having=None):
        """the first rule of the source (that has the member `having`)"""
        return next(r for _, r in rules(src) if having is None or having in r)

    def test_the_unchanged_source_converts_from_the_copy(self):
        code, out, err, d = self.run_on(lambda src: None)
        self.assertEqual(code, 0, err); self.assertIn("UNMAPPED: 0", out)

    def test_a_leaf_without_a_destination_is_a_failed_run(self):
        def change(src): self.rule(src)["a_member_of_a_later_publication"] = "x"
        code, out, err, d = self.run_on(change)
        self.assertEqual(code, 1, err)
        self.assertIn("UNMAPPED: 1", out)
        self.assertIn("no declared destination", err); self.assertIn("UNMAPPED = 0", err)
        report = read_json(os.path.join(d, "cr26-coverage-report.json"))      # written all the same: it lists the path
        self.assertEqual(report["totals"]["unmapped"], 1)
        self.assertEqual(report["unmapped"], [{"path": "cr26.FRR.*.data.*.*.*.a_member_of_a_later_publication", "count": 1}])
        self.assertTrue(os.path.isfile(os.path.join(d, "cr26-core-bundle", "content-manifest.json")))

    def stops(self, change, *words):
        code, out, err, d = self.run_on(change)
        self.assertNotEqual(code, 0, out)
        for w in words: self.assertIn(w, err)
        self.assertFalse(os.path.exists(d), "the run stopped and had written already")

    def test_a_fraction_where_the_kernel_has_a_number_stops_the_run(self):
        def change(src): self.rule(src, "timeframe_num")["timeframe_num"] = 0.5
        self.stops(change, "NUMBER-1", "0.5")
        def change_bound(src): self.rule(src, "timeframe_num_max")["timeframe_num_max"] = 10.5
        self.stops(change_bound, "NUMBER-1", "10.5")

    def test_an_optional_flag_other_than_true_stops_the_run(self):
        def change(src): self.rule(src, "notification")["notification"][0]["optional"] = False
        self.stops(change, "notification.optional")

    def test_an_ignore_in_terms_that_is_no_boolean_stops_the_run(self):
        def change(src): next(iter(src["FRD"]["data"]["all"].values()))["ignore_in_terms"] = "yes"
        self.stops(change, "ignore_in_terms")

    def test_a_control_link_written_twice_stops_the_run(self):
        def change(src):
            r = next(r for _, r in rules(src) if r.get("controls"))
            r["controls"].append(r["controls"][0])
        self.stops(change, "written twice")

    def test_a_rule_id_used_twice_stops_the_run(self):
        def change(src):      # one rule a second time, under a track of its family; a rule without control links,
            for fam in src["FRR"].values():      # so that the second object and not a second Mapping is what stops it
                for subset, members in fam["data"].get("all", {}).items():
                    for rid, r in members.items():
                        if not r.get("controls"):
                            fam["data"].setdefault("20x", {}).setdefault(subset, {})[rid] = copy.deepcopy(r)
                            return
        self.stops(change, "an id occurs twice")

    def test_without_the_source_the_run_says_where_to_get_it(self):
        self.stops(None, "SOURCES.sha256")

    def test_a_value_the_converter_does_not_write_is_unaccounted_and_the_run_ends_with_1(self):
        # The glossary block gets a member. The path map has a row for everything under FRD.info (glossary-info),
        # so the gate UNMAPPED = 0 is open; the converter copies six named members, and this one it does not write.
        # "A converter run with an unaccounted value exits non-zero" (author, 2026-11-14).
        def change(src): src["FRD"]["info"]["a_member_of_a_later_publication"] = "x"
        code, out, err, d = self.run_on(change)
        self.assertEqual(code, 1, out)
        self.assertIn("1 source value(s) unaccounted", err)
        self.assertIn("UNMAPPED: 0", out); self.assertIn("UNACCOUNTED", out); self.assertIn("PATH MAP CONTRADICTED", out)
        path = "cr26.FRD.info.a_member_of_a_later_publication"
        self.assertEqual(read_json(os.path.join(d, "cr26-coverage-report.json"))["ledger"]["path-map-rows-the-ledger-contradicts"],
                         [{"path": path, "level": "L1", "values": 1, "without-a-destination": 1}])
        ledger = read_json(os.path.join(d, "cr26-conversion-ledger.json"))
        self.assertIn({"path": path, "count": 1, "pointers": ["cr26#/FRD/info/a_member_of_a_later_publication"]},
                      ledger["unaccounted-paths"])
        # the run wrote all the same, and its report says this run's number, not the committed one
        self.assertEqual(ledger["totals"]["unaccounted"], 1)
        with open(os.path.join(d, "cr26-coverage-report.md"), encoding="utf-8") as f: self.assertIn("**1 unaccounted**", f.read())
        self.assertTrue(os.path.isfile(os.path.join(d, "cr26-core-bundle", "content-manifest.json")))

    def test_a_flag_the_converter_does_not_write_is_unaccounted_too(self):
        # until 2026-11-14 the ledger could not follow a flag, and a lost one looked like every carried one
        def change(src): src["FRD"]["info"]["a_flag_of_a_later_publication"] = True
        code, out, err, d = self.run_on(change)
        self.assertEqual(code, 1, out); self.assertIn("1 source value(s) unaccounted", err)

    def test_a_family_marked_placeholder_is_not_written_active(self):
        # a family the source calls stable is made a placeholder: its Set, its subset Sets, its rules and their Mappings
        # change their lifecycle with it, and nothing else does
        fk = next(k for k, f in self.original["FRR"].items() if f["info"].get("status") == "stable"
                  and any(r.get("controls") for t in f["data"].values() for sub in t.values() for r in sub.values()))
        def change(src): src["FRR"][fk]["info"]["status"] = "placeholder"
        code, out, err, d = self.run_on(change)
        self.assertEqual(code, 0, err)
        code, _, err, unchanged = self.run_on(lambda src: None)
        self.assertEqual(code, 0, err)
        new, old = objects(os.path.join(d, "cr26-core-bundle")), objects(os.path.join(unchanged, "cr26-core-bundle"))
        self.assertEqual(set(new), set(old))
        fam = self.original["FRR"][fk]
        made = {f"{NS}/set/tax/{slug(fk)}"} | {i for i in new if i.startswith(f"{NS}/set/subset/{slug(fk)}-")}
        for track in fam["data"].values():
            for subset in track.values():
                for rid, r in subset.items():
                    made.add(f"{NS}/req/{rid}"); made.update(f"{NS}/map/{slug(rid)}--{slug(c)}" for c in r.get("controls") or [])
        self.assertGreater(len([i for i in made if "/map/" in i]), 0)
        for i in new:
            if i in made: self.assertEqual((old[i]["lifecycle"], new[i]["lifecycle"]), ("active", "draft"), i)
            else: self.assertEqual(new[i]["lifecycle"], old[i]["lifecycle"], i)
        self.assertEqual(new[f"{NS}/set/tax/{slug(fk)}"]["facets"][NARR]["status"], "placeholder")

    def test_a_status_the_converter_has_no_rule_for_stops_the_run(self):
        def change(src): next(iter(src["FRR"].values()))["info"]["status"] = "retired"
        self.stops(change, "retired", "guesses at no other word")
        def change_theme(src): next(iter(src["KSI"].values()))["status"] = "retired"
        self.stops(change_theme, "retired")

    # ---- the SP 800-53 bundle the 14 carried Requirements are read from, changed in one place ----
    def run_on_changed_sp800_53(self, change):
        """-> (exit code, stdout, stderr, the --out directory) of a run on the unchanged source after change(folder)
        has changed this class's copy of the SP 800-53 bundle. The copy is put back afterwards."""
        nist = os.path.join(self.root, "converted_examples", "US.SP800-53", "sp800-53-core-bundle")
        type(self).n += 1
        kept = os.path.join(TMP, f"sp800-53-kept-{self.n}")
        shutil.copytree(nist, kept)
        try:
            change(nist)
            return self.run_on(lambda src: None)
        finally:
            shutil.rmtree(nist); shutil.copytree(kept, nist)

    @staticmethod
    def rewrite(path, change):
        with open(path, encoding="utf-8") as f: doc = json.load(f)
        change(doc)
        with open(path, "w", encoding="utf-8") as f: json.dump(doc, f, ensure_ascii=False, indent=1)

    CARRIED = "AC-6.1"         # one of the Rev 5 controls the overlay assigns a parameter of
    CARRIED_FILE = ("objects", "req", "ac-6-1.json")

    def test_a_member_the_sp800_53_bundle_adds_to_a_facet_comes_with_its_pin(self):
        # the converter wrote the pins of the carried facets from its own text until 2026-11-14; a facet that gained a
        # member in the SP 800-53 conversion would have been refused by the pin this bundle carried
        fid = NIST.rsplit("/", 1)[0] + "/facet/narrative"
        def change(nist):
            manifest = read_json(os.path.join(nist, "content-manifest.json"))
            pin = next(x for x in manifest["facet-schemas"] if x["id"] == fid)
            self.rewrite(os.path.join(nist, *pin["path"].split("/")),
                         lambda desc: desc["schema"]["properties"].update({"a-later-member": {"type": "string"}}))
            self.rewrite(os.path.join(nist, *self.CARRIED_FILE), lambda o: o["facets"][fid + "@1"].update({"a-later-member": "x"}))
        code, out, err, d = self.run_on_changed_sp800_53(change)
        self.assertEqual(code, 0, err)
        bundle = os.path.join(d, "cr26-core-bundle")
        self.assertEqual(objects(bundle)[f"{NIST}/{self.CARRIED}"]["facets"][fid + "@1"]["a-later-member"], "x")
        pin = next(x for x in read_json(os.path.join(bundle, "content-manifest.json"))["facet-schemas"] if x["id"] == fid)
        self.assertIn("a-later-member", read_json(os.path.join(bundle, *pin["path"].split("/")))["schema"]["properties"])

    def test_a_carried_requirement_that_uses_the_compat_facet_is_held_to_the_one_schema(self):
        # since 2026-11-14 every converter of the repository pins one compat schema (1.1.0); until then this converter
        # merged its own compat schema with the one a carried Requirement brought
        def change(nist):
            self.rewrite(os.path.join(nist, *self.CARRIED_FILE), lambda o: o["facets"].update({COMPAT: {"uuid": "x"}}))
        code, out, err, d = self.run_on_changed_sp800_53(change)
        self.assertEqual(code, 0, err)
        bundle = os.path.join(d, "cr26-core-bundle")
        pins = [x for x in read_json(os.path.join(bundle, "content-manifest.json"))["facet-schemas"] if x["id"] == COMPAT.rsplit("@", 1)[0]]
        self.assertEqual([(x["exact-version"], x["path"]) for x in pins], [("1.1.0", "schemas/oscal-1x-compat-1.1.0.json")], "one facet, one pin")
        self.assertEqual(objects(bundle)[f"{NIST}/{self.CARRIED}"]["facets"][COMPAT], {"uuid": "x"})

    def test_a_compat_schema_of_another_kind_in_the_sp800_53_bundle_stops_the_run(self):
        def change(nist):
            self.rewrite(os.path.join(nist, "schemas", "oscal-1x-compat-1.1.0.json"),
                         lambda sc: sc["schema"]["properties"].update({"labels": {"type": "object"}}))
            self.rewrite(os.path.join(nist, *self.CARRIED_FILE), lambda o: o["facets"].update({COMPAT: {"labels": {"formal": "x"}}}))
        code, out, err, d = self.run_on_changed_sp800_53(change)
        self.assertNotEqual(code, 0)
        self.assertIn("pins a compat schema that is not the one schema of this repository's converters", err)

    def test_a_carried_requirement_with_a_facet_nobody_pins_stops_the_run(self):
        def change(nist):
            self.rewrite(os.path.join(nist, *self.CARRIED_FILE),
                         lambda o: o["facets"].update({NIST.rsplit("/", 1)[0] + "/facet/of-a-later-conversion@1": {"x": "y"}}))
        code, out, err, d = self.run_on_changed_sp800_53(change)
        self.assertNotEqual(code, 0, out)
        self.assertIn("pins no schema for it", err)
        self.assertFalse(os.path.exists(d), "the run stopped and had written already")

    def test_a_claim_of_the_ledger_that_does_not_hold_is_a_failed_run(self):
        # The ledger reads every file back. Here the converter is made to write another modality into the files
        # than the one it holds: the rule "modality from the force word" then gives `must` and the file says `should`.
        with open(self.converter, encoding="utf-8") as f: text = f.read()
        writes = 'f.write(json.dumps(o,indent=1,ensure_ascii=False)+"\\n")'
        self.assertEqual(text.count(writes), 1, "the line that writes an object is not where this test changes it")
        changed = os.path.join(os.path.dirname(self.converter), "convert_cr26_writes_another_value.py")
        with open(changed, "w", encoding="utf-8") as f:
            f.write(text.replace(writes, 'f.write(json.dumps(o,indent=1,ensure_ascii=False).replace(\'"must"\',\'"should"\')+"\\n")'))
        code, out, err, d = self.run_on(lambda src: None, converter=changed)
        self.assertEqual(code, 1, err)
        self.assertIn("claim(s) that do not hold", err)
        self.assertIn("LEDGER CLAIMS THAT DO NOT HOLD", out)
        ledger = read_json(os.path.join(d, "cr26-conversion-ledger.json"))        # written all the same: it says which claims
        musts = sum(1 for _, r in rules(self.original) if r.get("force") == "MUST")
        self.assertGreater(musts, 0)
        self.assertGreaterEqual(len(ledger["verification-failures"]), musts)
        self.assertEqual(read_json(os.path.join(d, "cr26-coverage-report.json"))["ledger"]["verification-failures"],
                         len(ledger["verification-failures"]))


if __name__ == "__main__":
    if not os.path.isfile(SOURCE):
        sys.stderr.write(f"NOT RUN: {SOURCE} is missing. The source is not in the repository; "
                         f"converted_examples/FedRAMP-CR26/SOURCES.sha256 says where to get it.\n")
        sys.exit(2)
    with tempfile.TemporaryDirectory() as TMP:
        unittest.main()
