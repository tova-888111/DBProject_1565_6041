import customtkinter as ctk
from db_connection import get_db_connection

def show_dashboard_view(main_frame):
    # ניקוי המסך
    for widget in main_frame.winfo_children():
        widget.destroy()

    # --- כותרת עליונה רחבה וברורה ---
    header_label = ctk.CTkLabel(main_frame, text="לוח בקרה רשתי", font=("Segoe UI", 28, "bold"), text_color="#111827", anchor="e")
    header_label.pack(pady=(30, 2), padx=35, fill="x")
    
    sub_header = ctk.CTkLabel(main_frame, text="סקירה כללית של כל פעילות הרשת בזמן אמת", font=("Segoe UI", 14), text_color="#6B7280", anchor="e")
    sub_header.pack(pady=(0, 30), padx=35, fill="x")

    # --- שורת הכרטיסיות העליונה (הקופסאות המעוגלות) ---
    cards_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    cards_frame.pack(padx=25, fill="x")

    # שליפת נתוני אמת מה-DB
    total_employees = 0
    total_stores = 0
    low_stock = 0
    out_of_stock = 0

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM EMPLOYEE;")
            total_employees = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM STORE;")
            total_stores = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM INVENTORY WHERE Quantity <= MinimumStock AND Quantity > 0;")
            low_stock = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM INVENTORY WHERE Quantity = 0;")
            out_of_stock = cursor.fetchone()[0]
        except Exception as e:
            print(f"Error fetching dashboard metrics: {e}")
        finally:
            cursor.close()
            conn.close()

    # יצירת 4 כרטיסיות עם פינות רחבות ומעוגלות וטקסט גדול וברור
    create_card(cards_frame, "👥  סה\"ך עובדים ברשת", f"{total_employees}", "#E0F2FE")
    create_card(cards_frame, "🏪  סניפים פעילים", f"{total_stores}", "#E8F5E9")
    create_card(cards_frame, "📦  ערך מלאי נוכחי", "₪8,420,000", "#EFF6FF")
    create_card(cards_frame, "⚠️  מוצרים בחוסר", f"{low_stock + out_of_stock}", "#FEE2E2")

    # --- פאנל תחתון מפוצל: התראות מימין, גרף משמאל ---
    bottom_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    bottom_frame.pack(pady=25, padx=25, fill="both", expand=True)

    # 1. קוביית גרף פיזור מלאי (תופס את הצד המרכזי הרחב)
    graph_container = ctk.CTkFrame(bottom_frame, fg_color="#FFFFFF", corner_radius=18, border_color="#E5E7EB", border_width=1)
    graph_container.pack(side="right", fill="both", expand=True, padx=12, pady=10)
    
    ctk.CTkLabel(graph_container, text="פיזור מלאי לפי סניפים", font=("Segoe UI", 18, "bold"), text_color="#111827", anchor="e").pack(pady=20, padx=25, fill="x")
    ctk.CTkLabel(graph_container, text="(כאן נציג בהמשך את גרף העמודות של הסניפים)", font=("Segoe UI", 13), text_color="#9CA3AF").pack(pady=90)

    # 2. קוביית התראות דחופות (צד שמאל - צרה ואלגנטית)
    alerts_container = ctk.CTkFrame(bottom_frame, fg_color="#FFFFFF", width=360, corner_radius=18, border_color="#E5E7EB", border_width=1)
    alerts_container.pack(side="left", fill="both", padx=12, pady=10)
    alerts_container.pack_propagate(False)
    
    ctk.CTkLabel(alerts_container, text="⚠️  התראות דחופות", font=("Segoe UI", 18, "bold"), text_color="#DC2626", anchor="e").pack(pady=20, padx=25, fill="x")

    # טעינת התראות אמיתיות
    conn = get_db_connection()
    has_alerts = False
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT p.ProductName, s.StoreName, i.Quantity 
                FROM INVENTORY i JOIN PRODUCT p ON i.ProductID = p.ProductID 
                JOIN STORE s ON i.StoreID = s.StoreID 
                WHERE i.Quantity <= i.MinimumStock ORDER BY i.Quantity ASC LIMIT 4;
            """)
            for prod_name, store_name, qty in cursor.fetchall():
                has_alerts = True
                status_txt = "חוסר קריטי" if qty == 0 else "מתחת לסף"
                lbl_color = "#EF4444" if qty == 0 else "#F59E0B"
                create_alert_row(alerts_container, f"{prod_name}\nסניף {store_name}", status_txt, lbl_color)
        except Exception as e:
            print(f"Error loading alerts: {e}")
        finally:
            cursor.close()
            conn.close()

    if not has_alerts:
        ctk.CTkLabel(alerts_container, text="✅ המלאי תקין בכל הסניפים", font=("Segoe UI", 14), text_color="#059669").pack(pady=60)

def create_card(parent, title, value, icon_bg):
    """ייצור כרטיסיית מידע לבנה, פונט גדול ופינות מעוגלות רחבות (18)"""
    card = ctk.CTkFrame(parent, fg_color="#FFFFFF", height=120, width=220, corner_radius=18, border_color="#E5E7EB", border_width=1)
    card.pack(side="right", padx=12, pady=5, fill="x", expand=True)
    card.pack_propagate(False)
    
    # כותרת הכרטיס (טקסט ברור יותר)
    ctk.CTkLabel(card, text=title, font=("Segoe UI", 14), text_color="#4B5563", anchor="e").pack(pady=(20, 2), padx=22, fill="x")
    # ערך מספרי גדול ומודגש מאוד
    ctk.CTkLabel(card, text=value, font=("Segoe UI", 28, "bold"), text_color="#111827", anchor="e").pack(padx=22, fill="x")

def create_alert_row(parent, title_text, status_text, tag_color):
    """שורת התראה חלקה ומעוגלת, עם תגית סטטוס צבעונית בולטת"""
    row = ctk.CTkFrame(parent, fg_color="#F9FAFB", corner_radius=12, height=60)
    row.pack(pady=6, padx=15, fill="x")
    row.pack_propagate(False)
    
    # טקסט המוצר והסניף (מיושר לימין, שתי שורות קריאות)
    ctk.CTkLabel(row, text=title_text, font=("Segoe UI", 12, "bold"), text_color="#1F2937", justify="right", anchor="e").pack(side="right", padx=12, fill="y")
    
    # תגית סטטוס מעוגלת משמאל
    tag = ctk.CTkLabel(row, text=status_text, font=("Segoe UI", 11, "bold"), text_color="#FFFFFF", fg_color=tag_color, corner_radius=8, width=75, height=24)
    tag.pack(side="left", padx=12, pady=18)