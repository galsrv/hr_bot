from fastapi import FastAPI
import uvicorn

from config import settings
from routers import main_router

app = FastAPI(
    title=settings.APP_TITLE
)

app.include_router(main_router)

uvicorn.run(
    app,
    host=settings.HOST,
    port=settings.PORT,
    reload=False if settings.PROD_ENVIRONMENT else True,
)