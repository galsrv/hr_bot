import sys

from loguru import logger

logger.remove()

logger.add(
    sys.stderr,
    level='DEBUG',
)

logger.level('API_REQUEST', no=15, color='<magenta>')

logger.level('AUTH', no=15, color='<green>')
