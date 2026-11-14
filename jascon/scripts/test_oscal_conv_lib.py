#!/usr/bin/env python3
"""Regression tests for the two value-level measurements of the converters'
coverage reports in oscal_conv_lib: global_occurrence (is there an equal
value anywhere) and Ledger (where did each source value go).

    python3 jascon/scripts/test_oscal_conv_lib.py

Each test is named after the report that found the defect (issues 32 and 33
in the GitHub tracker of the repository, 2026-11-13). Until that day the
function was `value_arrival`: it joined every output key and scalar into one
string and tested substring membership, so the six cases of issue 32 gave
five false arrivals and one false absence. Standard library only."""
import copy, json, os, sys, tempfile, unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from oscal_conv_lib import global_occurrence, Ledger, props_by_name, slug, RESPONSE_TREATMENT, response_treatment
from oscal_conv_lib import document_author, document_day, provenance, provenance_override, needs_kernel_2
from oscal_conv_lib import obligated_party, obligated_party_line, obligated_party_record


def measure(source, output):
    return global_occurrence([("src", source)], output)


class Issue32TypedWholeValues(unittest.TestCase):
    """A source value has arrived only if an output VALUE of the same JSON
    type equals it as a whole."""

    def assert_not_exact(self, source, output):
        r = measure(source, output)
        self.assertEqual((r["leaf-values"], r["exact"]), (1, 0), r)
        return r

    def test_issue_32_a_substring_of_another_value_is_no_arrival(self):
        r = self.assert_not_exact({"status": "open"}, [{"status": "not-open"}])
        # kept as information, in a category of its own, and not counted
        self.assertEqual(r["embedded"], 1)
        self.assertEqual(r["embedded-paths"][0]["pointers"], ["src#/status"])

    def test_issue_32_a_number_inside_a_longer_number_is_no_arrival(self):
        r = self.assert_not_exact({"count": 1}, [{"count": 10}])
        self.assertEqual((r["embedded"], r["absent"]["content"]), (0, 1))

    def test_issue_32_a_boolean_does_not_match_a_string(self):
        r = self.assert_not_exact({"enabled": True}, [{"enabled": "true"}])
        self.assertEqual(r["absent"]["content"], 1)

    def test_issue_32_a_match_never_spans_a_value_and_the_next_key(self):
        r = self.assert_not_exact({"description": "alpha\nnext"}, [{"a": "alpha", "next": "beta"}])
        self.assertEqual((r["embedded"], r["key-only"], r["absent"]["content"]), (0, 0, 1))

    def test_issue_32_the_empty_string_needs_a_destination(self):
        self.assert_not_exact({"description": ""}, [])
        r = self.assert_not_exact({"description": ""}, [{"description": "some text"}])
        self.assertEqual(r["embedded"], 0, "the empty string is inside every string and proves nothing")
        self.assertEqual(measure({"description": ""}, [{"title": ""}])["exact"], 1)

    def test_issue_32_a_preserved_null_has_arrived(self):
        r = measure({"value": None}, [{"value": None}])
        self.assertEqual((r["exact"], r["absent"]["content"]), (1, 0))
        self.assertEqual(measure({"value": None}, [{"value": "null"}])["exact"], 0)

    def test_issue_32_the_four_json_types_stay_apart(self):
        out = [{"a": 1, "b": "1", "c": True, "d": "true", "e": None}]
        for value in (1, "1", True, "true", None):
            self.assertEqual(measure({"x": value}, out)["exact"], 1, value)
        for value, other in ((1, [{"a": True}]), (True, [{"a": 1}]), (0, [{"a": False}]), ("null", [{"a": None}])):
            self.assertEqual(measure({"x": value}, other)["exact"], 0, value)


