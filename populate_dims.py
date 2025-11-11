import pandas as pd

import numpy as np

import mysql.connector

from datetime import date, timedelta


DB_CONFIG = {

    'user': 'root',

    'password': 'YOUR-PASSWORD',

    'host': 'localhost',

    'database': 'e_commerce_demo'

}


print("Встановлення з'єднання...")


try:

    cnx = mysql.connector.connect(**DB_CONFIG)

    cursor = cnx.cursor()


    print("Заповнення dim_date...")

    sql_dim_date = """

        INSERT INTO dim_date (date_key, full_date, day_of_week_num, day_of_week_name, month_number, month_name, quarter, year)

        WITH RECURSIVE DateRange AS (

            SELECT MIN(CAST(transaction_datetime AS DATE)) AS date_val FROM stg_transactions

            UNION ALL

            SELECT DATE_ADD(date_val, INTERVAL 1 DAY) FROM DateRange

            WHERE date_val < (SELECT MAX(CAST(transaction_datetime AS DATE)) FROM stg_transactions)

        )

        SELECT

            CAST(DATE_FORMAT(date_val, '%Y%m%d') AS SIGNED) AS date_key,

            date_val AS full_date, DAYOFWEEK(date_val), DAYNAME(date_val),

            MONTH(date_val), MONTHNAME(date_val), QUARTER(date_val), YEAR(date_val)

        FROM DateRange

    """

    cursor.execute("SET @@cte_max_recursion_depth = 2000;")

    cursor.execute(sql_dim_date)

    cursor.execute("SET @@cte_max_recursion_depth = 1000;")

    cnx.commit() 

    print("Заповнення dim_products та dim_stores...")

    

    df_products = pd.read_sql("SELECT product_id, name, unit, category, current_retail_price FROM stg_products", cnx)

    


    product_tuples = list(df_products.itertuples(index=False, name=None))

    insert_sql = "INSERT INTO dim_products (product_id, name, unit_of_measure, category, current_retail_price) VALUES (%s, %s, %s, %s, %s)"

    cursor.executemany(insert_sql, product_tuples)

    cnx.commit()


    df_stores = pd.read_sql("SELECT store_id, store_format, city, region FROM stg_stores", cnx)

    store_tuples = list(df_stores.itertuples(index=False, name=None))

    insert_sql = "INSERT INTO dim_stores (store_id, format, city, region) VALUES (%s, %s, %s, %s)"

    cursor.executemany(insert_sql, store_tuples)

    cnx.commit()

    print("Заповнення dim_customers з SCD2...")


    df_stg = pd.read_sql("SELECT customer_id, name, city, birthday FROM stg_customers", cnx)


    sql_first_purchase = """

        SELECT

            customer_id,

            MIN(CAST(transaction_datetime AS DATE)) AS first_purchase_date

        FROM stg_transactions

        WHERE customer_id IS NOT NULL

        GROUP BY customer_id

    """

    df_first_purchase = pd.read_sql(sql_first_purchase, cnx)

    print("Симуляція історії клієнтів...")

    df_dim = df_stg.merge(df_first_purchase, on='customer_id', how='left')

    df_dim['first_purchase_date'] = df_dim['first_purchase_date'].fillna(pd.to_datetime('today').date())

    df_dim['valid_from'] = pd.to_datetime(df_dim['first_purchase_date'])

    df_dim['valid_to'] = date(9999, 12, 31)

    df_dim['is_current'] = 1


    historical_records = []

    old_cities = ['Київ', 'Одеса', 'Харків', 'Дніпро', 'Варшава']

    customer_ids_to_change = df_dim.loc[df_dim['customer_id'].notnull(), 'customer_id'].sample(frac=0.3)


    for cust_id in customer_ids_to_change:

        current_index_list = df_dim[df_dim['customer_id'] == cust_id].index

        if len(current_index_list) == 0:

            continue

        current_index = current_index_list[0]

        

        start = df_dim.at[current_index, 'valid_from'].date()

        end = pd.to_datetime('today').date()

        

        if start >= end:

            continue

            

        days_diff = (end - start).days

        random_days = np.random.randint(1, days_diff)

        change_date = start + timedelta(days=random_days)

        

        df_dim.at[current_index, 'valid_from'] = change_date


        historical_record = df_dim.loc[current_index].to_dict()

        current_city = historical_record['city']

        new_old_city = np.random.choice([c for c in old_cities if c != current_city])

        

        historical_record['city'] = new_old_city

        historical_record['valid_from'] = df_dim.at[current_index, 'first_purchase_date']

        historical_record['valid_to'] = change_date - timedelta(days=1)

        historical_record['is_current'] = 0

        historical_records.append(historical_record)


    df_final_dim = pd.concat([df_dim, pd.DataFrame(historical_records)], ignore_index=True)

    df_final_dim = df_final_dim.drop(columns=['first_purchase_date'])

    print(f"Завантаження {len(df_final_dim)} рядків у dim_customers...")

    df_final_dim = df_final_dim[[

        'customer_id', 'name', 'city', 'birthday', 

        'valid_from', 'valid_to', 'is_current'

    ]]

    

    customer_tuples = list(df_final_dim.itertuples(index=False, name=None))

    

  
    clean_tuples = []

    for row in customer_tuples:

        clean_row = [None if pd.isna(item) else item for item in row]

        clean_tuples.append(tuple(clean_row))


    insert_sql = """

        INSERT INTO dim_customers 

        (customer_id, name, city, birthday, valid_from, valid_to, is_current) 

        VALUES (%s, %s, %s, %s, %s, %s, %s)

    """

    

    cursor.executemany(insert_sql, clean_tuples)

    cnx.commit()


    print("Готово!")


finally:


    if 'cursor' in locals() and cursor:

        cursor.close()

    if 'cnx' in locals() and cnx and cnx.is_connected():

        cnx.close()

    print("З'єднання закрито.")


