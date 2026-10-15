# Migration pattern knowledge

This folder captures common source-schema patterns that should be translated into a cleaner relational design.

## Included patterns

- customer master and address separation
- order and order-item decomposition
- product and category relationships
- employee and department mappings
- lookup tables and junction tables

## How to use these documents

The pattern documents are intended to help the LLM propose a normalized target structure based on the source profile and observed data distributions.

A strong migration recommendation usually includes:

- observed source symptoms
- likely target entities
- PK/FK relationships
- source-to-target mappings
- edge cases and invalid assumptions

## Good migration judgment

A pattern should only be applied when there is evidence from the source schema, the data, or the domain meaning. Not every repeated column becomes a new table.
