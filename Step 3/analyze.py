import re

def final_reverse_engineer(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # 1. חיפוש כל פקודות ה-ALTER TABLE שמוסיפות מפתחות
        # מחפש מפתחות ראשיים
        pk_matches = re.findall(r'ALTER TABLE ONLY (?:public\.)?"?(\w+)"?.*?PRIMARY KEY \("?(\w+)"?\);', content, re.DOTALL | re.IGNORECASE)
        pk_map = {t.upper(): c.lower() for t, c in pk_matches}

        # מחפש מפתחות זרים
        fk_matches = re.findall(r'ALTER TABLE ONLY (?:public\.)?"?(\w+)"?.*?FOREIGN KEY \("?(\w+)"?\)\s+REFERENCES (?:public\.)?"?(\w+)"?\("?(\w+)"?\)', content, re.DOTALL | re.IGNORECASE)
        
        # 2. מציאת מבנה הטבלאות
        table_blocks = re.findall(r'CREATE TABLE (?:public\.)?"?(\w+)"?\s*\((.*?)\);', content, re.DOTALL | re.IGNORECASE)

        print(f"\n=== FINAL STRUCTURAL ANALYSIS REPORT: {file_path} ===")
        print("=" * 100)

        for table_name, columns_raw in table_blocks:
            t_upper = table_name.upper()
            
            # זיהוי קשרים עבור הטבלה הנוכחית
            table_fks = [f for f in fk_matches if f[0].upper() == t_upper]
            
            # החלטה על סוג הישות (Algorithm logic)
            if "_" in t_upper:
                design_type = "MULTIVALUED ATTRIBUTE / WEAK ENTITY"
            elif len(table_fks) >= 2:
                design_type = "RELATIONSHIP (Diamond in ERD)"
            else:
                design_type = "ENTITY (Rectangle in ERD)"

            print(f"\n[TABLE]: {t_upper}")
            print(f"DESIGN TYPE: {design_type}")
            print(f"{'Column Name':<25} | {'Key Classification'}")
            print("-" * 100)

            # פירוק העמודות
            columns = [c.strip().split()[0].replace('"', '').lower() for c in columns_raw.split(',\n') if c.strip()]
            
            for col in columns:
                if col in ['constraint', 'primary', 'foreign']: continue
                
                key_label = "Regular Attribute"
                
                # האם זה PK?
                if pk_map.get(t_upper) == col:
                    key_label = "[PK] PRIMARY KEY (Underline in ERD)"
                
                # האם זה FK?
                for _, f_col, r_table, r_col in table_fks:
                    if f_col.lower() == col:
                        key_label = f"[FK] FOREIGN KEY -> Refers to {r_table.upper()}({r_col})"
                
                print(f"{col:<25} | {key_label}")

            print("-" * 100)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    final_reverse_engineer('BackupSara.sql')