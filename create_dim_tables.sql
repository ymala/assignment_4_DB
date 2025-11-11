USE e_commerce_demo;

DROP TABLE IF EXISTS fct_sales;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_products;
DROP TABLE IF EXISTS dim_stores;
DROP TABLE IF EXISTS dim_customers;

CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE NOT NULL,
    day_of_week_num INT NOT NULL,
    day_of_week_name VARCHAR(20),
    month_number INT NOT NULL,
    month_name VARCHAR(20),
    quarter INT NOT NULL,
    year INT NOT NULL
);

CREATE TABLE dim_products (
    product_key INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    name VARCHAR(255),
    unit_of_measure VARCHAR(50),
    category VARCHAR(100),
    current_retail_price DECIMAL(10, 2)
);
ALTER TABLE dim_products ADD INDEX idx_dim_prod_natural (product_id);

REPLACE INTO dim_products (product_key, product_id, name)
VALUES (-1, -1, 'Unknown'); 

CREATE TABLE dim_stores (
    store_key INT AUTO_INCREMENT PRIMARY KEY,
    store_id INT NOT NULL,
    format VARCHAR(100),
    city VARCHAR(100),
    region VARCHAR(100)
);
ALTER TABLE dim_stores ADD INDEX idx_dim_store_natural (store_id);

REPLACE INTO dim_stores (store_key, store_id, format, city, region)
VALUES (-1, -1, 'Unknown', 'Unknown', 'Unknown');

CREATE TABLE dim_customers (
    customer_key BIGINT AUTO_INCREMENT PRIMARY KEY,
    customer_id BIGINT,
    name VARCHAR(255),
    city VARCHAR(100),
    birthday DATE,
    valid_from DATE NOT NULL,
    valid_to DATE NOT NULL,
    is_current BOOLEAN NOT NULL
);
ALTER TABLE dim_customers ADD INDEX idx_dim_cust_lookup (customer_id, is_current);
ALTER TABLE dim_customers ADD INDEX idx_dim_cust_natural (customer_id);

SET @@SESSION.sql_mode = CONCAT(@@SESSION.sql_mode, ',NO_AUTO_VALUE_ON_ZERO'); 

REPLACE INTO dim_customers (customer_key, customer_id, name, city, valid_from, valid_to, is_current)
VALUES (0, NULL, 'Guest Customer', 'Unknown', '1900-01-01', '9999-12-31', TRUE); -- placeholder

ALTER TABLE dim_customers AUTO_INCREMENT = 1;
