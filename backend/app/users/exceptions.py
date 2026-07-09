from app.core.exceptions import HTTPDomainError


class EmailAlreadyRegisteredError(HTTPDomainError):
    status_code = 400
    detail = "The user with this email already exists in the system"


class EmailAlreadyInUseError(HTTPDomainError):
    status_code = 409
    detail = "User with this email already exists"


class CurrentPasswordIncorrectError(HTTPDomainError):
    status_code = 400
    detail = "Incorrect password"


class PasswordUnchangedError(HTTPDomainError):
    status_code = 400
    detail = "New password cannot be the same as the current one"


class CannotDeleteSelfError(HTTPDomainError):
    status_code = 403
    detail = "Super users are not allowed to delete themselves"


class UserNotFoundError(HTTPDomainError):
    status_code = 404
    detail = "User not found"


class UserAccessDeniedError(HTTPDomainError):
    status_code = 403
    detail = "The user doesn't have enough privileges"
