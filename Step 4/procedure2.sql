
--שאילתא שמציגה נתונים על הזמנה מספר 1
SELECT 
    o.OrderId,
    o.Status AS Order_Status, -- הנה עמודת הסטטוס שהוספנו!
    i.StoreID, 
    i.ProductID, 
    c.Quantity AS Ordered_Quantity, 
    i.Quantity AS Current_Stock_In_Store
FROM INVENTORY i
JOIN CONTAINS c ON i.ProductID = c.ProductID
JOIN "ORDER" o ON c.OrderId = o.OrderId -- חיבור לטבלת ההזמנות בשביל הסטטוס
WHERE o.OrderId = 1 
  AND i.StoreID = o.StoreID;


--הפרוצדורה
CREATE OR REPLACE PROCEDURE complete_order_and_update_stock(p_order_id INT)
LANGUAGE plpgsql
AS $$
/**
 * פרויקט בסיסי נתונים - שלב ד' - תכנות PL/pgSQL
 * פרוצדורה מספר 3: השלמת הזמנה ועדכון מלאי החנות (INVENTORY)
 * * מטרה: לסמן הזמנה כ-COMPLETED ולהוסיף את כמויות המוצרים שהגיעו
 * אל המלאי הקיים של החנות הספציפית שביצעה את ההזמנה.
 */
DECLARE
    v_current_status VARCHAR(20);
    v_store_id INT;     -- מזהה החנות המשויכת לטבלת ההזמנה
    r_item RECORD;      -- רשומה זמנית עבור לולאת המוצרים
BEGIN
    -- 1. שליפת הסטטוס הנוכחי ומזהה החנות מתוך טבלת האם של ההזמנה
    SELECT Status, StoreID 
    INTO v_current_status, v_store_id 
    FROM "ORDER" 
    WHERE OrderId = p_order_id;

    -- בדיקה א': הגנה למקרה שההזמנה לא קיימת
    IF NOT FOUND THEN
        RAISE EXCEPTION 'שגיאה: הזמנה מספר % לא קיימת במערכת.', p_order_id;
    END IF;

    -- בדיקה ב': מניעת הרצה כפולה - האם ההזמנה כבר טופלה ונקלטה בעבר?
    IF v_current_status = 'COMPLETED' THEN
        RAISE EXCEPTION 'שגיאה: הזמנה מספר % כבר סומנה כ-COMPLETED. המלאי בחנות כבר עודכן.', p_order_id;
    END IF;

    -- 2. עדכון הסטטוס של ההזמנה ל-'COMPLETED'
    UPDATE "ORDER"
    SET Status = 'COMPLETED'
    WHERE OrderId = p_order_id;

    RAISE NOTICE 'סטטוס ההזמנה % עודכן בהצלחה ל-COMPLETED.', p_order_id;

    -- 3. שימוש ב-Implicit Cursor לריצה על כל המוצרים והכמויות שנמצאים בתוך ההזמנה הזו
    FOR r_item IN 
        SELECT ProductID, Quantity 
        FROM CONTAINS 
        WHERE OrderId = p_order_id
    LOOP
        -- 4. עדכון המלאי בטבלת INVENTORY - הוספת (פלוס) הכמות שהגיעה למלאי החנות
        UPDATE INVENTORY
        SET Quantity = Quantity + r_item.Quantity
        WHERE StoreID = v_store_id AND ProductID = r_item.ProductID;

        -- במידה והמוצר עדיין לא היה קיים בכלל במלאי של החנות הזו (בטיפול חריגות מקומי), נכניס שורה חדשה
        IF NOT FOUND THEN
            INSERT INTO INVENTORY (StoreID, ProductID, Quantity, MinimumStock)
            VALUES (v_store_id, r_item.ProductID, r_item.Quantity, 10); -- 10 כמלאי מינימלי ברירת מחדל
            RAISE NOTICE 'מוצר % לא היה קיים במלאי חנות % - נוצרה רשומה חדשה עם כמות %.', 
                r_item.ProductID, v_store_id, r_item.Quantity;
        ELSE
            RAISE NOTICE 'המלאי עבור מוצר % בחנות % עודכן והועלה ב-% יחידות.', 
                r_item.ProductID, v_store_id, r_item.Quantity;
        END IF;
    END LOOP;

    RAISE NOTICE 'תהליך קליטת המשלוח ועדכון המלאי עבור הזמנה % הסתיים בהצלחה.', p_order_id;

EXCEPTION
    -- בלוק טיפול בשגיאות כלליות
    WHEN OTHERS THEN
        RAISE NOTICE 'אירעה שגיאה בתהליך השלמת ההזמנה %: %', p_order_id, SQLERRM;
        RAISE;
END;
$$;

-- קריאה 
CALL complete_order_and_update_stock(1);


--שאילתא שמציגה נתונים על הזמנה מספר 1
SELECT 
    o.OrderId,
    o.Status AS Order_Status, -- הנה עמודת הסטטוס שהוספנו!
    i.StoreID, 
    i.ProductID, 
    c.Quantity AS Ordered_Quantity, 
    i.Quantity AS Current_Stock_In_Store
FROM INVENTORY i
JOIN CONTAINS c ON i.ProductID = c.ProductID
JOIN "ORDER" o ON c.OrderId = o.OrderId -- חיבור לטבלת ההזמנות בשביל הסטטוס
WHERE o.OrderId = 1 
  AND i.StoreID = o.StoreID;