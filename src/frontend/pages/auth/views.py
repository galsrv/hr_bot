import asyncio

from fastapi import Depends, Request
from nicegui import APIRouter, ui

from log import logger
from pages.auth.service import auth_api_client
from pages.dependencies import get_current_user
from pages.layout import navbar
import pages.styles as st
from pages.urls import (
    LOGIN_PAGE_URL,
    SETTINGS_PAGE_URL,
)
from pages.users.schemas import UserLoginSchema, UserReadSchema
from pydantic import ValidationError

auth_router = APIRouter()


def _user_login_form(login_data: dict) -> None:
    """Вывод полей формы логина пользователя."""
    with ui.row():
        ui.input(
            label='Имя пользователя',
            placeholder='Введите имя пользователя',
        ).props(st.INPUT_PROPS).classes(st.INPUT).bind_value_to(login_data, 'username')
    with ui.row():
        ui.input(
            label='Пароль',
            placeholder='Введите пароль',
            password=True,
            password_toggle_button=True,
        ).props(st.INPUT_PROPS).classes(st.INPUT).bind_value_to(login_data, 'password')


async def _user_login_button_handler(
    login_data: dict,
) -> None:
    """Аутентифицируем пользователя и получаем номер сессии."""
    try:
        user_to_log_in = UserLoginSchema(**login_data)
        result = await auth_api_client.user_login(user_to_log_in.model_dump())
    except ValidationError:
        ui.notify('Все поля обязательны для ввода!', type='negative')
        return

    result = await auth_api_client.user_login(login_data)

    if result['OK']:
        # Создаем куки в браузере. Альтернативные методы показались хуже
        ui.run_javascript(f'document.cookie = "session_id={result["id"]}; path=/; SameSite=Lax";')

        logger.log('AUTH', f'Login by {login_data["username"]}')
        ui.notify(result['message'], type='positive')
        await asyncio.sleep(1)
        ui.navigate.to(SETTINGS_PAGE_URL)
    else:
        ui.notify(result['message'], type='negative')


@auth_router.page('/login', title='Аутентификация')
async def user_login(
    current_user: UserReadSchema | None = Depends(get_current_user),
) -> None:
    """Страница kjubyf."""
    if current_user:
        ui.navigate.to(SETTINGS_PAGE_URL)

    navbar(current_user)
    # Инициализируем стартовые значения атрибутов пользователя
    login_data = {'username': None, 'password': None}

    # Выводим заголовок
    ui.item_label('Войдите в систему').classes(st.PAGE_HEADER)

    with ui.card().classes('w-full'):
        # Выводим поля формы
        _user_login_form(login_data=login_data)
        ui.button('ВОЙТИ', on_click=lambda: _user_login_button_handler(login_data)).props(st.BUTTON_PROPS).classes(st.BUTTON)


@auth_router.page('/logout', title='Выход')
async def user_logout(request: Request) -> None:
    """Логаут пользователя."""
    ui.run_javascript(
        'document.cookie = "session_id=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";'
    )
    session_id = request.cookies.get('session_id')
    await auth_api_client.delete_session(session_id)
    logger.log('AUTH', f'Session {session_id} was removed')
    ui.navigate.to(LOGIN_PAGE_URL)


@auth_router.page('/')
async def auth_page_redirect() -> None:
    """Переадресуем на страницу логина."""
    ui.navigate.to(LOGIN_PAGE_URL)
