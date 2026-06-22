import customtkinter as ctk
from db_connection import get_db_connection

# ייבוא הרכיבים הנדרשים ליצירת גרפים וחיבורם לממשק הגרפי
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# משתנים פנימיים לצורך ניהול הרענון הדינמי ללא הבהובים וקפיצות
_dashboard_loop_id = None
_fig, _ax = None, None
_canvas_widget_ref = None

def show_dashboard_view(main_frame):
    global _dashboard_loop_id, _fig, _ax, _canvas_widget_ref
    
    # ביטול לולאות רענון קודמות למניעת כפילויות בריצה ברקע
    if _dashboard_loop_id is not None:
        try:
            main_frame.after_cancel(_dashboard_loop_id)
        except:
            pass
        _dashboard_loop_id = None

    # אתחול אובייקטי הגרף הנייחים פעם אחת בלבד למניעת קפיצות
    _fig, _ax = plt.subplots(figsize=(5, 3), dpi=100)
    _canvas_widget_ref = None

    # ניקוי המסך כדי למנוע כפילויות תצוגה
    for widget in main_frame.winfo_children():
        widget.destroy()

    # --- 1. כותרת עליונה רחבה ונשייה (מנופחת ועשירה) ---
    header_label = ctk.CTkLabel(
        main_frame, 
        text="לוח בקרה רשתי", 
        font=("Segoe UI", 32, "bold"), 
        text_color="#111827", 
        anchor="e"
    )
    header_label.pack(pady=(35, 4), padx=35, fill="x")
    
    sub_header = ctk.CTkLabel(
        main_frame, 
        text="סקירה כללית של כל פעילות הרשת בזמן אמת", 
        font=("Segoe UI", 14, "bold"), 
        text_color="#4B5563", 
        anchor="e"
    )
    sub_header.pack(pady=(0, 20), padx=35, fill="x")

    # --- 2. תיבת אודות בצבע של סרגל הצד (#030712) עם שורות מפורקות למניעת היפוך ---
    about_frame = ctk.CTkFrame(main_frame, fg_color="#030712", corner_radius=18)
    about_frame.pack(pady=(0, 25), padx=37, fill="x")
    
    about_title = ctk.CTkLabel(
        about_frame, 
        text="💡  אודות הרשת ואתר הניהול המרכזי", 
        font=("Segoe UI", 16, "bold"), 
        text_color="#FFFFFF", 
        anchor="e"
    )
    about_title.pack(fill="x", padx=30, pady=(20, 10))
    
    sentences = [
        " רשת רמי לוי שיווק השקמה היא מרשתות המזון והקמעונאות המובילות והמשפיעות ביותר בישראל•",
        " הרשת חורטת על דגלה מתן שירות איכותי, יעיל, ומחירים הוגנים ומשתלמים לצרכן הישראלי•",
        " אתר ניהול מטה זה פותח במטרה לספק מענה טכנולוגי מתקדם ואינטראקטיבי לפיקוח על זרועות הרשת•",
        " הפורטל מאפשר לבצע סנכרון מלא של מלאי הסניפים, לעקוב אחר תנועות משאיות ההפצה ולנהל כוח אדם•"
    ]
    
    for sentence in sentences:
        lbl = ctk.CTkLabel(
            about_frame,
            text=sentence,
            font=("Segoe UI", 13, "bold"),
            text_color="#F3F4F6", 
            anchor="e",
            justify="right"
        )
        lbl.pack(fill="x", padx=30, pady=3)
        
    ctk.CTkLabel(about_frame, text="", height=10).pack()

    # --- 3. שורת הכרטיסיות (הסטטיסטיקות) ---
    cards_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    cards_frame.pack(padx=25, fill="x")

    # בניית הכרטיסיות ושמירת הרפרנס של הלייבלים לעדכון ישיר
    lbl_emp = create_card(cards_frame, "👥  סה\"ך עובדים ברשת", "0", "#E0F2FE")
    lbl_stores = create_card(cards_frame, "🏪  סניפים פעילים", "0", "#E8F5E9")
    lbl_val = create_card(cards_frame, "📦  ערך מלאי נוכחי", "₪0", "#EFF6FF")
    lbl_qty = create_card(cards_frame, "📊  סך מלאי ברשת (פריטים)", "0", "#FEE2E2")

    # --- 4. פאנל תחתון מפוצל (גרף + התראות) ---
    bottom_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    bottom_frame.pack(pady=(20, 20), padx=25, fill="x")

    # קוביית גרף פיזור מלאי לפי אזורים (צד ימין של המסך)
    graph_container = ctk.CTkFrame(bottom_frame, fg_color="#FFFFFF", corner_radius=18, border_color="#E5E7EB", border_width=1)
    graph_container.pack(side="right", fill="both", expand=True, padx=12, pady=5)
    
    ctk.CTkLabel(graph_container, text="פיזור סניפים לפי אזורים", font=("Segoe UI", 18, "bold"), text_color="#111827", anchor="e").pack(pady=(20, 5), padx=25, fill="x")

    # קוביית סיכום התראות (צד שמאל של המסך)
    alerts_wrapper = ctk.CTkFrame(bottom_frame, fg_color="#FFFFFF", width=380, height=340, corner_radius=18, border_color="#E5E7EB", border_width=1)
    alerts_wrapper.pack(side="left", fill="both", padx=12, pady=5)
    alerts_wrapper.pack_propagate(False)
    
    ctk.CTkLabel(alerts_wrapper, text="⚠️  סטטוס חריגות מלאי", font=("Segoe UI", 18, "bold"), text_color="#DC2626", anchor="e").pack(pady=20, padx=25, fill="x")

    lbl_out_of_stock = create_summary_box(
        alerts_wrapper, 
        title="חוסר קריטי ברשת", 
        value="0", 
        desc="פריטים שאזלו לחלוטין מהמלאי ודורשים הזמנה מיידית מהספק", 
        bg_color="#FEF2F2", 
        text_color="#991B1B"
    )

    lbl_low_stock = create_summary_box(
        alerts_wrapper, 
        title="מתחת לסף מינימום", 
        value="0", 
        desc="פריטים שהגיעו לקו האדום של המלאי שהוגדר בסניף", 
        bg_color="#FFFBEB", 
        text_color="#92400E"
    )

    # פונקציית לולאת הרענון הדינמית והשקטה
    def refresh_dashboard_loop():
        global _dashboard_loop_id, _canvas_widget_ref
        
        total_employees = 0
        total_stores = 0
        total_inventory_value = 0.0
        total_items_quantity = 0
        low_stock_count = 0
        out_of_stock_count = 0

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT COUNT(*) FROM EMPLOYEE;")
                total_employees = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM STORE;")
                total_stores = cursor.fetchone()[0]
                
                cursor.execute("SELECT SUM(i.Quantity * p.Price) FROM INVENTORY i JOIN PRODUCT p ON i.ProductID = p.ProductID;")
                res_val = cursor.fetchone()[0]
                total_inventory_value = float(res_val) if res_val else 0.0

                cursor.execute("SELECT SUM(Quantity) FROM INVENTORY;")
                res_qty = cursor.fetchone()[0]
                total_items_quantity = int(res_qty) if res_qty else 0

                cursor.execute("SELECT COUNT(*) FROM INVENTORY WHERE Quantity <= MinimumStock AND Quantity > 0;")
                low_stock_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM INVENTORY WHERE Quantity = 0;")
                out_of_stock_count = cursor.fetchone()[0]

            except Exception as e:
                print(f"Error fetching dashboard metrics: {e}")
            finally:
                cursor.close()
                conn.close()

        # עדכון הערכים בלייבלים הקיימים ללא הבהובים
        lbl_emp.configure(text=f"{total_employees}")
        lbl_stores.configure(text=f"{total_stores}")
        lbl_val.configure(text=f"₪{int(total_inventory_value):,}")
        lbl_qty.configure(text=f"{total_items_quantity:,}")
        lbl_out_of_stock.configure(text=f"{out_of_stock_count}")
        lbl_low_stock.configure(text=f"{low_stock_count}")

        # ✨ עדכון הגרף בצורה שקטה על גבי הקנבס הקיים ללא יצירת אובייקט חדש (מונע קפיצות)
        update_regions_graph_data(graph_container)

        try:
            main_frame.update_idletasks()
        except:
            pass

        # הרצה חוזרת של הלולאה בעוד 5 שניות בדיוק
        _dashboard_loop_id = main_frame.after(5000, refresh_dashboard_loop)

    # הזנקת הרענון הראשון
    refresh_dashboard_loop()


