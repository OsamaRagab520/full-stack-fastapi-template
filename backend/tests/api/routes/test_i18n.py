import pytest
from httpx import AsyncClient

from app.core.config import settings

pytestmark = pytest.mark.anyio


async def test_error_detail_translated_by_accept_language(client: AsyncClient) -> None:
    login_data = {"username": settings.FIRST_SUPERUSER, "password": "incorrect"}

    r_en = await client.post(
        f"{settings.API_V1_STR}/login/access-token", data=login_data
    )
    assert r_en.status_code == 400
    assert r_en.json()["detail"] == "Incorrect email or password"

    r_ar = await client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data=login_data,
        headers={"Accept-Language": "ar"},
    )
    assert r_ar.status_code == 400
    assert r_ar.json()["detail"] == "البريد الإلكتروني أو كلمة المرور غير صحيحة"


async def test_unsupported_locale_falls_back_to_default(client: AsyncClient) -> None:
    login_data = {"username": settings.FIRST_SUPERUSER, "password": "incorrect"}

    r = await client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data=login_data,
        headers={"Accept-Language": "de"},
    )
    assert r.json()["detail"] == "Incorrect email or password"
