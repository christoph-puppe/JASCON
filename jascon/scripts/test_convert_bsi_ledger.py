#!/usr/bin/env python3
"""The conversion ledger of convert_bsi.py (backlog #41), and what the author
asked of the Grundschutz++ conversion on 2026-11-14, held on a small
catalogue nobody published, in the shape of Grundschutz++.

    python3 jascon/scripts/test_convert_bsi_ledger.py

What the pinned source gives is held elsewhere: the Validators workflow
converts it again and compares the bundle, the two reports and the ledger
record byte for byte. Here:
  - every control is a Requirement of its own, at every depth, with its own
    statement, parameters, props and links; a control that has nested
    controls gives a Set that lists its own Requirement first and then what
    stands for each nested control; no relation is written between a
    control and the controls nested in it;
  - every source value is carried or is no content by a rule the ledger
    checks (the id of a part, the name `statement`, the namespace of a
    prop), 0 are unaccounted, and the document metadata stands on the root
    Set as the source holds it;
  - what the pinned source never has, and the mapping does not read, is
    carried all the same: a prop it does not know, a prop in another
    namespace, a name that repeats, a part of another name, a part id the
    rule does not give, a second value of a parameter, a member OSCAL
    allows and this catalogue does not use;
  - a run ends with a non-zero exit code when a value is lost, when a rule
    of what is no content does not hold, when a name selects a value that
    is not written, and on every other defect put into a copy of the
    converter below. Each change names the text it replaces and fails
    loudly if that text is no longer there.

Standard library only."""
import ast, collections, json, os, shutil, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
NS = "https://ns.bsi.bund.de/gspp"
CSV = "https://github.com/BSI-Bund/Stand-der-Technik-Bibliothek/tree/main/Dokumentation/namespaces/"
COMPAT = "https://ns.jascon.net/compat/oscal-1x@1"
TAX = "https://ns.bsi.bund.de/facet/gspp-taxonomy@1"
NARR = "https://ns.bsi.bund.de/facet/gspp-narrative@1"
RES_A, RES_B = "aaaaaaaa-0000-4000-8000-000000000001", "bbbbbbbb-0000-4000-8000-000000000002"
PARTY = "cccccccc-0000-4000-8000-000000000003"
C = "gspp.catalog.groups[].groups[].controls[]"


def prop(name, value, csv=None):
    p = {"name": name}
    if csv: p["ns"] = CSV + csv
    p["value"] = value
    return p

def control(cid, title, level="normal-SdT", prose=None, **more):
    """a control as Grundschutz++ writes one: an alt-identifier, a security
    and an effort level, the four objectives, a statement part with the
    sentence template in its props, and a guidance part"""
    c = {"id": cid, "class": "BSI-Methodik", "title": title}
    c.update({k: v for k, v in more.items() if k == "params"})
    c["props"] = [prop("alt-identifier", f"uuid-of-{cid}"), prop("sec_level", level, "security_level.csv"),
                  prop("effort_level", "2", "effort_level.csv"), prop("tags", "Eins, Zwei", "tags.csv"),
                  prop("confidentiality", "1", "security_targets.csv"), prop("integrity", "0", "security_targets.csv"),
                  prop("availability", "0", "security_targets.csv"), prop("authenticity", "1", "security_targets.csv"),
                  prop("threats", "G 0.14, G 0.15", "basethreats.csv")]
    c["parts"] = [{"id": f"{cid}_stm", "name": "statement",
                   "props": [prop("documentation", "Regelwerk", "documentation_guidelines.csv"),
                             prop("result", "ein Ergebnis", "result.csv"), prop("action_word", "regeln", "action_words.csv"),
                             prop("modal_verb", "MUSS", "modal_verbs.csv"),
                             prop("target_object_categories", "Server, Clients", "target_object_categories.csv")],
                   "prose": prose or f"Die Praktik MUSS regeln, was {cid} verlangt."},
                  {"id": f"{cid}_gdn", "name": "guidance", "prose": f"Ein Hinweis zu {cid}."}]
    c.update({k: v for k, v in more.items() if k in ("links", "controls")})
    return c

