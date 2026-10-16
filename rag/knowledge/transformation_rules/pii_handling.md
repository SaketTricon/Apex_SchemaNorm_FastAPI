# PII-aware profiling and migration

## Purpose

Minimize exposure of personally identifiable or sensitive information while profiling, retrieving knowledge, generating recommendations, and migrating data.

## Common sensitive attributes

Email addresses, phone numbers, names, postal addresses, government identifiers, account identifiers, and precise location or activity data may be sensitive depending on the domain and applicable policy.

## Safe handling rules

- Treat profiler labels such as `possible PII` as a signal for review, not a definitive legal classification.
- Prefer aggregate statistics and redacted or synthetic examples over raw values.
- Do not include raw PII in logs, retrieval queries, prompts, error messages, or test fixtures unless explicitly required and approved.
- Restrict access and retention of source extracts, profile artifacts, and generated indexes according to organizational policy.
- Preserve required data through migration only with appropriate access controls, encryption, and documented purpose.
- Avoid using sensitive attributes as keys unless the business and compliance requirements explicitly justify it.

## Recommendation

Report which columns may be sensitive and what handling is recommended, while avoiding copying their values into generated schema advice. Apply the organization's privacy and retention policies before sharing profile content with external services.

## Retrieval keywords

PII, personally identifiable information, sensitive data, email, phone, redaction, privacy-aware migration, prompt safety, data minimization, retention, access control
