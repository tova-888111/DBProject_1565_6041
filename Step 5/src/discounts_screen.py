import customtkinter as ctk
from tkinter import ttk, messagebox
import tkinter as tk
from db_connection import get_db_connection
from datetime import datetime

def show_discounts_view(main_frame):
    # ניקוי המסך למניעת כפילויות תצוגה
    for widget in main_frame.winfo_children():
        widget.destroy()

    # --- כותרת עליונה ---
    header_label = ctk.CTkLabel(main_frame, text="ניהול מבצעים והנחות רשתיים", font=("Segoe UI", 28, "bold"), text_color="#111827", anchor="e")
    header_label.pack(pady=(30, 2), padx=35, fill="x")
    
    sub_header = ctk.CTkLabel(main_frame, text="הגדרה וניהול של אחוזי הנחה, תאריכי תוקף והחלת מבצעים על מוצרי הרשת", font=("Segoe UI", 14), text_color="#6B7280", anchor="e")
    sub_header.pack(pady=(0, 20), padx=35, fill="x")

    # --- שימוש ב-Tabview לחלוקה פנימית ---
    tabview = ctk.CTkTabview(main_frame, fg_color="transparent", segmented_button_selected_color="#059669", segmented_button_selected_hover_color="#047857")
    tabview.pack(fill="both", expand=True, padx=35, pady=(0, 20))
    
    tab_catalog = tabview.add("🏷️  ניהול מבצעים")
    tab_applies = tabview.add("🔗  החלת מבצעים על מוצרים")

    setup_discount_catalog_tab(tab_catalog)
    setup_applies_to_tab(tab_applies)


