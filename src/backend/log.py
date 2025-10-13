import logging
import sys
from enum import Enum

from loguru import logger


class AnsiColor(str, Enum):
    """Часто используемые цвета."""
    RESET = '\033[0m'
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'


# Конфигурируем логгер Loguru
logger.remove()

logger.add(
    sys.stderr,
    level='DEBUG',
    format='<green>{time:YYYY-MM-DD HH:mm:ss}</> | <yellow>{level}</> | <cyan>{name}:{function}</> | {message}',
)

logger.level('DB_ACCESS', no=15, color='<yellow>')


# Конфигурируем логгер для SQLAlchemy
sql_logger = logging.getLogger('sqlalchemy.engine.Engine')
sql_logger.setLevel(logging.INFO)
sql_logger.propagate = False

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    f'{AnsiColor.GREEN.value}%(asctime)s {AnsiColor.WHITE.value}| {AnsiColor.YELLOW.value}%(levelname)s {AnsiColor.WHITE.value}| {AnsiColor.CYAN.value}%(filename)s {AnsiColor.RESET.value}| {AnsiColor.WHITE.value}%(message)s',
    '%Y-%m-%d %H:%M:%S',
)
handler.setFormatter(formatter)

sql_logger.handlers.clear()
sql_logger.addHandler(handler)
