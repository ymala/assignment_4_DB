import csv
import random
import os
from faker import Faker
from datetime import datetime, timedelta
from tqdm import tqdm

# --- Налаштування ---
OUTPUT_DIR = "raw_data"

# Кількість рядків
TOTAL_STORES = 100
TOTAL_CUSTOMERS = 20000
TOTAL_PRODUCTS = 2000
TOTAL_PRICING_ROWS = 10000
TOTAL_PROMO_ROWS = 400
TOTAL_CHECK_DETAILS = 1000000
# Припустимо, в середньому 3.5 товари на чек
TOTAL_CHECK_SUMMARY = int(TOTAL_CHECK_DETAILS / 3.5)

# Діапазон дат
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2024, 12, 31)
DATE_RANGE_DAYS = (END_DATE - START_DATE).days

# Списки для цілісності даних
store_ids = []
customer_ids = []
product_data = {}  # {product_id: {'name': '...', 'unit': '...'}}
product_ids = []
check_summary_data = []  # [(check_id, datetime), ...]

# Списки для швидкого пошуку цін/промо (для імітації)
# У реальному DWH це буде зроблено через JOIN
pricing_lookup = {}  # {product_id: [(start, end, price), ...]}
promo_lookup = {}  # {product_id: [(start, end, pct, type), ...]}

# Ініціалізація
fake = Faker('uk_UA')  # Використовуємо українську локаль для міст


# --- Допоміжні функції ---

def ensure_dir(directory):
    """Створює папку, якщо її не існує."""
    if not os.path.exists(directory):
        os.makedirs(directory)


def random_date(start, end):
    """Генерує випадкову дату в діапазоні."""
    return start + timedelta(days=random.randint(0, (end - start).days))


def random_datetime(start, end):
    """Генерує випадкову дату і час."""
    dt = random_date(start, end)
    dt = dt.replace(hour=random.randint(8, 22), minute=random.randint(0, 59))
    return dt


def format_date(dt):
    """Форматує дату як ДД-ММ-РРРР."""
    return dt.strftime('%d-%m-%Y')


def format_datetime(dt):
    """Форматує дату-час як ДД-ММ-РРРР ГГ:ХХ."""
    return dt.strftime('%d-%m-%Y %H:%M')


def get_price_for_date(product_id, date):
    """Знаходить ціну товару на конкретну дату."""
    if product_id not in pricing_lookup:
        return round(random.uniform(10.0, 500.0), 2)  # Fallback

    for start, end, price in pricing_lookup[product_id]:
        if start <= date.date() <= end:
            return price
    # Якщо дата не знайдена (не мало б статися), повертаємо останню ціну
    return pricing_lookup[product_id][-1][2]


def get_promo_for_date(product_id, date):
    """Знаходить промо для товару на конкретну дату."""
    if product_id not in promo_lookup:
        return None

    for start, end, pct, promo_type in promo_lookup[product_id]:
        if start <= date.date() <= end:
            return {'pct': pct, 'type': promo_type}
    return None


# --- Функції-генератори ---

def generate_stores():
    """1. Довідник магазинів"""
    print("Генерація: 1. Довідник магазинів...")
    global store_ids
    formats = ['гіпер', 'супер', 'to go']
    regions = ['Київська', 'Львівська', 'Одеська', 'Харківська', 'Дніпропетровська', 'Запорізька']

    with open(os.path.join(OUTPUT_DIR, 'stores.csv'), 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['store_id', 'format', 'city', 'region'])

        for i in range(TOTAL_STORES):
            store_id = str(100 + i)
            store_ids.append(store_id)
            region = random.choice(regions)
            writer.writerow([
                store_id,
                random.choice(formats),
                fake.city_name(),
                region + ' область'
            ])
    store_ids.append('9999')  # Додаємо онлайн-магазин


def generate_customers():
    """2. Покупці із програми лояльності"""
    print("Генерація: 2. Покупці...")
    global customer_ids

    with open(os.path.join(OUTPUT_DIR, 'customers.csv'), 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['customer_id', 'city', 'birthday'])

        for i in range(TOTAL_CUSTOMERS):
            customer_id = str(10000000 + i)
            customer_ids.append(customer_id)

            city = random.choices([fake.city_name(), '9999'], weights=[0.9, 0.1], k=1)[0]
            dob = random_choices_with_empty(
                [format_date(fake.date_of_birth(minimum_age=18, maximum_age=70))],
                weights=[0.8]
            )

            writer.writerow([customer_id, city, dob])


def random_choices_with_empty(population, weights):
    """Допоміжна функція, що додає "порожнє" значення."""
    return random.choices(population + [''], weights=weights + [1 - sum(weights)], k=1)[0]


