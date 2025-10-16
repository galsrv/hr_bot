from sqlalchemy import Integer
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Mapped, declarative_base, declared_attr, mapped_column

from config import settings
from log import sql_logger  # noqa


class PreBase:
    """Базовый класс для всех моделей ORM."""

    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    @declared_attr
    def __order_by__(cls):
        return (cls.id.asc(),)


AppBaseClass = declarative_base(cls=PreBase)

engine = create_async_engine(
    url=settings.DATABASE_URL, echo=False if settings.PROD_ENVIRONMENT else True
)

AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession)


async def get_async_session():
    async with AsyncSessionLocal() as async_session:
        yield async_session
