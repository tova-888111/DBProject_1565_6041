import customtkinter as ctk
from tkinter import ttk, messagebox
import tkinter as tk
from db_connection import get_db_connection

def show_warehouses_view(main_frame):
    # ניקוי המסך למניעת כפילויות תצוגה
    for widget in main_frame.winfo_children():
        widget.destroy()

    # --- כותרת עליונה ראשית ---
    header_label = ctk.CTkLabel(main_frame, text="מערך לוגיסטיקה ומחסני הרשת", font=("Segoe UI", 28, "bold"), text_color="#111827", anchor="e")
    header_label.pack(pady=(30, 2), padx=35, fill="x")
    
    sub_header = ctk.CTkLabel(main_frame, text="ניהול מרכזי של מחסני הפצה, צוותי ניהול, ואיתור מיקומי מוצרים על גבי המדפים", font=("Segoe UI", 14), text_color="#6B7280", anchor="e")
    sub_header.pack(pady=(0, 15), padx=35, fill="x")

    # --- מערכת הטאבים המרכזית (Tabview) ---
    tabview = ctk.CTkTabview(main_frame, corner_radius=12, fg_color="#F3F4F6", segmented_button_fg_color="#E5E7EB",
                             segmented_button_selected_color="#3B82F6", segmented_button_selected_hover_color="#2563EB",
                             segmented_button_unselected_color="#FFFFFF", segmented_button_unselected_hover_color="#F3F4F6",
                             text_color="#111827")
    tabview.pack(fill="both", expand=True, padx=35, pady=(0, 20))

    try:
        tabview._segmented_button.configure(font=("Segoe UI", 13, "bold"))
    except:
        pass

    # הגדרת הטאבים
    tab_warehouses = tabview.add("🏢  ניהול מחסנים וצוות מנהלים")
    tab_located = tabview.add("📦  איתור ומיקומי מוצרים במלאי")

    setup_combined_warehouses_tab(tab_warehouses)
    setup_located_products_tab(tab_located)


