-- =========================================================
-- Step 2 - RollbackCommit.sql
-- Demonstrating Transaction Control
-- =========================================================

-- חלק א: הדגמת ROLLBACK (ביטול פעולה)
-- ---------------------------------------------------------
-- 1. מצב לפני
SELECT * FROM EMPLOYEE WHERE Role = 'Store Manager';

-- 2. התחלת טרנזקציה וביצוע שינוי (העלאת שכר מוגזמת)
BEGIN;
UPDATE EMPLOYEE SET Salary = Salary * 2 WHERE Role = 'Store Manager';

-- 3. בדיקה שהשינוי קרה (זמנית)
SELECT * FROM EMPLOYEE WHERE Role = 'Store Manager';

-- 4. ביצוע ביטול
ROLLBACK;

-- 5. הוכחה שהנתונים חזרו לקדמותם
SELECT * FROM EMPLOYEE WHERE Role = 'Store Manager';


-- חלק ב: הדגמת COMMIT (אישור פעולה)
-- ---------------------------------------------------------
-- 1. מצב לפני
SELECT * FROM STORE WHERE StoreID = 1;

-- 2. התחלת טרנזקציה ועדכון דירוג חנות
BEGIN;
UPDATE STORE SET Rating = 10 WHERE StoreID = 1;

SELECT * FROM STORE WHERE StoreID = 1;

-- 3. אישור סופי של השינוי
COMMIT;

-- 4. הוכחה שהשינוי נשמר לצמיתות
SELECT * FROM STORE WHERE StoreID = 1;