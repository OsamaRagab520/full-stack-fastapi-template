import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import col, func, select

from app.auth.dependencies import CurrentUser, SessionDep
from app.items import service as items_service
from app.items.models import Item
from app.items.schemas import ItemCreate, ItemPublic, ItemsPublic, ItemUpdate
from app.models import Message
from app.users.models import User

router = APIRouter(prefix="/items", tags=["items"])


def _assert_item_access(item: Item, user: User) -> None:
    if not user.is_superuser and item.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )


@router.get("/", response_model=ItemsPublic)
async def read_items(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
) -> Any:
    """
    Retrieve items.
    """
    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Item)
        count = (await session.exec(count_statement)).one()
        statement = (
            select(Item).order_by(col(Item.created_at).desc()).offset(skip).limit(limit)
        )
        items = (await session.exec(statement)).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Item)
            .where(Item.owner_id == current_user.id)
        )
        count = (await session.exec(count_statement)).one()
        statement = (
            select(Item)
            .where(Item.owner_id == current_user.id)
            .order_by(col(Item.created_at).desc())
            .offset(skip)
            .limit(limit)
        )
        items = (await session.exec(statement)).all()

    return ItemsPublic(data=items, count=count)


@router.get(
    "/{id}",
    response_model=ItemPublic,
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "Not enough permissions"},
        status.HTTP_404_NOT_FOUND: {"description": "Item not found"},
    },
)
async def read_item(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    Get item by ID.
    """
    item = await session.get(Item, id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    _assert_item_access(item, current_user)
    return item


@router.post(
    "/",
    response_model=ItemPublic,
    status_code=status.HTTP_201_CREATED,
)
async def create_item(
    *, session: SessionDep, current_user: CurrentUser, item_in: ItemCreate
) -> Any:
    """
    Create new item.
    """
    item = await items_service.create_item(
        session=session, item_in=item_in, owner_id=current_user.id
    )
    return item


@router.put(
    "/{id}",
    response_model=ItemPublic,
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "Not enough permissions"},
        status.HTTP_404_NOT_FOUND: {"description": "Item not found"},
    },
)
async def update_item(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    item_in: ItemUpdate,
) -> Any:
    """
    Update an item.
    """
    item = await session.get(Item, id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    _assert_item_access(item, current_user)
    update_dict = item_in.model_dump(exclude_unset=True)
    item.sqlmodel_update(update_dict)
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


@router.delete(
    "/{id}",
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "Not enough permissions"},
        status.HTTP_404_NOT_FOUND: {"description": "Item not found"},
    },
)
async def delete_item(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an item.
    """
    item = await session.get(Item, id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    _assert_item_access(item, current_user)
    await session.delete(item)
    await session.commit()
    return Message(message="Item deleted successfully")
