from sqlalchemy import Boolean, Column, String, text

from database import AppBaseClass
from bot_settings.constants import (SETTING_NAME_MAX_LEN,
                       SETTING_VALUE_MAX_LEN,
                       SETTING_DESCRIPTION_MAX_LEN)


class BotSettings(AppBaseClass):
    """Модель таблицы BotSettings."""

    name = Column(
        String(SETTING_NAME_MAX_LEN),
        nullable=False)
    value = Column(
        String(SETTING_VALUE_MAX_LEN),
        nullable=True,
        server_default=text("''"))
    int_type = Column(
        Boolean,
        server_default=text('false'))
    description = Column(
        String(SETTING_DESCRIPTION_MAX_LEN),
        nullable=True,
        server_default=text("''"))
