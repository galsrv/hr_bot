from fastapi import HTTPException, status
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

        success = 'success' if db_obj else 'not found'
        logger.log('DB_ACCESS', f'Entry retrieve: model={self.model.__name__}, id={obj_id}, result={success}')

        if db_obj is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Запрошенная запись не существует'
            )

        return db_obj

    async def get_all(
        self,
        session: AsyncSession,
     ):
        """Метод чтения всех записей таблицы."""
        query = select(self.model)
        result = await session.execute(query)
        result = result.scalars().all()
        logger.log('DB_ACCESS', f'Entry retrieve: model={self.model.__name__}, {len(result)} entries retrieved')    
        return result

    async def create(self,
                     session: AsyncSession,
                     data_input):
        new_db_obj = self.model(**data_input.model_dump())
        session.add(new_db_obj)
        await session.commit()
        await session.refresh(new_db_obj)
        logger.log('DB_ACCESS', f'Entry creation: model={new_db_obj.__class__.__name__}, id={new_db_obj.id}')
        return new_db_obj

    async def update(self,
                       session: AsyncSession,
                       id: int,
                       data_input):
        db_obj = await self.get(session, id)
        data_input: dict = data_input.model_dump(exclude_none=True)
        [setattr(db_obj, k, v) for k, v in data_input.items()]

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        logger.log('DB_ACCESS', f'Entry update: model={db_obj.__class__.__name__}, id={db_obj.id}')
        return db_obj