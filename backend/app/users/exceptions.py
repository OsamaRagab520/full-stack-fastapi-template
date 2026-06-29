from app.core.exceptions import HTTPDomainError
from app.core.i18n import _


class EmailAlreadyRegisteredError(HTTPDomainError):
    status_code = 400
    detail = _("The user with this email already exists in the system")


class EmailAlreadyInUseError(HTTPDomainError):
    status_code = 409
    detail = _("User with this email already exists")


class CurrentPasswordIncorrectError(HTTPDomainError):
    status_code = 400
    detail = _("Incorrect password")


class PasswordUnchangedError(HTTPDomainError):
    status_code = 400
    detail = _("New password cannot be the same as the current one")


class CannotDeleteSelfError(HTTPDomainError):
    status_code = 403
    detail = _("Super users are not allowed to delete themselves")


class UserNotFoundError(HTTPDomainError):
    status_code = 404
    detail = _("User not found")


class UserAccessDeniedError(HTTPDomainError):
    status_code = 403
    detail = _("The user doesn't have enough privileges")
