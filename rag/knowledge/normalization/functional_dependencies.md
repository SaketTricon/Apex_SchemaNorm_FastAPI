# Functional dependencies and normalization signals

## Purpose

A functional dependency `X -> Y` means the value of attribute set `X` determines attribute set `Y` within the applicable data domain and business rules. Candidate keys and dependencies help explain whether a table is at the right grain and whether attributes belong in separate entities.

## Candidate-key guidance

A candidate key uniquely identifies a row and is minimal for that purpose. Profiler statistics can suggest candidates:

- a key candidate should be non-null and unique in the observed data
- consider composite candidates when no single column uniquely identifies the row
- inspect declared constraints and business meaning when source database access permits
- assess whether a candidate is stable over time and meaningful outside the current sample

Observed uniqueness is evidence, not proof of a declared or valid primary key. If two columns are both unique, do not designate both as primary keys; choose one primary key and treat other appropriate candidates as alternate unique keys. A surrogate key may be useful when natural identifiers are mutable, sensitive, or inconsistent, but retain meaningful source identifiers for traceability.

## Example

A source table like `CUSTOMER_ORDER` may include:

- `customer_id`
- `customer_name`
- `customer_email`
- `order_id`
- `order_date`
- `shipping_city`
- `shipping_state`

If `customer_id -> customer_name` and `customer_id -> customer_email`, then `customer_name` and `customer_email` depend on the customer key rather than the order row. If the same customer appears in many rows, the data should usually be moved into a `Customer` table.

## Signal to detect

- repeated descriptive values across multiple rows
- repeated customer, product, or vendor details in transactional tables
- a non-key column that determines another non-key column
- columns that must be updated in many rows when a master record changes

## Target design

Typical normalized split:

- `Customer(customer_id, customer_name, email)`
- `Order(order_id, customer_id, order_date, shipping_address_id)`

This exposes the actual relationship instead of copying the same customer details into every order row.

## Recommendation

Do not decompose a table solely because a repeated value appears. Confirm whether the dependency is real for the domain, whether the column is a true key, and whether the business rule is stable. A surrogate key may preserve valid source data while avoiding fragile composite-key logic. Low distinctness alone does not prove a functional dependency.

## Retrieval keywords

functional dependency, normalization, repeating values, master-detail schema, transitive dependency, customer detachment, key-driven design, candidate key, primary key, alternate key, natural key, surrogate key, composite key, uniqueness, unique constraint
