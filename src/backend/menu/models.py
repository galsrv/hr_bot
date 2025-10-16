from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import AppBaseClass
from menu.constants import MENU_ANSWER_MAX_LENGTH, MENU_BUTTON_TEXT_MAX_LENGTH
from users.models import UsersOrm


class MenuOrm(AppBaseClass):
    """Модель справочника ответов."""

    __tablename__ = 'menu'

    button_text: Mapped[str] = mapped_column(
        String(MENU_BUTTON_TEXT_MAX_LENGTH), nullable=False, unique=True
    )
    answer: Mapped[str] = mapped_column(String(MENU_ANSWER_MAX_LENGTH), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    created_by_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('auth_user.id', ondelete='SET NULL'), nullable=True
    )
    updated_by_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('auth_user.id', ondelete='SET NULL'), nullable=True
    )

    created_by: Mapped['UsersOrm'] = relationship(
        'UsersOrm',
        foreign_keys=[
            created_by_id,
        ],
        lazy='joined',
        join_depth=1,
    )
    # Черная магия, но иначе отношение будет работать в обе стороны
    # Без лямбды UsersOrm не определено к этому моменту
    # remote_side=lambda: [UsersOrm.id])

    updated_by: Mapped['UsersOrm'] = relationship(
        'UsersOrm',
        foreign_keys=[
            updated_by_id,
        ],
        lazy='joined',
        join_depth=1,
    )
    # remote_side=lambda: [UsersOrm.id])

    __order_by__ = ('id',)

    def to_dict(self) -> dict:
        """Используется для выгрузки в csv."""
        return {'button_text': self.button_text, 'answer': self.answer}
