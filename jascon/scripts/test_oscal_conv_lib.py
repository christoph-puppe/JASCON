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
from oscal_conv_lib import known_arguments, out_dir
from oscal_conv_lib import obligated_party, obligated_party_line, obligated_party_record
from oscal_conv_lib import ledger_by_path, ledger_gate, Bundle, COMPAT, COMPAT_ID, COMPAT_FILE
from oscal_conv_lib import lifecycle_default_record, lifecycle_default_line


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
        self.assertEqual(r["totals"], {"copied": 3, "transformed": 0, "not-content": 0, "intentionally-dropped": 0, "unaccounted": 1})
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
        self.assertEqual(r["totals"], {"copied": 8, "transformed": 0, "not-content": 0, "intentionally-dropped": 0, "unaccounted": 0})
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


class Backlog74WhatAConverterIsTold(unittest.TestCase):
    """Two readers of a converter's command line that came with #74: where
    the conversion is written, and that no argument goes unread. The nine
    converters that use them are run in test_convert_obligated_party.py."""

    def test_backlog_74_out_names_the_folder_and_without_it_the_corpus_folder_stands(self):
        self.assertEqual(out_dir([], "/repo/converted_examples/X"), "/repo/converted_examples/X")
        self.assertEqual(out_dir(["--obligated-party", "https://a.example/p"], "d"), "d")
        self.assertEqual(out_dir(["--obligated-party", "https://a.example/p", "--out", os.path.join("some", "where")], "d"),
                         os.path.abspath(os.path.join("some", "where")))
        for argv, word in ((["--out"], "needs a directory"), (["--out", ""], "needs a directory"),
                           (["--out", "a", "--out", "b"], "more than once")):
            with self.assertRaises(SystemExit, msg=argv) as c: out_dir(argv, "d")
            self.assertIn(word, str(c.exception))

    def test_backlog_74_an_argument_nobody_reads_stops_the_run(self):
        takes = ("--obligated-party", "--out")
        for ok in ([], ["--out", "x"], ["--obligated-party", "https://a.example/p", "--out", "x"]):
            self.assertIsNone(known_arguments(ok, takes), ok)
        for argv, word in ((["--obligated-partie", "https://a.example/p"], "unknown argument '--obligated-partie'"),   # the default would be written, silently
                           (["https://a.example/p"], "unknown argument"),
                           (["--out", "x", "stray"], "unknown argument 'stray'"),
                           (["--date", "2026-11-14"], "unknown argument '--date'"),       # another converter's argument is not this one's
                           (["--out"], "--out needs a value"),
                           (["--out", "--obligated-party", "https://a.example/p"], "--out needs a value")):
            with self.assertRaises(SystemExit, msg=argv) as c: known_arguments(argv, takes)
            self.assertIn(word, str(c.exception))


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

class Backlog75NoManifestListsAnAttestation(unittest.TestCase):
    """MANIFEST-1: the library's Bundle lists whatever is added to it, so it
    takes no Attestation. A converter writes one beside the manifest."""
    def test_backlog_75_an_attestation_is_not_added_to_a_bundle(self):
        from oscal_conv_lib import Bundle
        b = Bundle(tempfile.mkdtemp())
        att = {"id": "https://a.example/attestation/x", "version": "1", "lifecycle": "active", "signer": "https://a.example/party/ao",
               "timestamp": "2026-11-14T09:00:00Z", "content-manifest-digest": "sha256:" + "a" * 64,
               "subject-semantic-digests": [{"id": "https://a.example/req/1", "semantic-digest": "sha256:" + "b" * 64}]}
        with self.assertRaises(SystemExit) as c: b.add("objects/attestation/x.json", att)
        self.assertIn("MANIFEST-1", str(c.exception))
        self.assertEqual(b.objects, {})
        comp = {"id": "https://a.example/attestation/not-one", "version": "1", "lifecycle": "active", "kind": "system", "title": "A component"}
        b.add("objects/component/c.json", comp)                 # the shape decides, not the id
        self.assertEqual(list(b.objects), ["objects/component/c.json"])

