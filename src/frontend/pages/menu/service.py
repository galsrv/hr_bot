from pages.base_service import BaseApiClient
from pages.menu.schemas import (
    MenuItemsPageSchema
)
from config import settings

class MenuApiClient(BaseApiClient):
    MODULE_URL = 'menu'

    async def get_menu_item(self, id: int) -> dict:
        '''Получить запись справочника от бэкенда.'''
        url = f'{settings.API_URL}/{self.MODULE_URL}/{id}'
        menu_item = await self.get(url)
        return menu_item

    async def get_menu_page(self, page: int = 1, size: int = 50) -> MenuItemsPageSchema:
        '''Получить запись справочника от бэкенда.'''
        url = f'{settings.API_URL}/{self.MODULE_URL}/?page={page}&size={size}'
        menu_page = await self.get(url)
        menu_page = MenuItemsPageSchema.model_validate(menu_page)
        return menu_page

    async def create_menu_item(self, data_input: dict) -> dict:
        '''Создать запись справочника на бэкенде.'''
        url = f'{settings.API_URL}/{self.MODULE_URL}/'
        menu_item: dict = await self.post(url, data_input)
        return menu_item

    async def update_menu_item(self, id: int, data_input: dict) -> dict:
        '''Изменить запись справочника на бэкенде.'''
        url = f'{settings.API_URL}/{self.MODULE_URL}/{id}'
        menu_item: dict = await self.patch(url, data_input)
        return menu_item

    async def delete_menu_item(self, id: int) -> None:
        '''Удалить запись справочника на бэкенде.'''
        url = f'{settings.API_URL}/{self.MODULE_URL}/{id}'
        await self.delete(url)

menu_api_client = MenuApiClient()