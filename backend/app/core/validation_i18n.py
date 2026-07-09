from typing import Any

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.requests import Request

from app.core.i18n import _, current_locale, translate

_PYDANTIC_MSG_MAP: dict[str, str] = {
    "string_too_short": _("String should have at least {min_length} characters"),
    "string_too_long": _("String should have at most {max_length} characters"),
    "missing": _("Field required"),
    "value_error": _("Value error, {error}"),
    "string_type": _("Input should be a valid string"),
    "bool_type": _("Input should be a valid boolean"),
    "int_parsing": _("Input should be a valid integer"),
}


def _format_ctx(ctx: dict[str, Any]) -> dict[str, str]:
    """Coerce ctx values to strings so .format(**ctx) is safe."""
    return {k: str(v) for k, v in ctx.items()}


async def validation_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Translate Pydantic 422 validation error messages to the request locale."""
    assert isinstance(exc, RequestValidationError)
    locale = getattr(request.state, "locale", None) or current_locale.get()
    detail = []
    for err in exc.errors():
        error_type = err.get("type", "")
        template = _PYDANTIC_MSG_MAP.get(error_type)
        if template is not None:
            ctx = _format_ctx(err.get("ctx", {}))
            try:
                msg = translate(template, locale).format(**ctx)
            except (KeyError, IndexError):
                msg = translate(template, locale)
        else:
            msg = translate(err["msg"], locale)
        detail.append({**err, "msg": msg})
    return JSONResponse(status_code=422, content={"detail": detail})
