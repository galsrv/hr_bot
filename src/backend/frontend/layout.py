from functools import wraps

from nicegui import ui

def navbar() -> None:
    '''Навигационная панель.'''
    with ui.header().classes('bg-black text-white shadow-md'):
        with ui.row().classes(
            'flex flex-col sm:flex-row justify-center items-center '
            'gap-4 sm:gap-10 p-1 w-full'
        ):
            ui.link('Меню', 'menu').classes('!text-white no-underline hover:!text-gray-300 text-lg')
            ui.link('Сообщения', 'messages').classes('!text-white no-underline hover:!text-gray-300 text-lg')
            ui.link('Настройки', 'settings').classes('!text-white no-underline hover:!text-gray-300 text-lg')
            ui.link('Пользователи', 'users').classes('!text-white no-underline hover:!text-gray-300 text-lg')

def layout_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        navbar()
        func(*args, **kwargs)
    return wrapper