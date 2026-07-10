from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

limiter = Limiter(key_func=get_remote_address)

# Rate limiting guards staging/production. Disable it in local so the dev
# workflow and the e2e/Playwright stack (which drive the real app over one IP
# and would otherwise trip the login/signup limits) aren't throttled. Backend
# tests disable it via a conftest fixture and re-enable it only for the
# dedicated rate-limit test.
limiter.enabled = settings.ENVIRONMENT != "local"
