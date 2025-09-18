from urllib.parse import urlencode

from pages.base_service import BaseApiClient
from pages.users.schemas import UsersListPageSchema
from config import settings

class UsersApiClient(BaseApiClient):
    MODULE_URL = 'users'

    async def get_users(
        self,
        page: int = 1,
        role: int = None,
        is_active: bool = None,
        name: str = None
)-> UsersListPageSchema | None:
        '''Получить список пользователей от бэкенда.'''
        params = {
            'page': page,
            'size': settings.USERS_PER_PAGE,}
        if role is not None:
            params['role'] = role
        if is_active is not None:
            params['is_active'] = is_active
        if name:
            params['name'] = name

        query_string = urlencode(params)
        url = f'{settings.API_URL}/{self.MODULE_URL}/?{query_string}'
        response = await self.get(url)
        return UsersListPageSchema(**response) if response else None

    async def get_roles(self) -> dict:
        '''Получить список ролей от бэкенда.'''
        url = f'{settings.API_URL}/{self.MODULE_URL}/roles'
        roles = await self.get(url)
        return {r['id']: r['name'] for r in roles}

    async def get_user(self, id: int) -> dict | None:
        '''Получить список пользователей от бэкенда.'''
        url = f'{settings.API_URL}/{self.MODULE_URL}/{id}'
        return await self.get(url)

    async def create_user(self, data_input: dict) -> dict:
        '''Создать пользователя.'''
        url = f'{settings.API_URL}/{self.MODULE_URL}/'
        return await self.post(url, data_input)

    async def update_user(self, id: int, data_input: dict) -> dict:
        '''Изменить пользователя.'''
        url = f'{settings.API_URL}/{self.MODULE_URL}/{id}'
        return await self.patch(url, data_input)

users_api_client = UsersApiClient()