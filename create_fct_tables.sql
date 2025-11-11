USE e_commerce_demo;

DROP TABLE IF EXISTS fct_sales;

CREATE TABLE fct_sales (
    date_key INT,
    product_key INT,
    store_key INT,
    customer_key BIGINT,
    check_id BIGINT,
    quantity DECIMAL(18, 4),
    unit_price DECIMAL(18, 4),
    total_amount DECIMAL(18, 4),
    discount_abs DECIMAL(18, 4),

    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (product_key) REFERENCES dim_products(product_key),
    FOREIGN KEY (store_key) REFERENCES dim_stores(store_key),
    FOREIGN KEY (customer_key) REFERENCES dim_customers(customer_key)
);
INSERT INTO fct_sales (
    date_key, product_key, store_key, customer_key,
    check_id,
    quantity, unit_price, total_amount, discount_abs
)
SELECT
    d.date_key,
    COALESCE(p.product_key, -1) AS product_key,
    COALESCE(s.store_key, -1) AS store_key,
    COALESCE(c.customer_key, 0) AS customer_key,
	stg.check_id,
    stg.quantity,
    stg.unit_price,
    stg.total_amount,
    stg.discount_abs

FROM stg_transactions AS stg

LEFT JOIN dim_date AS d
    ON d.full_date = CAST(stg.transaction_datetime AS DATE)

LEFT JOIN dim_products AS p
    ON p.product_id = stg.product_id

LEFT JOIN dim_stores AS s
    ON s.store_id = stg.store_id

LEFT JOIN dim_customers AS c
    ON stg.customer_id = c.customer_id
    AND CAST(stg.transaction_datetime AS DATE) BETWEEN c.valid_from AND c.valid_to;
    
ALTER TABLE fct_sales ADD INDEX idx_fct_date (date_key);
ALTER TABLE fct_sales ADD INDEX idx_fct_product (product_key);
ALTER TABLE fct_sales ADD INDEX idx_fct_store (store_key);
ALTER TABLE fct_sales ADD INDEX idx_fct_customer (customer_key);