import asyncio
from http import HTTPStatus
import os

from aiohttp import ClientSession
from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), '../../infra/.env')
load_dotenv(dotenv_path)

API_HOST = os.getenv('API_HOST')
API_PORT = os.getenv('API_PORT')
API_URL = f'{API_HOST}:{API_PORT}/api'

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