import asyncio
from functools import partial
import re
from typing import Callable

from aiohttp import ClientConnectorError
from nicegui import APIRouter, ui

from pages.layout import layout_decorator
from pages.users.constants import(
    USER_NAME_MAX_LENGTH,
    USER_NAME_MIN_LENGTH,
    USER_PASSWORD_MAX_LENGTH,
    USER_PASSWORD_MIN_LENGTH,
    USERNAME_REGEXP
)
# from pages.users.layout import users_filters
from pages.users.service import users_api_client
from pages.urls import USERS_PAGE_URL
from pages.utils import build_url, client_connector_error_decorator

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
            validation={
                f'Введите значение из латинских символов длиной от {USER_NAME_MIN_LENGTH} до {USER_NAME_MAX_LENGTH} символов': lambda value: value is None or (USER_NAME_MIN_LENGTH <= len(value) <= USER_NAME_MAX_LENGTH and re.match(USERNAME_REGEXP, value))}
            ).classes('w-full').bind_value_to(user_data, 'username')
        fields_to_validate.append(username_input)
    ui.select(
        options=roles,
        label='Роль',
        value=user_data['role_id']).bind_value_to(user_data, 'role_id')
    is_active_checkbox = ui.checkbox(
        text='Активен',
        value=user_data['is_active'],
        ).bind_value_to(user_data, 'is_active')
    # Активность пользователя можно выбрать только при изменении
    is_active_checkbox.visible = bool(user_data.get('id', False))
    password_input = ui.input(
        label='Новый пароль',
        placeholder='Введите новый пароль длиной не менее 8 знаков и не более 50 символов',
        password=True,
        password_toggle_button=True,
        validation={
            f'Введите значение не короче {USER_PASSWORD_MIN_LENGTH} и не длиннее {USER_PASSWORD_MAX_LENGTH}': lambda value: value is None or USER_PASSWORD_MIN_LENGTH <= len(value) <= USER_PASSWORD_MAX_LENGTH}
    ).classes('w-full').bind_value_to(user_data, 'password')
    fields_to_validate.append(password_input)
    # Возвращаем объекты полей, которые необходимо проверить перед сохранением записи
    return fields_to_validate

@client_connector_error_decorator
async def _save_user_button_handler(
    user_data: dict,
    fields_to_validate: list,
    action: str = 'create'
) -> None:

    # Валидируем поля ввода 
    # Так избегаем отправки заведомо некорректных данных на бэкенд. 
    # Правда также дублируем валидацию на фронтенде
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
@client_connector_error_decorator
@layout_decorator
async def users_list_page(page: int = 1, role: int = None, is_active: bool = None, name: str = None):
    '''Страница со списком пользователей.'''
    # Получаем список пользователей согласно фильтрам
    response = await users_api_client.get_users(page, role, is_active, name)
    
    if response is None:
        raise ClientConnectorError

    users_list, total, page, pages  = response['items'], response['total'], response['page'], response['pages']

    # Получаем список ролей для опции фильтрации
    roles: dict | None = await users_api_client.get_roles()

    # Выводим заголовок
    ui.item_label('Пользователи').props('header').classes('text-bold text-h4')
    ui.item_label(f'Всего записей: {total}').props('header').classes('text-h6')

    # Выводим фильтры записей в списке, получаем функцию для корретного перехода по страницам 
    navigate_func: Callable = _user_list_filters(roles, role, is_active, name)

    # Выводим кнопку Создать нового пользователя
    ui.button('Создать', on_click=lambda : ui.navigate.to('create'))

    # Выводим список пользователей
    for user in users_list:
        with ui.card().classes('w-full'):
            ui.label(f'id: {user['id']}').classes('text-subtitle2')
            ui.label(f'Имя: {user['username']}').classes('text-h6')
            ui.label(f'Роль: {user['role_name']}').classes('text-subtitle2')
            ui.label(f'Активен: {user['is_active']}').classes('text-subtitle2')
            ui.button('ИЗМЕНИТЬ',
                    on_click=lambda s_id=user["id"]: ui.navigate.to(f'{s_id}'))

    # Выводим кнопки пагинации
    if pages > 1:
        current_page = ui.pagination(1, pages,
            value=page,
            direction_links=True,
            on_change=lambda: navigate_func(current_page.value))

@users_router.page('/create', title='Создание пользователя')
@client_connector_error_decorator
@layout_decorator
async def user_create_page():
    '''Страница создания пользователя.'''
    # Получаем список ролей для вывода опции в поле выбора
    roles: dict | None = await users_api_client.get_roles()
    # Инициализируем стартовые значения атрибутов пользователя
    user_data = {'username': None, 'role_id': list(roles.keys())[0], 'is_active': True}

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
@client_connector_error_decorator
@layout_decorator
async def user_edit_page(id: int):
    '''Страница изменения пользователя.'''
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
