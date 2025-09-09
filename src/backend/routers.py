from fastapi import APIRouter

from bot_settings.views import botsettings_router
from users.views import auth_router

main_router = APIRouter()

main_router.include_router(
    botsettings_router, prefix='/api/settings', tags=['settings'])

main_router.include_router(
    auth_router, prefix='/api/users', tags=['users'])



