# Missing reference entities

## Purpose

Identify source identifiers that appear to reference a product, category, department, status, or other entity for which no reference table is present.

## Detection signals

- a column such as `product_id` or `department_id` is typed or named like an identifier
- the value repeats across transactional rows
- related descriptive attributes are absent from the source table
- no corresponding entity table is present in the profiled schema

## Recommended investigation

1. Check whether the identifier matches a key in any profiled table.
2. Inspect constraints, application metadata, and source-system documentation when available.
3. Determine whether the reference entity exists outside the profiled dataset.
4. Establish whether values are stable business identifiers, source-local codes, or free-form labels.
5. Record unresolved references and request the missing domain definition or source data.

## Recommendation

Flag a possible missing reference entity and show the evidence. Do not invent entity attributes, create fabricated reference rows, or claim a foreign key when the target table and semantics are unknown. A target design may reserve a relationship for the missing entity, but it should be marked as conditional until confirmed.

## Retrieval keywords

missing reference table, missing product table, orphan identifier, unresolved foreign key, product_id, absent dimension, source schema gap, unknown reference entity
