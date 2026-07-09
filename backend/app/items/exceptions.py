from app.core.exceptions import HTTPDomainError
from app.core.i18n import _


class ItemNotFoundError(HTTPDomainError):
    status_code = 404
    detail = _("Item not found")


class ItemAccessDeniedError(HTTPDomainError):
    status_code = 403
    detail = _("Not enough permissions")
