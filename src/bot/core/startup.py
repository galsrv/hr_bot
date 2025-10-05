import asyncio
from aiogram import Bot, Dispatcher

from config import BotSettings, settings as s
from core.service import api_client, ApiClientException

async def on_startup(bot: Bot, dispatcher: Dispatcher):
    '''Загрузка настроек при старте бота и далее обновление по таймеру'''
    async def refresh_settings():
        while True:
            try:
                bot_settings: dict = await api_client.get_settings()
                bs = BotSettings(**bot_settings)
                dispatcher.workflow_data['settings'] = bs
            except ApiClientException:
                pass
            await asyncio.sleep(s.SETTINGS_UPDATE_DELAY)

    asyncio.create_task(refresh_settings())

def register_startup(dp: Dispatcher):
    dp.startup.register(on_startup)