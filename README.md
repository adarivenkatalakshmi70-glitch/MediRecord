# MediRecord – Digital Patient Medical Records Management System

MediRecord is a web-based **Digital Patient Medical Records Management System** designed to help clinics and healthcare organizations digitally manage patient information, medical history, visits, diagnoses, and prescriptions in one centralized system.

The system replaces scattered paper-based records with a structured digital workflow, making patient information easier to store, search, update, and retrieve.

---

## 📌 Problem Statement

In small clinics and healthcare centers, patient information is often maintained using:

* Paper files
* Separate registers
* Manually maintained records
* Scattered patient documents

This can make it difficult to quickly find previous medical information, update records, and maintain organized patient histories.

MediRecord provides a centralized digital solution for managing these records.

---

## 🎯 Objectives

The main objectives of MediRecord are to:

* Digitally store patient information
* Maintain structured medical history
* Record patient visits and diagnoses
* Manage prescriptions
* Quickly search and retrieve patient records
* Provide role-based access for different healthcare staff
* Reduce dependency on paper-based records
* Maintain organized and structured healthcare data

---

## ✨ Key Features

### 👤 Patient Management

* Register new patients
* Generate a unique Patient ID
* Store patient demographic information
* Edit patient information
* Search patients
* View complete patient profiles
* Archive or restore patient records

### 🩺 Medical History

Doctors can maintain:

* Existing medical conditions
* Diagnoses
* Medical notes
* Historical health information

### 📅 Visit Management

Each patient can have multiple visits.

A visit can contain:

* Doctor name
* Visit date
* Symptoms
* Diagnosis
* Doctor notes

### 💊 Prescription Management

Doctors can add prescriptions related to a visit.

Prescription information includes:

* Medicine name
* Dosage
* Frequency
* Duration
* Instructions

### 🔐 Authentication & Roles

The system supports user authentication with different roles:

**Admin**

* Manage users
* Manage patients
* Access all records

**Doctor**

* View patient records
* Add medical history
* Add visits
* Add diagnoses
* Add prescriptions

**Receptionist**

* Register patients
* Search patients
* Update basic patient information
* Manage basic visit information

### 🛡️ Security

The application includes:

* Password hashing using Werkzeug
* Flask session-based authentication
* Role-based access control
* Server-side form validation
* Parameterized SQL queries
* Environment variables for sensitive configuration
* Protection against storing passwords as plain text

---

## 🛠️ Technology Stack

### Frontend

* HTML5
* CSS3
* JavaScript
* Bootstrap 5 *(optional)*

### Backend

* Python 3
* Flask

### Database

* SQLite for development/demo
* MySQL/PostgreSQL can be used for production

### Tools

* Visual Studio Code
* Git
* GitHub

### Deployment

* Render
* Gunicorn

---

## 🏗️ System Architecture

```text
             ┌──────────────────────┐
             │       User           │
             │ Doctor / Admin /     │
             │ Receptionist         │
             └──────────┬───────────┘
                        │
                        ▼
             ┌──────────────────────┐
             │     Frontend         │
             │ HTML / CSS / JS      │
             └──────────┬───────────┘
                        │
                        ▼
             ┌──────────────────────┐
             │      Flask           │
             │      Backend         │
             └──────────┬───────────┘
                        │
                        ▼
             ┌──────────────────────┐
             │      Database        │
             │   SQLite / MySQL     │
             └──────────────────────┘
```

---

## 🗄️ Database Design

MediRecord uses a relational database structure.

### Users

Stores application users and their roles.

| Field         | Description                   |
| ------------- | ----------------------------- |
| id            | Unique user ID                |
| username      | Unique username               |
| password_hash | Hashed password               |
| role          | Admin / Doctor / Receptionist |
| created_at    | Account creation time         |

### Patients

Stores basic patient information.

| Field             | Description           |
| ----------------- | --------------------- |
| id                | Internal patient ID   |
| patient_id        | Unique Patient ID     |
| name              | Patient name          |
| date_of_birth     | Date of birth         |
| gender            | Gender                |
| phone             | Phone number          |
| address           | Address               |
| blood_group       | Blood group           |
| emergency_contact | Emergency contact     |
| is_active         | Active/archive status |
| created_at        | Creation time         |
| updated_at        | Last update time      |

### Medical History

Stores previous medical conditions and diagnoses.

| Field      | Description          |
| ---------- | -------------------- |
| id         | History ID           |
| patient_id | Related patient      |
| condition  | Medical condition    |
| diagnosis  | Diagnosis            |
| notes      | Additional notes     |
| created_at | Record creation time |

### Visits

Stores individual patient visits.

| Field      | Description          |
| ---------- | -------------------- |
| id         | Visit ID             |
| patient_id | Related patient      |
| doctor     | Doctor name          |
| visit_date | Date of visit        |
| symptoms   | Patient symptoms     |
| diagnosis  | Diagnosis            |
| notes      | Doctor notes         |
| created_at | Record creation time |

### Prescriptions

Stores medicines prescribed during a visit.

| Field        | Description             |
| ------------ | ----------------------- |
| id           | Prescription ID         |
| visit_id     | Related visit           |
| medicine     | Medicine name           |
| dosage       | Dosage                  |
| frequency    | Frequency               |
| duration     | Duration                |
| instructions | Additional instructions |
| created_at   | Record creation time    |

---

## 🔗 Database Relationships

```text
User
 │
 └── Authentication & Roles


Patient
 │
 ├── Medical History
 │       └── Multiple records
 │
 └── Visits
         │
         └── Prescriptions
                 └── Multiple medicines
```

### Relationships

* One Patient → Many Medical History records
* One Patient → Many Visits
* One Visit → Many Prescriptions

