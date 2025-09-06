import json

from aiohttp import ClientSession
from fastapi import status

from config import settings

class ApiClient():

    async def get_settings(self, to_dict: bool = False) -> dict | list[dict] | None:
        '''Получить список настроек от бэкенда.'''
        url = f'{settings.API_URL}/settings'

        async with ClientSession() as session:
            async with session.get(url) as response:
                if response.status == status.HTTP_200_OK:
                    result = await response.json()
                    if to_dict:
                        # Для бота преобразуем список в словарь ключ-значение
                        result = {el['name']: el['value'] for el in result}
                    return result
                return None

    async def get_one_setting(self, id: int) -> dict | None:
        '''Получить одну настройку от бэкенда.'''
        url = f'{settings.API_URL}/settings/{id}'

        async with ClientSession() as session:
            async with session.get(url) as response:
                if response.status == status.HTTP_200_OK:
                    result = await response.json()
                    return result
                return None

    async def update_setting_value(self, id: int, new_value: str) -> dict:
        '''Изменить значение настройки.'''
        url = f'{settings.API_URL}/settings/{id}'

        async with ClientSession() as session:
            async with session.patch(url, json={'value': new_value}) as response:
                # Преобразуем полученную строку в python-типы данных
                response_string = await response.content.read()
                response_dict: dict = json.loads(response_string.decode())

                if not response.status == status.HTTP_200_OK:
                    try:
                        error_message = response_dict['detail'][0]['msg']
                    except (KeyError, IndexError):
                        error_message = 'Произошла ошибка при сохранении данных'

                    return {'OK': False, 'message': error_message}

                return {'OK': True, 'message': 'Значение сохранено!'}

api_client = ApiClient()