import customtkinter as ctk
import sys
import os
from PIL import Image
from tkinter import ttk, Canvas

# הוספת התיקייה הנוכחית לנתיב למניעת בעיות ייבוא
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dashboard_screen import show_dashboard_view
from stores_screen import show_stores_view
from employees_screen import show_employees_view
from warehouses_screen import show_warehouses_view 
from inventory_screen import show_inventory_view
from suppliers_screen import show_suppliers_view
from orders_screen import show_orders_view
from discounts_screen import show_discounts_view

class RamiLeviApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # -------------------------------------------------------------
        # הגדרות חלון ממוקסם ויציב
        # -------------------------------------------------------------
        self.title("רמי לוי - לוח בקרה ניהולי")
        self.geometry("1366x768")
        
        try:
            self.state('zoomed')
        except:
            pass
            
        ctk.set_appearance_mode("light")  
        ctk.set_default_color_theme("blue")

        # -------------------------------------------------------------
        # אתחול וייצוב גלובלי של מנוע הטבלאות (ttk.Style)
        # -------------------------------------------------------------
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("Custom.Treeview",
                        background="#FFFFFF",
                        foreground="#111827",
                        rowheight=40, 
                        fieldbackground="#FFFFFF",
                        font=("Segoe UI", 12),
                        borderwidth=0,
                        relief="flat")
        
        style.configure("Custom.Treeview.Heading",
                        background="#F9FAFB",
                        foreground="#4B5563",
                        font=("Segoe UI", 13, "bold"),
                        relief="flat",
                        borderwidth=0)
        
        style.map("Custom.Treeview", background=[('selected', '#E0F2FE')], foreground=[('selected', '#0369A1')])

        # -------------------------------------------------------------
        # 1. תפריט צד ימני (Right Sidebar)
        # -------------------------------------------------------------
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color="#030712")
        self.sidebar_frame.pack(side="right", fill="y")
        self.sidebar_frame.pack_propagate(False)

        # טעינת לוגו
        self.logo_path = os.path.join(os.path.dirname(__file__), "assets", "rami_levi_logo.png")
        if os.path.exists(self.logo_path):
            logo_img = Image.open(self.logo_path)
            self.ctk_logo = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(120, 50))
            self.logo_label = ctk.CTkLabel(self.sidebar_frame, image=self.ctk_logo, text="")
            self.logo_label.pack(pady=(35, 5))
        else:
            self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="רמי לוי", font=("Segoe UI", 28, "bold"), text_color="#10B981")
            self.logo_label.pack(pady=(35, 5))

        self.sub_logo = ctk.CTkLabel(self.sidebar_frame, text="ניהול מטה רשתי", font=("Segoe UI", 12), text_color="#6B7280")
        self.sub_logo.pack(pady=(0, 35))

        self.buttons = {}
        
        # כפתורי הניווט קוראים עכשיו לפונקציית מעבר מהירה ומאובטחת
        self.create_sidebar_button("dashboard", "📊   לוח בקרה רשתי", lambda: self.switch_view("dashboard"))
        self.create_sidebar_button("stores", "🏪   ניהול סניפים", lambda: self.switch_view("stores"))
        self.create_sidebar_button("employees", "👥   ניהול עובדים", lambda: self.switch_view("employees"))
        self.create_sidebar_button("warehouses", "🏭   מחסנים לוגיסטיים", lambda: self.switch_view("warehouses"))
        self.create_sidebar_button("inventory", "📦   מלאי ומוצרים", lambda: self.switch_view("inventory"))
        self.create_sidebar_button("suppliers", "🚚   ספקים ורכש", lambda: self.switch_view("suppliers"))
        self.create_sidebar_button("orders", "🛒   הזמנות הפצה", lambda: self.switch_view("orders"))
        self.create_sidebar_button("discounts", "🏷️   מבצעים והנחות", lambda: self.switch_view("discounts"))

        # פרופיל משתמש
        self.user_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="#111827", corner_radius=14, height=65)
        self.user_frame.pack(side="bottom", pady=25, padx=15, fill="x")
        self.user_frame.pack_propagate(False)
        
        self.user_title = ctk.CTkLabel(self.user_frame, text="משה כהן", font=("Segoe UI", 14, "bold"), text_color="#F8FAFC", anchor="e")
        self.user_title.pack(pady=(10, 0), padx=18, fill="x")
        self.user_role = ctk.CTkLabel(self.user_frame, text="מנהל תפעול רשתי", font=("Segoe UI", 11), text_color="#94A3B8", anchor="e")
        self.user_role.pack(padx=18, fill="x")

        # -------------------------------------------------------------
        # 2. מנגנון גלילה חכם ומותנה
        # -------------------------------------------------------------
        self.left_container = ctk.CTkFrame(self, fg_color="#F3F4F6", corner_radius=0)
        self.left_container.pack(side="left", fill="both", expand=True)

        self.canvas = Canvas(self.left_container, bg="#F3F4F6", highlightthickness=0)
        self.scrollbar = ctk.CTkScrollbar(self.left_container, orientation="vertical", command=self.canvas.yview)
        
        # המכולה הראשית שמחזיקה את כל המסכים
        self.views_container = ctk.CTkFrame(self.canvas, fg_color="#F3F4F6", corner_radius=0)
        
        self.canvas.create_window((0, 0), window=self.views_container, anchor="nw", tags="self.views_container")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.views_container.bind("<Configure>", self.update_scroll_region)
        self.canvas.bind("<Configure>", self.respond_to_canvas_resize)

        # -------------------------------------------------------------
        # ✨ מילון לאחסון המסכים הטעונים מראש (View Caching)
        # -------------------------------------------------------------
        self.loaded_views = {}
        self.current_active_key = None

        # טעינה ראשונית חלקה של עמוד הבית
        self.switch_view("dashboard")

    def update_scroll_region(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def respond_to_canvas_resize(self, event):
        canvas_width = event.width
        self.canvas.itemconfig("self.views_container", width=canvas_width)
        
        if self.views_container.winfo_reqheight() > event.height:
            self.scrollbar.pack(side="right", fill="y")
        else:
            self.scrollbar.pack_forget()

    def create_sidebar_button(self, key, text, command):
        btn = ctk.CTkButton(
            self.sidebar_frame, text=text, font=("Segoe UI", 15),
            fg_color="transparent", text_color="#94A3B8", 
            hover_color="#111827", anchor="e", height=45, corner_radius=10,
            command=command
        )
        btn.pack(pady=3, padx=15, fill="x")
        self.buttons[key] = btn

    def set_active_button(self, active_key):
        for key, btn in self.buttons.items():
            if key == active_key:
                btn.configure(fg_color="#059669", text_color="#FFFFFF", font=("Segoe UI", 15, "bold"))
            else:
                btn.configure(fg_color="transparent", text_color="#94A3B8", font=("Segoe UI", 15))

    # -------------------------------------------------------------
    # ✨ הפונקציה החדשה למעבר מסכים מיידי ללא השהיה (0ms Delay)
    # -------------------------------------------------------------
    def switch_view(self, key):
        """מסתירה את המסך הנוכחי ומציגה את המסך המבוקש בלחיצה, טוענת רק פעם אחת"""
        if self.current_active_key == key:
            return  # לחיצה מחדש על הלשונית הפעילה - אין צורך לעשות כלום

        self.set_active_button(key)

        # 1. הסתרת המסך הפעיל הנוכחי (אם קיים) מבלי למחוק אותו מהזיכרון
        if self.current_active_key and self.current_active_key in self.loaded_views:
            self.loaded_views[self.current_active_key].pack_forget()

        # 2. אם המסך המבוקש עדיין לא נוצר מעולם - נייצר אותו פעם אחת עכשיו
        if key not in self.loaded_views:
            # יצירת פריים ייעודי מבודד עבור הלשונית הזו
            frame_view = ctk.CTkFrame(self.views_container, fg_color="#F3F4F6", corner_radius=0)
            
            # בניית התוכן של הלשונית בתוך הפריים החדש (קורא לקבצים החיצוניים שלך)
            if key == "dashboard":
                show_dashboard_view(frame_view)
            elif key == "stores":
                show_stores_view(frame_view)
            elif key == "employees":
                show_employees_view(frame_view)
            elif key == "warehouses":
                show_warehouses_view(frame_view)
            elif key == "inventory":
                show_inventory_view(frame_view)
            elif key == "suppliers":
                show_suppliers_view(frame_view)
            elif key == "orders":
                show_orders_view(frame_view)
            elif key == "discounts":
                show_discounts_view(frame_view)
                
            # שמירת המסך הבנוי במילון הזיכרון
            self.loaded_views[key] = frame_view

        # 3. הצגת המסך המבוקש (הוא עולה מיידית כי הוא כבר בנוי או נשלף מהזיכרון)
        self.loaded_views[key].pack(fill="both", expand=True)
        
        # עדכון מפתח המסך הנוכחי ועדכון סרגל הגלילה במידת הצורך
        self.current_active_key = key
        self.update_scroll_region()

if __name__ == "__main__":
    app = RamiLeviApp()
    app.mainloop()