import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError

from app.auth.config import auth_settings
from app.auth.schemas import TokenPayload

ALGORITHM = "HS256"


def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.now(UTC) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    return jwt.encode(to_encode, auth_settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, auth_settings.SECRET_KEY, algorithms=[ALGORITHM])


def read_access_subject(token: str) -> uuid.UUID | None:
    """Return the user id an access token authenticates, or None if invalid.

    Owns all JWT-level failure handling so callers never touch the ``jwt``
    library: a bad signature, expired token, malformed payload, or non-UUID
    subject all collapse to ``None``.
    """
    try:
        payload = decode_token(token)
        return uuid.UUID(TokenPayload(**payload).sub)
    except (InvalidTokenError, ValidationError, ValueError):
        return None


def generate_password_reset_token(email: str) -> str:
    delta = timedelta(hours=auth_settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.now(UTC)
    expires = now + delta
    return jwt.encode(
        {"exp": expires.timestamp(), "nbf": now, "sub": email},
        auth_settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )


def verify_password_reset_token(token: str) -> str | None:
    try:
        decoded_token = decode_token(token)
        return str(decoded_token["sub"])
    except InvalidTokenError:
        return None
