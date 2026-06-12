from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.dependencies import get_current_user, get_db
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.auth import Token, UserCreate, UserLogin, UserRead
from app.services.user_service import authenticate_user, create_user, get_user_by_email

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    if get_user_by_email(db, payload.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db, payload)


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> Token:
    user = authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(
        subject=str(user.id),
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        extra_claims={"role": user.role.value},
    )
    return Token(access_token=token)


@router.get("/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.post("/logout")
def logout() -> dict[str, str]:
    return {"message": "Logged out successfully"}