# =========================================================================
# 📑 טאב 1: מחסנים וצוות ניהול
# =========================================================================
def setup_combined_warehouses_tab(tab):
    # --- שורת חיפוש עליונה (חדש!) ---
    search_frame = ctk.CTkFrame(tab, fg_color="transparent")
    search_frame.pack(fill="x", pady=(5, 10))
    
    search_lbl = ctk.CTkLabel(search_frame, text="🔍  חיפוש לפי קוד מחסן או שם מנהל:", font=("Segoe UI", 12, "bold"), text_color="#374151")
    search_lbl.pack(side="right", padx=(10, 0))
    
    search_entry = ctk.CTkEntry(search_frame, placeholder_text="הקלידי קוד מחסן או שם מנהל לסינון...", font=("Segoe UI", 12), width=300, height=35, corner_radius=8, justify="right")
    search_entry.pack(side="right")
    
    search_entry.bind("<KeyRelease>", lambda event: refresh_combined_warehouses_data(tree, search_entry.get().strip()))

    # שורת פעולות עליונה - הוספות
    btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
    btn_frame.pack(fill="x", pady=(0, 10))
    
    add_mgr_btn = ctk.CTkButton(btn_frame, text="👤 מינוי מנהל למחסן קיים", font=("Segoe UI", 12, "bold"), fg_color="#3B82F6", hover_color="#2563EB", height=35, corner_radius=10, command=lambda: open_manager_add_modal(tree))
    add_mgr_btn.pack(side="left", padx=5)
    
    add_w_btn = ctk.CTkButton(btn_frame, text="🏢 הקמת מחסן חדש ברשת", font=("Segoe UI", 12, "bold"), fg_color="#10B981", hover_color="#059669", height=35, corner_radius=10, command=lambda: open_warehouse_modal(tree))
    add_w_btn.pack(side="right", padx=5)

    table_container = ctk.CTkFrame(tab, fg_color="#FFFFFF", corner_radius=12, border_color="#E5E7EB", border_width=1)
    table_container.pack(fill="both", expand=True, pady=5)
    table_container.grid_rowconfigure(0, weight=1)
    table_container.grid_columnconfigure(0, weight=0) 
    table_container.grid_columnconfigure(1, weight=1) 

    columns = ("manager", "address", "region", "warehouse_id")
    tree = ttk.Treeview(table_container, columns=columns, show="headings", style="Custom.Treeview")
    
    tree.heading("warehouse_id", text="קוד מחסן", anchor="center")
    tree.heading("region", text="אזור גיאוגרפי", anchor="center")
    tree.heading("address", text="כתובת המחסן", anchor="center")
    tree.heading("manager", text="מנהל מחסן אחראי", anchor="center")

    tree.column("warehouse_id", width=120, anchor="center", stretch=tk.YES)
    tree.column("region", width=160, anchor="center", stretch=tk.YES)
    tree.column("address", width=280, anchor="e", stretch=tk.YES)
    tree.column("manager", width=220, anchor="e", stretch=tk.YES)

    v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=v_scrollbar.set)
    
    v_scrollbar.grid(row=0, column=0, sticky="ns", pady=10, padx=(10, 0))
    tree.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    actions = ctk.CTkFrame(tab, fg_color="transparent")
    actions.pack(fill="x", pady=(10, 5))
    
    ctk.CTkButton(actions, text="✏️ עריכת מיקום מחסן", font=("Segoe UI", 12, "bold"), fg_color="#10B981", hover_color="#059669", height=35, corner_radius=10, command=lambda: edit_warehouse(tree)).pack(side="right", padx=5)
    ctk.CTkButton(actions, text="🗑️ סגירת מחסן מהרשת", font=("Segoe UI", 12, "bold"), fg_color="#EF4444", hover_color="#DC2626", height=35, corner_radius=10, command=lambda: delete_warehouse(tree)).pack(side="right", padx=25)
    
    ctk.CTkButton(actions, text="🗑️ ביטול מינוי מנהל", font=("Segoe UI", 12, "bold"), fg_color="#EF4444", hover_color="#DC2626", height=35, corner_radius=10, command=lambda: delete_manager(tree)).pack(side="left", padx=5)
    ctk.CTkButton(actions, text="✏️ החלפת מנהל מחסן", font=("Segoe UI", 12, "bold"), fg_color="#3B82F6", hover_color="#2563EB", height=35, corner_radius=10, command=lambda: edit_manager(tree)).pack(side="left", padx=5)

    refresh_combined_warehouses_data(tree)


def refresh_combined_warehouses_data(tree, search_query=""):
    for item in tree.get_children(): tree.delete(item)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        
        # תמיכה בסינון דינמי לפי קוד מחסן או שם מנהל
        if search_query:
            query = """
                SELECT w.WarehouseID, w.Region, w.Address, wm.WarehouseManager
                FROM WAREHOUSE w
                LEFT JOIN WAREHOUSEMANAGER wm ON w.WarehouseID = wm.WarehouseID
                WHERE CAST(w.WarehouseID AS TEXT) LIKE %s OR wm.WarehouseManager ILIKE %s
                ORDER BY w.WarehouseID ASC;
            """
            cursor.execute(query, (f"%{search_query}%", f"%{search_query}%"))
        else:
            query = """
                SELECT w.WarehouseID, w.Region, w.Address, wm.WarehouseManager
                FROM WAREHOUSE w
                LEFT JOIN WAREHOUSEMANAGER wm ON w.WarehouseID = wm.WarehouseID
                ORDER BY w.WarehouseID ASC;
            """
            cursor.execute(query)
            
        for row in cursor.fetchall():
            manager_val = row[3] if row[3] else "❌ טרם שויך מנהל"
            tree.insert("", "end", values=(manager_val, row[2], row[1], row[0]))
        cursor.close()
        conn.close()


