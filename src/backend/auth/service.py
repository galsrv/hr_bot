from fastapi import HTTPException, status
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from base_service import BaseService
from auth.constants import(
    ERROR_MESSAGE_WRONG_PASSWORD,
    ERROR_MESSAGE_ENTRY_NOT_EXIST
)
from auth.models import SessionsOrm
from auth.schemas import (
    SessionCreateSchema,
    SessionInSchema
)
from auth.utils import verify_password
from users.models import UsersOrm
from users.schemas import UserLoginSchema
from users.service import user_service

class SessionService(BaseService):
    def __init__(self):
        super().__init__(SessionsOrm)

    async def user_login(
            self,
            session: AsyncSession,
            login_schema: UserLoginSchema
    ) -> SessionsOrm:
        '''Аутентифицируем пользователя по имени и паролю.'''
        user = await user_service.get_user_by_username(session, login_schema.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_MESSAGE_ENTRY_NOT_EXIST) 

        user_service.is_user_active(user)

        if not verify_password(login_schema.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_MESSAGE_WRONG_PASSWORD)

        user_session_schema = SessionCreateSchema(user_id=user.id)
        user_session = await session_service.create(session, user_session_schema)
        return user_session

    async def get_user_by_session(
            self,
            session: AsyncSession,
            user_session_provided: SessionInSchema,
    ) -> UsersOrm:
        '''Получаем пользователя по сессии.'''
        user_session: SessionsOrm = await session_service.get(session, user_session_provided.id)
        user_service.is_user_active(user_session.user)
        return user_session.user

    async def delete_sessions_by_user(
            self,
            session: AsyncSession,
            user_id: int,
    ) -> None:
        '''Удаляем все сессии пользователя (не используется).'''
        query = delete(SessionsOrm).where(user_id=user_id)
        session.execute(query)
        session.commit()

session_service = SessionService()

