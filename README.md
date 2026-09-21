# CampusCare 🎓

**College Complaint & Service Management System** — an ICT mini-project.

Students report campus problems (hostel, academic, canteen, IT/Wi-Fi, etc.), admins review and update the status until it's resolved. Built with plain fundamentals — no frameworks, no external APIs, no payment gateway.

## Tech Stack

| Layer      | Technology                      |
|------------|----------------------------------|
| Frontend   | HTML5, CSS3, Vanilla JavaScript |
| Backend    | Python (Flask)                  |
| Database   | SQL (SQLite)                    |
| Templating | Jinja2 (comes with Flask)       |

No React, no Firebase, no external APIs, no payment system — just HTML + CSS + JS + Python + SQL, exactly as required.

## Features

- **Student side**
  - Sign up / login with a hashed password
  - Submit a complaint (title, category, priority, description)
  - Track status live: `Pending → In Progress → Resolved / Rejected`
  - See admin remarks on each complaint
  - Delete a complaint while it's still `Pending`
- **Admin side**
  - Default seeded admin account (see below)
  - View every complaint from every student
  - Filter by status and category
  - Update status and add a remark
  - Dashboard stat cards (total / pending / in progress / resolved / rejected)
- Comic-book / pop-art visual theme (Bangers + Oswald + Inter fonts, bold borders, hard drop-shadows)
- Fully responsive (mobile, tablet, desktop)
- Flash messages for feedback (login errors, success actions)

## Project Structure

```
CampusCare/
├── app.py                  # Flask app: routes, auth, business logic
├── schema.sql               # SQL schema (users + complaints tables)
├── requirements.txt
├── campuscare.db             # auto-created on first run (SQLite)
├── static/
│   ├── css/style.css         # comic-book theme
│   └── js/script.js          # vanilla JS (flash auto-dismiss, validation)
└── templates/
    ├── base.html              # shared header/footer/layout
    ├── index.html              # landing page
    ├── login.html
    ├── register.html
    ├── student_dashboard.html
    └── admin_dashboard.html
```
## Default Admin Login

```
Email:    admin@campuscare.edu
Password: admin123
```

Students register their own accounts from the **Sign Up** page.

## Database Schema (short version)

**users** — `id, name, email, password (hashed), role (student/admin), enrollment_no, department, created_at`

**complaints** — `id, student_id (FK → users), title, category, description, priority, status, admin_remarks, created_at, updated_at`

## Possible Future Enhancements

- Email notifications on status change
- Complaint attachments (image upload)
- Admin analytics charts
- Multiple admin roles / departments
