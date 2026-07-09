from unittest.mock import patch

import pytest
from httpx import AsyncClient

from app.core.config import settings

pytestmark = pytest.mark.anyio


async def test_test_email_sends_when_configured(
    client: AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    with (
        patch("app.emails.service.send_email", return_value=None),
        patch("app.emails.config.email_settings.SMTP_HOST", "smtp.example.com"),
    ):
        r = await client.post(
            f"{settings.API_V1_STR}/utils/test-email/?email_to=test@example.com",
            headers=superuser_token_headers,
        )
    assert r.status_code == 202
    assert r.json()["message"] == "Test email sent"


async def test_test_email_reports_when_not_configured(
    client: AsyncClient, superuser_token_headers: dict[str, str]
) -> None:
    # emails are disabled by default in the test environment (no SMTP_HOST), so
    # the diagnostic endpoint must say so rather than claim success.
    r = await client.post(
        f"{settings.API_V1_STR}/utils/test-email/?email_to=test@example.com",
        headers=superuser_token_headers,
    )
    assert r.status_code == 503
    assert r.json()["detail"] == "Email delivery is not configured"

    r_ar = await client.post(
        f"{settings.API_V1_STR}/utils/test-email/?email_to=test@example.com",
        headers={**superuser_token_headers, "Accept-Language": "ar"},
    )
    assert r_ar.status_code == 503
    assert r_ar.json()["detail"] == "خدمة إرسال البريد الإلكتروني غير مُهيأة"
