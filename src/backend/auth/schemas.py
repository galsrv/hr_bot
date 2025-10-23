from pydantic import BaseModel, ConfigDict


class SessionInSchema(BaseModel):
    """Класс получения номера сессии на вход."""

    id: str

    model_config = ConfigDict(extra='ignore')


class SessionReadSchema(BaseModel):
    """Класс чтения сессии."""

    id: str
    user_id: int


class SessionCreateSchema(BaseModel):
    """Класс создания сессии."""

    user_id: int

    model_config = ConfigDict(extra='ignore')
