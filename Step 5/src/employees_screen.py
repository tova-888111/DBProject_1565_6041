import customtkinter as ctk
from tkinter import ttk, messagebox
import tkinter as tk
from db_connection import get_db_connection

def show_employees_view(main_frame):
    # ניקוי המסך למניעת כפילויות תצוגה
    for widget in main_frame.winfo_children():
        widget.destroy()

    # --- כותרת עליונה ---
    header_label = ctk.CTkLabel(main_frame, text="ניהול עובדי הרשת", font=("Segoe UI", 32, "bold"), text_color="#111827", anchor="e")
    header_label.pack(pady=(35, 4), padx=35, fill="x")
    
    sub_header = ctk.CTkLabel(main_frame, text="צפייה, הוספה, עריכה ופיטורין של צוות העובדים בכלל סניפי הרשת", font=("Segoe UI", 14, "bold"), text_color="#4B5563", anchor="e")
    sub_header.pack(pady=(0, 20), padx=35, fill="x")

    # --- שורת חיפוש עליונה משולבת (לפי מספר זהות וקוד סניף) ---
    search_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    search_frame.pack(padx=35, fill="x", pady=(0, 15))
    
    search_lbl = ctk.CTkLabel(search_frame, text="🔍  מסנני חיפוש", font=("Segoe UI", 13, "bold"), text_color="#374151")
    search_lbl.pack(side="right", padx=(10, 0))
    
    # 1. ✨ תיקון: שדה חיפוש לפי מספר זהות עובד
    search_emp_entry = ctk.CTkEntry(search_frame, placeholder_text="לפי מספר זהות עובד", font=("Segoe UI", 13), width=240, height=35, corner_radius=8, justify="right")
    search_emp_entry.pack(side="right", padx=5)
    
    # 2. ✨ תיקון: שדה חיפוש לפי קוד סניף
    search_store_id_entry = ctk.CTkEntry(search_frame, placeholder_text="לפי קוד סניף (מספר)", font=("Segoe UI", 13), width=160, height=35, corner_radius=8, justify="right")
    search_store_id_entry.pack(side="right", padx=5)
    
    # קישור אירועי הקלדה לעדכון דינמי משולב של שני השדות יחד בזמן אמת
    search_emp_entry.bind("<KeyRelease>", lambda event: refresh_table(tree, search_emp_entry.get().strip(), search_store_id_entry.get().strip()))
    search_store_id_entry.bind("<KeyRelease>", lambda event: refresh_table(tree, search_emp_entry.get().strip(), search_store_id_entry.get().strip()))

    # --- שורת כפתורי פעולה מתחת לחיפוש ---
    action_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    action_frame.pack(padx=35, fill="x", pady=(0, 15))

    add_btn = ctk.CTkButton(action_frame, text="➕  הוספת עובד חדש", font=("Segoe UI", 13, "bold"), fg_color="#10B981", hover_color="#059669", width=160, height=40, corner_radius=10, command=lambda: open_employee_modal(tree))
    add_btn.pack(side="right", padx=5)

    # --- אזור הטבלה המרכזי ---
    table_container = ctk.CTkFrame(main_frame, fg_color="#FFFFFF", corner_radius=18, border_color="#E5E7EB", border_width=1)
    table_container.pack(fill="both", expand=True, padx=35, pady=(0, 20))

    table_container.grid_rowconfigure(0, weight=1)
    table_container.grid_columnconfigure(0, weight=0) 
    table_container.grid_columnconfigure(1, weight=1) 

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

    columns = ("store_name", "store_id", "role", "salary", "status", "last_name", "first_name", "emp_id")
    tree = ttk.Treeview(table_container, columns=columns, show="headings", style="Custom.Treeview")

    tree.heading("emp_id", text="תעודת זהות", anchor="center")
    tree.heading("first_name", text="שם פרטי", anchor="center")
    tree.heading("last_name", text="שם משפחה", anchor="center")
    tree.heading("status", text="סטטוס עבודה", anchor="center")
    tree.heading("salary", text="שכר חודשי", anchor="center")
    tree.heading("role", text="תפקיד", anchor="center")
    tree.heading("store_id", text="קוד סניף", anchor="center")
    tree.heading("store_name", text="משויך לסניף", anchor="center")

    tree.column("emp_id", width=100, anchor="center", stretch=tk.NO)
    tree.column("first_name", width=120, anchor="center", stretch=tk.YES)
    tree.column("last_name", width=120, anchor="center", stretch=tk.YES)
    tree.column("status", width=110, anchor="center", stretch=tk.NO)
    tree.column("salary", width=110, anchor="center", stretch=tk.NO)
    tree.column("role", width=200, anchor="center", stretch=tk.YES) 
    tree.column("store_id", width=90, anchor="center", stretch=tk.NO)       
    tree.column("store_name", width=280, anchor="e", stretch=tk.YES)      

    tree.tag_configure("active_status", foreground="#10B981", font=("Segoe UI", 12, "bold"))
    tree.tag_configure("inactive_status", foreground="#EF4444", font=("Segoe UI", 12, "bold"))

    v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=v_scrollbar.set)
    
    v_scrollbar.grid(row=0, column=0, sticky="ns", pady=15, padx=(15, 0))
    tree.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)

    bottom_actions = ctk.CTkFrame(main_frame, fg_color="transparent")
    bottom_actions.pack(padx=35, fill="x", pady=(0, 30))

    edit_btn = ctk.CTkButton(bottom_actions, text="✏️  עריכת פרטי עובד", font=("Segoe UI", 13, "bold"), fg_color="#3B82F6", hover_color="#2563EB", width=150, height=38, corner_radius=10, command=lambda: edit_selected_employee(tree))
    edit_btn.pack(side="right", padx=5)

    delete_btn = ctk.CTkButton(bottom_actions, text="🗑️  מחיקת עובד", font=("Segoe UI", 13, "bold"), fg_color="#EF4444", hover_color="#DC2626", width=120, height=38, corner_radius=10, command=lambda: delete_selected_employee(tree))
    delete_btn.pack(side="right", padx=5)

    refresh_table(tree)


