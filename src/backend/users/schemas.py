from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from users.constants import (
    USERNAME_REGEXP,
    USER_NAME_MAX_LENGTH,
    USER_NAME_MIN_LENGTH,
    USER_PASSWORD_MAX_LENGTH,
    USER_PASSWORD_MIN_LENGTH,
)
from users.utils import hash_password


class RoleCreateSchema(BaseModel):
    """Класс создания роли."""
    name: str
    can_edit_settings: bool
    can_edit_users: bool
    can_send_messages: bool
    can_edit_menu: bool


class RoleReadSchema(BaseModel):
    """Класс чтения роли."""
    id: int
    name: str
    can_edit_settings: bool
    can_edit_users: bool
    can_send_messages: bool
    can_edit_menu: bool


class UserBaseSchema(BaseModel):
    """Базовый класс для создания и изменения пользователя."""

    @field_serializer('password', check_fields=False)
    def hashing_password(self, password: str) -> str | None:
        """Хэшируем заданный пользователем пароль."""
        if password:
            return hash_password(password)
        return None

    model_config = ConfigDict(extra='ignore')


class UserCreateSchema(UserBaseSchema):
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
    created_by_id: Optional[int] = None
    updated_by_id: Optional[int] = None


class UserUpdateSchema(UserBaseSchema):
    """Класс изменения пользователя."""

    password: Optional[str] = Field(
        default=None,
        min_length=USER_PASSWORD_MIN_LENGTH,
        max_length=USER_PASSWORD_MAX_LENGTH,
        repr=False,
    )
    role_id: Optional[int] = None
    is_active: Optional[bool] = None
    updated_by_id: int


class UserRelationshipSchema(BaseModel):
    """Класс пользователя для сериализации внутри ссылки."""

    id: int
    username: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserReadSchema(BaseModel):
    """Класс  пользователя."""

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
        # json_encoders={datetime: lambda v: v.strftime("%d-%m-%Y %H:%M:%S")}
    )


class UserLoginSchema(BaseModel):
    """Класс логина пользователя."""

    username: str
    password: str

    model_config = ConfigDict(extra='ignore')
