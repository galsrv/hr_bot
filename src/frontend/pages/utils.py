from functools import wraps

from aiohttp import ClientConnectorError
from nicegui import ui

def client_connector_error_decorator(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            await func(*args, **kwargs)
        except ClientConnectorError:
            ui.navigate.back
            ui.notify('Ошибка выполнения запроса', type='negative')        
    return wrapper