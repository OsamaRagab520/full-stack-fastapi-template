import uuid
from collections.abc import Sequence

from sqlmodel import col, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.users.models import User


async def get_user(*, session: AsyncSession, user_id: uuid.UUID) -> User | None:
    return await session.get(User, user_id)


async def get_user_by_email(*, session: AsyncSession, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return (await session.exec(statement)).first()


async def list_users(
    *, session: AsyncSession, skip: int = 0, limit: int = 100
) -> tuple[Sequence[User], int]:
    count = (await session.exec(select(func.count()).select_from(User))).one()
    statement = (
        select(User).order_by(col(User.created_at).desc()).offset(skip).limit(limit)
    )
    users = (await session.exec(statement)).all()
    return users, count
