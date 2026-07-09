import uuid
from datetime import datetime

from pydantic import EmailStr, field_validator
from sqlmodel import Field, SQLModel

from app.core.config import settings
from app.users.models import UserBase


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


class UserUpdate(SQLModel):
    email: EmailStr | None = Field(default=None, max_length=255)
    is_active: bool | None = None
    is_superuser: bool | None = None
    full_name: str | None = Field(default=None, max_length=255)
    locale: str | None = Field(default=None, max_length=5)
    password: str | None = Field(default=None, min_length=8, max_length=128)

    @field_validator("locale")
    @classmethod
    def validate_locale(cls, v: str | None) -> str | None:
        if v is not None and v not in settings.SUPPORTED_LANGUAGES:
            raise ValueError(
                f"unsupported locale {v!r}; must be one of {settings.SUPPORTED_LANGUAGES}"
            )
        return v


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)
    locale: str | None = Field(default=None, max_length=5)

    @field_validator("locale")
    @classmethod
    def validate_locale(cls, v: str | None) -> str | None:
        if v is not None and v not in settings.SUPPORTED_LANGUAGES:
            raise ValueError(
                f"unsupported locale {v!r}; must be one of {settings.SUPPORTED_LANGUAGES}"
            )
        return v


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime | None = None


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int
