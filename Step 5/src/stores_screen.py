import customtkinter as ctk
from tkinter import ttk, messagebox
import tkinter as tk
from db_connection import get_db_connection

def show_stores_view(main_frame):
    # ניקוי המסך למניעת כפילויות תצוגה
    for widget in main_frame.winfo_children():
        widget.destroy()

    # --- כותרת עליונה ---
    header_label = ctk.CTkLabel(main_frame, text="ניהול סניפי הרשת", font=("Segoe UI", 32, "bold"), text_color="#111827", anchor="e")
    header_label.pack(pady=(35, 4), padx=35, fill="x")
    
    sub_header = ctk.CTkLabel(main_frame, text="צפייה, הוספה, עריכה ומחיקה של סניפים פעילים במערכת", font=("Segoe UI", 14, "bold"), text_color="#4B5563", anchor="e")
    sub_header.pack(pady=(0, 20), padx=35, fill="x")

    # --- שורת חיפוש עליונה ---
    search_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    search_frame.pack(padx=35, fill="x", pady=(0, 15))
    
    search_lbl = ctk.CTkLabel(search_frame, text="🔍   חיפוש סניף לפי שם", font=("Segoe UI", 13, "bold"), text_color="#374151")
    search_lbl.pack(side="right", padx=(10, 0))
    
    search_entry = ctk.CTkEntry(search_frame, placeholder_text="הקלידי שם סניף לחיפוש", font=("Segoe UI", 13), width=280, height=35, corner_radius=8, justify="right")
    search_entry.pack(side="right")
    
    # הפעלת חיפוש בזמן אמת בעת הקלדה
    search_entry.bind("<KeyRelease>", lambda event: refresh_table(tree, search_entry.get().strip()))

    # --- ✨ החזרה למקום המקורי: שורת כפתורי פעולה מתחת לחיפוש ---
    action_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    action_frame.pack(padx=35, fill="x", pady=(0, 15))

    # כפתור הוספת סניף חזר למיקומו המקורי בצד ימין (כפתור הרענון הוסר בהצלחה)
    add_btn = ctk.CTkButton(action_frame, text="➕   הוספת סניף חדש", font=("Segoe UI", 13, "bold"), fg_color="#10B981", hover_color="#059669", width=160, height=40, corner_radius=10, command=lambda: open_store_modal(tree))
    add_btn.pack(side="right", padx=5)

    # --- אזור הטבלה המרכזי ---
    table_container = ctk.CTkFrame(main_frame, fg_color="#FFFFFF", corner_radius=18, border_color="#E5E7EB", border_width=1)
    table_container.pack(fill="both", expand=True, padx=35, pady=(0, 20))

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

    # שמירה על עמודת קוד סניף גלויה בטבלה
    columns = ("emp_count", "region", "address", "website", "rating", "email", "phone", "name", "store_id")
    tree = ttk.Treeview(table_container, columns=columns, show="headings", style="Custom.Treeview")

    # כותרות העמודות
    tree.heading("store_id", text="קוד סניף", anchor="center")
    tree.heading("name", text="שם סניף", anchor="center")
    tree.heading("phone", text="טלפון", anchor="center")
    tree.heading("email", text="אימייל", anchor="center")
    tree.heading("rating", text="דירוג", anchor="center")
    tree.heading("website", text="כתובת אתר", anchor="center")
    tree.heading("address", text="כתובת פיזית", anchor="center")
    tree.heading("region", text="מחוז/אזור", anchor="center")
    tree.heading("emp_count", text="מספר עובדים", anchor="center")

    # רוחב ומתיחה נכונה לעמודות
    tree.column("store_id", width=90, anchor="center", stretch=tk.NO)
    tree.column("name", width=260, anchor="e", stretch=tk.YES)       
    tree.column("phone", width=140, anchor="center", stretch=tk.NO)
    tree.column("email", width=220, anchor="center", stretch=tk.NO)
    tree.column("rating", width=100, anchor="center", stretch=tk.NO)
    tree.column("website", width=200, anchor="center", stretch=tk.NO)
    tree.column("address", width=320, anchor="e", stretch=tk.YES)    
    tree.column("region", width=120, anchor="center", stretch=tk.NO)
    tree.column("emp_count", width=130, anchor="center", stretch=tk.NO)

    tree.tag_configure("has_employees", foreground="#1E3A8A", font=("Segoe UI", 12, "bold"))
    tree.tag_configure("no_employees", foreground="#6B7280", font=("Segoe UI", 12))

    # סרגלי גלילה
    v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=tree.yview)
    h_scrollbar = ttk.Scrollbar(table_container, orient="horizontal", command=tree.xview)
    
    tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
    
    h_scrollbar.pack(side="bottom", fill="x", padx=15, pady=(0, 10))
    v_scrollbar.pack(side="left", fill="y", padx=(10, 0), pady=15)
    tree.pack(side="right", fill="both", expand=True, padx=(15, 0), pady=15)

    # שורת כפתורי CRUD תחתונים
    bottom_actions = ctk.CTkFrame(main_frame, fg_color="transparent")
    bottom_actions.pack(padx=35, fill="x", pady=(0, 30))

    edit_btn = ctk.CTkButton(bottom_actions, text="✏️   עריכת סניף נבחר", font=("Segoe UI", 13, "bold"), fg_color="#3B82F6", hover_color="#2563EB", width=150, height=38, corner_radius=10, command=lambda: edit_selected_store(tree))
    edit_btn.pack(side="right", padx=5)

    delete_btn = ctk.CTkButton(bottom_actions, text="🗑️   מחיקת סניף", font=("Segoe UI", 13, "bold"), fg_color="#EF4444", hover_color="#DC2626", width=120, height=38, corner_radius=10, command=lambda: delete_selected_store(tree))
    delete_btn.pack(side="right", padx=5)

    refresh_table(tree)


