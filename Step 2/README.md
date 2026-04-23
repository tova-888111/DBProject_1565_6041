# 🛒 דוח פרויקט: ניהול רשת "רמי לוי" - שלב ב' 
## שאילתות ואילוצים

בשלב זה ביצענו תשאול מתקדם של בסיס הנתונים, תוך שימוש בשאילתות מורכבות, עדכונים, מחיקות, אילוצים ואינדקסים.  
המטרה הייתה להפיק מידע משמעותי מהנתונים, לשפר ביצועים ולהתאים את בסיס הנתונים לצרכי המערכת והמסכים שהוגדרו.

---

## 🔍 שאילתות SELECT

בשלב זה נכתבו 8 שאילתות SELECT ברמת מורכבות גבוהה, הכוללות חיבורים בין מספר טבלאות, שימוש בפונקציות אגרגציה, תתי־שאילתות ושדות תאריכים.
4 השאילתות הראשונות נכתבו ב2 גרסאות.

### 🔁 SELECT 1 – מוצרים במלאי נמוך
שאילתה זו מציגה מוצרים שכמותם נמוכה מהמינימום הנדרש.  
המידע משמש את לוח הבקרה לצורך זיהוי מחסור במלאי וקבלת החלטות על הזמנה מחדש.
שאילתה זו נכתבה ב2 גרסאות.

**גרסה 1:**

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

![הרצת גרסה 1](images/selectQuery1_1.png)

**גרסה 2:**

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

![הרצת גרסה 2](images/selectQuery1_2.png)

**ניתוח יעילות:**
* **הבדל:** גרסה 1א מבצעת סינון ישיר תוך כדי חיבור הטבלאות. גרסה 1ב מבצעת JOIN לטבלת המלאי, ואז ב-`WHERE` מריצה תת-שאילתה שסורקת **שוב** את אותה טבלת מלאי כדי להחזיר רשימת מפתחות שכבר אותרו בחיבור המקורי.
* **מה יותר יעיל?** גרסה 1א.
* **מדוע?** גרסה 1ב מאלצת את המנוע לבצע סריקה חוזרת ומיותרת של טבלת ה-`INVENTORY`. גרסה 1א מסננת את הנתונים בסריקה אחת בלבד ("On-the-fly"), מה שחוסך משאבי זיכרון וזמן עיבוד יקר.

---

### 🔁 SELECT 2 – מוצרים עם תפוגה קרובה
שאילתה זו מציגה מוצרים שתוקפם יפוג במהלך החודש הקרוב.  
המידע מאפשר לרשת להיערך למבצעים או לפינוי מוצרים לפני פקיעת תוקף.
שאילתה זו נכתבה ב2 גרסאות.

**גרסה 1:**

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

![הרצת גרסה 1](images/selectQuery2_1.png)

**גרסה 2:**

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

![הרצת גרסה 2](images/selectQuery2_2.png)

**ניתוח יעילות:**
* **הבדל:** גרסה 2א ניגשת לטבלת המוצרים פעם אחת ומסננת. גרסה 2ב מבצעת JOIN לטבלת המוצרים כדי לשלוף את הנתונים להצגה, ובנוסף מריצה תת-שאילתה פנימית שסורקת **שוב** את טבלת המוצרים כדי לסנן את ה-IDs שלהם.
* **מה יותר יעיל?** גרסה 2א.
* **מדוע?** בגרסה 2ב ישנה כפילות ביצועים מובהקת; השאילתה הפנימית מבצעת חיפוש שתוצאותיו כבר נגישות לשאילתה הראשית. גרסה 2א חוסכת את הגישה הכפולה לטבלה ומאפשרת שימוש אופטימלי באינדקסים קיימים.

---

### 🔁 SELECT 3 – ספקים וכמות מוצרים
שאילתה זו מציגה כל ספק יחד עם מספר המוצרים שהוא מספק לרשת.  
המידע מסייע בהבנת היקף העבודה עם כל ספק ובקבלת החלטות עסקיות.
שאילתה זו נכתבה ב2 גרסאות.

