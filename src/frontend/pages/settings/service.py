from pages.base_service import BaseApiClient
from config import settings

class SettingsApiClient(BaseApiClient):
    MODULE_URL = 'settings'

    async def get_settings(self, to_dict: bool = False) -> dict | list[dict] | None:
        '''Получить список настроек от бэкенда.'''
        url = f'{settings.API_URL}/{self.MODULE_URL}/'
        return await self.get(url)

    async def get_one_setting(self, id: int) -> dict | None:
        '''Получить одну настройку от бэкенда.'''
        url = f'{settings.API_URL}/{self.MODULE_URL}/{id}'
        return await self.get(url)

    async def update_setting(self, data_input: dict) -> dict:
        '''Изменить значение настройки.'''
        url = f'{settings.API_URL}/{self.MODULE_URL}/{data_input['id']}'
        return await self.patch(url, data_input)

settings_api_client = SettingsApiClient()