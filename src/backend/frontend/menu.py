from nicegui import ui

from frontend.layout import layout_decorator

@ui.page('/menu', title='Дерево меню бота')
@layout_decorator
def menu_page():
    ui.label('Menu tree will be here').classes('text-2xl')
    # ui.button('TEST', on_click=lambda: ui.navigate.to(settings_page))