# Retail Customer Schema

A typical retail customer model contains:

Customer
- customer_id
- customer_name
- email
- phone

Address
- address_id
- customer_id
- address_line_1
- address_line_2
- city
- state
- postal_code
- country

Customer and Address are normally modeled as separate entities when address information needs to be maintained independently.
