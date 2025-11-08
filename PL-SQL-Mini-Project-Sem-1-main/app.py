from flask import Flask, request, render_template, redirect, session, url_for, flash
import psycopg2
import psycopg2.extras  # Import this for dictionary cursors
import os
from functools import wraps

# Flask app setup. It will look for the 'templates' folder automatically.
app = Flask(__name__)
app.secret_key = "super_secret_key"  # Keep this for session management


# --- Database connection setup ---
def get_db_connection():
    """
    Establishes a connection to the PostgreSQL database.
    Returns a connection object with a Dictionary Cursor.
    """
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="online_bookstore_db",
            user="postgres",
            # !!! IMPORTANT !!!
            # Update this password to your own PostgreSQL password
            password="Aditya123",
            cursor_factory=psycopg2.extras.DictCursor,  # Use DictCursor
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error connecting to database: {e}")
        return None


# ------------------- AUTH DECORATORS ------------------- #


def admin_required(f):
    """
    A decorator to restrict access to admin-only pages.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "role" not in session or session["role"] != "admin":
            flash("Admin access only! Please log in as an admin.", "danger")
            return redirect(url_for("login_user"))
        return f(*args, **kwargs)

    return decorated_function


def login_required(f):
    """
    A decorator to restrict access to logged-in users.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            session["next_url"] = request.path  # Save where they were trying to go
            return redirect(url_for("login_user"))
        return f(*args, **kwargs)

    return decorated_function


# ------------------- CORE ROUTES ------------------- #


@app.route("/")
def home():
    """
    Redirects the homepage to the main books page or login.
    """
    if "user_id" in session:
        return redirect(url_for("search_books"))
    return redirect(url_for("login_user"))


@app.route("/login", methods=["GET", "POST"])
def login_user():
    """
    Handles user login.
    """
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        if not conn:
            flash("Database connection error.", "danger")
            return render_template("login.html")

        cur = conn.cursor()
        # Use your login function (assuming it's loaded in the DB)
        # We'll just use a direct query as in your original file
        cur.execute(
            "SELECT * FROM users WHERE email = %s AND password = %s", (email, password)
        )
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            # Thanks to DictCursor, we can access by name!
            session["user_id"] = user["user_id"]
            session["username"] = user["name"]
            session["email"] = user["email"]
            session["role"] = user["role"]

            flash(f"Welcome back, {user['name']}!", "success")

            next_url = session.pop("next_url", None)
            if next_url:
                return redirect(next_url)
            elif user["role"] == "admin":
                return redirect(url_for("manage_books"))
            else:
                return redirect(url_for("profile"))
        else:
            flash("Invalid email or password. Please try again.", "danger")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    """
    Logs the user out by clearing the session.
    """
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("login_user"))


@app.route("/register", methods=["GET", "POST"])
def register_user():
    """
    Handles new user registration using your PL/SQL procedure.
    """
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        address = request.form.get("address")

        conn = get_db_connection()
        if not conn:
            flash("Database connection error.", "danger")
            return render_template("register.html")

        cur = conn.cursor()
        try:
            # Use your stored procedure `register_user`
            cur.execute(
                "CALL register_user(%s, %s, %s, %s)", (name, email, password, address)
            )
            conn.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login_user"))
        except psycopg2.Error as e:
            conn.rollback()
            if "users_email_key" in str(e):  # Check for unique email violation
                flash("An account with this email already exists.", "danger")
            else:
                flash(f"An error occurred. Please try again.", "danger")
        finally:
            cur.close()
            conn.close()

    return render_template("register.html")


