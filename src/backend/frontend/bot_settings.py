import asyncio
from functools import partial

from nicegui import ui

from frontend.layout import layout_decorator
from frontend.service import get_setting, get_settings, update_setting


@ui.page('/settings/{id}', title='Изменение настройки')
@layout_decorator
def setting_page(id: int):
    setting: dict | None = get_setting(id)
    if setting:
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
                    on_click=partial(lambda: update_setting(setting['id'], new_value.value)))
                ui.button('НАЗАД', on_click=lambda: ui.navigate.to(settings_page))

@ui.page('/settings', title='Настройки проекта')
@layout_decorator
def settings_page():
    settings_list = get_settings()
    ui.item_label('Настройки').props('header').classes('text-bold text-h2')
    if settings_list:
        for setting in settings_list:
            with ui.card().classes('w-full'):
                ui.label(setting['name']).classes('text-h6')
                ui.label(setting['description']).classes('text-subtitle2')
                ui.label(setting['value']).classes('')
                ui.button('ИЗМЕНИТЬ',
                        on_click=lambda s_id=setting["id"]: ui.navigate.to(settings_page, id=s_id)) # pyright: ignore[reportCallIssue]


