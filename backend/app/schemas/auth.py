from datetime import datetime

from pydantic import EmailStr, Field

from app.models.user import UserRole
from app.schemas.common import ORMBaseModel


class UserBase(ORMBaseModel):
    full_name: str
    email: EmailStr
    phone_number: str | None = None
    role: UserRole = UserRole.patient


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserLogin(ORMBaseModel):
    email: EmailStr
    password: str


class UserRead(UserBase):
    id: int
    created_at: datetime


class Token(ORMBaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(ORMBaseModel):
    sub: str | None = None
