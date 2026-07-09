from sqlmodel.ext.asyncio.session import AsyncSession

from app.auth.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    InvalidResetTokenError,
)
from app.auth.tokens import verify_password_reset_token
from app.users import service as users_service
from app.users.models import User
from app.users.selectors import get_user_by_email


async def login(*, session: AsyncSession, email: str, password: str) -> User:
    """Authenticate, raising on bad credentials or an inactive account.

    Raises InvalidCredentialsError if the email/password pair is wrong and
    InactiveUserError if the account is disabled.
    """
    user = await users_service.authenticate(
        session=session, email=email, password=password
    )
    if user is None:
        raise InvalidCredentialsError
    if not user.is_active:
        raise InactiveUserError
    return user


async def resolve_reset_password_user(*, session: AsyncSession, token: str) -> User:
    """Resolve the user a password-reset token points at.

    Raises InvalidResetTokenError for a bad/expired token or an unknown email,
    and InactiveUserError if the account is disabled.
    """
    email = verify_password_reset_token(token=token)
    if email is None:
        raise InvalidResetTokenError
    user = await get_user_by_email(session=session, email=email)
    if user is None:
        raise InvalidResetTokenError
    if not user.is_active:
        raise InactiveUserError
    return user
