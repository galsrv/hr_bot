from config import settings
from pages.base_service import BaseApiClient
from pages.menu.schemas import MenuItemsPageSchema


class MenuApiClient(BaseApiClient):
    """Класс методов api-клиента."""
    MODULE_URL = 'menu'

    async def get_menu_item(self, menu_item_id: int) -> dict:
        """Получить запись справочника от бэкенда."""
        url = f'{settings.API_URL}/{self.MODULE_URL}/{menu_item_id}'
        menu_item = await self.get(url)
        return menu_item

    async def get_menu_page(self, page: int = 1, size: int = 50) -> MenuItemsPageSchema:
        """Получить запись справочника от бэкенда."""
        url = f'{settings.API_URL}/{self.MODULE_URL}/?page={page}&size={size}'
        menu_page = await self.get(url)
        menu_page = MenuItemsPageSchema.model_validate(menu_page)
        return menu_page

    async def create_menu_item(self, data_input: dict) -> dict:
        """Создать запись справочника на бэкенде."""
        url = f'{settings.API_URL}/{self.MODULE_URL}/'
        menu_item: dict = await self.post(url, data_input)
        return menu_item

    async def update_menu_item(self, menu_item_id: int, data_input: dict) -> dict:
        """Изменить запись справочника на бэкенде."""
        url = f'{settings.API_URL}/{self.MODULE_URL}/{menu_item_id}'
        menu_item: dict = await self.patch(url, data_input)
        return menu_item

    async def delete_menu_item(self, menu_item_id: int) -> None:
        """Удалить запись справочника на бэкенде."""
        url = f'{settings.API_URL}/{self.MODULE_URL}/{menu_item_id}'
        await self.delete(url)

    async def download_menu(self) -> dict:
        """Выгрузить справочник в файл."""
        url = f'{settings.API_URL}/{self.MODULE_URL}/download'
        return await self.post(url, {})

    async def upload_menu(self, data_input: dict) -> dict:
        """Загрузить справочник из файла."""
        url = f'{settings.API_URL}/{self.MODULE_URL}/upload'
        return await self.post(url, data_input)


menu_api_client = MenuApiClient()
