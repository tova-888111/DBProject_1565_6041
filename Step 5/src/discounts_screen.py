import customtkinter as ctk
from tkinter import ttk, messagebox
import tkinter as tk
from db_connection import get_db_connection
from datetime import datetime

def show_discounts_view(main_frame):
    # ניקוי המסך למניעת כפילויות תצוגה
    for widget in main_frame.winfo_children():
        widget.destroy()

    # --- כותרת עליונה מנופחת ומודגשת ---
    header_label = ctk.CTkLabel(main_frame, text="ניהול מבצעים והנחות רשתיים", font=("Segoe UI", 32, "bold"), text_color="#111827", anchor="e")
    header_label.pack(pady=(35, 4), padx=35, fill="x")
    
    sub_header = ctk.CTkLabel(main_frame, text="הגדרה וניהול של אחוזי הנחה, תאריכי תוקף והחלת מבצעים על מוצרי הרשת", font=("Segoe UI", 14, "bold"), text_color="#4B5563", anchor="e")
    sub_header.pack(pady=(0, 20), padx=35, fill="x")

    # --- מערכת הטאבים המרכזית (Tabview) בעיצוב האחיד והזהה לשאר האתר ---
    tabview = ctk.CTkTabview(main_frame, corner_radius=12, fg_color="#F3F4F6", segmented_button_fg_color="#E5E7EB",
                             segmented_button_selected_color="#3B82F6", segmented_button_selected_hover_color="#2563EB",
                             segmented_button_unselected_color="#FFFFFF", segmented_button_unselected_hover_color="#F3F4F6",
                             text_color="#111827")
    tabview.pack(fill="both", expand=True, padx=35, pady=(0, 20))
    
    try:
        tabview._segmented_button.configure(font=("Segoe UI", 14, "bold"), height=45)
    except:
        pass
    
    tab_catalog = tabview.add("🏷️   ניהול מבצעים")
    tab_applies = tabview.add("🔗   החלת מבצעים על מוצרים")

    # שליפת רפרנסים לטבלאות לצורך סנכרון בזמן אמת במעבר בין הטאבים
    catalog_tree = setup_discount_catalog_tab(tab_catalog)
    applies_tree = setup_applies_to_tab(tab_applies)

    # ✨ תיקון: פונקציית האזנה המרעננת את הצבעים והנתונים בדיוק ברגע המעבר בין הלשוניות
    def on_tab_change():
        if tabview.get() == "🏷️   ניהול מבצעים":
            refresh_discounts_table(catalog_tree)
        elif tabview.get() == "🔗   החלת מבצעים על מוצרים":
            refresh_applies_table(applies_tree)
            
    tabview.configure(command=on_tab_change)


