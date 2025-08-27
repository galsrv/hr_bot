from fastapi import APIRouter

from bot_settings.views import botsettings_router

# Исправить инициализацию 
from frontend import bot_settings, menu

main_router = APIRouter()

main_router.include_router(
    botsettings_router, prefix='/api/settings', tags=['settings'])




