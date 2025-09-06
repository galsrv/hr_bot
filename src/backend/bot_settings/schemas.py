from pydantic import BaseModel, ConfigDict, field_serializer, model_validator
from typing import List

from bot_settings.constants import SETTING_VALUE_MAX_LEN


class SettingsRead(BaseModel):
    '''Класс чтения записи таблицы Settings.'''
    id: int
    name: str
    value: str
    description: str
    int_type: bool

    @field_serializer('value')
    def serialize_value(self, value: str):
        '''Преобразовываем тип для части значений.'''
        return value if not self.int_type else int(value)

class SettingsList(BaseModel):
    '''Класс чтения записей таблицы Settings.'''
    data: List[SettingsRead]

class SettingsChange(BaseModel):
    '''Класс изменения записи таблицы Settings.'''
    value: str

    model_config = ConfigDict(
        extra='forbid',
        )

class SettingsChangeValidated(SettingsChange):
    int_type: bool

    @model_validator(mode='after')
    def value_validator(self) -> 'SettingsChangeValidated':
        '''Валидируем значение поля value.'''
        if not 0 < len(self.value) < SETTING_VALUE_MAX_LEN:
            raise ValueError('Допустимая длина значения - от 1 до 255 символов')

        if self.int_type:
            try:
                int(self.value)
            except ValueError:
                raise ValueError('Значение должно быть целым числом')
            if not (1 < int(self.value) < 10):
                raise ValueError('Значение должно быть не менее 1 и не более 10')

        return self