import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

base_dir = Path(__file__).resolve().parent.parent
file_path = base_dir / "05_insert_discount_python.sql"

discount_types = [
    "Weekend Sale",
    "Holiday Sale",
    "Dairy Sale",
    "Bakery Sale",
    "Beverage Sale",
    "Snack Sale",
    "Frozen Food Sale",
    "Cleaning Sale",
    "Personal Care Sale",
    "Special Offer"
]

def random_start_date():
    start = date(2026, 1, 1)
    end = date(2026, 12, 1)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))

with open(file_path, "w", encoding="utf-8") as f:
    for i in range(1, 501):
        discount_name = f"{random.choice(discount_types)} {i}"
        discount_percentage = random.choice([5, 10, 15, 20, 25, 30, 35, 40])
        start_date = random_start_date()
        end_date = start_date + timedelta(days=random.randint(7, 30))

        f.write(
            "INSERT INTO DISCOUNT "
            "(DiscountID, DiscountName, DiscountPercentage, StartDate, EndDate) "
            f"VALUES ({i}, '{discount_name}', {discount_percentage}, '{start_date}', '{end_date}');\n"
        )

print(f"Created: {file_path}")