# =====================================================================
# 📑 כרטיסייה 1: קטלוג המבצעים (טבלת DISCOUNT)
# =====================================================================
def setup_discount_catalog_tab(tab):
    # שורת כותרת פנימית
    title_frame = ctk.CTkFrame(tab, fg_color="transparent")
    title_frame.pack(fill="x", pady=(5, 2))
    title_lbl = ctk.CTkLabel(title_frame, text="📋  רשימת מבצעי קטלוג מוגדרים", font=("Segoe UI", 13, "bold"), text_color="#374151", anchor="e")
    title_lbl.pack(fill="x", padx=5)

    # החזרת כפתור "מבצע חדש" מתחת למלל הכותרת בצד ימין
    action_frame = ctk.CTkFrame(tab, fg_color="transparent")
    action_frame.pack(fill="x", pady=(2, 10))
    add_btn = ctk.CTkButton(action_frame, text="➕   מבצע חדש", font=("Segoe UI", 13, "bold"), fg_color="#10B981", hover_color="#059669", width=140, height=38, corner_radius=10, command=lambda: open_discount_modal(tree))
    add_btn.pack(side="right", padx=5)

    table_container = ctk.CTkFrame(tab, fg_color="#FFFFFF", corner_radius=12, border_color="#E5E7EB", border_width=1)
    table_container.pack(fill="both", expand=True, pady=5)
    table_container.grid_rowconfigure(0, weight=1)
    table_container.grid_columnconfigure(0, weight=0) 
    table_container.grid_columnconfigure(1, weight=1)

    columns = ("status", "end_date", "start_date", "percentage", "name", "discount_id")
    tree = ttk.Treeview(table_container, columns=columns, show="headings", style="Custom.Treeview")

    tree.heading("discount_id", text="קוד מבצע", anchor="center")
    tree.heading("name", text="שם המבצע", anchor="center")
    tree.heading("percentage", text="אחוז הנחה", anchor="center")
    tree.heading("start_date", text="תאריך התחלה", anchor="center")
    tree.heading("end_date", text="תאריך סיום", anchor="center")
    tree.heading("status", text="סטטוס תוקף", anchor="center")

    tree.column("discount_id", width=90, anchor="center", stretch=tk.NO)
    tree.column("name", width=220, anchor="e", stretch=tk.YES)
    tree.column("percentage", width=110, anchor="center", stretch=tk.NO)
    tree.column("start_date", width=140, anchor="center", stretch=tk.NO)
    tree.column("end_date", width=140, anchor="center", stretch=tk.NO)
    tree.column("status", width=130, anchor="center", stretch=tk.NO)

    tree.tag_configure("active", background="#E8F5E9", foreground="#10B981", font=("Segoe UI", 12, "bold"))
    tree.tag_configure("upcoming", background="#FFFBEB", foreground="#F59E0B", font=("Segoe UI", 12, "bold"))
    tree.tag_configure("expired", background="#FEF2F2", foreground="#EF4444", font=("Segoe UI", 12, "bold"))

    v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=v_scrollbar.set)
    v_scrollbar.grid(row=0, column=0, sticky="ns", pady=15, padx=(15, 0))
    tree.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)

    bottom_actions = ctk.CTkFrame(tab, fg_color="transparent")
    bottom_actions.pack(fill="x", pady=(15, 10))

    edit_btn = ctk.CTkButton(bottom_actions, text="✏️   עריכת מבצע", font=("Segoe UI", 13, "bold"), fg_color="#3B82F6", hover_color="#2563EB", width=140, height=38, corner_radius=10, command=lambda: edit_selected_discount(tree))
    edit_btn.pack(side="right", padx=5)

    delete_btn = ctk.CTkButton(bottom_actions, text="🗑️   מחיקת מבצע", font=("Segoe UI", 13, "bold"), fg_color="#EF4444", hover_color="#DC2626", width=120, height=38, corner_radius=10, command=lambda: delete_selected_discount(tree))
    delete_btn.pack(side="right", padx=5)

    refresh_discounts_table(tree)
    return tree


def refresh_discounts_table(tree):
    for item in tree.get_children():
        tree.delete(item)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT DiscountID, DiscountName, DiscountPercentage, StartDate, EndDate FROM DISCOUNT ORDER BY DiscountID ASC;")
            today = datetime.now().date()
            for row in cursor.fetchall():
                s_date = row[3]
                e_date = row[4]
                
                if today > e_date:
                    status, tag = "🔴 פג תוקף", "expired"
                elif today < s_date:
                    status, tag = "🟡 עתידי", "upcoming"
                else:
                    status, tag = "🟢 פעיל רשת", "active"
                
                tree.insert("", "end", values=(status, e_date.strftime('%Y-%m-%d'), s_date.strftime('%Y-%m-%d'), f"{row[2]}%", row[1], row[0]), tags=(tag,))
        except Exception as e:
            print(f"Error refreshing discounts catalog: {e}")
        finally:
            cursor.close()
            conn.close()


