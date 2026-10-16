# Data type, null, and identifier transformation rules

## Purpose

A normalized schema recommendation is not complete if it ignores source value formats, nullability, and identifier semantics. The migration layer must convert data without losing meaning or inventing invalid values.

## Common transformation patterns

- `ZIP` or `POSTAL_CODE` stored as integers should be converted to strings when leading zeroes matter
- phone numbers should generally be stored as strings, not arithmetic numbers, to preserve leading zeros, country codes, extensions, and formatting
- `DATE` values stored as text should be parsed and validated before mapping to typed date columns
- boolean flags stored as `Y/N`, `1/0`, or text labels should be normalized to a canonical boolean or lookup value
- monetary values should use an exact decimal representation with an explicit precision and scale; confirm currency and rounding rules before migration
- customer numbers or order numbers should remain distinct from surrogate keys when a business identifier is required
- missing values should be classified as `NULL`, unknown, or defaulted only when the domain and validation rules support that decision

## Example

Source values:

- `"00123"`, `123`, `NULL`, `"N/A"`

Target logic:

- preserve leading zeros in `postal_code` when the domain expects them
- use `NULL` for absence when the business means no postal code exists
- treat `"N/A"` as a known invalid or placeholder value only if the source system defines it that way

## Detection signals

- mixed numeric and text representations in the same column
- the same semantic field has different source types across tables, such as a phone number stored as text in one table and an integer in another
- inconsistent date formats or boolean flags across records
- values that look like IDs but are not consistently unique
- source fields that change meaning depending on the table or row

## Recommendation

Always record the source value, the transformation rule, and the target field. A schema recommendation should not silently coerce values if the conversion affects uniqueness, validation, or downstream reporting.

## Retrieval keywords

data type mapping, null handling, date conversion, string to integer, postal code formatting, phone number type, leading zeros, currency precision, decimal type, identifier preservation, business key, source values, transformation rule
