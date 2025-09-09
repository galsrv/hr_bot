from sqlalchemy import Integer
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, declared_attr, mapped_column, Mapped

from config import settings


class PreBase:
    '''Базовый класс для всех моделей ORM.'''
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    @classmethod
    def default_order(cls, stmt):
        '''Сортировка при наличии параметра __order_by__ у модели.'''
        if hasattr(cls, '__order_by__'):
            stmt = stmt.order_by(*cls.__order_by__)
        return stmt


AppBaseClass = declarative_base(cls=PreBase)

engine = create_async_engine(
    url=settings.DATABASE_URL,
    echo=False if settings.PROD_ENVIRONMENT else True)

AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession)


async def get_async_session():
    async with AsyncSessionLocal() as async_session:
        yield async_session