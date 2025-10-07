from nicegui import APIRouter

from pages.auth.views import auth_router
from pages.menu.views import menu_router
from pages.messages.views import messages_router
from pages.root import root_router
from pages.settings.views import settings_router
from pages.users.views import users_router

main_router = APIRouter()

main_router.include_router(root_router)
main_router.include_router(menu_router)
main_router.include_router(settings_router)
main_router.include_router(users_router)
main_router.include_router(auth_router)
main_router.include_router(messages_router)