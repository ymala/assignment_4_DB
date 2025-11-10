import csv
import os
import mysql.connector

DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'YOUR PASSWORD',
    'database': 'e_commerce_demo'
}

RAW_DATA_DIR = 'raw_data'
BATCH_SIZE = 50000

TABLE_FILES_MAP = {
    'raw_stores': 'stores.csv',
    'raw_customers': 'customers.csv',
    'raw_products': 'products.csv',
    'raw_pricing': 'pricing.csv',
    'raw_promo': 'promo.csv',
    'raw_check_summary': 'check_summary.csv',
    'raw_check_details': 'check_details.csv'
}


def load_csv_to_db(connection, cursor, table_name, file_path):
    print(f"  Завантаження '{file_path}' в таблицю '{table_name}'...")

    try:
        cursor.execute(f"TRUNCATE TABLE {table_name}")
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            header_sql = ", ".join([f"`{col}`" for col in header])  # `col_name`
            placeholders = ", ".join(["%s"] * len(header))  # %s, %s, %s
            insert_sql = f"INSERT INTO {table_name} ({header_sql}) VALUES ({placeholders})"
            batch = []
            row_count = 0

            for row in reader:
                batch.append(row)

                if len(batch) >= BATCH_SIZE:
                    cursor.executemany(insert_sql, batch)
                    connection.commit()
                    row_count += len(batch)
                    print(f"    ...завантажено {row_count} рядків...")
                    batch = []

            if batch:
                cursor.executemany(insert_sql, batch)
                connection.commit()
                row_count += len(batch)

            print(f"  ✅ Успіх! Всього завантажено {row_count} рядків.")

    except Exception as e:
        print(f"\n  ❌ ПОМИЛКА при завантаженні '{table_name}': {e}")
        print("  Можливо, назви стовпців у CSV не збігаються з тими, що у 'create_raw_db.sql'?")


def main():
    print("Підключення до бази даних MySQL...")
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        print("✅ Підключення успішне.")

        for table_name, file_name in TABLE_FILES_MAP.items():
            file_path = os.path.join(RAW_DATA_DIR, file_name)

            if os.path.exists(file_path):
                load_csv_to_db(connection, cursor, table_name, file_path)
            else:
                print(f"  ⚠️ Попередження: Файл '{file_path}' не знайдено, пропуск.")

        print("\n🎉 Вся робота з завантаження RAW-шару завершена!")
        cursor.close()
        connection.close()

    except mysql.connector.Error as e:
        print(f"❌ Помилка підключення до MySQL: {e}")


if __name__ == "__main__":
    main()