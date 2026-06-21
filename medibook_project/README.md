# ♥ MediBook — Smart Clinic Management System

![MediBook](https://img.shields.io/badge/MediBook-v1.0-1A6B9A?style=for-the-badge)
![Django](https://img.shields.io/badge/Django-4.x-092E20?style=for-the-badge&logo=django)
![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap)
![Stripe](https://img.shields.io/badge/Stripe-Payments-635BFF?style=for-the-badge&logo=stripe)
![Claude AI](https://img.shields.io/badge/Claude-AI%20Chat-D97706?style=for-the-badge)

A full-stack Django web application for smart clinic management — allowing patients to book appointments, view medical records, pay bills, and communicate with clinic agents, powered by AI chat.


---

## 🌐 Live Demo

Deployed on AWS EC2: `http://<your-ec2-ip>`


---

## ✨ Features

### 👤 Patient Portal
- Register & Login with full validation
- Dashboard with upcoming appointments & billing summary
- Book, reschedule, or cancel appointments
- View medical history, lab results & health summary
- Upload and manage patient files
- Pay bills online via *Stripe*
- Send messages to clinic agents
- Receive email notifications (SMTP)
- Forgot password / reset via email code

### 🧑‍💼 Agent Dashboard
- Agent login & registration
- View and manage patient profiles
- Add patients to the system
- View appointments and messages
- Respond to patient messages
- View patient billing records

### 🤖 AI Chat (Claude + Groq)
- Integrated AI medical assistant powered by *Anthropic Claude*
- Groq API for fast inference
- Accessible from patient dashboard

### 🔔 Reminders App
- Separate reminders Django app
- send_reminders.py management command for scheduled email reminders
- Bookings management via custom commands

---

## 🛠️ Tech Stack

| Layer           | Technology                        |
|-----------------|-----------------------------------|
| Backend         | Django 4.x (Python)               |
| Database        | SQLite 3 (dev) / MySQL (prod)     |
| Frontend        | HTML5, CSS3, Bootstrap 5.3        |
| Dynamic Updates | AJAX / Fetch API                  |
| Authentication  | Custom bcrypt sessions            |
| Payments        | Stripe API                        |
| AI Chat         | Anthropic Claude API + Groq API   |
| Email API       | SMTP (Gmail)                      |
| Deployment      | AWS EC2 + Gunicorn + Nginx        |
| Version Control | GitHub                            |

---

## 📁 Project Structure

medibook_project/
├── medibook_project/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── users_app/                 # Main patient/agent app
│   ├── management/
│   │   └── commands/
│   │       └── send_reminders.py
│   ├── migrations/
│   ├── static/
│   │   ├── css/
│   │   │   └── main.css
│   │   └── js/
│   │       └── main.js
│   ├── templates/
│   │   ├── base.html
│   │   ├── landing.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── dashboard.html
│   │   ├── about.html
│   │   ├── contact.html
│   │   ├── services.html
│   │   ├── health.html
│   │   ├── appointments.html
│   │   ├── appointment_confirmation.html
│   │   ├── patient_appointments.html
│   │   ├── patient_billing.html
│   │   ├── patient_bills_summary.html
│   │   ├── patient_messages.html
│   │   ├── patients_list.html
│   │   ├── patient_added_confirmation.html
│   │   ├── doctors_list.html
│   │   ├── doctor_detail.html
│   │   ├── doctor.added_confirmation.html
│   │   ├── agent_dashboard.html
│   │   ├── agent_login.html
│   │   ├── agent_register.html
│   │   ├── agent_add_patient.html
│   │   ├── agent_patient_profile.html
│   │   ├── agent_message_detail.html
│   │   ├── forgot_password.html
│   │   ├── reset_code.html
│   │   ├── reset_password.html
│   │   ├── payment_success.html
│   │   ├── payment_cancel.html
│   │   ├── privacy_policy.html
│   │   └── terms_of_service.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── tests.py
│
├── reminders/                 # Reminders Django app
│   ├── bookings/
│   │   └── management/
│   │       └── commands/
│   │           └── send_reminders.py
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── booking.py
│   ├── models.py
│   ├── views.py
│   └── tests.py
│
├── .env                       # Environment variables (not committed)
├── .gitignore
├── db.sqlite3
├── manage.py
└── README.md

---

## 🗄️ Database Schema

*Tables:*

- User — Patients with full profile
- Agent — Clinic staff accounts
- Doctor — Clinic doctors
- Appointment — Bookings (patient ↔ doctor)
- Bill — Patient billing records
- Message — Patient-agent communication
- MedicalRecord — Health info per patient
- LabResult — Lab test results
- PatientFile — Uploaded patient documents
- PatientProfile — Extended patient info
- HealthSummary — AI-generated or manual health summaries
- PasswordResetCode — Email-based password reset tokens

---

## 🚀 Getting Started

### Prerequisites

- Python 3.x
- pip

### Installation

*1. Clone the repository:*

git clone https://github.com/baraasalahbs96/MediBook.git
cd MediBook

*2. Create virtual environment:*

python3 -m venv venv
source venv/bin/activate

*3. Install dependencies:*

pip install -r requirements.txt

**4. Create .env file:**

SECRET_KEY=your-secret-key-here
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
ANTHROPIC_API_KEY=your-anthropic-key
GROQ_API_KEY=your-groq-key
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key

*5. Run migrations:*

python manage.py makemigrations
python manage.py migrate

*6. Run the server:*

python manage.py runserver

*7. Open in browser:*

http://127.0.0.1:8000

---

## 📦 Requirements

django>=4.0
python-dotenv
bcrypt
stripe
anthropic
groq

Generate with:

pip freeze > requirements.txt

---

## 📄 Pages

| # | Page                     | URL                          | Access  |
|---|--------------------------|------------------------------|---------|
| 1 | Landing Page             | /                          | Public  |
| 2 | Login                    | /login/                    | Public  |
| 3 | Register                 | /register/                 | Public  |
| 4 | Patient Dashboard        | /dashboard/                | Patient |
| 5 | Appointments             | /appointments/             | Patient |
| 6 | Patient Billing          | /billing/                  | Patient |
| 7 | Patient Messages         | /messages/                 | Patient |
| 8 | Health Summary           | /health/                   | Patient |
| 9 | Doctors List             | /doctors/                  | Patient |
| 10| Forgot Password          | /forgot-password/          | Public  |
| 11| Agent Login              | /agent/login/              | Public  |
| 12| Agent Dashboard          | /agent/dashboard/          | Agent   |
| 13| Agent — Patient Profile  | /agent/patient/<id>/       | Agent   |
| 14| About                    | /about/                    | Public  |
| 15| Services                 | /services/                 | Public  |
| 16| Contact                  | /contact/                  | Public  |
| 17| Privacy Policy           | /privacy/                  | Public  |
| 18| Terms of Service         | /terms/                    | Public  |

---

## 🔐 Security

- ✅ Password hashing with *bcrypt*
- ✅ *CSRF* tokens on all forms
- ✅ Server-side *form validation*
- ✅ *SQL injection* protection via Django ORM
- ✅ Session-based authentication (patient & agent)
- ✅ Role-based access control (Agent vs Patient)
- ✅ Environment variables via .env
- ✅ Password reset via secure email code

---

## 💳 Stripe Integration

MediBook uses *Stripe* for secure online bill payments:

| Trigger          | Action              |
|------------------|---------------------|
| Patient pays bill | Stripe Checkout     |
| Payment success  | Bill marked as paid |
| Payment cancel   | Returns to billing  |

---

## 📧 Email Notifications

MediBook uses *Gmail SMTP* for automated emails:

| Trigger              | Email Sent          |
|----------------------|---------------------|
| Registration         | Welcome email       |
| Appointment booked   | Confirmation        |
| Bill generated       | Payment reminder    |
| New message          | Notification        |
| Forgot password      | Reset code          |
| Appointment reminder | Scheduled reminder  |

---

## 🤖 AI Chat

- Powered by *Anthropic Claude API*
- Fast inference via *Groq API*
- Accessible from the patient dashboard
- Answers medical FAQs and clinic-related questions

---

## ☁️ AWS Deployment

Deployed on *AWS EC2* with:

- *Gunicorn* as WSGI server
- *Nginx* as reverse proxy
- Environment variables secured via .env

---

## 🗂️ Project Management

- *GitHub Repo:* [baraasalahbs96/MediBook](https://github.com/baraasalahbs96/MediBook)

---

## 👨‍💻 Developer

*Baraa Salah*

- GitHub: [@baraasalahbs96](https://github.com/baraasalahbs96)
- Axsos Academy — Python Stack 2026

---

## 📝 License

This project was built as part of the Axsos Academy Solo Project Week — June 2026.