"""Read a CSV and write a statistics report CSV with one row per column.

Defaults to examples/vendor_customers.csv with examples/config.json.
Custom CSV inputs default to text columns unless --config is supplied.
"""

import argparse
import csv
import json
import sys
from pathlib import Path

from app.services.statistical_profiler import ProfileError, profile_csv

ROOT = Path(__file__).resolve().parent
DEFAULT_INPUT = ROOT / "examples" / "vendor_customers.csv"
CONFIG_KEYS = {"column_types", "null_tokens", "delimiter", "encoding", "max_distinct_values"}
COLUMN_FIELDS = [
    "name", "statistical_type", "row_count", "null_count", "null_percentage",
    "non_null_count", "distinct_count", "distinct_percentage",
    "distinct_percentage_of_all_rows", "duplicate_value_excess_count",
    "valid_value_count", "invalid_value_count", "invalid_percentage_of_non_null",
    "min", "max", "average", "unique_and_non_null_in_this_file",
]
REPORT_FIELDS = ["source_file", *COLUMN_FIELDS, "length_min", "length_max", "length_average"]


def build_report(csv_path, output_path, *, config=None):
    """Profile before creating output; preserve input and existing reports.

    Missing or inapplicable metrics become empty CSV fields.
    """
    config = {} if config is None else config
    if not isinstance(config, dict) or set(config) - CONFIG_KEYS:
        raise ProfileError("Config must be an object containing only supported settings")
    profile = profile_csv(csv_path, **config)
    with Path(output_path).open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=REPORT_FIELDS)
        writer.writeheader()
        for column in profile["columns"]:
            row = {field: column[field] for field in COLUMN_FIELDS}
            row["source_file"] = profile["source_file"]
            row.update({f"length_{key}": column["length"][key] for key in ("min", "max", "average")})
            writer.writerow(row)
    return profile


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", nargs="?", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--config", type=Path, help="JSON settings for column types, null tokens, etc.")
    parser.add_argument("--output", type=Path, help="New output file; defaults to <input_name>.report.csv")
    args = parser.parse_args(argv)
    output_path = args.output if args.output is not None else args.csv_path.with_name(
        f"{args.csv_path.stem}.report.csv"
    )
    try:
        config_path = args.config
        if config_path is None and args.csv_path.resolve() == DEFAULT_INPUT.resolve():
            config_path = ROOT / "examples" / "config.json"
        config = json.loads(config_path.read_text(encoding="utf-8")) if config_path else {}
        profile = build_report(args.csv_path, output_path, config=config)
    except (OSError, ValueError, LookupError, TypeError) as error:
        print(f"Report failed: {error}", file=sys.stderr)
        return 2
    print(f"Processed {profile['row_count']} input rows and {profile['column_count']} columns.")
    print(f"CSV report: {output_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
