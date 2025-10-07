import asyncio
from functools import partial
from fastapi import Depends
from nicegui import APIRouter, ui

from pages.layout import navbar
from pages.dependencies import get_current_user, get_send_messages_permission
from pages.messages.constants import (
    MESSAGE_TEXT_MAX_LENGTH,
    ERROR_MESSAGE_TOO_LONG,
)
from pages.messages.schemas import (
    EmployeeChatListSchema,
    EmployeeChatSchema,
)
from pages.messages.service import messages_api_client
from pages.users.schemas import UserReadSchema
from pages.urls import MESSAGES_PAGE_URL, LOGIN_PAGE_URL

messages_router = APIRouter(prefix=MESSAGES_PAGE_URL)

async def _ban_unban_employee_button_handler(
    employee_id: int, is_banned: bool, updated_by_id: int
) -> None:
    '''Обрабатываем нажатие кнопки Отправить сообщение'''
    data_input = {'is_banned': not is_banned, 'updated_by_id': updated_by_id}
    result = await messages_api_client.ban_unban_employee(employee_id, data_input)

    if result['OK']:
        ui.notify(result['message'], type='positive')
        await asyncio.sleep(1)
        ui.navigate.to(MESSAGES_PAGE_URL)
    else:
        ui.notify(result['message'], type='negative')

async def _send_message_button_handler(
    employee_id: int, text: str, manager_id: int
) -> None:
    '''Обрабатываем нажатие кнопки Отправить сообщение'''
    data_input = {'employee_id': employee_id, 'text': text, 'manager_id': manager_id}
    result = await messages_api_client.send_message(data_input)

    if result['OK']:
        ui.notify(result['message'], type='positive')
        await asyncio.sleep(1)
        ui.navigate.to(MESSAGES_PAGE_URL)
    else:
        ui.notify(result['message'], type='negative')

@messages_router.page('/', title='Чаты')
async def chats_list_page(
    current_user: UserReadSchema = Depends(get_current_user),
):
    '''Страница со списком чатов с сотрудниками.'''
    # Создание ui-элементов нельзя вынести в зависимость
    if not current_user:
        ui.navigate.to(LOGIN_PAGE_URL)

    navbar(current_user)

    # Получаем список пользователей согласно фильтрам
    chats: list[EmployeeChatListSchema] = await messages_api_client.get_chats()
    
    # Выводим заголовок
    ui.item_label('Чаты').props('header').classes('text-bold text-h4')

    # Выводим список чатов
    for chat in chats:
        with ui.card().classes('w-full'):
            with ui.row():
                ui.label(chat.name).classes('text-subtitle2')
                ui.label(chat.unread_count).classes('text-subtitle2 text-white bg-red rounded-lg')
                ui.button('ПЕРЕЙТИ',
                    on_click=lambda s_id=chat.id: ui.navigate.to(f'{s_id}/chat'))

@messages_router.page('/{id}/chat', title='Час с сотрудником')
async def chat_page(
    id: int,
    current_user: UserReadSchema = Depends(get_current_user),
    permission: bool = Depends(get_send_messages_permission)
):
    '''Страница чата с сотрудником.'''
    if not current_user:
        ui.navigate.to(LOGIN_PAGE_URL)

    navbar(current_user)

    # Получаем част с сотрудником
    chat: EmployeeChatSchema = await messages_api_client.get_chat(id)

    # Выводим заголовки страницы
    ui.item_label(f'Чат с сотрудником {chat.name}').props('header').classes('text-bold text-h4')
    if chat.is_banned:
        ui.item_label('БАН').props('header').classes('text-bold text-h4 text-red')
    # Выводим чат
    with ui.card().classes('w-full'):
        for message in chat.messages.items:
            message_element = ui.chat_message(
                    text=message.text,
                    name=chat.name if message.manager is None else message.manager.username,
                    sent=bool(message.manager),
                    stamp=message.created_at_str,)
            # Выделяем непрочитанные сообщения
            if not message.is_read:
                message_element.classes('text-bold')

    await messages_api_client.mark_chat_as_read(id)

    with ui.row():
        # Выводим Поле для ввода ответа и кнопку Отправить
        if permission: 
            new_message_input = ui.input(
                placeholder='Введите ответ',
                validation={ERROR_MESSAGE_TOO_LONG: lambda value: 0 < len(value) < MESSAGE_TEXT_MAX_LENGTH}
                ).classes('w-full')     
            ui.button(
                'ОТПРАВИТЬ',
                on_click=partial(lambda: _send_message_button_handler(chat.id, new_message_input.value, current_user.id)))
            ban_button_title = 'РАЗБАНИТЬ СОТРУДНИКА' if chat.is_banned else 'ЗАБАНИТЬ СОТРУДНИКА'
            ui.button(
                ban_button_title,
                on_click=partial(lambda: _ban_unban_employee_button_handler(chat.id, chat.is_banned, current_user.id)))
        ui.button('НАЗАД', on_click=ui.navigate.back)


