from log import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class BaseService:

    def __init__(self, model):
        """Инициализация объекта класса."""
        self.model = model

    async def get(
        self,
        session: AsyncSession,
        obj_id: int,
    ):
        """Функция чтения единичной записи таблицы."""
        query = select(self.model).where(self.model.id == obj_id)
        db_obj = await session.execute(query)
        db_obj = db_obj.scalars().first()
        logger.log('DB_ACCESS', f'Entry retrieve: model={db_obj.__class__.__name__}, id={db_obj.id}')
        return db_obj

    async def get_all(
        self,
        session: AsyncSession,
    ):
        """Метод чтения всех записей таблицы."""
        result = await session.execute(select(self.model))
        result = result.scalars().all()
        logger.log('DB_ACCESS', f'All entries retrieve: model={self.model.__name__}')        
        return result