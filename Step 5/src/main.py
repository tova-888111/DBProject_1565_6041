import os
import tkinter as tk
from tkinter import messagebox, ttk
from decimal import Decimal

import customtkinter as ctk
try:
    from PIL import Image
except Exception:
    Image = None

from db_connection import get_db_connection


# ============================================================
# Theme
# ============================================================
PRIMARY_GREEN = "#2E7D32"
DARK_GREEN = "#1B5E20"
LIGHT_GREEN = "#E8F5E9"
BACKGROUND = "#F7F8FA"
CARD_BG = "#FFFFFF"
TEXT_DARK = "#263238"
TEXT_GRAY = "#607D8B"
DANGER = "#C62828"
WARNING = "#F9A825"
BORDER = "#E0E0E0"

FONT_TITLE = ("Arial", 26, "bold")
FONT_SUBTITLE = ("Arial", 15)
FONT_BUTTON = ("Arial", 14, "bold")
FONT_TEXT = ("Arial", 13)
FONT_SMALL = ("Arial", 12)


# ============================================================
# Table configuration based on Step 4 createTable.sql
# ============================================================
TABLES = {
    "STORE": {
        "label": "סניפים",
        "sql": "STORE",
        "pk": ["StoreID"],
        "auto_pk": True,
        "columns": ["StoreID", "StoreName", "Phone", "StoreEmail", "Rating", "websiteurl", "Address", "Region"],
        "headers": {
            "StoreName": "שם סניף", "Phone": "טלפון", "StoreEmail": "אימייל", "Rating": "דירוג",
            "websiteurl": "אתר", "Address": "כתובת", "Region": "אזור"
        },
    },
    "EMPLOYEE": {
        "label": "עובדים",
        "sql": "EMPLOYEE",
        "pk": ["EmployeeID"],
        "auto_pk": True,
        "columns": ["EmployeeID", "FirstName", "LastName", "Status", "Salary", "Role", "StoreID"],
        "headers": {
            "FirstName": "שם פרטי", "LastName": "שם משפחה", "Status": "סטטוס", "Salary": "שכר",
            "Role": "תפקיד", "StoreID": "סניף"
        },
        "fks": {
            "StoreID": {"table": "STORE", "sql": "STORE", "pk": "StoreID", "label_sql": "r.StoreName", "order_by": "r.StoreName"}
        },
    },
    "CATEGORY": {
        "label": "קטגוריות",
        "sql": "CATEGORY",
        "pk": ["CategoryID"],
        "auto_pk": True,
        "columns": ["CategoryID", "CategoryName", "IsActive"],
        "headers": {"CategoryName": "שם קטגוריה", "IsActive": "פעיל"},
    },
    "PRODUCT": {
        "label": "מוצרים",
        "sql": "PRODUCT",
        "pk": ["ProductID"],
        "auto_pk": True,
        "columns": ["ProductID", "ProductName", "Price", "Brand", "ExpirationDate", "dateofmanufacture", "CategoryID"],
        "headers": {
            "ProductName": "שם מוצר", "Price": "מחיר", "Brand": "מותג/יצרן",
            "ExpirationDate": "תאריך תפוגה", "dateofmanufacture": "תאריך ייצור", "CategoryID": "קטגוריה"
        },
        "fks": {
            "CategoryID": {"table": "CATEGORY", "sql": "CATEGORY", "pk": "CategoryID", "label_sql": "r.CategoryName", "order_by": "r.CategoryName"}
        },
    },
    "SUPPLIER": {
        "label": "ספקים",
        "sql": "SUPPLIER",
        "pk": ["SupplierID"],
        "auto_pk": True,
        "columns": ["SupplierID", "SupplierName", "Email", "ContactPhone", "Address"],
        "headers": {"SupplierName": "שם ספק", "Email": "אימייל", "ContactPhone": "טלפון", "Address": "כתובת"},
    },
    "INVENTORY": {
        "label": "מלאי",
        "sql": "INVENTORY",
        "pk": ["StoreID", "ProductID"],
        "auto_pk": False,
        "columns": ["StoreID", "ProductID", "Quantity", "MinimumStock"],
        "headers": {"StoreID": "סניף", "ProductID": "מוצר", "Quantity": "כמות", "MinimumStock": "מלאי מינימלי"},
        "fks": {
            "StoreID": {"table": "STORE", "sql": "STORE", "pk": "StoreID", "label_sql": "r.StoreName", "order_by": "r.StoreName"},
            "ProductID": {"table": "PRODUCT", "sql": "PRODUCT", "pk": "ProductID", "label_sql": "r.ProductName", "order_by": "r.ProductName"},
        },
    },
    "DISCOUNT": {
        "label": "הנחות",
        "sql": "DISCOUNT",
        "pk": ["DiscountID"],
        "auto_pk": True,
        "columns": ["DiscountID", "DiscountName", "DiscountPercentage", "StartDate", "EndDate"],
        "headers": {"DiscountName": "שם הנחה", "DiscountPercentage": "אחוז הנחה", "StartDate": "מתאריך", "EndDate": "עד תאריך"},
    },
    "WAREHOUSE": {
        "label": "מחסנים",
        "sql": "WAREHOUSE",
        "pk": ["WarehouseID"],
        "auto_pk": True,
        "columns": ["WarehouseID", "Region", "Address"],
        "headers": {"Region": "אזור", "Address": "כתובת"},
    },
    "DELIVERYCOMPANY": {
        "label": "חברות משלוח",
        "sql": "DELIVERYCOMPANY",
        "pk": ["DeliveryCieID"],
        "auto_pk": True,
        "columns": ["DeliveryCieID", "DeliveryCieName", "DeliveryCiePhoneNb", "Email"],
        "headers": {"DeliveryCieName": "חברת משלוח", "DeliveryCiePhoneNb": "טלפון", "Email": "אימייל"},
    },
    "TRUCK": {
        "label": "משאיות / נהגים",
        "sql": "TRUCK",
        "pk": ["DriverID"],
        "auto_pk": True,
        "columns": ["DriverID", "Active", "Capacity", "LicensePlate", "MaintenanceStatus", "DeliveryCieID"],
        "headers": {
            "Active": "פעיל", "Capacity": "קיבולת", "LicensePlate": "לוחית רישוי",
            "MaintenanceStatus": "מצב תחזוקה", "DeliveryCieID": "חברת משלוח"
        },
        "fks": {
            "DeliveryCieID": {"table": "DELIVERYCOMPANY", "sql": "DELIVERYCOMPANY", "pk": "DeliveryCieID", "label_sql": "r.DeliveryCieName", "order_by": "r.DeliveryCieName"}
        },
    },
    "ORDER": {
        "label": "הזמנות",
        "sql": '"ORDER"',
        "pk": ["OrderId"],
        "auto_pk": True,
        "columns": ["OrderId", "Price", "DeliveryDate", "OrderDate", "StoreID", "DriverID", "Status"],
        "headers": {
            "Price": "מחיר", "DeliveryDate": "תאריך משלוח", "OrderDate": "תאריך הזמנה",
            "StoreID": "סניף", "DriverID": "משאית/נהג", "Status": "סטטוס"
        },
        "skip_insert": ["OrderDate"],
        "readonly_update": ["OrderDate"],
        "fks": {
            "StoreID": {"table": "STORE", "sql": "STORE", "pk": "StoreID", "label_sql": "r.StoreName", "order_by": "r.StoreName"},
            "DriverID": {"table": "TRUCK", "sql": "TRUCK", "pk": "DriverID", "label_sql": "r.LicensePlate", "order_by": "r.LicensePlate"},
        },
    },
    "PRODUCT_KASHRUT": {
        "label": "כשרות מוצר",
        "sql": "PRODUCT_KASHRUT",
        "pk": ["Kashrut", "ProductID"],
        "auto_pk": False,
        "columns": ["ProductID", "Kashrut"],
        "headers": {"ProductID": "מוצר", "Kashrut": "כשרות"},
        "fks": {
            "ProductID": {"table": "PRODUCT", "sql": "PRODUCT", "pk": "ProductID", "label_sql": "r.ProductName", "order_by": "r.ProductName"}
        },
    },
    "WAREHOUSEMANAGER": {
        "label": "מנהלי מחסנים",
        "sql": "WAREHOUSEMANAGER",
        "pk": ["WarehouseManager", "WarehouseID"],
        "auto_pk": False,
        "columns": ["WarehouseID", "WarehouseManager"],
        "headers": {"WarehouseID": "מחסן", "WarehouseManager": "מנהל מחסן"},
        "fks": {
            "WarehouseID": {"table": "WAREHOUSE", "sql": "WAREHOUSE", "pk": "WarehouseID", "label_sql": "r.Region || ' - ' || r.Address", "order_by": "r.Region"}
        },
    },
    "DELIVERYCOMPANY_REGIONSERVED": {
        "label": "אזורי שירות לחברות משלוח",
        "sql": "DELIVERYCOMPANY_REGIONSERVED",
        "pk": ["RegionServed", "DeliveryCieID"],
        "auto_pk": False,
        "columns": ["DeliveryCieID", "RegionServed"],
        "headers": {"DeliveryCieID": "חברת משלוח", "RegionServed": "אזור שירות"},
        "fks": {
            "DeliveryCieID": {"table": "DELIVERYCOMPANY", "sql": "DELIVERYCOMPANY", "pk": "DeliveryCieID", "label_sql": "r.DeliveryCieName", "order_by": "r.DeliveryCieName"}
        },
    },
    "SUPPLIERED_BY": {
        "label": "ספקים ומוצרים",
        "sql": "SUPPLIERED_BY",
        "pk": ["SupplierID", "ProductID"],
        "auto_pk": False,
        "columns": ["SupplierID", "ProductID"],
        "headers": {"SupplierID": "ספק", "ProductID": "מוצר"},
        "fks": {
            "SupplierID": {"table": "SUPPLIER", "sql": "SUPPLIER", "pk": "SupplierID", "label_sql": "r.SupplierName", "order_by": "r.SupplierName"},
            "ProductID": {"table": "PRODUCT", "sql": "PRODUCT", "pk": "ProductID", "label_sql": "r.ProductName", "order_by": "r.ProductName"},
        },
    },
    "APPLIES_TO": {
        "label": "הנחות על מוצרים",
        "sql": "APPLIES_TO",
        "pk": ["ProductID", "DiscountID"],
        "auto_pk": False,
        "columns": ["ProductID", "DiscountID"],
        "headers": {"ProductID": "מוצר", "DiscountID": "הנחה"},
        "fks": {
            "ProductID": {"table": "PRODUCT", "sql": "PRODUCT", "pk": "ProductID", "label_sql": "r.ProductName", "order_by": "r.ProductName"},
            "DiscountID": {"table": "DISCOUNT", "sql": "DISCOUNT", "pk": "DiscountID", "label_sql": "r.DiscountName", "order_by": "r.DiscountName"},
        },
    },
    "CONTAINS": {
        "label": "פריטים בהזמנה",
        "sql": "CONTAINS",
        "pk": ["OrderId", "ProductID"],
        "auto_pk": False,
        "columns": ["OrderId", "ProductID", "Quantity"],
        "headers": {"OrderId": "הזמנה", "ProductID": "מוצר", "Quantity": "כמות"},
        "fks": {
            "OrderId": {"table": "ORDER", "sql": '"ORDER"', "pk": "OrderId", "label_sql": "'Order ' || r.OrderId::TEXT", "order_by": "r.OrderId"},
            "ProductID": {"table": "PRODUCT", "sql": "PRODUCT", "pk": "ProductID", "label_sql": "r.ProductName", "order_by": "r.ProductName"},
        },
    },
    "LOCATED": {
        "label": "מיקום מוצרים במחסן",
        "sql": "LOCATED",
        "pk": ["ProductID", "WarehouseID"],
        "auto_pk": False,
        "columns": ["ProductID", "WarehouseID", "AisleNb", "ShelfNb"],
        "headers": {"ProductID": "מוצר", "WarehouseID": "מחסן", "AisleNb": "מספר מעבר", "ShelfNb": "מספר מדף"},
        "fks": {
            "ProductID": {"table": "PRODUCT", "sql": "PRODUCT", "pk": "ProductID", "label_sql": "r.ProductName", "order_by": "r.ProductName"},
            "WarehouseID": {"table": "WAREHOUSE", "sql": "WAREHOUSE", "pk": "WarehouseID", "label_sql": "r.Region || ' - ' || r.Address", "order_by": "r.Region"},
        },
    },
}


