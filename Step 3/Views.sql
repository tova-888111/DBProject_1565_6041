-- =====================================================================
-- חלק ג' - מבטים ושאילתות (Views.sql)
-- =====================================================================

-- ---------------------------------------------------------------------
-- מבט 1: אגף קמעונאות וחנויות (האגף המקורי)
-- הסבר פשוט: מרכז את כל המידע הניהולי על החנויות - כמה עובדים יש, 
-- מה עלות השכר שלהן, וכמה מוצרים ופריטים נמצאים פיזית במלאי של כל סניף.
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW v_store_operational_summary AS
SELECT 
    s.StoreID AS store_id,                       -- המספר המזהה של החנות
    s.StoreName AS store_name,                   -- שם סניף החנות
    s.Region AS store_region,                    -- האזור הגיאוגרפי של הסניף
    s.Rating AS store_rating,                    -- דירוג החנות (1 עד 5)
    COUNT(DISTINCT e.EmployeeID) AS total_employees, -- כמות העובדים הפעילים בסניף
    COALESCE(SUM(e.Salary), 0) AS monthly_payroll, -- סך תקציב השכר החודשי של הסניף
    COUNT(DISTINCT i.ProductID) AS unique_products, -- מספר המוצרים השונים שיש לחנות במלאי
    COALESCE(SUM(i.Quantity), 0) AS total_items_stock -- סך כל הפריטים פיזית שנמצאים במחסן החנות
FROM STORE s
LEFT JOIN EMPLOYEE e ON s.StoreID = e.StoreID AND e.Status = 'Active'
LEFT JOIN INVENTORY i ON s.StoreID = i.StoreID
GROUP BY s.StoreID, s.StoreName, s.Region, s.Rating;

-- ---------------------------------------------------------------------
-- שאילתא 1 על מבט 1: איתור חנויות מצטיינות
-- הסבר: שולף חנויות מובילות שקיבלו את הציון המקסימלי (Rating 5) כדי לנתח את מאפייניהן.
-- ---------------------------------------------------------------------
SELECT 
    store_name,                                  -- שם סניף החנות ברשת
    store_region,                                -- האזור הגיאוגרפי שבו ממוקם הסניף
    store_rating,                                -- דירוג האיכות או שביעות הרצון של החנות
    monthly_payroll,                             -- סך תקציב השכר החודשי המשולם לעובדי הסניף
    total_items_stock                            -- כמות הפריטים הכוללת שנמצאת כרגע במלאי החנות
FROM v_store_operational_summary
WHERE store_rating >= 5
ORDER BY store_rating DESC;

