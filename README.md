# MediRecord — Digital Patient Medical Records Management System

This application is an educational prototype and is not intended for production clinical use.

MediRecord is a beginner-friendly hospital/clinic web app for storing and retrieving structured patient records. Staff can register patients, keep medical history, record visits and prescriptions, search records, edit demographics, archive records instead of deleting them, and view a database-driven dashboard.

Do not use real patient information. Demo records in this project are fictional.

---

## 1. Project overview

The system demonstrates how healthcare information can be stored, validated, updated, and presented through a simple Flask + SQLite web interface.

It is a **healthcare database + CRUD project**, not an AI diagnosis system.

---

## 2. Features

- Staff login with hashed passwords and Flask sessions
- Role-based access: Admin, Doctor, Receptionist
- Patient registration and search (Patient ID, name, phone)
- Patient profile with demographics, history, visits, and prescriptions
- Add medical history, visits, and prescriptions
- Edit patient information (Patient ID cannot be changed)
- Archive / restore instead of permanent delete
- Dashboard statistics from live database queries
- Simple audit trail for important actions
- Client-side and server-side validation

---

## 3. Technology stack

- Frontend: HTML5, CSS3, Vanilla JavaScript, Bootstrap 5, Chart.js
- Backend: Python 3, Flask
- Database: SQLite (structured so MySQL can replace it later with connection changes)
- Security: Flask sessions, Werkzeug password hashing, parameterized SQL, validation, role checks

---

## 4. Folder structure

```text
patient-record-system/
├── app.py
├── database.py
├── requirements.txt
├── README.md
├── database/
│   └── hospital.db
├── templates/
│   ├── login.html
│   ├── dashboard.html
│   ├── patients.html
│   ├── add_patient.html
│   ├── edit_patient.html
│   ├── patient_details.html
│   ├── add_history.html
│   ├── add_visit.html
│   ├── add_prescription.html
│   ├── visits.html
│   ├── visit_details.html
│   ├── error.html
│   └── base.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── script.js
```

---

## 5. Database design

### users

Staff login accounts: `id`, `username`, `password_hash`, `role`, `created_at`.

Roles: Admin, Doctor, Receptionist. Passwords are never stored in plain text.

### patients

Demographics: `patient_id` (unique, example `P1001`), name, date of birth, gender, phone, address, blood group, emergency contact, `is_active`, timestamps.

### medical_history

Linked to `patients.id`. One patient can have many history rows.

### visits

Linked to `patients.id`. One patient can have many visits.

### prescriptions

Linked to `visits.id`. One visit can have many prescriptions.

### audit_logs

Tracks important actions: who did what, on which entity, and when.

---

## 6. Entity relationships

```text
Patient
├── Medical History (1 → many)
└── Visits (1 → many)
    └── Prescriptions (1 → many)
```

SQLite foreign keys are enabled.

---

## 7. Installation instructions

Use Python 3.10 or later.

```bash
cd patient-record-system
python -m venv venv
```

---

## 8. Virtual environment setup

**Windows (PowerShell):**

```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**

```bat
venv\Scripts\activate.bat
```

**macOS / Linux:**

```bash
source venv/bin/activate
```

---

## 9. requirements.txt installation

```bash
pip install -r requirements.txt
```

---

## 10. Database initialization

Tables, demo staff accounts, and DEMO DATA are created automatically when the app starts (`python app.py`).

The SQLite file is created at `database/hospital.db`.

If you need a fresh database, delete `database/hospital.db` and start the app again.

---

## 11. How to run Flask

```bash
python app.py
```

Then open [http://127.0.0.1:5000](http://127.0.0.1:5000) in a browser.

---

## 12. Demo login credentials

These accounts are created on first startup. Change them before any real use.

| Role | Username | Password |
| --- | --- | --- |
| Admin | `admin` | `admin123` |
| Doctor | `doctor` | `doctor123` |
| Receptionist | `receptionist` | `reception123` |

Sample DEMO DATA patients (fictional):

- P1001 — Lakshmi
- P1002 — Ravi
- P1003 — Anjali

---

## 13. CRUD explanation

- **Create:** register patient, add history, add visit, add prescription
- **Read:** list/search patients, view profile, visits, prescriptions, dashboard counts
- **Update:** edit patient demographics
- **Archive (safer than delete):** set `is_active = 0`. Archived patients are hidden from the normal active list. Admin can restore a record.

Healthcare records are not permanently deleted in this demonstration.

---

## 14. Role-based access explanation

**Admin:** dashboard, view/add/edit patients, archive/restore, visits, prescriptions, medical history.

**Doctor:** view patients, add/view medical history, add/view visits, add prescriptions. Cannot register, edit, archive, or restore patients.

**Receptionist:** register patients, search/view patients, edit basic patient information, view visit information. Cannot add clinical history, visits, or prescriptions.

---

## 15. Security considerations

- Passwords hashed with Werkzeug
- Flask session after successful login
- Login required for protected pages
- Role checks on sensitive routes
- Parameterized SQL queries (user input is not concatenated into SQL)
- Server-side validation always runs, even if the browser also validates
- Friendly error pages instead of stack traces for 404/500

This is still a student prototype. It is **not** HIPAA-compliant and is **not** suitable for real clinical data.

---

## 16. Future improvements

- Replace SQLite with MySQL
- Stronger session secret stored in environment variables
- Pagination for large patient lists
- Printable visit summaries
- Password reset for staff accounts
- More detailed audit log viewer for Admin

---

## 17. Educational-use disclaimer

This application is an educational prototype and is not intended for production clinical use.

It does not claim HIPAA, DPDP, or other legal compliance. Do not store real patient records in this system.
