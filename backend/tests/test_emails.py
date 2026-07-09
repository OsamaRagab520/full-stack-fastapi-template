from app.emails.service import (
    _load_email_template,
    generate_reset_password_email,
    generate_test_email,
    render_email_template,
)


def test_render_email_template_returns_html() -> None:
    html = render_email_template(
        template_name="test_email.html",
        context={"project_name": "Acme", "t": {"line": "Test email for: a@b.com"}},
    )
    assert isinstance(html, str)
    assert html  # non-empty


def test_load_email_template_is_cached() -> None:
    _load_email_template.cache_clear()
    render_email_template(
        template_name="test_email.html",
        context={"project_name": "Acme", "t": {"line": "Test email for: a@b.com"}},
    )
    render_email_template(
        template_name="test_email.html",
        context={"project_name": "Beta", "t": {"line": "Test email for: c@d.com"}},
    )
    info = _load_email_template.cache_info()
    assert info.misses == 1  # file read/compiled exactly once
    assert info.hits >= 1  # second call served from cache


def test_generate_test_email_renders() -> None:
    data = generate_test_email(email_to="user@example.com")
    assert data.subject
    assert data.html_content


def test_reset_password_email_localized_by_locale() -> None:
    en = generate_reset_password_email(email="a@b.com", token="tok", locale="en")
    ar = generate_reset_password_email(email="a@b.com", token="tok", locale="ar")
    assert "Reset password" in en.html_content
    assert "إعادة تعيين كلمة المرور" in ar.html_content
    assert "Reset password" not in ar.html_content
