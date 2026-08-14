# 🎓 Smart Result Analysis System

> **Turn static PDF marksheets into dynamic, intelligent dashboards.** Upload a marksheet, and the system automatically extracts every student record, computes batch analytics, predicts future SGPA, and builds a searchable academic history — all stored securely in the cloud.

[![React](https://img.shields.io/badge/Frontend-React_18-61dafb?logo=react&logoColor=white)](https://react.dev)
[![Vite](https://img.shields.io/badge/Build-Vite_5-646cff?logo=vite&logoColor=white)](https://vitejs.dev)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Firebase](https://img.shields.io/badge/DB-Firestore-ffca28?logo=firebase&logoColor=white)](https://firebase.google.com)
[![Python](https://img.shields.io/badge/Python-3.9+-3776ab?logo=python&logoColor=white)](https://www.python.org)
[![Node](https://img.shields.io/badge/Node.js-18+-339933?logo=nodedotjs&logoColor=white)](https://nodejs.org)

---

## 📚 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [How It Works](#-how-it-works)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [API Reference](#-api-reference)
- [Database Schema](#-database-schema)
- [Role Model](#-role-model)
- [Project Structure](#-project-structure)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [Credits & License](#-credits--license)

---

## 📖 Overview

Educational institutions routinely manage results as raw PDF marksheets. Extracting, comparing, and tracking student performance across semesters is tedious and error-prone.

**Smart Result Analysis System** solves this with three core capabilities:

1. **Automated Extraction** — a parsing engine reads any university marksheet PDF and reconstructs structured records for every student (PRN, seat number, name, subjects, grades, SGPA, credits).
2. **Intelligent Analytics** — pass/fail classification, grade distributions, batch statistics, subject-level failure analysis, and a **machine-learning SGPA prediction** based on a student's past trajectory.
3. **Cloud Persistence** — analyzed results are archived to Firebase Firestore keyed by PRN, so a student's full academic timeline is assembled automatically across multiple exams.

Two role-based experiences are built in: **Teachers** analyze and manage batches; **Students** view their own academic journey.

---

## ✨ Features

### 👨‍🏫 Teacher

| Feature | Details |
|---|---|
| **PDF Upload & Analysis** | Upload a marksheet, get instant summary — pass %, average SGPA, failure count, top performers |
| **6-Way Analysis Suite** | Overview · Top Performers · Failures · Subject Analysis · Detailed List · Advanced Insights |
| **Subject Analysis** | Identifies "critical subjects" where most students fail, with per-subject pass rates |
| **Cloud Archive** | Save analyzed batches; browse, search, and filter archived exams by name/department/year |
| **Global Student Search** | Find any student by **Name or PRN** across all uploaded exams and view their full history |
| **Institutional Overview** | Department-wise and year-wise performance trends across the entire database |

### 👨‍🎓 Student

| Feature | Details |
|---|---|
| **Personal Records** | Select your profile and view your complete result history in one place |
| **SGPA Trend** | Visual chart of your SGPA across every semester |
| **AI Prediction** | Estimated **next-semester SGPA** computed by linear regression on your past scores |
| **Failure Insights** | Flagged list of subjects you failed, with exam and grade details |

---

## 🏗️ Architecture

```
┌──────────────────────┐         ┌─────────────────────────┐         ┌──────────────────────┐
│    React SPA (Vite)   │  HTTPS  │       FastAPI            │         │      Firebase          │
│  ┌──────────────────┐ │ ──────▶ │  ┌─────────────────────┐ │  REST   │  ┌──────────────────┐ │
│  │  TeacherDashboard │ │         │  │ routers/            │ │ ──────▶ │  │ Auth (email/pass)│ │
│  │  StudentDashboard │ │         │  │  auth · results     │ │         │  └──────────────────┘ │
│  │  Login/Register   │ │  /api   │  │  students · overview │ │         │  ┌──────────────────┐ │
│  └──────────────────┘ │         │  ├─────────────────────┤ │         │  │ Firestore DB      │ │
│  Recharts · Axios     │         │  │ analyzer.py          │ │         │  │  users            │ │
│                       │         │  │  (PDF + ML engine)   │ │         │  │  result_files     │ │
└──────────────────────┘         │  └─────────────────────┘ │         │  └──────────────────┘ │
         Vercel                  └─────────────────────────┘         └──────────────────────┘
                                          Render.com
```

**Request flow:** React (Vercel or `localhost:5173`) → `/api/*` (proxied in dev, absolute URL in prod) → FastAPI → Firebase Auth & Firestore REST → JSON back to the UI.

---

## ⚙️ How It Works

### 1️⃣ PDF Parsing Engine (`analyzer.py`)
- The raw PDF text is read with **PyPDF2**.
- Text is **segmented per student** by locating the `SEAT NO.:` keyword.
- **Regular expressions** then extract structured fields from each block: PRN, seat number, name, mother's name, subjects with grades and credits, SGPA, and total credits.
- Grade → grade-point mapping classifies each subject result (`O`, `A+`, `A`, …, `F`, `FF`, `AB`, `IC`).

### 2️⃣ Result Classification
- A student is marked **Pass** when they have a valid SGPA and no failing grades; otherwise **Fail**.
- Failure modes are categorized (backlog vs. absent/null SGPA) for deeper insight.

### 3️⃣ AI SGPA Prediction
- Uses **linear regression (scikit-learn)** on a student's ordered SGPA history `(t₁,g₁), (t₂,g₂), …, (tₖ,gₖ)`.
- The fitted trend line is extrapolated to produce an **estimated next-semester SGPA**.
- See [`mathematical_model.txt`](mathematical_model.txt) for the formal mathematical specification.

### 4️⃣ Cloud Memory
- Every saved batch links students by **PRN**, automatically assembling each student's academic timeline across all uploaded exams.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, Vite 5, React Router 6, Axios, Recharts |
| **Backend** | FastAPI, Pydantic v2, Uvicorn |
| **Data Processing** | PyPDF2, pandas, numpy |
| **Machine Learning** | scikit-learn (Linear Regression) |
| **Database & Auth** | Firebase Firestore + Firebase Auth (email/password) via REST |
| **Hosting** | Render (API) · Vercel (Frontend) |

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.9+** and **Node.js 18+**
- A **Google Firebase project** with **Firestore** and **Email/Password Authentication** enabled
- Git

### 1. Clone the repository

```bash
git clone https://github.com/rahulchaudhari31/new-result-analysis-system.git
cd new-result-analysis-system
```

### 2. Backend (FastAPI)

```bash
cd backend

# create & activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS / Linux

# install dependencies
pip install -r requirements.txt

# configure Firebase credentials
copy .env.example .env         # Windows
cp .env.example .env           # macOS / Linux
#  → edit .env with YOUR Firebase values

# run the API server
uvicorn main:app --reload --port 5000
```

The API is now live at **`http://localhost:5000`** — interactive docs at **`http://localhost:5000/docs`**.

> ⚠️ **The local backend runs on port `5000`.** The frontend's Vite dev server is configured to proxy `/api` to `localhost:5000` — do **not** change it to `8000`.

### 3. Frontend (React + Vite)

```bash
cd frontend

npm install
cp .env.example .env.local    # optional — leave VITE_API_URL empty for local dev
npm run dev
```

Open **`http://localhost:5173`**. API calls under `/api` are automatically proxied to the backend by Vite, so no CORS issues in development.

### 4. Create a Firebase project

1. Go to the [Firebase Console](https://console.firebase.google.com) and create a project.
2. Enable **Authentication → Sign-in method → Email/Password**.
3. Create a **Cloud Firestore** database (production mode).
4. In **Project Settings**, copy your web app config values into `backend/.env`:
   - `FIREBASE_API_KEY`
   - `FIREBASE_AUTH_DOMAIN`
   - `FIREBASE_PROJECT_ID`
   - `FIREBASE_STORAGE_BUCKET`
   - `FIREBASE_MESSAGING_SENDER_ID`
   - `FIREBASE_APP_ID`
   - `FIREBASE_MEASUREMENT_ID`

No Firestore security rules are needed for development, but **lock down rules before going to production** (see [Deployment](#-deployment)).

---

## 🔐 Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|---|---|---|
| `FIREBASE_API_KEY` | ✅ | Firebase web app API key |
| `FIREBASE_AUTH_DOMAIN` | ✅ | `your-project.firebaseapp.com` |
| `FIREBASE_PROJECT_ID` | ✅ | Firebase project ID |
| `FIREBASE_STORAGE_BUCKET` | ✅ | `your-project.firebasestorage.app` |
| `FIREBASE_MESSAGING_SENDER_ID` | ✅ | From Firebase project settings |
| `FIREBASE_APP_ID` | ✅ | From Firebase project settings |
| `FIREBASE_MEASUREMENT_ID` | ✅ | From Firebase project settings |
| `CORS_ORIGINS` | ⬜ | Comma-separated allowed origins. **Always** includes `http://localhost:5173` and the production Vercel URL, even when unset |

### Frontend (`frontend/.env.local`)

| Variable | Required | Description |
|---|---|---|
| `VITE_API_URL` | ⬜ | Base URL of the backend. Leave **empty** locally (Vite proxy handles it). Set to `https://<your-backend>.onrender.com` for production builds |

---

## 📡 API Reference

All routes are prefixed with `/api`. Auth-protected routes require an `Authorization: Bearer <firebase-id-token>` header.

### Authentication

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/api/auth/register` | Create account (`email`, `password`, `name`, `role`) | ❌ |
| `POST` | `/api/auth/login` | Sign in (`email`, `password`) → returns user + token | ❌ |

### Results

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/api/results/analyze` | Upload PDF (multipart `file`) → full analysis payload | ✅ |
| `POST` | `/api/results/save` | Persist an analyzed batch to Firestore | ✅ |
| `GET` | `/api/results/` | List all archived result files | ✅ |
| `GET` | `/api/results/{id}` | Fetch a single archived result file | ✅ |

### Students

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/api/students/identifiers` | Map of PRN → student name | ✅ |
| `GET` | `/api/students/history?prn=…` | Full academic history + SGPA prediction | ✅ |

### Overview

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/api/overview/` | Institutional KPIs (dept/year-wise stats) | ✅ |

> Full interactive docs: `http://localhost:5000/docs` (Swagger UI).

---

## 🗄️ Database Schema (Firestore)

### `users` collection

| Field | Type | Notes |
|---|---|---|
| `email` | string | User's email |
| `name` | string | Display name |
| `role` | string | `teacher` or `student` (lowercase) |
| `user_id` | string | Firebase Auth UID |
| `created_at` / `last_login` | timestamp | Audit timestamps |

### `result_files` collection

| Field | Type | Notes |
|---|---|---|
| `file_name` | string | Original PDF filename |
| `exam_tag` | string | e.g. `SE Computer May 2024` |
| `department` / `year` | string | Batch metadata |
| `uploaded_by` | string | Teacher's name |
| `students_data` | array | Full structured records for every student |
| `summary` | map | Pre-computed stats (pass %, avg SGPA, …) |
| `total_students` | number | Batch size |
| `uploaded_at` | timestamp | When the batch was archived |

---

## 🎭 Role Model

Only two roles exist — **`teacher`** and **`student`** (stored/transmitted lowercase):

| Role | Can access |
|---|---|
| `teacher` | Upload/analyze PDFs, save & browse archives, global student search, institutional overview |
| `student` | Their own profile, academic history, SGPA prediction |

- Registration payload must send `role` as `"teacher"` or `"student"` (the UI maps display labels `Teacher`/`Student` to lowercase values automatically).
- Frontend route guards (`RoleRoute` in `App.jsx`) enforce role-based navigation.

---

## 📂 Project Structure

```
smart-result-analysis-system/
├── backend/                    # FastAPI REST API
│   ├── app/
│   │   ├── main.py             # App entry, CORS, error handlers, router mounting
│   │   ├── config.py           # Env-driven config + guaranteed CORS origins
│   │   ├── schemas.py          # Pydantic request/response models
│   │   ├── analyzer.py         # PDF parsing + analytics + SGPA prediction
│   │   ├── firebase_manager.py # Firebase Auth + Firestore REST client
│   │   ├── deps.py             # Bearer-token dependency for protected routes
│   │   └── routers/
│   │       ├── auth.py         # Login / Register
│   │       ├── results.py      # PDF upload, analysis, archive
│   │       ├── students.py     # Global search & history
│   │       └── overview.py     # Institutional analytics
│   ├── requirements.txt
│   ├── render.yaml             # Render.com deploy config
│   └── .env.example
│
├── frontend/                   # React (Vite) SPA
│   ├── src/
│   │   ├── main.jsx / App.jsx  # Entry + role-based routing
│   │   ├── config.js           # Grades, colors, departments, years
│   │   ├── api/client.js       # Axios wrapper + shared error formatting
│   │   ├── context/AuthContext.jsx
│   │   ├── pages/              # LoginPage, TeacherDashboard, StudentDashboard
│   │   └── components/         # AnalysisView, StudentProfile, charts, UI kit
│   ├── index.html
│   ├── vite.config.js          # Dev server + /api proxy → localhost:5000
│   ├── vercel.json             # SPA rewrite for Vercel
│   └── .env.example
│
├── mathematical_model.txt      # Formal math spec for parsing & prediction
└── README.md
```

---

## ☁️ Deployment

### Backend → Render.com

1. Push the repo to GitHub.
2. In [Render](https://render.com): **New → Web Service → Connect repo**.
3. Settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory:** `backend`
4. Add the same Firebase env vars from `backend/.env.example` (set `CORS_ORIGINS` to include your Vercel URL).
5. Deploy → note your service URL, e.g. `https://new-result-analysis-system.onrender.com`.

> 💡 `render.yaml` in the repo contains this configuration; Render can provision from it directly.

### Frontend → Vercel

1. In [Vercel](https://vercel.com): **Add New Project → Import repo**.
2. Framework preset: **Vite**; build output `dist`.
3. Env var: `VITE_API_URL=https://<your-backend>.onrender.com`.
4. `vercel.json` is already configured to rewrite all routes to `index.html` (SPA routing).
5. Deploy → e.g. `https://new-result-analysis-system-6zcb.vercel.app`.

### ⚠️ Production checklist

- **Firestore security rules:** restrict reads/writes to authenticated users (or a server-side admin flow) — do **not** expose the database in public rules.
- **CORS:** the backend always allows `http://localhost:5173` and your Vercel origin; add any other origins via `CORS_ORIGINS`.
- **Secrets:** `FIREBASE_API_KEY` etc. are injected as env vars on Render — never commit your real `.env`.

---

## 🧯 Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `Request failed with status code 500` (empty body) | Vite dev proxy target mismatch / backend not running | Ensure backend runs on port **5000**; keep `vite.config.js` proxy at `localhost:5000` |
| **Network Error** in browser | Render free-tier cold start (API sleeps after ~15 min idle) | Wait 30–60 s and retry; first request wakes the instance |
| CORS blocked on registration/login | Backend origin list missing the frontend URL | `CORS_ORIGINS` env var or code-level required origins (both include local & Vercel by default) |
| HTTP 422 `String should match pattern '^(teacher\|student)$'` | `role` sent capitalized (`"Teacher"`) | The UI sends lowercase `teacher`/`student` automatically |
| `Objects are not valid as a React child` | Rendering raw API error objects | Shared `getErrorMessage()` in `api/client.js` converts validation errors to readable text |

---

## 🤝 Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature`.
3. Commit your changes with a clear message.
4. Push and open a Pull Request describing the change.

---

## 📄 Credits & License

**Developed by Sakshi, Rahul, Sakshi** — Smart Result Analysis System.

This project is provided as an open educational tool. You are free to use, modify, and adapt it for your institution.

---

<div align="center">

**🎯 Upload. Analyze. Predict. — Smart Result Analysis System**

</div>
