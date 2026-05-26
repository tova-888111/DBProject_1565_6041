import re

# פונקציה שמנקה שם של עמודה/טבלה:
# מסירה גרשיים כפולים, רווחים מיותרים
# ומחזירה באותיות קטנות
def clean_id(name):
    return name.replace('"', '').strip().lower()

# פונקציה ראשית שמבצעת Reverse Engineering לקובץ SQL
def final_reverse_engineer(file_path):
    try:
        # פתיחת קובץ ה-SQL לקריאה
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # =========================================================
        # 1. שליפת כל המפתחות הראשיים (PRIMARY KEY)
        # =========================================================

        # מילון:
        # שם טבלה -> רשימת עמודות שהן PK
        pk_map = {}

        # regex שמחפש פקודות ALTER TABLE עם PRIMARY KEY
        pk_pattern = r'ALTER TABLE\s+(?:ONLY\s+)?(?:public\.)?"?(\w+)"?.*?PRIMARY KEY\s*\((.*?)\);'

        # מעבר על כל ההתאמות שנמצאו
        for table, cols in re.findall(pk_pattern, content, re.DOTALL | re.IGNORECASE):

            # שמירת ה-PK במילון
            pk_map[table.upper()] = [clean_id(c) for c in cols.split(',')]

        # =========================================================
        # 2. שליפת כל המפתחות הזרים (FOREIGN KEY)
        # =========================================================

        # רשימה שתכיל את כל ה-FK
        fk_list = []

        # regex למציאת FOREIGN KEY
        fk_pattern = r'ALTER TABLE\s+(?:ONLY\s+)?(?:public\.)?"?(\w+)"?.*?FOREIGN KEY\s*\((.*?)\)\s+REFERENCES\s+(?:public\.)?"?(\w+)"?\s*\((.*?)\)'

        # מעבר על כל ההתאמות
        for table, fcols, rtable, rcols in re.findall(fk_pattern, content, re.DOTALL | re.IGNORECASE):

            # הוספת FK לרשימה
            fk_list.append({
                "table": table.upper(),  # הטבלה שמכילה את ה-FK
                "fk_cols": [clean_id(c) for c in fcols.split(',')],
                "ref_table": rtable.upper(),  # הטבלה שאליה מצביעים
                "ref_cols": [clean_id(c) for c in rcols.split(',')]
            })

        # =========================================================
        # 3. היקש לוגי של PK חסרים
        # =========================================================

        # לפעמים SQL לא מגדיר PK במפורש
        # אבל אם FK מצביע לעמודה מסוימת,
        # כנראה שהיא מפתח בטבלה היעד

        for fk in fk_list:

            target_table = fk["ref_table"]
            target_cols = fk["ref_cols"]

            # אם לטבלת היעד אין PK עדיין
            if target_table not in pk_map:
                pk_map[target_table] = target_cols

            # אחרת נוסיף עמודות חסרות
            else:
                for col in target_cols:
                    if col not in pk_map[target_table]:
                        pk_map[target_table].append(col)

        # =========================================================
        # 4. זיהוי כל הטבלאות מתוך CREATE TABLE
        # =========================================================

        table_blocks = re.findall(
            r'CREATE TABLE (?:public\.)?"?(\w+)"?\s*\((.*?)\);',
            content,
            re.DOTALL | re.IGNORECASE
        )

        # כותרת לדוח
        print(f"\n=== FINAL REVERSE ENGINEERING REPORT FOR ERD: {file_path} ===")
        print("=" * 125)

        # =========================================================
        # 5. מעבר על כל הטבלאות
        # =========================================================

        for table_name, columns_raw in table_blocks:

            t_upper = table_name.upper()

            # =====================================================
            # בדיקה האם יש PRIMARY KEY פנימי בתוך CREATE TABLE
            # =====================================================

            if t_upper not in pk_map:

                internal = re.search(
                    r'"?(\w+)"?\s+[\w\(\)]+\s+PRIMARY KEY',
                    columns_raw,
                    re.IGNORECASE
                )

                # אם נמצא PK פנימי
                if internal:
                    pk_map[t_upper] = [internal.group(1).lower()]

            # רשימת ה-PK של הטבלה
            t_pks = pk_map.get(t_upper, [])

            # כל ה-FK ששייכים לטבלה
            t_fks = [f for f in fk_list if f["table"] == t_upper]

            # =====================================================
            # 6. סיווג סוג הישות ב-ERD
            # =====================================================

            is_weak = False

            # אם FK הוא גם חלק מה-PK
            # זו ישות חלשה
            if t_pks:
                for fk in t_fks:
                    if any(col in t_pks for col in fk["fk_cols"]):
                        is_weak = True
                        break

            # קביעת סוג הישות
            if is_weak:
                design_type = "WEAK ENTITY (Double Rectangle)"

            # אם יש לפחות 2 FK
            # כנראה טבלת קישור
            elif len(t_fks) >= 2:
                design_type = "ASSOCIATIVE ENTITY (Rectangle + Diamond)"

            # אם יש underscore בשם
            # נניח שזה מאפיין רב ערכי
            elif "_" in t_upper:
                design_type = "MULTIVALUED ATTRIBUTE"

            # אחרת זו ישות רגילה
            else:
                design_type = "REGULAR ENTITY (Rectangle)"

            # =====================================================
            # הדפסת מידע על הטבלה
            # =====================================================

            print(f"\n[TABLE]: {t_upper}")
            print(f"ERD SUGGESTION: {design_type}")

            print(f"{'Column Name':<25} | {'Classification':<45} | {'Cardinality Context'}")
            print("-" * 125)

            # =====================================================
            # פירוק העמודות של הטבלה
            # =====================================================

            # פיצול לפי פסיקים
            # אבל לא בתוך סוגריים
            col_lines = re.split(r',(?![^\(]*\))', columns_raw)

            # מעבר על כל שורה
            for line in col_lines:

                line = line.strip()

                # דילוג על שורות לא רלוונטיות
                if not line or any(
                    k in line.upper()
                    for k in ['CONSTRAINT', 'PRIMARY KEY', 'FOREIGN KEY', 'CHECK']
                ):
                    continue

                # שם העמודה
                col = clean_id(line.split()[0])

                # רשימת תוויות לעמודה
                labels = []

                # ברירת מחדל לקשר
                context = "-"

                # =================================================
                # האם זו עמודת PRIMARY KEY
                # =================================================

                if col in t_pks:

                    labels.append("[PK] PRIMARY KEY")

                    # אם הטבלה חלשה
                    if is_weak:
                        context = "Identifying Attribute"
                    else:
                        context = "Identifier"

                # =================================================
                # האם זו עמודת FOREIGN KEY
                # =================================================

                for fk in t_fks:

                    if col in fk["fk_cols"]:

                        labels.append(f"[FK] -> {fk['ref_table']}")

                        # קשר רבים לאחד
                        context = "Many to 1 (N:1)"

                # אם אין תוויות מיוחדות
                if labels:
                    final_label = ", ".join(labels)
                else:
                    final_label = "Regular Attribute"

                # הדפסת המידע
                print(f"{col:<25} | {final_label:<45} | {context}")

            print("-" * 125)

    # טיפול בשגיאות
    except Exception as e:
        print(f"Error during execution: {e}")

# =============================================================
# נקודת התחלה של התוכנית
# =============================================================
if __name__ == "__main__":

    # ודאי ששם הקובץ תואם לקובץ הגיבוי שלך
    final_reverse_engineer('BackupSara.sql')