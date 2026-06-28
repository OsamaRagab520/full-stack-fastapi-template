from app.core.exceptions import HTTPDomainError


class InvalidCredentialsError(HTTPDomainError):
    status_code = 400
    detail = "Incorrect email or password"


class InactiveUserError(HTTPDomainError):
    status_code = 400
    detail = "Inactive user"


class InvalidTokenError(HTTPDomainError):
    status_code = 400
    detail = "Invalid token"
