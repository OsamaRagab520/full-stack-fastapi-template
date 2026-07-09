from app.core.exceptions import HTTPDomainError
from app.core.i18n import _


class InvalidCredentialsError(HTTPDomainError):
    status_code = 400
    detail = _("Incorrect email or password")


class InactiveUserError(HTTPDomainError):
    status_code = 400
    detail = _("Inactive user")


class InvalidTokenError(HTTPDomainError):
    status_code = 400
    detail = _("Invalid token")


class CouldNotValidateCredentialsError(HTTPDomainError):
    status_code = 403
    detail = _("Could not validate credentials")