def open_discount_modal(tree, data=None):
    is_edit = data is not None
    title_text = "✏️ עריכת פרטי מבצע" if is_edit else "➕ יצירת מבצע הנחה חדש"
    
    modal = ctk.CTkToplevel()
    modal.title(title_text)
    modal.geometry("480x550")
    modal.resizable(True, True)
    modal.lift()
    modal.focus_force()
    modal.grab_set()

    canvas = tk.Canvas(modal, bg="#F3F4F6", highlightthickness=0)
    scrollbar = ctk.CTkScrollbar(modal, orientation="vertical", command=canvas.yview)
    scrollable_frame = ctk.CTkFrame(canvas, fg_color="#F3F4F6")

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=460)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="left", fill="y")
    canvas.pack(side="right", fill="both", expand=True)

    ctk.CTkLabel(scrollable_frame, text=title_text, font=("Segoe UI", 20, "bold"), text_color="#111827").pack(pady=(25, 15))

    fields = [
        {"label": "קוד מבצע מספר", "key": "id", "type": "entry"},
        {"label": "שם המבצע או התיאור שלו", "key": "name", "type": "entry"},
        {"label": "אחוז הנחה מספר שלם", "key": "percentage", "type": "entry"},
        {"label": "תאריך תחילת המבצע במבנה YYYY-MM-DD", "key": "start", "type": "entry"},
        {"label": "תאריך סיום המבצע במבנה YYYY-MM-DD", "key": "end", "type": "entry"}
    ]
    widgets = {}
    for cfg in fields:
        frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        frame.pack(fill="x", padx=40, pady=5)
        ctk.CTkLabel(frame, text=cfg["label"], font=("Segoe UI", 13), text_color="#4B5563", anchor="e").pack(fill="x")
        
        widget = ctk.CTkEntry(frame, font=("Segoe UI", 13), height=35, corner_radius=8, justify="right")
        widget.pack(fill="x")
        
        if is_edit:
            if cfg["key"] == "id":
                widget.insert(0, data['id'])
                widget.configure(state="disabled", fg_color="#E5E7EB")
            else:
                widget.insert(0, data[cfg["key"]])
        widgets[cfg["key"]] = widget

    save_btn = ctk.CTkButton(scrollable_frame, text="💾   שמור מבצע", font=("Segoe UI", 14, "bold"), fg_color="#10B981", hover_color="#059669", height=42, corner_radius=10,
                             command=lambda: save_discount(modal, widgets, tree, is_edit))
    save_btn.pack(fill="x", padx=40, pady=(25, 30))


def save_discount(modal, widgets, tree, is_edit):
    d_id = widgets["id"].get().strip()
    name = widgets["name"].get().strip()
    pct = widgets["percentage"].get().strip()
    start = widgets["start"].get().strip()
    end = widgets["end"].get().strip()

    if not d_id or not name or not pct or not start or not end:
        messagebox.showwarning("שדות חסרים", "אנא מלאי את כל שדות המבצע.")
        return

    try:
        pct_val = int(pct)
        if pct_val < 1 or pct_val > 100: raise ValueError()
    except ValueError:
        messagebox.showwarning("שגיאה", "אחוז ההנחה חייב להיות מספר שלם בין 1 ל-100.")
        return

    try:
        start_dt = datetime.strptime(start, "%Y-%m-%d").date()
        end_dt = datetime.strptime(end, "%Y-%m-%d").date()
        if start_dt > end_dt:
            messagebox.showwarning("שגיאת תאריכים", "תאריך תחילת המבצע אינו יכול להיות מאוחר מתאריך הסיום!")
            return
    except ValueError:
        messagebox.showwarning("פורמט שגוי", "אחד התאריכים הוקלד בפורמט שגוי. אנא השתמשי במבנה: YYYY-MM-DD")
        return

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            if is_edit:
                cursor.execute("UPDATE DISCOUNT SET DiscountName=%s, DiscountPercentage=%s, StartDate=%s, EndDate=%s WHERE DiscountID=%s;", (name, pct_val, start_dt, end_dt, int(d_id)))
            else:
                cursor.execute("INSERT INTO DISCOUNT (DiscountID, DiscountName, DiscountPercentage, StartDate, EndDate) VALUES (%s, %s, %s, %s, %s);", (int(d_id), name, pct_val, start_dt, end_dt))
            conn.commit()
            messagebox.showinfo("הצלחה", "המבצע נשמר בהצלחה!")
            modal.destroy()
            refresh_discounts_table(tree)
        except Exception as e:
            if "duplicate key" in str(e):
                messagebox.showerror("קוד תפוס", f"קוד מבצע מספר {d_id} כבר תפוס וקיים במערכת.")
            else:
                messagebox.showerror("שגיאה", f"הפעולה נכשלה:\n{e}")
        finally:
            cursor.close()
            conn.close()


