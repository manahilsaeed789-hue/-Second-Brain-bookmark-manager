"""Authentication API routes."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from backend.auth import (
    authenticate_user,
    create_user,
    get_current_user,
    get_session_max_age,
)
from backend.database import get_db
from backend.models import User
from backend.schemas import UserLogin, UserRegister, UserResponse

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse)
async def register(data: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email.lower()).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    user = create_user(db, data.email, data.username, data.password)
    return UserResponse.model_validate(user)


@router.post("/login")
async def login(data: UserLogin, request: Request, db: Session = Depends(get_db)):
    user = authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    request.session["user_id"] = user.id
    request.session["username"] = user.username
    max_age = get_session_max_age(data.remember_me)
    request.session.setdefault("_max_age", max_age)

    return {"message": "Login successful", "user": UserResponse.model_validate(user)}


@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    return UserResponse.model_validate(user)
