from fastapi import APIRouter, Depends, status
from fastapi_pagination import Page, Params
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from users.schemas import (
    RoleReadSchema,
    UserCreateSchema,
    UserReadSchema,
    UserUpdateSchema,
)
from users.service import role_service, user_service

users_router = APIRouter()
auth_router = APIRouter()


@users_router.get(
    '/roles', response_model=list[RoleReadSchema], summary='Получить список ролей'
)
async def retrieve_roles(
    session: AsyncSession = Depends(get_async_session),
) -> list[RoleReadSchema]:
    """Эндпоинт получения списка ролей пользователей."""
    roles = await role_service.get_all(session)
    return roles


@users_router.get(
    '/', response_model=Page[UserReadSchema], summary='Получить список пользователей'
)
async def retrieve_users(
    role: int | None = None,
    is_active: bool | None = None,
    name: str | None = None,
    # Параметры фильтрации можно было бы вынести в модель Pydantic, но это пришлось бы стыковать с пагинацией
    page_params: Params = Depends(),
    session: AsyncSession = Depends(get_async_session),
) -> Page[UserReadSchema]:
    """Эндпоинт получения списка пользователей с учетом фильтров и пагинации."""
    users = await user_service.get_multiple_entries(
        session, role, is_active, name, page_params
    )
    return users


@users_router.get(
    '/{user_id}', response_model=UserReadSchema, summary='Получить пользователя'
)
async def retrieve_user(
    user_id: int, session: AsyncSession = Depends(get_async_session)
) -> UserReadSchema:
    """Эндпоинт получения пользователя."""
    user = await user_service.get_user(session, user_id)
    return user


@users_router.post(
    '/',
    response_model=UserReadSchema,
    status_code=status.HTTP_201_CREATED,
    summary='Создать нового пользователя',
)
async def create_user(
    new_user: UserCreateSchema, session: AsyncSession = Depends(get_async_session)
) -> UserReadSchema:
    """Эндпоинт создания пользователя."""
    new_user = await user_service.create_user(session, new_user)
    return new_user


@users_router.patch(
    '/{user_id}', response_model=UserReadSchema, summary='Изменить пользователя'
)
async def change_user(
    user_id: int,
    data_input: UserUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
) -> UserReadSchema:
    """Эндпоинт изменения пользователя."""
    user = await user_service.update_user(session, user_id, data_input)
    return user
