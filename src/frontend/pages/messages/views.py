import asyncio
from functools import partial

from fastapi import Depends
from nicegui import APIRouter, ui

from pages.dependencies import get_current_user, get_send_messages_permission
from pages.layout import navbar
from pages.messages.constants import (
    ERROR_MESSAGE_TOO_LONG,
    MESSAGE_TEXT_MAX_LENGTH,
)
from pages.messages.schemas import (
    EmployeeChatListSchema,
    EmployeeChatSchema,
)
from pages.messages.service import messages_api_client
import pages.styles as st
from pages.urls import LOGIN_PAGE_URL, MESSAGES_PAGE_URL
from pages.users.schemas import UserReadSchema

messages_router = APIRouter()


async def _ban_unban_employee_button_handler(
    employee_id: int, is_banned: bool, updated_by_id: int
) -> None:
    """Обрабатываем нажатие кнопки Отправить сообщение."""
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
    """Обрабатываем нажатие кнопки Отправить сообщение."""
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
) -> None:
    """Страница со списком чатов с сотрудниками."""
    # Создание ui-элементов нельзя вынести в зависимость
    if not current_user:
        ui.navigate.to(LOGIN_PAGE_URL)

    navbar(current_user)

    # Получаем список пользователей согласно фильтрам
    chats: list[EmployeeChatListSchema] = await messages_api_client.get_chats()

    # Выводим заголовок
    ui.item_label('Чаты').classes(st.PAGE_HEADER)

    # Выводим список чатов
    for chat in chats:
        with ui.card().classes('w-full'):
            with ui.row():
                ui.label(str(chat.id) + ' - ' + chat.name).classes(st.LABEL_BOLD + ' self-center')
                if chat.is_banned:
                    ui.chip('БАН', icon='block', color='red')
                with ui.button(
                    'ПЕРЕЙТИ',
                    on_click=lambda s_id=chat.id: ui.navigate.to(f'{s_id}/chat'),
                ).props(st.BUTTON_PROPS).classes(st.BUTTON):
                    if chat.unread_count:
                        ui.badge(chat.unread_count, color='red').props('floating')


@messages_router.page('/{chat_id}/chat', title='Чат с сотрудником')
async def chat_page(
    chat_id: int,
    current_user: UserReadSchema = Depends(get_current_user),
    permission: bool = Depends(get_send_messages_permission),
) -> None:
    """Страница чата с сотрудником."""
    if not current_user:
        ui.navigate.to(LOGIN_PAGE_URL)

    navbar(current_user)

    # Получаем част с сотрудником
    chat: EmployeeChatSchema = await messages_api_client.get_chat(chat_id)

    # Выводим заголовки страницы
    ui.item_label(f'Чат с сотрудником {chat.name}').classes(st.PAGE_HEADER)
    if chat.is_banned:
        ui.item_label('БАН').classes(st.LABEL_RED)
    # Выводим чат

    with ui.card().classes(st.THIRD_WIDTH):
        for message in chat.messages.items:
            with ui.row().classes('w-full mb-2'):
                with ui.row().classes(st.ALIGN_RIGTH if bool(message.manager) else st.ALIGN_LEFT):
                    message_element = ui.chat_message(
                        text=message.text,
                        name=chat.name if message.manager is None else message.manager.username,
                        sent=bool(message.manager),
                        stamp=message.created_at_str,
                    ).classes('inline-block max-w-[70%]')
                    # Выделяем непрочитанные сообщения
                    if not message.is_read:
                        message_element.classes(st.LABEL_BOLD)

    await messages_api_client.mark_chat_as_read(chat_id)

    with ui.row():
        # Выводим Поле для ввода ответа и кнопку Отправить
        if permission:
            new_message_input = ui.input(
                placeholder='Введите ответ',
                validation={
                    ERROR_MESSAGE_TOO_LONG: lambda value: 0
                    < len(value)
                    < MESSAGE_TEXT_MAX_LENGTH
                },
            ).props(st.INPUT_PROPS).classes(st.INPUT)
            ui.button(
                'ОТПРАВИТЬ',
                on_click=partial(
                    lambda: _send_message_button_handler(chat.id, new_message_input.value, current_user.id)),
            ).props(st.BUTTON_PROPS).classes(st.BUTTON)
            ban_button_title = 'РАЗБАНИТЬ СОТРУДНИКА' if chat.is_banned else 'ЗАБАНИТЬ СОТРУДНИКА'
            ui.button(
                ban_button_title,
                on_click=partial(
                    lambda: _ban_unban_employee_button_handler(chat.id, chat.is_banned, current_user.id)),
            ).props(st.BUTTON_PROPS).classes(st.BUTTON)
        ui.button('НАЗАД', on_click=ui.navigate.back).props(st.BUTTON_PROPS).classes(st.BUTTON)
