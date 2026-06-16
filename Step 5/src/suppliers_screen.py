import customtkinter as ctk
from tkinter import ttk, messagebox
import tkinter as tk
from db_connection import get_db_connection

def show_suppliers_view(main_frame):
    # ניקוי המסך למניעת כפילויות תצוגה
    for widget in main_frame.winfo_children():
        widget.destroy()

    # --- כותרת עליונה ראשית - מודגשת ובולטת ---
    header_label = ctk.CTkLabel(main_frame, text="ניהול ספקים ורכש רשתי", font=("Segoe UI", 30, "bold"), text_color="#111827", anchor="e")
    header_label.pack(pady=(35, 4), padx=35, fill="x")
    
    # --- כותרת משנה מתוקנת ללא סימנים הפוכים ובעיצוב בולט ויוקרתי ---
    sub_header = ctk.CTkLabel(
        main_frame, 
        text="מערכת רכש מרכזית. ספקי הרשת מספקים סחורה באופן ישיר אל המחסנים הלוגיסטיים בלבד ומשם מבוצעת הפצה מבוקרת לסניפים", 
        font=("Segoe UI", 14, "bold"), 
        text_color="#047857", # ירוק-ברקת עמוק ובולט יותר
        anchor="e"
    )
    sub_header.pack(pady=(0, 25), padx=35, fill="x") # הגדלנו את המרווח התחתון ל-25

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

    tab_suppliers = tabview.add("🚚  ניהול ספקי הרשת")
    tab_supplied_by = tabview.add("📦  קטלוג פריטים לפי ספקים")

    setup_suppliers_tab(tab_suppliers)
    setup_supplied_by_tab(tab_supplied_by)


# =========================================================================
# 📑 טאב 1: ניהול ספקי הרשת (SUPPLIER)
# =========================================================================
def setup_suppliers_tab(tab):
    # שורת מסנני חיפוש סימטרית ב-Grid
    search_frame = ctk.CTkFrame(tab, fg_color="transparent")
    search_frame.pack(fill="x", pady=(5, 12))
    search_frame.grid_columnconfigure(0, weight=1)
    
    search_lbl = ctk.CTkLabel(search_frame, text="🔍  מסנני חיפוש", font=("Segoe UI", 13, "bold"), text_color="#374151")
    search_lbl.grid(row=0, column=3, padx=(10, 15), sticky="e")
    
    search_id_entry = ctk.CTkEntry(search_frame, placeholder_text="לפי קוד ספק מדויק", font=("Segoe UI", 12), width=160, height=35, corner_radius=8, justify="right")
    search_id_entry.grid(row=0, column=2, padx=6, sticky="e")
    
    search_name_entry = ctk.CTkEntry(search_frame, placeholder_text="לפי שם ספק", font=("Segoe UI", 12), width=160, height=35, corner_radius=8, justify="right")
    search_name_entry.grid(row=0, column=1, padx=6, sticky="e")

    search_id_entry.bind("<KeyRelease>", lambda event: refresh_suppliers_data(tree, search_id_entry.get().strip(), search_name_entry.get().strip()))
    search_name_entry.bind("<KeyRelease>", lambda event: refresh_suppliers_data(tree, search_id_entry.get().strip(), search_name_entry.get().strip()))

    # שורת פעולות
    btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
    btn_frame.pack(fill="x", pady=(0, 10))
    ctk.CTkButton(btn_frame, text="➕ הוספת ספק חדש", font=("Segoe UI", 12, "bold"), fg_color="#10B981", hover_color="#059669", height=35, corner_radius=10, command=lambda: open_supplier_modal(tree)).pack(side="right", padx=5)

    # מיכל טבלה ב-Grid
    table_container = ctk.CTkFrame(tab, fg_color="#FFFFFF", corner_radius=12, border_color="#E5E7EB", border_width=1)
    table_container.pack(fill="both", expand=True, pady=5)
    table_container.grid_rowconfigure(0, weight=1)
    table_container.grid_columnconfigure(0, weight=0)
    table_container.grid_columnconfigure(1, weight=1)

    columns = ("address", "phone", "email", "supplier_name", "supplier_id")
    tree = ttk.Treeview(table_container, columns=columns, show="headings", style="Custom.Treeview")
    
    tree.heading("supplier_id", text="קוד ספק", anchor="center")
    tree.heading("supplier_name", text="שם חברת הספק", anchor="center")
    tree.heading("email", text="כתובת אימייל", anchor="center")
    tree.heading("phone", text="טלפון ליצירת קשר", anchor="center")
    tree.heading("address", text="כתובת משרד/מפעל", anchor="center")

    tree.column("supplier_id", width=100, anchor="center", stretch=tk.YES)
    tree.column("supplier_name", width=200, anchor="e", stretch=tk.YES)
    tree.column("email", width=180, anchor="center", stretch=tk.YES)
    tree.column("phone", width=140, anchor="center", stretch=tk.YES)
    tree.column("address", width=250, anchor="e", stretch=tk.YES)

    v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=v_scrollbar.set)
    v_scrollbar.grid(row=0, column=0, sticky="ns", pady=10, padx=(10, 0))
    tree.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    # --- שדרוג: הרחבה וייצוב של שורת כפתורי הפעולה התחתונה ---
    actions = ctk.CTkFrame(tab, fg_color="transparent")
    actions.pack(fill="x", pady=(15, 10)) # הוספת מרווח אנכי עשיר למניעת כיווץ

    # הרחבנו את ה-width של הכפתורים שיהיו בולטים ונוחים
    ctk.CTkButton(actions, text="✏️ עריכת פרטי ספק", font=("Segoe UI", 13, "bold"), fg_color="#3B82F6", hover_color="#2563EB", width=160, height=38, corner_radius=10, command=lambda: edit_supplier(tree)).pack(side="right", padx=5)
    ctk.CTkButton(actions, text="🗑️ מחיקת ספק מהמערכת", font=("Segoe UI", 13, "bold"), fg_color="#EF4444", hover_color="#DC2626", width=180, height=38, corner_radius=10, command=lambda: delete_supplier(tree)).pack(side="right", padx=25)

    refresh_suppliers_data(tree)


