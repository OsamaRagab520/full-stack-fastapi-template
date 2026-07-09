from fastapi import Request
from fastapi.responses import JSONResponse


class HTTPDomainError(Exception):
    """Base for service-layer errors that map to a fixed HTTP status + detail.

    Each subclass sets ``status_code`` and ``detail``. A single handler
    (registered in ``app.main``) converts them into JSON responses, so route
    functions never catch them or raise ``HTTPException`` for domain failures:
    they simply let the exception propagate.
    """

    status_code: int = 500
    detail: str = "Internal Server Error"


async def http_domain_exception_handler(
    _request: Request, exc: Exception
) -> JSONResponse:
    assert isinstance(exc, HTTPDomainError)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
