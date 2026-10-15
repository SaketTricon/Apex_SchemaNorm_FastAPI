# Healthcare schema reference

## Typical healthcare pattern

Healthcare systems often combine patient data, encounters, procedures, providers, and billing lines. A denormalized source table may include patient information, physician information, diagnosis codes, and billing data all in the same record.

### Patient

- `patient_id`
- `patient_name`
- `date_of_birth`
- `gender`
- `insurance_plan_id`

### Encounter

- `encounter_id`
- `patient_id`
- `provider_id`
- `encounter_date`
- `department_id`

### Procedure or Diagnosis

- `encounter_id`
- `code`
- `code_type`
- `description`

## Why the split matters

- patients can have many encounters and many codes
- providers and departments are shared reference entities
- diagnosis and procedure details are often modeled as child rows, not repeated fields
- billing can be separated from clinical encounter data to respect different lifecycle rules

## Caveats

Use this pattern as a domain example. Some healthcare systems intentionally flatten reports for operational dashboards, so the recommended model must still be checked against actual cardinality and privacy requirements.

## Retrieval keywords

healthcare schema, patient encounter, diagnosis code, provider relationship, billing separation, department dimension, clinical data model
