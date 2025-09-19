from nicegui import APIRouter, ui

from pages.urls import MENU_PAGE_URL

menu_router = APIRouter(prefix=MENU_PAGE_URL)

@menu_router.page('/', title='Дерево меню бота')
async def menu_page():
    ui.label('Menu tree will be here').classes('text-2xl')