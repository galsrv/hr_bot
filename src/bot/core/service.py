import asyncio
from http import HTTPStatus

from aiohttp import ClientSession
from core.log import logger

from config import settings as s

class ApiClientException(Exception):
    pass

class ApiClient():
    '''Класс функций api-клиента'''
    API_URL = f'{s.API_HOST}:{s.API_PORT}/api'

    def timeout_decorator(func):
        '''Функция-декоратор для повторного вызова API-сервера'''
        async def wrapper(*args, **kwargs):
            result = None
            for _ in range(s.API_CONNECTION_ATTEMPTS):
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception:
                    pass
                await asyncio.sleep(s.TIMEOUT)
            # Если за указанное число попыток данные загрузить не удалось...
            if not result:
                logger.error(s.ERROR_CONNECTION_TO_BACKEND_API)
                raise ApiClientException(s.ERROR_CONNECTION_TO_BACKEND_API)
        return wrapper

    @timeout_decorator
    async def get_settings(self) -> dict | None:
        '''Получить список настроек от бэкенда.'''
        url = f'{self.API_URL}/settings/'

        async with ClientSession() as session:
            async with session.get(url) as response:
                logger.log('API_REQUEST', f'Request to {url}, reponse status {response.status}')
                if response.status == HTTPStatus.OK:
                    result = await response.json()
                    # Преобразуем список в словарь ключ-значение
                    result = {el['name']: el['value'] for el in result}
                    return result
                return None

    @timeout_decorator
    async def get_menu_page(self, page: int = 1, size: int = 4) -> dict | None:
        '''Получить список элементов меню от бэкенда.'''
        url = f'{self.API_URL}/menu/?page={page}&size={size}'

        async with ClientSession() as session:
            async with session.get(url) as response:
                logger.log('API_REQUEST', f'Request to {url}, reponse status {response.status}')
                if response.status == HTTPStatus.OK:
                    result = await response.json()
                    return result
                return None

    @timeout_decorator
    async def get_menu_item(self, id: int) -> dict | None:
        '''Получить элемент меню от бэкенда.'''
        url = f'{self.API_URL}/menu/{id}'

        async with ClientSession() as session:
            async with session.get(url) as response:
                logger.log('API_REQUEST', f'Request to {url}, reponse status {response.status}')
                if response.status == HTTPStatus.OK:
                    result = await response.json()
                    return result
                return None

    @timeout_decorator
    async def get_or_create_employee(self, id, name) -> dict | None:
        '''Получить сотрудника бэкенда.'''
        url = f'{self.API_URL}/messages/employees/'
        data = {'id': id, 'name': name}

        async with ClientSession() as session:
            async with session.post(url, json=data) as response:
                logger.log('API_REQUEST', f'Request to {url} with {data}, reponse status {response.status}')
                if response.status in (HTTPStatus.CREATED, HTTPStatus.OK):
                    result = await response.json()
                    return result
                return None

    @timeout_decorator
    async def send_message(self, text, author) -> bool:
        '''Отправить сообщение сотрудника на бэкенд.'''
        url = f'{self.API_URL}/messages/'
        data = {'employee_id': author, 'text': text}

        async with ClientSession() as session:
            async with session.post(url, json=data) as response:
                logger.log('API_REQUEST', f'Request to {url} with {data}, reponse status {response.status}')
                if response.status == HTTPStatus.CREATED:
                    return True
                return False

api_client = ApiClient()

# Ручные тесты
async def run_tests():
    data = await api_client.get_settings()
    print(data)

if __name__ == '__main__':
    asyncio.run(run_tests())