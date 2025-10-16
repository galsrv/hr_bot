from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field

from pages.users.constants import (
    USERNAME_REGEXP,
    USER_NAME_MAX_LENGTH,
    USER_NAME_MIN_LENGTH,
    USER_PASSWORD_MAX_LENGTH,
    USER_PASSWORD_MIN_LENGTH,
)


class CustomDateFormat:
    """Своего рода Миксин для переиспользования."""

    @computed_field
    def created_at_str(self) -> str | None:
        """Кастомный формат даты."""
        if hasattr(self, 'created_at'):
            return self.created_at.strftime('%d-%m-%Y %H:%M:%S')
        return None

    @computed_field
    def updated_at_str(self) -> str | None:
        """Кастомный формат даты."""
        if hasattr(self, 'updated_at'):
            return self.updated_at.strftime('%d-%m-%Y %H:%M:%S')
        return None


class RoleReadSchema(BaseModel):
    """Модель роли."""

    id: int
    name: str
    can_edit_settings: bool
    can_edit_users: bool
    can_send_messages: bool
    can_edit_menu: bool


class UserRelationshipSchema(BaseModel):
    """Класс пользователя для сериализации внутри ссылки."""

    id: int
    username: str


class UserReadSchema(BaseModel, CustomDateFormat):
    """Модель пользователя."""

    id: int
    username: str
    is_active: bool
    role: RoleReadSchema
    created_at: datetime
    updated_at: datetime
    created_by: UserRelationshipSchema | None = None
    updated_by: UserRelationshipSchema | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )


class UsersListPageSchema(BaseModel):
    """Модель страницы со списком пользователей."""

    items: list[UserReadSchema]
    total: int
    page: int
    pages: int


class UserCreateSchema(BaseModel):
    """Класс создания пользователя."""

    username: str = Field(
        pattern=USERNAME_REGEXP,
        min_length=USER_NAME_MIN_LENGTH,
        max_length=USER_NAME_MAX_LENGTH,
    )
    password: str = Field(
        min_length=USER_PASSWORD_MIN_LENGTH,
        max_length=USER_PASSWORD_MAX_LENGTH,
        repr=False,
    )
    role_id: int
    is_active: Optional[bool] = True
    created_by_id: int
    updated_by_id: Optional[int] = None


class UserUpdateSchema(BaseModel):
    """Класс изменения пользователя."""

    id: int
    password: Optional[str] = Field(
        default=None,
        min_length=USER_PASSWORD_MIN_LENGTH,
        max_length=USER_PASSWORD_MAX_LENGTH,
        repr=False,
    )
    role_id: Optional[int] = None
    is_active: Optional[bool] = None
    updated_by_id: int


class UserLoginSchema(BaseModel):
    """Класс логина пользователя."""

    username: str = Field(min_length=1)
    password: str = Field(min_length=1)
