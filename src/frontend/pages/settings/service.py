from config import settings
from pages.base_service import BaseApiClient


class SettingsApiClient(BaseApiClient):
    """Класс методов api-клиента."""
    MODULE_URL = 'settings'

    async def get_settings(self, to_dict: bool = False) -> dict | list[dict] | None:
        """Получить список настроек от бэкенда."""
        url = f'{settings.API_URL}/{self.MODULE_URL}/'
        return await self.get(url)

    async def get_one_setting(self, setting_id: int) -> dict | None:
        """Получить одну настройку от бэкенда."""
        url = f'{settings.API_URL}/{self.MODULE_URL}/{setting_id}'
        return await self.get(url)

    async def update_setting(self, data_input: dict) -> dict:
        """Изменить значение настройки."""
        url = f'{settings.API_URL}/{self.MODULE_URL}/{data_input["id"]}'
        return await self.patch(url, data_input)

    async def download_settings(self) -> dict:
        """Выгрузить настройки проект в файл."""
        url = f'{settings.API_URL}/{self.MODULE_URL}/download'
        return await self.post(url, {})

    async def upload_settings(self) -> dict:
        """Загрузить настройки проекта из файла."""
        url = f'{settings.API_URL}/{self.MODULE_URL}/upload'
        return await self.post(url, {})


settings_api_client = SettingsApiClient()
