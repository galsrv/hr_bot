from nicegui import APIRouter, app as ui

from pages.layout import layout_decorator

root_router = APIRouter()

@root_router.page('/', title='Корневая страница сайта')
@root_router.page('/admin', title='Корневая страница админки')
@layout_decorator
async def site_root_page():
    ui.label('Панель администратора Телеграмм-бота').props('header').classes('text-bold text-h2')
