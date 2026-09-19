"""
MediRecord database helpers.

SQLite is used for the student project. Queries are parameterized so the
same functions can later be pointed at MySQL with only connection changes.
"""

import os
import sqlite3
from datetime import datetime

from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, "database")
DATABASE_PATH = os.path.join(DATABASE_DIR, "hospital.db")


def get_connection():
    """Open a SQLite connection with foreign keys enabled."""
    os.makedirs(DATABASE_DIR, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(seed_demo=True):
    """Create tables, default staff accounts, and optional DEMO DATA."""
    os.makedirs(DATABASE_DIR, exist_ok=True)
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at DATETIME
        );

        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            date_of_birth DATE NOT NULL,
            gender TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT,
            blood_group TEXT,
            emergency_contact TEXT,
            is_active INTEGER DEFAULT 1,
            created_at DATETIME,
            updated_at DATETIME
        );

        CREATE TABLE IF NOT EXISTS medical_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            condition TEXT NOT NULL,
            diagnosis TEXT,
            notes TEXT,
            created_at DATETIME,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        );

        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor TEXT NOT NULL,
            visit_date DATE NOT NULL,
            symptoms TEXT,
            diagnosis TEXT,
            notes TEXT,
            created_at DATETIME,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        );

        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            visit_id INTEGER NOT NULL,
            medicine TEXT NOT NULL,
            dosage TEXT,
            frequency TEXT,
            duration TEXT,
            instructions TEXT,
            created_at DATETIME,
            FOREIGN KEY (visit_id) REFERENCES visits(id)
        );

        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            entity_type TEXT,
            entity_id TEXT,
            timestamp DATETIME,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
    )

    _ensure_user(cur, "admin", "admin123", "Admin")
    _ensure_user(cur, "doctor", "doctor123", "Doctor")
    _ensure_user(cur, "receptionist", "reception123", "Receptionist")

    if seed_demo:
        _seed_demo_data(cur)

    conn.commit()
    conn.close()


