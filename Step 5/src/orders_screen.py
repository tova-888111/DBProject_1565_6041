import customtkinter as ctk
from tkinter import ttk, messagebox
import tkinter as tk
from db_connection import get_db_connection
from datetime import datetime

def show_orders_view(main_frame):
    # ניקוי המסך למניעת כפילויות תצוגה
    for widget in main_frame.winfo_children():
        widget.destroy()

    # --- כותרת עליונה ראשית ---
    header_label = ctk.CTkLabel(main_frame, text="מערך הזמנות, לוגיסטיקה והפצה", font=("Segoe UI", 28, "bold"), text_color="#111827", anchor="e")
    header_label.pack(pady=(30, 2), padx=35, fill="x")
    
    sub_header = ctk.CTkLabel(main_frame, text="ניהול הזמנות סניפים, מעקב סטטוסי משלוח, פיקוח על צי רכבי ההפצה וחברות המשלוחים", font=("Segoe UI", 14), text_color="#6B7280", anchor="e")
    sub_header.pack(pady=(0, 15), padx=35, fill="x")

    # --- מערכת הטאבים המרכזית (Tabview) ---
    tabview = ctk.CTkTabview(main_frame, corner_radius=12, fg_color="#F3F4F6", segmented_button_fg_color="#E5E7EB",
                             segmented_button_selected_color="#3B82F6", segmented_button_selected_hover_color="#2563EB",
                             segmented_button_unselected_color="#FFFFFF", segmented_button_unselected_hover_color="#F3F4F6",
                             text_color="#111827")
    tabview.pack(fill="both", expand=True, padx=35, pady=(0, 20))

    try:
        tabview._segmented_button.configure(font=("Segoe UI", 14, "bold"), height=45)
    except:
        pass

    tab_orders = tabview.add("🛒  ניהול הזמנות והפצה")
    tab_trucks = tabview.add("🚛  צי משאיות ונהגים")
    tab_companies = tabview.add("🏢  חברות הפצה ואזורי שירות")

    setup_orders_tab(tab_orders)
    setup_trucks_tab(tab_trucks)
    setup_companies_tab(tab_companies)


# =========================================================================
# 📑 טאב 1: ניהול הזמנות והפצה ("ORDER" + CONTAINS)
# =========================================================================
def setup_orders_tab(tab):
    search_frame = ctk.CTkFrame(tab, fg_color="transparent")
    search_frame.pack(fill="x", pady=(5, 12))
    search_frame.grid_columnconfigure(0, weight=1)
    
    search_lbl = ctk.CTkLabel(search_frame, text="🔍  מסנני חיפוש", font=("Segoe UI", 13, "bold"), text_color="#374151")
    search_lbl.grid(row=0, column=3, padx=(10, 15), sticky="e")
    
    search_id_entry = ctk.CTkEntry(search_frame, placeholder_text="לפי קוד הזמנה מדויק", font=("Segoe UI", 12), width=160, height=35, corner_radius=8, justify="right")
    search_id_entry.grid(row=0, column=2, padx=6, sticky="e")
    
    search_store_entry = ctk.CTkEntry(search_frame, placeholder_text="לפי קוד סניף מדויק", font=("Segoe UI", 12), width=160, height=35, corner_radius=8, justify="right")
    search_store_entry.grid(row=0, column=1, padx=6, sticky="e")

    search_id_entry.bind("<KeyRelease>", lambda event: refresh_orders_data(tree, search_id_entry.get().strip(), search_store_entry.get().strip()))
    search_store_entry.bind("<KeyRelease>", lambda event: refresh_orders_data(tree, search_id_entry.get().strip(), search_store_entry.get().strip()))

    btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
    btn_frame.pack(fill="x", pady=(0, 10))
    
    ctk.CTkButton(btn_frame, text="📦 ניהול תכולת הזמנה", font=("Segoe UI", 12, "bold"), fg_color="#3B82F6", hover_color="#2563EB", height=35, corner_radius=10, command=lambda: open_contains_manager_modal(tree)).pack(side="left", padx=5)
    ctk.CTkButton(btn_frame, text="➕ יצירת הזמנת הפצה חדשה", font=("Segoe UI", 12, "bold"), fg_color="#10B981", hover_color="#059669", height=35, corner_radius=10, command=lambda: open_order_modal(tree)).pack(side="right", padx=5)

    table_container = ctk.CTkFrame(tab, fg_color="#FFFFFF", corner_radius=12, border_color="#E5E7EB", border_width=1)
    table_container.pack(fill="both", expand=True, pady=5)
    table_container.grid_rowconfigure(0, weight=1)
    table_container.grid_columnconfigure(0, weight=0)
    table_container.grid_columnconfigure(1, weight=1)

    columns = ("status", "driver_id", "store_info", "order_date", "price", "order_id", "hidden_store_id")
    tree = ttk.Treeview(table_container, columns=columns, show="headings", style="Custom.Treeview")
    
    tree.heading("order_id", text="קוד הזמנה", anchor="center")
    tree.heading("price", text="עלות כוללת", anchor="center")
    tree.heading("order_date", text="תאריך יצירה", anchor="center")
    tree.heading("store_info", text="סניף יעד מבוקש", anchor="center")
    tree.heading("driver_id", text="קוד נהג/משאית", anchor="center")
    tree.heading("status", text="סטטוס הפצה", anchor="center")

    tree.column("order_id", width=100, anchor="center", stretch=tk.NO)
    tree.column("price", width=120, anchor="center", stretch=tk.NO)
    tree.column("order_date", width=150, anchor="center", stretch=tk.NO)
    tree.column("store_info", width=250, anchor="e", stretch=tk.NO)
    tree.column("driver_id", width=120, anchor="center", stretch=tk.NO)
    tree.column("status", width=140, anchor="center", stretch=tk.NO)
    tree.column("hidden_store_id", width=0, stretch=tk.NO)

    v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=tree.yview)
    h_scrollbar = ttk.Scrollbar(table_container, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
    
    h_scrollbar.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=(0, 10))
    v_scrollbar.grid(row=0, column=0, sticky="ns", pady=10, padx=(10, 0))
    tree.grid(row=0, column=1, sticky="nsew", padx=10, pady=(10, 2))

    actions = ctk.CTkFrame(tab, fg_color="transparent")
    actions.pack(fill="x", pady=(15, 10))
    ctk.CTkButton(actions, text="✏️ עדכון סטטוס/פרטי הזמנה", font=("Segoe UI", 13, "bold"), fg_color="#10B981", hover_color="#059669", width=180, height=38, corner_radius=10, command=lambda: edit_order(tree)).pack(side="right", padx=5)
    ctk.CTkButton(actions, text="🗑️ ביטול הזמנה מהמערכת", font=("Segoe UI", 13, "bold"), fg_color="#EF4444", hover_color="#DC2626", width=180, height=38, corner_radius=10, command=lambda: delete_order(tree)).pack(side="right", padx=25)

    refresh_orders_data(tree)


