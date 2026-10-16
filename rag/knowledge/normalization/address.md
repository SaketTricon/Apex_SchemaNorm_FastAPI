# Address normalization

## Purpose

Address information should usually be modeled as a separate entity when a customer, organization, or order can have multiple addresses or when address details are reused across records.

## Common source fields

- `address_line_1`
- `address_line_2`
- `city`
- `state`
- `postal_code`
- `country`

Typical source variations include:

- `addr`, `addr1`, `addr2`
- `city_name`, `state_code`
- `zip`, `zipcode`, `postal`
- `country_code`, `country_name`

## Detection signals

- repeated postcode, city, and state information across many rows
- multiple address-related columns for billing, shipping, mailing, or home addresses
- one-to-many customer or order relationships represented as repeated address fields in a single row

## Recommended target design

- `Address(address_id, customer_id, address_type, address_line_1, address_line_2, city, state, postal_code, country)`

This supports multiple addresses per customer while keeping address updates separate from contact and identity details.

## Recommendation

Do not split addresses purely because a source table has several columns. The real driver is whether the business meaning is entity-level and reusable. Preserve the original values and document mapping rules for region and postal-code formats.

## Retrieval keywords

address normalization, customer address, postal code, state code, shipping address, billing address, address entity, address table, mailing address
