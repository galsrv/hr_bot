from fastapi import APIRouter, Depends
from fastapi_pagination import Page, Params
from sqlalchemy.ext.asyncio import AsyncSession

from menu.schemas import (
    MenuItemCreateSchema,
    MenuItemReadSchema,
    MenuItemUpdateSchema
)
from menu.service import menu_service

from database import get_async_session

menu_router = APIRouter()

@menu_router.get(
    '/',
    response_model=Page[MenuItemReadSchema],
    summary='Получить записи справочника'
)
async def get_menu_page(
    page_params: Params = Depends(),
    session: AsyncSession = Depends(get_async_session)
):
    '''Эндпоинт получения записи справочника.'''
    menu_page = await menu_service.get_menu_page(session, page_params)
    return menu_page

@menu_router.get(
    '/{id}',
    response_model=MenuItemReadSchema,
    summary='Получить запись справочника'
)
async def get_menu_item(
    id: int,
    session: AsyncSession = Depends(get_async_session)
):
    '''Эндпоинт получения записи справочника.'''
    menu_item = await menu_service.get_menu_item(session, id)
    return menu_item

@menu_router.post(
    '/',
    response_model=MenuItemReadSchema,
    summary='Создать запись справочника'
)
async def create_menu_item(
    data_input: MenuItemCreateSchema,
    session: AsyncSession = Depends(get_async_session)
):
    '''Эндпоинт создания записи справочника.'''
    new_menu_item = await menu_service.create_menu_item(session, data_input)
    return new_menu_item

@menu_router.patch(
    '/{id}',
    response_model=MenuItemReadSchema,
    summary='Изменить запись справочника'
)
async def update_menu_item(
    id: int,
    data_input: MenuItemUpdateSchema,
    session: AsyncSession = Depends(get_async_session)
):
    '''Эндпоинт изменения записи справочника.'''
    edited_menu_item = await menu_service.update_menu_item(session, id, data_input)
    return edited_menu_item

@menu_router.delete(
    '/{id}',
    response_model=None,
    status_code=204,
    summary='Удалить запись справочника'
)
async def delete_menu_item(
    id: int,
    session: AsyncSession = Depends(get_async_session)
):
    '''Эндпоинт удаления записи справочника.'''
    await menu_service.delete_menu_item(session, id)
