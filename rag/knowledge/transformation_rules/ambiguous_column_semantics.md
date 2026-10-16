# Ambiguous column semantics

## Purpose

Prevent a schema recommendation from inventing business meaning based only on a column name, inferred type, or value distribution.

## Common ambiguous fields

- `membership` may be a yes/no flag, a membership tier, or an enrollment state.
- `status` may refer to different lifecycle concepts in different tables.
- `category` may describe a customer segment, product class, or another domain.
- `notes` may contain free text, repeated codes, placeholders, or generated labels.
- a numeric field may be a measurement, amount, count, or identifier.

## Investigation steps

1. Inspect distinct observed values and representative redacted examples.
2. Compare the field across tables, including data type, nullability, and value domain.
3. Check source-system documentation, constraints, and application behavior.
4. Identify whether values are controlled codes, free text, or derived labels.
5. Ask the domain owner when available; record unresolved meanings explicitly.

## Recommendation

Do not rename or transform an ambiguous column into a more specific target concept until its meaning is supported by evidence. Retain the source name, record the proposed interpretation as a hypothesis, and preserve a reversible source-to-target mapping.

## Retrieval keywords

ambiguous column, unknown semantics, membership flag, boolean-like field, status meaning, category meaning, notes column, inferred type, column interpretation, preserve source name, semantic uncertainty
