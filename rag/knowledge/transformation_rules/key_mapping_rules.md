# Primary-key and foreign-key mapping rules

## Purpose

Guide key selection and relationship mapping using profile evidence without overstating what the profile proves.

## Candidate-key evidence

- A column that is non-null and 100% unique in the observed rows is a candidate-key signal.
- Two individually unique columns may both be candidate keys; choose one primary key and consider the other an alternate unique key.
- If no single field is unique, investigate a composite key using the source row grain and business rules.
- Consider a surrogate target key when source identifiers are mutable, sensitive, inconsistent, or scoped to another system; preserve source identifiers and lineage for reconciliation.

## Foreign-key evidence

- Matching names, compatible types, and overlapping values suggest a possible relationship.
- Validate that every non-null source value maps to the intended referenced key and assess unmatched values.
- Confirm relationship direction and cardinality from row grain and business rules.
- If one source key appears to match multiple tables, investigate each match and identify the authoritative target relationship rather than choosing one by name alone.

## Important constraints

- Observed uniqueness is not proof of a declared primary key.
- Value overlap alone is not proof of a foreign-key constraint.
- A small sample may hide duplicates, nulls, or out-of-domain values.
- Do not drop or rewrite source identifiers without an explicit mapping and reconciliation plan.

## Retrieval keywords

candidate primary key, alternate key, natural key, surrogate key, foreign-key inference, referential integrity, composite key, key mapping, value overlap, cardinality
