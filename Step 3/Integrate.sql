-- יצירת ענף חדש
CREATE SCHEMA sara_branch;


-- ====================================================================
-- שלב 1: עדכון מבני והתאמת טבלאות קיימות בסכמת PUBLIC
-- ====================================================================

-- 1. הוספת עמודות כתובת ואתר לטבלת STORE הקיימת ב-public
ALTER TABLE public.STORE 
    ADD COLUMN IF NOT EXISTS websiteurl TEXT,
    ADD COLUMN IF NOT EXISTS Address TEXT,
    ADD COLUMN IF NOT EXISTS Region VARCHAR(50);

-- 2. גיבוי ומעבר נתוני הכתובות מטבלת LOCATION הישנה לתוך טבלת STORE החדשה
UPDATE public.STORE s
SET Address = l.Street || ' ' || l.StreetNumber || ', ' || l.City,
    Region = l.Region
FROM public.LOCATION l
WHERE s.StoreID = l.StoreID;

-- 3. הגדרת עמודות הכתובת החדשות כ-NOT NULL לאחר שהן אוכלסו בנתונים
ALTER TABLE public.STORE 
    ALTER COLUMN Address SET NOT NULL,
    ALTER COLUMN Region SET NOT NULL;

-- 4. מחיקת טבלת LOCATION הישנה (כבר אין בה צורך, הנתונים בתוך STORE)
DROP TABLE IF EXISTS public.LOCATION CASCADE;

-- 5. התאמת טבלת PRODUCT ב-public (הסרת כשרות והוספת תאריך ייצור)
ALTER TABLE public.PRODUCT 
    DROP COLUMN IF EXISTS Kashrut,
    ADD COLUMN IF NOT EXISTS dateofmanufacture DATE;


-- ====================================================================
-- שלב 2: יצירת הטבלאות החדשות בסכמת PUBLIC (לפי המבנה הסופי)
-- ====================================================================

CREATE TABLE IF NOT EXISTS public.WAREHOUSE
(
  WarehouseID INT NOT NULL,
  Region VARCHAR(50) NOT NULL,
  Address TEXT NOT NULL,
  PRIMARY KEY (WarehouseID)
);

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

