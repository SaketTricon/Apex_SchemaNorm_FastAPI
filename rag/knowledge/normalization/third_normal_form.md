# Third Normal Form (3NF)

## Purpose

Third Normal Form reduces transitive dependencies by ensuring that non-key attributes depend on the key, the whole key, and nothing but the key.

## Rule

A table should not store a non-key attribute that depends on another non-key attribute rather than directly on the key. When this pattern appears, there is usually a hidden entity or lookup table that should be modeled separately.

## Example: before normalization

Table: `CUSTOMER`

| customer_id | customer_name | postal_code | city |
| --- | --- | --- | --- |
| 101 | Ravi | 560001 | Bengaluru |
| 102 | Priya | 500001 | Hyderabad |

If `postal_code` is a business determinant for `city`, the city may be duplicated and maintained in multiple customer rows instead of being associated once in a reference table.

## Possible target design

- `Customer(customer_id, customer_name, postal_code)`
- `PostalArea(postal_code, city)`

This is not always the right choice if postal codes are not stable or if the domain permits many localities per code, but it is a common pattern for schema normalization.

## Detection signals

- same descriptive values repeated across many rows
- an attribute like city or status description that changes in many places
- a report is built from multiple columns that are actually a reference data set
- one update forces multiple rows to be changed

## Recommendation

Investigate whether the relationship is truly stable and whether the column belongs to an independent dimension. Preserve source values and document the migration logic before decomposing the table.

## Important caveats

- a repeated value alone does not prove a functional dependency
- postal codes may map to multiple localities depending on the region or business rules
- not every descriptive value should become a lookup table; normalization requires a real business relationship

## Retrieval keywords

3NF, third normal form, transitive dependency, functional dependency, postal code, address dimension, repeated descriptive values, customer normalization