-- ---------------------------------------------------------------------
-- שאילתא 2 על מבט 1: ניתוח גיאוגרפי אזורי
-- הסבר: מחשב את ממוצע הפריטים במלאי וסך תקציבי השכר המשולמים בכל אזור פעילות ברשת.
-- ---------------------------------------------------------------------
SELECT 
    store_region AS operational_region,          -- אזור הפעילות של הרשת (צפון, מרכז, דרום וכו')
    COUNT(store_id) AS total_stores,             -- מספר החנויות הפעילות באותו אזור
    ROUND(AVG(total_items_stock), 2) AS avg_stock_per_store, -- ממוצע הפריטים במלאי לחנות יחידה באזור
    SUM(monthly_payroll) AS regional_payroll_spend -- סך כל הוצאות השכר המשולמות באותו חבל ארץ
FROM v_store_operational_summary
WHERE store_region IS NOT NULL
GROUP BY store_region;


-- ---------------------------------------------------------------------
-- מבט 2: אגף לוגיסטיקה, הפצה ומשלוחים (האגף של שרה)
-- הסבר פשוט: עושה סדר בביצועים של חברות המשלוחים - כמה נהגים פעילים יש להן, 
-- מה נפח ההובלה המקסימלי של המשאיות שלהן, וכמה הזמנות וכסף הן שינעו בפועל.
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW v_delivery_performance_summary AS
SELECT 
    dc.DeliveryCieID AS company_id,              -- מזהה ייחודי של חברת המשלוחים
    dc.DeliveryCieName AS company_name,          -- שם חברת הלוגיסטיקה והמשלוחים
    dc.DeliveryCiePhoneNb AS company_phone,      -- טלפון ליצירת קשר עם החברה
    COUNT(DISTINCT t.DriverID) AS active_drivers, -- מספר הנהגים הפעילים שנוהגים כרגע בחברה
    COALESCE(SUM(t.Capacity), 0) AS fleet_capacity, -- קיבולת המשקל המקסימלית של כל צי המשאיות שלהם
    COUNT(DISTINCT o.OrderId) AS orders_handled,  -- סך כל ההזמנות שהחברה שינעה עבור הרשת
    COALESCE(SUM(o.Price), 0) AS revenue_handled -- השווי הכספי המצטבר של כל ההזמנות שבוצעו דרכה
FROM DELIVERYCOMPANY dc
LEFT JOIN TRUCK t ON dc.DeliveryCieID = t.DeliveryCieID AND t.Active = 1
LEFT JOIN "ORDER" o ON t.DriverID = o.DriverID
GROUP BY dc.DeliveryCieID, dc.DeliveryCieName, dc.DeliveryCiePhoneNb;

-- ---------------------------------------------------------------------
-- שאילתא 1 על מבט 2: דירוג פיננסי של חברות השילוח
-- הסבר: מוצא את חברות ההפצה הדומיננטיות ששינעו הזמנות בשווי כספי גבוה מאוד (מעל 10,000 ש"ח).
-- ---------------------------------------------------------------------
SELECT 
    company_name,                                -- שם חברת הלוגיסטיקה והמשלוחים
    active_drivers,                              -- מספר הנהגים הפעילים הרשומים בחברה
    orders_handled AS total_orders_shipped,      -- כמות ההזמנות הכוללת שהחברה שינעה עבורנו
    revenue_handled AS total_revenue_value        -- השווי הכספי המצטבר של כל המשלוחים שטופלו בחברה
FROM v_delivery_performance_summary
WHERE revenue_handled > 10000.00
ORDER BY revenue_handled DESC;

-- ---------------------------------------------------------------------
-- שאילתא 2 על מבט 2: ניתוח קיבולת ותשתית לוגיסטית
-- הסבר: מסנן חברות לפי גודל צי הרכב שלהן (קיבולת מעל 500) כדי לבדוק את יעילות הניצול שלהן.
-- ---------------------------------------------------------------------
SELECT 
    company_name AS supplier_name,               -- שם ספק השילוח החיצוני
    fleet_capacity AS total_fleet_capacity,      -- קיבולת הנפח/משקל המקסימלית של כל משאיות החברה יחד
    orders_handled AS active_orders,             -- מספר המשלוחים שבוצעו בפועל
    revenue_handled AS revenue_handled           -- נפח הפעילות הכספית שהופקד בידי אותה חברה
FROM v_delivery_performance_summary
WHERE fleet_capacity >= 500.00
ORDER BY revenue_handled DESC;


-- ---------------------------------------------------------------------
-- מבט 3: מבט אינטגרטיבי משולב (חיבור בין האגפים)
-- הסבר פשוט: מחבר בין שני האגפים ומציג את שרשרת האספקה המלאה - אילו מוצרים 
-- הוזמנו לכל חנות, מאיזה מחסן לוגיסטי הם מגיעים, ובאיזה מעבר ומדף מדויקים הם מאוחסנים.
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW v_integrated_supply_chain AS
SELECT 
    o.OrderId AS order_id,                       -- מספר מזהה של ההזמנה
    s.StoreName AS destination_store,            -- שם חנות היעד שאליה נוסע המשלוח
    p.ProductName AS item_name,                  -- שם המוצר שהוזמן
    p.Brand AS item_brand,                       -- המותג של המוצר
    c.Quantity AS ordered_quantity,              -- כמות היחידות שהוזמנו מהמוצר הזה
    o.OrderDate AS order_date,                   -- תאריך ושעת ביצוע ההזמנה
    w.WarehouseID AS warehouse_number,           -- מספר המחסן הלוגיסטי שממנו הסחורה יוצאת
    w.Region AS warehouse_region,                -- האזור הגיאוגרפי שבו נמצא המחסן
    l.AisleNb AS aisle_number,                   -- מספר המעבר הפיזי בתוך המחסן
    l.ShelfNb AS shelf_number                    -- מספר המדף המדויק בתוך אותו מעבר
FROM "ORDER" o
JOIN STORE s ON o.StoreID = s.StoreID
JOIN CONTAINS c ON o.OrderId = c.OrderId
JOIN PRODUCT p ON c.ProductID = p.ProductID
JOIN LOCATED l ON p.ProductID = l.ProductID
JOIN WAREHOUSE w ON l.WarehouseID = w.WarehouseID;

-- ---------------------------------------------------------------------
-- שאילתא 1 על מבט 3: הפקת רשימת ליקוט למחסנאים
-- הסבר: שולף את כל הפריטים שצריך לאסוף ממחסן מספר 59, ממוין לפי מעבר ומדף לעבודה מהירה.
-- ---------------------------------------------------------------------
SELECT 
    order_id AS target_order_id,                 -- מספר מזהה של ההזמנה שלשמה מלקטים את הסחורה
    destination_store,                           -- שם חנות היעד שאליה יישלח המשלוח בסוף
    item_name,                                   -- שם המוצר הספציפי שצריך לאסוף מהמדף
    ordered_quantity AS items_to_pick,           -- כמות היחידות המדויקת שחובה ללקט
    aisle_number,                                -- מספר המעבר הפיזי בתוך המחסן שבו נמצא המוצר
    shelf_number                                 -- מספר המדף המדויק בתוך המעבר
FROM v_integrated_supply_chain
WHERE warehouse_number = 59
ORDER BY aisle_number, shelf_number;

-- ---------------------------------------------------------------------
-- שאילתא 2 על מבט 3: סיכום תפוקת מחסנים לוגיסטיים
-- הסבר: מנתח את נפח הפעילות של המחסנים על ידי סיכום הפריטים שיצאו וכמות ההזמנות שנסגרו.
-- ---------------------------------------------------------------------
SELECT 
    warehouse_number,                            -- מציג את המספר המזהה הייחודי של המחסן הלוגיסטי
    SUM(ordered_quantity) AS total_items_sent,   -- מסכם את כל היחידות הפיזיות של המוצרים שנשלחו מהמחסן
    COUNT(DISTINCT order_id) AS total_orders_count -- סופר כמה הזמנות נפרדות ושונות טופלו ויצאו מהמחסן הזה
FROM v_integrated_supply_chain
GROUP BY warehouse_number
ORDER BY warehouse_number DESC;