import customtkinter as ctk
from tkinter import messagebox, ttk
import tkinter as tk
from db_connection import get_db_connection

class RamiLeviApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # הגדרות חלון ראשי
        self.title("מערכת ניהול רשת - רמי לוי")
        self.geometry("1000x600")
        
        # --- שינוי למצב בהיר וצבעים נעימים ---
        ctk.set_appearance_mode("light")  
        ctk.set_default_color_theme("blue") 

        # הגדרת סגנון לטבלאות המובנות של tkinter (כי ל-customtkinter אין טבלה מובנית)
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Treeview", font=("Arial", 11), rowheight=25, background="#ffffff", fieldbackground="#ffffff")
        self.style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#e1f5fe", foreground="#000000")

        # -------------------------------------------------------------
        # 1. תפריט צד (Sidebar Frame)
        # -------------------------------------------------------------
        # צבע רקע ירוק-זית עדין/אפרפר שמתאים לעין
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#f5f5f5", border_color="#e0e0e0", border_width=1)
        self.sidebar_frame.pack(side="right", fill="y")
        self.sidebar_frame.pack_propagate(False)

        # כותרת תפריט הצד
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="רמי לוי", font=("Arial", 26, "bold"), text_color="#2e7d32")
        self.logo_label.pack(pady=30)

        # כפתורי ניווט בתפריט הצד (טקסט כהה על רקע בהיר)
        self.btn_products = ctk.CTkButton(self.sidebar_frame, text="🛒 ניהול מוצרים ומלאי", fg_color="transparent", text_color="#333333", hover_color="#e0e0e0", anchor="e", command=lambda: self.show_page("products"))
        self.btn_products.pack(pady=10, padx=10, fill="x")

        self.btn_employees = ctk.CTkButton(self.sidebar_frame, text="👥 עובדים וסניפים", fg_color="transparent", text_color="#333333", hover_color="#e0e0e0", anchor="e", command=lambda: self.show_page("employees"))
        self.btn_employees.pack(pady=10, padx=10, fill="x")

        self.btn_orders = ctk.CTkButton(self.sidebar_frame, text="🚚 הזמנות ומשלוחים", fg_color="transparent", text_color="#333333", hover_color="#e0e0e0", anchor="e", command=lambda: self.show_page("orders"))
        self.btn_orders.pack(pady=10, padx=10, fill="x")

        self.btn_reports = ctk.CTkButton(self.sidebar_frame, text="📊 דוחות ופרוצדורות", fg_color="transparent", text_color="#333333", hover_color="#e0e0e0", anchor="e", command=lambda: self.show_page("reports"))
        self.btn_reports.pack(pady=10, padx=10, fill="x")

        # כפתור בדיקת חיבור בתחתית התפריט
        self.btn_test_db = ctk.CTkButton(self.sidebar_frame, text="🔌 בדיקת חיבור ל-DB", fg_color="#2e7d32", text_color="white", hover_color="#1b5e20", command=self.test_database_connection)
        self.btn_test_db.pack(side="bottom", pady=20, padx=10, fill="x")

        # -------------------------------------------------------------
        # 2. האזור המרכזי הדינמי (Main Content Area)
        # -------------------------------------------------------------
        self.main_frame = ctk.CTkFrame(self, fg_color="#fafafa")
        self.main_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        # הצגת מסך ברוכים הבאים ראשוני
        self.show_welcome_screen()

    def show_welcome_screen(self):
        self.clear_main_frame()
        welcome_label = ctk.CTkLabel(self.main_frame, text="ברוכים הבאים למערכת ניהנול הרשת", font=("Arial", 22, "bold"), text_color="#2e7d32")
        welcome_label.pack(pady=40)
        instructions = ctk.CTkLabel(self.main_frame, text="אנא בחרי תפריט מצד ימין כדי להתחיל בניהול הטבלאות.\nלחצי על ניהול מוצרים כדי לראות נתונים חיים מהדוקר!", font=("Arial", 14), text_color="#555555")
        instructions.pack(pady=10)

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_page(self, page_name):
        self.clear_main_frame()
        
        if page_name == "products":
            self.display_products_table()
        else:
            # שלד זמני לשאר העמודים
            title_mapping = {
                "employees": "עמוד ניהול עובדים וסניפים",
                "orders": "עמוד ניהול הזמנות, משאיות וחברות משלוח",
                "reports": "עמוד הרצת שאילתות (שלב ב') ופרוצדורות (שלב ד')"
            }
            lbl = ctk.CTkLabel(self.main_frame, text=title_mapping.get(page_name), font=("Arial", 20, "bold"), text_color="#333333")
            lbl.pack(pady=30)

    def display_products_table(self):
        """שליפת נתונים אמיתית מהדוקר והצגתם בטבלה ללא קוד קטגוריה יבש"""
        title_lbl = ctk.CTkLabel(self.main_frame, text="ניהול מוצרים וקטגוריות", font=("Arial", 20, "bold"), text_color="#2e7d32")
        title_lbl.pack(pady=10)

        # יצירת קונטיינר לטבלה ולפס גלילה
        table_frame = tk.Frame(self.main_frame)
        table_frame.pack(pady=15, padx=10, fill="both", expand=True)

        # הגדרת עמודות הטבלה (שימי לב: מציגים שם קטגוריה ולא קוד!)
        columns = ("product_id", "product_name", "price", "brand", "expiration", "category_name")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        
        # כותרות העמודות בעברית (מיושר לימין)
        tree.heading("product_id", text="קוד מוצר")
        tree.heading("product_name", text="שם מוצר")
        tree.heading("price", text="מחיר")
        tree.heading("brand", text="מותג/יצרן")
        tree.heading("expiration", text="תאריך תפוגה")
        tree.heading("category_name", text="קטגוריה")

        # עיצוב רוחב עמודות ויישור טקסט למרכז/ימין
        for col in columns:
            tree.column(col, width=120, anchor="center")

        # הוספת פס גלילה אנכי
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="left", fill="y") # פס גלילה משמאל בעברית
        tree.pack(side="right", fill="both", expand=True)

        # --- שליפת הנתונים האמיתית מה-DB ---
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                # שאילתת JOIN שמחליפה את ה-CategoryID בשם הקטגוריה האמיתי!
                query = """
                    SELECT p.ProductID, p.ProductName, p.Price, p.Brand, p.ExpirationDate, c.CategoryName
                    FROM PRODUCT p
                    JOIN CATEGORY c ON p.CategoryID = c.CategoryID
                    ORDER BY p.ProductID ASC
                    LIMIT 50; -- מגבילים ל-50 בשביל התצוגה הראשונית
                """
                cursor.execute(query)
                rows = cursor.fetchall()
                
                # הכנסת הנתונים לתוך הטבלה הגרפית
                for row in rows:
                    tree.insert("", "end", values=row)
                    
            except Exception as e:
                messagebox.showerror("שגיאת שאילתה", f"נכשל בשליפת נתונים: {e}")
            finally:
                cursor.close()
                conn.close()
        else:
            messagebox.showerror("שגיאת חיבור", "לא ניתן להתחבר לדוקר לשליפת המוצרים.")

    def test_database_connection(self):
        conn = get_db_connection()
        if conn:
            messagebox.showinfo("סטטוס חיבור", "החיבור ל-PostgreSQL בתוך ה-Docker הצליח ב-100%!")
            conn.close()
        else:
            messagebox.showerror("סטטוס חיבור", "החיבור נכשל.\nודאי ש-Docker Desktop דלוק.")

if __name__ == "__main__":
    app = RamiLeviApp()
    app.mainloop()