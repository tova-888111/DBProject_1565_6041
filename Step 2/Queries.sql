-- =========================================
-- Step 2 - Queries.sql
-- 8 SELECT queries
-- 4 pairs written in 2 different ways
-- In each pair, both queries return the same result
-- =========================================


-- =========================================================
-- SELECT 1A - Dashboard
-- מוצרים שנמצאים במלאי נמוך ברשת
-- דרך 1: JOIN רגיל
-- =========================================================
SELECT 
    p.ProductID,
    p.ProductName,
    s.StoreID,
    s.StoreName,
    i.Quantity,
    i.MinimumStock
FROM INVENTORY i
JOIN PRODUCT p ON i.ProductID = p.ProductID
JOIN STORE s ON i.StoreID = s.StoreID
WHERE i.Quantity < i.MinimumStock
ORDER BY p.ProductID, s.StoreID;


-- =========================================================
-- SELECT 1B - Dashboard
-- מוצרים שנמצאים במלאי נמוך ברשת
-- דרך 2: עם תת-שאילתה ב-IN
-- מחזירה בדיוק את אותן עמודות
-- =========================================================
SELECT 
    p.ProductID,
    p.ProductName,
    s.StoreID,
    s.StoreName,
    i.Quantity,
    i.MinimumStock
FROM INVENTORY i
JOIN PRODUCT p ON i.ProductID = p.ProductID
JOIN STORE s ON i.StoreID = s.StoreID
WHERE (i.StoreID, i.ProductID) IN
(
    SELECT StoreID, ProductID
    FROM INVENTORY
    WHERE Quantity < MinimumStock
)
ORDER BY p.ProductID, s.StoreID;


-- =========================================================
-- SELECT 2A - Inventory / Dashboard
-- מוצרים עם תפוגה קרובה בחודש הקרוב
-- דרך 1: תנאי ישיר
-- =========================================================
SELECT 
    p.ProductID,
    p.ProductName,
    c.CategoryName,
    p.Price,
    p.ExpirationDate
FROM PRODUCT p
JOIN CATEGORY c ON p.CategoryID = c.CategoryID
WHERE p.ExpirationDate BETWEEN DATE '2026-04-16' AND DATE '2026-05-16'
ORDER BY p.ExpirationDate, p.ProductID;


-- =========================================================
-- SELECT 2B - Inventory / Dashboard
-- מוצרים עם תפוגה קרובה בחודש הקרוב
-- דרך 2: IN
-- מחזירה בדיוק את אותן עמודות
-- =========================================================
SELECT 
    p.ProductID,
    p.ProductName,
    c.CategoryName,
    p.Price,
    p.ExpirationDate
FROM PRODUCT p
JOIN CATEGORY c ON p.CategoryID = c.CategoryID
WHERE p.ProductID IN
(
    SELECT ProductID
    FROM PRODUCT
    WHERE ExpirationDate BETWEEN DATE '2026-04-16' AND DATE '2026-05-16'
)
ORDER BY p.ExpirationDate, p.ProductID;


-- =========================================================
-- SELECT 3A - Suppliers screen
-- ספקים ומספר המוצרים שהם מספקים
-- דרך 1: GROUP BY
-- =========================================================
SELECT 
    s.SupplierID,
    s.SupplierName,
    s.Email,
    s.ContactPhone,
    COUNT(sb.ProductID) AS NumProductsSupplied
FROM SUPPLIER s
JOIN SUPPLIERED_BY sb ON s.SupplierID = sb.SupplierID
GROUP BY s.SupplierID, s.SupplierName, s.Email, s.ContactPhone
ORDER BY s.SupplierID;


-- =========================================================
-- SELECT 3B - Suppliers screen
-- ספקים ומספר המוצרים שהם מספקים
-- דרך 2: תת-שאילתה קורלטיבית
-- מחזירה בדיוק את אותן עמודות
-- =========================================================
SELECT 
    s.SupplierID,
    s.SupplierName,
    s.Email,
    s.ContactPhone,
    (
        SELECT COUNT(*)
        FROM SUPPLIERED_BY sb
        WHERE sb.SupplierID = s.SupplierID
    ) AS NumProductsSupplied
