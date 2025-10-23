from functools import wraps
from typing import Callable
from urllib.parse import urlencode

from aiohttp import ClientConnectorError
from nicegui import ui


def client_connector_error_decorator(func: Callable) -> Callable:
    """Декоратор для обработки ошибки подключения к бэкенду."""
    @wraps(func)
    async def wrapper(*args, **kwargs) -> None:
        try:
            await func(*args, **kwargs)
        except ClientConnectorError:
            ui.navigate.back
            ui.notify('Ошибка выполнения запроса', type='negative')

    return wrapper


def build_url(base: str, **params) -> str:
    """Формируем урлы с параметрами."""
    params_cleaned = {k: v for k, v in params.items() if v is not None and v != ''}
    if not params_cleaned:
        return base
    return f'{base}?{urlencode(params_cleaned)}'


def url_shortener(url: str) -> str:
    """Укорачиваем строки для вывода в консоль."""
    return url if len(url) < 50 else url[:50] + '...' + url[-4:]
