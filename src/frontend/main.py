from config import settings
from nicegui import app as nicegui_app
from nicegui import ui
from routers import main_router

nicegui_app.include_router(main_router)

# nicegui_app.add_tailwind()
ui.colors(primary='indigo', secondary='gray', accent='blue')

ui.run(
    title=settings.APP_TITLE,
    host=settings.HOST,
    port=settings.PORT,
    reload=False if settings.PROD_ENVIRONMENT else True,
    favicon='static/favicon.ico',
    show=False,
    storage_secret=settings.SECRET_KEY,
)
