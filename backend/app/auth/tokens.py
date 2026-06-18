from datetime import UTC, datetime, timedelta

import jwt
from jwt.exceptions import InvalidTokenError

from app.auth.config import auth_settings
from app.core import security


def generate_password_reset_token(email: str) -> str:
    delta = timedelta(hours=auth_settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.now(UTC)
    expires = now + delta
    encoded_jwt = jwt.encode(
        {"exp": expires.timestamp(), "nbf": now, "sub": email},
        auth_settings.SECRET_KEY,
        algorithm=security.ALGORITHM,
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> str | None:
    try:
        decoded_token = security.decode_token(token)
        return str(decoded_token["sub"])
    except InvalidTokenError:
        return None
