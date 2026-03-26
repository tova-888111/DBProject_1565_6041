from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
file_path = base_dir / "11_insert_applies_to_python.sql"

with open(file_path, "w", encoding="utf-8") as f:
    for i in range(1, 501):
        product_id = i
        discount_id = i

        f.write(
            "INSERT INTO APPLIES_TO "
            "(ProductID, DiscountID) "
            f"VALUES ({product_id}, {discount_id});\n"
        )

print(f"Created: {file_path}")