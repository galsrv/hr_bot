from fastapi import APIRouter, BackgroundTasks, Depends, status
from fastapi_pagination import Params
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from messages.models import EmployeesOrm, MessagesOrm
from messages.schemas import (
    EmployeeChangeSchema,
    EmployeeChatListSchema,
    EmployeeChatSchema,
    EmployeeCreareSchema,
    EmployeeReadSchema,
    MessageCreateSchema,
    MessageReadSchema,
)
from messages.service import employee_service, messages_service
from messages.utils import send_telegram_message

messages_router = APIRouter()


@messages_router.post(
    '/employees/',
    response_model=EmployeeReadSchema,
    status_code=status.HTTP_201_CREATED,
    summary='Создать сотрудника',
)
async def create_or_get_employee(
    data_input: EmployeeCreareSchema, session: AsyncSession = Depends(get_async_session)
) -> EmployeeReadSchema:
    """Создаем нового сотрудника."""
    new_employee = await employee_service.get_or_create_employee(session, data_input)
    return new_employee


@messages_router.get(
    '/employees/{employee_id}',
    response_model=EmployeeReadSchema,
    summary='Получить данные сотрудника',
)
async def get_employee(
    employee_id: int, session: AsyncSession = Depends(get_async_session)
) -> EmployeeReadSchema:
    """Получаем запись сотрудника."""
    employee: EmployeesOrm | None = await employee_service.get_employee(session, employee_id)
    return employee


@messages_router.get(
    '/employees/',
    response_model=list[EmployeeChatListSchema],
    summary='Получить список сотрудников (чатов)',
)
async def get_employees(
    session: AsyncSession = Depends(get_async_session),
) -> list[EmployeeChatListSchema]:
    """Получаем чаты с сотрудниками."""
    employees = await employee_service.get_employees_chat_list(session)
    return employees


@messages_router.patch(
    '/employees/{employee_id}',
    response_model=EmployeeReadSchema,
    summary='Заблокировать/разблокировать сотрудника',
)
async def change_employee(
    employee_id: int,
    data_input: EmployeeChangeSchema,
    session: AsyncSession = Depends(get_async_session),
) -> EmployeeReadSchema:
    """Блокируем/разблокируем сотрудника."""
    edited_employee = await employee_service.ban_unban_employee(session, employee_id, data_input)
    return edited_employee


@messages_router.post(
    '/',
    response_model=MessageReadSchema,
    status_code=status.HTTP_201_CREATED,
    summary='Отправить сообщение или ответ',
)
async def create_message(
    new_message: MessageCreateSchema,
    backgorund_task: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
) -> MessageReadSchema:
    """Создаем новое сообщение пользователя или менеджера."""
    new_message: MessagesOrm = await messages_service.create_message(session, new_message)
    # Для отправки ответов менеджера создаем фоновую задачу
    if new_message.manager_id is not None:
        backgorund_task.add_task(send_telegram_message, new_message.employee_id, new_message.text)
    return new_message


@messages_router.get(
    '/employees/{employee_id}/chat',
    response_model=EmployeeChatSchema,
    summary='Получить чат с сотрудником',
)
async def get_employee_chat(
    employee_id: int,
    page_params: Params = Depends(),
    session: AsyncSession = Depends(get_async_session),
) -> EmployeeChatSchema:
    """Получаем чаты с сотрудником."""
    employee_chat = await messages_service.get_employee_chat(session, employee_id, page_params)
    return employee_chat


@messages_router.post(
    '/employees/{employee_id}/chat/mark_as_read',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Отметить чат прочитанным',
)
async def mark_employee_chat_as_read(
    employee_id: int, session: AsyncSession = Depends(get_async_session)
) -> None:
    """Помечаем чат прочитанным."""
    await messages_service.mark_chat_as_read(session, employee_id)
