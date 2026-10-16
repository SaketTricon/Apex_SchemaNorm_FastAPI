# Schema smells and data-quality signals

## Purpose

A source schema may contain patterns that suggest incorrect denormalization or weak modeling. These are useful signals for investigation, but they are not automatically proof of a `bad` design.

## Common smells

### Repeating groups

Columns such as `phone_1`, `phone_2`, `phone_3`, `email_1`, `email_2`, `email_3` often indicate a repeated-value pattern. A normalized design usually favors a child table such as `CustomerContact` with one row per contact method.

### Delimited values

A single field such as `tags`, `skills`, `emails`, or `product_ids` may contain comma-separated values. This normally indicates a many-to-many or multi-valued attribute, which is often better represented as separate records or a junction table.

### Mixed entity data

A table containing both customer and order facts in the same row may result from a denormalized operational view. The target schema should separate master and transaction data.

### Duplicated descriptive fields

If a table repeats the same description or category value across many rows, that often suggests a lookup table or dimension table, especially when the description is stable but reused frequently.

### Missing identifiers

Columns that appear to identify a row but are missing or inconsistent often cause ambiguous joins and invalid aggregations. A schema recommendation should call out the missing key or the need for surrogate keys.

## Recommended investigation workflow

1. inspect whether a repeated value is truly controlled or free-form
2. determine whether the value belongs to a master entity, a lookup, or a detailed record
3. review whether the value is one-to-many, one-to-one, or many-to-many
4. validate the expected cardinality before recommending a split

## Retrieval keywords

schema smell, repeated columns, delimited values, mixed entity table, missing keys, denormalization warning, repeated descriptions, multi-valued attribute, junction table signal