def open_warehouse_modal(tree, edit_data=None):
    is_edit = edit_data is not None
    modal = ctk.CTkToplevel()
    modal.title("עריכת מחסן" if is_edit else "הקמת מחסן חדש")
    modal.geometry("400x320")
    
    try: modal.transient(tree.winfo_toplevel())
    except: pass
        
    modal.lift()
    modal.focus_force()
    modal.grab_set()

    ctk.CTkLabel(modal, text="🏢 פרטי מיקום מחסן", font=("Segoe UI", 16, "bold")).pack(pady=15)

    ctk.CTkLabel(modal, text="קוד מחסן מספר", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    id_entry = ctk.CTkEntry(modal, justify="right")
    id_entry.pack(fill="x", padx=40, pady=2)
    if is_edit:
        id_entry.insert(0, edit_data[3])
        id_entry.configure(state="disabled", fg_color="#E5E7EB")

    ctk.CTkLabel(modal, text="אזור גיאוגרפי בארץ", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    region_entry = ctk.CTkEntry(modal, justify="right")
    region_entry.pack(fill="x", padx=40, pady=2)
    if is_edit: region_entry.insert(0, edit_data[2])

    ctk.CTkLabel(modal, text="כתובת פיזית מלאה", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    addr_entry = ctk.CTkEntry(modal, justify="right")
    addr_entry.pack(fill="x", padx=40, pady=2)
    if is_edit: addr_entry.insert(0, edit_data[1])

    def save():
        w_id = id_entry.get().strip()
        reg = region_entry.get().strip()
        addr = addr_entry.get().strip()
        if not w_id or not reg or not addr:
            messagebox.showwarning("שדות חסרים", "אנא מלאי את כל השדות.")
            return
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                if is_edit:
                    cursor.execute("UPDATE WAREHOUSE SET Region=%s, Address=%s WHERE WarehouseID=%s;", (reg, addr, int(w_id)))
                else:
                    cursor.execute("INSERT INTO WAREHOUSE (WarehouseID, Region, Address) VALUES (%s, %s, %s);", (int(w_id), reg, addr))
                conn.commit()
                modal.destroy()
                refresh_combined_warehouses_data(tree)
            except Exception as e:
                messagebox.showerror("שגיאה", f"הפעולה נכשלה:\n{e}")
            finally:
                cursor.close()
                conn.close()

    ctk.CTkButton(modal, text="💾 שמור מחסן", fg_color="#10B981", hover_color="#059669", height=38, corner_radius=8, command=save).pack(pady=20)

def edit_warehouse(tree):
    sel = tree.selection()
    if not sel: return messagebox.showwarning("בחירה חובה", "אנא בחרי שורה מהטבלה לצורך עריכה.")
    open_warehouse_modal(tree, tree.item(sel[0], 'values'))

def delete_warehouse(tree):
    sel = tree.selection()
    if not sel: return messagebox.showwarning("בחירה חובה", "אנא בחרי מחסן למחיקה.")
    vals = tree.item(sel[0], 'values')
    w_id = vals[3]
    w_name = vals[2]
    if messagebox.askyesno("אישור סגירה", f"האם את בטוחה שברצונך לסגור ולמחוק את מחסן מספר {w_id}?"):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM WAREHOUSE WHERE WarehouseID = %s;", (int(w_id),))
                conn.commit()
                refresh_combined_warehouses_data(tree)
            except Exception as e:
                error_msg = str(e)
                # הודעה ידידותית ומפורטת למשתמש במקרה של תלות במפתח זר כנדרש!
                if "foreign key constraint" in error_msg or "is still referenced" in error_msg:
                    messagebox.showerror(
                        "לא ניתן למחוק - מחסן פעיל", 
                        f"פעולת המחיקה עבור מחסן מספר {w_id} נחסמה באופן מאובטח.\n\n"
                        f"💡 מדוע זה קרה?\n"
                        f"בסיס הנתונים מזהה שקיימים כרגע במערכת נתונים התלויים ישירות במחסן זה (מוצרים שממוקמים במעברים שלו, או מנהל הרשום בו).\n\n"
                        f"🛠️ מה צריך לעשות עכשיו?\n"
                        f"יש לפנות תחילה את כל המוצרים מהמלאי המשויכים למחסן זה (בטאב איתור מוצרים) ולבטל את מינוי המנהל, ורק אז ניתן יהיה למחוק את המחסן."
                    )
                else:
                    messagebox.showerror("שגיאה במחיקה", f"פעולת המחיקה נכשלה:\n{error_msg}")
            finally:
                cursor.close()
                conn.close()


def open_manager_add_modal(tree):
    warehouses_list = []
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT WarehouseID, Region FROM WAREHOUSE ORDER BY WarehouseID ASC;")
            for row in cursor.fetchall():
                warehouses_list.append(f"{row[0]} - {row[1]}")
            cursor.close()
            conn.close()
    except Exception as e:
        messagebox.showerror("שגיאת מסד נתונים", f"נכשלה טעינת המחסנים:\n{e}")
        return

    if not warehouses_list: warehouses_list = ["אין מחסנים קיימים ברשת"]

    modal = ctk.CTkToplevel()
    modal.title("מינוי מנהל מחסן")
    modal.geometry("400x340")
    
    try: modal.transient(tree.winfo_toplevel())
    except: pass

    modal.lift()
    modal.focus_force()
    modal.grab_set()

    ctk.CTkLabel(modal, text="👤 מינוי מנהל מחסן חדש", font=("Segoe UI", 16, "bold")).pack(pady=15)
    ctk.CTkLabel(modal, text="בחרי מחסן יעד למינוי", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    w_option = ctk.CTkOptionMenu(modal, values=warehouses_list)
    w_option.pack(fill="x", padx=40, pady=2)

    ctk.CTkLabel(modal, text="שם מנהל המחסן", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    name_entry = ctk.CTkEntry(modal, justify="right")
    name_entry.pack(fill="x", padx=40, pady=2)

    def save():
        selected_w = w_option.get()
        mgr_name = name_entry.get().strip()
        if selected_w.startswith("אין") or not mgr_name:
            messagebox.showwarning("שגיאה", "אנא מלאי את כל השדות בצורה תקינה.")
            return
        w_id = int(selected_w.split(" - ")[0])
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO WAREHOUSEMANAGER (WarehouseID, WarehouseManager) VALUES (%s, %s);", (w_id, mgr_name))
                conn.commit()
                modal.destroy()
                refresh_combined_warehouses_data(tree)
            except Exception as e:
                messagebox.showerror("שגיאה", f"לא ניתן למנות מנהל זה (ייתכן והמחסן כבר מנוהל):\n{e}")
            finally:
                cursor.close()
                conn.close()

    # תוקן הטקסט ל-"בצע מינוי" הידידותי והנכון כפי שביקשת
    ctk.CTkButton(modal, text="✅ בצע מינוי", fg_color="#10B981", hover_color="#059669", height=38, corner_radius=8, command=save).pack(pady=20)

def edit_manager(tree):
    sel = tree.selection()
    if not sel: return messagebox.showwarning("בחירה חובה", "אנא בחרי שורה מהטבלה לצורך החלפת מנהל.")
    vals = tree.item(sel[0], 'values')
    w_id = vals[3]
    old_mgr = vals[0]
    
    modal = ctk.CTkToplevel()
    modal.title("החלפת מנהל מחסן")
    modal.geometry("400x260")
    
    try: modal.transient(tree.winfo_toplevel())
    except: pass
        
    modal.lift()
    modal.focus_force()
    modal.grab_set()

    ctk.CTkLabel(modal, text=f"✏️ עדכון מנהל למחסן מספר {w_id}", font=("Segoe UI", 15, "bold")).pack(pady=15)
    ctk.CTkLabel(modal, text="שם המנהל החדש", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    name_entry = ctk.CTkEntry(modal, justify="right")
    name_entry.pack(fill="x", padx=40, pady=2)
    if old_mgr != "❌ טרם שויך מנהל": name_entry.insert(0, old_mgr)

    def save():
        new_mgr = name_entry.get().strip()
        if not new_mgr: return messagebox.showwarning("קלט חסר", "אנא הזיני את שם המנהל החדש.")
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM WAREHOUSEMANAGER WHERE WarehouseID=%s;", (int(w_id),))
            cursor.execute("INSERT INTO WAREHOUSEMANAGER (WarehouseID, WarehouseManager) VALUES (%s, %s);", (int(w_id), new_mgr))
            conn.commit()
            cursor.close()
            conn.close()
            modal.destroy()
            refresh_combined_warehouses_data(tree)

    ctk.CTkButton(modal, text="💾 עדכן מינוי", fg_color="#10B981", hover_color="#059669", height=38, corner_radius=8, command=save).pack(pady=20)

def delete_manager(tree):
    sel = tree.selection()
    if not sel: return messagebox.showwarning("בחירה חובה", "אנא בחרי שורה לביטול המינוי.")
    vals = tree.item(sel[0], 'values')
    mgr_name = vals[0]
    w_id = vals[3]
    if mgr_name == "❌ טרם שויך מנהל": return messagebox.showwarning("שגיאה", "למחסן זה אין מנהל משויך כרגע.")
    
    if messagebox.askyesno("אישור ביטול", f"האם לבטל את מינויו של {mgr_name} כמנהל מחסן {w_id}?"):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM WAREHOUSEMANAGER WHERE WarehouseManager=%s AND WarehouseID=%s;", (mgr_name, int(w_id)))
            conn.commit()
            cursor.close()
            conn.close()
            refresh_combined_warehouses_data(tree)


# =========================================================================
# 📑 טאב 2: איתור ומיקומי מוצרים במלאי (LOCATED)
# =========================================================================
def setup_located_products_tab(tab):
    # --- שורת חיפוש עליונה כפולה (חדש!) ---
    search_frame = ctk.CTkFrame(tab, fg_color="transparent")
    search_frame.pack(fill="x", pady=(5, 10))
    
    search_lbl = ctk.CTkLabel(search_frame, text="🔍  חיפוש לפי קוד מחסן או קוד מוצר:", font=("Segoe UI", 12, "bold"), text_color="#374151")
    search_lbl.pack(side="right", padx=(10, 0))
    
    search_entry = ctk.CTkEntry(search_frame, placeholder_text="הקלידי קוד מחסן או קוד מוצר לסינון...", font=("Segoe UI", 12), width=320, height=35, corner_radius=8, justify="right")
    search_entry.pack(side="right")
    
    search_entry.bind("<KeyRelease>", lambda event: refresh_located_data(tree, search_entry.get().strip()))

    # שורת פעולות
    btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
    btn_frame.pack(fill="x", pady=(0, 10))
    add_btn = ctk.CTkButton(btn_frame, text="➕ הצבת מוצר חדש במחסן", font=("Segoe UI", 12, "bold"), fg_color="#10B981", hover_color="#059669", height=35, corner_radius=10, command=lambda: open_located_modal(tree))
    add_btn.pack(side="right", padx=5)

    table_container = ctk.CTkFrame(tab, fg_color="#FFFFFF", corner_radius=12, border_color="#E5E7EB", border_width=1)
    table_container.pack(fill="both", expand=True, pady=5)
    table_container.grid_rowconfigure(0, weight=1)
    table_container.grid_columnconfigure(0, weight=0)
    table_container.grid_columnconfigure(1, weight=1)

    # --- תוקן: עמודות מופרדות לקוד מחסן וכתובת מחסן במקום העמודה הישנה המאוחדת ---
    columns = ("shelf_nb", "aisle_nb", "warehouse_addr", "warehouse_id", "product_name", "product_id")
    tree = ttk.Treeview(table_container, columns=columns, show="headings", style="Custom.Treeview")
    
    tree.heading("product_id", text="קוד מוצר", anchor="center")
    tree.heading("product_name", text="שם מוצר בקטלוג", anchor="center")
    tree.heading("warehouse_id", text="קוד מחסן", anchor="center")
    tree.heading("warehouse_addr", text="כתובת המחסן", anchor="center")
    tree.heading("aisle_nb", text="מספר מעבר", anchor="center")
    tree.heading("shelf_nb", text="מספר מדף", anchor="center")

    tree.column("product_id", width=100, anchor="center", stretch=tk.YES)
    tree.column("product_name", width=200, anchor="e", stretch=tk.YES)
    tree.column("warehouse_id", width=100, anchor="center", stretch=tk.YES) # מוצג נקי קוד בלבד כפי שביקשת
    tree.column("warehouse_addr", width=220, anchor="e", stretch=tk.YES) # עמודת הכתובת החדשה והמרווחת
    tree.column("aisle_nb", width=110, anchor="center", stretch=tk.YES)
    tree.column("shelf_nb", width=110, anchor="center", stretch=tk.YES)

    v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=v_scrollbar.set)
    
    v_scrollbar.grid(row=0, column=0, sticky="ns", pady=10, padx=(10, 0))
    tree.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    actions = ctk.CTkFrame(tab, fg_color="transparent")
    actions.pack(fill="x", pady=(10, 5))
    ctk.CTkButton(actions, text="🗑️ פינוי מהמלאי במחסן", font=("Segoe UI", 12, "bold"), fg_color="#EF4444", hover_color="#DC2626", height=35, corner_radius=10, command=lambda: delete_located(tree)).pack(side="right", padx=5)
    ctk.CTkButton(actions, text="✏️ עדכון מעבר/מדף", font=("Segoe UI", 12, "bold"), fg_color="#3B82F6", hover_color="#2563EB", height=35, corner_radius=10, command=lambda: edit_located(tree)).pack(side="right", padx=5)

    refresh_located_data(tree)


def refresh_located_data(tree, search_query=""):
    for item in tree.get_children(): tree.delete(item)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        
        # תמיכה בחיפוש לפי קוד מחסן או קוד מוצר
        if search_query:
            query = """
                SELECT l.ProductID, p.ProductName, l.WarehouseID, w.Address, l.AisleNb, l.ShelfNb
                FROM LOCATED l
                JOIN PRODUCT p ON l.ProductID = p.ProductID
                JOIN WAREHOUSE w ON l.WarehouseID = w.WarehouseID
                WHERE CAST(l.WarehouseID AS TEXT) LIKE %s OR CAST(l.ProductID AS TEXT) LIKE %s
                ORDER BY l.WarehouseID ASC, l.AisleNb ASC;
            """
            cursor.execute(query, (f"%{search_query}%", f"%{search_query}%"))
        else:
            query = """
                SELECT l.ProductID, p.ProductName, l.WarehouseID, w.Address, l.AisleNb, l.ShelfNb
                FROM LOCATED l
                JOIN PRODUCT p ON l.ProductID = p.ProductID
                JOIN WAREHOUSE w ON l.WarehouseID = w.WarehouseID
                ORDER BY l.WarehouseID ASC, l.AisleNb ASC;
            """
            cursor.execute(query)
            
        for row in cursor.fetchall():
            # מוזן בדיוק לפי העמודות המופרדות החדשות: shelf, aisle, address, w_id, prod_name, prod_id
            tree.insert("", "end", values=(row[5], row[4], row[3], row[2], row[1], row[0]))
        cursor.close()
        conn.close()


def get_warehouses_and_products_lists():
    warehouses = []
    products = []
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT WarehouseID, Region FROM WAREHOUSE ORDER BY WarehouseID ASC;")
        for r in cursor.fetchall(): warehouses.append(f"{r[0]} - {r[1]}")
        cursor.execute("SELECT ProductID, ProductName FROM PRODUCT ORDER BY ProductID ASC;")
        for r in cursor.fetchall(): products.append(f"{r[0]} - {r[1]}")
        cursor.close()
        conn.close()
    return warehouses, products


def open_located_modal(tree, edit_data=None):
    is_edit = edit_data is not None
    modal = ctk.CTkToplevel()
    modal.title("עדכון מיקום מלאי" if is_edit else "הצבת מוצר חדש במלאי")
    modal.geometry("420x460")
    
    try: modal.transient(tree.winfo_toplevel())
    except: pass
        
    modal.lift()
    modal.focus_force()
    modal.grab_set()

    ctk.CTkLabel(modal, text="📦 פרטי מיקום מוצר במחסן", font=("Segoe UI", 16, "bold")).pack(pady=15)

    warehouses_list, products_list = get_warehouses_and_products_lists()

    ctk.CTkLabel(modal, text="בחרי מוצר מהקטלוג", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    p_option = ctk.CTkOptionMenu(modal, values=products_list if products_list else ["אין מוצרים"])
    p_option.pack(fill="x", padx=40, pady=2)

    ctk.CTkLabel(modal, text="בחרי מחסן לוגיסטי לייעוד", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    w_option = ctk.CTkOptionMenu(modal, values=warehouses_list if warehouses_list else ["אין מחסנים"])
    w_option.pack(fill="x", padx=40, pady=2)

    if is_edit:
        # שליפת הנתונים לפי האינדקסים החדשים: קוד מוצר נמצא באינדקס 5, קוד מחסן באינדקס 3
        for prod_str in products_list:
            if prod_str.startswith(str(edit_data[5]) + " -"): p_option.set(prod_str)
        p_option.configure(state="disabled")
        
        for w_str in warehouses_list:
            if w_str.startswith(str(edit_data[3]) + " -"): w_option.set(w_str)
        w_option.configure(state="disabled")

    ctk.CTkLabel(modal, text="מספר מעבר אחסון", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    aisle_entry = ctk.CTkEntry(modal, justify="right")
    aisle_entry.pack(fill="x", padx=40, pady=2)
    if is_edit: aisle_entry.insert(0, edit_data[1])

    ctk.CTkLabel(modal, text="מספר מדף אחסון", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    shelf_entry = ctk.CTkEntry(modal, justify="right")
    shelf_entry.pack(fill="x", padx=40, pady=2)
    if is_edit: shelf_entry.insert(0, edit_data[0])

    def save():
        try:
            p_id = int(p_option.get().split(" - ")[0])
            w_id = int(w_option.get().split(" - ")[0])
            aisle = int(aisle_entry.get().strip())
            shelf = int(shelf_entry.get().strip())
        except:
            messagebox.showwarning("קלט שגוי", "אנא ודאי שהזנת מספרים חיוביים תקינים.")
            return

        if aisle <= 0 or shelf <= 0:
            messagebox.showwarning("ערך שגוי", "המספרים חייבים להיות גדולים מ-0!")
            return

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                if is_edit:
                    cursor.execute("UPDATE LOCATED SET AisleNb=%s, ShelfNb=%s WHERE ProductID=%s AND WarehouseID=%s;", (aisle, shelf, p_id, w_id))
                else:
                    cursor.execute("INSERT INTO LOCATED (ProductID, WarehouseID, AisleNb, ShelfNb) VALUES (%s, %s, %s, %s);", (p_id, w_id, aisle, shelf))
                conn.commit()
                modal.destroy()
                refresh_located_data(tree)
            except Exception as e:
                messagebox.showerror("שגיאה", f"ההצבה נכשלה. ייתכן והמוצר כבר משויך למחסן זה:\n{e}")
            finally:
                cursor.close()
                conn.close()

    ctk.CTkButton(modal, text="💾 שמור מיקום מלאי", fg_color="#10B981", hover_color="#059669", height=38, corner_radius=8, command=save).pack(pady=20)


def edit_located(tree):
    sel = tree.selection()
    if not sel: return messagebox.showwarning("בחירה חובה", "אנא בחרי מוצר לצורך שינוי מיקומו.")
    open_located_modal(tree, tree.item(sel[0], 'values'))


def delete_located(tree):
    sel = tree.selection()
    if not sel: return messagebox.showwarning("בחירה חובה", "אנא בחרי שורה לפינוי מהמלאי.")
    vals = tree.item(sel[0], 'values')
    p_id = vals[5] # אינדקס 5 עבור קוד מוצר
    w_id = vals[3] # אינדקס 3 עבור קוד מחסן
    p_name = vals[4]
    
    if messagebox.askyesno("אישור פינוי", f"האם את בטוחה שברצונך לפנות את המוצר מספר '{p_id}' ממחסן מספר {w_id}?"):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM LOCATED WHERE ProductID=%s AND WarehouseID=%s;", (int(p_id), int(w_id)))
                conn.commit()
                refresh_located_data(tree)
            except Exception as e:
                messagebox.showerror("שגיאה בפינוי", f"פעולת הפינוי נכשלה:\n{e}")
            finally:
                cursor.close()
                conn.close()