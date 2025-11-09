from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DB_NAME = "books.db"


# --- Initialize Database ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    year INTEGER NOT NULL
                )"""
    )
    conn.commit()
    conn.close()


# --- Home Page: List All Books ---
@app.route("/")
def index():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM books")
    books = c.fetchall()
    conn.close()
    return render_template("index.html", books=books)


# --- Add Book ---
@app.route("/add", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        year = request.form["year"]

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(
            "INSERT INTO books (title, author, year) VALUES (?, ?, ?)",
            (title, author, year),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    return render_template("add_book.html")


# --- Edit Book ---
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_book(id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM books WHERE id=?", (id,))
    book = c.fetchone()
    conn.close()

    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        year = request.form["year"]

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(
            "UPDATE books SET title=?, author=?, year=? WHERE id=?",
            (title, author, year, id),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    return render_template("edit_book.html", book=book)


# --- Delete Book ---
@app.route("/delete/<int:id>")
def delete_book(id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM books WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
