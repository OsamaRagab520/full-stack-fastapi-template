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


async def test_invalid_token_error_translated(client: AsyncClient) -> None:
    r = await client.get(
        f"{settings.API_V1_STR}/users/me",
        headers={
            "Authorization": "Bearer not-a-real-token",
            "Accept-Language": "ar",
        },
    )
    assert r.status_code == 403
    assert r.json()["detail"] == "تعذر التحقق من بيانات الاعتماد"


async def test_superuser_privileges_error_translated(
    client: AsyncClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = await client.get(
        f"{settings.API_V1_STR}/users/",
        headers={**normal_user_token_headers, "Accept-Language": "ar"},
    )
    assert r.status_code == 403
    assert r.json()["detail"] == "لا يمتلك المستخدم صلاحيات كافية"


async def test_422_field_required_translated(client: AsyncClient) -> None:
    """Missing required field in JSON body returns an Arabic 422 msg."""
    r = await client.post(
        f"{settings.API_V1_STR}/users/signup",
        json={},
        headers={"Accept-Language": "ar"},
    )
    assert r.status_code == 422
    detail = r.json()["detail"]
    assert isinstance(detail, list)
    assert any("هذا الحقل مطلوب" in err["msg"] for err in detail)


async def test_422_string_too_short_translated(client: AsyncClient) -> None:
    """Password shorter than min_length returns an Arabic 422 msg."""
    r = await client.post(
        f"{settings.API_V1_STR}/users/signup",
        json={"email": "new@example.com", "password": "abc"},
        headers={"Accept-Language": "ar"},
    )
    assert r.status_code == 422
    detail = r.json()["detail"]
    assert isinstance(detail, list)
    assert any("حرف على الأقل" in err["msg"] for err in detail)
