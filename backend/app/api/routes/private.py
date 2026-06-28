from typing import Any

from fastapi import APIRouter, status
from pydantic import BaseModel, EmailStr
from sqlmodel import Field

from app.core.db import SessionDep
from app.users import service as users_service
from app.users.schemas import UserCreate, UserPublic

router = APIRouter(tags=["private"], prefix="/private")


class PrivateUserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(max_length=255)


@router.post("/users/", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: PrivateUserCreate, session: SessionDep) -> Any:
    """
    Create a new user.
    """
    user_create = UserCreate(
        email=user_in.email,
        password=user_in.password,
        full_name=user_in.full_name,
    )
    return await users_service.create_user(session=session, user_create=user_create)
