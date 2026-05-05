from simple_ddl_parser import DDLParser
import json

def analyze_sql_backup(file_path):
    try:
        # 1. קריאת תוכן הקובץ
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        print(f"--- מנתח קובץ גיבוי: {file_path} ---")
        
        # 2. הרצת ה-Parser על תוכן הקובץ
        # ה-Parser מחלץ טבלאות, עמודות, מפתחות וקשרים
        parser = DDLParser(sql_content)
        result = parser.run(group_by_type=True)

        if not result.get('tables'):
            print("לא נמצאו פקודות CREATE TABLE בקובץ. וודאי שהקובץ הוא בפורמט Plain SQL.")
            return

        # 3. מעבר על התוצאות והדפסה בצורה שנוחה לשרטוט
        for table in result['tables']:
            table_name = table['table_name']
            print(f"\n[טבלה]: {table_name.upper()}")
            
            # הדפסת עמודות
            print("  עמודות:")
            for col in table['columns']:
                name = col['name']
                dtype = col['type']
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                is_pk = "(PK)" if col.get('primary_key') else ""
                print(f"    - {name:20} | {dtype:15} | {nullable} {is_pk}")

            # הדפסת מפתחות זרים (קשרים)
            # לעיתים הקשרים מוגדרים בתוך הטבלה ולעיתים ב-ALTER TABLE בנפרד
            constraints = table.get('constraints', {})
            fks = table.get('foreign_keys', [])
            
            if fks:
                print("  קשרים (Foreign Keys):")
                for fk in fks:
                    col = fk['columns'][0]
                    ref_table = fk['ref_table']
                    ref_col = fk['ref_columns'][0]
                    print(f"    -> העמודה '{col}' מקשרת לטבלה '{ref_table}' ({ref_col})")
            
            print("-" * 40)

    except Exception as e:
        print(f"שגיאה בניתוח הקובץ: {e}")

if __name__ == "__main__":
    # החליפי את השם לשם הקובץ הנקי שלך (אחרי ההמרה ל-Plain)
    file_to_analyze = 'clean_logistics_backup.sql' 
    analyze_engineer = analyze_sql_backup(file_to_analyze)