REPORTS = {
    "מוצרים במלאי נמוך": """
        SELECT
            p.ProductName AS "שם מוצר",
            s.StoreName AS "סניף",
            c.CategoryName AS "קטגוריה",
            i.Quantity AS "כמות",
            i.MinimumStock AS "מלאי מינימלי"
        FROM INVENTORY i
        JOIN PRODUCT p ON i.ProductID = p.ProductID
        JOIN STORE s ON i.StoreID = s.StoreID
        JOIN CATEGORY c ON p.CategoryID = c.CategoryID
        WHERE i.Quantity < i.MinimumStock
        ORDER BY p.ProductName, s.StoreName;
    """,
    "עובדים פעילים לפי סניף": """
        SELECT
            e.FirstName AS "שם פרטי",
            e.LastName AS "שם משפחה",
            e.Role AS "תפקיד",
            e.Salary AS "שכר",
            s.StoreName AS "סניף"
        FROM EMPLOYEE e
        JOIN STORE s ON e.StoreID = s.StoreID
        WHERE e.Status = 'Active'
        ORDER BY s.StoreName, e.LastName;
    """,
    "ספקים וכמות מוצרים": """
        SELECT
            s.SupplierName AS "שם ספק",
            s.Email AS "אימייל",
            s.ContactPhone AS "טלפון",
            COUNT(sb.ProductID) AS "כמות מוצרים"
        FROM SUPPLIER s
        JOIN SUPPLIERED_BY sb ON s.SupplierID = sb.SupplierID
        GROUP BY s.SupplierID, s.SupplierName, s.Email, s.ContactPhone
        ORDER BY s.SupplierName;
    """,
    "מצב מלאי מפורט": """
        SELECT
            p.ProductName AS "מוצר",
            s.StoreName AS "סניף",
            c.CategoryName AS "קטגוריה",
            i.Quantity AS "כמות",
            i.MinimumStock AS "מינימום",
            CASE
                WHEN i.Quantity = 0 THEN 'Out of Stock'
                WHEN i.Quantity < i.MinimumStock THEN 'Low Stock'
                ELSE 'In Stock'
            END AS "סטטוס מלאי"
        FROM INVENTORY i
        JOIN PRODUCT p ON i.ProductID = p.ProductID
        JOIN STORE s ON i.StoreID = s.StoreID
        JOIN CATEGORY c ON p.CategoryID = c.CategoryID
        ORDER BY p.ProductName, s.StoreName;
    """,
    "סיכום רשת": """
        SELECT
            (SELECT COUNT(*) FROM STORE) AS "סניפים",
            (SELECT COUNT(*) FROM EMPLOYEE) AS "עובדים",
            (SELECT COUNT(*) FROM PRODUCT) AS "מוצרים",
            (SELECT SUM(Quantity) FROM INVENTORY) AS "סך מלאי",
            (SELECT COUNT(*) FROM INVENTORY WHERE Quantity < MinimumStock) AS "נקודות מלאי נמוך";
    """,
}


