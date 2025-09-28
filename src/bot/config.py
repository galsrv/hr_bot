import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

dotenv_path = os.path.join(os.path.dirname(__file__), '../../infra/.env')
load_dotenv(dotenv_path)


class Settings(BaseSettings):
    '''Класс настроек приложения.'''

    PROD_ENVIRONMENT: bool = os.getenv('PROD', 'False').lower() in ('true', '1')
    # APP_TITLE: str = 'HR Bot'
    # HOST: str = '127.0.0.1'
    # PORT: int = 8000
    # TELEGRAM_API_URL: str = os.getenv('TELEGRAM_API_URL', '')
    API_HOST: str = os.getenv('API_HOST')
    API_PORT: int = os.getenv('API_PORT')
    TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', '')

settings = Settings()