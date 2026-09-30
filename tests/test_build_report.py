import csv
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from build_report import ROOT, build_report
from app.services.statistical_profiler import ProfileError


class ReportTests(unittest.TestCase):
    def test_default_cli_uses_vendor_sample_configuration(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "report.csv"
            run = subprocess.run(
                [sys.executable, str(ROOT / "build_report.py"), "--output", str(output)],
                cwd=folder, capture_output=True, text=True,
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            with output.open(newline="", encoding="utf-8") as stream:
                cols = {row["name"]: row for row in csv.DictReader(stream)}
            self.assertEqual(cols["BALANCE"]["source_file"], "vendor_customers.csv")
            self.assertEqual(cols["BALANCE"]["row_count"], "10")
            self.assertEqual(cols["BALANCE"]["average"], "125.00")

    def test_custom_cli_defaults_to_text(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "custom.csv"
            source.write_text("id\n0001\n0002\n", encoding="utf-8")
            run = subprocess.run(
                [sys.executable, str(ROOT / "build_report.py"), str(source)],
                cwd=folder, capture_output=True, text=True,
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            with source.with_name("custom.report.csv").open(newline="", encoding="utf-8") as stream:
                row = next(csv.DictReader(stream))
            self.assertEqual(row["statistical_type"], "string")
            self.assertEqual(row["min"], "0001")
            self.assertEqual(row["average"], "")

    def test_sample_cli_generates_expected_statistics(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "report.csv"
            run = subprocess.run(
                [sys.executable, str(ROOT / "build_report.py"),
                 str(ROOT / "examples/customers_test.csv"),
                 "--config", str(ROOT / "examples/config.json"), "--output", str(output)],
                cwd=folder, capture_output=True, text=True,
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            with output.open(newline="", encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(len(rows), 8)
            cols = {row["name"]: row for row in rows}
            self.assertTrue(all(row["row_count"] == "12" for row in rows))
            self.assertEqual(cols["CUST_NO"]["min"], "0001")
            self.assertEqual(cols["CUST_NO"]["distinct_count"], "11")
            self.assertEqual(cols["AGE"]["null_count"], "2")
            self.assertEqual(cols["AGE"]["invalid_value_count"], "1")
            self.assertEqual(Decimal(cols["AGE"]["average"]).quantize(Decimal("0.01")), Decimal("34.44"))
            self.assertEqual(Decimal(cols["BALANCE"]["average"]).quantize(Decimal("0.01")), Decimal("122.22"))
            self.assertEqual(cols["JOIN_DATE"]["invalid_value_count"], "1")
            self.assertEqual(cols["UNUSED"]["null_percentage"], "100.0")
            self.assertEqual(cols["UNUSED"]["min"], "")
            self.assertEqual(cols["PHONE"]["length_min"], "11")

    def test_report_round_trips_csv_special_characters(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "source.csv"
            output = Path(folder) / "report.csv"
            value = 'Zoë, "hello"\nworld'
            with source.open("w", newline="", encoding="utf-8") as stream:
                csv.writer(stream).writerows([["text"], [value]])
            build_report(source, output)
            with output.open(newline="", encoding="utf-8") as stream:
                row = next(csv.DictReader(stream))
            self.assertEqual(row["min"], value)
            self.assertEqual(row["max"], value)
            self.assertEqual(row["average"], "")

    def test_preserves_source_and_existing_reports(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "source.csv"
            source.write_text("id\n0001\n", encoding="utf-8")
            output = Path(folder) / "report.csv"
            output.write_text("existing report", encoding="utf-8")
            for target in (source, output):
                before = target.read_bytes()
                with self.assertRaises(FileExistsError):
                    build_report(source, target)
                self.assertEqual(target.read_bytes(), before)

    def test_invalid_csv_or_config_does_not_create_report(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "source.csv"
            output = Path(folder) / "report.csv"
            source.write_text("x,y\n1\n", encoding="utf-8")
            with self.assertRaises(ProfileError):
                build_report(source, output)
            self.assertFalse(output.exists())
            for config in ([], {"unexpected": True}):
                with self.subTest(config=config), self.assertRaises(ProfileError):
                    build_report(source, output, config=config)
                self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
