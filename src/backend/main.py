import uvicorn
from auth.tasks import lifespan_tasks
from config import settings
from exceptions import validation_exception_handler
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from routers import main_router

fastapi_app = FastAPI(title=settings.APP_TITLE, lifespan=lifespan_tasks)

fastapi_app.include_router(main_router)

fastapi_app.add_exception_handler(RequestValidationError, validation_exception_handler)

if __name__ == '__main__':
    uvicorn.run(
        'main:fastapi_app',
        host=settings.HOST,
        port=settings.PORT,
        reload=False if settings.PROD_ENVIRONMENT else True,
    )
