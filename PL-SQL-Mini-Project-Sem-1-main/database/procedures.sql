-- procedures.sql : PL/pgSQL Procedures and Functions for Online Bookstore Management System

-- 1. Procedure: Register a new user
CREATE OR REPLACE PROCEDURE register_user(
    p_name VARCHAR,
    p_email VARCHAR,
    p_password VARCHAR,
    p_address TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO users (name, email, password, address)
    VALUES (p_name, p_email, p_password, p_address);
END;
$$;


-- 2. Function: User login validation (returns user_id if valid)
CREATE OR REPLACE FUNCTION login_user(
    p_email VARCHAR,
    p_password VARCHAR
)
RETURNS TABLE(user_id INT, name VARCHAR, email VARCHAR, address TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT u.user_id, u.name, u.email, u.address
    FROM users u
    WHERE u.email = p_email AND u.password = p_password;
END;
$$ LANGUAGE plpgsql;


-- 3. Function: Search books by title or author
CREATE OR REPLACE FUNCTION search_books(
    p_keyword VARCHAR
) RETURNS TABLE(
    book_id INT,
    title VARCHAR,
    author VARCHAR,
    category VARCHAR,
    price NUMERIC,
    quantity INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT b.book_id, b.title, b.author, b.category, b.price, b.quantity
    FROM books b
    WHERE LOWER(b.title) LIKE LOWER('%' || p_keyword || '%')
       OR LOWER(b.author) LIKE LOWER('%' || p_keyword || '%');
END;
$$;


-- 4. Procedure: Add book to cart
CREATE OR REPLACE PROCEDURE add_to_cart(
    p_user_id INT,
    p_book_id INT,
    p_quantity INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_cart_id INT;
BEGIN
    -- Get or create user's cart
    SELECT cart_id INTO v_cart_id FROM cart WHERE user_id = p_user_id;

    IF v_cart_id IS NULL THEN
        INSERT INTO cart (user_id) VALUES (p_user_id) RETURNING cart_id INTO v_cart_id;
    END IF;

    -- Add item to cart or update quantity
    INSERT INTO cart_items (cart_id, book_id, quantity)
    VALUES (v_cart_id, p_book_id, p_quantity)
    ON CONFLICT (cart_id, book_id)
    DO UPDATE SET quantity = cart_items.quantity + EXCLUDED.quantity;
END;
$$;


-- 5. Procedure: Place an order
CREATE OR REPLACE PROCEDURE place_order(p_user_id INT)
LANGUAGE plpgsql
AS $$
DECLARE
    v_cart_id INT;
    v_order_id INT;
BEGIN
    -- Get user's cart
    SELECT cart_id INTO v_cart_id FROM cart WHERE user_id = p_user_id;
    IF v_cart_id IS NULL THEN
        RAISE EXCEPTION 'No cart found for user';
    END IF;

    -- Create new order
    INSERT INTO orders (user_id, status, total_amount)
    VALUES (p_user_id, 'Pending', 0.0) RETURNING order_id INTO v_order_id;

    -- Move items from cart to order_items
    INSERT INTO order_items (order_id, book_id, quantity, price)
    SELECT v_order_id, b.book_id, ci.quantity, b.price
    FROM cart_items ci
    JOIN books b ON ci.book_id = b.book_id
    WHERE ci.cart_id = v_cart_id;

    -- Clear cart after order placement
    DELETE FROM cart_items WHERE cart_id = v_cart_id;

    -- Update total using trigger automatically
END;
$$;


-- 6. Function: View order history (FIXED)
CREATE OR REPLACE FUNCTION view_order_history(p_user_id INT)
RETURNS TABLE(
    order_id INT,
    order_date TIMESTAMP,
    status VARCHAR,
    total_amount NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    -- FIX: Added table alias 'o' to specify columns
    SELECT o.order_id, o.order_date, o.status, o.total_amount
    FROM orders o
    WHERE o.user_id = p_user_id
    ORDER BY o.order_date DESC;
END;
$$;

