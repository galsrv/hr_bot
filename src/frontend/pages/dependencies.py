from fastapi import Depends, Request

from pages.auth.service import auth_api_client
from pages.users.schemas import UserReadSchema


async def get_current_user(request: Request) -> UserReadSchema | None:
    """Получить текущего пользователя."""
    session_id = request.cookies.get('session_id')
    return await auth_api_client.get_user_by_session(session_id) if session_id else None


async def get_edit_users_permission(
    user: UserReadSchema = Depends(get_current_user)
) -> bool:
    """Получить флаг пермишена на изменение пользователей."""
    return user.role.can_edit_users if user else False


async def get_edit_settings_permission(
    user: UserReadSchema = Depends(get_current_user),
) -> bool:
    """Получить флаг пермишена на изменение настроек."""
    return user.role.can_edit_settings if user else False


async def get_send_messages_permission(
    user: UserReadSchema = Depends(get_current_user),
) -> bool:
    """Получить флаг пермишена на отправку сообщений."""
    return user.role.can_send_messages if user else False


async def get_edit_menu_permission(
    user: UserReadSchema = Depends(get_current_user)
) -> bool:
    """Получить флаг пермишена на изменение меню."""
    return user.role.can_edit_menu if user else False