class Issue33WhatTheMeasureCannotSee(unittest.TestCase):
    """The measure is global. These tests pin down what follows from that, so
    that nobody reads more into the figure than it holds."""

    def test_issue_33_a_key_match_is_a_candidate_not_an_arrival(self):
        r = measure({"description": "title"}, [{"title": "Unrelated prose"}])
        self.assertEqual((r["exact"], r["key-only"]), (0, 1))
        self.assertEqual(r["key-only-paths"], [{"path": "src.description", "count": 1, "pointers": ["src#/description"]}])

    def test_issue_33_a_dropped_occurrence_hides_behind_an_equal_value(self):
        # KNOWN LIMIT, asserted on purpose: the second description is gone and
        # the global measure still says 4 of 4. Only a ledger of source
        # occurrences can see it; `exact` is an upper bound.
        source = {"controls": [{"id": "a", "description": "Same text"}, {"id": "b", "description": "Same text"}]}
        output = [{"id": "a", "description": "Same text"}, {"id": "b"}]
        r = measure(source, output)
        self.assertEqual((r["leaf-values"], r["exact"]), (4, 4))
        self.assertIn("upper bound", r["measures"])

    def test_issue_33_diagnostics_keep_the_array_index(self):
        source = {"controls": [{"description": "kept"}, {"description": "lost on the way"}]}
        r = measure(source, [{"description": "kept"}])
        self.assertEqual(r["absent-content-paths"],
                         [{"path": "src.controls[].description", "count": 1, "pointers": ["src#/controls/1/description"]}])

    def test_pointers_follow_rfc_6901(self):
        r = measure({"a/b": {"c~d": "lost"}}, [])
        self.assertEqual(r["absent-content-paths"][0]["pointers"], ["src#/a~1b/c~0d"])

    def test_every_leaf_is_in_exactly_one_class(self):
        source = {"a": "exact", "b": "key", "c": "part", "d": "gone", "uuid": "0000", "metadata": {"title": "zz"}}
        r = measure(source, [{"x": "exact", "key": "a longer part of text"}])
        self.assertEqual(r["leaf-values"], r["exact"] + r["key-only"] + r["embedded"] + sum(r["absent"].values()))
        self.assertEqual((r["exact"], r["key-only"], r["embedded"]), (1, 1, 1))
        self.assertEqual(r["absent"], {"identity": 1, "document-metadata": 1, "content": 1})


