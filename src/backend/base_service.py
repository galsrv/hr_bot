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
        return db_obj.scalars().first()

    async def get_all(
        self,
        db: AsyncSession,
    ):
        """Метод чтения всех записей таблицы."""
        result = await db.execute(select(self.model))
        return result.scalars().all()