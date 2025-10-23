from fastapi import APIRouter, Depends
from fastapi_pagination import Page, Params
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings as s
from database import get_async_session
from menu.schemas import (
    MenuItemCreateSchema,
    MenuItemReadSchema,
    MenuItemUpdateSchema,
    MenuUploadSchema,
)
from menu.service import menu_service

menu_router = APIRouter()


@menu_router.get(
    '/', response_model=Page[MenuItemReadSchema], summary='Получить записи справочника'
)
async def get_menu_page(
    page_params: Params = Depends(), session: AsyncSession = Depends(get_async_session)
) -> Page[MenuItemReadSchema]:
    """Эндпоинт получения записи справочника."""
    menu_page = await menu_service.get_menu_page(session, page_params)
    return menu_page


@menu_router.get(
    '/{menu_item_id}', response_model=MenuItemReadSchema, summary='Получить запись справочника'
)
async def get_menu_item(
    menu_item_id: int,
    session: AsyncSession = Depends(get_async_session)
) -> MenuItemReadSchema:
    """Эндпоинт получения записи справочника."""
    menu_item = await menu_service.get_menu_item(session, menu_item_id)
    return menu_item


@menu_router.post(
    '/', response_model=MenuItemReadSchema, summary='Создать запись справочника'
)
async def create_menu_item(
    data_input: MenuItemCreateSchema, session: AsyncSession = Depends(get_async_session)
) -> MenuItemReadSchema:
    """Эндпоинт создания записи справочника."""
    new_menu_item = await menu_service.create_menu_item(session, data_input)
    return new_menu_item


@menu_router.patch(
    '/{menu_item_id}', response_model=MenuItemReadSchema, summary='Изменить запись справочника'
)
async def update_menu_item(
    menu_item_id: int,
    data_input: MenuItemUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
) -> MenuItemReadSchema:
    """Эндпоинт изменения записи справочника."""
    edited_menu_item = await menu_service.update_menu_item(
        session, menu_item_id, data_input)
    return edited_menu_item


@menu_router.delete(
    '/{menu_item_id}', response_model=None, status_code=204, summary='Удалить запись справочника'
)
async def delete_menu_item(
    menu_item_id: int, session: AsyncSession = Depends(get_async_session)
) -> None:
    """Эндпоинт удаления записи справочника."""
    await menu_service.delete_menu_item(session, menu_item_id)


@menu_router.post(
    '/download', response_model=None, summary='Выгрузить справочник в файл'
)
async def download_menu(
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """Эндпоинт выгрузки справочника в файл."""
    await menu_service.download_data(session, s.FIXTURES_MENU_PATH)


@menu_router.post(
    '/upload', response_model=None, summary='Загрузить справочник из файла'
)
async def upload_menu(
    data_input: MenuUploadSchema,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """Эндпоинт загрузки справочника из файла."""
    await menu_service.upload_data(
        session, s.FIXTURES_MENU_PATH, MenuItemCreateSchema, data_input.created_by_id
    )
