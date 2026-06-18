import secrets
import warnings
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self
from pydantic import model_validator


class AuthConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    @model_validator(mode="after")
    def _check_secret_key(self) -> Self:
        if self.SECRET_KEY == "changethis":
            message = (
                'The value of SECRET_KEY is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)
        return self


auth_settings = AuthConfig()  # type: ignore
