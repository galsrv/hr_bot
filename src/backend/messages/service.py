from fastapi import HTTPException, status
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from loguru import logger
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from base_service import BaseService
from messages.constants import (
    ERROR_MESSAGE_USER_IS_BANNED,
    ERROR_MESSAGE_EMPLOYEE_EXISTS,
    ERROR_MESSAGE_EMPLOYEE_NOT_EXIST,
    ERROR_MESSAGE_NO_PERMISSION,
)
from messages.models import MessagesOrm, EmployeesOrm
from messages.schemas import (
    EmployeeCreareSchema,
    EmployeeChangeSchema,
    EmployeeChatSchema,
    MessageCreateSchema,
)
from users.models import UsersOrm
from users.service import user_service

class EmployeeService(BaseService):
    def __init__(self):
        super().__init__(EmployeesOrm)

    async def create_employee(
            self,
            session: AsyncSession,
            data_input: EmployeeCreareSchema
    ) -> EmployeesOrm:
        '''Создаем нового пользователя.'''
        try:
            new_employee: EmployeesOrm = await self.create(session, data_input)
        except IntegrityError:
            logger.log('DB_ACCESS', f'Entry create error: model={EmployeesOrm.__name__}, id={data_input.id}')
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=ERROR_MESSAGE_EMPLOYEE_EXISTS)
        return new_employee

    async def get_employee(
            self,
            session: AsyncSession,
            id: int,
    ) -> EmployeesOrm:
        '''Получаем запись пользователя.'''
        employee: EmployeesOrm | None = await self.get(session, id)

        if employee is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGE_EMPLOYEE_NOT_EXIST)

        return employee

    async def ban_unban_employee(
            self,
            session: AsyncSession,
            id: int,
            data_input: EmployeeChangeSchema,
    ) -> EmployeeChangeSchema:
        '''Блокируем/разблокируем сотрудника.'''

        # Проверяем существование и полномочия менеджера
        manager: UsersOrm | None = await user_service.get(session, data_input.updated_by_id)
        if not manager or not manager.is_active or not manager.role.can_send_messages:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ERROR_MESSAGE_NO_PERMISSION)

        # Проверяем существование сотрудника
        employee: EmployeesOrm | None = await self.get_employee(session, id)

        edited_employee = await self.update(session, employee, data_input)
        return edited_employee

employee_service = EmployeeService()


class MessagesService(BaseService):
    def __init__(self):
        super().__init__(MessagesOrm)

    async def create_message(
            self,
            session: AsyncSession,
            data_input: MessageCreateSchema
    ) -> MessagesOrm:
        '''Создаем новое сообщение.'''
        employee = await employee_service.get_employee(session, data_input.employee_id)

        # Если пользователь заблокирован 
        if employee.is_banned:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ERROR_MESSAGE_USER_IS_BANNED)

        if data_input.manager_id is not None:
            manager: UsersOrm | None = await user_service.get(session, data_input.manager_id)

            # Если указанный менеджер не существует или не имеет полномочий:
            if not manager or not manager.is_active or not manager.role.can_send_messages:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=ERROR_MESSAGE_NO_PERMISSION)

            data_input.is_read = True

        new_message: MessagesOrm = await self.create(session, data_input)
        return new_message

    async def mark_chat_as_read(
            self,
            session: AsyncSession,
            employee_id: int,
    ) -> None:
        '''Помечаем сообщения чата прочитанными.'''
        stmt = update(MessagesOrm).where(MessagesOrm.employee_id == employee_id).values(is_read=True)
        result = await session.execute(stmt)
        await session.commit()
        logger.log('DB_ACCESS', f'Entry change: model={self.model.__name__}, t_id={employee_id}, entries affected={result.rowcount}')

    async def get_employee_chat(
            self,
            session: AsyncSession,
            id: int,
            page_params: Params,
    ) -> EmployeeChatSchema:
        employee: EmployeesOrm | None = await employee_service.get_employee(session, id)

        query = select(MessagesOrm).where(MessagesOrm.employee_id == employee.id)
        messages: Page = await paginate(session, query, page_params)

        # Собираем структуру с вложенной пагинацией
        employee.messages = messages
        chat_schema = EmployeeChatSchema.model_validate(employee)

        return chat_schema

messages_service = MessagesService()