from sqlalchemy import Boolean, String, text
from sqlalchemy.orm import Mapped, mapped_column

from bot_settings.constants import (
    SETTING_DESCRIPTION_MAX_LEN,
    SETTING_NAME_MAX_LEN,
    SETTING_VALUE_MAX_LEN,
)
from database import AppBaseClass


class BotSettingsOrm(AppBaseClass):
    """Модель таблицы BotSettings."""

    __tablename__ = 'setting'

    name: Mapped[str] = mapped_column(String(SETTING_NAME_MAX_LEN), nullable=False)
    value: Mapped[str] = mapped_column(
        String(SETTING_VALUE_MAX_LEN), nullable=True, server_default=text("''")
    )
    int_type: Mapped[bool] = mapped_column(Boolean, server_default=text('false'))
    description: Mapped[str] = mapped_column(
        String(SETTING_DESCRIPTION_MAX_LEN), nullable=True, server_default=text("''")
    )

    def to_dict(self) -> dict:
        """Используется для выгрузки в csv."""
        return {
            'name': self.name,
            'value': self.value,
            'int_type': self.int_type,
            'description': self.description,
        }
