import asyncio
import argparse

from database import AsyncSessionLocal
from log import logger
from models import UsersOrm, SessionsOrm, RolesOrm # noqa
from users.schemas import RoleCreateSchema, UserCreateSchema
from users.service import role_service, user_service


async def create_admin(
    username: str,
    password: str,
) -> None:
    """Создаем суперпользователя, печатаем в лог его id."""

    async with AsyncSessionLocal() as session:
        # Создаем модель роли
        try:
            role_data_input = RoleCreateSchema(
                name='admin',
                can_edit_menu=True,
                can_edit_settings=True,
                can_edit_users=True,
                can_send_messages=True)
        except Exception as e:
            logger.error(f'Error validating role data: {e}')
            return
        # Создаем роль админа в БД
        try:
            role: RolesOrm = await role_service.create(session, role_data_input)
        except Exception as e:
            logger.error(f'Error while creating new role: {e}')
            return
        # Создаем модель пользователя
        try:
            user_data_input = UserCreateSchema(username=username, password=password, role_id=role.id)
        except Exception as e:
            logger.error(f'Error validating users data: {e}')
            return
        # Создаем пользователя в БД
        try:
            result: UsersOrm = await user_service.create_user(session, user_data_input)
            logger.info(f'New admin was created, id = {result.id}')
        except Exception as e:
            logger.error(f'Error while creating new admin: {e}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create admin')
    parser.add_argument('-u', required=True, help='Enter username:')
    parser.add_argument('-p', required=True, help='Enter password')
    args = parser.parse_args()

    asyncio.run(create_admin(username=args.u, password=args.p))