def catalogue():
    """One practice with one section and five controls: PR.1.1 has two
    nested controls, and the second of them has one of its own; PR.1.2 has
    none. Links: one on a top-level control, three on nested controls, and
    on PR.1.2 one to a back-matter resource and one to another address.
    The metadata names its creator and links to the other resource."""
    return {"catalog": {
        "uuid": "00000000-0000-4000-8000-00000000000a",
        "metadata": {
            "title": "Ein erfundener Katalog", "last-modified": "2026-11-14T08:00:00.000Z", "version": "2026-11-14",
            "oscal-version": "1.1.3",
            "props": [{"name": "keywords", "value": "erfunden"},
                      {"name": "scope_implements_norm", "ns": "http://csrc.nist.gov/ns/oscal/1.0", "value": "keine Norm"}],
            "links": [{"href": f"#{RES_A}", "rel": "reference", "text": "Ein anderes Werk"}],
            "roles": [{"id": "creator", "title": "Creator"}],
            "parties": [{"uuid": PARTY, "type": "organization", "name": "Niemand e. V.", "email-addresses": ["niemand@example.org"]}],
            "responsible-parties": [{"role-id": "creator", "party-uuids": [PARTY]}],
            "remarks": "Ein Katalog, den niemand herausgegeben hat."},
        "groups": [{"id": "PR", "title": "Eine Praktik",
                    "props": [{"name": "label", "value": "PR", "remarks": "Was die Praktik soll."}, prop("alt-identifier", "uuid-of-PR")],
                    "groups": [{"id": "PR.1", "title": "Ein Abschnitt",
                                "props": [prop("label", "1"), prop("alt-identifier", "uuid-of-PR.1")],
                                "controls": [
            control("PR.1.1", "Die erste Anforderung",
                    prose="Die Praktik MUSS nach {{ insert: param, pr.1.1-prm1 }} regeln, was PR.1.1 verlangt.",
                    params=[{"id": "pr.1.1-prm1", "props": [prop("alt-identifier", "uuid-of-prm")], "label": "ein Standard"}],
                    links=[{"href": "#PR.1.2", "rel": "related"}],
                    controls=[
                        control("PR.1.1.1", "Die erste eingebettete", level="erhöht",
                                links=[{"href": "#PR.1.1", "rel": "required"}, {"href": "#PR.1.2", "rel": "related"}]),
                        control("PR.1.1.2", "Die zweite eingebettete",
                                controls=[control("PR.1.1.2.1", "Die tief eingebettete", level="erhöht",
                                                  links=[{"href": "#PR.1.1.2", "rel": "related"}])])]),
            control("PR.1.2", "Die zweite Anforderung",
                    links=[{"href": f"#{RES_B}", "rel": "reference"}, {"href": "https://example.org/anderswo", "rel": "related"}])]}]}],
        "back-matter": {"resources": [
            {"uuid": RES_A, "title": "Ein anderes Werk", "rlinks": [{"href": "https://example.org/werk", "hashes": [{"algorithm": "SHA-256", "value": "00ff"}]}]},
            {"uuid": RES_B, "title": "Ein benanntes Werk", "rlinks": [{"href": "https://example.org/benannt"}]}]}}}

def controls_of(doc):
    """-> [(control, depth, parent or None)] in document order"""
    out = []
    def of(cs, depth, parent):
        for c in cs or []: out.append((c, depth, parent)); of(c.get("controls"), depth + 1, c)
    def groups(gs):
        for g in gs or []: of(g.get("controls"), 0, None); groups(g.get("groups"))
    groups(doc["catalog"]["groups"])
    return out

def odd_catalogue():
    """The catalogue above with what the pinned source never has. Nothing of
    it is read by the mapping, and nothing of it may be lost."""
    doc = catalogue()
    cs = {c["id"]: c for c, _, _ in controls_of(doc)}
    a, b = cs["PR.1.1"], cs["PR.1.2"]
    b["props"] += [{"name": "marking", "value": "intern"},                                  # a prop the mapping does not know
                   {"name": "tags", "ns": "https://example.org/andere-liste", "value": "Fremd"},    # a known name in another namespace
                   prop("tags", "Drei", "tags.csv"),                                         # the name repeats: this one is read
                   {"name": "integrity", "ns": CSV + "security_targets.csv", "value": "1", "remarks": "neu bewertet"}]   # read, and says more
    b["parts"][0]["id"] = "PR.1.2_smt"                                                       # an id the rule does not give
    b["parts"][0]["props"] += [{"name": "note", "value": "nur hier"}]                        # a part prop the mapping does not know
    next(p for p in b["parts"][0]["props"] if p["name"] == "modal_verb")["value"] = "WIRD"   # a verb outside the code map
    b["parts"][1]["props"] = [{"name": "status", "value": "Entwurf"}]                        # props on the guidance part
    b["parts"].append({"id": "PR.1.2_obj", "name": "objective", "prose": "Ein Ziel.", "props": [{"name": "method", "value": "TEST"}]})
    b["links"].append({"href": "#PR.1.1", "rel": "related", "text": "siehe dort"})           # a link that says more than rel and href
    b["remarks"] = "Eine Bemerkung an der Anforderung."                                      # a member of a control the mapping does not read
    b["x-reviewed"] = True; b["x-weight"] = 0.5                                              # a boolean and a fraction
    a["params"][0]["values"] = ["ein Standard", "ein anderer Standard"]                      # two values: `default` holds one
    a["params"][0]["remarks"] = "Zur Wahl."; a["params"][0]["props"].append({"name": "usage", "value": "frei"})
    g = doc["catalog"]["groups"][0]
    g["class"] = "practice"                                                                  # a member of a group
    g["props"] += [{"name": "sort-id", "value": "01"}, {"name": "label", "value": "PR (neu)"}]    # a prop it does not know; the label repeats
    doc["catalog"]["params"] = [{"id": "allgemein", "label": "ein Wert für alle"}]           # a member of the catalogue
    doc["catalog"]["groups"].append({"id": "LEER", "title": "Eine leere Praktik", "props": [prop("label", "LEER")]})   # a group that holds nothing
    doc["catalog"]["controls"] = [control("X.1", "Eine Anforderung ohne Gruppe")]            # a control that stands in no group
    return doc


