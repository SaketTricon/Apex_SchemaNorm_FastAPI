# Knowledge base for schema normalization

This folder contains retrieval-ready guidance for schema profiling, normalization, naming, and migration planning.

The documents are intentionally written as decision-support material rather than short glossary entries.
Each file explains:

- the pattern to detect
- a realistic source-schema example
- the normalized target shape
- migration considerations and caveats
- the terms that should match user queries and generated profiles

## Structure

- `normalization/`: rules for 1NF, 2NF, 3NF, functional dependencies, and schema smells
- `naming_rules/`: standard column naming and source-to-target mapping practices
- `industry_schemas/`: example domain models used as design references
- `migration_patterns/`: common source patterns and target tables for real migrations
- `transformation_rules/`: rules for data type, null, and identifier conversions

The goal is to help the profiler and LLM recommend a target schema that is consistent with both the source profile and database design best practices.
