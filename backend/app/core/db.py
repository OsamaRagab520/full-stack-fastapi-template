from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings

async_engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI), pool_pre_ping=True)
AsyncSessionFactory = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


async def init_db(session: AsyncSession) -> None:
    # Importing here ensures all table models are registered with SQLAlchemy's
    # mapper before the first query runs.
    from app.items.models import Item  # noqa: F401
    from app.users import service as users_service
    from app.users.models import User
    from app.users.schemas import UserCreate

    user = (
        await session.exec(select(User).where(User.email == settings.FIRST_SUPERUSER))
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        await users_service.create_user(session=session, user_create=user_in)
