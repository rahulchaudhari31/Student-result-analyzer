import datetime
import hashlib
import time
from typing import Dict, List, Optional

import requests

from .config import FIREBASE_AUTH_URL, FIREBASE_CONFIG, FIREBASE_REST_URL


class FirebaseError(Exception):
    """Raised when Firebase operations fail."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class FirebaseManager:
    def __init__(self, id_token: Optional[str] = None, user_id: Optional[str] = None):
        self.id_token = id_token
        self.user_id = user_id

    # ------------------------------------------------------------------
    # Auth (Firebase Auth REST API)
    # ------------------------------------------------------------------
    def sign_in_with_email_password(self, email: str, password: str) -> Dict:
        auth_url = f"{FIREBASE_AUTH_URL}/accounts:signInWithPassword?key={FIREBASE_CONFIG['apiKey']}"
        auth_data = {"email": email, "password": password, "returnSecureToken": True}
        response = requests.post(auth_url, json=auth_data)
        result = response.json()
        if response.status_code != 200:
            raise FirebaseError(
                result.get('error', {}).get('message', 'Unknown error'), response.status_code
            )
        self.id_token = result.get('idToken')
        self.user_id = result.get('localId')
        return result

    def create_user_with_email_password(self, email: str, password: str, name: str) -> Dict:
        auth_url = f"{FIREBASE_AUTH_URL}/accounts:signUp?key={FIREBASE_CONFIG['apiKey']}"
        auth_data = {"email": email, "password": password, "displayName": name, "returnSecureToken": True}
        response = requests.post(auth_url, json=auth_data)
        result = response.json()
        if response.status_code != 200:
            raise FirebaseError(
                result.get('error', {}).get('message', 'Unknown error'), response.status_code
            )
        self.id_token = result.get('idToken')
        self.user_id = result.get('localId')
        return result

    # ------------------------------------------------------------------
    # Firestore helpers
    # ------------------------------------------------------------------
    def firestore_request(self, method: str, path: str, data: Optional[Dict] = None) -> Optional[Dict]:
        if not self.id_token:
            raise FirebaseError("Not authenticated", 401)
        url = f"{FIREBASE_REST_URL}/{path}"
        headers = {"Authorization": f"Bearer {self.id_token}", "Content-Type": "application/json"}
        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method == "PATCH":
                response = requests.patch(url, headers=headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                return None

            if response.status_code == 401 or response.status_code == 403:
                raise FirebaseError("Invalid or expired session", 401)
            if response.status_code == 404:
                return None
            if response.status_code not in [200, 201, 409]:
                raise FirebaseError(f"DB Error {response.status_code}: {response.text}", response.status_code)
            return response.json()
        except requests.RequestException as e:
            raise FirebaseError(f"Request Exception: {str(e)}", 500) from e

    @staticmethod
    def _to_firestore_value(value):
        if value is None:
            return {"nullValue": None}
        if isinstance(value, bool):
            return {"booleanValue": value}
        if isinstance(value, int):
            return {"integerValue": str(value)}
        if isinstance(value, float):
            return {"doubleValue": value}
        if isinstance(value, str):
            return {"stringValue": value}
        if isinstance(value, datetime.datetime):
            return {"timestampValue": value.isoformat() + "Z"}
        if isinstance(value, list):
            return {"arrayValue": {"values": [FirebaseManager._to_firestore_value(v) for v in value]}}
        if isinstance(value, dict):
            return {"mapValue": {"fields": {k: FirebaseManager._to_firestore_value(v) for k, v in value.items()}}}
        return {"stringValue": str(value)}

    @staticmethod
    def _convert_single_value(value):
        if 'stringValue' in value:
            return value['stringValue']
        if 'integerValue' in value:
            return int(value['integerValue'])
        if 'doubleValue' in value:
            return float(value['doubleValue'])
        if 'booleanValue' in value:
            return value['booleanValue']
        if 'timestampValue' in value:
            try:
                return datetime.datetime.fromisoformat(value['timestampValue'].replace('Z', '+00:00'))
            except Exception:
                return value['timestampValue']
        if 'arrayValue' in value:
            return [FirebaseManager._convert_single_value(v) for v in value['arrayValue'].get('values', [])]
        if 'mapValue' in value:
            return FirebaseManager._convert_from_firestore({'fields': value['mapValue']['fields']})
        return None

    @staticmethod
    def _convert_from_firestore(doc: Dict) -> Dict:
        fields = doc.get('fields', {})
        result = {}
        for key, value in fields.items():
            result[key] = FirebaseManager._convert_single_value(value)
        return result

    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------
    def create_user(self, email: str, password: str, role: str, name: str) -> str:
        result = self.create_user_with_email_password(email, password, name)
        user_id = result.get('localId')
        user_data = {
            "fields": {
                "email": self._to_firestore_value(email),
                "role": self._to_firestore_value(role.lower()),
                "name": self._to_firestore_value(name),
                "user_id": self._to_firestore_value(user_id),
                "created_at": self._to_firestore_value(datetime.datetime.utcnow()),
                "last_login": self._to_firestore_value(datetime.datetime.utcnow()),
            }
        }
        response = self.firestore_request("POST", f"users?documentId={user_id}", user_data)
        if not response:
            response = self.firestore_request("PATCH", f"users/{user_id}", user_data)
        return user_id

    def verify_user(self, email: str, password: str) -> Dict:
        self.sign_in_with_email_password(email, password)
        user_doc = self.firestore_request("GET", f"users/{self.user_id}")
        if not user_doc:
            raise FirebaseError("User profile not found.", 404)

        role = user_doc.get('fields', {}).get('role', {}).get('stringValue', '')
        if not role:
            raise FirebaseError("User role missing.", 400)

        return {
            'email': user_doc.get('fields', {}).get('email', {}).get('stringValue', ''),
            'role': role,
            'name': user_doc.get('fields', {}).get('name', {}).get('stringValue', ''),
            'uid': self.user_id,
            'token': self.id_token,
        }

    # ------------------------------------------------------------------
    # Result files
    # ------------------------------------------------------------------
    def save_result_data(
        self,
        file_name: str,
        exam_tag: str,
        department: str,
        year: str,
        students_data: List[Dict],
        uploaded_by: str,
        summary: Dict,
    ) -> Optional[str]:
        if not self.id_token:
            raise FirebaseError("Not authenticated", 401)

        batch_data = {
            "fields": {
                "file_name": self._to_firestore_value(file_name),
                "exam_tag": self._to_firestore_value(exam_tag),
                "department": self._to_firestore_value(department),
                "year": self._to_firestore_value(year),
                "uploaded_by": self._to_firestore_value(uploaded_by),
                "uploaded_at": self._to_firestore_value(datetime.datetime.utcnow()),
                "total_students": self._to_firestore_value(len(students_data)),
                "students_data": self._to_firestore_value(students_data),
                "summary": self._to_firestore_value(summary),
            }
        }

        doc_id = f"result_{int(time.time())}_{hashlib.md5(file_name.encode()).hexdigest()[:10]}"
        result = self.firestore_request("POST", f"result_files?documentId={doc_id}", batch_data)
        return doc_id if result else None

    def get_all_result_files(self) -> List[Dict]:
        if not self.id_token:
            raise FirebaseError("Not authenticated", 401)
        result = self.firestore_request("GET", "result_files")
        if not result or 'documents' not in result:
            return []

        files = []
        for doc in result['documents']:
            file_data = self._convert_from_firestore(doc)
            file_data['id'] = doc['name'].split('/')[-1]
            files.append(file_data)
        return sorted(files, key=lambda x: str(x.get('uploaded_at', '')), reverse=True)

    def get_all_student_identifiers(self) -> Dict[str, str]:
        files = self.get_all_result_files()
        identifiers = {}
        for file_data in files:
            for student in file_data.get('students_data', []):
                prn = str(student.get('PRN', '')).strip()
                name = str(student.get('Name', '')).strip()
                if prn:
                    identifiers[prn] = name
        return identifiers

    def get_student_history(self, search_term: str) -> List[Dict]:
        files = self.get_all_result_files()
        student_history = {}
        search_term = search_term.lower().strip()

        for file_data in files:
            exam_tag = file_data.get('exam_tag', file_data.get('file_name', 'Unknown Exam'))
            upload_date = file_data.get('uploaded_at')

            for student in file_data.get('students_data', []):
                s_name = str(student.get('Name', '')).lower()
                s_prn = str(student.get('PRN', '')).strip()
                is_match = (search_term == s_prn.lower()) or (search_term in s_name)

                if is_match:
                    if s_prn not in student_history:
                        student_history[s_prn] = {
                            'Name': student.get('Name'),
                            'PRN': s_prn,
                            'Mother': student.get('Mother Name'),
                            'Results': [],
                        }

                    result_entry = {
                        'Exam': exam_tag,
                        'Date': upload_date,
                        'SGPA': student.get('SGPA', 0),
                        'Result': student.get('Result Status'),
                        'Credits': student.get('Credits'),
                        'Seat': student.get('Seat No'),
                        'Subjects': student.get('Subjects', []),
                    }
                    if isinstance(result_entry['Date'], str):
                        try:
                            result_entry['Date'] = datetime.datetime.fromisoformat(
                                result_entry['Date'].replace('Z', '+00:00')
                            )
                        except Exception:
                            pass
                    student_history[s_prn]['Results'].append(result_entry)

        for prn in student_history:
            student_history[prn]['Results'].sort(
                key=lambda x: x['Date'] if isinstance(x['Date'], datetime.datetime) else datetime.datetime.min
            )

        return list(student_history.values())
