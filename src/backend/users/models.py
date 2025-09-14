from datetime import datetime

from sqlalchemy import Boolean, Index, Integer, ForeignKey, String, DateTime, func
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql import text

from database import AppBaseClass
from users.constants import (
    USER_NAME_MAX_LENGTH,
    USER_PASSWORD_MAX_LENGTH,
    SESSION_DURATION_IN_DAYS,
    SESSION_ID_LENGTH
)


class RolesOrm(AppBaseClass):
    """Модель таблицы пользователей."""
    __tablename__ = 'auth_role'

    name: Mapped[str] = mapped_column(String(USER_NAME_MAX_LENGTH), nullable=False, unique=True)

    user: Mapped[list['UsersOrm']] = relationship(
        'UsersOrm',
        back_populates='role')

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

    session: Mapped['SessionsOrm'] = relationship(
        'SessionsOrm',
        back_populates='user')

    @property
    def role_name(self) -> str:
        return self.role.name if self.role else None

    __order_by__ = (func.lower(username).asc(), )

class SessionsOrm(AppBaseClass):
    """Модель таблицы пользовательских сессий."""
    __tablename__ = 'auth_session'
    
    session_id: Mapped[str] = mapped_column(String(SESSION_ID_LENGTH), nullable=False, unique=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(UsersOrm.id, ondelete='CASCADE'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    expired_at: Mapped[datetime] = mapped_column(DateTime, server_default=text(f"(NOW() + interval '{SESSION_DURATION_IN_DAYS} days')"), nullable=False)

    user: Mapped[UsersOrm] = relationship(
        UsersOrm,
        back_populates='session',
        lazy='joined')

    # Иначе Alembic не видит этого индекса
    __table_args__ = (Index('ix_auth_session_session_id', 'session_id'), )