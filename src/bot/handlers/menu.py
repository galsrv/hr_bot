from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.types.callback_query import CallbackQuery

from config import BotCallback, BotDir, BotSettings
from core.service import ApiClientException, api_client

menu_router = Router(name=__name__)


async def _menu_inline_keyboard_builder(
    message: Message, bs: BotSettings, page: int = 1
) -> list:
    """Собираем элементы экранной клавиатуры."""
    if page is None:
        page = 1

    try:
        menu_page: dict = await api_client.get_menu_page(
            page=page, size=bs.MENU_BUTTONS_PER_PAGE
        )
    except ApiClientException:
        await message.answer(bs.ERROR_CONNECTION_TO_BACKEND_API)
        return None

    inline_keyboard = []

    for i in range(len(menu_page['items'])):
        if i % bs.MENU_BUTTONS_PER_INLINE_ROW == 0:
            inline_keyboard.append([])

        menu_item = menu_page['items'][i]

        inline_keyboard[-1].append(
            InlineKeyboardButton(
                text=menu_item['button_text'],
                callback_data=BotCallback(
                    action=BotDir.menu, item_id=menu_item['id']
                ).pack(),
            )
        )

    # Если страниц больше одной
    if menu_page['pages'] > 1:
        inline_keyboard.append([])
        # Если текущая страница - не первая
        if menu_page['page'] > 1:
            inline_keyboard[-1].append(
                InlineKeyboardButton(
                    text='⬅️',
                    callback_data=BotCallback(
                        action=BotDir.menu, page=menu_page['page'] - 1
                    ).pack(),
                )
            )
        # Если текущая страница - не последняя
        if menu_page['page'] < menu_page['pages']:
            inline_keyboard[-1].append(
                InlineKeyboardButton(
                    text='➡️',
                    callback_data=BotCallback(
                        action=BotDir.menu, page=menu_page['page'] + 1
                    ).pack(),
                )
            )

    return inline_keyboard


@menu_router.message(Command('menu'))
async def command_menu_handler(
    message: Message, bs: BotSettings, page: int = 1
) -> None:
    """Обработчик команды /menu."""
    inline_keyboard = await _menu_inline_keyboard_builder(message, bs, page)
    if inline_keyboard:
        await message.answer(
            text=bs.INVITATION_TO_EXPLORE_THE_MENU,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_keyboard),
        )


async def _print_menu_item(
    message: Message, menu_item_id: int, bs: BotSettings
) -> None:
    """Выдаем ответ на выбранный пользователем элемент справочника."""
    try:
        item: dict = await api_client.get_menu_item(menu_item_id)
        if item:
            await message.answer(item['answer'])
    except ApiClientException:
        await message.answer(bs.ERROR_CONNECTION_TO_BACKEND_API)
        return


@menu_router.callback_query(BotCallback.filter(F.action == BotDir.menu))
async def handle_menu_callbacks(
    callback: CallbackQuery, callback_data: BotCallback, bs: BotSettings
) -> None:
    """Обработчик обратных вызовов опций меню."""
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.edit_text('Ответ получен 👍')

    # Выводим либо другую страницу справочника, либ ответ на выбранный раздел
    if callback_data.item_id is not None:
        await _print_menu_item(callback.message, callback_data.item_id, bs)
    else:
        await command_menu_handler(callback.message, bs, callback_data.page)

    # Без этого вечно крутится анимация загрузки
    await callback.answer()