class Backlog41TheLedgerOfALargeCorpus(unittest.TestCase):
    """ledger_by_path: the record of a corpus too large for one entry per
    leaf value. It counts the entries Ledger.account() checked; it adds
    nothing and loses no leaf."""
    def run_ledger(self):
        src = {"controls": [{"id": "a-1", "title": "First", "class": "x", "note": "kept nowhere", "uuid": "u1"},
                            {"id": "a-2", "title": "Second", "class": "x", "note": "kept nowhere too", "uuid": "u2"},
                            {"id": "a-3", "title": "Third", "class": "y", "uuid": "u3"}]}
        led = Ledger(); doc = led.source("cat", copy.deepcopy(src))
        led.drop(r"\.uuid$", "an identity of the source document, not content")
        objs = {}
        for i, c in enumerate(doc["controls"]):
            objs[f"objects/req/{c['id']}.json"] = {"id": led.derive("id-rule", lambda v: "https://x.example/req/" + v, c["id"]),
                                                   "statements": [{"prose": {"en": c["title"]}}], "tags": [c["class"]]}
        out = tempfile.mkdtemp()
        for rel, o in objs.items():
            os.makedirs(os.path.dirname(os.path.join(out, rel)), exist_ok=True)
            with open(os.path.join(out, rel), "w", encoding="utf-8") as f: json.dump(o, f)
        return led.account(out, objs)

    def test_backlog_41_one_row_per_path_and_outcome_and_every_leaf_counted_once(self):
        full = self.run_ledger()
        before = json.dumps(full, sort_keys=True)
        short = ledger_by_path(full, examples=1)
        self.assertEqual(json.dumps(full, sort_keys=True), before)                  # the per-leaf ledger is not touched
        self.assertEqual(short["leaf-values"], 14)
        self.assertEqual(short["totals"], full["totals"])
        self.assertEqual(short["totals"], {"copied": 6, "transformed": 3, "not-content": 0, "intentionally-dropped": 3, "unaccounted": 2})
        self.assertEqual(sum(r["count"] for r in short["paths"]), 14)
        rows = {(r["path"], r["outcome"]): r for r in short["paths"]}
        self.assertEqual(len(rows), len(short["paths"]))                            # one row per path and outcome
        self.assertEqual(rows[("cat.controls[].title", "copied")]["count"], 3)
        self.assertEqual(rows[("cat.controls[].title", "copied")]["to"], [{"pointer": "/statements/[]/prose/en", "count": 3}])
        self.assertEqual(rows[("cat.controls[].title", "copied")]["example"], "cat#/controls/0/title")
        self.assertEqual(rows[("cat.controls[].id", "transformed")]["to"], [{"pointer": "/id", "count": 3, "rule": "id-rule"}])
        self.assertEqual(rows[("cat.controls[].uuid", "intentionally-dropped")]["reasons"],
                         [{"reason": "an identity of the source document, not content", "count": 3}])
        self.assertEqual(rows[("cat.controls[].note", "unaccounted")]["count"], 2)
        self.assertNotIn("to", rows[("cat.controls[].note", "unaccounted")])
        self.assertEqual(short["unaccounted-paths"], [{"path": "cat.controls[].note", "count": 2, "pointers": ["cat#/controls/0/note"]}])
        self.assertNotIn("entries", short)

