import asyncio
from datetime import datetime
from functools import partial
from typing import Callable

from fastapi import Depends
from nicegui import APIRouter, ui
from pydantic import ValidationError

from config import settings as s
from pages.dependencies import get_current_user, get_edit_users_permission
from pages.layout import navbar
import pages.styles as st
from pages.urls import LOGIN_PAGE_URL, USERS_PAGE_URL
from pages.users.constants import (
    USER_NAME_MAX_LENGTH,
    USER_NAME_MIN_LENGTH,
    USER_PASSWORD_MAX_LENGTH,
    USER_PASSWORD_MIN_LENGTH,
)
from pages.users.schemas import (
    UserCreateSchema,
    UserReadSchema,
    UserUpdateSchema,
    UsersListPageSchema,
)
from pages.users.service import users_api_client
from pages.utils import build_url

users_router = APIRouter()


def _user_list_filters(
    roles: dict | None,
    role: int | None = None,
    is_active: bool | None = None,
    name: str | None = None,
    permission: bool = False,
) -> Callable:
    """Вспомогательная функция вывода фильтров в списке пользователей."""
    with ui.card().classes(st.FULL_WIDTH):
        with ui.row().classes(st.FULL_WIDTH + ' items-stretch gap-4'):
            role_select = ui.select(
                options={None: 'Все записи'} | roles,
                label='Роль: ',
                value=role,
                on_change=lambda: ui.navigate.to(
                    build_url(
                        USERS_PAGE_URL,
                        role=role_select.value,
                        is_active=is_active,
                        name=name)),
            ).props(st.INPUT_PROPS).classes(st.QUARTER_WIDTH)
            is_active_select = ui.select(
                options={None: 'Все записи', True: 'Активные', False: 'Неактивные'},
                label='Активность: ',
                value=is_active,
                on_change=lambda: ui.navigate.to(
                    build_url(
                        USERS_PAGE_URL,
                        role=role_select.value,
                        is_active=is_active_select.value,
                        name=name)),
            ).props(st.INPUT_PROPS).classes(st.QUARTER_WIDTH)
            username_input = ui.input(
                label='Поиск по имени: ',
                value=name if name else '',
                validation={
                    'Введите не более 10 символов': lambda value: value is None
                    or len(value) < 10},
            ).props('clearable').props(st.INPUT_PROPS).classes(st.QUARTER_WIDTH)
            username_input.on(
                type='keydown.enter',
                handler=lambda: ui.navigate.to(
                    build_url(
                        USERS_PAGE_URL,
                        role=role_select.value,
                        is_active=is_active_select.value,
                        name=username_input.value)))
            username_input.on(
                type='clear',
                handler=lambda: ui.navigate.to(
                    build_url(
                        USERS_PAGE_URL,
                        role=role_select.value,
                        is_active=is_active_select.value)))

            # Выводим кнопку Создать нового пользователя
            ui.button('Создать', on_click=lambda: ui.navigate.to('create')).props(st.BUTTON_PROPS).classes(st.BUTTON_CENTERED).visible = permission

    def navigate_to_filtered_list(current_page: int) -> None:
        ui.navigate.to(
            build_url(
                USERS_PAGE_URL,
                page=current_page,
                role=role_select.value,
                is_active=is_active_select.value,
                name=username_input.value,
            )
        )

    return navigate_to_filtered_list


def _validate_username(value: str | None) -> str | None:
    """Валидируем имя пользователя в ходе ввода в поле формы."""
    # Pydantic не предоставляет удобного способа валидировать отдельное поле модели
    # Испробован метод из https://github.com/pydantic/pydantic/discussions/7367
    try:
        UserCreateSchema(username=value)  # pyright: ignore[reportCallIssue]
    except ValidationError as e:
        for error in e.errors():
            if 'username' in error['loc']:
                return f'Введите значение из латинских символов длиной от {USER_NAME_MIN_LENGTH} до {USER_NAME_MAX_LENGTH} символов'


def _validate_password(value: str | None) -> str | None:
    """Валидируем пароль."""
    # А здесь пробуем второй способ, еще более костыльный
    try:
        UserCreateSchema.__pydantic_validator__.validate_assignment(
            UserCreateSchema.model_construct(), 'password', value
        )
    except ValidationError:
        return f'Введите значение не короче {USER_PASSWORD_MIN_LENGTH} и не длиннее {USER_PASSWORD_MAX_LENGTH}'


