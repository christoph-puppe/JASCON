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
from oscal_conv_lib import global_occurrence, Ledger, slug


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

    def test_tracking_changes_nothing_that_is_written(self):
        source = {"n": 27017, "s": "text", "nested": [{"k": "v"}]}
        led = Ledger(); tracked = led.source("src", source)
        self.assertEqual(json.dumps(tracked), json.dumps(source))
        self.assertIs(copy.deepcopy(tracked["s"]), tracked["s"], "a copy keeps the trace")
        self.assertEqual((type(tracked["n"] + 1), type(tracked["s"].strip())), (int, str), "a computed value is plain")
        with self.assertRaises(TypeError): led.derive("to a list", lambda s: [s], tracked["s"])


if __name__ == "__main__":
    unittest.main()