class PhaseEWhatIsNoContent(unittest.TestCase):
    """The author's rule of 2026-11-14: "Real content is never dropped. What
    may stay out of a bundle is only what is not content: a name that merely
    selects a field, a namespace, an id that is rebuilt exactly from another
    value. Each such class needs a stated rule that the ledger checks, not an
    'unaccounted' line." Each test plays a converter that states such a rule
    and looks at what the ledger makes of it."""

    SOURCE = {"controls": [{"id": "ac-1", "props": [{"name": "label", "ns": "https://ns.example/a", "value": "AC-1"},
                                                    {"name": "sort-id", "ns": "https://ns.example/a", "value": "ac-01"}],
                            "parts": [{"id": "ac-1_smt", "name": "statement", "prose": "Develop a policy."}]}]}
    NAMES = {"label": "label", "sort-id": "sort"}

    def run_ledger(self, convert, source=None, typed=False, tamper=None, resolve=True):
        led = Ledger()
        objects = convert(led.source("src", copy.deepcopy(source or self.SOURCE), typed=typed), led)
        if resolve: led.resolve(objects)
        with tempfile.TemporaryDirectory() as out:
            for rel, obj in objects.items():
                os.makedirs(os.path.dirname(os.path.join(out, rel)), exist_ok=True)
                written = tamper(json.loads(json.dumps(obj))) if tamper else obj
                with open(os.path.join(out, rel), "w", encoding="utf-8") as f: json.dump(written, f)
            return led.account(out, objects)

    @staticmethod
    def by_source(result):
        return {e["source"]: e for e in result["entries"]}

    def convert(self, carry=("label", "sort-id"), among=NAMES, allowed=("https://ns.example/a",), part_id=None, drop=None):
        """a converter that writes a prop's value into the field its name selects"""
        def run(src, led):
            c = src["controls"][0]; part = c["parts"][0]
            obj = {"id": led.derive("id from the control id", lambda i: "https://ex.org/" + i, c["id"]),
                   "statements": [{"prose": part["prose"]}]}
            for p in c["props"]:
                if p["name"] in carry: obj[self.NAMES.get(p["name"], "other")] = p["value"]
                led.selector(p["name"], "a prop's name selects the field its value is written to", p["value"], among=among)
                led.namespace(p["ns"], "the namespace of a prop this mapping is written for", allowed, p["name"])
            led.selector(part["name"], "a part's name selects the member its prose is written to", part["prose"])
            led.rebuilt(part["id"], "a statement part's id is its control's id and _smt",
                        part_id or (lambda i: i + "_smt"), c["id"])
            if drop: led.drop(drop, "declared by this test")
            return {"o/ac-1.json": obj}
        return run

    def test_a_name_a_namespace_and_a_rebuilt_id_are_no_content_when_the_rule_holds(self):
        r = self.run_ledger(self.convert())
        self.assertEqual(r["totals"], {"copied": 3, "transformed": 1, "not-content": 6, "intentionally-dropped": 0, "unaccounted": 0})
        self.assertEqual(r["verification-failures"], [])
        e = self.by_source(r)
        name = e["src#/controls/0/props/0/name"]
        self.assertEqual({k: name[k] for k in ("kind", "rule", "outcome")},
                         {"kind": "selector", "rule": "a prop's name selects the field its value is written to", "outcome": "not-content"})
        self.assertEqual(e["src#/controls/0/props/1/ns"]["kind"], "namespace")
        self.assertEqual(e["src#/controls/0/parts/0/id"]["kind"], "rebuilt-id")
        self.assertNotIn("destinations", e["src#/controls/0/parts/0/id"])

    def test_a_name_that_selects_a_lost_value_is_not_covered(self):
        # the value of sort-id is written nowhere: its name selected nothing, and its namespace qualifies that name
        r = self.run_ledger(self.convert(carry=("label",)))
        e = self.by_source(r)
        self.assertEqual([e[f"src#/controls/0/props/1/{k}"]["outcome"] for k in ("value", "name", "ns")], ["unaccounted"] * 3)
        self.assertEqual([e[f"src#/controls/0/props/0/{k}"]["outcome"] for k in ("value", "name", "ns")],
                         ["copied", "not-content", "not-content"])
        self.assertEqual(r["totals"]["unaccounted"], 3)
        self.assertEqual(r["verification-failures"], [], "a lost value is unaccounted; no claim about it was false")

    def test_a_name_goes_with_a_value_that_is_dropped_for_a_declared_reason(self):
        r = self.run_ledger(self.convert(carry=("label",), drop=r"props\[\]\.value$"))
        e = self.by_source(r)
        self.assertEqual(e["src#/controls/0/props/0/value"]["outcome"], "copied", "a drop never overrides a destination")
        self.assertEqual(e["src#/controls/0/props/1/value"]["outcome"], "intentionally-dropped")
        name = e["src#/controls/0/props/1/name"]
        self.assertEqual(name["outcome"], "intentionally-dropped")
        self.assertEqual(name["reason"], "a prop's name selects the field its value is written to - of a value that is dropped: declared by this test")
        self.assertEqual(r["totals"]["not-content"], 4)

    def test_a_name_the_mapping_does_not_know_is_a_claim_that_does_not_hold(self):
        r = self.run_ledger(self.convert(among={"label": "label"}))
        e = self.by_source(r)
        self.assertEqual(e["src#/controls/0/props/1/name"]["outcome"], "unaccounted")
        self.assertEqual(r["verification-failures"], [{"source": "src#/controls/0/props/1/name", "claim": "selector",
                                                       "rule": "a prop's name selects the field its value is written to"}])

    def test_another_namespace_is_another_meaning_and_is_not_covered(self):
        src = copy.deepcopy(self.SOURCE); src["controls"][0]["props"][1]["ns"] = "https://ns.example/b"
        r = self.run_ledger(self.convert(), source=src)
        e = self.by_source(r)
        self.assertEqual((e["src#/controls/0/props/0/ns"]["outcome"], e["src#/controls/0/props/1/ns"]["outcome"]), ("not-content", "unaccounted"))
        self.assertEqual([(f["source"], f["claim"]) for f in r["verification-failures"]], [("src#/controls/0/props/1/ns", "namespace")])

    def test_an_id_the_rule_does_not_give_is_not_rebuilt(self):
        r = self.run_ledger(self.convert(part_id=lambda i: i + ".smt"))
        self.assertEqual(self.by_source(r)["src#/controls/0/parts/0/id"]["outcome"], "unaccounted")
        self.assertEqual([(f["source"], f["claim"]) for f in r["verification-failures"]], [("src#/controls/0/parts/0/id", "rebuilt-id")])

    def test_an_id_is_rebuilt_only_from_what_the_bundle_holds(self):
        def convert(src, led):                       # the control id is written nowhere
            c = src["controls"][0]; part = c["parts"][0]
            led.rebuilt(part["id"], "id plus _smt", lambda i: i + "_smt", c["id"])
            return {"o/x.json": {"id": "https://ex.org/x", "prose": part["prose"]}}
        e = self.by_source(self.run_ledger(convert))
        self.assertEqual((e["src#/controls/0/id"]["outcome"], e["src#/controls/0/parts/0/id"]["outcome"]), ("unaccounted", "unaccounted"))
        def dropped(src, led):
            led.drop(r"controls\[\]\.id$", "declared by this test")
            return convert(src, led)
        e = self.by_source(self.run_ledger(dropped))
        self.assertEqual(e["src#/controls/0/parts/0/id"]["outcome"], "intentionally-dropped", "it goes with what it is rebuilt from")

    def test_a_value_that_has_a_destination_is_carried_whatever_is_declared_for_it(self):
        def convert(src, led):
            p = src["controls"][0]["props"][0]
            led.selector(p["name"], "a prop's name", p["value"])
            return {"o/x.json": {"id": "https://ex.org/x", "props": {p["name"]: p["value"]}}}
        e = self.by_source(self.run_ledger(convert))
        self.assertEqual(e["src#/controls/0/props/0/name"]["outcome"], "copied")
        self.assertNotIn("kind", e["src#/controls/0/props/0/name"])

    def test_a_rule_is_stated_about_a_source_leaf_and_about_something(self):
        led = Ledger(); src = led.source("src", copy.deepcopy(self.SOURCE)); p = src["controls"][0]["props"][0]
        with self.assertRaises(TypeError): led.selector("label", "a plain string", p["value"])
        with self.assertRaises(TypeError): led.selector(led.derive("made", lambda v: v + "x", p["name"]), "a derived value", p["value"])
        with self.assertRaises(ValueError): led.selector(p["name"], "selects nothing", "a plain string")
        with self.assertRaises(ValueError): led.selector(p["name"], "selects itself only", {"name": p["name"]})
        with self.assertRaises(ValueError): led.namespace(p["ns"], "qualifies nothing", ["https://ns.example/a"], None)
        led.selector(p["name"], "the prop handed over whole", p)     # its own name is left out of what it rests on

    def test_two_rules_that_rest_on_each_other_cover_nothing(self):
        def convert(src, led):
            p = src["controls"][0]["props"][0]
            led.selector(p["name"], "the name selects the namespace", p["ns"])
            led.namespace(p["ns"], "the namespace qualifies the name", ["https://ns.example/a"], p["name"])
            return {"o/x.json": {"id": "https://ex.org/x"}}
        e = self.by_source(self.run_ledger(convert))
        self.assertEqual((e["src#/controls/0/props/0/name"]["outcome"], e["src#/controls/0/props/0/ns"]["outcome"]),
                         ("unaccounted", "unaccounted"))

    def test_the_record_of_a_large_corpus_names_the_rules(self):
        short = ledger_by_path(self.run_ledger(self.convert()))
        rows = {(r["path"], r["outcome"]): r for r in short["paths"]}
        self.assertEqual(rows[("src.controls[].props[].name", "not-content")]["rules"],
                         [{"kind": "selector", "rule": "a prop's name selects the field its value is written to", "count": 2}])
        self.assertEqual(rows[("src.controls[].parts[].id", "not-content")]["rules"],
                         [{"kind": "rebuilt-id", "rule": "a statement part's id is its control's id and _smt", "count": 1}])
        self.assertEqual(short["totals"]["not-content"], 6)
        self.assertEqual(sum(r["count"] for r in short["paths"]), short["leaf-values"])


