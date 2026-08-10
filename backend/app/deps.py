from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .firebase_manager import FirebaseError, FirebaseManager

bearer_scheme = HTTPBearer(auto_error=False)


def get_firebase_manager(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> FirebaseManager:
    """Extract the Firebase idToken from the Authorization header and
    build a token-scoped FirebaseManager."""
    if credentials is None or not credentials.credentials:
        raise FirebaseError("Missing authorization token", 401)
    return FirebaseManager(id_token=credentials.credentials)
