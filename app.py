"""
CampusCare — College Complaint & Service Management System
============================================================
A mini-project built with Flask (Python), SQLite (SQL) and a
hand-rolled HTML/CSS/JS frontend. No external APIs, no JS
frameworks, no payment gateway — pure fundamentals.

Run:
    python app.py
Then open:
    http://127.0.0.1:5000
"""

import os
import sqlite3
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "campuscare.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")

app = Flask(__name__)
app.secret_key = "campuscare-dev-secret-key-change-me"  # fine for a college mini-project

CATEGORIES = ["Hostel", "Academic", "Canteen", "Infrastructure", "IT / Wi-Fi", "Library", "Transport", "Other"]
STATUSES = ["Pending", "In Progress", "Resolved", "Rejected"]


# ---------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create tables (if missing) and seed one default admin account."""
    first_time = not os.path.exists(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())

    # Seed a default admin so the project is runnable out of the box
    admin_email = "admin@campuscare.edu"
    existing = conn.execute("SELECT id FROM users WHERE email = ?", (admin_email,)).fetchone()
    if not existing:
        conn.execute(
            "INSERT INTO users (name, email, password, role, department) VALUES (?, ?, ?, ?, ?)",
            ("Campus Admin", admin_email, generate_password_hash("admin123"), "admin", "Administration"),
        )
    conn.commit()
    conn.close()
    if first_time:
        print(">> Fresh database created at", DB_PATH)
    print(">> Default admin login  ->  admin@campuscare.edu / admin123")


# ---------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------
def current_user():
    if "user_id" not in session:
        return None
    db = get_db()
    return db.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()


def login_required(role=None):
    def decorator(fn):
        from functools import wraps

        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = current_user()
            if user is None:
                flash("Please login first, yaar!", "error")
                return redirect(url_for("login"))
            if role and user["role"] != role:
                flash("You are not allowed to access that page.", "error")
                return redirect(url_for("index"))
            return fn(*args, **kwargs)

        return wrapper

    return decorator


@app.context_processor
def inject_user():
    return {"logged_in_user": current_user()}


