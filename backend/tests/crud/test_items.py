import uuid

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from app.items import service as items_service
from app.items.exceptions import ItemAccessDeniedError, ItemNotFoundError
from app.items.models import Item
from app.items.schemas import ItemCreate, ItemUpdate
from app.users.models import User
from tests.utils.user import create_random_user
from tests.utils.utils import random_lower_string

pytestmark = pytest.mark.anyio


async def _create_item(db: AsyncSession, owner: User) -> Item:
    item_in = ItemCreate(title=random_lower_string(), description=random_lower_string())
    return await items_service.create_item(
        session=db, item_in=item_in, owner_id=owner.id
    )


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
    owner = await create_random_user(db)
    item = await _create_item(db, owner)
    new_title = random_lower_string()
    item_in = ItemUpdate(title=new_title)
    updated = await items_service.update_item(
        session=db, item_id=item.id, item_in=item_in, acting_user=owner
    )
    assert updated.title == new_title
    assert updated.id == item.id
    assert updated.owner_id == item.owner_id


async def test_update_item_description(db: AsyncSession) -> None:
    owner = await create_random_user(db)
    item = await _create_item(db, owner)
    new_description = random_lower_string()
    item_in = ItemUpdate(title=item.title, description=new_description)
    updated = await items_service.update_item(
        session=db, item_id=item.id, item_in=item_in, acting_user=owner
    )
    assert updated.description == new_description


async def test_update_item_partial(db: AsyncSession) -> None:
    """Partial update: only title sent; description must be unchanged."""
    owner = await create_random_user(db)
    item = await _create_item(db, owner)
    original_description = item.description
    new_title = random_lower_string()
    item_in = ItemUpdate(title=new_title)
    updated = await items_service.update_item(
        session=db, item_id=item.id, item_in=item_in, acting_user=owner
    )
    assert updated.title == new_title
    assert updated.description == original_description


async def test_delete_item(db: AsyncSession) -> None:
    owner = await create_random_user(db)
    item = await _create_item(db, owner)
    item_id = item.id
    await items_service.delete_item(session=db, item_id=item_id, acting_user=owner)
    deleted = await db.get(Item, item_id)
    assert deleted is None


async def test_get_item_for_user_not_found(db: AsyncSession) -> None:
    user = await create_random_user(db)
    with pytest.raises(ItemNotFoundError):
        await items_service.get_item_for_user(
            session=db, item_id=uuid.uuid4(), acting_user=user
        )


async def test_get_item_for_user_denied_for_non_owner(db: AsyncSession) -> None:
    owner = await create_random_user(db)
    other = await create_random_user(db)
    item = await _create_item(db, owner)
    with pytest.raises(ItemAccessDeniedError):
        await items_service.get_item_for_user(
            session=db, item_id=item.id, acting_user=other
        )


async def test_superuser_can_access_any_item(db: AsyncSession) -> None:
    owner = await create_random_user(db)
    item = await _create_item(db, owner)
    superuser = await create_random_user(db)
    superuser.is_superuser = True
    db.add(superuser)
    await db.commit()
    fetched = await items_service.get_item_for_user(
        session=db, item_id=item.id, acting_user=superuser
    )
    assert fetched.id == item.id


async def test_update_item_denied_for_non_owner(db: AsyncSession) -> None:
    owner = await create_random_user(db)
    other = await create_random_user(db)
    item = await _create_item(db, owner)
    with pytest.raises(ItemAccessDeniedError):
        await items_service.update_item(
            session=db,
            item_id=item.id,
            item_in=ItemUpdate(title=random_lower_string()),
            acting_user=other,
        )
