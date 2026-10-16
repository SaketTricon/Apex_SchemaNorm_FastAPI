# Order and order-item migration pattern

## Typical source pattern

A denormalized order table might contain:

- `order_id`
- `order_date`
- `customer_id`
- `customer_name`
- `product_id`
- `product_name`
- `quantity`
- `unit_price`
- `discount_percent`
- `shipping_address`

When an order contains multiple products, customer and product details may be repeated in each row. This is a common signal for master-detail normalization.

## Possible target model

If each row represents one product line and an order can contain multiple products, consider separating the order header from its lines:

- `Order(order_id, customer_id, order_date, shipping_address_id, status)`
- `OrderItem(order_item_id, order_id, product_id, quantity, unit_price, discount_percent)`
- `Product(product_id, product_name, category_id, sku)`
- `Customer(customer_id, customer_name)`

If each row is already one complete order, a separate `OrderItem` table may not be justified by the available evidence.

## Why this is usually better

- the order header is separate from the line-item detail
- each order item is a distinct business transaction
- product and customer information is stored once, not repeated across every order row
- reporting can aggregate by order, product, customer, and date without data duplication

## Migration considerations

- identify whether `order_id` is unique for the entire order or whether a composite key is required
- establish the row grain: one row per order, order line, or another business event
- determine whether amount columns represent unit price, line amount, or whole-order total
- verify whether an order can have multiple products and whether a product can appear more than once per order
- do not create an `OrderItem` split solely because a `product_id` column exists
- use `order_item_id` or a natural key if the source data supports stable item identification
- retain pricing and discount source values carefully if currency, tax, or discount rounding is involved
- validate whether a single order can reference multiple addresses or one shipping address only

## Retrieval keywords

order header, order item, order details, product master, customer master, one-to-many relationship, transactional denormalization, order line normalization, row grain, order amount, line amount, total amount
