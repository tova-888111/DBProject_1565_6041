import customtkinter as ctk
from tkinter import ttk, messagebox
import tkinter as tk
from db_connection import get_db_connection

def show_employees_view(main_frame):
    # ניקוי המסך למניעת כפילויות תצוגה
    for widget in main_frame.winfo_children():
        widget.destroy()

    # --- כותרת עליונה ---
    header_label = ctk.CTkLabel(main_frame, text="ניהול עובדי הרשת", font=("Segoe UI", 28, "bold"), text_color="#111827", anchor="e")
    header_label.pack(pady=(30, 2), padx=35, fill="x")
    
    sub_header = ctk.CTkLabel(main_frame, text="צפייה, הוספה, עריכה ופיטורין של צוות העובדים בכלל סניפי הרשת", font=("Segoe UI", 14), text_color="#6B7280", anchor="e")
    sub_header.pack(pady=(0, 15), padx=35, fill="x")

    # --- שורת חיפוש עליונה לפי שם סניף ---
    search_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    search_frame.pack(padx=35, fill="x", pady=(0, 15))
    
    search_lbl = ctk.CTkLabel(search_frame, text="🔍  סינון עובדים לפי שם סניף", font=("Segoe UI", 13, "bold"), text_color="#374151")
    search_lbl.pack(side="right", padx=(10, 0))
    
    search_entry = ctk.CTkEntry(search_frame, placeholder_text="הקלידי שם סניף (למשל: ירושלים)...", font=("Segoe UI", 13), width=320, height=35, corner_radius=8, justify="right")
    search_entry.pack(side="right")
    
    search_entry.bind("<KeyRelease>", lambda event: refresh_table(tree, search_entry.get().strip()))

    # --- שורת כפתורי פעולה עליונה ---
    action_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    action_frame.pack(padx=35, fill="x", pady=(0, 15))

    refresh_btn = ctk.CTkButton(action_frame, text="🔄  רענן נתונים", font=("Segoe UI", 13, "bold"), fg_color="#4B5563", hover_color="#374151", width=120, height=40, corner_radius=10, 
                             command=lambda: [search_entry.delete(0, tk.END), refresh_table(tree)])
    refresh_btn.pack(side="left", padx=5)

    add_btn = ctk.CTkButton(action_frame, text="➕  הוספת עובד חדש", font=("Segoe UI", 13, "bold"), fg_color="#10B981", hover_color="#059669", width=160, height=40, corner_radius=10, command=lambda: open_employee_modal(tree))
    add_btn.pack(side="right", padx=5)

    # --- אזור הטבלה המרכזי ---
    table_container = ctk.CTkFrame(main_frame, fg_color="#FFFFFF", corner_radius=18, border_color="#E5E7EB", border_width=1)
    table_container.pack(fill="both", expand=True, padx=35, pady=(0, 20))

    # הגדרת משקלים (Weights) - כעת עמודה 1 (הטבלה) מתרחבת, ועמודה 0 (הגלילה) קבועה בצד שמאל
    table_container.grid_rowconfigure(0, weight=1)
    table_container.grid_columnconfigure(0, weight=0) # סרגל גלילה משמאל
    table_container.grid_columnconfigure(1, weight=1) # הטבלה מימין

    style = ttk.Style()
    style.theme_use("clam")
    
    style.configure("Custom.Treeview",
                    background="#FFFFFF",
                    foreground="#111827",
                    rowheight=40,
                    fieldbackground="#FFFFFF",
                    font=("Segoe UI", 12),
                    borderwidth=0,
                    relief="flat")
    
    style.configure("Custom.Treeview.Heading",
                    background="#F9FAFB",
                    foreground="#4B5563",
                    font=("Segoe UI", 13, "bold"),
                    relief="flat",
                    borderwidth=0)
    
    style.map("Custom.Treeview", background=[('selected', '#E0F2FE')], foreground=[('selected', '#0369A1')])

    columns = ("store_name", "role", "salary", "status", "last_name", "first_name", "hidden_store_id", "hidden_emp_id")
    tree = ttk.Treeview(table_container, columns=columns, show="headings", style="Custom.Treeview")

    tree.heading("first_name", text="שם פרטי", anchor="center")
    tree.heading("last_name", text="שם משפחה", anchor="center")
    tree.heading("status", text="סטטוס עבודה", anchor="center")
    tree.heading("salary", text="שכר חודשי", anchor="center")
    tree.heading("role", text="תפקיד", anchor="center")
    tree.heading("store_name", text="משויך לסניף", anchor="center")

    # הגדרת מתיחה דינמית לעמודות כדי שימלאו את כל שטח הבלוק בצורה סימטרית
    tree.column("first_name", width=120, anchor="center", stretch=tk.YES)
    tree.column("last_name", width=120, anchor="center", stretch=tk.YES)
    tree.column("status", width=110, anchor="center", stretch=tk.YES)
    tree.column("salary", width=110, anchor="center", stretch=tk.YES)
    tree.column("role", width=250, anchor="center", stretch=tk.YES)        
    tree.column("store_name", width=340, anchor="e", stretch=tk.YES)      
    
    tree.column("hidden_store_id", width=0, stretch=tk.NO)
    tree.column("hidden_emp_id", width=0, stretch=tk.NO)

    tree.tag_configure("active_status", foreground="#10B981", font=("Segoe UI", 12, "bold"))
    tree.tag_configure("inactive_status", foreground="#EF4444", font=("Segoe UI", 12, "bold"))

    # יצירת סרגל גלילה אנכי בלבד (ללא גלילה אופקית)
    v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=v_scrollbar.set)
    
    # --- מיקום מעודכן: סרגל הגלילה בעמודה 0 (שמאל) והטבלה בעמודה 1 (ימין) ---
    v_scrollbar.grid(row=0, column=0, sticky="ns", pady=15, padx=(15, 0))
    tree.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)

    # שורת כפתורי CRUD תחתונים
    bottom_actions = ctk.CTkFrame(main_frame, fg_color="transparent")
    bottom_actions.pack(padx=35, fill="x", pady=(0, 30))

    edit_btn = ctk.CTkButton(bottom_actions, text="✏️  עריכת פרטי עובד", font=("Segoe UI", 13, "bold"), fg_color="#3B82F6", hover_color="#2563EB", width=150, height=38, corner_radius=10, command=lambda: edit_selected_employee(tree))
    edit_btn.pack(side="right", padx=5)

    delete_btn = ctk.CTkButton(bottom_actions, text="🗑️  מחיקת עובד", font=("Segoe UI", 13, "bold"), fg_color="#EF4444", hover_color="#DC2626", width=120, height=38, corner_radius=10, command=lambda: delete_selected_employee(tree))
    delete_btn.pack(side="right", padx=5)

    refresh_table(tree)


