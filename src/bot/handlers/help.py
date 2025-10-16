from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import BotSettings

help_router = Router(name=__name__)


@help_router.message(Command('help'))
async def command_help_handler(message: Message, bs: BotSettings) -> None:
    """Обработчик команды /help."""
    await message.answer(bs.HELP_BUTTON_TEXT)
