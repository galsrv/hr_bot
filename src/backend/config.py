import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

dotenv_path = os.path.join(os.path.dirname(__file__), '../../infra/.env')
load_dotenv(dotenv_path)


class Settings(BaseSettings):
    """Класс настроек приложения."""

    PROD_ENVIRONMENT: bool = os.getenv('HRBOT_PROD', 'False').lower() in ('true', '1')
    APP_TITLE: str = 'HR Bot'
    HOST: str = os.getenv('HRBOT_BACKEND_HOST', '127.0.0.1')
    PORT: int = os.getenv('HRBOT_BACKEND_PORT', 8000)
    DATABASE_URL: str = (
        f'postgresql+asyncpg://'
        f'{os.getenv('HRBOT_POSTGRES_USER')}:'
        f'{os.getenv('HRBOT_POSTGRES_PASSWORD')}@'
        f'{os.getenv('HRBOT_POSTGRES_DB_HOST')}:{os.getenv('HRBOT_POSTGRES_DB_PORT')}/'
        f'{os.getenv('HRBOT_POSTGRES_DB')}'
    )
    TELEGRAM_API_URL: str = os.getenv('HRBOT_TELEGRAM_API_URL', '')
    TELEGRAM_BOT_TOKEN: str = os.getenv('HRBOT_TELEGRAM_BOT_TOKEN', '')

    FIXTURES_MENU_PATH: str = 'fixtures/menu.csv'
    FIXTURES_SETTINGS_PATH: str = 'fixtures/settings.csv'

    OPENAPI_URL: str = '/bot/api/openapi.json'
    DOCS_URL: str = '/bot/api/docs'
    REDOC_URL: str = '/bot/api/redoc'


settings = Settings()
