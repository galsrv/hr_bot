from datetime import datetime
from fastapi_pagination import Page
from pydantic import BaseModel, ConfigDict, Field

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

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: lambda v: v.strftime("%d-%m-%Y %H:%M:%S")}
    )

class EmployeeChangeSchema(BaseModel):
    is_banned: bool
    updated_by_id: int

class MessageCreateSchema(BaseModel):
    employee_id: int
    text: str
    manager_id: int | None
    is_read: bool | None = False

class MessageReadSchema(BaseModel):
    id: int
    employee_id: int
    text: str
    manager: UserRelationshipSchema | None
    created_at: datetime
    is_read: bool

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: lambda v: v.strftime("%d-%m-%Y %H:%M:%S")}
    )

class EmployeeChatSchema(EmployeeReadSchema):
    messages: Page[MessageReadSchema]

    model_config = ConfigDict(
        from_attributes=True
    )