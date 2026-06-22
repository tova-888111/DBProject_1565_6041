import customtkinter as ctk
from tkinter import ttk, messagebox
import tkinter as tk
from db_connection import get_db_connection
from datetime import datetime

def show_inventory_view(main_frame):
    # ניקוי המסך למניעת כפילויות תצוגה
    for widget in main_frame.winfo_children():
        widget.destroy()

    # --- כותרת עליונה ראשית ---
    header_label = ctk.CTkLabel(main_frame, text="ניהול מלאי וקטלוג מוצרים רשתי", font=("Segoe UI", 32, "bold"), text_color="#111827", anchor="e")
    header_label.pack(pady=(35, 4), padx=35, fill="x")
    
    sub_header = ctk.CTkLabel(main_frame, text="ניהול פריטי הקטלוג, מחלקות הרשת, רמות מלאי בסניפים וסטטוסי כשרות", font=("Segoe UI", 14, "bold"), text_color="#4B5563", anchor="e")
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

    tab_products = tabview.add("🍎  קטלוג מוצרים וכשרות")
    tab_categories = tabview.add("🗂️  קטגוריות")
    tab_inventory = tabview.add("📊  מלאי בסניפים")

    setup_products_tab(tab_products)
    setup_categories_tab(tab_categories)
    setup_inventory_tab(tab_inventory)


# =========================================================================
# 📑 טאב 1: קטלוג מוצרים וכשרות (PRODUCT + PRODUCT_KASHRUT)
# =========================================================================
def setup_products_tab(tab):
    # שורת מסנני חיפוש סימטרית ואחידה באמצעות מנגנון Grid
    search_frame = ctk.CTkFrame(tab, fg_color="transparent")
    search_frame.pack(fill="x", pady=(5, 12))
    
    search_frame.grid_columnconfigure(0, weight=1) 
    
    search_lbl = ctk.CTkLabel(search_frame, text="🔍  מסנני חיפוש", font=("Segoe UI", 13, "bold"), text_color="#374151")
    search_lbl.grid(row=0, column=4, padx=(10, 15), sticky="e")
    
    search_id_entry = ctk.CTkEntry(search_frame, placeholder_text="לפי קוד מוצר", font=("Segoe UI", 12), width=165, height=35, corner_radius=8, justify="right")
    search_id_entry.grid(row=0, column=3, padx=6, sticky="e")
    
    search_name_entry = ctk.CTkEntry(search_frame, placeholder_text="לפי שם מוצר", font=("Segoe UI", 12), width=165, height=35, corner_radius=8, justify="right")
    search_name_entry.grid(row=0, column=2, padx=6, sticky="e")

    search_cat_entry = ctk.CTkEntry(search_frame, placeholder_text="לפי קוד קטגוריה", font=("Segoe UI", 12), width=165, height=35, corner_radius=8, justify="right")
    search_cat_entry.grid(row=0, column=1, padx=6, sticky="e")

    search_id_entry.bind("<KeyRelease>", lambda event: refresh_products_data(tree, search_id_entry.get().strip(), search_name_entry.get().strip(), search_cat_entry.get().strip()))
    search_name_entry.bind("<KeyRelease>", lambda event: refresh_products_data(tree, search_id_entry.get().strip(), search_name_entry.get().strip(), search_cat_entry.get().strip()))
    search_cat_entry.bind("<KeyRelease>", lambda event: refresh_products_data(tree, search_id_entry.get().strip(), search_name_entry.get().strip(), search_cat_entry.get().strip()))

    # שורת פעולות עליונה
    btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
    btn_frame.pack(fill="x", pady=(0, 10))
    
    ctk.CTkButton(btn_frame, text="📜 ניהול כשרויות המוצר", font=("Segoe UI", 12, "bold"), fg_color="#8B5CF6", hover_color="#7C3AED", height=35, corner_radius=10, command=lambda: open_kashrut_manager_modal(tree)).pack(side="left", padx=5)
    ctk.CTkButton(btn_frame, text="➕ הוספת מוצר חדש", font=("Segoe UI", 12, "bold"), fg_color="#10B981", hover_color="#059669", height=35, corner_radius=10, command=lambda: open_product_modal(tree)).pack(side="right", padx=5)

    table_container = ctk.CTkFrame(tab, fg_color="#FFFFFF", corner_radius=12, border_color="#E5E7EB", border_width=1)
    table_container.pack(fill="both", expand=True, pady=5)
    table_container.grid_rowconfigure(0, weight=1)
    table_container.grid_columnconfigure(0, weight=0)
    table_container.grid_columnconfigure(1, weight=1)

    style = ttk.Style()
    style.theme_use("clam")
    
    # ✨ בידוד סטייל: שינוי שם הסטייל ל-Prod.Treeview למניעת התנגשויות ודריסת צבעים
    style.configure("Prod.Treeview",
                    background="#FFFFFF",
                    foreground="#1E3A8A", 
                    rowheight=40,
                    fieldbackground="#FFFFFF",
                    font=("Segoe UI", 12, "bold"), 
                    borderwidth=0,
                    relief="flat")
    
    style.configure("Prod.Treeview.Heading",
                    background="#F9FAFB",
                    foreground="#4B5563",
                    font=("Segoe UI", 13, "bold"),
                    relief="flat",
                    borderwidth=0)
    
    style.map("Prod.Treeview", background=[('selected', '#E0F2FE')], foreground=[('selected', '#0369A1')])

    columns = ("exp_date", "prod_date", "category_name", "brand", "price", "product_name", "product_id", "hidden_cat_id")
    tree = ttk.Treeview(table_container, columns=columns, show="headings", style="Prod.Treeview")
    
    tree.heading("product_id", text="קוד מוצר", anchor="center")
    tree.heading("product_name", text="שם מוצר", anchor="center")
    tree.heading("price", text="מחיר רשת", anchor="center")
    tree.heading("brand", text="מותג/יצרן", anchor="center")
    tree.heading("category_name", text="קטגוריית שיוך", anchor="center")
    tree.heading("prod_date", text="תאריך ייצור", anchor="center")
    tree.heading("exp_date", text="תאריך תפוגה", anchor="center")

    tree.column("product_id", width=110, anchor="center", stretch=tk.NO)
    tree.column("product_name", width=280, anchor="e", stretch=tk.YES)
    tree.column("price", width=120, anchor="center", stretch=tk.NO)
    tree.column("brand", width=150, anchor="center", stretch=tk.NO)
    tree.column("category_name", width=280, anchor="center", stretch=tk.NO) 
    tree.column("prod_date", width=140, anchor="center", stretch=tk.NO)
    tree.column("exp_date", width=140, anchor="center", stretch=tk.NO)
    tree.column("hidden_cat_id", width=0, stretch=tk.NO)

    v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=tree.yview)
    h_scrollbar = ttk.Scrollbar(table_container, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
    
    h_scrollbar.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=(0, 10))
    v_scrollbar.grid(row=0, column=0, sticky="ns", pady=10, padx=(10, 0))
    tree.grid(row=0, column=1, sticky="nsew", padx=10, pady=(10, 2))

    actions = ctk.CTkFrame(tab, fg_color="transparent")
    actions.pack(fill="x", pady=(10, 5))
    
    ctk.CTkButton(actions, text="✏️ עריכת פרטי מוצר", font=("Segoe UI", 12, "bold"), fg_color="#3B82F6", hover_color="#2563EB", height=35, corner_radius=10, command=lambda: edit_product(tree)).pack(side="right", padx=5)
    ctk.CTkButton(actions, text="🗑️ מחיקת מוצר מהקטלוג", font=("Segoe UI", 12, "bold"), fg_color="#EF4444", hover_color="#DC2626", height=35, corner_radius=10, command=lambda: delete_product(tree)).pack(side="right", padx=25)

    refresh_products_data(tree)


