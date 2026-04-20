-- =========================================================
-- Step 2 - Index.sql
-- יצירת 3 אינדקסים אסטרטגיים לשיפור ביצועי המערכת
-- המטרה: מעבר מ-Full Table Scan ל-Index Scan
-- =========================================================

-- ---------------------------------------------------------
-- 1. אינדקס על שם המוצר (PRODUCT.ProductName)
-- מוטיבציה: חיפוש מוצרים לפי שם הוא הפעולה הנפוצה ביותר בקופה ובניהול המלאי.
-- ---------------------------------------------------------

-- שאילתה לבדיקת זמן ריצה לפני (לצלם זמן לפני):
SELECT * FROM PRODUCT WHERE ProductName = 'Product 13111';

-- יצירת האינדקס:
CREATE INDEX idx_product_name ON PRODUCT(ProductName);

-- שאילתה לבדיקת זמן ריצה אחרי (לצלם זמן אחרי):
SELECT * FROM PRODUCT WHERE ProductName = 'Product 13111';


-- ---------------------------------------------------------
-- 2. אינדקס משולב על שם העובד (EMPLOYEE.FirstName, EMPLOYEE.LastName)
-- מוטיבציה: במערכת ניהול, חיפושי עובדים מתבצעים כמעט תמיד לפי השם המלא.
-- אינדקס משולב (Composite) מאפשר שליפה מהירה ומדויקת.
-- ---------------------------------------------------------

-- שאילתה לבדיקת זמן ריצה לפני:
SELECT * FROM EMPLOYEE WHERE FirstName = 'Roni' AND LastName = 'Dahan';

-- יצירת האינדקס:
CREATE INDEX idx_employee_full_name ON EMPLOYEE(FirstName, LastName);

-- שאילתה לבדיקת זמן ריצה אחרי:
SELECT * FROM EMPLOYEE WHERE FirstName = 'Roni' AND LastName = 'Dahan';


-- ---------------------------------------------------------
-- 3. אינדקס על תאריך תפוגה (PRODUCT.ExpirationDate)
-- מוטיבציה: עבור רשת כמו "רמי לוי", ניהול פגי תוקף הוא קריטי.
-- האינדקס משפר משמעותית שאילתות של טווחי תאריכים (BETWEEN).
-- ---------------------------------------------------------

-- שאילתה לבדיקת זמן ריצה לפני:
SELECT ProductID, ProductName, ExpirationDate 
FROM PRODUCT 
WHERE ExpirationDate BETWEEN DATE '2026-04-16' AND DATE '2026-05-16';

-- יצירת האינדקס:
CREATE INDEX idx_product_expiration ON PRODUCT(ExpirationDate);

-- שאילתה לבדיקת זמן ריצה אחרי:
SELECT ProductID, ProductName, ExpirationDate 
FROM PRODUCT 
WHERE ExpirationDate BETWEEN DATE '2026-04-16' AND DATE '2026-05-16';