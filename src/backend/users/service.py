from fastapi import HTTPException, status
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from base_service import BaseService
from users.constants import(
    ERROR_MESSAGE_USERNAME_TAKEN,
    ERROR_MESSAGE_ROLE_NOT_EXIST,
    ERROR_MESSAGE_ENTRY_NOT_EXIST,
    ERROR_MESSAGE_WRONG_PASSWORD,
)
from users.models import RolesOrm, UsersOrm, SessionsOrm
from users.schemas import UserCreateSchema, UserUpdateSchema, SessionCreateSchema
from users.utils import verify_password

class RoleService(BaseService):
    def __init__(self):
        super().__init__(RolesOrm)

role_service = RoleService()

class SessionService(BaseService):
    def __init__(self):
        super().__init__(SessionsOrm)

session_service = SessionService()


class UserService(BaseService):
    def __init__(self):
        super().__init__(UsersOrm)

    async def get_multiple_entries(
        self,
        session: AsyncSession,
        role: int | None = None,
        is_active: bool | None = None,
        name: str | None = None,
        page_params: Params = None,
     ):
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
        logger.log('DB_ACCESS', f'Data retrieve: model={self.model.__name__}, {len(result.items)} entries retrieved')        
        return result

    async def is_username_available(
        self,
        session: AsyncSession,
        username: str,
    ) -> HTTPException | None:
        '''Проверяем, занято ли запрошенное имя пользователя.'''
        query = select(UsersOrm).where(UsersOrm.username == username)
        result = await session.execute(query)
        result = result.scalars().one_or_none()
        logger.log('DB_ACCESS', f'Data retrieve: model={UsersOrm.__name__}, username availability was checked') 
        if result is not None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=ERROR_MESSAGE_USERNAME_TAKEN)

    async def get_user_by_username(
        self,
        session: AsyncSession,
        username: str,
    ) -> UsersOrm:           
        '''Ищем пользователя по имени.'''
        query = select(UsersOrm).where(UsersOrm.username == username)
        result = await session.execute(query)
        result = result.scalars().one_or_none()

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGE_ENTRY_NOT_EXIST)

        logger.log('DB_ACCESS', f'Data retrieve: model={UsersOrm.__name__}, user {result.id} was found by username')
        return result

    async def does_role_exist(
        self,
        session: AsyncSession,
        role_id: int,
    ) -> HTTPException | None:
        '''Проверяем, существует ли указанная роль.'''
        query = select(RolesOrm).where(RolesOrm.id == role_id)
        result = await session.execute(query)
        result = result.scalars().one_or_none()
        logger.log('DB_ACCESS', f'Data retrieve: model={RolesOrm.__name__}, role"s existense was checked') 
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=ERROR_MESSAGE_ROLE_NOT_EXIST
            )

    async def user_create(
            self,
            session: AsyncSession,
            data_input: UserCreateSchema
    ) -> UsersOrm:
        '''Создаем нового пользователя.'''
        # Валидируем то, что не выловил Pydantic. Всё, что связано с данными в БД
        await self.is_username_available(session, data_input.username)
        await self.does_role_exist(session, data_input.role_id)

        new_user = await self.create(session, data_input)
        return new_user

    async def user_update(
            self,
            session: AsyncSession,
            id: int,
            data_input: UserUpdateSchema
    ) -> UsersOrm:
        '''Вносим изменения в пользователя.'''
        # Валидируем то, что не выловил Pydantic. Всё, что связано с данными в БД
        if hasattr(data_input, 'role_id') and data_input.role_id is not None:
            await self.does_role_exist(session, data_input.role_id)
        
        new_user = await self.update(session, id, data_input)
        return new_user

    async def user_login(
            self,
            session: AsyncSession,
            user: UsersOrm,
            password_entered: str
    ) -> SessionsOrm:
        '''Аутентифицируем пользователя.'''
        if not verify_password(password_entered, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_MESSAGE_WRONG_PASSWORD)
        user_session_schema = SessionCreateSchema(user_id=user.id, session_id='generate me')
        user_session = await session_service.create(session, user_session_schema)
        return user_session

user_service = UserService()

