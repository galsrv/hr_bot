from nicegui import APIRouter, ui


root_router = APIRouter()

@root_router.page('/', title='Корневая страница сайта')
@root_router.page('/admin', title='Корневая страница админки')
async def site_root_page():
    ui.label('Панель администратора Телеграмм-бота').props('header').classes('text-bold text-h2')
