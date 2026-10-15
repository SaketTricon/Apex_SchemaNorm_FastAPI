# Functional dependencies and normalization signals

## Purpose

A functional dependency exists when the value of one attribute or set of attributes determines another attribute. In practical schema modeling, this is the main clue that a table may be denormalized or missing a relationship.

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

Do not decompose a table solely because a repeated value appears. Confirm whether the dependency is real for the domain, whether the column is a true key, and whether the business rule is stable. A surrogate key may preserve valid source data while avoiding fragile composite-key logic.

## Retrieval keywords

functional dependency, normalization, repeating values, master-detail schema, transitive dependency, customer detachment, key-driven design
