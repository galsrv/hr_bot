import asyncio
from functools import partial
import re
from typing import Callable

from fastapi import Depends
from nicegui import APIRouter, ui

from pages.layout import navbar
from pages.users.constants import(
    USER_NAME_MAX_LENGTH,
    USER_NAME_MIN_LENGTH,
    USER_PASSWORD_MAX_LENGTH,
    USER_PASSWORD_MIN_LENGTH,
    USERNAME_REGEXP
)
from pages.dependencies import get_current_user, get_edit_users_permission
from pages.users.service import users_api_client
from pages.users.schemas import (
    UserReadSchema,
    UsersListPageSchema
)
from pages.urls import USERS_PAGE_URL, LOGIN_PAGE_URL
from pages.utils import build_url

users_router = APIRouter(prefix=USERS_PAGE_URL)


def _user_list_filters(roles: dict | None, role: int = None, is_active: bool = None, name: str = None) -> Callable:
    '''Вспомогательная функция вывода фильтров в списке пользователей'''

    with ui.row():
        role_select = ui.select(
            options={None: 'Все записи'} | roles,
            label='Роль: ',
            value=role,
            on_change=lambda: ui.navigate.to(
                build_url(USERS_PAGE_URL, role=role_select.value, is_active=is_active, name=name))
        )
        is_active_select = ui.select(
            options={None: 'Все записи', True: 'Активные', False: 'Неактивные'},
            label='Активность: ',
            value=is_active,
            on_change=lambda: ui.navigate.to(
                build_url(USERS_PAGE_URL, role=role_select.value, is_active=is_active_select.value, name=name))
        )
        username_input = ui.input(
            label='Имя: ',
            value=name if name else '',
            validation={'Введите не более 10 символов': lambda value: value is None or len(value) < 10}
        ).props('clearable')
        username_input.on(
            type='keydown.enter',
                handler=lambda: ui.navigate.to(
                build_url(USERS_PAGE_URL, role=role_select.value, is_active=is_active_select.value, name=username_input.value))
        )
        username_input.on(
            type='clear',
                handler=lambda: ui.navigate.to(
                build_url(USERS_PAGE_URL, role=role_select.value, is_active=is_active_select.value))
        )

    def navigate_to_filtered_list(current_page):
        ui.navigate.to(
            build_url(USERS_PAGE_URL, page=current_page, role=role_select.value, is_active=is_active_select.value, name=username_input.value))

    return navigate_to_filtered_list

def _validate_username(value: str | None) -> str | None:
    '''Валидируем имя пользователя'''
    if value and not (USER_NAME_MIN_LENGTH <= len(value) <= USER_NAME_MAX_LENGTH and re.match(USERNAME_REGEXP, value)):
        return f'Введите значение из латинских символов длиной от {USER_NAME_MIN_LENGTH} до {USER_NAME_MAX_LENGTH} символов'

def _validate_password(value: str | None) -> str | None:
    '''Валидируем пароль'''
    if value and not (USER_PASSWORD_MIN_LENGTH <= len(value) <= USER_PASSWORD_MAX_LENGTH):
        return f'Введите значение не короче {USER_PASSWORD_MIN_LENGTH} и не длиннее {USER_PASSWORD_MAX_LENGTH}'

def _user_details(user_data: dict, roles: list) -> list:
    '''Вывод полей формы создания/изменения пользователя'''
    fields_to_validate = list()
    # Поля формы связываем с ключами словаря
    if user_data.get('id') and user_data['id']:
        ui.label(f'id: {user_data['id']}').classes('text-subtitle2')
    if user_data['username']:
        ui.label(f'Имя: {user_data['username']}').classes('text-h6')
    else:
        username_input = ui.input(
            label='Имя пользователя',
            placeholder='Введите имя пользователя, состоящее из латинских букв',
            validation=lambda value: _validate_username(value),
            ).classes('w-full').bind_value_to(user_data, 'username')
        fields_to_validate.append(username_input)
    ui.select(
        options=roles,
        label='Роль',
        value=user_data['role']['id']).bind_value_to(user_data, 'role_id')
    is_active_checkbox = ui.checkbox(
        text='Активен',
        value=user_data['is_active'],
        ).bind_value_to(user_data, 'is_active')
    # Активность пользователя можно выбрать только при изменении
    is_active_checkbox.visible = bool(user_data.get('id', False))
    password_input = ui.input(
        label='Новый пароль',
        placeholder=f'Введите новый пароль длиной не менее {USER_PASSWORD_MIN_LENGTH} знаков и не более {USER_PASSWORD_MAX_LENGTH} символов',
        password=True,
        password_toggle_button=True,
        validation=lambda value: _validate_password(value)
        ).bind_value_to(user_data, 'password')
    fields_to_validate.append(password_input)
    # Возвращаем объекты полей, которые необходимо проверить перед сохранением записи
    return fields_to_validate

