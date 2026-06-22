import customtkinter as ctk
from tkinter import ttk, messagebox
import tkinter as tk
from db_connection import get_db_connection

def show_warehouses_view(main_frame):
    # ניקוי המסך למניעת כפילויות תצוגה
    for widget in main_frame.winfo_children():
        widget.destroy()

    # --- כותרת עליונה מנופחת ומודגשת ---
    header_label = ctk.CTkLabel(main_frame, text="מערך לוגיסטיקה ומחסני הרשת", font=("Segoe UI", 32, "bold"), text_color="#111827", anchor="e")
    header_label.pack(pady=(35, 4), padx=35, fill="x")
    
    sub_header = ctk.CTkLabel(main_frame, text="ניהול מרכזי של מחסני הפצה, צוותי ניהול, ואיתור מיקומי מוצרים על גבי המדפים שמהם ניתן לקחת הזמנות לסניפים", font=("Segoe UI", 14, "bold"), text_color="#4B5563", anchor="e")
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

    # הגדרת הטאבים
    tab_warehouses = tabview.add("🏢  ניהול מחסנים וצוות מנהלים")
    tab_located = tabview.add("📦  איתור ומיקומי מוצרים במחסנים")

    setup_combined_warehouses_tab(tab_warehouses)
    setup_located_products_tab(tab_located)


# =========================================================================
# 📑 טאב 1: מחסנים וצוות ניהול
# =========================================================================
def setup_combined_warehouses_tab(tab):
    search_frame = ctk.CTkFrame(tab, fg_color="transparent")
    search_frame.pack(fill="x", pady=(5, 10))
    
    search_lbl = ctk.CTkLabel(search_frame, text="🔍  מסנני חיפוש", font=("Segoe UI", 13, "bold"), text_color="#374151")
    search_lbl.pack(side="right", padx=(10, 15))
    
    search_id_entry = ctk.CTkEntry(search_frame, placeholder_text="חפש לפי קוד מחסן מדויק", font=("Segoe UI", 12), width=180, height=35, corner_radius=8, justify="right")
    search_id_entry.pack(side="right", padx=(0, 15))
    
    search_addr_entry = ctk.CTkEntry(search_frame, placeholder_text="חפש לפי כתובת מחסן", font=("Segoe UI", 12), width=180, height=35, corner_radius=8, justify="right")
    search_addr_entry.pack(side="right")
    
    search_id_entry.bind("<KeyRelease>", lambda event: refresh_combined_warehouses_data(tree, search_id_entry.get().strip(), search_addr_entry.get().strip()))
    search_addr_entry.bind("<KeyRelease>", lambda event: refresh_combined_warehouses_data(tree, search_id_entry.get().strip(), search_addr_entry.get().strip()))

    btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
    btn_frame.pack(fill="x", pady=(0, 10))
    
    add_w_btn = ctk.CTkButton(btn_frame, text="🏢 הקמת מחסן חדש ברשת", font=("Segoe UI", 12, "bold"), fg_color="#10B981", hover_color="#059669", height=35, corner_radius=10, command=lambda: open_warehouse_modal(tree))
    add_w_btn.pack(side="right", padx=5)

    table_container = ctk.CTkFrame(tab, fg_color="#FFFFFF", corner_radius=12, border_color="#E5E7EB", border_width=1)
    table_container.pack(fill="both", expand=True, pady=5)
    table_container.grid_rowconfigure(0, weight=1)
    table_container.grid_columnconfigure(0, weight=0) 
    table_container.grid_columnconfigure(1, weight=1) 

    style = ttk.Style()
    style.theme_use("clam")
    
    # ✨ בידוד סטייל: שינוי שם הסטייל ל-Wh.Treeview למניעת התנגשויות ודריסת צבעים
    style.configure("Wh.Treeview",
                    background="#FFFFFF",
                    foreground="#1E3A8A",
                    rowheight=40,
                    fieldbackground="#FFFFFF",
                    font=("Segoe UI", 12, "bold"),
                    borderwidth=0,
                    relief="flat")
    
    style.configure("Wh.Treeview.Heading",
                    background="#F9FAFB",
                    foreground="#4B5563",
                    font=("Segoe UI", 13, "bold"),
                    relief="flat",
                    borderwidth=0)
    
    style.map("Wh.Treeview", background=[('selected', '#E0F2FE')], foreground=[('selected', '#0369A1')])

    columns = ("address", "region", "warehouse_id")
    tree = ttk.Treeview(table_container, columns=columns, show="headings", style="Wh.Treeview")
    
    tree.heading("warehouse_id", text="קוד מחסן", anchor="center")
    tree.heading("region", text="אזור גיאוגרפי", anchor="center")
    tree.heading("address", text="כתובת המחסן", anchor="center")

    tree.column("warehouse_id", width=200, anchor="center", stretch=tk.NO)
    tree.column("region", width=350, anchor="center", stretch=tk.NO)
    tree.column("address", width=350, anchor="e", stretch=tk.YES)

    v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=v_scrollbar.set)
    
    v_scrollbar.grid(row=0, column=0, sticky="ns", pady=10, padx=(10, 0))
    tree.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    actions = ctk.CTkFrame(tab, fg_color="transparent")
    actions.pack(fill="x", pady=(10, 5))
    
    ctk.CTkButton(actions, text="✏️ עריכת מיקום מחסן", font=("Segoe UI", 12, "bold"), fg_color="#3B82F6", hover_color="#2563EB", height=35, corner_radius=10, command=lambda: edit_warehouse(tree)).pack(side="right", padx=5)
    ctk.CTkButton(actions, text="🗑️ סגירת מחסן מהרשת", font=("Segoe UI", 12, "bold"), fg_color="#EF4444", hover_color="#DC2626", height=35, corner_radius=10, command=lambda: delete_warehouse(tree)).pack(side="right", padx=25)
    
    ctk.CTkButton(actions, text="📜 צפייה במנהלים", font=("Segoe UI", 12, "bold"), fg_color="#8B5CF6", hover_color="#7C3AED", height=35, corner_radius=10, command=lambda: open_managers_manager_modal(tree)).pack(side="left", padx=5)

    refresh_combined_warehouses_data(tree)


