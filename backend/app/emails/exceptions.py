from app.core.exceptions import HTTPDomainError
from app.core.i18n import _


class EmailDeliveryNotConfiguredError(HTTPDomainError):
    status_code = 503
    detail = _("Email delivery is not configured")
