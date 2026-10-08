# Customer Normalization

Customer information should generally be represented as a Customer entity.

Common customer attributes include:

- customer_id
- customer_name
- email
- phone

Common source-system variations include:

- cust_id
- customer_no
- client_id
- member_id
- party_id

A source table containing customer information should normally map to a standardized Customer entity.

If customer address information is stored in the same table as customer information, consider separating the address into a dedicated Address entity.

Customer and Address should have a relationship through customer_id.