def create_card(parent, title, value, icon_bg):
    card = ctk.CTkFrame(parent, fg_color="#FFFFFF", height=120, width=220, corner_radius=18, border_color="#E5E7EB", border_width=1)
    card.pack(side="right", padx=12, pady=5, fill="x", expand=True)
    card.pack_propagate(False)
    
    ctk.CTkLabel(card, text=title, font=("Segoe UI", 14), text_color="#4B5563", anchor="e").pack(pady=(20, 2), padx=22, fill="x")
    val_lbl = ctk.CTkLabel(card, text=value, font=("Segoe UI", 28, "bold"), text_color="#111827", anchor="e")
    val_lbl.pack(padx=22, fill="x")
    return val_lbl

def create_summary_box(parent, title, value, desc, bg_color, text_color):
    box = ctk.CTkFrame(parent, fg_color=bg_color, corner_radius=14, height=110)
    box.pack(pady=10, padx=20, fill="x")
    box.pack_propagate(False)
    
    top_row = ctk.CTkFrame(box, fg_color="transparent")
    top_row.pack(fill="x", padx=15, pady=(12, 2))
    
    val_lbl = ctk.CTkLabel(top_row, text=value, font=("Segoe UI", 18, "bold"), text_color=text_color)
    val_lbl.pack(side="left")
    
    title_lbl = ctk.CTkLabel(top_row, text=title, font=("Segoe UI", 14, "bold"), text_color=text_color, anchor="e")
    title_lbl.pack(side="right")
    
    desc_lbl = ctk.CTkLabel(box, text=desc, font=("Segoe UI", 11), text_color="#4B5563", wraplength=310, justify="right", anchor="e")
    desc_lbl.pack(fill="x", padx=15, pady=(2, 8))
    return val_lbl

