# Naming standards

## Goal

Use explicit and consistent names for target database columns so the final schema is self-describing and easier to validate.

## Recommended mappings

- `cust_id` -> `customer_id`
- `cust_nm` or `cust_name` -> `customer_name`
- `addr1` or `addr_line1` -> `address_line_1`
- `addr2` or `addr_line2` -> `address_line_2`
- `zip`, `zipcode`, or `postal` -> `postal_code`
- `state_code` -> `state`
- `phone_no` -> `phone`
- `email_id` -> `email`
- `order_no` -> `order_id`

## Naming rules

- prefer full words over cryptic abbreviations whenever the name remains readable
- use singular nouns for entities and plural names only for explicit collections or child tables
- use a consistent key suffix such as `_id` for identifiers
- keep status and code fields explicit: `status`, `type`, `category_code`
- do not let naming strategy override actual schema logic; names should reflect the relationship, not just a string transform

## Example

Source columns:

- `CUST_NO`, `CUST_NAME`, `ADDR_1`, `ZIPCODE`, `PHN_NO`

Target columns:

- `customer_id`, `customer_name`, `address_line_1`, `postal_code`, `phone`

## Retrieval keywords

naming standards, target schema naming, column naming, customer_id mapping, postal_code mapping, source-to-target names, field normalization, schema conventions
