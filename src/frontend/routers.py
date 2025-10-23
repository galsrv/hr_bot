from nicegui import APIRouter

from config import settings as s
from pages.auth.views import auth_router
from pages.menu.views import menu_router
from pages.messages.views import messages_router
from pages.root import root_router
from pages.settings.views import settings_router
from pages.users.views import users_router
from pages import urls as u

main_router = APIRouter(prefix=s.URL_PREFIX)

main_router.include_router(root_router)
main_router.include_router(menu_router, prefix=u.MENU_URL_PREFIX)
main_router.include_router(settings_router, prefix=u.SETTINGS_URL_PREFIX)
main_router.include_router(users_router, prefix=u.USERS_URL_PREFIX)
main_router.include_router(auth_router, prefix=u.AUTH_URL_PREFIX)
main_router.include_router(messages_router, prefix=u.MESSAGES_URL_PREFIX)
