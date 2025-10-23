from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import text

from database import AppBaseClass
from users.constants import (
    USER_NAME_MAX_LENGTH,
    USER_PASSWORD_MAX_LENGTH,
)


class RolesOrm(AppBaseClass):
    """Модель таблицы ролей."""

    __tablename__ = 'auth_role'

    name: Mapped[str] = mapped_column(
        String(USER_NAME_MAX_LENGTH), nullable=False, unique=True
    )
    can_edit_settings = mapped_column(
        Boolean, default=False, server_default=text('false'), nullable=False
    )
    can_edit_users = mapped_column(
        Boolean, default=False, server_default=text('false'), nullable=False
    )
    can_send_messages = mapped_column(
        Boolean, default=False, server_default=text('false'), nullable=False
    )
    can_edit_menu = mapped_column(
        Boolean, default=False, server_default=text('false'), nullable=False
    )

    user: Mapped[list['UsersOrm']] = relationship('UsersOrm', back_populates='role')

    __order_by__ = (name.asc(),)


class UsersOrm(AppBaseClass):
    """Модель таблицы пользователей."""

    __tablename__ = 'auth_user'

    username: Mapped[str] = mapped_column(
        String(USER_NAME_MAX_LENGTH), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(
        String(USER_PASSWORD_MAX_LENGTH), nullable=False)
    role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('auth_role.id', ondelete='CASCADE'), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default=text('true'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('auth_user.id', ondelete='SET NULL'), nullable=True)
    updated_by_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('auth_user.id', ondelete='SET NULL'), nullable=True)

    role: Mapped[RolesOrm] = relationship(
        'RolesOrm', back_populates='user', lazy='joined')

    session: Mapped['SessionsOrm'] = relationship(  # noqa: F821 # pyright: ignore[reportUndefinedVariable]
        'SessionsOrm', back_populates='user')

    created_by: Mapped['UsersOrm'] = relationship(
        'UsersOrm',
        foreign_keys=[
            created_by_id,
        ],
        lazy='joined',
        # Если не ограничить глубину, можно запустить бескочненый цикл жадной загрузки
        join_depth=1,
        # Черная магия, но иначе отношение будет работать в обе стороны
        # Без лямбды UsersOrm не определено к этому моменту
        remote_side=lambda: [UsersOrm.id],
    )

    updated_by: Mapped['UsersOrm'] = relationship(
        'UsersOrm',
        foreign_keys=[
            updated_by_id,
        ],
        lazy='joined',
        join_depth=1,
        remote_side=lambda: [UsersOrm.id],
    )

    __order_by__ = (func.lower(username).asc(),)
