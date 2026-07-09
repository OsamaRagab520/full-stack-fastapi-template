from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, BackgroundTasks, Depends, status
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from starlette.requests import Request

from app.auth import service as auth_service
from app.auth.config import auth_settings
from app.auth.dependencies import CurrentUser, get_current_active_superuser
from app.auth.schemas import NewPassword, Token
from app.auth.tokens import create_access_token, generate_password_reset_token
from app.core.db import SessionDep
from app.core.i18n import _, translate
from app.core.rate_limit import limiter
from app.emails.service import generate_reset_password_email, send_reset_password_email
from app.models import Message
from app.users import selectors as users_selectors
from app.users import service as users_service
from app.users.exceptions import UserNotFoundError
from app.users.schemas import UserPublic, UserUpdate

router = APIRouter(tags=["login"])


@router.post(
    "/login/access-token",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Incorrect credentials or inactive user"
        },
    },
)
@limiter.limit("5/minute")
async def login_access_token(
    request: Request,
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await auth_service.login(
        session=session, email=form_data.username, password=form_data.password
    )
    access_token_expires = timedelta(minutes=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=create_access_token(user.id, expires_delta=access_token_expires)
    )


@router.post("/login/test-token", response_model=UserPublic)
async def test_token(current_user: CurrentUser) -> Any:
    """
    Test access token
    """
    return current_user


@router.post("/password-recovery/{email}")
@limiter.limit("3/minute")
async def recover_password(
    request: Request, email: str, session: SessionDep, bg: BackgroundTasks
) -> Message:
    """
    Password Recovery
    """
    user = await users_selectors.get_user_by_email(session=session, email=email)

    if user:
        password_reset_token = generate_password_reset_token(email=email)
        send_reset_password_email(
            bg, email_to=user.email, token=password_reset_token, locale=user.locale
        )
    return Message(
        message=translate(
            _("If that email is registered, we sent a password recovery link")
        )
    )


@router.post(
    "/reset-password/",
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid token or inactive user"},
    },
)
async def reset_password(session: SessionDep, body: NewPassword) -> Message:
    """
    Reset password
    """
    user = await auth_service.resolve_reset_password_user(
        session=session, token=body.token
    )
    await users_service.update_user(
        session=session,
        db_user=user,
        user_in=UserUpdate(password=body.new_password),
    )
    return Message(message=translate(_("Password updated successfully")))


@router.post(
    "/password-recovery-html-content/{email}",
    dependencies=[Depends(get_current_active_superuser)],
    response_class=HTMLResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "User not found"},
    },
)
async def recover_password_html_content(email: str, session: SessionDep) -> Any:
    """
    HTML Content for Password Recovery
    """
    user = await users_selectors.get_user_by_email(session=session, email=email)
    if user is None:
        raise UserNotFoundError
    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(
        email=email, token=password_reset_token, locale=user.locale
    )

    return HTMLResponse(
        content=email_data.html_content,
        headers={"X-Email-Subject": email_data.subject},
    )
