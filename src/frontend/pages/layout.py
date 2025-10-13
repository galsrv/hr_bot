from nicegui import ui
from pages.urls import (
    LOGIN_PAGE_URL,
    LOGOUT_PAGE_URL,
    MENU_PAGE_URL,
    MESSAGES_PAGE_URL,
    SETTINGS_PAGE_URL,
    USERS_PAGE_URL,
)
from pages.users.schemas import UserReadSchema


def navbar(user: UserReadSchema | None = None) -> None:
    """Навигационная панель."""
    with ui.header().classes('bg-black text-white shadow-md'):
        with ui.row().classes(
            'flex flex-col sm:flex-row justify-center items-center '
            'gap-4 sm:gap-10 p-1 w-full'
        ):
            ui.link('Меню', MENU_PAGE_URL).classes(
                '!text-white no-underline hover:!text-gray-300 text-lg'
            )
            ui.link('Сообщения', MESSAGES_PAGE_URL).classes(
                '!text-white no-underline hover:!text-gray-300 text-lg'
            )
            ui.link('Настройки', SETTINGS_PAGE_URL).classes(
                '!text-white no-underline hover:!text-gray-300 text-lg'
            )
            ui.link('Пользователи', USERS_PAGE_URL).classes(
                '!text-white no-underline hover:!text-gray-300 text-lg'
            )
            if user:
                ui.label(user.username).classes(
                    '!text-white no-underline hover:!text-gray-300 text-lg'
                )
                ui.link('Выйти', LOGOUT_PAGE_URL).classes(
                    '!text-white no-underline hover:!text-gray-300 text-lg'
                )
            else:
                ui.link('Войти', LOGIN_PAGE_URL).classes(
                    '!text-white no-underline hover:!text-gray-300 text-lg'
                )
