import uuid
from collections.abc import Sequence

from sqlmodel.ext.asyncio.session import AsyncSession

from app.items import selectors
from app.items.exceptions import ItemAccessDeniedError, ItemNotFoundError
from app.items.models import Item
from app.items.schemas import ItemCreate, ItemUpdate
from app.users.models import User


async def get_item_for_user(
    *, session: AsyncSession, item_id: uuid.UUID, acting_user: User
) -> Item:
    """Load an item, enforcing that the acting user may access it.

    Raises ItemNotFoundError if it does not exist and ItemAccessDeniedError if
    the user is neither a superuser nor the owner. This is the single place the
    ownership rule lives; every read/mutate path goes through it.
    """
    item = await selectors.get_item(session=session, item_id=item_id)
    if item is None:
        raise ItemNotFoundError
    if not acting_user.is_superuser and item.owner_id != acting_user.id:
        raise ItemAccessDeniedError
    return item


async def list_items_for_user(
    *, session: AsyncSession, acting_user: User, skip: int = 0, limit: int = 100
) -> tuple[Sequence[Item], int]:
    owner_id = None if acting_user.is_superuser else acting_user.id
    return await selectors.list_items(
        session=session, owner_id=owner_id, skip=skip, limit=limit
    )


async def create_item(
    *, session: AsyncSession, item_in: ItemCreate, owner_id: uuid.UUID
) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)
    return db_item


async def update_item(
    *, session: AsyncSession, item_id: uuid.UUID, item_in: ItemUpdate, acting_user: User
) -> Item:
    db_item = await get_item_for_user(
        session=session, item_id=item_id, acting_user=acting_user
    )
    update_dict = item_in.model_dump(exclude_unset=True)
    db_item.sqlmodel_update(update_dict)
    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)
    return db_item


async def delete_item(
    *, session: AsyncSession, item_id: uuid.UUID, acting_user: User
) -> None:
    db_item = await get_item_for_user(
        session=session, item_id=item_id, acting_user=acting_user
    )
    await session.delete(db_item)
    await session.commit()
