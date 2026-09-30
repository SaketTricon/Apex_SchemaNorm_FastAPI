# CSV statistical profiling

The service reads one complete CSV and calculates a profile for each column.
`build_report.py` exports the profile as CSV, with one report row per source
column. `statistical_profiler.py` exports the same statistics as JSON.
Both commands use Python's standard library and leave the input unchanged.

## Generate a report

From the repository root:

```bash
python build_report.py
```

The default input is `examples/vendor_customers.csv`, using `examples/config.json`.
The output is `examples/vendor_customers.report.csv` (10 source rows, 8 columns).

To run the additional 12-row synthetic test file:

```bash
python build_report.py examples/customers_test.csv --config examples/config.json
```

This creates `examples/customers_test.report.csv` with 8 report rows. It includes
11 distinct customer IDs, 2 missing ages, 1 invalid age, 1 invalid balance, an
invalid calendar date, and an entirely empty column. The valid age average is
34.444444… and the valid balance average is 122.222222….

For another file or output location:

```bash
python build_report.py path/to/input.csv --config path/to/config.json --output report.csv
python statistical_profiler.py path/to/input.csv --config path/to/config.json --output profile.json
```

Existing output files are not overwritten. Select a new output name for another
run. A malformed CSV fails before the report is created.

Custom inputs default to text columns without `--config`. Only the default
vendor sample automatically uses the bundled configuration. The JSON CLI always
requires an explicit `--config` to apply settings.

## Configuration

Example configuration for a file containing `customer_id`, `age`, and `joined`:

```json
{
  "column_types": {
    "customer_id": "string",
    "age": "number",
    "joined": "date"
  },
  "null_tokens": ["", "NULL"]
}
```

Supported settings are `column_types`, `null_tokens`, `delimiter`, `encoding`, and
`max_distinct_values`. Column types are `string`, `number`, and `date`; dates use
`YYYY-MM-DD`. UTF-8 with an optional BOM is the default encoding. Numeric-looking
identifiers remain text unless explicitly configured otherwise.

## Metric definitions

| Metric | Definition |
| --- | --- |
| Row count | Parsed data records, excluding header and completely blank records |
| Null count / percentage | Missing values / all data rows × 100 |
| Distinct count | Different non-null raw field values |
| Distinct percentage | Distinct count / non-null count × 100 |
| Distinct percentage of all rows | Distinct count / row count × 100 |
| Duplicate value excess count | Non-null count minus distinct count; not a duplicate-row count |
| Valid / invalid count | Non-null fields that pass / fail their configured type |
| Invalid percentage | Invalid count / non-null count × 100 |
| Min / max | Extrema of valid typed values; strings use Unicode lexicographic order |
| Average | Valid numeric sum / valid numeric count |
| Length min / max / average | Unicode code-point counts of original non-null fields |
| Unique and non-null | Every row has a populated value and raw values are unique in this file |

Null matching strips surrounding whitespace and is case-sensitive. The default
null token is the empty string; the samples also configure uppercase `NULL`.
Literal `NA`, zero, and false are not null by default. Invalid numbers and dates
are non-null: they still participate in raw distinct and length statistics but
are excluded from typed extrema and averages. Distinct comparison preserves case,
whitespace, and numeric representations (`1`, `1.0`, and `01` are distinct).

Unavailable statistics are empty fields in the CSV report and null in JSON.
Percentages use the 0–100 scale. Decimal calculations use 50 significant digits;
JSON numeric extrema and averages are strings to avoid binary floating-point
conversion. CSV fields preserve these decimal representations and leading zeros
on disk; spreadsheet applications may infer their own display types when opening
CSV. Reports contain raw source extrema, so treat them as source-derived data.

## Service integration

```python
from app.services.statistical_profiler import profile_csv

statistics = profile_csv(
    "vendor.csv",
    column_types={"customer_id": "string", "balance": "number"},
    null_tokens=["", "NULL"],
)
```

The service returns a dictionary. This change adds the reusable service and CLI;
an HTTP upload endpoint is not included. A future API adapter should run large
scans outside the asynchronous request handler and apply its upload limits.

The profiler streams records but stores exact distinct values in memory. The
default cap is 1,000,000 distinct entries across all columns; exceeding it fails
the scan. This is an entry-count safeguard, not a fixed memory limit. The parser
also rejects blank/duplicate headers, headers with surrounding whitespace,
mismatched record widths, and malformed CSV. Median, standard deviation, automatic
type inference, full-row duplicate detection, and schema/sample merging are not
included.

## Verify

```bash
python -m unittest discover -s tests -v
```

Tests cover hand-calculated results, missing versus invalid values, leading zeros,
dates, Unicode, quoted multiline CSV, structural errors, distinct limits, CSV
report quoting, and protection of source files and existing reports.
