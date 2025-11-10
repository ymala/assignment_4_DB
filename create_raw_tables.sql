CREATE DATABASE IF NOT EXISTS e_commerce_demo
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE e_commerce_demo;

DROP TABLE IF EXISTS raw_stores;
CREATE TABLE raw_stores (
                            store_id VARCHAR(10),
                            format VARCHAR(50),
                            city VARCHAR(100),
                            region VARCHAR(100)
);

DROP TABLE IF EXISTS raw_customers;
CREATE TABLE raw_customers (
                               customer_id VARCHAR(10),
                               name VARCHAR(255),
                               city VARCHAR(100),
                               birthday VARCHAR(20)
);

DROP TABLE IF EXISTS raw_products;
CREATE TABLE raw_products (
                              product_id VARCHAR(10),
                              name VARCHAR(255),
                              unit VARCHAR(10),
                              category VARCHAR(100)
);

DROP TABLE IF EXISTS raw_pricing;
CREATE TABLE raw_pricing (
                             product_id VARCHAR(10),
                             price VARCHAR(20),
                             start_date VARCHAR(20),
                             end_date VARCHAR(20),
                             is_active VARCHAR(5)
);

DROP TABLE IF EXISTS raw_promo;
CREATE TABLE raw_promo (
                           promo_type VARCHAR(10),
                           product_id VARCHAR(10),
                           discount_pct VARCHAR(10),
                           start_date VARCHAR(20),
                           end_date VARCHAR(20),
                           is_active VARCHAR(5),
                           description VARCHAR(255)
);

DROP TABLE IF EXISTS raw_check_summary;
CREATE TABLE raw_check_summary (
                                   check_id VARCHAR(20),
                                   store_id VARCHAR(10),
                                   cashier_id VARCHAR(10),
                                   datetime VARCHAR(30),
                                   customer_id VARCHAR(10)
);

DROP TABLE IF EXISTS raw_check_details;
CREATE TABLE raw_check_details (
                                   check_id VARCHAR(20),
                                   product_id VARCHAR(10),
                                   product_name VARCHAR(255),
                                   unit_price VARCHAR(20),
                                   discount_pct VARCHAR(20),
                                   discount_abs VARCHAR(20),
                                   discount_type VARCHAR(10),
                                   quantity VARCHAR(20),
                                   total_amount VARCHAR(20)
);
