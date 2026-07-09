"""Internationalization helpers backed by Babel gettext catalogs.

Source strings are marked with :func:`_` (an identity marker) so ``pybabel
extract`` can build the catalog template. Actual translation happens at request
time via :func:`translate`, which looks the message up in the compiled
``.mo`` catalog for the current request locale.

The active locale is resolved per-request by ``LocaleMiddleware`` (registered
in ``app.main``), which sets both ``request.state.locale`` and the
``current_locale`` context var. Routes read the context var implicitly through
:func:`translate`; the domain-exception handler reads ``request.state.locale``
directly.
"""

import gettext as gettext_module
from contextvars import ContextVar
from functools import cache
from pathlib import Path

from app.core.config import settings

_DOMAIN = "messages"
_LOCALES_DIR = Path(__file__).resolve().parent.parent / "locales"

# Set by LocaleMiddleware for each request; defaults to the app default.
current_locale: ContextVar[str] = ContextVar(
    "current_locale", default=settings.DEFAULT_LANGUAGE
)

# Language codes (primary subtag) whose text flows right-to-left.
_RTL_LANGUAGES = frozenset({"ar", "he", "fa", "ur", "yi", "ps", "sd"})


def _(message: str) -> str:
    """Source-level marker for ``pybabel extract``.

    Returns the message unchanged; the canonical English string stays the
    gettext ``msgid`` regardless of the runtime default locale. Translation is
    deferred to :func:`translate` at response time.
    """
    return message


@cache
def _get_translation(
    locale: str,
) -> gettext_module.NullTranslations:
    try:
        return gettext_module.translation(
            _DOMAIN, localedir=str(_LOCALES_DIR), languages=[locale]
        )
    except FileNotFoundError:
        return gettext_module.NullTranslations()


def translate(message: str, locale: str | None = None) -> str:
    """Translate ``message`` (a gettext msgid) for ``locale``.

    Falls back to the current request locale, then to the app default.
    """
    resolved = locale or current_locale.get()
    return _get_translation(resolved).gettext(message)


def negotiate_locale(accept_language: str) -> str:
    """Pick the best supported locale from an ``Accept-Language`` header value."""
    for tag in accept_language.split(","):
        code = tag.split(";")[0].strip().split("-")[0].lower()
        if code and code in settings.SUPPORTED_LANGUAGES:
            return code
    return settings.DEFAULT_LANGUAGE


def get_text_direction(locale: str) -> str:
    """Return ``"rtl"`` for right-to-left languages, otherwise ``"ltr"``."""
    lang = locale.split("-")[0].split("_")[0].lower()
    return "rtl" if lang in _RTL_LANGUAGES else "ltr"
