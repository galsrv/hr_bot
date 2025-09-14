from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from users.constants import (
    USER_NAME_MIN_LENGTH,
    USER_NAME_MAX_LENGTH,
    USER_PASSWORD_MIN_LENGTH,
    USER_PASSWORD_MAX_LENGTH,
    USERNAME_REGEXP)
from users.utils import hash_password, create_random_session_string


class RoleReadSchema(BaseModel):
    '''Класс чтения роли.'''
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
        '''Хэшируем заданный пользователем пароль.'''
        if password:
            return hash_password(password)

    model_config = ConfigDict(extra='ignore')

class UserCreateSchema(UserBaseSchema):
    '''Класс создания пользователя.'''
    username: str = Field(pattern=USERNAME_REGEXP,
                          min_length=USER_NAME_MIN_LENGTH,
                          max_length=USER_NAME_MAX_LENGTH)
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
    role_id: int
    role_name: str
    is_active: bool

class UserLoginSchema(BaseModel):
    '''Класс чтения пользователя.'''
    username: str
    password: str

    model_config = ConfigDict(extra='ignore')

class SessionReadSchema(BaseModel):
    '''Класс чтения сессии.'''
    id: int
    session_id: str
    user_id: int

class SessionCreateSchema(BaseModel):
    '''Класс создания сессии.'''
    user_id: int
    session_id: str

    model_config = ConfigDict(
        extra='ignore')

    @field_serializer('session_id')
    def session_id_generation(self, session_id):
        '''Генерируем id сессии.'''
        return create_random_session_string()
