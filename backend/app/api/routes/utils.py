from fastapi import APIRouter, BackgroundTasks, Depends, status
from pydantic.networks import EmailStr

from app.auth.dependencies import get_current_active_superuser
from app.core.i18n import _, translate
from app.emails.config import email_settings
from app.emails.exceptions import EmailDeliveryNotConfiguredError
from app.emails.service import send_test_email
from app.models import Message

router = APIRouter(prefix="/utils", tags=["utils"])


@router.post(
    "/test-email/",
    dependencies=[Depends(get_current_active_superuser)],
    status_code=status.HTTP_202_ACCEPTED,
)
async def test_email(email_to: EmailStr, bg: BackgroundTasks) -> Message:
    """
    Test emails.
    """
    if not email_settings.emails_enabled:
        raise EmailDeliveryNotConfiguredError
    send_test_email(bg, email_to=email_to)
    return Message(message=translate(_("Test email sent")))


@router.get("/health-check/")
async def health_check() -> bool:
    return True
