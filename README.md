Online Examination and Grading Management System
An end-to-end web application for conducting online exams with automated grading and real-time result management.
🚀 Features
🔐 JWT-based secure login system

🧑‍🎓 Student dashboard displaying enrollment and profile details

📝 Subject-wise online exams (DBMS, Math, ML – 10 questions each)

✅ Auto-grading system based on selected answers

📊 Result section storing and showing previous scores

💾 MySQL database for persistent student, question, and result data

🌐 Full-stack integration using FastAPI + JavaScript frontend

🛠️ Tech Stack
Layer	Technology
Frontend	HTML, CSS, JavaScript
Backend	Python (FastAPI), SQLAlchemy
Database	MySQL
Auth	JWT Tokens
Tools Used	VS Code, GitHub, MySQL Workbench

⚙️ Project Structure
├── backend/
│   ├── main.py                # FastAPI app entry point
│   ├── models.py              # SQLAlchemy models
│   ├── database.py            # DB connection
│   └── routes/
│       ├── auth.py            # JWT login routes
│       ├── exam.py            # Exam and grading routes
│       └── result.py          # Result fetching/storing
├── frontend/
│   ├── index.html             # Login + Dashboard UI
│   ├── exam.html              # Exam screen
│   └── result.html            # Results page
└── README.md


🧑‍💻 Author
Anushna Immadisetty

📧 immadisettyanushna@gmail.com
