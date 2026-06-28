import uuid
from collections.abc import Sequence

from sqlmodel import col, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.items.models import Item


async def get_item(*, session: AsyncSession, item_id: uuid.UUID) -> Item | None:
    return await session.get(Item, item_id)


async def list_items(
    *,
    session: AsyncSession,
    owner_id: uuid.UUID | None = None,
    skip: int = 0,
    limit: int = 100,
) -> tuple[Sequence[Item], int]:
    count_stmt = select(func.count()).select_from(Item)
    item_stmt = (
        select(Item).order_by(col(Item.created_at).desc()).offset(skip).limit(limit)
    )
    if owner_id is not None:
        count_stmt = count_stmt.where(Item.owner_id == owner_id)
        item_stmt = item_stmt.where(Item.owner_id == owner_id)
    count = (await session.exec(count_stmt)).one()
    items = (await session.exec(item_stmt)).all()
    return items, count