@app.route("/profile")
@login_required
def profile():
    """
    Displays the user's profile and their order history.
    """
    user_id = session["user_id"]
    conn = get_db_connection()
    cur = conn.cursor()

    # Get user details
    cur.execute(
        "SELECT name, email, address, role FROM users WHERE user_id = %s", (user_id,)
    )
    user = cur.fetchone()

    # Get user's order history using your function
    cur.execute("SELECT * FROM view_order_history(%s)", (user_id,))
    orders = cur.fetchall()

    # Get full order items for display
    full_orders = []
    for order in orders:
        cur.execute(
            """
            SELECT oi.quantity, oi.price, b.title
            FROM order_items oi
            JOIN books b ON oi.book_id = b.book_id
            WHERE oi.order_id = %s
        """,
            (order["order_id"],),
        )
        items = cur.fetchall()
        full_orders.append({"details": order, "items": items})

    cur.close()
    conn.close()

    return render_template("profile.html", user=user, orders=full_orders)


# ------------------- BOOK & SEARCH ROUTES ------------------- #


@app.route("/books")
@login_required
def books():
    """
    Redirects to the main search page.
    """
    return redirect(url_for("search_books"))


@app.route("/search", methods=["GET"])
@login_required
def search_books():
    """
    Displays books, optionally filtered by a search query, using your PL/SQL function.
    """
    query = request.args.get("query", "")
    conn = get_db_connection()
    cur = conn.cursor()

    # Use your search_books function
    cur.execute("SELECT * FROM search_books(%s)", (query,))
    books = cur.fetchall()

    cur.close()
    conn.close()

    # This one template handles both customer and admin
    # The template itself will check session['role']
    return render_template("book_management.html", books=books, search_query=query)


# ------------------- CART ROUTES ------------------- #


@app.route("/cart")
@login_required
def view_cart():
    """
    Displays the contents of the user's shopping cart.
    """
    user_id = session["user_id"]
    conn = get_db_connection()
    cur = conn.cursor()

    # Get user's cart items with book details
    cur.execute(
        """
        SELECT ci.cart_item_id, b.book_id, b.title, b.author, b.price, ci.quantity, 
               (b.price * ci.quantity) AS subtotal, b.quantity AS stock
        FROM cart_items ci
        JOIN books b ON ci.book_id = b.book_id
        JOIN cart c ON ci.cart_id = c.cart_id
        WHERE c.user_id = %s
        ORDER BY b.title;
    """,
        (user_id,),
    )
    cart_items = cur.fetchall()

    total = sum([item["subtotal"] for item in cart_items])

    cur.close()
    conn.close()

    return render_template("cart.html", cart_items=cart_items, total=total)


@app.route("/cart/add/<int:book_id>", methods=["POST"])
@login_required
def add_to_cart(book_id):
    """
    Adds a book to the user's cart using your PL/SQL procedure.
    """
    user_id = session["user_id"]
    quantity = int(request.form.get("quantity", 1))

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Use your stored procedure `add_to_cart`
        cur.execute("CALL add_to_cart(%s, %s, %s)", (user_id, book_id, quantity))
        conn.commit()
        flash("Book added to your cart!", "success")
    except psycopg2.Error as e:
        conn.rollback()
        flash(f"Error adding to cart: Could not add item.", "danger")
    finally:
        cur.close()
        conn.close()

    return redirect(request.referrer or url_for("books"))


@app.route("/cart/update/<int:cart_item_id>", methods=["POST"])
@login_required
def update_cart(cart_item_id):
    """
    Updates the quantity of an item in the cart.
    """
    try:
        quantity = int(request.form.get("quantity"))
        if quantity < 1:
            flash("Quantity must be at least 1.", "danger")
            return redirect(url_for("view_cart"))
    except ValueError:
        flash("Invalid quantity.", "danger")
        return redirect(url_for("view_cart"))

    conn = get_db_connection()
    cur = conn.cursor()
    # Check against stock before updating
    cur.execute(
        """
        SELECT b.quantity 
        FROM books b
        JOIN cart_items ci ON b.book_id = ci.book_id
        WHERE ci.cart_item_id = %s
    """,
        (cart_item_id,),
    )
    stock = cur.fetchone()["quantity"]

    if quantity > stock:
        flash(f"Only {stock} copies available. Quantity set to maximum.", "warning")
        quantity = stock

    cur.execute(
        "UPDATE cart_items SET quantity = %s WHERE cart_item_id = %s",
        (quantity, cart_item_id),
    )
    conn.commit()
    cur.close()
    conn.close()

    flash("Cart updated successfully.", "info")
    return redirect(url_for("view_cart"))