async def _edit_user_form_handler(
    user_data: dict,
) -> None:
    """Вывод полей формы создания/изменения пользователя."""
    # Получаем список ролей для вывода опции в поле выбора
    roles: dict | None = await users_api_client.get_roles()

    with ui.grid(columns=2):
        ui.label('id: ').classes(st.LABEL_BOLD)
        ui.label(user_data['id']).classes(st.LABEL)

        ui.label('Имя пользователя: ').classes(st.LABEL_BOLD)
        ui.label(user_data['username']).classes(st.LABEL)

        # Поля формы связываем с ключами словаря
        ui.label('Роль: ').classes(st.LABEL_BOLD)
        ui.select(options=roles, value=user_data['role']['id']).bind_value_to(user_data['role'], 'id').props(st.INPUT_PROPS)

        ui.label('Активен: ').classes(st.LABEL_BOLD)
        ui.checkbox(
            value=user_data['is_active'],
        ).bind_value_to(user_data, 'is_active').props(st.INPUT_PROPS)

        ui.label('Пароль: ').classes(st.LABEL_BOLD)
        ui.input(
            placeholder=f'Введите значение длиной не менее {USER_PASSWORD_MIN_LENGTH} знаков и не более {USER_PASSWORD_MAX_LENGTH} символов',
            password=True,
            password_toggle_button=True,
            validation=lambda value: _validate_password(value),
        ).props(st.INPUT_PROPS).classes(st.INPUT).bind_value_to(user_data, 'password')

    # Работаем с датой в виде строки, конвертирую по-простому. Модель Pydantic?
    user_data['created_at'], user_data['updated_at'] = [
        datetime.strptime(el, '%Y-%m-%dT%H:%M:%S.%f').strftime(s.DATETIME_FORMAT)
        for el in (user_data['created_at'], user_data['updated_at'])
    ]

    created_by = (
        user_data['created_by']['username']
        if user_data['created_by']
        else '<неизвестно>')
    updated_by = (
        user_data['updated_by']['username']
        if user_data['updated_by']
        else '<неизвестно>')

    ui.label(
        f'Запись создана: {user_data["created_at"]} пользователем {created_by}, изменена {user_data["updated_at"]} пользователем {updated_by}'
    ).classes(st.LABEL)


async def _create_user_form_handler(
    new_user_data: dict,
) -> None:
    """Выводим форму создания пользователя."""
    # Получаем список ролей для вывода опций в поле выбора
    roles: dict | None = await users_api_client.get_roles()

    # Поля формы связываем с ключами словаря
    with ui.grid(columns=2):
        ui.label('Имя пользователя: ').classes(st.LABEL_BOLD)
        ui.input(
            placeholder='Введите значение, состоящее из латинских букв',
            validation=lambda value: _validate_username(value),
        ).props(st.INPUT_PROPS).classes(st.INPUT).bind_value_to(new_user_data, 'username')

        ui.label('Роль: ').classes(st.LABEL_BOLD)
        ui.select(options=roles, value=list(roles.keys())[0]).bind_value_to(new_user_data, 'role_id').props(st.INPUT_PROPS)

        ui.label('Пароль: ').classes(st.LABEL_BOLD)
        ui.input(
            placeholder=f'Введите значение длиной не менее {USER_PASSWORD_MIN_LENGTH} знаков и не более {USER_PASSWORD_MAX_LENGTH} символов',
            password=True,
            password_toggle_button=True,
            validation=lambda value: _validate_password(value),
        ).props(st.INPUT_PROPS).classes(st.INPUT).bind_value_to(new_user_data, 'password')


async def _save_user_button_handler(
    user_data: dict,
    action: str = 'create',
) -> None:
    """Валидируем введенные данные и сохраняем пользователя."""
    result = dict()
    if action == 'create':
        try:
            new_user = UserCreateSchema(**user_data)
            result = await users_api_client.create_user(new_user.model_dump())
        except ValidationError:
            ui.notify('Проверьте значения полей!', type='negative')
            return

    if action == 'update':
        try:
            # Если при обновлении не заполнен пароль, игнорируем его
            if user_data['password'] is None or user_data['password'] == '':
                user_data.pop('password')
            edited_user = UserUpdateSchema(**user_data)
            result = await users_api_client.update_user(edited_user.model_dump())
        except ValidationError:
            ui.notify('Проверьте значения полей!', type='negative')
            return

    if result.get('OK', False):
        ui.notify(result['message'], type='positive')
        await asyncio.sleep(1)
        ui.navigate.to(USERS_PAGE_URL)
    else:
        ui.notify(result['message'], type='negative')