def refresh_orders_data(tree, search_id="", search_store=""):
    for item in tree.get_children(): tree.delete(item)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
            SELECT o.OrderId, o.Price, o.OrderDate, s.StoreName, o.DriverID, o.Status, o.StoreID
            FROM "ORDER" o
            JOIN STORE s ON o.StoreID = s.StoreID
            WHERE 1=1
        """
        params = []
        if search_id and search_id.isdigit():
            query += " AND o.OrderId = %s"
            params.append(int(search_id))
        if search_store and search_store.isdigit():
            query += " AND o.StoreID = %s"
            params.append(int(search_store))
            
        query += " ORDER BY o.OrderId DESC;"
        cursor.execute(query, tuple(params))
        for row in cursor.fetchall():
            o_date = row[2].strftime('%Y-%m-%d %H:%M') if row[2] else "-"
            tree.insert("", "end", values=(row[5], row[4], f"סניף {row[6]} - {row[3]}", o_date, f"₪{row[1]:,.2f}", row[0], row[6]))
        cursor.close()
        conn.close()


def open_order_modal(tree, edit_data=None):
    is_edit = edit_data is not None
    modal = ctk.CTkToplevel()
    modal.title("עריכת הזמנה" if is_edit else "הזמנת הפצה חדשה")
    modal.geometry("420x460")
    try: modal.transient(tree.winfo_toplevel())
    except: pass
    modal.grab_set()

    ctk.CTkLabel(modal, text="🛒 פרטי הזמנת רשת", font=("Segoe UI", 16, "bold")).pack(pady=15)

    stores_list = []
    trucks_list = []
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT StoreID, StoreName FROM STORE ORDER BY StoreID ASC;")
        for r in cursor.fetchall(): stores_list.append(f"{r[0]} - {r[1]}")
        cursor.execute("SELECT DriverID, LicensePlate FROM TRUCK WHERE Active = 1 ORDER BY DriverID ASC;")
        for r in cursor.fetchall(): trucks_list.append(f"{r[0]} - לוחית {r[1]}")
        cursor.close()
        conn.close()

    ctk.CTkLabel(modal, text="קוד הזמנה מספר", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    id_entry = ctk.CTkEntry(modal, justify="right")
    id_entry.pack(fill="x", padx=40, pady=2)
    if is_edit:
        id_entry.insert(0, edit_data[5])
        id_entry.configure(state="disabled", fg_color="#E5E7EB")

    ctk.CTkLabel(modal, text="עלות הזמנה כוללת", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    price_entry = ctk.CTkEntry(modal, justify="right")
    price_entry.pack(fill="x", padx=40, pady=2)
    if is_edit: price_entry.insert(0, edit_data[4].replace("₪", "").replace(",", ""))

    ctk.CTkLabel(modal, text="סניף יעד מזמין", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    store_option = ctk.CTkOptionMenu(modal, values=stores_list)
    store_option.pack(fill="x", padx=40, pady=2)
    if is_edit:
        for s_str in stores_list:
            if s_str.startswith(str(edit_data[6]) + " -"): store_option.set(s_str)

    ctk.CTkLabel(modal, text="נהג/משאית הפצה מיועדת", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    truck_option = ctk.CTkOptionMenu(modal, values=trucks_list)
    truck_option.pack(fill="x", padx=40, pady=2)
    if is_edit:
        for t_str in trucks_list:
            if t_str.startswith(str(edit_data[1]) + " -"): truck_option.set(t_str)

    ctk.CTkLabel(modal, text="סטטוס הפצה נוכחי", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    status_option = ctk.CTkOptionMenu(modal, values=["PENDING", "IN TRANSIT", "DELIVERED", "CANCELLED"])
    status_option.pack(fill="x", padx=40, pady=2)
    if is_edit: status_option.set(edit_data[0])

    def save():
        o_id = id_entry.get().strip()
        price = price_entry.get().strip()
        s_sel = store_option.get()
        t_sel = truck_option.get()
        stat = status_option.get()

        if not o_id or not price:
            messagebox.showwarning("שדות חסרים", "אנא מלאי את כל השדות.")
            return

        try:
            price_val = float(price)
            if price_val < 0: raise ValueError()
        except ValueError:
            messagebox.showwarning("קלט שגוי", "העלות חייבת להיות מספר חיובי.")
            return

        s_id = int(s_sel.split(" - ")[0])
        t_id = int(t_sel.split(" - ")[0])

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                if is_edit:
                    cursor.execute("""
                        UPDATE "ORDER" 
                        SET Price=%s, StoreID=%s, DriverID=%s, Status=%s 
                        WHERE OrderId=%s;
                    """, (price_val, s_id, t_id, stat, int(o_id)))
                else:
                    cursor.execute("""
                        INSERT INTO "ORDER" (OrderId, Price, StoreID, DriverID, Status, OrderDate) 
                        VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP);
                    """, (int(o_id), price_val, s_id, t_id, stat))
                conn.commit()
                modal.destroy()
                refresh_orders_data(tree)
            except Exception as e:
                messagebox.showerror("שגיאה", f"הפעולה נכשלה, ודאי שקוד ההזמנה אינו כפול:\n{e}")
            finally:
                cursor.close()
                conn.close()

    ctk.CTkButton(modal, text="שמור", fg_color="#10B981", hover_color="#059669", height=38, corner_radius=8, command=save).pack(pady=15)

def edit_order(tree):
    sel = tree.selection()
    if not sel: return messagebox.showwarning("בחירה חובה", "אנא בחרי שורה מהטבלה לעריכה.")
    open_order_modal(tree, tree.item(sel[0], 'values'))

def delete_order(tree):
    sel = tree.selection()
    if not sel: return messagebox.showwarning("בחירה חובה", "אנא בחרי הזמנה לביטול.")
    o_id = tree.item(sel[0], 'values')[5]
    if messagebox.askyesno("אישור ביטול", f"האם את בטוחה שברצונך למחוק לחלוטין את הזמנה מספר {o_id} מהמערכת?"):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute('DELETE FROM "ORDER" WHERE OrderId = %s;', (int(o_id),))
                conn.commit()
                refresh_orders_data(tree)
            except Exception as e:
                messagebox.showerror("חסימת מחיקה", f"לא ניתן למחוק הזמנה זו.\n\nהסיבה: קיימים פריטים תלויים מקושרים בתוך ההזמנה. יש לרוקן את תכולת ההזמנה תחילה.")
            finally:
                cursor.close()
                conn.close()


# --- תת מערך CRUD מלא עבור טבלת CONTAINS (תכולת הזמנה) ---
def open_contains_manager_modal(tree):
    sel = tree.selection()
    if not sel: return messagebox.showwarning("בחירה חובה", "אנא בחרי שורת הזמנה מהטבלה כדי לנהל את תכולת המוצרים שלה.")
    o_id = tree.item(sel[0], 'values')[5]

    modal = ctk.CTkToplevel()
    modal.title(f"ניהול פריטי הזמנה מספר {o_id}")
    modal.geometry("540x500")
    modal.grab_set()

    ctk.CTkLabel(modal, text=f"📦 ניהול תכולת מוצרים - הזמנה {o_id}", font=("Segoe UI", 15, "bold")).pack(pady=10)

    # רשימת מוצרים נפתחת
    products_list = []
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ProductID, ProductName FROM PRODUCT ORDER BY ProductID ASC;")
        for r in cursor.fetchall(): products_list.append(f"{r[0]} - {r[1]}")
        cursor.close()
        conn.close()

    add_frame = ctk.CTkFrame(modal, fg_color="transparent")
    add_frame.pack(fill="x", padx=20, pady=5)
    
    qty_entry = ctk.CTkEntry(add_frame, placeholder_text="כמות", width=80, justify="right")
    qty_entry.pack(side="left", padx=5)
    
    prod_option = ctk.CTkOptionMenu(add_frame, values=products_list, width=220)
    prod_option.pack(side="left", padx=5)

    def add_item():
        try:
            p_id = int(prod_option.get().split(" - ")[0])
            qty = int(qty_entry.get().strip())
        except:
            return messagebox.showwarning("קלט שגוי", "אנא הזיני כמות תקינה.")
        if qty <= 0: return messagebox.showwarning("ערך שגוי", "הכמות חייבת להיות גדולה מ-0.")

        conn_sub = get_db_connection()
        if conn_sub:
            cursor_sub = conn_sub.cursor()
            try:
                cursor_sub.execute('INSERT INTO CONTAINS (OrderId, ProductID, Quantity) VALUES (%s, %s, %s);', (int(o_id), p_id, qty))
                conn_sub.commit()
                refresh_contains_table(c_tree, o_id)
                qty_entry.delete(0, tk.END)
            except:
                messagebox.showerror("כפילות", "מוצר זה כבר קיים בהזמנה. השתמשי באפשרות מחיקה ועדכון מחדש.")
            finally:
                cursor_sub.close()
                conn_sub.close()

    ctk.CTkButton(add_frame, text="הוסף פריט", fg_color="#10B981", hover_color="#059669", width=90, command=add_item).pack(side="right", padx=5)

    # טבלת תצוגה פנימית
    c_container = ctk.CTkFrame(modal, fg_color="#FFFFFF", corner_radius=8, border_color="#E5E7EB", border_width=1)
    c_container.pack(fill="both", expand=True, padx=20, pady=10)
    c_container.grid_rowconfigure(0, weight=1)
    c_container.grid_columnconfigure(0, weight=1)

    c_tree = ttk.Treeview(c_container, columns=("qty", "p_name", "p_id"), show="headings", style="Custom.Treeview")
    c_tree.heading("p_id", text="קוד מוצר")
    c_tree.heading("p_name", text="שם מוצר")
    c_tree.heading("qty", text="כמות מוזמנת")
    c_tree.column("p_id", width=90, anchor="center")
    c_tree.column("p_name", width=220, anchor="e")
    c_tree.column("qty", width=110, anchor="center")
    c_tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

    def delete_item():
        c_sel = c_tree.selection()
        if not c_sel: return messagebox.showwarning("בחירה חובה", "בחרי פריט למחיקה.")
        p_id = c_tree.item(c_sel[0], 'values')[2]
        conn_del = get_db_connection()
        if conn_del:
            cursor_del = conn_del.cursor()
            cursor_del.execute('DELETE FROM CONTAINS WHERE OrderId=%s AND ProductID=%s;', (int(o_id), int(p_id)))
            conn_del.commit()
            cursor_del.close()
            conn_del.close()
            refresh_contains_table(c_tree, o_id)

    ctk.CTkButton(modal, text="🗑️ הסר פריט נבחר מההזמנה", fg_color="#EF4444", hover_color="#DC2626", height=35, command=delete_item).pack(pady=(0, 15))
    refresh_contains_table(c_tree, o_id)

def refresh_contains_table(tree, order_id):
    for item in tree.get_children(): tree.delete(item)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute('SELECT c.Quantity, p.ProductName, c.ProductID FROM CONTAINS c JOIN PRODUCT p ON c.ProductID = p.ProductID WHERE c.OrderId = %s;', (int(order_id),))
        for row in cursor.fetchall():
            tree.insert("", "end", values=(row[0], row[1], row[2]))
        cursor.close()
        conn.close()


# =========================================================================
# 📑 טאב 2: צי משאיות ונהגים (TRUCK)
# =========================================================================
def setup_trucks_tab(tab):
    btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
    btn_frame.pack(fill="x", pady=(10, 10))
    ctk.CTkButton(btn_frame, text="➕ רישום רכב/נהג חדש", font=("Segoe UI", 12, "bold"), fg_color="#10B981", hover_color="#059669", height=35, corner_radius=10, command=lambda: open_truck_modal(tree)).pack(side="right", padx=5)

    table_container = ctk.CTkFrame(tab, fg_color="#FFFFFF", corner_radius=12, border_color="#E5E7EB", border_width=1)
    table_container.pack(fill="both", expand=True, pady=5)
    table_container.grid_rowconfigure(0, weight=1)
    table_container.grid_columnconfigure(0, weight=0)
    table_container.grid_columnconfigure(1, weight=1)

    columns = ("company_name", "status", "plate", "capacity", "driver_id", "hidden_cie_id")
    tree = ttk.Treeview(table_container, columns=columns, show="headings", style="Custom.Treeview")
    
    tree.heading("driver_id", text="קוד נהג/רכב", anchor="center")
    tree.heading("capacity", text="כושר נשיאה (טון)", anchor="center")
    tree.heading("plate", text="לוחית זיהוי", anchor="center")
    tree.heading("status", text="מצב תחזוקה", anchor="center")
    tree.heading("company_name", text="חברת הפצה משוייכת", anchor="center")

    tree.column("driver_id", width=110, anchor="center", stretch=tk.YES)
    tree.column("capacity", width=140, anchor="center", stretch=tk.YES)
    tree.column("plate", width=140, anchor="center", stretch=tk.YES)
    tree.column("status", width=130, anchor="center", stretch=tk.YES)
    tree.column("company_name", width=220, anchor="e", stretch=tk.YES)
    tree.column("hidden_cie_id", width=0, stretch=tk.NO)

    tree.tag_configure("active_truck", background="#E8F5E9", foreground="#155724")

    v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=v_scrollbar.set)
    v_scrollbar.grid(row=0, column=0, sticky="ns", pady=10, padx=(10, 0))
    tree.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    actions = ctk.CTkFrame(tab, fg_color="transparent")
    actions.pack(fill="x", pady=(15, 10))
    ctk.CTkButton(actions, text="✏️ עריכת נתוני רכב", font=("Segoe UI", 13, "bold"), fg_color="#3B82F6", hover_color="#2563EB", width=160, height=38, corner_radius=10, command=lambda: edit_truck(tree)).pack(side="right", padx=5)
    ctk.CTkButton(actions, text="🗑️ השבתת רכב מהצי", font=("Segoe UI", 13, "bold"), fg_color="#EF4444", hover_color="#DC2626", width=160, height=38, corner_radius=10, command=lambda: delete_truck(tree)).pack(side="right", padx=25)

    refresh_trucks_data(tree)


def refresh_trucks_data(tree):
    for item in tree.get_children(): tree.delete(item)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
            SELECT t.DriverID, t.Capacity, t.LicensePlate, t.MaintenanceStatus, dc.DeliveryCieName, t.Active, t.DeliveryCieID
            FROM TRUCK t
            JOIN DELIVERYCOMPANY dc ON t.DeliveryCieID = dc.DeliveryCieID
            ORDER BY t.DriverID ASC;
        """
        cursor.execute(query)
        for row in cursor.fetchall():
            row_tag = "active_truck" if row[5] == 1 else ""
            tree.insert("", "end", values=(row[4], row[3], row[2], f"{row[1]} טון", row[0], row[6]), tags=(row_tag,))
        cursor.close()
        conn.close()


