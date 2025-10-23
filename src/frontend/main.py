from nicegui import app as nicegui_app
from nicegui import ui

from config import settings
from routers import main_router

nicegui_app.include_router(main_router)

ui.run(
    title=settings.APP_TITLE,
    host=settings.HOST,
    port=settings.PORT,
    # root_path='/bot/admin', # пришлось вынести в настройки nginx
    reload=False if settings.PROD_ENVIRONMENT else True,
    favicon='static/favicon.ico',
    show=False,
    storage_secret=settings.SECRET_KEY,
)
