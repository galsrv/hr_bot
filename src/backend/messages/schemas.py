from datetime import datetime

from fastapi_pagination import Page
from pydantic import BaseModel, ConfigDict, Field

from messages.constants import MESSAGE_TEXT_MAX_LENGTH
from users.schemas import UserRelationshipSchema


class EmployeeCreareSchema(BaseModel):
    """Класс создания нового сотрудника."""
    id: int = Field(gt=0)
    name: str | None


class EmployeeReadSchema(BaseModel):
    """Класс представления данных сотрудника."""
    id: int
    name: str | None
    is_banned: bool
    created_at: datetime
    updated_at: datetime
    updated_by_id: int | None

    model_config = ConfigDict(from_attributes=True)


class EmployeeChangeSchema(BaseModel):
    """Класс изменения данных сотрудника."""
    is_banned: bool
    updated_by_id: int


class MessageCreateSchema(BaseModel):
    """Класс создания сообщения."""
    employee_id: int
    text: str = Field(min_length=1, max_length=MESSAGE_TEXT_MAX_LENGTH)
    manager_id: int | None = None
    is_read: bool | None = False


class MessageReadSchema(BaseModel):
    """Класс представления сообщения."""
    id: int
    employee_id: int
    text: str
    manager: UserRelationshipSchema | None
    created_at: datetime
    is_read: bool

    model_config = ConfigDict(
        from_attributes=True,
    )


class EmployeeChatSchema(EmployeeReadSchema):
    """Класс чата с сотрудником."""
    messages: Page[MessageReadSchema]

    model_config = ConfigDict(from_attributes=True)


class EmployeeChatListSchema(BaseModel):
    """Класс списка чатов с сотрудниками."""
    id: int
    name: str | None
    is_banned: bool
    unread_count: int
    last_message_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