class PhaseETypedValues(unittest.TestCase):
    """A boolean and a fraction are content like a string. Until 2026-11-14
    the ledger could not follow them: the CR26 source has 49 booleans and 3
    fractions, the converter carried them, and its ledger read them as
    unaccounted."""

    SOURCE = {"rule": {"id": "r1", "required": True, "optional": False, "weight": 0.75, "count": 3}}

    def run_ledger(self, convert, typed=True, resolve=True, tamper=None):
        return PhaseEWhatIsNoContent.run_ledger(self, convert, source=self.SOURCE, typed=typed, tamper=tamper, resolve=resolve)

    @staticmethod
    def convert(src, led):
        r = src["rule"]
        return {"o/r1.json": {"id": led.derive("id", lambda i: "https://ex.org/" + i, r["id"]),
                              "required": r["required"], "optional": r["optional"], "weight": r["weight"], "count": r["count"]}}

    def test_a_boolean_and_a_fraction_are_followed_to_where_they_stand(self):
        r = self.run_ledger(self.convert)
        self.assertEqual(r["totals"], {"copied": 4, "transformed": 1, "not-content": 0, "intentionally-dropped": 0, "unaccounted": 0})
        e = PhaseEWhatIsNoContent.by_source(r)
        self.assertEqual(e["src#/rule/optional"]["destinations"], [{"object": "https://ex.org/r1", "pointer": "/optional"}])
        self.assertEqual(e["src#/rule/weight"]["destinations"], [{"object": "https://ex.org/r1", "pointer": "/weight"}])

    def test_without_the_argument_they_are_plain_as_before(self):
        r = self.run_ledger(self.convert, typed=False)
        e = PhaseEWhatIsNoContent.by_source(r)
        self.assertEqual([e[f"src#/rule/{k}"]["outcome"] for k in ("required", "optional", "weight", "count")],
                         ["unaccounted", "unaccounted", "unaccounted", "copied"])

    def test_what_is_written_is_a_plain_boolean_and_the_same_bytes(self):
        led = Ledger(); src = led.source("src", copy.deepcopy(self.SOURCE), typed=True)
        objects = self.convert(src, led)
        with self.assertRaises(TypeError): json.dumps(objects)       # a converter that forgets resolve() writes nothing
        led.resolve(objects)
        obj = objects["o/r1.json"]
        self.assertIs(obj["required"], True); self.assertIs(obj["optional"], False)
        self.assertEqual(json.dumps(obj), '{"id": "https://ex.org/r1", "required": true, "optional": false, "weight": 0.75, "count": 3}')

    def test_a_tracked_boolean_is_true_and_false_as_its_value_is(self):
        led = Ledger(); r = led.source("src", copy.deepcopy(self.SOURCE), typed=True)["rule"]
        self.assertTrue(r["required"]); self.assertFalse(r["optional"])
        self.assertEqual((r["required"] == True, r["optional"] == False, r["optional"] != True), (True, True, True))
        self.assertEqual("yes" if r["optional"] else "no", "no")
        self.assertIs(copy.deepcopy(r["optional"]), r["optional"], "a copy keeps the trace")

    def test_a_boolean_is_checked_against_the_written_file_with_its_type(self):
        def flipped(o): o["optional"] = True; return o
        r = self.run_ledger(self.convert, tamper=flipped)
        self.assertEqual([f["source"] for f in r["verification-failures"]], ["src#/rule/optional"])
        def as_number(o): o["required"] = 1; o["weight"] = "0.75"; return o
        r = self.run_ledger(self.convert, tamper=as_number)
        self.assertEqual(sorted(f["source"] for f in r["verification-failures"]), ["src#/rule/required", "src#/rule/weight"])

    def test_a_boolean_in_a_list_and_one_made_by_a_rule(self):
        def convert(src, led):
            r = src["rule"]
            return {"o/r1.json": {"id": "https://ex.org/r1", "flags": [r["required"], r["optional"]],
                                  "free": led.derive("optional or not required", lambda a, b: bool(a) or not b, r["optional"], r["required"]),
                                  "share": led.derive("the weight in percent", lambda w: w * 100, r["weight"])}}
        r = self.run_ledger(convert)
        e = PhaseEWhatIsNoContent.by_source(r)
        self.assertEqual(r["verification-failures"], [])
        self.assertEqual(e["src#/rule/optional"]["destinations"],
                         [{"object": "https://ex.org/r1", "pointer": "/flags/1"},
                          {"object": "https://ex.org/r1", "pointer": "/free", "rule": "optional or not required"}])
        self.assertEqual(e["src#/rule/weight"]["destinations"], [{"object": "https://ex.org/r1", "pointer": "/share", "rule": "the weight in percent"}])
        def wrong(o): o["free"] = True; return o
        self.assertEqual(len(self.run_ledger(convert, tamper=wrong)["verification-failures"]), 2, "both inputs of the rule")