async def _save_user_button_handler(
    user_data: dict,
    fields_to_validate: list,
    action: str = 'create'
) -> None:
    # Валидируем поля ввода, избегаем отправки заведомо некорректных данных на бэкенд. 
    # Валидация дублируется на бэке и фронте
    if any([not f.validate() for f in fields_to_validate]):
        ui.notify('Проверьте значения полей!', type='negative')
        return 

    if action == 'create':
        result = await users_api_client.create_user(user_data)

    if action == 'update':
        # Если при обновлении не заполнен пароль, игнорируем его
        if user_data['password'] is None or user_data['password'] == '':
            user_data.pop('password')
        result = await users_api_client.update_user(user_data['id'], user_data)

    if result['OK']:
        ui.notify(result['message'], type='positive')
        await asyncio.sleep(1)
        ui.navigate.to(USERS_PAGE_URL)
    else:
        ui.notify(result['message'], type='negative')



@users_router.page('/', title='Пользователи')
async def users_list_page(
    page: int = 1,
    role: int = None,
    is_active: bool = None,
    name: str = None,
    current_user: UserReadSchema = Depends(get_current_user),
    permission: bool = Depends(get_edit_users_permission),
):
    '''Страница со списком пользователей.'''
    # Создание ui-элементов нельзя вынести в зависимость
    if not current_user:
        ui.navigate.to(LOGIN_PAGE_URL)

    navbar(current_user)

    # Получаем список пользователей согласно фильтрам
    users_list: UsersListPageSchema | None = await users_api_client.get_users(page, role, is_active, name)
    
    # Получаем список ролей для опции фильтрации
    roles: dict | None = await users_api_client.get_roles()

    # Выводим заголовок
    ui.item_label('Пользователи').props('header').classes('text-bold text-h4')
    ui.item_label(f'Всего записей: {users_list.total}').props('header').classes('text-h6')

    # Выводим фильтры записей в списке, получаем функцию для корретного перехода по страницам 
    navigate_func: Callable = _user_list_filters(roles, role, is_active, name)

    # Выводим кнопку Создать нового пользователя
    ui.button('Создать', on_click=lambda : ui.navigate.to('create')).visible = permission

    # Выводим список пользователей
    for user in users_list.items:
        with ui.card().classes('w-full'):
            with ui.grid(columns=2):
                ui.label('id').classes('text-subtitle2')
                ui.label(user.id).classes('text-subtitle2')
                ui.label('Имя').classes('text-subtitle2')
                ui.label(user.username).classes('text-subtitle2')
                ui.label('Роль').classes('text-subtitle2')
                ui.label(user.role.name).classes('text-subtitle2')
                ui.label('Активен').classes('text-subtitle2')
                ui.label(str(user.is_active)).classes('text-subtitle2')
                ui.button('ИЗМЕНИТЬ',
                        on_click=lambda s_id=user.id: ui.navigate.to(f'{s_id}')).visible = permission

    # Выводим кнопки пагинации
    if users_list.pages > 1:
        current_page = ui.pagination(1, users_list.pages,
            value=users_list.page,
            direction_links=True,
            on_change=lambda: navigate_func(current_page.value))

@users_router.page('/create', title='Создание пользователя')
async def user_create_page(
    current_user: UserReadSchema = Depends(get_current_user),
    permission: bool = Depends(get_edit_users_permission),
):
    if not current_user:
        ui.navigate.to(LOGIN_PAGE_URL)

    if not permission:
        ui.navigate.to(USERS_PAGE_URL)

    navbar(current_user)

    '''Страница создания пользователя.'''
    # Получаем список ролей для вывода опции в поле выбора
    roles: dict | None = await users_api_client.get_roles()
    # Инициализируем стартовые значения атрибутов пользователя
    user_data = {'username': None, 'role': {'id': list(roles.keys())[0]}, 'is_active': True}

    # Выводим заголовок
    ui.item_label('Новый пользователь').props('header').classes('text-bold text-h4')
    
    with ui.card().classes('w-full'):
        # Выводим поля формы
        fields_to_validate = _user_details(user_data=user_data, roles=roles)
        with ui.row():
            # Выводим кнопки Сохранить и Назад
            ui.button('СОХРАНИТЬ',
                on_click=partial(lambda: _save_user_button_handler(user_data, fields_to_validate, action='create')))
            ui.button('НАЗАД',
                on_click=ui.navigate.back)

@users_router.page('/{id}', title='Изменение пользователя')
async def user_edit_page(
    current_user: UserReadSchema = Depends(get_current_user),
    permission: bool = Depends(get_edit_users_permission)
):
    '''Страница изменения пользователя.'''
    if not current_user:
        ui.navigate.to(LOGIN_PAGE_URL)

    if not permission:
        ui.navigate.to(USERS_PAGE_URL)

    navbar(current_user)

    # Получаем данные пользователя и список ролей для вывода опции в поле выбора
    user_data: dict | None = await users_api_client.get_user(id)
    roles: dict | None = await users_api_client.get_roles()

    if user_data is None:
        ui.notify('Указанный пользователь не существует', type='negative')
        ui.button('НАЗАД', on_click=ui.navigate.back)
    else:
        # Выводим заголовки страницы
        ui.item_label('Изменение пользователя').props('header').classes('text-bold text-h4')
        with ui.card().classes('w-full'):
            # Выводим поля пользователя
            fields_to_validate = _user_details(user_data, roles)
            with ui.row():
                # Выводим кнопки Сохранить и Назад
                ui.button(
                    'СОХРАНИТЬ',
                    on_click=partial(lambda: _save_user_button_handler(user_data, fields_to_validate, action='update')))
                ui.button('НАЗАД', on_click=ui.navigate.back)
