import re

def clean_id(name):
    return name.replace('"', '').strip().lower()

def final_reverse_engineer(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # 1. מיפוי מפתחות ראשיים (PK) מה-SQL (ALTER + CONSTRAINT)
        pk_map = {}
        pk_pattern = r'ALTER TABLE\s+(?:ONLY\s+)?(?:public\.)?"?(\w+)"?.*?PRIMARY KEY\s*\((.*?)\);'
        for table, cols in re.findall(pk_pattern, content, re.DOTALL | re.IGNORECASE):
            pk_map[table.upper()] = [clean_id(c) for c in cols.split(',')]

        # 2. מיפוי מפתחות זרים (FK)
        fk_list = []
        fk_pattern = r'ALTER TABLE\s+(?:ONLY\s+)?(?:public\.)?"?(\w+)"?.*?FOREIGN KEY\s*\((.*?)\)\s+REFERENCES\s+(?:public\.)?"?(\w+)"?\s*\((.*?)\)'
        for table, fcols, rtable, rcols in re.findall(fk_pattern, content, re.DOTALL | re.IGNORECASE):
            fk_list.append({
                "table": table.upper(),
                "fk_cols": [clean_id(c) for c in fcols.split(',')],
                "ref_table": rtable.upper(),
                "ref_cols": [clean_id(c) for c in rcols.split(',')]
            })

        # --- היקש לוגי של מפתחות חסרים ---
        for fk in fk_list:
            target_table = fk["ref_table"]
            target_cols = fk["ref_cols"]
            if target_table not in pk_map:
                pk_map[target_table] = target_cols
            else:
                for col in target_cols:
                    if col not in pk_map[target_table]:
                        pk_map[target_table].append(col)

        # 3. זיהוי מבנה הטבלאות
        table_blocks = re.findall(r'CREATE TABLE (?:public\.)?"?(\w+)"?\s*\((.*?)\);', content, re.DOTALL | re.IGNORECASE)

        print(f"\n=== FINAL REVERSE ENGINEERING REPORT FOR ERD: {file_path} ===")
        print("=" * 125)

        for table_name, columns_raw in table_blocks:
            t_upper = table_name.upper()
            
            # בדיקת PK פנימי בתוך הבלוק
            if t_upper not in pk_map:
                internal = re.search(r'"?(\w+)"?\s+[\w\(\)]+\s+PRIMARY KEY', columns_raw, re.IGNORECASE)
                if internal: pk_map[t_upper] = [internal.group(1).lower()]

            t_pks = pk_map.get(t_upper, [])
            t_fks = [f for f in fk_list if f["table"] == t_upper]

            # --- לוגיקה לסיווג צורות ב-ERD ---
            is_weak = False
            # אם אחד מה-FKs הוא גם חלק מה-PK -> ישות חלשה
            if t_pks:
                for fk in t_fks:
                    if any(col in t_pks for col in fk["fk_cols"]):
                        is_weak = True
                        break

            if is_weak:
                design_type = "WEAK ENTITY (Double Rectangle)"
            elif len(t_fks) >= 2:
                # טבלה שמקשרת בין ישויות ומהווה צומת (כמו ORDER)
                design_type = "ASSOCIATIVE ENTITY (Rectangle + Diamond)"
            elif "_" in t_upper:
                design_type = "MULTIVALUED ATTRIBUTE"
            else:
                design_type = "REGULAR ENTITY (Rectangle)"

            print(f"\n[TABLE]: {t_upper}")
            print(f"ERD SUGGESTION: {design_type}")
            print(f"{'Column Name':<25} | {'Classification':<45} | {'Cardinality Context'}")
            print("-" * 125)

            # פירוק עמודות
            col_lines = re.split(r',(?![^\(]*\))', columns_raw) 
            for line in col_lines:
                line = line.strip()
                if not line or any(k in line.upper() for k in ['CONSTRAINT', 'PRIMARY KEY', 'FOREIGN KEY', 'CHECK']):
                    continue
                
                col = clean_id(line.split()[0])
                labels = []
                context = "-"
                
                # האם PK?
                if col in t_pks:
                    labels.append("[PK] PRIMARY KEY")
                    context = "Identifying Attribute" if is_weak else "Identifier"
                
                # האם FK?
                for fk in t_fks:
                    if col in fk["fk_cols"]:
                        labels.append(f"[FK] -> {fk['ref_table']}")
                        context = "Many to 1 (N:1)"

                final_label = ", ".join(labels) if labels else "Regular Attribute"
                print(f"{col:<25} | {final_label:<45} | {context}")

            print("-" * 125)

    except Exception as e:
        print(f"Error during execution: {e}")

if __name__ == "__main__":
    # ודאי ששם הקובץ תואם לקובץ הגיבוי שלך
    final_reverse_engineer('BackupSara.sql')