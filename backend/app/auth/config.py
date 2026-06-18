import secrets
import warnings
from typing import Self

from pydantic import model_validator

from app.core.config import AppBaseConfig


class AuthConfig(AppBaseConfig):
    SECRET_KEY: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48

    @model_validator(mode="after")
    def _check_secret_key(self) -> Self:
        if not self.SECRET_KEY:
            if self.ENVIRONMENT == "local":
                object.__setattr__(self, "SECRET_KEY", secrets.token_urlsafe(32))
            else:
                raise ValueError("SECRET_KEY must be set in .env for non-local environments")
        elif self.SECRET_KEY == "changethis":
            message = (
                'The value of SECRET_KEY is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)
        return self


auth_settings = AuthConfig()
