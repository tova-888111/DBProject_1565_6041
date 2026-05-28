-- הצגה
SELECT 
    OrderId, 
    Price, 
    StoreID, 
    Status, 
    OrderDate -- העמודה שהטריגר תיקן בזמן אמת!
FROM "ORDER" 
WHERE OrderId = 100000;

--יצירת הטריגר
CREATE OR REPLACE FUNCTION set_order_date_fn()
RETURNS TRIGGER AS $$
/**
 * פונקציית טריגר עבור טבלת ORDER
 * תפקיד: אכיפת תאריך יצירה אמין ואוטומטי ברקע
 */
BEGIN
    -- דריסה ידנית של שדה תאריך ההזמנה והשמת הזמן הנוכחי המדויק של שרת ה-DB
    NEW.OrderDate := CURRENT_TIMESTAMP;
    
    -- החזרת הרשומה המעודכנת להמשך ביצוע פעולת ה-INSERT
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE TRIGGER trg_set_order_date
BEFORE INSERT ON "ORDER"
FOR EACH ROW -- יופעל עבור כל הזמנה חדשה שנוצרת
EXECUTE FUNCTION set_order_date_fn();

--נסיון הכנסה
INSERT INTO "ORDER" (OrderId, Price, StoreID, DriverID, OrderDate)
VALUES (100000, 250.00, 1, 1, '2020-01-01 10:00:00');

-- הצגה
SELECT 
    OrderId, 
    Price, 
    StoreID, 
    Status, 
    OrderDate -- העמודה שהטריגר תיקן בזמן אמת!
FROM "ORDER" 
WHERE OrderId = 100000;