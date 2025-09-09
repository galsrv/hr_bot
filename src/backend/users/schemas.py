from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from users.constants import (
    USER_NAME_MIN_LENGTH,
    USER_NAME_MAX_LENGTH,
    USER_PASSWORD_MIN_LENGTH,
    USER_PASSWORD_MAX_LENGTH)
from users.utils import hash_password


class RoleReadSchema(BaseModel):
    id: int
    name: str

class UserBaseSchema(BaseModel):
    '''Базовый класс для создания и изменения пользователя'''
    password: str = Field(min_length=USER_PASSWORD_MIN_LENGTH,
                          max_length=USER_PASSWORD_MAX_LENGTH,
                          repr=False)
    role_id: int

    @field_serializer('password')
    def hashing_password(self, password: str):
        '''Хэшируем заданный пользоваетелем пароль.'''
        if password:
            return hash_password(password)

    model_config = ConfigDict(
        extra='forbid',
        )

class UserCreateSchema(UserBaseSchema):
    '''Класс создания пользователя'''
    username: str = Field(pattern=r'^[A-Za-z]+$',
                          min_length=USER_NAME_MIN_LENGTH,
                          max_length=USER_NAME_MAX_LENGTH)

class UserUpdateSchema(UserBaseSchema):
    '''Класс изменения пользователя'''
    password: Optional[str] = Field(default=None,
                                    min_length=USER_PASSWORD_MIN_LENGTH,
                                    max_length=USER_PASSWORD_MAX_LENGTH,
                                    repr=False)
    role_id: Optional[int] = None
    is_active: Optional[bool] = None

class UserReadSchema(BaseModel):
    '''Класс чтения отдельного пользователя'''
    id: int
    username: str
    role: RoleReadSchema
    is_active: bool