class PhaseETheGate(unittest.TestCase):
    """"A converter run with an unaccounted value exits non-zero" (author,
    2026-11-14)."""
    def result(self, unaccounted=0, failures=0):
        return {"totals": {"copied": 5, "transformed": 0, "not-content": 0, "intentionally-dropped": 0, "unaccounted": unaccounted},
                "verification-failures": [{}] * failures}

    def test_a_run_with_nothing_unaccounted_goes_on(self):
        self.assertIsNone(ledger_gate(self.result(), "convert_x.py"))

    def test_one_unaccounted_value_ends_the_run_with_a_message(self):
        with self.assertRaises(SystemExit) as c: ledger_gate(self.result(unaccounted=1), "convert_x.py")
        self.assertIn("convert_x.py", str(c.exception)); self.assertIn("1 source value(s) unaccounted", str(c.exception))
        self.assertNotEqual(c.exception.code, 0)

    def test_a_claim_that_does_not_hold_ends_the_run_too(self):
        with self.assertRaises(SystemExit) as c: ledger_gate(self.result(failures=2), "convert_x.py")
        self.assertIn("2 claim(s) that do not hold", str(c.exception))

    def test_the_exit_code_of_a_process_is_one(self):
        import subprocess
        code = ("import sys; sys.path.insert(0, %r)\nfrom oscal_conv_lib import ledger_gate\n"
                "ledger_gate({'totals': {'unaccounted': 3}, 'verification-failures': []}, 'convert_x.py')\n") % os.path.dirname(os.path.abspath(__file__))
        p = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
        self.assertEqual(p.returncode, 1); self.assertIn("3 source value(s) unaccounted", p.stderr)