def edit_selected_discount(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("בחירה חובה", "אנא בחר מבצע מהטבלה לצורך עריכה.")
        return
    val = tree.item(selected[0], 'values')
    data = {'id': val[5], 'name': val[4], 'percentage': val[3].replace("%",""), 'start': val[2], 'end': val[1]}
    open_discount_modal(tree, data)


def delete_selected_discount(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("בחירה חובה", "אנא בחר מבצע למחיקה.")
        return
    val = tree.item(selected[0], 'values')
    d_id = val[5]
    d_name = val[4]
    
    confirm = messagebox.askyesno("אישור", f"האם את בטוחה שברצונך למחוק את מבצע מספר {d_id} ('{d_name}')?")
    if not confirm: return

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM DISCOUNT WHERE DiscountID = %s;", (int(d_id),))
            conn.commit()
            messagebox.showinfo("הצלחה", "המבצע נמחק לחלוטין מהמערכת.")
            refresh_discounts_table(tree)
        except Exception as e:
            error_msg = str(e)
            if "foreign key constraint" in error_msg or "is still referenced" in error_msg:
                messagebox.showerror(
                    "חסימת מחיקה - מבצע משויך למוצרים", 
                    f"לא ניתן למחוק את המבצע '{d_name}' מהמערכת.\n\n"
                    f"💡 הסיבה:\n"
                    f"מבצע זה מוחל כעת באופן פעיל על מוצרים שונים ברחבי הרשת (קיימות שורות משויכות בטבלת החלת מבצעים).\n\n"
                    f"🛠️ מה צריך לעשות?\n"
                    f"עברי ללשונית 'החלת מבצעים על מוצרים', בחר את המוצרים המקושרים למבצע זה, ולחצי על 'ביטול מבצע ממוצר'. "
                    f"רק לאחר שהמבצע יהיה חופשי לחלוטין ולא משויך לשום מוצר, תוכלי להסירו מהקטלוג."
                )
            else:
                messagebox.showerror("שגיאה", f"המחיקה נכשלה:\n{error_msg}")
        finally:
            cursor.close()
            conn.close()


# =====================================================================
# 📑 כרטיסייה 2: החלת מבצעים על מוצרים (טבלת APPLIES_TO)
# =====================================================================
def setup_applies_to_tab(tab):
    search_frame = ctk.CTkFrame(tab, fg_color="transparent")
    search_frame.pack(fill="x", pady=(5, 12))

    # === 🔍 שדות חיפוש סימטריים ומשולבים ===
    
    # 1. מסנן לפי קוד מבצע
    search_lbl = ctk.CTkLabel(search_frame, text="קוד מבצע", font=("Segoe UI", 13, "bold"), text_color="#374151")
    search_lbl.pack(side="right", padx=(15, 5))
    
    search_id_entry = ctk.CTkEntry(search_frame, placeholder_text="הקלידי קוד מבצע", font=("Segoe UI", 13), width=160, height=35, corner_radius=8, justify="right")
    search_id_entry.pack(side="right", padx=(0, 15))
    
    # 2. מסנן לפי קוד מוצר (מיושר ומרווח בצורה זהה לחלוטין)
    search_prod_lbl = ctk.CTkLabel(search_frame, text="קוד מוצר", font=("Segoe UI", 13, "bold"), text_color="#374151")
    search_prod_lbl.pack(side="right", padx=(15, 5))
    
    search_prod_entry = ctk.CTkEntry(search_frame, placeholder_text="הקלידי קוד מוצר", font=("Segoe UI", 13), width=160, height=35, corner_radius=8, justify="right")
    search_prod_entry.pack(side="right")

    # קישור שני השדות לעדכון דינמי משולב
    search_id_entry.bind("<KeyRelease>", lambda event: refresh_applies_table(tree, search_id_entry.get().strip(), search_prod_entry.get().strip()))
    search_prod_entry.bind("<KeyRelease>", lambda event: refresh_applies_table(tree, search_id_entry.get().strip(), search_prod_entry.get().strip()))

    # החזרת כפתור הפעולה העליון לשורת כפתורי הפעולה הבאה בצד ימין
    action_frame = ctk.CTkFrame(tab, fg_color="transparent")
    action_frame.pack(fill="x", pady=(0, 10))

    add_btn = ctk.CTkButton(action_frame, text="🔗   החלת מבצע על מוצר", font=("Segoe UI", 13, "bold"), fg_color="#10B981", hover_color="#059669", width=180, height=40, corner_radius=10, command=lambda: open_applies_modal(tree))
    add_btn.pack(side="right", padx=5)

    table_container = ctk.CTkFrame(tab, fg_color="#FFFFFF", corner_radius=12, border_color="#E5E7EB", border_width=1)
    table_container.pack(fill="both", expand=True, pady=5)
    table_container.grid_rowconfigure(0, weight=1)
    table_container.grid_columnconfigure(0, weight=0) 
    table_container.grid_columnconfigure(1, weight=1)

    columns = ("discount_pct", "discount_name", "product_brand", "product_name", "discount_id", "product_id")
    tree = ttk.Treeview(table_container, columns=columns, show="headings", style="Custom.Treeview")

    tree.heading("product_id", text="קוד מוצר", anchor="center")
    tree.heading("product_name", text="שם מוצר", anchor="center")
    tree.heading("product_brand", text="מותג מוצר", anchor="center")
    tree.heading("discount_id", text="קוד מבצע", anchor="center")
    tree.heading("discount_name", text="שם המבצע המוחל", anchor="center")
    tree.heading("discount_pct", text="אחוז הנחה", anchor="center")

    tree.column("product_id", width=90, anchor="center", stretch=tk.NO)
    tree.column("product_name", width=180, anchor="e", stretch=tk.YES)
    tree.column("product_brand", width=130, anchor="center", stretch=tk.NO)
    tree.column("discount_id", width=90, anchor="center", stretch=tk.NO)
    tree.column("discount_name", width=220, anchor="e", stretch=tk.YES)
    tree.column("discount_pct", width=110, anchor="center", stretch=tk.NO)

    # --- ✨ תיקון צבעים: ירוק לפעיל, כתום מודגש לעתידי, אדום בהיר לפג תוקף ---
    tree.tag_configure("active_link", background="#E8F5E9", foreground="#047857", font=("Segoe UI", 12, "bold"))
    tree.tag_configure("upcoming_link", background="#FFFBEB", foreground="#F59E0B", font=("Segoe UI", 12, "bold"))
    tree.tag_configure("inactive_link", background="#FEF2F2", foreground="#991B1B", font=("Segoe UI", 12))

    v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=v_scrollbar.set)
    v_scrollbar.grid(row=0, column=0, sticky="ns", pady=15, padx=(15, 0))
    tree.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)

    bottom_actions = ctk.CTkFrame(tab, fg_color="transparent")
    bottom_actions.pack(fill="x", pady=(15, 10))

    edit_btn = ctk.CTkButton(bottom_actions, text="✏️   עריכת שיוך מבצע", font=("Segoe UI", 13, "bold"), fg_color="#3B82F6", hover_color="#2563EB", width=150, height=38, corner_radius=10, command=lambda: edit_selected_applies(tree))
    edit_btn.pack(side="right", padx=5)

    delete_btn = ctk.CTkButton(bottom_actions, text="❌   ביטול מבצע ממוצר", font=("Segoe UI", 13, "bold"), fg_color="#EF4444", hover_color="#DC2626", width=160, height=38, corner_radius=10, command=lambda: delete_applies_link(tree))
    delete_btn.pack(side="right", padx=5)

    refresh_applies_table(tree)
    return tree