@app.route("/cart/remove/<int:cart_item_id>", methods=["POST"])
@login_required
def remove_from_cart(cart_item_id):
    """
    Removes an item from the cart.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM cart_items WHERE cart_item_id = %s", (cart_item_id,))
    conn.commit()
    cur.close()
    conn.close()

    flash("Book removed from cart.", "success")
    return redirect(url_for("view_cart"))


# ------------------- ORDER ROUTES ------------------- #


@app.route("/checkout", methods=["POST"])
@login_required
def checkout():
    """
    Processes the checkout using your PL/SQL procedure.
    """
    user_id = session["user_id"]
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Use your stored procedure `place_order`
        cur.execute("CALL place_order(%s)", (user_id,))
        conn.commit()
        flash("Order placed successfully! ✅", "success")
        # Your triggers (update_book_stock, update_order_total)
        # will run automatically in the database!
    except psycopg2.Error as e:
        conn.rollback()
        # This will catch errors from your trigger, e.g., negative stock
        flash(f"Error placing order: {e}", "danger")
        return redirect(url_for("view_cart"))  # Go back to cart if error
    finally:
        cur.close()
        conn.close()

    return redirect(url_for("profile"))  # Redirect to profile to see the new order


# ------------------- ADMIN ROUTES ------------------- #


@app.route("/admin/books")
@admin_required
def manage_books():
    """
    Redirects admin to the main search/book management page.
    """
    # The 'search_books' route already handles admin/customer views
    return redirect(url_for("search_books"))


@app.route("/admin/books/add", methods=["GET", "POST"])
@admin_required
def add_book():
    """
    Handles adding a new book to the database.
    """
    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        category = request.form.get("category")
        price = request.form.get("price")
        quantity = request.form.get("quantity")

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO books (title, author, category, price, quantity)
            VALUES (%s, %s, %s, %s, %s)
        """,
            (title, author, category, price, quantity),
        )
        conn.commit()
        cur.close()
        conn.close()

        flash("Book added successfully!", "success")
        return redirect(url_for("manage_books"))

    # For GET request, just show the form
    return render_template("add_book.html")


@app.route("/admin/books/update/<int:book_id>", methods=["GET", "POST"])
@admin_required
def update_book(book_id):
    """
    Handles editing an existing book.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        category = request.form.get("category")
        price = request.form.get("price")
        quantity = request.form.get("quantity")

        cur.execute(
            """
            UPDATE books 
            SET title=%s, author=%s, category=%s, price=%s, quantity=%s
            WHERE book_id=%s
        """,
            (title, author, category, price, quantity, book_id),
        )
        conn.commit()
        cur.close()
        conn.close()
        flash("Book updated successfully!", "success")
        return redirect(url_for("manage_books"))

    # For GET request, fetch the book and show the form
    cur.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
    book = cur.fetchone()
    cur.close()
    conn.close()

    if not book:
        flash("Book not found.", "danger")
        return redirect(url_for("manage_books"))

    return render_template("update_book.html", book=book)


@app.route("/admin/books/delete/<int:book_id>", methods=["POST"])
@admin_required
def delete_book(book_id):
    """
    Deletes a book from the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
    conn.commit()
    cur.close()
    conn.close()

    flash("Book deleted successfully!", "success")
    return redirect(url_for("manage_books"))


@app.route("/reports", endpoint="reports")
def reports():
    # prepare data for the template as needed
    return render_template("reports.html")


# ------------------- RUN SERVER ------------------- #

if __name__ == "__main__":
    app.run(debug=True, host="", port=5000)
