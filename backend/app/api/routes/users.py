from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db, require_roles
from app.models.user import User, UserRole
from app.schemas.auth import UserRead
from app.services.user_service import list_users

router = APIRouter()


@router.get("/", response_model=list[UserRead], dependencies=[Depends(require_roles(UserRole.admin))])
def read_users(db: Session = Depends(get_db)) -> list[User]:
    return list_users(db)


@router.get("/me", response_model=UserRead)
def read_my_profile(current_user: User = Depends(get_current_user)) -> User:
    return current_user

