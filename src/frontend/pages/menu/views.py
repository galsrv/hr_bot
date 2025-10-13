import asyncio
from datetime import datetime
from functools import partial
from typing import Callable

from config import settings as s
from fastapi import Depends
from nicegui import APIRouter, ui
from pages.dependencies import get_current_user, get_edit_menu_permission
from pages.layout import navbar
from pages.menu.constants import (
    MENU_ANSWER_MAX_LENGTH,
    MENU_BUTTON_TEXT_MAX_LENGTH,
    MENU_PAGE_SIZE,
)
from pages.menu.schemas import (
    MenuItemCreateSchema,
    MenuItemUpdateSchema,
    MenuItemsPageSchema,
)
from pages.menu.service import menu_api_client
from pages.urls import LOGIN_PAGE_URL, MENU_PAGE_URL
from pages.users.schemas import UserReadSchema
from pydantic import ValidationError

menu_router = APIRouter(prefix=MENU_PAGE_URL)


async def _create_menu_item_form_builder(
    new_menu_item_data: dict,
) -> None:
    """Выводим форму создания нового элемента справочника."""
    # Поля формы связываем с атрибутами объекта
    with ui.grid(columns=2):
        ui.label('Имя кнопки').classes('text-subtitle2')
        ui.input(
            placeholder='Введите текст кнопки меню бота',
            validation={
                'Недопустимая длина значения': lambda value: 0
                < len(value)
                < MENU_BUTTON_TEXT_MAX_LENGTH
            },
        ).classes('w-full').bind_value_to(new_menu_item_data, 'button_text')

        ui.label('Ответ').classes('text-subtitle2')
        ui.input(
            placeholder='Введите текст ответа',
            validation={
                'Недопустимая длина значения': lambda value: 0
                < len(value)
                < MENU_ANSWER_MAX_LENGTH
            },
        ).classes('w-full').bind_value_to(new_menu_item_data, 'answer')


async def _update_menu_item_form_builder(
    menu_item_data: dict,
) -> None:
    """Выводим форму изменения элемента справочника."""
    # Поля формы связываем с атрибутами объекта
    with ui.grid(columns=2):
        ui.label('Имя кнопки').classes('text-subtitle2')
        ui.label(menu_item_data['button_text']).classes('text-subtitle2')

        ui.label('Ответ').classes('text-subtitle2')
        ui.input(
            placeholder='Введите текст ответа',
            value=menu_item_data['answer'],
            validation={
                'Недопустимая длина значения': lambda value: 0
                < len(value)
                < MENU_ANSWER_MAX_LENGTH
            },
        ).classes('w-full').bind_value_to(menu_item_data, 'answer')

    # Преобразуем данные для вывода пользователя и времени создания/редактирования записи
    menu_item_data['created_at'], menu_item_data['updated_at'] = [
        datetime.strptime(el, '%Y-%m-%dT%H:%M:%S.%f').strftime(s.DATETIME_FORMAT)
        for el in (menu_item_data['created_at'], menu_item_data['updated_at'])
    ]
    created_by = (
        menu_item_data['created_by']['username']
        if menu_item_data['created_by']
        else '<неизвестно>'
    )
    updated_by = (
        menu_item_data['updated_by']['username']
        if menu_item_data['updated_by']
        else '<неизвестно>'
    )
    ui.label(
        f'Запись создана {menu_item_data["created_at"]} пользователем {created_by}, изменена {menu_item_data["updated_at"]} пользователем {updated_by}'
    ).classes('text-subtitle2')


async def _save_menu_item_button_handler(
    menu_item_data: dict,
    action: str = 'create',
) -> None:
    """Сохраняем элемент справочника меню."""
    try:
        if action == 'create':
            new_menu_item = MenuItemCreateSchema.model_validate(menu_item_data)
            result = await menu_api_client.create_menu_item(new_menu_item.model_dump())
        if action == 'update':
            menu_item_id = menu_item_data['id']
            new_menu_item = MenuItemUpdateSchema.model_validate(menu_item_data)
            result = await menu_api_client.update_menu_item(
                menu_item_id, new_menu_item.model_dump()
            )
    except ValidationError:
        ui.notify('Проверьте значения полей!', type='negative')
        return

    if result['OK']:
        ui.notify(result['message'], type='positive')
        await asyncio.sleep(1)
        ui.navigate.to(MENU_PAGE_URL)
    else:
        ui.notify(result['message'], type='negative')


async def _delete_menu_item_button_handler(
    menu_item_id: int,
) -> None:
    """Удаляем элемент справочника меню."""
    await menu_api_client.delete_menu_item(menu_item_id)

    ui.notify('Запись удалена', type='positive')
    await asyncio.sleep(1)
    ui.navigate.to(MENU_PAGE_URL)


async def _download_upload_menu_button_handler(func: Callable, *args) -> None:
    """Обрабатываем нажатие кнопок Выгрузить / Загрузить."""
    # Для кнопки Загрузить есть доп аргумент
    result = await func(*args)

    if result['OK']:
        ui.notify(result['message'], type='positive')
        await asyncio.sleep(1)
        ui.navigate.to(MENU_PAGE_URL)
    else:
        ui.notify(result['message'], type='negative')


