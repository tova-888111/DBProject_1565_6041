from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
file_path = base_dir / "10_insert_suppliered_by_python.sql"

with open(file_path, "w", encoding="utf-8") as f:
    for i in range(1, 501):
        supplier_id = i
        product_id = i

        f.write(
            "INSERT INTO SUPPLIERED_BY "
            "(SupplierID, ProductID) "
            f"VALUES ({supplier_id}, {product_id});\n"
        )

print(f"Created: {file_path}")