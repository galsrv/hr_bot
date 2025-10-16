import asyncio

from aiogram import Bot, Dispatcher

from config import BotSettings
from config import settings as s
from core.service import ApiClientException, api_client


async def on_startup(bot: Bot, dispatcher: Dispatcher) -> None:
    """Загрузка настроек при старте бота и далее обновление по таймеру."""

    async def refresh_settings() -> None:
        """Обновления настройки в цикле."""
        while True:
            try:
                bot_settings: dict = await api_client.get_settings()
                bs = BotSettings(**bot_settings)
                dispatcher.workflow_data['settings'] = bs
            except ApiClientException:
                pass
            await asyncio.sleep(s.SETTINGS_UPDATE_DELAY)

    asyncio.create_task(refresh_settings())


def register_startup(dp: Dispatcher) -> None:
    """Регистрируем функцию для запуска на старте работы бота."""
    dp.startup.register(on_startup)
