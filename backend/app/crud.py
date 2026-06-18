"""
Backward-compatibility re-exports.
Import directly from domain service modules in new code:
  from app.users import service as users_service
  from app.items import service as items_service
"""
from app.items.service import create_item
from app.users.service import (
    authenticate,
    create_user,
    get_user_by_email,
    update_user,
    update_user_password,
)

__all__ = [
    "create_user",
    "update_user",
    "get_user_by_email",
    "authenticate",
    "update_user_password",
    "create_item",
]
