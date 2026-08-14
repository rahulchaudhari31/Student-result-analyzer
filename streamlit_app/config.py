import os

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

API_URL = (os.getenv("STREAMLIT_API_URL") or os.getenv("API_URL") or "http://localhost:8000").rstrip("/")

GRADES = ['O', 'A+', 'A', 'B+', 'B', 'C', 'P', 'F']

GRADE_COLORS = {
    'O': '#27ae60',
    'A+': '#2ecc71',
    'A': '#58d68d',
    'B+': '#3498db',
    'B': '#5dade2',
    'C': '#aed6f1',
    'P': '#bdc3c7',
    'F': '#ef4444',
}

GRADE_POINTS = {
    'O': 10,
    'A+': 9,
    'A': 8,
    'B+': 7,
    'B': 6,
    'C': 5,
    'P': 4,
    'F': 3,
    'FF': 3,
    'AB': 2,
    'ABS': 2,
    'IC': 2,
}

FAIL_GRADES = ['F', 'FF', 'AB', 'IC', 'ABS']

DEPARTMENTS = [
    'Computer',
    'IT',
    'Mechanical',
    'Civil',
    'Electrical',
    'AIDS',
    'E&TC',
    'General Science',
]

YEARS = ['FE', 'SE', 'TE', 'BE']
