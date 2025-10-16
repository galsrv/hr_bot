from fastapi import HTTPException, status
from nicegui import app as nicegui_app
from nicegui import ui


@ui.page('/raise_404_error')
def raise_404_error() -> None:
    """Кастмная страница ошибки 404."""
    raise HTTPException(status_code=404)


# Практически бесполезно - срабатывает только при ошибке в коде вью-функции
@nicegui_app.on_page_exception
def custom_error_page(exception: HTTPException) -> None:
    """Кастомная страница ошибок."""
    if not isinstance(exception, HTTPException):
        raise exception
    if exception.status_code == status.HTTP_404_NOT_FOUND:
        ui.label('Страница не найдена').props('header').classes('text-bold text-h2')
    elif exception.status_code == status.HTTP_403_FORBIDDEN:
        ui.label('Доступ запрещен').props('header').classes('text-bold text-h2')
    else:
        ui.label('Возникла ошибка').props('header').classes('text-bold text-h2')
