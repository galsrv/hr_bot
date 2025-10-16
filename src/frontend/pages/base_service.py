from aiohttp import ClientResponse, ClientSession
from fastapi import status

from log import logger
from pages.utils import url_shortener


class BaseApiClient:
    """Базовый класс методов api-клиента."""
    async def _response_parser(self, response: ClientResponse) -> dict:
        if response.status >= status.HTTP_500_INTERNAL_SERVER_ERROR:
            return {'OK': False, 'message': 'Произошла ошибка на стороне сервера'}

        response_dict = await response.json()

        if response.status not in (
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_204_NO_CONTENT,
        ):
            # Парсим текст ошибки от API-сервера, ответ может приходить в разной структуре
            try:
                error_message = response_dict['detail']
                if type(error_message) is list:
                    error_message = error_message[0]['msg']
            except (KeyError, IndexError, TypeError):
                error_message = 'Произошла ошибка при обработке данных'
            return {'OK': False, 'message': error_message}

        return {'OK': True, 'message': 'Значение сохранено!'}

    async def get(self, url: str) -> dict | list[dict] | None:
        """Получить данные от бэкенда."""
        async with ClientSession() as session:
            async with session.get(url) as response:
                logger.log(
                    'API_REQUEST',
                    f'Method: GET, URL: {url_shortener(url)}, status: {response.status}',
                )

                if response.status >= status.HTTP_500_INTERNAL_SERVER_ERROR:
                    return {'OK': False, 'message': 'Ошибка получения данных'}

                if response.status == status.HTTP_200_OK:
                    result = await response.json()
                    return result

                return None

    async def post(self, url: str, data_input: dict) -> dict:
        """Создать запись на бэкенде."""
        async with ClientSession() as session:
            async with session.post(url, json=data_input) as response:
                logger.log(
                    'API_REQUEST',
                    f'Method: POST, URL: {url_shortener(url)}, status: {response.status}',
                )
                return await self._response_parser(response)

    async def patch(self, url: str, data_input: dict) -> dict:
        """Обновить данные записи на бэкенде."""
        async with ClientSession() as session:
            async with session.patch(url, json=data_input) as response:
                logger.log(
                    'API_REQUEST',
                    f'Method: PATCH, URL: {url_shortener(url)}, status: {response.status}',
                )
                return await self._response_parser(response)

    async def delete(self, url: str) -> None:
        """Удалить данне на бэкенде бэкенда."""
        async with ClientSession() as session:
            async with session.delete(url) as response:
                logger.log(
                    'API_REQUEST',
                    f'Method: DELETE, URL: {url_shortener(url)}, status: {response.status}',
                )
                return
