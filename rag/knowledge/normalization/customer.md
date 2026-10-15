# Customer normalization

## Purpose

The `Customer` entity usually represents the unique business party and should hold stable identity and contact details rather than operational or address data that can repeat across many rows.

## Common customer fields

- `customer_id`
- `customer_name`
- `email`
- `phone`
- `status`

Common source variations include:

- `cust_id`, `customer_no`, `client_id`
- `member_id`, `party_id`, `account_id`

## Detection signals

- customer details appear in every order or transaction row
- customer and address information are stored in the same table with repeating values
- one customer has multiple billing or shipping addresses
- a table mixes entity identity with transaction-level facts

## Recommended target design

- `Customer(customer_id, customer_name, email, phone, status)`
- `Address(address_id, customer_id, address_type, address_line_1, address_line_2, city, state, postal_code, country)`

## Recommendation

Keep customer master attributes in a separate entity and move repeated, multi-valued, or reusable details such as addresses into related tables. The exact boundaries should still be validated against the actual source profile and business semantics.

## Retrieval keywords

customer normalization, customer entity, customer master, party table, address split, contact details, customer_id, customer_name, party_id