def open_truck_modal(tree, edit_data=None):
    is_edit = edit_data is not None
    modal = ctk.CTkToplevel()
    modal.title("עריכת פרטי משאית")
    modal.geometry("400x460")
    try: modal.transient(tree.winfo_toplevel())
    except: pass
    modal.grab_set()

    ctk.CTkLabel(modal, text="🚛 פרטי רכב במערך הצי", font=("Segoe UI", 16, "bold")).pack(pady=15)

    companies_list = []
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DeliveryCieID, DeliveryCieName FROM DELIVERYCOMPANY ORDER BY DeliveryCieID ASC;")
        for r in cursor.fetchall(): companies_list.append(f"{r[0]} - {r[1]}")
        cursor.close()
        conn.close()

    ctk.CTkLabel(modal, text="קוד נהג/רכב מספר", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    id_entry = ctk.CTkEntry(modal, justify="right")
    id_entry.pack(fill="x", padx=40, pady=2)
    if is_edit:
        id_entry.insert(0, edit_data[4])
        id_entry.configure(state="disabled", fg_color="#E5E7EB")

    ctk.CTkLabel(modal, text="כושר נשיאה (טון)", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    cap_entry = ctk.CTkEntry(modal, justify="right")
    cap_entry.pack(fill="x", padx=40, pady=2)
    if is_edit: cap_entry.insert(0, edit_data[3].replace(" טון", ""))

    ctk.CTkLabel(modal, text="מספר לוחית זיהוי", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    plate_entry = ctk.CTkEntry(modal, justify="right")
    plate_entry.pack(fill="x", padx=40, pady=2)
    if is_edit: plate_entry.insert(0, edit_data[2])

    ctk.CTkLabel(modal, text="מצב תחזוקה נוכחי", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    status_entry = ctk.CTkEntry(modal, justify="right")
    status_entry.pack(fill="x", padx=40, pady=2)
    if is_edit: status_entry.insert(0, edit_data[1])
    else: status_entry.insert(0, "Good")

    ctk.CTkLabel(modal, text="חברת הפצה אחראית", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    cie_option = ctk.CTkOptionMenu(modal, values=companies_list)
    cie_option.pack(fill="x", padx=40, pady=2)
    if is_edit:
        for c_str in companies_list:
            if c_str.startswith(str(edit_data[5]) + " -"): cie_option.set(c_str)

    def save():
        d_id = id_entry.get().strip()
        cap = cap_entry.get().strip()
        plate = plate_entry.get().strip()
        stat = status_entry.get().strip()
        cie_sel = cie_option.get()

        if not d_id or not cap or not plate or not stat:
            messagebox.showwarning("קלט חסר", "אנא מלאי את כל השדות.")
            return

        try:
            cap_val = float(cap)
        except:
            return messagebox.showwarning("שגיאה", "כושר נשיאה חייב להיות מספרי.")

        cie_id = int(cie_sel.split(" - ")[0])

        conn_save = get_db_connection()
        if conn_save:
            cursor_save = conn_save.cursor()
            try:
                if is_edit:
                    cursor_save.execute("UPDATE TRUCK SET Capacity=%s, LicensePlate=%s, MaintenanceStatus=%s, DeliveryCieID=%s WHERE DriverID=%s;",
                                        (cap_val, plate, stat, cie_id, int(d_id)))
                else:
                    cursor_save.execute("INSERT INTO TRUCK (DriverID, Capacity, LicensePlate, MaintenanceStatus, DeliveryCieID, Active) VALUES (%s, %s, %s, %s, %s, 1);",
                                        (int(d_id), cap_val, plate, stat, cie_id))
                conn_save.commit()
                modal.destroy()
                refresh_trucks_data(tree)
            except Exception as e:
                messagebox.showerror("שגיאה", f"לוחית הזיהוי או קוד הנהג תפוסים במערכת:\n{e}")
            finally:
                cursor_save.close()
                conn_save.close()

    ctk.CTkButton(modal, text="שמור", fg_color="#10B981", hover_color="#059669", height=38, corner_radius=8, command=save).pack(pady=15)

def edit_truck(tree):
    sel = tree.selection()
    if not sel: return messagebox.showwarning("בחירה חובה", "אנא בחרי רכב מהטבלה לעריכה.")
    open_truck_modal(tree, tree.item(sel[0], 'values'))

def delete_truck(tree):
    sel = tree.selection()
    if not sel: return messagebox.showwarning("בחירה חובה", "אנא בחרי רכב להשבתה.")
    d_id = tree.item(sel[0], 'values')[4]
    if messagebox.askyesno("אישור פעולה", f"האם את בטוחה שברצונך למחוק ולהשבית רכב מספר {d_id} מצי ההפצה?"):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM TRUCK WHERE DriverID = %s;", (int(d_id),))
                conn.commit()
                refresh_trucks_data(tree)
            except Exception as e:
                messagebox.showerror("חסימת מחיקה", f"לא ניתן למחוק רכב זה מהצי.\n\nהסיבה: רכב זה מקושר כעת להזמנות הפצה רשתיות פתוחות במערכת.")
            finally:
                cursor.close()
                conn.close()


# =========================================================================
# 🏢 טאב 3: חברות הפצה ואזורי שירות (DELIVERYCOMPANY + REGIONSERVED)
# =========================================================================
def setup_companies_tab(tab):
    btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
    btn_frame.pack(fill="x", pady=(10, 10))
    
    ctk.CTkButton(btn_frame, text="🗺️ הגדרת אזור שירות חדש", font=("Segoe UI", 12, "bold"), fg_color="#3B82F6", hover_color="#2563EB", height=35, corner_radius=10, command=lambda: open_region_modal(tree)).pack(side="left", padx=5)
    ctk.CTkButton(btn_frame, text="➕ רישום חברת הפצה חדשה", font=("Segoe UI", 12, "bold"), fg_color="#10B981", hover_color="#059669", height=35, corner_radius=10, command=lambda: open_company_modal(tree)).pack(side="right", padx=5)

    table_container = ctk.CTkFrame(tab, fg_color="#FFFFFF", corner_radius=12, border_color="#E5E7EB", border_width=1)
    table_container.pack(fill="both", expand=True, pady=5)
    table_container.grid_rowconfigure(0, weight=1)
    table_container.grid_columnconfigure(0, weight=0)
    table_container.grid_columnconfigure(1, weight=1)

    columns = ("regions", "email", "phone", "cie_name", "cie_id")
    tree = ttk.Treeview(table_container, columns=columns, show="headings", style="Custom.Treeview")
    
    tree.heading("cie_id", text="קוד חברה", anchor="center")
    tree.heading("cie_name", text="שם חברת משלוחים", anchor="center")
    tree.heading("phone", text="מספר טלפון", anchor="center")
    tree.heading("email", text="כתובת אימייל", anchor="center")
    tree.heading("regions", text="אזורי שירות מורשים ברשת", anchor="center")

    tree.column("cie_id", width=100, anchor="center", stretch=tk.YES)
    tree.column("cie_name", width=180, anchor="e", stretch=tk.YES)
    tree.column("phone", width=130, anchor="center", stretch=tk.YES)
    tree.column("email", width=180, anchor="center", stretch=tk.YES)
    tree.column("regions", width=250, anchor="e", stretch=tk.YES)

    v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=v_scrollbar.set)
    v_scrollbar.grid(row=0, column=0, sticky="ns", pady=10, padx=(10, 0))
    tree.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    actions = ctk.CTkFrame(tab, fg_color="transparent")
    actions.pack(fill="x", pady=(15, 10))
    ctk.CTkButton(actions, text="✏️ עריכת פרטי חברה", font=("Segoe UI", 13, "bold"), fg_color="#10B981", hover_color="#059669", width=160, height=38, corner_radius=10, command=lambda: edit_company(tree)).pack(side="right", padx=5)
    ctk.CTkButton(actions, text="🗑️ הסרת חברת הפצה", font=("Segoe UI", 13, "bold"), fg_color="#EF4444", hover_color="#DC2626", width=160, height=38, corner_radius=10, command=lambda: delete_company(tree)).pack(side="right", padx=25)
    ctk.CTkButton(actions, text="🗑️ הסרת אזור שירות", font=("Segoe UI", 13, "bold"), fg_color="#EF4444", hover_color="#DC2626", width=160, height=38, corner_radius=10, command=lambda: delete_region(tree)).pack(side="left", padx=5)

    refresh_companies_data(tree)


def refresh_companies_data(tree):
    for item in tree.get_children(): tree.delete(item)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        # שליפת רשימת החברות ושרשור אזורי השירות המורשים שלהן (STRING_AGG)
        query = """
            SELECT dc.DeliveryCieID, dc.DeliveryCieName, dc.DeliveryCiePhoneNb, dc.Email,
                   COALESCE(STRING_AGG(r.RegionServed, ', '), 'טרם הוגדרו אזורים')
            FROM DELIVERYCOMPANY dc
            LEFT JOIN DELIVERYCOMPANY_REGIONSERVED r ON dc.DeliveryCieID = r.DeliveryCieID
            GROUP BY dc.DeliveryCieID, dc.DeliveryCieName, dc.DeliveryCiePhoneNb, dc.Email
            ORDER BY dc.DeliveryCieID ASC;
        """
        cursor.execute(query)
        for row in cursor.fetchall():
            tree.insert("", "end", values=(row[4], row[3], row[2], row[1], row[0]))
        cursor.close()
        conn.close()


def open_company_modal(tree, edit_data=None):
    is_edit = edit_data is not None
    modal = ctk.CTkToplevel()
    modal.title("עריכת חברת הפצה")
    modal.geometry("400x380")
    try: modal.transient(tree.winfo_toplevel())
    except: pass
    modal.grab_set()

    ctk.CTkLabel(modal, text="🏢 פרטי חברת הפצה והובלה", font=("Segoe UI", 16, "bold")).pack(pady=15)

    ctk.CTkLabel(modal, text="קוד חברה מספר", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    id_entry = ctk.CTkEntry(modal, justify="right")
    id_entry.pack(fill="x", padx=40, pady=2)
    if is_edit:
        id_entry.insert(0, edit_data[4])
        id_entry.configure(state="disabled", fg_color="#E5E7EB")

    ctk.CTkLabel(modal, text="שם חברת המשלוחים", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    name_entry = ctk.CTkEntry(modal, justify="right")
    name_entry.pack(fill="x", padx=40, pady=2)
    if is_edit: name_entry.insert(0, edit_data[3])

    ctk.CTkLabel(modal, text="מספר טלפון של המוקד", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    phone_entry = ctk.CTkEntry(modal, justify="right")
    phone_entry.pack(fill="x", padx=40, pady=2)
    if is_edit: phone_entry.insert(0, edit_data[2])

    ctk.CTkLabel(modal, text="כתובת אימייל רשמית", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    email_entry = ctk.CTkEntry(modal, justify="right")
    email_entry.pack(fill="x", padx=40, pady=2)
    if is_edit: email_entry.insert(0, edit_data[1])

    def save():
        c_id = id_entry.get().strip()
        name = name_entry.get().strip()
        phone = phone_entry.get().strip()
        email = email_entry.get().strip()

        if not c_id or not name or not phone or not email:
            messagebox.showwarning("קלט חסר", "אנא מלאי את כל השדות.")
            return

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                if is_edit:
                    cursor.execute("UPDATE DELIVERYCOMPANY SET DeliveryCieName=%s, DeliveryCiePhoneNb=%s, Email=%s WHERE DeliveryCieID=%s;",
                                   (name, phone, email, int(c_id)))
                else:
                    cursor.execute("INSERT INTO DELIVERYCOMPANY (DeliveryCieID, DeliveryCieName, DeliveryCiePhoneNb, Email) VALUES (%s, %s, %s, %s);",
                                   (int(c_id), name, phone, email))
                conn.commit()
                modal.destroy()
                refresh_companies_data(tree)
            except Exception as e:
                messagebox.showerror("שגיאה", f"ערכי שם החברה, הטלפון או ה-ID קיימים כבר או שאינם תואמים תבנית אימייל:\n{e}")
            finally:
                cursor.close()
                conn.close()

    ctk.CTkButton(modal, text="שמור", fg_color="#10B981", hover_color="#059669", height=38, corner_radius=8, command=save).pack(pady=20)

def edit_company(tree):
    sel = tree.selection()
    if not sel: return messagebox.showwarning("בחירה חובה", "אנא בחרי חברה מהטבלה לעריכה.")
    open_company_modal(tree, tree.item(sel[0], 'values'))

def delete_company(tree):
    sel = tree.selection()
    if not sel: return messagebox.showwarning("בחירה חובה", "אנא בחרי חברה למחיקה.")
    c_id = tree.item(sel[0], 'values')[4]
    if messagebox.askyesno("אישור מחיקה", f"האם למחוק את חברת ההפצה מספר {c_id}?"):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM DELIVERYCOMPANY WHERE DeliveryCieID = %s;", (int(c_id),))
                conn.commit()
                refresh_companies_data(tree)
            except Exception as e:
                messagebox.showerror("חסימת מחיקה", f"לא ניתן למחוק חברה זו.\n\nהסיבה: קיימות משאיות פעילות בצי הרשת הרשומות תחתיה.")
            finally:
                cursor.close()
                conn.close()


# --- פעולות CRUD עבור טבלת האזורים DELIVERYCOMPANY_REGIONSERVED ---
def open_region_modal(tree):
    companies_list = []
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DeliveryCieID, DeliveryCieName FROM DELIVERYCOMPANY ORDER BY DeliveryCieID ASC;")
        for r in cursor.fetchall(): companies_list.append(f"{r[0]} - {r[1]}")
        cursor.close()
        conn.close()

    if not companies_list: return messagebox.showwarning("שגיאה", "אנא רשמי תחילה חברת הפצה במערכת.")

    modal = ctk.CTkToplevel()
    modal.title("הגדרת אזור שירות")
    modal.geometry("380x260")
    modal.grab_set()

    ctk.CTkLabel(modal, text="🗺️ הוספת אזור פעילות לחברה", font=("Segoe UI", 15, "bold")).pack(pady=15)
    
    ctk.CTkLabel(modal, text="בחרי חברת הפצה", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    cie_option = ctk.CTkOptionMenu(modal, values=companies_list)
    cie_option.pack(fill="x", padx=40, pady=2)

    ctk.CTkLabel(modal, text="שם אזור השירות (למשל: ירושלים, מרכז)", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    region_entry = ctk.CTkEntry(modal, justify="right")
    region_entry.pack(fill="x", padx=40, pady=2)

    def save():
        reg = region_entry.get().strip()
        cie_sel = cie_option.get()
        if not reg: return messagebox.showwarning("קלט חסר", "אנא הזיני שם אזור.")
        
        cie_id = int(cie_sel.split(" - ")[0])
        conn_r = get_db_connection()
        if conn_r:
            cursor_r = conn_r.cursor()
            try:
                cursor_r.execute("INSERT INTO DELIVERYCOMPANY_REGIONSERVED (DeliveryCieID, RegionServed) VALUES (%s, %s);", (cie_id, reg))
                conn_r.commit()
                modal.destroy()
                refresh_companies_data(tree)
            except:
                messagebox.showerror("כפילות", "אזור שירות זה כבר מוגדר ומאושר עבור החברה הנבחרת.")
            finally:
                cursor_r.close()
                conn_r.close()

    ctk.CTkButton(modal, text="בצע", fg_color="#10B981", hover_color="#059669", height=38, corner_radius=8, command=save).pack(pady=15)

def delete_region(tree):
    sel = tree.selection()
    if not sel: return messagebox.showwarning("בחירה חובה", "אנא בחרי חברה מהטבלה.")
    c_id = tree.item(sel[0], 'values')[4]
    
    modal = ctk.CTkToplevel()
    modal.title("הסרת אזור שירות")
    modal.geometry("380x240")
    modal.grab_set()

    regions_list = []
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT RegionServed FROM DELIVERYCOMPANY_REGIONSERVED WHERE DeliveryCieID = %s;", (int(c_id),))
        for r in cursor.fetchall(): regions_list.append(r[0])
        cursor.close()
        conn.close()

    if not regions_list: 
        modal.destroy()
        return messagebox.showwarning("שגיאה", "לחברה זו לא מוגדרים אזורי שירות להסרה.")

    ctk.CTkLabel(modal, text="בחרי אזור להסרה", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    r_option = ctk.CTkOptionMenu(modal, values=regions_list)
    r_option.pack(fill="x", padx=40, pady=15)

    def do_delete():
        reg = r_option.get()
        conn_d = get_db_connection()
        if conn_d:
            cursor_d = conn_d.cursor()
            cursor_d.execute("DELETE FROM DELIVERYCOMPANY_REGIONSERVED WHERE DeliveryCieID=%s AND RegionServed=%s;", (int(c_id), reg))
            conn_d.commit()
            cursor_d.close()
            conn_d.close()
            modal.destroy()
            refresh_companies_data(tree)

    ctk.CTkButton(modal, text="בצע", fg_color="#EF4444", hover_color="#DC2626", height=38, corner_radius=8, command=do_delete).pack(pady=10)