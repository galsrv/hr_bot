from nicegui import ui
import pages.styles as st
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
    with ui.header().classes(st.HAVBAR_HEADER):
        with ui.row().classes(st.HAVBAR_ROW):
            ui.link('Меню', MENU_PAGE_URL).classes(st.NAVBAR_ELEMENT)
            ui.link('Сообщения', MESSAGES_PAGE_URL).classes(st.NAVBAR_ELEMENT)
            ui.link('Настройки', SETTINGS_PAGE_URL).classes(st.NAVBAR_ELEMENT)
            ui.link('Пользователи', USERS_PAGE_URL).classes(st.NAVBAR_ELEMENT)
            if user:
                ui.label(user.username).classes(st.NAVBAR_ELEMENT)
                ui.link('Выйти', LOGOUT_PAGE_URL).classes(st.NAVBAR_ELEMENT)
            else:
                ui.link('Войти', LOGIN_PAGE_URL).classes(st.NAVBAR_ELEMENT)
