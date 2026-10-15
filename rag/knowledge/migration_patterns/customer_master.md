# Customer master migration pattern

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

## Caveats

- a single address field does not always require a separate table if the business never stores multiple addresses
- some source systems intentionally denormalize for reporting convenience, so the recommendation should be validated by the business meaning of the data

## Retrieval keywords

customer master, customer and address split, billing address, shipping address, contact details, address lifecycle, master-detail mapping
