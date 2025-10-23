from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.types.callback_query import CallbackQuery

from config import BotCallback, BotDir, BotSettings
from core.service import ApiClientException, api_client

message_router = Router(name=__name__)


@message_router.message(Command('message'))
async def command_message_handler(
    message: Message, state: FSMContext, bs: BotSettings
) -> None:
    """Обработчик команды /message."""
    await state.update_data(await_message=True)
    await message.answer(bs.INVITATION_TO_SEND_MESSAGE)


@message_router.message()
async def incoming_message_handler(
    message: Message, state: FSMContext, bs: BotSettings
) -> None:
    """Обработчик произвольного сообщения."""
    await_message: bool = await state.get_value('await_message')
    # Сообщение имеет смысл отправлять только когда бот его ожидает
    if await_message:
        if len(message.text) > bs.MESSAGE_MAX_LENGTH:
            await message.answer(bs.ERROR_MESSAGE_TOO_LONG)
        else:
            try:
                sent_flag: bool = await api_client.send_message(message.text, message.chat.id)
                if sent_flag:
                    await message.answer(bs.SUCCESS_MESSAGE_SENT)
                    await state.update_data(await_message=False)
                else:
                    await message.answer(bs.ERROR_MESSAGE_NOT_SENT)
            except ApiClientException:
                await message.answer(bs.ERROR_MESSAGE_NOT_SENT)
    else:
        await message.answer(bs.ERROR_MESSAGE_NOT_EXPECTED)


@message_router.callback_query(BotCallback.filter(F.action == BotDir.message))
async def handle_inline_button(
    callback: CallbackQuery, state: FSMContext, bs: BotSettings
) -> None:
    """Обработчик ответов на нажатия кнопок."""
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.edit_text(bs.MESSAGE_TO_REPLACE_ANOTHER)

    await command_message_handler(callback.message, state, bs)

    # Без этого вечно крутится анимация загрузки
    await callback.answer()