@menu_router.page('/', title='Справочник элементов меню')
async def menu_page(
    page: int = 1,
    current_user: UserReadSchema = Depends(get_current_user),
    permission: bool = Depends(get_edit_menu_permission),
) -> None:
    """Страница со списком пользователей."""
    # Создание ui-элементов нельзя вынести в зависимость
    if not current_user:
        ui.navigate.to(LOGIN_PAGE_URL)

    navbar(current_user)

    # Получаем список элементов справочника с пагинацией
    menu_page: MenuItemsPageSchema | None = await menu_api_client.get_menu_page(
        page, size=MENU_PAGE_SIZE
    )

    # Выводим заголовок
    ui.item_label('Справочник меню').props('header').classes('text-bold text-h4')
    ui.item_label(f'Всего записей: {menu_page.total}').props('header').classes(
        'text-h6'
    )

    # Выводим кнопку Создать / Выгрузить / Загрузить
    if permission:
        with ui.card().classes('w-full'):
            with ui.row():
                ui.button(
                    'СОЗДАТЬ', on_click=lambda: ui.navigate.to('create')
                ).visible = permission
                ui.button(
                    'ВЫГРУЗИТЬ В ФАЙЛ',
                    on_click=lambda x=menu_api_client.download_menu: _download_upload_menu_button_handler(
                        x
                    ),
                )
                ui.button(
                    'ЗАГРУЗИТЬ ИЗ ФАЙЛА',
                    on_click=lambda x=menu_api_client.upload_menu: _download_upload_menu_button_handler(
                        x, {'created_by_id': current_user.id}
                    ),
                )

    # Выводим список элементов меню
    for menu_item in menu_page.items:
        with ui.card().classes('w-full'):
            with ui.grid(columns=2):
                ui.label('id').classes('text-subtitle2')
                ui.label(menu_item.id).classes('text-subtitle2')
                ui.label('Кнопка').classes('text-subtitle2')
                ui.label(menu_item.button_text).classes('text-subtitle2')
                ui.label('Ответ').classes('text-subtitle2')
                ui.label(menu_item.answer).classes('text-subtitle2')
                ui.button(
                    'ИЗМЕНИТЬ',
                    on_click=lambda m_id=menu_item.id: ui.navigate.to(f'{m_id}'),
                ).visible = permission
                ui.button(
                    'УДАЛИТЬ',
                    on_click=partial(
                        lambda m_id=menu_item.id: _delete_menu_item_button_handler(m_id)
                    ),
                ).visible = permission

    # Выводим кнопки пагинации
    if menu_page.pages > 1:
        chosen_page = ui.pagination(
            1,
            menu_page.pages,
            value=menu_page.page,
            direction_links=True,
            on_change=partial(lambda: ui.navigate.to(f'?page={chosen_page.value}')),
        )


@menu_router.page('/create', title='Создание элемента справочника')
async def menu_item_create_page(
    current_user: UserReadSchema = Depends(get_current_user),
    permission: bool = Depends(get_edit_menu_permission),
) -> None:
    """Страница создания элемента справочника меню."""
    if not current_user:
        ui.navigate.to(LOGIN_PAGE_URL)

    if not permission:
        ui.navigate.to(MENU_PAGE_URL)

    navbar(current_user)

    # Инициализируем стартовые значения нового элемента справочника
    new_menu_item_data = {
        'button_text': None,
        'answer': None,
        'created_by_id': current_user.id,
        'updated_by_id': current_user.id,
    }

    # Выводим заголовок
    ui.item_label('Новый элемент справочника').props('header').classes(
        'text-bold text-h4'
    )

    with ui.card().classes('w-full'):
        # Выводим поля формы и связывает переменные
        await _create_menu_item_form_builder(new_menu_item_data)
        # Выводим кнопки Сохранить и Назад
        with ui.row():
            ui.button(
                'СОХРАНИТЬ',
                on_click=partial(
                    lambda: _save_menu_item_button_handler(
                        new_menu_item_data, action='create'
                    )
                ),
            )
            ui.button('НАЗАД', on_click=ui.navigate.back)


@menu_router.page('/{id}', title='Изменение элемента справочника')
async def menu_item_update_page(
    menu_item_id: int,
    current_user: UserReadSchema = Depends(get_current_user),
    permission: bool = Depends(get_edit_menu_permission),
) -> None:
    """Страница изменения элемента справочника меню."""
    if not current_user:
        ui.navigate.to(LOGIN_PAGE_URL)

    if not permission:
        ui.navigate.to(MENU_PAGE_URL)

    navbar(current_user)

    # Получаем данные элемента справочника
    menu_item_data: dict | None = await menu_api_client.get_menu_item(menu_item_id)

    if menu_item_data is None:
        ui.notify('Указанная запись не существует', type='negative')
        ui.button('НАЗАД', on_click=ui.navigate.back)
    else:
        menu_item_data['updated_by_id'] = current_user.id

        # Выводим заголовок
        ui.item_label('Изменение элемента справочника').props('header').classes(
            'text-bold text-h4'
        )

        with ui.card().classes('w-full'):
            # Выводим поля формы и связывает переменные
            await _update_menu_item_form_builder(menu_item_data)
            # Выводим кнопки Сохранить и Назад
            with ui.row():
                ui.button(
                    'СОХРАНИТЬ',
                    on_click=partial(
                        lambda: _save_menu_item_button_handler(
                            menu_item_data, action='update'
                        )
                    ),
                )
                ui.button('НАЗАД', on_click=ui.navigate.back)
