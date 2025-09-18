from pydantic import BaseModel

class RoleReadSchema(BaseModel):
    '''Модель роли.'''
    id: int
    name: str
    can_edit_settings: bool
    can_edit_users: bool
    can_send_messages: bool
    can_edit_menu: bool

class UserReadSchema(BaseModel):
    '''Модель пользователя.'''
    id: int
    username: str
    is_active: bool
    role: RoleReadSchema

class UsersListPageSchema(BaseModel):
    '''Модель страницы со списком пользователей.'''
    items: list[UserReadSchema]
    total: int
    page: int
    pages: int
