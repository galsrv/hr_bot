import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from auth.tasks import lifespan_tasks
from config import settings
from exceptions import validation_exception_handler
from routers import main_router

fastapi_app = FastAPI(
    title=settings.APP_TITLE,
    lifespan=lifespan_tasks,
    openapi_url=settings.OPENAPI_URL,
    docs_url=settings.DOCS_URL,
    redoc_url=settings.REDOC_URL
)

fastapi_app.include_router(main_router)

fastapi_app.add_exception_handler(RequestValidationError, validation_exception_handler)

if __name__ == '__main__':
    uvicorn.run(
        'main:fastapi_app',
        host=settings.HOST,
        port=settings.PORT,
        proxy_headers=True,
        reload=False if settings.PROD_ENVIRONMENT else True,
    )
