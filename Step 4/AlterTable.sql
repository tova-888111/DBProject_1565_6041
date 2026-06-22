
--לפרוצדורה 2 הוספנו לטבלה ORDER עמודה של STATUS עם ברירת מחדל PENDING
ALTER TABLE "ORDER" ADD COLUMN Status VARCHAR(20) DEFAULT 'PENDING';


-- מחקנו מהטבלה של הזמנות את תאריך מסירה, זה נתון לא נצרך מבחינתנו
ALTER TABLE "ORDER" DROP COLUMN DeliveryDate;