from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from users.constants import (
    USER_NAME_MIN_LENGTH,
    USER_NAME_MAX_LENGTH,
    USER_PASSWORD_MIN_LENGTH,
    USER_PASSWORD_MAX_LENGTH,
    USERNAME_REGEXP)
from users.utils import hash_password


class RoleReadSchema(BaseModel):
    '''Класс чтения роли.'''
    id: int
    name: str
    can_edit_settings: bool
    can_edit_users: bool
    can_send_messages: bool
    can_edit_menu: bool

class UserBaseSchema(BaseModel):
    '''Базовый класс для создания и изменения пользователя'''

    @field_serializer('password', check_fields=False)
    def hashing_password(self, password: str):
        '''Хэшируем заданный пользователем пароль.'''
        if password:
            return hash_password(password)

    model_config = ConfigDict(extra='ignore')

class UserCreateSchema(UserBaseSchema):
    '''Класс создания пользователя.'''
    username: str = Field(pattern=USERNAME_REGEXP,
                          min_length=USER_NAME_MIN_LENGTH,
                          max_length=USER_NAME_MAX_LENGTH)
    password: str = Field(min_length=USER_PASSWORD_MIN_LENGTH,
                          max_length=USER_PASSWORD_MAX_LENGTH,
                          repr=False)
    role_id: int
    is_active: Optional[bool] = True

class UserUpdateSchema(UserBaseSchema):
    '''Класс изменения пользователя.'''
    password: Optional[str] = Field(default=None,
                                    min_length=USER_PASSWORD_MIN_LENGTH,
                                    max_length=USER_PASSWORD_MAX_LENGTH,
                                    repr=False)
    role_id: Optional[int] = None
    is_active: Optional[bool] = None

class UserReadSchema(BaseModel):
    '''Класс чтения пользователя.'''
    id: int
    username: str
    is_active: bool
    role: RoleReadSchema

class UserLoginSchema(BaseModel):
    '''Класс чтения пользователя.'''
    username: str
    password: str

    model_config = ConfigDict(extra='ignore')


