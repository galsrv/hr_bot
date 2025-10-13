import asyncio
from functools import partial
from typing import Callable

from fastapi import Depends
from nicegui import APIRouter, ui
from pages.dependencies import get_current_user, get_edit_settings_permission
from pages.layout import navbar
from pages.settings.constants import (
    SETTING_INT_MAX_VALUE,
    SETTING_VALUE_MAX_LEN,
)
from pages.settings.service import settings_api_client
from pages.urls import LOGIN_PAGE_URL, SETTINGS_PAGE_URL
from pages.users.schemas import UserReadSchema

settings_router = APIRouter(prefix=SETTINGS_PAGE_URL)


def _validate_setting_value(value: str, int_type: bool) -> str | None:
    """Валидируем значение настройки."""
    if not int_type:
        if value is None or not (1 < len(value) < SETTING_VALUE_MAX_LEN):
            return f'Введите значение длиной от 1 до {SETTING_VALUE_MAX_LEN} символов'
    else:
        error_msg = f'Введите целое число от 1 до {SETTING_INT_MAX_VALUE}'
        try:
            return None if 0 < int(value) < SETTING_INT_MAX_VALUE else error_msg
        except ValueError:
            return error_msg
    return None


def _setting_details(setting_data: dict) -> list:
    """Вывод полей формы изменения настройки."""
    ui.label(setting_data['name']).classes('text-h6')
    ui.label(setting_data['description']).classes('text-subtitle2')

    value_input = (
        ui.input(
            label='Значение настройки',
            value=setting_data['value'],
            placeholder='Введите значение настройки',
            validation=lambda value: _validate_setting_value(
                value, setting_data['int_type']
            ),
        )
        .classes('w-full')
        .bind_value_to(setting_data, 'value')
    )
    # Возвращаем объекты полей, которые необходимо проверить перед сохранением записи
    return [value_input]


async def _save_setting_button_handler(
    setting_data: dict, fields_to_validate: list
) -> None:
    # Валидируем поля ввода, избегаем отправки заведомо некорректных данных на бэкенд.
    # Валидация дублируется на бэке и фронте
    if any([not f.validate() for f in fields_to_validate]):
        ui.notify('Проверьте значения полей!', type='negative')
        return

    result = await settings_api_client.update_setting(setting_data)

    if result['OK']:
        ui.notify(result['message'], type='positive')
        await asyncio.sleep(1)
        ui.navigate.to(SETTINGS_PAGE_URL)
    else:
        ui.notify(result['message'], type='negative')


async def _download_upload_settings_button_handler(func: Callable) -> None:
    result = await func()

    if result['OK']:
        ui.notify(result['message'], type='positive')
        await asyncio.sleep(1)
        ui.navigate.to(SETTINGS_PAGE_URL)
    else:
        ui.notify(result['message'], type='negative')


@settings_router.page('/', title='Настройки проекта')
async def settings_list_page(
    current_user: UserReadSchema = Depends(get_current_user),
    permission: bool = Depends(get_edit_settings_permission),
) -> None:
    """Выводим список настроек проекта."""
    # Создание ui-элементов нельзя вынести в зависимость
    if not current_user:
        ui.navigate.to(LOGIN_PAGE_URL)

    navbar(current_user)

    settings_list = await settings_api_client.get_settings()
    ui.item_label('Настройки').props('header').classes('text-bold text-h4')

    if permission:
        with ui.card().classes('w-full'):
            with ui.row():
                ui.button(
                    'ВЫГРУЗИТЬ В ФАЙЛ',
                    on_click=lambda x=settings_api_client.download_settings: _download_upload_settings_button_handler(
                        x
                    ),
                )
                ui.button(
                    'ЗАГРУЗИТЬ ИЗ ФАЙЛА',
                    on_click=lambda x=settings_api_client.upload_settings: _download_upload_settings_button_handler(
                        x
                    ),
                )

    if settings_list:
        for setting in settings_list:
            with ui.card().classes('w-full'):
                ui.label(setting['name']).classes('text-h6')
                ui.label(setting['description']).classes('text-subtitle2')
                ui.label(setting['value']).classes('')
                if permission:
                    ui.button(
                        'ИЗМЕНИТЬ',
                        on_click=lambda s_id=setting['id']: ui.navigate.to(f'{s_id}'),
                    )


@settings_router.page('/{id}', title='Изменение настройки')
async def setting_page(
    setting_id: int,
    current_user: UserReadSchema = Depends(get_current_user),
    permission: bool = Depends(get_edit_settings_permission),
) -> None:
    """Получаем настройку от бэкенда."""
    # Создание ui-элементов нельзя вынести в зависимость
    if not current_user:
        ui.navigate.to(LOGIN_PAGE_URL)

    if not permission:
        ui.navigate.to(SETTINGS_PAGE_URL)

    navbar(current_user)

    setting_data: dict | None = await settings_api_client.get_one_setting(setting_id)

    if setting_data is None:
        ui.notify('Запрошенная настройка не найдена', type='negative')
        ui.button('НАЗАД', on_click=ui.navigate.back)
    else:
        ui.item_label('Изменение настройки').props('header').classes(
            'text-bold text-h4'
        )
        with ui.card().classes('w-full'):
            # Выводим поля пользователя
            fields_to_validate = _setting_details(setting_data)
            with ui.row():
                ui.button(
                    'СОХРАНИТЬ',
                    on_click=partial(
                        lambda: _save_setting_button_handler(
                            setting_data, fields_to_validate
                        )
                    ),
                )
                ui.button('НАЗАД', on_click=ui.navigate.back)
