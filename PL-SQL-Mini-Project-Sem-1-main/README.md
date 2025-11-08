Online Bookstore Management System (Flask + PostgreSQL)This is your complete, working web application built with Flask and connected to your PostgreSQL database.Project StructurePlace all the files I've provided into the following folder structure:

```
online-bookstore/
├── app.py                  <-- The main Flask backend (provided)
├── database/
│   ├── schema.sql            <-- Your original file
│   ├── data.sql              <-- Your original file
│   ├── procedures.sql        <-- Your original file
│   ├── triggers.sql          <-- Your original file
├── templates/
│   ├── base.html             <-- Provided (Styled with Tailwind)
│   ├── _flashes.html         <-- Provided (For alerts)
│   ├── login.html            <-- Provided (Styled with Tailwind)
│   ├── register.html         <-- Provided (Styled with Tailwind)
│   ├── profile.html          <-- Provided (Styled with Tailwind)
│   ├── book_management.html  <-- Provided (Styled with Tailwind)
│   ├── add_book.html         <-- Provided (Styled with Tailwind)
│   ├── update_book.html      <-- Provided (Styled with Tailwind)
│   ├── cart.html             <-- Provided (Styled with Tailwind)
└── static/
    └── css/
        └── style.css         <-- (Can be empty, just good practice)
```

How to Run Your ProjectSet up PostgreSQL:Make sure your PostgreSQL server is running.Create the database: CREATE DATABASE bookstore_db;Connect to your new database (\c bookstore_db) and run your SQL files in this order:schema.sql (to create tables)data.sql (to add sample data)procedures.sql (to add functions)triggers.sql (to add triggers)Update Database Connection (VERY IMPORTANT):Open app.py.Find the get_db_connection() function.Change the password from "Anubhav@2024?" to your actual PostgreSQL password.Install Python Libraries:Make sure you have Python and pip installed.pip install Flaskpip install psycopg2-binaryRun the Application:Open your terminal in the online-bookstore/ directory (the same folder as app.py).Type: python app.pyYour website will be running at http://127.0.0.1:5000 (or http://localhost:5000).Test Your Website:Open http://localhost:5000 in your browser.Test Customer Login: anubhav@example.com / anubhav123Test Admin Login: admin@bookstore.com / admin123