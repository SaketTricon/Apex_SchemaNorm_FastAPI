"""SchemaNorm statistics exploration: a standard-library CSV profiler.

Python 3.10+. No AI calls, source changes, or automatic type inference.
See README.md for the metric contract and prototype limitations.
"""

import argparse
import csv
import json
import re
import sys
from datetime import date
from decimal import Decimal, InvalidOperation, localcontext
from pathlib import Path


class ProfileError(ValueError):
    """Input cannot be profiled under the requested contract."""


NUMBER = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\Z")
ISO_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}\Z")


def percentage(numerator, denominator):
    return round(numerator * 100 / denominator, 6) if denominator else None


def parse_value(value, kind):
    """Parse a non-null value, without changing raw distinct/length metrics."""
    if kind == "string":
        return value
    cleaned = value.strip()
    if kind == "number":
        if not NUMBER.fullmatch(cleaned):
            raise ValueError("Not a decimal number")
        number = Decimal(cleaned)
        # Keep arithmetic bounded for this teaching prototype.
        if not number.is_finite() or len(number.as_tuple().digits) > 100 or abs(number.as_tuple().exponent) > 1000:
            raise ValueError("Number exceeds the prototype's supported range")
        return number
    if not ISO_DATE.fullmatch(cleaned):
        raise ValueError("Expected YYYY-MM-DD")
    return date.fromisoformat(cleaned)


def serialize_value(value):
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, date):
        return value.isoformat()
    return value


class ColumnStats:
    def __init__(self, name, kind):
        self.name, self.kind = name, kind
        self.nulls = self.valid = self.invalid = self.length_total = 0
        self.length_min = self.length_max = self.minimum = self.maximum = None
        self.total = Decimal(0)
        self.distinct = set()

    def add(self, value, null_tokens):
        if value.strip() in null_tokens:
            self.nulls += 1
            return 0
        is_new = value not in self.distinct
        self.distinct.add(value)
        length = len(value)
        self.length_total += length
        self.length_min = length if self.length_min is None else min(self.length_min, length)
        self.length_max = length if self.length_max is None else max(self.length_max, length)
        try:
            parsed = parse_value(value, self.kind)
        except (ValueError, InvalidOperation):
            self.invalid += 1
            return int(is_new)
        self.valid += 1
        self.minimum = parsed if self.minimum is None else min(self.minimum, parsed)
        self.maximum = parsed if self.maximum is None else max(self.maximum, parsed)
        if self.kind == "number":
            self.total += parsed
        return int(is_new)

    def result(self, rows):
        non_null = rows - self.nulls
        distinct = len(self.distinct)
        return {
            "name": self.name,
            "statistical_type": self.kind,
            "row_count": rows,
            "null_count": self.nulls,
            "null_percentage": percentage(self.nulls, rows),
            "non_null_count": non_null,
            "distinct_count": distinct,
            "distinct_percentage": percentage(distinct, non_null),
            "distinct_percentage_of_all_rows": percentage(distinct, rows),
            "duplicate_value_excess_count": non_null - distinct,
            "valid_value_count": self.valid,
            "invalid_value_count": self.invalid,
            "invalid_percentage_of_non_null": percentage(self.invalid, non_null),
            "min": serialize_value(self.minimum),
            "max": serialize_value(self.maximum),
            "average": str(self.total / self.valid) if self.kind == "number" and self.valid else None,
            "length": {
                "unit": "Unicode code points in the original non-null CSV field",
                "min": self.length_min,
                "max": self.length_max,
                "average": round(self.length_total / non_null, 6) if non_null else None,
            },
            "unique_and_non_null_in_this_file": bool(rows and non_null == rows and distinct == rows),
        }


