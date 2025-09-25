from datetime import datetime
from pydantic import BaseModel, Field

from users.schemas import UserRelationshipSchema

class EmployeeCreareSchema(BaseModel):
    id: int = Field(gt=0)
    name: str | None

class EmployeeReadSchema(BaseModel):
    id: int
    name: str | None
    is_banned: bool
    created_at: datetime
    updated_at: datetime
    updated_by_id: int | None

class EmployeeChangeSchema(BaseModel):
    is_banned: bool
    updated_by_id: int

class MessageCreateSchema(BaseModel):
    employee_id: int
    text: str
    manager_id: int
    is_read: bool | None = False

class MessageReadSchema(BaseModel):
    id: int
    employee_id: int
    text: str
    manager: UserRelationshipSchema | None
    created_at: datetime
    is_read: bool

class EmployeeChatSchema(EmployeeReadSchema):
    messages: list[MessageReadSchema]

