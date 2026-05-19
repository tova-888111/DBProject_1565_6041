-- יצירת ענף חדש
CREATE SCHEMA sara_branch;


-- ====================================================================
-- שלב 1: עדכון מבני של טבלאות קיימות בסכמת PUBLIC
-- ====================================================================

-- 1. עדכון טבלת STORE ב-public (הוספת עמודת אתר ושינוי אורך טלפון במידת הצורך)
ALTER TABLE public.STORE 
    ADD COLUMN IF NOT EXISTS websiteurl TEXT,
    ALTER COLUMN Phone TYPE VARCHAR(20);

-- 2. עדכון טבלת PRODUCT ב-public (הסרת כשרות כי היא עוברת לטבלה נפרדת, והוספת תאריך ייצור)
ALTER TABLE public.PRODUCT 
    DROP COLUMN IF EXISTS Kashrut,
    ADD COLUMN IF NOT EXISTS dateofmanufacture DATE;


-- ====================================================================
-- שלב 2: יצירת הטבלאות החדשות בסכמת PUBLIC
-- ====================================================================

-- 1. יצירת טבלת מחסנים
CREATE TABLE IF NOT EXISTS public.WAREHOUSE
(
  WarehouseID INT NOT NULL,
  Region VARCHAR(50) NOT NULL,
  Address TEXT NOT NULL,
  PRIMARY KEY (WarehouseID)
);

-- 2. יצירת טבלת חברות משלוחים
CREATE TABLE IF NOT EXISTS public.DELIVERYCOMPAGNY
(
  DeliveryCieID INT NOT NULL,
  DeliveryCieName VARCHAR(100) NOT NULL,
  DeliveryCiePhoneNb VARCHAR(20) NOT NULL,
  Email VARCHAR(100) NOT NULL CHECK (Email LIKE '%@%'),
  PRIMARY KEY (DeliveryCieID),
  UNIQUE (DeliveryCieName),
  UNIQUE (DeliveryCiePhoneNb)
);

-- 3. יצירת טבלת משאיות
CREATE TABLE IF NOT EXISTS public.TRUCK
(
  DriverID INT NOT NULL,
  Active SMALLINT NOT NULL DEFAULT 1 CHECK (Active IN (0, 1)), 
  Capacity NUMERIC(10,2) NOT NULL CHECK (Capacity > 0),
  LicensePlate VARCHAR(20) NOT NULL,
  MaintenanceStatus VARCHAR(50) DEFAULT 'Good',
  DeliveryCieID INT NOT NULL,
  PRIMARY KEY (DriverID),
  FOREIGN KEY (DeliveryCieID) REFERENCES public.DELIVERYCOMPAGNY(DeliveryCieID),
  UNIQUE (LicensePlate)
);

-- 4. יצירת טבלת הזמנות
CREATE TABLE IF NOT EXISTS public."ORDER"
(
  OrderId INT NOT NULL,
  Price DECIMAL(10,2) NOT NULL CHECK (Price >= 0),
  DeliveryDate TIMESTAMP,
  OrderDate TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  StoreID INT NOT NULL,
  DriverID INT NOT NULL,
  PRIMARY KEY (OrderId),
  FOREIGN KEY (StoreID) REFERENCES public.STORE(StoreID),
  FOREIGN KEY (DriverID) REFERENCES public.TRUCK(DriverID)
);

-- 5. טבלת כשרות מוצר (קשר מרובה למוצר)
CREATE TABLE IF NOT EXISTS public.PRODUCT_KASHRUT
(
  ProductID INT NOT NULL,
  Kashrut VARCHAR(50) NOT NULL,
  PRIMARY KEY (Kashrut, ProductID),
  FOREIGN KEY (ProductID) REFERENCES public.PRODUCT(ProductID) ON DELETE CASCADE
);

-- 6. טבלת מנהלי מחסנים
CREATE TABLE IF NOT EXISTS public.WAREHOUSE_WAREHOUSEMANAGER
(
  WarehouseID INT NOT NULL,
  WarehouseManager VARCHAR(100) NOT NULL,
  PRIMARY KEY (WarehouseManager, WarehouseID),
  FOREIGN KEY (WarehouseID) REFERENCES public.WAREHOUSE(WarehouseID) ON DELETE CASCADE
);

-- 7. טבלת אזורי שירות של חברות משלוחים
CREATE TABLE IF NOT EXISTS public.DELIVERYCOMPAGNY_REGIONSERVED
(
  DeliveryCieID INT NOT NULL,
  RegionServed VARCHAR(50) NOT NULL,
  PRIMARY KEY (RegionServed, DeliveryCieID),
  FOREIGN KEY (DeliveryCieID) REFERENCES public.DELIVERYCOMPAGNY(DeliveryCieID) ON DELETE CASCADE
);

-- 8. טבלת תכולת הזמנה (קשר מרובה בין מוצרים להזמנות)
CREATE TABLE IF NOT EXISTS public.CONTAINS
(
  OrderId INT NOT NULL,
  ProductID INT NOT NULL,
  Quantity INT NOT NULL DEFAULT 1 CHECK (Quantity > 0),
  PRIMARY KEY (OrderId, ProductID),
  FOREIGN KEY (OrderId) REFERENCES public."ORDER"(OrderId) ON DELETE CASCADE,
  FOREIGN KEY (ProductID) REFERENCES public.PRODUCT(ProductID)
);

