import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

dotenv_path = os.path.join(os.path.dirname(__file__), '../../infra/.env')
load_dotenv(dotenv_path)


class Settings(BaseSettings):
    '''Класс настроек приложения.'''

    PROD_ENVIRONMENT: bool = bool(os.getenv('PROD', 0))
    APP_TITLE: str = 'HR Bot'
    HOST: str = '127.0.0.1'
    PORT: int = 8000
    DATABASE_URL: str = (
        f'postgresql+asyncpg://'
        f'{os.getenv('POSTGRES_USER')}:'
        f'{os.getenv('POSTGRES_PASSWORD')}@'
        f'{os.getenv('POSTGRES_DB_HOST')}:{os.getenv('POSTGRES_DB_PORT')}/'
        f'{os.getenv('POSTGRES_DB')}')
    # LOGS_FILE_PATH: str = 'logs/{time:YYYY-MM-DD}.log'
    # LOGS_FORMAT: str = '[{level}] | {time:DD.MM.YYYY HH:mm:ss} {message}'
    # SECRET_KEY: str = os.getenv('SECRET_KEY', 'default_secret_key')
    # ACCESS_TOKEN_EXPIRES_DAYS: int = int(os.getenv('ACCESS_TOKEN_EXPIRES_DAYS', 30))
    # ALGORITHM: str = os.getenv('ALGORITHM', 'HS256')


settings = Settings()