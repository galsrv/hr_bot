import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

dotenv_path = os.path.join(os.path.dirname(__file__), '../../infra/.env')
load_dotenv(dotenv_path)


class Settings(BaseSettings):
    '''Класс настроек приложения.'''

    PROD_ENVIRONMENT: bool = os.getenv('PROD', 'False').lower() in ('true', '1')
    APP_TITLE: str = 'HR Bot'
    HOST: str = '127.0.0.1'
    PORT: int = 8000
    DATABASE_URL: str = (
        f'postgresql+asyncpg://'
        f'{os.getenv('POSTGRES_USER')}:'
        f'{os.getenv('POSTGRES_PASSWORD')}@'
        f'{os.getenv('POSTGRES_DB_HOST')}:{os.getenv('POSTGRES_DB_PORT')}/'
        f'{os.getenv('POSTGRES_DB')}')
    TELEGRAM_API_URL: str = os.getenv('TELEGRAM_API_URL', '')
    TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', '')

settings = Settings()