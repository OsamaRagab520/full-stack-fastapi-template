"""
Backward-compatibility re-exports plus the shared Message schema.
Import directly from domain packages in new code:
  from app.users.models import User
  from app.users.schemas import UserCreate, UserPublic
  from app.items.models import Item
  from app.items.schemas import ItemCreate, ItemPublic
  from app.auth.schemas import Token, TokenPayload, NewPassword
"""
from sqlmodel import SQLModel

from app.auth.schemas import NewPassword, Token, TokenPayload
from app.items.models import Item, ItemBase
from app.items.schemas import ItemCreate, ItemPublic, ItemsPublic, ItemUpdate
from app.users.models import User, UserBase
from app.users.schemas import (
    UpdatePassword,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)


class Message(SQLModel):
    message: str


__all__ = [
    # auth
    "Token",
    "TokenPayload",
    "NewPassword",
    # users
    "User",
    "UserBase",
    "UserCreate",
    "UserRegister",
    "UserUpdate",
    "UserUpdateMe",
    "UpdatePassword",
    "UserPublic",
    "UsersPublic",
    # items
    "Item",
    "ItemBase",
    "ItemCreate",
    "ItemUpdate",
    "ItemPublic",
    "ItemsPublic",
    # shared
    "Message",
]
