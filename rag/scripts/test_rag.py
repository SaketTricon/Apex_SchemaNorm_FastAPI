import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from rag.index import load_index
from rag.vector_search import format_rag_context, vector_search


INDEX_PATH = PROJECT_ROOT / "rag" / "data" / "knowledge_index.pkl"


def main() -> None:
	query = """Dataset overview  
The supplied data set consists of three source files containing a total of 520 rows and 32 columns. The files are: vendor_profiling_sample.csv (500 rows, 18 columns), orders.csv (12 rows, 7 columns), and customers.csv (8 rows, 7 columns). Across the three tables there are 32 distinct column names.

Table descriptions  

1. vendor_profiling_sample – a wide table with 500 records describing individual customers and assorted attributes such as contact information, activity flags, and transactional details.  

2. orders – a narrow fact‑like table with 12 order records, each linking a customer to a product and capturing quantity, amount, status and date.  

3. customers – a small reference table with 8 customer records, mirroring a subset of the fields found in vendor_profiling_sample.

Column descriptions  

vendor_profiling_sample  
- customer_id (position 1): integer, identified as an identifier, not nullable. All 500 rows are non‑null, each value distinct (100 % uniqueness). Marked as a candidate primary key.  
- customer_uuid (position 2): string, identifier, not nullable. 500 distinct UUID strings, also a candidate primary key.  
- customer_name (position 3): string, generic text, not nullable. 98 distinct values (19.6 % distinctness) with 402 duplicate occurrences.  
- email (position 4): string, semantic type email, nullable. 21 nulls (4.2 %); the 479 non‑null values are all distinct and follow an email pattern.  
- phone (position 5): string, phone_number, nullable. 16 nulls (3.2 %); the remaining 484 values are distinct and match a phone‑like pattern.  
- age (position 6): integer, numeric_measure, nullable. 29 nulls (5.8 %); 471 non‑null values with 48 distinct ages (10.19 % distinctness), many repeats.  
- city (position 7): string, city, not nullable. Only 8 distinct city names across 500 rows (1.6 % distinctness), heavy repetition.  
- category (position 8): string, generic, not nullable. 5 distinct categories (1.0 % distinctness).  
- price (position 9): numeric, monetary_amount, nullable. 26 nulls (5.2 %); 474 distinct non‑null values, each unique.  
- quantity (position 10): integer, numeric_measure, not nullable. 25 distinct quantities (5.0 % distinctness) with 475 duplicate occurrences.  
- is_active (position 11): boolean, not nullable. Two distinct values (true/false) covering 99.6 % of rows; only 2 duplicate rows.  
- membership (position 12): boolean_like, not nullable. Same distribution as is_active (two distinct values, 0.4 % distinctness).  
- signup_date (position 13): date, not nullable. 340 distinct dates (68 % distinctness); 160 duplicate dates.  
- last_login (position 14): datetime, timestamp, not nullable. 495 distinct timestamps (99 % distinctness); only 5 duplicate timestamps. Identified as a possible audit column.  
- website (position 15): string, nullable. 17 nulls (3.4 %); 483 distinct non‑null values, each matching a URL pattern.  
- ip_address (position 16): string, ip_address, not nullable. 495 distinct IPs (99 % distinctness); 5 duplicate entries.  
- status (position 17): string, not nullable. 3 distinct status values (0.6 % distinctness) with 497 duplicate rows.  
- notes (position 18): string, nullable. 109 nulls (21.8 %); only 4 distinct non‑null note strings (1.02 % distinctness) repeated across 391 rows.

orders  
- order_id (position 1): integer, identifier, not nullable. All 12 values distinct (100 % uniqueness); candidate primary key.  
- customer_id (position 2): integer, identifier, not nullable. 7 distinct values (58.33 % uniqueness); duplicates indicate many‑to‑one relationship to customers.  
- product_id (position 3): string, identifier, not nullable. 5 distinct product identifiers (41.67 % uniqueness).  
- quantity (position 4): integer, numeric_measure, not nullable. 4 distinct quantities (33.33 % uniqueness); heavy duplication.  
- order_amount (position 5): numeric, monetary_amount, not nullable. 11 distinct amounts (91.67 % uniqueness); only one duplicate.  
- order_status (position 6): string, not nullable. 4 distinct status values (33.33 % uniqueness).  
- order_date (position 7): date, not nullable. All 12 dates distinct (100 % uniqueness).

customers  
- customer_id (position 1): integer, identifier, not nullable. All 8 values distinct; candidate primary key.  
- customer_name (position 2): string, not nullable. 8 distinct names (100 % uniqueness).  
- email (position 3): string, email, not nullable. 8 distinct email addresses (100 % uniqueness).  
- phone (position 4): integer, phone_number, not nullable. 8 distinct phone numbers (100 % uniqueness).  
- city (position 5): string, city, not nullable. 7 distinct cities (87.5 % uniqueness); one duplicate city.  
- status (position 6): string, not nullable. 2 distinct status values (25 % uniqueness); 6 duplicate rows.  
- created_at (position 7): datetime, timestamp, not nullable. All 8 timestamps distinct; flagged as a possible audit column.

Keys and relationships  
Primary key candidates: vendor_profiling_sample – customer_id and customer_uuid; orders – order_id; customers – customer_id.  
Foreign key relationships (high confidence): orders.customer_id → vendor_profiling_sample.customer_id (many‑to‑one) and orders.customer_id → customers.customer_id (many‑to‑one).  
Possible audit columns: vendor_profiling_sample.last_login and customers.created_at.  
Potential PII columns: vendor_profiling_sample.email, vendor_profiling_sample.phone, customers.email, customers.phone.

Data quality and notable patterns  
- Null prevalence is low overall; the highest null column is vendor_profiling_sample.notes (21.8 % null). Email, phone, price, website, and ip_address have modest null rates (≤5 %).  
- Uniqueness varies widely: identifiers (customer_id, customer_uuid, order_id) are fully unique, while descriptive fields such as city, category, status, and notes show very low distinctness, indicating categorical or repetitive data.  
- Boolean‑like columns (is_active, membership) contain exactly two values, suitable for binary flags.  
- Timestamp columns (last_login, created_at) are almost entirely unique, supporting audit tracking.  
- Numeric columns (price, quantity, age) show distinctness patterns consistent with measurement data; price is fully unique, quantity repeats heavily, age repeats moderately.  
- Pattern detection confirms expected formats: UUIDs, emails, URLs, IP addresses, dates, and datetimes are consistently matched.

Uncertain or ambiguous fields  
- The column membership is typed as boolean_like; while it behaves like a binary flag, the exact semantics (e.g., membership tier vs. simple yes/no) are not defined.  
- The status columns in both vendor_profiling_sample and customers have very low distinctness; without a lookup table the meaning of each status value remains ambiguous.  
- The notes field contains only four distinct strings despite many rows; the content and purpose of these notes cannot be inferred from the profiling alone.  
- The category field in vendor_profiling_sample is a generic string with five distinct values; its business meaning (product category, customer segment, etc.) is unclear.  
- The product_id in orders is identified as an identifier but no product reference table is present, leaving its relationship to other data undefined.
 """
	
	index = load_index(INDEX_PATH)
	results = vector_search(query=query, index=index, top_k=5)
	context = format_rag_context(results)

	print("\nRAG Context")
	print("=" * 60)
	print(context)


if __name__ == "__main__":
	main()
