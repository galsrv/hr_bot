from aiohttp import ClientSession
from fastapi import status

from pages.base_service import BaseApiClient
from pages.users.schemas import UserReadSchema
from config import settings

class AuthApiClient(BaseApiClient):
    MODULE_URL = 'auth/sessions'

    async def _login_response_parser(self, response) -> dict:
        response_dict = await response.json()

        if response.status not in (status.HTTP_200_OK, status.HTTP_201_CREATED):
            # Парсим текст ошибки от API-сервера, ответ может приходить в разной структуре
            try:
                error_message = response_dict['detail']
                if type(error_message) is list:
                    error_message = error_message[0]['msg']
            except (KeyError, IndexError, TypeError):
                error_message = 'Произошла ошибка при обработке данных'
            return {'OK': False, 'message': error_message}

        return {'OK': True, 'message': 'Вход успешно выполнен!'} | response_dict

    async def user_login(self, data_input: dict) -> dict:
        '''Аутентификация по логину и паролю.'''
        url = f'{settings.API_URL}/{self.MODULE_URL}/'
        async with ClientSession() as session:
            async with session.post(url, json=data_input) as response:
                return await self._login_response_parser(response)

    async def get_user_by_session(self, id: int) -> UserReadSchema | None:
        '''Получить пользователя по номеру сессии.'''
        url = f'{settings.API_URL}/{self.MODULE_URL}/{id}'
        user = await self.get(url)
        return UserReadSchema(**user) if user else None

    async def delete_session(self, id: int) -> None:
        '''Удалить сессию на бэкенде.'''
        url = f'{settings.API_URL}/{self.MODULE_URL}/{id}'
        return await self.delete(url)


auth_api_client = AuthApiClient()