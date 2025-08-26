from sqlalchemy import Column, Integer
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, declared_attr

from config import settings


class PreBase:
    """Базовый класс для всех моделей ORM."""
    __abstract__ = True

    id = Column(Integer, primary_key=True)

    @declared_attr # type: ignore[valid-type]
    def __tablename__(cls) -> str:
        return cls.__name__.lower() # type: ignore[attr-defined]


AppBaseClass = declarative_base(cls=PreBase)

engine = create_async_engine(settings.DATABASE_URL)

AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession)


async def get_async_session():
    async with AsyncSessionLocal() as async_session:
        yield async_session