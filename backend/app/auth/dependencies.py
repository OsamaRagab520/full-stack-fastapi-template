from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.auth.exceptions import CouldNotValidateCredentialsError, InactiveUserError
from app.auth.tokens import read_access_subject
from app.core.config import settings
from app.core.db import SessionDep
from app.users.exceptions import UserAccessDeniedError, UserNotFoundError
from app.users.models import User
from app.users.selectors import get_user

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

TokenDep = Annotated[str, Depends(reusable_oauth2)]


async def get_current_user(session: SessionDep, token: TokenDep) -> User:
    user_id = read_access_subject(token)
    if user_id is None:
        raise CouldNotValidateCredentialsError
    user = await get_user(session=session, user_id=user_id)
    if user is None:
        raise UserNotFoundError
    if not user.is_active:
        raise InactiveUserError
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise UserAccessDeniedError
    return current_user
