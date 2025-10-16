from fastapi import HTTPException, status
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from loguru import logger
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from base_service import BaseService
from messages.constants import (
    ERROR_MESSAGE_EMPLOYEE_NOT_EXIST,
    ERROR_MESSAGE_NO_PERMISSION,
    ERROR_MESSAGE_USER_IS_BANNED,
)
from messages.models import EmployeesOrm, MessagesOrm
from messages.schemas import (
    EmployeeChangeSchema,
    EmployeeChatListSchema,
    EmployeeChatSchema,
    EmployeeCreareSchema,
    MessageCreateSchema,
)
from users.models import UsersOrm
from users.service import user_service


class EmployeeService(BaseService):
    """Класс сервисных функций модели."""
    def __init__(self) -> None:
        super().__init__(EmployeesOrm)

    async def get_or_create_employee(
        self, session: AsyncSession, data_input: EmployeeCreareSchema
    ) -> EmployeesOrm:
        """Получаем пользователя или создаем нового."""
        try:
            employee: EmployeesOrm = await self.get_employee(session, data_input.id)
        except HTTPException:
            employee: EmployeesOrm = await self.create(session, data_input)

        if employee.is_banned:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ERROR_MESSAGE_NO_PERMISSION,
            )

        return employee

    async def get_employee(
        self,
        session: AsyncSession,
        employee_id: int,
    ) -> EmployeesOrm:
        """Получаем запись пользователя."""
        employee: EmployeesOrm | None = await self.get(session, employee_id)

        if employee is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGE_EMPLOYEE_NOT_EXIST,
            )

        return employee

    async def get_employees_chat_list(
        self,
        session: AsyncSession,
    ) -> list[EmployeeChatListSchema]:
        """Получаем список чатов кастомным запросом."""
        # Подзапрос с количеством непрочитанных сообщений и датой последнего
        message_stats = (
            select(
                MessagesOrm.employee_id,
                func.count().filter(MessagesOrm.is_read == False).label('unread_count'),  # noqa: E712
                func.max(MessagesOrm.created_at).label('last_message_at'),
            )
            .group_by(MessagesOrm.employee_id)
            .subquery()
        )

        # Основной запрос с данными сотрудников и данными подзапроса
        stmt = (
            select(
                EmployeesOrm.id,
                EmployeesOrm.name,
                EmployeesOrm.is_banned,
                func.coalesce(message_stats.c.unread_count, 0).label('unread_count'),
                message_stats.c.last_message_at,
            )
            .outerjoin(message_stats, EmployeesOrm.id == message_stats.c.employee_id)
            .order_by(message_stats.c.last_message_at.desc().nullslast())
        )

        employees = await session.execute(stmt)
        employees = employees.all()
        employees = [EmployeeChatListSchema.model_validate(e) for e in employees]

        return employees

    async def ban_unban_employee(
        self,
        session: AsyncSession,
        employee_id: int,
        data_input: EmployeeChangeSchema,
    ) -> EmployeeChangeSchema:
        """Блокируем/разблокируем сотрудника."""
        # Проверяем существование и полномочия менеджера
        manager: UsersOrm | None = await user_service.get(
            session, data_input.updated_by_id
        )
        if not manager or not manager.is_active or not manager.role.can_send_messages:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ERROR_MESSAGE_NO_PERMISSION,
            )

        # Проверяем существование сотрудника
        employee: EmployeesOrm | None = await self.get_employee(session, employee_id)

        edited_employee = await self.update(session, employee, data_input)
        return edited_employee


employee_service = EmployeeService()


class MessagesService(BaseService):
    """Класс сервисных функций модели."""

    def __init__(self) -> None:
        super().__init__(MessagesOrm)

    async def create_message(
        self, session: AsyncSession, data_input: MessageCreateSchema
    ) -> MessagesOrm:
        """Создаем новое сообщение."""
        employee = await employee_service.get_employee(session, data_input.employee_id)

        # Если пользователь заблокирован
        if employee.is_banned:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ERROR_MESSAGE_USER_IS_BANNED,
            )

        if data_input.manager_id is not None:
            manager: UsersOrm | None = await user_service.get(
                session, data_input.manager_id
            )

            # Если указанный менеджер не существует или не имеет полномочий:
            if (
                not manager
                or not manager.is_active
                or not manager.role.can_send_messages
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=ERROR_MESSAGE_NO_PERMISSION,
                )

            data_input.is_read = True

        new_message: MessagesOrm = await self.create(session, data_input)

        return new_message

    async def mark_chat_as_read(
        self,
        session: AsyncSession,
        employee_id: int,
    ) -> None:
        """Помечаем сообщения чата прочитанными."""
        stmt = (
            update(MessagesOrm)
            .where(MessagesOrm.employee_id == employee_id)
            .values(is_read=True)
        )
        result = await session.execute(stmt)
        await session.commit()
        logger.log(
            'DB_ACCESS',
            f'Entry change: model={self.model.__name__}, t_id={employee_id}, entries affected={result.rowcount}',
        )

    async def get_employee_chat(
        self,
        session: AsyncSession,
        employee_id: int,
        page_params: Params,
    ) -> EmployeeChatSchema:
        """Получаем чат с сотрудником."""
        employee: EmployeesOrm | None = await employee_service.get_employee(session, employee_id)

        query = (
            select(MessagesOrm)
            .where(MessagesOrm.employee_id == employee.id)
            .order_by(MessagesOrm.created_at.asc())
        )
        messages: Page = await paginate(session, query, page_params)

        # Собираем структуру с вложенной пагинацией
        employee.messages = messages
        chat_schema = EmployeeChatSchema.model_validate(employee)

        return chat_schema


messages_service = MessagesService()
