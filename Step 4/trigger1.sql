CREATE OR REPLACE FUNCTION check_store_rating_fn()
RETURNS TRIGGER AS $$
/**
 * פונקציית טריגר עבור טבלת STORE
 * תפקיד: לבצע ולידציה על שדה הדירוג לפני שמירה בבסיס הנתונים
 */
BEGIN
    -- [1] דרישה: תנאי לוגי (IF) הבודק אם הדירוג החדש מחוץ לטווח המותר (1 עד 10)
    IF NEW.Rating < 1 OR NEW.Rating > 10 THEN
        -- זריקת שגיאה מבוקרת שחוסמת את פקודת ה-SQL ומחזירה הודעה ברורה למשתמש
        RAISE EXCEPTION 'שגיאה: דירוג החנות חייב להיות מספר שלם בין 1 ל-10 בלבד! (ניסיתם להזין: %)', NEW.Rating;
    END IF;
    
    -- אם הנתון תקין, מאשרים את הרשומה (NEW) ומאפשרים לה להיכתב לטבלה
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE TRIGGER trg_check_store_rating
BEFORE INSERT OR UPDATE ON STORE
FOR EACH ROW -- הטריגר יבדוק כל שורה בנפרד (Row-Level Trigger)
EXECUTE FUNCTION check_store_rating_fn();



INSERT INTO STORE (StoreID, StoreName, Phone, StoreEmail, Rating, Address)
VALUES (10000, 'CHECK', '0500000000', 'test@store.com', 12, 'Jerusalem Bait Vagan 12');