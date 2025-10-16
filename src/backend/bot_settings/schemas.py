from pydantic import BaseModel, ConfigDict, Field, field_serializer

from bot_settings.constants import SETTING_VALUE_MAX_LEN


class SettingsReadSchema(BaseModel):
    """Класс чтения записи таблицы Settings."""

    id: int
    name: str
    value: str
    description: str
    int_type: bool

    @field_serializer('value')
    def serialize_value(self, value: str):
        """Преобразовываем тип для части значений."""
        return value if not self.int_type else int(value)


class SettingsChangeSchema(BaseModel):
    """Класс изменения записи таблицы Settings."""

    value: str = Field(min_length=1, max_length=SETTING_VALUE_MAX_LEN)

    model_config = ConfigDict(
        extra='ignore',
    )


class SettingCreateSchema(BaseModel):
    """Класс создания записи таблицы Settings."""

    name: str
    value: str
    description: str
    int_type: bool
