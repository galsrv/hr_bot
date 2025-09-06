from nicegui import APIRouter, ui

from pages.layout import layout_decorator
from pages.urls import MENU_PAGE_URL
from pages.utils import client_connector_error_decorator

menu_router = APIRouter(prefix=MENU_PAGE_URL)

@menu_router.page('/', title='Дерево меню бота')
@client_connector_error_decorator
@layout_decorator
async def menu_page():
    ui.label('Menu tree will be here').classes('text-2xl')