def refresh_applies_table(tree, filter_discount_id="", filter_product_id=""):
    for item in tree.get_children():
        tree.delete(item)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            query = """
                SELECT a.ProductID, p.ProductName, p.Brand, a.DiscountID, d.DiscountName, d.DiscountPercentage, d.StartDate, d.EndDate
                FROM APPLIES_TO a
                JOIN PRODUCT p ON a.ProductID = p.ProductID
                JOIN DISCOUNT d ON a.DiscountID = d.DiscountID
                WHERE 1=1
            """
            params = []
            
            if filter_discount_id and filter_discount_id.isdigit():
                query += " AND a.DiscountID = %s"
                params.append(int(filter_discount_id))

            # ✨ תיקון: הוספת סינון שאילתה דינמי לפי קוד מוצר
            if filter_product_id and filter_product_id.isdigit():
                query += " AND a.ProductID = %s"
                params.append(int(filter_product_id))
                
            query += " ORDER BY a.ProductID ASC, a.DiscountID ASC;"
            cursor.execute(query, tuple(params))
            
            today = datetime.now().date()
            for row in cursor.fetchall():
                start_date = row[6]
                end_date = row[7]
                
                # --- ✨ תיקון חלוקת תגיות וצבעים: פעיל (ירוק), עתידי (כתום), פג תוקף (אדום) ---
                if today > end_date:
                    row_tag = "inactive_link"
                elif today < start_date:
                    row_tag = "upcoming_link"
                else:
                    row_tag = "active_link"
                
                tree.insert("", "end", values=(f"{row[5]}%", row[4], row[2], row[1], row[3], row[0]), tags=(row_tag,))
        except Exception as e:
            print(f"Error refreshing applies_to view: {e}")
        finally:
            cursor.close()
            conn.close()