def refresh_products_data(tree, search_id="", search_name="", search_cat_id=""):
    for item in tree.get_children(): tree.delete(item)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
            SELECT p.ProductID, p.ProductName, p.Price, p.Brand, c.CategoryName,
                   p.CategoryID, p.dateofmanufacture, p.ExpirationDate
            FROM PRODUCT p
            JOIN CATEGORY c ON p.CategoryID = c.CategoryID
            WHERE 1=1
        """
        params = []
        if search_id and search_id.isdigit():
            query += " AND p.ProductID = %s"
            params.append(int(search_id))
        if search_name:
            query += " AND p.ProductName ILIKE %s"
            params.append(f"%{search_name}%")
        if search_cat_id and search_cat_id.isdigit():
            query += " AND p.CategoryID = %s"
            params.append(int(search_cat_id))
            
        query += " ORDER BY p.ProductID ASC;"
        cursor.execute(query, tuple(params))
        for row in cursor.fetchall():
            p_date = row[6].strftime('%Y-%m-%d') if row[6] else "-"
            e_date = row[7].strftime('%Y-%m-%d') if row[7] else "-"
            tree.insert("", "end", values=(e_date, p_date, row[4], row[3], f"₪{row[2]:,.2f}", row[1], row[0], row[5]))
        cursor.close()
        conn.close()


def open_product_modal(tree, edit_data=None):
    is_edit = edit_data is not None
    modal = ctk.CTkToplevel()
    modal.title("עריכת מוצר" if is_edit else "הוספת מוצר חדש")
    modal.geometry("440x540")
    try: modal.transient(tree.winfo_toplevel())
    except: pass
    modal.lift()
    modal.focus_force()
    modal.grab_set()

    ctk.CTkLabel(modal, text="🍎 פרטי מוצר רשתי קטלוגי", font=("Segoe UI", 16, "bold")).pack(pady=15)

    categories_list = []
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT CategoryID, CategoryName FROM CATEGORY WHERE IsActive = 1 ORDER BY CategoryID ASC;")
        for r in cursor.fetchall(): categories_list.append(f"{r[0]} - {r[1]}")
        cursor.close()
        conn.close()
    if not categories_list: categories_list = ["אין קטגוריות פעילות"]

    ctk.CTkLabel(modal, text="קוד מוצר מספר", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    id_entry = ctk.CTkEntry(modal, justify="right")
    id_entry.pack(fill="x", padx=40, pady=2)
    if is_edit:
        id_entry.insert(0, edit_data[6]) 
        id_entry.configure(state="disabled", fg_color="#E5E7EB")

    ctk.CTkLabel(modal, text="שם המוצר", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    name_entry = ctk.CTkEntry(modal, justify="right")
    name_entry.pack(fill="x", padx=40, pady=2)
    if is_edit: name_entry.insert(0, edit_data[5]) 

    ctk.CTkLabel(modal, text="מחיר לצרכן (בשקלים)", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    price_entry = ctk.CTkEntry(modal, justify="right")
    price_entry.pack(fill="x", padx=40, pady=2)
    if is_edit: price_entry.insert(0, edit_data[4].replace("₪", "").replace(",", "")) 

    ctk.CTkLabel(modal, text="מותג / יצרן", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    brand_entry = ctk.CTkEntry(modal, justify="right")
    brand_entry.pack(fill="x", padx=40, pady=2)
    if is_edit: brand_entry.insert(0, edit_data[3]) 

    ctk.CTkLabel(modal, text="תאריך ייצור (YYYY-MM-DD)", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    prod_date_entry = ctk.CTkEntry(modal, justify="right")
    prod_date_entry.pack(fill="x", padx=40, pady=2)
    if is_edit: prod_date_entry.insert(0, edit_data[1]) 
    else: prod_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))

    ctk.CTkLabel(modal, text="תאריך תפוגה (YYYY-MM-DD)", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    exp_date_entry = ctk.CTkEntry(modal, justify="right")
    exp_date_entry.pack(fill="x", padx=40, pady=2)
    if is_edit: exp_date_entry.insert(0, edit_data[0]) 
    else: exp_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))

    ctk.CTkLabel(modal, text="קטגוריית שיוך מחלקתית", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    cat_option = ctk.CTkOptionMenu(modal, values=categories_list)
    cat_option.pack(fill="x", padx=40, pady=2)
    if is_edit:
        for cat_str in categories_list:
            if cat_str.startswith(str(edit_data[7]) + " -"): cat_option.set(cat_str) 

    def save():
        p_id = id_entry.get().strip()
        p_name = name_entry.get().strip()
        price = price_entry.get().strip()
        brand = brand_entry.get().strip()
        p_date = prod_date_entry.get().strip()
        e_date = exp_date_entry.get().strip()
        cat_sel = cat_option.get()

        if not p_id or not p_name or not price or not brand or not p_date or not e_date or cat_sel.startswith("אין"):
            messagebox.showwarning("שדות חסרים", "אנא מלאי את כל שדות החובה בצורה תקינה.")
            return

        try:
            price_val = float(price)
            if price_val < 0: raise ValueError()
        except ValueError:
            messagebox.showwarning("קלט שגוי", "המחיר חייב להיות מספר חיובי תקין.")
            return

        try:
            p_dt = datetime.strptime(p_date, "%Y-%m-%d").date()
            e_dt = datetime.strptime(e_date, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showwarning("פורמט שגוי", "התאריך הוקלד בצורה שגויה. השתמשי במבנה: YYYY-MM-DD")
            return
            
        cat_id = int(cat_sel.split(" - ")[0])

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                if is_edit:
                    cursor.execute("UPDATE PRODUCT SET ProductName=%s, Price=%s, Brand=%s, dateofmanufacture=%s, ExpirationDate=%s, CategoryID=%s WHERE ProductID=%s;",
                                   (p_name, price_val, brand, p_dt, e_dt, cat_id, int(p_id)))
                else:
                    cursor.execute("INSERT INTO PRODUCT (ProductID, ProductName, Price, Brand, ExpirationDate, dateofmanufacture, CategoryID) VALUES (%s, %s, %s, %s, %s, %s, %s);",
                                   (int(p_id), p_name, price_val, brand, e_dt, p_dt, cat_id))
                conn.commit()
                modal.destroy()
                refresh_products_data(tree)
            except Exception as e:
                error_msg = str(e)
                if "duplicate key" in error_msg or "already exists" in error_msg:
                    messagebox.showerror("קוד מוצר קיים במערכת", f"לא ניתן להוסיף את המוצר.\nקוד מוצר מספר {p_id} כבר רשום ותפוס במערכת על ידי מוצר אחר!\nאנא בחר קוד מוצר פנוי.")
                else:
                    messagebox.showerror("שגיאה", f"הפעולה נכשלה:\n{error_msg}")
            finally:
                cursor.close()
                conn.close()

    ctk.CTkButton(modal, text="שמור", fg_color="#10B981", hover_color="#059669", height=38, corner_radius=8, command=save).pack(pady=15)

def edit_product(tree):
    sel = tree.selection()
    if not sel: return messagebox.showwarning("בחירה חובה", "אנא בחר מוצר מהטבלה לעריכה.")
    open_product_modal(tree, tree.item(sel[0], 'values'))

def delete_product(tree):
    sel = tree.selection()
    if not sel: return messagebox.showwarning("בחירה חובה", "אנא בחר מוצר למחיקה.")
    p_id = tree.item(sel[0], 'values')[6] 
    
    if messagebox.askyesno("אישור מחיקה", f"האם את בטוחה שברצונך למחוק את המוצר מספר '{p_id}' מהקטלוג?"):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM PRODUCT WHERE ProductID = %s;", (int(p_id),))
                conn.commit()
                refresh_products_data(tree)
            except Exception as e:
                error_msg = str(e)
                if "foreign key constraint" in error_msg or "is still referenced" in error_msg:
                    messagebox.showerror(
                        "לא ניתן למחוק מוצר", 
                        f"פעולת המחיקה עבור המוצר נחסמה באופן מאובטח.\n\n"
                        f"💡 מדוע זה קרה?\n"
                        f"מוצר זה נמצא כרגע במלאי של אחד או יותר מסניפי הרשת (טבלת מלאי), משויך למבצע הנחות פעיל או קשור להזמנות הפצה.\n\n"
                        f"🛠️ מה צריך לעשות?\n"
                        f"יש לאפס את כמויות המלאי שלו בסניפים (בלשונית מלאי בסניפים) ולבטל מבצעים מקושרים לפני שניתן יהיה למחוק אותו סופית מהמערכת."
                    )
                else:
                    messagebox.showerror("שגיאה במחיקה", f"פעולת המחיקה נכשלה:\n{error_msg}")
            finally:
                cursor.close()
                conn.close()


# =========================================================================
# 📜 חלון ניהול כשרויות (רב-ערכי משולב בטבלה וניהול מלא בתוך חלון אחד)
# =========================================================================
def open_kashrut_manager_modal(main_tree):
    sel = main_tree.selection()
    if not sel: return messagebox.showwarning("בחירה חובה", "אנא בחר מוצר מהטבלה לצורך ניהול הכשרויות שלו.")
    
    vals = main_tree.item(sel[0], 'values')
    p_id = int(vals[6]) 
    p_name = vals[5]   

    modal = ctk.CTkToplevel()
    modal.title(f"ניהול כשרויות פריט - קוד {p_id}")
    modal.geometry("540x460")
    modal.grab_set()

    ctk.CTkLabel(modal, text=f"📜 רשימת כשרויות: {p_name}", font=("Segoe UI", 16, "bold")).pack(pady=10)

    add_frame = ctk.CTkFrame(modal, fg_color="transparent")
    add_frame.pack(fill="x", padx=25, pady=5)
    
    k_entry = ctk.CTkEntry(add_frame, placeholder_text=" להוספה חדשה כשרות שם הקלד", justify="right", width=280, height=35)
    k_entry.pack(side="right", padx=5)

    def add_kashrut():
        k_val = k_entry.get().strip()
        if not k_val: return messagebox.showwarning("קלט חסר", "אנא הקלידי את שם הכשרות.")
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO PRODUCT_KASHRUT (ProductID, Kashrut) VALUES (%s, %s);", (p_id, k_val))
                conn.commit()
                k_entry.delete(0, tk.END)
                refresh_kashrut_sub_table(sub_tree, p_id)
            except:
                messagebox.showerror("כפילות", "כשרות זו כבר מוגדרת עבור המוצר הנוכחי!")
            finally:
                cursor.close()
                conn.close()

    ctk.CTkButton(add_frame, text="➕ הוספת כשרות", fg_color="#10B981", hover_color="#059669", height=35, font=("Segoe UI", 12, "bold"), command=add_kashrut).pack(side="left", padx=5)

    table_container = ctk.CTkFrame(modal, fg_color="#FFFFFF", corner_radius=8, border_color="#E5E7EB", border_width=1)
    table_container.pack(fill="both", expand=True, padx=25, pady=10)
    table_container.grid_rowconfigure(0, weight=1)
    table_container.grid_columnconfigure(0, weight=0) 
    table_container.grid_columnconfigure(1, weight=1) 

    # ✨ תיקון: הצמדת סטייל ה-Prod.Treeview המבודד גם לתת-הטבלה הפנימית של הכשרויות
    sub_tree = ttk.Treeview(table_container, columns=("kashrut_name"), show="headings", style="Prod.Treeview")
    sub_tree.heading("kashrut_name", text="סוג כשרות מאושר ומחייב", anchor="center")
    sub_tree.column("kashrut_name", width=420, anchor="center")
    
    sub_v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=sub_tree.yview)
    sub_tree.configure(yscrollcommand=sub_v_scrollbar.set)
    
    sub_v_scrollbar.grid(row=0, column=0, sticky="ns", pady=5, padx=(5, 0))
    sub_tree.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

    actions_frame = ctk.CTkFrame(modal, fg_color="transparent")
    actions_frame.pack(fill="x", padx=25, pady=(5, 15))

    def edit_kashrut():
        sub_sel = sub_tree.selection()
        if not sub_sel: return messagebox.showwarning("בחירה חובה", "אנא בחר כשרות מהרשימה לצורך עריכה.")
        old_kashrut = sub_tree.item(sub_sel[0], 'values')[0]

        edit_modal = ctk.CTkToplevel()
        edit_modal.title("עדכון שם כשרות")
        edit_modal.geometry("340x160")
        edit_modal.grab_set()

        ctk.CTkLabel(edit_modal, text="שם כשרות מעודכן:", font=("Segoe UI", 12, "bold")).pack(pady=10)
        edit_entry = ctk.CTkEntry(edit_modal, justify="right", width=220)
        edit_entry.pack(pady=5)
        edit_entry.insert(0, old_kashrut)

        def save_edited_kashrut():
            new_kashrut = edit_entry.get().strip()
            if not new_kashrut: return messagebox.showwarning("שגיאה", "השם לא יכול להיות ריק.")
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("UPDATE PRODUCT_KASHRUT SET Kashrut=%s WHERE ProductID=%s AND Kashrut=%s;", (new_kashrut, p_id, old_kashrut))
                    conn.commit()
                    edit_modal.destroy()
                    refresh_kashrut_sub_table(sub_tree, p_id)
                except Exception as e:
                    messagebox.showerror("שגיאה", f"העדכון נכשל, ייתכן והשם כפול:\n{e}")
                finally:
                    cursor.close()
                    conn.close()

        ctk.CTkButton(edit_modal, text="שמור שינוי", fg_color="#3B82F6", command=save_edited_kashrut).pack(pady=10)

    def delete_kashrut():
        sub_sel = sub_tree.selection()
        if not sub_sel: return messagebox.showwarning("בחירה חובה", "אנא בחר כשרות מהטבלה לצורך מחיקה.")
        target_kashrut = sub_tree.item(sub_sel[0], 'values')[0]

        if messagebox.askyesno("אישור מחיקה", f"האם את בטוחה שברצונך למחוק את הכשרות '{target_kashrut}' ממוצר זה?"):
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("DELETE FROM PRODUCT_KASHRUT WHERE ProductID=%s AND Kashrut=%s;", (p_id, target_kashrut))
                    conn.commit()
                    refresh_kashrut_sub_table(sub_tree, p_id)
                except Exception as e:
                    messagebox.showerror("שגיאה", f"המחיקה נכשלה:\n{e}")
                finally:
                    cursor.close()
                    conn.close()

    ctk.CTkButton(actions_frame, text="✏️כשרות עריכת ", fg_color="#3B82F6", hover_color="#2563EB", height=35, command=edit_kashrut).pack(side="right", padx=5, expand=True, fill="x")
    ctk.CTkButton(actions_frame, text="🗑️כשרות מחיקת  ", fg_color="#EF4444", hover_color="#DC2626", height=35, command=delete_kashrut).pack(side="left", padx=5, expand=True, fill="x")

    refresh_kashrut_sub_table(sub_tree, p_id)


def refresh_kashrut_sub_table(tree, product_id):
    for item in tree.get_children(): tree.delete(item)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT Kashrut FROM PRODUCT_KASHRUT WHERE ProductID = %s ORDER BY Kashrut ASC;", (product_id,))
        for row in cursor.fetchall():
            tree.insert("", "end", values=(row[0],))
        cursor.close()
        conn.close()


# =========================================================================
# 🗂️ טאב 2: קטגוריות
# =========================================================================
def setup_categories_tab(tab):
    btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
    btn_frame.pack(fill="x", pady=(10, 10))
    ctk.CTkButton(btn_frame, text="➕ הוספת קטגוריה חדשה", font=("Segoe UI", 12, "bold"), fg_color="#10B981", hover_color="#059669", height=35, corner_radius=10, command=lambda: open_category_modal(tree)).pack(side="right", padx=5)

    table_container = ctk.CTkFrame(tab, fg_color="#FFFFFF", corner_radius=12, border_color="#E5E7EB", border_width=1)
    table_container.pack(fill="both", expand=True, pady=5)
    table_container.grid_rowconfigure(0, weight=1)
    table_container.grid_columnconfigure(0, weight=0)
    table_container.grid_columnconfigure(1, weight=1)

    columns = ("status", "category_name", "category_id")
    # ✨ תיקון: הצמדת סטייל ה-Prod.Treeview המבודד גם לטבלת הקטגוריות
    tree = ttk.Treeview(table_container, columns=columns, show="headings", style="Prod.Treeview")
    
    tree.heading("category_id", text="קוד קטגוריה", anchor="center")
    tree.heading("category_name", text="שם המחלקה/קטגוריה", anchor="center")
    tree.heading("status", text="סטטוס פעילות", anchor="center")

    tree.column("category_id", width=120, anchor="center", stretch=tk.YES)
    tree.column("category_name", width=350, anchor="e", stretch=tk.YES)
    tree.column("status", width=180, anchor="center", stretch=tk.YES)

    tree.tag_configure("active_cat", background="#E8F5E9", foreground="#155724")
    tree.tag_configure("inactive_cat", background="#FEF2F2", foreground="#991B1B")

    v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=v_scrollbar.set)
    v_scrollbar.grid(row=0, column=0, sticky="ns", pady=10, padx=(10, 0))
    tree.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    actions = ctk.CTkFrame(tab, fg_color="transparent")
    actions.pack(fill="x", pady=(10, 5))
    
    ctk.CTkButton(actions, text="✏️ עריכת קטגוריה", font=("Segoe UI", 12, "bold"), fg_color="#3B82F6", hover_color="#2563EB", height=35, corner_radius=10, command=lambda: edit_category(tree)).pack(side="right", padx=5)
    ctk.CTkButton(actions, text="🗑️ מחיקת קטגוריה מהרשת", font=("Segoe UI", 12, "bold"), fg_color="#EF4444", hover_color="#DC2626", height=35, corner_radius=10, command=lambda: delete_category(tree)).pack(side="right", padx=25)

    refresh_categories_data(tree)


def refresh_categories_data(tree):
    for item in tree.get_children(): tree.delete(item)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT CategoryID, CategoryName, IsActive FROM CATEGORY ORDER BY CategoryID ASC;")
        for row in cursor.fetchall():
            if row[2] == 1:
                status_text = "🟢 פעילה במערכת"
                row_tag = "active_cat" 
            else:
                status_text = "🔴 לא פעילה"
                row_tag = "inactive_cat"
            tree.insert("", "end", values=(status_text, row[1], row[0]), tags=(row_tag,))
        cursor.close()
        conn.close()


def open_category_modal(tree, edit_data=None):
    is_edit = edit_data is not None
    modal = ctk.CTkToplevel()
    modal.title("עריכת קטגוריה" if is_edit else "הוספת קטגוריה")
    modal.geometry("380x300")
    try: modal.transient(tree.winfo_toplevel())
    except: pass
    modal.lift()
    modal.focus_force()
    modal.grab_set()

    ctk.CTkLabel(modal, text="🗂️ פרטי מחלקה ברשת", font=("Segoe UI", 16, "bold")).pack(pady=15)

    ctk.CTkLabel(modal, text="קוד קטגוריה מספר", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    id_entry = ctk.CTkEntry(modal, justify="right")
    id_entry.pack(fill="x", padx=40, pady=2)
    if is_edit:
        id_entry.insert(0, edit_data[2])
        id_entry.configure(state="disabled", fg_color="#E5E7EB")

    ctk.CTkLabel(modal, text="שם המחלקה/קטגוריה", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    name_entry = ctk.CTkEntry(modal, justify="right")
    name_entry.pack(fill="x", padx=40, pady=2)
    if is_edit: name_entry.insert(0, edit_data[1])

    ctk.CTkLabel(modal, text="סטטוס פעילות", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    status_opt = ctk.CTkOptionMenu(modal, values=["פעילה", "לא פעילה"])
    status_opt.pack(fill="x", padx=40, pady=2)
    if is_edit: status_opt.set("פעילה" if "🟢" in edit_data[0] else "לא פעילה")

    def save():
        c_id = id_entry.get().strip()
        c_name = name_entry.get().strip()
        act_val = 1 if status_opt.get() == "פעילה" else 0

        if not c_id or not c_name:
            messagebox.showwarning("שדות חסרים", "אנא מלאי את כל השדות.")
            return

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                if is_edit:
                    cursor.execute("UPDATE CATEGORY SET CategoryName=%s, IsActive=%s WHERE CategoryID=%s;", (c_name, act_val, int(c_id)))
                else:
                    cursor.execute("INSERT INTO CATEGORY (CategoryID, CategoryName, IsActive) VALUES (%s, %s, %s);", (int(c_id), c_name, act_val))
                conn.commit()
                modal.destroy()
                refresh_categories_data(tree)
            except Exception as e:
                error_msg = str(e)
                if "duplicate key" in error_msg or "already exists" in error_msg:
                    messagebox.showerror("קוד קטגוריה קיים במערכת", f"לא ניתן להוסיף את הקטגוריה.\nקוד מספר {c_id} כבר רשום ותפוס ברשת!")
                else:
                    messagebox.showerror("שגיאה", f"הפעולה נכשלה:\n{error_msg}")
            finally:
                cursor.close()
                conn.close()

    ctk.CTkButton(modal, text="שמור", fg_color="#10B981", hover_color="#059669", height=38, corner_radius=8, command=save).pack(pady=15)

def edit_category(tree):
    sel = tree.selection()
    if not sel: return messagebox.showwarning("בחירה חובה", "אנא בחר קטגוריה לעריכה.")
    open_category_modal(tree, tree.item(sel[0], 'values'))

def delete_category(tree):
    sel = tree.selection()
    if not sel: return messagebox.showwarning("בחירה חובה", "אנא בחר קטגוריה למחיקה.")
    c_id = tree.item(sel[0], 'values')[2]
    c_name = tree.item(sel[0], 'values')[1]

    if messagebox.askyesno("אישור מחיקה", f"האם את בטוחה שברצונך למחוק את קטגוריית '{c_name}'?"):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM CATEGORY WHERE CategoryID = %s;", (int(c_id),))
                conn.commit()
                refresh_categories_data(tree)
            except Exception as e:
                error_msg = str(e)
                if "foreign key constraint" in error_msg or "is still referenced" in error_msg:
                    messagebox.showerror(
                        "חסימת מחיקת קטגוריה", 
                        f"לא ניתן למחוק את קטגוריית '{c_name}' מהמערכת!\n\n"
                        f"הסיבה: קיימים מוצרים פעילים בקטלוג הרשת המשויכים ומסווגים תחת מחלקה זו.\n\n"
                        f"🛠️ מה צריך לעשות?\n"
                        f"יש להעביר תחילה את המוצרים האלו לקטגוריות אחרות או למחוק אותם, ורק אז ניתן יהיה להסיר את הקטגוריה סופית."
                    )
                else:
                    messagebox.showerror("שגיאה", f"פעולת המחיקה נכשלה:\n{error_msg}")
            finally:
                cursor.close()
                conn.close()


# =========================================================================
# 📊 טאב 3: מלאי בסניפים (INVENTORY)
# =========================================================================
def setup_inventory_tab(tab):
    search_frame = ctk.CTkFrame(tab, fg_color="transparent")
    search_frame.pack(fill="x", pady=(5, 10))
    
    search_lbl = ctk.CTkLabel(search_frame, text="🔍  מסנני חיפוש", font=("Segoe UI", 12, "bold"), text_color="#374151")
    search_lbl.pack(side="right", padx=(10, 15))
    
    search_store_entry = ctk.CTkEntry(search_frame, placeholder_text="חפש לפי קוד סניף מדויק", font=("Segoe UI", 12), width=180, height=35, corner_radius=8, justify="right")
    search_store_entry.pack(side="right", padx=(0, 15))
    
    search_prod_entry = ctk.CTkEntry(search_frame, placeholder_text="חפש לפי קוד מוצר מדויק", font=("Segoe UI", 12), width=180, height=35, corner_radius=8, justify="right")
    search_prod_entry.pack(side="right")

    search_store_entry.bind("<KeyRelease>", lambda event: refresh_inventory_data(tree, search_store_entry.get().strip(), search_prod_entry.get().strip()))
    search_prod_entry.bind("<KeyRelease>", lambda event: refresh_inventory_data(tree, search_store_entry.get().strip(), search_prod_entry.get().strip()))

    btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
    btn_frame.pack(fill="x", pady=(0, 10))
    ctk.CTkButton(btn_frame, text="➕ קליטת מלאי חדש לסניף", font=("Segoe UI", 12, "bold"), fg_color="#10B981", hover_color="#059669", height=35, corner_radius=10, command=lambda: open_inventory_modal(tree)).pack(side="right", padx=5)

    table_container = ctk.CTkFrame(tab, fg_color="#FFFFFF", corner_radius=12, border_color="#E5E7EB", border_width=1)
    table_container.pack(fill="both", expand=True, pady=5)
    table_container.grid_rowconfigure(0, weight=1)
    table_container.grid_columnconfigure(0, weight=0)
    table_container.grid_columnconfigure(1, weight=1)

    columns = ("min_stock", "quantity", "product_name", "product_id", "store_name", "store_id")
    # ✨ תיקון: הצמדת סטייל ה-Prod.Treeview המבודד גם לטבלת רמות המלאי בלשונית השלישית
    tree = ttk.Treeview(table_container, columns=columns, show="headings", style="Prod.Treeview")
    
    tree.heading("store_id", text="קוד סניף", anchor="center")
    tree.heading("store_name", text="שם סניף", anchor="center")
    tree.heading("product_id", text="קוד מוצר", anchor="center")
    tree.heading("product_name", text="שם מוצר", anchor="center")
    tree.heading("quantity", text="כמות במלאי", anchor="center")
    tree.heading("min_stock", text="מלאי מינימום", anchor="center")

    tree.column("store_id", width=90, anchor="center", stretch=tk.YES)
    tree.column("store_name", width=160, anchor="e", stretch=tk.YES)
    tree.column("product_id", width=90, anchor="center", stretch=tk.YES)
    tree.column("product_name", width=180, anchor="e", stretch=tk.YES)
    tree.column("quantity", width=110, anchor="center", stretch=tk.YES)
    tree.column("min_stock", width=110, anchor="center", stretch=tk.YES)

    tree.tag_configure("normal_stock", background="#E8F5E9", foreground="#155724")
    tree.tag_configure("low_stock", background="#FFEBEE", foreground="#C62828", font=("Segoe UI", 12, "bold"))

    v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=v_scrollbar.set)
    v_scrollbar.grid(row=0, column=0, sticky="ns", pady=10, padx=(10, 0))
    tree.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    actions = ctk.CTkFrame(tab, fg_color="transparent")
    actions.pack(fill="x", pady=(10, 5))
    
    ctk.CTkButton(actions, text="✏️ עדכון כמות מלאי בסניף", font=("Segoe UI", 12, "bold"), fg_color="#3B82F6", hover_color="#2563EB", height=35, corner_radius=10, command=lambda: edit_inventory(tree)).pack(side="right", padx=5)
    ctk.CTkButton(actions, text="🗑️ איפוס מלאי מוצר בסניף", font=("Segoe UI", 12, "bold"), fg_color="#EF4444", hover_color="#DC2626", height=35, corner_radius=10, command=lambda: delete_inventory(tree)).pack(side="right", padx=25)

    refresh_inventory_data(tree)


def refresh_inventory_data(tree, search_store="", search_prod=""):
    for item in tree.get_children(): tree.delete(item)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
            SELECT i.StoreID, s.StoreName, i.ProductID, p.ProductName, i.Quantity, i.MinimumStock
            FROM INVENTORY i
            JOIN STORE s ON i.StoreID = s.StoreID
            JOIN PRODUCT p ON i.ProductID = p.ProductID
            WHERE 1=1
        """
        params = []
        if search_store and search_store.isdigit():
            query += " AND i.StoreID = %s"
            params.append(int(search_store))
        if search_prod and search_prod.isdigit():
            query += " AND i.ProductID = %s"
            params.append(int(search_prod))
            
        query += " ORDER BY i.StoreID ASC, i.ProductID ASC;"
        cursor.execute(query, tuple(params))
        for row in cursor.fetchall():
            qty = row[4]
            min_stk = row[5]
            
            if qty < min_stk:
                row_tag = "low_stock"
            else:
                row_tag = "normal_stock"
                
            tree.insert("", "end", values=(min_stk, qty, row[3], row[2], row[1], row[0]), tags=(row_tag,))
        cursor.close()
        conn.close()


