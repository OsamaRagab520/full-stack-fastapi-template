from app.core.exceptions import HTTPDomainError


class ItemNotFoundError(HTTPDomainError):
    status_code = 404
    detail = "Item not found"


class ItemAccessDeniedError(HTTPDomainError):
    status_code = 403
    detail = "Not enough permissions"
