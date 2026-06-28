import uuid
from typing import Any, NoReturn

from fastapi import APIRouter, HTTPException, Query, status

from app.auth.dependencies import CurrentUser
from app.core.db import SessionDep
from app.items import service as items_service
from app.items.exceptions import ItemAccessDeniedError, ItemNotFoundError
from app.items.schemas import ItemCreate, ItemPublic, ItemsPublic, ItemUpdate
from app.models import Message

router = APIRouter(prefix="/items", tags=["items"])


def _raise_http(exc: ItemNotFoundError | ItemAccessDeniedError) -> NoReturn:
    """Map item domain errors onto their HTTP responses (the only place we do)."""
    if isinstance(exc, ItemNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
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
    items, count = await items_service.list_items_for_user(
        session=session, acting_user=current_user, skip=skip, limit=limit
    )
    return {"data": items, "count": count}


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
    try:
        return await items_service.get_item_for_user(
            session=session, item_id=id, acting_user=current_user
        )
    except (ItemNotFoundError, ItemAccessDeniedError) as exc:
        _raise_http(exc)


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
    return await items_service.create_item(
        session=session, item_in=item_in, owner_id=current_user.id
    )


@router.patch(
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
    try:
        return await items_service.update_item(
            session=session, item_id=id, item_in=item_in, acting_user=current_user
        )
    except (ItemNotFoundError, ItemAccessDeniedError) as exc:
        _raise_http(exc)


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
    try:
        await items_service.delete_item(
            session=session, item_id=id, acting_user=current_user
        )
    except (ItemNotFoundError, ItemAccessDeniedError) as exc:
        _raise_http(exc)
    return Message(message="Item deleted successfully")
