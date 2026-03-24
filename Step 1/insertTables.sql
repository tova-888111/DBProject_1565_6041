-- דוגמה להכנסת נתונים ידנית (שיטה א')
INSERT INTO STORE (StoreID, StoreName, Phone, StoreEmail, Rating) 
VALUES (1, 'Rami Levy Jerusalem', '02-1234567', 'jer@ramilevy.co.il', 5);

INSERT INTO CATEGORY (CategoryID, CategoryName, IsActive) 
VALUES (1, 'Dairy', 1);

INSERT INTO PRODUCT (ProductID, ProductName, Price, Kashrut, Brand, ExpirationDate, CategoryID)
VALUES (101, 'Milk 3%', 6.90, 'Badatz', 'Tnuva', '2026-04-01', 1);

-- כאן יבואו שאר פקודות ה-INSERT מהשיטות השונות