from fastapi import HTTPException

from ..firebase_manager import FirebaseError


def handle_firebase_error(e: Exception):
    if isinstance(e, FirebaseError):
        raise HTTPException(status_code=e.status_code, detail=e.message)
    raise HTTPException(status_code=500, detail=str(e))