-- 9. טבלת מיקום מוצרים במחסן
CREATE TABLE IF NOT EXISTS public.LOCATED
(
  ProductID INT NOT NULL,
  WarehouseID INT NOT NULL,
  AisleNb INT NOT NULL CHECK (AisleNb > 0),
  ShelfNb INT NOT NULL CHECK (ShelfNb > 0),
  PRIMARY KEY (ProductID, WarehouseID),
  FOREIGN KEY (ProductID) REFERENCES public.PRODUCT(ProductID),
  FOREIGN KEY (WarehouseID) REFERENCES public.WAREHOUSE(WarehouseID)
);


-- ====================================================================
-- שלב 3: העתקת ומיזוג הנתונים מ-SARA_BRANCH ל-PUBLIC (מניעת כפילויות)
-- ====================================================================

-- 1. מיזוג נתוני חנויות (מעדכן את אתר האינטרנט לחנויות קיימות, מוסיף חנויות חדשות)
INSERT INTO public.STORE (StoreID, StoreName, Phone, StoreEmail, Rating, websiteurl)
SELECT StoreID, StoreName, Phone, 'info@store.com', COALESCE(Rating, 5), WebSiteUrl 
FROM sara_branch.STORE
ON CONFLICT (StoreID) DO UPDATE 
SET websiteurl = EXCLUDED.websiteurl,
    Phone = EXCLUDED.Phone;

-- 2. מיזוג נתוני מוצרים (מעדכן תאריך ייצור למוצרים קיימים, מוסיף חדשים עם קטגוריית ברירת מחדל 1)
INSERT INTO public.PRODUCT (ProductID, ProductName, Price, Brand, ExpirationDate, dateofmanufacture, CategoryID)
SELECT ProductID, ProductName, Price, 'General', ExpirationDate, DateOfManufacture, 1 
FROM sara_branch.PRODUCT
ON CONFLICT (ProductID) DO UPDATE 
SET dateofmanufacture = EXCLUDED.dateofmanufacture,
    Price = EXCLUDED.Price;

-- 3. העתקת מחסנים
INSERT INTO public.WAREHOUSE 
SELECT WarehouseID, Region, Address FROM sara_branch.WAREHOUSE 
ON CONFLICT (WarehouseID) DO NOTHING;

-- 4. העתקת חברות משלוחים
INSERT INTO public.DELIVERYCOMPAGNY 
SELECT DeliveryCieID, DeliveryCieName, DeliveryCiePhoneNb, Email FROM sara_branch.DELIVERYCOMPAGNY 
ON CONFLICT (DeliveryCieID) DO NOTHING;

-- 5. העתקת משאיות/נהגים
INSERT INTO public.TRUCK 
SELECT DriverID, Active, Capacity, LicensePlate, MaintenanceStatus, DeliveryCieID FROM sara_branch.TRUCK 
ON CONFLICT (DriverID) DO NOTHING;

-- 6. העתקת הזמנות
INSERT INTO public."ORDER" 
SELECT OrderId, Price, DeliveryDate, OrderDate, StoreID, DriverID FROM sara_branch."ORDER" 
ON CONFLICT (OrderId) DO NOTHING;

-- 7. העתקת טבלאות קשר ישיר ותתי-ישויות
INSERT INTO public.PRODUCT_KASHRUT 
SELECT ProductID, Kashrut FROM sara_branch.PRODUCT_KASHRUT 
ON CONFLICT (Kashrut, ProductID) DO NOTHING;

INSERT INTO public.WAREHOUSE_WAREHOUSEMANAGER 
SELECT WarehouseID, WarehouseManager FROM sara_branch.WAREHOUSE_WAREHOUSEMANAGER 
ON CONFLICT (WarehouseManager, WarehouseID) DO NOTHING;

INSERT INTO public.DELIVERYCOMPAGNY_REGIONSERVED 
SELECT DeliveryCieID, RegionServed FROM sara_branch.DELIVERYCOMPAGNY_REGIONSERVED 
ON CONFLICT (RegionServed, DeliveryCieID) DO NOTHING;

INSERT INTO public.CONTAINS 
SELECT OrderId, ProductID, Quantity FROM sara_branch.CONTAINS 
ON CONFLICT (OrderId, ProductID) DO NOTHING;

INSERT INTO public.LOCATED 
SELECT ProductID, WarehouseID, AisleNb, ShelfNb FROM sara_branch.LOCATED 
ON CONFLICT (ProductID, WarehouseID) DO NOTHING;


-- ====================================================================
-- שלב 4: מיזוג מיוחד לטבלת המלאי (INVENTORY)
-- ====================================================================
-- בגלל שב-sara_branch לא היה StoreID, הנתונים משוייכים כאן כברירת מחדל לחנות מספר 1.
-- במידה והמוצר כבר קיים במלאי של החנות, הכמויות יחוברו יחד פלוס עדכון רמת המלאי המינימלי.

INSERT INTO public.INVENTORY (StoreID, ProductID, Quantity, MinimumStock)
SELECT 1, ProductID, Quantity, MinimumStock 
FROM sara_branch.INVENTORY
ON CONFLICT (StoreID, ProductID) DO UPDATE 
SET Quantity = public.INVENTORY.Quantity + EXCLUDED.Quantity,
    MinimumStock = GREATEST(public.INVENTORY.MinimumStock, EXCLUDED.MinimumStock);

