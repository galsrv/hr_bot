from fastapi import FastAPI
import uvicorn

from config import settings
from routers import main_router

fastapi_app = FastAPI(title=settings.APP_TITLE)

fastapi_app.include_router(main_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:fastapi_app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False if settings.PROD_ENVIRONMENT else True,
    )
