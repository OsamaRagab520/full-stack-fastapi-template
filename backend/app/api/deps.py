"""
Backward-compatibility re-exports.
Import directly from app.auth.dependencies in new code.
"""
from app.auth.dependencies import (
    CurrentUser,
    SessionDep,
    TokenDep,
    get_current_active_superuser,
    get_current_user,
    get_db,
    reusable_oauth2,
)

__all__ = [
    "get_db",
    "SessionDep",
    "TokenDep",
    "get_current_user",
    "CurrentUser",
    "get_current_active_superuser",
    "reusable_oauth2",
]