def get_available_ids_with_names(table_name, id_column, name_column):
    items = []
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(f"SELECT {id_column}, {name_column} FROM {table_name} ORDER BY {id_column} ASC;")
            for s_id, s_name in cursor.fetchall():
                items.append(f"{s_id} - {s_name}")
        except Exception as e:
            print(e)
        finally:
            cursor.close()
            conn.close()
    return items


def open_applies_modal(tree, edit_data=None):
    is_edit = edit_data is not None
    title_text = "✏️ עדכון שיוך מבצע למוצר" if is_edit else "🔗 החלת מבצע על מוצר קטלוג"
    
    modal = ctk.CTkToplevel()
    modal.title(title_text)
    modal.geometry("460x400")
    modal.resizable(False, False)
    modal.lift()
    modal.focus_force()
    modal.grab_set()

    ctk.CTkLabel(modal, text=title_text, font=("Segoe UI", 18, "bold"), text_color="#111827").pack(pady=(25, 20))

    products_list = get_available_ids_with_names("PRODUCT", "ProductID", "ProductName")
    discounts_list = get_available_ids_with_names("DISCOUNT", "DiscountID", "DiscountName")

    if not products_list: products_list = ["אין מוצרים בקטלוג"]
    if not discounts_list: discounts_list = ["אין מבצעים בקטלוג"]

    # בחירת מוצר
    frame_prod = ctk.CTkFrame(modal, fg_color="transparent")
    frame_prod.pack(fill="x", padx=45, pady=8)
    ctk.CTkLabel(frame_prod, text="מוצר נבחר מהרשת", font=("Segoe UI", 13), text_color="#4B5563", anchor="e").pack(fill="x")
    prod_opt = ctk.CTkOptionMenu(frame_prod, values=products_list, font=("Segoe UI", 13), height=35, corner_radius=8, fg_color="#FFFFFF", text_color="#111827", button_color="#E5E7EB")
    prod_opt.pack(fill="x")

    # בחירת מבצע
    frame_disc = ctk.CTkFrame(modal, fg_color="transparent")
    frame_disc.pack(fill="x", padx=45, pady=8)
    ctk.CTkLabel(frame_disc, text="מבצע הנחה להחלה", font=("Segoe UI", 13), text_color="#4B5563", anchor="e").pack(fill="x")
    disc_opt = ctk.CTkOptionMenu(frame_disc, values=discounts_list, font=("Segoe UI", 13), height=35, corner_radius=8, fg_color="#FFFFFF", text_color="#111827", button_color="#E5E7EB")
    disc_opt.pack(fill="x")

    if is_edit:
        for item in products_list:
            if item.startswith(str(edit_data['product_id']) + " -"):
                prod_opt.set(item)
                break
        prod_opt.configure(state="disabled")
        
        for item in discounts_list:
            if item.startswith(str(edit_data['discount_id']) + " -"):
                disc_opt.set(item)
                break
    else:
        prod_opt.set(products_list[0])
        disc_opt.set(discounts_list[0])

    save_btn = ctk.CTkButton(modal, text="💾   שמור שיוך מעודכן" if is_edit else "🔗   בצע שיוך מבצע", 
                             font=("Segoe UI", 14, "bold"), fg_color="#10B981", hover_color="#059669", height=42, corner_radius=10,
                             command=lambda: save_applies_link(modal, prod_opt.get().split(" - ")[0], disc_opt.get().split(" - ")[0], tree, is_edit, edit_data))
    save_btn.pack(fill="x", padx=45, pady=(30, 0))


