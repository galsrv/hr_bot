from config import settings
from pages.base_service import BaseApiClient
from pages.messages.schemas import (
    EmployeeChatListSchema,
    EmployeeChatSchema,
)


class MessagesApiClient(BaseApiClient):
    """Класс методов api-клиента."""
    MODULE_URL = 'messages'

    async def get_chats(self) -> list[EmployeeChatListSchema]:
        """Получить список чатов от бэкенда."""
        url = f'{settings.API_URL}/{self.MODULE_URL}/employees'
        chats = await self.get(url)
        chats = [EmployeeChatListSchema.model_validate(c) for c in chats]
        return chats

    async def get_chat(self, chat_id: int) -> EmployeeChatSchema:
        """Получить чат от бэкенда."""
        url = (
            f'{settings.API_URL}/{self.MODULE_URL}/employees/{chat_id}/chat?page=1&size=100'
        )
        chat = await self.get(url)
        chat = EmployeeChatSchema.model_validate(chat)
        return chat

    async def mark_chat_as_read(self, chat_id: int) -> dict:
        """Пометить сообщения в чате прочитанными."""
        url = f'{settings.API_URL}/{self.MODULE_URL}/employees/{chat_id}/chat/mark_as_read'
        response = await self.post(url, {})
        return response

    async def send_message(self, data_input: dict) -> dict:
        """Пометить сообщения в чате прочитанными."""
        url = f'{settings.API_URL}/{self.MODULE_URL}/'
        response = await self.post(url, data_input)
        return response

    async def ban_unban_employee(self, employee_id: int, data_input: dict) -> dict:
        """Пометить сообщения в чате прочитанными."""
        url = f'{settings.API_URL}/{self.MODULE_URL}/employees/{employee_id}'
        response = await self.patch(url, data_input)
        return response


messages_api_client = MessagesApiClient()
