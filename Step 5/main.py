import os
import tkinter as tk
from tkinter import messagebox, ttk

import customtkinter as ctk
from PIL import Image

from db_connection import get_db_connection


# ---------- App Theme ----------
PRIMARY_GREEN = "#2E7D32"
DARK_GREEN = "#1B5E20"
LIGHT_GREEN = "#E8F5E9"
BACKGROUND = "#F7F8FA"
CARD_BG = "#FFFFFF"
TEXT_DARK = "#263238"
TEXT_GRAY = "#607D8B"
DANGER = "#C62828"

FONT_TITLE = ("Arial", 26, "bold")
FONT_SUBTITLE = ("Arial", 15)
FONT_BUTTON = ("Arial", 14, "bold")
FONT_TEXT = ("Arial", 13)


class RamiLeviApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ---------- Window Settings ----------
        self.title("מערכת ניהול רשת - רמי לוי")
        self.geometry("1100x650")
        self.minsize(1000, 600)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # ---------- Table Style ----------
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(
            "Treeview",
            font=("Arial", 11),
            rowheight=28,
            background="#ffffff",
            fieldbackground="#ffffff",
            foreground="#000000",
            borderwidth=0
        )
        self.style.configure(
            "Treeview.Heading",
            font=("Arial", 12, "bold"),
            background="#E8F5E9",
            foreground="#1B5E20"
        )
        self.style.map(
            "Treeview",
            background=[("selected", "#C8E6C9")],
            foreground=[("selected", "#000000")]
        )

        # ---------- Sidebar ----------
        self.sidebar_frame = ctk.CTkFrame(
            self,
            width=240,
            corner_radius=0,
            fg_color="#FFFFFF",
            border_color="#E0E0E0",
            border_width=1
        )
        self.sidebar_frame.pack(side="right", fill="y")
        self.sidebar_frame.pack_propagate(False)

        self.create_sidebar()

        # ---------- Main Frame ----------
        self.main_frame = ctk.CTkFrame(self, fg_color=BACKGROUND)
        self.main_frame.pack(side="left", fill="both", expand=True)

        self.show_welcome_screen()

    # -------------------------------------------------------------
    # Sidebar
    # -------------------------------------------------------------
    def create_sidebar(self):
        # Logo
        base_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(base_dir, "assets", "rami_levi_logo.png")

        if os.path.exists(logo_path):
            try:
                self.logo_image = ctk.CTkImage(
                    light_image=Image.open(logo_path),
                    dark_image=Image.open(logo_path),
                    size=(160, 90)
                )

                self.logo_label = ctk.CTkLabel(
                    self.sidebar_frame,
                    image=self.logo_image,
                    text=""
                )
                self.logo_label.pack(pady=(25, 10))

            except Exception:
                self.logo_label = ctk.CTkLabel(
                    self.sidebar_frame,
                    text="רמי לוי",
                    font=("Arial", 28, "bold"),
                    text_color=PRIMARY_GREEN
                )
                self.logo_label.pack(pady=(35, 20))
        else:
            self.logo_label = ctk.CTkLabel(
                self.sidebar_frame,
                text="רמי לוי",
                font=("Arial", 28, "bold"),
                text_color=PRIMARY_GREEN
            )
            self.logo_label.pack(pady=(35, 20))

        subtitle = ctk.CTkLabel(
            self.sidebar_frame,
            text="מערכת ניהול רשת",
            font=("Arial", 13),
            text_color=TEXT_GRAY
        )
        subtitle.pack(pady=(0, 25))

        self.create_sidebar_button("🛒  מוצרים ומלאי", "products")
        self.create_sidebar_button("👥  סניפים ועובדים", "employees")
        self.create_sidebar_button("🚚  הזמנות ומשלוחים", "orders")
        self.create_sidebar_button("📊  דוחות ופרוצדורות", "reports")

        self.btn_test_db = ctk.CTkButton(
            self.sidebar_frame,
            text="🔌 בדיקת חיבור ל-DB",
            font=FONT_BUTTON,
            fg_color=PRIMARY_GREEN,
            text_color="white",
            hover_color=DARK_GREEN,
            corner_radius=12,
            command=self.test_database_connection
        )
        self.btn_test_db.pack(side="bottom", pady=25, padx=15, fill="x")

    def create_sidebar_button(self, text, page_name):
        button = ctk.CTkButton(
            self.sidebar_frame,
            text=text,
            font=FONT_BUTTON,
            fg_color="transparent",
            text_color=TEXT_DARK,
            hover_color=LIGHT_GREEN,
            anchor="e",
            corner_radius=10,
            height=42,
            command=lambda: self.show_page(page_name)
        )
        button.pack(pady=7, padx=15, fill="x")

    # -------------------------------------------------------------
    # General Helpers
    # -------------------------------------------------------------
    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_page(self, page_name):
        self.clear_main_frame()

        if page_name == "products":
            self.display_products_table()
        elif page_name == "employees":
            self.show_placeholder_page(
                "סניפים ועובדים",
                "כאן נבנה בהמשך מסך לניהול עובדים, סניפים ונתוני כוח אדם."
            )
        elif page_name == "orders":
            self.show_placeholder_page(
                "הזמנות ומשלוחים",
                "כאן נבנה בהמשך מסך לניהול הזמנות, משאיות וחברות משלוח."
            )
        elif page_name == "reports":
            self.show_placeholder_page(
                "דוחות ופרוצדורות",
                "כאן נבנה בהמשך מסך להרצת שאילתות משלב ב' ופונקציות/פרוצדורות משלב ד'."
            )

    # -------------------------------------------------------------
    # Welcome / Dashboard Screen
    # -------------------------------------------------------------
    def show_welcome_screen(self):
        self.clear_main_frame()

        header = ctk.CTkFrame(
            self.main_frame,
            fg_color=PRIMARY_GREEN,
            corner_radius=20
        )
        header.pack(fill="x", padx=30, pady=(30, 15))

        title = ctk.CTkLabel(
            header,
            text="מערכת ניהול רשת רמי לוי",
            font=("Arial", 30, "bold"),
            text_color="white"
        )
        title.pack(anchor="e", padx=30, pady=(25, 5))

        subtitle = ctk.CTkLabel(
            header,
            text="ניהול מוצרים, מלאי, עובדים, הזמנות ודוחות מתוך בסיס הנתונים",
            font=FONT_SUBTITLE,
            text_color="#E8F5E9"
        )
        subtitle.pack(anchor="e", padx=30, pady=(0, 25))

        cards_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        cards_frame.pack(fill="both", expand=True, padx=30, pady=10)

        cards_frame.grid_columnconfigure(0, weight=1)
        cards_frame.grid_columnconfigure(1, weight=1)
        cards_frame.grid_rowconfigure(0, weight=1)
        cards_frame.grid_rowconfigure(1, weight=1)

        self.create_dashboard_card(
            cards_frame,
            "🛒 מוצרים ומלאי",
            "צפייה במוצרים, קטגוריות ומלאי. בהמשך נוסיף הוספה, עדכון ומחיקה.",
            "products",
            0,
            1
        )

        self.create_dashboard_card(
            cards_frame,
            "👥 סניפים ועובדים",
            "ניהול עובדים, סניפים ופרטי העסקה בצורה נוחה וברורה.",
            "employees",
            0,
            0
        )

        self.create_dashboard_card(
            cards_frame,
            "🚚 הזמנות ומשלוחים",
            "ניהול הזמנות, חברות משלוח, משאיות וסטטוסי הזמנה.",
            "orders",
            1,
            1
        )

        self.create_dashboard_card(
            cards_frame,
            "📊 דוחות ופעולות",
            "הרצת שאילתות, פונקציות ופרוצדורות מתוך הממשק הגרפי.",
            "reports",
            1,
            0
        )

    def create_dashboard_card(self, parent, title, description, page_name, row, col):
        card = ctk.CTkFrame(
            parent,
            fg_color=CARD_BG,
            corner_radius=18,
            border_width=1,
            border_color="#E0E0E0"
        )
        card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 20, "bold"),
            text_color=PRIMARY_GREEN
        )
        title_label.pack(anchor="e", padx=25, pady=(25, 8))

        desc_label = ctk.CTkLabel(
            card,
            text=description,
            font=FONT_TEXT,
            text_color=TEXT_GRAY,
            wraplength=340,
            justify="right"
        )
        desc_label.pack(anchor="e", padx=25, pady=8)

        button = ctk.CTkButton(
            card,
            text="כניסה למסך",
            font=FONT_BUTTON,
            fg_color=PRIMARY_GREEN,
            hover_color=DARK_GREEN,
            text_color="white",
            corner_radius=12,
            command=lambda: self.show_page(page_name)
        )
        button.pack(anchor="e", padx=25, pady=(15, 25))

    # -------------------------------------------------------------
    # Placeholder Pages
    # -------------------------------------------------------------
    def show_placeholder_page(self, title, description):
        container = ctk.CTkFrame(
            self.main_frame,
            fg_color=CARD_BG,
            corner_radius=18,
            border_width=1,
            border_color="#E0E0E0"
        )
        container.pack(fill="both", expand=True, padx=30, pady=30)

        title_label = ctk.CTkLabel(
            container,
            text=title,
            font=FONT_TITLE,
            text_color=PRIMARY_GREEN
        )
        title_label.pack(anchor="e", padx=30, pady=(35, 10))

        desc_label = ctk.CTkLabel(
            container,
            text=description,
            font=FONT_SUBTITLE,
            text_color=TEXT_GRAY,
            justify="right"
        )
        desc_label.pack(anchor="e", padx=30, pady=10)

        back_button = ctk.CTkButton(
            container,
            text="חזרה למסך הראשי",
            font=FONT_BUTTON,
            fg_color=PRIMARY_GREEN,
            hover_color=DARK_GREEN,
            command=self.show_welcome_screen
        )
        back_button.pack(anchor="e", padx=30, pady=25)

    # -------------------------------------------------------------
    # Products Page
    # -------------------------------------------------------------
    def display_products_table(self):
        page_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        page_container.pack(fill="both", expand=True, padx=25, pady=25)

        header = ctk.CTkFrame(
            page_container,
            fg_color=CARD_BG,
            corner_radius=18,
            border_width=1,
            border_color="#E0E0E0"
        )
        header.pack(fill="x", pady=(0, 15))

        title_lbl = ctk.CTkLabel(
            header,
            text="ניהול מוצרים וקטגוריות",
            font=FONT_TITLE,
            text_color=PRIMARY_GREEN
        )
        title_lbl.pack(anchor="e", padx=25, pady=(18, 5))

        subtitle_lbl = ctk.CTkLabel(
            header,
            text="הנתונים נשלפים ישירות מתוך PostgreSQL. מוצג שם קטגוריה במקום CategoryID.",
            font=FONT_SUBTITLE,
            text_color=TEXT_GRAY
        )
        subtitle_lbl.pack(anchor="e", padx=25, pady=(0, 18))

        # Buttons row
        buttons_frame = ctk.CTkFrame(page_container, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(0, 15))

        refresh_btn = ctk.CTkButton(
            buttons_frame,
            text="🔄 רענון נתונים",
            font=FONT_BUTTON,
            fg_color=PRIMARY_GREEN,
            hover_color=DARK_GREEN,
            command=self.display_products_table
        )
        refresh_btn.pack(side="right", padx=5)

        add_btn = ctk.CTkButton(
            buttons_frame,
            text="➕ הוספת מוצר",
            font=FONT_BUTTON,
            fg_color=PRIMARY_GREEN,
            hover_color=DARK_GREEN,
            command=lambda: messagebox.showinfo("בקרוב", "כאן נוסיף Insert למוצר.")
        )
        add_btn.pack(side="right", padx=5)

        update_btn = ctk.CTkButton(
            buttons_frame,
            text="✏️ עדכון מוצר נבחר",
            font=FONT_BUTTON,
            fg_color="#F9A825",
            hover_color="#F57F17",
            command=lambda: messagebox.showinfo("בקרוב", "כאן נוסיף Update למוצר נבחר.")
        )
        update_btn.pack(side="right", padx=5)

        delete_btn = ctk.CTkButton(
            buttons_frame,
            text="🗑️ מחיקת מוצר נבחר",
            font=FONT_BUTTON,
            fg_color=DANGER,
            hover_color="#8E0000",
            command=lambda: messagebox.showinfo("בקרוב", "כאן נוסיף Delete למוצר נבחר.")
        )
        delete_btn.pack(side="right", padx=5)

        # Table card
        table_card = ctk.CTkFrame(
            page_container,
            fg_color=CARD_BG,
            corner_radius=18,
            border_width=1,
            border_color="#E0E0E0"
        )
        table_card.pack(fill="both", expand=True)

        table_frame = tk.Frame(table_card, bg="white")
        table_frame.pack(pady=18, padx=18, fill="both", expand=True)

        # לא מציגים ProductID למשתמש
        columns = ("product_name", "price", "brand", "expiration", "category_name")

        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        tree.heading("product_name", text="שם מוצר")
        tree.heading("price", text="מחיר")
        tree.heading("brand", text="מותג/יצרן")
        tree.heading("expiration", text="תאריך תפוגה")
        tree.heading("category_name", text="קטגוריה")

        tree.column("product_name", width=170, anchor="center")
        tree.column("price", width=100, anchor="center")
        tree.column("brand", width=130, anchor="center")
        tree.column("expiration", width=130, anchor="center")
        tree.column("category_name", width=220, anchor="center")

        scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar_x = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)

        tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        scrollbar_y.pack(side="left", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        tree.pack(side="right", fill="both", expand=True)

        self.load_products_data(tree)

    def load_products_data(self, tree):
        conn = get_db_connection()

        if not conn:
            messagebox.showerror("שגיאת חיבור", "לא ניתן להתחבר לבסיס הנתונים.")
            return

        cursor = conn.cursor()

        try:
            query = """
                SELECT
                    p.ProductID,
                    p.ProductName,
                    p.Price,
                    p.Brand,
                    p.ExpirationDate,
                    c.CategoryName
                FROM PRODUCT p
                JOIN CATEGORY c ON p.CategoryID = c.CategoryID
                ORDER BY p.ProductID ASC
                LIMIT 50;
            """

            cursor.execute(query)
            rows = cursor.fetchall()

            for row in rows:
                product_id = row[0]
                visible_values = row[1:]
                tree.insert("", "end", iid=str(product_id), values=visible_values)

        except Exception as e:
            messagebox.showerror("שגיאת שאילתה", f"נכשל בשליפת נתונים:\n{e}")

        finally:
            cursor.close()
            conn.close()

    # -------------------------------------------------------------
    # DB Test
    # -------------------------------------------------------------
    def test_database_connection(self):
        conn = get_db_connection()

        if conn:
            messagebox.showinfo(
                "סטטוס חיבור",
                "החיבור ל-PostgreSQL הצליח!"
            )
            conn.close()
        else:
            messagebox.showerror(
                "סטטוס חיבור",
                "החיבור נכשל.\nודאי ש-Docker Desktop דלוק ושהנתונים בקובץ .env נכונים."
            )


if __name__ == "__main__":
    app = RamiLeviApp()
    app.mainloop()