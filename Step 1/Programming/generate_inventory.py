import random
from pathlib import Path

random.seed(42)

base_dir = Path(__file__).resolve().parent.parent
file_path = base_dir / "09_insert_inventory_python.sql"

with open(file_path, "w", encoding="utf-8") as f:
    for product_id in range(1, 20001):
        store_id = ((product_id - 1) % 500) + 1
        quantity = random.randint(0, 300)
        minimum_stock = random.randint(5, 50)

        f.write(
            "INSERT INTO INVENTORY "
            "(StoreID, ProductID, Quantity, MinimumStock) "
            f"VALUES ({store_id}, {product_id}, {quantity}, {minimum_stock});\n"
        )

print(f"Created: {file_path}")