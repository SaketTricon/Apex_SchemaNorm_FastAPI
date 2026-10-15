# Lookup tables and junction tables

## Purpose

Some source tables contain values that are not really facts but controlled descriptors. These are often better represented as lookup tables or junction tables.

## Lookup table example

A source table may contain repeated status values such as:

- `status = 'Active'`
- `status = 'Pending'`
- `status = 'Closed'`

These values are usually better modeled as a `StatusLookup` table or domain value list, especially when the same status labels are reused across multiple tables.

## Junction table example

A many-to-many relationship such as `customer` to `interest` or `order` to `product` is frequently stored in one denormalized row with repeated values. The normalized design is usually:

- `Customer(customer_id, ...)`
- `Interest(interest_id, name)`
- `CustomerInterest(customer_id, interest_id)`

This avoids arrays or delimited values and supports cleaner reports and updates.

## Signals to detect

- same short code or label repeated across many rows
- a single field with multiple values in one cell
- parent-child relationships implemented as repeated column groups
- many-to-many relationships hidden inside a transaction table

## Recommendation

Split the relationship into a dedicated entity only when the cardinality and business meaning justify it. A simple category string is not always a reason to create a lookup table; the data must be shared, controlled, and reused.

## Retrieval keywords

lookup table, junction table, many-to-many, category values, status mapping, repeated code, category dimension, relationship normalization
