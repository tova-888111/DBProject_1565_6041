-- Optional: delete existing data first
-- DELETE FROM CATEGORY;

INSERT INTO CATEGORY (CategoryID, CategoryName, IsActive) VALUES
(1, 'Fresh Milk', 1),
(2, 'Yellow Cheese', 1),
(3, 'Fruit Yogurt', 1),
(4, 'Chocolate Desserts', 1),
(5, 'Butter and Margarine', 1),
(6, 'Free Range Eggs', 1),
(7, 'Sliced Bread', 1),
(8, 'Whole Grain Bread', 1),
(9, 'Pita Bread', 1),
(10, 'Bread Rolls', 1),
(11, 'Yeast Cakes', 1),
(12, 'Dry Cookies', 1),
(13, 'Burekas and Frozen Pastries', 1),
(14, 'Frozen Pizza', 1),
(15, 'Strauss Ice Cream', 1),
(16, 'Apples', 1),
(17, 'Bananas', 1),
(18, 'Cucumbers', 1),
(19, 'Tomatoes', 1),
(20, 'Colored Peppers', 1),
(21, 'Onions and Root Vegetables', 1),
(22, 'Potatoes', 1),
(23, 'Lettuce and Leafy Greens', 1),
(24, 'Citrus Fruits', 1),
(25, 'Tropical Fruits', 1),
(26, 'Fresh Beef', 1),
(27, 'Whole Chicken', 1),
(28, 'Chicken Drumsticks', 1),
(29, 'Chicken Breast', 1),
(30, 'Ground Beef', 1),
(31, 'Premium Steaks', 1),
(32, 'Salmon', 1),
(33, 'Tilapia', 1),
(34, 'Canned Tuna', 1),
(35, 'Sausages', 1),
(36, 'Deli Pastrami', 1),
(37, 'Prepared Salads', 1),
(38, 'Hummus and Tahini', 1),
(39, 'Persian Rice', 1),
(40, 'Brown Rice', 1),
(41, 'Lentils and Legumes', 1),
(42, 'Italian Pasta', 1),
(43, 'Spaghetti', 1),
(44, 'Ptitim', 1),
(45, 'Couscous', 1),
(46, 'Wheat Flour', 1),
(47, 'Spelt Flour', 1),
(48, 'White Sugar', 1),
(49, 'Canola Oil', 1),
(50, 'Olive Oil', 1),
(51, 'Tomato Paste', 1),
(52, 'Ketchup and Mayonnaise', 1),
(53, 'House Spices', 1),
(54, 'Instant Coffee', 1),
(55, 'Turkish Coffee', 1),
(56, 'Green Tea', 1),
(57, 'Herbal Tea', 1),
(58, 'Kids Breakfast Cereals', 1),
(59, 'Granola and Fiber', 1),
(60, 'Energy Bars', 1),
(61, 'Dark Chocolate', 1),
(62, 'Savory Snacks', 1),
(63, 'Bamba and Bissli', 1),
(64, 'Roasted Nuts and Seeds', 1),
(65, 'Orange Juice', 1),
(66, 'Cola and Soft Drinks', 1),
(67, 'Mineral Water', 1),
(68, 'Light Beer', 1),
(69, 'Red Wine', 1),
(70, 'White Wine', 1),
(71, 'Vodka and Arak', 1),
(72, 'Laundry Detergent', 1),
(73, 'Fabric Softener', 1),
(74, 'Dishwashing Liquid', 1),
(75, 'Floor Cleaner', 1),
(76, 'Window Cleaner', 1),
(77, 'Air Fresheners', 1),
(78, 'Toilet Paper', 1),
(79, 'Paper Towels', 1),
(80, 'Diapers', 1),
(81, 'Wet Wipes', 1),
(82, 'Shampoo and Conditioner', 1),
(83, 'Liquid Soap', 1),
(84, 'Toothpaste', 1),
(85, 'Men Deodorant', 1),
(86, 'Women Deodorant', 1),
(87, 'Shaving Products', 1),
(88, 'Feminine Hygiene Products', 1),
(89, 'Vitamins', 1),
(90, 'Bandages and First Aid', 1),
(91, 'Shabbat Candles', 1),
(92, 'Premium Disposable Products', 1),
(93, 'Trash Bags', 1),
(94, 'Dog Food', 1),
(95, 'Cat Food', 1),
(96, 'Cat Litter', 1),
(97, 'Stationery', 1),
(98, 'Batteries', 1),
(99, 'Gift Cards', 1),
(100, 'Holiday Products', 1);

INSERT INTO CATEGORY (CategoryID, CategoryName, IsActive)
SELECT CategoryID + 100, CategoryName || ' Organic', 1
FROM CATEGORY
WHERE CategoryID BETWEEN 1 AND 100;

INSERT INTO CATEGORY (CategoryID, CategoryName, IsActive)
SELECT CategoryID + 200, CategoryName || ' Kosher for Passover', 1
FROM CATEGORY
WHERE CategoryID BETWEEN 1 AND 100;

INSERT INTO CATEGORY (CategoryID, CategoryName, IsActive)
SELECT CategoryID + 300, CategoryName || ' Sugar Free', 1
FROM CATEGORY
WHERE CategoryID BETWEEN 1 AND 100;

INSERT INTO CATEGORY (CategoryID, CategoryName, IsActive)
SELECT CategoryID + 400, CategoryName || ' Mehadrin', 1
FROM CATEGORY
WHERE CategoryID BETWEEN 1 AND 100;