class Issue33Ledger(unittest.TestCase):
    """The ledger traces a value by what the converter did with it (object
    identity), never by equal text. `convert` plays a converter: it gets the
    tracked source and the ledger and returns {relpath: object}."""

    SOURCE = {"controls": [{"id": "a", "description": "Same text"}, {"id": "b", "description": "Same text"}]}

    def run_ledger(self, source, convert, tamper=None):
        led = Ledger()
        objects = convert(led.source("src", source), led)
        with tempfile.TemporaryDirectory() as out:
            for rel, obj in objects.items():
                os.makedirs(os.path.dirname(os.path.join(out, rel)), exist_ok=True)
                written = tamper(rel, json.loads(json.dumps(obj))) if tamper else obj
                with open(os.path.join(out, rel), "w", encoding="utf-8") as f: json.dump(written, f)
            return led.account(out, objects)

    @staticmethod
    def outcomes(result):
        return {e["source"]: e["outcome"] for e in result["entries"]}

    def test_issue_33_the_dropped_description_is_unaccounted_whatever_else_is_equal(self):
        def convert(src, led):
            a, b = src["controls"]
            return {"o/a.json": {"id": a["id"], "description": a["description"]},
                    # b's description is dropped; an unrelated equal value and an equal key do not save it
                    "o/b.json": {"id": b["id"], "title": "Same text", "Same text": 1}}
        r = self.run_ledger(self.SOURCE, convert)
        self.assertEqual(self.outcomes(r), {"src#/controls/0/id": "copied", "src#/controls/0/description": "copied",
                                            "src#/controls/1/id": "copied", "src#/controls/1/description": "unaccounted"})
        self.assertEqual(r["unaccounted-paths"],
                         [{"path": "src.controls[].description", "count": 1, "pointers": ["src#/controls/1/description"]}])
        self.assertEqual(r["totals"], {"copied": 3, "transformed": 0, "intentionally-dropped": 0, "unaccounted": 1})
        # the global check, on the same data, sees nothing wrong
        self.assertEqual(global_occurrence([("src", self.SOURCE)], [{"id": "a", "description": "Same text"}, {"id": "b"}])["exact"], 4)

    def test_issue_33_a_declared_deduplication_accounts_for_the_dropped_twin(self):
        def convert(src, led):
            a, b = ({"description": c["description"]} for c in src["controls"])
            led.same(b, a, "both controls carry one shared description, kept once")
            return {"o/shared.json": {"id": "https://ex.org/shared", **a}}
        r = self.run_ledger(self.SOURCE, convert)
        twin = next(e for e in r["entries"] if e["source"] == "src#/controls/1/description")
        self.assertEqual(twin["outcome"], "copied")
        self.assertEqual(twin["destinations"], [{"object": "https://ex.org/shared", "pointer": "/description",
                                                 "via": "both controls carry one shared description, kept once"}])

    def test_issue_33_a_deduplication_of_unequal_values_is_refused(self):
        source = {"controls": [{"description": "one text"}, {"description": "another text"}]}
        def convert(src, led):
            a, b = ({"description": c["description"]} for c in src["controls"])
            led.same(b, a, "claimed to be the same")
            return {"o/x.json": {"id": "https://ex.org/x", **a}}
        r = self.run_ledger(source, convert)
        self.assertEqual(self.outcomes(r)["src#/controls/1/description"], "unaccounted")
        self.assertEqual([f["source"] for f in r["verification-failures"]], ["src#/controls/1/description"])

    def test_a_transformation_is_named_and_applied_again_to_the_source(self):
        def convert(src, led):
            c = src["controls"][0]
            return {"o/a.json": {"id": led.derive("id from the control id", lambda i: "https://ex.org/" + slug(i), c["id"]),
                                 "label": led.derive("two values joined", lambda i, d: f"{i}: {d}", c["id"], c["description"])}}
        r = self.run_ledger(self.SOURCE, convert)
        e = {x["source"]: x for x in r["entries"]}
        self.assertEqual(e["src#/controls/0/id"]["outcome"], "transformed")
        self.assertEqual([d["rule"] for d in e["src#/controls/0/id"]["destinations"]], ["id from the control id", "two values joined"])
        self.assertEqual(e["src#/controls/0/description"]["destinations"],
                         [{"object": "https://ex.org/a", "pointer": "/label", "rule": "two values joined"}])
        self.assertEqual(r["verification-failures"], [])

    def test_a_plain_string_operation_loses_the_origin_until_it_is_stated(self):
        # the property the whole design rests on: computing a value un-tracks it
        def convert(src, led):
            c = src["controls"][0]
            return {"o/a.json": {"id": "https://ex.org/a", "upper": c["description"].upper(), "sliced": c["id"][:1]}}
        r = self.run_ledger(self.SOURCE, convert)
        self.assertEqual(self.outcomes(r)["src#/controls/0/description"], "unaccounted")
        self.assertEqual(self.outcomes(r)["src#/controls/0/id"], "unaccounted")

    def test_every_claim_is_checked_against_the_written_file(self):
        def convert(src, led):
            c = src["controls"][0]
            return {"o/a.json": {"id": "https://ex.org/a", "description": c["description"],
                                 "ref": led.derive("id from the control id", lambda i: "https://ex.org/" + i, c["id"])}}
        def tamper(rel, obj):
            obj["description"] = "Same text."; obj["ref"] = "https://ex.org/b"; return obj
        r = self.run_ledger(self.SOURCE, convert, tamper)
        self.assertEqual(sorted(f["source"] for f in r["verification-failures"]), ["src#/controls/0/description", "src#/controls/0/id"])
        self.assertEqual(self.outcomes(r)["src#/controls/0/description"], "unaccounted")

    def test_a_value_that_became_a_key_names_that_key(self):
        source = {"props": [{"name": "asset-type", "value": "appliance"}, {"name": "ipv4", "value": "10.0.0.1"}, {"name": "ipv4", "value": "10.0.0.2"}]}
        def convert(src, led):
            return {"o/a.json": {"id": "https://ex.org/a", "props": {p["name"]: p["value"] for p in src["props"]}}}
        r = self.run_ledger(source, convert)
        e = {x["source"]: x for x in r["entries"]}
        self.assertEqual(e["src#/props/0/name"]["destinations"], [{"object": "https://ex.org/a", "pointer": "/props/asset-type", "as": "key"}])
        # found on the IFA inventory, 2026-11-13: a dict built from repeated prop
        # names keeps the first key and the last value - one name and one value are lost
        self.assertEqual((e["src#/props/1/name"]["outcome"], e["src#/props/1/value"]["outcome"]), ("copied", "unaccounted"))
        self.assertEqual((e["src#/props/2/name"]["outcome"], e["src#/props/2/value"]["outcome"]), ("unaccounted", "copied"))

    def test_a_repeated_prop_name_keeps_every_value(self):
        # the fix for what the test above shows (the IFA inventory, item 4)
        source = {"props": [{"name": "asset-type", "value": "appliance"}, {"name": "ipv4-address", "value": "172.1.2.3"},
                            {"name": "ipv4-address", "value": "1.1.2.3"}, {"name": "ipv4-address", "value": "10.0.0.9"}]}
        self.assertEqual(props_by_name(source["props"]),
                         {"asset-type": "appliance", "ipv4-address": ["172.1.2.3", "1.1.2.3", "10.0.0.9"]})
        self.assertEqual(props_by_name(None), {})
        classed = [{"name": "a", "value": "1", "class": "x"}, {"name": "b", "value": "2"}, {"name": "a", "value": "3", "class": "y"}]
        self.assertEqual(props_by_name(classed, field="class"), {"a": ["x", "y"]}, "another member of the prop; props without it are left out")
        def convert(src, led):
            return {"o/a.json": {"id": "https://ex.org/a", "props": props_by_name(src["props"], led)}}
        r = self.run_ledger(source, convert)
        self.assertEqual(r["totals"], {"copied": 8, "transformed": 0, "intentionally-dropped": 0, "unaccounted": 0})
        e = {x["source"]: x for x in r["entries"]}
        self.assertEqual(e["src#/props/1/value"]["destinations"], [{"object": "https://ex.org/a", "pointer": "/props/ipv4-address/0"}])
        self.assertEqual(e["src#/props/3/value"]["destinations"], [{"object": "https://ex.org/a", "pointer": "/props/ipv4-address/2"}])
        self.assertEqual(e["src#/props/2/name"]["destinations"], [{"object": "https://ex.org/a", "pointer": "/props/ipv4-address", "as": "key",
                         "via": "a prop name that repeats is one key; its values are listed in source order"}])

    def test_a_drop_is_declared_with_its_reason_and_never_overrides_a_destination(self):
        source = {"uuid": "u-1", "items": [{"uuid": "u-2", "title": "kept"}, {"uuid": "u-3", "title": "lost"}]}
        def convert(src, led):
            led.drop(r"\.uuid$", "identity is re-minted")
            return {"o/a.json": {"id": "https://ex.org/a", "title": src["items"][0]["title"], "source-uuid": src["items"][0]["uuid"]}}
        r = self.run_ledger(source, convert)
        e = {x["source"]: x for x in r["entries"]}
        self.assertEqual((e["src#/uuid"]["outcome"], e["src#/uuid"]["reason"]), ("intentionally-dropped", "identity is re-minted"))
        self.assertEqual(e["src#/items/0/uuid"]["outcome"], "copied", "a carried uuid is a copy, whatever the drop rule says")
        self.assertEqual(e["src#/items/1/title"]["outcome"], "unaccounted", "a drop covers only what it names")
        self.assertEqual(sum(r["totals"].values()), r["leaf-values"])

    def test_one_value_is_dropped_by_name_not_by_path(self):
        source = {"roles": [{"role": "admin", "party": "p-1"}, {"role": "owner", "party": "p-2"}]}
        def convert(src, led):
            led.drop_value(src["roles"][1]["party"], "the party record has no name")
            led.drop_value(src["roles"][0]["role"], "never applies: the value has a destination")
            return {"o/a.json": {"id": "https://ex.org/a", "roles": [r["role"] for r in src["roles"]]}}
        r = self.run_ledger(source, convert)
        e = {x["source"]: x for x in r["entries"]}
        self.assertEqual((e["src#/roles/1/party"]["outcome"], e["src#/roles/1/party"]["reason"]),
                         ("intentionally-dropped", "the party record has no name"))
        self.assertEqual(e["src#/roles/0/party"]["outcome"], "unaccounted", "the same path, another value: not covered")
        self.assertEqual(e["src#/roles/0/role"]["outcome"], "copied")

    def test_tracking_changes_nothing_that_is_written(self):
        source = {"n": 27017, "s": "text", "nested": [{"k": "v"}]}
        led = Ledger(); tracked = led.source("src", source)
        self.assertEqual(json.dumps(tracked), json.dumps(source))
        self.assertIs(copy.deepcopy(tracked["s"]), tracked["s"], "a copy keeps the trace")
        self.assertEqual((type(tracked["n"] + 1), type(tracked["s"].strip())), (int, str), "a computed value is plain")
        with self.assertRaises(TypeError): led.derive("to a list", lambda s: [s], tracked["s"])


