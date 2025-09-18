from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.schemas import (
    SessionReadSchema,
    SessionInSchema,
)
from auth.service import session_service
from users.schemas import (
    UserReadSchema,
    UserLoginSchema,
)
from database import get_async_session

auth_router = APIRouter()


@auth_router.post(
    '/',
    response_model=SessionReadSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Аутентификация пользователя с созданием сессии"
)
async def create_session(
    data_input: UserLoginSchema,
    session: AsyncSession = Depends(get_async_session)
) -> SessionReadSchema:
    '''Эндпоинт аутентификации пользователя.'''
    user_session = await session_service.user_login(session, data_input)
    return user_session

@auth_router.get(
    '/{id}',
    response_model=UserReadSchema,
    status_code=status.HTTP_200_OK,
    summary="Получение пользователя по сессии"
)
async def get_session(
    id: str,
    session: AsyncSession = Depends(get_async_session)
) -> UserReadSchema:
    '''Эндпоинт получения пользователя по сессии.'''
    session_schema = SessionInSchema(id=id)
    user = await session_service.get_user_by_session(session, session_schema)
    return user

@auth_router.delete(
    '/{id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление сессии"
)
async def delete_session(
    id: str,
    session: AsyncSession = Depends(get_async_session)
) -> None:
    '''Эндпоинт получения пользователя по сессии.'''
    await session_service.delete(session, id)