# ============================================================
# Utility functions
# ============================================================
def format_db_value(value):
    if value is None:
        return ""
    if isinstance(value, Decimal):
        return str(value)
    return str(value)


def db_error_message(error):
    return str(error).strip()


# ============================================================
# Main application
# ============================================================
class RamiLeviApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("מערכת ניהול רשת - רמי לוי")
        self.geometry("1280x760")
        self.minsize(1120, 650)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.current_table_key = None
        self.current_tree = None
        self.current_tree_pk_map = {}
        self.current_search_var = tk.StringVar()
        self.current_rows_cache = []
        self.current_visible_cols = []

        self.configure_tree_style()
        self.create_layout()
        self.show_home()

    # --------------------------------------------------------
    # Basic UI
    # --------------------------------------------------------
    def configure_tree_style(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(
            "Treeview",
            font=("Arial", 11),
            rowheight=30,
            background="#FFFFFF",
            fieldbackground="#FFFFFF",
            foreground="#111111",
            borderwidth=0,
        )
        self.style.configure(
            "Treeview.Heading",
            font=("Arial", 12, "bold"),
            background=LIGHT_GREEN,
            foreground=DARK_GREEN,
            relief="flat",
        )
        self.style.map(
            "Treeview",
            background=[("selected", "#C8E6C9")],
            foreground=[("selected", "#000000")],
        )

    def create_layout(self):
        self.sidebar = ctk.CTkFrame(
            self,
            width=260,
            corner_radius=0,
            fg_color="#FFFFFF",
            border_width=1,
            border_color=BORDER,
        )
        self.sidebar.pack(side="right", fill="y")
        self.sidebar.pack_propagate(False)

        self.main_frame = ctk.CTkFrame(self, fg_color=BACKGROUND)
        self.main_frame.pack(side="left", fill="both", expand=True)

        self.create_sidebar()

    def create_sidebar(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(base_dir, "assets", "rami_levi_logo.png")

        if Image is not None and os.path.exists(logo_path):
            try:
                self.logo_image = ctk.CTkImage(
                    light_image=Image.open(logo_path),
                    dark_image=Image.open(logo_path),
                    size=(150, 88),
                )
                ctk.CTkLabel(self.sidebar, image=self.logo_image, text="").pack(pady=(24, 8))
            except Exception:
                self.sidebar_text_logo()
        else:
            self.sidebar_text_logo()

        ctk.CTkLabel(
            self.sidebar,
            text="מערכת ניהול רשת",
            font=("Arial", 13),
            text_color=TEXT_GRAY,
        ).pack(pady=(0, 25))

        self.sidebar_button("🏠  מסך ראשי", self.show_home)
        self.sidebar_button("🧾  ניהול כל הטבלאות", self.show_tables_screen)
        self.sidebar_button("📊  דוחות ושאילתות", self.show_reports_screen)
        self.sidebar_button("⚙️  פונקציות ופרוצדורות", self.show_actions_screen)

        self.test_button = ctk.CTkButton(
            self.sidebar,
            text="🔌 בדיקת חיבור ל-DB",
            font=FONT_BUTTON,
            fg_color=PRIMARY_GREEN,
            hover_color=DARK_GREEN,
            text_color="white",
            corner_radius=12,
            height=40,
            command=self.test_database_connection,
        )
        self.test_button.pack(side="bottom", pady=22, padx=15, fill="x")

    def sidebar_text_logo(self):
        ctk.CTkLabel(
            self.sidebar,
            text="רמי לוי",
            font=("Arial", 32, "bold"),
            text_color=PRIMARY_GREEN,
        ).pack(pady=(35, 0))
        ctk.CTkLabel(
            self.sidebar,
            text="שיווק השקמה",
            font=("Arial", 22, "bold"),
            text_color="#D32F2F",
        ).pack(pady=(0, 12))

    def sidebar_button(self, text, command):
        btn = ctk.CTkButton(
            self.sidebar,
            text=text,
            font=FONT_BUTTON,
            fg_color="transparent",
            hover_color=LIGHT_GREEN,
            text_color=TEXT_DARK,
            anchor="e",
            corner_radius=10,
            height=44,
            command=command,
        )
        btn.pack(pady=7, padx=15, fill="x")

    def clear_main(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def page_header(self, parent, title, subtitle):
        header = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=18, border_width=1, border_color=BORDER)
        header.pack(fill="x", padx=24, pady=(24, 14))

        ctk.CTkLabel(header, text=title, font=FONT_TITLE, text_color=PRIMARY_GREEN).pack(anchor="e", padx=25, pady=(18, 4))
        ctk.CTkLabel(header, text=subtitle, font=FONT_SUBTITLE, text_color=TEXT_GRAY, justify="right").pack(anchor="e", padx=25, pady=(0, 18))
        return header

    def create_table_widget(self, parent, columns, headings):
        card = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=18, border_width=1, border_color=BORDER)
        card.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        table_frame = tk.Frame(card, bg="white")
        table_frame.pack(fill="both", expand=True, padx=16, pady=16)

        tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        for col in columns:
            tree.heading(col, text=headings.get(col, col))
            tree.column(col, width=145, minwidth=90, anchor="center")

        scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar_x = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        scrollbar_y.pack(side="left", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        tree.pack(side="right", fill="both", expand=True)
        return tree

    # --------------------------------------------------------
    # Home
    # --------------------------------------------------------
    def show_home(self):
        self.clear_main()

        hero = ctk.CTkFrame(self.main_frame, fg_color=PRIMARY_GREEN, corner_radius=20)
        hero.pack(fill="x", padx=28, pady=(28, 18))

        ctk.CTkLabel(
            hero,
            text="מערכת ניהול רשת רמי לוי",
            font=("Arial", 32, "bold"),
            text_color="white",
        ).pack(anchor="e", padx=30, pady=(28, 6))

        ctk.CTkLabel(
            hero,
            text="ממשק גרפי לעבודה מול PostgreSQL: טבלאות, CRUD, דוחות, פונקציות ופרוצדורות",
            font=FONT_SUBTITLE,
            text_color="#E8F5E9",
        ).pack(anchor="e", padx=30, pady=(0, 28))

        cards = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        cards.pack(fill="both", expand=True, padx=28, pady=8)
        for i in range(2):
            cards.grid_columnconfigure(i, weight=1)
        for i in range(2):
            cards.grid_rowconfigure(i, weight=1)

        self.dashboard_card(cards, "🧾 ניהול טבלאות", "גישה לכל הטבלאות וביצוע שליפה, הוספה, עדכון ומחיקה.", self.show_tables_screen, 0, 1)
        self.dashboard_card(cards, "📊 דוחות", "הרצת שאילתות משלב ב' והצגת תוצאות בטבלה נוחה.", self.show_reports_screen, 0, 0)
        self.dashboard_card(cards, "⚙️ פעולות מתקדמות", "הפעלת פונקציות ופרוצדורות משלב ד' ישירות מהממשק.", self.show_actions_screen, 1, 1)
        self.dashboard_card(cards, "🔌 בדיקת מערכת", "בדיקת חיבור למסד הנתונים והכנה לצילומי מסך להגשה.", self.test_database_connection, 1, 0)

    def dashboard_card(self, parent, title, desc, command, row, col):
        card = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=18, border_width=1, border_color=BORDER)
        card.grid(row=row, column=col, sticky="nsew", padx=12, pady=12)

        ctk.CTkLabel(card, text=title, font=("Arial", 21, "bold"), text_color=PRIMARY_GREEN).pack(anchor="e", padx=24, pady=(24, 8))
        ctk.CTkLabel(card, text=desc, font=FONT_TEXT, text_color=TEXT_GRAY, wraplength=390, justify="right").pack(anchor="e", padx=24, pady=(0, 14))
        ctk.CTkButton(card, text="כניסה", font=FONT_BUTTON, fg_color=PRIMARY_GREEN, hover_color=DARK_GREEN, command=command).pack(anchor="e", padx=24, pady=(6, 24))

    # --------------------------------------------------------
    # Generic table CRUD
    # --------------------------------------------------------
    def show_tables_screen(self):
        self.clear_main()
        self.page_header(
            self.main_frame,
            "ניהול כל הטבלאות",
            "בחרו טבלה מהרשימה. הממשק מציג שמות במקום מפתחות זרים ומאפשר CRUD מלא מול בסיס הנתונים.",
        )

        controls = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        controls.pack(fill="x", padx=24, pady=(0, 12))

        labels = [cfg["label"] for cfg in TABLES.values()]
        self.table_label_to_key = {cfg["label"]: key for key, cfg in TABLES.items()}
        self.table_select = ctk.CTkComboBox(controls, values=labels, width=230, font=FONT_TEXT, command=self.on_table_selected)
        self.table_select.pack(side="right", padx=6)
        self.table_select.set(TABLES["PRODUCT"]["label"])

        ctk.CTkButton(controls, text="🔄 רענון", font=FONT_BUTTON, fg_color=PRIMARY_GREEN, hover_color=DARK_GREEN, command=self.reload_current_table).pack(side="right", padx=6)
        ctk.CTkButton(controls, text="➕ הוספה", font=FONT_BUTTON, fg_color=PRIMARY_GREEN, hover_color=DARK_GREEN, command=self.open_insert_window).pack(side="right", padx=6)
        ctk.CTkButton(controls, text="✏️ עדכון נבחר", font=FONT_BUTTON, fg_color=WARNING, hover_color="#F57F17", command=self.open_update_window).pack(side="right", padx=6)
        ctk.CTkButton(controls, text="🗑️ מחיקה נבחרת", font=FONT_BUTTON, fg_color=DANGER, hover_color="#8E0000", command=self.delete_selected_row).pack(side="right", padx=6)

        self.current_search_var.set("")
        search_entry = ctk.CTkEntry(controls, textvariable=self.current_search_var, placeholder_text="חיפוש בטבלה...", width=250, font=FONT_TEXT)
        search_entry.pack(side="left", padx=6)
        ctk.CTkButton(controls, text="חפש", width=80, font=FONT_BUTTON, fg_color="#455A64", hover_color="#263238", command=self.apply_search_filter).pack(side="left", padx=6)
        ctk.CTkButton(controls, text="נקה", width=80, font=FONT_BUTTON, fg_color="#78909C", hover_color="#546E7A", command=self.clear_search_filter).pack(side="left", padx=6)

        self.table_area = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.table_area.pack(fill="both", expand=True)

        self.current_table_key = "PRODUCT"
        self.render_table("PRODUCT")

    def on_table_selected(self, selected_label):
        key = self.table_label_to_key[selected_label]
        self.current_table_key = key
        self.current_search_var.set("")
        self.render_table(key)

    def reload_current_table(self):
        if self.current_table_key:
            self.render_table(self.current_table_key)

    def build_select_sql(self, table_key):
        cfg = TABLES[table_key]
        fks = cfg.get("fks", {})
        pk_cols = cfg["pk"]
        select_parts = []
        visible_cols = []
        headings = {}

        for pk_col in pk_cols:
            select_parts.append(f"t.{pk_col} AS __pk_{pk_col}")

        for col in cfg["columns"]:
            hide_single_pk = cfg.get("auto_pk") and len(pk_cols) == 1 and col in pk_cols
            if hide_single_pk:
                continue

            display_col = col
            if col in fks:
                display_col = f"{col}_display"
                fk = fks[col]
                join_clause = fk.get("join", "")
                label_sql = fk["label_sql"]
                subquery = f"(SELECT {label_sql} FROM {fk['sql']} r {join_clause} WHERE r.{fk['pk']} = t.{col} LIMIT 1)"
                select_parts.append(f"{subquery} AS {display_col}")
            else:
                select_parts.append(f"t.{col} AS {display_col}")

            visible_cols.append(display_col)
            headings[display_col] = cfg.get("headers", {}).get(col, col)

        sql = f"SELECT {', '.join(select_parts)} FROM {cfg['sql']} t ORDER BY "
        sql += ", ".join([f"t.{col}" for col in pk_cols])
        sql += " LIMIT 500;"
        return sql, visible_cols, headings

    def render_table(self, table_key):
        for widget in self.table_area.winfo_children():
            widget.destroy()

        cfg = TABLES[table_key]
        title = ctk.CTkLabel(self.table_area, text=f"טבלה: {cfg['label']}", font=("Arial", 18, "bold"), text_color=TEXT_DARK)
        title.pack(anchor="e", padx=28, pady=(0, 8))

        sql, visible_cols, headings = self.build_select_sql(table_key)
        self.current_visible_cols = visible_cols
        self.current_tree = self.create_table_widget(self.table_area, visible_cols, headings)
        self.load_table_data(table_key, sql, visible_cols)

    def load_table_data(self, table_key, sql, visible_cols):
        conn = get_db_connection()
        if not conn:
            messagebox.showerror("שגיאת חיבור", "לא ניתן להתחבר לבסיס הנתונים.")
            return

        cfg = TABLES[table_key]
        pk_cols = cfg["pk"]
        self.current_tree_pk_map = {}
        self.current_rows_cache = []

        try:
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]

            for index, row in enumerate(rows):
                row_dict = dict(zip(columns, row))
                pk_values = {pk: row_dict[f"__pk_{pk}".lower()] if f"__pk_{pk}".lower() in row_dict else row_dict.get(f"__pk_{pk}") for pk in pk_cols}

                # psycopg usually returns lowercase aliases, so normalize keys
                fixed_pk = {}
                for pk in pk_cols:
                    lower_alias = f"__pk_{pk}".lower()
                    exact_alias = f"__pk_{pk}"
                    fixed_pk[pk] = row_dict.get(exact_alias, row_dict.get(lower_alias))

                values = []
                for col in visible_cols:
                    values.append(format_db_value(row_dict.get(col, row_dict.get(col.lower()))))

                iid = f"row_{index}"
                self.current_tree.insert("", "end", iid=iid, values=values)
                self.current_tree_pk_map[iid] = fixed_pk
                self.current_rows_cache.append((iid, values, fixed_pk))

            cur.close()
        except Exception as error:
            messagebox.showerror("שגיאת שאילתה", f"נכשל בשליפת הנתונים:\n{db_error_message(error)}")
        finally:
            conn.close()

    def apply_search_filter(self):
        if not self.current_tree:
            return
        search = self.current_search_var.get().strip().lower()
        self.current_tree.delete(*self.current_tree.get_children())
        self.current_tree_pk_map = {}

        for iid, values, pk in self.current_rows_cache:
            joined = " ".join([str(v).lower() for v in values])
            if not search or search in joined:
                self.current_tree.insert("", "end", iid=iid, values=values)
                self.current_tree_pk_map[iid] = pk

    def clear_search_filter(self):
        self.current_search_var.set("")
        self.apply_search_filter()

    def get_selected_pk(self):
        if not self.current_tree:
            return None
        selected = self.current_tree.focus()
        if not selected:
            messagebox.showwarning("לא נבחרה רשומה", "בחרי רשומה מהטבלה ואז נסי שוב.")
            return None
        return self.current_tree_pk_map.get(selected)

    def get_lookup_options(self, fk):
        conn = get_db_connection()
        if not conn:
            messagebox.showerror("שגיאת חיבור", "לא ניתן להתחבר לבסיס הנתונים.")
            return [], {}

        options = []
        label_to_id = {}
        try:
            cur = conn.cursor()
            join_clause = fk.get("join", "")
            order_by = fk.get("order_by", "label_value")
            sql = f"""
                SELECT r.{fk['pk']} AS key_value, {fk['label_sql']} AS label_value
                FROM {fk['sql']} r {join_clause}
                ORDER BY {order_by}
                LIMIT 1000;
            """
            cur.execute(sql)
            for key_value, label_value in cur.fetchall():
                label = format_db_value(label_value)
                if label in label_to_id:
                    label = f"{label} [{key_value}]"
                options.append(label)
                label_to_id[label] = key_value
            cur.close()
        except Exception as error:
            messagebox.showerror("שגיאת טעינת רשימות", f"נכשל בטעינת ערכי בחירה:\n{db_error_message(error)}")
        finally:
            conn.close()
        return options, label_to_id

    def get_lookup_label_by_id(self, fk, key_value):
        if key_value is None:
            return ""
        options, label_to_id = self.get_lookup_options(fk)
        for label, value in label_to_id.items():
            if str(value) == str(key_value):
                return label
        return ""

    def get_next_id(self, cfg):
        pk = cfg["pk"][0]
        conn = get_db_connection()
        if not conn:
            raise RuntimeError("לא ניתן להתחבר לבסיס הנתונים")
        try:
            cur = conn.cursor()
            cur.execute(f"SELECT COALESCE(MAX({pk}), 0) + 1 FROM {cfg['sql']};")
            value = cur.fetchone()[0]
            cur.close()
            return value
        finally:
            conn.close()

    def open_insert_window(self):
        if not self.current_table_key:
            return
        self.open_form_window("insert")

    def open_update_window(self):
        if not self.current_table_key:
            return
        pk = self.get_selected_pk()
        if not pk:
            return
        self.open_form_window("update", pk)

    def open_form_window(self, mode, pk_values=None):
        cfg = TABLES[self.current_table_key]
        is_insert = mode == "insert"
        title = "הוספת רשומה" if is_insert else "עדכון רשומה"

        current_values = {}
        if not is_insert:
            current_values = self.fetch_raw_row(cfg, pk_values)
            if current_values is None:
                return

        win = ctk.CTkToplevel(self)
        win.title(f"{title} - {cfg['label']}")
        win.geometry("560x620")
        win.transient(self)
        win.grab_set()

        container = ctk.CTkScrollableFrame(win, fg_color=BACKGROUND)
        container.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(container, text=f"{title} - {cfg['label']}", font=("Arial", 22, "bold"), text_color=PRIMARY_GREEN).pack(anchor="e", pady=(8, 16))

        fields = {}
        lookup_maps = {}
        fks = cfg.get("fks", {})
        skip_insert = set(cfg.get("skip_insert", []))
        readonly_update = set(cfg.get("readonly_update", []))

        form_columns = []
        for col in cfg["columns"]:
            if is_insert and cfg.get("auto_pk") and len(cfg["pk"]) == 1 and col in cfg["pk"]:
                continue
            if is_insert and col in skip_insert:
                continue
            if not is_insert and cfg.get("auto_pk") and len(cfg["pk"]) == 1 and col in cfg["pk"]:
                continue
            form_columns.append(col)

        if not form_columns:
            ctk.CTkLabel(container, text="לטבלה זו אין שדות לעדכון. ניתן להוסיף או למחוק רשומות.", font=FONT_TEXT, text_color=TEXT_GRAY).pack(anchor="e", pady=10)

        for col in form_columns:
            label_text = cfg.get("headers", {}).get(col, col)
            row = ctk.CTkFrame(container, fg_color="transparent")
            row.pack(fill="x", pady=7)

            ctk.CTkLabel(row, text=label_text, font=FONT_TEXT, text_color=TEXT_DARK, width=140, anchor="e").pack(side="right", padx=6)

            current = current_values.get(col) if current_values else None

            if col in fks:
                options, label_to_id = self.get_lookup_options(fks[col])
                lookup_maps[col] = label_to_id
                combo = ctk.CTkComboBox(row, values=options, width=300, font=FONT_TEXT)
                combo.pack(side="right", padx=6)
                if not is_insert:
                    current_label = self.get_lookup_label_by_id(fks[col], current)
                    if current_label:
                        combo.set(current_label)
                elif options:
                    combo.set(options[0])
                fields[col] = combo
            elif not is_insert and col in readonly_update:
                entry = ctk.CTkEntry(row, width=300, font=FONT_TEXT)
                entry.pack(side="right", padx=6)
                entry.insert(0, format_db_value(current))
                entry.configure(state="disabled")
                fields[col] = entry
            else:
                entry = ctk.CTkEntry(row, width=300, font=FONT_TEXT)
                entry.pack(side="right", padx=6)
                if current is not None:
                    entry.insert(0, format_db_value(current))
                fields[col] = entry

        ctk.CTkLabel(
            container,
            text="בתאריכים השתמשי בפורמט YYYY-MM-DD. בשדה ריק יישלח NULL אם העמודה מאפשרת זאת.",
            font=FONT_SMALL,
            text_color=TEXT_GRAY,
            justify="right",
        ).pack(anchor="e", pady=(10, 5))

        submit_text = "שמירת רשומה חדשה" if is_insert else "שמירת עדכון"
        ctk.CTkButton(
            container,
            text=submit_text,
            font=FONT_BUTTON,
            fg_color=PRIMARY_GREEN,
            hover_color=DARK_GREEN,
            command=lambda: self.submit_form(win, cfg, mode, fields, lookup_maps, pk_values),
        ).pack(anchor="e", pady=18)

    def fetch_raw_row(self, cfg, pk_values):
        conn = get_db_connection()
        if not conn:
            messagebox.showerror("שגיאת חיבור", "לא ניתן להתחבר לבסיס הנתונים.")
            return None
        try:
            cur = conn.cursor()
            where_clause = " AND ".join([f"{pk} = %s" for pk in cfg["pk"]])
            sql = f"SELECT {', '.join(cfg['columns'])} FROM {cfg['sql']} WHERE {where_clause};"
            params = [pk_values[pk] for pk in cfg["pk"]]
            cur.execute(sql, params)
            row = cur.fetchone()
            cur.close()
            if not row:
                messagebox.showerror("שגיאה", "הרשומה לא נמצאה בבסיס הנתונים.")
                return None
            return dict(zip(cfg["columns"], row))
        except Exception as error:
            messagebox.showerror("שגיאת שליפה", f"לא ניתן להביא את הרשומה לעדכון:\n{db_error_message(error)}")
            return None
        finally:
            conn.close()

    def collect_form_values(self, fields, lookup_maps):
        values = {}
        for col, widget in fields.items():
            raw = widget.get().strip()
            if col in lookup_maps:
                values[col] = lookup_maps[col].get(raw)
            else:
                values[col] = None if raw == "" else raw
        return values

    def submit_form(self, win, cfg, mode, fields, lookup_maps, pk_values=None):
        values = self.collect_form_values(fields, lookup_maps)
        conn = get_db_connection()
        if not conn:
            messagebox.showerror("שגיאת חיבור", "לא ניתן להתחבר לבסיס הנתונים.")
            return

        try:
            cur = conn.cursor()

            if mode == "insert":
                insert_values = dict(values)
                if cfg.get("auto_pk") and len(cfg["pk"]) == 1:
                    insert_values[cfg["pk"][0]] = self.get_next_id(cfg)

                cols = list(insert_values.keys())
                placeholders = ", ".join(["%s"] * len(cols))
                sql = f"INSERT INTO {cfg['sql']} ({', '.join(cols)}) VALUES ({placeholders});"
                params = [insert_values[col] for col in cols]
                cur.execute(sql, params)
                conn.commit()
                messagebox.showinfo("הצלחה", "הרשומה נוספה בהצלחה.")

            else:
                update_values = dict(values)
                # Single auto primary keys stay hidden and are not updated.
                # Composite keys may be updated because those tables are associative and have no hidden numeric ID.
                set_cols = list(update_values.keys())
                if not set_cols:
                    messagebox.showwarning("אין שדות", "אין שדות שניתן לעדכן בטבלה זו.")
                    return

                set_clause = ", ".join([f"{col} = %s" for col in set_cols])
                where_clause = " AND ".join([f"{pk} = %s" for pk in cfg["pk"]])
                sql = f"UPDATE {cfg['sql']} SET {set_clause} WHERE {where_clause};"
                params = [update_values[col] for col in set_cols] + [pk_values[pk] for pk in cfg["pk"]]
                cur.execute(sql, params)
                conn.commit()
                messagebox.showinfo("הצלחה", "הרשומה עודכנה בהצלחה.")

            cur.close()
            win.destroy()
            self.reload_current_table()
        except Exception as error:
            conn.rollback()
            messagebox.showerror("שגיאת שמירה", f"הפעולה נכשלה:\n{db_error_message(error)}")
        finally:
            conn.close()

    def delete_selected_row(self):
        if not self.current_table_key:
            return
        pk_values = self.get_selected_pk()
        if not pk_values:
            return

        cfg = TABLES[self.current_table_key]
        confirm = messagebox.askyesno("אישור מחיקה", "האם למחוק את הרשומה שנבחרה?\nפעולה זו תשפיע על בסיס הנתונים.")
        if not confirm:
            return

        conn = get_db_connection()
        if not conn:
            messagebox.showerror("שגיאת חיבור", "לא ניתן להתחבר לבסיס הנתונים.")
            return

        try:
            cur = conn.cursor()
            where_clause = " AND ".join([f"{pk} = %s" for pk in cfg["pk"]])
            sql = f"DELETE FROM {cfg['sql']} WHERE {where_clause};"
            params = [pk_values[pk] for pk in cfg["pk"]]
            cur.execute(sql, params)
            conn.commit()
            cur.close()
            messagebox.showinfo("הצלחה", "הרשומה נמחקה בהצלחה.")
            self.reload_current_table()
        except Exception as error:
            conn.rollback()
            messagebox.showerror("שגיאת מחיקה", f"לא ניתן למחוק את הרשומה:\n{db_error_message(error)}")
        finally:
            conn.close()

    # --------------------------------------------------------
    # Reports
    # --------------------------------------------------------
    def show_reports_screen(self):
        self.clear_main()
        self.page_header(
            self.main_frame,
            "דוחות ושאילתות משלב ב'",
            "בחרו דוח להפעלה. התוצאות מוצגות בטבלה, עם שמות ברורים במקום מפתחות זרים.",
        )

        controls = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        controls.pack(fill="x", padx=24, pady=(0, 12))

        for report_name in REPORTS.keys():
            ctk.CTkButton(
                controls,
                text=report_name,
                font=FONT_BUTTON,
                fg_color=PRIMARY_GREEN,
                hover_color=DARK_GREEN,
                command=lambda name=report_name: self.run_report(name),
            ).pack(side="right", padx=5, pady=5)

        self.report_area = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.report_area.pack(fill="both", expand=True)
        self.run_report("מוצרים במלאי נמוך")

    def run_report(self, report_name):
        sql = REPORTS[report_name]
        self.display_query_result(self.report_area, report_name, sql)

    def display_query_result(self, area, title, sql, params=None, rows=None, columns=None):
        for widget in area.winfo_children():
            widget.destroy()

        ctk.CTkLabel(area, text=title, font=("Arial", 18, "bold"), text_color=TEXT_DARK).pack(anchor="e", padx=28, pady=(0, 8))

        if rows is None or columns is None:
            conn = get_db_connection()
            if not conn:
                messagebox.showerror("שגיאת חיבור", "לא ניתן להתחבר לבסיס הנתונים.")
                return
            try:
                cur = conn.cursor()
                cur.execute(sql, params or [])
                rows = cur.fetchall()
                columns = [desc[0] for desc in cur.description]
                cur.close()
            except Exception as error:
                messagebox.showerror("שגיאת דוח", f"נכשל בהרצת הדוח:\n{db_error_message(error)}")
                return
            finally:
                conn.close()

        headings = {col: col for col in columns}
        tree = self.create_table_widget(area, columns, headings)
        for row in rows:
            tree.insert("", "end", values=[format_db_value(v) for v in row])

    # --------------------------------------------------------
    # Functions and procedures
    # --------------------------------------------------------
    def show_actions_screen(self):
        self.clear_main()
        self.page_header(
            self.main_frame,
            "פונקציות ופרוצדורות משלב ד'",
            "כאן ניתן להפעיל פעולות PL/pgSQL ולהראות את ההשפעה שלהן על הטבלאות.",
        )

        content = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        left = ctk.CTkFrame(content, fg_color=CARD_BG, corner_radius=18, border_width=1, border_color=BORDER, width=360)
        left.pack(side="right", fill="y", padx=(0, 12))
        left.pack_propagate(False)

        self.action_result_area = ctk.CTkFrame(content, fg_color="transparent")
        self.action_result_area.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(left, text="פעולות זמינות", font=("Arial", 20, "bold"), text_color=PRIMARY_GREEN).pack(anchor="e", padx=18, pady=(20, 10))

        self.action_form_calculate_price(left)
        self.separator(left)
        self.action_form_complete_order(left)
        self.separator(left)
        self.action_form_discount_products(left)
        self.separator(left)
        self.action_form_active_discounts(left)

        self.show_action_message("בחרי פעולה מצד ימין כדי להציג כאן את התוצאה.")

    def separator(self, parent):
        ctk.CTkFrame(parent, height=1, fg_color=BORDER).pack(fill="x", padx=15, pady=12)

    def input_row(self, parent, label, placeholder=""):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=15, pady=4)
        ctk.CTkLabel(row, text=label, width=115, anchor="e", font=FONT_SMALL, text_color=TEXT_DARK).pack(side="right", padx=5)
        entry = ctk.CTkEntry(row, placeholder_text=placeholder, width=165, font=FONT_SMALL)
        entry.pack(side="right", padx=5)
        return entry

    def action_form_calculate_price(self, parent):
        ctk.CTkLabel(parent, text="חישוב מחיר הזמנה", font=("Arial", 15, "bold"), text_color=TEXT_DARK).pack(anchor="e", padx=18, pady=(4, 4))
        order_entry = self.input_row(parent, "מספר הזמנה", "לדוגמה 1")
        pct_entry = self.input_row(parent, "אחוז סיטונאי", "לדוגמה 65")
        ctk.CTkButton(parent, text="חשב מחיר", font=FONT_BUTTON, fg_color=PRIMARY_GREEN, hover_color=DARK_GREEN, command=lambda: self.run_calculate_price(order_entry, pct_entry)).pack(anchor="e", padx=20, pady=7)

    def action_form_complete_order(self, parent):
        ctk.CTkLabel(parent, text="השלמת הזמנה ועדכון מלאי", font=("Arial", 15, "bold"), text_color=TEXT_DARK).pack(anchor="e", padx=18, pady=(4, 4))
        order_entry = self.input_row(parent, "מספר הזמנה", "לדוגמה 2")
        ctk.CTkButton(parent, text="השלם הזמנה", font=FONT_BUTTON, fg_color=PRIMARY_GREEN, hover_color=DARK_GREEN, command=lambda: self.run_complete_order(order_entry)).pack(anchor="e", padx=20, pady=7)

    def action_form_discount_products(self, parent):
        ctk.CTkLabel(parent, text="הנחת מוצרים קרובים לתפוגה", font=("Arial", 15, "bold"), text_color=TEXT_DARK).pack(anchor="e", padx=18, pady=(4, 4))
        days_entry = self.input_row(parent, "מספר ימים", "30")
        pct_entry = self.input_row(parent, "אחוז הנחה", "10")
        ctk.CTkButton(parent, text="הפעל הנחה", font=FONT_BUTTON, fg_color=PRIMARY_GREEN, hover_color=DARK_GREEN, command=lambda: self.run_discount_near_expiration(days_entry, pct_entry)).pack(anchor="e", padx=20, pady=7)

    def action_form_active_discounts(self, parent):
        ctk.CTkLabel(parent, text="שליפת הנחות פעילות", font=("Arial", 15, "bold"), text_color=TEXT_DARK).pack(anchor="e", padx=18, pady=(4, 4))
        date_entry = self.input_row(parent, "תאריך בדיקה", "2026-05-28")
        ctk.CTkButton(parent, text="הצג הנחות", font=FONT_BUTTON, fg_color=PRIMARY_GREEN, hover_color=DARK_GREEN, command=lambda: self.run_active_discounts(date_entry)).pack(anchor="e", padx=20, pady=7)

    def show_action_message(self, text):
        for widget in self.action_result_area.winfo_children():
            widget.destroy()
        card = ctk.CTkFrame(self.action_result_area, fg_color=CARD_BG, corner_radius=18, border_width=1, border_color=BORDER)
        card.pack(fill="both", expand=True)
        ctk.CTkLabel(card, text=text, font=FONT_SUBTITLE, text_color=TEXT_GRAY, justify="right").pack(anchor="e", padx=28, pady=28)

    def run_calculate_price(self, order_entry, pct_entry):
        order_id = order_entry.get().strip()
        pct = pct_entry.get().strip()
        if not order_id or not pct:
            messagebox.showwarning("חסר קלט", "יש להזין מספר הזמנה ואחוז סיטונאי.")
            return

        conn = get_db_connection()
        if not conn:
            messagebox.showerror("שגיאת חיבור", "לא ניתן להתחבר לבסיס הנתונים.")
            return
        try:
            cur = conn.cursor()
            cur.execute("SELECT calculate_order_price(%s, %s);", (order_id, pct))
            price = cur.fetchone()[0]
            conn.commit()
            cur.close()
            self.display_query_result(
                self.action_result_area,
                f"מחיר הזמנה {order_id} חושב בהצלחה",
                "" ,
                rows=[(order_id, price)],
                columns=["מספר הזמנה", "מחיר מחושב"],
            )
        except Exception as error:
            conn.rollback()
            messagebox.showerror("שגיאת פעולה", f"הפונקציה נכשלה:\n{db_error_message(error)}")
        finally:
            conn.close()

    def run_complete_order(self, order_entry):
        order_id = order_entry.get().strip()
        if not order_id:
            messagebox.showwarning("חסר קלט", "יש להזין מספר הזמנה.")
            return

        conn = get_db_connection()
        if not conn:
            messagebox.showerror("שגיאת חיבור", "לא ניתן להתחבר לבסיס הנתונים.")
            return
        try:
            cur = conn.cursor()
            cur.execute("CALL complete_order_and_update_stock(%s);", (order_id,))
            conn.commit()
            cur.close()
            self.show_order_status_after_action(order_id, "ההזמנה הושלמה והמלאי עודכן")
        except Exception as error:
            conn.rollback()
            messagebox.showerror("שגיאת פעולה", f"הפרוצדורה נכשלה:\n{db_error_message(error)}")
        finally:
            conn.close()

    def run_discount_near_expiration(self, days_entry, pct_entry):
        days = days_entry.get().strip()
        pct = pct_entry.get().strip()
        if not days or not pct:
            messagebox.showwarning("חסר קלט", "יש להזין מספר ימים ואחוז הנחה.")
            return

        conn = get_db_connection()
        if not conn:
            messagebox.showerror("שגיאת חיבור", "לא ניתן להתחבר לבסיס הנתונים.")
            return
        try:
            cur = conn.cursor()
            cur.execute("CALL discount_near_expiration_products(%s, %s);", (days, pct))
            conn.commit()
            cur.close()
            query = """
                SELECT ProductName AS "מוצר", Price AS "מחיר", ExpirationDate AS "תאריך תפוגה"
                FROM PRODUCT
                WHERE ExpirationDate::DATE BETWEEN CURRENT_DATE AND CURRENT_DATE + %s::INT
                ORDER BY ExpirationDate, ProductName;
            """
            self.display_query_result(self.action_result_area, "מוצרים בטווח התפוגה לאחר הפעלת הפרוצדורה", query, params=(days,))
        except Exception as error:
            conn.rollback()
            messagebox.showerror("שגיאת פעולה", f"הפרוצדורה נכשלה:\n{db_error_message(error)}")
        finally:
            conn.close()

    def run_active_discounts(self, date_entry):
        check_date = date_entry.get().strip()
        if not check_date:
            messagebox.showwarning("חסר קלט", "יש להזין תאריך בפורמט YYYY-MM-DD.")
            return

        conn = get_db_connection()
        if not conn:
            messagebox.showerror("שגיאת חיבור", "לא ניתן להתחבר לבסיס הנתונים.")
            return
        try:
            cur = conn.cursor()
            cur.execute("BEGIN;")
            cur.execute("SELECT get_active_discounts(%s);", (check_date,))
            cur.execute('FETCH ALL IN "discount_result_cursor";')
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            cur.execute("COMMIT;")
            cur.close()
            self.display_query_result(self.action_result_area, f"הנחות פעילות בתאריך {check_date}", "", rows=rows, columns=columns)
        except Exception as error:
            try:
                conn.rollback()
            except Exception:
                pass
            messagebox.showerror("שגיאת פעולה", f"הפונקציה נכשלה:\n{db_error_message(error)}")
        finally:
            conn.close()

    def show_order_status_after_action(self, order_id, title):
        sql = """
            SELECT
                o.OrderId AS "הזמנה",
                o.Status AS "סטטוס",
                o.Price AS "מחיר",
                s.StoreName AS "סניף",
                o.OrderDate AS "תאריך הזמנה",
                o.DeliveryDate AS "תאריך משלוח"
            FROM "ORDER" o
            JOIN STORE s ON o.StoreID = s.StoreID
            WHERE o.OrderId = %s;
        """
        self.display_query_result(self.action_result_area, title, sql, params=(order_id,))

    # --------------------------------------------------------
    # DB test
    # --------------------------------------------------------
    def test_database_connection(self):
        conn = get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT version();")
                version = cur.fetchone()[0]
                cur.close()
                messagebox.showinfo("סטטוס חיבור", f"החיבור ל-PostgreSQL הצליח.\n\n{version}")
            except Exception:
                messagebox.showinfo("סטטוס חיבור", "החיבור ל-PostgreSQL הצליח.")
            finally:
                conn.close()
        else:
            messagebox.showerror("סטטוס חיבור", "החיבור נכשל. ודאי ש-Docker Desktop דלוק ושהנתונים בקובץ .env נכונים.")


if __name__ == "__main__":
    app = RamiLeviApp()
    app.mainloop()