class PhaseEKeysThatAreSourceValues(unittest.TestCase):
    """ledger_by_path(collapse=...): a payload keyed by a source value gives
    one row per key unless the key is collapsed (SP 800-53: 741 kB)."""
    def test_a_key_made_of_a_source_value_is_one_row(self):
        src = {"params": [{"id": "ac-01_odp.01", "label": "frequency"}, {"id": "ac-01_odp.02", "label": "personnel"}]}
        led = Ledger(); doc = led.source("cat", copy.deepcopy(src))
        obj = {"id": "https://ex.org/ac-1", "facets": {"odp": {p["id"]: {"label": p["label"]} for p in doc["params"]}}}
        out = tempfile.mkdtemp()
        with open(os.path.join(out, "o.json"), "w", encoding="utf-8") as f: json.dump(obj, f)
        full = led.account(out, {"o.json": obj})
        rows = {(r["path"], r["outcome"]): r for r in ledger_by_path(full)["paths"]}
        self.assertEqual(len(rows[("cat.params[].label", "copied")]["to"]), 2)
        short = ledger_by_path(full, collapse=[(r"^(/facets/odp)/[^/]+", r"\1/{param id}")])
        rows = {(r["path"], r["outcome"]): r for r in short["paths"]}
        self.assertEqual(rows[("cat.params[].label", "copied")]["to"], [{"pointer": "/facets/odp/{param id}/label", "count": 2}])
        self.assertEqual(rows[("cat.params[].id", "copied")]["to"], [{"pointer": "/facets/odp/{param id}", "count": 2, "as": "key"}])


