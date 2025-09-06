import asyncio
from functools import partial

from nicegui import APIRouter, ui

from pages.layout import layout_decorator
from pages.settings.service import api_client
from pages.urls import SETTINGS_PAGE_URL
from pages.utils import client_connector_error_decorator

settings_router = APIRouter(prefix=SETTINGS_PAGE_URL)

@settings_router.page('/', title='Настройки проекта')
@client_connector_error_decorator
@layout_decorator
async def settings_page():
    '''Получаем настройки от бэкенда.'''
    settings_list = await api_client.get_settings()
    ui.item_label('Настройки').props('header').classes('text-bold text-h2')
    if settings_list:
        for setting in settings_list:
            with ui.card().classes('w-full'):
                ui.label(setting['name']).classes('text-h6')
                ui.label(setting['description']).classes('text-subtitle2')
                ui.label(setting['value']).classes('')
                ui.button('ИЗМЕНИТЬ',
                        on_click=lambda s_id=setting["id"]: ui.navigate.to(f'{s_id}'))

@client_connector_error_decorator
async def save_setting_button_handler(id: int, new_value: str) -> None:
    result = await api_client.update_setting_value(id, new_value)

    if result['OK']:
        ui.notify(result['message'], type='positive')
        await asyncio.sleep(1)
        ui.navigate.to(SETTINGS_PAGE_URL)
    else:
        ui.notify(result['message'], type='negative')

@settings_router.page('/{id}', title='Изменение настройки')
@client_connector_error_decorator
@layout_decorator
async def setting_page(id: int):
    '''Получаем настройку от бэкенда.'''
    setting: dict | None = await api_client.get_one_setting(id)

    if setting is None:
        ui.notify('Запрошенная настройка не найдена', type='negative')
        ui.button('НАЗАД', on_click=ui.navigate.back)
    else:
        ui.item_label('Изменение настройки').props('header').classes('text-bold text-h2')
        with ui.card().classes('w-full'):
            ui.label(setting['name']).classes('text-h6')
            ui.label(setting['description']).classes('text-subtitle2')
            new_value = ui.input(
                value=setting['value'],
                placeholder='Введите значение настройки').classes('w-full')
            with ui.row():
                ui.button(
                    'СОХРАНИТЬ',
                    on_click=partial(lambda: save_setting_button_handler(setting['id'], new_value.value)))
                ui.button('НАЗАД', on_click=ui.navigate.back)
