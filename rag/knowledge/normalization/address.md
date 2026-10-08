# Address Normalization

Address information should generally be separated from the Customer entity when multiple address attributes are present.

Common address attributes include:

- address_line_1
- address_line_2
- city
- state
- postal_code
- country

Common source-system variations include:

- addr
- addr1
- addr2
- city_name
- state_code
- zip
- zipcode
- postal

If a customer table contains several address-related columns, consider creating a separate Address table.