class PhaseEOrphans(unittest.TestCase):
    """The author's fourth class of what may stay out of a bundle
    (2026-11-14): "orphaned elemente braucht niemand" - a back-matter
    resource nothing in its document refers to. The ledger checks that
    nothing does."""

    SOURCE = {"uuid": "00000000-0000-4000-8000-00000000000a",
              "metadata": {"links": [{"href": "#00000000-0000-4000-8000-000000000002", "rel": "latest-version"}]},
              "controls": [{"id": "c-1", "prose": "See [the guide](#00000000-0000-4000-8000-000000000001)."}],
              "back-matter": {"resources": [
                  {"uuid": "00000000-0000-4000-8000-000000000001", "title": "The guide", "rlinks": [{"href": "https://example.org/guide"}]},
                  {"uuid": "00000000-0000-4000-8000-000000000002", "title": "The latest version"},
                  {"uuid": "00000000-0000-4000-8000-000000000003", "title": "Nobody names this", "rlinks": [{"href": "https://example.org/x"}],
                   "remarks": "Listed as #00000000-0000-4000-8000-000000000003 in the printed edition."},
                  {"uuid": "00000000-0000-4000-8000-00000000000a", "title": "Has the document's own uuid"}]}}

    def run_ledger(self, orphans, carry=(0, 1), source=None):
        def convert(src, led):
            res = src["back-matter"]["resources"]
            for i in orphans: led.orphan(res[i]["uuid"], "a back-matter resource nothing in the document refers to")
            return {"o/root.json": {"id": "https://ex.org/root", "uuid": src["uuid"], "links": src["metadata"]["links"],
                                    "prose": src["controls"][0]["prose"], "ctl": src["controls"][0]["id"],
                                    "resources": [res[i] for i in carry]}}
        return PhaseEWhatIsNoContent.run_ledger(self, convert, source=source or self.SOURCE)

    def test_a_resource_nothing_refers_to_stays_out_by_a_checked_rule(self):
        r = self.run_ledger(orphans=(2, 3))
        self.assertEqual((r["totals"]["unaccounted"], r["verification-failures"]), (0, []))
        e = PhaseEWhatIsNoContent.by_source(r)
        self.assertEqual({k: e["src#/back-matter/resources/2/title"][k] for k in ("outcome", "kind")}, {"outcome": "not-content", "kind": "orphan"})
        self.assertEqual(e["src#/back-matter/resources/2/rlinks/0/href"]["kind"], "orphan", "every leaf of the element")
        self.assertEqual(e["src#/back-matter/resources/2/remarks"]["outcome"], "not-content", "its own text naming itself is no reference from outside")
        self.assertEqual(r["totals"]["not-content"], 6)
        self.assertEqual(e["src#/back-matter/resources/3/uuid"]["outcome"], "not-content",
                         "equal to the document's own uuid, which is no reference to it")

    def test_a_resource_a_text_or_a_metadata_link_names_is_no_orphan(self):
        for i, source in ((0, "src#/back-matter/resources/0/title"), (1, "src#/back-matter/resources/1/title")):
            r = self.run_ledger(orphans=(i, 2, 3), carry=tuple({0, 1} - {i}))
            e = PhaseEWhatIsNoContent.by_source(r)
            self.assertEqual(e[source]["outcome"], "unaccounted")
            self.assertEqual({f["claim"] for f in r["verification-failures"]}, {"orphan"})
            self.assertEqual(e["src#/back-matter/resources/2/title"]["outcome"], "not-content", "the true orphan is not touched")

    def test_an_orphan_that_is_carried_all_the_same_reads_as_carried(self):
        r = self.run_ledger(orphans=(2, 3), carry=(0, 1, 2))
        self.assertEqual(PhaseEWhatIsNoContent.by_source(r)["src#/back-matter/resources/2/title"]["outcome"], "copied")

    def test_an_undeclared_resource_that_is_not_carried_is_unaccounted(self):
        r = self.run_ledger(orphans=(3,))
        self.assertEqual(r["totals"]["unaccounted"], 4)

    def test_the_rule_is_stated_about_an_elements_own_uuid(self):
        led = Ledger(); src = led.source("src", copy.deepcopy(self.SOURCE))
        with self.assertRaises(TypeError): led.orphan("00000000-0000-4000-8000-000000000003", "a plain string")
        with self.assertRaises(ValueError): led.orphan(src["uuid"], "the document itself")


