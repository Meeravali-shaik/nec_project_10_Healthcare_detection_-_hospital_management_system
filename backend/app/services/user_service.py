from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.user import User, UserRole
from app.schemas.auth import UserCreate


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def create_user(db: Session, payload: UserCreate) -> User:
    user = User(
        full_name=payload.full_name,
        email=payload.email.lower(),
        phone_number=payload.phone_number,
        role=payload.role,
        password_hash=get_password_hash(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    if user.role == UserRole.patient and not user.patient_profile:
        db.add(Patient(user_id=user.id, full_name=user.full_name))
        db.commit()
        db.refresh(user)
    elif user.role == UserRole.doctor and not user.doctor_profile:
        db.add(Doctor(user_id=user.id, full_name=user.full_name, email=user.email, phone_number=user.phone_number))
        db.commit()
        db.refresh(user)

    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email.lower())
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


def list_users(db: Session) -> list[User]:
    return list(db.scalars(select(User).order_by(User.created_at.desc())).all())
