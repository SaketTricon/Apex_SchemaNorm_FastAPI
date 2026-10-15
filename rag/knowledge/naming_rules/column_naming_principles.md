# Column naming and source-to-target mapping

## Principle

A target schema is easier to validate and query when names are explicit, consistent, and domain-aligned. Naming should improve meaning without forcing a single rigid convention across every source system.

## Recommended mappings

- `cust_id` -> `customer_id`
- `cust_nm` or `cust_name` -> `customer_name`
- `addr1` or `addr_line1` -> `address_line_1`
- `addr2` or `addr_line2` -> `address_line_2`
- `zip`, `zipcode`, or `postal` -> `postal_code`
- `state_code` -> `state`
- `phone_no` -> `phone`
- `email_id` -> `email`

## Naming rules

- prefer singular, domain nouns such as `customer`, `order`, `product`, `address`
- use `_id` for surrogate or business identifiers
- use `*_date`, `*_status`, and `*_code` to distinguish domain concepts
- avoid abbreviations unless they are standard in the target domain and documented
- do not rename a source field just because a different name exists, unless the target standard is clear and consistent

## Practical example

Source table:

- `CUST_NO`, `CUST_NAME`, `ADDR_1`, `ZIPCODE`, `PHN_NO`

Target table:

- `customer_id`, `customer_name`, `address_line_1`, `postal_code`, `phone`

## Caveats

- a naming standard is not a schema guarantee; the target still needs keys, relationships, and value checks
- column names must remain traceable to the source through mapping documentation
- use the same naming pattern across lookup tables, fact tables, and dimension tables

## Retrieval keywords

naming standards, source-to-target mapping, column normalization, customer_id, postal_code, address_line_1, mapping rules, schema convention
