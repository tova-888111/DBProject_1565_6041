--לבדיקת הטבלה
SELECT ProductName, Price, ExpirationDate
FROM PRODUCT
WHERE ExpirationDate::DATE BETWEEN CURRENT_DATE AND CURRENT_DATE + 30;

--הפרוצדורה- מורידה באחוזים מחיר של מוצרים שתוקפם עומד לפוג
CREATE OR REPLACE PROCEDURE discount_near_expiration_products(
    p_days_ahead INT,
    p_discount_percent NUMERIC
)
LANGUAGE plpgsql
AS $$
/**
 * פרויקט בסיסי נתונים - שלב ד' - תכנות PL/pgSQL
 * פרוצדורה מספר 2: הורדת מחיר למוצרים שתאריך התפוגה שלהם קרוב
 * * מטרה: לאתר באופן דינמי מוצרים שעומדים לפוג בקרוב ולהחיל עליהם הנחת פחת במחיר.
 * * אלמנטים ממומשים: Implicit Cursor (סמן משתמע), FOR LOOP (לולאת סמן), 
 * RECORD (רשומה), IF (הסתעפות לוגית), UPDATE (פקודת DML), Exception Handling (טיפול בשגיאות).
 */
DECLARE
    -- [1] דרישה: שימוש ברשומה (RECORD) זמנית לקליטת נתוני השורות בתוך הלולאה
    r_product RECORD;
    v_new_price NUMERIC(10,2);
    v_counter INT := 0; -- מונה לספירת כמות המוצרים שעודכנו בפועל
BEGIN
    -- [2] דרישה: מבנה תנאי (IF) - ולידציה על קלט תקין של טווח הימים
    IF p_days_ahead IS NULL OR p_days_ahead < 0 THEN
        -- זריקת שגיאה מבוקרת במידה והפרמטר שלילי או ריק
        RAISE EXCEPTION 'שגיאה: מספר הימים חייב להיות חיובי';
    END IF;

    -- [3] דרישה: מבנה תנאי (IF) - ולידציה על תקינות אחוז ההנחה (חייב להיות בין 0 ל-100)
    IF p_discount_percent IS NULL OR p_discount_percent <= 0 OR p_discount_percent >= 100 THEN
        RAISE EXCEPTION 'שגיאה: אחוז ההנחה חייב להיות בין 0 ל-100';
    END IF;

    -- [4] דרישה: שימוש ב-Implicit Cursor (סמן משתמע) מובנה בתוך לולאת FOR
    -- הסמן שולף את המוצרים שתאריך התפוגה שלהם נופל בטווח הימים המבוקש החל מהיום
    FOR r_product IN
        SELECT ProductID, ProductName, Price, ExpirationDate
        FROM PRODUCT
        WHERE ExpirationDate::DATE BETWEEN CURRENT_DATE 
                                      AND CURRENT_DATE + p_days_ahead
    LOOP
        -- חישוב המחיר החדש לאחר הפחתת אחוז ההנחה שקיבלנו כפרמטר
        v_new_price := r_product.Price * (1 - p_discount_percent / 100.0);

        -- [5] דרישה: ביצוע פקודת DML (UPDATE) - עדכון המחיר החדש ישירות בטבלת המוצרים
        UPDATE PRODUCT
        SET Price = v_new_price
        WHERE ProductID = r_product.ProductID;

        -- קידום מונה העדכונים
        v_counter := v_counter + 1;

        -- הדפסת הודעת פירוט (Log) לחלונית ה-Messages עבור כל מוצר שעודכן
        RAISE NOTICE 'המוצר % עומד לפוג בתאריך %, המחיר עודכן מ-% ל-%',
            r_product.ProductName,
            r_product.ExpirationDate,
            r_product.Price,
            v_new_price;
    END LOOP;

    -- בדיקה מסכמת: הדפסת פלט מותאם לפי תוצאות הרצת הלולאה
    IF v_counter = 0 THEN
        RAISE NOTICE 'לא נמצאו מוצרים שתוקפם פג בטווח של % ימים.', p_days_ahead;
    ELSE
        RAISE NOTICE 'הפרוצדורה הסתיימה. עודכנו % מוצרים.', v_counter;
    END IF;

EXCEPTION
    -- [6] דרישה: בלוק טיפול בחריגות ושגיאות (Exception Handling)
    WHEN OTHERS THEN
        -- הדפסת הודעת שגיאה מפורטת לחלונית ה-Messages עם תיאור השגיאה המקורי מהשרת (SQLERRM)
        RAISE NOTICE 'אירעה שגיאה בפרוצדורת הנחת מוצרים קרובים לתפוגה: %', SQLERRM;
        -- גלגול השגיאה (Re-raise) כדי לבצע ביטול (Rollback) אוטומטי של הטרנזקציה במידת הצורך
        RAISE;
END;
$$;




-- הרצה
CALL discount_near_expiration_products(30, 10);

--לבדיקת הטבלה
SELECT ProductName, Price, ExpirationDate
FROM PRODUCT
WHERE ExpirationDate::DATE BETWEEN CURRENT_DATE AND CURRENT_DATE + 30;