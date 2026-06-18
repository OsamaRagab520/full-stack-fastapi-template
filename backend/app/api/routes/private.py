from typing import Any

from fastapi import APIRouter, status
from pydantic import BaseModel

from app.api.deps import SessionDep
from app.models import UserPublic
from app.users import service as users_service
from app.users.schemas import UserCreate

router = APIRouter(tags=["private"], prefix="/private")


class PrivateUserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    is_verified: bool = False


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
