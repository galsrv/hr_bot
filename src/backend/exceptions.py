from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Убираем введенный пользователем пароль из выдачи ошибки."""
    errors: dict[dict] = exc.errors()

    for error in errors:
        if 'password' in error.get('loc', []):
            error.pop('input', None)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={'detail': errors},
    )
