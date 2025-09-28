import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import settings as s
from service import api_client

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    '''Обработчик команды /start.'''
    settings = await api_client.get_settings()
    await message.answer(str(settings))


@dp.message()
async def echo_handler(message: Message) -> None:
    '''
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    '''
    try:
        # Send a copy of the received message
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer('Nice try!')


async def main():
    bot = Bot(
        token=s.TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())