def refresh_combined_warehouses_data(tree, search_id="", search_addr=""):
    for item in tree.get_children(): tree.delete(item)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        
        query = """
            SELECT w.WarehouseID, w.Region, w.Address
            FROM WAREHOUSE w
            WHERE 1=1
        """
        params = []
        if search_id and search_id.isdigit():
            query += " AND w.WarehouseID = %s"
            params.append(int(search_id))
        if search_addr:
            query += " AND w.Address ILIKE %s"
            params.append(f"%{search_addr}%")
            
        query += " ORDER BY w.WarehouseID ASC;"
        cursor.execute(query, tuple(params))
            
        for row in cursor.fetchall():
            tree.insert("", "end", values=(row[2], row[1], row[0]))
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
        id_entry.insert(0, edit_data[2]) 
        id_entry.configure(state="disabled", fg_color="#E5E7EB")

    ctk.CTkLabel(modal, text="אזור גיאוגרפי בארץ", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    region_entry = ctk.CTkEntry(modal, justify="right")
    region_entry.pack(fill="x", padx=40, pady=2)
    if is_edit: region_entry.insert(0, edit_data[1]) 

    ctk.CTkLabel(modal, text="כתובת פיזית מלאה", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    addr_entry = ctk.CTkEntry(modal, justify="right")
    addr_entry.pack(fill="x", padx=40, pady=2)
    if is_edit: addr_entry.insert(0, edit_data[0]) 

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
                    conn.commit()
                    messagebox.showinfo("הצלחה", "פרטי המחסן עודכנו בהצלחה!")
                    modal.destroy()
                    refresh_combined_warehouses_data(tree)
                else:
                    cursor.execute("INSERT INTO WAREHOUSE (WarehouseID, Region, Address) VALUES (%s, %s, %s);", (int(w_id), reg, addr))
                    conn.commit()
                    messagebox.showinfo("הצלחה", "המחסן הלוגיסטי החדש הוקם בהצלחה!")
                    modal.destroy()
                    refresh_combined_warehouses_data(tree)
            except Exception as e:
                error_msg = str(e)
                if "duplicate key" in error_msg or "already exists" in error_msg:
                    messagebox.showerror("קוד מחסן תפוס", f"לא ניתן להקים את המחסן החדש.\n\nקוד מחסן מספר {w_id} כבר תפוס ורשום במערכת הרשת!\nאנא בחר מספר מזהה ייחודי אחר.")
                else:
                    messagebox.showerror("שגיאה", f"הפעולה נכשלה:\n{error_msg}")
            finally:
                cursor.close()
                conn.close()

    ctk.CTkButton(modal, text="שמור", fg_color="#10B981", hover_color="#059669", height=38, corner_radius=8, command=save).pack(pady=20)


def edit_warehouse(tree):
    sel = tree.selection()
    if not sel: return messagebox.showwarning("בחירה חובה", "אנא בחר שורה מהטבלה לצורך עריכה.")
    open_warehouse_modal(tree, tree.item(sel[0], 'values'))


def delete_warehouse(tree):
    sel = tree.selection()
    if not sel: return messagebox.showwarning("בחירה חובה", "אנא בחר מחסן למחיקה.")
    vals = tree.item(sel[0], 'values')
    w_id = vals[2] 
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
                if "foreign key constraint" in error_msg or "is still referenced" in error_msg:
                    messagebox.showerror(
                        "לא ניתן למחוק - מחסן פעיל ברשת", 
                        f"פעולת המחיקה עבור מחסן מספר {w_id} נחסמה באופן מאובטח בדאטהבייס.\n\n"
                        f"💡 הסיבה:\n"
                        f"קיימים כרגע במערכת נתונים התלויים ישירות במחסן זה (מוצרים שממוקמים במעברים שלו, או מנהל הרשום בו).\n\n"
                        f"🛠️ מה צריך לעשות עכשיו?\n"
                        f"יש לפנות תחילה את כל המוצרים מהמלאי המשויכים למחסן זה (בלשונית איתור מוצרים) ולבטל את מינוי המנהל, ורק אז ניתן יהיה למחוק את המחסן מהמערכת."
                    )
                else:
                    messagebox.showerror("שגיאה במחיקה", f"פעולת המחיקה נכשלה:\n{error_msg}")
            finally:
                cursor.close()
                conn.close()


# =========================================================================
# 📜 חלון ניהול המנהלים (כולל גלילה מלאה לכל החלון ו-CRUD מובנה)
# =========================================================================
def open_managers_manager_modal(main_tree):
    sel = main_tree.selection()
    if not sel: return messagebox.showwarning("בחירה חובה", "אנא בחר מחסן מהטבלה לצורך ניהול המנהלים שלו.")
    
    vals = main_tree.item(sel[0], 'values')
    w_id = int(vals[2]) 
    w_addr = vals[0]

    modal = ctk.CTkToplevel()
    modal.title(f"ניהול מנהלי מחסן - קוד {w_id}")
    modal.geometry("540x500")
    modal.grab_set()

    canvas = tk.Canvas(modal, bg="#F3F4F6", highlightthickness=0)
    scrollbar = ctk.CTkScrollbar(modal, orientation="vertical", command=canvas.yview)
    scrollable_frame = ctk.CTkFrame(canvas, fg_color="#F3F4F6", corner_radius=0)

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=515)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="left", fill="y")
    canvas.pack(side="right", fill="both", expand=True)

    ctk.CTkLabel(scrollable_frame, text=f"👤 צוות ניהול מחסן: {w_addr}", font=("Segoe UI", 15, "bold"), text_color="#111827").pack(pady=10)

    add_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
    add_frame.pack(fill="x", padx=25, pady=5)
    
    mgr_entry = ctk.CTkEntry(add_frame, placeholder_text="חדש מנהל שם הקלד ", justify="right", width=260, height=35)
    mgr_entry.pack(side="right", padx=5)

    def add_manager_action():
        mgr_name = mgr_entry.get().strip()
        if not mgr_name: return messagebox.showwarning("קלט חסר", "אנא הקלד את שם המנהל.")
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO WAREHOUSEMANAGER (WarehouseID, WarehouseManager) VALUES (%s, %s);", (w_id, mgr_name))
                conn.commit()
                mgr_entry.delete(0, tk.END)
                refresh_managers_sub_table(sub_tree, w_id)
            except Exception as e:
                messagebox.showerror("שגיאה", "לא ניתן להוסיף מנהל זה (ייתכן והשם כבר קיים עבור מחסן זה).")
            finally:
                cursor.close()
                conn.close()

    ctk.CTkButton(add_frame, text="➕  הוספה", fg_color="#10B981", hover_color="#059669", height=35, font=("Segoe UI", 12, "bold"), command=add_manager_action).pack(side="left", padx=5)

    table_container = ctk.CTkFrame(scrollable_frame, fg_color="#FFFFFF", corner_radius=8, border_color="#E5E7EB", border_width=1)
    table_container.pack(fill="both", expand=True, padx=25, pady=10)
    table_container.grid_rowconfigure(0, weight=1)
    table_container.grid_columnconfigure(0, weight=1)

    # ✨ תיקון: הצמדת סטייל ה-Wh.Treeview המבודד גם לתת-הטבלה הפנימית
    sub_tree = ttk.Treeview(table_container, columns=("manager_name"), show="headings", style="Wh.Treeview")
    sub_tree.heading("manager_name", text="שם מנהל מורשה", anchor="center")
    sub_tree.column("manager_name", width=440, anchor="center")
    sub_tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

    actions_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
    actions_frame.pack(fill="x", padx=25, pady=(5, 15))

    def edit_manager_action():
        sub_sel = sub_tree.selection()
        if not sub_sel: return messagebox.showwarning("בחירה חובה", "אנא בחר מנהל מהרשימה לצורך עריכה.")
        old_mgr = sub_tree.item(sub_sel[0], 'values')[0]

        edit_modal = ctk.CTkToplevel()
        edit_modal.title("עדכון שם מנהל")
        edit_modal.geometry("340x160")
        edit_modal.grab_set()

        ctk.CTkLabel(edit_modal, text="שם מנהל מעודכן:", font=("Segoe UI", 12, "bold")).pack(pady=10)
        edit_entry = ctk.CTkEntry(edit_modal, justify="right", width=220)
        edit_entry.pack(pady=5)
        edit_entry.insert(0, old_mgr)

        def save_edited_manager():
            new_mgr = edit_entry.get().strip()
            if not new_mgr: return messagebox.showwarning("שגיאה", "השם לא יכול להיות ריק.")
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("UPDATE WAREHOUSEMANAGER SET WarehouseManager=%s WHERE WarehouseID=%s AND WarehouseManager=%s;", (new_mgr, w_id, old_mgr))
                    conn.commit()
                    edit_modal.destroy()
                    refresh_managers_sub_table(sub_tree, w_id)
                except Exception as e:
                    messagebox.showerror("שגיאה", f"העדכון נכשל:\n{e}")
                finally:
                    cursor.close()
                    conn.close()

        ctk.CTkButton(edit_modal, text="שינוי שמור ", fg_color="#3B82F6", command=save_edited_manager).pack(pady=10)

    def delete_manager_action():
        sub_sel = sub_tree.selection()
        if not sub_sel: return messagebox.showwarning("בחירה חובה", "אנא בחר מנהל מהטבלה לצורך הסרת המינוי.")
        target_mgr = sub_tree.item(sub_sel[0], 'values')[0]

        if messagebox.askyesno("אישור הסרה", f"האם את בטוחה שברצונך לבטל את מינויו של '{target_mgr}' כמנהל המחסן?"):
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("DELETE FROM WAREHOUSEMANAGER WHERE WarehouseID=%s AND WarehouseManager=%s;", (w_id, target_mgr))
                    conn.commit()
                    refresh_managers_sub_table(sub_tree, w_id)
                except Exception as e:
                    messagebox.showerror("שגיאה", f"הפעולה נכשלה:\n{e}")
                finally:
                    cursor.close()
                    conn.close()

    ctk.CTkButton(actions_frame, text="✏️מנהל עריכת  ", fg_color="#3B82F6", hover_color="#2563EB", height=35, command=edit_manager_action).pack(side="right", padx=5, expand=True, fill="x")
    ctk.CTkButton(actions_frame, text="🗑️  מנהל מחיקת", fg_color="#EF4444", hover_color="#DC2626", height=35, command=delete_manager_action).pack(side="left", padx=5, expand=True, fill="x")

    refresh_managers_sub_table(sub_tree, w_id)