def refresh_table(tree, store_search_query=""):
    for item in tree.get_children():
        tree.delete(item)

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            if store_search_query:
                query = """
                    SELECT e.EmployeeID, e.FirstName, e.LastName, e.Status, e.Salary, e.Role, e.StoreID, s.StoreName
                    FROM EMPLOYEE e
                    JOIN STORE s ON e.StoreID = s.StoreID
                    WHERE s.StoreName ILIKE %s
                    ORDER BY e.EmployeeID ASC;
                """
                cursor.execute(query, (f"%{store_search_query}%",))
            else:
                query = """
                    SELECT e.EmployeeID, e.FirstName, e.LastName, e.Status, e.Salary, e.Role, e.StoreID, s.StoreName
                    FROM EMPLOYEE e
                    JOIN STORE s ON e.StoreID = s.StoreID
                    ORDER BY e.EmployeeID ASC;
                """
                cursor.execute(query)

            rows = cursor.fetchall()
            for row in rows:
                status_val = str(row[3]).strip()
                salary_display = f"₪{row[4]:,}"
                
                if status_val == "Active":
                    row_tag = "active_status"
                else:
                    row_tag = "inactive_status"
                
                tree.insert("", "end", values=(row[7], row[5], salary_display, status_val, row[2], row[1], row[6], row[0]), tags=(row_tag,))
        except Exception as e:
            messagebox.showerror("שגיאה", f"נכשלה שליפת נתוני עובדים: {e}")
        finally:
            cursor.close()
            conn.close()