def open_inventory_modal(tree, edit_data=None):
    is_edit = edit_data is not None
    modal = ctk.CTkToplevel()
    modal.title("עדכון מלאי סניף" if is_edit else "קליטת מלאי חדש")
    modal.geometry("420x440")
    try: modal.transient(tree.winfo_toplevel())
    except: pass
    modal.lift()
    modal.focus_force()
    modal.grab_set()

    ctk.CTkLabel(modal, text="📊 רמות מלאי בסניפי הרשת", font=("Segoe UI", 16, "bold")).pack(pady=15)

    stores_list = []
    products_list = []
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT StoreID, StoreName FROM STORE ORDER BY StoreID ASC;")
        for r in cursor.fetchall(): stores_list.append(f"{r[0]} - {r[1]}")
        cursor.execute("SELECT ProductID, ProductName FROM PRODUCT ORDER BY ProductID ASC;")
        for r in cursor.fetchall(): products_list.append(f"{r[0]} - {r[1]}")
        cursor.close()
        conn.close()

    ctk.CTkLabel(modal, text="בחר סניף יעד", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    s_option = ctk.CTkOptionMenu(modal, values=stores_list if stores_list else ["אין סניפים"])
    s_option.pack(fill="x", padx=40, pady=2)

    ctk.CTkLabel(modal, text="בחר מוצר מהקטלוג", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    p_option = ctk.CTkOptionMenu(modal, values=products_list if products_list else ["אין מוצרים"])
    p_option.pack(fill="x", padx=40, pady=2)

    if is_edit:
        for s_str in stores_list:
            if s_str.startswith(str(edit_data[5]) + " -"): s_option.set(s_str)
        s_option.configure(state="disabled")
        for p_str in products_list:
            if p_str.startswith(str(edit_data[3]) + " -"): p_option.set(p_str)
        p_option.configure(state="disabled")

    ctk.CTkLabel(modal, text="כמות קיימת במדף/מלאי", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    qty_entry = ctk.CTkEntry(modal, justify="right")
    qty_entry.pack(fill="x", padx=40, pady=2)
    if is_edit: qty_entry.insert(0, edit_data[1])

    ctk.CTkLabel(modal, text="רף מלאי מינימום מבוקש", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    min_entry = ctk.CTkEntry(modal, justify="right")
    min_entry.pack(fill="x", padx=40, pady=2)
    if is_edit: min_entry.insert(0, edit_data[0])

    def save():
        try:
            s_id = int(s_option.get().split(" - ")[0])
            p_id = int(p_option.get().split(" - ")[0])
            qty = int(qty_entry.get().strip())
            min_stk = int(min_entry.get().strip())
        except:
            messagebox.showwarning("קלט שגוי", "אנא ודאי שהזנת מספרים שלמים תקינים.")
            return

        if qty < 0 or min_stk < 0:
            messagebox.showwarning("ערך שלילי", "הכמויות אינן יכולות להיות קטנות מ-0!")
            return

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                if is_edit:
                    cursor.execute("UPDATE INVENTORY SET Quantity=%s, MinimumStock=%s WHERE StoreID=%s AND ProductID=%s;", (qty, min_stk, s_id, p_id))
                else:
                    cursor.execute("INSERT INTO INVENTORY (StoreID, ProductID, Quantity, MinimumStock) VALUES (%s, %s, %s, %s);", (s_id, p_id, qty, min_stk))
                conn.commit()
                modal.destroy()
                refresh_inventory_data(tree)
            except Exception as e:
                error_msg = str(e)
                if "duplicate key" in error_msg or "already exists" in error_msg:
                    messagebox.showerror("מלאי קיים", f"לא ניתן לקלוט רשומה כפולה.\nמלאי עבור מוצר זה כבר קיים בסניף הנבחר!\nאנא השתמשי באפשרות 'עדכון כמות מלאי' לצורך שינוי.")
                else:
                    messagebox.showerror("שגיאה", f"רישום המלאי נכשל:\n{error_msg}")
            finally:
                cursor.close()
                conn.close()

    ctk.CTkButton(modal, text="שמור", fg_color="#10B981", hover_color="#059669", height=38, corner_radius=8, command=save).pack(pady=15)

def edit_inventory(tree):
    sel = tree.selection()
    if not sel: return messagebox.showwarning("בחירה חובה", "אנא בחר שורת מלאי מהטבלה לעדכון.")
    open_inventory_modal(tree, tree.item(sel[0], 'values'))

def delete_inventory(tree):
    sel = tree.selection()
    if not sel: return messagebox.showwarning("בחירה חובה", "אנא בחר שורת מלאי לאיפוס.")
    vals = tree.item(sel[0], 'values')
    s_id = vals[5]
    p_id = vals[3]

    if messagebox.askyesno("אישור איפור מלאי", f"האם את בטוחה שברצונך למחוק ולאפס את רשומת המלאי של מוצר מספר {p_id} בסניף מספר {s_id}?"):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM INVENTORY WHERE StoreID=%s AND ProductID=%s;", (int(s_id), int(p_id)))
                conn.commit()
                refresh_inventory_data(tree)
            except Exception as e:
                messagebox.showerror(
                    "חסימת הסרת מלאי", 
                    f"לא ניתן לבצע את מחיקת הרשומה.\n\n"
                    f"הסיבה: קיימות תלויות של הזמנות הפצה רשתיות פעילות המסתמכות על המלאי הנוכחי של סניף זה.\n"
                    f"אנא ודאי שאין תלויות פעילות בדף ההפצות לפני הסרת הרשומה."
                )
            finally:
                cursor.close()
                conn.close()