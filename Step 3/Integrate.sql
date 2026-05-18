-- יצירת ענף חדש
CREATE SCHEMA sara_branch;


------------ שלב 1: התאמת מבנה הטבלאות הקיימות ב-PUBLIC ------------

-- 1. עדכון טבלת STORE ב-public (הוספת העמודה של שרה ושינוי הגדרות)
ALTER TABLE public.STORE ADD COLUMN IF NOT EXISTS websiteurl TEXT;
ALTER TABLE public.STORE ALTER COLUMN Phone TYPE VARCHAR(20); -- התאמה לאורך של שרה
ALTER TABLE public.STORE ALTER COLUMN StoreEmail DROP NOT NULL; -- מאחר ולשרה אין אימיילים לחנויות

-- 2. עדכון טבלת PRODUCT ב-public (הוספת תאריך ייצור)
ALTER TABLE public.PRODUCT ADD COLUMN IF NOT EXISTS dateofmanufacture DATE;

-- 3. עדכון טבלת INVENTORY ב-public (הפיכת StoreID ל-Nullable לצורך קליטת המלאי הכללי של שרה)
ALTER TABLE public.INVENTORY ALTER COLUMN StoreID DROP NOT NULL;


------------ שלב 2: יצירת הטבלאות החדשות ב-PUBLIC (אלו שהיו רק אצל שרה) ------------

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

CREATE TABLE IF NOT EXISTS public.CONTAINS
(
  OrderId INT NOT NULL,
  ProductID INT NOT NULL,
  Quantity INT NOT NULL DEFAULT 1 CHECK (Quantity > 0),
  PRIMARY KEY (OrderId, ProductID),
  FOREIGN KEY (OrderId) REFERENCES public."ORDER"(OrderId) ON DELETE CASCADE,
  FOREIGN KEY (ProductID) REFERENCES public.PRODUCT(ProductID)
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


------------ שלב 3: מיזוג והזרקת הנתונים מ-SARA_BRANCH ל-PUBLIC ------------

-- 1. מיזוג חנויות: אם החנות קיימת ב-public, נעדכן לה את ה-websiteurl וה-rating של שרה. אם לא, נכניס אותה.
INSERT INTO public.STORE (StoreID, StoreName, Phone, StoreEmail, Rating, websiteurl)
SELECT 
    s.StoreID, 
    s.StoreName, 
    s.Phone, 
    'unknown@ramilevi.co.il', -- אימייל דיפולטיבי לחנויות של שרה מאחר והשדה ב-public הוא NOT NOT
    COALESCE(s.Rating, 3),    -- אם אין דירוג, נשים 3 כברירת מחדל
    s.WebSiteUrl
FROM sara_branch.STORE s
ON CONFLICT (StoreID) DO UPDATE 
SET websiteurl = EXCLUDED.websiteurl,
    Rating = EXCLUDED.Rating;

-- 2. מיזוג מוצרים: אם המוצר קיים, נעדכן לו את תאריך הייצור של שרה. אם לא קיים, נכניס כמוצר חדש (עם ערכי ברירת מחדל לעמודות החסרות של שרה).
INSERT INTO public.PRODUCT (ProductID, ProductName, Price, Brand, ExpirationDate, dateofmanufacture, CategoryID)
SELECT 
    p.ProductID, 
    p.ProductName, 
    p.Price, 
    'Generic', -- מותג דיפולטיבי למוצרים של שרה שחסר להם השדה הזה
    p.ExpirationDate, 
    p.DateOfManufacture,
    1 -- משייך זמנית לקטגוריה מספר 1. ודאי שקיימת אצלך לפחות קטגוריה אחת בטבלת CATEGORY ב-public!
FROM sara_branch.PRODUCT p
ON CONFLICT (ProductID) DO UPDATE 
SET dateofmanufacture = EXCLUDED.dateofmanufacture;

-- 3. העברת חברות משלוחים
INSERT INTO public.DELIVERYCOMPAGNY SELECT * FROM sara_branch.deliverycompagny ON CONFLICT DO NOTHING;

-- 4. העברת אזורי שירות של חברות המשלוחים
INSERT INTO public.DELIVERYCOMPAGNY_REGIONSERVED SELECT * FROM sara_branch.deliverycompagny_regionserved ON CONFLICT DO NOTHING;

-- 5. העברת משאיות/נהגים
INSERT INTO public.TRUCK SELECT * FROM sara_branch.truck ON CONFLICT DO NOTHING;

-- 6. העברת מחסנים
INSERT INTO public.WAREHOUSE SELECT * FROM sara_branch.warehouse ON CONFLICT DO NOTHING;

-- 7. העברת מנהלי מחסנים
INSERT INTO public.WAREHOUSE_WAREHOUSEMANAGER SELECT * FROM sara_branch.warehouse_warehousemanager ON CONFLICT DO NOTHING;

-- 8. העברת מיקומי מוצרים במחסנים
INSERT INTO public.LOCATED SELECT * FROM sara_branch.located ON CONFLICT DO NOTHING;

-- 9. העברת כשרות מוצרים
INSERT INTO public.PRODUCT_KASHRUT SELECT * FROM sara_branch.product_kashrut ON CONFLICT DO NOTHING;

-- 10. העברת הזמנות (מבוצע אחרי שחברות המשלוחים והחנויות כבר עודכנו)
INSERT INTO public."ORDER" SELECT * FROM sara_branch."ORDER" ON CONFLICT DO NOTHING;

-- 11. העברת תכולת הזמנות
INSERT INTO public.CONTAINS SELECT * FROM sara_branch.contains ON CONFLICT DO NOTHING;

-- 12. מיזוג טבלת מלאי: מאחר ובטבלה של שרה אין StoreID, נכניס את המלאי שלה עם StoreID כ-NULL (מלאי מרכזי/לא משויך)
INSERT INTO public.INVENTORY (StoreID, ProductID, Quantity, MinimumStock)
SELECT 
    NULL, -- מלאי כללי מהאגף של שרה שאינו משויך לסניף ספציפי
    i.ProductID, 
    i.Quantity, 
    i.MinimumStock
FROM sara_branch.inventory i
ON CONFLICT (StoreID, ProductID) DO UPDATE 
SET Quantity = public.INVENTORY.Quantity + EXCLUDED.Quantity; -- אם הצירוף קיים, נסכום את המלאים


------------ שלב 4: בדיקת תקינות מהירה (אופציונלי) ------------
-- את יכולה להריץ את השורות האלו כדי לוודא שהטבלאות ב-public אכן התמלאו:
-- SELECT COUNT(*) FROM public."ORDER";
-- SELECT COUNT(*) FROM public.WAREHOUSE;
-- SELECT COUNT(*) FROM public.PRODUCT_KASHRUT;

