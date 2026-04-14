# 🎓 AICTE Activity & Points Management System

> **Digitizing co-curricular achievement — from paperwork to dashboard, in one platform.**

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=flat-square&logo=mysql&logoColor=white)](https://www.mysql.com/)

---

<!-- Replace the placeholder below with your actual logo -->
<p align="center">
  <img src="docs/assets/logo.png" alt="AICTE Points System Logo" width="180"/>
</p>

Engineering colleges require students to earn **100 co-curricular points** before graduation — a mandate tracked almost entirely through manual paperwork, spreadsheets, and physical certificates. This system eliminates that friction entirely.

The **AICTE Activity & Points Management System** is a full-stack web application that gives students a live view of their progress, empowers clubs to organize and manage events with a single dashboard, and provides administrators with a verified, audit-ready record of every activity — all backed by QR-based attendance and automated PDF generation.

---

## ✨ Core Features

### 👤 Three-Tier Role Access
Dedicated, permission-scoped dashboards for each user type — Students track progress, Clubs manage events, and Admins oversee the entire ecosystem. No role can exceed its privilege boundary.

### 📊 Visual Points Tracking
Students see a real-time progress bar toward the **100-point AICTE target**, broken down by category:

| Category | Description |
|---|---|
| 🔧 Technical | Hackathons, workshops, paper presentations |
| 🎭 Cultural | Fests, competitions, performing arts |
| 🤝 Social | NSS, community outreach, volunteering |
| ⚽ Sports | Inter-college and intra-college competitions |

### 📱 QR Attendance System
Each event generates a **unique, time-bound QR token**. Students scan it on-site for instant, tamper-resistant attendance marking — no proxy, no paperwork.

### 📄 Automated Document Generation
Participation **certificates** and complete **activity reports** are generated on demand as polished PDFs using ReportLab — ready to submit, download, or archive.

### ✅ Approval Workflow
Clubs submit events for review. Admins approve or reject with remarks through a dedicated moderation interface before the event goes live and points are awarded.


---
### 🖼️ System Wireframes
![AICTE System Flow Wireframe](/Aicte%20project%20wireframe.png)

---
## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | Bootstrap 5, Jinja2 Templates, Vanilla JavaScript, Lucide Icons |
| **Backend** | Python 3.8+, Flask 2.x, ReportLab (PDF), qrcode |
| **Database** | MySQL 8.0 |
| **Auth** | Flask-Login, bcrypt |
| **Dev Tools** | python-dotenv, pip, virtualenv |

---

## ⚙️ Installation & Setup

### Prerequisites

- Python **3.8+**
- MySQL **8.0+**
- `pip` and `virtualenv`

---

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/aicte-points-system.git
cd aicte-points-system
```

### 2. Create and Activate a Virtual Environment

```bash
# Create
python -m venv venv

# Activate — macOS/Linux
source venv/bin/activate

# Activate — Windows
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize the Database

Log into MySQL and run the provided schema:

```bash
mysql -u root -p
```

```sql
CREATE DATABASE aicte_points;
USE aicte_points;
SOURCE schema.sql;
```

The schema creates the three core tables:
- **`users`** — stores student, club, and admin accounts with role flags
- **`events`** — holds event metadata, category, points value, and approval status
- **`registrations`** — join table linking users to events, with QR token and attendance timestamp

### 5. Configure the Application

Copy the example config and fill in your credentials:

```bash
cp config.example.py config.py
```

```python
# config.py
SECRET_KEY = "your-secret-key-here"

DB_HOST     = "localhost"
DB_USER     = "root"
DB_PASSWORD = "your-mysql-password"
DB_NAME     = "aicte_points"
```

### 6. Run the Development Server

```bash
flask run
```

The app will be live at **`http://127.0.0.1:5000`**.

---

## 🚀 Usage Guide

The platform follows a simple, three-step workflow:

```
Club creates event  →  Admin approves  →  Students register & scan QR
        ↓                    ↓                        ↓
  Fills in details,    Reviews and         Attends event, scans unique
  category & points    approves/rejects    QR code on-site
  value                with remarks        ↓
                                     Points credited automatically
                                     Certificate available to download
```

1. **Club** logs in, navigates to *Create Event*, and submits details (name, date, category, points).
2. **Admin** reviews the submission in the *Pending Approvals* queue and approves or rejects it.
3. **Student** browses *Upcoming Events*, registers, and scans the event QR code on the day.
4. Attendance is marked instantly. Points reflect on the student's dashboard in real time.
5. Both students and admins can generate **PDF certificates / reports** from the dashboard at any time.

---

## 📁 Project Structure

```
aicte-points-system/
│
├── app.py                  # Application entry point & factory
├── config.py               # Environment & DB configuration
├── schema.sql              # Database schema (users, events, registrations)
├── requirements.txt
│
├── models/                 # Database models & query logic
│   ├── user.py
│   ├── event.py
│   └── registration.py
│
├── routes/                 # Flask Blueprints — one per role
│   ├── auth.py             # Login, logout, registration
│   ├── student.py          # Student dashboard, QR scan
│   ├── club.py             # Event creation & management
│   └── admin.py            # Approvals, reports, user management
│
├── templates/              # Jinja2 HTML templates
│   ├── base.html           # Base layout with nav & theme toggle
│   ├── student/
│   ├── club/
│   └── admin/
│
├── utils/                  # Helpers: QR generation, PDF creation
│   ├── qr_generator.py
│   ├── pdf_generator.py
│   └── points_calculator.py
│
└── static/                 # CSS, JS, images
    ├── css/
    ├── js/
    └── uploads/            # Generated QR codes & certificates
```

---



## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

<p align="center">
  Built with ❤️ to make academic management less painful.
</p>