def generate_products():
    """3. Довідник номенклатури"""
    print("Генерація: 3. Довідник номенклатури...")
    global product_data, product_ids
    units = ['шт', 'г', 'кг', 'л', 'мл', 'упак']
    categories = [
        'Молочні продукти', 'М\'ясо та птиця', 'Риба', 'Овочі та фрукти', 'Бакалія',
        'Напої', 'Хлібобулочні', 'Солодощі', 'Заморожені продукти', 'Побутова хімія',
        'Алкоголь', 'Дитячі товари', 'Товари для тварин', 'Косметика', 'Для дому',
        'Електроніка', 'Одяг', 'Книги', 'Іграшки', 'Спорттовари'
    ]

    with open(os.path.join(OUTPUT_DIR, 'products.csv'), 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['product_id', 'name', 'unit', 'category'])

        for i in range(TOTAL_PRODUCTS):
            product_id = str(100000 + i)
            unit = random.choice(units)
            name = f"Товар {i} {fake.word()}"  # Проста назва для швидкості

            product_ids.append(product_id)
            product_data[product_id] = {'name': name, 'unit': unit}

            writer.writerow([
                product_id,
                name,
                unit,
                random.choice(categories)
            ])


def generate_pricing():
    """4. Ціноутворення"""
    print("Генерація: 4. Ціноутворення...")
    global pricing_lookup

    with open(os.path.join(OUTPUT_DIR, 'pricing.csv'), 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['product_id', 'price', 'start_date', 'end_date', 'is_active'])

        rows_per_product = TOTAL_PRICING_ROWS // TOTAL_PRODUCTS

        for prod_id in tqdm(product_ids, desc="  Ціни"):
            current_date = START_DATE
            for i in range(rows_per_product):
                price = round(random.uniform(10.0, 5000.0), 2)

                # Гарантуємо не-пересічні дати
                start_dt = current_date
                end_dt = random_date(start_dt + timedelta(days=30), start_dt + timedelta(days=180))

                # Остання дата ціни = кінець періоду
                if i == rows_per_product - 1:
                    end_dt = END_DATE

                # Зберігаємо для швидкого пошуку
                if prod_id not in pricing_lookup:
                    pricing_lookup[prod_id] = []
                pricing_lookup[prod_id].append((start_dt.date(), end_dt.date(), price))

                is_active = 1 if end_dt == END_DATE else 0

                writer.writerow([
                    prod_id,
                    f"{price:.2f}",
                    format_date(start_dt),
                    format_date(end_dt),
                    is_active
                ])

                current_date = end_dt + timedelta(days=1)
                if current_date > END_DATE:
                    break


