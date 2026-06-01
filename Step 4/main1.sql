DO $$
/**
 * פרויקט בסיסי נתונים - שלב ד' - תוכנית ראשית מספר 1
 * תיאור: שילוב תהליכים שיווקיים ותפעוליים - החלת הנחות פחת על מוצרים 
 * קרובים לתפוגה והדפסת דוח הנחות אקטיביות להיום.
 * אלמנטים ממומשים: זימון פרוצדורה (CALL), זימון פונקציה המחזירה Ref Cursor,
 * פתיחת טרנזקציה פנימית, לולאת Fetch, רשומת Record, והדפסות לוג.
 */
DECLARE
    -- הגדרת משתנה לקליטת ה-Ref Cursor שחוזר מהפונקציה
    v_discount_rc refcursor;
    
    -- הגדרת רשומה (RECORD) זמנית לצורך מעבר על תוצאות הסמן המוחזר
    r_discount_row RECORD;
BEGIN
    RAISE NOTICE '=== תחילת ריצת תוכנית ראשית 1: עדכון פחת והצגת מבצעים ===';

    -- [א] זימון פרוצדורה מספר 1: החלת 15% הנחה על מוצרים הפגים בעוד 45 ימים
    RAISE NOTICE '--- שלב 1: מפעיל פרוצדורת הנחת מוצרים קרובים לתפוגה ---';
    CALL discount_near_expiration_products(45, 15.00);

    -- [ב] זימון פונקציה מספר 1: שליפת סמן ההנחות הפעילות לתאריך הנוכחי
    RAISE NOTICE '--- שלב 2: מפעיל פונקציה לשליפת הנחות אקטיביות להיום ---';
    v_discount_rc := get_active_discounts(CURRENT_DATE);

    -- מעבר בלולאה על ה-Ref Cursor שחזר מהפונקציה והדפסת הפריטים
    RAISE NOTICE '--- שלב 3: פירוט ההנחות והמוצרים מתוך הסמן המוחזר ---';
    LOOP
        -- שליפת השורה הבאה מתוך ה-Ref Cursor לתוך הרשומה
        FETCH NEXT FROM v_discount_rc INTO r_discount_row;
        -- תנאי יציאה: כאשר נגמרו השורות בסמן
        EXIT WHEN NOT FOUND;

        -- התיקון כאן: הדפסה תקינה ללא כפל אחוזים + שילוב ה-IDs החדשים שהוספנו לפונקציה
        RAISE NOTICE 'מבצע מספר %: "%" (% אחוז הנחה) תקף על מוצר %: "%" [טווח: % עד %]',
            r_discount_row.DiscountID,
            r_discount_row.DiscountName,
            r_discount_row.DiscountPercentage,
            r_discount_row.ProductID,
            r_discount_row.ProductName,
            r_discount_row.StartDate,
            r_discount_row.EndDate;
    END LOOP;

    -- סגירת הסמן המוחזר לשחרור משאבי מערכת
    CLOSE v_discount_rc;

    RAISE NOTICE '=== תוכנית ראשית 1 הסתיימה בהצלחה ===';
END $$;