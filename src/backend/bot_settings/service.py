from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from base_service import BaseService
from bot_settings.constants import (
    ERROR_MESSAGE_INT_TYPE,
    ERROR_MESSAGE_VALUE_INT,
    SETTING_INT_MAX_VALUE,
)
from bot_settings.models import BotSettingsOrm
from bot_settings.schemas import SettingsChangeSchema


class BotSettingsService(BaseService):
    def __init__(self):
        super().__init__(BotSettingsOrm)

    async def _setting_value_check(
        self,
        int_type: int,
        new_value: str,
    ) -> HTTPException | None:
        """Проверяем новое значение настройки на основании поля int_type."""
        if int_type:
            try:
                int(new_value)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=ERROR_MESSAGE_INT_TYPE,
                )
            if not (0 < int(new_value) < SETTING_INT_MAX_VALUE):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=ERROR_MESSAGE_VALUE_INT,
                )

    async def get_setting(
        self,
        session: AsyncSession,
        id: int,
    ) -> BotSettingsOrm:
        """Получаем одну настройку проекта."""
        setting: BotSettingsOrm | None = await self.get(session, id)

        if setting is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Запрошенная запись не существует',
            )

        return setting

    async def update_setting(
        self,
        session: AsyncSession,
        id: int,
        data_input: SettingsChangeSchema,
    ) -> BotSettingsOrm:
        """Обновляем значение настройки проекта."""
        setting: BotSettingsOrm = await self.get_setting(session, id)

        # Валидируем то, что не выловил Pydantic. Всё, что связано с данными в БД
        await self._setting_value_check(setting.int_type, data_input.value)

        setting = await self.update(session, setting, data_input)
        return setting


bot_settings_service = BotSettingsService()
