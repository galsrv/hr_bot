from sqlalchemy import Boolean, String, text
from sqlalchemy.orm import mapped_column, Mapped

from database import AppBaseClass
from bot_settings.constants import (SETTING_NAME_MAX_LEN,
                       SETTING_VALUE_MAX_LEN,
                       SETTING_DESCRIPTION_MAX_LEN)


class BotSettingsOrm(AppBaseClass):
    """Модель таблицы BotSettings."""
    __tablename__ = 'setting'

    name: Mapped[str] = mapped_column(
        String(SETTING_NAME_MAX_LEN),
        nullable=False)
    value: Mapped[str] = mapped_column(
        String(SETTING_VALUE_MAX_LEN),
        nullable=True,
        server_default=text("''"))
    int_type: Mapped[bool] = mapped_column(
        Boolean,
        server_default=text('false'))
    description: Mapped[str] = mapped_column(
        String(SETTING_DESCRIPTION_MAX_LEN),
        nullable=True,
        server_default=text("''"))