class Backlog47bResponseTypes(unittest.TestCase):
    """OSCAL allows seven values for the type of a risk response; C.10 has
    four treatment options. Five of the seven are one of the four. `none`
    and `contingency` get no code (backlog #47b, decided 2026-11-13): the
    converter writes no `treatment` and counts the response."""

    def test_backlog_47b_the_five_mapped_types_reach_all_four_options(self):
        for rtype, code in RESPONSE_TREATMENT.items():
            self.assertEqual(response_treatment(rtype), (code, None), rtype)
        self.assertEqual(set(RESPONSE_TREATMENT.values()), {"modify", "retain", "avoid", "share"})

    def test_backlog_47b_none_gives_no_option_and_says_that_none_was_chosen(self):
        code, why = response_treatment("none")
        self.assertIsNone(code)
        self.assertIn("no `treatment` is written", why)

    def test_backlog_47b_contingency_gives_no_option_and_is_counted_as_uncoded(self):
        self.assertEqual(response_treatment("contingency"),
                         (None, "response type `contingency` has no treatment code (C.10)"))

    def test_backlog_47b_a_misspelled_type_is_not_guessed_at(self):
        self.assertIsNone(response_treatment("mitigation")[0])


class Backlog69WhoWroteItAndWhen(unittest.TestCase):
    """A converter pre-fills `provenance` from what the source document says
    about itself, and the caller may overwrite it (author decision
    2026-11-13). The rule for the author of an OSCAL document is one rule,
    in this library and in the app's importer (jascon-oscal.js); the table
    below is the same table on both sides."""
    A = {"uuid": "a", "type": "person", "name": "Amy Assessor"}
    B = {"uuid": "b", "type": "person", "name": "Owen Pearson"}
    O = {"uuid": "o", "type": "organization", "name": "Important Federal Agency"}
    P = {"uuid": "p", "type": "organization", "name": "Assessors Inc."}
    N = {"uuid": "n", "type": "person"}                          # defined without a name

    def who(self, rps, parties):
        meta = {"responsible-parties": [{"role-id": r, "party-uuids": us} for r, us in rps]}
        if parties is not None: meta["parties"] = parties
        got = document_author(meta)
        return None if got is None else got["uuid"]

    def test_backlog_69_the_document_author_table(self):
        A, B, O, P, N = self.A, self.B, self.O, self.P, self.N
        table = [
            ("a creator is the author", [("creator", ["a"]), ("contact", ["b"])], [A, B], "a"),
            ("prepared-by, where no creator is named", [("prepared-by", ["a"]), ("owner", ["b"])], [A, B], "a"),
            ("two creators are no answer; prepared-by is asked next", [("creator", ["a", "b"]), ("prepared-by", ["b"])], [A, B], "b"),
            ("the one party any role names", [("assessor", ["a"])], [A, O], "a"),
            ("several responsible people: the one organization", [("owner", ["a"]), ("developer", ["b"])], [A, B, O], "o"),
            ("several responsible people and no organization", [("owner", ["a"]), ("developer", ["b"])], [A, B], None),
            ("several responsible people and two organizations", [("owner", ["a"]), ("developer", ["b"])], [A, B, O, P], None),
            ("no role, one party", [], [A], "a"),
            ("no role, two people", [], [A, B], None),
            ("no role, two people and one organization", [], [A, B, O], "o"),
            ("no parties at all", [], None, None),
            ("a creator the document does not define is nobody; the one party stands", [("creator", ["x"])], [A], "a"),
            ("a party without a name cannot be named by a URI", [("assessor", ["n"])], [N, O], None),
            ("a uuid the document does not define is not counted", [("assessor", ["x", "a"])], [A, B], "a"),
            ("a party defined twice is one party", [], [A, dict(A)], "a"),
            ("of two definitions of one uuid the first is the party", [], [A, {"uuid": "a", "type": "person"}], "a"),
            ("of two definitions of one uuid the first is the party, also when it has no name", [], [{"uuid": "a", "type": "person"}, A], None),
            ("an entry without a uuid is no party", [], [{"type": "organization", "name": "Nameless Ltd"}, A], "a"),
        ]
        for what, rps, parties, want in table:
            self.assertEqual(self.who(rps, parties), want, what)

    def test_backlog_69_the_day_is_the_date_of_last_modified_or_nothing(self):
        self.assertEqual(document_day({"last-modified": "2026-05-12T10:26:16.00000-00:00"}), "2026-05-12")
        self.assertEqual(document_day({"last-modified": "2026-05-12"}), "2026-05-12")
        for bad in ("2026-13-01T00:00:00Z", "12 May 2026", "", None, 20260512, "2026-05-1"):
            self.assertIsNone(document_day({"last-modified": bad}), repr(bad))
        self.assertIsNone(document_day({}))

    def test_backlog_69_the_caller_overwrites_field_by_field(self):
        src = ("https://ifa.gov/party/amy", "2026-05-12")
        self.assertEqual(provenance(*src), {"author-ref": src[0], "date": src[1]})
        self.assertEqual(provenance(*src, override=("https://org.example/party/ciso", None)),
                         {"author-ref": "https://org.example/party/ciso", "date": "2026-05-12"})
        self.assertEqual(provenance(*src, override=(None, "2026-11-13")),
                         {"author-ref": src[0], "date": "2026-11-13"})
        self.assertEqual(provenance(None, None, override=("https://org.example/party/ciso", "2026-11-13")),
                         {"author-ref": "https://org.example/party/ciso", "date": "2026-11-13"})

    def test_backlog_69_no_provenance_without_both_an_author_and_a_date(self):
        self.assertIsNone(provenance(None, "2026-05-12"))
        self.assertIsNone(provenance("https://ifa.gov/party/amy", None))
        self.assertIsNone(provenance(None, None, override=("https://org.example/party/ciso", None)))
        self.assertIsNone(provenance(None, None))

    def test_backlog_69_the_two_arguments_are_read_and_held_to_their_types(self):
        self.assertEqual(provenance_override([]), (None, None))
        self.assertEqual(provenance_override(["--author-ref", "https://org.example/party/ciso"]),
                         ("https://org.example/party/ciso", None))
        self.assertEqual(provenance_override(["--date", "2026-11-13", "--author-ref", "https://org.example/party/ciso"]),
                         ("https://org.example/party/ciso", "2026-11-13"))
        for bad in (["--date", "13.11.2026"], ["--date", "2026-11-13\n"], ["--date", "2026-02-30"], ["--date", "2026-1-3"], ["--date"],
                    ["--author-ref", "the CISO"], ["--author-ref", ""], ["--author-ref"]):
            with self.assertRaises(SystemExit, msg=repr(bad)): provenance_override(bad)

    def test_backlog_69_other_arguments_are_left_to_the_converter(self):
        self.assertEqual(provenance_override(["--out", "/tmp/x", "--date", "2026-11-13"]), (None, "2026-11-13"))