def get_all_store_ids():
    store_ids = []
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT StoreID FROM STORE ORDER BY StoreID ASC;")
            for (s_id,) in cursor.fetchall():
                store_ids.append(str(s_id))
        except Exception as e:
            print(f"Error fetching store IDs: {e}")
        finally:
            cursor.close()
            conn.close()
    return store_ids


def open_employee_modal(tree, employee_data=None):
    is_edit = employee_data is not None
    title_text = "✏️ עדכון פרטי עובד" if is_edit else "➕ הוספת עובד חדש לרשת"
    
    modal = ctk.CTkToplevel()
    modal.title(title_text)
    modal.geometry("480x580")
    modal.resizable(True, True)  
    modal.lift()
    modal.focus_force()
    modal.grab_set()

    canvas = tk.Canvas(modal, bg="#F3F4F6", highlightthickness=0)
    scrollbar = ctk.CTkScrollbar(modal, orientation="vertical", command=canvas.yview)
    scrollable_frame = ctk.CTkFrame(canvas, fg_color="#F3F4F6", corner_radius=0)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=460)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="left", fill="y")
    canvas.pack(side="right", fill="both", expand=True)

    ctk.CTkLabel(scrollable_frame, text=title_text, font=("Segoe UI", 20, "bold"), text_color="#111827").pack(pady=(25, 20))

    available_store_ids = get_all_store_ids()
    if not available_store_ids:
        available_store_ids = ["אין סניפים"]

    status_options = ["Active", "Inactive"]

    fields_config = [
        {"label": "תעודת זהות עובד מספר", "key": "id", "type": "entry"},
        {"label": "שם פרטי", "key": "first_name", "type": "entry"},
        {"label": "שם משפחה", "key": "last_name", "type": "entry"},
        {"label": "תפקיד עובד", "key": "role", "type": "entry"},
        {"label": "שכר חודשי בשקלים", "key": "salary", "type": "entry"},
        {"label": "סטטוס עבודה ברשת", "key": "status", "type": "option", "options": status_options},
        {"label": "קוד סניף משויך (ID המפתח הזר)", "key": "store_id", "type": "option", "options": available_store_ids}
    ]
    
    widgets_dict = {}
    
    for cfg in fields_config:
        frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        frame.pack(fill="x", padx=40, pady=6)
        
        lbl = ctk.CTkLabel(frame, text=cfg["label"], font=("Segoe UI", 13), text_color="#4B5563", anchor="e")
        lbl.pack(fill="x", pady=(0, 2))
        
        if cfg["type"] == "entry":
            widget = ctk.CTkEntry(frame, font=("Segoe UI", 13), height=35, corner_radius=8, justify="right")
            widget.pack(fill="x")
            
            if is_edit and cfg["key"] == "id":
                widget.insert(0, employee_data['id'])
                widget.configure(state="disabled", fg_color="#E5E7EB")
            elif is_edit:
                widget.insert(0, employee_data[cfg["key"]])
                
        elif cfg["type"] == "option":
            widget = ctk.CTkOptionMenu(
                frame, values=cfg["options"], font=("Segoe UI", 13), height=35, corner_radius=8,
                fg_color="#FFFFFF", text_color="#111827", button_color="#E5E7EB", button_hover_color="#D1D5DB",
                dropdown_font=("Segoe UI", 12), anchor="e"
            )
            widget.pack(fill="x")
            
            if is_edit:
                val = str(employee_data[cfg["key"]])
                widget.set(val) if val in cfg["options"] else widget.set(cfg["options"][0])
            else:
                widget.set(cfg["options"][0])
                
        widgets_dict[cfg["key"]] = widget

    save_btn = ctk.CTkButton(scrollable_frame, text="💾  שמור שינויים" if is_edit else "✅  הוסף עובד", 
                             font=("Segoe UI", 14, "bold"), fg_color="#10B981", hover_color="#059669", 
                             height=42, corner_radius=10, 
                             command=lambda: save_employee(modal, widgets_dict, tree, is_edit))
    save_btn.pack(fill="x", padx=40, pady=(25, 30))


