# 🎓 Smart Result Analysis System

**Smart Result Analysis System** is an advanced web application designed for educational institutions to automate the extraction, analysis, and storage of student examination results.

It transforms static PDF marksheets into dynamic, interactive dashboards, allowing teachers to track batch performance and students to visualize their academic growth over time.

---

## 🧠 How It Works (The Logic)

### 1. 📄 The "Reading" Algorithm (PDF Parsing)
The computer reads the PDF file line by line using **PyPDF2**.
*   **Segmentation:** The code looks for the keyword **"SEAT NO.:"**. Every time it finds this word, it knows a new student's record is starting. It cuts the text into blocks, one for each student.
*   **Extraction (Regex):** Inside each student's block, the code uses "Regular Expressions" (pattern matching) to find specific data:
    *   *Find a pattern like "722..."* → That's the **PRN**.
    *   *Find a number after "SGPA :"* → That's the **Result**.
    *   *Find lines with course codes (e.g., "210242")* → These are **Subjects**.

### 2. 🔮 The "Prediction" Algorithm (AI)
We use a mathematical concept called **Linear Regression** (via `scikit-learn`).
*   **Logic:** If a student scored 7.0 in Sem 1, 7.5 in Sem 2, and 8.0 in Sem 3, the algorithm draws a straight line through these points to guess where the next point (Sem 4) will land.
*   **Goal:** To give students an estimated target for their next exam based on their current trajectory.

### 3. ☁️ The "Memory" System (Cloud Storage)
We save data to **Google Firebase**.
*   **Structure:** We store data in a "NoSQL" format (like a giant JSON file).
*   **Linking:** When you upload a new file, the system checks the **PRN**. If that PRN already exists in the database from a previous exam, the system links the new result to that student's history, creating a complete timeline.

---

## 📂 Project Structure

```
├── backend/                 # FastAPI REST API
│   ├── app/
│   │   ├── main.py          # App entry point (routes, CORS, error handlers)
│   │   ├── config.py        # Firebase config + CORS origins (env-driven)
│   │   ├── firebase_manager.py  # Firebase Auth + Firestore REST client
│   │   ├── analyzer.py      # PDF parsing + AI predictions
│   │   ├── deps.py          # Shared dependencies
│   │   ├── schemas.py       # Pydantic request/response models
│   │   └── routers/
│   │       ├── auth.py      # Login / Register
│   │       ├── results.py   # PDF upload & analysis
│   │       ├── students.py  # Global student search & history
│   │       └── overview.py  # Batch analytics
│   ├── requirements.txt
│   ├── render.yaml          # Render.com deployment config
│   └── .env.example         # Firebase env template
│
├── frontend/                # React (Vite) SPA
│   ├── src/
│   │   ├── main.jsx / App.jsx
│   │   ├── config.js        # Grades, colors, departments
│   │   ├── api/client.js    # API wrapper
│   │   ├── context/AuthContext.jsx
│   │   ├── pages/           # LoginPage, TeacherDashboard, StudentDashboard
│   │   └── components/      # Charts, tables, profile cards, UI primitives
│   ├── index.html
│   ├── vercel.json          # Vercel deployment config
│   └── .env.example
│
├── mathematical_model.txt   # Formal math model behind the analytics
└── README.md
```

---

## 🛠️ Tech Stack

*   **Frontend:** React + Vite (SPA)
*   **Backend:** FastAPI (Python REST API)
*   **Database:** Google Firebase Firestore (NoSQL Cloud DB)
*   **Authentication:** Firebase Auth (Email/Password)
*   **Data Processing:**
    *   `Pandas` (Data Tables)
    *   `PyPDF2` (PDF Reading)
    *   `Regex` (Pattern Matching)
*   **Visualization:** Chart.js (Interactive Charts)
*   **Machine Learning:** `Scikit-Learn` (Linear Regression for predictions)

---

## Installation and Setup Guide

### Prerequisites

- **Python** 3.9+ and **Node.js** 18+ installed.
- A **Google Firebase Project** with Firestore and Authentication enabled.
- A stable internet connection for installing dependencies.

### 1. Backend (FastAPI)

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows (use: source venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
cp .env.example .env         # fill in your Firebase values
uvicorn main:app --reload --port 8000
```

The API is now available at `http://localhost:8000` (docs at `/docs`).

### 2. Frontend (React + Vite)

```bash
cd frontend
npm install
cp .env.example .env.local   # set VITE_API_URL (empty = uses Vite dev proxy)
npm run dev
```

The app will open at `http://localhost:5173` and proxy API calls to the backend.

---

## 🌟 Features Breakdown

### 👨‍🏫 For Teachers
1.  **Upload & Analyze:**
    *   Upload a PDF marksheet.
    *   Get instant stats: Pass %, Average SGPA, Failure Count.
    *   View "Critical Subjects" (subjects where most students failed).
2.  **Global Search:**
    *   Search for any student by Name or PRN across *all* uploaded exams.
    *   See their complete history in one place.
3.  **Cloud Sync:**
    *   Save analyzed data to the cloud with one click.
    *   Access saved reports anytime from the "Saved" tab.

### 👨‍🎓 For Students
1.  **Personal Dashboard:**
    *   Login to view your specific results.
    *   See a graph of your SGPA growth.
2.  **AI Prediction:**
    *   The system predicts your *next* SGPA based on your past performance trend.
3.  **Downloadable Reports:**
    *   Download your history or specific semester results as Excel files.

---

## 📊 Database Schema (Firestore)

The app uses two main collections in Firebase:

**1. `users` Collection**
*   Stores user profiles (Email, Role, Name).

**2. `result_files` Collection**
*   Stores the parsed data from every PDF uploaded.
*   **Fields:**
    *   `exam_tag`: e.g., "SE Computer 2024"
    *   `students_data`: A huge array containing every student's marks from that PDF.
    *   `summary`: Pre-calculated stats (Avg SGPA, Pass Rate).

---

## 🤝 Contributing

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature-branch`).
3.  Commit your changes.
4.  Push to the branch.
5.  Open a Pull Request.

---

**Developed by Sakshi, Rahul, Sakshi** | Smart Result Analysis System