def _ensure_user(cur, username, password, role):
    existing = cur.execute(
        "SELECT id FROM users WHERE username = ?", (username,)
    ).fetchone()
    if existing:
        return
    cur.execute(
        """
        INSERT INTO users (username, password_hash, role, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (username, generate_password_hash(password), role, _now()),
    )


def _seed_demo_data(cur):
    """Insert clearly marked DEMO DATA. Never use real patient information."""
    if cur.execute("SELECT COUNT(*) AS c FROM patients").fetchone()["c"] > 0:
        return

    demo_patients = [
        (
            "P1001",
            "Lakshmi",
            "1998-04-12",
            "Female",
            "9876543210",
            "12 MG Road, Hyderabad",
            "O+",
            "9123456780",
        ),
        (
            "P1002",
            "Ravi",
            "1992-11-03",
            "Male",
            "9988776655",
            "45 Park Street, Chennai",
            "B+",
            "9001122334",
        ),
        (
            "P1003",
            "Anjali",
            "2001-07-21",
            "Female",
            "9090909090",
            "88 Lake View, Bengaluru",
            "A+",
            "9811122233",
        ),
    ]

    for row in demo_patients:
        cur.execute(
            """
            INSERT INTO patients (
                patient_id, name, date_of_birth, gender, phone, address,
                blood_group, emergency_contact, is_active, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
            """,
            (*row, _now(), _now()),
        )

    p1 = cur.execute("SELECT id FROM patients WHERE patient_id = 'P1001'").fetchone()["id"]
    p2 = cur.execute("SELECT id FROM patients WHERE patient_id = 'P1002'").fetchone()["id"]
    p3 = cur.execute("SELECT id FROM patients WHERE patient_id = 'P1003'").fetchone()["id"]

    history_rows = [
        (p1, "Seasonal allergy", "Allergic rhinitis", "DEMO DATA: pollen sensitivity"),
        (p2, "Hypertension", "Essential hypertension", "DEMO DATA: lifestyle advice given"),
        (p3, "Migraine", "Migraine without aura", "DEMO DATA: triggered by missed meals"),
    ]
    for row in history_rows:
        cur.execute(
            """
            INSERT INTO medical_history (patient_id, condition, diagnosis, notes, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (*row, _now()),
        )

    visit_rows = [
        (p1, "Dr. Kumar", "2026-09-18", "Fever, headache", "Viral fever", "DEMO DATA: rest and hydration"),
        (p2, "Dr. Mehta", "2026-09-19", "Dizziness", "Uncontrolled BP", "DEMO DATA: review medication"),
        (p3, "Dr. Kumar", "2026-09-17", "Headache, nausea", "Migraine", "DEMO DATA: dark room rest"),
    ]
    for row in visit_rows:
        cur.execute(
            """
            INSERT INTO visits (
                patient_id, doctor, visit_date, symptoms, diagnosis, notes, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (*row, _now()),
        )

    v1 = cur.execute(
        "SELECT id FROM visits WHERE patient_id = ? ORDER BY id LIMIT 1", (p1,)
    ).fetchone()["id"]
    v2 = cur.execute(
        "SELECT id FROM visits WHERE patient_id = ? ORDER BY id LIMIT 1", (p2,)
    ).fetchone()["id"]
    v3 = cur.execute(
        "SELECT id FROM visits WHERE patient_id = ? ORDER BY id LIMIT 1", (p3,)
    ).fetchone()["id"]

    prescriptions = [
        (v1, "Paracetamol", "500 mg", "2 times/day", "3 days", "After food"),
        (v1, "Cetirizine", "10 mg", "1 time/day", "5 days", "At night"),
        (v2, "Amlodipine", "5 mg", "1 time/day", "30 days", "Morning"),
        (v3, "Sumatriptan", "50 mg", "As needed", "1 day", "At onset of migraine"),
    ]
    for row in prescriptions:
        cur.execute(
            """
            INSERT INTO prescriptions (
                visit_id, medicine, dosage, frequency, duration, instructions, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (*row, _now()),
        )


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def add_audit_log(user_id, action, entity_type=None, entity_id=None):
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO audit_logs (user_id, action, entity_type, entity_id, timestamp)
        VALUES (?, ?, ?, ?, ?)
        """,
        (user_id, action, entity_type, str(entity_id) if entity_id is not None else None, _now()),
    )
    conn.commit()
    conn.close()


def get_user_by_username(username):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    return row


def get_dashboard_stats():
    conn = get_connection()
    today = datetime.now().strftime("%Y-%m-%d")
    stats = {
        "total_patients": conn.execute("SELECT COUNT(*) AS c FROM patients").fetchone()["c"],
        "active_patients": conn.execute(
            "SELECT COUNT(*) AS c FROM patients WHERE is_active = 1"
        ).fetchone()["c"],
        "today_visits": conn.execute(
            "SELECT COUNT(*) AS c FROM visits WHERE visit_date = ?", (today,)
        ).fetchone()["c"],
        "total_prescriptions": conn.execute(
            "SELECT COUNT(*) AS c FROM prescriptions"
        ).fetchone()["c"],
    }
    recent = conn.execute(
        """
        SELECT patient_id, name, gender, phone, created_at
        FROM patients
        WHERE is_active = 1
        ORDER BY id DESC
        LIMIT 5
        """
    ).fetchall()
    visits_by_day = conn.execute(
        """
        SELECT visit_date AS label, COUNT(*) AS total
        FROM visits
        GROUP BY visit_date
        ORDER BY visit_date DESC
        LIMIT 7
        """
    ).fetchall()
    conn.close()
    return stats, recent, list(reversed(visits_by_day))


def search_patients(query="", include_archived=False):
    conn = get_connection()
    like = f"%{query.strip()}%"
    sql = """
        SELECT * FROM patients
        WHERE (patient_id LIKE ? OR name LIKE ? OR phone LIKE ?)
    """
    params = [like, like, like]
    if not include_archived:
        sql += " AND is_active = 1"
    sql += " ORDER BY name"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return rows


def get_patient_by_code(patient_code):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM patients WHERE patient_id = ?", (patient_code,)
    ).fetchone()
    conn.close()
    return row


def get_patient_by_id(internal_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM patients WHERE id = ?", (internal_id,)).fetchone()
    conn.close()
    return row


def create_patient(data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO patients (
            patient_id, name, date_of_birth, gender, phone, address,
            blood_group, emergency_contact, is_active, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
        """,
        (
            data["patient_id"],
            data["name"],
            data["date_of_birth"],
            data["gender"],
            data["phone"],
            data.get("address") or None,
            data.get("blood_group") or None,
            data.get("emergency_contact") or None,
            _now(),
            _now(),
        ),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def update_patient(patient_code, data):
    conn = get_connection()
    conn.execute(
        """
        UPDATE patients
        SET name = ?, date_of_birth = ?, gender = ?, phone = ?, address = ?,
            blood_group = ?, emergency_contact = ?, updated_at = ?
        WHERE patient_id = ?
        """,
        (
            data["name"],
            data["date_of_birth"],
            data["gender"],
            data["phone"],
            data.get("address") or None,
            data.get("blood_group") or None,
            data.get("emergency_contact") or None,
            _now(),
            patient_code,
        ),
    )
    conn.commit()
    conn.close()


def set_patient_active(patient_code, is_active):
    conn = get_connection()
    conn.execute(
        "UPDATE patients SET is_active = ?, updated_at = ? WHERE patient_id = ?",
        (1 if is_active else 0, _now(), patient_code),
    )
    conn.commit()
    conn.close()


def get_medical_history(internal_patient_id):
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT * FROM medical_history
        WHERE patient_id = ?
        ORDER BY created_at DESC, id DESC
        """,
        (internal_patient_id,),
    ).fetchall()
    conn.close()
    return rows


def add_medical_history(internal_patient_id, data):
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO medical_history (patient_id, condition, diagnosis, notes, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            internal_patient_id,
            data["condition"],
            data.get("diagnosis") or None,
            data.get("notes") or None,
            _now(),
        ),
    )
    conn.commit()
    conn.close()


def get_visits_for_patient(internal_patient_id):
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT * FROM visits
        WHERE patient_id = ?
        ORDER BY visit_date DESC, id DESC
        """,
        (internal_patient_id,),
    ).fetchall()
    conn.close()
    return rows


def get_all_visits():
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT v.*, p.patient_id AS patient_code, p.name AS patient_name
        FROM visits v
        JOIN patients p ON p.id = v.patient_id
        ORDER BY v.visit_date DESC, v.id DESC
        """
    ).fetchall()
    conn.close()
    return rows


def get_visit(visit_id):
    conn = get_connection()
    row = conn.execute(
        """
        SELECT v.*, p.patient_id AS patient_code, p.name AS patient_name,
               p.gender, p.phone, p.date_of_birth, p.blood_group
        FROM visits v
        JOIN patients p ON p.id = v.patient_id
        WHERE v.id = ?
        """,
        (visit_id,),
    ).fetchone()
    conn.close()
    return row


def add_visit(internal_patient_id, data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO visits (
            patient_id, doctor, visit_date, symptoms, diagnosis, notes, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            internal_patient_id,
            data["doctor"],
            data["visit_date"],
            data.get("symptoms") or None,
            data.get("diagnosis") or None,
            data.get("notes") or None,
            _now(),
        ),
    )
    conn.commit()
    visit_id = cur.lastrowid
    conn.close()
    return visit_id


def get_prescriptions_for_visit(visit_id):
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT * FROM prescriptions
        WHERE visit_id = ?
        ORDER BY id
        """,
        (visit_id,),
    ).fetchall()
    conn.close()
    return rows


def get_prescriptions_for_patient(internal_patient_id):
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT pr.*, v.visit_date, v.doctor
        FROM prescriptions pr
        JOIN visits v ON v.id = pr.visit_id
        WHERE v.patient_id = ?
        ORDER BY v.visit_date DESC, pr.id DESC
        """,
        (internal_patient_id,),
    ).fetchall()
    conn.close()
    return rows


def add_prescription(visit_id, data):
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO prescriptions (
            visit_id, medicine, dosage, frequency, duration, instructions, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            visit_id,
            data["medicine"],
            data.get("dosage") or None,
            data.get("frequency") or None,
            data.get("duration") or None,
            data.get("instructions") or None,
            _now(),
        ),
    )
    conn.commit()
    conn.close()
