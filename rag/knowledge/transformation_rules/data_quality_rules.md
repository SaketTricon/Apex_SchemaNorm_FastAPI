# Data profiling and quality interpretation rules

## Purpose

Interpret profiler statistics as evidence about a dataset, not as definitive business rules.

## Uniqueness and cardinality

- High uniqueness may indicate an identifier, event, timestamp, or genuinely unique attribute.
- Low cardinality may indicate a category, flag, repeated description, or constrained domain.
- Neither uniqueness nor low cardinality establishes the business meaning of a column.

## Null values

- Null percentages describe observed missingness; nulls may be valid, unknown, inapplicable, or a data-quality issue.
- Do not automatically replace nulls with defaults, drop a column, or delete rows.
- Preserve distinctions among null, empty string, sentinel values, and invalid values when the source semantics are unknown.

## Categorical and boolean-like fields

- Two distinct values may indicate a binary attribute, but values and business meaning must be inspected.
- A low-cardinality field may be a lookup candidate when the domain is controlled and reused.
- Do not turn every category into a separate lookup table; consider governance and business use.

## Timestamps and repeated attributes

- High uniqueness in a timestamp can indicate event or audit data, but column names and lifecycle meaning need confirmation.
- Names such as `created_at`, `updated_at`, or `last_login` suggest audit or activity semantics; confirm whether the timestamp describes row creation, source-system updates, or a business event before assigning it to a target entity.
- Repeated descriptive values may suggest normalization opportunities, but decomposition requires a functional dependency and meaningful entity boundary.

## Cross-table relationship signals

- A source key matching values in more than one table may indicate overlapping entities, duplicate snapshots, reused identifiers, or an ambiguous source relationship.
- Compare key scope, row grain, value coverage, and source constraints before selecting a target relationship.
- A partial value overlap may be caused by sampling or filtering; do not use it alone to merge tables or declare one table authoritative.

## Ambiguous semantics

- Type labels and names such as `boolean_like`, `membership`, `category`, `status`, or `notes` provide clues, not definitions.
- Inspect observed values, source documentation, and business context before renaming a field or creating a target entity.
- Preserve the original source name and value mapping when meaning remains uncertain.

## Recommended reporting

For each recommendation, state:

1. The observed evidence and its scope (row count, null count, distinct count, and sample limitations).
2. A possible interpretation, clearly labeled as a hypothesis.
3. Confidence and unresolved ambiguity.
4. The additional evidence needed.
5. A safe next action that does not discard source data.

## Retrieval keywords

data profiling, null percentage, cardinality, uniqueness, low cardinality, categorical column, boolean-like, timestamp, audit column, created_at, updated_at, last_login, data quality, schema inference, missing values, sample limitations, ambiguous semantics, overlapping tables
