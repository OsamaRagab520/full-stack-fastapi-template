from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings


def _utc_now() -> datetime:
    return datetime.now(UTC)

async_engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI), pool_pre_ping=True)
AsyncSessionFactory = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db)]


async def init_db(session: AsyncSession) -> None:
    # Importing here ensures all table models are registered with SQLAlchemy's
    # mapper before the first query runs.
    from app.items.models import Item  # noqa: F401
    from app.users import service as users_service
    from app.users.models import User  # noqa: F401
    from app.users.schemas import UserCreate
    from app.users.selectors import get_user_by_email

    user = await get_user_by_email(session=session, email=settings.FIRST_SUPERUSER)
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        await users_service.create_user(session=session, user_create=user_in)
