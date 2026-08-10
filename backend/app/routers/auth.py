from fastapi import APIRouter, Depends

from ..firebase_manager import FirebaseManager
from ..schemas import LoginRequest, RegisterRequest, UserResponse
from .auth_helpers import handle_firebase_error

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
def register(request: RegisterRequest):
    fm = FirebaseManager()
    try:
        user_id = fm.create_user(request.email, request.password, request.role, request.name)
        return UserResponse(
            uid=user_id,
            email=request.email,
            name=request.name,
            role=request.role.lower(),
            token=fm.id_token,
        )
    except Exception as e:
        handle_firebase_error(e)


@router.post("/login", response_model=UserResponse)
def login(request: LoginRequest):
    fm = FirebaseManager()
    try:
        user = fm.verify_user(request.email, request.password)
        return UserResponse(
            uid=user["uid"],
            email=user["email"],
            name=user["name"],
            role=user["role"],
            token=user["token"],
        )
    except Exception as e:
        handle_firebase_error(e)
