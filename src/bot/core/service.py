import asyncio
from math import ceil
from http import HTTPStatus

from aiohttp import ClientSession
from core.log import logger

from config import settings as s

menu = [
    {'id': 1, 'button_text': 'Отпуск', 'answer': 'Напишите заявление чтобы уйти в отпуск'},
    {'id': 2, 'button_text': 'Больничный', 'answer': 'Оповестите отдел кадров об уходе на больничный'},
    {'id': 3, 'button_text': 'Увольнение', 'answer': 'Напишите заявление чтобы уволиться по собственному желанию'},
    {'id': 4, 'button_text': 'Зарплата', 'answer': 'Заработная плата выплачивается 5 и 20 числа каждого месяца'},
    {'id': 5, 'button_text': 'Премия', 'answer': 'Премия выплачивается по итогам года'},
    {'id': 6, 'button_text': 'Переработки', 'answer': 'Переработки оплачиваются согласно Политике Компании'},
    {'id': 7, 'button_text': 'Льготы', 'answer': 'Сотрудник имеет право на ряд льгот'},
    {'id': 8, 'button_text': 'Связь', 'answer': 'Сотрудник имеет право на корпоративную связь'},
    {'id': 9, 'button_text': 'Учеба', 'answer': 'Сотрудник может пройти дополнительное обучение'},
    {'id': 10, 'button_text': 'Развитие', 'answer': 'Сотруднику предоставляются возможности для развития'},
]

def _get_menu_page(page: int, page_size: int):
    # logger.debug(page)
    # logger.debug(menu[page_size * (page - 1): page_size * page])
    return {
        'items': menu[page_size * (page - 1): page_size * page],
        'page': page,
        'pages': ceil(len(menu)/page_size),
        'total': len(menu)
    }

def _get_menu_item(id: int) -> dict | None:
    for el in menu:
        if el['id'] == id:
            return el

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
        '''Получить список настроек от бэкенда.'''
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