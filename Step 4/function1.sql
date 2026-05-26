CREATE OR REPLACE FUNCTION get_active_discounts(check_date DATE)
RETURNS refcursor AS $$
DECLARE
    -- הגדרת ה-Cursor שיחזור
    discount_cursor refcursor := 'discount_result_cursor';
BEGIN
    -- בדיקת תקינות: אם לא הוכנס תאריך, נזרוק חריגה (Exception)
    IF check_date IS NULL THEN
        RAISE EXCEPTION 'שגיאה: יש להזין תאריך תקין לבדיקה';
    END IF;

    -- פתיחת ה-Cursor עבור השאילתה המבוקשת
    OPEN discount_cursor FOR
        SELECT d.DiscountName, d.DiscountPercentage, p.ProductName, d.StartDate, d.EndDate
        FROM DISCOUNT d
        JOIN APPLIES_TO a ON d.DiscountID = a.DiscountID
        JOIN PRODUCT p ON p.ProductID = a.ProductID
        WHERE check_date BETWEEN d.StartDate AND d.EndDate;

    -- החזרת הסמן לתוכנית הראשית
    RETURN discount_cursor;

EXCEPTION
    -- טיפול בחריגות (Exceptions)
    WHEN OTHERS THEN
        RAISE NOTICE 'אירעה שגיאה בפונקציית ההנחות: %', SQLERRM;
        RETURN NULL;
END;
$$ LANGUAGE plpgsql;