class PhaseEOneCompatSchemaAndTheLifecycleDefault(unittest.TestCase):
    def test_every_bundle_pins_the_same_compat_schema(self):
        a, b = Bundle(tempfile.mkdtemp(), "a"), Bundle(tempfile.mkdtemp(), "b")
        a.pin_compat(); b.pin_compat()
        self.assertEqual(json.dumps(a.schemas), json.dumps(b.schemas))
        pin = a.schemas["schemas/" + COMPAT_FILE]
        self.assertEqual((pin["id"], pin["version"], pin["schema"]["additionalProperties"]), (COMPAT_ID, "1.1.0", False))
        self.assertEqual(COMPAT, COMPAT_ID + "@1")
        # every member a converter wrote under 1.0.0 (ISM, Grundschutz++, CSF, SP 800-53, CR26) is a member of it
        for member in ("group-parts", "props", "nested-in", "metadata", "back-matter", "catalog", "param-extras", "parts", "links",
                       "control", "group", "unmapped", "merge", "class", "class-variants", "ctl"):
            self.assertIn(member, pin["schema"]["properties"])

    def test_the_lifecycle_a_converter_writes_on_its_own_is_counted_and_named(self):
        objs = {"a": {"id": "x/a", "lifecycle": "active"}, "b": {"id": "x/b", "lifecycle": "withdrawn"}, "c": {"id": "x/c", "lifecycle": "active"},
                "m": {"objects": []}}
        r = lifecycle_default_record(objs, stated=["x/b"])
        self.assertEqual(r, {"value": "active", "origin": "converter-default", "objects": 2, "source-states": 1})
        self.assertIn("`active` on 2 object(s) is the converter's default", lifecycle_default_line(r))
        self.assertIn("On 1 object(s) the lifecycle is the source's own status", lifecycle_default_line(r))
        with self.assertRaises(SystemExit): lifecycle_default_record(objs, stated=[])     # `withdrawn` by nobody's word


if __name__ == "__main__":
    unittest.main()
