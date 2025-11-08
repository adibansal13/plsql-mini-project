-- data.sql : Sample Data for Online Bookstore Management System

-- 1. Insert sample users
INSERT INTO users (name, email, password, address, role) VALUES
('Anubhav Yadav', 'anubhav@example.com', 'anubhav123', 'Delhi NCR, India', 'customer'),
('John Doe', 'john@example.com', 'john123', 'New York, USA', 'customer'),
('Admin', 'admin@bookstore.com', 'admin123', 'System Admin', 'admin');

-- 2. Insert sample books
INSERT INTO books (title, author, category, price, quantity) VALUES
('The Data Science Handbook', 'Field Cady', 'Data Science', 799.99, 10),
('Python for Data Analysis', 'Wes McKinney', 'Programming', 699.50, 15),
('Machine Learning with Python', 'Sebastian Raschka', 'AI & ML', 850.00, 12),
('Deep Learning', 'Ian Goodfellow', 'AI & ML', 999.00, 8),
('Clean Code', 'Robert C. Martin', 'Software Engineering', 550.00, 20),
('Database System Concepts', 'Abraham Silberschatz', 'Database', 950.00, 5);

-- 3. Create carts for users
INSERT INTO cart (user_id) VALUES (1), (2);

-- 4. Add items to carts
INSERT INTO cart_items (cart_id, book_id, quantity) VALUES
(1, 1, 1),
(1, 2, 2),
(2, 3, 1);

-- 5. Insert sample orders
INSERT INTO orders (user_id, status, total_amount) VALUES
(1, 'Delivered', 2198.49),
(2, 'Pending', 850.00);

-- 6. Add order items
INSERT INTO order_items (order_id, book_id, quantity, price) VALUES
(1, 1, 1, 799.99),
(1, 2, 2, 699.50),
(2, 3, 1, 850.00);