---

## 📂 Project Structure

```text
MediRecord/
│
├── app.py
├── database.py
├── requirements.txt
├── Procfile
├── README.md
├── .gitignore
│
├── database/
│   └── medirecord.db
│
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
│   └── visit_details.html
│
└── static/
    ├── css/
    │   └── style.css
    │
    └── js/
        └── script.js
```

> The exact structure may vary depending on the implementation.

---

## 🚀 Main Application Routes

| Route                          | Purpose                  |
| ------------------------------ | ------------------------ |
| `/login`                       | User authentication      |
| `/dashboard`                   | Main dashboard           |
| `/patients`                    | View/search patients     |
| `/add-patient`                 | Register patient         |
| `/patient/<id>`                | View patient details     |
| `/edit-patient/<id>`           | Edit patient information |
| `/patient/<id>/add-history`    | Add medical history      |
| `/patient/<id>/add-visit`      | Add patient visit        |
| `/visit/<id>/add-prescription` | Add prescription         |
| `/health`                      | Application health check |
| `/logout`                      | Logout user              |

---

## ✅ Data Validation

The application validates important patient information before storing it.

Examples:

* Patient ID must be unique
* Patient name is required
* Date of birth cannot be a future date
* Gender must be selected
* Phone number must follow the expected format
* Blood group can be selected from predefined values
* Required foreign-key relationships are validated
* Invalid form submissions are rejected

Both frontend and backend validation can be used to improve data reliability.

---

## 🔄 Application Workflow

```text
Login
  │
  ▼
Dashboard
  │
  ├── View Patients
  │       │
  │       ├── Search Patient
  │       │
  │       └── Open Patient Profile
  │                    │
  │                    ├── Medical History
  │                    │
  │                    ├── Previous Visits
  │                    │
  │                    └── Prescriptions
  │
  └── Add New Patient
```

---

# 💻 Installation & Setup

## 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/MediRecord.git
```

Move into the project directory:

```bash
cd MediRecord
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file if your application uses environment variables.

Example:

```env
FLASK_SECRET_KEY=your-secret-key
```

Do **not** commit `.env` to GitHub.

---

## 5. Initialize the Database

The application should automatically create the required database tables when the application starts.

If your implementation uses a separate initialization script, run:

```bash
python database.py
```

---

## 6. Run the Application

```bash
python app.py
```

The application will normally be available at:

```text
http://127.0.0.1:5000
```

Open the URL in your browser.

---

# 🔑 Demo Login

If demo credentials are configured in the application, use the credentials provided by the project administrator.

For security, real passwords should never be stored inside the source code or README.

---

# ☁️ Deployment on Render

MediRecord can be deployed on Render using Gunicorn.

### Requirements

`requirements.txt` should contain the packages required by the project, for example:

```text
Flask
gunicorn
```

Add other packages only if they are actually used by the application.

### Start Command

```text
gunicorn app:app
```

### Build Command

```text
pip install -r requirements.txt
```

### Environment Variables

Configure sensitive values such as:

```text
FLASK_SECRET_KEY
```

inside the Render environment settings rather than committing them to GitHub.

---

## ⚠️ Database Note

SQLite is suitable for:

* Learning
* College projects
* Demonstrations
* Small-scale testing

For a production healthcare application, a persistent database such as **PostgreSQL or MySQL** is recommended.

When deploying SQLite on platforms with ephemeral filesystems, database changes may not persist after certain deployments or service restarts. A production implementation should therefore use a persistent database.

---

# 🔒 Privacy & Security Considerations

MediRecord is an educational/project implementation and should not be used with real patient information without appropriate security, privacy, compliance, and infrastructure controls.

Important practices include:

* Never upload real patient data to GitHub
* Never commit passwords
* Never commit API keys or secret keys
* Use password hashing
* Use HTTPS in production
* Use parameterized SQL queries
* Restrict access based on user roles
* Use a secure production database
* Maintain appropriate audit logs
* Protect backups and database credentials

---

# 🧪 Testing Checklist

Before deployment, verify:

* [x] Login works
* [ ] Invalid login is rejected
* [ ] Patient registration works
* [ ] Patient ID uniqueness works
* [ ] Patient search works
* [ ] Patient details display correctly
* [ ] Patient information can be updated
* [ ] Medical history can be added
* [ ] Visits can be added
* [ ] Prescriptions can be added
* [ ] Role-based permissions work
* [ ] Logout works
* [ ] Database tables are created correctly
* [ ] `/health` endpoint works
* [ ] Application works with Gunicorn

---

# 🎓 Learning Outcomes

This project demonstrates practical knowledge of:

* Python
* Flask web development
* HTML, CSS and JavaScript
* SQL and relational databases
* CRUD operations
* Database relationships
* Authentication
* Password hashing
* Role-based access control
* Form validation
* Git and GitHub
* Web application deployment
* Basic application security

---

# 🔮 Future Enhancements

Possible future improvements include:

* PostgreSQL/MySQL production database
* Advanced search and filtering
* Appointment management
* Doctor management
* Patient document upload
* Medical report upload
* Email/SMS notifications
* Dashboard analytics
* Audit logging
* PDF medical reports
* Automatic database backups
* REST API
* Mobile-friendly improvements
* AI-assisted medical record summarization with appropriate safeguards

---

# 📌 Project Status

**Status:** Academic / Educational Project

**Current Focus:** Digital patient medical record management with Flask and a relational database.

---

## 👩‍💻 Author

**Adari Venkata Lakshmi**

GitHub:adarivenkatalakshmi70-glitch 

---

## 📄 License

This project is intended for educational purposes. Add an appropriate open-source license if you plan to distribute the project publicly.

