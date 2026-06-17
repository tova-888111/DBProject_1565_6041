import customtkinter as ctk
from tkinter import ttk, messagebox
import tkinter as tk
from db_connection import get_db_connection
from datetime import datetime

def show_orders_view(main_frame):
    # ניקוי המסך למניעת כפילויות תצוגה
    for widget in main_frame.winfo_children():
        widget.destroy()

    # --- ✨ תיקון: שינוי הכותרות שיהיו זהות לחלוטין לקבצים הקודמים ---
    header_label = ctk.CTkLabel(main_frame, text="ניהול מבצעים והנחות רשתיים", font=("Segoe UI", 32, "bold"), text_color="#111827", anchor="e")
    header_label.pack(pady=(35, 4), padx=35, fill="x")
    
    sub_header = ctk.CTkLabel(main_frame, text="הגדרה וניהול של אחוזי הנחה, תאריכי תוקף והחלת מבצעים על מוצרי הרשת", font=("Segoe UI", 14, "bold"), text_color="#4B5563", anchor="e")
    sub_header.pack(pady=(0, 20), padx=35, fill="x")

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
    
    search_id_entry = ctk.CTkEntry(search_frame, placeholder_text="לפי קוד הזמנה", font=("Segoe UI", 12), width=160, height=35, corner_radius=8, justify="right")
    search_id_entry.grid(row=0, column=2, padx=6, sticky="e")
    
    search_store_entry = ctk.CTkEntry(search_frame, placeholder_text="לפי קוד סניף", font=("Segoe UI", 12), width=160, height=35, corner_radius=8, justify="right")
    search_store_entry.grid(row=0, column=1, padx=6, sticky="e")

    search_id_entry.bind("<KeyRelease>", lambda event: refresh_orders_data(tree, search_id_entry.get().strip(), search_store_entry.get().strip()))
    search_store_entry.bind("<KeyRelease>", lambda event: refresh_orders_data(tree, search_id_entry.get().strip(), search_store_entry.get().strip()))

    btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
    btn_frame.pack(fill="x", pady=(0, 10))
    
    ctk.CTkButton(btn_frame, text="📦 ניהול ועדכון תכולת הזמנה", font=("Segoe UI", 12, "bold"), fg_color="#3B82F6", hover_color="#2563EB", height=35, corner_radius=10, command=lambda: open_contains_manager_modal(tree)).pack(side="left", padx=5)
    ctk.CTkButton(btn_frame, text="➕ יצירת הזמנת הפצה חדשה", font=("Segoe UI", 12, "bold"), fg_color="#10B981", hover_color="#059669", height=35, corner_radius=10, command=lambda: open_order_modal(tree)).pack(side="right", padx=5)

    table_container = ctk.CTkFrame(tab, fg_color="#FFFFFF", corner_radius=12, border_color="#E5E7EB", border_width=1)
    table_container.pack(fill="both", expand=True, pady=5)
    table_container.grid_rowconfigure(0, weight=1)
    table_container.grid_columnconfigure(0, weight=0) 
    table_container.grid_columnconfigure(1, weight=1) 

    columns = ("status", "driver_id", "store_info", "deliv_date", "order_date", "price", "order_id", "hidden_store_id")
    tree = ttk.Treeview(table_container, columns=columns, show="headings", style="Custom.Treeview")
    
    tree.heading("order_id", text="קוד הזמנה", anchor="center")
    tree.heading("price", text="עלות כוללת", anchor="center")
    tree.heading("order_date", text="תאריך יצירה", anchor="center")
    tree.heading("deliv_date", text="תאריך אספקה מיועד", anchor="center")
    tree.heading("store_info", text="סניף יעד מבוקש", anchor="center")
    tree.heading("driver_id", text="קוד נהג / משאית", anchor="center")
    tree.heading("status", text="סטטוס הפצה", anchor="center")

    tree.column("order_id", width=110, anchor="center", stretch=tk.NO)
    tree.column("price", width=130, anchor="center", stretch=tk.NO)
    tree.column("order_date", width=160, anchor="center", stretch=tk.NO) 
    tree.column("deliv_date", width=180, anchor="center", stretch=tk.NO) 
    tree.column("store_info", width=340, anchor="e", stretch=tk.YES)  
    tree.column("driver_id", width=180, anchor="center", stretch=tk.NO) 
    tree.column("status", width=150, anchor="center", stretch=tk.NO)
    tree.column("hidden_store_id", width=0, stretch=tk.NO)

    tree.tag_configure("pending_order", background="#FFEBEE", foreground="#C62828") 
    tree.tag_configure("processed_order", background="#E8F5E9", foreground="#155724") 

    v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=tree.yview)
    h_scrollbar = ttk.Scrollbar(table_container, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
    
    h_scrollbar.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=(0, 10))
    v_scrollbar.grid(row=0, column=0, sticky="ns", pady=10, padx=(10, 0)) 
    tree.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=(10, 2)) 

    actions = ctk.CTkFrame(tab, fg_color="transparent")
    actions.pack(fill="x", pady=(15, 10))
    
    ctk.CTkButton(actions, text="✏️ עדכון סטטוס/פרטי הזמנה", font=("Segoe UI", 13, "bold"), fg_color="#10B981", hover_color="#059669", width=175, height=38, corner_radius=10, command=lambda: edit_order(tree)).pack(side="right", padx=3)
    ctk.CTkButton(actions, text="🗑️ ביטול הזמנה מהמערכת", font=("Segoe UI", 13, "bold"), fg_color="#EF4444", hover_color="#DC2626", width=175, height=38, corner_radius=10, command=lambda: delete_order(tree)).pack(side="right", padx=15)
    
    ctk.CTkButton(actions, text="⚡ חישוב עלות סיטונאית", font=("Segoe UI", 13, "bold"), fg_color="#2563EB", hover_color="#1D4ED8", width=180, height=38, corner_radius=10, command=lambda: open_calculate_price_modal(tree)).pack(side="left", padx=3)
    ctk.CTkButton(actions, text="✅ השלמת הזמנה וקליטת מלאי", font=("Segoe UI", 13, "bold"), fg_color="#8B5CF6", hover_color="#7C3AED", width=210, height=38, corner_radius=10, command=lambda: trigger_complete_order_procedure(tree)).pack(side="left", padx=3)

    refresh_orders_data(tree)