def refresh_table(tree, search_query=""):
    for item in tree.get_children():
        tree.delete(item)

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            if search_query:
                query = """
                    SELECT s.StoreID, s.StoreName, s.Phone, s.StoreEmail, s.Rating, s.websiteurl, s.Address, s.Region,
                           COUNT(e.EmployeeID) AS TotalEmployees
                    FROM STORE s
                    LEFT JOIN EMPLOYEE e ON s.StoreID = e.StoreID
                    WHERE s.StoreName ILIKE %s
                    GROUP BY s.StoreID, s.StoreName, s.Phone, s.StoreEmail, s.Rating, s.websiteurl, s.Address, s.Region
                    ORDER BY s.StoreID ASC;
                """
                cursor.execute(query, (f"%{search_query}%",))
            else:
                query = """
                    SELECT s.StoreID, s.StoreName, s.Phone, s.StoreEmail, s.Rating, s.websiteurl, s.Address, s.Region,
                           COUNT(e.EmployeeID) AS TotalEmployees
                    FROM STORE s
                    LEFT JOIN EMPLOYEE e ON s.StoreID = e.StoreID
                    GROUP BY s.StoreID, s.StoreName, s.Phone, s.StoreEmail, s.Rating, s.websiteurl, s.Address, s.Region
                    ORDER BY s.StoreID ASC;
                """
                cursor.execute(query)

            rows = cursor.fetchall()
            for row in rows:
                web_val = row[5] if row[5] else "-"
                addr_val = row[6] if row[6] else "-"
                reg_val = row[7] if row[7] else "-"
                emp_count = row[8]
                
                emp_display = f"👥  {emp_count}" if emp_count > 0 else "0"
                row_tag = "has_employees" if emp_count > 0 else "no_employees"
                
                tree.insert("", "end", values=(emp_display, reg_val, addr_val, web_val, f"⭐ {row[4]}/10", row[3], row[2], row[1], row[0]), tags=(row_tag,))
        except Exception as e:
            messagebox.showerror("שגיאה", f"נכשלה שליפת הנתונים: {e}")
        finally:
            cursor.close()
            conn.close()


