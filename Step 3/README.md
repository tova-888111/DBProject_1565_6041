# 🛒 דוח פרויקט: ניהול רשת "רמי לוי" - שלב ג'  
##  אינטגרציה ומבטים 統合

הקדמה
בשלב זה של הפרויקט, ביצענו אינטגרציה בין מערכת ניהול רשת השיווק שלנו ("רמי לוי") לבין מערכת חיצונית של ניהול ולוגיסטיקה שקיבלנו. התהליך כלל ניתוח של בסיס הנתונים החדש, הבנת המבנה הלוגי שלו (Reverse Engineering), ומיזוגו לתוך המערכת הקיימת ליצירת בסיס נתונים אחד אחוד.
לאחר מכן כתבנו מבטים.

---
## חלק 1: ניתוח המערכת החדשה (Reverse Engineering)

המערכת שהתקבלה מתמקדת בניהול שרשרת האספקה, משלוחים, אחסון וניהול מלאי. להלן פירוט הטבלאות המרכזיות:

**STORE** (חנויות): ניהול פרטי הסניפים, דירוג ואתר אינטרנט

**PRODUCT** (מוצרים): פרטי המוצר, מחיר ותאריכי תוקף

**WAREHOUSE** (מחסנים): ניהול מיקומי אחסון וכתובות

**DELIVERY COMPANY** (חברות משלוחים): פרטי קשר של ספקי הלוגיסטיקה

**TRUCK** (משאיות/נהגים): ניהול צי הרכב והקשר לחברת השילוח

**ORDER** (הזמנות): ישות קשר מרכזית המחברת בין סניף  לנהג  ומייצגת את תהליך ההזמנה

**CONTAINS**: פירוט המוצרים והכמויות בתוך כל הזמנה 

**LOCATED**: ניהול מיקום פיזי של מוצרים בתוך המחסנים

**PRODUCT_KASHRUT**: ניהול רמות כשרות שונות למוצר

**INVENTORY**: ניהול מלאי ורמות מינימום למוצר

**WAREHOUSE_MANAGER**: ניהול מנהלים מרובים למחסן

**REGION_SERVED**: פירוט אזורי הפעילות של כל חברת משלוחים

---

## חלק 2:  אלגוריתם הינדוס לאחור (Reverse Engineering)

כדי להבין את המבנה של המערכת החדשה מתוך קובץ הגיבוי (SQL) שקיבלנו, פיתחנו אלגוריתם ב-Python המבצע "הינדוס לאחור".

[קישור לאלגוריתם לחץ כאן](analyze.py)


הסבר האלגוריתם:

## הסבר האלגוריתם: 

אלגוריתם זה מבצע ניתוח מעמיק (Parsing) של קבצי גיבוי מסוג PostgreSQL (SQL Dump) במטרה לחלץ את המבנה הלוגי של מסד הנתונים ולהמיר אותו להמלצות עיצוב עבור תרשים ישויות-קשרים (ERD).

## 🚀 פונקציונליות עיקרית

האלגוריתם פועל בשלושה שלבים מרכזיים:

### 1. מיפוי אילוצים (Constraints Mapping)
הכלי סורק את הקובץ ומזהה את כל הקשרים בין הטבלאות:
* **מפתחות ראשיים (PK):** איתור עמודות המזהות באופן ייחודי כל שורה.
* **מפתחות זרים (FK):** זיהוי קשרים והפניות לטבלאות חיצוניות.
* **היקש לוגי (Inference):** במידה ומפתח זר מפנה לטבלה שבה המפתח הראשי לא הוגדר במפורש, האלגוריתם יודע "להסיק" מהו המפתח הראשי של טבלת היעד לצורך השלמת ניתוח הקשרים.

