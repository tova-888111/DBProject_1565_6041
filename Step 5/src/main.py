import customtkinter as ctk
import sys
import os
from PIL import Image

# הוספת התיקייה הנוכחית לנתיב למניעת בעיות ייבוא
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dashboard_screen import show_dashboard_view
from stores_screen import show_stores_view
from employees_screen import show_employees_view 
from discounts_screen import show_discounts_view

class RamiLeviApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # הגדרות חלון - רחב ומקצועי
        self.title("רמי לוי - לוח בקרה ניהולי")
        self.geometry("1280x720")
        
        # ערכת נושא בהירה לחלק המרכזי
        ctk.set_appearance_mode("light")  
        ctk.set_default_color_theme("blue")

        # -------------------------------------------------------------
        # 1. תפריט צד ימני (Right Sidebar) - כחול-נייבי כהה ועמוק
        # -------------------------------------------------------------
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color="#030712")
        self.sidebar_frame.pack(side="right", fill="y")
        self.sidebar_frame.pack_propagate(False)

        # טעינת הלוגו הרשמי מתיקיית ה-assets
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

        # מילון לשמירת כפתורי הניווט
        self.buttons = {}
        
        # יצירת כפתורי הניווט המורחבים המכסים את כל 17 הטבלאות במערכת
        self.create_sidebar_button("dashboard", "📊   לוח בקרה רשתי", self.open_dashboard)
        self.create_sidebar_button("stores", "🏪   ניהול סניפים", lambda: [self.set_active_button("stores"), show_stores_view(self.main_frame)])
        self.create_sidebar_button("employees", "👥   ניהול עובדים", lambda: [self.set_active_button("employees"), show_employees_view(self.main_frame)])
        self.create_sidebar_button("warehouses", "🏭   מחסנים לוגיסטיים", lambda: self.placeholder_screen("warehouses", "מחסנים לוגיסטיים"))
        self.create_sidebar_button("inventory", "📦   מלאי ומוצרים", lambda: self.placeholder_screen("inventory", "מלאי ומוצרים"))
        self.create_sidebar_button("suppliers", "🚚   ספקים ורכש", lambda: self.placeholder_screen("suppliers", "ספקים ורכש"))
        self.create_sidebar_button("orders", "🛒   הזמנות הפצה", lambda: self.placeholder_screen("orders", "הזמנות הפצה"))
        self.create_sidebar_button("discounts", "🏷️   מבצעים והנחות", lambda: [self.set_active_button("discounts"), show_discounts_view(self.main_frame)])

        # פרופיל משתמש מעוגל בתחתית
        self.user_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="#111827", corner_radius=14, height=65)
        self.user_frame.pack(side="bottom", pady=25, padx=15, fill="x")
        self.user_frame.pack_propagate(False)
        
        self.user_title = ctk.CTkLabel(self.user_frame, text="משה כהן", font=("Segoe UI", 14, "bold"), text_color="#F8FAFC", anchor="e")
        self.user_title.pack(pady=(10, 0), padx=18, fill="x")
        self.user_role = ctk.CTkLabel(self.user_frame, text="מנהל תפעול רשתי", font=("Segoe UI", 11), text_color="#94A3B8", anchor="e")
        self.user_role.pack(padx=18, fill="x")

        # -------------------------------------------------------------
        # 2. האזור המרכזי הדינמי - רקע ווב בהיר
        # -------------------------------------------------------------
        self.main_frame = ctk.CTkFrame(self, fg_color="#F3F4F6", corner_radius=0)
        self.main_frame.pack(side="left", fill="both", expand=True)

        # טעינת עמוד הבית כברירת מחדל
        self.open_dashboard()

    def create_sidebar_button(self, key, text, command):
        """מייצר כפתור ניווט איכותי, מיושר לימין ופונט ברור"""
        btn = ctk.CTkButton(
            self.sidebar_frame, text=text, font=("Segoe UI", 15),
            fg_color="transparent", text_color="#94A3B8", 
            hover_color="#111827", anchor="e", height=45, corner_radius=10,
            command=command
        )
        btn.pack(pady=3, padx=15, fill="x")
        self.buttons[key] = btn

    def set_active_button(self, active_key):
        """אפקט סימון ירוק-ברקת בולט לכפתור הפעיל"""
        for key, btn in self.buttons.items():
            if key == active_key:
                btn.configure(fg_color="#059669", text_color="#FFFFFF", font=("Segoe UI", 15, "bold"))
            else:
                btn.configure(fg_color="transparent", text_color="#94A3B8", font=("Segoe UI", 15))

    def open_dashboard(self):
        self.set_active_button("dashboard")
        show_dashboard_view(self.main_frame)

    def placeholder_screen(self, key, title):
        """מסך זמני המדליק את הסימון האקטיבי ומציג כותרת ברורה"""
        self.set_active_button(key)
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        lbl = ctk.CTkLabel(self.main_frame, text=f"מסך {title}", font=("Segoe UI", 24, "bold"), text_color="#111827", anchor="e")
        lbl.pack(pady=40, padx=40, fill="x")
        
        desc = ctk.CTkLabel(self.main_frame, text=".כאן נבנה בשלב הבא את טבלאות הניהול, ההוספה, העריכה והמחיקה המלאות בהתאם לעיצוב שתבחרי", font=("Segoe UI", 14), text_color="#4B5563", anchor="e")
        desc.pack(padx=40, fill="x")

if __name__ == "__main__":
    app = RamiLeviApp()
    app.mainloop()