FROM SUPPLIER s
WHERE EXISTS
(
    SELECT 1
    FROM SUPPLIERED_BY sb
    WHERE sb.SupplierID = s.SupplierID
)
ORDER BY s.SupplierID;


-- =========================================================
-- SELECT 4A - Employees screen
-- עובדים פעילים בלבד עם שם הסניף
-- דרך 1: JOIN
-- =========================================================
SELECT 
    e.EmployeeID,
    e.FirstName,
    e.LastName,
    e.Role,
    e.Salary,
    s.StoreName
FROM EMPLOYEE e
JOIN STORE s ON e.StoreID = s.StoreID
WHERE e.Status = 'Active'
ORDER BY e.EmployeeID;


-- =========================================================
-- SELECT 4B - Employees screen
-- עובדים פעילים בלבד עם שם הסניף
-- דרך 2: EXISTS + תת-שאילתה לשם סניף
-- מחזירה בדיוק את אותן עמודות
-- =========================================================
SELECT 
    e.EmployeeID,
    e.FirstName,
    e.LastName,
    e.Role,
    e.Salary,
    (
        SELECT s.StoreName
        FROM STORE s
        WHERE s.StoreID = e.StoreID
    ) AS StoreName
FROM EMPLOYEE e
WHERE e.Status = 'Active'
  AND EXISTS
  (
      SELECT 1
      FROM STORE s
      WHERE s.StoreID = e.StoreID
  )
ORDER BY e.EmployeeID;


-- =========================================================
-- SELECT 5 - Detailed Branches Dashboard
-- פרטי סניפים מלאים: כתובת, מנהל, מלאי וכמות עובדים
-- =========================================================
SELECT 
    s.StoreID,
    s.StoreName,
    -- כתובת הסניף
    COALESCE(l.City || ', ' || l.Street || ' ' || l.StreetNumber::TEXT, 'No Address') AS StoreAddress,
    -- פרטי מנהל
    COALESCE(e_mgr.EmployeeID::TEXT, 'None') AS ManagerID,
    COALESCE(e_mgr.FirstName || ' ' || e_mgr.LastName, 'None') AS ManagerName,
    -- נתוני מלאי
    COUNT(DISTINCT i.ProductID) AS NumProductsInStore,
    SUM(CASE WHEN i.Quantity < i.MinimumStock THEN 1 ELSE 0 END) AS LowStockItems,
    -- מספר עובדים בסניף
    (SELECT COUNT(*) FROM EMPLOYEE e WHERE e.StoreID = s.StoreID) AS TotalEmployees
FROM STORE s
LEFT JOIN LOCATION l ON s.StoreID = l.StoreID
LEFT JOIN EMPLOYEE e_mgr ON s.StoreID = e_mgr.StoreID AND e_mgr.Role = 'Store Manager'
LEFT JOIN INVENTORY i ON s.StoreID = i.StoreID
GROUP BY 
    s.StoreID, 
    s.StoreName, 
    l.City, 
    l.Street, 
    l.StreetNumber,
    e_mgr.EmployeeID, 
    e_mgr.FirstName, 
    e_mgr.LastName
ORDER BY s.StoreID;


-- =========================================================
-- SELECT 6 - Inventory screen
-- מסך מלאי מפורט: מוצר, סניף, קטגוריה, כמות, מינימום, סטטוס
-- =========================================================
SELECT 
    p.ProductID,
    p.ProductName,
    s.StoreName,
    c.CategoryName,
    i.Quantity,
    i.MinimumStock,
    CASE
        WHEN i.Quantity = 0 THEN 'Out of Stock'
        WHEN i.Quantity < i.MinimumStock THEN 'Low Stock'
        ELSE 'In Stock'
    END AS StockStatus
FROM INVENTORY i
JOIN PRODUCT p ON i.ProductID = p.ProductID
JOIN STORE s ON i.StoreID = s.StoreID
JOIN CATEGORY c ON p.CategoryID = c.CategoryID
ORDER BY p.ProductID, s.StoreID;