**גרסה 1:**

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

![הרצת גרסה 1](images/selectQuery3_1.png)

**גרסה 2:**

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

![הרצת גרסה 2](images/selectQuery3_2.png)

**ניתוח יעילות:**
* **הבדל:** גרסה 3א משתמשת ב-`GROUP BY` המעבד את כל הנתונים בבת אחת. גרסה 3ב משתמשת בתת-שאילתה קורלטיבית בתוך ה-SELECT שרצה **שוב ושוב** לכל ספק שמופיע בתוצאה.
* **מה יותר יעיל?** גרסה 3א.
* **מדוע?** בגרסה 3ב, אם קיימים 100 ספקים, השאילתה הפנימית תופעל 100 פעמים נפרדות (מבנה של לולאה בתוך לולאה). בגרסה 3א, המנוע מבצע פעולת עיבוד מרוכזת אחת (Batch Processing), שהיא יעילה ומהירה בסדרי גודל.

---

### 🔁 SELECT 4 – עובדים פעילים
שאילתה זו מציגה עובדים פעילים בלבד, כולל פרטי הסניף שבו הם עובדים.  
המידע משמש לניהול כוח אדם ומעקב אחרי עובדים פעילים במערכת.
שאילתה זו נכתבה ב2 גרסאות.

**גרסה 1:**

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

![הרצת גרסה 1](images/selectQuery4_1.png)

**גרסה 2:**

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

![הרצת גרסה 2](images/selectQuery4_2.png)

**ניתוח יעילות:**
* **הבדל:** גרסה 4א מחברת את הטבלאות פעם אחת. גרסה 4ב מריצה תת-שאילתה ב-SELECT לשליפת השם ותת-שאילתה נוספת ב-`EXISTS` לצורך סינון – שתיהן ניגשות לאותה טבלת סניפים.
* **מה יותר יעיל?** גרסה 4א.
* **מדוע?** גרסה 4ב מאלצת את המנוע לבצע שתי סריקות נפרדות ומיותרות של טבלת הסניפים עבור כל עובד ברשימה. שימוש ב-JOIN בגרסה 4א מאפשר למנוע לשלב את המידע פעם אחת בצורה מובנית ואופטימלית.

---

### 📊 SELECT 5 – נתוני סניפים
שאילתה זו מציגה עבור כל סניף:

- כתובת מלאה ומנהל הסניף 
- מספר המוצרים הקיימים בו
- כמות הפריטים שנמצאים במלאי נמוך
- סך כל העובדים המועסקים בסניף 

המידע מסייע בניהול סניפים והשוואה ביניהם.

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

![שאילתה 5](images/selectQuery5.png)

---

### 📦 SELECT 6 – מצב מלאי מפורט
שאילתה זו מציגה תמונת מצב מלאה של המלאי עבור מוצר בכל סניף , כולל סטטוס לכל מוצר:
- זמין במלאי  
- מלאי נמוך  
- אזל מהמלאי  

המידע מתאים להצגה במסך ניהול מלאי.

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

![שאילתה 6](images/selectQuery6.png)

---

### 🏪 SELECT 7 – סיכום נתונים ארצי
שאילתה זו מספקת מבט-על לניהול הרשת ומרכזת נתונים מכלל הטבלאות לשורת סיכום אחת:

- סך כל העובדים: כמות העובדים המועסקים בכלל הסניפים.
- מגוון מוצרים: מספר המוצרים השונים המנוהלים בקטלוג הרשת.
- מלאי כולל: כמות היחידות הפיזית הקיימת בכלל מחסני וסניפי הרשת.
- מוקדי חוסר: מספר המקרים בהם מוצר בסניף מסוים ירד מתחת לסף המלאי המינימלי.