def generate_promo():
    """5. Промо від маркетингу"""
    print("Генерація: 5. Промо...")
    global promo_lookup
    promo_types = [str(i) for i in range(10, 20)]
    promo_descriptions = {
        '10': 'Ціна тижня', '11': '1+1', '12': 'Знижка 30%', '13': 'Товар дня',
        '14': 'Чорна п\'ятниця', '15': 'Сезонний розпродаж', '16': 'Новорічна',
        '17': 'До ДН', '18': 'За 2 од.', '19': 'Весняна'
    }

    with open(os.path.join(OUTPUT_DIR, 'promo.csv'), 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(
            ['promo_type', 'product_id', 'discount_pct', 'start_date', 'end_date', 'is_active', 'description'])

        for _ in range(TOTAL_PROMO_ROWS):
            prod_id = random.choice(product_ids)
            promo_type = random.choice(promo_types)
            discount_pct = random.randint(10, 50)

            start_dt = random_date(START_DATE, END_DATE - timedelta(days=30))
            end_dt = random_date(start_dt + timedelta(days=7), start_dt + timedelta(days=30))
            if end_dt > END_DATE:
                end_dt = END_DATE

            # Зберігаємо для швидкого пошуку
            if prod_id not in promo_lookup:
                promo_lookup[prod_id] = []
            promo_lookup[prod_id].append((start_dt.date(), end_dt.date(), discount_pct, promo_type))

            is_active = 1 if end_dt.date() >= datetime.now().date() >= start_dt.date() else 0

            writer.writerow([
                promo_type,
                prod_id,
                discount_pct,
                format_date(start_dt),
                format_date(end_dt),
                is_active,
                promo_descriptions[promo_type]
            ])


def generate_check_summary():
    """6. Касовий апарат (Підсумки)"""
    print("Генерація: 6. Касовий апарат (Підсумки)...")
    global check_summary_data

    with open(os.path.join(OUTPUT_DIR, 'check_summary.csv'), 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['check_id', 'store_id', 'cashier_id', 'datetime', 'customer_id'])

        start_check_id = 100000000000

        for i in tqdm(range(TOTAL_CHECK_SUMMARY), desc="  Чеки"):
            check_id = str(start_check_id + i)
            dt = random_datetime(START_DATE, END_DATE)

            store_id = random.choice(store_ids)
            cashier_id = '' if store_id == '9999' else str(random.randint(1, 10))

            # --- ОСЬ ВИПРАВЛЕНИЙ РЯДОК ---
            # 60% чеків з карткою, 40% - без
            customer_id = random.choice(customer_ids) if random.random() < 0.6 else ''

            check_summary_data.append((check_id, dt, store_id))

            writer.writerow([
                check_id,
                store_id,
                cashier_id,
                format_datetime(dt),
                customer_id
            ])

def generate_check_details():
    """7. Касовий апарат (Розширено)"""
    print("Генерація: 7. Касовий апарат (Розширено)...")

    with open(os.path.join(OUTPUT_DIR, 'check_details.csv'), 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'check_id', 'product_id', 'product_name', 'unit_price', 'discount_pct',
            'discount_abs', 'discount_type', 'quantity', 'total_amount'
        ])

        details_count = 0

        # Використовуємо tqdm для зовнішнього циклу
        pbar = tqdm(total=TOTAL_CHECK_DETAILS, desc="  Товари в чеках")

        while details_count < TOTAL_CHECK_DETAILS:
            for check_id, dt, store_id in check_summary_data:
                # Випадкова кількість товарів у чеку (1-7)
                items_in_check = random.randint(1, 7)

                for _ in range(items_in_check):
                    if details_count >= TOTAL_CHECK_DETAILS:
                        break  # Досягли ліміту

                    prod_id = random.choice(product_ids)
                    prod_info = product_data[prod_id]

                    unit_price = get_price_for_date(prod_id, dt)

                    if prod_info['unit'] in ['шт', 'упак', 'л', 'кг']:
                        quantity = random.randint(1, 5)
                    else:  # г, мл
                        quantity = round(random.uniform(0.1, 1.5), 3)

                    discount_pct = ''
                    discount_abs = ''
                    discount_type = ''

                    promo = get_promo_for_date(prod_id, dt)

                    # 30% шанс на знижку (або промо, або фіксована)
                    if random.random() < 0.3:
                        if promo and random.random() < 0.7:  # 70% шанс, що спрацює промо
                            discount_pct = promo['pct']
                            discount_type = promo['type']
                            discount_abs_calc = (unit_price * quantity * promo['pct']) / 100
                        else:  # Або просто фіксована знижка
                            discount_type = '99'  # Ручна знижка
                            discount_abs_calc = round(random.uniform(1.0, unit_price * 0.2), 2)  # до 20%

                        discount_abs = f"{discount_abs_calc:.2f}"

                    # Розрахунок фінальної суми
                    total_amount_calc = (unit_price * quantity)
                    if discount_abs:
                        total_amount_calc -= float(discount_abs)

                    total_amount = f"{max(0, total_amount_calc):.2f}"  # Не може бути < 0

                    writer.writerow([
                        check_id,
                        prod_id,
                        prod_info['name'],
                        f"{unit_price:.2f}",
                        discount_pct,
                        discount_abs,
                        discount_type,
                        quantity,
                        total_amount
                    ])

                    details_count += 1
                    pbar.update(1)  # Оновлюємо progress bar

                if details_count >= TOTAL_CHECK_DETAILS:
                    break

            # Якщо ми пройшли всі чеки, а ліміт не досягнуто, почнемо знову
            if details_count >= TOTAL_CHECK_DETAILS:
                break

        pbar.close()


# --- Головна функція ---

def main():
    print("Початок генерації RAW-даних...")
    ensure_dir(OUTPUT_DIR)

    # Генератори довідників (Dimensions)
    generate_stores()  # 1
    generate_customers()  # 2
    generate_products()  # 3

    # Залежні довідники (потребують ID з попередніх)
    generate_pricing()  # 4
    generate_promo()  # 5

    # Генератори "фактів" (потребують ID з довідників)
    generate_check_summary()  # 6

    # Головний генератор (залежить від чеків, цін, промо)
    generate_check_details()  # 7

    print(
        f"\n✅ Успіх! Всі {TOTAL_CHECK_DETAILS + TOTAL_CHECK_SUMMARY + TOTAL_STORES + TOTAL_CUSTOMERS + TOTAL_PRODUCTS + TOTAL_PRICING_ROWS + TOTAL_PROMO_ROWS} рядків згенеровано в папці '{OUTPUT_DIR}'.")


if __name__ == "__main__":
    main()