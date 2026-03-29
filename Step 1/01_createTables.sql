-- יצירת טבלת חנות
CREATE TABLE STORE
(
  StoreID INT NOT NULL,
  StoreName VARCHAR(100) NOT NULL,
  Phone VARCHAR(15) NOT NULL,
  StoreEmail VARCHAR(100) NOT NULL,
  Rating INT NOT NULL,
  PRIMARY KEY (StoreID)
);

-- יצירת טבלת מיקומים (קשר 1:1 או 1:N מול חנות)
CREATE TABLE LOCATION
(
  LocationID INT NOT NULL,
  City VARCHAR(100) NOT NULL,
  Street VARCHAR(100) NOT NULL,
  StreetNumber INT NOT NULL,
  Region VARCHAR(50) NOT NULL,
  StoreID INT NOT NULL,
  PRIMARY KEY (LocationID),
  FOREIGN KEY (StoreID) REFERENCES STORE(StoreID)
);

-- יצירת טבלת עובדים
CREATE TABLE EMPLOYEE
(
  EmployeeID INT NOT NULL,
  FirstName VARCHAR(50) NOT NULL,
  LastName VARCHAR(50) NOT NULL,
  Status VARCHAR(20) NOT NULL, -- פעיל/לא פעיל
  Salary NUMERIC(10, 2) NOT NULL,
  Role VARCHAR(50) NOT NULL,
  StoreID INT NOT NULL,
  PRIMARY KEY (EmployeeID),
  FOREIGN KEY (StoreID) REFERENCES STORE(StoreID)
);

-- יצירת טבלת קטגוריות
CREATE TABLE CATEGORY
(
  CategoryID INT NOT NULL,
  CategoryName VARCHAR(100) NOT NULL,
  IsActive INT NOT NULL, -- 1 לכן, 0 ללא
  PRIMARY KEY (CategoryID)
);

-- יצירת טבלת מוצרים
CREATE TABLE PRODUCT
(
  ProductID INT NOT NULL,
  ProductName VARCHAR(100) NOT NULL,
  Price NUMERIC(10, 2) NOT NULL,
  Kashrut VARCHAR(50) NOT NULL,
  Brand VARCHAR(50) NOT NULL,
  ExpirationDate DATE NOT NULL, -- שימוש בטיפוס DATE כנדרש
  CategoryID INT NOT NULL,
  PRIMARY KEY (ProductID),
  FOREIGN KEY (CategoryID) REFERENCES CATEGORY(CategoryID)
);

-- יצירת טבלת ספקים
CREATE TABLE SUPPLIER
(
  SupplierID INT NOT NULL,
  SupplierName VARCHAR(100) NOT NULL,
  Email VARCHAR(100) NOT NULL,
  ContactPhone VARCHAR(15) NOT NULL,
  Address VARCHAR(200) NOT NULL,
  PRIMARY KEY (SupplierID)
);

-- יצירת טבלת מלאי (טבלת קשר חנות-מוצר)
CREATE TABLE INVENTORY
(
  StoreID INT NOT NULL,
  ProductID INT NOT NULL,
  Quantity INT NOT NULL,
  MinimumStock INT NOT NULL,
  PRIMARY KEY (StoreID, ProductID),
  FOREIGN KEY (StoreID) REFERENCES STORE(StoreID),
  FOREIGN KEY (ProductID) REFERENCES PRODUCT(ProductID)
);

-- יצירת טבלת הנחות
CREATE TABLE DISCOUNT
(
  DiscountID INT NOT NULL,
  DiscountName VARCHAR(100) NOT NULL,
  DiscountPercentage INT NOT NULL,
  StartDate DATE NOT NULL, -- שימוש בטיפוס DATE כנדרש
  EndDate DATE NOT NULL,
  PRIMARY KEY (DiscountID)
);

-- טבלת קשר: ספקים שמספקים מוצרים
CREATE TABLE SUPPLIERED_BY
(
  SupplierID INT NOT NULL,
  ProductID INT NOT NULL,
  PRIMARY KEY (SupplierID, ProductID),
  FOREIGN KEY (SupplierID) REFERENCES SUPPLIER(SupplierID),
  FOREIGN KEY (ProductID) REFERENCES PRODUCT(ProductID)
);

-- טבלת קשר: הנחות שחלות על מוצרים
CREATE TABLE APPLIES_TO
(
  ProductID INT NOT NULL,
  DiscountID INT NOT NULL,
  PRIMARY KEY (ProductID, DiscountID),
  FOREIGN KEY (ProductID) REFERENCES PRODUCT(ProductID),
  FOREIGN KEY (DiscountID) REFERENCES DISCOUNT(DiscountID)
);

