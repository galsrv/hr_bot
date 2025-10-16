from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from menu.constants import MENU_ANSWER_MAX_LENGTH, MENU_BUTTON_TEXT_MAX_LENGTH
from users.schemas import UserRelationshipSchema


class MenuItemCreateSchema(BaseModel):
    """Схема создания элемента справочника."""

    button_text: str = Field(min_length=1, max_length=MENU_BUTTON_TEXT_MAX_LENGTH)
    answer: str = Field(min_length=1, max_length=MENU_ANSWER_MAX_LENGTH)
    created_by_id: int | None = None
    updated_by_id: int | None = None

    model_config = ConfigDict(from_attributes=True)


class MenuItemReadSchema(BaseModel):
    """Схема представления элемента справочника."""

    id: int
    button_text: str
    answer: str
    created_by: UserRelationshipSchema | None
    created_at: datetime
    updated_by: UserRelationshipSchema | None
    updated_at: datetime


class MenuItemUpdateSchema(BaseModel):
    """Схема изменения элемента справочника."""

    answer: str = Field(min_length=1, max_length=MENU_ANSWER_MAX_LENGTH)
    updated_by_id: int


class MenuUploadSchema(BaseModel):
    """Схема загрузки справочника из файла."""

    created_by_id: int
