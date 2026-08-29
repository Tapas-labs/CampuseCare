-- ============================================================
-- CampusCare : College Complaint & Service Management System
-- Database Schema (SQLite)
-- ============================================================

DROP TABLE IF EXISTS complaints;
DROP TABLE IF EXISTS users;

-- Users table: stores both students and admins
CREATE TABLE users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE,
    password      TEXT NOT NULL,                 -- hashed password (never plain text)
    role          TEXT NOT NULL DEFAULT 'student' CHECK (role IN ('student', 'admin')),
    enrollment_no TEXT,                           -- only relevant for students
    department    TEXT,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Complaints table: every complaint raised by a student
CREATE TABLE complaints (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id    INTEGER NOT NULL,
    title         TEXT NOT NULL,
    category      TEXT NOT NULL,                  -- Hostel, Academic, Canteen, Infrastructure, IT/Wifi, Other
    description   TEXT NOT NULL,
    priority      TEXT NOT NULL DEFAULT 'Medium' CHECK (priority IN ('Low', 'Medium', 'High')),
    status        TEXT NOT NULL DEFAULT 'Pending' CHECK (status IN ('Pending', 'In Progress', 'Resolved', 'Rejected')),
    admin_remarks TEXT,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Default admin account  ->  email: admin@campuscare.edu | password: admin123
-- (password below is a werkzeug pbkdf2 hash generated in seed.py, inserted at first run)
