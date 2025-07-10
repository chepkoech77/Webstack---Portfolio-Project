# 🛡️ GCAPI – GC-API

A secure and lightweight RESTful API built with FastAPI, Tortoise ORM, and SQLite, designed to manage users, (GCs), and products. Includes JWT authentication and email verification support.

---

## 🚀 Features

- 🧑 User registration, login (OAuth2/JWT)
- ✅ Email verification
- 🔐 Password hashing with `passlib[bcrypt]`
- 📦 CRUD for:
  - Users
  - GCs (Keepers)
  - Products
- 🔄 Uvicorn with live reload (`--reload`)
- ⚡ Fully async using Tortoise ORM
- 📘 Swagger UI (`/docs`) and ReDoc (`/redoc`)

---

## 🔧 Requirements

- Python 3.10+
- `pip` (Python package manager)
- Virtualenv (recommended)

Install dependencies:
```bash
pip install -r requirements.txt

pip install python-multipart

uvicorn main:app --reload

GCAPI/
├── main.py               # FastAPI entry point
├── models.py             # Tortoise ORM models
├── auth.py               # JWT auth utils
├── email_sender.py       # Email verification logic
├── requirements.txt
└── db.sqlite3            # SQLite DB (auto-created)

👨💻 Author

Built by @GChep
Inspired by real-world secure API patterns.

