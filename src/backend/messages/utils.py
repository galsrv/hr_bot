from fastapi import status
from httpx import AsyncClient

from config import settings
from messages.constants import MESSAGE_FROM_MANAGER_PREFIX


async def send_telegram_message(chat_id: str, text: str) -> bool:
    """Отправляем ответ менеджера сотруднику через бот."""
    method = '/sendMessage'

    url = (
        f'{settings.TELEGRAM_API_URL}{settings.TELEGRAM_BOT_TOKEN}{method}'
        f'?chat_id={chat_id}&text={MESSAGE_FROM_MANAGER_PREFIX}{text}'
    )

    async with AsyncClient() as client:
        response = await client.get(url)

    if response.status_code == status.HTTP_200_OK:
        return True

    return False
