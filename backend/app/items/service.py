import uuid

from sqlmodel import col, delete
from sqlmodel.ext.asyncio.session import AsyncSession

from app.items.models import Item
from app.items.schemas import ItemCreate


async def create_item(
    *, session: AsyncSession, item_in: ItemCreate, owner_id: uuid.UUID
) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)
    return db_item


async def delete_items_by_owner(*, session: AsyncSession, owner_id: uuid.UUID) -> None:
    statement = delete(Item).where(col(Item.owner_id) == owner_id)
    await session.exec(statement)
