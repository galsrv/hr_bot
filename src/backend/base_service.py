from typing import Any

from pydantic import BaseModel, ValidationError
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from log import logger
from utils import read_csv, write_csv


class BaseService:
    """Базовый класс сервисных методов обращения в БД."""
    def __init__(self, model):
        """Инициализация объекта класса."""
        self.model = model

    async def get(
        self,
        session: AsyncSession,
        obj_id: int,
    ) -> Any | None:
        """Функция чтения единичной записи таблицы."""
        query = select(self.model).where(self.model.id == obj_id)
        db_obj = await session.execute(query)
        db_obj = db_obj.scalars().first()

        success = 'success' if db_obj else 'not found'
        logger.log(
            'DB_ACCESS',
            f'Entry retrieve: model={self.model.__name__}, id={obj_id}, result={success}',
        )

        return db_obj

    async def get_all(
        self,
        session: AsyncSession,
    ) -> list:
        """Метод чтения всех записей таблицы."""
        query = select(self.model).order_by(*self.model.__order_by__)
        result = await session.execute(query)
        result = result.scalars().all()
        logger.log(
            'DB_ACCESS',
            f'Entry retrieve: model={self.model.__name__}, {len(result)} entries retrieved',
        )
        return result

    async def create(self, session: AsyncSession, data_input):
        new_db_obj = self.model(**data_input.model_dump())
        session.add(new_db_obj)
        await session.commit()
        await session.refresh(new_db_obj)
        logger.log(
            'DB_ACCESS',
            f'Entry creation: model={new_db_obj.__class__.__name__}, id={new_db_obj.id}',
        )
        return new_db_obj

    async def update(self, session: AsyncSession, db_obj, data_input):
        data_input: dict = data_input.model_dump(exclude_none=True)
        [setattr(db_obj, k, v) for k, v in data_input.items()]

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        logger.log(
            'DB_ACCESS',
            f'Entry update: model={db_obj.__class__.__name__}, id={db_obj.id}',
        )
        return db_obj

    async def delete(
        self,
        session: AsyncSession,
        obj_id: int,
    ) -> None:
        """Удаляем запись из таблицы по ключу."""
        query = delete(self.model).where(self.model.id == obj_id)
        await session.execute(query)
        await session.commit()
        logger.log(
            'DB_ACCESS', f'Entry deletion: model={self.model.__name__}, id={obj_id}'
        )

    async def delete_all(
        self,
        session: AsyncSession,
    ) -> None:
        """Удаляем все записи из таблицы."""
        query = delete(self.model)
        await session.execute(query)
        await session.commit()
        logger.log(
            'DB_ACCESS', f'All data from model={self.model.__name__} was deleted')

    async def upload_data(
        self,
        session: AsyncSession,
        filepath: str,
        pydantic_model: type[BaseModel],
        created_by_id: int = None,
    ) -> None:
        """Загружаем данные в таблицу БД, делая предварительно копию."""
        # Сначала делаем бэкап и потом затираем текущие данные в таблице БД
        try:
            backup_filepath = filepath[: filepath.rfind('.csv')] + '_backup.csv'
            await self.download_data(session, backup_filepath)
        except Exception as e:
            logger.error(f'❌ Error while creating backup. Error text: {e}')
            return

        logger.info(
            f'⚠️  The data of {self.model.__name__} was backed up to the file {backup_filepath}'
        )
        await self.delete_all(session)
        logger.info(f'⚠️  The data of {self.model.__name__} was deleted')

        data: list[dict] = await read_csv(filepath)

        # Если в модели есть поля с авторами, то дообогащаем данные
        for attr in ('created_by_id', 'updated_by_id'):
            if attr in pydantic_model.model_fields:
                for el in data:
                    el[attr] = created_by_id

        try:
            data = [pydantic_model.model_validate(el) for el in data]
        except ValidationError as e:
            logger.error(f'❌ Error while creating Pydantic model. Error text: {e}')
            return

        for el in data:
            await self.create(session, el)

        logger.info(
            f'✅ The data from {filepath} was uploaded to {self.model.__name__} DB table, {len(data)} rows in total'
        )

    async def download_data(self, session: AsyncSession, filepath: str) -> None:
        """Выгружаем данные в csv-файл."""
        entries = await self.get_all(session)

        if len(entries) == 0:
            logger.info(
                f'⚠️ Attempt to backup {self.model.__name__}. Table is empty. Proceed.')
            return

        if hasattr(self.model, 'to_dict'):
            headers = entries[0].to_dict().keys()
            entries: list[dict] = [
                headers,
            ] + [el.to_dict().values() for el in entries]

            await write_csv(entries, filepath)
            logger.info(
                f'✅ The data of {self.model.__name__} was downloaded to the file {filepath}')
        else:
            logger.warning(
                f'❌ Error while downloading data of {self.model.__name__}. Model has to have to_dict method'
            )
