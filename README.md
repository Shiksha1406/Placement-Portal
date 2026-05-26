# Placement Portal

A full-stack placement portal web application for managing students, companies, job postings, applications, and admin workflows.

## Features

- Student registration and login
- Company registration and login
- Admin dashboard
- Job posting management
- Student application tracking
- Resume upload support
- Role-based authentication
- Flask backend API
- Vue.js frontend interface

## Tech Stack

### Frontend
- Vue.js
- Vue Router
- Axios
- Vite

### Backend
- Flask
- Flask-SQLAlchemy
- Flask-CORS
- JWT Authentication
- SQLite
- Flask-Mail
- Flask-Caching
- Flask-Limiter

## Project Structure
Placement-Portal/
├── Backend/
│   ├── app.py
│   ├── models.py
│   ├── database.py
│   ├── config.py
│   ├── requirements.txt
│   ├── controllers/
│   └── routes/
├── Frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
└── .gitignore


Setup Instructions

Backend Setup
cd Backend
python -m venv ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt
python app.py

The backend will run at:
http://127.0.0.1:5000

Frontend Setup
Open a new terminal:
cd Frontend
npm install
npm run dev

The frontend will run at:
http://localhost:5173

Default Admin Login
Username: admin
Password: admin@123

