from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError

from app.auth.exceptions import CouldNotValidateCredentialsError, InactiveUserError
from app.auth.schemas import TokenPayload
from app.auth.tokens import decode_token
from app.core.config import settings
from app.core.db import SessionDep
from app.users.exceptions import UserAccessDeniedError, UserNotFoundError
from app.users.models import User

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

TokenDep = Annotated[str, Depends(reusable_oauth2)]


async def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = decode_token(token)
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise CouldNotValidateCredentialsError
    user = await session.get(User, token_data.sub)
    if not user:
        raise UserNotFoundError
    if not user.is_active:
        raise InactiveUserError
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise UserAccessDeniedError
    return current_user