class TheGrundschutzConverter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="jascon-bsi-ledger-")
        cls.n = 0
        cls.plain = cls.convert(catalogue())
        cls.odd = cls.convert(odd_catalogue())

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    @classmethod
    def convert(cls, source, changes=(), before=None):
        """Runs a copy of the converter on `source`. changes: (text of the
        converter, what stands in its place). before(out): called before the
        run. -> {done, out, ledger, report, objects}: the record, the JSON
        report and the objects of the bundle by id, read from disk (None or
        empty where a file is not there)."""
        cls.n += 1
        tree = os.path.join(cls.tmp, str(cls.n))
        scripts = os.path.join(tree, "jascon", "scripts"); os.makedirs(scripts)
        os.makedirs(os.path.join(tree, "sources"))
        with open(os.path.join(tree, "sources", "Grundschutz++-catalog.json"), "w", encoding="utf-8") as f: json.dump(source, f, ensure_ascii=False)
        shutil.copy(os.path.join(HERE, "oscal_conv_lib.py"), scripts)
        shutil.copytree(os.path.join(HERE, "..", "schemas", "stdlib"), os.path.join(tree, "jascon", "schemas", "stdlib"))
        with open(os.path.join(HERE, "convert_bsi.py"), encoding="utf-8") as f: code = f.read()
        for old, new in changes:
            if code.count(old) != 1:
                raise AssertionError(f"convert_bsi.py holds this text {code.count(old)} times, the test changes it once: {old!r}")
            code = code.replace(old, new)
        with open(os.path.join(scripts, "convert_bsi.py"), "w", encoding="utf-8") as f: f.write(code)
        out = os.path.join(tree, "out")
        if before: before(out)
        done = subprocess.run([sys.executable, os.path.join(scripts, "convert_bsi.py"), "--out", out], capture_output=True, text=True)
        def read(fn):
            p = os.path.join(out, fn)
            if not os.path.exists(p): return None
            with open(p, encoding="utf-8") as f: return json.load(f)
        objects = {}
        for base, _, files in os.walk(os.path.join(out, "bsi-core-bundle", "objects")):
            for fn in files:
                with open(os.path.join(base, fn), encoding="utf-8") as f: o = json.load(f)
                objects[o["id"]] = o
        return {"done": done, "out": out, "ledger": read("bsi-conversion-ledger.json"), "report": read("bsi-coverage-report.json"),
                "manifest": read(os.path.join("bsi-core-bundle", "content-manifest.json")), "objects": objects}

    @staticmethod
    def rows(run):
        return {(r["path"], r["outcome"]): r for r in run["ledger"]["paths"]}

    @staticmethod
    def req(run, cid): return run["objects"][f"{NS}/req/{cid}"]

    # ---------------- the ledger: nothing unaccounted, nothing false ----------------
    def test_every_value_is_carried_or_no_content_by_a_checked_rule(self):
        for run in (self.plain, self.odd):
            self.assertEqual(run["done"].returncode, 0, run["done"].stderr[-800:])
            led, rep = run["ledger"], run["report"]["ledger"]
            self.assertEqual(led["verification-failures"], [])
            self.assertEqual(led["totals"]["unaccounted"], 0)
            self.assertEqual(led["unaccounted-paths"], [])
            self.assertEqual(sorted(led["totals"]), ["copied", "intentionally-dropped", "not-content", "transformed", "unaccounted"])
            self.assertEqual(sum(led["totals"].values()), led["leaf-values"])
            self.assertEqual(sum(r["count"] for r in led["paths"]), led["leaf-values"])
            self.assertEqual(rep["totals"], led["totals"])
            self.assertEqual(rep["wiring-checks-failed"], [])
            self.assertEqual(rep["path-map-against-ledger"]["values-whose-outcome-the-map-does-not-allow"], 0)
            self.assertEqual(rep["path-map-against-ledger"]["values-at-a-place-the-map-does-not-name"], 0)
            self.assertEqual(run["report"]["totals"]["unmapped"], 0)

    def test_the_three_classes_of_no_content_and_their_rules(self):
        rows, n = self.rows(self.plain), len(controls_of(catalogue()))
        def rule(path): return [(x["kind"], x["rule"], x["count"]) for r in self.plain["ledger"]["paths"]
                                if r["path"].endswith(path) and r["outcome"] == "not-content" for x in r["rules"]]
        ids = rule(".parts[].id")
        self.assertEqual(sum(c for k, r, c in ids if k == "rebuilt-id" and "_stm" in r), n, "the id of each statement part")
        self.assertEqual(sum(c for k, r, c in ids if k == "rebuilt-id" and "_gdn" in r), n, "the id of each guidance part")
        names = rule(".parts[].name")
        self.assertEqual((sum(c for _, _, c in names), {k for k, _, _ in names}), (n, {"selector"}), "the name `statement`, not `guidance`")
        ns = rule(".parts[].props[].ns") + rule(".controls[].props[].ns")
        self.assertEqual((sum(c for _, _, c in ns), {k for k, _, _ in ns}), (n * 5 + n * 8, {"namespace"}))
        self.assertEqual(self.plain["ledger"]["totals"]["not-content"], n * 2 + n + n * 13)
        listed = {(x["kind"], x["rule"]): x["source-values"] for x in self.plain["report"]["ledger"]["not-content"]}
        self.assertEqual(sum(listed.values()), self.plain["ledger"]["totals"]["not-content"], "the report lists every rule with its count")
        # the name `guidance` is the key of the narrative payload: carried
        self.assertEqual(sum(r["count"] for (p, o), r in rows.items() if p.endswith(".parts[].name") and o == "copied"), n)

    def test_the_declared_drops_that_remain_are_the_two_of_before_and_no_other(self):
        dropped = {(d["path"], d["count"]) for d in self.plain["report"]["ledger"]["declared-drops"]}
        self.assertEqual(dropped, {("gspp.catalog.uuid", 1), ("gspp.catalog.back-matter.resources[].uuid", 1),
                                   ("gspp.catalog.back-matter.resources[].title", 1),
                                   ("gspp.catalog.back-matter.resources[].rlinks[].href", 1),
                                   ("gspp.catalog.back-matter.resources[].rlinks[].hashes[].algorithm", 1),
                                   ("gspp.catalog.back-matter.resources[].rlinks[].hashes[].value", 1)})
        for d in self.plain["report"]["ledger"]["declared-drops"]:
            self.assertTrue(d["reason"].startswith("as decided for IFA on 2026-11-13: "), d)
            self.assertTrue(d["reading"].startswith("content"), "the reading is given, the decision is the author's")
            self.assertIn("example-value", d)
        self.assertEqual(self.plain["ledger"]["totals"]["intentionally-dropped"], 6)
        with open(os.path.join(HERE, "convert_bsi.py"), encoding="utf-8") as f: code = f.read()
        self.assertEqual((code.count("led.drop("), code.count("led.drop_value(")), (1, 1), "no drop is added to the two that were declared")

    def test_the_gate_is_the_last_statement_of_the_converter(self):
        with open(os.path.join(HERE, "convert_bsi.py"), encoding="utf-8") as f: tree = ast.parse(f.read())
        self.assertEqual(ast.unparse(tree.body[-1]), "ledger_gate(LEDGER, 'convert_bsi.py')")

    # ---------------- a nested control is a full control ----------------
    def test_every_control_at_every_depth_is_a_requirement_of_its_own(self):
        run, src = self.plain, controls_of(catalogue())
        reqs = {i: o for i, o in run["objects"].items() if "statements" in o}
        self.assertEqual(sorted(reqs), sorted(f"{NS}/req/{c['id']}" for c, _, _ in src))
        self.assertEqual(len(reqs), 5)
        for c, depth, _ in src:
            r = self.req(run, c["id"])
            self.assertEqual([s["id"] for s in r["statements"]], ["smt"], "one statement, its own")
            self.assertEqual((r["label"], r["title"]), (c["id"], {"de": c["title"]}))
            self.assertEqual(r["aliases"], [{"scheme": "bsi-uuid", "value": f"uuid-of-{c['id']}"}])
            self.assertIn(c["id"], r["statements"][0]["prose"]["de"], "its own prose, not its parent's")
            tax = r["facets"][TAX]["by-statement"]
            self.assertEqual(list(tax), ["smt"])
            self.assertEqual(tax["smt"]["sec-level"], next(p["value"] for p in c["props"] if p["name"] == "sec_level"))
            self.assertNotIn("title", tax["smt"]); self.assertNotIn("alt-identifier", tax["smt"])
            self.assertEqual(r["facets"][NARR]["by-statement"]["smt"]["guidance"], {"de": f"Ein Hinweis zu {c['id']}."})
        deep = self.req(run, "PR.1.1.2.1")
        self.assertEqual(deep["statements"][0]["modality"], "must")
        self.assertEqual(self.req(run, "PR.1.1")["statements"][0]["parameters"],
                         [{"name": "pr.1.1-prm1", "type": "string", "label": "ein Standard"}])
        self.assertEqual(run["report"]["objects"], {"requirements": 5, "statements": 5, "sets": 7, "total": 12, "sets-of-a-group": 2,
                                                    "sets-of-a-control-with-nested-controls": 2, "baseline-sets": 2, "root-sets": 1})

    def test_the_links_of_a_nested_control_are_relations_of_its_own_requirement(self):
        run, src = self.plain, controls_of(catalogue())
        for c, depth, _ in src:
            want = [{"type": l["rel"], "ref": ("https://example.org/benannt" if l["href"] == f"#{RES_B}" else
                                               f"{NS}/req/{l['href'][1:]}" if l["href"].startswith("#") else l["href"])}
                    for l in c.get("links", [])]
            self.assertEqual(self.req(run, c["id"]).get("relations", []), want, c["id"])
        relations = [r for o in run["objects"].values() for r in o.get("relations", [])]
        self.assertEqual(len(relations), 6)
        self.assertEqual(len(relations), sum(len(c.get("links", [])) for c, _, _ in src), "a relation for a link, and for nothing else")
        self.assertEqual([r["ref"] for r in relations if r["ref"].startswith(NS + "/") and r["ref"] not in run["objects"]], [],
                         "no relation names an id that is no object of the bundle")
        back = run["report"]["ledger"]["bundle-read-back"]
        self.assertEqual((back["links"], back["links-of-nested-controls"], back["links-that-are-a-relation-of-their-own-requirement"],
                          back["relations"], back["relations-that-name-no-object"]), (6, 3, 6, 6, 0))

    def test_nesting_is_carried_as_grouping_and_as_nothing_else(self):
        run = self.plain
        def members(set_id): return [m["ref"] for m in run["objects"][set_id]["members"]]
        outer, inner = run["objects"][f"{NS}/set/tax/pr-1-1"], run["objects"][f"{NS}/set/tax/pr-1-1-2"]
        self.assertEqual(outer["title"], {"de": "Die erste Anforderung"}, "titled as the control")
        self.assertEqual(members(outer["id"]), [f"{NS}/req/PR.1.1", f"{NS}/req/PR.1.1.1", f"{NS}/set/tax/pr-1-1-2"],
                         "its own Requirement first, then what stands for each nested control")
        self.assertEqual(members(inner["id"]), [f"{NS}/req/PR.1.1.2", f"{NS}/req/PR.1.1.2.1"])
        self.assertEqual(members(f"{NS}/set/tax/pr-1"), [f"{NS}/set/tax/pr-1-1", f"{NS}/req/PR.1.2"],
                         "in the Set of the group the grouping Set stands where the control stood")
        self.assertEqual(members(f"{NS}/set/tax/pr"), [f"{NS}/set/tax/pr-1"])
        self.assertEqual(members(f"{NS}/set/tax/root"), [f"{NS}/set/tax/pr"])
        for o in (outer, inner):
            self.assertEqual(sorted(o), ["id", "lifecycle", "members", "title", "version"], "a grouping, and nothing else")
            self.assertEqual([m["sequence"] for m in o["members"]], sorted(m["sequence"] for m in o["members"]))
        # every Requirement and every Set but the root is listed in exactly one taxonomy Set
        listed = collections.Counter(m["ref"] for i, o in run["objects"].items() if "/set/tax/" in i for m in o["members"])
        for i in run["objects"]:
            if "/set/baseline/" in i: continue
            self.assertEqual(listed[i], 0 if i.endswith("/set/tax/root") else 1, i)
        # no relation between a control and the controls nested in it, but the one the source states itself
        self.assertEqual(self.req(run, "PR.1.1").get("relations"), [{"type": "related", "ref": f"{NS}/req/PR.1.2"}])
        self.assertNotIn("relations", self.req(run, "PR.1.1.2"))
        self.assertEqual(self.req(run, "PR.1.1.1")["relations"][0], {"type": "required", "ref": f"{NS}/req/PR.1.1"},
                         "the link the source wrote from a nested control to its parent is carried as the source's link")

    def test_a_baseline_lists_every_control_of_its_level_nested_ones_too(self):
        run = self.plain
        def members(level): return [m["ref"].rsplit("/", 1)[1] for m in run["objects"][f"{NS}/set/baseline/{level}"]["members"]]
        self.assertEqual(members("normal-sdt"), ["PR.1.1", "PR.1.1.2", "PR.1.2"])
        self.assertEqual(members("erh-ht"), ["PR.1.1.1", "PR.1.1.2.1"])

    # ---------------- the document metadata ----------------
    def test_the_document_metadata_stands_on_the_root_set_as_the_source_holds_it(self):
        run, meta = self.plain, catalogue()["catalog"]["metadata"]
        root = run["objects"][f"{NS}/set/tax/root"]
        self.assertEqual(root["title"], {"de": meta["title"]}); self.assertEqual(root["version"], meta["version"])
        self.assertEqual(root["facets"][COMPAT]["metadata"], {k: v for k, v in meta.items() if k not in ("title", "version")})
        self.assertEqual(list(root["facets"][COMPAT]), ["metadata", "back-matter"])
        source = run["manifest"]["provenance"]["sources"][0]
        self.assertEqual(source, {"key": "gspp", "title": meta["title"], "version": meta["version"], "oscal-version": "1.1.3",
                                  "author-ref": f"{NS}/party/niemand-e-v", "date": "2026-11-14"})
        rows = self.rows(run)
        for (path, outcome), r in rows.items():
            if ".catalog.metadata." in path: self.assertEqual(outcome, "copied", path)
        self.assertEqual(sum(r["count"] for (p, _), r in rows.items() if ".catalog.metadata." in p), 21)

    def test_a_document_that_names_no_author_and_no_day_gets_none(self):
        doc = catalogue()
        for k in ("parties", "responsible-parties", "roles"): del doc["catalog"]["metadata"][k]
        doc["catalog"]["metadata"]["last-modified"] = "irgendwann"
        run = self.convert(doc)
        self.assertEqual(run["done"].returncode, 0, run["done"].stderr[-600:])
        self.assertEqual(sorted(run["manifest"]["provenance"]["sources"][0]), ["key", "oscal-version", "title", "version"],
                         "a missing value is a line of the report at most, never a refusal, and nothing is made up")
        self.assertEqual(run["objects"][f"{NS}/set/tax/root"]["facets"][COMPAT]["metadata"]["last-modified"], "irgendwann")

    def test_a_resource_a_link_names_is_carried_and_the_other_stays_a_declared_drop(self):
        run = self.plain
        root = run["objects"][f"{NS}/set/tax/root"]
        self.assertEqual(root["facets"][COMPAT]["back-matter"],
                         {"resources": [{"uuid": RES_B, "title": "Ein benanntes Werk", "rlinks": [{"href": "https://example.org/benannt"}]}]})
        self.assertEqual(self.req(run, "PR.1.2")["relations"][0], {"type": "reference", "ref": "https://example.org/benannt"})

    # ---------------- what the mapping does not read is carried ----------------
    def test_what_the_mapping_does_not_read_is_carried_as_the_source_holds_it(self):
        run, src = self.odd, odd_catalogue()
        cs = {c["id"]: c for c, _, _ in controls_of(src)}
        b, a = self.req(run, "PR.1.2"), self.req(run, "PR.1.1")
        compat = b["facets"][COMPAT]
        self.assertEqual(list(compat), ["props", "parts", "links", "control"])
        self.assertEqual(compat["props"], [cs["PR.1.2"]["props"][i] for i in (3, 5, 9, 10, 12)],
                         "the earlier `tags`, the earlier `integrity`, the unknown prop, the one in another namespace, the one that says more")
        tax = b["facets"][TAX]["by-statement"]["smt"]
        self.assertEqual(tax["tags"], ["Drei"], "of a name that repeats the last one is read")
        stm, gdn, obj = cs["PR.1.2"]["parts"]
        self.assertEqual(compat["parts"], [
            {"id": "PR.1.2_smt", "name": "statement", "props": [stm["props"][5], stm["props"][3]]},   # the unknown prop, the unknown verb
            {"name": "guidance", "props": gdn["props"]},
            obj])
        self.assertEqual(b["statements"][0]["modality"], "unspecified")
        self.assertEqual(run["report"]["unknown-modal-verbs"], {"WIRD": 1})
        self.assertEqual(compat["links"], [{"href": "#PR.1.1", "rel": "related", "text": "siehe dort"}])
        self.assertEqual(b["relations"][-1], {"type": "related", "ref": f"{NS}/req/PR.1.1"})
        self.assertEqual(compat["control"], {"remarks": "Eine Bemerkung an der Anforderung.", "x-reviewed": True, "x-weight": "0.5"},
                         "as the source holds it; a fraction as a decimal string, because a kernel number is an integer (NUMBER-1)")
        extras = a["facets"][COMPAT]["param-extras"]["pr.1.1-prm1"]
        self.assertEqual(extras, {"alt-identifier": "uuid-of-prm", "values": ["ein Standard", "ein anderer Standard"],
                                  "props": [{"name": "usage", "value": "frei"}], "remarks": "Zur Wahl."})
        self.assertEqual(a["statements"][0]["parameters"][0]["default"], "ein Standard")
        group = run["objects"][f"{NS}/set/tax/pr"]
        self.assertEqual(group["label"], "PR (neu)")
        self.assertEqual(group["facets"][COMPAT], {"props": [src["catalog"]["groups"][0]["props"][0], {"name": "sort-id", "value": "01"}],
                                                   "group": {"class": "practice"}})
        root = run["objects"][f"{NS}/set/tax/root"]
        self.assertEqual(root["facets"][COMPAT]["catalog"], {"params": [{"id": "allgemein", "label": "ein Wert für alle"}]})
        self.assertEqual([m["ref"] for m in root["members"]], [f"{NS}/set/tax/pr", f"{NS}/set/tax/leer", f"{NS}/req/X.1"],
                         "a group that holds nothing is a Set all the same, and a control in no group is listed by the root")
        empty = run["objects"][f"{NS}/set/tax/leer"]
        self.assertEqual((empty["members"], empty["label"], empty["title"]), ([], "LEER", {"de": "Eine leere Praktik"}))
        self.assertEqual(self.req(run, "X.1")["statements"][0]["prose"], {"de": "Die Praktik MUSS regeln, was X.1 verlangt."})
        rows = self.rows(run)
        self.assertEqual(rows[(C + ".x-reviewed", "copied")]["count"], 1, "a boolean is followed to where it stands")
        self.assertEqual([t.get("rule", "")[:44] for t in rows[(C + ".x-weight", "transformed")]["to"]],
                         ["a number that is no integer, written as a de"])
        self.assertEqual(rows[(C + ".parts[].id", "copied")]["count"], 2, "the id the rule does not give, and the id of the part it does not read")
        self.assertEqual(run["report"]["ledger"]["carried-as-the-source-holds-it"],
                         {"catalog": 1, "back-matter": 1, "control": 1, "group": 1, "links": 1, "metadata": 1,
                          "param-extras beyond the alt-identifier": 1, "parts": 1, "props": 2})

    # ---------------- deliberate defects: each ends the run with a non-zero exit code ----------------
    def refused(self, changes, *words, source=None, before=None):
        run = self.convert(source or catalogue(), changes, before)
        self.assertNotEqual(run["done"].returncode, 0, "the run went through: " + run["done"].stdout[-300:])
        for w in words: self.assertIn(w, run["done"].stderr)
        self.assertIsNotNone(run["report"], "the reports are written before the run ends, so that it says why")
        return run

    CLASS = ('tx=by(F_TAX); tx["class"]=c.get("class")', 'tx=by(F_TAX)')

    def test_defect_a_value_that_is_lost_ends_the_run(self):
        run = self.refused([self.CLASS], "LEDGER UNACCOUNTED", "5 source value(s) unaccounted")
        self.assertEqual(run["done"].returncode, 1)
        self.assertEqual(run["ledger"]["totals"]["unaccounted"], 5)
        self.assertEqual({u["path"].rsplit(".", 1)[1] for u in run["ledger"]["unaccounted-paths"]}, {"class"},
                         "the record of the failed run names what is lost")

    def test_defect_a_rule_that_does_not_give_the_id_ends_the_run(self):
        run = self.refused([('led.rebuilt(part["id"],N_STM_ID,stm_id,c["id"])', 'led.rebuilt(part["id"],N_STM_ID,gdn_id,c["id"])')],
                           "LEDGER CHECK FAILED", '"claim": "rebuilt-id"', "5 claim(s) that do not hold")
        self.assertEqual(len(run["ledger"]["verification-failures"]), 5)
        self.assertEqual(run["ledger"]["totals"]["unaccounted"], 5, "an id the rule does not give is not covered by it")

    def test_defect_a_name_that_selects_a_value_which_is_not_written_ends_the_run(self):
        run = self.refused([('"prose":{"de":prose}}', '"prose":{"de":"ein anderer Text"}}')], "LEDGER UNACCOUNTED")
        rows = self.rows(run)
        self.assertEqual(sum(r["count"] for (p, o), r in rows.items() if p.endswith(".parts[].prose") and o == "unaccounted"), 5)
        names = [r for (p, o), r in rows.items() if p.endswith(".parts[].name") and o == "unaccounted"]
        self.assertEqual(sum(r["count"] for r in names), 5, "the name `statement` selected a prose that is not in the bundle: it shares its fate")
        self.assertEqual(run["ledger"]["verification-failures"], [], "nothing claimed was false; the values are simply not there")

    def test_defect_a_namespace_the_mapping_is_not_written_for_ends_the_run(self):
        run = self.refused([('led.namespace(p["ns"],N_NS,[PROP_NS[p["name"]]],p["name"])',
                             'led.namespace(p["ns"],N_NS,[CSV+"tags.csv"],p["name"])')], '"claim": "namespace"')
        self.assertEqual(len(run["ledger"]["verification-failures"]), 5 * 12, "every namespace but that of `tags`")

    def test_defect_a_nested_control_that_is_no_requirement_ends_the_run(self):
        self.refused([("        for ch in nested:\n", "        for ch in []:\n")], "LEDGER WIRING the source has 5 controls and the bundle 2 Requirements")

    def test_defect_links_that_are_not_carried_end_the_run(self):
        self.refused([('    for l in c.get("links",[]) or []:\n        href=l.get("href","")', '    for l in []:\n        href=l.get("href","")')],
                     "6 link(s) of a control are no relation of that control's own Requirement", "LEDGER UNACCOUNTED")

    def test_defect_a_relation_between_a_nested_control_and_its_parent_ends_the_run(self):
        self.refused([('            members.append({"ref":ref,"sequence":nseq()})',
                       '            members.append({"ref":ref,"sequence":nseq()}); req.setdefault("relations",[]).append({"type":"required","ref":ref})')],
                     "a relation was written that no link states")

    def test_defect_a_drop_that_is_added_ends_the_run(self):
        run = self.refused([self.CLASS, ('for pattern,reason,_ in DROPS:\n', 'led.drop(r"\\.class$","not needed")\nfor pattern,reason,_ in DROPS:\n')],
                           "LEDGER WIRING a value is dropped for a reason that DROPS does not hold",
                           "are intentionally-dropped, and the path map allows copied or transformed there")
        self.assertEqual(run["ledger"]["totals"]["unaccounted"], 0, "the gate alone would have let it through")

    def test_defect_a_value_that_stands_where_the_path_map_does_not_say_ends_the_run(self):
        self.refused([('CARRIED, at(TAX_AT+r"/class")),', 'CARRIED, at(TAX_AT+r"/klasse")),')],
                     "a place the path map does not name for that path")

    def test_defect_a_record_that_is_not_this_runs_ends_the_run(self):
        stale = json.dumps(self.plain["ledger"])
        def before(out):
            os.makedirs(out)
            with open(os.path.join(out, "bsi-conversion-ledger.json"), "w", encoding="utf-8") as f: f.write(stale)
        write = 'with open(LJS,"w",encoding="utf-8") as f:\n    json.dump(LEDGER,f,indent=1,ensure_ascii=False); f.write("\\n")\n'
        self.refused([(write, "")], "bsi-conversion-ledger.json on disk is not the record of this run", source=odd_catalogue(), before=before)
        self.refused([(write, "")], "bsi-conversion-ledger.json on disk is not the record of this run")

    def test_defect_a_rule_whose_function_is_changed_ends_the_run(self):
        # the ledger alone cannot see it: the rule gives what the file holds. The bundle read back does.
        run = self.refused([('def link_uri(ns,href): return f"{ns}/req/{href[1:]}"', 'def link_uri(ns,href): return f"{ns}/requirement/{href[1:]}"')],
                           "link(s) of a control are no relation of that control's own Requirement")
        self.assertEqual((run["ledger"]["verification-failures"], run["ledger"]["totals"]["unaccounted"]), ([], 0))

    def test_defect_document_metadata_that_is_not_carried_ends_the_run(self):
        run = self.refused([('    if mrest: rfound["metadata"]=mrest\n', '')], "LEDGER UNACCOUNTED")
        self.assertEqual({u["path"].split(".")[2] for u in run["ledger"]["unaccounted-paths"]}, {"metadata"})

    def test_defect_a_prop_in_another_namespace_that_is_read_all_the_same_ends_the_run(self):
        # the mapping is written for BSI's lists: a `tags` of another list is another prop
        doc = catalogue()
        other = next(p for p in controls_of(doc)[-1][0]["props"] if p["name"] == "tags")
        other["ns"] = "https://example.org/andere-liste"
        run = self.convert(doc)
        self.assertEqual(run["done"].returncode, 0, run["done"].stderr[-600:])
        b = self.req(run, "PR.1.2")
        self.assertNotIn("tags", b["facets"][TAX]["by-statement"]["smt"], "it is not read as BSI's `tags`")
        self.assertEqual(b["facets"][COMPAT]["props"], [other], "and it is carried whole, its namespace with it")
        run = self.refused([('        if name in names and p.get("ns")==PROP_NS.get(name):', '        if name in names:')],
                           '"claim": "namespace"', "1 claim(s) that do not hold", source=doc)
        self.assertEqual([f["source"].rsplit("/", 1)[1] for f in run["ledger"]["verification-failures"]], ["ns"])

    def test_defect_a_file_changed_after_it_was_written_ends_the_run(self):
        change = ('ACCOUNT=led.account(', '_p=os.path.join(OUT,"objects","gspp","req-pr-1-2.json"); _o=json.load(open(_p,encoding="utf-8")); '
                  '_o["title"]["de"]+=" (2)"; json.dump(_o,open(_p,"w",encoding="utf-8"))\nACCOUNT=led.account(')
        self.refused([change], "LEDGER CHECK FAILED", "1 claim(s) that do not hold")

    # ---------------- the committed conversion ----------------
    def test_the_committed_bundle_is_what_its_record_and_its_report_say(self):
        folder = os.path.join(ROOT, "converted_examples", "DE.BSI")
        if not os.path.isdir(os.path.join(folder, "bsi-core-bundle")):
            self.skipTest("no converted_examples/ beside jascon/ (the skill unpacked on its own)")
        with open(os.path.join(folder, "bsi-conversion-ledger.json"), encoding="utf-8") as f: led = json.load(f)
        with open(os.path.join(folder, "bsi-coverage-report.json"), encoding="utf-8") as f: rep = json.load(f)
        self.assertEqual((led["totals"]["unaccounted"], led["verification-failures"]), (0, []))
        self.assertEqual(rep["ledger"]["totals"], led["totals"])
        objects = {}
        for base, _, files in os.walk(os.path.join(folder, "bsi-core-bundle", "objects")):
            for fn in files:
                with open(os.path.join(base, fn), encoding="utf-8") as f: o = json.load(f)
                objects[o["id"]] = o
        reqs = [o for o in objects.values() if "statements" in o]
        back = rep["ledger"]["bundle-read-back"]
        self.assertEqual(len(reqs), back["controls"], "a Requirement for every control of the source, at every depth")
        self.assertEqual(back["controls"], back["controls-top-level"] + back["controls-nested"])
        self.assertTrue(all(len(o["statements"]) == 1 for o in reqs))
        relations = [r for o in objects.values() for r in o.get("relations", [])]
        self.assertEqual(len(relations), back["links"])
        self.assertEqual([r["ref"] for r in relations if r["ref"].startswith(NS + "/") and r["ref"] not in objects], [])
        self.assertEqual([m["ref"] for o in objects.values() for m in o.get("members", []) if m["ref"] not in objects], [])
        self.assertEqual(back["links-that-are-a-relation-of-their-own-requirement"], back["links"])
        self.assertGreater(back["links-of-nested-controls"], 0)


if __name__ == "__main__":
    unittest.main()