SELECT 
    (SELECT COUNT(*) FROM EMPLOYEE) AS TotalEmployees,
    (SELECT COUNT(*) FROM PRODUCT) AS ProductTypes,
    (SELECT SUM(Quantity) FROM INVENTORY) AS OverallStock,
    (SELECT COUNT(*) FROM INVENTORY WHERE Quantity < MinimumStock) AS LowStockPoints
FROM (SELECT 1) AS dummy;

![שאילתה 7](images/selectQuery7.png)

---

### 💸 SELECT 8 – ניהול הנחות
שאילתה זו מציגה את כל ההנחות ברשת ואת המוצרים המשויכים אליהן, כולל פירוק תאריכים ליום, חודש ושנה.  
המידע מאפשר ניהול נוח של מבצעים והצגה ברורה בממשק המשתמש.
השאילתה מכילה תאריכים ופירוקם לימים חודשים ושנים.

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

![שאילתה 8](images/selectQuery8.png)

---

## ✏️ שאילתות UPDATE

נכתבו 3 שאילתות UPDATE שמדגימות עדכון נתונים בצורה מבוקרת:

- העלאת שכר ב-5% לכל הקופאיות הפעילות 

**לפני העדכון:**

![לפני עדכון 1](images/update1before.png)

**העדכון:**

![עדכון 1](images/update1.png)

**אחרי העדכון:**

![אחרי עדכון 1](images/update1after.png)

- העלאת דירוג ב-1 לסניפים עם מעט פריטי מלאי נמוך 

**לפני העדכון:**

![לפני עדכון 2](images/update2before.png)

**העדכון:**

![עדכון 2](images/update2.png)

**אחרי העדכון:**

![אחרי עדכון 2](images/update2after.png)

- הגדלת אחוז ההנחה ב-5 לכל ההנחות הפעילות בתאריך 2026-04-16
- שההנחה שלהן קטנה מ-20%

**לפני העדכון:**

![לפני עדכון 3](images/update3before.png)

**העדכון:**

![עדכון 3](images/update3.png)

**אחרי העדכון:**

![אחרי עדכון 3](images/update3after.png)

שאילתות אלו מדגימות שימוש בתנאים מורכבים ובקבוצות נתונים.

---

## ❌ שאילתות DELETE

נכתבו 3 שאילתות DELETE שמדגימות מחיקה מבוקרת של נתונים:

- מחיקת רשומה אחת מטבלת המלאי שמתאימה לזוג מפתחות ספציפים

**לפני המחיקה:**

![לפני מחיקה 1](images/delete1before.png)

**המחיקה:**

![מחיקה 1](images/delete1.png)

**אחרי המחיקה:**

![אחרי מחיקה 1](images/delete1after.png)
- מחיקת רשומות מלאי של מוצר שאזל מהמלאי וגם פג תוקפו

**לפני המחיקה:**

![לפני מחיקה 2](images/delete2before.png)

**המחיקה:**

![מחיקה 2](images/delete2.png)

**אחרי המחיקה:**

![אחרי מחיקה 2](images/delete2after.png)

- מחיקת עובדים לא פעילים עם שכר בין 9000 ל-10000

**לפני המחיקה:**

![לפני מחיקה 3](images/delete3before.png)

**המחיקה:**

![מחיקה 3](images/delete3.png)

**אחרי המחיקה:**

![אחרי מחיקה 3](images/delete3after.png)

המטרה היא לשמור על בסיס נתונים נקי ורלוונטי.

---

## 🔒 אילוצים (Constraints)

נוספו אילוצים לבסיס הנתונים כדי להבטיח תקינות ועקביות של הנתונים במערכת:

* **בקרת מלאי:** הוגדר אילוץ בטבלת `INVENTORY` המבטיח כי כמות המוצרים במלאי לא תרד מתחת ל-0.

**העדכון:**

![עדכון 1](images/alter1.png)

**ניסיון הכנסת נתונים שגויים:**

![נסיון שגוי 1](images/alter1error.png)

* **עקביות תאריכי הנחה:** נוסף אילוץ בטבלת `DISCOUNT` המבטיח שתאריך הסיום של הנחה יהיה תמיד כרונולוגי לתאריך ההתחלה (EndDate ≥ StartDate).