### 2. סיווג ישויות (ERD Logic Classification)
זהו הלב של האלגוריתם. הוא מסווג כל טבלה לאחת מארבע צורות לוגיות המקובלות במודל החן (Chen's Notation):

* **Regular Entity (מלבן):** טבלה עצמאית המכילה נתונים ללא תלות קיומית בישות אחרת.
* **Weak Entity (מלבן כפול):** ישות התלויה בישות אחרת (מזוהה על פי כך שהמפתח הזר שלה הוא גם חלק מהמפתח הראשי).
* **Associative Entity (מעוין בתוך מלבן):** טבלה המקשרת בין שתי ישויות או יותר (קשר "רבים לרבים"), כגון טבלת הזמנות או מיקומים.
* **Multivalued Attribute (אליפסה כפולה):** זיהוי תכונות רב-ערכיות המיוצגות כטבלה נפרדת (מזוהה לרוב לפי קו תחתי בשם הטבלה או לפי מבנה המפתחות).



### 3. ניתוח עמודות והקשרים (Context Analysis)
עבור כל עמודה בכל טבלה, האלגוריתם מפיק דוח הכולל:
* **Classification:** האם העמודה היא PK, FK, או תכונה רגילה.
* **Cardinality Context:** הסבר על עוצמת הקשר (למשל, האם מדובר בקשר של "רבים לאחד" - N:1).

## 📊 פלט האלגוריתם
בסיום ההרצה, מתקבל דוח מפורט המספק למתכנן בסיס הנתונים "מפת דרכים" ויזואלית הכוללת:
1.  **שם הטבלה** כפי שהיא מופיעה במסד הנתונים.
2.  **הצורה הלוגית המומלצת** לציור ב-ERD.
3.  **דוח עמודות מפורט** הכולל את התפקיד הלוגי של כל שדה והקשר שלו לישויות אחרות.



**דוגמת פלט**: 

```
=== FINAL REVERSE ENGINEERING REPORT FOR ERD: BackupSara.sql ===
=============================================================================================================================

[TABLE]: ORDER
ERD SUGGESTION: ASSOCIATIVE ENTITY (Rectangle + Diamond)
Column Name               | Classification                                | Cardinality Context
-----------------------------------------------------------------------------------------------------------------------------
orderid                   | [PK] PRIMARY KEY                              | Identifier
price                     | Regular Attribute                             | -
deliverydate              | Regular Attribute                             | -
orderdate                 | Regular Attribute                             | -
storeid                   | [FK] -> STORE                                 | Many to 1 (N:1)
driverid                  | [FK] -> TRUCK                                 | Many to 1 (N:1)
-----------------------------------------------------------------------------------------------------------------------------

[TABLE]: CONTAINS
ERD SUGGESTION: WEAK ENTITY (Double Rectangle)
Column Name               | Classification                                | Cardinality Context
-----------------------------------------------------------------------------------------------------------------------------
orderid                   | [PK] PRIMARY KEY, [FK] -> ORDER               | Many to 1 (N:1)
productid                 | [PK] PRIMARY KEY, [FK] -> PRODUCT             | Many to 1 (N:1)
quantity                  | Regular Attribute                             | -
-----------------------------------------------------------------------------------------------------------------------------

[TABLE]: DELIVERYCOMPAGNY
ERD SUGGESTION: REGULAR ENTITY (Rectangle)
Column Name               | Classification                                | Cardinality Context
-----------------------------------------------------------------------------------------------------------------------------
deliverycieid             | [PK] PRIMARY KEY                              | Identifier
deliveryciename           | Regular Attribute                             | -
deliveryciephonenb        | Regular Attribute                             | -
email                     | Regular Attribute                             | -
-----------------------------------------------------------------------------------------------------------------------------

[TABLE]: DELIVERYCOMPAGNY_REGIONSERVED
ERD SUGGESTION: WEAK ENTITY (Double Rectangle)
Column Name               | Classification                                | Cardinality Context
-----------------------------------------------------------------------------------------------------------------------------
deliverycieid             | [PK] PRIMARY KEY, [FK] -> DELIVERYCOMPAGNY    | Many to 1 (N:1)
regionserved              | [PK] PRIMARY KEY                              | Identifying Attribute
-----------------------------------------------------------------------------------------------------------------------------

[TABLE]: INVENTORY
ERD SUGGESTION: WEAK ENTITY (Double Rectangle)
Column Name               | Classification                                | Cardinality Context
-----------------------------------------------------------------------------------------------------------------------------
productid                 | [PK] PRIMARY KEY, [FK] -> PRODUCT             | Many to 1 (N:1)
quantity                  | Regular Attribute                             | -
minimumstock              | Regular Attribute                             | -
-----------------------------------------------------------------------------------------------------------------------------

[TABLE]: LOCATED
ERD SUGGESTION: WEAK ENTITY (Double Rectangle)
Column Name               | Classification                                | Cardinality Context
-----------------------------------------------------------------------------------------------------------------------------
productid                 | [PK] PRIMARY KEY, [FK] -> PRODUCT             | Many to 1 (N:1)
warehouseid               | [PK] PRIMARY KEY, [FK] -> WAREHOUSE           | Many to 1 (N:1)
aislenb                   | Regular Attribute                             | -
shelfnb                   | Regular Attribute                             | -
-----------------------------------------------------------------------------------------------------------------------------

[TABLE]: PRODUCT
ERD SUGGESTION: REGULAR ENTITY (Rectangle)
Column Name               | Classification                                | Cardinality Context
-----------------------------------------------------------------------------------------------------------------------------
productid                 | [PK] PRIMARY KEY                              | Identifier
productname               | Regular Attribute                             | -
price                     | Regular Attribute                             | -
dateofmanufacture         | Regular Attribute                             | -
expirationdate            | Regular Attribute                             | -
-----------------------------------------------------------------------------------------------------------------------------

[TABLE]: PRODUCT_KASHRUT
ERD SUGGESTION: WEAK ENTITY (Double Rectangle)
Column Name               | Classification                                | Cardinality Context
-----------------------------------------------------------------------------------------------------------------------------
productid                 | [PK] PRIMARY KEY, [FK] -> PRODUCT             | Many to 1 (N:1)
kashrut                   | [PK] PRIMARY KEY                              | Identifying Attribute
-----------------------------------------------------------------------------------------------------------------------------

[TABLE]: STORE
ERD SUGGESTION: REGULAR ENTITY (Rectangle)
Column Name               | Classification                                | Cardinality Context
-----------------------------------------------------------------------------------------------------------------------------
storeid                   | [PK] PRIMARY KEY                              | Identifier
storename                 | Regular Attribute                             | -
phone                     | Regular Attribute                             | -
rating                    | Regular Attribute                             | -
websiteurl                | Regular Attribute                             | -
-----------------------------------------------------------------------------------------------------------------------------

[TABLE]: TRUCK
ERD SUGGESTION: REGULAR ENTITY (Rectangle)
Column Name               | Classification                                | Cardinality Context
-----------------------------------------------------------------------------------------------------------------------------
driverid                  | [PK] PRIMARY KEY                              | Identifier
active                    | Regular Attribute                             | -
capacity                  | Regular Attribute                             | -
licenseplate              | Regular Attribute                             | -
maintenancestatus         | Regular Attribute                             | -
deliverycieid             | [FK] -> DELIVERYCOMPAGNY                      | Many to 1 (N:1)
-----------------------------------------------------------------------------------------------------------------------------

[TABLE]: WAREHOUSE
ERD SUGGESTION: REGULAR ENTITY (Rectangle)
Column Name               | Classification                                | Cardinality Context
-----------------------------------------------------------------------------------------------------------------------------
warehouseid               | [PK] PRIMARY KEY                              | Identifier
region                    | Regular Attribute                             | -
address                   | Regular Attribute                             | -
-----------------------------------------------------------------------------------------------------------------------------

[TABLE]: WAREHOUSE_WAREHOUSEMANAGER
ERD SUGGESTION: WEAK ENTITY (Double Rectangle)
Column Name               | Classification                                | Cardinality Context
-----------------------------------------------------------------------------------------------------------------------------
warehouseid               | [PK] PRIMARY KEY, [FK] -> WAREHOUSE           | Many to 1 (N:1)
warehousemanager          | [PK] PRIMARY KEY                              | Identifying Attribute
-----------------------------------------------------------------------------------------------------------------------------
```

---
## חלק 3: דיאגרמות DSD ERD של המערכת שהתקבלה

מתוך ניתוח הפלט של האלגוריתם, שרטטנו את המבנה הלוגי של המערכת החדשה:

תרשים DSD (Data Structure Diagram): שורטט בהתאם לתלויות הפונקציונליות והמפתחות שזוהו באלגוריתם.

תרשים ERD (Entity Relationship Diagram): שרטוט גרפי המציג את הישויות, הישויות החלשות והקשרים ביניהן, כולל קרדינליות מלאה.

**DSD**:

![DSD שרה](images/SARADSD.png)

**ERD**

![שרה ERD](images/SARAERD.png)

ביצענו בדיקות אחורה על מנת להוכיח שהתרשימים נכונים.

---

## חלק 4: תהליך האינטגרציה
בשלב זה חיברנו את המערכת המקורית שלנו עם המערכת החדשה ליצירת בסיס נתונים אחד אחוד.

**DSD משותף**:

![DSD משותף](images/IntegratedDSD.png)

**ERD משותף**

![ERD משותף](images/IntegratedERD.png)

### החלטות עיצוב ואינטגרציה:
לטבלה Store נוספה תכונה websiteurl.
לטבלה Product הוסרה התכונה Kashrut ונוספה התכונה dateofmanufacture .
איחדנו את טבלאות Store החדשה והישנה, Product החדשה והישנה.
איחדנו את הטבלאות Inventory החדשה והישנה , על אף שלחדשה אין שדה מפתח זר StoreID  מהטבלה Store.
את נקודות החיבור שהיו עם הטבלאות Product Store  החדשות, העברנו לטבלאות הישנות.


---

## חלק 5: מבטים (Views)
יצרנו 3 מבטים מורכבים המאפשרים שליפת נתונים רלוונטיים מהמערכת המאוחדת:

| שם המבט | תיאור | אגף |
| :--- | :--- | :--- |
| `View_Original_Dept` | מבט המציג נתונים מהאגף המקורי (רשת החנויות) | מקורי |
| `View_New_Dept` | מבט המציג נתונים מהאגף שהתקבל | חדש |
| `View_Integrated` | מבט משולב המצליב נתונים בין שני האגפים | משולב |

---
## חלק 6: ## 💾 גיבוי בסיס הנתונים (Database Backup)