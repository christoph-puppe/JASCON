#!/usr/bin/env python3
"""Regression tests for oscal_conv_lib.global_occurrence, the value-level
measurement of the converters' coverage reports.

    python3 jascon/scripts/test_oscal_conv_lib.py

Each test is named after the report that found the defect (issues 32 and 33
in the GitHub tracker of the repository, 2026-11-13). Until that day the
function was `value_arrival`: it joined every output key and scalar into one
string and tested substring membership, so the six cases of issue 32 gave
five false arrivals and one false absence. Standard library only."""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from oscal_conv_lib import global_occurrence


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


if __name__ == "__main__":
    unittest.main()
