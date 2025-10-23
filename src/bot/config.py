import os
from enum import Enum

from aiogram.filters.callback_data import CallbackData
from aiogram.types import BotCommand
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

dotenv_path = os.path.join(os.path.dirname(__file__), '../../infra/.env')
load_dotenv(dotenv_path)


class BotDir(Enum):
    """Вспомогательный класс."""

    menu = 'menu'
    message = 'message'


class BotCallback(CallbackData, prefix='b'):
    """Вспомогательный класс для структурирования текстового обратного вызова."""

    action: BotDir
    item_id: int | None = None
    page: int | None = None


class Settings(BaseSettings):
    """Класс настроек приложения."""

    PROD_ENVIRONMENT: bool = os.getenv('HRBOT_PROD', 'False').lower() in ('true', '1')
    API_HOST: str = os.getenv('HRBOT_API_HOST')
    API_PORT: int = os.getenv('HRBOT_API_PORT')
    API_PREFIX: str = '/bot/api'
    TOKEN: str = os.getenv('HRBOT_TELEGRAM_BOT_TOKEN', '')

    # Бот обрабатывает только два типа реакций пользователя
    ALLOWED_UPDATES: list[str] = ['message', 'callback_query']

    # Команды, отображающиеся по кнопке Меню бота
    COMMANDS: list[BotCommand] = [
        BotCommand(command='/start', description='Начать сначала'),
        BotCommand(command='/menu', description='Справочник меню'),
        BotCommand(command='/message', description='Отправить сообщение'),
        BotCommand(command='/help', description='Помощь'),
    ]

    SETTINGS_UPDATE_DELAY: int = 10
    MESSAGE_MAX_LENGTH: int = 2048

    # Число попыток получить данные с бэкенда, интервал между попытками
    API_CONNECTION_ATTEMPTS: int = 3
    TIMEOUT: float = 0.3

    ERROR_CONNECTION_TO_BACKEND_API: str = 'Ошибка подключения. Повторите попытку позже'

    # Настройки для вебхуков
    WEBHOOK_SECRET: str = os.getenv('HRBOT_WEBHOOK_SECRET')
    WEB_SERVER_HOST: str = os.getenv('HRBOT_WEB_SERVER_HOST')
    WEB_SERVER_PORT: int = os.getenv('HRBOT_WEB_SERVER_PORT')
    WEBHOOK_PATH: str = os.getenv('HRBOT_WEBHOOK_PATH')
    BASE_WEBHOOK_URL: str = os.getenv('HRBOT_BASE_WEBHOOK_URL')


class BotSettings(Settings):
    """Класс настроек бота, значения загружаются с бэкенда."""

    INITIAL_GREETING: str
    MESSAGE_TO_REPLACE_ANOTHER: str
    ERROR_USER_NOT_FOUND: str
    INVITATION_TO_EXPLORE_THE_MENU: str
    INVITATION_TO_SEND_MESSAGE: str
    SUCCESS_MESSAGE_SENT: str
    ERROR_MESSAGE_TOO_LONG: str
    ERROR_MESSAGE_NOT_EXPECTED: str
    ERROR_MESSAGE_NOT_SENT: str
    OPERATION_CANCELLED: str
    HELP_BUTTON_TEXT: str
    INLINE_BUTTON_TEXT_MENU: str
    INLINE_BUTTON_TEXT_MESSAGE: str

    MENU_BUTTONS_PER_INLINE_ROW: int
    MENU_BUTTONS_PER_PAGE: int


settings = Settings()
