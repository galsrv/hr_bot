from pydantic import BaseModel
from typing import List


class SettingsRead(BaseModel):
    """Класс чтения записи таблицы Settings."""
    id: int
    name: str
    value: str
    int_type: bool


class SettingsList(BaseModel):
    """Класс чтения записей таблицы Settings."""
    data: List[SettingsRead]
