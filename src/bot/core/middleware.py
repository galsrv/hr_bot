from typing import Any, Awaitable, Callable, Dict

from aiogram import Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import CallbackQuery, Chat, Message
from aiogram.types.update import Update

from config import BotSettings
from config import settings as s
from core.dispatcher import dispatcher
from core.service import ApiClientException, api_client


def _extract_object_from_update(update: Update) -> tuple[Message | CallbackQuery, Chat]:
    """Вытаскиваем объект из атрибута Update, чат спрятан на разном уровне."""
    if update.message:
        return update.message, update.message.chat
    if update.callback_query:
        return update.callback_query, update.callback_query.message.chat
    return None


async def settings_dependency_middleware(
    handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
    event: Update,
    data: Dict[str, Any],
) -> Any:
    """Создаем зависимость с настройками."""
    # dispatcher: Dispatcher = data['dispatcher']

    try:
        bs: BotSettings = dispatcher.workflow_data['settings']
    except KeyError:
        event_object, _ = _extract_object_from_update(event)
        event_object: Message | CallbackQuery
        await event_object.answer(s.ERROR_CONNECTION_TO_BACKEND_API)
        return None

    # Вставляем в контект хендлеров под именем bs
    data['bs'] = bs

    return await handler(event, data)


async def await_message_state_middleware(
    handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
    event: Update,
    data: Dict[str, Any],
) -> Any:
    """Устанавливаем состояние ожидания сообщения."""
    bot = data['bot']
    # dispatcher: Dispatcher = data['dispatcher']

    event_object, chat = _extract_object_from_update(event)
    event_object: Message | CallbackQuery
    chat: Chat

    if not event_object.from_user or not chat:
        return await handler(event, data)

    # Вручную формируем контекст
    state = FSMContext(
        storage=dispatcher.storage,
        key=StorageKey(bot.id, event_object.from_user.id, chat.id),
    )

    # Если апдейт = не обычное сообщение, то меняем статус ожидания сообщения
    if not isinstance(event_object, Message) or event_object.text.startswith('/'):
        await state.update_data(await_message=False)

    # Делаем состояние доступным для хэндлеров
    data['state'] = state

    return await handler(event, data)


async def employee_check_middleware(
    handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
    event: Update,
    data: Dict[str, Any],
) -> Any:
    """Создаем пользователя либо проверяем статус существующего."""
    bs: BotSettings = data['bs']

    event_object, _ = _extract_object_from_update(event)
    event_object: Message | CallbackQuery

    if event_object.from_user is not None:
        try:
            employee: dict | None = await api_client.get_or_create_employee(
                event_object.from_user.id, event_object.from_user.full_name
            )
        except ApiClientException:
            await event_object.answer(bs.ERROR_CONNECTION_TO_BACKEND_API)
            return None

    if not employee:
        await event_object.answer(bs.ERROR_USER_NOT_FOUND)
        return None

    return await handler(event, data)


def register_middlewares(dp: Dispatcher) -> None:
    """Регистрируем middleware бота."""
    dp.update.outer_middleware(settings_dependency_middleware)
    dp.update.outer_middleware(employee_check_middleware)
    dp.update.outer_middleware(await_message_state_middleware)
