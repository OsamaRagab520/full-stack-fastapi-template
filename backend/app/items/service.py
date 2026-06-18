import uuid

from sqlmodel import Session, col, delete

from app.items.models import Item
from app.items.schemas import ItemCreate


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def delete_items_by_owner(*, session: Session, owner_id: uuid.UUID) -> None:
    statement = delete(Item).where(col(Item.owner_id) == owner_id)
    session.exec(statement)  # type: ignore
