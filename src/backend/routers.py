from fastapi import APIRouter

from auth.views import auth_router
from bot_settings.views import botsettings_router
from menu.views import menu_router
from messages.views import messages_router
from users.views import users_router

main_router = APIRouter(prefix='/bot/api')

main_router.include_router(botsettings_router, prefix='/settings', tags=['settings'])
main_router.include_router(users_router, prefix='/users', tags=['users'])
main_router.include_router(auth_router, prefix='/auth/sessions', tags=['auth'])
main_router.include_router(messages_router, prefix='/messages', tags=['messages'])
main_router.include_router(menu_router, prefix='/menu', tags=['menu'])