def open_store_modal(tree, store_data=None):
    is_edit = store_data is not None
    title_text = "✏️ עדכון פרטי סניף" if is_edit else "➕ הוספת סניף חדש לרשת"
    
    modal = ctk.CTkToplevel()
    modal.title(title_text)
    modal.geometry("480x620")
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

    regions_list = ["East", "Center", "West", "North", "South"]
    ratings_list = [str(i) for i in range(1, 11)]

    fields_config = [
        {"label": "קוד סניף מספר", "key": "id", "type": "entry"},
        {"label": "שם הסניף", "key": "name", "type": "entry"},
        {"label": "מספר טלפון", "key": "phone", "type": "entry"},
        {"label": "כתובת אימייל", "key": "email", "type": "entry"},
        {"label": "כתובת אתר אינטרנט", "key": "website", "type": "entry"},
        {"label": "כתובת פיזית רחוב ועיר", "key": "address", "type": "entry"},
        {"label": "דירוג סניף", "key": "rating", "type": "option", "options": ratings_list},
        {"label": "מחוז או אזור", "key": "region", "type": "option", "options": regions_list}
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
                widget.insert(0, store_data['id'])
                widget.configure(state="disabled", fg_color="#E5E7EB")
            elif is_edit:
                widget.insert(0, store_data[cfg["key"]])
                
        elif cfg["type"] == "option":
            widget = ctk.CTkOptionMenu(
                frame, values=cfg["options"], font=("Segoe UI", 13), height=35, corner_radius=8,
                fg_color="#FFFFFF", text_color="#111827", button_color="#E5E7EB", button_hover_color="#D1D5DB",
                dropdown_font=("Segoe UI", 12), anchor="e"
            )
            widget.pack(fill="x")
            
            if is_edit:
                val = store_data[cfg["key"]]
                widget.set(val) if val in cfg["options"] else widget.set(cfg["options"][0])
            else:
                widget.set(cfg["options"][0])
                
        widgets_dict[cfg["key"]] = widget

    save_btn = ctk.CTkButton(scrollable_frame, text="💾   שמור שינויים" if is_edit else "✅   הוסף סניף", 
                             font=("Segoe UI", 14, "bold"), fg_color="#10B981", hover_color="#059669", 
                             height=42, corner_radius=10, 
                             command=lambda: save_store(modal, widgets_dict, tree, is_edit))
    save_btn.pack(fill="x", padx=40, pady=(25, 30))


def save_store(modal, widgets, tree, is_edit):
    s_id = widgets["id"].get().strip()
    name = widgets["name"].get().strip()
    phone = widgets["phone"].get().strip()
    email = widgets["email"].get().strip()
    website = widgets["website"].get().strip()
    address = widgets["address"].get().strip()
    rating = widgets["rating"].get()
    region = widgets["region"].get()

    if not s_id or not name or not phone or not email:
        messagebox.showwarning("שדות חסרים", "אנא מלאי את כל שדות החובה (קוד, שם, טלפון ואימייל).")
        return

    rating_val = int(rating)
    web_val = website if website else None
    addr_val = address if address else None

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            if is_edit:
                cursor.execute("""
                    UPDATE STORE 
                    SET StoreName = %s, Phone = %s, StoreEmail = %s, Rating = %s, websiteurl = %s, Address = %s, Region = %s 
                    WHERE StoreID = %s;
                """, (name, phone, email, rating_val, web_val, addr_val, region, int(s_id)))
                conn.commit()
                messagebox.showinfo("הצלחה", "הנתונים עודכנו בהצלחה!")
                modal.destroy()
                refresh_table(tree)
            else:
                cursor.execute("""
                    INSERT INTO STORE (StoreID, StoreName, Phone, StoreEmail, Rating, websiteurl, Address, Region) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                """, (int(s_id), name, phone, email, rating_val, web_val, addr_val, region))
                conn.commit()
                messagebox.showinfo("הצלחה", "הסניף החדש נוסף בהצלחה לרשת!")
                modal.destroy()
                refresh_table(tree)
        except Exception as e:
            error_msg = str(e)
            if "duplicate key" in error_msg or "already exists" in error_msg:
                messagebox.showerror(
                    "קוד סניף קיים במערכת", 
                    f"לא ניתן לבצע רישום לסניף החדש.\n\n"
                    f"💡 הסיבה:\n"
                    f"קוד סניף מספר {s_id} כבר תפוס ורשום על ידי חנות אחרת ברשת!\n\n"
                    f"🛠️ מה צריך לעשות?\n"
                    f"אנא בחרי מספר מזהה (קוד) ייחודי ופנוי שאינו קיים עדיין במערכת."
                )
            else:
                messagebox.showerror("שגיאה בפעולה", f"הפעולה נכשלה במערכת:\n{error_msg}")
        finally:
            cursor.close()
            conn.close()


def edit_selected_store(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("נא לבחור שורה", "אנא בחרי סניף מהטבלה לצורך עריכה.")
        return
    
    item_values = tree.item(selected[0], 'values')
    
    store_data = {
        'id': item_values[8],  
        'name': item_values[7],
        'phone': item_values[6],
        'email': item_values[5],
        'rating': item_values[4].replace("⭐ ", "").replace("/10", "").strip(),
        'website': "" if item_values[3] == "-" else item_values[3],
        'address': "" if item_values[2] == "-" else item_values[2],
        'region': item_values[1].strip()
    }
    open_store_modal(tree, store_data)


def delete_selected_store(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("נא לבחור שורה", "אנא בחרי סניף מהטבלה למחיקה.")
        return
    
    item_values = tree.item(selected[0], 'values')
    store_id = item_values[8] 
    store_name = item_values[7]

    confirm = messagebox.askyesno("אישור מחיקה", f"האם את בטוחה שברצונך למחוק את סניף '{store_name}'?")
    if not confirm:
        return

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM STORE WHERE StoreID = %s;", (int(store_id),))
            conn.commit()
            messagebox.showinfo("הצלחה", f"סניף '{store_name}' נמחק בהצלחה מהמערכת.")
            refresh_table(tree)
        except Exception as e:
            error_msg = str(e)
            if "foreign key constraint" in error_msg or "is still referenced" in error_msg:
                messagebox.showerror(
                    "לא ניתן למחוק - סניף פעיל ברשת", 
                    f"פעולת המחיקה עבור סניף '{store_name}' נחסמה באופן מאובטח.\n\n"
                    f"💡 מדוע זה קרה?\n"
                    f"בסיס הנתונים מזהה שקיימים כרגע ברשת נתונים פעילים המשויכים ישירות לחנות הזו (עובדים הרשומים בסניף, סחורה קיימת במלאי, או הזמנות הפצה בתהליך).\n\n"
                    f"🛠️ מה צריך לעשות עכשיו?\n"
                    f"על מנת לבצע את המחיקה, יש להיכנס תחילה ללשוניות המתאימות (כמו 'ניהול עובדים' או 'מלאי') ולהעביר או למחוק את הרשומות המשויכות לסניף זה."
                )
            else:
                messagebox.showerror("שגיאה במחיקה", f"פעולת המחיקה נכשלה:\n{error_msg}")
        finally:
            cursor.close()
            conn.close()