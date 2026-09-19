"""
MediRecord — Digital Patient Medical Records Management System.

Educational prototype. Not intended for production clinical use.
"""

from datetime import date, datetime
from functools import wraps
import re
import sqlite3

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash

import database as db

app = Flask(__name__)
app.secret_key = "medirecord-student-demo-secret"

VALID_GENDERS = {"Male", "Female", "Other", "Prefer not to say"}
VALID_BLOOD_GROUPS = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", ""}
PATIENT_ID_PATTERN = re.compile(r"^P\d{4,}$")
PHONE_PATTERN = re.compile(r"^(?:\+91[-\s]?)?[6-9]\d{9}$")


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def roles_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in to continue.", "warning")
                return redirect(url_for("login"))
            if session.get("role") not in roles:
                flash("You do not have permission to perform this action.", "danger")
                return redirect(url_for("dashboard"))
            return view(*args, **kwargs)

        return wrapped

    return decorator


def current_role():
    return session.get("role")


def can_add_patient():
    return current_role() in ("Admin", "Receptionist")


def can_edit_patient():
    return current_role() in ("Admin", "Receptionist")


def can_archive():
    return current_role() == "Admin"


def can_add_clinical():
    return current_role() in ("Admin", "Doctor")


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def clean(value):
    return (value or "").strip()


