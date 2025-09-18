from nicegui import app as nicegui_app, ui

from config import settings
from routers import main_router

nicegui_app.include_router(main_router)

ui.run(
    title=settings.APP_TITLE,
    host=settings.HOST,
    port=settings.PORT,
    reload=False if settings.PROD_ENVIRONMENT else True,
    favicon='static/favicon.ico',
    show=False,
)
