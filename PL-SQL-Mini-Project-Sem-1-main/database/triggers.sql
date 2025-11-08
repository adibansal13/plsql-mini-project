-- triggers.sql : Triggers for Online Bookstore Management System (PostgreSQL)

-- 1. Trigger to update book stock when order_items are inserted
CREATE OR REPLACE FUNCTION update_book_stock()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE books
    SET quantity = quantity - NEW.quantity
    WHERE book_id = NEW.book_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_book_stock
AFTER INSERT ON order_items
FOR EACH ROW
EXECUTE FUNCTION update_book_stock();


-- 2. Trigger to automatically calculate total amount in orders
CREATE OR REPLACE FUNCTION update_order_total()
RETURNS TRIGGER AS $$
DECLARE
    total NUMERIC(10,2);
BEGIN
    SELECT SUM(quantity * price)
    INTO total
    FROM order_items
    WHERE order_id = NEW.order_id;

    UPDATE orders
    SET total_amount = total
    WHERE order_id = NEW.order_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_order_total
AFTER INSERT OR UPDATE OR DELETE ON order_items
FOR EACH ROW
EXECUTE FUNCTION update_order_total();


-- 3. Trigger to ensure book quantity never goes negative
CREATE OR REPLACE FUNCTION prevent_negative_stock()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.quantity < 0 THEN
        RAISE EXCEPTION 'Book stock cannot be negative';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_prevent_negative_stock
BEFORE UPDATE ON books
FOR EACH ROW
EXECUTE FUNCTION prevent_negative_stock();