def refresh_orders_data(tree, search_id="", search_store=""):
    for item in tree.get_children(): tree.delete(item)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
            SELECT o.OrderId, o.Price, o.OrderDate, s.StoreName, o.DriverID, o.Status, o.StoreID, o.DeliveryDate
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
            d_date = row[7].strftime('%Y-%m-%d %H:%M') if row[7] else "טרם סופק"
            status_val = str(row[5]).strip()
            row_tag = "pending_order" if status_val == "PENDING" else "processed_order"
            tree.insert("", "end", values=(status_val, row[4], f"סניף {row[6]} - {row[3]}", d_date, o_date, f"₪{row[1]:,.2f}", row[0], row[6]), tags=(row_tag,))
        cursor.close()
        conn.close()


def open_order_modal(tree, edit_data=None):
    is_edit = edit_data is not None
    modal = ctk.CTkToplevel()
    modal.title("עריכת הזמנה" if is_edit else "הזמנת הפצה חדשה")
    modal.geometry("420x520")
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
        id_entry.insert(0, edit_data[6])
        id_entry.configure(state="disabled", fg_color="#E5E7EB")

    ctk.CTkLabel(modal, text="עלות הזמנה כוללת", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    price_entry = ctk.CTkEntry(modal, justify="right")
    price_entry.pack(fill="x", padx=40, pady=2)
    if is_edit: price_entry.insert(0, edit_data[5].replace("₪", "").replace(",", ""))

    ctk.CTkLabel(modal, text="תאריך אספקה (YYYY-MM-DD HH:MM)", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    deliv_entry = ctk.CTkEntry(modal, justify="right")
    deliv_entry.pack(fill="x", padx=40, pady=2)
    if is_edit and edit_data[3] != "טרם סופק": 
        deliv_entry.insert(0, edit_data[3])

    ctk.CTkLabel(modal, text="סניף יעד מזמין", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    store_option = ctk.CTkOptionMenu(modal, values=stores_list)
    store_option.pack(fill="x", padx=40, pady=2)
    if is_edit:
        for s_str in stores_list:
            if s_str.startswith(str(edit_data[7]) + " -"): store_option.set(s_str)

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
        d_time_str = deliv_entry.get().strip()
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

        parsed_d_time = None
        if d_time_str:
            try:
                parsed_d_time = datetime.strptime(d_time_str, "%Y-%m-%d %H:%M")
            except ValueError:
                messagebox.showwarning("פורמט שגוי", "תאריך האספקה חייב להיות במבנה: YYYY-MM-DD HH:MM")
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
                        SET Price=%s, StoreID=%s, DriverID=%s, Status=%s, DeliveryDate=%s 
                        WHERE OrderId=%s;
                    """, (price_val, s_id, t_id, stat, parsed_d_time, int(o_id)))
                    conn.commit()
                    messagebox.showinfo("הצלחה", "פרטי ההזמנה עודכנו בהצלחה!")
                    modal.destroy()
                    refresh_orders_data(tree)
                else:
                    cursor.execute("""
                        INSERT INTO "ORDER" (OrderId, Price, StoreID, DriverID, Status, OrderDate, DeliveryDate) 
                        VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s);
                    """, (int(o_id), price_val, s_id, t_id, stat, parsed_d_time))
                    conn.commit()
                    messagebox.showinfo("הצלחה", "ההזמנה החדשה נוצרה בהצלחה!")
                    modal.destroy()
                    refresh_orders_data(tree)
            except Exception as e:
                error_msg = str(e)
                if "duplicate key" in error_msg or "already exists" in error_msg:
                    messagebox.showerror("קוד הזמנה תפוס", f"לא ניתן להוסיף את הרשומה.\nקוד הזמנה מספר {o_id} כבר רשום ותפוס במערכת!")
                else:
                    messagebox.showerror("שגיאה", f"הפעולה נכשלה, אנא ודאי את תקינות הנתונים:\n{error_msg}")
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
    o_id = tree.item(sel[0], 'values')[6]
    if messagebox.askyesno("אישור ביטול", f"האם את בטוחה שברצונך למחוק לחלוטין את הזמנה מספר {o_id} מהמערכת?"):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute('DELETE FROM "ORDER" WHERE OrderId = %s;', (int(o_id),))
                conn.commit()
                refresh_orders_data(tree)
            except Exception as e:
                error_msg = str(e)
                if "foreign key constraint" in error_msg or "is still referenced" in error_msg:
                    messagebox.showerror(
                        "לא ניתן לבצע מחיקה", 
                        f"פעולת המחיקה עבור הזמנה מספר {o_id} נחסמה באופן מאובטח.\n\n"
                        f"💡 הסיבה:\n"
                        f"להזמנה זו יש פריטי תכולה רשומים (מוצרים המשויכים אליה בטבלת הקשר).\n\n"
                        f"🛠️ מה צריך לעשות?\n"
                        f"לחצי על כפתור '📦 ניהול ועדכון תכולת הזמנה', מחקי והסירי משם את כל הפריטים, ורק כשהיא תהיה ריקה לחלוטין תוכלי למחוק אותה."
                    )
                else:
                    messagebox.showerror("שגיאה במחיקה", f"פעולת המחיקה נכשלה:\n{error_msg}")
            finally:
                cursor.close()
                conn.close()


def open_contains_manager_modal(tree):
    sel = tree.selection()
    if not sel: return messagebox.showwarning("בחירה חובה", "אנא בחרי שורת הזמנה מהטבלה כדי לנהל את תכולת המוצרים שלה.")
    o_id = tree.item(sel[0], 'values')[6]

    modal = ctk.CTkToplevel()
    modal.title(f"ניהול פריטי הזמנה מספר {o_id}")
    modal.geometry("560x540")
    modal.grab_set()

    ctk.CTkLabel(modal, text="📦 ניהול תכולת מוצרים - הזמנה " + str(o_id), font=("Segoe UI", 15, "bold")).pack(pady=10)

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
                messagebox.showerror("כפילות", "מוצר זה כבר קיים בהזמנה. השתמשי באפשרות עריכת כמות למטה.")
            finally:
                cursor_sub.close()
                conn_sub.close()

    ctk.CTkButton(add_frame, text="פריט הוסף", fg_color="#10B981", hover_color="#059669", width=90, command=add_item).pack(side="right", padx=5)

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

    def edit_item_qty():
        c_sel = c_tree.selection()
        if not c_sel: return messagebox.showwarning("בחירה חובה", "אנא בחרי פריט מהרשימה לעריכה.")
        vals = c_tree.item(c_sel[0], 'values')
        p_id = vals[2]
        p_name = vals[1]
        current_qty = vals[0]
        
        edit_modal = ctk.CTkToplevel()
        edit_modal.title("עדכון כמות פריט")
        edit_modal.geometry("320x180")
        edit_modal.grab_set()
        
        ctk.CTkLabel(edit_modal, text="עדכון כמות עבור\n" + str(p_name), font=("Segoe UI", 12, "bold"), justify="center").pack(pady=10)
        new_qty_entry = ctk.CTkEntry(edit_modal, justify="right", width=120)
        new_qty_entry.pack(pady=5)
        new_qty_entry.insert(0, current_qty)
        
        def save_qty():
            try:
                new_qty = int(new_qty_entry.get().strip())
                if new_qty <= 0: raise ValueError()
            except:
                return messagebox.showwarning("קלט שגוי", "הכמות חייבת להיות מספר גדול מ-0.")
                
            conn_u = get_db_connection()
            if conn_u:
                cursor_u = conn_u.cursor()
                cursor_u.execute("UPDATE CONTAINS SET Quantity=%s WHERE OrderId=%s AND ProductID=%s;", (new_qty, int(o_id), int(p_id)))
                conn_u.commit()
                cursor_u.close()
                conn_u.close()
                edit_modal.destroy()
                refresh_contains_table(c_tree, o_id)
                
        ctk.CTkButton(edit_modal, text="שמור", fg_color="#3B82F6", command=save_qty).pack(pady=10)

    def delete_item():
        c_sel = c_tree.selection()
        if not c_sel: return messagebox.showwarning("בחירה חובה", "בחרי פריט למחיקה.")
        p_id = c_tree.item(c_sel[0], 'values')[2]
        conn_del = get_db_connection()
        if conn_del:
            cursor_del = conn_del.cursor()
            try:
                cursor_del.execute('DELETE FROM CONTAINS WHERE OrderId=%s AND ProductID=%s;', (int(o_id), int(p_id)))
                conn_del.commit()
                refresh_contains_table(c_tree, o_id)
            except Exception as e:
                messagebox.showerror("שגיאה", f"לא ניתן להסיר פריט זה:\n{e}")
            finally:
                cursor_del.close()
                conn_del.close()

    actions_frame = ctk.CTkFrame(modal, fg_color="transparent")
    actions_frame.pack(fill="x", padx=20, pady=(0, 15))
    ctk.CTkButton(actions_frame, text="✏️פריט כמות עריכת", fg_color="#3B82F6", hover_color="#2563EB", height=35, command=edit_item_qty).pack(side="right", padx=5, expand=True, fill="x")
    ctk.CTkButton(actions_frame, text="🗑️ מההזמנה פריט הסר", fg_color="#EF4444", hover_color="#DC2626", height=35, command=delete_item).pack(side="left", padx=5, expand=True, fill="x")
    
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
    ctk.CTkButton(btn_frame, text="➕ ️רישום רכב/נהג חדש", font=("Segoe UI", 12, "bold"), fg_color="#10B981", hover_color="#059669", height=35, corner_radius=10, command=lambda: open_truck_modal(tree)).pack(side="right", padx=5)

    table_container = ctk.CTkFrame(tab, fg_color="#FFFFFF", corner_radius=12, border_color="#E5E7EB", border_width=1)
    table_container.pack(fill="both", expand=True, pady=5)
    table_container.grid_rowconfigure(0, weight=1)
    table_container.grid_columnconfigure(0, weight=0)
    table_container.grid_columnconfigure(1, weight=1)

    # --- ✨ תיקון: הוספת עמודת קוד חברה (hidden_cie_id) כעמודה גלויה בטבלה ---
    columns = ("company_name", "hidden_cie_id", "status", "plate", "is_active", "capacity", "driver_id", "hidden_active_num")
    tree = ttk.Treeview(table_container, columns=columns, show="headings", style="Custom.Treeview")
    
    tree.heading("driver_id", text="קוד נהג/רכב")
    tree.heading("capacity", text="כושר נשיאה (בטונות)") 
    tree.heading("is_active", text="סטטוס פעילות")      
    tree.heading("plate", text="לוחית זיהוי")
    tree.heading("status", text="מצב תחזוקה")
    tree.heading("hidden_cie_id", text="קוד חברה")
    tree.heading("company_name", text="חברת הפצה משוייכת")

    tree.column("driver_id", width=110, anchor="center", stretch=tk.YES)
    tree.column("capacity", width=140, anchor="center", stretch=tk.YES)
    tree.column("is_active", width=130, anchor="center", stretch=tk.YES)
    tree.column("plate", width=140, anchor="center", stretch=tk.YES)
    tree.column("status", width=130, anchor="center", stretch=tk.YES)
    tree.column("hidden_cie_id", width=100, anchor="center", stretch=tk.YES)
    tree.column("company_name", width=220, anchor="e", stretch=tk.YES)
    tree.column("hidden_active_num", width=0, stretch=tk.NO)

    tree.tag_configure("active_truck", background="#E8F5E9", foreground="#155724")
    tree.tag_configure("inactive_truck", background="#FFEBEE", foreground="#C62828")

    v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=v_scrollbar.set)
    v_scrollbar.grid(row=0, column=0, sticky="ns", pady=10, padx=(10, 0)) 
    tree.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)

    actions = ctk.CTkFrame(tab, fg_color="transparent")
    actions.pack(fill="x", pady=(15, 10))
    ctk.CTkButton(actions, text="✏️ עריכת נתוני רכב וסטטוס", font=("Segoe UI", 13, "bold"), fg_color="#3B82F6", hover_color="#2563EB", width=180, height=38, corner_radius=10, command=lambda: edit_truck(tree)).pack(side="right", padx=5)
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
            is_act_num = row[5]
            act_text = "פעיל" if is_act_num == 1 else "מושתת / לא פעיל"
            row_tag = "active_truck" if is_act_num == 1 else "inactive_truck"
            # גלגול הערכים לפי הסדר החדש של העמודות, כולל הצבת מזהה חברת ההפצה בעמודה הגלויה
            tree.insert("", "end", values=(row[4], row[6], row[3], row[2], act_text, f"{row[1]:.2f}", row[0], is_act_num), tags=(row_tag,))
        cursor.close()
        conn.close()


def open_truck_modal(tree, edit_data=None):
    is_edit = edit_data is not None
    modal = ctk.CTkToplevel()
    modal.title("עריכת פרטי משאית ונהג")
    modal.geometry("400x520")
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
        id_entry.insert(0, edit_data[6])
        id_entry.configure(state="disabled", fg_color="#E5E7EB")

    ctk.CTkLabel(modal, text="כושר נשיאה (בטונות)", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    cap_entry = ctk.CTkEntry(modal, justify="right")
    cap_entry.pack(fill="x", padx=40, pady=2)
    if is_edit: cap_entry.insert(0, edit_data[5])

    ctk.CTkLabel(modal, text="מספר לוחית זיהוי", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    plate_entry = ctk.CTkEntry(modal, justify="right")
    plate_entry.pack(fill="x", padx=40, pady=2)
    if is_edit: plate_entry.insert(0, edit_data[3])

    ctk.CTkLabel(modal, text="מצב תחזוקה נוכחי", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    status_entry = ctk.CTkEntry(modal, justify="right")
    status_entry.pack(fill="x", padx=40, pady=2)
    if is_edit: status_entry.insert(0, edit_data[2])
    else: status_entry.insert(0, "Good")

    ctk.CTkLabel(modal, text="חברת הפצה אחראית", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    cie_option = ctk.CTkOptionMenu(modal, values=companies_list)
    cie_option.pack(fill="x", padx=40, pady=2)
    if is_edit:
        for c_str in companies_list:
            if c_str.startswith(str(edit_data[1]) + " -"): cie_option.set(c_str)

    ctk.CTkLabel(modal, text="סטטוס פעילות במערכת", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    active_option = ctk.CTkOptionMenu(modal, values=["1 - פעיל", "0 - לא פעיל"])
    active_option.pack(fill="x", padx=40, pady=2)
    if is_edit:
        active_option.set("1 - פעיל" if str(edit_data[7]) == "1" else "0 - לא פעיל")

    def save():
        d_id = id_entry.get().strip()
        cap = cap_entry.get().strip()
        plate = plate_entry.get().strip()
        stat = status_entry.get().strip()
        cie_sel = cie_option.get()
        act_sel = active_option.get()

        if not d_id or not cap or not plate or not stat:
            messagebox.showwarning("קלט חסר", "אנא מלאי את כל השדות.")
            return

        try:
            cap_val = float(cap)
        except:
            return messagebox.showwarning("שגיאה", "כושר נשיאה חייב להיות מספרי חיובי.")

        cie_id = int(cie_sel.split(" - ")[0])
        act_val = int(act_sel.split(" - ")[0])

        conn_save = get_db_connection()
        if conn_save:
            cursor_save = conn_save.cursor()
            try:
                if is_edit:
                    cursor_save.execute("UPDATE TRUCK SET Capacity=%s, LicensePlate=%s, MaintenanceStatus=%s, DeliveryCieID=%s, Active=%s WHERE DriverID=%s;",
                                        (cap_val, plate, stat, cie_id, act_val, int(d_id)))
                    conn.commit()
                    messagebox.showinfo("הצלחה", "נתוני הרכב עודכנו בהצלחה!")
                    modal.destroy()
                    refresh_trucks_data(tree)
                else:
                    cursor_save.execute("INSERT INTO TRUCK (DriverID, Capacity, LicensePlate, MaintenanceStatus, DeliveryCieID, Active) VALUES (%s, %s, %s, %s, %s, %s);",
                                        (int(d_id), cap_val, plate, stat, cie_id, act_val))
                    conn.commit()
                    messagebox.showinfo("הצלחה", "הרכב החדש נרשם בהצלחה בצי!")
                    modal.destroy()
                    refresh_trucks_data(tree)
            except Exception as e:
                error_msg = str(e)
                if "duplicate key" in error_msg or "already exists" in error_msg:
                    messagebox.showerror("קוד נהג/רכב תפוס", f"לא ניתן לבצע רישום.\nקוד נהג/רכב מספר {d_id} או לוחית הזיהוי כבר רשומים במערכת הצי!")
                else:
                    messagebox.showerror("שגיאה", f"הפעולה נכשלה, אנא ודאי את תקינות הנתונים:\n{error_msg}")
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
    d_id = tree.item(sel[0], 'values')[6]
    if messagebox.askyesno("אישור פעולה", f"האם את בטוחה שברצונך למחוק ולהשבית רכב מספר {d_id} מצי ההפצה?"):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM TRUCK WHERE DriverID = %s;", (int(d_id),))
                conn.commit()
                refresh_trucks_data(tree)
            except Exception as e:
                error_msg = str(e)
                if "foreign key constraint" in error_msg or "is still referenced" in error_msg:
                    messagebox.showerror(
                        "לא ניתן למחוק רכב", 
                        f"פעולת המחיקה עבור רכב מספר {d_id} נחסמה באופן מאובטח.\n\n"
                        f"💡 הסיבה:\n"
                        f"רכב זה מקושר כעת להזמנות הפצה פעילות או פתוחות הקיימות במערכת.\n\n"
                        f"🛠️ מה צריך לעשות?\n"
                        f"יש לערוך או למחוק תחילה את ההזמנות המשויכות לרכב זה בטאב 'ניהול הזמנות והפצה', ורק אז ניתן יהיה להסירו מהצי."
                    )
                else:
                    messagebox.showerror("שגיאה במחיקה", f"לא ניתן למחוק רכב זה מהצי:\n{error_msg}")
            finally:
                cursor.close()
                conn.close()


# =========================================================================
# 🏢 טאב 3: חברות הפצה ואזורי שירות
# =========================================================================
def setup_companies_tab(tab):
    btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
    btn_frame.pack(fill="x", pady=(10, 10))
    
    ctk.CTkButton(btn_frame, text="✏️ עריכת אזור שירות קיים", font=("Segoe UI", 12, "bold"), fg_color="#3B82F6", hover_color="#2563EB", height=35, corner_radius=10, command=lambda: open_edit_region_modal(tree)).pack(side="left", padx=5)
    ctk.CTkButton(btn_frame, text="🗺️ הגדרת אזור שירות חדש", font=("Segoe UI", 12, "bold"), fg_color="#10B981", hover_color="#059669", height=35, corner_radius=10, command=lambda: open_region_modal(tree)).pack(side="left", padx=5)
    ctk.CTkButton(btn_frame, text="➕ רישום חברת הפצה חדשה", font=("Segoe UI", 12, "bold"), fg_color="#10B981", hover_color="#059669", height=35, corner_radius=10, command=lambda: open_company_modal(tree)).pack(side="right", padx=5)

    table_container = ctk.CTkFrame(tab, fg_color="#FFFFFF", corner_radius=12, border_color="#E5E7EB", border_width=1)
    table_container.pack(fill="both", expand=True, pady=5)
    table_container.grid_rowconfigure(0, weight=1)
    table_container.grid_columnconfigure(0, weight=0)
    table_container.grid_columnconfigure(1, weight=1)

    # === ✨ תוספת עבור כיתוב כחול כהה ומודגש בטבלת חברות ההפצה ===
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Custom.Treeview",
                    background="#FFFFFF",
                    foreground="#1E3A8A",  # צבע כחול כהה בולט
                    rowheight=40,
                    fieldbackground="#FFFFFF",
                    font=("Segoe UI", 12, "bold"),  # כתב עבה ומודגש
                    borderwidth=0,
                    relief="flat")
    
    style.configure("Custom.Treeview.Heading",
                    background="#F9FAFB",
                    foreground="#4B5563",
                    font=("Segoe UI", 13, "bold"),
                    relief="flat",
                    borderwidth=0)
    
    style.map("Custom.Treeview", background=[('selected', '#E0F2FE')], foreground=[('selected', '#0369A1')])
    # ==========================================================
    
    columns = ("regions", "email", "phone", "cie_name", "cie_id")
    tree = ttk.Treeview(table_container, columns=columns, show="headings", style="Custom.Treeview")
    
    tree.heading("cie_id", text="קוד חברה")
    tree.heading("cie_name", text="שם חברת משלוחים")
    tree.heading("phone", text="מספר טלפון")
    tree.heading("email", text="כתובת אימייל")
    tree.heading("regions", text="אזורי שירות מורשים ברשת")

    tree.column("cie_id", width=100, anchor="center", stretch=tk.NO)
    tree.column("cie_name", width=180, anchor="e", stretch=tk.NO)
    tree.column("phone", width=130, anchor="center", stretch=tk.NO)
    # --- ✨ תיקון: הגדלת שטח הרוחב לעמודת כתובת מייל מ-180 ל-260 ---
    tree.column("email", width=260, anchor="center", stretch=tk.NO)
    # --- ✨ תיקון: רישום תוכן עמודת אזורי שירות משמאל לימין באמצעות שינוי ה-anchor ל-"w" ---
    tree.column("regions", width=500, anchor="w", stretch=tk.YES) 

    v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=tree.yview)
    h_scrollbar = ttk.Scrollbar(table_container, orient="horizontal", command=tree.xview) 
    tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
    
    h_scrollbar.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=(0, 10))
    v_scrollbar.grid(row=0, column=0, sticky="ns", pady=10, padx=(10, 0)) 
    tree.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=(10, 2))

    actions = ctk.CTkFrame(tab, fg_color="transparent")
    actions.pack(fill="x", pady=(15, 10))
    ctk.CTkButton(actions, text="✏️ עריכת פרטי חברה", font=("Segoe UI", 13, "bold"), fg_color="#10B981", hover_color="#059669", height=38, width=160, corner_radius=10, command=lambda: edit_company(tree)).pack(side="right", padx=5)
    ctk.CTkButton(actions, text="🗑️ הסרת חברת הפצה", font=("Segoe UI", 13, "bold"), fg_color="#EF4444", hover_color="#DC2626", height=38, width=160, corner_radius=10, command=lambda: delete_company(tree)).pack(side="right", padx=25)
    ctk.CTkButton(actions, text="🗑️ הסרת אזור שירות", font=("Segoe UI", 13, "bold"), fg_color="#EF4444", hover_color="#DC2626", height=38, width=160, corner_radius=10, command=lambda: delete_region(tree)).pack(side="left", padx=5)

    refresh_companies_data(tree)


def refresh_companies_data(tree):
    for item in tree.get_children(): tree.delete(item)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
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
                    conn.commit()
                    messagebox.showinfo("הצלחה", "פרטי החברה עודכנו בהצלחה!")
                    modal.destroy()
                    refresh_companies_data(tree)
                else:
                    cursor.execute("INSERT INTO DELIVERYCOMPANY (DeliveryCieID, DeliveryCieName, DeliveryCiePhoneNb, Email) VALUES (%s, %s, %s, %s);",
                                   (int(c_id), name, phone, email))
                    conn.commit()
                    messagebox.showinfo("הצלחה", "חברת ההפצה החדשה נרשמה בהצלחה!")
                    modal.destroy()
                    refresh_companies_data(tree)
            except Exception as e:
                error_msg = str(e)
                if "duplicate key" in error_msg or "already exists" in error_msg:
                    messagebox.showerror("קוד חברה תפוס", f"לא ניתן לבצע רישום.\nקוד חברה מספר {c_id} או שם החברה כבר קיימים ותפוסים ברשת!")
                else:
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
                error_msg = str(e)
                if "foreign key constraint" in error_msg or "is still referenced" in error_msg:
                    messagebox.showerror(
                        "לא ניתן למחוק חברה", 
                        f"פעולת המחיקה עבור חברת ההפצה מספר {c_id} נחסמה באופן מאובטח.\n\n"
                        f"💡 הסיבה:\n"
                        f"חברה זו מחזיקה כעת במשאיות ונהגים פעילים הרשומים תחתיה בצי הרשת.\n\n"
                        f"🛠️ מה צריך לעשות?\n"
                        f"יש להעביר את המשאיות לחברה אחרת או למחוק אותן תחילה בלשונית 'צי משאיות ונהגים', ורק אז תוכלי למחוק חברה זו."
                    )
                else:
                    messagebox.showerror("חסימת מחיקה", f"לא ניתן למחוק חברה זו:\n{error_msg}")
            finally:
                cursor.close()
                conn.close()


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


def open_edit_region_modal(tree):
    sel = tree.selection()
    if not sel: return messagebox.showwarning("בחירה חובה", "אנא בחרי חברה מהטבלה כדי לערוך את אזורי השירות שלה.")
    c_id = tree.item(sel[0], 'values')[4]
    
    modal = ctk.CTkToplevel()
    modal.title("עריכת אזור שירות")
    modal.geometry("380x300")
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
        return messagebox.showwarning("שגיאה", "לחברה זו אין אזורי שירות מוגדרים שניתן לערוך.")

    ctk.CTkLabel(modal, text="✏️ עריכת אזור שירות קיים", font=("Segoe UI", 15, "bold")).pack(pady=10)
    
    ctk.CTkLabel(modal, text="בחרי את האזור הנוכחי שברצונך לשנות", font=("Segoe UI", 11), text_color="#4B5563").pack(anchor="e", padx=40)
    r_option = ctk.CTkOptionMenu(modal, values=regions_list)
    r_option.pack(fill="x", padx=40, pady=5)
    
    ctk.CTkLabel(modal, text="הזיני את השם החדש לאזור זה", font=("Segoe UI", 11), text_color="#4B5563").pack(anchor="e", padx=40)
    new_reg_entry = ctk.CTkEntry(modal, justify="right")
    new_reg_entry.pack(fill="x", padx=40, pady=5)

    def do_update():
        old_reg = r_option.get()
        new_reg = new_reg_entry.get().strip()
        if not new_reg: return messagebox.showwarning("שדה ריק", "אנא הזיני שם אזור חדש.")
        
        conn_u = get_db_connection()
        if conn_u:
            cursor_u = conn_u.cursor()
            try:
                cursor_u.execute("""
                    UPDATE DELIVERYCOMPANY_REGIONSERVED 
                    SET RegionServed=%s 
                    WHERE DeliveryCieID=%s AND RegionServed=%s;
                """, (new_reg, int(c_id), old_reg))
                conn_u.commit()
                cursor_u.close()
                conn_u.close()
                modal.destroy()
                refresh_companies_data(tree)
            except Exception as e:
                messagebox.showerror("שגיאה כפילות", "השם החדש שהזנת כבר קיים עבור חברה זו.")

    ctk.CTkButton(modal, text="שמור", fg_color="#3B82F6", hover_color="#2563EB", height=38, command=do_update).pack(pady=15)


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


# =========================================================================
# 🧮 פונקציות העריכה וההפעלה החדשות עבור ה-PL/pgSQL שביקשת
# =========================================================================
def open_calculate_price_modal(tree):
    """חלונית מודאלית להזנת אחוז סיטונאי והפעלת הפונקציה calculate_order_price"""
    sel = tree.selection()
    if not sel: 
        return messagebox.showwarning("בחירה חובה", "אנא בחרי שורת הזמנה מהטבלה לצורך חישוב עלות.")
    
    vals = tree.item(sel[0], 'values')
    o_id = vals[6]
    
    modal = ctk.CTkToplevel()
    modal.title("חישוב עלות רכש מספק")
    modal.geometry("380x220")
    modal.grab_set()
    
    ctk.CTkLabel(modal, text=f"📊 חישוב עלות סיטונאית להזמנה {o_id}", font=("Segoe UI", 14, "bold")).pack(pady=15)
    ctk.CTkLabel(modal, text="הזן אחוז עלות מהמחירון הכללי בין 1 ל-100", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    
    percent_entry = ctk.CTkEntry(modal, justify="center", font=("Segoe UI", 13), placeholder_text="לדוגמה: 65")
    percent_entry.pack(fill="x", padx=40, pady=5)
    
    def execute_calc():
        percent_str = percent_entry.get().strip()
        if not percent_str:
            return messagebox.showwarning("שדה חסר", "אנא הזיני אחוז תקין.")
        try:
            percent_val = float(percent_str)
        except ValueError:
            return messagebox.showerror("קלט שגוי", "האחוז חייב להיות ערך מספרי.")
            
        if percent_val < 1.0 or percent_val > 100.0:
            return messagebox.showwarning("ערך מחוץ לטווח", "אחוז עלות סיטונאית חייב להיות מספר בין 1 ל-100 בלבד.")
            
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT COUNT(*) FROM CONTAINS WHERE OrderId = %s;", (int(o_id),))
                items_in_order = cursor.fetchone()[0]
                
                if items_in_order == 0:
                    cursor.execute('UPDATE "ORDER" SET Price = 0 WHERE OrderId = %s;', (int(o_id),))
                    conn.commit()
                    messagebox.showinfo("החישוב הסתיים", f"הזמנה מספר {o_id} אינה מכילה מוצרים.\n\nהעלות הסיטונאית עודכנה אוטומטית ל-₪0.00 ללא שגיאה!")
                    modal.destroy()
                    refresh_orders_data(tree)
                    return
                
                cursor.execute("SELECT calculate_order_price(%s, %s);", (int(o_id), percent_val))
                new_price = cursor.fetchone()[0]
                conn.commit()
                
                messagebox.showinfo("החישוב הסתיים", f"הפונקציה רצה בהצלחה!\n\nהעלות הסיטונאית המעודכנת שחושבה עבור הזמנה מספר {o_id} היא:\n₪{new_price:,.2f}")
                modal.destroy()
                refresh_orders_data(tree)
            except Exception as e:
                messagebox.showerror("שגיאה / חריגה מבוקרת", f"הפונקציה נכשלה או חסמה את הפעולה:\n{str(e)}")
            finally:
                cursor.close()
                conn.close()

    ctk.CTkButton(modal, text="הנתונים לבסיס מחיר הזן", fg_color="#2563EB", hover_color="#1D4ED8", height=35, command=execute_calc).pack(pady=15)


def trigger_complete_order_procedure(tree):
    """מפעיל את הפרוצדורה complete_order_and_update_stock ומציג כמה מוצרים עודכנו במלאי"""
    sel = tree.selection()
    if not sel: 
        return messagebox.showwarning("בחירה חובה", "אנא בחרי שורת הזמנה לצורך השלמה וקליטה במלאי.")
        
    vals = tree.item(sel[0], 'values')
    o_id = vals[6]
    current_status = vals[0]
    
    if current_status == "COMPLETED":
        return messagebox.showwarning("הזמנה סגורה", f"הזמנה מספר {o_id} כבר סומנה כ-COMPLETED בעבר והמלאי עודכן.")
        
    if not messagebox.askyesno("אישור קליטת מלאי", f"האם את בטוחה שברצונך להשלים את הזמנה מספר {o_id}?\n\nפעולה זו תפעיל פרוצדורת שרת ותעדכן את המלאי בחנות."):
        return
        
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM CONTAINS WHERE OrderId = %s;", (int(o_id),))
            items_count = cursor.fetchone()[0]
            
            cursor.execute("CALL complete_order_and_update_stock(%s);", (int(o_id),))
            conn.commit()
            
            messagebox.showinfo("קליטה הצליחה", 
                                f"🎉 הפרוצדורה בוצעה בהצלחה!\n\n"
                                f"📊 סיכום פעולת קליטת המלאי:\n"
                                f"▫️ סטטוס ההזמנה עודכן ל-COMPLETED.\n"
                                f"▫️ עודכנו ונקלטו בהצלחה: {items_count} מוצרים שונים במלאי החנות.\n\n"
                                f"הנתונים בטבלת INVENTORY סונכרנו.")
            refresh_orders_data(tree)
        except Exception as e:
            messagebox.showerror("שגיאה בפרוצדורה", f"הפרוצדורה נכשלה או זרקה חריגה מבוקרת:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()