def refresh_table(tree, emp_id_query="", store_id_query=""):
    for item in tree.get_children():
        tree.delete(item)

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # ✨ תיקון: התאמת השאילתה לסינון המבוקש לפי תעודת זהות וקוד סניף
            query = """
                SELECT e.EmployeeID, e.FirstName, e.LastName, e.Status, e.Salary, e.Role, e.StoreID, s.StoreName
                FROM EMPLOYEE e
                JOIN STORE s ON e.StoreID = s.StoreID
                WHERE 1=1
            """
            params = []
            
            if emp_id_query and emp_id_query.isdigit():
                query += " AND e.EmployeeID = %s"
                params.append(int(emp_id_query))
                
            if store_id_query and store_id_query.isdigit():
                query += " AND e.StoreID = %s"
                params.append(int(store_id_query))
                
            query += " ORDER BY e.EmployeeID ASC;"
            cursor.execute(query, tuple(params))

            rows = cursor.fetchall()
            for row in rows:
                status_val = str(row[3]).strip()
                salary_display = f"₪{row[4]:,}"
                
                if status_val == "Active":
                    row_tag = "active_status"
                else:
                    row_tag = "inactive_status"
                
                tree.insert("", "end", values=(row[7], row[6], row[5], salary_display, status_val, row[2], row[1], row[0]), tags=(row_tag,))
        except Exception as e:
            messagebox.showerror("שגיאה", f"נכשלה שליפת נתוני עובדים: {e}")
        finally:
            cursor.close()
            conn.close()


def get_all_store_ids_with_names():
    """✨ תיקון: שליפת קוד סניף משולב יחד עם שם הסניף עבור המפתח הזר"""
    store_labels = []
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT StoreID, StoreName FROM STORE ORDER BY StoreID ASC;")
            for s_id, s_name in cursor.fetchall():
                store_labels.append(f"{s_id} - {s_name}")
        except Exception as e:
            print(f"Error fetching store IDs and names: {e}")
        finally:
            cursor.close()
            conn.close()
    return store_labels


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

    # שימוש ברשימה המורחבת של קוד + שם סניף
    available_stores = get_all_store_ids_with_names()
    if not available_stores:
        available_stores = ["אין סניפים"]

    status_options = ["Active", "Inactive"]

    fields_config = [
        {"label": "תעודת זהות עובד מספר", "key": "id", "type": "entry"},
        {"label": "שם פרטי", "key": "first_name", "type": "entry"},
        {"label": "שם משפחה", "key": "last_name", "type": "entry"},
        {"label": "תפקיד עובד", "key": "role", "type": "entry"},
        {"label": "שכר חודשי בשקלים", "key": "salary", "type": "entry"},
        {"label": "סטטוס עבודה ברשת", "key": "status", "type": "option", "options": status_options},
        {"label": "בחירת סניף (קוד ושם סניף)", "key": "store_id", "type": "option", "options": available_stores}
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
                # התאמה למצב עריכה: מציאת השורה שמתחילה באותו ID סניף
                found = False
                for item in cfg["options"]:
                    if item.startswith(val + " -"):
                        widget.set(item)
                        found = True
                        break
                if not found:
                    widget.set(cfg["options"][0])
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
    store_selection = widgets["store_id"].get()

    if not emp_id or not first_name or not last_name or not role or not salary:
        messagebox.showwarning("שדות חסרים", "אנא מלאי את כל שדות החובה של העובד.")
        return

    if store_selection == "אין סניפים" or " - " not in store_selection:
        messagebox.showerror("שגיאת מפתח זר", "לא ניתן להוסיף עובד ללא בחירת קוד סניף תקין וקיים במערכת!")
        return

    # חילוץ קוד הסניף (ID המספרי בלבד) מתוך השורה הנבחרת
    store_id = int(store_selection.split(" - ")[0])

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
        messagebox.showwarning("נא לבחור שורה", "אנא בחר עובד מהטבלה לצורך עריכה.")
        return
    
    item_values = tree.item(selected[0], 'values')
    
    store_data = {
        'id': item_values[7],
        'first_name': item_values[6],
        'last_name': item_values[5],
        'status': item_values[4].strip(),
        'salary': item_values[3].replace("₪", "").replace(",", "").strip(),
        'role': item_values[2],
        'store_id': item_values[1]
    }
    open_employee_modal(tree, store_data)


def delete_selected_employee(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("נא לבחור שורה", "אנא בחרי עובד מהטבלה למחיקה.")
        return
    
    item_values = tree.item(selected[0], 'values')
    emp_id = item_values[7]
    emp_name = f"{item_values[6]} {item_values[5]}"

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