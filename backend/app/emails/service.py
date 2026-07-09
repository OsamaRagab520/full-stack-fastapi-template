import logging
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Any

import emails
from jinja2 import Template

from app.auth.config import auth_settings
from app.core.config import settings
from app.core.i18n import _, current_locale, translate
from app.emails.config import email_settings

logger = logging.getLogger(__name__)


def _t(message: str, locale: str | None, **params: Any) -> str:
    """Translate ``message`` for ``locale`` and interpolate ``params``."""
    resolved = locale or current_locale.get()
    return translate(message, resolved).format(**params)


@dataclass
class EmailData:
    html_content: str
    subject: str


@cache
def _load_email_template(template_name: str) -> Template:
    template_str = (
        Path(__file__).parent.parent / "email-templates" / "build" / template_name
    ).read_text()
    return Template(template_str)


def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    return _load_email_template(template_name).render(context)


def send_email(
    *,
    email_to: str,
    subject: str = "",
    html_content: str = "",
) -> None:
    if not email_settings.emails_enabled:
        raise RuntimeError("no provided configuration for email variables")
    assert email_settings.EMAILS_FROM_EMAIL  # narrow Optional for the type checker
    message = emails.message.Message(
        subject=subject,
        html=html_content,
        mail_from=(email_settings.EMAILS_FROM_NAME, email_settings.EMAILS_FROM_EMAIL),
    )
    smtp_options: dict[str, Any] = {
        "host": email_settings.SMTP_HOST,
        "port": email_settings.SMTP_PORT,
    }
    if email_settings.SMTP_TLS:
        smtp_options["tls"] = True
    elif email_settings.SMTP_SSL:
        smtp_options["ssl"] = True
    if email_settings.SMTP_USER:
        smtp_options["user"] = email_settings.SMTP_USER
    if email_settings.SMTP_PASSWORD:
        smtp_options["password"] = email_settings.SMTP_PASSWORD
    response = message.send(to=email_to, smtp=smtp_options)
    logger.info(f"send email result: {response}")


def generate_test_email(email_to: str, locale: str | None = None) -> EmailData:
    subject = _t(
        _("{project_name} - Test email"), locale, project_name=settings.PROJECT_NAME
    )
    t = {"line": _t(_("Test email for: {email}"), locale, email=email_to)}
    html_content = render_email_template(
        template_name="test_email.html",
        context={"project_name": settings.PROJECT_NAME, "t": t},
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_reset_password_email(
    email: str, token: str, locale: str | None = None
) -> EmailData:
    subject = _t(
        _("{project_name} - Password recovery for user {email}"),
        locale,
        project_name=settings.PROJECT_NAME,
        email=email,
    )
    link = f"{settings.FRONTEND_HOST}/reset-password?token={token}"
    valid_hours = auth_settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS
    t = {
        "heading": _t(
            _("{project_name} - Password Recovery"),
            locale,
            project_name=settings.PROJECT_NAME,
        ),
        "greeting": _t(_("Hello {username}"), locale, username=email),
        "body_intro": _t(
            _(
                "We've received a request to reset your password. You can do it "
                "by clicking the button below:"
            ),
            locale,
        ),
        "cta": _t(_("Reset password"), locale),
        "or_copy": _t(
            _("Or copy and paste the following link into your browser:"), locale
        ),
        "expires": _t(
            _("This password will expire in {valid_hours} hours."),
            locale,
            valid_hours=valid_hours,
        ),
        "disclaimer": _t(
            _(
                "If you didn't request a password recovery you can disregard "
                "this email."
            ),
            locale,
        ),
    }
    html_content = render_email_template(
        template_name="reset_password.html",
        context={"link": link, "t": t},
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_new_account_email(username: str, locale: str | None = None) -> EmailData:
    subject = _t(
        _("{project_name} - New account for user {username}"),
        locale,
        project_name=settings.PROJECT_NAME,
        username=username,
    )
    t = {
        "heading": _t(
            _("{project_name} - New Account"),
            locale,
            project_name=settings.PROJECT_NAME,
        ),
        "welcome": _t(_("Welcome to your new account!"), locale),
        "details": _t(_("Here are your account details:"), locale),
        "username": _t(_("Username: {username}"), locale, username=username),
        "cta": _t(_("Go to Dashboard"), locale),
    }
    html_content = render_email_template(
        template_name="new_account.html",
        context={"link": settings.FRONTEND_HOST, "t": t},
    )
    return EmailData(html_content=html_content, subject=subject)