def update_regions_graph_data(parent_frame):
    """שליפת נתונים ועדכון שקט של הגרף על גבי התשתית הקיימת ללא קפיצות מסך"""
    global _fig, _ax, _canvas_widget_ref
    
    regions = []
    store_counts = []

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT COALESCE(Region, 'לא מוגדר'), COUNT(*) 
                FROM STORE 
                GROUP BY Region 
                ORDER BY COUNT(*) DESC;
            """)
            for reg, count in cursor.fetchall():
                regions.append(reg)
                store_counts.append(count)
        except Exception as e:
            print(f"Error fetching graph data: {e}")
        finally:
            cursor.close()
            conn.close()

    if not regions:
        regions = ['אין נתונים']
        store_counts = [0]

    # ✨ ניקוי הנתונים בלבד מה-Axes הקיים מבלי למחוק את כל האובייקט הגרפי
    _ax.clear()
    
    _fig.patch.set_facecolor('#FFFFFF') 
    _ax.set_facecolor('#FFFFFF')  

    bars = _ax.bar(regions, store_counts, color='#10B981', width=0.4, edgecolor='none')

    _ax.spines['top'].set_visible(False)
    _ax.spines['right'].set_visible(False)
    _ax.spines['left'].set_color('#E5E7EB')
    _ax.spines['bottom'].set_color('#E5E7EB')
    _ax.tick_params(colors='#4B5563', labelsize=10)
    
    _ax.yaxis.get_major_locator().set_params(integer=True)

    for bar in bars:
        height = bar.get_height()
        _ax.annotate(f'{int(height)}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10, color='#111827', weight='bold')

    # יצירת הווידג'ט רק בפעם הראשונה, ובפעמים הבאות רק קוראים ל-draw יציב על אותו אלמנט
    if _canvas_widget_ref is None:
        canvas_obj = FigureCanvasTkAgg(_fig, master=parent_frame)
        _canvas_widget_ref = canvas_obj.get_tk_widget()
        _canvas_widget_ref.config(bg='#FFFFFF', highlightthickness=0)
        _canvas_widget_ref.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        canvas_obj.draw()
    else:
        _fig.canvas.draw_idle() # פקודת רענון רקע שקטה לחלוטין ללא קפיצות בעיניים