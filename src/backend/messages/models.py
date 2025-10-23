from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy import (
    text as t,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import AppBaseClass
from messages.constants import (
    EMPLOYEE_NAME_MAX_LENGTH,
    MESSAGE_TEXT_MAX_LENGTH,
)


class MessagesOrm(AppBaseClass):
    """Модель таблицы сообщений."""

    __tablename__ = 'messages'

    employee_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey('employees.id', ondelete='CASCADE'), nullable=False
    )
    text: Mapped[str] = mapped_column(
        String(MESSAGE_TEXT_MAX_LENGTH))
    manager_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('auth_user.id', ondelete='SET NULL'), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False)
    is_read: Mapped[bool] = mapped_column(
        Boolean, server_default=t('false'), default=False)

    manager: Mapped['UsersOrm'] = relationship(  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
        'UsersOrm',
        lazy='joined',
    )

    employee: Mapped['EmployeesOrm'] = relationship(
        'EmployeesOrm',
        lazy='joined',
        # back_populates='messages'
    )

    __order_by__ = (func.lower(created_at).asc(),)


class EmployeesOrm(AppBaseClass):
    """Модель таблицы сотрудников."""

    __tablename__ = 'employees'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String(EMPLOYEE_NAME_MAX_LENGTH), nullable=True)
    is_banned: Mapped[bool] = mapped_column(
        Boolean, server_default=t('false'), default=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    updated_by_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('auth_user.id', ondelete='SET NULL'),
        server_default=t('null'),
        default=None,
        nullable=True,
    )  # pyright: ignore[reportUndefinedVariable] # noqa: F821

    # messages: Mapped[list['MessagesOrm']] = relationship(
    #     'MessagesOrm',
    #     lazy='selectin',
    # )
