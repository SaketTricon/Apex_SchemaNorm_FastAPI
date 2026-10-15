# Normalization knowledge

This folder focuses on identifying when a source table should be split into separate entities or relationships.

## Included topics

- 1NF, 2NF, and 3NF concepts
- functional dependencies and transitive dependencies
- repeated values and schema smells
- lookup tables and junction tables
- entity boundary detection for customer, order, product, and address data

## Retrieval emphasis

These documents are designed to help the profiler and LLM answer questions such as:

- Does this table represent a master entity or an operational fact?
- Which columns are repeated and therefore likely belong in a related table?
- Is this a many-to-many relationship or a hidden lookup dimension?
- Are the source columns describing a value that should be modeled as a reference table?

## Core rules

1. Prefer separate tables for stable master entities and repeating data.
2. Treat repeated descriptive values as signals, not proof.
3. Verify whether a data pattern is business-driven, not just syntactically repeated.
4. Preserve source values and document every migration assumption.
