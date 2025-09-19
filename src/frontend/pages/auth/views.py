import asyncio

from fastapi import Request
from nicegui import APIRouter, ui

from log import logger
from pages.layout import navbar
from pages.auth.service import auth_api_client
from pages.urls import (
    SETTINGS_PAGE_URL,
    AUTH_PAGE_URL,
    LOGIN_PAGE_URL,
)

auth_router = APIRouter(prefix=AUTH_PAGE_URL)

def _user_login_form(login_data: dict) -> list:
    '''Вывод полей формы логина пользователя'''
    with ui.row():
        ui.input(
            label='Имя пользователя',
            placeholder='Введите имя пользователя',
            ).classes('w-full').bind_value_to(login_data, 'username')        
    with ui.row():
        ui.input(
            label='Пароль',
            placeholder='Введите пароль',
            password=True,
            password_toggle_button=True,
            ).classes('w-full').bind_value_to(login_data, 'password')     

async def _user_login_button_handler(
    login_data: dict,
) -> None:
    '''Аутентифицируем пользователя и получаем номер сессии'''
    if any([v is None or v == '' for v in login_data.values()]):
        ui.notify('Проверьте значения полей!', type='negative')
        return 

    result = await auth_api_client.user_login(login_data)

    if result['OK']:
        # Создаем куки в браузере. Альтернативные методы показались хуже
        ui.run_javascript(
            f'document.cookie = "session_id={result["id"]}; path=/; SameSite=Lax";')

        logger.log('AUTH', f'Login by {login_data['username']}')   
        ui.notify(result['message'], type='positive')
        await asyncio.sleep(1)
        ui.navigate.to(SETTINGS_PAGE_URL)
    else:
        ui.notify(result['message'], type='negative')

@auth_router.page('/login', title='Аутентификация')
async def user_login(request: Request):
    '''Страница создания пользователя.'''
    user = None
    session_id = request.cookies.get('session_id')
    if session_id:
        user = await auth_api_client.get_user_by_session(session_id)

    if user:
        ui.navigate.to(SETTINGS_PAGE_URL)

    navbar(user)
    # Инициализируем стартовые значения атрибутов пользователя
    login_data = {'username': None, 'password': None}

    # Выводим заголовок
    ui.item_label('Войдите в систему').props('header').classes('text-bold text-h4')
    
    with ui.card().classes('w-full'):
        # Выводим поля формы
        _user_login_form(login_data=login_data)
        ui.button('ВОЙТИ',
            on_click=lambda: _user_login_button_handler(login_data))

@auth_router.page('/logout', title='Выход')
async def user_logout(request: Request):
    '''Логаут пользователя.'''
    ui.run_javascript(
        'document.cookie = "session_id=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";')
    session_id = request.cookies.get('session_id')
    await auth_api_client.delete_session(session_id)
    logger.log('AUTH', f'Session {session_id} was removed')  
    ui.navigate.to(LOGIN_PAGE_URL)

@auth_router.page('/')
async def auth_page_redirect():
    '''Переадресуем на страницу логина.'''
    ui.navigate.to(LOGIN_PAGE_URL)