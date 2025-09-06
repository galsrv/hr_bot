from nicegui import APIRouter

from pages.menu.views import menu_router
from pages.root import root_router
from pages.settings.views import settings_router

main_router = APIRouter()

main_router.include_router(root_router)
main_router.include_router(menu_router)
main_router.include_router(settings_router)
