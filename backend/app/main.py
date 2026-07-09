from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.api.main import api_router
from app.core.config import settings
from app.core.exceptions import HTTPDomainError, http_domain_exception_handler
from app.core.i18n import _, current_locale, negotiate_locale, translate
from app.core.rate_limit import limiter
from app.core.validation_i18n import validation_exception_handler

_SHOW_DOCS_ENVS = {"local", "staging"}


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


class LocaleMiddleware(BaseHTTPMiddleware):
    """Resolve the request locale from Accept-Language.

    Sets ``request.state.locale`` and the ``current_locale`` context var so
    routes and the domain-exception handler translate responses consistently.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        locale = negotiate_locale(request.headers.get("accept-language", ""))
        request.state.locale = locale
        token = current_locale.set(locale)
        try:
            return await call_next(request)
        finally:
            current_locale.reset(token)


async def rate_limit_exceeded_handler(
    request: Request, _exc: Exception
) -> JSONResponse:
    locale = getattr(request.state, "locale", None) or current_locale.get()
    return JSONResponse(
        status_code=429,
        content={"detail": translate(_("Too many requests"), locale)},
    )


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
        sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
    if settings.ENVIRONMENT in _SHOW_DOCS_ENVS
    else None,
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan,
)

# Map every typed domain error to its fixed HTTP status + detail, so routes
# never catch them or raise HTTPException for domain failures.
app.add_exception_handler(HTTPDomainError, http_domain_exception_handler)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.add_middleware(LocaleMiddleware)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)
