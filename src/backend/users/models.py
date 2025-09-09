from datetime import datetime

from sqlalchemy import Boolean, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql import func, text

from database import AppBaseClass
from users.constants import (USER_NAME_MAX_LENGTH,
                            USER_PASSWORD_MAX_LENGTH)


class RolesOrm(AppBaseClass):
    """Модель таблицы пользователей."""
    __tablename__ = 'auth_role'

    name: Mapped[str] = mapped_column(String(USER_NAME_MAX_LENGTH), nullable=False, unique=True)

    user: Mapped[list['UsersOrm']] = relationship(
        'UsersOrm',
        back_populates='role')
        # lazy='selectin')

    __order_by__ = (name.asc(), )

class UsersOrm(AppBaseClass):
    """Модель таблицы пользователей."""
    __tablename__ = 'auth_user'
    
    username: Mapped[str] = mapped_column(String(USER_NAME_MAX_LENGTH), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(USER_PASSWORD_MAX_LENGTH), nullable=False)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey('auth_role.id', ondelete='CASCADE'), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text('true'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), server_onupdate=func.now(), nullable=False)

    role: Mapped[RolesOrm] = relationship(
        'RolesOrm',
        back_populates='user',
        lazy='joined')

    __order_by__ = (username.asc(), )