def profile_csv(path, *, column_types=None, null_tokens=None, delimiter=",",
                encoding="utf-8-sig", max_distinct_values=1_000_000):
    """Return complete statistics or raise; never emit a partial exact profile.

    column_types comes from schema profiling / caller configuration. Unspecified
    fields default to string, protecting identifiers and their leading zeros.
    max_distinct_values limits total stored distinct entries across columns.
    """
    path = Path(path)
    column_types = {} if column_types is None else column_types
    null_tokens = [""] if null_tokens is None else null_tokens
    if not isinstance(column_types, dict) or any(
        not isinstance(k, str) or v not in ("string", "number", "date")
        for k, v in column_types.items()
    ):
        raise ProfileError("column_types must map column names to string, number, or date")
    if not isinstance(null_tokens, (list, tuple)) or any(not isinstance(t, str) for t in null_tokens):
        raise ProfileError("null_tokens must be a list of strings")
    if not isinstance(delimiter, str) or len(delimiter) != 1 or delimiter in "\r\n\x00":
        raise ProfileError("delimiter must be one non-newline character")
    if type(max_distinct_values) is not int or max_distinct_values < 1:
        raise ProfileError("max_distinct_values must be a positive integer")
    tokens = {token.strip() for token in null_tokens}
    with localcontext() as context:
        context.prec = 50
        with path.open(encoding=encoding, newline="") as stream:
            reader = csv.reader(stream, delimiter=delimiter, strict=True)
            try:
                headers = next(reader, None)
                if not headers or any(not h.strip() or h != h.strip() for h in headers):
                    raise ProfileError("Expected nonempty headers without surrounding whitespace")
                if len(set(headers)) != len(headers):
                    raise ProfileError("Duplicate column headers are not supported")
                if set(column_types) - set(headers):
                    raise ProfileError("column_types contains names absent from the CSV header")
                columns = [ColumnStats(h, column_types.get(h, "string")) for h in headers]
                rows = skipped_blank_records = distinct_entries = 0
                for record in reader:
                    if not record:
                        skipped_blank_records += 1
                        continue
                    if len(record) != len(headers):
                        raise ProfileError(f"CSV record ending at line {reader.line_num} has {len(record)} fields; expected {len(headers)}")
                    rows += 1
                    for column, value in zip(columns, record):
                        distinct_entries += column.add(value, tokens)
                        if distinct_entries > max_distinct_values:
                            raise ProfileError("Exact distinct-value limit exceeded; use a disk-backed approach or deliberately raise the limit")
            except csv.Error as error:
                raise ProfileError(f"Invalid CSV near line {reader.line_num}: {error}") from error
        results = [column.result(rows) for column in columns]
    return {
        "profile_version": "1.0",
        "source_file": path.name,
        "row_count": rows,
        "column_count": len(columns),
        "scan": {"mode": "full", "sampled": False, "skipped_blank_records": skipped_blank_records},
        "policy": {
            "null_tokens": sorted(tokens),
            "null_matching": "case-sensitive after stripping surrounding whitespace",
            "distinct_basis": "original non-null text, case-sensitive; no trimming or type conversion",
            "distinct_percentage_denominator": "non_null_count",
            "numeric_summary_basis": "valid parsed non-null values only",
            "numeric_json_representation": "decimal strings; arithmetic precision 50 significant digits",
            "date_format": "YYYY-MM-DD",
            "string_order": "Unicode code point lexicographic order",
            "max_distinct_values_across_columns": max_distinct_values,
        },
        "columns": results,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--config", type=Path, help="JSON object containing profile_csv keyword arguments")
    parser.add_argument("--output", type=Path, help="Write JSON to a new file (default: stdout)")
    args = parser.parse_args()
    try:
        config = json.loads(args.config.read_text(encoding="utf-8")) if args.config else {}
        allowed = {"column_types", "null_tokens", "delimiter", "encoding", "max_distinct_values"}
        if not isinstance(config, dict) or set(config) - allowed:
            raise ProfileError("Config must be an object containing only supported settings")
        profile = profile_csv(args.csv_path, **config)
        payload = json.dumps(profile, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
        if args.output:
            # Avoid overwriting source data or a previously generated report.
            with args.output.open("x", encoding="utf-8") as output:
                output.write(payload)
        else:
            print(payload, end="")
    except (OSError, ValueError, LookupError, TypeError) as error:
        print(f"Profiling failed: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
