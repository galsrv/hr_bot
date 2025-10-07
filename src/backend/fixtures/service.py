from pydantic import ValidationError, BaseModel

from base_service import BaseService
from database import AsyncSessionLocal
from fixtures.csv import write_csv, read_csv
from log import logger


async def upload_data(model_service: BaseService, filepath: str, pydantic_model: BaseModel):
    '''Загружаем данные в таблицу БД, делая предварительно копию.'''
    async with AsyncSessionLocal() as session:
        # Сначала делаем бэкап и потом затираем текущие данные в таблице БД
        backup_filepath = filepath[:filepath.rfind('.csv')] + '_backup.csv'
        await download_data(model_service, backup_filepath)
        logger.info(f'⚠️  The data of {model_service.model.__name__} was backed up to the file {backup_filepath}')
        await model_service.delete_all(session)
        logger.info(f'⚠️  The data of {model_service.model.__name__} was deleted')

        data: list[dict] = await read_csv(filepath)
        try:
            data = [pydantic_model.model_validate(el) for el in data]
        except ValidationError as e:
            logger.error(f'❌ Error while creating Pydantic model. Error text: {e}')
            return

        for el in data:
            await model_service.create(session, el)

        logger.info(f'✅ The data from {filepath} was uploaded to {model_service.model.__name__} DB table, {len(data)} rows in total')


async def download_data(model_service: BaseService, filepath: str):
    '''Выгружаем данные в csv-файл.'''
    async with AsyncSessionLocal() as session:
        entries = await model_service.get_all(session)
        if hasattr(model_service.model, 'to_dict'):
            headers = entries[0].to_dict().keys()
            entries: list[dict] = [headers, ] + [el.to_dict().values() for el in entries]

            await write_csv(entries, filepath)
            logger.info(f'✅ The data of {model_service.model.__name__} was downloaded to the file {filepath}')
        else:
            logger.warning(f'❌ Error while downloading data of {model_service.model.__name__}. Model has to have to_dict method')