**העדכון:**

![עדכון 2](images/alter2.png)

**ניסיון הכנסת נתונים שגויים:**

![נסיון שגוי 2](images/alter2error.png)

* **תקינות מחירים:** הוגדר אילוץ בטבלת `PRODUCT` המבטיח שמחיר מוצר יהיה תמיד ערך חיובי הגדול מ-0.

**העדכון:**

![עדכון 3](images/alter3.png)

**ניסיון הכנסת נתונים שגויים:**

![נסיון שגוי 3](images/alter3error.png)

* **מניעת שגיאות לוגיות:** האילוצים חוסמים ניסיונות להכנסת נתונים לא תקינים (כמו מחיר שלילי או תאריכים הפוכים) כבר ברמת ה-DB, ובכך שומרים על אמינות המידע.

---

## 🔄 בקרת טרנזקציות (Transactions Control)

כדי להבטיח את אמינות הנתונים ומניעת טעויות אנוש, יישמנו שימוש בטרנזקציות המאפשרות לבחון שינויים לפני אישורם הסופי בבסיס הנתונים:

* **הדגמת ROLLBACK (ביטול פעולה):** ביצענו סימולציה של טעות אנוש (הכפלת שכר מנהלים). בזכות שימוש בטרנזקציה מבוקרת, הצלחנו לבצע בדיקה של הנתונים ולאחר מכן לבטל את הפעולה בעזרת `ROLLBACK`, מה שהחזיר את הנתונים למצבם המקורי.

**הרצת הטרנזקציה והביטול:**

![](images/rollback1_1.png)

![](images/rollback1_2.png)

![](images/rollback1_3.png)

![](images/rollback1_4.png)

![](images/rollback1_5.png)

![](images/rollback1_6.png)

* **הדגמת COMMIT (אישור פעולה):** ביצענו עדכון אסטרטגי לדירוג הסניף הראשי (StoreID 1). לאחר וידוא שהנתונים תקינים בתוך הטרנזקציה, השתמשנו ב-`COMMIT` כדי לצרוב את השינוי בבסיס הנתונים באופן קבוע וסופי.

**אישור השינוי לצמיתות:**

![](images/commit2_1.png)

![](images/commit2_2.png)

![](images/commit2_3.png)

![](images/commit2_4.png)

![](images/commit2_5.png)

![](images/commit2_6.png)

* **חשיבות הטרנזקציות:** ניהול טרנזקציות הוא קריטי ברשת כמו "רמי לוי", שבה עדכוני שכר, מחירים או מלאי חייבים להתבצע בצורה אטומית (Atomic) – מה שמבטיח שאף טעות לא תישמר בטעות בבסיס הנתונים ותפגע באמינות המידע.

---

## ⚡ אינדקסים (Indexes)

כדי לייעל את מהירות המערכת ולמנוע סריקה מיותרת של כל בסיס הנתונים (Full Table Scan), הוספנו אינדקסים אסטרטגיים על עמודות חיפוש מרכזיות:

* **חיפוש מוצרים מהיר:** נוצר אינדקס על עמודת `ProductName` בטבלת `PRODUCT`. מכיוון שחיפוש מוצר לפי שם הוא הפעולה הנפוצה ביותר בקופה ובניהול המלאי, האינדקס מאפשר שליפה מיידית גם בקטלוג מוצרים גדול.

**לפני האינדקס:**

![לפני אינדקס 1](images/index1before.png)

**יצירת האינדקס:**

![יצירת אינדקס 1](images/index1.png)

**בדיקת ביצועים (Explain Analyze):**

![שיפור ביצועים 1](images/index1after.png)

* **ניהול כוח אדם:** הוגדר אינדקס משולב (Composite Index) על השדות `FirstName` ו-`LastName` בטבלת `EMPLOYEE`. במערכת ניהול, חיפוש עובד מתבצע כמעט תמיד לפי השם המלא. אינדקס זה מייעל את פעולת השליפה (Retrieval) עבור שאילתות של מחלקת משאבי אנוש.