class Backlog69ThePinAWriterSets(unittest.TestCase):
    """Bundle.write pins kernel 2.0.0 when the content needs it. The rule is
    the validator's (kernel_needed); the library's copy is held to the pin
    vectors of the conformance corpus, so the two cannot drift apart
    unnoticed."""
    def test_backlog_69_the_library_pins_what_the_pin_vectors_say_needs_a_pin(self):
        here = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(here, "..", "conformance", "kernel-vectors.json"), encoding="utf-8") as f:
            vectors = json.load(f)["vectors"]
        asked = 0
        for v in vectors:
            m = v["manifest"]
            if m.get("scales") or m.get("pack"): continue          # reasons a manifest carries; Bundle.write writes neither
            frags = " ".join(v.get("expected-frags") or [])
            if "KERNEL-1" in frags:
                self.assertTrue(needs_kernel_2(v["objects"]), v["name"]); asked += 1
            elif not v.get("expected-fails") and m.get("kernel-version") in (None, "1.0.0"):
                self.assertFalse(needs_kernel_2(v["objects"]), v["name"]); asked += 1
            elif not v.get("expected-fails") and m.get("kernel-version") == "2.0.0":
                # a pinned vector is content that needs its pin, except the one that pins 2.0.0 on 1.0.0 content
                asked += 1
        self.assertGreaterEqual(asked, 15, "the pin vectors were not found")

    def test_backlog_69_each_reason_for_a_pin_is_known(self):
        req = {"id": "https://x/req/1", "version": "1", "lifecycle": "active", "statements": []}
        self.assertFalse(needs_kernel_2([req]))
        self.assertFalse(needs_kernel_2([{"id": "https://x/map/1", "relationship": "equal",
                                          "provenance": {"author-ref": "https://x/p", "date": "2026-11-13"}}]))
        reasons = {
            "a Risk": {"scenario": "s", "owner-ref": "https://x/p"},
            "risk-refs": {"assessment-ref": "a", "risk-refs": ["https://x/risk/1"]},
            "check-ref": {"assessment-ref": "a", "check-ref": "https://x/check/1"},
            "a Check": {"criteria": [], "observes": []},
            "check results": {"performer-ref": "p", "check-results": [{}]},
            "a tailoring-ref on an Assessment": {"performer-ref": "p", "tailoring-ref": "https://x/t"},
            "product-version": {"kind": "software", "product-version": "7"},
            "statement-ids on a capability": {"kind": "software", "capabilities": [{"id": "c", "statement-ids": ["s1"]}]},
            "a dated authorization": {"kind": "system", "authorizations": [{"id": "a", "date": "2026-06-30"}]},
            "provenance on an Implementation": {"component-ref": "c", "requirement-ref": "r", "provenance": {}},
            "provenance on a Finding": {"assessment-ref": "a", "provenance": {}},
            "provenance on a Tailoring": {"selects": [], "provenance": {}},
            "provenance on a select": {"selects": [{"set-ref": "s", "provenance": {}}]},
            "provenance on an operation": {"selects": [], "operations": [{"op": "set-parameter", "provenance": {}}]},
            "a Deviation with decided": {"assessment-ref": "a", "deviations": [{"decided": "2026-11-13"}]},
            "a Deviation with review-due": {"assessment-ref": "a", "deviations": [{"review-due": {}}]},
            "a Deviation on an operation": {"selects": [], "operations": [{"deviation": {"decided": "2026-11-13"}}]},
        }
        for what, o in reasons.items():
            self.assertTrue(needs_kernel_2([req, o]), what)


