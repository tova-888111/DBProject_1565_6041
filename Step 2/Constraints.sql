-- 1. אילוץ על מלאי: כמות במלאי לא יכולה להיות קטנה מ-0
ALTER TABLE INVENTORY 
ADD CONSTRAINT chk_inventory_qty CHECK (Quantity >= 0);

-- בדיקה 1: ניסיון להכניס מלאי שלילי
-- INSERT INTO INVENTORY (StoreID, ProductID, Quantity, MinimumStock) VALUES (1, 1, -5, 10);

-- 2. אילוץ על תאריכי הנחה: תאריך סיום חייב להיות אחרי תאריך התחלה
ALTER TABLE DISCOUNT 
ADD CONSTRAINT chk_discount_dates CHECK (EndDate >= StartDate);

-- בדיקה 2: ניסיון ליצור הנחה עם תאריכים הפוכים
-- INSERT INTO DISCOUNT (DiscountID, DiscountName, DiscountPercentage, StartDate, EndDate) 
-- VALUES (999, 'Test Error', 20, DATE '2026-12-31', DATE '2026-01-01');


-- 3. מחיר מוצר חייב להיות גדול מ-0

ALTER TABLE PRODUCT
ADD CONSTRAINT chk_product_price_positive
CHECK (Price > 0);


-- בדיקה : ניסיון להכניס מוצר עם מחיר שלילי--
-- INSERT INTO PRODUCT (ProductID, ProductName, Price, Kashrut, Brand, ExpirationDate, CategoryID)
-- VALUES (999999, 'Test Product', -10, 'Badatz', 'TestBrand', '2026-12-31', 1);