CREATE OR REPLACE FUNCTION get_active_discounts(check_date DATE)
RETURNS refcursor AS $$
/**
 * פרויקט בסיסי נתונים - שלב ד' - תכנות PL/pgSQL
 * פונקציה מספר 1: שליפת הנחות פעילות עבור תאריך נתון
 * * תיאור: הפונקציה מקבלת תאריך ומחזירה Ref Cursor המכיל את כל ההנחות
 * הפעילות באותו יום, כולל שמות המוצרים עליהם הן חלות.
 * * אלמנטים ממומשים: Ref Cursor, Exception Handling, Conditional Logic (IF)
 */
DECLARE
    -- דרישה: הגדרת סמן משתנה (Ref Cursor) שיחזור לתוכנית הראשית
    discount_cursor refcursor := 'discount_result_cursor';
BEGIN
    -- [1] דרישה: הסתעפות (Conditional Branching) ובדיקת תקינות קלט (Validation)
    IF check_date IS NULL THEN
        -- דרישה: שימוש ב-Exception מונע למקרה של ערך ריק
        RAISE EXCEPTION 'שגיאה במערכת: לא ניתן לבצע בדיקה ללא הזנת תאריך תקין';
    END IF;

    -- הדפסת לוג פנימי למעקב (עוזר מאוד להוכחות ריצה בדו"ח)
    RAISE NOTICE 'מריץ בדיקת הנחות פעילות עבור התאריך: %', check_date;

    -- [2] דרישה: פתיחת ה-Cursor (Explicit Cursor Opening) עבור שאילתה מורכבת
    OPEN discount_cursor FOR
        SELECT d.DiscountID,
               d.DiscountName, 
               d.DiscountPercentage,
               p.ProductID, 
               p.ProductName, 
               d.StartDate, 
               d.EndDate
        FROM DISCOUNT d
        JOIN APPLIES_TO a ON d.DiscountID = a.DiscountID
        JOIN PRODUCT p ON p.ProductID = a.ProductID
        WHERE check_date BETWEEN d.StartDate AND d.EndDate;

    -- [3] החזרת הסמן הפתוח לתוכנית הראשי שמזמנת את הפונקציה
    RETURN discount_cursor;

EXCEPTION
    -- [4] דרישה: מנגנון טיפול בשגיאות (Exception Handling Block)
    WHEN OTHERS THEN
        -- תפיסת כל סוגי השגיאות הבלתי צפויות והדפסת הודעה מפורטת
        RAISE NOTICE 'אירעה שגיאה בלתי צפויה בפונקציית ההנחות: %', SQLERRM;
        RETURN NULL;
END;
$$ LANGUAGE plpgsql;




--איך נפעיל?
-- קוד לבדיקת הפונקציה בחלונית ה-SQL שלכם (עבור הדו"ח)
BEGIN; -- חובה לפתוח טרנזקציה כשעובדים עם Cursor
SELECT get_active_discounts('2026-05-28'); -- מפעיל את הפונקציה ומאתחל את הסמן
FETCH ALL IN "discount_result_cursor"; -- שולף את הנתונים מתוך הסמן ומציג אותם בטבלה

--בנפרד
COMMIT;