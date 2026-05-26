# Placement Portal

A full-stack Placement Portal built with **Flask (Backend)** and **Vite + React (Frontend)**.

---

## 🚀 Tech Stack

### Backend

* Flask
* SQLAlchemy
* Flask-JWT-Extended
* Flask-CORS
* Flask-Limiter

### Frontend

* React
* Vite
* Axios
* React Router DOM

---

# 📁 Project Structure

```bash
Placement-Portal/
│
├── Backend/
│   ├── app.py
│   ├── models.py
│   ├── database.py
│   ├── config.py
│   ├── requirements.txt
│   │
│   ├── controllers/
│   └── routes/
│
├── Frontend/
│   ├── src/
│   ├── package.json
│   ├── vite.config.js
│   └── .gitignore
│
└── README.md
```

---

# ⚙️ Setup Instructions

## 1️⃣ Backend Setup

Open a terminal and run:

```bash
cd Backend

python -m venv ../venv

# Activate virtual environment
# Windows
..\venv\Scripts\activate

# macOS/Linux
source ../venv/bin/activate

pip install -r requirements.txt

python app.py
```

### Backend Server

The backend will start at:

```bash
http://127.0.0.1:5000
```

---

## 2️⃣ Frontend Setup

Open a new terminal and run:

```bash
cd Frontend

npm install
npm run dev
```

### Frontend Server

The frontend will start at:

```bash
http://localhost:5173
```

---

# 🔐 Default Admin Credentials

```txt
Username: admin
Password: admin@123
```

---