def save_applies_link(modal, p_id, d_id, tree, is_edit, old_data=None):
    if p_id.startswith("אין") or d_id.startswith("אין"):
        messagebox.showwarning("שגיאה", "לא ניתן לבצע פעולה ללא נתונים תקינים.")
        return

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            if is_edit:
                cursor.execute("UPDATE APPLIES_TO SET DiscountID = %s WHERE ProductID = %s AND DiscountID = %s;", 
                               (int(d_id), int(p_id), int(old_data['discount_id'])))
            else:
                cursor.execute("INSERT INTO APPLIES_TO (ProductID, DiscountID) VALUES (%s, %s);", (int(p_id), int(d_id)))
            
            conn.commit()
            messagebox.showinfo("הצלחה", "החלת המבצע עודכנה ונשמרה בהצלחה!")
            modal.destroy()
            refresh_applies_table(tree)
        except Exception as e:
            if "duplicate key" in str(e):
                messagebox.showerror("שגיאה", "מבצע זה כבר מוחל על המוצר הנבחר!")
            else:
                messagebox.showerror("שגיאה", f"הפעולה נכשלה:\n{e}")
        finally:
            cursor.close()
            conn.close()


def edit_selected_applies(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("בחירה חובה", "אנא בחר שורת שיוך מהטבלה לצורך עריכה.")
        return
    val = tree.item(selected[0], 'values')
    
    edit_data = {
        'discount_id': val[4],
        'product_id': val[5]
    }
    open_applies_modal(tree, edit_data)


def delete_applies_link(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("בחירה חובה", "אנא בחר שורת שיוך מהטבלה לביטול המבצע.")
        return
    val = tree.item(selected[0], 'values')
    d_id = val[4] 
    p_id = val[5] 

    confirm = messagebox.askyesno("אישור ביטול", "האם את בטוחה שברצונך לבטל את החלת המבצע על מוצר זה?")
    if not confirm: return

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM APPLIES_TO WHERE ProductID = %s AND DiscountID = %s;", (int(p_id), int(d_id)))
            conn.commit()
            messagebox.showinfo("הצלחה", "המבצע בבוטל מהמוצר בהצלחה.")
            refresh_applies_table(tree)
        except Exception as e:
            messagebox.showerror("שגיאה", f"הביטול נכשל:\n{e}")
        finally:
            cursor.close()
            conn.close()