-- =========================================================
-- SELECT 7 - Network Totals Dashboard
-- סכימה כללית של עובדים, מוצרים ומלאי חסר ברמת הרשת
-- =========================================================
SELECT 
    (SELECT COUNT(*) FROM EMPLOYEE) AS TotalEmployees,
    (SELECT COUNT(*) FROM PRODUCT) AS ProductTypes,
    (SELECT SUM(Quantity) FROM INVENTORY) AS OverallStock,
    (SELECT COUNT(*) FROM INVENTORY WHERE Quantity < MinimumStock) AS LowStockPoints
FROM (SELECT 1) AS dummy;


-- =========================================================
-- SELECT 8 - Discounts Management Screen
-- כל ההנחות שהוגדרו ברשת והמוצרים המשויכים אליהן
-- כולל פירוק תאריכים לימים, חודשים ושנים (לפי דרישות שלב ב')
-- =========================================================
SELECT 
    d.DiscountID,
    d.DiscountName,
    d.DiscountPercentage,
    p.ProductID,
    p.ProductName,
    -- פירוק תאריך התחלה לניהול נוח ב-GUI
    EXTRACT(DAY FROM d.StartDate) AS StartDay,
    EXTRACT(MONTH FROM d.StartDate) AS StartMonth,
    EXTRACT(YEAR FROM d.StartDate) AS StartYear,
    -- פירוק תאריך סיום לניהול נוח ב-GUI
    EXTRACT(DAY FROM d.EndDate) AS EndDay,
    EXTRACT(MONTH FROM d.EndDate) AS EndMonth,
    EXTRACT(YEAR FROM d.EndDate) AS EndYear
FROM DISCOUNT d
JOIN APPLIES_TO a ON d.DiscountID = a.DiscountID
JOIN PRODUCT p ON a.ProductID = p.ProductID
ORDER BY d.StartDate DESC, d.DiscountID;


-- =========================================================
-- UPDATE 1 - Employees screen
-- העלאת שכר ב-5% לכל הקופאיות הפעילות
-- פעולה כללית ומשמעותית יותר למסך ניהול עובדים
-- =========================================================
SELECT *
FROM EMPLOYEE
WHERE Role = 'Cashier'
  AND Status = 'Active'
ORDER BY EmployeeID;

UPDATE EMPLOYEE
SET Salary = ROUND(Salary * 1.05, 2)
WHERE Role = 'Cashier'
  AND Status = 'Active';

SELECT *
FROM EMPLOYEE
WHERE Role = 'Cashier'
  AND Status = 'Active'
ORDER BY EmployeeID;


-- =========================================================
-- UPDATE 2 - Branches screen
-- העלאת דירוג ב-1 לסניפים עם מעט פריטי מלאי נמוך
-- מתאים למסך ניהול סניפים
-- =========================================================
SELECT 
    s.StoreID,
    s.StoreName,
    s.Rating,
    SUM(CASE WHEN i.Quantity < i.MinimumStock THEN 1 ELSE 0 END) AS LowStockItems
FROM STORE s
LEFT JOIN INVENTORY i ON s.StoreID = i.StoreID
GROUP BY s.StoreID, s.StoreName, s.Rating
HAVING SUM(CASE WHEN i.Quantity < i.MinimumStock THEN 1 ELSE 0 END) <= 2
ORDER BY s.StoreID;

UPDATE STORE
SET Rating = LEAST(Rating + 1, 10)
WHERE StoreID IN
(
    SELECT s.StoreID
    FROM STORE s
    LEFT JOIN INVENTORY i ON s.StoreID = i.StoreID
    GROUP BY s.StoreID
    HAVING SUM(CASE WHEN i.Quantity < i.MinimumStock THEN 1 ELSE 0 END) <= 2
);

SELECT 
    s.StoreID,
    s.StoreName,
    s.Rating,
    SUM(CASE WHEN i.Quantity < i.MinimumStock THEN 1 ELSE 0 END) AS LowStockItems
FROM STORE s
LEFT JOIN INVENTORY i ON s.StoreID = i.StoreID
GROUP BY s.StoreID, s.StoreName, s.Rating
HAVING SUM(CASE WHEN i.Quantity < i.MinimumStock THEN 1 ELSE 0 END) <= 2
ORDER BY s.StoreID;


-- =========================================================
-- UPDATE 3 - Discounts screen
-- הגדלת אחוז ההנחה ב-5 לכל ההנחות הפעילות בתאריך 2026-04-16
-- שההנחה שלהן קטנה מ-20%
-- =========================================================
SELECT *
FROM DISCOUNT
WHERE DATE '2026-04-16' BETWEEN StartDate AND EndDate
  AND DiscountPercentage < 25
ORDER BY DiscountID;

UPDATE DISCOUNT
SET DiscountPercentage = DiscountPercentage + 5
WHERE DATE '2026-04-16' BETWEEN StartDate AND EndDate
  AND DiscountPercentage < 20;

SELECT *
FROM DISCOUNT
WHERE DATE '2026-04-16' BETWEEN StartDate AND EndDate
  AND DiscountPercentage < 25
ORDER BY DiscountID;


-- =========================================================
-- DELETE 1 - Inventory screen
-- מחיקת רשומה אחת מטבלת המלאי שמתאימה לזוג מפתחות ספציפים
-- =========================================================
SELECT 
    i.StoreID,
    i.ProductID,
    i.Quantity,
    p.ProductName,
    p.ExpirationDate
FROM INVENTORY i
JOIN PRODUCT p ON i.ProductID = p.ProductID
WHERE i.StoreID = 82
  AND i.ProductID = 82;

DELETE FROM INVENTORY
WHERE StoreID = 82
  AND ProductID = 82;

SELECT 
    i.StoreID,
    i.ProductID,
    i.Quantity,
    p.ProductName,
    p.ExpirationDate
FROM INVENTORY i
JOIN PRODUCT p ON i.ProductID = p.ProductID
WHERE i.StoreID = 82
  AND i.ProductID = 82;


-- =========================================================
-- DELETE 2 - Inventory screen
-- מחיקת רשומות מלאי של מוצר שאזל מהמלאי וגם פג תוקפו
-- מחיקה קטנה ומבוקרת יותר
-- =========================================================
SELECT 
    i.StoreID,
    i.ProductID,
    i.Quantity,
    p.ProductName,
    p.ExpirationDate
FROM INVENTORY i
JOIN PRODUCT p ON i.ProductID = p.ProductID
WHERE i.Quantity = 0
  AND p.ExpirationDate < DATE '2026-04-16'
ORDER BY i.StoreID, i.ProductID;

DELETE FROM INVENTORY
WHERE (StoreID, ProductID) IN
(
    SELECT i.StoreID, i.ProductID
    FROM INVENTORY i
    JOIN PRODUCT p ON i.ProductID = p.ProductID
    WHERE i.Quantity = 0
      AND p.ExpirationDate < DATE '2026-04-16'
    ORDER BY i.StoreID, i.ProductID
);

SELECT 
    i.StoreID,
    i.ProductID,
    i.Quantity,
    p.ProductName,
    p.ExpirationDate
FROM INVENTORY i
JOIN PRODUCT p ON i.ProductID = p.ProductID
WHERE i.Quantity = 0
  AND p.ExpirationDate < DATE '2026-04-16'
ORDER BY i.StoreID, i.ProductID;


-- =========================================================
-- DELETE 3 - Employees screen
-- מחיקת עובדים לא פעילים עם שכר בין 9000 ל-10000
-- =========================================================

SELECT *
FROM EMPLOYEE
WHERE Status = 'Inactive'
  AND Salary BETWEEN 9000 AND 10000
ORDER BY EmployeeID;

DELETE FROM EMPLOYEE
WHERE EmployeeID IN
(
    SELECT EmployeeID
    FROM EMPLOYEE
    WHERE Status = 'Inactive'
      AND Salary BETWEEN 9000 AND 10000
    ORDER BY EmployeeID
);

SELECT *
FROM EMPLOYEE
WHERE Status = 'Inactive'
  AND Salary BETWEEN 9000 AND 10000
ORDER BY EmployeeID;