def refresh_managers_sub_table(tree, warehouse_id):
    for item in tree.get_children(): tree.delete(item)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT WarehouseManager FROM WAREHOUSEMANAGER WHERE WarehouseID = %s ORDER BY WarehouseManager ASC;", (warehouse_id,))
        for row in cursor.fetchall():
            tree.insert("", "end", values=(row[0],))
        cursor.close()
        conn.close()


# =========================================================================
# 📦 טאב 2: איתור ומיקומי מוצרים במלאי
# =========================================================================
def setup_located_products_tab(tab):
    search_frame = ctk.CTkFrame(tab, fg_color="transparent")
    search_frame.pack(fill="x", pady=(5, 10))
    
    search_lbl = ctk.CTkLabel(search_frame, text="🔍  מסנני חיפוש", font=("Segoe UI", 13, "bold"), text_color="#374151")
    search_lbl.pack(side="right", padx=(10, 15))
    
    search_wh_entry = ctk.CTkEntry(search_frame, placeholder_text="חפש לפי קוד מחסן מדויק", font=("Segoe UI", 12), width=180, height=35, corner_radius=8, justify="right")
    search_wh_entry.pack(side="right", padx=(0, 15))
    
    search_prod_entry = ctk.CTkEntry(search_frame, placeholder_text="חפש לפי קוד מוצר מדויק", font=("Segoe UI", 12), width=180, height=35, corner_radius=8, justify="right")
    search_prod_entry.pack(side="right")
    
    search_wh_entry.bind("<KeyRelease>", lambda event: refresh_located_data(tree, search_wh_entry.get().strip(), search_prod_entry.get().strip()))
    search_prod_entry.bind("<KeyRelease>", lambda event: refresh_located_data(tree, search_wh_entry.get().strip(), search_prod_entry.get().strip()))

    btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
    btn_frame.pack(fill="x", pady=(0, 10))
    
    add_btn = ctk.CTkButton(btn_frame, text="➕ הצבת מוצר חדש במחסן", font=("Segoe UI", 12, "bold"), fg_color="#10B981", hover_color="#059669", height=35, corner_radius=10, command=lambda: open_located_modal(tree))
    add_btn.pack(side="right", padx=5)

    table_container = ctk.CTkFrame(tab, fg_color="#FFFFFF", corner_radius=12, border_color="#E5E7EB", border_width=1)
    table_container.pack(fill="both", expand=True, pady=5)
    table_container.grid_rowconfigure(0, weight=1)
    table_container.grid_columnconfigure(0, weight=0)
    table_container.grid_columnconfigure(1, weight=1)

    columns = ("shelf_nb", "aisle_nb", "warehouse_addr", "warehouse_id", "product_name", "product_id")
    # ✨ תיקון: הצמדת סטייל ה-Wh.Treeview המבודד גם לטבלת המיקומים בטאב השני
    tree = ttk.Treeview(table_container, columns=columns, show="headings", style="Wh.Treeview")
    
    tree.heading("product_id", text="קוד מוצר", anchor="center")
    tree.heading("product_name", text="שם מוצר בקטלוג", anchor="center")
    tree.heading("warehouse_id", text="קוד מחסן", anchor="center")
    tree.heading("warehouse_addr", text="כתובת המחסן", anchor="center")
    tree.heading("aisle_nb", text="מספר מעבר", anchor="center")
    tree.heading("shelf_nb", text="מספר מדף", anchor="center")

    tree.column("product_id", width=100, anchor="center", stretch=tk.YES)
    tree.column("product_name", width=200, anchor="e", stretch=tk.YES)
    tree.column("warehouse_id", width=100, anchor="center", stretch=tk.YES) 
    tree.column("warehouse_addr", width=220, anchor="e", stretch=tk.YES) 
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


