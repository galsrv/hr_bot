from functools import wraps

from nicegui import ui

from pages.urls import (
    MENU_PAGE_URL,
    SETTINGS_PAGE_URL,
    USERS_PAGE_URL
)

def navbar() -> None:
    '''Навигационная панель.'''
    with ui.header().classes('bg-black text-white shadow-md'):
        with ui.row().classes(
            'flex flex-col sm:flex-row justify-center items-center '
            'gap-4 sm:gap-10 p-1 w-full'
        ):
            ui.link('Меню', MENU_PAGE_URL).classes('!text-white no-underline hover:!text-gray-300 text-lg')
            ui.link('Сообщения', '/messages').classes('!text-white no-underline hover:!text-gray-300 text-lg')
            ui.link('Настройки', SETTINGS_PAGE_URL).classes('!text-white no-underline hover:!text-gray-300 text-lg')
            ui.link('Пользователи', USERS_PAGE_URL).classes('!text-white no-underline hover:!text-gray-300 text-lg')

def layout_decorator(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        navbar()
        await func(*args, **kwargs)
    return wrapper