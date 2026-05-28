CREATE OR REPLACE FUNCTION calculate_order_price(p_order_id INT)
RETURNS NUMERIC AS $$
/**
 * פרויקט בסיסי נתונים - שלב ד' - תכנות PL/pgSQL
 * פונקציה מספר 2: חישוב ועדכון עלות סופית של הזמנה כולל הנחות
 * * תיאור: הפונקציה מקבלת מזהה הזמנה, רצה בלולאה על כל פריטיה, בודקת הנחות
 * פעילות בהתאם לתאריך המקורי של ההזמנה, ומעדכנת את מחיר הנטו בטבלת האם.
 * * אלמנטים ממומשים: Explicit Cursor, Cursor Loop, RECORD, DML (UPDATE), 
 * Conditional Logic (IF), Exception Handling (כולל בדיקת סטאטוס סמן)
 */
DECLARE
    -- משתנים מקומיים לשמירת תאריך, סכומים ומונים
    v_order_date TIMESTAMP;
    v_total_price NUMERIC(10, 2) := 0.00;
    v_items_count INT := 0;

    -- [1] דרישה: הגדרת סמן מפורש (Explicit Cursor) לחיבור טבלת הקשר עם טבלת המוצרים
    cur_order_items CURSOR FOR 
        SELECT c.ProductID, c.Quantity, p.Price 
        FROM CONTAINS c
        JOIN PRODUCT p ON c.ProductID = p.ProductID
        WHERE c.OrderId = p_order_id;

    -- [2] דרישה: שימוש ברשומה (RECORD) דינמית לצורך מעבר על שורות הסמן
    r_item RECORD;
    v_discount_pct INT;
    v_item_final_price NUMERIC(10, 2);
BEGIN
    -- שליפת תאריך ההזמנה המקורית מטבלת האם
    SELECT OrderDate
    INTO v_order_date
    FROM "ORDER"
    WHERE OrderId = p_order_id;

    -- [3] דרישה: הסתעפות (Conditional Logic) - בדיקה אם ההזמנה בכלל קיימת בבסיס הנתונים
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

        -- שליפת אחוז ההנחה המקסימלי התקף עבור המוצר הספציפי ביום ביצוע ההזמנה
        SELECT COALESCE(MAX(d.DiscountPercentage), 0)
        INTO v_discount_pct
        FROM APPLIES_TO a
        JOIN DISCOUNT d ON a.DiscountID = d.DiscountID
        WHERE a.ProductID = r_item.ProductID
          AND v_order_date::DATE BETWEEN d.StartDate AND d.EndDate;

        -- חישוב מחיר הפריט לאחר שקלול אחוז ההנחה שחזר
        v_item_final_price := r_item.Price * (1 - (v_discount_pct / 100.0));

        -- הוספת העלות של השורה הנוכחית (מחיר לאחר הנחה X כמות שהוזמנה) לסך הכל הכולל
        v_total_price := v_total_price + (v_item_final_price * r_item.Quantity);
    END LOOP;

    -- [6] סגירת הסמן המפורש לשחרור משאבי מערכת
    CLOSE cur_order_items;

    -- בדיקה לוגית נוספת: חסימת מקרה של הזמנה "רפאים" ללא מוצרים משויכים
    IF v_items_count = 0 THEN
        RAISE EXCEPTION 'שגיאה: להזמנה מספר % אין מוצרים ולכן לא ניתן לחשב מחיר.', p_order_id;
    END IF;

    -- [7] דרישה: פקודת עדכון בסיס הנתונים (DML UPDATE) מתוך פונקציה
    UPDATE "ORDER"
    SET Price = v_total_price
    WHERE OrderId = p_order_id;

    -- הדפסת הודעת הצלחה מפורטת לחלונית ה-Messages לטובת מעקב (ולוגים בדו"ח)
    RAISE NOTICE 'החישוב הסתיים בהצלחה. המחיר הכולל המעודכן עבור הזמנה % הוא: %',
        p_order_id, v_total_price;

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
        RAISE NOTICE 'אירעה שגיאה בזמן חישוב העלות עבור הזמנה %: %',
            p_order_id, SQLERRM;

        -- גלגול השגיאה הלאה (Re-raise) כדי שהטרנזקציה תיכשל ולא יישמרו נתונים שגויים
        RAISE;
END;
$$ LANGUAGE plpgsql;


--הרצה
SELECT calculate_order_price(1);