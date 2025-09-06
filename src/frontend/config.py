import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

dotenv_path = os.path.join(os.path.dirname(__file__), '../../infra/.env')
load_dotenv(dotenv_path)


class Settings(BaseSettings):
    '''Класс настроек приложения.'''

    PROD_ENVIRONMENT: bool = os.getenv('PROD', 'False').lower() in ('true', '1')
    APP_TITLE: str = 'HR Bot Admin Panel'
    HOST: str = '127.0.0.1'
    PORT: int = 5000
    API_HOST: str = os.getenv('API_HOST', '127.0.0.1')
    API_PORT: str = os.getenv('API_PORT', '8000')
    API_URL: str = f'{API_HOST}:{API_PORT}/api'
    # LOGS_FILE_PATH: str = 'logs/{time:YYYY-MM-DD}.log'
    # LOGS_FORMAT: str = '[{level}] | {time:DD.MM.YYYY HH:mm:ss} {message}'
    # SECRET_KEY: str = os.getenv('SECRET_KEY', 'default_secret_key')
    # ACCESS_TOKEN_EXPIRES_DAYS: int = int(os.getenv('ACCESS_TOKEN_EXPIRES_DAYS', 30))
    # ALGORITHM: str = os.getenv('ALGORITHM', 'HS256')


settings = Settings()