def refresh_located_data(tree, search_wh="", search_prod=""):
    for item in tree.get_children(): tree.delete(item)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        
        query = """
            SELECT l.ProductID, p.ProductName, l.WarehouseID, w.Address, l.AisleNb, l.ShelfNb
            FROM LOCATED l
            JOIN PRODUCT p ON l.ProductID = p.ProductID
            JOIN WAREHOUSE w ON l.WarehouseID = w.WarehouseID
            WHERE 1=1
        """
        params = []
        if search_wh and search_wh.isdigit():
            query += " AND l.WarehouseID = %s"
            params.append(int(search_wh))
        if search_prod and search_prod.isdigit():
            query += " AND l.ProductID = %s"
            params.append(int(search_prod))
            
        query += " ORDER BY l.WarehouseID ASC, l.AisleNb ASC;"
        cursor.execute(query, tuple(params))
            
        for row in cursor.fetchall():
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

    ctk.CTkLabel(modal, text="בחר מוצר מהקטלוג", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    p_option = ctk.CTkOptionMenu(modal, values=products_list if products_list else ["אין מוצרים"])
    p_option.pack(fill="x", padx=40, pady=2)

    ctk.CTkLabel(modal, text="בחר מחסן לוגיסטי לייעוד", font=("Segoe UI", 12), text_color="#4B5563").pack(anchor="e", padx=40)
    w_option = ctk.CTkOptionMenu(modal, values=warehouses_list if warehouses_list else ["אין מחסנים"])
    w_option.pack(fill="x", padx=40, pady=2)

    if is_edit:
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
                messagebox.showinfo("הצלחה", "מיקום המוצר במחסן נשמר בהצלחה!")
                modal.destroy()
                refresh_located_data(tree)
            except Exception as e:
                error_msg = str(e)
                if "duplicate key" in error_msg or "already exists" in error_msg:
                    messagebox.showerror("מוצר כבר מוצב במחסן", f"לא ניתן להוסיף את הרשומה.\n\nמוצר מספר {p_id} כבר משויך ומוצב בתוך מחסן מספר {w_id}!\nאנא השתמשי באפשרות עריכת מיקום למטה במידה וברצונך לשנות מעבר או מדף.")
                else:
                    messagebox.showerror("שגיאה", f"ההצבה נכשלה:\n{error_msg}")
            finally:
                cursor.close()
                conn.close()

    ctk.CTkButton(modal, text="שמור", fg_color="#10B981", hover_color="#059669", height=38, corner_radius=8, command=save).pack(pady=20)


def edit_located(tree):
    sel = tree.selection()
    if not sel: return messagebox.showwarning("בחירה חובה", "אנא בחר מוצר לצורך שינוי מיקומו.")
    open_located_modal(tree, tree.item(sel[0], 'values'))


def delete_located(tree):
    sel = tree.selection()
    if not sel: return messagebox.showwarning("בחירה חובה", "אנא בחר שורה לפינוי מהמלאי.")
    vals = tree.item(sel[0], 'values')
    p_id = vals[5] 
    w_id = vals[3] 
    
    if messagebox.askyesno("אישור פינוי", f"האם את בטוחה שברצונך לפנות את המוצר מספר '{p_id}' ממחסן מספר {w_id}?"):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM LOCATED WHERE ProductID=%s AND WarehouseID=%s;", (int(p_id), int(w_id)))
                conn.commit()
                refresh_located_data(tree)
            except Exception as e:
                error_msg = str(e)
                if "foreign key constraint" in error_msg or "is still referenced" in error_msg:
                    messagebox.showerror(
                        "חסימת פינוי מלאי - רשומה תלויה", 
                        f"לא ניתן לפנות את מוצר מספר {p_id} ממחסן {w_id}.\n\n"
                        f"💡 הסיבה:\n"
                        f"קיימות רשומות רשת פתוחות התלויות במיקום מוצר זה (כגון הזמנות הפצה רשתיות פתוחות או תלויות מלאי ספקים).\n\n"
                        f"🛠️ מה צריך לעשות?\n"
                        f"אנא ודאי שאין תלויות לוגיסטיות פעילות או הזמנות משויכות בטאב 'ניהול הזמנות והפצה' לפני ביצוע הפינוי."
                    )
                else:
                    messagebox.showerror("שגיאה", f"הביטול נכשל:\n{error_msg}")
            finally:
                cursor.close()
                conn.close()