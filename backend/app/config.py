import os
from typing import Dict

from dotenv import load_dotenv

load_dotenv()


def _env_or(key: str, default: str) -> str:
    return os.getenv(key, default).strip()


FIREBASE_CONFIG: Dict[str, str] = {
    "apiKey": _env_or("FIREBASE_API_KEY", "AIzaSyA5102WcvfwHAsJHUZhxG19U-m3vEyM-KU"),
    "authDomain": _env_or("FIREBASE_AUTH_DOMAIN", "result-alanysis.firebaseapp.com"),
    "projectId": _env_or("FIREBASE_PROJECT_ID", "result-alanysis"),
    "storageBucket": _env_or("FIREBASE_STORAGE_BUCKET", "result-alanysis.firebasestorage.app"),
    "messagingSenderId": _env_or("FIREBASE_MESSAGING_SENDER_ID", "1070766476956"),
    "appId": _env_or("FIREBASE_APP_ID", "1:1070766476956:web:2ba001712fb71204ade759"),
    "measurementId": _env_or("FIREBASE_MEASUREMENT_ID", "G-9XGXHMXR3F"),
}

FIREBASE_REST_URL = (
    f"https://firestore.googleapis.com/v1/projects/{FIREBASE_CONFIG['projectId']}"
    f"/databases/(default)/documents"
)
FIREBASE_AUTH_URL = "https://identitytoolkit.googleapis.com/v1"

ALLOWED_ORIGINS = [
    origin.strip()
    for origin in _env_or(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:3000,https://localhost:5173",
    ).split(",")
    if origin.strip()
]
