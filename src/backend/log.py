import sys

from loguru import logger

logger.remove()

logger.add(
    sys.stderr,
    level='DEBUG',
)

logger.level(
    'DB_ACCESS',
    no=15,
    color='<yellow>')