@users_router.page('/', title='Пользователи')
async def users_list_page(
    page: int = 1,
    role: int | None = None,
    is_active: bool | None = None,
    name: str | None = None,
    current_user: UserReadSchema = Depends(get_current_user),
    permission: bool = Depends(get_edit_users_permission),
) -> None:
    """Страница со списком пользователей."""
    # Создание ui-элементов нельзя вынести в зависимость
    if not current_user:
        ui.navigate.to(LOGIN_PAGE_URL)

    navbar(current_user)

    # Получаем список пользователей согласно фильтрам
    users_list: UsersListPageSchema | None = await users_api_client.get_users(
        page, role, is_active, name)

    # Получаем список ролей для опции фильтрации
    roles: dict | None = await users_api_client.get_roles()

    # Выводим заголовок
    ui.item_label('Пользователи').classes(st.PAGE_HEADER)
    ui.item_label(f'Всего записей: {users_list.total}').classes(st.PAGE_SUBHEADER)

    # Выводим фильтры записей в списке, получаем функцию для перехода по страницам
    navigate_func: Callable = _user_list_filters(roles, role, is_active, name, permission)

    # Выводим список пользователей
    for user in users_list.items:  # pyright: ignore[reportOptionalMemberAccess]
        with ui.card().classes('w-full'):
            with ui.row().classes(st.ROW):
                with ui.column():
                    ui.label('id').classes(st.LABEL_BOLD)
                    ui.label('Имя').classes(st.LABEL_BOLD)
                    ui.label('Роль').classes(st.LABEL_BOLD)
                    ui.label('Активен').classes(st.LABEL_BOLD)
                with ui.column():
                    ui.label(user.id).classes(st.LABEL)
                    ui.label(user.username).classes(st.LABEL)
                    ui.label(user.role.name).classes(st.LABEL)
                    ui.label(str(user.is_active)).classes(st.LABEL)
                    ui.button(
                        'ИЗМЕНИТЬ', on_click=lambda s_id=user.id: ui.navigate.to(f'{s_id}')
                    ).props(st.BUTTON_PROPS).classes(st.BUTTON).visible = permission

    # Выводим кнопки пагинации
    if users_list.pages > 1:
        current_page = ui.pagination(
            1,
            users_list.pages,
            value=users_list.page,
            direction_links=True,
            on_change=lambda: navigate_func(current_page.value),
        ).props(st.PAGINATION_PROPS).classes(st.PAGINATION)


@users_router.page('/create', title='Создание пользователя')
async def user_create_page(
    current_user: UserReadSchema = Depends(get_current_user),
    permission: bool = Depends(get_edit_users_permission),
) -> None:
    """Страница создания пользователя."""
    if not current_user:
        ui.navigate.to(LOGIN_PAGE_URL)

    if not permission:
        ui.navigate.to(USERS_PAGE_URL)

    navbar(current_user)

    # Инициализируем стартовые значения атрибутов пользователя
    new_user_data = {
        'username': None,
        'password': None,
        'role_id': None,
        'is_active': True,
        'created_by_id': current_user.id,
    }

    # Выводим заголовок
    ui.item_label('Новый пользователь').classes(st.PAGE_HEADER)

    with ui.card().classes('w-full'):
        # Выводим поля формы и связывает переменные
        await _create_user_form_handler(new_user_data)
        # Выводим кнопки Сохранить и Назад
        with ui.row():
            ui.button(
                'СОХРАНИТЬ',
                on_click=partial(lambda: _save_user_button_handler(new_user_data, action='create'))
            ).props(st.BUTTON_PROPS).classes(st.BUTTON)
            ui.button('НАЗАД', on_click=ui.navigate.back).props(st.BUTTON_PROPS).classes(st.BUTTON)


@users_router.page('/{user_id}', title='Изменение пользователя')
async def user_edit_page(
    user_id: int,
    current_user: UserReadSchema = Depends(get_current_user),
    permission: bool = Depends(get_edit_users_permission),
) -> None:
    """Страница изменения пользователя."""
    if not current_user:
        ui.navigate.to(LOGIN_PAGE_URL)

    if not permission:
        ui.navigate.to(USERS_PAGE_URL)

    navbar(current_user)

    # Получаем данные пользователя
    user_data: dict | None = await users_api_client.get_user(user_id)
    user_data['updated_by_id'] = current_user.id

    if user_data is None:
        ui.notify('Указанный пользователь не существует', type='negative')
        ui.button('НАЗАД', on_click=ui.navigate.back)
    else:
        # Выводим заголовки страницы
        ui.item_label('Изменение пользователя').classes(st.PAGE_HEADER)
        # Выводим поля формы пользователя
        with ui.card().classes('w-full'):
            await _edit_user_form_handler(user_data)
            with ui.row():
                # Выводим кнопки Сохранить и Назад
                ui.button(
                    'СОХРАНИТЬ',
                    on_click=partial(lambda: _save_user_button_handler(user_data, action='update'))
                ).props(st.BUTTON_PROPS).classes(st.BUTTON)
                ui.button('НАЗАД', on_click=ui.navigate.back).props(st.BUTTON_PROPS).classes(st.BUTTON)
