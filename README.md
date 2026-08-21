# LineByLine — AI-Powered Code Learning Platform

LineByLine is an AI-powered code explanation and learning engine built with React (Vite), Flask, and Supabase.

---

## 📁 Project Structure

```
LineByLine/
├── backend/                  # Flask REST API & Python Explanation Engine
│   ├── app.py                # Flask application entry point
│   ├── requirements.txt      # Python dependencies
│   ├── .env                  # Backend environment variables
│   ├── .env.example          # Template environment variables
│   ├── explanation_engine/   # Explainer, Parser, Resources, Auth & Persistence
│   ├── database/             # Schema, Seed SQL & DB audit scripts (verify_database.py)
│   ├── static/               # Flask static assets
│   └── templates/            # Flask templates
│
├── frontend/                 # React + Vite Frontend UI
│   ├── package.json          # Node dependencies and scripts
│   ├── vite.config.js        # Vite dev server & API proxy config
│   ├── index.html            # Main HTML entry point
│   ├── .env                  # Frontend environment variables
│   └── src/                  # React components, pages, contexts & services
│
├── README.md                 # Project documentation
└── .gitignore                # Root gitignore rules
```

---

## 🚀 Quick Start Guide

### 1. Backend Setup & Startup

```bash
# Navigate to backend directory
cd backend

# Create & activate virtual environment (if not active)
python -m venv .venv
# On Windows: .venv\Scripts\activate
# On macOS/Linux: source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the Flask API server (runs on http://127.0.0.1:5000)
python app.py
```

### 2. Frontend Setup & Startup

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Start Vite development server (runs on http://localhost:5173 with proxy to :5000)
npm run dev
```

---

## 🧪 Verification & Audit Commands

### Backend Syntax Verification
```bash
cd backend
python -m py_compile app.py
```

### Database & Security Audit (52/52 Checks)
```bash
cd backend
python database/verify_database.py
```

### Frontend Production Build
```bash
cd frontend
npm run build
```
