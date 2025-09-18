import asyncio
from functools import partial

from fastapi import Request
from nicegui import APIRouter, ui

from pages.layout import navbar
from pages.auth.service import auth_api_client
from pages.settings.constants import (
    SETTING_VALUE_MAX_LEN,
    SETTING_INT_MAX_VALUE,
)
from pages.settings.service import settings_api_client
from pages.urls import SETTINGS_PAGE_URL, LOGIN_PAGE_URL
from pages.users.schemas import UserReadSchema

settings_router = APIRouter(prefix=SETTINGS_PAGE_URL)

def _validate_setting_value(value: str, int_type: bool) -> str | None:
    '''Валидируем значение настройки'''

    if not int_type:
        if value is None or not (1 < len(value) < SETTING_VALUE_MAX_LEN): 
            return f'Введите значение длиной от 1 до {SETTING_VALUE_MAX_LEN} символов'
    else:
        error_msg = f'Введите целое число от 1 до {SETTING_INT_MAX_VALUE}'
        try:
            return None if 0 < int(value) < SETTING_INT_MAX_VALUE else error_msg
        except ValueError:
            return error_msg

def _setting_details(setting_data: dict) -> list:
    '''Вывод полей формы изменения настройки'''
    ui.label(setting_data['name']).classes('text-h6')
    ui.label(setting_data['description']).classes('text-subtitle2')

    value_input = ui.input(
        label='Значение настройки',
        value=setting_data['value'],
        placeholder='Введите значение настройки',
        validation=lambda value: _validate_setting_value(value, setting_data['int_type'])
        ).classes('w-full').bind_value_to(setting_data, 'value')

    fields_to_validate = [value_input, ]
    # Возвращаем объекты полей, которые необходимо проверить перед сохранением записи
    return fields_to_validate

async def _save_setting_button_handler(
    setting_data: dict,
    fields_to_validate: list
) -> None:
    # Валидируем поля ввода, избегаем отправки заведомо некорректных данных на бэкенд. 
    # Валидация дублируется на бэке и фронте
    if any([not f.validate() for f in fields_to_validate]):
        ui.notify('Проверьте значения полей!', type='negative')
        return 

    result = await settings_api_client.update_setting(setting_data['id'], setting_data)

    if result['OK']:
        ui.notify(result['message'], type='positive')
        await asyncio.sleep(1)
        ui.navigate.to(SETTINGS_PAGE_URL)
    else:
        ui.notify(result['message'], type='negative')

@settings_router.page('/', title='Настройки проекта')
async def settings_page(request: Request):
    '''Получаем настройки от бэкенда.'''
    user = None
    session_id = request.cookies.get('session_id')
    user: UserReadSchema | None = await auth_api_client.get_user_by_session(session_id) if session_id else None

    if not user:
        ui.navigate.to(LOGIN_PAGE_URL)

    navbar(user)

    permission = user.role.can_edit_settings if user else False

    settings_list = await settings_api_client.get_settings()
    ui.item_label('Настройки').props('header').classes('text-bold text-h4')
    if settings_list:
        for setting in settings_list:
            with ui.card().classes('w-full'):
                ui.label(setting['name']).classes('text-h6')
                ui.label(setting['description']).classes('text-subtitle2')
                ui.label(setting['value']).classes('')
                if permission:
                    ui.button('ИЗМЕНИТЬ',
                            on_click=lambda s_id=setting["id"]: ui.navigate.to(f'{s_id}'))

@settings_router.page('/{id}', title='Изменение настройки')
async def setting_page(id: int, request: Request):
    '''Получаем настройку от бэкенда.'''
    user = None
    session_id = request.cookies.get('session_id')
    user: UserReadSchema | None = await auth_api_client.get_user_by_session(session_id) if session_id else None

    if not user:
        ui.navigate.to(LOGIN_PAGE_URL)

    navbar(user)

    permission = user.role.can_edit_settings if user else False

    if not permission:
        ui.navigate.to(SETTINGS_PAGE_URL)

    setting_data: dict | None = await settings_api_client.get_one_setting(id)

    if setting_data is None:
        ui.notify('Запрошенная настройка не найдена', type='negative')
        ui.button('НАЗАД', on_click=ui.navigate.back)
    else:
        ui.item_label('Изменение настройки').props('header').classes('text-bold text-h4')
        with ui.card().classes('w-full'):
            # Выводим поля пользователя
            fields_to_validate = _setting_details(setting_data)
            with ui.row():
                ui.button(
                    'СОХРАНИТЬ',
                    on_click=partial(lambda: _save_setting_button_handler(setting_data, fields_to_validate)))
                ui.button('НАЗАД', on_click=ui.navigate.back)
