from fastapi import HTTPException, status
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from auth.constants import (
    ERROR_MESSAGE_WRONG_LOGIN_DATA,
)
from auth.models import SessionsOrm
from auth.schemas import SessionCreateSchema, SessionInSchema
from auth.utils import verify_password
from base_service import BaseService
from users.models import UsersOrm
from users.schemas import UserLoginSchema
from users.service import user_service


class SessionService(BaseService):
    def __init__(self):
        super().__init__(SessionsOrm)

    async def user_login(
        self, session: AsyncSession, login_schema: UserLoginSchema
    ) -> SessionsOrm:
        """Аутентифицируем пользователя по имени и паролю."""
        user: UsersOrm | None = await user_service.get_user_by_username(
            session, login_schema.username
        )

        # Пользователя нет, он неактивен или введен неверный пароль...
        if (
            not user
            or not user.is_active
            or not verify_password(login_schema.password, user.password)
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_MESSAGE_WRONG_LOGIN_DATA,
            )

        user_session_schema = SessionCreateSchema(user_id=user.id)
        user_session = await session_service.create(session, user_session_schema)
        return user_session

    async def get_user_by_session(
        self,
        session: AsyncSession,
        user_session_provided: SessionInSchema,
    ) -> UsersOrm:
        """Получаем пользователя по сессии."""
        user_session: SessionsOrm | None = await session_service.get(
            session, user_session_provided.id
        )

        if not user_session or not user_session.user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_MESSAGE_WRONG_LOGIN_DATA,
            )

        # Тут какой-то нюанс жадной загрузки, объект user_session.user неполноценный, приходится отдельным запросом доставать
        user: UsersOrm | None = await user_service.get(session, user_session.user.id)
        return user

    async def delete_sessions_by_user(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> None:
        """Удаляем все сессии пользователя (не используется)."""
        query = delete(SessionsOrm).where(user_id=user_id)
        session.execute(query)
        session.commit()


session_service = SessionService()