def save_employee(modal, widgets, tree, is_edit):
    emp_id = widgets["id"].get().strip()
    first_name = widgets["first_name"].get().strip()
    last_name = widgets["last_name"].get().strip()
    role = widgets["role"].get().strip()
    salary = widgets["salary"].get().strip()
    status = widgets["status"].get()
    store_id_str = widgets["store_id"].get()

    if not emp_id or not first_name or not last_name or not role or not salary:
        messagebox.showwarning("שדות חסרים", "אנא מלאי את כל שדות החובה של העובד.")
        return

    if store_id_str == "אין סניפים" or not store_id_str.isdigit():
        messagebox.showerror("שגיאת מפתח זר", "לא ניתן להוסיף עובד ללא בחירת קוד סניף תקין וקיים במערכת!")
        return

    store_id = int(store_id_str)

    try:
        salary_val = float(salary.replace("₪", "").replace(",", "").strip())
    except ValueError:
        messagebox.showwarning("נתון שגוי", "השכר חייב להיות מספר תקין.")
        return

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            if is_edit:
                cursor.execute("""
                    UPDATE EMPLOYEE 
                    SET FirstName = %s, LastName = %s, Status = %s, Salary = %s, Role = %s, StoreID = %s 
                    WHERE EmployeeID = %s;
                """, (first_name, last_name, status, salary_val, role, store_id, int(emp_id)))
            else:
                cursor.execute("""
                    INSERT INTO EMPLOYEE (EmployeeID, FirstName, LastName, Status, Salary, Role, StoreID) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                """, (int(emp_id), first_name, last_name, status, salary_val, role, store_id))
            
            conn.commit()
            messagebox.showinfo("הצלחה", "פרטי העובד נשמרו בהצלחה!")
            modal.destroy()
            refresh_table(tree)
        except Exception as e:
            error_msg = str(e)
            if "duplicate key" in error_msg or "already exists" in error_msg:
                messagebox.showerror("תעודת זהות קיימת", f"לא ניתן להוסיף את העובד.\nעובד עם תעודת זהות מספר {emp_id} כבר רשום במערכת הרשת!")
            elif "foreign key" in error_msg:
                messagebox.showerror("שגיאת תלות", "קוד הסניף שנבחר אינו קיים עוד בדאטהבייס. אנא רענני את הנתונים.")
            else:
                messagebox.showerror("שגיאה", f"הפעולה נכשלה במערכת:\n{error_msg}")
        finally:
            cursor.close()
            conn.close()


def edit_selected_employee(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("נא לבחור שורה", "אנא בחרי עובד מהטבלה לצורך עריכה.")
        return
    
    item_values = tree.item(selected[0], 'values')
    
    employee_data = {
        'id': item_values[7],
        'first_name': item_values[5],
        'last_name': item_values[4],
        'status': item_values[3].strip(),
        'salary': item_values[2].replace("₪", "").replace(",", "").strip(),
        'role': item_values[1],
        'store_id': item_values[6]
    }
    open_employee_modal(tree, employee_data)


def delete_selected_employee(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("נא לבחור שורה", "אנא בחרי עובד מהטבלה למחיקה.")
        return
    
    item_values = tree.item(selected[0], 'values')
    emp_id = item_values[7]
    emp_name = f"{item_values[5]} {item_values[4]}"

    confirm = messagebox.askyesno("אישור מחיקה", f"האם את בטוחה שברצונך למחוק לצמיתות את העובד '{emp_name}' מהמערכת?")
    if not confirm:
        return

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM EMPLOYEE WHERE EmployeeID = %s;", (int(emp_id),))
            conn.commit()
            messagebox.showinfo("הצלחה", f"העובד '{emp_name}' נמחק בהצלחה מהרשת.")
            refresh_table(tree)
        except Exception as e:
            messagebox.showerror("שגיאה במחיקה", f"פעולת המחיקה נכשלה:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()