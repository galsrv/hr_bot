from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import BotCallback, BotDir, BotSettings

start_router = Router(name=__name__)


@start_router.message(Command('start'))
async def command_start_handler(message: Message, bs: BotSettings) -> None:
    """Обработчик команды /start."""
    await message.answer(
        text=bs.INITIAL_GREETING,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=bs.INLINE_BUTTON_TEXT_MENU,
                        callback_data=BotCallback(action=BotDir.menu).pack(),
                    ),
                    InlineKeyboardButton(
                        text=bs.INLINE_BUTTON_TEXT_MESSAGE,
                        callback_data=BotCallback(action=BotDir.message).pack(),
                    ),
                ],
            ]
        ),
    )
