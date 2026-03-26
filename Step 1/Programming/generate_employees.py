import random
from pathlib import Path

random.seed(42)

base_dir = Path(__file__).resolve().parent.parent
file_path = base_dir / "08_insert_employee_python.sql"

first_names = [
    "Noam", "Yael", "Dana", "Roni", "Maya",
    "Lior", "Neta", "Yarden", "Omri", "Eden"
]

last_names = [
    "Cohen", "Levi", "Mizrahi", "Peretz", "Biton",
    "Malka", "Avraham", "Dahan", "Amar", "Haddad"
]

statuses = ["Active", "Inactive"]
roles = [
    "Cashier",
    "Store Manager",
    "Shift Manager",
    "Stock Clerk",
    "Customer Service Representative",
    "Department Manager"
]

with open(file_path, "w", encoding="utf-8") as f:
    for i in range(1, 501):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        status = random.choice(statuses)
        salary = round(random.uniform(6000, 18000), 2)
        role = random.choice(roles)
        store_id = i  # 500 עובדים, כל עובד לחנות קיימת אחת

        f.write(
            "INSERT INTO EMPLOYEE "
            "(EmployeeID, FirstName, LastName, Status, Salary, Role, StoreID) "
            f"VALUES ({i}, '{first_name}', '{last_name}', '{status}', {salary}, '{role}', {store_id});\n"
        )

print(f"Created: {file_path}")