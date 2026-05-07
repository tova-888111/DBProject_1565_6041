# 🛒 דוח פרויקט: ניהול רשת "רמי לוי" - שלב ג'  
##  אינטגרציה ומבטים 統合

הקדמה
בשלב זה של הפרויקט, ביצענו אינטגרציה בין מערכת ניהול רשת השיווק שלנו ("רמי לוי") לבין מערכת חיצונית של ניהול ולוגיסטיקה שקיבלנו. התהליך כלל ניתוח של בסיס הנתונים החדש, הבנת המבנה הלוגי שלו (Reverse Engineering), ומיזוגו לתוך המערכת הקיימת ליצירת בסיס נתונים אחד אחוד.
לאחר מכן כתבנו מבטים.

---
## 1. ניתוח המערכת החדשה (Reverse Engineering)

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

## חלק 1: אלגוריתם הינדוס לאחור (Reverse Engineering)

כדי להבין את המבנה של המערכת החדשה מתוך קובץ הגיבוי (SQL) שקיבלנו, פיתחנו אלגוריתם ב-Python המבצע "הינדוס לאחור".

[קישור לאלגוריתם לחץ כאן](analyze.py)


הסבר האלגוריתם:

```
האלגוריתם סורק את קובץ ה-SQL ומנתח את הסטרוקטורה של הטבלאות לפי השלבים הבאים:

זיהוי עמודות ומפתחות: סריקה של פקודות CREATE TABLE ו-ALTER TABLE לזיהוי מפתחות ראשיים (PK) וזרים (FK).

היקש לוגי (Inference): במידה ומפתח לא הוגדר מפורשות, האלגוריתם מזהה אותו על ידי ניתוח קשרי הגומלין (אם טבלה א' מפנה לטבלה ב', העמודה בטבלה ב' מזוהה כמפתח).

סיווג צורות ל-ERD:

טבלה עם מפתח זר שהוא חלק מהמפתח הראשי מסווגת כ-Weak Entity (ישות חלשה).

טבלה עם שני מפתחות זרים או יותר המקשרת בין ישויות מסווגת כ-Associative Entity (ישות קשר).

טבלה רגילה מסווגת כ-Entity (ישות).

ניתוח קרדינליות: קביעת עוצמת הקשר (1:N, N:M) לפי מיקום המפתחות הזרים.
```

פלט הרצת האלגוריתם על קובץ הגיבוי:

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
## חלק 2: דיאגרמות DSD ERD של המערכת שהתקבלה

מתוך ניתוח הפלט של האלגוריתם, שרטטנו את המבנה הלוגי של המערכת החדשה:

תרשים DSD (Data Structure Diagram): שורטט בהתאם לתלויות הפונקציונליות והמפתחות שזוהו באלגוריתם.

תרשים ERD (Entity Relationship Diagram): שרטוט גרפי המציג את הישויות, הישויות החלשות והקשרים ביניהן, כולל קרדינליות מלאה.

**DSD**:

![DSD שרה](images/SARADSD.png)

**ERD משותף**

![שרה ERD](images/SARAERD.png)

ביצענו בדיקות אחורה על מנת להוכיח שהתרשימים נכונים.

---

## חלק 3: תהליך האינטגרציה
בשלב זה חיברנו את המערכת המקורית שלנו עם המערכת החדשה ליצירת בסיס נתונים אחד אחוד.

**DSD משותף**:

![DSD משותף](images/)

**ERD משותף**

![ERD משותף](images/)

### החלטות עיצוב ואינטגרציה:
* **נקודת החיבור:** החלטנו לקשר בין [שם ישות ממערכת א'] לבין [שם ישות ממערכת ב'] כדי לאפשר זרימת מידע בין האגפים.
* **טיפול בכפילויות:** (לדוגמה: איחוד טבלאות משתמשים או התאמת סוגי נתונים).
* **שינויים בסכמה:** ביצוע שינויים באמצעות פקודות `ALTER TABLE` מבלי למחוק את הנתונים הקיימים.

---

## חלק 4: מבטים (Views)
יצרנו 3 מבטים מורכבים המאפשרים שליפת נתונים רלוונטיים מהמערכת המאוחדת:

| שם המבט | תיאור | אגף |
| :--- | :--- | :--- |
| `View_Original_Dept` | מבט המציג נתונים מהאגף המקורי (רשת החנויות) | מקורי |
| `View_New_Dept` | מבט המציג נתונים מהאגף שהתקבל | חדש |
| `View_Integrated` | מבט משולב המצליב נתונים בין שני האגפים | משולב |

---
## חלק 5: ## 💾 גיבוי בסיס הנתונים (Database Backup)