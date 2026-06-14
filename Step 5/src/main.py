import customtkinter as ctk
import sys
import os

# הוספת התיקייה הנוכחית לנתיב כדי למנוע בעיות ייבוא בין קבצים
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ייבוא העמודים (ניצור את הקבצים האלו מיד בשלבים הבאים)
from dashboard_screen import show_dashboard_view

class RamiLeviApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # הגדרות חלון מודרני ורחב
        self.title("רמי לוי - מערכת ניהול רשת חנויות")
        self.geometry("1200x700")
        
        # ערכת נושא בהירה לחלק המרכזי (כמו באתר)
        ctk.set_appearance_mode("light")  
        ctk.set_default_color_theme("blue")

        # -------------------------------------------------------------
        # 1. תפריט צד ימני (Right Sidebar) - צבע כהה עמוק
        # -------------------------------------------------------------
        self.sidebar_frame = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color="#030712")
        self.sidebar_frame.pack(side="right", fill="y")
        self.sidebar_frame.pack_propagate(False)

        # לוגו וסטטוס עליון
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="רמי לוי", font=("Arial", 26, "bold"), text_color="#10B981") # ירוק מותג מודרני
        self.logo_label.pack(pady=(35, 2))
        self.sub_logo = ctk.CTkLabel(self.sidebar_frame, text="ניהול מטה רשתי", font=("Arial", 12), text_color="#94A3B8")
        self.sub_logo.pack(pady=(0, 40))

        # מילון לשמירת כפתורי הניווט
        self.buttons = {}
        
        # יצירת תפריטי הניווט בדיוק לפי הצילום מסך שלך
        self.create_sidebar_button("dashboard", "📊   לוח בקרה רשתי", self.open_dashboard)
        self.create_sidebar_button("stores", "🏪   ניהול סניפים", lambda: self.placeholder_screen("ניהול סניפים"))
        self.create_sidebar_button("inventory", "📦   מלאי רשתי", lambda: self.placeholder_screen("מלאי רשתי"))
        self.create_sidebar_button("suppliers", "🚚   ספקים ומשלוחים", lambda: self.placeholder_screen("ספקים ומשלוחים"))
        self.create_sidebar_button("employees", "👥   ניהול עובדים", lambda: self.placeholder_screen("ניהול עובדים"))

        # פרופיל משתמש בתחתית התפריט (כמו "משה כהן" בתמונה)
        self.user_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="#111827", corner_radius=12, height=60)
        self.user_frame.pack(side="bottom", pady=25, padx=15, fill="x")
        self.user_frame.pack_propagate(False)
        
        self.user_title = ctk.CTkLabel(self.user_frame, text="משה כהן", font=("Arial", 13, "bold"), text_color="#F8FAFC", anchor="e")
        self.user_title.pack(pady=(8, 0), padx=15, fill="x")
        self.user_role = ctk.CTkLabel(self.user_frame, text="מנהל תפעול רשתי", font=("Arial", 11), text_color="#94A3B8", anchor="e")
        self.user_role.pack(padx=15, fill="x")

        # -------------------------------------------------------------
        # 2. האזור המרכזי הדינמי (Main Canvas) - רקע בהיר ונקי
        # -------------------------------------------------------------
        self.main_frame = ctk.CTkFrame(self, fg_color="#F9FAFB", corner_radius=0) # אפור-ווב עדין מאוד
        self.main_frame.pack(side="left", fill="both", expand=True)

        # טעינת עמוד הבית (לוח הבקרה) כברירת מחדל בריצה הראשונה
        self.open_dashboard()

    def create_sidebar_button(self, key, text, command):
        """מייצר כפתור ניווט איכותי ומיושר לימין בשבילך עברית"""
        btn = ctk.CTkButton(
            self.sidebar_frame, text=text, font=("Arial", 14),
            fg_color="transparent", text_color="#94A3B8", 
            hover_color="#1F2937", anchor="e", height=45, corner_radius=8,
            command=command
        )
        btn.pack(pady=5, padx=15, fill="x")
        self.buttons[key] = btn

    def set_active_button(self, active_key):
        """צובע את הכפתור שנלחץ בירוק-תכלת זוהר ומכבה את האחרים, בדיוק כמו בהשראה שלך"""
        for key, btn in self.buttons.items():
            if key == active_key:
                btn.configure(fg_color="#059669", text_color="#FFFFFF", font=("Arial", 14, "bold")) # צבע ירוק-ווב עשיר
            else:
                btn.configure(fg_color="transparent", text_color="#94A3B8", font=("Arial", 14))

    # --- פונקציות הניווט ---
    def open_dashboard(self):
        self.set_active_button("dashboard")
        show_dashboard_view(self.main_frame)

    def placeholder_screen(self, title):
        """מסך זמני לעמודים שעדיין לא בנינו כדי שהתוכנה תנווט חלק"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        lbl = ctk.CTkLabel(self.main_frame, text=f"מסך {title}", font=("Arial", 22, "bold"), text_color="#1F2937", anchor="e")
        lbl.pack(pady=40, padx=30, fill="x")
        desc = ctk.CTkLabel(self.main_frame, text="בשלבים הבאים נבנה כאן את טבלאות ה-CRUD המלאות בצורה מסודרת.", font=("Arial", 14), text_color="#4B5563", anchor="e")
        desc.pack(padx=30, fill="x")

if __name__ == "__main__":
    app = RamiLeviApp()
    app.mainloop()