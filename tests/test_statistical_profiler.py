import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from app.services.statistical_profiler import ProfileError, profile_csv


class StatisticsTests(unittest.TestCase):
    def profile(self, text, **kwargs):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "input.csv"
            path.write_text(text, encoding="utf-8")
            return profile_csv(path, **kwargs)

    def test_demo_hand_calculated_results(self):
        folder = Path(__file__).resolve().parents[1] / "examples"
        config = json.loads((folder / "config.json").read_text())
        result = profile_csv(folder / "vendor_customers.csv", **config)
        cols = {c["name"]: c for c in result["columns"]}
        self.assertEqual(result["row_count"], 10)
        self.assertEqual(cols["CUST_NO"]["distinct_count"], 9)
        self.assertEqual(cols["CUST_NO"]["min"], "0001")
        self.assertIsNone(cols["CUST_NO"]["average"])
        self.assertFalse(cols["CUST_NO"]["unique_and_non_null_in_this_file"])
        self.assertEqual(cols["AGE"]["null_count"], 2)
        self.assertEqual(cols["AGE"]["invalid_value_count"], 1)
        self.assertEqual(Decimal(cols["AGE"]["average"]).quantize(Decimal("0.000001")), Decimal("34.285714"))
        self.assertEqual(cols["BALANCE"]["min"], "-20.00")
        self.assertEqual(cols["BALANCE"]["average"], "125.00")
        self.assertEqual(cols["BALANCE"]["distinct_percentage"], 88.888889)
        self.assertEqual(cols["BALANCE"]["distinct_percentage_of_all_rows"], 80.0)
        self.assertEqual(cols["JOIN_DATE"]["invalid_value_count"], 1)
        self.assertEqual(cols["UNUSED"]["null_percentage"], 100)
        self.assertIsNone(cols["UNUSED"]["distinct_percentage"])
        self.assertEqual(cols["ST_CD"]["null_count"], 0)
        json.dumps(result, allow_nan=False)

    def test_distinct_is_not_singleton_count(self):
        c = self.profile('x\nA\nA\nB\n""\n')["columns"][0]
        self.assertEqual(c["distinct_count"], 2)
        self.assertEqual(c["duplicate_value_excess_count"], 1)
        self.assertEqual(c["distinct_percentage"], 66.666667)
        self.assertEqual(c["distinct_percentage_of_all_rows"], 50)

    def test_defaults_preserve_ids_na_and_whitespace(self):
        c = self.profile('x\n001\n1\nNA\nNULL\n A \nA\n"  "\n')["columns"][0]
        self.assertEqual(c["distinct_count"], 6)
        self.assertEqual(c["null_count"], 1)
        self.assertEqual(c["length"]["max"], 4)
        self.assertIsNone(c["average"])

    def test_header_only_and_all_null_have_no_fake_zero_average(self):
        for text in ['x\n', 'x\n""\n" "\n']:
            c = self.profile(text, column_types={"x": "number"})["columns"][0]
            self.assertIsNone(c["average"])
            self.assertIsNone(c["min"])
            self.assertIsNone(c["distinct_percentage"])
            self.assertFalse(c["unique_and_non_null_in_this_file"])

    def test_invalid_numbers_are_not_null_and_not_in_average(self):
        c = self.profile('x\n0.1\n0.2\nNaN\nInfinity\n1_000\n', column_types={"x": "number"})["columns"][0]
        self.assertEqual(c["average"], "0.15")
        self.assertEqual(c["invalid_value_count"], 3)
        self.assertEqual(c["null_count"], 0)

    def test_date_validation_and_raw_distinct_semantics(self):
        c = self.profile('x\n2024-02-29\n2023-02-29\n20240101\n', column_types={"x": "date"})["columns"][0]
        self.assertEqual(c["invalid_value_count"], 2)
        self.assertEqual(c["min"], "2024-02-29")
        c = self.profile('x\n1\n1.0\n01\n', column_types={"x": "number"})["columns"][0]
        self.assertEqual(c["distinct_count"], 3)
        self.assertEqual(Decimal(c["average"]), 1)

    def test_quoted_multiline_bom_unicode_and_blank_record(self):
        result = self.profile('\ufeffname,note\nZoë,"hello,\nworld"\n\n,\n')
        self.assertEqual(result["row_count"], 2)
        self.assertEqual(result["scan"]["skipped_blank_records"], 1)
        self.assertEqual(result["columns"][0]["length"]["max"], 3)
        self.assertEqual(result["columns"][1]["length"]["max"], 12)

    def test_bad_structure_is_rejected(self):
        for text in ["", "x,x\n1,2\n", "x,y\n1\n", "x\n1,2\n", 'x\n"unterminated', " x\n1\n"]:
            with self.subTest(text=text), self.assertRaises(ProfileError):
                self.profile(text)

    def test_distinct_cap_rejects_instead_of_returning_partial_counts(self):
        with self.assertRaisesRegex(ProfileError, "distinct-value limit"):
            self.profile("x,y\na,a\nb,b\n", max_distinct_values=3)

    def test_explicit_null_policy_and_delimiter(self):
        c = self.profile('x;y\nNULL;1\nnull;2\n', null_tokens=["NULL"], delimiter=";")["columns"][0]
        self.assertEqual(c["null_count"], 1)
        self.assertEqual(c["distinct_count"], 1)

    def test_unknown_types_and_columns_are_rejected(self):
        for config in [{"column_types": {"x": "integer"}}, {"column_types": {"missing": "number"}}, {"max_distinct_values": 0}]:
            with self.subTest(config=config), self.assertRaises(ProfileError):
                self.profile("x\n1\n", **config)


if __name__ == "__main__":
    unittest.main()
