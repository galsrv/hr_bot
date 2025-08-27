from fastapi import FastAPI
from nicegui import ui
import uvicorn

from config import settings
from routers import main_router

app = FastAPI(
    title=settings.APP_TITLE
)

app.include_router(main_router)

ui.run_with(app, mount_path='/admin')

uvicorn.run(
    app,
    host=settings.HOST,
    port=settings.PORT,
    reload=False if settings.PROD_ENVIRONMENT else True,
)