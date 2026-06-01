CREATE OR REPLACE FUNCTION calculate_order_price(p_order_id INT, p_wholesale_percentage NUMERIC)
RETURNS NUMERIC AS $$
/**
 * פרויקט בסיסי נתונים - שלב ד' - תכנות PL/pgSQL
 * פונקציה מספר 2: חישוב ועדכון עלות הזמנת רכש מספק לפי אחוז סיטונאי
 * * תיאור: הפונקציה מקבלת מזהה הזמנה ואחוז עלות מהמחירון (רכש מספק).
 * היא מחשבת את סך ההזמנה ישירות ממחירי המוצרים הנוכחיים ומעדכנת את טבלת ORDER.
 * * אלמנטים ממומשים: Explicit Cursor, Cursor Loop, RECORD, DML (UPDATE), 
 * Conditional Logic (IF), Exception Handling (כולל בדיקת סטאטוס סמן)
 */
DECLARE
    -- משתנים מקומיים לשמירת סכומים ומונים
    v_total_price NUMERIC(10, 2) := 0.00;
    v_items_count INT := 0;
    v_order_exists INT;

    -- [1] דרישה: הגדרת סמן מפורש (Explicit Cursor) לחיבור טבלת הקשר עם טבלת המוצרים
    cur_order_items CURSOR FOR 
        SELECT c.ProductID, c.Quantity, p.Price 
        FROM CONTAINS c
        JOIN PRODUCT p ON c.ProductID = p.ProductID
        WHERE c.OrderId = p_order_id;

    -- [2] דרישה: שימוש ברשומה (RECORD) דינמית לצורך מעבר על שורות הסמן
    r_item RECORD;
    v_item_wholesale_price NUMERIC(10, 2);
BEGIN
    -- [3] דרישה: הסתעפות ובדיקת תקינות קלט (Validation) על אחוז הסיטונאות
    IF p_wholesale_percentage IS NULL OR p_wholesale_percentage <= 0 OR p_wholesale_percentage > 100 THEN
        RAISE EXCEPTION 'שגיאה: אחוז עלות סיטונאית חייב להיות בין 1 ל-100.';
    END IF;

    -- בדיקה ישירה אם ההזמנה קיימת במערכת
    SELECT 1 INTO v_order_exists FROM "ORDER" WHERE OrderId = p_order_id;
    
    IF NOT FOUND THEN
        -- דרישה: זריקת חריגה מבוקרת (RAISE EXCEPTION)
        RAISE EXCEPTION 'שגיאה: הזמנה מספר % לא קיימת במערכת.', p_order_id;
    END IF;

    -- [4] דרישה: פתיחה ידנית של הסמן המפורש (Opening Explicit Cursor)
    OPEN cur_order_items;

    -- [5] דרישה: שימוש בלולאה (Loop) לעיבוד שורה-אחרי-שורה
    LOOP
        -- שליפת הרשומה הנוכחית מהסמן לתוך משתנה הרשומה
        FETCH cur_order_items INTO r_item;
        EXIT WHEN NOT FOUND; -- תנאי יציאה מהלולאה כאשר נגמרים המוצרים בהזמנה

        -- קידום מונה הפריטים בהזמנה
        v_items_count := v_items_count + 1;

        -- חישוב מחיר הפריט הסיטונאי (מחיר החנות * אחוז הסיטונאות)
        v_item_wholesale_price := r_item.Price * (p_wholesale_percentage / 100.0);

        -- הוספת העלות של השורה הנוכחית (מחיר סיטונאי X כמות שהוזמנה) לסך הכל הכולל
        v_total_price := v_total_price + (v_item_wholesale_price * r_item.Quantity);
    END LOOP;

    -- [6] סגירת הסמן המפורש לשחרור משאבי מערכת
    CLOSE cur_order_items;

    -- בדיקה לוגית נוספת: חסימת מקרה של הזמנה ללא מוצרים משויכים
    IF v_items_count = 0 THEN
        RAISE EXCEPTION 'שגיאה: להזמנה מספר % אין מוצרים ולכן לא ניתן לחשב מחיר.', p_order_id;
    END IF;

    -- [7] דרישה: פקודת עדכון בסיס הנתונים (DML UPDATE) מתוך פונקציה
    UPDATE "ORDER"
    SET Price = v_total_price
    WHERE OrderId = p_order_id;

    -- הדפסת הודעת הצלחה מפורטת לחלונית ה-Messages לטובת מעקב (ולוגים בדו"ח)
    RAISE NOTICE 'חישוב עלות רכש מספק הסתיים. אחוז סיטונאי: % אחוז, מחיר מעודכן להזמנה % הוא: %',
        p_wholesale_percentage, p_order_id, v_total_price;

    -- החזרת המחיר הסופי שחושב לתוכנית הקוראת
    RETURN v_total_price;

EXCEPTION
    -- [8] דרישה: בלוק טיפול בחריגות ושגיאות (Exception Handling)
    WHEN OTHERS THEN
        -- מנגנון הגנה: בדיקה אם הסמן נשאר פתוח עקב השגיאה, וסגירתו במידת הצורך
        IF cur_order_items%ISOPEN THEN
            CLOSE cur_order_items;
        END IF;

        -- הדפסת לוג שגיאה מפורט עם תיאור הבעיה המדויק מהשרת (SQLERRM)
        RAISE NOTICE 'אירעה שגיאה בזמן חישוב עלות רכש עבור הזמנה %: %',
            p_order_id, SQLERRM;

        -- גלגול השגיאה הלאה (Re-raise)
        RAISE;
END;
$$ LANGUAGE plpgsql;


--הרצה
SELECT calculate_order_price(1, 65.00);