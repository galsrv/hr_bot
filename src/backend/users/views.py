from fastapi import APIRouter, Depends
from fastapi_pagination import Page, Params
from sqlalchemy.ext.asyncio import AsyncSession

from users.schemas import (
    UserCreateSchema,
    UserReadSchema,
    UserUpdateSchema
)
from users.service import user_service
from database import get_async_session

auth_router = APIRouter()


@auth_router.get(
    '/',
    response_model=Page[UserReadSchema],
    summary="Получить список пользователей"
)
async def retrieve_users(
    role: int | None = None,
    is_active: bool | None = None,
    name: str | None = None,
    page_params: Params = Depends(),
    session: AsyncSession = Depends(get_async_session)
) -> Page[UserReadSchema]:
    '''Эндпоинт получения списка пользователей с учетом фильтров и пагинации.'''
    users = await user_service.get_multiple_entries(session, role, is_active, name, page_params)
    return users

@auth_router.get(
    '/{id}',
    response_model=UserReadSchema,
    summary="Получить пользователя"
)
async def retrieve_user(
    id: int,
    session: AsyncSession = Depends(get_async_session)
) -> UserReadSchema:
    '''Эндпоинт получения пользователя.'''
    user = await user_service.get(session, id)
    return user

@auth_router.post(
    '/',
    response_model=UserReadSchema,
    summary="Создать нового пользователя"
)
async def create_user(
    new_user: UserCreateSchema,
    session: AsyncSession = Depends(get_async_session)
) -> UserReadSchema:
    '''Эндпоинт создания пользователя.'''
    new_user = await user_service.user_create(session, new_user)
    return new_user

@auth_router.patch(
    '/{id}',
    response_model=UserReadSchema,
    summary="Изменить пользователя"
)
async def change_user(
    id: int,
    data_input: UserUpdateSchema,
    session: AsyncSession = Depends(get_async_session)
) -> UserReadSchema:
    '''Эндпоинт изменения пользователя.'''
    user = await user_service.user_update(session, id, data_input)
    return user
