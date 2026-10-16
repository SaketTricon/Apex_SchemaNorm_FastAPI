# Customer entity resolution and migration pattern

## Typical source symptom

A legacy table may contain all of the following in one row:

- `customer_id`
- `customer_name`
- `email`
- `phone`
- `billing_address_1`
- `billing_address_2`
- `shipping_address_1`
- `shipping_address_2`
- `city`
- `state`
- `postal_code`

This pattern usually indicates mixed master and address concerns.

Another common case is two or more source tables containing overlapping customer attributes, such as a wide profiling table and a smaller `customers` table. The tables may represent the same entity, different source-system views, a subset, or separate snapshots.

## Verify table grain before assigning an entity

A wide table may be described as customer data while containing measures or activity attributes such as `price`, `quantity`, `last_login`, or event dates. Before mapping every row to one `Customer`, determine what one row represents:

- one customer
- one customer snapshot at a point in time
- one customer activity or transaction
- a flattened join of multiple entities

Check whether a purported customer key repeats across time or events, whether measures belong to a transaction, and whether multiple rows per customer are expected. A unique key in a sample does not by itself establish the business grain.

## Entity-resolution investigation

1. Compare candidate-key values and measure their overlap across tables.
2. Compare data types, nullability, and value formats for matching columns.
3. Check whether one table is a subset of another, while accounting for sampling and time differences.
4. Investigate conflicting names, contact details, statuses, and update timestamps.
5. Determine which system or table is authoritative for each attribute and lifecycle stage.
6. Compare row grain and key scope before treating overlapping tables as duplicate customer masters.

Similar names or overlapping values are evidence to investigate, not proof that the tables should be merged.

## Recommended target model

- `Customer(customer_id, customer_name, email, phone)`
- `Address(address_id, customer_id, address_type, address_line_1, address_line_2, city, state, postal_code, country)`

## Why this is usually better

- customer identity is distinct from address lifecycle
- multiple addresses can be stored for one customer without repeating customer attributes
- address updates do not create redundant customer edits
- the schema supports billing, shipping, and mailing use cases with a consistent relationship model

## Migration considerations

- identify whether the source supports one or many addresses per customer
- decide whether `address_type` is a domain value or a foreign key to a lookup table
- preserve original source values, especially if country names, state codes, or postal formats vary
- check whether duplicate addresses should be deduplicated or preserved as separate records
- preserve source-table lineage and define conflict-resolution rules before consolidating overlapping customer records
- do not discard records or attributes merely because their values overlap

## Caveats

- a single address field does not always require a separate table if the business never stores multiple addresses
- some source systems intentionally denormalize for reporting convenience, so the recommendation should be validated by the business meaning of the data

## Retrieval keywords

customer master, customer entity resolution, duplicate customer tables, overlapping schemas, customer and address split, billing address, shipping address, contact details, address lifecycle, master-detail mapping, source table consolidation, row grain, customer snapshot, customer activity, transaction attributes
