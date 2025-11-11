-- ! only for updating customer data !

USE e_commerce_demo;

SET @update_date = CURDATE();

DROP TEMPORARY TABLE IF EXISTS tmp_changed_customers;
CREATE TEMPORARY TABLE tmp_changed_customers AS
SELECT
    s.customer_id,
    s.name,
    s.city,
    s.birthday
FROM stg_customers AS s
JOIN dim_customers AS d
    ON s.customer_id = d.customer_id AND d.is_current = TRUE
WHERE
    COALESCE(s.city, '') != COALESCE(d.city, '');
   
UPDATE dim_customers d
JOIN tmp_changed_customers t ON d.customer_id = t.customer_id
SET
    d.is_current = FALSE,
    d.valid_to = DATE_SUB(@update_date, INTERVAL 1 DAY)
WHERE
    d.is_current = TRUE;


INSERT INTO dim_customers (customer_id, name, city, birthday, valid_from, valid_to, is_current)
SELECT
    t.customer_id,
    t.name,
    t.city,
    t.birthday,
    @update_date AS valid_from,
    '9999-12-31' AS valid_to,
    TRUE AS is_current
FROM tmp_changed_customers AS t;

INSERT INTO dim_customers (customer_id, name, city, birthday, valid_from, valid_to, is_current)
SELECT
    s.customer_id,
    s.name,
    s.city,
    s.birthday,
    @update_date AS valid_from,
    '9999-12-31' AS valid_to,
    TRUE AS is_current
FROM stg_customers AS s
LEFT JOIN dim_customers AS d ON s.customer_id = d.customer_id
WHERE
    d.customer_id IS NULL; 

DROP TEMPORARY TABLE IF EXISTS tmp_changed_customers;