from fastapi import HTTPException, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from base_service import BaseService
from bot_settings.constants import(
    ERROR_MESSAGE_INT_TYPE,
    ERROR_MESSAGE_VALUE_INT
)
from bot_settings.models import BotSettingsOrm
from bot_settings.schemas import SettingsChangeSchema

class BotSettingsService(BaseService):
    def __init__(self):
        super().__init__(BotSettingsOrm)

    async def setting_value_check(
        self,
        int_type: int,
        new_value: str,
    ) -> HTTPException | None:
        '''Проверяем новое значение настройки на основании поля int_type.'''
        if int_type:
            try:
                int(new_value)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=ERROR_MESSAGE_INT_TYPE
                )
            if not (1 < int(new_value) < 10):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=ERROR_MESSAGE_VALUE_INT
                )

    async def setting_update(self,
        session: AsyncSession,
        id: int,
        data_input: SettingsChangeSchema,
 ) -> BotSettingsOrm:
        '''Обновляем значение настройки проекта.'''
        setting: BotSettingsOrm = await bot_settings_service.get(session, id)

        # Валидируем то, что не выловил Pydantic. Всё, что связано с данными в БД
        await self.setting_value_check(setting.int_type, data_input.value)
        
        setting.value = data_input.value
        session.add(setting)
        await session.commit()
        await session.refresh(setting)
        logger.log('DB_ACCESS', f'Entry update: model={setting.__class__.__name__}, id={setting.id}, updated: value={setting.value}')
        return setting

bot_settings_service = BotSettingsService()