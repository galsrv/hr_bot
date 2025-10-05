import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from core.log import logger
from config import settings as s


async def setup_webhook(bot: Bot, dispatcher: Dispatcher) -> None:
    '''Настраивает вебхуки и запускаем aiohttp-сервер. Используется только в проде.'''
    webhook_url = f'{s.BASE_WEBHOOK_URL}{s.WEBHOOK_PATH}'
    logger.info(f'🌍 Setting webhook to {webhook_url}')

    await bot.set_webhook(
        url=webhook_url,
        secret_token=s.WEBHOOK_SECRET,
        drop_pending_updates=True,
    )

    # Создаем приложение Aiohttp
    app = web.Application()
    app['bot'] = bot

    # Регистрируем хэндлер вебхуков и настраиваем диспетчер
    SimpleRequestHandler(dispatcher=dispatcher, bot=bot).register(app, path=s.WEBHOOK_PATH)
    setup_application(app, dispatcher, bot=bot)

    # Запускаем сервер
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=s.WEB_SERVER_HOST, port=s.WEB_SERVER_PORT)
    await site.start()

    logger.info(f'🚀 Webhook server started on {s.WEB_SERVER_HOST}:{s.WEB_SERVER_PORT}')
    logger.info(f'✅ Listening for updates at {webhook_url}')

    await asyncio.Event().wait()
