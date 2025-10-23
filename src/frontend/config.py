import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

dotenv_path = os.path.join(os.path.dirname(__file__), '../../infra/.env')
load_dotenv(dotenv_path)


class Settings(BaseSettings):
    """Класс настроек приложения."""

    PROD_ENVIRONMENT: bool = os.getenv('HRBOT_PROD', 'False').lower() in ('true', '1')
    APP_TITLE: str = 'HR Bot Admin Panel'
    HOST: str = os.getenv('HRBOT_NICEGUI_HOST', '127.0.0.1')
    PORT: int = os.getenv('HRBOT_NICEGUI_PORT', '5005')
    API_HOST: str = os.getenv('HRBOT_API_HOST', '127.0.0.1')
    API_PORT: str = os.getenv('HRBOT_API_PORT', '8000')
    SECRET_KEY: str = os.getenv('HRBOT_NICEGUI_SECRET_KEY', 'default_secret_key')
    USERS_PER_PAGE: int = 3

    DATETIME_FORMAT: str = '%d.%m.%Y %H:%M:%S'

    API_URL_PREFIX: str = '/bot/api'
    URL_PREFIX: str = ''  # вынес '/bot/admin' в настройки nginx
    API_URL: str = f'{API_HOST}:{API_PORT}{API_URL_PREFIX}'


settings = Settings()