def refresh_suppliers_data(tree, search_id="", search_name=""):
    for item in tree.get_children(): tree.delete(item)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = "SELECT SupplierID, SupplierName, Email, ContactPhone, Address FROM SUPPLIER WHERE 1=1"
        params = []
        if search_id and search_id.isdigit():
            query += " AND SupplierID = %s"
            params.append(int(search_id))
        if search_name:
            query += " AND SupplierName ILIKE %s"
            params.append(f"%{search_name}%")
            
        query += " ORDER BY SupplierID ASC;"
        cursor.execute(query, tuple(params))
        for row in cursor.fetchall():
            tree.insert("", "end", values=(row[4], row[3], row[2], row[1], row[0]))
        cursor.close()
        conn.close()


def open_supplier_modal(tree, edit_data=None):
    is_edit = edit_data is not None
    modal = ctk.CTkToplevel()
    modal.title("עריכת ספק" if is_edit else "הוספת ספק")
    modal.geometry("400x440")
    try: modal.transient(tree.winfo_toplevel())
    except: pass
    modal.lift()
    modal.focus_force()
    modal.grab_set()

    ctk.CTkLabel(modal, text="🚚 פרטי חברת ספק רכש", font=("Segoe UI", 16, "bold")).pack(pady=15)

    ctk.CTkLabel(modal, text="קוד ספק מספר", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    id_entry = ctk.CTkEntry(modal, justify="right")
    id_entry.pack(fill="x", padx=40, pady=2)
    if is_edit:
        id_entry.insert(0, edit_data[4])
        id_entry.configure(state="disabled", fg_color="#E5E7EB")

    ctk.CTkLabel(modal, text="שם חברת הספק", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    name_entry = ctk.CTkEntry(modal, justify="right")
    name_entry.pack(fill="x", padx=40, pady=2)
    if is_edit: name_entry.insert(0, edit_data[3])

    ctk.CTkLabel(modal, text="אימייל להתקשרות", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    email_entry = ctk.CTkEntry(modal, justify="right")
    email_entry.pack(fill="x", padx=40, pady=2)
    if is_edit: email_entry.insert(0, edit_data[2])

    ctk.CTkLabel(modal, text="טלפון ליצירת קשר", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    phone_entry = ctk.CTkEntry(modal, justify="right")
    phone_entry.pack(fill="x", padx=40, pady=2)
    if is_edit: phone_entry.insert(0, edit_data[1])

    ctk.CTkLabel(modal, text="כתובת משרדים/מפעל", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    addr_entry = ctk.CTkEntry(modal, justify="right")
    addr_entry.pack(fill="x", padx=40, pady=2)
    if is_edit: addr_entry.insert(0, edit_data[0])

    def save():
        s_id = id_entry.get().strip()
        s_name = name_entry.get().strip()
        email = email_entry.get().strip()
        phone = phone_entry.get().strip()
        addr = addr_entry.get().strip()

        if not s_id or not s_name or not email or not phone or not addr:
            messagebox.showwarning("שדות חסרים", "אנא מלאי את כל השדות בצורה תקינה.")
            return

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                if is_edit:
                    cursor.execute("UPDATE SUPPLIER SET SupplierName=%s, Email=%s, ContactPhone=%s, Address=%s WHERE SupplierID=%s;",
                                   (s_name, email, phone, addr, int(s_id)))
                else:
                    cursor.execute("INSERT INTO SUPPLIER (SupplierID, SupplierName, Email, ContactPhone, Address) VALUES (%s, %s, %s, %s, %s);",
                                   (int(s_id), s_name, email, phone, addr))
                conn.commit()
                modal.destroy()
                refresh_suppliers_data(tree)
            except Exception as e:
                messagebox.showerror("שגיאה", f"הפעולה נכשלה, ודאי שקוד הספק אינו כפול:\n{e}")
            finally:
                cursor.close()
                conn.close()

    ctk.CTkButton(modal, text="שמור", fg_color="#10B981", hover_color="#059669", height=38, corner_radius=8, command=save).pack(pady=15)

def edit_supplier(tree):
    sel = tree.selection()
    if not sel: return messagebox.showwarning("בחירה חובה", "אנא בחרי ספק מהטבלה לעריכה.")
    open_supplier_modal(tree, tree.item(sel[0], 'values'))

def delete_supplier(tree):
    sel = tree.selection()
    if not sel: return messagebox.showwarning("בחירה חובה", "אנא בחרי ספק למחיקה.")
    s_id = tree.item(sel[0], 'values')[4]
    s_name = tree.item(sel[0], 'values')[3]
    
    if messagebox.askyesno("אישור מחיקה", f"האם את בטוחה שברצונך למחוק את ספק '{s_name}' מהמערכת?"):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM SUPPLIER WHERE SupplierID = %s;", (int(s_id),))
                conn.commit()
                refresh_suppliers_data(tree)
            except Exception as e:
                error_msg = str(e)
                if "foreign key constraint" in error_msg or "is still referenced" in error_msg:
                    messagebox.showerror(
                        "לא ניתן למחוק ספק", 
                        f"פעולת המחיקה עבור ספק '{s_name}' נחסמה באופן מאובטח.\n\n"
                        f"💡 מדוע זה קרה?\n"
                        f"ספק זה רשום כמי שמספק מוצרים פעילים לקטלוג הרשת (טבלת שיוך פריטים לספקים).\n\n"
                        f"🛠️ מה צריך לעשות עכשיו?\n"
                        f"יש להיכנס ללשונית השנייה ('קטלוג פריטים לפי ספקים') ולמחוק תחילה את כל שיוכי המוצרים השייכים לספק זה, ורק אז ניתן יהיה למחוק אותו מהמערכת."
                    )
                else:
                    messagebox.showerror("שגיאה במחיקה", f"פעולת המחיקה נכשלה:\n{error_msg}")
            finally:
                cursor.close()
                conn.close()


# =========================================================================
# 📑 טאב 2: קטלוג פריטים לפי ספקים (SUPPLIERED_BY CRUD מלא)
# =========================================================================
def setup_supplied_by_tab(tab):
    # שורת מסנני חיפוש סימטרית ב-Grid
    search_frame = ctk.CTkFrame(tab, fg_color="transparent")
    search_frame.pack(fill="x", pady=(5, 12))
    search_frame.grid_columnconfigure(0, weight=1)
    
    search_lbl = ctk.CTkLabel(search_frame, text="🔍  מסנני חיפוש", font=("Segoe UI", 13, "bold"), text_color="#374151")
    search_lbl.grid(row=0, column=3, padx=(10, 15), sticky="e")
    
    search_wh_entry = ctk.CTkEntry(search_frame, placeholder_text="לפי קוד ספק מדויק", font=("Segoe UI", 12), width=160, height=35, corner_radius=8, justify="right")
    search_wh_entry.grid(row=0, column=2, padx=6, sticky="e")
    
    search_prod_entry = ctk.CTkEntry(search_frame, placeholder_text="לפי קוד מוצר מדויק", font=("Segoe UI", 12), width=160, height=35, corner_radius=8, justify="right")
    search_prod_entry.grid(row=0, column=1, padx=6, sticky="e")

    search_wh_entry.bind("<KeyRelease>", lambda event: refresh_supplied_by_data(tree, search_wh_entry.get().strip(), search_prod_entry.get().strip()))
    search_prod_entry.bind("<KeyRelease>", lambda event: refresh_supplied_by_data(tree, search_wh_entry.get().strip(), search_prod_entry.get().strip()))

    # שורת פעולות
    btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
    btn_frame.pack(fill="x", pady=(0, 10))
    ctk.CTkButton(btn_frame, text="➕ שיוך מוצר חדש לספק", font=("Segoe UI", 12, "bold"), fg_color="#10B981", hover_color="#059669", height=35, corner_radius=10, command=lambda: open_supplied_by_modal(tree)).pack(side="right", padx=5)

    # מיכל טבלה ב-Grid
    table_container = ctk.CTkFrame(tab, fg_color="#FFFFFF", corner_radius=12, border_color="#E5E7EB", border_width=1)
    table_container.pack(fill="both", expand=True, pady=5)
    table_container.grid_rowconfigure(0, weight=1)
    table_container.grid_columnconfigure(0, weight=0)
    table_container.grid_columnconfigure(1, weight=1)

    columns = ("product_name", "product_id", "supplier_name", "supplier_id")
    tree = ttk.Treeview(table_container, columns=columns, show="headings", style="Custom.Treeview")
    
    tree.heading("supplier_id", text="קוד ספק", anchor="center")
    tree.heading("supplier_name", text="שם חברת הספק", anchor="center")
    tree.heading("product_id", text="קוד מוצר", anchor="center")
    tree.heading("product_name", text="שם מוצר מורשה לאספקה", anchor="center")

    tree.column("supplier_id", width=120, anchor="center", stretch=tk.YES)
    tree.column("supplier_name", width=250, anchor="e", stretch=tk.YES)
    tree.column("product_id", width=120, anchor="center", stretch=tk.YES)
    tree.column("product_name", width=300, anchor="e", stretch=tk.YES)

    v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=v_scrollbar.set)
    v_scrollbar.grid(row=0, column=0, sticky="ns", pady=10, padx=(10, 0))
    tree.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    # --- שדרוג: הרחבה וייצוב של שורת כפתורי הפעולה התחתונה של הקטלוג ---
    actions = ctk.CTkFrame(tab, fg_color="transparent")
    actions.pack(fill="x", pady=(15, 10)) # מניעת כיווץ אנכי

    # הגדלת מימדי הכפתורים לרוחב סימטרי אחיד ומקצועי
    ctk.CTkButton(actions, text="✏️ עדכון שיוך ספק-מוצר", font=("Segoe UI", 13, "bold"), fg_color="#3B82F6", hover_color="#2563EB", width=180, height=38, corner_radius=10, command=lambda: edit_supplied_by(tree)).pack(side="right", padx=5)
    ctk.CTkButton(actions, text="🗑️ ביטול הרשאת אספקה", font=("Segoe UI", 13, "bold"), fg_color="#EF4444", hover_color="#DC2626", width=180, height=38, corner_radius=10, command=lambda: delete_supplied_by(tree)).pack(side="right", padx=25)

    refresh_supplied_by_data(tree)


def refresh_supplied_by_data(tree, search_sup="", search_prod=""):
    for item in tree.get_children(): tree.delete(item)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        query = """
            SELECT sb.SupplierID, s.SupplierName, sb.ProductID, p.ProductName
            FROM SUPPLIERED_BY sb
            JOIN SUPPLIER s ON sb.SupplierID = s.SupplierID
            JOIN PRODUCT p ON sb.ProductID = p.ProductID
            WHERE 1=1
        """
        params = []
        if search_sup and search_sup.isdigit():
            query += " AND sb.SupplierID = %s"
            params.append(int(search_sup))
        if search_prod and search_prod.isdigit():
            query += " AND sb.ProductID = %s"
            params.append(int(search_prod))
            
        query += " ORDER BY sb.SupplierID ASC, sb.ProductID ASC;"
        cursor.execute(query, tuple(params))
        for row in cursor.fetchall():
            tree.insert("", "end", values=(row[3], row[2], row[1], row[0]))
        cursor.close()
        conn.close()


def get_suppliers_and_products_lists():
    suppliers = []
    products = []
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT SupplierID, SupplierName FROM SUPPLIER ORDER BY SupplierID ASC;")
        for r in cursor.fetchall(): suppliers.append(f"{r[0]} - {r[1]}")
        cursor.execute("SELECT ProductID, ProductName FROM PRODUCT ORDER BY ProductID ASC;")
        for r in cursor.fetchall(): products.append(f"{r[0]} - {r[1]}")
        cursor.close()
        conn.close()
    return suppliers, products


def open_supplied_by_modal(tree, edit_data=None):
    is_edit = edit_data is not None
    modal = ctk.CTkToplevel()
    modal.title("עדכון הרשאת אספקה" if is_edit else "שיוך מוצר לספק")
    modal.geometry("420x360")
    try: modal.transient(tree.winfo_toplevel())
    except: pass
    modal.lift()
    modal.focus_force()
    modal.grab_set()

    ctk.CTkLabel(modal, text="📦 שיוך פריט אספקה לחברה", font=("Segoe UI", 16, "bold")).pack(pady=15)

    suppliers_list, products_list = get_suppliers_and_products_lists()

    ctk.CTkLabel(modal, text="בחרי חברת ספק", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    s_option = ctk.CTkOptionMenu(modal, values=suppliers_list if suppliers_list else ["אין ספקים"])
    s_option.pack(fill="x", padx=40, pady=4)

    ctk.CTkLabel(modal, text="בחרי מוצר מורשה מהקטלוג", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    p_option = ctk.CTkOptionMenu(modal, values=products_list if products_list else ["אין מוצרים"])
    p_option.pack(fill="x", padx=40, pady=4)

    if is_edit:
        # במצב עריכה - נועלים את מפתחות הקשר הקבועים
        for s_str in suppliers_list:
            if s_str.startswith(str(edit_data[3]) + " -"): s_option.set(s_str)
        s_option.configure(state="disabled")
        
        for p_str in products_list:
            if p_str.startswith(str(edit_data[1]) + " -"): p_option.set(p_str)

    def save():
        s_sel = s_option.get()
        p_sel = p_option.get()

        if s_sel.startswith("אין") or p_sel.startswith("אין"):
            messagebox.showwarning("קלט חסר", "לא נבחרו נתונים תקינים.")
            return

        sup_id = int(s_sel.split(" - ")[0])
        prod_id = int(p_sel.split(" - ")[0])

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                if is_edit:
                    # עריכת טבלת קשר מורכבת משני מפתחות: מעדכנים את ה-ProductID עבור ה-SupplierID הקיים
                    cursor.execute("UPDATE SUPPLIERED_BY SET ProductID=%s WHERE SupplierID=%s AND ProductID=%s;", 
                                   (prod_id, sup_id, int(edit_data[1])))
                else:
                    cursor.execute("INSERT INTO SUPPLIERED_BY (SupplierID, ProductID) VALUES (%s, %s);", (sup_id, prod_id))
                conn.commit()
                modal.destroy()
                refresh_supplied_by_data(tree)
            except Exception as e:
                messagebox.showerror("שגיאה", f"הפעולה נכשלה, ייתכן והמוצר כבר משויך לספק זה:\n{e}")
            finally:
                cursor.close()
                conn.close()

    ctk.CTkButton(modal, text="בצע", fg_color="#10B981", hover_color="#059669", height=38, corner_radius=8, command=save).pack(pady=20)


def edit_supplied_by(tree):
    sel = tree.selection()
    if not sel: return messagebox.showwarning("בחירה חובה", "אנא בחרי שורת שיוך מהטבלה לצורך עריכה.")
    open_supplied_by_modal(tree, tree.item(sel[0], 'values'))


def delete_supplied_by(tree):
    sel = tree.selection()
    if not sel: return messagebox.showwarning("בחירה חובה", "אנא בחרי שורת שיוך לבטול המינוי.")
    vals = tree.item(sel[0], 'values')
    prod_id = vals[1]
    sup_id = vals[3]
    prod_name = vals[0]
    
    if messagebox.askyesno("אישור ביטול הרשאה", f"האם לבטל את הרשאת האספקה של מוצר '{prod_name}' מספק זה?"):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM SUPPLIERED_BY WHERE SupplierID=%s AND ProductID=%s;", (int(sup_id), int(prod_id)))
                conn.commit()
                refresh_supplied_by_data(tree)
            except Exception as e:
                messagebox.showerror(
                    "חסימת ביטול הרשאה",
                    f"לא ניתן לבטל הרשאת אספקה זו כרגע.\n\n"
                    f"הסיבה: קיימות הזמנות פתוחות או תלויות רכש במחסנים הממתינות לאספקה מול פריט זה.\n"
                    f"אנא ודאי שאין תלויות פעילות בדף ההזמנות."
                )
            finally:
                cursor.close()
                conn.close()