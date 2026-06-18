from fastapi import APIRouter

from app.api.routes import private, utils
from app.auth.router import router as auth_router
from app.core.config import settings
from app.items.router import router as items_router
from app.users.router import router as users_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(utils.router)
api_router.include_router(items_router)

if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
