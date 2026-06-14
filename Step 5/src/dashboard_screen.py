import customtkinter as ctk
from db_connection import get_db_connection

def show_dashboard_view(main_frame):
    # 1. ניקוי יסודי של המסך הראשי
    for widget in main_frame.winfo_children():
        widget.destroy()

    # 2. כותרת עליונה של הלוח בקרה (מיושרת לימין)
    header_label = ctk.CTkLabel(main_frame, text="לוח בקרה רשתי", font=("Arial", 24, "bold"), text_color="#111827", anchor="e")
    header_label.pack(pady=(25, 2), padx=30, fill="x")
    
    sub_header = ctk.CTkLabel(main_frame, text="סקירה כללית של כל פעילות הרשת בזמן אמת מתוך בסיס הנתונים", font=("Arial", 13), text_color="#4B5563", anchor="e")
    sub_header.pack(pady=(0, 25), padx=30, fill="x")

    # 3. פאנל כרטיסיות (Cards Grid) - שורה עליונה
    cards_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    cards_frame.pack(padx=20, fill="x")

    # --- שליפת מדדים אמיתיים מהדוקר עבור הכרטיסיות ---
    total_employees = 0
    total_stores = 0
    low_stock_count = 0
    out_of_stock_count = 0

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # א. ספירת עובדים
            cursor.execute("SELECT COUNT(*) FROM EMPLOYEE;")
            total_employees = cursor.fetchone()[0]
            
            # ב. ספירת סניפים
            cursor.execute("SELECT COUNT(*) FROM STORE;")
            total_stores = cursor.fetchone()[0]
            
            # ג. ספירת מוצרים מתחת לסף המינימום (טבלת INVENTORY)
            cursor.execute("SELECT COUNT(*) FROM INVENTORY WHERE Quantity <= MinimumStock AND Quantity > 0;")
            low_stock_count = cursor.fetchone()[0]

            # ד. ספירת מוצרים שאזלו לחלוטין מהמלאי
            cursor.execute("SELECT COUNT(*) FROM INVENTORY WHERE Quantity = 0;")
            out_of_stock_count = cursor.fetchone()[0]
        except Exception as e:
            print(f"שגיאה בשליפת נתוני דאשבורד: {e}")
        finally:
            cursor.close()
            conn.close()

    # יצירת 4 כרטיסיות מעוצבות בדיוק כמו בתמונה שלך (מיושרות מימין לשמאל)
    create_card(cards_frame, "👥  סה\"ך עובדים ברשת", f"{total_employees}", "#E0F2FE")
    create_card(cards_frame, "🏪  סניפים פעילים", f"{total_stores}", "#E8F5E9")
    create_card(cards_frame, "🚨  מוצרים בחוסר", f"{out_of_stock_count}", "#FEE2E2")
    create_card(cards_frame, "⚠️  מתחת לסף מלאי", f"{low_stock_count}", "#FEF3C7")

    # 4. פאנל תחתון: אזור ההתראות הדחופות (צד שמאל של המסך)
    bottom_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    bottom_frame.pack(pady=20, padx=20, fill="both", expand=True)

    # פאנל לבן מעוגל עבור רשימת ההתראות החיות
    alerts_container = ctk.CTkFrame(bottom_frame, fg_color="#FFFFFF", corner_radius=16, border_color="#E5E7EB", border_width=1)
    alerts_container.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    
    ctk.CTkLabel(alerts_container, text="⚠️  התראות דחופות מהמלאי", font=("Arial", 16, "bold"), text_color="#DC2626", anchor="e").pack(pady=15, padx=20, fill="x")

    # --- שליפת רשימת החוסרים האמיתית (שאילתת JOIN בין INVENTORY, PRODUCT ו-STORE) ---
    conn = get_db_connection()
    alert_triggered = False
    if conn:
        cursor = conn.cursor()
        try:
            query = """
                SELECT p.ProductName, s.StoreName, i.Quantity
                FROM INVENTORY i
                JOIN PRODUCT p ON i.ProductID = p.ProductID
                JOIN STORE s ON i.StoreID = s.StoreID
                WHERE i.Quantity <= i.MinimumStock
                ORDER BY i.Quantity ASC
                LIMIT 4; -- מציגים את 4 החוסרים הכי דחופים
            """
            cursor.execute(query)
            alerts = cursor.fetchall()
            
            for prod_name, store_name, qty in alerts:
                alert_triggered = True
                status_desc = f"חוסר קריטי (מלאי: {qty})" if qty == 0 else f"מלאי נמוך: {qty} יחידות"
                bg_color = "#FEE2E2" if qty == 0 else "#FEF3C7"
                create_alert_row(alerts_container, f"{prod_name} — סניף {store_name}", status_desc, bg_color)
        except Exception as e:
            print(f"שגיאה בטעינת רשימת התראות: {e}")
        finally:
            cursor.close()
            conn.close()

    if not alert_triggered:
        # הודעת הרגעה אם הכל תקין ברשת
        ctk.CTkLabel(alerts_container, text="✅ כל המוצרים בכל הסניפים מעל סף המינימום!", font=("Arial", 13), text_color="#059669").pack(pady=40)

    # אזור ימין זמני לגרף שנוסיף בשלבים הבאים
    graph_container = ctk.CTkFrame(bottom_frame, fg_color="#FFFFFF", corner_radius=16, border_color="#E5E7EB", border_width=1)
    graph_container.pack(side="right", fill="both", expand=True, padx=10, pady=10)
    ctk.CTkLabel(graph_container, text="📊 פיזור מלאי לפי סניפים", font=("Arial", 16, "bold"), text_color="#111827", anchor="e").pack(pady=15, padx=20, fill="x")
    ctk.CTkLabel(graph_container, text="(כאן נלבש בשלב הבא את גרף העמודות החי באמצעות Matplotlib)", font=("Arial", 12), text_color="#6B7280").pack(pady=80)

def create_card(parent, title, value, bg_color):
    """פונקציית עזר ליצירת כרטיסיית מידע לבנה ויפה בהתאם להשראה שלך"""
    card = ctk.CTkFrame(parent, fg_color="#FFFFFF", height=110, width=210, corner_radius=16, border_color="#E5E7EB", border_width=1)
    card.pack(side="right", padx=12, pady=5, fill="x", expand=True)
    card.pack_propagate(False)
    
    # כותרת עליונה של הכרטיס (אפורה קטנה)
    ctk.CTkLabel(card, text=title, font=("Arial", 13), text_color="#4B5563", anchor="e").pack(pady=(16, 2), padx=20, fill="x")
    # מספר גדול ובולט
    ctk.CTkLabel(card, text=value, font=("Arial", 26, "bold"), text_color="#111827", anchor="e").pack(padx=20, fill="x")

def create_alert_row(parent, text_main, text_status, bg_color):
    """מייצר שורת התראה צבעונית רכה ומרופדת ללוח התראות"""
    row = ctk.CTkFrame(parent, fg_color=bg_color, corner_radius=10, height=48)
    row.pack(pady=6, padx=15, fill="x")
    row.pack_propagate(False)
    
    # שם המוצר והסניף מימין
    ctk.CTkLabel(row, text=text_main, font=("Arial", 12, "bold"), text_color="#1F2937").pack(side="right", padx=15)
    # סטטוס המלאי משמאל
    ctk.CTkLabel(row, text=text_status, font=("Arial", 12), text_color="#4B5563").pack(side="left", padx=15)