**לפני האינדקס:**

![לפני האינדקס:](images/index2before.png)

**יצירת האינדקס:**

![יצירת אינדקס 2](images/index2.png)

**בדיקת ביצועים (Explain Analyze):**

![שיפור ביצועים 2](images/index2after.png)

* **בקרת תוקף ופגי תוקף:** נוסף אינדקס על עמודת `ExpirationDate` בטבלת `PRODUCT`. ברשת קמעונאית כמו "רמי לוי", שליפת מוצרים שעומדים לפוג (שאילתות טווח - Range Queries) היא פעולה יומיומית קריטית למניעת אובדן מלאי.

**לפני האינדקס:**

![לפני האינדקס:](images/index3before.png)

**יצירת האינדקס:**

![יצירת אינדקס 3](images/index3.png)

**בדיקת ביצועים (Explain Analyze):**

![שיפור ביצועים 3](images/index3after.png)

> **💡 הערה טכנית על ביצועי השאילתות:**
> במהלך הבדיקות, ייתכן וזמני הריצה לא יציגו שיפור דרמטי באופן מיידי. הדבר נובע משתי סיבות מרכזיות:
> 1. **נפח נתונים (Data Volume):** בסיס הנתונים כרגע מכיל כמות קטנה יחסית של שורות. במקרים כאלו, ה-Optimizer של PostgreSQL עשוי להחליט שסריקה טורית (Sequential Scan) מהירה יותר משימוש באינדקס.
> 2. **מנגנון ה-Caching:** לאחר הרצה ראשונה, הנתונים נשמרים בזיכרון המהיר (RAM), מה שגורם להבדלים בזמנים להיראות זניחים. 
> **עם זאת**, חשיבות האינדקסים היא ב-**Scalability** – הם קריטיים לשמירה על ביצועים יציבים ככל שהמערכת תתרחב לאלפי ומיליוני רשומות.

---

## 💾 גיבוי בסיס הנתונים (Database Backup)

כדי להבטיח את שרידות הנתונים ולאפשר שחזור מלא של המערכת, יצרנו קובץ גיבוי מעודכן הכולל את כל מבנה הטבלאות, האילוצים והאינדקסים של שלב ב'.

* **שלב 1: הגדרת הגיבוי ובחירת האובייקטים** - בתוך ממשק ה-pgAdmin, הגדרנו את שם הקובץ ובחרנו לגבות את כל הטבלאות תחת סכימת ה-public של בסיס הנתונים `ramileviDB`.


* **שלב 2: ביצוע הגיבוי ואישור סיום** - תהליך הגיבוי הורץ באמצעות כלי ה-Backup המובנה. ניתן לראות כי הפעולה הסתיימה בהצלחה (Process completed) ללא שגיאות.

![אישור סיום גיבוי](images/backup2.png)

* **שלב 3: הורדת הקובץ למחשב המקומי** - לאחר סיום התהליך, השתמשנו ב-Storage Manager של pgAdmin כדי לאתר את הקובץ ולהורידו ישירות למחשב המקומי. 

![וידוא קובץ בסטורג'](images/backup2storageManager.png)

* **שלב 4: העברה לתיקיית הפרויקט** - הקובץ `backup2_20_04_2026.sql` הועבר לתיקיית `Step 2` בתוך ה-Repository המקומי, ומשם הועלה ל-GitHub כחלק מהתיעוד הסופי של השלב.

---

## ✅ סיכום

בשלב זה יושם דגש על כתיבת שאילתות מורכבות ולא טריוויאליות, ניתוח יעילותן ושיפור ביצועי המערכת.  
בנוסף, הובטחה תקינות הנתונים באמצעות אילוצים ונוהל ניהול טרנזקציות.

שלב זה מהווה בסיס להמשך פיתוח המערכת וחיבור בסיס הנתונים לממשק משתמש.