CREATE TABLE IF NOT EXISTS public.PRODUCT_KASHRUT
(
  ProductID INT NOT NULL,
  Kashrut VARCHAR(50) NOT NULL,
  PRIMARY KEY (Kashrut, ProductID),
  FOREIGN KEY (ProductID) REFERENCES public.PRODUCT(ProductID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS public.WAREHOUSE_WAREHOUSEMANAGER
(
  WarehouseID INT NOT NULL,
  WarehouseManager VARCHAR(100) NOT NULL,
  PRIMARY KEY (WarehouseManager, WarehouseID),
  FOREIGN KEY (WarehouseID) REFERENCES public.WAREHOUSE(WarehouseID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS public.DELIVERYCOMPAGNY_REGIONSERVED
(
  DeliveryCieID INT NOT NULL,
  RegionServed VARCHAR(50) NOT NULL,
  PRIMARY KEY (RegionServed, DeliveryCieID),
  FOREIGN KEY (DeliveryCieID) REFERENCES public.DELIVERYCOMPAGNY(DeliveryCieID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS public.CONTAINS
(
  OrderId INT NOT NULL,
  ProductID INT NOT NULL,
  Quantity INT NOT NULL DEFAULT 1 CHECK (Quantity > 0),
  PRIMARY KEY (OrderId, ProductID),
  FOREIGN KEY (OrderId) REFERENCES public."ORDER"(OrderId) ON DELETE CASCADE,
  FOREIGN KEY (ProductID) REFERENCES public.PRODUCT(ProductID)
);

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
-- שלב 3: מיזוג נתונים ופתרון התנגשויות מ-SARA_BRANCH ל-PUBLIC
-- ====================================================================

-- 1. מיזוג נתוני החנויות של שרה (מעדכן את האתר, שומר על הכתובת הקיימת בציבורי במקרה של כפל)
INSERT INTO public.STORE (StoreID, StoreName, Phone, StoreEmail, Rating, websiteurl, Address, Region)
SELECT StoreID, StoreName, Phone, 'info@store.com', COALESCE(Rating, 5), WebSiteUrl, 'Unknown Address', 'Unknown Region'
FROM sara_branch.STORE
ON CONFLICT (StoreID) DO UPDATE 
SET websiteurl = EXCLUDED.websiteurl;

-- 2. מיזוג נתוני מוצרים (מעדכן תאריך ייצור למוצרים קיימים, יוצר קשר דיפולטיבי לקטגוריה 1 למוצרים חדשים)
INSERT INTO public.PRODUCT (ProductID, ProductName, Price, Brand, ExpirationDate, dateofmanufacture, CategoryID)
SELECT ProductID, ProductName, Price, 'General', ExpirationDate, DateOfManufacture, 1 
FROM sara_branch.PRODUCT
ON CONFLICT (ProductID) DO UPDATE 
SET dateofmanufacture = EXCLUDED.dateofmanufacture;

-- 3. העתקת ישויות לוגיסטיקה עצמאיות
INSERT INTO public.WAREHOUSE SELECT * FROM sara_branch.WAREHOUSE ON CONFLICT (WarehouseID) DO NOTHING;
INSERT INTO public.DELIVERYCOMPAGNY SELECT * FROM sara_branch.DELIVERYCOMPAGNY ON CONFLICT (DeliveryCieID) DO NOTHING;
INSERT INTO public.TRUCK SELECT * FROM sara_branch.TRUCK ON CONFLICT (DriverID) DO NOTHING;
INSERT INTO public."ORDER" SELECT * FROM sara_branch."ORDER" ON CONFLICT (OrderId) DO NOTHING;

-- 4. העתקת טבלאות קשר ותתי-ישויות
INSERT INTO public.PRODUCT_KASHRUT SELECT * FROM sara_branch.PRODUCT_KASHRUT ON CONFLICT (Kashrut, ProductID) DO NOTHING;
INSERT INTO public.WAREHOUSE_WAREHOUSEMANAGER SELECT * FROM sara_branch.WAREHOUSE_WAREHOUSEMANAGER ON CONFLICT (WarehouseManager, WarehouseID) DO NOTHING;
INSERT INTO public.DELIVERYCOMPAGNY_REGIONSERVED SELECT * FROM sara_branch.DELIVERYCOMPAGNY_REGIONSERVED ON CONFLICT (RegionServed, DeliveryCieID) DO NOTHING;
INSERT INTO public.CONTAINS SELECT * FROM sara_branch.CONTAINS ON CONFLICT (OrderId, ProductID) DO NOTHING;
INSERT INTO public.LOCATED SELECT * FROM sara_branch.LOCATED ON CONFLICT (ProductID, WarehouseID) DO NOTHING;


-- ====================================================================
-- שלב 4: מיזוג טבלת המלאי (INVENTORY)
-- ====================================================================
-- מכיוון שבמלאי של שרה לא הוגדר StoreID, הנתונים מוזרמים כאן לחנות מספר 1 כברירת מחדל.
-- במידה והמוצר כבר רשום במלאי של חנות 1, הכמויות יסוכמו יחד באופן אוטומטי.

INSERT INTO public.INVENTORY (StoreID, ProductID, Quantity, MinimumStock)
SELECT 1, ProductID, Quantity, MinimumStock 
FROM sara_branch.INVENTORY
ON CONFLICT (StoreID, ProductID) DO UPDATE 
SET Quantity = public.INVENTORY.Quantity + EXCLUDED.Quantity,
    MinimumStock = GREATEST(public.INVENTORY.MinimumStock, EXCLUDED.MinimumStock);

