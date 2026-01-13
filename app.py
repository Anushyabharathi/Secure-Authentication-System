from flask import Flask, render_template, request, redirect, session
import sqlite3, bcrypt
import os

app = Flask(__name__)
app.secret_key = "secret123"  # Required for session

DB_NAME = "users.db"

# ---------- Helper Functions ----------
def get_db():
    return sqlite3.connect(DB_NAME)

def create_table():
    """Create users table if it does not exist"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    db.commit()
    db.close()
    print("Database checked: 'users' table exists!")

# ---------- Routes ----------
@app.route("/")
def home():
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    message = ""
    if request.method == "POST":
        username = request.form["username"]
        password = bcrypt.hashpw(request.form["password"].encode(), bcrypt.gensalt())
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            db.commit()
            db.close()
            return redirect("/login")
        except sqlite3.IntegrityError:
            message = "⚠ Username already exists"
    return render_template("register.html", message=message)

@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"].encode()
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT password FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        db.close()
        if user and bcrypt.checkpw(password, user[0]):
            session["user"] = username
            return redirect("/dashboard")
        else:
            message = "❌ Invalid username or password"
    return render_template("login.html", message=message)

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    return render_template("dashboard.html", user=session["user"])

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

# ---------- Run App ----------
if __name__ == "__main__":
    # ✅ Ensure DB and table exist before starting app
    create_table()
    app.run(debug=True)
