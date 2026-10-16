# Retail schema reference

## Typical retail pattern

A standard retail domain often separates customer identity, shipping data, orders, and products into distinct entities.

### Customer

- `customer_id`
- `customer_name`
- `email`
- `phone`
- `status`

### Address

- `address_id`
- `customer_id`
- `address_type`
- `address_line_1`
- `address_line_2`
- `city`
- `state`
- `postal_code`
- `country`

### Order

- `order_id`
- `customer_id`
- `order_date`
- `shipping_address_id`
- `status`

### OrderItem

- `order_item_id`
- `order_id`
- `product_id`
- `quantity`
- `unit_price`

## Why this pattern is common

- customer details are stable and reused across transactions
- addresses may vary by customer and by address type
- order headers and order items represent different levels of granularity
- product and customer references are more maintainable when stored in master tables

## Caveats

This pattern is a reference, not a universal rule. Some source systems intentionally denormalize order data for reporting simplicity, and some retailers may track a single shipping address only.

## Retrieval keywords

retail schema, customer master, order header, order item, address table, retail modeling, schema reference, normalized retail design
