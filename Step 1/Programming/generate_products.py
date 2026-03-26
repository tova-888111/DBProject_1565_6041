import random
from datetime import date, timedelta
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
print("BASE DIR:", base_dir)

def random_date():
    start = date(2026, 1, 1)
    end = date(2027, 12, 31)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))

file_path = base_dir / "07_insert_product_python.sql"
print("OUTPUT FILE:", file_path)

with open(file_path, "w", encoding="utf-8") as f:
    for i in range(1, 20001):
        product_name = f"Product {i}"
        price = round(random.uniform(5, 200), 2)
        kashrut = random.choice(["Badatz", "Rabanut", "Mehadrin"])
        brand = random.choice(["Tnuva", "Osem", "Strauss", "Elite", "Coca Cola"])
        expiration_date = random_date()
        category_id = random.randint(1, 500)

        line = (
            f"INSERT INTO PRODUCT (ProductID, ProductName, Price, Kashrut, Brand, ExpirationDate, CategoryID) "
            f"VALUES ({i}, '{product_name}', {price}, '{kashrut}', '{brand}', '{expiration_date}', {category_id});\n"
        )
        f.write(line)

print("Products SQL file created!")