from app.emails.service import (
    _load_email_template,
    generate_test_email,
    render_email_template,
)


def test_render_email_template_returns_html() -> None:
    html = render_email_template(
        template_name="test_email.html",
        context={"project_name": "Acme", "email": "user@example.com"},
    )
    assert isinstance(html, str)
    assert html  # non-empty


def test_load_email_template_is_cached() -> None:
    _load_email_template.cache_clear()
    render_email_template(
        template_name="test_email.html",
        context={"project_name": "Acme", "email": "user@example.com"},
    )
    render_email_template(
        template_name="test_email.html",
        context={"project_name": "Beta", "email": "other@example.com"},
    )
    info = _load_email_template.cache_info()
    assert info.misses == 1  # file read/compiled exactly once
    assert info.hits >= 1  # second call served from cache


def test_generate_test_email_renders() -> None:
    data = generate_test_email(email_to="user@example.com")
    assert data.subject
    assert data.html_content
