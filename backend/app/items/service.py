import uuid

from sqlmodel.ext.asyncio.session import AsyncSession

from app.items.models import Item
from app.items.schemas import ItemCreate, ItemUpdate


async def create_item(
    *, session: AsyncSession, item_in: ItemCreate, owner_id: uuid.UUID
) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)
    return db_item


async def update_item(*, session: AsyncSession, db_item: Item, item_in: ItemUpdate) -> Item:
    update_dict = item_in.model_dump(exclude_unset=True)
    db_item.sqlmodel_update(update_dict)
    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)
    return db_item


async def delete_item(*, session: AsyncSession, db_item: Item) -> None:
    await session.delete(db_item)
    await session.commit()
