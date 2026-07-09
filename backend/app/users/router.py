import uuid
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, Query, status

from app.auth.dependencies import CurrentUser, get_current_active_superuser
from app.core.db import SessionDep
from app.core.i18n import _, translate
from app.emails.config import email_settings
from app.emails.service import generate_new_account_email, send_email
from app.models import Message
from app.users import selectors as users_selectors
from app.users import service as users_service
from app.users.schemas import (
    UpdatePassword,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UsersPublic,
)
async def read_users(
    session: SessionDep,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
) -> Any:
    """
    Retrieve users.
    """
    users, count = await users_selectors.list_users(
        session=session, skip=skip, limit=limit
    )
    return {"data": users, "count": count}


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Email already registered"},
    },
)
async def create_user(
    *, session: SessionDep, user_in: UserCreate, bg: BackgroundTasks
) -> Any:
    """
    Create new user.
    """
    user = await users_service.create_user(session=session, user_create=user_in)
    if email_settings.emails_enabled and user_in.email:
        email_data = generate_new_account_email(
            username=user_in.email, locale=user_in.locale
        )
        bg.add_task(
            send_email,
            email_to=user_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    return user


@router.patch(
    "/me",
    response_model=UserPublic,
    responses={
        status.HTTP_409_CONFLICT: {"description": "Email already in use"},
    },
)
async def update_user_me(
    *, session: SessionDep, user_in: UserUpdateMe, current_user: CurrentUser
) -> Any:
    """
    Update own user.
    """
    return await users_service.update_user_me(
        session=session, db_user=current_user, user_in=user_in
    )


@router.patch(
    "/me/password",
    response_model=Message,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Wrong current password or same password"
        },
    },
)
async def update_password_me(
    *, session: SessionDep, body: UpdatePassword, current_user: CurrentUser
) -> Any:
    """
    Update own password.
    """
    await users_service.change_password(
        session=session,
        user=current_user,
        current_password=body.current_password,
        new_password=body.new_password,
    )
    return Message(message=translate(_("Password updated successfully")))


@router.get("/me", response_model=UserPublic)
async def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    return current_user


@router.delete(
    "/me",
    response_model=Message,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "Superusers cannot delete themselves"
        },
    },
)
async def delete_user_me(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Delete own user.
    """
    await users_service.delete_own_account(session=session, user=current_user)
    return Message(message=translate(_("User deleted successfully")))


@router.post(
    "/signup",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Email already registered"},
    },
)
async def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    """
    Create new user without the need to be logged in.
    """
    user_create = UserCreate.model_validate(user_in)
    return await users_service.create_user(session=session, user_create=user_create)


@router.get(
    "/{user_id}",
    response_model=UserPublic,
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "Not enough privileges"},
        status.HTTP_404_NOT_FOUND: {"description": "User not found"},
    },
)
async def read_user_by_id(
    user_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific user by id.
    """
    return await users_service.get_user_for_viewer(
        session=session, user_id=user_id, acting_user=current_user
    )


@router.patch(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "User not found"},
        status.HTTP_409_CONFLICT: {"description": "Email already in use"},
    },
)
async def update_user(
    *,
    session: SessionDep,
    user_id: uuid.UUID,
    user_in: UserUpdate,
) -> Any:
    """
    Update a user.
    """
    db_user = await users_service.get_user_or_raise(session=session, user_id=user_id)
    return await users_service.update_user(
        session=session, db_user=db_user, user_in=user_in
    )


@router.delete(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "Superusers cannot delete themselves"
        },
        status.HTTP_404_NOT_FOUND: {"description": "User not found"},
    },
)
async def delete_user(
    session: SessionDep, current_user: CurrentUser, user_id: uuid.UUID
) -> Message:
    """
    Delete a user.
    """
    user = await users_service.get_user_or_raise(session=session, user_id=user_id)
    await users_service.delete_user(
        session=session, db_user=user, acting_user=current_user
    )
    return Message(message=translate(_("User deleted successfully")))
