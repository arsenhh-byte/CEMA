# 🏥 Health Information System

This project is a **simple but powerful health information management system** built with Flask, SQLAlchemy, and Bootstrap. It allows doctors to register clients, create health programs (e.g., TB, Malaria, HIV), enroll clients in programs, and manage client data securely.

It follows **API-first principles**, includes **data security**, **dynamic search**, **data export features**, and is **deployment ready**.  
The system is intuitive, fast, and modern — designed to **scale and extend**.

---

## ✨ Features

- 🩺 **Doctor Login and Registration** with bcrypt password encryption.
- 🆕 **Create Health Programs** (e.g., HIV, TB, Malaria).
- 👤 **Register Clients** (First name, Last name, Date of Birth, Gender, Contact, Email).
- ➡️ **Enroll Clients** in one or more health programs.
- 🔍 **Search Clients** with live search and program/date filters.
- 📄 **Export Client Data** to CSV and PDF formats.
- 📧 **(Optional)** Email Client Registry PDF via SMTP.
- 🧩 **API-First Approach** to expose client and program data securely.
- 🔒 **Security Measures** (bcrypt hashing, secure sessions, CSRF protected forms).
- 📊 **Interactive Dashboard** with animated stats and real-time charts.
- ⚡ **Modern UI** using Bootstrap 5, SweetAlert2, and fade-in animations.
- 🚀 **Ready for Deployment** to platforms like Render, Railway, or AWS.

---

## 🏗️ System Architecture

- **Frontend**: Bootstrap 5, Jinja2 templating, Vanilla JS for interactivity.
- **Backend**: Flask (Python 3), SQLAlchemy ORM.
- **Database**: SQLite (easy to upgrade to PostgreSQL/MySQL).
- **Mail Server**: Flask-Mail (Gmail SMTP setup).
- **Authentication**: Secure session-based login.
- **PDF Reports**: Generated with ReportLab.
- **Data APIs**: Exposing `/api/clients`, `/api/programs`, `/api/clients/<id>`.
-- **Testing**: Pytest
 

---

## 📸 Screenshots (Insert Your Images)

| Feature                         | Image Placeholder                |
|:---------------------------------|:----------------------------------|
| Database ER Diagram             |![health_info_er_diagram](https://github.com/user-attachments/assets/e28c62a9-cffc-4ad7-8970-b7d2730ebbab) |
| Client Management Page          | ![image](https://github.com/user-attachments/assets/ea48fa47-decd-4d2d-8ce4-8b7f2e2087c7)  |
| Dashboard with Charts           | ![image](https://github.com/user-attachments/assets/cff4fb6e-b513-4b71-a997-7115a5a1fb9c) |
| Program Management Page         | ![image](https://github.com/user-attachments/assets/e2c4924f-133b-42f6-9c14-7f5322f24b32)  |
| Client Profile API (JSON Output) |![image](https://github.com/user-attachments/assets/2928cc02-1ca8-4cae-a84c-15fca769b7b8)  |
---

## 🚀 How to Run Locally

1. **Clone the repository**:
   ```bash
   git clone https://github.com/arsenhh-byte/CEMA.git
   cd CEMA
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up `.env` (for email settings)**:
   ```bash
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your_email@gmail.com
   MAIL_PASSWORD=your_app_password
   SECRET_KEY=your_secret_key
   ```

5. **Run the application**:
   ```bash
   flask run
   ```

6. **Access at**: `http://127.0.0.1:5000/`

---

## 📚 API Endpoints

| Endpoint                         | Method | Description                   |
|:----------------------------------|:------:|:------------------------------|
| `/api/clients`                   | GET    | Retrieve all clients          |
| `/api/clients/<client_id>`        | GET    | Retrieve a specific client    |
| `/api/programs`                  | GET    | Retrieve all programs         |
| `/api/dashboard-data`            | GET    | Get dashboard overview data   |

---

## 🔒 Security Measures

- Passwords hashed with **bcrypt**.
- Secure session configuration: **HTTPOnly**, **Secure**, **SameSite=Lax**.
- Input validation on server and client sides.
- PDF exports handled in-memory (no file leaks).

---

## 💡 Innovations & Improvements

- API-first design principle.
- Bulk delete and sort programs dynamically.
- Auto-detection of country code on registration.
- Email multiple recipients (future support).
- Automatic session expiration.
- Deployment ready on **Render**, **Railway**, or **AWS EC2**.
- Clean commit history and detailed documentation.

---

## 🛠️ Technologies Used

- Python 3
- Flask
- Flask-Mail
- Flask-Bcrypt
- SQLAlchemy
- ReportLab (PDF generation)
- Bootstrap 5
- JavaScript (SweetAlert2, Chart.js)

---

## ✅ Demonstration Checklist

- [x] Create health programs
- [x] Register clients
- [x] Enroll clients in programs
- [x] Search and filter clients
- [x] View client profiles
- [x] Export client list (CSV/PDF)
- [x] Expose APIs for integration
- [x] Clean and secure code
- [x] Modern UI/UX experience
- [x] Deployment readiness


## 🧪 How to Run Tests

Tests are written using **Pytest**.

1. Ensure you are inside your virtual environment.

2. Run:

```bash
pytest tests/test_app.py
```

This will automatically discover and execute the test cases for:

- Client registration
- Program creation
- Enrollment
- API endpoint responses
- PDF generation

✅ You should see output like:

```plaintext
============================= test session starts =============================
collected 5 items

tests/test_app.py .....                                        [100%]

============================== 5 passed in 1.25s =============================
```

---

## 🌐 Deployed Version

> You can access the deployed live version here:  
> https://cema-obl7.onrender.com


## 👨‍💻 Author

> **Arsen Ogutu**  

## PowerPoint Presentation
https://docs.google.com/presentation/d/1b5asWs0IvcBCDjYZ2mDMO4zjMDr9KUtFdFfy3oQh_Ls/edit?usp=sharing

---

## 📃 License

This project is released under the [MIT License](LICENSE).

---

## 🙌 Acknowledgments

Thanks to Flask, Bootstrap, ReportLab, and all open-source contributors who made building this solution possible.
