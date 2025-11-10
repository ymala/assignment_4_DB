### For this project we have chosen a retail business case  

It has:
- A network of physical stores (hypermarkets, supermarkets, and local "to go" shops)  
- An e-commerce platform (which we treat as store '9999')  
- A customer loyalty program to track registered buyers  
- Dynamic pricing and marketing promotions that change over time  

Our raw data comes from 7 different sources. All data is for the period 01-Jan-2023 to 31-Dec-2024.

### How to set up the DB
1) Execute a script from file "data_generation.py" and you'll have csv generated
2) Execute a script from file "create_raw_tables.sql"
3) Execute a Python script "load_raw_data" in your Python shell  
   **Don't forget to fill in your password in config var in the script and right path to the csv files.**
5) Execute a script from file "refill_stg_tables.sql"

### Raw Data Sources (7 CSV files)

1. check_summary.csv  
One raw for a single transaction. It tells us where, when, and (sometimes) who made the purchase.
- check_id: A 12-digit unique ID for the receipt  
- store_id: The 3-digit store code, or '9999' for online sales  
- cashier_id: The 2-digit ID of the cashier (empty for online)  
- datetime: The full date and time of the sale (format: dd-mm-yyyy hh:mm)  
- customer_id: The 8-digit loyalty ID, if the customer used their card (can be empty)  

2. check_details.csv  
The most important file - it contains the lines for every receipt. Each row is one product sold.
- check_id: The 12-digit ID to link back to the check_summary  
- product_id: The 6-digit ID of the item  
- product_name: A string with the product name (this is a bit "dirty" as it's copied at the time of sale)  
- unit_price: The price of one unit at the moment of sale  
- discount_pct: Discount percentage, if any (empty otherwise)  
- discount_abs: Absolute discount amount in money (empty otherwise)  
- discount_type: A 2-digit code for the type of promotion  
- quantity: The amount sold (e.g., 2 for "pcs" or 0.5 for "kg")  
- total_amount: The final calculated amount for this line ((unit_price * quantity) - discount_abs)  

3. products.csv
This is our master "product catalog".
- product_id: The 6-digit unique product ID  
- name: The official, clean product name  
- unit_of_measure: The unit (e.g., pcs, g, kg, l, ml, pack)  
- category: The product category (e.g., "Dairy", "Beverages", etc.)  

4. pricing.csv
This file comes from the commercial department. It defines the retail price for products over time.
- product_id: The product ID  
- retail_price: The standard retail price  
- start_date: The first day this price is active (format: dd-mm-yyyy)  
- end_date: The last day this price is active  
- is_active: A flag (0 or 1) to show if this is the current active price  

(Note: The rule is only one price is active per product per day)

5. promo.csv

This file is from the marketing team.
- promo_type: A 2-digit code for the promo (e.g., '10' = "Black Friday")  
- product_id: The product ID on promotion  
- discount_pct: The discount percentage for this promo  
- start_date: The first day of the promo  
- end_date: The last day of the promo  
- is_active: A flag (0 or 1)  
- description: A text description (e.g., "Spring Sale")  

6. customers.csv
This is our list of loyalty program members.
- customer_id: The 8-digit unique member ID  
- name: The customer's first name  
- city: The city where they registered (or '9999' for online)  
- birthday: The customer's date of birth (can be empty)  

7. stores.csv
This is the catalog of our physical stores.
- store_id: The 3-digit unique store ID  
- format: The type of store (e.g., hyper, super, to go)  
- city: The city where the store is located  
- region: The region/state where the store is located  

### Stage Layer Transformation Logic
This layer takes the "as-is" data from the raw_ tables and transforms it into clean, standardized tables (stg_). All data types are converted from VARCHAR to their proper types (INT, DECIMAL, DATE, etc.)  

1. stg_transactions  
This table is the most important one. It flattens the two raw_check_ tables into a single, wide table to avoid expensive joins during analysis.
Source: raw_check_summary JOIN raw_check_details on check_id.

- check_id: Convert from VARCHAR to BIGINT  
- store_id: Convert from VARCHAR to INT  
- cashier_id: Convert from VARCHAR to INT. Handle empty strings as NULL  
- customer_id: Convert from VARCHAR to BIGINT. Handle empty strings as NULL  
- product_id: Convert from VARCHAR to INT  
- datetime: Convert from VARCHAR (format dd-mm-yyyy hh:mm) to a TIMESTAMP  
- For unit_price, discount_abs, quantity, total_amount:
  -    Convert from VARCHAR to DECIMAL(18, 4)
  -    Replace any NULL values or empty strings with 0 using COALESCE(column, 0)  
- For discount_pct, discount_type:
  -    Convert from VARCHAR to INT 
  -    Replace any NULL values or empty strings with 0 using COALESCE(column, 0)
  -    Data Quality Check: Add logic to flag (or set to 0) any values where unit_price, quantity, or total_amount are negative.

2. stg_pricing
Source: raw_pricing

- product_id: Convert from VARCHAR to INT  
- price: Convert from VARCHAR to DECIMAL(10, 2)  
- start_date, end_date: Convert from VARCHAR (format dd-mm-yyyy) to DATE  
- is_active: Convert from VARCHAR ('0' or '1') to BOOLEAN

3. stg_products
We will join the current price to products for a faster analysis.
Source: raw_products

- product_id: Convert from VARCHAR to INT
- name, unit, category: Apply TRIM() to remove any leading/trailing whitespace
- Enrichment: add a new column current_retail_price from the joined table, which will be NULL if no active price is found  

4. stg_promo
Source: raw_promo

- promo_type: Convert from VARCHAR to INT. Replace any empty strings with NULL  
- product_id: Convert from VARCHAR to INT  
- discount_pct: Convert from VARCHAR to INT  
- start_date, end_date: Convert from VARCHAR (format dd-mm-yyyy) to DATE  
- is_active: Convert from VARCHAR ('0' or '1') to BOOLEAN  
- description: Apply TRIM() to remove whitespace  
- Data Quality Check: Ensure discount_pct is 0 or greater  

5. stg_customers
Source: raw_customers

- customer_id: Convert from VARCHAR to BIGINT
- name, city: Apply TRIM() to remove whitespace  
- city: Standardize the "Online" value: CASE WHEN city = '9999' THEN 'Online' ELSE city END  
- birthday: Convert from VARCHAR (format dd-mm-yyyy) to DATE

6. stg_stores
Source: raw_stores

- store_id: Convert from VARCHAR to INT
- format, city, region: Apply TRIM() to remove any leading/trailing whitespace  

Note: We must also add the missing '9999' Online store to this table, since it exists in transactions but not in the raw directory file. We will add a record with store_id = 9999, format = 'Online', city = 'Online', region = 'Online'.
