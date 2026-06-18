import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from app.items import service as items_service
from app.items.schemas import ItemCreate, ItemUpdate
from tests.utils.item import create_random_item
from tests.utils.user import create_random_user
from tests.utils.utils import random_lower_string

pytestmark = pytest.mark.anyio


async def test_create_item(db: AsyncSession) -> None:
    user = await create_random_user(db)
    title = random_lower_string()
    description = random_lower_string()
    item_in = ItemCreate(title=title, description=description)
    item = await items_service.create_item(session=db, item_in=item_in, owner_id=user.id)
    assert item.title == title
    assert item.description == description
    assert item.owner_id == user.id
    assert item.id is not None


async def test_create_item_without_description(db: AsyncSession) -> None:
    user = await create_random_user(db)
    title = random_lower_string()
    item_in = ItemCreate(title=title)
    item = await items_service.create_item(session=db, item_in=item_in, owner_id=user.id)
    assert item.title == title
    assert item.description is None
    assert item.owner_id == user.id


async def test_update_item_title(db: AsyncSession) -> None:
    item = await create_random_item(db)
    new_title = random_lower_string()
    item_in = ItemUpdate(title=new_title)
    updated = await items_service.update_item(session=db, db_item=item, item_in=item_in)
    assert updated.title == new_title
    assert updated.id == item.id
    assert updated.owner_id == item.owner_id


async def test_update_item_description(db: AsyncSession) -> None:
    item = await create_random_item(db)
    new_description = random_lower_string()
    item_in = ItemUpdate(title=item.title, description=new_description)
    updated = await items_service.update_item(session=db, db_item=item, item_in=item_in)
    assert updated.description == new_description


async def test_update_item_partial(db: AsyncSession) -> None:
    """Partial update: only title sent; description must be unchanged."""
    item = await create_random_item(db)
    original_description = item.description
    new_title = random_lower_string()
    item_in = ItemUpdate(title=new_title)
    updated = await items_service.update_item(session=db, db_item=item, item_in=item_in)
    assert updated.title == new_title
    assert updated.description == original_description


async def test_delete_item(db: AsyncSession) -> None:
    item = await create_random_item(db)
    item_id = item.id
    await items_service.delete_item(session=db, db_item=item)
    deleted = await db.get(type(item), item_id)
    assert deleted is None
