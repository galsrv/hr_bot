from base_service import BaseService
from fastapi import HTTPException, status
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from users.constants import ERROR_MESSAGE_USERNAME_TAKEN, ERROR_MESSAGE_WRONG_LOGIN_DATA
from users.models import RolesOrm, UsersOrm
from users.schemas import (
    UserCreateSchema,
    UserUpdateSchema,
)


class RoleService(BaseService):
    """Класс сервисный функций модели."""
    def __init__(self) -> None:
        super().__init__(RolesOrm)


role_service = RoleService()


class UserService(BaseService):
    """Класс сервисный функций модели."""
    def __init__(self) -> None:
        super().__init__(UsersOrm)

    async def get_multiple_entries(
        self,
        session: AsyncSession,
        role: int | None = None,
        is_active: bool | None = None,
        name: str | None = None,
        page_params: Params | None = None,
    ) -> Page:
        """Читаем записи таблицы, применяя фильтры."""
        filters = list()

        if role is not None:
            filters.append(UsersOrm.role_id == role)

        if is_active is not None:
            filters.append(UsersOrm.is_active == is_active)

        if name is not None:
            filters.append(UsersOrm.username.ilike(f'%{name}%'))

        query = select(self.model).filter(*filters).order_by(*self.model.__order_by__)
        # Пагинация результата
        result: Page = await paginate(session, query, page_params)
        logger.log(
            'DB_ACCESS',
            f'Data retrieve: model={self.model.__name__}, {len(result.items)} entries retrieved',
        )
        return result

    async def get_user_by_username(
        self,
        session: AsyncSession,
        username: str,
    ) -> UsersOrm | None:
        """Ищем пользователя по имени."""
        query = select(UsersOrm).where(UsersOrm.username == username)
        user = await session.execute(query)
        user = user.scalars().first()
        logger.log(
            'DB_ACCESS',
            f'Data retrieve: model={UsersOrm.__name__}, user {user.id if user else None} was found by username',
        )
        return user

    async def is_username_available(
        self,
        session: AsyncSession,
        username: str,
    ) -> UsersOrm:
        """Проверяем доступность запрошенного имени."""
        user = await self.get_user_by_username(session, username)

        if user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGE_USERNAME_TAKEN,
            )
        return user

    def is_user_active(
        self,
        user: UsersOrm,
    ) -> None:
        """Проверяем активность пользователя."""
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ERROR_MESSAGE_WRONG_LOGIN_DATA,
            )

    async def get_user(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> UsersOrm:
        """Получаем одну настройку проекта."""
        user: UsersOrm | None = await self.get(session, user_id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Запрошенная запись не существует',
            )

        return user

    async def create_user(
        self, session: AsyncSession, data_input: UserCreateSchema
    ) -> UsersOrm:
        """Создаем нового пользователя."""
        # Валидируем данные в БД. Это Pydantic не проверяет
        await self.is_username_available(session, data_input.username)
        await role_service.get(session, data_input.role_id)
        await self.get(session, data_input.created_by_id)
        data_input.updated_by_id = data_input.created_by_id
        new_user = await self.create(session, data_input)
        return new_user

    async def update_user(
        self, session: AsyncSession, user_id: int, data_input: UserUpdateSchema
    ) -> UsersOrm:
        """Вносим изменения в пользователя."""
        # Валидируем данные в БД. Это Pydantic не проверяет
        if hasattr(data_input, 'role_id') and data_input.role_id is not None:
            await role_service.get(session, data_input.role_id)

        user: UsersOrm = await self.get_user(session, user_id)
        user = await self.update(session, user, data_input)

        return user


user_service = UserService()
