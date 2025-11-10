USE e_commerce_demo;


DROP TABLE IF EXISTS stg_stores;
CREATE TABLE stg_stores AS
SELECT
    CAST(store_id AS UNSIGNED) AS store_id,
    TRIM(format) AS store_format,
    TRIM(city) AS city,
    TRIM(region) AS region
FROM
    raw_stores
UNION ALL
SELECT 9999, 'Online', 'Online', 'Online';



DROP TABLE IF EXISTS stg_customers;
CREATE TABLE stg_customers AS
SELECT
    CAST(customer_id AS UNSIGNED) AS customer_id,
    TRIM(name) AS name,
    CASE
        WHEN TRIM(city) = '9999' THEN 'Online'
        ELSE TRIM(city)
        END AS city,
    STR_TO_DATE(NULLIF(TRIM(birthday), ''), '%d-%m-%Y') AS birthday
FROM
    raw_customers;


DROP TABLE IF EXISTS stg_pricing;
CREATE TABLE stg_pricing AS
SELECT
    CAST(product_id AS UNSIGNED) AS product_id,
    CAST(price AS DECIMAL(10, 2)) AS price,
    STR_TO_DATE(start_date, '%d-%m-%Y') AS start_date,
    STR_TO_DATE(end_date, '%d-%m-%Y') AS end_date,
    CAST(is_active AS UNSIGNED) AS is_active
FROM
    raw_pricing;


DROP TABLE IF EXISTS stg_promo;
CREATE TABLE stg_promo AS
SELECT
    CAST(NULLIF(TRIM(promo_type), '') AS UNSIGNED) AS promo_type,
    CAST(product_id AS UNSIGNED) AS product_id,
    GREATEST(
            COALESCE(CAST(NULLIF(TRIM(discount_pct), '') AS UNSIGNED), 0),
            0) AS discount_pct,
    STR_TO_DATE(start_date, '%d-%m-%Y') AS start_date,
    STR_TO_DATE(end_date, '%d-%m-%Y') AS end_date,
    CAST(is_active AS UNSIGNED) AS is_active,
    TRIM(description) AS description
FROM
    raw_promo;



DROP TABLE IF EXISTS stg_products;
CREATE TABLE stg_products AS
SELECT
    CAST(p.product_id AS UNSIGNED) AS product_id,
    TRIM(p.name) AS name,
    TRIM(p.unit) AS unit,
    TRIM(p.category) AS category,
    pr.price AS current_retail_price
FROM
    raw_products AS p
        LEFT JOIN
    stg_pricing AS pr
    ON CAST(p.product_id AS UNSIGNED) = pr.product_id
        AND pr.is_active = 1;



DROP TABLE IF EXISTS stg_transactions;
CREATE TABLE stg_transactions AS
SELECT
    CAST(s.check_id AS UNSIGNED) AS check_id,
    CAST(s.store_id AS UNSIGNED) AS store_id,
    CAST(NULLIF(TRIM(s.cashier_id), '') AS UNSIGNED) AS cashier_id,
    CAST(NULLIF(TRIM(s.customer_id), '') AS UNSIGNED) AS customer_id,
    STR_TO_DATE(s.datetime, '%d-%m-%Y %H:%i') AS transaction_datetime,
    CAST(d.product_id AS UNSIGNED) AS product_id,
    COALESCE(
            GREATEST(CAST(NULLIF(TRIM(d.unit_price), '') AS DECIMAL(18, 4)), 0),
            0) AS unit_price,
    COALESCE(
            GREATEST(CAST(NULLIF(TRIM(d.quantity), '') AS DECIMAL(18, 4)), 0),
            0) AS quantity,
    COALESCE(
            GREATEST(CAST(NULLIF(TRIM(d.total_amount), '') AS DECIMAL(18, 4)), 0),
            0) AS total_amount,
    COALESCE(
            GREATEST(CAST(NULLIF(TRIM(d.discount_abs), '') AS DECIMAL(18, 4)), 0),
            0) AS discount_abs,
    COALESCE(
            GREATEST(CAST(NULLIF(TRIM(d.discount_pct), '') AS UNSIGNED), 0),
            0) AS discount_pct,
    COALESCE(CAST(NULLIF(TRIM(d.discount_type), '') AS UNSIGNED), 0) AS discount_type
FROM
    raw_check_summary AS s
        JOIN
    raw_check_details AS d
    ON s.check_id = d.check_id;