# ---------------------------------------------------------------
# Public routes
# ---------------------------------------------------------------
@app.route("/")
def index():
    if session.get("user_id"):
        user = current_user()
        return redirect(url_for("admin_dashboard") if user["role"] == "admin" else url_for("student_dashboard"))
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        enrollment_no = request.form.get("enrollment_no", "").strip()
        department = request.form.get("department", "").strip()

        if not name or not email or not password:
            flash("Sab fields fill karo, kuch bhi khaali mat chhodo!", "error")
            return redirect(url_for("register"))
        if password != confirm:
            flash("Passwords match nahi kar rahe. Try again.", "error")
            return redirect(url_for("register"))
        if len(password) < 6:
            flash("Password kam se kam 6 characters ka rakho.", "error")
            return redirect(url_for("register"))

        db = get_db()
        existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            flash("Ye email already registered hai. Login kar lo.", "error")
            return redirect(url_for("register"))

        db.execute(
            "INSERT INTO users (name, email, password, role, enrollment_no, department) VALUES (?, ?, ?, 'student', ?, ?)",
            (name, email, generate_password_hash(password), enrollment_no, department),
        )
        db.commit()
        flash("Account ban gaya! Ab login karo.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if user is None or not check_password_hash(user["password"], password):
            flash("Email ya password galat hai.", "error")
            return redirect(url_for("login"))

        session["user_id"] = user["id"]
        session["role"] = user["role"]
        flash(f"Welcome back, {user['name']}!", "success")
        return redirect(url_for("admin_dashboard") if user["role"] == "admin" else url_for("student_dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out. See you soon!", "success")
    return redirect(url_for("index"))


# ---------------------------------------------------------------
# Student routes
# ---------------------------------------------------------------
@app.route("/student/dashboard")
@login_required(role="student")
def student_dashboard():
    db = get_db()
    user = current_user()
    complaints = db.execute(
        "SELECT * FROM complaints WHERE student_id = ? ORDER BY created_at DESC", (user["id"],)
    ).fetchall()

    total = len(complaints)
    pending = sum(1 for c in complaints if c["status"] == "Pending")
    in_progress = sum(1 for c in complaints if c["status"] == "In Progress")
    resolved = sum(1 for c in complaints if c["status"] == "Resolved")

    return render_template(
        "student_dashboard.html",
        complaints=complaints,
        categories=CATEGORIES,
        stats={"total": total, "pending": pending, "in_progress": in_progress, "resolved": resolved},
    )


@app.route("/student/submit", methods=["POST"])
@login_required(role="student")
def submit_complaint():
    user = current_user()
    title = request.form.get("title", "").strip()
    category = request.form.get("category", "Other")
    description = request.form.get("description", "").strip()
    priority = request.form.get("priority", "Medium")

    if not title or not description:
        flash("Title aur description dono zaroori hain.", "error")
        return redirect(url_for("student_dashboard"))

    db = get_db()
    db.execute(
        "INSERT INTO complaints (student_id, title, category, description, priority) VALUES (?, ?, ?, ?, ?)",
        (user["id"], title, category, description, priority),
    )
    db.commit()
    flash("Complaint submit ho gayi! Admin jaldi dekhega.", "success")
    return redirect(url_for("student_dashboard"))


@app.route("/student/delete/<int:complaint_id>", methods=["POST"])
@login_required(role="student")
def delete_complaint(complaint_id):
    user = current_user()
    db = get_db()
    complaint = db.execute("SELECT * FROM complaints WHERE id = ?", (complaint_id,)).fetchone()
    if complaint is None or complaint["student_id"] != user["id"]:
        flash("Complaint nahi mili.", "error")
        return redirect(url_for("student_dashboard"))
    if complaint["status"] != "Pending":
        flash("Sirf Pending complaints delete ho sakti hain.", "error")
        return redirect(url_for("student_dashboard"))
    db.execute("DELETE FROM complaints WHERE id = ?", (complaint_id,))
    db.commit()
    flash("Complaint delete kar di.", "success")
    return redirect(url_for("student_dashboard"))


# ---------------------------------------------------------------
# Admin routes
# ---------------------------------------------------------------
@app.route("/admin/dashboard")
@login_required(role="admin")
def admin_dashboard():
    db = get_db()

    status_filter = request.args.get("status", "All")
    category_filter = request.args.get("category", "All")

    query = """
        SELECT complaints.*, users.name AS student_name, users.email AS student_email,
               users.enrollment_no AS student_enrollment
        FROM complaints
        JOIN users ON complaints.student_id = users.id
        WHERE 1=1
    """
    params = []
    if status_filter != "All":
        query += " AND complaints.status = ?"
        params.append(status_filter)
    if category_filter != "All":
        query += " AND complaints.category = ?"
        params.append(category_filter)
    query += " ORDER BY complaints.created_at DESC"

    complaints = db.execute(query, params).fetchall()

    all_complaints = db.execute("SELECT status FROM complaints").fetchall()
    total = len(all_complaints)
    pending = sum(1 for c in all_complaints if c["status"] == "Pending")
    in_progress = sum(1 for c in all_complaints if c["status"] == "In Progress")
    resolved = sum(1 for c in all_complaints if c["status"] == "Resolved")
    rejected = sum(1 for c in all_complaints if c["status"] == "Rejected")

    return render_template(
        "admin_dashboard.html",
        complaints=complaints,
        categories=CATEGORIES,
        statuses=STATUSES,
        status_filter=status_filter,
        category_filter=category_filter,
        stats={"total": total, "pending": pending, "in_progress": in_progress, "resolved": resolved, "rejected": rejected},
    )


@app.route("/admin/update/<int:complaint_id>", methods=["POST"])
@login_required(role="admin")
def update_complaint(complaint_id):
    new_status = request.form.get("status")
    remarks = request.form.get("admin_remarks", "").strip()

    if new_status not in STATUSES:
        flash("Invalid status.", "error")
        return redirect(url_for("admin_dashboard"))

    db = get_db()
    db.execute(
        "UPDATE complaints SET status = ?, admin_remarks = ?, updated_at = ? WHERE id = ?",
        (new_status, remarks, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), complaint_id),
    )
    db.commit()
    flash("Complaint status update kar diya!", "success")
    return redirect(url_for("admin_dashboard"))


# ---------------------------------------------------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
