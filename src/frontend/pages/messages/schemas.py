from datetime import datetime

from pydantic import BaseModel, ConfigDict, computed_field

from config import settings as s
from pages.users.schemas import UserRelationshipSchema


class CustomDateFormat:
    """Своего рода Миксин для переиспользования."""

    @computed_field
    def created_at_str(self) -> str | None:
        """Кастомный формат даты."""
        if hasattr(self, 'created_at'):
            return self.created_at.strftime(s.DATETIME_FORMAT)
        return None

    @computed_field
    def updated_at_str(self) -> str | None:
        """Кастомный формат даты."""
        if hasattr(self, 'updated_at'):
            return self.updated_at.strftime(s.DATETIME_FORMAT)
        return None


class EmployeeChatListSchema(BaseModel):
    """Модель представления списка чатов."""
    id: int
    name: str | None
    is_banned: bool
    unread_count: int
    last_message_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class EmployeeReadSchema(BaseModel, CustomDateFormat):
    """Модель представления сотрудника."""
    id: int
    name: str | None
    is_banned: bool
    created_at: datetime
    updated_at: datetime
    updated_by_id: int | None

    model_config = ConfigDict(
        from_attributes=True,
    )


class MessageReadSchema(BaseModel, CustomDateFormat):
    """Модель представления сообщения."""
    id: int
    employee_id: int
    text: str
    manager: UserRelationshipSchema | None
    created_at: datetime
    is_read: bool

    model_config = ConfigDict(
        from_attributes=True,
    )


class Page(BaseModel):
    """Вручную собранная модель fastapi-pagination."""

    items: list[MessageReadSchema]
    total: int
    page: int
    size: int
    pages: int

    model_config = ConfigDict(
        from_attributes=True,
    )


class EmployeeChatSchema(EmployeeReadSchema):
    """Модель чата со страницей с сообщениями."""
    messages: Page
