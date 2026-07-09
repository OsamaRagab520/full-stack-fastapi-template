from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.i18n import current_locale, translate


class HTTPDomainError(Exception):
    """Base for service-layer errors that map to a fixed HTTP status + detail.

    Each subclass sets ``status_code`` and ``detail``. ``detail`` holds the
    gettext msgid (marked with :func:`_`); it is translated to the request
    locale by :func:`http_domain_exception_handler`. A single handler
    (registered in ``app.main``) converts these into JSON responses, so route
    functions never catch them or raise ``HTTPException`` for domain failures:
    they simply let the exception propagate.
    """

    status_code: int = 500
    detail: str = "Internal Server Error"
    headers: dict[str, str] | None = None


async def http_domain_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    assert isinstance(exc, HTTPDomainError)
    locale = getattr(request.state, "locale", None) or current_locale.get()
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": translate(exc.detail, locale)},
        headers=exc.headers,
    )
