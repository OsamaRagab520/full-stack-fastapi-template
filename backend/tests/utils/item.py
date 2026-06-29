from sqlmodel.ext.asyncio.session import AsyncSession

from app.items import service as items_service
from app.items.models import Item
from app.items.schemas import ItemCreate
from tests.utils.user import create_random_user
from tests.utils.utils import random_lower_string


async def create_random_item(db: AsyncSession) -> Item:
    user = await create_random_user(db)
    owner_id = user.id
    assert owner_id is not None
    title = random_lower_string()
    description = random_lower_string()
    item_in = ItemCreate(title=title, description=description)
    return await items_service.create_item(
        session=db, item_in=item_in, owner_id=owner_id
    )
