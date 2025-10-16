from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import text

from auth.constants import SESSION_DURATION_IN_DAYS, SESSION_ID_LENGTH
from auth.utils import create_random_session_string
from database import AppBaseClass
from users.models import UsersOrm


class SessionsOrm(AppBaseClass):
    """Модель таблицы пользовательских сессий."""

    __tablename__ = 'auth_session'

    id: Mapped[str] = mapped_column(
        String(SESSION_ID_LENGTH),
        primary_key=True,
        nullable=False,
        unique=True,
        index=True,
        default=create_random_session_string,
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(UsersOrm.id, ondelete='CASCADE'), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    expired_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text(f"(NOW() + interval '{SESSION_DURATION_IN_DAYS} days')"),
        nullable=False,
    )

    user: Mapped[UsersOrm] = relationship(
        UsersOrm,
        back_populates='session',
        lazy='joined',
    )