def calculate_age(dob_text):
    try:
        dob = datetime.strptime(dob_text, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None
    today = date.today()
    years = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return years


def validate_phone(phone, required=True, field_name="Phone"):
    phone = clean(phone)
    if not phone:
        return None if not required else f"{field_name} is required."
    if not PHONE_PATTERN.match(phone):
        return f"{field_name} must be a valid 10-digit Indian mobile number."
    return None


def validate_patient_form(form, is_edit=False):
    errors = []
    data = {
        "patient_id": clean(form.get("patient_id")).upper(),
        "name": clean(form.get("name")),
        "date_of_birth": clean(form.get("date_of_birth")),
        "gender": clean(form.get("gender")),
        "phone": clean(form.get("phone")),
        "address": clean(form.get("address")),
        "blood_group": clean(form.get("blood_group")),
        "emergency_contact": clean(form.get("emergency_contact")),
    }

    if not is_edit:
        if not data["patient_id"]:
            errors.append("Patient ID is required.")
        elif not PATIENT_ID_PATTERN.match(data["patient_id"]):
            errors.append("Patient ID must look like P1001.")
        elif db.get_patient_by_code(data["patient_id"]):
            errors.append("Patient ID already exists.")

    if not data["name"] or len(data["name"]) < 2:
        errors.append("Full name is required (at least 2 characters).")
    elif data["name"].replace(" ", "").isdigit():
        errors.append("Name cannot contain only numbers.")

    if not data["date_of_birth"]:
        errors.append("Date of birth is required.")
    else:
        try:
            dob = datetime.strptime(data["date_of_birth"], "%Y-%m-%d").date()
            if dob > date.today():
                errors.append("Date of birth cannot be in the future.")
        except ValueError:
            errors.append("Date of birth must be a valid date.")

    if data["gender"] not in VALID_GENDERS:
        errors.append("Please select a valid gender.")

    phone_error = validate_phone(data["phone"], required=True, field_name="Phone")
    if phone_error:
        errors.append(phone_error)

    if data["blood_group"] not in VALID_BLOOD_GROUPS:
        errors.append("Please select a valid blood group.")

    if data["emergency_contact"]:
        emergency_error = validate_phone(
            data["emergency_contact"], required=False, field_name="Emergency contact"
        )
        if emergency_error:
            errors.append(emergency_error)

    return data, errors


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = clean(request.form.get("username"))
        password = request.form.get("password") or ""
        user = db.get_user_by_username(username)
        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid username or password.", "danger")
            return render_template("login.html")

        session.clear()
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["role"] = user["role"]
        db.add_audit_log(user["id"], f"{user['username']} logged in", "user", user["id"])
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    user_id = session.get("user_id")
    username = session.get("username")
    session.clear()
    if user_id:
        db.add_audit_log(user_id, f"{username} logged out", "user", user_id)
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    stats, recent, visits_by_day = db.get_dashboard_stats()
    chart_labels = [row["label"] for row in visits_by_day]
    chart_values = [row["total"] for row in visits_by_day]
    return render_template(
        "dashboard.html",
        stats=stats,
        recent=recent,
        chart_labels=chart_labels,
        chart_values=chart_values,
    )


@app.route("/patients")
@login_required
def patients():
    query = clean(request.args.get("q"))
    include_archived = current_role() == "Admin" and request.args.get("archived") == "1"
    results = db.search_patients(query, include_archived=include_archived)
    return render_template(
        "patients.html",
        patients=results,
        query=query,
        include_archived=include_archived,
        can_edit=can_edit_patient(),
        can_archive=can_archive(),
    )


@app.route("/patients/add", methods=["GET", "POST"])
@roles_required("Admin", "Receptionist")
def add_patient():
    if request.method == "POST":
        data, errors = validate_patient_form(request.form, is_edit=False)
        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("add_patient.html", form=data)
        try:
            db.create_patient(data)
        except sqlite3.IntegrityError:
            flash("Patient ID already exists.", "danger")
            return render_template("add_patient.html", form=data)
        except sqlite3.Error:
            flash("Unable to save the patient record. Please try again.", "danger")
            return render_template("add_patient.html", form=data)

        db.add_audit_log(
            session["user_id"],
            f"{session['username']} registered patient {data['patient_id']}",
            "patient",
            data["patient_id"],
        )
        flash("Patient registered successfully.", "success")
        return redirect(url_for("patient_details", patient_id=data["patient_id"]))

    return render_template("add_patient.html", form={})


@app.route("/patient/<patient_id>")
@login_required
def patient_details(patient_id):
    patient = db.get_patient_by_code(patient_id)
    if not patient:
        flash("Patient record not found.", "danger")
        return redirect(url_for("patients"))

    history = db.get_medical_history(patient["id"])
    visits = db.get_visits_for_patient(patient["id"])
    prescriptions = db.get_prescriptions_for_patient(patient["id"])
    return render_template(
        "patient_details.html",
        patient=patient,
        age=calculate_age(patient["date_of_birth"]),
        history=history,
        visits=visits,
        prescriptions=prescriptions,
        can_edit=can_edit_patient(),
        can_archive=can_archive(),
        can_add_clinical=can_add_clinical(),
    )


@app.route("/patient/<patient_id>/edit", methods=["GET", "POST"])
@roles_required("Admin", "Receptionist")
def edit_patient(patient_id):
    patient = db.get_patient_by_code(patient_id)
    if not patient:
        flash("Patient record not found.", "danger")
        return redirect(url_for("patients"))

    if request.method == "POST":
        data, errors = validate_patient_form(request.form, is_edit=True)
        data["patient_id"] = patient["patient_id"]
        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("edit_patient.html", patient=patient, form=data)
        try:
            db.update_patient(patient_id, data)
        except sqlite3.Error:
            flash("Unable to update the patient record. Please try again.", "danger")
            return render_template("edit_patient.html", patient=patient, form=data)

        db.add_audit_log(
            session["user_id"],
            f"{session['username']} updated patient {patient_id}",
            "patient",
            patient_id,
        )
        flash("Patient information updated successfully.", "success")
        return redirect(url_for("patient_details", patient_id=patient_id))

    form = dict(patient)
    return render_template("edit_patient.html", patient=patient, form=form)


@app.route("/patient/<patient_id>/archive", methods=["POST"])
@roles_required("Admin")
def archive_patient(patient_id):
    patient = db.get_patient_by_code(patient_id)
    if not patient:
        flash("Patient record not found.", "danger")
        return redirect(url_for("patients"))
    db.set_patient_active(patient_id, False)
    db.add_audit_log(
        session["user_id"],
        f"{session['username']} archived patient {patient_id}",
        "patient",
        patient_id,
    )
    flash("Patient archived. The record was deactivated, not deleted.", "success")
    return redirect(url_for("patients"))


@app.route("/patient/<patient_id>/restore", methods=["POST"])
@roles_required("Admin")
def restore_patient(patient_id):
    patient = db.get_patient_by_code(patient_id)
    if not patient:
        flash("Patient record not found.", "danger")
        return redirect(url_for("patients"))
    db.set_patient_active(patient_id, True)
    db.add_audit_log(
        session["user_id"],
        f"{session['username']} restored patient {patient_id}",
        "patient",
        patient_id,
    )
    flash("Patient record restored.", "success")
    return redirect(url_for("patient_details", patient_id=patient_id))


@app.route("/patient/<patient_id>/history/add", methods=["GET", "POST"])
@roles_required("Admin", "Doctor")
def add_history(patient_id):
    patient = db.get_patient_by_code(patient_id)
    if not patient:
        flash("Patient record not found.", "danger")
        return redirect(url_for("patients"))

    if request.method == "POST":
        condition = clean(request.form.get("condition"))
        diagnosis = clean(request.form.get("diagnosis"))
        notes = clean(request.form.get("notes"))
        if not condition:
            flash("Please enter all required fields.", "danger")
            return render_template("add_history.html", patient=patient)
        db.add_medical_history(
            patient["id"],
            {"condition": condition, "diagnosis": diagnosis, "notes": notes},
        )
        db.add_audit_log(
            session["user_id"],
            f"{session['username']} added medical history for {patient_id}",
            "medical_history",
            patient_id,
        )
        flash("Medical history saved.", "success")
        return redirect(url_for("patient_details", patient_id=patient_id))

    return render_template("add_history.html", patient=patient)


@app.route("/visits")
@login_required
def visits():
    return render_template("visits.html", visits=db.get_all_visits())


@app.route("/patient/<patient_id>/visit/add", methods=["GET", "POST"])
@roles_required("Admin", "Doctor")
def add_visit(patient_id):
    patient = db.get_patient_by_code(patient_id)
    if not patient:
        flash("Patient record not found.", "danger")
        return redirect(url_for("patients"))

    if request.method == "POST":
        doctor = clean(request.form.get("doctor"))
        visit_date = clean(request.form.get("visit_date"))
        symptoms = clean(request.form.get("symptoms"))
        diagnosis = clean(request.form.get("diagnosis"))
        notes = clean(request.form.get("notes"))
        errors = []
        if not doctor:
            errors.append("Doctor name is required.")
        if not visit_date:
            errors.append("Visit date is required.")
        else:
            try:
                datetime.strptime(visit_date, "%Y-%m-%d")
            except ValueError:
                errors.append("Visit date must be a valid date.")
        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("add_visit.html", patient=patient)
        visit_id = db.add_visit(
            patient["id"],
            {
                "doctor": doctor,
                "visit_date": visit_date,
                "symptoms": symptoms,
                "diagnosis": diagnosis,
                "notes": notes,
            },
        )
        db.add_audit_log(
            session["user_id"],
            f"{session['username']} added visit for {patient_id}",
            "visit",
            visit_id,
        )
        flash("Visit saved.", "success")
        return redirect(url_for("visit_details", visit_id=visit_id))

    return render_template("add_visit.html", patient=patient, today=date.today().isoformat())


@app.route("/visit/<int:visit_id>")
@login_required
def visit_details(visit_id):
    visit = db.get_visit(visit_id)
    if not visit:
        flash("Visit record not found.", "danger")
        return redirect(url_for("visits"))
    prescriptions = db.get_prescriptions_for_visit(visit_id)
    return render_template(
        "visit_details.html",
        visit=visit,
        prescriptions=prescriptions,
        can_add_clinical=can_add_clinical(),
    )


@app.route("/visit/<int:visit_id>/prescription/add", methods=["GET", "POST"])
@roles_required("Admin", "Doctor")
def add_prescription(visit_id):
    visit = db.get_visit(visit_id)
    if not visit:
        flash("Visit record not found.", "danger")
        return redirect(url_for("visits"))

    if request.method == "POST":
        medicine = clean(request.form.get("medicine"))
        if not medicine:
            flash("Please enter all required fields.", "danger")
            return render_template("add_prescription.html", visit=visit)
        db.add_prescription(
            visit_id,
            {
                "medicine": medicine,
                "dosage": clean(request.form.get("dosage")),
                "frequency": clean(request.form.get("frequency")),
                "duration": clean(request.form.get("duration")),
                "instructions": clean(request.form.get("instructions")),
            },
        )
        db.add_audit_log(
            session["user_id"],
            f"{session['username']} added prescription for visit {visit_id}",
            "prescription",
            visit_id,
        )
        flash("Prescription added.", "success")
        return redirect(url_for("visit_details", visit_id=visit_id))

    return render_template("add_prescription.html", visit=visit)


@app.errorhandler(404)
def not_found(_error):
    return render_template("error.html", code=404, message="Page not found."), 404


@app.errorhandler(500)
def server_error(_error):
    return render_template(
        "error.html",
        code=500,
        message="Something went wrong. Please try again.",
    ), 500


@app.context_processor
def inject_permissions():
    return {
        "can_add_patient": can_add_patient() if session.get("user_id") else False,
        "can_edit_patient": can_edit_patient() if session.get("user_id") else False,
        "can_archive": can_archive() if session.get("user_id") else False,
        "can_add_clinical": can_add_clinical() if session.get("user_id") else False,
    }


if __name__ == "__main__":
    db.init_db(seed_demo=True)
    app.run(debug=True)
