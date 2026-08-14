import requests

from config import API_URL


class ApiError(Exception):
    def __init__(self, message: str, status: int = None):
        super().__init__(message)
        self.message = message
        self.status = status


class APIClient:
    """Requests-based mirror of the React `api/client.js` wrapper."""

    def __init__(self):
        self.token = None
        self.session = requests.Session()

    def set_token(self, token):
        self.token = token

    def _headers(self):
        headers = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _request(self, method: str, path: str, **kwargs):
        url = f"{API_URL}/api{path}"
        kwargs.setdefault("headers", self._headers())
        kwargs["timeout"] = 120
        try:
            resp = self.session.request(method, url, **kwargs)
        except requests.exceptions.ConnectionError:
            raise ApiError(
                f"Cannot reach backend at {API_URL}. "
                "Start the FastAPI server first: uvicorn app.main:app --reload --port 8000"
            )
        except requests.exceptions.RequestException as e:
            raise ApiError(str(e))

        if resp.status_code in (401, 403):
            raise ApiError("Invalid or expired session. Please sign in again.", resp.status_code)

        try:
            data = resp.json()
        except ValueError:
            data = {}

        if resp.status_code >= 400:
            if isinstance(data, dict):
                detail = data.get("detail") or data.get("message") or resp.text
            else:
                detail = resp.text
            raise ApiError(detail or "Something went wrong. Please try again.", resp.status_code)
        return data

    # ---------------- auth ----------------
    def login(self, email: str, password: str):
        data = self._request("POST", "/auth/login", json={"email": email, "password": password})
        self.token = data["token"]
        return data

    def register(self, email: str, password: str, name: str, role: str):
        data = self._request(
            "POST", "/auth/register",
            json={"email": email, "password": password, "name": name, "role": role},
        )
        self.token = data["token"]
        return data

    # ---------------- results ----------------
    def analyze(self, file_bytes, file_name: str):
        return self._request(
            "POST", "/results/analyze",
            files={"file": (file_name, file_bytes, "application/pdf")},
        )

    def save_result(self, payload: dict):
        return self._request("POST", "/results/save", json=payload)

    def list_results(self):
        return self._request("GET", "/results/")

    def get_result(self, result_id: str):
        return self._request("GET", f"/results/{result_id}")

    # ---------------- students ----------------
    def identifiers(self):
        return self._request("GET", "/students/identifiers")

    def history(self, prn: str):
        return self._request("GET", "/students/history", params={"prn": prn})

    # ---------------- overview ----------------
    def overview(self):
        return self._request("GET", "/overview/")


client = APIClient()