# =====================================================================
# 📑 כרטיסייה 1: קטלוג המבצעים (טבלת DISCOUNT)
# =====================================================================
def setup_discount_catalog_tab(tab):
    action_frame = ctk.CTkFrame(tab, fg_color="transparent")
    action_frame.pack(fill="x", pady=(10, 15))

    refresh_btn = ctk.CTkButton(action_frame, text="🔄  רענן", font=("Segoe UI", 13, "bold"), fg_color="#4B5563", hover_color="#374151", width=100, height=38, corner_radius=10, command=lambda: refresh_discounts_table(tree))
    refresh_btn.pack(side="left", padx=5)

    add_btn = ctk.CTkButton(action_frame, text="➕  מבצע חדש", font=("Segoe UI", 13, "bold"), fg_color="#10B981", hover_color="#059669", width=140, height=38, corner_radius=10, command=lambda: open_discount_modal(tree))
    add_btn.pack(side="right", padx=5)

    table_container = ctk.CTkFrame(tab, fg_color="#FFFFFF", corner_radius=18, border_color="#E5E7EB", border_width=1)
    table_container.pack(fill="both", expand=True, pady=(0, 15))

    # ה-ID מוסתר בעמודה האחרונה index 5
    columns = ("status", "end_date", "start_date", "percentage", "name", "hidden_id")
    tree = ttk.Treeview(table_container, columns=columns, show="headings", style="Custom.Treeview")

    tree.heading("name", text="שם המבצע", anchor="center")
    tree.heading("percentage", text="אחוז הנחה", anchor="center")
    tree.heading("start_date", text="תאריך התחלה", anchor="center")
    tree.heading("end_date", text="תאריך סיום", anchor="center")
    tree.heading("status", text="סטטוס תוקף", anchor="center")

    tree.column("name", width=160, anchor="center")
    tree.column("percentage", width=100, anchor="center")
    tree.column("start_date", width=130, anchor="center")
    tree.column("end_date", width=130, anchor="center")
    tree.column("status", width=120, anchor="center")
    
    # הסתרת עמודת ה-ID מהתצוגה הכללית כפי שנדרש
    tree.column("hidden_id", width=0, stretch=tk.NO)

    tree.add_tag = tree.tag_configure
    tree.tag_configure("active", foreground="#10B981", font=("Segoe UI", 12, "bold"))
    tree.tag_configure("upcoming", foreground="#F59E0B", font=("Segoe UI", 12, "bold"))
    tree.tag_configure("expired", foreground="#EF4444", font=("Segoe UI", 12, "bold"))

    scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="left", fill="y", padx=(10, 0), pady=15)
    tree.pack(fill="both", expand=True, padx=15, pady=15)

    bottom_actions = ctk.CTkFrame(tab, fg_color="transparent")
    bottom_actions.pack(fill="x", pady=(0, 10))

    edit_btn = ctk.CTkButton(bottom_actions, text="✏️  עריכת מבצע", font=("Segoe UI", 13, "bold"), fg_color="#3B82F6", hover_color="#2563EB", width=140, height=38, corner_radius=10, command=lambda: edit_selected_discount(tree))
    edit_btn.pack(side="right", padx=5)

    delete_btn = ctk.CTkButton(bottom_actions, text="🗑️  מחיקת מבצע", font=("Segoe UI", 13, "bold"), fg_color="#EF4444", hover_color="#DC2626", width=120, height=38, corner_radius=10, command=lambda: delete_selected_discount(tree))
    delete_btn.pack(side="right", padx=5)

    refresh_discounts_table(tree)


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
                    status, tag = "🔴 Expired", "expired"
                elif today < s_date:
                    status, tag = "🟡 Upcoming", "upcoming"
                else:
                    status, tag = "🟢 Active", "active"
                
                # תוקן פורמט התאריך ל-%Y-%m-%d הנקי ללא תווים עודפים
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

    save_btn = ctk.CTkButton(scrollable_frame, text="💾  שמור מבצע", font=("Segoe UI", 14, "bold"), fg_color="#10B981", hover_color="#059669", height=42, corner_radius=10,
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
                messagebox.showerror("שגיאה", f"קוד מבצע מספר {d_id} כבר קיים במערכת.")
            else:
                messagebox.showerror("שגיאה", f"הפעולה נכשלה:\n{e}")
        finally:
            cursor.close()
            conn.close()


def edit_selected_discount(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("בחירה חובה", "אנא בחרי מבצע מהטבלה לצורך עריכה.")
        return
    val = tree.item(selected[0], 'values')
    data = {'id': val[5], 'name': val[4], 'percentage': val[3].replace("%",""), 'start': val[2], 'end': val[1]}
    open_discount_modal(tree, data)


def delete_selected_discount(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("בחירה חובה", "אנא בחרי מבצע למחיקה.")
        return
    val = tree.item(selected[0], 'values')
    d_id = val[5]
    
    confirm = messagebox.askyesno("אישור", f"האם את בטוחה שברצונך למחוק את מבצע מספר {d_id}?\nשים לב: פעולה זו תסיר את המבצע מכל המוצרים המקושרים אליו!")
    if not confirm: return

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM APPLIES_TO WHERE DiscountID = %s;", (int(d_id),))
            cursor.execute("DELETE FROM DISCOUNT WHERE DiscountID = %s;", (int(d_id),))
            conn.commit()
            messagebox.showinfo("הצלחה", "המבצע נמחק לחלוטין.")
            refresh_discounts_table(tree)
        except Exception as e:
            messagebox.showerror("שגיאה", f"המחיקה נכשלה:\n{e}")
        finally:
            cursor.close()
            conn.close()


# =====================================================================
# 📑 כרטיסייה 2: החלת מבצעים על מוצרים (טבלת APPLIES_TO)
# =====================================================================
def setup_applies_to_tab(tab):
    action_frame = ctk.CTkFrame(tab, fg_color="transparent")
    action_frame.pack(fill="x", pady=(10, 15))

    refresh_btn = ctk.CTkButton(action_frame, text="🔄  רענן שיוכים", font=("Segoe UI", 13, "bold"), fg_color="#4B5563", hover_color="#374151", width=120, height=38, corner_radius=10, command=lambda: refresh_applies_table(tree))
    refresh_btn.pack(side="left", padx=5)

    add_btn = ctk.CTkButton(action_frame, text="🔗  החלת מבצע על מוצר", font=("Segoe UI", 13, "bold"), fg_color="#10B981", hover_color="#059669", width=180, height=38, corner_radius=10, command=lambda: open_applies_modal(tree))
    add_btn.pack(side="right", padx=5)

    table_container = ctk.CTkFrame(tab, fg_color="#FFFFFF", corner_radius=18, border_color="#E5E7EB", border_width=1)
    table_container.pack(fill="both", expand=True, pady=(0, 15))

    # מפתחות ה-ID הועברו לסוף והוסתרו מהתצוגה הגלויה
    columns = ("discount_pct", "discount_name", "product_brand", "product_name", "hidden_discount_id", "hidden_product_id")
    tree = ttk.Treeview(table_container, columns=columns, show="headings", style="Custom.Treeview")

    tree.heading("product_name", text="שם מוצר", anchor="center")
    tree.heading("product_brand", text="מותג מוצר", anchor="center")
    tree.heading("discount_name", text="מבצע מוחל", anchor="center")
    tree.heading("discount_pct", text="אחוז הנחה בסניפים", anchor="center")

    tree.column("product_name", width=150, anchor="center")
    tree.column("product_brand", width=120, anchor="center")
    tree.column("discount_name", width=180, anchor="center")
    tree.column("discount_pct", width=120, anchor="center")
    
    # הסתרת מפתחות ה-ID כדי לשמור על הנקיון החזותי שביקשת
    tree.column("hidden_discount_id", width=0, stretch=tk.NO)
    tree.column("hidden_product_id", width=0, stretch=tk.NO)

    scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="left", fill="y", padx=(10, 0), pady=15)
    tree.pack(fill="both", expand=True, padx=15, pady=15)

    bottom_actions = ctk.CTkFrame(tab, fg_color="transparent")
    bottom_actions.pack(fill="x", pady=(0, 10))

    # הוספת כפתור העריכה החדש לשיוך המבצעים!
    edit_btn = ctk.CTkButton(bottom_actions, text="✏️  עריכת שיוך מבצע", font=("Segoe UI", 13, "bold"), fg_color="#3B82F6", hover_color="#2563EB", width=150, height=38, corner_radius=10, command=lambda: edit_selected_applies(tree))
    edit_btn.pack(side="right", padx=5)

    delete_btn = ctk.CTkButton(bottom_actions, text="❌  ביטול מבצע ממוצר", font=("Segoe UI", 13, "bold"), fg_color="#EF4444", hover_color="#DC2626", width=160, height=38, corner_radius=10, command=lambda: delete_applies_link(tree))
    delete_btn.pack(side="right", padx=5)

    refresh_applies_table(tree)


def refresh_applies_table(tree):
    for item in tree.get_children():
        tree.delete(item)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            query = """
                SELECT a.ProductID, p.ProductName, p.Brand, a.DiscountID, d.DiscountName, d.DiscountPercentage
                FROM APPLIES_TO a
                JOIN PRODUCT p ON a.ProductID = p.ProductID
                JOIN DISCOUNT d ON a.DiscountID = d.DiscountID
                ORDER BY a.ProductID ASC, a.DiscountID ASC;
            """
            cursor.execute(query)
            for row in cursor.fetchall():
                # סדר הנתונים תואם לאינדקסים: [0]=pct, [1]=disc_name, [2]=brand, [3]=prod_name, [4]=hidden_discount_id, [5]=hidden_product_id
                tree.insert("", "end", values=(f"{row[5]}%", row[4], row[2], row[1], row[3], row[0]))
        except Exception as e:
            print(f"Error refreshing applies_to view: {e}")
        finally:
            cursor.close()
            conn.close()


def get_available_ids_with_names(table_name, id_column, name_column):
    """שליפת מזהים משולבים בשמות עבור ה-OptionMenu כדי לתת חווית CRUD מובנת"""
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
    """מודל הוספה ועריכה עבור שיוך מבצעים (APPLIES_TO CRUD)"""
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
        # במצב עריכה: נועלים את המוצר (חלק מהמפתח) ומאפשרים לשנות את ההנחה שחלה עליו
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

    save_btn = ctk.CTkButton(modal, text="💾  שמור שיוך מעודכן" if is_edit else "🔗  בצע שיוך מבצע", 
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
                # פעולת UPDATE על טבלת הקשר: מעדכנים את ה-DiscountID עבור אותו ProductID
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
    """שליפת מפתחות ה-ID הנסתרים מהכרטיסייה השנייה לצורך עריכת ההנחה על המוצר"""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("בחירה חובה", "אנא בחרי שורת שיוך מהטבלה לצורך עריכה.")
        return
    val = tree.item(selected[0], 'values')
    
    # שליפת ה-IDs הנסתרים מהאינדקסים האחרונים (4 ו-5)
    edit_data = {
        'discount_id': val[4],
        'product_id': val[5]
    }
    open_applies_modal(tree, edit_data)


def delete_applies_link(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("בחירה חובה", "אנא בחרי שורת שיוך מהטבלה לביטול המבצע.")
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