class Backlog74WhomAStatementBinds(unittest.TestCase):
    """The obligated party of a converted statement is the converter's default
    unless the caller names another (author, 2026-11-14). The report says
    which of the two it was."""
    D = "https://ns.example/fw/party/organisation"

    def test_backlog_74_without_the_argument_the_default_is_written_and_named_as_the_converters(self):
        self.assertEqual(obligated_party([], self.D), (self.D, "converter-default"))
        self.assertEqual(obligated_party(["--author-ref", "https://a.example/p", "--date", "2026-01-01"], self.D), (self.D, "converter-default"))

    def test_backlog_74_the_callers_party_takes_the_defaults_place(self):
        mine = "https://acme.example/party/it-operations"
        for argv in (["--obligated-party", mine], ["--date", "2026-01-01", "--obligated-party", mine, "--out", "x"]):
            self.assertEqual(obligated_party(argv, self.D), (mine, "caller"))

    def test_backlog_74_a_value_that_is_no_party_stops_the_run(self):
        for argv, word in ((["--obligated-party"], "needs a value"), (["--obligated-party", ""], "not an http(s) URI"),
                           (["--obligated-party", "organisation"], "not an http(s) URI"),
                           (["--obligated-party", "https://a.example/p\n"], "not an http(s) URI"),      # #68: a line break ends no value
                           (["--obligated-party", "https://a.example/p q"], "not an http(s) URI"),
                           (["--obligated-party", "https://a.example/p", "--obligated-party", "https://b.example/p"], "more than once")):
            with self.assertRaises(SystemExit, msg=argv) as c: obligated_party(argv, self.D)
            self.assertIn(word, str(c.exception))
        with self.assertRaises(SystemExit) as c: obligated_party([], "organisation")       # a converter's own default is held to the same
        self.assertIn("default", str(c.exception))

    def test_backlog_74_the_report_says_who_chose_the_party(self):
        mine = "https://acme.example/party/it"
        d = obligated_party_line(self.D, "converter-default", self.D, "the framework binds the organisation implicitly")
        self.assertIn(f"`{self.D}` on every statement.", d)
        self.assertIn("the converter's default and not a value of the source", d)
        self.assertIn("--obligated-party URI", d)
        self.assertIn("Why this default: the framework binds the organisation implicitly.", d)
        c = obligated_party_line(mine, "caller", self.D)
        self.assertIn(f"`{mine}` on every statement, given by the caller", c)
        self.assertIn(f"The converter's own default is `{self.D}`.", c)
        self.assertNotIn("not a value of the source", c)
        s = obligated_party_line(self.D, "converter-default", self.D, source_states="as the implementation level of a control")
        self.assertIn("for which the source names no party; where it names one (as the implementation level of a control), that one is written", s)
        self.assertEqual(obligated_party_record(self.D, "converter-default", self.D), {"value": self.D, "origin": "converter-default", "converter-default": self.D})
        self.assertEqual(obligated_party_record(mine, "caller", self.D, "in `affects` of a rule"),
                         {"value": mine, "origin": "caller", "converter-default": self.D, "source-states": "in `affects` of a rule"})

if __name__ == "__main__":
    unittest.main()
