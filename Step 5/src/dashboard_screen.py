import customtkinter as ctk
from db_connection import get_db_connection

# ייבוא הרכיבים הנדרשים ליצירת גרפים וחיבורם לממשק הגרפי
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def show_dashboard_view(main_frame):
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

    # --- ✨ 2. שדרוג ועיצוב: תיבת אודות בצבע של סרגל הצד (#030712) עם שורות מפורקות למניעת היפוך ---
    about_frame = ctk.CTkFrame(main_frame, fg_color="#030712", corner_radius=18)
    about_frame.pack(pady=(0, 25), padx=37, fill="x")
    
    about_title = ctk.CTkLabel(
        about_frame, 
        text="💡  אודות הרשת ואתר הניהול המרכזי", 
        font=("Segoe UI", 16, "bold"), 
        text_color="#FFFFFF", # טקסט לבן בולט על רקע כהה
        anchor="e"
    )
    about_title.pack(fill="x", padx=30, pady=(20, 10))
    
    # פירוק המלל למשפטים קצרים בנפרד כדי לחסום לחלוטין את באג היפוך השורות של tkinter
    sentences = [
        " רשת רמי לוי שיווק השקמה היא מרשתות המזון והקמעונאות המובילות והמשפיעות ביותר בישראל•",
        " הרשת חורטת על דגלה מתן שירות איכותי, יעיל, ומחירים הוגנים ומשתלמים לצרכן הישראלי•",
        " אתר ניהול מטה זה פותח במטרה לספק מענה טכנולוגי מתקדם ואינטראקטיבי לפיקוח על זרועות הרשת•",
        " הפורטל מאפשר לבצע סנכרון מלא של מלאי הסניפים, לעקוב אחר תנועות משאיות ההפצה ולנהל כוח אדם•"
    ]
    
    # יצירת אלמנט נפרד לכל שורה - מבטיח יישור מושלם מימין לשמאל ללא חיתוכי מילים
    for sentence in sentences:
        lbl = ctk.CTkLabel(
            about_frame,
            text=sentence,
            font=("Segoe UI", 13, "bold"),
            text_color="#F3F4F6", # צבע בהיר קריא ונקי
            anchor="e",
            justify="right"
        )
        lbl.pack(fill="x", padx=30, pady=3)
        
    # מרווח תחתון קל לסגירת הפריים הכהה
    ctk.CTkLabel(about_frame, text="", height=10).pack()

    # --- 3. שורת הכרטיסיות (הסטטיסטיקות) ---
    cards_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    cards_frame.pack(padx=25, fill="x")

    # משתנים לשמירת מדדי האמת מהדאטהבייס
    total_employees = 0
    total_stores = 0
    total_items_quantity = 0 
    total_inventory_value = 0
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

    formatted_value = f"₪{int(total_inventory_value):,}"
    formatted_items = f"{total_items_quantity:,}"

    # יצירת 4 כרטיסיות הסטטיסטיקה
    create_card(cards_frame, "👥  סה\"ך עובדים ברשת", f"{total_employees}", "#E0F2FE")
    create_card(cards_frame, "🏪  סניפים פעילים", f"{total_stores}", "#E8F5E9")
    create_card(cards_frame, "📦  ערך מלאי נוכחי", formatted_value, "#EFF6FF")
    create_card(cards_frame, "📊  סך מלאי ברשת (פריטים)", formatted_items, "#FEE2E2")

    # --- 4. פאנל תחתון מפוצל (גרף + התראות) ---
    bottom_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    bottom_frame.pack(pady=(20, 20), padx=25, fill="x")

    # קוביית גרף פיזור מלאי לפי אזורים (צד ימין של המסך)
    graph_container = ctk.CTkFrame(bottom_frame, fg_color="#FFFFFF", corner_radius=18, border_color="#E5E7EB", border_width=1)
    graph_container.pack(side="right", fill="both", expand=True, padx=12, pady=5)
    
    ctk.CTkLabel(graph_container, text="פיזור סניפים לפי אזורים", font=("Segoe UI", 18, "bold"), text_color="#111827", anchor="e").pack(pady=(20, 5), padx=25, fill="x")
    
    build_regions_graph(graph_container)

    # קוביית סיכום התראות (צד שמאל של המסך)
    alerts_wrapper = ctk.CTkFrame(bottom_frame, fg_color="#FFFFFF", width=380, height=340, corner_radius=18, border_color="#E5E7EB", border_width=1)
    alerts_wrapper.pack(side="left", fill="both", padx=12, pady=5)
    alerts_wrapper.pack_propagate(False)
    
    ctk.CTkLabel(alerts_wrapper, text="⚠️  סטטוס חריגות מלאי", font=("Segoe UI", 18, "bold"), text_color="#DC2626", anchor="e").pack(pady=20, padx=25, fill="x")

    create_summary_box(
        alerts_wrapper, 
        title="חוסר קריטי ברשת", 
        value=f"{out_of_stock_count}", 
        desc="פריטים שאזלו לחלוטין מהמלאי ודורשים הזמנה מיידית מהספק", 
        bg_color="#FEF2F2", 
        text_color="#991B1B"
    )

    create_summary_box(
        alerts_wrapper, 
        title="מתחת לסף מינימום", 
        value=f"{low_stock_count}", 
        desc="פריטים שהגיעו לקו האדום של המלאי שהוגדר בסניף", 
        bg_color="#FFFBEB", 
        text_color="#92400E"
    )

    # אילוץ המערכת הגרפית לחשב ולייצב את המיקומים והגלילה מיד
    try:
        main_frame.update_idletasks()
        main_frame.winfo_toplevel().update()
    except:
        pass


def create_card(parent, title, value, icon_bg):
    card = ctk.CTkFrame(parent, fg_color="#FFFFFF", height=120, width=220, corner_radius=18, border_color="#E5E7EB", border_width=1)
    card.pack(side="right", padx=12, pady=5, fill="x", expand=True)
    card.pack_propagate(False)
    
    ctk.CTkLabel(card, text=title, font=("Segoe UI", 14), text_color="#4B5563", anchor="e").pack(pady=(20, 2), padx=22, fill="x")
    ctk.CTkLabel(card, text=value, font=("Segoe UI", 28, "bold"), text_color="#111827", anchor="e").pack(padx=22, fill="x")

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

def build_regions_graph(parent_frame):
    """שליפת כמות סניפים לפי אזור מטבלת STORE והצגת גרף עמודות מודרני"""
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

    fig, ax = plt.subplots(figsize=(5, 3), dpi=100)
    fig.patch.set_facecolor('#FFFFFF') 
    ax.set_facecolor('#FFFFFF')  

    bars = ax.bar(regions, store_counts, color='#10B981', width=0.4, edgecolor='none')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#E5E7EB')
    ax.spines['bottom'].set_color('#E5E7EB')
    ax.tick_params(colors='#4B5563', labelsize=10)
    
    ax.yaxis.get_major_locator().set_params(integer=True)

    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{int(height)}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10, color='#111827', weight='bold')

    canvas = FigureCanvasTkAgg(fig, master=parent_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.config(bg='#FFFFFF', highlightthickness=0)
    canvas_widget.pack(fill="both", expand=True, padx=20, pady=(10, 20))
    canvas.draw()
    
    plt.close(fig)