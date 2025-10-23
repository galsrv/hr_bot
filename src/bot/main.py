import asyncio

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import settings as s
from core.dispatcher import dispatcher
from core.log import logger
from core.middleware import register_middlewares
from core.startup import register_startup
from core.webhooks import setup_webhook


async def main() -> None:
    """Функция запуска бота в работу."""
    bot = Bot(token=s.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await bot.set_my_commands(s.COMMANDS)

    # Регистрируем middleware
    register_middlewares(dispatcher)

    # Регистрируем функцию для запуска на старте бота
    register_startup(dispatcher)

    if 1 == 0 and s.PROD_ENVIRONMENT:
        # В проде работаем через вебхуки (в теории)
        logger.info('⚙️  Running in PRODUCTION mode (Webhook enabled)')
        await setup_webhook(bot, dispatcher)
    else:
        # В деве/тесте работаем с пуллингом
        logger.info('⚙️  Running in DEVELOPMENT mode (Polling enabled)')
        await bot.delete_webhook(drop_pending_updates=True)
        await dispatcher.start_polling(
            bot,
            allowed_updates=s.ALLOWED_UPDATES,
        )


if __name__ == '__main__':
    asyncio.run(main())
