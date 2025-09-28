import asyncio
from http import HTTPStatus

from aiohttp import ClientSession

from config import settings


API_URL = f'{settings.API_HOST}:{settings.API_PORT}/api'

class ApiClient():

    async def get_settings(self) -> dict | None:
        '''Получить список настроек от бэкенда.'''
        url = f'{API_URL}/settings'

        async with ClientSession() as session:
            async with session.get(url) as response:
                if response.status == HTTPStatus.OK:
                    result = await response.json()
                    # Преобразуем список в словарь ключ-значение
                    result = {el['name']: el['value']
                            if not el['int_type']
                            else int(el['value']) for el in result}
                    return result
                return None

api_client = ApiClient()

# Ручные тесты
async def run_tests():
    data = await api_client.get_settings()
    print(data)

if __name__ == '__main__':
    asyncio.run(run_tests())